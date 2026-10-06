import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fpa_params as P
import fpa_parts as G

DOC_NAME = "Feed_Pusher_Auger"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Feed_Pusher_Auger.FCStd")
STEP_PATH = os.path.join(FOLDER, "Feed_Pusher_Auger.step")
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbot design")

COLOR = {
    "frame": (0.22, 0.24, 0.26),
    "hood": (0.30, 0.33, 0.36),
    "auger": (0.95, 0.70, 0.05),
    "steel": (0.75, 0.75, 0.78),
    "zinc": (0.82, 0.84, 0.87),
    "bearing": (0.10, 0.20, 0.45),
    "motor": (0.08, 0.08, 0.08),
    "chain": (0.25, 0.25, 0.27),
    "guard": (0.95, 0.70, 0.05),
    "rubber": (0.08, 0.08, 0.08),
    "pe": (0.92, 0.92, 0.88),
    "nylon": (0.95, 0.95, 0.90),
    "mount": (0.93, 0.42, 0.08),
    "ballast": (0.35, 0.36, 0.38),
}
TRANSPARENT = {"hood": 35, "guard": 55}


# ---------------------------------------------------------------------
# Hulpfuncties boom (zelfde als build_lfa.py)
# ---------------------------------------------------------------------
def new_part(doc, parent, name, label, placement=None):
    part = doc.addObject("App::Part", name)
    part.Label = label
    if placement is not None:
        part.Placement = placement
    if parent is not None:
        parent.addObject(part)
    return part


def add_shape(doc, parent, name, label, shape, color, visible=True, transparency=None):
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
        view.Transparency = TRANSPARENT.get(color, 0) if transparency is None else transparency
    return obj


def rotation_x(angle, center):
    """Rotatie om een as evenwijdig aan x door (y, z) = center."""
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), angle), V(0, center[0], center[1]))


AUGER_AXIS = (P.auger_y, P.auger_z)
MOTOR_AXIS = (G.MY, G.MZ)


# ---------------------------------------------------------------------
# Onderdelen in de boom
# ---------------------------------------------------------------------
def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "robot_mount_wheel_modules")
    xcs = []
    for i, (x_hole, side) in enumerate(G.arm_spots()):
        shape, xc = G.arm(x_hole, side)
        xcs.append(xc)
        where = ("left" if x_hole < 0 else "right") + ("_inner" if abs(x_hole) < P.robot_wheel_x else "_outer")
        add_shape(doc, grp, "arm_%d" % (i + 1), "mount_arm_%s" % where, shape, "mount")
        add_shape(doc, grp, "arm_bolts_%d" % (i + 1), "mount_bolts_%s_M10_M12" % where, G.arm_bolts(x_hole, xc), "zinc")
    return grp, xcs


def build_frame(doc, parent, xcs):
    grp = new_part(doc, parent, "Frame", "frame_sheet_metal")
    add_shape(doc, grp, "hood", "hood_2mm_4_bends", G.hood(), "hood")
    add_shape(doc, grp, "cross_beam", "cross_beam_80x80x3", G.beam().cut(G.beam_arm_holes(xcs)), "frame")
    for i, cap in enumerate(G.beam_caps()):
        add_shape(doc, grp, "beam_cap_%s" % ("left", "right")[i], "beam_end_plate_8mm_%s" % ("left", "right")[i], cap, "frame")
    add_shape(doc, grp, "beam_cap_bolts", "beam_end_bolts_M12", G.cap_bolts(), "zinc")
    add_shape(doc, grp, "side_plate_left", "side_plate_left_8mm_drive", G.side_plate_left(), "frame")
    add_shape(doc, grp, "bearing_plate_right", "bearing_plate_right_8mm_open_end", G.bearing_plate_right(), "frame")
    add_shape(doc, grp, "hood_brackets", "hood_brackets_40x40x3", G.hood_brackets(), "zinc")
    add_shape(doc, grp, "flap", "rubber_scraper_flap_10mm", G.flap(), "rubber")
    add_shape(doc, grp, "clamp_strip", "flap_clamp_strip_30x5", G.clamp_strip(), "zinc")
    add_shape(doc, grp, "skid", "glide_shoe_PE1000_left", G.skid(), "pe")
    add_shape(doc, grp, "skid_bolts", "glide_shoe_bolts_M8", G.skid_bolts(), "zinc")
    add_shape(doc, grp, "motor_base", "motor_base_plate_8mm_on_hood", G.motor_base(), "frame")
    add_shape(doc, grp, "motor_base_bolts", "motor_base_bolts_M10_to_beam", G.base_bolts(), "zinc")
    return grp


def build_bearings(doc, parent):
    grp = new_part(doc, parent, "Bearings", "bearings_UCF206")
    for tag, xf, s in (("left", -P.xo, -1), ("right", P.xo, 1)):
        add_shape(doc, grp, "ucf206_" + tag, "flange_bearing_UCF206_" + tag, G.ucf206(xf, s), "bearing")
        add_shape(doc, grp, "ucf206_bolts_" + tag, "bearing_bolts_M12_" + tag, G.ucf_bolts(xf, s), "zinc")
    return grp


def build_drive(doc, parent):
    grp = new_part(doc, parent, "Drive", "drive_foot_mounted_gearmotor_chain")
    add_shape(doc, grp, "gearmotor", "gearmotor_24V_550W_B3_feet", G.gearmotor(), "motor")
    add_shape(doc, grp, "foot_bolts", "gearmotor_foot_bolts_M10", G.foot_bolts(), "zinc")
    add_shape(doc, grp, "motor_shaft", "gearmotor_output_shaft_D25", G.motor_shaft(), "steel")
    add_shape(doc, grp, "motor_sprocket", "sprocket_08B_%dT_motor" % P.z_motor, G.motor_sprocket(), "steel")
    add_shape(doc, grp, "chain", "roller_chain_08B-1", G.chain(), "chain")
    body, idler, hw = G.tensioner()
    add_shape(doc, grp, "tensioner", "chain_tensioner_arm_rubber_element", body, "frame")
    add_shape(doc, grp, "tensioner_idler", "chain_tensioner_idler_PA_D40", idler, "nylon")
    add_shape(doc, grp, "tensioner_hw", "chain_tensioner_bolts", hw, "zinc")
    add_shape(doc, grp, "chain_guard", "chain_guard_2mm", G.chain_guard(), "guard")
    return grp


def build_rotor(doc, parent, angle=0.0):
    rot = new_part(doc, parent, "Auger_rotor", "auger_rotor_turns", rotation_x(angle, AUGER_AXIS))
    add_shape(doc, rot, "shaft", "stub_shafts_D30_C45", G.shaft(), "steel")
    add_shape(doc, rot, "core", "core_tube_60.3x4", G.core(), "auger")
    add_shape(doc, rot, "blade", "flight_D320_P260_5mm", G.blade(), "auger")
    add_shape(doc, rot, "pins", "pins_M10_shear_bolt_left", G.pins(), "zinc")
    add_shape(doc, rot, "auger_sprocket", "sprocket_08B_%dT_auger" % P.z_auger, G.auger_sprocket(), "steel")
    return rot


def build_ballast(doc, parent):
    grp = new_part(doc, parent, "Counterweight", "counterweight_front_2x20kg")
    add_shape(doc, grp, "ballast", "counterweight_blocks", G.ballast(), "ballast")
    add_shape(doc, grp, "ballast_bolts", "counterweight_bolts_M10", G.ballast_bolts(), "zinc")
    return grp


def build_into(doc, parent=None, ballast=True):
    """Zet de voerschuif in een document, in robotcoordinaten (ook gebruikt door animate_fpa.py)."""
    root = new_part(doc, parent, "Feed_pusher", "feed_pusher_auger")
    _, xcs = build_mount(doc, root)
    build_frame(doc, root, xcs)
    build_bearings(doc, root)
    build_drive(doc, root)
    build_rotor(doc, root)
    if ballast:
        build_ballast(doc, root)
    return root


def build_robot(doc):
    """Echt robotmodel uit 'agbot design' (alleen lezen, de bestanden daar worden niet aangepast)."""
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


def build(save_path=SAVE_PATH, show_robot=False, step_path=STEP_PATH):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Feed pusher auger (advanced)"
    doc.Comment = ("Gegenereerd met build_fpa.py uit fpa_params.py. Robotcoordinaten: x = rechts, y = rijrichting "
                   "robot (voor = +y), z = omhoog, grond = z 0. Vijzel achter de robot (vaste wielmotoren), voerhek +x.")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robotmodel niet geladen:", exc)
    build_into(doc, robot)
    if robot is not None and not show_robot:
        set_robot_visible(False, doc)
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    if step_path:
        export_step(doc, step_path)
    return doc


def pusher_objects(doc):
    return [o for o in doc.getObject("Feed_pusher").OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    pusher = {o.Name for o in pusher_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in pusher]


def set_robot_visible(visible, doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in pusher_objects(doc):
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        f = doc.addObject("Part::Feature", "step_" + o.Name)
        f.Label = o.Label
        f.Shape = s
        objs.append(f)
    try:
        Import.export(objs, path)
    finally:
        for f in objs:
            doc.removeObject(f.Name)


# ---------------------------------------------------------------------
# Controle
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def check_interference(doc=None, tol=1.0):
    """Volume-overlap (mm3): voerschuif onderling en voerschuif tegen de (zichtbare en verborgen) robot."""
    doc = doc or App.getDocument(DOC_NAME)
    mine = [(o, global_shape(o)) for o in pusher_objects(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    hits = []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    for (oa, sa), (ob, sb) in pairs:
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


def clearance(doc=None, names=("hood", "flap", "clamp_strip", "arm_1", "arm_2", "arm_3", "arm_4"),
              robot_names=("RL_tire", "RR_tire")):
    """Kleinste afstand (mm) tussen delen van de voerschuif en de achterbanden."""
    doc = doc or App.getDocument(DOC_NAME)
    out = {}
    for n in names:
        a = global_shape(doc.getObject(n))
        out[n] = round(min(a.distToShape(global_shape(doc.getObject(r)))[0] for r in robot_names), 1)
    return out


MASS_FIXED = {"gearmotor": 14.0}
DENSITY = (("flap", 1.5e-6), ("skid", 0.96e-6), ("tensioner_idler", 1.15e-6), ("chain", 7.85e-6 * 0.45))
STEEL = 7.85e-6


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
    """Massa (kg) en zwaartepunt (robotcoordinaten) van voerschuif, rotor en contragewicht."""
    doc = doc or App.getDocument(DOC_NAME)
    ballast = {o.Name for o in doc.getObject("Counterweight").OutListRecursive} if doc.getObject("Counterweight") else set()
    objs = [o for o in pusher_objects(doc) if o.Name not in ballast]
    rotor = [o for o in doc.getObject("Auger_rotor").OutListRecursive if o.TypeId == "Part::Feature"]
    m, c = _sum(objs)
    mr, cr = _sum(rotor)
    mb, cb = _sum([o for o in pusher_objects(doc) if o.Name in ballast]) if ballast else (0.0, V(0, 0, 0))
    return {"pusher_kg": round(m, 1), "pusher_cg": (round(c.x), round(c.y), round(c.z)),
            "rotor_kg": round(mr, 1), "ballast_kg": round(mb, 1), "ballast_cg_y": round(cb.y)}


def size(doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    bb = None
    for o in pusher_objects(doc):
        if o.Name.startswith("ballast"):
            continue
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


# ---------------------------------------------------------------------
# Afbeeldingen
# ---------------------------------------------------------------------
def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, -850, 300)
    eye = tgt - d * 8000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(30000.0)
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


def add_floor(doc, y=(-1400.0, 900.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span((-1000.0, 1000.0), y, (-60.0, 0.0))
    obj.ViewObject.ShapeColor = (0.70, 0.70, 0.68)
    obj.ViewObject.Transparency = 40
    return obj


def remove_floor(doc):
    if doc.getObject(GROUND):
        doc.removeObject(GROUND)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def render_all():
    """Alle afbeeldingen in previews/: los werktuig, details en op de robot."""
    doc = build(save_path=None, show_robot=False, step_path=None)
    set_visible(doc, ("ballast", "ballast_bolts"), False)
    out = []
    out.append(save_view("1_iso_front_left.png", (1.0, 1.0, -0.7)))
    out.append(save_view("2_iso_rear_right.png", (-1.0, -1.0, -0.65)))
    out.append(save_view("4_top.png", (0.0, 0.0, -1.0), up=(0.0, 1.0, 0.0)))
    out.append(save_view("5_front.png", (0.0, 1.0, 0.0)))
    out.append(save_view("6_drive_detail.png", (1.0, 0.6, -0.45), target=(-760, -960, 330), height=700))
    out.append(save_view("7_mount_detail.png", (-0.9, -1.0, -0.5), target=(375, -680, 380), height=750))
    add_floor(doc)
    try:
        out.append(save_view("3_side_left.png", (1.0, 0.0, 0.0), target=(0, -870, 300), height=800))
        set_visible(doc, ("hood", "chain_guard"), False)
        out.append(save_view("8_open_end_right.png", (-1.0, 0.25, -0.2), target=(700, -960, 220), height=700))
        set_visible(doc, ("hood", "chain_guard"), True)
    finally:
        remove_floor(doc)
    set_visible(doc, ("ballast", "ballast_bolts"), True)
    set_robot_visible(True, doc)
    out.append(save_view("9_on_robot_iso.png", (1.0, 1.1, -0.7), target=(0, -250, 350)))
    add_floor(doc, (-1500.0, 1100.0))
    try:
        out.append(save_view("10_on_robot_side.png", (1.0, 0.0, 0.0), target=(0, -250, 400), height=1500))
    finally:
        remove_floor(doc)
    out.append(save_view("11_on_robot_rear_right.png", (-1.0, 1.0, -0.6), target=(0, -250, 350)))
    set_robot_visible(False, doc)
    doc.saveAs(SAVE_PATH)
    export_step(doc, STEP_PATH)
    return out
