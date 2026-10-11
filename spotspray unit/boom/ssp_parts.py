"""Parts of the spot sprayer: one function per part, in robot coordinates, wings in the working position (phi = 0).
The left wing and the left actuator are the mirror images of the right ones (see mirror_x)."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ssp_params as P
import ssp_calc as C

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

HX, HZ = P.centre_half, P.hinge_z          # right hinge axis (x, z), along y
BY = P.boom_y


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


# ---------------------------------------------------------------------
# Tank and cradle
# ---------------------------------------------------------------------
def cradle_tubes():
    t, w = P.cradle_tube, P.cradle_wall
    out = []
    for y in P.cradle_y:
        tube = square_tube_x(-P.cradle_half_len, P.cradle_half_len, y, (P.cradle_z[0] + P.cradle_z[1]) / 2.0, t, w)
        holes = [cyl_z(P.m10_hole, P.cradle_z[0] - 1, P.cradle_z[1] + 1, x, y) for x in P.robot_upper_beam_x[1:3]]
        out.append(tube.cut(holes))
    return Part.makeCompound(out)


def cradle_pads():
    hx = P.robot_upper_beam_x[2] - 20.0          # between the bolt heads on the inner upper beams
    return Part.makeCompound([box_span((-hx, hx), (y - 18.0, y + 18.0), (P.cradle_z[1], P.tank_z0)) for y in P.cradle_y])


def cradle_bolts():
    """M10 button-head bolts through the cradle tube and the inner upper beams, nut under the beam."""
    out = []
    for y in P.cradle_y:
        for x in P.robot_upper_beam_x[1:3]:
            out.append(bolt_z(x, y, P.cradle_z[1], P.robot_upper_beam_z[0], k=4.0))
    return Part.makeCompound(out)


def straps():
    """Flat steel straps over the tank, with a foot on each end of the cradle tube."""
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
    """Liquid body for the given volume (for the animation)."""
    _, h = C.liquid_cg_z(litres)
    if h <= 0.5:
        return None
    z0 = P.tank_z0 + P.tank_wall
    return tank_inner().common(box_span((-P.tank_x, P.tank_x), P.tank_y, (z0, z0 + h)))


def tank_fittings():
    x, y, d, h = P.fill_cap
    z0 = P.tank_z[1]
    cap = fuse_all([cyl_z(d - 30.0, z0, z0 + h * 0.4, x, y), cyl_z(d, z0 + h * 0.4, z0 + h, x, y),
                    box_span((x - d / 2.0 + 10, x + d / 2.0 - 10), (y - 6, y + 6), (z0 + h, z0 + h + 10))])
    vx, vy, vd, vh = P.vent
    vent = fuse_all([cyl_z(vd, z0, z0 + vh, vx, vy), cyl_x(vd, vx - 30.0, vx + vd / 2.0, vy, z0 + vh - vd / 2.0)])
    bulk = [cyl_z(P.bulkhead[0], P.tank_z0 - P.bulkhead[1], P.tank_z0, xy[0], xy[1])
            for xy in (P.outlet_xy, P.return_xy)]
    return Part.makeCompound([cap, vent] + bulk)


def level_sensor():
    x, y, d, h = P.level_sensor
    z0 = P.tank_z[1]
    return fuse_all([cyl_z(d + 20.0, z0, z0 + 12.0, x, y), cyl_z(d, z0 + 12.0, z0 + h, x, y),
                     cyl_z(16.0, z0 + h, z0 + h + 20.0, x, y)])


# ---------------------------------------------------------------------
# Rear subframe: plate under the rear lower beams, 2 hanger webs, 2 clamp plates for the boom
# ---------------------------------------------------------------------
SUB_BOLTS = [(x, y) for x in P.sub_bolt_x for y in P.robot_lower_beam_y[:2]]


def sub_plate():
    p = box_span(P.sub_x, P.sub_y, P.sub_z)
    return p.cut([cyl_z(P.m10_hole, P.sub_z[0] - 1, P.sub_z[1] + 1, x, y) for (x, y) in SUB_BOLTS])


def hanger_web(sx):
    y_c = P.clamp_y[1]
    pts = [(P.sub_y[1] - 5.0, P.sub_z[0]), (y_c, P.sub_z[0]), (y_c, P.clamp_z[0] + 20.0), (y_c + 50.0, P.clamp_z[0] + 20.0),
           (P.sub_y[0], 580.0), (P.sub_y[1] - 5.0, 600.0)]
    return poly_yz(pts, sx * P.web_x - P.web_t / 2.0, P.web_t)


def clamp_plate(sx):
    x0, x1 = sx * (P.web_x - P.clamp_x), sx * (P.web_x + P.clamp_x)
    p = box_span((x0, x1), P.clamp_y, P.clamp_z)
    holes = [cyl_y(P.m10_hole, P.clamp_y[0] - 1, P.clamp_y[1] + 1, sx * (P.web_x + dx), zc + dz)
             for dx in (-25.0, 25.0) for dz in P.height_steps for zc in ((P.tube_z[0] + P.tube_z[1]) / 2.0,)]
    return p.cut(holes)


def hangers():
    return Part.makeCompound([fuse_all([hanger_web(s), clamp_plate(s)]) for s in (-1, 1)])


def sub_bolts():
    """8 x M10 through the control box base plate, the rear lower beams and the sub plate."""
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1] + P.box_base[2], P.sub_z[0]) for (x, y) in SUB_BOLTS])


def boom_bolts():
    """4 x M10 through the clamp plates and the centre tube (head in front, nut on the back of the tube)."""
    zc = (P.tube_z[0] + P.tube_z[1]) / 2.0
    return Part.makeCompound([bolt_y(sx * (P.web_x + dx), zc, P.clamp_y[1], BY - P.tube / 2.0)
                              for sx in (-1, 1) for dx in (-25.0, 25.0)])


# ---------------------------------------------------------------------
# Control box on the rear lower beams
# ---------------------------------------------------------------------
BOX_RAIL_Y = ((-525.0, -505.0), (-475.0, -455.0))
BOX_Z0 = P.robot_lower_beam_z[1] + P.box_base[2] + 20.0


def box_base():
    z = (P.robot_lower_beam_z[1], P.robot_lower_beam_z[1] + P.box_base[2])
    plate = box_span(P.box_base[0], P.box_base[1], z)
    holes = [cyl_z(P.m10_hole, z[0] - 1, z[1] + 1, x, y) for (x, y) in SUB_BOLTS]
    holes += [cyl_z(P.m10_hole, z[0] - 1, z[1] + 1, x, y) for x in P.box_bolt_x for y in P.robot_lower_beam_y[:2]]
    rails = [square_tube_x(P.box_x[0], P.box_x[1], (ry[0] + ry[1]) / 2.0, (z[1] + BOX_Z0) / 2.0, 20.0, 2.0)
             for ry in BOX_RAIL_Y]
    return fuse_all([plate.cut(holes)] + rails)


def box_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1] + P.box_base[2], P.robot_lower_beam_z[0])
                              for x in P.box_bolt_x for y in P.robot_lower_beam_y[:2]])


def control_box():
    body = box_span(P.box_x, P.box_y, (BOX_Z0, BOX_Z0 + P.box_h))
    lid = box_span((P.box_x[0] + 5, P.box_x[1] - 5), (P.box_y[0] + 5, P.box_y[1] - 5),
                   (BOX_Z0 + P.box_h, BOX_Z0 + P.box_h + 8.0))
    glands = [cyl_y(16.0, P.box_y[0] - 15.0, P.box_y[0], x, BOX_Z0 + 30.0) for x in (-150.0, -90.0, -30.0, 30.0, 90.0, 150.0)]
    return fuse_all([body, lid] + glands)


# ---------------------------------------------------------------------
# Pump, filter, regulator and hoses (under the rear lower beams)
# ---------------------------------------------------------------------
def pump():
    d, y0, y1, z = P.pump_motor
    head = box_span(*P.pump_head)
    motor = cyl_y(d, y0, y1, 0.0, z)
    ribs = [cyl_y(d + 6.0, y, y + 6.0, 0.0, z) for y in (y1 + 15.0, y1 + 90.0)]
    return fuse_all([head, motor] + ribs)


def pump_mounts():
    top = P.sub_z[0]
    a = box_span((-30.0, 30.0), (-490.0, -455.0), (P.pump_head[2][1], top))
    d, _, _, z = P.pump_motor
    b = box_span((-30.0, 30.0), P.pump_foot[1], (z + d / 2.0, top))
    c = box_span((50.0, 100.0), (-490.0, -460.0), (P.regulator[2][1], top))
    fx, fy = P.filter_xy
    f = box_span((fx - 25.0, fx + 25.0), (fy - 25.0, fy + 25.0), (P.filter_z[1], top))
    return Part.makeCompound([a, b, c, f])


def filter_bowl():
    fx, fy = P.filter_xy
    bowl = cyl_z(P.filter_d, P.filter_z[0], P.filter_z[1] - 15.0, fx, fy)
    head = cyl_z(P.filter_d + 10.0, P.filter_z[1] - 15.0, P.filter_z[1], fx, fy)
    return fuse_all([bowl, head])


def regulator():
    body = box_span(*P.regulator)
    (x0, x1), (y0, y1), (z0, z1) = P.regulator
    gauge = cyl_x(40.0, x1, x1 + 15.0, (y0 + y1) / 2.0, z1 - 25.0)
    knob = cyl_x(28.0, x1, x1 + 25.0, (y0 + y1) / 2.0, z0 + 22.0)
    return fuse_all([body, gauge, knob])


def suction_hose():
    ox, oy = P.outlet_xy
    fx, fy = P.filter_xy
    z0 = P.tank_z0 - P.bulkhead[1]
    a = hose([(ox, oy, z0), (ox, oy, P.hose_z), (fx, oy, P.hose_z), (fx, fy + P.filter_d / 2.0 + 6.0, P.hose_z)])
    b = hose([(fx + P.filter_d / 2.0 + 1.0, -475.0, P.port_z), (P.pump_head[0][0], -475.0, P.port_z)])
    return Part.makeCompound([a, b])


def return_hose():
    rx, ry = P.return_xy
    return hose([(P.feed_x, P.regulator[1][1], P.hose_z), (rx, ry, P.hose_z), (rx, ry, P.tank_z0 - P.bulkhead[1])])


def pressure_hose():
    y_end = BY + P.pipe_od / 2.0 + 0.5
    return hose([(P.feed_x, -475.0, P.regulator[2][0]), (P.feed_x, -475.0, P.pipe_z), (P.feed_x, y_end, P.pipe_z)])


# ---------------------------------------------------------------------
# Boom: centre section (fixed)
# ---------------------------------------------------------------------
TUBE_ZC = (P.tube_z[0] + P.tube_z[1]) / 2.0
LUG_Y = ((BY - P.lug_gap - P.lug_t, BY - P.lug_gap), (BY + P.lug_gap, BY + P.lug_gap + P.lug_t))


def centre_tube():
    x1 = P.centre_half - P.end_plate
    t = square_tube_x(-x1, x1, BY, TUBE_ZC, P.tube, P.tube_wall_centre)
    ends = [box_span((s * x1, s * P.centre_half), (BY - P.tube / 2, BY + P.tube / 2), P.tube_z) for s in (-1, 1)]
    holes = [cyl_y(P.m10_hole, BY - P.tube, BY + P.tube, sx * (P.web_x + dx), TUBE_ZC)
             for sx in (-1, 1) for dx in (-25.0, 25.0)]
    return fuse_all([t.cut(holes)] + ends)


def _lug_points():
    """Fixed hinge lug outline relative to the hinge axis (x, z): chamfered below the pin so the wing can fold."""
    return [(-60.0, -25.0), (-2.0, -25.0), (16.0, -8.0), (16.0, 6.0), (6.0, 18.0), (-60.0, 18.0)]


def hinge_lugs_right():
    pts = [(HX + x, HZ + z) for (x, z) in _lug_points()]
    out = []
    for y0, y1 in LUG_Y:
        out.append(poly_xz(pts, y0, y1 - y0).cut(cyl_y(P.hinge_pin_d, y0 - 1, y1 + 1, HX, HZ)))
    return Part.makeCompound(out)


def hinge_lugs():
    return both_sides(hinge_lugs_right())


def hinge_pins():
    def one(x):
        pin = cyl_y(P.hinge_pin_d, LUG_Y[0][0] - 4.0, LUG_Y[1][1] + 4.0, x, HZ)
        heads = [cyl_y(24.0, LUG_Y[0][0] - 8.0, LUG_Y[0][0] - 4.0, x, HZ),
                 cyl_y(24.0, LUG_Y[1][1] + 4.0, LUG_Y[1][1] + 8.0, x, HZ)]
        return fuse_all([pin] + heads)
    return Part.makeCompound([one(HX), one(-HX)])


ACT_B = P.act_base                     # right actuator base pin (x, z)
ACT_BRK_Y = LUG_Y


def act_brackets_right():
    bx, bz = ACT_B
    pts = [(bx - 22.0, P.tube_z[1]), (bx + 17.0, P.tube_z[1]), (bx + 17.0, bz)] + circle_pts(bx, bz, 14.0)
    pts.append((bx - 22.0, bz))
    return Part.makeCompound([plate_xz(pts, y0, y1 - y0, [(bx, bz, P.act_pin_d)]) for (y0, y1) in ACT_BRK_Y])


def act_brackets():
    return both_sides(act_brackets_right())


def act_base_pins():
    bx, bz = ACT_B

    def one(x):
        return fuse_all([cyl_y(P.act_pin_d, ACT_BRK_Y[0][0] - 3.0, ACT_BRK_Y[1][1] + 3.0, x, bz),
                         cyl_y(16.0, ACT_BRK_Y[0][0] - 6.0, ACT_BRK_Y[0][0] - 3.0, x, bz),
                         cyl_y(16.0, ACT_BRK_Y[1][1] + 3.0, ACT_BRK_Y[1][1] + 6.0, x, bz)])
    return Part.makeCompound([one(bx), one(-bx)])


RISER_C = P.centre_half - 25.0          # x of the centre riser (600)
RISER_W = P.centre_half + 25.0          # x of the wing riser (650)
SWIVEL_R = P.swivel[0] / 2.0


def centre_pipe():
    """Wet boom pipe of the centre section, with the risers to the hinge swivels at both ends."""
    xs = RISER_C
    ry = P.riser_y
    pts = [(HX - SWIVEL_R, ry, HZ), (xs, ry, HZ), (xs, ry, P.pipe_z), (xs, BY, P.pipe_z),
           (-xs, BY, P.pipe_z), (-xs, ry, P.pipe_z), (-xs, ry, HZ), (-HX + SWIVEL_R, ry, HZ)]
    return hose(pts, P.pipe_od)


def swivels():
    return Part.makeCompound([cyl_y(P.swivel[0], P.swivel[1], P.swivel[2], s * HX, HZ) for s in (-1, 1)])


def pipe_clip(x):
    r_o = P.pipe_od / 2.0 + 2.0
    ring = cyl_x(2 * r_o, x - 7.5, x + 7.5, BY, P.pipe_z).cut(cyl_x(P.pipe_od, x - 8, x + 8, BY, P.pipe_z))
    tab = box_span((x - 7.5, x + 7.5), (BY - 8.0, BY + 8.0), (P.pipe_z + r_o - 1.0, P.tube_z[0]))
    return fuse_all([ring, tab])


def centre_clips():
    return Part.makeCompound([pipe_clip(x) for x in P.clip_x])


def nozzle_body(x):
    """Clamp-on nozzle body with a PWM solenoid valve, cap and 40-degree flat-fan tip."""
    ring_o = P.nz_clamp[0]
    ring = cyl_x(ring_o, x - P.nz_clamp[1] / 2.0, x + P.nz_clamp[1] / 2.0, BY, P.pipe_z).cut(
        cyl_x(P.pipe_od, x - 20, x + 20, BY, P.pipe_z))
    s = P.nz_body[0] / 2.0
    body = box_span((x - s, x + s), (BY - s, BY + s), (P.nz_body[1], P.pipe_z - ring_o / 2.0 + 0.5))
    body = body.cut(cyl_x(P.pipe_od, x - 20, x + 20, BY, P.pipe_z))
    coil = cyl_y(P.nz_coil[0], BY - s - P.nz_coil[1], BY - s, x, P.nz_coil_z)
    plug = box_span((x - 8, x + 8), (BY - s - P.nz_coil[1] - 14.0, BY - s - P.nz_coil[1]),
                    (P.nz_coil_z - 9, P.nz_coil_z + 9))
    cap = cyl_z(P.nz_cap[0], P.nz_cap[1], P.nz_cap[2], x, BY)
    tip = cyl_z(P.nz_tip[0], P.nz_tip[1] + 4.0, P.nz_tip[2], x, BY)
    slot = box_span((x - 6, x + 6), (BY - 3, BY + 3), (P.nz_tip[1], P.nz_tip[1] + 4.0))
    return fuse_all([ring, body, coil, plug, cap, tip, slot])


def centre_nozzles():
    return Part.makeCompound([nozzle_body(x) for x in P.nozzle_x if abs(x) < P.centre_half])


# ---------------------------------------------------------------------
# Right wing (rotates about the hinge axis); left = mirror
# ---------------------------------------------------------------------
WING_X1 = P.centre_half + P.wing_len - 10.0         # 1865: tube end (the guard reaches to 1910)
WING_PIPE_END = 1820.0


def wing_tube_right():
    x0 = P.centre_half + P.wing_gap + P.end_plate
    t = square_tube_x(x0, WING_X1, BY, TUBE_ZC, P.tube, P.tube_wall_wing)
    plug = box_span((WING_X1 - 15.0, WING_X1), (BY - P.tube / 2 + P.tube_wall_wing, BY + P.tube / 2 - P.tube_wall_wing),
                    (P.tube_z[0] + P.tube_wall_wing, P.tube_z[1] - P.tube_wall_wing))
    return fuse_all([t, plug])


def wing_end_plate_right():
    x0 = P.centre_half + P.wing_gap
    return box_span((x0, x0 + P.end_plate), (BY - P.tube / 2, BY + P.tube / 2), P.tube_z)


def knuckle_right():
    """Wing knuckle and actuator lever in one plate (steel 12): pin hole on the hinge axis, lever pin 90 mm up-out."""
    lx, lz = P.lever_pin
    pts = circle_pts(HX, HZ, 16.0) + circle_pts(HX + lx, HZ + lz, 14.0)
    pts += [(HX + P.wing_gap, P.tube_z[1]), (HX + 110.0, P.tube_z[1]), (HX + 110.0, P.tube_z[1] + 13.0)]
    y0 = BY - P.knuckle_t / 2.0
    return plate_xz(pts, y0, P.knuckle_t, [(HX, HZ, P.hinge_pin_d), (HX + lx, HZ + lz, P.act_pin_d)])


def lever_pin_right():
    lx, lz = P.lever_pin
    x, z = HX + lx, HZ + lz
    return fuse_all([cyl_y(P.act_pin_d, BY - 15.0, BY + 15.0, x, z), cyl_y(16.0, BY - 18.0, BY - 15.0, x, z),
                     cyl_y(16.0, BY + 15.0, BY + 18.0, x, z)])


def wing_pipe_right():
    ry = P.riser_y
    pts = [(HX + SWIVEL_R, ry, HZ), (RISER_W, ry, HZ), (RISER_W, ry, P.pipe_z), (RISER_W, BY, P.pipe_z),
           (WING_PIPE_END, BY, P.pipe_z)]
    pipe = hose(pts, P.pipe_od)
    cap = cyl_x(P.pipe_od + 4.0, WING_PIPE_END, WING_PIPE_END + 8.0, BY, P.pipe_z)
    return fuse_all([pipe, cap])


def wing_clips_right():
    return Part.makeCompound([pipe_clip(x) for x in (875.0, 1125.0, 1375.0, 1625.0)])


def wing_nozzles_right():
    return Part.makeCompound([nozzle_body(x) for x in P.nozzle_x if x > P.centre_half])


def tip_guard_right():
    gx0 = WING_X1 - 20.0
    gx1 = P.guard_x[1] - P.guard_d / 2.0
    gz0 = P.guard_z[0] + P.guard_d / 2.0
    pts = [(gx0, BY, P.tube_z[0]), (gx0, BY, gz0), (gx1, BY, gz0), (gx1, BY, TUBE_ZC), (WING_X1, BY, TUBE_ZC)]
    return hose(pts, P.guard_d)


# ---------------------------------------------------------------------
# Fold actuator (right), drawn at phi = 0: horizontal from the base pin to the lever pin.
# Body part rotates about the base pin; the rod part slides along the axis inside the body part.
# ---------------------------------------------------------------------
L0 = C.act_length(0.0)


def _ux(u):
    return ACT_B[0] + u


def act_body_right():
    bx, bz = ACT_B
    eye = fuse_all([cyl_y(26.0, BY - 6.0, BY + 6.0, bx, bz),
                    box_span((bx, _ux(P.act_body_u[0])), (BY - 6.0, BY + 6.0), (bz - 10.0, bz + 10.0))])
    eye = eye.cut(cyl_y(P.act_pin_d, BY - 10, BY + 10, bx, bz))
    tube = cyl_x(P.act_body_d, _ux(P.act_body_u[0]), _ux(P.act_body_u[1]), BY, bz).cut(
        cyl_x(P.act_rod_d + 2.0, _ux(P.act_body_u[0] + 15.0), _ux(P.act_body_u[1]) + 1, BY, bz))
    d, u0, u1, off = P.act_motor
    motor = cyl_x(d, _ux(u0), _ux(u1), BY, bz + off)
    gear = box_span((_ux(P.act_body_u[0]), _ux(u0 + 15.0)), (BY - 20.0, BY + 20.0), (bz, bz + off + d / 2.0))
    return fuse_all([eye, tube, motor, gear])


def act_rod_right():
    bz = ACT_B[1]
    rod = cyl_x(P.act_rod_d, _ux(L0 - P.act_rod_len), _ux(L0 - 60.0), BY, bz)
    bridge = box_span((_ux(L0 - 60.0), _ux(L0 - 45.0)), (BY - 12.0, BY + 12.0), (bz - 14.0, bz + 14.0))
    prongs = [box_span((_ux(L0 - 45.0), _ux(L0)), (BY + s * 7.0, BY + s * 12.0), (bz - 14.0, bz + 14.0))
              for s in (-1, 1)]
    prongs += [cyl_y(28.0, BY + s * 7.0, BY + s * 12.0, _ux(L0), bz) for s in (-1, 1)]
    fork = fuse_all([rod, bridge] + prongs)
    return fork.cut(cyl_y(P.act_pin_d, BY - 15, BY + 15, _ux(L0), bz))


# ---------------------------------------------------------------------
# Camera mast at the front
# ---------------------------------------------------------------------
MAST_BOLTS = [(x, y) for x in P.mast_plate_bolt_x for y in P.robot_lower_beam_y[2:]]
MX, MY = P.mast_xy
MS = P.mast_tube / 2.0


def mast_plate():
    (x0, x1), (y0, y1), (z0, z1) = P.mast_plate
    ya, yb, xn = P.mast_plate_taper
    p = poly_xy([(x0, y0), (x1, y0), (x1, ya), (xn, yb), (xn, y1), (-xn, y1), (-xn, yb), (x0, ya)], z0, z1 - z0)
    p = p.cut(box_span(P.mast_plate_window[0], P.mast_plate_window[1], (z0 - 1, z1 + 1)))
    holes = [cyl_z(P.m10_hole, z0 - 1, z1 + 1, x, y) for (x, y) in MAST_BOLTS]
    holes.append(cyl_z(P.gnss_clear_hole, z0 - 1, z1 + 1, P.robot_gnss[0], P.robot_gnss[1]))
    return p.cut(holes)


def brace_foot(sx):
    x, y, z = P.brace_foot
    foot = box_span((sx * (x - 25.0), sx * (x + 25.0)), (y - 20.0, y + P.brace_end_dy + 20.0), (z, z + 6.0))
    return foot.cut(cyl_z(P.m10_hole, z - 1, z + 7, sx * x, y))


def mast_bolts():
    out = []
    for (x, y) in MAST_BOLTS:
        top = P.robot_lower_beam_z[1] + (6.0 if (abs(x) == P.brace_foot[0] and y == P.brace_foot[1]) else 0.0)
        out.append(bolt_z(x, y, top, P.mast_plate[2][0]))
    return Part.makeCompound(out)


def mast_tube():
    t = square_tube_z(P.mast_z[0], P.mast_z[1], MX, MY, P.mast_tube, P.mast_wall)
    cap = box_span((MX - 40.0, MX + 40.0), (MY - 40.0, MY + 40.0), (P.mast_z[1], P.mast_z[1] + P.cap_t))
    return fuse_all([t, cap])


def mast_gussets():
    z0 = P.mast_z[0]
    t = P.gusset_t
    side = [poly_xz([(s * MS, z0), (s * 75.0, z0), (s * MS, z0 + 140.0)], MY - t / 2.0, t) for s in (-1, 1)]
    front = poly_yz([(MY + MS, z0), (P.mast_plate[1][1], z0), (MY + MS, z0 + 80.0)], MX - t / 2.0, t)
    return Part.makeCompound(side + [front])


def braces():
    out = []
    x, y, z = P.brace_foot
    for s in (-1, 1):
        a = V(s * (MS + 13.0), MY, P.brace_top_z)
        f = V(s * x, y + P.brace_end_dy, z + 6.0 + 9.0)
        out.append(rod_between(a, f, P.brace_d))
        out.append(brace_foot(s))
        ear = box_span((s * MS, s * (MS + 13.0)), (MY - 15.0, MY + 15.0), (P.brace_top_z - 20.0, P.brace_top_z + 20.0))
        out.append(ear)
    return Part.makeCompound(out)


def camera_arms():
    (ax0, ax1), (ay0, ay1), (az0, az1) = P.cam_arm
    return Part.makeCompound([box_span((s * ax0, s * ax1), (ay0, ay1), (az0, az1)) for s in (-1, 1)])


def _camera_local():
    """Camera housing with lens and hood, optical axis along +y, origin = tilt pivot."""
    bx, by, bz = P.cam_box
    body = box_span((-bx / 2, bx / 2), (-by / 2, by / 2), (-bz / 2, bz / 2))
    lens = cyl_y(P.cam_lens[0], by / 2, by / 2 + P.cam_lens[1], 0.0, 0.0)
    glass = cyl_y(P.cam_lens[0] - 8.0, by / 2 + P.cam_lens[1], by / 2 + P.cam_lens[1] + 2.0, 0.0, 0.0)
    hw, hl, ht = P.cam_hood
    hood = box_span((-hw / 2, hw / 2), (-by / 2, -by / 2 + hl), (bz / 2, bz / 2 + ht))
    bosses = [cyl_x(20.0, s * bx / 2, s * P.cam_arm[0][0], 0.0, 0.0) for s in (-1, 1)]
    gland = cyl_y(14.0, -by / 2 - 15.0, -by / 2, 0.0, -15.0)
    return fuse_all([body, lens, hood, gland] + bosses), glass


def _place_camera(shape):
    s = shape.copy()
    s.rotate(V(0, 0, 0), X, -P.cam_pitch)
    s.translate(V(*P.cam_pivot))
    return s


def camera():
    return _place_camera(_camera_local()[0])


def camera_glass():
    return _place_camera(_camera_local()[1])


def antenna():
    """The robot's GNSS antenna, moved from the front beam to the top of the mast (5/8" adapter)."""
    z0 = P.mast_z[1] + P.cap_t
    stem = cyl_z(P.ant_stem[0], z0, z0 + P.ant_stem[1], MX, MY)
    d, h = P.ant_dome
    zb = z0 + P.ant_stem[1]
    base = cyl_z(d, zb, zb + 10.0, MX, MY)
    dome = Part.makeSphere(d / 2.0, V(0, 0, 0))
    m = App.Matrix()
    m.scale(1.0, 1.0, (h - 10.0) / (d / 2.0))
    dome = dome.transformGeometry(m)
    dome.translate(V(MX, MY, zb + 10.0))
    dome = dome.common(box_span((MX - d, MX + d), (MY - d, MY + d), (zb + 10.0, zb + h + 1)))
    return fuse_all([stem, base, dome])


# ---------------------------------------------------------------------
# Field objects for the animation and the renders
# ---------------------------------------------------------------------
def dock(x, y, d, h, seed=0):
    """Broad-leaved dock rosette: a ring of flat leaves (ellipsoids) and a few upright ones."""
    import random
    rnd = random.Random(seed)
    leaves = []
    n = 7
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
        ln = d / 2.0 * rnd.uniform(0.75, 1.0)
        leaf = Part.makeSphere(1.0)
        m = App.Matrix()
        m.scale(ln / 2.0, ln / 6.0, 6.0)
        leaf = leaf.transformGeometry(m)
        leaf.rotate(V(0, 0, 0), Y, -rnd.uniform(15.0, 40.0))
        leaf.translate(V(ln / 2.0, 0, 0))
        leaf.rotate(V(0, 0, 0), Z, math.degrees(a))
        leaves.append(leaf)
    for i in range(3):
        a = 2 * math.pi * i / 3 + rnd.uniform(-0.4, 0.4)
        leaf = Part.makeSphere(1.0)
        m = App.Matrix()
        m.scale(h / 2.0, d / 10.0, 5.0)
        leaf = leaf.transformGeometry(m)
        leaf.rotate(V(0, 0, 0), Y, -rnd.uniform(55.0, 75.0))
        leaf.translate(V(h / 4.0, 0, h / 3.0))
        leaf.rotate(V(0, 0, 0), Z, math.degrees(a))
        leaves.append(leaf)
    c = Part.makeCompound(leaves)
    c.translate(V(x, y, 5.0))
    return c


def post(x, y, d=150.0, h=1500.0):
    return cyl_z(d, 0.0, h, x, y)


def spray_fan(x, y, z_tip=P.nozzle_h, angle=P.nozzle_angle, t=12.0):
    """Flat fan from the nozzle tip to the ground (thin wedge across the boom)."""
    w = z_tip * math.tan(math.radians(angle / 2.0))
    return poly_xz([(x, z_tip), (x - w, 1.0), (x + w, 1.0)], y - t / 2.0, t)


def patch(x0, x1, y0, y1, z=1.0, t=0.6):
    return box_span((x0, x1), (y0, y1), (z, z + t))


def ring(x, y, d, w=12.0, z=2.0, t=1.0):
    return cyl_z(d + w, z, z + t, x, y).cut(cyl_z(d - w, z - 1, z + t + 1, x, y))


def ground_polygon(points, z=1.5, t=0.5):
    pts = [V(px, py, z) for (px, py) in points]
    return _poly(pts).extrude(V(0, 0, t))
