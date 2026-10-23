import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import sol_params as P
import sol_parts as G
import sol_calc as C

DOC_NAME = "Solar_canopy"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Solar_canopy.FCStd")
STEP_PATH = os.path.join(FOLDER, "Solar_canopy.step")
PREVIEW_DIR = os.path.join(FOLDER, "previews")
AGBOT_FOLDER = os.path.join(os.path.dirname(FOLDER), "agbots", "agbot design")

COLOR = {
    "frame": (0.22, 0.24, 0.26),
    "plate": (0.35, 0.36, 0.38),
    "zinc": (0.82, 0.84, 0.87),
    "steel": (0.55, 0.55, 0.58),
    "brace": (0.30, 0.32, 0.35),
    "panel_frame": (0.75, 0.77, 0.80),
    "laminate": (0.05, 0.08, 0.25),
    "cells": (0.12, 0.20, 0.50),
    "jbox": (0.10, 0.10, 0.10),
    "mppt": (0.92, 0.55, 0.10),
    "white": (0.95, 0.95, 0.95),
}

DENSITY = P.frame_density
BASE_NAMES = ("Base",)
FRAME_GROUPS = ("Base", "Canopy")


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


def build_base(doc, parent):
    grp = new_part(doc, parent, "Base", "base_square_tube_50x50x3")
    for i, shp in enumerate(G.long_tubes()):
        add_shape(doc, grp, "long_tube_%d" % (i + 1), "long_tube_%s_across_width" % ("rear", "front")[i], shp, "frame")
    for i, shp in enumerate(G.stringers()):
        add_shape(doc, grp, "stringer_%d" % (i + 1), "stringer_%s_along_y" % ("left", "right")[i], shp, "frame")
    add_shape(doc, grp, "mount_sleeves", "mount_spacer_sleeves_D16", G.mount_sleeves(), "steel")
    add_shape(doc, grp, "mount_bolts", "mount_bolts_M10x130_to_upper_beams", G.mount_bolts(), "zinc")
    return grp


def build_canopy(doc, parent):
    grp = new_part(doc, parent, "Canopy", "canopy_frame_40x40x3")
    for i, shp in enumerate(G.posts()):
        add_shape(doc, grp, "post_%d" % (i + 1), "post_%d" % (i + 1), shp, "frame")
    for i, shp in enumerate(G.rails()):
        add_shape(doc, grp, "rail_%d" % (i + 1), "top_rail_%s_along_y" % ("left", "right")[i], shp, "frame")
    for i, shp in enumerate(G.cross_members()):
        add_shape(doc, grp, "cross_%d" % (i + 1), "cross_member_%s_across_width" % ("rear", "front")[i], shp, "frame")
    for i, shp in enumerate(G.struts()):
        add_shape(doc, grp, "strut_%d" % (i + 1), "strut_x_diagonal_%d" % (i + 1), shp, "brace")
    for i, shp in enumerate(G.y_braces()):
        add_shape(doc, grp, "ybrace_%d" % (i + 1), "brace_y_diagonal_%d" % (i + 1), shp, "brace")
    return grp


def build_panels(doc, parent):
    grp = new_part(doc, parent, "Panels", "solar_panels_%dx%dWp" % (P.n_panels, P.panel_wp))
    for i, cx in enumerate(G.panel_centres()):
        sub = new_part(doc, grp, "Panel_%d" % (i + 1), "solar_panel_%d" % (i + 1))
        add_shape(doc, sub, "panel_%d_frame" % (i + 1), "panel_%d_aluminium_frame" % (i + 1), G.panel_frame(cx), "panel_frame")
        add_shape(doc, sub, "panel_%d_laminate" % (i + 1), "panel_%d_glass_laminate" % (i + 1), G.panel_laminate(cx), "laminate")
        add_shape(doc, sub, "panel_%d_cells" % (i + 1), "panel_%d_cells" % (i + 1), G.panel_cells(cx), "cells")
        add_shape(doc, sub, "panel_%d_jbox" % (i + 1), "panel_%d_junction_box" % (i + 1), G.panel_junction_box(cx), "jbox")
    add_shape(doc, grp, "panel_bolts", "panel_bolts_M8_to_cross_members", G.panel_bolts(), "zinc")
    return grp


def build_electronics(doc, parent):
    grp = new_part(doc, parent, "Electronics", "electronics_MPPT_and_GNSS")
    add_shape(doc, grp, "mppt_plate", "mppt_base_plate_6mm", G.mppt_plate(), "plate")
    add_shape(doc, grp, "mppt", "mppt_charge_controller", G.mppt_box(), "mppt")
    add_shape(doc, grp, "gnss_mast", "gnss_mast_D25", G.gnss_mast(), "zinc")
    add_shape(doc, grp, "gnss_antenna", "gnss_antenna_on_roof", G.gnss_antenna(), "white")
    return grp


def build_into(doc, parent=None):
    root = new_part(doc, parent, "Solar", "solar_canopy")
    build_base(doc, root)
    build_canopy(doc, root)
    build_panels(doc, root)
    build_electronics(doc, root)
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


def hide_robot_gnss(doc):
    """The antenna is moved to the roof (under the panels there is no sky): hide the one on the front beam."""
    for name in ("gnss_dome", "gnss_mount"):
        o = doc.getObject(name)
        if o is not None and o.ViewObject is not None:
            o.ViewObject.Visibility = False


def build(save_path=SAVE_PATH, step_path=STEP_PATH):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Solar canopy"
    doc.Comment = ("Generated with build_sol.py from sol_params.py. Robot coordinates: x = right, y = driving "
                   "direction (front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    hide_robot_gnss(doc)
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    if step_path:
        export_step(doc, step_path)
    return doc


def solar_objects(doc):
    return [o for o in doc.getObject("Solar").OutListRecursive if o.TypeId == "Part::Feature"]


def robot_objects(doc):
    robot = doc.getObject("Robot")
    if robot is None:
        return []
    mine = {o.Name for o in solar_objects(doc)}
    return [o for o in robot.OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in mine]


def export_step(doc, path):
    import Import
    objs = []
    for o in solar_objects(doc):
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


SKIP = ("mount_bolts", "mount_sleeves", "panel_bolts")


def skipped(o):
    """Bolts, sleeves and the thin cell plates (120 solids, slow, only lying on the laminate)."""
    return o.Name in SKIP or o.Name.endswith("_cells")


def check_interference(doc=None, tol=1.0):
    """Pairs with a common volume > tol mm3: canopy among itself and against the robot. Bolts/sleeves excluded."""
    doc = doc or App.getDocument(DOC_NAME)
    mine = [o for o in solar_objects(doc) if not skipped(o) and o.ViewObject.Visibility]
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
    """Smallest distance (mm) from the canopy parts to the visible robot parts (upper beams not counted)."""
    doc = doc or App.getDocument(DOC_NAME)
    res = {}
    others = [o for o in robot_objects(doc) if o.ViewObject.Visibility]
    for o in solar_objects(doc):
        if skipped(o):
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
        "Base": None,
        "Canopy": None,
        "Panels": C.mass_panels(),
        "Electronics": P.mppt_mass + P.gnss_mass,
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
    from pivy import coin  # noqa: F401 (loads the SWIG wrapper for getCameraNode)
    os.makedirs(folder, exist_ok=True)
    doc = App.getDocument(DOC_NAME)
    for o in robot_objects(doc):
        if o.Name in ("gnss_dome", "gnss_mount"):
            continue
        o.ViewObject.Visibility = robot_visible
    view = Gui.ActiveDocument.ActiveView
    views = {
        "1_iso": (1, -1, 0.9),
        "2_top": (0, 0, 1),
        "3_side": (1, 0, 0),
        "4_front": (0, -1, 0),
        "5_iso_rear": (-1, 1, 0.9),
        "6_iso_low": (1, -1, 0.25),
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
