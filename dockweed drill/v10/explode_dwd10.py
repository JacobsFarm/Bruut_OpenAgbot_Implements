"""Exploded-view animation of the dockweed drill v10: take it apart, then build it up again piece by piece, with the
focus on the new Z axis (rail beams, HGR20 rails, HGH20CA carriages, the bent U sled and the Linak LA36), then the
spindle bracket, motor, cutter and can on the sled, and at the end a full stroke (driving height to 200 mm deep and
back) with the slide running to x +300 and back, so the carriages roll along the rails and the belt runs.

Builds a separate document (DWD10_exploded_animation) with the implement only (from build_dwd10.build_into) and a
ground plate that only shows during the stroke. Every Part::Feature gets an explode offset (EXPLODE, world mm; the
parents only translate). Nothing is changed in the model files.

Use in FreeCAD:
    import explode_dwd10
    explode_dwd10.build()
    explode_dwd10.play()                       # live, explode_dwd10.stop()
    explode_dwd10.summary()
    explode_dwd10.render_all(r"C:\\temp\\dwd10_explode")
    import make_gif_dwd10
    make_gif_dwd10.main_explode(r"C:\\temp\\dwd10_explode", r"previews\\exploded_assembly_linear_guide.gif")
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd10_params as P
import build_dwd10

DOC_NAME = "DWD10_exploded_animation"
FPS = 12
HIGHLIGHT = (1.0, 0.82, 0.10)          # colour of a part while it moves into place
GHOST = 88                             # transparency of the other parts during the focus
GROUND = (0.45, 0.62, 0.31)
STROKE_X = 300.0                       # X move during the final stroke

_timer = None
_play = {}


# ---------------------------------------------------------------------
# Explode offsets (mm, x right, y forward to the robot, z up)
# ---------------------------------------------------------------------
def _add(a, b):
    return tuple(a[k] + b[k] for k in range(3))


XS = (0.0, -700.0, 0.0)               # X slide and everything on it: backwards, off the X tubes
A = _add(XS, (0.0, -250.0, 750.0))    # LA36: up above the slide, opened up along its axis
R = _add(XS, (0.0, -350.0, 0.0))      # rail beams with the rails: behind the slide
Z = _add(R, (0.0, -450.0, 0.0))       # Z sled
SB = _add(Z, (0.0, -450.0, 0.0))      # spindle bracket and everything on it

EXPLODE = {
    # headstock: the uprights stay (reference), the rest moves away from them
    "upright_left": (0, 0, 0), "upright_right": (0, 0, 0),
    "hs_top_left": (0, 0, 120), "hs_top_right": (0, 0, 120),
    "hs_back_left": (0, 220, 0), "hs_back_right": (0, 220, 0),
    "gusset_left": (-160, 0, 0), "gusset_right": (160, 0, 0),
    "upright_cap_left": (0, 0, 220), "upright_cap_right": (0, 0, 220),
    "hs_clamp_left": (0, 0, -170), "hs_clamp_right": (0, 0, -170),
    "hs_bolts_left": (0, 0, -380), "hs_bolts_right": (0, 0, -380),
    "hs_cross": (0, 0, -330),
    # electrics: forward (to the robot)
    "ebox_plate": (0, 300, 0), "ebox": (0, 560, 0), "ebox_glands": (0, 560, -260),
    # X axis: cross beams up/down, tubes backwards, side plates sideways, drive to the right and forward
    "x_beam_lower": (0, -60, -220), "x_beam_upper": (0, -60, 220), "x_beam_bolts": (0, 380, 0),
    "x_guide_tube_lower": (0, -300, -330), "x_guide_tube_upper": (0, -300, 330), "tube_plugs": (0, -300, 0),
    "end_plate_left": (-480, 0, 0), "end_plate_right": (480, 0, 0),
    "tube_bolts_left": (-700, 0, 0), "tube_bolts_right": (700, 0, 0),
    "drive_bracket_left": (-330, -60, 0), "drive_bracket_right": (330, -60, 0),
    "x_gearbox": (360, 260, 0), "x_motor": (360, 470, 0),
    "x_pulleys": (0, -420, 0), "x_pulley_shafts": (0, -200, 0),
    "belt_upper": (0, -520, 140), "belt_lower": (0, -520, -140),
    "limit_switch": (-650, 0, 0), "end_stop": (650, 0, 0), "chain_bracket": (-330, 0, 260),
    "chain_lower": (0, 0, 380), "chain_upper": (0, 0, 460), "chain_bend": (0, 0, 420),
    # X slide
    "x_slide": XS, "x_houses": _add(XS, (0, 330, 0)), "x_house_bolts": _add(XS, (0, 520, 0)),
    "x_bushes": _add(XS, (-260, 330, 0)), "x_wipers": _add(XS, (260, 330, 0)),
    "x_grease_nipples": _add(XS, (0, 330, -220)), "belt_clamp": _add(XS, (0, 220, -170)),
    "chain_driver": _add(XS, (0, 160, 420)), "cable_bracket_x": _add(XS, (380, -220, 260)),
    # LA36
    "act_top_bracket": _add(A, (0, 0, 430)), "act_pin_top": _add(A, (-200, 0, 430)),
    "act_body": _add(A, (0, 0, 180)), "act_rod": _add(A, (0, 0, -270)), "act_pin_eye": _add(A, (-200, 0, -560)),
    # Z rail frame
    "rail_beam_left": R, "rail_beam_right": R, "rail_beam_caps": _add(R, (0, 0, -330)),
    "rail_beam_bolts": _add(XS, (0, 520, 0)), "z_rails": _add(R, (0, -150, 0)), "rail_bolts": _add(R, (0, -300, 0)),
    "rail_stops": _add(R, (0, -150, 0)),
    # Z sled and carriages
    "z_carriages": _add(R, (0, -270, 0)), "carriage_nipples": _add(R, (0, -270, 0)),
    "z_sled": Z, "act_eye_bracket": Z, "carriage_bolts": _add(Z, (0, -260, 0)), "cable_bracket_z": _add(Z, (380, 0, 0)),
    "spiral_cable": _add(XS, (520, -480, 0)),
    # spindle bracket
    "sb_lower": _add(SB, (0, 0, -230)), "sb_top": _add(SB, (0, 0, 260)),
    "sb_side_left": _add(SB, (-180, 0, 0)), "sb_side_right": _add(SB, (180, 0, 0)), "sb_bearing_plate": SB,
    "bearing_lower": _add(SB, (0, -260, -90)), "bearing_upper": _add(SB, (0, -260, 90)),
    "bearing_bolts": _add(SB, (0, 300, 0)),
    "spindle_shaft": _add(SB, (0, -560, 0)), "spindle_flange": _add(SB, (0, -560, -110)),
    "jaw_coupling": _add(SB, (0, -560, 380)), "spindle_motor_shaft": _add(SB, (0, -560, 520)),
    "spindle_motor": _add(SB, (0, -560, 760)),
    "motor_plate": _add(SB, (300, -560, 520)), "motor_gussets": _add(SB, (190, -560, 420)),
    "pot_bushes": _add(SB, (0, 0, -380)),
    "pot_sensor": _add(SB, (330, 0, -60)), "pot_sensor_bracket": _add(SB, (280, 0, -60)),
    # cutter (Tool, below the spindle)
    "cutter_flange": _add(SB, (0, -560, -200)), "cutter_core_tube": _add(SB, (0, -560, -265)),
    "cutter_cross_upper": _add(SB, (0, -560, -325)), "cutter_cross_lower": _add(SB, (0, -560, -385)),
    "cutter_teeth": _add(SB, (0, -560, -450)), "cutter_centre_point": _add(SB, (0, -560, -540)),
    # can
    "pot_set_rings": _add(SB, (0, -1000, 260)), "pot_rods": _add(SB, (0, -1000, 120)),
    "shaft_seal": _add(SB, (0, -1000, -40)), "pot_lid": _add(SB, (0, -1000, -110)),
    "pot_shell": _add(SB, (0, -1000, -330)),
    # camera: up
    "camera_mast": (0, 0, 250), "camera_arm": (0, -250, 420),
    "camera_crossbar": (0, -450, 560), "led_bar": (0, -450, 700), "camera": (0, -450, 380),
}

# assembly order: (label, objects)
STEPS = [
    ("Headstock: 2 uprights 40x40x3 with top plate, back plate, gusset and cap, cross tube",
     ["hs_top_left", "hs_top_right", "hs_back_left", "hs_back_right", "gusset_left", "gusset_right",
      "upright_cap_left", "upright_cap_right", "hs_cross"]),
    ("Clamp plates and M10 bolts onto the robot's rear beam", ["hs_clamp_left", "hs_clamp_right",
                                                              "hs_bolts_left", "hs_bolts_right"]),
    ("Electrics: mounting plate, IP65 box, cable glands", ["ebox_plate", "ebox", "ebox_glands"]),
    ("X frame: 2 cross beams 40x40x3 and 2 side plates 12 mm, 4 x M12 to the uprights",
     ["x_beam_lower", "x_beam_upper", "x_beam_bolts", "end_plate_left", "end_plate_right"]),
    ("2 precision tubes D50x4 with welded plugs, 8 x M10 through the side plates",
     ["x_guide_tube_lower", "x_guide_tube_upper", "tube_plugs", "tube_bolts_left", "tube_bolts_right"]),
    ("X drive fixed at the right end: bracket, 5:1 gearbox, NEMA 23 closed loop",
     ["drive_bracket_right", "x_gearbox", "x_motor"]),
    ("Tension pulley in its slot at the left, 2 pulleys HTD5M 20T, upper belt run",
     ["drive_bracket_left", "x_pulley_shafts", "x_pulleys", "belt_upper"]),
    ("Limit switch, end stop and cable chain support", ["limit_switch", "end_stop", "chain_bracket"]),
    ("X slide alu 12 mm", ["x_slide"]),
    ("3 bush housings D50 on the X tubes, iglidur bushes, wipers, M8, grease nipples",
     ["x_houses", "x_bushes", "x_wipers", "x_house_bolts", "x_grease_nipples"]),
    ("Belt clamp on the slide: the lower belt run moves with the slide", ["belt_clamp", "belt_lower"]),
    ("Cable chain and its driver", ["chain_driver", "chain_lower", "chain_upper", "chain_bend"]),
    ("Camera mast, arm, crossbar, camera and LED bar",
     ["camera_mast", "camera_arm", "camera_crossbar", "camera", "led_bar"]),
]
FOCUS_STEPS = [
    ("Z axis: 2 rail beams RHS 50x40x4, 4 x M8 each through the X slide",
     ["rail_beam_left", "rail_beam_right", "rail_beam_caps", "rail_beam_bolts"]),
    ("2 profile rails HGR20, M5 every 60 mm into the back of the rail beams", ["z_rails", "rail_bolts"]),
    ("Rubber end stops under and above each rail", ["rail_stops"]),
    ("4 carriages HGH20CA (double seal + scraper) slide onto the rails", ["z_carriages", "carriage_nipples"]),
    ("Z sled: 6 mm plate bent into a U, with the rod-eye bracket in the middle (as the photo)",
     ["z_sled", "act_eye_bracket"]),
    ("16 x M5 from the back of the sled into the carriages", ["carriage_bolts"]),
    ("LA36 top bracket on the extension of the X slide", ["act_top_bracket"]),
    ("Linak LA36 24 V 1700 N, stroke 400, between the rail beams", ["act_body", "act_pin_top"]),
    ("Inner tube with rod eye, pin D12: the LA36 now holds the sled", ["act_rod", "act_pin_eye"]),
]
FINAL_STEPS = [
    ("Spindle bracket welded to the sled: lower, side, bearing and top plates",
     ["sb_lower", "sb_side_left", "sb_side_right", "sb_bearing_plate", "sb_top"]),
    ("2 x UCP 206 pillow blocks, M14", ["bearing_lower", "bearing_upper", "bearing_bolts"]),
    ("Spindle shaft D30 with welded flange", ["spindle_shaft", "spindle_flange"]),
    ("Jaw coupling, motor plate and gussets, 800 W gearmotor",
     ["jaw_coupling", "motor_plate", "motor_gussets", "spindle_motor_shaft", "spindle_motor"]),
    ("Cutter D180: flange, core tube, 2 Hardox crosses, teeth, centre point",
     ["cutter_flange", "cutter_core_tube", "cutter_cross_upper", "cutter_cross_lower", "cutter_teeth",
      "cutter_centre_point"]),
    ("Can D219 on 2 rods in PE bushes, ground sensor",
     ["pot_bushes", "pot_rods", "pot_set_rings", "shaft_seal", "pot_lid", "pot_shell", "pot_sensor_bracket",
      "pot_sensor"]),
    ("Spiral cable from the X slide to the sled", ["cable_bracket_x", "cable_bracket_z", "spiral_cable"]),
]
FOCUS_NAMES = [n for _, names in FOCUS_STEPS for n in names]
Z_NAMES = set(FOCUS_NAMES) | {n for _, names in FINAL_STEPS for n in names}


# ---------------------------------------------------------------------
# Timeline: list of frame states
# ---------------------------------------------------------------------
def ease(t):
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


CAM_FULL = {"target": (0.0, -1700.0, 900.0), "dist": 7000.0}
CAM_BUILT = {"target": (0.0, -830.0, 1000.0), "dist": 3200.0}
CAM_FOCUS = {"target": (-100.0, -1400.0, 850.0), "dist": 3600.0}
CAM_STROKE = {"target": (0.0, -830.0, 720.0), "dist": 2500.0}
AZ_FOCUS, EL_FOCUS = 196.0, 14.0       # from the left, a little behind: slide | beams | rails | carriages | sled
AZ_STROKE, EL_STROKE = 203.0, 11.0


def _cam(a, b, s):
    return {"target": tuple(a["target"][k] + (b["target"][k] - a["target"][k]) * s for k in range(3)),
            "dist": a["dist"] + (b["dist"] - a["dist"]) * s}


def prepare(fps=FPS):
    """Frames: dict(f = explode fraction per object, moving set, ghost 0..1, focus set, x, z, angle, ground, cam,
    label)."""
    names = list(EXPLODE)
    kf = FPS / float(fps)             # camera turn and spin per frame are tuned at FPS: same speed per second
    order = [n for _, ns in STEPS + FOCUS_STEPS + FINAL_STEPS for n in ns]
    frames = []
    state = {"f": {n: 0.0 for n in names}, "moving": [], "ghost": 0.0, "solid": "focus", "x": 0.0,
             "z": P.drive_z, "angle": 0.0, "ground": False, "az": 215.0, "el": 22.0, "cam": CAM_BUILT,
             "follow": 0.0, "label": "Dockweed drill v10 - assembled"}

    def emit(**kw):
        st = dict(state)
        st["f"] = dict(state["f"])
        st.update(kw)
        frames.append(st)

    def frames_for(seconds):
        return max(1, int(round(seconds * fps)))

    # 1. assembled, slow turn
    for i in range(frames_for(1.5)):
        state["az"] += 0.6 * kf
        emit()
    # 2. explode (reverse assembly order, staggered)
    n = frames_for(3.5)
    rev = list(reversed(order))
    for i in range(n):
        t = (i + 1) / n
        for k, name in enumerate(rev):
            start = 0.45 * k / len(rev)
            state["f"][name] = ease((t - start) / 0.55)
        state["cam"] = _cam(CAM_BUILT, CAM_FULL, ease(t))
        state["az"] -= 0.55 * kf
        state["label"] = "Taking it apart"
        emit()
    # 3. exploded, turn to the left side (the explosion is mostly along y)
    for i in range(frames_for(3.5)):
        state["az"] -= 0.95 * kf
        state["label"] = "Exploded: %d parts" % len(names)
        emit()
    # 4. assemble step by step: headstock, X axis, slide, camera
    for label, ns in STEPS:
        n = frames_for(0.85)
        for i in range(n):
            t = (i + 1) / n
            for name in ns:
                state["f"][name] = 1.0 - ease(t)
            state["az"] += 0.27 * kf
            emit(moving=list(ns), label=label)
        emit(label=label)
    # 5. focus on the linear guide: the rest ghosted, camera to the left rear
    n = frames_for(1.5)
    az0, el0 = state["az"], state["el"]
    for i in range(n):
        t = ease((i + 1) / n)
        state["ghost"] = t
        state["solid"] = "focus"
        state["cam"] = _cam(CAM_FULL, CAM_FOCUS, t)
        state["az"] = az0 + (AZ_FOCUS - az0) * t
        state["el"] = el0 + (EL_FOCUS - el0) * t
        emit(label="Z axis on linear guides (after the photos): rails fixed on the slide, carriages on the sled")
    for label, ns in FOCUS_STEPS:
        n = frames_for(1.4)
        for i in range(n):
            t = (i + 1) / n
            for name in ns:
                state["f"][name] = 1.0 - ease(t)
            emit(moving=list(ns), label=label)
        for i in range(frames_for(0.4)):
            emit(label=label)
    # 6. ghost off, spindle bracket, motor, cutter and can onto the sled
    n = frames_for(1.0)
    for i in range(n):
        state["ghost"] = 1.0 - ease((i + 1) / n)
        emit(label="The spindle drive of v8 goes onto the sled")
    for label, ns in FINAL_STEPS:
        n = frames_for(0.9)
        for i in range(n):
            t = (i + 1) / n
            for name in ns:
                state["f"][name] = 1.0 - ease(t)
            state["cam"] = _cam(CAM_FOCUS, CAM_BUILT, ease((FINAL_STEPS.index((label, ns)) + t) / len(FINAL_STEPS)))
            state["az"] -= 0.15 * kf
            emit(moving=list(ns), label=label)
        emit(label=label)
    # 7. stroke: X to +300 and back, Z from driving height to full depth and back, the frame ghosted
    n = frames_for(1.5)
    az0, el0 = state["az"], state["el"]
    for i in range(n):
        t = ease((i + 1) / n)
        state["ghost"] = t
        state["solid"] = "z"
        state["cam"] = _cam(CAM_BUILT, CAM_STROKE, t)
        state["az"] = az0 + (AZ_STROKE - az0) * t
        state["el"] = el0 + (EL_STROKE - el0) * t
        state["ground"] = True
        state["follow"] = t
        emit(label="Z sled rolls on 4 carriages; the X slide runs on the round tubes")
    for x0, x1, z0, z1, label, secs, spin in (
            (0.0, STROKE_X, P.drive_z, P.drive_z, "X slide to x +%d: the belt runs round the fixed pulleys" % STROKE_X,
             1.8, False),
            (STROKE_X, STROKE_X, P.drive_z, -P.depth_max,
             "LA36 extends: the sled rolls down %d mm, cutter %d mm into the soil" % (P.drive_z + P.depth_max,
                                                                                    P.depth_max), 3.2, True),
            (STROKE_X, STROKE_X, -P.depth_max, -P.depth_max, "Full depth: lower carriages near the rail end", 0.8,
             True),
            (STROKE_X, STROKE_X, -P.depth_max, P.drive_z, "LA36 retracts the sled to driving height", 3.0, False),
            (STROKE_X, 0.0, P.drive_z, P.drive_z, "X slide back to the middle", 1.8, False)):
        n = frames_for(secs)
        for i in range(n):
            s = ease((i + 1) / n)
            state["x"] = x0 + (x1 - x0) * s
            state["z"] = z0 + (z1 - z0) * s
            if spin:
                state["angle"] += 37.0 * kf
            emit(label=label)
    # 8. back to normal, final turn
    n = frames_for(2.5)
    for i in range(n):
        t = ease((i + 1) / n)
        state["ghost"] = 1.0 - t
        state["cam"] = _cam(CAM_STROKE, CAM_BUILT, t)
        state["el"] = EL_STROKE + (22.0 - EL_STROKE) * t
        state["az"] += 1.0 * kf
        state["follow"] = 1.0 - t
        state["ground"] = t < 0.5
        emit(label="Dockweed drill v10 - complete")
    for i in range(frames_for(1.0)):
        state["az"] += 0.6 * kf
        emit(label="Dockweed drill v10 - complete")
    return frames


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
_base = {}
_color = {}


def build():
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Dockweed drill v10 - exploded animation"
    doc.Comment = "Generated by explode_dwd10.py (no need to save). Implement from build_dwd10."
    build_dwd10.build_into(doc, None, 0.0, P.drive_z)
    ground = doc.addObject("Part::Feature", "xp_ground")
    ground.Shape = Part.makeBox(1800.0, 1400.0, 60.0, V(-700.0, -1640.0, -60.0))
    ground.ViewObject.ShapeColor = GROUND
    ground.ViewObject.Transparency = 55
    ground.ViewObject.Visibility = False
    doc.recompute()
    record(doc)
    missing = [o.Name for o in build_dwd10.implement_objects(doc) if o.Name not in EXPLODE]
    extra = [n for n in EXPLODE if doc.getObject(n) is None]
    if missing or extra:
        raise ValueError("explode offsets: missing %s, unknown %s" % (missing, extra))
    return doc


def record(doc):
    _base.clear()
    _color.clear()
    for o in build_dwd10.implement_objects(doc):
        _base[o.Name] = App.Placement(o.Placement)
        _color[o.Name] = tuple(o.ViewObject.ShapeColor[:3])


def _document():
    """The animation document, rebuilt when the base placements are lost (e.g. after a module reload)."""
    if DOC_NAME not in App.listDocuments() or not _base:
        return build()
    return App.getDocument(DOC_NAME)


def apply_frame(doc, f):
    build_dwd10.set_pose(doc, f["x"], f["z"], angle=f["angle"])
    moving = set(f["moving"])
    solid = set(FOCUS_NAMES) if f["solid"] == "focus" else Z_NAMES
    for name, (dx, dy, dz) in EXPLODE.items():
        o = doc.getObject(name)
        s = f["f"][name]
        o.Placement = App.Placement(V(dx * s, dy * s, dz * s), App.Rotation()).multiply(_base[name])
        vo = o.ViewObject
        vo.ShapeColor = HIGHLIGHT if name in moving else _color[name]
        ghost = 0 if name in solid or name in moving else int(round(GHOST * f["ghost"]))
        if name in ("pot_shell", "pot_lid") and name not in moving:
            ghost = max(ghost, 60)                                # cutter visible inside the can
        if vo.Transparency != ghost:
            vo.Transparency = ghost
    doc.getObject("xp_ground").ViewObject.Visibility = f["ground"]


def track_camera(f, fov=38.0):
    import FreeCADGui as Gui
    from pivy import coin
    tx, ty, tz = f["cam"]["target"]
    tx += f["x"] * f["follow"]
    d = f["cam"]["dist"]
    az, el = math.radians(f["az"]), math.radians(f["el"])
    eye = (tx + d * math.cos(el) * math.cos(az), ty + d * math.cos(el) * math.sin(az), tz + d * math.sin(el))
    cam = Gui.getDocument(DOC_NAME).ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(*eye))
    cam.pointAt(coin.SbVec3f(tx, ty, tz), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


def meta(f):
    return {"label": f["label"], "x": round(f["x"]), "z": round(f["z"])}


def summary(frames=None):
    frames = frames or prepare()
    return {"frames": len(frames), "duration_s": round(len(frames) / FPS, 1), "parts": len(EXPLODE),
            "steps": len(STEPS) + len(FOCUS_STEPS) + len(FINAL_STEPS),
            "x_range": (round(min(f["x"] for f in frames)), round(max(f["x"] for f in frames))),
            "z_range": (round(min(f["z"] for f in frames)), round(max(f["z"] for f in frames)))}


def render_frames(folder, first=0, count=None, size=(800, 600), fps=FPS):
    import FreeCADGui as Gui
    doc = _document()
    frames = prepare(fps)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.getDocument(DOC_NAME).ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i])
        track_camera(frames[i])
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, size=(800, 600), fps=FPS):
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 40, size, fps)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=FPS, loop=False):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer
    stop()
    doc = _document()
    frames = prepare()
    Gui.getDocument(DOC_NAME).ActiveView.setCameraType("Perspective")
    _play.update({"index": 0})

    def step():
        try:
            if _play["index"] >= len(frames):
                if loop:
                    _play["index"] = 0
                else:
                    stop()
                    return
            i = _play["index"]
            _play["index"] += 1
            apply_frame(doc, frames[i])
            track_camera(frames[i])
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))
