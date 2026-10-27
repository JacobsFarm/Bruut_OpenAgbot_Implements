"""Bouwt het FreeCAD-model van de eenvoudige toediener (Liquid_Fertilizer_Applicator_Simple_v2.FCStd).

Gebruik in FreeCAD (map in sys.path, of via run_in_freecad.py):
    import build_lfs2
    build_lfs2.build()                         # werkstand, slaat het FCStd op
    build_lfs2.build(psi=build_lfs2.K.lift_angle(), save_path=None, show_robot=True)   # geheven
    build_lfs2.check_interference()            # overlappende onderdelen (moet leeg zijn)
    build_lfs2.mass_properties()               # massa en zwaartepunten
    build_lfs2.render_all()                    # afbeeldingen in previews/ en opslaan in werkstand
"""
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lfs2_params as P
import lfs2_kin as K
import lfs2_parts as G

DOC_NAME = "Liquid_Fertilizer_Applicator_Simple_v2"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Liquid_Fertilizer_Applicator_Simple_v2.FCStd")
PREVIEW_DIR = os.path.join(FOLDER, "previews")

COLOR = {
    "frame": (0.22, 0.24, 0.26),
    "knife": (0.30, 0.30, 0.32),
    "disc": (0.72, 0.74, 0.77),
    "steel": (0.85, 0.86, 0.88),
    "zinc": (0.82, 0.84, 0.87),
    "nozzle": (0.95, 0.75, 0.10),
    "pump": (0.12, 0.35, 0.65),
    "filter": (0.16, 0.16, 0.18),
    "hose": (0.96, 0.96, 0.92),
    "suction": (0.30, 0.65, 0.35),
    "tire": (0.08, 0.08, 0.08),
    "rim": (0.80, 0.12, 0.10),
    "actuator": (0.15, 0.15, 0.16),
    "chrome": (0.88, 0.89, 0.92),
    "robot_beam_lower": (0.47, 0.31, 0.22),
    "robot_beam_upper": (0.11, 0.11, 0.12),
    "robot_tire": (0.07, 0.07, 0.07),
    "robot_fork": (0.46, 0.47, 0.50),
}
TRANSPARENT = {"hose": 25, "suction": 15}
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


def lift_placement(psi):
    """Placement van het hefraam: psi graden, + = achterkant omhoog (rotatie om de draaibouten)."""
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -psi), V(0, P.pivot[0], P.pivot[1]))


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
    return hs


def build_actuator(doc, parent, psi, length=None):
    """Actuator in coordinaten van de bok: huis op de pen van het hefraam, stangoog in het langgat."""
    f = K.frame_pin(psi)
    pin = K.slot_pin(psi, length)
    body, rod = G.actuator(f, pin)
    grp = new_part(doc, parent, "Lift", "lift_actuator")
    add_shape(doc, grp, "act_body", "linear_actuator_body_1500N_200", body, "actuator")
    add_shape(doc, grp, "act_rod", "linear_actuator_rod", rod, "chrome")
    add_shape(doc, grp, "act_pin_slot", "actuator_pin_in_slot_M10", G.act_pin_bolt(pin, P.act_lug_gap), "zinc")
    add_shape(doc, grp, "act_pin_frame", "actuator_pin_frame_M10", G.act_pin_bolt(f, P.act_lug_gap), "zinc")
    return grp


def build_frame(doc, parent):
    add_shape(doc, parent, "toolbar", "toolbar_60x60x4", G.bar(), "frame")
    add_shape(doc, parent, "arms", "frame_arms_40x40x3_with_bushes", G.arms(), "frame")
    add_shape(doc, parent, "cross_tube", "cross_tube_with_actuator_lugs", G.cross_tube(), "frame")


_UNIT_CACHE = {}


def unit_shapes(side):
    """Vormen van een element (gecached per kant van de schijfarm)."""
    if side not in _UNIT_CACHE:
        _UNIT_CACHE[side] = {
            "plate": G.h_bottom_plate(side),
            "sides": G.h_side_plates(),
            "ubolts": G.h_ubolts(),
            "knife": G.knife(),
            "bolts": G.knife_bolts(),
            "tube": G.tube(),
            "clips": G.tube_clips(),
            "nozzle": G.nozzle(),
            "disc": G.disc(),
            "hub": G.disc_hub(side),
            "stub": G.disc_stub(side),
            "disc_arm": G.disc_arm(side),
        }
    return _UNIT_CACHE[side]


def build_unit(doc, parent, index, x):
    s = unit_shapes(P.disc_side[x])
    n = index + 1
    tag = "K%d" % n
    unit = new_part(doc, parent, "Knife_unit_%d" % n, "disc_and_knife_%d_x%+d" % (n, int(x)), translation(x=x))

    def add(key, label, color):
        return add_shape(doc, unit, "%s_%s" % (tag, key), "%s_k%d" % (label, n), s[key], color)

    add("plate", "holder_bottom_plate_100x10", "frame")
    add("disc_arm", "disc_arm_60x10", "frame")
    add("stub", "disc_stub_axle_M20", "zinc")
    add("hub", "disc_bearing_hub", "pump")
    add("disc", "coulter_disc_300x4", "disc")
    add("sides", "holder_side_plates_80x8", "frame")
    add("ubolts", "holder_u_bolts_M12", "zinc")
    add("knife", "slot_knife_50x10", "knife")
    add("bolts", "pivot_bolt_M12_and_shear_bolt_M6", "zinc")
    add("tube", "injection_tube_10x1", "steel")
    add("clips", "tube_clips_P_M6", "steel")
    add("nozzle", "nozzle_body_check_valve_orifice", "nozzle")
    return unit


def build_gauge_wheel(doc, parent, index, x):
    n = index + 1
    tag = "W%d" % n
    side = "left" if x < 0 else "right"
    grp = new_part(doc, parent, "Gauge_wheel_%d" % n, "gauge_wheel_%s" % side, translation(x=x))
    add_shape(doc, grp, tag + "_clamp", "gauge_wheel_clamp_plate_" + side, G.gw_clamp_plate(), "frame")
    add_shape(doc, grp, tag + "_ubolts", "gauge_wheel_u_bolts_M10_" + side, G.gw_ubolts(), "zinc")
    add_shape(doc, grp, tag + "_sleeve", "gauge_wheel_sleeve_50x50x4_" + side, G.gw_sleeve(), "frame")
    add_shape(doc, grp, tag + "_stem", "gauge_wheel_stem_40x40x3_" + side, G.gw_stem(), "frame")
    add_shape(doc, grp, tag + "_pin", "depth_pin_12_" + side, G.gw_pin(), "zinc")
    add_shape(doc, grp, tag + "_fork", "gauge_wheel_fork_" + side, G.gw_fork(), "frame")
    add_shape(doc, grp, tag + "_axle", "gauge_wheel_axle_bolt_M20_" + side, G.gw_axle_bolt(), "zinc")
    tire, rest = G.gw_wheel()
    add_shape(doc, grp, tag + "_tire", "wheelbarrow_tire_3.00-4_" + side, tire, "tire")
    add_shape(doc, grp, tag + "_rim", "wheelbarrow_rim_and_hub_" + side, rest, "rim")
    return grp


def build_dosing(doc, parent):
    grp = new_part(doc, parent, "Dosing", "dosing_unit_on_headstock")
    pump, filt, reg, mani = G.pump_shapes()
    add_shape(doc, grp, "pump", "diaphragm_pump_12V_bypass", pump, "pump")
    add_shape(doc, grp, "suction_filter", "suction_filter_50mesh_with_camlock", filt, "filter")
    add_shape(doc, grp, "regulator", "pressure_regulator_2bar_and_gauge", reg, "steel")
    add_shape(doc, grp, "manifold", "manifold_5_outlets", mani, "filter")
    add_shape(doc, grp, "link_hoses", "link_hoses_filter_pump_regulator", G.link_hoses(), "suction")
    return grp


def build_hoses(doc, parent, psi):
    grp = new_part(doc, parent, "Hoses", "outlet_hoses_flex_with_lift")
    for i, x in enumerate(P.row_x):
        add_shape(doc, grp, "hose_%d" % (i + 1), "outlet_hose_k%d" % (i + 1), G.outlet_hose(i, x, psi), "hose")
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
def build_into(doc, parent=None, psi=0.0, placement=None):
    """Zet het hele werktuig in een bestaand document. psi = hefhoek van het hefraam (graden, + = omhoog)."""
    root = new_part(doc, parent, "Applicator", "liquid_fertilizer_applicator_simple_v2", placement)
    build_headstock(doc, root)
    build_dosing(doc, root)
    build_actuator(doc, root, psi)
    build_hoses(doc, root, psi)
    frame = new_part(doc, root, "Swing_frame", "swing_frame_moves_with_lift", lift_placement(psi))
    build_frame(doc, frame)
    for i, x in enumerate(P.row_x):
        build_unit(doc, frame, i, x)
    for i, x in enumerate(P.gw_x):
        build_gauge_wheel(doc, frame, i, x)
    return root


def build(psi=0.0, save_path=SAVE_PATH, show_robot=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Liquid fertilizer applicator simple v2"
    doc.Comment = ("Gegenereerd met build_lfs2.py uit lfs2_params.py. x = rechts, y = rijrichting (voor = +y), "
                   "z = omhoog, grond = z 0. y = 0 is het hart van de achterste onderbalk van de robot "
                   "(wereld-y = y - 575). Heffen: build(psi=lfs2_kin.lift_angle()).")
    build_into(doc, None, psi)
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
MASS_FIXED = {"act_body": 2.6, "act_rod": 0.5, "pump": 2.3, "suction_filter": 0.7, "regulator": 0.5,
              "manifold": 0.3}
MASS_PREFIX = (("_tire", 1.6), ("_rim", 1.1), ("_nozzle", 0.08), ("_hub", 1.4))   # wiel ca. 2,7 kg; lagernaaf 1,4 kg
DENSITY = (("hose_", 1.3e-6 * 0.55), ("link_hoses", 1.3e-6 * 0.45))
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
    for key, m in MASS_PREFIX:
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


def mass_properties(doc=None):
    """Massa (kg) en zwaartepunt (y, z): heel werktuig en het hefraam (draait mee bij heffen)."""
    doc = doc or App.getDocument(DOC_NAME)
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in robot_names]
    moving = [o for o in doc.getObject("Swing_frame").OutListRecursive if o.TypeId == "Part::Feature"]
    m_all, c_all = _sum(feats)
    m_mov, c_mov = _sum(moving)
    knife = [o for o in doc.getObject("Knife_unit_1").OutListRecursive if o.TypeId == "Part::Feature"]
    m_k, c_k = _sum(knife)
    wheel = [o for o in doc.getObject("Gauge_wheel_1").OutListRecursive if o.TypeId == "Part::Feature"]
    m_w, c_w = _sum(wheel)
    return {"implement_kg": round(m_all, 1), "implement_cg": (round(c_all.y), round(c_all.z)),
            "moving_kg": round(m_mov, 1), "moving_cg": (round(c_mov.y), round(c_mov.z)),
            "knife_unit_kg": round(m_k, 2), "gauge_wheel_kg": round(m_w, 2)}


def mass_table(doc=None):
    """Massa per object (kg), gesorteerd."""
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
    tgt = V(*target) if target is not None else V(0, -300, 380)
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
    Gui.updateGui()                      # na een rebuild eerst de 3D-weergave laten bijwerken
    view = set_camera(direction, target, height, up)
    Gui.updateGui()
    view = set_camera(direction, target, height, up)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, name)
    view.saveImage(path, size[0], size[1], "White")
    return path


GROUND = "render_ground"


def add_ground(doc, y=(-900.0, 300.0)):
    shape = G.box_span((-700.0, 700.0), y, (-90.0, 0.0))
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = (0.55, 0.40, 0.25)
    obj.ViewObject.Transparency = 55
    return obj


def remove_ground(doc):
    if doc.getObject(GROUND):
        doc.removeObject(GROUND)


def render_work_previews(doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    out = []
    out.append(save_view("1_iso_rear_right.png", (-1.0, 1.0, -0.75)))
    out.append(save_view("2_iso_front_left.png", (1.0, -1.1, -0.7)))
    out.append(save_view("4_top.png", (0.0, 0.0, -1.0), up=(0.0, 1.0, 0.0)))
    out.append(save_view("5_rear.png", (0.0, 1.0, 0.0)))
    out.append(save_view("6_knife_detail.png", (-1.0, 0.8, -0.45), target=(-300, -480, 200), height=760))
    out.append(save_view("7_dosing_detail.png", (-1.0, 0.9, -0.9), target=(0, -60, 720), height=560))
    add_ground(doc)
    try:
        out.append(save_view("3_side_right.png", (-1.0, 0.0, 0.0), target=(0, -330, 360), height=1050))
        out.append(save_view("8_knife_side.png", (-1.0, 0.0, 0.0), target=(0, -470, 150), height=640))
    finally:
        remove_ground(doc)
    return out


def render_all():
    """Alle afbeeldingen: geheven + robotreferentie, daarna werkstand (die wordt opgeslagen)."""
    out = []
    doc = build(psi=K.lift_angle(), save_path=None, show_robot=True)
    add_ground(doc)
    try:
        out.append(save_view("9_lifted_side_with_robot.png", (-1.0, 0.0, 0.0), target=(0, -250, 420), height=1150))
    finally:
        remove_ground(doc)
    out.append(save_view("10_lifted_iso_with_robot.png", (-1.0, 1.0, -0.6)))
    doc = build(psi=0.0, save_path=None, show_robot=True)
    out.append(save_view("11_work_iso_with_robot.png", (1.0, -1.0, -0.65)))
    set_robot_reference(False, doc)
    out += render_work_previews(doc)
    doc.saveAs(SAVE_PATH)
    return out
