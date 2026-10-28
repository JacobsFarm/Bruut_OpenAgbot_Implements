"""Model of the compost spreader on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_csp
    build_csp.build()                      # saves FCStd and STEP (bin full: 150 kg of moist green compost)
    build_csp.set_load(False)              # hide the compost
    build_csp.set_gate(30)                 # gate opening above the belt (mm), 30..150
    build_csp.check_interference()         # overlap (must be empty)
    build_csp.check_poses()                # overlap over the gate range (must be empty)
    build_csp.clearance()                  # smallest distance to the tyres, steering stacks and rear unit bolts
    build_csp.mass_properties()
    build_csp.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import csp_params as P
import csp_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Compost_Spreader"
SAVE_BASE = os.path.join(FOLDER, "Compost_Spreader")
ROOT = "Compost_spreader"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "bin": (0.20, 0.45, 0.25),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "rubber": (0.10, 0.10, 0.10),
    "uhmw": (0.95, 0.95, 0.92),
    "motor": (0.25, 0.26, 0.28),
    "plastic": (0.10, 0.10, 0.10),
    "compost": (0.30, 0.20, 0.12),
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







def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_bearers_on_upper_beams")
    add_shape(doc, grp, "bearers", "bearers_40x40x3_3x", G.bearers(), "frame")
    add_shape(doc, grp, "bearer_bolts", "bearer_bolts_M10_12x", G.bearer_bolts(), "zinc")
    add_shape(doc, grp, "feet", "feet_angle_40x40x4_6x", G.feet(), "frame")
    add_shape(doc, grp, "feet_bolts", "feet_bolts_M10_6x", G.feet_bolts(), "zinc")
    return grp


def build_conveyor(doc, parent):
    grp = new_part(doc, parent, "Conveyor", "floor_belt_conveyor")
    add_shape(doc, grp, "side_plates", "side_plates_4mm", G.side_plates(), "frame")
    add_shape(doc, grp, "bed_rails", "bed_rails_angle_20x20x4", G.bed_rails(), "frame")
    add_shape(doc, grp, "slide_bed", "slide_bed_UHMW_10mm", G.slide_bed(), "uhmw")
    add_shape(doc, grp, "drums", "drums_D%d_L%d" % (P.drum_d, P.drum_len), G.drums(), "steel")
    add_shape(doc, grp, "drum_shafts", "drum_shafts_D%d" % P.shaft_d, G.drum_shafts(), "zinc")
    add_shape(doc, grp, "drum_bearings", "drum_bearings_UCFL204_4x", G.drum_bearings(), "motor")
    add_shape(doc, grp, "belt", "floor_belt_%dx%d" % (P.belt_w, P.belt_t), G.belt(), "rubber")
    add_shape(doc, grp, "cross_tube", "cross_tube_40x40x3", G.cross_tube(), "frame")
    box, motor = G.belt_gearmotor()
    add_shape(doc, grp, "belt_gearbox", "belt_worm_gearbox_60_1", box, "motor")
    add_shape(doc, grp, "belt_motor", "belt_motor_24V_120W", motor, "motor")
    add_shape(doc, grp, "torque_arm", "torque_arm_50x8", G.torque_arm(), "frame")
    return grp


def build_bin(doc, parent):
    grp = new_part(doc, parent, "Bin", "bin_and_gate")
    add_shape(doc, grp, "flare_walls", "flare_walls_3mm", G.flare_walls(), "bin")
    add_shape(doc, grp, "front_wall", "front_wall_3mm", G.front_wall(), "bin")
    add_shape(doc, grp, "rear_wall", "rear_wall_3mm_over_gate", G.rear_wall(), "bin")
    add_shape(doc, grp, "skirts", "rubber_skirts_8mm", G.skirts(), "rubber")
    add_shape(doc, grp, "gate", "slide_gate_6mm", G.gate(), "zinc")
    add_shape(doc, grp, "gate_guides", "gate_guides_55x4", G.gate_guides(), "frame")
    add_shape(doc, grp, "gate_knobs", "gate_star_knobs_M10", G.gate_knobs(), "plastic")
    return grp


def build_beater(doc, parent):
    grp = new_part(doc, parent, "Beater", "beater_and_drive")
    add_shape(doc, grp, "beater_rotor", "beater_rotor_D114_paddles_tip_D280", G.beater_rotor(), "steel")
    add_shape(doc, grp, "beater_shaft", "beater_stub_shafts_D30", G.beater_shaft(), "zinc")
    add_shape(doc, grp, "beater_bearings", "beater_bearings_UCFL206_2x", G.beater_bearings(), "motor")
    add_shape(doc, grp, "hood", "deflector_hood_3mm", G.hood(), "bin")
    add_shape(doc, grp, "pulleys", "polyV_pulleys_D250_D50_alu", G.pulleys(), "steel")
    add_shape(doc, grp, "vbelt", "polyV_belt", G.vbelt(), "rubber")
    add_shape(doc, grp, "guard", "belt_guard", G.guard(), "bin")
    add_shape(doc, grp, "beater_motor", "beater_motor_48V_1kW", G.beater_motor(), "motor")
    return grp


def build_load(doc, parent):
    grp = new_part(doc, parent, "Load", "compost_load")
    add_shape(doc, grp, "compost_load", "compost_%dkg" % P.payload_max, G.compost_load(), "compost")
    return grp


def build_into(doc, parent=None):
    """Put the compost spreader in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "compost_spreader_simple")
    build_mount(doc, root)
    build_conveyor(doc, root)
    build_bin(doc, root)
    build_beater(doc, root)
    build_load(doc, root)
    return root


def set_load(visible=True, doc=None):
    doc = active_doc(doc)
    for o in objects_of(doc, "Load"):
        o.ViewObject.Visibility = visible


def set_gate(opening=P.gate_open, doc=None):
    doc = active_doc(doc)
    doc.getObject("gate").Shape = G.gate(opening)
    doc.getObject("gate_knobs").Shape = G.gate_knobs(opening)


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


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Compost spreader simple"
    doc.Comment = ("Generated by build_csp.py from csp_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Bin full; build_csp.set_load(False) hides the compost.")
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




# shafts, bolts and studs pass through holes in the parts they join; the belt lies on the drums and the bed, the
# skirts and the compost touch the walls: those pairs are by design
JOINTS = {("bearer_bolts", "bearers"), ("feet_bolts", "bearers"), ("feet_bolts", "feet"), ("feet", "side_plates"),
          ("drum_shafts", "drums"), ("drum_shafts", "side_plates"), ("drum_shafts", "drum_bearings"),
          ("drum_shafts", "belt_gearbox"), ("beater_shaft", "beater_rotor"), ("beater_shaft", "side_plates"),
          ("beater_shaft", "beater_bearings"), ("beater_shaft", "pulleys"), ("beater_shaft", "guard"),
          ("gate_knobs", "gate"), ("gate_knobs", "gate_guides"), ("compost_load", "skirts"),
          ("pulleys", "vbelt"), ("beater_motor", "guard")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    return (a == "bearer_bolts" and b.startswith("upper_beam")) or (b == "bearer_bolts" and a.startswith("upper_beam"))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3): spreader parts and load among themselves and against the robot (JOINTS skipped)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    """The gate and its knobs over the range against the rest (the only parts that change place). Must be empty."""
    doc = active_doc(doc)
    out = {}
    moving = ("gate", "gate_knobs")
    others = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in moving]
    for opening in P.GATE_RANGE:
        set_gate(opening, doc)
        mv = [(doc.getObject(n), global_shape(doc.getObject(n))) for n in moving]
        hits = _overlaps([(a, b) for a in mv for b in others if not _joint(a[0].Name, b[0].Name)], tol)
        if hits:
            out[opening] = hits
    set_gate(P.gate_open, doc)
    return out


def tyre_envelope(x, y, steer=0.0):
    """Plain cylinder O430 x 100 (the lugged tyre is far too slow for distToShape)."""
    c = V(x, y, P.robot_axle_z)
    t = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, c - V(P.robot_tire_w / 2.0, 0, 0), V(1, 0, 0))
    t.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return t


def clearance(doc=None):
    """Smallest distance (mm) of the spreader to the rear tyres, the front steering stacks and the rear unit bolts."""
    doc = active_doc(doc)
    targets = [("tyre", tyre_envelope(sx * P.robot_wheel_x, -P.robot_axle_y)) for sx in (-1, 1)]
    targets += [(o.Name, global_shape(o)) for o in robot_objects(doc)
                if o.Name.startswith(("FL_", "FR_", "RL_frame_bolts", "RR_frame_bolts"))
                and global_shape(o).BoundBox.ZMax > P.robot_upper_beam_z[1]]
    best = (1e9, None, None)
    for o in objects_of(doc, ROOT):
        if o.Name in ("bearer_bolts",):
            continue
        s = global_shape(o)
        for name, t in targets:
            if not s.BoundBox.isValid():
                continue
            d = s.distToShape(t)[0]
            if d < best[0]:
                best = (d, o.Name, name)
    return round(best[0], 1), best[1], best[2]


MASS_FIXED = {"belt_motor": 2.5, "belt_gearbox": 4.5, "beater_motor": 4.0, "drum_bearings": 4 * 0.9,
              "beater_bearings": 2 * 1.6, "gate_knobs": 0.3, "compost_load": P.payload_max}
DENSITY = (("slide_bed", P.uhmw), ("belt", P.rubber), ("skirts", P.rubber), ("vbelt", P.rubber), ("pulleys", P.alu))


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole spreader with load and of each group."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Mount", "Conveyor", "Bin", "Beater", "Load"):
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
    add_floor(doc, y=(-1500.0, 900.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.2, -0.8), target=(0, -250, 650)))
    out.append(save_view("2_side_full.png", (-1.0, 0.0, 0.0), target=(0, -300, 650), height=1700))
    set_load(False, doc)
    out.append(save_view("3_iso_front_left_empty.png", (1.0, -1.1, -0.9), target=(0, -300, 750)))
    remove(doc, [GROUND])
    out.append(save_view("4_top_empty.png", (0.0, 0.0, -1.0), target=(0, -300, 0), up=(0.0, 1.0, 0.0), height=2200))
    set_robot_visible(False, doc)
    out.append(save_view("6_beater_drive_rear.png", (-0.9, 1.0, -0.4), target=(300, -1000, 850), height=900))
    set_load(True, doc)
    for n in ("side_plates", "flare_walls", "skirts", "guard", "beater_motor", "pulleys", "vbelt", "drum_bearings",
              "beater_bearings", "feet", "feet_bolts", "bed_rails", "gate_guides", "gate_knobs"):
        doc.getObject(n).ViewObject.Visibility = False
    out.append(save_view("5_section_belt_beater.png", (-1.0, 0.0, 0.0), target=(0, -440, 870), height=1300))
    App.closeDocument(doc.Name)
    build()
    return out
