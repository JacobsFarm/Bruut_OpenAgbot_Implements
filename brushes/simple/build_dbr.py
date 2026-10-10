"""Model van de schotelborstels op de Bruut OpenAgbot (standaard robot).

Gebruik in FreeCAD (map in sys.path, of via run_in_freecad.py):
    import build_dbr
    build_dbr.build("double_750")                 # of "double_650", "single_850"; slaat FCStd en STEP op
    build_dbr.build("double_750", mode="windrow") # borstels uit elkaar voor een wiers
    build_dbr.check_interference()                # overlap (moet leeg zijn)
    build_dbr.clearance()                         # kleinste afstand tot de achterbanden
    build_dbr.mass_properties()
    build_dbr.render_all()                        # alle afbeeldingen in previews/
"""
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dbr_params as P
import dbr_parts as G

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbots", "agbot design")
DOC_PREFIX = "Disc_Brushes_"

COLOR = {
    "frame": (0.93, 0.42, 0.08),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "gearbox": (0.66, 0.70, 0.74),
    "motor": (0.08, 0.08, 0.08),
    "bristle": (0.12, 0.12, 0.12),
    "brush_plate": (0.85, 0.75, 0.10),
    "plastic": (0.10, 0.10, 0.10),
    "box": (0.55, 0.57, 0.60),
    "ballast": (0.35, 0.36, 0.38),
}


def doc_name(config):
    return DOC_PREFIX + config


def save_paths(config):
    base = os.path.join(FOLDER, "Disc_Brushes_%s" % config)
    return base + ".FCStd", base + ".step"


# ---------------------------------------------------------------------
# Hulpfuncties boom (zelfde als build_fpa.py)
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
# Units
# ---------------------------------------------------------------------
def units(config, mode="spread", gap=None, h=None):
    """Lijst (tag, unit_frame) voor een uitvoering. Linker motor naar -x, rechter (en enkele) naar +x."""
    c = P.config(config)
    xs = P.centres_x(c, mode, gap)
    if len(xs) == 1:
        return [("centre", G.unit_frame(c, xs[0], 1, h))]
    return [("left", G.unit_frame(c, xs[0], -1, h)), ("right", G.unit_frame(c, xs[1], 1, h))]


def build_mount(doc, parent):
    grp = new_part(doc, parent, "Mount", "mount_toolbar_hangers")
    add_shape(doc, grp, "toolbar", "toolbar_80x80x5_L1300", G.toolbar(), "frame")
    add_shape(doc, grp, "toolbar_caps", "toolbar_end_caps_PE", G.toolbar_caps(), "plastic")
    for sx, tag in ((-1, "left"), (1, "right")):
        add_shape(doc, grp, "hanger_top_" + tag, "hanger_top_plate_10mm_" + tag, G.hanger_top(sx), "frame")
        add_shape(doc, grp, "hanger_webs_" + tag, "hanger_webs_8mm_" + tag, G.hanger_webs(sx), "frame")
        add_shape(doc, grp, "hanger_bolts_" + tag, "hanger_bolts_M10_" + tag, G.hanger_bolts(sx), "zinc")
    return grp


def build_controller(doc, parent):
    grp = new_part(doc, parent, "Controller", "controller_box_2x_motor_driver")
    add_shape(doc, grp, "box_base", "controller_base_plate_3mm", G.box_base(), "zinc")
    add_shape(doc, grp, "controller_box", "controller_box_IP66_2x48V30A", G.controller_box(), "box")
    add_shape(doc, grp, "box_bolts", "controller_bolts_M8", G.box_bolts(), "zinc")
    return grp


def build_unit(doc, parent, tag, u):
    d = int(u["c"]["d"])
    grp = new_part(doc, parent, "Unit_" + tag, "brush_unit_%s" % tag)
    add_shape(doc, grp, "clamp_plate_" + tag, "clamp_plate_10mm_4_slots_" + tag, G.clamp_plate(u), "frame")
    add_shape(doc, grp, "jack_tab_" + tag, "jack_tab_10mm_" + tag, G.jack_tab(u), "frame")
    add_shape(doc, grp, "jack_hw_" + tag, "jack_bolt_M16_welded_nut_" + tag, G.jack_hw(u), "zinc")
    add_shape(doc, grp, "u_bolts_" + tag, "square_U_bolts_M16_80_" + tag, G.u_bolts(u), "zinc")
    add_shape(doc, grp, "head_plate_" + tag, "head_plate_10mm_tilt_%g_%s" % (P.tilt_deg, tag), G.head_plate(u), "frame")
    add_shape(doc, grp, "gussets_" + tag, "head_gussets_8mm_" + tag, G.gussets(u), "frame")
    add_shape(doc, grp, "gearmotor_" + tag, "worm_gearmotor_NMRV063_i30_48V_550W_" + tag, G.gearmotor(u), "gearbox")
    add_shape(doc, grp, "gm_bolts_" + tag, "gearmotor_bolts_M10_" + tag, G.gearmotor_bolts(u), "zinc")
    rotor = new_part(doc, grp, "Brush_" + tag, "brush_rotor_%s_turns" % tag)
    add_shape(doc, rotor, "shaft_" + tag, "plug_in_shaft_D25_" + tag, G.shaft(u), "steel")
    add_shape(doc, rotor, "hub_" + tag, "brush_hub_D160_" + tag, G.hub(u), "steel")
    add_shape(doc, rotor, "hub_bolts_" + tag, "hub_bolts_M10_end_bolt_" + tag, G.hub_bolts(u), "zinc")
    add_shape(doc, rotor, "brush_plate_" + tag, "brush_plate_D%d_%s" % (u["c"]["plate_d"], tag), G.brush_plate(u),
              "brush_plate")
    add_shape(doc, rotor, "bristles_" + tag, "disc_brush_D%d_PP_steel_%s" % (d, tag), G.bristles(u), "bristle")
    return grp


def build_ballast(doc, parent):
    grp = new_part(doc, parent, "Counterweight", "counterweight_front_2x20kg_optional")
    add_shape(doc, grp, "ballast", "counterweight_blocks", G.ballast(), "ballast")
    add_shape(doc, grp, "ballast_bolts", "counterweight_bolts_M10", G.ballast_bolts(), "zinc")
    return grp


def build_into(doc, parent=None, config=P.DEFAULT_CONFIG, mode="spread", gap=None, h=None, ballast=True):
    """Zet de borstels in een document, in robotcoordinaten (ook gebruikt door animate_dbr.py)."""
    root = new_part(doc, parent, "Disc_brushes", "disc_brushes_%s" % config)
    build_mount(doc, root)
    build_controller(doc, root)
    for tag, u in units(config, mode, gap, h):
        build_unit(doc, root, tag, u)
    if ballast:
        build_ballast(doc, root)
    return root


def build_robot(doc):
    """Echt robotmodel uit 'agbot design' (alleen lezen)."""
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


def build(config=P.DEFAULT_CONFIG, mode="spread", gap=None, h=None, save=True, show_robot=False, step=True):
    name = doc_name(config)
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    c = P.config(config)
    doc.Label = "Disc brushes %s" % config
    doc.Comment = ("Gegenereerd met build_dbr.py uit dbr_params.py (%s, %s). Robotcoordinaten: x = rechts, y = rijrichting "
                   "robot (voor = +y), z = omhoog, grond = z 0. Borstels achter de robot, de robot rijdt naar -y." % (
                       config, mode))
    robot = None
    if show_robot is not None:
        try:
            robot = build_robot(doc)
        except Exception as exc:
            print("robotmodel niet geladen:", exc)
    build_into(doc, robot, config, mode, gap, h)
    if robot is not None and not show_robot:
        set_robot_visible(False, doc)
    doc.recompute()
    fc, st = save_paths(config)
    if save:
        doc.saveAs(fc)
    if step:
        export_step(doc, st)
    return doc


def active_doc(doc=None):
    if doc is not None:
        return doc
    d = App.ActiveDocument
    if d is not None and d.Name.startswith(DOC_PREFIX):
        return d
    for n in App.listDocuments():
        if n.startswith(DOC_PREFIX):
            return App.getDocument(n)
    raise RuntimeError("geen borsteldocument open")


def brush_objects(doc):
    return [o for o in doc.getObject("Disc_brushes").OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in brush_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


def set_robot_visible(visible, doc=None):
    doc = active_doc(doc)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = visible


def export_step(doc, path):
    import Import
    objs = []
    for o in brush_objects(doc):
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
# Controle
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def check_interference(doc=None, tol=1.0):
    """Volume-overlap (mm3): borstels onderling en tegen de (zichtbare en verborgen) robot."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in brush_objects(doc)]
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


def clearance(doc=None, robot_names=("RL_tire", "RR_tire", "RL_side_l", "RL_side_r", "RR_side_l", "RR_side_r",
                                     "RL_spacer", "RR_spacer", "RL_top_plate", "RR_top_plate")):
    """Kleinste afstand (mm) van de borstelunits en de hangers tot de achterwielen en wielbeugels."""
    doc = active_doc(doc)
    targets = [global_shape(doc.getObject(r)) for r in robot_names if doc.getObject(r) is not None]
    out = {}
    for o in brush_objects(doc):
        if o.Name.startswith(("bristles", "brush_plate", "gearmotor", "clamp", "head_plate", "hanger", "toolbar",
                              "u_bolts")):
            a = global_shape(o)
            out[o.Name] = round(min(a.distToShape(t)[0] for t in targets), 1)
    return out


def floor_contact(doc=None):
    """Laagste punt van elke haarkrans (moet 0 zijn) en de y van dat punt."""
    doc = active_doc(doc)
    out = {}
    for o in brush_objects(doc):
        if o.Name.startswith("bristles"):
            s = global_shape(o)
            bb = s.BoundBox
            low = s.common(Part.makeBox(4000, 4000, 2, V(-2000, -3000, 0))).BoundBox   # contactstrook (onderste 2 mm)
            out[o.Name] = {"z_min": round(bb.ZMin, 2), "x": round(bb.Center.x),
                           "contact_y": (round(low.YMin), round(low.YMax)), "contact_x": (round(low.XMin), round(low.XMax))}
    return out


MASS_FIXED = {"gearmotor": 13.0, "controller_box": 3.5}
DENSITY = (("bristles", 0.30e-6), ("toolbar_caps", 0.95e-6))
STEEL = 7.85e-6


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
    """Massa (kg) en zwaartepunt (robotcoordinaten): totaal zonder contragewicht, per unit, mount, contragewicht."""
    doc = active_doc(doc)

    def objs_of(name):
        g = doc.getObject(name)
        return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []
    ballast = {o.Name for o in objs_of("Counterweight")}
    main = [o for o in brush_objects(doc) if o.Name not in ballast]
    m, c = _sum(main)
    out = {"total_kg": round(m, 1), "total_cg": (round(c.x), round(c.y), round(c.z))}
    for g in ("Mount", "Controller"):
        mg, cgg = _sum(objs_of(g))
        out[g.lower() + "_kg"] = round(mg, 1)
        out[g.lower() + "_cg"] = (round(cgg.x), round(cgg.y), round(cgg.z))
    for tag in ("left", "right", "centre"):
        if doc.getObject("Unit_" + tag):
            mu, cu = _sum(objs_of("Unit_" + tag))
            mb, _ = _sum(objs_of("Brush_" + tag))
            out["unit_%s_kg" % tag] = round(mu, 1)
            out["unit_%s_cg" % tag] = (round(cu.x), round(cu.y), round(cu.z))
            out["brush_%s_kg" % tag] = round(mb, 1)
    mb, cb = _sum([o for o in brush_objects(doc) if o.Name in ballast])
    out["ballast_kg"] = round(mb, 1)
    out["ballast_cg"] = (round(cb.x), round(cb.y), round(cb.z))
    return out


def size(doc=None):
    doc = active_doc(doc)
    bb = None
    for o in brush_objects(doc):
        if o.Name.startswith("ballast"):
            continue
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return (round(bb.XLength), round(bb.YLength), round(bb.ZLength)), (round(bb.XMin), round(bb.YMin), round(bb.ZMin))


# ---------------------------------------------------------------------
# Afbeeldingen
# ---------------------------------------------------------------------
def set_camera(direction, target=None, height=None, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    cam = view.getCameraNode()
    tgt = V(*target) if target is not None else V(0, -900, 300)
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


GROUND = "render_floor"


def add_floor(doc, y=(-1800.0, 1000.0), x=(-1100.0, 1100.0)):
    obj = doc.addObject("Part::Feature", GROUND)
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = (0.72, 0.72, 0.70)
    obj.ViewObject.Transparency = 30
    return obj


def remove_floor(doc):
    if doc.getObject(GROUND):
        doc.removeObject(GROUND)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None:
            o.ViewObject.Visibility = visible


def render_config(config, prefix):
    """Standaardbeelden van een uitvoering, los en op de robot."""
    doc = build(config, save=False, show_robot=True, step=False)
    out = []
    set_visible(doc, ("ballast", "ballast_bolts"), False)
    out.append(save_view(prefix + "_iso_on_robot.png", (1.0, 1.1, -0.7), target=(0, -350, 350)))
    add_floor(doc)
    try:
        out.append(save_view(prefix + "_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, -400, 400), height=1700))
    finally:
        remove_floor(doc)
    out.append(save_view(prefix + "_top_on_robot.png", (0.0, 0.0, -1.0), target=(0, -400, 0), up=(0.0, 1.0, 0.0)))
    out.append(save_view(prefix + "_rear_on_robot.png", (0.0, 1.0, -0.15), target=(0, -400, 350), height=1300))
    set_robot_visible(False, doc)
    set_visible(doc, ("box_base", "controller_box", "box_bolts"), False)
    out.append(save_view(prefix + "_iso_rear_right.png", (-1.0, 1.0, -0.6), target=(0, -950, 250)))
    return doc, out


PREFIX = {"double_750": "1_double_750", "double_650": "2_double_650", "single_850": "3_single_850"}


def render_one(config):
    """Afbeeldingen van één uitvoering in previews/, daarna opslaan (FCStd + STEP, robot verborgen)."""
    doc, out = render_config(config, PREFIX[config])
    if config == "double_750":
        u = dict(units(config))["right"]
        xc, yc = u["xc"], u["yc"]
        out.append(save_view("4_unit_detail.png", (-1.0, 0.75, -0.55), target=(xc, yc + 80, 300), height=750))
        out.append(save_view("5_unit_side.png", (1.0, 0.0, 0.0), target=(xc, -950, 300), height=750))
        out.append(save_view("6_clamp_detail.png", (0.7, 1.0, -0.6), target=(xc, -830, 400), height=520))
    App.closeDocument(doc.Name)
    if config == "double_750":
        doc = build(config, mode="windrow", save=False, show_robot=True, step=False)
        set_visible(doc, ("ballast", "ballast_bolts"), False)
        out.append(save_view("7_double_750_windrow_top.png", (0.0, 0.0, -1.0), target=(0, -400, 0), up=(0.0, 1.0, 0.0)))
        App.closeDocument(doc.Name)
    build(config)
    return out


def render_all():
    """Alle afbeeldingen in previews/ en opslaan (FCStd + STEP) van alle uitvoeringen."""
    out = []
    for config in PREFIX:
        out += render_one(config)
    return out
