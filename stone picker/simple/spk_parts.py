"""Parts of the stone picker. Every function returns a Part shape in robot coordinates (frame parts in the work pose;
build_spk moves the Lift group and turns the Door group).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import spk_params as P



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


def plate_xz(pts, y0, y1):
    """Plate in the x-z plane from a list of (x, z) points, from y0 to y1."""
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, y1 - y0, 0))


def cyl_x(d, x0, x1, y, z):
    return cyl(d, (x0, y, z), (x1, y, z))


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both(shape):
    """Compound of a right-side shape and its mirror."""
    return Part.makeCompound([shape, mirror_x(shape)])


def rot_yz(shape, centre, deg):
    """Rotate a copy about an x axis through centre (y, z)."""
    s = shape.copy()
    s.rotate(V(0, centre[0], centre[1]), V(1, 0, 0), deg)
    return s


def lower_pin(i, theta):
    """(y, z) of the lower pin of link i (0 front, 1 rear) at a link angle."""
    dy, dz = P.link_offset(theta)
    return P.hanger_y[i] + dy, P.hanger_pivot_z + dz


def frame_pin(i):
    """(y, z) of the lower pins in the work pose (frame coordinates)."""
    return lower_pin(i, P.theta_work)


# ---------------------------------------------------------------------
# Mount (fixed): hangers under the inner upper beams, bearer with the actuator lug
# ---------------------------------------------------------------------
def hanger_tops():
    x0, x1, t = P.hanger_top
    z1 = P.robot_upper_beam_z[0]
    out = []
    for y in P.hanger_y:
        p = box_span((x0, x1), (y - P.hanger_top_len / 2, y + P.hanger_top_len / 2), (z1 - t, z1))
        for dy in (-25.0, 25.0):
            p = p.cut(cyl(P.m10_hole, (P.robot_upper_beam_x[1], y + dy, z1 - t - 1), (P.robot_upper_beam_x[1], y + dy, z1 + 1)))
        out.append(p)
    return both(Part.makeCompound(out))


def hanger_webs():
    x0, x1 = P.hanger_web_x
    z1 = P.robot_upper_beam_z[0] - P.hanger_top[2]
    out = []
    for y in P.hanger_y:
        pts = ((y - 35.0, z1), (y + 35.0, z1), (y + 25.0, P.hanger_pivot_z - 25.0), (y - 25.0, P.hanger_pivot_z - 25.0))
        w = plate_yz(pts, x0, x1 - x0).fuse(cyl_x(50.0, x0, x1, y, P.hanger_pivot_z)).removeSplitter()
        out.append(w.cut(cyl_x(P.pin_d + 0.5, x0 - 1, x1 + 1, y, P.hanger_pivot_z)))
    return both(Part.makeCompound(out))


def hanger_bolts():
    z1 = P.robot_upper_beam_z
    out = [bolt_z(10.0, P.robot_upper_beam_x[1], y + dy, z1[0] - P.hanger_top[2], z1[1])
           for y in P.hanger_y for dy in (-25.0, 25.0)]
    return both(Part.makeCompound(out))


def upper_pins():
    out = [cyl_x(P.pin_d, P.link_x[0] - 0.5, P.hanger_web_x[1] + 6.0, y, P.hanger_pivot_z) for y in P.hanger_y]
    return both(Part.makeCompound(out))


def bearer():
    y = (P.bearer_y - P.bearer / 2, P.bearer_y + P.bearer / 2)
    z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + P.bearer)
    t = tube_span((-P.bearer_x, P.bearer_x), y, z, 3.0, "x")
    for sx in (-1, 1):
        for xb in P.robot_upper_beam_x:
            t = t.cut(cyl(P.m10_hole, (sx * xb, P.bearer_y, 600), (sx * xb, P.bearer_y, 800)))
    return t


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * xb, P.bearer_y, P.robot_upper_beam_z[0],
                                     P.robot_upper_beam_z[1] + P.bearer)
                              for sx in (-1, 1) for xb in P.robot_upper_beam_x])


def act_lug():
    """2 plates 8 mm on top of the bearer, base pin of the lift actuator."""
    yb, zb = P.act_base
    z0 = P.robot_upper_beam_z[1] + P.bearer
    out = []
    for x0 in (16.0, -24.0):
        pts = ((P.bearer_y - 30.0, z0), (P.bearer_y + 30.0, z0), (yb + 18.0, zb), (yb - 18.0, zb))
        p = plate_yz(pts, x0, 8.0).fuse(cyl_x(36.0, x0, x0 + 8.0, yb, zb)).removeSplitter()
        out.append(p.cut(cyl_x(12.5, x0 - 1, x0 + 9, yb, zb)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Links (they turn): flat bar 40 x 8 between the pins, ends rounded
# ---------------------------------------------------------------------
def links(theta=P.theta_work):
    out = []
    for i, y in enumerate(P.hanger_y):
        a = V(0, y, P.hanger_pivot_z)
        yl, zl = lower_pin(i, theta)
        b = V(0, yl, zl)
        x0, x1 = P.link_x
        u = b - a
        L = u.Length
        s = box_span((x0, x1), (-P.link[0] / 2, P.link[0] / 2), (-L, 0.0))
        s = s.fuse(cyl_x(P.link[0], x0, x1, 0.0, 0.0)).fuse(cyl_x(P.link[0], x0, x1, 0.0, -L)).removeSplitter()
        s = s.cut(cyl_x(P.pin_d + 0.5, x0 - 1, x1 + 1, 0.0, 0.0)).cut(cyl_x(P.pin_d + 0.5, x0 - 1, x1 + 1, 0.0, -L))
        s.rotate(V(0, 0, 0), V(1, 0, 0), theta)
        s.translate(a)
        out.append(s)
    return both(Part.makeCompound(out))


# ---------------------------------------------------------------------
# Frame (moves with the lift, drawn in the work pose)
# ---------------------------------------------------------------------
def frame():
    """Weldment: 2 side beams 40 x 40 x 3 outside the wheel line, front cross tube 60 x 40 x 3 over the rotor, rear
    cross tube 40 x 40 x 3 for the basket, 2 bearing plates 8 mm, 2 top stays 20 x 6 to the basket rear wall, lug for
    the lift actuator rod. Holes for the lower link pins and the rotor shaft."""
    parts = []
    for sx in (-1, 1):
        x = sorted((sx * P.side_beam_x[0], sx * P.side_beam_x[1]))
        parts.append(tube_span(x, P.side_beam_y, P.frame_z, 3.0, "y"))
        for ye in (P.side_beam_y[0], P.side_beam_y[1] - 3.0):
            parts.append(box_span(x, (ye, ye + 3.0), P.frame_z))
        xp = sorted((sx * P.brg_plate_x, sx * (P.brg_plate_x + P.brg_plate_t)))
        parts.append(box_span(xp, (P.rotor_y - 50.0, P.rotor_y + 50.0), (P.rotor_z - 50.0, P.frame_z[0])))
        xs = sorted((sx * (P.basket_x - 20.0), sx * P.basket_x))
        parts.append(box_span(xs, (P.basket_y[0], P.rear_cross_y[0]), (P.basket_top, P.basket_top + 6.0)))
    xi = P.side_beam_x[0]
    parts.append(tube_span((-xi, xi), P.cross_y, P.cross_z, 3.0, "x"))
    parts.append(tube_span((-xi, xi), P.rear_cross_y, P.frame_z, 3.0, "x"))
    yr, zr = P.act_rod
    for x0 in (14.0, -22.0):
        pts = ((P.rear_cross_y[0] + 4.0, P.frame_z[1]), (P.rear_cross_y[1] - 4.0, P.frame_z[1]), (yr + 16.0, zr),
               (yr - 16.0, zr))
        parts.append(plate_yz(pts, x0, 8.0).fuse(cyl_x(32.0, x0, x0 + 8.0, yr, zr)))
    shape = fuse_all(parts)
    for i in (0, 1):
        y, z = frame_pin(i)
        shape = shape.cut(cyl_x(P.pin_d + 0.5, -600, 600, y, z))
    shape = shape.cut(cyl_x(P.shaft_d + 1.0, -600, 600, P.rotor_y, P.rotor_z))
    return shape.cut(cyl_x(12.5, -30, 30, yr, zr))


def lower_pins():
    out = []
    for i in (0, 1):
        y, z = frame_pin(i)
        out.append(cyl_x(P.pin_d, P.side_beam_x[0] - 6.0, P.link_x[1] + 0.5, y, z))
    return both(Part.makeCompound(out))


def lower_pins_ok():
    """The lower pins sit in the side beams: frame_z must contain the pin height."""
    return all(P.frame_z[0] + 8.0 < frame_pin(i)[1] < P.frame_z[1] - 8.0 for i in (0, 1))


# ---------------------------------------------------------------------
# Rotor
# ---------------------------------------------------------------------
def rotor_tube():
    L = P.rotor_len / 2.0
    t = cyl_x(P.rotor_tube, -L, L, P.rotor_y, P.rotor_z).cut(cyl_x(P.rotor_tube - 8.0, -L + 8, L - 8, P.rotor_y, P.rotor_z))
    return t.cut(cyl_x(P.shaft_d, -L - 1, L + 1, P.rotor_y, P.rotor_z))


def _pt(r, ang_deg):
    a = math.radians(ang_deg)
    return P.rotor_y + r * math.cos(a), P.rotor_z + r * math.sin(a)


def tines():
    """6 rows of double spring tines; each leg from the tube to the tip radius, trailing by tine_lean."""
    r0 = P.rotor_tube / 2.0 - 2.0
    out = []
    for row in range(P.tine_rows):
        a = 360.0 / P.tine_rows * row - 90.0
        for i in range(P.tines_per_row):
            xc = -440.0 + i * 120.0 + (row % 2) * 60.0
            for dx in (-14.0, 14.0):
                y0, z0 = _pt(r0, a)
                y1, z1 = _pt(P.tip_r - P.tine_wire / 2.0, a + P.tine_lean)
                out.append(cyl(P.tine_wire, (xc + dx, y0, z0), (xc + dx, y1, z1)))
            # clamp of the double tine on the tube
            yc, zc = _pt(r0 + 6.0, a)
            out.append(cyl(22.0, (xc - 22.0, yc, zc), (xc + 22.0, yc, zc)))
    return Part.makeCompound(out)


def rotor_shaft():
    x1 = P.brg_plate_x + P.brg_plate_t + P.brg_depth + 6.0
    return cyl_x(P.shaft_d, -x1, x1 + 30.0, P.rotor_y, P.rotor_z)


def rotor_bearings():
    x0 = P.brg_plate_x + P.brg_plate_t
    sq = P.brg_sq
    b = box_span((x0, x0 + P.brg_flange), (P.rotor_y - sq / 2, P.rotor_y + sq / 2), (P.rotor_z - sq / 2, P.rotor_z + sq / 2))
    b = b.fuse(cyl_x(P.brg_body_d, x0 + P.brg_flange, x0 + P.brg_depth, P.rotor_y, P.rotor_z))
    b = b.cut(cyl_x(P.shaft_d, x0 - 1, x0 + P.brg_depth + 1, P.rotor_y, P.rotor_z))
    return both(b)


def gearmotor():
    """48 V 750 W planetary gearmotor on the right shaft end, torque arm to the bearing plate."""
    x0 = P.brg_plate_x + P.brg_plate_t + P.brg_depth + 4.0
    gm = cyl_x(P.gm_d, x0, x0 + P.gm_len, P.rotor_y, P.rotor_z).cut(
        cyl_x(P.shaft_d, x0 - 1, x0 + 40.0, P.rotor_y, P.rotor_z))
    arm = box_span((P.brg_plate_x + P.brg_plate_t, x0 + 20.0), (P.rotor_y - 6.0, P.rotor_y + 6.0),
                   (P.rotor_z + P.gm_d / 2.0, P.rotor_z + P.gm_d / 2.0 + 60.0))
    return gm, arm


# ---------------------------------------------------------------------
# Basket (welded to the frame) and comb
# ---------------------------------------------------------------------
def basket_walls():
    """Side walls and rear wall 3 mm, from just under the floor to the top."""
    zb = P.floor_z - P.floor_bar - 8.0
    yb = (P.basket_y[0], P.basket_y[1])
    side = box_span((P.basket_x - P.wall_t, P.basket_x), yb, (zb, P.basket_top))
    rear = box_span((-P.basket_x + P.wall_t, P.basket_x - P.wall_t), (yb[0], yb[0] + P.wall_t),
                    (P.floor_z + 2.0, P.basket_top))
    # front wall above the comb, up to the rear cross tube (the basket hangs from it)
    front = box_span((-P.basket_x, P.basket_x), (yb[1] - P.wall_t, yb[1]), (P.comb_root_z + 160.0, P.frame_z[0]))
    return Part.makeCompound([side, mirror_x(side), rear, front])


def comb():
    """13 bars O12 from the floor hinge forward-down to the tips just behind the rotor."""
    w = 2.0 * (P.basket_x - P.wall_t) - P.floor_bar - 10.0
    out = []
    for i in range(P.comb_bars):
        x = -w / 2.0 + w * i / (P.comb_bars - 1)
        out.append(cyl(P.floor_bar, (x, P.basket_y[1] - 4.0, P.comb_root_z), (x, P.comb_tip[0], P.comb_tip[1])))
    # cross bar under the comb roots, welded to the side walls
    out.append(box_span((-P.basket_x + P.wall_t, P.basket_x - P.wall_t), (P.basket_y[1] - 16.0, P.basket_y[1]),
                        (P.comb_root_z + 6.0, P.comb_root_z + 22.0)))
    return Part.makeCompound(out)


def deflectors():
    """Plates from the rotor ends to the basket front corners, so the outer stones bounce into the basket."""
    t = P.deflector_t
    xo = P.rotor_len / 2.0
    pts = [(P.basket_x, P.basket_y[1]), (xo, P.rotor_y - P.tip_r - 25.0), (xo, P.rotor_y - P.tip_r - 25.0 + t),
           (P.basket_x, P.basket_y[1] + t)]
    w = Part.makePolygon([V(x, y, 20.0) for x, y in pts] + [V(pts[0][0], pts[0][1], 20.0)])
    s = Part.Face(w).extrude(V(0, 0, P.frame_z[0] - 20.0))
    return both(s)


def hinge():
    """(y, z) of the floor hinge axis."""
    return P.basket_y[1] - 8.0, P.floor_z - P.floor_bar - 2.0


def floor():
    """Sieve floor: bars O12 along y at 37 mm, 3 cross flats under them, hinge tube, lug for the door actuator."""
    hy, hz = hinge()
    w = 2.0 * (P.basket_x - P.wall_t) - 10.0
    n = int(w // (P.floor_bar + P.floor_gap)) + 1
    pitch = w / (n - 1)
    zc = P.floor_z - P.floor_bar / 2.0
    y_rear = P.basket_y[0] + P.wall_t + 2.0
    parts = [cyl(P.floor_bar, (-w / 2 + i * pitch, hy - 8.0, zc), (-w / 2 + i * pitch, y_rear, zc)) for i in range(n)]
    for yf in (hy - 40.0, (hy + y_rear) / 2.0, y_rear + 25.0):
        parts.append(box_span((-w / 2 - 6, w / 2 + 6), (yf - 15.0, yf + 15.0), (zc - P.floor_bar / 2 - 6.0, zc - P.floor_bar / 2)))
    parts.append(cyl_x(20.0, -(P.basket_x - P.wall_t) + 1, P.basket_x - P.wall_t - 1, hy, hz))
    # actuator lug behind the rear wall, under it
    ly, lz = door_rod_pin()
    parts.append(box_span((-4.0, 4.0), (ly - 12.0, y_rear + 40.0), (lz - 12.0, zc - P.floor_bar / 2)))
    shape = Part.makeCompound(parts)
    return shape


def door_rod_pin():
    """(y, z) of the door actuator rod pin on the floor lug, closed."""
    return P.basket_y[0] - 30.0, P.floor_z - P.floor_bar - 16.0


def door_lug():
    """2 plates 6 mm on the back of the rear wall, base pin of the door actuator."""
    yb, zb = P.door_base
    out = []
    for x0 in (10.0, -16.0):
        p = box_span((x0, x0 + 6.0), (yb - 15.0, P.basket_y[0]), (zb - 15.0, zb + 20.0))
        out.append(p.cut(cyl_x(10.5, x0 - 1, x0 + 7, yb, zb)))
    return Part.makeCompound(out)


def door_point(door_deg):
    """Rod pin (y, z) when the floor is open by door_deg (frame coordinates)."""
    hy, hz = hinge()
    py, pz = door_rod_pin()
    a = math.radians(door_deg)
    dy, dz = py - hy, pz - hz
    return hy + dy * math.cos(a) - dz * math.sin(a), hz + dy * math.sin(a) + dz * math.cos(a)


def actuator_between(a, b, body_d, rod_d, body_len):
    """(body, rod) of a linear actuator from pin a to pin b (both (y, z) at x 0)."""
    A, B = V(0, a[0], a[1]), V(0, b[0], b[1])
    u = B - A
    L = u.Length
    u.normalize()
    body = Part.makeCompound([cyl(body_d, A + u * 18.0, A + u * (18.0 + body_len)), cyl(body_d * 0.55, A - u * 10.0, A + u * 18.0)])
    rod = Part.makeCompound([cyl(rod_d, A + u * (18.0 + body_len - 10.0), B - u * 10.0), cyl(rod_d * 1.3, B - u * 12.0, B + u * 10.0)])
    return body, rod, L


def door_actuator(door_deg=0.0):
    return actuator_between(P.door_base, door_point(door_deg), P.door_body_d, P.door_rod_d, 200.0)


def lift_actuator(theta=P.theta_work):
    dy, dz = P.frame_shift(theta)
    rod = (P.act_rod[0] + dy, P.act_rod[1] + dz)
    return actuator_between(P.act_base, rod, P.act_body_d, P.act_rod_d, P.act_retracted - 70.0)


def stones(seed=3):
    """Stones (spheres O40..110) lying in the front of the basket, for the pictures (not a real load model)."""
    import random
    rnd = random.Random(seed)
    out = []
    for _ in range(26):
        r = rnd.uniform(20.0, 55.0)
        x = rnd.uniform(-P.basket_x + P.wall_t + r + 2, P.basket_x - P.wall_t - r - 2)
        y = rnd.uniform(P.basket_y[0] + P.wall_t + r + 2, P.basket_y[1] - r - 2)
        s = Part.makeSphere(r, V(x, y, P.floor_z + r + 1.0))
        if all(s.distToShape(o)[0] > 1.0 for o in out):
            out.append(s)
    return Part.makeCompound(out)
