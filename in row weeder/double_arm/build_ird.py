"""Model of the in-row weeder with double arms (2 rows of broccoli, 2 arms per row) under the Bruut OpenAgbot.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_ird
    build_ird.build()                               # saves FCStd and STEP (units down, knives in)
    build_ird.set_pose(lift=0, right=2.6, left=(23.4, 2.6))  # arm angles in degrees (23.4 = in, 2.6 = out);
                                                    # a number for both arms of a row or (outer, inner)
    build_ird.check_interference()                  # overlap in the current pose (must be empty)
    build_ird.check_fit()                           # overlap over lift and swing of both units (must be empty)
    build_ird.clearance()                           # distances to the tyres, the steering sweep and the robot frame
    build_ird.mass_properties()
    build_ird.render_all()                          # all images in previews/
"""
import math
import os
import random
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ird_params as P
import ird_calc as C
import ird_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "In_Row_Double_Arm_Weeder"
SAVE_BASE = os.path.join(FOLDER, "In_Row_Double_Arm_Weeder")
ROOT = "In_row_weeder"

COLOR = {
    "frame": (0.10, 0.45, 0.30),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "spring": (0.20, 0.20, 0.22),
    "knife": (0.62, 0.64, 0.68),
    "motor": (0.15, 0.15, 0.17),
    "gearbox": (0.55, 0.57, 0.60),
    "bearing": (0.30, 0.32, 0.36),
    "rubber": (0.10, 0.10, 0.10),
    "rim": (0.85, 0.75, 0.15),
    "actuator": (0.30, 0.31, 0.33),
    "box": (0.55, 0.57, 0.60),
    "camera": (0.12, 0.12, 0.13),
    "glass": (0.25, 0.45, 0.75),
    "led": (0.95, 0.95, 0.85),
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
# Pose: lift of both units (parallelogram) and the arm angle of each finger
# ---------------------------------------------------------------------
SIDE_TAG = {1: "outer", -1: "inner"}
MOVING = ("Unit_right", "Unit_left", "Upper_links_right", "Upper_links_left", "Lower_links_right", "Lower_links_left",
          "Act_right", "Act_left", "Act_right_rod", "Act_left_rod") + tuple(
    "Arm_%s_%s" % (r, SIDE_TAG[s]) for r in ("right", "left") for s in P.SIDES)


def _pair(th):
    """Arm angles of a row: a number for both arms or (outer, inner)."""
    if isinstance(th, (tuple, list)):
        return {1: float(th[0]), -1: float(th[1])}
    return {1: float(th), -1: float(th)}


def _act_dir0():
    d = V(0, P.act_end[1] - P.act_base[1], P.act_end[2] - P.act_base[2])
    d.normalize()
    return d


def pose_placements(lift=0.0, right=P.theta_in, left=P.theta_in):
    if not -1e-6 <= lift <= P.lift_travel + 1e-6:
        raise ValueError("lift %.1f outside 0 .. %.1f" % (lift, P.lift_travel))
    right, left = _pair(right), _pair(left)
    for pr in (right, left):
        for th in pr.values():
            if not P.theta_park - 1e-6 <= th <= P.theta_in + 1e-6:
                raise ValueError("arm angle %.1f outside %.1f .. %.1f" % (th, P.theta_park, P.theta_in))
    dy, dz, beta = C.head_offset(lift)
    out = {}
    d0 = _act_dir0()
    d_ang = C.act_angle(lift) - C.act_angle(0.0)
    d_len = C.act_length(lift) - C.act_length(0.0)
    for s, tag, th in ((1, "right", right), (-1, "left", left)):
        out["Unit_" + tag] = App.Placement(V(0, dy, dz), App.Rotation())
        for side in P.SIDES:
            x, y = G.shaft_xy(side)
            out["Arm_%s_%s" % (tag, SIDE_TAG[side])] = App.Placement(
                V(0, 0, 0), App.Rotation(V(0, 0, 1), -s * side * (th[side] - P.theta_in)), V(s * x, y, 0))
        out["Upper_links_" + tag] = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -beta),
                                                  V(0, P.pin_y_front, P.pin_z[0]))
        out["Lower_links_" + tag] = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -beta),
                                                  V(0, P.pin_y_front, P.pin_z[1]))
        out["Act_" + tag] = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), d_ang),
                                          V(0, P.act_base[1], P.act_base[2]))
        out["Act_%s_rod" % tag] = App.Placement(d0 * d_len, App.Rotation())
    return out


def set_pose(lift=0.0, right=P.theta_in, left=P.theta_in, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(lift, right, left).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_frame(doc, parent):
    grp = new_part(doc, parent, "Frame", "frame_rails_toolbar")
    add_shape(doc, grp, "frame_weldment", "rails_40x40x3_toolbar_50x50x4_brackets_lugs", G.frame_weldment(), "frame")
    add_shape(doc, grp, "frame_bolts", "frame_bolts_8xM10", G.frame_bolts(), "zinc")
    add_shape(doc, grp, "front_pins", "parallelogram_front_pins_D16", G.both_sides(G.front_pins_right()), "steel")
    return grp


def build_unit(doc, parent, s, pl):
    tag = "right" if s > 0 else "left"

    def side(shape):
        return shape if s > 0 else G.mirror_x(shape)
    grp = new_part(doc, parent, "Row_unit_" + tag, "row_unit_%s" % tag)
    for key, fn in (("Upper_links", G.upper_links_right), ("Lower_links", G.lower_links_right)):
        lk = new_part(doc, grp, "%s_%s" % (key, tag), "%s_%s" % (key.lower(), tag), pl["%s_%s" % (key, tag)])
        add_shape(doc, lk, "%s_bars_%s" % (key.lower(), tag), "%s_flat_30x8_%s" % (key.lower(), tag), side(fn()),
                  "frame")
    u = new_part(doc, grp, "Unit_" + tag, "unit_head_%s" % tag, pl["Unit_" + tag])
    add_shape(doc, u, "head_" + tag, "unit_head_deck_cheeks_gauge_fork_8mm_" + tag, side(G.head_weldment_right()),
              "frame")
    add_shape(doc, u, "rear_pins_" + tag, "parallelogram_rear_pins_D16_" + tag, side(G.rear_pins_right()), "steel")
    add_shape(doc, u, "gauge_tyre_" + tag, "gauge_wheel_200x60_" + tag, side(G.gauge_wheel_right()), "rubber")
    add_shape(doc, u, "gauge_axle_" + tag, "gauge_wheel_axle_M12_" + tag, side(G.gauge_axle_right()), "zinc")
    for sd in P.SIDES:
        t2 = "%s_%s" % (tag, SIDE_TAG[sd])
        add_shape(doc, u, "bearing_" + t2, "flange_bearing_UCFL204_" + t2, side(G.bearing_right(sd)), "bearing")
        add_shape(doc, u, "gearbox_" + t2, "planetary_gearbox_10to1_" + t2, side(G.gearbox_right(sd)), "gearbox")
        add_shape(doc, u, "motor_" + t2, "stepper_NEMA23_closed_loop_" + t2, side(G.motor_right(sd)), "motor")
        a = new_part(doc, u, "Arm_" + t2, "swing_arm_" + t2, pl["Arm_" + t2])
        add_shape(doc, a, "shaft_" + t2, "shaft_D20_" + t2, side(G.shaft_right(sd)), "steel")
        add_shape(doc, a, "arm_" + t2, "arm_flat_40x12_clamp_hub_" + t2, side(G.arm_right(sd)), "frame")
        add_shape(doc, a, "finger_" + t2, "finger_spring_shank_knife_50x35_" + t2, side(G.finger_right(sd)), "knife")
    ac = new_part(doc, grp, "Act_" + tag, "lift_actuator_%s_500N" % tag, pl["Act_" + tag])
    add_shape(doc, ac, "act_body_" + tag, "lift_actuator_body_24V_" + tag, side(G.act_body_right()), "actuator")
    r = new_part(doc, ac, "Act_%s_rod" % tag, "lift_actuator_rod_%s" % tag, pl["Act_%s_rod" % tag])
    add_shape(doc, r, "act_rod_" + tag, "lift_actuator_rod_slotted_clevis_" + tag, side(G.act_rod_right()), "steel")
    return grp


def build_camera(doc, parent):
    grp = new_part(doc, parent, "Camera", "camera_under_front_beam")
    add_shape(doc, grp, "cam_plate", "camera_plate_6mm_lugs", G.cam_plate(), "frame")
    add_shape(doc, grp, "cam_bolts", "camera_plate_bolts_2xM10", G.cam_bolts(), "zinc")
    add_shape(doc, grp, "camera", "camera_2MP_global_shutter_6mm", G.camera(), "camera")
    add_shape(doc, grp, "camera_glass", "camera_lens_window", G.camera_glass(), "glass")
    add_shape(doc, grp, "led_bars", "led_bars_2x", G.led_bars(), "led")
    return grp


def build_control(doc, parent):
    grp = new_part(doc, parent, "Control", "control_box")
    add_shape(doc, grp, "box_base", "control_box_base_plate_4mm", G.box_base(), "frame")
    add_shape(doc, grp, "box_bolts", "control_box_bolts_4xM10", G.box_bolts(), "zinc")
    add_shape(doc, grp, "control_box", "control_box_IP66_computer_stepper_drivers", G.control_box(), "box")
    return grp


def build_into(doc, parent=None, lift=0.0, right=P.theta_in, left=P.theta_in):
    """Put the weeder in a document, in robot coordinates (also used by animate_ird.py)."""
    pl = pose_placements(lift, right, left)
    root = new_part(doc, parent, ROOT, "in_row_weeder_double_arms_2_rows")
    build_frame(doc, root)
    build_unit(doc, root, 1, pl)
    build_unit(doc, root, -1, pl)
    build_camera(doc, root)
    build_control(doc, root)
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


def build(lift=0.0, right=P.theta_in, left=P.theta_in, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "In-row weeder, double arms"
    doc.Comment = ("Generated by build_ird.py from ird_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Pose with build_ird.set_pose(lift, right, left).")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, lift, right, left)
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
    raise RuntimeError("no in-row weeder (double arms) document open")


def weeder_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in weeder_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in weeder_objects(doc):
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


# pins sit in their holes (0.5 mm play) and the pin heads touch the plates: the pin / plate pairs are excluded
TOUCH = (("front_pins", "frame_weldment"), ("front_pins", "upper_links_bars"), ("front_pins", "lower_links_bars"),
         ("rear_pins", "head"), ("rear_pins", "upper_links_bars"), ("rear_pins", "lower_links_bars"),
         ("shaft", "bearing"), ("shaft", "gearbox"), ("shaft", "head"), ("act_body", "frame_weldment"),
         ("act_rod", "head"), ("gauge_axle", "head"), ("gauge_axle", "gauge_tyre"), ("bearing", "head"),
         ("frame_bolts", "frame_weldment"), ("cam_bolts", "cam_plate"), ("box_bolts", "box_base"),
         ("camera", "cam_plate"))


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
    """Volume overlap (mm3) in the current pose: weeder parts among themselves and against the robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in weeder_objects(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def fit_poses():
    th = [P.theta_in, (P.theta_in + P.theta_out) / 2.0, P.theta_out, P.theta_park]
    poses = [(0.0, t, t) for t in th]
    poses += [(0.0, (P.theta_in, P.theta_out), (P.theta_out, P.theta_in)),
              (P.lift_travel / 2.0, P.theta_park, P.theta_park), (P.lift_travel, P.theta_park, P.theta_park),
              (P.lift_travel, P.theta_in, P.theta_out)]
    return poses


def check_fit(doc=None, poses=None, tol=1.0):
    """Interference over lift and swing (all parts against each other and the robot). Must be empty."""
    doc = active_doc(doc)
    out = {}
    for pose in poses or fit_poses():
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
    """Smallest distances (mm): weeder to the front wheel units at full steering lock (lifted and down), fingers and
    gauge wheels to the rear tyres, motors to the upper beams (lifted), camera to the front units."""
    doc = active_doc(doc)
    if doc.getObject("Robot") is None:
        return {}
    out = {}
    front = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
    rear = [o for o in robot_objects(doc) if o.Name.startswith(("RL_", "RR_"))]
    mine = weeder_objects(doc)
    for lift in (0.0, P.lift_travel):
        set_pose(lift, P.theta_park, P.theta_park, doc)
        for steer in (-P.robot_steer_max, P.robot_steer_max):
            set_steering(steer, steer, doc)
            out["weeder_to_front_units_lift_%d_steer_%+d" % (lift, steer)] = _min_dist(mine, front)
        set_steering(0.0, 0.0, doc)
    set_pose(doc=doc)
    fingers = [o for o in weeder_objects(doc) if o.Name.startswith(("finger_", "gauge_tyre_"))]
    for th in (P.theta_in, P.theta_out, P.theta_park):
        set_pose(0.0, th, th, doc)
        out["fingers_gauge_to_rear_units_theta_%.1f" % th] = _min_dist(fingers, rear)
    set_pose(P.lift_travel, P.theta_park, P.theta_park, doc)
    beams = [o for o in robot_objects(doc) if o.Name.startswith(("upper_beam", "lower_beam"))]
    out["motors_to_beams_lifted"] = _min_dist([o for o in weeder_objects(doc) if o.Name.startswith("motor_")], beams)
    set_pose(doc=doc)
    out["camera_to_front_units"] = _min_dist([doc.getObject(n) for n in ("camera", "cam_plate", "led_bars")], front)
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
MASS_FIXED = {"motor": P.motor_kg, "gearbox": P.gear_kg, "bearing": 0.65, "gauge_tyre": 1.1, "camera_glass": 0.01,
              "camera": 0.35, "led_bars": 0.4, "control_box": 4.5, "act_body": P.act_kg - 0.25, "act_rod": 0.25}
DENSITY = (("arm_", 2.7e-6),)       # arm and clamp hub aluminium 6082
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


def arm_inertia(doc=None):
    """Inertia of the right outer arm (shaft, arm, finger) about the shaft axis (kg m2), from the solids."""
    doc = active_doc(doc)
    axis_x, axis_y = G.shaft_xy(1)
    J, m = 0.0, 0.0
    for n in ("shaft_right_outer", "arm_right_outer", "finger_right_outer"):
        s = global_shape(doc.getObject(n))
        rho = 2.7e-6 if n.startswith("arm_") else STEEL
        for sol in s.Solids:
            mi = sol.Volume * rho
            I = sol.MatrixOfInertia          # about the centre of mass, per unit density (mm^5)
            c = sol.CenterOfMass
            Izz = I.A33 * rho + mi * ((c.x - axis_x) ** 2 + (c.y - axis_y) ** 2)
            J += Izz * 1e-6
            m += mi
    return round(J, 4), round(m, 2)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) in the current pose."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(weeder_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for name in ("Frame", "Row_unit_right", "Arm_right_outer", "Camera", "Control"):
        ms, cs = _sum(objs_of(name))
        out[name.lower() + "_kg"] = round(ms, 2)
    out["arm_J_kgm2"], out["arm_kg_solid"] = arm_inertia(doc)
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in weeder_objects(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin)), (
        round(bb.XMax), round(bb.YMax), round(bb.ZMax))


# ---------------------------------------------------------------------
# Scene for the images: soil, two broccoli rows, weeds
# ---------------------------------------------------------------------
SCENE = ("render_soil", "render_crop", "render_weeds", "render_footprint")


def crop_positions(y0=-1400.0, y1=1700.0, seed=4):
    rnd = random.Random(seed)
    out = []
    for x in P.row_x:
        y = y0 + rnd.uniform(0, P.plant_spacing)
        while y < y1:
            out.append((x + rnd.uniform(-8, 8), y + rnd.uniform(-P.plant_scatter, P.plant_scatter),
                        rnd.uniform(*P.canopy_d), rnd.uniform(190.0, 260.0), rnd.randint(0, 999)))
            y += P.plant_spacing
    return out


def add_scene(doc, y=(-1600.0, 1900.0), x=(-900.0, 900.0), weeds=True, footprint=False):
    soil = doc.addObject("Part::Feature", "render_soil")
    soil.Shape = G.box_span(x, y, (-40.0, 0.0))
    soil.ViewObject.ShapeColor = (0.45, 0.33, 0.22)
    crop = doc.addObject("Part::Feature", "render_crop")
    crop.Shape = Part.makeCompound([G.broccoli(px, py, d, h, s) for (px, py, d, h, s) in crop_positions(y[0] + 200,
                                                                                                         y[1] - 200)])
    crop.ViewObject.ShapeColor = (0.25, 0.50, 0.30)
    if weeds:
        rnd = random.Random(8)
        pts = [(rnd.uniform(x[0] + 50, x[1] - 50), rnd.uniform(y[0] + 50, y[1] - 50)) for _ in range(160)]
        pts += [(rx + rnd.gauss(0, 30), rnd.uniform(y[0] + 50, y[1] - 50)) for rx in P.row_x for _ in range(40)]
        w = doc.addObject("Part::Feature", "render_weeds")
        w.Shape = Part.makeCompound([G.weed(px, py, rnd.uniform(0.7, 1.3)) for (px, py) in pts])
        w.ViewObject.ShapeColor = (0.45, 0.75, 0.25)
    if footprint:
        fp = doc.addObject("Part::Feature", "render_footprint")
        fp.Shape = G.ground_polygon(C.footprint(), z=1.0)
        fp.ViewObject.ShapeColor = (0.98, 0.82, 0.20)
        fp.ViewObject.Transparency = 50
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


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


TOP_KEEP = ("shaft_", "arm_", "finger_", "gauge_")


def render_top_detail(doc):
    """From above, only the arms, knives and gauge wheels: right knives out on both sides of a plant (safe circle),
    left knives in the row band. The soil is see-through so that the knives (20 mm deep) show."""
    set_pose(0.0, P.theta_out, P.theta_in, doc)
    hidden = [o for o in weeder_objects(doc) if not o.Name.startswith(TOP_KEEP)]
    for o in hidden:
        o.ViewObject.Visibility = False
    yk = (C.finger_uv(P.theta_out, 1)[1] + C.finger_uv(P.theta_out, -1)[1]) / 2.0     # between the two knives
    soil = doc.addObject("Part::Feature", "render_soil")
    soil.Shape = G.box_span((-450.0, 450.0), (-500.0, 250.0), (-40.0, 0.0))
    soil.ViewObject.ShapeColor = (0.45, 0.33, 0.22)
    soil.ViewObject.Transparency = 55
    crop = doc.addObject("Part::Feature", "render_crop")
    crop.Shape = Part.makeCompound([G.broccoli(P.row_x[0], yk - 260.0, 200.0, 220.0, 3),
                                    G.broccoli(P.row_x[1], yk, 200.0, 220.0, 5)])
    crop.ViewObject.ShapeColor = (0.25, 0.50, 0.30)
    crop.ViewObject.Transparency = 35
    ring = doc.addObject("Part::Feature", "render_footprint")
    ring.Shape = Part.makeCylinder(P.safe_r + 4.0, 1.0, V(P.row_x[1], yk, 1.0)).cut(
        Part.makeCylinder(P.safe_r, 1.0, V(P.row_x[1], yk, 1.0)))
    ring.ViewObject.ShapeColor = (0.98, 0.55, 0.10)
    doc.recompute()
    path = save_view("6_knives_from_above_out_and_in.png", (0.0, 0.0, -1.0), target=(0, -60, 0), up=(0.0, 1.0, 0.0),
                     height=820, size_px=(1500, 1100))
    remove(doc, SCENE)
    for o in hidden:
        o.ViewObject.Visibility = True
    set_pose(doc=doc)
    return path


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    set_pose(0.0, P.theta_out, P.theta_in, doc)
    add_scene(doc)
    out.append(save_view("1_work_iso_on_robot.png", (1.0, 1.3, -0.8), target=(0, -50, 300), height=2300))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, 0, 450), height=1700))
    out.append(save_view("3_rear_on_robot.png", (0.0, 1.0, -0.15), target=(0, 0, 400), height=1400))
    remove(doc, SCENE)
    add_scene(doc, weeds=False, footprint=True)
    out.append(save_view("4_top_camera_footprint.png", (0.0, 0.0, -1.0), target=(0, 250, 0), up=(0.0, 1.0, 0.0),
                         height=2600, size_px=(1300, 1500)))
    remove(doc, SCENE)
    set_robot_visible(False, doc)
    add_scene(doc, y=(-700.0, 500.0), x=(-500.0, 500.0), weeds=True)
    set_pose(0.0, P.theta_in, P.theta_in, doc)
    out.append(save_view("5_unit_detail_knives_in.png", (-0.9, 1.0, -0.6), target=(190, -100, 220), height=950))
    remove(doc, SCENE)
    out.append(render_top_detail(doc))
    set_pose(P.lift_travel, P.theta_park, P.theta_park, doc)
    set_robot_visible(True, doc)
    add_scene(doc, weeds=False)
    out.append(save_view("7_lifted_headland_side.png", (1.0, 0.0, 0.0), target=(0, 0, 400), height=1500))
    remove(doc, SCENE)
    set_pose(doc=doc)
    out.append(save_view("8_camera_led_front.png", (-0.6, -1.0, 0.35), target=(0, 420, 560), height=650))
    App.closeDocument(doc.Name)
    build()
    return out
