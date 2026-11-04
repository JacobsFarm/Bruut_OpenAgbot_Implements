"""Model of the manure vacuum collector on the Bruut OpenAgbot (standard robot).

Mount, lift arms, carrier, king pin, actuator (push blade), head frame and castors (magnet sweeper), nozzle hood, hose,
inlet stub and cross bars (debris vacuum) are imported via build_dvc / dvc_parts; this file adds the squeegee lip,
the vacuum tank with float valve, moisture trap, vacuum pump and dump valve.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_mvc
    build_mvc.build()
    build_mvc.set_pose(18)                 # lift (transport)
    build_mvc.check_interference()         # must be empty
    build_mvc.check_poses()                # lift poses x steering +-30: empty
    build_mvc.mass_properties()
    build_mvc.render_all()
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mvc_params as P
import mvc_parts as G
import dvc_parts as DG
import build_dvc as BD

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Manure_Vacuum"
SAVE_BASE = os.path.join(FOLDER, "Manure_Vacuum")
ROOT = "Manure_vacuum"

COLOR = dict(BD.COLOR)
COLOR.update({"tank": (0.86, 0.87, 0.88), "valve": (0.85, 0.15, 0.10), "pump": (0.15, 0.35, 0.70),
              "lip": (0.08, 0.08, 0.08)})


def add_shape(doc, parent, name, label, shape, color, visible=True):
    obj = BD.BP.add_shape(doc, parent, name, label, shape, "frame", visible)
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = COLOR[color]
    return obj


def build_lift(doc, parent, lift=P.lift_work):
    PP = BD.PP
    lg = BD.new_part(doc, parent, "Lift", "lift_arms_turn_about_pivot", BD.lift_placement(lift))
    add_shape(doc, lg, "carrier", "carrier_weldment_from_push_blade", PP.carrier(), "frame")
    add_shape(doc, lg, "king_pin", "king_pin_M30_PE_washer", PP.king_pin(), "zinc")
    add_shape(doc, lg, "lock_pin", "lock_pin_D16_middle_hole", PP.lock_pin(), "zinc")
    head = BD.new_part(doc, lg, "Head", "nozzle_head_on_king_pin", BD.head_placement(0.0))
    add_shape(doc, head, "head_frame", "head_frame_from_magnet_sweeper", DG.head_frame(), "head")
    add_shape(doc, head, "box_bolts", "nozzle_bolts_M10_8x", DG.box_bolts(), "zinc")
    add_shape(doc, head, "hood", "nozzle_hood_steel_2mm_from_debris_vacuum", G.hood(), "hood")
    add_shape(doc, head, "end_plates", "nozzle_end_plates_5mm", G.end_plates(), "hood")
    add_shape(doc, head, "flaps", "front_flap_rubber_6mm_40_high", G.flap(), "rubber")
    add_shape(doc, head, "mvc_lip", "squeegee_lip_rubber_12mm", G.lip(), "lip")
    add_shape(doc, head, "mvc_lip_clamp", "squeegee_clamp_bar_5mm", G.lip_clamp(), "zinc")
    add_shape(doc, head, "outlet", "outlet_stub_D125", DG.outlet(), "hood")
    add_shape(doc, head, "castor_spacers", "castor_spacers_20mm", DG.castor_spacers(), "head")
    add_shape(doc, head, "castors", "swivel_castors_125", DG.castors(), "castor")
    add_shape(doc, head, "castor_wheels", "castor_wheels_PU_125x40", DG.castor_wheels(), "pu")
    add_shape(doc, head, "castor_bolts", "castor_bolts_M8", DG.castor_bolts(), "zinc")
    return lg


def build_tank(doc, parent):
    grp = BD.new_part(doc, parent, "Tank", "vacuum_tank_130l_pump_dump_valve")
    add_shape(doc, grp, "cross_bars", "cross_bars_60x40x3_2x", G.cross_bars(), "frame")
    add_shape(doc, grp, "bar_bolts", "cross_bar_bolts_M10_8x", G.bar_bolts(), "zinc")
    add_shape(doc, grp, "mvc_saddles", "tank_saddles_PE", G.saddles(), "rubber")
    add_shape(doc, grp, "mvc_tank", "vacuum_tank_stainless_O460_130l", G.tank(), "tank")
    add_shape(doc, grp, "inlet", "tank_inlet_stub_D125", G.inlet(), "tank")
    add_shape(doc, grp, "mvc_float", "float_valve_shut_off", G.float_valve(), "valve")
    add_shape(doc, grp, "mvc_trap", "moisture_trap", G.moisture_trap(), "tank")
    add_shape(doc, grp, "mvc_vac_hoses", "vacuum_hoses_O40", G.vac_hoses(), "hose")
    add_shape(doc, grp, "mvc_shelf_tubes", "pump_shelf_tubes_40x40", G.shelf_tubes(), "frame")
    add_shape(doc, grp, "mvc_shelf_bolts", "pump_shelf_bolts_M10_8x", G.shelf_bolts(), "zinc")
    add_shape(doc, grp, "mvc_shelf", "pump_shelf_plate_6mm", G.shelf(), "frame")
    add_shape(doc, grp, "mvc_pump", "rotary_vane_vacuum_pump_48V_900W", G.pump(), "pump")
    add_shape(doc, grp, "mvc_dump", "knife_gate_dump_valve_O150_pipe", G.dump_body(), "valve")
    add_shape(doc, grp, "mvc_dump_act", "dump_valve_actuator_24V", G.dump_actuator(), "motor")
    return grp


def build_into(doc, parent=None, lift=P.lift_work):
    root = BD.new_part(doc, parent, ROOT, "manure_vacuum_simple")
    BD.BP.build_mount(doc, root)
    build_lift(doc, root, lift)
    BD.build_actuator(doc, root, lift)
    build_tank(doc, root)
    hose = BD.new_part(doc, root, "Hose", "suction_hose_PU_D125")
    add_shape(doc, hose, "hose", "suction_hose_PU_D125", DG.hose(lift), "hose")
    return root


def set_pose(lift=P.lift_work, doc=None):
    BD.set_pose(lift, active_doc(doc))
    active_doc(doc).recompute()


def set_steering(deg, doc=None):
    BD.set_steering(deg, active_doc(doc))


global_shape = BD.global_shape
_overlaps = BD._overlaps


def build(save=True, show_robot=False, step=True, lift=P.lift_work):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Manure vacuum simple"
    doc.Comment = ("Generated by build_mvc.py from mvc_params.py (nozzle, lift, hose from debris vacuum/simple). Robot "
                   "coordinates: x = right, y = driving direction (front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = BD.build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, lift)
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


JOINTS = {("mvc_lip", "mvc_lip_clamp"), ("inlet", "mvc_tank"), ("mvc_float", "mvc_tank"), ("mvc_vac_hoses", "mvc_float"),
          ("mvc_vac_hoses", "mvc_trap"), ("mvc_vac_hoses", "mvc_pump"), ("mvc_dump", "mvc_tank"),
          ("mvc_dump_act", "mvc_dump"), ("mvc_shelf_bolts", "mvc_shelf_tubes"), ("mvc_saddles", "mvc_tank"),
          ("mvc_shelf", "mvc_shelf_tubes")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS or BD._joint(a, b):
        return True
    for x, y in ((a, b), (b, a)):
        if x == "mvc_shelf_bolts" and y.startswith("upper_beam"):
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
    out = {}
    beams = [o for o in robot_objects(doc) if o.Name.startswith("upper_beam")]
    for bn in ("bar_bolts", "mvc_shelf_bolts"):
        sb = global_shape(doc.getObject(bn))
        for o in beams:
            so = global_shape(o)
            if sb.BoundBox.intersect(so.BoundBox):
                v = sb.common(so).Volume
                if v > tol:
                    out[str((bn, o.Name))] = round(v, 1)
    return out


def check_poses(doc=None, tol=1.0, steer=(-30.0, 0.0, 30.0)):
    doc = active_doc(doc)
    moving = objects_of(doc, "Lift") + objects_of(doc, "Actuator") + objects_of(doc, "Hose")
    names = {o.Name for o in moving}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for lift in P.LIFT_POSES:
            set_pose(lift, doc)
            mv = [(o, global_shape(o)) for o in moving]
            hits = _overlaps([(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
            if hits:
                out[str((st, lift))] = hits
    set_steering(0.0, doc)
    set_pose(P.lift_work, doc)
    return out


MASS_FIXED = {"mvc_pump": 19.0, "mvc_float": 1.2, "mvc_trap": 1.5, "mvc_dump_act": 1.8, "act_body": 2.4, "act_rod": 1.0}
DENSITY = (("mvc_tank", P.stainless), ("inlet", P.stainless), ("mvc_saddles", 0.95e-6), ("mvc_lip", P.rubber),
           ("flaps", P.rubber), ("hose", 1.6e-6), ("castor_wheels", 1.2e-6), ("mvc_vac_hoses", 1.2e-6))


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
    for name in (ROOT, "Mount", "Lift", "Tank"):
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


set_camera = BD.BP.set_camera


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


SCENE = ("render_floor", "render_manure", "render_film")


def add_scene(doc):
    y0, y1 = -2500.0, 3500.0
    for name, shape, color in ((SCENE[0], G.floor(y0, y1), (0.62, 0.62, 0.60)),
                               (SCENE[1], G.manure(y0, y1), (0.38, 0.30, 0.15)),
                               (SCENE[2], G.wet_film(y0, y1), (0.48, 0.42, 0.28))):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = color


def render_all():
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_scene(doc)
    out.append(save_view("1_iso_front_in_alley.png", (-1.0, -1.1, -0.65), target=(0, 500, 550), height=2900))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, 400, 600), height=2600))
    for n in SCENE:
        doc.removeObject(n)
    set_pose(P.lift_transport, doc)
    out.append(save_view("3_side_lifted.png", (1.0, 0.0, 0.0), target=(0, 400, 600), height=2600))
    set_pose(P.lift_work, doc)
    out.append(save_view("4_iso_rear_tank_pump_dump.png", (-1.0, 1.0, -0.6), target=(0, -200, 900), height=1800))
    set_robot_visible(False, doc)
    doc.getObject("hood").ViewObject.Transparency = 60
    out.append(save_view("5_nozzle_squeegee_from_below.png", (0.4, -0.6, 1.0), target=(0, 1400, 100), height=1300))
    doc.getObject("hood").ViewObject.Transparency = 0
    set_robot_visible(True, doc)
    set_steering(30.0, doc)
    out.append(save_view("6_top_steered_30deg.png", (0.0, 0.0, -1.0), target=(0, 400, 0), up=(0.0, 1.0, 0.0), height=2600))
    set_steering(0.0, doc)
    App.closeDocument(doc.Name)
    build()
    return out
