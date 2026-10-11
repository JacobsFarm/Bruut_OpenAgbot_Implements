import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import irr_params as P
import irr_calc as C

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

# All shapes are drawn in robot coordinates. The reel (App::Part in build_irr) rotates about the line
# x through (reel_y, reel_z); the coil and the hose on the robot are rebuilt for every amount of hose on the reel.


# ---------------------------------------------------------------------
# Basic shapes (same style as mrk_parts.py)
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


def tube_x(od, wall, x0, x1, y, z):
    return cyl_x(od, x0, x1, y, z).cut(cyl_x(od - 2 * wall, x0 - 1, x1 + 1, y, z))


def tube_z(od, wall, z0, z1, x, y):
    return cyl_z(od, z0, z1, x, y).cut(cyl_z(od - 2 * wall, z0 - 1, z1 + 1, x, y))


def _poly(pts):
    pts = list(pts)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


def poly_yz(points, x0, t):
    """Closed polygon in the y-z plane, (y, z) world, extruded over +x from x0."""
    return _poly([V(x0, y, z) for (y, z) in points]).extrude(V(t, 0, 0))


def _hex(af, p0, axis, length):
    r = af / math.sqrt(3.0)
    if axis == "x":
        pts = [V(p0[0], p0[1] + r * math.cos(math.radians(60 * i + 30)), p0[2] + r * math.sin(math.radians(60 * i + 30)))
               for i in range(6)]
        d = V(length, 0, 0)
    else:
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1] + r * math.sin(math.radians(60 * i)), p0[2])
               for i in range(6)]
        d = V(0, 0, length)
    return _poly(pts).extrude(d)


def hex_x(af, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return _hex(af, (x0, y, z), "x", x1 - x0)


def hex_z(af, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return _hex(af, (x, y, z0), "z", z1 - z0)


def frame(shape, origin, u, v, w):
    """Shape drawn in a local frame (local x = u, y = v, z = w) placed in the world. u x v must be w."""
    m = App.Matrix(u.x, v.x, w.x, origin.x,
                   u.y, v.y, w.y, origin.y,
                   u.z, v.z, w.z, origin.z,
                   0.0, 0.0, 0.0, 1.0)
    s = shape.copy()
    s.transformShape(m)
    return s


def bolt_down(x, y, z_top, length, d=10.0, af=17.0, k=6.4, nut_m=8.4, nut_at=None):
    """Hex bolt with the head on top (z_top = underside of the head), shank down; optional nut at z nut_at (top)."""
    items = [hex_z(af, z_top, z_top + k, x, y), cyl_z(d, z_top - length, z_top, x, y)]
    if nut_at is not None:
        items.append(hex_z(af, nut_at - nut_m, nut_at, x, y))
    return items


def bolt_x(y, z, x_head, x_nut, d=10.0, af=17.0, k=6.4, nut_m=8.4, proj=3.0):
    """Bolt along x: head outside x_head (pointing away from x_nut), nut outside x_nut."""
    s = 1.0 if x_head > x_nut else -1.0
    return [hex_x(af, x_head, x_head + s * k, y, z), cyl_x(d, x_nut - s * (nut_m + proj), x_head, y, z),
            hex_x(af, x_nut, x_nut - s * nut_m, y, z)]


# ---------------------------------------------------------------------
# Mount: cradle tubes on the upper beams
# ---------------------------------------------------------------------
def cradle_tubes():
    out = []
    w, t = P.cradle_tube, P.cradle_wall
    for cy in P.cradle_y:
        outer = box_span((-P.cradle_half_len, P.cradle_half_len), (cy - w / 2, cy + w / 2), P.cradle_z)
        inner = box_span((-P.cradle_half_len - 1, P.cradle_half_len + 1), (cy - w / 2 + t, cy + w / 2 - t),
                         (P.cradle_z[0] + t, P.cradle_z[1] - t))
        holes = [cyl_z(P.m10_hole, P.cradle_z[0] - 1, P.cradle_z[1] + 1, x, cy) for x in P.robot_upper_beam_x +
                 FOOT_BOLT_X + tuple(-x for x in FOOT_BOLT_X)]
        out.append(outer.cut(inner).cut(holes))
    return out


def cradle_bolts():
    out = []
    for cy in P.cradle_y:
        for x in P.robot_upper_beam_x:
            out += bolt_down(x, cy, P.cradle_z[1], P.cradle_z[1] - P.robot_upper_beam_z[0] + 12.0,
                             nut_at=P.robot_upper_beam_z[0])
    return out


# ---------------------------------------------------------------------
# Stands (welded): side plate + 2 feet; tie tubes between the plates
# ---------------------------------------------------------------------
FOOT_Z = (P.cradle_z[1], P.cradle_z[1] + P.foot[2])
FOOT_X = (P.plate_x - 10.0, P.plate_x + P.foot[0])
FOOT_BOLT_X = (110.0, 135.0)
UCF_BOLTS = [(dy, dz) for dy in (-P.ucf[1] / 2, P.ucf[1] / 2) for dz in (-P.ucf[1] / 2, P.ucf[1] / 2)]
PB_BOLT_DY = 42.0               # 2-bolt flange bearings of the pinch rollers, bolts at pinch_y -+ 42


def _x0(sx):
    """Inner face of the plate on side sx (outer face = inner + sx * plate_t)."""
    return sx * P.plate_x


def side_plate(sx):
    x0 = P.plate_x if sx > 0 else -P.plate_x - P.plate_t
    outline = poly_yz(P.plate_pts, x0, P.plate_t)
    xa, xb = x0 - 1, x0 + P.plate_t + 1
    band = box_span((xa, xb), (-2000.0, 2000.0), P.plate_band)
    plate = outline.cut([poly_yz(w, xa, P.plate_t + 2) for w in P.plate_windows]).fuse(outline.common(band))
    plate = plate.removeSplitter()
    cuts = [cyl_x(d, xa, xb, y, z) for (y, z, d) in P.plate_holes]
    cuts += [cyl_x(30.0, xa, xb, P.reel_y, P.reel_z),
            cyl_x(21.0, xa, xb, P.pinch_y, P.pinch_z_bottom),
            cyl_x(21.0, xa, xb, P.low_y, P.low_z),
            box_span((xa, xb), (P.pinch_y - P.slot[0] / 2, P.pinch_y + P.slot[0] / 2),
                     (P.pinch_z_top - P.slot[1] / 2, P.pinch_z_top + P.slot[1] / 2))]
    cuts += [cyl_x(P.m10_hole, xa, xb, P.reel_y + dy, P.reel_z + dz) for dy, dz in UCF_BOLTS]
    cuts += [cyl_x(P.m10_hole, xa, xb, P.pinch_y + s * PB_BOLT_DY, P.pinch_z_bottom) for s in (-1, 1)]
    cuts += [cyl_x(P.m8_hole, xa, xb, P.pinch_y + s * 22.0, SPRING_BRACKET_Z[1] + 12.0) for s in (-1, 1)]
    cuts += [cyl_x(P.m10_hole, xa, xb, P.pinch_y + s * 22.0, P.low_z) for s in (-1, 1)]
    if sx > 0:
        cuts += [cyl_x(P.m8_hole, xa, xb, y, P.box_bolt_z) for y in (P.box[1][0] + 30.0, P.box[1][1] - 30.0)]
    return plate.cut(cuts)


def feet(sx):
    out = []
    xr = FOOT_X if sx > 0 else (-FOOT_X[1], -FOOT_X[0])
    for cy in P.cradle_y:
        f = box_span(xr, (cy - P.foot[1] / 2, cy + P.foot[1] / 2), FOOT_Z)
        out.append(f.cut([cyl_z(P.m10_hole, FOOT_Z[0] - 1, FOOT_Z[1] + 1, sx * x, cy) for x in FOOT_BOLT_X]))
    return out


def foot_bolts():
    out = []
    for cy in P.cradle_y:
        for sx in (-1, 1):
            for x in FOOT_BOLT_X:
                out += bolt_down(sx * x, cy, FOOT_Z[1], FOOT_Z[1] - P.cradle_z[0] + 12.0, nut_at=P.cradle_z[0])
    return out


def tie_tubes():
    return [tube_x(P.tie_tube_d, 3.0, -P.plate_x, P.plate_x, y, z) for (y, z) in P.tie_tubes]


# ---------------------------------------------------------------------
# Reel bearings, shaft and the rotating reel
# ---------------------------------------------------------------------
def ucf_bearing(sx):
    sq, pitch, ft, hub_d, height = P.ucf
    x0 = sx * (P.plate_x + P.plate_t)
    x1 = x0 + sx * ft
    body = box_span((x0, x1), (P.reel_y - sq / 2, P.reel_y + sq / 2), (P.reel_z - sq / 2, P.reel_z + sq / 2))
    body = body.fuse(cyl_x(hub_d, x0, x0 + sx * height, P.reel_y, P.reel_z))
    cuts = [cyl_x(P.shaft_d, x0 - sx, x0 + sx * (height + 1), P.reel_y, P.reel_z)]
    cuts += [cyl_x(11.5, x0 - sx, x1 + sx, P.reel_y + dy, P.reel_z + dz) for dy, dz in UCF_BOLTS]
    return body.cut(cuts)


def ucf_bolts():
    out = []
    for sx in (-1, 1):
        x_head = sx * (P.plate_x + P.plate_t + P.ucf[2])
        x_nut = sx * P.plate_x
        for dy, dz in UCF_BOLTS:
            out += bolt_x(P.reel_y + dy, P.reel_z + dz, x_head, x_nut, proj=1.0)
    return out


def shaft():
    return cyl_x(P.shaft_d, P.shaft_x[0], P.shaft_x[1], P.reel_y, P.reel_z)


HALF_GAP = P.reel_gap / 2.0
FL_OUT = HALF_GAP + P.flange_t


def core():
    return tube_x(P.core_od, P.core_wall, -HALF_GAP, HALF_GAP, P.reel_y, P.reel_z)


def _ring_points(r, n, phase=0.0):
    return [(r * math.cos(math.radians(phase + 360.0 * i / n)), r * math.sin(math.radians(phase + 360.0 * i / n)))
            for i in range(n)]


def flanges():
    out = []
    for sx in (-1, 1):
        x0, x1 = sx * HALF_GAP, sx * FL_OUT
        disc = cyl_x(P.flange_d, x0, x1, P.reel_y, P.reel_z)
        cuts = [cyl_x(P.shaft_d + 1, x0 - sx, x1 + sx, P.reel_y, P.reel_z)]
        cuts += [cyl_x(P.m10_hole, x0 - sx, x1 + sx, P.reel_y + a, P.reel_z + b)
                 for a, b in _ring_points(P.tie_r, P.tie_n)]
        cuts += [cyl_x(P.m8_hole, x0 - sx, x1 + sx, P.reel_y + a, P.reel_z + b) for a, b in _ring_points(45.0, 4, 0.0)]
        out.append(disc.cut(cuts))
    return out


def tie_rods():
    out = []
    for a, b in _ring_points(P.tie_r, P.tie_n):
        y, z = P.reel_y + a, P.reel_z + b
        out.append(cyl_x(10.0, -FL_OUT - 8.4, FL_OUT + 8.4, y, z))
        for sx in (-1, 1):
            out.append(hex_x(17.0, sx * FL_OUT, sx * (FL_OUT + 8.4), y, z))
    return out


def hubs():
    out = []
    for sx in (-1, 1):
        x_fl = sx * HALF_GAP
        plate = cyl_x(P.hub_plate[0], x_fl, x_fl - sx * P.hub_plate[1], P.reel_y, P.reel_z)
        boss = cyl_x(P.hub_boss[0], x_fl - sx * P.hub_plate[1], x_fl - sx * (P.hub_plate[1] + P.hub_boss[1]),
                     P.reel_y, P.reel_z)
        hub = plate.fuse(boss).cut([cyl_x(P.shaft_d, -200, 200, P.reel_y, P.reel_z)] +
                                   [cyl_x(P.m8_hole, x_fl - sx * 20, x_fl + sx, P.reel_y + a, P.reel_z + b)
                                    for a, b in _ring_points(45.0, 4, 0.0)])
        out.append(hub)
    return out


def hub_bolts():
    out = []
    for sx in (-1, 1):
        for a, b in _ring_points(45.0, 4, 0.0):
            y, z = P.reel_y + a, P.reel_z + b
            out += [hex_x(13.0, sx * FL_OUT, sx * (FL_OUT + 5.3), y, z),
                    cyl_x(8.0, sx * FL_OUT, sx * (HALF_GAP - P.hub_plate[1] - 8.0), y, z)]
    return out


def sprocket_big():
    x0, x1 = P.sprocket_x
    disc = cyl_x(P.sprocket_big - 6.0, x0, x1, P.reel_y, P.reel_z)
    boss = cyl_x(50.0, P.shaft_x[0], x0, P.reel_y, P.reel_z)
    return disc.fuse(boss).cut(cyl_x(P.shaft_d, -300, 300, P.reel_y, P.reel_z))


# ---------------------------------------------------------------------
# Drive (left side): bracket on 2 standoffs, worm gearbox, motor, small sprocket, chain
# ---------------------------------------------------------------------
MOTOR_Z = P.reel_z + P.motor_dz
BRACKET_X = (P.gearbox_x0 + P.motor_bracket[0], P.gearbox_x0)       # (-146, -154)


def standoffs():
    x0 = -(P.plate_x + P.plate_t)
    return [cyl_x(P.motor_standoff[0], x0, BRACKET_X[0], P.reel_y + s * P.motor_standoff[1], MOTOR_Z)
            for s in (-1, 1)]


def motor_bracket():
    b = box_span(BRACKET_X, (P.reel_y - P.motor_bracket[1] / 2, P.reel_y + P.motor_bracket[1] / 2),
                 (MOTOR_Z - P.motor_bracket[2] / 2, MOTOR_Z + P.motor_bracket[2] / 2))
    return b.cut(cyl_x(24.0, -300, 0, P.reel_y, MOTOR_Z))


def gearmotor():
    gx, gy, gz = P.gearbox
    x0 = P.gearbox_x0
    box = box_span((x0, x0 - gx), (P.reel_y - gy / 2, P.reel_y + gy / 2), (MOTOR_Z - gz / 2, MOTOR_Z + gz / 2))
    motor = cyl_z(P.motor_body[0], MOTOR_Z - gz / 2 - P.motor_body[1], MOTOR_Z - gz / 2, x0 - gx / 2, P.reel_y)
    out_shaft = cyl_x(20.0, x0, P.sprocket_x[1], P.reel_y, MOTOR_Z)
    return [box, motor, out_shaft]


def sprocket_small():
    x0, x1 = P.sprocket_x
    disc = cyl_x(P.sprocket_small - 6.0, x0, x1, P.reel_y, MOTOR_Z)
    boss = cyl_x(30.0, x0, x0 - 6.0, P.reel_y, MOTOR_Z)
    return disc.fuse(boss).cut(cyl_x(20.0, -300, 0, P.reel_y, MOTOR_Z))


def _stadium(r1, r2, x0, x1):
    """Convex hull of two circles in the y-z plane (big one at the reel axis, small one at the motor)."""
    c1 = V(0, P.reel_y, P.reel_z)
    c2 = V(0, P.reel_y, MOTOR_Z)
    d = P.reel_z - MOTOR_Z
    phi = math.asin((r1 - r2) / d)
    pts = []
    for s in (1, -1, ):
        m = V(0, s * math.cos(phi), math.sin(phi))
        pts.append((c1 + m * r1, c2 + m * r2))
    quad = [pts[0][0], pts[0][1], pts[1][1], pts[1][0]]
    face = _poly([V(x0, p.y, p.z) for p in quad]).extrude(V(x1 - x0, 0, 0))
    return face.fuse([cyl_x(2 * r1, x0, x1, c1.y, c1.z), cyl_x(2 * r2, x0, x1, c2.y, c2.z)])


def chain():
    x0, x1 = P.sprocket_x[0] + 1.0, P.sprocket_x[1] - 1.0
    r1, r2 = P.sprocket_big / 2.0, P.sprocket_small / 2.0
    return _stadium(r1 + 5.0, r2 + 5.0, x0, x1).cut(_stadium(r1 + 0.5, r2 + 0.5, x0 - 1, x1 + 1))


# ---------------------------------------------------------------------
# Pinch rollers, lower guide roller, springs, encoder
# ---------------------------------------------------------------------
ROLL_X = (-P.pinch_len / 2.0, P.pinch_len / 2.0)
SHAFT_END = P.plate_x + P.plate_t + 34.0


def roller(z, d=P.pinch_d):
    """PU-coated steel tube with welded end discs, bored for the shaft."""
    r = tube_x(d, 5.0, ROLL_X[0], ROLL_X[1], P.pinch_y, z).fuse(
        [cyl_x(d - 2.0, ROLL_X[0], ROLL_X[0] + 5.0, P.pinch_y, z), cyl_x(d - 2.0, ROLL_X[1] - 5.0, ROLL_X[1],
                                                                          P.pinch_y, z)])
    return r.cut(cyl_x(P.pinch_shaft, -300, 300, P.pinch_y, z))


def roller_shaft(z, right_extra=0.0):
    return cyl_x(P.pinch_shaft, -SHAFT_END, SHAFT_END + right_extra, P.pinch_y, z)


def pinch_bearings():
    """2-bolt flange bearings (UCFL204 style) of the bottom pinch roller, on the outer faces."""
    out = []
    for sx in (-1, 1):
        x0 = sx * (P.plate_x + P.plate_t)
        x1 = x0 + sx * 11.0
        flange = box_span((x0, x1), (P.pinch_y - 60, P.pinch_y + 60), (P.pinch_z_bottom - 30, P.pinch_z_bottom + 30))
        hub = cyl_x(48.0, x0, x0 + sx * 30.0, P.pinch_y, P.pinch_z_bottom)
        b = flange.fuse(hub).cut([cyl_x(P.pinch_shaft, -300, 300, P.pinch_y, P.pinch_z_bottom)] +
                                 [cyl_x(11.5, x0 - sx, x1 + sx, P.pinch_y + s * PB_BOLT_DY, P.pinch_z_bottom)
                                  for s in (-1, 1)])
        out.append(b)
        for s in (-1, 1):
            out += bolt_x(P.pinch_y + s * PB_BOLT_DY, P.pinch_z_bottom, x1, sx * P.plate_x)
    return out


def top_blocks():
    """Sliding bearing blocks of the top pinch roller (outside the plates, guided by the slot)."""
    by, bz, bt = P.block
    out = []
    for sx in (-1, 1):
        x0 = sx * (P.plate_x + P.plate_t)
        b = box_span((x0, x0 + sx * bt), (P.pinch_y - by / 2, P.pinch_y + by / 2),
                     (P.pinch_z_top - bz / 2, P.pinch_z_top + bz / 2))
        out.append(b.cut(cyl_x(P.pinch_shaft, -300, 300, P.pinch_y, P.pinch_z_top)))
    return out


BLOCK_TOP = P.pinch_z_top + P.block[1] / 2.0
SPRING_BRACKET_Z = (BLOCK_TOP + P.spring[2] - P.spring_pre, BLOCK_TOP + P.spring[2] - P.spring_pre +
                    P.spring_bracket[1])
SPRING_X = P.plate_x + P.plate_t + P.block[2] / 2.0


def springs():
    od, wire, free = P.spring
    return [tube_z(od, wire, BLOCK_TOP, SPRING_BRACKET_Z[0], sx * SPRING_X, P.pinch_y) for sx in (-1, 1)]


def spring_brackets():
    """Angle 6 mm: horizontal leg over the spring, vertical leg bolted (M8) to the plate."""
    ly, t, lx = P.spring_bracket
    out = []
    for sx in (-1, 1):
        x0 = sx * (P.plate_x + P.plate_t)
        horiz = box_span((x0, x0 + sx * lx), (P.pinch_y - ly / 2, P.pinch_y + ly / 2), SPRING_BRACKET_Z)
        vert = box_span((x0, x0 + sx * t), (P.pinch_y - ly / 2, P.pinch_y + ly / 2),
                        (SPRING_BRACKET_Z[1], SPRING_BRACKET_Z[1] + 22.0))
        br = horiz.fuse(vert).cut([cyl_z(10.5, 0, 2000, sx * SPRING_X, P.pinch_y),
                                   cyl_x(P.m8_hole, x0 - sx, x0 + sx * (t + 1), P.pinch_y - 22.0,
                                         SPRING_BRACKET_Z[1] + 12.0),
                                   cyl_x(P.m8_hole, x0 - sx, x0 + sx * (t + 1), P.pinch_y + 22.0,
                                         SPRING_BRACKET_Z[1] + 12.0)])
        out.append(br)
    return out


def spring_bolts():
    """M10 adjusting bolts (preload) with a lock nut on top of the bracket; M8 bolts of the brackets."""
    out = []
    for sx in (-1, 1):
        x = sx * SPRING_X
        out += [hex_z(17.0, SPRING_BRACKET_Z[1] + 8.4, SPRING_BRACKET_Z[1] + 14.8, x, P.pinch_y),
                cyl_z(10.0, BLOCK_TOP + 15.0, SPRING_BRACKET_Z[1] + 8.4, x, P.pinch_y),
                hex_z(17.0, SPRING_BRACKET_Z[1], SPRING_BRACKET_Z[1] + 8.4, x, P.pinch_y)]
        x0 = sx * (P.plate_x + P.plate_t + P.spring_bracket[1])
        for s in (-1, 1):
            out += bolt_x(P.pinch_y + s * 22.0, SPRING_BRACKET_Z[1] + 12.0, x0, sx * P.plate_x, d=8.0, af=13.0, k=5.3,
                          nut_m=6.8)
    return out


def low_bushings():
    """Lower roller: flanged plastic bushings on the outer faces, 2 x M10 each, collar on the shaft."""
    out = []
    for sx in (-1, 1):
        x0 = sx * (P.plate_x + P.plate_t)
        fl = box_span((x0, x0 + sx * 8.0), (P.low_y - 35, P.low_y + 35), (P.low_z - 20, P.low_z + 20))
        hub = cyl_x(40.0, x0, x0 + sx * 20.0, P.low_y, P.low_z)
        b = fl.fuse(hub).cut([cyl_x(P.pinch_shaft, -300, 300, P.low_y, P.low_z)] +
                             [cyl_x(11.5, -300, 300, P.low_y + s * 22.0, P.low_z) for s in (-1, 1)])
        out.append(b)
        for s in (-1, 1):
            out += bolt_x(P.low_y + s * 22.0, P.low_z, x0 + sx * 8.0, sx * P.plate_x)
    return out


def low_shaft():
    return cyl_x(P.pinch_shaft, -(P.plate_x + P.plate_t + 26.0), P.plate_x + P.plate_t + 26.0, P.low_y, P.low_z)


def encoder():
    x0 = SHAFT_END + 2.0
    return [cyl_x(50.0, x0, x0 + 35.0, P.pinch_y, P.pinch_z_bottom),
            box_span((P.plate_x + P.plate_t + 30.0, x0 + 5.0), (P.pinch_y - 5, P.pinch_y + 5),
                     (P.pinch_z_bottom - 50, P.pinch_z_bottom - 25))]


def control_box():
    return box_span(*P.box)


# ---------------------------------------------------------------------
# Hose on the robot: coil and run (coil -> nip -> around the bottom pinch roller -> down -> lower roller -> ground)
# ---------------------------------------------------------------------
HW = P.hose_flat_w
HT = P.hose_flat_t


def coil(l_reel):
    r0 = P.core_od / 2.0
    r1 = C.coil_r(l_reel)
    outer = cyl_x(2 * r1, -HW / 2, HW / 2, P.reel_y, P.reel_z)
    return outer.cut(cyl_x(2 * r0, -HW / 2 - 1, HW / 2 + 1, P.reel_y, P.reel_z))


def _arc(cy, cz, r, a0, a1, n=6):
    return [(cy + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def run_points(l_reel, ground_y=None):
    """(y, z) of the hose centre line on the robot."""
    r = C.coil_r(l_reel) - HT / 2.0
    ny, nz = P.pinch_y, P.nip_z
    dy, dz = ny - P.reel_y, nz - P.reel_z
    d = math.hypot(dy, dz)
    a = math.atan2(dz, dy)
    b = math.acos(min(1.0, r / d))
    cands = [(P.reel_y + r * math.cos(a + s * b), P.reel_z + r * math.sin(a + s * b)) for s in (-1, 1)]
    tan = min(cands, key=lambda p: p[1])
    rb = P.pinch_d / 2.0 + HT / 2.0
    rl = P.low_d / 2.0 + HT / 2.0
    pts = [tan, (ny, nz)]
    pts += _arc(P.pinch_y, P.pinch_z_bottom, rb, 90.0, 180.0)[1:]
    pts += _arc(P.low_y, P.low_z, rl, 180.0, 270.0)
    gy = P.low_y - 650.0 if ground_y is None else ground_y
    pts.append((gy, HT / 2.0))
    return pts


def ribbon(points, w=HW, t=HT):
    """Flat hose along a 3D polyline: width horizontal (across the line), thickness normal to it."""
    out = []
    for p, q in zip(points[:-1], points[1:]):
        p, q = V(*p), V(*q)
        u = q - p
        length = u.Length
        if length < 0.5:
            continue
        u.normalize()
        v = Z.cross(u)
        v = X if v.Length < 1e-6 else v.normalize()
        wv = u.cross(v)
        seg = Part.makeBox(length, w, t, V(0, -w / 2.0, -t / 2.0))
        out.append(frame(seg, p, u, v, wv))
    return out


def hose_run(l_reel, ground_y=None, tail_y=None):
    pts = [(0.0, y, z) for (y, z) in run_points(l_reel, ground_y)]
    if tail_y is not None:
        pts.append((0.0, tail_y, HT / 2.0))
    return ribbon(pts)


# ---------------------------------------------------------------------
# Field (animation): hose on the ground, outlets, wet patches, pump unit at the ditch
# ---------------------------------------------------------------------
def hose_ground(points, state):
    """state: 'flat' (empty), 'full' (round) or 'wet' (just drained, slightly swollen)."""
    if state == "full":
        out = []
        r = (P.hose_id + 2 * P.hose_wall) / 2.0
        for p, q in zip(points[:-1], points[1:]):
            p, q = V(p[0], p[1], r), V(q[0], q[1], r)
            u = q - p
            if u.Length < 0.5:
                continue
            out.append(Part.makeCylinder(r, u.Length, p, u))
        return out
    if state == "wet":
        return ribbon([(x, y, 4.0) for (x, y) in points], w=HW - 15.0, t=8.0)
    return ribbon([(x, y, HT / 2.0 + 1.5) for (x, y) in points])     # lifted 1.5 mm: drawn over the wet patches


def outlet_marks(points_xy_dir):
    """Saddle + drop tail at each outlet: (x, y, dir_x, dir_y) with dir = towards the hydrant."""
    out = []
    sx, sl, st = P.outlet_saddle
    tw, tl, tt = P.outlet_tail
    for x, y, ux, uy in points_xy_dir:
        u = V(ux, uy, 0)
        v = Z.cross(u)
        sad = Part.makeBox(sl, sx, st, V(-sl / 2, -sx / 2, HT))
        tail = Part.makeBox(tl, tw, tt, V(-tl, -tw / 2 - HW / 2 - 4.0, 0))
        out.append(frame(sad, V(x, y, 0), u, v, Z))
        out.append(frame(tail, V(x, y, 0), u, v, Z))
    return out


def wet_patch(x, y, r):
    return Part.makeCylinder(r, 1.0, V(x, y, -8.0), Z)       # between the (lowered) grass and the hose


def pump_unit(x, y):
    """Petrol pump on a skid at the ditch side (x, y = hydrant valve). Simple outline for the animation."""
    skid = box_span((x - 700, x - 100), (y - 600, y - 150), (0, 60))
    pump = cyl_y(260, y - 560, y - 380, x - 400, 260)
    engine = box_span((x - 560, x - 240), (y - 380, y - 170), (60, 420))
    tank = box_span((x - 520, x - 280), (y - 360, y - 190), (420, 520))
    frame_ = [cyl_z(25, 60, 640, x + dx, y + dy) for dx in (-680, -120) for dy in (-580, -170)]
    frame_ += [cyl_x(25, x - 680, x - 120, y + dy, 640) for dy in (-580, -170)]
    outlet = cyl_y(90, y - 380, y - 150, x - 400, 260)
    riser = [cyl_x(90, x - 400, x, y - 150, 260), cyl_z(90, 0, 300, x, y - 150)]
    valve = [box_span((x - 70, x + 70), (y - 220, y - 80), (300, 420)), cyl_z(20, 420, 500, x, y - 150),
             cyl_x(16, x, x + 180, y - 150, 495)]
    coupling = cyl_y(110, y - 80, y + 40, x, 60)
    drain = cyl_x(60, x - 40, x - 400, y - 30, 60)
    return {"skid": [skid] + frame_, "pump": [pump, outlet] + riser, "engine": [engine, tank],
            "valve": valve + [coupling], "drain": [drain]}


def suction_hose(x, y, ditch_y, water_z):
    pts = [(x - 400, y - 560, 260), (x - 400, y - 700, 260), (x - 400, ditch_y + 500, 120),
           (x - 400, ditch_y, water_z - 250)]
    out = []
    for p, q in zip(pts[:-1], pts[1:]):
        p, q = V(*p), V(*q)
        out.append(Part.makeCylinder(50, (q - p).Length, p, q - p))
    out.append(Part.makeCylinder(80, 200, V(x - 400, ditch_y, water_z - 450), Z))       # strainer
    return out
