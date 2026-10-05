"""Animatie: de eenvoudige toediener versie 2 (schijf + mes) achter de Bruut OpenAgbot over dezelfde hobbelige
strook als de geavanceerde variant en versie 1.

Bouwt een apart document (de robotbestanden in "agbot design" worden niet aangepast):
robot uit build_agbot + toediener uit build_lfs2 + golvend maaiveld (lfs2_ground.terrain).
Per frame (rekenregels in lfs2_ground.py):
- robot rust met 4 wielen op het maaiveld (vlak door de wielpunten: hoogte, stampen, rollen);
- het hefraam zakt tot het eerste dieptewiel de grond raakt, binnen het bereik van actuator en langgat;
- schijven en messen hangen star aan de balk; achter de messen verschijnen de sleuven, schijven en dieptewielen
  draaien mee.

Gebruik in FreeCAD:
    import animate_lfs2
    animate_lfs2.build()                       # document opbouwen
    animate_lfs2.play()                        # live afspelen, animate_lfs2.stop()
    animate_lfs2.render_frames(r"C:\\temp\\lfs_frames", 0, 30)   # in stukken van ~30 frames renderen
    import make_gif_lfs2; make_gif_lfs2.main(r"C:\\temp\\lfs_frames", r"previews\\animation_strip_ground_following.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lfs2_params as P
import lfs2_kin as K
import lfs2_parts as G
import lfs2_ground as GR
import lfs2_calc as C
import build_lfs2

FOLDER = os.path.dirname(os.path.abspath(__file__))
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbot design")
DOC_NAME = "LFS2_on_robot_animation"
FPS = 10

TERRAIN_X = (-1500.0, 1500.0)
TERRAIN_Y = (-2600.0, 9400.0)
TERRAIN_OUTER = (-6000.0, -4000.0, -2600.0, -2000.0, 2000.0, 2600.0, 4000.0, 6000.0)
COLOR = {"grass": (0.45, 0.62, 0.31), "lines": (0.35, 0.50, 0.24), "slot": (0.20, 0.13, 0.08)}
SLOT_HALF = 6.0
PUMP_MIN_DEPTH = 10.0           # pomp aan als alle messen dieper zitten dan dit en de robot op snelheid is

_timer = None
_play = {}
_cache = {"act": {}, "hose": {}}
_base = {}


# ---------------------------------------------------------------------
# Maaiveld en sleuven
# ---------------------------------------------------------------------
def terrain_shapes(step=100.0, line_step=250.0):
    fine = [TERRAIN_X[0] + i * step for i in range(int((TERRAIN_X[1] - TERRAIN_X[0]) / step) + 1)]
    xs = sorted(set(fine + list(TERRAIN_OUTER)))
    ys = [TERRAIN_Y[0] + i * step for i in range(int((TERRAIN_Y[1] - TERRAIN_Y[0]) / step) + 1)]
    surf = Part.BSplineSurface()
    surf.interpolate([[V(x, y, GR.terrain(x, y)) for y in ys] for x in xs])
    face = surf.toShape()
    lines = []
    x_line = [xs[0] + i * step for i in range(int((xs[-1] - xs[0]) / step) + 1)]
    y = TERRAIN_Y[0]
    while y <= TERRAIN_Y[1] + 1e-6:
        c = Part.BSplineCurve()
        c.interpolate([V(x, y, GR.terrain(x, y) + 1.5) for x in x_line])
        lines.append(c.toShape())
        y += line_step
    x = xs[0]
    while x <= xs[-1] + 1e-6:
        c = Part.BSplineCurve()
        c.interpolate([V(x, yy, GR.terrain(x, yy) + 1.5) for yy in ys])
        lines.append(c.toShape())
        x += line_step
    return face, Part.makeCompound(lines)


def slot_ribbon(points):
    if len(points) < 2:
        return None
    pts = points[::2] + ([points[-1]] if len(points) % 2 == 0 else [])
    left = Part.makePolygon([V(x - SLOT_HALF, y, GR.terrain(x - SLOT_HALF, y) + 2.0) for x, y in pts])
    right = Part.makePolygon([V(x + SLOT_HALF, y, GR.terrain(x + SLOT_HALF, y) + 2.0) for x, y in pts])
    return Part.makeRuledSurface(left, right)


# ---------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------
def robot_placement(f):
    rot = App.Rotation(V(1, 0, 0), f["pitch"]).multiply(App.Rotation(V(0, 1, 0), f["roll"]))
    return App.Placement(V(0.0, f["y"], f["pose"].c), rot)


def prepare(fps=FPS):
    frames = GR.prepare(fps)
    dist = 0.0
    spin_robot = 0.0
    spin_wheel = [0.0 for _ in P.gw_x]
    spin_disc = [0.0 for _ in P.row_x]
    applied = 0.0
    slots = [[] for _ in P.row_x]
    prev = frames[0]
    flow = C.orifice_flow_l_min(P.orifice_d) * len(P.row_x)
    for f in frames:
        ds = f["y"] - prev["y"]
        dt = f["t"] - prev["t"]
        prev = f
        dist += ds
        spin_robot += ds / P.robot_tire_d * 2.0
        for i, g in enumerate(f["wheel_gap"]):
            if g < 5.0:
                spin_wheel[i] += ds / (P.gw_d / 2.0)
        for i, r in enumerate(f["rows"]):
            if r["depth"] > 2.0:
                slots[i].append(r["xy"])
            if r["disc"] > 0.0:
                spin_disc[i] += ds / (P.disc_d / 2.0)
        pump = (f["phase"] in ("lower", "work") and f["v"] >= 0.8 * GR.SPEED
                and min(r["depth"] for r in f["rows"]) > PUMP_MIN_DEPTH)
        if pump:
            applied += flow * dt / 60.0
        f.update({"dist": dist, "spin_robot": spin_robot, "spin_wheel": list(spin_wheel), "pump": pump,
                  "spin_disc": list(spin_disc),
                  "applied": applied, "slots": [len(s) for s in slots], "flow": flow if pump else 0.0})
    return frames, slots


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def build():
    if AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, AGBOT_FOLDER)
    import build_agbot as BA
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "LFS on robot - animation"
    doc.Comment = "Gegenereerd door animate_lfs2.py (niet opslaan nodig). Robot uit agbot design, toediener uit build_lfs2."
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    build_lfs2.build_into(doc, robot, 0.0, build_lfs2.translation(0.0, P.robot_mount_y, 0.0))

    face, lines = terrain_shapes()
    for name, shape, color, extra in (("anim_terrain", face, COLOR["grass"], None),
                                      ("anim_terrain_lines", lines, COLOR["lines"], 1.0)):
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = color
        obj.ViewObject.Deviation = 0.03
        if extra:
            obj.ViewObject.LineWidth = extra
    for i in range(len(P.row_x)):
        obj = doc.addObject("Part::Feature", "anim_slot_%d" % (i + 1))
        obj.ViewObject.ShapeColor = COLOR["slot"]
        obj.ViewObject.LineColor = COLOR["slot"]
    doc.recompute()
    record_base(doc)
    return doc


SPIN_WHEEL = ("tire", "rim")
SPIN_DISC = ("disc", "hub")


def record_base(doc):
    _base.clear()
    for n in range(len(P.gw_x)):
        for k in SPIN_WHEEL:
            name = "W%d_%s" % (n + 1, k)
            _base[name] = doc.getObject(name).Placement
    for n in range(len(P.row_x)):
        for k in SPIN_DISC:
            name = "K%d_%s" % (n + 1, k)
            _base[name] = doc.getObject(name).Placement
    for c in _cache.values():
        c.clear()


def actuator_shapes(psi, length):
    key = (round(psi, 2), round(length, 1))
    if key not in _cache["act"]:
        f = K.frame_pin(key[0])
        pin = K.slot_pin(key[0], key[1])
        body, rod = G.actuator(f, pin)
        _cache["act"][key] = (body, rod, G.act_pin_bolt(pin, P.act_lug_gap), G.act_pin_bolt(f, P.act_lug_gap))
    return _cache["act"][key]


def hose_shape(i, psi):
    key = (i, round(psi * 4.0) / 4.0)
    if key not in _cache["hose"]:
        _cache["hose"][key] = G.outlet_hose(i, P.row_x[i], key[1])
    return _cache["hose"][key]


def apply_frame(doc, f, slots=None):
    doc.getObject("Robot").Placement = robot_placement(f)
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin_robot"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    psi = f["psi"]
    doc.getObject("Swing_frame").Placement = build_lfs2.lift_placement(psi)
    body, rod, pin_slot, pin_frame = actuator_shapes(psi, f["length"])
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod
    doc.getObject("act_pin_slot").Shape = pin_slot
    doc.getObject("act_pin_frame").Shape = pin_frame
    for i in range(len(P.row_x)):
        doc.getObject("hose_%d" % (i + 1)).Shape = hose_shape(i, psi)
    for n in range(len(P.gw_x)):
        ang = -math.degrees(f["spin_wheel"][n])
        for k in SPIN_WHEEL:
            name = "W%d_%s" % (n + 1, k)
            doc.getObject(name).Placement = App.Placement(
                V(0, 0, 0), App.Rotation(V(1, 0, 0), ang), V(0, P.gw_axle[0], P.gw_axle[1])).multiply(_base[name])
    for n in range(len(P.row_x)):
        ang = -math.degrees(f["spin_disc"][n])
        for k in SPIN_DISC:
            name = "K%d_%s" % (n + 1, k)
            doc.getObject(name).Placement = App.Placement(
                V(0, 0, 0), App.Rotation(V(1, 0, 0), ang), V(0, P.disc_center[0], P.disc_center[1])).multiply(_base[name])
    if slots is not None:
        for i, s in enumerate(slots):
            shape = slot_ribbon(s[:f["slots"][i]])
            doc.getObject("anim_slot_%d" % (i + 1)).Shape = shape if shape is not None else Part.Shape()


def reset(doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    frames, slots = prepare()
    apply_frame(doc, frames[0], slots)


# ---------------------------------------------------------------------
# Camera en renderen (zelfde camera als de geavanceerde animatie)
# ---------------------------------------------------------------------
CAM_HIGH = ((2500.0, -2300.0, 1500.0), -650.0, 350.0)     # oogverschuiving, doel-y t.o.v. robot, doel-z
CAM_LOW = ((1800.0, -1650.0, 330.0), -1250.0, 170.0)


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def camera_blend(f, frames):
    t0 = next((g["t"] for g in frames if g["v"] > 0.0), 0.0) + 1.0
    t_raise = next((g["t"] for g in frames if g["phase"] == "raise"), frames[-1]["t"])
    return smooth((f["t"] - t0) / 1.8) * (1.0 - smooth((f["t"] - t_raise) / 1.8))


def track_camera(f, s, fov=38.0):
    import FreeCADGui as Gui
    from pivy import coin
    (e1, ty1, tz1), (e2, ty2, tz2) = CAM_HIGH, CAM_LOW
    eye = [e1[k] + (e2[k] - e1[k]) * s for k in range(3)]
    ty = ty1 + (ty2 - ty1) * s
    tz = tz1 + (tz2 - tz1) * s
    tgt = (0.0, f["y"] + ty, tz)
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(tgt[0] + eye[0], tgt[1] + eye[1], tgt[2] + eye[2]))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


STATE_NL = {"hold": "geheven", "lower": "zakken", "work": "werkstand", "raise": "heffen", "end": "geheven"}


def meta(f):
    return {"t": round(f["t"], 3), "v": round(f["v"], 1), "dist": round(f["dist"], 1), "psi": round(f["psi"], 2),
            "act_len": round(f["length"], 1), "hanging": f["hanging"], "blocked": f["blocked"],
            "state": STATE_NL[f["phase"]], "pitch": round(f["pitch"], 2), "roll": round(f["roll"], 2),
            "depth": [round(r["depth"], 1) for r in f["rows"]], "wheel_gap": [round(g, 1) for g in f["wheel_gap"]],
            "disc": [round(r["disc"], 1) for r in f["rows"]],
            "knife_angle": round(f["knife_angle"], 1), "pump": f["pump"], "flow": round(f["flow"], 2),
            "applied_l": round(f["applied"], 3)}


def render_frames(folder, first=0, count=None, fps=FPS, size=(720, 480)):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames, slots = prepare(fps)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i], slots)
        track_camera(frames[i], camera_blend(frames[i], frames))
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


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
    frames, slots = prepare(fps)
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
            apply_frame(doc, f, slots)
            if follow:
                track_camera(f, camera_blend(f, frames))
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))


def check_fit(doc=None, tol=1.0):
    """Overlap tussen het echte robotmodel en de toediener (robot vlak, werkstand)."""
    doc = doc or App.getDocument(DOC_NAME)
    lfs_names = {o.Name for o in doc.getObject("Applicator").OutListRecursive}
    robot_objs, lfs_objs = [], []
    for o in doc.getObject("Robot").OutListRecursive:
        if o.TypeId != "Part::Feature" or not o.ViewObject.Visibility:
            continue
        (lfs_objs if o.Name in lfs_names else robot_objs).append((o, build_lfs2.global_shape(o)))
    hits = []
    for oa, sa in robot_objs:
        for ob, sb in lfs_objs:
            if sa.BoundBox.intersect(sb.BoundBox):
                vol = sa.common(sb).Volume
                if vol > tol:
                    hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits
