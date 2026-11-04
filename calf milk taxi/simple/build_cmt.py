"""Model of the calf milk taxi on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_cmt
    build_cmt.build()
    build_cmt.set_arm(90)                  # 0 = parked along -y, 90 = out over the bucket (+x)
    build_cmt.check_interference()         # must be empty
    build_cmt.check_holes()                # bolts in the upper-beam holes
    build_cmt.check_poses()                # arm 0 / 45 / 90 x steering +-30: empty
    build_cmt.mass_properties()
    build_cmt.render_all()
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cmt_params as P
import cmt_parts as G

SSP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "spotspray unit", "boom")
if SSP_FOLDER not in sys.path:
    sys.path.append(SSP_FOLDER)
import build_ssp as BS          # noqa: E402  (robot model, camera, helpers)

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Calf_Milk_Taxi"
SAVE_BASE = os.path.join(FOLDER, "Calf_Milk_Taxi")
ROOT = "Calf_milk_taxi"

COLOR = {"frame": (0.93, 0.42, 0.08), "zinc": (0.82, 0.84, 0.87), "alu": (0.80, 0.81, 0.83),
         "stainless": (0.86, 0.87, 0.88), "insul": (0.95, 0.85, 0.30), "motor": (0.12, 0.12, 0.13),
         "pump": (0.15, 0.35, 0.70), "box": (0.55, 0.57, 0.60), "hose": (0.92, 0.92, 0.88), "rubber": (0.10, 0.10, 0.10),
         "reader": (0.20, 0.20, 0.22)}


def add_shape(doc, parent, name, label, shape, color, visible=True, transparency=0):
    if isinstance(shape, (list, tuple)):
        shape = Part.makeCompound(list(shape))
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    parent.addObject(obj)
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = COLOR[color]
        obj.ViewObject.Visibility = visible
        obj.ViewObject.Transparency = transparency
    return obj


def arm_placement(angle=0.0):
    return App.Placement(V(P.pivot[0], P.pivot[1], 0), App.Rotation(V(0, 0, 1), angle))


def build_into(doc, parent=None, angle=0.0):
    root = BS.new_part(doc, parent, ROOT, "calf_milk_taxi_simple")
    m = BS.new_part(doc, root, "cmt_Mount", "cross_tubes_base_plate")
    add_shape(doc, m, "cmt_bars", "cross_tubes_40x40x3_y325", G.bars(), "frame")
    add_shape(doc, m, "cmt_bar_bolts", "plate_bolts_8xM10", G.bar_bolts(), "zinc")
    add_shape(doc, m, "cmt_plate", "base_plate_alu_6mm", G.plate(), "alu")
    t = BS.new_part(doc, root, "cmt_Tank", "insulated_tank_80l_stirrer")
    add_shape(doc, t, "cmt_tank", "inner_shell_stainless_O480_cone", G.tank_inner(), "stainless")
    add_shape(doc, t, "cmt_insulation", "PU_insulation_40", G.insulation(), "insul", transparency=0)
    add_shape(doc, t, "cmt_jacket", "jacket_stainless_1mm", G.jacket(), "stainless")
    add_shape(doc, t, "cmt_feet", "feet_3x_O40", G.feet(), "stainless")
    add_shape(doc, t, "cmt_lid", "lid_insulated_fill_cover", G.lid(), "stainless")
    add_shape(doc, t, "cmt_stirrer_motor", "stirrer_gearmotor_24V", G.stirrer_motor(), "motor")
    add_shape(doc, t, "cmt_stirrer", "stirrer_shaft_paddle", G.stirrer(), "stainless")
    add_shape(doc, t, "cmt_outlet", "outlet_O25_butterfly_valve", G.outlet(), "stainless")
    d = BS.new_part(doc, root, "cmt_Dosing", "pump_box_post_gearmotor_hoses")
    add_shape(doc, d, "cmt_pump", "peristaltic_pump_24V_6lpm", G.pump(), "pump")
    add_shape(doc, d, "cmt_box", "control_box_IP66", G.control_box(), "box")
    add_shape(doc, d, "cmt_post", "pivot_post_O60x4_flange", G.post(), "frame")
    add_shape(doc, d, "cmt_gearmotor", "worm_gearmotor_hollow_shaft_rotary_union", G.gearmotor(), "motor")
    add_shape(doc, d, "cmt_hose", "milk_hose_food_grade_O32", G.feed_hose(), "hose")
    a = BS.new_part(doc, root, "cmt_Arm", "swing_arm_moves", arm_placement(angle))
    # the arm shapes are drawn in robot coordinates (parked); the sub-Part rotates about the pivot axis
    for name, label, shape, color in (("cmt_hub", "output_flange_O90", G.hub(), "zinc"),
                                      ("cmt_arm", "arm_40x40x3_620", G.arm_tube(), "alu"),
                                      ("cmt_nozzle", "nozzle_stainless_O22_drip_cone", G.nozzle(), "stainless"),
                                      ("cmt_reader", "rfid_reader_camera_bracket", G.reader(), "reader"),
                                      ("cmt_arm_hose", "arm_hose_O19", G.arm_hose(), "hose")):
        shape = shape.copy()
        shape.translate(V(-P.pivot[0], -P.pivot[1], 0))
        add_shape(doc, a, name, label, shape, color)
    return root


def set_arm(angle=0.0, doc=None):
    doc = active_doc(doc)
    doc.getObject("cmt_Arm").Placement = arm_placement(angle)
    doc.recompute()


def set_steering(deg, doc=None):
    BS.set_steering(deg, deg, active_doc(doc))


global_shape = BS.global_shape
_overlaps = BS._overlaps


def build(save=True, show_robot=False, step=True, angle=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Calf milk taxi simple"
    doc.Comment = ("Generated by build_cmt.py from cmt_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. build_cmt.set_arm(angle) swings the arm.")
    robot = None
    try:
        robot = BS.build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, angle)
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


JOINTS = {("cmt_bar_bolts", "cmt_bars"), ("cmt_bar_bolts", "cmt_plate"), ("cmt_hose", "cmt_outlet"),
          ("cmt_hose", "cmt_pump"), ("cmt_hose", "cmt_post"), ("cmt_arm_hose", "cmt_hub"), ("cmt_arm_hose", "cmt_arm"),
          ("cmt_arm_hose", "cmt_gearmotor"), ("cmt_hose", "cmt_gearmotor"), ("cmt_nozzle", "cmt_arm"),
          ("cmt_stirrer", "cmt_lid"), ("cmt_stirrer", "cmt_stirrer_motor"), ("cmt_outlet", "cmt_tank"),
          ("cmt_outlet", "cmt_insulation"), ("cmt_outlet", "cmt_jacket"), ("cmt_reader", "cmt_arm")}
BEAM_BOLTS = ("cmt_bar_bolts",)


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x in BEAM_BOLTS and y.startswith("upper_beam"):
            return True
    return False


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    for o in robot_objects(doc):
        if o.Name.startswith("upper_beam"):
            objs[o.Name] = global_shape(o)
    pairs = {("cmt_bar_bolts", "cmt_bars"), ("cmt_bar_bolts", "cmt_plate")}
    pairs |= {("cmt_bar_bolts", n) for n in objs if n.startswith("upper_beam")}
    out = {}
    for a, b in sorted(pairs):
        if objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[str((a, b))] = round(v, 1)
    return out


ARM_POSES = (P.ARM_PARK, 45.0, P.ARM_OUT)


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_max, 0.0, P.robot_steer_max)):
    doc = active_doc(doc)
    arm = objects_of(doc, "cmt_Arm")
    names = {o.Name for o in arm}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for a in ARM_POSES:
            set_arm(a, doc)
            mv = [(o, global_shape(o)) for o in arm]
            hits = _overlaps([(x, y) for x in mv for y in fixed if not _joint(x[0].Name, y[0].Name)], tol)
            if hits:
                out[str((st, a))] = hits
    set_steering(0.0, doc)
    set_arm(0.0, doc)
    return out


def nozzle_position(doc=None, angle=P.ARM_OUT):
    doc = active_doc(doc)
    set_arm(angle, doc)
    bb = global_shape(doc.getObject("cmt_nozzle")).BoundBox
    set_arm(0.0, doc)
    return (round(bb.Center.x), round(bb.Center.y), round(bb.ZMin))


MASS_FIXED = {"cmt_pump": 6.5, "cmt_box": 4.0, "cmt_gearmotor": 3.5, "cmt_stirrer_motor": 1.5, "cmt_reader": 0.6}
DENSITY = (("cmt_plate", P.alu), ("cmt_arm", P.alu), ("cmt_insulation", P.pu), ("cmt_hose", 1.2e-6),
           ("cmt_arm_hose", 1.2e-6), ("cmt_tank", P.stainless), ("cmt_jacket", P.stainless),
           ("cmt_lid", 1.1e-6))  # lid: 2 x 3 mm stainless over a PU core


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
    return vol * dens, cg


def mass_properties(doc=None):
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "cmt_Mount", "cmt_Tank", "cmt_Dosing", "cmt_Arm"):
        m, c = 0.0, V(0, 0, 0)
        for o in objects_of(doc, name):
            mo, co = _mass_cg(o)
            m += mo
            c += co * mo
        c = c * (1.0 / m) if m > 0 else c
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


SCENE = ("render_floor", "render_hutches", "render_doors", "render_buckets")


def add_scene(doc):
    def put(name, shape, color, tr=0):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = color
        o.ViewObject.Transparency = tr
    put(SCENE[0], G.box_span((-1300.0, 3200.0), (-3000.0, 3000.0), (-40.0, 0.0)), (0.55, 0.53, 0.48))
    hs, ds = [], []
    ys = [P.pivot[1] - P.hutch_pitch * 1000.0, P.pivot[1], P.pivot[1] + P.hutch_pitch * 1000.0]
    for y in ys:
        h, d = G.hutch(y)
        hs.append(h)
        ds.append(d)
    put(SCENE[1], Part.makeCompound(hs), (0.95, 0.95, 0.92))
    put(SCENE[2], Part.makeCompound(ds), (0.15, 0.15, 0.15))
    put(SCENE[3], Part.makeCompound([G.bucket(y) for y in ys]), (0.95, 0.75, 0.20))


def render_all():
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_scene(doc)
    set_arm(P.ARM_OUT, doc)
    out.append(save_view("1_iso_dosing_at_hutch.png", (-1.0, 1.0, -0.6), target=(600, 300, 700), height=3000))
    out.append(save_view("2_front_arm_over_bucket.png", (0.0, -1.0, -0.05), target=(450, 0, 800), height=1800))
    set_arm(P.ARM_PARK, doc)
    out.append(save_view("3_iso_arm_parked.png", (-1.0, -1.0, -0.6), target=(300, 0, 800), height=2600))
    for n in SCENE:
        if doc.getObject(n):
            doc.removeObject(n)
    set_robot_visible(False, doc)
    for n in ("cmt_jacket", "cmt_insulation"):
        doc.getObject(n).ViewObject.Transparency = 70
    out.append(save_view("4_tank_section_stirrer.png", (-1.0, -0.9, -0.4), target=(0, 0, 1000), height=1300))
    for n in ("cmt_jacket", "cmt_insulation"):
        doc.getObject(n).ViewObject.Transparency = 0
    set_arm(45.0, doc)
    out.append(save_view("5_pump_post_arm.png", (-0.6, -1.0, -0.7), target=(200, -50, 950), height=1300))
    set_arm(P.ARM_PARK, doc)
    set_robot_visible(True, doc)
    out.append(save_view("6_top_parked.png", (0.0, 0.0, -1.0), target=(0, 0, 0), up=(0.0, 1.0, 0.0), height=1800))
    set_arm(P.ARM_OUT, doc)
    out.append(save_view("7_top_out.png", (0.0, 0.0, -1.0), target=(250, 0, 0), up=(0.0, 1.0, 0.0), height=2200))
    App.closeDocument(doc.Name)
    build()
    return out
