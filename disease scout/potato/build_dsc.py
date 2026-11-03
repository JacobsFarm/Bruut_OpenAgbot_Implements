"""Model of the potato disease scout (3.0 m camera hood, wings swing forward to 1.20 m) on the Bruut OpenAgbot.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_dsc
    build_dsc.build()                              # saves FCStd and STEP (wings out)
    build_dsc.set_fold(left=0, right=90)           # swing angle of the wings in degrees (0 = working, 90 = folded)
    build_dsc.check_interference()                 # overlap in the current pose (must be empty)
    build_dsc.check_fit()                          # overlap over the whole swing of both wings (must be empty)
    build_dsc.clearance()                          # distances to the front wheels (steering) and the robot frame
    build_dsc.mass_properties()
    build_dsc.render_all()                         # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dsc_params as P
import dsc_calc as C
import dsc_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Potato_Disease_Scout"
SAVE_BASE = os.path.join(FOLDER, "Potato_Disease_Scout")
ROOT = "Disease_scout"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "alu": (0.80, 0.81, 0.83),
    "hood": (0.16, 0.36, 0.22),
    "white": (0.96, 0.96, 0.95),
    "rubber": (0.10, 0.10, 0.10),
    "curtain": (0.12, 0.12, 0.13),
    "brush": (0.25, 0.22, 0.18),
    "camera": (0.12, 0.12, 0.13),
    "glass": (0.25, 0.45, 0.75),
    "led": (0.30, 0.30, 0.32),
    "diffuser": (1.00, 0.97, 0.80),
    "actuator": (0.30, 0.31, 0.33),
    "box": (0.55, 0.57, 0.60),
    "rim": (0.85, 0.75, 0.15),
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


# ---------------------------------------------------------------------
# Pose: swing angle of both wings. The wings rotate about their kingpin, the actuator bodies about their base pin,
# the rods slide in the bodies.
# ---------------------------------------------------------------------
MOVING = ("Wing_right", "Wing_left", "Act_right", "Act_left", "Act_right_rod", "Act_left_rod")


def pose_placements(left=0.0, right=0.0):
    for name, b in (("left", left), ("right", right)):
        if not -1e-6 <= b <= P.fold + 1e-6:
            raise ValueError("%s swing %.1f outside 0 .. %.1f" % (name, b, P.fold))
    px, py = P.pivot
    bx, by = P.act_base
    out = {"Wing_right": App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), right), V(px, py, 0)),
           "Wing_left": App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), -left), V(-px, py, 0)),
           "Act_right": App.Placement(V(bx, by, 0), App.Rotation(V(0, 0, 1), C.act_angle(right))),
           "Act_left": App.Placement(V(-bx, by, 0), App.Rotation(V(0, 0, 1), 180.0 - C.act_angle(left))),
           "Act_right_rod": App.Placement(V(C.act_length(right) - P.act_closed, 0, 0), App.Rotation()),
           "Act_left_rod": App.Placement(V(C.act_length(left) - P.act_closed, 0, 0), App.Rotation())}
    return out


def set_fold(left=0.0, right=0.0, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(left, right).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


def mirror_y(shape):
    return shape.mirror(V(0, 0, 0), V(0, 1, 0))


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "posts_on_front_beams_and_parallelogram")
    add_shape(doc, grp, "post_plates", "post_plates_10mm_on_front_lower_beams", G.post_plates(), "frame")
    add_shape(doc, grp, "post_bolts", "post_bolts_8xM10", G.post_bolts(), "zinc")
    add_shape(doc, grp, "posts", "posts_60x60x4", G.posts(), "frame")
    add_shape(doc, grp, "post_ears", "post_ears_6mm", G.post_ears(), "frame")
    add_shape(doc, grp, "links", "parallelogram_links_30x30x3", G.links(), "frame")
    add_shape(doc, grp, "link_pins", "link_pins_D16", G.link_pins(), "steel")
    return grp


def _section(doc, grp, tag, fns):
    for name, label, fn, color in fns:
        add_shape(doc, grp, name + tag, label + tag, fn(), color)


def build_centre(doc, parent):
    grp = new_part(doc, parent, "Centre_section", "centre_section_1200_on_castors")
    _section(doc, grp, "", (
        ("centre_roof", "roof_alu_1.5", G.centre_roof, "hood"),
        ("centre_walls", "front_rear_walls_alu_1.5", G.centre_walls, "hood"),
        ("centre_frame", "roof_frame_alu_40x40x2", G.centre_frame, "alu"),
        ("centre_rails", "rails_alu_40x20_cameras_leds", G.centre_rails, "alu"),
        ("centre_curtains", "strip_curtains_PVC_2mm", G.centre_curtains, "curtain"),
        ("centre_clamps", "curtain_clamps_30x4", G.centre_clamps, "alu"),
        ("centre_cameras", "cameras_5MP_12mm_4x", G.centre_cameras, "camera"),
        ("centre_lenses", "lens_glass_4x", G.centre_lenses, "glass"),
        ("centre_leds", "led_strobe_bars_8x", G.centre_leds, "led"),
        ("centre_diffusers", "led_diffusers_8x", G.centre_diffusers, "diffuser"),
        ("uprights", "headstock_uprights_alu_40x40", G.uprights, "alu"),
        ("headstock", "headstock_plates_and_ears", G.headstock, "frame"),
        ("kingpin_plate", "kingpin_plate_10mm", G.kingpin_plate, "frame"),
        ("kingpins", "kingpins_D40_caps", G.kingpins, "steel"),
        ("act_base_posts", "actuator_base_posts", G.act_base_posts, "frame"),
        ("act_base_pins", "actuator_base_pins_D12", G.act_base_pins, "steel"),
        ("control_box", "control_box_IP66_computer_strobes_poe", G.control_box, "box"),
        ("antenna", "gnss_antenna_moved_from_robot", G.antenna, "white"),
    ))
    for s, tag in ((1, "right"), (-1, "left")):
        def side(shape, s=s):
            return shape if s > 0 else G.mirror_x(shape)
        add_shape(doc, grp, "castor_housing_" + tag, "castor_swivel_housing_" + tag, side(G.castor_housing_right()), "steel")
        add_shape(doc, grp, "castor_fork_" + tag, "castor_fork_stem_axle_" + tag, side(G.castor_fork_right()), "frame")
        w = new_part(doc, grp, "Castor_wheel_" + tag, "castor_wheel_250x60_" + tag)
        add_shape(doc, w, "castor_tyre_" + tag, "castor_tyre_" + tag, side(G.castor_wheel_right()), "rubber")
        add_shape(doc, w, "castor_rim_" + tag, "castor_rim_" + tag, side(G.castor_rim_right()), "rim")
    return grp


def build_wings(doc, parent, pl):
    for s, tag in ((1, "right"), (-1, "left")):
        def side(shape, s=s):
            return shape if s > 0 else G.mirror_x(shape)
        w = new_part(doc, parent, "Wing_" + tag, "wing_%s_900_swings_forward" % tag, pl["Wing_" + tag])
        for name, label, fn, color in (
                ("wing_roof", "roof_alu_1.5", G.wing_roof_right, "hood"),
                ("wing_walls", "walls_alu_1.5", G.wing_walls_right, "hood"),
                ("wing_frame", "roof_frame_alu_40x40x2", G.wing_frame_right, "alu"),
                ("wing_rails", "rails_alu_40x20", G.wing_rails_right, "alu"),
                ("wing_curtains", "strip_curtains_PVC_2mm", G.wing_curtains_right, "curtain"),
                ("wing_clamps", "curtain_clamps_30x4", G.wing_clamps_right, "alu"),
                ("wing_brush", "end_brush_strip", G.wing_brush_right, "brush"),
                ("wing_cameras", "cameras_5MP_12mm_3x", G.wing_cameras_right, "camera"),
                ("wing_lenses", "lens_glass_3x", G.wing_lenses_right, "glass"),
                ("wing_leds", "led_strobe_bars_6x", G.wing_leds_right, "led"),
                ("wing_diffusers", "led_diffusers_6x", G.wing_diffusers_right, "diffuser"),
                ("wing_pads", "arm_spacer_pads_12mm", G.wing_pads_right, "frame"),
                ("swing_arm", "swing_arm_sleeve_tie_rod", G.swing_arm_right, "frame"),
                ("rod_end_bracket", "actuator_rod_end_bracket", G.rod_end_bracket_right, "frame"),
                ("rod_end_pin", "actuator_rod_end_pin_D12", G.rod_end_pin_right, "steel")):
            add_shape(doc, w, "%s_%s" % (name, tag), "%s_%s" % (label, tag), side(fn()), color)
        xw = P.castor_wing_x
        add_shape(doc, w, "wing_castor_housing_" + tag, "wing_castor_swivel_housing_" + tag,
                  side(G.castor_housing_right(xw)), "steel")
        add_shape(doc, w, "wing_castor_fork_" + tag, "wing_castor_fork_stem_axle_" + tag, side(G.castor_fork_right(xw)),
                  "frame")
        cw = new_part(doc, w, "Wing_castor_wheel_" + tag, "wing_castor_wheel_250x60_" + tag)
        add_shape(doc, cw, "wing_castor_tyre_" + tag, "wing_castor_tyre_" + tag, side(G.castor_wheel_right(xw)), "rubber")
        add_shape(doc, cw, "wing_castor_rim_" + tag, "wing_castor_rim_" + tag, side(G.castor_rim_right(xw)), "rim")
        a = new_part(doc, parent, "Act_" + tag, "swing_actuator_%s_%dN_stroke_%d" % (tag, P.act_force, P.act_stroke),
                     pl["Act_" + tag])

        def act_side(shape, s=s):
            return shape if s > 0 else mirror_y(shape)
        add_shape(doc, a, "act_body_" + tag, "actuator_body_24V_" + tag, act_side(G.act_body()), "actuator")
        r = new_part(doc, a, "Act_%s_rod" % tag, "actuator_rod_%s" % tag, pl["Act_%s_rod" % tag])
        add_shape(doc, r, "act_rod_" + tag, "actuator_rod_eye_" + tag, act_side(G.act_rod()), "steel")


def build_into(doc, parent=None, left=0.0, right=0.0):
    """Put the scout in a document, in robot coordinates (also used by animate_dsc.py)."""
    pl = pose_placements(left, right)
    root = new_part(doc, parent, ROOT, "potato_disease_scout_3000")
    build_mount(doc, root)
    hood = new_part(doc, root, "Hood", "camera_hood_3000_folding_1200")
    build_centre(doc, hood)
    build_wings(doc, hood, pl)
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


ROBOT_GNSS = ("gnss_dome", "gnss_mount")


def build(left=0.0, right=0.0, save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Potato disease scout 3000"
    doc.Comment = ("Generated by build_dsc.py from dsc_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = furrow bottom z 0. Swing the wings with build_dsc.set_fold(l, r).")
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robot model not loaded:", exc)
    build_into(doc, robot, left, right)
    if robot is not None:
        set_robot_visible(bool(show_robot), doc)
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
    raise RuntimeError("no disease scout document open")


def scout_objects(doc):
    return [o for o in doc.getObject(ROOT).OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in scout_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible and o.Name not in ROBOT_GNSS


def export_step(doc, path):
    import Import
    objs = []
    for o in scout_objects(doc):
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


def check_interference(doc=None, tol=1.0, with_robot=True):
    """Volume overlap (mm3) in the current pose: scout parts among themselves and against the robot (the robot's
    GNSS antenna excluded: it moves to the hood roof)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in scout_objects(doc)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc) if o.Name not in ROBOT_GNSS] if with_robot else []
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    pairs += [(a, b) for a in mine for b in robot]
    return _overlaps(pairs, tol)


def _group_of(obj):
    parent = obj.getParentGeoFeatureGroup()
    while parent is not None:
        if parent.Name in MOVING:
            return parent.Name.replace("_rod", "")
        parent = parent.getParentGeoFeatureGroup()
    return "fixed"


def fit_poses(step=10.0):
    n = int(round(P.fold / step))
    return [(i * step, i * step) for i in range(n + 1)] + [(0.0, 45.0), (90.0, 0.0)]


def check_fit(doc=None, poses=None, tol=1.0):
    """Interference over the whole swing of both wings (pairs that move relative to each other). Must be empty."""
    doc = active_doc(doc)
    set_fold(doc=doc)
    out = {}
    mine = scout_objects(doc)
    group = {o.Name: _group_of(o) for o in mine}
    moving = [o for o in mine if group[o.Name] != "fixed"]
    fixed = [(o, global_shape(o)) for o in mine if group[o.Name] == "fixed"]
    fixed += [(o, global_shape(o)) for o in robot_objects(doc) if o.Name not in ROBOT_GNSS]
    for pose in poses or fit_poses():
        set_fold(*pose, doc=doc)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if group[mv[i][0].Name] != group[mv[j][0].Name]]
        hits = _overlaps(pairs, tol)
        if hits:
            out[str(pose)] = hits
    set_fold(doc=doc)
    return out


def _min_dist(objs, targets):
    best = (1e9, None, None)
    for o in objs:
        s = global_shape(o)
        for t in targets:
            ts = global_shape(t)
            if s.BoundBox.isValid() and ts.BoundBox.isValid():
                d = s.distToShape(ts)[0]
                if d < best[0]:
                    best = (d, o.Name, t.Name)
    return (round(best[0], 1), best[1], best[2])


def set_steering(left_deg, right_deg, doc):
    for name, angle in (("FL_steered", left_deg), ("FR_steered", right_deg)):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle))
    doc.recompute()


def tyre_envelope(steer):
    """Front tyres as plain cylinders (O430 x 100) at a steering angle (the lugged tyre is very slow in distToShape)."""
    out = []
    for s in (1, -1):
        c = Part.makeCylinder(P.robot_tire_d / 2, P.robot_tire_w, V(-P.robot_tire_w / 2, 0, 0), V(1, 0, 0))
        c.rotate(V(0, 0, 0), V(0, 0, 1), steer)
        c.translate(V(s * P.robot_wheel_x, P.robot_axle_y, P.robot_axle_z))
        out.append(c)
    return Part.makeCompound(out)


def clearance(doc=None):
    """Smallest distances (mm): hood (rear wall, curtains, headstock) to the front tyres at full steering lock,
    posts and links to the front wheel units, castors to the hood interior."""
    doc = active_doc(doc)
    out = {}
    hood = [doc.getObject(n) for n in ("centre_walls", "centre_curtains", "centre_clamps", "headstock", "links",
                                       "castor_tyre_right", "castor_fork_right")]
    for steer in (-P.robot_steer_max, 0.0, P.robot_steer_max):
        env = tyre_envelope(steer)
        best = min((global_shape(o).distToShape(env)[0], o.Name) for o in hood)
        out["hood_to_front_tyres_steer_%+d" % steer] = (round(best[0], 1), best[1])
    if doc.getObject("Robot") is not None:
        units = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_")) and "tire" not in o.Name]
        mount = [doc.getObject(n) for n in ("posts", "post_ears", "links", "link_pins", "post_plates", "post_bolts")]
        for steer in (-P.robot_steer_max, P.robot_steer_max):
            set_steering(steer, steer, doc)
            out["mount_to_front_units_steer_%+d" % steer] = _min_dist(mount, units)
        set_steering(0.0, 0.0, doc)
    inside = [doc.getObject(n) for n in ("centre_cameras", "centre_leds", "centre_rails", "centre_curtains")]
    out["castor_fork_to_hood_parts"] = _min_dist([doc.getObject("castor_fork_right")], inside)
    return out


# mass: bought parts with a fixed mass (kg), the rest from volume x density
N_CENTRE = len(G.CENTRE_CAMS)
N_WING = len(G.WING_CAMS)
MASS_FIXED = {"centre_cameras": N_CENTRE * P.cam_kg, "wing_cameras": N_WING * P.cam_kg, "centre_lenses": 0.0,
              "wing_lenses": 0.0, "centre_leds": 2 * N_CENTRE * P.led_kg, "wing_leds": 2 * N_WING * P.led_kg,
              "centre_diffusers": 0.0, "wing_diffusers": 0.0, "control_box": 5.0, "antenna": 0.0,
              "castor_tyre": 1.6, "castor_rim": 0.4, "castor_fork": 2.0, "castor_housing": 0.5,
              "wing_castor_tyre": 1.6, "wing_castor_rim": 0.4, "wing_castor_fork": 2.0, "wing_castor_housing": 0.5,
              "act_body": P.act_kg - 0.5, "act_rod": 0.5}
DENSITY = (("centre_roof", 2.7e-6), ("centre_walls", 2.7e-6), ("centre_frame", 2.7e-6), ("centre_rails", 2.7e-6),
           ("centre_clamps", 2.7e-6), ("uprights", 2.7e-6), ("wing_roof", 2.7e-6), ("wing_walls", 2.7e-6),
           ("wing_frame", 2.7e-6), ("wing_rails", 2.7e-6), ("wing_clamps", 2.7e-6), ("centre_curtains", 1.4e-6),
           ("wing_curtains", 1.4e-6), ("wing_brush", 0.6e-6))
STEEL = 7.85e-6


def _mass_cg(obj):
    shape = global_shape(obj)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    for key in sorted(MASS_FIXED, key=len, reverse=True):
        if obj.Name.startswith(key):
            return MASS_FIXED[key], cg
    dens = STEEL
    for key, d in DENSITY:
        if obj.Name.startswith(key):
            dens = d
            break
    return vol * dens, cg


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) in the current pose."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []

    def r(v):
        return (round(v.x), round(v.y), round(v.z))
    m, c = _sum(scout_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": r(c)}
    for name in ("Mount", "Hood", "Centre_section", "Wing_right", "Act_right"):
        ms, cs = _sum(objs_of(name))
        out[name.lower() + "_kg"] = round(ms, 2)
        out[name.lower() + "_cg"] = r(cs)
    w = out["wing_right_cg"]
    out["wing_cg_rel"] = (round(w[0] - P.pivot[0]), round(w[1] - P.pivot[1]))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in scout_objects(doc):
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin)), (
        round(bb.XMax), round(bb.YMax), round(bb.ZMax))


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
    tgt = V(*target) if target is not None else V(0, 0, 600)
    eye = tgt - d * 12000.0
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


FIELD = ("render_ridges", "render_plants", "render_sick")


def add_field(doc, y=(-1500.0, 3500.0), x=(-2300.0, 2300.0), top=650.0):
    """Ridges and potato plants for the renders (plants only outside the robot wheels' furrows)."""
    import dsc_field as FLD
    r = doc.addObject("Part::Feature", FIELD[0])
    r.Shape = G.ridges(x, y)
    r.ViewObject.ShapeColor = (0.55, 0.42, 0.30)
    healthy, sick = [], []
    for (px, py, t, s, ill) in FLD.plants(x, y, top=top):
        (sick if ill else healthy).append(G.plant(px, py, t, s))
    p = doc.addObject("Part::Feature", FIELD[1])
    p.Shape = Part.makeCompound(healthy)
    p.ViewObject.ShapeColor = (0.25, 0.52, 0.20)
    q = doc.addObject("Part::Feature", FIELD[2])
    q.Shape = Part.makeCompound(sick) if sick else Part.Shape()
    q.ViewObject.ShapeColor = (0.70, 0.62, 0.20)
    return r


def add_footprints(doc, zc=600.0):
    obj = doc.addObject("Part::Feature", "render_footprints")
    obj.Shape = Part.makeCompound([G.footprint(x, zc) for x in P.cam_x])
    obj.ViewObject.ShapeColor = (0.98, 0.82, 0.20)
    obj.ViewObject.Transparency = 50
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


HOOD_SKIN = ("centre_roof", "centre_walls", "wing_roof_right", "wing_walls_right", "wing_roof_left", "wing_walls_left",
             "centre_curtains", "wing_curtains_right", "wing_curtains_left", "control_box", "antenna")


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_field(doc)
    out.append(save_view("1_work_iso_on_robot.png", (1.0, 1.15, -0.8), target=(0, 650, 650), height=4300))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, 700, 800), height=2300))
    out.append(save_view("3_front_over_ridges.png", (0.0, -1.0, -0.08), target=(0, 0, 700), height=2100,
                         size_px=(1700, 900)))
    set_fold(90.0, 90.0, doc)
    out.append(save_view("4_folded_iso_transport.png", (-1.0, -1.1, -0.7), target=(0, 1100, 800), height=3500))
    out.append(save_view("5_folded_front_1200.png", (0.0, -1.0, -0.05), target=(0, 0, 800), height=2000))
    set_fold(0.0, 45.0, doc)
    out.append(save_view("6_right_wing_swinging_top.png", (0.0, 0.0, -1.0), target=(0, 1200, 0), up=(0.0, 1.0, 0.0),
                         height=3600))
    set_fold(doc=doc)
    remove(doc, FIELD)
    set_visible(doc, HOOD_SKIN, False)
    add_footprints(doc)
    out.append(save_view("7_inside_cameras_leds_footprints.png", (-0.55, -0.9, 0.8), target=(0, 1050, 900),
                         height=3300))
    remove(doc, ["render_footprints"])
    set_visible(doc, HOOD_SKIN, True)
    set_robot_visible(False, doc)
    set_fold(0.0, 30.0, doc)
    out.append(save_view("8_kingpin_actuator_detail.png", (-0.6, -0.9, -0.8), target=(120, 1200, 1530), height=900))
    set_fold(90.0, 90.0, doc)
    set_robot_visible(True, doc)
    out.append(save_view("9_parallelogram_castor.png", (-1.0, -0.25, -0.15), target=(250, 750, 750), height=1600))
    App.closeDocument(doc.Name)
    build()
    return out
