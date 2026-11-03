"""Parts of the camera bridge of the mole mapper, in robot coordinates. The cone penetrometer is the soil compaction
meter (build_scm.build_into), unchanged.
"""
import math

import Part
from FreeCAD import Vector as V

import mmp_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
rect_tube = PP.rect_tube
fuse_all = PP.fuse_all

ZT = P.robot_lower_beam_z[1]
YC = sum(P.robot_front_beam_y) / 2.0
PW = P.post_w


def brackets():
    """Base plate on top of the front outer lower beam (2 x M10) and an upright plate the post is welded to."""
    bx, by, bt = P.bracket
    out = []
    for sx in (-1, 1):
        x = sx * P.post_x
        base = box_span((x - bx / 2.0, x + bx / 2.0), (P.robot_front_beam_y[0] - 10.0, P.post_y[0]), (ZT, ZT + bt))
        up = box_span((x - bx / 2.0, x + bx / 2.0), (P.post_y[0] - bt, P.post_y[0]), (ZT + bt, ZT + 120.0))
        b = base.fuse(up)
        for xb in P.bolt_x:
            b = b.cut(cyl(10.5, (sx * xb, YC, ZT - 1), (sx * xb, YC, ZT + bt + 1)))
        out.append(b)
    return Part.makeCompound(out)


def bracket_bolts():
    return Part.makeCompound([PP.bolt_z(10.0, sx * xb, YC, P.robot_lower_beam_z[0], ZT + P.bracket[2])
                              for sx in (-1, 1) for xb in P.bolt_x])


def posts():
    return Part.makeCompound([tube_span((sx * P.post_x - PW / 2.0, sx * P.post_x + PW / 2.0), P.post_y,
                                        (ZT + P.bracket[2], P.bar_z[0]), 3.0, "z") for sx in (-1, 1)])


def cross_bar():
    return tube_span((-P.bar_x, P.bar_x), P.post_y, P.bar_z, 3.0, "x")


def stays():
    """Flat 30 x 5 from each post (at stay_z0) out and up to the bar."""
    yc = sum(P.post_y) / 2.0
    out = []
    for sx in (-1, 1):
        a = (sx * (P.post_x + PW / 2.0), yc, P.stay_z0)
        b = (sx * P.stay_x, yc, P.bar_z[0])
        out.append(rect_tube(a, b, 5.0, 30.0, up=(0.0, 1.0, 0.0)))
    return Part.makeCompound(out)


def _cam(x, box):
    """Camera on a short plate on the front face of the bar, tilted forward."""
    w, d, h = box
    y0 = P.post_y[1]
    yc = y0 + d / 2.0
    top = P.bar_z[1]
    b = box_span((x - w / 2.0, x + w / 2.0), (y0, y0 + d), (top - h, top))
    lens = cyl(36.0, (x, yc, top - h - 20.0), (x, yc, top - h))
    s = b.fuse(lens)
    s.rotate(V(x, y0, top), V(1, 0, 0), P.cam_tilt)
    return s


def cameras():
    return Part.makeCompound([_cam(x, P.cam_box) for x in P.cam_x])


def thermal():
    return _cam(P.thermal_x, P.thermal_box)


def hill(x, y, d=400.0, h=120.0):
    """A molehill (render only): spherical cap."""
    r = (d * d / 4.0 + h * h) / (2.0 * h)
    s = Part.makeSphere(r, V(x, y, h - r))
    return s.common(box_span((x - d, x + d), (y - d, y + d), (0.0, h + 1)))


def tunnel(p0, p1, z=-150.0):
    """A mole tunnel (render only, cut-away view)."""
    return cyl(P.tunnel_d, (p0[0], p0[1], z), (p1[0], p1[1], z))


def ring_points(cx, cy):
    return [(cx + P.ring_r * math.cos(2 * math.pi * i / P.ring_n), cy + P.ring_r * math.sin(2 * math.pi * i / P.ring_n))
            for i in range(P.ring_n)]
