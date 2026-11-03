"""Model of the MBH3+ battery rack (open, 2, 3 or 4 drop-in batteries) on the Bruut OpenAgbot (standard robot), three ideas.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_bbx
    build_bbx.build("well", 2)             # concept top / well / saddle, number of batteries; saves FCStd and STEP
    build_bbx.check_interference()         # overlap (must be empty), front wheels at -30 / 0 / 30
    build_bbx.clearance()                  # smallest distance to the tyres (front steered +-30)
    build_bbx.mass_properties()
    build_bbx.build_placeholder(kind="MU3+")  # a battery placeholder alone (MBH3+ / MU3+): FCStd + STEP
    build_bbx.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bbx_params as P
import bbx_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
VENDOR_STEP = r"F:\veldrobot\Battery Labs\CAD\MBH3+_BSI_AS150U_mockup\MBH3+_BSI_AS150U_mockup.STEP"
ROOT = "Battery_box"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "alu": (0.70, 0.72, 0.75),
    "lid": (0.55, 0.58, 0.62),
    "battery": (0.88, 0.89, 0.90),
    "black": (0.10, 0.10, 0.10),
    "hdpe": (0.95, 0.95, 0.90),
    "rubber": (0.20, 0.20, 0.20),
    "yellow": (0.95, 0.80, 0.10),
    "wood": (0.80, 0.62, 0.40),
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


BAT_NAMES = {"MBH3+": ("bat", "MBH3plus"), "MU3+": ("batmu", "MU3plus")}


def add_batteries(doc, parent, bodies, tops, tag="", kind="MBH3+"):
    pre, lab = BAT_NAMES[kind]
    grp = new_part(doc, parent, "Batteries" + tag, "batteries_%s%s" % (lab, tag))
    for i, (b, t) in enumerate(zip(bodies, tops)):
        add_shape(doc, grp, "%s%s_%d" % (pre, tag, i + 1), "%s_placeholder%s_%d" % (lab, tag, i + 1), b, "battery")
        add_shape(doc, grp, "%stop%s_%d" % (pre, tag, i + 1), "%s_handle_AS150U%s_%d" % (lab, tag, i + 1), t, "black")
    return grp


# ---------------------------------------------------------------------
# Concepts
# ---------------------------------------------------------------------
def build_upright(doc, root, concept, n, k):
    """Top / well: n tray segments in one open rack, k batteries in it."""
    mount = new_part(doc, root, "Mount", "mount_cross_rails")
    add_shape(doc, mount, "rails", "cross_rail_tube_40x40x3_2x", G.rails(n, concept), "frame")
    add_shape(doc, mount, "rbolts", "rail_bolts_M10_4x", G.rail_bolts(n, concept), "zinc")
    rack = new_part(doc, root, "Rack", "open_rack_%d_slots" % n)
    add_shape(doc, rack, "trays", "tray_segments_alu_4mm_%dx" % n, G.trays(n, concept), "alu")
    add_shape(doc, rack, "frames", "end_frames_alu_tube_30x30_2x", G.end_frames(n, concept), "alu")
    add_shape(doc, rack, "guides", "side_guides_30x10_2x", G.guides(n, concept), "alu")
    add_shape(doc, rack, "mat", "floor_mat_rubber_10", G.floor_mat(n, concept), "rubber")
    if n > 1:
        add_shape(doc, rack, "seps", "separators_HDPE_12_%dx" % (n - 1), G.separators(n, concept), "hdpe")
    add_shape(doc, rack, "hold", "hold_down_bar_30x6_hinged", G.hold_down(n, concept), "lid")
    add_shape(doc, rack, "knob", "hold_down_star_knob", G.hold_knob(n, concept), "black")
    add_shape(doc, rack, "combiner", "combiner_box_AS150U_fuse_CAN", G.combiner_box(n, concept), "yellow")
    if concept == "well":
        add_shape(doc, rack, "ears", "hanging_ears_alu_5_2x", G.ears(n, concept), "alu")
    bodies, tops = G.batteries_upright(k, n, concept)
    add_batteries(doc, root, bodies, tops)


def build_saddle(doc, root, n):
    """Saddle: one cradle per side, n split 1 + 1 / 1 + 2 / 2 + 2."""
    for sx, tag, k in ((-1, "left", P.saddle_split(n)[0]), (1, "right", P.saddle_split(n)[1])):
        if k == 0:
            continue
        side = new_part(doc, root, "Side_" + tag, "saddle_cradle_%s_%d_slots" % (tag, k))
        add_shape(doc, side, "hangers_" + tag, "hangers_40x8_spacers_2x_" + tag, G.saddle_hangers(sx, k), "frame")
        add_shape(doc, side, "hbolts_" + tag, "hanger_bolts_M10_4x_" + tag, G.saddle_bolts(sx, k), "zinc")
        add_shape(doc, side, "knobs_" + tag, "star_knobs_M8_2x_" + tag, G.saddle_knobs(sx, k), "black")
        add_shape(doc, side, "cradle_" + tag, "cradle_plates_alu_4mm_" + tag, G.saddle_cradle(sx, k), "alu")
        add_shape(doc, side, "posts_" + tag, "end_posts_alu_tube_30x30_" + tag, G.saddle_posts(sx, k), "alu")
        add_shape(doc, side, "bars_" + tag, "retaining_bars_hinged_2x_" + tag, G.saddle_bars(sx, k), "lid")
        add_shape(doc, side, "fittings_" + tag, "latches_2x_" + tag, G.saddle_latches(sx, k), "black")
        add_shape(doc, side, "mat_" + tag, "floor_mat_rubber_10_" + tag, G.saddle_mat(sx, k), "rubber")
        if k > 1:
            add_shape(doc, side, "seps_" + tag, "separator_HDPE_12_" + tag, G.saddle_separator(sx, k), "hdpe")
        add_shape(doc, side, "combiner_" + tag, "combiner_box_" + tag, G.saddle_combiner(sx, k), "yellow")
        bodies, tops = G.saddle_batteries(sx, k)
        add_batteries(doc, side, bodies, tops, "_" + tag)


def build_cabinet(doc, root, concept, n, k):
    """Closed alu cabinet, n levels with a drop-down door each, k batteries lying flat from the bottom up."""
    mount = new_part(doc, root, "Mount", "mount_cross_rails")
    add_shape(doc, mount, "rails", "cross_rail_tube_40x40x3_2x", G.rails(n, concept), "frame")
    add_shape(doc, mount, "rbolts", "rail_bolts_M10_4x", G.rail_bolts(n, concept), "zinc")
    cab = new_part(doc, root, "Cabinet", "closed_cabinet_%d_levels" % n)
    add_shape(doc, cab, "shell", "cabinet_shell_alu_3mm_%d_levels" % n, G.cabinet_shell(n, concept), "alu")
    add_shape(doc, cab, "shelves", "shelves_alu_4_HDPE_strip_%dx" % n, G.cabinet_shelves(n, concept), "hdpe")
    add_shape(doc, cab, "doors", "drop_down_doors_alu_3_%dx" % n, G.cabinet_doors(n, concept), "lid")
    add_shape(doc, cab, "latches", "door_latches_%dx" % n, G.cabinet_latches(n, concept), "black")
    add_shape(doc, cab, "combiner", "combiner_box_AS150U_fuse_CAN", G.cabinet_combiner(n, concept), "yellow")
    if concept == "cabinet_well":
        add_shape(doc, cab, "ears", "hanging_ears_alu_5_4x", G.cabinet_ears(n, concept), "alu")
    bodies, tops = G.cabinet_batteries(k, n, concept)
    add_batteries(doc, root, bodies, tops)


def build_wood(doc, root, concept):
    """Wooden box with 2 compartments on the right upper beams, batteries upright, plugs up."""
    box = new_part(doc, root, "Wood_box", "wooden_box_multiplex_18_2_compartments")
    add_shape(doc, box, "wood_box", "box_bottom_walls_divider_multiplex_18", G.wood_box(concept), "wood")
    add_shape(doc, box, "wood_lid", "lid_multiplex_18", G.wood_lid(concept), "wood")
    add_shape(doc, box, "wfit", "hinges_hasp_handles", G.wood_fittings(concept), "black")
    add_shape(doc, box, "mat_wood", "mats_EPDM_5_2x", G.wood_mats(concept), "rubber")
    add_shape(doc, box, "wbolts", "box_bolts_M10_countersunk_4x", G.wood_bolts(concept), "zinc")
    bodies, tops = G.wood_batteries(concept)
    add_batteries(doc, root, bodies, tops, kind=P.WOOD[concept]["kind"])


def build_into(doc, concept, n, slots=None, parent=None):
    """Put the battery rack in a document, in robot coordinates. slots >= n leaves slots empty (upright only)."""
    kind = P.WOOD[concept]["kind"] if concept in P.WOOD else "MBH3+"
    root = new_part(doc, parent, ROOT, "battery_rack_%s_%s_%d" % (BAT_NAMES[kind][1], concept, n))
    if concept in P.WOOD:
        build_wood(doc, root, concept)
    elif concept.startswith("cabinet"):
        build_cabinet(doc, root, concept, slots or n, n)
    elif concept == "saddle":
        build_saddle(doc, root, n)
    else:
        build_upright(doc, root, concept, slots or n, n)
    return root


def set_steering(deg, doc=None):
    doc = active_doc(doc)
    for name in ("FL_steered", "FR_steered"):
        o = doc.getObject(name)
        if o is not None:
            pl = o.Placement
            o.Placement = App.Placement(pl.Base, App.Rotation(V(0, 0, 1), deg))


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


def doc_name(concept):
    return "Battery_Rack_" + concept


def build(concept="well", n=2, save=True, show_robot=False, step=True):
    name = doc_name(concept)
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    kind = P.WOOD[concept]["kind"] if concept in P.WOOD else "MBH3+"
    doc.Label = "Battery rack %s %s %d" % (kind, concept, n)
    doc.Comment = ("Generated by build_bbx.py from bbx_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Concept %s with %d %s batteries." % (concept, n, kind))
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, concept, n, parent=robot)
    if robot is not None and not show_robot:
        set_robot_visible(False, doc)
    doc.recompute()
    base = os.path.join(FOLDER, name)
    if save:
        doc.saveAs(base + ".FCStd")
    if step:
        export_step(doc, base + ".step")
    return doc


PLACEHOLDER_INFO = {
    "MBH3+": "BatteryLabs MBH3+ 14S 48 V 50 Ah, outer dimensions only (265 x 82 x 409.6). x = width, y = thickness",
    "MU3+": "BatteryLabs MegaUMPF3+ (MU3+) 14S 48 V 50 Ah, outer dimensions only (167 x 197 x 301.9 with the handle)",
}


def build_placeholder(save=True, kind="MBH3+"):
    """A battery placeholder alone (origin = centre of the bottom face, handle up), for other implements."""
    lab = BAT_NAMES[kind][1]
    name = lab + "_placeholder"
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    doc.Label = kind + " placeholder"
    doc.Comment = (PLACEHOLDER_INFO[kind] + ". Origin = centre of the bottom face, z = up. Generated by "
                   "build_bbx.build_placeholder().")
    root = new_part(doc, None, lab, name)
    body, top = G.battery_local(kind)
    add_shape(doc, root, "bat_body", lab + "_body", body, "battery")
    add_shape(doc, root, "bat_top", lab + "_handle_frame_AS150U", top, "black")
    doc.recompute()
    if save:
        base = os.path.join(FOLDER, name)
        doc.saveAs(base + ".FCStd")
        import Import
        Import.export([doc.getObject("bat_body"), doc.getObject("bat_top")], base + ".step")
    return doc


def compare_vendor():
    """Bounding box of the placeholder against the vendor STEP (that one is hollow, so no volume compare)."""
    ref = Part.read(VENDOR_STEP).BoundBox
    own = Part.makeCompound([G.battery_body_local(), G.battery_top_local()]).BoundBox
    return ({"vendor": (round(ref.XLength, 1), round(ref.ZLength, 1), round(ref.YLength, 1)),
             "placeholder": (round(own.XLength, 1), round(own.YLength, 1), round(own.ZLength, 1))})


# ---------------------------------------------------------------------
# Object lists and checks
# ---------------------------------------------------------------------
def active_doc(doc=None):
    if doc is not None:
        return doc
    d = App.ActiveDocument
    if d is not None and d.getObject(ROOT) is not None:
        return d
    for name in App.listDocuments():
        d = App.getDocument(name)
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


def _joint(a, b):
    """Bolts through the rails / hangers and the upper beams."""
    for p, q in ((a, b), (b, a)):
        if p.startswith(("rbolts", "hbolts_", "wbolts")) and q.startswith(("rails", "hangers_", "upper_beam",
                                                                          "wood_box")):
            return True
    return False


def check_interference(doc=None, tol=1.0, steer=(-30.0, 0.0, 30.0)):
    """Volume overlap (mm3): rack parts among themselves and against the robot, with the front wheels steered."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    hits = _overlaps(pairs, tol)
    for st in steer:
        set_steering(st, doc)
        robot = [(o, global_shape(o)) for o in robot_objects(doc)]
        hits += [h + (st,) for h in _overlaps([(a, b) for a in mine for b in robot
                                               if not _joint(a[0].Name, b[0].Name)], tol)]
    set_steering(0.0, doc)
    return hits


def tyre_envelope(x, y, steer=0.0):
    c = V(x, y, 215.0)
    t = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, c - V(P.robot_tire_w / 2.0, 0, 0), V(1, 0, 0))
    t.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return t


def clearance(doc=None):
    """Smallest distance (mm) of the rack to the 4 tyres (plain cylinders, front steered +-30)."""
    doc = active_doc(doc)
    best = (1e9, None, None)
    for st in (-P.robot_steer_deg, 0.0, P.robot_steer_deg):
        tyres = [tyre_envelope(sx * P.robot_wheel_x, sy * P.robot_axle_y, st if sy > 0 else 0.0)
                 for sx in (-1, 1) for sy in (-1, 1)]
        for o in objects_of(doc, ROOT):
            s = global_shape(o)
            for t in tyres:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name, st)
    return round(best[0], 1), best[1], best[2]


MASS_FIXED = {"bat": P.bat_kg, "battop": 0.0, "combiner": 1.5, "knobs": 0.2, "knob": 0.1, "fittings": 0.4,
              "latches": 0.4, "wfit": 1.0,
              "batmu": P.mu3_kg, "batmutop": 0.0}
DENSITY = (("trays", P.alu), ("frames", P.alu), ("posts", P.alu), ("guides", P.alu), ("hold", P.alu),
           ("ears", P.alu), ("cradle", P.alu), ("shell", P.alu), ("shelves", P.alu), ("doors", P.alu),
           ("bars", P.alu), ("seps", P.hdpe), ("mat", P.rubber), ("wood", P.plywood))


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    key = obj.Name.split("_")[0]
    if key in MASS_FIXED:
        return MASS_FIXED[key], cg
    dens = P.steel
    for k, d in DENSITY:
        if obj.Name.startswith(k):
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
    """Mass (kg) and centre of gravity (robot coordinates): all, and without the batteries."""
    doc = active_doc(doc)
    objs = objects_of(doc, ROOT)
    m, c = sum_mass(objs)
    me, _ = sum_mass([o for o in objs if not o.Name.startswith("bat")])
    return {"total_kg": round(m, 1), "empty_kg": round(me, 1), "cg": (round(c.x), round(c.y), round(c.z))}


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in objects_of(doc, ROOT):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin)), \
        round(bb.ZMax)


def check_all(concepts=P.CONCEPTS, ns=(2, 3, 4)):
    """Every concept and size: interference, clearance, mass, size. Long: start with a QTimer, see AGENTS.md."""
    out = {}
    for concept in concepts:
        for n in P.CONCEPT_NS.get(concept, ns):
            doc = build(concept, n, save=False, step=False)
            out["%s_%d" % (concept, n)] = {"hits": check_interference(doc), "clearance": clearance(doc),
                                           "mass": mass_properties(doc), "size": size(doc)}
            App.closeDocument(doc.Name)
    return out


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
    tgt = V(*target) if target is not None else V(0, 0, 450)
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


def add_floor(doc, y=(-900.0, 900.0), x=(-900.0, 900.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.72, 0.72, 0.70)
    obj.ViewObject.Transparency = 30
    return obj


def set_transparent(doc, prefixes, value=70):
    for o in objects_of(doc, ROOT):
        if o.Name.startswith(prefixes):
            o.ViewObject.Transparency = value


def render_sizes():
    """The upright rack with 2, 3 and 4 slots next to each other, without the robot (well geometry)."""
    name = "Battery_Rack_sizes"
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    for i, n in enumerate((2, 3, 4)):
        holder = new_part(doc, None, "Size_%d" % n, "rack_%d_batteries" % n,
                          App.Placement(V((i - 1) * 520.0, 0, 0), App.Rotation()))
        build_into(doc, "well", n, parent=holder).Label = "battery_rack_%d" % n
        for o in holder.OutListRecursive:
            if o.TypeId == "Part::Feature" and o.Name.startswith(("rails", "rbolts")):
                o.ViewObject.Visibility = False
    doc.recompute()
    path = save_view("0_rack_2_3_4.png", (-0.8, 1.0, -0.6), target=(0, 0, 460), height=1100)
    App.closeDocument(name)
    return path


def render_placeholder(kind="MBH3+"):
    doc = build_placeholder(save=False, kind=kind)
    h = 560 if kind == "MBH3+" else 420
    path = save_view("p_%s_placeholder.png" % BAT_NAMES[kind][1].lower(), (-1.0, 0.8, -0.6), target=(0, 0, 150),
                     height=h, size_px=(1000, 1000))
    App.closeDocument(doc.Name)
    return path


def render_wood_open(concept):
    doc = build(concept, 2, save=False, show_robot=True, step=False)
    doc.getObject("wood_lid").ViewObject.Visibility = False
    doc.getObject("wfit").ViewObject.Visibility = False
    zm = (P.wood_outer(concept)[4] + P.wood_outer(concept)[5]) / 2.0 + 100.0
    path = save_view("x_%s_open.png" % concept, (-0.5, 0.9, -1.0), target=(P.wood_x_c, 0, zm), height=800)
    App.closeDocument(doc.Name)
    return path


def render_all():
    """Standard images in previews/, then build and save every concept with 2 batteries (robot hidden)."""
    out = [render_sizes()]
    i = 1
    for concept in P.CONCEPTS:
        for n in P.CONCEPT_NS.get(concept, (2, 4)):
            doc = build(concept, n, save=False, show_robot=True, step=False)
            add_floor(doc)
            # the cabinet on top has its doors at the rear: look from the rear right
            d = (-1.0, 1.2, -0.7) if concept == "cabinet_top" else (-1.0, -1.2, -0.7)
            out.append(save_view("%d_%s_%d.png" % (i, concept, n), d, target=(0, 0, 500), height=1900))
            i += 1
            App.closeDocument(doc.Name)
    doc = build("well", 2, save=False, show_robot=True, step=False)
    out.append(save_view("x_well_side.png", (-1.0, 0.0, 0.0), target=(0, 0, 450), height=1100))
    App.closeDocument(doc.Name)
    doc = build("cabinet_well", 4, save=False, show_robot=False, step=False)
    set_transparent(doc, ("shell", "doors"), 75)
    out.append(save_view("x_cabinet_inside.png", (-1.0, -0.6, -0.45), target=(0, 0, 460), height=750))
    App.closeDocument(doc.Name)
    for concept in P.WOOD:
        out.append(render_wood_open(concept))
    for kind in BAT_NAMES:
        out.append(render_placeholder(kind))
    for concept in P.CONCEPTS:
        App.closeDocument(build(concept, 2).Name)
    for kind in BAT_NAMES:
        App.closeDocument(build_placeholder(kind=kind).Name)
    return out
