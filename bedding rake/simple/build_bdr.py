"""Model of the bedding rake (cubicle groomer) on the Bruut OpenAgbot (standard robot), with a row of cubicles.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_bdr
    build_bdr.build()                      # saves FCStd and STEP (work pose, barn included)
    build_bdr.set_pose(lift=40)            # arm swung up (row end); barn_dy moves the cubicles along y
    build_bdr.check_interference()         # overlap in work with the barn (must be empty)
    build_bdr.check_poses()                # dividers passing the arm, and the lifted poses (must be empty)
    build_bdr.actuator_range()
    build_bdr.mass_properties()
    build_bdr.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bdr_params as P
import bdr_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Bedding_Rake"
SAVE_BASE = os.path.join(FOLDER, "Bedding_Rake")
ROOT = "Bedding_rake"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "motor": (0.25, 0.26, 0.28),
    "concrete": (0.80, 0.78, 0.72),
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







def arm_placement(lift):
    """Arm swing about the pivot axis (y); + lift = the outer end goes up."""
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 1, 0), -lift), V(P.pivot[0], 0, P.pivot[1]))


def build_into(doc, parent=None, lift=0.0):
    root = new_part(doc, parent, ROOT, "bedding_rake_simple")
    mount = new_part(doc, root, "Mount", "mount_bracket_bearer")
    add_shape(doc, mount, "bracket", "bracket_8mm_back_plate_pivot_lugs", G.bracket(), "frame")
    add_shape(doc, mount, "clamp_bolts", "clamp_bolts_M10_4x", G.clamp_bolts(), "zinc")
    add_shape(doc, mount, "pivot_pin", "pivot_pin_D20", G.pivot_pin(), "zinc")
    add_shape(doc, mount, "bearer", "bearer_40x40x3_actuator_lug", G.bearer(), "frame")
    add_shape(doc, mount, "bearer_bolts", "bearer_bolts_M10_4x", G.bearer_bolts(), "zinc")
    body, rod, _ = G.actuator(lift)
    add_shape(doc, mount, "act_body", "lift_actuator_24V_1500N_stroke_150", body, "motor")
    add_shape(doc, mount, "act_rod", "lift_actuator_rod", rod, "zinc")
    arm = new_part(doc, root, "Arm", "arm_swings_about_pivot", arm_placement(lift))
    add_shape(doc, arm, "arm", "arm_60x40x3_hangers_crank", G.arm(), "frame")
    add_shape(doc, arm, "crank_pin", "crank_pin_D12", G.crank_pin(), "zinc")
    add_shape(doc, arm, "rotor", "tine_rotor_D60_L970_tines_D7_tip_D240", G.rotor(), "steel")
    shaft, brgs = G.shaft_and_bearings()
    add_shape(doc, arm, "rotor_shaft", "rotor_shaft_D20", shaft, "zinc")
    add_shape(doc, arm, "rotor_bearings", "rotor_bearings_2x", brgs, "motor")
    add_shape(doc, arm, "gearmotor", "rotor_gearmotor_48V_400W", G.gearmotor(), "motor")
    barn = new_part(doc, root, "Barn", "barn_curb_beds_dividers")
    add_shape(doc, barn, "bed", "cubicle_beds_and_curb", G.bed(), "concrete")
    add_shape(doc, barn, "dividers", "divider_loops_D48", G.dividers(), "zinc")
    return root


def set_pose(lift=0.0, barn_dy=0.0, doc=None):
    """lift: arm swing (deg); barn_dy: shift of the barn along y (the robot drives along the cubicles)."""
    doc = active_doc(doc)
    doc.getObject("Arm").Placement = arm_placement(lift)
    body, rod, _ = G.actuator(lift)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod
    doc.getObject("Barn").Placement = App.Placement(V(0, barn_dy, 0), App.Rotation())


def set_barn(visible=True, doc=None):
    for o in objects_of(active_doc(doc), "Barn"):
        o.ViewObject.Visibility = visible


def build_robot(doc):
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Bedding rake simple"
    doc.Comment = ("Generated by build_bdr.py from bdr_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Work pose, cubicles on the right (Barn group).")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    if robot is not None and not show_robot:
        set_robot_visible(False, doc)
    doc.recompute()
    if save:
        doc.saveAs(SAVE_BASE + ".FCStd")
    if step:
        export_step(doc, SAVE_BASE + ".step")
    return doc


# ---------------------------------------------------------------------
# Object lists and checks
# ---------------------------------------------------------------------
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
    raise RuntimeError("no document with %s open" % ROOT)


def objects_of(doc, name):
    g = doc.getObject(name)
    if g is None:
        return []
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in objects_of(doc, ROOT)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def export_step(doc, path):
    import Import
    objs = []
    for o in objects_of(doc, ROOT):
        f = doc.addObject("Part::Feature", "step_" + o.Name)
        f.Label = o.Label
        f.Shape = global_shape(o)
        objs.append(f)
    try:
        Import.export(objs, path)
    finally:
        for f in objs:
            doc.removeObject(f.Name)


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
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




JOINTS = {("clamp_bolts", "bracket"), ("pivot_pin", "bracket"), ("pivot_pin", "arm"), ("bearer_bolts", "bearer"),
          ("act_body", "bearer"), ("act_body", "act_rod"), ("act_rod", "crank_pin"), ("crank_pin", "arm"),
          ("rotor_shaft", "rotor"), ("rotor_shaft", "arm"), ("rotor_shaft", "rotor_bearings"),
          ("rotor_shaft", "gearmotor"), ("rotor_bearings", "arm"), ("gearmotor", "arm"), ("rotor", "bed"),
          ("dividers", "bed")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    return (a == "bearer_bolts" and b.startswith("upper_beam")) or (b == "bearer_bolts" and a.startswith("upper_beam"))


def _mine(doc, barn=True):
    names = {o.Name for o in objects_of(doc, "Barn")}
    return [o for o in objects_of(doc, ROOT) if barn or o.Name not in names]


def check_interference(doc=None, tol=1.0):
    """Work pose with the barn: everything among itself and against the robot (JOINTS skipped)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in _mine(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    """1) Work: the dividers moved along y past the arm (the robot drives on). 2) Lifted (row end, no barn): arm and
    actuator against the robot and the mount. Must be empty."""
    doc = active_doc(doc)
    out = {}
    moving = objects_of(doc, "Arm") + [doc.getObject("act_body"), doc.getObject("act_rod")]
    for dy in (-600.0, -450.0, -300.0, -150.0, 0.0):
        set_pose(0.0, dy, doc)
        mv = [(o, global_shape(o)) for o in objects_of(doc, "Arm")]
        dv = (doc.getObject("dividers"), global_shape(doc.getObject("dividers")))
        hits = _overlaps([(a, dv) for a in mv], tol)
        if hits:
            out[("dy", dy)] = hits
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in _mine(doc, barn=False) + robot_objects(doc) if o.Name not in names]
    for lift in P.LIFT_POSES[1:]:
        set_pose(lift, 0.0, doc)
        mv = [(o, global_shape(o)) for o in moving]
        hits = _overlaps([(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
        if hits:
            out[("lift", lift)] = hits
    set_pose(0.0, 0.0, doc)
    return out


def actuator_range():
    lens = [G.actuator(a)[2] for a in P.LIFT_POSES]
    return {"length_mm": (round(min(lens)), round(max(lens))), "stroke_used": round(max(lens) - min(lens))}


MASS_FIXED = {"act_body": 2.4, "act_rod": 0.6, "gearmotor": 5.5, "rotor_bearings": 1.0, "bed": 0.0, "dividers": 0.0}
DENSITY = ()


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key, m in MASS_FIXED.items():
        if obj.Name == key:
            return m, cg
    dens = P.steel
    for key, d in DENSITY:
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def sum_mass(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) of the whole rake, the mount and the arm (the barn counts 0)."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Mount", "Arm"):
        m, c = sum_mass(objects_of(doc, name))
        out[name.lower() + "_kg"] = round(m, 1)
        out[name.lower() + "_cg"] = (round(c.x), round(c.y), round(c.z))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in objects_of(doc, ROOT):
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
    tgt = V(*target) if target is not None else V(0, 600, 300)
    eye = tgt - d * 9000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(30000.0)
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


GROUND = "render_floor"


def add_floor(doc, y=(-900.0, 1800.0), x=(-1000.0, 1000.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.72, 0.72, 0.70)
    obj.ViewObject.Transparency = 30
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)





def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_floor(doc, y=(-1800.0, 1800.0), x=(-900.0, 3000.0))
    out.append(save_view("1_iso_rear_right_in_barn.png", (-1.0, 1.3, -0.8), target=(800, 0, 400)))
    out.append(save_view("2_rear_view_work.png", (0.0, 1.0, 0.0), target=(800, 0, 500), height=1600))
    set_pose(40.0, 0.0, doc)
    set_barn(False, doc)
    out.append(save_view("3_rear_view_lifted.png", (0.0, 1.0, 0.0), target=(500, 0, 600), height=1600))
    set_pose(0.0, 0.0, doc)
    set_barn(True, doc)
    remove(doc, [GROUND])
    out.append(save_view("4_top_in_barn.png", (0.0, 0.0, -1.0), target=(800, 0, 0), up=(0.0, 1.0, 0.0), height=2600))
    set_robot_visible(False, doc)
    doc.getObject("dividers").ViewObject.Visibility = False
    out.append(save_view("5_rotor_detail.png", (-0.6, 1.0, -0.6), target=(1200, 0, 350), height=1300))
    App.closeDocument(doc.Name)
    build()
    return out
