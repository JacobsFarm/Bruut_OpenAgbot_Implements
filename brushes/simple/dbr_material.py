"""Materiaalmodel voor de animatie: los materiaal (zaagsel, zand, voerresten) als deeltjes op de vloer.

Eenvoudig en bewust grof (Python + numpy, geen FreeCAD nodig):
- de borstel helt naar voren; met ca. 20 mm indrukking raakt de haarkrans de vloer over een boog van +-75 graden
  rond de voorkant (CONTACT_DEG). De achterkant staat vrij: wat binnen de krans ligt wordt niet geraakt;
- een deeltje in de krans binnen die boog krijgt de snelheid van de haarpunten (omega x r + rijsnelheid) maal
  SLIP (per deeltje) en wordt zo langs de omtrek meegenomen, tot zijn eigen loslaathoek (willekeurig tussen RELEASE_DEG en
  CONTACT_DEG: het ene deeltje valt eerder tussen de haren uit dan het andere);
- daarna glijdt het uit met wrijving mu_material * g en blijft liggen.
Startsituatie: een gelijkmatige laag ("layer") of een wiers in het midden ("windrow", om breed te leggen).
Gebruik: m = Material("double_750", "windrow"); m.step(y_robot, dt, rpm, v_robot); triangles(m, m.heights())
"""
import math

import numpy as np

import dbr_params as P

G_ACC = 9.81
CONTACT_DEG = 75.0      # halve hoek van de contactboog (tilt 4 graden, ca. 20 mm indrukking van het haar)
RELEASE_DEG = 5.0       # vroegste loslaathoek
SLIP = (0.30, 0.60)     # deeltje haalt 30..60 % van de haarsnelheid (glijdt tussen de haren door), per deeltje
RING_IN = 70.0          # krans: R - 70 .. R + 5
CELL = 50.0             # afstand tussen de deeltjes bij de start (mm)
SEED = 7


class Material:
    def __init__(self, config=P.DEFAULT_CONFIG, mode="spread", start="layer", strip_y=(-1530.0, -4100.0),
                 layer=P.layer_kg_m2, strip_x=(-820.0, 820.0), windrow=(400.0, 10.0)):
        """start 'layer': laag van layer kg/m2 over strip_x; 'windrow': wiers van windrow = (breedte mm, kg/m)."""
        self.c = P.config(config)
        self.mode = mode
        rng = np.random.default_rng(SEED)
        ys = np.arange(strip_y[1], strip_y[0], CELL)
        if start == "windrow":
            w, kg_m = windrow
            self.mass = P.layer_kg_m2 * (CELL / 1000.0) ** 2
            per_row = int(round(kg_m * CELL / 1000.0 / self.mass))
            xs = np.linspace(-w / 2.0, w / 2.0, per_row)
        else:
            self.mass = layer * (CELL / 1000.0) ** 2           # kg per deeltje
            xs = np.arange(strip_x[0], strip_x[1], CELL)
        gx, gy = np.meshgrid(xs, ys)
        n = gx.size
        jit = min(CELL, xs[1] - xs[0]) if xs.size > 1 else CELL
        self.x = gx.ravel() + rng.uniform(-0.4, 0.4, n) * jit
        self.y = gy.ravel() + rng.uniform(-0.4, 0.4, n) * CELL
        self.x0, self.y0 = self.x.copy(), self.y.copy()
        self.vx = np.zeros(n)
        self.vy = np.zeros(n)
        self.release = rng.uniform(RELEASE_DEG, CONTACT_DEG, n)
        self.slip = rng.uniform(SLIP[0], SLIP[1], n)
        self.size = rng.uniform(0.55, 0.8, n) * CELL
        self.rot = rng.uniform(0, 90, n)
        self.brush_x = np.array(P.centres_x(self.c, mode if self.c["n"] == 2 else "spread"))
        self.brush_y = P.floor_centre_y(self.c)               # robotcoordinaten
        self.signs = P.brush_signs(self.c, mode)
        self.engaged = 0.0

    def step(self, y_robot, dt, rpm, v_robot):
        """y_robot = robotmidden (wereld-y), v_robot = rijsnelheid (mm/s, naar -y), rpm van de borstels."""
        omega = rpm * 2.0 * math.pi / 60.0
        R = self.c["R"]
        touched = np.zeros(self.x.size, dtype=bool)
        for bx, s in zip(self.brush_x, self.signs):
            cy = self.brush_y + y_robot
            dx, dy = self.x - bx, self.y - cy
            d = np.hypot(dx, dy)
            th = np.degrees(np.arctan2(dx, -dy))             # 0 = voorkant (-y)
            arc = (d > R - RING_IN) & (d < R + 5.0) & (np.abs(th) < CONTACT_DEG) & ~touched
            if rpm <= 0.0:                                   # stilstaande borstel schuift alleen voor zich uit
                self.vy[arc] = np.minimum(self.vy[arc], -v_robot)
                touched |= arc
                continue
            # ingaande kant (s * th < 0): altijd mee naar de voorkant; uitgaande kant: mee tot de loslaathoek
            hit = arc & (s * th < self.release)
            w = s * omega
            k = self.slip[hit]
            self.vx[hit] = k * (-w * dy[hit])
            self.vy[hit] = k * (w * dx[hit] - v_robot) - (1.0 - k) * v_robot   # de krans duwt minstens mee
            touched |= hit
        free = ~touched
        sp = np.hypot(self.vx[free], self.vy[free])
        dec = P.mu_material * G_ACC * 1000.0 * dt
        f = np.where(sp > dec, (sp - dec) / np.maximum(sp, 1e-9), 0.0)
        self.vx[free] *= f
        self.vy[free] *= f
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.engaged = float(np.count_nonzero(touched) * self.mass)

    def moved_kg(self, min_mm=40.0):
        return float(np.count_nonzero(np.hypot(self.x - self.x0, self.y - self.y0) > min_mm) * self.mass)

    def profile(self, y_robot, bin_mm=100.0, half=1500.0):
        """Verdeling over x (kg per m rijlengte) van wat de borstels al gepasseerd zijn."""
        behind = self.y > (self.brush_y + y_robot + 80.0)
        y_span = (np.max(self.y0) - np.min(self.y0)) / 1000.0
        hist, edges = np.histogram(self.x[behind], bins=np.arange(-half, half + 1, bin_mm))
        return edges, hist * self.mass / max(y_span, 1e-6) / (bin_mm / 1000.0)

    def stats(self, y_robot):
        behind = self.y > (self.brush_y + y_robot + 80.0)
        x = self.x[behind]
        return {"behind_kg": float(x.size * self.mass), "centre_kg": float(np.count_nonzero(np.abs(x) < 150.0) * self.mass),
                "width_mm": float(np.percentile(x, 95) - np.percentile(x, 5)) if x.size > 10 else 0.0}

    def heights(self, bin_mm=32.0, dz=7.0):
        """z-onderkant per deeltje: deeltjes in hetzelfde vak worden gestapeld (een wiers wordt een rug)."""
        ix = np.floor(self.x / bin_mm).astype(np.int64)
        iy = np.floor(self.y / bin_mm).astype(np.int64)
        key = ix * 1000003 + iy
        order = np.argsort(key, kind="stable")
        ks = key[order]
        start = np.r_[0, np.flatnonzero(np.diff(ks)) + 1]
        counts = np.diff(np.r_[start, ks.size])
        level = np.zeros(ks.size)
        level[order] = np.arange(ks.size) - np.repeat(start, counts)
        return level * dz


def triangles(m, z_levels, h=8.0):
    """Mesh-driehoeken van alle deeltjes (vierkante plaatjes, gedraaid), voor Mesh.Mesh."""
    a = np.radians(m.rot)
    hs = m.size / 2.0
    cx = np.array([-1, 1, 1, -1])
    cy = np.array([-1, -1, 1, 1])
    px = m.x[:, None] + (cx[None, :] * np.cos(a)[:, None] - cy[None, :] * np.sin(a)[:, None]) * hs[:, None]
    py = m.y[:, None] + (cx[None, :] * np.sin(a)[:, None] + cy[None, :] * np.cos(a)[:, None]) * hs[:, None]
    z0 = np.repeat(z_levels[:, None], 4, axis=1)
    z1 = z0 + h
    B = np.stack([px, py, z0], axis=2)                        # (n, 4, 3)
    T = np.stack([px, py, z1], axis=2)
    faces = [T[:, [0, 1, 2]], T[:, [0, 2, 3]]]
    for k in range(4):
        j = (k + 1) % 4
        faces.append(np.stack([B[:, k], B[:, j], T[:, j]], axis=1))
        faces.append(np.stack([B[:, k], T[:, j], T[:, k]], axis=1))
    return np.concatenate(faces, axis=0).tolist()
