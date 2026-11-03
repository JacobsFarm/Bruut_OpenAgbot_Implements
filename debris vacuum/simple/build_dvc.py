"""Model of the debris vacuum on the Bruut OpenAgbot (standard robot).

Toolbar, lift arms, carrier, king pin and lift actuator from "push blade/simple" (build_pbl, pbl_parts); head frame and
castors from "magnet sweeper/simple" (mgs_parts); this file adds the nozzle with the brush, the hose, and the bin with
the fan on the upper beams.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_dvc
    build_dvc.build()                      # saves FCStd and STEP (work pose)
    build_dvc.set_pose(lift=18)            # lift of the arms (deg, + = up); the hose follows
    build_dvc.check_interference()         # overlap in the current pose (must be empty)
    build_dvc.check_holes()                # pins, shafts and bolts in their holes (must be empty)
    build_dvc.check_poses()                # overlap over lift x steering +-30 (must be empty)
    build_dvc.clearance()                  # smallest distance of the head to the front tyres over the poses
    build_dvc.mass_properties()
    build_dvc.render_all()                 # all images in previews/
"""
import os

import FreeCAD as App
from FreeCAD import Vector as V

import dvc_params as P
import dvc_parts as G
import build_pbl as BP
import pbl_parts as PP

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Debris_Vacuum"
SAVE_BASE = os.path.join(FOLDER, "Debris_Vacuum")
ROOT = "Debris_vacuum"

COLOR = dict(BP.COLOR)
COLOR.update({
    "head": (0.95, 0.75, 0.10),
    "hood": (0.20, 0.45, 0.75),
    "bristle": (0.15, 0.15, 0.15),
    "core": (0.55, 0.56, 0.58),
    "motor": (0.20, 0.22, 0.25),
    "bin": (0.78, 0.80, 0.83),
    "hose": (0.90, 0.55, 0.15),
    "fan": (0.15, 0.50, 0.30),
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


def build_lift(doc, parent, lift=P.lift_work):
    lift_grp = new_part(doc, parent, "Lift", "lift_arms_turn_about_pivot", lift_placement(lift))
    add_shape(doc, lift_grp, "carrier", "carrier_weldment_from_push_blade", PP.carrier(), "frame")
    add_shape(doc, lift_grp, "king_pin", "king_pin_M30_PE_washer", PP.king_pin(), "zinc")
    add_shape(doc, lift_grp, "lock_pin", "lock_pin_D16_middle_hole", PP.lock_pin(), "zinc")
    head = new_part(doc, lift_grp, "Head", "nozzle_head_on_king_pin", head_placement(0.0))
    add_shape(doc, head, "head_frame", "head_frame_from_magnet_sweeper", G.head_frame(), "head")
    add_shape(doc, head, "box_bolts", "nozzle_bolts_M10_8x", G.box_bolts(), "zinc")
    add_shape(doc, head, "hood", "nozzle_hood_steel_2mm", G.hood(), "hood")
    add_shape(doc, head, "end_plates", "nozzle_end_plates_5mm", G.end_plates(), "hood")
    add_shape(doc, head, "flaps", "nozzle_flaps_rubber_6mm", G.flaps(), "rubber")
    add_shape(doc, head, "outlet", "outlet_stub_D125", G.outlet(), "hood")
    add_shape(doc, head, "bearings", "flange_bearings_UCFL205_2x", G.bearings(), "steel")
    add_shape(doc, head, "bearing_bolts", "bearing_bolts_M10", G.bearing_bolts(), "zinc")
    add_shape(doc, head, "gearmotor", "worm_gearmotor_48V_250W", G.gearmotor(), "motor")
    add_shape(doc, head, "castor_spacers", "castor_spacers_20mm", G.castor_spacers(), "head")
    add_shape(doc, head, "castors", "swivel_castors_125", G.castors(), "castor")
    add_shape(doc, head, "castor_wheels", "castor_wheels_PU_125x40", G.castor_wheels(), "pu")
    add_shape(doc, head, "castor_bolts", "castor_bolts_M8", G.castor_bolts(), "zinc")
    brush = new_part(doc, head, "Brush", "brush_roller_turns_about_its_axis")
    add_shape(doc, brush, "bristles", "bristles_PP_D%dx%d" % (P.brush_d, P.brush_l), G.bristles(), "bristle")
    add_shape(doc, brush, "brush_core", "brush_core_tube_D60", G.brush_core(), "core")
    add_shape(doc, brush, "brush_shaft", "brush_shaft_D25", G.brush_shaft(), "steel")
    return lift_grp


def build_actuator(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Actuator", "lift_actuator_24V_3000N_stroke_100")
    body, rod, _ = PP.actuator(lift)
    add_shape(doc, grp, "act_body", "actuator_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "actuator_rod_clevis", rod, "steel")
    return grp


def build_bin(doc, parent):
    grp = new_part(doc, parent, "Bin", "bin_and_fan_on_upper_beams")
    add_shape(doc, grp, "cross_bars", "cross_bars_60x40x3_2x", G.cross_bars(), "frame")
    add_shape(doc, grp, "bar_bolts", "cross_bar_bolts_M10_8x", G.bar_bolts(), "zinc")
    add_shape(doc, grp, "pads", "bin_pads_PE_15mm_6x", G.pads(), "rubber")
    add_shape(doc, grp, "bin_body", "bin_alu_3mm_270l", G.bin_body(), "bin")
    add_shape(doc, grp, "inlet", "bin_inlet_stub_D125", G.inlet(), "bin")
    add_shape(doc, grp, "door", "rear_door_alu_3mm_hinged_top", G.door(), "bin")
    add_shape(doc, grp, "screen", "screen_perforated_3mm", G.screen(), "steel")
    add_shape(doc, grp, "fan", "centrifugal_fan_D420_outlet_duct", G.fan(), "fan")
    add_shape(doc, grp, "fan_motor", "fan_motor_48V_1200W", G.fan_motor(), "motor")
    return grp


def build_into(doc, parent=None, lift=P.lift_work):
    """Put the debris vacuum in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "debris_vacuum_simple")
    BP.build_mount(doc, root)
    build_lift(doc, root, lift)
    build_actuator(doc, root, lift)
    build_bin(doc, root)
    hose = new_part(doc, root, "Hose", "suction_hose_PU_D125")
    add_shape(doc, hose, "hose", "suction_hose_PU_D125", G.hose(lift), "hose")
    return root


def set_pose(lift=P.lift_work, doc=None):
    doc = active_doc(doc)
    doc.getObject("Lift").Placement = lift_placement(lift)
    body, rod, _ = PP.actuator(lift)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod
    doc.getObject("hose").Shape = G.hose(lift)


build_robot = BP.build_robot
set_steering = BP.set_steering
tyre_envelope = BP.tyre_envelope
global_shape = BP.global_shape
_overlaps = BP._overlaps
objects_of = BP.objects_of


def build(save=True, show_robot=False, step=True, lift=P.lift_work):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Debris vacuum simple"
    doc.Comment = ("Generated by build_dvc.py from dvc_params.py (toolbar, arms and actuator from push blade/simple, "
                   "head frame and castors from magnet sweeper/simple). Robot coordinates: x = right, y = driving "
                   "direction (front = +y), z = up, ground = z 0. Work pose; build_dvc.set_pose() lifts the arms.")
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


# pins, shafts, bolts and hose ends sit in holes or over stubs of the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "carrier"), ("pivot_pins", "pivot_lugs"), ("king_pin", "carrier"), ("king_pin", "head_frame"),
          ("lock_pin", "carrier"), ("lock_pin", "head_frame"), ("act_body", "act_mast"), ("act_rod", "carrier"),
          ("act_body", "act_rod"), ("hanger_bolts_left", "hanger_top_left"), ("hanger_bolts_right", "hanger_top_right"),
          ("box_bolts", "head_frame"), ("box_bolts", "hood"), ("castor_bolts", "castors"),
          ("castor_bolts", "castor_spacers"), ("castor_bolts", "head_frame"), ("castors", "castor_wheels"),
          ("brush_shaft", "end_plates"), ("brush_shaft", "bearings"), ("brush_shaft", "brush_core"),
          ("brush_shaft", "gearmotor"), ("bearing_bolts", "bearings"), ("bearing_bolts", "end_plates"),
          ("hose", "outlet"), ("hose", "inlet"), ("bar_bolts", "cross_bars"), ("inlet", "bin_body")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for bolt, beam in (("hanger_bolts", "lower_beam"), ("bar_bolts", "upper_beam")):
        if (a.startswith(bolt) and b.startswith(beam)) or (b.startswith(bolt) and a.startswith(beam)):
            return True
    return False


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: implement parts among themselves and against the robot."""
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
            continue
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[str((a, b))] = round(v, 1)
    return out


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Interference over the lift poses x steering angles: lift group, actuator and hose against everything else.
    Must be empty."""
    doc = active_doc(doc)
    lift_objs = objects_of(doc, "Lift")
    act_objs = objects_of(doc, "Actuator") + objects_of(doc, "Hose")
    names = {o.Name for o in lift_objs + act_objs}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for lift in P.LIFT_POSES:
            set_pose(lift, doc)
            lf = [(o, global_shape(o)) for o in lift_objs]
            ac = [(o, global_shape(o)) for o in act_objs]
            pairs = [(a, b) for a in lf + ac for b in fixed if not _joint(a[0].Name, b[0].Name)]
            pairs += [(a, b) for a in ac for b in lf + ac
                      if a[0].Name != b[0].Name and not _joint(a[0].Name, b[0].Name)]
            hits = _overlaps(pairs, tol)
            if hits:
                out[str((st, lift))] = hits
    set_steering(0.0, doc)
    set_pose(P.lift_work, doc)
    return out


def clearance(doc=None, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Smallest distance (mm) of the head to the front tyres over the poses (tyre envelope)."""
    doc = active_doc(doc)
    moving = [doc.getObject(n) for n in ("head_frame", "castors", "castor_wheels", "end_plates", "gearmotor", "carrier",
                                         "hose")]
    best = (1e9, None, None)
    for st in steer:
        tg = [tyre_envelope(sx * P.robot_wheel_x, st) for sx in (-1, 1)]
        for lift in (P.LIFT_POSES[0], P.LIFT_POSES[-1]):
            set_pose(lift, doc)
            for o in moving:
                s = global_shape(o)
                for t in tg:
                    d = s.distToShape(t)[0]
                    if d < best[0]:
                        best = (d, o.Name, (st, lift))
    set_pose(P.lift_work, doc)
    return round(best[0], 1), best[1], best[2]


def ground_contact(doc=None):
    """Lowest point (z) of castor wheels, flaps, bristles and hood in work, hop and transport."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_hop, P.lift_transport):
        set_pose(lift, doc)
        out["lift_%g" % lift] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1)
                                 for n in ("castor_wheels", "flaps", "bristles", "hood")}
    set_pose(P.lift_work, doc)
    out["hose_length_mm"] = round(G.hose_length(P.lift_work))
    return out


MASS_FIXED = {"act_body": P.act_kg - 0.6, "act_rod": 0.6, "gearmotor": 7.5, "fan": 9.0, "fan_motor": 4.5}
DENSITY = (("bristles", P.bristle_bulk), ("flaps", P.rubber), ("bin_body", P.alu), ("door", P.alu), ("inlet", P.alu),
           ("hose", 1.2e-6), ("pads", P.pe), ("toolbar_caps", P.pe), ("castor_wheels", 1.2e-6))


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
    """Mass (kg) and centre of gravity of the whole vacuum and its groups."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Lift", "Head", "Brush", "Mount", "Bin", "Hose"):
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


def add_floor(doc, y=(-900.0, 2000.0), x=(-1100.0, 1100.0), color=(0.45, 0.62, 0.30)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = color
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
    out.append(save_view("1_iso_front_on_robot.png", (-1.0, -1.2, -0.7), target=(0, 500, 500)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, 550, 650), height=1900))
    set_pose(P.lift_transport, doc)
    out.append(save_view("3_side_lifted_18deg.png", (1.0, 0.0, 0.0), target=(0, 550, 650), height=1900))
    remove(doc, [GROUND])
    set_pose(P.lift_work, doc)
    set_steering(P.robot_steer_deg, doc)
    out.append(save_view("4_top_steered_30deg.png", (0.0, 0.0, -1.0), target=(0, 500, 0), up=(0.0, 1.0, 0.0),
                         height=2600))
    set_steering(0.0, doc)
    out.append(save_view("5_iso_rear_bin_fan.png", (1.0, 1.1, -0.7), target=(0, 0, 900), height=1700))
    set_robot_visible(False, doc)
    for n in ("hood", "end_plates", "flaps"):
        doc.getObject(n).ViewObject.Transparency = 70
    out.append(save_view("6_nozzle_brush_inside.png", (-1.0, -0.5, -0.5), target=(0, 1450, 200), height=1300))
    App.closeDocument(doc.Name)
    build()
    return out
