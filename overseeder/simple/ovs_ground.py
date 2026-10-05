"""Bodemvolging van de doorzaaimachine over dezelfde hobbelige strook als de toedieners
(puur Python, geen FreeCAD nodig).

Per robotpositie:
- de robot rust met zijn vier wielen op het maaiveld (vlak door de wielpunten: hoogte, stampen, rollen),
  precies zoals ../../liquid fertilezer applicator/simple_v2/lfs2_ground.py;
- elke sleeparm draait tot de dieptering op de schijf het maaiveld raakt (of hangt op de aanslag);
- de aandrukrol volgt het maaiveld op zijn eigen rolarm (torsieveer);
- de veerkracht volgt uit de armhoek, de kracht op de dieptering uit de armbalans (ovs_calc.unit_band); de
  dieptering zakt iets in (BAND_SINK), en bij te weinig neerdruk gaat de schijf minder diep;
- het hefraam zweeft in het langgat tot de grondkrachten gelijk zijn aan het gewicht plus de duw van de
  gasveren (ovs_kin.gas_moment, robotgewicht via de actuator).
Uitkomst per rij: snijdiepte van de schijf (= zaaidiepte, het zaad valt op de bodem van de sleuf), diepte van de
zaaischoen, kracht op de aandrukrol.

Gebruik:
    import ovs_ground
    ovs_ground.summary()                 # 80 robotposities in werkstand, zelfde als de toedieners
    ovs_ground.compare_v2()              # snede van de schijf van simple_v2 (starre balk) op dezelfde posities
"""
import importlib.util
import json
import math
import os

import ovs_params as P
import ovs_kin as K
import ovs_calc as C

FOLDER = os.path.dirname(os.path.abspath(__file__))
V2_FOLDER = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "liquid fertilezer applicator", "simple_v2")
ADVANCED_JSON = os.path.join(V2_FOLDER, "ground_advanced_reference.json")

# ---------------------------------------------------------------------
# Maaiveld: zelfde functie en waarden als de toedieners
# ---------------------------------------------------------------------
BUMPS = (                    # x, y, hoogte, straal
    (-200.0, 900.0, 34.0, 150.0),
    (0.0, 1750.0, 24.0, 120.0),
    (260.0, 2450.0, -26.0, 240.0),
    (430.0, 4300.0, 28.0, 170.0),
    (-380.0, 5600.0, -20.0, 220.0),
)
RIDGES = ((3300.0, 20.0, 150.0),)


def terrain(x, y):
    h = 14.0 * math.sin(2.0 * math.pi * y / 2600.0 + 0.4)
    h += 10.0 * max(-1.5, min(1.5, x / 500.0)) * math.sin(2.0 * math.pi * y / 3700.0 + 1.3)
    for bx, by, a, r in BUMPS:
        h += a * math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (r * r))
    for ry, a, w in RIDGES:
        h += a * math.exp(-((y - ry) / w) ** 2)
    return h


def robot_pose(y):
    hx = P.robot_wheel_x
    hy = 500.0
    h_rl, h_rr = terrain(-hx, y - hy), terrain(hx, y - hy)
    h_fl, h_fr = terrain(-hx, y + hy), terrain(hx, y + hy)
    a = ((h_rr + h_fr) - (h_rl + h_fl)) / (2.0 * 2 * hx)
    b = ((h_fl + h_fr) - (h_rl + h_rr)) / (2.0 * 2 * hy)
    c = (h_rl + h_rr + h_fl + h_fr) / 4.0
    return c, math.degrees(math.atan(b)), -math.degrees(math.atan(a))


def _matrix(pitch, roll):
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

    def unit_point(self, x, pt, phi, psi):
        """Punt van een sleeparm (werkstand (y, z)) bij armhoek phi en hefhoek psi, in wereldcoordinaten."""
        yy, zz = K.rot_up(K.arm_point(pt, phi), psi)
        return self.world(x, yy, zz)


# ---------------------------------------------------------------------
# Element en hefraam
# ---------------------------------------------------------------------
BAND_SINK = 0.075       # mm inzakken van de dieptering per N belasting (aangenomen: ca. 3 mm bij 40 N, vochtig grasland);
                        # de ringmaat wordt gekozen bij de nominale ringkracht, dus alleen de afwijking telt


def band_gap(pose, x, phi, psi):
    """Afstand onderkant dieptering - maaiveld onder het hart van de schijf."""
    c = pose.unit_point(x, P.disc_center, phi, psi)
    return c[2] - P.band_d / 2.0 - terrain(c[0], c[1])


def unit_phi(pose, x, psi):
    """(armhoek, hangt op de aanslag): de arm draait tot de dieptering het maaiveld raakt."""
    lo, hi = -P.u_stop_deg, 40.0
    if band_gap(pose, x, lo, psi) > 0.0:
        return lo, True
    return K._bisect(lambda a: band_gap(pose, x, a, psi), lo, hi), False


def pw_chi(pose, x, phi, psi):
    """Rolarmhoek: de aandrukrol volgt het maaiveld binnen zijn aanslagen."""
    lo, hi = P.pw_link_range

    def gap(chi):
        yz = K.rot_up(K.arm_point(K.pw_axle(chi), phi), psi)
        w = pose.world(x + P.pw_x, yz[0], yz[1])
        return w[2] - P.pw_d / 2.0 - terrain(w[0], w[1])
    if gap(lo) > 0.0:
        return lo, False
    if gap(hi) < 0.0:
        return hi, False
    return K._bisect(gap, lo, hi), True


def unit_state(pose, x, psi, case="normaal"):
    phi, hanging = unit_phi(pose, x, psi)
    spring = K.spring_force(phi)
    chi, pw_contact = pw_chi(pose, x, phi, psi)
    pw = K.pw_force(chi) if pw_contact else 0.0
    band = 0.0 if hanging else C.unit_band(spring, case, pw)
    c = pose.unit_point(x, P.disc_center, phi, psi)
    disc = terrain(c[0], c[1]) - (c[2] - P.disc_d / 2.0)
    short = False
    if not hanging:
        if band > 0.0:
            disc += BAND_SINK * (band - C.unit_band(K.spring_force(0.0), case))
        else:
            # te weinig neerdruk: de schijf gaat minder diep (kracht ~ diepte^1,5)
            ld = C.LOADS[case]
            lv = C._levers(P.u_pivot)
            avail = ld["disc_vertical"] + band * lv["band_v"] / lv["disc_v"]
            disc = P.disc_depth * (max(avail, 0.0) / ld["disc_vertical"]) ** (2.0 / 3.0)
            band, short = 0.0, True
    by, bz = K.disc_to_unit(K.boot_x()[1], 0.5 * (P.boot_y[0] + P.boot_y[1]), K.boot_bottom_z())[1:]
    b = pose.unit_point(x, (by, bz), phi, psi)
    boot = terrain(b[0], b[1]) - b[2] + (disc - (terrain(c[0], c[1]) - (c[2] - P.disc_d / 2.0)))
    return {"phi": phi, "chi": chi, "hanging": hanging, "short": short, "spring": spring, "band": band, "pw": pw,
            "disc": disc, "boot": boot, "disc_xy": (c[0], c[1])}


def frame_net(pose, psi, case="normaal", seed_kg=None):
    """Moment (Nmm) van de grondkrachten om de draaibouten min het gewichtsmoment; > 0 = hefraam wil omhoog."""
    ld = C.LOADS[case]
    seed_kg = C.SEED["kg"] if seed_kg is None else seed_kg
    pv = P.pivot
    m_w = C.MODEL["moving_kg"] * C.G_ACC * (pv[0] - K.rot_up(C.MODEL["moving_cg"], psi)[0])
    m_w += seed_kg * C.G_ACC * (pv[0] - K.rot_up(C.SEED["cg"], psi)[0])
    pts = C.unit_points()
    m_u = 0.0
    states = []
    for x in P.row_x:
        s = unit_state(pose, x, psi, case)
        states.append(s)
        dv = K.rot_up(K.arm_point(pts["disc_v"], s["phi"]), psi)
        bd = K.rot_up(K.arm_point(pts["band"], s["phi"]), psi)
        pw = K.rot_up(K.arm_point(K.pw_axle(s["chi"]), s["phi"]), psi)
        if not s["hanging"]:
            f_dv = ld["disc_vertical"] * (1.0 if not s["short"] else (s["disc"] / P.disc_depth) ** 1.5)
            m_u += f_dv * (pv[0] - dv[0]) + s["band"] * (pv[0] - bd[0])
            m_u += (ld["disc_draft"] + ld["boot_draft"] + C.SOIL["rolling"] * s["band"]) * (pv[1] - dv[1])
        m_u += s["pw"] * (pv[0] - pw[0]) + C.SOIL["rolling"] * s["pw"] * pv[1]
    return m_u - m_w, states


def solve(y, case="normaal", seed_kg=None):
    """Werkstand (actuator helemaal uit) bij robotpositie y. Het hefraam zweeft tot de grondkrachten gelijk zijn
    aan gewicht + gasveren; bovenin het langgat (top) duwt de robot extra, onderin (low) hangt het aan de robot."""
    pose = Pose(y)
    lo, hi = K.float_range()

    def f(a):
        return frame_net(pose, a, case, seed_kg)[0] - K.gas_moment(a)
    if f(hi) > 0.0:
        mode, psi = "top", hi
    elif f(lo) < 0.0:
        mode, psi = "low", lo
    else:
        mode, psi = "float", K._bisect(f, lo, hi, n=40)
    net, states = frame_net(pose, psi, case, seed_kg)
    push = K.gas_force(psi) + (max(0.0, net - K.gas_moment(psi)) / K.act_lever(psi) if mode == "top" else 0.0)
    return {"y": y, "pose": pose, "pitch": pose.pitch, "roll": pose.roll, "psi": psi, "mode": mode,
            "actuator_push": push, "rows": states}


# ---------------------------------------------------------------------
# Posities en samenvatting
# ---------------------------------------------------------------------
def work_positions():
    """De 80 robotposities in werkstand van de animatie van de geavanceerde toediener (ook gebruikt door v1/v2)."""
    with open(ADVANCED_JSON, encoding="utf-8") as handle:
        frames = json.load(handle)["frames"]
    return [f["y"] for f in frames if f["phase"] == "work"]


def _sd(values):
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


def run(case="normaal", seed_kg=None):
    return [solve(y, case, seed_kg) for y in work_positions()]


def summary(sol=None):
    sol = sol or run()
    disc = [r["disc"] for s in sol for r in s["rows"]]
    boot = [r["boot"] for s in sol for r in s["rows"]]
    pw = [r["pw"] for s in sol for r in s["rows"] if not r["hanging"]]
    band = [r["band"] for s in sol for r in s["rows"] if not r["hanging"]]
    spring = [r["spring"] for s in sol for r in s["rows"]]
    target = P.disc_depth
    return {"positions": len(sol),
            "disc_depth_range": (round(min(disc), 1), round(max(disc), 1)),
            "disc_depth_mean": round(sum(disc) / len(disc), 1), "disc_depth_sd": round(_sd(disc), 1),
            "share_within_5mm": round(100.0 * sum(1 for d in disc if abs(d - target) <= 5.0) / len(disc), 1),
            "share_within_3mm": round(100.0 * sum(1 for d in disc if abs(d - target) <= 3.0) / len(disc), 1),
            "boot_depth_range": (round(min(boot), 1), round(max(boot), 1)),
            "disc_out_of_soil": sum(1 for d in disc if d <= 0.0),
            "pw_force_range": (round(min(pw), 1), round(max(pw), 1)),
            "band_force_range": (round(min(band), 1), round(max(band), 1)),
            "too_little_downforce": sum(1 for s in sol for r in s["rows"] if r["short"]),
            "spring_range": (round(min(spring)), round(max(spring))),
            "hanging_units": sum(1 for s in sol for r in s["rows"] if r["hanging"]),
            "phi_range": (round(min(r["phi"] for s in sol for r in s["rows"]), 1),
                          round(max(r["phi"] for s in sol for r in s["rows"]), 1)),
            "chi_range": (round(min(r["chi"] for s in sol for r in s["rows"]), 1),
                          round(max(r["chi"] for s in sol for r in s["rows"]), 1)),
            "frame_modes": {m: sum(1 for s in sol if s["mode"] == m) for m in ("top", "float", "low")},
            "psi_range": (round(min(s["psi"] for s in sol), 1), round(max(s["psi"] for s in sol), 1)),
            "actuator_push_range": (round(min(s["actuator_push"] for s in sol)),
                                    round(max(s["actuator_push"] for s in sol))),
            "depth_range_per_row": [(round(min(s["rows"][i]["disc"] for s in sol), 1),
                                     round(max(s["rows"][i]["disc"] for s in sol), 1)) for i in range(len(P.row_x))]}


def load_v2():
    """lfs2_ground van simple_v2 (starre balk met dieptewielen), zonder de map in sys.path te zetten."""
    import sys
    if V2_FOLDER not in sys.path:
        sys.path.append(V2_FOLDER)
    spec = importlib.util.spec_from_file_location("lfs2_ground", os.path.join(V2_FOLDER, "lfs2_ground.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compare_v2(sol=None):
    """Afwijking van de ingestelde snijdiepte: doorzaaier (8 sleeparmen) en simple_v2 (starre balk, 5 schijven)."""
    sol = sol or run()
    g2 = load_v2()
    import lfs2_params as P2
    dev_o = [r["disc"] - P.disc_depth for s in sol for r in s["rows"]]
    dev_2 = [r["disc"] - P2.work_depth for y in work_positions() for r in g2.solve(y)["rows"]]
    return {"overseeder": {"range": (round(min(dev_o), 1), round(max(dev_o), 1)), "sd": round(_sd(dev_o), 1)},
            "simple_v2_rigid": {"range": (round(min(dev_2), 1), round(max(dev_2), 1)), "sd": round(_sd(dev_2), 1)}}


if __name__ == "__main__":
    sol = run()
    for k, v in summary(sol).items():
        print(k, v)
    print(compare_v2(sol))
