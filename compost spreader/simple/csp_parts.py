"""Parts of the compost spreader. Every function returns a Part shape in robot coordinates.
The belt and the beater turn, but nothing changes place: there is no pose, only the load (compost) can be hidden.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import csp_params as P



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


def both_sides(fn):
    """Compound of fn(sx) for sx = -1, +1."""
    return Part.makeCompound([fn(sx) for sx in (-1, 1)])


SHAFTS = ((P.drum_y_front, P.drum_z, P.shaft_d), (P.drum_y_rear, P.drum_z, P.shaft_d),
          (P.beater_y, P.beater_z, P.beater_shaft))


# ---------------------------------------------------------------------
# Mount: bearers on the upper beams, feet of the side plates
# ---------------------------------------------------------------------
def foot_x():
    return P.side_x + P.side_t + P.foot[0] / 2.0


def bearers():
    """3 tubes 40 x 40 x 3 across the upper beams, holes for 4 x M10 to the beams and 2 x M10 for the feet."""
    out = []
    for yc in P.bearer_y:
        t = tube_span((-P.bearer_x, P.bearer_x), (yc - P.bearer / 2.0, yc + P.bearer / 2.0), P.bearer_z, 3.0, "x")
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x + (foot_x(),):
                t = t.cut(cyl(P.m10_hole, (sx * xb, yc, 600), (sx * xb, yc, 800)))
        out.append(t)
    return Part.makeCompound(out)


def bearer_bolts():
    out = []
    for yc in P.bearer_y:
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                out.append(bolt_z(10.0, sx * xb, yc, P.robot_upper_beam_z[0], P.bearer_z[1]))
    return Part.makeCompound(out)


def feet():
    """Angle 40 x 40 x 4 welded outside the side plates, standing on each bearer."""
    a, t, L = P.foot
    out = []
    for yc in P.bearer_y:
        for sx in (-1, 1):
            x0 = P.side_x + P.side_t
            z0 = P.bearer_z[1]
            f = box_span((x0, x0 + a), (yc - L / 2, yc + L / 2), (z0, z0 + t))
            f = f.fuse(box_span((x0, x0 + t), (yc - L / 2, yc + L / 2), (z0 + t, z0 + a))).removeSplitter()
            f = f.cut(cyl(P.m10_hole, (foot_x(), yc, z0 - 1), (foot_x(), yc, z0 + t + 1)))
            out.append(f if sx > 0 else mirror_x(f))
    return Part.makeCompound(out)


def feet_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * foot_x(), yc, P.bearer_z[0], P.bearer_z[1] + P.foot[1])
                              for yc in P.bearer_y for sx in (-1, 1)])


# ---------------------------------------------------------------------
# Conveyor frame
# ---------------------------------------------------------------------
def side_plates():
    def one(sx):
        p = plate_yz(P.side_pts, P.side_x, P.side_t)
        for y, z, d in SHAFTS:
            p = p.cut(cyl_x(d + 2.0, P.side_x - 1, P.side_x + P.side_t + 1, y, z))
        return p if sx > 0 else mirror_x(p)
    return both_sides(one)


def bed_z():
    """(bottom, top) of the slide bed."""
    top = P.drum_z + P.drum_d / 2.0 - P.bed_gap
    return top - P.bed_t, top


def bed_rails():
    """Angle 20 x 20 x 4 welded inside the side plates under the slide bed."""
    a, _ = P.bed_rail
    z1 = bed_z()[0]

    def one(sx):
        r = box_span((P.side_x - a, P.side_x), P.bed_y, (z1 - 4.0, z1))
        r = r.fuse(box_span((P.side_x - 4.0, P.side_x), P.bed_y, (z1 - a, z1 - 4.0))).removeSplitter()
        return r if sx > 0 else mirror_x(r)
    return both_sides(one)


def slide_bed():
    z0, z1 = bed_z()
    return box_span((-P.side_x + 5.0, P.side_x - 5.0), P.bed_y, (z0, z1))


def drums():
    """Tube O100 x 4 with 8 mm end discs on the shaft (rear drum lagged with rubber, drawn as steel)."""
    r = P.drum_len / 2.0
    out = []
    for y in (P.drum_y_front, P.drum_y_rear):
        d = cyl_x(P.drum_d, -r, r, y, P.drum_z).cut(cyl_x(P.drum_d - 8.0, -r + 8.0, r - 8.0, y, P.drum_z))
        out.append(d.cut(cyl_x(P.shaft_d, -r - 1, r + 1, y, P.drum_z)))
    return Part.makeCompound(out)


def drum_shafts():
    x_out = P.side_x + P.side_t + P.brg_depth + 6.0
    front = cyl_x(P.shaft_d, -x_out, x_out, P.drum_y_front, P.drum_z)
    rear = cyl_x(P.shaft_d, -(x_out + P.belt_gm_box[0] - 6.0), x_out, P.drum_y_rear, P.drum_z)
    return Part.makeCompound([front, rear])


def belt():
    """Endless belt round the two drums: outer stadium minus inner stadium, 920 wide."""
    x = (-P.belt_w / 2.0, P.belt_w / 2.0)

    def stadium(r):
        s = cyl_x(2 * r, x[0], x[1], P.drum_y_front, P.drum_z)
        s = s.fuse(cyl_x(2 * r, x[0], x[1], P.drum_y_rear, P.drum_z))
        return s.fuse(box_span(x, (P.drum_y_rear, P.drum_y_front), (P.drum_z - r, P.drum_z + r)))
    R = P.drum_d / 2.0
    return stadium(R + P.belt_t).cut(stadium(R)).removeSplitter()


def flange_bearing(sx, y, z, sq, flange, body_d, depth):
    x0 = P.side_x + P.side_t
    b = box_span((x0, x0 + flange), (y - sq / 2, y + sq / 2), (z - sq / 2, z + sq / 2))
    b = b.fuse(cyl_x(body_d, x0 + flange, x0 + depth, y, z))
    return b if sx > 0 else mirror_x(b)


def drum_bearings():
    """4 x UCFL204, front pair in take-up slots."""
    return Part.makeCompound([flange_bearing(sx, y, P.drum_z, P.brg_sq, P.brg_flange, P.brg_body_d, P.brg_depth)
                              for y in (P.drum_y_front, P.drum_y_rear) for sx in (-1, 1)])


# ---------------------------------------------------------------------
# Bin
# ---------------------------------------------------------------------
def skirts():
    """Rubber strips 8 mm from the inside of the side plates down onto the belt edges."""
    z0 = P.belt_top + 2.0
    pts = ((P.skirt_low_x, z0), (P.skirt_low_x + P.skirt_t, z0), (P.side_x, P.skirt_top_z - 25.0),
           (P.side_x, P.skirt_top_z), (P.side_x - P.skirt_t, P.skirt_top_z))
    s = plate_xz(pts, P.bin_y[0], P.bin_y[1] - P.wall_t)
    return Part.makeCompound([s, mirror_x(s)])


def flare_walls():
    """Flared walls 3 mm on top of the side plates, z 1060..1160."""
    z0, z1 = P.bin_flare_z
    xo = P.side_x + 4.0
    pts = ((P.side_x, z0), (xo, z0), (P.bin_top_x + 4.0, z1), (P.bin_top_x, z1))
    s = plate_xz(pts, P.bin_y[0], P.bin_y[1] - P.wall_t)
    return Part.makeCompound([s, mirror_x(s)])


def front_wall():
    z0, z1 = P.bin_flare_z
    xs, xo, xt = P.side_x, P.side_x + 4.0, P.bin_top_x + 4.0
    zb = P.drum_z + 35.0
    pts = [(-xs, zb), (xs, zb), (xs, z0), (xo, z0), (xt, z1), (-xt, z1), (-xo, z0), (-xs, z0)]
    return plate_xz(pts, P.bin_y[1] - P.wall_t, P.bin_y[1])


def rear_wall():
    """Fixed rear wall over the flare; below z 1060 the gate is the rear wall."""
    z0, z1 = P.bin_flare_z
    xo, xt = P.side_x + 4.0, P.bin_top_x + 4.0
    return plate_xz([(-xo, z0), (xo, z0), (xt, z1), (-xt, z1)], P.gate_y[1], P.gate_y[1] + P.wall_t)


def gate_bottom(opening=P.gate_open):
    return P.belt_top + opening


KNOB_X = 445.0
KNOB_DZ = 150.0                         # clamp stud above the gate bottom


def gate(opening=P.gate_open):
    """Slide gate 6 mm with 2 welded M10 studs at the back."""
    z0 = gate_bottom(opening)
    return box_span((-P.gate_w / 2, P.gate_w / 2), P.gate_y, (z0, z0 + P.gate_h))


def gate_guides():
    """Flat bars 55 x 4 behind the gate edges, welded to the side plates, with a vertical slot for the stud."""
    y = (P.gate_y[0] - P.guide[1], P.gate_y[0])
    lo = gate_bottom(P.GATE_RANGE[0]) + KNOB_DZ - 8.0
    hi = gate_bottom(P.GATE_RANGE[1]) + KNOB_DZ + 8.0

    def one(sx):
        b = box_span((420.0, P.side_x), y, (P.belt_top + 10.0, hi + 30.0))
        b = b.cut(box_span((KNOB_X - 5.5, KNOB_X + 5.5), (y[0] - 1, y[1] + 1), (lo, hi)))
        return b if sx > 0 else mirror_x(b)
    return both_sides(one)


def gate_knobs(opening=P.gate_open):
    """Star knobs O50 on the welded studs: they clamp the gate against the guides."""
    out = []
    yg = P.gate_y[0] - P.guide[1]
    z = gate_bottom(opening) + KNOB_DZ
    for sx in (-1, 1):
        x = sx * KNOB_X
        out.append(cyl(P.knob_d, (x, yg - 30.0, z), (x, yg, z)))
        out.append(cyl(10.0, (x, yg, z), (x, P.gate_y[0], z)))
    return Part.makeCompound(out)


def compost_load(rho=None):
    """Compost in the bin up to the level of a full payload (flat top)."""
    rho = P.COMPOST[P.compost_ref] if rho is None else rho
    zf = P.fill_level(P.payload_max, rho)
    z0 = P.belt_top + 1.0
    pts = [(-P.side_x + 1, z0), (P.side_x - 1, z0)]
    if zf > P.bin_flare_z[0]:
        pts += [(P.side_x - 1, P.bin_flare_z[0]), (P.bin_section(zf) - 1, zf), (-P.bin_section(zf) + 1, zf),
                (-P.side_x + 1, P.bin_flare_z[0])]
    else:
        pts += [(P.side_x - 1, zf), (-P.side_x + 1, zf)]
    return plate_xz(pts, P.bin_y[0] + 4.0, P.bin_y[1] - P.wall_t - 1.0)


# ---------------------------------------------------------------------
# Beater, hood, cross tube
# ---------------------------------------------------------------------
def beater_rotor():
    """Tube O114 x 4 with 10 mm end discs and 4 rows of 7 paddles 50 x 8 (staggered), tip radius 140."""
    r0 = P.beater_tube / 2.0
    L = P.beater_len / 2.0
    tube = cyl_x(P.beater_tube, -L, L, P.beater_y, P.beater_z).cut(
        cyl_x(P.beater_tube - 8.0, -L + 10, L - 10, P.beater_y, P.beater_z))
    tube = tube.cut(cyl_x(P.beater_shaft, -L - 1, -L + 10, P.beater_y, P.beater_z))
    tube = tube.cut(cyl_x(P.beater_shaft, L - 10, L + 1, P.beater_y, P.beater_z))
    out = [tube]
    w, t = P.paddle
    for row in range(P.paddle_rows):
        ang = 90.0 * row + 20.0
        for i in range(P.paddles_per_row):
            xc = -420.0 + i * 130.0 + (row % 2) * 65.0
            p = box_span((xc - w / 2, xc + w / 2), (-t / 2, t / 2), (r0, P.beater_tip_r))
            p.rotate(V(0, 0, 0), V(1, 0, 0), ang)
            p.translate(V(0, P.beater_y, P.beater_z))
            out.append(p)
    return Part.makeCompound(out)


def beater_shaft():
    """2 stub shafts O30 welded into the end discs of the rotor tube."""
    L = P.beater_len / 2.0 - 6.0
    x_left = P.side_x + P.side_t + P.beater_brg_depth + 6.0
    x_right = P.side_x + P.side_t + P.beater_brg_depth + P.guard[0] - 6.0
    return Part.makeCompound([cyl_x(P.beater_shaft, -x_left, -L, P.beater_y, P.beater_z),
                              cyl_x(P.beater_shaft, L, x_right, P.beater_y, P.beater_z)])


def beater_bearings():
    return Part.makeCompound([flange_bearing(sx, P.beater_y, P.beater_z, P.beater_brg_sq, P.beater_brg_flange,
                                             P.beater_brg_body_d, P.beater_brg_depth) for sx in (-1, 1)])


def hood():
    """Deflector 3 mm over and behind the rotor, between the side plates."""
    x = (-P.side_x, P.side_x)
    shell = cyl_x(2 * (P.hood_r + 3.0), x[0], x[1], P.beater_y, P.beater_z).cut(
        cyl_x(2 * P.hood_r, x[0] - 1, x[1] + 1, P.beater_y, P.beater_z))
    a0, a1 = P.hood_ang
    pts = [(P.beater_y, P.beater_z)]
    for k in range(7):
        a = math.radians(a0 + (a1 - a0) * k / 6.0)
        pts.append((P.beater_y + 400.0 * math.cos(a), P.beater_z + 400.0 * math.sin(a)))
    wedge = plate_yz(pts, x[0] - 2, 2 * P.side_x + 4)
    return shell.common(wedge)


def cross_tube():
    """Tube 40 x 40 x 3 between the side plates in front of and under the rotor."""
    return tube_span((-P.side_x, P.side_x), (-935.0, -895.0), (650.0, 690.0), 3.0, "x")


# ---------------------------------------------------------------------
# Drives
# ---------------------------------------------------------------------
def belt_gearmotor():
    """Worm box on the rear drum shaft (left) and the motor standing up on it."""
    bx, by, bz = P.belt_gm_box
    x1 = -(P.side_x + P.side_t + P.brg_depth + 2.0)
    box = box_span((x1 - bx, x1), (P.drum_y_rear - by / 2, P.drum_y_rear + by / 2),
                   (P.drum_z - bz / 2, P.drum_z + bz / 2))
    box = box.cut(cyl_x(P.shaft_d, x1 - bx - 1, x1 + 1, P.drum_y_rear, P.drum_z))
    motor = cyl((P.belt_motor_d), (x1 - bx / 2, P.drum_y_rear, P.drum_z + bz / 2),
                (x1 - bx / 2, P.drum_y_rear, P.drum_z + bz / 2 + P.belt_motor_l))
    return box, motor


def torque_arm():
    """Flat 50 x 8 from the worm box to the side plate."""
    bx, by, _ = P.belt_gm_box
    y1 = P.drum_y_rear - by / 2
    x1 = -(P.side_x + P.side_t + P.brg_depth + 2.0)
    return box_span((x1 - bx / 2, -(P.side_x + P.side_t)), (y1 - 8.0, y1), (P.drum_z - 25.0, P.drum_z + 25.0))


def guard_x():
    x0 = P.side_x + P.side_t + P.beater_brg_depth + 2.0
    return x0, x0 + P.guard[0]


def pulleys():
    x0, x1 = guard_x()
    xa, xb = x0 + 10.0, x1 - 10.0
    my, mz = P.beater_motor_pos
    big = cyl_x(P.pulley_big, xa, xb, P.beater_y, P.beater_z).cut(
        cyl_x(P.beater_shaft, xa - 1, xb + 1, P.beater_y, P.beater_z))
    return Part.makeCompound([big, cyl_x(P.pulley_small, xa, xb, my, mz)])


def vbelt():
    """Poly-V belt as a thin loop round both pulleys (outer hull minus inner hull)."""
    x0, x1 = guard_x()
    xa, xb = x0 + 12.0, x1 - 12.0
    my, mz = P.beater_motor_pos

    def hull(grow):
        a = cyl_x(P.pulley_big + 2 * grow, xa, xb, P.beater_y, P.beater_z)
        b = cyl_x(P.pulley_small + 2 * grow, xa, xb, my, mz)
        dy, dz = my - P.beater_y, mz - P.beater_z
        d = math.hypot(dy, dz)
        r1, r2 = P.pulley_big / 2 + grow, P.pulley_small / 2 + grow
        base = math.atan2(dz, dy)
        phi = math.acos((r1 - r2) / d)
        pts = []
        for s in (1, -1):
            a1 = base + s * phi
            pts.append((P.beater_y + r1 * math.cos(a1), P.beater_z + r1 * math.sin(a1)))
            pts.append((my + r2 * math.cos(a1), mz + r2 * math.sin(a1)))
        band = plate_yz([pts[0], pts[1], pts[3], pts[2]], xa, xb - xa)
        return a.fuse(b).fuse(band)
    return hull(5.0).cut(hull(0.0)).removeSplitter()


def guard():
    """Sheet guard round the poly-V drive; the outer sheet (4 mm) carries the motor."""
    x0, x1 = guard_x()
    my, mz = P.beater_motor_pos
    y = (P.beater_y - P.pulley_big / 2 - 25.0, my + P.pulley_small / 2 + 40.0)
    z = (P.beater_z - P.pulley_big / 2 - 25.0, mz + P.pulley_small / 2 + 30.0)
    g = box_span((x0, x1), y, z).cut(box_span((x0 - 1, x1 - 4.0), (y[0] + 2, y[1] - 2), (z[0] + 2, z[1] - 2)))
    return g


def beater_motor():
    x1 = guard_x()[1]
    my, mz = P.beater_motor_pos
    return cyl_x(P.beater_motor_d, x1, x1 + P.beater_motor_l, my, mz)
