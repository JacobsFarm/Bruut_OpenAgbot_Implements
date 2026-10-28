"""Parts of the dumper barrow. Every function returns a Part shape in robot coordinates (the tipping part drawn down;
build_dmb turns the Tip group about the hinge).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dmb_params as P



# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def tube_span(x, y, z, t, axis):
    """Axis-aligned rectangular tube (wall t) filling the box x, y, z, open along 'axis'."""
    outer = box_span(x, y, z)
    spans = {"x": list(x), "y": list(y), "z": list(z)}
    for k in spans:
        if k == axis:
            spans[k] = [spans[k][0] - 1.0, spans[k][1] + 1.0]
        else:
            spans[k] = [spans[k][0] + t, spans[k][1] - t]
    return outer.cut(box_span(spans["x"], spans["y"], spans["z"]))


def rect_tube(p0, p1, w, h, t=0.0, up=(0.0, 0.0, 1.0)):
    """Rectangular tube (or solid bar for t = 0) from p0 to p1, w across, h along 'up'."""
    a, b = V(*p0), V(*p1)
    X = b - a
    length = X.Length
    X.normalize()
    u = V(*up)
    Z = u - X * u.dot(X)
    Z.normalize()
    Y = Z.cross(X)
    m = App.Matrix(X.x, Y.x, Z.x, a.x, X.y, Y.y, Z.y, a.y, X.z, Y.z, Z.z, a.z, 0, 0, 0, 1)
    s = Part.makeBox(length, w, h, V(0, -w / 2.0, -h / 2.0))
    if t > 0.0:
        s = s.cut(Part.makeBox(length + 2.0, w - 2 * t, h - 2 * t, V(-1.0, -w / 2.0 + t, -h / 2.0 + t)))
    s.transformShape(m)
    return s


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def plate_yz(pts, x0, t):
    """Plate in the y-z plane from a list of (y, z) points, thickness t from x0 along +x."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(t, 0, 0))


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    """Vertical bolt: head under z_head, shank up to the nut on top of z_nut."""
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def bolt_axis(d, p_head, p_nut, head, k, m):
    """Bolt along any axis: head outside p_head, nut outside p_nut."""
    a, b = V(*p_head), V(*p_nut)
    u = b - a
    u.normalize()
    return Part.makeCompound([cyl(head * 1.1, a - u * k, a), cyl(d, a, b + u * (m + 3.0)), cyl(head * 1.1, b, b + u * m)])




def cyl_x(d, x0, x1, y, z):
    return cyl(d, (x0, y, z), (x1, y, z))


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


HY, HZ = P.hinge
TOP = P.rail_z[1] + P.sheet + P.bin_h       # rim height


# ---------------------------------------------------------------------
# Mount (fixed)
# ---------------------------------------------------------------------
def bearers():
    out = []
    for yc in P.bearer_y.values():
        t = tube_span((-P.bearer_x, P.bearer_x), (yc - P.bearer / 2, yc + P.bearer / 2), P.bearer_z, 3.0, "x")
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                t = t.cut(cyl(P.m10_hole, (sx * xb, yc, 600), (sx * xb, yc, 800)))
        out.append(t)
    return Part.makeCompound(out)


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * xb, yc, P.robot_upper_beam_z[0], P.bearer_z[1])
                              for yc in P.bearer_y.values() for sx in (-1, 1) for xb in P.robot_upper_beam_x])


def rest_pads():
    w, d, t = P.rest_pad
    yc = P.bearer_y["front"]
    return both(box_span((P.rail_x - w / 2, P.rail_x + w / 2), (yc - d / 2, yc + d / 2), (P.bearer_z[1], P.bearer_z[1] + t)))


def hinge_lugs():
    """2 plates 10 mm per rail on the hinge bearer, either side of the rail boss."""
    yc = P.bearer_y["hinge"]
    out = []
    for x0 in (P.rail_x - 20.0 - 12.0, P.rail_x + 22.0):
        pts = ((yc - 25.0, P.bearer_z[1]), (yc + 25.0, P.bearer_z[1]), (HY + 18.0, HZ), (HY - 18.0, HZ))
        p = plate_yz(pts, x0, 10.0).fuse(cyl_x(36.0, x0, x0 + 10.0, HY, HZ)).removeSplitter()
        out.append(p.cut(cyl_x(P.hinge_pin_d + 0.5, x0 - 1, x0 + 11, HY, HZ)))
    return both(Part.makeCompound(out))


def hinge_pins():
    return both(cyl_x(P.hinge_pin_d, P.rail_x - 38.0, P.rail_x + 38.0, HY, HZ))


def act_lugs():
    """2 plates 8 mm per actuator hanging from the actuator bearer between the upper beams, base pin."""
    yb, zb = P.act_base
    out = []
    for x0 in (P.act_x - 22.0 - 8.0, P.act_x + 22.0):
        yc = P.bearer_y["act"]
        pts = ((yc - 20.0, P.bearer_z[0]), (yb + 25.0, P.bearer_z[0]), (yb + 18.0, zb), (yb - 18.0, zb))
        p = plate_yz(pts, x0, 8.0).fuse(cyl_x(36.0, x0, x0 + 8.0, yb, zb)).removeSplitter()
        out.append(p.cut(cyl_x(12.5, x0 - 1, x0 + 9, yb, zb)))
    return both(Part.makeCompound(out))


# ---------------------------------------------------------------------
# Tipping part (drawn down): subframe and bin
# ---------------------------------------------------------------------
def subframe():
    """2 rails 40 x 40 x 3 with hinge bosses, actuator cross tube with 2 pairs of rod lugs."""
    parts = []
    for sx in (-1, 1):
        x = sorted((sx * (P.rail_x - 20.0), sx * (P.rail_x + 20.0)))
        parts.append(tube_span(x, P.rail_y, P.rail_z, 3.0, "y"))
        parts.append(box_span(x, (P.rail_y[0], P.rail_y[0] + 3.0), P.rail_z))
        parts.append(cyl_x(36.0, x[0], x[1], HY, HZ))
    parts.append(tube_span((-P.rail_x + 20.0, P.rail_x - 20.0), P.cross_y, P.rail_z, 3.0, "x"))
    yr, zr = P.act_rod
    for sx in (-1, 1):
        for x0 in (P.act_x - 15.0 - 6.0, P.act_x + 15.0):
            xx = x0 if sx > 0 else -x0 - 6.0
            pts = ((P.cross_y[0], P.rail_z[0]), (P.cross_y[1], P.rail_z[0]), (yr + 14.0, zr), (yr - 14.0, zr))
            parts.append(plate_yz(pts, xx, 6.0).fuse(cyl_x(28.0, xx, xx + 6.0, yr, zr)))
    s = fuse_all(parts)
    s = s.cut(cyl_x(P.hinge_pin_d + 0.5, -600, 600, HY, HZ))
    return s.cut(cyl_x(12.5, -600, 600, yr, zr))


def bin_body():
    """Floor, front wall, side walls and the sloping rear lip, 2 mm; rim angle 30 x 30 x 3 round the top."""
    t = P.sheet
    z0 = P.rail_z[1]
    y0, y1 = P.bin_y
    yl = y0 - P.bin_h * math.tan(math.radians(P.lip_deg))
    x = P.bin_x
    floor = box_span((-x, x), (y0, y1), (z0, z0 + t))
    front = box_span((-x, x), (y1 - t, y1), (z0 + t, TOP))
    side_pts = ((y0, z0 + t), (y1, z0 + t), (y1, TOP), (yl, TOP))
    side = plate_yz(side_pts, x - t, t)
    lip_pts = ((y0, z0), (y0 + t, z0 + t), (yl + t, TOP), (yl, TOP))
    lip = plate_yz(lip_pts, -x + t, 2 * (x - t))
    a, _, rt = P.rim
    rim = [box_span((-x, x), (y1 - a, y1), (TOP - rt, TOP)), box_span((-x, x), (yl, yl + a), (TOP - rt, TOP))]
    for sx in (-1, 1):
        rim.append(box_span(sorted((sx * x, sx * (x - a))), (yl, y1), (TOP - rt, TOP)))
    return Part.makeCompound([floor, front, side, mirror_x(side), lip] + [r for r in rim])


def actuators(deg=0.0):
    """(bodies, rods) of the 2 tipping actuators at a tip angle."""
    yb, zb = P.act_base
    yr, zr = P.rotate(P.act_rod, deg)
    bodies, rods = [], []
    for sx in (-1, 1):
        x = sx * P.act_x
        A, B = V(x, yb, zb), V(x, yr, zr)
        u = B - A
        u.normalize()
        body_len = P.act_retracted - 90.0
        bodies.append(cyl(P.act_body_d, A + u * 15.0, A + u * (15.0 + body_len)))
        bodies.append(cyl(30.0, A - u * 12.0, A + u * 15.0))
        rods.append(cyl(P.act_rod_d, A + u * (body_len + 5.0), B - u * 12.0))
        rods.append(cyl(26.0, B - u * 14.0, B + u * 12.0))
    return Part.makeCompound(bodies), Part.makeCompound(rods)


def act_pins(deg=0.0):
    yb, zb = P.act_base
    yr, zr = P.rotate(P.act_rod, deg)
    out = []
    for sx in (-1, 1):
        x = sx * P.act_x
        out.append(cyl_x(12.0, x - 32.0, x + 32.0, yb, zb))
    return Part.makeCompound(out)


def control_box():
    """Stop / go / follow / tip button box on the outside of the left bin wall (tips with the bin, cable loop)."""
    x0 = -P.bin_x
    return box_span((x0 - 90.0, x0), (-50.0, 50.0), (900.0, 990.0)).fuse(
        cyl(30.0, (x0 - 45.0, 0.0, 990.0), (x0 - 45.0, 0.0, 1005.0)))
