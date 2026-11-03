"""Model of the magnet sweeper on the Bruut OpenAgbot (standard robot).

The front toolbar, lift arms, carrier, king pin and lift actuator are built from "push blade/simple" (build_pbl,
pbl_parts), the castor wheels from "broom sweeper/simple" (bsw_parts); this file adds the magnet head on the king pin.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_mgs
    build_mgs.build()                      # saves FCStd and STEP (work pose: on the castors, core down)
    build_mgs.set_pose(lift=9, core=1)     # lift of the arms (deg, + = up), core position (0 = down, 1 = lifted)
    build_mgs.check_interference()         # overlap in the current pose (must be empty)
    build_mgs.check_holes()                # pins and bolts in their holes (must be empty)
    build_mgs.check_poses()                # overlap over lift x core x steering +-30 (must be empty)
    build_mgs.clearance()                  # smallest distance of the head to the front tyres over the poses
    build_mgs.mass_properties()
    build_mgs.render_all()                 # all images in previews/
"""
import os

import FreeCAD as App
from FreeCAD import Vector as V

import mgs_params as P
import mgs_parts as G
import build_pbl as BP
import pbl_parts as PP

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Magnet_Sweeper"
SAVE_BASE = os.path.join(FOLDER, "Magnet_Sweeper")
ROOT = "Magnet_sweeper"

COLOR = dict(BP.COLOR)
COLOR.update({
    "head": (0.95, 0.75, 0.10),
    "box": (0.78, 0.80, 0.83),
    "skin": (0.62, 0.64, 0.66),
    "magnet": (0.22, 0.22, 0.24),
    "core": (0.80, 0.15, 0.12),
    "pe": (0.95, 0.95, 0.92),
    "castor": (0.85, 0.30, 0.10),
    "pu": (0.15, 0.40, 0.80),
    "tray": (0.15, 0.55, 0.30),
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


def core_placement(core):
    """core 0 = down on the skin (work), 1 = lifted by core_lift (release)."""
    return App.Placement(V(0, 0, core * P.core_lift), App.Rotation())


def build_lift(doc, parent, lift=P.lift_work, core=0.0):
    lift_grp = new_part(doc, parent, "Lift", "lift_arms_turn_about_pivot", lift_placement(lift))
    add_shape(doc, lift_grp, "carrier", "carrier_weldment_from_push_blade", PP.carrier(), "frame")
    add_shape(doc, lift_grp, "king_pin", "king_pin_M30_PE_washer", PP.king_pin(), "zinc")
    add_shape(doc, lift_grp, "lock_pin", "lock_pin_D16_middle_hole", PP.lock_pin(), "zinc")
    head = new_part(doc, lift_grp, "Head", "magnet_head_on_king_pin", head_placement(0.0))
    add_shape(doc, head, "head_frame", "head_frame_swivel_plate_beam_80x60_brackets_10mm", G.head_frame(), "head")
    add_shape(doc, head, "box_bolts", "box_bolts_M10_8x", G.box_bolts(), "zinc")
    add_shape(doc, head, "box_walls", "magnet_box_walls_alu_4mm", G.box_walls(), "box")
    add_shape(doc, head, "lid", "magnet_box_lid_alu_5mm", G.lid(), "box")
    add_shape(doc, head, "skin", "skin_stainless_304_3mm_%dx%d" % (2 * P.box_x, P.box_y[1] - P.box_y[0]), G.skin(),
              "skin")
    add_shape(doc, head, "skids", "skids_PE_10mm_4x", G.skids(), "pe")
    add_shape(doc, head, "guide_rods", "guide_rods_stainless_D16_4x", G.guide_rods(), "steel")
    add_shape(doc, head, "release_body", "release_actuator_24V_3000N_stroke_100", G.release_body(), "actuator")
    add_shape(doc, head, "castor_spacers", "castor_spacers_20mm", G.castor_spacers(), "head")
    add_shape(doc, head, "castors", "swivel_castors_125", G.castors(), "castor")
    add_shape(doc, head, "castor_wheels", "castor_wheels_PU_125x40", G.castor_wheels(), "pu")
    add_shape(doc, head, "castor_bolts", "castor_bolts_M8", G.castor_bolts(), "zinc")
    core_grp = new_part(doc, head, "Core", "magnet_core_lifts_to_release", core_placement(core))
    add_shape(doc, core_grp, "back_plate", "core_back_plate_steel_15mm", G.back_plate(), "core")
    add_shape(doc, core_grp, "magnets", "NdFeB_N35_100x100x10_%dx" % (P.mag_rows * P.mag_n), G.magnets(), "magnet")
    add_shape(doc, core_grp, "bushes", "guide_bushes_PE_4x", G.bushes(), "pe")
    add_shape(doc, core_grp, "clevis", "clevis_plates_6mm", G.clevis(), "core")
    add_shape(doc, core_grp, "clevis_pin", "clevis_pin_D10", G.clevis_pin(), "zinc")
    add_shape(doc, core_grp, "release_rod", "release_actuator_rod_D20", G.release_rod(), "steel")
    return lift_grp


def build_actuator(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Actuator", "lift_actuator_24V_3000N_stroke_100")
    body, rod, _ = PP.actuator(lift)
    add_shape(doc, grp, "act_body", "actuator_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "actuator_rod_clevis", rod, "steel")
    return grp


def build_into(doc, parent=None, lift=P.lift_work, core=0.0):
    """Put the magnet sweeper in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "magnet_sweeper_simple")
    BP.build_mount(doc, root)
    build_lift(doc, root, lift, core)
    build_actuator(doc, root, lift)
    return root


def set_pose(lift=P.lift_work, core=0.0, doc=None):
    doc = active_doc(doc)
    doc.getObject("Lift").Placement = lift_placement(lift)
    doc.getObject("Core").Placement = core_placement(core)
    body, rod, _ = PP.actuator(lift)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod


build_robot = BP.build_robot
set_steering = BP.set_steering
tyre_envelope = BP.tyre_envelope
global_shape = BP.global_shape
_overlaps = BP._overlaps
objects_of = BP.objects_of


def build(save=True, show_robot=False, step=True, lift=P.lift_work, core=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Magnet sweeper simple"
    doc.Comment = ("Generated by build_mgs.py from mgs_params.py (toolbar, arms and actuator from push blade/simple, "
                   "castors from broom sweeper/simple). Robot coordinates: x = right, y = driving direction (front = +y), "
                   "z = up, ground = z 0. Work pose; build_mgs.set_pose() lifts the arms and the magnet core.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, lift, core)
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


# pins, shafts and bolts pass through holes in the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "carrier"), ("pivot_pins", "pivot_lugs"), ("king_pin", "carrier"), ("king_pin", "head_frame"),
          ("lock_pin", "carrier"), ("lock_pin", "head_frame"), ("act_body", "act_mast"), ("act_rod", "carrier"),
          ("act_body", "act_rod"), ("hanger_bolts_left", "hanger_top_left"), ("hanger_bolts_right", "hanger_top_right"),
          ("box_bolts", "head_frame"), ("box_bolts", "box_walls"), ("guide_rods", "back_plate"),
          ("guide_rods", "bushes"), ("clevis_pin", "clevis"), ("clevis_pin", "release_rod"),
          ("release_rod", "lid"), ("release_rod", "release_body"), ("castor_bolts", "castors"),
          ("castor_bolts", "castor_spacers"), ("castor_bolts", "head_frame"), ("castors", "castor_wheels")}


def _joint(a, b):
    return (a, b) in JOINTS or (b, a) in JOINTS or (a.startswith("hanger_bolts") and b.startswith("lower_beam")) or \
        (b.startswith("hanger_bolts") and a.startswith("lower_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: implement parts among themselves and against the robot.
    Pins, rods and bolts in their own holes are skipped (JOINTS); their holes are checked by check_holes()."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """The pins, rods and bolts must sit in holes: overlap of the JOINTS pairs (should be ~0)."""
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
    """Interference over the lift poses x core down/up x steering angles: the lift group and the actuator against
    everything else, and the core against the rest of the head. Must be empty."""
    doc = active_doc(doc)
    lift_objs = objects_of(doc, "Lift")
    act_objs = objects_of(doc, "Actuator")
    core_names = {o.Name for o in objects_of(doc, "Core")}
    names = {o.Name for o in lift_objs + act_objs}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for lift in P.LIFT_POSES:
            for core in (0.0, 1.0):
                set_pose(lift, core, doc)
                lf = [(o, global_shape(o)) for o in lift_objs]
                ac = [(o, global_shape(o)) for o in act_objs]
                co = [x for x in lf if x[0].Name in core_names]
                rest = [x for x in lf if x[0].Name not in core_names]
                pairs = [(a, b) for a in lf + ac for b in fixed if not _joint(a[0].Name, b[0].Name)]
                pairs += [(a, b) for a in ac for b in lf if not _joint(a[0].Name, b[0].Name)]
                if st == 0.0:
                    pairs += [(a, b) for a in co for b in rest if not _joint(a[0].Name, b[0].Name)]
                hits = _overlaps(pairs, tol)
                if hits:
                    out[str((st, lift, core))] = hits
    set_steering(0.0, doc)
    set_pose(P.lift_work, 0.0, doc)
    return out


def clearance(doc=None, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Smallest distance (mm) of the head to the front tyres over the poses (tyre envelope)."""
    doc = active_doc(doc)
    moving = [doc.getObject(n) for n in ("head_frame", "castors", "castor_wheels", "box_walls", "carrier")]
    best = (1e9, None, None)
    for st in steer:
        tg = [tyre_envelope(sx * P.robot_wheel_x, st) for sx in (-1, 1)]
        for lift in (P.LIFT_POSES[0], P.LIFT_POSES[-1]):
            set_pose(lift, 0.0, doc)
            for o in moving:
                s = global_shape(o)
                for t in tg:
                    d = s.distToShape(t)[0]
                    if d < best[0]:
                        best = (d, o.Name, (st, lift))
    set_pose(P.lift_work, 0.0, doc)
    return round(best[0], 1), best[1], best[2]


def ground_contact(doc=None):
    """Lowest point (z) of castor wheels, skids and skin in work, release and transport."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_hop, P.lift_transport):
        set_pose(lift, 0.0, doc)
        out["lift_%g" % lift] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1)
                                 for n in ("castor_wheels", "skids", "skin", "head_frame")}
    set_pose(P.lift_work, 0.0, doc)
    return out


def tray_y():
    """y of the collecting tray centre: under the magnet rows in the work pose (release)."""
    return P.mag_y


MASS_FIXED = {"act_body": P.act_kg - 0.6, "act_rod": 0.6, "release_body": P.rel_kg - 0.4}
DENSITY = (("magnets", P.ndfeb), ("box_walls", P.alu), ("lid", P.alu), ("skids", P.pe), ("bushes", P.pe),
           ("toolbar_caps", P.pe), ("castor_wheels", 1.2e-6))


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
    """Mass (kg) and centre of gravity of the whole sweeper, the lift group, the head, the core and the mount."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Lift", "Head", "Core", "Mount"):
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
TRAY = "render_tray"


def add_floor(doc, y=(-900.0, 2000.0), x=(-1100.0, 1100.0), color=(0.45, 0.62, 0.30)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = 30
    return obj


def add_tray(doc):
    obj = doc.addObject("Part::Feature", TRAY)
    obj.Shape = G.tray(tray_y())
    obj.ViewObject.ShapeColor = COLOR["tray"]
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
    out.append(save_view("1_iso_front_on_robot.png", (-1.0, -1.2, -0.7), target=(0, 700, 300)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, 750, 350), height=1700))
    set_pose(P.lift_work, 1.0, doc)
    add_tray(doc)
    out.append(save_view("3_side_release_over_tray.png", (1.0, 0.0, 0.0), target=(0, 1250, 150), height=900))
    out.append(save_view("4_iso_release_over_tray.png", (-1.0, -1.0, -0.6), target=(0, 1200, 200), height=1900))
    remove(doc, [TRAY, GROUND])
    set_pose(P.lift_transport, 0.0, doc)
    out.append(save_view("4b_side_lifted_18deg.png", (1.0, 0.0, 0.0), target=(0, 750, 350), height=1700))
    set_pose(P.lift_work, 0.0, doc)
    set_steering(P.robot_steer_deg, doc)
    out.append(save_view("5_top_steered_30deg.png", (0.0, 0.0, -1.0), target=(0, 600, 0), up=(0.0, 1.0, 0.0),
                         height=2400))
    set_steering(0.0, doc)
    set_robot_visible(False, doc)
    out.append(save_view("6_head_from_below.png", (-0.6, 0.7, 1.0), target=(0, 1350, 100), height=1500))
    for n in ("lid", "release_body", "box_walls"):
        doc.getObject(n).ViewObject.Transparency = 70
    out.append(save_view("7_core_down_inside.png", (-1.0, -0.6, -0.5), target=(0, 1430, 150), height=1250))
    set_pose(P.lift_work, 1.0, doc)
    out.append(save_view("8_core_lifted_inside.png", (-1.0, -0.6, -0.5), target=(0, 1430, 150), height=1250))
    App.closeDocument(doc.Name)
    build()
    return out
