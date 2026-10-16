"""Grass for the renders and the animation of the triple sickle bar mower.

A field of tufts on a jittered grid. Each tuft knows its strip: 'F' (cut by the front bar, |x| <= 625), 'W' (cut by
a wing, 625 < |x| <= 1625) or 'O' (outside the working width, never cut). A tuft is cut when the knife of its strip
passes it; then it is drawn as stubble at the cut height with the cut part lying behind it.
The positions are pure Python; the shapes need FreeCAD (sbm_parts.tuft).
"""
import math
import random

import sbm_params as P


def region(x):
    ax = abs(x)
    if ax <= P.front_L / 2.0:
        return "F"
    if ax <= P.front_L / 2.0 + P.wing_L:
        return "W"
    return "O"


class Field:
    def __init__(self, y=(-2500.0, 3300.0), x=(-2500.0, 2500.0), pitch=(95.0, 90.0), seed=7):
        rnd = random.Random(seed)
        self.tufts = []
        ny = int((y[1] - y[0]) / pitch[1]) + 1
        nx = int((x[1] - x[0]) / pitch[0]) + 1
        for j in range(ny):
            for i in range(nx):
                tx = x[0] + i * pitch[0] + rnd.uniform(-0.35, 0.35) * pitch[0]
                ty = y[0] + j * pitch[1] + rnd.uniform(-0.35, 0.35) * pitch[1]
                self.tufts.append({"x": tx, "y": ty, "h": P.grass_h * rnd.uniform(0.8, 1.2),
                                   "rot": rnd.uniform(0.0, 60.0), "lie": rnd.uniform(-25.0, 25.0),
                                   "region": region(tx), "row": j})
        self._cache = {}

    def tuft_shapes(self, i):
        """(standing, stubble, cut) face lists of tuft i (cached)."""
        if i not in self._cache:
            import sbm_parts as G
            from FreeCAD import Vector as V
            import Part
            t = self.tufts[i]
            standing = G.tuft(t["x"], t["y"], t["h"], rot=t["rot"])
            stubble = G.tuft(t["x"], t["y"], P.cut_h, r=20.0, rot=t["rot"])
            a = math.radians(t["lie"])
            ln = 0.85 * (t["h"] - P.cut_h)
            z = P.cut_h + 4.0
            pts = [V(t["x"] - 14.0, t["y"], z), V(t["x"] + 14.0, t["y"], z),
                   V(t["x"] + ln * math.sin(a), t["y"] - ln * math.cos(a), z + 6.0)]
            pts.append(pts[0])
            cut = [Part.Face(Part.makePolygon(pts))]
            self._cache[i] = (standing, stubble, cut)
        return self._cache[i]

    def shapes(self, standing, y_window=None):
        """Faces per colour: {'grass': [...], 'stubble': [...], 'cut': [...]}. standing(tuft) -> True when it still
        stands; y_window = (y0, y1) limits the tufts drawn (camera view)."""
        out = {"grass": [], "stubble": [], "cut": []}
        for i, t in enumerate(self.tufts):
            if y_window is not None and not (y_window[0] <= t["y"] <= y_window[1]):
                continue
            s, b, c = self.tuft_shapes(i)
            if standing(t):
                out["grass"] += s
            else:
                out["stubble"] += b
                out["cut"] += c
        return out

    def counts(self, standing):
        n = {"F": [0, 0], "W": [0, 0], "O": [0, 0]}
        for t in self.tufts:
            n[t["region"]][0 if standing(t) else 1] += 1
        return n
