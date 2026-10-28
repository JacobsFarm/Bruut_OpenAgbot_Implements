"""Model of the grass meter / crop scanner on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_gmt
    build_gmt.build()                      # saves FCStd and STEP (plate on a 60 mm sward)
    build_gmt.set_height(250)              # compressed sward height under the plate; 250 = lifted
    build_gmt.check_interference()         # overlap (must be empty)
    build_gmt.check_poses()                # plate heights and steering +-30 (must be empty)
    build_gmt.clearance()                  # boom to the steered front tyres, plate to the rear tyres
    build_gmt.mass_properties()
    build_gmt.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import gmt_params as P
import gmt_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Grass_Meter"
SAVE_BASE = os.path.join(FOLDER, "Grass_Meter")
ROOT = "Grass_meter"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "sensor": (0.15, 0.35, 0.75),
    "box": (0.20, 0.45, 0.25),
    "plate": (0.95, 0.85, 0.20),
    "motor": (0.25, 0.26, 0.28),
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







def build_boom(doc, parent):
    grp = new_part(doc, parent, "Boom", "front_sensor_boom")
    add_shape(doc, grp, "brackets", "boom_brackets_flat_8mm_2x", G.brackets(), "frame")
    add_shape(doc, grp, "bracket_bolts", "bracket_bolts_M10_4x", G.bracket_bolts(), "zinc")
    add_shape(doc, grp, "boom", "boom_40x40x3_L%d" % (2 * P.boom_x), G.boom(), "frame")
    add_shape(doc, grp, "sensor_brackets", "sensor_brackets_5mm", G.sensor_brackets(), "zinc")
    add_shape(doc, grp, "ndvi_sensors", "active_ndvi_sensors_2x", G.ndvi_sensors(), "sensor")
    add_shape(doc, grp, "lidar", "lidar_distance_sensor", G.lidar(), "sensor")
    mast, cam = G.camera()
    add_shape(doc, grp, "cam_mast", "camera_mast_D25", mast, "zinc")
    add_shape(doc, grp, "camera", "rgb_camera", cam, "sensor")
    add_shape(doc, grp, "logger", "logger_rtk_box", G.logger(), "box")
    return grp


def build_plate_meter(doc, parent, h=P.sward_h):
    grp = new_part(doc, parent, "PlateMeter", "sledge_plate_meter")
    add_shape(doc, grp, "bearer", "bearer_40x40x3", G.bearer(), "frame")
    add_shape(doc, grp, "bearer_bolts", "bearer_bolts_M10_4x", G.bearer_bolts(), "zinc")
    add_shape(doc, grp, "post", "post_40x40x3_cap_lug", G.post(), "frame")
    add_shape(doc, grp, "post_bolts", "post_bolts_M8_2x", G.post_bolts(), "zinc")
    add_shape(doc, grp, "encoder", "angle_sensor_upper_pivot", G.encoder(), "sensor")
    mv = new_part(doc, grp, "PlateMoving", "arms_and_plate")
    add_shape(doc, mv, "arms", "parallel_arms_20x20x2_4x", G.arms(h), "frame")
    add_shape(doc, mv, "arm_pins", "arm_pins_D10", G.arm_pins(h), "zinc")
    pl, brk = G.plate(h)
    add_shape(doc, mv, "plate", "plate_316x316_PE_5mm", pl, "plate")
    add_shape(doc, mv, "plate_bracket", "plate_bracket_6mm", brk, "zinc")
    body, rod, _ = G.actuator(h)
    add_shape(doc, mv, "act_body", "lift_actuator_24V_200N", body, "motor")
    add_shape(doc, mv, "act_rod", "lift_actuator_rod_slotted", rod, "zinc")
    return grp


def build_into(doc, parent=None, h=P.sward_h):
    root = new_part(doc, parent, ROOT, "grass_meter_simple")
    build_boom(doc, root)
    build_plate_meter(doc, root, h)
    return root


def set_height(h=P.sward_h, doc=None):
    """Compressed sward height under the plate (mm); P.lift_h = lifted for transport."""
    doc = active_doc(doc)
    doc.getObject("arms").Shape = G.arms(h)
    doc.getObject("arm_pins").Shape = G.arm_pins(h)
    pl, brk = G.plate(h)
    doc.getObject("plate").Shape = pl
    doc.getObject("plate_bracket").Shape = brk
    body, rod, _ = G.actuator(h)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod


def build_robot(doc, steer=0.0):
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, steer if tag in ("FL", "FR") else 0.0)
    return robot


def set_steering(deg, doc=None):
    doc = active_doc(doc)
    for n in ("FL_steered", "FR_steered"):
        o = doc.getObject(n)
        if o is not None:
            pl = o.Placement
            o.Placement = App.Placement(pl.Base, App.Rotation(V(0, 0, 1), deg))


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Grass meter simple"
    doc.Comment = ("Generated by build_gmt.py from gmt_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Plate on a sward of %d mm; set_height() moves it." % P.sward_h)
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




# bolts and pins in their holes, sensors on their brackets, the actuator in its lug: by design
JOINTS = {("bracket_bolts", "brackets"), ("bearer_bolts", "bearer"), ("post_bolts", "post"), ("post_bolts", "bearer"),
          ("arm_pins", "arms"), ("arm_pins", "post"), ("arm_pins", "plate_bracket"), ("act_body", "post"),
          ("act_rod", "arms"), ("act_body", "act_rod"), ("encoder", "arm_pins"), ("plate", "plate_bracket")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    bolts = ("bracket_bolts", "bearer_bolts")
    return (a in bolts and b.startswith(("upper_beam", "lower_beam"))) or \
        (b in bolts and a.startswith(("upper_beam", "lower_beam")))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3): grass meter parts among themselves and against the robot (JOINTS skipped)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_deg, P.robot_steer_deg)):
    """Plate heights (range and lifted) and front wheels steered +-30: all parts against the robot, the moving parts
    against the rest. Must be empty."""
    doc = active_doc(doc)
    out = {}
    moving = objects_of(doc, "PlateMoving")
    names = {o.Name for o in moving}
    for st in steer:
        set_steering(st, doc)
        mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT) if o.Name not in names]
        robot = [(o, global_shape(o)) for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
        hits = _overlaps([(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)], tol)
        if hits:
            out[("steer", st)] = hits
    set_steering(0.0, doc)
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    for h in (P.H_RANGE[0], P.H_RANGE[1], P.lift_h):
        set_height(h, doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[("h", h)] = hits
    set_height(P.sward_h, doc)
    return out


def tyre_envelope(x, y, steer=0.0):
    c = V(x, y, P.robot_axle_z)
    t = Part.makeCylinder(P.robot_tire_r, P.robot_tire_w, c - V(P.robot_tire_w / 2.0, 0, 0), V(1, 0, 0))
    t.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return t


def clearance(doc=None):
    """Smallest distance (mm) of the boom group to the steered front tyres and of the plate to the rear tyres."""
    doc = active_doc(doc)
    best = (1e9, None, None)
    for st in (-P.robot_steer_deg, 0.0, P.robot_steer_deg):
        tyres = [tyre_envelope(sx * P.robot_wheel_x, P.robot_axle_y, st) for sx in (-1, 1)]
        for o in objects_of(doc, "Boom"):
            s = global_shape(o)
            for t in tyres:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name, st)
    front = (round(best[0], 1), best[1], best[2])
    best = (1e9, None)
    rear = [tyre_envelope(sx * P.robot_wheel_x, -P.robot_axle_y) for sx in (-1, 1)]
    for h in (P.H_RANGE[0], P.lift_h):
        set_height(h, doc)
        for o in objects_of(doc, "PlateMoving"):
            s = global_shape(o)
            for t in rear:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name)
    set_height(P.sward_h, doc)
    return {"boom_to_front_tyres": front, "plate_to_rear_tyres": (round(best[0], 1), best[1])}


MASS_FIXED = {"ndvi_sensors": 2 * 0.6, "lidar": 0.2, "camera": 0.4, "logger": 1.5, "encoder": 0.15, "act_body": 0.8,
              "act_rod": 0.2}
DENSITY = (("plate", P.pe),)


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole kit, the boom and the plate meter."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Boom", "PlateMeter"):
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
    add_floor(doc, y=(-900.0, 1200.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_front_right_on_robot.png", (-1.0, -1.2, -0.7), target=(0, 300, 400)))
    out.append(save_view("2_side.png", (-1.0, 0.0, 0.0), target=(0, 250, 450), height=1500))
    set_steering(P.robot_steer_deg, doc)
    remove(doc, [GROUND])
    out.append(save_view("3_top_steered.png", (0.0, 0.0, -1.0), target=(0, 300, 0), up=(0.0, 1.0, 0.0), height=2000))
    set_steering(0.0, doc)
    set_robot_visible(False, doc)
    out.append(save_view("4_boom_sensors.png", (-0.8, -1.0, -0.5), target=(0, 880, 650), height=900))
    out.append(save_view("5_plate_meter_side.png", (-1.0, 0.0, 0.0), target=(0, 50, 350), height=800))
    set_height(P.lift_h, doc)
    out.append(save_view("6_plate_meter_lifted.png", (-1.0, 0.0, 0.0), target=(0, 50, 350), height=800))
    App.closeDocument(doc.Name)
    build()
    return out
