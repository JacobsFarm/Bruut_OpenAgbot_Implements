"""Model of the Cambridge roll with the tow hitch on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_cbr
    build_cbr.build()                          # saves FCStd and STEP (trailer straight behind the robot)
    build_cbr.set_articulation(35, 0)          # yaw (+ = trailer swings to the left), pitch (+ = drawbar up)
    build_cbr.check_interference()             # overlap in the current pose (must be empty)
    build_cbr.check_poses()                    # overlap over the articulation range (must be empty)
    build_cbr.clearance()                      # smallest distance of the trailer to the robot over the yaw range
    build_cbr.mass_properties()                # mass, centre of gravity, load on the tow ball
    build_cbr.render_all()                     # all images in previews/

The general helpers here (tree, checks, camera) are also used by the overseeder and the combination.
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cbr_params as P
import cbr_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Cambridge_Roll"
SAVE_BASE = os.path.join(FOLDER, "Cambridge_Roll")
ROOT = "Cambridge_roll"
TRAILER = "Roll_trailer"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "hitch": (0.12, 0.12, 0.13),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "cast": (0.28, 0.29, 0.31),
    "bearing": (0.10, 0.27, 0.62),
    "coupling": (0.15, 0.15, 0.16),
    "red": (0.80, 0.10, 0.08),
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


def add_shape(doc, parent, name, label, shape, color, visible=True, colors=None):
    if isinstance(shape, (list, tuple)):
        shape = Part.makeCompound(list(shape))
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = (colors or COLOR)[color] if isinstance(color, str) else color
        view.Visibility = visible
    return obj


# ---------------------------------------------------------------------
# Articulation of the trailer about the ball centre (relative to the robot)
# ---------------------------------------------------------------------
def articulation(yaw=0.0, pitch=0.0):
    """Placement of the trailer part: yaw about the vertical through the ball (+ = trailer to the left, i.e. the
    robot turns right), pitch about the cross axis through the ball centre (+ = drawbar up)."""
    c = V(P.ball[0], P.ball[1], P.ball_z)
    rot = App.Rotation(V(0, 0, 1), yaw).multiply(App.Rotation(V(1, 0, 0), -pitch))
    return App.Placement(c, rot).multiply(App.Placement(-c, App.Rotation()))


def set_articulation(yaw=0.0, pitch=0.0, doc=None, trailer=TRAILER):
    doc = doc or App.ActiveDocument
    doc.getObject(trailer).Placement = articulation(yaw, pitch)
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_hitch(doc, parent):
    grp = new_part(doc, parent, "Hitch", "tow_hitch_50mm_ball")
    add_shape(doc, grp, "hitch_plate", "hitch_top_plate_10mm", G.hitch_plate(), "hitch")
    add_shape(doc, grp, "hitch_bolts", "hitch_bolts_4xM10", G.hitch_bolts(), "zinc")
    add_shape(doc, grp, "hitch_leg", "hitch_leg_square_tube_60x60x5", G.hitch_leg(), "hitch")
    add_shape(doc, grp, "hitch_bar", "hitch_bar_square_tube_60x60x5", G.hitch_bar(), "hitch")
    add_shape(doc, grp, "hitch_gusset", "hitch_gusset_8mm", G.hitch_gusset(), "hitch")
    add_shape(doc, grp, "tow_ball", "tow_ball_50mm_bolt_on", G.tow_ball(), "steel")
    add_shape(doc, grp, "ball_stud", "tow_ball_stud_nut_M20", G.ball_stud(), "zinc")
    return grp


def build_drawbar(doc, parent, cross_y, prefix=""):
    """Drawbar, braces, coupling head and parking leg (shared with the overseeder)."""
    grp = new_part(doc, parent, prefix + "Drawbar", prefix.lower() + "drawbar_coupling")
    add_shape(doc, grp, prefix + "drawbar", "drawbar_square_tube_60x60x4", G.drawbar(cross_y), "frame")
    add_shape(doc, grp, prefix + "braces", "drawbar_braces_40x40x3", G.braces(cross_y), "frame")
    add_shape(doc, grp, prefix + "coupling", "coupling_head_50mm_ball", G.coupling_head(), "coupling")
    add_shape(doc, grp, prefix + "park_lug", "parking_leg_lug_8mm", G.park_lug(cross_y), "frame")
    add_shape(doc, grp, prefix + "park_leg", "parking_leg_40x40_stowed", G.park_leg(cross_y), "frame")
    add_shape(doc, grp, prefix + "park_pin", "parking_leg_pin_D12", G.park_pin(cross_y), "zinc")
    return grp


def build_roll_frame(doc, parent, axle_y, cross_y):
    grp = new_part(doc, parent, "Roll_frame", "roll_frame")
    add_shape(doc, grp, "side_plates", "side_plates_10mm", G.side_plates(axle_y), "frame")
    add_shape(doc, grp, "bearings", "flange_bearings_UCFL208", G.bearings(axle_y), "bearing")
    add_shape(doc, grp, "bearing_bolts", "bearing_bolts_M12", G.bearing_bolts(axle_y), "zinc")
    add_shape(doc, grp, "arms", "arms_square_tube_40x40x3", G.arms(axle_y, cross_y), "frame")
    add_shape(doc, grp, "cross_beam", "front_cross_beam_40x40x3", G.cross_beam(cross_y), "frame")
    return grp


def build_roll(doc, parent, axle_y):
    roll = new_part(doc, parent, "Roll", "roll_rotates_about_axle")
    add_shape(doc, roll, "rings", "cambridge_rings_%dx_D%d" % (P.ring_n, P.ring_od), G.rings(axle_y), "cast")
    add_shape(doc, roll, "shaft", "shaft_D40_C45", G.shaft(axle_y), "steel")
    add_shape(doc, roll, "collars", "shaft_collars_D40", G.collars(axle_y), "zinc")
    return roll


def roll_spin(angle_deg, axle_y):
    """Placement of the Roll part for a rotation about the axle (+ = rolling forward)."""
    c = V(0, axle_y, P.axle_z)
    return App.Placement(c, App.Rotation(V(1, 0, 0), -angle_deg)).multiply(App.Placement(-c, App.Rotation()))


def build_trailer(doc, parent, axle_y=P.roll_axle_y, cross_y=P.cross_y, name=TRAILER, label="roll_trailer"):
    tr = new_part(doc, parent, name, label)
    build_roll_frame(doc, tr, axle_y, cross_y)
    build_roll(doc, tr, axle_y)
    build_drawbar(doc, tr, cross_y)
    return tr


def build_into(doc, parent=None):
    """Put the hitch and the roll in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "cambridge_roll_simple")
    build_hitch(doc, root)
    build_trailer(doc, root)
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


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Cambridge roll simple"
    doc.Comment = ("Generated by build_cbr.py from cbr_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Trailer straight behind the robot; "
                   "build_cbr.set_articulation() swings it about the ball.")
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
        export_step(doc, SAVE_BASE + ".step", ROOT)
    return doc


# ---------------------------------------------------------------------
# Object lists and checks (generic: root = name of the implement part)
# ---------------------------------------------------------------------
def active_doc(doc=None, root=ROOT):
    if doc is not None:
        return doc
    d = App.ActiveDocument
    if d is not None and d.getObject(root) is not None:
        return d
    for n in App.listDocuments():
        d = App.getDocument(n)
        if d.getObject(root) is not None:
            return d
    raise RuntimeError("no document with %s open" % root)


def objects_of(doc, name):
    g = doc.getObject(name)
    if g is None:
        return []
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature" and not o.Name.startswith("anim_")]


def robot_objects(doc, root=ROOT):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in objects_of(doc, root)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None, root=ROOT):
    doc = active_doc(doc, root)
    for o in robot_objects(doc, root):
        o.ViewObject.Visibility = visible


def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def export_step(doc, path, root=ROOT):
    import Import
    objs = []
    for o in objects_of(doc, root):
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


def check_interference(doc=None, tol=1.0, root=ROOT, exclude=()):
    """Volume overlap (mm3) in the current pose: implement parts among themselves and against the robot."""
    doc = active_doc(doc, root)
    mine = [(o, global_shape(o)) for o in objects_of(doc, root) if not o.Name.startswith(tuple(exclude) or ("\0",))]
    robot = [(o, global_shape(o)) for o in robot_objects(doc, root)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


ARTICULATION_POSES = [(y, p) for y in (-75.0, -45.0, -20.0, 20.0, 45.0, 75.0) for p in (-8.0, 0.0, 8.0)]


def check_poses(doc=None, poses=None, tol=1.0, root=ROOT, trailer=TRAILER):
    """Interference of the trailer against the hitch and the robot over yaw +-75 and pitch +-8 degrees (bumps,
    a hollow). Only the pairs that move relative to each other. Must be empty."""
    doc = active_doc(doc, root)
    moving = objects_of(doc, trailer)
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, root) if o.Name not in names]
    fixed += [(o, global_shape(o)) for o in robot_objects(doc, root)]
    out = {}
    for yaw, pitch in poses or ARTICULATION_POSES:
        set_articulation(yaw, pitch, doc, trailer)
        mv = [(o, global_shape(o)) for o in moving]
        hits = _overlaps([(a, b) for a in mv for b in fixed], tol)
        if hits:
            out[(yaw, pitch)] = hits
    set_articulation(0.0, 0.0, doc, trailer)
    return out


CLEARANCE_TARGETS = ("RL_tire", "RR_tire", "RL_side_l", "RL_side_r", "RR_side_l", "RR_side_r", "RL_top_plate",
                     "RR_top_plate", "hitch_bar", "hitch_gusset", "hitch_leg")


def clearance(doc=None, root=ROOT, trailer=TRAILER, yaws=(0.0, 30.0, 60.0, 90.0)):
    """Smallest distance (mm) of the trailer (drawbar group only: the rest is far away) to the rear tyres, the
    wheel brackets and the hitch bracket, per yaw."""
    doc = active_doc(doc, root)
    robot = [global_shape(doc.getObject(n)) for n in CLEARANCE_TARGETS if doc.getObject(n) is not None]
    moving = [o for o in objects_of(doc, trailer) if o.Name.endswith(("coupling", "drawbar", "braces", "park_leg",
                                                                      "park_lug", "park_pin"))]
    out = {}
    for yaw in yaws:
        set_articulation(yaw, 0.0, doc, trailer)
        best = (1e9, None)
        for o in moving:
            s = global_shape(o)
            for t in robot:
                if s.BoundBox.isValid() and t.BoundBox.isValid():
                    d = s.distToShape(t)[0]
                    if d < best[0]:
                        best = (d, o.Name)
        out[yaw] = (round(best[0], 1), best[1])
    set_articulation(0.0, 0.0, doc, trailer)
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
MASS_FIXED = {"bearings": 2 * P.bearing_kg, "coupling": 3.5, "tow_ball": 1.6}
DENSITY = (("rings", P.cast_iron),)


def _mass_cg(obj, fixed=None, density=None):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key, m in (fixed or MASS_FIXED).items():
        if obj.Name.startswith(key):
            return m, cg
    dens = P.steel
    for key, d in (density or DENSITY):
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def sum_mass(objs, fixed=None, density=None):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o, fixed, density)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def ball_load(mass, cg_y, axle_y):
    """Vertical load (N) on the tow ball of a trailer that rests on the ball and on the roll (or wheels) at axle_y."""
    return mass * 9.81 * (cg_y - axle_y) / (P.ball[1] - axle_y)


def mass_properties(doc=None):
    doc = active_doc(doc)
    tr = objects_of(doc, TRAILER)
    names = {o.Name for o in tr}
    m, c = sum_mass(tr)
    mh, ch = sum_mass([o for o in objects_of(doc, ROOT) if o.Name not in names])
    mr, _ = sum_mass(objects_of(doc, "Roll"))
    ring_kg = P.ring_volume() * P.cast_iron
    return {"trailer_kg": round(m, 1), "trailer_cg": (round(c.x), round(c.y), round(c.z)),
            "roll_kg": round(mr, 1), "ring_kg": round(ring_kg, 2), "hitch_kg": round(mh, 1),
            "ball_load_N": round(ball_load(m, c.y, P.roll_axle_y)),
            "roll_line_load_kg_per_m": round((m - ball_load(m, c.y, P.roll_axle_y) / 9.81) / 1.0, 1)}


def size(doc=None, root=ROOT):
    doc = active_doc(doc, root)
    bb = None
    for o in objects_of(doc, root):
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
    tgt = V(*target) if target is not None else V(0, -1200, 300)
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


def save_view(name, direction, target=None, height=None, up=(0.0, 0.0, 1.0), size_px=(1600, 1100),
              folder=PREVIEW_DIR):
    import FreeCADGui as Gui
    Gui.updateGui()
    set_camera(direction, target, height, up)
    Gui.updateGui()
    view = set_camera(direction, target, height, up)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    view.saveImage(path, size_px[0], size_px[1], "White")
    return path


GROUND = "render_floor"


def add_floor(doc, y=(-2600.0, 1000.0), x=(-1100.0, 1100.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.47, 0.62, 0.30)
    obj.ViewObject.Transparency = 20
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_floor(doc)
    out.append(save_view("1_iso_on_robot.png", (1.0, 1.2, -0.7), target=(0, -900, 300)))
    out.append(save_view("2_side.png", (1.0, 0.0, 0.0), target=(0, -900, 350), height=1500))
    remove(doc, [GROUND])
    set_articulation(45.0, 0.0, doc)
    out.append(save_view("3_top_turn_45deg.png", (0.0, 0.0, -1.0), target=(-300, -1100, 0), up=(0.0, 1.0, 0.0),
                         height=3200))
    set_articulation(0.0, 0.0, doc)
    set_robot_visible(False, doc)
    out.append(save_view("4_roll_iso_rear.png", (-1.0, 1.0, -0.6), target=(0, -1500, 250)))
    out.append(save_view("5_hitch_detail.png", (1.0, 0.7, -0.45), target=(0, -760, 380), height=750))
    set_robot_visible(True, doc)
    App.closeDocument(doc.Name)
    build()
    return out
