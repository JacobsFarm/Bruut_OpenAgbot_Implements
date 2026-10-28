"""Parts of the charging dock. Every function returns a Part shape in robot coordinates with the robot docked (robot
centre at the origin); build_cdk moves the Station group for the approach.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cdk_params as P



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




def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


PAD_Z = P.pe_z + P.pe_block[2] / 2.0


def bars_y():
    """(y0, y1) of the copper bars: their rear face touches the pads when docked."""
    y0 = P.pads_y()[1] + P.gap_docked
    return y0, y0 + P.bar[1]


def head_y():
    y0 = bars_y()[1]
    return y0, y0 + P.head[1]


# ---------------------------------------------------------------------
# Robot side
# ---------------------------------------------------------------------
def robot_bracket():
    """Plate 6 mm on the front face of the front outer lower beam with a top flange over the beam (notched round the
    GNSS mount), 2 x M10 into the hole grid at x +-125."""
    y0, y1 = P.robot_front_beam_y
    zt = P.robot_lower_beam_z[1]
    plate = box_span((-P.bk_x, P.bk_x), P.bk_y, (P.bk_z[0], zt + 6.0))
    flange = box_span((-P.bk_x, P.bk_x), (y0, P.bk_y[1]), (zt, zt + 6.0))
    s = plate.fuse(flange).removeSplitter()
    s = s.cut(box_span((-30.0, 30.0), (y0 - 1, y1 - 2.0), (zt - 1, zt + 7)))
    for x in (-125.0, 125.0):
        s = s.cut(cyl(P.m10_hole, (x, (y0 + y1) / 2.0, zt - 1), (x, (y0 + y1) / 2.0, zt + 7)))
    return s


def bracket_bolts():
    y = sum(P.robot_front_beam_y) / 2.0
    zb = P.robot_lower_beam_z
    return Part.makeCompound([bolt_z(10.0, x, y, zb[0], zb[1] + 6.0) for x in (-125.0, 125.0)])


def pe_carrier():
    w, d, h = P.pe_block
    s = box_span((-w / 2, w / 2), (P.bk_y[1], P.bk_y[1] + d), (P.pe_z, P.pe_z + h))
    for x in (-P.pad_x, P.pad_x):
        s = s.cut(box_span((x - P.pad[0] / 2 - 1, x + P.pad[0] / 2 + 1), (P.bk_y[1] + d - 12.0, P.bk_y[1] + d + 1),
                           (PAD_Z - P.pad[2] / 2 - 1, PAD_Z + P.pad[2] / 2 + 1)))
    return s.cut(cyl(P.pilot_d + 1.0, (0, P.bk_y[1] - 1, PAD_Z), (0, P.bk_y[1] + d + 1, PAD_Z)))


def pads():
    """2 copper pads (+ right, - left) on 2 springs each, half compressed when docked."""
    w, t, h = P.pad
    y1 = P.pads_y()[1]
    out = []
    for x in (-P.pad_x, P.pad_x):
        out.append(box_span((x - w / 2, x + w / 2), (y1 - t, y1), (PAD_Z - h / 2, PAD_Z + h / 2)))
    return Part.makeCompound(out)


def springs():
    y0 = P.bk_y[1] + P.pe_block[1] - 12.0
    y1 = P.pads_y()[1] - P.pad[1]
    return Part.makeCompound([cyl(10.0, (x + dx, y0, PAD_Z), (x + dx, y1, PAD_Z))
                              for x in (-P.pad_x, P.pad_x) for dx in (-15.0, 15.0)])


def pilot():
    y0 = P.bk_y[1]
    return cyl(P.pilot_d, (0, y0, PAD_Z), (0, P.pads_y()[1] + P.pilot_len, PAD_Z))


# ---------------------------------------------------------------------
# Station
# ---------------------------------------------------------------------
def base_plate():
    bx, by, bt = P.base
    s = box_span((-bx / 2, bx / 2), (P.base_y0, P.base_y0 + by), (0.0, bt))
    for x in (-bx / 2 + 40, bx / 2 - 40):
        for y in (P.base_y0 + 40, P.base_y0 + by - 40):
            s = s.cut(cyl(P.anchor[0] + 2.0, (x, y, -1), (x, y, bt + 1)))
    return s


def anchors():
    bx, by, bt = P.base
    out = []
    for x in (-bx / 2 + 40, bx / 2 - 40):
        for y in (P.base_y0 + 40, P.base_y0 + by - 40):
            out.append(cyl(P.anchor[0], (x, y, -P.anchor[1]), (x, y, bt + 15.0)))
            out.append(cyl(40.0, (x, y, bt), (x, y, bt + 8.0)))
    return Part.makeCompound(out)


def post():
    p = P.post / 2.0
    tube = tube_span((-p, p), (P.post_y - p, P.post_y + p), (P.base[2], P.post_h), 4.0, "z")
    gussets = []
    for sx in (-1, 1):
        pts = ((P.post_y - p - 120.0, P.base[2]), (P.post_y + p + 120.0, P.base[2]), (P.post_y + p, P.base[2] + 150.0),
               (P.post_y - p, P.base[2] + 150.0))
        gussets.append(plate_yz(pts, sx * p - (8.0 if sx < 0 else 0.0), 8.0))
    return fuse_all([tube] + gussets)


def arm_and_head():
    """Arm tube 60 x 40 x 3 from the post back to the head; head plate (PE 20 on a steel 3 mm backing) with a hole
    for the pilot pin; funnel plates 3 mm."""
    hy0, hy1 = head_y()
    p = P.post / 2.0
    arm = tube_span((-P.arm[0] / 2, P.arm[0] / 2), (hy1, P.post_y - p), P.arm_z, 3.0, "y")
    w, d, h = P.head
    head = box_span((-w / 2, w / 2), (hy0, hy1), (P.head_z, P.head_z + h))
    head = head.cut(cyl(P.pilot_d + 4.0, (0, hy0 - 1, PAD_Z), (0, hy1 + 1, PAD_Z)))
    return arm, head


def funnel():
    """2 V-plates 3 mm from the head edges back and out: throat +-165 (the PE block is +-150), mouth +-225."""
    hy0 = bars_y()[0]
    out = []
    t = 3.0
    pts = [(P.pe_block[0] / 2 + 15.0, hy0 + 15.0), (P.pe_block[0] / 2 + 15.0 + P.funnel_open * 0.75, P.bk_y[1] + 10.0)]
    (x0, y0), (x1, y1) = pts
    poly = [(x0, y0), (x1, y1), (x1 + t, y1), (x0 + t, y0), (x0 + t, head_y()[1]), (x0, head_y()[1])]
    w = Part.makePolygon([V(x, y, P.head_z) for x, y in poly] + [V(poly[0][0], poly[0][1], P.head_z)])
    s = Part.Face(w).extrude(V(0, 0, P.head[2]))
    return both(s)


def bars():
    w, t, h = P.bar
    y0, y1 = bars_y()
    return Part.makeCompound([box_span((x - w / 2, x + w / 2), (y0, y1), (PAD_Z - h / 2, PAD_Z + h / 2))
                              for x in (-P.bar_x, P.bar_x)])


def charger():
    w, d, h = P.charger_box
    p = P.post / 2.0
    return box_span((-w / 2, w / 2), (P.post_y + p, P.post_y + p + d), (600.0, 600.0 + h))


def roof():
    w, d, t = P.roof
    return box_span((-w / 2, w / 2), (P.post_y + 190.0 - d, P.post_y + 190.0), (P.post_h, P.post_h + t))
