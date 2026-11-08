"""Animation: the Bruut OpenAgbot works a strip with the small cultivator in the A-frame hitch and lifts it at the
headland with the LA36 top link.

In work the LA36 stands at its work length (rod pin in the middle of the slot in the apex lugs): the lift frame
floats, the gauge wheels follow the bumps in their tracks and the rod pin slides in the slot. At the headland the
LA36 retracts at its datasheet speed under the load (tpa_calc): the slot closes, the frame turns up about the lower
pivots and the shares come out of the ground; the robot drives on slowly and stops with the cultivator lifted.
Behind every share the loosened strip appears (dark) while the share is in the ground.

Builds a separate document (the robot files in "agbot design" are not changed): robot from build_agbot, hitch and
cultivator from build_tpa, a grass floor with mounds in the gauge wheel tracks.

Use in FreeCAD:
    import animate_tpa
    animate_tpa.build()                              # build the document
    animate_tpa.play()                               # play live, animate_tpa.stop()
    animate_tpa.summary()                            # key figures of the run
    animate_tpa.render_all(r"C:\\temp\\tpa_frames")
    import make_gif_tpa; make_gif_tpa.main(r"C:\\temp\\tpa_frames", r"previews\\animation_work_and_lift.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tpa_params as P
import tpa_parts as G
import tpa_calc as C
import tph_params as TP
import build_tpa

DOC_NAME = "TPA_on_robot_animation"
FPS = 10
COLOR = {"grass": (0.47, 0.62, 0.30), "mound": (0.55, 0.45, 0.30), "tilled": (0.33, 0.22, 0.13)}

# ---------------------------------------------------------------------
# Run (robot centre y, mm and s)
# ---------------------------------------------------------------------
SPEED = 1000.0          # mm/s in work (as tph_calc)
SLOW = 400.0            # mm/s while lifting at the headland
ACCEL = 1.0             # s to reach SPEED
HOLD_START = 0.6
Y_LIFT = 5200.0         # robot centre where the LA36 starts to retract
HOLD_END = 1.5
MOUNDS = (              # x, y (mm, world), height, radius: in the tracks of the gauge wheels (x +-565)
    (565.0, 1300.0, 22.0, 160.0),
    (-565.0, 2500.0, 18.0, 140.0),
    (565.0, 3500.0, 14.0, 120.0),
    (-565.0, 4300.0, 24.0, 170.0),
)
WHEEL_X = (-TP.wheel_x, TP.wheel_x)

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
    """Height (mm) the gauge wheel at (x, wy) must rise to roll over the mounds (2D profile in its plane)."""
    r = TP.wheel_d / 2.0
    best = 0.0
    for k in range(-25, 26):
        dy = k * r / 25.0
        best = max(best, mound_h(x, wy + dy) + math.sqrt(max(r * r - dy * dy, 0.0)) - r)
    return best


def theta_ground(y_robot):
    """Frame angle (deg) at which the higher gauge wheel touches the ground (robot at y_robot, flat ground)."""
    wy0, wz0 = G.cult_wheel_centre()
    best = -5.0
    for x in WHEEL_X:
        lo, hi = -6.0, 6.0
        for _ in range(30):
            mid = (lo + hi) / 2.0
            wy, wz = P.rotate_yz((wy0, wz0), mid)
            if wz - wz0 < wheel_rise(x, wy + y_robot):
                lo = mid
            else:
                hi = mid
        best = max(best, (lo + hi) / 2.0)
    return best


def float_limits(act_len):
    """(lowest, highest) frame angle with the LA36 at act_len: pin at the slot end / at the far end."""
    lo = P.lift_for_length(act_len)
    a, b = lo, 40.0
    for _ in range(40):
        mid = (a + b) / 2.0
        d, u = P.act_d(mid), P.slot_dir(mid)
        e = (d[0] + P.float_slot * u[0], d[1] + P.float_slot * u[1])
        if math.hypot(e[0] - P.act_c[0], e[1] - P.act_c[1]) > act_len:
            a = mid
        else:
            b = mid
    return lo, (a + b) / 2.0


def act_force_now(theta):
    """Pull in the LA36 (N) when it carries the frame at theta (virtual work, as tpa_calc.actuator)."""
    items = C.moving_loads()
    h = 0.25
    dz = sum(k * P.g * (P.rotate_yz(c, theta + h)[1] - P.rotate_yz(c, theta - h)[1]) for k, c in items)
    dl = abs(P.act_length(theta + h) - P.act_length(theta - h))
    return dz / dl


# ---------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------
def _drive(t):
    """Robot y and speed at time t for the work part (before the lift)."""
    t1 = t - HOLD_START
    if t1 <= 0.0:
        return 0.0, 0.0
    if t1 < ACCEL:
        return 0.5 * SPEED / ACCEL * t1 * t1, SPEED * t1 / ACCEL
    return 0.5 * SPEED * ACCEL + SPEED * (t1 - ACCEL), SPEED


def prepare(fps=FPS):
    L_w, L_t = P.act_work_length(), P.act_length(P.lift_transport)
    t_lift = HOLD_START + ACCEL + (Y_LIFT - 0.5 * SPEED * ACCEL) / SPEED
    frames = []
    dt = 1.0 / fps
    t, y, L = 0.0, 0.0, L_w
    lifted_at = None
    in_ground = {x: [] for x in TP.tine_x}
    while True:
        if t < t_lift:
            y, v = _drive(t)
            phase = "work"
        else:
            # decelerate to SLOW over 0.5 s, LA36 retracts at its speed under the load
            v = max(SLOW, SPEED - (SPEED - SLOW) * (t - t_lift) / 0.5)
            if lifted_at is not None and t > lifted_at + 1.0:
                v = max(0.0, SLOW - SLOW * (t - lifted_at - 1.0) / 0.8)
            y += v * dt if frames else 0.0
            phase = "lifting" if L > L_t + 0.01 else "lifted"
        th_g = theta_ground(y)
        lo, hi = float_limits(L)
        theta = min(max(th_g, lo), hi)
        carrying = theta <= lo + 1e-6 and th_g < lo
        f_act = act_force_now(theta) if carrying else 0.0
        if phase != "work" and L > L_t:
            L = max(L_t, L - P.act_speed(f_act if carrying else 0.0) * dt)
            if L <= L_t + 0.01 and lifted_at is None:
                lifted_at = t
        share_z = [P.rotate_yz((p[1], p[2]), theta)[1] for p in G.cult_share_points()]
        share_y = [P.rotate_yz((p[1], p[2]), theta)[0] + y for p in G.cult_share_points()]
        for x, sz, sy in zip(TP.tine_x, share_z, share_y):
            seg = in_ground[x]
            if sz < -2.0:
                if seg and seg[-1][1] is None:
                    seg[-1][2] = sy
                else:
                    seg.append([sy, None, sy])
            elif seg and seg[-1][1] is None:
                seg[-1][1] = sy
        frames.append({"t": round(t, 3), "y": y, "v": v, "theta": theta, "act_len": L, "carrying": carrying,
                       "act_N": f_act, "phase": phase, "depth": -min(share_z),
                       "strips": {x: [(a, (b if b is not None else c)) for a, b, c in in_ground[x]]
                                  for x in TP.tine_x},
                       "spin": y / (P.robot_tire_d / 2.0)})
        t += dt
        if lifted_at is not None and v <= 0.0 and t > lifted_at + 1.8 + HOLD_END:
            break
        if t > 60.0:
            break
    return frames


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def build():
    if build_tpa.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_tpa.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "A-frame hitch on robot - animation"
    doc.Comment = "Generated by animate_tpa.py. Robot from agbot design, hitch and cultivator from build_tpa."
    robot = build_tpa.build_robot(doc)
    build_tpa.build_into(doc, robot)
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
    build_tpa.set_pose(f["theta"], doc, None if f["carrying"] else f["act_len"])
    doc.getObject("anim_tilled").Shape = _strips(f["strips"])


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_A = ((2300.0, -3300.0, 1500.0), (-150.0, -900.0, 330.0))     # eye and target relative to the robot centre


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


STATE = {"work": "work: LA36 at its work length, frame floats on the gauge wheels (rod pin free in the slot)",
         "lifting": "headland: LA36 retracts, slot closed, frame turns up about the lower pivots",
         "lifted": "cultivator lifted (lower pins +200 mm): ready to turn"}


def meta(f):
    wy0, wz0 = G.cult_wheel_centre()
    return {"t": round(f["t"], 2), "phase": f["phase"], "state": STATE[f["phase"]], "v": round(f["v"]),
            "act_len": round(f["act_len"], 1), "act_N": round(f["act_N"]), "theta": round(f["theta"], 2),
            "pin_z": round(P.lower_pin(f["theta"])[1]), "depth": round(f["depth"], 1),
            "wheel_lift": round(P.rotate_yz((wy0, wz0), f["theta"])[1] - wz0, 1),
            "driven_m": round(f["y"] / 1000.0, 2)}


def summary(frames=None):
    frames = frames or prepare()
    work = [f for f in frames if f["phase"] == "work"]
    return {"frames": len(frames), "t_end": frames[-1]["t"], "driven_m": round(frames[-1]["y"] / 1000.0, 2),
            "float_deg": (round(min(f["theta"] for f in work), 2), round(max(f["theta"] for f in work), 2)),
            "depth_work_mm": (round(min(f["depth"] for f in work), 1), round(max(f["depth"] for f in work), 1)),
            "act_N_max": round(max(f["act_N"] for f in frames)),
            "lift_time_s": round(sum(1 for f in frames if f["phase"] == "lifting") / float(FPS), 1),
            "theta_end": round(frames[-1]["theta"], 2)}


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
