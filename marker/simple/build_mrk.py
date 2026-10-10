"""Model of the field marker on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_mrk
    build_mrk.build()                              # saves FCStd and STEP (nozzle in the middle, parked)
    build_mrk.set_pose(x=300, y=-950, zc=build_mrk.P.ZC_WORK, lift=6)   # move the stage (slides only)
    build_mrk.check_interference()                 # overlap in the current pose (must be empty)
    build_mrk.check_fit()                          # overlap in all corner poses of the stage (must be empty)
    build_mrk.clearance()                          # smallest distance to the rear tyres and wheel brackets
    build_mrk.mass_properties()
    build_mrk.render_all()                         # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrk_params as P
import mrk_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Field_Marker"
SAVE_BASE = os.path.join(FOLDER, "Field_Marker")

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "alu": (0.80, 0.81, 0.83),
    "module": (0.70, 0.72, 0.75),
    "carriage": (0.20, 0.21, 0.23),
    "motor": (0.08, 0.08, 0.08),
    "pvc": (0.55, 0.57, 0.60),
    "paint": (0.98, 0.20, 0.55),
    "plastic": (0.10, 0.10, 0.10),
    "box": (0.55, 0.57, 0.60),
    "white": (0.96, 0.96, 0.95),
    "sensor": (0.85, 0.65, 0.10),
    "spring": (0.30, 0.30, 0.32),
}


# ---------------------------------------------------------------------
# Tree helpers (same as build_dbr.py)
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


# ---------------------------------------------------------------------
# Pose of the stage. x, y = nozzle axis (robot coordinates), zc = Z carriage centre, lift = shroud pushed up.
# ---------------------------------------------------------------------
SLIDES = ("X_slide", "Y_slide", "Z_slide", "Shroud")


def pose_placements(x=None, y=None, zc=None, lift=None):
    r = G.REF
    x = r["x"] if x is None else x
    y = r["y"] if y is None else y
    zc = r["zc"] if zc is None else zc
    lift = r["lift"] if lift is None else lift
    lim = (-P.x_stroke / 2.0, P.x_stroke / 2.0), (P.y_tool_front - P.y_stroke, P.y_tool_front), P.zc_range
    for name, val, (a, b) in (("x", x, lim[0]), ("y", y, lim[1]), ("zc", zc, lim[2])):
        if not a - 1e-6 <= val <= b + 1e-6:
            raise ValueError("%s = %.1f outside the stroke %.1f .. %.1f" % (name, val, a, b))
    if not 0.0 <= lift <= P.shroud_travel:
        raise ValueError("lift = %.1f outside 0 .. %.1f" % (lift, P.shroud_travel))
    return {"X_slide": App.Placement(V(x - r["x"], 0, 0), App.Rotation()),
            "Y_slide": App.Placement(V(0, y - r["y"], 0), App.Rotation()),
            "Z_slide": App.Placement(V(0, 0, zc - r["zc"]), App.Rotation()),
            "Shroud": App.Placement(V(0, 0, lift), App.Rotation())}


def set_pose(x=None, y=None, zc=None, lift=None, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(x, y, zc, lift).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_hangers_control_box")
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "hanger_" + tag, "hanger_welded_10_8_8mm_" + tag, G.hanger(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_4xM10_4xM8_" + tag, G.hanger_bolts(sx), "zinc")
    add_shape(doc, grp, "box_base", "control_box_base_plate_3mm", G.box_base(), "zinc")
    add_shape(doc, grp, "control_box", "control_box_IP66_3x_stepper_driver", G.control_box(), "box")
    add_shape(doc, grp, "box_bolts", "control_box_bolts_M8", G.box_bolts(), "zinc")
    return grp


def build_x_axis(doc, parent):
    grp = new_part(doc, parent, "X_axis", "x_axis_belt_module_stroke_%d" % P.x_stroke)
    add_shape(doc, grp, "x_module", "x_linear_module_belt_80_L%d" % P.xm_len, G.x_module(), "module")
    add_shape(doc, grp, "x_motor", "x_motor_nema23_closed_loop", G.x_motor(), "motor")
    return grp


def build_x_slide(doc, parent, pl):
    sl = new_part(doc, parent, "X_slide", "x_slide_moves_in_x", pl["X_slide"])
    add_shape(doc, sl, "x_carriage", "x_carriage_80x150", G.x_carriage(), "carriage")
    add_shape(doc, sl, "xy_adapter", "xy_bracket_adapter_plate_8mm", G.xy_adapter(), "frame")
    add_shape(doc, sl, "y_plate", "xy_bracket_y_plate_8mm", G.y_plate(), "frame")
    add_shape(doc, sl, "gussets", "xy_bracket_gussets_8mm", G.gussets(), "frame")
    add_shape(doc, sl, "y_module", "y_linear_module_sfu1605_stroke_%d" % P.y_stroke, G.y_module(), "module")
    add_shape(doc, sl, "y_motor", "y_motor_nema23_closed_loop", G.y_motor(), "motor")
    return sl


def build_y_slide(doc, parent, pl):
    sl = new_part(doc, parent, "Y_slide", "y_slide_moves_in_y", pl["Y_slide"])
    add_shape(doc, sl, "y_carriage", "y_carriage_60x80", G.y_carriage(), "carriage")
    add_shape(doc, sl, "z_adapter", "z_adapter_plate_alu_10mm", G.z_adapter(), "alu")
    add_shape(doc, sl, "z_module", "z_linear_module_sfu1605_stroke_%d" % P.z_stroke, G.z_module(), "module")
    add_shape(doc, sl, "z_motor", "z_motor_nema23_closed_loop", G.z_motor(), "motor")
    add_shape(doc, sl, "mast_bracket", "mast_bracket_alu_10mm", G.mast_bracket(), "alu")
    add_shape(doc, sl, "mast", "mast_tube_25x2_collar", G.mast(), "alu")
    add_shape(doc, sl, "antenna", "gnss_antenna_on_nozzle_axis", G.antenna(), "white")
    add_shape(doc, sl, "rx_box", "gnss_receiver_imu_box", G.rx_box(), "box")
    return sl


def build_z_slide(doc, parent, pl):
    sl = new_part(doc, parent, "Z_slide", "z_slide_moves_in_z", pl["Z_slide"])
    add_shape(doc, sl, "z_carriage", "z_carriage_60x80", G.z_carriage(), "carriage")
    add_shape(doc, sl, "head_mount", "head_mount_plate_alu_8mm", G.head_mount(), "alu")
    add_shape(doc, sl, "hook_pins", "head_hook_pins_D12", G.hook_pins(), "steel")
    add_shape(doc, sl, "knobs", "head_star_knobs_M8", G.knobs(), "plastic")
    head = new_part(doc, sl, "Head", "paint_head_quick_change")
    add_shape(doc, head, "head_plate", "head_plate_alu_6mm_bent", G.head_plate(), "alu")
    add_shape(doc, head, "guide_tube", "guide_tube_pvc_75x1.8", G.guide_tube(), "pvc")
    add_shape(doc, head, "spray_can", "marking_spray_can_500ml_inverted", G.spray_can(), "paint")
    add_shape(doc, head, "pusher", "can_pusher_disc", G.pusher(), "plastic")
    add_shape(doc, head, "u_bolts", "u_bolts_M8_76mm", G.u_bolts(), "zinc")
    add_shape(doc, head, "servo_bracket", "servo_bracket_alu_3mm", G.servo_bracket(), "alu")
    add_shape(doc, head, "servo", "servo_35kgcm_waterproof", G.servo(), "plastic")
    add_shape(doc, head, "lever", "servo_lever_alu_3mm", G.lever(), "alu")
    add_shape(doc, head, "bushings", "flanged_bushings_10x12", G.bushings(), "steel")
    add_shape(doc, head, "springs", "shroud_springs", G.springs(), "spring")
    add_shape(doc, head, "sensor", "touch_off_sensor_M12_inductive", G.sensor(), "sensor")
    sh = new_part(doc, head, "Shroud", "spray_shroud_sprung", pl["Shroud"])
    add_shape(doc, sh, "shroud_ring", "shroud_ring_alu_4mm", G.shroud_ring(), "alu")
    add_shape(doc, sh, "shroud_tube", "shroud_pvc_110x3.2", G.shroud_tube(), "pvc")
    add_shape(doc, sh, "rods", "shroud_rods_D10_stainless", G.rods(), "steel")
    add_shape(doc, sh, "collars", "shroud_rod_collars", G.collars(), "zinc")
    return sl


def build_into(doc, parent=None, x=None, y=None, zc=None, lift=None):
    """Put the marker in a document, in robot coordinates (also used by animate_mrk.py)."""
    pl = pose_placements(x, y, zc, lift)
    root = new_part(doc, parent, "Field_marker", "field_marker_simple")
    build_mount(doc, root)
    build_x_axis(doc, root)
    xs = build_x_slide(doc, root, pl)
    ys = build_y_slide(doc, xs, pl)
    build_z_slide(doc, ys, pl)
    return root


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


def build(x=None, y=None, zc=None, lift=None, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Field marker simple"
    doc.Comment = ("Generated by build_mrk.py from mrk_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Stage behind the robot; move it with build_mrk.set_pose().")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, x, y, zc, lift)
    if robot is not None and not show_robot:
        set_robot_visible(False, doc)
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
    if d is not None and d.getObject("Field_marker") is not None:
        return d
    for n in App.listDocuments():
        d = App.getDocument(n)
        if d.getObject("Field_marker") is not None:
            return d
    raise RuntimeError("no marker document open")


def marker_objects(doc):
    return [o for o in doc.getObject("Field_marker").OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in marker_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in marker_objects(doc):
        f = doc.addObject("Part::Feature", "step_" + o.Name)
        f.Label = o.Label
        f.Shape = global_shape(o)
        objs.append(f)
    try:
        Import.export(objs, path)
    finally:
        for f in objs:
            doc.removeObject(f.Name)


# ---------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


EXCLUDE = ("springs",)          # compliant: drawn at free length, compressed when the shroud lifts


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


def _checked(objs):
    return [o for o in objs if not o.Name.startswith(EXCLUDE)]


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3) in the current pose: marker parts among themselves and against the (visible and hidden)
    robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in _checked(marker_objects(doc))]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def fit_poses():
    """x at the ends and at the tyres, y at both ends, Z in steps of 50 mm, plus the shroud fully pushed up."""
    xs = (-P.x_stroke / 2.0, -P.robot_wheel_x, 0.0, P.robot_wheel_x, P.x_stroke / 2.0)
    ys = (P.y_tool_front, P.y_tool_front - P.y_stroke)
    n = int(round((P.zc_range[1] - P.zc_range[0]) / 50.0))
    zs = [P.zc_range[0] + i * (P.zc_range[1] - P.zc_range[0]) / n for i in range(n + 1)]
    out = [(x, y, zc, 0.0) for x in xs for y in ys for zc in zs]
    out += [(x, P.y_tool_front, zc, P.shroud_travel) for x in (-P.robot_wheel_x, P.robot_wheel_x)
            for zc in (P.ZC_WORK, P.zc_range[0])]
    return out


def _slide_of(obj):
    """Nearest moving group of an object ('fixed' for the mount and the X module). Head moves with Z_slide."""
    parent = obj.getParentGeoFeatureGroup()
    while parent is not None:
        if parent.Name in SLIDES:
            return parent.Name
        parent = parent.getParentGeoFeatureGroup()
    return "fixed"


def check_fit(doc=None, poses=None, tol=1.0):
    """Interference over the whole stroke of the stage (see fit_poses). Only pairs that move relative to each other
    are checked again per pose. Must be empty."""
    doc = active_doc(doc)
    set_pose(doc=doc)
    out = {}
    base = check_interference(doc, tol)
    if base:
        out["reference"] = base
    mine = _checked(marker_objects(doc))
    group = {o.Name: _slide_of(o) for o in mine}
    moving = [o for o in mine if group[o.Name] != "fixed"]
    fixed = [(o, global_shape(o)) for o in mine if group[o.Name] == "fixed"]
    fixed += [(o, global_shape(o)) for o in robot_objects(doc)]
    for pose in poses or fit_poses():
        set_pose(*pose, doc=doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if group[mv[i][0].Name] != group[mv[j][0].Name]]
        hits = _overlaps(pairs, tol)
        if hits:
            out[pose] = hits
    set_pose(doc=doc)
    return out


def clearance(doc=None, poses=None):
    """Smallest distance (mm) of the moving stage to the rear tyres and wheel brackets, front-most y, over x."""
    doc = active_doc(doc)
    names = ("RL_tire", "RR_tire", "RL_side_l", "RL_side_r", "RR_side_l", "RR_side_r", "RL_top_plate", "RR_top_plate",
             "RL_spacer", "RR_spacer")
    targets = [global_shape(doc.getObject(n)) for n in names if doc.getObject(n) is not None]
    if not targets:
        return {}
    poses = poses or [(x, P.y_tool_front, zc, 0.0) for x in (-P.robot_wheel_x, P.robot_wheel_x)
                      for zc in (P.zc_range[0], P.ZC_WORK)]
    moving = [o for o in doc.getObject("X_slide").OutListRecursive if o.TypeId == "Part::Feature"]
    out = {}
    for pose in poses:
        set_pose(*pose, doc=doc)
        best = (1e9, None)
        for o in moving:
            s = global_shape(o)
            for t in targets:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name)
        out[pose] = (round(best[0], 1), best[1])
    hanger_targets = [global_shape(doc.getObject(n)) for n in ("RR_top_plate", "RR_spacer", "RR_frame_bolts")
                      if doc.getObject(n) is not None]
    hanger = global_shape(doc.getObject("hanger_right"))
    out["hanger_to_wheel_bracket"] = round(min(hanger.distToShape(t)[0] for t in hanger_targets), 1)
    set_pose(doc=doc)
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
MASS_FIXED = {"x_module": P.xm_kg_per_m * P.xm_len / 1000.0, "x_carriage": P.xm_car_kg,
              "y_module": P.sm_kg_per_m * P.ym_len / 1000.0, "z_module": P.sm_kg_per_m * P.zm_len / 1000.0,
              "y_carriage": P.sm_car_kg, "z_carriage": P.sm_car_kg,
              "x_motor": P.nema_kg + 0.3, "y_motor": P.nema_kg + 0.2, "z_motor": P.nema_kg + 0.2,
              "spray_can": 0.45, "servo": 0.08, "sensor": 0.06, "antenna": 0.45, "rx_box": 0.35,
              "control_box": 3.0, "springs": 0.02}
DENSITY = (("z_adapter", 2.7e-6), ("mast", 2.7e-6), ("head_mount", 2.7e-6), ("head_plate", 2.7e-6),
           ("servo_bracket", 2.7e-6), ("lever", 2.7e-6), ("shroud_ring", 2.7e-6), ("box_base", 2.7e-6),
           ("guide_tube", 1.4e-6), ("shroud_tube", 1.4e-6), ("pusher", 1.0e-6), ("knobs", 1.2e-6))
STEEL = 7.85e-6


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
    dens = STEEL
    for key, d in DENSITY:
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) in the current pose: total, fixed part, per slide."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(marker_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    moving = {o.Name for o in objs_of("X_slide")}
    mf, cf = _sum([o for o in marker_objects(doc) if o.Name not in moving])
    out["fixed_kg"] = round(mf, 1)
    out["fixed_cg"] = (round(cf.x), round(cf.y), round(cf.z))
    for name in SLIDES + ("Head",):
        ms, cs = _sum(objs_of(name))
        out[name.lower() + "_kg"] = round(ms, 2)
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in marker_objects(doc):
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
    tgt = V(*target) if target is not None else V(0, -800, 400)
    eye = tgt - d * 8000.0
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


def add_floor(doc, y=(-1700.0, 1000.0), x=(-1000.0, 1000.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.62, 0.70, 0.52)
    obj.ViewObject.Transparency = 30
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    # working: nozzle right of centre, shroud on the ground
    set_pose(x=200.0, y=P.y_tool_nom, zc=P.ZC_WORK, lift=6.0, doc=doc)
    add_floor(doc)
    out.append(save_view("1_work_iso_on_robot.png", (1.0, 1.1, -0.7), target=(0, -500, 400)))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, -400, 450), height=1500))
    out.append(save_view("3_rear_on_robot.png", (0.0, 1.0, -0.12), target=(0, -800, 480), height=1250))
    remove(doc, [GROUND])
    out.append(save_view("4_top_on_robot.png", (0.0, 0.0, -1.0), target=(0, -350, 0), up=(0.0, 1.0, 0.0)))
    # parked, from behind
    set_pose(doc=doc)
    out.append(save_view("5_parked_iso_rear.png", (-1.0, 1.0, -0.6), target=(0, -750, 450)))
    set_robot_visible(False, doc)
    set_visible(doc, ("box_base", "control_box", "box_bolts"), False)
    set_pose(x=0.0, y=P.y_tool_nom, zc=P.ZC_WORK, lift=6.0, doc=doc)
    out.append(save_view("6_stage_iso.png", (-1.0, 1.2, -0.55), target=(-100, -850, 400)))
    out.append(save_view("7_head_detail.png", (-1.0, 0.8, -0.35), target=(0, -890, 220), height=650))
    set_visible(doc, ("guide_tube", "shroud_tube"), False)
    out.append(save_view("8_head_section.png", (-1.0, 0.0, -0.05), target=(0, -890, 220), height=600))
    App.closeDocument(doc.Name)
    build()
    return out
