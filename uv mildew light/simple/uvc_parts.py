"""Parts of the UV-C mildew light. Every function returns a Part shape in robot coordinates. Nothing moves.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import uvc_params as P



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


def lamp_ys():
    inner = P.hood_y - P.brush[0] - 25.0
    return [-inner + 2 * inner * i / (P.n_lamps - 1) for i in range(P.n_lamps)]


# ---------------------------------------------------------------------
# Mount
# ---------------------------------------------------------------------
def bearers():
    out = []
    z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + P.bearer)
    for yb in P.bearer_y:
        t = tube_span((-P.bearer_x, P.bearer_x), (yb - P.bearer / 2, yb + P.bearer / 2), z, 3.0, "x")
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                t = t.cut(cyl(P.m10_hole, (sx * xb, yb, 600), (sx * xb, yb, 800)))
        out.append(t)
    return Part.makeCompound(out)


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * xb, yb, P.robot_upper_beam_z[0], P.robot_upper_beam_z[1] + P.bearer)
                              for yb in P.bearer_y for sx in (-1, 1) for xb in P.robot_upper_beam_x])


def hangers():
    """Flat 40 x 6 on the inner face of each bearer (towards the hood centre), with a slot for the hood height."""
    w, t = P.hanger
    out = []
    for yb in P.bearer_y:
        s = 1 if yb < 0 else -1                         # inner face: towards y = 0
        y0 = yb + s * P.bearer / 2.0
        ys = sorted((y0, y0 + s * t))
        for sx in (-1, 1):
            x = sx * P.hanger_x
            h = box_span((x - w / 2, x + w / 2), ys, (P.hood_top, P.robot_upper_beam_z[1] + P.bearer))
            h = h.cut(box_span((x - 5.5, x + 5.5), (ys[0] - 1, ys[1] + 1),
                               (P.robot_upper_beam_z[1] + 8.0 - P.slot / 2, P.robot_upper_beam_z[1] + 32.0)))
            out.append(h)
    return Part.makeCompound(out)


def driver_box():
    w, d, h = P.driver_box
    yb = P.bearer_y[1]
    z0 = P.robot_upper_beam_z[1] + P.bearer
    return box_span((-w / 2, w / 2), (yb - d / 2, yb + d / 2), (z0, z0 + h))


# ---------------------------------------------------------------------
# Hood
# ---------------------------------------------------------------------
def hood():
    """Roof and side walls, aluminium 2 mm, with a 20 mm flange turned in at the bottom of the walls."""
    t = P.sheet
    roof = box_span((-P.hood_x, P.hood_x), (-P.hood_y, P.hood_y), (P.hood_top - t, P.hood_top))
    wall = box_span((P.hood_x - t, P.hood_x), (-P.hood_y, P.hood_y), (P.hood_bottom, P.hood_top - t))
    flange = box_span((P.hood_x - 20.0, P.hood_x - t), (-P.hood_y, P.hood_y), (P.hood_bottom, P.hood_bottom + t))
    w = wall.fuse(flange).removeSplitter()
    return Part.makeCompound([roof, w, mirror_x(w)])


def skirts():
    t, h = P.skirt
    s = box_span((P.hood_x - t, P.hood_x), (-P.hood_y, P.hood_y), (P.hood_bottom - h, P.hood_bottom))
    return both(s)


def brushes():
    """Brush curtains front and rear between the walls (a strip holder and the bristles drawn as a block)."""
    t, h = P.brush
    x = P.hood_x - P.skirt[0]
    out = []
    for s in (-1, 1):
        y = sorted((s * P.hood_y, s * (P.hood_y - t)))
        out.append(box_span((-x, x), y, (P.hood_top - P.sheet - h, P.hood_top - P.sheet)))
    return Part.makeCompound(out)


def lamps():
    """6 compact UV-C tubes (2 legs O19) across the hood, sockets at the right wall."""
    out = []
    x_end = P.hood_x - P.sheet - P.lamp_holder[0]
    for y in lamp_ys():
        for dy in (-P.lamp_leg_gap / 2, P.lamp_leg_gap / 2):
            out.append(cyl_x(P.lamp_tube_d, x_end - P.lamp_len + 20.0, x_end, y + dy, P.lamp_z))
        out.append(Part.makeSphere(P.lamp_tube_d / 2, V(x_end - P.lamp_len + 20.0, y - P.lamp_leg_gap / 2, P.lamp_z)))
        out.append(Part.makeSphere(P.lamp_tube_d / 2, V(x_end - P.lamp_len + 20.0, y + P.lamp_leg_gap / 2, P.lamp_z)))
    return Part.makeCompound(out)


def sockets():
    w, d, h = P.lamp_holder
    x1 = P.hood_x - P.sheet
    return Part.makeCompound([box_span((x1 - w, x1), (y - d / 2, y + d / 2), (P.lamp_z - h / 2, P.lamp_z + h / 2))
                              for y in lamp_ys()])


def lamp_clips():
    """Spring clip at the free end of each lamp, hanging from the roof."""
    x = P.hood_x - P.sheet - P.lamp_holder[0] - P.lamp_len + 60.0
    out = []
    for y in lamp_ys():
        out.append(box_span((x - 8.0, x + 8.0), (y - 3.0, y + 3.0), (P.lamp_z + P.lamp_tube_d / 2, P.hood_top - P.sheet)))
    return Part.makeCompound(out)


def guards():
    """2 stainless wires O3 under each lamp, wall to wall."""
    x = P.hood_x - P.sheet
    out = []
    for y in lamp_ys():
        for dy in (-18.0, 18.0):
            out.append(cyl_x(P.guard_d, -x, x, y + dy, P.lamp_z - P.lamp_tube_d / 2 - 8.0))
    return Part.makeCompound(out)
