"""Parts of the propane flame weeder: one function per part, in robot coordinates (hood down on its castors). Flames,
seedbed and weed shapes for the renders and the animation are at the end."""
import math
import random

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import flw_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)
HX = P.hood_x
HY0, HY1 = P.hood_y
HZ = P.hood_h
T = P.skin
Z_COVER = HZ + P.cover_gap                       # underside of the aluminium top cover


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


def poly_xy(points, z0, t):
    return _poly([V(x, y, z0) for (x, y) in points]).extrude(V(0, 0, t))


def poly_yz(points, x0, t):
    return _poly([V(x0, y, z) for (y, z) in points]).extrude(V(t, 0, 0))


def tube_y(y0, y1, x, z, w, h, wall):
    o = box_span((x - w / 2, x + w / 2), (y0, y1), (z - h / 2, z + h / 2))
    i = box_span((x - w / 2 + wall, x + w / 2 - wall), (y0 - 1, y1 + 1), (z - h / 2 + wall, z + h / 2 - wall))
    return o.cut(i)


def tube_x(x0, x1, y, z, w, h, wall):
    o = box_span((x0, x1), (y - w / 2, y + w / 2), (z - h / 2, z + h / 2))
    i = box_span((x0 - 1, x1 + 1), (y - w / 2 + wall, y + w / 2 - wall), (z - h / 2 + wall, z + h / 2 - wall))
    return o.cut(i)


def hex_prism_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    return _poly(pts).extrude(V(0, 0, z1 - z0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    head = hex_prism_z(af, z_head, z_head + k, x, y)
    shank = cyl_z(d, z_nut - m - 4.0, z_head, x, y)
    nut = hex_prism_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))
    return fuse_all([head, shank, nut])


def pin_x(x0, x1, y, z, d=P.pin_d):
    return fuse_all([cyl_x(d, x0 - 4.0, x1 + 4.0, y, z), cyl_x(d + 10.0, x1 + 4.0, x1 + 8.0, y, z),
                     cyl_x(d + 8.0, x0 - 6.0, x0 - 4.0, y, z)])


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both_sides(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


def tube_path(points, d):
    """Pipe or hose along a polyline, a ball at every bend."""
    pts = [V(*p) for p in points]
    parts = [Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a) for a, b in zip(pts[:-1], pts[1:])
             if (b - a).Length > 1e-6]
    parts += [Part.makeSphere(d / 2.0, p) for p in pts[1:-1]]
    return fuse_all(parts)


# ---------------------------------------------------------------------
# Hood
# ---------------------------------------------------------------------
def hood_skin():
    """1.5 mm steel: top, two side walls, front wall (down to hood_gap), rear wall (down to exhaust_gap)."""
    top = box_span((-HX, HX), (HY0, HY1), (HZ - T, HZ))
    sides = [box_span((s * HX - (T if s > 0 else 0.0), s * HX + (0.0 if s > 0 else T)), (HY0, HY1), (P.hood_gap, HZ))
             for s in (1, -1)]
    front = box_span((-HX, HX), (HY1 - T, HY1), (P.hood_gap, HZ))
    rear = box_span((-HX, HX), (HY0, HY0 + T), (P.exhaust_gap, HZ))
    return fuse_all([top] + sides + [front, rear])


def blanket():
    return box_span((-HX + T, HX - T), (HY0 + T, HY1 - T), (HZ - T - P.blanket, HZ - T))


def top_cover():
    """Aluminium 0.8 mm on 15 mm spacers, a little larger than the skin."""
    cov = box_span((-HX, HX), (HY0 - 10.0, HY1 + 10.0), (Z_COVER, Z_COVER + P.cover))
    spacers = [cyl_z(16.0, HZ, Z_COVER, x, y) for x in (-HX + 60.0, 0.0, HX - 60.0)
               for y in (HY0 + 60.0, (HY0 + HY1) / 2.0, HY1 - 60.0)]
    return fuse_all([cov] + spacers)


def ribs():
    """Angles 30 x 30 x 3 along the top edges of the side walls (outside) - they also carry the castor arms."""
    a, b, t = P.rib
    out = []
    for s in (1, -1):
        x0 = s * HX
        h = box_span((x0, x0 + s * a), (HY0, HY1), (HZ - t, HZ))
        v = box_span((x0, x0 + s * t), (HY0, HY1), (HZ - b, HZ))
        out.append(fuse_all([h, v]))
    return Part.makeCompound(out)


def front_shield():
    t, gap = P.front_shield
    y0 = HY1 + gap
    sh = box_span((-HX, HX), (y0, y0 + t), (P.hood_gap, P.shield_top))
    clips = [box_span((x - 15.0, x + 15.0), (HY1, y0), (P.shield_top - 40.0, P.shield_top - 10.0))
             for x in (-HX + 80.0, -250.0, 250.0, HX - 80.0)]
    return fuse_all([sh] + clips)


def hood_bracket():
    """Bracket on the front of the hood top (bolted to the skin through the cover) with the two lugs of the
    parallelogram."""
    base = box_span((-90.0, 90.0), (HY1 - 90.0, HY1 + 40.0), (Z_COVER + P.cover, Z_COVER + P.cover + 8.0))
    post = box_span((-30.0, 30.0), (HY1 - 90.0, HY1 - 60.0), (HZ, Z_COVER + P.cover))
    lugs = []
    zb = Z_COVER + P.cover + 8.0
    for sx in (-1, 1):
        x = sx * P.hood_lug_x
        lug = poly_yz([(HY1 - 80.0, zb), (HY1 + 40.0, zb), (P.pin_hood_y + 25.0, P.pin_z[0] + 25.0),
                       (P.pin_hood_y - 25.0, P.pin_z[0] + 25.0)], x - 4.0, 8.0)
        for z in P.pin_z:
            lug = lug.cut(cyl_x(P.pin_d + 0.5, x - 10, x + 10, P.pin_hood_y, z))
        lugs.append(lug)
    return fuse_all([base, post] + lugs)


def hood_pins():
    x0, x1 = P.hood_lug_x - 4.0, P.arm_x + P.arm_tube[0] / 2.0
    return Part.makeCompound([pin_x(x0, x1, P.pin_hood_y, z) if s > 0 else mirror_x(pin_x(x0, x1, P.pin_hood_y, z))
                              for z in P.pin_z for s in (-1, 1)])


# ---------------------------------------------------------------------
# Burners, manifold, pilots, vaporiser coil
# ---------------------------------------------------------------------
def _burner_frame():
    a = math.radians(P.burner_angle)
    axis = V(0, -math.cos(a), -math.sin(a))          # flame direction: back and down
    return axis


def burners():
    """Flat-flame burner: a wedge body that widens to the mouth (210 mm), on a feed tube from the manifold."""
    axis = _burner_frame()
    out = []
    w, L, h = P.burner_body
    for x in P.burner_x:
        mouth = V(x, P.burner_y, P.burner_z)
        back = mouth - axis * L
        # body built along -y, then turned down about x
        body = _poly([V(x - 20.0, 0, -h / 2.0), V(x + 20.0, 0, -h / 2.0), V(x + w / 2.0, -L, -h / 4.0),
                      V(x - w / 2.0, -L, -h / 4.0)]).extrude(V(0, 0, h * 0.75))
        body = body.fuse(box_span((x - w / 2.0, x + w / 2.0), (-L - 6.0, -L), (-h / 4.0, h / 2.0)))
        body.rotate(V(0, 0, 0), X, P.burner_angle)
        body.translate(V(0, back.y, back.z))
        out.append(body)
    return Part.makeCompound(out)


def burner_feeds():
    axis = _burner_frame()
    out = []
    for x in P.burner_x:
        back = V(x, P.burner_y, P.burner_z) - axis * P.burner_body[1]
        out.append(tube_path([(x, P.manifold_y, P.manifold_z), (x, back.y + 5.0, P.manifold_z), (x, back.y, back.z)], 12.0))
    return Part.makeCompound(out)


def manifold():
    x0, x1 = P.burner_x[0] - 40.0, P.burner_x[-1] + 40.0
    pipe = cyl_x(P.manifold_d, x0, x1, P.manifold_y, P.manifold_z)
    caps = [cyl_x(P.manifold_d + 4.0, x - 6.0, x, P.manifold_y, P.manifold_z) for x in (x0 + 6.0,)] + \
           [cyl_x(P.manifold_d + 4.0, x1 - 6.0, x1, P.manifold_y, P.manifold_z)]
    feed = tube_path([(P.manifold_feed_x, P.manifold_y, P.manifold_z), (P.manifold_feed_x, P.manifold_y, HZ + 5.0)],
                     14.0)
    clamps = [box_span((x - 15.0, x + 15.0), (HY1 - T - 40.0, HY1 - T), (P.manifold_z - 14.0, P.manifold_z + 14.0))
              for x in (-500.0, 0.0, 500.0)]
    return fuse_all([pipe, feed] + caps + clamps)


def pilots():
    """Pilot tube and spark igniter beside each burner mouth (with the thermocouple flame sensor)."""
    axis = _burner_frame()
    out = []
    for x in P.burner_x:
        m = V(x, P.burner_y, P.burner_z)
        p0 = m - axis * 50.0 + V(P.burner_body[0] / 2.0 + 14.0, 0, 0)
        out.append(Part.makeCylinder(P.pilot[0] / 2.0, P.pilot[1] + 10.0, p0, axis))
        i0 = m - axis * 60.0 + V(-P.burner_body[0] / 2.0 - 12.0, 0, 6.0)
        out.append(Part.makeCylinder(P.igniter[0] / 2.0, P.igniter[1], i0, axis))
    return Part.makeCompound(out)


def coil():
    """Vaporiser: stainless tube serpentine in the hot gas under the blanket, in and out through the top."""
    pts = []
    for k in range(P.coil_passes):
        y = P.coil_y0 - k * P.coil_pitch
        xs = (-P.coil_x, P.coil_x) if k % 2 == 0 else (P.coil_x, -P.coil_x)
        pts += [(xs[0], y, P.coil_z), (xs[1], y, P.coil_z)]
    yi, yo = P.coil_y0 + 30.0, pts[-1][1]
    path = [(60.0, yi, HZ + 5.0), (60.0, yi, P.coil_z), (-P.coil_x, yi, P.coil_z)] + pts + [(pts[-1][0], yo, HZ + 5.0)]
    return tube_path(path, P.coil_d)


def hood_gas_train():
    """On the hood top, behind the shield: regulator (motorised), pressure sensor, burner solenoid, pilot valve,
    hoses from the coil outlet to the manifold feed."""
    z = Z_COVER + P.cover
    y = HY1 - 160.0
    reg = cyl_x(P.regulator[0], 150.0, 150.0 + P.regulator[1], y, z + 45.0)
    reg_motor = box_span((165.0, 195.0), (y - 25.0, y + 25.0), (z + 80.0, z + 120.0))
    valves = [box_span((x - P.valve[0] / 2.0, x + P.valve[0] / 2.0), (y - P.valve[1] / 2.0, y + P.valve[1] / 2.0),
                       (z, z + P.valve[2])) for x in (-120.0, -200.0)]
    sensor = cyl_z(22.0, z, z + 55.0, -60.0, y)
    return fuse_all([reg, reg_motor, sensor] + valves)


def hood_hoses():
    z = Z_COVER + P.cover + 25.0
    y = HY1 - 160.0
    xo = P.coil_x if P.coil_passes % 2 == 0 else -P.coil_x
    yo = P.coil_y0 - (P.coil_passes - 1) * P.coil_pitch
    a = tube_path([(-xo, yo, Z_COVER + P.cover), (-xo, yo, z), (210.0 + 20.0, y, z)], P.hose_d)
    b = tube_path([(150.0, y, z + 20.0), (-100.0, y, z + 20.0)], P.hose_d)
    fx = P.manifold_feed_x
    c = tube_path([(-220.0, y, z + 20.0), (fx, y, z + 20.0), (fx, P.manifold_y, z + 20.0),
                   (fx, P.manifold_y, Z_COVER + P.cover)], P.hose_d)
    return Part.makeCompound([a, b, c])


# ---------------------------------------------------------------------
# Castors: steel wheels, swivel, arms from the side ribs
# ---------------------------------------------------------------------
YS = P.caster_y + P.caster_offset


def castor_arms():
    s, _, wall = P.caster_arm
    out = []
    for sx in (1, -1):
        x0 = sx * HX
        x1 = sx * (P.caster_x + 30.0)
        arm = tube_x(min(x0, x1), max(x0, x1), YS, HZ + s / 2.0, s, s, wall)          # on top of the rib
        post = box_span((sx * P.caster_x - 20.0, sx * P.caster_x + 20.0), (YS - 20.0, YS + 20.0),
                        (P.caster_h + 6.0, HZ))
        out.append(fuse_all([arm, post]))
    return Part.makeCompound(out)


def castors():
    out = []
    yw = P.caster_y
    az = P.caster_d / 2.0
    for sx in (1, -1):
        x = sx * P.caster_x
        plate = box_span((x - 45.0, x + 45.0), (YS - 45.0, YS + 45.0), (P.caster_h, P.caster_h + 6.0))
        swivel = cyl_z(65.0, P.caster_h - 18.0, P.caster_h, x, YS)
        fork = []
        for s in (-1, 1):
            fork.append(poly_yz([(YS - 20.0, P.caster_h - 18.0), (YS + 20.0, P.caster_h - 18.0), (yw + 15.0, az - 12.0),
                                 (yw - 15.0, az - 12.0)], x + s * (P.caster_w / 2.0 + 4.0) - (4.0 if s > 0 else 0.0),
                                4.0))
        axle = cyl_x(12.0, x - P.caster_w / 2.0 - 10.0, x + P.caster_w / 2.0 + 10.0, yw, az)
        wheel = cyl_x(P.caster_d, x - P.caster_w / 2.0, x + P.caster_w / 2.0, yw, az).cut(
            cyl_x(P.caster_d - 40.0, x - P.caster_w / 2.0 + 8.0, x + P.caster_w / 2.0 - 8.0, yw, az))
        wheel = wheel.fuse(cyl_x(40.0, x - P.caster_w / 2.0, x + P.caster_w / 2.0, yw, az))
        out.append((fuse_all([plate, swivel] + fork + [axle]), wheel))
    return out


def castor_frames():
    return Part.makeCompound([c[0] for c in castors()])


def castor_wheels():
    return Part.makeCompound([c[1] for c in castors()])


# ---------------------------------------------------------------------
# Mount on the robot: sub plate under the rear lower beams, headstock, parallelogram arms
# ---------------------------------------------------------------------
def sub_plate():
    (x0, x1), (y0, y1), (z0, z1) = P.sub_plate
    pl = box_span((x0, x1), (y0, y1), (z0, z1))
    for x in P.sub_bolt_x:
        for y in (P.robot_lower_beam_y[0], P.robot_lower_beam_y[1]):
            pl = pl.cut(cyl_z(P.m10_hole, z0 - 1, z1 + 1, x, y))
    pl = pl.cut(box_span((-40.0, 40.0), (-530.0, -470.0), (z0 - 1, z1 + 1)))     # hose passage
    return pl


def sub_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], P.sub_plate[2][0]) for x in P.sub_bolt_x
                              for y in (P.robot_lower_beam_y[0], P.robot_lower_beam_y[1])])


def headstock():
    z1 = P.sub_plate[2][0]
    out = []
    for sx in (-1, 1):
        x = sx * P.stock_x
        y0, y1 = P.stock_y
        pl = poly_yz([(y1, z1), (y0, z1), (P.pin_rear_y - 35.0, P.pin_z[1] - 30.0), (P.pin_rear_y + 35.0,
                                                                                    P.pin_z[1] - 30.0)],
                     x - P.stock_t / 2.0, P.stock_t)
        for z in P.pin_z:
            pl = pl.cut(cyl_x(P.pin_d + 0.5, x - 10, x + 10, P.pin_rear_y, z))
        out.append(pl)
    return Part.makeCompound(out)


def stock_pins():
    x0, x1 = P.arm_x - P.arm_tube[0] / 2.0, P.stock_x + P.stock_t / 2.0
    return Part.makeCompound([pin_x(x0, x1, P.pin_rear_y, z) if s > 0 else mirror_x(pin_x(x0, x1, P.pin_rear_y, z))
                              for z in P.pin_z for s in (-1, 1)])


def arm_pair(z, cross=False):
    w, h, wall = P.arm_tube
    out = []
    for sx in (-1, 1):
        x = sx * P.arm_x
        a = tube_y(P.pin_hood_y - 22.0, P.pin_rear_y + 22.0, x, z, w, h, wall)
        for y in (P.pin_rear_y, P.pin_hood_y):
            a = a.cut(cyl_x(P.pin_d + 0.5, x - 30, x + 30, y, z))
            a = a.fuse(cyl_x(P.pin_d + 12.0, x - w / 2.0, x + w / 2.0, y, z).cut(
                cyl_x(P.pin_d + 0.5, x - 30, x + 30, y, z)))
        out.append(a)
    if cross:
        yc = (P.pin_rear_y + P.pin_hood_y) / 2.0
        out.append(box_span((-P.arm_x + w / 2.0, P.arm_x - w / 2.0), (yc - 20.0, yc + 20.0), (z - 20.0, z + 20.0)))
    return fuse_all(out)


def upper_arms():
    return arm_pair(P.pin_z[0])


def lower_arms():
    return arm_pair(P.pin_z[1], cross=True)


def robot_gas_train():
    """Under the sub plate between the headstock plates: liquid filter and two main solenoid valves in series."""
    z1 = P.sub_plate[2][0]
    y0, y1 = P.panel_y
    bracket = box_span((-70.0, 70.0), (y0, y1), (z1 - 6.0, z1))
    filt = cyl_z(45.0, z1 - 110.0, z1 - 6.0, -40.0, (y0 + y1) / 2.0)
    valves = [box_span((x - P.valve[0] / 2.0, x + P.valve[0] / 2.0), ((y0 + y1) / 2.0 - P.valve[1] / 2.0,
                                                                         (y0 + y1) / 2.0 + P.valve[1] / 2.0),
                       (z1 - 6.0 - P.valve[2], z1 - 6.0)) for x in (10.0, 55.0)]
    return fuse_all([bracket, filt] + valves)


def robot_hoses():
    """Liquid hoses: cylinder valves -> through the gap between the rear beams -> filter; valves -> along the upper
    arm -> vaporiser inlet on the hood."""
    yc = (P.panel_y[0] + P.panel_y[1]) / 2.0
    z1 = P.sub_plate[2][0]
    out = []
    zc = cyl_axis_z()
    for x in P.cyl_x:
        out.append(tube_path([(x, P.cyl_y[0] - 40.0, zc - 60.0), (x, -500.0, zc - 60.0), (x * 0.25, -500.0, z1 + 30.0),
                              (-40.0 if x < 0 else -20.0, -500.0, z1 + 30.0), (-40.0 if x < 0 else -20.0, -500.0, z1)],
                             P.hose_d))
    yi = P.coil_y0 + 30.0
    y_front = P.stock_y[1] + 25.0                      # in front of the headstock plates
    out.append(tube_path([(75.0, yc, z1 - 50.0), (75.0, y_front, z1 - 50.0), (110.0, y_front, z1 - 50.0),
                          (110.0, P.pin_rear_y + 40.0, P.pin_z[0] + 40.0),
                          (110.0, P.pin_hood_y - 40.0, P.pin_z[0] + 40.0), (60.0, yi, Z_COVER + 60.0),
                          (60.0, yi, Z_COVER + P.cover)], P.hose_d))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Gas cylinders on the cradle
# ---------------------------------------------------------------------
def cyl_axis_z():
    return P.robot_upper_beam_z[1] + P.cradle[0] + P.saddle_t + P.cyl_d / 2.0


def cradle():
    h, w, t = P.cradle
    z0 = P.robot_upper_beam_z[1]
    out = []
    for y in P.cradle_y:
        ch = box_span((-P.cradle_half, P.cradle_half), (y - w / 2.0, y + w / 2.0), (z0, z0 + h)).cut(
            box_span((-P.cradle_half - 1, P.cradle_half + 1), (y - w / 2.0 + t, y + w / 2.0 - t), (z0 + t, z0 + h + 1)))
        for x in (P.robot_upper_beam_x[1], P.robot_upper_beam_x[2]):
            ch = ch.cut(cyl_z(P.m10_hole, z0 - 1, z0 + t + 1, x, y))
        out.append(ch)
    return Part.makeCompound(out)


def saddles():
    """Rubber-lined saddles on the channels (a round cut for each cylinder)."""
    zc = cyl_axis_z()
    z0 = P.robot_upper_beam_z[1] + P.cradle[0]
    out = []
    for y in P.cradle_y:
        for x in P.cyl_x:
            s = box_span((x - 110.0, x + 110.0), (y - 30.0, y + 30.0), (z0, zc - 60.0))
            s = s.cut(cyl_y(P.cyl_d, y - 31, y + 31, x, zc))
            out.append(s)
    return Part.makeCompound(out)


def cradle_bolts():
    z0 = P.robot_upper_beam_z[1]
    out = []
    for y in P.cradle_y:
        for x in (P.robot_upper_beam_x[1], P.robot_upper_beam_x[2]):
            out.append(bolt_z(x, y, z0 + P.cradle[2], P.robot_upper_beam_z[0]))
    return Part.makeCompound(out)


def straps():
    zc = cyl_axis_z()
    r = P.cyl_d / 2.0
    w, t = P.strap
    out = []
    for y in P.cradle_y:
        for x in P.cyl_x:
            band = cyl_y(P.cyl_d + 2 * t, y - w / 2.0, y + w / 2.0, x, zc).cut(cyl_y(P.cyl_d, y - w, y + w, x, zc))
            band = band.cut(box_span((x - r - 10, x + r + 10), (y - w, y + w), (zc - r - 10, zc - 40.0)))
            out.append(band)
    return Part.makeCompound(out)


def cylinders():
    """Forklift cylinders: body with rounded ends, collar and valve at the rear (valve end)."""
    zc = cyl_axis_z()
    r = P.cyl_d / 2.0
    out = []
    for x in P.cyl_x:
        y0, y1 = P.cyl_y
        body = cyl_y(P.cyl_d, y0 + 20.0, y1, x, zc)
        edges = [e for e in body.Edges if e.Curve.__class__.__name__ == "Circle"]
        body = body.makeFillet(70.0, edges)
        out.append(body)
    return Part.makeCompound(out)


def collars():
    zc = cyl_axis_z()
    out = []
    for x in P.cyl_x:
        y0 = P.cyl_y[0]
        c = cyl_y(P.collar[0], y0 - P.collar[1] + 60.0, y0 + 60.0, x, zc).cut(
            cyl_y(P.collar[0] - 6.0, y0 - P.collar[1] + 59.0, y0 + 61.0, x, zc))
        c = c.cut(box_span((x - 40.0, x + 40.0), (y0 - P.collar[1] + 59.0, y0 + 61.0), (zc + 40.0, zc + 120.0)))
        valve = cyl_y(30.0, y0 - 40.0, y0 + 25.0, x, zc - 60.0).fuse(cyl_z(26.0, zc - 60.0, zc - 20.0, x, y0 - 10.0))
        out.append(fuse_all([c, valve]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Scene: flames, seedbed, weeds (alive and scorched)
# ---------------------------------------------------------------------
def flame(x, scale=1.0):
    """Flame of one burner: a flattened wedge from the mouth, back and down to the soil (for the drawings)."""
    a = math.radians(P.burner_angle)
    L = P.flame_len * scale
    w0, w1 = P.burner_body[0] * 0.9, P.burner_body[0] * 1.15
    m = V(x, P.burner_y, P.burner_z)
    d = V(0, -math.cos(a), -math.sin(a))
    end = m + d * L
    if end.z < 2.0:                                   # stops on the soil and spreads to the rear
        L = (P.burner_z - 2.0) / math.sin(a)
        end = m + d * L
    pts = [V(x - w0 / 2.0, m.y, m.z + 8.0), V(x + w0 / 2.0, m.y, m.z + 8.0), V(x + w1 / 2.0, end.y, end.z + 4.0),
           V(x - w1 / 2.0, end.y, end.z + 4.0)]
    f = _poly(pts).extrude(V(0, 0, -16.0))
    spread = box_span((x - w1 / 2.0, x + w1 / 2.0), (end.y - 180.0 * scale, end.y + 5.0), (1.5, 12.0))
    return fuse_all([f, spread])


def flames(scale=1.0):
    return Part.makeCompound([flame(x, scale) for x in P.burner_x])


def seedbed(y0, y1, w=P.work_w, h=60.0):
    """Raised, smooth seedbed with the sown rows as faint lines (render only)."""
    bed = box_span((-w / 2.0, w / 2.0), (y0, y1), (-40.0, 0.0))
    return bed


def seed_rows(y0, y1, rows=(-450.0, -150.0, 150.0, 450.0)):
    return Part.makeCompound([box_span((x - 6.0, x + 6.0), (y0, y1), (0.0, 0.6)) for x in rows])


def weed(x, y, s=1.0):
    a = cyl_z(2.5, 0.0, 14.0 * s, x, y)
    leaves = []
    for k in (-1, 1):
        lf = Part.makeCylinder(7.0 * s, 1.2, V(0, 0, 0), Z)
        m = App.Matrix()
        m.scale(1.0, 0.6, 1.0)
        lf = lf.transformGeometry(m)
        lf.translate(V(k * 7.0 * s, 0, 14.0 * s))
        lf.rotate(V(0, 0, 14.0 * s), Z, (x * 7.0 + y * 3.0) % 180.0)
        lf.translate(V(x, y, 0))
        leaves.append(lf)
    return Part.makeCompound([a] + leaves)


def weed_scorched(x, y, s=1.0):
    """Wilted seedling: leaves collapsed on the soil."""
    lf = Part.makeCylinder(6.0 * s, 1.0, V(x, y, 0.4), Z)
    m = App.Matrix()
    m.scale(1.0, 0.5, 1.0)
    lf = lf.transformGeometry(m)
    return Part.makeCompound([lf, cyl_z(2.0, 0.0, 5.0 * s, x, y)])
