"""Parts of the cauliflower root-crown applicator: one function per part, in robot coordinates, row units at the
working height. Row-unit parts take the row centre rx; they are drawn for the right side of the row (dx > 0) and
mirrored about the row centre (both_sides_of_row)."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import cfa_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basic shapes
# ---------------------------------------------------------------------
def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_y(d, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def fuse_all(shapes):
    shapes = list(shapes)
    result = shapes[0]
    if len(shapes) > 1:
        result = result.fuse(shapes[1:])
    try:
        result = result.removeSplitter()
    except Exception:
        pass
    return result


def _poly(pts):
    pts = list(pts)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


def poly_xz(points, y0, t):
    """Closed polygon in the x-z plane, (x, z), extruded over +y from y0."""
    return _poly([V(x, y0, z) for (x, z) in points]).extrude(V(0, t, 0))


def poly_xy(points, z0, t):
    """Closed polygon in the x-y plane, (x, y), extruded over +z from z0."""
    return _poly([V(x, y, z0) for (x, y) in points]).extrude(V(0, 0, t))


def poly_yz(points, x0, t):
    """Closed polygon in the y-z plane, (y, z), extruded over +x from x0."""
    return _poly([V(x0, y, z) for (y, z) in points]).extrude(V(t, 0, 0))


def hull2d(points):
    """Convex hull (monotone chain), counter-clockwise."""
    pts = sorted(set((round(p[0], 4), round(p[1], 4)) for p in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def circle_pts(cx, cz, r, n=32):
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def plate_xz(points, y0, t, holes=()):
    """Convex plate in the x-z plane (hull of the points), y0 .. y0 + t, with round holes (x, z, d)."""
    s = poly_xz(hull2d(points), y0, t)
    for (hx, hz, d) in holes:
        s = s.cut(cyl_y(d, y0 - 1, y0 + t + 1, hx, hz))
    return s


def rbox(x, y, z, r):
    """Box with rounded vertical edges (rotomoulded tank)."""
    b = box_span(x, y, z)
    if r <= 0:
        return b
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    return b.makeFillet(r, edges)


def rod_between(p0, p1, d):
    p0, p1 = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (p1 - p0).Length, p0, p1 - p0)


def hose(points, od=P.hose_d):
    """Hose / pipe along a polyline, with a ball at every bend."""
    pts = [V(*p) for p in points]
    parts = [Part.makeCylinder(od / 2.0, (b - a).Length, a, b - a) for a, b in zip(pts[:-1], pts[1:])
             if (b - a).Length > 1e-6]
    parts += [Part.makeSphere(od / 2.0, p) for p in pts[1:-1]]
    return fuse_all(parts)


def square_tube_x(x0, x1, y, z, size, wall):
    o = box_span((x0, x1), (y - size / 2, y + size / 2), (z - size / 2, z + size / 2))
    i = box_span((x0 - 1, x1 + 1), (y - size / 2 + wall, y + size / 2 - wall), (z - size / 2 + wall, z + size / 2 - wall))
    return o.cut(i)


def square_tube_z(z0, z1, x, y, size, wall):
    o = box_span((x - size / 2, x + size / 2), (y - size / 2, y + size / 2), (z0, z1))
    i = box_span((x - size / 2 + wall, x + size / 2 - wall), (y - size / 2 + wall, y + size / 2 - wall), (z0 - 1, z1 + 1))
    return o.cut(i)


def hex_prism_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    return _poly(pts).extrude(V(0, 0, z1 - z0))


def hex_prism_y(af, y0, y1, x, z):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y0, z + r * math.sin(math.radians(60 * i))) for i in range(6)]
    return _poly(pts).extrude(V(0, y1 - y0, 0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    """Vertical bolt: head on top of z_head, nut under z_nut (underside of the clamped stack)."""
    head = hex_prism_z(af, z_head, z_head + k, x, y)
    shank = cyl_z(d, z_nut - m - 4.0, z_head, x, y)
    nut = hex_prism_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))
    return fuse_all([head, shank, nut])


def bolt_y(x, z, y_head, y_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    """Bolt along y: head in front of y_head (+y side), nut behind y_nut (-y side)."""
    head = hex_prism_y(af, y_head, y_head + k, x, z)
    shank = cyl_y(d, y_nut - m - 4.0, y_head, x, z)
    nut = hex_prism_y(af, y_nut - m, y_nut, x, z).cut(cyl_y(d, y_nut - m - 1, y_nut + 1, x, z))
    return fuse_all([head, shank, nut])


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both_sides(shape):
    return Part.makeCompound([shape, mirror_x(shape)])




def row_shape(rx, shape_right):
    """Row-unit part drawn for dx > 0 (row centre at x 0): mirror for the other side and move to the row."""
    s = Part.makeCompound([shape_right, mirror_x(shape_right)])
    s.translate(V(rx, 0, 0))
    return s


def at_row(rx, shape):
    s = shape.copy()
    s.translate(V(rx, 0, 0))
    return s


# ---------------------------------------------------------------------
# Tank and cradle
# ---------------------------------------------------------------------
def cradle_tubes():
    t, w = P.cradle_tube, P.cradle_wall
    out = []
    for y in P.cradle_y:
        tube = square_tube_x(-P.cradle_half_len, P.cradle_half_len, y, (P.cradle_z[0] + P.cradle_z[1]) / 2.0, t, w)
        holes = [cyl_z(P.m10_hole, P.cradle_z[0] - 1, P.cradle_z[1] + 1, x, y) for x in (-P.upper_bolt_x, P.upper_bolt_x)]
        out.append(tube.cut(holes))
    return Part.makeCompound(out)


def cradle_pads():
    hx = P.tank_x - 10.0           # between the strap legs
    return Part.makeCompound([box_span((-hx, hx), (y - 18.0, y + 18.0), (P.cradle_z[1], P.tank_z0)) for y in P.cradle_y])


def cradle_bolts():
    """M10 button-head bolts through the cradle tube and the upper beams, nut under the beam."""
    return Part.makeCompound([bolt_z(x, y, P.cradle_z[1], P.robot_upper_beam_z[0], k=4.0)
                              for y in P.cradle_y for x in (-P.upper_bolt_x, P.upper_bolt_x)])


def straps():
    t, w = P.strap_t, P.strap_w
    hx, top = P.tank_x, P.tank_z[1]
    out = []
    for y in P.cradle_y:
        yy = (y - w / 2.0, y + w / 2.0)
        parts = [box_span((-hx - t, hx + t), yy, (top, top + t))]
        for s in (-1, 1):
            parts.append(box_span((s * hx, s * (hx + t)), yy, (P.cradle_z[1], top + t)))
            parts.append(box_span((s * (hx + t), s * (hx + t + 22.0)), yy, (P.cradle_z[1], P.cradle_z[1] + t)))
        out.append(fuse_all(parts))
    return Part.makeCompound(out)


def _tank(inset=0.0):
    i = inset
    return rbox((-P.tank_x + i, P.tank_x - i), (P.tank_y[0] + i, P.tank_y[1] - i), (P.tank_z[0] + i, P.tank_z[1] - i),
                max(1.0, P.tank_r - i))


def tank_inner():
    return _tank(P.tank_wall)


def tank_shell():
    return _tank(0.0).cut(tank_inner())


def liquid(litres):
    z0 = P.tank_z0 + P.tank_wall
    inner = tank_inner()
    area = inner.Volume / (P.tank_h - 2 * P.tank_wall)
    h = min(P.tank_h - 2 * P.tank_wall - 1.0, litres * 1e6 / area)
    return inner.common(box_span((-P.tank_x, P.tank_x), P.tank_y, (z0, z0 + h)))


def tank_fittings():
    x, y, d, h = P.fill_cap
    z0 = P.tank_z[1]
    cap = fuse_all([cyl_z(d - 30.0, z0, z0 + h * 0.4, x, y), cyl_z(d, z0 + h * 0.4, z0 + h, x, y),
                    box_span((x - d / 2.0 + 10, x + d / 2.0 - 10), (y - 6, y + 6), (z0 + h, z0 + h + 10))])
    vx, vy, vd, vh = P.vent
    vent = fuse_all([cyl_z(vd, z0, z0 + vh, vx, vy), cyl_x(vd, vx - 30.0, vx + vd / 2.0, vy, z0 + vh - vd / 2.0)])
    d, l = P.wall_fitting
    walls = [cyl_y(d, P.tank_y[0] - l, P.tank_y[0], x, P.wall_fitting_z) for x in (P.outlet_x, P.return_x)]
    return Part.makeCompound([cap, vent] + walls)


def level_sensor():
    x, y, d, h = P.level_sensor
    z0 = P.tank_z[1]
    return fuse_all([cyl_z(d + 16.0, z0, z0 + 10.0, x, y), cyl_z(d, z0 + 10.0, z0 + h, x, y),
                     cyl_z(14.0, z0 + h, z0 + h + 18.0, x, y)])


# ---------------------------------------------------------------------
# Pump plate on the rear lower beams
# ---------------------------------------------------------------------
PLATE_BOLTS = [(x, y) for x in P.plate_bolt_x for y in P.robot_lower_beam_y[:2]]


def pump_plate():
    p = box_span(P.plate_x, P.plate_y, P.plate_z)
    return p.cut([cyl_z(P.m10_hole, P.plate_z[0] - 1, P.plate_z[1] + 1, x, y) for x, y in PLATE_BOLTS])


def plate_bolts():
    return Part.makeCompound([bolt_z(x, y, P.plate_z[1], P.robot_lower_beam_z[0]) for x, y in PLATE_BOLTS])


PUMP_ZC = P.pz + 5.0 + P.pump_motor[0] / 2.0


def pump():
    head = box_span(*P.pump_head)
    d, x0, x1 = P.pump_motor
    motor = fuse_all([cyl_x(d, x0, x1, P.pump_y, PUMP_ZC), cyl_x(30.0, x1, x1 + 12.0, P.pump_y, PUMP_ZC)])
    ports = [cyl_z(16.0, P.pump_head[2][1], P.pump_head[2][1] + 10.0, -160.0, P.pump_y),
             cyl_x(16.0, P.pump_head[0][0] - 12.0, P.pump_head[0][0], P.pump_y, P.pz + 55.0)]
    return Part.makeCompound([head, motor] + ports)


def pump_foot():
    return box_span(*P.pump_foot)


def filter_bowl():
    x, y = P.filter_xy
    d, h = P.filter_d, P.filter_h
    return fuse_all([cyl_z(d, P.pz, P.pz + h, x, y), cyl_z(d + 12.0, P.pz + h - 18.0, P.pz + h, x, y)])


REG_PORT = (47.5, -455.0)


def regulator():
    return fuse_all([box_span(*P.regulator),
                     cyl_z(30.0, P.regulator[2][1], P.regulator[2][1] + 12.0, REG_PORT[0], REG_PORT[1])])


def accumulator():
    x, y, d, h = P.accumulator
    return fuse_all([cyl_z(d, P.pz + 15.0, P.pz + h - d / 2.0, x, y), Part.makeSphere(d / 2.0, V(x, y, P.pz + h - d / 2.0)),
                     cyl_z(30.0, P.pz, P.pz + 15.0, x, y)])


def control_box():
    body = box_span(P.box_x, P.box_y, (P.pz, P.pz + P.box_h))
    glands = [cyl_y(14.0, P.box_y[1], P.box_y[1] + 12.0, x, P.pz + 25.0) for x in (190.0, 215.0, 240.0)]
    return Part.makeCompound([body] + glands)


def suction_hose():
    """Tank outlet -> filter top, filter side -> pump inlet."""
    xo, zf = P.outlet_x, P.wall_fitting_z
    fx, fy = P.filter_xy
    top = P.pz + P.filter_h
    a = hose([(xo, P.tank_y[0] - P.wall_fitting[1], zf), (xo, -445.0, zf), (fx, -445.0, zf + 15.0),
              (fx, fy, zf + 15.0), (fx, fy, top)])
    b = hose([(fx + P.filter_d / 2.0, P.pump_y, P.pz + 55.0), (P.pump_head[0][0] - 12.0, P.pump_y, P.pz + 55.0)])
    return Part.makeCompound([a, b])


def return_hose():
    """Regulator bypass -> tank return fitting."""
    xr, zf = P.return_x, P.wall_fitting_z
    return hose([(30.0, -440.0, P.regulator[2][1]), (30.0, -440.0, zf), (xr, -440.0, zf),
                 (xr, P.tank_y[0] - P.wall_fitting[1], zf)])


def pump_hose():
    """Pump outlet -> regulator."""
    top = P.pump_head[2][1] + 10.0
    zr = P.regulator[2][1] + 12.0
    return hose([(-160.0, P.pump_y, top), (-160.0, P.pump_y, 800.0), (REG_PORT[0], P.pump_y, 800.0),
                 (REG_PORT[0], REG_PORT[1], 800.0), (REG_PORT[0], REG_PORT[1], zr)])


def main_hose():
    """Regulator -> manifold on the toolbar, under the tank."""
    z = P.hose_main_z
    m = P.manifold
    yc = (m[1][0] + m[1][1]) / 2.0
    zr = P.pz + 35.0
    return hose([(47.5, P.regulator[1][1], zr), (47.5, -415.0, zr), (47.5, -400.0, z), (0.0, -370.0, z),
                 (0.0, yc, z), (0.0, yc, m[2][1])])


# ---------------------------------------------------------------------
# Toolbar
# ---------------------------------------------------------------------
BAR_ZC = (P.bar_z[0] + P.bar_z[1]) / 2.0


def toolbar():
    t = square_tube_x(-P.bar_half, P.bar_half, P.bar_y, BAR_ZC, P.bar, P.bar_wall)
    caps = [box_span((s * P.bar_half, s * (P.bar_half + 3.0)), (P.bar_y - P.bar / 2, P.bar_y + P.bar / 2), P.bar_z)
            for s in (-1, 1)]
    t = fuse_all([t] + caps)
    return t.cut([cyl_z(P.m10_hole, P.bar_z[0] - 1, P.bar_z[1] + 1, x, P.bar_y) for x in (-P.upper_bolt_x, P.upper_bolt_x)])


def toolbar_bolts():
    """M10 through the upper beam and the toolbar: head on the beam, nut under the toolbar."""
    return Part.makeCompound([bolt_z(x, P.bar_y, P.robot_upper_beam_z[1], P.bar_z[0])
                              for x in (-P.upper_bolt_x, P.upper_bolt_x)])


MAN_YC = (P.manifold[1][0] + P.manifold[1][1]) / 2.0
MAN_Z = 634.0


def manifold():
    m = P.manifold
    body = box_span(*m)
    ports = [cyl_x(14.0, s * m[0][1], s * (m[0][1] + 10.0), MAN_YC, MAN_Z) for s in (-1, 1)]
    return Part.makeCompound([body] + ports)


def sensor_brackets():
    out = []
    for rx in P.rows_x:
        y0 = P.bar_y + P.bar / 2.0
        plate = box_span((rx - 22.0, rx + 22.0), (y0, P.sensor_y + 22.0), (P.bar_z[1] - 20.0, P.bar_z[1] - 14.0))
        out.append(plate.cut(cyl_z(P.sensor[0] + 0.5, 600.0, 700.0, rx, P.sensor_y)))
    return Part.makeCompound(out)


def sensors():
    d, l = P.sensor
    out = []
    for rx in P.rows_x:
        z0 = P.bar_z[1] - 20.0 - 45.0
        body = cyl_z(d, z0, z0 + l, rx, P.sensor_y)
        nuts = [hex_prism_z(24.0, z, z + 5.0, rx, P.sensor_y).cut(cyl_z(d, z - 1, z + 6, rx, P.sensor_y))
                for z in (P.bar_z[1] - 25.0, P.bar_z[1] - 14.0)]
        out.append(fuse_all([body] + nuts))
    return Part.makeCompound(out)


def _pl_plate(y, z, holes_y):
    """Side plate (dx 26..34) with the two pivot holes."""
    p = box_span(P.plate_dx, y, z)
    return p.cut([cyl_x(P.pin_d + 0.4, 0, 100, holes_y, zz) for zz in P.pl_z])


def bracket_plates(rx):
    return row_shape(rx, _pl_plate(P.bracket_y, P.bracket_z, P.pl_y_bracket))


def bracket_pins(rx):
    return at_row(rx, Part.makeCompound([cyl_x(P.pin_d, -P.pin_dx, P.pin_dx, P.pl_y_bracket, z) for z in P.pl_z]))


def feed_hoses():
    """Manifold -> above each row unit (the flexible part to the head is in the row unit)."""
    return Part.makeCompound([hose([(s * (P.manifold[0][1] + 10.0), MAN_YC, MAN_Z), (rx, MAN_YC, MAN_Z),
                                    (rx, MAN_YC, 600.0)], 10.0)
                              for s, rx in ((-1, P.rows_x[0]), (1, P.rows_x[1]))])


# ---------------------------------------------------------------------
# Parallelogram arms (each link rotates about its bracket pin)
# ---------------------------------------------------------------------
def arm(rx, z):
    h = P.arm_h / 2.0
    bar = box_span(P.arm_dx, (P.pl_y_head - h, P.pl_y_bracket + h), (z - h, z + h))
    bar = bar.cut([cyl_x(P.pin_d + 0.4, 0, 100, y, z) for y in (P.pl_y_head, P.pl_y_bracket)])
    return row_shape(rx, bar)


# ---------------------------------------------------------------------
# Row unit (moves with the head)
# ---------------------------------------------------------------------
def head_plates(rx):
    return row_shape(rx, _pl_plate(P.head_y, (P.arch_z[1], P.pl_z[1] + 15.0), P.pl_y_head))


def head_pins(rx):
    return at_row(rx, Part.makeCompound([cyl_x(P.pin_d, -P.pin_dx, P.pin_dx, P.pl_y_head, z) for z in P.pl_z]))


def lifter_right():
    rod = hose([P.lifter_tip, P.lifter_mid, P.lifter_end], P.lifter_d)
    return fuse_all([rod, Part.makeSphere(P.lifter_d / 2.0 + 2.0, V(*P.lifter_tip))])


def arch(rx):
    """Welded arch: cross tube, two legs, corner gussets, leaf lifter rods."""
    zc = (P.arch_z[0] + P.arch_z[1]) / 2.0
    tube = square_tube_x(-P.arch_half, P.arch_half, 0.0, zc, P.arch, P.arch_wall)
    caps = [box_span((s * P.arch_half, s * (P.arch_half + 3.0)), (-P.arch / 2, P.arch / 2), P.arch_z) for s in (-1, 1)]
    leg = box_span(P.leg_dx, P.leg_y, (P.leg_z[0], P.arch_z[1]))
    g = P.gusset
    gus = poly_xz([(P.leg_dx[0], P.arch_z[0]), (P.leg_dx[0] - g, P.arch_z[0]), (P.leg_dx[0], P.arch_z[0] - g)], -4.0, 8.0)
    right = fuse_all([leg, gus, lifter_right()])
    s = fuse_all([tube] + caps + [right, mirror_x(right)])
    s.translate(V(rx, 0, 0))
    return s


def skid_right():
    sole = box_span(P.skid_dx, P.skid_y, (0.0, P.skid_t))
    y0, y1, zt = P.skid_nose
    nose = poly_yz([(y0, 0.0), (y1, zt - P.skid_t), (y1, zt), (y0, P.skid_t)], P.skid_dx[0], P.skid_dx[1] - P.skid_dx[0])
    return fuse_all([sole, nose])


def skids(rx):
    return row_shape(rx, skid_right())


def valve_bracket_right():
    yb = P.leg_y[0]
    p = box_span((P.valve_dx - 30.0, P.leg_dx[0]), (yb - P.vbr_t, yb), P.vbr_z)
    slot = box_span((P.valve_dx - 20.0, P.valve_dx + 20.0), (yb - P.vbr_t - 1, yb + 1),
                    (P.vbr_z[0] + 13.0, P.vbr_z[1] - 13.0))
    return p.cut(slot)


def valve_brackets(rx):
    return row_shape(rx, valve_bracket_right())


VALVE_Z = (P.valve_z0, P.valve_z0 + P.valve_body[2])


def valve_right():
    bx, by, bz = P.valve_body
    body = box_span((P.valve_dx - bx / 2, P.valve_dx + bx / 2), (P.nz_y - by / 2, P.nz_y + by / 2), VALVE_Z)
    coil = cyl_z(P.coil[0], VALVE_Z[1], VALVE_Z[1] + P.coil[1], P.valve_dx, P.nz_y)
    plug = box_span((P.valve_dx - 8, P.valve_dx + 8), (P.nz_y - by / 2 - 14, P.nz_y - by / 2),
                    (VALVE_Z[1] + 5, VALVE_Z[1] + P.coil[1] - 2))
    return fuse_all([body, coil, plug])


def valves(rx):
    return row_shape(rx, valve_right())


def tip_points():
    """Drop tube bottom (= tip start) and tip end, (dx, z) on the right side of the row."""
    a = math.radians(P.nozzle_angle)
    end = (P.valve_dx - P.tip_len * math.sin(a), P.tip_z)
    start = (P.valve_dx, P.tip_z + P.tip_len * math.cos(a))
    return start, end


def landing_dx():
    (sx, sz), (ex, ez) = tip_points()
    return ex - ez * math.tan(math.radians(P.nozzle_angle))


def nozzle_right():
    (sx, sz), (ex, ez) = tip_points()
    y = P.nz_y
    a = math.radians(P.nozzle_angle)
    drop = cyl_z(P.drop_d, sz, VALVE_Z[0], sx, y)
    tip = rod_between((sx, y, sz), (ex, y, ez), P.drop_d)
    cap = rod_between((ex + 6.0 * math.sin(a), y, ez + 6.0 * math.cos(a)), (ex, y, ez), 11.0)
    return fuse_all([drop, tip, Part.makeSphere(P.drop_d / 2.0, V(sx, y, sz)), cap])


def nozzles(rx):
    return row_shape(rx, nozzle_right())


def shroud_right():
    """Splash shroud: a short tube coaxial with the tip, 10 mm past it, clamped on the tip."""
    od, wall, length = P.shroud
    a = math.radians(P.nozzle_angle)
    (sx, sz), (ex, ez) = tip_points()
    d = V(-math.sin(a), 0, -math.cos(a))
    p_end = V(ex, P.nz_y, ez) + d * 10.0
    p0 = p_end - d * length
    outer = Part.makeCylinder(od / 2.0, length, p0, d)
    inner = Part.makeCylinder(od / 2.0 - wall, length + 2.0, p0 - d * 1.0, d)
    clamp = Part.makeCylinder(od / 2.0, 6.0, p0, d).cut(Part.makeCylinder(P.drop_d / 2.0 + 0.3, 30.0, p0 - d * 10.0, d))
    return fuse_all([outer.cut(inner), clamp])


def shrouds(rx):
    return row_shape(rx, shroud_right())


def unit_hose(rx):
    """Flexible hose from the toolbar to the head, tee on the arch, branches down to the valve inlets."""
    zt = P.arch_z[1] + 8.0
    yb = P.head_y[0] - 10.0         # behind the head plates
    trunk = hose([(0.0, MAN_YC, 600.0), (0.0, 20.0, 600.0), (0.0, 20.0, zt), (0.0, yb, zt)], 10.0)
    xb = P.valve_dx - 30.0
    vin = (VALVE_Z[0] + VALVE_Z[1]) / 2.0
    right = hose([(0.0, yb, zt), (xb, yb, zt), (xb, P.nz_y, zt), (xb, P.nz_y, vin),
                  (P.valve_dx - P.valve_body[0] / 2.0, P.nz_y, vin)], 10.0)
    s = fuse_all([trunk, right, mirror_x(right), Part.makeSphere(7.0, V(0.0, yb, zt))])
    s.translate(V(rx, 0, 0))
    return s


# ---------------------------------------------------------------------
# Crop and field (for the images)
# ---------------------------------------------------------------------
def cauliflower(x, y, h=P.plant_h, spread=P.plant_spread, seed=0):
    """Simple plant: stem, young curd, a ring of leaves rising outwards."""
    import random
    rnd = random.Random(seed)
    stem = cyl_z(P.stem_d, 0.0, 110.0, x, y)
    curd = Part.makeSphere(55.0, V(x, y, 120.0)).common(box_span((x - 60, x + 60), (y - 60, y + 60), (100.0, 200.0)))
    leaves = []
    n = 9
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.2, 0.2)
        r = spread / 2.0 * rnd.uniform(0.85, 1.0)
        top = h * rnd.uniform(0.85, 1.0)
        base = V(x + 20 * math.cos(a), y + 20 * math.sin(a), rnd.uniform(70.0, 110.0))
        mid = V(x + r * 0.55 * math.cos(a), y + r * 0.55 * math.sin(a), top)
        tip = V(x + r * math.cos(a), y + r * math.sin(a), top * 0.7)
        w = V(-math.sin(a), math.cos(a), 0) * 60.0
        for tri in ((base, mid - w, mid + w), (mid - w, tip, mid + w)):
            leaves.append(Part.Face(Part.makePolygon([tri[0], tri[1], tri[2], tri[0]])))
    return Part.makeCompound([stem, curd] + leaves)


def dose_spot(x, y, r=22.0):
    return cyl_z(2.0 * r, 0.5, 2.0, x, y)
