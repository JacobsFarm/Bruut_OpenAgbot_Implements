"""Animatie: de dockweed drill achter de Bruut OpenAgbot behandelt 3 ridderzuringplanten.

Bouwt een apart document (de robotbestanden in "agbot design" worden niet aangepast):
robot uit build_agbot + werktuig uit build_dwd6 + maaiveld met planten.
De robot rijdt met het portaal voorop (achteruit, -y). Per plant:
- rijden en stoppen met de plant onder de spillijn, de X-slede gaat tijdens het rijden al naar de plant;
- de actuator schuift uit (ijlgang) tot de bus de zode raakt (sensor = maaiveld), de spil draait 500 rpm;
- insteken met 25 mm/s tot 150 mm diep, nadraaien, draaiend omhoog tot de bus loskomt, actuator in naar de rijstand;
- de plant verdwijnt, er blijft een vermorzelde kolom achter.
Vermogen, Z-kracht, actuatorstroom en wiellasten komen uit dwd6_calc, zodat animatie en rapport dezelfde getallen
geven. (Gebaseerd op animate_dwd4; v6 maait niet: 500 rpm is te langzaam voor de maaischijf.)

Gebruik in FreeCAD:
    import animate_dwd6
    animate_dwd6.build()
    animate_dwd6.play()                       # live, animate_dwd6.stop()
    animate_dwd6.summary()
    animate_dwd6.render_all(r"C:\\temp\\dwd6_frames")
    import make_gif_dwd6; make_gif_dwd6.main(r"C:\\temp\\dwd6_frames", r"previews\\animation_three_plants.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd6_params as P
import dwd6_parts as G
import dwd6_calc as C
import build_dwd6

FOLDER = os.path.dirname(os.path.abspath(__file__))
DOC_NAME = "DWD6_on_robot_animation"

# ---------------------------------------------------------------------
# Rijplan en planten (wereldcoordinaten; robot start met zijn midden op y = 0 en rijdt naar -y)
# ---------------------------------------------------------------------
DT = 0.25              # s simulatietijd per frame (GIF met 12 fps = 3x versneld)
ACCEL = 0.8            # s optrekken / remmen
SETTLE = 0.5           # s stilstaan na het remmen (RTK, camera)
HOLD_END = 1.5
PLANTS = ((-300.0, -1750.0, 1.0), (330.0, -3000.0, 0.85), (40.0, -4250.0, 1.1))   # x, y, grootte
SPIN_DEG = 37.0        # draaiing van het gereedschap per frame (stroboscopisch)
SPINUP = 1.0           # s spil op toeren

COLOR = {"grass": (0.45, 0.62, 0.31), "lines": (0.35, 0.50, 0.24), "soil": (0.42, 0.29, 0.16),
         "leaf": (0.18, 0.45, 0.12), "root": (0.45, 0.30, 0.20)}
TERRAIN = ((-1600.0, 1600.0), (-6200.0, 1800.0))

_timer = None
_play = {}


# ---------------------------------------------------------------------
# Tijdlijn
# ---------------------------------------------------------------------
def drive_profile(dist, v=P.drive_speed, t_acc=ACCEL):
    """Trapezium: geeft (duur, functie s(t)) voor een afstand dist (mm)."""
    a = v / t_acc
    if dist <= v * t_acc:                       # driehoek
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


def segments():
    """Lijst van fasen: dict(name, T, f(t) -> (robot_y, x, z, spinning), plant index)."""
    segs = []
    ph = dict(C.cycle(P.depth_std))
    y = 0.0
    x = 0.0
    zd = P.drive_z
    z_pot = P.pot_rim                         # freesonderkant als de pot de grond raakt
    z_bot = -P.depth_std
    for i, (px, py, _) in enumerate(PLANTS):
        y_stop = py - C.SPINDLE_Y
        T, s = drive_profile(abs(y_stop - y))
        tx = abs(px - x) / P.rapid_x
        segs.append({"name": "drive", "T": T + SETTLE, "plant": i,
                     "f": (lambda t, y0=y, y1=y_stop, s=s, x0=x, x1=px, tx=tx:
                           (y0 - s(t), x0 + (x1 - x0) * ease(t / tx) if tx > 0 else x1, zd, False))})
        segs.append({"name": "probe", "T": ph["z_down_to_pot"], "plant": i,
                     "f": (lambda t, T=ph["z_down_to_pot"], y=y_stop, x=px: (y, x, zd - (zd - z_pot) * ease(t / T), True))})
        segs.append({"name": "plunge", "T": ph["plunge"], "plant": i,
                     "f": (lambda t, T=ph["plunge"], y=y_stop, x=px: (y, x, z_pot - (z_pot - z_bot) * t / T, True))})
        segs.append({"name": "dwell", "T": ph["dwell"], "plant": i,
                     "f": (lambda t, y=y_stop, x=px: (y, x, z_bot, True))})
        segs.append({"name": "rise", "T": ph["rise_mixing"], "plant": i,
                     "f": (lambda t, T=ph["rise_mixing"], y=y_stop, x=px: (y, x, z_bot + (z_pot - z_bot) * t / T, True))})
        segs.append({"name": "up", "T": ph["z_up"], "plant": i,
                     "f": (lambda t, T=ph["z_up"], y=y_stop, x=px: (y, x, z_pot + (zd - z_pot) * ease(t / T), False))})
        y, x = y_stop, px
    T, s = drive_profile(900.0)
    segs.append({"name": "away", "T": T + HOLD_END, "plant": len(PLANTS) - 1,
                 "f": (lambda t, y0=y, s=s, x0=x: (y0 - s(t), x0 * (1 - ease(t / 2.5)), zd, False))})
    return segs


TEXT = {
    "drive": "Rijden, camera vindt ridderzuring; X-slede gaat al naar de plant",
    "probe": "Spil %d rpm, actuator schuift uit tot de bus de zode voelt (= maaiveld)" % P.cutter_rpm,
    "plunge": "Vermorzelen: %d mm/s insteken tot %d mm diep" % (P.plunge_v, P.depth_std),
    "dwell": "Nadraaien op diepte",
    "rise": "Draaiend omhoog (mengt nog eens), grond blijft in het gat",
    "up": "Bus los, actuator in naar de rijstand, spil remt",
    "away": "Klaar: 3 gaten van 18 cm met fijngemalen wortel",
}


def act_current(phase, fz):
    """Stroom van de Z-actuator (A, 24 V) per fase: duwen = freeskracht min het gewicht van de Z-slede (helpt mee),
    trekken = gewicht van Z-slede en bus."""
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


def prepare(dt=DT):
    frames = []
    t_total = 0.0
    angle = 0.0
    dist = 0.0
    spin_t = 0.0
    done = set()
    prev_y = 0.0
    for seg in segments():
        n = max(1, int(round(seg["T"] / dt)))
        for k in range(n):
            t = (k + 1) * seg["T"] / n
            y, x, z, spinning = seg["f"](t)
            spin_t = spin_t + seg["T"] / n if spinning else 0.0
            rpm = P.cutter_rpm * min(1.0, spin_t / SPINUP) if spinning else 0.0
            if rpm > 0:
                angle += SPIN_DEG
            dist += abs(prev_y - y)
            prev_y = y
            depth = max(0.0, -z)
            rim = build_dwd6.pot_rim(z)
            on_ground = rim <= 1e-6
            cutting = seg["name"] == "plunge" and z < 0
            power = C.cut_power() if cutting else (C.cut_power() * 0.3 if seg["name"] == "rise" and z < 0
                                                   else (P.idle_w * rpm / P.cutter_rpm))
            fz = C.thrust(depth) if seg["name"] in ("plunge", "dwell") else 0.0
            loads = C.axle_loads(x, fz, on_ground)
            act_a = act_current(seg["name"], fz)
            i = seg["plant"]
            treating = seg["name"] in ("plunge", "dwell", "rise") and z < P.pot_rim / 2
            if seg["name"] == "up":
                done.add(i)
            t_total += seg["T"] / n
            frames.append({"t": t_total, "phase": seg["name"], "plant": i, "robot_y": y, "x": x, "z": z,
                           "depth": depth, "rim": rim, "pot_on_ground": on_ground, "rpm": rpm, "angle": angle,
                           "power": power, "fz": fz, "act_a": act_a, "wheels": loads["wheels_kg"], "front": loads["front_kg"],
                           "rear": loads["rear_kg"], "dist": dist, "done": sorted(done),
                           "treating": treating,
                           "leaves_gone": [j for j in range(len(PLANTS)) if j in done or (j == i and treating)]})
    return frames


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def build():
    BA = build_dwd6.load_robot()
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Dockweed drill v6 on robot - animation"
    doc.Comment = "Gegenereerd door animate_dwd6.py (niet opslaan nodig). Robot uit agbot design, werktuig uit build_dwd6."
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    build_dwd6.build_into(doc, robot, 0.0, P.drive_z)

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

    def add(name, shape, color, tr=0, visible=True):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = color
        o.ViewObject.LineColor = color
        o.ViewObject.Transparency = tr
        o.ViewObject.Visibility = visible
        return o

    add("anim_ground", ground, COLOR["grass"], 55)
    add("anim_ground_lines", Part.makeCompound(lines), COLOR["lines"])
    for i, (px, py, sc) in enumerate(PLANTS):
        leaves, root = G.dock_plant(px, py, sc, spin=25 * i)
        add("anim_leaves_%d" % i, leaves, COLOR["leaf"])
        add("anim_root_%d" % i, root, COLOR["root"], 20)
        add("anim_crushed_%d" % i, Part.makeCylinder(P.cutter_d / 2, P.depth_std, V(px, py, -P.depth_std)),
            COLOR["soil"], 30, False)
    build_dwd6.set_group_transparency(doc, "Pot", 65)      # frees in de pot zichtbaar
    doc.recompute()
    return doc


def apply_frame(doc, f):
    doc.getObject("Robot").Placement = build_dwd6.translation(y=f["robot_y"])
    rot = App.Rotation(V(1, 0, 0), math.degrees(f["dist"] / (P.robot_tire_d / 2)))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    build_dwd6.set_pose(doc, f["x"], f["z"], angle=f["angle"])
    for i in range(len(PLANTS)):
        gone = i in f["leaves_gone"]
        doc.getObject("anim_leaves_%d" % i).ViewObject.Visibility = not gone
        treated = i in f["done"]
        doc.getObject("anim_root_%d" % i).ViewObject.Visibility = not treated
        doc.getObject("anim_crushed_%d" % i).ViewObject.Visibility = treated


# ---------------------------------------------------------------------
# Camera en renderen
# ---------------------------------------------------------------------
CAM_WIDE = ((-2600.0, -2300.0, 1700.0), (0.0, -650.0, 500.0))     # oogverschuiving, doel t.o.v. (0, robot_y, 0)
CAM_CLOSE = ((-2100.0, -1100.0, 1050.0), (0.0, -900.0, 300.0))    # doel x volgt de spil


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def camera_blend(frames):
    """Per frame 0 (wijd) .. 1 (dichtbij): dichtbij tijdens de behandeling, wijd tijdens het rijden."""
    work = [1.0 if f["phase"] in ("probe", "plunge", "dwell", "rise", "up") else 0.0 for f in frames]
    out = []
    n = len(work)
    w = 6
    for i in range(n):
        lo, hi = max(0, i - w), min(n, i + w + 1)
        out.append(smooth(sum(work[lo:hi]) / (hi - lo)))
    return out


def track_camera(f, s, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    (e1, t1), (e2, t2) = CAM_WIDE, CAM_CLOSE
    eye = [e1[k] + (e2[k] - e1[k]) * s for k in range(3)]
    tgt = [t1[k] + (t2[k] - t1[k]) * s for k in range(3)]
    tgt = (tgt[0] + f["x"] * s, f["robot_y"] + tgt[1], tgt[2])
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(tgt[0] + eye[0], tgt[1] + eye[1], tgt[2] + eye[2]))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


def meta(f):
    return {"t": round(f["t"], 2), "phase": f["phase"], "text": TEXT[f["phase"]], "plant": f["plant"] + 1,
            "n_plants": len(PLANTS), "done": len(f["done"]), "x": round(f["x"]), "z": round(f["z"]),
            "depth": round(f["depth"]), "pot_on_ground": f["pot_on_ground"], "rpm": round(f["rpm"]),
            "power": round(f["power"]), "current": round(C.spindle_current(f["power"]), 1), "fz": round(f["fz"]),
            "act_a": round(f["act_a"], 1),
            "wheels": {k: round(v, 1) for k, v in f["wheels"].items()}, "front": round(f["front"]),
            "rear": round(f["rear"])}


def summary(frames=None):
    frames = frames or prepare()
    work = [f for f in frames if f["phase"] in ("plunge", "dwell")]
    wheels = [v for f in frames for v in f["wheels"].values()]
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 1),
            "time_per_plant_s": round(frames[-1]["t"] / len(PLANTS), 1),
            "x_range": (round(min(f["x"] for f in frames)), round(max(f["x"] for f in frames))),
            "z_range": (round(min(f["z"] for f in frames)), round(max(f["z"] for f in frames))),
            "max_depth": round(max(f["depth"] for f in frames)),
            "power_range_w": (round(min(f["power"] for f in work)), round(max(f["power"] for f in work))),
            "z_force_max_n": round(max(f["fz"] for f in frames)),
            "wheel_kg_range": (round(min(wheels), 1), round(max(wheels), 1)),
            "front_kg_range": (round(min(f["front"] for f in frames)), round(max(f["front"] for f in frames))),
            "plants_done": len(frames[-1]["done"])}


def render_frames(folder, first=0, count=None, size=(720, 480)):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames = prepare()
    blend = camera_blend(frames)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i])
        track_camera(frames[i], blend[i])
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, size=(720, 480)):
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 30, size)
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
                track_camera(frames[i], blend[i])
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / fps))


def check_fit(doc=None, tol=1.0):
    """Overlap tussen het echte robotmodel en het werktuig in de eindstanden (X +-500, rijstand en max. diepte)."""
    doc = doc or App.getDocument(DOC_NAME)
    out = {}
    for x, z in build_dwd6.POSES:
        build_dwd6.set_pose(doc, x, z)
        doc.recompute()
        impl = {o.Name for o in build_dwd6.implement_objects(doc)}
        robot = [(o, build_dwd6.global_shape(o)) for o in doc.getObject("Robot").OutListRecursive
                 if o.TypeId == "Part::Feature" and o.Name not in impl]
        mine = [(o, build_dwd6.global_shape(o)) for o in build_dwd6.implement_objects(doc)]
        hits = []
        for oa, sa in robot:
            for ob, sb in mine:
                if sa.BoundBox.intersect(sb.BoundBox):
                    vol = sa.common(sb).Volume
                    if vol > tol:
                        hits.append((oa.Label, ob.Label, round(vol, 1)))
        out[(x, z)] = hits
    build_dwd6.set_pose(doc, 0.0, P.drive_z)
    return out
