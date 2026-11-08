"""Exploded-view animation of the dockweed drill v7: take it apart, then build it up again piece by piece, with the
focus on the Linak LA36 (Z actuator) at the end, including a stroke from driving height to full depth and back.

Builds a separate document (DWD7_exploded_animation) with the implement only (from build_dwd7.build_into) and a
ground plate that only shows during the stroke. Every Part::Feature gets an explode offset (EXPLODE, in the frame
of its parent; the parents only translate). Nothing is changed in the model files.

Use in FreeCAD:
    import explode_dwd7
    explode_dwd7.build()
    explode_dwd7.play()                       # live, explode_dwd7.stop()
    explode_dwd7.summary()
    explode_dwd7.render_all(r"C:\\temp\\dwd7_explode")
    import make_gif_dwd7; make_gif_dwd7.main_explode(r"C:\\temp\\dwd7_explode", r"previews\\exploded_assembly.gif")
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd7_params as P
import build_dwd7

DOC_NAME = "DWD7_exploded_animation"
FPS = 12
HIGHLIGHT = (1.0, 0.82, 0.10)          # colour of a part while it moves into place
GHOST = 88                             # transparency of the other parts during the actuator focus
GROUND = (0.45, 0.62, 0.31)

_timer = None
_play = {}

# ---------------------------------------------------------------------
# Explode offsets (mm, x right, y forward to the robot, z up)
# ---------------------------------------------------------------------
C = (0.0, -1250.0, 0.0)               # Z carriage as a whole: backwards, out of the bushes
S = (0.0, -1600.0, 0.0)               # spindle bracket and everything on it: further back
A = (-650.0, -250.0, 0.0)             # actuator: sideways, to the camera side


def _add(a, b):
    return tuple(a[k] + b[k] for k in range(3))


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
    # fixed Z frame: layers backwards
    "z_beam_bolts": (0, 380, 0),
    "z_beam_lower": (0, -170, -90), "z_beam_upper": (0, -170, 90),
    "mount_plate_bolts": (0, -300, 0), "mount_plate": (0, -430, 0),
    "z_houses": (0, -650, 0), "z_house_bolts": (0, -830, 0), "z_grease_nipples": (0, -830, 330),
    "z_bushes": (0, -650, 520), "z_wipers": (0, -650, -540),
    "cable_bracket_fixed": (380, -420, 0),
    # Z carriage
    "z_guide_tube_left": _add(C, (-230, 0, 300)), "z_guide_tube_right": _add(C, (230, 0, 300)),
    "z_tube_cap": _add(C, (-230, 0, 650)),
    "z_yoke": _add(C, (0, 0, -120)), "z_clamp_plate": _add(C, (0, 0, 0)),
    "cable_bracket_z": _add(C, (300, 0, 700)),
    "spiral_cable": (420, -800, 0),
    # spindle bracket
    "sb_back": _add(S, (0, 180, 0)), "sb_bearing_plate": _add(S, (0, 0, 0)),
    "sb_side_left": _add(S, (-170, 0, 0)), "sb_side_right": _add(S, (170, 0, 0)),
    "sb_lower": _add(S, (0, 0, -230)), "sb_top": _add(S, (0, 0, 260)),
    "bearing_lower": _add(S, (0, -260, -90)), "bearing_upper": _add(S, (0, -260, 90)),
    "bearing_bolts": _add(S, (0, 330, 0)),
    "spindle_shaft": _add(S, (0, -560, 0)), "spindle_flange": _add(S, (0, -560, -110)),
    "jaw_coupling": _add(S, (0, -560, 380)), "spindle_motor_shaft": _add(S, (0, -560, 520)),
    "spindle_motor": _add(S, (0, -560, 760)),
    "motor_plate": _add(S, (300, -560, 520)), "motor_gussets": _add(S, (190, -560, 420)),
    "pot_bushes": _add(S, (0, 0, -380)),
    "pot_sensor": _add(S, (330, 0, -60)), "pot_sensor_bracket": _add(S, (280, 0, -60)),
    # cutter (Tool, below the spindle)
    "cutter_flange": _add(S, (0, -560, -200)), "cutter_core_tube": _add(S, (0, -560, -265)),
    "cutter_cross_upper": _add(S, (0, -560, -325)), "cutter_cross_lower": _add(S, (0, -560, -385)),
    "cutter_teeth": _add(S, (0, -560, -450)), "cutter_centre_point": _add(S, (0, -560, -540)),
    # can
    "pot_set_rings": _add(S, (0, -1000, 260)), "pot_rods": _add(S, (0, -1000, 120)),
    "shaft_seal": _add(S, (0, -1000, -40)), "pot_lid": _add(S, (0, -1000, -110)),
    "pot_shell": _add(S, (0, -1000, -330)),
    # camera: up
    "camera_mast": (0, 0, 250), "camera_arm": (0, -250, 420),
    "camera_crossbar": (0, -450, 560), "led_bar": (0, -450, 700), "camera": (0, -450, 380),
    # actuator (LA36): to the camera side, opened up along its axis
    "act_top_bracket": _add(A, (0, 0, 430)), "act_pin_top": _add(A, (-200, 0, 430)),
    "act_body": _add(A, (0, 0, 180)),
    "act_rod": _add(A, (0, 0, -270)),
    "act_eye_bracket": _add(A, (0, 0, -480)), "act_pin_eye": _add(A, (-200, 0, -480)),
}

# assembly order: (label, objects). The last block (actuator) is the focus.
STEPS = [
    ("Headstock: 2 uprights 40x40x3 with top plate, back plate, gusset and cap, cross tube",
     ["hs_top_left", "hs_top_right", "hs_back_left", "hs_back_right", "gusset_left", "gusset_right",
      "upright_cap_left", "upright_cap_right", "hs_cross"]),
    ("Clamp plates and M10 bolts onto the robot's rear beam", ["hs_clamp_left", "hs_clamp_right",
                                                              "hs_bolts_left", "hs_bolts_right"]),
    ("Electrics: mounting plate, IP65 box, cable glands", ["ebox_plate", "ebox", "ebox_glands"]),
    ("2 cross beams 40x40x3 between the uprights, 4 x M12", ["z_beam_lower", "z_beam_upper", "z_beam_bolts"]),
    ("Z mount plate 10 mm, 4 x M10 (future X slide interface)", ["mount_plate", "mount_plate_bolts"]),
    ("4 bush housings D50, 16 x M8, grease nipples", ["z_houses", "z_house_bolts", "z_grease_nipples"]),
    ("Plain bushes (iglidur) and rubber wipers", ["z_bushes", "z_wipers"]),
    ("Z guide: 2 precision tubes D50x4", ["z_guide_tube_left", "z_guide_tube_right", "z_tube_cap"]),
    ("Lower yoke and clamp plate, welded to the tubes", ["z_yoke", "z_clamp_plate"]),
    ("Spindle bracket: back, lower, side, bearing and top plates",
     ["sb_back", "sb_lower", "sb_side_left", "sb_side_right", "sb_bearing_plate", "sb_top"]),
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
    ("Camera mast, arm, crossbar, camera and LED bar",
     ["camera_mast", "camera_arm", "camera_crossbar", "camera", "led_bar"]),
    ("Spiral cable and its brackets", ["cable_bracket_fixed", "cable_bracket_z", "spiral_cable"]),
]
ACT_STEPS = [
    ("LA36 top bracket on the mount plate", ["act_top_bracket"]),
    ("Linak LA36 24 V 1700 N, stroke 400: housing and outer tube", ["act_body"]),
    ("Top pin D12: the LA36 hangs from the fixed frame", ["act_pin_top"]),
    ("Rod-eye bracket, welded on the clamp plate of the Z carriage", ["act_eye_bracket"]),
    ("Inner tube with rod eye slides out of the housing", ["act_rod"]),
    ("Rod-eye pin D12: the LA36 now carries the whole Z carriage (45 kg)", ["act_pin_eye"]),
]
ACT_NAMES = [n for _, names in ACT_STEPS for n in names]


# ---------------------------------------------------------------------
# Timeline: list of frame states
# ---------------------------------------------------------------------
def ease(t):
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


CAM_FULL = {"target": (0.0, -1500.0, 900.0), "dist": 5600.0}
CAM_BUILT = {"target": (0.0, -830.0, 1050.0), "dist": 3000.0}
CAM_ACT = {"target": (-330.0, -800.0, 1000.0), "dist": 2700.0}


def _cam(a, b, s):
    return {"target": tuple(a["target"][k] + (b["target"][k] - a["target"][k]) * s for k in range(3)),
            "dist": a["dist"] + (b["dist"] - a["dist"]) * s}


def prepare(fps=FPS):
    """Frames: dict(f = explode fraction per object, moving set, ghost 0..1, z, angle, ground, cam, label)."""
    names = list(EXPLODE)
    kf = FPS / float(fps)             # camera turn and spin per frame are tuned at FPS: same speed per second
    order = [n for _, ns in STEPS for n in ns] + ACT_NAMES
    frames = []
    state = {"f": {n: 0.0 for n in names}, "moving": [], "ghost": 0.0, "z": P.drive_z, "angle": 0.0,
             "ground": False, "az": 215.0, "el": 22.0, "cam": CAM_BUILT, "label": "Dockweed drill v7 - assembled",
             "focus": False}

    def emit(**kw):
        st = dict(state)
        st["f"] = dict(state["f"])
        st.update(kw)
        frames.append(st)

    def frames_for(seconds):
        return max(1, int(round(seconds * fps)))

    # 1. assembled, slow turn
    n = frames_for(1.5)
    for i in range(n):
        state["az"] += 0.6 * kf
        emit()
    # 2. explode (actuator first, the rest staggered in reverse assembly order)
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
    n = frames_for(3.5)
    for i in range(n):
        state["az"] -= 0.95 * kf
        state["label"] = "Exploded: %d parts" % len(names)
        emit()
    # 4. assemble step by step
    for label, ns in STEPS:
        n = frames_for(0.85)
        for i in range(n):
            t = (i + 1) / n
            for name in ns:
                state["f"][name] = 1.0 - ease(t)
            state["az"] += 0.27 * kf          # turn back to the left rear, where the actuator lies
            emit(moving=list(ns), label=label)
        emit(label=label)
    # 5. actuator focus: others ghosted, camera closer
    n = frames_for(1.5)
    for i in range(n):
        t = ease((i + 1) / n)
        state["ghost"] = t
        state["cam"] = _cam(CAM_FULL, CAM_ACT, t)
        state["az"] += 2.7 * kf          # to the rear left: the LA36 parts come in from the side
        state["el"] = 22.0 - 8.0 * t
        state["focus"] = True
        emit(label="Z drive: Linak LA36 between the two guide tubes")
    for label, ns in ACT_STEPS:
        n = frames_for(1.4)
        for i in range(n):
            t = (i + 1) / n
            for name in ns:
                state["f"][name] = 1.0 - ease(t)
            emit(moving=list(ns), label=label)
        for i in range(frames_for(0.4)):
            emit(label=label)
    # 6. stroke: driving height -> full depth -> back, cutter turning
    state["ground"] = True
    for z0, z1, label, secs, spin in ((P.drive_z, -P.depth_max,
                                       "LA36 extends: Z carriage down %d mm, cutter %d mm into the soil" % (
                                           P.drive_z + P.depth_max, P.depth_max), 3.0, True),
                                      (-P.depth_max, -P.depth_max, "Full depth", 0.6, True),
                                      (-P.depth_max, P.drive_z, "LA36 retracts to driving height", 3.0, False)):
        n = frames_for(secs)
        for i in range(n):
            state["z"] = z0 + (z1 - z0) * ease((i + 1) / n)
            if spin:
                state["angle"] += 37.0 * kf
            emit(label=label)
    # 7. back to normal, final turn
    n = frames_for(2.5)
    for i in range(n):
        t = ease((i + 1) / n)
        state["ghost"] = 1.0 - t
        state["cam"] = _cam(CAM_ACT, CAM_BUILT, t)
        state["el"] = 14.0 + 8.0 * t
        state["az"] -= 1.0 * kf
        state["ground"] = t < 0.5
        state["focus"] = t < 0.5
        emit(label="Dockweed drill v7 - Z part complete")
    for i in range(frames_for(1.0)):
        state["az"] += 0.6 * kf
        emit(label="Dockweed drill v7 - Z part complete")
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
    doc.Label = "Dockweed drill v7 - exploded animation"
    doc.Comment = "Generated by explode_dwd7.py (no need to save). Implement from build_dwd7."
    build_dwd7.build_into(doc, None, P.drive_z)
    ground = doc.addObject("Part::Feature", "xp_ground")
    ground.Shape = Part.makeBox(1400.0, 1400.0, 60.0, V(-700.0, -1570.0, -60.0))
    ground.ViewObject.ShapeColor = GROUND
    ground.ViewObject.Transparency = 55
    ground.ViewObject.Visibility = False
    doc.recompute()
    record(doc)
    missing = [n for n in build_dwd7.implement_objects(doc) if n.Name not in EXPLODE]
    if missing:
        raise ValueError("no explode offset for %s" % [o.Name for o in missing])
    return doc


def record(doc):
    _base.clear()
    _color.clear()
    for o in build_dwd7.implement_objects(doc):
        _base[o.Name] = App.Placement(o.Placement)
        _color[o.Name] = tuple(o.ViewObject.ShapeColor[:3])


def _document():
    """The animation document, rebuilt when the base placements are lost (e.g. after a module reload)."""
    if DOC_NAME not in App.listDocuments() or not _base:
        return build()
    return App.getDocument(DOC_NAME)


def apply_frame(doc, f):
    build_dwd7.set_pose(doc, f["z"], angle=f["angle"])
    cable = doc.getObject("spiral_cable")
    _base["spiral_cable"] = App.Placement(cable.Placement)       # set_pose makes a new cable shape
    moving = set(f["moving"])
    for name, (dx, dy, dz) in EXPLODE.items():
        o = doc.getObject(name)
        s = f["f"][name]
        o.Placement = App.Placement(V(dx * s, dy * s, dz * s), App.Rotation()).multiply(_base[name])
        vo = o.ViewObject
        vo.ShapeColor = HIGHLIGHT if name in moving else _color[name]
        ghost = 0 if name in ACT_NAMES or name in moving else int(round(GHOST * f["ghost"]))
        if name in ("pot_shell", "pot_lid") and name not in moving:
            ghost = max(ghost, 60)                                # cutter visible inside the can
        if vo.Transparency != ghost:
            vo.Transparency = ghost
    doc.getObject("xp_ground").ViewObject.Visibility = f["ground"]


def track_camera(f, fov=38.0):
    import FreeCADGui as Gui
    from pivy import coin
    tx, ty, tz = f["cam"]["target"]
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
    return {"label": f["label"], "focus": f["focus"], "z": round(f["z"])}


def summary(frames=None):
    frames = frames or prepare()
    return {"frames": len(frames), "duration_s": round(len(frames) / FPS, 1), "parts": len(EXPLODE),
            "steps": len(STEPS) + len(ACT_STEPS), "z_range": (round(min(f["z"] for f in frames)),
                                                             round(max(f["z"] for f in frames)))}


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
