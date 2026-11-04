"""Parts of the manure vacuum collector. Every function returns a Part shape in robot coordinates (work pose).
Nozzle hood, end plates, outlet, head frame, castors, hose, inlet stub and cross bars are the debris vacuum's
(dvc_parts); this file adds the flaps with the squeegee lip, the vacuum tank, saddles, float valve, moisture trap,
vacuum pump on its shelf and the dump valve.
"""
import math

import Part
from FreeCAD import Vector as V

import mvc_params as P
import dvc_parts as DG

box_span = DG.box_span
cyl = DG.cyl
fuse_all = DG.fuse_all
D = P.D

X_IN = DG.X_IN
AZ = P.tank_axis_z
R = P.tank_d / 2.0


# ---------------------------------------------------------------------
# Nozzle: front flap 40 mm high, squeegee lip on the rear wall
# ---------------------------------------------------------------------
def hood():
    """The debris vacuum hood without the brush; the brush-shaft and bearing holes in the end plates are plugged."""
    return DG.hood()


def end_plates():
    return DG.end_plates()


def flap():
    y1 = D.noz_y[1]
    return box_span((-X_IN, X_IN), (y1, y1 + D.flap_t), (P.flap_gap_front, D.noz_z[0] + 60.0))


def lip():
    """Rubber squeegee 12 mm, clamped on the outside of the rear wall, 5 mm into the floor line (it bends back)."""
    y0 = D.noz_y[0]
    return box_span((-X_IN, X_IN), (y0 - P.lip_t, y0), (-P.lip_press, D.noz_z[0] + 60.0))


def lip_clamp():
    y0 = D.noz_y[0]
    return box_span((-X_IN, X_IN), (y0 - P.lip_t - 5.0, y0 - P.lip_t), (D.noz_z[0] + 10.0, D.noz_z[0] + 60.0))


# ---------------------------------------------------------------------
# Tank
# ---------------------------------------------------------------------
TY0, TY1 = P.tank_y


def tank():
    shell = cyl(P.tank_d, (0, TY0, AZ), (0, TY1, AZ)).cut(cyl(P.tank_d - 2 * P.tank_t, (0, TY0 + 4.0, AZ), (0, TY1 - 4.0, AZ)))
    ribs = [cyl(P.tank_d + 16.0, (0, y - 4.0, AZ), (0, y + 4.0, AZ)).cut(cyl(P.tank_d - 1.0, (0, y - 5.0, AZ), (0, y + 5.0, AZ)))
            for y in (-200.0, 150.0)]
    s = fuse_all([shell] + ribs)
    s = s.cut(cyl(D.hose_d - 12.0 + 1.0, (0, TY1 - 5.0, P.inlet_z), (0, TY1 + 1.0, P.inlet_z)))
    for (x, y), d in ((P.float_xy, 40.0), ((0.0, P.dump_y), P.dump_d)):
        z = AZ + R if d == 40.0 else AZ - R
        s = s.cut(cyl(d, (x, y, z - 30.0), (x, y, z + 30.0)))
    return s


inlet = DG.inlet


def saddles():
    out = []
    for y in P.saddle_y:
        b = box_span((-200.0, 200.0), (y - P.saddle_w / 2.0, y + P.saddle_w / 2.0), (P.bar_top, AZ - 60.0))
        out.append(b.cut(cyl(P.tank_d + 0.5, (0, y - 40.0, AZ), (0, y + 40.0, AZ))))
    return Part.makeCompound(out)


cross_bars = DG.cross_bars
bar_bolts = DG.bar_bolts


def float_valve():
    x, y = P.float_xy
    d, h = P.float_d
    z0 = AZ + R - 8.0
    body = cyl(d, (x, y, z0 + 30.0), (x, y, z0 + h))
    neck = cyl(40.0, (x, y, z0), (x, y, z0 + 31.0))
    return fuse_all([body, neck])


def moisture_trap():
    x, y = P.trap_xy
    d, h = P.trap
    z0 = AZ + R + 5.0                       # on a bracket over the tank (the tank top is lower at x 150)
    return cyl(d, (x, y, z0), (x, y, z0 + h))


# shelf with the vacuum pump behind the tank, on 2 cross tubes 40 x 40 at y -475 and -625 on the upper beams
SHELF_TUBES_Y = (-475.0, -625.0)
SHELF_Z = (P.upper_beam_top + 40.0, P.upper_beam_top + 40.0 + P.shelf[2])


def shelf_tubes():
    out = []
    for y in SHELF_TUBES_Y:
        o = box_span((-470.0, 470.0), (y - 20.0, y + 20.0), (P.upper_beam_top, P.upper_beam_top + 40.0))
        i = box_span((-471.0, 471.0), (y - 17.0, y + 17.0), (P.upper_beam_top + 3.0, P.upper_beam_top + 37.0))
        t = o.cut(i)
        for x in (-425.0, -325.0, 325.0, 425.0):
            t = t.cut(cyl(10.4, (x, y, P.upper_beam_top - 1), (x, y, P.upper_beam_top + 41)))
        out.append(t)
    return Part.makeCompound(out)


def shelf_bolts():
    out = []
    for y in SHELF_TUBES_Y:
        for x in (-425.0, -325.0, 325.0, 425.0):
            # head on the tube, nut under the beam (beam bottom = top - 40)
            out.append(fuse_all([cyl(10.0, (x, y, P.upper_beam_top - 52.0), (x, y, P.upper_beam_top + 40.0)),
                                 cyl(17.0, (x, y, P.upper_beam_top + 40.0), (x, y, P.upper_beam_top + 46.4)),
                                 cyl(17.0, (x, y, P.upper_beam_top - 48.4), (x, y, P.upper_beam_top - 40.0))]))
    return Part.makeCompound(out)


def shelf():
    sx, sy, st = P.shelf
    return box_span((-sx / 2.0, sx / 2.0), (P.pump_y - sy / 2.0, P.pump_y + sy / 2.0), SHELF_Z)


def pump():
    bx, by, bz = P.pump_box
    z0 = SHELF_Z[1]
    body = box_span((-bx / 2.0, bx / 2.0), (P.pump_y - by / 2.0, P.pump_y + by / 2.0), (z0, z0 + bz * 0.55))
    motor = cyl(140.0, (-bx / 2.0 + 10.0, P.pump_y, z0 + bz * 0.55 + 70.0), (bx / 2.0 - 10.0, P.pump_y, z0 + bz * 0.55 + 70.0))
    silencer = cyl(60.0, (bx / 2.0 - 40.0, P.pump_y - by / 2.0 - 60.0, z0 + 60.0), (bx / 2.0 - 40.0, P.pump_y - by / 2.0, z0 + 60.0))
    return fuse_all([body, motor, silencer])


def vac_hoses():
    """Float valve -> moisture trap -> pump inlet (O40)."""
    fx, fy = P.float_xy
    tx, ty = P.trap_xy
    zt = AZ + R + P.float_d[1] - 30.0
    a = DG.fuse_all([cyl(40.0, (fx, fy, zt), (tx, fy, zt)), cyl(40.0, (tx, fy, zt), (tx, ty, zt)),
                     Part.makeSphere(20.0, V(tx, fy, zt))])
    pz = SHELF_Z[1] + P.pump_box[2] * 0.55
    b = DG.fuse_all([cyl(40.0, (tx, ty - P.trap[0] / 2.0 + 5.0, AZ + R + 60.0), (tx, P.pump_y + 30.0, AZ + R + 60.0)),
                     cyl(40.0, (tx, P.pump_y + 30.0, AZ + R + 60.0), (tx, P.pump_y + 30.0, pz - 5.0)),
                     Part.makeSphere(20.0, V(tx, P.pump_y + 30.0, AZ + R + 60.0))])
    return Part.makeCompound([a, b])


def dump_valve():
    s, h = P.dump_body
    z1 = AZ - R + 5.0
    body = box_span((-s / 2.0, s / 2.0), (P.dump_y - s / 2.0 + 40.0, P.dump_y + s / 2.0 - 40.0), (z1 - h, z1))
    body = body.cut(cyl(P.dump_d, (0, P.dump_y, z1 - h - 1), (0, P.dump_y, z1 + 1)))
    pipe = cyl(P.dump_d + 6.0, (0, P.dump_y, 620.0), (0, P.dump_y, z1 - h)).cut(cyl(P.dump_d, (0, P.dump_y, 619.0), (0, P.dump_y, z1 - h + 1)))
    d, L = P.dump_act
    act = cyl(d, (s / 2.0, P.dump_y, z1 - h / 2.0), (s / 2.0 + L, P.dump_y, z1 - h / 2.0))
    return fuse_all([body, pipe]), act


def dump_body():
    return dump_valve()[0]


def dump_actuator():
    return dump_valve()[1]


# ---------------------------------------------------------------------
# Scene: barn alley with manure, cleaned strip behind the nozzle
# ---------------------------------------------------------------------
def floor(y0, y1):
    return box_span((-1600.0, 1600.0), (y0, y1), (-40.0, 0.0))


def manure(y0, y1, seed=5):
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(70):
        x = rnd.uniform(-1500, 1500)
        y = rnd.uniform(y0, y1)
        if abs(x) < 520 and y < D.noz_y[0]:
            continue                          # cleaned behind the nozzle
        r = rnd.uniform(60, 140)
        out.append(Part.makeCylinder(r, rnd.uniform(15, 35), V(x, y, 0.0)).common(
            Part.makeSphere(r * 1.3, V(x, y, -r * 0.9))))
    return Part.makeCompound(out)


def wet_film(y0, y1):
    return box_span((-1600.0, 1600.0), (y0, y1), (0.0, 1.0)).cut(box_span((-500.0, 500.0), (y0 - 1, D.noz_y[0]), (-1.0, 2.0)))
