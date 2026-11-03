"""Model of the cauliflower root-crown applicator on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_cfa
    build_cfa.build()                              # saves FCStd and STEP (row units at working height)
    build_cfa.set_float(left=0, right=40)          # row unit float in mm (+ up), parallelogram follows
    build_cfa.check_interference()                 # overlap in the current pose (must be empty)
    build_cfa.check_poses()                        # overlap over the float range of both row units (must be empty)
    build_cfa.clearance()                          # distances to the tyres, the steering sweep and the robot frame
    build_cfa.mass_properties()
    build_cfa.render_all()                         # all images in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cfa_params as P
import cfa_calc as C
import cfa_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Cauliflower_Applicator"
SAVE_BASE = os.path.join(FOLDER, "Cauliflower_Applicator")
ROOT = "Cauliflower_applicator"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "galv": (0.70, 0.72, 0.74),
    "stainless": (0.86, 0.87, 0.88),
    "tank": (0.93, 0.93, 0.90),
    "rubber": (0.10, 0.10, 0.10),
    "hose": (0.15, 0.25, 0.55),
    "pump": (0.15, 0.15, 0.17),
    "plastic": (0.10, 0.10, 0.10),
    "uhmw": (0.95, 0.95, 0.92),
    "brass": (0.80, 0.65, 0.25),
    "coil": (0.20, 0.20, 0.22),
    "box": (0.55, 0.57, 0.60),
    "red": (0.85, 0.15, 0.10),
    "yellow": (0.95, 0.80, 0.10),
    "sensor": (0.20, 0.45, 0.80),
}

ROWS = (("left", "l", P.rows_x[0]), ("right", "r", P.rows_x[1]))


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
# Pose: float of each row unit (mm, + up). The arms rotate about their bracket pins, the unit translates.
# ---------------------------------------------------------------------
def pose_placements(left=0.0, right=0.0):
    out = {}
    for (tag, t, rx), dz in zip(ROWS, (left, right)):
        if not P.float_range[0] - 1e-6 <= dz <= P.float_up_stop + 1e-6:
            raise ValueError("%s float %.1f outside %.0f .. %.0f" % (tag, dz, P.float_range[0], P.float_up_stop))
        ang, dy = C.float_pose(dz)
        for name, z in (("Upper_arm_", P.pl_z[1]), ("Lower_arm_", P.pl_z[0])):
            out[name + tag] = App.Placement(V(0, P.pl_y_bracket, z), App.Rotation(V(1, 0, 0), -ang))
        out["Unit_" + tag] = App.Placement(V(0, dy, dz), App.Rotation())
    return out


MOVING = tuple(n + tag for tag, _, _ in ROWS for n in ("Upper_arm_", "Lower_arm_", "Unit_"))


def set_float(left=0.0, right=0.0, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(left, right).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_tank(doc, parent):
    grp = new_part(doc, parent, "Tank", "tank_%dl_on_cradle" % P.tank_nominal)
    add_shape(doc, grp, "cradle_tubes", "cradle_tubes_40x40x3", G.cradle_tubes(), "galv")
    add_shape(doc, grp, "cradle_pads", "cradle_rubber_strips_5mm", G.cradle_pads(), "rubber")
    add_shape(doc, grp, "cradle_bolts", "cradle_bolts_4xM10", G.cradle_bolts(), "zinc")
    add_shape(doc, grp, "straps", "tank_straps_50x3", G.straps(), "galv")
    add_shape(doc, grp, "tank_shell", "tank_PE_%dl_wall_5" % P.tank_nominal, G.tank_shell(), "tank")
    add_shape(doc, grp, "tank_fittings", "fill_cap_vent_wall_fittings", G.tank_fittings(), "plastic")
    add_shape(doc, grp, "level_sensor", "tank_level_switch", G.level_sensor(), "plastic")
    return grp


def build_plumbing(doc, parent):
    grp = new_part(doc, parent, "Plumbing", "pump_plate_filter_pump_regulator_accumulator_box")
    add_shape(doc, grp, "pump_plate", "pump_plate_6mm_on_rear_beams", G.pump_plate(), "frame")
    add_shape(doc, grp, "plate_bolts", "pump_plate_bolts_4xM10", G.plate_bolts(), "zinc")
    add_shape(doc, grp, "pump", "pump_diaphragm_24V_6lpm", G.pump(), "pump")
    add_shape(doc, grp, "pump_foot", "pump_rubber_foot", G.pump_foot(), "rubber")
    add_shape(doc, grp, "filter_bowl", "suction_filter_80_mesh", G.filter_bowl(), "plastic")
    add_shape(doc, grp, "regulator", "pressure_regulator_bypass_sensor", G.regulator(), "red")
    add_shape(doc, grp, "accumulator", "pressure_accumulator_0_5l", G.accumulator(), "yellow")
    add_shape(doc, grp, "control_box", "control_box_IP66_controller_valve_driver", G.control_box(), "box")
    add_shape(doc, grp, "hose_suction", "hose_suction_tank_filter_pump", G.suction_hose(), "hose")
    add_shape(doc, grp, "hose_pump", "hose_pump_to_regulator", G.pump_hose(), "hose")
    add_shape(doc, grp, "hose_return", "hose_bypass_return_to_tank", G.return_hose(), "hose")
    add_shape(doc, grp, "hose_main", "hose_main_feed_to_manifold", G.main_hose(), "hose")
    return grp


def build_toolbar(doc, parent):
    grp = new_part(doc, parent, "Toolbar", "toolbar_50x50_under_upper_beams")
    add_shape(doc, grp, "toolbar", "toolbar_tube_50x50x3", G.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_bolts", "toolbar_bolts_2xM10_through_upper_beams", G.toolbar_bolts(), "zinc")
    add_shape(doc, grp, "manifold", "manifold_2_outlets", G.manifold(), "red")
    add_shape(doc, grp, "sensor_brackets", "crown_sensor_brackets_6mm", G.sensor_brackets(), "frame")
    add_shape(doc, grp, "sensors", "crown_sensors_M18_ToF", G.sensors(), "sensor")
    add_shape(doc, grp, "hose_feed", "hoses_manifold_to_rows", G.feed_hoses(), "hose")
    return grp


def build_row(doc, parent, tag, t, rx, pl):
    grp = new_part(doc, parent, "Row_" + tag, "row_unit_%s_x%+d" % (tag, rx))
    add_shape(doc, grp, "bracket_plates_" + t, "parallelogram_bracket_plates_8mm_" + tag, G.bracket_plates(rx), "frame")
    add_shape(doc, grp, "bracket_pins_" + t, "bracket_pins_D12_" + tag, G.bracket_pins(rx), "steel")
    for name, z, label in (("Upper_arm_", P.pl_z[1], "upper"), ("Lower_arm_", P.pl_z[0], "lower")):
        a = new_part(doc, grp, name + tag, "%s_arms_%s" % (label, tag), pl[name + tag])
        arm = G.arm(rx, z)
        arm.translate(V(0, -P.pl_y_bracket, -z))         # local: origin on the bracket pin
        add_shape(doc, a, "%s_arms_%s" % (label, t), "%s_arms_flat_30x8_%s" % (label, tag), arm, "frame")
    u = new_part(doc, grp, "Unit_" + tag, "floating_unit_%s" % tag, pl["Unit_" + tag])
    add_shape(doc, u, "head_plates_" + t, "head_plates_8mm_" + tag, G.head_plates(rx), "frame")
    add_shape(doc, u, "head_pins_" + t, "head_pins_D12_" + tag, G.head_pins(rx), "steel")
    add_shape(doc, u, "arch_" + t, "arch_tube_legs_leaf_lifters_" + tag, G.arch(rx), "frame")
    add_shape(doc, u, "skids_" + t, "skids_UHMW_40x15_" + tag, G.skids(rx), "uhmw")
    add_shape(doc, u, "valve_brackets_" + t, "valve_brackets_slotted_6mm_" + tag, G.valve_brackets(rx), "galv")
    add_shape(doc, u, "valves_" + t, "solenoid_valves_24V_2x_" + tag, G.valves(rx), "brass")
    add_shape(doc, u, "nozzles_" + t, "drop_tubes_and_nozzles_stainless_" + tag, G.nozzles(rx), "stainless")
    add_shape(doc, u, "shrouds_" + t, "splash_shrouds_" + tag, G.shrouds(rx), "plastic")
    add_shape(doc, u, "hose_unit_" + t, "hose_unit_to_valves_" + tag, G.unit_hose(rx), "hose")
    return grp


def build_into(doc, parent=None, left=0.0, right=0.0):
    """Put the applicator in a document, in robot coordinates."""
    pl = pose_placements(left, right)
    root = new_part(doc, parent, ROOT, "cauliflower_root_crown_applicator")
    build_tank(doc, root)
    build_plumbing(doc, root)
    build_toolbar(doc, root)
    for tag, t, rx in ROWS:
        build_row(doc, root, tag, t, rx, pl)
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


def build(left=0.0, right=0.0, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Cauliflower root-crown applicator"
    doc.Comment = ("Generated by build_cfa.py from cfa_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Float the row units with build_cfa.set_float(left, right).")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, left, right)
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
    raise RuntimeError("no cauliflower applicator document open")


def implement_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in implement_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in implement_objects(doc):
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


def _skip(a, b):
    """Hoses are flexible and meet each other at their joints."""
    return a.Name.startswith("hose") and b.Name.startswith("hose")


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        if _skip(oa, ob) or not sa.BoundBox.intersect(sb.BoundBox):
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
    """Volume overlap (mm3) in the current pose: implement parts among themselves and against the robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in implement_objects(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def _group_of(obj):
    parent = obj.getParentGeoFeatureGroup()
    while parent is not None:
        if parent.Name in MOVING:
            return parent.Name
        parent = parent.getParentGeoFeatureGroup()
    return "fixed"


def check_poses(doc=None, poses=None, tol=1.0):
    """Interference over the float range of both row units (pairs that move relative to each other). Must be empty."""
    doc = active_doc(doc)
    poses = poses or [(-60.0, 80.0), (-30.0, 30.0), (30.0, -30.0), (60.0, -60.0), (80.0, 80.0)]
    mine = implement_objects(doc)
    group = {o.Name: _group_of(o) for o in mine}
    moving = [o for o in mine if group[o.Name] != "fixed"]
    fixed = [(o, global_shape(o)) for o in mine if group[o.Name] == "fixed"]
    fixed += [(o, global_shape(o)) for o in robot_objects(doc)]
    out = {}
    for pose in poses:
        set_float(*pose, doc=doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if group[mv[i][0].Name] != group[mv[j][0].Name]]
        hits = _overlaps(pairs, tol)
        if hits:
            out[str(pose)] = hits
    set_float(doc=doc)
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
    """Smallest distances (mm): row units to the wheel units (float up and down), toolbar and tank to the front
    wheel units at full steering lock, pump plate to the rear wheel units."""
    doc = active_doc(doc)
    if doc.getObject("Robot") is None:
        return {}
    out = {}
    wheels = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_", "RL_", "RR_"))]
    rows = [o for o in implement_objects(doc) if o.getParentGeoFeatureGroup() is not None and
            _group_of(o) != "fixed"]
    for dz in (P.float_range[0], 0.0, P.float_up_stop):
        set_float(dz, dz, doc)
        out["row_units_to_wheel_units_float_%+d" % dz] = _min_dist(rows, wheels)
    set_float(doc=doc)
    front = [o for o in wheels if o.Name.startswith(("FL_", "FR_"))]
    fixed = [doc.getObject(n) for n in ("toolbar", "toolbar_bolts", "sensors", "sensor_brackets", "tank_shell",
                                        "cradle_tubes", "straps", "cradle_bolts", "bracket_plates_l", "bracket_plates_r")]
    for steer in (-P.robot_steer_max, P.robot_steer_max):
        set_steering(steer, steer, doc)
        out["toolbar_tank_to_front_units_steer_%+d" % steer] = _min_dist(fixed, front)
        out["row_units_to_front_units_steer_%+d" % steer] = _min_dist(rows, front)
    set_steering(0.0, 0.0, doc)
    rear = [o for o in wheels if o.Name.startswith(("RL_", "RR_"))]
    plumb = [o for o in doc.getObject("Plumbing").OutListRecursive if o.TypeId == "Part::Feature"]
    out["plumbing_to_rear_units"] = _min_dist(plumb, rear)
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
MASS_FIXED = {"pump": P.pump_kg, "filter_bowl": 0.4, "regulator": 0.7, "accumulator": 1.3, "control_box": 3.0,
              "level_sensor": 0.2, "tank_fittings": 0.4, "manifold": 0.4, "sensors": 0.3,
              "valves_": 2 * P.kg_valve}
DENSITY = (("tank_shell", 0.95e-6), ("cradle_pads", 1.2e-6), ("skids", 0.94e-6), ("shrouds", 1.2e-6),
           ("hose_", 1.3e-6), ("pump_foot", 1.2e-6))
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
    """Mass (kg) and centre of gravity (robot coordinates), tank empty."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(implement_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for name in ("Tank", "Plumbing", "Toolbar", "Row_right", "Unit_right"):
        ms, _ = _sum(objs_of(name))
        out[name.lower() + "_kg"] = round(ms, 2)
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in implement_objects(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin)), (
        round(bb.XMax), round(bb.YMax), round(bb.ZMax))


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
    tgt = V(*target) if target is not None else V(0, 0, 500)
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


GROUND = "render_floor"
CROP = "render_crop"
SPOTS = "render_dose_spots"


def plant_ys(n_back=2, n_front=2):
    """Plants placed so that one stem is exactly at the nozzles."""
    return [P.nz_y + k * P.plant_pitch for k in range(-n_back, n_front + 1)]


def add_field(doc, y=(-1300.0, 1300.0), x=(-1100.0, 1100.0), crop=True):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.55, 0.42, 0.30)
    if crop:
        plants = []
        i = 0
        for rx in P.rows_x + (-600.0, 600.0):
            for py in plant_ys():
                plants.append(G.cauliflower(rx, py, seed=i))
                i += 1
        c = doc.addObject("Part::Feature", CROP)
        c.Shape = Part.makeCompound(plants)
        c.ViewObject.ShapeColor = (0.30, 0.55, 0.30)
        c.ViewObject.LineColor = (0.18, 0.38, 0.18)
        land = G.landing_dx()
        spots = [G.dose_spot(rx + s * land, py) for rx in P.rows_x for s in (-1, 1) for py in plant_ys()[:3]]
        sp = doc.addObject("Part::Feature", SPOTS)
        sp.Shape = Part.makeCompound(spots)
        sp.ViewObject.ShapeColor = (0.15, 0.35, 0.85)
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
    add_field(doc)
    out.append(save_view("1_iso_on_robot_in_crop.png", (-1.0, -1.25, -0.8), target=(0, 0, 450), height=2300))
    out.append(save_view("2_rear_on_robot.png", (0.0, 1.0, -0.08), target=(0, 0, 500), height=1500))
    set_robot_visible(False, doc)
    remove(doc, [CROP])
    out.append(save_view("3_side_without_robot.png", (1.0, 0.0, 0.0), target=(0, 0, 500), height=1300))
    set_robot_visible(True, doc)
    remove(doc, [GROUND, SPOTS])
    out.append(save_view("4_iso_front_on_robot.png", (1.0, -1.2, -0.7), target=(0, 0, 500), height=2100))
    set_robot_visible(False, doc)
    set_visible(doc, ["Row_left"], False)
    add_field(doc, crop=False)
    out.append(save_view("5_row_unit_detail.png", (-0.9, 1.0, -0.55), target=(200, 60, 280), height=850))
    out.append(save_view("6_nozzles_shroud_detail.png", (-0.35, 1.0, -0.25), target=(200, -46, 120), height=380))
    set_visible(doc, ["Row_left"], True)
    set_float(-60.0, 60.0, doc)
    out.append(save_view("7_float_left_down_right_up.png", (0.0, 1.0, -0.05), target=(0, 0, 330), height=1000))
    set_float(doc=doc)
    remove(doc, [GROUND])
    out.append(save_view("8_pump_plate.png", (0.55, 1.0, -0.6), target=(0, -480, 730), height=750))
    App.closeDocument(doc.Name)
    build()
    return out
