"""Voer in de voergang: hoogteveld (kg per cel) dat de vijzel opneemt, naar het voerhek voert en daar neerlegt.

Puur Python + numpy (geen FreeCAD nodig). Gebruikt door animate_fpa.py.
Wereld = robotcoordinaten bij de start: x = dwars (voerhek aan +x), y = langs de voergang, de robot rijdt naar -y.

Model per tijdstap:
1. opnemen: cellen die de voorkant van het blad passeert (x binnen de beblading) gaan voor 97 % de vijzel in;
2. transport: de vijzel is verdeeld in vakken van dx; per vak schuift min(massa, capaciteit) met v_ax naar +x
   (meer dan de capaciteit blijft liggen en wordt voor de vijzel uit geschoven: bulldozeren);
3. uitwerpen: wat voorbij het rechter blad-einde komt, valt tussen de open eindplaat en het voerhek op de vloer.
"""
import math

import numpy as np

import fpa_params as P
import fpa_calc as C

FENCE_X = 960.0             # voorkant opstand voerhek
RESIDUE = 0.03              # blijft achter op de vloer (onder het blad, door de flap meegesleept)
DROP_X = (735.0, 955.0)     # waar het uitgeworpen voer op de vloer valt
DROP_PEAK = 850.0
DROP_V = (-230.0, 20.0)     # t.o.v. de vijzelas, in y


class FeedField:
    def __init__(self, dx=25.0, x_range=(-1000.0, FENCE_X), y_range=(-5300.0, 1400.0), seed=7):
        self.dx = dx
        self.xs = np.arange(x_range[0] + dx / 2.0, x_range[1], dx)
        self.ys = np.arange(y_range[0] + dx / 2.0, y_range[1], dx)
        self.M = np.zeros((len(self.ys), len(self.xs)))
        cols = np.where((self.xs >= P.blade_x[0]) & (self.xs <= P.blade_x[1]))[0]
        self.c0, self.c1 = int(cols[0]), int(cols[-1]) + 1
        self.bx = self.xs[self.c0:self.c1]
        self.B = np.zeros(self.c1 - self.c0)
        self.cap_bin = C.capacity()["q_cap_kg_m"] * dx / 1000.0
        self.collected = 0.0
        self.moved = 0.0
        self._init_windrow(seed)
        self.initial_total = float(self.M.sum())
        w = np.clip(1.0 - np.abs(self.xs - DROP_PEAK) / ((DROP_X[1] - DROP_X[0]) / 2.0), 0.0, None)
        w[(self.xs < DROP_X[0]) | (self.xs > DROP_X[1])] = 0.0
        self.drop_w = w / w.sum()

    # -----------------------------------------------------------------
    def _init_windrow(self, seed):
        """Door de koeien weggeduwd voer, enkele uren na het voeren: een slingerende strook 600-950 mm van het
        hek (ca. 24 kg/m), met een plek waar al gevreten is en een klont; tegen het hek ligt nog een dun laagje."""
        X, Y = np.meshgrid(self.xs, self.ys)
        dy = self.dx / 1000.0
        lam = 24.0 + 6.0 * np.sin(2 * math.pi * Y / 1700.0 + 0.6)                  # kg per m voergang
        lam *= 1.0 - 0.65 * np.exp(-((Y + 3150.0) / 260.0) ** 2)                  # hier is al gevreten
        lam *= np.clip((Y + 4500.0) / 350.0, 0, 1) * np.clip((150.0 - Y) / 350.0, 0, 1)
        xc = 190.0 + 150.0 * np.sin(2 * math.pi * Y / 2900.0 + 1.1)
        sx = 170.0 + 35.0 * np.sin(2 * math.pi * Y / 2100.0)
        gx = np.exp(-0.5 * ((X - xc) / sx) ** 2) / (math.sqrt(2 * math.pi) * sx) * self.dx
        M = lam * dy * gx
        clump = np.exp(-((X - 150.0) ** 2 + (Y + 2050.0) ** 2) / (2 * 170.0 ** 2))
        M += clump / clump.sum() * 10.0                                         # klont van 10 kg
        near = (X > FENCE_X - 170.0) & (Y < 150.0) & (Y > -4500.0)
        M += np.where(near, 3.0 * dy / (170.0 / self.dx), 0.0)
        rng = np.random.default_rng(seed)
        noise = rng.normal(0.0, 1.0, M.shape)
        for _ in range(3):
            noise = (noise + np.roll(noise, 1, 0) + np.roll(noise, -1, 0) + np.roll(noise, 1, 1) + np.roll(noise, -1, 1)) / 5.0
        self.M = np.clip(M * (1.0 + 0.35 * noise), 0.0, None)
        self.relax(iters=6)

    # -----------------------------------------------------------------
    def rows_between(self, y_lo, y_hi):
        return np.where((self.ys >= y_lo) & (self.ys < y_hi))[0]

    def step(self, y_robot_old, y_robot_new, dt, turning=True):
        """Eén tijdstap. y_robot = y van het robotmidden (de vijzel zit op auger_y daarachter)."""
        front_old = y_robot_old + P.auger_y - P.blade_d / 2.0
        front_new = y_robot_new + P.auger_y - P.blade_d / 2.0
        rows = self.rows_between(front_new, front_old)
        if len(rows):
            take = self.M[rows, self.c0:self.c1] * (1.0 - RESIDUE)
            self.M[rows, self.c0:self.c1] -= take
            got = take.sum(axis=0)
            self.B += got
            self.collected += float(got.sum())
        out = 0.0
        if turning:
            c = C.kinematics()["v_ax"] * 1000.0 * dt / self.dx
            moving = np.minimum(self.B, self.cap_bin) * min(1.0, c)
            self.B -= moving
            self.B[1:] += moving[:-1]
            out = float(moving[-1])
        if out > 0.0:
            yc = y_robot_new + P.auger_y
            r = self.rows_between(yc + DROP_V[0], yc + DROP_V[1])
            if len(r):
                self.M[r, :] += out / len(r) * self.drop_w[None, :]
                self.relax((yc - 450.0, yc + 450.0), x_min=P.blade_x[1] - 60.0, iters=4)
            self.moved += out
        return out

    def relax(self, y_range=None, x_min=None, iters=4, slope=0.9, rate=0.4):
        """Uitzakken onder het stortgewicht: steiler dan 'slope' (dh/dx) stroomt voer naar de buurcel.
        De rand van het rooster aan +x is de opstand van het voerhek (daar stroomt niets door).
        y_range / x_min beperken het gebied (alleen achter de vijzel, anders loopt voer terug in de schone strook)."""
        rows = slice(None)
        if y_range is not None:
            r = self.rows_between(*y_range)
            if not len(r):
                return
            rows = slice(int(r[0]), int(r[-1]) + 1)
        cols = slice(None) if x_min is None else slice(int(np.searchsorted(self.xs, x_min)), None)
        region = (rows, cols)
        k = P.feed_density * (self.dx / 1000.0) ** 2 / 1000.0      # kg per mm hoogte per cel
        dh_max = slope * self.dx
        for _ in range(iters):
            for axis in (0, 1):
                H = self.M[region] / k
                d = np.diff(H, axis=axis)                              # h[i+1] - h[i]
                flow = np.sign(d) * np.clip(np.abs(d) - dh_max, 0.0, None) * rate / 2.0
                f = flow * k                                           # kg van i+1 naar i (als d > 0)
                Mi = self.M[region]
                if axis == 0:
                    f = np.clip(f, -Mi[:-1], Mi[1:])
                    Mi[:-1] += f
                    Mi[1:] -= f
                else:
                    f = np.clip(f, -Mi[:, :-1], Mi[:, 1:])
                    Mi[:, :-1] += f
                    Mi[:, 1:] -= f
                self.M[region] = Mi

    # -----------------------------------------------------------------
    def engaged(self):
        m = float(self.B.sum())
        xc = float((self.B * self.bx).sum() / m) if m > 1e-9 else 0.0
        over = float(np.clip(self.B - self.cap_bin, 0, None).sum())
        return m, xc, over

    def heights(self, smooth=2):
        """Hoogte (mm) per cel bij de stortdichtheid, licht gladgestreken voor de weergave."""
        H = self.M / (P.feed_density * (self.dx / 1000.0) ** 2) * 1000.0
        for _ in range(smooth):
            Hp = np.pad(H, 1, mode="edge")
            H = (4 * H + Hp[:-2, 1:-1] + Hp[2:, 1:-1] + Hp[1:-1, :-2] + Hp[1:-1, 2:]) / 8.0
        return H

    def blob_heights(self, a=170.0):
        """Hoogte (mm) van de voerstapel in/voor de vijzel per vak, halve ellips met halve breedte a."""
        area = self.B / (P.feed_density * self.dx / 1000.0) * 1e6       # mm2 doorsnede
        return np.clip(area / (math.pi * a / 2.0), 0.0, 340.0)

    def strip_mass(self, x_lo, x_hi, y_lo, y_hi):
        rows = self.rows_between(y_lo, y_hi)
        cols = np.where((self.xs >= x_lo) & (self.xs < x_hi))[0]
        if not len(rows) or not len(cols):
            return 0.0
        return float(self.M[np.ix_(rows, cols)].sum())


def mesh_triangles(xs, ys, H, z0=0.6, h_min=1.5, x_off=0.0, y_off=0.0):
    """Driehoeken (lijst van punten, per 3 een facet) voor het hoogteveld; alleen waar voer ligt."""
    ny, nx = H.shape
    Z = H + z0
    mask = H > h_min
    quad = mask[:-1, :-1] | mask[1:, :-1] | mask[:-1, 1:] | mask[1:, 1:]
    jj, ii = np.nonzero(quad)
    if not len(jj):
        return []
    X = xs + x_off
    Y = ys + y_off

    def pt(j, i):
        return np.stack([X[i], Y[j], Z[j, i]], axis=1)
    p00, p10, p01, p11 = pt(jj, ii), pt(jj, ii + 1), pt(jj + 1, ii), pt(jj + 1, ii + 1)
    tri = np.concatenate([np.stack([p00, p10, p11], axis=1), np.stack([p00, p11, p01], axis=1)], axis=0)
    return tri.reshape(-1, 3).tolist()


def blob_triangles(bx, hb, v_center, a=170.0, n=10, h_min=2.0):
    """Driehoeken voor de voerstapel in de vijzel (robotcoordinaten): per vak een halve ellips in het y-z vlak."""
    if hb.max() < h_min:
        return []
    th = np.linspace(0.0, math.pi, n)
    yy = P.auger_y + v_center + a * np.cos(th)
    pts = []
    k = len(bx)
    hb = hb.copy()
    hb[hb < h_min] = 0.0
    for i in range(k - 1):
        if hb[i] <= 0 and hb[i + 1] <= 0:
            continue
        z0 = hb[i] * np.sin(th) + 0.8
        z1 = hb[i + 1] * np.sin(th) + 0.8
        x0, x1 = bx[i], bx[i + 1]
        for m in range(n - 1):
            a0 = (x0, yy[m], z0[m])
            b0 = (x0, yy[m + 1], z0[m + 1])
            a1 = (x1, yy[m], z1[m])
            b1 = (x1, yy[m + 1], z1[m + 1])
            pts += [a0, a1, b1, a0, b1, b0]
    return pts
