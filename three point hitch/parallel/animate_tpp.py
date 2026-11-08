"""Animation: the Bruut OpenAgbot works a strip with the small cultivator on the parallel hitch (suspension of the
liquid fertilizer applicator) and lifts it at the headland.

In work the LA36 stands at its work length: the rod pin sits at the end of the slot with the carrier at the bottom
of its float, so the parallel linkage floats up to +81 mm (+-40 around the work pose) and the cultivator follows the
mounds in the gauge wheel tracks while it stays level. At the headland the LA36 retracts at its datasheet speed under
the load (tpp_calc), the slot closes and the carrier goes straight up 203 mm; the robot drives on slowly and stops.

Builds a separate document: robot from build_agbot, hitch and cultivator from build_tpp, a grass floor with mounds.

Use in FreeCAD:
    import animate_tpp
    animate_tpp.build(); animate_tpp.play(); animate_tpp.stop(); animate_tpp.summary()
    animate_tpp.render_all(r"C:\\temp\\tpp_frames")
    import make_gif_tpp; make_gif_tpp.main(r"C:\\temp\\tpp_frames", r"previews\\animation_float_and_lift.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tpp_params as P
import tpp_calc as C
import tpa_parts as GA
import tph_params as TP
import build_tpp

DOC_NAME = "TPP_on_robot_animation"
FPS = 10
COLOR = {"grass": (0.47, 0.62, 0.30), "mound": (0.55, 0.45, 0.30), "tilled": (0.33, 0.22, 0.13)}

SPEED = 1000.0
SLOW = 400.0
ACCEL = 1.0
HOLD_START = 0.6
Y_LIFT = 5200.0
HOLD_END = 1.5
MOUNDS = (                      # x, y (world), height, radius: in the gauge wheel tracks; the robot tracks stay flat
    (565.0, 1200.0, 34.0, 200.0),
    (-565.0, 2300.0, 22.0, 150.0),
    (565.0, 3100.0, 16.0, 120.0),
    (-565.0, 3900.0, 38.0, 210.0),
    (565.0, 4500.0, 26.0, 160.0),
)
WHEEL_X = (-TP.wheel_x, TP.wheel_x)
BASE = P.cp_base

_timer = None
_play = {}


def mound_h(x, y):
    h = 0.0
    for mx, my, a, r in MOUNDS:
        d2 = ((x - mx) ** 2 + (y - my) ** 2) / (r * r)
        if d2 < 1.0:
            h = max(h, a * math.sqrt(1.0 - d2))
    return h


def wheel_rise(x, wy):
    r = TP.wheel_d / 2.0
    best = 0.0
    for k in range(-25, 26):
        dy = k * r / 25.0
        best = max(best, mound_h(x, wy + dy) + math.sqrt(max(r * r - dy * dy, 0.0)) - r)
    return best


def theta_ground(y_robot):
    """Link angle at which the higher gauge wheel touches the ground (the carrier translates)."""
    wy0, _ = GA.cult_wheel_centre(BASE)
    lo, hi = -40.0, 10.0
    for _ in range(36):
        mid = (lo + hi) / 2.0
        d = P.shift(mid)
        need = max(wheel_rise(x, wy0 + d[0] + y_robot) for x in WHEEL_X)
        if d[1] < need:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def act_force_now(theta):
    h = 0.25
    dz = P.shift(theta + h)[1] - P.shift(theta - h)[1]
    dl = abs(P.act_length(theta + h) - P.act_length(theta - h))
    return sum(k * w for k, w in C._items()) * P.g * dz / dl


def _drive(t):
    t1 = t - HOLD_START
    if t1 <= 0.0:
        return 0.0, 0.0
    if t1 < ACCEL:
        return 0.5 * SPEED / ACCEL * t1 * t1, SPEED * t1 / ACCEL
    return 0.5 * SPEED * ACCEL + SPEED * (t1 - ACCEL), SPEED


def prepare(fps=FPS):
    L_w, L_t = P.act_work_length(), P.act_length(P.theta_lift)
    t_lift = HOLD_START + ACCEL + (Y_LIFT - 0.5 * SPEED * ACCEL) / SPEED
    frames = []
    dt = 1.0 / fps
    t, y, L = 0.0, 0.0, L_w
    lifted_at = None
    shares0 = [(p[0], p[1], p[2]) for p in GA.cult_share_points(BASE)]
    in_ground = {x: [] for x in TP.tine_x}
    while True:
        if t < t_lift:
            y, v = _drive(t)
            phase = "work"
        else:
            v = max(SLOW, SPEED - (SPEED - SLOW) * (t - t_lift) / 0.5)
            if lifted_at is not None and t > lifted_at + 1.0:
                v = max(0.0, SLOW - SLOW * (t - lifted_at - 1.0) / 0.8)
            y += v * dt
            phase = "lifting" if L > L_t + 0.01 else "lifted"
        th_g = theta_ground(y)
        lo, hi = P.float_limits(L)
        theta = min(max(th_g, lo), hi)
        carrying = th_g < lo
        f_act = act_force_now(theta) if carrying else 0.0
        if phase != "work" and L > L_t:
            L = max(L_t, L - C.Q.act_speed(f_act, P.act_variant) * dt)
            if L <= L_t + 0.01 and lifted_at is None:
                lifted_at = t
        d = P.shift(theta)
        for (x, sy0, sz0) in shares0:
            sz, sy = sz0 + d[1], sy0 + d[0] + y
            seg = in_ground[x]
            if sz < -2.0:
                if seg and seg[-1][1] is None:
                    seg[-1][2] = sy
                else:
                    seg.append([sy, None, sy])
            elif seg and seg[-1][1] is None:
                seg[-1][1] = sy
        frames.append({"t": round(t, 3), "y": y, "v": v, "theta": theta, "act_len": L, "carrying": carrying,
                       "act_N": f_act, "phase": phase, "depth": -(shares0[0][2] + d[1]), "dz": d[1],
                       "strips": {x: [(a, (b if b is not None else c)) for a, b, c in in_ground[x]]
                                  for x in TP.tine_x},
                       "spin": y / (P.robot_tire_d / 2.0)})
        t += dt
        if lifted_at is not None and v <= 0.0 and t > lifted_at + 1.8 + HOLD_END:
            break
        if t > 60.0:
            break
    return frames


def build():
    if build_tpp.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_tpp.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Parallel hitch on robot - animation"
    doc.Comment = "Generated by animate_tpp.py. Robot from agbot design, hitch and cultivator from build_tpp."
    robot = build_tpp.build_robot(doc)
    build_tpp.build_into(doc, robot)
    floor = doc.addObject("Part::Feature", "anim_floor")
    floor.Shape = Part.makeBox(5000.0, 14000.0, 40.0, V(-2500.0, -4000.0, -40.0))
    floor.ViewObject.ShapeColor = COLOR["grass"]
    mounds = []
    for mx, my, a, r in MOUNDS:
        s = Part.makeSphere(r, V(0, 0, 0))
        m = App.Matrix()
        m.scale(1.0, 1.0, a / r)
        s = s.transformGeometry(m)
        s.translate(V(mx, my, 0.0))
        mounds.append(s.common(Part.makeBox(2 * r, 2 * r, a + 1.0, V(mx - r, my - r, 0.0))))
    o = doc.addObject("Part::Feature", "anim_mounds")
    o.Shape = Part.makeCompound(mounds)
    o.ViewObject.ShapeColor = COLOR["mound"]
    o = doc.addObject("Part::Feature", "anim_tilled")
    o.ViewObject.ShapeColor = COLOR["tilled"]
    o.ViewObject.DisplayMode = "Shaded"
    doc.recompute()
    return doc


def _strips(strips):
    out = []
    w = TP.share_w * 0.7
    for x, segs in strips.items():
        for a, b in segs:
            y0, y1 = sorted((a, b))
            if y1 - y0 > 2.0:
                out.append(Part.makeBox(w, y1 - y0, 1.5, V(x - w / 2.0, y0, 0.2)))
    return Part.makeCompound(out) if out else Part.Shape()


def apply_frame(doc, f):
    y = f["y"]
    doc.getObject("Robot").Placement = App.Placement(V(0.0, y, 0.0), App.Rotation())
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    build_tpp.set_pose(f["theta"], doc, None if f["carrying"] else f["act_len"])
    doc.getObject("anim_tilled").Shape = _strips(f["strips"])


CAM_A = ((2600.0, -2500.0, 1100.0), (-100.0, -950.0, 330.0))


def track_camera(f, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    y = f["y"]
    tgt = (CAM_A[1][0], y + CAM_A[1][1], CAM_A[1][2])
    eye = (CAM_A[0][0], y + CAM_A[0][1], CAM_A[0][2])
    cam = Gui.getDocument(DOC_NAME).ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(*eye))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


STATE = {"work": "work: LA36 at its work length, the parallel linkage floats, the cultivator stays level",
         "lifting": "headland: LA36 retracts, slot closed, the carrier goes straight up",
         "lifted": "cultivator lifted 203 mm, level: ready to turn"}


def meta(f):
    return {"t": round(f["t"], 2), "phase": f["phase"], "state": STATE[f["phase"]], "v": round(f["v"]),
            "act_len": round(f["act_len"], 1), "act_N": round(f["act_N"]), "theta": round(f["theta"], 2),
            "dz": round(f["dz"], 1), "depth": round(f["depth"], 1), "driven_m": round(f["y"] / 1000.0, 2)}


def summary(frames=None):
    frames = frames or prepare()
    work = [f for f in frames if f["phase"] == "work"]
    return {"frames": len(frames), "t_end": frames[-1]["t"], "driven_m": round(frames[-1]["y"] / 1000.0, 2),
            "float_mm": (round(min(f["dz"] for f in work), 1), round(max(f["dz"] for f in work), 1)),
            "depth_work_mm": (round(min(f["depth"] for f in work), 1), round(max(f["depth"] for f in work), 1)),
            "act_N_max": round(max(f["act_N"] for f in frames)),
            "lift_time_s": round(sum(1 for f in frames if f["phase"] == "lifting") / float(FPS), 1),
            "dz_end": round(frames[-1]["dz"], 1)}


def render_frames(folder, first=0, count=None, fps=FPS, size=(800, 500), frames=None):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames = frames or prepare(fps)
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


def render_all(folder, fps=FPS, size=(800, 500)):
    build()
    frames = prepare(fps)
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 30, fps, size, frames)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=FPS, loop=False, follow=True, speed=1.0):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer
    stop()
    doc = App.getDocument(DOC_NAME)
    frames = prepare(fps)
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
            f = frames[_play["index"]]
            _play["index"] += 1
            apply_frame(doc, f)
            if follow:
                track_camera(f)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / (fps * speed)))
