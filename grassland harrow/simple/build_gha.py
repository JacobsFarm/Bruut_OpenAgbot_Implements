"""Model of the grassland harrow on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_gha
    build_gha.build()                      # saves FCStd and STEP (work pose: harrow on the ground)
    build_gha.set_pose(lift=25)            # lift of the arms (deg, + = harrow up)
    build_gha.check_interference()         # overlap in the current pose (must be empty)
    build_gha.check_poses()                # overlap over the lift poses (must be empty)
    build_gha.clearance()                  # smallest distance to the rear tyres and wheel units, work and transport
    build_gha.ground_contact()             # lowest point of board and tines
    build_gha.mass_properties()
    build_gha.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import gha_params as P
import gha_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Grassland_Harrow"
SAVE_BASE = os.path.join(FOLDER, "Grassland_Harrow")
ROOT = "Grassland_harrow"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "tine": (0.15, 0.15, 0.16),
    "board": (0.30, 0.31, 0.33),
    "actuator": (0.25, 0.26, 0.28),
    "plastic": (0.10, 0.10, 0.10),
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



def lift_placement(lift_deg):
    """Rotation of the harrow about the pivot axis (x); + lift = harrow up (it is behind the pivot)."""
    c = V(0, P.pivot[0], P.pivot[1])
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -lift_deg), c)


def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_rear_toolbar")
    add_shape(doc, grp, "toolbar", "rear_toolbar_80x80x4_L900", G.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_caps", "toolbar_end_caps_PE", G.toolbar_caps(), "plastic")
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "hanger_top_" + tag, "hanger_top_plate_10mm_" + tag, G.hanger_top(sx), "frame")
        add_shape(doc, grp, "hanger_webs_" + tag, "hanger_webs_6mm_" + tag, G.hanger_webs(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_M10_" + tag, G.hanger_bolts(sx), "zinc")
    add_shape(doc, grp, "pivot_lugs", "pivot_lugs_8mm_4x", G.pivot_lugs(), "frame")
    add_shape(doc, grp, "pivot_pins", "pivot_pins_D20_R_clip", G.pivot_pins(), "zinc")
    add_shape(doc, grp, "act_mast", "actuator_mast_2x8mm", G.act_mast(), "frame")
    return grp


def build_harrow(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Harrow", "harrow_turns_about_pivot", lift_placement(lift))
    add_shape(doc, grp, "harrow_frame", "harrow_frame_weldment_arms_main_beam_tine_bars", G.harrow_frame(), "frame")
    add_shape(doc, grp, "board", "levelling_board_angle_100x100x8_L%d" % (2 * P.frame_x), G.board(), "board")
    add_shape(doc, grp, "board_straps", "board_straps_60x8", G.board_straps(), "board")
    add_shape(doc, grp, "tines", "spring_tines_D8_%d" % (len(P.tine_x(0)) + len(P.tine_x(1))), G.tines(), "tine")
    add_shape(doc, grp, "tine_clamps", "tine_clamps_U_bolt_M8", G.tine_clamps(), "zinc")
    return grp


def build_actuator(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Actuator", "lift_actuator_24V_1500N_stroke_100")
    body, rod, _ = G.actuator(lift)
    add_shape(doc, grp, "act_body", "actuator_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "actuator_rod_clevis", rod, "steel")
    return grp


def build_into(doc, parent=None, lift=P.lift_work):
    """Put the harrow in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "grassland_harrow_simple")
    build_mount(doc, root)
    build_harrow(doc, root, lift)
    build_actuator(doc, root, lift)
    return root


def set_pose(lift=P.lift_work, doc=None):
    doc = active_doc(doc)
    doc.getObject("Harrow").Placement = lift_placement(lift)
    body, rod, _ = G.actuator(lift)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod


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


def build(save=True, show_robot=False, step=True, lift=P.lift_work):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Grassland harrow simple"
    doc.Comment = ("Generated by build_gha.py from gha_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Work pose; build_gha.set_pose() lifts the harrow.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, lift)
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


# pins, bolts and clamps pass through holes in or touch the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "harrow_frame"), ("pivot_pins", "pivot_lugs"), ("act_body", "act_mast"),
          ("act_rod", "harrow_frame"), ("act_body", "act_rod"), ("hanger_bolts_left", "hanger_top_left"),
          ("hanger_bolts_right", "hanger_top_right"), ("tine_clamps", "tines"), ("tine_clamps", "harrow_frame"),
          ("board_straps", "harrow_frame"), ("board_straps", "board")}


def _joint(a, b):
    return (a, b) in JOINTS or (b, a) in JOINTS or (a.startswith("hanger_bolts") and b.startswith("lower_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: harrow parts among themselves and against the robot.
    Pins, bolts and clamps in their own holes are skipped (JOINTS)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    """Interference over the lift poses: only the moving parts (harrow, actuator) against everything else and each
    other; the fixed pairs do not change (check_interference). Must be empty."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Harrow") + objects_of(doc, "Actuator")
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for lift in P.LIFT_POSES:
        set_pose(lift, doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[lift] = hits
    set_pose(P.lift_work, doc)
    return out


def clearance(doc=None, names=("RL_top_plate", "RR_top_plate", "RL_side_l", "RR_side_r")):
    """Smallest distance (mm) of the harrow and actuator to the rear tyres (plain cylinder O430 x 100: the lugged
    tyre is far too slow for distToShape) and the wheel brackets, work and transport."""
    doc = active_doc(doc)
    targets = [global_shape(doc.getObject(n)) for n in names if doc.getObject(n) is not None]
    for sx in (-1, 1):
        targets.append(Part.makeCylinder(P.robot_tire_d / 2.0, 100.0, V(sx * 375.0 - 50.0, -P.robot_axle_y, 215.0),
                                         V(1, 0, 0)))
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, doc)
        best = (1e9, None)
        for o in objects_of(doc, "Harrow") + objects_of(doc, "Actuator"):
            s = global_shape(o)
            for t in targets:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name)
        out[lift] = (round(best[0], 1), best[1])
    set_pose(P.lift_work, doc)
    return out


def ground_contact(doc=None):
    """Lowest point (z) of the board and the tines, work and transport."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, doc)
        out[lift] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1) for n in ("board", "tines")}
    set_pose(P.lift_work, doc)
    return out


MASS_FIXED = {"act_body": P.act_kg - 0.6, "act_rod": 0.6}
DENSITY = (("toolbar_caps", 0.95e-6),)


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole harrow, the moving harrow and the mount."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Harrow", "Mount"):
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
    add_floor(doc, y=(-1700.0, 900.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.2, -0.7), target=(0, -600, 350)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, -700, 350), height=1500))
    set_pose(P.lift_transport, doc)
    out.append(save_view("3_side_transport.png", (1.0, 0.0, 0.0), target=(0, -700, 350), height=1500))
    set_pose(P.lift_work, doc)
    remove(doc, [GROUND])
    out.append(save_view("4_top.png", (0.0, 0.0, -1.0), target=(0, -500, 0), up=(0.0, 1.0, 0.0), height=2300))
    set_robot_visible(False, doc)
    out.append(save_view("5_harrow_iso_from_below.png", (-0.8, -1.0, 0.45), target=(0, -1100, 150), height=1500))
    out.append(save_view("6_tine_detail.png", (1.0, -0.5, -0.4), target=(400, -1250, 200), height=500))
    App.closeDocument(doc.Name)
    build()
    return out
