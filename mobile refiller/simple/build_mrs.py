"""Model of the mobile refiller, simple (IBC) on the Bruut OpenAgbot, and the receiver kit for the working robot.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_mrs
    build_mrs.build()                              # saves FCStd and STEP (arm out, IBC 800 l)
    build_mrs.set_arm(90)                          # arm folded backwards for transport (0 = out to the left)
    build_mrs.set_levels(ibc=600)                  # litres in the IBC
    build_mrs.check_interference()                 # overlap in the current pose (must be empty)
    build_mrs.check_fit()                          # arm 0 .. 90 deg (must be empty)
    build_mrs.clearance()                          # steering sweep, stepper motors, heights, width
    build_mrs.mass_properties()                    # masses and centres of gravity
    build_mrs.build_docked()                       # scene: working robot stopped under the nozzle in its U-turn
    build_mrs.render_all()                         # all images in previews/
"""
import math
import os
import re
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrs_params as P
import mrs_parts as G
import mrs_calc as C

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
ROOT = os.path.dirname(os.path.dirname(FOLDER))
AGBOT_FOLDER = os.path.join(ROOT, "agbots", "agbot design")
AGBOT_MODULES = ("agbot_params", "agbot_parts", "build_agbot")
LFA_FOLDER = os.path.join(ROOT, "liquid fertilizer applicator", "advanced")
DOC_NAME = "Mobile_Refiller_Simple"
DOCKED_DOC = "Mobile_Refiller_Simple_refill"
SAVE_BASE = os.path.join(FOLDER, "Mobile_Refiller_Simple")
ROBOT_GNSS = ("gnss_dome", "gnss_mount")    # the robot's own antenna: moved to the arm tip (hidden on the refiller)

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "galv": (0.70, 0.72, 0.74),
    "motor": (0.08, 0.08, 0.08),
    "pump": (0.10, 0.35, 0.65),
    "bottle": (0.95, 0.95, 0.92),
    "pallet": (0.15, 0.15, 0.16),
    "tank": (0.93, 0.93, 0.88),
    "liquid": (0.15, 0.50, 0.80),
    "hose": (0.12, 0.12, 0.13),
    "rubber": (0.10, 0.10, 0.10),
    "valve": (0.85, 0.20, 0.15),
    "pp": (0.20, 0.22, 0.25),
    "white": (0.96, 0.96, 0.95),
    "black": (0.03, 0.03, 0.03),
    "yellow": (0.95, 0.75, 0.10),
    "strap": (0.95, 0.55, 0.05),
    "camlock": (0.80, 0.62, 0.25),
    "funnel": (0.95, 0.75, 0.10),
}
TRANSPARENT = {"bottle": 55, "tank": 75, "liquid": 0}


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
    obj.Shape = shape if shape is not None else Part.Shape()
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
        if color in TRANSPARENT:
            view.Transparency = TRANSPARENT[color]
    return obj


def base_name(name):
    """Object name without the number FreeCAD adds when a name is taken (RL_tire001 -> RL_tire)."""
    return re.sub(r"\d{3}$", "", name)


# ---------------------------------------------------------------------
# Pose of the arm and liquid levels
# ---------------------------------------------------------------------
REF = {"arm": 0.0}


def arm_placement(angle=None):
    angle = REF["arm"] if angle is None else angle
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle), V(G.MX, G.MY, 0))


def set_arm(angle, doc=None):
    doc = active_doc(doc)
    doc.getObject("MRS_arm").Placement = arm_placement(angle)
    doc.recompute()


def level_for(kind, litres):
    return C.level_for(kind, litres)


INNER = {}


def inner_shape(kind):
    if kind not in INNER:
        INNER[kind] = {"ibc": G.bottle_inner, "receiver": G.rx_tank_inner}[kind]()
    return INNER[kind]


_liq = {}


def liquid_shape(kind, litres):
    key = (kind, round(litres * 2.0) / 2.0)
    if key not in _liq:
        s = G.liquid(inner_shape(kind), level_for(kind, key[1]))
        _liq[key] = s if s is not None else Part.Shape()
    return _liq[key]


LIQUID_OBJ = {"ibc": "ibc_liquid", "receiver": "rx_liquid"}


def set_levels(ibc=None, receiver=None, doc=None, objs=None):
    for kind, litres in (("ibc", ibc), ("receiver", receiver)):
        if litres is None:
            continue
        o = objs.get(LIQUID_OBJ[kind]) if objs is not None else (doc or App.ActiveDocument).getObject(LIQUID_OBJ[kind])
        if o is not None:
            o.Shape = liquid_shape(kind, litres)


# ---------------------------------------------------------------------
# Robot (read only, from agbots/agbot design)
# ---------------------------------------------------------------------
def load_agbot():
    if AGBOT_FOLDER in sys.path:
        sys.path.remove(AGBOT_FOLDER)
    sys.path.insert(0, AGBOT_FOLDER)
    for name in AGBOT_MODULES:
        mod = sys.modules.get(name)
        if mod is not None and os.path.dirname(os.path.abspath(mod.__file__)) != os.path.abspath(AGBOT_FOLDER):
            del sys.modules[name]
    import build_agbot
    return build_agbot


def build_robot(doc, label="Bruut_OpenAgbot_robot", placement=None):
    """Robot from 'agbot design'. Returns (robot part, {base name: object})."""
    BA = load_agbot()
    before = {o.Name for o in doc.Objects}
    robot = BA.new_part(doc, None, "Robot", label)
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    if placement is not None:
        robot.Placement = placement
    objs = {base_name(o.Name): o for o in doc.Objects if o.Name not in before}
    return robot, objs


def hide_robot_gnss(objs):
    for n in ROBOT_GNSS:
        o = objs.get(n)
        if o is not None and o.ViewObject is not None:
            o.ViewObject.Visibility = False


# ---------------------------------------------------------------------
# Refiller
# ---------------------------------------------------------------------
def build_frame(doc, parent):
    grp = new_part(doc, parent, "MRS_frame", "ibc_bed_and_mast")
    add_shape(doc, grp, "mrs_cross", "bed_cross_tubes_60x40x3", G.bed_cross_tubes(), "frame")
    add_shape(doc, grp, "mrs_rails", "bed_side_rails_60x40x3", G.bed_side_rails(), "frame")
    add_shape(doc, grp, "mrs_outrigger", "mast_outrigger_80x40x3", G.mast_outrigger(), "frame")
    add_shape(doc, grp, "mrs_gussets", "mast_gussets_10mm", G.mast_gussets(), "frame")
    add_shape(doc, grp, "mrs_bolts", "bed_bolts_12xM10", G.bed_bolts(), "zinc")
    add_shape(doc, grp, "mrs_guides", "corner_guides_angle_50x5", G.corner_guides(), "frame")
    add_shape(doc, grp, "mrs_eyes", "lashing_eyes", G.lashing_eyes(), "frame")
    add_shape(doc, grp, "mrs_mast", "mast_80x80x4", G.mast(), "frame")
    add_shape(doc, grp, "mrs_top_plate", "mast_top_plate_10mm", G.mast_top_plate(), "frame")
    add_shape(doc, grp, "mrs_pivot_pin", "pivot_pin_D30_washer_clip", G.pivot_pin(), "zinc")
    return grp


def build_ibc(doc, parent, litres):
    grp = new_part(doc, parent, "MRS_ibc", "IBC_1000l_standard")
    add_shape(doc, grp, "ibc_pallet", "ibc_pallet_4way", G.pallet(), "pallet")
    add_shape(doc, grp, "ibc_bottle", "ibc_bottle_HDPE", G.bottle(), "bottle")
    add_shape(doc, grp, "ibc_liquid", "liquid_in_ibc", liquid_shape("ibc", litres), "liquid")
    add_shape(doc, grp, "ibc_cage", "ibc_cage_tube_grid", G.cage(), "galv")
    add_shape(doc, grp, "ibc_valve", "ibc_valve_DN50_butterfly", G.ibc_valve(), "black")
    add_shape(doc, grp, "ibc_cap", "ibc_cap_DN150", G.ibc_cap(), "white")
    return grp


def build_straps(doc, parent):
    grp = new_part(doc, parent, "MRS_straps", "ratchet_straps")
    add_shape(doc, grp, "mrs_straps", "ratchet_straps_50mm", G.straps(), "strap")
    add_shape(doc, grp, "mrs_ratchets", "ratchets", G.ratchets(), "steel")
    return grp


def build_pump(doc, parent):
    grp = new_part(doc, parent, "MRS_pump", "pump_and_hoses")
    add_shape(doc, grp, "mrs_pump", "transfer_pump_24V_1.5in", G.pump_body(), "pump")
    add_shape(doc, grp, "mrs_pump_cradle", "pump_cradle_6mm", G.pump_cradle(), "frame")
    add_shape(doc, grp, "mrs_camlock", "camlock_elbow_on_ibc_valve", G.camlock_elbow(), "camlock")
    add_shape(doc, grp, "mrs_suction", "suction_hose_1.5in", G.suction_hose(), "hose")
    add_shape(doc, grp, "mrs_discharge", "discharge_hose_up_inside_mast", G.discharge_hose(), "hose")
    return grp


def build_arm(doc, parent, angle):
    grp = new_part(doc, parent, "MRS_arm", "arm_pivots_on_mast", arm_placement(angle))
    add_shape(doc, grp, "mrs_arm", "arm_60x60x3_with_boss", G.arm(), "frame")
    add_shape(doc, grp, "mrs_lock_pin", "lock_pin_D12", G.lock_pin(), "zinc")
    add_shape(doc, grp, "mrs_tip_plate", "arm_tip_plate", G.tip_plate(), "frame")
    add_shape(doc, grp, "mrs_drop_pipe", "drop_pipe_PP50", G.drop_pipe(), "pp")
    add_shape(doc, grp, "mrs_nozzle", "drip_stop_nozzle", G.nozzle(), "black")
    add_shape(doc, grp, "mrs_antenna", "rtk_antenna_above_nozzle", G.antenna(), "white")
    add_shape(doc, grp, "mrs_arm_hose", "hose_along_arm", G.arm_hose(), "hose")
    return grp


def build_refiller_into(doc, parent=None, arm=None, litres=None):
    """Refiller kit in robot coordinates; parent = the robot part (also used by animate_mrs.py)."""
    litres = 0.8 * P.ibc_nominal_l if litres is None else litres
    root = new_part(doc, parent, "Mobile_refiller", "mobile_refiller_simple_ibc")
    build_frame(doc, root)
    build_ibc(doc, root, litres)
    build_straps(doc, root)
    build_pump(doc, root)
    build_arm(doc, root, REF["arm"] if arm is None else arm)
    return root


def build_receiver_into(doc, parent=None, fill_l=None):
    """Receiver kit on the working robot (robot coordinates of that robot)."""
    fill_l = 0.8 * P.rx_tank_nominal if fill_l is None else fill_l
    root = new_part(doc, parent, "Receiver_kit", "receiver_kit_on_working_robot")
    add_shape(doc, root, "rx_cradle", "cradle_tubes_40x40x3", G.cradle_tubes(), "frame")
    add_shape(doc, root, "rx_pads", "rubber_strips_5mm", G.cradle_pads(), "rubber")
    add_shape(doc, root, "rx_cradle_bolts", "cradle_bolts_4xM10", G.cradle_bolts(), "zinc")
    add_shape(doc, root, "rx_tank", "work_tank_PE_%dl" % P.rx_tank_nominal, G.rx_tank_shell(), "tank")
    add_shape(doc, root, "rx_liquid", "liquid_in_work_tank", liquid_shape("receiver", fill_l), "liquid")
    add_shape(doc, root, "rx_straps", "tank_straps_50x3", G.rx_straps(), "zinc")
    add_shape(doc, root, "rx_funnel", "fill_funnel_300", G.funnel(), "funnel")
    add_shape(doc, root, "rx_strainer", "funnel_strainer", G.strainer(), "steel")
    add_shape(doc, root, "rx_level", "level_sensor_ultrasonic", G.rx_level_sensor(), "black")
    add_shape(doc, root, "rx_vent", "vent", G.rx_vent(), "yellow")
    return root


def build(arm=None, litres=None, save=True, step=True, show_robot=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Mobile refiller simple"
    doc.Comment = ("Generated by build_mrs.py from mrs_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Arm: build_mrs.set_arm(angle), IBC level: set_levels(ibc=...). "
                   "The robot's own GNSS antenna is hidden: it moves to the arm tip.")
    robot, objs = build_robot(doc)
    hide_robot_gnss(objs)
    build_refiller_into(doc, robot, arm, litres)
    if not show_robot:
        set_robot_visible(False, doc)
    doc.recompute()
    if save:
        doc.saveAs(SAVE_BASE + ".FCStd")
    if step:
        export_step(doc, SAVE_BASE + ".step")
    return doc


# ---------------------------------------------------------------------
# Refill scene: the working robot stopped on the straight of its U-turn, funnel under the nozzle
# (refiller robot coordinates; the field: refiller heading = along the headland)
# ---------------------------------------------------------------------
def worker_placement():
    """Working robot on the left of the refiller, same heading (turn to the right), funnel under the nozzle."""
    return App.Placement(V(G.NX, G.NY - P.funnel_xy[1], 0.0), App.Rotation())


def field_to_local(x, y, xm=0.0):
    """Field coordinates (x along the headland, y from the field edge) -> refiller coordinates, for the refill of a
    U-turn whose middle is at x = xm."""
    spot = C.refill_spot(xm - 0.5 * C.skip_n() * C.WORK_WIDTH, xm + 0.5 * C.skip_n() * C.WORK_WIDTH)
    return -(y - spot["yc"]), x - spot["xc"]


def turn_marks():
    """Rear-axle path of the U-turn (right) and the field edge, in refiller coordinates."""
    n = C.skip_n()
    pts, _ = C.u_turn_points(-0.5 * n * C.WORK_WIDTH, 0.5 * n * C.WORK_WIDTH, y_in=-2500.0, y_out=-2500.0, step=50.0)
    path = [field_to_local(x, y) for x, y in pts]
    edge = [field_to_local(x, 0.0) for x in (-6000.0, 6000.0)]
    return path, edge


def load_lfa():
    if LFA_FOLDER not in sys.path:
        sys.path.insert(0, LFA_FOLDER)
    import build_lfa
    return build_lfa


def build_docked(lift=140.0, litres=None, rx_fill=None):
    """Scene: the refiller inside the U-turn, the working robot (with the applicator, lifted) stopped on the straight
    with its funnel under the nozzle."""
    if DOCKED_DOC in App.listDocuments():
        App.closeDocument(DOCKED_DOC)
    doc = App.newDocument(DOCKED_DOC)
    doc.Label = "Mobile refiller simple - refill in the U-turn"
    doc.Comment = "Generated by build_mrs.build_docked(). Refiller robot coordinates; working robot on the left."
    worker, wobjs = build_robot(doc, "working_robot_with_applicator", worker_placement())
    try:
        BL = load_lfa()
        BL.build_into(doc, worker, lift, BL.translation(0.0, BL.P.robot_mount_y, 0.0))
    except Exception as exc:
        print("applicator not loaded:", exc)
    build_receiver_into(doc, worker, rx_fill)
    robot, objs = build_robot(doc, "refiller_robot")
    hide_robot_gnss(objs)
    build_refiller_into(doc, robot, 0.0, litres)
    doc.recompute()
    return doc


def check_docked(doc=None, tol=1.0):
    """Refiller (robot + kit) against the working robot with its applicator and receiver kit. Must be empty."""
    doc = doc or App.getDocument(DOCKED_DOC)
    refiller = {o.Name for o in doc.getObject("Robot001").OutListRecursive if o.TypeId == "Part::Feature"}
    worker = [o for o in doc.getObject("Robot").OutListRecursive if o.TypeId == "Part::Feature"]
    a = [(o, global_shape(o)) for o in doc.Objects if o.Name in refiller and base_name(o.Name) not in SKIP
         and not o.Shape.isNull()]
    b = [(o, global_shape(o)) for o in worker if base_name(o.Name) not in SKIP and not o.Shape.isNull()]
    rx = [(o, s) for o, s in b if o.Name.startswith("rx_")]
    rest = [(o, s) for o, s in b if not o.Name.startswith("rx_")]
    pairs = [(x, y) for x in a for y in b] + [(x, y) for x in rx for y in rest]
    return _overlaps(pairs, tol)


def nozzle_over_funnel(doc=None):
    """In the refill scene: horizontal offset nozzle - funnel axis (mm) and the height of the nozzle tip above the
    funnel rim (mm)."""
    fx, fy = worker_placement().multVec(V(P.funnel_xy[0], P.funnel_xy[1], 0.0))[:2]
    return math.hypot(fx - G.NX, fy - G.NY), P.nozzle_tip_z - P.FUNNEL_RIM_Z


def active_doc(doc=None):
    if doc is not None:
        return doc
    d = App.ActiveDocument
    if d is not None and d.getObject("Mobile_refiller") is not None:
        return d
    for n in App.listDocuments():
        d = App.getDocument(n)
        if d.getObject("Mobile_refiller") is not None:
            return d
    raise RuntimeError("no refiller document open")


def kit_objects(doc, root="Mobile_refiller"):
    return [o for o in doc.getObject(root).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc, robot="Robot"):
    r = doc.getObject(robot)
    if r is None:
        return []
    mine = {o.Name for o in kit_objects(doc)} if doc.getObject("Mobile_refiller") else set()
    return [o for o in r.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith(("anim_", "rx_"))]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        if base_name(o.Name) not in ROBOT_GNSS:
            o.ViewObject.Visibility = visible


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
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


# parts that are meant to touch or enter each other (hose ends in fittings, pins in holes, ...)
PAIRS_OK = {frozenset(p) for p in (
    ("mrs_suction", "mrs_camlock"), ("mrs_suction", "mrs_pump"), ("mrs_discharge", "mrs_pump"),
    ("mrs_camlock", "ibc_valve"), ("mrs_arm_hose", "mrs_drop_pipe"), ("mrs_lock_pin", "mrs_top_plate"),
    ("mrs_lock_pin", "mrs_arm"), ("mrs_pivot_pin", "mrs_arm"), ("rx_pads", "rx_cradle"), ("rx_strainer", "rx_funnel"),
    # flexible hose loop at the pivot (drawn rigid): it bends when the arm is folded
    ("mrs_arm_hose", "mrs_discharge"), ("mrs_arm_hose", "mrs_mast"), ("mrs_arm_hose", "mrs_top_plate"))}
SKIP = ("ibc_liquid", "rx_liquid")


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


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3) in the current pose: kit parts among themselves and against the robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in _checked(kit_objects(doc))]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def _in_arm(obj):
    parent = obj.getParentGeoFeatureGroup()
    while parent is not None:
        if parent.Name == "MRS_arm":
            return True
        parent = parent.getParentGeoFeatureGroup()
    return False


def check_fit(doc=None, tol=1.0, step=15):
    """Arm from out (0) to folded (arm_fold) in 'step' degree steps against the rest (the lock pin is pulled out
    between the two lock positions). Must be empty."""
    doc = active_doc(doc)
    mine = _checked(kit_objects(doc))
    still = [(o, global_shape(o)) for o in mine if not _in_arm(o)] + [(o, global_shape(o)) for o in robot_objects(doc)]
    out = {}
    a = 0
    while a <= P.arm_fold + 1e-6:
        doc.getObject("MRS_arm").Placement = arm_placement(a)
        doc.recompute()
        locked = a in (0, P.arm_fold)
        mv = [(o, global_shape(o)) for o in mine if _in_arm(o) and (locked or base_name(o.Name) != "mrs_lock_pin")]
        hits = _overlaps([(x, y) for x in mv for y in still], tol)
        if hits:
            out[a] = hits
        a += step
    doc.getObject("MRS_arm").Placement = arm_placement()
    doc.recompute()
    return out


def clearance(doc=None):
    """- front wheels steered 30 deg both ways: smallest distance to the kit;
    - IBC front to the stepper-motor plates; widest point on the left below 1.3 m; heights."""
    doc = active_doc(doc)
    out = {}
    kit = [(o, global_shape(o)) for o in _checked(kit_objects(doc)) if not _in_arm(o)]
    worst = (1e9, None)
    for tag in ("FL", "FR"):
        st = doc.getObject(tag + "_steered")
        keep = st.Placement
        for a in (-30.0, 30.0):
            st.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), a))
            doc.recompute()
            for o in st.OutListRecursive:
                if o.TypeId != "Part::Feature":
                    continue
                so = global_shape(o)
                for k, sk in kit:
                    if so.BoundBox.XLength == 0:
                        continue
                    bb = so.BoundBox
                    bb.enlarge(300.0)
                    if not bb.intersect(sk.BoundBox):
                        continue
                    d = sk.distToShape(so)[0]
                    if d < worst[0]:
                        worst = (d, "%s / %s %+.0f deg" % (k.Name, o.Name, a))
        st.Placement = keep
    doc.recompute()
    out["steering_30deg_to_kit"] = (round(worst[0], 1), worst[1])
    stepper = min((global_shape(o).BoundBox.YMin for o in robot_objects(doc) if re.match(r"F[LR]_", o.Name)
                   and global_shape(o).BoundBox.ZMax > P.bed_z[0]), default=None)
    ibc_front = max(global_shape(doc.getObject(n)).BoundBox.YMax for n in ("ibc_pallet", "ibc_cage", "mrs_guides"))
    out["ibc_front_to_front_stack"] = round(stepper - ibc_front, 1) if stepper is not None else None
    cut = G.box_span((-3000.0, 3000.0), (-3000.0, 3000.0), (0.0, 1300.0))
    worst = (0.0, None)
    for o in _checked(kit_objects(doc)):
        if _in_arm(o):
            continue
        s = global_shape(o)
        if s.BoundBox.ZMin < 1300.0:
            c = s.common(cut)
            if not c.isNull() and c.Volume > 0 and -c.BoundBox.XMin > worst[0]:
                worst = (-c.BoundBox.XMin, o.Name)
    out["left_extent_below_1300"] = (round(worst[0], 1), worst[1])
    out["nozzle_tip_z"] = P.nozzle_tip_z
    out["funnel_rim_z"] = P.FUNNEL_RIM_Z
    out["ibc_top_z"] = P.IBC_TOP
    out["antenna_top_z"] = round(G.ANT_TOP, 1)
    return out


# ---------------------------------------------------------------------
# Mass: bought parts with a fixed mass (kg), the rest from volume x density
# ---------------------------------------------------------------------
MASS_FIXED = {"mrs_pump": P.pump_kg, "ibc_pallet": P.ibc_kg["pallet"], "ibc_cage": P.ibc_kg["cage"],
              "ibc_bottle": P.ibc_kg["bottle"] - 1.5, "ibc_valve": 1.2, "ibc_cap": 0.3, "mrs_antenna": 0.45,
              "mrs_nozzle": 0.6, "mrs_ratchets": 1.6, "mrs_camlock": 0.5, "rx_level": 0.3}
PE, ALU, STEEL = 0.95e-6, 2.7e-6, 7.85e-6
HOSE = 0.6 / (math.pi * (P.hose_od / 2.0) ** 2 * 1000.0)     # 0.6 kg/m for a solid modelled hose
DENSITY = (("mrs_drop_pipe", PE), ("mrs_straps", 1.2e-6), ("mrs_suction", HOSE), ("mrs_discharge", HOSE),
           ("mrs_arm_hose", HOSE), ("rx_tank", PE), ("rx_funnel", PE), ("rx_vent", PE), ("rx_pads", 1.2e-6),
           ("ibc_liquid", P.liquid_density * 1e-6), ("rx_liquid", P.liquid_density * 1e-6))
IBC_PARTS = ("ibc_pallet", "ibc_cage", "ibc_bottle", "ibc_valve", "ibc_cap")


def _mass_cg(obj):
    shape = global_shape(obj)
    if shape.isNull():
        return 0.0, V(0, 0, 0)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    name = base_name(obj.Name)
    if name in MASS_FIXED:
        return MASS_FIXED[name], cg
    for key, d in DENSITY:
        if name == key:
            return vol * d, cg
    return vol * STEEL, cg


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Masses (kg) and centres of gravity: kit (without the IBC), empty IBC, arm, liquid."""
    doc = active_doc(doc)
    objs = kit_objects(doc)
    out = {}
    for name, sel in (("kit", lambda o: base_name(o.Name) not in IBC_PARTS + SKIP),
                      ("ibc_empty", lambda o: base_name(o.Name) in IBC_PARTS), ("arm", _in_arm),
                      ("liquid", lambda o: base_name(o.Name) in SKIP)):
        m, c = _sum([o for o in objs if sel(o)])
        out[name + "_kg"] = round(m, 1)
        out[name + "_cg"] = (round(c.x), round(c.y), round(c.z))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in kit_objects(doc) + robot_objects(doc):
        if o.Shape.isNull() or not o.ViewObject.Visibility:
            continue
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


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
    tgt = V(*target) if target is not None else V(0, 0, 900)
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


GROUND = ("render_floor", "render_field", "render_edge", "render_path")


def add_floor(doc, x=(-2600.0, 1400.0), y=(-1500.0, 1500.0), color=(0.62, 0.70, 0.52)):
    obj = doc.addObject("Part::Feature", GROUND[0])
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = 30
    return obj


def add_field(doc):
    """Refill scene: headland, field, field edge and the rear-axle path of the U-turn (refiller coordinates)."""
    path, edge = turn_marks()
    ex = edge[0][0]
    add_floor(doc, x=(-5200.0, ex), y=(-5500.0, 5500.0), color=(0.62, 0.70, 0.52))
    fld = doc.addObject("Part::Feature", GROUND[1])
    fld.Shape = G.box_span((ex, ex + 2500.0), (-5500.0, 5500.0), (-40.0, 0.0))
    fld.ViewObject.ShapeColor = (0.45, 0.62, 0.30)
    e = doc.addObject("Part::Feature", GROUND[2])
    e.Shape = G.ground_line(edge, w=50.0)
    e.ViewObject.ShapeColor = (0.97, 0.97, 0.95)
    p = doc.addObject("Part::Feature", GROUND[3])
    p.Shape = G.ground_line(path, w=30.0, z=1.5)
    p.ViewObject.ShapeColor = (0.95, 0.95, 0.95)


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def add_stream(doc):
    fx, fy = G.NX, G.NY
    obj = doc.addObject("Part::Feature", "render_stream")
    obj.Shape = G.stream(fx, fy, P.nozzle_tip_z, G.RX_TOP + P.funnel_neck)
    obj.ViewObject.ShapeColor = COLOR["liquid"]
    obj.ViewObject.Transparency = 30
    return obj


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP)."""
    import FreeCADGui as Gui
    out = []
    doc = build(save=False, step=False)
    add_floor(doc)
    out.append(save_view("1_iso_refiller_ibc.png", (1.0, -1.1, -0.7), target=(-350, 0, 1000), height=3000))
    out.append(save_view("2_side.png", (1.0, 0.0, 0.0), target=(-200, 0, 1050), height=2600))
    out.append(save_view("3_front_arm_out.png", (0.0, -1.0, 0.0), target=(-450, 0, 1050), height=2600))
    remove(doc, [GROUND[0]])
    set_visible(doc, ("ibc_pallet", "ibc_bottle", "ibc_liquid", "ibc_cage", "ibc_valve", "ibc_cap", "mrs_straps",
                      "mrs_ratchets"), False)
    out.append(save_view("4_bed_without_ibc.png", (1.0, -1.0, -0.8), target=(-200, 0, 700), height=2300))
    arm = [o.Name for o in kit_objects(doc) if _in_arm(o)]
    set_visible(doc, arm, False)
    out.append(save_view("5_pump_under_ibc.png", (0.75, 0.35, -0.75), target=(-330, -100, 600), height=1250))
    set_visible(doc, arm, True)
    set_visible(doc, ("ibc_pallet", "ibc_bottle", "ibc_liquid", "ibc_cage", "ibc_valve", "ibc_cap", "mrs_straps",
                      "mrs_ratchets"), True)
    out.append(save_view("6_valve_mast_foot.png", (1.0, -0.55, -0.35), target=(-640, -60, 900), height=900))
    set_arm(P.arm_fold, doc)
    add_floor(doc)
    out.append(save_view("7_arm_folded_transport.png", (0.75, -1.0, -0.6), target=(-200, -100, 1000), height=3000))
    App.closeDocument(doc.Name)
    # refill in the U-turn
    doc = build_docked()
    Gui.updateGui()
    add_stream(doc)
    add_field(doc)
    out.append(save_view("8_refill_iso.png", (1.0, 0.75, -0.65), target=(-800, 100, 600), height=3600))
    out.append(save_view("9_refill_along_headland.png", (0.0, 1.0, -0.12), target=(-750, 0, 900), height=2500))
    out.append(save_view("10_refill_top_in_the_turn.png", (0.0, 0.0, -1.0), target=(0, 0, 0), height=9500,
                         up=(-1.0, 0.0, 0.0)))
    out.append(save_view("11_nozzle_over_funnel.png", (1.0, 0.45, -0.35), target=(G.NX + 40, G.NY, 1250), height=800))
    App.closeDocument(doc.Name)
    build()
    return out
