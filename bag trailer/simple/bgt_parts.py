"""Parts of the bag trailer (frame, axle, wheels, deck, boards, bags). Every function returns a Part shape in robot
coordinates with the trailer straight behind the robot. Hitch and drawbar parts come from cbr_parts.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bgt_params as P



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


AZ = P.wheel_d / 2.0


def frame():
    """2 side rails 40 x 40 x 3 (as the roll frame arms), cross members 40 x 40 x 3, axle hangers 8 mm."""
    parts = []
    x0, x1 = P.frame_x
    for sx in (-1, 1):
        x = sorted((sx * x0, sx * x1))
        parts.append(tube_span(x, P.rail_y, P.frame_z, P.rhs_t, "y"))
        parts.append(box_span(x, (P.rail_y[0], P.rail_y[0] + 3.0), P.frame_z))
        xh = sorted((sx * (x0 + 20.0 - P.hanger_t / 2), sx * (x0 + 20.0 + P.hanger_t / 2)))
        parts.append(box_span(xh, (P.axle_y - 50.0, P.axle_y + 50.0), (AZ + P.axle_tube / 2 - 5.0, P.frame_z[0])))
    for yc in P.cross_members_y:
        parts.append(tube_span((-x0, x0), (yc - 20.0, yc + 20.0), P.frame_z, P.rhs_t, "x"))
    return fuse_all(parts)


def axle():
    """Square tube 50 x 50 x 4 across, stub spindles O30 to the wheel hubs."""
    a = P.axle_tube / 2
    tube = tube_span((-P.wheel_x + P.wheel_w / 2 + 10.0, P.wheel_x - P.wheel_w / 2 - 10.0), (P.axle_y - a, P.axle_y + a),
                     (AZ - a, AZ + a), 4.0, "x")
    spindles = [cyl_x(30.0, sx * (P.wheel_x - P.wheel_w / 2 - 12.0), sx * (P.wheel_x + P.wheel_w / 2 + 15.0), P.axle_y, AZ)
                for sx in (-1, 1)]
    return Part.makeCompound([tube] + spindles)


def wheels():
    """4.00-8 wheels: tyre O400 x 100 on a rim O200."""
    x0, x1 = P.wheel_x - P.wheel_w / 2, P.wheel_x + P.wheel_w / 2
    tyre = cyl_x(P.wheel_d, x0, x1, P.axle_y, AZ).cut(cyl_x(205.0, x0 - 1, x1 + 1, P.axle_y, AZ))
    return both(tyre)


def rims():
    x0, x1 = P.wheel_x - P.wheel_w / 2 + 10.0, P.wheel_x + P.wheel_w / 2 - 10.0
    rim = cyl_x(205.0, x0, x1, P.axle_y, AZ).cut(cyl_x(190.0, x0 - 1, x1 + 1, P.axle_y, AZ))
    disc = cyl_x(195.0, P.wheel_x - 3.0, P.wheel_x + 3.0, P.axle_y, AZ)
    hub = cyl_x(70.0, P.wheel_x - P.wheel_w / 2 - 2.0, P.wheel_x + P.wheel_w / 2 + 2.0, P.axle_y, AZ)
    return both(rim.fuse(disc).fuse(hub).removeSplitter().cut(cyl_x(30.5, 0, 2000, P.axle_y, AZ)))


def mudguards():
    """Half-round guard 2 mm, 50 over the tyre, on a stay from the side rail."""
    w, t = P.mudguard
    r = P.wheel_d / 2 + 50.0
    x0 = P.wheel_x - w / 2
    ring = cyl_x(2 * (r + t), x0, x0 + w, P.axle_y, AZ).cut(cyl_x(2 * r, x0 - 1, x0 + w + 1, P.axle_y, AZ))
    guard = ring.common(box_span((x0 - 1, x0 + w + 1), (P.axle_y - r - 10, P.axle_y + r + 10), (AZ + 60.0, AZ + r + 10)))
    stay = box_span((P.frame_x[1], x0 + 5.0), (P.axle_y - 20.0, P.axle_y + 20.0), (P.frame_z[0], P.frame_z[0] + 6.0))
    up = box_span((x0, x0 + 6.0), (P.axle_y - 20.0, P.axle_y + 20.0), (P.frame_z[0], AZ + r + 1.0))
    return both(guard.fuse(stay).fuse(up).removeSplitter())


def deck():
    return box_span((-P.deck_x, P.deck_x), P.deck_y, (P.frame_z[1], P.deck_z))


def boards():
    """Side and front boards (plywood 18), drop tailgate at the rear (closed)."""
    t = P.ply_t
    z = (P.deck_z, P.deck_z + P.board_h)
    y0, y1 = P.deck_y
    out = []
    for sx in (-1, 1):
        out.append(box_span(sorted((sx * P.deck_x, sx * (P.deck_x - t))), (y0 + t, y1), z))
    out.append(box_span((-P.deck_x + t, P.deck_x - t), (y1 - t, y1), z))
    return Part.makeCompound(out)


def tailgate():
    t = P.ply_t
    y0 = P.deck_y[0]
    return box_span((-P.deck_x, P.deck_x), (y0, y0 + t), (P.deck_z, P.deck_z + P.board_h))


def bags():
    bx, by, bz = P.bag
    return Part.makeCompound([box_span((x, x + bx), (y, y + by), (z, z + bz - 2.0)) for x, y, z in P.bag_positions()])
