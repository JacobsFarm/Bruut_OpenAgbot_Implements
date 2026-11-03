"""Model of the drop-on-demand boom on the Bruut OpenAgbot (standard robot).

Tank, cradle, pump, filter, regulator, suction / return hoses and the control box are built from "spotspray unit/boom"
(build_ssp, ssp_parts); this file adds the belly rails, the hanger posts and the hood with the camera, LEDs and the
injector rail.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_ddb
    build_ddb.build()                      # saves FCStd and STEP (hood at the middle height step)
    build_ddb.set_height(25)               # hood height step (-25, 0, 25 mm)
    build_ddb.check_interference()         # overlap in the current pose (must be empty)
    build_ddb.check_holes()                # bolts and pins in their holes (must be empty)
    build_ddb.check_poses()                # overlap over the height steps x steering +-30 (must be empty)
    build_ddb.clearance()                  # smallest distance of the hood to the tyres over steering
    build_ddb.mass_properties()
    build_ddb.render_all()                 # all images in previews/
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ddb_params as P
import ddb_parts as G
import ssp_parts as SG
import build_ssp as BS

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Drop_On_Demand_Boom"
SAVE_BASE = os.path.join(FOLDER, "Drop_On_Demand_Boom")
ROOT = "Drop_on_demand_boom"

COLOR = dict(BS.COLOR)
COLOR.update({
    "hood": (0.22, 0.24, 0.26),
    "brush": (0.12, 0.12, 0.12),
    "led": (0.98, 0.98, 0.85),
    "injector": (0.15, 0.55, 0.85),
    "manifold": (0.80, 0.81, 0.83),
    "accu": (0.85, 0.15, 0.10),
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


def hood_placement(dz=0.0):
    return App.Placement(V(0, 0, dz), App.Rotation())


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "belly_rails_rear_subframe_control_box")
    add_shape(doc, grp, "rails", "belly_rails_40x40x3_x225", G.rails(), "frame")
    add_shape(doc, grp, "rail_bolts", "rail_bolts_8xM10", G.rail_bolts(), "zinc")
    add_shape(doc, grp, "posts", "hanger_posts_30x30x2_feet_8mm", G.posts(), "frame")
    add_shape(doc, grp, "post_bolts", "post_foot_bolts_M8_rivet_nuts", G.post_bolts(), "zinc")
    add_shape(doc, grp, "sub_plate", "sub_plate_10mm_under_rear_beams_from_spot_sprayer", SG.sub_plate(), "frame")
    add_shape(doc, grp, "sub_bolts", "sub_plate_bolts_8xM10", SG.sub_bolts(), "zinc")
    add_shape(doc, grp, "box_base", "control_box_base_plate_4_extra_holes", G.box_base(), "galv")
    add_shape(doc, grp, "box_bolts", "control_box_bolts_4xM10", SG.box_bolts(), "zinc")
    add_shape(doc, grp, "control_box", "control_box_IP66_vision_computer_24ch_injector_driver", SG.control_box(), "box")
    return grp


def build_plumbing(doc, parent):
    grp = new_part(doc, parent, "Plumbing", "pump_filter_regulator_hoses_from_spot_sprayer")
    add_shape(doc, grp, "pump", "pump_diaphragm_24V_11lpm", SG.pump(), "pump")
    add_shape(doc, grp, "pump_mounts", "pump_filter_regulator_brackets", SG.pump_mounts(), "frame")
    add_shape(doc, grp, "filter_bowl", "suction_filter_50_mesh", SG.filter_bowl(), "plastic")
    add_shape(doc, grp, "regulator", "pressure_regulator_3bar_bypass_sensor", SG.regulator(), "red")
    add_shape(doc, grp, "hose_suction", "hose_suction_tank_filter_pump", SG.suction_hose(), "hose")
    add_shape(doc, grp, "hose_return", "hose_bypass_return_to_tank", SG.return_hose(), "hose")
    add_shape(doc, grp, "hose_feed", "hose_feed_to_low_pressure_regulator", G.feed_hose(), "hose")
    return grp


def build_hood(doc, parent, dz=0.0):
    grp = new_part(doc, parent, "Hood", "hood_600_camera_leds_24_injectors_moves_with_height_step", hood_placement(dz))
    add_shape(doc, grp, "hood_shell", "hood_alu_2mm_600x524x360", G.hood_shell(), "hood")
    add_shape(doc, grp, "brush_holder", "brush_holder_alu_U", G.holder(), "alu")
    add_shape(doc, grp, "brush", "brush_strip_nylon_50", G.brush(), "brush")
    add_shape(doc, grp, "post_brackets", "post_brackets_6mm", G.post_brackets(), "frame")
    add_shape(doc, grp, "bracket_bolts", "post_bracket_bolts_8xM8", G.bracket_bolts(), "zinc")
    add_shape(doc, grp, "pins", "height_pins_M10_R_clip", G.pins(), "steel")
    add_shape(doc, grp, "camera_bracket", "camera_angle_bracket_5mm", G.camera_bracket(), "alu")
    add_shape(doc, grp, "camera", "camera_5MP_global_shutter_f3_5_down", G.camera(), "camera")
    add_shape(doc, grp, "camera_glass", "camera_lens_window", G.camera_glass(), "glass")
    add_shape(doc, grp, "led_bars", "led_bars_2x24W", G.led_bars(), "alu")
    add_shape(doc, grp, "led_lenses", "led_bar_lenses", G.led_lenses(), "led")
    add_shape(doc, grp, "manifold", "injector_manifold_alu_590x30x25", G.manifold(), "manifold")
    add_shape(doc, grp, "manifold_brackets", "manifold_brackets_4mm", G.manifold_brackets(), "alu")
    add_shape(doc, grp, "injectors", "micro_injectors_12V_24x_pitch_25", G.injectors(), "injector")
    add_shape(doc, grp, "bleed_valve", "bleed_valve_manifold", G.bleed_valve(), "steel")
    add_shape(doc, grp, "lp_regulator", "low_pressure_regulator_0_5bar_gauge", G.lp_regulator(), "red")
    add_shape(doc, grp, "accumulator", "accumulator_pulsation_damper", G.accumulator(), "accu")
    add_shape(doc, grp, "hose_drop", "hose_regulator_to_manifold", G.drop_hose(), "hose")
    return grp


def build_into(doc, parent=None, dz=0.0):
    """Put the boom in a document, in robot coordinates (also used by animate_ddb.py)."""
    root = new_part(doc, parent, ROOT, "drop_on_demand_boom_simple")
    BS.build_tank(doc, root)
    build_mount(doc, root)
    build_plumbing(doc, root)
    build_hood(doc, root, dz)
    return root


def set_height(dz=0.0, doc=None):
    if dz not in P.height_steps:
        raise ValueError("height step %s not in %s" % (dz, P.height_steps))
    doc = active_doc(doc)
    doc.getObject("Hood").Placement = hood_placement(dz)
    doc.recompute()


build_robot = BS.build_robot
global_shape = BS.global_shape
_overlaps = BS._overlaps


def set_steering(deg, doc=None):
    BS.set_steering(deg, deg, active_doc(doc))


def build(save=True, show_robot=False, step=True, dz=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Drop on demand boom simple"
    doc.Comment = ("Generated by build_ddb.py from ddb_params.py (tank, pump and control box from spotspray unit/boom). "
                   "Robot coordinates: x = right, y = driving direction (front = +y), z = up, ground = z 0. Middle height "
                   "step; build_ddb.set_height() moves the hood.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, dz)
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


# bolts and pins pass through holes in the parts they join: those pairs are by design
JOINTS = {("rail_bolts", "rails"), ("rail_bolts", "box_base"), ("post_bolts", "rails"), ("post_bolts", "posts"),
          ("sub_bolts", "sub_plate"), ("sub_bolts", "box_base"), ("box_bolts", "box_base"),
          ("bracket_bolts", "post_brackets"), ("bracket_bolts", "hood_shell"), ("pins", "post_brackets"),
          ("pins", "posts"), ("hose_drop", "hood_shell"), ("hose_drop", "manifold"), ("injectors", "manifold"),
          ("bleed_valve", "manifold"),
          ("hose_feed", "regulator"), ("hose_feed", "lp_regulator"), ("hose_drop", "lp_regulator"), ("cradle_bolts", "cradle_tubes"), ("cradle_bolts", "cradle_pads")}
BEAM_BOLTS = ("rail_bolts", "sub_bolts", "box_bolts", "cradle_bolts")


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x in BEAM_BOLTS and y.startswith(("lower_beam", "upper_beam")):
            return True
    return False


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: boom parts among themselves and against the robot. Bolts and pins in
    their own holes are skipped (JOINTS); their holes are checked by check_holes()."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """The bolts and pins must sit in holes: overlap of the JOINTS pairs and of the beam bolts with the beams (~0)."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    for o in robot_objects(doc):
        if o.Name.startswith(("lower_beam", "upper_beam")):
            objs[o.Name] = global_shape(o)
    pairs = set(JOINTS)
    for b in BEAM_BOLTS:
        for n in objs:
            if n.startswith(("lower_beam", "upper_beam")):
                pairs.add((b, n))
    out = {}
    for a, b in sorted(pairs):
        if a.startswith("hose_"):
            continue                                # hose ends are pushed into the ports of the fittings
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[str((a, b))] = round(v, 1)
    return out


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_max, 0.0, P.robot_steer_max)):
    """Interference of the hood group over the height steps x steering angles against everything else. Must be empty."""
    doc = active_doc(doc)
    hood = objects_of(doc, "Hood")
    names = {o.Name for o in hood}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for dz in P.height_steps:
            set_height(dz, doc)
            hd = [(o, global_shape(o)) for o in hood]
            hits = _overlaps([(a, b) for a in hd for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
            if hits:
                out[str((st, dz))] = hits
    set_steering(0.0, doc)
    set_height(0.0, doc)
    return out


def tyre_envelope(x, y, steer):
    """Plain cylinder O430 x 100 for a tyre (the lugged tyre is very slow in distToShape)."""
    c = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, V(x - P.robot_tire_w / 2.0, y, P.robot_axle_z), V(1, 0, 0))
    c.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return c


def clearance(doc=None, steer=(-P.robot_steer_max, 0.0, P.robot_steer_max)):
    """Smallest distance (mm) of the hood and the rails to the tyres (front steered, rear straight)."""
    doc = active_doc(doc)
    parts = [doc.getObject(n) for n in ("hood_shell", "brush_holder", "brush", "rails", "posts")]
    best = (1e9, None, None)
    for st in steer:
        tg = [tyre_envelope(sx * P.robot_wheel_x, P.robot_axle_y, st) for sx in (-1, 1)]
        tg += [tyre_envelope(sx * P.robot_wheel_x, -P.robot_axle_y, 0.0) for sx in (-1, 1)]
        for o in parts:
            s = global_shape(o)
            for i, t in enumerate(tg):
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name, (st, "front" if i < 2 else "rear"))
    return round(best[0], 1), best[1], best[2]


def ground_contact(doc=None):
    """Lowest point (z) of the brush, the skirt and the injector tips at the 3 height steps."""
    doc = active_doc(doc)
    out = {}
    for dz in P.height_steps:
        set_height(dz, doc)
        out["step_%+d" % dz] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1)
                                for n in ("brush", "hood_shell", "injectors", "camera")}
    set_height(0.0, doc)
    return out


MASS_FIXED = {"pump": P.S.pump_kg, "filter_bowl": 0.6, "regulator": 1.2, "control_box": 6.5, "camera_glass": 0.02,
              "camera": 0.6, "level_sensor": 0.3, "tank_fittings": 0.6, "injectors": 24 * 0.06, "led_bars": 1.4,
              "led_lenses": 0.1, "lp_regulator": 0.5, "accumulator": 0.8, "bleed_valve": 0.1}
DENSITY = (("tank_shell", 0.95e-6), ("cradle_pads", 1.2e-6), ("hose_", 1.6e-6), ("hood_shell", P.alu),
           ("brush_holder", P.alu), ("brush", P.nylon), ("camera_bracket", P.alu), ("manifold", P.alu))


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key in sorted(MASS_FIXED, key=len, reverse=True):
        if obj.Name == key:
            return MASS_FIXED[key], cg
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
    for name in (ROOT, "Tank", "Mount", "Plumbing", "Hood"):
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


GROUND = "render_ground"
PLANTS = "render_plants"


def add_ground(doc, y=(-1400.0, 1500.0)):
    """Bed with 2 rows of lettuce and a few weed seedlings."""
    import random
    obj = doc.addObject("Part::Feature", GROUND)
    paths = G.box_span((-1300.0, 1300.0), y, (-100.0, -60.0))
    obj.Shape = Part.makeCompound([G.bed(y[0], y[1]), paths])
    obj.ViewObject.ShapeColor = (0.45, 0.33, 0.22)
    rnd = random.Random(3)
    shapes = [G.lettuce(x, yy, 120.0, int(yy) + int(x)) for x in P.crop_rows
              for yy in range(int(y[0]) + 100, int(y[1]) - 100, int(P.crop_spacing))]
    obj2 = doc.addObject("Part::Feature", PLANTS)
    obj2.Shape = Part.makeCompound(shapes)
    obj2.ViewObject.ShapeColor = (0.35, 0.65, 0.20)
    weeds = [G.weed(rnd.uniform(-280, 280), rnd.uniform(y[0] + 100, y[1] - 100), rnd.uniform(*P.weed_d), i)
             for i in range(30)]
    obj3 = doc.addObject("Part::Feature", PLANTS + "_weeds")
    obj3.Shape = Part.makeCompound(weeds)
    obj3.ViewObject.ShapeColor = (0.20, 0.45, 0.10)
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
    out.append(save_view("1_iso_on_robot_in_bed.png", (-1.0, -1.1, -0.65), target=(0, 0, 450), height=2300))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, 0, 450), height=1900))
    out.append(save_view("3_front_over_bed.png", (0.0, -1.0, -0.05), target=(0, 0, 400), height=1500))
    doc.getObject("hood_shell").ViewObject.Transparency = 75
    doc.getObject("brush").ViewObject.Transparency = 60
    doc.getObject("brush_holder").ViewObject.Transparency = 60
    out.append(save_view("4_hood_see_through_iso.png", (-1.0, -0.9, -0.55), target=(0, 0, 250), height=1100))
    remove(doc, [GROUND, PLANTS, PLANTS + "_weeds"])
    set_robot_visible(False, doc)
    out.append(save_view("5_inside_from_below.png", (0.25, 0.35, 1.0), target=(0, 0, 250), height=900))
    out.append(save_view("6_injector_rail_detail.png", (-1.0, 0.6, -0.35), target=(-200, -205, 150), height=380))
    for n in ("hood_shell", "brush", "brush_holder"):
        doc.getObject(n).ViewObject.Transparency = 0
    set_robot_visible(True, doc)
    set_steering(P.robot_steer_max, doc)
    out.append(save_view("7_top_steered_30deg.png", (0.0, 0.0, -1.0), target=(0, 0, 0), up=(0.0, 1.0, 0.0),
                         height=1800))
    set_steering(0.0, doc)
    for n in ("tank_shell", "straps", "cradle_tubes", "cradle_pads", "tank_fittings", "level_sensor", "cradle_bolts"):
        doc.getObject(n).ViewObject.Visibility = False
    out.append(save_view("8_rails_posts_rear_mount.png", (-1.0, 0.7, -0.5), target=(150, -250, 550), height=1100))
    App.closeDocument(doc.Name)
    build()
    return out
