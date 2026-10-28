"""Parts of the biological-control spreader. Every function returns a Part shape in robot coordinates. Nothing moves.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bcs_params as P



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


BZ = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + P.bearer)
X, Y = P.row_x, P.hopper_y
CONE_Z0 = P.hopper_z0 - P.cone_h
METER_Z = (CONE_Z0 - 10.0 - P.meter_box[2], CONE_Z0 - 10.0)
VEN_Z = (METER_Z[0] - P.venturi[1], METER_Z[0])
MAN_Z = (VEN_Z[0] + VEN_Z[1]) / 2.0


def bearer():
    y = (P.bearer_y - P.bearer / 2, P.bearer_y + P.bearer / 2)
    t = tube_span((-P.bearer_x, P.bearer_x), y, BZ, 3.0, "x")
    for sx in (-1, 1):
        for xb in P.robot_upper_beam_x:
            t = t.cut(cyl(P.m10_hole, (sx * xb, P.bearer_y, 600), (sx * xb, P.bearer_y, 800)))
    return t


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * xb, P.bearer_y, P.robot_upper_beam_z[0], BZ[1])
                              for sx in (-1, 1) for xb in P.robot_upper_beam_x])


def arms_and_rings():
    """Per hopper: 2 flat bars 30 x 6 from the bearer top forward to a ring 6 mm round the hopper."""
    w, t = P.arm
    r = P.hopper_d / 2.0
    out = []
    zr = P.hopper_z0 + 30.0
    ring = cyl(P.hopper_d + 12.0, (X, Y, zr), (X, Y, zr + 25.0)).cut(cyl(P.hopper_d, (X, Y, zr - 1), (X, Y, zr + 26.0)))
    out.append(ring)
    for dx in (-60.0, 60.0):
        x = X + dx
        y0 = P.bearer_y - P.bearer / 2
        y1 = Y - math.sqrt(max(r ** 2 - dx ** 2, 0.0)) - 4.0
        out.append(box_span((x - t / 2, x + t / 2), (y0, y1), (BZ[1], BZ[1] + w)))
        out.append(box_span((x - t / 2, x + t / 2), (y1 - t, y1), (BZ[1], zr + 25.0)))
    return both(Part.makeCompound(out))


def hoppers():
    r = P.hopper_d / 2.0
    w = P.hopper_wall
    cyl_o = cyl(P.hopper_d, (X, Y, P.hopper_z0), (X, Y, P.hopper_z0 + P.hopper_h))
    cyl_i = cyl(P.hopper_d - 2 * w, (X, Y, P.hopper_z0), (X, Y, P.hopper_z0 + P.hopper_h + 1))
    cone_o = Part.makeCone(20.0, r, P.cone_h, V(X, Y, CONE_Z0))
    cone_i = Part.makeCone(20.0 - w, r - w, P.cone_h + 0.1, V(X, Y, CONE_Z0))
    lid = cyl(P.hopper_d + 6.0, (X, Y, P.hopper_z0 + P.hopper_h), (X, Y, P.hopper_z0 + P.hopper_h + 6.0))
    s = cyl_o.cut(cyl_i).fuse(cone_o.cut(cone_i)).fuse(lid).removeSplitter()
    spout = cyl(40.0, (X, Y, CONE_Z0 - 10.0), (X, Y, CONE_Z0)).cut(cyl(34.0, (X, Y, CONE_Z0 - 11.0), (X, Y, CONE_Z0 + 1)))
    return both(s.fuse(spout))


def agitator_motors():
    d, L = P.agitator_motor
    z0 = P.hopper_z0 + P.hopper_h + 6.0
    shaft = cyl(8.0, (X, Y, CONE_Z0 + 20.0), (X, Y, z0))
    return both(Part.makeCompound([cyl(d, (X, Y, z0), (X, Y, z0 + L)), shaft]))


def meters():
    w, d, h = P.meter_box
    box = box_span((X - w / 2, X + w / 2), (Y - d / 2, Y + d / 2), METER_Z)
    stepper = box_span((X + w / 2, X + w / 2 + 42.0), (Y - 21.0, Y + 21.0), (METER_Z[0] + 14.0, METER_Z[1] - 14.0))
    return both(box.fuse(stepper))


def venturis():
    d, L = P.venturi
    v = cyl(d, (X, Y, VEN_Z[0]), (X, Y, VEN_Z[1]))
    return both(v)


def fan():
    """Centrifugal fan O200 x 90 standing on the bearer, outlet to the manifold, motor behind."""
    z0 = BZ[1] + 5.0
    zc = z0 + P.fan_d / 2.0
    housing = cyl((P.fan_d), (0, P.bearer_y - P.fan_w / 2, zc), (0, P.bearer_y + P.fan_w / 2, zc))
    foot = box_span((-60.0, 60.0), (P.bearer_y - 20.0, P.bearer_y + 20.0), (BZ[1], z0 + 10.0))
    motor = cyl(70.0, (0, P.bearer_y - P.fan_w / 2 - 80.0, zc), (0, P.bearer_y - P.fan_w / 2, zc))
    return housing.fuse(foot).removeSplitter(), motor


def manifold():
    """Air pipe O40 from the fan outlet (x 0) to the 2 venturis: up/forward from the fan, across at venturi height."""
    zc = BZ[1] + 5.0 + P.fan_d / 2.0
    out = [cyl(P.manifold_d, (0, P.bearer_y + P.fan_w / 2, zc), (0, Y, zc)),
           cyl(P.manifold_d, (0, Y, zc), (0, Y, MAN_Z)),
           Part.makeSphere(P.manifold_d / 2.0, V(0, Y, zc)),
           cyl(P.manifold_d, (-X + P.venturi[0] / 2, Y, MAN_Z), (X - P.venturi[0] / 2, Y, MAN_Z)),
           Part.makeSphere(P.manifold_d / 2.0, V(0, Y, MAN_Z))]
    return Part.makeCompound(out)


def hoses():
    h = cyl(P.hose_d, (X, Y, P.nozzle_z + 30.0), (X, Y, VEN_Z[0]))
    return both(h)


def nozzles():
    z = P.nozzle_z
    body = cyl(P.hose_d + 8.0, (X, Y, z + 30.0), (X, Y, z + 60.0))
    defl = Part.makeCone(P.deflector_d / 2.0, 6.0, 40.0, V(X, Y, z - 10.0))
    stay = [cyl(4.0, (X + dx, Y, z + 15.0), (X + dx, Y, z + 30.0)) for dx in (-20.0, 20.0)]
    return both(Part.makeCompound([body, defl] + stay))


def controller():
    """Driver box (2 steppers, agitators, fan) hanging under the bearer between the upper beams."""
    return box_span((-100.0, 100.0), (P.bearer_y - 50.0, P.bearer_y + 50.0), (BZ[0] - 85.0, BZ[0]))
