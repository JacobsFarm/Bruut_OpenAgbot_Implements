"""Parts of the chicken house robot that are new: the tine rotor (drawn in the broom's work pose, on its axis), the
sensor box with its hangers under the rear outer lower beam, and the 360 degree camera post. The broom head, push-blade
arms and toolbar come from build_bsw.
"""
import math

import Part
from FreeCAD import Vector as V

import chk_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all

AY, AZ = P.axis


def tines():
    """6 rows of spring tines O6 from the core surface to the tip circle, rows staggered half a step."""
    out = []
    r0 = P.core_d / 2.0 - 2.0
    for row in range(P.tine_rows):
        a = 2.0 * math.pi * row / P.tine_rows
        dx = (P.tine_step / 2.0) if row % 2 else 0.0
        cy, cz = math.cos(a), math.sin(a)
        for i in range(P.tines_per_row):
            x = P.tine_x0 + dx + i * P.tine_step
            if x > -P.tine_x0 + 1.0:
                continue
            out.append(cyl(P.tine_d, (x, AY + r0 * cy, AZ + r0 * cz), (x, AY + P.tip_r * cy, AZ + P.tip_r * cz)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Sensor box under the rear outer lower beam
# ---------------------------------------------------------------------
YB = sum(P.rear_beam_y) / 2.0
ZT = P.lower_beam_z[1]


def hangers():
    out = []
    bx, by, bz = P.box
    for x in P.hanger_x:
        top = box_span((x - 35.0, x + 35.0), (P.rear_beam_y[0] - 6.0, P.rear_beam_y[1] + 5.0), (ZT, ZT + 6.0))
        flat = box_span((x - 20.0, x + 20.0), (P.rear_beam_y[0] - 6.0, P.rear_beam_y[0]), (P.box_z0 + bz, ZT + 6.0))
        h = top.fuse(flat)
        for xb in (x - 25.0, x + 25.0):
            h = h.cut(cyl(10.5, (xb, YB, ZT - 1), (xb, YB, ZT + 7)))
        out.append(h)
    return Part.makeCompound(out)


def hanger_bolts():
    return Part.makeCompound([PP.bolt_z(10.0, xb, YB, P.lower_beam_z[0], ZT + 6.0) for x in P.hanger_x
                              for xb in (x - 25.0, x + 25.0)])


def sensor_box():
    bx, by, bz = P.box
    b = box_span((-bx / 2.0, bx / 2.0), (P.box_y0, P.box_y0 + by), (P.box_z0, P.box_z0 + bz))
    inlet = cyl(P.inlet_d, (0, P.box_y0, P.box_z0 + 40.0), (0, P.box_y0 - 40.0, P.box_z0 + 40.0))
    return fuse_all([b, inlet])


# ---------------------------------------------------------------------
# Camera post on a bar across the inner upper beams at y -325
# ---------------------------------------------------------------------
def cam_bar():
    y = -P.hole_y
    z0 = P.upper_beam_top
    s = box_span(P.bar_x, (y - P.bar_w / 2.0, y + P.bar_w / 2.0), (z0, z0 + 8.0))
    for x in (-325.0, 325.0):
        s = s.cut(cyl(10.5, (x, y, z0 - 1), (x, y, z0 + 9)))
    return s


def cam_bar_bolts():
    return Part.makeCompound([PP.bolt_z(10.0, x, -P.hole_y, P.upper_beam_top - 40.0, P.upper_beam_top + 8.0)
                              for x in (-325.0, 325.0)])


def cam_post():
    w = P.post[0] / 2.0
    y = -P.hole_y
    return tube_span((-w, w), (y - w, y + w), (P.upper_beam_top + 8.0, P.post[1]), 3.0, "z")


def camera360():
    d, h = P.cam360
    y = -P.hole_y
    body = cyl(d, (0, y, P.post[1]), (0, y, P.post[1] + h))
    dome = Part.makeSphere(d / 2.0 - 10.0, V(0, y, P.post[1] + h)).common(
        box_span((-d, d), (y - d, y + d), (P.post[1] + h, P.post[1] + h + d)))
    return fuse_all([body, dome])


# ---------------------------------------------------------------------
# Scene (render only): litter layer and some birds
# ---------------------------------------------------------------------
def litter(y=(-1500.0, 2600.0)):
    return box_span((-1300.0, 1300.0), y, (0.0, P.litter_depth))


def birds():
    out = []
    for i, (x, y) in enumerate(((-800, 2100), (700, 1900), (-1000, 900), (900, 600), (-900, -900), (950, -1200),
                                (300, 2400), (-400, 2300))):
        a = (i * 47) % 360
        body = Part.makeSphere(130.0, V(x, y, P.litter_depth + 170.0))
        head = Part.makeSphere(55.0, V(x + 110 * math.cos(math.radians(a)), y + 110 * math.sin(math.radians(a)),
                                       P.litter_depth + 330.0))
        out.append(fuse_all([body, head]))
    return Part.makeCompound(out)
