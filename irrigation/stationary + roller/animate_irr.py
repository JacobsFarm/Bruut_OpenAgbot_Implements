"""Animation: one strip with the irrigation hose reel on the Bruut OpenAgbot.

The pump stands at the ditch, the hose is coupled to the hydrant valve. The robot drives into the field and lays the
hose (the first 20 m, the lead, curve over the headland to the start of the strip, 4 m to the right of the previous
strip). The pump starts, the hose fills, water leaves every 2 m and spreads over a strip of ~4 m. After the gift the
pump stops, the valve opens to the drain and the hose runs empty. The robot drives back in reverse and winds the hose;
the pinch rollers squeeze it flat.

Time is compressed per phase (the caption gives the real time); durations, flows and speeds come from irr_calc.

Builds a separate document (the robot files in "agbot design" are not changed): robot from build_agbot, reel from
build_irr, grass, ditch, pump unit, the hose in the field, the outlets and the wet strip.

Use in FreeCAD:
    import animate_irr
    animate_irr.build()                              # build the document
    animate_irr.play()                               # play live, animate_irr.stop()
    animate_irr.summary()                            # key figures of the run
    animate_irr.render_all(r"C:\\temp\\irr_frames")
    import make_gif_irr; make_gif_irr.main(r"C:\\temp\\irr_frames", r"previews\\animation_one_strip.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import irr_params as P
import irr_calc as C
import irr_parts as G
import build_irr

DOC_NAME = "Irrigation_on_robot_animation"

# ---------------------------------------------------------------------
# Field: hydrant at the origin of the world, ditch behind it (-y), strips to +y
# ---------------------------------------------------------------------
HYDRANT = (0.0, 40.0)           # hose coupling (world x, y)
STRIP = 1                       # this strip is 1 x strip_w to the right of the hydrant; strip 0 is already done
DITCH_Y = (-4000.0, -1800.0)
WATER_Z = -850.0
BANK_Y = -1200.0
FLOOR_Z = -15.0                 # grass drawn 15 mm low: keeps the flat hose and the wet patches visible from afar

FRAMES = {"start": 5, "lay_out": 50, "fill": 12, "irrigate": 26, "drain": 8, "roll_up": 50, "done": 14}
HOSE_STEP = 2000.0              # mm, sampling of the hose in the field
COLOR = {"grass": (0.47, 0.62, 0.30), "wet": (0.27, 0.42, 0.30), "wet_old": (0.36, 0.50, 0.31),
         "water": (0.25, 0.45, 0.70), "bank": (0.45, 0.40, 0.30), "pump": (0.80, 0.10, 0.10),
         "engine": (0.25, 0.25, 0.27), "skid": (0.30, 0.30, 0.32), "valve": (0.10, 0.30, 0.75),
         "hose": (0.10, 0.35, 0.80), "outlet": (0.10, 0.10, 0.10), "suction": (0.15, 0.15, 0.15)}

_timer = None
_play = {}


# ---------------------------------------------------------------------
# Path of the hose / robot (s in mm from the hydrant)
# ---------------------------------------------------------------------
def strip_x():
    return HYDRANT[0] + STRIP * P.strip_w * 1000.0


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def path(s):
    """(x, y, heading) at distance s along the hose; heading in rad, 0 = +y, positive = to the left (about z)."""
    lead = P.lead_len * 1000.0
    dx = strip_x() - HYDRANT[0]
    x = HYDRANT[0] + dx * _smooth(s / lead)
    t = max(0.0, min(1.0, s / lead))
    slope = dx * 6.0 * t * (1.0 - t) / lead if s < lead else 0.0
    return x, HYDRANT[1] + s, -math.atan(slope)


def run_len():
    """Length (m) of the hose on the robot between the coil and the ground (full reel)."""
    pts = G.run_points(P.hose_len)
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:])) / 1000.0


GROUND_Y = P.low_y - 650.0      # local y where the hose touches the ground (G.run_points default)


def robot_pose(s_c):
    """Robot centre and heading with the hose touching the ground at s_c."""
    x, y, h = path(s_c - GROUND_Y)
    return x, y, h


def l_reel(s_c):
    return P.hose_len - s_c / 1000.0 - run_len()


def s_end():
    return (P.hose_len - P.reel_reserve - run_len()) * 1000.0


def outlets_world(s_max):
    out = []
    for s in C.outlets(P.hose_len):
        s_mm = s * 1000.0
        if s_mm > s_max:
            break
        x, y, h = path(s_mm)
        out.append((x, y, s_mm, h))
    return out


# ---------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------
def segments():
    c = C.cycle()
    return [("start", 20.0), ("lay_out", c["lay_out"]), ("fill", c["fill"]), ("irrigate", c["irrigate"]),
            ("drain", c["drain"]), ("roll_up", c["roll_up"]), ("done", 30.0)]


def wind_profile(n=400):
    """s_c as a function of time while winding (speed limited by the reel motor at a small coil)."""
    se = s_end()
    ts, ss = [0.0], [se]
    t = 0.0
    for i in range(n):
        s_a = se * (1.0 - i / float(n))
        ds = se / n
        t += ds / 1000.0 / C.wind_speed(l_reel(s_a))
        ts.append(t)
        ss.append(se * (1.0 - (i + 1) / float(n)))
    return ts, ss


def prepare():
    d = C.design()
    se = s_end()
    wt, ws = wind_profile()
    frames = []
    t0 = 0.0
    spin = 0.0
    prev_s = 0.0
    r_max = P.strip_w * 1000.0 / 2.0
    for phase, dur in segments():
        n = FRAMES[phase]
        for k in range(n):
            f = k / float(max(1, n - 1)) if phase != "start" else 0.0
            t = dur * f
            s_c, v = 0.0, 0.0
            hose = "flat"
            front = 0.0
            wet = 0.0
            pump = False
            if phase == "lay_out":
                s_c = se * f
                v = P.v_layout
            elif phase in ("fill", "irrigate", "drain"):
                s_c = se
            elif phase == "roll_up":
                i = min(range(len(wt)), key=lambda j: abs(wt[j] - wt[-1] * f))
                s_c = ws[i]
                v = -C.wind_speed(l_reel(s_c))
            if phase == "fill":
                hose, front, pump = "fill", se * f, True
                wet = 0.03 * f
            elif phase == "irrigate":
                hose, front, pump = "full", se, True
                wet = 0.03 + 0.97 * f
            elif phase == "drain":
                hose = "wet" if f < 0.85 else "flat"
                wet = 1.0
            elif phase in ("roll_up", "done"):
                wet = 1.0
            spin += (s_c - prev_s) / (P.robot_tire_d / 2.0)
            prev_s = s_c
            given = P.gift * min(1.0, max(0.0, wet))
            radius = r_max * min(1.0, math.sqrt(max(0.0, wet) / 0.3)) if wet > 0 else 0.0
            frames.append({"phase": phase, "t": t0 + t, "t_phase": t, "dur": dur, "s_c": s_c, "v": v,
                           "l_reel": l_reel(s_c), "spin": spin, "hose": hose, "front": front, "pump": pump,
                           "wet": wet, "radius": radius, "given": given, "q": d["q"] if pump else 0.0,
                           "h_in": d["h_in"] if pump else 0.0})
        t0 += dur
    return frames


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
SHADED = ("anim_wet", "anim_floor", "anim_bank", "anim_water")


def _add(doc, name, shape, color, transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeCompound(shape) if isinstance(shape, list) else shape
    obj.ViewObject.ShapeColor = COLOR[color]
    obj.ViewObject.Transparency = transparency
    if name.startswith(SHADED):
        obj.ViewObject.DisplayMode = "Shaded"       # no edge lines on the wet patches
    return obj


def build():
    if build_irr.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_irr.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Irrigation hose reel on robot - animation"
    doc.Comment = "Generated by animate_irr.py. Robot from agbot design, hose reel from build_irr."
    robot = build_irr.build_robot(doc)
    build_irr.build_into(doc, robot, P.hose_len, tail_y=None)
    x0, x1 = -8000.0, 16000.0
    _add(doc, "anim_floor", G.box_span((x0, x1), (BANK_Y, 165000.0), (-60.0, FLOOR_Z)), "grass")
    bank = G.poly_yz([(BANK_Y, 0.0), (DITCH_Y[1], WATER_Z - 100.0), (DITCH_Y[1], WATER_Z - 300.0),
                      (BANK_Y, -300.0)], x0, x1 - x0)
    _add(doc, "anim_bank", bank, "bank")
    _add(doc, "anim_water", G.box_span((x0, x1), DITCH_Y, (WATER_Z - 300.0, WATER_Z)), "water", 20)
    pu = G.pump_unit(*HYDRANT[:1], HYDRANT[1] - 40.0)
    for key, color in (("skid", "skid"), ("pump", "pump"), ("engine", "engine"), ("valve", "valve"), ("drain", "valve")):
        _add(doc, "anim_pump_" + key, pu[key], color)
    _add(doc, "anim_suction", G.suction_hose(HYDRANT[0], HYDRANT[1] - 40.0, DITCH_Y[1] - 600.0, WATER_Z), "suction")
    # strip 0 (done earlier): old wet strip and nothing else
    old = [G.wet_patch(HYDRANT[0], HYDRANT[1] + s * 1000.0, P.strip_w * 500.0) for s in C.outlets()]
    _add(doc, "anim_wet_old", old, "wet_old")
    for name, color in (("anim_hose", "hose"), ("anim_hose_full", "hose"), ("anim_outlets", "outlet"),
                        ("anim_wet", "wet")):
        _add(doc, name, Part.Shape(), color)
    doc.recompute()
    return doc


def _hose_points(s_from, s_to):
    if s_to - s_from < 1.0:
        return []
    n = max(1, int(math.ceil((s_to - s_from) / HOSE_STEP)))
    return [path(s_from + (s_to - s_from) * i / n)[:2] for i in range(n + 1)]


def apply_frame(doc, f):
    x, y, h = robot_pose(f["s_c"])
    doc.getObject("Robot").Placement = App.Placement(V(x, y, 0.0), App.Rotation(V(0, 0, 1), math.degrees(h)))
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    lr = f["l_reel"]
    doc.getObject("Reel").Placement = build_irr.reel_placement(build_irr.reel_angle_deg(lr))
    doc.getObject("hose_coil").Shape = G.coil(lr)
    doc.getObject("hose_run").Shape = Part.makeCompound(G.hose_run(lr))
    s_c = f["s_c"]
    flat, full = [], []
    if f["hose"] in ("fill", "full"):
        full = G.hose_ground(_hose_points(0.0, min(f["front"], s_c)), "full")
        flat = G.hose_ground(_hose_points(min(f["front"], s_c), s_c), "flat")
    else:
        flat = G.hose_ground(_hose_points(0.0, s_c), "wet" if f["hose"] == "wet" else "flat")
    doc.getObject("anim_hose").Shape = Part.makeCompound(flat) if flat else Part.Shape()
    doc.getObject("anim_hose_full").Shape = Part.makeCompound(full) if full else Part.Shape()
    outs = outlets_world(s_c)
    marks = []
    for ox, oy, s_mm, oh in outs:
        marks += G.outlet_marks([(ox, oy, math.sin(oh), -math.cos(oh))])
    doc.getObject("anim_outlets").Shape = Part.makeCompound(marks) if marks else Part.Shape()
    wet = []
    if f["radius"] > 1.0:
        front = f["front"] if f["phase"] == "fill" else 1e9
        wet = [G.wet_patch(ox, oy, f["radius"]) for ox, oy, s_mm, oh in outlets_world(P.hose_len * 1000.0)
               if s_mm <= front]
    doc.getObject("anim_wet").Shape = Part.makeCompound(wet) if wet else Part.Shape()


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_FOLLOW = ((-3600.0, -5200.0, 2600.0), (0.0, -1200.0, 500.0))     # relative to the robot (eye, target)
CAM_OVER = ((-6000.0, -5000.0, 9000.0), (2500.0, 19000.0, 0.0))          # relative to the start of the strip


def overview_weight(f, frames):
    """0 = follow the robot, 1 = overview of the strip."""
    i = frames.index(f)
    w = []
    for g in frames:
        w.append(1.0 if g["phase"] in ("fill", "irrigate", "drain") else 0.0)
    lo, hi = max(0, i - 4), min(len(frames), i + 5)
    return sum(w[lo:hi]) / float(hi - lo)


def track_camera(f, frames, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    x, y, _ = robot_pose(f["s_c"])
    s = _smooth(overview_weight(f, frames))
    eye_a = [x + CAM_FOLLOW[0][0], y + CAM_FOLLOW[0][1], CAM_FOLLOW[0][2]]
    tgt_a = [x + CAM_FOLLOW[1][0], y + CAM_FOLLOW[1][1], CAM_FOLLOW[1][2]]
    sx, sy = strip_x(), HYDRANT[1]
    eye_b = [sx + CAM_OVER[0][0], sy + CAM_OVER[0][1], CAM_OVER[0][2]]
    tgt_b = [sx + CAM_OVER[1][0], sy + CAM_OVER[1][1], CAM_OVER[1][2]]
    eye = [eye_a[k] + (eye_b[k] - eye_a[k]) * s for k in range(3)]
    tgt = [tgt_a[k] + (tgt_b[k] - tgt_a[k]) * s for k in range(3)]
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(*eye))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(1500.0)          # depth precision: the flat hose lies 2 mm above the grass
    cam.farDistance.setValue(250000.0)


STATE = {"start": "hose coupled to the hydrant, pump off",
         "lay_out": "laying out: the robot drives into the field, the hose pays out and lies still",
         "fill": "pump on: the hose fills, the pinch rollers keep the reel dry",
         "irrigate": "irrigating: every 2 m an outlet floods the strip",
         "drain": "pump off, valve to drain: the hose runs empty",
         "roll_up": "winding: the robot reverses, the pinch rollers squeeze the hose flat",
         "done": "strip done; next strip 4 m to the right"}


def meta(f):
    return {"t": round(f["t"], 1), "phase": f["phase"], "state": STATE[f["phase"]], "s_c": round(f["s_c"] / 1000.0, 1),
            "l_reel": round(f["l_reel"], 1), "v": round(f["v"], 2), "q": round(f["q"], 2), "h_in": round(f["h_in"], 2),
            "given": round(f["given"], 1), "pump": f["pump"], "hose_len": P.hose_len, "gift": P.gift,
            "coil_d": round(2 * C.coil_r(max(f["l_reel"], 0.0))), "strip": STRIP + 1,
            "strip_w": P.strip_w, "dur": round(f["dur"], 1), "t_phase": round(f["t_phase"], 1)}


def summary(frames=None):
    frames = frames or prepare()
    segs = segments()
    return {"frames": len(frames), "real_time_h": round(sum(d for _, d in segs) / 3600.0, 2),
            "phases_min": {k: round(d / 60.0, 1) for k, d in segs}, "run_len_m": round(run_len(), 2),
            "s_end_m": round(s_end() / 1000.0, 1), "l_reel_min": round(min(f["l_reel"] for f in frames), 2),
            "l_reel_max": round(max(f["l_reel"] for f in frames), 2),
            "outlets_on_ground": len(outlets_world(s_end())),
            "max_heading_deg": round(max(abs(math.degrees(path(s)[2])) for s in range(0, 30000, 500)), 1)}


def render_frames(folder, first=0, count=None, size=(720, 480)):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames = prepare()
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


def render_all(folder, size=(720, 480)):
    build()
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 40, size)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=8, loop=False, follow=True):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer
    stop()
    doc = App.getDocument(DOC_NAME)
    frames = prepare()
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
    _timer.start(int(1000 / fps))


def check_fit(doc=None, tol=1.0):
    """Overlap between the robot model and the reel in the animation document, reel full and nearly empty."""
    doc = doc or App.getDocument(DOC_NAME)
    out = {}
    for lr in (P.hose_len - run_len(), P.reel_reserve):
        doc.getObject("Reel").Placement = build_irr.reel_placement(build_irr.reel_angle_deg(lr))
        doc.recompute()
        hits = build_irr.check_interference(doc, tol)
        if hits:
            out[lr] = hits
    return out
