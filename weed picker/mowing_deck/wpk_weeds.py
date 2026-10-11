"""Weed model for the renders and the animation: thistles, ragwort and dock standing in short grass. A plant is cut
when a blade circle passes over its stem and it stands higher than the cut height; the part above the cut is chopped
and thrown out of the discharge as chips, most of them into the windrow behind the deck (windrow_share), the rest
scattered over the cut strip. Pure Python; shapes are made in wpk_parts.weed_shapes / chip_shape.

Use:  f = wpk_weeds.Field(); f.cut_by(rotors_xy, cut_z, t, y_discharge); f.stats()
"""
import math
import random

import wpk_params as P

# kind: (height range, stem d, crown d, fresh mass of the upright plant kg, share of the plants), estimated
KINDS = {
    "thistle": ((600.0, 1100.0), 12.0, 160.0, (0.12, 0.25), 0.45),
    "ragwort": ((500.0, 900.0), 10.0, 260.0, (0.15, 0.30), 0.30),
    "dock": ((700.0, 1200.0), 14.0, 200.0, (0.20, 0.40), 0.25),
}
CHIP_KG = 0.012                 # one drawn chip stands for 12 g of chopped weed


def make_plant(rnd, x, y, kind=None):
    if kind is None:
        r = rnd.random()
        acc = 0.0
        for k, v in KINDS.items():
            acc += v[4]
            if r <= acc:
                kind = k
                break
        kind = kind or "thistle"
    hr, sd, cd, mr, _ = KINDS[kind]
    return {"x": x, "y": y, "kind": kind, "h": rnd.uniform(*hr), "stem_d": sd, "crown_d": cd * rnd.uniform(0.8, 1.2),
            "rot": rnd.uniform(0.0, 360.0), "m": rnd.uniform(*mr), "cut": None}


def mass_above(p, cut_z):
    """Fresh mass (kg) above the cut: the upright plant from 50 mm up, taken as evenly spread over its height."""
    return p["m"] * max(0.0, p["h"] - cut_z) / (p["h"] - 50.0)


def scene_plants(seed=3):
    """A few plants in front of the deck for the still images (robot at y 0)."""
    rnd = random.Random(seed)
    out = []
    for x, y in ((-650, 1500), (-380, 1750), (-90, 1520), (150, 1900), (420, 1600), (700, 1800), (-250, 2150),
                 (300, 2300), (-560, 2400), (80, 2500), (600, 2450), (-850, 2000)):
        out.append(make_plant(rnd, x + rnd.uniform(-40, 40), y + rnd.uniform(-40, 40)))
    return out


class Field(object):
    def __init__(self, x=(-800.0, 800.0), y=(1700.0, 6900.0), density=3.5, seed=11):
        """density: plants per m2 in the patch."""
        self.rnd = random.Random(seed)
        n = int(density * (x[1] - x[0]) * (y[1] - y[0]) / 1e6)
        self.plants = []
        tries = 0
        while len(self.plants) < n and tries < 20 * n:
            tries += 1
            px, py = self.rnd.uniform(*x), self.rnd.uniform(*y)
            if all(math.hypot(px - q["x"], py - q["y"]) > 180.0 for q in self.plants):
                self.plants.append(make_plant(self.rnd, px, py))
        self.chips = []                  # dicts: x, y, z, l, w, rot, tilt, t, windrow
        self._pile = {}

    def _chip(self, t, y_dis, windrow):
        rnd = self.rnd
        if windrow:
            x = max(-P.windrow_w / 2.0, min(P.windrow_w / 2.0, rnd.gauss(0.0, P.windrow_w / 5.0)))
        else:
            x = rnd.uniform(-0.45, 0.45) * P.CUT_W
        y = y_dis - rnd.uniform(0.0, 220.0)
        key = (int(x // 60), int(y // 60))
        n = self._pile.get(key, 0)
        self._pile[key] = n + 1
        return {"x": x, "y": y, "z": min(90.0, 7.0 * n), "l": rnd.uniform(50.0, 110.0), "w": rnd.uniform(15.0, 35.0),
                "rot": rnd.uniform(0, 180.0), "tilt": rnd.uniform(-25.0, 25.0), "t": t, "windrow": windrow}

    def cut_by(self, rotors, cut_z, t, y_dis, r=P.blade_r[1]):
        """rotors: [(x, y, z_blade)] of the rotor axes (world); cut_z: right-hand blade height; y_dis: world y of the
        discharge (rear edge of the deck). Cuts every plant whose stem is inside a blade circle and taller than the
        blades. Returns the fresh mass (kg) cut now."""
        m_now = 0.0
        for p in self.plants:
            if p["cut"] is not None:
                continue
            for (rx, ry, rz) in rotors:
                if (p["x"] - rx) ** 2 + (p["y"] - ry) ** 2 <= r * r and p["h"] > rz + 20.0:
                    m = mass_above(p, rz)
                    p["cut"] = {"t": t, "z": rz, "kg": m}
                    m_now += m
                    n = max(2, int(round(m / CHIP_KG)))
                    for k in range(n):
                        self.chips.append(self._chip(t, y_dis, self.rnd.random() < P.windrow_share))
                    break
        return m_now

    def stats(self):
        inside = [p for p in self.plants if abs(p["x"]) <= P.CUT_W / 2.0 - 20.0]
        cut = [p for p in self.plants if p["cut"] is not None]
        kg = sum(p["cut"]["kg"] for p in cut)
        n_w = sum(1 for c in self.chips if c["windrow"])
        return {"plants": len(self.plants), "in_width": len(inside), "cut": len(cut),
                "share": len(cut) / float(len(inside)) if inside else 0.0, "kg_cut": kg,
                "kg_windrow": kg * n_w / float(len(self.chips)) if self.chips else 0.0}
