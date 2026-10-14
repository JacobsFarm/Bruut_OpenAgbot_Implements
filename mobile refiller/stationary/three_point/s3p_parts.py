"""One function per part of the three-point frame station (frame, hitch, box supports, hoses).
All shapes in frame coordinates (origin = middle of the IBC footprint on the ground, y towards the tractor).
The IBC, the control box and the mast with the arm come from ../stc_parts.py.
"""
import math

import Part
from FreeCAD import Vector as V

import s3p_params as P
import stc_params as C
import stc_parts as G
from stc_parts import box_span, cyl_x, cyl_y, cyl_z, rtube, fuse_all, hose, poly_xz


# ---------------------------------------------------------------------
# Placements
# ---------------------------------------------------------------------
def ibc_placement():
    """IBC turned 180 deg: valve on the right (+x)."""
    return G.placement(0.0, 0.0, P.plat_z, 180.0)


def box_placement():
    """Control box under the platform, turned 180 deg: door to the rear, suction port right, discharge left."""
    return G.placement(*P.box_xyz, rot=180.0)


def mast_spec():
    return G.mast_spec(0.0, P.mast_y, P.low_z[0] + P.mast_foot[1], P.reach(), tube=P.mast_tube, in_face="-x",
                       in_z=P.in_z, folds=(0.0, 90.0, 180.0))


# ---------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------
RZ = (P.plat_z - P.rail[1], P.plat_z)


def side_rails():
    t = P.rail[2]
    return Part.makeCompound([rtube((s * P.side_x[0], s * P.side_x[1]), (-P.end_y[1], P.end_y[1]), RZ, t, "y")
                              for s in (-1, 1)])


def end_rails():
    """Front and rear rails between the side rails, and a middle one under the middle pallet runner."""
    t = P.rail[2]
    out = [rtube((-P.side_x[0], P.side_x[0]), (s * P.end_y[0], s * P.end_y[1]), RZ, t, "x") for s in (-1, 1)]
    out.append(rtube((-P.side_x[0], P.side_x[0]), (-30.0, 30.0), RZ, t, "x"))
    return Part.makeCompound(out)


def legs():
    a, t = P.leg
    lx, ly = P.leg_xy
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * lx, sy * ly
            out.append(rtube((x - a / 2.0, x + a / 2.0), (y - a / 2.0, y + a / 2.0), (P.foot[1], RZ[0]), t, "z"))
    return Part.makeCompound(out)


def feet():
    f, t = P.foot
    lx, ly = P.leg_xy
    return Part.makeCompound([box_span((sx * lx - f / 2.0, sx * lx + f / 2.0), (sy * ly - f / 2.0, sy * ly + f / 2.0),
                                       (0.0, t)) for sx in (-1, 1) for sy in (-1, 1)])


def lower_rails():
    """60 x 40 x 3 between the front legs and between the rear legs."""
    a = P.leg[0]
    lx, ly = P.leg_xy
    return Part.makeCompound([rtube((-lx + a / 2.0, lx - a / 2.0), (s * ly - 30.0, s * ly + 30.0), P.low_z, 3.0, "x")
                              for s in (-1, 1)])


def box_supports():
    w, h, t = P.box_sup
    ly = P.leg_xy[1] - 30.0
    return Part.makeCompound([rtube((s * P.box_sup_x - w / 2.0, s * P.box_sup_x + w / 2.0), (-ly, ly),
                                    (P.low_z[1] - h, P.low_z[1]), t, "y") for s in (-1, 1)])


def braces():
    """Diagonal braces in the side planes (x = +-610) and the rear plane (y = -530)."""
    lx, ly = P.leg_xy
    a = P.leg[0] / 2.0
    zb, zt = P.low_z[1] + 20.0, RZ[0] - 20.0
    out = []
    for s in (-1, 1):
        out.append(G.strut((s * lx, -ly + a, zb), (s * lx, ly - a, zt), P.brace_d))
    out.append(G.strut((-lx + a, -ly, zb), (lx - a, -ly, zt), P.brace_d))
    return fuse_all(out)


def corner_guides():
    return G.corner_guides(-C.ibc_len / 2.0, C.ibc_len / 2.0, -C.ibc_wid / 2.0, C.ibc_wid / 2.0, P.plat_z)


# ---------------------------------------------------------------------
# Hitch: plates with the lower pins, mast foot, top link plates, braces to the mast
# ---------------------------------------------------------------------
PX = P.cat2_spread / 2.0                       # outer face of the hitch plates


def hitch_plates():
    t, (y0, y1), (z0, z1) = P.hitch_plate
    out = []
    for s in (-1, 1):
        xs = sorted((s * (PX - t), s * PX))
        pl = box_span(xs, (y0, y1), (z0, z1))
        out.append(pl.cut(cyl_x(P.lower_pin[0] + 0.5, xs[0] - 1, xs[1] + 1, P.lower_pin_yz[0], P.lower_pin_yz[1])))
    return Part.makeCompound(out)


def lower_pins():
    d, ln = P.lower_pin
    y, z = P.lower_pin_yz
    out = []
    for s in (-1, 1):
        x0 = s * (PX - P.hitch_plate[0])
        x1 = s * (PX + ln)
        pin = cyl_x(d, x0, x1, y, z)
        collar = cyl_x(P.pin_collar[0], s * PX, s * (PX + P.pin_collar[1]), y, z)
        linch = cyl_y(10.0, y - 35.0, y + 35.0, s * (PX + ln - 15.0), z)
        out.append(fuse_all([pin, collar, linch]))
    return Part.makeCompound(out)


def mast_foot():
    w, h, t = P.mast_foot
    return rtube((-(PX - P.hitch_plate[0]), PX - P.hitch_plate[0]), (P.mast_y - w / 2.0, P.mast_y + w / 2.0),
                 (P.low_z[0], P.low_z[0] + h), t, "x")


def mast_link():
    """Short tube 100 x 40 between the front platform rail and the mast."""
    m = P.mast_tube[0]
    return rtube((-m / 2.0, m / 2.0), (P.end_y[1], P.mast_y - m / 2.0), RZ, 3.0, "y")


def top_link_plates():
    t, gap, ln, h = P.top_plate
    m = P.mast_tube[0]
    y0 = P.mast_y + m / 2.0
    zc = P.top_pin_z()
    out = []
    for s in (-1, 1):
        xs = sorted((s * gap / 2.0, s * (gap / 2.0 + t)))
        pl = box_span(xs, (y0, y0 + ln), (zc - h / 2.0, zc + h / 2.0))
        out.append(pl.cut(cyl_x(P.top_pin + 1.0, xs[0] - 1, xs[1] + 1, y0 + ln - 40.0, zc)))
    return Part.makeCompound(out)


def top_pin():
    t, gap, ln, h = P.top_plate
    y = P.mast_y + P.mast_tube[0] / 2.0 + ln - 40.0
    z = P.top_pin_z()
    return fuse_all([cyl_x(P.top_pin, -gap / 2.0 - t - 10.0, gap / 2.0 + t + 30.0, y, z),
                     cyl_x(40.0, -gap / 2.0 - t - 18.0, -gap / 2.0 - t - 10.0, y, z)])


def hitch_braces():
    """Round tubes from the hitch plates (above the pins) to the mast below the top link: an A in the front plane."""
    y = P.mast_y
    m = P.mast_tube[0] / 2.0
    out = [G.strut((s * (PX - P.hitch_plate[0] - 15.0), y, P.plat_z - 30.0),
                   (s * (m + 15.0), y, P.top_pin_z() - 40.0), 50.0) for s in (-1, 1)]
    return fuse_all(out)


# ---------------------------------------------------------------------
# Hoses
# ---------------------------------------------------------------------
def elbow_out():
    return G.xform(G.ELBOW_OUT, ibc_placement())


def suction_hose():
    """IBC valve (right) -> down beside the side rail -> in under the platform -> suction port of the box."""
    ex, ey, ez = elbow_out()
    px, py, pz = G.xform(C.SUCTION_PORT, box_placement())
    return hose([(ex, ey, ez), (ex, ey, pz + 60.0), (ex - 60.0, py, pz), (px, py, pz)])


def discharge_hose(M):
    """Discharge port (left side of the box) -> forward under the platform -> into the mast (-x face)."""
    px, py, pz = G.xform(C.DISCHARGE_PORT, box_placement())
    xo = px - 30.0
    pts = [(px, py, pz), (xo, py, pz), (xo, P.end_y[0] - 80.0, pz), (xo + 40.0, P.mast_y, M["in_z"])]
    return hose(pts + G.mast_in_points(M))
