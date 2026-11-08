"""Model of the lift mast (2 columns, carriage on plain bushes with the male A-frame triangle, LA36 stroke 300) with a
demo machine on parking legs, on the Bruut OpenAgbot.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_tpl
    build_tpl.build()                      # saves FCStd and STEP (carriage low, machine standing on its legs)
    build_tpl.set_pose(dz=280)             # carriage up (machine lifted 220 mm)
    build_tpl.check_interference(), build_tpl.check_poses(), build_tpl.clearance(), build_tpl.mass_properties()
    build_tpl.render_all()                 # all images in previews/
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tpl_params as P
import tpl_parts as G
import tpa_params as Q
import tpa_parts as GA
import tph_parts as TG
import build_tpa as BA

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = BA.AGBOT_FOLDER
DOC_NAME = "Three_Point_Hitch_Lift"
SAVE_BASE = os.path.join(FOLDER, "Three_Point_Hitch_Lift")
ROOT = "TPL_hitch"
MACHINE = "TPL_Machine"
COLOR = dict(BA.COLOR)
COLOR.update({"box": (0.20, 0.55, 0.30), "load": (0.85, 0.75, 0.45), "bush": (0.95, 0.75, 0.20),
              "machine": (0.10, 0.40, 0.70)})
BA.COLOR.update(COLOR)
new_part = BA.new_part
add_shape = BA.add_shape
global_shape = BA.global_shape
objects_of = BA.objects_of
_overlaps = BA._overlaps
ROD_REF = P.act_retracted
SIDES = ((-1, "left"), (1, "right"))


def carriage_placement(dz):
    return App.Placement(V(0, 0, dz), App.Rotation())


def machine_placement(dz_m, dy=0.0):
    return App.Placement(V(0, dy, dz_m), App.Rotation())


def build_mount(doc, parent):
    grp = new_part(doc, parent, "TPL_Mount", "mount_rear_toolbar_and_lift_mast")
    add_shape(doc, grp, "toolbar", "rear_toolbar_80x80x4_L900", TG.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_caps", "toolbar_end_caps_PE", TG.toolbar_caps(), "plastic")
    for sx, tag in SIDES:
        add_shape(doc, grp, "hanger_top_" + tag, "hanger_top_plate_10mm_" + tag, TG.hanger_top(sx), "frame")
        add_shape(doc, grp, "hanger_webs_" + tag, "hanger_webs_6mm_" + tag, TG.hanger_webs(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_M10_" + tag, TG.hanger_bolts(sx), "zinc")
    add_shape(doc, grp, "mast_frame", "mast_cross_tubes_60x40_uprights_40x40_brackets", G.mast_frame(), "frame")
    add_shape(doc, grp, "columns", "columns_D50x4_2x", G.columns(), "steel")
    add_shape(doc, grp, "slot_plates", "LA36_rod_slot_plates_2x8mm_slot_%d" % P.float_slot, G.slot_plates(), "frame")
    return grp


def build_carriage(doc, parent, dz=0.0):
    grp = new_part(doc, parent, "TPL_Carriage", "carriage_with_male_A_frame_moves_up", carriage_placement(dz))
    add_shape(doc, grp, "housings", "bush_housings_90x80x60_4x", G.housings(), "frame")
    add_shape(doc, grp, "bushes", "iglidur_bushes_D50_4x", G.bushes(), "bush")
    add_shape(doc, grp, "carriage_plate", "carriage_plate_10mm_wedges_LA36_lugs", G.carriage_plate(), "frame")
    add_shape(doc, grp, "carriage_pins", "LA36_body_pin_D12", G.carriage_pins(), "zinc")
    add_shape(doc, grp, "male_frame", "A_frame_male_triangle_40x40x3", G.male_frame(), "coupler")
    add_shape(doc, grp, "male_latch", "A_frame_latch_pin_D20_T_handle", G.male_latch(), "handle")
    return grp


def build_actuator(doc, parent, dz=0.0, act_len=None):
    grp = new_part(doc, parent, "TPL_Actuator", "linak_LA36_%s_stroke%d_vertical" % (P.act_variant, P.act_stroke))
    add_shape(doc, grp, "act_body", "linak_LA36_24V_housing_motor_along_x_outer_tube",
              GA.la36_body(P.act_motor_side, P.act_retracted, P.act_roll), "actuator")
    pin_half = Q.act_rod_eye_c / 2.0 + Q.act_eye_clear + 8.0 + 4.0
    add_shape(doc, grp, "act_rod", "linak_LA36_inner_tube_rod_eye_pin_D12",
              GA.la36_rod(ROD_REF, P.act_retracted, pin_half, P.act_stroke), "chrome")
    set_actuator(doc, dz, act_len)
    return grp


def set_actuator(doc, dz, act_len=None):
    pb, pr, L = GA.la36_placements(P.body_pin(dz), P.act_pin(dz, act_len), ROD_REF)
    doc.getObject("act_body").Placement = pb
    doc.getObject("act_rod").Placement = pr
    return L


def build_machine(doc, parent, dz_m=0.0):
    grp = new_part(doc, parent, MACHINE, "demo_machine_box_on_parking_legs_female_A_frame", machine_placement(dz_m))
    add_shape(doc, grp, "machine_frame", "machine_frame_female_A_frame_rails_parking_legs", G.machine_frame(),
              "machine")
    add_shape(doc, grp, "machine_box", "machine_box_PE_840x560x380", G.machine_box(), "box")
    add_shape(doc, grp, "machine_load", "machine_load_%dkg" % P.mc_load_kg, G.machine_load(), "load")
    return grp


def build_into(doc, parent=None, dz=0.0, machine_parent="root"):
    """Hitch (and the demo machine) in a document, robot coordinates. machine_parent: "root" (in the hitch tree),
    None (top level, for the animation where the machine stands in the field)."""
    root = new_part(doc, parent, ROOT, "three_point_hitch_lift_mast_LA36")
    build_mount(doc, root)
    build_carriage(doc, root, dz)
    build_actuator(doc, root, dz)
    build_machine(doc, root if machine_parent == "root" else machine_parent, P.machine_dz(dz))
    return root


def set_pose(dz=0.0, doc=None, act_len=None, machine=True):
    doc = active_doc(doc)
    doc.getObject("TPL_Carriage").Placement = carriage_placement(dz)
    if machine and doc.getObject(MACHINE) is not None:
        doc.getObject(MACHINE).Placement = machine_placement(P.machine_dz(dz))
    return set_actuator(doc, dz, act_len)


def build(save=True, show_robot=False, step=True, dz=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Three-point hitch lift"
    doc.Comment = ("Generated by build_tpl.py from tpl_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Carriage low, machine on its legs; build_tpl.set_pose() lifts.")
    robot = None
    try:
        robot = BA.build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, dz)
    if robot is not None and not show_robot:
        set_robot_visible(False, doc)
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


def my_objects(doc):
    names = {o.Name for o in objects_of(doc, ROOT)}
    return objects_of(doc, ROOT) + [o for o in objects_of(doc, MACHINE) if o.Name not in names]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in my_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in my_objects(doc):
        f = doc.addObject("Part::Feature", "step_" + o.Name)
        f.Label = o.Label
        f.Shape = global_shape(o)
        objs.append(f)
    try:
        Import.export(objs, path)
    finally:
        for f in objs:
            doc.removeObject(f.Name)


JOINTS = {("housings", "bushes"), ("bushes", "columns"), ("columns", "mast_frame"), ("housings", "carriage_plate"),
          ("carriage_pins", "carriage_plate"), ("carriage_pins", "act_body"), ("act_rod", "slot_plates"),
          ("act_body", "act_rod"), ("male_latch", "male_frame"), ("male_latch", "machine_frame"),
          ("carriage_plate", "male_frame"), ("slot_plates", "mast_frame"), ("machine_box", "machine_load"),
          ("hanger_bolts_left", "hanger_top_left"), ("hanger_bolts_right", "hanger_top_right"),
          ("mast_frame", "toolbar")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x.startswith("hanger_bolts") and y.startswith("lower_beam"):
            return True
    return False


MOVING = ("TPL_Carriage", "TPL_Actuator", MACHINE)


def _pairs_all(items):
    return [(items[i], items[j]) for i in range(len(items)) for j in range(i + 1, len(items))
            if not _joint(items[i][0].Name, items[j][0].Name)]


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in my_objects(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = _pairs_all(mine) + [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0, poses=None):
    """Interference over the travel (LA36 carrying; machine on its legs until the triangle has lifted into it) and
    with the rod pin floating up in the slot."""
    doc = active_doc(doc)
    moving = [o for n in MOVING for o in objects_of(doc, n)]
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in my_objects(doc) + robot_objects(doc) if o.Name not in names]
    out = {}
    poses = poses or [(x, None) for x in P.DZ_POSES] + [(P.float_slot, P.act_length(0.0))]
    for dz, act_len in poses:
        set_pose(dz, doc, act_len)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)] + _pairs_all(mv)
        hits = _overlaps(pairs, tol)
        if hits:
            out[str((dz, act_len))] = hits
    set_pose(doc=doc)
    return out


def clearance(doc=None, names=("RL_top_plate", "RR_top_plate", "RL_side_l", "RR_side_r")):
    doc = active_doc(doc)
    targets = [global_shape(doc.getObject(n)) for n in names if doc.getObject(n) is not None]
    for sx in (-1, 1):
        targets.append(Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w,
                                         V(sx * P.robot_wheel_x - P.robot_tire_w / 2.0, -P.robot_axle_y, 215.0),
                                         V(1, 0, 0)))
    out = {}
    for dz in (0.0, P.travel):
        set_pose(dz, doc)
        best = (1e9, None)
        for o in [o for n in MOVING for o in objects_of(doc, n)]:
            s = global_shape(o)
            for t in targets:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name)
        out[dz] = (round(best[0], 1), best[1])
    set_pose(doc=doc)
    return out


def ground_contact(doc=None):
    doc = active_doc(doc)
    out = {}
    for dz in (0.0, P.couple_dz, P.travel):
        set_pose(dz, doc)
        out[dz] = {"machine_feet": round(global_shape(doc.getObject("machine_frame")).BoundBox.ZMin, 1),
                   "carriage_low": round(min(global_shape(o).BoundBox.ZMin for o in objects_of(doc, "TPL_Carriage")), 1)}
    set_pose(doc=doc)
    return out


MASS_FIXED = {"act_body": P.act_mass() - 0.8, "act_rod": 0.8}
DENSITY = (("toolbar_caps", P.pe_density), ("bushes", 1.4e-6), ("machine_box", P.pe_density))


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
    if obj.Name == "machine_load":
        return P.mc_load_kg, cg
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
    doc = active_doc(doc)
    set_pose(doc=doc)
    out = {}
    for name in (ROOT, "TPL_Mount") + MOVING:
        m, c = sum_mass(objects_of(doc, name))
        key = name.replace("TPL_", "").lower()
        out[key + "_kg"] = round(m, 1)
        out[key + "_cg"] = (round(c.x), round(c.y), round(c.z))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in objects_of(doc, ROOT):
        if o.Name.startswith("machine"):
            continue
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


# ---------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------
def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.getDocument(DOC_NAME).ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, 600, 300)
    eye = tgt - d * 9000.0
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


def set_visible(doc, group, visible):
    for o in objects_of(doc, group):
        o.ViewObject.Visibility = visible


def render_all():
    out = []
    doc = build(save=False, show_robot=True, step=False)
    App.setActiveDocument(doc.Name)
    BA.add_floor(doc, y=(-2200.0, 900.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.2, -0.7), target=(0, -1000, 500)))
    out.append(save_view("2_side_low_machine_on_legs.png", (1.0, 0.0, 0.0), target=(0, -1250, 560), height=1500))
    set_pose(P.travel, doc)
    out.append(save_view("3_side_machine_lifted.png", (1.0, 0.0, 0.0), target=(0, -1250, 560), height=1500))
    out.append(save_view("4_iso_machine_lifted.png", (-1.0, 1.2, -0.7), target=(0, -1100, 550), height=2200))
    set_pose(doc=doc)
    BA.remove(doc, [BA.GROUND])
    out.append(save_view("5_top.png", (0.0, 0.0, -1.0), target=(0, -1050, 0), up=(0.0, 1.0, 0.0), height=2500))
    set_robot_visible(False, doc)
    set_visible(doc, MACHINE, False)
    out.append(save_view("6_mast_carriage_LA36.png", (-1.0, 0.9, -0.5), target=(0, -980, 620), height=1250))
    out.append(save_view("7_mast_from_the_robot.png", (0.3, -1.0, -0.35), target=(0, -980, 620), height=1250))
    set_pose(P.travel, doc)
    out.append(save_view("8_carriage_up.png", (-1.0, 0.9, -0.5), target=(0, -980, 700), height=1250))
    set_pose(doc=doc)
    set_visible(doc, MACHINE, True)
    for g in ("TPL_Mount", "TPL_Carriage", "TPL_Actuator"):
        set_visible(doc, g, False)
    out.append(save_view("9_demo_machine.png", (1.0, 1.0, -0.6), target=(0, -1450, 350), height=1500))
    App.closeDocument(doc.Name)
    build()
    return out
