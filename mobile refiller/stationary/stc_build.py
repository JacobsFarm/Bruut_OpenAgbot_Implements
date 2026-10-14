"""FreeCAD tools shared by the three stationary refill stations: model tree helpers, the IBC, the control box, the mast
with the arm, the working robot in the refill scene, interference checks, mass, images and STEP export.

The carrier folders (ibc_trailer, three_point, flat_wagon) build their own frame with these helpers; see their
build_*.py.
"""
import math
import os
import re
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import stc_params as P
import stc_parts as G

COLOR = {
    "frame": (0.10, 0.45, 0.25),         # station green
    "wagon": (0.80, 0.12, 0.10),
    "deck": (0.62, 0.64, 0.66),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.75, 0.75, 0.78),
    "galv": (0.70, 0.72, 0.74),
    "motor": (0.08, 0.08, 0.08),
    "pump": (0.10, 0.35, 0.65),
    "box": (0.88, 0.88, 0.84),
    "door": (0.80, 0.80, 0.76),
    "battery": (0.15, 0.30, 0.55),
    "pcb": (0.15, 0.45, 0.20),
    "din": (0.70, 0.70, 0.70),
    "bottle": (0.95, 0.95, 0.92),
    "pallet": (0.15, 0.15, 0.16),
    "liquid": (0.15, 0.50, 0.80),
    "hose": (0.12, 0.12, 0.13),
    "rubber": (0.10, 0.10, 0.10),
    "tyre": (0.09, 0.09, 0.09),
    "rim": (0.78, 0.78, 0.80),
    "valve": (0.85, 0.20, 0.15),
    "pp": (0.20, 0.22, 0.25),
    "white": (0.96, 0.96, 0.95),
    "black": (0.03, 0.03, 0.03),
    "yellow": (0.95, 0.75, 0.10),
    "red": (0.85, 0.08, 0.06),
    "green": (0.10, 0.80, 0.25),
    "amber": (1.00, 0.55, 0.05),
    "strap": (0.95, 0.55, 0.05),
    "camlock": (0.80, 0.62, 0.25),
    "funnel": (0.95, 0.75, 0.10),
    "plate": (0.98, 0.80, 0.05),
}
TRANSPARENT = {"bottle": 55, "liquid": 0}

ROBOT_GNSS = ("gnss_dome", "gnss_mount")


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
        shape = Part.makeCompound([s for s in shape if s is not None])
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape if shape is not None else Part.Shape()
    parent.addObject(obj)
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
        if color in TRANSPARENT:
            view.Transparency = TRANSPARENT[color]
    return obj


def base_name(name):
    return re.sub(r"\d{3}$", "", name)


def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def new_doc(name, label, comment):
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    doc.Label = label
    doc.Comment = comment
    return doc


# ---------------------------------------------------------------------
# IBC, control box, mast and arm
# ---------------------------------------------------------------------
def build_ibc(doc, parent, tag, pl, litres, strap_axis="y", strap_z=12.0, ratchet_z=410.0, elbow=True):
    """IBC as a sub-Part with placement pl (IBC local -> carrier). Objects <tag>_pallet, ... """
    I = G.ibc_local()
    grp = new_part(doc, parent, "IBC_" + tag, "IBC_1000l_" + tag, pl)
    add_shape(doc, grp, tag + "_pallet", tag + "_pallet_4way", I["pallet"], "pallet")
    add_shape(doc, grp, tag + "_bottle", tag + "_bottle_HDPE", I["bottle"], "bottle")
    add_shape(doc, grp, tag + "_liquid", tag + "_liquid", G.ibc_liquid_local(litres), "liquid")
    add_shape(doc, grp, tag + "_cage", tag + "_cage_tube_grid", I["cage"], "galv")
    add_shape(doc, grp, tag + "_valve", tag + "_valve_DN50", I["valve"], "black")
    add_shape(doc, grp, tag + "_cap", tag + "_cap_DN150", I["cap"], "white")
    if elbow:
        add_shape(doc, grp, tag + "_camlock", tag + "_camlock_elbow", G.camlock_elbow(), "camlock")
    if strap_axis:
        add_shape(doc, grp, tag + "_straps", tag + "_ratchet_straps_50mm", G.ibc_straps(strap_axis, strap_z), "strap")
        add_shape(doc, grp, tag + "_ratchets", tag + "_ratchets", G.ibc_ratchets(strap_axis, ratchet_z), "steel")
    return grp


def set_ibc_level(doc, tag, litres):
    o = doc.getObject(tag + "_liquid")
    if o is not None:
        o.Shape = G.ibc_liquid_local(litres)


def build_box(doc, parent, pl):
    """Control box as a sub-Part with placement pl (box local -> carrier)."""
    grp = new_part(doc, parent, "Control_box", "control_box_pump_and_electronics", pl)
    add_shape(doc, grp, "box_rails", "box_mounting_rails", G.box_rails(), "steel")
    add_shape(doc, grp, "box_shell", "enclosure_steel_IP55_600x400x450", G.box_shell(), "box")
    add_shape(doc, grp, "box_roof", "rain_roof", G.box_roof(), "box")
    add_shape(doc, grp, "box_door", "door_with_lock", G.box_door(), "door")
    base, knob = G.estop()
    add_shape(doc, grp, "box_estop_base", "emergency_stop_housing", base, "yellow")
    add_shape(doc, grp, "box_estop", "emergency_stop_button", knob, "red")
    add_shape(doc, grp, "box_glands", "cable_glands_and_bulkheads", G.box_glands(), "black")
    add_shape(doc, grp, "box_pump", "transfer_pump_24V_1.5in", G.pump(), "pump")
    add_shape(doc, grp, "box_pump_feet", "pump_feet", G.pump_feet(), "steel")
    add_shape(doc, grp, "box_line", "discharge_line_1.5in", G.discharge_line(), "pp")
    add_shape(doc, grp, "box_flow", "flow_meter", G.flow_meter(), "black")
    add_shape(doc, grp, "box_mvalve", "motorised_ball_valve", G.motor_valve(), "valve")
    add_shape(doc, grp, "box_battery", "battery_LiFePO4_25.6V_50Ah", G.battery(), "battery")
    add_shape(doc, grp, "box_din", "din_plate", G.din_plate(), "din")
    add_shape(doc, grp, "box_modules", "controller_rtk_radio_dcdc", G.din_modules(), "pcb")
    return grp


BOX_INSIDE = ("box_pump", "box_pump_feet", "box_line", "box_flow", "box_mvalve", "box_battery", "box_din",
              "box_modules")
BOX_COVER = ("box_shell", "box_roof", "box_door", "box_estop_base", "box_estop")


def arm_placement(M, angle):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), angle), V(M["x"], M["y"], 0))


def build_mast_arm(doc, parent, M, angle=0.0, beacon_face="+x", beacon_z=None):
    grp = new_part(doc, parent, "Mast", "mast_and_arm")
    add_shape(doc, grp, "mast", "mast_%dx%dx%d" % (M["tube"][0], M["tube"][0], M["tube"][1]), G.mast(M), "frame")
    add_shape(doc, grp, "mast_top_plate", "mast_top_plate_10mm", G.mast_top_plate(M), "frame")
    add_shape(doc, grp, "mast_pivot_pin", "pivot_pin_D30_washer_clip", G.pivot_pin(M), "zinc")
    bz = M["arm_z"][0] - 330.0 if beacon_z is None else beacon_z
    br, g, a, r = G.beacon(M["x"], M["y"], bz, beacon_face, M["tube"][0])
    add_shape(doc, grp, "beacon_bracket", "beacon_bracket", br, "steel")
    add_shape(doc, grp, "beacon_green", "beacon_green_ready", g, "green")
    add_shape(doc, grp, "beacon_amber", "beacon_amber_pumping", a, "amber")
    add_shape(doc, grp, "beacon_red", "beacon_red_fault", r, "red")
    arm = new_part(doc, grp, "Arm", "arm_swings_on_mast", arm_placement(M, angle))
    add_shape(doc, arm, "arm", "arm_60x60x3_with_boss", G.arm(M), "frame")
    add_shape(doc, arm, "arm_lock_pin", "lock_pin_D12", G.lock_pin(M), "zinc")
    add_shape(doc, arm, "arm_tip_plate", "arm_tip_plate", G.tip_plate(M), "frame")
    add_shape(doc, arm, "arm_drop_pipe", "drop_pipe_PP50", G.drop_pipe(M), "pp")
    add_shape(doc, arm, "arm_nozzle", "drip_stop_nozzle", G.nozzle(M), "black")
    add_shape(doc, arm, "arm_antenna", "rtk_antenna_above_nozzle", G.antenna(M), "white")
    add_shape(doc, arm, "arm_hose", "hose_along_arm", G.arm_hose(M), "hose")
    return grp


def set_arm(doc, M, angle):
    doc.getObject("Arm").Placement = arm_placement(M, angle)
    doc.recompute()


def in_arm(obj):
    parent = obj.getParentGeoFeatureGroup()
    while parent is not None:
        if parent.Name == "Arm":
            return True
        parent = parent.getParentGeoFeatureGroup()
    return False


# ---------------------------------------------------------------------
# Working robot (agbot design + liquid fertilizer applicator + receiver kit, via simple/build_mrs.py)
# ---------------------------------------------------------------------
def load_mrs():
    import build_mrs
    return build_mrs


def dock_reach(half_width):
    """Mast-free reach: carrier half width (widest part on the docking side) + gap + half the working robot,
    rounded up."""
    r = half_width + P.dock_clear + P.worker_half_w
    return math.ceil(r / P.dock_round) * P.dock_round


def worker_placement(M, angle=0.0, heading=0.0):
    """Working robot with its funnel under the nozzle (arm at 'angle'), robot heading 'heading' (0 = +y)."""
    a = math.radians(angle)
    nx = M["x"] - M["reach"] * math.cos(a)
    ny = M["y"] - M["reach"] * math.sin(a)
    rot = App.Rotation(V(0, 0, 1), heading)
    f = rot.multVec(V(P.funnel_xy[0], P.funnel_xy[1], 0))
    return App.Placement(V(nx - f.x, ny - f.y, 0), rot)


def build_worker(doc, pl, lift=140.0, rx_fill=None):
    BM = load_mrs()
    worker, wobjs = BM.build_robot(doc, "working_robot_with_applicator", pl)
    try:
        BL = BM.load_lfa()
        BL.build_into(doc, worker, lift, BL.translation(0.0, BL.P.robot_mount_y, 0.0))
    except Exception as exc:
        print("applicator not loaded:", exc)
    BM.build_receiver_into(doc, worker, rx_fill)
    return worker


# ---------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------
SKIP_SUFFIX = ("_liquid",)


def checked(objs):
    return [o for o in objs if not o.Name.endswith(SKIP_SUFFIX) and not base_name(o.Name).endswith(SKIP_SUFFIX)
            and not o.Shape.isNull() and o.Shape.Volume > 0]


def kit_objects(doc, root):
    return [o for o in doc.getObject(root).OutListRecursive if o.TypeId == "Part::Feature"]


def overlaps(pairs, ok, tol=1.0):
    hits = []
    for (oa, sa), (ob, sb) in pairs:
        key = frozenset((base_name(oa.Name), base_name(ob.Name)))
        if key in ok or not sa.BoundBox.intersect(sb.BoundBox):
            continue
        try:
            vol = sa.common(sb).Volume
        except Exception as exc:
            hits.append((oa.Label, ob.Label, "error %s" % exc))
            continue
        if vol > tol:
            hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits


def pair_ok(pairs):
    """Set of allowed contacts from (a, b) name pairs; a name may contain '*' for every IBC tag."""
    out = set()
    for a, b in pairs:
        out.add(frozenset((a, b)))
    return out


def check_interference(doc, root, ok, tol=1.0):
    mine = [(o, global_shape(o)) for o in checked(kit_objects(doc, root))]
    pairs = [(mine[i], mine[j]) for i in range(len(mine)) for j in range(i + 1, len(mine))]
    return overlaps(pairs, ok, tol)


def check_fit(doc, root, M, ok, angles=None, tol=1.0):
    """Arm swung through its range (lock pin pulled between the lock positions) against the rest. Must be empty."""
    if angles is None:
        lo, hi = min(M["folds"]), max(M["folds"])
        angles = list(range(int(lo), int(hi) + 1, 15))
    mine = checked(kit_objects(doc, root))
    still = [(o, global_shape(o)) for o in mine if not in_arm(o)]
    keep = doc.getObject("Arm").Placement
    out = {}
    for a in angles:
        doc.getObject("Arm").Placement = arm_placement(M, a)
        doc.recompute()
        locked = any(abs(a - f) < 1e-6 for f in M["folds"])
        mv = [(o, global_shape(o)) for o in mine if in_arm(o) and (locked or base_name(o.Name) != "arm_lock_pin")]
        hits = overlaps([(x, y) for x in mv for y in still], ok, tol)
        if hits:
            out[a] = hits
    doc.getObject("Arm").Placement = keep
    doc.recompute()
    return out


def check_docked(doc, root, worker_name, ok, tol=1.0):
    station = [(o, global_shape(o)) for o in checked(kit_objects(doc, root))]
    worker = [(o, global_shape(o)) for o in doc.getObject(worker_name).OutListRecursive
              if o.TypeId == "Part::Feature" and not o.Shape.isNull() and not o.Name.endswith("liquid")]
    return overlaps([(a, b) for a in station for b in worker], ok, tol)


def min_gap(doc, root, worker_name, z_max=1300.0):
    """Smallest horizontal-ish distance between station parts and the working robot (mm), parts below z_max."""
    cut = G.box_span((-20000.0, 20000.0), (-20000.0, 20000.0), (-10.0, z_max))
    st = [global_shape(o) for o in checked(kit_objects(doc, root)) if not in_arm(o)]
    wk = [global_shape(o) for o in doc.getObject(worker_name).OutListRecursive
          if o.TypeId == "Part::Feature" and not o.Shape.isNull() and not o.Name.endswith("liquid")]
    best = 1e9
    wb = None
    for s in wk:
        wb = s.BoundBox if wb is None else wb.united(s.BoundBox)
    for s in st:
        b = s.BoundBox
        b.enlarge(800.0)
        if not b.intersect(wb):
            continue
        c = s.common(cut)
        if c.isNull() or c.Volume <= 0:
            continue
        for w in wk:
            bb = w.BoundBox
            bb.enlarge(800.0)
            if not bb.intersect(c.BoundBox):
                continue
            best = min(best, c.distToShape(w)[0])
    return best


# ---------------------------------------------------------------------
# Mass: fixed masses for bought parts, the rest volume x density
# ---------------------------------------------------------------------
PE, ALU, STEEL, RUBBER = 0.95e-6, 2.7e-6, 7.85e-6, 1.15e-6
HOSE = 0.6 / (math.pi * (P.hose_od / 2.0) ** 2 * 1000.0)
MASS_FIXED = {"box_pump": P.pump_kg, "box_battery": P.box_kg["battery"], "box_modules": P.box_kg["electronics"],
              "box_flow": 1.5, "box_mvalve": 2.0, "box_shell": P.box_kg["enclosure"], "arm_antenna": 0.45,
              "arm_nozzle": 0.6, "box_estop": 0.1, "box_estop_base": 0.2, "box_glands": 0.4,
              "beacon_green": 0.15, "beacon_amber": 0.15, "beacon_red": 0.15}
IBC_FIXED = {"pallet": P.ibc_kg * 22.0 / 58.0, "cage": P.ibc_kg * 20.0 / 58.0, "bottle": P.ibc_kg * 14.5 / 58.0,
             "valve": 1.2, "cap": 0.3, "camlock": 0.5, "ratchets": 1.6}
DENSITY = {"arm_drop_pipe": PE, "box_line": PE, "arm_hose": HOSE}


def mass_cg(obj, fixed=None, density=None, liquid_rho=None):
    shape = global_shape(obj)
    if shape.isNull():
        return 0.0, V(0, 0, 0)
    solids = shape.Solids or [shape]
    vol = sum(s.Volume for s in solids)
    cg = V(0, 0, 0)
    for s in solids:
        cg += s.CenterOfMass * s.Volume
    cg = cg * (1.0 / vol) if vol > 0 else shape.BoundBox.Center
    name = base_name(obj.Name)
    fixed = dict(MASS_FIXED, **(fixed or {}))
    density = dict(DENSITY, **(density or {}))
    if name in fixed:
        return fixed[name], cg
    suffix = name.split("_", 1)[1] if "_" in name else name
    if name.startswith("ibc") and suffix in IBC_FIXED:
        return IBC_FIXED[suffix], cg
    if name.endswith("_liquid"):
        return vol * (P.liquid_density if liquid_rho is None else liquid_rho) * 1e-6, cg
    if name.endswith("_straps"):
        return vol * 1.2e-6, cg
    if name in density:
        return vol * density[name], cg
    for key, d in density.items():
        if key.endswith("*") and name.startswith(key[:-1]):
            return vol * d, cg
    return vol * STEEL, cg


def sum_mass(objs, fixed=None, density=None):
    m, c = 0.0, V(0, 0, 0)
    for o in objs:
        mo, co = mass_cg(o, fixed, density)
        m += mo
        c += co * mo
    return m, (c * (1.0 / m) if m > 0 else c)


def mass_groups(doc, root, groups, fixed=None, density=None):
    """groups: {name: predicate(obj)} -> {name_kg, name_cg}."""
    objs = kit_objects(doc, root)
    out = {}
    for name, sel in groups.items():
        m, c = sum_mass([o for o in objs if sel(o)], fixed, density)
        out[name + "_kg"] = round(m, 1)
        out[name + "_cg"] = (round(c.x), round(c.y), round(c.z))
    return out


def is_ibc(o):
    return base_name(o.Name).startswith("ibc") and not o.Name.endswith("_liquid")


def is_liquid(o):
    return o.Name.endswith("_liquid")


def bbox(doc, objs):
    bb = None
    for o in objs:
        if o.Shape.isNull() or (o.ViewObject is not None and not o.ViewObject.Visibility):
            continue
        b = global_shape(o).BoundBox
        bb = b if bb is None else bb.united(b)
    return bb


# ---------------------------------------------------------------------
# STEP export
# ---------------------------------------------------------------------
def export_step(doc, root, path):
    import Import
    objs = []
    for o in kit_objects(doc, root):
        if o.Shape.isNull() or o.Name.endswith("liquid"):
            continue
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
    tgt = V(*target) if target is not None else V(0, 0, 900)
    eye = tgt - d * 30000.0
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(80000.0)
    if height is None:
        view.fitAll()
    else:
        cam.height.setValue(height)
    return view


def save_view(folder, name, direction, target=None, height=None, up=(0.0, 0.0, 1.0), size_px=(1600, 1100)):
    import FreeCADGui as Gui
    Gui.updateGui()
    set_camera(direction, target, height, up)
    Gui.updateGui()
    view = set_camera(direction, target, height, up)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    view.saveImage(path, size_px[0], size_px[1], "White")
    return path


GROUND = ("render_floor", "render_stream")


def add_floor(doc, x, y, color=(0.62, 0.70, 0.52)):
    obj = doc.addObject("Part::Feature", GROUND[0])
    obj.Shape = G.box_span(x, y, (-40.0, 0.0))
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = 30
    return obj


def add_stream(doc, M, angle=0.0):
    a = math.radians(angle)
    nx = M["x"] - M["reach"] * math.cos(a)
    ny = M["y"] - M["reach"] * math.sin(a)
    obj = doc.addObject("Part::Feature", GROUND[1])
    obj.Shape = G.stream(nx, ny, M["nozzle_z"], P.FUNNEL_RIM_Z - 120.0)
    obj.ViewObject.ShapeColor = COLOR["liquid"]
    obj.ViewObject.Transparency = 30
    return obj


def remove(doc, names):
    for n in names:
        if doc.getObject(n):
            doc.removeObject(n)


def set_visible(doc, names, visible):
    for n in names:
        o = doc.getObject(n)
        if o is not None and o.ViewObject is not None:
            o.ViewObject.Visibility = visible
