"""Animatie: de toediener achter de Bruut OpenAgbot, rijdend over een hobbelige strook.

Bouwt een apart document (de robotbestanden in "agbot design" worden niet aangepast):
robot uit build_agbot + toediener uit build_lfa + golvend maaiveld met bulten, een kuil en een dwarsrichel.
Per frame:
- robot rust met 4 wielen op het maaiveld (vlak door de wielpunten: hoogte, stampen, rollen);
- toolbar hangt vast aan de actuator (werkstand) of wordt geheven / gezakt;
- elk element en het loopwiel zoeken hun eigen armhoek waarbij dieptering / wiel de grond raakt
  (tussen de aanslagen), veerpoten en slangen rekken mee;
- achter de messen verschijnen de sleuven, schijven en wielen draaien mee.

Gebruik in FreeCAD:
    import animate_lfa
    animate_lfa.build()                       # document opbouwen
    animate_lfa.play()                        # live afspelen, animate_lfa.stop()
    animate_lfa.render_all(r"C:\\temp\\lfa_frames")   # frames renderen (in stukken: render_frames)
    import make_gif_lfa; make_gif_lfa.main(r"C:\\temp\\lfa_frames", r"previews\\animation_strip_ground_following.gif")
"""
import json
import math
import os
import sys

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lfa_params as P
import lfa_parts as G
import lfa_calc as C
import build_lfa

FOLDER = os.path.dirname(os.path.abspath(__file__))
AGBOT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "agbot design")
DOC_NAME = "LFA_on_robot_animation"

# ---------------------------------------------------------------------
# Rijplan
# ---------------------------------------------------------------------
SPEED = 750.0          # mm/s werksnelheid (2,7 km/h)
ACCEL_TIME = 1.2
DECEL_TIME = 1.2
ACT_SPEED = 60.0       # mm/s actuator: 148 mm slag in ca. 2,5 s
HOLD_START = 0.6
HOLD_END = 0.8
Y_START = 0.0          # robotmidden bij de start
Y_LIFT = 6300.0        # robotmidden waar het heffen begint

# armhoeken (graden, + = arm zakt): aanslagen
UNIT_UP = -16.0        # ca. 66 mm omhoog (veer bijna blokvast)
WHEEL_UP = -20.0
WHEEL_N = 150.0        # neerdruk loopwiel (torsieveer + gewicht arm)
BLOCKED_N = 5000.0     # element tegen de bovenaanslag: grond duwt de balk omhoog

# ---------------------------------------------------------------------
# Maaiveld (mm): lange golf, dwarshelling die wisselt, bulten/kuil en een dwarsrichel
# ---------------------------------------------------------------------
BUMPS = (                    # x, y, hoogte, straal
    (-200.0, 900.0, 34.0, 150.0),     # molshoop onder rij 2
    (0.0, 1750.0, 24.0, 120.0),       # kleine bult onder rij 3
    (260.0, 2450.0, -26.0, 240.0),    # kuil onder rij 4 en het loopwiel
    (430.0, 4300.0, 28.0, 170.0),     # bult onder rij 5 en het rechter robotwiel
    (-380.0, 5600.0, -20.0, 220.0),   # kuil onder rij 1 en het linker robotwiel
)
RIDGES = ((3300.0, 20.0, 150.0),)     # y, hoogte, breedte: hele werkbreedte tegelijk
TERRAIN_X = (-1500.0, 1500.0)
TERRAIN_Y = (-2600.0, 9400.0)

COLOR = {"grass": (0.45, 0.62, 0.31), "lines": (0.35, 0.50, 0.24), "slot": (0.20, 0.13, 0.08)}
SLOT_HALF = 7.0

_timer = None
_play = {}
_cache = {"strut": {}, "hose": {}, "act": {}}
_base = {}


def terrain(x, y):
    h = 14.0 * math.sin(2.0 * math.pi * y / 2600.0 + 0.4)
    h += 10.0 * max(-1.5, min(1.5, x / 500.0)) * math.sin(2.0 * math.pi * y / 3700.0 + 1.3)
    for bx, by, a, r in BUMPS:
        h += a * math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (r * r))
    for ry, a, w in RIDGES:
        h += a * math.exp(-((y - ry) / w) ** 2)
    return h


TERRAIN_OUTER = (-6000.0, -4000.0, -2600.0, -2000.0, 2000.0, 2600.0, 4000.0, 6000.0)


def terrain_shapes(step=100.0, line_step=250.0):
    # fijn raster over de strook (bulten), grof daarbuiten zodat de rand buiten beeld valt
    fine = [TERRAIN_X[0] + i * step for i in range(int((TERRAIN_X[1] - TERRAIN_X[0]) / step) + 1)]
    xs = sorted(set(fine + list(TERRAIN_OUTER)))
    ys = [TERRAIN_Y[0] + i * step for i in range(int((TERRAIN_Y[1] - TERRAIN_Y[0]) / step) + 1)]
    surf = Part.BSplineSurface()
    surf.interpolate([[V(x, y, terrain(x, y)) for y in ys] for x in xs])
    face = surf.toShape()
    lines = []
    x_line = [xs[0] + i * step for i in range(int((xs[-1] - xs[0]) / step) + 1)]
    y = TERRAIN_Y[0]
    while y <= TERRAIN_Y[1] + 1e-6:
        c = Part.BSplineCurve()
        c.interpolate([V(x, y, terrain(x, y) + 1.5) for x in x_line])
        lines.append(c.toShape())
        y += line_step
    x = xs[0]
    while x <= xs[-1] + 1e-6:
        c = Part.BSplineCurve()
        c.interpolate([V(x, yy, terrain(x, yy) + 1.5) for yy in ys])
        lines.append(c.toShape())
        x += line_step
    return face, Part.makeCompound(lines)


def slot_ribbon(points):
    if len(points) < 2:
        return None
    pts = points[::2] + ([points[-1]] if len(points) % 2 == 0 else [])
    left = Part.makePolygon([V(x - SLOT_HALF, y, terrain(x - SLOT_HALF, y) + 2.0) for x, y in pts])
    right = Part.makePolygon([V(x + SLOT_HALF, y, terrain(x + SLOT_HALF, y) + 2.0) for x, y in pts])
    return Part.makeRuledSurface(left, right)


# ---------------------------------------------------------------------
# Rijplan simuleren
# ---------------------------------------------------------------------
def simulate(fps=12):
    """Rijplan: snelheid v (mm/s), positie y van het robotmidden en actuatorlengte L (mm)."""
    n_sub = 10
    dt = 1.0 / (fps * n_sub)
    t = 0.0
    y = Y_START
    v = 0.0
    l_min = build_lfa.ab_length(P.lift_height)
    l_max = float(P.act_extended)
    act_time = (l_max - l_min) / ACT_SPEED
    L = l_min
    phase = "hold"
    t_phase = 0.0
    frames = []
    step = 0
    while True:
        if step % n_sub == 0:
            frames.append({"t": t, "y": y, "v": v, "L": L, "phase": phase})
        if phase == "hold":
            if t >= HOLD_START:
                phase, t_phase = "lower", t
        elif phase == "lower":
            v = min(SPEED, v + SPEED / ACCEL_TIME * dt)
            L = min(l_max, L + ACT_SPEED * dt)
            if L >= l_max and v >= SPEED:
                phase = "work"
        elif phase == "work":
            if y >= Y_LIFT:
                phase, t_phase = "raise", t
        elif phase == "raise":
            L = max(l_min, L - ACT_SPEED * dt)
            if t - t_phase >= act_time - DECEL_TIME:
                v = max(0.0, v - SPEED / DECEL_TIME * dt)
            if L <= l_min and v <= 0.0:
                phase, t_phase = "end", t
        else:
            if t - t_phase >= HOLD_END:
                break
        y += v * dt
        t += dt
        step += 1
    return frames


# ---------------------------------------------------------------------
# Houding per frame
# ---------------------------------------------------------------------
def robot_placement(y):
    hx = P.robot_wheel_x
    hy = 500.0
    h_rl, h_rr = terrain(-hx, y - hy), terrain(hx, y - hy)
    h_fl, h_fr = terrain(-hx, y + hy), terrain(hx, y + hy)
    a = ((h_rr + h_fr) - (h_rl + h_fl)) / (2.0 * 2 * hx)     # helling in x
    b = ((h_fl + h_fr) - (h_rl + h_rr)) / (2.0 * 2 * hy)     # helling in y
    c = (h_rl + h_rr + h_fl + h_fr) / 4.0
    pitch = math.degrees(math.atan(b))
    roll = -math.degrees(math.atan(a))
    rot = App.Rotation(V(1, 0, 0), pitch).multiply(App.Rotation(V(0, 1, 0), roll))
    return App.Placement(V(0.0, y, c), rot), pitch, roll


def solve_arm(chain, axis_c, point, radius, lo, hi, iters=22):
    """Armhoek (graden) waarbij een cirkel (wiel/ring, straal radius) om point de grond raakt.
    chain = placement tot het frame van de arm, axis_c = (y, z) draaipunt in dat frame.
    Geeft (hoek, contact, geblokkeerd)."""
    def gap(a):
        w = chain.multiply(build_lfa.rotation_x(a, axis_c)).multVec(V(*point))
        return w.z - radius - terrain(w.x, w.y)
    if gap(hi) >= 0.0:
        return hi, False, False
    if gap(lo) <= 0.0:
        return lo, True, True
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if gap(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), True, False


GW_PT = (float(P.gw_x), P.jack[0] + P.gw_wheel_rel[0], P.jack[1] + P.gw_wheel_rel[1])
DISC_PT = (0.0, P.disc_y, P.disc_z)


def bar_placement(pl_robot, lift):
    theta, dy, dz = build_lfa.lift_state(lift)
    return pl_robot.multiply(build_lfa.translation(0.0, P.robot_mount_y + dy, dz))


def ground_forces(pl_robot, lift):
    """Armhoeken en grondkrachten bij balkhoogte lift. Geeft (som krachten N, elementen, loopwiel)."""
    bar = bar_placement(pl_robot, lift)
    units = []
    total = 0.0
    for x in P.row_x:
        a, contact, blocked = solve_arm(bar.multiply(build_lfa.translation(x=x)), P.u_pivot, DISC_PT,
                                        P.band_d / 2.0, UNIT_UP, P.unit_drop_deg)
        force = BLOCKED_N if blocked else (C.unit_downforce(drop=a)[0] if contact else 0.0)
        total += force
        units.append({"a": a, "contact": contact, "force": force})
    ga, gcontact, _ = solve_arm(bar, P.jack, GW_PT, P.gw_d / 2.0, WHEEL_UP, P.wheel_drop_deg)
    total += WHEEL_N if gcontact else 0.0
    return total, units, (ga, gcontact)


def solve_frame(frame):
    """Zweefstand: de balk zakt tot de grond (elementen + loopwiel) het bewegende gewicht draagt, binnen
    het zweefbereik dat de actuatorlengte L en het langgat toelaten."""
    pl_robot, pitch, roll = robot_placement(frame["y"])
    weight = C.MODEL["moving_kg"] * C.G_ACC
    f_lo, f_hi = build_lfa.float_range(frame["L"])
    total_lo, units, wheel = ground_forces(pl_robot, f_lo)
    lift, hanging = f_lo, True
    if total_lo > weight:
        hanging = False
        total_hi, units_hi, wheel_hi = ground_forces(pl_robot, f_hi)
        if total_hi >= weight:
            lift, units, wheel = f_hi, units_hi, wheel_hi
        else:
            lo, hi = f_lo, f_hi
            for _ in range(20):
                mid = 0.5 * (lo + hi)
                total, units, wheel = ground_forces(pl_robot, mid)
                if total > weight:
                    lo = mid
                else:
                    hi = mid
            lift = 0.5 * (lo + hi)
            total, units, wheel = ground_forces(pl_robot, lift)
    theta, dy, dz = build_lfa.lift_state(lift)
    bar = bar_placement(pl_robot, lift)
    tip = G.rel_disc(P.knife_tip_rel)
    for x, u in zip(P.row_x, units):
        k = bar.multiply(build_lfa.translation(x=x)).multiply(build_lfa.rotation_x(u["a"], P.u_pivot)).multVec(
            V(0.0, tip[0], tip[1]))
        u["depth"] = terrain(k.x, k.y) - k.z
        u["knife"] = (k.x, k.y)
        u["dz"] = C.disc_dz(u["a"])
    ga, gcontact = wheel
    gz = G.rot_yz((GW_PT[1], GW_PT[2]), ga, P.jack)[1] - GW_PT[2]
    frame.update({"pl": pl_robot, "pitch": pitch, "roll": roll, "lift": lift, "hanging": hanging,
                  "theta": theta, "dy": dy, "dz": dz, "units": units, "wa": ga, "wcontact": gcontact, "wdz": gz})
    return frame


def prepare(fps=12):
    frames = [solve_frame(f) for f in simulate(fps)]
    dist = 0.0
    spin = {"robot": 0.0, "disc": [0.0] * len(P.row_x), "wheel": 0.0}
    applied = 0.0
    slots = [[] for _ in P.row_x]
    prev_y = frames[0]["y"]
    eff_r = P.gw_rolling_circ / (2.0 * math.pi)
    for f in frames:
        ds = f["y"] - prev_y
        prev_y = f["y"]
        dist += ds
        spin["robot"] += ds / P.robot_tire_d * 2.0
        for i, u in enumerate(f["units"]):
            if u["contact"]:
                spin["disc"][i] += ds / (P.band_d / 2.0)
            if u["depth"] > 2.0:
                slots[i].append(u["knife"])
        if f["wcontact"]:
            spin["wheel"] += ds / eff_r
            applied += ds / 1000.0 * P.work_width / 1000.0 * 505.0 / 10000.0
        f["dist"] = dist
        f["spin"] = {"robot": spin["robot"], "disc": list(spin["disc"]), "wheel": spin["wheel"]}
        f["slots"] = [len(s) for s in slots]
        f["applied"] = applied
        ratio = P.z_wheel / float(P.z_jack)
        f["pump_rpm"] = (f["v"] / eff_r * 60.0 / (2 * math.pi)) * ratio if f["wcontact"] else 0.0
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
    doc.Label = "LFA on robot - animation"
    doc.Comment = "Gegenereerd door animate_lfa.py (niet opslaan nodig). Robot uit agbot design, toediener uit build_lfa."
    robot = BA.new_part(doc, None, "Robot", "Bruut_OpenAgbot_robot")
    BA.build_chassis(doc, robot)
    shapes = BA.make_shapes()
    for tag in ("RL", "RR", "FL", "FR"):
        BA.build_wheel_unit(doc, robot, tag, shapes, 0.0)
    build_lfa.build_into(doc, robot, 0.0, build_lfa.translation(0.0, P.robot_mount_y, 0.0))

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


SPIN_UNIT = ("disc", "hub", "band_l", "band_r")
SPIN_WHEEL = ("gw_wheel", "gw_sprocket", "gw_axle")


def record_base(doc):
    _base.clear()
    names = ["link_%s_%s" % (lv, sd) for lv in ("upper", "lower") for sd in ("left", "right")]
    names += ["U%d_%s" % (n + 1, k) for n in range(len(P.row_x)) for k in SPIN_UNIT]
    names += list(SPIN_WHEEL) + ["jack_sprocket"]
    for n in names:
        _base[n] = doc.getObject(n).Placement
    for c in _cache.values():
        c.clear()


def spin_about(name, angle, center, doc):
    doc.getObject(name).Placement = build_lfa.rotation_x(angle, center).multiply(_base[name])


def strut_shapes(a):
    key = round(a * 4.0) / 4.0
    if key not in _cache["strut"]:
        rod, spring, _ = G.u_strut(key)
        _cache["strut"][key] = (rod, spring)
    return _cache["strut"][key]


def hose_shape(i, a):
    key = (i, round(a * 4.0) / 4.0)
    if key not in _cache["hose"]:
        _cache["hose"][key] = G.outlet_hose(i, P.row_x[i], key[1])
    return _cache["hose"][key]


def actuator_shapes(lift, length):
    key = (round(lift, 1), round(length, 1))
    if key not in _cache["act"]:
        a, b = build_lfa.actuator_points(key[0], key[1])
        _cache["act"][key] = G.actuator(b, a)
    return _cache["act"][key]


def apply_frame(doc, f, slots=None):
    doc.getObject("Robot").Placement = f["pl"]
    rot = App.Rotation(V(1, 0, 0), -math.degrees(f["spin"]["robot"]))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("%s_%s" % (tag, part)).Placement = App.Placement(V(0, 0, 0), rot)
    # heffen
    doc.getObject("Toolbar_assembly").Placement = build_lfa.translation(0.0, f["dy"], f["dz"])
    for lv, z in (("upper", P.pin_upper_z), ("lower", P.pin_lower_z)):
        for sd in ("left", "right"):
            n = "link_%s_%s" % (lv, sd)
            doc.getObject(n).Placement = build_lfa.rotation_x(-f["theta"], (P.pin_front_y, z)).multiply(_base[n])
    body, rod = actuator_shapes(f["lift"], f["L"])
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod
    # elementen
    for i, u in enumerate(f["units"]):
        n = i + 1
        doc.getObject("Unit_%d_arm" % n).Placement = build_lfa.rotation_x(u["a"], P.u_pivot)
        rod_s, spring_s = strut_shapes(u["a"])
        doc.getObject("U%d_strut_rod" % n).Shape = rod_s
        doc.getObject("U%d_spring" % n).Shape = spring_s
        doc.getObject("hose_%d" % n).Shape = hose_shape(i, u["a"])
        ang = -math.degrees(f["spin"]["disc"][i])
        for k in SPIN_UNIT:
            spin_about("U%d_%s" % (n, k), ang, (P.disc_y, P.disc_z), doc)
    # loopwiel en pomp
    doc.getObject("Ground_wheel_arm").Placement = build_lfa.rotation_x(f["wa"], P.jack)
    wc = (P.jack[0] + P.gw_wheel_rel[0], P.jack[1] + P.gw_wheel_rel[1])
    wang = -math.degrees(f["spin"]["wheel"])
    for k in SPIN_WHEEL:
        spin_about(k, wang, wc, doc)
    spin_about("jack_sprocket", wang * P.z_wheel / float(P.z_jack), P.jack, doc)
    # sleuven
    if slots is not None:
        for i, s in enumerate(slots):
            shape = slot_ribbon(s[:f["slots"][i]])
            obj = doc.getObject("anim_slot_%d" % (i + 1))
            obj.Shape = shape if shape is not None else Part.Shape()


def reset(doc=None):
    """Terug naar het begin van de animatie (geheven, op de startplek)."""
    doc = doc or App.getDocument(DOC_NAME)
    frames, slots = prepare()
    apply_frame(doc, frames[0], slots)


# ---------------------------------------------------------------------
# Camera en renderen
# ---------------------------------------------------------------------
CAM_HIGH = ((2500.0, -2300.0, 1500.0), -650.0, 350.0)     # oogverschuiving, doel-y t.o.v. robot, doel-z
CAM_LOW = ((1800.0, -1650.0, 330.0), -1250.0, 170.0)


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def camera_blend(f, frames):
    t = f["t"]
    t_low0, t_low1 = 3.2, 5.0
    t_raise = next((g["t"] for g in frames if g["phase"] == "raise"), frames[-1]["t"])
    s = smooth((t - t_low0) / (t_low1 - t_low0)) * (1.0 - smooth((t - t_raise) / 1.8))
    return s


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
    return {"t": round(f["t"], 3), "v": round(f["v"], 1), "dist": round(f["dist"], 1), "lift": round(f["lift"], 1),
            "act_len": round(f["L"], 1), "hanging": f["hanging"],
            "state": STATE_NL[f["phase"]], "pitch": round(f["pitch"], 2), "roll": round(f["roll"], 2),
            "unit_dz": [round(u["dz"], 1) for u in f["units"]], "unit_contact": [u["contact"] for u in f["units"]],
            "depth": [round(u["depth"], 1) for u in f["units"]], "wheel_dz": round(f["wdz"], 1),
            "wheel_contact": f["wcontact"], "pump_rpm": round(f["pump_rpm"], 1), "applied_l": round(f["applied"], 3)}


def summary(frames=None):
    frames = frames or prepare()[0]
    work = [f for f in frames if f["phase"] == "work"]
    dz = [u["dz"] for f in work for u in f["units"]]
    depth = [u["depth"] for f in work for u in f["units"]]
    stops = sum(1 for f in work for u in f["units"] if not u["contact"] or u["a"] <= UNIT_UP + 1e-6)
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 2),
            "bar_float_range": (round(min(f["lift"] for f in work), 1), round(max(f["lift"] for f in work), 1)),
            "bar_hanging_frames": sum(1 for f in work if f["hanging"]),
            "unit_force_range": (round(min(u["force"] for f in work for u in f["units"])),
                                 round(max(u["force"] for f in work for u in f["units"]))),
            "unit_dz_range": (round(min(dz), 1), round(max(dz), 1)),
            "knife_depth_range": (round(min(depth), 1), round(max(depth), 1)),
            "wheel_dz_range": (round(min(f["wdz"] for f in work), 1), round(max(f["wdz"] for f in work), 1)),
            "pitch_range": (round(min(f["pitch"] for f in frames), 2), round(max(f["pitch"] for f in frames), 2)),
            "roll_range": (round(min(f["roll"] for f in frames), 2), round(max(f["roll"] for f in frames), 2)),
            "unit_at_stop_frames": stops, "wheel_lost_contact": sum(1 for f in work if not f["wcontact"])}


def render_frames(folder, first=0, count=None, fps=12, size=(720, 480)):
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


def render_all(folder, fps=12, size=(720, 480)):
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 30, fps, size)
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
    """Overlap tussen het echte robotmodel en de toediener (werkstand, robot vlak)."""
    doc = doc or App.getDocument(DOC_NAME)
    robot_objs, lfa_objs = [], []
    lfa_names = {o.Name for o in doc.getObject("Applicator").OutListRecursive}
    for o in doc.getObject("Robot").OutListRecursive:
        if o.TypeId != "Part::Feature" or not o.ViewObject.Visibility:
            continue
        (lfa_objs if o.Name in lfa_names else robot_objs).append((o, build_lfa.global_shape(o)))
    hits = []
    for oa, sa in robot_objs:
        for ob, sb in lfa_objs:
            if sa.BoundBox.intersect(sb.BoundBox):
                vol = sa.common(sb).Volume
                if vol > tol:
                    hits.append((oa.Label, ob.Label, round(vol, 1)))
    return hits
