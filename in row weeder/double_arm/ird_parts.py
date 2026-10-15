"""Parts of the in-row weeder with double arms: one function per part, in robot coordinates, working position (units
down, knives in). Functions ending in _right give the right row unit; the left unit is the mirror image (see mirror_x).
Arm functions take side = +1 (outer arm) or -1 (inner arm). Crop and weed shapes for the drawings are at the end."""
import math
import random

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ird_params as P
import ird_calc as C

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)
XR = P.row_x[1]                 # right row


# ---------------------------------------------------------------------
# Basic shapes
# ---------------------------------------------------------------------
def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def ubox(u, y, z):
    """Box in unit coordinates of the right unit (u = x - row_x)."""
    return box_span((XR + u[0], XR + u[1]), y, z)


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


def rod_between(p0, p1, d):
    p0, p1 = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (p1 - p0).Length, p0, p1 - p0)


def square_tube_x(x0, x1, y, z, size, wall):
    o = box_span((x0, x1), (y - size / 2, y + size / 2), (z - size / 2, z + size / 2))
    i = box_span((x0 - 1, x1 + 1), (y - size / 2 + wall, y + size / 2 - wall), (z - size / 2 + wall, z + size / 2 - wall))
    return o.cut(i)


def square_tube_y(y0, y1, x, z, size, wall):
    o = box_span((x - size / 2, x + size / 2), (y0, y1), (z - size / 2, z + size / 2))
    i = box_span((x - size / 2 + wall, x + size / 2 - wall), (y0 - 1, y1 + 1), (z - size / 2 + wall, z + size / 2 - wall))
    return o.cut(i)


def hex_prism_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    return _poly(pts).extrude(V(0, 0, z1 - z0))


def hex_prism_x(af, x0, x1, y, z):
    r = af / math.sqrt(3.0)
    pts = [V(x0, y + r * math.cos(math.radians(60 * i)), z + r * math.sin(math.radians(60 * i))) for i in range(6)]
    return _poly(pts).extrude(V(x1 - x0, 0, 0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    """Vertical bolt: head on top of z_head, nut under z_nut."""
    head = hex_prism_z(af, z_head, z_head + k, x, y)
    shank = cyl_z(d, z_nut - m - 4.0, z_head, x, y)
    nut = hex_prism_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))
    return fuse_all([head, shank, nut])


def pin_x(x0, x1, y, z, d=P.link_pin_d):
    """Pin along x with a head on the outside (+x) and a washer + split pin on the other end."""
    return fuse_all([cyl_x(d, x0 - 4.0, x1 + 4.0, y, z), cyl_x(d + 10.0, x1 + 4.0, x1 + 8.0, y, z),
                     cyl_x(d + 8.0, x0 - 6.0, x0 - 4.0, y, z)])


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both_sides(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


def ux(u):
    return XR + u


# ---------------------------------------------------------------------
# Frame: rails under the lower beams, toolbar, toolbar brackets and actuator lugs (one weldment)
# ---------------------------------------------------------------------
def rails():
    zc = (P.rail_z[0] + P.rail_z[1]) / 2.0
    out = []
    for sx in (1, -1):
        r = square_tube_y(P.rail_y[0], P.rail_y[1], sx * P.rail_x, zc, P.rail, P.rail_wall)
        holes = [cyl_z(P.m10_hole, P.rail_z[0] - 1, P.rail_z[1] + 1, sx * P.rail_x, y) for y in P.robot_lower_beam_y]
        out.append(r.cut(holes))
    return Part.makeCompound(out)


def toolbar():
    zc = (P.toolbar_z[0] + P.toolbar_z[1]) / 2.0
    return square_tube_x(-P.toolbar_half, P.toolbar_half, P.toolbar_y, zc, P.toolbar, P.toolbar_wall)


BRK_U = (P.link_u - 46.0, P.link_u + 46.0)          # bracket plate centres


def toolbar_brackets_right():
    """Two plates per unit, welded under the toolbar, with the front pins of the parallelogram."""
    out = []
    y0, y1 = P.pin_y_front - 25.0, P.toolbar_y + P.toolbar / 2.0
    for uc in BRK_U:
        pts = [(y0, P.pin_z[1] - 22.0), (P.pin_y_front + 25.0, P.pin_z[1] - 22.0), (y1, P.toolbar_z[0] - 30.0),
               (y1, P.toolbar_z[0]), (y0, P.toolbar_z[0])]
        pl = poly_yz(pts, ux(uc) - P.brk_plate_t / 2.0, P.brk_plate_t)
        for z in P.pin_z:
            pl = pl.cut(cyl_x(P.link_pin_d + 0.5, ux(uc) - 10, ux(uc) + 10, P.pin_y_front, z))
        out.append(pl)
    return Part.makeCompound(out)


def act_lug_toolbar_right():
    bu, by, bz = P.act_base
    pl = box_span((ux(bu) - P.lug_t / 2.0, ux(bu) + P.lug_t / 2.0), (by - 22.0, by + 22.0), (P.toolbar_z[1], bz + 18.0))
    return pl.cut(cyl_x(10.5, ux(bu) - 10, ux(bu) + 10, by, bz))


def frame_weldment():
    return Part.makeCompound([rails(), toolbar(), both_sides(toolbar_brackets_right()),
                              both_sides(act_lug_toolbar_right())])


def frame_bolts():
    """M10 through the lower beams and the rails, head on top of the beam, nut under the rail."""
    out = []
    for sx in (1, -1):
        for y in P.robot_lower_beam_y:
            out.append(bolt_z(sx * P.rail_x, y, P.robot_lower_beam_z[1], P.rail_z[0]))
    return Part.makeCompound(out)


def front_pins_right():
    u0, u1 = BRK_U[0] - P.brk_plate_t / 2.0, BRK_U[1] + P.brk_plate_t / 2.0
    return Part.makeCompound([pin_x(ux(u0), ux(u1), P.pin_y_front, z) for z in P.pin_z])


# ---------------------------------------------------------------------
# Parallelogram links (each link pair is its own sub-Part: rotates about its front pin)
# ---------------------------------------------------------------------
LINK_U = (P.link_u - 38.0, P.link_u + 38.0)


def link_pair_right(z):
    out = []
    h, t = P.link_bar
    for uc in LINK_U:
        bar = box_span((ux(uc) - t / 2.0, ux(uc) + t / 2.0), (P.pin_y_rear - 18.0, P.pin_y_front + 18.0),
                       (z - h / 2.0, z + h / 2.0))
        for y in (P.pin_y_front, P.pin_y_rear):
            bar = bar.cut(cyl_x(P.link_pin_d + 0.5, ux(uc) - 10, ux(uc) + 10, y, z))
        out.append(bar)
    return Part.makeCompound(out)


def upper_links_right():
    return link_pair_right(P.pin_z[0])


def lower_links_right():
    return link_pair_right(P.pin_z[1])


# ---------------------------------------------------------------------
# Unit head (moves up / down with the parallelogram)
# ---------------------------------------------------------------------
CHEEK_U = (P.link_u - 30.0, P.link_u + 30.0)


def shaft_xy(side):
    """Shaft position (x, y) of the right unit's arm on this side."""
    return ux(side * P.shaft_u), P.shaft_y[side]


def deck_right():
    d = ubox(P.deck_u, P.deck_y, P.deck_z)
    for side in P.SIDES:
        sx, sy = shaft_xy(side)
        d = d.cut(cyl_z(P.shaft_d + 2.0, P.deck_z[0] - 1, P.deck_z[1] + 1, sx, sy))
    return d


def cheeks_right():
    out = []
    for uc in CHEEK_U:
        c = ubox((uc - P.cheek_t / 2.0, uc + P.cheek_t / 2.0), P.cheek_y, P.cheek_z)
        for z in P.pin_z:
            c = c.cut(cyl_x(P.link_pin_d + 0.5, ux(uc) - 10, ux(uc) + 10, P.pin_y_rear, z))
        out.append(c)
    return Part.makeCompound(out)


def deck_lug_right():
    eu, ey, ez = P.act_end
    pl = box_span((ux(eu) - P.lug_t / 2.0, ux(eu) + P.lug_t / 2.0), (ey - 22.0, ey + 22.0), (P.deck_z[1], ez + 18.0))
    return pl.cut(cyl_x(10.5, ux(eu) - 10, ux(eu) + 10, ey, ez))


def gauge_fork_right():
    """Two fork plates from the deck down to the gauge wheel axle, a row of depth holes."""
    out = []
    gu, gy = P.gauge_u, P.gauge_y
    az = P.gauge_d / 2.0
    for uc in (gu - P.gauge_w / 2.0 - 4.0 - P.gauge_fork_t / 2.0, gu + P.gauge_w / 2.0 + 4.0 + P.gauge_fork_t / 2.0):
        pts = [(gy - 22.0, az - 32.0), (gy + 22.0, az - 32.0), (gy + 35.0, P.deck_z[0]), (gy - 35.0, P.deck_z[0])]
        pl = poly_yz(pts, ux(uc) - P.gauge_fork_t / 2.0, P.gauge_fork_t)
        for k in range(P.gauge_holes):
            dz = (k - (P.gauge_holes - 1) / 2.0) * P.gauge_hole_pitch
            pl = pl.cut(cyl_x(12.5, ux(uc) - 10, ux(uc) + 10, gy, az + dz))
        out.append(pl)
    return Part.makeCompound(out)


def head_weldment_right():
    return Part.makeCompound([deck_right(), cheeks_right(), deck_lug_right(), gauge_fork_right()])


def rear_pins_right():
    u0, u1 = LINK_U[0] - P.link_bar[1] / 2.0, LINK_U[1] + P.link_bar[1] / 2.0
    return Part.makeCompound([pin_x(ux(u0), ux(u1), P.pin_y_rear, z) for z in P.pin_z])


def bearing_right(side):
    """Flange bearing (UCFL204 class) under the deck, bolted with 2 x M10."""
    x, y = shaft_xy(side)
    w, h, _ = P.bearing
    z1 = P.deck_z[0]
    flange = poly_xy([(x - w / 2.0, y), (x, y - 32.0), (x + w / 2.0, y), (x, y + 32.0)], z1 - 12.0, 12.0)
    body = cyl_z(58.0, z1 - h, z1 - 12.0, x, y)
    s = flange.fuse(body).cut(cyl_z(P.shaft_d, z1 - h - 1, z1 + 1, x, y))
    bolts = [cyl_z(10.0, z1 - 16.0, P.deck_z[1] + 6.0, x + dx, y) for dx in (-38.0, 38.0)]
    return Part.makeCompound([s] + bolts)


def gearbox_right(side):
    x, y = shaft_xy(side)
    z0 = P.deck_z[1]
    flange = box_span((x - P.gear_d / 2.0, x + P.gear_d / 2.0), (y - P.gear_d / 2.0, y + P.gear_d / 2.0), (z0, z0 + 10.0))
    body = cyl_z(P.gear_d - 4.0, z0 + 10.0, z0 + P.gear_len, x, y)
    return fuse_all([flange, body])


def motor_right(side):
    x, y = shaft_xy(side)
    z0 = P.deck_z[1] + P.gear_len
    m = P.motor_sq
    body = box_span((x - m / 2.0, x + m / 2.0), (y - m / 2.0, y + m / 2.0), (z0, z0 + P.motor_len))
    edges = [e for e in body.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    body = body.makeFillet(5.0, edges)
    plug = box_span((x - 12.0, x + 12.0), (y - m / 2.0 - 15.0, y - m / 2.0),            # connector to the rear
                    (z0 + P.motor_len - 40.0, z0 + P.motor_len - 10.0))
    return fuse_all([body, plug])


def gauge_wheel_right():
    gu, gy = P.gauge_u, P.gauge_y
    az = P.gauge_d / 2.0
    tyre = cyl_x(P.gauge_d, ux(gu) - P.gauge_w / 2.0, ux(gu) + P.gauge_w / 2.0, gy, az)
    tyre = tyre.cut(cyl_x(P.gauge_d - 60.0, ux(gu) - P.gauge_w / 2.0 - 1, ux(gu) + P.gauge_w / 2.0 + 1, gy, az))
    rim = cyl_x(P.gauge_d - 60.0, ux(gu) - P.gauge_w / 2.0 + 8.0, ux(gu) + P.gauge_w / 2.0 - 8.0, gy, az)
    return Part.makeCompound([tyre, rim])


def gauge_axle_right():
    gu, gy = P.gauge_u, P.gauge_y
    u0 = gu - P.gauge_w / 2.0 - 4.0 - P.gauge_fork_t
    u1 = gu + P.gauge_w / 2.0 + 4.0 + P.gauge_fork_t
    return fuse_all([cyl_x(12.0, ux(u0) - 6.0, ux(u1) + 6.0, gy, P.gauge_d / 2.0),
                     cyl_x(16.0, ux(gu) - P.gauge_w / 2.0, ux(u0) + P.gauge_fork_t, gy, P.gauge_d / 2.0),
                     cyl_x(16.0, ux(u1) - P.gauge_fork_t, ux(gu) + P.gauge_w / 2.0, gy, P.gauge_d / 2.0)])


# ---------------------------------------------------------------------
# Swing arm with the finger (its own sub-Part: rotates about the shaft; drawn at theta_in)
# ---------------------------------------------------------------------
def _arm_frame(side):
    """Origin = shaft, unit vector e along the arm (to the finger) and n across it, in x-y (right unit)."""
    x, y = shaft_xy(side)
    a = math.radians(P.theta_in)
    e = V(-side * math.sin(a), -math.cos(a), 0)
    n = V(math.cos(a), -side * math.sin(a), 0)
    return V(x, y, 0), e, n


def _plate_along(o, e, n, s0, s1, w, z0, z1):
    pts = [o + e * s0 + n * (-w / 2.0), o + e * s1 + n * (-w / 2.0), o + e * s1 + n * (w / 2.0),
           o + e * s0 + n * (w / 2.0)]
    return _poly([V(p.x, p.y, z0) for p in pts]).extrude(V(0, 0, z1 - z0))


def shaft_right(side):
    x, y = shaft_xy(side)
    return cyl_z(P.shaft_d, P.shaft_z[0], P.shaft_z[1], x, y)


def arm_right(side):
    o, e, n = _arm_frame(side)
    bar = _plate_along(o, e, n, 0.0, P.arm_r + 20.0, P.arm_bar[0], P.arm_z[0], P.arm_z[1])
    hub = cyl_z(P.hub_d, P.arm_z[0], P.arm_z[1] + 30.0, o.x, o.y)
    s = fuse_all([bar, hub]).cut(cyl_z(P.shaft_d, P.arm_z[0] - 1, P.arm_z[1] + 31, o.x, o.y))
    slot = cyl_z(P.shank[0] * 0.0 + 10.5, P.arm_z[0] - 1, P.arm_z[1] + 1, (o + e * P.arm_r).x, (o + e * P.arm_r).y)
    return s.cut(slot)


def finger_right(side):
    """Spring-steel shank (thin edge leading), coil under the arm, knife at the bottom. The knife lies across the travel
    when the arm is at theta_in."""
    o, e, n = _arm_frame(side)
    f = o + e * P.arm_r
    coil_z = (P.arm_z[0] - P.shank_coil[1], P.arm_z[0])
    coil = cyl_z(P.shank_coil[0], coil_z[0], coil_z[1], f.x, f.y).cut(
        cyl_z(P.shank_coil[0] - 14.0, coil_z[0] - 1, coil_z[1] + 1, f.x, f.y))
    bolt = cyl_z(10.0, coil_z[0] - 5.0, P.arm_z[1] + 8.0, f.x, f.y)
    shank = box_span((f.x - P.shank[1] / 2.0, f.x + P.shank[1] / 2.0), (f.y - P.shank[0] / 2.0, f.y + P.shank[0] / 2.0),
                     (P.knife_z[1], coil_z[0] + 5.0))
    knife = box_span((f.x - P.knife_w / 2.0, f.x + P.knife_w / 2.0), (f.y - P.knife_l / 2.0, f.y + P.knife_l / 2.0),
                     P.knife_z)
    # sharpened leading edge (chamfer on the front)
    wedge = _poly([V(f.x - P.knife_w / 2.0 - 1, f.y + P.knife_l / 2.0 - 12.0, P.knife_z[1]),
                   V(f.x - P.knife_w / 2.0 - 1, f.y + P.knife_l / 2.0 + 1, P.knife_z[1]),
                   V(f.x - P.knife_w / 2.0 - 1, f.y + P.knife_l / 2.0 + 1, P.knife_z[0] + 0.8)]).extrude(
        V(P.knife_w + 2, 0, 0))
    knife = knife.cut(wedge)
    return Part.makeCompound([coil, bolt, fuse_all([shank, knife])])


# ---------------------------------------------------------------------
# Lift actuator (body rotates about the toolbar pin, rod slides; drawn at the working length)
# ---------------------------------------------------------------------
def _act_axis():
    bu, by, bz = P.act_base
    eu, ey, ez = P.act_end
    b = V(ux(bu), by, bz)
    d = V(0, ey - by, ez - bz)
    L0 = d.Length
    d.normalize()
    return b, d, L0


L0 = None


def act_body_right():
    b, d, L = _act_axis()
    body = Part.makeCylinder(P.act_body_d / 2.0, 170.0, b + d * 25.0, d).cut(
        Part.makeCylinder(P.act_rod_d / 2.0 + 1.0, 130.0, b + d * 66.0, d))       # bore: the rod retracts into it
    eye = cyl_x(22.0, b.x - 9.0, b.x - P.lug_t / 2.0 - 0.5, b.y, b.z).fuse(
        cyl_x(22.0, b.x + P.lug_t / 2.0 + 0.5, b.x + 9.0, b.y, b.z))
    neck = Part.makeCylinder(9.0, 25.0, b + d * 2.0, d)
    motor = Part.makeCylinder(17.0, 110.0, b + d * 40.0 + V(0, -d.z, d.y) * 32.0, d)
    return Part.makeCompound([body, eye, neck, motor])


def act_rod_right():
    """Rod with a slotted clevis on the deck pin (float in work); drawn for the working length."""
    b, d, L = _act_axis()
    rod = Part.makeCylinder(P.act_rod_d / 2.0, L - 195.0 - 22.0, b + d * 195.0, d)
    e = b + d * L
    clevis = []
    for s in (-1, 1):
        clevis.append(box_span((e.x + s * (P.lug_t / 2.0 + 0.5), e.x + s * (P.lug_t / 2.0 + 5.5)),
                               (e.y - 14.0, e.y + 14.0), (e.z - 14.0, e.z + 14.0)))
    clevis.append(Part.makeCylinder(12.0, 10.0, e - d * 32.0, d))
    pin = cyl_x(10.0, e.x - 9.0, e.x + 9.0, e.y, e.z)
    return Part.makeCompound([rod, pin] + clevis)


# ---------------------------------------------------------------------
# Camera plate, camera, LED bars
# ---------------------------------------------------------------------
def cam_plate():
    (x0, x1), (y0, y1), (z0, z1) = P.cam_plate
    pl = box_span((x0, x1), (y0, y1), (z0, z1))
    for x in P.cam_plate_bolt_x:
        pl = pl.cut(cyl_z(P.m10_hole, z0 - 1, z1 + 1, x, P.robot_lower_beam_y[2]))
    lugs = [box_span((sx * 36.0 - 3.0, sx * 36.0 + 3.0), (P.cam_xyz[1] - 20.0, P.cam_xyz[1] + 20.0),
                     (P.cam_xyz[2] - 5.0, z0)) for sx in (-1, 1)]
    return Part.makeCompound([pl] + lugs)


def cam_bolts():
    return Part.makeCompound([bolt_z(x, P.robot_lower_beam_y[2], P.robot_lower_beam_z[1], P.cam_plate[2][0])
                              for x in P.cam_plate_bolt_x])


def _place_cam(shape):
    s = shape.copy()
    s.rotate(V(*P.cam_xyz), X, P.cam_pitch)
    return s


def camera():
    cx, cy, cz = P.cam_xyz
    bx, by, bz = P.cam_box
    body = box_span((cx - bx / 2.0 + 3.0, cx + bx / 2.0 - 3.0), (cy - by / 2.0, cy + by / 2.0), (cz - 10.0, cz + bz - 10.0))
    body = body.fuse(cyl_x(14.0, cx - 39.0, cx + 39.0, cy, cz + 15.0))        # tilt pivot through the lugs
    lens = cyl_z(P.cam_lens[0], cz - 10.0 - P.cam_lens[1], cz - 10.0, cx, cy)
    return _place_cam(fuse_all([body, lens]))


def camera_glass():
    cx, cy, cz = P.cam_xyz
    return _place_cam(cyl_z(P.cam_lens[0] - 6.0, cz - 11.0 - P.cam_lens[1], cz - 10.0 - P.cam_lens[1], cx, cy))


def led_bars():
    l, w, h = P.led_bar
    z1 = P.cam_plate[2][0]
    out = []
    for sx in (-1, 1):
        x0 = sx * (P.led_x - l / 2.0 + 30.0)
        out.append(box_span((x0, x0 + sx * l * 0.6), (P.led_y - w / 2.0, P.led_y + w / 2.0), (z1 - h, z1)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Control box on the upper inner beams
# ---------------------------------------------------------------------
def box_base():
    (x0, x1), (y0, y1), t = P.box_base
    z0 = P.robot_upper_beam_z[1]
    pl = box_span((x0, x1), (y0, y1), (z0, z0 + t))
    for x in P.box_bolt[0]:
        for y in P.box_bolt[1]:
            pl = pl.cut(cyl_z(P.m10_hole, z0 - 1, z0 + t + 1, x, y))
    return pl


def box_bolts():
    z0 = P.robot_upper_beam_z[1]
    return Part.makeCompound([bolt_z(x, y, z0 + P.box_base[2], P.robot_upper_beam_z[0]) for x in P.box_bolt[0]
                              for y in P.box_bolt[1]])


def control_box():
    z0 = P.robot_upper_beam_z[1] + P.box_base[2]
    b = box_span(P.box_x, P.box_y, (z0, z0 + P.box_h))
    lid = box_span((P.box_x[0] - 4, P.box_x[1] + 4), (P.box_y[0] - 4, P.box_y[1] + 4), (z0 + P.box_h, z0 + P.box_h + 12))
    glands = [cyl_y(16.0, P.box_y[1], P.box_y[1] + 14.0, x, z0 + 30.0) for x in (-200.0, -120.0, 120.0, 200.0)]
    return fuse_all([b, lid] + glands)


# ---------------------------------------------------------------------
# Crop, weeds, soil (renders and animation)
# ---------------------------------------------------------------------
def broccoli(x, y, d=220.0, h=230.0, seed=0):
    """Young broccoli: stem and 6-7 leaves (thin tilted ellipses) in a rosette."""
    rnd = random.Random(seed)
    parts = [cyl_z(P.stem_d, 0.0, h * 0.35, x, y)]
    n = rnd.randint(6, 7)
    for i in range(n):
        ang = 360.0 * i / n + rnd.uniform(-15, 15)
        l = d / 2.0 * rnd.uniform(0.75, 1.0)
        leaf = Part.makeCylinder(l / 2.0, 3.0, V(0, 0, 0), Z)
        m = App.Matrix()
        m.scale(1.0, 0.55, 1.0)
        leaf = leaf.transformGeometry(m)
        leaf.translate(V(l / 2.0, 0, 0))
        leaf.rotate(V(0, 0, 0), Y, -rnd.uniform(20.0, 45.0))
        leaf.rotate(V(0, 0, 0), Z, ang)
        leaf.translate(V(x, y, h * rnd.uniform(0.25, 0.4)))
        parts.append(leaf)
    return Part.makeCompound(parts)


def weed(x, y, s=1.0):
    """Weed seedling: two small leaves on a short stalk."""
    a = cyl_z(3.0, 0.0, 18.0 * s, x, y)
    leaves = []
    for k in (-1, 1):
        lf = Part.makeCylinder(9.0 * s, 1.5, V(0, 0, 0), Z)
        m = App.Matrix()
        m.scale(1.0, 0.6, 1.0)
        lf = lf.transformGeometry(m)
        lf.translate(V(k * 9.0 * s, 0, 18.0 * s))
        lf.rotate(V(0, 0, 18.0 * s), Z, (x * 7.0 + y * 3.0) % 180.0)
        lf.translate(V(x, y, 0))
        leaves.append(lf)
    return Part.makeCompound([a] + leaves)


def weed_dead(x, y, s=1.0):
    """Uprooted seedling lying on the soil."""
    lf = Part.makeCylinder(8.0 * s, 1.5, V(x, y, 0.5), Z)
    m = App.Matrix()
    m.scale(1.0, 0.45, 1.0)
    lf = lf.transformGeometry(m)
    return lf


def worked_strip(corners0, corners1, z=0.6, t=0.6):
    """Hoed soil between two knife positions (convex hull of both outlines)."""
    pts = hull2d(list(corners0) + list(corners1))
    return poly_xy(pts, z, t)


def hull2d(points):
    pts = sorted(set((round(p[0], 3), round(p[1], 3)) for p in points))
    if len(pts) < 3:
        return pts

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


def ground_polygon(points, z=1.0, t=0.5):
    return poly_xy(hull2d(points), z, t)


def ridge(x, y0, y1, w=300.0, h=0.0):
    return box_span((x - w / 2.0, x + w / 2.0), (y0, y1), (-1.0, h))
