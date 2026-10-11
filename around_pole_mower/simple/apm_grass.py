"""Grass model for the animation: a grid of tufts under the fence. A tuft is cut (to the cut height) as soon as the
circle of the strings has passed over it. Pure Python; shapes are made in animate_apm.

Use:  g = apm_grass.Grass(); g.cut_by(head_xy_list); g.stats()
"""
import math
import random

import apm_params as P


class Grass(object):
    def __init__(self, x=(460.0, None), y=(-1100.0, 4300.0), cell=50.0, h=(180.0, 260.0), posts=(), seed=7):
        x1 = P.POST_X + 260.0 if x[1] is None else x[1]
        rnd = random.Random(seed)
        self.cell = cell
        self.tufts = []                         # [x, y, h_long, h_cut, cut]
        nx = int((x1 - x[0]) / cell) + 1
        ny = int((y[1] - y[0]) / cell) + 1
        r_post = P.fence_post_d / 2.0 + 15.0
        for i in range(nx):
            for j in range(ny):
                px = x[0] + i * cell + rnd.uniform(-12.0, 12.0)
                py = y[0] + j * cell + rnd.uniform(-12.0, 12.0)
                if any(math.hypot(px - P.POST_X, py - yp) < r_post for yp in posts):
                    continue
                self.tufts.append([px, py, rnd.uniform(*h), P.cut_h + rnd.uniform(0.0, 12.0), False])
        self.x = (x[0], x1)
        self.y = y

    def cut_by(self, heads, r=P.string_r[1]):
        """heads: list of (x, y) world positions of the head centre (the strings turn). Returns tufts cut now."""
        n = 0
        r2 = r * r
        for t in self.tufts:
            if t[4]:
                continue
            for hx, hy in heads:
                if (t[0] - hx) ** 2 + (t[1] - hy) ** 2 <= r2:
                    t[4] = True
                    n += 1
                    break
        return n

    def state(self):
        return [t[4] for t in self.tufts]

    def set_state(self, cut):
        for t, c in zip(self.tufts, cut):
            t[4] = c

    def stats(self, strip=None, y_max=None):
        """Share of the tufts cut inside the strip x0..x1 (default: string reach at rest, 20 mm inside), only the
        tufts with y <= y_max (the part the head has passed) if y_max is given."""
        x0, x1 = strip or (P.HEAD_REST[0] - P.string_r[1] + 20.0, P.HEAD_REST[0] + P.string_r[1] - 20.0)
        inside = [t for t in self.tufts if x0 <= t[0] <= x1 and (y_max is None or t[1] <= y_max)]
        cut = sum(1 for t in inside if t[4])
        return {"cut": cut, "total": len(inside), "share": cut / float(len(inside)) if inside else 0.0}
