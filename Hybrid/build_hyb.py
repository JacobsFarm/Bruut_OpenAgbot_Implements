import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import hyb_params as P
import hyb_parts as G
import hyb_calc as C

DOC_NAME = "Hybrid_range_extender"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Hybrid_range_extender.FCStd")
STEP_PATH = os.path.join(FOLDER, "Hybrid_range_extender.step")
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(FOLDER), "agbots", "agbot design")

COLOR = {
    "frame": (0.22, 0.24, 0.26),
    "plate": (0.35, 0.36, 0.38),
    "zinc": (0.82, 0.84, 0.87),
    "engine": (0.80, 0.10, 0.08),
    "tank": (0.85, 0.15, 0.10),
    "steel": (0.55, 0.55, 0.58),
    "muffler": (0.45, 0.40, 0.36),
    "generator": (0.15, 0.35, 0.60),
    "coupling": (0.95, 0.70, 0.05),
    "battery": (0.10, 0.45, 0.25),
    "strap": (0.15, 0.15, 0.17),
    "controller": (0.92, 0.55, 0.10),
    "filter": (0.10, 0.10, 0.10),
}

# material density (kg/m3) for the frame mass; components use the estimated masses from hyb_params
DENSITY = P.frame_density


def new_part(doc, parent, name, label, placement=None):
    part = doc.addObject("App::Part", name)
    part.Label = label
    if placement is not None:
        part.Placement = placement
    if parent is not None:
        parent.addObject(part)
    return part


def add_shape(doc, parent, name, label, shape, color, visible=True, transparency=0):
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
        view.Transparency = transparency
    return obj


def build_frame(doc, parent):
    grp = new_part(doc, parent, "Frame", "frame_square_tube_50x50x3")
    for i, shp in enumerate(G.long_tubes()):
        add_shape(doc, grp, "long_tube_%d" % (i + 1), "long_tube_%s_across_width" % ("rear", "front")[i], shp, "frame")
    for i, shp in enumerate(G.short_tubes()):
        add_shape(doc, grp, "short_tube_%d" % (i + 1), "short_tube_%d_along_y" % (i + 1), shp, "frame")
    add_shape(doc, grp, "mount_sleeves", "mount_spacer_sleeves_D16", G.mount_sleeves(), "steel")
    add_shape(doc, grp, "mount_bolts", "mount_bolts_M10x130_to_upper_beams", G.mount_bolts(), "zinc")
    return grp


def build_engine(doc, parent):
    grp = new_part(doc, parent, "Engine", "engine_petrol_212cc")
    add_shape(doc, grp, "engine_plate", "engine_base_plate_6mm", G.engine_plate(), "plate")
    add_shape(doc, grp, "engine", "engine_block_crankcase_head_fan", G.engine(), "engine")
    add_shape(doc, grp, "fuel_tank", "fuel_tank_3L", G.fuel_tank(), "tank")
    add_shape(doc, grp, "muffler", "muffler", G.muffler(), "muffler")
    add_shape(doc, grp, "air_filter", "air_filter", G.air_filter(), "filter")
    return grp


def build_generator(doc, parent):
    grp = new_part(doc, parent, "Generator", "generator_PM_alternator_3kW")
    add_shape(doc, grp, "generator", "generator_body_cap_terminal_box", G.generator(), "generator")
    add_shape(doc, grp, "flange", "generator_adapter_flange", G.generator_flange(), "steel")
    add_shape(doc, grp, "saddle", "generator_saddle_block", G.generator_saddle(), "plate")
    add_shape(doc, grp, "coupling", "jaw_coupling_engine_to_generator", G.coupling(), "coupling")
    return grp


def build_battery(doc, parent):
    grp = new_part(doc, parent, "Battery", "battery_60V_40Ah")
    add_shape(doc, grp, "battery_plate", "battery_base_plate_6mm", G.battery_plate(), "plate")
    add_shape(doc, grp, "battery", "battery_pack_16S_2.4kWh", G.battery(), "battery")
    add_shape(doc, grp, "battery_strap", "battery_hold_down_strap", G.battery_strap(), "strap")
    return grp


def build_controller(doc, parent):
    grp = new_part(doc, parent, "Controller", "controller_rectifier_BMS_box")
    add_shape(doc, grp, "controller_plate", "controller_base_plate_6mm", G.controller_plate(), "plate")
    add_shape(doc, grp, "controller", "controller_box", G.controller(), "controller")
    return grp


def build_into(doc, parent=None):
    root = new_part(doc, parent, "Hybrid", "hybrid_range_extender")
    build_frame(doc, root)
    build_engine(doc, root)
    build_generator(doc, root)
    build_controller(doc, root)
    build_battery(doc, root)
    return root


def build_robot(doc):
    """Real robot model from 'agbot design' (read only, nothing there is changed)."""
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    return robot


def build(save_path=SAVE_PATH, step_path=STEP_PATH):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Hybrid range extender"
    doc.Comment = ("Generated with build_hyb.py from hyb_params.py. Robot coordinates: x = right, y = driving "
                   "direction (front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    if step_path:
        export_step(doc, step_path)
    return doc


def hybrid_objects(doc):
    return [o for o in doc.getObject("Hybrid").OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in hybrid_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine]


def export_step(doc, path):
    import Import
    objs = []
    for o in hybrid_objects(doc):
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
# Checks
# ---------------------------------------------------------------------
def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def check_interference(doc=None, tol=1.0):
    """Pairs with a common volume > tol mm3: hybrid among itself and against the robot. Bolts/sleeves excluded."""
    doc = doc or App.getDocument(DOC_NAME)
    skip = ("mount_bolts", "mount_sleeves")
    mine = [o for o in hybrid_objects(doc) if o.Name not in skip and o.ViewObject.Visibility]
    others = [o for o in robot_objects(doc) if o.ViewObject.Visibility]
    shp = {o.Name: global_shape(o) for o in mine + others}
    found = []
    def pair(a, b):
        sa, sb = shp[a.Name], shp[b.Name]
        if not sa.BoundBox.intersect(sb.BoundBox):
            return
        vol = sa.common(sb).Volume
        if vol > tol:
            found.append((a.Label, b.Label, round(vol, 1)))
    for i, a in enumerate(mine):
        for b in mine[i + 1:]:
            pair(a, b)
        for b in others:
            pair(a, b)
    return found


def clearance(doc=None):
    """Smallest distance (mm) from the hybrid parts to the robot parts (tires, steering stack, beams not counted as touching)."""
    doc = doc or App.getDocument(DOC_NAME)
    res = {}
    others = [o for o in robot_objects(doc)]
    for o in hybrid_objects(doc):
        if o.Name in ("mount_bolts", "mount_sleeves"):
            continue
        so = global_shape(o)
        for r in others:
            if "beam" in r.Name:
                continue
            d = so.distToShape(global_shape(r))[0]
            key = o.Label
            if key not in res or d < res[key][0]:
                res[key] = (round(d, 1), r.Label)
    return dict(sorted(res.items(), key=lambda kv: kv[1][0])[:6])


def mass_properties(doc=None):
    """Mass (kg) and centre of gravity (mm). Frame from the volume, components from the estimated masses."""
    doc = doc or App.getDocument(DOC_NAME)
    groups = {
        "Frame": None,
        "Engine": P.eng_mass,
        "Generator": P.gen_mass,
        "Controller": P.ctl_mass,
        "Battery": P.batt_mass,
    }
    total = 0.0
    mom = V(0, 0, 0)
    rows = {}
    for gname, mass in groups.items():
        grp = doc.getObject(gname)
        objs = [o for o in grp.OutListRecursive if o.TypeId == "Part::Feature"]
        shapes = [global_shape(o) for o in objs]
        if mass is None:
            vol = sum(s.Volume for s in shapes)
            mass = vol * 1e-9 * DENSITY
            cg = V(0, 0, 0)
            for s in shapes:
                for sol in s.Solids:
                    cg = cg + sol.CenterOfMass * sol.Volume
            cg = cg * (1.0 / vol)
        else:
            box = App.BoundBox()
            for s in shapes:
                box.add(s.BoundBox)
            cg = box.Center
        rows[gname] = (round(mass, 1), tuple(round(c) for c in (cg.x, cg.y, cg.z)))
        total += mass
        mom = mom + cg * mass
    cg = mom * (1.0 / total)
    return round(total, 1), (round(cg.x), round(cg.y), round(cg.z)), rows


# ---------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------
def render_all(folder=PREVIEW_DIR, robot_visible=True):
    import FreeCADGui as Gui
    from pivy import coin
    os.makedirs(folder, exist_ok=True)
    doc = App.getDocument(DOC_NAME)
    for o in robot_objects(doc):
        o.ViewObject.Visibility = robot_visible
    view = Gui.ActiveDocument.ActiveView
    views = {
        "1_iso": (1, -1, 0.9),
        "2_top": (0, 0, 1),
        "3_side": (1, 0, 0),
        "4_front": (0, -1, 0),
        "5_iso_rear": (-1, 1, 0.9),
    }
    for name, d in views.items():
        view.viewIsometric()
        cam = view.getCameraNode()
        zax = V(*d)
        zax.normalize()
        up = V(0, 1, 0) if abs(zax.z) > 0.99 else V(0, 0, 1)
        xax = up.cross(zax)
        xax.normalize()
        yax = zax.cross(xax)
        mat = App.Matrix(xax.x, yax.x, zax.x, 0, xax.y, yax.y, zax.y, 0, xax.z, yax.z, zax.z, 0, 0, 0, 0, 1)
        cam.orientation.setValue(App.Rotation(mat).Q)
        view.fitAll()
        view.saveImage(os.path.join(folder, name + ".png"), 1600, 1000, "White")
    return sorted(os.listdir(folder))
