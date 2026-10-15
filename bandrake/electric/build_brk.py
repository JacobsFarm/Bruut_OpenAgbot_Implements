"""Model of the electric belt rake on the front of the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_brk
    build_brk.build()                          # saves FCStd and STEP (rake down, comb mode)
    build_brk.set_pose(lift=100, phase=60)     # rake raised on its castor actuators (mm), belt position (mm)
    build_brk.check_interference()             # overlap in the current pose (must be empty)
    build_brk.check_fit()                      # overlap over the lift and a belt pitch (must be empty)
    build_brk.clearance()                      # distances to the front wheels at full steering lock, GNSS, beams
    build_brk.mass_properties()
    build_brk.render_all()                     # all images in previews/
"""
import math
import os
import random
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import brk_params as P
import brk_calc as C
import brk_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Belt_Rake_Electric"
SAVE_BASE = os.path.join(FOLDER, "Belt_Rake_Electric")
ROOT = "Belt_rake"

COLOR = {
    "frame": (0.90, 0.30, 0.10),
    "alu": (0.95, 0.80, 0.15),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "galv": (0.70, 0.72, 0.74),
    "rubber": (0.10, 0.10, 0.10),
    "belt": (0.16, 0.16, 0.17),
    "tine": (0.30, 0.31, 0.33),
    "bar": (0.85, 0.15, 0.10),
    "uhmw": (0.95, 0.95, 0.93),
    "motor": (0.15, 0.15, 0.17),
    "gearbox": (0.55, 0.57, 0.60),
    "bearing": (0.30, 0.32, 0.36),
    "hub": (0.85, 0.75, 0.15),
    "actuator": (0.30, 0.31, 0.33),
    "box": (0.55, 0.57, 0.60),
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


# ---------------------------------------------------------------------
# Pose: lift of the rake (parallelogram) and the belt position
# ---------------------------------------------------------------------
BARS = ["Bar_%02d" % k for k in range(P.n_bars)]
MOVING = ("Rake", "Upper_arms", "Lower_arms", "Castor_drop") + tuple(BARS)


def pose_placements(lift=0.0, phase=0.0):
    """lift: the rake above its working height (mm). Up to lift_travel the castor actuators push it up (the castors stay
    on the ground); beyond that up to float_up the parallelogram floats (castors lifted with the rake, e.g. on a hump)."""
    if not -1e-6 <= lift <= P.float_up + 1e-6:
        raise ValueError("lift %.1f outside 0 .. %.1f" % (lift, P.float_up))
    dy, dz, beta = C.head_offset(lift)
    out = {"Rake": App.Placement(V(0, dy, dz), App.Rotation())}
    for name, z in (("Upper_arms", P.pin_z[0]), ("Lower_arms", P.pin_z[1])):
        out[name] = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), beta), V(0, P.pin_front_y, z))
    out["Castor_drop"] = App.Placement(V(0, 0, -min(lift, P.lift_travel)), App.Rotation())
    for k, name in enumerate(BARS):
        out[name] = G.bar_placement(phase + k * P.bar_pitch)
    return out


def set_pose(lift=0.0, phase=0.0, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(lift, phase).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_rake(doc, parent, pl):
    rake = new_part(doc, parent, "Rake", "belt_rake_1500", pl["Rake"])
    fr = new_part(doc, rake, "Rake_frame", "rake_frame")
    add_shape(doc, fr, "side_plates", "side_plates_alu_3mm_stadium", G.side_plates(), "alu")
    add_shape(doc, fr, "rails", "side_rails_60x30x2", G.rails(), "frame")
    add_shape(doc, fr, "bearing_plates", "bearing_plates_6mm_tension_slots_left", G.bearing_plates(), "frame")
    add_shape(doc, fr, "cross_tubes", "cross_tubes_50x50x3_through_the_loop", G.cross_tubes(), "frame")
    add_shape(doc, fr, "stub", "roll_stub_D50", G.stub(), "steel")
    add_shape(doc, fr, "guide_flat", "bottom_run_guide_flat_and_posts", G.guide_flat(), "frame")
    add_shape(doc, fr, "guide_strip", "bottom_run_guide_UHMW_10mm", G.guide_strip(), "uhmw")
    add_shape(doc, fr, "castor_arms", "castor_arms_40x40_height_holes", G.castor_arms(), "frame")
    add_shape(doc, fr, "board_support", "swath_board_post_arm_hinge", G.board_support(), "frame")
    add_shape(doc, fr, "swath_board", "swath_board_3mm", G.swath_board(), "alu")
    add_shape(doc, fr, "head", "rake_head_sleeve_lugs", G.head(), "frame")
    add_shape(doc, fr, "head_pins", "parallelogram_rear_pins_D20", G.head_pins(), "steel")
    add_shape(doc, fr, "stub_collar", "roll_stub_collar", G.stub_collar(), "steel")
    dr = new_part(doc, rake, "Rake_drive", "drums_belt_drive")
    add_shape(doc, dr, "drums", "drums_D220_crowned", G.drums(), "galv")
    add_shape(doc, dr, "shafts", "drum_shafts_D30", G.shafts(), "steel")
    add_shape(doc, dr, "bearings", "flange_bearings_UCF206_4x", G.bearings(), "bearing")
    add_shape(doc, dr, "belt", "belt_rubber_260x8", G.belt(), "belt")
    add_shape(doc, dr, "gearbox", "planetary_gearbox_20to1", G.gearbox(), "gearbox")
    add_shape(doc, dr, "motor", "motor_BLDC_48V_750W", G.motor(), "motor")
    cs = new_part(doc, rake, "Castors", "castors_D200_swivel_on_actuators")
    add_shape(doc, cs, "castor_act_bodies", "castor_actuators_24V_1000N_stroke_150", G.castor_act_bodies(), "actuator")
    dp = new_part(doc, cs, "Castor_drop", "castor_rods_and_wheels", pl["Castor_drop"])
    add_shape(doc, dp, "castor_act_rods", "castor_actuator_rods", G.castor_act_rods(), "steel")
    add_shape(doc, dp, "castor_frames", "castor_plates_swivels_forks", G.castor_frames(), "galv")
    add_shape(doc, dp, "castor_tyres", "castor_tyres_200x60", G.castor_tyres(), "rubber")
    add_shape(doc, dp, "castor_hubs", "castor_hubs", G.castor_hubs(), "hub")
    tg = new_part(doc, rake, "Tine_bars", "tine_bars_%dx" % P.n_bars)
    bar, bolts, tines = G.bar_local()
    for k, name in enumerate(BARS):
        b = new_part(doc, tg, name, "tine_bar_%02d" % k, pl[name])
        add_shape(doc, b, "bar_tube_%02d" % k, "bar_25x25x2.5_%02d" % k, bar, "bar")
        add_shape(doc, b, "bar_bolts_%02d" % k, "bar_bolts_M8_%02d" % k, bolts, "zinc")
        add_shape(doc, b, "tines_%02d" % k, "spring_tines_3x_double_D5.5_%02d" % k, tines, "tine")
    return rake


def build_mount(doc, parent, pl):
    grp = new_part(doc, parent, "Mount", "mount_headstock_parallelogram")
    add_shape(doc, grp, "mount_plate", "mount_plate_8mm_under_front_beams", G.mount_plate(), "frame")
    add_shape(doc, grp, "mount_bolts", "mount_bolts_4xM10", G.mount_bolts(), "zinc")
    add_shape(doc, grp, "headstock", "headstock_plates_8mm_actuator_lug", G.headstock(), "frame")
    add_shape(doc, grp, "front_pins", "parallelogram_front_pins_D20", G.front_pins(), "steel")
    up = new_part(doc, grp, "Upper_arms", "upper_arms", pl["Upper_arms"])
    add_shape(doc, up, "upper_arm_tubes", "upper_arms_40x40x3", G.upper_arms(), "frame")
    lo = new_part(doc, grp, "Lower_arms", "lower_arms", pl["Lower_arms"])
    add_shape(doc, lo, "lower_arm_tubes", "lower_arms_40x40x3_cross_tube_lug", G.lower_arms(), "frame")
    cb = new_part(doc, grp, "Control", "control_box")
    add_shape(doc, cb, "box_base", "control_box_base_plate_4mm", G.box_base(), "frame")
    add_shape(doc, cb, "box_bolts", "control_box_bolts_4xM10", G.box_bolts(), "zinc")
    add_shape(doc, cb, "control_box", "control_box_IP66_48V_motor_controller", G.control_box(), "box")
    return grp


def build_into(doc, parent=None, lift=0.0, phase=0.0):
    """Put the rake in a document, in robot coordinates (also used by animate_brk.py)."""
    pl = pose_placements(lift, phase)
    root = new_part(doc, parent, ROOT, "electric_belt_rake_1500")
    build_mount(doc, root, pl)
    build_rake(doc, root, pl)
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


def build(lift=0.0, phase=0.0, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Electric belt rake"
    doc.Comment = ("Generated by build_brk.py from brk_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Pose with build_brk.set_pose(lift, phase).")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, lift, phase)
    if robot is not None:
        set_robot_visible(bool(show_robot), doc)
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
    if d is not None and d.getObject(ROOT) is not None:
        return d
    for n in App.listDocuments():
        d = App.getDocument(n)
        if d.getObject(ROOT) is not None:
            return d
    raise RuntimeError("no belt rake document open")


def rake_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in rake_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in rake_objects(doc):
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


# parts that sit in each other on purpose (pins in holes, shafts in bearings, bolts through the belt, ...)
TOUCH = (("front_pins", "headstock"), ("front_pins", "upper_arm_tubes"), ("front_pins", "lower_arm_tubes"),
         ("head_pins", "head"), ("head_pins", "upper_arm_tubes"), ("head_pins", "lower_arm_tubes"),
         ("shafts", "drums"), ("shafts", "bearings"), ("shafts", "gearbox"), ("shafts", "bearing_plates"),
         ("shafts", "side_plates"), ("shafts", "rails"), ("stub", "cross_tubes"), ("stub", "rails"), ("stub", "head"),
         ("stub", "stub_collar"), ("stub", "side_plates"), ("bar_bolts", "belt"), ("bar_bolts", "bar_tube"),
         ("tines", "bar_tube"), ("mount_bolts", "mount_plate"), ("box_bolts", "box_base"),
         ("castor_act_rods", "castor_act_bodies"), ("castor_act_rods", "castor_frames"),
         ("castor_act_bodies", "castor_arms"), ("guide_strip", "guide_flat"), ("castor_frames", "castor_tyres"),
         ("castor_frames", "castor_hubs"), ("castor_frames", "castor_arms"), ("castor_hubs", "castor_tyres"),
         ("board_support", "swath_board"), ("board_support", "rails"), ("cross_tubes", "side_plates"),
         ("rails", "bearing_plates"), ("rails", "side_plates"), ("castor_arms", "rails"), ("guide_flat", "cross_tubes"),
         ("bearings", "bearing_plates"), ("gearbox", "bearings"), ("motor", "gearbox"))


def _touch(a, b):
    for p, q in TOUCH:
        if (a.startswith(p) and b.startswith(q)) or (a.startswith(q) and b.startswith(p)):
            return True
    return False


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        if _touch(oa.Name, ob.Name):
            continue
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


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3) in the current pose: rake parts among themselves and against the robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in rake_objects(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def check_fit(doc=None, tol=1.0):
    """Interference over the lift (0, half, full, float stop) and over one bar pitch of the belt. Must be empty."""
    doc = active_doc(doc)
    out = {}
    poses = [(0.0, 0.0), (0.0, P.bar_pitch / 3.0), (0.0, 2.0 * P.bar_pitch / 3.0),
             (P.lift_travel / 2.0, 0.0), (P.lift_travel, 0.0), (P.float_up, 0.0)]
    for pose in poses:
        set_pose(*pose, doc=doc)
        hits = check_interference(doc, tol)
        if hits:
            out[pose] = hits
    set_pose(doc=doc)
    return out


def _min_dist(objs, targets):
    best = (1e9, None, None)
    for o in objs:
        s = global_shape(o)
        for t in targets:
            ts = global_shape(t)
            if s.BoundBox.isValid() and ts.BoundBox.isValid():
                d = s.distToShape(ts)[0]
                if d < best[0]:
                    best = (d, o.Name, t.Name)
    return (round(best[0], 1), best[1], best[2])


def set_steering(left_deg, right_deg, doc):
    for name, angle in (("FL_steered", left_deg), ("FR_steered", right_deg)):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle))
    doc.recompute()


def clearance(doc=None):
    """Smallest distances (mm): rake and mount to the front wheel units at full steering lock (down and lifted), mount
    plate to the GNSS stem. The tyres are left out of the rake check above their bounding box (only the tread
    near the rake matters)."""
    doc = active_doc(doc)
    if doc.getObject("Robot") is None:
        return {}
    out = {}
    front = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
    rake = [o for o in rake_objects(doc) if o.getParentGeoFeatureGroup() is not None and
            o.getParentGeoFeatureGroup().Name in ("Rake_frame", "Rake_drive", "Castors")]
    mount = [o for o in doc.getObject("Mount").OutListRecursive if o.TypeId == "Part::Feature"]
    for lift in (0.0, P.float_up):
        set_pose(lift, 0.0, doc)
        for steer in (-P.robot_steer_max, P.robot_steer_max):
            set_steering(steer, steer, doc)
            out["rake_to_front_units_lift_%d_steer_%+d" % (lift, steer)] = _min_dist(rake, front)
            out["mount_to_front_units_lift_%d_steer_%+d" % (lift, steer)] = _min_dist(mount, front)
        set_steering(0.0, 0.0, doc)
    set_pose(doc=doc)
    gnss = [doc.getObject(n) for n in ("gnss_mount", "gnss_dome") if doc.getObject(n) is not None]
    out["mount_to_gnss"] = _min_dist(mount, gnss)
    return out


MASS_FIXED = {"motor": P.motor_kg, "gearbox": P.gear_kg, "bearings": 4 * P.bearing_kg, "castor_tyres": 2.0,
              "castor_hubs": 1.0, "castor_frames": 2 * P.caster_kg - 3.0, "control_box": 3.0,
              "castor_act_bodies": 2 * (P.cact_kg - 0.5), "castor_act_rods": 1.0}
DENSITY = (("side_plates", 2.7e-6), ("swath_board", 2.7e-6), ("belt", 1.3e-6), ("guide_strip", 0.95e-6))
STEEL = 7.85e-6


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key in sorted(MASS_FIXED, key=len, reverse=True):
        if obj.Name.startswith(key):
            return MASS_FIXED[key], cg
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
    """Mass (kg) and centre of gravity (robot coordinates) in the current pose."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(rake_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for name in ("Rake", "Mount", "Tine_bars", "Rake_drive", "Castors", "Castor_drop", "Upper_arms", "Lower_arms"):
        ms, cs = _sum(objs_of(name))
        out[name.lower() + "_kg"] = round(ms, 2)
        if name in ("Rake", "Mount"):
            out[name.lower() + "_cg"] = (round(cs.x), round(cs.y), round(cs.z))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in rake_objects(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin)), (
        round(bb.XMax), round(bb.YMax), round(bb.ZMax))


# ---------------------------------------------------------------------
# Scene for the images
# ---------------------------------------------------------------------
SCENE = ("render_floor", "render_litter", "render_windrow", "render_trees", "render_weeds")


def add_grass_scene(doc, y=(-900.0, 3200.0), x=(-1600.0, 1600.0)):
    floor = doc.addObject("Part::Feature", "render_floor")
    floor.Shape = G.box_span(x, y, (-40.0, 0.0))
    floor.ViewObject.ShapeColor = (0.50, 0.64, 0.32)
    rnd = random.Random(5)
    lit = [G.straw(rnd.uniform(-850, 850), rnd.uniform(P.rake_y + 150, y[1] - 100), rnd.uniform(40, 110),
                   rnd.uniform(0, 180)) for _ in range(700)]
    o = doc.addObject("Part::Feature", "render_litter")
    o.Shape = Part.makeCompound(lit)
    o.ViewObject.ShapeColor = (0.72, 0.64, 0.38)
    o.ViewObject.DisplayMode = "Shaded"
    win = [G.straw(rnd.gauss(-930, 45), rnd.uniform(y[0] + 100, P.rake_y - 150), rnd.uniform(40, 110),
                   rnd.uniform(0, 180), z=rnd.uniform(1, 35)) for _ in range(800)]
    w = doc.addObject("Part::Feature", "render_windrow")
    w.Shape = Part.makeCompound(win)
    w.ViewObject.ShapeColor = (0.72, 0.64, 0.38)
    w.ViewObject.DisplayMode = "Shaded"
    doc.recompute()


def add_nursery_scene(doc, y=(-900.0, 3200.0), x=(-1600.0, 1600.0)):
    floor = doc.addObject("Part::Feature", "render_floor")
    floor.Shape = G.box_span(x, y, (-40.0, 0.0))
    floor.ViewObject.ShapeColor = (0.45, 0.33, 0.22)
    rnd = random.Random(7)
    trees = []
    for rx in range(-675, 700, 150):
        if abs(abs(rx) - P.robot_wheel_x) < 100.0:      # lanes for the robot wheels and the castors
            continue
        yy = y[0] + 60.0
        while yy < y[1] - 60:
            trees.append(G.tree(rx + rnd.uniform(-8, 8), yy, rnd.uniform(130, 175), rnd.randint(0, 99)))
            yy += rnd.uniform(70, 110)
    t = doc.addObject("Part::Feature", "render_trees")
    t.Shape = Part.makeCompound(trees)
    t.ViewObject.ShapeColor = (0.20, 0.42, 0.25)
    weeds = [G.weed(rnd.uniform(-750, 750), rnd.uniform(P.rake_y + 150, y[1] - 100), rnd.uniform(0.6, 1.1))
             for _ in range(260)]
    w = doc.addObject("Part::Feature", "render_weeds")
    w.Shape = Part.makeCompound(weeds)
    w.ViewObject.ShapeColor = (0.45, 0.78, 0.25)
    doc.recompute()


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


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
    tgt = V(*target) if target is not None else V(0, 0, 400)
    eye = tgt - d * 12000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(40000.0)
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
    doc = build(save=False, show_robot=True, step=False)
    add_grass_scene(doc)
    out.append(save_view("1_work_iso_on_robot.png", (1.0, -1.2, -0.75), target=(-100, 650, 350), height=3000))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, 550, 450), height=1900))
    out.append(save_view("3_front.png", (0.0, -1.0, -0.12), target=(-100, 900, 380), height=1500))
    out.append(save_view("4_top_windrow.png", (0.0, 0.0, -1.0), target=(-150, 700, 0), up=(0.0, 1.0, 0.0),
                         height=3300, size_px=(1500, 1400)))
    remove(doc, SCENE)
    set_robot_visible(False, doc)
    out.append(save_view("5_tine_bars_bottom_run.png", (0.6, -1.0, 0.25), target=(-300, 960, 150), height=1100))
    out.append(save_view("6_drive_motor_castor.png", (-0.8, -1.0, -0.5), target=(450, 1200, 330), height=800))
    out.append(save_view("7_mount_parallelogram.png", (-1.0, 0.6, -0.45), target=(0, 600, 470), height=800))
    set_robot_visible(True, doc)
    set_pose(P.lift_travel, 0.0, doc)
    add_grass_scene(doc)
    out.append(save_view("8_lifted_side.png", (1.0, 0.0, 0.0), target=(0, 550, 450), height=1900))
    remove(doc, SCENE)
    set_pose(doc=doc)
    add_nursery_scene(doc)
    out.append(save_view("9_nursery_bed_iso.png", (1.0, -1.1, -0.7), target=(0, 800, 250), height=2600))
    App.closeDocument(doc.Name)
    build()
    return out
