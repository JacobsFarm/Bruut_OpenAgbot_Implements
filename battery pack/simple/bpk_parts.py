"""Parts of the battery pack. Every function returns a Part shape in robot coordinates; sx = -1 (left) or 1 (right).
Nothing moves."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bpk_params as P


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




def _xs(sx, a, b):
    return tuple(sorted((sx * a, sx * b)))


def hangers(sx):
    """2 hangers per side: flat bar 40 x 8 under 2 spacer blocks 40 x 40 under the upper beams."""
    zb = P.robot_upper_beam_z[0]
    w, t = P.hanger
    out = []
    for yc in P.hanger_y:
        y = (yc - w / 2.0, yc + w / 2.0)
        bar = box_span(_xs(sx, *P.hanger_x), y, (zb - P.hanger_drop - t, zb - P.hanger_drop))
        for xb in P.robot_upper_beam_x:
            bar = bar.fuse(box_span(_xs(sx, xb - 20.0, xb + 20.0), y, (zb - P.hanger_drop, zb)))
        bar = bar.removeSplitter()
        for xb in P.robot_upper_beam_x:
            bar = bar.cut(cyl(P.m10_hole, (sx * xb, yc, zb - 100), (sx * xb, yc, zb + 1)))
        out.append(bar)
    return Part.makeCompound(out)


def hanger_bolts(sx):
    zb = P.robot_upper_beam_z[0]
    return Part.makeCompound([bolt_z(10.0, sx * xb, yc, zb - P.hanger_drop - P.hanger[1], P.robot_upper_beam_z[1])
                              for yc in P.hanger_y for xb in P.robot_upper_beam_x])


def pod_box(sx):
    """Aluminium box 3 mm (closed, the lid bolted on), drawn as one shell."""
    xs = P.pod_xs(sx)
    t = P.pod_wall
    outer = box_span(xs, P.pod_y, P.pod_z)
    inner = box_span((xs[0] + t, xs[1] - t), (P.pod_y[0] + t, P.pod_y[1] - t), (P.pod_z[0] + t, P.pod_z[1] - t))
    return outer.cut(inner)


def hooks(sx):
    """2 hook strips on the lid: up beside the hanger bar, a lip over it."""
    w, t, h = P.hook
    zt = P.pod_z[1]
    zbar = P.robot_upper_beam_z[0] - P.hanger_drop
    xc = sx * sum(P.pod_x) / 2.0
    out = []
    for yc in P.hanger_y:
        s = 1.0 if yc > 0 else -1.0
        yo = yc + s * (P.hanger[0] / 2.0 + 2.0)                 # vertical strip just outside the bar
        up = box_span((xc - 15.0, xc + 15.0), tuple(sorted((yo, yo + s * t))), (zt, zbar + 2.0 + t))
        lip = box_span((xc - 15.0, xc + 15.0), tuple(sorted((yo + s * t, yc - s * P.hanger[0] / 2.0))),
                       (zbar + 2.0, zbar + 2.0 + t))
        out.append(up.fuse(lip).removeSplitter())
    return Part.makeCompound(out)


def cells(sx):
    cx, cy, cz = P.cell
    return Part.makeCompound([box_span((x, x + cx), (y + 0.5, y + cy - 0.5), (z, z + cz))
                              for x, y, z in P.cell_positions(sx)])


def bms(sx):
    xs = P.pod_xs(sx)
    z0 = P.cell_positions(sx)[0][2] + P.cell[2] + 10.0
    return box_span((xs[0] + 20.0, xs[1] - 20.0), (-150.0, 150.0), (z0, z0 + 25.0))


def outer_fittings(sx):
    """2 handles, the Anderson connector housing and 2 over-centre latches on the outer face."""
    xo = sx * P.pod_x[1]
    L, so, d = P.handle
    out = []
    for yc in (-140.0, 140.0):
        z = P.pod_z[1] - 60.0
        out.append(cyl(d, (xo + sx * so, yc - L / 2.0, z), (xo + sx * so, yc + L / 2.0, z)))
        for ye in (yc - L / 2.0, yc + L / 2.0):
            out.append(cyl(d, (xo, ye, z), (xo + sx * (so + d / 2.0), ye, z)))
    cx, cy, cz = P.connector
    out.append(box_span(_xs(sx, P.pod_x[1], P.pod_x[1] + cx / 2.0), (-cy, cy), (420.0, 420.0 + cz)))
    lx, ly, lz = P.latch
    for yc in P.hanger_y:
        out.append(box_span(_xs(sx, P.pod_x[1], P.pod_x[1] + ly), (yc - lx / 2.0, yc + lx / 2.0),
                            (P.pod_z[1] - lz, P.pod_z[1])))
    return Part.makeCompound(out)
