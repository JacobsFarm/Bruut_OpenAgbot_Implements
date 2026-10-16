"""Animation: the Bruut OpenAgbot mows a strip of grass 3.25 m wide with the triple sickle bar mower, stops at the
headland and puts the mower in the transport position (front bar lifted, wings folded up).

Builds a separate document (the robot files in "agbot design" are not changed): robot from build_agbot, mower from
build_sbm, ground and the grass (sbm_grass). Per frame: robot (position, wheel rotation), knives (crank angle), front
bar (linkage, actuator via build_sbm.set_front), wings (fold, actuators via build_sbm.set_wing) and the grass
(standing / cut). The power comes from sbm_calc, so the animation and the report give the same numbers.

Use in FreeCAD:
    import animate_sbm
    animate_sbm.build()                              # build the document
    animate_sbm.play()                               # live, animate_sbm.stop()
    animate_sbm.summary()                            # key figures of the run
    animate_sbm.render_all(r"C:\\temp\\sbm_frames")
    import make_gif_sbm; make_gif_sbm.main(r"C:\\temp\\sbm_frames", r"previews\\animation_mow_fold.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import sbm_params as P
import sbm_calc as C
import sbm_grass as W
import build_sbm

DOC_NAME = "SBM_on_robot_animation"

# ---------------------------------------------------------------------
# Drive plan
# ---------------------------------------------------------------------
FPS = 8
SPEED = P.drive_speed                   # m/s
ACCEL = (0.5, 0.8)                      # m/s2 speeding up, slowing down
Y_STOP = 6000.0                         # robot origin stops here (headland)
T_HOLD = 0.6                            # s standing still before the actuators start
T_END_HOLD = 1.0                        # s at the end
FIELD_Y = (1300.0, 9800.0)              # grass
FIELD_X = (-2400.0, 2400.0)
CRANK_STEP = 0.75                       # rad per frame in the pictures (the real 600 rpm would alias)
DENSITY = 3.0                           # t DM/ha
COLOR = {"ground": (0.45, 0.36, 0.24)}

_timer = None
_play = {}


def drive():
    """Speed profile (t, y, v) at a fine step: accelerate, cruise, brake to stop at Y_STOP."""
    dt = 0.01
    t, y, v = 0.0, 0.0, 0.0
    out = [(t, y, v)]
    while True:
        brake = v * v / (2 * ACCEL[1]) * 1000.0
        if y + brake >= Y_STOP and v > 0:
            v = max(0.0, v - ACCEL[1] * dt)
        elif v < SPEED:
            v = min(SPEED, v + ACCEL[0] * dt)
        y += v * 1000.0 * dt
        t += dt
        out.append((t, y, v))
        if v <= 0.0 and y > 0.5 * Y_STOP:
            break
    return out


def front_lift_for(act):
    """Bar lift for a front actuator length (pin to pin): the float link slack is taken up first."""
    lo, hi = P.lift_work, P.lift_max + 20.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if P.act_length(mid) - P.float_len > act:
            lo = mid
        else:
            hi = mid
    return max(0.0, 0.5 * (lo + hi)), 0.5 * (lo + hi)


def wing_fold_for(act):
    """Fold angle for a wing actuator length: 0 while the anchor pin slides to the end of its slot."""
    if act >= P.wact_length(0.0):
        return 0.0
    lo, hi = 0.0, P.fold_max
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if P.wact_length(mid) > act:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def prepare(fps=FPS):
    """Frames (dicts): robot position and speed, crank angle, front lift, wing fold, power, cut area."""
    plan = drive()
    t_stop = plan[-1][0]
    a0 = P.act_length(P.lift_work) - P.float_len
    a1 = P.act_length(P.lift_max) - P.float_len
    w0, w1 = P.WACT_WORK, P.wact_length(P.fold_max)
    t_front = (a0 - a1) / P.act_speed
    t_wing = (w0 - w1) / P.wact_speed
    t_end = t_stop + T_HOLD + max(t_front, t_wing) + T_END_HOLD
    frames = []
    n = int(round(t_end * fps))
    k_plan = 0
    area = 0.0
    theta = build_sbm.G.THETA0
    last_y = 0.0
    for i in range(n + 1):
        t = i / float(fps)
        while k_plan + 1 < len(plan) and plan[k_plan + 1][0] <= t:
            k_plan += 1
        _, y, v = plan[k_plan] if t < t_stop else plan[-1]
        tf = max(0.0, t - t_stop - T_HOLD)
        act_f = max(a1, a0 - P.act_speed * tf)
        lift, lift_set = front_lift_for(act_f)
        act_w = max(w1, w0 - P.wact_speed * tf)
        fold = wing_fold_for(act_w)
        mowing = tf <= 0.0
        yk_f = y + P.y_front + 30.0
        yk_w = y + P.y_wing + 30.0
        in_f = mowing and FIELD_Y[0] < yk_f < FIELD_Y[1]
        in_w = mowing and FIELD_Y[0] < yk_w < FIELD_Y[1]
        p_front = C.bar_power(P.front_L, v, DENSITY if in_f else 0.0) if mowing else None
        p_wing = C.bar_power(P.wing_L, v, DENSITY if in_w else 0.0) if mowing else None
        if p_front is not None and not in_f:
            p_front = dict(p_front, el_W=P.idle_W_m * P.front_L / 1000.0 / P.eta_gear / P.eta_motor)
        if p_wing is not None and not in_w:
            p_wing = dict(p_wing, el_W=P.idle_W_m * P.wing_L / 1000.0 / P.eta_gear / P.eta_motor)
        pe_f = p_front["el_W"] if p_front else 0.0
        pe_w = p_wing["el_W"] if p_wing else 0.0
        dy = (y - last_y) / 1000.0
        area += dy * ((P.front_L / 1000.0 if in_f else 0.0) + (2 * P.wing_L / 1000.0 if in_w else 0.0))
        last_y = y
        if mowing and i:
            theta += CRANK_STEP
        state = "mowing" if mowing and (in_f or in_w) else ("driving in" if mowing and v > 0 else
                                                             ("stopped at the headland" if mowing else
                                                              ("lifting and folding" if fold < P.fold_max - 0.5
                                                               or lift < P.lift_max - 0.5 else "transport position")))
        frames.append({"t": t, "y": y, "v": v, "theta": theta, "lift": lift, "lift_set": lift_set,
                       "fold": fold, "act_w": act_w, "mowing": mowing, "in_f": in_f, "in_w": in_w,
                       "P_front": pe_f, "P_wing": pe_w, "P_el": pe_f + 2 * pe_w, "area": area, "state": state,
                       "y_cut_f": yk_f if mowing else None, "y_cut_w": yk_w if mowing else None,
                       "spin_robot": y / (P.robot_tire_d / 2.0)})
    # the knife lines only move forward: keep the furthest cut position after the stop
    yf = yw = -1e9
    for f in frames:
        yf = max(yf, f["y_cut_f"] if f["y_cut_f"] is not None else yf)
        yw = max(yw, f["y_cut_w"] if f["y_cut_w"] is not None else yw)
        f["y_cut_f"], f["y_cut_w"] = yf, yw
    return frames


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
GRASS_OBJECTS = ("grass", "stubble", "cut")
_FIELD = {}


def field():
    if "f" not in _FIELD:
        _FIELD["f"] = W.Field(y=FIELD_Y, x=FIELD_X)
    return _FIELD["f"]


def build():
    if build_sbm.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_sbm.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Triple sickle bar mower on robot - animation"
    doc.Comment = "Generated by animate_sbm.py. Robot from agbot design, mower from build_sbm."
    robot = build_sbm.build_robot(doc)
    build_sbm.build_into(doc, robot)
    g = doc.addObject("Part::Feature", "anim_ground")
    g.Shape = Part.makeBox(9000.0, 16000.0, 40.0, V(-4500.0, -4000.0, -40.0))
    g.ViewObject.ShapeColor = COLOR["ground"]
    for key in GRASS_OBJECTS:
        o = doc.addObject("Part::Feature", "anim_" + key)
        o.ViewObject.ShapeColor = build_sbm.COLOR[key]
    for o in doc.Objects:
        if o.Name.startswith("anim_"):
            o.ViewObject.DisplayMode = "Shaded"
    doc.recompute()
    return doc


def apply_frame(doc, f):
    doc.getObject("Robot").Placement = App.Placement(V(0.0, f["y"], 0.0), App.Rotation())
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin_robot"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    build_sbm.set_knives(doc, f["theta"])
    build_sbm.set_front(doc, f["lift"], f["lift_set"])
    for bar in ("R", "L"):
        build_sbm.set_wing(doc, bar, f["fold"], None if f["fold"] <= 0.0 and f["act_w"] >= P.WACT_WORK - 0.1
                           else f["act_w"])
    yf, yw = f["y_cut_f"], f["y_cut_w"]

    def standing(t):
        if t["region"] == "F":
            return t["y"] > yf
        if t["region"] == "W":
            return t["y"] > yw
        return True
    shapes = field().shapes(standing, (f["y"] - 2600.0, f["y"] + 4200.0))
    for key in GRASS_OBJECTS:
        doc.getObject("anim_" + key).Shape = Part.makeCompound(shapes[key] or [Part.Vertex(0, 0, -50)])


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_A = ((-2300.0, 2800.0, 3400.0), (250.0, 250.0, 100.0))      # front left, high: three bars cutting
CAM_B = ((-3300.0, -2600.0, 2100.0), (0.0, 100.0, 450.0))       # rear left: lifting and folding


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def track_camera(f, frames, fov=42.0):
    import FreeCADGui as Gui
    from pivy import coin
    t_stop = next((g["t"] for g in frames if not g["mowing"]), frames[-1]["t"])
    s = smooth((f["t"] - (t_stop - 2.0)) / 2.5)
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
    return {"t": round(f["t"], 3), "v": round(f["v"] * 1000.0, 1), "dist": round(f["y"], 1),
            "area": round(f["area"], 2), "P_el": round(f["P_el"]), "P_front": round(f["P_front"]),
            "P_wing": round(f["P_wing"]), "lift": round(f["lift"], 1), "fold": round(f["fold"], 1),
            "state": f["state"], "rpm": P.crank_rpm, "width": P.WIDTH,
            "P_limit": round(P.motor_P * 0.9 * (1 + 2) / P.eta_motor)}


def summary(frames=None):
    frames = frames or prepare()
    last = frames[-1]
    mow = [f for f in frames if f["mowing"]]
    return {"frames": len(frames), "duration_s": round(last["t"], 2), "distance_m": round(last["y"] / 1000.0, 2),
            "area_m2": round(last["area"], 1), "P_el_W": (round(min(f["P_el"] for f in mow)),
                                                         round(max(f["P_el"] for f in mow))),
            "lift_mm": round(last["lift"]), "fold_deg": round(last["fold"], 1),
            "t_stop": round(next(f["t"] for f in frames if not f["mowing"]), 2)}


def render_frames(folder, first=0, count=None, fps=FPS, size=(720, 480), frames=None):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    if frames is None:
        frames = prepare(fps)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i])
        doc.recompute()
        track_camera(frames[i], frames)
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, fps=FPS, size=(720, 480)):
    build()
    frames = prepare(fps)
    first, total = 0, len(frames)
    while first < total:
        first, total = render_frames(folder, first, 25, fps, size, frames)
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
    frames = prepare(fps)
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
            apply_frame(doc, frames[i])
            if follow:
                track_camera(frames[i], frames)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))


def check_fit(doc=None, steps=(0.0, 0.25, 0.5, 0.75, 1.0)):
    """Overlap between the real robot model and the mower in the animation document along the way from work to
    transport (robot at the origin)."""
    doc = doc or App.getDocument(DOC_NAME)
    doc.getObject("Robot").Placement = App.Placement()
    out = {}
    for s in steps:
        build_sbm.set_transport(doc, s)
        doc.recompute()
        out["transport_%g" % s] = build_sbm.check_interference(doc)
    build_sbm.reset(doc)
    return out
