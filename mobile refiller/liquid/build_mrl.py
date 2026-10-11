"""Model of the mobile refiller (liquid) on the Bruut OpenAgbot, with its trailer and the receiver kit for the
working robot.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_mrl
    build_mrl.build()                              # saves FCStd and STEP (boom parked, tanks 80 % full)
    build_mrl.set_pose(phi=90, r=1446, s=150)      # slew angle (deg, + = to the left), trolley radius, spout down
    build_mrl.set_trailer(25)                      # articulation of the trailer (deg, + = trailer swings left)
    build_mrl.set_levels(refiller=200, trailer=100)    # litres
    build_mrl.check_interference()                 # overlap in the current pose (must be empty)
    build_mrl.check_fit()                          # boom over its whole range + trailer articulation (must be empty)
    build_mrl.clearance()                          # steering sweep vs sump, max trailer articulation, boom height
    build_mrl.mass_properties()                    # masses, centres of gravity, wheel loads (full / empty)
    build_mrl.build_docked()                       # scene: refiller docked next to the working robot (LFA)
    build_mrl.render_all()                         # all images in previews/
"""
import math
import os
import re
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrl_params as P
import mrl_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
ROOT = os.path.dirname(os.path.dirname(FOLDER))
AGBOT_FOLDER = os.path.join(ROOT, "agbots", "agbot design")
AGBOT_MODULES = ("agbot_params", "agbot_parts", "build_agbot")
LFA_FOLDER = os.path.join(ROOT, "liquid fertilizer applicator", "advanced")
DOC_NAME = "Mobile_Refiller_Liquid"
DOCKED_DOC = "Mobile_Refiller_docked"
SAVE_BASE = os.path.join(FOLDER, "Mobile_Refiller_Liquid")

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "trailer": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "alu": (0.80, 0.81, 0.83),
    "module": (0.70, 0.72, 0.75),
    "carriage": (0.20, 0.21, 0.23),
    "motor": (0.08, 0.08, 0.08),
    "pump": (0.10, 0.35, 0.65),
    "tank": (0.93, 0.93, 0.88),
    "liquid": (0.15, 0.50, 0.80),
    "hose": (0.12, 0.12, 0.13),
    "rubber": (0.10, 0.10, 0.10),
    "valve": (0.85, 0.20, 0.15),
    "pp": (0.20, 0.22, 0.25),
    "box": (0.55, 0.57, 0.60),
    "white": (0.96, 0.96, 0.95),
    "black": (0.03, 0.03, 0.03),
    "yellow": (0.95, 0.75, 0.10),
    "chain": (0.15, 0.15, 0.16),
    "camlock": (0.80, 0.62, 0.25),
    "funnel": (0.95, 0.75, 0.10),
}
TRANSPARENT = {"tank": 75, "liquid": 0}

# ---------------------------------------------------------------------
# Tree helpers
# ---------------------------------------------------------------------
def new_part(doc, parent, name, label, placement=None):
    part = doc.addObject("App::Part", name)
    part.Label = label
    if placement is not None:
        part.Placement = placement
    if parent is not None:
        parent.addObject(part)
    return part


def add_shape(doc, parent, name, label, shape, color, visible=True):
    if isinstance(shape, (list, tuple)):
        shape = Part.makeCompound(list(shape))
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape if shape is not None else Part.Shape()
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
        if color in TRANSPARENT:
            view.Transparency = TRANSPARENT[color]
    return obj


def base_name(name):
    """Object name without the number FreeCAD adds when a name is taken (RL_tire001 -> RL_tire)."""
    return re.sub(r"\d{3}$", "", name)


# ---------------------------------------------------------------------
# Pose
# ---------------------------------------------------------------------
REF = {"phi": P.phi_park, "r": P.r_park, "s": 0.0, "trail": 0.0}


def pose_placements(phi=None, r=None, s=None, trail=None):
    phi = REF["phi"] if phi is None else phi
    r = REF["r"] if r is None else r
    s = REF["s"] if s is None else s
    trail = REF["trail"] if trail is None else trail
    if not P.r_park - 1e-6 <= r <= P.r_max + 1e-6:
        raise ValueError("r = %.1f outside %.0f .. %.0f" % (r, P.r_park, P.r_max))
    if not -1e-6 <= s <= P.spout_stroke + 1e-6:
        raise ValueError("s = %.1f outside 0 .. %.0f" % (s, P.spout_stroke))
    hx, hy, _ = P.hitch
    return {"MR_slew": App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), phi), V(G.CX, G.CY, 0)),
            "MR_trolley": App.Placement(V(0, r - G.REF_R, 0), App.Rotation()),
            "MR_spout": App.Placement(V(0, 0, -s), App.Rotation()),
            "MR_trailer": App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), trail), V(hx, hy, 0))}


_dyn = {"chain": {}, "hose": {}}


def chain_shape(r):
    key = round(r / 5.0) * 5.0
    if key not in _dyn["chain"]:
        _dyn["chain"][key] = G.drag_chain(key)
    return _dyn["chain"][key]


def spout_hose_shape(s):
    key = round(s / 5.0) * 5.0
    if key not in _dyn["hose"]:
        _dyn["hose"][key] = G.spout_hose(key)
    return _dyn["hose"][key]


def apply_pose(doc, phi=None, r=None, s=None, trail=None, objs=None):
    """Set the moving parts (doc objects found by name, or via objs = {base name: object})."""
    def get(n):
        return objs[n] if objs is not None else doc.getObject(n)
    for name, pl in pose_placements(phi, r, s, trail).items():
        get(name).Placement = pl
    if r is not None:
        get("mr_chain").Shape = chain_shape(r)
    if s is not None:
        get("mr_spout_hose").Shape = spout_hose_shape(s)


def set_pose(phi=None, r=None, s=None, doc=None):
    doc = active_doc(doc)
    apply_pose(doc, phi, r, s)
    doc.recompute()


def set_trailer(angle, doc=None):
    doc = active_doc(doc)
    apply_pose(doc, trail=angle)
    doc.recompute()


# ---------------------------------------------------------------------
# Levels
# ---------------------------------------------------------------------
def volume_l(kind, level_z):
    v = 0.0
    for z0, z1, a in G.tank_sections(kind):
        v += a * max(0.0, min(level_z, z1) - z0)
    return v / 1e6


def level_for(kind, litres):
    v = litres * 1e6
    secs = G.tank_sections(kind)
    z = secs[0][0]
    for z0, z1, a in secs:
        cap = a * (z1 - z0)
        if v <= cap:
            return z0 + v / a
        v -= cap
        z = z1
    return z


def capacity_l(kind):
    secs = G.tank_sections(kind)
    return volume_l(kind, secs[-1][1])


INNER = {}


def inner_shape(kind):
    if kind not in INNER:
        INNER[kind] = {"refiller": G.tank_inner, "trailer": G.trailer_tank_inner, "receiver": G.rx_tank_inner}[kind]()
    return INNER[kind]


_liq = {}


def liquid_shape(kind, litres):
    key = (kind, round(litres * 2.0) / 2.0)
    if key not in _liq:
        s = G.liquid(inner_shape(kind), level_for(kind, key[1]))
        _liq[key] = s if s is not None else Part.Shape()
    return _liq[key]


LIQUID_OBJ = {"refiller": "mr_liquid", "trailer": "tr_liquid", "receiver": "rx_liquid"}


def set_levels(refiller=None, trailer=None, receiver=None, doc=None, objs=None):
    for kind, litres in (("refiller", refiller), ("trailer", trailer), ("receiver", receiver)):
        if litres is None:
            continue
        o = objs.get(LIQUID_OBJ[kind]) if objs is not None else (doc or App.ActiveDocument).getObject(LIQUID_OBJ[kind])
        if o is not None:
            o.Shape = liquid_shape(kind, litres)


# ---------------------------------------------------------------------
# Robot (read only, from agbots/agbot design)
# ---------------------------------------------------------------------
def load_agbot():
    if AGBOT_FOLDER in sys.path:
        sys.path.remove(AGBOT_FOLDER)
    sys.path.insert(0, AGBOT_FOLDER)
    for name in AGBOT_MODULES:
        mod = sys.modules.get(name)
        if mod is not None and os.path.dirname(os.path.abspath(mod.__file__)) != os.path.abspath(AGBOT_FOLDER):
            del sys.modules[name]
    import build_agbot
    return build_agbot


def build_robot(doc, label="Bruut_OpenAgbot_robot", placement=None):
    """Robot from 'agbot design'. Returns (robot part, {base name: object}) so that a second robot in the same
    document (names with 001) can be found too."""
    BA = load_agbot()
    before = {o.Name for o in doc.Objects}
    robot = BA.new_part(doc, None, "Robot", label)
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    if placement is not None:
        robot.Placement = placement
    objs = {base_name(o.Name): o for o in doc.Objects if o.Name not in before}
    return robot, objs


# ---------------------------------------------------------------------
# Refiller
# ---------------------------------------------------------------------
def build_tank(doc, parent, fill_l):
    grp = new_part(doc, parent, "MR_tank", "tank_%dl_with_sump" % round(capacity_l("refiller")))
    add_shape(doc, grp, "mr_cradle", "cradle_tubes_40x40x3", G.cradle_tubes(), "frame")
    add_shape(doc, grp, "mr_pads", "rubber_strips_5mm", G.cradle_pads(), "rubber")
    add_shape(doc, grp, "mr_cradle_bolts", "cradle_bolts_8xM10", G.cradle_bolts(), "zinc")
    add_shape(doc, grp, "mr_tank", "tank_PE_rotomoulded_T_shape", G.tank_shell(), "tank")
    add_shape(doc, grp, "mr_liquid", "liquid_in_tank", liquid_shape("refiller", fill_l), "liquid")
    add_shape(doc, grp, "mr_fittings", "fill_lid_and_vent", G.tank_fittings(), "yellow")
    add_shape(doc, grp, "mr_level", "level_sensor_ultrasonic", G.tank_level_sensor(), "black")
    add_shape(doc, grp, "mr_straps", "tank_straps_50x3", G.straps(P.tank_x, P.tank_z[1]), "zinc")
    return grp


def build_pump(doc, parent):
    grp = new_part(doc, parent, "MR_pump", "transfer_pump_and_hoses")
    add_shape(doc, grp, "mr_pump", "transfer_pump_24V_1.5in", G.pump_body(), "pump")
    add_shape(doc, grp, "mr_pump_cradle", "pump_cradle_8mm", G.pump_cradle(), "frame")
    add_shape(doc, grp, "mr_suction", "suction_hose_1.5in", G.suction_hose(), "hose")
    add_shape(doc, grp, "mr_valve", "ball_valve_electric_tank", G.outlet_valve(), "valve")
    branch, v2 = G.trailer_branch()
    add_shape(doc, grp, "mr_branch", "suction_hose_from_trailer", branch, "hose")
    add_shape(doc, grp, "mr_branch_valve", "ball_valve_electric_trailer", v2, "valve")
    add_shape(doc, grp, "mr_camlock", "camlock_trailer_line_robot_half", G.camlock(*G.CAMLOCK_ROBOT), "camlock")
    add_shape(doc, grp, "mr_discharge", "discharge_hose_to_swivel", G.discharge_hose(), "hose")
    return grp


def build_frame(doc, parent):
    grp = new_part(doc, parent, "MR_frame", "subframe_hitch_column")
    add_shape(doc, grp, "mr_sub_plate", "sub_plate_10mm_under_rear_beams", G.sub_plate(), "frame")
    add_shape(doc, grp, "mr_hitch_sides", "hitch_side_plates_10mm", G.hitch_side_plates(), "frame")
    add_shape(doc, grp, "mr_clevis", "hitch_clevis_plates_12mm", G.clevis_plates(), "frame")
    add_shape(doc, grp, "mr_hitch_pin", "hitch_pin_D20", G.hitch_pin(), "zinc")
    add_shape(doc, grp, "mr_frame_bolts", "frame_bolts_8xM10", G.frame_bolts(), "zinc")
    add_shape(doc, grp, "mr_base_plate", "column_base_plate_12mm", G.base_plate(), "frame")
    add_shape(doc, grp, "mr_column", "column_114x4_gussets_flange", G.column(), "frame")
    add_shape(doc, grp, "mr_slew_drive", "slew_drive_worm_24V", G.slew_drive(), "motor")
    add_shape(doc, grp, "mr_ctrl_box", "control_box_IP66_pump_slew_radio", G.control_box(), "box")
    add_shape(doc, grp, "mr_ctrl_bracket", "control_box_brackets", G.control_box_bracket(), "frame")
    return grp


def build_boom(doc, parent, pl, r, s):
    sl = new_part(doc, parent, "MR_slew", "boom_slews_about_column", pl["MR_slew"])
    add_shape(doc, sl, "mr_root_plate", "boom_root_plate_10mm", G.root_plate(), "alu")
    add_shape(doc, sl, "mr_boom", "boom_belt_linear_module_80_L%d" % (P.boom_v[1] - P.boom_v[0]), G.boom_module(), "module")
    add_shape(doc, sl, "mr_boom_motor", "boom_motor_nema23_closed_loop", G.boom_motor(), "motor")
    add_shape(doc, sl, "mr_chain", "hose_carrier", chain_shape(r), "chain")
    tr = new_part(doc, sl, "MR_trolley", "trolley_moves_along_boom", pl["MR_trolley"])
    add_shape(doc, tr, "mr_carriage", "boom_carriage_80x150", G.carriage(), "carriage")
    add_shape(doc, tr, "mr_head_plate", "head_plate_alu_8mm", G.head_plate(), "alu")
    add_shape(doc, tr, "mr_sleeve", "spout_sleeve_PE", G.spout_sleeve(), "white")
    add_shape(doc, tr, "mr_spout_act", "spout_actuator_24V_stroke_150", G.spout_actuator_body(), "motor")
    add_shape(doc, tr, "mr_camera", "camera_looking_down", G.camera(), "black")
    add_shape(doc, tr, "mr_spout_hose", "spout_hose_1.5in", spout_hose_shape(s), "hose")
    sp = new_part(doc, tr, "MR_spout", "spout_moves_down", pl["MR_spout"])
    add_shape(doc, sp, "mr_spout", "spout_PP_50", G.spout(), "pp")
    add_shape(doc, sp, "mr_spout_inlet", "spout_inlet_elbow", G.spout_inlet(), "pp")
    add_shape(doc, sp, "mr_spout_clamp", "spout_clamp_and_actuator_rod", G.spout_clamp_rod(), "steel")
    add_shape(doc, sp, "mr_mast", "mast_25_on_spout_axis", G.mast(), "alu")
    add_shape(doc, sp, "mr_antenna", "rtk_antenna_above_spout", G.antenna(), "white")
    return sl


def build_trailer(doc, parent, pl, fill_l):
    BA = load_agbot()
    tl = new_part(doc, parent, "MR_trailer", "trailer_%dl_powered" % round(capacity_l("trailer")), pl["MR_trailer"])
    fr = new_part(doc, tl, "TR_frame", "trailer_frame_robot_parts")
    for i, y in enumerate(P.tr_lower_y):
        add_shape(doc, fr, "tr_lower_%d" % (i + 1), "chassis_beam_1_trailer_%d" % (i + 1), BA.G.moved(
            BA.G.chassis_beam_1(), y=y, z=sum(P.robot_lower_beam_z) / 2.0), "trailer")
    for x in P.robot_upper_beam_x:
        add_shape(doc, fr, "tr_upper_%s%d" % ("L" if x < 0 else "R", abs(int(x))), "chassis_beam_2_trailer_x%+d" % x,
                  BA.G.moved(BA.G.chassis_beam_2(), x=x, y=P.tr_upper_y, z=sum(P.robot_upper_beam_z) / 2.0), "carriage")
    add_shape(doc, fr, "tr_drawbar", "drawbar_A_frame_50x50_eye", G.drawbar(), "trailer")
    add_shape(doc, fr, "tr_jack", "parking_jack_raised", G.jack(), "zinc")
    add_shape(doc, fr, "tr_jack_bracket", "parking_jack_bracket", G.jack_bracket(), "trailer")
    shapes = BA.make_shapes()
    wheel = {}
    for tag, sx in (("TL", -1), ("TR", 1)):
        unit = new_part(doc, tl, "TR_%s_unit" % tag[1], "trailer_wheel_unit_%s" % ("left" if sx < 0 else "right"),
                        App.Placement(V(sx * P.robot_wheel_x, P.tr_axle_y, P.robot_axle_z), App.Rotation()))
        for key, label, shape, color in (
                ("tire", "tire", shapes["tire"], "tire"), ("rim", "rim", shapes["rim"], "rim"),
                ("hub", "hub_motor_driven", shapes["hub_motor"], "hub"), ("axle", "axle", shapes["axle"], "axle"),
                ("top_plate", "bracket_top_plate", shapes["top_plate"], "top_plate"),
                ("side_l", "bracket_side_plate_left", shapes["side_plate"][-1], "fork"),
                ("side_r", "bracket_side_plate_right", shapes["side_plate"][1], "fork"),
                ("axle_br_l", "axle_bracket_left", shapes["axle_bracket"][-1], "fork"),
                ("axle_br_r", "axle_bracket_right", shapes["axle_bracket"][1], "fork"),
                ("wheel_hw", "wheel_hardware", shapes["wheel_hardware"], "zinc"),
                ("spacer", "wooden_spacer_block", shapes["spacer_block"], "wood"),
                ("frame_bolts", "frame_bolts", shapes["frame_bolts"], "zinc")):
            obj = doc.addObject("Part::Feature", "tr_%s_%s" % (tag, key))
            obj.Label = "%s_trailer_%s" % (label, tag)
            obj.Shape = Part.makeCompound(list(shape)) if isinstance(shape, (list, tuple)) else shape
            unit.addObject(obj)
            if obj.ViewObject is not None:
                obj.ViewObject.ShapeColor = BA.COLOR[color]
            wheel[key] = obj
    tk = new_part(doc, tl, "TR_tank", "trailer_tank")
    add_shape(doc, tk, "tr_cradle", "cradle_tubes_trailer", G.cradle_tubes(P.tr_cradle_y), "trailer")
    add_shape(doc, tk, "tr_pads", "rubber_strips_trailer", G.cradle_pads(P.tr_cradle_y), "rubber")
    add_shape(doc, tk, "tr_cradle_bolts", "cradle_bolts_trailer", G.cradle_bolts(P.tr_cradle_y), "zinc")
    add_shape(doc, tk, "tr_tank", "tank_PE_trailer", G.trailer_tank_shell(), "tank")
    add_shape(doc, tk, "tr_liquid", "liquid_in_trailer_tank", liquid_shape("trailer", fill_l), "liquid")
    add_shape(doc, tk, "tr_fittings", "fill_lid_outlet_valve", G.trailer_fittings(), "yellow")
    add_shape(doc, tk, "tr_straps", "tank_straps_trailer", G.straps(P.tr_tank_x, P.tank_z0 + P.tr_tank_h,
                                                                     P.tr_cradle_y), "zinc")
    add_shape(doc, tk, "tr_hose", "hose_trailer_to_refiller", G.trailer_hose(), "hose")
    add_shape(doc, tk, "tr_camlock", "camlock_trailer_half", G.camlock(*G.CAMLOCK_TRAILER), "camlock")
    return tl


def build_refiller_into(doc, parent=None, phi=None, r=None, s=None, trail=None, fill=0.8, trailer=True):
    """Refiller kit (+ trailer) in robot coordinates; parent = the robot part (also used by animate_mrl.py)."""
    pl = pose_placements(phi, r, s, trail)
    r = REF["r"] if r is None else r
    s = REF["s"] if s is None else s
    root = new_part(doc, parent, "Mobile_refiller", "mobile_refiller_liquid")
    build_tank(doc, root, fill * capacity_l("refiller"))
    build_pump(doc, root)
    build_frame(doc, root)
    build_boom(doc, root, pl, r, s)
    if trailer:
        build_trailer(doc, root, pl, fill * capacity_l("trailer"))
    return root


def build_receiver_into(doc, parent=None, fill_l=None):
    """Receiver kit on the working robot (robot coordinates of that robot)."""
    fill_l = 0.8 * P.rx_tank_nominal if fill_l is None else fill_l
    root = new_part(doc, parent, "Receiver_kit", "receiver_kit_on_working_robot")
    add_shape(doc, root, "rx_cradle", "cradle_tubes_40x40x3", G.cradle_tubes(), "frame")
    add_shape(doc, root, "rx_pads", "rubber_strips_5mm", G.cradle_pads(), "rubber")
    add_shape(doc, root, "rx_cradle_bolts", "cradle_bolts_8xM10", G.cradle_bolts(), "zinc")
    add_shape(doc, root, "rx_tank", "work_tank_PE_%dl" % P.rx_tank_nominal, G.rx_tank_shell(), "tank")
    add_shape(doc, root, "rx_liquid", "liquid_in_work_tank", liquid_shape("receiver", fill_l), "liquid")
    add_shape(doc, root, "rx_straps", "tank_straps_50x3", G.straps(P.rx_tank_x, G.RX_TOP), "zinc")
    add_shape(doc, root, "rx_funnel", "fill_funnel_300", G.funnel(), "funnel")
    add_shape(doc, root, "rx_strainer", "funnel_strainer", G.strainer(), "steel")
    add_shape(doc, root, "rx_target", "camera_target_plate", G.target_plate(), "white")
    add_shape(doc, root, "rx_marks", "camera_target_code", G.target_marks(), "black")
    add_shape(doc, root, "rx_level", "level_sensor_ultrasonic", G.rx_level_sensor(), "black")
    add_shape(doc, root, "rx_vent", "vent", G.rx_vent(), "yellow")
    return root


# Colors of the robot parts used for the trailer wheel units: from build_agbot.COLOR (keys tire, rim, ...)


def build(phi=None, r=None, s=None, trail=None, fill=0.8, save=True, step=True, show_robot=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Mobile refiller liquid"
    doc.Comment = ("Generated by build_mrl.py from mrl_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Move the boom with build_mrl.set_pose(), the trailer with "
                   "set_trailer().")
    robot, _ = build_robot(doc)
    build_refiller_into(doc, robot, phi, r, s, trail, fill)
    if not show_robot:
        set_robot_visible(False, doc)
    doc.recompute()
    if save:
        doc.saveAs(SAVE_BASE + ".FCStd")
    if step:
        export_step(doc, SAVE_BASE + ".step")
    return doc


def worker_placement(dock_dy=0.0):
    """Working robot docked on the left of the refiller, opposite heading, funnel next to the column."""
    fy = -P.funnel_xy[1]                    # funnel after the 180 degree turn
    return App.Placement(V(-P.dock_d, G.CY - fy + dock_dy, 0.0), App.Rotation(V(0, 0, 1), 180.0))


def ik(tx, ty):
    """Slew angle (deg) and trolley radius that put the spout axis on (tx, ty) (refiller robot coordinates)."""
    dx, dy = tx - G.CX, ty - G.CY
    d2 = dx * dx + dy * dy
    r = math.sqrt(max(0.0, d2 - P.spout_u ** 2))
    phi = math.degrees(math.atan2(dy, dx) - math.atan2(r, P.spout_u))
    return phi, r


def load_lfa():
    if LFA_FOLDER not in sys.path:
        sys.path.insert(0, LFA_FOLDER)
    import build_lfa
    return build_lfa


def build_docked(lift=140.0, fill=0.8, rx_fill=None):
    """Scene: refiller with boom out and spout in the funnel of the working robot (with the applicator, lifted)."""
    if DOCKED_DOC in App.listDocuments():
        App.closeDocument(DOCKED_DOC)
    doc = App.newDocument(DOCKED_DOC)
    doc.Label = "Mobile refiller docked"
    doc.Comment = "Generated by build_mrl.build_docked(). Refiller robot coordinates; working robot on the left."
    worker, wobjs = build_robot(doc, "working_robot_with_applicator", worker_placement())
    try:
        BL = load_lfa()
        BL.build_into(doc, worker, lift, BL.translation(0.0, BL.P.robot_mount_y, 0.0))
    except Exception as exc:
        print("applicator not loaded:", exc)
    build_receiver_into(doc, worker, rx_fill)
    robot, objs = build_robot(doc, "refiller_robot")
    fx, fy = funnel_world()
    phi, r = ik(fx, fy)
    build_refiller_into(doc, robot, phi, r, P.spout_stroke, 0.0, fill)
    doc.recompute()
    return doc


def check_docked(doc=None, tol=1.0):
    """In the docked scene: refiller (robot + kit) against the working robot, its applicator and receiver kit, and the
    receiver kit against its own robot. Must be empty."""
    doc = doc or App.getDocument(DOCKED_DOC)
    refiller = {o.Name for o in doc.getObject("Robot001").OutListRecursive if o.TypeId == "Part::Feature"}
    worker = [o for o in doc.getObject("Robot").OutListRecursive if o.TypeId == "Part::Feature"]
    a = [(o, global_shape(o)) for o in doc.Objects if o.Name in refiller and base_name(o.Name) not in SKIP]
    b = [(o, global_shape(o)) for o in worker if base_name(o.Name) not in SKIP]
    rx = [(o, s) for o, s in b if o.Name.startswith("rx_")]
    rest = [(o, s) for o, s in b if not o.Name.startswith("rx_")]
    pairs = [(x, y) for x in a for y in b] + [(x, y) for x in rx for y in rest]
    pairs += [(rx[i], rx[j]) for i in range(len(rx)) for j in range(i + 1, len(rx))]
    return _overlaps(pairs, tol)


def funnel_world(placement=None):
    pl = placement or worker_placement()
    p = pl.multVec(V(P.funnel_xy[0], P.funnel_xy[1], 0.0))
    return p.x, p.y


def active_doc(doc=None):
    if doc is not None:
        return doc
    d = App.ActiveDocument
    if d is not None and d.getObject("Mobile_refiller") is not None:
        return d
    for n in App.listDocuments():
        d = App.getDocument(n)
        if d.getObject("Mobile_refiller") is not None:
            return d
    raise RuntimeError("no refiller document open")


def kit_objects(doc, root="Mobile_refiller"):
    return [o for o in doc.getObject(root).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc, robot="Robot"):
    r = doc.getObject(robot)
    if r is None:
        return []
    mine = {o.Name for o in kit_objects(doc)} if doc.getObject("Mobile_refiller") else set()
    return [o for o in r.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith(("anim_", "rx_"))]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in kit_objects(doc):
        if o.Shape.isNull() or o.Name.endswith("liquid"):
            continue
        f = doc.addObject("Part::Feature", "step_" + o.Name)
        f.Label = o.Label
        f.Shape = global_shape(o)
        objs.append(f)
    try:
        Import.export(objs, path)
    finally:
        for f in objs:
            doc.removeObject(f.Name)


# ---------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


# parts that are meant to touch or enter each other (hose ends in fittings, the rod in the hollow actuator, ...)
PAIRS_OK = {frozenset(p) for p in (
    ("mr_suction", "mr_valve"), ("mr_suction", "mr_pump"), ("mr_suction", "mr_branch"), ("mr_branch", "mr_branch_valve"),
    ("mr_branch", "mr_camlock"), ("mr_discharge", "mr_pump"), ("mr_camlock", "tr_camlock"), ("tr_hose", "tr_camlock"),
    ("tr_hose", "tr_fittings"), ("mr_spout_hose", "mr_spout_inlet"), ("mr_spout_hose", "mr_chain"),
    ("mr_spout_inlet", "mr_spout"), ("mr_spout_clamp", "mr_spout"), ("mr_mast", "mr_spout"),
    ("mr_antenna", "mr_mast"), ("mr_spout_clamp", "mr_spout_act"), ("mr_spout_clamp", "mr_mast"), ("mr_pads", "mr_cradle"), ("tr_pads", "tr_cradle"),
    ("rx_pads", "rx_cradle"), ("rx_strainer", "rx_funnel"), ("rx_marks", "rx_target"), ("mr_discharge", "mr_column"),
    ("mr_spout_hose", "mr_carriage"), ("mr_spout_hose", "mr_head_plate"),
    # flexible part of the trailer hose at the hitch (drawn rigid): it bends when the trailer articulates
    ("tr_hose", "mr_branch"), ("tr_camlock", "mr_branch"), ("tr_hose", "mr_camlock"))}
SKIP = ("mr_liquid", "tr_liquid", "rx_liquid")


def _ok(a, b):
    return frozenset((base_name(a.Name), base_name(b.Name))) in PAIRS_OK


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        if _ok(oa, ob) or not sa.BoundBox.intersect(sb.BoundBox):
            continue
        try:
            vol = sa.common(sb).Volume
        except Exception as exc:
            hits.append((oa.Label, ob.Label, "error %s" % exc))
            continue
        if vol > tol:
            hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits


def _checked(objs):
    return [o for o in objs if base_name(o.Name) not in SKIP and not o.Shape.isNull()]


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3) in the current pose: kit and trailer among themselves and against the robot.
    Trailer wheel units against the trailer frame are part of the same robot-style stack (checked too)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in _checked(kit_objects(doc))]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


MOVING = ("MR_slew", "MR_trolley", "MR_spout", "MR_trailer")
# the spout only goes down beside the robot (docking sectors); above its own tanks it is blocked in software
SPOUT_DOWN_PHI = (60, 90, 120, 240, 270, 300)


def _group_of(obj):
    parent = obj.getParentGeoFeatureGroup()
    while parent is not None:
        if parent.Name == "MR_trailer":
            return "trailer"
        if parent.Name == "MR_slew":
            return "boom"
        parent = parent.getParentGeoFeatureGroup()
    return "fixed"


def check_fit(doc=None, tol=1.0):
    """Boom: slew 0..330 deg in 30 deg steps, trolley at park / middle / max, spout up and down; trailer -60..60 deg.
    Only the moving group against the rest. Must be empty."""
    doc = active_doc(doc)
    out = {}
    mine = _checked(kit_objects(doc))
    group = {o.Name: _group_of(o) for o in mine}
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    apply_pose(doc, phi=REF["phi"], r=REF["r"], s=0.0, trail=0.0)
    doc.recompute()
    still = {g: [(o, global_shape(o)) for o in mine if group[o.Name] != g] + robot for g in ("boom", "trailer")}
    for phi in range(0, 360, 30):
        for r in (P.r_park, 0.5 * (P.r_park + P.r_max), P.r_max):
            for s in ((0.0, P.spout_stroke) if phi in SPOUT_DOWN_PHI else (0.0,)):
                apply_pose(doc, phi=phi, r=r, s=s)
                doc.recompute()
                mv = [(o, global_shape(o)) for o in mine if group[o.Name] == "boom"]
                hits = _overlaps([(a, b) for a in mv for b in still["boom"]], tol)
                if hits:
                    out[("boom", phi, r, s)] = hits
    apply_pose(doc, phi=REF["phi"], r=REF["r"], s=0.0)
    for a in range(-60, 61, 15):
        apply_pose(doc, trail=a)
        doc.recompute()
        mv = [(o, global_shape(o)) for o in mine if group[o.Name] == "trailer"]
        hits = _overlaps([(x, y) for x in mv for y in still["trailer"]], tol)
        if hits:
            out[("trailer", a)] = hits
    apply_pose(doc, phi=REF["phi"], r=REF["r"], s=0.0, trail=0.0)
    doc.recompute()
    return out


def clearance(doc=None):
    """- front wheels steered 30 deg both ways: smallest distance to the tank / sump;
    - largest trailer articulation before the drawbar/trailer touches the robot or its kit;
    - boom: lowest point of the head and the spout tip (up and down), height of the antenna."""
    doc = active_doc(doc)
    out = {}
    tank = global_shape(doc.getObject("mr_tank"))
    worst = (1e9, None)
    for tag in ("FL", "FR"):
        st = doc.getObject(tag + "_steered")
        keep = st.Placement
        for a in (-30.0, 30.0):
            st.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), a))
            doc.recompute()
            for o in st.OutListRecursive:
                if o.TypeId != "Part::Feature":
                    continue
                d = tank.distToShape(global_shape(o))[0]
                if d < worst[0]:
                    worst = (d, "%s %+.0f deg" % (o.Name, a))
        st.Placement = keep
    doc.recompute()
    out["steering_30deg_to_tank"] = (round(worst[0], 1), worst[1])
    mine = _checked(kit_objects(doc))
    trailer = [o for o in mine if _group_of(o) == "trailer"]
    other = [(o, global_shape(o)) for o in mine if _group_of(o) == "fixed"] + \
            [(o, global_shape(o)) for o in robot_objects(doc)]
    limit = None
    for a in range(30, 121, 5):
        apply_pose(doc, trail=a)
        doc.recompute()
        mv = [(o, global_shape(o)) for o in trailer]
        if _overlaps([(x, y) for x in mv for y in other], 1.0):
            limit = a
            break
    out["trailer_articulation_first_contact_deg"] = limit
    apply_pose(doc, trail=0.0)
    out["spout_tip_up_down"] = (P.spout_tip_up, P.SPOUT_TIP_DOWN)
    out["funnel_rim_z"] = P.FUNNEL_RIM_Z
    out["head_bottom_z"] = round(min(P.camera[2][0] - 18.0, P.head_z[0]), 1)
    out["antenna_top_z"] = round(G.ANT_TOP_UP, 1)
    doc.recompute()
    return out


# ---------------------------------------------------------------------
# Mass: bought parts with a fixed mass (kg), the rest from volume x density
# ---------------------------------------------------------------------
MASS_FIXED = {"mr_pump": P.pump_kg, "mr_boom": P.boom_kg_per_m * (P.boom_v[1] - P.boom_v[0]) / 1000.0,
              "mr_boom_motor": 1.6, "mr_slew_drive": 9.0, "mr_ctrl_box": 6.0, "mr_camera": 0.4, "mr_antenna": 0.45,
              "mr_spout_act": 1.8, "mr_carriage": 0.8, "mr_valve": 1.2, "mr_branch_valve": 1.2, "mr_level": 0.3,
              "rx_level": 0.3, "mr_chain": 1.5, "tr_TL_tire": 3.0, "tr_TR_tire": 3.0, "tr_TL_hub": 9.0,
              "tr_TR_hub": 9.0, "tr_TL_rim": 1.5, "tr_TR_rim": 1.5}
PE, ALU, STEEL, WOOD = 0.95e-6, 2.7e-6, 7.85e-6, 0.6e-6
HOSE = 0.6 / (math.pi * (P.hose_od / 2.0) ** 2 * 1000.0)     # 0.6 kg/m for a solid modelled hose
DENSITY = (("mr_tank", PE), ("tr_tank", PE), ("rx_tank", PE), ("rx_funnel", PE), ("mr_sleeve", PE),
           ("mr_spout_inlet", PE), ("mr_spout", PE), ("mr_fittings", PE), ("tr_fittings", PE), ("rx_vent", PE),
           ("mr_pads", 1.2e-6), ("tr_pads", 1.2e-6), ("rx_pads", 1.2e-6), ("rx_target", ALU), ("rx_marks", ALU),
           ("mr_root_plate", ALU), ("mr_head_plate", ALU), ("mr_mast", ALU), ("tr_TL_spacer", WOOD),
           ("tr_TR_spacer", WOOD), ("mr_suction", HOSE), ("mr_branch", HOSE), ("mr_discharge", HOSE),
           ("tr_hose", HOSE), ("mr_spout_hose", HOSE * 0.7), ("mr_liquid", P.liquid_density * 1e-6),
           ("tr_liquid", P.liquid_density * 1e-6), ("rx_liquid", P.liquid_density * 1e-6))


def _mass_cg(obj):
    shape = global_shape(obj)
    if shape.isNull():
        return 0.0, V(0, 0, 0)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    name = base_name(obj.Name)
    if name in MASS_FIXED:
        return MASS_FIXED[name], cg
    for key, d in DENSITY:
        if name == key:
            return vol * d, cg
    return vol * STEEL, cg


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Masses (kg) and centres of gravity in the current pose and fill. Liquid separately."""
    doc = active_doc(doc)
    objs = kit_objects(doc)
    liquid = [o for o in objs if base_name(o.Name) in SKIP]
    dry = [o for o in objs if base_name(o.Name) not in SKIP]
    out = {}
    for name, sel in (("kit_on_robot", lambda o: _group_of(o) != "trailer"),
                      ("trailer", lambda o: _group_of(o) == "trailer"), ("boom", lambda o: _group_of(o) == "boom")):
        m, c = _sum([o for o in dry if sel(o)])
        out[name + "_kg"] = round(m, 1)
        out[name + "_cg"] = (round(c.x), round(c.y), round(c.z))
    for o in liquid:
        m, c = _mass_cg(o)
        out[base_name(o.Name) + "_kg"] = round(m, 1)
        out[base_name(o.Name) + "_cg"] = (round(c.x), round(c.y), round(c.z))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in kit_objects(doc) + robot_objects(doc):
        if o.Shape.isNull():
            continue
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


# ---------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------
def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, -500, 700)
    eye = tgt - d * 12000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(40000.0)
    if height is None:
        view.fitAll()
    else:
        cam.height.setValue(height)
    return view


def save_view(name, direction, target=None, height=None, up=(0.0, 0.0, 1.0), size_px=(1600, 1100)):
    import FreeCADGui as Gui
    Gui.updateGui()
    set_camera(direction, target, height, up)
    Gui.updateGui()
    view = set_camera(direction, target, height, up)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, name)
    view.saveImage(path, size_px[0], size_px[1], "White")
    return path


GROUND = "render_floor"


def add_floor(doc, x=(-3000.0, 1500.0), y=(-3800.0, 1500.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.62, 0.70, 0.52)
    obj.ViewObject.Transparency = 30
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def add_stream(doc):
    fx, fy = funnel_world()
    obj = doc.addObject("Part::Feature", "render_stream")
    obj.Shape = G.stream(fx, fy, P.SPOUT_TIP_DOWN, G.RX_TOP + P.funnel_neck)
    obj.ViewObject.ShapeColor = COLOR["liquid"]
    obj.ViewObject.Transparency = 30
    return obj


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP)."""
    import FreeCADGui as Gui
    out = []
    doc = build(save=False, step=False)
    add_floor(doc)
    out.append(save_view("1_iso_refiller_with_trailer.png", (1.0, -1.25, -0.75), target=(0, -1050, 700), height=3000))
    out.append(save_view("2_side.png", (-1.0, 0.0, 0.0), target=(0, -1050, 900), height=2700))
    remove(doc, [GROUND])
    set_pose(phi=90.0, r=P.r_max, s=P.spout_stroke, doc=doc)
    out.append(save_view("3_boom_out_iso.png", (1.0, 1.0, -0.6), target=(-450, -900, 800), height=3000))
    set_pose(doc=doc)
    set_robot_visible(False, doc)
    set_visible(doc, ("mr_tank",), False)
    out.append(save_view("4_tank_sump_pump.png", (1.0, -0.6, -0.25), target=(0, -550, 700), height=2000))
    set_visible(doc, ("mr_tank",), True)
    set_robot_visible(True, doc)
    out.append(save_view("5_pump_hitch_below.png", (0.55, 0.9, 0.35), target=(0, -620, 450), height=1100))
    apply_pose(doc, trail=35.0)
    doc.recompute()
    out.append(save_view("6_top_trailer_35deg.png", (0.0, 0.0, -1.0), target=(-300, -1100, 0), height=4000, up=(0.0, 1.0, 0.0)))
    App.closeDocument(doc.Name)
    # docked with the working robot
    doc = build_docked()
    Gui.updateGui()
    add_stream(doc)
    add_floor(doc, x=(-3200.0, 1300.0), y=(-4000.0, 2400.0))
    out.append(save_view("7_docked_iso.png", (1.0, 0.9, -0.65), target=(-700, -900, 700), height=3300))
    out.append(save_view("8_docked_front.png", (0.0, -1.0, -0.18), target=(-700, -500, 750), height=2100))
    remove(doc, [GROUND])
    out.append(save_view("9_docked_top.png", (0.0, 0.0, -1.0), target=(-700, -900, 0), height=4200, up=(0.0, 1.0, 0.0)))
    fx, fy = funnel_world()
    out.append(save_view("10_spout_in_funnel.png", (1.0, 0.35, -0.45), target=(fx + 30, fy, 1180), height=700))
    App.closeDocument(doc.Name)
    build()
    return out
