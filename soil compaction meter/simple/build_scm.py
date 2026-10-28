"""Model of the soil compaction meter (cone penetrometer) on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_scm
    build_scm.build()                      # saves FCStd and STEP (park pose)
    build_scm.set_pose(-600)               # cone tip height (mm, - = in the soil)
    build_scm.check_interference()         # overlap (must be empty)
    build_scm.check_poses()                # park .. full depth (must be empty)
    build_scm.travel_ok()                  # carriage stays on the rails
    build_scm.mass_properties()
    build_scm.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import scm_params as P
import scm_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Soil_Compaction_Meter"
SAVE_BASE = os.path.join(FOLDER, "Soil_Compaction_Meter")
ROOT = "Soil_compaction_meter"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "alu": (0.70, 0.72, 0.75),
    "rail": (0.55, 0.57, 0.60),
    "steel": (0.75, 0.75, 0.78),
    "stainless": (0.85, 0.86, 0.88),
    "motor": (0.25, 0.26, 0.28),
    "sensor": (0.15, 0.35, 0.75),
    "box": (0.20, 0.45, 0.25),
    "pe": (0.95, 0.95, 0.92),
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







def carriage_placement(tip):
    return App.Placement(V(0, 0, P.carriage_z(tip) - G.PARK_C), App.Rotation())


def foot_placement(tip):
    """The foot hangs foot_drop below the tip until it rests on the ground."""
    z = max(0.0, tip - P.foot_drop)
    return App.Placement(V(0, 0, z - (P.tip_park - P.foot_drop)), App.Rotation())


def build_into(doc, parent=None, tip=P.tip_park):
    root = new_part(doc, parent, ROOT, "soil_compaction_meter_simple")
    mount = new_part(doc, root, "Mount", "mount_bridges_mast")
    add_shape(doc, mount, "bridges", "bridges_40x40x3_L730_2x", G.bridges(), "frame")
    add_shape(doc, mount, "bridge_bolts", "bridge_bolts_M10", G.bridge_bolts(), "zinc")
    add_shape(doc, mount, "stays", "mast_stays_40x6", G.stays(), "frame")
    add_shape(doc, mount, "logger", "logger_box", G.logger(), "box")
    add_shape(doc, mount, "mast", "mast_plate_10mm", G.mast(), "alu")
    add_shape(doc, mount, "mast_bolts", "mast_bolts_M8", G.mast_bolts(), "zinc")
    add_shape(doc, mount, "rails", "rails_SBR20", G.rails(), "rail")
    add_shape(doc, mount, "screw", "ball_screw_SFU1605", G.screw(), "steel")
    add_shape(doc, mount, "z_motor", "z_motor_NEMA23_closed_loop", G.z_motor(), "motor")
    car = new_part(doc, root, "Carriage", "carriage_moves_in_z", carriage_placement(tip))
    add_shape(doc, car, "carriage", "carriage_plate_blocks_nut_holder", G.carriage(), "alu")
    add_shape(doc, car, "loadcell", "s_type_load_cell_2kN", G.loadcell(), "sensor")
    add_shape(doc, car, "clamp", "rod_clamp_block", G.clamp(), "steel")
    add_shape(doc, car, "rod", "penetrometer_rod_D9_5_cone_D12_83_30deg", G.rod(), "stainless")
    foot = new_part(doc, root, "Foot", "sprung_foot", foot_placement(tip))
    add_shape(doc, foot, "foot", "foot_ring_PE_D%d_PTFE_bush_rods" % P.foot_d, G.foot(), "pe")
    add_shape(doc, foot, "moisture_probe", "capacitive_moisture_probe", G.moisture_probe(), "sensor")
    return root


def set_pose(tip=P.tip_park, doc=None):
    """Cone tip height (mm, - = in the soil)."""
    doc = active_doc(doc)
    doc.getObject("Carriage").Placement = carriage_placement(tip)
    doc.getObject("Foot").Placement = foot_placement(tip)


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
    doc.Label = "Soil compaction meter simple"
    doc.Comment = ("Generated by build_scm.py from scm_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Park pose; build_scm.set_pose(tip) moves the cone.")
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




JOINTS = {("bridge_bolts", "bridges"), ("mast_bolts", "mast"), ("mast_bolts", "bridges"), ("screw", "mast"),
          ("screw", "carriage"), ("screw", "z_motor"), ("rails", "mast"), ("rails", "carriage"), ("stays", "mast"),
          ("stays", "bridges"), ("loadcell", "carriage"), ("loadcell", "clamp"), ("rod", "clamp"), ("rod", "foot"),
          ("foot", "carriage"), ("foot", "moisture_probe"), ("logger", "bridges")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    return (a == "bridge_bolts" and b.startswith("upper_beam")) or (b == "bridge_bolts" and a.startswith("upper_beam"))


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    """Cone from park to full depth: carriage and foot against the rest and each other. Must be empty."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Carriage") + objects_of(doc, "Foot")
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for tip in P.TIP_POSES:
        set_pose(tip, doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[tip] = hits
    set_pose(P.tip_park, doc)
    return out


def travel_ok():
    """The carriage stays on the rails between park and full depth."""
    lo, hi = P.carriage_z(-P.depth_max), P.carriage_z(P.tip_park) + P.carriage_h
    return {"carriage_z": (lo, hi), "rails": (P.mast_z[0] + 30.0, P.mast_z[1] - 5.0),
            "ok": lo + 5.0 >= P.mast_z[0] + 30.0 and hi <= P.mast_z[1] - 5.0}


MASS_FIXED = {"z_motor": P.m_motor, "loadcell": P.m_loadcell, "logger": P.m_logger, "moisture_probe": 0.15}
DENSITY = (("mast", P.alu), ("carriage", P.alu), ("foot", P.pe))


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole meter and of each group."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Mount", "Carriage", "Foot"):
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
    add_floor(doc, y=(-900.0, 900.0), x=(-900.0, 900.0))
    out.append(save_view("1_iso_front_right_on_robot.png", (-1.0, -1.2, -0.6), target=(0, 0, 500)))
    out.append(save_view("2_side_park.png", (-1.0, 0.0, 0.0), target=(0, -50, 500), height=1500))
    set_pose(-P.depth_max, doc)
    floor = doc.getObject(GROUND)
    floor.ViewObject.Transparency = 60
    out.append(save_view("3_side_full_depth.png", (-1.0, 0.0, 0.0), target=(0, -50, 300), height=1700))
    set_robot_visible(False, doc)
    remove(doc, [GROUND])
    set_pose(-150.0, doc)
    out.append(save_view("4_iso_probe_in_soil.png", (-1.0, -1.0, -0.4), target=(0, 0, 400), height=1400))
    set_pose(P.tip_park, doc)
    out.append(save_view("5_carriage_detail.png", (-0.8, -1.0, -0.3), target=(0, -40, 950), height=500))
    out.append(save_view("6_foot_detail.png", (-0.8, -1.0, -0.6), target=(0, -60, 130), height=350))
    App.closeDocument(doc.Name)
    build()
    return out
