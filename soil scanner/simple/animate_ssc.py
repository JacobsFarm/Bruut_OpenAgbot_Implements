"""Animation: the Bruut OpenAgbot scans a field with the gamma-ray soil scanner and then takes the calibration samples.

Step 1 - scan: the robot drives 3 lanes 10 m apart at 1.2 m/s with headland half-turns of radius 5 m. Every second
a spectrum is stored: a block of 10 x 1.2 m appears on the ground, coloured by the pH it maps to (red = acid 4.4,
blue = 5.1, as on the Interra map of the maize field).
Step 2 - calibration: after the scan the deviating spots get a calibration sample (blue squares, at least 4 per
field). The robot drives there and the soil sampler in the middle of the robot takes a core at each one; a done
square turns white. The camera follows the robot and ends on the whole map.

Builds a separate document (the robot files in "agbot design" are not changed): robot from build_agbot, scanner from
build_ssc, soil sampler from build_ssa, field, map blocks and sample squares.

Use in FreeCAD:
    import animate_ssc
    animate_ssc.build()
    animate_ssc.play()                               # live, animate_ssc.stop()
    animate_ssc.summary()                            # key figures of the run
    animate_ssc.render_all(r"C:\\temp\\ssc_frames")
    import make_gif_ssc; make_gif_ssc.main(r"C:\\temp\\ssc_frames", r"previews\\animation_scan_and_calibrate.gif")
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ssc_params as P
import ssc_parts as G
import build_ssc

DOC_NAME = "Soil_scanner_on_robot_animation"

# ---------------------------------------------------------------------
# Field, lanes, map
# ---------------------------------------------------------------------
FIELD_X = (0.0, 30000.0)
FIELD_Y = (0.0, 36000.0)
LANE_W = P.lane * 1000.0
BLOCK = P.block_len() * 1000.0
LANES_X = [FIELD_X[0] + LANE_W * (i + 0.5) for i in range(int((FIELD_X[1] - FIELD_X[0]) / LANE_W))]
N_BLOCKS = int(round((FIELD_Y[1] - FIELD_Y[0]) / BLOCK))
REAR = P.robot_axle_y                   # rear axle at y -500 in robot coordinates
AHEAD = P.det_y + REAR                  # detector this far in front of the rear axle
TURN_R = P.turn_r * 1000.0
PH_RANGE = (4.4, 5.1)
PH_COLORS = [(0.80, 0.08, 0.08), (0.93, 0.33, 0.08), (0.98, 0.62, 0.12), (0.98, 0.88, 0.22), (0.72, 0.80, 0.50),
             (0.42, 0.52, 0.85), (0.30, 0.25, 0.72)]

# calibration: after the scan the robot follows straight legs with rounded corners (radius ROUTE_R) and stops on 4
# legs; the probe position at each stop becomes a sample square
CORNERS = [(25000.0, 46000.0), (19000.0, 46000.0), (18000.0, 30000.0), (6000.0, 26000.0), (8000.0, 10000.0), (20000.0, 4000.0)]
ROUTE_END = (27000.0, 8000.0)
ROUTE_R = 2500.0
STOPS = ((3, 0.5), (4, 0.5), (5, 0.5), (6, 0.55))   # (leg, fraction along its straight part)
V_SCAN = P.speed * 1000.0
V_TRANSIT = 1.5 * 1000.0
ACC = 500.0                             # mm/s2
STEP = 25.0                             # mm path resolution
T_CORE = 8.0                            # s per core in the animation: down, up, chute + carousel
SIM_DT = 0.05
FPS = 2                                 # frames per second of real time; the GIF at 10 fps = 5 x speed
HOLD_END = 7.0

COLOR = {"field": (0.64, 0.58, 0.36), "headland": (0.48, 0.60, 0.32), "marker": (0.12, 0.32, 0.88),
         "marker_done": (0.97, 0.97, 0.97)}

_timer = None
_play = {}


def ph_at(x, y):
    """Synthetic pH field (x, y in mm) between 4.4 and 5.1, like the maize field in the webinar."""
    xm, ym = x / 1000.0, y / 1000.0
    v = (4.72 + 0.22 * math.sin(0.16 * xm + 0.6) * math.cos(0.11 * ym - 0.3) + 0.16 * math.sin(0.07 * (xm - ym) + 1.0)
         - 0.006 * (xm - 15.0) + 0.004 * (ym - 18.0))
    return max(PH_RANGE[0], min(PH_RANGE[1] - 1e-6, v))


def ph_bin(ph):
    return min(len(PH_COLORS) - 1, int((ph - PH_RANGE[0]) / 0.1))


def blocks():
    """All map blocks: (lane, k, x0, x1, y0, y1, ph)."""
    out = []
    for i, xc in enumerate(LANES_X):
        for k in range(N_BLOCKS):
            y0 = FIELD_Y[0] + k * BLOCK
            out.append((i, k, xc - LANE_W / 2, xc + LANE_W / 2, y0, y0 + BLOCK, ph_at(xc, y0 + BLOCK / 2)))
    return out


# ---------------------------------------------------------------------
# Path of the rear axle centre: lanes + half-turns, then the calibration route
# ---------------------------------------------------------------------
def _line(a, b):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / STEP))
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]


def _arc(c, r, a0, a1):
    n = max(2, int(abs(a1 - a0) * r / STEP))
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n)]


def _fillet_route(start, corners, end, radius):
    """Straight lines through the corners, each corner rounded with an arc of the given radius. Returns the points
    and, per straight leg, the (first, last) point index (for the sample stops)."""
    pts, legs = [], []
    nodes = [start] + list(corners) + [end]
    prev = start
    for i in range(1, len(nodes) - 1):
        a, c, b = nodes[i - 1], nodes[i], nodes[i + 1]
        u = (c[0] - a[0], c[1] - a[1])
        w = (b[0] - c[0], b[1] - c[1])
        lu, lw = math.hypot(*u), math.hypot(*w)
        u, w = (u[0] / lu, u[1] / lu), (w[0] / lw, w[1] / lw)
        turn = math.atan2(u[0] * w[1] - u[1] * w[0], u[0] * w[0] + u[1] * w[1])
        d = radius * math.tan(abs(turn) / 2.0)
        t1 = (c[0] - u[0] * d, c[1] - u[1] * d)
        i0 = len(pts)
        pts += _line(prev, t1)
        legs.append((i0, len(pts) - 1))
        side = 1.0 if turn > 0 else -1.0
        n = (-u[1] * side, u[0] * side)                 # towards the centre
        cen = (t1[0] + n[0] * radius, t1[1] + n[1] * radius)
        a0 = math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        pts += _arc(cen, radius, a0, a0 + turn)
        prev = (c[0] + w[0] * d, c[1] + w[1] * d)
    i0 = len(pts)
    pts += _line(prev, end) + [end]
    legs.append((i0, len(pts) - 1))
    return pts, legs


def path():
    """Points (x, y) of the rear axle, the index where the scan ends and the indices of the sample stops."""
    x0, x1, x2 = LANES_X
    y_top = FIELD_Y[1] + AHEAD      # rear axle when lane 2 (driving -y) starts with the detector at the top
    y_bot = FIELD_Y[0] - AHEAD      # rear axle when lane 3 (driving +y) starts with the detector at the bottom
    y_end = FIELD_Y[1] - AHEAD + 200.0
    pts = _line((x0, FIELD_Y[0] - AHEAD - 1200.0), (x0, y_top))
    pts += _arc(((x0 + x1) / 2, y_top), TURN_R, math.pi, 0.0)
    pts += _line((x1, y_top), (x1, y_bot))
    pts += _arc(((x1 + x2) / 2, y_bot), TURN_R, math.pi, 2 * math.pi)
    pts += _line((x2, y_bot), (x2, y_end))
    scan_end = len(pts)
    route, legs = _fillet_route((x2, y_end), CORNERS, ROUTE_END, ROUTE_R)
    off = len(pts)
    pts += route
    stops = [off + legs[i][0] + int((legs[i][1] - legs[i][0]) * f) for i, f in STOPS]
    return pts, scan_end, stops


def geometry(pts):
    """Arc length, heading (rad, from +x) and curvature (1/mm, + = left) at every point."""
    n = len(pts)
    s = [0.0] * n
    for i in range(1, n):
        s[i] = s[i - 1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
    th = []
    for i in range(n):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        th.append(math.atan2(b[1] - a[1], b[0] - a[0]))
    k = [0.0] * n
    w = 8
    for i in range(n):
        a, b = max(0, i - w), min(n - 1, i + w)
        if s[b] > s[a]:
            d = (th[b] - th[a] + math.pi) % (2 * math.pi) - math.pi
            k[i] = d / (s[b] - s[a])
    return s, th, k


def _interp(s_list, val, s, angle=False):
    lo, hi = 0, len(s_list) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if s_list[mid] <= s:
            lo = mid
        else:
            hi = mid
    if s_list[hi] == s_list[lo]:
        return val[lo]
    f = (s - s_list[lo]) / (s_list[hi] - s_list[lo])
    if angle:
        d = (val[hi] - val[lo] + math.pi) % (2 * math.pi) - math.pi
        return val[lo] + d * f
    return val[lo] + (val[hi] - val[lo]) * f


def local_to_world(origin, local):
    ox, oy, psi = origin
    lx, ly = local
    return (ox + lx * math.cos(psi) - ly * math.sin(psi), oy + lx * math.sin(psi) + ly * math.cos(psi))


def pose_at(pts_x, pts_y, s_list, th, kap, s):
    rx, ry = _interp(s_list, pts_x, s), _interp(s_list, pts_y, s)
    t = _interp(s_list, th, s, angle=True)
    k = _interp(s_list, kap, s)
    psi = t - math.pi / 2
    origin = (rx + REAR * math.cos(t), ry + REAR * math.sin(t), psi)
    return origin, k


def ackermann(k):
    L, tw = P.robot_wheelbase, P.robot_track
    dl = math.atan(L * k / (1.0 - k * tw / 2.0))
    dr = math.atan(L * k / (1.0 + k * tw / 2.0))
    return dl, dr


WHEELS = {"RL": (-P.robot_wheel_x, -P.robot_axle_y), "RR": (P.robot_wheel_x, -P.robot_axle_y),
          "FL": (-P.robot_wheel_x, P.robot_axle_y), "FR": (P.robot_wheel_x, P.robot_axle_y)}


def sampler_params():
    build_ssc.sampler_module()
    import ssa_params
    return ssa_params


def prepare(fps=FPS):
    """Frames (dicts) of the whole run, sampled at fps (real time)."""
    SP = sampler_params()
    pts, scan_end, stops = path()
    s_list, th, kap = geometry(pts)
    px, py = [p[0] for p in pts], [p[1] for p in pts]
    s_scan_end = s_list[scan_end - 1]
    s_stops = [s_list[i] for i in stops]
    s_end = s_list[-1]
    blks = blocks()
    # sample squares where the probe stands at each stop
    markers = []
    for ss in s_stops:
        o, _ = pose_at(px, py, s_list, th, kap, ss)
        markers.append(local_to_world(o, (0.0, SP.probe_y)))
    frames = []
    s, v, t = 0.0, 0.0, 0.0
    revealed = set()
    rolls = {k: 0.0 for k in WHEELS}
    prev_w = None
    stop_i = 0
    dwell = None                       # time into the sampling cycle
    done = 0
    next_frame = 0.0
    t_done = None
    while True:
        phase = "scan" if s < s_scan_end else "transit"
        tip, chute = SP.tip_park, 0.0
        if dwell is not None:
            phase = "sample"
            f = dwell / T_CORE
            down, up = 0.4, 0.8
            if f < down:
                tip = SP.tip_park - (SP.tip_park + SP.depth_max) * (f / down)
            elif f < up:
                tip = -SP.depth_max + (SP.tip_park + SP.depth_max) * ((f - down) / (up - down))
            chute = SP.chute_aside_deg if f < up else SP.chute_aside_deg * (1.0 - (f - up) / (1.0 - up))
        elif t_done is not None:
            phase = "done"
        origin, k = pose_at(px, py, s_list, th, kap, s)
        wheels = {tag: local_to_world(origin, loc) for tag, loc in WHEELS.items()}
        if prev_w is not None:
            for tag, (wx, wy) in wheels.items():
                rolls[tag] += math.hypot(wx - prev_w[tag][0], wy - prev_w[tag][1])
        prev_w = wheels
        det = local_to_world(origin, (0.0, P.det_y))
        if phase == "scan":
            for b in blks:
                lane, kk, x0, x1, y0, y1, ph = b
                if (lane, kk) in revealed or not (x0 < det[0] < x1):
                    continue
                heading_up = math.cos(origin[2]) > 0
                if (heading_up and det[1] >= y1) or (not heading_up and det[1] <= y0):
                    if abs(math.cos(origin[2])) > 0.99:            # straight in the lane
                        revealed.add((lane, kk))
        if t + 1e-9 >= next_frame:
            dl, dr = ackermann(k)
            cur = None
            if FIELD_X[0] < det[0] < FIELD_X[1] and FIELD_Y[0] < det[1] < FIELD_Y[1]:
                cur = round(ph_at(det[0], det[1]), 2)
            frames.append({"t": round(t, 2), "phase": phase, "origin": origin, "dl": dl, "dr": dr,
                           "rolls": dict(rolls), "revealed": sorted(revealed), "v": v, "tip": tip, "chute": chute,
                           "carousel": done + (0 if dwell is None else min(1.0, max(0.0, (dwell / T_CORE - 0.8) / 0.2))),
                           "markers": markers if phase != "scan" else [], "done": done, "ph": cur,
                           "radius_m": round(1.0 / abs(k) / 1000.0, 1) if abs(k) > 1e-7 else None})
            next_frame += 1.0 / fps
        # advance
        if t_done is not None:
            if t - t_done >= HOLD_END:
                break
        elif dwell is not None:
            dwell += SIM_DT
            if dwell >= T_CORE:
                dwell = None
                done += 1
                stop_i += 1
        else:
            if phase == "scan":
                v_max, s_goal = V_SCAN, None
            else:
                v_max = V_TRANSIT
                s_goal = s_stops[stop_i] if stop_i < len(s_stops) else s_end
            if s_goal is not None:
                v_max = min(v_max, math.sqrt(max(0.0, 2 * ACC * (s_goal - s))))
            v = min(v_max, v + ACC * SIM_DT) if v < v_max else v_max
            s = min(s + v * SIM_DT, s_end)
            if s_goal is not None and s_goal - s < 2.0:
                s, v = s_goal, 0.0
                if stop_i < len(s_stops):
                    dwell = 0.0
                else:
                    t_done = t
        t += SIM_DT
    return frames


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def build():
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Soil scanner on robot - animation"
    _shown.pop(DOC_NAME, None)
    doc.Comment = "Generated by animate_ssc.py. Robot from agbot design, scanner from build_ssc, sampler from build_ssa."
    robot = build_ssc.build_robot(doc)
    build_ssc.build_into(doc, robot)
    build_ssc.sampler_module().build_into(doc, robot)

    def add(name, shape, color, transp=0):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = color
        o.ViewObject.Transparency = transp
        return o
    add("anim_headland", G.box_span((-14000.0, 44000.0), (-14000.0, 52000.0), (-60.0, -20.0)), COLOR["headland"])
    add("anim_field", G.box_span(FIELD_X, FIELD_Y, (-20.0, 0.0)), COLOR["field"])
    for b in range(len(PH_COLORS)):
        add("anim_map_%d" % b, Part.Shape(), PH_COLORS[b])
    for i in range(len(STOPS)):
        add("anim_sample_%d" % i, Part.Shape(), COLOR["marker"])
    doc.recompute()
    return doc


_shown = {}


def apply_frame(doc, f):
    ox, oy, psi = f["origin"]
    z_axis = V(0, 0, 1)
    doc.getObject("Robot").Placement = App.Placement(V(ox, oy, 0.0), App.Rotation(z_axis, math.degrees(psi)))
    doc.getObject("FL_steered").Placement = App.Placement(V(0, 0, 0), App.Rotation(z_axis, math.degrees(f["dl"])))
    doc.getObject("FR_steered").Placement = App.Placement(V(0, 0, 0), App.Rotation(z_axis, math.degrees(f["dr"])))
    for tag in WHEELS:
        rot = App.Rotation(V(1, 0, 0), -math.degrees(f["rolls"][tag] / (P.robot_tire_d / 2)))
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    ssa = build_ssc.sampler_module()
    ssa.set_pose(f["tip"], f["chute"], f["carousel"], doc=doc)
    key = (doc.Name, len(f["revealed"]))
    if _shown.get(doc.Name) != key:
        _shown[doc.Name] = key
        rev = set(tuple(r) for r in f["revealed"])
        bins = [[] for _ in PH_COLORS]
        for lane, kk, x0, x1, y0, y1, ph in blocks():
            if (lane, kk) in rev:
                bins[ph_bin(ph)].append(G.map_block(x0 + 10, x1 - 10, y0 + 10, y1 - 10))
        for b, shapes in enumerate(bins):
            doc.getObject("anim_map_%d" % b).Shape = Part.makeCompound(shapes) if shapes else Part.Shape()
    for i in range(len(STOPS)):
        o = doc.getObject("anim_sample_%d" % i)
        if f["markers"]:
            if o.Shape.isNull():
                mx, my = f["markers"][i]
                o.Shape = G.sample_marker(mx, my)
            o.ViewObject.ShapeColor = COLOR["marker_done"] if i < f["done"] else COLOR["marker"]
        elif not o.Shape.isNull():
            o.Shape = Part.Shape()


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_FAR = ((-5000.0, -6500.0, 5200.0), (0.0, 1200.0, 0.0))     # eye and target offset from the robot (scan)
CAM_NEAR = ((-2600.0, -3300.0, 2600.0), (0.0, 0.0, 300.0))     # at a sample stop
CAM_END = ((15000.0, -16000.0, 30000.0), (15000.0, 17000.0, 0.0))  # world: the whole map at the end


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def camera_track(frames):
    """Eye and target per frame: far behind while scanning, close at the stops, the whole field at the end."""
    out = []
    near = 0.0
    t_end = frames[-1]["t"]
    for f in frames:
        goal = 1.0 if f["phase"] == "sample" else 0.0
        near += (goal - near) * 0.35
        ox, oy, _ = f["origin"]
        eye = [(ox, oy, 0.0)[i] + CAM_FAR[0][i] + (CAM_NEAR[0][i] - CAM_FAR[0][i]) * near for i in range(3)]
        tgt = [(ox, oy, 0.0)[i] + CAM_FAR[1][i] + (CAM_NEAR[1][i] - CAM_FAR[1][i]) * near for i in range(3)]
        e = smooth((f["t"] - (t_end - HOLD_END)) / (HOLD_END * 0.6))
        eye = [eye[i] + (CAM_END[0][i] - eye[i]) * e for i in range(3)]
        tgt = [tgt[i] + (CAM_END[1][i] - tgt[i]) * e for i in range(3)]
        out.append((eye, tgt))
    return out


def set_cam(eye, tgt, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    cam = Gui.getDocument(DOC_NAME).ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(*eye))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(50.0)
    cam.farDistance.setValue(150000.0)


def meta(f):
    return {"t": f["t"], "phase": f["phase"], "v": round(f["v"] / 1000.0, 2), "blocks": len(f["revealed"]),
            "n_blocks": len(LANES_X) * N_BLOCKS, "done": f["done"], "n_samples": len(STOPS), "ph": f["ph"],
            "tip": round(f["tip"]), "radius_m": f["radius_m"]}


def summary(frames=None):
    frames = frames or prepare()
    pts, scan_end, stops = path()
    s_list, th, kap = geometry(pts)
    k_scan = max(abs(k) for k in kap[:scan_end])
    k_all = max(abs(k) for k in kap)
    t_scan = max(f["t"] for f in frames if f["phase"] == "scan")
    ph = [b[6] for b in blocks()]
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 1), "scan_s": round(t_scan, 1),
            "blocks": len(frames[-1]["revealed"]), "of_blocks": len(LANES_X) * N_BLOCKS,
            "path_m": round(s_list[-1] / 1000.0, 1), "scan_path_m": round(s_list[scan_end - 1] / 1000.0, 1),
            "min_radius_scan_m": round(1.0 / k_scan / 1000.0, 1), "min_radius_m": round(1.0 / k_all / 1000.0, 1),
            "max_steer_deg": round(math.degrees(max(max(abs(f["dl"]), abs(f["dr"])) for f in frames)), 1),
            "samples": frames[-1]["done"], "ph_range": (round(min(ph), 2), round(max(ph), 2)),
            "markers": [(round(x), round(y)) for x, y in frames[-1]["markers"]],
            "marker_inside_field": all(FIELD_X[0] + 500 < x < FIELD_X[1] - 500 and FIELD_Y[0] + 500 < y < FIELD_Y[1] - 500
                                       for x, y in frames[-1]["markers"])}


def render_frames(folder, first=0, count=None, fps=FPS, size=(720, 480), frames=None):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames = frames or prepare(fps)
    cams = camera_track(frames)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.getDocument(DOC_NAME).ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i])
        set_cam(*cams[i])
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, fps=FPS, size=(720, 480)):
    build()
    App.setActiveDocument(DOC_NAME)
    frames = prepare(fps)
    _shown.clear()
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 60, fps, size, frames)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=FPS, loop=False, follow=True, speed=5.0):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer
    stop()
    doc = App.getDocument(DOC_NAME)
    frames = prepare(fps)
    cams = camera_track(frames)
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
                set_cam(*cams[i])
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / (fps * speed)))
