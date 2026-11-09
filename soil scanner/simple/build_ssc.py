"""Model of the soil scanner (gamma-ray spectrometer) on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_ssc
    build_ssc.build()                      # saves FCStd and STEP
    build_ssc.build(with_sampler=True, save=False)   # with the soil sampler in the middle (calibration samples)
    build_ssc.check_interference()         # overlap (must be empty)
    build_ssc.check_holes()                # bracket bolts in the grid holes of the front beam (must be empty)
    build_ssc.check_steer()                # front wheels at -30 / 0 / +30 degrees (must be empty)
    build_ssc.clearance()                  # smallest distances to the tyres and the steering stack
    build_ssc.mass_properties()
    build_ssc.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ssc_params as P
import ssc_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Soil_Scanner"
SAVE_BASE = os.path.join(FOLDER, "Soil_Scanner")
ROOT = "Soil_scanner"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "tube": (0.10, 0.11, 0.13),
    "cap": (0.12, 0.45, 0.80),
    "label": (0.86, 0.87, 0.89),
    "crystal": (0.92, 0.95, 1.00),
    "foam": (0.93, 0.90, 0.75),
    "pmt": (0.55, 0.42, 0.20),
    "board": (0.10, 0.45, 0.20),
    "rubber": (0.08, 0.08, 0.08),
    "steel": (0.72, 0.73, 0.76),
    "box": (0.30, 0.32, 0.35),
    "cable": (0.05, 0.05, 0.05),
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


def build_into(doc, parent=None):
    root = new_part(doc, parent, ROOT, "soil_scanner_simple")
    mount = new_part(doc, root, "SSC_Mount", "mount_brackets_guard_processor")
    add_shape(doc, mount, "ssc_brackets", "brackets_base_side_arm_8mm_2x", G.brackets(), "frame")
    add_shape(doc, mount, "ssc_bracket_bolts", "bracket_bolts_M10_4x", G.bracket_bolts(), "zinc")
    add_shape(doc, mount, "ssc_rubber_mounts", "rubber_mounts_D30x20_M8_4x", G.rubber_mounts(), "rubber")
    add_shape(doc, mount, "ssc_mount_nuts", "rubber_mount_studs_nuts_M8", G.mount_nuts(), "zinc")
    add_shape(doc, mount, "ssc_clamps", "clamp_rings_50x6_lug_ears_2x", G.clamps(), "frame")
    add_shape(doc, mount, "ssc_clamp_bolts", "clamp_bolts_M8", G.clamp_bolts(), "zinc")
    add_shape(doc, mount, "ssc_liners", "clamp_liners_EPDM_2mm", G.liners(), "rubber")
    add_shape(doc, mount, "ssc_guard", "guard_tube_D30x2_5", G.guard(), "frame")
    add_shape(doc, mount, "ssc_ebox", "processor_box_IP67_spectrum_logger_4G", G.ebox(), "box")
    add_shape(doc, mount, "ssc_cable", "detector_cable_D9", G.cable(), "cable")
    det = new_part(doc, root, "SSC_Detector", "gamma_detector_CsI_4l")
    add_shape(doc, det, "ssc_tube", "housing_tube_alu_D200x4_L660", G.tube(), "tube")
    add_shape(doc, det, "ssc_caps", "end_caps_alu_D226", G.caps(), "cap")
    add_shape(doc, det, "ssc_labels", "end_cap_face_plates", G.labels(), "label")
    add_shape(doc, det, "ssc_gland", "cable_gland_M20", G.gland(), "rubber")
    add_shape(doc, det, "ssc_crystal", "crystal_CsI_Tl_100x100x400", G.crystal(), "crystal")
    add_shape(doc, det, "ssc_foam", "foam_sleeve_PE", G.foam(), "foam")
    add_shape(doc, det, "ssc_pmt", "photomultiplier_D76", G.pmt(), "pmt")
    add_shape(doc, det, "ssc_mca", "mca_hv_board_D160", G.mca(), "board")
    return root


def build_robot(doc):
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


def sampler_module():
    if P.SSA_FOLDER not in sys.path:
        sys.path.append(P.SSA_FOLDER)
    import build_ssa
    return build_ssa


def build(save=True, show_robot=False, step=True, with_sampler=False):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Soil scanner simple"
    doc.Comment = ("Generated by build_ssc.py from ssc_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    if with_sampler:
        sampler_module().build_into(doc, robot)
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
    """Everything under Robot that is not the scanner (robot itself, and the soil sampler when fitted)."""
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in objects_of(doc, ROOT)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    sampler = {o.Name for o in objects_of(doc, "Soil_sampler")}
    for o in robot_objects(doc):
        if o.Name not in sampler:
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


JOINTS = {("ssc_bracket_bolts", "ssc_brackets"), ("ssc_rubber_mounts", "ssc_brackets"),
          ("ssc_rubber_mounts", "ssc_clamps"), ("ssc_mount_nuts", "ssc_brackets"),
          ("ssc_mount_nuts", "ssc_rubber_mounts"), ("ssc_clamp_bolts", "ssc_clamps"), ("ssc_liners", "ssc_clamps"),
          ("ssc_liners", "ssc_tube"), ("ssc_guard", "ssc_brackets"), ("ssc_ebox", "ssc_brackets"),
          ("ssc_cable", "ssc_ebox"), ("ssc_cable", "ssc_gland"), ("ssc_gland", "ssc_caps"), ("ssc_caps", "ssc_tube"),
          ("ssc_labels", "ssc_caps"), ("ssc_crystal", "ssc_pmt"), ("ssc_pmt", "ssc_mca"), ("ssc_foam", "ssc_tube"),
          ("ssc_foam", "ssc_crystal")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    pair = {a, b}
    return "ssc_bracket_bolts" in pair and any(n.startswith("lower_beam") for n in pair)


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """An O9 rod at every bracket bolt against the front lower beam: must not cut steel (the bolt is in a hole)."""
    doc = active_doc(doc)
    beams = [global_shape(o) for o in robot_objects(doc) if o.Name.startswith("lower_beam")]
    yc = sum(P.robot_front_beam_y) / 2
    out = {}
    for sx in G.SIDES:
        for dx in (-P.bolt_dx, P.bolt_dx):
            x = sx * P.bracket_x + dx
            rod = G.cyl(9.0, (x, yc, P.robot_lower_beam_z[0] - 5), (x, yc, P.robot_lower_beam_z[1] + 5))
            v = sum(rod.common(b).Volume for b in beams)
            if v > tol:
                out[str(x)] = round(v, 1)
    return out


def set_steer(deg, doc=None):
    doc = active_doc(doc)
    for tag in ("FL", "FR"):
        o = doc.getObject("%s_steered" % tag)
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), deg))


def check_steer(doc=None, tol=1.0):
    """Front wheels and steering stack at -30, 0 and +30 degrees against the scanner. Must be empty."""
    doc = active_doc(doc)
    out = {}
    for deg in (-P.robot_steer_deg, 0.0, P.robot_steer_deg):
        set_steer(deg, doc)
        steered = [(o, global_shape(o)) for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
        mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
        hits = _overlaps([(a, b) for a in mine for b in steered], tol)
        if hits:
            out[str(deg)] = hits
    set_steer(0.0, doc)
    return out


def clearance(doc=None):
    """Smallest distance (mm) of the scanner to the front tyres (over the steering range) and the steering stack."""
    doc = active_doc(doc)
    mine = [global_shape(o) for o in objects_of(doc, ROOT)]
    out = {"tyre": 1e9, "steering_stack": 1e9, "gnss": 1e9}
    for deg in (-P.robot_steer_deg, -15.0, 0.0, 15.0, P.robot_steer_deg):
        set_steer(deg, doc)
        for o in robot_objects(doc):
            if o.Name.startswith(("FL_", "FR_")):
                key = "tyre" if o.Name.endswith("_tire") else "steering_stack"
            elif o.Name.startswith("gnss"):
                key = "gnss"
            else:
                continue
            s = global_shape(o)
            sb = s.BoundBox
            for m in mine:
                mb = m.BoundBox
                gap = max(sb.XMin - mb.XMax, mb.XMin - sb.XMax, sb.YMin - mb.YMax, mb.YMin - sb.YMax,
                          sb.ZMin - mb.ZMax, mb.ZMin - sb.ZMax, 0.0)
                if gap < out[key]:
                    out[key] = min(out[key], m.distToShape(s)[0])
    set_steer(0.0, doc)
    return {k: round(v, 1) for k, v in out.items()}


MASS_FIXED = {"ssc_pmt": 0.8, "ssc_mca": 0.35, "ssc_ebox": 2.4, "ssc_gland": 0.05}
DENSITY = (("ssc_tube", P.alu), ("ssc_caps", P.alu), ("ssc_labels", P.alu), ("ssc_crystal", P.csi_rho * 1e-6),
           ("ssc_foam", P.pe_foam), ("ssc_rubber", P.epdm), ("ssc_liners", P.epdm), ("ssc_cable", 1.6e-6))
HOLLOW = {"ssc_guard": (30.0 ** 2 - 25.0 ** 2) / 30.0 ** 2}     # the guard is drawn solid, it is a tube 30 x 2.5


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
            break
    return vol * dens * HOLLOW.get(obj.Name, 1.0), cg


def sum_mass(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) of the scanner and its groups, plus the crystal."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "SSC_Mount", "SSC_Detector"):
        m, c = sum_mass(objects_of(doc, name))
        out[name.lower() + "_kg"] = round(m, 1)
        out[name.lower() + "_cg"] = (round(c.x), round(c.y), round(c.z))
    out["crystal_kg"] = round(_mass_cg(doc.getObject("ssc_crystal"))[0], 1)
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
    view = Gui.getDocument(DOC_NAME).ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, 600, 400)
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


def add_floor(doc, y=(-900.0, 1400.0), x=(-1000.0, 1000.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.62, 0.70, 0.45)
    obj.ViewObject.Transparency = 20
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_transparency(doc, names, value):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Transparency = value


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    import FreeCADGui as Gui
    out = []
    doc = build(save=False, show_robot=True, step=False)
    Gui.getDocument(DOC_NAME).ActiveView  # make sure the view exists
    App.setActiveDocument(DOC_NAME)
    add_floor(doc)
    out.append(save_view("1_iso_front_right_on_robot.png", (-1.0, -1.1, -0.55), target=(0, 300, 450), height=2000))
    out.append(save_view("2_side_600mm_above_ground.png", (-1.0, 0.0, 0.0), target=(0, 250, 500), height=1500))
    out.append(save_view("3_front.png", (0.0, -1.0, 0.0), target=(0, 0, 450), height=1250))
    set_steer(P.robot_steer_deg, doc)
    out.append(save_view("4_top_steering_30deg.png", (0.0, 0.0, -1.0), target=(0, 450, 500), height=1500,
                         up=(0.0, 1.0, 0.0)))
    set_steer(0.0, doc)
    set_robot_visible(False, doc)
    remove(doc, [GROUND])
    set_transparency(doc, ["ssc_tube", "ssc_caps", "ssc_labels", "ssc_liners", "ssc_clamps"], 75)
    set_transparency(doc, ["ssc_foam"], 55)
    out.append(save_view("5_cutaway_crystal_pmt.png", (-0.7, -1.0, -0.6), target=(0, 880, 600), height=900))
    set_transparency(doc, ["ssc_tube", "ssc_caps", "ssc_labels", "ssc_liners", "ssc_clamps", "ssc_foam"], 0)
    out.append(save_view("6_mount_detail.png", (-1.0, 0.8, -0.5), target=(225, 780, 680), height=520))
    App.closeDocument(doc.Name)
    doc = build(save=False, show_robot=True, step=False, with_sampler=True)
    App.setActiveDocument(DOC_NAME)
    add_floor(doc)
    out.append(save_view("7_with_soil_sampler.png", (-1.0, -1.1, -0.5), target=(0, 200, 500), height=2100))
    App.closeDocument(doc.Name)
    build()
    return out
