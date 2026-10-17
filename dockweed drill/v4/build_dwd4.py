"""Modelboom van de Dockweed drill v4, met controle (interferentie, vrijloop), massa, export en afbeeldingen.

Gebruik in FreeCAD (map in sys.path, of via run_in_freecad.py):
    import build_dwd4
    build_dwd4.build()                              # werkstand (x 150, frees 150 diep), slaat het FCStd op
    build_dwd4.build(x=-500, z=280, show_robot=True, save_path=None)   # rijstand met de robot erbij
    build_dwd4.check_interference()                 # moet leeg zijn
    build_dwd4.check_poses()                        # eindstanden X en Z tegen robot en vaste delen
    build_dwd4.clearance()                          # kleinste afstand tot banden en wielbeugels
    build_dwd4.mass_properties()
    build_dwd4.render_all()                         # afbeeldingen in previews/, STEP en DXF
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd4_params as P
import dwd4_parts as G

DOC_NAME = "Dockweed_drill_v4"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Dockweed_drill_v4.FCStd")
STEP_PATH = os.path.join(FOLDER, "Dockweed_drill_v4.step")
DXF_DIR = os.path.join(FOLDER, "dxf")
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
AGBOT_MODULES = ("agbot_params", "agbot_parts", "build_agbot")

COLOR = {
    "frame": (0.25, 0.27, 0.30),
    "galv": (0.62, 0.66, 0.68),
    "guard": (0.62, 0.66, 0.68),
    "alu": (0.80, 0.82, 0.85),
    "chrome": (0.72, 0.74, 0.77),
    "steel": (0.55, 0.57, 0.60),
    "stainless": (0.83, 0.85, 0.87),
    "hardox": (0.95, 0.72, 0.08),
    "orange": (0.90, 0.40, 0.06),
    "black": (0.08, 0.08, 0.09),
    "blue": (0.10, 0.25, 0.55),
    "grey": (0.55, 0.57, 0.60),
    "rubber": (0.13, 0.13, 0.13),
    "pe": (0.94, 0.94, 0.88),
    "red": (0.80, 0.12, 0.10),
    "led": (0.98, 0.92, 0.55),
    "ground": (0.45, 0.62, 0.31),
    "soil": (0.42, 0.29, 0.16),
    "leaf": (0.18, 0.45, 0.12),
    "root": (0.45, 0.30, 0.20),
}
TRANSPARENT = {"stainless": 25, "guard": 65}
ROBOT_TRANSPARENCY = 0
SIDES = ((-1, "left"), (1, "right"))

# materiaal per kleur (kg/mm3); gekochte delen met een catalogusmassa staan in MASS_FIXED
DENSITY = {"alu": 2.70e-6, "rubber": 1.2e-6, "pe": 0.95e-6, "stainless": 7.9e-6, "led": 1.5e-6}
STEEL = 7.85e-6
MASS_FIXED = {"spindle_motor": P.motor_kg, "x_motor": 1.6, "x_gearbox": 0.9, "jack_motor": 1.8, "ebox": 3.0,
              "camera": 0.4, "led_bar": 0.6, "bearing_lower": P.ucp_kg, "bearing_upper": P.ucp_kg,
              "motor_sprocket": 1.9, "spindle_sprocket": 0.35, "drive_chain": 0.9,
              "jack_head": 2.5,
              "chain_lower": 0.25, "chain_upper": 0.15, "chain_bend": 0.05, "spiral_cable": 0.4,
              "pot_sensor": 0.05, "limit_switch": 0.05, "x_pulley": 0.15, "x_idlers": 0.1}


# ---------------------------------------------------------------------
# Hulpfuncties boom
# ---------------------------------------------------------------------
def new_part(doc, parent, name, label, placement=None):
    part = doc.addObject("App::Part", name)
    part.Label = label
    if placement is not None:
        part.Placement = placement
    if parent is not None:
        parent.addObject(part)
    return part


def add_shape(doc, parent, name, label, shape, color, visible=True, transparency=None):
    if isinstance(shape, (list, tuple)):
        shape = Part.makeCompound(list(shape))
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Material", "Dockweed")
    obj.Material = color
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
        view.Transparency = TRANSPARENT.get(color, 0) if transparency is None else transparency
    return obj


def translation(x=0.0, y=0.0, z=0.0):
    return App.Placement(V(x, y, z), App.Rotation())


def spin_placement(angle):
    """Rotatie van het gereedschap om de spilas (graden)."""
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle), V(0, G.spindle_y(), 0))


def pot_rim(z, ground=0.0):
    """Hoogte van de potrand: hangt pot_rim onder de freesonderkant, of staat op de grond."""
    return max(z - P.pot_rim, ground)


def pot_placement(z, ground=0.0):
    return translation(z=pot_rim(z, ground) - G.pot_rim_ref())


# ---------------------------------------------------------------------
# Opbouw
# ---------------------------------------------------------------------
def build_headstock(doc, root):
    hs = new_part(doc, root, "Headstock", "headstock_robot_mount")
    for side, tag in SIDES:
        add_shape(doc, hs, "hs_top_" + tag, "headstock_top_plate_8mm_" + tag, G.hs_top_plate(side), "frame")
        add_shape(doc, hs, "hs_clamp_" + tag, "headstock_clamp_plate_8mm_" + tag, G.hs_clamp_plate(side), "frame")
        add_shape(doc, hs, "hs_back_" + tag, "headstock_back_plate_8mm_" + tag, G.hs_back_plate(side), "frame")
        add_shape(doc, hs, "hs_bolts_" + tag, "headstock_bolts_M10_" + tag, G.hs_bolts(side), "galv")
        add_shape(doc, hs, "upright_" + tag, "upright_50x50x3_" + tag, G.upright(side), "frame")
        add_shape(doc, hs, "upright_cap_" + tag, "upright_cap_6mm_" + tag, G.upright_cap(side), "frame")
        add_shape(doc, hs, "gusset_" + tag, "gusset_6mm_" + tag, G.gusset(side), "frame")
    add_shape(doc, hs, "hs_cross", "cross_tube_40x40x3", G.cross_tube(), "frame")
    return hs


def build_x_axis(doc, root):
    xa = new_part(doc, root, "X_axis", "x_axis_pto_tubes")
    for zp, lvl in zip(P.xbar_z, ("lower", "upper")):
        add_shape(doc, xa, "pto_tube_" + lvl, "pto_inner_tube_49x39_5x4_5_" + lvl, G.pto_tube(zp), "frame")
        for side, tag in SIDES:
            add_shape(doc, xa, "flange_%s_%s" % (lvl, tag), "support_flange_8mm_%s_%s" % (lvl, tag),
                      G.support_flange(side, zp), "frame")
            add_shape(doc, xa, "flange_bolts_%s_%s" % (lvl, tag), "support_flange_bolts_M10_%s_%s" % (lvl, tag),
                      G.support_flange_bolts(side, zp), "galv")
            add_shape(doc, xa, "rib_%s_%s" % (lvl, tag), "support_rib_10mm_%s_%s" % (lvl, tag),
                      G.support_rib(side, zp), "frame")
    for side, tag in SIDES:
        add_shape(doc, xa, "end_plate_" + tag, "end_plate_steel_12mm_" + tag, G.end_plate(side), "frame")
        add_shape(doc, xa, "belt_bracket_" + tag, "belt_clamp_bracket_6mm_" + tag, G.belt_clamp_bracket(side), "galv")
        add_shape(doc, xa, "belt_clamp_" + tag, "belt_clamp_" + tag, G.belt_clamp(side), "galv")
    add_shape(doc, xa, "belt", "belt_HTD5M_15mm_steel_cord", G.belt(), "black")
    add_shape(doc, xa, "limit_switch", "limit_switch_inductive_M12_x_min", G.limit_switch(), "red")
    add_shape(doc, xa, "end_stop", "end_stop_rubber_x_max", G.end_stop(), "rubber")
    add_shape(doc, xa, "chain_bracket", "cable_chain_bracket", G.chain_bracket(), "galv")
    return xa


def build_electrics(doc, root):
    el = new_part(doc, root, "Electrics", "electrics_fixed")
    add_shape(doc, el, "ebox_plate", "ebox_mounting_plate_3mm", G.ebox_plate(), "galv")
    add_shape(doc, el, "ebox", "ebox_IP65_300x250x120", G.ebox(), "grey")
    add_shape(doc, el, "ebox_glands", "cable_glands_M20", G.ebox_glands(), "black")
    return el


def build_x_carriage(doc, root, x):
    xc = new_part(doc, root, "X_carriage", "x_carriage_moves_in_x", translation(x=x))
    add_shape(doc, xc, "sleeves", "pto_outer_tube_sleeves_57_5x48x4", G.sleeves(), "frame")
    add_shape(doc, xc, "sleeve_pads", "sleeve_pads_8mm", G.sleeve_pads(), "frame")
    add_shape(doc, xc, "sleeve_bolts", "sleeve_bolts_M8", G.sleeve_bolts(), "galv")
    add_shape(doc, xc, "scrapers", "sleeve_scrapers_rubber", G.scrapers(), "rubber")
    add_shape(doc, xc, "grease_nipples", "grease_nipples", G.grease_nipples(), "chrome")
    add_shape(doc, xc, "x_slide", "x_slide_alu_10mm", G.x_slide(), "alu")
    add_shape(doc, xc, "x_gearbox", "planetary_gearbox_5to1_nema23", G.x_gearbox(), "black")
    add_shape(doc, xc, "x_motor", "nema23_closed_loop_3Nm_x", G.x_motor(), "black")
    add_shape(doc, xc, "x_pulley", "pulley_HTD5M_20T", G.x_pulley(), "chrome")
    add_shape(doc, xc, "x_idlers", "idlers_D30", G.x_idlers(), "chrome")
    add_shape(doc, xc, "jack_mount_plate", "jack_mounting_plate_8mm", G.jack_mount_plate(), "frame")
    add_shape(doc, xc, "jack_outer", "drop_leg_jack_outer_tube_65x65x4", G.jack_outer_tube(), "red")
    add_shape(doc, xc, "jack_guide_bush", "jack_guide_bush_PE", G.jack_guide_bush(), "pe")
    add_shape(doc, xc, "jack_head", "drop_leg_jack_bevel_gear_head", G.jack_head(), "red")
    add_shape(doc, xc, "jack_screw", "drop_leg_jack_screw_Tr20", G.jack_screw(), "chrome")
    add_shape(doc, xc, "jack_motor", "nema23_closed_loop_on_jack_crank", G.jack_motor(), "black")
    add_shape(doc, xc, "chain_driver", "cable_chain_driver_3mm", G.chain_driver(), "galv")
    add_shape(doc, xc, "cable_bracket_x", "spiral_cable_bracket_x_slide", G.cable_bracket_x(), "galv")
    return xc


def build_camera(doc, root):
    """Vaste camera hoog boven de werkstrook (zoals Robot Ruud), op de rechter staander."""
    cam = new_part(doc, root, "Camera", "camera_fixed_high")
    add_shape(doc, cam, "camera_mast", "camera_mast_alu_40x40x3", G.camera_mast(), "alu")
    add_shape(doc, cam, "camera_arm", "camera_arm_alu_40x40x3", G.camera_arm(), "alu")
    add_shape(doc, cam, "camera_crossbar", "camera_crossbar_alu_40x40x3", G.camera_crossbar(), "alu")
    add_shape(doc, cam, "camera", "camera_industrial_usb3", G.camera(), "black")
    add_shape(doc, cam, "led_bar", "led_light_bar_48V", G.led_bar(), "led")
    return cam


def build_z_carriage(doc, xc, z):
    zc = new_part(doc, xc, "Z_carriage", "z_jack_inner_tube_moves_in_z", translation(z=z - P.z_ref))
    add_shape(doc, zc, "inner_tube", "drop_leg_jack_inner_tube_50x50x5", G.inner_tube(), "red")
    add_shape(doc, zc, "inner_guide_ring", "jack_guide_ring_PE", G.inner_guide_ring(), "pe")
    add_shape(doc, zc, "inner_foot_plate", "jack_foot_plate_10mm", G.inner_foot_plate(), "orange")
    add_shape(doc, zc, "cable_bracket_z", "spiral_cable_bracket_top_plate", G.cable_bracket_z(), "galv")
    add_shape(doc, zc, "sb_back", "spindle_bracket_back_plate_6mm", G.sb_back_plate(), "orange")
    add_shape(doc, zc, "sb_back_bolts", "spindle_bracket_bolts_M10", G.sb_back_bolts(), "galv")
    add_shape(doc, zc, "sb_lower", "spindle_bracket_lower_plate_8mm", G.sb_plate_lower(), "orange")
    add_shape(doc, zc, "sb_top", "spindle_bracket_top_plate_8mm", G.sb_top_plate(), "orange")
    for side, tag in SIDES:
        add_shape(doc, zc, "sb_side_" + tag, "spindle_bracket_side_plate_5mm_" + tag, G.sb_side_plate(side), "orange")
    add_shape(doc, zc, "sb_bearing_plate", "spindle_bracket_bearing_plate_10mm", G.sb_bearing_plate(), "orange")
    add_shape(doc, zc, "bearing_lower", "pillow_block_UCP204_lower", G.bearing_lower(), "blue")
    add_shape(doc, zc, "bearing_upper", "pillow_block_UCP204_upper", G.bearing_upper(), "blue")
    add_shape(doc, zc, "bearing_bolts", "bearing_bolts_M12", G.bearing_bolts(), "galv")
    add_shape(doc, zc, "spindle_shaft", "spindle_shaft_D20_C45", G.spindle_shaft(), "chrome")
    add_shape(doc, zc, "spindle_tube", "spindle_tube_42_4x4_welded", G.spindle_tube(), "steel")
    add_shape(doc, zc, "spindle_flange", "spindle_flange_D110x12_welded", G.spindle_flange(), "chrome")
    add_shape(doc, zc, "spindle_sprocket", "sprocket_10B_12T_bore20", G.spindle_sprocket(), "steel")
    add_shape(doc, zc, "motor_plate", "spindle_motor_plate_10mm_slotted", G.motor_plate(), "orange")
    add_shape(doc, zc, "spindle_motor", "gearmotor_800W_48V_500rpm_foot", G.spindle_motor(), "black")
    add_shape(doc, zc, "spindle_motor_shaft", "gearmotor_shaft_D19", G.spindle_motor_shaft(), "chrome")
    add_shape(doc, zc, "motor_sprocket", "sprocket_10B_38T_taperlock_2012", G.motor_sprocket(), "steel")
    add_shape(doc, zc, "drive_chain", "chain_10B_1_%d_links" % P.chain_links, G.drive_chain(), "black")
    add_shape(doc, zc, "chain_guard", "chain_guard_2mm", G.chain_guard(), "guard")
    add_shape(doc, zc, "pot_bushes", "pot_rod_bushes_PE_D40", G.pot_bushes(), "pe")
    add_shape(doc, zc, "pot_sensor", "pot_sensor_ground_contact_M12", G.pot_sensor(), "red")
    add_shape(doc, zc, "pot_sensor_bracket", "pot_sensor_bracket_3mm", G.pot_sensor_bracket(), "galv")
    return zc


def build_tool(doc, zc, tool, angle=0.0):
    tl = new_part(doc, zc, "Tool", "tool_%s_rotates_about_spindle" % tool, spin_placement(angle))
    parts = G.cutter_parts() if tool == "cutter" else G.mower_parts()
    for name, shape, color in parts:
        add_shape(doc, tl, name, name, shape, color)
    return tl


def build_pot(doc, xc, z, ground=0.0):
    pot = new_part(doc, xc, "Pot", "pot_rests_on_ground", pot_placement(z, ground))
    add_shape(doc, pot, "pot_shell", "can_steel_pipe_219x3_6", G.pot_shell(), "galv")
    add_shape(doc, pot, "pot_lid", "can_lid_steel_5mm", G.pot_lid(), "galv")
    add_shape(doc, pot, "shaft_seal", "shaft_seal_rubber", G.shaft_seal(), "rubber")
    add_shape(doc, pot, "pot_rods", "pot_rods_D16", G.pot_rods(), "chrome")
    add_shape(doc, pot, "pot_set_rings", "pot_set_rings_D28", G.pot_set_rings(), "chrome")
    return pot


def build_cables(doc, root, x, z):
    cab = new_part(doc, root, "Cables", "cables_follow_x_and_z")
    lower, upper, bend = G.chain_shapes(x)
    add_shape(doc, cab, "chain_lower", "cable_chain_x_lower_run", lower, "black")
    add_shape(doc, cab, "chain_upper", "cable_chain_x_upper_run", upper, "black")
    add_shape(doc, cab, "chain_bend", "cable_chain_x_bend", bend, "black")
    add_shape(doc, cab, "spiral_cable", "spiral_cable_x_to_z", G.spiral_cable(x, z), "black")
    return cab


def build_into(doc, parent=None, x=None, z=None, tool="cutter", ground=0.0, placement=None):
    """Zet het hele werktuig in een bestaand document (ook gebruikt door animate_dwd4.py).
    x = spilhart (robot-x), z = onderkant gereedschap (grond = 0)."""
    x = P.work_x if x is None else x
    z = P.work_z if z is None else z
    root = new_part(doc, parent, "Dockweed_drill", "dockweed_drill_" + P.VARIANT, placement)
    build_headstock(doc, root)
    build_x_axis(doc, root)
    build_electrics(doc, root)
    build_camera(doc, root)
    xc = build_x_carriage(doc, root, x)
    zc = build_z_carriage(doc, xc, z)
    build_tool(doc, zc, tool)
    build_pot(doc, xc, z, ground)
    build_cables(doc, root, x, z)
    return root


def load_robot():
    """build_agbot uit agbots/agbot design (zie ook animate_lfa.load_robot)."""
    if AGBOT_FOLDER in sys.path:
        sys.path.remove(AGBOT_FOLDER)
    sys.path.insert(0, AGBOT_FOLDER)
    for name in AGBOT_MODULES:
        mod = sys.modules.get(name)
        if mod is not None and os.path.dirname(os.path.abspath(mod.__file__)) != os.path.abspath(AGBOT_FOLDER):
            del sys.modules[name]
    import build_agbot
    return build_agbot


def build_robot_reference(doc, visible):
    BA = load_robot()
    ref = new_part(doc, None, "Robot_reference", "robot_reference_NOT_PART_OF_DESIGN")
    BA.build_chassis(doc, ref)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, ref, tag, shapes, 0.0)
    set_robot_reference(visible, doc)
    return ref


def set_robot_reference(visible, doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    for obj in doc.getObject("Robot_reference").OutListRecursive:
        if obj.TypeId == "Part::Feature" and obj.ViewObject is not None:
            obj.ViewObject.Visibility = visible
            obj.ViewObject.Transparency = ROBOT_TRANSPARENCY


def build(x=None, z=None, tool="cutter", save_path=SAVE_PATH, show_robot=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Dockweed drill " + P.VARIANT
    doc.Comment = ("Gegenereerd met build_dwd4.py uit dwd4_params.py. Robotcoordinaten: x = rechts, y = rijrichting "
                   "(voor = +y), z = omhoog, grond = z 0. Het portaal hangt achter de robot. "
                   "Stand: build(x=..., z=...), x = spilhart, z = onderkant gereedschap.")
    build_into(doc, None, x, z, tool)
    build_robot_reference(doc, show_robot)
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    return doc


def set_pose(doc, x, z, ground=0.0, angle=None):
    """Stand van X-slede, Z-slede, pot en kabels in een bestaand document."""
    doc.getObject("X_carriage").Placement = translation(x=x)
    doc.getObject("Z_carriage").Placement = translation(z=z - P.z_ref)
    doc.getObject("Pot").Placement = pot_placement(z, ground)
    if angle is not None:
        doc.getObject("Tool").Placement = spin_placement(angle)
    lower, upper, bend = G.chain_shapes(x)
    doc.getObject("chain_lower").Shape = lower
    doc.getObject("chain_upper").Shape = upper
    doc.getObject("chain_bend").Shape = bend
    doc.getObject("spiral_cable").Shape = G.spiral_cable(x, z)


# ---------------------------------------------------------------------
# Controle
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def implement_objects(doc):
    return [o for o in doc.getObject("Dockweed_drill").OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    ref = doc.getObject("Robot_reference") or doc.getObject("Robot")
    if ref is None:
        return []
    impl = {o.Name for o in implement_objects(doc)}
    return [o for o in ref.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in impl]


def check_interference(doc=None, include_robot=True, tol=1.0):
    """Volume-overlap (mm3) tussen alle onderdelen van het werktuig, en (include_robot) tegen het robotmodel."""
    doc = doc or App.getDocument(DOC_NAME)
    items = [(o, global_shape(o)) for o in implement_objects(doc)]
    n_impl = len(items)
    if include_robot:
        items += [(o, global_shape(o)) for o in robot_objects(doc)]
    hits = []
    for i in range(n_impl):
        oa, sa = items[i]
        ba = sa.BoundBox
        for j in range(i + 1, len(items)):
            ob, sb = items[j]
            if not ba.intersect(sb.BoundBox):
                continue
            try:
                vol = sa.common(sb).Volume
            except Exception as exc:
                hits.append((oa.Label, ob.Label, "error %s" % exc))
                continue
            if vol > tol:
                hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits


POSES = [(x, z) for x in (P.x_min, 0.0, P.x_max) for z in (P.drive_z, -P.depth_max)]


def check_poses(doc=None, poses=POSES):
    """Eindstanden van X en Z: interferentie van het hele werktuig (met robot). Zet daarna de stand terug."""
    doc = doc or App.getDocument(DOC_NAME)
    x0, z0 = current_pose(doc)
    out = {}
    try:
        for x, z in poses:
            set_pose(doc, x, z)
            doc.recompute()
            out[(x, z)] = check_interference(doc)
    finally:
        set_pose(doc, x0, z0)
        doc.recompute()
    return out


def current_pose(doc):
    x = doc.getObject("X_carriage").Placement.Base.x
    z = doc.getObject("Z_carriage").Placement.Base.z + P.z_ref
    return x, z


CLEARANCE_GROUPS = ("Pot", "Tool", "Z_carriage", "X_carriage", "X_axis", "Electrics")     # aanbouwbok zit vast
CLEARANCE_ROBOT = ("RL_tire", "RR_tire", "RL_side_l", "RL_side_r", "RR_side_l", "RR_side_r", "RL_top_plate",
                   "RR_top_plate", "RL_spacer", "RR_spacer", "upper_beam_left_inner", "upper_beam_right_inner",
                   "upper_beam_left_outer", "upper_beam_right_outer", "lower_beam_rear_outer")


def clearance(doc=None, poses=None):
    """Kleinste afstand (mm) per groep tot de achterwielen, wielbeugels en balken van de robot, over de standen."""
    doc = doc or App.getDocument(DOC_NAME)
    poses = poses or POSES
    x0, z0 = current_pose(doc)
    robot = [global_shape(doc.getObject(n)) for n in CLEARANCE_ROBOT if doc.getObject(n)]
    robot_c = Part.makeCompound(robot)
    out = {}
    try:
        for x, z in poses:
            set_pose(doc, x, z)
            doc.recompute()
            for grp in CLEARANCE_GROUPS:
                objs = [o for o in doc.getObject(grp).OutListRecursive if o.TypeId == "Part::Feature"]
                if grp == "X_carriage":       # alleen de slede zelf, niet de Z-slede en de pot
                    sub = {o.Name for n in ("Z_carriage", "Pot") for o in doc.getObject(n).OutListRecursive}
                    objs = [o for o in objs if o.Name not in sub]
                if grp == "Z_carriage":
                    sub = {o.Name for o in doc.getObject("Tool").OutListRecursive}
                    objs = [o for o in objs if o.Name not in sub]
                d = Part.makeCompound([global_shape(o) for o in objs]).distToShape(robot_c)[0]
                out[grp] = min(out.get(grp, 1e9), round(d, 1))
    finally:
        set_pose(doc, x0, z0)
        doc.recompute()
    return out


# ---------------------------------------------------------------------
# Massa
# ---------------------------------------------------------------------
def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    if obj.Name in MASS_FIXED:
        return MASS_FIXED[obj.Name], cg
    return vol * DENSITY.get(getattr(obj, "Material", ""), STEEL), cg


def _sum(objs):
    m = 0.0
    c = V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def _features(doc, name):
    return [o for o in doc.getObject(name).OutListRecursive if o.TypeId == "Part::Feature"]


def mass_properties(doc=None):
    """Massa (kg) en zwaartepunt (robotcoordinaten): heel werktuig, per groep en de bewegende delen.
    x_moving = alles wat met de X-as meebeweegt (incl. Z-slede, pot, gereedschap)."""
    doc = doc or App.getDocument(DOC_NAME)
    feats = implement_objects(doc)
    m_all, c_all = _sum(feats)
    groups = {}
    for name in ("Headstock", "X_axis", "Electrics", "Camera", "Cables", "Pot", "Tool"):
        groups[name] = round(_sum(_features(doc, name))[0], 1)
    zc_all = _features(doc, "Z_carriage")
    xc_all = _features(doc, "X_carriage")
    groups["Z_carriage"] = round(_sum(zc_all)[0] - groups["Tool"], 1)
    groups["X_carriage"] = round(_sum(xc_all)[0] - groups["Z_carriage"] - groups["Tool"] - groups["Pot"], 1)
    m_x, c_x = _sum(xc_all)
    m_z, c_z = _sum(zc_all)
    return {"implement_kg": round(m_all, 1), "implement_cg": tuple(round(v) for v in (c_all.x, c_all.y, c_all.z)),
            "x_moving_kg": round(m_x, 1), "x_moving_cg": tuple(round(v) for v in (c_x.x, c_x.y, c_x.z)),
            "z_moving_kg": round(m_z, 1), "pot_kg": groups["Pot"], "tool_kg": groups["Tool"], "groups": groups}


# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------
def export_step(doc=None, path=STEP_PATH):
    import Import
    doc = doc or App.getDocument(DOC_NAME)
    Import.export(implement_objects(doc), path)
    return path


def laser_parts():
    """(bestandsnaam, shape, normaal): snijcontouren voor laser/plasma. Getekend uit de onderdeelfuncties."""
    def first(s):
        return s.Solids[0]
    mower = {n: s for n, s, c in G.mower_parts()}
    cutter = {n: s for n, s, c in G.cutter_parts()}
    return [
        ("headstock_top_plate_8mm", G.hs_top_plate(-1), "z"),
        ("headstock_clamp_plate_8mm", G.hs_clamp_plate(-1), "z"),
        ("headstock_back_plate_8mm", G.hs_back_plate(-1), "y"),
        ("gusset_6mm", G.gusset(-1), "x"),
        ("support_flange_8mm", G.support_flange(-1, P.xbar_z[0]), "y"),
        ("end_plate_steel_12mm", G.end_plate(-1), "x"),
        ("sleeve_pad_8mm", first(G.sleeve_pads()), "y"),
        ("x_slide_alu_10mm", G.x_slide(), "y"),
        ("jack_mounting_plate_8mm", G.jack_mount_plate(), "y"),
        ("jack_foot_plate_10mm", G.inner_foot_plate(), "z"),
        ("spindle_bracket_back_plate_6mm", G.sb_back_plate(), "y"),
        ("spindle_bracket_lower_plate_8mm", G.sb_plate_lower(), "z"),
        ("spindle_bracket_bearing_plate_10mm", G.sb_bearing_plate(), "y"),
        ("spindle_bracket_top_plate_8mm", G.sb_top_plate(), "z"),
        ("spindle_motor_plate_10mm", G.motor_plate(), "y"),
        ("spindle_bracket_side_plate_5mm", G.sb_side_plate(-1), "x"),
        ("can_lid_steel_5mm", G.pot_lid(), "z"),
        ("cutter_cross_lower_hardox_10mm", cutter["cutter_cross_lower"], "z"),
        ("cutter_cross_upper_hardox_10mm", cutter["cutter_cross_upper"], "z"),
        ("cutter_tooth_hardox_10mm", first(cutter["cutter_teeth"]), "y"),
        ("cutter_flange_10mm", cutter["cutter_flange"], "z"),
        ("mower_disc_4mm", mower["mower_disc"], "z"),
        ("mower_flange_10mm", mower["mower_flange"], "z"),
    ]


def _flat(shape, normal):
    bb = shape.BoundBox
    if normal == "z":
        mid = bb.ZMin + 0.8 * (bb.ZMax - bb.ZMin)        # boven de afschuining van de snijkanten
        c = Part.makeCompound(shape.slice(V(0, 0, 1), mid))
        c.translate(V(-bb.XMin, -bb.YMin, -mid))
    elif normal == "y":
        mid = (bb.YMin + bb.YMax) / 2
        c = Part.makeCompound(shape.slice(V(0, 1, 0), mid))
        c.translate(V(-bb.XMin, -mid, -bb.ZMin))
        c.rotate(V(0, 0, 0), V(1, 0, 0), 90)
    else:
        mid = (bb.XMin + bb.XMax) / 2
        c = Part.makeCompound(shape.slice(V(1, 0, 0), mid))
        c.translate(V(-mid, -bb.YMin, -bb.ZMin))
        c.rotate(V(0, 0, 0), V(0, 1, 0), -90)
    return c


def export_dxf(folder=DXF_DIR):
    import importDXF
    os.makedirs(folder, exist_ok=True)
    tmp = App.newDocument("dxf_tmp")
    done = []
    try:
        for name, shape, normal in laser_parts():
            obj = tmp.addObject("Part::Feature", "flat")
            obj.Shape = _flat(shape, normal)
            importDXF.export([obj], os.path.join(folder, name + ".dxf"))
            tmp.removeObject(obj.Name)
            done.append(name)
    finally:
        App.closeDocument(tmp.Name)
    return done


# ---------------------------------------------------------------------
# Afbeeldingen
# ---------------------------------------------------------------------
def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, -800, 650)
    eye = tgt - d * 8000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(30000.0)
    if height is None:
        view.fitAll()
    else:
        cam.height.setValue(height)
    return view


def save_view(name, direction, target=None, height=None, up=(0.0, 0.0, 1.0), size=(1600, 1100)):
    import FreeCADGui as Gui
    Gui.updateGui()
    view = set_camera(direction, target, height, up)
    Gui.updateGui()
    view = set_camera(direction, target, height, up)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, name)
    view.saveImage(path, size[0], size[1], "White")
    return path


ENV = "Environment"


def add_environment(doc, plant=None, crushed=None, ground_t=220.0, extent=((-1100, 1100), (-1700, 700))):
    """Maaiveld, een ridderzuring (plant = (x, y)) en een vermorzelde kolom (crushed = (x, y, diepte))."""
    remove_environment(doc)
    env = new_part(doc, None, ENV, "environment_NOT_PART_OF_DESIGN")
    (x0, x1), (y0, y1) = extent
    gr = Part.makeBox(x1 - x0, y1 - y0, ground_t, V(x0, y0, -ground_t))
    if crushed:
        cx, cy, d = crushed
        gr = gr.cut(Part.makeCylinder(P.cutter_d / 2 + 2, ground_t + 2, V(cx, cy, -ground_t - 1)))
        add_shape(doc, env, "env_crushed", "crushed_soil_column", Part.makeCylinder(P.cutter_d / 2, d, V(cx, cy, -d)),
                  "soil", transparency=55)
        add_shape(doc, env, "env_hole_floor", "soil_below_hole",
                  Part.makeCylinder(P.cutter_d / 2 + 2, ground_t - d, V(cx, cy, -ground_t)), "soil", transparency=55)
    add_shape(doc, env, "env_ground", "ground", gr, "ground", transparency=45)
    if plant:
        leaves, root = G.dock_plant(plant[0], plant[1])
        add_shape(doc, env, "env_plant_leaves", "dock_plant_leaves", leaves, "leaf")
        add_shape(doc, env, "env_plant_root", "dock_plant_root", root, "root", transparency=30)
    return env


def remove_environment(doc):
    env = doc.getObject(ENV)
    if env is None:
        return
    names = [o.Name for o in env.OutListRecursive]
    for n in names:
        if doc.getObject(n) is not None:
            doc.removeObject(n)
    doc.removeObject(ENV)


def set_group_transparency(doc, name, value):
    for o in _features(doc, name):
        o.ViewObject.Transparency = value


def render_all(export=True):
    """Alle afbeeldingen, daarna de werkstand opslaan (+ STEP en DXF)."""
    out = []
    ys = G.spindle_y()
    # rijstand met robot
    doc = build(x=-250.0, z=P.drive_z, save_path=None, show_robot=True)
    add_environment(doc, plant=(-250.0, ys - 700.0))
    out.append(save_view("2_driving_iso_rear_left.png", (1.0, 1.0, -0.65), target=(0, -550, 950), height=2700))
    # maaien
    doc = build(x=250.0, z=P.mower_rim, tool="mower", save_path=None, show_robot=True)
    add_environment(doc)
    out.append(save_view("9_mowing_iso_rear_right.png", (-1.0, 1.0, -0.55), target=(150, -800, 800), height=2300))
    # werkstand
    doc = build(save_path=None, show_robot=True)
    add_environment(doc, crushed=(P.work_x, ys, P.depth_std))
    out.append(save_view("1_work_iso_rear_right.png", (-1.0, 1.0, -0.65), target=(0, -650, 950), height=2700))
    out.append(save_view("3_side_left.png", (1.0, 0.0, 0.0), target=(0, -550, 1000), height=2400))
    out.append(save_view("5_rear.png", (0.0, 1.0, 0.0), target=(0, 0, 1000), height=2400))
    remove_environment(doc)
    out.append(save_view("4_top.png", (0.0, 0.0, -1.0), target=(0, -650, 0), height=1900, up=(0.0, 1.0, 0.0)))
    out.append(save_view("7_x_axis_detail.png", (-1.0, 1.4, -0.6), target=(330, -700, 950), height=650))
    out.append(save_view("8_headstock_detail.png", (-1.0, 0.3, -0.35), target=(250, -620, 680), height=560))
    out.append(save_view("10_z_jack_detail.png", (-1.0, 1.3, -0.5), target=(P.work_x, -840, 950), height=1100,
                         size=(1000, 1100)))
    out.append(save_view("11_spindle_drive_detail.png", (-1.0, 1.0, -0.55), target=(P.work_x, ys - 90, 400),
                         height=750, size=(1000, 1000)))
    # detail frees in de grond: alleen spil, pot, gereedschap en een stuk grond
    set_robot_reference(False, doc)
    add_environment(doc, crushed=(P.work_x, ys, P.depth_std),
                    extent=((P.work_x - 330, P.work_x + 330), (ys - 330, ys + 330)))
    hide = [o for n in ("Headstock", "X_axis", "Electrics", "Camera", "Cables") for o in _features(doc, n)]
    for o in hide:
        o.ViewObject.Visibility = False
    set_group_transparency(doc, "Pot", 70)
    out.append(save_view("6_cutter_in_soil_detail.png", (1.0, 0.45, -0.3), target=(P.work_x, ys, 60), height=1000,
                         size=(1100, 1300)))
    remove_environment(doc)
    doc = build(show_robot=False)          # werkstand opslaan
    if export:
        export_step(doc)
        export_dxf()
    return out
