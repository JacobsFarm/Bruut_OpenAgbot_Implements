"""Parts of the sawdust spreader. Every function returns a Part shape in robot coordinates. The auger and the disc
turn in place; nothing changes position.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import sds_params as P



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


AY, AZ = P.trough_y, P.auger_z


# ---------------------------------------------------------------------
# Mount
# ---------------------------------------------------------------------
def bearers():
    out = []
    for yc in P.bearer_y:
        t = tube_span((-P.bearer_x, P.bearer_x), (yc - P.bearer / 2.0, yc + P.bearer / 2.0), P.bearer_z, 3.0, "x")
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                t = t.cut(cyl(P.m10_hole, (sx * xb, yc, 600), (sx * xb, yc, 800)))
        out.append(t)
    return Part.makeCompound(out)


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * xb, yc, P.robot_upper_beam_z[0], P.bearer_z[1])
                              for yc in P.bearer_y for sx in (-1, 1) for xb in P.robot_upper_beam_x])


def _slope_z(y):
    """z of the inside of the sloping wall above y (front or rear)."""
    pts = P.bin_section()
    (yr, zr), (yf, zf), (yft, zft) = pts[0], pts[1], pts[2]
    if y >= yf:
        return zf + (y - yf) * (zft - zf) / (yft - yf)
    return zr + (yr - y) * (zft - zf) / (yft - yf)


def legs():
    """Angle 40 x 4 from each bearer up to the slope above it, at x +-(bin_x - 30)."""
    a, t = P.leg
    out = []
    for yc in P.bearer_y:
        z1 = _slope_z(yc) - P.wall_t
        for sx in (-1, 1):
            x0 = sx * (P.bin_x - 30.0)
            out.append(box_span((x0 - a / 2, x0 + a / 2), (yc - a / 2, yc + a / 2), (P.bearer_z[1], z1)).cut(
                box_span((x0 - a / 2 + t, x0 + a / 2 + 1), (yc - a / 2 + t, yc + a / 2 + 1), (P.bearer_z[1] - 1, z1 + 1))))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Bin
# ---------------------------------------------------------------------
def _slab(p0, p1, t, x):
    """Plate t thick between the points p0, p1 (y, z), on the outside of the line (away from the bin centre)."""
    d = V(0, p1[0] - p0[0], p1[1] - p0[1])
    d.normalize()
    n = V(0, d.z, -d.y)                         # normal to one side
    mid = V(0, (p0[0] + p1[0]) / 2.0 - AY, (p0[1] + p1[1]) / 2.0 - (AZ + 200.0))
    if n.dot(mid) < 0:
        n = n * -1.0
    pts = [p0, p1, (p1[0] + n.y * t, p1[1] + n.z * t), (p0[0] + n.y * t, p0[1] + n.z * t)]
    return plate_yz(pts, -x, 2 * x)


def bin_walls():
    """Front and rear walls (slope + vertical part), trough, 2 mm."""
    pts = P.bin_section()
    t = P.wall_t
    x = P.bin_x
    (yr, zr), (yf, zf), (yft, zft), _, _, (yrt, zrt) = pts
    out = [_slab((yf, zf), (yft, zft), t, x), _slab((yft, zft), (yft, P.bin_top), t, x),
           _slab((yr, zr), (P.bin_rear_y, zrt), t, x), _slab((P.bin_rear_y, zrt), (P.bin_rear_y, P.bin_top), t, x)]
    ring = cyl_x(2 * (P.trough_r + t), -x, x, AY, AZ).cut(cyl_x(2 * P.trough_r, -x - 1, x + 1, AY, AZ))
    out.append(ring.common(box_span((-x - 1, x + 1), (AY - 200.0, AY + 200.0), (AZ - 200.0, zf + 0.5))))
    return Part.makeCompound(out)


def side_walls():
    """Side walls 2 mm with the outline of the bin and the trough; auger hole on the right, shaft hole on the left."""
    pts = P.bin_section()
    t = P.wall_t
    out = []
    for sx in (-1, 1):
        x0 = P.bin_x if sx > 0 else -P.bin_x - t
        w = plate_yz(pts, x0, t).fuse(cyl_x(2 * (P.trough_r + t), x0, x0 + t, AY, AZ)).removeSplitter()
        hole = P.auger_d + 4.0 if sx > 0 else P.auger_shaft + 2.0
        out.append(w.cut(cyl_x(hole, x0 - 1, x0 + t + 1, AY, AZ)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Auger and drive
# ---------------------------------------------------------------------
def auger_shaft():
    return cyl_x(P.auger_shaft, -(P.bin_x + P.wall_t + P.gm_box[0] - 10.0), P.housing_x[0] + 25.0, AY, AZ)


def auger_flight():
    """Helical flight between r 15 and r 75 (a ruled surface; its mass is set in MASS_FIXED)."""
    x0, x1 = -P.bin_x + 5.0, P.housing_x[0] - 3.0
    L = x1 - x0
    hi = Part.makeHelix(P.auger_pitch, L, P.auger_shaft / 2.0)
    ho = Part.makeHelix(P.auger_pitch, L, P.auger_d / 2.0)
    f = Part.makeRuledSurface(hi, ho)
    f.rotate(V(0, 0, 0), V(0, 1, 0), 90.0)
    f.translate(V(x0, AY, AZ))
    return f


def outlet_tube():
    d, t = P.outlet_tube
    return cyl_x(d, P.bin_x + P.wall_t, P.housing_x[0], AY, AZ).cut(cyl_x(d - 2 * t, P.bin_x, P.housing_x[0] + 1, AY, AZ))


def gearmotor():
    bx, by, bz = P.gm_box
    x1 = -(P.bin_x + P.wall_t)
    box = box_span((x1 - bx, x1), (AY - by / 2, AY + by / 2), (AZ - bz / 2, AZ + bz / 2))
    box = box.cut(cyl_x(P.auger_shaft, x1 - bx + 9, x1 + 1, AY, AZ))
    d, L = P.gm_motor
    motor = cyl((d), (x1 - bx / 2, AY, AZ + bz / 2), (x1 - bx / 2, AY, AZ + bz / 2 + L))
    return box, motor


# ---------------------------------------------------------------------
# Spinner housing, disc, motor
# ---------------------------------------------------------------------
def housing():
    """Box 2 mm open at the bottom and with the throw opening in the right wall (lower 150 mm)."""
    x, y, z = P.housing_x, P.housing_y, P.housing_z
    t = P.wall_t
    outer = box_span(x, y, z)
    inner = box_span((x[0] + t, x[1] - t), (y[0] + t, y[1] - t), (z[0] - 1, z[1] - t))
    s = outer.cut(inner)
    s = s.cut(box_span((x[1] - t - 1, x[1] + 1), (y[0] + 20.0, y[1] - 20.0), (z[0] - 1, z[0] + 150.0)))
    s = s.cut(cyl_x(P.outlet_tube[0] - 2 * P.outlet_tube[1], x[0] - 1, x[0] + t + 1, AY, AZ))
    return s.cut(cyl(20.0, (P.spinner_x, AY, z[1] - t - 1), (P.spinner_x, AY, z[1] + 1)))


def disc():
    r = P.disc_d / 2.0
    d = cyl(P.disc_d, (P.spinner_x, AY, P.disc_z), (P.spinner_x, AY, P.disc_z + 4.0))
    out = [d, cyl(20.0, (P.spinner_x, AY, P.disc_z), (P.spinner_x, AY, P.housing_z[1] - 2.0))]
    for k in range(4):
        v = box_span((30.0, r - 5.0), (-2.0, 2.0), (P.disc_z + 4.0, P.disc_z + 4.0 + P.vane_h))
        v.rotate(V(0, 0, 0), V(0, 0, 1), 45.0 + 90.0 * k)
        v.translate(V(P.spinner_x, AY, 0))
        out.append(v)
    return Part.makeCompound(out)


def spinner_motor():
    d, L = P.spinner_motor
    z0 = P.housing_z[1]
    return cyl(d, (P.spinner_x, AY, z0), (P.spinner_x, AY, z0 + L))


def bearing_housing():
    """Flange bearing for the auger shaft end on the left wall of the housing (inside)."""
    x0 = P.housing_x[0] + P.wall_t
    return box_span((x0, x0 + 12.0), (AY - 40.0, AY + 40.0), (AZ - 40.0, AZ + 40.0)).cut(
        cyl_x(P.auger_shaft, x0 - 1, x0 + 13, AY, AZ)).fuse(
        cyl_x(60.0, x0 + 12.0, x0 + 20.0, AY, AZ).cut(cyl_x(P.auger_shaft, x0, x0 + 21, AY, AZ)))
