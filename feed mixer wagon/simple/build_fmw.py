"""Model of the feed mixing and distribution wagon on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_fmw
    build_fmw.build()                      # saves FCStd and STEP
    build_fmw.set_auger(30)                # auger angle
    build_fmw.set_door(1.0)                # door open (0 .. 1)
    build_fmw.check_interference()         # must be empty
    build_fmw.check_poses()                # door open, auger angles, front wheels at +-30 deg: empty
    build_fmw.check_holes()                # every cross-tube bolt in an upper-beam grid hole
    build_fmw.mass_properties()
    build_fmw.render_all()
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fmw_params as P
import fmw_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Feed_Mixer_Wagon"
SAVE_BASE = os.path.join(FOLDER, "Feed_Mixer_Wagon")
ROOT = "Feed_mixer_wagon"

COLOR = {"frame": (0.93, 0.42, 0.08), "zinc": (0.82, 0.84, 0.87), "bin": (0.10, 0.35, 0.65),
         "steel": (0.55, 0.56, 0.58), "cell": (0.75, 0.76, 0.78), "box": (0.20, 0.20, 0.22),
         "motor": (0.12, 0.12, 0.13), "actuator": (0.25, 0.25, 0.28), "feed": (0.62, 0.55, 0.25)}


def new_part(doc, parent, name, label, placement=None):
    part = doc.addObject("App::Part", name)
    part.Label = label
    if placement is not None:
        part.Placement = placement
    if parent is not None:
        parent.addObject(part)
    return part


def add_shape(doc, parent, name, label, shape, color, visible=True):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    parent.addObject(obj)
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = COLOR[color]
        obj.ViewObject.Visibility = visible
    return obj


def build_into(doc, parent=None):
    root = new_part(doc, parent, ROOT, "feed_mixer_wagon_simple")
    fr = new_part(doc, root, "fmw_Frame", "cross_tubes_load_cells")
    add_shape(doc, fr, "fmw_cross_tubes", "cross_tubes_60x40x3", G.cross_tubes(), "frame")
    add_shape(doc, fr, "fmw_cross_bolts", "cross_tube_bolts_8xM10", G.cross_bolts(), "zinc")
    add_shape(doc, fr, "fmw_load_cells", "load_cells_single_point_300kg_4x", G.load_cells(), "cell")
    add_shape(doc, fr, "fmw_junction_box", "load_cell_junction_box_indicator", G.junction_box(), "box")
    bn = new_part(doc, root, "fmw_Bin", "weighed_bin")
    add_shape(doc, bn, "fmw_sub_frame", "sub_frame_40x40x3", G.sub_frame(), "frame")
    add_shape(doc, bn, "fmw_floor", "floor_6mm", G.floor(), "bin")
    add_shape(doc, bn, "fmw_bin_shell", "bin_cone_2mm_0_33m3", G.bin_shell(), "bin")
    add_shape(doc, bn, "fmw_door_guides", "door_guides", G.door_guides(), "frame")
    add_shape(doc, bn, "fmw_act_bracket", "door_actuator_bracket", G.act_bracket(), "frame")
    add_shape(doc, bn, "fmw_act_body", "door_actuator_24V_stroke_200", G.actuator_body(), "actuator")
    add_shape(doc, bn, "fmw_chute", "discharge_chute_3mm", G.chute(), "bin")
    add_shape(doc, bn, "fmw_gearbox", "planetary_gearbox_i100", G.gearbox(), "motor")
    add_shape(doc, bn, "fmw_motor", "motor_48V_2kW", G.motor(), "motor")
    dr = new_part(doc, bn, "fmw_Door", "door_slides_up")
    add_shape(doc, dr, "fmw_door", "sliding_door_3mm", G.door(), "steel")
    add_shape(doc, dr, "fmw_door_rod", "door_actuator_rod_lug", G.door_actuator_rod(), "zinc")
    au = new_part(doc, bn, "fmw_Auger", "auger_turns_about_z")
    add_shape(doc, au, "fmw_shaft", "auger_shaft_D60", G.shaft(), "steel")
    add_shape(doc, au, "fmw_flight", "conical_flight_8mm_2_turns", G.flight(), "steel")
    add_shape(doc, au, "fmw_knives", "knives_2x", G.knives(), "zinc")
    return root


def set_auger(angle, doc=None):
    doc = active_doc(doc)
    doc.getObject("fmw_Auger").Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle),
                                                         V(P.bin_c[0], P.bin_c[1], 0))
    doc.recompute()


def set_door(frac, doc=None):
    """Door 0 = closed .. 1 = open: slides door_lift up along the cone wall (actuator drawn with the door group)."""
    doc = active_doc(doc)
    doc.getObject("fmw_Door").Placement = App.Placement(G.slide_dir() * (frac * P.door_lift), App.Rotation())
    doc.recompute()


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
    doc.Label = "Feed mixer wagon simple"
    doc.Comment = ("Generated by build_fmw.py from fmw_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
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
    if DOC_NAME in App.listDocuments():
        return App.getDocument(DOC_NAME)
    raise RuntimeError("no document %s open" % DOC_NAME)


def objects_of(doc, name):
    g = doc.getObject(name)
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []


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


_J = [("cross_bolts", "cross_tubes"), ("load_cells", "cross_tubes"), ("load_cells", "sub_frame"),
      ("junction_box", "sub_frame"), ("floor", "sub_frame"), ("bin_shell", "floor"), ("door_guides", "bin_shell"),
      ("door", "door_guides"), ("act_bracket", "bin_shell"), ("act_body", "act_bracket"),
      ("door_rod", "act_body"), ("door_rod", "door"), ("chute", "bin_shell"), ("chute", "floor"), ("chute", "sub_frame"),
      ("gearbox", "floor"), ("motor", "gearbox"), ("shaft", "gearbox"), ("shaft", "floor"), ("flight", "shaft"),
      ("knives", "flight"), ("chute", "door_guides"), ("junction_box", "cross_tubes")]
JOINTS = {("fmw_" + a, "fmw_" + b) for a, b in _J}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x == "fmw_cross_bolts" and y.startswith("upper_beam"):
            return True
    return False


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        if not sa.BoundBox.intersect(sb.BoundBox):
            continue
        vol = sa.common(sb).Volume
        if vol > tol:
            hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    doc = active_doc(doc)
    out = {}
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    for st in (-P.robot_steer_max, P.robot_steer_max):
        for name in ("FL_steered", "FR_steered"):
            o = doc.getObject(name)
            if o is not None:
                o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), st))
        doc.recompute()
        front = [(o, global_shape(o)) for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
        hits = _overlaps([(a, b) for a in mine for b in front], tol)
        if hits:
            out["steer_%+d" % st] = hits
    for name in ("FL_steered", "FR_steered"):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement()
    doc.recompute()
    for grp, fn, vals in (("fmw_Door", set_door, (1.0,)), ("fmw_Auger", set_auger, (5.0, 10.0))):
        mv_objs = objects_of(doc, grp)
        names = {o.Name for o in mv_objs}
        for v in vals:
            fn(v, doc)
            mv = [(o, global_shape(o)) for o in mv_objs]
            fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
            hits = _overlaps([(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
            if hits:
                out["%s_%g" % (grp, v)] = hits
        fn(0.0, doc)
    return out


def check_holes(doc=None):
    doc = active_doc(doc)
    beams = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith("upper_beam")]
    bad = []
    for (x, y) in G.BOLTS:
        rod = Part.makeCylinder(4.5, 60.0, V(x, y, 650.0))
        v = sum(rod.common(b).Volume for b in beams)
        if v > 1.0:
            bad.append((x, y, round(v)))
    return bad


DENSITY = {}
MASS_FIXED = {"fmw_motor": 11.0, "fmw_gearbox": 14.0, "fmw_load_cells": 4 * 0.6, "fmw_junction_box": 1.5,
              "fmw_act_body": 2.0}


def mass_properties(doc=None):
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "fmw_Bin"):
        m, c = 0.0, V(0, 0, 0)
        for o in objects_of(doc, name):
            s = global_shape(o)
            mo = MASS_FIXED.get(o.Name, s.Volume * DENSITY.get(o.Name, P.steel))
            m += mo
            c += s.BoundBox.Center * mo
        c = c * (1.0 / m) if m > 0 else c
        out[name.lower() + "_kg"] = round(m, 1)
        out[name.lower() + "_cg"] = (round(c.x), round(c.y), round(c.z))
    return out


def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.getDocument(DOC_NAME).ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, 0, 800)
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


def render_all():
    out = []
    doc = build(save=False, show_robot=True, step=False)
    sc = []
    for name, shape, col in (("render_fence", G.fence(-2500.0, 2500.0), (0.55, 0.56, 0.58)),
                             ("render_feed_row", G.feed_row(-2500.0, 0.0), COLOR["feed"]),
                             ("render_feed", G.feed_fill(0.6), COLOR["feed"])):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = col
        sc.append(o)
    set_door(1.0, doc)
    out.append(save_view("1_iso_feeding_along_fence.png", (-1.0, 1.0, -0.7), target=(300, -300, 700), height=3000))
    out.append(save_view("2_front_discharge.png", (0.0, -1.0, 0.0), target=(250, 0, 800), height=2000))
    for o in sc:
        doc.removeObject(o.Name)
    set_door(0.0, doc)
    out.append(save_view("3_side.png", (-1.0, 0.0, 0.0), target=(0, 0, 850), height=1900))
    set_robot_visible(False, doc)
    doc.getObject("fmw_bin_shell").ViewObject.Transparency = 70
    out.append(save_view("4_auger_in_bin.png", (-0.8, -1.0, -0.6), target=(0, -50, 1000), height=1300))
    doc.getObject("fmw_bin_shell").ViewObject.Transparency = 0
    out.append(save_view("5_weighing_frame_below.png", (-0.8, -1.0, 0.6), target=(0, -50, 760), height=1300))
    App.closeDocument(doc.Name)
    build()
    return out
