"""Bodemvolging van de eenvoudige toediener over dezelfde hobbelige strook als de geavanceerde variant
(puur Python, geen FreeCAD nodig; animate_lfs.py gebruikt dezelfde rekenregels voor de animatie).

Per robotpositie:
- de robot rust met zijn vier wielen op het maaiveld (vlak door de wielpunten: hoogte, stampen, rollen),
  precies zoals ../advanced/animate_lfa.py;
- het hefraam zakt tot het eerste dieptewiel de grond raakt, binnen het zweefbereik dat de actuatorlengte en het
  langgat toelaten (de messen hangen star aan de balk);
- per rij volgt de diepte van de mespunt en de hoek van het mes.

Gebruik:
    import lfs_ground
    frames = lfs_ground.prepare()          # rijplan + houding per frame
    lfs_ground.summary(frames)             # bereik mesdiepte, zweefhoek, aanslagen
    lfs_ground.compare()                   # tabel eenvoudig vs geavanceerd (ground_advanced_reference.json)
"""
import json
import math
import os

import lfs_params as P
import lfs_kin as K

FOLDER = os.path.dirname(os.path.abspath(__file__))
ADVANCED_JSON = os.path.join(FOLDER, "ground_advanced_reference.json")

# ---------------------------------------------------------------------
# Rijplan (gelijk aan de geavanceerde animatie; de actuator is hier trager)
# ---------------------------------------------------------------------
SPEED = 750.0          # mm/s werksnelheid (2,7 km/h)
ACCEL_TIME = 1.2
DECEL_TIME = 1.2
ACT_SPEED = 25.0       # mm/s, goedkope actuator 1000 N (heffen ca. 8 s)
HOLD_START = 0.6
HOLD_END = 0.8
Y_START = 0.0          # robotmidden bij de start
Y_LIFT = 6300.0        # robotmidden waar het heffen begint
DRIVE_GAP = 25.0       # robot rijdt weg als de mespunten nog zoveel mm boven het maaiveld hangen

# ---------------------------------------------------------------------
# Maaiveld: zelfde functie en waarden als ../advanced/animate_lfa.py
# ---------------------------------------------------------------------
BUMPS = (                    # x, y, hoogte, straal
    (-200.0, 900.0, 34.0, 150.0),     # molshoop onder rij 2
    (0.0, 1750.0, 24.0, 120.0),       # kleine bult onder rij 3
    (260.0, 2450.0, -26.0, 240.0),    # kuil onder rij 4
    (430.0, 4300.0, 28.0, 170.0),     # bult onder rij 5 en het rechter robotwiel
    (-380.0, 5600.0, -20.0, 220.0),   # kuil onder rij 1 en het linker robotwiel
)
RIDGES = ((3300.0, 20.0, 150.0),)     # y, hoogte, breedte: hele werkbreedte tegelijk


def terrain(x, y):
    h = 14.0 * math.sin(2.0 * math.pi * y / 2600.0 + 0.4)
    h += 10.0 * max(-1.5, min(1.5, x / 500.0)) * math.sin(2.0 * math.pi * y / 3700.0 + 1.3)
    for bx, by, a, r in BUMPS:
        h += a * math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (r * r))
    for ry, a, w in RIDGES:
        h += a * math.exp(-((y - ry) / w) ** 2)
    return h


# ---------------------------------------------------------------------
# Robot op vier wielen
# ---------------------------------------------------------------------
def robot_pose(y):
    """(hoogte c, stampen graden, rollen graden) van de robot met het midden op y."""
    hx = P.robot_wheel_x
    hy = 500.0
    h_rl, h_rr = terrain(-hx, y - hy), terrain(hx, y - hy)
    h_fl, h_fr = terrain(-hx, y + hy), terrain(hx, y + hy)
    a = ((h_rr + h_fr) - (h_rl + h_fl)) / (2.0 * 2 * hx)
    b = ((h_fl + h_fr) - (h_rl + h_rr)) / (2.0 * 2 * hy)
    c = (h_rl + h_rr + h_fl + h_fr) / 4.0
    return c, math.degrees(math.atan(b)), -math.degrees(math.atan(a))


def _matrix(pitch, roll):
    """R = Rx(pitch) * Ry(roll), zelfde volgorde als App.Rotation(X, pitch).multiply(App.Rotation(Y, roll))."""
    p, r = math.radians(pitch), math.radians(roll)
    cp, sp, cr, sr = math.cos(p), math.sin(p), math.cos(r), math.sin(r)
    rx = ((1, 0, 0), (0, cp, -sp), (0, sp, cp))
    ry = ((cr, 0, sr), (0, 1, 0), (-sr, 0, cr))
    return tuple(tuple(sum(rx[i][k] * ry[k][j] for k in range(3)) for j in range(3)) for i in range(3))


class Pose:
    """Werktuigcoordinaten -> wereld voor een robot met het midden op y."""

    def __init__(self, y):
        self.y = y
        self.c, self.pitch, self.roll = robot_pose(y)
        self.m = _matrix(self.pitch, self.roll)

    def world(self, x, yi, z):
        v = (x, yi + P.robot_mount_y, z)
        m = self.m
        return (sum(m[0][k] * v[k] for k in range(3)),
                sum(m[1][k] * v[k] for k in range(3)) + self.y,
                sum(m[2][k] * v[k] for k in range(3)) + self.c)

    def frame_point(self, x, pt, psi):
        """Punt van het hefraam (werkstand-coordinaten pt = (y, z)) bij hefhoek psi, in wereldcoordinaten."""
        yy, zz = K.rot_up(pt, psi)
        return self.world(x, yy, zz)


# ---------------------------------------------------------------------
# Hefraam: zweefbereik bij een actuatorlengte en contact van de dieptewielen
# ---------------------------------------------------------------------
def float_range(length=P.act_extended):
    """(laagste, hoogste) hefhoek bij actuatorlengte length: stangoog onderin / bovenin het langgat."""
    lo_end, hi_end = K.slot_ends()
    lo = K._bisect(lambda a: K.dist(lo_end, K.frame_pin(a)) - length, -40.0, 70.0)
    hi = K._bisect(lambda a: K.dist(hi_end, K.frame_pin(a)) - length, -40.0, 70.0)
    return lo, hi


def wheel_gap(pose, x, psi):
    w = pose.frame_point(x, P.gw_axle, psi)
    return w[2] - P.gw_d / 2.0 - terrain(w[0], w[1])


def wheel_contact_angle(pose, x, lo=-40.0, hi=70.0):
    """Hefhoek waarbij dieptewiel x net de grond raakt."""
    if wheel_gap(pose, x, lo) > 0.0:
        return lo
    return K._bisect(lambda a: wheel_gap(pose, x, a), lo, hi)


def solve(y, length=P.act_extended):
    """Houding bij robotpositie y en actuatorlengte length."""
    pose = Pose(y)
    lo, hi = float_range(length)
    contact = [wheel_contact_angle(pose, x) for x in P.gw_x]
    psi_free = max(contact)
    psi = min(hi, max(lo, psi_free))
    tip = K.knife_tip()
    rows = []
    for x in P.row_x:
        t = pose.frame_point(x, tip, psi)
        rows.append({"depth": terrain(t[0], t[1]) - t[2], "xy": (t[0], t[1])})
    gaps = [wheel_gap(pose, x, psi) for x in P.gw_x]
    return {"y": y, "pose": pose, "pitch": pose.pitch, "roll": pose.roll, "psi": psi, "length": length,
            "hanging": psi_free < lo - 1e-6, "blocked": psi_free > hi + 1e-6, "rows": rows,
            "wheel_gap": gaps, "knife_angle": P.knife_angle - psi + pose.pitch}


# ---------------------------------------------------------------------
# Rijplan
# ---------------------------------------------------------------------
def simulate(fps=12):
    """Rijplan: tijd, positie y van het robotmidden, snelheid v (mm/s), actuatorlengte L (mm) en fase."""
    n_sub = 10
    dt = 1.0 / (fps * n_sub)
    t, y, v = 0.0, Y_START, 0.0
    L = P.act_retracted
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
            L = min(P.act_extended, L + ACT_SPEED * dt)
            if v > 0.0 or min(r["depth"] for r in solve(y, L)["rows"]) > -DRIVE_GAP:
                v = min(SPEED, v + SPEED / ACCEL_TIME * dt)
            if L >= P.act_extended and v >= SPEED:
                phase = "work"
        elif phase == "work":
            if y >= Y_LIFT:
                phase, t_phase = "raise", t
        elif phase == "raise":
            L = max(P.act_retracted, L - ACT_SPEED * dt)
            v = max(0.0, v - SPEED / DECEL_TIME * dt)
            if L <= P.act_retracted and v <= 0.0:
                phase, t_phase = "end", t
        else:
            if t - t_phase >= HOLD_END:
                break
        y += v * dt
        t += dt
        step += 1
    return frames


def prepare(fps=12):
    out = []
    for f in simulate(fps):
        f.update(solve(f["y"], f["L"]))
        out.append(f)
    return out


# ---------------------------------------------------------------------
# Samenvatting en vergelijking
# ---------------------------------------------------------------------
def work_frames(frames):
    return [f for f in frames if f["phase"] == "work"]


def summary(frames=None):
    frames = frames or prepare()
    work = work_frames(frames)
    depth = [r["depth"] for f in work for r in f["rows"]]
    per_row = [[f["rows"][i]["depth"] for f in work] for i in range(len(P.row_x))]
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 2), "work_frames": len(work),
            "knife_depth_range": (round(min(depth), 1), round(max(depth), 1)),
            "knife_depth_mean": round(sum(depth) / len(depth), 1),
            "knife_depth_sd": round(_sd(depth), 1),
            "depth_range_per_row": [(round(min(d)), round(max(d))) for d in per_row],
            "share_15_65": round(100.0 * sum(1 for d in depth if 15.0 <= d <= 65.0) / len(depth), 1),
            "knife_out_of_soil": sum(1 for d in depth if d <= 0.0),
            "psi_range": (round(min(f["psi"] for f in work), 1), round(max(f["psi"] for f in work), 1)),
            "knife_angle_range": (round(min(f["knife_angle"] for f in work), 1),
                                  round(max(f["knife_angle"] for f in work), 1)),
            "hanging_frames": sum(1 for f in work if f["hanging"]),
            "blocked_frames": sum(1 for f in work if f["blocked"]),
            "wheel_off_ground": sum(1 for f in work for g in f["wheel_gap"] if g > 5.0),
            "pitch_range": (round(min(f["pitch"] for f in frames), 2), round(max(f["pitch"] for f in frames), 2)),
            "roll_range": (round(min(f["roll"] for f in frames), 2), round(max(f["roll"] for f in frames), 2))}


def _sd(values):
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


def profile(step=50.0, y0=None, y1=None):
    """Mesdiepte per rij in werkstand (actuator uit) langs de strook, op vaste robotposities."""
    y0 = 600.0 if y0 is None else y0
    y1 = Y_LIFT if y1 is None else y1
    out = []
    y = y0
    while y <= y1 + 1e-6:
        s = solve(y)
        out.append({"y": y, "knife_y": s["rows"][0]["xy"][1], "depth": [r["depth"] for r in s["rows"]],
                    "psi": s["psi"], "pitch": s["pitch"], "roll": s["roll"], "hanging": s["hanging"],
                    "blocked": s["blocked"]})
        y += step
    return out


def load_advanced():
    with open(ADVANCED_JSON, encoding="utf-8") as handle:
        return json.load(handle)


def compare():
    """Kerngetallen werkstand: eenvoudig (dit model) en geavanceerd (uit ground_advanced_reference.json)."""
    s = summary()
    adv = load_advanced()
    work = [f for f in adv["frames"] if f["phase"] == "work"]
    depth = [d for f in work for d in f["depth"]]
    return {"simple": s,
            "advanced": {"work_frames": len(work),
                         "knife_depth_range": (round(min(depth), 1), round(max(depth), 1)),
                         "knife_depth_mean": round(sum(depth) / len(depth), 1),
                         "knife_depth_sd": round(_sd(depth), 1),
                         "share_15_65": round(100.0 * sum(1 for d in depth if 15.0 <= d <= 65.0) / len(depth), 1),
                         "summary": adv.get("summary")}}


if __name__ == "__main__":
    for k, v in summary().items():
        print(k, v)
