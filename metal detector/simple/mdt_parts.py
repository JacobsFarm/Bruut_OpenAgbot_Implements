"""Parts of the metal detector. Every function returns a Part shape in robot coordinates, in the work pose (boom
down, coil on its skids). build_mdt.py puts the boom parts in a sub-Part that turns about the pivot axis (x).
"""
import math

import Part
from FreeCAD import Vector as V

import mdt_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
rect_tube = PP.rect_tube
fuse_all = PP.fuse_all
plate_yz = PP.plate_yz

PY, PZ = P.pivot
_L = math.hypot(P.boom_end[0] - PY, P.boom_end[1] - PZ)
DIR = ((P.boom_end[0] - PY) / _L, (P.boom_end[1] - PZ) / _L)      # boom direction (y, z)
HALF_DZ = P.boom_w / 2.0 / DIR[0]                                   # half tube height measured vertically


def boom_point(f):
    """(y, z) on the boom centre line at fraction f of the pivot-to-end length."""
    return PY + DIR[0] * _L * f, PZ + DIR[1] * _L * f


def boom_z(y):
    return PZ + (y - PY) * DIR[1] / DIR[0]


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


# ---------------------------------------------------------------------
# Fixed: root brackets, bolts, pivot pin
# ---------------------------------------------------------------------
def _base(sx):
    zt = P.robot_lower_beam_z[1]
    y0, y1 = P.robot_front_beam_y
    x0, x1 = P.base_x
    b = box_span((x0, x1), (y0 - 10.0, y1 + 10.0), (zt, zt + P.base_t))
    for xb in P.bolt_x:
        b = b.cut(cyl(P.m10_hole, (xb, (y0 + y1) / 2.0, zt - 1), (xb, (y0 + y1) / 2.0, zt + P.base_t + 1)))
    return b if sx > 0 else mirror_x(b)


def _side(sx):
    s = plate_yz(P.side_pts, P.bracket_x, P.bracket_t)
    s = s.cut(cyl(P.pivot_d + 0.5, (0, PY, PZ), (400, PY, PZ)))
    return s if sx > 0 else mirror_x(s)


def _mast():
    yb, zb = P.act_base
    pts = ((560.0, 700.0), (640.0, 690.0), (yb + 22.0, zb), (yb - 22.0, zb))
    out = []
    for x0, x1 in P.mast_x:
        pl = plate_yz(pts, x0, x1 - x0).fuse(cyl(44.0, (x0, yb, zb), (x1, yb, zb)))
        out.append(pl)
    spacer = box_span((P.mast_x[0][1], P.mast_x[1][0]), (575.0, 635.0), (700.0, 740.0))
    s = fuse_all(out + [spacer])
    return s.cut(cyl(12.5, (150, yb, zb), (250, yb, zb)))


def bracket_left():
    return fuse_all([_base(-1), _side(-1)])


def bracket_right():
    return fuse_all([_base(1), _side(1), _mast()])


def bracket_bolts():
    zt = P.robot_lower_beam_z[1]
    yc = sum(P.robot_front_beam_y) / 2.0
    out = []
    for sx in (-1, 1):
        for xb in P.bolt_x:
            out.append(PP.bolt_z(10.0, sx * xb, yc, P.robot_lower_beam_z[0], zt + P.base_t))
    return Part.makeCompound(out)


def pivot_pin():
    """Stainless pin O16 through both side plates and both boom tubes, with collars outside."""
    x = P.bracket_x + P.bracket_t
    return Part.makeCompound([cyl(P.pivot_d, (-x - 6, PY, PZ), (x + 6, PY, PZ)),
                              cyl(26.0, (-x - 12, PY, PZ), (-x, PY, PZ)), cyl(26.0, (x, PY, PZ), (x + 12, PY, PZ))])


# ---------------------------------------------------------------------
# Boom (turns about the pivot): 2 GFRP tubes, 2 cross tubes, lug, electronics box, carrier plate, wedges
# ---------------------------------------------------------------------
def _tube(sx):
    a = (sx * P.boom_x, PY - DIR[0] * 40.0, PZ - DIR[1] * 40.0)
    b = (sx * P.boom_x, P.boom_end[0], P.boom_end[1])
    t = rect_tube(a, b, P.boom_w, P.boom_w, P.boom_wall, up=(1.0, 0.0, 0.0))
    return t.cut(cyl(P.pivot_d + 0.5, (-400, PY, PZ), (400, PY, PZ)))


def boom_tubes():
    return Part.makeCompound([_tube(-1), _tube(1)])


def cross_tubes():
    xi = P.boom_x - P.boom_w / 2.0
    out = []
    for f in P.cross_at:
        y, z = boom_point(f)
        out.append(rect_tube((-xi, y, z), (xi, y, z), P.cross_w, P.cross_w, P.boom_wall))
    return Part.makeCompound(out)


def lug():
    yp, zp = P.act_pin
    zt = boom_z(yp) - HALF_DZ + 10.0
    s = box_span(P.lug_x, (yp - 25.0, yp + 25.0), (zt, zp + P.float_slot + 25.0))
    slot = box_span((P.lug_x[0] - 1, P.lug_x[1] + 1), (yp - 6.5, yp + 6.5), (zp - 6.5, zp + P.float_slot + 6.5))
    return s.cut(slot)


def ebox():
    y, z = boom_point(P.cross_at[0])
    w, d, h = P.ebox
    zt = z + P.cross_w / 2.0
    return box_span((-w / 2.0, w / 2.0), (y - d / 2.0, y + d / 2.0), (zt, zt + h))


def carrier():
    """GFRP plate 10 mm on the coil housing, the boom ends on 2 GFRP wedges."""
    z0 = P.house_z[1]
    plate = box_span((-P.boom_x - 40.0, P.boom_x + 40.0), P.carrier_y, (z0, z0 + P.carrier_t))
    out = [plate]
    zp = z0 + P.carrier_t
    y0, y1 = P.carrier_y[0], P.boom_end[0]
    pts = ((y0, zp), (y1, zp), (y1, boom_z(y1) - HALF_DZ), (y0, boom_z(y0) - HALF_DZ))
    for sx in (-1, 1):
        x0 = sx * P.boom_x - P.boom_w / 2.0
        out.append(plate_yz(pts, x0, P.boom_w).cut(_tube(sx)))
    return fuse_all(out)


# ---------------------------------------------------------------------
# Search coil: housing, winding, skids
# ---------------------------------------------------------------------
def _rounded(sx, sy, z0, z1, r):
    cx, cy = P.coil_c
    b = Part.makeBox(sx, sy, z1 - z0, V(cx - sx / 2.0, cy - sy / 2.0, z0))
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1.0]
    return b.makeFillet(r, edges)


def housing():
    sx, sy = P.coil_size
    t = P.house_t
    z0, z1 = P.house_z
    return _rounded(sx, sy, z0, z1, P.coil_r).cut(_rounded(sx - 2 * t, sy - 2 * t, z0 + t, z1 - t, P.coil_r - t))


def winding():
    sx, sy = P.coil_size
    g = P.house_t + 6.0
    zc = sum(P.house_z) / 2.0
    w = P.wind
    outer = _rounded(sx - 2 * g, sy - 2 * g, zc - w / 2.0, zc + w / 2.0, P.coil_r - g)
    inner = _rounded(sx - 2 * (g + w), sy - 2 * (g + w), zc - w, zc + w, P.coil_r - g - w)
    return outer.cut(inner)


def skids():
    cy = P.coil_c[1]
    y0, y1 = cy - P.coil_size[1] / 2.0, cy + P.coil_size[1] / 2.0
    pts = ((y0, 0.0), (y1 - P.skid_nose, 0.0), (y1, P.skid_h), (y0, P.skid_h))
    return Part.makeCompound([plate_yz(pts, sx * P.skid_x - P.skid_w / 2.0, P.skid_w) for sx in (-1, 1)])


# ---------------------------------------------------------------------
# Lift actuator
# ---------------------------------------------------------------------
def rod_point(lift_deg):
    """Rod pin (y, z): moves with the lug when lifted; in a hollow (lift < 0) the lug drops and the pin stays."""
    if lift_deg <= 0.0:
        return P.act_pin
    a = math.radians(lift_deg)
    dy, dz = P.act_pin[0] - PY, P.act_pin[1] - PZ
    return PY + dy * math.cos(a) - dz * math.sin(a), PZ + dy * math.sin(a) + dz * math.cos(a)


def actuator(lift_deg=0.0):
    """(body, rod, pins, length) of the actuator at this lift angle."""
    x = P.act_x
    yb, zb = P.act_base
    yr, zr = rod_point(lift_deg)
    a, b = V(x, yb, zb), V(x, yr, zr)
    u = b - a
    L = u.Length
    u.normalize()
    body_len = P.act_retracted - 90.0
    body = fuse_all([cyl(P.act_body_d, a + u * 35.0, a + u * (35.0 + body_len)),
                     cyl(30.0, a - V(10, 0, 0), a + V(10, 0, 0)),
                     rect_tube(a, a + u * 35.0, 20.0, 20.0, up=(1.0, 0.0, 0.0))])
    body = body.cut(cyl(12.5, a - V(20, 0, 0), a + V(20, 0, 0)))
    rod = fuse_all([cyl(P.act_rod_d, a + u * (35.0 + body_len - 20.0), b - u * 10.0),
                    cyl(26.0, b - V(10, 0, 0), b + V(10, 0, 0))])
    rod = rod.cut(cyl(12.5, b - V(20, 0, 0), b + V(20, 0, 0)))
    pins = Part.makeCompound([cyl(12.0, (P.mast_x[0][0], yb, zb), (P.mast_x[1][1] + 4.0, yb, zb)),
                              cyl(12.0, (P.lug_x[0], yr, zr), (x + 16.0, yr, zr))])
    return body, rod, pins, L
