"""Parts of the hedge trimmer and leaf blower. Every function returns a Part shape in robot coordinates. Mast, screw,
stepper, camera, carriage, hinge pin and arm are the fence inspector's (fin_parts); this file adds the tilt gearmotor,
the trimmer (drawn at tilt 0, bar up; build_hdg turns it about the tilt axis) and the front blower.
"""
import math

import Part
from FreeCAD import Vector as V

import hdg_params as P
import fin_parts as FG

box_span = FG.box_span
cyl = FG.cyl
fuse_all = FG.fuse_all
ZC = FG.ZC
TX = P.tilt_x


def tilt_motor():
    bx, by, bz = P.tilt_box
    body = box_span((P.arm_x1 - 5.0, P.arm_x1 - 5.0 + bx), (-by / 2.0, by / 2.0), (ZC - bz / 2.0, ZC + bz / 2.0))
    motor = cyl(60.0, (TX, by / 2.0, ZC), (TX, by / 2.0 + 90.0, ZC))
    return fuse_all([body, motor])


def tilt_flange():
    return cyl(80.0, (TX, P.flange_y[0], ZC), (TX, P.flange_y[1], ZC))


HX = TX + P.housing_dx
HY = P.housing_y
HZ = (ZC - P.housing[2] / 2.0, ZC + P.housing[2] / 2.0)


def housing():
    hx, hy, hz = P.housing
    body = box_span((HX - hx / 2.0, HX + hx / 2.0), (HY - hy / 2.0, HY + hy / 2.0), HZ)
    cap = cyl(70.0, (HX, HY - hy / 2.0 - 30.0, ZC - 20.0), (HX, HY - hy / 2.0, ZC - 20.0))     # motor cap on -y
    return fuse_all([body, cap])                    # the +y face bolts straight onto the tilt flange


BX = HX + 5.0                   # bar centre x (outer face at BX + t/2 ~ 940 at tilt 0)


def bar():
    """Double-sided bar: blade 32 x 10, teeth both edges (y), along +z from the housing top."""
    z0, z1 = HZ[1], HZ[1] + P.bar_len
    w, t = P.bar_w, P.bar_t
    blade = box_span((BX - t / 2.0, BX + t / 2.0), (HY - w / 2.0, HY + w / 2.0), (z0, z1))
    teeth = []
    z = z0 + 20.0
    while z < z1 - 10.0:
        for sy in (-1, 1):
            y0 = HY + sy * w / 2.0
            pts = [V(BX - t / 2.0, y0, z), V(BX - t / 2.0, y0 + sy * P.tooth_len, z + 6.0),
                   V(BX - t / 2.0, y0 + sy * P.tooth_len, z + 14.0), V(BX - t / 2.0, y0, z + 20.0), V(BX - t / 2.0, y0, z)]
            teeth.append(Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0)))
        z += P.tooth_pitch
    return Part.makeCompound([blade] + teeth)


def guard():
    gx, gy = P.guard
    z0, z1 = HZ[1], HZ[1] + P.bar_len - 50.0
    return box_span((BX - P.bar_t / 2.0 - gx, BX - P.bar_t / 2.0), (HY - gy / 2.0, HY + gy / 2.0), (z0, z1))


def tof():
    x, y, z = P.tof
    return box_span((HX + P.housing[0] / 2.0, HX + P.housing[0] / 2.0 + x), (HY - y / 2.0, HY + y / 2.0),
                    (HZ[0] + 20.0, HZ[0] + 20.0 + z))


# ---------------------------------------------------------------------
# Front blower
# ---------------------------------------------------------------------
def _dir():
    d = V(*P.blow_dir)
    d.normalize()
    return d


def blower():
    a = V(*P.blow_start)
    d = _dir()
    body = Part.makeCylinder(P.blow_d / 2.0, P.blow_len, a, d)
    b = a + d * P.blow_len
    nozzle = Part.makeCone(P.nozzle_d[0] / 2.0, P.nozzle_d[1] / 2.0, P.nozzle_len, b, d)
    return fuse_all([body, nozzle])


def blower_bracket():
    """Flat bar 80 x 8 down from the front lower beam (2 x M10 through the beam holes at x +-25) to a clamp ring."""
    bx, by, bt = P.bracket
    y0, y1 = P.front_beam_y
    x0 = P.blow_start[0]
    top = box_span((x0 - bx / 2.0, x0 + bx / 2.0), (y0, y1), (P.lower_beam_z[0] - bt, P.lower_beam_z[0]))
    a = V(*P.blow_start)
    d = _dir()
    c = a + d * 120.0
    leg = box_span((x0 - 20.0, x0 + 20.0), (y0 + 10.0, y0 + 10.0 + bt), (c.z + P.blow_d / 2.0 - 10.0, P.lower_beam_z[0] - bt))
    ring = Part.makeCylinder(P.blow_d / 2.0 + 6.0, 40.0, c - d * 20.0, d).cut(Part.makeCylinder(P.blow_d / 2.0, 42.0, c - d * 21.0, d))
    return fuse_all([top, leg, ring])


# ---------------------------------------------------------------------
# Scene: hedge along x 1000 .. 1800 (side face at x 1000), paved path in front
# ---------------------------------------------------------------------
def hedge(y0, y1, cut_to=None):
    face = 1000.0 if cut_to is None else cut_to
    body = box_span((face, face + P.hedge_top_w * 1000.0), (y0, y1), (0.0, P.hedge_h * 1000.0))
    return body


def hedge_uncut(y0, y1):
    """Untrimmed growth (60 mm proud of the face) in front of the robot."""
    import random
    rnd = random.Random(7)
    out = []
    y = y0
    while y < y1:
        for z in range(100, int(P.hedge_h * 1000.0), 160):
            out.append(Part.makeSphere(rnd.uniform(50, 80), V(1000.0 + rnd.uniform(-10, 25), y + rnd.uniform(-40, 40), z)))
        y += 150.0
    return Part.makeCompound(out)


def path(y0, y1):
    return box_span((-1500.0, 1000.0), (y0, y1), (-40.0, 0.0))


def leaves(y0, y1, seed=9):
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(80):
        x = rnd.uniform(-1200, 950)
        y = rnd.uniform(y0, y1)
        if y < 900.0 and x > -400:
            continue                                          # blown off already
        out.append(Part.makeCylinder(rnd.uniform(20, 35), 2.0, V(x, y, 0.5)))
    return Part.makeCompound(out)
