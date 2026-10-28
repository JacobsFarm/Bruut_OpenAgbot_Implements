"""Model of the mulch layer on the three-point hitch of the Bruut OpenAgbot (standard robot).
The hitch (toolbar, links, lift rods) is built by build_tph from "three point hitch/simple"; this file adds the
implement and the foil.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_mly
    build_mly.build()                      # saves FCStd and STEP (work pose, foil laid)
    build_mly.set_pose(25)                 # lift of the lower links (deg, + = up); the foil is hidden when lifted
    build_mly.check_interference()         # overlap in the current pose (must be empty)
    build_mly.check_poses()                # overlap over the lift poses (must be empty)
    build_mly.ground_contact()             # press wheels and discs in work and transport
    build_mly.clearance()                  # distance of the implement to the rear tyres
    build_mly.mass_properties()
    build_mly.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mly_params as P
import mly_parts as G
import build_tph as H

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Mulch_Layer"
SAVE_BASE = os.path.join(FOLDER, "Mulch_Layer")
ROOT = "Mulch_layer"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "rubber": (0.10, 0.10, 0.10),
    "foil": (0.08, 0.08, 0.09),
    "card": (0.70, 0.55, 0.35),
    "soil": (0.42, 0.30, 0.20),
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







def build_implement(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Implement", "mulch_layer_cat0", H.implement_placement(lift))
    add_shape(doc, grp, "frame", "frame_toolbar_60x60_A_mast_side_beams_50x50", G.frame(), "frame")
    add_shape(doc, grp, "hitch_pins", "hitch_pins_D16_linch", G.hitch_pins(), "zinc")
    add_shape(doc, grp, "roll", "foil_roll_%d_D%d" % (P.foil_w, P.roll_d), G.roll(), "foil")
    add_shape(doc, grp, "roll_core", "roll_core_D76_cone_chucks", G.roll_core(), "card")
    add_shape(doc, grp, "roll_shaft", "roll_shaft_D25", G.roll_shaft(), "zinc")
    drum, band = G.brake()
    add_shape(doc, grp, "brake_drum", "brake_drum_D120", drum, "steel")
    add_shape(doc, grp, "brake_band", "brake_band_spring", band, "rubber")
    add_shape(doc, grp, "guide_bar", "guide_bar_D40", G.guide_bar(), "zinc")
    add_shape(doc, grp, "press_wheels", "press_wheels_D%dx%d_2x" % (P.press_d, P.press_w), G.press_wheels(), "rubber")
    add_shape(doc, grp, "press_rims", "press_wheel_rims_steel", G.press_rims(), "steel")
    arms, axles = G.press_arms()
    add_shape(doc, grp, "press_arms", "press_wheel_arms_10mm", arms, "frame")
    add_shape(doc, grp, "press_axles", "press_wheel_axles_D20", axles, "zinc")
    add_shape(doc, grp, "discs", "covering_discs_D%d_2x" % P.disc_d, G.discs(), "steel")
    add_shape(doc, grp, "disc_arms", "covering_disc_arms_stub_D30", G.disc_arms(), "frame")
    return grp


def build_field(doc, parent):
    grp = new_part(doc, parent, "Field", "foil_and_soil_ridges")
    add_shape(doc, grp, "foil", "mulch_foil_%d" % P.foil_w, G.foil(), "foil")
    add_shape(doc, grp, "ridges", "soil_ridges_on_the_edges", G.ridges(), "soil")
    return grp


def build_into(doc, parent=None, lift=P.lift_work):
    """Put the three-point hitch (from "three point hitch/simple") and the mulch layer in a document."""
    root = new_part(doc, parent, ROOT, "mulch_layer_simple_on_three_point_hitch")
    hitch = new_part(doc, root, "Hitch", "three_point_hitch_cat0")
    H.build_mount(doc, hitch)
    H.build_links(doc, hitch, lift)
    H.build_actuators(doc, hitch, lift)
    build_implement(doc, root, lift)
    build_field(doc, root)
    return root


def set_pose(lift=P.lift_work, doc=None):
    """Lift angle of the lower links (deg, + = up): hitch and implement; the foil is only shown in work."""
    doc = active_doc(doc)
    H.set_pose(lift, doc)
    set_field(abs(lift - P.lift_work) < 0.1, doc)


def set_field(visible=True, doc=None):
    doc = active_doc(doc)
    for o in objects_of(doc, "Field"):
        o.ViewObject.Visibility = visible


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


def build(save=True, show_robot=False, step=True, lift=P.lift_work):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Mulch layer simple"
    doc.Comment = ("Generated by build_mly.py from mly_params.py (hitch from three point hitch/simple). Robot coordinates: "
                   "x = right, y = driving direction (front = +y), z = up, ground = z 0. Work pose; build_mly.set_pose() lifts.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, lift)
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




# hitch joints (pins in their lugs, actuator rods) plus the implement's own: pins, shafts and axles in their holes,
# the foil touching roll, guide bar and press wheels
JOINTS = {pair for pair in H.JOINTS if "tine" not in pair[0] + pair[1] and "imp_frame" not in pair
          and "gauge" not in pair[0] + pair[1] and "wheel_axles" not in pair}
JOINTS |= {("hitch_pins", "frame"), ("hitch_pins", "lower_link_left"), ("hitch_pins", "lower_link_right"),
           ("hitch_pins", "top_link"), ("roll_shaft", "frame"), ("roll_shaft", "roll_core"),
           ("roll_shaft", "brake_drum"), ("brake_drum", "brake_band"), ("roll", "roll_core"), ("guide_bar", "frame"),
           ("press_axles", "press_rims"), ("press_rims", "press_wheels"), ("press_axles", "press_arms"), ("press_arms", "frame"),
           ("disc_arms", "discs"), ("disc_arms", "frame"), ("foil", "guide_bar"), ("foil", "roll"),
           ("foil", "press_wheels"), ("ridges", "foil"), ("ridges", "discs")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    return (a.startswith("hanger_bolts") and b.startswith("lower_beam")) or \
        (b.startswith("hanger_bolts") and a.startswith("lower_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: hitch, implement and foil among themselves and against the robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT) if o.ViewObject.Visibility]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    """Over the lift poses: links, actuators and implement against the fixed parts and each other. Must be empty."""
    doc = active_doc(doc)
    moving = objects_of(doc, "Links") + objects_of(doc, "Actuator") + objects_of(doc, "Implement")
    names = {o.Name for o in moving} | {o.Name for o in objects_of(doc, "Field")}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for lift in P.LIFT_POSES:
        set_pose(lift, doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[lift] = hits
    set_pose(P.lift_work, doc)
    return out


def ground_contact(doc=None):
    """Lowest point (z) of the press wheels and discs in work and transport, and the pitch of the implement."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, doc)
        out[lift] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1) for n in ("press_wheels", "discs")}
        out[lift]["pitch_deg"] = round(H.P.linkage(lift)[2], 1)
    set_pose(P.lift_work, doc)
    return out


def clearance(doc=None):
    """Smallest distance (mm) of the implement to the rear tyres (lugged model tyres) in work and transport."""
    doc = active_doc(doc)
    tyres = [Part.makeCylinder(265.0, 100.0, V(sx * 375.0 - 50.0, -500.0, 215.0), V(1, 0, 0)) for sx in (-1, 1)]
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, doc)
        best = (1e9, None)
        for o in objects_of(doc, "Implement"):
            s = global_shape(o)
            for t in tyres:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name)
        out[lift] = (round(best[0], 1), best[1])
    set_pose(P.lift_work, doc)
    return out


MASS_FIXED = {"roll": P.roll_mass(), "roll_core": 1.2, "act_body_left": H.P.act_kg - 0.6, "act_rod_left": 0.6,
              "act_body_right": H.P.act_kg - 0.6, "act_rod_right": 0.6, "foil": 0.0, "ridges": 0.0}
DENSITY = (("toolbar_caps", 0.95e-6), ("press_wheels", P.rubber * 0.5), ("brake_band", P.rubber))


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
    """Mass (kg) and centre of gravity (robot coordinates) of the hitch with the mulch layer, the hitch and the implement (with a full roll)."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Hitch", "Implement"):
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
    add_floor(doc, y=(-2300.0, 900.0), x=(-1100.0, 1100.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.3, -0.7), target=(0, -900, 350)))
    out.append(save_view("2_side_work.png", (-1.0, 0.0, 0.0), target=(0, -1100, 400), height=1700))
    set_pose(P.lift_transport, doc)
    out.append(save_view("3_side_transport.png", (-1.0, 0.0, 0.0), target=(0, -1100, 400), height=1700))
    set_pose(P.lift_work, doc)
    remove(doc, [GROUND])
    out.append(save_view("4_top_work.png", (0.0, 0.0, -1.0), target=(0, -1000, 0), up=(0.0, 1.0, 0.0), height=2600))
    set_robot_visible(False, doc)
    out.append(save_view("5_rear_view.png", (0.0, 1.0, 0.0), target=(0, -1500, 300), height=900))
    out.append(save_view("6_iso_front_left_implement.png", (1.0, -0.9, -0.6), target=(0, -1600, 250), height=1500))
    App.closeDocument(doc.Name)
    build()
    return out
