"""Model of the air-assisted orchard sprayer on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_oas
    build_oas.build()                      # saves FCStd and STEP
    build_oas.check_interference()         # overlap (must be empty)
    build_oas.check_steering()             # overlap with the front wheel units at +-30 degrees (must be empty)
    build_oas.check_holes()                # every arm bolt in a real lower-beam hole
    build_oas.mass_properties()
    build_oas.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import oas_params as P
import oas_parts as G
import ssp_parts as S
import ssp_params as SP

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Orchard_Air_Sprayer"
SAVE_BASE = os.path.join(FOLDER, "Orchard_Air_Sprayer")
ROOT = "Orchard_air_sprayer"

COLOR = {"frame": (0.93, 0.42, 0.08), "zinc": (0.82, 0.84, 0.87), "galv": (0.70, 0.72, 0.74),
         "tank": (0.92, 0.92, 0.88), "plastic": (0.15, 0.15, 0.17), "rubber": (0.08, 0.08, 0.08),
         "pump": (0.20, 0.35, 0.60), "red": (0.80, 0.10, 0.08), "hose": (0.10, 0.10, 0.10), "box": (0.55, 0.57, 0.60),
         "shroud": (0.20, 0.45, 0.25), "motor": (0.25, 0.25, 0.28), "rotor": (0.95, 0.80, 0.10),
         "nozzle": (0.95, 0.55, 0.10), "stainless": (0.86, 0.87, 0.88), "lidar": (0.10, 0.10, 0.12),
         "valve": (0.20, 0.35, 0.80), "liquid": (0.40, 0.65, 0.90), "spray": (0.75, 0.88, 0.98)}


def new_part(doc, parent, name, label):
    part = doc.addObject("App::Part", name)
    part.Label = label
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


def build_into(doc, parent=None):
    root = new_part(doc, parent, ROOT, "orchard_air_sprayer_simple")
    tk = new_part(doc, root, "oas_Tank", "tank_from_spot_sprayer")
    add_shape(doc, tk, "oas_cradle_tubes", "cradle_tubes_40x40x3", S.cradle_tubes(), "galv")
    add_shape(doc, tk, "oas_cradle_pads", "cradle_rubber_strips_5mm", S.cradle_pads(), "rubber")
    add_shape(doc, tk, "oas_cradle_bolts", "cradle_bolts_4xM10", S.cradle_bolts(), "zinc")
    add_shape(doc, tk, "oas_straps", "tank_straps_50x3", S.straps(), "galv")
    add_shape(doc, tk, "oas_tank_shell", "tank_PE_%dl" % P.tank_l, S.tank_shell(), "tank")
    add_shape(doc, tk, "oas_tank_fittings", "fill_cap_vent_bulkhead_fittings", S.tank_fittings(), "plastic")
    add_shape(doc, tk, "oas_level_sensor", "tank_level_sensor_ultrasonic", S.level_sensor(), "plastic")
    pl = new_part(doc, root, "oas_Plumbing", "pump_filter_regulator_sections")
    add_shape(doc, pl, "oas_sub_plate", "sub_plate_10mm_under_rear_beams", S.sub_plate(), "frame")
    add_shape(doc, pl, "oas_sub_bolts", "sub_plate_bolts_M10", S.sub_bolts(), "zinc")
    add_shape(doc, pl, "oas_pump", "pump_diaphragm_24V_7bar", S.pump(), "pump")
    add_shape(doc, pl, "oas_pump_mounts", "pump_filter_regulator_brackets", S.pump_mounts(), "frame")
    add_shape(doc, pl, "oas_filter", "suction_filter_50_mesh", S.filter_bowl(), "plastic")
    add_shape(doc, pl, "oas_regulator", "pressure_regulator_bypass_sensor", S.regulator(), "red")
    add_shape(doc, pl, "oas_hose_suction", "hose_suction_tank_filter_pump", S.suction_hose(), "hose")
    add_shape(doc, pl, "oas_hose_return", "hose_bypass_return_to_tank", S.return_hose(), "hose")
    add_shape(doc, pl, "oas_hose_pressure", "hose_pressure_to_manifold", G.pressure_hose(), "hose")
    add_shape(doc, pl, "oas_manifold", "section_manifold_6_solenoid_valves", G.manifold(), "valve")
    add_shape(doc, pl, "oas_section_lines", "section_lines_D8_6x", G.pods(G.section_line_right), "hose")
    cb = new_part(doc, root, "oas_Control", "control_box_from_spot_sprayer")
    holes = [S.cyl_z(P.m10_hole, 600.0, 700.0, x, y) for (x, y) in G.ARM_BOLTS]
    add_shape(doc, cb, "oas_box_base", "control_box_base_plate_and_rails", S.box_base().cut(holes), "galv")
    add_shape(doc, cb, "oas_box_bolts", "control_box_bolts_4xM10", S.box_bolts(), "zinc")
    add_shape(doc, cb, "oas_control_box", "control_box_IP66_lidar_computer_valve_driver", S.control_box(), "box")
    tw = new_part(doc, root, "oas_Tower", "tower_arms_mast")
    add_shape(doc, tw, "oas_arms", "arms_40x60x3_under_lower_beams", G.arms(), "frame")
    add_shape(doc, tw, "oas_arm_bolts", "arm_bolts_4xM10", G.arm_bolts(), "zinc")
    add_shape(doc, tw, "oas_cross_beam", "cross_beam_60x60x4", G.cross_beam(), "frame")
    add_shape(doc, tw, "oas_mast", "mast_80x80x4_gussets", G.mast(), "frame")
    add_shape(doc, tw, "oas_pod_bars", "fan_pod_bars_8x40", G.pods(G.bars_right), "frame")
    fn = new_part(doc, root, "oas_Fans", "fan_pods_6x_O300")
    add_shape(doc, fn, "oas_shrouds", "fan_shrouds_O330", G.pods(G.shroud_right), "shroud")
    add_shape(doc, fn, "oas_guards", "intake_guards", G.pods(G.guard_right), "zinc")
    add_shape(doc, fn, "oas_motors", "fan_motors_48V_spokes", G.pods(G.motor_right), "motor")
    rt = new_part(doc, fn, "oas_Rotors", "fan_rotors")
    add_shape(doc, rt, "oas_rotors", "fan_rotors_6_blades", G.pods(G.rotor_right), "rotor")
    add_shape(doc, fn, "oas_ring_tabs", "nozzle_ring_tabs", G.pods(G.ring_tabs_right), "zinc")
    add_shape(doc, fn, "oas_nozzle_rings", "nozzle_rings_hollow_cone_2x", G.pods(G.nozzle_ring_right), "nozzle")
    ld = new_part(doc, root, "oas_Sensing", "canopy_lidars")
    add_shape(doc, ld, "oas_lidar_arm", "lidar_arm_40x40", G.lidar_arm(), "frame")
    add_shape(doc, ld, "oas_lidars", "lidar_2D_vertical_scan_2x", G.lidars(), "lidar")
    return root


def build_robot(doc):
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Orchard air sprayer simple"
    doc.Comment = ("Generated by build_oas.py from oas_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
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
    if DOC_NAME in App.listDocuments():
        return App.getDocument(DOC_NAME)
    raise RuntimeError("no document %s open" % DOC_NAME)


def objects_of(doc, name):
    g = doc.getObject(name)
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []


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


_J = [("cradle_bolts", "cradle_tubes"), ("cradle_pads", "cradle_tubes"), ("straps", "cradle_tubes"),
      ("straps", "tank_shell"), ("tank_shell", "cradle_pads"), ("tank_fittings", "tank_shell"),
      ("level_sensor", "tank_shell"), ("level_sensor", "tank_fittings"), ("sub_bolts", "sub_plate"),
      ("pump_mounts", "sub_plate"), ("pump_mounts", "pump"), ("pump_mounts", "filter"), ("pump_mounts", "regulator"),
      ("hose_suction", "filter"), ("hose_suction", "pump"), ("hose_suction", "tank_fittings"),
      ("hose_return", "regulator"), ("hose_return", "tank_fittings"), ("hose_pressure", "regulator"),
      ("hose_pressure", "manifold"), ("section_lines", "manifold"), ("section_lines", "nozzle_rings"),
      ("manifold", "mast"), ("manifold", "cross_beam"), ("box_bolts", "box_base"), ("control_box", "box_base"), ("sub_bolts", "box_base"),
      ("arm_bolts", "arms"), ("arm_bolts", "box_base"), ("cross_beam", "arms"), ("mast", "cross_beam"),
      ("pod_bars", "mast"), ("pod_bars", "shrouds"), ("guards", "shrouds"), ("motors", "shrouds"),
      ("rotors", "motors"), ("ring_tabs", "shrouds"), ("ring_tabs", "nozzle_rings"), ("lidar_arm", "mast"),
      ("lidars", "lidar_arm"), ("hose_suction", "sub_plate"), ("hose_return", "sub_plate"),
      ("hose_pressure", "pump_mounts")]
JOINTS = {("oas_" + a, "oas_" + b) for a, b in _J}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x in ("oas_cradle_bolts", "oas_cradle_pads") and y.startswith("upper_beam"):
            return True
        if x in ("oas_sub_bolts", "oas_box_bolts", "oas_arm_bolts", "oas_box_base", "oas_sub_plate", "oas_arms") \
                and y.startswith("lower_beam"):
            return True
    return False


def _overlaps(pairs, tol):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        if not sa.BoundBox.intersect(sb.BoundBox):
            continue
        vol = sa.common(sb).Volume
        if vol > tol:
            hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_steering(doc=None, tol=1.0):
    doc = active_doc(doc)
    out = {}
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    for st in (-P.robot_steer_max, P.robot_steer_max):
        for name in ("FL_steered", "FR_steered"):
            o = doc.getObject(name)
            if o is not None:
                o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), st))
        doc.recompute()
        front = [(o, global_shape(o)) for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
        hits = _overlaps([(a, b) for a in mine for b in front], tol)
        if hits:
            out["steer_%+d" % st] = hits
    for name in ("FL_steered", "FR_steered"):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement()
    doc.recompute()
    return out


def check_holes(doc=None):
    """Each arm bolt line (O9 rod) must pass through a hole: common() with the lower beams ~0."""
    doc = active_doc(doc)
    beams = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith("lower_beam")]
    bad = []
    for (x, y) in G.ARM_BOLTS:
        rod = Part.makeCylinder(4.5, 80.0, V(x, y, 600.0))
        v = sum(rod.common(b).Volume for b in beams)
        if v > 1.0:
            bad.append((x, y, round(v)))
    return bad


def clearance(doc=None):
    """Smallest distance from the tower (arms, mast, pods) to the rear tyres (cylinder envelope O430 x 100)."""
    doc = active_doc(doc)
    mine = Part.makeCompound([global_shape(o) for o in objects_of(doc, ROOT)
                              if o.Name in ("oas_arms", "oas_cross_beam", "oas_shrouds", "oas_section_lines",
                                            "oas_nozzle_rings", "oas_hose_pressure")])
    d = []
    for sx in (-1, 1):
        c = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, V(sx * P.robot_wheel_x - P.robot_tire_w / 2.0,
                                                                        -P.robot_axle_y, P.robot_axle_z), V(1, 0, 0))
        d.append(mine.distToShape(c)[0])
    return {"rear_tyre_min": round(min(d), 1)}


DENSITY = {"oas_tank_shell": 0.95e-6, "oas_tank_fittings": 1.1e-6, "oas_level_sensor": 1.1e-6, "oas_cradle_pads": 1.2e-6,
           "oas_hose_suction": 1.2e-6, "oas_hose_return": 1.2e-6, "oas_hose_pressure": 1.2e-6,
           "oas_section_lines": 1.2e-6, "oas_shrouds": 1.0e-6,
           "oas_nozzle_rings": 3.0e-6}
MASS_FIXED = {"oas_pump": SP.pump_kg, "oas_control_box": 6.0, "oas_motors": 6 * 2.2, "oas_rotors": 6 * 0.5,
              "oas_lidars": 2 * 0.9, "oas_manifold": 2.5, "oas_filter": 0.6, "oas_regulator": 0.8}


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity, empty tank."""
    doc = active_doc(doc)
    m, c = 0.0, V(0, 0, 0)
    parts = {}
    for o in objects_of(doc, ROOT):
        s = global_shape(o)
        mo = MASS_FIXED.get(o.Name, s.Volume * DENSITY.get(o.Name, P.steel))
        parts[o.Name] = round(mo, 1)
        m += mo
        c += s.BoundBox.Center * mo
    c = c * (1.0 / m)
    return {"total_kg": round(m, 1), "cg": (round(c.x), round(c.y), round(c.z)), "parts": parts}


def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.getDocument(DOC_NAME).ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, 0, 800)
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


def _spray_cones():
    """Render only: a cone of air and droplets from each pod outward."""
    out = []
    for s in (-1, 1):
        for z in P.pod_z:
            c = Part.makeCone(P.shroud_d[1] / 2.0, 330.0, 1100.0, V(P.pod_x[1] + 30.0, P.mast_y, z), V(1, 0, 0))
            if s < 0:
                c = c.mirror(V(0, 0, 0), V(1, 0, 0))
            out.append(c)
    return Part.makeCompound(out)


def _trees():
    """Render only: two tree rows (spindle trees) at +-row_spacing/2."""
    out = []
    xr = P.row_spacing * 1000.0 / 2.0
    for s in (-1, 1):
        for y in range(-2400, 2500, 900):
            out.append(Part.makeCylinder(45.0, 700.0, V(s * xr, y, 0)))
            out.append(Part.makeCone(480.0, 100.0, 1500.0, V(s * xr, y, 600.0)))
    return Part.makeCompound(out)


def render_all():
    import FreeCADGui as Gui
    out = []
    doc = build(save=False, show_robot=True, step=False)
    fl = doc.addObject("Part::Feature", "render_floor")
    fl.Shape = S.box_span((-2200.0, 2200.0), (-2600.0, 2600.0), (-40.0, 0.0))
    fl.ViewObject.ShapeColor = (0.45, 0.60, 0.35)
    tr = doc.addObject("Part::Feature", "render_trees")
    tr.Shape = _trees()
    tr.ViewObject.ShapeColor = (0.20, 0.50, 0.18)
    sp = doc.addObject("Part::Feature", "render_spray")
    sp.Shape = _spray_cones()
    sp.ViewObject.ShapeColor = COLOR["spray"]
    sp.ViewObject.Transparency = 60
    out.append(save_view("1_iso_spraying_alley.png", (-0.45, 1.0, -0.9), target=(0, -300, 900), height=4600))
    out.append(save_view("2_rear_spraying.png", (0.0, 1.0, 0.0), target=(0, 0, 1200), height=3000))
    tr.ViewObject.Visibility = False
    sp.ViewObject.Visibility = False
    out.append(save_view("3_side.png", (1.0, 0.0, 0.0), target=(0, -150, 1100), height=2600))
    out.append(save_view("4_tower_detail.png", (-0.8, 1.0, -0.5), target=(0, -800, 1200), height=1900))
    out.append(save_view("5_plumbing_below.png", (-0.6, 1.0, 0.7), target=(0, -650, 600), height=1300))
    App.closeDocument(doc.Name)
    build()
    return out
