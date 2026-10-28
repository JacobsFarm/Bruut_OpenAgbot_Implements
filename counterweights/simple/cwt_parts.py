"""Parts of the counterweights. Every function returns a Part shape in robot coordinates; end = "front" or "rear",
sx = -1 (left) or 1 (right). Nothing moves."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cwt_params as P


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
    return sorted((sx * a, sx * b))


def base(end, sx):
    """Base plate 15 mm on the two lower beams, 4 x M10 holes, O32 holes over the hanger bolt nuts, 2 studs M16
    welded in."""
    z0 = P.robot_lower_beam_z[1]
    s = box_span(_xs(sx, *P.stack_x), P.end_span(P.stack_y, end), (z0, z0 + P.base_t))
    for yb in P.robot_beam_y:
        y = P.end_y(yb, end)
        for xb in P.base_bolt_x:
            s = s.cut(cyl(P.m10_hole, (sx * xb, y, z0 - 1), (sx * xb, y, z0 + P.base_t + 1)))
        for xb in P.hanger_bolt_x:
            s = s.cut(cyl(32.0, (sx * xb, y, z0 - 1), (sx * xb, y, z0 + P.base_t + 1)))
    for ys in P.stud_y:
        s = s.fuse(cyl(P.stud_d, (sx * P.stud_x, P.end_y(ys, end), z0 + P.base_t - 1.0),
                       (sx * P.stud_x, P.end_y(ys, end), z0 + P.base_t + P.stud_len)))
    return s.removeSplitter()


def base_bolts(end, sx):
    """Countersunk M10 from the top (flush with the base plate, the plates lie on it), nut under the beam."""
    z0, z1 = P.robot_lower_beam_z[0], P.robot_lower_beam_z[1] + P.base_t
    out = []
    for yb in P.robot_beam_y:
        for xb in P.base_bolt_x:
            x, y = sx * xb, P.end_y(yb, end)
            out += [cyl(10.0, (x, y, z0 - 11.5), (x, y, z1)), cyl(18.5, (x, y, z0 - 8.4), (x, y, z0))]
    return Part.makeCompound(out)


def plate(end, sx, k):
    """Ballast plate k (0 = lowest): open slots from the outer edge to the studs, a hand grip between them."""
    px, py, pz = P.plate
    z0 = P.robot_lower_beam_z[1] + P.base_t + k * pz
    y0, y1 = P.end_span(P.stack_y, end)
    yc = (y0 + y1) / 2.0
    s = box_span(_xs(sx, P.plate_x0, P.plate_x0 + px), (yc - py / 2.0, yc + py / 2.0), (z0 + 0.5, z0 + pz))
    xo = P.plate_x0 + px
    for ys in P.stud_y:
        y = P.end_y(ys, end)
        w = P.slot_w / 2.0
        s = s.cut(box_span(_xs(sx, P.stud_x, xo + 1.0), (y - w, y + w), (z0 - 1, z0 + pz + 1)))
        s = s.cut(cyl(P.slot_w, (sx * P.stud_x, y, z0 - 1), (sx * P.stud_x, y, z0 + pz + 1)))
    gx, gy = P.grip
    s = s.cut(box_span(_xs(sx, xo - 15.0 - gx, xo - 15.0), (yc - gy / 2.0, yc + gy / 2.0), (z0 - 1, z0 + pz + 1)))
    return s


def clamp(end, sx, n):
    """Flat bar over both studs on top of the stack, with 2 knobs (through nut: the stud stands out above a low stack)."""
    w, t = P.clamp
    z0 = P.robot_lower_beam_z[1] + P.base_t + n * P.plate[2]
    y0, y1 = P.end_y(P.stud_y[0], end), P.end_y(P.stud_y[1], end)
    ys = sorted((y0, y1))
    bar = box_span(_xs(sx, P.stud_x - w / 2.0, P.stud_x + w / 2.0), (ys[0] - 25.0, ys[1] + 25.0), (z0 + 0.5, z0 + t))
    for y in (y0, y1):
        bar = bar.cut(cyl(P.stud_d + 1.0, (sx * P.stud_x, y, z0 - 1), (sx * P.stud_x, y, z0 + t + 1)))
    knobs = []
    for y in (y0, y1):
        k = cyl(P.knob_d, (sx * P.stud_x, y, z0 + t), (sx * P.stud_x, y, z0 + t + P.knob_h * 0.4))
        k = k.fuse(cyl(28.0, (sx * P.stud_x, y, z0 + t + P.knob_h * 0.4), (sx * P.stud_x, y, z0 + t + P.knob_h)))
        knobs.append(k.cut(cyl(P.stud_d, (sx * P.stud_x, y, z0 + t - 1), (sx * P.stud_x, y, z0 + t + P.knob_h + 1))))
    return bar, Part.makeCompound(knobs)
