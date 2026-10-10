"""Animation: the Bruut OpenAgbot stakes out three points with the field marker.

The robot drives along the row and stops roughly behind each point (a few cm off in x and y, as it would in the
field). It stands still, measures, the stage moves the nozzle onto the point (X and Y together), the Z axis goes
down until the shroud touches the ground (the shroud lifts, the sensor switches), the can sprays a dot, Z goes up
and the robot drives on. Timing from mrk_calc (the same move profiles and times as the capacity calculation).

Builds a separate document (the robot files in "agbot design" are not changed): robot from build_agbot, marker
from build_mrk, grass floor, the design points (black crosses) and the paint dots.

Use in FreeCAD:
    import animate_mrk
    animate_mrk.build()                              # build the document
    animate_mrk.play()                               # play live, animate_mrk.stop()
    animate_mrk.summary()                            # key figures of the run
    animate_mrk.render_all(r"C:\\temp\\mrk_frames")
    import make_gif_mrk; make_gif_mrk.main(r"C:\\temp\\mrk_frames", r"previews\\animation_staking_out.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrk_params as P
import mrk_calc as C
import mrk_parts as G
import build_mrk

DOC_NAME = "Marker_on_robot_animation"

# ---------------------------------------------------------------------
# Run: design points (world x, y) and how far off the robot stops behind each one (robot x offset, y error)
# ---------------------------------------------------------------------
POINTS = [(150.0, 2300.0), (-240.0, 4400.0), (330.0, 6500.0)]
ROBOT_X = 40.0                  # the robot drives 40 mm right of the line through the start (cross-track error)
STOP_ERR = [-60.0, 75.0, 30.0]  # robot stops this much too early (-) or too late (+) in y
DOT_ERR = [(2.0, -3.0), (-3.0, 1.0), (1.0, 2.0)]    # where the dot really lands (mm): GNSS, tilt, stage, paint
START_GAP = 1500.0              # robot starts this far before the first stop

FPS = 5                         # frames per second of real time; the GIF plays at 10 fps = 2 x speed
HOLD_END = 2.5
COLOR = {"grass": (0.47, 0.62, 0.30), "cross": (0.08, 0.08, 0.08), "dot": (0.98, 0.20, 0.55)}

_timer = None
_play = {}


# ---------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------
def profile(d, v, a, t):
    """Position along a trapezoid move of length d (sign kept) at time t."""
    s = abs(d)
    if s == 0.0:
        return 0.0
    d_acc = v * v / a
    if s <= d_acc:
        tm = math.sqrt(s / a)
        x = 0.5 * a * t * t if t <= tm else s - 0.5 * a * max(0.0, 2 * tm - t) ** 2
    else:
        ta = v / a
        tc = (s - d_acc) / v
        if t <= ta:
            x = 0.5 * a * t * t
        elif t <= ta + tc:
            x = 0.5 * v * ta + v * (t - ta)
        else:
            x = s - 0.5 * a * max(0.0, 2 * ta + tc - t) ** 2
    return math.copysign(min(s, x), d)


def segments():
    """List of (phase, duration, data) for the whole run."""
    out = []
    y_r = POINTS[0][1] - P.y_tool_nom + STOP_ERR[0] - START_GAP
    sx, sy = 0.0, P.y_tool_nom
    for i, ((px, py), err) in enumerate(zip(POINTS, STOP_ERR)):
        y_stop = py - P.y_tool_nom + err
        d = y_stop - y_r
        out.append(("drive", C.move_time(d, P.drive_speed * 1000.0, P.drive_acc * 1000.0), {"i": i, "y0": y_r, "d": d}))
        y_r = y_stop
        out.append(("settle", P.settle_s, {"i": i}))
        out.append(("measure", P.measure_s, {"i": i}))
        tx, ty = px - ROBOT_X, py - y_r                         # target in robot coordinates
        t_st = max(C.move_time(tx - sx, P.x_v, P.x_a), C.move_time(ty - sy, P.y_v, P.y_a))
        out.append(("stage", t_st, {"i": i, "x0": sx, "y0": sy, "x1": tx, "y1": ty}))
        sx, sy = tx, ty
        z_fast = P.ZC_PARK - P.ZC_WORK - P.z_touch_zone
        out.append(("z_down", C.move_time(z_fast, P.z_v, P.z_a), {"i": i, "z0": P.ZC_PARK, "d": -z_fast}))
        out.append(("touch", P.z_touch_zone / P.z_touch_v, {"i": i, "z0": P.ZC_WORK + P.z_touch_zone}))
        out.append(("spray", 2 * P.servo_s + P.spray_s, {"i": i}))
        out.append(("z_up", C.move_time(P.ZC_PARK - P.ZC_WORK, P.z_v, P.z_a), {"i": i, "z0": P.ZC_WORK,
                                                                               "d": P.ZC_PARK - P.ZC_WORK}))
        out.append(("photo", P.photo_s, {"i": i}))
    out.append(("done", HOLD_END, {"i": len(POINTS) - 1}))
    return out


def prepare(fps=FPS):
    """Frames (dicts) of the whole run, sampled at fps (real time)."""
    segs = segments()
    frames = []
    t0 = 0.0
    state = {"y_r": segs[0][2]["y0"], "sx": 0.0, "sy": P.y_tool_nom, "zc": P.ZC_PARK, "lift": 0.0, "spin": 0.0,
             "dots": [], "v": 0.0}
    n = int(math.ceil(sum(s[1] for s in segs) * fps)) + 1
    k = 0
    for phase, dur, d in segs:
        t_end = t0 + dur
        while k < n and k / float(fps) <= t_end + 1e-9:
            t = k / float(fps) - t0
            f = frame_state(phase, dur, d, t, state)
            f["t"] = k / float(fps)
            frames.append(f)
            k += 1
        finish_segment(phase, d, state)
        t0 = t_end
    return frames


def contact_zc():
    return P.zc_for_ground(0.0, 0.0)


def frame_state(phase, dur, d, t, st):
    i = d["i"]
    px, py = POINTS[i]
    y_r, sx, sy, zc, lift = st["y_r"], st["sx"], st["sy"], st["zc"], st["lift"]
    v = 0.0
    spray = 0.0
    if phase == "drive":
        y_r = d["y0"] + profile(d["d"], P.drive_speed * 1000.0, P.drive_acc * 1000.0, t)
        dt = 0.05
        v = abs(profile(d["d"], P.drive_speed * 1000.0, P.drive_acc * 1000.0, min(dur, t + dt)) -
                profile(d["d"], P.drive_speed * 1000.0, P.drive_acc * 1000.0, max(0.0, t - dt))) / (2 * dt)
    elif phase == "stage":
        sx = d["x0"] + profile(d["x1"] - d["x0"], P.x_v, P.x_a, t)
        sy = d["y0"] + profile(d["y1"] - d["y0"], P.y_v, P.y_a, t)
    elif phase == "z_down":
        zc = d["z0"] + profile(d["d"], P.z_v, P.z_a, t)
    elif phase == "touch":
        zc = d["z0"] - P.z_touch_v * t
        lift = max(0.0, contact_zc() - zc)
    elif phase == "spray":
        spray = min(1.0, max(0.0, (t - P.servo_s) / P.spray_s))
    elif phase == "z_up":
        zc = d["z0"] + profile(d["d"], P.z_v, P.z_a, t)
        lift = max(0.0, contact_zc() - zc)
    spin = st["spin"] + (y_r - st["y_r"]) / (P.robot_tire_d / 2.0)
    dots = list(st["dots"])
    if phase == "spray" and spray > 0.0:
        ex, ey = DOT_ERR[i]
        dots.append((px + ex, py + ey, C.spray()["dot_d"] * (0.35 + 0.65 * spray)))
    # nozzle in world coordinates and its distance to the point
    nx, ny = ROBOT_X + sx, y_r + sy
    tx, ty = px - ROBOT_X, py - y_r
    return {"phase": phase, "i": i, "robot": (ROBOT_X, y_r), "spin": spin, "v": v,
            "stage": (sx, sy, zc, lift), "dots": dots, "target_rel": (tx, ty),
            "nozzle_err": math.hypot(nx - px, ny - py), "shroud_bottom": zc + P.SHROUD_BOTTOM_DZ + lift}


def finish_segment(phase, d, st):
    i = d["i"]
    if phase == "drive":
        y_new = d["y0"] + d["d"]
        st["spin"] += (y_new - st["y_r"]) / (P.robot_tire_d / 2.0)
        st["y_r"] = y_new
    elif phase == "stage":
        st["sx"], st["sy"] = d["x1"], d["y1"]
    elif phase == "z_down":
        st["zc"] = d["z0"] + d["d"]
    elif phase == "touch":
        st["zc"] = P.ZC_WORK
        st["lift"] = contact_zc() - P.ZC_WORK
    elif phase == "spray":
        px, py = POINTS[i]
        ex, ey = DOT_ERR[i]
        st["dots"].append((px + ex, py + ey, C.spray()["dot_d"]))
    elif phase == "z_up":
        st["zc"] = P.ZC_PARK
        st["lift"] = 0.0


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def build():
    if build_mrk.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_mrk.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Field marker on robot - animation"
    doc.Comment = "Generated by animate_mrk.py. Robot from agbot design, marker from build_mrk."
    robot = build_mrk.build_robot(doc)
    build_mrk.build_into(doc, robot)
    floor = doc.addObject("Part::Feature", "anim_floor")
    floor.Shape = Part.makeBox(16000.0, 30000.0, 40.0, V(-8000.0, -6000.0, -40.0))
    floor.ViewObject.ShapeColor = COLOR["grass"]
    crosses = doc.addObject("Part::Feature", "anim_targets")
    crosses.Shape = Part.makeCompound([G.target_cross(x, y, 180.0, 0.0, 8.0, 0.8) for (x, y) in POINTS])
    crosses.ViewObject.ShapeColor = COLOR["cross"]
    dots = doc.addObject("Part::Feature", "anim_dots")
    dots.ViewObject.ShapeColor = COLOR["dot"]
    doc.recompute()
    return doc


def apply_frame(doc, f):
    doc.getObject("Robot").Placement = App.Placement(V(f["robot"][0], f["robot"][1], 0.0), App.Rotation())
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    sx, sy, zc, lift = f["stage"]
    for name, pl in build_mrk.pose_placements(sx, sy, zc, lift).items():
        doc.getObject(name).Placement = pl
    dots = [G.paint_dot(x, y, d, 0.8, 0.6) for (x, y, d) in f["dots"]]
    doc.getObject("anim_dots").Shape = Part.makeCompound(dots) if dots else Part.Shape()


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_A = ((-1550.0, -2450.0, 1250.0), (0.0, -650.0, 520.0))      # from behind left onto the stage (follows the robot)
CAM_B = ((-420.0, -760.0, 700.0), (0.0, 0.0, 40.0))             # end: close to the last dot (relative to the point)


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def track_camera(f, frames, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    t_end = frames[-1]["t"]
    s = smooth((f["t"] - (t_end - HOLD_END)) / (HOLD_END * 0.7))
    follow = (f["robot"][0] + 0.5 * f["stage"][0], f["robot"][1] + CAM_A[1][1], CAM_A[1][2])
    px, py = POINTS[-1]
    end = (px + CAM_B[1][0], py + CAM_B[1][1], CAM_B[1][2])
    tgt = [follow[i] + (end[i] - follow[i]) * s for i in range(3)]
    eye_a = [follow[i] + CAM_A[0][i] for i in range(3)]
    eye_b = [end[i] + CAM_B[0][i] for i in range(3)]
    eye = [eye_a[i] + (eye_b[i] - eye_a[i]) * s for i in range(3)]
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(*eye))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


STATE = {"drive": "driving to the point", "settle": "standing still", "measure": "measuring: RTK fix + IMU, averaging",
         "stage": "stage moves the nozzle onto the point", "z_down": "Z down", "touch": "Z slow until the shroud touches",
         "spray": "spraying", "z_up": "Z up", "photo": "photo + log", "done": "done"}


def meta(f):
    sx, sy, zc, lift = f["stage"]
    tx, ty = f["target_rel"]
    return {"t": round(f["t"], 2), "phase": f["phase"], "state": STATE[f["phase"]], "i": f["i"] + 1, "n": len(POINTS),
            "v": round(f["v"], 0), "stage": [round(sx, 1), round(sy, 1), round(zc, 1), round(lift, 1)],
            "target_rel": [round(tx, 1), round(ty, 1)], "stop_err": STOP_ERR[f["i"]], "robot_x": ROBOT_X,
            "point": POINTS[f["i"]], "nozzle_err": round(f["nozzle_err"], 1),
            "shroud_bottom": round(f["shroud_bottom"], 1), "dots": len([d for d in f["dots"]]),
            "window": [-P.x_stroke / 2.0, P.x_stroke / 2.0, P.y_tool_front - P.y_stroke, P.y_tool_front],
            "dot_err": DOT_ERR[f["i"]]}


def summary(frames=None):
    frames = frames or prepare()
    segs = segments()
    per_point = [sum(s[1] for s in segs if s[2]["i"] == i and s[0] != "done") for i in range(len(POINTS))]
    stage = [s[2] for s in segs if s[0] == "stage"]
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 1),
            "time_per_point_s": [round(t, 1) for t in per_point],
            "stage_targets": [(round(s["x1"]), round(s["y1"])) for s in stage],
            "in_window": all(-P.x_stroke / 2.0 <= s["x1"] <= P.x_stroke / 2.0 and
                             P.y_tool_front - P.y_stroke <= s["y1"] <= P.y_tool_front for s in stage),
            "min_shroud_bottom": round(min(f["shroud_bottom"] for f in frames), 1),
            "dot_d": round(C.spray()["dot_d"], 1)}


def render_frames(folder, first=0, count=None, fps=FPS, size=(720, 480)):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames = prepare(fps)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i])
        track_camera(frames[i], frames)
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, fps=FPS, size=(720, 480)):
    build()
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 40, fps, size)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=FPS, loop=False, follow=True, speed=2.0):
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
            f = frames[_play["index"]]
            _play["index"] += 1
            apply_frame(doc, f)
            if follow:
                track_camera(f, frames)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / (fps * speed)))


def check_fit(doc=None, tol=1.0):
    """Overlap between the real robot model and the marker in the animation document, in every stage pose of the run
    (pose changes only)."""
    doc = doc or App.getDocument(DOC_NAME)
    poses = sorted({tuple(round(v, 1) for v in f["stage"]) for f in prepare()[::5]})
    return build_mrk.check_fit(doc, poses=poses, tol=tol)
