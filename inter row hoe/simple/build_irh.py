"""Model of the inter-row hoe on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_irh
    build_irh.build()                      # saves FCStd and STEP (work pose: hoe on the ground, shift 0)
    build_irh.set_pose(lift=25, shift=75)  # lift of the arms (deg, + = up), side shift (mm, + = right)
    build_irh.check_interference()         # overlap in the current pose (must be empty)
    build_irh.check_poses()                # overlap over the lift poses x shift positions (must be empty)
    build_irh.clearance()                  # smallest distance to the rear tyres and wheel units, work and transport
    build_irh.ground_contact()             # lowest point of gauge wheel and shares
    build_irh.row_margin()                 # distance of the L-blades to the crop row
    build_irh.mass_properties()
    build_irh.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import irh_params as P
import irh_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Inter_Row_Hoe"
SAVE_BASE = os.path.join(FOLDER, "Inter_Row_Hoe")
ROOT = "Inter_row_hoe"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "tine": (0.15, 0.15, 0.16),
    "rubber": (0.12, 0.12, 0.12),
    "actuator": (0.25, 0.26, 0.28),
    "plastic": (0.10, 0.10, 0.10),
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



def lift_placement(lift_deg):
    """Rotation of the carrier about the pivot axis (x); + lift = hoe up (it is behind the pivot)."""
    c = V(0, P.pivot[0], P.pivot[1])
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -lift_deg), c)


def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_rear_toolbar")
    add_shape(doc, grp, "toolbar", "rear_toolbar_80x80x4_L900", G.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_caps", "toolbar_end_caps_PE", G.toolbar_caps(), "plastic")
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "hanger_top_" + tag, "hanger_top_plate_10mm_" + tag, G.hanger_top(sx), "frame")
        add_shape(doc, grp, "hanger_webs_" + tag, "hanger_webs_6mm_" + tag, G.hanger_webs(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_M10_" + tag, G.hanger_bolts(sx), "zinc")
    add_shape(doc, grp, "pivot_lugs", "pivot_lugs_8mm_4x", G.pivot_lugs(), "frame")
    add_shape(doc, grp, "pivot_pins", "pivot_pins_D20_R_clip", G.pivot_pins(), "zinc")
    add_shape(doc, grp, "act_mast", "actuator_mast_2x8mm", G.act_mast(), "frame")
    return grp


def shift_placement(shift):
    return App.Placement(V(shift, 0, 0), App.Rotation())


def build_lift(doc, parent, lift=P.lift_work, shift=0.0):
    grp = new_part(doc, parent, "Lift", "carrier_turns_about_pivot", lift_placement(lift))
    add_shape(doc, grp, "carrier", "carrier_weldment_arms_main_beam_60x60_rail_plate", G.carrier(), "frame")
    add_shape(doc, grp, "rails", "linear_rails_HGR15_L%d_2x" % (2 * P.rail_x), G.rails(), "steel")
    add_shape(doc, grp, "bearings", "screw_bearings_BK12_BF12", G.bearings(), "actuator")
    add_shape(doc, grp, "screw", "ball_screw_SFU1610", G.screw(), "steel")
    add_shape(doc, grp, "coupling", "jaw_coupling_D25", G.coupling(), "zinc")
    flange, body = G.motor()
    add_shape(doc, grp, "motor_flange", "motor_flange_8mm", flange, "frame")
    add_shape(doc, grp, "motor", "closed_loop_stepper_NEMA23_2Nm", body, "actuator")
    sh = new_part(doc, grp, "Shift", "shift_plate_slides_along_x", shift_placement(shift))
    add_shape(doc, sh, "carriages", "carriages_HGH15CA_4x", G.carriages(), "steel")
    add_shape(doc, sh, "shift_plate", "shift_plate_10mm", G.shift_plate(), "frame")
    add_shape(doc, sh, "nut_housing", "ball_nut_housing", G.nut_housing(), "actuator")
    add_shape(doc, sh, "mast", "camera_mast_40x40", G.mast(), "frame")
    add_shape(doc, sh, "camera_bracket", "camera_bracket_2x4mm", G.camera_bracket(), "frame")
    add_shape(doc, sh, "camera", "row_camera_tilted_%d_deg" % P.cam_tilt, G.camera(), "plastic")
    for xu, tag in zip(P.unit_x, ("left", "right")):
        u = new_part(doc, sh, "Unit_" + tag, "hoe_unit_" + tag)
        add_shape(doc, u, "head_" + tag, "parallelogram_head_" + tag, G.head(xu), "frame")
        add_shape(doc, u, "links_" + tag, "parallelogram_links_40x10_" + tag, G.links(xu), "frame")
        add_shape(doc, u, "pins_" + tag, "link_pins_D12_" + tag, G.pins(xu), "zinc")
        add_shape(doc, u, "unit_frame_" + tag, "unit_frame_post_beam_cross_bar_" + tag, G.unit_frame(xu), "frame")
        add_shape(doc, u, "wheel_" + tag, "gauge_wheel_D%dx%d_%s" % (P.wheel_d, P.wheel_w, tag), G.gauge_wheel(xu),
                  "rubber")
        add_shape(doc, u, "axle_" + tag, "gauge_wheel_axle_D16_" + tag, G.wheel_axle(xu), "zinc")
        share, shank = G.goosefoot(xu)
        add_shape(doc, u, "share_" + tag, "goosefoot_share_%d_%s" % (P.share_w, tag), share, "tine")
        blades, lshanks = G.lblades(xu)
        add_shape(doc, u, "lblades_" + tag, "L_blades_2x_" + tag, blades, "tine")
        add_shape(doc, u, "shanks_" + tag, "shanks_40x12_3x_" + tag, [shank] + lshanks, "steel")
    return grp


def build_actuator(doc, parent, lift=P.lift_work):
    grp = new_part(doc, parent, "Actuator", "lift_actuator_24V_1500N_stroke_100")
    body, rod, _ = G.actuator(lift)
    add_shape(doc, grp, "act_body", "actuator_body", body, "actuator")
    add_shape(doc, grp, "act_rod", "actuator_rod_clevis", rod, "steel")
    return grp


def build_into(doc, parent=None, lift=P.lift_work, shift=0.0):
    """Put the hoe in a document, in robot coordinates."""
    root = new_part(doc, parent, ROOT, "inter_row_hoe_simple")
    build_mount(doc, root)
    build_lift(doc, root, lift, shift)
    build_actuator(doc, root, lift)
    return root


def set_pose(lift=P.lift_work, shift=0.0, doc=None):
    doc = active_doc(doc)
    doc.getObject("Lift").Placement = lift_placement(lift)
    doc.getObject("Shift").Placement = shift_placement(shift)
    body, rod, _ = G.actuator(lift)
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod


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


def build(save=True, show_robot=False, step=True, lift=P.lift_work, shift=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Inter-row hoe simple"
    doc.Comment = ("Generated by build_irh.py from irh_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Work pose; build_irh.set_pose() lifts and shifts the hoe.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, lift, shift)
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


# pins, bolts and shanks pass through holes in or touch the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "carrier"), ("pivot_pins", "pivot_lugs"), ("act_body", "act_mast"), ("act_rod", "carrier"),
          ("act_body", "act_rod"), ("hanger_bolts_left", "hanger_top_left"), ("hanger_bolts_right", "hanger_top_right"),
          ("screw", "nut_housing"), ("screw", "bearings"), ("screw", "coupling")}
UNIT_JOINTS = (("pins", "head"), ("pins", "links"), ("pins", "unit_frame"), ("axle", "wheel"), ("axle", "unit_frame"),
               ("shanks", "share"), ("shanks", "lblades"))


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS or (a.startswith("hanger_bolts") and b.startswith("lower_beam")):
        return True
    for p, q in UNIT_JOINTS:
        for t in ("_left", "_right"):
            if (a, b) in ((p + t, q + t), (q + t, p + t)):
                return True
    return False


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: hoe parts among themselves and against the robot.
    Pins, bolts and shanks in their own holes are skipped (JOINTS)."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0):
    """Interference over the lift poses x shift positions: the lift group and actuator against the fixed parts, and
    the shift group against the rest of the lift group. Must be empty."""
    doc = active_doc(doc)
    lift_objs = objects_of(doc, "Lift") + objects_of(doc, "Actuator")
    shift_names = {o.Name for o in objects_of(doc, "Shift")}
    names = {o.Name for o in lift_objs}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    for lift in P.LIFT_POSES:
        for shift in P.SHIFT_POSES:
            set_pose(lift, shift, doc)
            mv = [(o, global_shape(o)) for o in lift_objs]
            pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
            pairs += [(a, b) for a in mv for b in mv if a[0].Name in shift_names and b[0].Name not in shift_names
                      and not _joint(a[0].Name, b[0].Name)]
            hits = _overlaps(pairs, tol)
            if hits:
                out[(lift, shift)] = hits
    set_pose(doc=doc)
    return out


def clearance(doc=None, names=("RL_top_plate", "RR_top_plate", "RL_side_l", "RR_side_r")):
    """Smallest distance (mm) of the lift group and actuator to the rear tyres (plain cylinder) and the wheel
    brackets, work and transport, shift at both ends."""
    doc = active_doc(doc)
    targets = [global_shape(doc.getObject(n)) for n in names if doc.getObject(n) is not None]
    for sx in (-1, 1):
        targets.append(Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w,
                                         V(sx * P.robot_wheel_x - P.robot_tire_w / 2.0, -P.robot_axle_y, 215.0),
                                         V(1, 0, 0)))
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        best = (1e9, None)
        for shift in (-P.shift_stroke, P.shift_stroke):
            set_pose(lift, shift, doc)
            for o in objects_of(doc, "Lift") + objects_of(doc, "Actuator"):
                s = global_shape(o)
                for t in targets:
                    d = s.distToShape(t)[0]
                    if d < best[0]:
                        best = (d, o.Name)
        out[lift] = (round(best[0], 1), best[1])
    set_pose(doc=doc)
    return out


def ground_contact(doc=None):
    """Lowest point (z) of gauge wheel and shares, work and transport."""
    doc = active_doc(doc)
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        set_pose(lift, 0.0, doc)
        out[lift] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1)
                     for n in ("wheel_left", "share_left", "lblades_left")}
    set_pose(doc=doc)
    return out


def row_margin(doc=None):
    """Distance (mm) from the outer edge of the L-blades to the crop row at shift 0 (the band left to the guidance)."""
    doc = active_doc(doc)
    bb = global_shape(doc.getObject("lblades_right")).BoundBox
    return {"blade_edge_x": round(bb.XMax, 1), "row_x": P.row_spacing, "margin": round(P.row_spacing - bb.XMax, 1)}




MASS_FIXED = {"act_body": P.act_kg - 0.6, "act_rod": 0.6}
MASS_FIXED.update({"motor": P.motor_kg, "camera": 0.6})
DENSITY = (("toolbar_caps", 0.95e-6), ("wheel_", P.rubber))


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
    """Mass (kg) and centre of gravity (robot coordinates) of the whole hoe, the lift group, the shift group and the mount."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Lift", "Shift", "Mount"):
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
    add_floor(doc, y=(-1900.0, 900.0), x=(-1100.0, 1100.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.2, -0.7), target=(0, -700, 350)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, -900, 400), height=1600))
    set_pose(P.lift_transport, 0.0, doc)
    out.append(save_view("3_side_transport.png", (1.0, 0.0, 0.0), target=(0, -900, 400), height=1600))
    set_pose(P.lift_work, P.shift_stroke, doc)
    remove(doc, [GROUND])
    out.append(save_view("4_top_shift_75.png", (0.0, 0.0, -1.0), target=(0, -700, 0), up=(0.0, 1.0, 0.0),
                         height=2500))
    set_pose(doc=doc)
    out.append(save_view("5_rear_rows.png", (0.0, 1.0, 0.0), target=(0, -1000, 350), height=1300))
    set_robot_visible(False, doc)
    out.append(save_view("6_unit_iso_from_below.png", (-0.8, 1.0, 0.45), target=(375, -1350, 150), height=900))
    out.append(save_view("7_shift_axis_detail.png", (-0.7, 1.0, -0.5), target=(150, -1040, 330), height=800))
    App.closeDocument(doc.Name)
    build()
    return out
