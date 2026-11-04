"""Model of the belly-mounted flail mulcher on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_flm
    build_flm.build()                      # saves FCStd and STEP
    build_flm.set_lift(100)                # housing up 100 mm (transport); 0 = work
    build_flm.set_rotor(30)                # rotor angle
    build_flm.check_interference()         # must be empty
    build_flm.check_poses()                # lift 0 / 100 and front wheels at +-30 degrees: empty
    build_flm.check_holes()                # every rail bolt in a lower-beam grid hole
    build_flm.mass_properties()
    build_flm.render_all()
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import flm_params as P
import flm_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Flail_Mulcher"
SAVE_BASE = os.path.join(FOLDER, "Flail_Mulcher")
ROOT = "Flail_mulcher"

COLOR = {"frame": (0.93, 0.42, 0.08), "zinc": (0.82, 0.84, 0.87), "housing": (0.15, 0.45, 0.20),
         "rubber": (0.08, 0.08, 0.08), "steel": (0.55, 0.56, 0.58), "knife": (0.30, 0.30, 0.33),
         "motor": (0.12, 0.12, 0.13), "actuator": (0.25, 0.25, 0.28), "guard": (0.95, 0.80, 0.10)}


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


def build_into(doc, parent=None, lift=0.0):
    root = new_part(doc, parent, ROOT, "flail_mulcher_belly_simple")
    mt = new_part(doc, root, "flm_Mount", "belly_rails_brackets_actuators")
    add_shape(doc, mt, "flm_rails", "belly_rails_40x40x3", G.rails(), "frame")
    add_shape(doc, mt, "flm_rail_bolts", "rail_bolts_8xM10", G.rail_bolts(), "zinc")
    add_shape(doc, mt, "flm_side_brackets", "guide_sleeves_actuator_brackets_4mm", G.side_brackets(), "frame")
    add_shape(doc, mt, "flm_act_bodies", "actuators_24V_1500N_stroke100_2x", G.actuator_bodies(), "actuator")
    lg = new_part(doc, root, "flm_Lift", "mulcher_moves_up_for_transport", App.Placement(V(0, 0, lift), App.Rotation()))
    add_shape(doc, lg, "flm_act_rods", "actuator_rods", G.actuator_rods(), "zinc")
    add_shape(doc, lg, "flm_guide_posts", "guide_posts_30x30x2_4x", G.guide_posts(), "zinc")
    add_shape(doc, lg, "flm_top_lugs", "rod_lugs_post_feet", G.top_lugs(), "housing")
    add_shape(doc, lg, "flm_housing", "housing_top_3mm_sides_6mm", G.housing(), "housing")
    add_shape(doc, lg, "flm_skids", "front_skids_8mm", G.skids(), "steel")
    add_shape(doc, lg, "flm_front_flap", "front_rubber_flap_6mm", G.front_flap(), "rubber")
    add_shape(doc, lg, "flm_shear_bar", "shear_bar_angle_40x6", G.shear_bar(), "steel")
    add_shape(doc, lg, "flm_bearings", "rotor_roller_bearings", G.bearings(), "zinc")
    add_shape(doc, lg, "flm_belt_guard", "belt_guard_poly_V", G.belt_guard(), "guard")
    add_shape(doc, lg, "flm_motor", "motor_48V_2kW", G.motor(), "motor")
    add_shape(doc, lg, "flm_roller", "rear_roller_D140", G.roller(), "steel")
    rt = new_part(doc, lg, "flm_Rotor", "flail_rotor_turns_about_x")
    add_shape(doc, rt, "flm_rotor_tube", "rotor_tube_D108x6_shaft_D35", G.rotor_tube(), "steel")
    add_shape(doc, rt, "flm_lugs", "shackle_lugs", G.lugs(), "steel")
    add_shape(doc, rt, "flm_pins", "shackle_pins_D12", G.pins(), "zinc")
    add_shape(doc, rt, "flm_flails", "Y_knives_40x5", G.flails(), "knife")
    return root


def set_lift(dz, doc=None):
    doc = active_doc(doc)
    doc.getObject("flm_Lift").Placement = App.Placement(V(0, 0, dz), App.Rotation())
    doc.recompute()


def set_rotor(angle, doc=None):
    doc = active_doc(doc)
    doc.getObject("flm_Rotor").Placement = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), angle),
                                                         V(0, P.rotor_y, P.rotor_z))
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


def build(save=True, show_robot=False, step=True, lift=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Flail mulcher simple"
    doc.Comment = ("Generated by build_flm.py from flm_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, lift)
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


_J = [("rail_bolts", "rails"), ("side_brackets", "rails"), ("act_bodies", "side_brackets"), ("act_rods", "act_bodies"),
      ("act_rods", "top_lugs"), ("guide_posts", "top_lugs"), ("guide_posts", "side_brackets"), ("top_lugs", "housing"),
      ("guide_posts", "housing"), ("act_rods", "housing"), ("skids", "housing"), ("front_flap", "housing"),
      ("shear_bar", "housing"), ("bearings", "housing"), ("belt_guard", "housing"), ("motor", "housing"),
      ("motor", "belt_guard"), ("roller", "housing"), ("roller", "bearings"), ("rotor_tube", "housing"),
      ("rotor_tube", "bearings"), ("rotor_tube", "belt_guard"), ("lugs", "rotor_tube"), ("pins", "lugs"),
      ("pins", "flails"), ("flails", "lugs")]
JOINTS = {("flm_" + a, "flm_" + b) for a, b in _J}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x in ("flm_rail_bolts", "flm_rails") and y.startswith("lower_beam"):
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


def _steer(doc, st):
    for name in ("FL_steered", "FR_steered"):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), st))
    doc.recompute()


def check_poses(doc=None, tol=1.0):
    """Lifted (transport) against the mount and the robot; work and lifted against the front wheels at +-30 deg;
    rotor angles against the housing."""
    doc = active_doc(doc)
    out = {}
    moving = objects_of(doc, "flm_Lift")
    mn = {o.Name for o in moving}
    for dz in (0.0, P.lift):
        set_lift(dz, doc)
        for st in (-P.robot_steer_max, 0.0, P.robot_steer_max):
            _steer(doc, st)
            fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in mn]
            mv = [(o, global_shape(o)) for o in moving]
            hits = _overlaps([(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
            if hits:
                out["lift_%g_steer_%+d" % (dz, st)] = hits
    _steer(doc, 0.0)
    set_lift(0.0, doc)
    rotor = objects_of(doc, "flm_Rotor")
    rn = {o.Name for o in rotor}
    housing = [(o, global_shape(o)) for o in moving if o.Name not in rn]
    for a in (7.5, 22.5, 45.0):
        set_rotor(a, doc)
        rv = [(o, global_shape(o)) for o in rotor]
        hits = _overlaps([(p, q) for p in rv for q in housing if not _joint(p[0].Name, q[0].Name)], tol)
        if hits:
            out["rotor_%g" % a] = hits
    set_rotor(0.0, doc)
    return out


def check_holes(doc=None):
    doc = active_doc(doc)
    beams = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith("lower_beam")]
    bad = []
    for (x, y) in G.RAIL_BOLTS:
        rod = Part.makeCylinder(4.5, 80.0, V(x, y, 600.0))
        v = sum(rod.common(b).Volume for b in beams)
        if v > 1.0:
            bad.append((x, y, round(v)))
    return bad


def ground_contact(doc=None):
    doc = active_doc(doc)
    out = {}
    for dz in (0.0, P.lift):
        set_lift(dz, doc)
        out["lift_%g" % dz] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1)
                               for n in ("flm_roller", "flm_flails", "flm_skids", "flm_front_flap")}
    set_lift(0.0, doc)
    return out


DENSITY = {"flm_front_flap": P.rubber, "flm_belt_guard": 0.25 * P.steel}
MASS_FIXED = {"flm_motor": P.motor_kg, "flm_act_bodies": 2 * 2.2}


def mass_properties(doc=None):
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "flm_Lift", "flm_Rotor"):
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
    gr = doc.addObject("Part::Feature", "render_grass")
    gr.Shape = G.grass(-2400.0, 1600.0, cut=P.rotor_y)
    gr.ViewObject.ShapeColor = (0.30, 0.58, 0.22)
    set_rotor(20.0, doc)
    out.append(save_view("1_iso_mulching.png", (-1.0, 1.0, -0.6), target=(0, -300, 300), height=2600))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, 0, 400), height=1900))
    doc.removeObject(gr.Name)
    set_lift(P.lift, doc)
    out.append(save_view("3_side_lifted.png", (1.0, 0.0, 0.0), target=(0, 0, 400), height=1900))
    set_lift(0.0, doc)
    set_robot_visible(False, doc)
    doc.getObject("flm_housing").ViewObject.Transparency = 75
    out.append(save_view("4_rotor_in_housing.png", (-0.8, -0.7, 0.5), target=(0, 0, 250), height=1100))
    doc.getObject("flm_housing").ViewObject.Transparency = 0
    out.append(save_view("5_mount_and_drive.png", (-0.9, 0.9, -0.7), target=(100, 0, 450), height=1300))
    App.closeDocument(doc.Name)
    build()
    return out
