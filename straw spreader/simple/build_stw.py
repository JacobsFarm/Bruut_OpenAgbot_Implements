"""Model of the straw spreader on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_stw
    build_stw.build()                      # saves FCStd and STEP
    build_stw.check_interference()         # overlap between the parts and with the robot (must be empty)
    build_stw.check_holes()                # bolts in their holes (must be empty)
    build_stw.check_steering()             # overlap with the front wheels steered +-30 (must be empty)
    build_stw.check_rows()                 # parts in the space of the crop rows (must be empty)
    build_stw.check_teeth()                # drum spikes in the rear of the bales (by design, > 0)
    build_stw.clearance()                  # smallest distance to the tyres (rear and steered front)
        build_stw.mass_properties()
    build_stw.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import stw_params as P
import stw_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Straw_Spreader"
SAVE_BASE = os.path.join(FOLDER, "Straw_Spreader")
ROOT = "Straw_spreader"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "wall": (0.20, 0.45, 0.75),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "chain": (0.25, 0.25, 0.27),
    "motor": (0.20, 0.22, 0.25),
    "bearing": (0.15, 0.30, 0.65),
    "straw": (0.90, 0.80, 0.40),
    "crop": (0.25, 0.60, 0.20),
}


def new_part(doc, parent, name, label):
    part = doc.addObject("App::Part", name)
    part.Label = label
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
    root = new_part(doc, parent, ROOT, "straw_spreader_simple")
    m = new_part(doc, root, "Mount", "bearers_and_rails")
    add_shape(doc, m, "bearers", "bearers_40x40x3_on_upper_beams", G.bearers(), "frame")
    add_shape(doc, m, "rails", "rails_40x40x3", G.rails(), "frame")
    add_shape(doc, m, "bolts", "bolts_M10", G.bolts(), "zinc")
    f = new_part(doc, root, "Floor", "slatted_floor_chain")
    add_shape(doc, f, "floor_plate", "floor_plate_2mm", G.floor_plate(), "steel")
    add_shape(doc, f, "shafts", "sprocket_shafts_D25", G.shafts(), "steel")
    add_shape(doc, f, "pillow_blocks", "pillow_blocks_UCP204", G.pillow_blocks(), "bearing")
    add_shape(doc, f, "sprockets", "sprockets_08B", G.sprockets(), "steel")
    add_shape(doc, f, "chains", "roller_chains_08B", G.chains(), "chain")
    add_shape(doc, f, "slats", "slat_angles_25x20x3", G.slats(), "chain")
    add_shape(doc, f, "floor_gearmotor", "gearmotor_24V_floor", G.floor_gearmotor(), "motor")
    c = new_part(doc, root, "Chamber", "bale_chamber")
    add_shape(doc, c, "walls", "chamber_walls_alu_2mm", G.walls(), "wall")
    add_shape(doc, c, "posts", "wall_posts_40x6", G.posts(), "frame")
    d = new_part(doc, root, "Shredder", "drum_housing_chute")
    add_shape(doc, d, "drum", "shredder_drum_D160_spikes_D16", G.drum(), "steel")
    add_shape(doc, d, "housing", "drum_housing_3mm", G.housing(), "frame")
    add_shape(doc, d, "drum_bearing", "drum_flange_bearing", G.drum_bearing(), "bearing")
    add_shape(doc, d, "drum_motor", "drum_motor_48V_750W_gearbox", G.drum_motor(), "motor")
    add_shape(doc, d, "chute", "chute_alu_2mm", G.chute(), "wall")
    return root


def build_load(doc, strip=True):
    """Bales and the laid strip: not part of the implement, not in the checks."""
    grp = new_part(doc, None, "Load", "bales_and_strip")
    add_shape(doc, grp, "bales", "small_bales_2x", G.bales(), "straw")
    if strip:
        add_shape(doc, grp, "strip", "straw_strip", G.mulch_strip(), "straw")
    return grp


def build_robot(doc, steer=0.0):
    """Real robot model from 'agbot design' (read only)."""
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


def build(save=True, show_robot=False, step=True, crop=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Straw spreader simple"
    doc.Comment = ("Generated by build_stw.py from stw_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    build_load(doc, strip=crop)
    if crop:
        grp = new_part(doc, None, "Crop", "crop_rows_for_images")
        add_shape(doc, grp, "crop", "crop_2_rows_375", G.crop(), "crop")
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


JOINTS = {("bolts", "bearers"), ("bolts", "rails"), ("shafts", "pillow_blocks"), ("shafts", "sprockets"),
          ("shafts", "floor_gearmotor"), ("drum", "housing"), ("drum", "drum_bearing"), ("drum", "drum_motor"),
          ("sprockets", "chains")}
ROBOT_JOINTS = {"bolts": "upper_beam"}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    return any(x == k and y.startswith(v) for k, v in ROBOT_JOINTS.items() for x, y in ((a, b), (b, a)))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3): parts among themselves and against the robot (bolts in their holes: check_holes)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """Bolts and shafts must pass through holes in the parts they join and in the robot beams."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    for o in robot_objects(doc):
        if o.Name.startswith("upper_beam") or o.Name.startswith("lower_beam"):
            objs[o.Name] = global_shape(o)
    pairs = [p for p in JOINTS if p != ("sprockets", "chains")]
    pairs += [(k, n) for k, v in ROBOT_JOINTS.items() for n in objs if n.startswith(v)]
    out = {}
    for a, b in pairs:
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[a + "|" + b] = round(v, 1)
    return out


def check_rows(doc=None, tol=1.0):
    """Parts in the space of the 2 crop rows (x row +- row_band, up to crop_h). Must be empty."""
    doc = active_doc(doc)
    bands = G.row_bands()
    out = {}
    for o in objects_of(doc, ROOT):
        s = global_shape(o)
        if s.BoundBox.intersect(bands.BoundBox):
            v = s.common(bands).Volume
            if v > tol:
                out[o.Name] = round(v, 1)
    return out


def check_teeth(doc=None):
    """Volume (mm3) of the drum spikes in the bales: the spikes must reach into the bale face."""
    doc = active_doc(doc)
    return round(global_shape(doc.getObject("drum")).common(global_shape(doc.getObject("bales"))).Volume, 1)


def check_steering(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    out = {}
    for st in (-P.robot_steer_deg, P.robot_steer_deg):
        set_steering(st, doc)
        front = [(o, global_shape(o)) for o in robot_objects(doc) if o.Name[:2] in ("FL", "FR")]
        hits = _overlaps([(a, b) for a in mine for b in front], tol)
        if hits:
            out[str(st)] = hits
    set_steering(0.0, doc)
    return out


def tyre_envelope(x, y, steer=0.0):
    c = V(x, y, P.robot_axle_z)
    t = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, c - V(P.robot_tire_w / 2.0, 0, 0), V(1, 0, 0))
    t.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return t


def clearance(doc=None):
    """Smallest distance (mm) of the implement to the rear tyres (envelopes)."""
    doc = active_doc(doc)
    tyres = [tyre_envelope(sx * P.robot_wheel_x, -P.robot_axle_y) for sx in (-1, 1)]
    best = (1e9, None)
    for o in objects_of(doc, ROOT):
        s = global_shape(o)
        for t in tyres:
            d = s.distToShape(t)[0]
            if d < best[0]:
                best = (d, o.Name)
    return round(best[0], 1), best[1]


MASS_FIXED = {"drum_motor": 9.0, "floor_gearmotor": 2.5}
DENSITY = (("walls", P.alu), ("chute", P.alu))


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    if obj.Name in MASS_FIXED:
        return MASS_FIXED[obj.Name], cg
    dens = P.steel
    for key, d in DENSITY:
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def mass_properties(doc=None):
    doc = active_doc(doc)
    m, c = 0.0, V(0, 0, 0)
    for o in objects_of(doc, ROOT):
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    c = c * (1.0 / m)
    return {"kg": round(m, 1), "cg": (round(c.x), round(c.y), round(c.z))}


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
    tgt = V(*target) if target is not None else V(0, -400, 800)
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


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False, crop=True)
    floor = doc.addObject("Part::Feature", "render_floor")
    floor.Shape = G.box_span((-1100, 1100), (-1700, 900), (-40.0, 0.0))
    floor.ViewObject.ShapeColor = (0.55, 0.45, 0.33)
    out.append(save_view("1_iso_rear_right_in_crop.png", (-1.0, 1.2, -0.8), target=(0, -400, 600)))
    out.append(save_view("2_side.png", (-1.0, 0.0, 0.0), target=(0, -350, 800), height=1900))
    out.append(save_view("3_rear.png", (0.0, 1.0, 0.0), target=(0, -400, 800), height=1800))
    doc.removeObject("render_floor")
    set_robot_visible(False, doc)
    for n in ("crop", "bales", "strip", "walls", "housing"):
        doc.getObject(n).ViewObject.Visibility = False
    out.append(save_view("4_floor_drum_iso.png", (-1.0, 1.0, -0.8), target=(0, -250, 900), height=1700))
    out.append(save_view("5_drum_side.png", (-1.0, 0.0, 0.0), target=(0, -600, 900), height=900))
    App.closeDocument(doc.Name)
    build()
    return out
