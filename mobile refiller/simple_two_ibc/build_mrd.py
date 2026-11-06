"""Model of the mobile refiller with two IBCs (two liquids) on a lengthened Bruut OpenAgbot.

Use in FreeCAD (via run_in_freecad.py, or with this folder on sys.path):
    import build_mrd
    build_mrd.build()                          # saves FCStd and STEP (arm out, 500 l in each IBC)
    build_mrd.set_arm(90)                      # arm folded backwards for transport (0 = out to the left)
    build_mrd.set_levels(a=500, b=300)         # litres per IBC
    build_mrd.check_interference()             # overlap in the current pose (must be empty)
    build_mrd.check_fit()                      # arm 0 .. 90 deg (must be empty)
    build_mrd.build_docked()                   # scene: the precision applicator V4 stopped under the two nozzles
    build_mrd.check_docked()                   # refiller against the working robot (must be empty)
    build_mrd.render_all()

Tree: Robot (lengthened robot: wheelbase 2200, upper beams 2500)
        Mobile_refiller_2ibc
          MRD_frame        bed cross tubes, side rails, bolts, corner guides, lashing eyes, outrigger, gussets, mast,
                           top plate, pivot pin, hose clamps
          MRD_ibc_A/B      IBC 1000 l (+ liquid), straps
          MRD_pump_A/B     pump under each IBC, cradle, camlock elbow, suction hose, fixed discharge hose
          MRD_arm          arm, lock pin, 2 tip plates, 2 drop pipes, 2 nozzles, RTK antenna, the two arm hoses
"""
import math
import os
import re
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

FOLDER = os.path.dirname(os.path.abspath(__file__))
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mrd_params as P      # noqa: E402
import mrd_parts as G       # noqa: E402
import mrd_calc as C        # noqa: E402
import mrs_params as S      # noqa: E402
import build_mrs as BM      # noqa: E402

PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Mobile_Refiller_Two_IBC"
DOCKED_DOC = "Mobile_Refiller_Two_IBC_refill"
SAVE_BASE = os.path.join(FOLDER, DOC_NAME)
ROOT = "Mobile_refiller_2ibc"
DEFAULT_L = 500.0

COLOR = dict(BM.COLOR)
COLOR.update({"liquid_A": (0.16, 0.42, 0.85), "liquid_B": (0.95, 0.50, 0.08), "hose_A": (0.12, 0.25, 0.55),
              "hose_B": (0.45, 0.20, 0.03), "funnel_A": (0.16, 0.42, 0.85), "funnel_B": (0.93, 0.50, 0.08)})
TRANSPARENT = dict(BM.TRANSPARENT)


def new_part(doc, parent, name, label, placement=None):
    return BM.new_part(doc, parent, name, label, placement)


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
        elif color.startswith("liquid"):
            view.Transparency = 0
    return obj


def base_name(name):
    return re.sub(r"\d{3}$", "", name)


# ---------------------------------------------------------------------
# Lengthened robot: agbots/agbot design with a few parameters changed while it is built
# ---------------------------------------------------------------------
def build_robot(doc, label="Bruut_OpenAgbot_long_robot", placement=None):
    BA = BM.load_agbot()
    import agbot_params as AP
    keys = list(P.ROBOT_OVERRIDE) + ["stappen_y", "align_length"]
    saved = {k: getattr(AP, k) for k in keys}
    try:
        for k, v in P.ROBOT_OVERRIDE.items():
            setattr(AP, k, v)
        AP.stappen_y = AP._round_half_up((AP.chassis_length - AP.chassis_length_min) / (2 * AP.grid_step))
        AP.align_length = AP.chassis_length_min + AP.stappen_y * 2 * AP.grid_step
        before = {o.Name for o in doc.Objects}
        robot = BA.new_part(doc, None, "Robot", label)
        BA.build_chassis(doc, robot)
        shapes = BA.make_shapes()
        for tag in ("RL", "RR", "FL", "FR"):
            BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    finally:
        for k, v in saved.items():
            setattr(AP, k, v)
    if placement is not None:
        robot.Placement = placement
    objs = {base_name(o.Name): o for o in doc.Objects if o.Name not in before}
    BM.hide_robot_gnss(objs)
    return robot, objs


# ---------------------------------------------------------------------
# Refiller kit
# ---------------------------------------------------------------------
REF = {"arm": 0.0}


def arm_placement(angle=None):
    angle = REF["arm"] if angle is None else angle
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle), V(G.MX, G.MY, 0))


def liquid_shape(liq, litres):
    s = BM.liquid_shape("ibc", litres).copy()
    if not s.isNull():
        s.translate(V(0, P.ibc_dy[liq], 0))
    return s


def build_refiller_into(doc, parent=None, arm=None, litres=(DEFAULT_L, DEFAULT_L)):
    root = new_part(doc, parent, ROOT, "mobile_refiller_two_ibc")
    fr = new_part(doc, root, "MRD_frame", "bed_mast_lengthened")
    add_shape(doc, fr, "mrd_cross", "bed_cross_tubes_60x40x3", G.bed_cross_tubes(), "frame")
    add_shape(doc, fr, "mrd_rails", "bed_side_rails_60x40x3", G.bed_side_rails(), "frame")
    add_shape(doc, fr, "mrd_bolts", "bed_bolts_M10", G.bed_bolts(), "zinc")
    add_shape(doc, fr, "mrd_guides", "corner_guides_angle_50x5", G.corner_guides(), "frame")
    add_shape(doc, fr, "mrd_eyes", "lashing_eyes", G.lashing_eyes(), "frame")
    add_shape(doc, fr, "mrd_outrigger", "mast_outrigger_80x40x3", G.mast_outrigger(), "frame")
    add_shape(doc, fr, "mrd_gussets", "mast_gussets_10mm", G.mast_gussets(), "frame")
    add_shape(doc, fr, "mrd_mast", "mast_80x80x4", G.mast(), "frame")
    add_shape(doc, fr, "mrd_top_plate", "mast_top_plate_10mm", G.mast_top_plate(), "frame")
    add_shape(doc, fr, "mrd_pivot_pin", "pivot_pin_D30", G.pivot_pin(), "zinc")
    add_shape(doc, fr, "mrd_clamps", "hose_clamps_on_mast", G.mast_clamps(), "steel")
    for liq, l in zip(P.LIQUIDS, litres):
        t = liq.lower()
        ig = new_part(doc, root, "MRD_ibc_" + liq, "IBC_1000l_liquid_" + liq)
        I = G.ibc(liq)
        add_shape(doc, ig, "ibc%s_pallet" % t, "ibc_%s_pallet" % liq, I["pallet"], "pallet")
        add_shape(doc, ig, "ibc%s_bottle" % t, "ibc_%s_bottle" % liq, I["bottle"], "bottle")
        add_shape(doc, ig, "ibc%s_liquid" % t, "ibc_%s_liquid" % liq, liquid_shape(liq, l), "liquid_" + liq)
        add_shape(doc, ig, "ibc%s_cage" % t, "ibc_%s_cage" % liq, I["cage"], "galv")
        add_shape(doc, ig, "ibc%s_valve" % t, "ibc_%s_valve_DN50" % liq, I["valve"], "black")
        add_shape(doc, ig, "ibc%s_cap" % t, "ibc_%s_cap" % liq, I["cap"], "white")
        st, ra = G.ibc_straps(liq)
        add_shape(doc, ig, "ibc%s_straps" % t, "ibc_%s_ratchet_straps" % liq, st, "strap")
        add_shape(doc, ig, "ibc%s_ratchets" % t, "ibc_%s_ratchets" % liq, ra, "steel")
        pg = new_part(doc, root, "MRD_pump_" + liq, "pump_liquid_" + liq)
        U = G.pump(liq)
        add_shape(doc, pg, "pump%s" % t, "transfer_pump_24V_liquid_" + liq, U["pump"], "pump")
        add_shape(doc, pg, "pump%s_cradle" % t, "pump_cradle_" + liq, U["cradle"], "frame")
        add_shape(doc, pg, "pump%s_camlock" % t, "camlock_elbow_" + liq, U["camlock"], "camlock")
        add_shape(doc, pg, "pump%s_suction" % t, "suction_hose_" + liq, U["suction"], "hose")
        add_shape(doc, pg, "hose%s_fixed" % t, "discharge_hose_up_mast_" + liq, G.hose_fixed(liq), "hose_" + liq)
    fg = new_part(doc, root, "MRD_fill", "fill_bridge_two_funnels")
    add_shape(doc, fg, "fill_bridge", "fill_bridge_plate", G.bridge_plate(), "frame")
    for liq in P.LIQUIDS:
        t = liq.lower()
        add_shape(doc, fg, "fill_funnel_" + t, "fill_funnel_200_" + liq, G.fill_funnel(liq), "funnel_" + liq)
        add_shape(doc, fg, "fill_support_" + t, "funnel_support_" + liq, G.fill_support(liq), "steel")
        add_shape(doc, fg, "fill_pipe_" + t, "fill_pipe_PP50_" + liq, G.fill_pipe(liq), "pp")
        add_shape(doc, fg, "fill_fitting_" + t, "bulkhead_fitting_DN50_" + liq, G.fill_fitting(liq), "black")
    ag = new_part(doc, root, "MRD_arm", "arm_two_nozzles", arm_placement(REF["arm"] if arm is None else arm))
    add_shape(doc, ag, "mrd_arm", "arm_60x60x3_two_nozzles", G.arm(), "frame")
    add_shape(doc, ag, "mrd_lock_pin", "lock_pin_D12", G.lock_pin(), "zinc")
    add_shape(doc, ag, "mrd_tip_plates", "tip_plates", G.tip_plates(), "frame")
    add_shape(doc, ag, "mrd_saddles", "hose_saddles", G.arm_saddles(), "frame")
    add_shape(doc, ag, "mrd_antenna", "rtk_antenna_between_nozzles", G.antenna(), "white")
    for liq in P.LIQUIDS:
        t = liq.lower()
        add_shape(doc, ag, "drop%s" % t, "drop_pipe_PP50_" + liq, G.drop_pipe(liq), "pp")
        add_shape(doc, ag, "nozzle%s" % t, "drip_stop_nozzle_" + liq, G.nozzle(liq), "black")
        add_shape(doc, ag, "hose%s_arm" % t, "hose_along_arm_" + liq, G.hose_arm(liq), "hose_" + liq)
    return root


def build(arm=None, litres=(DEFAULT_L, DEFAULT_L), save=True, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Mobile refiller with two IBCs"
    doc.Comment = ("Generated by build_mrd.py from mrd_params.py. Lengthened Bruut (wheelbase 2200). Robot "
                   "coordinates. Arm: build_mrd.set_arm(angle); levels: set_levels(a=, b=).")
    robot, objs = build_robot(doc)
    build_refiller_into(doc, robot, arm, litres)
    doc.recompute()
    if save:
        doc.saveAs(SAVE_BASE + ".FCStd")
    if step:
        export_step(doc, SAVE_BASE + ".step")
    return doc


def active_doc(doc=None):
    if doc is not None:
        return doc
    for n in (DOC_NAME, DOCKED_DOC):
        if n in App.listDocuments():
            return App.getDocument(n)
    raise RuntimeError("no two-IBC refiller document open")


def set_arm(angle, doc=None):
    doc = active_doc(doc)
    doc.getObject("MRD_arm").Placement = arm_placement(angle)
    doc.recompute()


def set_levels(a=None, b=None, doc=None):
    doc = active_doc(doc)
    for liq, l in (("A", a), ("B", b)):
        if l is not None:
            doc.getObject("ibc%s_liquid" % liq.lower()).Shape = liquid_shape(liq, l)


def kit_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


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
PAIRS_OK = {frozenset(p) for p in [
    ("mrd_cross", "mrd_rails"), ("mrd_cross", "mrd_bolts"), ("mrd_outrigger", "mrd_rails"),
    ("mrd_outrigger", "mrd_cross"), ("mrd_gussets", "mrd_rails"), ("mrd_gussets", "mrd_outrigger"),
    ("mrd_gussets", "mrd_mast"), ("mrd_mast", "mrd_outrigger"), ("mrd_top_plate", "mrd_mast"),
    ("mrd_pivot_pin", "mrd_top_plate"), ("mrd_pivot_pin", "mrd_arm"), ("mrd_lock_pin", "mrd_top_plate"),
    ("mrd_lock_pin", "mrd_arm"), ("mrd_guides", "mrd_rails"), ("mrd_eyes", "mrd_rails"), ("mrd_clamps", "mrd_mast"),
    ("mrd_tip_plates", "mrd_arm"), ("mrd_saddles", "mrd_arm"), ("mrd_antenna", "mrd_arm")] +
    [p for t in "ab" for p in [
        ("ibc%s_pallet" % t, "mrd_cross"), ("ibc%s_pallet" % t, "mrd_rails"),
        ("pump%s_suction" % t, "pump%s_camlock" % t), ("pump%s_suction" % t, "pump%s" % t),
        ("hose%s_fixed" % t, "pump%s" % t), ("pump%s_camlock" % t, "ibc%s_valve" % t),
        ("pump%s_cradle" % t, "mrd_cross"), ("pump%s_cradle" % t, "pump%s" % t),
        ("hose%s_fixed" % t, "mrd_clamps"), ("hose%s_arm" % t, "hose%s_fixed" % t),
        ("hose%s_arm" % t, "drop%s" % t), ("hose%s_arm" % t, "mrd_saddles"),
        ("drop%s" % t, "mrd_tip_plates"), ("nozzle%s" % t, "drop%s" % t), ("drop%s" % t, "mrd_arm"),
        ("ibc%s_straps" % t, "ibc%s_cage" % t), ("ibc%s_straps" % t, "mrd_rails"),
        ("ibc%s_ratchets" % t, "ibc%s_straps" % t), ("ibc%s_straps" % t, "mrd_eyes"),
        ("ibc%s_cage" % t, "ibc%s_pallet" % t), ("ibc%s_bottle" % t, "ibc%s_pallet" % t),
        ("ibc%s_valve" % t, "ibc%s_bottle" % t), ("ibc%s_valve" % t, "ibc%s_cage" % t),
        ("ibc%s_cap" % t, "ibc%s_bottle" % t), ("ibc%s_cap" % t, "ibc%s_cage" % t),
        ("ibc%s_bottle" % t, "ibc%s_cage" % t)]] +
    # the hose loop over the pivot is flexible (drawn rigid)
    [p for t in "ab" for p in [
        ("fill_support_" + t, "fill_bridge"), ("fill_support_" + t, "fill_funnel_" + t),
        ("fill_pipe_" + t, "fill_funnel_" + t), ("fill_pipe_" + t, "fill_fitting_" + t),
        ("fill_fitting_" + t, "ibc%s_bottle" % t), ("fill_pipe_" + t, "ibc%s_bottle" % t),
        ("fill_bridge", "ibc%s_cage" % t)]] +
    [("hosea_arm", "hoseb_fixed"), ("hoseb_arm", "hosea_fixed")]}
SKIP = ("ibca_liquid", "ibcb_liquid")
LOOP_OK = ("mast_", "hose_clamps", "discharge_hose", "pivot_pin", "hose_along_arm")


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


ROLLING = ("tire", "rim", "hub")


def check_interference(doc=None, tol=1.0):
    """Kit against itself and against the robot (tyres, rims, hubs by bounding box: the lug profile is slow)."""
    doc = active_doc(doc)
    kit = [(o, global_shape(o)) for o in _checked(kit_objects(doc))]
    names = {o.Name for o, _ in kit}
    robot = [o for o in doc.getObject("Robot").OutListRecursive if o.TypeId == "Part::Feature"
             and o.Name not in names and o.ViewObject.Visibility]
    hits = _overlaps([(kit[i], kit[j]) for i in range(len(kit)) for j in range(i + 1, len(kit))], tol)
    for o in robot:
        s = global_shape(o)
        for ok_, sk in kit:
            if not s.BoundBox.intersect(sk.BoundBox):
                continue
            if base_name(o.Name).rsplit("_", 1)[-1] in ROLLING:
                hits.append((ok_.Label, o.Label, "bbox"))
                continue
            vol = s.common(sk).Volume
            if vol > tol:
                hits.append((ok_.Label, o.Label, round(vol, 1)))
    return hits


def check_fit(doc=None, angles=(0.0, 30.0, 60.0, 90.0), tol=1.0):
    """Arm (and its hoses) from out to folded against the fixed kit and the robot."""
    doc = active_doc(doc)
    arm = [o for o in doc.getObject("MRD_arm").OutListRecursive if o.TypeId == "Part::Feature"]
    arm_names = {o.Name for o in arm}
    rest = [o for o in _checked(kit_objects(doc)) if o.Name not in arm_names]
    rest += [o for o in doc.getObject("Robot").OutListRecursive if o.TypeId == "Part::Feature"
             and o.Name not in {x.Name for x in kit_objects(doc)} and o.ViewObject.Visibility
             and base_name(o.Name).rsplit("_", 1)[-1] not in ROLLING]
    keep = doc.getObject("MRD_arm").Placement
    out = {}
    try:
        for a in angles:
            doc.getObject("MRD_arm").Placement = arm_placement(a)
            doc.recompute()
            pairs = [((o, global_shape(o)), (r, global_shape(r))) for o in arm for r in rest]
            # the hose loop over the pivot is flexible (drawn rigid, as it hangs with the arm out): when the arm
            # folds, the loop bends around the mast top; those contacts are not counted
            hits = [h for h in _overlaps(pairs, tol)
                    if not (a > 0 and "hose_along_arm" in h[0] and h[1].startswith(LOOP_OK))]
            out[a] = hits
    finally:
        doc.getObject("MRD_arm").Placement = keep
        doc.recompute()
    return out


def clearance(doc=None):
    doc = active_doc(doc)
    bb = App.BoundBox()
    for o in kit_objects(doc):
        if not o.Shape.isNull():
            bb.add(global_shape(o).BoundBox)
    rb = App.BoundBox()
    for o in doc.getObject("Robot").OutListRecursive:
        if o.TypeId == "Part::Feature" and not o.Shape.isNull() and o.ViewObject.Visibility:
            rb.add(global_shape(o).BoundBox)
    bb.add(rb)
    front = [o for o in doc.getObject("Robot").OutListRecursive if o.TypeId == "Part::Feature"
             and base_name(o.Name).startswith(("FL_", "FR_")) and "stepper" in o.Name]
    ibc_a = global_shape(doc.getObject("ibca_cage"))
    return {"size_x_y_z": (round(bb.XLength), round(bb.YLength), round(bb.ZLength)),
            "ibc_to_front_stepper": round(min(ibc_a.distToShape(global_shape(f))[0] for f in front), 1)
            if front else None,
            "nozzle_xy": {k: G.nozzle_xy(k) for k in P.LIQUIDS}, "nozzle_tip_z": P.nozzle_tip_z,
            "nozzle_pitch": P.nozzle_x["A"] - P.nozzle_x["B"], "ibc_top_z": P.IBC_TOP,
            "antenna_top_z": G.SG.antenna_top(G.M["mid"])}


# ---------------------------------------------------------------------
# Refill scene: the precision applicator V4 stopped beside the refiller, funnels under the nozzles
# ---------------------------------------------------------------------
def load_cmb4():
    if P.CMB4 not in sys.path:
        sys.path.insert(0, P.CMB4)
    import build_cmb4
    build_cmb4.setup_path()
    return build_cmb4


def worker_placement():
    """Working robot on the left of the refiller, same heading; its funnels (y 170, x +-227.5) under the nozzles."""
    return App.Placement(V(-P.dock_d, G.MY - P.funnel_y, 0.0), App.Rotation())


def build_docked(lift=150.0, litres=(DEFAULT_L, DEFAULT_L), rx=(30.0, 30.0)):
    if DOCKED_DOC in App.listDocuments():
        App.closeDocument(DOCKED_DOC)
    doc = App.newDocument(DOCKED_DOC)
    doc.Label = "Mobile refiller with two IBCs - refill"
    B4 = load_cmb4()
    B4.build_into(doc, lift, litres=rx, placement=worker_placement())
    robot, objs = build_robot(doc, "refiller_robot_long")
    build_refiller_into(doc, robot, 0.0, litres)
    doc.recompute()
    return doc


def _wheel_envelope(shape):
    """Plain cylinder round a tyre, rim or hub (axis along x, both robots head +y in the scene): booleans with the
    lug profile take hours."""
    bb = shape.BoundBox
    r = 0.5 * max(bb.YLength, bb.ZLength)
    return Part.makeCylinder(r, bb.XLength, V(bb.XMin, bb.Center.y, bb.Center.z), V(1, 0, 0))


def check_docked(doc=None, tol=1.0):
    """Refiller (lengthened robot + kit) against the working robot with everything on it (booleans; tyres by bbox)."""
    doc = doc or App.getDocument(DOCKED_DOC)
    worker = [o for o in doc.getObject("Robot").OutListRecursive if o.TypeId == "Part::Feature"
              and not o.Shape.isNull() and not o.Name.startswith("tank_liquid")]
    ref = [o for o in doc.getObject("Robot001").OutListRecursive if o.TypeId == "Part::Feature"
           and not o.Shape.isNull() and base_name(o.Name) not in SKIP]
    ws = [(o, global_shape(o)) for o in worker]
    hits = []
    for o in ref:
        s = global_shape(o)
        for w, sw in ws:
            if not s.BoundBox.intersect(sw.BoundBox):
                continue
            a, b = s, sw
            if base_name(o.Name).rsplit("_", 1)[-1] in ROLLING:
                a = _wheel_envelope(s)
            if base_name(w.Name).rsplit("_", 1)[-1] in ROLLING:
                b = _wheel_envelope(sw)
            vol = a.common(b).Volume
            if vol > tol:
                hits.append((o.Label, w.Label, round(vol, 1)))
    return hits


def nozzles_over_funnels():
    """Horizontal offset nozzle - funnel axis (mm) per liquid, and the nozzle tip above the funnel rim."""
    pl = worker_placement()
    out = {}
    for liq in P.LIQUIDS:
        fx = (P.funnel_pitch / 2.0) * (1 if liq == "A" else -1)
        f = pl.multVec(V(fx, P.funnel_y, 0))
        nx, ny = G.nozzle_xy(liq)
        out[liq] = round(math.hypot(f.x - nx, f.y - ny), 2)
    out["tip_above_rim"] = P.nozzle_tip_z - P.funnel_rim_z
    return out


# ---------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------
def save_view(name, direction, target, height, up=(0.0, 0.0, 1.0), size=(1600, 1100)):
    import FreeCADGui as Gui
    from pivy import coin
    Gui.updateGui()
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    t = V(*target)
    eye = t - d * 9000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(t.x, t.y, t.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(30000.0)
    cam.height.setValue(height)
    Gui.updateGui()
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, name)
    view.saveImage(path, size[0], size[1], "White")
    return path


def render_all():
    import FreeCADGui as Gui
    doc = build(save=False, step=False)
    Gui.setActiveDocument(doc.Name)
    out = [save_view("1_iso_refiller_two_ibc.png", (1.0, -1.0, -0.7), (-300, -100, 1100), 3600),
           save_view("2_side.png", (1.0, 0.0, 0.0), (-300, -100, 1100), 3000),
           save_view("3_top.png", (0.0, 0.0, -1.0), (-500, -100, 0), 3600, up=(0.0, 1.0, 0.0)),
           save_view("4_mast_arm_hoses.png", (1.0, 0.8, -0.5), (-1050, -40, 1850), 1500),
           save_view("5_pumps_under_ibcs.png", (1.0, -0.5, 0.35), (-300, -100, 650), 3000)]
    for o in kit_objects(doc):
        if o.Name.startswith(("ibca", "ibcb")):
            o.ViewObject.Visibility = False
    out.append(save_view("6_bed_without_ibcs.png", (1.0, -1.0, -0.9), (-200, -100, 700), 3400))
    for o in kit_objects(doc):
        if o.Name.startswith(("ibca", "ibcb")):
            o.ViewObject.Visibility = True
    set_arm(P.arm_fold, doc)
    out.append(save_view("7_arm_folded_transport.png", (1.0, -1.0, -0.7), (-300, -300, 1100), 3800))
    App.closeDocument(doc.Name)
    doc = build_docked()
    Gui.setActiveDocument(doc.Name)
    out += [save_view("8_refill_iso.png", (1.0, -0.8, -0.55), (-800, -200, 900), 4400),
            save_view("9_refill_top.png", (0.0, 0.0, -1.0), (-750, -200, 0), 4200, up=(0.0, 1.0, 0.0)),
            save_view("10_nozzles_over_funnels.png", (0.25, 1.0, -0.35), (-1450, -70, 1400), 1300)]
    App.closeDocument(doc.Name)
    build()
    return out
