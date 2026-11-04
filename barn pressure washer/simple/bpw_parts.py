"""Parts of the barn pressure washer. Every function returns a Part shape in robot coordinates. Mast, carriage, arm
(fence inspector) and the tilt motor and flange (hedge trimmer) are imported; this file adds the lance with the turbo
nozzle (drawn at tilt 0, along +x), the HP hose reel and the hoses.
"""
import math

import Part
from FreeCAD import Vector as V

import bpw_params as P
import hdg_parts as HG

box_span = HG.box_span
cyl = HG.cyl
fuse_all = HG.fuse_all
ZC = HG.ZC
TX = P.tilt_x
LY = P.lance_y


# ---------------------------------------------------------------------
# Lance (sub-Part "Tilt", turns about y at (TX, ZC))
# ---------------------------------------------------------------------
def clamp():
    cx, cy, cz = P.clamp
    return box_span((TX - cx / 2.0, TX + cx / 2.0), (LY - cy / 2.0, LY + cy / 2.0), (ZC - cz / 2.0, ZC + cz / 2.0))


def lance():
    x0 = TX + P.clamp[0] / 2.0
    tube = cyl(P.lance_d, (x0, LY, ZC), (x0 + P.lance_len, LY, ZC))
    d, L = P.turbo
    nozzle = cyl(d, (x0 + P.lance_len, LY, ZC), (x0 + P.lance_len + L, LY, ZC))
    tip = Part.makeCone(d / 2.0, 6.0, 25.0, V(x0 + P.lance_len + L, LY, ZC), V(1, 0, 0))
    return fuse_all([tube, nozzle, tip])


def swivel():
    d, L = P.swivel
    x1 = TX - P.clamp[0] / 2.0
    return cyl(d, (x1 - L, LY, ZC), (x1, LY, ZC))


def jet(length=900.0):
    """Spray cone (images only)."""
    x0 = TX + P.clamp[0] / 2.0 + P.lance_len + P.turbo[1] + 25.0
    return Part.makeCone(4.0, 90.0, length, V(x0, LY, ZC), V(1, 0, 0))


# ---------------------------------------------------------------------
# Reel
# ---------------------------------------------------------------------
RY, RZ = P.reel_y, P.reel_z
W2 = P.drum_w / 2.0


def bars():
    out = []
    for y in P.BAR_Y:
        o = box_span((-P.bar_x, P.bar_x), (y - 20.0, y + 20.0), P.bar_z)
        i = box_span((-P.bar_x - 1, P.bar_x + 1), (y - 17.0, y + 17.0), (P.bar_z[0] + 3.0, P.bar_z[1] - 3.0))
        t = o.cut(i)
        for x in (-425.0, -325.0, 325.0, 425.0):
            t = t.cut(cyl(10.4, (x, y, P.bar_z[0] - 1), (x, y, P.bar_z[1] + 1)))
        out.append(t)
    return Part.makeCompound(out)


def bar_bolts():
    out = []
    for y in P.BAR_Y:
        for x in (-425.0, -325.0, 325.0, 425.0):
            out.append(fuse_all([cyl(10.0, (x, y, P.bar_z[0] - 52.0), (x, y, P.bar_z[1])),
                                 cyl(17.0, (x, y, P.bar_z[1]), (x, y, P.bar_z[1] + 6.4)),
                                 cyl(17.0, (x, y, P.bar_z[0] - 48.4), (x, y, P.bar_z[0] - 40.0))]))
    return Part.makeCompound(out)


def side_plates():
    out = []
    for sx in (-1, 1):
        x0 = sx * (W2 + 22.0) - (P.side_t if sx < 0 else 0.0)
        pts = [(P.BAR_Y[0] + 20.0, P.bar_z[1]), (P.BAR_Y[1] - 20.0, P.bar_z[1]), (RY - 40.0, RZ + 45.0), (RY + 40.0, RZ + 45.0)]
        poly = Part.makePolygon([V(x0, y, z) for (y, z) in pts] + [V(x0, pts[0][0], pts[0][1])])
        p = Part.Face(poly).extrude(V(P.side_t, 0, 0))
        out.append(p.cut(cyl(26.0, (x0 - 1, RY, RZ), (x0 + P.side_t + 1, RY, RZ))))
    return Part.makeCompound(out)


def drum():
    core = cyl(P.drum_d, (-W2, RY, RZ), (W2, RY, RZ))
    flanges = [cyl(P.flange_d, (sx * W2 - (6.0 if sx > 0 else 0.0), RY, RZ), (sx * W2 + (0.0 if sx > 0 else 6.0), RY, RZ))
               for sx in (-1, 1)]
    hose_wrap = cyl(P.drum_d + 4 * P.hose_od, (-W2 + 6.0, RY, RZ), (W2 - 6.0, RY, RZ))
    shaft = cyl(25.0, (-W2 - 40.0, RY, RZ), (W2 + 40.0, RY, RZ))
    return fuse_all([core] + flanges + [shaft]), hose_wrap


def drum_body():
    return drum()[0]


def wound_hose():
    return drum()[1]


def reel_motor():
    x0 = -(W2 + 22.0) - P.side_t
    return fuse_all([box_span((x0 - 70.0, x0), (RY - 45.0, RY + 45.0), (RZ - 45.0, RZ + 45.0)),
                     cyl(70.0, (x0 - 70.0, RY, RZ + 80.0), (x0 - 70.0 + 0.0001 + 60.0, RY, RZ + 80.0))])


def rotary_joint():
    x0 = W2 + 22.0 + P.side_t
    return cyl(40.0, (x0, RY, RZ), (x0 + 60.0, RY, RZ))


def supply_hose():
    """From the rotary joint up to the guide roller on the mast top (the loop down to the arm is not drawn)."""
    x0 = W2 + 22.0 + P.side_t + 60.0
    pts = [V(x0, RY, RZ), V(x0 + 40.0, RY, RZ), V(x0 + 40.0, RY, P.guide_z), V(x0 + 40.0, P.guide_y, P.guide_z),
           V(455.0, P.guide_y, P.guide_z)]
    parts = [Part.makeCylinder(P.hose_od / 2.0, (b - a).Length, a, b - a) for a, b in zip(pts[:-1], pts[1:])]
    parts += [Part.makeSphere(P.hose_od / 2.0, p) for p in pts[1:-1]]
    return fuse_all(parts)


def guide_roller():
    roller = cyl(50.0, (455.0, P.guide_y, P.guide_z), (515.0, P.guide_y, P.guide_z))
    bracket = box_span((480.0, 490.0), (30.0, P.guide_y), (P.guide_z - 20.0, P.guide_z + 20.0))
    return fuse_all([roller, bracket])


def arm_hose():
    """Along the arm to the swivel (rides with the arm)."""
    hx, hy = HG.P.hinge_xy
    x1 = TX - P.clamp[0] / 2.0 - P.swivel[1]
    pts = [V(hx + 30.0, hy - 40.0, ZC + 30.0), V(TX - 80.0, hy - 40.0, ZC + 30.0), V(x1 - 20.0, LY, ZC), V(x1, LY, ZC)]
    parts = [Part.makeCylinder(P.hose_od / 2.0, (b - a).Length, a, b - a) for a, b in zip(pts[:-1], pts[1:])]
    parts += [Part.makeSphere(P.hose_od / 2.0, p) for p in pts[1:-1]]
    return fuse_all(parts)


# ---------------------------------------------------------------------
# Scene: pig pen (partition walls, slatted floor) on the right
# ---------------------------------------------------------------------
def pen(y0, y1):
    floor = box_span((-1200.0, 3000.0), (y0, y1), (-40.0, 0.0))
    wall = box_span((2300.0, 2360.0), (y0, y1), (0.0, 1000.0))
    parts = [floor, wall]
    for y in (y0 + 300.0, y1 - 300.0):
        parts.append(box_span((1000.0, 2300.0), (y - 30.0, y + 30.0), (0.0, 1000.0)))
    return Part.makeCompound(parts)


def dirt(y0, y1, seed=11):
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(40):
        z = rnd.uniform(0, 700)
        y = rnd.uniform(y0 + 400, y1 - 400)
        if y > 0:
            out.append(box_span((2298.0, 2300.0), (y, y + rnd.uniform(60, 160)), (z, z + rnd.uniform(40, 120))))
    return Part.makeCompound(out)
