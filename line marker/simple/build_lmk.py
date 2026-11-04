"""Model of the sports field line marker on the Bruut OpenAgbot (standard robot).

Tank, cradle, pump, filter, regulator, suction / return hoses and the control box are built from "spotspray unit/boom"
(build_ssp, ssp_parts); the rail bolts and the control-box base plate from "drop on demand boom/simple" (ddb_parts);
this file adds the belly rails, the hanger posts, the belt module across the rear axle line, the drag chain and the
paint head (own sub-Part, moves in x).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_lmk
    build_lmk.build()                      # saves FCStd and STEP (head in the middle)
    build_lmk.set_head(120)                # nozzle x (-180 .. +180), also regenerates the drag chain
    build_lmk.check_interference()         # overlap in the current pose (must be empty)
    build_lmk.check_holes()                # bolts in their holes (must be empty)
    build_lmk.check_poses()                # overlap over the stroke x steering +-30 (must be empty)
    build_lmk.clearance()                  # smallest distance of the head to the tyres
    build_lmk.mass_properties()
    build_lmk.render_all()                 # all images in previews/
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lmk_params as P
import lmk_parts as G
import ssp_parts as SG
import build_ssp as BS

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Line_Marker"
SAVE_BASE = os.path.join(FOLDER, "Line_Marker")
ROOT = "Line_marker"

COLOR = dict(BS.COLOR)
COLOR.update({
    "module": (0.80, 0.81, 0.83),
    "carriage": (0.25, 0.27, 0.30),
    "motor": (0.15, 0.15, 0.17),
    "chain": (0.12, 0.12, 0.12),
    "shroud": (0.95, 0.95, 0.93),
    "brush": (0.12, 0.12, 0.12),
    "valve": (0.15, 0.35, 0.75),
    "paint": (0.98, 0.98, 0.98),
})


def new_part(doc, parent, name, label, placement=None):
    return BS.new_part(doc, parent, name, label, placement)


def add_shape(doc, parent, name, label, shape, color, visible=True):
    if isinstance(shape, (list, tuple)):
        shape = Part.makeCompound(list(shape))
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    parent.addObject(obj)
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = COLOR[color]
        obj.ViewObject.Visibility = visible
    return obj


def head_placement(x=0.0):
    return App.Placement(V(x, 0, 0), App.Rotation())


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "belly_rails_posts_sub_plate_control_box")
    add_shape(doc, grp, "rails", "belly_rails_40x40x3_x225", G.rails(), "frame")
    add_shape(doc, grp, "rail_bolts", "rail_bolts_8xM10", G.rail_bolts(), "zinc")
    add_shape(doc, grp, "posts", "hanger_posts_30x30x2_rear_axle_line", G.posts(), "frame")
    add_shape(doc, grp, "post_bolts", "post_bolts_M8_rivet_nuts_M6_T_nuts", G.post_bolts(), "zinc")
    add_shape(doc, grp, "sub_plate", "sub_plate_10mm_under_rear_beams_from_spot_sprayer", SG.sub_plate(), "frame")
    add_shape(doc, grp, "sub_bolts", "sub_plate_bolts_8xM10", SG.sub_bolts(), "zinc")
    add_shape(doc, grp, "box_base", "control_box_base_plate_4_extra_holes", G.box_base(), "galv")
    add_shape(doc, grp, "box_bolts", "control_box_bolts_4xM10", SG.box_bolts(), "zinc")
    add_shape(doc, grp, "control_box", "control_box_IP66_controller_valve_and_stepper_driver", SG.control_box(), "box")
    return grp


def build_plumbing(doc, parent):
    grp = new_part(doc, parent, "Plumbing", "pump_filter_regulator_hoses_from_spot_sprayer")
    add_shape(doc, grp, "pump", "pump_diaphragm_24V_11lpm", SG.pump(), "pump")
    add_shape(doc, grp, "pump_mounts", "pump_filter_regulator_brackets", SG.pump_mounts(), "frame")
    add_shape(doc, grp, "filter_bowl", "suction_filter_50_mesh", SG.filter_bowl(), "plastic")
    add_shape(doc, grp, "regulator", "pressure_regulator_3bar_bypass_agitation", SG.regulator(), "red")
    add_shape(doc, grp, "hose_suction", "hose_suction_tank_filter_pump", SG.suction_hose(), "hose")
    add_shape(doc, grp, "hose_return", "hose_bypass_return_to_tank_agitation", SG.return_hose(), "hose")
    add_shape(doc, grp, "hose_feed", "hose_feed_to_drag_chain", G.feed_hose(), "hose")
    return grp


def build_slide(doc, parent, x=0.0):
    grp = new_part(doc, parent, "Slide", "belt_module_stroke_360_across_rear_axle_line")
    add_shape(doc, grp, "module_body", "belt_module_60x45_upside_down", G.module_body(), "module")
    add_shape(doc, grp, "fold_box", "fold_back_belt_box_1_1", G.fold_box(), "carriage")
    add_shape(doc, grp, "motor", "nema23_closed_loop_fold_back", G.motor(), "motor")
    add_shape(doc, grp, "chain_tray", "drag_chain_tray_alu_3mm", G.chain_tray(), "alu")
    add_shape(doc, grp, "drag_chain", "drag_chain_15x20_r25", G.chain(x), "chain")
    return grp


def build_head(doc, parent, x=0.0):
    grp = new_part(doc, parent, "Head", "paint_head_moves_in_x", head_placement(x))
    add_shape(doc, grp, "carriage", "module_carriage_80", G.module_carriage(0.0), "carriage")
    add_shape(doc, grp, "head_plate", "head_plate_6mm_chain_arm", G.head_plate(), "alu")
    add_shape(doc, grp, "stem", "stem_25x25x2_foot_gusset", G.stem(), "alu")
    add_shape(doc, grp, "shroud", "shroud_alu_1_5_200x300x150", G.shroud(), "shroud")
    add_shape(doc, grp, "brush", "brush_skirt_nylon_30", G.brush(), "brush")
    add_shape(doc, grp, "valve", "solenoid_valve_12V_3_8", G.valve(), "valve")
    add_shape(doc, grp, "nozzle", "nozzle_body_tip_4002E_even_fan", G.nozzle(), "nozzle")
    add_shape(doc, grp, "hose_head", "hose_chain_to_valve", G.head_hose(), "hose")
    return grp


def build_into(doc, parent=None, x=0.0):
    """Put the line marker in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "line_marker_simple")
    BS.build_tank(doc, root)
    build_mount(doc, root)
    build_plumbing(doc, root)
    build_slide(doc, root, x)
    build_head(doc, root, x)
    return root


def set_head(x=0.0, doc=None):
    """Nozzle x (mm, -stroke/2 .. +stroke/2): moves the head, regenerates the drag chain."""
    if abs(x) > P.stroke / 2.0 + 1e-6:
        raise ValueError("head x %s outside +-%s" % (x, P.stroke / 2.0))
    doc = active_doc(doc)
    doc.getObject("Head").Placement = head_placement(x)
    doc.getObject("drag_chain").Shape = G.chain(x)
    doc.recompute()


build_robot = BS.build_robot
global_shape = BS.global_shape
_overlaps = BS._overlaps


def set_steering(deg, doc=None):
    BS.set_steering(deg, deg, active_doc(doc))


def build(save=True, show_robot=False, step=True, x=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Line marker simple"
    doc.Comment = ("Generated by build_lmk.py from lmk_params.py (tank, pump and control box from spotspray unit/boom, "
                   "rails from drop on demand boom/simple). Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. build_lmk.set_head(x) moves the paint head.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, x)
    if robot is not None:
        set_robot_visible(bool(show_robot), doc)
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
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in objects_of(doc, ROOT)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


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


# bolts pass through holes in the parts they join, the carriage runs on the module, the chain ends sit in their
# brackets, hoses push into their fittings: those pairs are by design
JOINTS = {("rail_bolts", "rails"), ("rail_bolts", "box_base"), ("post_bolts", "rails"), ("post_bolts", "posts"),
          ("post_bolts", "module_body"), ("sub_bolts", "sub_plate"), ("sub_bolts", "box_base"),
          ("box_bolts", "box_base"), ("cradle_bolts", "cradle_tubes"), ("cradle_bolts", "cradle_pads"),
          ("hose_feed", "regulator"), ("hose_feed", "drag_chain"), ("hose_head", "drag_chain"),
          ("hose_head", "valve"), ("hose_head", "head_plate"), ("nozzle", "shroud"), ("nozzle", "valve")}
BEAM_BOLTS = ("rail_bolts", "sub_bolts", "box_bolts", "cradle_bolts")


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x in BEAM_BOLTS and y.startswith(("lower_beam", "upper_beam")):
            return True
    return False


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: marker parts among themselves and against the robot. Bolts in their
    own holes are skipped (JOINTS); their holes are checked by check_holes()."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """The bolts must sit in holes: overlap of the bolt JOINTS pairs and of the beam bolts with the beams (~0)."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    for o in robot_objects(doc):
        if o.Name.startswith(("lower_beam", "upper_beam")):
            objs[o.Name] = global_shape(o)
    pairs = {p for p in JOINTS if "bolts" in p[0]}
    for b in BEAM_BOLTS:
        for n in objs:
            if n.startswith(("lower_beam", "upper_beam")):
                pairs.add((b, n))
    out = {}
    for a, b in sorted(pairs):
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[str((a, b))] = round(v, 1)
    return out


STROKE_POSES = (-P.stroke / 2.0, -90.0, 0.0, 90.0, P.stroke / 2.0)


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_max, 0.0, P.robot_steer_max)):
    """Interference of the head and the drag chain over the stroke x steering angles against everything else."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Head") + [doc.getObject("drag_chain")]
    names = {o.Name for o in moving}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for x in STROKE_POSES:
            set_head(x, doc)
            mv = [(o, global_shape(o)) for o in moving]
            pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
            pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                      if not _joint(mv[i][0].Name, mv[j][0].Name)]
            hits = _overlaps(pairs, tol)
            if hits:
                out[str((st, x))] = hits
    set_steering(0.0, doc)
    set_head(0.0, doc)
    return out


def tyre_envelope(x, y, steer):
    """Plain cylinder O430 x 100 for a tyre (the lugged tyre is very slow in distToShape)."""
    c = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, V(x - P.robot_tire_w / 2.0, y, P.robot_axle_z), V(1, 0, 0))
    c.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return c


def clearance(doc=None):
    """Smallest distance (mm) of the head, the module and the motor to the rear tyres at the stroke ends."""
    doc = active_doc(doc)
    tg = [tyre_envelope(sx * P.robot_wheel_x, -P.robot_axle_y, 0.0) for sx in (-1, 1)]
    out = {}
    for x in (-P.stroke / 2.0, P.stroke / 2.0):
        set_head(x, doc)
        best = (1e9, None)
        for n in ("shroud", "brush", "head_plate", "module_body", "fold_box", "motor", "chain_tray"):
            s = global_shape(doc.getObject(n))
            for t in tg:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, n)
        out["x_%+d" % x] = (round(best[0], 1), best[1])
    set_head(0.0, doc)
    return out


MASS_FIXED = {"pump": P.S.pump_kg, "filter_bowl": 0.6, "regulator": 1.2, "control_box": 6.5, "level_sensor": 0.3,
              "tank_fittings": 0.6, "motor": P.nema_kg + 0.3, "valve": 0.45, "nozzle": 0.12,
              "drag_chain": 0.25, "carriage": P.car_kg}
DENSITY = (("tank_shell", 0.95e-6), ("cradle_pads", 1.2e-6), ("hose_", 1.6e-6), ("module_body", 0.45 * P.alu),
           ("fold_box", 0.5 * P.alu), ("chain_tray", P.alu), ("head_plate", P.alu), ("stem", P.alu),
           ("shroud", P.alu), ("brush", P.nylon))


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
    """Mass (kg) and centre of gravity (robot coordinates), tank empty."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Tank", "Mount", "Plumbing", "Slide", "Head"):
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
set_camera = BS.set_camera


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


GROUND = "render_turf"
LINES = "render_lines"
FAN = "render_fan"


def add_ground(doc, x_head=0.0):
    """Turf with a fresh line behind the nozzle, a corner arc and the touchline it joins."""
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span((-2600.0, 2600.0), (-3200.0, 1600.0), (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.36, 0.60, 0.25)
    w = P.line_width()
    xl = x_head
    strips = [G.line_strip(xl, -3200.0, xl, P.nozzle_y, w)]
    strips.append(G.line_strip(xl - 1500.0, -3200.0 + 50.0, xl - 1500.0, 1600.0, w))
    obj2 = doc.addObject("Part::Feature", LINES)
    obj2.Shape = Part.makeCompound(strips)
    obj2.ViewObject.ShapeColor = COLOR["paint"]
    fan = doc.addObject("Part::Feature", FAN)
    s = G.fan()
    s.translate(V(x_head, 0, 0))
    fan.Shape = s
    fan.ViewObject.ShapeColor = (0.85, 0.90, 0.98)
    fan.ViewObject.Transparency = 40
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_ground(doc)
    out.append(save_view("1_iso_on_robot_painting.png", (-1.0, 1.0, -0.6), target=(0, -600, 350), height=2600))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, -100, 450), height=1900))
    out.append(save_view("3_rear_on_robot.png", (0.0, 1.0, -0.05), target=(0, 0, 400), height=1500))
    remove(doc, [GROUND, LINES, FAN])
    set_head(P.stroke / 2.0, doc)
    for n in ("tank_shell", "straps", "cradle_tubes", "cradle_pads", "tank_fittings", "level_sensor", "cradle_bolts"):
        doc.getObject(n).ViewObject.Visibility = False
    out.append(save_view("4_slide_head_right_end.png", (-0.9, -1.0, -0.55), target=(60, -500, 350), height=1000))
    set_robot_visible(False, doc)
    out.append(save_view("5_slide_from_below.png", (0.3, 0.45, 1.0), target=(0, -500, 380), height=900))
    set_head(-P.stroke / 2.0, doc)
    doc.getObject("shroud").ViewObject.Transparency = 70
    doc.getObject("brush").ViewObject.Transparency = 60
    out.append(save_view("6_head_detail_left_end.png", (-1.0, -0.8, -0.35), target=(-180, -520, 300), height=600))
    doc.getObject("shroud").ViewObject.Transparency = 0
    doc.getObject("brush").ViewObject.Transparency = 0
    set_head(0.0, doc)
    set_robot_visible(True, doc)
    out.append(save_view("7_top_on_robot.png", (0.0, 0.0, -1.0), target=(0, 0, 0), up=(0.0, 1.0, 0.0), height=1800))
    App.closeDocument(doc.Name)
    build()
    return out
