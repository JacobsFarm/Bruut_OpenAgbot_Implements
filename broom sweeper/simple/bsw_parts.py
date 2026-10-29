"""Parts of the broom head. Every function returns a Part shape in robot coordinates, in the work pose (arms down,
head straight). The toolbar, lift arms, carrier, king pin and actuator come from "push blade/simple" (pbl_parts);
build_bsw.py puts the head in the same sub-Part as the blade (turns about the king pin) and the brush in its own
sub-Part (turns about the brush axis).
"""
import math

import Part
from FreeCAD import Vector as V

import bsw_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all
plate_yz = PP.plate_yz


def cyl_x(d, yz, x0, x1):
    return cyl(d, (x0, yz[0], yz[1]), (x1, yz[0], yz[1]))


def hull2_x(c1, r1, c2, r2, x0, x1):
    """Convex hull of 2 circles in the y-z plane (centres c1, c2 as (y, z)), extruded from x0 to x1."""
    dy, dz = c2[0] - c1[0], c2[1] - c1[1]
    L = math.hypot(dy, dz)
    uy, uz = dy / L, dz / L
    ny, nz = -uz, uy
    k = (r1 - r2) / L
    s = math.sqrt(1.0 - k * k)
    pts = []
    for side in (1, -1):
        my, mz = uy * k + side * ny * s, uz * k + side * nz * s
        pts.append((c1[0] + r1 * my, c1[1] + r1 * mz))
        pts.append((c2[0] + r2 * my, c2[1] + r2 * mz))
    quad = [pts[0], pts[1], pts[3], pts[2]]
    prism = plate_yz(quad, x0, x1 - x0)
    return fuse_all([prism, cyl_x(2 * r1, c1, x0, x1), cyl_x(2 * r2, c2, x0, x1)])


AXIS = (P.axis_y, P.axis_z)
SHAFT_X = (-P.end_x - P.end_t - P.brg_len - 7.0, P.pulley_x[1] + 4.0)
BRG_BOLT_DZ = 60.0


# ---------------------------------------------------------------------
# Head frame (weldment): swivel plate, spine, cross beam, end plates
# ---------------------------------------------------------------------
def head_frame():
    sz = P.swivel_z
    parts = [cyl(P.head_d, (0, P.king_y, sz[0]), (0, P.king_y, sz[1])),
             box_span((-P.spine_x, P.spine_x), (P.king_y, P.beam_y[1]), sz),
             tube_span((-P.end_x, P.end_x), P.beam_y, P.beam_z, P.beam_wall, "x")]
    for sx in (-1, 1):
        x0 = P.end_x if sx > 0 else -P.end_x - P.end_t
        parts.append(plate_yz(P.end_pts, x0, P.end_t))
    s = fuse_all(parts)
    s = s.cut(cyl(P.king_d + 1.0, (0, P.king_y, 0), (0, P.king_y, 500)))
    for a in P.angle_steps:
        ang = math.radians(-90.0 - a)       # hole for head angle a sits under the lock pin when turned by a
        x, y = P.lock_r * math.cos(ang), P.king_y + P.lock_r * math.sin(ang)
        s = s.cut(cyl(P.lock_d + 1.0, (x, y, 0), (x, y, 500)))
    s = s.cut(cyl_x(P.shaft_d + 2.0, AXIS, -800, 800))
    for dz in (-BRG_BOLT_DZ, BRG_BOLT_DZ):
        s = s.cut(cyl_x(13.0, (P.axis_y, P.axis_z + dz), -800, 800))
    s = s.cut(cyl_x(30.0, P.motor_yz, 0, 800))                     # gearbox output shaft, right plate only
    for yz in _standoff_yz():
        s = s.cut(cyl_x(9.0, yz, 0, 800))
    for x, y in _castor_bolts():
        s = s.cut(cyl(9.0, (x, y, 100), (x, y, 200)))
    return s


# ---------------------------------------------------------------------
# Hood and flap
# ---------------------------------------------------------------------
def _arc(r, n=36):
    a0, a1 = (math.radians(a) for a in P.hood_deg)
    return [(P.axis_y + r * math.cos(a0 + (a1 - a0) * i / n), P.axis_z + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def hood():
    pts = _arc(P.hood_r) + _arc(P.hood_r + P.hood_t)[::-1]
    shell = plate_yz(pts, -P.end_x, 2 * P.end_x)
    lip = box_span((-P.end_x, P.end_x), (P.flap_y - 4.0, P.flap_y), (215.0, P.flap_z[1]))
    return fuse_all([shell, lip])


def flap():
    return box_span((-P.end_x, P.end_x), (P.flap_y, P.flap_y + P.flap_t), P.flap_z)


# ---------------------------------------------------------------------
# Brush (own sub-Part) and bearings
# ---------------------------------------------------------------------
def bristles():
    L = P.brush_l / 2.0 - 5.0
    return cyl_x(P.brush_d, AXIS, -L, L).cut(cyl_x(P.fill_d, AXIS, -L - 1, L + 1))


def brush_core():
    L = P.brush_l / 2.0
    tube = cyl_x(P.core_d, AXIS, -L, L).cut(cyl_x(P.core_d - 2 * P.core_wall, AXIS, -L - 1, L + 1))
    discs = [cyl_x(P.core_d - 2 * P.core_wall, AXIS, sx * L - (10.0 if sx > 0 else 0.0),
                   sx * L + (0.0 if sx > 0 else 10.0)) for sx in (-1, 1)]
    s = fuse_all([tube] + discs).cut(cyl_x(P.shaft_d, AXIS, -L - 1, L + 1))
    return s


def brush_shaft():
    """2 stub shafts O40, welded into the core end discs."""
    L = P.brush_l / 2.0
    return Part.makeCompound([cyl_x(P.shaft_d, AXIS, SHAFT_X[0], -L + P.stub_l),
                              cyl_x(P.shaft_d, AXIS, L - P.stub_l, SHAFT_X[1])])


def bearings():
    """2 x UCFL 208 on the outside of the end plates: flange 15 mm and housing O80 x 40."""
    out = []
    ft, fy, fz = P.brg_flange
    for sx in (-1, 1):
        x0 = sx * (P.end_x + P.end_t)
        x1 = x0 + sx * ft
        fl = box_span((min(x0, x1), max(x0, x1)), (P.axis_y - fy / 2.0, P.axis_y + fy / 2.0),
                      (P.axis_z - fz / 2.0, P.axis_z + fz / 2.0))
        hs = cyl_x(P.brg_house_d, AXIS, x0, x0 + sx * P.brg_len)
        b = fuse_all([fl, hs]).cut(cyl_x(P.shaft_d, AXIS, -800, 800))
        for dz in (-BRG_BOLT_DZ, BRG_BOLT_DZ):
            b = b.cut(cyl_x(13.0, (P.axis_y, P.axis_z + dz), -800, 800))
        out.append(b)
    return Part.makeCompound(out)


def bearing_bolts():
    out = []
    for sx in (-1, 1):
        xin = sx * P.end_x
        xout = sx * (P.end_x + P.end_t + P.brg_flange[0])
        for dz in (-BRG_BOLT_DZ, BRG_BOLT_DZ):
            z = P.axis_z + dz
            out.append(PP.bolt_axis(12.0, (xout, P.axis_y, z), (xin, P.axis_y, z), 19.0, 7.5, 10.0))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Drive: motor + gearbox, pulleys, belt, guard
# ---------------------------------------------------------------------
def motor():
    x1 = P.end_x
    x0 = x1 - P.motor_len
    flange = cyl_x(P.motor_flange_d, P.motor_yz, x1 - 10.0, x1)
    body = cyl_x(P.motor_d, P.motor_yz, x0, x1 - 10.0)
    cap = cyl_x(P.motor_d - 20.0, P.motor_yz, x0 - 15.0, x0)
    return fuse_all([flange, body, cap])


def motor_shaft():
    return cyl_x(25.0, P.motor_yz, P.end_x, P.pulley_x[1] + 2.0)


def pulleys():
    x0, x1 = P.pulley_x
    small = cyl_x(P.pulley_small[1], P.motor_yz, x0, x1).cut(cyl_x(25.0, P.motor_yz, x0 - 1, x1 + 1))
    big = cyl_x(P.pulley_big[1], AXIS, x0, x1).cut(cyl_x(P.shaft_d, AXIS, x0 - 1, x1 + 1))
    return Part.makeCompound([small, big])


def belt():
    r1, r2 = P.pulley_big[1] / 2.0, P.pulley_small[1] / 2.0
    x0, x1 = P.pulley_x[0] + 3.0, P.pulley_x[1] - 3.0
    outer = hull2_x(AXIS, r1 + P.belt_t, P.motor_yz, r2 + P.belt_t, x0, x1)
    inner = hull2_x(AXIS, r1, P.motor_yz, r2, x0 - 1, x1 + 1)
    return outer.cut(inner)


def guard():
    r1 = P.pulley_big[1] / 2.0 + P.belt_t + P.guard_gap
    r2 = P.pulley_small[1] / 2.0 + P.belt_t + P.guard_gap
    x0, x1 = P.guard_x
    outer = hull2_x(AXIS, r1 + P.guard_t, P.motor_yz, r2 + P.guard_t, x0, x1)
    inner = hull2_x(AXIS, r1, P.motor_yz, r2, x0 - 1, x1 - P.guard_t)
    s = outer.cut(inner)
    tabs = [cyl_x(24.0, yz, x0, x0 + 4.0) for yz in _standoff_yz()]
    return fuse_all([s] + tabs).cut(Part.makeCompound([cyl_x(9.0, yz, 0, 800) for yz in _standoff_yz()]))


def _standoff_yz():
    """2 guard standoffs inside the guard rim: in front of the brush pulley and midway between the pulleys."""
    return ((P.axis_y + 60.0, P.axis_z), ((P.axis_y + P.motor_yz[0]) / 2.0, (P.axis_z + P.motor_yz[1]) / 2.0))


def guard_standoffs():
    out = []
    for yz in _standoff_yz():
        sp = cyl_x(16.0, yz, P.end_x + P.end_t, P.guard_x[0]).cut(cyl_x(9.0, yz, 0, 800))
        out.append(sp)
        out.append(PP.bolt_axis(8.0, (P.guard_x[0] + 4.0, yz[0], yz[1]), (P.end_x, yz[0], yz[1]), 13.0, 5.3, 6.8))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Castor wheels under the beam
# ---------------------------------------------------------------------
def _castor_bolts():
    px, py, _ = P.castor_plate
    out = []
    for sx in (-1, 1):
        for dx in (-px / 2.0 + 14.0, px / 2.0 - 14.0):
            for dy in (-py / 2.0 + 14.0, py / 2.0 - 14.0):
                out.append((sx * P.castor_x + dx, P.castor_y + dy))
    return out


def castor_spacers():
    px, py, _ = P.castor_plate
    out = []
    for sx in (-1, 1):
        x = sx * P.castor_x
        out.append(box_span((x - px / 2.0, x + px / 2.0), (P.castor_y - py / 2.0, P.castor_y + py / 2.0),
                            (P.castor_height, P.beam_z[0])))
    s = Part.makeCompound(out)
    for x, y in _castor_bolts():
        s = s.cut(cyl(9.0, (x, y, 100), (x, y, 200)))
    return s


def castors():
    """Swivel castor: top plate, swivel housing, fork (2 plates), shown trailing straight back."""
    px, py, pt = P.castor_plate
    r = P.castor_wheel_d / 2.0
    ay = P.castor_y - P.castor_trail
    w = P.castor_wheel_w
    out = []
    for sx in (-1, 1):
        x = sx * P.castor_x
        top = P.castor_height
        plate = box_span((x - px / 2.0, x + px / 2.0), (P.castor_y - py / 2.0, P.castor_y + py / 2.0), (top - pt, top))
        for bx, by in _castor_bolts():
            plate = plate.cut(cyl(9.0, (bx, by, 100), (bx, by, 200)))
        swivel = cyl(70.0, (x, P.castor_y, top - pt - 14.0), (x, P.castor_y, top - pt))
        fork_pts = ((P.castor_y + 30.0, top - pt - 14.0), (P.castor_y - 30.0, top - pt - 14.0), (ay - 14.0, r),
                    (ay + 14.0, r - 14.0))
        forks = [plate_yz(fork_pts, x + side * (w / 2.0 + 3.0) + (0.0 if side > 0 else -5.0), 5.0)
                 for side in (-1, 1)]
        axle = cyl(12.0, (x - w / 2.0 - 10.0, ay, r), (x + w / 2.0 + 10.0, ay, r))
        out.append(fuse_all([plate, swivel] + forks + [axle]))
    return Part.makeCompound(out)


def castor_wheels():
    r = P.castor_wheel_d / 2.0
    ay = P.castor_y - P.castor_trail
    w = P.castor_wheel_w
    out = []
    for sx in (-1, 1):
        x = sx * P.castor_x
        out.append(cyl(P.castor_wheel_d, (x - w / 2.0, ay, r), (x + w / 2.0, ay, r)).cut(
            cyl(12.0, (x - w, ay, r), (x + w, ay, r))))
    return Part.makeCompound(out)


def castor_bolts():
    out = []
    for x, y in _castor_bolts():
        out.append(PP.bolt_z(8.0, x, y, P.castor_height - P.castor_plate[2], P.beam_z[0] + P.beam_wall,
                             head=13.0, k=5.3, m=6.8))
    return Part.makeCompound(out)
