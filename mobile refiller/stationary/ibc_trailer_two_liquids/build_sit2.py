"""Model of the stationary refill station on the IBC trailer with two liquids (IBC 1 = A, IBC 2 = B).

Use in FreeCAD (via run_in_freecad.py):
    import build_sit2
    build_sit2.build()                     # saves FCStd and STEP (arm out to the left, 800 l in each IBC)
    build_sit2.set_arm(angle)              # 0 = out left, cfg()['fold'] = transport, -180 = out right
    build_sit2.set_levels(a=..., b=...)
    build_sit2.check_interference()        # must be empty
    build_sit2.check_fit()                 # arm from transport over the front to the right (must be empty)
    build_sit2.build_docked()              # scene: the precision applicator V4 stopped under the two nozzles
    build_sit2.check_docked()
    build_sit2.render_all()

The trailer itself (frame, running gear, drawbar, parking gear, lights) is ../ibc_trailer (sit_parts, cfg(2)); the
IBC, mast and arm come from ../stc_parts. Only what differs is in sit2_parts.
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

FOLDER = os.path.dirname(os.path.abspath(__file__))
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import sit2_params as P     # noqa: E402
import sit2_parts as S2     # noqa: E402
import sit_parts as T       # noqa: E402
import stc_params as C      # noqa: E402
import stc_parts as G       # noqa: E402
import stc_build as B       # noqa: E402

PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Stationary_IBC_Trailer_Two_Liquids"
DOCKED_DOC = DOC_NAME + "_refill"
ROOT = "Station"
DEFAULT_L = 800.0
CMB4 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(FOLDER))), "liquid fertilizer applicator",
                    "precision_applicator", "combined_v4")

B.COLOR.update({"liquid_A": (0.16, 0.42, 0.85), "liquid_B": (0.95, 0.50, 0.08), "hose_A": (0.12, 0.25, 0.55),
                "hose_B": (0.60, 0.30, 0.05)})


def spec():
    c = P.cfg()
    return c, S2.mast_specs(c)


# ---------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------
def build_ibc(doc, root, c, i, liq, litres):
    tag = "ibc%d" % (i + 1)
    grp = B.build_ibc(doc, root, tag, T.ibc_placement(c, i), litres, strap_axis="y", strap_z=12.0)
    grp.Label = "IBC_1000l_liquid_" + liq
    o = doc.getObject(tag + "_liquid")
    if o.ViewObject is not None:
        o.ViewObject.ShapeColor = B.COLOR["liquid_" + liq]
    return grp


def build_box(doc, parent, c):
    grp = B.new_part(doc, parent, "Control_box", "control_box_two_pumps", S2.box_placement(c))
    add = B.add_shape
    add(doc, grp, "box_rails", "box_mounting_rails", S2.box_rails(), "steel")
    add(doc, grp, "box_shell", "enclosure_steel_IP55_600x660x450", S2.box_shell(), "box")
    add(doc, grp, "box_roof", "rain_roof", S2.box_roof(), "box")
    add(doc, grp, "box_door", "door_with_lock", S2.box_door(), "door")
    base, knob = S2.estop()
    add(doc, grp, "box_estop_base", "emergency_stop_housing", base, "yellow")
    add(doc, grp, "box_estop", "emergency_stop_button", knob, "red")
    add(doc, grp, "box_glands", "cable_glands_and_4_bulkheads", S2.box_glands(), "black")
    for liq in P.LIQUIDS:
        t = liq.lower()
        add(doc, grp, "box_pump_" + t, "transfer_pump_24V_liquid_" + liq, S2.pump(liq), "pump")
        add(doc, grp, "box_pump_feet_" + t, "pump_feet_" + liq, S2.pump_feet(liq), "steel")
        add(doc, grp, "box_line_" + t, "discharge_line_" + liq, S2.discharge_line(liq), "pp")
        add(doc, grp, "box_flow_" + t, "flow_meter_" + liq, S2.flow_meter(liq), "black")
        add(doc, grp, "box_mvalve_" + t, "motorised_ball_valve_" + liq, S2.motor_valve(liq), "valve")
    add(doc, grp, "box_battery", "battery_LiFePO4_25.6V_50Ah", G.battery(), "battery")
    add(doc, grp, "box_din", "din_plate", G.din_plate(), "din")
    add(doc, grp, "box_modules", "controller_rtk_radio_dcdc", G.din_modules(), "pcb")
    return grp


def arm_placement(M, angle):
    return B.arm_placement(M, angle)


def lift_placement(lift):
    return App.Placement(V(0, 0, lift), App.Rotation())


def build_mast_arm(doc, parent, c, Ms, angle=0.0, lift=0.0):
    """Round mast with the actuator (fixed), Lift part (thrust collar + actuator rod, moves up) with the Arm part in
    it (sleeve, arm, drop pipes, nozzles, antenna, arm hoses; swings about the mast axis)."""
    M = Ms["B"]
    grp = B.new_part(doc, parent, "Mast", "lifting_mast_and_arm_two_nozzles")
    add = B.add_shape
    add(doc, grp, "mast", "mast_round_114x5", S2.mast_tube(c, M), "frame")
    add(doc, grp, "mast_base", "mast_foot_plate_12mm", S2.mast_base(c, M), "frame")
    add(doc, grp, "mast_gussets", "mast_gussets_10mm", S2.mast_gussets(c, M), "frame")
    add(doc, grp, "mast_clamps", "hose_clamps_on_mast", S2.mast_clamps(c, M), "steel")
    add(doc, grp, "mast_act_bracket", "actuator_clevis_bracket", S2.actuator_bracket(c, M), "steel")
    add(doc, grp, "mast_actuator", "linear_actuator_24V_stroke_706", S2.actuator_body(c, M), "black")
    br, g, a, r = G.beacon(M["x"], M["y"], P.fixed_top_z - 450.0, "+x", 2.0 * S2.mast_r())
    add(doc, grp, "beacon_bracket", "beacon_bracket", br, "steel")
    add(doc, grp, "beacon_green", "beacon_green_ready", g, "green")
    add(doc, grp, "beacon_amber", "beacon_amber_pumping", a, "amber")
    add(doc, grp, "beacon_red", "beacon_red_fault", r, "red")
    lg = B.new_part(doc, grp, "Lift", "lift_carriage", lift_placement(lift))
    add(doc, lg, "lift_collar", "thrust_collar_with_lug", S2.collar_lug(M), "steel")
    add(doc, lg, "lift_rod", "actuator_rod_D30", S2.actuator_rod(M), "zinc")
    arm = B.new_part(doc, lg, "Arm", "arm_swings_on_mast", arm_placement(M, angle))
    add(doc, arm, "arm_sleeve", "sleeve_D140_on_mast", S2.sleeve(M), "frame")
    add(doc, arm, "arm", "arm_60x60x3_two_nozzles", S2.arm_tube(Ms), "frame")
    add(doc, arm, "arm_tip_plates", "tip_plates", Part.makeCompound([G.tip_plate(Ms[k]) for k in P.LIQUIDS]), "frame")
    add(doc, arm, "arm_saddles", "hose_saddles", S2.arm_saddles(Ms), "frame")
    add(doc, arm, "arm_antenna", "rtk_antenna_between_nozzles", G.antenna(Ms["mid"]), "white")
    for liq in P.LIQUIDS:
        t = liq.lower()
        add(doc, arm, "arm_drop_" + t, "drop_pipe_PP50_" + liq, S2.drop_pipe(Ms[liq]), "pp")
        add(doc, arm, "arm_nozzle_" + t, "drip_stop_nozzle_" + liq, G.nozzle(Ms[liq]), "black")
        add(doc, arm, "arm_hose_" + t, "hose_along_arm_" + liq, S2.arm_hose(liq, Ms), "hose_" + liq)
    return grp


def build_into(doc, arm=0.0, litres=(DEFAULT_L, DEFAULT_L), placement=None, lift=0.0):
    c, Ms = spec()
    root = B.new_part(doc, None, ROOT, "stationary_refiller_ibc_trailer_two_liquids", placement)
    fr = B.new_part(doc, root, "Frame", "trailer_frame")
    add = B.add_shape
    add(doc, fr, "frame_side_rails", "side_rails_100x50x4", T.side_rails(c), "frame")
    add(doc, fr, "frame_end_rails", "front_and_rear_rail_100x50x4", S2.end_rails(c), "frame")
    add(doc, fr, "frame_cross", "cross_members_80x40x3", S2.cross_members(c), "frame")
    add(doc, fr, "frame_floor", "floor_plate_3mm", T.floor_plate(c), "deck")
    add(doc, fr, "frame_guides", "corner_guides_angle_50x5", T.corner_guides(c), "frame")
    add(doc, fr, "frame_a", "a_frame_drawbar_100x50x4", T.a_frame(c), "frame")
    add(doc, fr, "frame_box_cross", "box_cross_members_60x40x3", T.box_cross(c), "frame")
    add(doc, fr, "frame_mast_cross", "mast_cross_beam_100x100x4", T.mast_cross(c), "frame")
    add(doc, fr, "frame_eye", "tow_eye_40", T.tow_eye(c), "steel")
    rg = B.new_part(doc, root, "Running_gear", "running_gear")
    ax, plates = T.axle(c)
    add(doc, rg, "rg_axle", "axle_square_70_with_stubs", ax, "steel")
    add(doc, rg, "rg_plates", "axle_clamp_plates", plates, "steel")
    add(doc, rg, "rg_tyres", "tyres_" + c["tyre_size"], T.tyres(c), "tyre")
    add(doc, rg, "rg_rims", "rims", T.rims(c), "rim")
    add(doc, rg, "rg_guards", "mudguards", T.mudguards(c), "frame")
    pk = B.new_part(doc, root, "Parking", "parking_gear_and_lights")
    clamp, body, wheel = T.jockey(c)
    add(doc, pk, "park_jockey_clamp", "jockey_wheel_clamp", clamp, "frame")
    add(doc, pk, "park_jockey", "jockey_wheel_tube_and_crank", body, "steel")
    add(doc, pk, "park_jockey_wheel", "jockey_wheel_200", wheel, "tyre")
    sl, legs, pins = T.drop_legs(c)
    add(doc, pk, "park_leg_sleeves", "drop_leg_sleeves_60", sl, "frame")
    add(doc, pk, "park_legs", "drop_legs_50_with_feet", legs, "steel")
    add(doc, pk, "park_leg_pins", "drop_leg_pins", pins, "zinc")
    hs, ls, plate = T.rear_lights(c)
    add(doc, pk, "light_housings", "rear_light_clusters", hs, "black")
    add(doc, pk, "light_lenses", "rear_light_lenses", ls, "red")
    add(doc, pk, "light_plate", "number_plate", plate, "plate")
    for i, (liq, l) in enumerate(zip(P.LIQUIDS, litres)):
        build_ibc(doc, root, c, i, liq, l)
    build_box(doc, root, c)
    hz = B.new_part(doc, root, "Hoses", "hoses")
    for liq in P.LIQUIDS:
        t = liq.lower()
        add(doc, hz, "hose_suction_" + t, "suction_hose_1.5in_" + liq, S2.suction_hose(c, liq), "hose")
        add(doc, hz, "hose_discharge_" + t, "discharge_hose_up_mast_" + liq, S2.discharge_hose(c, liq, Ms[liq]),
            "hose_" + liq)
        add(doc, hz, "hose_loop_" + t, "slack_loop_to_lifting_arm_" + liq, S2.hose_loop(liq, Ms[liq], lift),
            "hose_" + liq)
    build_mast_arm(doc, root, c, Ms, arm, lift)
    return root, c, Ms


def build(arm=0.0, litres=(DEFAULT_L, DEFAULT_L), save=True, step=True):
    doc = B.new_doc(DOC_NAME, "Stationary refiller - IBC trailer, two liquids",
                    "Generated by build_sit2.py from sit2_params.py, ../ibc_trailer and ../stc_*.py. Trailer "
                    "coordinates: origin = middle of the axle on the ground, x = right, y = forward. "
                    "Arm: build_sit2.set_arm(angle).")
    build_into(doc, arm, litres)
    doc.recompute()
    base = os.path.join(FOLDER, DOC_NAME)
    if save:
        doc.saveAs(base + ".FCStd")
    if step:
        B.export_step(doc, ROOT, base + ".step")
    return doc


def active(doc=None):
    if doc is not None:
        return doc
    for n in (DOC_NAME, DOCKED_DOC):
        if n in App.listDocuments():
            return App.getDocument(n)
    raise RuntimeError("no two-liquid trailer document open")


def set_arm(angle, doc=None):
    doc = active(doc)
    doc.getObject("Arm").Placement = arm_placement(spec()[1]["B"], angle)
    doc.recompute()


def set_lift(lift, doc=None):
    """Arm height above its low position (0 = nozzles at 1460 for the working robot, P.lift_high for the refiller)."""
    doc = active(doc)
    c, Ms = spec()
    doc.getObject("Lift").Placement = lift_placement(lift)
    for liq in P.LIQUIDS:
        doc.getObject("hose_loop_" + liq.lower()).Shape = S2.hose_loop(liq, Ms[liq], lift)
    doc.recompute()


def set_levels(a=None, b=None, doc=None):
    doc = active(doc)
    for tag, l in (("ibc1", a), ("ibc2", b)):
        if l is not None:
            B.set_ibc_level(doc, tag, l)


# ---------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------
OK = B.pair_ok([
    ("frame_a", "frame_end_rails"), ("frame_a", "frame_side_rails"), ("frame_a", "frame_box_cross"),
    ("frame_a", "frame_mast_cross"), ("frame_a", "frame_eye"), ("frame_a", "park_jockey_clamp"),
    ("frame_side_rails", "park_leg_sleeves"), ("park_leg_sleeves", "park_leg_pins"), ("park_legs", "park_leg_pins"),
    ("rg_axle", "rg_plates"), ("rg_axle", "rg_rims"), ("rg_tyres", "rg_rims"), ("rg_plates", "frame_side_rails"),
    ("rg_guards", "frame_side_rails"), ("mast_base", "frame_mast_cross"), ("mast_base", "mast"),
    ("mast_gussets", "mast"), ("mast_gussets", "mast_base"), ("park_jockey_clamp", "park_jockey"),
    ("light_housings", "frame_end_rails"), ("light_plate", "frame_end_rails"),
    ("box_estop_base", "box_door"), ("box_estop", "box_estop_base"), ("beacon_bracket", "mast"),
    ("beacon_bracket", "beacon_green"), ("mast_clamps", "mast"), ("arm_tip_plates", "arm"),
    ("arm_saddles", "arm"), ("arm_antenna", "arm"), ("arm", "arm_sleeve"), ("arm_sleeve", "lift_collar"),
    ("mast_act_bracket", "mast"), ("mast_act_bracket", "mast_actuator"), ("lift_rod", "mast_actuator"),
    ("lift_rod", "lift_collar")] +
    [p for t in "ab" for p in [
        ("box_pump_" + t, "box_glands"), ("box_line_" + t, "box_glands"), ("box_line_" + t, "box_flow_" + t),
        ("box_line_" + t, "box_mvalve_" + t), ("box_line_" + t, "box_pump_" + t),
        ("box_pump_feet_" + t, "box_pump_" + t), ("hose_suction_" + t, "box_pump_" + t),
        ("hose_suction_" + t, "box_glands"), ("hose_discharge_" + t, "box_line_" + t),
        ("hose_discharge_" + t, "box_glands"), ("hose_discharge_" + t, "mast_clamps"),
        ("hose_loop_" + t, "hose_discharge_" + t), ("arm_hose_" + t, "hose_loop_" + t),
        ("arm_hose_" + t, "arm_drop_" + t), ("arm_hose_" + t, "arm_saddles"), ("arm_drop_" + t, "arm_tip_plates"),
        ("arm_drop_" + t, "arm"), ("arm_nozzle_" + t, "arm_drop_" + t)]] +
    [(t + "_camlock", t + "_valve") for t in ("ibc1", "ibc2")] +
    [("hose_suction_a", "ibc1_camlock"), ("hose_suction_b", "ibc2_camlock")])


def check_interference(doc=None, tol=1.0):
    return B.check_interference(active(doc), ROOT, OK, tol)


def check_fit(doc=None, tol=1.0):
    """Arm from the transport lock over the left and the front to the right. Contacts of the flexible hose loop over
    the pivot with the mast top are not counted when the arm is swung (the loop is drawn rigid, as with the arm out
    to the left)."""
    doc = active(doc)
    c, Ms = spec()
    angles = sorted(set(list(range(-180, int(c["fold"]) + 1, 30)) + [c["fold"]]))
    out = B.check_fit(doc, ROOT, Ms["B"], OK, angles, tol)
    if isinstance(out, dict):
        clean = {}
        for a, hits in out.items():
            clean[a] = [h for h in hits if not (float(a) != 0.0 and (_loop(h) or _slack(h)))]
        return clean
    return [h for h in out if not _loop(h)]


def _slack(h):
    """The slack loop is redrawn for the lift, not for the swing (its top end turns with the arm): contacts of the
    loop with the swung arm are not counted."""
    return any("slack_loop" in str(x) for x in h[:2])


def _loop(h):
    """The hose from the slack loop onto the arm is flexible: when the arm swings, it twists round the mast."""
    labels = (str(h[0]), str(h[1]))
    return any("hose_along_arm" in s for s in labels) and any(
        k in s for s in labels for k in ("mast", "hose_clamps", "slack_loop", "hose_along_arm", "beacon", "actuator"))


def clearance(doc=None):
    doc = active(doc)
    c, Ms = spec()
    objs = B.kit_objects(doc, ROOT)
    bb = B.bbox(doc, objs)
    return {"size": (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), "reach_mid": c["reach"],
            "reach_A": c["reach_A"], "reach_B": c["reach_B"], "nozzle_tip_z": P.nozzle_tip_z,
            "deck_z": c["deck_z"], "mast_y": c["mast_y"], "box_y": c["box_y"],
            "antenna_top_z": G.antenna_top(Ms["mid"]), "transport_angle": round(c["fold"], 1)}


def mass_properties(doc=None):
    doc = active(doc)
    groups = {"trailer": lambda o: o.Name.startswith(("frame_", "rg_", "park_", "light_")),
              "box": lambda o: o.Name.startswith("box_"),
              "mast": lambda o: o.Name.startswith(("mast", "arm", "beacon", "lift")),
              "hoses": lambda o: o.Name.startswith("hose_"),
              "ibc_empty": B.is_ibc, "liquid": B.is_liquid}
    fixed = {"rg_tyres": 2 * 38.0, "rg_rims": 2 * 16.0, "park_jockey_wheel": 2.0, "light_lenses": 0.3,
             "light_housings": 1.6}
    density = {"light_plate": 1.4e-6}
    density.update({"hose_%s_%s" % (k, t): B.HOSE for k in ("suction", "discharge", "loop") for t in "ab"})
    return B.mass_groups(doc, ROOT, groups, fixed, density)


# ---------------------------------------------------------------------
# Refill scene: the precision applicator V4 with both funnels under the nozzles
# ---------------------------------------------------------------------
def load_cmb4():
    if CMB4 not in sys.path:
        sys.path.insert(0, CMB4)
    import build_cmb4
    build_cmb4.setup_path()
    return build_cmb4


def worker_placement(angle=0.0, heading=0.0, funnel_y=None):
    """Working robot (heading 0 = +y, same as the trailer) with funnel A under nozzle A and B under B (arm at angle).
    The working robot's centre line lies under the middle of the two nozzles."""
    c, Ms = spec()
    M = Ms["mid"]
    a = math.radians(angle)
    mx = M["x"] - M["reach"] * math.cos(a)
    my = M["y"] - M["reach"] * math.sin(a)
    rot = App.Rotation(V(0, 0, 1), heading)
    f = rot.multVec(V(0.0, P.funnel_y if funnel_y is None else funnel_y, 0))
    return App.Placement(V(mx - f.x, my - f.y, 0), rot)


MRD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "simple_two_ibc")
REFILLER_DOC = DOC_NAME + "_refills_refiller"


def load_mrd():
    if MRD_FOLDER not in sys.path:
        sys.path.insert(0, MRD_FOLDER)
    import build_mrd
    return build_mrd


def refiller_placement(angle=0.0):
    """Mobile refiller with two IBCs beside the trailer, same heading, its fill funnels (y -70, x +-227.5) under the
    nozzles of the lifted arm."""
    BD = load_mrd()
    return worker_placement(angle, 0.0, BD.P.fill_y)


def build_docked_refiller(litres=(DEFAULT_L, DEFAULT_L), refiller_l=(150.0, 150.0)):
    """Scene: the arm lifted, the mobile refiller with two IBCs stopped beside the trailer, both fill funnels under
    the nozzles."""
    doc = B.new_doc(REFILLER_DOC, "IBC trailer two liquids - refills the mobile refiller",
                    "Generated by build_sit2.build_docked_refiller(): arm lifted, refiller funnels under the nozzles.")
    build_into(doc, 0.0, litres, lift=P.lift_high)
    BD = load_mrd()
    robot, objs = BD.build_robot(doc, "mobile_refiller_two_ibc", refiller_placement())
    BD.build_refiller_into(doc, robot, 0.0, refiller_l)
    doc.recompute()
    return doc


def check_docked_refiller(doc=None, tol=1.0):
    """Station against the mobile refiller (robot + kit). Must be empty."""
    doc = doc or App.getDocument(REFILLER_DOC)
    return B.check_docked(doc, ROOT, "Robot", OK, tol)


def nozzles_over_refiller_funnels():
    c, Ms = spec()
    BD = load_mrd()
    pl = refiller_placement()
    out = {}
    for liq in P.LIQUIDS:
        f = pl.multVec(V(BD.P.fill_x[liq], BD.P.fill_y, 0))
        nx, ny = G.nozzle_xy(Ms[liq])
        out[liq] = round(math.hypot(f.x - nx, f.y - ny), 2)
    out["tip_above_rim"] = P.nozzle_tip_z + P.lift_high - BD.P.FILL_RIM_Z
    return out


def build_docked(litres=(DEFAULT_L, DEFAULT_L), rx=(20.0, 20.0), lift=150.0):
    doc = B.new_doc(DOCKED_DOC, "IBC trailer two liquids - refill",
                    "Generated by build_sit2.build_docked(): precision applicator V4 under the two nozzles.")
    build_into(doc, 0.0, litres)
    B4 = load_cmb4()
    B4.build_into(doc, lift, litres=rx, placement=worker_placement())
    doc.recompute()
    return doc


def check_docked(doc=None, tol=1.0):
    doc = doc or App.getDocument(DOCKED_DOC)
    return B.check_docked(doc, ROOT, "Robot", OK, tol)


def nozzles_over_funnels():
    c, Ms = spec()
    pl = worker_placement()
    out = {}
    for liq in P.LIQUIDS:
        fx = (P.funnel_pitch / 2.0) * (1 if liq == "A" else -1)
        f = pl.multVec(V(fx, P.funnel_y, 0))
        nx, ny = G.nozzle_xy(Ms[liq])
        out[liq] = round(math.hypot(f.x - nx, f.y - ny), 2)
    out["tip_above_rim"] = P.nozzle_tip_z - P.funnel_rim_z
    return out


# ---------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------
def render_all():
    import FreeCADGui as Gui
    out = []
    doc = build(save=False, step=False)
    c, Ms = spec()
    cy = 0.5 * (c["deck_rear"] + c["eye_y"])
    B.add_floor(doc, (-3000.0, 1600.0), (c["deck_rear"] - 800.0, c["eye_y"] + 1200.0))
    out.append(B.save_view(PREVIEW_DIR, "1_iso_two_liquids.png", (1.0, -1.0, -0.7), (-500, cy, 900), height=5000))
    out.append(B.save_view(PREVIEW_DIR, "2_side.png", (1.0, 0.0, 0.0), (0, cy, 1000), height=3300))
    arm = [o.Name for o in B.kit_objects(doc, ROOT) if B.in_arm(o)]
    B.set_visible(doc, B.BOX_COVER, False)
    out.append(B.save_view(PREVIEW_DIR, "3_control_box_two_pumps.png", (1.0, -0.35, -0.6),
                           (P.box_x - 150.0, c["box_y"], c["box_z"] + 250), height=1500))
    B.set_visible(doc, B.BOX_COVER, True)
    out.append(B.save_view(PREVIEW_DIR, "4_mast_hoses_arm.png", (0.6, -1.0, -0.45), (-650.0, c["mast_y"], 1750.0),
                           height=1900))
    ibc = [o.Name for o in B.kit_objects(doc, ROOT) if o.Name.startswith("ibc")]
    B.set_visible(doc, ibc + ["frame_floor"], False)
    out.append(B.save_view(PREVIEW_DIR, "5_suction_lines_under_floor.png", (0.9, -0.7, 0.6), (-100.0, cy - 500, 500),
                           height=3800))
    B.set_visible(doc, ibc + ["frame_floor"], True)
    set_arm(c["fold"], doc)
    out.append(B.save_view(PREVIEW_DIR, "6_transport.png", (0.8, -1.0, -0.6), (0, cy, 900), height=4800))
    App.closeDocument(doc.Name)
    doc = build_docked()
    Gui.updateGui()
    B.add_floor(doc, (-3800.0, 1600.0), (c["deck_rear"] - 1600.0, c["eye_y"] + 1200.0))
    out.append(B.save_view(PREVIEW_DIR, "7_refill_iso.png", (1.0, -0.8, -0.6), (-1000, cy, 700), height=5200))
    out.append(B.save_view(PREVIEW_DIR, "8_refill_top.png", (0.0, 0.0, -1.0), (-1000, cy - 300, 0), height=6600,
                           up=(0.0, 1.0, 0.0)))
    out.append(B.save_view(PREVIEW_DIR, "9_nozzles_over_funnels.png", (0.3, -1.0, -0.35),
                           (-c["reach"], c["mast_y"], 1450), height=1300))
    App.closeDocument(doc.Name)
    doc = build_docked_refiller()
    Gui.updateGui()
    B.add_floor(doc, (-3800.0, 1600.0), (c["deck_rear"] - 1600.0, c["eye_y"] + 1200.0))
    out.append(B.save_view(PREVIEW_DIR, "10_refills_refiller_iso.png", (1.0, -0.8, -0.6), (-1000, cy, 1000),
                           height=5400))
    out.append(B.save_view(PREVIEW_DIR, "11_lifted_nozzles_over_refiller.png", (0.3, -1.0, -0.3),
                           (-c["reach"], c["mast_y"], 2150), height=1500))
    App.closeDocument(doc.Name)
    build()
    return out
