"""Bouwt de scene voor de veldanimaties: de werkrobot (combined_v2 met 5 rijen) met een werktank en vultrechter, de
refiller van het scenario en het veld.

Boom (document <scenario>_field_animation, hoeft niet opgeslagen te worden):
    Robot                         werkrobot uit agbots/agbot design, pomp, applicator V2, slangen (build_cmb2)
      Work_tank_kit               zadelkokers, werktank, vultrechter, zeef, niveausensor, ontluchting
    Robot001 / Station            refiller (mobile refiller/simple of liquid) of IBC-aanhanger (stationary/ibc_trailer)
    anim_*                        veld, kopakkers, hek, sporen van de applicator, route, straal

Gebruik in FreeCAD:
    import build_fld
    doc = build_fld.build_tank_check()       # alleen de werkrobot met tank: interferentie en maten
    build_fld.check_interference(doc)        # moet leeg zijn
    build_fld.worker_outline(doc)            # buitenmaten werkrobot (robotcoordinaten), voor de afstand tot de refiller
"""
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fld_plan                    # zet sys.path (combined_v2, robot, applicator, refillers)
import fld_params as P
import fld_parts as G

import build_cmb2
import build_pa
import build_rp
import build_pa2
import cmb2_parts

PREFIX = build_cmb2.PREFIX
FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
CHECK_DOC = "Precision_applicator_V2_work_tank"

COLOR = {
    "frame": (0.18, 0.36, 0.62), "rubber": (0.10, 0.10, 0.10), "tank": (0.93, 0.93, 0.88),
    "liquid": (0.15, 0.45, 0.80), "funnel": (0.95, 0.75, 0.10), "steel": (0.75, 0.75, 0.78),
    "zinc": (0.82, 0.84, 0.87), "black": (0.05, 0.05, 0.05), "yellow": (0.95, 0.75, 0.10),
    "field": (0.47, 0.63, 0.31), "headland": (0.60, 0.70, 0.44), "lines": (0.66, 0.78, 0.50),
    "treated": (0.33, 0.50, 0.24), "slot": (0.22, 0.14, 0.08), "flow": (0.12, 0.40, 0.85),
    "closed": (0.72, 0.60, 0.40), "post": (0.45, 0.33, 0.20), "wire": (0.75, 0.75, 0.75),
    "path": (0.96, 0.96, 0.92), "stream": (0.15, 0.50, 0.85),
}
TRANSPARENT = {"tank": 45}


def add_shape(doc, parent, name, label, shape, color, visible=True):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    if parent is not None:
        parent.addObject(obj)
    if obj.ViewObject is not None:
        rgb = COLOR[color] if isinstance(color, str) else color
        obj.ViewObject.ShapeColor = rgb
        obj.ViewObject.LineColor = rgb
        obj.ViewObject.Transparency = TRANSPARENT.get(color, 0) if isinstance(color, str) else 0
        obj.ViewObject.Visibility = visible
    return obj


# ---------------------------------------------------------------------
# Werkrobot met werktank
# ---------------------------------------------------------------------
def build_tank_kit(doc, robot, litres):
    kit = build_pa.new_part(doc, robot, "Work_tank_kit", "work_tank_kit")
    add_shape(doc, kit, "fld_rx_cradle", "cradle_tubes_40x40x3", G.cradle_tubes(), "frame")
    add_shape(doc, kit, "fld_rx_pads", "rubber_strips_5mm", G.cradle_pads(), "rubber")
    add_shape(doc, kit, "fld_rx_tank", "work_tank_PE_%dl" % round(G.tank_volume_l()), G.tank_shell(), "tank")
    add_shape(doc, kit, "fld_rx_liquid", "liquid_in_work_tank", G.liquid(litres), "liquid")
    add_shape(doc, kit, "fld_rx_straps", "tank_straps_50x3", G.straps(), "zinc")
    add_shape(doc, kit, "fld_rx_funnel", "fill_funnel_300", G.funnel(), "funnel")
    add_shape(doc, kit, "fld_rx_strainer", "funnel_strainer", G.strainer(), "steel")
    add_shape(doc, kit, "fld_rx_level", "level_sensor_ultrasonic", G.level_sensor(), "black")
    add_shape(doc, kit, "fld_rx_vent", "vent", G.vent(), "yellow")
    add_shape(doc, kit, "fld_rx_feed", "feed_hose_to_pump_manifold", G.feed_pipe(), "black")
    return kit


def build_worker(doc, lift, litres):
    build_cmb2.configure(5)
    robot = build_cmb2.build_into(doc, lift)
    build_tank_kit(doc, robot, litres)
    return robot


def build_tank_check(lift=0.0):
    build_cmb2.configure(5)
    if CHECK_DOC in App.listDocuments():
        App.closeDocument(CHECK_DOC)
    doc = App.newDocument(CHECK_DOC)
    doc.Label = "Precision applicator V2 (5 rows) with work tank and fill funnel"
    build_worker(doc, lift, 60.0)
    doc.recompute()
    return doc


def global_shape(obj):
    s = obj.Shape.copy()
    s.Placement = obj.getGlobalPlacement()
    return s


def check_interference(doc=None, tol=1.0):
    """Werktankkit tegen de rest van de werkrobot (pomp, robot, applicator, slangen): moet leeg zijn."""
    doc = doc or App.getDocument(CHECK_DOC)
    kit = [o for o in doc.getObject("Work_tank_kit").OutListRecursive if o.TypeId == "Part::Feature"]
    kit_names = {o.Name for o in kit}
    others = [o for o in doc.getObject("Robot").OutListRecursive
              if o.TypeId == "Part::Feature" and o.Name not in kit_names and not o.Shape.isNull()]
    hits = []
    for a in kit:
        if a.Name == "fld_rx_liquid" or a.Shape.isNull():
            continue
        sa = global_shape(a)
        for b in others:
            sb = global_shape(b)
            if sa.BoundBox.intersect(sb.BoundBox):
                vol = sa.common(sb).Volume
                if vol > tol:
                    hits.append((a.Label, b.Label, round(vol, 1)))
    return hits


def clearance(doc=None):
    """Kleinste afstanden van tank en trechter tot de pomp en de stappenmotoren voor."""
    doc = doc or App.getDocument(CHECK_DOC)
    kit = [o for o in doc.getObject("Work_tank_kit").OutListRecursive if o.TypeId == "Part::Feature"
           and o.Name != "fld_rx_liquid"]
    pump = [o for o in doc.getObject("Roller_pump").OutListRecursive if o.TypeId == "Part::Feature"]
    sk = Part.makeCompound([global_shape(o) for o in kit if o.Name != "fld_rx_feed"])
    sp = Part.makeCompound([global_shape(o) for o in pump])
    front = Part.makeCompound([global_shape(o) for o in doc.Objects if o.TypeId == "Part::Feature"
                               and o.Name.startswith(("FL_", "FR_")) and "stepper" in o.Label.lower()])
    out = {"tank_to_pump_mm": round(sk.distToShape(sp)[0], 1), "tank_volume_l": round(G.tank_volume_l(), 1),
           "funnel_rim_z": P.FUNNEL_RIM_Z, "pump_top_z": round(sp.BoundBox.ZMax, 1)}
    if not front.isNull() and front.SubShapes:
        out["tank_to_front_steppers_mm"] = round(sk.distToShape(front)[0], 1)
    return out


def worker_outline(doc=None, lift=None):
    """Buitenmaten van de werkrobot met applicator (robotcoordinaten): x min/max, y min/max, z max."""
    doc = doc or App.getDocument(CHECK_DOC)
    if lift is not None:
        build_cmb2.set_lift(lift, doc)
        doc.recompute()
    bb = App.BoundBox()
    for o in doc.getObject("Robot").OutListRecursive:
        if o.TypeId == "Part::Feature" and not o.Shape.isNull() and o.ViewObject.Visibility:
            bb.add(global_shape(o).BoundBox)
    return {"x": (round(bb.XMin), round(bb.XMax)), "y": (round(bb.YMin), round(bb.YMax)), "z_max": round(bb.ZMax)}


# ---------------------------------------------------------------------
# Refillers
# ---------------------------------------------------------------------
def build_refiller(doc, kind, run):
    """Bouwt de refiller van het scenario; geeft een dict met de objecten die de animatie verzet."""
    fr = run["frames"][0]["ref"]
    if kind == "simple":
        import build_mrs as BM
        robot, objs = BM.build_robot(doc, "refiller_robot_simple_ibc")
        BM.hide_robot_gnss(objs)
        BM.build_refiller_into(doc, robot, 0.0, fr["ibc"])
        return {"kind": kind, "mod": BM, "root": robot, "objs": objs}
    if kind == "liquid":
        import build_mrl as BL
        robot, objs = BL.build_robot(doc, "refiller_robot_liquid")
        phi, r, s = fr["boom"]
        BL.build_refiller_into(doc, robot, phi, r, s, 0.0, fill=0.85)
        return {"kind": kind, "mod": BL, "root": robot, "objs": objs}
    import build_sit as BS
    import stc_parts as SG
    BS.STATE["n"] = 1
    BS.build_into(doc, 1, 0.0, fr["ibc"])
    root = doc.getObject(BS.ROOT)
    (x, y), rot = fr["pose"], 90.0
    root.Placement = App.Placement(V(x, y, 0.0), App.Rotation(V(0, 0, 1), rot))
    return {"kind": kind, "mod": BS, "SG": SG, "root": root, "objs": {}}


# ---------------------------------------------------------------------
# Veld
# ---------------------------------------------------------------------
def build_ground(doc, run):
    field, head = G.ground()
    add_shape(doc, None, "anim_field", "field", field, "field")
    add_shape(doc, None, "anim_headland", "headlands", head, "headland")
    add_shape(doc, None, "anim_pass_lines", "pass_boundaries", G.pass_lines(), "lines")
    posts, wires = G.fence()
    add_shape(doc, None, "anim_posts", "fence_posts", posts, "post")
    add_shape(doc, None, "anim_wires", "fence_wires", wires, "wire")
    for p in range(1, P.N_PASSES + 1):
        add_shape(doc, None, "anim_band_%d" % p, "treated_pass_%d" % p, Part.Shape(), "treated")
        add_shape(doc, None, "anim_slot_%d" % p, "open_slots_pass_%d" % p, Part.Shape(), "slot")
        add_shape(doc, None, "anim_flow_%d" % p, "liquid_in_slots_pass_%d" % p, Part.Shape(), "flow")
        add_shape(doc, None, "anim_closed_%d" % p, "closed_slots_pass_%d" % p, Part.Shape(), "closed")
    add_shape(doc, None, "anim_path", "planned_turn", Part.Shape(), "path")
    add_shape(doc, None, "anim_stream", "liquid_stream", Part.Shape(), "stream")
