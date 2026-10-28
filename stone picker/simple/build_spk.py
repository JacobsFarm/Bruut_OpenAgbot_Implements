"""Model of the stone picker on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_spk
    build_spk.build()                      # saves FCStd and STEP (work pose)
    build_spk.set_pose(theta=85, door=25)  # link angle 55 (work) .. 85 (lifted), floor open 0 .. 25 degrees
    build_spk.check_interference()         # overlap in the current pose (must be empty)
    build_spk.check_poses()                # overlap over lift, door and steering poses (must be empty)
    build_spk.clearance()                  # smallest distance of the moving parts to the tyres
    build_spk.mass_properties()
    build_spk.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import spk_params as P
import spk_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Stone_Picker"
SAVE_BASE = os.path.join(FOLDER, "Stone_Picker")
ROOT = "Stone_picker"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "basket": (0.20, 0.45, 0.25),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "tine": (0.15, 0.15, 0.16),
    "motor": (0.25, 0.26, 0.28),
    "stone": (0.62, 0.58, 0.52),
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







def lift_placement(theta):
    dy, dz = P.frame_shift(theta)
    return App.Placement(V(0, dy, dz), App.Rotation())


def door_placement(door_deg):
    hy, hz = G.hinge()
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), door_deg), V(0, hy, hz))


def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_hangers_bearer")
    add_shape(doc, grp, "hanger_tops", "hanger_top_plates_10mm_4x", G.hanger_tops(), "frame")
    add_shape(doc, grp, "hanger_webs", "hanger_webs_10mm_4x", G.hanger_webs(), "frame")
    add_shape(doc, grp, "hanger_bolts", "hanger_bolts_M10_8x", G.hanger_bolts(), "zinc")
    add_shape(doc, grp, "upper_pins", "upper_link_pins_D16_4x", G.upper_pins(), "zinc")
    add_shape(doc, grp, "bearer", "bearer_40x40x3", G.bearer(), "frame")
    add_shape(doc, grp, "bearer_bolts", "bearer_bolts_M10_4x", G.bearer_bolts(), "zinc")
    add_shape(doc, grp, "act_lug", "lift_actuator_lug_2x8mm", G.act_lug(), "frame")
    return grp


def build_lift(doc, parent, theta=P.theta_work, door=0.0):
    grp = new_part(doc, parent, "Lift", "picker_frame_rotor_basket", lift_placement(theta))
    add_shape(doc, grp, "frame", "frame_weldment_side_beams_cross_tubes", G.frame(), "frame")
    add_shape(doc, grp, "lower_pins", "lower_link_pins_D16_4x", G.lower_pins(), "zinc")
    add_shape(doc, grp, "rotor_tube", "rotor_tube_D114x4_L%d" % P.rotor_len, G.rotor_tube(), "steel")
    add_shape(doc, grp, "tines", "spring_tines_D9_%dx%d_double" % (P.tine_rows, P.tines_per_row), G.tines(), "tine")
    add_shape(doc, grp, "rotor_shaft", "rotor_shaft_D25", G.rotor_shaft(), "zinc")
    add_shape(doc, grp, "rotor_bearings", "rotor_bearings_UCFL205_2x", G.rotor_bearings(), "motor")
    gm, arm = G.gearmotor()
    add_shape(doc, grp, "gearmotor", "rotor_gearmotor_48V_750W", gm, "motor")
    add_shape(doc, grp, "torque_arm", "gearmotor_torque_arm", arm, "frame")
    add_shape(doc, grp, "basket_walls", "basket_walls_3mm", G.basket_walls(), "basket")
    add_shape(doc, grp, "comb", "comb_bars_D12_13x", G.comb(), "zinc")
    add_shape(doc, grp, "deflectors", "side_deflectors_3mm", G.deflectors(), "basket")
    add_shape(doc, grp, "door_lug", "door_actuator_lug_2x6mm", G.door_lug(), "frame")
    add_shape(doc, grp, "stones", "stones_example", G.stones(), "stone")
    body, rod, _ = G.door_actuator(door)
    add_shape(doc, grp, "door_body", "door_actuator_24V_500N_body", body, "motor")
    add_shape(doc, grp, "door_rod", "door_actuator_rod", rod, "steel")
    dgrp = new_part(doc, grp, "Door", "sieve_floor_turns_about_hinge", door_placement(door))
    add_shape(doc, dgrp, "floor", "sieve_floor_bars_D12_gap_25", G.floor(), "zinc")
    return grp


def build_links(doc, parent, theta=P.theta_work):
    grp = new_part(doc, parent, "Links", "swing_links")
    add_shape(doc, grp, "links", "swing_links_40x8_L250_4x", G.links(theta), "frame")
    body, rod, _ = G.lift_actuator(theta)
    add_shape(doc, grp, "act_body", "lift_actuator_24V_1500N_stroke_150", body, "motor")
    add_shape(doc, grp, "act_rod", "lift_actuator_rod", rod, "steel")
    return grp


def build_into(doc, parent=None, theta=P.theta_work, door=0.0):
    """Put the stone picker in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "stone_picker_simple")
    build_mount(doc, root)
    build_links(doc, root, theta)
    build_lift(doc, root, theta, door)
    return root


def set_pose(theta=P.theta_work, door=0.0, doc=None):
    """theta: link angle (55 work .. 85 lifted); door: floor opening in degrees (0 .. door_open)."""
    doc = active_doc(doc)
    doc.getObject("Lift").Placement = lift_placement(theta)
    doc.getObject("Door").Placement = door_placement(door)
    doc.getObject("links").Shape = G.links(theta)
    body, rod, _ = G.lift_actuator(theta)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod
    body, rod, _ = G.door_actuator(door)
    doc.getObject("door_body").Shape = body
    doc.getObject("door_rod").Shape = rod


def set_stones(visible=True, doc=None):
    active_doc(doc).getObject("stones").ViewObject.Visibility = visible


def build_robot(doc, steer=0.0):
    """Real robot model from 'agbot design' (read only)."""
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, steer if tag in ("FL", "FR") else 0.0)
    return robot


def set_steering(deg, doc=None):
    doc = active_doc(doc)
    for n in ("FL_steered", "FR_steered"):
        o = doc.getObject(n)
        if o is not None:
            pl = o.Placement
            o.Placement = App.Placement(pl.Base, App.Rotation(V(0, 0, 1), deg))


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Stone picker simple"
    doc.Comment = ("Generated by build_spk.py from spk_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Work pose; build_spk.set_pose() lifts the frame and opens the floor.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    if robot is not None and not show_robot:
        set_robot_visible(False, doc)
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
    if g is None:
        return []
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"]


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


def _overlaps(pairs, tol):
    hits = []
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




# pins, bolts and shafts pass through holes in the parts they join, actuator rods run in their bodies, the stones lie
# on the floor bars: those pairs are by design
JOINTS = {("hanger_bolts", "hanger_tops"), ("bearer_bolts", "bearer"), ("upper_pins", "hanger_webs"),
          ("upper_pins", "links"), ("lower_pins", "links"), ("lower_pins", "frame"), ("rotor_shaft", "rotor_tube"),
          ("rotor_shaft", "frame"), ("rotor_shaft", "rotor_bearings"), ("rotor_shaft", "gearmotor"),
          ("tines", "rotor_tube"), ("act_body", "act_lug"), ("act_rod", "frame"), ("act_body", "act_rod"),
          ("door_body", "door_lug"), ("door_rod", "floor"), ("door_body", "door_rod"), ("floor", "basket_walls"),
          ("comb", "basket_walls"), ("stones", "floor")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    bolts = ("hanger_bolts", "bearer_bolts")
    return (a in bolts and b.startswith("upper_beam")) or (b in bolts and a.startswith("upper_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: picker parts among themselves and against the robot (JOINTS skipped)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Lift poses x door (closed / open) x steering: the moving parts against the rest and each other. Must be empty."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Lift") + objects_of(doc, "Links")
    names = {o.Name for o in moving}
    others = [o for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for st in steer:
        set_steering(st, doc)
        fixed = [(o, global_shape(o)) for o in others]
        for theta in P.THETA_POSES:
            for door in (0.0, P.door_open):
                if door and theta != P.theta_lift:
                    continue                        # the floor only opens lifted
                set_pose(theta, door, doc)
                mv = [(o, global_shape(o)) for o in moving]
                pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
                pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                          if not _joint(mv[i][0].Name, mv[j][0].Name)]
                hits = _overlaps(pairs, tol)
                if hits:
                    out[(st, theta, door)] = hits
    set_steering(0.0, doc)
    set_pose(P.theta_work, 0.0, doc)
    return out


def tyre_envelope(x, y, steer=0.0):
    """Plain cylinder for a tyre (radius of the lugged model tyre)."""
    c = V(x, y, P.robot_axle_z)
    t = Part.makeCylinder(P.robot_tire_r, P.robot_tire_w, c - V(P.robot_tire_w / 2.0, 0, 0), V(1, 0, 0))
    t.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return t


def clearance(doc=None, steer=(-P.robot_steer_deg, 0.0, P.robot_steer_deg)):
    """Smallest distance (mm) of the moving picker parts to the four tyres over lift poses and steering."""
    doc = active_doc(doc)
    names = ("frame", "rotor_tube", "tines", "rotor_bearings", "gearmotor", "basket_walls", "deflectors", "links",
             "floor", "door_body")
    best = (1e9, None, None)
    for st in steer:
        tyres = [tyre_envelope(sx * P.robot_wheel_x, sy * P.robot_axle_y, st if sy > 0 else 0.0)
                 for sx in (-1, 1) for sy in (-1, 1)]
        for theta in (P.theta_work, P.theta_lift):
            set_pose(theta, P.door_open if theta == P.theta_lift else 0.0, doc)
            for n in names:
                s = global_shape(doc.getObject(n))
                for t in tyres:
                    d = s.distToShape(t)[0]
                    if d < best[0]:
                        best = (d, n, (st, theta))
    set_pose(P.theta_work, 0.0, doc)
    return round(best[0], 1), best[1], best[2]


MASS_FIXED = {"gearmotor": 7.5, "rotor_bearings": 2 * 0.9, "act_body": 2.2, "act_rod": 0.5, "door_body": 1.2,
              "door_rod": 0.3, "stones": 0.0}
DENSITY = ()


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key, m in MASS_FIXED.items():
        if obj.Name == key:
            return m, cg
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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole picker and of each group (work pose, no stones)."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Mount", "Lift", "Links"):
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
def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.ActiveDocument.ActiveView
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


GROUND = "render_floor"


def add_floor(doc, y=(-900.0, 1800.0), x=(-1000.0, 1000.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.72, 0.72, 0.70)
    obj.ViewObject.Transparency = 30
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)





def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_floor(doc, y=(-900.0, 900.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_front_right_on_robot.png", (-1.0, -1.2, -0.6), target=(0, 0, 350)))
    out.append(save_view("2_side_work.png", (-1.0, 0.0, 0.0), target=(0, -50, 400), height=1500))
    set_pose(P.theta_lift, P.door_open, doc)
    out.append(save_view("3_side_lifted_open.png", (-1.0, 0.0, 0.0), target=(0, -50, 400), height=1500))
    set_pose(P.theta_work, 0.0, doc)
    set_robot_visible(False, doc)
    out.append(save_view("4_iso_rear_left_picker.png", (1.0, 1.1, -0.7), target=(0, -150, 250), height=1500))
    remove(doc, [GROUND])
    out.append(save_view("5_top_picker.png", (0.0, 0.0, -1.0), target=(0, -100, 0), up=(0.0, 1.0, 0.0), height=1500))
    doc.getObject("basket_walls").ViewObject.Visibility = False
    doc.getObject("deflectors").ViewObject.Visibility = False
    out.append(save_view("6_rotor_comb_detail.png", (-1.0, -0.6, -0.5), target=(150, -100, 150), height=800))
    App.closeDocument(doc.Name)
    build()
    return out
