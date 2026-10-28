"""Model of the fertilizer spreader on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_fsp
    build_fsp.build()                    # saves FCStd and STEP
    build_fsp.set_disc(30)               # turn the disc (degrees)
    build_fsp.check_interference()       # overlap (must be empty)
    build_fsp.check_holes()              # bolts and shafts in their holes
    build_fsp.clearance()                # smallest distance to the rear tyres and wheel units
    build_fsp.mass_properties()          # empty and full hopper
    build_fsp.render_all()               # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fsp_params as P
import fsp_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Fertilizer_Spreader"
SAVE_BASE = os.path.join(FOLDER, "Fertilizer_Spreader")
ROOT = "Fertilizer_spreader"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "stainless": (0.86, 0.87, 0.88),
    "hopper": (0.20, 0.45, 0.80),
    "lid": (0.12, 0.30, 0.60),
    "motor": (0.08, 0.08, 0.08),
    "roller": (0.95, 0.75, 0.10),
    "ballast": (0.35, 0.36, 0.38),
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



def disc_placement(deg):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), deg), V(0, P.disc_y, 0))


def build_into(doc, parent=None):
    """Put the spreader in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "fertilizer_spreader_simple")
    mount = new_part(doc, root, "Mount", "mount_rails_on_upper_beams")
    add_shape(doc, mount, "rails", "rails_40x40x3_L940", G.rails(), "frame")
    add_shape(doc, mount, "spacers", "rail_spacers_40x40x25", G.spacers(), "frame")
    add_shape(doc, mount, "rail_bolts", "rail_bolts_M10", G.rail_bolts(), "zinc")
    add_shape(doc, mount, "posts", "hopper_posts_40x40x3", G.posts(), "frame")
    add_shape(doc, mount, "ring", "hopper_ring_angle_40x40x4", G.ring(), "frame")
    hop = new_part(doc, root, "Hopper", "hopper_%dl" % round(P.hopper_volume()))
    add_shape(doc, hop, "hopper", "hopper_PE_%dl" % round(P.hopper_volume()), G.hopper(), "hopper")
    add_shape(doc, hop, "lid", "hopper_lid_PE", G.lid(), "lid")
    met = new_part(doc, root, "Metering", "metering_fluted_roller")
    add_shape(doc, met, "housing", "metering_housing_3mm_stainless", G.housing(), "stainless")
    add_shape(doc, met, "roller", "fluted_roller_D%dx%d_%d_flutes" % (P.roller_d, P.roller_len, P.flutes), G.roller(),
              "roller")
    add_shape(doc, met, "meter_motor", "metering_gearmotor_12V", G.meter_motor(), "motor")
    add_shape(doc, met, "chute", "drop_chute_stainless", G.chute(), "stainless")
    spin = new_part(doc, root, "Spinner", "spinner")
    add_shape(doc, spin, "spinner_frame", "spinner_frame_40x40_weldment", G.spinner_frame(), "frame")
    add_shape(doc, spin, "spin_motor", "spinner_motor_48V_BLDC_300W", G.spin_motor(), "motor")
    add_shape(doc, spin, "guard", "throw_guard_2mm", G.guard(), "stainless")
    add_shape(doc, spin, "guard_straps", "guard_straps_30x5_tabs", G.guard_straps(), "frame")
    add_shape(doc, spin, "strap_bolts", "guard_strap_bolts_M10", G.strap_bolts(), "zinc")
    rotor = new_part(doc, spin, "Disc", "disc_turns", disc_placement(0.0))
    add_shape(doc, rotor, "disc", "spinner_disc_D%d_stainless" % P.disc_d, G.disc(), "stainless")
    add_shape(doc, rotor, "vanes", "vanes_4x_h%d" % P.vane_h, G.vanes(), "stainless")
    bal = new_part(doc, root, "Counterweight", "counterweight_front_2x20kg_for_a_full_hopper")
    add_shape(doc, bal, "ballast", "counterweight_blocks", G.ballast(), "ballast")
    add_shape(doc, bal, "ballast_bolts", "counterweight_bolts_M10", G.ballast_bolts(), "zinc")
    return root


def set_disc(deg, doc=None):
    active_doc(doc).getObject("Disc").Placement = disc_placement(deg)


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


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Fertilizer spreader simple"
    doc.Comment = ("Generated by build_fsp.py from fsp_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0.")
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


# bolts and shafts pass through holes in the parts they join: those pairs are by design
JOINTS = {("rail_bolts", "rails"), ("rail_bolts", "spacers"), ("roller", "housing"), ("strap_bolts", "guard_straps"),
          ("spin_motor", "disc"), ("ballast_bolts", "ballast")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    pair = {a, b}
    return ("rail_bolts" in pair and any(n.startswith("upper_beam") for n in pair)) or \
           (pair & {"strap_bolts", "ballast_bolts"} and any(n.startswith("lower_beam") for n in pair))


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3): spreader parts among themselves and against the robot (bolts in their holes skipped)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """Bolts and shafts must sit in holes: overlap of the JOINTS pairs (should be ~0)."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    out = {}
    for a, b in JOINTS:
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[(a, b)] = round(v, 1)
    return out


def clearance(doc=None):
    """Smallest distance (mm) of the spreader to the rear tyres and rear wheel units."""
    doc = active_doc(doc)
    targets = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith(("RL_", "RR_"))]
    best = (1e9, None)
    for o in objects_of(doc, ROOT):
        if o.Name in ("rail_bolts", "spacers", "rails"):
            continue
        s = global_shape(o)
        for t in targets:
            d = s.distToShape(t)[0]
            if d < best[0]:
                best = (d, o.Name)
    return round(best[0], 1), best[1]


MASS_FIXED = {"meter_motor": P.m_meter_motor, "spin_motor": P.m_spin_motor}
DENSITY = (("hopper", P.pe), ("lid", P.pe))


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key, m in MASS_FIXED.items():
        if obj.Name.startswith(key):
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
    """Mass (kg) and centre of gravity of the spreader (without counterweight), empty and with a full hopper
    (fill_density), and of the counterweight."""
    doc = active_doc(doc)
    bal = {o.Name for o in objects_of(doc, "Counterweight")}
    m, c = sum_mass([o for o in objects_of(doc, ROOT) if o.Name not in bal])
    mb, cb = sum_mass(objects_of(doc, "Counterweight"))
    vol_l = P.hopper_volume()
    inner = G._hopper_solid(0.0).Solids
    fc = sum((s.CenterOfMass * s.Volume for s in inner), V(0, 0, 0)) * (1.0 / sum(s.Volume for s in inner))
    mf = vol_l * P.fill_density
    cf = (c * m + fc * mf) * (1.0 / (m + mf))
    return {"empty_kg": round(m, 1), "empty_cg": (round(c.x), round(c.y), round(c.z)),
            "volume_l": round(vol_l, 1), "fill_kg": round(mf, 1), "full_kg": round(m + mf, 1),
            "full_cg": (round(cf.x), round(cf.y), round(cf.z)), "ballast_kg": round(mb, 1), "ballast_cg_y": round(cb.y)}


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
    add_floor(doc, y=(-1600.0, 900.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.2, -0.7), target=(0, -500, 500)))
    out.append(save_view("2_side.png", (1.0, 0.0, 0.0), target=(0, -400, 550), height=1600))
    remove(doc, [GROUND])
    out.append(save_view("3_top.png", (0.0, 0.0, -1.0), target=(0, -400, 0), up=(0.0, 1.0, 0.0), height=2000))
    out.append(save_view("4_rear.png", (0.0, 1.0, -0.1), target=(0, -500, 550), height=1300))
    set_robot_visible(False, doc)
    for n in ("hopper", "lid", "ring"):
        doc.getObject(n).ViewObject.Transparency = 70
    out.append(save_view("5_metering_spinner_detail.png", (-1.0, 0.8, -0.5), target=(0, -880, 520), height=700))
    App.closeDocument(doc.Name)
    build()
    return out
