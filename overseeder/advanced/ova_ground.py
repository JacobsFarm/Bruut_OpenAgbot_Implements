"""Bodemvolging van de geavanceerde doorzaaimachine over dezelfde hobbelige strook als de toedieners en de
eenvoudige versie (puur Python, geen FreeCAD nodig).

Per robotpositie:
- de robot rust met zijn vier wielen op het maaiveld (zelfde houding als ../simple/ovs_ground.py);
- de balk zweeft aan het parallellogram: hij blijft evenwijdig aan de robot en zakt of stijgt (h) tot de
  grondkrachten van de elementen gelijk zijn aan het gewicht plus de duw van de gasveren;
- elke arm draait tot de diepteringen (links en rechts van de schijf) het maaiveld raken;
- de aandrukrol volgt het maaiveld in zijn gaffel (torsieveer);
- de kracht op de ringen volgt uit de armbalans (ova_calc.unit_band); de ringen zakken iets in (BAND_SINK);
  te weinig neerdruk: de schijf gaat minder diep (kracht ~ diepte^1,5).

Gebruik:
    import ova_ground
    ova_ground.summary()
    ova_ground.compare()           # tegen de eenvoudige versie en de starre balk van de toediener simple_v2
"""
import importlib.util
import math
import os
import sys

import ova_params as P
import ova_kin as K
import ova_calc as C

FOLDER = os.path.dirname(os.path.abspath(__file__))
SIMPLE_FOLDER = os.path.join(os.path.dirname(FOLDER), "simple")
BAND_SINK = 0.075       # mm per N afwijking van de nominale ringkracht (aangenomen, gelijk aan de eenvoudige versie)
BAND_DX = 9.0           # hart van de ringen naast de schijf (x)


def _load(name, folder):
    if folder not in sys.path:
        sys.path.append(folder)
    spec = importlib.util.spec_from_file_location(name, os.path.join(folder, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SG = _load("ovs_ground", SIMPLE_FOLDER)       # maaiveld, robothouding en posities van de eenvoudige versie
terrain = SG.terrain


class Pose(SG.Pose):
    def bar_point(self, x, pt, h):
        dy, dz = K.bar_shift(h)
        return self.world(x, pt[0] + dy, pt[1] + dz)

    def unit_point(self, x, pt, drop, h):
        return self.bar_point(x, K.rot_yz(pt, drop, P.u_pivot), h)


def band_gap(pose, x, drop, h):
    c = pose.unit_point(x, K.disc_center(), drop, h)
    g = 0.5 * (terrain(c[0] - BAND_DX, c[1]) + terrain(c[0] + BAND_DX, c[1]))
    return c[2] - P.band_d / 2.0 - g


def unit_drop(pose, x, h):
    lo, hi = -25.0, P.unit_drop_deg          # arm omhoog (veer in) tot 25 graden, omlaag tot de stelmoer
    if band_gap(pose, x, hi, h) > 0.0:
        return hi, True
    if band_gap(pose, x, lo, h) < 0.0:
        return lo, False
    return K._bisect(lambda a: band_gap(pose, x, a, h), lo, hi), False


def pw_chi(pose, x, drop, h):
    lo, hi = P.pw_range

    def gap(chi):
        w = pose.unit_point(x, K.pw_axle(chi), drop, h)
        return w[2] - P.pw_d / 2.0 - terrain(w[0], w[1])
    if gap(hi) > 0.0:
        return hi, False
    if gap(lo) < 0.0:
        return lo, True
    return K._bisect(gap, lo, hi), True


def unit_state(pose, x, h, case="normaal"):
    drop, hanging = unit_drop(pose, x, h)
    spring = K.spring_force(drop)
    chi, contact = pw_chi(pose, x, drop, h)
    pw = K.pw_force(chi) if contact else 0.0
    band = 0.0 if hanging else C.unit_band(spring, case, pw)
    c = pose.unit_point(x, K.disc_center(), drop, h)
    disc = terrain(c[0], c[1]) - (c[2] - P.disc_d / 2.0)
    short = False
    if not hanging:
        if band > 0.0:
            disc += BAND_SINK * (band - C.unit_band(K.spring_force(0.0), case))
        else:
            ld = C.LOADS[case]
            lv_band = P.u_pivot[0] - K.disc_center()[0]
            lv_disc = P.u_pivot[0] - C.unit_points()["disc_v"][0]
            avail = ld["disc_vertical"] + band * lv_band / lv_disc
            disc = P.work_depth * (max(avail, 0.0) / ld["disc_vertical"]) ** (2.0 / 3.0)
            band, short = 0.0, True
    t = pose.unit_point(x, K.boot_tip(), drop, h)
    boot = terrain(t[0], t[1]) - t[2] + (disc - (terrain(c[0], c[1]) - (c[2] - P.disc_d / 2.0)))
    return {"drop": drop, "chi": chi, "hanging": hanging, "short": short, "spring": spring, "band": band,
            "pw": pw, "disc": disc, "boot": boot}


def bar_net(pose, h, case="normaal", seed_kg=None):
    """Grondkrachten (N) min gewicht min gasveren; > 0 = balk wil omhoog."""
    ld = C.LOADS[case]
    w = (C.MODEL["moving_kg"] + C.MODEL["hoses_kg"] / 2.0) * C.G_ACC
    states = [unit_state(pose, x, h, case) for x in P.row_x]
    up = 0.0
    for s in states:
        if not s["hanging"]:
            f_dv = ld["disc_vertical"] * (1.0 if not s["short"] else (s["disc"] / P.work_depth) ** 1.5)
            up += f_dv + s["band"]
        up += s["pw"]
    return up - w - K.gas_vertical(h), states


def solve(y, case="normaal"):
    pose = Pose(y)
    lo, hi = K.float_range()
    f_hi, _ = bar_net(pose, hi, case)
    f_lo, _ = bar_net(pose, lo, case)
    if f_hi > 0.0:
        mode, h = "top", hi
    elif f_lo < 0.0:
        mode, h = "low", lo
    else:
        mode, h = "float", K._bisect(lambda a: bar_net(pose, a, case)[0], lo, hi, n=40)
    net, states = bar_net(pose, h, case)
    return {"y": y, "pose": pose, "h": h, "mode": mode, "rows": states}


def work_positions():
    return SG.work_positions()


def run(case="normaal"):
    return [solve(y, case) for y in work_positions()]


def _sd(values):
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


def summary(sol=None):
    sol = sol or run()
    rows = [r for s in sol for r in s["rows"]]
    disc = [r["disc"] for r in rows]
    boot = [r["boot"] for r in rows]
    t = P.work_depth
    return {"positions": len(sol),
            "disc_depth_range": (round(min(disc), 1), round(max(disc), 1)),
            "disc_depth_mean": round(sum(disc) / len(disc), 1), "disc_depth_sd": round(_sd(disc), 1),
            "share_within_5mm": round(100.0 * sum(1 for d in disc if abs(d - t) <= 5.0) / len(disc), 1),
            "share_within_3mm": round(100.0 * sum(1 for d in disc if abs(d - t) <= 3.0) / len(disc), 1),
            "boot_tip_depth_range": (round(min(boot), 1), round(max(boot), 1)),
            "boot_tip_sd": round(_sd(boot), 1),
            "band_force_range": (round(min(r["band"] for r in rows), 1), round(max(r["band"] for r in rows), 1)),
            "pw_lost": sum(1 for r in rows if r["pw"] == 0.0),
            "too_little_downforce": sum(1 for r in rows if r["short"]),
            "hanging_units": sum(1 for r in rows if r["hanging"]),
            "drop_range": (round(min(r["drop"] for r in rows), 1), round(max(r["drop"] for r in rows), 1)),
            "h_range": (round(min(s["h"] for s in sol), 1), round(max(s["h"] for s in sol), 1)),
            "modes": {m: sum(1 for s in sol if s["mode"] == m) for m in ("top", "float", "low")}}


def compare(sol=None):
    """Afwijking van de ingestelde snijdiepte: geavanceerd, eenvoudig (../simple) en de starre balk van simple_v2."""
    sol = sol or run()
    simple = SG.run()
    dev_a = [r["disc"] - P.work_depth for s in sol for r in s["rows"]]
    dev_s = [r["disc"] - 15.0 for s in simple for r in s["rows"]]
    boot_a = [r["boot"] for s in sol for r in s["rows"]]
    boot_s = [r["boot"] for s in simple for r in s["rows"]]
    out = {"advanced": {"range": (round(min(dev_a), 1), round(max(dev_a), 1)), "sd": round(_sd(dev_a), 1),
                        "boot_range": (round(min(boot_a), 1), round(max(boot_a), 1)), "boot_sd": round(_sd(boot_a), 1)},
           "simple": {"range": (round(min(dev_s), 1), round(max(dev_s), 1)), "sd": round(_sd(dev_s), 1),
                      "boot_range": (round(min(boot_s), 1), round(max(boot_s), 1)), "boot_sd": round(_sd(boot_s), 1)}}
    return out


if __name__ == "__main__":
    sol = run()
    for k, v in summary(sol).items():
        print(k, v)
    print(compare(sol))
