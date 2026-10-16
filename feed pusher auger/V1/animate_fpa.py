"""Animatie: de Bruut OpenAgbot schuift voer aan met de voerschuifvijzel, langs een voerhek.

Bouwt een apart document (de robotbestanden in "agbot design" worden niet aangepast): robot uit build_agbot,
voerschuif uit build_fpa, betonvloer, voerhek met opstand en een strook weggeduwd voer (fpa_feed).
De robot rijdt achteruit (vijzel voorop, naar -y); de stuurkoppen zitten achter.
Per frame:
- het voermodel neemt voer op aan de voorkant van het blad, voert het naar +x en legt het tegen het hek;
- uit de massa in de vijzel volgen de krachten (fpa_calc.feed_forces): zijkracht van het hek af, duwkracht
  tegen de rijrichting, askoppel, vermogen en stroom;
- de robot reageert (fpa_calc.robot_reaction): wiellasten, zijkrachten per wiel, scheefstand van de robot
  (achterwielen staan vast, de robot loopt een fractie scheef) en de stuurcorrectie van de voorwielen.
  Pijlen in beeld: rood = kracht van het voer op de vijzel, blauw = zijkracht van de vloer op elk wiel.

Gebruik in FreeCAD:
    import animate_fpa
    animate_fpa.build()                       # document opbouwen
    animate_fpa.play()                        # live afspelen, animate_fpa.stop()
    animate_fpa.summary()                     # kerngetallen van de rit
    animate_fpa.render_all(r"C:\\temp\\fpa_frames")    # frames renderen (in stukken: render_frames)
    import make_gif_fpa; make_gif_fpa.main(r"C:\\temp\\fpa_frames", r"previews\\animation_feed_pushing.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Mesh
import Part
from FreeCAD import Vector as V

import fpa_params as P
import fpa_calc as C
import fpa_feed as F
import build_fpa

FOLDER = os.path.dirname(os.path.abspath(__file__))
DOC_NAME = "FPA_on_robot_animation"

# ---------------------------------------------------------------------
# Rijplan
# ---------------------------------------------------------------------
FPS = 8
SPEED = P.drive_speed * 1000.0      # mm/s
ACCEL_TIME = 1.0
DECEL_TIME = 1.0
SPIN_UP = 0.6                       # vijzel op toeren voor het rijden
Y_START = 1250.0                    # robotmidden bij de start (blad 130 mm voor het begin van het voer)
Y_BRAKE = -2700.0                   # hier begint het remmen
RUN_OUT = 2.2                       # vijzel draait na tot hij leeg is
HOLD_END = 0.6
SUB = 5                             # deelstappen voermodel per frame
TAU_REACTION = 0.4                  # s, naijlen scheefstand en stuurhoek (band bouwt slip op)

FORCE_SCALE = 4.0                   # mm pijl per N
# snelheidsregeling: boven I_SET (vijzelmotor) gaat de robot langzamer rijden, bij I_MAX staat hij (bijna) stil
I_SET = 18.0
I_MAX = 30.0
V_MIN = 0.25                        # fractie van SPEED
COLOR = {"floor": (0.66, 0.66, 0.64), "curb": (0.78, 0.78, 0.75), "fence": (0.62, 0.66, 0.68),
         "feed": (0.64, 0.56, 0.24), "feed_auger": (0.72, 0.62, 0.22), "force_feed": (0.85, 0.10, 0.10),
         "force_wheel": (0.10, 0.35, 0.85)}

_timer = None
_play = {}


# ---------------------------------------------------------------------
# Simulatie
# ---------------------------------------------------------------------
def auger_rpm_at(t, t_stop):
    if t < SPIN_UP:
        return P.auger_rpm * t / SPIN_UP
    if t_stop is not None and t > t_stop:
        return max(0.0, P.auger_rpm * (1.0 - (t - t_stop) / 0.4))
    return P.auger_rpm


def speed_factor(current):
    """Rijsnelheid als fractie van SPEED bij gemeten motorstroom van de vijzel (A)."""
    if current <= I_SET:
        return 1.0
    return max(V_MIN, 1.0 - (1.0 - V_MIN) * (current - I_SET) / (I_MAX - I_SET))


def prepare(fps=FPS):
    """Rijplan + voermodel + krachten. Geeft een lijst frames (dicts) en het voermodel aan het eind."""
    feed = F.FeedField()
    dt = 1.0 / (fps * SUB)
    t, y, v = 0.0, Y_START, 0.0
    phase = "spin"
    t_halt = None
    t_stop = None
    psi = delta = 0.0
    i_filt = 0.0
    spin = {"robot": 0.0, "auger": 0.0}
    frames = []
    step = 0
    while True:
        if step % SUB == 0:
            m, xc, over = feed.engaged()
            rpm = auger_rpm_at(t, t_stop)
            fo = C.feed_forces(m, v / 1000.0, rpm)
            point = (xc, P.auger_y - 150.0, 60.0)
            rr = C.robot_reaction(fo["F_ax"], fo["F_push"], point)
            frames.append({"t": t, "y": y, "v": v, "phase": phase, "rpm": rpm, "m": m, "xc": xc, "over": over,
                           "v_factor": speed_factor(i_filt),
                           "forces": fo, "reaction": rr, "point": point, "psi": psi, "delta": delta,
                           "spin": dict(spin), "H": feed.heights(), "B": feed.blob_heights(),
                           "bins": feed.B.copy(), "collected": feed.collected, "moved": feed.moved})
        # rijplan
        if phase == "spin" and t >= SPIN_UP:
            phase = "drive"
        elif phase == "drive":
            v_set = SPEED * speed_factor(i_filt)
            step_v = SPEED / ACCEL_TIME * dt
            v = min(v_set, v + step_v) if v < v_set else max(v_set, v - step_v)
            if y <= Y_BRAKE:
                phase = "brake"
        elif phase == "brake":
            v = max(0.0, v - SPEED / DECEL_TIME * dt)
            if v <= 0.0:
                phase, t_halt = "run_out", t
        elif phase == "run_out" and t - t_halt >= RUN_OUT:
            phase, t_stop = "stop", t
        elif phase == "stop" and t - t_stop >= HOLD_END:
            break
        rpm = auger_rpm_at(t, t_stop)
        y_new = y - v * dt
        feed.step(y, y_new, dt, turning=rpm > 1.0)
        # reactie van de robot (eerste orde naijlen)
        m, xc, _ = feed.engaged()
        fo = C.feed_forces(m, v / 1000.0, rpm)
        rr = C.robot_reaction(fo["F_ax"], fo["F_push"], (xc, P.auger_y - 150.0, 60.0))
        a = dt / (TAU_REACTION + dt)
        if v > 20.0:      # slip-hoeken bestaan alleen bij rollen; stilstaand houdt de band de zijkracht zonder te verlopen
            psi += a * (rr["psi"] - psi)
            delta += a * (rr["delta"] - delta)
        i_filt += dt / (0.3 + dt) * (fo["I"] - i_filt)                       # stroommeting, gefilterd
        spin["robot"] += (y_new - y) / (P.robot_tire_d / 2.0)
        spin["auger"] += rpm / 60.0 * 360.0 * dt
        y = y_new
        t += dt
        step += 1
    for f in frames:
        f["dist"] = Y_START - f["y"]
    return frames, feed


# ---------------------------------------------------------------------
# Omgeving
# ---------------------------------------------------------------------
def fence_shapes(y_range=(-6000.0, 2500.0)):
    """Opstand (beton) met een eenvoudig voerhek erop: palen, bovenregel, nekregel en schuine spijlen."""
    x0 = F.FENCE_X
    curb = Part.makeBox(150.0, y_range[1] - y_range[0], 200.0, V(x0, y_range[0], 0.0))
    parts = []
    y = y_range[0]
    while y <= y_range[1]:
        parts.append(Part.makeBox(60.0, 60.0, 1100.0, V(x0 + 45.0, y - 30.0, 200.0)))
        y += 1500.0
    for z in (700.0, 1250.0):
        parts.append(Part.makeCylinder(24.0, y_range[1] - y_range[0], V(x0 + 75.0, y_range[0], z), V(0, 1, 0)))
    y = y_range[0]
    while y <= y_range[1]:
        bar = Part.makeCylinder(14.0, 560.0, V(0, 0, 0), V(0, 0, 1))
        bar.rotate(V(0, 0, 0), V(1, 0, 0), 12.0)
        bar.translate(V(x0 + 75.0, y, 700.0))
        parts.append(bar)
        y += 250.0
    return curb, Part.makeCompound(parts)


def arrow(start, vec, r=13.0):
    """Pijl langs vec (mm) vanaf start; leeg als de kracht te klein is."""
    length = math.hypot(vec[0], vec[1])
    if length < 12.0:
        return Part.Shape()
    d = V(vec[0] / length, vec[1] / length, 0.0)
    head = min(70.0, 0.45 * length)
    shaft = Part.makeCylinder(r, length - head, V(*start), d)
    tip = Part.makeCone(2.4 * r, 0.0, head, V(*start) + d * (length - head), d)
    return shaft.fuse(tip)


def build():
    if build_fpa.AGBOT_FOLDER not in sys.path:
        sys.path.insert(0, build_fpa.AGBOT_FOLDER)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Feed pusher on robot - animation"
    doc.Comment = "Gegenereerd door animate_fpa.py. Robot uit agbot design, voerschuif uit build_fpa, voer uit fpa_feed."
    robot = build_fpa.build_robot(doc)
    build_fpa.build_into(doc, robot)

    floor = doc.addObject("Part::Feature", "anim_floor")
    floor.Shape = Part.makeBox(4200.0, 8500.0, 60.0, V(-3100.0, -6000.0, -60.0))
    floor.ViewObject.ShapeColor = COLOR["floor"]
    curb, fence = fence_shapes()
    for name, shape, color in (("anim_curb", curb, "curb"), ("anim_fence", fence, "fence")):
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        obj.ViewObject.ShapeColor = COLOR[color]
    feed = doc.addObject("Mesh::Feature", "anim_feed")
    feed.ViewObject.ShapeColor = COLOR["feed"]
    blob = doc.addObject("Mesh::Feature", "anim_feed_in_auger")
    blob.ViewObject.ShapeColor = COLOR["feed_auger"]
    robot.addObject(blob)
    for name, color in [("anim_force_feed", "force_feed")] + [("anim_force_" + t, "force_wheel") for t, _, _ in C.WHEELS]:
        obj = doc.addObject("Part::Feature", name)
        obj.ViewObject.ShapeColor = COLOR[color]
        robot.addObject(obj)
    for o in (feed, blob):
        o.ViewObject.Lighting = "Two side"
    doc.recompute()
    return doc


# ---------------------------------------------------------------------
# Frame toepassen
# ---------------------------------------------------------------------
def apply_frame(doc, f, feed_xy):
    doc.getObject("Robot").Placement = App.Placement(V(0.0, f["y"], 0.0), App.Rotation(V(0, 0, 1), f["psi"]))
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin"]["robot"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    for name in ("FL_steered", "FR_steered"):
        doc.getObject(name).Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), f["delta"]))
    # vijzel draait met de voorkant omhoog (negatief om +x), motorwiel 2x zo snel
    a = -f["spin"]["auger"]
    doc.getObject("Auger_rotor").Placement = build_fpa.rotation_x(a, build_fpa.AUGER_AXIS)
    doc.getObject("motor_sprocket").Placement = build_fpa.rotation_x(a * P.z_auger / P.z_motor, build_fpa.MOTOR_AXIS)
    xs, ys = feed_xy
    doc.getObject("anim_feed").Mesh = Mesh.Mesh(F.mesh_triangles(xs, ys, f["H"]))
    bx = xs[F_COLS[0]:F_COLS[1]]
    doc.getObject("anim_feed_in_auger").Mesh = Mesh.Mesh(F.blob_triangles(bx, f["B"], -110.0))
    # krachtpijlen (robotcoordinaten)
    fo = f["forces"]
    px = f["point"][0]
    py = P.auger_y + P.hood_pts[-1][0] - 60.0       # net voor de kaplip, boven het voer
    vec = (fo["F_ax"] * FORCE_SCALE, fo["F_push"] * FORCE_SCALE)
    doc.getObject("anim_force_feed").Shape = arrow((px - vec[0], py - vec[1], 330.0), vec)
    for tag, x, y in C.WHEELS:
        lat = f["reaction"]["wheels"][tag]["lat"]
        start = (x + math.copysign(60.0, lat), y, 40.0)       # vanaf de bandflank in de richting van de kracht
        doc.getObject("anim_force_" + tag).Shape = arrow(start, (lat * FORCE_SCALE, 0.0))


F_COLS = (0, 0)


def feed_grid():
    global F_COLS
    g = F.FeedField()
    F_COLS = (g.c0, g.c1)
    return g.xs, g.ys


# ---------------------------------------------------------------------
# Camera en renderen
# ---------------------------------------------------------------------
CAM_A = ((-2300.0, -2500.0, 1650.0), (0.0, -950.0, 150.0))      # schuin van voren, vanaf de voergang
CAM_B = ((-1500.0, -800.0, 4000.0), (250.0, -750.0, 0.0))       # bijna van boven: voer gaat naar het hek
CAM_C = ((-3300.0, -1700.0, 3000.0), (300.0, 900.0, 0.0))       # terugkijken: schone strook en nieuwe rand bij het hek


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def camera_pose(f, frames):
    t = f["t"]
    t_end = frames[-1]["t"]
    s1 = smooth((t - 4.0) / 2.5)
    s2 = smooth((t - (t_end - 5.5)) / 2.5)
    pose = []
    for k in range(2):
        a = [CAM_A[k][i] + (CAM_B[k][i] - CAM_A[k][i]) * s1 for i in range(3)]
        pose.append([a[i] + (CAM_C[k][i] - a[i]) * s2 for i in range(3)])
    return pose


def track_camera(f, frames, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    eye, tgt = camera_pose(f, frames)
    target = (tgt[0], f["y"] + tgt[1], tgt[2])
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(target[0] + eye[0], target[1] + eye[1], target[2] + eye[2]))
    cam.pointAt(coin.SbVec3f(*target), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


STATE_NL = {"spin": "vijzel start", "drive": "voerschuiven", "brake": "stoppen", "run_out": "vijzel loopt leeg",
            "stop": "klaar"}


def meta(f):
    rr = f["reaction"]
    fo = f["forces"]
    return {"t": round(f["t"], 3), "v": round(f["v"], 1), "dist": round(f["dist"], 1), "state": STATE_NL[f["phase"]],
            "rpm": round(f["rpm"], 1), "m": round(f["m"], 2), "over": round(f["over"], 2), "xc": round(f["xc"]),
            "F_ax": round(fo["F_ax"], 1), "F_push": round(fo["F_push"], 1), "T": round(fo["T"], 2),
            "P_el": round(fo["P_el"], 1), "I": round(fo["I"], 2), "F_chain": round(fo["F_chain"]),
            "psi": round(f["psi"], 3), "delta": round(f["delta"], 3), "F_rear": round(rr["F_rear"], 1),
            "v_factor": round(f["v_factor"], 3),
            "F_front": round(rr["F_front"], 1),
            "wheels": {k: {kk: round(vv, 3 if kk == "use" else 1) for kk, vv in w.items()} for k, w in rr["wheels"].items()},
            "collected": round(f["collected"], 2), "moved": round(f["moved"], 2),
            "bins": [round(b, 3) for b in f["bins"]], "cap_bin": round(C.capacity()["q_cap_kg_m"] * 0.025, 3)}


def summary(frames=None):
    frames = frames or prepare()[0]
    work = [f for f in frames if f["phase"] == "drive" and f["t"] > SPIN_UP + ACCEL_TIME]
    def rng(key, src=None):
        vals = [(f["forces"][key] if src == "forces" else f[key]) for f in work]
        return round(min(vals), 2), round(max(vals), 2)
    use = [w["use"] for f in work for w in f["reaction"]["wheels"].values()]
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 2),
            "feed_in_auger_kg": rng("m"), "bulldozed_kg": rng("over"),
            "torque_Nm": rng("T", "forces"), "P_el_W": rng("P_el", "forces"), "I_A": rng("I", "forces"),
            "F_ax_N": rng("F_ax", "forces"), "F_push_N": rng("F_push", "forces"),
            "F_rear_N": (round(min(f["reaction"]["F_rear"] for f in work)), round(max(f["reaction"]["F_rear"] for f in work))),
            "F_front_N": (round(min(f["reaction"]["F_front"] for f in work)), round(max(f["reaction"]["F_front"] for f in work))),
            "psi_deg": rng("psi"), "delta_deg": rng("delta"), "grip_use_max": round(max(use), 3),
            "speed_mm_s": rng("v"), "collected_kg": round(frames[-1]["collected"], 1),
            "moved_kg": round(frames[-1]["moved"], 1)}


def render_frames(folder, first=0, count=None, fps=FPS, size=(720, 480)):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames, _ = prepare(fps)
    grid = feed_grid()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i], grid)
        track_camera(frames[i], frames)
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, fps=FPS, size=(720, 480)):
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 30, fps, size)
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
    frames, _ = prepare(fps)
    grid = feed_grid()
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
            apply_frame(doc, f, grid)
            if follow:
                track_camera(f, frames)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))


def check_fit(doc=None, tol=1.0):
    """Overlap tussen het echte robotmodel en de voerschuif in het animatiedocument (robot recht)."""
    doc = doc or App.getDocument(DOC_NAME)
    pusher = {o.Name for o in doc.getObject("Feed_pusher").OutListRecursive}
    robot_objs, fpa_objs = [], []
    for o in doc.getObject("Robot").OutListRecursive:
        if o.TypeId != "Part::Feature" or o.Name.startswith("anim_"):
            continue
        (fpa_objs if o.Name in pusher else robot_objs).append((o, build_fpa.global_shape(o)))
    hits = []
    for oa, sa in robot_objs:
        for ob, sb in fpa_objs:
            if sa.BoundBox.intersect(sb.BoundBox):
                vol = sa.common(sb).Volume
                if vol > tol:
                    hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits
