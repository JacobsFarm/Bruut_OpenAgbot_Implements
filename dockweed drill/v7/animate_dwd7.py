"""Animation: dockweed drill v7 behind the Bruut OpenAgbot treats 3 dock plants. No X axis: the robot steers.

Builds a separate document (the robot files in "agbot design" are not changed):
robot from build_agbot + implement from build_dwd7 + ground with plants.
The robot drives backwards (-y, implement first). The spindle sits fixed at x 0, so per plant:
- drive and steer an S-curve (dwd7_calc.s_curve: steering 0 at start and end, no steering at standstill) so that the
  rear axle centre, and with heading 0 also the spindle, ends right over the plant; stop;
- the LA36 extends (rapid) until the can feels the sward (sensor = ground level), the spindle runs at 500 rpm;
- plunge at 25 mm/s to 150 mm deep, dwell, rise while turning until the can comes free, retract to driving height;
- the plant disappears, a crushed soil column stays behind.
Power, Z force, actuator current, wheel loads and the steering come from dwd7_calc, so animation and report agree.
(Based on ../v6/animate_dwd6.py.)

Use in FreeCAD:
    import animate_dwd7
    animate_dwd7.build()
    animate_dwd7.play()                       # live, animate_dwd7.stop()
    animate_dwd7.summary()
    animate_dwd7.check_fit()                  # implement vs robot in the Z end positions (empty)
    animate_dwd7.render_all(r"C:\\temp\\dwd7_frames")
    import make_gif_dwd7; make_gif_dwd7.main(r"C:\\temp\\dwd7_frames", r"previews\\animation_three_plants_steering.gif")
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd7_params as P
import dwd7_parts as G
import dwd7_calc as C
import build_dwd7

FOLDER = os.path.dirname(os.path.abspath(__file__))
DOC_NAME = "DWD7_on_robot_animation"

# ---------------------------------------------------------------------
# Drive plan and plants (world coordinates; the robot starts with its centre at (0, 0) and drives to -y)
# ---------------------------------------------------------------------
DT = 0.25              # s simulated time per frame (GIF at 12 fps = 3x speed)
ACCEL = 0.8            # s accelerate / brake
SETTLE = 0.5           # s standing still after braking (RTK, camera)
HOLD_END = 1.5
PLANTS = ((-220.0, -2600.0, 1.0), (180.0, -5000.0, 0.85), (20.0, -7000.0, 1.1))    # x, y, size
SPIN_DEG = 37.0        # tool rotation per frame (stroboscopic)
SPINUP = 1.0           # s spindle up to speed
REAR_AXLE = -P.robot_wheel_y                       # local y of the rear axle centre (path reference point)
WHEELS_LOCAL = {"RL": (-P.robot_wheel_x, -P.robot_wheel_y), "RR": (P.robot_wheel_x, -P.robot_wheel_y),
                "FL": (-P.robot_wheel_x, P.robot_wheel_y), "FR": (P.robot_wheel_x, P.robot_wheel_y)}

COLOR = {"grass": (0.45, 0.62, 0.31), "lines": (0.35, 0.50, 0.24), "soil": (0.42, 0.29, 0.16),
         "leaf": (0.18, 0.45, 0.12), "root": (0.45, 0.30, 0.20), "path": (0.95, 0.85, 0.20)}
TERRAIN = ((-1600.0, 1600.0), (-8600.0, 1800.0))

_timer = None
_play = {}


# ---------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------
def drive_profile(dist, v=P.drive_speed, t_acc=ACCEL):
    """Trapezoid: returns (duration, function s(t)) for a distance dist (mm)."""
    a = v / t_acc
    if dist <= v * t_acc:                       # triangle
        t1 = math.sqrt(dist / a)
        T = 2 * t1

        def s(t):
            t = max(0.0, min(T, t))
            return 0.5 * a * t * t if t < t1 else dist - 0.5 * a * (T - t) ** 2
        return T, s
    t_c = (dist - v * t_acc) / v
    T = 2 * t_acc + t_c

    def s(t):
        t = max(0.0, min(T, t))
        if t < t_acc:
            return 0.5 * a * t * t
        if t < t_acc + t_c:
            return 0.5 * v * t_acc + v * (t - t_acc)
        return dist - 0.5 * a * (T - t) ** 2
    return T, s


def ease(t):
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


def drive_leg(x0, y0, x1, dist):
    """Rear axle path of one leg: from (x0, y0) dist mm to -y, sideways to x1 with the sine S-curve over the whole
    leg. Returns f(s) -> (x, y, x', x'')."""
    d = x1 - x0
    if dist < C.s_curve_length(d):
        raise ValueError("leg %.0f mm too short for %.0f mm sideways (needs %.0f mm at %.0f deg)"
                         % (dist, d, C.s_curve_length(d), P.robot_steer_max_deg))

    def f(s):
        x, x1_, x2_ = C.s_curve(d, dist, s)
        return x0 + x, y0 - s, x1_, x2_
    return f


def segments():
    """List of phases: dict(name, T, f(t) -> (rear_x, rear_y, x', x'', z, spinning), plant index)."""
    segs = []
    ph = dict(C.cycle(P.depth_std))
    rx, ry = 0.0, REAR_AXLE                   # rear axle centre at the start
    zd = P.drive_z
    z_pot = P.pot_rim                         # tool underside when the can touches the ground
    z_bot = -P.depth_std
    for i, (px, py, _) in enumerate(PLANTS):
        ry_stop = py - C.SPINDLE_Y + REAR_AXLE      # heading 0 at the stop: spindle straight behind the rear axle
        dist = ry - ry_stop
        T, s = drive_profile(dist)
        leg = drive_leg(rx, ry, px, dist)
        segs.append({"name": "drive", "T": T + SETTLE, "plant": i,
                     "f": (lambda t, s=s, leg=leg: leg(s(t)) + (zd, False))})
        hold = (px, ry_stop, 0.0, 0.0)
        segs.append({"name": "probe", "T": ph["z_down_to_pot"], "plant": i,
                     "f": (lambda t, T=ph["z_down_to_pot"], h=hold: h + (zd - (zd - z_pot) * ease(t / T), True))})
        segs.append({"name": "plunge", "T": ph["plunge"], "plant": i,
                     "f": (lambda t, T=ph["plunge"], h=hold: h + (z_pot - (z_pot - z_bot) * t / T, True))})
        segs.append({"name": "dwell", "T": ph["dwell"], "plant": i,
                     "f": (lambda t, h=hold: h + (z_bot, True))})
        segs.append({"name": "rise", "T": ph["rise_mixing"], "plant": i,
                     "f": (lambda t, T=ph["rise_mixing"], h=hold: h + (z_bot + (z_pot - z_bot) * t / T, True))})
        segs.append({"name": "up", "T": ph["z_up"], "plant": i,
                     "f": (lambda t, T=ph["z_up"], h=hold: h + (z_pot + (zd - z_pot) * ease(t / T), False))})
        rx, ry = px, ry_stop
    T, s = drive_profile(1200.0)
    leg = drive_leg(rx, ry, rx, 1200.0)
    segs.append({"name": "away", "T": T + HOLD_END, "plant": len(PLANTS) - 1,
                 "f": (lambda t, s=s, leg=leg: leg(s(t)) + (zd, False))})
    return segs


TEXT = {
    "drive": "Driving backwards: the robot steers the fixed spindle over the next dock plant (no X axis)",
    "probe": "Stopped, heading 0. Spindle %d rpm, LA36 extends until the can feels the sward" % P.cutter_rpm,
    "plunge": "Crushing: plunge at %d mm/s to %d mm deep" % (P.plunge_v, P.depth_std),
    "dwell": "Dwell at depth",
    "rise": "Rising while turning (mixes once more), the soil stays in the hole",
    "up": "Can free, LA36 retracts to driving height, spindle brakes",
    "away": "Done: 3 holes of 18 cm with finely ground root",
}


def act_current(phase, fz):
    """LA36 current (A, 24 V) per phase: push = cutting force minus the weight of the Z carriage (helps),
    pull = weight of Z carriage and can."""
    W = C.MODEL["z_moving_kg"] * C.G_ACC
    if phase == "probe":
        return C.act_current(0.0, P.rapid_z)
    if phase == "plunge":
        return C.act_current(max(0.0, fz - W), P.plunge_v)
    if phase == "rise":
        return C.act_current(C.z_lift_force(), 2 * P.plunge_v)
    if phase == "up":
        return C.act_current(C.z_lift_force(), P.rapid_z)
    return 0.0


def robot_pose(rx, ry, x1):
    """Robot origin (centre) and heading psi (rad) from the rear axle centre and the path slope x' (driving to -y)."""
    psi = math.atan(x1)
    return rx + REAR_AXLE * math.sin(psi), ry - REAR_AXLE * math.cos(psi), psi


def local_to_world(origin, local):
    ox, oy, psi = origin
    lx, ly = local
    return (ox + lx * math.cos(psi) - ly * math.sin(psi), oy + lx * math.sin(psi) + ly * math.cos(psi))


def prepare(dt=DT):
    frames = []
    t_total = 0.0
    angle = 0.0
    spin_t = 0.0
    done = set()
    rolls = {k: 0.0 for k in WHEELS_LOCAL}
    prev = None
    prev_delta = 0.0
    for seg in segments():
        n = max(1, int(round(seg["T"] / dt)))
        for k in range(n):
            t = (k + 1) * seg["T"] / n
            rx, ry, x1, x2, z, spinning = seg["f"](t)
            origin = robot_pose(rx, ry, x1)
            delta = C.steer_angle(x1, x2)
            dl, dr = C.ackermann(delta)
            wheels = {tag: local_to_world(origin, loc) for tag, loc in WHEELS_LOCAL.items()}
            if prev is not None:
                for tag, (wx, wy) in wheels.items():
                    rolls[tag] += math.hypot(wx - prev[tag][0], wy - prev[tag][1])
            prev = wheels
            spindle = local_to_world(origin, (0.0, C.SPINDLE_Y))
            spin_t = spin_t + seg["T"] / n if spinning else 0.0
            rpm = P.cutter_rpm * min(1.0, spin_t / SPINUP) if spinning else 0.0
            if rpm > 0:
                angle += SPIN_DEG * dt / DT      # same strobe speed per second of simulation
            depth = max(0.0, -z)
            rim = build_dwd7.pot_rim(z)
            on_ground = rim <= 1e-6
            cutting = seg["name"] == "plunge" and z < 0
            power = C.cut_power() if cutting else (C.cut_power() * 0.3 if seg["name"] == "rise" and z < 0
                                                   else (P.idle_w * rpm / P.cutter_rpm))
            fz = C.thrust(depth) if seg["name"] in ("plunge", "dwell") else 0.0
            loads = C.axle_loads(fz, on_ground)
            act_a = act_current(seg["name"], fz)
            i = seg["plant"]
            px, py, _ = PLANTS[i]
            treating = seg["name"] in ("plunge", "dwell", "rise") and z < P.pot_rim / 2
            if seg["name"] == "up":
                done.add(i)
            step = seg["T"] / n
            t_total += step
            frames.append({"t": t_total, "dt": step, "phase": seg["name"], "plant": i, "origin": origin,
                           "rear": (rx, ry), "delta": delta, "dl": dl, "dr": dr,
                           "steer_rate": abs(delta - prev_delta) / step, "rolls": dict(rolls),
                           "spindle": spindle, "off_x": spindle[0] - px, "to_go": spindle[1] - py, "z": z,
                           "depth": depth, "rim": rim, "pot_on_ground": on_ground, "rpm": rpm, "angle": angle,
                           "power": power, "fz": fz, "act_a": act_a, "wheels": loads["wheels_kg"],
                           "front": loads["front_kg"], "rear_kg": loads["rear_kg"], "done": sorted(done),
                           "treating": treating,
                           "leaves_gone": [j for j in range(len(PLANTS)) if j in done or (j == i and treating)]})
            prev_delta = delta
    return frames


def path_points(step=25.0):
    """Planned rear axle path (= spindle path at the stops), for the line on the ground."""
    pts = []
    for seg in segments():
        if seg["name"] not in ("drive", "away"):
            continue
        n = max(2, int(seg["T"] / 0.05))
        for k in range(n + 1):
            rx, ry = seg["f"](k * seg["T"] / n)[:2]
            if not pts or math.hypot(rx - pts[-1][0], ry - pts[-1][1]) >= step:
                pts.append((rx, ry))
    return pts


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def build():
    BA = build_dwd7.load_robot()
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Dockweed drill v7 on robot - animation"
    doc.Comment = "Generated by animate_dwd7.py (no need to save). Robot from agbot design, implement from build_dwd7."
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    build_dwd7.build_into(doc, robot, P.drive_z)

    (x0, x1), (y0, y1) = TERRAIN
    ground = Part.makeBox(x1 - x0, y1 - y0, 80.0, V(x0, y0, -80.0))
    lines = []
    y = y0
    while y <= y1:
        lines.append(Part.makeLine(V(x0, y, 0.6), V(x1, y, 0.6)))
        y += 250.0
    x = x0
    while x <= x1:
        lines.append(Part.makeLine(V(x, y0, 0.6), V(x, y1, 0.6)))
        x += 250.0

    def add(name, shape, color, tr=0, visible=True, width=None):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = color
        o.ViewObject.LineColor = color
        o.ViewObject.Transparency = tr
        o.ViewObject.Visibility = visible
        if width:
            o.ViewObject.LineWidth = width
        return o

    add("anim_ground", ground, COLOR["grass"], 55)
    add("anim_ground_lines", Part.makeCompound(lines), COLOR["lines"])
    add("anim_path", Part.makePolygon([V(px, py, 1.5) for px, py in path_points()]), COLOR["path"], width=3)
    for i, (px, py, sc) in enumerate(PLANTS):
        leaves, root = G.dock_plant(px, py, sc, spin=25 * i)
        add("anim_leaves_%d" % i, leaves, COLOR["leaf"])
        add("anim_root_%d" % i, root, COLOR["root"], 20)
        add("anim_crushed_%d" % i, Part.makeCylinder(P.cutter_d / 2, P.depth_std, V(px, py, -P.depth_std)),
            COLOR["soil"], 30, False)
    build_dwd7.set_group_transparency(doc, "Pot", 65)      # cutter visible inside the can
    doc.recompute()
    return doc


def apply_frame(doc, f):
    ox, oy, psi = f["origin"]
    z_axis = V(0, 0, 1)
    doc.getObject("Robot").Placement = App.Placement(V(ox, oy, 0.0), App.Rotation(z_axis, math.degrees(psi)))
    doc.getObject("FL_steered").Placement = App.Placement(V(0, 0, 0), App.Rotation(z_axis, math.degrees(f["dl"])))
    doc.getObject("FR_steered").Placement = App.Placement(V(0, 0, 0), App.Rotation(z_axis, math.degrees(f["dr"])))
    for tag in ("RL", "RR", "FL", "FR"):
        rot = App.Rotation(V(1, 0, 0), math.degrees(f["rolls"][tag] / (P.robot_tire_d / 2)))
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    build_dwd7.set_pose(doc, f["z"], angle=f["angle"])
    for i in range(len(PLANTS)):
        gone = i in f["leaves_gone"]
        doc.getObject("anim_leaves_%d" % i).ViewObject.Visibility = not gone
        treated = i in f["done"]
        doc.getObject("anim_root_%d" % i).ViewObject.Visibility = not treated
        doc.getObject("anim_crushed_%d" % i).ViewObject.Visibility = treated


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_WIDE = ((-3300.0, -3600.0, 2900.0), (0.0, -900.0, 650.0))     # eye offset, target relative to the robot centre
CAM_CLOSE = ((-2000.0, -1150.0, 1150.0), (0.0, -870.0, 380.0))    # target follows the spindle


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def camera_blend(frames, dt=DT):
    """Per frame 0 (wide) .. 1 (close): close during the treatment, wide while driving."""
    work = [1.0 if f["phase"] in ("probe", "plunge", "dwell", "rise", "up") else 0.0 for f in frames]
    out = []
    n = len(work)
    w = max(1, int(round(6 * DT / dt)))       # 1.5 s either side
    for i in range(n):
        lo, hi = max(0, i - w), min(n, i + w + 1)
        out.append(smooth(sum(work[lo:hi]) / (hi - lo)))
    return out


def track_camera(f, s, fov=40.0):
    """Camera stays axis-aligned (so the steering is visible) and follows the robot centre, close up the spindle."""
    import FreeCADGui as Gui
    from pivy import coin
    (e1, t1), (e2, t2) = CAM_WIDE, CAM_CLOSE
    eye = [e1[k] + (e2[k] - e1[k]) * s for k in range(3)]
    tgt = [t1[k] + (t2[k] - t1[k]) * s for k in range(3)]
    ox, oy, _ = f["origin"]
    sx, sy = f["spindle"]
    tgt = (ox + (sx - ox) * s + tgt[0], oy + tgt[1] * (1 - s) + (sy - oy) * s, tgt[2])
    cam = Gui.getDocument(DOC_NAME).ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(tgt[0] + eye[0], tgt[1] + eye[1], tgt[2] + eye[2]))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


def meta(f):
    return {"t": round(f["t"], 2), "phase": f["phase"], "text": TEXT[f["phase"]], "plant": f["plant"] + 1,
            "n_plants": len(PLANTS), "done": len(f["done"]), "spindle_x": round(f["spindle"][0]),
            "off_x": round(f["off_x"]), "to_go": round(f["to_go"]), "heading": round(math.degrees(f["origin"][2]), 1),
            "steer": round(math.degrees(f["delta"]), 1), "steer_l": round(math.degrees(f["dl"]), 1),
            "steer_r": round(math.degrees(f["dr"]), 1), "z": round(f["z"]),
            "depth": round(f["depth"]), "pot_on_ground": f["pot_on_ground"], "rpm": round(f["rpm"]),
            "power": round(f["power"]), "current": round(C.spindle_current(f["power"]), 1), "fz": round(f["fz"]),
            "act_a": round(f["act_a"], 1),
            "wheels": {k: round(v, 1) for k, v in f["wheels"].items()}, "front": round(f["front"]),
            "rear": round(f["rear_kg"])}


def summary(frames=None):
    frames = frames or prepare()
    work = [f for f in frames if f["phase"] in ("plunge", "dwell")]
    wheels = [v for f in frames for v in f["wheels"].values()]
    stops = [f for f in frames if f["phase"] == "probe"]
    i2 = sum(f["act_a"] ** 2 * f["dt"] for f in frames) / frames[-1]["t"]
    allowed = P.act_amp[1] ** 2 * P.act_duty
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 1),
            "time_per_plant_s": round(frames[-1]["t"] / len(PLANTS), 1),
            "spindle_x_range": (round(min(f["spindle"][0] for f in frames)), round(max(f["spindle"][0] for f in frames))),
            "spindle_off_plant_at_stops_mm": round(max(abs(f["off_x"]) + abs(f["to_go"]) for f in stops), 2),
            "heading_max_deg": round(max(abs(math.degrees(f["origin"][2])) for f in frames), 1),
            "steer_max_deg (centre, inner wheel)": (round(max(abs(math.degrees(f["delta"])) for f in frames), 1),
                                                    round(max(max(abs(math.degrees(f["dl"])), abs(math.degrees(f["dr"])))
                                                              for f in frames), 1)),
            "steer_rate_max_deg_s": round(max(math.degrees(f["steer_rate"]) for f in frames), 1),
            "z_range": (round(min(f["z"] for f in frames)), round(max(f["z"] for f in frames))),
            "max_depth": round(max(f["depth"] for f in frames)),
            "power_range_w": (round(min(f["power"] for f in work)), round(max(f["power"] for f in work))),
            "z_force_max_n": round(max(f["fz"] for f in frames)),
            "act_mean_i2_a2 (allowed)": (round(i2, 1), round(allowed, 1)),
            "wheel_kg_range": (round(min(wheels), 1), round(max(wheels), 1)),
            "front_kg_range": (round(min(f["front"] for f in frames)), round(max(f["front"] for f in frames))),
            "plants_done": len(frames[-1]["done"])}


def render_frames(folder, first=0, count=None, size=(720, 480), dt=DT):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames = prepare(dt)
    blend = camera_blend(frames, dt)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.getDocument(DOC_NAME).ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i])
        track_camera(frames[i], blend[i])
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, size=(720, 480), dt=DT):
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 40, size, dt)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=12, loop=False, follow=True):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer
    stop()
    doc = App.getDocument(DOC_NAME)
    frames = prepare()
    blend = camera_blend(frames)
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
            if follow:
                track_camera(frames[i], blend[i])
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))


def check_fit(doc=None):
    """Overlap between the real robot model and the implement in the Z end positions (robot at its start pose)."""
    doc = doc or App.getDocument(DOC_NAME)
    doc.getObject("Robot").Placement = App.Placement()
    out = build_dwd7.check_poses(doc)
    build_dwd7.set_pose(doc, P.drive_z)
    doc.recompute()
    return out
