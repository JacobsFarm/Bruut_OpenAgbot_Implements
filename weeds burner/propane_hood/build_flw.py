"""Model of the propane flame weeder with a hood behind the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_flw
    build_flw.build()                      # saves FCStd and STEP (hood on the ground)
    build_flw.set_pose(float_h=60)         # the hood floats up / down on the parallelogram (mm)
    build_flw.check_interference()         # overlap in the current pose (must be empty)
    build_flw.check_fit()                  # overlap over the float range (must be empty)
    build_flw.clearance()                  # distances to the rear tyres and the robot frame
    build_flw.mass_properties()
    build_flw.render_all()                 # all images in previews/
"""
import math
import os
import random
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import flw_params as P
import flw_calc as C
import flw_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Flame_Weeder_Hood"
SAVE_BASE = os.path.join(FOLDER, "Flame_Weeder_Hood")
ROOT = "Flame_weeder"

COLOR = {
    "frame": (0.20, 0.22, 0.25),
    "skin": (0.55, 0.56, 0.58),
    "blanket": (0.95, 0.93, 0.85),
    "alu": (0.86, 0.87, 0.89),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "burner": (0.40, 0.25, 0.15),
    "pipe": (0.70, 0.45, 0.20),
    "stainless": (0.86, 0.87, 0.88),
    "valve": (0.85, 0.15, 0.10),
    "brass": (0.85, 0.70, 0.30),
    "hose": (0.10, 0.10, 0.10),
    "cylinder": (0.92, 0.92, 0.90),
    "saddle": (0.15, 0.15, 0.15),
    "wheel": (0.45, 0.46, 0.48),
}


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
    obj.Shape = shape
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
    return obj


# ---------------------------------------------------------------------
# Pose: float of the hood on the free parallelogram
# ---------------------------------------------------------------------
MOVING = ("Hood", "Upper_arms", "Lower_arms")


def pose_placements(float_h=0.0):
    if not P.float_range[0] - 1e-6 <= float_h <= P.float_range[1] + 1e-6:
        raise ValueError("float %.1f outside %.1f .. %.1f" % (float_h, P.float_range[0], P.float_range[1]))
    dy, dz, beta = C.head_offset(float_h)
    out = {"Hood": App.Placement(V(0, dy, dz), App.Rotation())}
    for name, z in (("Upper_arms", P.pin_z[0]), ("Lower_arms", P.pin_z[1])):
        out[name] = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -beta), V(0, P.pin_rear_y, z))
    return out


def set_pose(float_h=0.0, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(float_h).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_hood(doc, parent, pl):
    hood = new_part(doc, parent, "Hood", "hood_1500x800_6_burners", pl["Hood"])
    sh = new_part(doc, hood, "Hood_shell", "hood_shell")
    add_shape(doc, sh, "hood_skin", "hood_skin_steel_1.5mm", G.hood_skin(), "skin")
    add_shape(doc, sh, "blanket", "ceramic_fibre_blanket_25mm", G.blanket(), "blanket")
    add_shape(doc, sh, "top_cover", "top_cover_alu_0.8mm_on_spacers", G.top_cover(), "alu")
    add_shape(doc, sh, "ribs", "edge_angles_30x30x3", G.ribs(), "frame")
    add_shape(doc, sh, "front_shield", "heat_shield_alu_4mm_front", G.front_shield(), "alu")
    add_shape(doc, sh, "hood_bracket", "hood_bracket_lugs_8mm", G.hood_bracket(), "frame")
    add_shape(doc, sh, "hood_pins", "parallelogram_rear_pins_D20", G.hood_pins(), "steel")
    bu = new_part(doc, hood, "Burners", "burners_and_gas_on_the_hood")
    add_shape(doc, bu, "burners", "flat_flame_burners_6x_28kW", G.burners(), "burner")
    add_shape(doc, bu, "burner_feeds", "burner_feed_tubes", G.burner_feeds(), "pipe")
    add_shape(doc, bu, "manifold", "manifold_half_inch_clamps", G.manifold(), "pipe")
    add_shape(doc, bu, "pilots", "pilot_tubes_igniters_flame_sensors", G.pilots(), "stainless")
    add_shape(doc, bu, "coil", "vaporiser_coil_stainless_12x1", G.coil(), "stainless")
    add_shape(doc, bu, "hood_gas_train", "regulator_sensor_burner_and_pilot_valves", G.hood_gas_train(), "valve")
    add_shape(doc, bu, "hood_hoses", "gas_hoses_on_the_hood", G.hood_hoses(), "hose")
    cs = new_part(doc, hood, "Castors", "castors_steel_D200_swivel")
    add_shape(doc, cs, "castor_arms", "castor_arms_40x40_posts", G.castor_arms(), "frame")
    add_shape(doc, cs, "castor_frames", "castor_plates_swivels_forks", G.castor_frames(), "zinc")
    add_shape(doc, cs, "castor_wheels", "castor_wheels_steel_200x50", G.castor_wheels(), "wheel")
    return hood


def build_mount(doc, parent, pl):
    grp = new_part(doc, parent, "Mount", "mount_headstock_parallelogram_gas_train")
    add_shape(doc, grp, "sub_plate", "sub_plate_8mm_under_rear_beams", G.sub_plate(), "frame")
    add_shape(doc, grp, "sub_bolts", "sub_plate_bolts_4xM10", G.sub_bolts(), "zinc")
    add_shape(doc, grp, "headstock", "headstock_plates_8mm", G.headstock(), "frame")
    add_shape(doc, grp, "stock_pins", "parallelogram_front_pins_D20", G.stock_pins(), "steel")
    up = new_part(doc, grp, "Upper_arms", "upper_arms", pl["Upper_arms"])
    add_shape(doc, up, "upper_arm_tubes", "upper_arms_40x40x3", G.upper_arms(), "frame")
    lo = new_part(doc, grp, "Lower_arms", "lower_arms", pl["Lower_arms"])
    add_shape(doc, lo, "lower_arm_tubes", "lower_arms_40x40x3_cross_tube", G.lower_arms(), "frame")
    add_shape(doc, grp, "robot_gas_train", "liquid_filter_two_main_solenoid_valves", G.robot_gas_train(), "valve")
    add_shape(doc, grp, "robot_hoses", "liquid_hoses_cylinders_to_hood", G.robot_hoses(), "hose")
    return grp


def build_gas(doc, parent):
    grp = new_part(doc, parent, "Gas", "propane_2x18kg_forklift_cylinders")
    add_shape(doc, grp, "cradle", "cradle_channels_40x60x4", G.cradle(), "frame")
    add_shape(doc, grp, "cradle_bolts", "cradle_bolts_4xM10", G.cradle_bolts(), "zinc")
    add_shape(doc, grp, "saddles", "saddles_rubber_lined", G.saddles(), "saddle")
    add_shape(doc, grp, "cylinders", "forklift_cylinders_18kg_liquid_withdrawal", G.cylinders(), "cylinder")
    add_shape(doc, grp, "collars", "cylinder_collars_and_valves", G.collars(), "brass")
    add_shape(doc, grp, "straps", "straps_40x2", G.straps(), "frame")
    return grp


def build_into(doc, parent=None, float_h=0.0):
    """Put the flame weeder in a document, in robot coordinates (also used by animate_flw.py)."""
    pl = pose_placements(float_h)
    root = new_part(doc, parent, ROOT, "propane_flame_weeder_hood_1500")
    build_gas(doc, root)
    build_mount(doc, root, pl)
    build_hood(doc, root, pl)
    return root


def build_robot(doc):
    """Real robot model from 'agbot design' (read only)."""
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


def build(float_h=0.0, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Propane flame weeder with hood"
    doc.Comment = ("Generated by build_flw.py from flw_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Float the hood with build_flw.set_pose(float_h).")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, float_h)
    if robot is not None:
        set_robot_visible(bool(show_robot), doc)
    doc.recompute()
    if save:
        doc.saveAs(SAVE_BASE + ".FCStd")
    if step:
        export_step(doc, SAVE_BASE + ".step")
    return doc


def active_doc(doc=None):
    if doc is not None:
        return doc
    d = App.ActiveDocument
    if d is not None and d.getObject(ROOT) is not None:
        return d
    for n in App.listDocuments():
        d = App.getDocument(n)
        if d.getObject(ROOT) is not None:
            return d
    raise RuntimeError("no flame weeder document open")


def weeder_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in weeder_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in weeder_objects(doc):
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


# parts that sit in or on each other on purpose (pins, bolts, pipes through walls, hoses on fittings, ...)
TOUCH = (("hood_pins", "hood_bracket"), ("hood_pins", "upper_arm_tubes"), ("hood_pins", "lower_arm_tubes"),
         ("stock_pins", "headstock"), ("stock_pins", "upper_arm_tubes"), ("stock_pins", "lower_arm_tubes"),
         ("sub_bolts", "sub_plate"), ("cradle_bolts", "cradle"), ("saddles", "cylinders"), ("saddles", "cradle"),
         ("straps", "cylinders"), ("straps", "saddles"), ("collars", "cylinders"), ("manifold", "burner_feeds"),
         ("burner_feeds", "burners"), ("manifold", "hood_skin"), ("manifold", "blanket"), ("coil", "hood_skin"),
         ("coil", "blanket"), ("coil", "top_cover"), ("hood_hoses", "top_cover"), ("hood_hoses", "hood_gas_train"),
         ("hood_hoses", "coil"), ("hood_hoses", "manifold"), ("robot_hoses", "collars"), ("robot_hoses", "sub_plate"),
         ("robot_hoses", "robot_gas_train"), ("robot_hoses", "top_cover"), ("robot_hoses", "coil"),
         ("robot_gas_train", "sub_plate"), ("castor_arms", "ribs"), ("castor_arms", "castor_frames"),
         ("castor_frames", "castor_wheels"), ("top_cover", "hood_skin"), ("ribs", "hood_skin"),
         ("front_shield", "hood_skin"), ("hood_bracket", "top_cover"), ("hood_bracket", "hood_skin"),
         ("hood_bracket", "blanket"), ("hood_gas_train", "top_cover"), ("pilots", "burners"), ("blanket", "hood_skin"))


def _touch(a, b):
    for p, q in TOUCH:
        if (a.startswith(p) and b.startswith(q)) or (a.startswith(q) and b.startswith(p)):
            return True
    return False


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        if _touch(oa.Name, ob.Name):
            continue
        if not sa.BoundBox.intersect(sb.BoundBox):
            continue
        try:
            vol = sa.common(sb).Volume
        except Exception as exc:
            hits.append((oa.Label, ob.Label, "error %s" % exc))
            continue
        if vol > tol:
            hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3) in the current pose: weeder parts among themselves and against the robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in weeder_objects(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def check_fit(doc=None, tol=1.0):
    """Interference at the float limits (the robot hoses are flexible and left out). Must be empty."""
    doc = active_doc(doc)
    out = {}
    for h in (P.float_range[0], P.float_range[1]):
        set_pose(h, doc)
        hits = [x for x in check_interference(doc, tol) if "liquid_hoses" not in x[0] + x[1]]
        if hits:
            out[h] = hits
    set_pose(doc=doc)
    return out


def _min_dist(objs, targets):
    best = (1e9, None, None)
    for o in objs:
        s = global_shape(o)
        for t in targets:
            ts = global_shape(t)
            if s.BoundBox.isValid() and ts.BoundBox.isValid():
                d = s.distToShape(ts)[0]
                if d < best[0]:
                    best = (d, o.Name, t.Name)
    return (round(best[0], 1), best[1], best[2])


def clearance(doc=None):
    """Smallest distances (mm): hood (shield) to the rear tyres, cylinders to the steering stacks and the rear frame
    bolts, mount to the rear wheel units."""
    doc = active_doc(doc)
    if doc.getObject("Robot") is None:
        return {}
    out = {}
    rear = [o for o in robot_objects(doc) if o.Name.startswith(("RL_", "RR_"))]
    front = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
    hood = [o for o in doc.getObject("Hood_shell").OutListRecursive if o.TypeId == "Part::Feature"]
    for h in P.float_range:
        set_pose(h, doc)
        out["hood_to_rear_units_float_%+d" % h] = _min_dist(hood, rear)
    set_pose(doc=doc)
    gas = [doc.getObject(n) for n in ("cylinders", "collars", "cradle", "straps")]
    out["gas_to_front_units"] = _min_dist(gas, front)
    out["gas_to_rear_units"] = _min_dist(gas, rear)
    mount = [o for o in doc.getObject("Mount").OutListRecursive if o.TypeId == "Part::Feature"
             and o.Name != "robot_hoses"]
    out["mount_to_rear_units"] = _min_dist(mount, rear)
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
MASS_FIXED = {"burners": 6 * 1.1, "pilots": 0.6, "hood_gas_train": 3.0, "robot_gas_train": 2.5,
              "castor_wheels": 2 * 3.0, "castor_frames": 2 * 1.5, "cylinders": 2 * P.cyl_kg_tare, "collars": 1.0,
              "hood_hoses": 0.8, "robot_hoses": 1.5, "saddles": 1.2}
# tubes modelled as solid rods: density x the steel share of the cross-section
DENSITY = (("blanket", 0.128e-6), ("top_cover", 2.7e-6), ("front_shield", 2.7e-6), ("coil", 0.31 * 7.9e-6),
           ("manifold", 0.45 * 7.85e-6), ("burner_feeds", 0.44 * 7.85e-6))
STEEL = 7.85e-6


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key in sorted(MASS_FIXED, key=len, reverse=True):
        if obj.Name.startswith(key):
            return MASS_FIXED[key], cg
    dens = STEEL
    for key, d in DENSITY:
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates), cylinders empty."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(weeder_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for name in ("Hood", "Mount", "Gas", "Hood_shell", "Burners", "Castors"):
        ms, cs = _sum(objs_of(name))
        out[name.lower() + "_kg"] = round(ms, 2)
        if name in ("Hood", "Mount", "Gas"):
            out[name.lower() + "_cg"] = (round(cs.x), round(cs.y), round(cs.z))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in weeder_objects(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin)), (
        round(bb.XMax), round(bb.YMax), round(bb.ZMax))


# ---------------------------------------------------------------------
# Scene for the images: seedbed, weed seedlings, flames
# ---------------------------------------------------------------------
SCENE = ("render_floor", "render_bed", "render_rows", "render_weeds", "render_scorched", "render_flames")


def add_scene(doc, y=(-3200.0, 1800.0), flames=True):
    floor = doc.addObject("Part::Feature", "render_floor")
    floor.Shape = G.box_span((-1700.0, 1700.0), y, (-60.0, -40.0))
    floor.ViewObject.ShapeColor = (0.40, 0.30, 0.20)
    bed = doc.addObject("Part::Feature", "render_bed")
    bed.Shape = G.seedbed(y[0], y[1])
    bed.ViewObject.ShapeColor = (0.50, 0.37, 0.25)
    rows = doc.addObject("Part::Feature", "render_rows")
    rows.Shape = G.seed_rows(y[0], y[1])
    rows.ViewObject.ShapeColor = (0.62, 0.50, 0.36)
    rnd = random.Random(4)
    pts = [(rnd.uniform(-720, 720), rnd.uniform(y[0] + 50, y[1] - 50), rnd.uniform(0.7, 1.2)) for _ in range(420)]
    alive = [G.weed(x, yy, s) for (x, yy, s) in pts if yy > P.hood_y[0] + 100.0]
    dead = [G.weed_scorched(x, yy, s) for (x, yy, s) in pts if yy <= P.hood_y[0] + 100.0]
    w = doc.addObject("Part::Feature", "render_weeds")
    w.Shape = Part.makeCompound(alive)
    w.ViewObject.ShapeColor = (0.45, 0.78, 0.25)
    d = doc.addObject("Part::Feature", "render_scorched")
    d.Shape = Part.makeCompound(dead)
    d.ViewObject.ShapeColor = (0.30, 0.22, 0.12)
    if flames:
        f = doc.addObject("Part::Feature", "render_flames")
        f.Shape = G.flames()
        f.ViewObject.ShapeColor = (1.00, 0.55, 0.10)
        f.ViewObject.Transparency = 20
        f.ViewObject.DisplayMode = "Shaded"
    for n in ("render_weeds", "render_scorched", "render_rows"):
        doc.getObject(n).ViewObject.DisplayMode = "Shaded"
    doc.recompute()


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_transparency(doc, names, t):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Transparency = t


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
    tgt = V(*target) if target is not None else V(0, 0, 400)
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


HOOD_SEE = ("hood_skin", "blanket", "top_cover", "front_shield")


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_scene(doc, flames=False)
    out.append(save_view("1_work_iso_on_robot.png", (-1.0, 1.25, -0.8), target=(0, -600, 350), height=3000))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, -500, 500), height=2300))
    remove(doc, SCENE)
    add_scene(doc, flames=True)
    set_transparency(doc, HOOD_SEE, 70)
    out.append(save_view("3_flames_through_the_hood.png", (-1.0, 0.9, -0.55), target=(0, -1250, 120), height=1700))
    for n in ("top_cover", "blanket", "castor_wheels", "castor_frames", "castor_arms"):
        doc.getObject(n).ViewObject.Visibility = False
    set_transparency(doc, ("hood_skin", "front_shield"), 85)
    out.append(save_view("4_flames_side_section.png", (1.0, 0.0, 0.0), target=(0, -1250, 150), height=1000))
    for n in ("top_cover", "blanket", "castor_wheels", "castor_frames", "castor_arms"):
        doc.getObject(n).ViewObject.Visibility = True
    remove(doc, SCENE)
    set_transparency(doc, HOOD_SEE, 0)
    set_robot_visible(False, doc)
    out.append(save_view("5_burners_coil_from_below.png", (0.3, 0.4, 1.0), target=(0, -1250, 150), height=1800))
    out.append(save_view("6_gas_train_hood_front.png", (-0.6, -1.0, -0.7), target=(0, -1000, 300), height=900))
    set_robot_visible(True, doc)
    out.append(save_view("7_cylinders_on_robot.png", (-1.0, -0.9, -0.8), target=(0, -150, 800), height=1500))
    out.append(save_view("8_mount_parallelogram.png", (1.0, 0.5, -0.35), target=(0, -760, 450), height=900))
    App.closeDocument(doc.Name)
    build()
    return out
