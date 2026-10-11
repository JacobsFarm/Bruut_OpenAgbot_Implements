"""Model of the irrigation hose reel on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_irr
    build_irr.build()                              # saves FCStd and STEP (reel full, hose to the ground)
    build_irr.set_hose(l_reel=40.0)                # amount of hose on the reel (m): coil, run and reel angle follow
    build_irr.check_interference()                 # overlap (must be empty)
    build_irr.check_fit()                          # overlap with the reel turned over a full turn (must be empty)
    build_irr.clearance()                          # smallest distance to the robot per group
    build_irr.mass_properties()
    build_irr.render_all()                         # all images in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import irr_params as P
import irr_calc as C
import irr_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Irrigation_Hose_Reel"
SAVE_BASE = os.path.join(FOLDER, "Irrigation_Hose_Reel")
ROOT = "Hose_reel"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "alu": (0.80, 0.81, 0.83),
    "pe": (0.12, 0.12, 0.13),
    "pu": (0.95, 0.75, 0.15),
    "motor": (0.08, 0.08, 0.08),
    "gearbox": (0.25, 0.30, 0.38),
    "bearing": (0.30, 0.32, 0.35),
    "chain": (0.35, 0.35, 0.37),
    "box": (0.55, 0.57, 0.60),
    "spring": (0.30, 0.30, 0.32),
    "hose": (0.10, 0.35, 0.80),
    "sensor": (0.85, 0.65, 0.10),
}


# ---------------------------------------------------------------------
# Tree helpers (same as build_mrk.py)
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
# State: hose on the reel (m) -> reel angle, coil, run
# ---------------------------------------------------------------------
def reel_placement(angle_deg):
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), angle_deg), V(0, P.reel_y, P.reel_z))


def reel_angle_deg(l_reel):
    """Paying out turns the reel so that the bottom moves to the rear (-y): about +x that is a negative angle...
    winding is the opposite. Angle 0 = reel full."""
    return math.degrees(C.reel_angle(P.hose_len) - C.reel_angle(l_reel))


def set_hose(l_reel=P.hose_len, doc=None, tail_y=-2600.0):
    doc = active_doc(doc)
    doc.getObject("Reel").Placement = reel_placement(reel_angle_deg(l_reel))
    doc.getObject("hose_coil").Shape = G.coil(max(l_reel, 0.0))
    doc.getObject("hose_run").Shape = Part.makeCompound(G.hose_run(l_reel, tail_y=tail_y))
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_cradle_tubes_on_upper_beams")
    add_shape(doc, grp, "cradle_tubes", "cradle_tubes_40x40x3_L920", G.cradle_tubes(), "zinc")
    add_shape(doc, grp, "cradle_bolts", "cradle_bolts_8xM10", G.cradle_bolts(), "zinc")
    add_shape(doc, grp, "foot_bolts", "foot_bolts_8xM10", G.foot_bolts(), "zinc")
    return grp


def build_frame(doc, parent):
    grp = new_part(doc, parent, "Frame", "frame_stands_welded")
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "side_plate_" + tag, "side_plate_6mm_" + tag, G.side_plate(sx), "frame")
        add_shape(doc, grp, "feet_" + tag, "feet_10mm_welded_" + tag, G.feet(sx), "frame")
        add_shape(doc, grp, "ucf_" + tag, "bearing_UCF205_" + tag, G.ucf_bearing(sx), "bearing")
    add_shape(doc, grp, "tie_tubes", "tie_tubes_30x3_welded", G.tie_tubes(), "frame")
    add_shape(doc, grp, "ucf_bolts", "bearing_bolts_8xM10", G.ucf_bolts(), "zinc")
    add_shape(doc, grp, "control_box", "control_box_motor_driver_radio", G.control_box(), "box")
    return grp


def build_reel(doc, parent, angle_deg=0.0):
    grp = new_part(doc, parent, "Reel", "reel_rotates_about_x", reel_placement(angle_deg))
    add_shape(doc, grp, "shaft", "reel_shaft_D25", G.shaft(), "steel")
    add_shape(doc, grp, "core", "reel_core_PE_315_SDR17", G.core(), "pe")
    add_shape(doc, grp, "flanges", "reel_flanges_alu_4mm_D900", G.flanges(), "alu")
    add_shape(doc, grp, "tie_rods", "reel_tie_rods_6xM10", G.tie_rods(), "zinc")
    add_shape(doc, grp, "hubs", "reel_hubs_weld_on", G.hubs(), "steel")
    add_shape(doc, grp, "hub_bolts", "reel_hub_bolts_8xM8", G.hub_bolts(), "zinc")
    add_shape(doc, grp, "sprocket_big", "sprocket_08B_36T", G.sprocket_big(), "steel")
    return grp


def build_drive(doc, parent):
    grp = new_part(doc, parent, "Drive", "drive_worm_gearmotor_chain")
    add_shape(doc, grp, "standoffs", "motor_standoffs_30_welded", G.standoffs(), "frame")
    add_shape(doc, grp, "motor_bracket", "motor_bracket_8mm", G.motor_bracket(), "frame")
    add_shape(doc, grp, "gearmotor", "gearmotor_48V_350W_worm_100rpm", G.gearmotor(), "gearbox")
    add_shape(doc, grp, "sprocket_small", "sprocket_08B_12T", G.sprocket_small(), "steel")
    add_shape(doc, grp, "chain", "chain_08B", G.chain(), "chain")
    return grp


def build_pinch(doc, parent):
    grp = new_part(doc, parent, "Pinch", "pinch_rollers_and_guide")
    add_shape(doc, grp, "roller_bottom", "pinch_roller_bottom_D80_PU", G.roller(P.pinch_z_bottom), "pu")
    add_shape(doc, grp, "roller_top", "pinch_roller_top_D80_PU", G.roller(P.pinch_z_top), "pu")
    add_shape(doc, grp, "roller_low", "guide_roller_low_D80_PU", G.roller(P.low_z, P.low_d), "pu")
    add_shape(doc, grp, "roller_shafts", "roller_shafts_D20",
              [G.roller_shaft(P.pinch_z_bottom), G.roller_shaft(P.pinch_z_top), G.low_shaft()], "steel")
    add_shape(doc, grp, "pinch_bearings", "pinch_bearings_UCFL204", G.pinch_bearings(), "bearing")
    add_shape(doc, grp, "top_blocks", "top_roller_sliding_blocks", G.top_blocks(), "steel")
    add_shape(doc, grp, "springs", "pinch_springs_30Nmm", G.springs(), "spring")
    add_shape(doc, grp, "spring_brackets", "spring_brackets_angle_6mm", G.spring_brackets(), "frame")
    add_shape(doc, grp, "spring_bolts", "spring_bolts_M10_M8", G.spring_bolts(), "zinc")
    add_shape(doc, grp, "low_bushings", "guide_roller_bushings", G.low_bushings(), "bearing")
    add_shape(doc, grp, "encoder", "length_encoder", G.encoder(), "sensor")
    return grp


def build_hose(doc, parent, l_reel, tail_y=-2600.0):
    grp = new_part(doc, parent, "Hose", "hose_3in_layflat")
    add_shape(doc, grp, "hose_coil", "hose_coil_on_reel", G.coil(l_reel), "hose")
    add_shape(doc, grp, "hose_run", "hose_run_coil_to_ground", G.hose_run(l_reel, tail_y=tail_y), "hose")
    return grp


def build_into(doc, parent=None, l_reel=P.hose_len, tail_y=-2600.0):
    """Put the hose reel in a document, in robot coordinates (also used by animate_irr.py)."""
    root = new_part(doc, parent, ROOT, "irrigation_hose_reel")
    build_mount(doc, root)
    build_frame(doc, root)
    build_reel(doc, root, reel_angle_deg(l_reel))
    build_drive(doc, root)
    build_pinch(doc, root)
    build_hose(doc, root, l_reel, tail_y)
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


def build(l_reel=P.hose_len, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Irrigation hose reel"
    doc.Comment = ("Generated by build_irr.py from irr_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Hose on the reel: build_irr.set_hose(l_reel).")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, l_reel)
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
    raise RuntimeError("no hose reel document open")


def reel_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in reel_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in reel_objects(doc):
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


EXCLUDE = ("hose_",)            # compliant: the flat hose is squeezed between the rollers and lies on the core


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


def _checked(objs):
    return [o for o in objs if not o.Name.startswith(EXCLUDE)]


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3): reel parts among themselves and against the (visible and hidden) robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in _checked(reel_objects(doc))]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def check_fit(doc=None, steps=12, tol=1.0):
    """Turn the reel over a full turn in steps; check the rotating parts against everything else. Must be empty."""
    doc = active_doc(doc)
    reel = [o for o in doc.getObject("Reel").OutListRecursive if o.TypeId == "Part::Feature"]
    names = {o.Name for o in reel}
    fixed = [(o, global_shape(o)) for o in _checked(reel_objects(doc)) if o.Name not in names]
    fixed += [(o, global_shape(o)) for o in robot_objects(doc)]
    out = {}
    pl0 = doc.getObject("Reel").Placement
    for i in range(steps):
        ang = 360.0 * i / steps
        doc.getObject("Reel").Placement = reel_placement(ang)
        doc.recompute()
        mv = [(o, global_shape(o)) for o in reel]
        hits = _overlaps([(a, b) for a in mv for b in fixed], tol)
        if hits:
            out[ang] = hits
    doc.getObject("Reel").Placement = pl0
    doc.recompute()
    return out


def _near(sa, sb, margin):
    bb = sa.BoundBox
    bb.enlarge(margin)
    return bb.intersect(sb.BoundBox)


def _min_dist(shapes, targets, margin=150.0):
    """Smallest distance between two lists of (name, shape); only pairs whose boxes come within margin."""
    best = (1e9, None, None)
    for na, sa in shapes:
        for nb, sb in targets:
            if not _near(sa, sb, margin):
                continue
            d = sa.distToShape(sb)[0]
            if d < best[0]:
                best = (d, na, nb)
    return best


def hose_check(doc=None):
    """Smallest distance (mm) of the hose run to the frame and robot (except the rollers it runs over and the core),
    for an empty and a full reel."""
    doc = active_doc(doc)
    skip = ("roller_", "hose_", "core", "flanges")
    targets = [(o.Name, global_shape(o)) for o in _checked(reel_objects(doc)) + robot_objects(doc)
               if not o.Name.startswith(skip)]
    out = {}
    for l_reel in (P.reel_reserve, P.hose_len):
        set_hose(l_reel, doc, tail_y=None)
        best = _min_dist([("hose_run", global_shape(doc.getObject("hose_run")))], targets)
        out[l_reel] = (round(best[0], 1), best[2])
    set_hose(P.hose_len, doc)
    return out


def clearance(doc=None):
    """Smallest distance (mm) of each group of the implement to the robot."""
    doc = active_doc(doc)
    robot = [(o.Name, global_shape(o)) for o in robot_objects(doc)]
    if not robot:
        return {}
    out = {}
    for grp in ("Mount", "Frame", "Reel", "Drive", "Pinch"):
        objs = [o for o in doc.getObject(grp).OutListRecursive if o.TypeId == "Part::Feature"]
        if grp == "Mount":
            objs = [o for o in objs if o.Name.startswith("foot_bolts")]
        best = _min_dist([(o.Name, global_shape(o)) for o in objs], robot)
        out[grp] = (round(best[0], 1), best[1], best[2])
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
def _hose_kg(l_reel):
    n = len([s for s in C.outlets(P.hose_len) if s > P.hose_len - l_reel])
    return P.hose_kg_per_m * l_reel + n * P.outlet_kg


MASS_FIXED = {"gearmotor": P.motor_kg, "control_box": 2.5, "encoder": 0.3, "springs": 0.1, "chain": 0.6,
              "ucf_": 1.1, "pinch_bearings": 1.6, "low_bushings": 0.3}
DENSITY = (("flanges", 2.7e-6), ("core", 0.95e-6), ("hose_run", 1.25e-6))
STEEL = 7.85e-6


def _mass_cg(obj, l_reel):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    if obj.Name.startswith("hose_coil"):
        return _hose_kg(l_reel), cg
    for key, m in MASS_FIXED.items():
        if obj.Name.startswith(key):
            return m, cg
    dens = STEEL
    for key, d in DENSITY:
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def _sum(objs, l_reel):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o, l_reel)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None, l_reel=P.hose_len):
    """Mass (kg) and centre of gravity (robot coordinates): total and per group. Hose empty."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(reel_objects(doc), l_reel)
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for name in ("Mount", "Frame", "Reel", "Drive", "Pinch", "Hose"):
        out[name.lower() + "_kg"] = round(_sum(objs_of(name), l_reel)[0], 1)
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in reel_objects(doc):
        if o.Name == "hose_run":
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
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, -300, 900)
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


def add_floor(doc, y=(-3000.0, 1000.0), x=(-1000.0, 1000.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.62, 0.70, 0.52)
    obj.ViewObject.Transparency = 30
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
    add_floor(doc)
    out.append(save_view("1_full_reel_iso_on_robot.png", (1.0, 1.1, -0.65), target=(0, -600, 700)))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, -900, 850), height=2200))
    out.append(save_view("3_rear_on_robot.png", (0.0, 1.0, -0.12), target=(0, -800, 850), height=1900))
    remove(doc, [GROUND])
    set_hose(P.reel_reserve, doc)
    add_floor(doc)
    out.append(save_view("4_laid_out_iso_rear.png", (-1.0, 1.0, -0.55), target=(0, -900, 700)))
    remove(doc, [GROUND])
    set_hose(P.hose_len, doc)
    set_robot_visible(False, doc)
    out.append(save_view("5_reel_iso_left.png", (1.0, -0.6, -0.45), target=(0, -350, 950)))
    set_visible(doc, ("side_plate_right", "ucf_right", "control_box", "spring_brackets", "spring_bolts",
                      "pinch_bearings", "top_blocks", "springs", "low_bushings", "encoder", "ucf_bolts", "feet_right"),
                False)
    out.append(save_view("6_hose_path_section.png", (-1.0, 0.0, 0.0), target=(0, -400, 750), height=1500))
    out.append(save_view("7_pinch_detail.png", (-1.0, 0.6, -0.3), target=(0, -790, 700), height=650))
    App.closeDocument(doc.Name)
    build()
    return out
