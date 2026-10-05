"""Bouwt het FreeCAD-model van de doorzaaimachine (Overseeder.FCStd).

Gebruik in FreeCAD (map in sys.path, of via run_in_freecad.py):
    import build_ovs
    build_ovs.build()                          # werkstand, slaat het FCStd op
    build_ovs.build(psi=build_ovs.K.lift_angle(), phi=-build_ovs.P.u_stop_deg, save_path=None, show_robot=True)
    build_ovs.check_interference()             # overlappende onderdelen (moet leeg zijn)
    build_ovs.mass_properties()                # massa en zwaartepunten
    build_ovs.render_all()                     # afbeeldingen in previews/ en opslaan in werkstand
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ovs_params as P
import ovs_kin as K
import ovs_parts as G

DOC_NAME = "Overseeder"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Overseeder.FCStd")
PREVIEW_DIR = os.path.join(FOLDER, "previews")

COLOR = {
    "frame": (0.22, 0.24, 0.26),
    "unit": (0.13, 0.42, 0.30),
    "disc": (0.72, 0.74, 0.77),
    "band": (0.10, 0.10, 0.11),
    "boot": (0.30, 0.30, 0.32),
    "steel": (0.85, 0.86, 0.88),
    "zinc": (0.82, 0.84, 0.87),
    "hub": (0.12, 0.35, 0.65),
    "spring": (0.90, 0.62, 0.10),
    "rubber": (0.08, 0.08, 0.08),
    "rim": (0.85, 0.70, 0.15),
    "hopper": (0.78, 0.80, 0.82),
    "lid": (0.13, 0.42, 0.30),
    "meter": (0.62, 0.64, 0.67),
    "motor": (0.15, 0.15, 0.16),
    "seed_hose": (0.96, 0.96, 0.92),
    "box": (0.12, 0.35, 0.65),
    "actuator": (0.15, 0.15, 0.16),
    "chrome": (0.88, 0.89, 0.92),
    "robot_beam_lower": (0.47, 0.31, 0.22),
    "robot_beam_upper": (0.11, 0.11, 0.12),
    "robot_tire": (0.07, 0.07, 0.07),
    "robot_fork": (0.46, 0.47, 0.50),
}
TRANSPARENT = {"seed_hose": 30, "hopper": 0, "lid": 0}
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


def rot_placement(angle, center):
    """Rotatie om een as langs x door center (y, z); angle graden, + = achterkant omhoog."""
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -angle), V(0, center[0], center[1]))


# ---------------------------------------------------------------------
# Onderdelen in de boom
# ---------------------------------------------------------------------
def build_headstock(doc, parent):
    hs = new_part(doc, parent, "Headstock", "headstock_robot_mount")
    add_shape(doc, hs, "hs_top", "headstock_top_plate_150x10", G.hs_top_plate(), "frame")
    add_shape(doc, hs, "hs_clamp", "headstock_clamp_strip_50x10", G.hs_clamp_strip(), "frame")
    add_shape(doc, hs, "hs_cheeks", "headstock_cheeks_4x_100x10", G.hs_cheeks(), "frame")
    add_shape(doc, hs, "hs_act_lugs", "headstock_slot_plates_actuator", G.hs_act_lugs(), "frame")
    add_shape(doc, hs, "hs_bolts", "headstock_bolts_M10", G.hs_bolts(), "zinc")
    add_shape(doc, hs, "hs_pivot_bolts", "pivot_bolts_M16", G.hs_pivot_bolts(), "zinc")
    add_shape(doc, hs, "control_box", "control_box_motor_drivers_relay", G.control_box(), "box")
    return hs


def build_actuator(doc, parent, psi, length=None):
    f = K.frame_pin(psi)
    pin = K.slot_pin(psi, length)
    body, rod = G.actuator(f, pin)
    grp = new_part(doc, parent, "Lift", "lift_actuator")
    add_shape(doc, grp, "act_body", "linear_actuator_body_3000N_150", body, "actuator")
    add_shape(doc, grp, "act_rod", "linear_actuator_rod", rod, "chrome")
    add_shape(doc, grp, "act_pin_slot", "actuator_pin_in_slot_M10", G.act_pin_bolt(pin, P.act_lug_gap, True), "zinc")
    bodies, rods = G.gas_springs(pin)
    add_shape(doc, grp, "gas_bodies", "gas_springs_2x_400N_body", bodies, "actuator")
    add_shape(doc, grp, "gas_rods", "gas_springs_rods_and_top_pin", rods, "chrome")
    add_shape(doc, grp, "act_pin_frame", "actuator_pin_frame_M10", G.act_pin_bolt(f, P.act_lug_gap), "zinc")
    return grp


def build_frame(doc, parent):
    add_shape(doc, parent, "toolbar", "toolbar_60x60x4_with_coupling_flanges", G.bar(), "frame")
    add_shape(doc, parent, "arms", "frame_arms_40x40x3_with_bushes", G.arms(), "frame")
    add_shape(doc, parent, "cross_tube", "cross_tube_40x40x3", G.cross_tube(), "frame")
    add_shape(doc, parent, "frame_act_lugs", "actuator_lugs_on_toolbar", G.frame_act_lugs(), "frame")


def build_seeder(doc, parent):
    grp = new_part(doc, parent, "Seed_box", "seed_hopper_and_metering")
    add_shape(doc, grp, "hopper", "seed_hopper_2_compartments_40l_grass_19l_fine", G.hopper(), "hopper")
    add_shape(doc, grp, "hopper_lid", "hopper_lid", G.hopper_lid(), "lid")
    add_shape(doc, grp, "hopper_posts", "hopper_posts_6mm", G.hopper_posts(), "frame")
    add_shape(doc, grp, "meter_housing", "meter_housing_2_fluted_rolls_8_outlets", G.meter_housing(), "meter")
    add_shape(doc, grp, "meter_shafts", "meter_shaft_ends", G.meter_rolls(), "steel")
    main, fine = G.meter_motors()
    add_shape(doc, grp, "motor_main", "worm_gear_motor_12V_encoder_grass", main, "motor")
    add_shape(doc, grp, "motor_fine", "worm_gear_motor_12V_encoder_fine_seed", fine, "motor")
    return grp


_UNIT_CACHE = {}


def unit_shapes(phi):
    """Vormen van een element (gecached per armhoek; rolarm apart met chi)."""
    key = round(phi, 3)
    if key not in _UNIT_CACHE:
        rod, spring = G.u_strut(phi)
        tire, rim = G.u_press_wheel()
        _UNIT_CACHE[key] = {
            "holder": G.u_holder(),
            "ubolts": G.u_ubolts(),
            "pivot_bolt": G.u_pivot_bolt(),
            "strut": rod,
            "spring": spring,
            "hose": G.seed_hose(0.0, phi),
            "arm": G.u_arm(),
            "disc": G.u_disc(),
            "hub": G.u_hub(),
            "stub": G.u_stub(),
            "boot": G.u_seed_boot(),
            "band": G.u_band(),
            "pw_link": G.u_pw_link(),
            "pw_link_bolt": G.u_pw_link_bolt(),
            "tspring": G.u_tspring(),
            "pw_axle": G.u_pw_axle(),
            "pw_tire": tire,
            "pw_rim": rim,
        }
    return _UNIT_CACHE[key]


def build_unit(doc, parent, index, x, phi=0.0, chi=0.0):
    s = unit_shapes(phi)
    n = index + 1
    tag = "U%d" % n
    unit = new_part(doc, parent, "Row_unit_%d" % n, "row_unit_%d_x%+d" % (n, int(round(x))), translation(x=x))

    def add(grp, key, label, color):
        return add_shape(doc, grp, "%s_%s" % (tag, key), "%s_r%d" % (label, n), s[key], color)

    add(unit, "holder", "unit_holder_clamp_cheeks_spring_tower", "frame")
    add(unit, "ubolts", "unit_u_bolts_M12", "zinc")
    add(unit, "pivot_bolt", "unit_pivot_bolt_M16", "zinc")
    add(unit, "strut", "spring_rod_M12_with_eye_seat_stop_nut", "zinc")
    add(unit, "spring", "compression_spring_32x4.5", "spring")
    add(unit, "hose", "seed_hose_20x26", "seed_hose")
    arm = new_part(doc, unit, "Row_arm_%d" % n, "row_arm_%d_moves_with_ground" % n, rot_placement(phi, P.u_pivot))
    add(arm, "arm", "trailing_arm_30x30x3", "unit")
    add(arm, "stub", "disc_stub_axle_M20", "zinc")
    add(arm, "hub", "disc_bearing_hub", "hub")
    add(arm, "disc", "coulter_disc_300x3_7deg", "disc")
    add(arm, "band", "depth_band_PE_270", "band")
    add(arm, "boot", "seed_boot_and_tube_20x1.5", "boot")
    add(arm, "pw_link_bolt", "press_arm_pivot_bolt_M12", "zinc")
    add(arm, "tspring", "press_arm_torsion_spring", "spring")
    pw = new_part(doc, arm, "Press_arm_%d" % n, "press_arm_%d_sprung" % n, rot_placement(chi, K.pw_link_pivot()))
    add(pw, "pw_link", "press_arm_36x8", "unit")
    add(pw, "pw_axle", "press_wheel_axle_M16", "zinc")
    add(pw, "pw_tire", "press_wheel_solid_rubber_200x40", "rubber")
    add(pw, "pw_rim", "press_wheel_rim", "rim")
    return unit


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
def build_into(doc, parent=None, psi=0.0, phi=0.0, placement=None, rows=None, chi=0.0):
    """Zet het hele werktuig in een bestaand document. psi = hefhoek hefraam, phi = armhoek elementen (graden,
    + = omhoog; een getal voor alle rijen of een lijst per rij). rows = indices van de rijen die erop zitten."""
    root = new_part(doc, parent, "Overseeder_root", "overseeder_1m_8_rows", placement)
    build_headstock(doc, root)
    build_actuator(doc, root, psi)
    frame = new_part(doc, root, "Swing_frame", "swing_frame_moves_with_lift", rot_placement(psi, P.pivot))
    build_frame(doc, frame)
    build_seeder(doc, frame)
    phis = phi if isinstance(phi, (list, tuple)) else [phi] * len(P.row_x)
    for i, x in enumerate(P.row_x):
        if rows is None or i in rows:
            build_unit(doc, frame, i, x, phis[i], chi)
    return root


def build(psi=0.0, phi=0.0, save_path=SAVE_PATH, show_robot=False, chi=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Overseeder"
    doc.Comment = ("Gegenereerd met build_ovs.py uit ovs_params.py. x = rechts, y = rijrichting (voor = +y), "
                   "z = omhoog, grond = z 0. y = 0 is het hart van de achterste onderbalk van de robot "
                   "(wereld-y = y - 575). Heffen: build(psi=ovs_kin.lift_angle(), phi=-ovs_params.u_stop_deg).")
    build_into(doc, None, psi, phi, chi=chi)
    build_robot_reference(doc, show_robot)
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    return doc


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
    """Volume-overlap tussen alle onderdelen (mm3). Robotreferentie alleen tegen het werktuig."""
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


# massa per object: vaste waarde (kg) voor gekochte delen die als blok getekend zijn, anders volume x dichtheid
MASS_FIXED = {"act_body": 3.6, "act_rod": 0.6, "gas_bodies": 0.5, "gas_rods": 0.3, "motor_main": 1.0, "motor_fine": 1.0, "meter_housing": 4.5,
              "control_box": 1.5, "hopper_lid": 2.0}
MASS_SUFFIX = (("_hub", 1.0), ("_pw_tire", 0.9), ("_pw_rim", 0.35), ("_band", 0.36))
DENSITY = (("_hose", 1.3e-6 * 0.45), ("_spring", 7.85e-6), ("hopper_posts", 7.85e-6), ("hopper", 2.7e-6))
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
    """Massa (kg) en zwaartepunt (y, z): heel werktuig, hefraam (draait mee bij heffen), een sleeparm met alles
    wat meedraait en een heel element."""
    doc = doc or App.getDocument(DOC_NAME)
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in robot_names]
    m_all, c_all = _sum(feats)
    m_mov, c_mov = _sum(_feats(doc.getObject("Swing_frame")))
    m_arm, c_arm = _sum(_feats(doc.getObject("Row_arm_1")))
    m_u, c_u = _sum(_feats(doc.getObject("Row_unit_1")))
    m_box, c_box = _sum(_feats(doc.getObject("Seed_box")))
    return {"implement_kg": round(m_all, 1), "implement_cg": (round(c_all.y), round(c_all.z)),
            "moving_kg": round(m_mov, 1), "moving_cg": (round(c_mov.y), round(c_mov.z)),
            "arm_kg": round(m_arm, 2), "arm_cg": (round(c_arm.y), round(c_arm.z)),
            "unit_kg": round(m_u, 2), "unit_cg": (round(c_u.y), round(c_u.z)),
            "seed_box_kg": round(m_box, 1), "seed_box_cg": (round(c_box.y), round(c_box.z))}


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
    tgt = V(*target) if target is not None else V(0, -420, 400)
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


def add_ground(doc, y=(-1000.0, 300.0), x=(-700.0, 700.0)):
    shape = G.box_span(x, y, (-90.0, 0.0))
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = shape
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
    # detail element: zaadbak en deksel even verbergen
    hide = ["hopper", "hopper_lid"]
    set_visible(doc, hide, False)
    try:
        out.append(save_view("6_unit_detail.png", (-1.0, 0.75, -0.5), target=(150, -600, 200), height=620))
        out.append(save_view("7_boot_detail_from_below.png", (-0.6, 0.5, 0.65), target=(212, -590, 40), height=330))
    finally:
        set_visible(doc, hide, True)
    out.append(save_view("8_metering_detail.png", (-1.0, 0.9, -0.9), target=(250, -470, 520), height=650))
    add_ground(doc)
    try:
        out.append(save_view("3_side_right.png", (-1.0, 0.0, 0.0), target=(0, -420, 380), height=1100))
        out.append(save_view("9_unit_side.png", (-1.0, 0.0, 0.0), target=(0, -590, 200), height=560))
    finally:
        remove_ground(doc)
    return out


def render_all():
    """Alle afbeeldingen: geheven + robotreferentie, daarna werkstand (die wordt opgeslagen)."""
    out = []
    doc = build(psi=K.lift_angle(), phi=-P.u_stop_deg, save_path=None, show_robot=True, chi=P.pw_link_range[0])
    add_ground(doc)
    try:
        out.append(save_view("10_lifted_side_with_robot.png", (-1.0, 0.0, 0.0), target=(0, -330, 420), height=1200))
    finally:
        remove_ground(doc)
    out.append(save_view("11_lifted_iso_with_robot.png", (-1.0, 1.0, -0.6)))
    doc = build(psi=0.0, save_path=None, show_robot=True)
    out.append(save_view("12_work_iso_with_robot.png", (1.0, -1.0, -0.65)))
    set_robot_reference(False, doc)
    out += render_work_previews(doc)
    doc.saveAs(SAVE_PATH)
    return out
