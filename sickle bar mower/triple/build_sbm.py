"""Model of the triple sickle bar mower on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder in sys.path, or via run_in_freecad.py):
    import build_sbm
    build_sbm.build()                     # saves Sickle_Bar_Mower.FCStd and .step (work position)
    build_sbm.check_interference()        # overlap (must be empty)
    build_sbm.check_poses()               # overlap in the float, lift, fold and knife positions
    build_sbm.clearance()                 # smallest distance to the steered front wheels and the rear wheels
    build_sbm.mass_properties()           # mass and centre of gravity
    build_sbm.render_all()                # all images in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import sbm_params as P
import sbm_parts as G
import sbm_grass as W

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Sickle_Bar_Mower"
SAVE_BASE = os.path.join(FOLDER, DOC_NAME)
ROOT = "Sickle_bar_mower"

COLOR = {
    "frame": (0.78, 0.12, 0.10),
    "bar": (0.22, 0.23, 0.25),
    "knife": (0.80, 0.81, 0.84),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.62, 0.63, 0.66),
    "gearbox": (0.55, 0.57, 0.60),
    "motor": (0.08, 0.08, 0.08),
    "shoe": (0.30, 0.31, 0.33),
    "actuator": (0.55, 0.57, 0.60),
    "box": (0.55, 0.57, 0.60),
    "ground": (0.45, 0.36, 0.24),
    "grass": (0.30, 0.56, 0.20),
    "stubble": (0.55, 0.66, 0.30),
    "cut": (0.70, 0.74, 0.36),
}

BAR_NAMES = {"F": "front", "R": "right_wing", "L": "left_wing"}


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


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_cutter_bar(doc, parent, bar):
    """Static parts of a bar module, the 2 knives (sub-Parts) and the con-rods (redrawn per crank angle)."""
    L = G.BARS[bar]
    kind = "front" if bar == "F" else "wing"
    m = G.module(L, kind)
    name = BAR_NAMES[bar]
    labels = {"beam": "bar_flat_80x8", "stiffener": "bar_stiffener_RHS_50x30x3",
              "clips": "hold_down_clips_%dx" % P.clip_n[kind], "shoes": "shoes_inner_outer",
              "drive_plate": "drive_plate_12mm", "gearbox": "crank_gearbox_2_cranks",
              "motor": "BLDC_motor_48V_1000W_planetary_5to1"}
    colors = {"beam": "bar", "stiffener": "bar", "clips": "steel", "shoes": "shoe", "drive_plate": "frame",
              "gearbox": "gearbox", "motor": "motor"}
    for key, shape in m.items():
        add_shape(doc, parent, "%s_%s" % (bar, key), "%s_%s" % (labels[key], name), G.place(shape, bar), colors[key])
    add_shape(doc, parent, bar + "_rods", "con_rods_2x_" + name, G.place(G.rods(L), bar), "steel")
    for which in ("upper", "lower"):
        k = new_part(doc, parent, "%s_knife_%s" % (bar, which), "knife_%s_%s_moves" % (which, name))
        add_shape(doc, k, "%s_%s_knife" % (bar, which), "knife_%s_%d_sections_%s" % (which, int(L / P.pitch), name),
                  G.place(G.knife(L, which), bar), "knife")


def build_front(doc, parent):
    grp = new_part(doc, parent, "Front_mount", "front_mount_plate_lugs")
    add_shape(doc, grp, "mount_plate", "mount_plate_8mm", G.mount_plate(), "frame")
    add_shape(doc, grp, "mount_bolts", "mount_bolts_8x_M10", G.mount_bolts(), "zinc")
    add_shape(doc, grp, "robot_lugs", "link_lugs_2x_10mm", G.robot_lugs(), "frame")
    add_shape(doc, grp, "actuator_lug", "actuator_lug_10mm", G.actuator_lug(), "frame")
    add_shape(doc, grp, "robot_pins", "pins_M16_robot_side", G.robot_pins(), "zinc")
    top = new_part(doc, parent, "Top_links", "top_links_turn_about_robot_pivot")
    add_shape(doc, top, "top_links", "top_links_4x_flat_40x6", G.top_links(), "frame")
    bot = new_part(doc, parent, "Bottom_links", "bottom_links_turn_about_robot_pivot")
    add_shape(doc, bot, "bottom_links", "bottom_links_4x_flat_40x6", G.bottom_links(), "frame")
    act = new_part(doc, parent, "Front_actuator", "front_actuator_redrawn")
    body, rod, links = G.front_actuator()
    add_shape(doc, act, "F_act_body", "linear_actuator_150mm_4000N", body, "actuator")
    add_shape(doc, act, "F_act_rod", "actuator_rod_and_eye", rod, "steel")
    add_shape(doc, act, "F_float_link", "float_link_2x_flat_30x6_slot60", links, "frame")
    head = new_part(doc, parent, "Front_head", "front_head_frame_moves_with_links")
    add_shape(doc, head, "head_frame", "head_frame_plate_lugs", G.head_frame(), "frame")
    add_shape(doc, head, "head_pins", "pins_M16_head_side", G.head_pins(), "zinc")
    add_shape(doc, head, "roll_pin", "roll_pin_M30", G.roll_pin(), "zinc")
    bar = new_part(doc, head, "Front_bar", "front_bar_rolls_on_roll_pin")
    add_shape(doc, bar, "bar_frame", "bar_frame_RHS_60x40_arms", G.bar_frame(), "frame")
    build_cutter_bar(doc, bar, "F")


def build_middle(doc, parent):
    grp = new_part(doc, parent, "Mid_frame", "mid_frame_under_top_beams")
    add_shape(doc, grp, "mid_frame", "mid_frame_rails_cross_tube_hangers_post", G.mid_frame(), "frame")
    add_shape(doc, grp, "rail_bolts", "rail_bolts_8x_M10", G.rail_bolts(), "zinc")
    add_shape(doc, grp, "hinge_pins", "hinge_pins_2x_M30", G.hinge_pins(), "zinc")
    for bar in ("R", "L"):
        side = BAR_NAMES[bar]
        wing = new_part(doc, parent, "Wing_" + bar, "%s_folds_about_hinge" % side)
        hinge = G.wing_hinge()
        pin = G.lever_pin()
        if bar == "L":
            hinge, pin = G.mirror_x(hinge), G.mirror_x(pin)
        add_shape(doc, wing, bar + "_hinge", "hinge_bracket_tube_lever_" + side, hinge, "frame")
        add_shape(doc, wing, bar + "_lever_pin", "lever_pin_M16_" + side, pin, "zinc")
        build_cutter_bar(doc, wing, bar)
        act = new_part(doc, parent, "Wing_%s_actuator" % bar, "actuator_%s_redrawn" % side)
        body, rod, apin = G.wing_actuator()
        if bar == "L":
            body, rod, apin = G.mirror_x(body), G.mirror_x(rod), G.mirror_x(apin)
        add_shape(doc, act, bar + "_act_body", "linear_actuator_250mm_4000N_" + side, body, "actuator")
        add_shape(doc, act, bar + "_act_rod", "actuator_rod_and_eye_" + side, rod, "steel")
        add_shape(doc, act, bar + "_anchor_pin", "anchor_pin_M16_in_slot_" + side, apin, "zinc")


def build_controller(doc, parent):
    grp = new_part(doc, parent, "Controller", "controller_box_3_BLDC_drivers")
    add_shape(doc, grp, "box_base", "controller_base_plate_3mm", G.box_base(), "zinc")
    add_shape(doc, grp, "controller_box", "controller_box_IP66_3x48V_30A", G.controller_box(), "box")
    add_shape(doc, grp, "box_bolts", "controller_bolts_M8", G.box_bolts(), "zinc")


def build_into(doc, parent=None):
    """Puts the mower in a document, in robot coordinates (also used by animate_sbm.py)."""
    root = new_part(doc, parent, ROOT, "triple_sickle_bar_mower")
    build_front(doc, root)
    build_middle(doc, root)
    build_controller(doc, root)
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
    doc.Label = "Triple sickle bar mower"
    doc.Comment = ("Generated by build_sbm.py from sbm_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Front bar %g mm + 2 wings %g mm, work position."
                   % (P.front_L, P.wing_L))
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
    if d is not None and d.getObject(ROOT) is not None:
        return d
    raise RuntimeError("no sickle bar mower document open")


def own_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in own_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in own_objects(doc):
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
# Moving parts (animation and checks): only Placements change, actuators and con-rods are redrawn
# ---------------------------------------------------------------------
def set_front(doc, lift=0.0, lift_set=P.lift_work, roll=0.0):
    """Front bar at 'lift' mm above the work position (actuator set to lift_set; lift >= lift_set while the float link
    has slack), rolled by 'roll' deg (+ = right end down, seen from behind: rotation about +y)."""
    dy, dz = P.head_shift(lift)
    doc.getObject("Front_head").Placement = App.Placement(V(0, dy, dz), App.Rotation())
    doc.getObject("Front_bar").Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 1, 0), roll),
                                                         V(0, 0, P.roll_z))
    da = P.theta(lift) - P.theta(0.0)
    for name, z in (("Top_links", P.pivot_z[1]), ("Bottom_links", P.pivot_z[0])):
        doc.getObject(name).Placement = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), da), V(0, P.pivot_y, z))
    body, rod, links = G.front_actuator(lift_set, lift)
    doc.getObject("F_act_body").Shape = Part.makeCompound(body)
    doc.getObject("F_act_rod").Shape = Part.makeCompound(rod)
    doc.getObject("F_float_link").Shape = Part.makeCompound(links)


def set_wing(doc, bar, fold=0.0, act=None):
    """Wing 'R' or 'L' at fold angle (deg, + = outer end up; negative = floated down), actuator at length act (None:
    work setting, the anchor pin slides in its slot)."""
    s = 1 if bar == "R" else -1
    hx, hz = P.hinge
    doc.getObject("Wing_" + bar).Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 1, 0), -s * fold),
                                                           V(s * hx, 0, hz))
    body, rod, pin = G.wing_actuator(fold, act)
    if bar == "L":
        body, rod, pin = G.mirror_x(body), G.mirror_x(rod), G.mirror_x(pin)
    doc.getObject(bar + "_act_body").Shape = Part.makeCompound(body)
    doc.getObject(bar + "_act_rod").Shape = Part.makeCompound(rod)
    doc.getObject(bar + "_anchor_pin").Shape = Part.makeCompound(pin)


def set_knives(doc, theta=G.THETA0, bars=("F", "R", "L")):
    """Crank angle theta (rad) on all bars: knives shifted, con-rods redrawn."""
    up, low = G.knife_shift(theta)
    for bar in bars:
        d = G.u_dir(bar)
        doc.getObject(bar + "_knife_upper").Placement = App.Placement(d * up, App.Rotation())
        doc.getObject(bar + "_knife_lower").Placement = App.Placement(d * low, App.Rotation())
        doc.getObject(bar + "_rods").Shape = Part.makeCompound(G.place(G.rods(G.BARS[bar], theta), bar))


def fold_act(fold):
    """Wing actuator length for a fold angle when the actuator pulls (anchor pin at the outer end of its slot)."""
    return P.wact_length(fold)


def set_transport(doc, f=1.0):
    """Fraction f of the way from work (0) to transport (1): front bar lifted, both wings folded."""
    lift = P.lift_max * f
    set_front(doc, lift, lift)
    fold = P.fold_max * f
    for bar in ("R", "L"):
        set_wing(doc, bar, fold, fold_act(fold) if f > 0 else None)


def reset(doc):
    set_front(doc)
    for bar in ("R", "L"):
        set_wing(doc, bar)
    set_knives(doc)


def set_steering(doc, deg):
    for tag in ("FL", "FR"):
        o = doc.getObject(tag + "_steered")
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), deg))


# ---------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3): own parts with each other and with the (visible and hidden) robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in own_objects(doc)]
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


POSES = {
    "work_knives_0": {"theta": 0.0},
    "work_knives_90": {"theta": math.pi / 2.0},
    "work_knives_180": {"theta": math.pi},
    "work_knives_270": {"theta": 1.5 * math.pi},
    "front_float_down": {"front": (P.lift_work, P.lift_work, 0.0)},
    "front_float_up_rolled": {"front": (140.0, P.lift_work, P.roll_max)},
    "front_rolled_other": {"front": (0.0, P.lift_work, -P.roll_max)},
    "front_lifted": {"front": (P.lift_max, P.lift_max, 0.0), "theta": 0.0},
    "wings_float_down": {"wings": "down"},
    "wings_float_up": {"wings": "up", "theta": math.pi},
    "wings_45": {"wings": 45.0},
    "transport": {"transport": 1.0, "theta": 1.5 * math.pi},
}


def apply_pose(doc, pose):
    reset(doc)
    if "transport" in pose:
        set_transport(doc, pose["transport"])
    if "front" in pose:
        lift, lift_set, roll = pose["front"]
        set_front(doc, lift, lift_set, roll)
    if "wings" in pose:
        w = pose["wings"]
        down, up = P.wing_float_range()
        for bar in ("R", "L"):
            if w == "down":
                set_wing(doc, bar, down)
            elif w == "up":
                set_wing(doc, bar, up)
            else:
                set_wing(doc, bar, w, fold_act(w))
    if "theta" in pose:
        set_knives(doc, pose["theta"])
    doc.recompute()


def check_poses(doc=None, names=None):
    """Interference in every pose of POSES. Puts the model back in the work position."""
    doc = active_doc(doc)
    out = {}
    try:
        for name in (names or POSES):
            apply_pose(doc, POSES[name])
            out[name] = check_interference(doc)
    finally:
        reset(doc)
        doc.recompute()
    return out


FRONT_WHEEL = ("tire", "rim", "side_l", "side_r", "top_plate", "axle_br_l", "axle_br_r", "wheel_hw", "hub_flange")
NEAR = ("F_shoes", "F_beam", "F_stiffener", "bar_frame", "head_frame", "bottom_links", "top_links", "F_act_body",
        "R_shoes", "R_beam", "R_hinge", "L_shoes", "L_beam", "L_hinge", "mid_frame", "R_motor", "L_motor")


def clearance(doc=None, steers=(-P.steer_max, 0.0, P.steer_max), poses=("work", "front_lifted", "transport")):
    """Smallest distance (mm) of the mower to the wheel units (front steered), per steering angle and pose."""
    doc = active_doc(doc)
    out = {}
    try:
        for st in steers:
            set_steering(doc, st)
            doc.recompute()
            wheels = [global_shape(doc.getObject("%s_%s" % (t, n))) for t in ("FL", "FR", "RL", "RR")
                      for n in FRONT_WHEEL if doc.getObject("%s_%s" % (t, n)) is not None]
            for pose in poses:
                if pose == "work":
                    reset(doc)
                    doc.recompute()
                else:
                    apply_pose(doc, POSES[pose])
                best = (1e9, "")
                for n in NEAR:
                    a = global_shape(doc.getObject(n))
                    for w in wheels:
                        d = a.distToShape(w)[0]
                        if d < best[0]:
                            best = (d, n)
                out["steer_%g_%s" % (st, pose)] = (round(best[0], 1), best[1])
    finally:
        set_steering(doc, 0.0)
        reset(doc)
        doc.recompute()
    return out


MASS_FIXED = {"F_gearbox": 4.5, "R_gearbox": 4.5, "L_gearbox": 4.5,          # bought (estimated)
              "F_motor": 6.5, "R_motor": 6.5, "L_motor": 6.5,
              "F_act_body": 3.0, "R_act_body": 3.5, "L_act_body": 3.5, "controller_box": 3.5}
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
        return MASS_FIXED[obj.Name], cg, vol
    return vol * STEEL, cg, vol


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co, _ = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def _objs_of(doc, name):
    g = doc.getObject(name)
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) in the work position: total and per group, knife mass."""
    doc = active_doc(doc)
    m, c = _sum(own_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    groups = ("Front_mount", "Top_links", "Bottom_links", "Front_actuator", "Front_head", "Front_bar", "Mid_frame",
              "Wing_R", "Wing_L", "Wing_R_actuator", "Wing_L_actuator", "Controller")
    for g in groups:
        mg, cg = _sum(_objs_of(doc, g))
        out[g.lower() + "_kg"] = round(mg, 2)
        out[g.lower() + "_cg"] = (round(cg.x), round(cg.y), round(cg.z))
    for bar in ("F", "R"):
        for which in ("upper", "lower"):
            o = doc.getObject("%s_%s_knife" % (bar, which))
            out["%s_knife_%s_kg" % (bar, which)] = round(o.Shape.Volume * STEEL, 2)
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in own_objects(doc):
        if o.Name.startswith(("box", "controller")):
            continue
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


def size_transport(doc=None):
    doc = active_doc(doc)
    try:
        set_transport(doc, 1.0)
        doc.recompute()
        return size(doc)
    finally:
        reset(doc)
        doc.recompute()


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
    tgt = V(*target) if target is not None else V(0, 300, 300)
    eye = tgt - d * 9000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(40000.0)
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


def add_scenery(doc, y_front=None, y_wing=None, y=(-2600.0, 3400.0), x=(-2600.0, 2600.0), grass=True):
    """Ground and grass (render only, prefixed render_). Grass in front of a knife stands, behind it is cut."""
    y_front = P.y_front if y_front is None else y_front
    y_wing = P.y_wing if y_wing is None else y_wing
    g = doc.addObject("Part::Feature", "render_ground")
    g.Shape = G.box_span(x, y, (-40.0, 0.0))
    g.ViewObject.ShapeColor = COLOR["ground"]
    out = [g]
    if grass:
        field = W.Field(y=(y[0] + 100.0, y[1] - 100.0), x=(x[0] + 100.0, x[1] - 100.0))
        shapes = field.shapes(lambda t: t["y"] > (y_front if t["region"] == "F" else
                                                  (y_wing if t["region"] == "W" else 1e9)))
        for key in ("grass", "stubble", "cut"):
            o = doc.addObject("Part::Feature", "render_" + key)
            o.Shape = Part.makeCompound(shapes[key] or [Part.Vertex(0, 0, -50)])
            o.ViewObject.ShapeColor = COLOR[key]
            o.ViewObject.DisplayMode = "Shaded"
            out.append(o)
    return out


def remove_scenery(doc):
    for o in list(doc.Objects):
        if o.Name.startswith("render_"):
            doc.removeObject(o.Name)


def add_ghost(doc, pose, name, color=(0.95, 0.45, 0.35), transparency=70, groups=None):
    """Transparent copy of the moving groups in another pose."""
    apply_pose(doc, pose)
    groups = groups or ("Front_head", "Top_links", "Bottom_links", "Front_actuator", "Wing_R", "Wing_L",
                        "Wing_R_actuator", "Wing_L_actuator")
    shapes = [global_shape(o) for n in groups for o in _objs_of(doc, n)]
    reset(doc)
    doc.recompute()
    g = doc.addObject("Part::Feature", "render_" + name)
    g.Shape = Part.makeCompound(shapes)
    g.ViewObject.ShapeColor = color
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
    set_knives(doc, 0.35 * math.pi)
    doc.recompute()
    add_scenery(doc)
    out.append(save_view("1_work_iso_on_robot.png", (1.0, -1.15, -0.75), target=(0, 300, 250), height=4300))
    out.append(save_view("2_front_on_robot.png", (0.0, -1.0, -0.12), target=(0, 300, 400), height=2200,
                         size_px=(2000, 1000)))
    remove_scenery(doc)
    add_scenery(doc, grass=False)
    out.append(save_view("3_top_on_robot.png", (0.0, 0.0, -1.0), target=(0, 350, 0), up=(0.0, 1.0, 0.0),
                         height=2700, size_px=(2000, 1300)))
    remove_scenery(doc)
    add_scenery(doc, grass=False)
    set_transport(doc, 1.0)
    doc.recompute()
    out.append(save_view("4_transport_iso.png", (1.0, -1.2, -0.7), target=(0, 300, 600), height=3000))
    out.append(save_view("5_transport_rear.png", (0.0, 1.0, -0.1), target=(0, 0, 650), height=2200))
    reset(doc)
    set_knives(doc, 0.35 * math.pi)
    doc.recompute()
    add_ghost(doc, {"front": (P.lift_max, P.lift_max, 0.0)}, "ghost_lift", transparency=75,
              groups=("Front_head", "Top_links", "Bottom_links", "Front_actuator"))
    out.append(save_view("6_side_front_lift.png", (-1.0, 0.0, 0.0), target=(0, 500, 400), height=1600))
    remove_scenery(doc)
    add_scenery(doc, grass=False)
    down, up = P.wing_float_range()
    add_ghost(doc, {"wings": "up"}, "ghost_float_up", transparency=75, groups=("Wing_R", "Wing_L"))
    add_ghost(doc, {"wings": "down"}, "ghost_float_down", (0.35, 0.45, 0.95), 75, groups=("Wing_R", "Wing_L"))
    out.append(save_view("7_rear_wing_float.png", (0.0, 1.0, -0.05), target=(0, 0, 400), height=2100,
                         size_px=(2000, 1000)))
    remove_scenery(doc)
    set_robot_visible(False, doc)
    out.append(save_view("8_drive_end_detail.png", (-0.9, -1.0, -0.9), target=(1650, 120, 150), height=650))
    set_visible(doc, ("R_motor", "R_gearbox", "R_drive_plate"), False)
    out.append(save_view("9_knife_drive_gearbox_hidden.png", (-0.6, -0.8, -1.0), target=(1650, 140, 80),
                         height=480))
    set_visible(doc, ("R_motor", "R_gearbox", "R_drive_plate"), True)
    set_robot_visible(True, doc)
    out.append(save_view("10_hinge_mid_frame.png", (-1.0, 0.8, -0.45), target=(560, 0, 330), height=850))
    set_robot_visible(False, doc)
    out.append(save_view("11_mower_iso.png", (1.0, -1.2, -0.8), target=(0, 450, 250), height=3800))
    App.closeDocument(doc.Name)
    build()
    return out
