"""Model of the charging dock with the Bruut OpenAgbot (standard robot) docked.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_cdk
    build_cdk.build()                      # saves FCStd and STEP (docked)
    build_cdk.set_pose(dy=300)             # robot 300 mm short of the dock (approach); dx, yaw: robot off line
    build_cdk.check_interference()         # overlap docked (must be empty)
    build_cdk.check_poses()                # approach and docked with the wheels steered (must be empty)
    build_cdk.clearance()                  # station to the front tyres and wheel units
    build_cdk.mass_properties()
    build_cdk.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cdk_params as P
import cdk_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Charging_Dock"
SAVE_BASE = os.path.join(FOLDER, "Charging_Dock")
ROOT = "Charging_dock"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "pe": (0.95, 0.95, 0.92),
    "copper": (0.80, 0.45, 0.20),
    "box": (0.20, 0.45, 0.25),
    "roof": (0.60, 0.62, 0.65),
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







def station_placement(dy=0.0, dx=0.0, yaw=0.0):
    """The station relative to the robot: dy > 0 = robot still dy short of docked; dx, yaw = robot off line."""
    return App.Placement(V(-dx, dy, 0), App.Rotation(V(0, 0, 1), -yaw), V(0, P.robot_axle_y, 0))


def build_into(doc, parent=None, robot_parent=None):
    root = new_part(doc, parent, ROOT, "charging_dock_simple")
    kit = new_part(doc, root, "RobotKit", "contact_bracket_on_robot")
    add_shape(doc, kit, "robot_bracket", "contact_bracket_6mm", G.robot_bracket(), "frame")
    add_shape(doc, kit, "bracket_bolts", "bracket_bolts_M10_2x", G.bracket_bolts(), "zinc")
    add_shape(doc, kit, "pe_carrier", "pad_carrier_PE", G.pe_carrier(), "pe")
    add_shape(doc, kit, "pads", "copper_pads_2x", G.pads(), "copper")
    add_shape(doc, kit, "springs", "pad_springs_4x", G.springs(), "zinc")
    add_shape(doc, kit, "pilot", "pilot_pin_D10", G.pilot(), "zinc")
    st = new_part(doc, root, "Station", "docking_station", station_placement())
    add_shape(doc, st, "base_plate", "base_plate_10mm", G.base_plate(), "frame")
    add_shape(doc, st, "anchors", "ground_anchors_D20x400_4x", G.anchors(), "zinc")
    add_shape(doc, st, "post", "post_80x80x4_gussets", G.post(), "frame")
    arm, head = G.arm_and_head()
    add_shape(doc, st, "arm", "arm_60x40x3", arm, "frame")
    add_shape(doc, st, "head", "contact_head_PE", head, "pe")
    add_shape(doc, st, "funnel", "funnel_plates_3mm", G.funnel(), "zinc")
    add_shape(doc, st, "bars", "copper_bars_2x", G.bars(), "copper")
    add_shape(doc, st, "charger", "charger_48V_1kW_IP65", G.charger(), "box")
    add_shape(doc, st, "roof", "roof_sheet", G.roof(), "roof")
    return root


def set_pose(dy=0.0, dx=0.0, yaw=0.0, doc=None):
    active_doc(doc).getObject("Station").Placement = station_placement(dy, dx, yaw)


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


def build(save=True, show_robot=True, step=True):
    """The robot stays visible in the FCStd here: the dock only makes sense with the robot in it."""
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Charging dock simple"
    doc.Comment = ("Generated by build_cdk.py from cdk_params.py. Robot coordinates (robot docked, centre at the origin): "
                   "x = right, y = driving direction (front = +y), z = up, ground = z 0. set_pose() moves the station.")
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




JOINTS = {("bracket_bolts", "robot_bracket"), ("pe_carrier", "robot_bracket"), ("pads", "pe_carrier"),
          ("springs", "pe_carrier"), ("springs", "pads"), ("pilot", "pe_carrier"), ("pilot", "robot_bracket"),
          ("pilot", "head"), ("anchors", "base_plate"), ("post", "base_plate"), ("arm", "post"), ("arm", "head"),
          ("bars", "head"), ("funnel", "head"), ("charger", "post"), ("roof", "post"), ("pads", "bars")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    return (a == "bracket_bolts" and b.startswith("lower_beam")) or (b == "bracket_bolts" and a.startswith("lower_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) docked: kit and station among themselves and against the robot (JOINTS skipped)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Station against the robot (kit included) on the approach (300, 150 mm short) and docked, with the front wheels
    steered: nothing may touch except the funnel guiding the kit. Must be empty."""
    doc = active_doc(doc)
    st = objects_of(doc, "Station")
    others = robot_objects(doc) + objects_of(doc, "RobotKit")
    out = {}
    for s in steer:
        set_steering(s, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for dy in (300.0, 150.0, 0.0):
            set_pose(dy, doc=doc)
            mv = [(o, global_shape(o)) for o in st]
            hits = _overlaps([(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
            if hits:
                out[(s, dy)] = hits
    set_steering(0.0, doc)
    set_pose(doc=doc)
    return out


def tyre_envelope(x, y, steer=0.0):
    c = V(x, y, P.robot_axle_z)
    t = Part.makeCylinder(P.robot_tire_r, P.robot_tire_w, c - V(P.robot_tire_w / 2.0, 0, 0), V(1, 0, 0))
    t.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return t


def clearance(doc=None):
    """Smallest distance (mm) of the station to the steered front tyres and to the front wheel units, docked."""
    doc = active_doc(doc)
    st = [global_shape(o) for o in objects_of(doc, "Station")]
    best = 1e9
    for s in (-P.robot_steer_deg, 0.0, P.robot_steer_deg):
        set_steering(s, doc)
        targets = [tyre_envelope(sx * P.robot_wheel_x, P.robot_axle_y, s) for sx in (-1, 1)]
        targets += [global_shape(o) for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))
                    and not o.Name.endswith(("tire", "rim", "hub"))]
        for a in st:
            for t in targets:
                if a.BoundBox.isValid() and t.BoundBox.isValid():
                    best = min(best, a.distToShape(t)[0])
    set_steering(0.0, doc)
    return round(best, 1)


MASS_FIXED = {"charger": 6.0, "pilot": 0.02, "anchors": 4 * 1.1}
DENSITY = (("pe_carrier", P.pe), ("head", P.pe), ("pads", P.copper), ("bars", P.copper))


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole dock, the kit on the robot and the station."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "RobotKit", "Station"):
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
    """Standard images in previews/, then build and save (FCStd + STEP)."""
    out = []
    doc = build(save=False, step=False)
    add_floor(doc, y=(-900.0, 1500.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_docked.png", (1.0, -1.3, -0.7), target=(0, 500, 500)))
    out.append(save_view("2_side_docked.png", (-1.0, 0.0, 0.0), target=(0, 400, 600), height=1700))
    set_pose(300.0, doc=doc)
    out.append(save_view("3_side_approach.png", (-1.0, 0.0, 0.0), target=(0, 400, 600), height=1700))
    set_pose(doc=doc)
    remove(doc, [GROUND])
    set_steering(P.robot_steer_deg, doc)
    out.append(save_view("4_top_docked_steered.png", (0.0, 0.0, -1.0), target=(0, 600, 0), up=(0.0, 1.0, 0.0), height=1700))
    set_steering(0.0, doc)
    doc.getObject("roof").ViewObject.Visibility = False
    out.append(save_view("5_contacts_detail.png", (1.0, -0.8, -0.6), target=(0, 630, 570), height=450))
    set_robot_visible(False, doc)
    set_pose(120.0, doc=doc)
    out.append(save_view("6_contacts_open.png", (-1.0, 0.7, -0.5), target=(0, 650, 570), height=450))
    App.closeDocument(doc.Name)
    build()
    return out
