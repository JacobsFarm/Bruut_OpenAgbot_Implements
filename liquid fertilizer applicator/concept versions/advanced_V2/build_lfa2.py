"""Bouwt de toediener advanced V2: ophanging van advanced, per rij een V-schijfpaar met dubbel mes en aandrukwiel,
en de 10-sectie rollenpomp met jerrycans op de robot (pompset), met 10 slangen.

Boom: Applicator (werktuigcoordinaten, y = 0 hart achterste onderbalk van de robot)
        Headstock, Linkage, Lift                  als advanced
        Toolbar_assembly                          beweegt mee met heffen
          toolbar, achterframe
          Unit_1..5                                klemmen, beugel, veerpoot
            Unit_n_arm                             (draait om het draaipunt) vork, dwarskoker, hangplaten, 2 schijven
                                                   met naaf/ring/as, dubbel mes met 2 buisjes, aandrukwiel
              Unit_n_press_arm                     sleeparm aandrukwiel
        Pump_kit                                   vast op de robot: pompsteun + blokken, jerrycans, Roller_pump
        Hoses                                      hose_A_1..5, hose_B_1..5 (pomp -> buisje A/B)
      Robot_reference (verborgen)
"""
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lfa2_params as P
import lfa2_parts as G
import lfa2_pumpkit as PK
import rp_params as RP

DOC_NAME = "Liquid_Fertilizer_Applicator_V2"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Liquid_Fertilizer_Applicator_V2.FCStd")
STEP_PATH = os.path.join(FOLDER, "Liquid_Fertilizer_Applicator_V2.step")
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
    "actuator": (0.15, 0.15, 0.16),
    "chrome": (0.88, 0.89, 0.92),
    "tire": (0.09, 0.09, 0.09),
    "rim": (0.93, 0.76, 0.16),
    "robot_beam_lower": (0.47, 0.31, 0.22),
    "robot_beam_upper": (0.11, 0.11, 0.12),
    "robot_tire": (0.07, 0.07, 0.07),
    "robot_fork": (0.46, 0.47, 0.50),
    "hose_A": (0.35, 0.62, 0.92),        # vloeistof A: blauw (als combined_v3)
    "hose_B": (0.95, 0.62, 0.20),        # vloeistof B: oranje
    "mount": (0.18, 0.36, 0.62),
    "divider": (0.85, 0.15, 0.12),
    "can_A": (0.16, 0.42, 0.78),
    "can_B": (0.93, 0.50, 0.08),
    "cap": (0.12, 0.12, 0.13),
    "tray": (0.80, 0.81, 0.83),
    "tube_A": (0.35, 0.62, 0.92),
    "tube_B": (0.95, 0.62, 0.20),
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


def press_beta(drop, bar_dz):
    """Hoek van de sleeparm van het aandrukwiel (graden, + = wiel omlaag) op vlakke grond: het wiel raakt de grond,
    of hangt op de onderaanslag. drop = armhoek element, bar_dz = balk t.o.v. de ontwerphoogte."""
    w0 = G.pw_wheel_center()
    r = P.pw_d / 2.0

    def gap(beta):
        w = G.rot_yz(G.rot_yz(w0, beta, P.pw_pivot), drop, P.u_pivot)
        return w[1] + bar_dz - r
    lo, hi = P.pw_up_deg, P.pw_down_deg
    if gap(hi) >= 0.0:
        return hi
    if gap(lo) <= 0.0:
        return lo
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if gap(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


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
    """Zweefbereik van de balk (laagste, hoogste hefhoogte) bij actuatorlengte length: laagste met de pen onderin
    het langgat (act_a), hoogste met de pen bovenin (G.act_slot_end)."""
    import lfa2_calc
    return lfa2_calc.lift_for_len(length), lfa2_calc.lift_for_len(length, slot_top=True)


def slot_pin(b, length):
    """Pen in het (vaste) langgat op afstand length van de onderste pen b: A + s * e, s geklemd op 0 ... act_slot."""
    import lfa2_calc
    return lfa2_calc.slot_pin(b, length)


def actuator_points(lift, length=None):
    """(bovenste pen in het langgat, onderste pen). Zonder length: werkstand (actuator uit) als de balk
    op of onder de ontwerphoogte zweeft, anders getrokken (pen onderin het langgat)."""
    b = pin_b(lift)
    if length is None:
        length = P.act_extended if lift <= 0.0 else ab_length(lift)
    return slot_pin(b, length), b


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
    add_shape(doc, grp, "act_body", "linear_actuator_LA36_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "linear_actuator_LA36_rod", rod, "chrome")
    add_shape(doc, grp, "act_pins", "actuator_pins_12mm", G.actuator_pins(b, a), "zinc")
    return grp


def build_toolbar(doc, parent):
    add_shape(doc, parent, "toolbar", "toolbar_60x60x4", G.toolbar(), "frame")
    for side, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, parent, "rf_in_" + tag, "rear_frame_plate_inner_" + tag, G.rf_plate(side, True), "frame")
        add_shape(doc, parent, "rf_out_" + tag, "rear_frame_plate_outer_" + tag, G.rf_plate(side, False), "frame")
        add_shape(doc, parent, "rf_pins_" + tag, "link_pins_rear_" + tag, G.rf_pins(side), "zinc")
    add_shape(doc, parent, "rf_cross", "rear_frame_cross_tube_actuator", G.rf_cross(), "frame")


def build_pump_kit(doc, parent, angle=0.0):
    """Pompset op de robot (vast, beweegt niet mee met heffen): pompsteun met blokken, prop en aanvoerstompen,
    jerrycans met bak, kranen en aanvoerslangen (lfa2_pumpkit) en de rollenpomp zelf (roller_pump/build_rp)."""
    import build_rp
    RP.configure(P.pump_channels)
    grp = new_part(doc, parent, "Pump_kit", "pump_kit_on_robot")
    for name, (label, shape, color) in PK.shapes().items():
        add_shape(doc, grp, name, label, shape, color)
    add_shape(doc, grp, "pump_risers", "pump_riser_blocks_40x60x100", G.pump_risers(), "mount")
    build_rp.build_into(doc, grp, angle, PK.pump_placement())
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
            "yoke": G.u_yoke(),
            "knife": G.u_knife(),
            "tube_A": G.u_knife_tube(0),
            "tube_B": G.u_knife_tube(1),
            "knife_welds": G.u_knife_welds(),
            "knife_hw": G.u_knife_hardware(),
        })
        for side, tag in ((-1, "l"), (1, "r")):
            _UNIT_CACHE.update({
                "hanger_" + tag: G.u_hanger(side),
                "axle_" + tag: G.u_stub_axle(side),
                "hub_" + tag: G.u_hub(side),
                "disc_" + tag: G.u_disc(side),
                "band_" + tag: G.u_band(side),
            })
        if P.press_wheel:
            _UNIT_CACHE.update({
                "pw_pivot": G.pw_pivot_hardware(),
                "pw_stop": G.pw_stop_hardware(),
                "pw_coil_l": G.pw_coil(-1),
                "pw_coil_r": G.pw_coil(1),
                "pw_strap_l": G.pw_strap(-1),
                "pw_strap_r": G.pw_strap(1),
                "pw_peg_l": G.pw_peg(-1),
                "pw_peg_r": G.pw_peg(1),
                "pw_leg_l": G.pw_moving_leg(-1),
                "pw_leg_r": G.pw_moving_leg(1),
                "pw_axle": G.pw_axle(),
                "pw_hub": G.pw_hub(),
                "pw_rim": G.pw_rim(),
                "pw_tire": G.pw_tire(),
            })
    return _UNIT_CACHE


def build_press_wheel(doc, arm, add, n, beta):
    """Aandrukwiel: vaste delen op de element-arm, sleeparm als eigen sub-Part (draait om pw_pivot)."""
    add(arm, "pw_pivot", "press_arm_pivot_pin", "zinc")
    add(arm, "pw_stop", "press_arm_stop_bolt", "zinc")
    add(arm, "pw_coil_l", "press_torsion_spring_left", "spring")
    add(arm, "pw_coil_r", "press_torsion_spring_right", "spring")
    sw = new_part(doc, arm, "Unit_%d_press_arm" % n, "unit_%d_press_wheel_arm" % n, rotation_x(beta, P.pw_pivot))
    add(sw, "pw_strap_l", "press_arm_strap_left", "arm")
    add(sw, "pw_strap_r", "press_arm_strap_right", "arm")
    add(sw, "pw_peg_l", "press_spring_peg_left", "zinc")
    add(sw, "pw_peg_r", "press_spring_peg_right", "zinc")
    add(sw, "pw_leg_l", "press_spring_leg_left", "spring")
    add(sw, "pw_leg_r", "press_spring_leg_right", "spring")
    add(sw, "pw_axle", "press_wheel_axle_M12", "zinc")
    add(sw, "pw_hub", "press_wheel_hub", "steel")
    add(sw, "pw_rim", "press_wheel_rim", "rim")
    add(sw, "pw_tire", "press_wheel_tire_250x40", "tire")
    return sw


def build_unit(doc, parent, index, x, drop, strut, beta=0.0):
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
    add(arm, "yoke", "disc_yoke_tube_40x40", "arm")
    for sd, side in (("l", "left"), ("r", "right")):
        add(arm, "hanger_" + sd, "disc_hanger_" + side, "arm")
        add(arm, "axle_" + sd, "disc_stub_axle_" + side, "zinc")
        add(arm, "hub_" + sd, "disc_hub_" + side, "steel")
        add(arm, "disc_" + sd, "v_disc_325_" + side, "disc")
        add(arm, "band_" + sd, "depth_band_" + side, "band")
    add(arm, "knife", "double_injector_knife", "knife")
    add(arm, "tube_A", "knife_tube_A", "tube_A")
    add(arm, "tube_B", "knife_tube_B", "tube_B")
    add(arm, "knife_welds", "knife_tube_welds", "steel")
    add(arm, "knife_hw", "knife_bolts_and_spacers", "zinc")
    if P.press_wheel:
        build_press_wheel(doc, arm, add, n, beta)
    return unit


def hose_name(row, liquid):
    return "hose_%s_%d" % (liquid, row + 1)


def build_hoses(doc, parent, drop, lift):
    grp = new_part(doc, parent, "Hoses", "hoses_pump_to_knives")
    for liq in P.LIQUIDS:
        for i in range(len(P.row_x)):
            add_shape(doc, grp, hose_name(i, liq), "hose_8x12_liquid_%s_row_%d" % (liq, i + 1),
                      G.outlet_hose(i, liq, drop, lift), "hose_" + liq)
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
    """Zet het hele werktuig in een bestaand document (ook gebruikt door animate_lfa2.py)."""
    theta, dy, dz = lift_state(lift)
    band, r_band = P.band_contact()
    disc_rel = (band[1] - P.u_pivot[0], band[2] - r_band - P.u_pivot[1])
    drop = contact_drop(disc_rel, lift, P.unit_drop_deg)

    root = new_part(doc, parent, "Applicator", "liquid_fertilizer_applicator", placement)
    build_headstock(doc, root)
    build_links(doc, root, theta)
    build_actuator(doc, root, lift)
    bar = new_part(doc, root, "Toolbar_assembly", "toolbar_assembly_moves_with_lift", translation(0.0, dy, dz))
    build_toolbar(doc, bar)
    build_pump_kit(doc, root)
    strut = G.u_strut(drop)
    beta = press_beta(drop, dz) if P.press_wheel else 0.0
    for i, x in enumerate(P.row_x):
        build_unit(doc, bar, i, x, drop, strut, beta)
    build_hoses(doc, root, drop, lift)
    return root


def build(lift=0.0, save_path=SAVE_PATH, show_robot=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Liquid fertilizer applicator advanced V2"
    doc.Comment = ("Gegenereerd met build_lfa2.py uit lfa2_params.py (advanced V2). x = rechts, y = rijrichting (voor = +y), "
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


def _names(doc, part):
    obj = doc.getObject(part)
    return {o.Name for o in obj.OutListRecursive} if obj else set()


# bedoelde overlap: lassen (mes), aansluitingen van de pompset (kraan in de jerrycan en door de bakrand, aanvoerslang
# over de stomp), zoals in de eigen mappen van mes en combined_v3
ALLOWED = (("knife_tube_welds", ""), ("tap_half_inch", "jerrycan_20l"), ("tap_half_inch", "tank_tray"),
           ("supply_hose", "manifold_inlets"))


def _allowed(la, lb):
    for a, b in ALLOWED:
        if (la.startswith(a) and lb.startswith(b)) or (lb.startswith(a) and la.startswith(b)):
            return True
    return False


def check_interference(doc=None, include_robot=True, tol=1.0):
    """Volume-overlap tussen alle onderdelen (mm3). Robotreferentie alleen tegen het werktuig. De rollenpomp onderling
    wordt niet getest (dat doet roller_pump/build_rp.check_interference), wel tegen de rest; de slangen apart met
    check_hoses (punten op de slang: booleans met geveegde slangen duren te lang)."""
    doc = doc or App.getDocument(DOC_NAME)
    items = [(o, s) for o, s in solids_of(doc, include_robot) if o.Name not in _names(doc, "Hoses")]
    robot_names = _names(doc, "Robot_reference")
    pump_names = _names(doc, "Roller_pump")
    hits = []
    for i in range(len(items)):
        oa, sa = items[i]
        ba = sa.BoundBox
        for j in range(i + 1, len(items)):
            ob, sb = items[j]
            if oa.Name in robot_names and ob.Name in robot_names:
                continue
            if oa.Name in pump_names and ob.Name in pump_names:
                continue
            if not ba.intersect(sb.BoundBox) or _allowed(oa.Label, ob.Label):
                continue
            try:
                vol = sa.common(sb).Volume
            except Exception as exc:
                hits.append((oa.Label, ob.Label, "error %s" % exc))
                continue
            if vol > tol:
                hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits


def check_poses(lifts=(0.0, P.lift_height)):
    """Bouwt het werktuig in elke hefhoogte (met robotreferentie) en controleert onderdelen en slangen; daarna weer in
    werkstand. Duurt enkele minuten: vanuit MCP met QtCore.QTimer.singleShot starten."""
    out = {}
    for lift in lifts:
        doc = build(lift=lift, save_path=None, show_robot=True)
        out[lift] = {"interference": check_interference(doc), "hoses": check_hoses(doc, lift)}
    build(lift=0.0, save_path=None)
    return out


def _hose_ring(curve, step=5.0, ring=8, skip=6.0):
    """Punten net binnen het oppervlak van een slang (elke step mm, ring punten rond) en de hartlijnpunten."""
    a, length = curve.FirstParameter, curve.length()
    r = P.hose_od / 2.0 - 0.2
    centre, pts = [], []
    n = int(length / step)
    for k in range(n + 1):
        s = length * k / n
        if s < skip or s > length - skip:
            continue
        u = curve.parameterAtDistance(s, a)
        p, t = curve.value(u), curve.tangent(u)[0]
        e1 = t.cross(V(0, 0, 1)) if abs(t.z) < 0.9 else t.cross(V(1, 0, 0))
        e1.normalize()
        e2 = t.cross(e1)
        centre.append(p)
        for j in range(ring):
            w = 2.0 * math.pi * j / ring
            pts.append(p + e1 * (r * math.cos(w)) + e2 * (r * math.sin(w)))
    return centre, pts


def check_hoses(doc=None, lift=0.0, drop=None):
    """Slangen tegen alle delen (punten op de slang die in een solid liggen; robotreferentie als blok) en de kleinste
    afstand tussen twee slangen (hartlijnen). Bij hefhoogte lift (het document moet in die stand gebouwd zijn)."""
    doc = doc or App.getDocument(DOC_NAME)
    if drop is None:
        band, r_band = P.band_contact()
        drop = contact_drop((band[1] - P.u_pivot[0], band[2] - r_band - P.u_pivot[1]), lift, P.unit_drop_deg)
    hose_names = _names(doc, "Hoses")
    robot_names = _names(doc, "Robot_reference")
    solids = []
    for o, s in solids_of(doc, True):
        if o.Name in hose_names:
            continue
        if o.Name in robot_names:
            solids.append((o.Label + " (blok)", None, s.BoundBox))
        else:
            for so in (s.Solids or []):
                solids.append((o.Label, so, so.BoundBox))
    hits = {}
    centres = {}
    for liq in P.LIQUIDS:
        for i in range(len(P.row_x)):
            name = hose_name(i, liq)
            centre, ring = _hose_ring(G.hose_curve(i, liq, drop, lift))
            centres[name] = centre
            for label, so, bb in solids:
                k = sum(1 for p in ring if bb.isInside(p) and (so is None or so.isInside(p, 0.01, False)))
                if k:
                    hits[(name, label)] = k
    names = sorted(centres)
    best = (1e9, None, None)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            d = min((p - q).Length for p in centres[names[a]][::2] for q in centres[names[b]][::2]) - P.hose_od
            if d < best[0]:
                best = (round(d, 1), names[a], names[b])
    bends = {hose_name(i, liq): round(G.min_bend_radius(i, liq, drop, lift), 1)
             for liq in P.LIQUIDS for i in range(len(P.row_x))}
    return {"hits": [(a, b, k) for (a, b), k in sorted(hits.items())], "hose_gap_min": best,
            "min_bend_r": min(bends.values()), "bends": bends}


# massa per object: vaste waarde (kg) voor gekochte delen die als massief blok getekend zijn,
# anders volume x dichtheid (kg/mm3)
# LA36: 4.55 kg bij slag 100 + 0.24 kg per 50 mm (datasheet blz. 7); stang + oog ca. 0.6 kg daarvan
MASS_FIXED = {"act_body": P.act_mass_100 + P.act_mass_per_50 * (P.act_stroke - 100.0) / 50.0 - 0.6, "act_rod": 0.6}
PUMP_KG = 33.0                  # roller_pump/README.md: 10 secties zonder vloeistof (pomp als geheel geteld)
DENSITY = (("band", 1.2e-6), ("pw_tire", 1.2e-6 * 0.5), ("pw_rim", 1.15e-6), ("supply_hose", 1.3e-6 * 0.55),
           ("hose_", 1.3e-6 * 0.55), ("jerrycan_cap", 1.0e-6), ("jerrycan", 0.95e-6 * 0.1), ("tank_tray", 2.7e-6),
           ("tap_", 1.0e-6), ("divider", 1.0e-6))
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
    kit = doc.getObject("Pump_kit")
    pump = doc.getObject("Roller_pump")
    pump_names = {o.Name for o in pump.OutListRecursive} if pump else set()
    kit_names = {o.Name for o in kit.OutListRecursive} if kit else set()
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name not in robot_names
             and o.Name not in kit_names]
    kit_parts = [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name in kit_names
                 and o.Name not in pump_names]
    moving = [o for o in doc.getObject("Toolbar_assembly").OutListRecursive if o.TypeId == "Part::Feature"]
    press = doc.getObject("Unit_1_press_arm")
    pw = [o for o in press.OutListRecursive if o.TypeId == "Part::Feature"] if press else []
    pw_names = {o.Name for o in pw}
    arm = [o for o in doc.getObject("Unit_1_arm").OutListRecursive
           if o.TypeId == "Part::Feature" and o.Name not in pw_names]
    m_all, c_all = _sum(feats)
    m_mov, c_mov = _sum(moving)
    m_arm, c_arm = _sum(arm)
    m_kit, c_kit = _sum(kit_parts)
    out = {"implement_kg": round(m_all, 1), "implement_cg": (round(c_all.y), round(c_all.z)),
           "pump_kit_kg_empty": round(m_kit + PUMP_KG, 1), "pump_kit_cg_y": round(c_kit.y),
           "moving_kg": round(m_mov, 1), "moving_cg_y": round(c_mov.y),
           "arm_kg": round(m_arm, 2), "arm_cg_y": round(c_arm.y)}
    if pw:
        m_pw, c_pw = _sum(pw)
        out.update({"pw_kg": round(m_pw, 2), "pw_cg": (round(c_pw.y), round(c_pw.z))})
    return out


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
    shape = G.box_span((-700.0, 700.0), (-1450.0, 1300.0), (-90.0, 0.0))
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
    out.append(save_view("6_unit_detail.png", (-1.0, 0.75, -0.45), target=(-400, -820, 200), height=1050))
    out.append(save_view("7_pump_kit.png", (-1.0, 0.9, -0.6), target=(-40, 250, 900), height=1100))
    out.append(save_view("13_v_discs_rear.png", (0.0, 1.0, 0.0), target=(0, -750, 150), height=430))
    out.append(save_view("14_v_discs_top.png", (0.0, 0.0, -1.0), target=(0, -760, 150), height=520, up=(0.0, 1.0, 0.0)))
    out.append(save_view("15_v_discs_iso_below.png", (-0.8, 0.9, 0.35), target=(0, -760, 60), height=520))
    out.append(save_view("16_la36_side.png", (-1.0, 0.0, 0.0), target=(0, -130, 600), height=560))
    out.append(save_view("17_la36_iso.png", (-1.0, 0.75, -0.55), target=(0, -130, 610), height=560))
    if P.press_wheel:
        out.append(save_view("12_press_wheel_detail.png", (-1.0, 0.55, -0.45), target=(-400, -1010, 160),
                             height=430))
    add_ground(doc)
    try:
        out.append(save_view("3_side_right.png", (-1.0, 0.0, 0.0), target=(0, -250, 500), height=1500))
        out.append(save_view("8_unit_side.png", (-1.0, 0.0, 0.0), target=(0, -830, 200), height=820))
    finally:
        remove_ground(doc)
    return out


def render_all():
    """Alle afbeeldingen: geheven + robotreferentie, daarna werkstand (die wordt opgeslagen)."""
    out = []
    doc = build(lift=P.lift_height, save_path=None, show_robot=True)
    add_ground(doc)
    try:
        out.append(save_view("9_lifted_side_with_robot.png", (-1.0, 0.0, 0.0), target=(0, -500, 420), height=1550))
    finally:
        remove_ground(doc)
    out.append(save_view("10_lifted_iso_with_robot.png", (-1.0, 1.0, -0.6)))
    doc = build(lift=0.0, save_path=None, show_robot=True)
    out.append(save_view("11_work_iso_with_robot.png", (1.0, -1.0, -0.65)))
    set_robot_reference(False, doc)
    out += render_work_previews(doc)
    doc.save() if doc.FileName else doc.saveAs(SAVE_PATH)
    return out


def export_step(doc=None, path=STEP_PATH):
    import Import
    doc = doc or App.getDocument(DOC_NAME)
    Import.export([doc.getObject("Applicator")], path)
    return path
