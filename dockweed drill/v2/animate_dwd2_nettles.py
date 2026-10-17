"""Animatie: de dockweed drill v2 met de maaischijf maait twee bossen brandnetels die boven het gras uitsteken.

Bouwt een apart document (de robotbestanden in "agbot design" worden niet aangepast):
robot uit build_agbot + werktuig uit build_dwd2 (gereedschap "mower") + grasland met brandnetels.
De robot rijdt met het portaal voorop (achteruit, -y). Per bos:
- rijden en stoppen met de eerste baan onder de spillijn, de X-slede staat dan al links naast het bos;
- de maaischijf draait 3000 rpm, Z zakt tot de pot het gras voelt en gaat mow_lift terug (mesjes op mow_z);
- baan 1 van links naar rechts, robot schuift mow_step naar voren, baan 2 terug, nog eens naar voren, baan 3;
- Z omhoog naar de rijstand, schijf remt, door naar het volgende bos.
Een stengel binnen de tipcirkel van de mesjes wordt een stoppel van mow_z hoog plus wat snippers in het gras.
Banen, vermogen en wiellasten komen uit dwd2_calc (mow_rows, mow_power, axle_loads).

Gebruik in FreeCAD:
    import animate_dwd2_nettles as A
    A.build()
    A.play()                                   # live, A.stop()
    A.summary()
    A.render_all(r"C:\\temp\\dwd2_nettle_frames")
    import make_gif_dwd2; make_gif_dwd2.main(r"C:\\temp\\dwd2_nettle_frames", r"previews\\animation_nettles_mowing.gif",
                                        scale=0.75, values=False)
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd2_params as P
import dwd2_parts as G
import dwd2_calc as C
import build_dwd2

FOLDER = os.path.dirname(os.path.abspath(__file__))
DOC_NAME = "DWD2_nettles_on_robot_animation"

# ---------------------------------------------------------------------
# Rijplan en brandnetels (wereldcoordinaten; robot start met zijn midden op y = 0 en rijdt naar -y)
# ---------------------------------------------------------------------
DT = 0.25              # s simulatietijd per frame (GIF met 12 fps = 3x versneld)
ACCEL = 0.8            # s optrekken / remmen
SETTLE = 0.5           # s stilstaan na het remmen
HOLD_END = 1.5
PATCHES = ({"xc": -60.0, "yc": -2050.0, "a": 300.0, "b": 240.0, "n": 46, "seed": 11},
           {"xc": 170.0, "yc": -3750.0, "a": 250.0, "b": 230.0, "n": 38, "seed": 23})
SPIN_DEG = 47.0        # draaiing van de schijf per frame (stroboscopisch)
SPINUP = 1.0           # s schijf op toeren
CUT_R = P.mower_tip_d / 2.0

COLOR = {"ground": (0.30, 0.40, 0.18), "grass": (0.40, 0.60, 0.24), "litter": (0.36, 0.30, 0.18),
         "nettle": (0.17, 0.36, 0.12), "stub": (0.40, 0.48, 0.22), "mulch": (0.25, 0.45, 0.15)}
TERRAIN = ((-3000.0, 4200.0), (-7000.0, 3500.0))

_timer = None
_play = {}
_shown = {}


def nettles():
    """Alle stengels: [(x, y, h, seed, bos)]."""
    out = []
    for k, p in enumerate(PATCHES):
        out += [s + (k,) for s in G.nettle_patch(p["xc"], p["yc"], p["a"], p["b"], p["n"], p["seed"])]
    return out


# ---------------------------------------------------------------------
# Tijdlijn
# ---------------------------------------------------------------------
def move_profile(dist, v, t_acc):
    """Trapezium: geeft (duur, functie s(t)) voor een afstand dist (mm)."""
    dist = abs(dist)
    if dist < 1e-6:
        return 0.0, (lambda t: 0.0)
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


def patch_plan(k, stems):
    """Banen (spil-y) en X-grenzen van bos k."""
    xs = [s[0] for s in stems if s[4] == k]
    ys = [s[1] for s in stems if s[4] == k]
    rows = C.mow_rows(max(ys), min(ys))
    x_lo, x_hi = max(P.x_min, min(xs)), min(P.x_max, max(xs))
    x_start = max(P.x_min, x_lo - CUT_R - 20.0)            # schijf zakt naast het bos
    return rows, x_start, x_lo, x_hi


def segments(stems):
    """Fasen: dict(name, T, f(t) -> (robot_y, x, z, spinning), patch, row)."""
    segs = []
    y, x, zd = 0.0, 0.0, P.drive_z
    t_down = (P.drive_z - P.mower_rim) / P.rapid_z + 0.3
    for k in range(len(PATCHES)):
        rows, x_start, x_lo, x_hi = patch_plan(k, stems)
        y_stop = rows[0] - C.SPINDLE_Y
        T, s = move_profile(y_stop - y, P.drive_speed, ACCEL)
        tx = abs(x_start - x) / P.rapid_x
        segs.append({"name": "drive", "T": T + SETTLE, "patch": k, "row": 0,
                     "f": (lambda t, y0=y, s=s, x0=x, x1=x_start, tx=tx:
                           (y0 - s(t), x0 + (x1 - x0) * ease(t / tx) if tx > 0 else x1, zd, False))})
        segs.append({"name": "probe", "T": t_down, "patch": k, "row": 0,
                     "f": (lambda t, T=t_down, y=y_stop, x=x_start:
                           (y, x, zd - (zd - P.mower_rim) * ease(t / T), True))})
        t_lift = P.mow_lift / P.rapid_z + 0.3
        segs.append({"name": "lift", "T": t_lift, "patch": k, "row": 0,
                     "f": (lambda t, T=t_lift, y=y_stop, x=x_start:
                           (y, x, P.mower_rim + P.mow_lift * ease(t / T), True))})
        x, y = x_start, y_stop
        for r, row in enumerate(rows):
            if r > 0:
                y1 = row - C.SPINDLE_Y
                T, s = move_profile(y1 - y, P.drive_speed, ACCEL)
                segs.append({"name": "step", "T": T + 0.25, "patch": k, "row": r,
                             "f": (lambda t, y0=y, s=s, x=x: (y0 - s(t), x, P.mow_z, True))})
                y = y1
            x1 = x_hi if r % 2 == 0 else x_lo
            T, s = move_profile(x1 - x, P.mow_feed, 0.3)
            segs.append({"name": "pass", "T": T, "patch": k, "row": r,
                         "f": (lambda t, y=y, s=s, x0=x, sg=(1 if x1 > x else -1):
                               (y, x0 + sg * s(t), P.mow_z, True))})
            x = x1
        t_up = (P.drive_z - P.mow_z) / P.rapid_z + 0.3
        segs.append({"name": "up", "T": t_up, "patch": k, "row": len(rows) - 1,
                     "f": (lambda t, T=t_up, y=y, x=x: (y, x, P.mow_z + (zd - P.mow_z) * ease(t / T), False))})
    T, s = move_profile(900.0, P.drive_speed, ACCEL)
    segs.append({"name": "away", "T": T + HOLD_END, "patch": len(PATCHES) - 1, "row": 0,
                 "f": (lambda t, y0=y, s=s, x0=x: (y0 - s(t), x0 * (1 - ease(t / 2.5)), zd, False))})
    return segs


TEXT = {
    "drive": "Rijden, camera ziet brandnetels boven het gras; X-slede gaat naast het bos staan",
    "probe": "Maaischijf 3000 rpm, Z zakt tot de pot het gras voelt",
    "lift": "20 mm terug: mesjes 50 mm boven de grond, pot hangt net boven het gras",
    "pass": "Maaien: X-slede %s met 150 mm/s",
    "step": "Robot schuift 190 mm naar voren voor de volgende baan",
    "up": "Bos gemaaid tot in het gras, Z omhoog naar de rijstand, schijf remt",
    "away": "Klaar: twee bossen brandnetels tot 5 cm gemaaid, snippers liggen in het gras",
}


def phase_text(f):
    if f["phase"] == "pass":
        return TEXT["pass"] % ("naar rechts" if f["dir"] > 0 else "naar links")
    if f["phase"] == "drive" and f["patch"] > 0:
        return "Door naar het volgende bos; X-slede gaat naast het bos staan"
    return TEXT[f["phase"]]


def prepare(dt=DT):
    stems = nettles()
    plans = [patch_plan(k, stems) for k in range(len(PATCHES))]
    frames = []
    t_total = 0.0
    angle = 0.0
    dist = 0.0
    spin_t = 0.0
    cut = set()
    prev = None
    for seg in segments(stems):
        n = max(1, int(round(seg["T"] / dt)))
        for k in range(n):
            t = (k + 1) * seg["T"] / n
            y, x, z, spinning = seg["f"](t)
            spin_t = spin_t + seg["T"] / n if spinning else 0.0
            rpm = P.mower_rpm * min(1.0, spin_t / SPINUP) if spinning else 0.0
            if rpm > 0:
                angle += SPIN_DEG
            prev = prev or (y, x)
            dist += abs(prev[0] - y)
            # stengels binnen de tipcirkel, ook halverwege het vorige frame (geen gaten bij 37 mm per frame)
            new = 0
            if rpm > 0:
                pts = [(x, y + C.SPINDLE_Y), (0.5 * (x + prev[1]), 0.5 * (y + prev[0]) + C.SPINDLE_Y)]
                for i, (sx, sy, h, _, _) in enumerate(stems):
                    if i not in cut and z < h and any((sx - px) ** 2 + (sy - py) ** 2 < CUT_R ** 2 for px, py in pts):
                        cut.add(i)
                        new += 1
            _, _, x_lo, x_hi = plans[seg["patch"]]
            in_patch = x_lo - CUT_R < x < x_hi + CUT_R
            if seg["name"] == "pass" and in_patch or new:
                power = C.mow_power()
            else:
                power = P.mow_idle_w * (rpm / P.mower_rpm) ** 3 if rpm else 0.0
            rim = build_dwd2.pot_rim(z)
            on_ground = rim <= 1e-6
            loads = C.axle_loads(x, 0.0, on_ground)
            n_row = len(plans[seg["patch"]][0])
            t_total += seg["T"] / n
            frames.append({"t": t_total, "phase": seg["name"], "patch": seg["patch"], "row": seg["row"],
                           "n_rows": n_row, "dir": (1 if x > prev[1] else -1), "robot_y": y, "x": x, "z": z,
                           "rim": rim, "pot_on_ground": on_ground, "rpm": rpm, "angle": angle, "power": power,
                           "wheels": loads["wheels_kg"], "front": loads["front_kg"], "rear": loads["rear_kg"],
                           "dist": dist, "cut": sorted(cut)})
            prev = (y, x)
    return frames


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def add(doc, name, shape, color, tr=0, visible=True):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    o.ViewObject.ShapeColor = color
    o.ViewObject.LineColor = color
    o.ViewObject.Transparency = tr
    o.ViewObject.Visibility = visible
    return o


def build():
    import Mesh
    BA = build_dwd2.load_robot()
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Dockweed drill v2 mowing nettles - animation"
    doc.Comment = ("Gegenereerd door animate_dwd2_nettles.py (niet opslaan nodig). Robot uit agbot design, "
                   "werktuig uit build_dwd2 met de maaischijf.")
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    build_dwd2.build_into(doc, robot, 0.0, P.drive_z, tool="mower")

    (x0, x1), (y0, y1) = TERRAIN
    add(doc, "anim_ground", Part.makeBox(x1 - x0, y1 - y0, 80.0, V(x0, y0, -80.0)), COLOR["ground"])
    holes = [(p["xc"], p["yc"], p["a"] + 10, p["b"] + 10) for p in PATCHES]
    tris = G.grass_triangles(TERRAIN[0], TERRAIN[1], holes)
    grass = doc.addObject("Mesh::Feature", "anim_grass")
    grass.Mesh = Mesh.Mesh([V(*pt) for tri in tris for pt in tri])
    vo = grass.ViewObject
    vo.ShapeColor = COLOR["grass"]
    vo.Lighting = "Two side"
    vo.DisplayMode = "Shaded"
    for k, (hx, hy, ha, hb) in enumerate(holes):
        e = Part.Ellipse(V(hx, hy, 0.5), ha, hb)
        add(doc, "anim_litter_%d" % k, Part.Face(Part.Wire(e.toShape())), COLOR["litter"])
    for i, (sx, sy, h, seed, _) in enumerate(nettles()):
        add(doc, "anim_nettle_%d" % i, G.nettle(sx, sy, h, seed), COLOR["nettle"])
        add(doc, "anim_stub_%d" % i, G.nettle_stub(sx, sy, P.mow_z), COLOR["stub"], visible=False)
        add(doc, "anim_mulch_%d" % i, G.nettle_mulch(sx, sy, seed), COLOR["mulch"], visible=False)
    build_dwd2.set_group_transparency(doc, "Pot", 65)      # schijf in de pot zichtbaar
    doc.recompute()
    _shown.clear()
    return doc


def _visible(doc, name, value):
    if _shown.get(name) != value:
        doc.getObject(name).ViewObject.Visibility = value
        _shown[name] = value


def apply_frame(doc, f):
    doc.getObject("Robot").Placement = build_dwd2.translation(y=f["robot_y"])
    rot = App.Rotation(V(1, 0, 0), math.degrees(f["dist"] / (P.robot_tire_d / 2)))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    build_dwd2.set_pose(doc, f["x"], f["z"], angle=f["angle"])
    cut = set(f["cut"])
    for i in range(sum(p["n"] for p in PATCHES)):
        _visible(doc, "anim_nettle_%d" % i, i not in cut)
        _visible(doc, "anim_stub_%d" % i, i in cut)
        _visible(doc, "anim_mulch_%d" % i, i in cut)


# ---------------------------------------------------------------------
# Camera en renderen
# ---------------------------------------------------------------------
CAM_WIDE = ((-2600.0, -2500.0, 1800.0), (0.0, -900.0, 450.0))     # oogverschuiving, doel t.o.v. (0, robot_y, 0)
CAM_CLOSE = ((-1900.0, -500.0, 1750.0), (0.0, -1150.0, 200.0))   # doel x volgt de spil voor de helft
WORK = ("probe", "lift", "pass", "step", "up")


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def camera_blend(frames):
    """Per frame 0 (wijd) .. 1 (dichtbij): dichtbij tijdens het maaien, wijd tijdens het rijden."""
    work = [1.0 if f["phase"] in WORK else 0.0 for f in frames]
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
    tgt = (tgt[0] + 0.5 * f["x"] * s, f["robot_y"] + tgt[1], tgt[2])
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(tgt[0] + eye[0], tgt[1] + eye[1], tgt[2] + eye[2]))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(20.0)
    cam.farDistance.setValue(60000.0)


def meta(f):
    total = sum(p["n"] for p in PATCHES)
    return {"mode": "mow", "t": round(f["t"], 2), "phase": f["phase"], "text": phase_text(f),
            "patch": f["patch"] + 1, "n_patches": len(PATCHES), "row": f["row"] + 1, "n_rows": f["n_rows"],
            "cut": len(f["cut"]), "n_stems": total, "x": round(f["x"]), "z": round(f["z"]),
            "rim": round(f["rim"]), "pot_on_ground": f["pot_on_ground"], "rpm": round(f["rpm"]),
            "power": round(f["power"]), "current": round(C.spindle_current(f["power"]), 1),
            "wheels": {k: round(v, 1) for k, v in f["wheels"].items()}, "front": round(f["front"]),
            "rear": round(f["rear"])}


def summary(frames=None):
    frames = frames or prepare()
    wheels = [v for f in frames for v in f["wheels"].values()]
    per_patch = []
    for k in range(len(PATCHES)):
        ts = [f["t"] for f in frames if f["patch"] == k and f["phase"] in WORK]
        per_patch.append(round(ts[-1] - ts[0] + DT, 1))
    mow = [f for f in frames if f["phase"] == "pass"]
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 1), "mowing_time_per_patch_s": per_patch,
            "rows_per_patch": [len(patch_plan(k, nettles())[0]) for k in range(len(PATCHES))],
            "x_range": (round(min(f["x"] for f in frames)), round(max(f["x"] for f in frames))),
            "z_range": (round(min(f["z"] for f in frames)), round(max(f["z"] for f in frames))),
            "power_range_w": (round(min(f["power"] for f in mow)), round(max(f["power"] for f in mow))),
            "wheel_kg_range": (round(min(wheels), 1), round(max(wheels), 1)),
            "front_kg_range": (round(min(f["front"] for f in frames)), round(max(f["front"] for f in frames))),
            "stems_cut": "%d / %d" % (len(frames[-1]["cut"]), sum(p["n"] for p in PATCHES))}


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


MOW_POSES = [(x, z) for x in (P.x_min, 0.0, P.x_max) for z in (P.drive_z, P.mow_z, P.mower_rim)]


def check_fit(doc=None, tol=1.0, poses=MOW_POSES):
    """Overlap tussen het robotmodel en het werktuig met maaischijf (X +-500, rijstand, maaihoogte, pot op de grond)."""
    doc = doc or App.getDocument(DOC_NAME)
    out = {}
    impl_objs = build_dwd2.implement_objects(doc)
    impl = {o.Name for o in impl_objs}
    robot = [o for o in doc.getObject("Robot").OutListRecursive if o.TypeId == "Part::Feature" and o.Name not in impl]
    for x, z in poses:
        build_dwd2.set_pose(doc, x, z)
        doc.recompute()
        rs = [(o, build_dwd2.global_shape(o)) for o in robot]
        mine = [(o, build_dwd2.global_shape(o)) for o in impl_objs]
        hits = []
        for oa, sa in rs:
            for ob, sb in mine:
                if sa.BoundBox.intersect(sb.BoundBox):
                    vol = sa.common(sb).Volume
                    if vol > tol:
                        hits.append((oa.Label, ob.Label, round(vol, 1)))
        out[(x, z)] = hits
    build_dwd2.set_pose(doc, 0.0, P.drive_z)
    return out
