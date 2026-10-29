"""Model of the broom / sweeper on the Bruut OpenAgbot (standard robot).

The front toolbar, lift arms, carrier, king pin and actuator are built from "push blade/simple" (build_pbl, pbl_parts);
this file adds the broom head on the king pin instead of the blade.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_bsw
    build_bsw.build()                      # saves FCStd and STEP (work pose: on the castors, straight)
    build_bsw.set_pose(lift=18, angle=25)  # lift of the arms (deg, + = up), head angle (deg, + = right end forward)
    build_bsw.check_interference()         # overlap in the current pose (must be empty)
    build_bsw.check_holes()                # pins and bolts in their holes (must be empty)
    build_bsw.check_poses()                # overlap over lift x angle x steering +-30 (must be empty)
    build_bsw.clearance()                  # smallest distance of the head to the front tyres over the poses
    build_bsw.mass_properties()
    build_bsw.render_all()                 # all images in previews/
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bsw_params as P
import bsw_parts as G
import build_pbl as BP
import pbl_parts as PP

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Broom_Sweeper"
SAVE_BASE = os.path.join(FOLDER, "Broom_Sweeper")
ROOT = "Broom_sweeper"

COLOR = dict(BP.COLOR)
COLOR.update({
    "head": (0.95, 0.75, 0.10),
    "hood": (0.20, 0.45, 0.75),
    "bristle": (0.15, 0.15, 0.15),
    "core": (0.55, 0.56, 0.58),
    "motor": (0.20, 0.22, 0.25),
    "castor": (0.85, 0.30, 0.10),
    "pu": (0.15, 0.40, 0.80),
})


def new_part(doc, parent, name, label, placement=None):
    return BP.new_part(doc, parent, name, label, placement)


def add_shape(doc, parent, name, label, shape, color, visible=True):
    obj = BP.add_shape(doc, parent, name, label, shape, "frame", visible)
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = COLOR[color]
    return obj


lift_placement = BP.lift_placement
head_placement = BP.blade_placement


def brush_placement(deg):
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), deg), V(0, P.axis_y, P.axis_z))


def build_lift(doc, parent, lift=P.lift_work, angle=0.0):
    lift_grp = new_part(doc, parent, "Lift", "lift_arms_turn_about_pivot", lift_placement(lift))
    add_shape(doc, lift_grp, "carrier", "carrier_weldment_from_push_blade", PP.carrier(), "frame")
    add_shape(doc, lift_grp, "king_pin", "king_pin_M30_PE_washer", PP.king_pin(), "zinc")
    add_shape(doc, lift_grp, "lock_pin", "angle_lock_pin_D16", PP.lock_pin(), "zinc")
    head = new_part(doc, lift_grp, "Head", "broom_head_turns_about_king_pin", head_placement(angle))
    add_shape(doc, head, "head_frame", "head_frame_swivel_plate_beam_80x60_end_plates_8mm", G.head_frame(), "head")
    add_shape(doc, head, "hood", "hood_alu_2mm_R%d" % P.hood_r, G.hood(), "hood")
    add_shape(doc, head, "flap", "front_flap_rubber_6mm", G.flap(), "rubber")
    add_shape(doc, head, "bearings", "flange_bearings_UCFL208_2x", G.bearings(), "steel")
    add_shape(doc, head, "bearing_bolts", "bearing_bolts_M12", G.bearing_bolts(), "zinc")
    add_shape(doc, head, "motor", "motor_48V_1000W_gearbox_1to5", G.motor(), "motor")
    add_shape(doc, head, "motor_shaft", "gearbox_output_shaft_D25", G.motor_shaft(), "steel")
    add_shape(doc, head, "pulleys", "pulleys_HTD8M_30T_45T", G.pulleys(), "steel")
    add_shape(doc, head, "belt", "belt_HTD8M_25mm", G.belt(), "rubber")
    add_shape(doc, head, "guard", "belt_guard_2mm", G.guard(), "hood")
    add_shape(doc, head, "guard_standoffs", "guard_standoffs_M8", G.guard_standoffs(), "zinc")
    add_shape(doc, head, "castor_spacers", "castor_spacers_20mm", G.castor_spacers(), "head")
    add_shape(doc, head, "castors", "swivel_castors_125", G.castors(), "castor")
    add_shape(doc, head, "castor_wheels", "castor_wheels_PU_125x40", G.castor_wheels(), "pu")
    add_shape(doc, head, "castor_bolts", "castor_bolts_M8", G.castor_bolts(), "zinc")
    brush = new_part(doc, head, "Brush", "roller_brush_turns_about_its_axis", brush_placement(0.0))
    add_shape(doc, brush, "bristles", "bristles_PP_D%dx%d" % (P.brush_d, P.brush_l), G.bristles(), "bristle")
    add_shape(doc, brush, "brush_core", "brush_core_tube_114x3", G.brush_core(), "core")
    add_shape(doc, brush, "brush_shaft", "brush_shaft_D40", G.brush_shaft(), "steel")
    return lift_grp


def build_actuator(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Actuator", "lift_actuator_24V_3000N_stroke_100")
    body, rod, _ = PP.actuator(lift)
    add_shape(doc, grp, "act_body", "actuator_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "actuator_rod_clevis", rod, "steel")
    return grp


def build_into(doc, parent=None, lift=P.lift_work, angle=0.0):
    """Put the broom in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "broom_sweeper_simple")
    BP.build_mount(doc, root)
    build_lift(doc, root, lift, angle)
    build_actuator(doc, root, lift)
    return root


def set_pose(lift=P.lift_work, angle=0.0, doc=None, brush_deg=None):
    doc = active_doc(doc)
    doc.getObject("Lift").Placement = lift_placement(lift)
    doc.getObject("Head").Placement = head_placement(angle)
    if brush_deg is not None:
        doc.getObject("Brush").Placement = brush_placement(brush_deg)
    body, rod, _ = PP.actuator(lift)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod


build_robot = BP.build_robot
set_steering = BP.set_steering
tyre_envelope = BP.tyre_envelope
global_shape = BP.global_shape
_overlaps = BP._overlaps


def build(save=True, show_robot=False, step=True, lift=P.lift_work, angle=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Broom sweeper simple"
    doc.Comment = ("Generated by build_bsw.py from bsw_params.py (toolbar, arms and actuator from push blade/simple). "
                   "Robot coordinates: x = right, y = driving direction (front = +y), z = up, ground = z 0. Work pose; "
                   "build_bsw.set_pose() lifts and angles the head.")
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


objects_of = BP.objects_of


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


# pins, shafts and bolts pass through holes in the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "carrier"), ("pivot_pins", "pivot_lugs"), ("king_pin", "carrier"), ("king_pin", "head_frame"),
          ("lock_pin", "carrier"), ("lock_pin", "head_frame"), ("act_body", "act_mast"), ("act_rod", "carrier"),
          ("act_body", "act_rod"), ("hanger_bolts_left", "hanger_top_left"), ("hanger_bolts_right", "hanger_top_right"),
          ("brush_shaft", "head_frame"), ("brush_shaft", "bearings"), ("brush_shaft", "brush_core"),
          ("brush_shaft", "pulleys"), ("bearing_bolts", "bearings"), ("bearing_bolts", "head_frame"),
          ("motor_shaft", "head_frame"), ("motor_shaft", "pulleys"), ("motor_shaft", "motor"),
          ("guard_standoffs", "head_frame"), ("guard_standoffs", "guard"), ("castor_bolts", "castors"),
          ("castor_bolts", "castor_spacers"), ("castor_bolts", "head_frame"), ("castors", "castor_wheels")}


def _joint(a, b):
    return (a, b) in JOINTS or (b, a) in JOINTS or (a.startswith("hanger_bolts") and b.startswith("lower_beam")) or \
        (b.startswith("hanger_bolts") and a.startswith("lower_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: implement parts among themselves and against the robot.
    Pins, shafts and bolts in their own holes are skipped (JOINTS); their holes are checked by check_holes()."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """The pins, shafts and bolts must sit in holes: overlap of the JOINTS pairs (should be ~0)."""
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
    """Interference over the lift poses x head angles x steering angles: only the moving parts (lift group, actuator)
    against everything else and each other (the lift group itself is checked by check_interference). Must be empty."""
    doc = active_doc(doc)
    lift_objs = objects_of(doc, "Lift")
    act_objs = objects_of(doc, "Actuator")
    names = {o.Name for o in lift_objs + act_objs}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for lift in P.LIFT_POSES:
            for ang in (P.angle_steps[0], 0.0, P.angle_steps[-1]):
                set_pose(lift, ang, doc)
                lf = [(o, global_shape(o)) for o in lift_objs]
                ac = [(o, global_shape(o)) for o in act_objs]
                pairs = [(a, b) for a in lf + ac for b in fixed if not _joint(a[0].Name, b[0].Name)]
                pairs += [(a, b) for a in ac for b in lf if not _joint(a[0].Name, b[0].Name)]
                hits = _overlaps(pairs, tol)
                if hits:
                    out[(st, lift, ang)] = hits
    set_steering(0.0, doc)
    set_pose(P.lift_work, 0.0, doc)
    return out


def clearance(doc=None, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Smallest distance (mm) of the head to the front tyres over the poses (tyre envelope)."""
    doc = active_doc(doc)
    moving = [doc.getObject(n) for n in ("head_frame", "castors", "castor_wheels", "guard", "bearings", "carrier")]
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


def ground_contact(doc=None):
    """Lowest point (z) of the castor wheels and the bristles in work and transport (straight head)."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, 0.0, doc)
        out["lift_%g" % lift] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1)
                                 for n in ("castor_wheels", "bristles", "flap", "head_frame")}
    set_pose(P.lift_work, 0.0, doc)
    return out


MASS_FIXED = {"act_body": P.act_kg - 0.6, "act_rod": 0.6, "motor": P.motor_kg - 0.4}
DENSITY = (("bristles", P.bristle_bulk), ("hood", P.alu), ("flap", P.rubber), ("belt", P.rubber), ("toolbar_caps", 0.95e-6),
           ("castor_wheels", 1.2e-6))


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole broom, the lift group, the head, the brush
    and the mount."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Lift", "Head", "Brush", "Mount"):
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
def save_view(name, direction, target=None, height=None, up=(0.0, 0.0, 1.0), size_px=(1600, 1100)):
    import FreeCADGui as Gui
    Gui.updateGui()
    BP.set_camera(direction, target, height, up)
    Gui.updateGui()
    view = BP.set_camera(direction, target, height, up)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, name)
    view.saveImage(path, size_px[0], size_px[1], "White")
    return path


GROUND = "render_floor"


def add_floor(doc, y=(-900.0, 2000.0), x=(-1100.0, 1100.0)):
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
    out.append(save_view("1_iso_front_on_robot.png", (-1.0, -1.2, -0.7), target=(0, 600, 350)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, 750, 400), height=1700))
    set_pose(P.lift_transport, 0.0, doc)
    out.append(save_view("3_side_transport.png", (1.0, 0.0, 0.0), target=(0, 750, 400), height=1700))
    remove(doc, [GROUND])
    set_pose(P.lift_work, P.angle_steps[-1], doc)
    set_steering(P.robot_steer_deg, doc)
    out.append(save_view("4_top_angled_25deg.png", (0.0, 0.0, -1.0), target=(0, 600, 0), up=(0.0, 1.0, 0.0),
                         height=2400))
    set_steering(0.0, doc)
    set_pose(P.lift_work, 0.0, doc)
    set_robot_visible(False, doc)
    out.append(save_view("5_head_iso_rear.png", (-1.0, 1.0, -0.6), target=(0, 1350, 250), height=1500))
    doc.getObject("hood").ViewObject.Visibility = False
    doc.getObject("guard").ViewObject.Visibility = False
    out.append(save_view("6_drive_detail.png", (-1.0, -0.4, -0.5), target=(520, 1400, 300), height=700))
    App.closeDocument(doc.Name)
    build()
    return out
