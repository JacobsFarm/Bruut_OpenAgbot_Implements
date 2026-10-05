"""Bouwt het FreeCAD-model van de geavanceerde doorzaaimachine (Overseeder_Advanced.FCStd).

Gebruik in FreeCAD (map in sys.path, of via run_in_freecad.py):
    import build_ova
    build_ova.build()                                   # werkstand, slaat het FCStd op
    build_ova.build(h=140, drop=8, chi=15, save_path=None, show_robot=True)   # geheven
    build_ova.check_interference()                      # overlappende onderdelen (moet leeg zijn)
    build_ova.mass_properties()                         # massa en zwaartepunten
    build_ova.render_all()                              # afbeeldingen in previews/ en opslaan in werkstand
h = hefhoogte balk (mm), drop = armhoek elementen (graden, + = omlaag; getal of lijst per rij),
chi = gaffelhoek aandrukrollen (graden, + = omlaag).
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ova_params as P
import ova_kin as K
import ova_parts as G

DOC_NAME = "Overseeder_Advanced"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Overseeder_Advanced.FCStd")
PREVIEW_DIR = os.path.join(FOLDER, "previews")

COLOR = {
    "frame": (0.22, 0.24, 0.26),
    "arm": (0.93, 0.42, 0.08),
    "disc": (0.72, 0.74, 0.77),
    "band": (0.10, 0.10, 0.10),
    "boot": (0.30, 0.30, 0.32),
    "steel": (0.85, 0.86, 0.88),
    "spring": (0.90, 0.78, 0.25),
    "zinc": (0.82, 0.84, 0.87),
    "rubber": (0.08, 0.08, 0.08),
    "rim": (0.85, 0.70, 0.15),
    "hopper": (0.78, 0.80, 0.82),
    "lid": (0.93, 0.42, 0.08),
    "meter": (0.62, 0.64, 0.67),
    "motor": (0.15, 0.15, 0.16),
    "duct": (0.92, 0.92, 0.90),
    "fan": (0.12, 0.35, 0.65),
    "seed_hose": (0.96, 0.96, 0.92),
    "box": (0.12, 0.35, 0.65),
    "actuator": (0.15, 0.15, 0.16),
    "chrome": (0.88, 0.89, 0.92),
    "robot_beam_lower": (0.47, 0.31, 0.22),
    "robot_beam_upper": (0.11, 0.11, 0.12),
    "robot_tire": (0.07, 0.07, 0.07),
    "robot_fork": (0.46, 0.47, 0.50),
}
TRANSPARENT = {"seed_hose": 30}
ROBOT_TRANSPARENCY = 55


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
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
        if transparency is None:
            transparency = TRANSPARENT.get(color, 0)
        view.Transparency = transparency
    return obj


def translation(x=0.0, y=0.0, z=0.0):
    return App.Placement(V(x, y, z), App.Rotation())


def rotation_x(angle, center):
    """Rotatie om een as langs x door center (y, z); + = punten achter center gaan omlaag (als rot_yz)."""
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), angle), V(0, center[0], center[1]))


# ---------------------------------------------------------------------
# Onderdelen in de boom
# ---------------------------------------------------------------------
def build_headstock(doc, parent):
    hs = new_part(doc, parent, "Headstock", "headstock_robot_mount")
    for side, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, hs, "hs_top_" + tag, "headstock_top_plate_" + tag, G.hs_top_plate(side), "frame")
        add_shape(doc, hs, "hs_clamp_" + tag, "headstock_clamp_plate_" + tag, G.hs_clamp_plate(side), "frame")
        add_shape(doc, hs, "hs_back_" + tag, "headstock_back_plate_" + tag, G.hs_back_plate(side), "frame")
        add_shape(doc, hs, "hs_cheek_in_" + tag, "headstock_cheek_inner_" + tag, G.hs_cheek(side, True), "frame")
        add_shape(doc, hs, "hs_cheek_out_" + tag, "headstock_cheek_outer_" + tag, G.hs_cheek(side, False), "frame")
        add_shape(doc, hs, "hs_bolts_" + tag, "headstock_bolts_M10_" + tag, G.hs_bolts(side), "zinc")
        add_shape(doc, hs, "hs_pins_" + tag, "link_pins_front_" + tag, G.hs_pins(side), "zinc")
    add_shape(doc, hs, "hs_cross_top", "headstock_cross_tube_slot_plates_gas_springs", G.hs_cross_top(), "frame")
    add_shape(doc, hs, "hs_cross_low", "headstock_cross_tube_lower", G.hs_cross_low(), "frame")
    return hs


def build_seeder(doc, parent):
    grp = new_part(doc, parent, "Air_seeder", "air_seeder_on_robot")
    add_shape(doc, grp, "seed_frame", "seeder_frame_40x40x3_with_legs", G.seed_frame(), "frame")
    add_shape(doc, grp, "air_duct", "air_duct_60_with_8_venturi_outlets", G.air_duct(), "duct")
    add_shape(doc, grp, "meter_housing", "meter_housing_2_fluted_rolls", G.meter_housing(), "meter")
    main, fine = G.meter_motors()
    add_shape(doc, grp, "motor_main", "worm_gear_motor_12V_encoder_grass", main, "motor")
    add_shape(doc, grp, "motor_fine", "worm_gear_motor_12V_encoder_fine_seed", fine, "motor")
    add_shape(doc, grp, "hopper", "seed_hopper_2_compartments", G.hopper(), "hopper")
    add_shape(doc, grp, "hopper_lid", "hopper_lid", G.hopper_lid(), "lid")
    add_shape(doc, grp, "hopper_posts", "hopper_posts_6mm", G.hopper_posts(), "frame")
    body, pipe = G.fan()
    add_shape(doc, grp, "fan", "radial_fan_12V", body, "fan")
    add_shape(doc, grp, "fan_pipe", "fan_pipe_50_to_duct", pipe, "duct")
    add_shape(doc, grp, "control_box", "control_box_motor_and_fan_drivers", G.control_box(), "box")
    return grp


def build_links(doc, parent, theta):
    grp = new_part(doc, parent, "Linkage", "parallel_linkage")
    for side, tag in ((-1, "left"), (1, "right")):
        local = G.link_local(side)
        for z, level in ((P.pin_upper_z, "upper"), (P.pin_lower_z, "lower")):
            shape = G.moved(local, y=P.pin_front_y, z=z)
            shape.rotate(V(0, P.pin_front_y, z), V(1, 0, 0), -theta)
            add_shape(doc, grp, "link_%s_%s" % (level, tag), "link_%s_%s" % (level, tag), shape, "frame")
    return grp


def build_lift(doc, parent, h, length=None):
    a, b = K.actuator_points(h, length)
    body, rod = G.actuator(b, a)
    grp = new_part(doc, parent, "Lift", "lift_actuator_and_gas_springs")
    add_shape(doc, grp, "act_body", "linear_actuator_body_2500N_150", body, "actuator")
    add_shape(doc, grp, "act_rod", "linear_actuator_rod", rod, "chrome")
    add_shape(doc, grp, "act_pin_slot", "pin_in_slot_M16", G.slot_pin(a), "zinc")
    bodies, rods = G.gas_springs(a)
    add_shape(doc, grp, "gas_bodies", "gas_springs_2x_body", bodies, "actuator")
    add_shape(doc, grp, "gas_rods", "gas_springs_rods_and_top_pin", rods, "chrome")
    return grp


def build_toolbar(doc, parent):
    add_shape(doc, parent, "toolbar", "toolbar_60x60x4_with_coupling_flanges", G.toolbar(), "frame")
    for side, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, parent, "rf_in_" + tag, "rear_frame_plate_inner_" + tag, G.rf_plate(side, True), "frame")
        add_shape(doc, parent, "rf_out_" + tag, "rear_frame_plate_outer_" + tag, G.rf_plate(side, False), "frame")
        add_shape(doc, parent, "rf_pins_" + tag, "link_pins_rear_" + tag, G.rf_pins(side), "zinc")
    add_shape(doc, parent, "rf_cross", "rear_frame_cross_tube_actuator", G.rf_cross(), "frame")
    add_shape(doc, parent, "act_b_pin", "actuator_pin_B_M16", G.act_b_pin(), "zinc")


_UNIT_CACHE = {}


def unit_shapes():
    if not _UNIT_CACHE:
        tire, rim = G.u_press_wheel()
        _UNIT_CACHE.update({
            "clamp_front": G.u_clamp_plate(True), "clamp_rear": G.u_clamp_plate(False),
            "clamp_bolts": G.u_clamp_bolts(), "tongue": G.u_tongue(), "anchor": G.u_anchor_plate(),
            "pivot_pin": G.u_pivot_pin(), "fork_l": G.u_fork_plate(-1), "fork_r": G.u_fork_plate(1),
            "lug_pin": G.u_lug_pin(), "axle": G.u_axle(), "hub": G.u_hub(), "disc": G.u_disc(),
            "band_l": G.u_band(-1), "band_r": G.u_band(1), "boot": G.u_seed_boot(), "boot_hw": G.u_boot_hardware(),
            "pw_bolts": G.u_pw_pivot_bolts(), "pw_spring": G.u_pw_spring(), "pw_yoke": G.u_pw_yoke(),
            "pw_axle": G.u_pw_axle(), "pw_tire": tire, "pw_rim": rim,
        })
    return _UNIT_CACHE


_STRUT_CACHE = {}


def strut_shapes(drop):
    key = round(drop, 3)
    if key not in _STRUT_CACHE:
        _STRUT_CACHE[key] = G.u_strut(drop)
    return _STRUT_CACHE[key]


def build_unit(doc, parent, index, x, drop, chi):
    s = unit_shapes()
    n = index + 1
    tag = "U%d" % n
    unit = new_part(doc, parent, "Unit_%d" % n, "row_unit_%d_x%+d" % (n, int(round(x))), translation(x=x))

    def add(target, key, label, color):
        return add_shape(doc, target, "%s_%s" % (tag, key), "%s_r%d" % (label, n), s[key], color)

    add(unit, "clamp_front", "clamp_plate_front", "frame")
    add(unit, "clamp_rear", "clamp_plate_rear", "frame")
    add(unit, "clamp_bolts", "clamp_bolts_M12", "zinc")
    add(unit, "tongue", "unit_bracket", "frame")
    add(unit, "anchor", "spring_anchor_plate", "frame")
    add(unit, "pivot_pin", "pivot_pin", "zinc")
    rod, spring = strut_shapes(drop)
    add_shape(doc, unit, tag + "_strut_rod", "spring_rod_r%d" % n, rod, "zinc")
    add_shape(doc, unit, tag + "_spring", "downforce_spring_r%d" % n, spring, "spring")

    arm = new_part(doc, unit, "Unit_%d_arm" % n, "row_unit_%d_swing_arm" % n, rotation_x(drop, P.u_pivot))
    add(arm, "fork_l", "fork_plate_left", "arm")
    add(arm, "fork_r", "fork_plate_right", "arm")
    add(arm, "lug_pin", "spring_pin", "zinc")
    add(arm, "axle", "disc_axle", "zinc")
    add(arm, "hub", "disc_hub", "steel")
    add(arm, "disc", "coulter_disc_300x3", "disc")
    add(arm, "band_l", "depth_band_left_270", "band")
    add(arm, "band_r", "depth_band_right_270", "band")
    add(arm, "boot", "seed_coulter_with_tube", "boot")
    add(arm, "boot_hw", "seed_coulter_bolts_and_spacers", "zinc")
    add(arm, "pw_bolts", "press_yoke_shoulder_bolts_M12", "zinc")
    add(arm, "pw_spring", "press_yoke_torsion_spring", "spring")
    yoke = new_part(doc, arm, "Unit_%d_press" % n, "row_unit_%d_press_wheel" % n, rotation_x(chi, K.pw_pivot()))
    add(yoke, "pw_yoke", "press_wheel_yoke", "arm")
    add(yoke, "pw_axle", "press_wheel_axle_M16", "zinc")
    add(yoke, "pw_tire", "press_wheel_solid_rubber_200x40", "rubber")
    add(yoke, "pw_rim", "press_wheel_rim", "rim")
    return unit


def build_hoses(doc, parent, drops, h):
    grp = new_part(doc, parent, "Seed_hoses", "seed_hoses_air")
    for i, x in enumerate(P.row_x):
        add_shape(doc, grp, "hose_%d" % (i + 1), "seed_hose_20x26_r%d" % (i + 1),
                  G.seed_hose(x, P.outlet_x[i], drops[i], h), "seed_hose")
    return grp


def build_robot_reference(doc, visible):
    grp = new_part(doc, None, "Robot_reference", "robot_reference_NOT_PART_OF_DESIGN")
    t = ROBOT_TRANSPARENCY
    add_shape(doc, grp, "ref_beam_rear_outer", "ref_chassis_beam_1_rear_outer", G.robot_beam_x(0.0),
              "robot_beam_lower", visible, t)
    add_shape(doc, grp, "ref_beam_rear_inner", "ref_chassis_beam_1_rear_inner", G.robot_beam_x(P.robot_inner_beam_y),
              "robot_beam_lower", visible, t)
    add_shape(doc, grp, "ref_upper_beams", "ref_chassis_beam_2_rear_part", G.robot_upper_beams(),
              "robot_beam_upper", visible, t)
    for side, tag in ((-1, "left"), (1, "right")):
        tire, bracket = G.robot_wheel_unit(side)
        add_shape(doc, grp, "ref_tire_" + tag, "ref_rear_tire_" + tag, tire, "robot_tire", visible, t)
        add_shape(doc, grp, "ref_bracket_" + tag, "ref_rear_wheel_bracket_" + tag, bracket, "robot_fork", visible, t)
    return grp


# ---------------------------------------------------------------------
# Opbouw
# ---------------------------------------------------------------------
def build_into(doc, parent=None, h=0.0, drop=0.0, chi=0.0, placement=None, length=None):
    theta, dy, dz = K.lift_state(h)
    drops = drop if isinstance(drop, (list, tuple)) else [drop] * len(P.row_x)
    chis = chi if isinstance(chi, (list, tuple)) else [chi] * len(P.row_x)
    root = new_part(doc, parent, "Overseeder_root", "overseeder_advanced_1m_8_rows", placement)
    build_headstock(doc, root)
    build_seeder(doc, root)
    build_links(doc, root, theta)
    build_lift(doc, root, h, length)
    bar = new_part(doc, root, "Toolbar_assembly", "toolbar_assembly_moves_with_lift", translation(0.0, dy, dz))
    build_toolbar(doc, bar)
    for i, x in enumerate(P.row_x):
        build_unit(doc, bar, i, x, drops[i], chis[i])
    build_hoses(doc, root, drops, h)
    return root


def build(h=0.0, drop=0.0, chi=0.0, save_path=SAVE_PATH, show_robot=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Overseeder advanced"
    doc.Comment = ("Gegenereerd met build_ova.py uit ova_params.py. x = rechts, y = rijrichting (voor = +y), "
                   "z = omhoog, grond = z 0. y = 0 is het hart van de achterste onderbalk van de robot "
                   "(wereld-y = y - 575). Heffen: build(h=140, drop=8, chi=15).")
    build_into(doc, None, h, drop, chi)
    build_robot_reference(doc, show_robot)
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    return doc


def build_lifted(save_path=None, show_robot=True):
    return build(h=P.lift_height, drop=P.unit_drop_deg, chi=P.pw_range[1], save_path=save_path, show_robot=show_robot)


def set_robot_reference(visible, doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    for obj in doc.getObject("Robot_reference").Group:
        obj.ViewObject.Visibility = visible


# ---------------------------------------------------------------------
# Controle
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def check_interference(doc=None, include_robot=True, tol=1.0):
    doc = doc or App.getDocument(DOC_NAME)
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
    items = [(o, global_shape(o)) for o in doc.Objects if o.TypeId == "Part::Feature"
             and (include_robot or o.Name not in robot_names)]
    hits = []
    for i in range(len(items)):
        oa, sa = items[i]
        ba = sa.BoundBox
        for j in range(i + 1, len(items)):
            ob, sb = items[j]
            if oa.Name in robot_names and ob.Name in robot_names:
                continue
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


MASS_FIXED = {"act_body": 4.0, "act_rod": 0.5, "gas_bodies": 0.5, "gas_rods": 0.4, "motor_main": 1.0,
              "motor_fine": 1.0, "meter_housing": 4.0, "fan": 3.5, "control_box": 1.5, "hopper_lid": 2.0}
MASS_SUFFIX = (("_pw_tire", 0.9), ("_pw_rim", 0.35))
DENSITY = (("hopper_posts", 7.85e-6), ("_boot_hw", 7.85e-6), ("_boot", 7.85e-6 * 0.45),   # kouter gelast uit 2 platen 3 mm met zaadkanaal ertussen
           ("hose_", 1.3e-6 * 0.45), ("fan_pipe", 1.3e-6 * 0.45), ("_spring", 7.85e-6), ("air_duct", 1.4e-6),
           ("_band_", 0.95e-6), ("hopper", 2.7e-6))
STEEL = 7.85e-6


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
    for key, m in MASS_SUFFIX:
        if obj.Name.endswith(key):
            return m, cg
    density = STEEL
    for key, dens in DENSITY:
        if key in obj.Name:
            density = dens
            break
    return vol * density, cg


def _sum(objs):
    m = 0.0
    c = V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def _feats(obj):
    return [o for o in obj.OutListRecursive if o.TypeId == "Part::Feature"]


def mass_properties(doc=None):
    """Massa (kg) en zwaartepunt (y, z): heel werktuig, balk (beweegt mee bij heffen, inclusief de helft van de
    slangen), luchtzaaier op de robot, een sleeparm met alles wat meedraait en een heel element."""
    doc = doc or App.getDocument(DOC_NAME)
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in robot_names]
    m_all, c_all = _sum(feats)
    m_bar, c_bar = _sum(_feats(doc.getObject("Toolbar_assembly")))
    m_seed, c_seed = _sum(_feats(doc.getObject("Air_seeder")))
    m_arm, c_arm = _sum(_feats(doc.getObject("Unit_1_arm")))
    m_u, c_u = _sum(_feats(doc.getObject("Unit_1")))
    m_hose, c_hose = _sum(_feats(doc.getObject("Seed_hoses")))
    return {"implement_kg": round(m_all, 1), "implement_cg": (round(c_all.y), round(c_all.z)),
            "moving_kg": round(m_bar, 1), "moving_cg": (round(c_bar.y), round(c_bar.z)),
            "seeder_kg": round(m_seed, 1), "seeder_cg": (round(c_seed.y), round(c_seed.z)),
            "hoses_kg": round(m_hose, 2),
            "arm_kg": round(m_arm, 2), "arm_cg": (round(c_arm.y), round(c_arm.z)),
            "unit_kg": round(m_u, 2), "unit_cg": (round(c_u.y), round(c_u.z))}


def mass_table(doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
    rows = [(o.Label, round(_mass_cg(o)[0], 2)) for o in doc.Objects
            if o.TypeId == "Part::Feature" and o.Name not in robot_names]
    return sorted(rows, key=lambda r: -r[1])


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
    tgt = V(*target) if target is not None else V(0, -400, 600)
    eye = tgt - d * 6000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(20000.0)
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


GROUND = "render_ground"


def add_ground(doc, y=(-1150.0, 400.0), x=(-700.0, 700.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-90.0, 0.0))
    obj.ViewObject.ShapeColor = (0.55, 0.40, 0.25)
    obj.ViewObject.Transparency = 55
    return obj


def remove_ground(doc):
    if doc.getObject(GROUND):
        doc.removeObject(GROUND)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def render_work_previews(doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    out = []
    out.append(save_view("1_iso_rear_right.png", (-1.0, 1.0, -0.75)))
    out.append(save_view("2_iso_front_left.png", (1.0, -1.1, -0.7)))
    out.append(save_view("4_top.png", (0.0, 0.0, -1.0), up=(0.0, 1.0, 0.0)))
    out.append(save_view("5_rear.png", (0.0, 1.0, 0.0)))
    hoses = ["hose_%d" % (i + 1) for i in range(len(P.row_x))]
    set_visible(doc, hoses, False)
    try:
        out.append(save_view("6_unit_detail.png", (-1.0, 0.75, -0.5), target=(150, -800, 200), height=640))
        out.append(save_view("7_coulter_detail_from_below.png", (-0.6, 0.5, 0.65), target=(250, -760, 60),
                             height=360))
    finally:
        set_visible(doc, hoses, True)
    out.append(save_view("8_air_seeder_detail.png", (-1.0, -0.9, -0.8), target=(0, 80, 1050), height=900))
    add_ground(doc)
    try:
        out.append(save_view("3_side_right.png", (-1.0, 0.0, 0.0), target=(0, -360, 720), height=1650))
        out.append(save_view("9_unit_side.png", (-1.0, 0.0, 0.0), target=(0, -790, 230), height=620))
    finally:
        remove_ground(doc)
    return out


def render_all():
    out = []
    doc = build_lifted()
    add_ground(doc)
    try:
        out.append(save_view("10_lifted_side_with_robot.png", (-1.0, 0.0, 0.0), target=(0, -330, 730), height=1700))
    finally:
        remove_ground(doc)
    out.append(save_view("11_lifted_iso_with_robot.png", (-1.0, 1.0, -0.6)))
    doc = build(save_path=None, show_robot=True)
    out.append(save_view("12_work_iso_with_robot.png", (1.0, -1.0, -0.65)))
    set_robot_reference(False, doc)
    out += render_work_previews(doc)
    doc.saveAs(SAVE_PATH)
    return out
