"""Parts of the bedding rake (cubicle groomer). Every function returns a Part shape in robot coordinates (the arm
group in the work pose; build_bdr swings it about the pivot).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bdr_params as P



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




def cyl_y(d, y0, y1, x, z):
    return cyl(d, (x, y0, z), (x, y1, z))


PX, PZ = P.pivot
RZ = P.rotor_z()


# ---------------------------------------------------------------------
# Mount (fixed)
# ---------------------------------------------------------------------
def bracket():
    """Plate 8 mm on the outer face of the right outer upper beam, back plate inside, 2 pivot lugs."""
    t, L, h = P.bracket
    x0 = P.robot_outer_beam_x
    plate = box_span((x0, x0 + t), (-L / 2, L / 2), P.bracket_z)
    back = Part.makeCompound([box_span((x0 - 40.0 - t, x0 - 40.0), sorted((s * 35.0, s * L / 2)),
                                       (P.robot_upper_beam_z[0] - 20.0, P.robot_upper_beam_z[1] + 20.0)) for s in (-1, 1)])
    lugs = []
    for s in (-1, 1):
        y = sorted((s * P.lug_gap / 2, s * (P.lug_gap / 2 + P.lug_t)))
        lug = box_span((x0 + t, PX), y, (PZ - 25.0, PZ + 25.0)).fuse(cyl_y(50.0, y[0], y[1], PX, PZ))
        lugs.append(lug.cut(cyl_y(P.pivot_d + 0.5, y[0] - 1, y[1] + 1, PX, PZ)))
    return Part.makeCompound([plate, back] + lugs)


def clamp_bolts():
    """4 x M10 above and below the beam through plate and back plate (the beam is clamped between them)."""
    x0 = P.robot_outer_beam_x
    out = []
    for z in (P.robot_upper_beam_z[0] - 8.0, P.robot_upper_beam_z[1] + 8.0):
        for y in (-80.0, 80.0):
            out.append(bolt_axis(10.0, (x0 + P.bracket[0], y, z), (x0 - 40.0 - P.bracket[0], y, z), 17.0, 6.4, 8.4))
    return Part.makeCompound(out)


def pivot_pin():
    return cyl_y(P.pivot_d, -P.lug_gap / 2 - P.lug_t - 6.0, P.lug_gap / 2 + P.lug_t + 6.0, PX, PZ)


def bearer():
    z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + P.bearer)
    t = tube_span((-P.bearer_x, P.bearer_x), (-P.bearer / 2, P.bearer / 2), z, 3.0, "x")
    for sx in (-1, 1):
        for xb in P.robot_upper_beam_x:
            t = t.cut(cyl(P.m10_hole, (sx * xb, 0, 600), (sx * xb, 0, 800)))
    xb, zb = P.act_base
    lug = box_span((xb - 15.0, xb + 15.0), (P.bearer / 2, P.act_y - 8.0), (z[1] - 20.0, zb + 15.0))
    return t.fuse(lug).removeSplitter().cut(cyl_y(12.5, 0, P.act_y, xb, zb))


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * xb, 0.0, P.robot_upper_beam_z[0], P.robot_upper_beam_z[1] + P.bearer)
                              for sx in (-1, 1) for xb in P.robot_upper_beam_x])


# ---------------------------------------------------------------------
# Arm group (turns about the pivot; drawn in work)
# ---------------------------------------------------------------------
def arm():
    """Arm 60 x 40 x 3 (pivot -> elbow -> end), pivot boss, 2 hangers 8 mm for the rotor bearings, crank plate."""
    hx, hz = P.arm_end()
    ex, ez = P.elbow
    parts = [rect_tube((PX, 0.0, PZ), (ex, 0.0, ez), P.arm_w, P.arm_h, 3.0, up=(0.0, 0.0, 1.0)),
             rect_tube((ex, 0.0, ez), (hx, 0.0, hz), P.arm_w, P.arm_h, 3.0, up=(0.0, 0.0, 1.0)),
             cyl_y(P.arm_w, -P.arm_w / 2, P.arm_w / 2, ex, ez).common(box_span((ex - 30, ex + 30), (-30, 30), (ez - 20, ez + 20))),
             cyl_y(40.0, -P.lug_gap / 2 + 1.0, P.lug_gap / 2 - 1.0, PX, PZ)]
    for x0 in (P.rotor_x[0] - 12.0 - P.hanger_t, P.rotor_x[1] + 12.0):
        ztop = ez + (hz - ez) * (x0 - ex) / (hx - ex)
        parts.append(box_span((x0, x0 + P.hanger_t), (-30.0, 30.0), (RZ - 35.0, ztop)))
    cz = PZ + P.crank_r
    parts.append(box_span((PX - 15.0, PX + 15.0), (P.lug_gap / 2 - 13.0, P.lug_gap / 2 - 5.0), (PZ, cz + 15.0)))
    s = fuse_all(parts)
    s = s.cut(cyl_y(P.pivot_d + 0.5, -100, 100, PX, PZ))
    return s.cut(cyl_x(20.5, 0, 3000, 0.0, RZ))


def crank_pin():
    return cyl_y(12.0, P.lug_gap / 2 - 13.0, P.act_y + 10.0, PX, PZ + P.crank_r)


def cyl_x(d, x0, x1, y, z):
    return cyl(d, (x0, y, z), (x1, y, z))


def rotor():
    """Tube O60 along x on a shaft O20, 4 rows of 16 spring tines O7 (tip radius 120), trailing 20 degrees."""
    x0, x1 = P.rotor_x
    tube = cyl_x(P.rotor_tube, x0, x1, 0.0, RZ).cut(cyl_x(P.rotor_tube - 6.0, x0 - 1, x1 + 1, 0.0, RZ))
    out = [tube]
    r0 = P.rotor_tube / 2 - 1.0
    for row in range(P.tine_rows):
        a = 360.0 / P.tine_rows * row
        for i in range(P.tines_per_row):
            x = x0 + 25.0 + i * (P.rotor_len - 60.0) / (P.tines_per_row - 1) + (row % 2) * 12.0
            a0, a1 = math.radians(a), math.radians(a + 20.0)
            p0 = (x, r0 * math.cos(a0), RZ + r0 * math.sin(a0))
            p1 = (x, (P.tip_r - 4.0) * math.cos(a1), RZ + (P.tip_r - 4.0) * math.sin(a1))
            out.append(cyl(P.tine_d, p0, p1))
    return Part.makeCompound(out)


def shaft_and_bearings():
    x0, x1 = P.rotor_x
    shaft = cyl_x(20.0, x0 - 12.0 - P.hanger_t - 6.0, x1 + 12.0 + P.hanger_t + 40.0, 0.0, RZ)
    brgs = [cyl_x(62.0, x0 - 12.0, x0 - 2.0, 0.0, RZ), cyl_x(62.0, x1 + 2.0, x1 + 12.0, 0.0, RZ)]
    return shaft, Part.makeCompound([b.cut(cyl_x(20.5, 0, 3000, 0.0, RZ)) for b in brgs])


def gearmotor():
    x0 = P.rotor_x[1] + 12.0 + P.hanger_t
    return cyl_x(P.gm_d, x0, x0 + P.gm_len, 0.0, RZ).cut(cyl_x(20.5, x0 - 1, x0 + 30.0, 0.0, RZ))


def crank_point(lift):
    a = math.radians(lift)
    return PX - P.crank_r * math.sin(a), PZ + P.crank_r * math.cos(a)


def actuator(lift=0.0):
    """(body, rod, length) of the lift actuator from the bearer lug to the crank pin."""
    xb, zb = P.act_base
    cx, cz = crank_point(lift)
    A, B = V(xb, P.act_y, zb), V(cx, P.act_y, cz)
    u = B - A
    L = u.Length
    u.normalize()
    body_len = 400.0
    body = Part.makeCompound([cyl(P.act_body_d, A + u * 20.0, A + u * (20.0 + body_len)), cyl(24.0, A - u * 12.0, A + u * 20.0)])
    rod = Part.makeCompound([cyl(P.act_rod_d, A + u * (body_len + 10.0), B - u * 12.0), cyl(26.0, B - u * 14.0, B + u * 12.0)])
    return body, rod, L


# ---------------------------------------------------------------------
# Barn (picture and checks): curb with the bed, divider loops
# ---------------------------------------------------------------------
def bed():
    return box_span((P.curb_x, P.curb_x + P.bed_len), (-1800.0, 1800.0), (0.0, P.bed_z))


def _tube_path(pts, d, y):
    out = []
    for (x0, z0), (x1, z1) in zip(pts[:-1], pts[1:]):
        out.append(cyl(d, (x0, y, z0), (x1, y, z1)))
    for x, z in pts[1:-1]:
        out.append(Part.makeSphere(d / 2.0, V(x, y, z)))
    return out


def dividers(ys=P.divider_y):
    """Cantilever loops from a post at the neck rail end: bottom rail at bed + 380, top at bed + 1050."""
    zb, zt = P.bed_z + P.loop_bottom, P.bed_z + P.loop_top
    xf = P.curb_x + P.bed_len - 100.0
    pts = [(P.loop_rear_x, zb), (xf, zb), (xf, zt), (P.loop_rear_x + 600.0, zt), (P.loop_rear_x + 150.0, zb + 300.0),
           (P.loop_rear_x, zb)]
    out = []
    for y in ys:
        out += _tube_path(pts, P.divider_d, y)
        out.append(cyl(P.divider_d + 12.0, (xf + 40.0, y, P.bed_z), (xf + 40.0, y, zt + 100.0)))
    return Part.makeCompound(out)
