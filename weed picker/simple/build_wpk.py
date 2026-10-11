"""Model of the weed picker (simple) on the Bruut OpenAgbot (standard robot).

Use in FreeCAD (folder in sys.path, or via run_in_freecad.py):
    import build_wpk
    build_wpk.build()                     # saves Weed_Picker.FCStd and .step (default cut height)
    build_wpk.check_interference()        # overlap (must be empty)
    build_wpk.check_heights()             # overlap over the height range and with the deck floated up
    build_wpk.clearance()                 # smallest distance of the deck and links to the steered front wheels
    build_wpk.mass_properties()           # mass and centre of gravity
    build_wpk.render_all()                # all images in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import wpk_params as P
import wpk_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_NAME = "Weed_Picker"
SAVE_BASE = os.path.join(FOLDER, DOC_NAME)
ROOT = "Weed_picker"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "deck": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "blade": (0.30, 0.31, 0.33),
    "spindle": (0.20, 0.20, 0.22),
    "motor": (0.08, 0.08, 0.08),
    "coupling": (0.85, 0.75, 0.10),
    "actuator": (0.55, 0.57, 0.60),
    "box": (0.55, 0.57, 0.60),
    "ground": (0.45, 0.62, 0.32),
    "stem": (0.33, 0.52, 0.20),
    "leaves": (0.25, 0.48, 0.18),
    "thistle": (0.62, 0.30, 0.68),
    "ragwort": (0.98, 0.82, 0.10),
    "dock": (0.55, 0.25, 0.12),
    "chips": (0.86, 0.80, 0.36),
}


# ---------------------------------------------------------------------
# Tree helpers (same as build_apm.py)
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
    grp = new_part(doc, parent, "Mount", "mount_plate_lugs")
    add_shape(doc, grp, "mount_plate", "mount_plate_8mm", G.mount_plate(), "frame")
    add_shape(doc, grp, "mount_bolts", "mount_bolts_8x_M10", G.mount_bolts(), "zinc")
    add_shape(doc, grp, "robot_lugs", "link_lugs_2x_10mm", G.robot_lugs(), "frame")
    add_shape(doc, grp, "actuator_lug", "actuator_lug_10mm", G.actuator_lug(), "frame")
    add_shape(doc, grp, "robot_pins", "pins_M16_robot_side", G.robot_pins(), "zinc")
    return grp


def build_controller(doc, parent):
    grp = new_part(doc, parent, "Controller", "controller_box_2_BLDC_drivers")
    add_shape(doc, grp, "box_base", "controller_base_plate_3mm", G.box_base(), "zinc")
    add_shape(doc, grp, "controller_box", "controller_box_IP66_2x48V_25A", G.controller_box(), "box")
    add_shape(doc, grp, "box_bolts", "controller_bolts_M8", G.box_bolts(), "zinc")
    return grp


def build_linkage(doc, parent):
    top = new_part(doc, parent, "Top_links", "top_links_turn_about_robot_pivot")
    add_shape(doc, top, "top_links", "top_links_4x_flat_40x6", G.top_links(), "frame")
    bot = new_part(doc, parent, "Bottom_links", "bottom_links_turn_about_robot_pivot")
    add_shape(doc, bot, "bottom_links", "bottom_links_4x_flat_40x6", G.bottom_links(), "frame")
    act = new_part(doc, parent, "Actuator", "actuator_redrawn_per_height")
    body, rod, links = G.actuator_shapes()
    add_shape(doc, act, "act_body", "linear_actuator_150mm_4000N", body, "actuator")
    add_shape(doc, act, "act_rod", "actuator_rod_and_eye", rod, "steel")
    add_shape(doc, act, "float_link", "float_link_2x_flat_30x6_slot60", links, "frame")


def build_rotor(doc, parent, side):
    tag = "R" if side > 0 else "L"
    name = "right" if side > 0 else "left"
    rotor = new_part(doc, parent, "Rotor_" + tag, "rotor_%s_turns" % name)
    add_shape(doc, rotor, tag + "_shaft", "spindle_shaft_D19_" + tag, G.spindle_shaft(side), "steel")
    add_shape(doc, rotor, tag + "_boss", "blade_boss_" + tag, G.boss(side), "spindle")
    add_shape(doc, rotor, tag + "_bar", "blade_bar_340x60x12_" + tag, G.blade_bar(side), "frame")
    add_shape(doc, rotor, tag + "_blades", "swinging_blades_2x_50x6_" + tag, G.blades(side), "blade")
    add_shape(doc, rotor, tag + "_blade_bolts", "blade_bolts_2x_M16_" + tag, G.blade_bolts(side), "zinc")
    add_shape(doc, rotor, tag + "_coupling", "jaw_coupling_D55_" + tag, G.coupling(side), "coupling")
    add_shape(doc, rotor, tag + "_motor_shaft", "motor_shaft_D19_" + tag, G.motor_shaft(side), "steel")
    return rotor


def build_deck(doc, parent):
    deck = new_part(doc, parent, "Deck", "deck_moves_with_linkage")
    add_shape(doc, deck, "deck_plate", "deck_plate_3mm_stadium", G.deck_plate(), "deck")
    add_shape(doc, deck, "skirt", "skirt_3mm_rear_open", G.skirt(), "deck")
    add_shape(doc, deck, "swath_boards", "swath_boards_2x_4mm", G.swath_boards(), "deck")
    add_shape(doc, deck, "crossbeam", "crossbeam_RHS_50x40x3", G.crossbeam(), "frame")
    add_shape(doc, deck, "deck_lugs", "deck_lugs_2x_10mm", G.deck_lugs(), "frame")
    add_shape(doc, deck, "act_deck_lug", "actuator_deck_lug_2x_8mm", G.actuator_deck_lug(), "frame")
    add_shape(doc, deck, "deck_pins", "pins_M16_deck_side", G.deck_pins(), "zinc")
    add_shape(doc, deck, "doublers", "spindle_doublers_2x_6mm", G.doublers(), "frame")
    add_shape(doc, deck, "spacer_rings", "spacer_rings_2x_12mm_left", G.spacer_rings(), "zinc")
    add_shape(doc, deck, "spindle_housings", "deck_spindles_2x", G.spindle_housings(), "spindle")
    add_shape(doc, deck, "spindle_bolts", "spindle_bolts_6x_M8", G.spindle_bolts(), "zinc")
    add_shape(doc, deck, "standoffs", "standoffs_8x_D20_M10", G.standoffs(), "zinc")
    add_shape(doc, deck, "motor_plates", "motor_plates_2x_6mm", G.motor_plates(), "frame")
    add_shape(doc, deck, "motors", "BLDC_motors_2x_48V_750W", G.motors(), "motor")
    build_rotor(doc, deck, 1)
    build_rotor(doc, deck, -1)
    return deck


def build_into(doc, parent=None):
    """Puts the weed picker in a document, in robot coordinates (also used by animate_wpk.py)."""
    root = new_part(doc, parent, ROOT, "weed_picker_simple")
    build_mount(doc, root)
    build_controller(doc, root)
    build_linkage(doc, root)
    build_deck(doc, root)
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
    doc.Label = "Weed picker (simple)"
    doc.Comment = ("Generated by build_wpk.py from wpk_params.py. Robot coordinates: x = right, y = driving direction "
                   "(front = +y), z = up, ground = z 0. Twin-rotor weed topper in front of the robot, cut height %g mm."
                   % P.cut_h)
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
    raise RuntimeError("no weed picker document open")


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
# Moving the deck (animation and checks)
# ---------------------------------------------------------------------
def set_height(doc, cut, lift=0.0, spin=(0.0, 0.0)):
    """Deck at cut height 'cut' (actuator setting), floated up by 'lift' mm, rotors turned by spin (right, left) deg.
    Only the Placements of the sub-Parts change; the actuator is redrawn."""
    real = cut + lift
    dy, dz = P.deck_shift(real)
    doc.getObject("Deck").Placement = App.Placement(V(0, dy, dz), App.Rotation())
    da = P.theta(real) - P.theta()
    for name, z in (("Top_links", P.pivot_z[1]), ("Bottom_links", P.pivot_z[0])):
        doc.getObject(name).Placement = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), da), V(0, P.pivot_y, z))
    for tag, side, a in (("R", 1, spin[0]), ("L", -1, spin[1])):
        doc.getObject("Rotor_" + tag).Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), a),
                                                                V(side * P.rotor_x, P.YC0, 0))
    body, rod, links = G.actuator_shapes(cut, lift)
    doc.getObject("act_body").Shape = Part.makeCompound(body)
    doc.getObject("act_rod").Shape = Part.makeCompound(rod)
    doc.getObject("float_link").Shape = Part.makeCompound(links)


def set_steering(doc, deg):
    """Both front wheels turned by deg (+ = left), for the clearance check."""
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


def check_heights(doc=None, cuts=(P.cut_range[0], 150.0, 250.0, 300.0, P.cut_range[1]), lifts=((100.0, 80.0),)):
    """Interference over the height range and with the deck floated up (cut, lift). Puts the deck back."""
    doc = active_doc(doc)
    out = {}
    try:
        for c in cuts:
            set_height(doc, c, 0.0, (30.0, 60.0))
            doc.recompute()
            out["cut_%g" % c] = check_interference(doc)
        for c, lift in lifts:
            set_height(doc, c, lift)
            doc.recompute()
            out["cut_%g_float_%g" % (c, lift)] = check_interference(doc)
    finally:
        set_height(doc, P.cut_h)
        doc.recompute()
    return out


WHEEL_PARTS = ("tire", "rim", "side_l", "side_r", "top_plate", "axle_br_l", "axle_br_r", "wheel_hw", "hub_flange")
DECK_NEAR = ("skirt", "swath_boards", "deck_plate", "top_links", "bottom_links", "act_body", "float_link")


def clearance(doc=None, cuts=(P.cut_range[0], P.cut_h, P.cut_range[1]), steers=(-P.steer_max, 0.0, P.steer_max)):
    """Smallest distance (mm) of the deck, the links and the actuator to the front wheel units, for each cut height
    and steering angle."""
    doc = active_doc(doc)
    out = {}
    try:
        for st in steers:
            set_steering(doc, st)
            doc.recompute()
            wheels = [global_shape(doc.getObject("%s_%s" % (t, n))) for t in ("FL", "FR") for n in WHEEL_PARTS
                      if doc.getObject("%s_%s" % (t, n)) is not None]
            for c in cuts:
                set_height(doc, c)
                doc.recompute()
                best = (1e9, "")
                for n in DECK_NEAR:
                    a = global_shape(doc.getObject(n))
                    for w in wheels:
                        if a.BoundBox.isValid() and w.BoundBox.isValid():
                            d = a.distToShape(w)[0]
                            if d < best[0]:
                                best = (d, n)
                out["steer_%g_cut_%g" % (st, c)] = (round(best[0], 1), best[1])
    finally:
        set_steering(doc, 0.0)
        set_height(doc, P.cut_h)
        doc.recompute()
    return out


MASS_FIXED = {"motors": 9.0, "spindle_housings": 5.2, "controller_box": 3.0, "act_body": 2.6}     # bought (estimated)
DENSITY = (("R_coupling", 2.8e-6), ("L_coupling", 2.8e-6))       # jaw couplings: aluminium hubs
STEEL = 7.85e-6


def _density(name):
    for key, d in DENSITY:
        if name.startswith(key):
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


def _sum(objs):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co, _ = _mass_cg(o)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def _izz(objs, axis_xy):
    """Moment of inertia (kg m2) about a vertical axis through axis_xy (rotor)."""
    i = 0.0
    for o in objs:
        rho = _density(o.Name)
        for s in (global_shape(o).Solids or []):
            c = s.CenterOfMass
            i += s.MatrixOfInertia.A33 * rho + s.Volume * rho * ((c.x - axis_xy[0]) ** 2 + (c.y - axis_xy[1]) ** 2)
    return i * 1e-6


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (robot coordinates) at the default cut height: total and per group, rotor
    inertia."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    m, c = _sum(own_objects(doc))
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for g in ("Mount", "Controller", "Top_links", "Bottom_links", "Actuator", "Deck", "Rotor_R", "Rotor_L"):
        mg, cg = _sum(objs_of(g))
        out[g.lower() + "_kg"] = round(mg, 2)
        out[g.lower() + "_cg"] = (round(cg.x), round(cg.y), round(cg.z))
    out["rotor_I_kgm2"] = round(_izz(objs_of("Rotor_R"), (P.rotor_x, P.YC0)), 4)
    blade = doc.getObject("R_blades")
    out["blade_kg"] = round(blade.Shape.Volume * STEEL / 2.0, 3)
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
    tgt = V(*target) if target is not None else V(0, 700, 300)
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


def add_scenery(doc, plants=None, y=(-1500.0, 2600.0), x=(-1300.0, 1300.0), cut_y=None):
    """Ground and weeds (render only, prefixed render_). Plants with y < cut_y are drawn cut at the cut height."""
    import wpk_weeds as W
    plants = W.scene_plants() if plants is None else plants
    out = []
    g = doc.addObject("Part::Feature", "render_ground")
    g.Shape = G.box_span(x, y, (-40.0, 0.0))
    g.ViewObject.ShapeColor = COLOR["ground"]
    out.append(g)
    groups = {"stem": [], "leaves": [], "thistle": [], "ragwort": [], "dock": []}
    for p in plants:
        cz = P.cut_h if (cut_y is not None and p["y"] < cut_y) else None
        s = G.weed_shapes(p, cz)
        groups["stem"] += s["stem"]
        groups["leaves"] += s["leaves"]
        groups[p["kind"]] += s["crown"]
    for key, shapes in groups.items():
        if not shapes:
            continue
        o = doc.addObject("Part::Feature", "render_" + key)
        o.Shape = Part.makeCompound(shapes)
        o.ViewObject.ShapeColor = COLOR[key]
        o.ViewObject.DisplayMode = "Shaded"
        out.append(o)
    return out


def remove_scenery(doc):
    for o in list(doc.Objects):
        if o.Name.startswith("render_"):
            doc.removeObject(o.Name)


def add_ghost(doc, cut, name, transparency=70):
    """Transparent copy of the deck, links and actuator at another cut height (side view of the range)."""
    set_height(doc, cut)
    doc.recompute()
    shapes = [global_shape(o) for n in ("Deck", "Top_links", "Bottom_links", "Actuator")
              for o in doc.getObject(n).OutListRecursive if o.TypeId == "Part::Feature"]
    set_height(doc, P.cut_h)
    doc.recompute()
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
    add_scenery(doc)
    out.append(save_view("1_iso_on_robot.png", (1.0, -1.25, -0.8), target=(0, 500, 350), height=3000))
    remove_scenery(doc)
    add_scenery(doc, plants=[])
    out.append(save_view("2_front_on_robot.png", (0.0, -1.0, -0.15), target=(0, 800, 450), height=1700))
    add_ghost(doc, P.cut_range[0], "ghost_low", 75)
    add_ghost(doc, P.cut_range[1], "ghost_high", 80)
    out.append(save_view("3_side_height_range.png", (-1.0, 0.0, 0.0), target=(0, 650, 450), height=1500))
    remove_scenery(doc)
    out.append(save_view("4_top_on_robot.png", (0.0, 0.0, -1.0), target=(0, 450, 0), up=(0.0, 1.0, 0.0),
                         height=2600))
    set_robot_visible(False, doc)
    out.append(save_view("5_picker_iso.png", (1.0, -1.0, -0.7), target=(0, 850, 350), height=1500))
    out.append(save_view("6_from_below.png", (0.25, 0.35, 1.0), target=(0, 1000, 200), height=1300))
    set_visible(doc, ("skirt", "swath_boards", "deck_plate"), False)
    out.append(save_view("7_rotors_deck_hidden.png", (0.8, -1.0, 0.35), target=(0, 1050, 250), height=1150))
    set_visible(doc, ("skirt", "swath_boards", "deck_plate"), True)
    out.append(save_view("8_linkage_actuator.png", (-1.0, -0.6, -0.35), target=(0, 650, 450), height=800))
    App.closeDocument(doc.Name)
    build()
    return out
