"""Model of the around-pole fence mower (simple) on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder in sys.path, or via run_in_freecad.py):
    import build_apm
    build_apm.build()                     # saves Around_Pole_Mower.FCStd and .step
    build_apm.check_interference()        # overlap (must be empty)
    build_apm.check_swing()               # overlap over the whole swing range (rest .. max stop)
    build_apm.clearance()                 # smallest distances to the rear tyre and wheel bracket
    build_apm.mass_properties()           # mass, centre of gravity, inertia of the swing group about the post
    build_apm.render_all()                # all images in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import apm_params as P
import apm_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Around_Pole_Mower"
SAVE_BASE = os.path.join(FOLDER, DOC_NAME)

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "spindle": (0.20, 0.20, 0.22),
    "motor": (0.08, 0.08, 0.08),
    "pulley": (0.55, 0.57, 0.60),
    "belt": (0.12, 0.12, 0.12),
    "pe": (0.12, 0.12, 0.12),
    "pe_white": (0.92, 0.92, 0.90),
    "guard": (0.10, 0.10, 0.10),
    "disc": (0.85, 0.75, 0.10),
    "string": (0.95, 0.45, 0.05),
    "spring": (0.20, 0.35, 0.75),
    "box": (0.55, 0.57, 0.60),
    "post": (0.55, 0.40, 0.25),
    "wire": (0.85, 0.85, 0.30),
    "insulator": (0.95, 0.75, 0.10),
    "ground": (0.45, 0.62, 0.32),
}


# ---------------------------------------------------------------------
# Tree helpers (same as build_dbr.py)
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
# Groups
# ---------------------------------------------------------------------
def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_hanger_post_stops")
    add_shape(doc, grp, "hanger_plate", "hanger_plate_10mm", G.hanger_plate(), "frame")
    add_shape(doc, grp, "hanger_bolts", "hanger_bolts_4x_M10", G.hanger_bolts(), "zinc")
    add_shape(doc, grp, "webs", "hanger_webs_2x_6mm", G.webs(), "frame")
    add_shape(doc, grp, "post", "pivot_post_tube_60x5", G.post(), "frame")
    add_shape(doc, grp, "post_cap", "post_cap", G.post_cap(), "frame")
    add_shape(doc, grp, "end_plate", "end_plate_D100_with_plug", G.end_plate(), "zinc")
    add_shape(doc, grp, "end_bolt", "end_bolt_M12", G.end_bolt(), "zinc")
    add_shape(doc, grp, "thrust_washer", "thrust_washer_PE_3mm", G.thrust_washer(), "pe_white")
    add_shape(doc, grp, "collar", "collar_D80_welded", G.collar(), "frame")
    add_shape(doc, grp, "stop_plate", "stop_plate_10mm", G.stop_plate(), "frame")
    add_shape(doc, grp, "stop_bolts", "stop_bolts_2x_M12_rest_max", G.stop_bolts(), "zinc")
    add_shape(doc, grp, "anchor_bolt", "spring_eye_bolt_M10", G.anchor_bolt(), "zinc")
    add_shape(doc, grp, "spring", "return_spring_k1.8_OD32", G.spring_shape(), "spring")
    return grp


def build_controller(doc, parent):
    grp = new_part(doc, parent, "Controller", "controller_box_BLDC_driver")
    add_shape(doc, grp, "box_base", "controller_base_plate_3mm", G.box_base(), "zinc")
    add_shape(doc, grp, "controller_box", "controller_box_IP66_48V_25A", G.controller_box(), "box")
    add_shape(doc, grp, "box_bolts", "controller_bolts_M8", G.box_bolts(), "zinc")
    return grp


def build_swing(doc, parent):
    swing = new_part(doc, parent, "Swing", "swing_turns_about_post")
    add_shape(doc, swing, "sleeve", "sleeve_tube_76x5", G.sleeve(), "frame")
    add_shape(doc, swing, "bushes", "bushes_2x_PE", G.bushes(), "pe_white")
    add_shape(doc, swing, "clevis", "clevis_back_plate_and_lugs_10mm", G.clevis(), "frame")
    add_shape(doc, swing, "lever", "spring_lever_10mm", G.lever(), "frame")
    add_shape(doc, swing, "hinge_bolt", "hinge_bolt_M16", G.hinge_bolt(), "zinc")
    arm = new_part(doc, swing, "Arm", "arm_floats_about_hinge")
    add_shape(doc, arm, "base_plate", "arm_base_plate_6mm", G.base_plate(), "frame")
    add_shape(doc, arm, "ribs", "arm_ribs_flat_6x50", G.ribs(), "frame")
    add_shape(doc, arm, "cover", "belt_cover_2mm", G.cover(), "frame")
    add_shape(doc, arm, "motor_plate", "motor_plate_8mm_slotted", G.motor_plate(), "frame")
    add_shape(doc, arm, "motor", "BLDC_motor_48V_750W_3000rpm", G.motor(), "motor")
    add_shape(doc, arm, "motor_shaft", "motor_shaft_D19", G.motor_shaft(), "steel")
    add_shape(doc, arm, "motor_pulley", "pulley_A_D110", G.motor_pulley(), "pulley")
    add_shape(doc, arm, "belt", "V_belt_A", G.belt(), "belt")
    add_shape(doc, arm, "spindle_housing", "deck_spindle_housing", G.spindle_housing(), "spindle")
    add_shape(doc, arm, "spindle_bolts", "spindle_bolts_3x_M8", G.spindle_bolts(), "zinc")
    add_shape(doc, arm, "guard_cover", "guard_cover_3mm_D315", G.guard_cover(), "steel")
    add_shape(doc, arm, "guard_ring", "guard_ring_PE_pipe_315", G.guard_ring(), "guard")
    add_shape(doc, arm, "skid_leg", "skid_leg_flat_8x50", G.skid_leg(), "frame")
    add_shape(doc, arm, "skid", "skid_puck_HDPE_D160", G.skid(), "pe_white")
    rotor = new_part(doc, arm, "Rotor", "head_rotor_turns")
    add_shape(doc, rotor, "spindle_shaft", "spindle_shaft_D19", G.spindle_shaft(), "steel")
    add_shape(doc, rotor, "spindle_pulley", "pulley_A_D90", G.spindle_pulley(), "pulley")
    add_shape(doc, rotor, "boss", "blade_boss", G.boss(), "spindle")
    add_shape(doc, rotor, "disc", "string_disc_4mm_D280", G.disc(), "disc")
    add_shape(doc, rotor, "clamps", "string_clamps_4x", G.clamps(), "zinc")
    add_shape(doc, rotor, "strings", "nylon_strings_4x_3.3", G.strings(), "string")
    return swing


def build_into(doc, parent=None):
    """Puts the mower in a document, in robot coordinates (also used by animate_apm.py)."""
    root = new_part(doc, parent, "Around_pole_mower", "around_pole_mower_simple")
    build_mount(doc, root)
    build_controller(doc, root)
    build_swing(doc, root)
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


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Around-pole fence mower (simple)"
    doc.Comment = ("Generated by build_apm.py from apm_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Mower behind the right rear wheel, arm at rest (psi %g)."
                   % P.psi_rest)
    robot = None
    if show_robot is not None:
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


def active_doc(doc=None):
    if doc is not None:
        return doc
    if DOC_NAME in App.listDocuments():
        return App.getDocument(DOC_NAME)
    d = App.ActiveDocument
    if d is not None and d.getObject("Around_pole_mower") is not None:
        return d
    raise RuntimeError("no mower document open")


def mower_objects(doc):
    return [o for o in doc.getObject("Around_pole_mower").OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in mower_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in mower_objects(doc):
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
# Moving the arm (animation and checks)
# ---------------------------------------------------------------------
def set_swing(doc, psi, float_deg=0.0, spin_deg=0.0):
    """Arm at swing angle psi (deg), float angle about the hinge (+ = head up), rotor angle. Only the Placements of
    the sub-Parts change; the spring is redrawn."""
    rot = App.Rotation(V(0, 0, 1), -(psi - P.psi_rest))
    doc.getObject("Swing").Placement = App.Placement(V(0, 0, 0), rot, V(P.pivot[0], P.pivot[1], 0))
    du, dv = P.arm_dir(P.psi_rest)
    hx, hy = P.arm_point(P.hinge_u, 0.0)
    doc.getObject("Arm").Placement = App.Placement(V(0, 0, 0), App.Rotation(V(dv[0], dv[1], 0), -float_deg),
                                                   V(hx, hy, P.hinge_z))
    cx, cy = P.HEAD_REST
    doc.getObject("Rotor").Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), spin_deg), V(cx, cy, 0))
    doc.getObject("spring").Shape = Part.makeCompound(G.spring_shape(psi))


# ---------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3): mower parts with each other and with the (visible and hidden) robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in mower_objects(doc)]
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


def check_swing(doc=None, steps=(None, 45.0, 60.0, 75.0, P.psi_max), floats=(-P.float_deg, P.float_deg)):
    """Interference over the swing range (and the float extremes at rest and at the max stop). Puts the arm back."""
    doc = active_doc(doc)
    out = {}
    try:
        for psi in steps:
            psi = P.psi_rest if psi is None else psi
            set_swing(doc, psi)
            doc.recompute()
            out["psi_%g" % psi] = check_interference(doc)
        for fl in floats:
            for psi in (P.psi_rest, P.psi_max):
                set_swing(doc, psi, fl)
                doc.recompute()
                out["psi_%g_float_%g" % (psi, fl)] = check_interference(doc)
    finally:
        set_swing(doc, P.psi_rest)
        doc.recompute()
    return out


def clearance(doc=None, robot_names=("RR_tire", "RR_side_l", "RR_side_r", "RR_spacer", "RR_top_plate"),
              psis=(None, P.psi_max)):
    """Smallest distance (mm) of the mower parts to the right rear wheel and its bracket, at rest and at the max stop."""
    doc = active_doc(doc)
    targets = [global_shape(doc.getObject(r)) for r in robot_names if doc.getObject(r) is not None]
    out = {}
    try:
        for psi in psis:
            psi = P.psi_rest if psi is None else psi
            set_swing(doc, psi)
            doc.recompute()
            best = (1e9, "")
            for o in mower_objects(doc):
                if o.Name.startswith(("box", "controller")):
                    continue
                a = global_shape(o)
                d = min(a.distToShape(t)[0] for t in targets)
                if d < best[0]:
                    best = (d, o.Name)
            out["psi_%g" % psi] = (round(best[0], 1), best[1])
    finally:
        set_swing(doc, P.psi_rest)
        doc.recompute()
    return out


MASS_FIXED = {"motor": 4.5, "spindle_housing": 2.6, "controller_box": 2.5}     # bought parts (estimated)
DENSITY = (("bushes", 0.95e-6), ("thrust_washer", 0.95e-6), ("guard_ring", 0.96e-6), ("skid", 0.96e-6),
           ("strings", 1.14e-6), ("belt", 1.2e-6), ("motor_pulley", 3.5e-6), ("spindle_pulley", 3.5e-6))   # pulleys: cast iron with spokes
STEEL = 7.85e-6


def _density(name):
    for key, d in DENSITY:
        if name.startswith(key) and not (key == "skid" and name.startswith("skid_leg")):
            return d
    return STEEL


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    if obj.Name in MASS_FIXED:
        return MASS_FIXED[obj.Name], cg, vol
    return vol * _density(obj.Name), cg, vol


def _izz(obj, axis_xy):
    """Moment of inertia (kg m2) of an object about a vertical axis through axis_xy."""
    m, cg, vol = _mass_cg(obj)
    shape = global_shape(obj)
    i = 0.0
    if obj.Name in MASS_FIXED:                       # bought part: solid cylinder of its own volume, scaled to its mass
        rho = m / vol if vol > 0 else 0.0
    else:
        rho = _density(obj.Name)
    for s in (shape.Solids or [shape]):
        izz_c = s.MatrixOfInertia.A33 * rho          # about the solid's own CG (mm5 * kg/mm3 = kg mm2)
        c = s.CenterOfMass
        ms = s.Volume * rho
        i += izz_c + ms * ((c.x - axis_xy[0]) ** 2 + (c.y - axis_xy[1]) ** 2)
    return i * 1e-6


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co, _ = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates): total, mount, swing group (+ inertia about the post)."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(mower_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for g in ("Mount", "Controller", "Swing", "Arm", "Rotor"):
        mg, cg = _sum(objs_of(g))
        out[g.lower() + "_kg"] = round(mg, 2)
        out[g.lower() + "_cg"] = (round(cg.x), round(cg.y), round(cg.z))
    out["swing_I_kgm2"] = round(sum(_izz(o, P.pivot) for o in objs_of("Swing")), 2)
    mr = _sum(objs_of("Rotor"))[0]
    out["rotor_I_kgm2"] = round(sum(_izz(o, P.HEAD_REST) for o in objs_of("Rotor")), 4)
    out["rotor_kg"] = round(mr, 2)
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in mower_objects(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


def fence_check(doc=None):
    """Height of the head (top of the arm over the post line) against the lowest wire, and the robot's distance to
    the post line."""
    doc = active_doc(doc)
    robot_xmax = max((global_shape(o).BoundBox.XMax for o in robot_objects(doc)), default=None)
    return {"head_top_z": P.HEAD_TOP_Z, "lowest_wire_z": min(P.wire_z), "post_x": round(P.POST_X),
            "wire_x": round(P.WIRE_X), "robot_xmax": None if robot_xmax is None else round(robot_xmax),
            "robot_to_post_face": None if robot_xmax is None else round(P.POST_X - P.fence_post_d / 2.0 - robot_xmax)}


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
    tgt = V(*target) if target is not None else V(300, -900, 200)
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


def add_scenery(doc, posts=None, y=(-2600.0, 2600.0), x=(-1100.0, 1500.0)):
    """Ground, fence posts with insulators and wires (render only, prefixed render_). Default: the first post just
    touches the guard ring of the head at rest, the second 3 m further."""
    if posts is None:
        hx, hy = P.HEAD_REST
        y_touch = hy + math.sqrt((P.guard_d / 2.0 + P.fence_post_d / 2.0) ** 2 - (P.POST_X - hx) ** 2) + 2.0
        posts = (y_touch, y_touch + 3000.0)
    out = []
    g = doc.addObject("Part::Feature", "render_ground")
    g.Shape = G.box_span(x, y, (-40.0, 0.0))
    g.ViewObject.ShapeColor = COLOR["ground"]
    out.append(g)
    for i, yp in enumerate(posts):
        o = doc.addObject("Part::Feature", "render_post_%d" % i)
        o.Shape = G.fence_post(yp)
        o.ViewObject.ShapeColor = COLOR["post"]
        ins = doc.addObject("Part::Feature", "render_insulators_%d" % i)
        ins.Shape = Part.makeCompound(G.insulators(yp))
        ins.ViewObject.ShapeColor = COLOR["insulator"]
        out += [o, ins]
    w = doc.addObject("Part::Feature", "render_wires")
    w.Shape = Part.makeCompound(G.wires(y[0], y[1]))
    w.ViewObject.ShapeColor = COLOR["wire"]
    out.append(w)
    return out


def remove_scenery(doc):
    for o in list(doc.Objects):
        if o.Name.startswith("render_"):
            doc.removeObject(o.Name)


def add_ghost(doc, psi, name, transparency=75):
    """Transparent copy of the arm, head and swing at swing angle psi (top views)."""
    shapes = []
    rot = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), -(psi - P.psi_rest)), V(P.pivot[0], P.pivot[1], 0))
    for o in doc.getObject("Swing").OutListRecursive:
        if o.TypeId == "Part::Feature":
            s = global_shape(o)
            s.transformShape(rot.toMatrix())
            shapes.append(s)
    g = doc.addObject("Part::Feature", "render_" + name)
    g.Shape = Part.makeCompound(shapes)
    g.ViewObject.ShapeColor = (0.95, 0.55, 0.20)
    g.ViewObject.Transparency = transparency
    return g


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def render_all():
    """Standard images in previews/, then rebuild and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    hx, hy = P.HEAD_REST
    add_scenery(doc)
    out.append(save_view("1_iso_on_robot.png", (-1.0, 1.15, -0.75), target=(350, -500, 300), height=3000))
    out.append(save_view("2_rear_on_robot.png", (0.0, 1.0, -0.12), target=(350, -900, 400), height=1500))
    out.append(save_view("3_side_on_robot.png", (-1.0, 0.0, 0.0), target=(350, -700, 450), height=1700))
    add_ghost(doc, 53.0, "ghost_53")
    add_ghost(doc, P.psi_max, "ghost_max", 85)
    out.append(save_view("4_top_swing_range.png", (0.0, 0.0, -1.0), target=(350, -900, 0), up=(0.0, 1.0, 0.0),
                         height=2300))
    remove_scenery(doc)
    set_robot_visible(False, doc)
    out.append(save_view("5_mower_iso.png", (-1.0, 1.0, -0.6), target=(450, -1000, 200), height=1300))
    set_visible(doc, ("cover",), False)
    out.append(save_view("6_belt_drive_cover_off.png", (-0.6, 1.0, -1.0), target=(480, -1000, 150), height=900))
    set_visible(doc, ("cover",), True)
    out.append(save_view("7_pivot_spring_stops.png", (1.0, -1.0, -0.3), target=(120, -780, 300), height=620))
    out.append(save_view("8_head_from_below.png", (0.3, 0.4, 1.0), target=(hx, hy, 80), height=700))
    App.closeDocument(doc.Name)
    build()
    return out
