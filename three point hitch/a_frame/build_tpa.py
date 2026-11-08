"""Model of the A-frame hitch (triangle quick coupler, LA36 as top link) with the small cultivator on the Bruut OpenAgbot
(standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_tpa
    build_tpa.build()                      # saves FCStd and STEP (work pose: cultivator on its gauge wheels)
    build_tpa.set_pose(lift=25.6)          # angle of the lift frame (deg, + = up), LA36 carrying
    build_tpa.check_interference()         # overlap in the current pose (must be empty)
    build_tpa.check_poses()                # overlap over the lift and float poses (must be empty)
    build_tpa.clearance()                  # smallest distance to the rear tyres and wheel units
    build_tpa.ground_contact()             # lowest point of shares and gauge wheels
    build_tpa.mass_properties()
    build_tpa.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tpa_params as P
import tpa_parts as G
import tph_parts as TG

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Three_Point_Hitch_A_Frame"
SAVE_BASE = os.path.join(FOLDER, "Three_Point_Hitch_A_Frame")
ROOT = "TPA_hitch"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "coupler": (0.85, 0.12, 0.10),
    "implement": (0.10, 0.40, 0.70),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "tine": (0.15, 0.15, 0.16),
    "rubber": (0.12, 0.12, 0.12),
    "actuator": (0.25, 0.26, 0.28),
    "chrome": (0.86, 0.87, 0.90),
    "plastic": (0.10, 0.10, 0.10),
    "handle": (0.95, 0.80, 0.10),
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


def frame_placement(lift_deg):
    """Rotation of the lift frame (and the coupled implement) about the lower pivots; + = up."""
    c = V(0, P.lower_a[0], P.lower_a[1])
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -lift_deg), c)


def actuator_pose(lift_deg, act_len=None):
    """(body pin, rod pin, length) of the LA36: act_len None = carrying (rod pin at the slot end), else floating."""
    return P.act_c, P.act_pin(lift_deg, act_len)


ROD_REF = P.act_retracted       # the rod shape is drawn with its eye at this length; the placement slides it


def build_mount(doc, parent):
    grp = new_part(doc, parent, "TPA_Mount", "mount_rear_toolbar_and_tower")
    add_shape(doc, grp, "toolbar", "rear_toolbar_80x80x4_L900", TG.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_caps", "toolbar_end_caps_PE", TG.toolbar_caps(), "plastic")
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "hanger_top_" + tag, "hanger_top_plate_10mm_" + tag, TG.hanger_top(sx), "frame")
        add_shape(doc, grp, "hanger_webs_" + tag, "hanger_webs_6mm_" + tag, TG.hanger_webs(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_M10_" + tag, TG.hanger_bolts(sx), "zinc")
    add_shape(doc, grp, "lower_lugs", "lower_arm_lugs_8mm_4x", TG.lower_lugs(), "frame")
    add_shape(doc, grp, "pivot_pins", "lower_arm_pivot_pins_D16", G.pivot_pins(), "zinc")
    add_shape(doc, grp, "tower", "LA36_tower_post_60x60x4_with_gussets", G.tower(), "frame")
    add_shape(doc, grp, "tower_clevis", "LA36_body_clevis_2x8mm", G.tower_clevis(), "frame")
    add_shape(doc, grp, "tower_pin", "LA36_body_pin_D12", G.tower_pin(), "zinc")
    return grp


def build_frame(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "TPA_LiftFrame", "lift_frame_arms_triangle_turns_about_pivots",
                   frame_placement(lift))
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "arm_" + tag, "lower_arm_50x20_" + tag, G.arm(sx), "frame")
    add_shape(doc, grp, "arm_cross", "arm_cross_tube_40x40x3_brace_lugs", G.arm_cross(), "frame")
    add_shape(doc, grp, "brace", "pitch_brace_turnbuckle_D26", G.brace(), "zinc")
    add_shape(doc, grp, "male_frame", "A_frame_male_triangle_40x40x3", G.male_frame(), "coupler")
    add_shape(doc, grp, "male_latch", "A_frame_latch_pin_D20_T_handle", G.male_latch(), "handle")
    add_shape(doc, grp, "frame_pins", "lower_pins_D16_brace_pins_D16", G.frame_pins(), "zinc")
    return grp


def build_actuator(doc, parent, lift=P.lift_work, act_len=None):
    grp = new_part(doc, parent, "TPA_Actuator", "linak_LA36_%s_stroke%d_as_top_link" % (P.act_variant, P.act_stroke))
    add_shape(doc, grp, "act_body", "linak_LA36_24V_housing_motor_outer_tube", G.la36_body(), "actuator")
    pin_half = P.act_rod_eye_c / 2.0 + P.act_eye_clear + 8.0 + 4.0
    add_shape(doc, grp, "act_rod", "linak_LA36_inner_tube_rod_eye_pin_D12", G.la36_rod(ROD_REF, pin_half=pin_half),
              "chrome")
    set_actuator(doc, lift, act_len)
    return grp


def set_actuator(doc, lift, act_len=None):
    d, c = actuator_pose(lift, act_len)
    pb, pr, L = G.la36_placements(d, c, ROD_REF)
    doc.getObject("act_body").Placement = pb
    doc.getObject("act_rod").Placement = pr
    return L


def build_implement(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "TPA_Implement", "small_cultivator_with_female_A_frame", frame_placement(lift))
    add_shape(doc, grp, "imp_frame", "cultivator_toolbar_60x60_female_A_frame_stays_gauge_arms",
              G.cultivator_frame(), "implement")
    add_shape(doc, grp, "tine_clamps", "tine_clamps_5x", G.cult_clamps(), "zinc")
    add_shape(doc, grp, "tines", "S_tines_32x10_5x", G.cult_tines(), "steel")
    add_shape(doc, grp, "shares", "duckfoot_shares_100", G.cult_shares(), "tine")
    add_shape(doc, grp, "gauge_wheels", "gauge_wheels_D250x80_2x", G.cult_wheels(), "rubber")
    add_shape(doc, grp, "wheel_axles", "gauge_wheel_axles_D20", G.cult_axles(), "zinc")
    return grp


def build_into(doc, parent=None, lift=P.lift_work):
    """Put the hitch and the cultivator in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "three_point_hitch_A_frame_LA36")
    build_mount(doc, root)
    build_frame(doc, root, lift)
    build_actuator(doc, root, lift)
    build_implement(doc, root, lift)
    return root


def set_pose(lift=P.lift_work, doc=None, act_len=None, implement=True):
    """Lift frame angle (deg) and the LA36; act_len = fixed actuator length in work (rod pin floats in the slot)."""
    doc = active_doc(doc)
    pl = frame_placement(lift)
    doc.getObject("TPA_LiftFrame").Placement = pl
    if implement and doc.getObject("TPA_Implement") is not None:
        doc.getObject("TPA_Implement").Placement = pl
    return set_actuator(doc, lift, act_len)


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
    doc.Label = "Three-point hitch A-frame"
    doc.Comment = ("Generated by build_tpa.py from tpa_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Work pose; build_tpa.set_pose() lifts the implement.")
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


# pins and bolts pass through holes in the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "lower_lugs"), ("pivot_pins", "arm_left"), ("pivot_pins", "arm_right"),
          ("frame_pins", "arm_left"), ("frame_pins", "arm_right"), ("frame_pins", "male_frame"),
          ("frame_pins", "arm_cross"), ("frame_pins", "brace"), ("tower_pin", "tower_clevis"),
          ("tower_pin", "act_body"), ("act_rod", "male_frame"), ("act_body", "act_rod"), ("male_latch", "male_frame"),
          ("male_latch", "imp_frame"), ("arm_cross", "arm_left"), ("arm_cross", "arm_right"),
          ("tine_clamps", "tines"), ("tine_clamps", "imp_frame"), ("tines", "shares"), ("wheel_axles", "imp_frame"),
          ("wheel_axles", "gauge_wheels"), ("hanger_bolts_left", "hanger_top_left"),
          ("hanger_bolts_right", "hanger_top_right"), ("tower", "toolbar")}


def _joint(a, b):
    return (a, b) in JOINTS or (b, a) in JOINTS or (a.startswith("hanger_bolts") and b.startswith("lower_beam")) or \
        (b.startswith("hanger_bolts") and a.startswith("lower_beam"))


MOVING = ("TPA_LiftFrame", "TPA_Actuator", "TPA_Implement")


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: hitch and implement parts among themselves and against the robot.
    Pins and bolts in their own holes are skipped (JOINTS)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0, poses=None):
    """Interference over the lift poses (LA36 carrying) and the float poses (LA36 at its work length): the moving
    parts against the fixed parts and each other. Must be empty."""
    doc = active_doc(doc)
    moving = [o for n in MOVING for o in objects_of(doc, n)]
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    poses = poses or [(x, None) for x in P.LIFT_POSES] + [(x, P.act_work_length()) for x in P.lift_float]
    for lift, act_len in poses:
        set_pose(lift, doc, act_len)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[str((lift, act_len))] = hits
    set_pose(doc=doc)
    return out


def clearance(doc=None, names=("RL_top_plate", "RR_top_plate", "RL_side_l", "RR_side_r")):
    """Smallest distance (mm) of the moving parts to the rear tyres (plain cylinder) and wheel brackets."""
    doc = active_doc(doc)
    targets = [global_shape(doc.getObject(n)) for n in names if doc.getObject(n) is not None]
    for sx in (-1, 1):
        targets.append(Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w,
                                         V(sx * P.robot_wheel_x - P.robot_tire_w / 2.0, -P.robot_axle_y, 215.0),
                                         V(1, 0, 0)))
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, doc)
        best = (1e9, None)
        for o in [o for n in MOVING for o in objects_of(doc, n)]:
            s = global_shape(o)
            for t in targets:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name)
        out[lift] = (round(best[0], 1), best[1])
    set_pose(doc=doc)
    return out


def ground_contact(doc=None):
    """Lowest point (z) of shares and gauge wheels and the height of the lower pins, work and transport."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, doc)
        out[lift] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1) for n in ("shares", "gauge_wheels")}
        out[lift]["lower_pin_z"] = round(P.lower_pin(lift)[1], 1)
    set_pose(doc=doc)
    return out


MASS_FIXED = {"act_body": P.act_mass() - 0.6, "act_rod": 0.6}
DENSITY = (("toolbar_caps", 0.95e-6), ("gauge_wheels", P.rubber))


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


def sum_mass(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates, work pose) of the whole hitch with implement and its
    groups."""
    doc = active_doc(doc)
    set_pose(doc=doc)
    out = {}
    for name in (ROOT, "TPA_Mount", "TPA_LiftFrame", "TPA_Actuator", "TPA_Implement"):
        m, c = sum_mass(objects_of(doc, name))
        key = name.replace("TPA_", "").lower()
        out[key + "_kg"] = round(m, 1)
        out[key + "_cg"] = (round(c.x), round(c.y), round(c.z))
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
    view = Gui.getDocument(DOC_NAME).ActiveView if DOC_NAME in App.listDocuments() else Gui.ActiveDocument.ActiveView
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
    obj.Shape = TG.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.72, 0.72, 0.70)
    obj.ViewObject.Transparency = 30
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_visible(doc, group, visible):
    for o in objects_of(doc, group):
        o.ViewObject.Visibility = visible


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    import FreeCADGui as Gui
    out = []
    doc = build(save=False, show_robot=True, step=False)
    Gui.getDocument(doc.Name)
    App.setActiveDocument(doc.Name)
    add_floor(doc, y=(-1900.0, 900.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.2, -0.7), target=(0, -800, 450)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, -1000, 520), height=1500))
    set_pose(P.lift_transport, doc)
    out.append(save_view("3_side_transport.png", (1.0, 0.0, 0.0), target=(0, -1000, 520), height=1500))
    out.append(save_view("4_iso_transport.png", (-1.0, 1.2, -0.7), target=(0, -900, 500), height=1700))
    set_pose(doc=doc)
    remove(doc, [GROUND])
    out.append(save_view("5_top.png", (0.0, 0.0, -1.0), target=(0, -850, 0), up=(0.0, 1.0, 0.0), height=2100))
    out.append(save_view("6_rear.png", (0.0, 1.0, 0.0), target=(0, -1000, 520), height=1300))
    set_robot_visible(False, doc)
    set_visible(doc, "TPA_Implement", False)
    out.append(save_view("7_male_triangle_and_LA36.png", (-1.0, 0.8, -0.45), target=(0, -1030, 560), height=1050))
    set_visible(doc, "TPA_Implement", True)
    set_visible(doc, "TPA_LiftFrame", False)
    set_visible(doc, "TPA_Actuator", False)
    out.append(save_view("8_female_triangle_on_cultivator.png", (1.0, 0.8, -0.45), target=(0, -1300, 400),
                         height=1100))
    set_visible(doc, "TPA_LiftFrame", True)
    set_visible(doc, "TPA_Actuator", True)
    out.append(save_view("9_coupler_side_section.png", (1.0, 0.0, 0.0), target=(0, -1180, 430), height=650))
    App.closeDocument(doc.Name)
    build()
    return out
