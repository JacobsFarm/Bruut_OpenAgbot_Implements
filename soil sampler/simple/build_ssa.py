"""Model of the soil sampler on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_ssa
    build_ssa.build()                          # saves FCStd and STEP (park pose)
    build_ssa.set_pose(tip=-100, chute=90)     # probe tip height (mm, - = in the soil), chute angle, carousel step
    build_ssa.check_interference()             # overlap in the current pose (must be empty)
    build_ssa.check_poses()                    # overlap over the sampling cycle (must be empty)
    build_ssa.mass_properties()
    build_ssa.render_all()                     # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ssa_params as P
import ssa_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Soil_Sampler"
SAVE_BASE = os.path.join(FOLDER, "Soil_Sampler")
ROOT = "Soil_sampler"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "stainless": (0.86, 0.87, 0.88),
    "alu": (0.70, 0.72, 0.75),
    "motor": (0.08, 0.08, 0.08),
    "cup": (0.95, 0.95, 0.92),
    "pe": (0.10, 0.10, 0.10),
    "rail": (0.30, 0.31, 0.33),
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


def chute_placement(deg):
    px, py = P.chute_pivot
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), deg), V(px, py, 0))


def carousel_placement(step):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), 360.0 / P.n_cups * step), V(P.car_c[0], P.car_c[1], 0))


def build_into(doc, parent=None):
    """Put the sampler in a document, in robot coordinates (park pose)."""
    root = new_part(doc, parent, ROOT, "soil_sampler_simple")
    mount = new_part(doc, root, "Mount", "mount_bridges_mast")
    add_shape(doc, mount, "bridges", "bridges_40x40x3_L730", G.bridges(), "frame")
    add_shape(doc, mount, "bridge_bolts", "bridge_bolts_M10", G.bridge_bolts(), "zinc")
    add_shape(doc, mount, "mast", "mast_plate_10mm_bearing_motor_plate", G.mast(), "alu")
    add_shape(doc, mount, "mast_bolts", "mast_bolts_M8", G.mast_bolts(), "zinc")
    add_shape(doc, mount, "rails", "rails_SBR20", G.rails(), "rail")
    add_shape(doc, mount, "screw", "ball_screw_SFU1605", G.screw(), "steel")
    add_shape(doc, mount, "z_motor", "z_motor_NEMA23_coupling", G.z_motor(), "motor")
    car = new_part(doc, root, "Carriage", "carriage_moves_in_z", carriage_placement(P.tip_park))
    add_shape(doc, car, "carriage", "carriage_plate_blocks_nut_holder", G.carriage(), "alu")
    add_shape(doc, car, "probe", "gouge_probe_D%d_L%d" % (P.probe_d, P.probe_len), G.probe(), "stainless")
    add_shape(doc, car, "ejector", "ejector_actuator_24V_stroke_%d" % P.ejector_stroke, G.ejector(), "motor")
    foot = new_part(doc, root, "Foot", "sprung_foot", foot_placement(P.tip_park))
    add_shape(doc, foot, "foot", "foot_ring_PE_D%d_rods_springs" % P.foot_d, G.foot(), "pe")
    ch = new_part(doc, root, "Chute", "swing_chute_turns", chute_placement(0.0))
    add_shape(doc, ch, "chute", "swing_chute_half_pipe_D50", G.chute(), "stainless")
    fix = new_part(doc, root, "Funnel", "funnel_servo")
    add_shape(doc, fix, "chute_servo", "chute_servo_20kgcm", G.chute_servo(), "motor")
    add_shape(doc, fix, "funnel", "funnel_D110_D60", G.funnel(), "stainless")
    add_shape(doc, fix, "funnel_bracket", "funnel_bracket_30x6", G.funnel_bracket(), "frame")
    add_shape(doc, fix, "car_shaft", "carousel_shaft_D20", G.car_shaft(), "steel")
    add_shape(doc, fix, "car_drive", "carousel_bearings_NEMA17_5_1", G.car_drive(), "motor")
    carousel = new_part(doc, root, "Carousel", "carousel_turns", carousel_placement(0))
    add_shape(doc, carousel, "turntable", "turntable_D%d_PE" % P.car_d, G.turntable(), "pe")
    add_shape(doc, carousel, "cups", "sample_cups_%dx_D%d_%dl" % (P.n_cups, P.cup_d, round(P.cup_l())), G.cups(), "cup")
    return root


def set_pose(tip=P.tip_park, chute=0.0, step=0, doc=None):
    doc = active_doc(doc)
    doc.getObject("Carriage").Placement = carriage_placement(tip)
    doc.getObject("Foot").Placement = foot_placement(tip)
    doc.getObject("Chute").Placement = chute_placement(chute)
    doc.getObject("Carousel").Placement = carousel_placement(step)


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
    doc.Label = "Soil sampler simple"
    doc.Comment = ("Generated by build_ssa.py from ssa_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Park pose; build_ssa.set_pose() runs the sampling cycle.")
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


# shafts, rods and bolts pass through holes in the parts they join: those pairs are by design
JOINTS = {("bridge_bolts", "bridges"), ("mast_bolts", "mast"), ("mast_bolts", "bridges"), ("screw", "mast"),
          ("screw", "carriage"), ("screw", "z_motor"), ("rails", "carriage"), ("probe", "carriage"),
          ("ejector", "probe"), ("foot", "carriage"), ("car_shaft", "bridges"), ("car_shaft", "car_drive"),
          ("car_shaft", "turntable"), ("chute", "chute_servo")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    pair = {a, b}
    return "bridge_bolts" in pair and any(n.startswith("upper_beam") for n in pair)


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: sampler parts among themselves and against the robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """Shafts, rods and bolts must sit in holes: overlap of the JOINTS pairs (should be ~0)."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    out = {}
    for a, b in JOINTS:
        if (a, b) in (("ejector", "probe"), ("rails", "carriage"), ("chute", "chute_servo"), ("screw", "z_motor")):
            continue                    # rod in the probe bore, blocks on the rail shafts, servo spline, coupling
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[(a, b)] = round(v, 1)
    return out


# sampling cycle: (tip, chute angle, carousel step)
CYCLE = [(P.tip_park, 0.0, 0), (P.tip_park, P.chute_aside_deg, 0), (P.foot_drop, P.chute_aside_deg, 0),
         (0.0, P.chute_aside_deg, 0), (-P.depth_grass, P.chute_aside_deg, 0), (-P.depth_max, P.chute_aside_deg, 0),
         (P.tip_park, 0.0, 1), (P.tip_park, 0.0, 0.5)]


def check_poses(doc=None, tol=1.0):
    """Interference over the sampling cycle: moving groups against everything else. Must be empty."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Carriage") + objects_of(doc, "Foot") + objects_of(doc, "Chute") + \
        objects_of(doc, "Carousel")
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for pose in CYCLE:
        set_pose(*pose, doc=doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[pose] = hits
    set_pose(doc=doc)
    return out


def clearance(doc=None):
    """Smallest distance (mm) of the carousel to the rear wheel brackets and tyres (plain cylinder O430 x 100)."""
    doc = active_doc(doc)
    targets = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith(("RL_side", "RR_side"))]
    for sx in (-1, 1):
        targets.append(Part.makeCylinder(215.0, 100.0, V(sx * 375.0 - 50.0, -500.0, 215.0), V(1, 0, 0)))
    best = 1e9
    for o in objects_of(doc, "Carousel"):
        s = global_shape(o)
        for t in targets:
            best = min(best, s.distToShape(t)[0])
    return round(best, 1)


MASS_FIXED = {"z_motor": P.m_motor, "car_drive": P.m_car_motor + 0.6, "ejector": P.m_ejector, "chute_servo": 0.06,
              "cups": P.n_cups * P.m_cups}
DENSITY = (("mast", P.alu), ("carriage", P.alu), ("turntable", P.pe), ("foot", P.pe))


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key, m in MASS_FIXED.items():
        if obj.Name.startswith(key):
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
    """Mass (kg) and centre of gravity (robot coordinates) of the sampler and its groups."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Mount", "Carriage", "Carousel"):
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
    add_floor(doc, y=(-1000.0, 1000.0), x=(-900.0, 900.0))
    out.append(save_view("1_iso_on_robot_park.png", (-1.0, -1.0, -0.6), target=(0, -150, 500)))
    set_pose(-P.depth_grass, P.chute_aside_deg, 0, doc)
    out.append(save_view("2_side_sampling.png", (1.0, 0.0, 0.0), target=(0, -150, 500), height=1500))
    set_pose(doc=doc)
    out.append(save_view("3_side_park_eject.png", (1.0, 0.0, 0.0), target=(0, -150, 500), height=1500))
    remove(doc, [GROUND])
    set_robot_visible(False, doc)
    out.append(save_view("4_sampler_iso.png", (-1.0, -0.8, -0.5), target=(0, -150, 550), height=1300))
    out.append(save_view("5_chute_funnel_detail.png", (-1.0, -0.4, -0.6), target=(0, -150, 420), height=500))
    out.append(save_view("6_top.png", (0.0, 0.0, -1.0), target=(0, -150, 0), up=(0.0, 1.0, 0.0), height=1100))
    App.closeDocument(doc.Name)
    build()
    return out
