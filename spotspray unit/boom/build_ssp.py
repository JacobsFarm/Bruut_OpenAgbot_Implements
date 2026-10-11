"""Model of the spot sprayer with the folding 3.75 m boom on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_ssp
    build_ssp.build()                              # saves FCStd and STEP (wings out)
    build_ssp.set_fold(left=0, right=90)           # fold angle of the wings in degrees (0 = working, 90 = up)
    build_ssp.check_interference()                 # overlap in the current pose (must be empty)
    build_ssp.check_fit()                          # overlap over the whole fold of both wings (must be empty)
    build_ssp.clearance()                          # distances to the tyres, the steering sweep and the robot frame
    build_ssp.mass_properties()
    build_ssp.render_all()                         # all images in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ssp_params as P
import ssp_calc as C
import ssp_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Spot_Sprayer_Boom"
SAVE_BASE = os.path.join(FOLDER, "Spot_Sprayer_Boom")
ROOT = "Spot_sprayer"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "galv": (0.70, 0.72, 0.74),
    "alu": (0.80, 0.81, 0.83),
    "stainless": (0.86, 0.87, 0.88),
    "tank": (0.93, 0.93, 0.90),
    "rubber": (0.10, 0.10, 0.10),
    "hose": (0.15, 0.25, 0.55),
    "pump": (0.15, 0.15, 0.17),
    "plastic": (0.10, 0.10, 0.10),
    "nozzle": (0.95, 0.80, 0.10),
    "coil": (0.20, 0.20, 0.22),
    "actuator": (0.30, 0.31, 0.33),
    "box": (0.55, 0.57, 0.60),
    "white": (0.96, 0.96, 0.95),
    "camera": (0.12, 0.12, 0.13),
    "glass": (0.25, 0.45, 0.75),
    "red": (0.85, 0.15, 0.10),
}


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
    obj.Shape = shape
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
    return obj


# ---------------------------------------------------------------------
# Pose: fold angle of both wings. The wings rotate about their hinge axis, the actuator bodies about their base
# pin, the rods slide in the bodies.
# ---------------------------------------------------------------------
MOVING = ("Wing_right", "Wing_left", "Act_right", "Act_left", "Act_right_rod", "Act_left_rod")
REF = {"left": 0.0, "right": 0.0}


def pose_placements(left=0.0, right=0.0):
    for name, phi in (("left", left), ("right", right)):
        if not -1e-6 <= phi <= P.fold_stop + 1e-6:
            raise ValueError("%s fold %.1f outside 0 .. %.1f" % (name, phi, P.fold_stop))
    out = {}
    bx, bz = P.act_base
    for s, tag, phi in ((1, "right", right), (-1, "left", left)):
        out["Wing_" + tag] = App.Placement(V(0, 0, 0), App.Rotation(V(0, 1, 0), -s * phi), V(s * P.centre_half, 0, P.hinge_z))
        psi = C.act_angle(phi)
        out["Act_" + tag] = App.Placement(V(0, 0, 0), App.Rotation(V(0, 1, 0), -s * psi), V(s * bx, 0, bz))
        out["Act_%s_rod" % tag] = App.Placement(V(s * (C.act_length(phi) - G.L0), 0, 0), App.Rotation())
    return out


def set_fold(left=0.0, right=0.0, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(left, right).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_tank(doc, parent):
    grp = new_part(doc, parent, "Tank", "tank_%dl_on_cradle" % P.tank_nominal)
    add_shape(doc, grp, "cradle_tubes", "cradle_tubes_40x40x3", G.cradle_tubes(), "galv")
    add_shape(doc, grp, "cradle_pads", "cradle_rubber_strips_5mm", G.cradle_pads(), "rubber")
    add_shape(doc, grp, "cradle_bolts", "cradle_bolts_4xM10", G.cradle_bolts(), "zinc")
    add_shape(doc, grp, "straps", "tank_straps_50x3", G.straps(), "galv")
    add_shape(doc, grp, "tank_shell", "tank_PE_%dl_wall_6" % P.tank_nominal, G.tank_shell(), "tank")
    add_shape(doc, grp, "tank_fittings", "fill_cap_vent_bulkhead_fittings", G.tank_fittings(), "plastic")
    add_shape(doc, grp, "level_sensor", "tank_level_sensor_ultrasonic", G.level_sensor(), "plastic")
    return grp


def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "rear_subframe_hangers_control_box")
    add_shape(doc, grp, "sub_plate", "sub_plate_10mm_under_rear_beams", G.sub_plate(), "frame")
    add_shape(doc, grp, "hangers", "boom_hangers_webs_and_clamp_plates_8mm", G.hangers(), "frame")
    add_shape(doc, grp, "sub_bolts", "sub_plate_bolts_8xM10", G.sub_bolts(), "zinc")
    add_shape(doc, grp, "boom_bolts", "boom_clamp_bolts_4xM10", G.boom_bolts(), "zinc")
    add_shape(doc, grp, "box_base", "control_box_base_plate_and_rails", G.box_base(), "galv")
    add_shape(doc, grp, "box_bolts", "control_box_bolts_4xM10", G.box_bolts(), "zinc")
    add_shape(doc, grp, "control_box", "control_box_IP66_vision_computer_valve_driver", G.control_box(), "box")
    return grp


def build_plumbing(doc, parent):
    grp = new_part(doc, parent, "Plumbing", "pump_filter_regulator_hoses")
    add_shape(doc, grp, "pump", "pump_diaphragm_24V_11lpm", G.pump(), "pump")
    add_shape(doc, grp, "pump_mounts", "pump_filter_regulator_brackets", G.pump_mounts(), "frame")
    add_shape(doc, grp, "filter_bowl", "suction_filter_50_mesh", G.filter_bowl(), "plastic")
    add_shape(doc, grp, "regulator", "pressure_regulator_bypass_sensor", G.regulator(), "red")
    add_shape(doc, grp, "hose_suction", "hose_suction_tank_filter_pump", G.suction_hose(), "hose")
    add_shape(doc, grp, "hose_return", "hose_bypass_return_to_tank", G.return_hose(), "hose")
    add_shape(doc, grp, "hose_pressure", "hose_pressure_to_boom", G.pressure_hose(), "hose")
    return grp


def build_boom(doc, parent, pl):
    grp = new_part(doc, parent, "Boom", "boom_%dmm_%d_nozzles" % (P.work_width, P.n_nozzles))
    cen = new_part(doc, grp, "Centre_section", "centre_section_1250_fixed")
    add_shape(doc, cen, "centre_tube", "centre_tube_steel_40x40x2_end_plates", G.centre_tube(), "galv")
    add_shape(doc, cen, "hinge_lugs", "hinge_lugs_8mm", G.hinge_lugs(), "galv")
    add_shape(doc, cen, "hinge_pins", "hinge_pins_D16", G.hinge_pins(), "steel")
    add_shape(doc, cen, "act_brackets", "actuator_base_brackets_6mm", G.act_brackets(), "galv")
    add_shape(doc, cen, "act_base_pins", "actuator_base_pins_D10", G.act_base_pins(), "steel")
    add_shape(doc, cen, "centre_pipe", "wet_pipe_stainless_half_inch_centre", G.centre_pipe(), "stainless")
    add_shape(doc, cen, "swivels", "hinge_swivels_coaxial", G.swivels(), "stainless")
    add_shape(doc, cen, "centre_clips", "pipe_clips_centre", G.centre_clips(), "plastic")
    add_shape(doc, cen, "centre_nozzles", "nozzle_bodies_pwm_centre_5x", G.centre_nozzles(), "nozzle")
    for s, tag in ((1, "right"), (-1, "left")):
        w = new_part(doc, grp, "Wing_" + tag, "wing_%s_1250_folding" % tag, pl["Wing_" + tag])

        def side(shape, s=s):
            return shape if s > 0 else G.mirror_x(shape)
        add_shape(doc, w, "wing_end_plate_" + tag, "wing_end_plate_stop_4mm_" + tag, side(G.wing_end_plate_right()), "galv")
        add_shape(doc, w, "wing_tube_" + tag, "wing_tube_alu_40x40x3_" + tag, side(G.wing_tube_right()), "alu")
        add_shape(doc, w, "knuckle_" + tag, "wing_knuckle_lever_12mm_" + tag, side(G.knuckle_right()), "galv")
        add_shape(doc, w, "lever_pin_" + tag, "lever_pin_D10_" + tag, side(G.lever_pin_right()), "steel")
        add_shape(doc, w, "wing_pipe_" + tag, "wet_pipe_stainless_wing_" + tag, side(G.wing_pipe_right()), "stainless")
        add_shape(doc, w, "wing_clips_" + tag, "pipe_clips_wing_" + tag, side(G.wing_clips_right()), "plastic")
        add_shape(doc, w, "wing_nozzles_" + tag, "nozzle_bodies_pwm_wing_5x_" + tag, side(G.wing_nozzles_right()),
                  "nozzle")
        add_shape(doc, w, "tip_guard_" + tag, "tip_guard_tube_D20_" + tag, side(G.tip_guard_right()), "galv")
        a = new_part(doc, grp, "Act_" + tag, "fold_actuator_%s_1000N_stroke_%d" % (tag, P.act_stroke), pl["Act_" + tag])
        add_shape(doc, a, "act_body_" + tag, "actuator_body_24V_" + tag, side(G.act_body_right()), "actuator")
        r = new_part(doc, a, "Act_%s_rod" % tag, "actuator_rod_%s" % tag, pl["Act_%s_rod" % tag])
        add_shape(doc, r, "act_rod_" + tag, "actuator_rod_clevis_" + tag, side(G.act_rod_right()), "steel")
    return grp


def build_mast(doc, parent):
    grp = new_part(doc, parent, "Camera_mast", "camera_mast_front")
    add_shape(doc, grp, "mast_plate", "mast_plate_10mm_under_front_beams", G.mast_plate(), "frame")
    add_shape(doc, grp, "mast_bolts", "mast_plate_bolts_8xM10", G.mast_bolts(), "zinc")
    add_shape(doc, grp, "mast_tube", "mast_tube_50x50x3_cap", G.mast_tube(), "frame")
    add_shape(doc, grp, "mast_gussets", "mast_gussets_8mm", G.mast_gussets(), "frame")
    add_shape(doc, grp, "braces", "mast_braces_D25_feet", G.braces(), "frame")
    add_shape(doc, grp, "camera_arms", "camera_tilt_arms_6mm", G.camera_arms(), "frame")
    add_shape(doc, grp, "camera", "camera_5MP_global_shutter_IP67_hood", G.camera(), "camera")
    add_shape(doc, grp, "camera_glass", "camera_lens_window", G.camera_glass(), "glass")
    if P.gnss_on_mast:
        add_shape(doc, grp, "antenna", "gnss_antenna_moved_to_mast_top", G.antenna(), "white")
    return grp


def build_into(doc, parent=None, left=0.0, right=0.0):
    """Put the sprayer in a document, in robot coordinates (also used by animate_ssp.py)."""
    pl = pose_placements(left, right)
    root = new_part(doc, parent, ROOT, "spot_sprayer_boom_3750")
    build_tank(doc, root)
    build_mount(doc, root)
    build_plumbing(doc, root)
    build_boom(doc, root, pl)
    build_mast(doc, root)
    return root


def build_robot(doc):
    """Real robot model from 'agbot design' (read only)."""
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


ROBOT_GNSS = ("gnss_dome", "gnss_mount")


def build(left=0.0, right=0.0, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Spot sprayer boom 3750"
    doc.Comment = ("Generated by build_ssp.py from ssp_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Fold the wings with build_ssp.set_fold(left, right).")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, left, right)
    if robot is not None:
        set_robot_visible(bool(show_robot), doc)
    doc.recompute()
    if save:
        doc.saveAs(SAVE_BASE + ".FCStd")
    if step:
        export_step(doc, SAVE_BASE + ".step")
    return doc


def active_doc(doc=None):
    if doc is not None:
        return doc
    d = App.ActiveDocument
    if d is not None and d.getObject(ROOT) is not None:
        return d
    for n in App.listDocuments():
        d = App.getDocument(n)
        if d.getObject(ROOT) is not None:
            return d
    raise RuntimeError("no spot sprayer document open")


def sprayer_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in sprayer_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible and not (P.gnss_on_mast and o.Name in ROBOT_GNSS)


def export_step(doc, path):
    import Import
    objs = []
    for o in sprayer_objects(doc):
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


EXCLUDE = ()


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        if not sa.BoundBox.intersect(sb.BoundBox):
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
    return [o for o in objs if not o.Name.startswith(EXCLUDE)] if EXCLUDE else list(objs)


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3) in the current pose: sprayer parts among themselves and against the (visible and hidden)
    robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in _checked(sprayer_objects(doc))]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def _group_of(obj):
    parent = obj.getParentGeoFeatureGroup()
    while parent is not None:
        if parent.Name in MOVING:
            return parent.Name.replace("_rod", "")
        parent = parent.getParentGeoFeatureGroup()
    return "fixed"


def fit_poses(step=10.0):
    n = int(P.fold_up / step)
    angles = [i * step for i in range(n + 1)] + [P.fold_stop]
    return [(a, a) for a in angles]


def check_fit(doc=None, poses=None, tol=1.0):
    """Interference over the whole fold of both wings (pairs that move relative to each other). Must be empty."""
    doc = active_doc(doc)
    set_fold(doc=doc)
    out = {}
    base = check_interference(doc, tol)
    if base:
        out["reference"] = base
    mine = _checked(sprayer_objects(doc))
    group = {o.Name: _group_of(o) for o in mine}
    moving = [o for o in mine if group[o.Name] != "fixed"]
    fixed = [(o, global_shape(o)) for o in mine if group[o.Name] == "fixed"]
    fixed += [(o, global_shape(o)) for o in robot_objects(doc)]
    for pose in poses or fit_poses():
        set_fold(*pose, doc=doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if group[mv[i][0].Name] != group[mv[j][0].Name]]
        hits = _overlaps(pairs, tol)
        if hits:
            out[pose] = hits
    set_fold(doc=doc)
    return out


def _min_dist(objs, targets):
    best = (1e9, None, None)
    for o in objs:
        s = global_shape(o)
        for t in targets:
            ts = global_shape(t)
            if s.BoundBox.isValid() and ts.BoundBox.isValid():
                d = s.distToShape(ts)[0]
                if d < best[0]:
                    best = (d, o.Name, t.Name)
    return (round(best[0], 1), best[1], best[2])


def set_steering(left_deg, right_deg, doc):
    for name, angle in (("FL_steered", left_deg), ("FR_steered", right_deg)):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle))
    doc.recompute()


def clearance(doc=None):
    """Smallest distances (mm): boom and wings to the rear tyres and wheel brackets over the fold, mast to the front
    wheel units at full steering lock, rear subframe to the wheel units, tank to the steering stacks."""
    doc = active_doc(doc)
    if doc.getObject("Robot") is None:
        return {}
    out = {}
    rear = [doc.getObject(n) for n in ("RL_tire", "RR_tire", "RL_side_l", "RL_side_r", "RR_side_l", "RR_side_r",
                                       "RL_top_plate", "RR_top_plate", "RL_spacer", "RR_spacer", "RL_frame_bolts",
                                       "RR_frame_bolts")]
    rear = [o for o in rear if o is not None]
    boom = [o for o in sprayer_objects(doc) if o.getParentGeoFeatureGroup() is not None and
            (_group_of(o) != "fixed" or o.getParentGeoFeatureGroup().Name == "Centre_section")]
    for phi in (0.0, 45.0, P.fold_up):
        set_fold(phi, phi, doc)
        out["boom_to_rear_wheels_phi_%d" % phi] = _min_dist(boom, rear)
    set_fold(doc=doc)
    mount = [doc.getObject(n) for n in ("sub_plate", "hangers", "sub_bolts", "box_base", "box_bolts", "control_box",
                                        "pump", "filter_bowl", "regulator", "hose_suction", "hose_return",
                                        "hose_pressure")]
    out["rear_mount_to_rear_wheel_units"] = _min_dist(mount, rear)
    front = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
    mast = [o for o in doc.getObject("Camera_mast").OutListRecursive if o.TypeId == "Part::Feature"]
    for steer in (-P.robot_steer_max, P.robot_steer_max):
        set_steering(steer, steer, doc)
        out["mast_to_front_units_steer_%+d" % steer] = _min_dist(mast, front)
    set_steering(0.0, 0.0, doc)
    tank = [doc.getObject(n) for n in ("tank_shell", "cradle_tubes", "straps", "tank_fittings", "level_sensor")]
    out["tank_to_front_units"] = _min_dist(tank, front)
    gnss = [doc.getObject(n) for n in ROBOT_GNSS if doc.getObject(n) is not None]
    out["mast_to_old_gnss_mount"] = _min_dist(mast, gnss)
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
MASS_FIXED = {"pump": P.pump_kg, "filter_bowl": 0.6, "regulator": 1.2, "control_box": 6.0, "camera_glass": 0.02,
              "camera": 0.9, "antenna": 0.0, "level_sensor": 0.3, "tank_fittings": 0.6,
              "centre_nozzles": 5 * P.kg_nozzle, "wing_nozzles": 5 * P.kg_nozzle,
              "act_body": P.act_kg - 0.4, "act_rod": 0.4}
DENSITY = (("tank_shell", 0.95e-6), ("cradle_pads", 1.2e-6), ("wing_tube", 2.7e-6), ("centre_clips", 1.2e-6),
           ("wing_clips", 1.2e-6), ("hose_", 1.6e-6), ("centre_pipe", 2.9e-6), ("wing_pipe", 2.9e-6),
           ("tip_guard", 2.8e-6), ("braces", 3.0e-6), ("swivels", 4.0e-6))
STEEL = 7.85e-6


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key in sorted(MASS_FIXED, key=len, reverse=True):
        if obj.Name.startswith(key):
            return MASS_FIXED[key], cg
    dens = STEEL
    for key, d in DENSITY:
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) in the current pose, tank empty."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(sprayer_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for name in ("Tank", "Mount", "Plumbing", "Boom", "Camera_mast", "Wing_right", "Act_right"):
        ms, cs = _sum(objs_of(name))
        out[name.lower() + "_kg"] = round(ms, 2)
        if name in ("Boom", "Wing_right"):
            out[name.lower() + "_cg"] = (round(cs.x), round(cs.y), round(cs.z))
    out["wing_cg_r"] = round(out["wing_right_cg"][0] - P.centre_half)
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in sprayer_objects(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin)), (
        round(bb.XMax), round(bb.YMax), round(bb.ZMax))


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
    tgt = V(*target) if target is not None else V(0, 0, 600)
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
FOOTPRINT = "render_camera_footprint"


def add_floor(doc, y=(-1500.0, 1400.0), x=(-2100.0, 2100.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.62, 0.70, 0.52)
    obj.ViewObject.Transparency = 30
    return obj


def add_footprint(doc):
    obj = doc.addObject("Part::Feature", FOOTPRINT)
    obj.Shape = G.ground_polygon(C.footprint(), z=1.0)
    obj.ViewObject.ShapeColor = (0.95, 0.75, 0.15)
    obj.ViewObject.Transparency = 45
    c = C.camera()
    band = doc.addObject("Part::Feature", FOOTPRINT + "_band")
    band.Shape = Part.makeCompound([G.box_span((-P.work_width / 2.0, P.work_width / 2.0), (y - 6.0, y + 6.0), (1.5, 3.0))
                                    for y in c["band_y"][:1]] +
                                   [G.box_span((x - 4.0, x + 4.0), (P.boom_y - 60.0, c["band_y"][0]), (1.5, 2.5))
                                    for x in (-P.work_width / 2.0, P.work_width / 2.0)])
    band.ViewObject.ShapeColor = (0.85, 0.15, 0.10)
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


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_floor(doc)
    out.append(save_view("1_work_iso_on_robot.png", (1.0, 1.2, -0.75), target=(0, -250, 500), height=3500))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, 0, 820), height=2100))
    out.append(save_view("3_rear_on_robot.png", (0.0, 1.0, -0.12), target=(0, 0, 700), height=2300))
    remove(doc, [GROUND])
    add_footprint(doc)
    add_floor(doc, y=(-1300.0, 5000.0), x=(-3900.0, 3900.0))
    out.append(save_view("4_top_camera_footprint.png", (0.0, 0.0, -1.0), target=(0, 1850, 0), up=(0.0, 1.0, 0.0),
                         height=6500, size_px=(1500, 1400)))
    remove(doc, [GROUND, FOOTPRINT, FOOTPRINT + "_band"])
    add_floor(doc)
    set_fold(90.0, 90.0, doc)
    out.append(save_view("5_folded_iso_rear.png", (-1.0, 1.1, -0.6), target=(0, -100, 900), height=3000))
    set_fold(0.0, 45.0, doc)
    out.append(save_view("6_right_wing_folding_rear.png", (0.0, 1.0, -0.15), target=(250, 0, 800), height=2500))
    remove(doc, [GROUND])
    set_robot_visible(False, doc)
    set_fold(0.0, 30.0, doc)
    out.append(save_view("7_hinge_actuator_detail.png", (-0.7, 1.0, -0.55), target=(470, -850, 600), height=650))
    set_fold(doc=doc)
    out.append(save_view("8_nozzle_detail.png", (-0.8, 0.9, 0.35), target=(150, -850, 470), height=520))
    out.append(save_view("9_pump_filter_regulator.png", (-1.0, -0.35, 0.45), target=(0, -520, 560), height=800))
    set_robot_visible(True, doc)
    out.append(save_view("10_mast_camera_front.png", (-0.9, -1.0, -0.35), target=(0, 450, 1080), height=1750))
    App.closeDocument(doc.Name)
    build()
    return out
