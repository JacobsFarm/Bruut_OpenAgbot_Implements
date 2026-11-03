"""Model of the tray setter on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_tst
    build_tst.build()                          # saves FCStd and STEP (picker over the left funnel)
    build_tst.set_pose("pick_rear_right")      # one of POSES
    build_tst.check_interference()             # overlap in the current pose (must be empty)
    build_tst.check_poses()                    # gantry over the poses x steering +-30 (must be empty)
    build_tst.clearance()                      # shoes and press wheels to the tyres
    build_tst.mass_properties()
    build_tst.render_all()                     # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tst_params as P
import tst_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Tray_Setter"
SAVE_BASE = os.path.join(FOLDER, "Tray_Setter")
ROOT = "Tray_setter"

COLOR = {"frame": (0.93, 0.42, 0.08), "alu": (0.80, 0.81, 0.83), "zinc": (0.82, 0.84, 0.87),
         "steel": (0.75, 0.75, 0.78), "tray": (0.15, 0.15, 0.17), "plant": (0.35, 0.65, 0.20),
         "pe": (0.95, 0.95, 0.92), "motor": (0.20, 0.22, 0.25), "rubber": (0.10, 0.10, 0.10),
         "picker": (0.15, 0.45, 0.80), "shoe": (0.55, 0.56, 0.58)}


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


# ---------------------------------------------------------------------
# Poses: (picker axis x, picker axis y, needle lift above the pick height, plug held, cells taken)
# ---------------------------------------------------------------------
def _cell(tray_i, a, b):
    return P.cell_xy(tray_i, a, b)


POSES = {
    "over_funnel_left": (P.row_x[0], P.funnel_y, P.carry_lift, True, 1),
    "pick_front_left": (_cell(0, 0, P.tray_cells[1] - 1)[0], _cell(0, 0, P.tray_cells[1] - 1)[1], 0.0, True, 0),
    "carry_front_left": (_cell(0, 0, P.tray_cells[1] - 1)[0], _cell(0, 0, P.tray_cells[1] - 1)[1], P.carry_lift, True, 1),
    "pick_rear_right": (_cell(1, P.tray_cells[0] - 1, 0)[0], _cell(1, P.tray_cells[0] - 1, 0)[1], 0.0, True, 255),
    "over_funnel_right": (P.row_x[1], P.funnel_y, P.carry_lift, True, 1),
}


def pose_placements(pose):
    px, py, dz, held, taken = POSES[pose]
    return {"Gantry_Y": App.Placement(V(0, py - G.PICK_Y, 0), App.Rotation()),
            "Picker": App.Placement(V(px, 0, 0), App.Rotation()),
            "Picker_Z": App.Placement(V(0, 0, dz), App.Rotation())}


def held_plug():
    z = G.NEEDLE_TIP_PICK + P.pick_depth - P.plug[1]
    return G.seedling(0.0, G.PICK_Y, z, leaves=False)        # the leaves fold up between the needles


def build_into(doc, parent=None, pose="over_funnel_left"):
    pl = pose_placements(pose)
    _, _, _, held, taken = POSES[pose]
    root = new_part(doc, parent, ROOT, "tray_setter_simple")
    tb = new_part(doc, root, "Table", "tray_table_trays_funnels")
    add_shape(doc, tb, "cradle", "cradle_tubes_40x40x3", G.cradle(), "frame")
    add_shape(doc, tb, "cradle_bolts", "cradle_bolts_M10", G.cradle_bolts(), "zinc")
    add_shape(doc, tb, "table", "tray_table_alu_4mm_stops", G.table(), "alu")
    add_shape(doc, tb, "trays", "plug_trays_128_cells_2x", G.trays(), "tray")
    add_shape(doc, tb, "seedlings", "seedlings_in_plugs", G.seedlings_in_trays(taken), "plant")
    add_shape(doc, tb, "funnels", "funnels_PE_D110", G.funnels(), "pe")
    add_shape(doc, tb, "drop_tubes", "drop_tubes_PE_D50", G.drop_tubes(), "pe")
    gf = new_part(doc, root, "Gantry", "gantry_fixed")
    add_shape(doc, gf, "y_rails", "y_rails_alu_40x40_guides", G.y_rails(), "alu")
    add_shape(doc, gf, "y_motor", "y_motor_NEMA17", G.gantry_motors(), "motor")
    gy = new_part(doc, root, "Gantry_Y", "gantry_moves_in_y", pl["Gantry_Y"])
    add_shape(doc, gy, "y_carriages", "y_carriages_posts", G.y_carriages(), "alu")
    add_shape(doc, gy, "x_beam", "x_beam_60x40_x_motor", G.x_beam(), "alu")
    pk = new_part(doc, gy, "Picker", "picker_moves_in_x", pl["Picker"])
    add_shape(doc, pk, "picker_carriage", "picker_carriage_z_actuator", G.picker_carriage(), "picker")
    pz = new_part(doc, pk, "Picker_Z", "needle_head_moves_in_z", pl["Picker_Z"])
    rod_head, stripper = G.z_group()
    add_shape(doc, pz, "needle_head", "z_rod_needle_head_4_needles", rod_head, "steel")
    add_shape(doc, pz, "stripper", "stripper_plate", stripper, "steel")
    add_shape(doc, pz, "held_plug", "seedling_on_the_needles", held_plug(), "plant", held)
    bl = new_part(doc, root, "Belly", "belly_rails_shoes_press_wheels")
    add_shape(doc, bl, "rails", "belly_rails_40x40x3_x225", G.rails(), "frame")
    add_shape(doc, bl, "rail_bolts", "rail_bolts_8xM10", G.rail_bolts(), "zinc")
    add_shape(doc, bl, "cross_beams", "cross_beams_40x40x3", G.cross_beams(), "frame")
    add_shape(doc, bl, "cross_bolts", "cross_beam_bolts_M8_rivet_nuts", G.cross_bolts(), "zinc")
    add_shape(doc, bl, "shoes", "runner_shoes_posts_boots", G.shoes(), "shoe")
    add_shape(doc, bl, "press_hangers", "press_wheel_hangers_yokes", G.press_hangers(), "frame")
    add_shape(doc, bl, "press_wheels", "press_wheels_D250_tilted_15", G.press_wheels(), "rubber")
    return root


def set_pose(pose, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(pose).items():
        doc.getObject(name).Placement = pl
    _, _, _, held, taken = POSES[pose]
    doc.getObject("held_plug").ViewObject.Visibility = held
    doc.getObject("seedlings").Shape = G.seedlings_in_trays(taken)
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


def build(save=True, show_robot=False, step=True, pose="over_funnel_left"):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Tray setter simple"
    doc.Comment = ("Generated by build_tst.py from tst_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. build_tst.set_pose() moves the gantry.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, pose)
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
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []


def mine_visible(doc):
    return [o for o in objects_of(doc, ROOT) if o.ViewObject is None or o.ViewObject.Visibility]


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
    for o in mine_visible(doc):
        f = doc.addObject("Part::Feature", "step_" + o.Name)
        f.Label = o.Label
        f.Shape = global_shape(o)
        objs.append(f)
    try:
        Import.export(objs, path)
    finally:
        for f in objs:
            doc.removeObject(f.Name)


JOINTS = {("cradle_bolts", "cradle"), ("cradle_bolts", "table"), ("rail_bolts", "rails"), ("cross_bolts", "rails"),
          ("cross_bolts", "cross_beams"), ("shoes", "cross_beams"), ("press_hangers", "cross_beams"),
          ("press_hangers", "press_wheels"), ("drop_tubes", "shoes"), ("drop_tubes", "table"), ("funnels", "table"),
          ("funnels", "drop_tubes"), ("trays", "table"), ("seedlings", "trays"), ("y_motor", "y_rails"),
          ("y_carriages", "y_rails"), ("y_carriages", "x_beam"), ("picker_carriage", "x_beam"),
          ("needle_head", "picker_carriage"), ("needle_head", "stripper"), ("needle_head", "held_plug"),
          ("held_plug", "stripper"), ("held_plug", "trays"), ("needle_head", "seedlings"),
          ("held_plug", "seedlings"), ("stripper", "seedlings")}     # neighbours' leaves bend away
BEAM_BOLTS = ("rail_bolts", "cradle_bolts")


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x in BEAM_BOLTS and y.startswith(("lower_beam", "upper_beam")):
            return True
    return False


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


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in mine_visible(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def set_steering(deg, doc=None):
    doc = active_doc(doc)
    for name in ("FL_steered", "FR_steered"):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), deg))
    doc.recompute()


def check_poses(doc=None, tol=1.0):
    """Every pose of the gantry, and the whole setter at full steering lock. Must be empty."""
    doc = active_doc(doc)
    out = {}
    for name in POSES:
        set_pose(name, doc)
        hits = check_interference(doc, tol)
        if hits:
            out[name] = hits
    set_pose("over_funnel_left", doc)
    front = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
    for st in (-P.robot_steer_max, P.robot_steer_max):
        set_steering(st, doc)
        mine = [(o, global_shape(o)) for o in mine_visible(doc)]
        hits = _overlaps([(a, (b, global_shape(b))) for a in mine for b in front], tol)
        if hits:
            out["steer_%+d" % st] = hits
    set_steering(0.0, doc)
    return out


def tyre_envelope(x, y, steer):
    c = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, V(x - P.robot_tire_w / 2.0, y, P.robot_axle_z), V(1, 0, 0))
    c.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return c


def clearance(doc=None):
    """Smallest distance (mm) of the shoes, press wheels, hangers and drop tubes to the tyres (front steered +-30)."""
    doc = active_doc(doc)
    parts = [doc.getObject(n) for n in ("shoes", "press_wheels", "press_hangers", "drop_tubes", "cross_beams")]
    best = (1e9, None, None)
    for st in (-P.robot_steer_max, 0.0, P.robot_steer_max):
        tg = [tyre_envelope(sx * P.robot_wheel_x, P.robot_axle_y, st) for sx in (-1, 1)]
        tg += [tyre_envelope(sx * P.robot_wheel_x, -P.robot_axle_y, 0.0) for sx in (-1, 1)]
        for o in parts:
            s = global_shape(o)
            for i, t in enumerate(tg):
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name, (st, "front" if i < 2 else "rear"))
    return round(best[0], 1), best[1], best[2]


DENSITY = {"table": P.alu, "y_rails": P.alu, "y_carriages": P.alu, "x_beam": P.alu, "picker_carriage": P.alu,
           "funnels": P.pe, "drop_tubes": P.pe, "trays": P.pe, "press_wheels": P.rubber}
MASS_FIXED = {"seedlings": 2 * 128 * 0.03, "held_plug": 0.03, "y_motor": 0.5}


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity y, trays full."""
    doc = active_doc(doc)
    m, my = 0.0, 0.0
    for o in mine_visible(doc):
        s = global_shape(o)
        mo = MASS_FIXED.get(o.Name, s.Volume * DENSITY.get(o.Name, P.steel))
        m += mo
        my += mo * s.BoundBox.Center.y
    return {"total_kg": round(m, 1), "cg_y": round(my / m)}


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in mine_visible(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, 0, 500)
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


GROUND = ("render_bed", "render_planted")


def add_scene(doc):
    b = doc.addObject("Part::Feature", GROUND[0])
    b.Shape = G.bed(-1600.0, 1200.0)
    b.ViewObject.ShapeColor = (0.45, 0.33, 0.22)
    p = doc.addObject("Part::Feature", GROUND[1])
    p.Shape = Part.makeCompound([G.seedling(x, y, -P.plug[1] + 5.0) for x in P.row_x
                                 for y in range(int(P.press_y - 200), -1600, -int(P.spacing))])
    p.ViewObject.ShapeColor = COLOR["plant"]


def render_all():
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_scene(doc)
    out.append(save_view("1_iso_on_robot.png", (-1.0, 1.1, -0.7), target=(0, -200, 500), height=2300))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, -200, 500), height=2000))
    set_pose("pick_rear_right", doc)
    out.append(save_view("3_top_trays_gantry.png", (0.0, 0.0, -1.0), target=(0, -150, 0), up=(0.0, 1.0, 0.0),
                         height=1500))
    set_pose("pick_front_left", doc)
    set_robot_visible(False, doc)
    out.append(save_view("4_picker_needles_in_plug.png", (-1.0, 0.9, -0.5), target=(-260, -60, 800), height=520))
    set_pose("over_funnel_left", doc)
    for n in GROUND:
        doc.getObject(n).ViewObject.Transparency = 60
    out.append(save_view("5_shoe_press_wheels.png", (-1.0, 0.7, -0.35), target=(-150, -30, 200), height=900))
    App.closeDocument(doc.Name)
    build()
    return out
