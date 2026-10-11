"""Animation: the Bruut OpenAgbot tops a patch of thistles, ragwort and dock with the weed picker. The robot drives
forward (+y) at up to 0.5 m/s and slows down when the motors reach 90 % of their power; the two rotors cut every
weed in the 990 mm strip at the set height and sweep the chopped material out of the centre discharge into one
windrow between the wheels. Halfway the actuator raises the deck from
a 150 to a 250 mm cut height while driving.

Builds a separate document (the robot files in "agbot design" are not changed): robot from build_agbot, weed picker
from build_wpk, ground and the weeds (wpk_weeds). Per frame: robot (position, wheel rotation), cut height (linkage,
deck, actuator via build_wpk.set_height), rotors, weeds (standing / stub) and the chips in the windrow. The power comes
from wpk_calc (windage, idle) and the cut mass (e_chop), so the animation and the report give the same numbers.

Use in FreeCAD:
    import animate_wpk
    animate_wpk.build()                              # build the document
    animate_wpk.play()                               # live, animate_wpk.stop()
    animate_wpk.summary()                            # key figures of the run
    animate_wpk.render_all(r"C:\\temp\\wpk_frames")
    import make_gif_wpk; make_gif_wpk.main(r"C:\\temp\\wpk_frames", r"previews\\animation_topping_windrow.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import wpk_params as P
import wpk_calc as C
import wpk_kin as K
import wpk_parts as G
import wpk_weeds as W
import build_wpk

DOC_NAME = "WPK_on_robot_animation"

# ---------------------------------------------------------------------
# Drive plan
# ---------------------------------------------------------------------
FPS = 10
SPEED = P.drive_speed                   # m/s
Y_START = 0.0                           # robot origin
DURATION = 13.0                         # s
V_MIN = 0.15                            # m/s: the robot slows down when the motors reach LOAD of their power
LOAD = 0.9
ACCEL = (0.25, 1.0)                     # m/s2 speeding up, slowing down
CUT_START = 150.0                       # mm, first half
CUT_END = 250.0                         # mm, raised while driving
T_RAISE = 5.5                           # s, actuator starts
SPIN_DEG = 37.0                         # rotor turn per frame in the pictures (the real 2400 rpm would alias)
FEED_MM = 600.0                         # mm: a cut plant is pressed under the deck and chopped over this travel
DENSITY = 2.5                           # plants per m2 in the patch
PATCH_Y = (1600.0, 5300.0)              # world y of the weed patch
CHIP_DELAY = 0.25                       # s: from the cut to the chips on the ground
COLOR = {"ground": (0.40, 0.55, 0.28)}

_timer = None
_play = {}


def cut_at(t):
    """Cut height (actuator setting) at time t: the actuator moves at act_speed (in its own length)."""
    a0, a1 = K.act_setting(CUT_START), K.act_setting(CUT_END)
    if t <= T_RAISE:
        return CUT_START
    a = a0 + math.copysign(min(abs(a1 - a0), P.act_speed * (t - T_RAISE)), a1 - a0)
    lo, hi = P.cut_range
    for _ in range(40):                                     # invert act_setting (shorter actuator = higher deck)
        mid = 0.5 * (lo + hi)
        if K.act_setting(mid) > a:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def prepare(fps=FPS):
    """Drive plan, cutting and the windrow (wpk_weeds). A cut plant is pressed under the deck and chopped while the
    deck moves FEED_MM over it, so its power is proportional to the driving speed; the robot follows the motor load
    (target LOAD of the available power) with limited acceleration. Returns the frames (dicts) and the field."""
    field = W.Field(y=PATCH_Y, density=DENSITY)
    p_base = 2 * (C.windage() + P.idle_W)
    p_limit = 2 * LOAD * C.motor_available()
    feeding = []                                            # [kg left, kg total] per cut plant
    frames = []
    sub = 5
    dt = 1.0 / fps / sub
    n = int(round(DURATION * fps * sub))
    y, v, chop = Y_START, SPEED, 0.0
    for k in range(n + 1):
        t = k * dt
        v_ok = SPEED if chop <= 1.0 else v * (p_limit - p_base) / chop      # speed for the limit at this load
        v_ok = max(V_MIN, min(SPEED, v_ok))
        v = min(v_ok, v + ACCEL[0] * dt) if v_ok > v else max(v_ok, v - ACCEL[1] * dt)
        if k:
            y += v * 1000.0 * dt
        cut = cut_at(t)
        yc = y + P.rotor_y(cut)
        rotors = [(P.rotor_x, yc, cut), (-P.rotor_x, yc, cut + P.rotor_dz)]
        y_dis = yc - P.hood_r - P.swath_len
        kg = field.cut_by(rotors, cut, t, y_dis)
        if kg > 0:
            feeding.append([kg, kg])
        done = 0.0
        for item in feeding:
            dm = min(item[0], item[1] * v * 1000.0 * dt / FEED_MM)
            item[0] -= dm
            done += dm
        feeding = [item for item in feeding if item[0] > 1e-6]
        chop = done * P.e_chop / dt
        if k % sub:
            continue
        cut_now = [p for p in field.plants if p["cut"] is not None]
        kg_cut = sum(p["cut"]["kg"] for p in cut_now)
        frames.append({"t": t, "y": y, "v": v, "cut": cut, "P_shaft": p_base + chop,
                       "P_el": (p_base + chop) / P.eta_motor, "kg_cut": kg_cut,
                       "kg_windrow": kg_cut * P.windrow_share, "n_cut": len(cut_now),
                       "n_strip": sum(1 for p in field.plants if abs(p["x"]) <= P.CUT_W / 2.0 - 20.0
                                      and p["y"] <= yc + P.blade_r[1]),
                       "spin_robot": (y - Y_START) / (P.robot_tire_d / 2.0),
                       "raising": abs(cut - CUT_START) > 0.5 and abs(cut - CUT_END) > 0.5,
                       "plants": len(field.plants)})
    return frames, field



# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
WEED_OBJECTS = ("stem", "leaves", "thistle", "ragwort", "dock", "chips")


def build():
    if build_wpk.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_wpk.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Weed picker on robot - animation"
    doc.Comment = "Generated by animate_wpk.py. Robot from agbot design, weed picker from build_wpk."
    robot = build_wpk.build_robot(doc)
    build_wpk.build_into(doc, robot)
    g = doc.addObject("Part::Feature", "anim_ground")
    g.Shape = Part.makeBox(9000.0, 16000.0, 40.0, V(-4500.0, -4000.0, -40.0))
    g.ViewObject.ShapeColor = COLOR["ground"]
    for key in WEED_OBJECTS:
        o = doc.addObject("Part::Feature", "anim_" + key)
        o.ViewObject.ShapeColor = build_wpk.COLOR[key]
    for o in doc.Objects:
        if o.Name.startswith("anim_"):
            o.ViewObject.DisplayMode = "Shaded"                 # no black edges on weeds and ground
    doc.recompute()
    return doc


_SHAPES = {}


def plant_shapes(field, i):
    """(standing, cut) shape dicts of plant i (cached)."""
    key = (id(field), i)
    if key not in _SHAPES:
        p = field.plants[i]
        cut = G.weed_shapes(p, p["cut"]["z"]) if p["cut"] is not None else None
        _SHAPES[key] = (G.weed_shapes(p), cut)
    return _SHAPES[key]


_CHIPS = {}


def chip_shapes(field):
    key = id(field)
    if key not in _CHIPS:
        _CHIPS.clear()
        _CHIPS[key] = [G.chip_shape(c) for c in field.chips]
    return _CHIPS[key]


def apply_frame(doc, f, field, index):
    doc.getObject("Robot").Placement = App.Placement(V(0.0, f["y"], 0.0), App.Rotation())
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin_robot"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    build_wpk.set_height(doc, f["cut"], 0.0, (SPIN_DEG * index, -SPIN_DEG * index))
    groups = {k: [] for k in WEED_OBJECTS}
    for i, p in enumerate(field.plants):
        standing, cut = plant_shapes(field, i)
        s = cut if (p["cut"] is not None and p["cut"]["t"] <= f["t"]) else standing
        groups["stem"] += s["stem"]
        groups["leaves"] += s["leaves"]
        groups[p["kind"]] += s["crown"]
    chips = chip_shapes(field)
    groups["chips"] = [s for s, c in zip(chips, field.chips) if c["t"] + CHIP_DELAY <= f["t"]]
    for key, shapes in groups.items():
        doc.getObject("anim_" + key).Shape = Part.makeCompound(shapes or [Part.Vertex(0, 0, -50)])


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_A = ((-1500.0, 2300.0, 2700.0), (100.0, 950.0, 200.0))      # front left: deck cutting, windrow under the robot
CAM_B = ((-1300.0, -2300.0, 2900.0), (0.0, -500.0, 0.0))      # rear left at the end: the windrow behind the robot


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def track_camera(f, frames, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    t_end = frames[-1]["t"]
    s = smooth((f["t"] - (t_end - 3.0)) / 2.5)
    eye = [CAM_A[0][i] + (CAM_B[0][i] - CAM_A[0][i]) * s for i in range(3)]
    tgt = [CAM_A[1][i] + (CAM_B[1][i] - CAM_A[1][i]) * s for i in range(3)]
    target = (tgt[0], f["y"] + tgt[1], tgt[2])
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(target[0] + eye[0], target[1] + eye[1], target[2] + eye[2]))
    cam.pointAt(coin.SbVec3f(*target), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


def meta(f):
    return {"t": round(f["t"], 3), "v": round(f["v"] * 1000.0, 1), "dist": round(f["y"] - Y_START, 1),
            "cut": round(f["cut"], 1), "P_el": round(f["P_el"]), "P_shaft": round(f["P_shaft"]), "kg_cut": round(f["kg_cut"], 3),
            "kg_windrow": round(f["kg_windrow"], 3), "n_cut": f["n_cut"], "n_strip": f["n_strip"],
            "raising": f["raising"], "rpm": P.rpm, "P_limit": round(2 * LOAD * C.motor_available() / P.eta_motor)}


def summary(frames=None):
    if frames is None:
        frames, field = prepare()
    else:
        field = None
    last = frames[-1]
    out = {"frames": len(frames), "duration_s": round(last["t"], 2), "plants": last["plants"],
           "cut": last["n_cut"], "in_strip": last["n_strip"], "kg_cut": round(last["kg_cut"], 2),
           "kg_windrow": round(last["kg_windrow"], 2), "P_el_W": (round(min(f["P_el"] for f in frames)),
                                                               round(max(f["P_el"] for f in frames))),
           "cut_h": (round(frames[0]["cut"]), round(last["cut"]))}
    if field is not None:
        out["chips"] = len(field.chips)
        out["outside_strip_standing"] = sum(1 for p in field.plants if p["cut"] is None)
    return out


def render_frames(folder, first=0, count=None, fps=FPS, size=(720, 480), frames=None, field=None):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    if frames is None:
        frames, field = prepare(fps)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i], field, i)
        track_camera(frames[i], frames)
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, fps=FPS, size=(720, 480)):
    build()
    frames, field = prepare(fps)
    first, total = 0, len(frames)
    while first < total:
        first, total = render_frames(folder, first, 25, fps, size, frames, field)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=FPS, loop=False, follow=True):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer
    stop()
    doc = App.getDocument(DOC_NAME)
    frames, field = prepare(fps)
    Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
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
            apply_frame(doc, frames[i], field, i)
            if follow:
                track_camera(frames[i], frames)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))


def check_fit(doc=None, cuts=(CUT_START, 200.0, CUT_END)):
    """Overlap between the real robot model and the weed picker in the animation document at the cut heights of the
    run (robot at the origin)."""
    doc = doc or App.getDocument(DOC_NAME)
    doc.getObject("Robot").Placement = App.Placement()
    out = {}
    for c in cuts:
        build_wpk.set_height(doc, c)
        doc.recompute()
        out["cut_%g" % c] = build_wpk.check_interference(doc)
    build_wpk.set_height(doc, P.cut_h)
    return out