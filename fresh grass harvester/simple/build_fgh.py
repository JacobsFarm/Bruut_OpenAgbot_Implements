"""Model of the fresh grass harvester (zero grazing) on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_fgh
    build_fgh.build()                      # saves FCStd and STEP
    build_fgh.set_tip(55)                  # container tipped to the left (degrees)
    build_fgh.set_auger(30)                # auger angle
    build_fgh.check_interference()         # must be empty
    build_fgh.check_poses()                # container tipped, auger, front wheels at +-30 deg: empty
    build_fgh.check_holes()                # every bolt in a beam grid hole
    build_fgh.mass_properties()
    build_fgh.render_all()
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fgh_params as P
import fgh_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Fresh_Grass_Harvester"
SAVE_BASE = os.path.join(FOLDER, "Fresh_Grass_Harvester")
ROOT = "Fresh_grass_harvester"

COLOR = {"frame": (0.93, 0.42, 0.08), "zinc": (0.82, 0.84, 0.87), "green": (0.15, 0.50, 0.25),
         "steel": (0.55, 0.56, 0.58), "belt": (0.10, 0.10, 0.10), "knife": (0.75, 0.76, 0.78),
         "motor": (0.12, 0.12, 0.13), "actuator": (0.25, 0.25, 0.28), "grass": (0.35, 0.65, 0.25)}


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
    root = new_part(doc, parent, ROOT, "fresh_grass_harvester_simple")
    fr = new_part(doc, root, "fgh_Front", "front_arms_cutter_bar_auger")
    add_shape(doc, fr, "fgh_arms", "front_arms_40x60x3", G.arms(), "frame")
    add_shape(doc, fr, "fgh_arm_bolts", "arm_bolts_4xM10", G.arm_bolts(), "zinc")
    add_shape(doc, fr, "fgh_drop_plates", "drop_plates_8mm", G.drop_plates(), "frame")
    add_shape(doc, fr, "fgh_trough", "auger_trough_3mm", G.trough(), "green")
    add_shape(doc, fr, "fgh_cutter_bar", "sickle_bar_1200_sections_guards", G.cutter_bar(), "knife")
    add_shape(doc, fr, "fgh_skids", "skids", G.skids(), "steel")
    add_shape(doc, fr, "fgh_sickle_drive", "sickle_crank_box_motor", G.sickle_drive(), "motor")
    au = new_part(doc, fr, "fgh_Auger", "cross_auger_turns_about_x")
    add_shape(doc, au, "fgh_auger_shaft", "auger_shaft_D40", G.auger_shaft(), "steel")
    add_shape(doc, au, "fgh_auger_flight", "auger_flight_D200_pitch_200", G.auger_flight(), "steel")
    el = new_part(doc, root, "fgh_Elevator", "slatted_elevator_right")
    add_shape(doc, el, "fgh_elev_channel", "elevator_channel_3mm", G.elevator_channel(), "green")
    add_shape(doc, el, "fgh_belt", "slatted_belt", G.belt(), "belt")
    add_shape(doc, el, "fgh_rollers", "elevator_rollers_D100", G.rollers(), "steel")
    add_shape(doc, el, "fgh_elev_motor", "elevator_motor_24V", G.elevator_motor(), "motor")
    add_shape(doc, el, "fgh_spout", "spout", G.spout(), "green")
    add_shape(doc, el, "fgh_stay", "elevator_stay_D30", G.stay(), "frame")
    ct = new_part(doc, root, "fgh_Mount", "container_mount")
    add_shape(doc, ct, "fgh_cross_tubes", "cross_tubes_60x40x3", G.cross_tubes(), "frame")
    add_shape(doc, ct, "fgh_cross_bolts", "cross_tube_bolts_8xM10", G.cross_bolts(), "zinc")
    add_shape(doc, ct, "fgh_hinge_brackets", "hinge_brackets_8mm", G.hinge_brackets(), "frame")
    add_shape(doc, ct, "fgh_hinge_pins", "hinge_pins_D16", G.hinge_pins(), "zinc")
    add_shape(doc, ct, "fgh_tip_actuators", "tip_actuators_24V_2x", G.tip_actuators(), "actuator")
    add_shape(doc, ct, "fgh_ballast", "rear_ballast_60kg", G.ballast(), "steel")
    tp = new_part(doc, ct, "fgh_Tip", "container_tips_about_the_left_hinge")
    add_shape(doc, tp, "fgh_tip_frame", "tip_frame_40x40x3", G.tip_frame(), "frame")
    add_shape(doc, tp, "fgh_container", "container_2mm_0_41m3", G.container(), "green")
    return root


def set_tip(deg, doc=None):
    """Container tipped to the left about the hinge (x -455). The actuators pivot; they are not moved in the model."""
    doc = active_doc(doc)
    hx, hz = P.hinge
    doc.getObject("fgh_Tip").Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 1, 0), -deg), V(hx, 0, hz))
    doc.recompute()


def set_auger(angle, doc=None):
    doc = active_doc(doc)
    doc.getObject("fgh_Auger").Placement = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), angle),
                                                         V(0, P.auger_y, P.auger_z))
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
    doc.Label = "Fresh grass harvester simple"
    doc.Comment = ("Generated by build_fgh.py from fgh_params.py. Robot coordinates: x = right, y = driving direction "
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


_J = [("arm_bolts", "arms"), ("drop_plates", "arms"), ("drop_plates", "trough"), ("cutter_bar", "trough"),
      ("skids", "cutter_bar"), ("skids", "trough"), ("sickle_drive", "trough"), ("sickle_drive", "cutter_bar"),
      ("auger_shaft", "trough"), ("auger_flight", "auger_shaft"), ("elev_channel", "trough"), ("belt", "rollers"),
      ("rollers", "elev_channel"), ("elev_motor", "elev_channel"), ("elev_motor", "rollers"), ("spout", "elev_channel"),
      ("stay", "elev_channel"), ("stay", "cross_tubes"), ("cross_bolts", "cross_tubes"), ("hinge_brackets", "cross_tubes"),
      ("hinge_pins", "hinge_brackets"), ("hinge_pins", "tip_frame"), ("tip_actuators", "cross_tubes"),
      ("tip_actuators", "container"), ("tip_frame", "container"), ("tip_frame", "cross_tubes"),
      ("auger_flight", "elev_channel"), ("auger_shaft", "elev_channel"), ("ballast", "cross_tubes")]
JOINTS = {("fgh_" + a, "fgh_" + b) for a, b in _J}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x == "fgh_cross_bolts" and y.startswith("upper_beam"):
            return True
        if x in ("fgh_arm_bolts", "fgh_arms") and y.startswith("lower_beam"):
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
    skip = {"fgh_tip_actuators"}            # they pivot with the container (not moved in the model)
    for grp, fn, vals in (("fgh_Tip", set_tip, (25.0, P.tip_max)), ("fgh_Auger", set_auger, (7.5,))):
        mv_objs = objects_of(doc, grp)
        names = {o.Name for o in mv_objs}
        for v in vals:
            fn(v, doc)
            mv = [(o, global_shape(o)) for o in mv_objs]
            fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc)
                     if o.Name not in names and o.Name not in skip]
            hits = _overlaps([(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
            if hits:
                out["%s_%g" % (grp, v)] = hits
        fn(0.0, doc)
    return out


def check_holes(doc=None):
    doc = active_doc(doc)
    bad = []
    upper = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith("upper_beam")]
    for (x, y) in G.BOLTS:
        rod = Part.makeCylinder(4.5, 60.0, V(x, y, 650.0))
        v = sum(rod.common(b).Volume for b in upper)
        if v > 1.0:
            bad.append(("upper", x, y, round(v)))
    lower = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith("lower_beam")]
    for (x, y) in G.ARM_BOLTS:
        rod = Part.makeCylinder(4.5, 80.0, V(x, y, 600.0))
        v = sum(rod.common(b).Volume for b in lower)
        if v > 1.0:
            bad.append(("lower", x, y, round(v)))
    return bad


DENSITY = {"fgh_belt": 1.2e-6}
MASS_FIXED = {"fgh_sickle_drive": 6.0, "fgh_elev_motor": 4.0, "fgh_tip_actuators": 2 * 2.5}


def mass_properties(doc=None):
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "fgh_Tip", "fgh_Front", "fgh_Elevator"):
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
    field = doc.addObject("Part::Feature", "render_field")
    field.Shape = G.grass_field(-2600.0, 2600.0, P.bar_y[1])
    field.ViewObject.ShapeColor = COLOR["grass"]
    load = doc.addObject("Part::Feature", "render_load")
    load.Shape = G.grass_load(0.6)
    load.ViewObject.ShapeColor = COLOR["grass"]
    set_auger(20.0, doc)
    out.append(save_view("1_iso_mowing.png", (-1.0, -1.1, -0.7), target=(150, 300, 600), height=3300))
    doc.removeObject(field.Name)
    out.append(save_view("2_side.png", (-1.0, 0.0, 0.0), target=(150, 250, 750), height=2600))
    doc.removeObject(load.Name)
    set_tip(P.tip_max, doc)
    out.append(save_view("3_rear_tipped.png", (0.0, 1.0, 0.0), target=(0, 0, 900), height=2400))
    set_tip(0.0, doc)
    set_robot_visible(False, doc)
    out.append(save_view("4_cutter_auger_elevator.png", (-0.7, -1.0, -0.6), target=(250, 800, 300), height=1900))
    out.append(save_view("5_top.png", (0.0, 0.0, -1.0), target=(150, 250, 0), up=(0.0, 1.0, 0.0), height=2800))
    App.closeDocument(doc.Name)
    build()
    return out
