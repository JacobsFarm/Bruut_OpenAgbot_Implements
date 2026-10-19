"""Parts of the Cambridge roll and the tow hitch. Every function returns a Part shape in robot coordinates.

The frame functions take the axle and cross beam position as arguments (defaults = the stand-alone roll), so the
combination with the overseeder can use a longer frame without copying the parts.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cbr_params as P


# ---------------------------------------------------------------------
# Helpers (also used by the overseeder)
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


def _matrix(p0, p1, up):
    a, b = V(*p0), V(*p1)
    X = b - a
    X.normalize()
    u = V(*up)
    Z = u - X * u.dot(X)
    Z.normalize()
    Y = Z.cross(X)
    return App.Matrix(X.x, Y.x, Z.x, a.x, X.y, Y.y, Z.y, a.y, X.z, Y.z, Z.z, a.z, 0, 0, 0, 1), (b - a).Length


def rect_tube(p0, p1, w, h, t=0.0, up=(0.0, 0.0, 1.0)):
    """Rectangular tube (or solid bar for t = 0) from p0 to p1, w across, h along 'up'."""
    m, length = _matrix(p0, p1, up)
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


def stadium_x(length_z, width_y, t, x0, y, z):
    """Plate in the y-z plane (thickness t from x0 along +x), rounded ends along z (flange of a 2-bolt bearing)."""
    r = width_y / 2.0
    core = box_span((x0, x0 + t), (y - r, y + r), (z - length_z / 2.0 + r, z + length_z / 2.0 - r))
    ends = [cyl(width_y, (x0, y, zz), (x0 + t, y, zz)) for zz in (z - length_z / 2.0 + r, z + length_z / 2.0 - r)]
    return fuse_all([core] + ends)


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    """Vertical bolt: hex-ish head (cylinder) under z_head, shank up to z_nut, nut on top."""
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def bolt_x(d, x_head, x_nut, y, z, head=17.0, k=6.4, m=8.4):
    """Bolt along x: head outside x_head (on the side away from x_nut), nut beyond x_nut."""
    s = 1.0 if x_nut > x_head else -1.0
    return Part.makeCompound([cyl(head * 1.1, (x_head - s * k, y, z), (x_head, y, z)),
                              cyl(d, (x_head, y, z), (x_nut + s * (m + 3.0), y, z)),
                              cyl(head * 1.1, (x_nut, y, z), (x_nut + s * m, y, z))])


# ---------------------------------------------------------------------
# Tow hitch (fixed to the robot)
# ---------------------------------------------------------------------
def hitch_plate():
    x, y, z = P.hitch_plate
    s = box_span(x, y, z)
    for bx in P.hitch_bolts[0]:
        for by in P.hitch_bolts[1]:
            s = s.cut(cyl(P.m10_hole, (bx, by, z[0] - 1), (bx, by, z[1] + 1)))
    return s


def hitch_bolts():
    z = P.hitch_plate[2]
    return Part.makeCompound([bolt_z(10.0, bx, by, z[0], P.robot_lower_beam_z[1])
                              for bx in P.hitch_bolts[0] for by in P.hitch_bolts[1]])


def _stud_hole():
    bx, by = P.ball
    return cyl(P.m20_hole, (bx, by, P.hitch_bar_z[0] - 1), (bx, by, P.hitch_bar_z[1] + 1))


def hitch_leg():
    w = P.hitch_tube / 2.0
    return tube_span((-w, w), P.hitch_leg_y, (P.hitch_bar_z[1], P.hitch_plate[2][0]), P.hitch_tube_t, "z")


def hitch_bar():
    w = P.hitch_tube / 2.0
    bar = tube_span((-w, w), P.hitch_bar_y, P.hitch_bar_z, P.hitch_tube_t, "y")
    return bar.cut(_stud_hole())


def hitch_gusset():
    t, y0, y1, ztop = P.hitch_gusset
    z0 = P.hitch_bar_z[1]
    pts = [V(-t / 2.0, y0, z0), V(-t / 2.0, y0, ztop), V(-t / 2.0, y1, z0), V(-t / 2.0, y0, z0)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0))


def tow_ball():
    bx, by = P.ball
    z0 = P.hitch_bar_z[1]
    fd, ft = P.ball_flange
    nd, nh = P.ball_neck
    parts = [cyl(fd, (bx, by, z0), (bx, by, z0 + ft)),
             cyl(nd, (bx, by, z0 + ft - 1.0), (bx, by, P.ball_z)),
             Part.makeSphere(P.ball_d / 2.0, V(bx, by, P.ball_z))]
    return fuse_all(parts)


def ball_stud():
    bx, by = P.ball
    d, length = P.ball_stud
    z1 = P.hitch_bar_z[1]
    zb = P.hitch_bar_z[0]
    return Part.makeCompound([cyl(d, (bx, by, z1 - length), (bx, by, z1)),
                              cyl(30.0 * 1.1, (bx, by, zb - 16.0), (bx, by, zb))])


# ---------------------------------------------------------------------
# Coupling head (moves with the trailer, rotates about the ball centre)
# ---------------------------------------------------------------------
def coupling_head():
    bx, by = P.ball
    y0, y1 = P.coupling_y
    z0, z1 = P.coupling_z
    w = P.coupling_w / 2.0
    ys = y0 + P.coupling_socket
    block = box_span((-w, w), (ys, by), (z0, z1))
    nose = cyl(P.coupling_nose_d, (bx, by, z0), (bx, by, z1))
    body = fuse_all([block, nose])
    body = body.cut(Part.makeSphere(P.ball_d / 2.0 + 0.5, V(bx, by, P.ball_z)))
    body = body.cut(cyl(P.ball_neck[0] + 12.0, (bx, by, z0 - 1.0), (bx, by, P.ball_z)))     # room to pitch +-10 deg
    d = P.drawbar[0] / 2.0
    sleeve = box_span((-d - 4.0, d + 4.0), (y0, ys), (z0 - 4.0, z1 + 4.0)).cut(
        box_span((-d - 0.5, d + 0.5), (y0 - 1.0, ys + 1.0), (z0 - 0.5, z1 + 0.5)))
    hw, hl = P.coupling_handle
    handle = box_span((-hw / 2.0, hw / 2.0), (by - hl + 30.0, by + 30.0), (z1, z1 + 14.0))
    return Part.makeCompound([body, sleeve, handle])


# ---------------------------------------------------------------------
# Roll (rotates about the axle)
# ---------------------------------------------------------------------
_RING = None


def ring_shape():
    """One ring at x 0..50, axis = x axis through the origin."""
    global _RING
    if _RING is None:
        pts = [V(x, 0.0, r) for (x, r) in P.ring_profile()]
        face = Part.Face(Part.makePolygon(pts + [pts[0]]))
        _RING = face.revolve(V(0, 0, 0), V(1, 0, 0), 360.0)
    return _RING


def rings(axle_y=P.roll_axle_y):
    out = []
    for i in range(P.ring_n):
        s = ring_shape().copy()
        s.translate(V(P.roll_x[0] + i * P.ring_w, axle_y, P.axle_z))
        out.append(s)
    return Part.makeCompound(out)


def shaft(axle_y=P.roll_axle_y):
    return cyl(P.shaft_d, (-P.shaft_x, axle_y, P.axle_z), (P.shaft_x, axle_y, P.axle_z))


def collars(axle_y=P.roll_axle_y):
    od, w = P.collar
    out = []
    for s in (-1, 1):
        x0 = s * (P.roll_x[1] + 1.0)
        c = cyl(od, (x0, axle_y, P.axle_z), (x0 + s * w, axle_y, P.axle_z))
        out.append(c.cut(shaft(axle_y)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Frame (side plates, bearings, arms, cross beam, drawbar)
# ---------------------------------------------------------------------
def side_plates(axle_y=P.roll_axle_y):
    out = []
    dy = P.side_plate_dy
    z0, z1 = P.side_plate_z
    for s in (-1, 1):
        x = (s * P.side_plate_x[0], s * P.side_plate_x[1])
        x = (min(x), max(x))
        pts = [V(x[0], axle_y - dy, z1), V(x[0], axle_y - dy, z0 + 40.0), V(x[0], axle_y - dy + 40.0, z0),
               V(x[0], axle_y + dy - 40.0, z0), V(x[0], axle_y + dy, z0 + 40.0), V(x[0], axle_y + dy, z1)]
        plate = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(x[1] - x[0], 0, 0))
        plate = plate.cut(cyl(P.shaft_d + 5.0, (x[0] - 1, axle_y, P.axle_z), (x[1] + 1, axle_y, P.axle_z)))
        for dz in (-P.bearing_bolts / 2.0, P.bearing_bolts / 2.0):
            plate = plate.cut(cyl(13.0, (x[0] - 1, axle_y, P.axle_z + dz), (x[1] + 1, axle_y, P.axle_z + dz)))
        out.append(plate)
    return Part.makeCompound(out)


def bearings(axle_y=P.roll_axle_y):
    out = []
    lz, wy, t = P.bearing_flange
    bd, bl = P.bearing_boss
    for s in (-1, 1):
        x0 = P.side_plate_x[1] if s > 0 else -P.side_plate_x[1] - t
        flange = stadium_x(lz, wy, t, x0, axle_y, P.axle_z)
        xo = s * (P.side_plate_x[1] + t)
        boss = cyl(bd, (xo - s * 1.0, axle_y, P.axle_z), (xo + s * bl, axle_y, P.axle_z))
        body = fuse_all([flange, boss])
        body = body.cut(cyl(P.shaft_d, (s * P.side_plate_x[0], axle_y, P.axle_z), (s * (P.shaft_x + 5), axle_y,
                                                                                     P.axle_z)))
        for dz in (-P.bearing_bolts / 2.0, P.bearing_bolts / 2.0):
            body = body.cut(cyl(13.0, (s * 500.0, axle_y, P.axle_z + dz), (s * 600.0, axle_y, P.axle_z + dz)))
        out.append(body)
    return Part.makeCompound(out)


def bearing_bolts(axle_y=P.roll_axle_y):
    out = []
    for s in (-1, 1):
        for dz in (-P.bearing_bolts / 2.0, P.bearing_bolts / 2.0):
            out.append(bolt_x(12.0, s * (P.side_plate_x[1] + P.bearing_flange[2]), s * P.side_plate_x[0],
                              axle_y, P.axle_z + dz, head=19.0, k=7.5, m=10.0))
    return Part.makeCompound(out)


def arms(axle_y=P.roll_axle_y, cross_y=P.cross_y):
    out = []
    for s in (-1, 1):
        x = sorted((s * P.arm_x[0], s * P.arm_x[1]))
        out.append(tube_span(x, (axle_y - P.side_plate_dy, cross_y), P.arm_z, P.rhs_t, "y"))
    return Part.makeCompound(out)


def cross_beam(cross_y=P.cross_y):
    return tube_span((-P.arm_x[1], P.arm_x[1]), (cross_y, cross_y + P.cross_w), P.arm_z, P.rhs_t, "x")


def _drawbar_box(cross_y):
    d = P.drawbar[0] / 2.0
    return (-d, d), (cross_y + P.cross_w, P.DRAWBAR_FRONT_Y), P.drawbar_z


def drawbar(cross_y=P.cross_y):
    x, y, z = _drawbar_box(cross_y)
    return tube_span(x, y, z, P.drawbar[1], "y")


def braces(cross_y=P.cross_y):
    w, t = P.brace
    y_front = cross_y + P.cross_w
    zc_cross = sum(P.arm_z) / 2.0
    zc_bar = sum(P.drawbar_z) / 2.0
    x, y, z = _drawbar_box(cross_y)
    trim = box_span(x, (y[0] - 50.0, y[1]), (z[0] - 50, z[1] + 50)).fuse(
        box_span((-P.arm_x[1] - 50, P.arm_x[1] + 50), (cross_y - 50.0, y_front), (0.0, 600.0)))
    out = []
    for s in (-1, 1):
        p0 = (s * (P.arm_x[1] - 60.0), y_front - 30.0, zc_cross)
        p1 = (s * 10.0, y_front + P.brace_y + 30.0, zc_bar)
        out.append(rect_tube(p0, p1, w, w, t).cut(trim))
    return Part.makeCompound(out)


def _park_pin(cross_y):
    """Pin of the parking leg: through a lug on the right side of the drawbar, above the braces."""
    return (P.drawbar[0] / 2.0, P.DRAWBAR_FRONT_Y - P.park_leg_y, P.drawbar_z[1] + P.park_leg[0] / 2.0 + 2.0)


def park_lug(cross_y=P.cross_y):
    px, py, pz = _park_pin(cross_y)
    lug = box_span((px, px + 8.0), (py - 25.0, py + 25.0), (P.drawbar_z[1] - 9.0, pz + 22.0))
    return lug.cut(cyl(13.0, (px - 1, py, pz), (px + 9, py, pz)))


def park_leg(cross_y=P.cross_y):
    """Stowed: swung up along the right side of the drawbar (above the braces), foot to the front."""
    w, t, length = P.park_leg
    px, py, pz = _park_pin(cross_y)
    x = (px + 10.0, px + 10.0 + w)
    leg = tube_span(x, (py - 25.0, py - 25.0 + length), (pz - w / 2.0, pz + w / 2.0), t, "y")
    foot = box_span((x[0], x[1] + 10.0), (py - 25.0 + length, py - 25.0 + length + 6.0), (pz - 30.0, pz + 40.0))
    leg = fuse_all([leg, foot])
    return leg.cut(cyl(13.0, (x[0] - 1, py, pz), (x[1] + 1, py, pz)))


def park_pin(cross_y=P.cross_y):
    px, py, pz = _park_pin(cross_y)
    x1 = px + 10.0 + P.park_leg[0]
    return Part.makeCompound([cyl(12.0, (px + 1.0, py, pz), (x1 + 3.0, py, pz)),
                              cyl(22.0, (x1 + 3.0, py, pz), (x1 + 8.0, py, pz))])
