"""Model of the parallel hitch (headstock + parallel linkage as the liquid fertilizer applicator advanced V2, LA36 on
the diagonal with a slot, A-frame triangle on the carrier) with the small cultivator on the Bruut OpenAgbot.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_tpp
    build_tpp.build()                      # saves FCStd and STEP (work pose)
    build_tpp.set_pose(theta=28)           # link angle (deg, + = up), LA36 carrying
    build_tpp.set_pose(-12, act_len=487)   # work, LA36 at its work length (rod pin floats in the slot)
    build_tpp.check_interference()         # overlap in the current pose (must be empty)
    build_tpp.check_poses()                # lift and float poses (must be empty)
    build_tpp.clearance(), build_tpp.ground_contact(), build_tpp.mass_properties()
    build_tpp.render_all()                 # all images in previews/
"""
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tpp_params as P
import tpp_parts as G
import tpa_params as Q
import tpa_parts as GA
import tph_parts as TG
import build_tpa as BA

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = BA.AGBOT_FOLDER
DOC_NAME = "Three_Point_Hitch_Parallel"
SAVE_BASE = os.path.join(FOLDER, "Three_Point_Hitch_Parallel")
ROOT = "TPP_hitch"
COLOR = BA.COLOR
new_part = BA.new_part
add_shape = BA.add_shape
global_shape = BA.global_shape
ROD_REF = P.act_retracted
SIDES = ((-1, "left"), (1, "right"))
LINKS = [(sx, tag, up, "lo" if not up else "hi") for sx, tag in SIDES for up in (False, True)]


def link_placement(theta, upper):
    f = P.front_pins()[1 if upper else 0]
    return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -(theta - P.theta_work)), V(0, f[0], f[1]))


def carrier_placement(theta):
    d = P.shift(theta)
    return App.Placement(V(0, d[0], d[1]), App.Rotation())


def build_mount(doc, parent):
    grp = new_part(doc, parent, "TPP_Mount", "mount_rear_toolbar_and_headstock")
    add_shape(doc, grp, "toolbar", "rear_toolbar_80x80x4_L900", TG.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_caps", "toolbar_end_caps_PE", TG.toolbar_caps(), "plastic")
    for sx, tag in SIDES:
        add_shape(doc, grp, "hanger_top_" + tag, "hanger_top_plate_10mm_" + tag, TG.hanger_top(sx), "frame")
        add_shape(doc, grp, "hanger_webs_" + tag, "hanger_webs_6mm_" + tag, TG.hanger_webs(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_M10_" + tag, TG.hanger_bolts(sx), "zinc")
    add_shape(doc, grp, "hs_cheeks", "headstock_cheeks_8mm_4x_welded_on_toolbar", G.hs_cheeks(), "frame")
    add_shape(doc, grp, "hs_cross", "headstock_top_cross_tube_40x40x3", G.hs_cross(), "frame")
    add_shape(doc, grp, "hs_slot_plates", "LA36_rod_slot_plates_2x8mm_slot_%d" % round(P.float_slot()),
              G.hs_slot_plates(), "frame")
    add_shape(doc, grp, "hs_pins", "front_link_pins_D16_4x", G.hs_pins(), "zinc")
    return grp


def build_links(doc, parent, theta=P.theta_work):
    grp = new_part(doc, parent, "TPP_Links", "parallel_links_30x30x3_L%d" % P.link_len)
    for sx, tag, up, lvl in LINKS:
        lk = new_part(doc, grp, "TPP_Link_%s_%s" % (lvl, tag), "link_%s_%s_turns_about_front_pin" % (lvl, tag),
                      link_placement(theta, up))
        add_shape(doc, lk, "link_%s_%s" % (lvl, tag), "link_30x30x3_%s_%s" % (lvl, tag), G.link(sx, up), "frame")
    return grp


def build_carrier(doc, parent, theta=P.theta_work):
    grp = new_part(doc, parent, "TPP_Carrier", "carrier_with_male_A_frame_translates", carrier_placement(theta))
    add_shape(doc, grp, "carrier_plates", "carrier_plates_8mm_4x_LA36_lugs", G.carrier_plates(), "frame")
    add_shape(doc, grp, "carrier_pins", "rear_link_pins_D16_LA36_body_pin_D12", G.carrier_pins(), "zinc")
    add_shape(doc, grp, "male_frame", "A_frame_male_triangle_40x40x3", G.male_frame(), "coupler")
    add_shape(doc, grp, "male_latch", "A_frame_latch_pin_D20_T_handle", G.male_latch(), "handle")
    return grp


def build_actuator(doc, parent, theta=P.theta_work, act_len=None):
    grp = new_part(doc, parent, "TPP_Actuator", "linak_LA36_%s_stroke%d_diagonal" % (P.act_variant, P.act_stroke))
    add_shape(doc, grp, "act_body", "linak_LA36_24V_housing_motor_outer_tube",
              GA.la36_body(P.act_motor_side, P.act_retracted), "actuator")
    pin_half = Q.act_rod_eye_c / 2.0 + Q.act_eye_clear + 8.0 + 4.0
    add_shape(doc, grp, "act_rod", "linak_LA36_inner_tube_rod_eye_pin_D12",
              GA.la36_rod(ROD_REF, P.act_retracted, pin_half, P.act_stroke), "chrome")
    set_actuator(doc, theta, act_len)
    return grp


def set_actuator(doc, theta, act_len=None):
    pb, pr, L = GA.la36_placements(P.body_pin(theta), P.act_pin(theta, act_len), ROD_REF)
    doc.getObject("act_body").Placement = pb
    doc.getObject("act_rod").Placement = pr
    return L


def build_implement(doc, parent, theta=P.theta_work):
    grp = new_part(doc, parent, "TPP_Implement", "small_cultivator_with_female_A_frame", carrier_placement(theta))
    b = P.cp_base
    add_shape(doc, grp, "imp_frame", "cultivator_toolbar_60x60_female_A_frame_stays_gauge_arms",
              GA.cultivator_frame(b), "implement")
    add_shape(doc, grp, "tine_clamps", "tine_clamps_5x", GA.cult_clamps(b), "zinc")
    add_shape(doc, grp, "tines", "S_tines_32x10_5x", GA.cult_tines(b), "steel")
    add_shape(doc, grp, "shares", "duckfoot_shares_100", GA.cult_shares(b), "tine")
    add_shape(doc, grp, "gauge_wheels", "gauge_wheels_D250x80_2x", GA.cult_wheels(b), "rubber")
    add_shape(doc, grp, "wheel_axles", "gauge_wheel_axles_D20", GA.cult_axles(b), "zinc")
    return grp


def build_into(doc, parent=None, theta=P.theta_work):
    root = new_part(doc, parent, ROOT, "three_point_hitch_parallel_LA36")
    build_mount(doc, root)
    build_links(doc, root, theta)
    build_carrier(doc, root, theta)
    build_actuator(doc, root, theta)
    build_implement(doc, root, theta)
    return root


def set_pose(theta=P.theta_work, doc=None, act_len=None, implement=True):
    doc = active_doc(doc)
    for sx, tag, up, lvl in LINKS:
        doc.getObject("TPP_Link_%s_%s" % (lvl, tag)).Placement = link_placement(theta, up)
    pl = carrier_placement(theta)
    doc.getObject("TPP_Carrier").Placement = pl
    if implement and doc.getObject("TPP_Implement") is not None:
        doc.getObject("TPP_Implement").Placement = pl
    return set_actuator(doc, theta, act_len)


def build_robot(doc):
    return BA.build_robot(doc)


def build(save=True, show_robot=False, step=True, theta=P.theta_work):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Three-point hitch parallel"
    doc.Comment = ("Generated by build_tpp.py from tpp_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Work pose; build_tpp.set_pose() lifts the implement.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, theta)
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


objects_of = BA.objects_of


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


_overlaps = BA._overlaps

JOINTS = {("hs_pins", "hs_cheeks"), ("carrier_pins", "carrier_plates"), ("carrier_pins", "act_body"),
          ("act_rod", "hs_slot_plates"), ("act_body", "act_rod"), ("male_latch", "male_frame"),
          ("male_latch", "imp_frame"), ("hs_cross", "hs_cheeks"), ("carrier_plates", "male_frame"),
          ("tine_clamps", "tines"), ("tine_clamps", "imp_frame"), ("tines", "shares"), ("wheel_axles", "imp_frame"),
          ("wheel_axles", "gauge_wheels"), ("hanger_bolts_left", "hanger_top_left"),
          ("hanger_bolts_right", "hanger_top_right"), ("hs_slot_plates", "hs_cross")}


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x.startswith("hanger_bolts") and y.startswith("lower_beam"):
            return True
        if x in ("hs_pins", "carrier_pins") and y.startswith("link_"):
            return True
    return False


MOVING = ("TPP_Links", "TPP_Carrier", "TPP_Actuator", "TPP_Implement")


def check_interference(doc=None, tol=1.0):
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_poses(doc=None, tol=1.0, poses=None):
    """Interference over the lift poses (LA36 carrying) and the float poses (LA36 at its work length)."""
    doc = active_doc(doc)
    moving = [o for n in MOVING for o in objects_of(doc, n)]
    names = {o.Name for o in moving}
    fixed = [(o, global_shape(o)) for o in objects_of(doc, ROOT) + robot_objects(doc) if o.Name not in names]
    out = {}
    lw = P.act_work_length()
    lo, hi = P.float_limits(lw)
    poses = poses or [(x, None) for x in P.THETA_POSES] + [(lo, lw), (P.theta_work, lw), (hi, lw)]
    for theta, act_len in poses:
        set_pose(theta, doc, act_len)
        mv = [(o, global_shape(o)) for o in moving]
        pairs = [(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)]
        pairs += [(mv[i], mv[j]) for i in range(len(mv)) for j in range(i + 1, len(mv))
                  if not _joint(mv[i][0].Name, mv[j][0].Name)]
        hits = _overlaps(pairs, tol)
        if hits:
            out[str((round(theta, 2), act_len))] = hits
    set_pose(doc=doc)
    return out


def clearance(doc=None, names=("RL_top_plate", "RR_top_plate", "RL_side_l", "RR_side_r")):
    doc = active_doc(doc)
    targets = [global_shape(doc.getObject(n)) for n in names if doc.getObject(n) is not None]
    for sx in (-1, 1):
        targets.append(Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w,
                                         V(sx * P.robot_wheel_x - P.robot_tire_w / 2.0, -P.robot_axle_y, 215.0),
                                         V(1, 0, 0)))
    out = {}
    for theta in (P.theta_work, P.theta_lift):
        set_pose(theta, doc)
        best = (1e9, None)
        for o in [o for n in MOVING for o in objects_of(doc, n)]:
            s = global_shape(o)
            for t in targets:
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name)
        out[theta] = (round(best[0], 1), best[1])
    set_pose(doc=doc)
    return out


def ground_contact(doc=None):
    doc = active_doc(doc)
    out = {}
    for theta in (P.theta_work, P.theta_lift):
        set_pose(theta, doc)
        out[theta] = {n: round(global_shape(doc.getObject(n)).BoundBox.ZMin, 1) for n in ("shares", "gauge_wheels")}
    set_pose(doc=doc)
    return out


MASS_FIXED = {"act_body": P.act_mass() - 0.6, "act_rod": 0.6}


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
    for key, d in BA.DENSITY:
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
    doc = active_doc(doc)
    set_pose(doc=doc)
    out = {}
    for name in (ROOT,) + ("TPP_Mount",) + MOVING:
        m, c = sum_mass(objects_of(doc, name))
        key = name.replace("TPP_", "").lower()
        out[key + "_kg"] = round(m, 1)
        out[key + "_cg"] = (round(c.x), round(c.y), round(c.z))
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


def set_visible(doc, group, visible):
    for o in objects_of(doc, group):
        o.ViewObject.Visibility = visible


def render_all():
    out = []
    doc = build(save=False, show_robot=True, step=False)
    App.setActiveDocument(doc.Name)
    BA.add_floor(doc, y=(-1900.0, 900.0), x=(-1000.0, 1000.0))
    out.append(save_view("1_iso_rear_right_on_robot.png", (-1.0, 1.2, -0.7), target=(0, -800, 450)))
    out.append(save_view("2_side_work.png", (1.0, 0.0, 0.0), target=(0, -1000, 450), height=1300))
    set_pose(P.theta_lift, doc)
    out.append(save_view("3_side_lifted.png", (1.0, 0.0, 0.0), target=(0, -1000, 450), height=1300))
    out.append(save_view("4_iso_lifted.png", (-1.0, 1.2, -0.7), target=(0, -900, 450), height=1700))
    lw = P.act_work_length()
    lo, hi = P.float_limits(lw)
    set_pose(lo, doc, lw)
    out.append(save_view("5_side_float_low.png", (1.0, 0.0, 0.0), target=(0, -1000, 450), height=1300))
    set_pose(hi, doc, lw)
    out.append(save_view("6_side_float_high.png", (1.0, 0.0, 0.0), target=(0, -1000, 450), height=1300))
    set_pose(doc=doc)
    BA.remove(doc, [BA.GROUND])
    out.append(save_view("7_top.png", (0.0, 0.0, -1.0), target=(0, -850, 0), up=(0.0, 1.0, 0.0), height=2100))
    set_robot_visible(False, doc)
    set_visible(doc, "TPP_Implement", False)
    out.append(save_view("8_headstock_linkage_LA36.png", (-1.0, 0.8, -0.45), target=(0, -1000, 500), height=1050))
    out.append(save_view("9_headstock_from_above.png", (-0.6, 0.5, -1.0), target=(0, -950, 550), height=950))
    App.closeDocument(doc.Name)
    build()
    return out
