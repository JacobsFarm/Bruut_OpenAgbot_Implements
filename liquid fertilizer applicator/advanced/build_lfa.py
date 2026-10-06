import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lfa_params as P
import lfa_parts as G

DOC_NAME = "Liquid_Fertilizer_Applicator"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Liquid_Fertilizer_Applicator.FCStd")
PREVIEW_DIR = os.path.join(FOLDER, "previews")

COLOR = {
    "frame": (0.22, 0.24, 0.26),
    "arm": (0.93, 0.42, 0.08),
    "disc": (0.72, 0.74, 0.77),
    "band": (0.10, 0.10, 0.10),
    "knife": (0.30, 0.30, 0.32),
    "steel": (0.85, 0.86, 0.88),
    "valve": (0.80, 0.62, 0.25),
    "spring": (0.90, 0.78, 0.25),
    "zinc": (0.82, 0.84, 0.87),
    "pump": (0.12, 0.35, 0.65),
    "filter": (0.16, 0.16, 0.18),
    "hose": (0.96, 0.96, 0.92),
    "suction": (0.30, 0.65, 0.35),
    "wheel": (0.70, 0.72, 0.74),
    "chain": (0.25, 0.25, 0.27),
    "actuator": (0.15, 0.15, 0.16),
    "chrome": (0.88, 0.89, 0.92),
    "sensor": (0.95, 0.60, 0.10),
    "robot_beam_lower": (0.47, 0.31, 0.22),
    "robot_beam_upper": (0.11, 0.11, 0.12),
    "robot_tire": (0.07, 0.07, 0.07),
    "robot_fork": (0.46, 0.47, 0.50),
}
TRANSPARENT = {"hose": 25, "suction": 20}
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
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), angle), V(0, center[0], center[1]))


# ---------------------------------------------------------------------
# Kinematica heffen
# ---------------------------------------------------------------------
def lift_state(lift):
    """Parallellogram: hoek van de stangen en verplaatsing van de toolbar bij hefhoogte lift."""
    s = max(-0.5, min(0.95, lift / P.link_length))
    theta = math.asin(s)
    return math.degrees(theta), P.link_length * (1.0 - math.cos(theta)), lift


def contact_drop(rel, lift, max_deg):
    """Hoek waarover een arm (punt rel t.o.v. draaipunt) zakt zolang hij nog op de grond rust."""
    if lift <= 0:
        return 0.0
    lo, hi = 0.0, max_deg
    if rel[1] - G.rot_yz(rel, hi, (0.0, 0.0))[1] <= lift:
        return max_deg
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if rel[1] - G.rot_yz(rel, mid, (0.0, 0.0))[1] < lift:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def pin_b(lift):
    theta, dy, dz = lift_state(lift)
    return (P.act_b[0] + dy, P.act_b[1] + dz)


def ab_length(lift):
    """Afstand onderkant langgat (act_a) tot de onderste pen bij hefhoogte lift."""
    b = pin_b(lift)
    return math.hypot(b[0] - P.act_a[0], b[1] - P.act_a[1])


def lift_for_ab(ab):
    """Hefhoogte waarbij de afstand act_a - pen B gelijk is aan ab (ab neemt af als de balk stijgt)."""
    lo, hi = -0.45 * P.link_length, 0.9 * P.link_length
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if ab_length(mid) > ab:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def float_range(length=P.act_extended):
    """Zweefbereik van de balk (laagste, hoogste hefhoogte) bij actuatorlengte length."""
    return lift_for_ab(length), lift_for_ab(length - P.act_slot)


def actuator_points(lift, length=None):
    """(bovenste pen in het langgat, onderste pen). Zonder length: werkstand (actuator uit) als de balk
    op of onder de ontwerphoogte zweeft, anders getrokken (pen onderin het langgat)."""
    b = pin_b(lift)
    ab = ab_length(lift)
    if length is None:
        length = P.act_extended if lift <= 0.0 else ab
    s = max(0.0, min(P.act_slot, length - ab))
    uy, uz = (b[0] - P.act_a[0]) / ab, (b[1] - P.act_a[1]) / ab
    return (P.act_a[0] - s * uy, P.act_a[1] - s * uz), b


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
    add_shape(doc, hs, "hs_cross_top", "headstock_cross_tube_actuator", G.hs_cross_top(), "frame")
    add_shape(doc, hs, "hs_cross_low", "headstock_cross_tube_lower", G.hs_cross_low(), "frame")
    return hs


def build_links(doc, parent, theta):
    grp = new_part(doc, parent, "Linkage", "parallel_linkage")
    for side, tag in ((-1, "left"), (1, "right")):
        local = G.link_local(side)
        for z, level in ((P.pin_upper_z, "upper"), (P.pin_lower_z, "lower")):
            shape = G.moved(local, y=P.pin_front_y, z=z)
            shape.rotate(V(0, P.pin_front_y, z), V(1, 0, 0), -theta)
            add_shape(doc, grp, "link_%s_%s" % (level, tag), "link_%s_%s" % (level, tag), shape, "frame")
    return grp


def build_actuator(doc, parent, lift):
    a, b = actuator_points(lift)
    body, rod = G.actuator(b, a)
    grp = new_part(doc, parent, "Lift", "lift_actuator")
    add_shape(doc, grp, "act_body", "linear_actuator_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "linear_actuator_rod", rod, "chrome")
    return grp


def build_toolbar(doc, parent):
    add_shape(doc, parent, "toolbar", "toolbar_60x60x4", G.toolbar(), "frame")
    for side, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, parent, "rf_in_" + tag, "rear_frame_plate_inner_" + tag, G.rf_plate(side, True), "frame")
        add_shape(doc, parent, "rf_out_" + tag, "rear_frame_plate_outer_" + tag, G.rf_plate(side, False), "frame")
        add_shape(doc, parent, "rf_pins_" + tag, "link_pins_rear_" + tag, G.rf_pins(side), "zinc")
    add_shape(doc, parent, "rf_cross", "rear_frame_cross_tube_actuator", G.rf_cross(), "frame")


def build_drive(doc, parent, wheel_drop):
    grp = new_part(doc, parent, "Drive", "ground_wheel_drive_and_pump")
    add_shape(doc, grp, "pump", "peristaltic_pump_5ch", G.pump_body(), "pump")
    add_shape(doc, grp, "pump_nipples", "pump_hose_nipples", G.pump_nipples(), "steel")
    add_shape(doc, grp, "pump_bracket", "pump_bracket", G.pump_bracket(), "frame")
    add_shape(doc, grp, "inlet_filter", "inlet_filter_and_manifold", G.inlet_filter(), "filter")
    suction, camlock = G.suction_hose()
    add_shape(doc, grp, "suction_hose", "suction_hose_to_robot_tank", suction, "suction")
    add_shape(doc, grp, "camlock", "camlock_coupling", camlock, "zinc")
    add_shape(doc, grp, "coupling", "shaft_coupling", G.coupling(), "steel")
    add_shape(doc, grp, "jackshaft", "drive_shaft", G.jackshaft(), "steel")
    add_shape(doc, grp, "jack_sprocket", "sprocket_15T_drive_shaft", G.jack_sprocket(), "chain")
    for i, tag in ((0, "left"), (1, "right")):
        add_shape(doc, grp, "bearing_plate_" + tag, "bearing_plate_" + tag, G.bearing_plate(i), "frame")
        add_shape(doc, grp, "bearing_" + tag, "flange_bearing_UCFL204_" + tag, G.flange_bearing(i), "pump")
    add_shape(doc, grp, "bearing_bolts", "bearing_bolts_M10", G.bearing_bolts(), "zinc")
    add_shape(doc, grp, "torsion_spring", "torsion_spring_ground_wheel", G.torsion_spring(), "spring")
    bracket, sensor = G.sensor_parts()
    add_shape(doc, grp, "sensor_bracket", "sensor_bracket", bracket, "frame")
    add_shape(doc, grp, "sensor", "inductive_sensor_M18", sensor, "sensor")

    arm = new_part(doc, grp, "Ground_wheel_arm", "ground_wheel_arm_swing", rotation_x(wheel_drop, P.jack))
    add_shape(doc, arm, "gw_arm", "ground_wheel_arm", G.gw_arm(), "frame")
    add_shape(doc, arm, "gw_axle", "ground_wheel_axle", G.gw_axle(), "steel")
    add_shape(doc, arm, "gw_wheel", "ground_wheel_400_spiked", G.gw_wheel(), "wheel")
    add_shape(doc, arm, "gw_sprocket", "sprocket_30T_ground_wheel", G.gw_wheel_sprocket(), "chain")
    add_shape(doc, arm, "gw_chain", "roller_chain_08B", G.gw_chain(), "chain")
    return grp


_UNIT_CACHE = {}


def unit_shapes():
    if not _UNIT_CACHE:
        _UNIT_CACHE.update({
            "clamp_front": G.u_clamp_plate(True),
            "clamp_rear": G.u_clamp_plate(False),
            "clamp_bolts": G.u_clamp_bolts(),
            "tongue": G.u_tongue(),
            "anchor": G.u_anchor_plate(),
            "pivot_pin": G.u_pivot_pin(),
            "fork_l": G.u_fork_plate(-1),
            "fork_r": G.u_fork_plate(1),
            "lug_pin": G.u_lug_pin(),
            "axle": G.u_axle(),
            "hub": G.u_hub(),
            "disc": G.u_disc(),
            "band_l": G.u_band(-1),
            "band_r": G.u_band(1),
            "knife": G.u_knife(),
            "knife_hw": G.u_knife_hardware(),
            "tube": G.u_tube(),
            "valve": G.u_valve(),
        })
    return _UNIT_CACHE


def build_unit(doc, parent, index, x, drop, strut):
    s = unit_shapes()
    n = index + 1
    tag = "U%d" % n
    unit = new_part(doc, parent, "Unit_%d" % n, "injection_unit_%d_x%+d" % (n, int(x)), translation(x=x))

    def add(target, key, label, color):
        return add_shape(doc, target, "%s_%s" % (tag, key), "%s_u%d" % (label, n), s[key], color)

    add(unit, "clamp_front", "clamp_plate_front", "frame")
    add(unit, "clamp_rear", "clamp_plate_rear", "frame")
    add(unit, "clamp_bolts", "clamp_bolts_M12", "zinc")
    add(unit, "tongue", "unit_bracket", "frame")
    add(unit, "anchor", "spring_anchor_plate", "frame")
    add(unit, "pivot_pin", "pivot_pin", "zinc")
    rod, spring, spring_len = strut
    add_shape(doc, unit, tag + "_strut_rod", "spring_rod_u%d" % n, rod, "zinc")
    add_shape(doc, unit, tag + "_spring", "downforce_spring_u%d" % n, spring, "spring")

    arm = new_part(doc, unit, "Unit_%d_arm" % n, "unit_%d_swing_arm" % n, rotation_x(drop, P.u_pivot))
    add(arm, "fork_l", "fork_plate_left", "arm")
    add(arm, "fork_r", "fork_plate_right", "arm")
    add(arm, "lug_pin", "spring_pin", "zinc")
    add(arm, "axle", "disc_axle", "zinc")
    add(arm, "hub", "disc_hub", "steel")
    add(arm, "disc", "coulter_disc_300", "disc")
    add(arm, "band_l", "depth_band_left", "band")
    add(arm, "band_r", "depth_band_right", "band")
    add(arm, "knife", "slot_knife", "knife")
    add(arm, "knife_hw", "knife_bolts_and_spacers", "zinc")
    add(arm, "tube", "injection_tube_8x1", "steel")
    add(arm, "valve", "check_valve", "valve")
    return unit


def build_hoses(doc, parent, drop):
    grp = new_part(doc, parent, "Hoses", "outlet_hoses")
    for i, x in enumerate(P.row_x):
        add_shape(doc, grp, "hose_%d" % (i + 1), "outlet_hose_u%d" % (i + 1), G.outlet_hose(i, x, drop), "hose")
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
def build_into(doc, parent=None, lift=0.0, placement=None):
    """Zet het hele werktuig in een bestaand document (ook gebruikt door animate_lfa.py)."""
    theta, dy, dz = lift_state(lift)
    disc_rel = (P.disc_y - P.u_pivot[0], P.disc_z - P.u_pivot[1])
    drop = contact_drop(disc_rel, lift, P.unit_drop_deg)
    wheel_drop = contact_drop(P.gw_wheel_rel, lift, P.wheel_drop_deg)

    root = new_part(doc, parent, "Applicator", "liquid_fertilizer_applicator", placement)
    build_headstock(doc, root)
    build_links(doc, root, theta)
    build_actuator(doc, root, lift)
    bar = new_part(doc, root, "Toolbar_assembly", "toolbar_assembly_moves_with_lift", translation(0.0, dy, dz))
    build_toolbar(doc, bar)
    build_drive(doc, bar, wheel_drop)
    strut = G.u_strut(drop)
    for i, x in enumerate(P.row_x):
        build_unit(doc, bar, i, x, drop, strut)
    build_hoses(doc, bar, drop)
    return root


def build(lift=0.0, save_path=SAVE_PATH, show_robot=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Liquid fertilizer applicator"
    doc.Comment = ("Gegenereerd met build_lfa.py uit lfa_params.py. x = rechts, y = rijrichting (voor = +y), "
                   "z = omhoog, grond = z 0. y = 0 is het hart van de achterste onderbalk van de robot "
                   "(wereld-y = y - 575). Heffen: build(lift=...).")
    build_into(doc, None, lift)
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


def solids_of(doc, include_robot):
    out = []
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
    for obj in doc.Objects:
        if obj.TypeId != "Part::Feature":
            continue
        if obj.Name in robot_names and not include_robot:
            continue
        out.append((obj, global_shape(obj)))
    return out


def check_interference(doc=None, include_robot=True, tol=1.0):
    """Volume-overlap tussen alle onderdelen (mm3). Robotreferentie alleen tegen het werktuig."""
    doc = doc or App.getDocument(DOC_NAME)
    items = solids_of(doc, include_robot)
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
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


# massa per object: vaste waarde (kg) voor gekochte delen die als massief blok getekend zijn,
# anders volume x dichtheid (kg/mm3)
MASS_FIXED = {"pump": 6.0, "act_body": 3.5, "act_rod": 0.8, "inlet_filter": 1.5, "sensor": 0.15, "camlock": 0.3}
DENSITY = (("band", 1.2e-6), ("suction_hose", 1.3e-6 * 0.3), ("hose_", 1.3e-6 * 0.55), ("valve", 8.5e-6 * 0.5))
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
    """Massa (kg) en zwaartepunt: heel werktuig, bewegend deel (toolbar) en een zwenkarm van element 1."""
    doc = doc or App.getDocument(DOC_NAME)
    robot = doc.getObject("Robot_reference")
    robot_names = {o.Name for o in robot.Group} if robot else set()
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in robot_names]
    moving = [o for o in doc.getObject("Toolbar_assembly").OutListRecursive if o.TypeId == "Part::Feature"]
    arm = [o for o in doc.getObject("Unit_1_arm").OutListRecursive if o.TypeId == "Part::Feature"]
    m_all, c_all = _sum(feats)
    m_mov, c_mov = _sum(moving)
    m_arm, c_arm = _sum(arm)
    return {"implement_kg": round(m_all, 1), "implement_cg": (round(c_all.y), round(c_all.z)),
            "moving_kg": round(m_mov, 1), "implement_cg_y": round(c_mov.y),
            "arm_kg": round(m_arm, 2), "arm_cg_y": round(c_arm.y)}


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
    tgt = V(*target) if target is not None else V(0, -500, 350)
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


def add_ground(doc):
    grp = doc.getObject("Applicator")
    shape = G.box_span((-700.0, 700.0), (-1250.0, 300.0), (-90.0, 0.0))
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
    out.append(save_view("6_unit_detail.png", (-1.0, 0.75, -0.45), target=(-400, -700, 200), height=900))
    out.append(save_view("7_drive_detail.png", (-1.0, 0.9, -0.6), target=(220, -560, 380), height=850))
    add_ground(doc)
    try:
        out.append(save_view("3_side_right.png", (-1.0, 0.0, 0.0), target=(0, -500, 330), height=1250))
        out.append(save_view("8_unit_side.png", (-1.0, 0.0, 0.0), target=(0, -700, 200), height=700))
    finally:
        remove_ground(doc)
    return out


def render_all():
    """Alle afbeeldingen: geheven + robotreferentie, daarna werkstand (die wordt opgeslagen)."""
    out = []
    doc = build(lift=P.lift_height, save_path=None, show_robot=True)
    add_ground(doc)
    try:
        out.append(save_view("9_lifted_side_with_robot.png", (-1.0, 0.0, 0.0), target=(0, -400, 420), height=1400))
    finally:
        remove_ground(doc)
    out.append(save_view("10_lifted_iso_with_robot.png", (-1.0, 1.0, -0.6)))
    doc = build(lift=0.0, save_path=None, show_robot=True)
    out.append(save_view("11_work_iso_with_robot.png", (1.0, -1.0, -0.65)))
    set_robot_reference(False, doc)
    out += render_work_previews(doc)
    doc.save() if doc.FileName else doc.saveAs(SAVE_PATH)
    return out
