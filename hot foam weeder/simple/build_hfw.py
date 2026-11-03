"""Model of the hot foam weeder on the Bruut OpenAgbot (standard robot).

The hood shell, castors, mount plate, headstock, parallelogram, liquid gas valves and the propane cylinders are built
from "weeds burner/propane_hood" (build_flw, flw_parts); this file adds the water tank under the belly, the rear rack
with the boiler, pump and foam can, the foam bar in the hood and the hoses.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_hfw
    build_hfw.build()                      # saves FCStd and STEP (hood on the ground)
    build_hfw.set_pose(float_h=60)         # the hood floats up / down on the parallelogram (mm)
    build_hfw.check_interference()         # overlap in the current pose (must be empty)
    build_hfw.check_holes()                # bolts in their holes (must be empty)
    build_hfw.check_fit()                  # overlap over the float range x steering (must be empty)
    build_hfw.clearance()                  # smallest distance of the belly tank and the rack to the tyres
    build_hfw.mass_properties()
    build_hfw.render_all()                 # all images in previews/
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import hfw_params as P
import hfw_parts as G
import flw_parts as FG
import build_flw as BF

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Hot_Foam_Weeder"
SAVE_BASE = os.path.join(FOLDER, "Hot_Foam_Weeder")
ROOT = "Hot_foam_weeder"

COLOR = dict(BF.COLOR)
COLOR.update({
    "tank": (0.93, 0.93, 0.90),
    "rail": (0.93, 0.42, 0.08),
    "boiler": (0.80, 0.12, 0.10),
    "burner": (0.20, 0.20, 0.22),
    "pump": (0.15, 0.15, 0.17),
    "can": (0.95, 0.80, 0.15),
    "hot": (0.75, 0.15, 0.10),
    "water": (0.15, 0.25, 0.55),
    "nozzle": (0.15, 0.55, 0.85),
    "rubber": (0.10, 0.10, 0.10),
})


def new_part(doc, parent, name, label, placement=None):
    return BF.new_part(doc, parent, name, label, placement)


def add_shape(doc, parent, name, label, shape, color, visible=True):
    if isinstance(shape, (list, tuple)):
        shape = Part.makeCompound(list(shape))
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    parent.addObject(obj)
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = COLOR[color]
        obj.ViewObject.Visibility = visible
    return obj


pose_placements = BF.pose_placements


def set_pose(float_h=0.0, doc=None):
    doc = active_doc(doc)
    for name, pl in pose_placements(float_h).items():
        doc.getObject(name).Placement = pl
    doc.recompute()


# ---------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------
def build_hood(doc, parent, pl):
    hood = new_part(doc, parent, "Hood", "hood_1500x800_foam_bar_12_nozzles", pl["Hood"])
    sh = new_part(doc, hood, "Hood_shell", "hood_shell_from_flame_weeder")
    add_shape(doc, sh, "hood_skin", "hood_skin_steel_1.5mm_hose_hole", G.hood_skin(), "skin")
    add_shape(doc, sh, "blanket", "ceramic_fibre_blanket_25mm", G.blanket(), "blanket")
    add_shape(doc, sh, "top_cover", "top_cover_alu_0.8mm_on_spacers", G.top_cover(), "alu")
    add_shape(doc, sh, "ribs", "edge_angles_30x30x3", FG.ribs(), "frame")
    add_shape(doc, sh, "front_shield", "front_shield_alu_4mm", FG.front_shield(), "alu")
    add_shape(doc, sh, "hood_bracket", "hood_bracket_lugs_8mm", FG.hood_bracket(), "frame")
    add_shape(doc, sh, "hood_pins", "parallelogram_rear_pins_D20", FG.hood_pins(), "steel")
    fb = new_part(doc, hood, "Foam_bar", "foam_bar_and_hot_hose")
    add_shape(doc, fb, "foam_bar", "foam_bar_stainless_3_4in", G.foam_bar(), "stainless")
    add_shape(doc, fb, "nozzles", "foam_nozzles_12x_pitch_125", G.nozzles(), "nozzle")
    add_shape(doc, fb, "bar_clamps", "bar_straps_30x5", G.bar_clamps(), "stainless")
    add_shape(doc, fb, "hot_hose", "hot_water_hose_insulated", G.hot_hose(), "hot")
    cs = new_part(doc, hood, "Castors", "castors_steel_D200_swivel")
    add_shape(doc, cs, "castor_arms", "castor_arms_40x40_posts", FG.castor_arms(), "frame")
    add_shape(doc, cs, "castor_frames", "castor_plates_swivels_forks", FG.castor_frames(), "zinc")
    add_shape(doc, cs, "castor_wheels", "castor_wheels_steel_200x50", FG.castor_wheels(), "wheel")
    return hood


def build_mount(doc, parent, pl):
    grp = new_part(doc, parent, "Mount", "mount_headstock_parallelogram_gas_valves")
    add_shape(doc, grp, "sub_plate", "sub_plate_8mm_under_rear_beams", FG.sub_plate(), "frame")
    add_shape(doc, grp, "sub_bolts", "sub_plate_bolts_4xM10", FG.sub_bolts(), "zinc")
    add_shape(doc, grp, "headstock", "headstock_plates_8mm", FG.headstock(), "frame")
    add_shape(doc, grp, "stock_pins", "parallelogram_front_pins_D20", FG.stock_pins(), "steel")
    up = new_part(doc, grp, "Upper_arms", "upper_arms", pl["Upper_arms"])
    add_shape(doc, up, "upper_arm_tubes", "upper_arms_40x40x3", FG.upper_arms(), "frame")
    lo = new_part(doc, grp, "Lower_arms", "lower_arms", pl["Lower_arms"])
    add_shape(doc, lo, "lower_arm_tubes", "lower_arms_40x40x3_cross_tube", FG.lower_arms(), "frame")
    add_shape(doc, grp, "robot_gas_train", "liquid_filter_two_main_solenoid_valves", FG.robot_gas_train(), "valve")
    add_shape(doc, grp, "cylinder_hoses", "liquid_hoses_cylinders_to_valves", G.cylinder_hoses(), "hose")
    add_shape(doc, grp, "gas_hose", "liquid_hose_valves_to_burner", G.gas_hose(), "hose")
    return grp


def build_water(doc, parent):
    grp = new_part(doc, parent, "Water", "water_tank_100l_under_the_belly")
    add_shape(doc, grp, "rails", "belly_rails_40x40x3_x225", G.rails(), "rail")
    add_shape(doc, grp, "rail_bolts", "rail_bolts_8xM10", G.rail_bolts(), "zinc")
    add_shape(doc, grp, "hangers", "tank_hangers_40x40x3_feet", G.hangers(), "rail")
    add_shape(doc, grp, "hanger_bolts", "hanger_bolts_M8_rivet_nuts", G.hanger_bolts(), "zinc")
    add_shape(doc, grp, "tank_frame", "tank_frame_40x40x3", G.tank_frame(), "rail")
    add_shape(doc, grp, "tank_pads", "tank_rubber_strips", G.tank_pads(), "rubber")
    add_shape(doc, grp, "tank_shell", "water_tank_PE_100l", G.tank_shell(), "tank")
    add_shape(doc, grp, "tank_fittings", "camlock_fill_suction_fitting_level_sensor", G.tank_fittings(), "saddle")
    add_shape(doc, grp, "suction_hose", "suction_hose_tank_to_pump", G.suction_hose(), "water")
    return grp


def build_rack(doc, parent):
    grp = new_part(doc, parent, "Rack", "rear_rack_boiler_pump_foam")
    add_shape(doc, grp, "rack", "rack_tubes_40x40x3", G.rack(), "frame")
    add_shape(doc, grp, "rack_bolts", "rack_bolts_4xM10", G.rack_bolts(), "zinc")
    add_shape(doc, grp, "deck_plate", "deck_plate_4mm", G.deck_plate(), "frame")
    add_shape(doc, grp, "boiler_feet", "boiler_feet", G.boiler_feet(), "frame")
    add_shape(doc, grp, "boiler", "boiler_coil_heater_40kW_flue", G.boiler(), "boiler")
    add_shape(doc, grp, "burner", "burner_fan_gas_valve", G.burner(), "burner")
    add_shape(doc, grp, "water_ports", "boiler_water_ports", G.water_ports(), "brass")
    add_shape(doc, grp, "pump", "water_pump_diaphragm_24V_11lpm", G.pump(), "pump")
    add_shape(doc, grp, "foam_can", "foam_concentrate_can_10l", G.foam_can(), "can")
    add_shape(doc, grp, "can_bracket", "can_bracket_strap", G.can_bracket(), "frame")
    add_shape(doc, grp, "doser", "foam_dosing_pump", G.doser(), "pump")
    add_shape(doc, grp, "pressure_hose", "pressure_hose_pump_to_boiler", G.pressure_hose(), "water")
    add_shape(doc, grp, "foam_hose", "foam_hose_doser_to_pump", G.foam_hose(), "can")
    return grp


def build_into(doc, parent=None, float_h=0.0):
    """Put the weeder in a document, in robot coordinates (also used by animate_hfw.py)."""
    pl = pose_placements(float_h)
    root = new_part(doc, parent, ROOT, "hot_foam_weeder_simple")
    BF.build_gas(doc, root)
    build_mount(doc, root, pl)
    build_water(doc, root)
    build_rack(doc, root)
    build_hood(doc, root, pl)
    return root


build_robot = BF.build_robot
global_shape = BF.global_shape


def build(save=True, show_robot=False, step=True, float_h=0.0):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Hot foam weeder simple"
    doc.Comment = ("Generated by build_hfw.py from hfw_params.py (hood, mount and propane from weeds burner/propane_hood). "
                   "Robot coordinates: x = right, y = driving direction (front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot, float_h)
    if robot is not None:
        set_robot_visible(bool(show_robot), doc)
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
    return [o for o in g.OutListRecursive if o.TypeId == "Part::Feature"] if g else []


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in objects_of(doc, ROOT)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine
            and not o.Name.startswith("anim_")]


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


# pins, bolts and hose ends pass through holes / into ports of the parts they join: those pairs are by design
JOINTS = {("pivot_pins", "carrier"), ("stock_pins", "headstock"), ("stock_pins", "upper_arm_tubes"),
          ("stock_pins", "lower_arm_tubes"), ("hood_pins", "hood_bracket"), ("hood_pins", "upper_arm_tubes"),
          ("hood_pins", "lower_arm_tubes"), ("sub_bolts", "sub_plate"), ("cradle_bolts", "cradle"),
          ("rail_bolts", "rails"), ("hanger_bolts", "rails"), ("hanger_bolts", "hangers"), ("rack_bolts", "rack"),
          ("hangers", "tank_frame"), ("tank_pads", "tank_frame"), ("tank_pads", "tank_shell"),
          ("tank_fittings", "tank_shell"), ("suction_hose", "tank_fittings"), ("suction_hose", "pump"),
          ("pressure_hose", "pump"), ("pressure_hose", "water_ports"), ("water_ports", "boiler"),
          ("hot_hose", "water_ports"), ("hot_hose", "foam_bar"), ("hot_hose", "hood_skin"), ("hot_hose", "blanket"),
          ("hot_hose", "top_cover"), ("nozzles", "foam_bar"), ("bar_clamps", "foam_bar"), ("bar_clamps", "blanket"),
          ("foam_hose", "doser"), ("foam_hose", "pump"), ("foam_hose", "foam_can"), ("doser", "can_bracket"), ("foam_can", "can_bracket"),
          ("gas_hose", "burner"), ("gas_hose", "robot_gas_train"), ("cylinder_hoses", "robot_gas_train"),
          ("cylinder_hoses", "collars"), ("cylinder_hoses", "sub_plate"), ("burner", "boiler"),
          ("boiler_feet", "boiler"), ("castor_arms", "ribs"), ("castor_arms", "castor_frames"),
          ("castor_frames", "castor_wheels"), ("saddles", "cradle"), ("saddles", "cylinders"), ("straps", "saddles"),
          ("straps", "cylinders"), ("collars", "cylinders"), ("ribs", "hood_skin"), ("blanket", "hood_skin"),
          ("top_cover", "hood_skin"), ("front_shield", "hood_skin"), ("hood_bracket", "top_cover"),
          ("hood_bracket", "hood_skin"), ("hood_bracket", "blanket"), ("robot_gas_train", "sub_plate")}
BEAM_BOLTS = ("rail_bolts", "rack_bolts", "sub_bolts", "cradle_bolts")


def _joint(a, b):
    if (a, b) in JOINTS or (b, a) in JOINTS:
        return True
    for x, y in ((a, b), (b, a)):
        if x in BEAM_BOLTS and y.startswith(("lower_beam", "upper_beam")):
            return True
    return False


def _overlaps(pairs, tol):
    return BF._overlaps(pairs, tol)


def check_interference(doc=None, tol=1.0):
    """Volume overlap (mm3) in the current pose: weeder parts among themselves and against the robot. Pairs joined by
    design (JOINTS) are skipped; check_holes() checks the bolt holes."""
    doc = active_doc(doc)
    mine = [(o, global_shape(o)) for o in objects_of(doc, ROOT)]
    robot = [(o, global_shape(o)) for o in robot_objects(doc)]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))
             if not _joint(mine[i][0].Name, mine[j][0].Name)]
    pairs += [(a, b) for a in mine for b in robot if not _joint(a[0].Name, b[0].Name)]
    return _overlaps(pairs, tol)


def check_holes(doc=None, tol=1.0):
    """The bolts must sit in holes: overlap of the bolts with the parts and beams they pass (~0)."""
    doc = active_doc(doc)
    objs = {o.Name: global_shape(o) for o in objects_of(doc, ROOT)}
    for o in robot_objects(doc):
        if o.Name.startswith(("lower_beam", "upper_beam")):
            objs[o.Name] = global_shape(o)
    pairs = [(a, b) for (a, b) in JOINTS if a.endswith(("_bolts", "_pins"))]
    pairs += [(b, n) for b in BEAM_BOLTS for n in objs if n.startswith(("lower_beam", "upper_beam"))]
    out = {}
    for a, b in sorted(set(pairs)):
        if a in objs and b in objs and objs[a].BoundBox.intersect(objs[b].BoundBox):
            v = objs[a].common(objs[b]).Volume
            if v > tol:
                out[str((a, b))] = round(v, 1)
    return out


def set_steering(deg, doc=None):
    doc = active_doc(doc)
    for name in ("FL_steered", "FR_steered"):
        o = doc.getObject(name)
        if o is not None:
            o.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), deg))
    doc.recompute()


def check_fit(doc=None, tol=1.0, floats=(P.W.float_range[0], 0.0, P.W.float_range[1]),
              steer=(-P.robot_steer_max, P.robot_steer_max)):
    """Interference of the moving groups (hood, arms) over the float range, and of everything fixed at full steering
    lock, against the rest. Must be empty."""
    doc = active_doc(doc)
    moving_names = {o.Name for n in ("Hood", "Upper_arms", "Lower_arms") for o in objects_of(doc, n)}
    mine = objects_of(doc, ROOT)
    moving = [o for o in mine if o.Name in moving_names]
    fixed = [(o, global_shape(o)) for o in mine if o.Name not in moving_names]
    fixed += [(o, global_shape(o)) for o in robot_objects(doc)]
    out = {}
    for f in floats:
        set_pose(f, doc)
        mv = [(o, global_shape(o)) for o in moving]
        hits = _overlaps([(a, b) for a in mv for b in fixed if not _joint(a[0].Name, b[0].Name)], tol)
        if hits:
            out["float_%g" % f] = hits
    set_pose(0.0, doc)
    front = [o for o in robot_objects(doc) if o.Name.startswith(("FL_", "FR_"))]
    mine_s = [(o, global_shape(o)) for o in mine if o.Name not in moving_names]
    for st in steer:
        set_steering(st, doc)
        fr = [(o, global_shape(o)) for o in front]
        hits = _overlaps([(a, b) for a in mine_s for b in fr], tol)
        if hits:
            out["steer_%+d" % st] = hits
    set_steering(0.0, doc)
    return out


def tyre_envelope(x, y, steer):
    c = Part.makeCylinder(P.robot_tire_d / 2.0, P.robot_tire_w, V(x - P.robot_tire_w / 2.0, y, P.robot_axle_z), V(1, 0, 0))
    c.rotate(V(x, y, 0), V(0, 0, 1), steer)
    return c


def clearance(doc=None, steer=(-P.robot_steer_max, 0.0, P.robot_steer_max)):
    """Smallest distance (mm) of the belly tank group and the rack to the tyres (front steered, rear straight)."""
    doc = active_doc(doc)
    parts = [doc.getObject(n) for n in ("tank_shell", "tank_frame", "hangers", "rails", "suction_hose", "rack",
                                        "deck_plate")]
    best = (1e9, None, None)
    for st in steer:
        tg = [tyre_envelope(sx * P.robot_wheel_x, P.robot_axle_y, st) for sx in (-1, 1)]
        tg += [tyre_envelope(sx * P.robot_wheel_x, -P.robot_axle_y, 0.0) for sx in (-1, 1)]
        for o in parts:
            s = global_shape(o)
            for i, t in enumerate(tg):
                d = s.distToShape(t)[0]
                if d < best[0]:
                    best = (d, o.Name, (st, "front" if i < 2 else "rear"))
    return round(best[0], 1), best[1], best[2]


MASS_FIXED = {"boiler": P.boiler_kg - 4.0, "burner": 4.0, "pump": P.pump_kg, "doser": 0.8, "foam_can": 1.0,
              "tank_fittings": 0.8, "robot_gas_train": 2.5, "nozzles": 12 * 0.15, "water_ports": 0.3}
DENSITY = (("tank_shell", P.pe), ("tank_pads", 1.2e-6), ("blanket", 0.13e-6), ("top_cover", 2.7e-6),
           ("front_shield", 2.7e-6), ("castor_wheels", P.steel), ("cylinders", P.steel), ("saddles", 1.2e-6),
           ("suction_hose", 1.0e-6), ("pressure_hose", 1.0e-6), ("hot_hose", 0.9e-6), ("foam_hose", 1.0e-6),
           ("gas_hose", 1.2e-6), ("cylinder_hoses", 1.2e-6), ("collars", P.steel))


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
    if obj.Name == "cylinders":
        return 2 * P.W.cyl_kg_tare, cg
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
    """Mass (kg) and centre of gravity, tank and cylinders empty (cylinders = tare)."""
    doc = active_doc(doc)
    out = {}
    for name in (ROOT, "Gas", "Mount", "Water", "Rack", "Hood"):
        m, c = sum_mass(objects_of(doc, name))
        out[name.lower() + "_kg"] = round(m, 1)
        out[name.lower() + "_cg"] = (round(c.x), round(c.y), round(c.z))
    hood = {o.Name for o in objects_of(doc, "Hood")}
    m, c = sum_mass([o for o in objects_of(doc, ROOT) if o.Name not in hood])
    out["robot_side_kg"] = round(m, 1)
    out["robot_side_cg"] = (round(c.x), round(c.y), round(c.z))
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
set_camera = BF.set_camera


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


SCENE = ("render_path", "render_weeds", "render_foam")


def add_scene(doc, y=(-2600.0, 1400.0)):
    import random
    o = doc.addObject("Part::Feature", SCENE[0])
    o.Shape = G.path_strip(*y)
    o.ViewObject.ShapeColor = (0.62, 0.60, 0.56)
    rnd = random.Random(5)
    w = doc.addObject("Part::Feature", SCENE[1])
    w.Shape = Part.makeCompound([G.weed(rnd.uniform(-700, 700), rnd.uniform(-900, y[1] - 100), 1.6) for _ in range(28)])
    w.ViewObject.ShapeColor = (0.25, 0.55, 0.15)
    f = doc.addObject("Part::Feature", SCENE[2])
    f.Shape = G.foam(-P.W.work_w / 2.0, P.W.work_w / 2.0, y[0] + 100.0, P.bar_y, 0.0, 12.0)
    f.ViewObject.ShapeColor = (0.97, 0.97, 0.95)
    return o


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def render_all():
    """Standard images in previews/, then build and save (FCStd + STEP, robot hidden)."""
    out = []
    doc = build(save=False, show_robot=True, step=False)
    add_scene(doc)
    out.append(save_view("1_work_iso_on_robot.png", (-1.0, 1.1, -0.65), target=(0, -600, 450), height=3000))
    out.append(save_view("2_side_on_robot.png", (1.0, 0.0, 0.0), target=(0, -500, 600), height=2400))
    for n in ("hood_skin", "blanket", "top_cover", "front_shield"):
        doc.getObject(n).ViewObject.Transparency = 75
    out.append(save_view("3_foam_bar_through_the_hood.png", (-1.0, 0.9, -0.7), target=(0, -1250, 150), height=1900))
    for n in ("hood_skin", "blanket", "top_cover", "front_shield"):
        doc.getObject(n).ViewObject.Transparency = 0
    remove(doc, SCENE)
    out.append(save_view("4_rear_rack_boiler.png", (-0.8, 1.0, -0.6), target=(0, -850, 900), height=1300))
    out.append(save_view("5_belly_tank_from_below.png", (0.4, 0.5, 1.0), target=(0, 0, 400), height=1700))
    out.append(save_view("6_from_below_foam_bar.png", (0.3, -0.4, 1.0), target=(0, -1300, 150), height=1800))
    set_robot_visible(False, doc)
    for n in objects_of(doc, "Gas") + objects_of(doc, "Hood"):
        n.ViewObject.Visibility = False
    out.append(save_view("7_water_and_gas_lines.png", (-1.0, 0.6, -0.5), target=(0, -500, 600), height=1700))
    App.closeDocument(doc.Name)
    build()
    return out
