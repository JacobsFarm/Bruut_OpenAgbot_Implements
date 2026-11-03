"""Model of the soil moisture sensor placer on the Bruut OpenAgbot (standard robot).

The bridges and the Z axis (mast, SBR20 rails, ball screw, NEMA23, carriage) are built from "soil sampler/simple"
(ssa_parts, imported); this file adds the gripper, the 6 sensors and the magazine star with its drive.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_smp
    build_smp.build()                          # saves FCStd and STEP (park, 6 sensors in the magazine)
    build_smp.set_pose("plant")                # one of POSES: park, pick, lift, turned, plant, released
    build_smp.check_interference()             # overlap in the current pose (must be empty)
    build_smp.check_poses()                    # overlap over the placing cycle (must be empty)
    build_smp.clearance()                      # star and sensors to the rear wheel units
    build_smp.mass_properties()
    build_smp.render_all()                     # all images in previews/
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import smp_params as P
import smp_parts as G
import ssa_parts as AG
import build_ssa as BA

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Soil_Moisture_Placer"
SAVE_BASE = os.path.join(FOLDER, "Soil_Moisture_Placer")
ROOT = "Soil_moisture_placer"

COLOR = dict(BA.COLOR)
COLOR.update({"sensor": (0.95, 0.75, 0.10), "gripper": (0.20, 0.22, 0.25), "star": (0.85, 0.30, 0.10)})

STEP_DEG = 360.0 / P.n_sensors
# placing cycle: (carriage bottom, star angle, sensor held, sensors left in the magazine incl. the index one)
POSES = {
    "park": (P.c_park, 0.0, False, 6),
    "pick": (P.c_pick, 0.0, True, 5),
    "lift": (P.c_lift, 0.0, True, 5),
    "turned": (P.c_lift, STEP_DEG / 2.0, True, 5),
    "plant": (P.c_plant, STEP_DEG / 2.0, True, 5),
    "released": (P.c_plant, STEP_DEG / 2.0, False, 5),
    "back_up": (P.c_park, STEP_DEG / 2.0, False, 5),
}


def new_part(doc, parent, name, label, placement=None):
    return BA.new_part(doc, parent, name, label, placement)


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


def carriage_placement(c):
    return App.Placement(V(0, 0, c - G.PARK_C), App.Rotation())


def star_placement(deg):
    return App.Placement(V(G.MX, G.MY, 0), App.Rotation(V(0, 0, 1), deg))     # star drawn round the origin


def build_into(doc, parent=None, pose="park"):
    c, deg, held, left = POSES[pose]
    root = new_part(doc, parent, ROOT, "soil_moisture_placer_simple")
    mount = new_part(doc, root, "Mount", "bridges_z_axis_from_soil_sampler")
    add_shape(doc, mount, "bridges", "bridges_40x40x3_L730", AG.bridges(), "frame")
    add_shape(doc, mount, "bridge_bolts", "bridge_bolts_M10", AG.bridge_bolts(), "zinc")
    add_shape(doc, mount, "mast", "mast_plate_10mm_bearing_motor_plate", AG.mast(), "alu")
    add_shape(doc, mount, "mast_bolts", "mast_bolts_M8", AG.mast_bolts(), "zinc")
    add_shape(doc, mount, "rails", "rails_SBR20", AG.rails(), "rail")
    add_shape(doc, mount, "screw", "ball_screw_SFU1605", AG.screw(), "steel")
    add_shape(doc, mount, "z_motor", "z_motor_NEMA23_coupling", AG.z_motor(), "motor")
    car = new_part(doc, root, "Carriage", "carriage_with_gripper_moves_in_z", carriage_placement(c))
    add_shape(doc, car, "carriage", "carriage_plate_blocks_nut_holder", AG.carriage(), "alu")
    add_shape(doc, car, "gripper", "gripper_24V_parallel", G.gripper(), "gripper")
    add_shape(doc, car, "jaws", "gripper_jaws_80", G.jaws(held), "steel")
    add_shape(doc, car, "sensor_held", "sensor_in_the_gripper", G.sensor_held(), "sensor", held)
    mag = new_part(doc, root, "Magazine", "magazine_drive_fixed")
    add_shape(doc, mag, "mag_plate", "cantilever_plate_10mm_on_rear_bridge", G.mag_plate(), "frame")
    add_shape(doc, mag, "plate_bolts", "plate_bolts_M8", G.plate_bolts(), "zinc")
    add_shape(doc, mag, "shaft", "magazine_shaft_D20", G.shaft(), "steel")
    add_shape(doc, mag, "mag_drive", "bearings_NEMA17_5_1", G.mag_drive(), "motor")
    star = new_part(doc, root, "Star", "magazine_star_turns", star_placement(deg))
    add_shape(doc, star, "star", "star_6_fork_arms_50x8", _local_star(), "star")
    add_shape(doc, star, "sensors", "soil_moisture_sensors_in_magazine", _local_sensors(left), "sensor")
    return root


def _local_star():
    s = G.star()
    s.translate(V(-G.MX, -G.MY, 0))
    return s


def _local_sensors(left):
    """Sensors in the forks; with fewer than 6 left, the index fork (at +y) and the next ones are empty."""
    skip = tuple(range(P.n_sensors - left))
    s = G.sensors_in_magazine(skip)
    s.translate(V(-G.MX, -G.MY, 0))
    return s


def set_pose(pose="park", doc=None):
    doc = active_doc(doc)
    c, deg, held, left = POSES[pose]
    doc.getObject("Carriage").Placement = carriage_placement(c)
    doc.getObject("Star").Placement = star_placement(deg)
    doc.getObject("jaws").Shape = G.jaws(held)
    doc.getObject("sensor_held").ViewObject.Visibility = held
    doc.getObject("sensors").Shape = _local_sensors(left)
    doc.recompute()


build_robot = BA.build_robot
global_shape = BA.global_shape


def build(save=True, show_robot=False, step=True, pose="park"):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Soil moisture placer simple"
    doc.Comment = ("Generated by build_smp.py from smp_params.py (Z axis from soil sampler/simple). Robot coordinates: "
                   "x = right, y = driving direction (front = +y), z = up, ground = z 0. build_smp.set_pose() runs the cycle.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, pose)
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
    raise RuntimeError("no document with %s open" % ROOT)


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


def _visible_mine(doc):
    return [o for o in objects_of(doc, ROOT) if o.ViewObject is None or o.ViewObject.Visibility]


def export_step(doc, path):
    import Import
    objs = []
    for o in _visible_mine(doc):
        f = doc.addObject("Part::Feature", "step_" + o.Name)
        f.Label = o.Label
        f.Shape = global_shape(o)
        objs.append(f)
    try:
        Import.export(objs, path)
    finally:
        for f in objs:
            doc.removeObject(f.Name)


JOINTS = set(BA.JOINTS) | {("gripper", "carriage"), ("jaws", "gripper"), ("jaws", "sensor_held"),
                           ("sensor_held", "gripper"), ("shaft", "star"), ("shaft", "mag_plate"),
                           ("shaft", "mag_drive"), ("plate_bolts", "mag_plate"), ("plate_bolts", "bridges"),
                           ("mag_plate", "bridges"), ("mag_drive", "mag_plate"), ("sensors", "star")}


def _joint(a, b):
    return BA._joint(a, b) or (a, b) in JOINTS or (b, a) in JOINTS


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in _visible_mine(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return BA._overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    """Interference in every pose of the placing cycle, plus the star turning: a full turn with the gripper parked,
    and the half step (0..30 degrees) that it makes while a sensor is lifted out of the index fork. Must be empty."""
    doc = active_doc(doc)
    out = {}
    for name in POSES:
        set_pose(name, doc)
        hits = check_interference(doc, tol)
        if hits:
            out[name] = hits
    for pose, angles in (("park", range(0, 360, 10)), ("lift", range(0, int(STEP_DEG / 2.0) + 1, 5))):
        set_pose(pose, doc)
        star = objects_of(doc, "Star")
        others = [(o, global_shape(o)) for o in _visible_mine(doc) + robot_objects(doc) if o not in star]
        for k in angles:
            doc.getObject("Star").Placement = star_placement(float(k))
            st = [(o, global_shape(o)) for o in star]
            hits = BA._overlaps([(a, b) for a in st for b in others if not _joint(a[0].Name, b[0].Name)], tol)
            if hits:
                out["%s_star_%d" % (pose, k)] = hits
    set_pose("park", doc)
    return out


def clearance(doc=None):
    """Smallest distance (mm) of the star and its sensors (one full turn) to the rear wheel units."""
    doc = active_doc(doc)
    rear = [o for o in robot_objects(doc) if o.Name.startswith(("RL_", "RR_"))]
    rear_s = [global_shape(o) for o in rear]
    best = (1e9, None)
    for k in range(0, 36, 3):
        doc.getObject("Star").Placement = star_placement(k * 10.0)
        for o in objects_of(doc, "Star"):
            s = global_shape(o)
            for r, t in zip(rear, rear_s):
                if s.BoundBox.isValid() and t.BoundBox.isValid():
                    d = s.distToShape(t)[0]
                    if d < best[0]:
                        best = (d, (o.Name, r.Name, k * 10))
    set_pose("park", doc)
    return round(best[0], 1), best[1]


MASS_FIXED = {"gripper": P.m_gripper, "z_motor": P.A.m_motor, "mag_drive": P.m_mag_motor + 0.3}


def mass_properties(doc=None):
    """Mass (kg): steel and aluminium parts by volume, bought parts fixed, the 6 sensors at sensor_kg each."""
    doc = active_doc(doc)
    m = 0.0
    for o in _visible_mine(doc):
        if o.Name in MASS_FIXED:
            m += MASS_FIXED[o.Name]
        elif o.Name in ("sensors", "sensor_held"):
            m += P.sensor_kg * len(global_shape(o).Solids)
        else:
            dens = P.A.alu if o.Name in ("mast", "carriage") else P.A.steel
            m += global_shape(o).Volume * dens
    return {"total_kg": round(m, 1)}


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in _visible_mine(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


def save_view(name, direction, target=None, height=None, up=(0.0, 0.0, 1.0), size_px=(1600, 1100)):
    import FreeCADGui as Gui
    Gui.updateGui()
    BA.set_camera(direction, target, height, up)
    Gui.updateGui()
    view = BA.set_camera(direction, target, height, up)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, name)
    view.saveImage(path, size_px[0], size_px[1], "White")
    return path


GROUND = "render_grass"


def render_all():
    """Standard images in previews/ (the cycle seen from the side and in 3D), then build and save."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    g = doc.addObject("Part::Feature", GROUND)
    g.Shape = G.grass(-1100.0, 1100.0)
    g.ViewObject.ShapeColor = (0.47, 0.62, 0.30)
    g.ViewObject.Transparency = 30
    out.append(save_view("1_iso_on_robot_park.png", (-1.0, -1.0, -0.7), target=(0, -150, 500), height=1900))
    for i, pose in enumerate(("pick", "turned", "plant")):
        set_pose(pose, doc)
        out.append(save_view("%d_side_%s.png" % (i + 2, pose), (1.0, 0.0, 0.0), target=(0, -150, 450), height=1400))
    set_pose("released", doc)
    pl = doc.addObject("Part::Feature", "render_planted")
    pl.Shape = G.sensor_at(G.GX, G.GY, 0.0)
    pl.ViewObject.ShapeColor = COLOR["sensor"]
    doc.getObject(GROUND).ViewObject.Transparency = 75
    out.append(save_view("5_planted_iso.png", (-1.0, -0.6, -0.5), target=(0, -150, 250), height=1300))
    set_robot_visible(False, doc)
    BA.remove(doc, [GROUND, "render_planted"])
    set_pose("turned", doc)
    out.append(save_view("6_magazine_star_top.png", (0.0, 0.0, -1.0), target=(0, -200, 0), up=(0.0, 1.0, 0.0),
                         height=800))
    set_pose("lift", doc)
    out.append(save_view("7_gripper_detail.png", (-1.0, -0.8, -0.3), target=(0, -60, 600), height=500))
    App.closeDocument(doc.Name)
    build()
    return out
