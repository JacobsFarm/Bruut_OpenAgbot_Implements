"""Model of the electric weeder on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_elw
    build_elw.build()                      # saves FCStd and STEP
    build_elw.check_interference()         # overlap between the parts and with the robot (must be empty)
    build_elw.check_holes()                # bolts in their holes (must be empty)
    build_elw.check_steering()             # overlap with the front wheels steered +-30 (must be empty)
    build_elw.set_pose(20)                 # lift of the arms (deg, + = up)
    build_elw.check_poses()                # overlap of the moving parts over the lift poses (must be empty)
    build_elw.check_rows()                 # parts in the space of the crop rows (must be empty)
    build_elw.clearance()                  # smallest distance to the tyres (rear and steered front)
    build_elw.mass_properties()
    build_elw.render_all()                 # all images in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import elw_params as P
import elw_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Electric_Weeder"
SAVE_BASE = os.path.join(FOLDER, "Electric_Weeder")
ROOT = "Electric_weeder"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "hv": (0.85, 0.15, 0.10),
    "beacon": (1.00, 0.60, 0.00),
    "pe": (0.95, 0.95, 0.90),
    "rubber": (0.10, 0.10, 0.10),
    "motor": (0.20, 0.22, 0.25),
    "camera": (0.15, 0.15, 0.18),
    "crop": (0.25, 0.60, 0.20),
    "weed": (0.55, 0.65, 0.15),
}


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


def arm_placement(i, lift):
    c = V(0, P.pivot_y, P.pivot_z[i])
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), lift), c)


def carrier_placement(lift):
    a = math.radians(lift)
    return App.Placement(V(0, P.arm_len * (math.cos(a) - 1.0), P.arm_len * math.sin(a)), App.Rotation())


def build_into(doc, parent=None, lift=P.lift_work):
    root = new_part(doc, parent, ROOT, "electric_weeder_simple")
    m = new_part(doc, root, "Mount", "bearer_post_hv_camera")
    add_shape(doc, m, "bearer", "bearer_40x40x3_on_upper_beams", G.bearer(), "frame")
    add_shape(doc, m, "bearer_bolts", "bearer_bolts_M10", G.bearer_bolts(), "zinc")
    add_shape(doc, m, "post", "post_40x40x3_with_lugs", G.post(), "frame")
    add_shape(doc, m, "pins_fixed", "arm_and_actuator_pins_D12", G.pins_fixed(), "zinc")
    add_shape(doc, m, "hv_box", "hv_generator_48V_to_5kV", G.hv_box(), "hv")
    add_shape(doc, m, "beacon", "warning_beacon", G.beacon(), "beacon")
    add_shape(doc, m, "cam_plate", "camera_plate_10mm", G.cam_plate(), "frame")
    add_shape(doc, m, "cam_bolts", "camera_plate_bolts_M10", G.cam_bolts(), "zinc")
    add_shape(doc, m, "camera", "weed_camera", G.camera(), "camera")
    r = new_part(doc, root, "Return", "earth_return_coulter")
    add_shape(doc, r, "disc_arms", "coulter_arms_8mm", G.disc_arms(), "frame")
    add_shape(doc, r, "disc", "coulter_disc_D250_earth_return", G.disc(), "steel")
    add_shape(doc, r, "disc_pin", "coulter_arm_pin_D12", G.disc_pin(), "zinc")
    lift_grp = new_part(doc, root, "Lift", "parallel_lift")
    up = new_part(doc, lift_grp, "UpperArm", "upper_arm_turns_about_pivot", arm_placement(0, lift))
    add_shape(doc, up, "upper_arm", "upper_arm_20x30x2", G.arm(0), "frame")
    add_shape(doc, up, "act_lug", "actuator_lug_on_arm", G.act_lug(), "frame")
    lo = new_part(doc, lift_grp, "LowerArm", "lower_arm_turns_about_pivot", arm_placement(1, lift))
    add_shape(doc, lo, "lower_arm", "lower_arm_20x30x2", G.arm(1), "frame")
    ca = new_part(doc, lift_grp, "Carrier", "carrier_moves_parallel", carrier_placement(lift))
    add_shape(doc, ca, "carrier", "carrier_plates_6mm_foot", G.carrier(), "frame")
    add_shape(doc, ca, "pins_carrier", "carrier_pins_D12", G.pins_carrier(), "zinc")
    add_shape(doc, ca, "holder", "applicator_holder_PE", G.holder(), "pe")
    add_shape(doc, ca, "fingers", "electrode_fingers_spring_steel_D4", G.fingers(), "steel")
    add_shape(doc, ca, "curtains", "side_curtains_rubber_3mm", G.curtains(), "rubber")
    ac = new_part(doc, root, "Actuator", "lift_actuator_24V")
    body, rod = G.actuator(lift)
    add_shape(doc, ac, "act_body", "actuator_body", body, "motor")
    add_shape(doc, ac, "act_rod", "actuator_rod", rod, "steel")
    return root


def set_pose(lift=P.lift_work, doc=None):
    doc = active_doc(doc)
    doc.getObject("UpperArm").Placement = arm_placement(0, lift)
    doc.getObject("LowerArm").Placement = arm_placement(1, lift)
    doc.getObject("Carrier").Placement = carrier_placement(lift)
    body, rod = G.actuator(lift)
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


def build(save=True, show_robot=False, step=True, crop=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Electric weeder simple"
    doc.Comment = ("Generated by build_elw.py from elw_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    if crop:
        grp = new_part(doc, None, "Crop", "crop_rows_for_images")
        add_shape(doc, grp, "crop", "crop_2_rows_375", G.crop(), "crop")
        add_shape(doc, grp, "weeds", "weeds_in_the_band", G.weeds(), "weed")
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


JOINTS = {("bearer_bolts", "bearer"), ("cam_bolts", "cam_plate"), ("pins_fixed", "post"), ("pins_fixed", "upper_arm"),
          ("pins_fixed", "lower_arm"), ("pins_fixed", "act_body"), ("pins_carrier", "carrier"),
          ("pins_carrier", "upper_arm"), ("pins_carrier", "lower_arm"), ("act_rod", "act_lug"), ("act_rod", "upper_arm"),
          ("act_body", "act_rod"), ("disc_pin", "post"), ("disc_pin", "disc_arms"), ("disc", "disc_arms"),
          ("fingers", "holder"), ("post", "bearer"), ("act_body", "post")}
ROBOT_JOINTS = {"bearer_bolts": "upper_beam", "cam_bolts": "lower_beam"}


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
    """Pins and bolts must pass through holes in the parts they join and in the robot beams."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    for o in robot_objects(doc):
        if o.Name.startswith("upper_beam") or o.Name.startswith("lower_beam"):
            objs[o.Name] = global_shape(o)
    pairs = [p for p in JOINTS if p not in (("act_body", "act_rod"), ("fingers", "holder"), ("post", "bearer"),
                                            ("act_body", "post"))]
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


def check_poses(doc=None, tol=1.0):
    """Moving parts (arms, carrier, actuator) against everything else over the lift poses. Must be empty."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Lift") + objects_of(doc, "Actuator")
    names = {o.Name for o in moving}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    fixed = [(o, global_shape(o)) for o in others]
    out = {}
    for lift in P.LIFT_POSES:
        set_pose(lift, doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[str(lift)] = hits
    set_pose(P.lift_work, doc)
    return out


def ground_contact(doc=None):
    """Lowest z of the fingers and the disc in work and lifted."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, doc)
        out[str(lift)] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1) for n in ("fingers", "holder", "disc")}
    set_pose(P.lift_work, doc)
    return out


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


MASS_FIXED = {"hv_box": P.hv_kg, "act_body": P.act_kg - 0.3, "act_rod": 0.3, "camera": P.cam_kg, "beacon": 0.3}
DENSITY = (("holder", P.pe), ("curtains", P.rubber))


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
    tgt = V(*target) if target is not None else V(0, 0, 450)
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
    floor.Shape = G.box_span((-1000, 1000), (-1100, 1100), (-40.0, 0.0))
    floor.ViewObject.ShapeColor = (0.55, 0.45, 0.33)
    out.append(save_view("1_iso_front_right_in_crop.png", (-1.0, -1.2, -0.8), target=(0, 0, 350)))
    out.append(save_view("2_side_work.png", (-1.0, 0.0, 0.0), target=(0, 0, 450), height=1500))
    set_pose(P.lift_transport, doc)
    out.append(save_view("3_side_lifted.png", (-1.0, 0.0, 0.0), target=(0, 0, 450), height=1500))
    set_pose(P.lift_work, doc)
    out.append(save_view("4_front.png", (0.0, -1.0, 0.0), target=(0, 0, 450), height=1300))
    doc.removeObject("render_floor")
    set_robot_visible(False, doc)
    for n in ("crop", "weeds"):
        doc.getObject(n).ViewObject.Visibility = False
    out.append(save_view("5_unit_iso.png", (-1.0, -1.0, -0.6), target=(0, -150, 400), height=1300))
    App.closeDocument(doc.Name)
    build()
    return out
