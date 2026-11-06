"""Modelboom van de Dockweed drill v7, met controle (interferentie, vrijloop), massa, export en afbeeldingen.

v7 heeft geen X-as: de spil staat vast op x 0, de robot stuurt naar de plant. Alleen Z beweegt.

Gebruik in FreeCAD (map in sys.path, of via run_in_freecad.py):
    import build_dwd7
    build_dwd7.build()                              # werkstand (frees 150 diep), slaat het FCStd op
    build_dwd7.build(z=200, show_robot=True, save_path=None)   # rijstand met de robot erbij
    build_dwd7.check_interference()                 # moet leeg zijn
    build_dwd7.check_poses()                        # eindstanden Z tegen robot en vaste delen
    build_dwd7.clearance()                          # kleinste afstand tot banden, wielbeugels en balken
    build_dwd7.mass_properties()
    build_dwd7.render_all()                         # afbeeldingen in previews/, STEP en DXF
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd7_params as P
import dwd7_parts as G

DOC_NAME = "Dockweed_drill_v7"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Dockweed_drill_v7.FCStd")
STEP_PATH = os.path.join(FOLDER, "Dockweed_drill_v7.step")
DXF_DIR = os.path.join(FOLDER, "dxf")
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
AGBOT_MODULES = ("agbot_params", "agbot_parts", "build_agbot")

COLOR = {
    "frame": (0.25, 0.27, 0.30),
    "galv": (0.62, 0.66, 0.68),
    "alu": (0.80, 0.82, 0.85),
    "chrome": (0.72, 0.74, 0.77),
    "steel": (0.55, 0.57, 0.60),
    "hardox": (0.95, 0.72, 0.08),
    "orange": (0.90, 0.40, 0.06),
    "black": (0.08, 0.08, 0.09),
    "blue": (0.10, 0.25, 0.55),
    "grey": (0.55, 0.57, 0.60),
    "rubber": (0.13, 0.13, 0.13),
    "pe": (0.94, 0.94, 0.88),
    "igus": (0.95, 0.55, 0.10),
    "red": (0.80, 0.12, 0.10),
    "led": (0.98, 0.92, 0.55),
    "ground": (0.45, 0.62, 0.31),
    "soil": (0.42, 0.29, 0.16),
    "leaf": (0.18, 0.45, 0.12),
    "root": (0.45, 0.30, 0.20),
}
TRANSPARENT = {}
ROBOT_TRANSPARENCY = 0
SIDES = ((-1, "left"), (1, "right"))

# materiaal per kleur (kg/mm3); gekochte delen met een catalogusmassa staan in MASS_FIXED
DENSITY = {"alu": 2.70e-6, "rubber": 1.2e-6, "pe": 0.95e-6, "igus": 1.4e-6, "led": 1.5e-6}
STEEL = 7.85e-6
MASS_FIXED = {"spindle_motor": P.motor_kg, "ebox": 3.0 + 0.6,   # E-kast + omvormer
              "camera": 0.4, "led_bar": 0.6, "bearing_lower": P.ucp_kg, "bearing_upper": P.ucp_kg,
              "jaw_coupling": P.jaw_kg, "act_body": P.act_kg[0], "act_rod": P.act_kg[1],
              "z_houses": 4 * 1.2,          # 4 lagerhuizen (gietijzer/alu, geschat 1,2 kg elk)
              "spiral_cable": 0.4, "pot_sensor": 0.05}


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
        add_shape(doc, hs, "upright_" + tag, "upright_40x40x3_" + tag, G.upright(side), "frame")
        add_shape(doc, hs, "upright_cap_" + tag, "upright_cap_6mm_" + tag, G.upright_cap(side), "frame")
        add_shape(doc, hs, "gusset_" + tag, "gusset_6mm_" + tag, G.gusset(side), "frame")
    add_shape(doc, hs, "hs_cross", "cross_tube_40x40x3", G.cross_tube(), "frame")
    return hs


def build_z_frame(doc, root):
    """Vast Z-frame: dwarsbalken, montageplaat, 4 lagerhuizen met glijbus, vast deel van de actuator."""
    zf = new_part(doc, root, "Z_frame", "z_frame_fixed")
    for zp, lvl in zip(P.beam_z, ("lower", "upper")):
        add_shape(doc, zf, "z_beam_" + lvl, "cross_beam_40x40x3_" + lvl, G.z_beam(zp), "frame")
    add_shape(doc, zf, "z_beam_bolts", "cross_beam_bolts_M12", G.z_beam_bolts(), "galv")
    add_shape(doc, zf, "mount_plate", "z_mount_plate_steel_10mm", G.mount_plate(), "frame")
    add_shape(doc, zf, "mount_plate_bolts", "z_mount_plate_bolts_M10", G.mount_plate_bolts(), "galv")
    add_shape(doc, zf, "z_houses", "z_guide_bearing_housings_D50_x4", G.z_houses(), "grey")
    add_shape(doc, zf, "z_bushes", "z_guide_plain_bushes_iglidur_50x60x70_x4", G.z_bushes(), "igus")
    add_shape(doc, zf, "z_house_bolts", "z_guide_housing_bolts_M8", G.z_house_bolts(), "galv")
    add_shape(doc, zf, "z_wipers", "z_guide_wipers_rubber", G.z_wipers(), "rubber")
    add_shape(doc, zf, "z_grease_nipples", "z_guide_grease_nipples", G.z_grease_nipples(), "chrome")
    add_shape(doc, zf, "act_top_bracket", "actuator_top_bracket_8mm", G.act_top_bracket(), "frame")
    add_shape(doc, zf, "act_pin_top", "actuator_pin_D12_top", G.act_pin_top(), "chrome")
    add_shape(doc, zf, "act_body", "linak_LA36_24V_1700N_stroke400_housing_and_tube", G.act_body(), "grey")
    add_shape(doc, zf, "cable_bracket_fixed", "spiral_cable_bracket_mount_plate", G.cable_bracket_fixed(), "galv")
    return zf


def build_electrics(doc, root):
    el = new_part(doc, root, "Electrics", "electrics_fixed")
    add_shape(doc, el, "ebox_plate", "ebox_mounting_plate_3mm", G.ebox_plate(), "galv")
    add_shape(doc, el, "ebox", "ebox_IP65_300x250x120", G.ebox(), "grey")
    add_shape(doc, el, "ebox_glands", "cable_glands_M20", G.ebox_glands(), "black")
    return el


def build_camera(doc, root):
    """Vaste camera hoog boven de spillijn (zoals Robot Ruud), op de rechter staander."""
    cam = new_part(doc, root, "Camera", "camera_fixed_high")
    add_shape(doc, cam, "camera_mast", "camera_mast_alu_40x40x3", G.camera_mast(), "alu")
    add_shape(doc, cam, "camera_arm", "camera_arm_alu_40x40x3", G.camera_arm(), "alu")
    add_shape(doc, cam, "camera_crossbar", "camera_crossbar_alu_40x40x3", G.camera_crossbar(), "alu")
    add_shape(doc, cam, "camera", "camera_industrial_usb3", G.camera(), "black")
    add_shape(doc, cam, "led_bar", "led_light_bar_48V", G.led_bar(), "led")
    return cam


def build_z_carriage(doc, root, z):
    zc = new_part(doc, root, "Z_carriage", "z_two_round_tubes_slide_in_z", translation(z=z - P.z_ref))
    for side, tag in SIDES:
        add_shape(doc, zc, "z_guide_tube_" + tag, "z_guide_precision_tube_D50x4_" + tag, G.z_guide_tube(side), "chrome")
    add_shape(doc, zc, "z_tube_cap", "z_guide_tube_cap_left", G.z_tube_caps(), "frame")
    add_shape(doc, zc, "z_yoke", "z_lower_yoke_10mm", G.z_yoke(), "orange")
    add_shape(doc, zc, "z_clamp_plate", "z_tube_clamp_plate_10mm", G.z_clamp_plate(), "orange")
    add_shape(doc, zc, "act_eye_bracket", "actuator_rod_eye_bracket_8mm", G.act_eye_bracket(), "orange")
    add_shape(doc, zc, "act_rod", "linak_LA36_inner_tube_with_rod_eye_D27_8", G.act_rod(), "chrome")
    add_shape(doc, zc, "act_pin_eye", "actuator_pin_D12_rod_eye", G.act_pin_eye(), "chrome")
    add_shape(doc, zc, "cable_bracket_z", "spiral_cable_bracket_right_z_tube_top", G.cable_bracket_z(), "galv")
    add_shape(doc, zc, "sb_back", "spindle_bracket_back_plate_6mm", G.sb_back_plate(), "orange")
    add_shape(doc, zc, "sb_lower", "spindle_bracket_lower_plate_8mm", G.sb_plate_lower(), "orange")
    add_shape(doc, zc, "sb_top", "spindle_bracket_top_plate_8mm", G.sb_top_plate(), "orange")
    for side, tag in SIDES:
        add_shape(doc, zc, "sb_side_" + tag, "spindle_bracket_side_plate_5mm_" + tag, G.sb_side_plate(side), "orange")
    add_shape(doc, zc, "sb_bearing_plate", "spindle_bracket_bearing_plate_10mm", G.sb_bearing_plate(), "orange")
    add_shape(doc, zc, "bearing_lower", "pillow_block_UCP206_lower", G.bearing_lower(), "blue")
    add_shape(doc, zc, "bearing_upper", "pillow_block_UCP206_upper", G.bearing_upper(), "blue")
    add_shape(doc, zc, "bearing_bolts", "bearing_bolts_M14", G.bearing_bolts(), "galv")
    add_shape(doc, zc, "spindle_shaft", "spindle_shaft_D30_C45", G.spindle_shaft(), "chrome")
    add_shape(doc, zc, "spindle_flange", "spindle_flange_D110x12_welded", G.spindle_flange(), "chrome")
    add_shape(doc, zc, "jaw_coupling", "jaw_coupling_flexible_size28_bore30_19", G.jaw_coupling(), "red")
    add_shape(doc, zc, "motor_plate", "spindle_motor_plate_10mm", G.motor_plate(), "orange")
    add_shape(doc, zc, "motor_gussets", "spindle_motor_plate_gussets_6mm", G.motor_gussets(), "orange")
    add_shape(doc, zc, "spindle_motor", "gearmotor_800W_48V_500rpm_foot", G.spindle_motor(), "black")
    add_shape(doc, zc, "spindle_motor_shaft", "gearmotor_shaft_D19", G.spindle_motor_shaft(), "chrome")
    add_shape(doc, zc, "pot_bushes", "pot_rod_bushes_PE_D40", G.pot_bushes(), "pe")
    add_shape(doc, zc, "pot_sensor", "pot_sensor_ground_contact_M12", G.pot_sensor(), "red")
    add_shape(doc, zc, "pot_sensor_bracket", "pot_sensor_bracket_3mm", G.pot_sensor_bracket(), "galv")
    return zc


def build_tool(doc, zc, angle=0.0):
    tl = new_part(doc, zc, "Tool", "tool_cutter_rotates_about_spindle", spin_placement(angle))
    for name, shape, color in G.cutter_parts():
        add_shape(doc, tl, name, name, shape, color)
    return tl


def build_pot(doc, root, z, ground=0.0):
    pot = new_part(doc, root, "Pot", "pot_rests_on_ground", pot_placement(z, ground))
    add_shape(doc, pot, "pot_shell", "can_steel_pipe_219x3_6", G.pot_shell(), "galv")
    add_shape(doc, pot, "pot_lid", "can_lid_steel_5mm", G.pot_lid(), "galv")
    add_shape(doc, pot, "shaft_seal", "shaft_seal_rubber", G.shaft_seal(), "rubber")
    add_shape(doc, pot, "pot_rods", "pot_rods_D16", G.pot_rods(), "chrome")
    add_shape(doc, pot, "pot_set_rings", "pot_set_rings_D28", G.pot_set_rings(), "chrome")
    return pot


def build_cables(doc, root, z):
    cab = new_part(doc, root, "Cables", "cables_follow_z")
    add_shape(doc, cab, "spiral_cable", "spiral_cable_to_z_carriage", G.spiral_cable(z), "black")
    return cab


def build_into(doc, parent=None, z=None, ground=0.0, placement=None):
    """Zet het hele werktuig in een bestaand document. z = onderkant gereedschap (grond = 0)."""
    z = P.work_z if z is None else z
    root = new_part(doc, parent, "Dockweed_drill", "dockweed_drill_" + P.VARIANT, placement)
    build_headstock(doc, root)
    build_z_frame(doc, root)
    build_electrics(doc, root)
    build_camera(doc, root)
    zc = build_z_carriage(doc, root, z)
    build_tool(doc, zc)
    build_pot(doc, root, z, ground)
    build_cables(doc, root, z)
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


def build(z=None, save_path=SAVE_PATH, show_robot=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Dockweed drill " + P.VARIANT
    doc.Comment = ("Gegenereerd met build_dwd7.py uit dwd7_params.py. Robotcoordinaten: x = rechts, y = rijrichting "
                   "(voor = +y), z = omhoog, grond = z 0. Het werktuig hangt achter de robot, spil vast op x 0. "
                   "Stand: build(z=...), z = onderkant gereedschap.")
    build_into(doc, None, z)
    build_robot_reference(doc, show_robot)
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    return doc


def set_pose(doc, z, ground=0.0, angle=None):
    """Stand van Z-slede, pot en kabel in een bestaand document."""
    doc.getObject("Z_carriage").Placement = translation(z=z - P.z_ref)
    doc.getObject("Pot").Placement = pot_placement(z, ground)
    if angle is not None:
        doc.getObject("Tool").Placement = spin_placement(angle)
    doc.getObject("spiral_cable").Shape = G.spiral_cable(z)


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


POSES = (P.drive_z, 0.0, -P.depth_std, -P.depth_max)


def current_pose(doc):
    return doc.getObject("Z_carriage").Placement.Base.z + P.z_ref


def check_poses(doc=None, poses=POSES):
    """Eindstanden van Z: interferentie van het hele werktuig (met robot). Zet daarna de stand terug."""
    doc = doc or App.getDocument(DOC_NAME)
    z0 = current_pose(doc)
    out = {}
    try:
        for z in poses:
            set_pose(doc, z)
            doc.recompute()
            out[z] = check_interference(doc)
    finally:
        set_pose(doc, z0)
        doc.recompute()
    return out


CLEARANCE_GROUPS = ("Pot", "Tool", "Z_carriage", "Z_frame", "Electrics")     # aanbouwbok zit vast
CLEARANCE_ROBOT = ("RL_tire", "RR_tire", "RL_side_l", "RL_side_r", "RR_side_l", "RR_side_r", "RL_top_plate",
                   "RR_top_plate", "RL_spacer", "RR_spacer", "upper_beam_left_inner", "upper_beam_right_inner",
                   "upper_beam_left_outer", "upper_beam_right_outer", "lower_beam_rear_outer")


def clearance(doc=None, poses=None):
    """Kleinste afstand (mm) per groep tot de achterwielen, wielbeugels en balken van de robot, over de standen."""
    doc = doc or App.getDocument(DOC_NAME)
    poses = poses or (P.drive_z, -P.depth_max)
    z0 = current_pose(doc)
    robot = [global_shape(doc.getObject(n)) for n in CLEARANCE_ROBOT if doc.getObject(n)]
    robot_c = Part.makeCompound(robot)
    out = {}
    try:
        for z in poses:
            set_pose(doc, z)
            doc.recompute()
            for grp in CLEARANCE_GROUPS:
                objs = [o for o in doc.getObject(grp).OutListRecursive if o.TypeId == "Part::Feature"]
                if grp == "Z_carriage":
                    sub = {o.Name for o in doc.getObject("Tool").OutListRecursive}
                    objs = [o for o in objs if o.Name not in sub]
                d = Part.makeCompound([global_shape(o) for o in objs]).distToShape(robot_c)[0]
                out[grp] = min(out.get(grp, 1e9), round(d, 1))
    finally:
        set_pose(doc, z0)
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
    """Massa (kg) en zwaartepunt (robotcoordinaten): heel werktuig, per groep en de Z-slede."""
    doc = doc or App.getDocument(DOC_NAME)
    feats = implement_objects(doc)
    m_all, c_all = _sum(feats)
    groups = {}
    for name in ("Headstock", "Z_frame", "Electrics", "Camera", "Cables", "Pot", "Tool"):
        groups[name] = round(_sum(_features(doc, name))[0], 1)
    zc_all = _features(doc, "Z_carriage")
    m_z, c_z = _sum(zc_all)
    groups["Z_carriage"] = round(m_z - groups["Tool"], 1)
    return {"implement_kg": round(m_all, 1), "implement_cg": tuple(round(v) for v in (c_all.x, c_all.y, c_all.z)),
            "z_moving_kg": round(m_z, 1), "z_moving_cg": tuple(round(v) for v in (c_z.x, c_z.y, c_z.z)),
            "pot_kg": groups["Pot"], "tool_kg": groups["Tool"], "groups": groups}


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
    cutter = {n: s for n, s, c in G.cutter_parts()}
    return [
        ("headstock_top_plate_8mm", G.hs_top_plate(-1), "z"),
        ("headstock_clamp_plate_8mm", G.hs_clamp_plate(-1), "z"),
        ("headstock_back_plate_8mm", G.hs_back_plate(-1), "y"),
        ("gusset_6mm", G.gusset(-1), "x"),
        ("z_mount_plate_steel_10mm", G.mount_plate(), "y"),
        ("spindle_bracket_back_plate_6mm", G.sb_back_plate(), "y"),
        ("z_lower_yoke_10mm", G.z_yoke(), "z"),
        ("z_tube_clamp_plate_10mm", G.z_clamp_plate(), "z"),
        ("spindle_bracket_lower_plate_8mm", G.sb_plate_lower(), "z"),
        ("spindle_bracket_bearing_plate_10mm", G.sb_bearing_plate(), "y"),
        ("spindle_bracket_top_plate_8mm", G.sb_top_plate(), "z"),
        ("spindle_motor_plate_10mm", G.motor_plate(), "x"),
        ("spindle_motor_plate_gusset_6mm", G.motor_gussets().Solids[0], "y"),
        ("spindle_bracket_side_plate_5mm", G.sb_side_plate(-1), "x"),
        ("can_lid_steel_5mm", G.pot_lid(), "z"),
        ("cutter_cross_lower_hardox_10mm", cutter["cutter_cross_lower"], "z"),
        ("cutter_cross_upper_hardox_10mm", cutter["cutter_cross_upper"], "z"),
        ("cutter_tooth_hardox_10mm", first(cutter["cutter_teeth"]), "y"),
        ("cutter_flange_10mm", cutter["cutter_flange"], "z"),
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
    tmp = App.newDocument("dxf_tmp_dwd7")
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
    view = Gui.getDocument(DOC_NAME).ActiveView
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
    import FreeCADGui as Gui
    out = []
    ys = G.spindle_y()
    # rijstand met robot
    doc = build(z=P.drive_z, save_path=None, show_robot=True)
    add_environment(doc, plant=(0.0, ys - 700.0))
    out.append(save_view("2_driving_iso_rear_left.png", (1.0, 1.0, -0.65), target=(0, -550, 950), height=2700))
    # werkstand
    doc = build(save_path=None, show_robot=True)
    add_environment(doc, crushed=(0.0, ys, P.depth_std))
    out.append(save_view("1_work_iso_rear_right.png", (-1.0, 1.0, -0.65), target=(0, -650, 950), height=2700))
    out.append(save_view("3_side_left.png", (1.0, 0.0, 0.0), target=(0, -550, 1000), height=2400))
    out.append(save_view("5_rear.png", (0.0, 1.0, 0.0), target=(0, 0, 1000), height=2400))
    remove_environment(doc)
    out.append(save_view("4_top.png", (0.0, 0.0, -1.0), target=(0, -650, 0), height=1900, up=(0.0, 1.0, 0.0)))
    out.append(save_view("7_z_frame_detail.png", (-1.0, 1.3, -0.5), target=(0, -760, 960), height=1150,
                         size=(1000, 1100)))
    out.append(save_view("8_headstock_detail.png", (-1.0, 0.3, -0.35), target=(250, -620, 760), height=640))
    out.append(save_view("11_spindle_drive_detail.png", (-1.0, 1.0, -0.55), target=(0, ys, 520),
                         height=750, size=(1000, 1000)))
    # detail frees in de grond: alleen spil, pot, gereedschap en een stuk grond
    set_robot_reference(False, doc)
    add_environment(doc, crushed=(0.0, ys, P.depth_std), extent=((-330, 330), (ys - 330, ys + 330)))
    hide = [o for n in ("Headstock", "Z_frame", "Electrics", "Camera", "Cables") for o in _features(doc, n)]
    for o in hide:
        o.ViewObject.Visibility = False
    set_group_transparency(doc, "Pot", 70)
    out.append(save_view("6_cutter_in_soil_detail.png", (1.0, 0.45, -0.3), target=(0, ys, 60), height=1000,
                         size=(1100, 1300)))
    remove_environment(doc)
    doc = build(show_robot=False)          # werkstand opslaan
    if export:
        export_step(doc)
        export_dxf()
    return out
