"""Parts of the swarm kit, in robot coordinates."""
import Part
from FreeCAD import Vector as V

import swm_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all

Y = -P.hole_y
Z0 = P.upper_beam_top


def bar():
    s = box_span(P.bar_x, (Y - P.bar_w / 2.0, Y + P.bar_w / 2.0), (Z0, Z0 + P.bar_t))
    for x in (-325.0, 325.0):
        s = s.cut(cyl(10.5, (x, Y, Z0 - 1), (x, Y, Z0 + P.bar_t + 1)))
    return s


def bar_bolts():
    return Part.makeCompound([PP.bolt_z(10.0, x, Y, Z0 - 40.0, Z0 + P.bar_t) for x in (-325.0, 325.0)])


def post():
    w = P.post_w / 2.0
    return tube_span((P.post_x - w, P.post_x + w), (Y - w, Y + w), (Z0 + P.bar_t, P.post_top), 3.0, "z")


def light_segments():
    """Status light tower on the post top: one solid per colour segment (green, yellow, red, blue from the bottom)."""
    d, n, h = P.lights
    return [cyl(d, (P.post_x, Y, P.post_top + i * h), (P.post_x, Y, P.post_top + (i + 1) * h)) for i in range(n)]


def whip():
    d, n, h = P.lights
    z = P.post_top + n * h
    base = cyl(30.0, (P.post_x, Y, z), (P.post_x, Y, z + 25.0))
    return fuse_all([base, cyl(P.whip[0], (P.post_x, Y, z + 25.0), (P.post_x, Y, z + 25.0 + P.whip[1]))])


def box():
    w, d, h = P.box
    x0 = 60.0
    return box_span((x0, x0 + w), (Y - d / 2.0, Y + d / 2.0), (Z0 + P.bar_t, Z0 + P.bar_t + h))
