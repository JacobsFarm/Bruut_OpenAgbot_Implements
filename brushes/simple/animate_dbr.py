"""Animatie: de Bruut OpenAgbot borstelt los materiaal op een betonvloer, in drie runs (RUNS):
- "windrow": 2 x Ø750, voorkant naar binnen, maakt van een gelijkmatige laag een wiers in het midden;
- "spread":  2 x Ø750 tegen elkaar, voorkant naar buiten, legt een wiers breed;
- "single":  1 x Ø850, gooit alles naar rechts.

Bouwt een apart document (de robotbestanden in "agbot design" worden niet aangepast): robot uit build_agbot,
borstels uit build_dbr, betonvloer en het materiaal (dbr_material, deeltjes als mesh).
De robot rijdt achteruit (borstels voorop, naar -y). Per frame: robot (positie, wielrotatie), borstels (rotatie om de
gekantelde as), materiaal; koppel, vermogen en stroom per borstel uit dbr_calc met de gemeten materiaalstroom.

Gebruik in FreeCAD:
    import animate_dbr
    animate_dbr.build("windrow")                     # document opbouwen
    animate_dbr.play("windrow")                      # live afspelen, animate_dbr.stop()
    animate_dbr.summary("windrow")                   # kerngetallen van de rit
    animate_dbr.render_all("windrow", r"C:\\temp\\dbr_windrow")
    import make_gif_dbr; make_gif_dbr.main(r"C:\\temp\\dbr_windrow", r"previews\\animation_windrow.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Mesh
import Part
from FreeCAD import Vector as V

import dbr_params as P
import dbr_calc as C
import dbr_material as M
import build_dbr

DOC_NAME = "DBR_on_robot_animation"

RUNS = {
    "windrow": {"config": "double_750", "mode": "windrow", "start": "layer", "rpm": 70.0,
                "title": "wiers maken: 2 x Ø750, voorkant draait naar binnen"},
    "spread": {"config": "double_750", "mode": "spread", "start": "windrow", "rpm": 100.0,
               "title": "breed leggen: 2 x Ø750 tegen elkaar, voorkant draait naar buiten"},
    "single": {"config": "single_850", "mode": "right", "start": "layer", "rpm": 90.0, "strip_x": (-430.0, 430.0),
               "title": "1 x Ø850: de strook voor de robot naar rechts"},
}

# ---------------------------------------------------------------------
# Rijplan
# ---------------------------------------------------------------------
FPS = 10
SPEED = P.drive_speed * 1000.0      # mm/s
SPIN_UP = 0.6                       # borstels op toeren voor het rijden
ACCEL_TIME = 0.6
DECEL_TIME = 0.6
DRIVE = 3000.0                      # mm
STRIP = 2200.0                      # lengte van het materiaal (mm)
HOLD_END = 0.8
SUB = 10                            # deelstappen materiaalmodel per frame
COLOR = {"floor": (0.70, 0.70, 0.68), "material": (0.80, 0.62, 0.32)}

_timer = None
_play = {}


def make_material(run):
    r = RUNS[run]
    c = P.config(r["config"])
    front = P.floor_centre_y(c) - c["R"]
    return M.Material(r["config"], r["mode"], r["start"], strip_y=(front - 80.0, front - 80.0 - STRIP),
                      windrow=(400.0, 8.0), strip_x=r.get("strip_x", (-820.0, 820.0)))


def prepare(run, fps=FPS):
    """Rijplan + materiaalmodel. Geeft een lijst frames (dicts, met een kopie van de deeltjes)."""
    r = RUNS[run]
    name = r["config"]
    c = P.config(name)
    mat = make_material(run)
    dt = 1.0 / (fps * SUB)
    t, y, v = 0.0, 0.0, 0.0
    phase = "spin"
    spin = {"robot": 0.0, "brush": 0.0}
    frames = []
    step = 0
    moved_prev, t_prev = 0.0, 0.0
    m_dot = 0.0
    while True:
        rpm = r["rpm"] * min(1.0, t / SPIN_UP)
        if step % SUB == 0:
            moved = mat.moved_kg()
            if t > t_prev:
                m_dot += 0.5 * ((moved - moved_prev) / (t - t_prev) / c["n"] - m_dot)
            moved_prev, t_prev = moved, t
            tq = C.torque(name, rpm, v=v / 1000.0, m_dot=m_dot)
            e, prof = mat.profile(y, 100.0, 1500.0)
            frames.append({"t": t, "y": y, "v": v, "phase": phase, "rpm": rpm, "spin": dict(spin),
                           "x": mat.x.copy(), "yy": mat.y.copy(), "z": mat.heights(),
                           "T": tq["T"], "P_el": tq["P_el"], "I": tq["I"], "m_dot": m_dot, "moved": moved,
                           "profile": prof.tolist(), "stats": mat.stats(y)})
        if phase == "spin" and t >= SPIN_UP:
            phase = "drive"
        elif phase == "drive":
            v = min(SPEED, v + SPEED / ACCEL_TIME * dt)
            if -y >= DRIVE - SPEED * DECEL_TIME / 2.0:
                phase = "brake"
        elif phase == "brake":
            v = max(0.0, v - SPEED / DECEL_TIME * dt)
            if v <= 0.0:
                phase, t_halt = "stop", t
        elif phase == "stop" and t - t_halt >= HOLD_END:
            break
        mat.step(y, dt, rpm, v)
        y_new = y - v * dt
        spin["robot"] += (y_new - y) / (P.robot_tire_d / 2.0)
        spin["brush"] += rpm / 60.0 * 360.0 * dt
        y = y_new
        t += dt
        step += 1
    for f in frames:
        f["dist"] = -f["y"]
    return frames, mat


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def build(run="windrow"):
    r = RUNS[run]
    if build_dbr.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_dbr.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Disc brushes on robot - animation (%s)" % run
    doc.Comment = "Gegenereerd door animate_dbr.py (%s). Robot uit agbot design, borstels uit build_dbr." % run
    robot = build_dbr.build_robot(doc)
    build_dbr.build_into(doc, robot, r["config"], r["mode"] if r["mode"] in ("spread", "windrow") else "spread",
                         ballast=False)
    floor = doc.addObject("Part::Feature", "anim_floor")
    floor.Shape = Part.makeBox(5000.0, 9000.0, 40.0, V(-2500.0, -6500.0, -40.0))
    floor.ViewObject.ShapeColor = COLOR["floor"]
    mat = doc.addObject("Mesh::Feature", "anim_material")
    mat.ViewObject.ShapeColor = COLOR["material"]
    mat.ViewObject.Lighting = "Two side"
    doc.recompute()
    doc.Comment += " run=%s" % run
    return doc


def unit_axes(run):
    r = RUNS[run]
    mode = r["mode"] if r["mode"] in ("spread", "windrow") else "spread"
    return [(tag, build_dbr.G.brush_axis(u)) for tag, u in build_dbr.units(r["config"], mode)]


def apply_frame(doc, f, axes, signs):
    doc.getObject("Robot").Placement = App.Placement(V(0.0, f["y"], 0.0), App.Rotation())
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin"]["robot"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    for (tag, (p, d)), s in zip(axes, signs):
        doc.getObject("Brush_" + tag).Placement = App.Placement(V(0, 0, 0), App.Rotation(d, s * f["spin"]["brush"]), p)
    m = _MAT
    m.x, m.y = f["x"], f["yy"]
    doc.getObject("anim_material").Mesh = Mesh.Mesh(M.triangles(m, f["z"]))


_MAT = None


# ---------------------------------------------------------------------
# Camera en renderen
# ---------------------------------------------------------------------
CAM_A = ((-2100.0, -2900.0, 2000.0), (0.0, -1450.0, 0.0))      # schuin van voren: borstels pakken het materiaal
CAM_B = ((-1900.0, 3300.0, 2600.0), (0.0, 700.0, 0.0))         # van achteren over het resultaat naar de robot kijken


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def track_camera(f, frames, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    t_end = frames[-1]["t"]
    s = smooth((f["t"] - (t_end - 3.5)) / 2.5)
    eye = [CAM_A[0][i] + (CAM_B[0][i] - CAM_A[0][i]) * s for i in range(3)]
    tgt = [CAM_A[1][i] + (CAM_B[1][i] - CAM_A[1][i]) * s for i in range(3)]
    target = (tgt[0], f["y"] + tgt[1], tgt[2])
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(target[0] + eye[0], target[1] + eye[1], target[2] + eye[2]))
    cam.pointAt(coin.SbVec3f(*target), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


STATE_NL = {"spin": "borstels starten", "drive": "borstelen", "brake": "stoppen", "stop": "klaar"}


def meta(f, run):
    r = RUNS[run]
    return {"run": run, "title": r["title"], "t": round(f["t"], 3), "v": round(f["v"], 1), "dist": round(f["dist"], 1),
            "state": STATE_NL[f["phase"]], "rpm": round(f["rpm"], 1), "T": round(f["T"], 2), "P_el": round(f["P_el"], 1),
            "I": round(f["I"], 2), "n": P.config(r["config"])["n"], "moved": round(f["moved"], 2),
            "profile": [round(p, 2) for p in f["profile"]], "stats": {k: round(v, 2) for k, v in f["stats"].items()}}


def summary(run="windrow", frames=None):
    frames = frames or prepare(run)[0]
    work = [f for f in frames if f["phase"] == "drive" and f["t"] > SPIN_UP + ACCEL_TIME + 0.5]
    rng = lambda k: (round(min(f[k] for f in work), 2), round(max(f[k] for f in work), 2))
    last = frames[-1]
    return {"frames": len(frames), "duration_s": round(last["t"], 2), "torque_Nm": rng("T"), "P_el_W": rng("P_el"),
            "I_A": rng("I"), "m_dot_kg_s": rng("m_dot"), "moved_kg": round(last["moved"], 2),
            "end": {k: round(v, 2) for k, v in last["stats"].items()}}


def render_frames(run, folder, first=0, count=None, fps=FPS, size=(720, 480)):
    import FreeCADGui as Gui
    global _MAT
    doc = App.getDocument(DOC_NAME)
    frames, _MAT = prepare(run, fps)
    axes = unit_axes(run)
    signs = P.brush_signs(P.config(RUNS[run]["config"]), RUNS[run]["mode"])
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f, run) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i], axes, signs)
        track_camera(frames[i], frames)
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(run, folder, fps=FPS, size=(720, 480)):
    build(run)
    first, total = 0, 1
    while first < total:
        first, total = render_frames(run, folder, first, 30, fps, size)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(run="windrow", fps=FPS, loop=False, follow=True):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer, _MAT
    stop()
    doc = App.getDocument(DOC_NAME)
    frames, _MAT = prepare(run, fps)
    axes = unit_axes(run)
    signs = P.brush_signs(P.config(RUNS[run]["config"]), RUNS[run]["mode"])
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
            apply_frame(doc, f, axes, signs)
            if follow:
                track_camera(f, frames)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))


def check_fit(doc=None, tol=1.0):
    """Overlap tussen het echte robotmodel en de borstels in het animatiedocument (robot recht)."""
    doc = doc or App.getDocument(DOC_NAME)
    return build_dbr.check_interference(doc, tol)
