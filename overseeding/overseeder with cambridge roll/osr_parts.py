"""Parts that only exist in the combination: the spacer blocks and bolts that hang the seeder unit between the arms
of the roll. Everything else comes from cbr_parts (hitch, roll, frame, drawbar) and ovd_parts (seeder unit).
"""
import Part

import osr_params as P
import cbr_parts as C


def hanger_blocks():
    out = []
    for s in (-1, 1):
        x = sorted((s * P.hanger_x[0], s * P.hanger_x[1]))
        for v in P.hanger_v:
            b = C.box_span(x, (P.unit_y + v[0], P.unit_y + v[1]), P.hanger_z)
            vc = P.unit_y + sum(v) / 2.0
            zc = sum(P.hanger_z) / 2.0
            out.append(b.cut(C.cyl(P.C.m10_hole, (x[0] - 1, vc, zc), (x[1] + 1, vc, zc))))
    return Part.makeCompound(out)


def hanger_holes():
    """Holes O10.4 drilled through the arms and the end plates for the hanger bolts."""
    zc = sum(P.hanger_z) / 2.0
    out = []
    for s in (-1, 1):
        for v in P.hanger_v:
            vc = P.unit_y + sum(v) / 2.0
            out.append(C.cyl(P.C.m10_hole, (s * 480.0, vc, zc), (s * 570.0, vc, zc)))
    return Part.makeCompound(out)


def hanger_bolts():
    """M10 from the outside of the arm through arm, spacer and end plate, nut on the inside of the end plate."""
    out = []
    zc = sum(P.hanger_z) / 2.0
    for s in (-1, 1):
        for v in P.hanger_v:
            vc = P.unit_y + sum(v) / 2.0
            out.append(C.bolt_x(10.0, s * P.C.arm_x[1], s * (P.O.width / 2.0), vc, zc))
    return Part.makeCompound(out)
