"""Model of the push blade on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_pbl
    build_pbl.build()                      # saves FCStd and STEP (work pose: blade down, straight)
    build_pbl.set_pose(lift=18, angle=25)  # lift of the arms (deg, + = up), blade angle (deg, + = right end forward)
    build_pbl.check_interference()         # overlap in the current pose (must be empty)
    build_pbl.check_poses()                # overlap over all lift and angle poses and steering +-30 (must be empty)
    build_pbl.clearance()                  # smallest distance of the blade group to the front tyres over the poses
    build_pbl.mass_properties()
    build_pbl.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import pbl_params as P
import pbl_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Push_Blade"
SAVE_BASE = os.path.join(FOLDER, "Push_Blade")
ROOT = "Push_blade"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "blade": (0.95, 0.75, 0.10),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "rubber": (0.10, 0.10, 0.10),
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
    """Rotation of the lift group about the pivot axis (x)."""
    c = V(0, P.pivot[0], P.pivot[1])
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), lift_deg), c)


def blade_placement(angle_deg):
    """Rotation of the blade about the king pin (z); + = right end forward."""
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle_deg), V(0, P.king_y, 0))


def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_front_toolbar")
    add_shape(doc, grp, "toolbar", "front_toolbar_80x80x4_L900", G.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_caps", "toolbar_end_caps_PE", G.toolbar_caps(), "plastic")
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "hanger_top_" + tag, "hanger_top_plate_10mm_" + tag, G.hanger_top(sx), "frame")
        add_shape(doc, grp, "hanger_webs_" + tag, "hanger_webs_6mm_" + tag, G.hanger_webs(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_M10_" + tag, G.hanger_bolts(sx), "zinc")
    add_shape(doc, grp, "pivot_lugs", "pivot_lugs_8mm_4x", G.pivot_lugs(), "frame")
    add_shape(doc, grp, "pivot_pins", "pivot_pins_D20_R_clip", G.pivot_pins(), "zinc")
    add_shape(doc, grp, "act_mast", "actuator_mast_2x8mm", G.act_mast(), "frame")
    return grp


def build_lift(doc, parent, lift=P.lift_work, angle=0.0):
    lift_grp = new_part(doc, parent, "Lift", "lift_arms_turn_about_pivot", lift_placement(lift))
    add_shape(doc, lift_grp, "carrier", "carrier_weldment_arms_60x40_cross_60x60_head_plate", G.carrier(), "frame")
    add_shape(doc, lift_grp, "king_pin", "king_pin_M30_PE_washer", G.king_pin(), "zinc")
    add_shape(doc, lift_grp, "lock_pin", "angle_lock_pin_D16", G.lock_pin(), "zinc")
    blade = new_part(doc, lift_grp, "Blade", "blade_turns_about_king_pin", blade_placement(angle))
    add_shape(doc, blade, "moldboard", "moldboard_3mm_R%d_%dx%d" % (P.blade_r, P.blade_w, P.blade_h), G.moldboard(),
              "blade")
    add_shape(doc, blade, "blade_frame", "blade_frame_beam_80x60_ribs_swivel_plate", G.blade_frame(), "blade")
    add_shape(doc, blade, "side_plates", "blade_end_plates_6mm", G.side_plates(), "blade")
    add_shape(doc, blade, "rubber_edge", "rubber_edge_%dx%d" % (P.edge_h, P.edge_t), G.rubber_edge(), "rubber")
    add_shape(doc, blade, "clamp_bar", "edge_clamp_bar_40x6", G.clamp_bar(), "zinc")
    add_shape(doc, blade, "edge_bolts", "edge_bolts_M10_carriage", G.edge_bolts(), "zinc")
    return lift_grp


def build_actuator(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Actuator", "lift_actuator_24V_1500N_stroke_100")
    body, rod, _ = G.actuator(lift)
    add_shape(doc, grp, "act_body", "actuator_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "actuator_rod_clevis", rod, "steel")
    return grp


def build_into(doc, parent=None, lift=P.lift_work, angle=0.0):
    """Put the push blade in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "push_blade_simple")
    build_mount(doc, root)
    build_lift(doc, root, lift, angle)
    build_actuator(doc, root, lift)
    return root


def set_pose(lift=P.lift_work, angle=0.0, doc=None):
    doc = active_doc(doc)
    doc.getObject("Lift").Placement = lift_placement(lift)
    doc.getObject("Blade").Placement = blade_placement(angle)
    body, rod, _ = G.actuator(lift)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod


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


def build(save=True, show_robot=False, step=True, lift=P.lift_work, angle=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Push blade simple"
    doc.Comment = ("Generated by build_pbl.py from pbl_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Work pose; build_pbl.set_pose() lifts and angles the blade.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, lift, angle)
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


# pins and bolts pass through holes in the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "carrier"), ("pivot_pins", "pivot_lugs"), ("king_pin", "carrier"), ("king_pin", "blade_frame"),
          ("lock_pin", "carrier"), ("lock_pin", "blade_frame"), ("act_body", "act_mast"), ("act_rod", "carrier"),
          ("act_body", "act_rod"), ("edge_bolts", "moldboard"), ("edge_bolts", "rubber_edge"),
          ("edge_bolts", "clamp_bar"), ("hanger_bolts_left", "hanger_top_left"),
          ("hanger_bolts_right", "hanger_top_right")}


def _joint(a, b):
    return (a, b) in JOINTS or (b, a) in JOINTS or (a.startswith("hanger_bolts") and b.startswith("lower_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: implement parts among themselves and against the robot.
    Pins and bolts in their own holes are skipped (JOINTS); their holes are checked by check_holes()."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """The pins and bolts must sit in holes: overlap of the JOINTS pairs (should be ~0)."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    out = {}
    for a, b in JOINTS:
        if (a, b) == ("act_body", "act_rod"):
            continue                                # the rod runs inside the body
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[(a, b)] = round(v, 1)
    return out


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Interference over the lift poses x blade angles x steering angles: only the moving parts (lift group,
    actuator) against everything else and each other; the fixed pairs do not change (check_interference).
    Must be empty."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Lift") + objects_of(doc, "Actuator")
    names = {o.Name for o in moving}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for lift in P.LIFT_POSES:
            for ang in (P.angle_steps[0], 0.0, P.angle_steps[-1]):
                set_pose(lift, ang, doc)
                mv = [(o, global_shape(o)) for o in moving]
                pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
                pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                          if not _joint(mv[i][0].Name, mv[j][0].Name)]
                hits = _overlaps(pairs, tol)
                if hits:
                    out[(st, lift, ang)] = hits
    set_steering(0.0, doc)
    set_pose(P.lift_work, 0.0, doc)
    return out


def tyre_envelope(tag_x, steer):
    """Plain cylinder O430 x 100 for a front tyre (the lugged tyre is far too slow for distToShape)."""
    c = V(tag_x, P.robot_axle_y, P.robot_axle_z)
    t = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, c - V(P.robot_tire_w / 2.0, 0, 0), V(1, 0, 0))
    t.rotate(V(tag_x, P.robot_axle_y, 0), V(0, 0, 1), steer)
    return t


def clearance(doc=None, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Smallest distance (mm) of the carrier and the blade to the front tyres over the poses (tyre envelope)."""
    doc = active_doc(doc)
    moving = [doc.getObject(n) for n in ("carrier", "blade_frame", "moldboard", "side_plates", "rubber_edge")]
    best = (1e9, None, None)
    for st in steer:
        tg = [tyre_envelope(sx * P.robot_wheel_x, st) for sx in (-1, 1)]
        for lift in (P.LIFT_POSES[0], P.LIFT_POSES[-1]):
            for ang in (P.angle_steps[0], P.angle_steps[-1]):
                set_pose(lift, ang, doc)
                for o in moving:
                    s = global_shape(o)
                    for t in tg:
                        d = s.distToShape(t)[0]
                        if d < best[0]:
                            best = (d, o.Name, (st, lift, ang))
    set_pose(P.lift_work, 0.0, doc)
    return round(best[0], 1), best[1], best[2]


MASS_FIXED = {"act_body": P.act_kg - 0.6, "act_rod": 0.6}
DENSITY = (("rubber_edge", P.rubber), ("toolbar_caps", 0.95e-6))


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole blade, the lift group and the mount."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Lift", "Mount"):
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
    add_floor(doc)
    out.append(save_view("1_iso_front_on_robot.png", (-1.0, -1.2, -0.7), target=(0, 500, 350)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, 650, 400), height=1500))
    set_pose(P.lift_transport, 0.0, doc)
    out.append(save_view("3_side_transport.png", (1.0, 0.0, 0.0), target=(0, 650, 400), height=1500))
    remove(doc, [GROUND])
    set_pose(P.lift_work, P.angle_steps[-1], doc)
    set_steering(P.robot_steer_deg, doc)
    out.append(save_view("4_top_angled_25deg.png", (0.0, 0.0, -1.0), target=(0, 450, 0), up=(0.0, 1.0, 0.0),
                         height=2200))
    set_steering(0.0, doc)
    set_pose(P.lift_work, 0.0, doc)
    set_robot_visible(False, doc)
    out.append(save_view("5_blade_iso_rear.png", (1.0, 1.0, -0.6), target=(0, 950, 300), height=1500))
    out.append(save_view("6_king_pin_detail.png", (0.8, 0.6, -0.9), target=(0, 1030, 300), height=650))
    App.closeDocument(doc.Name)
    build()
    return out
