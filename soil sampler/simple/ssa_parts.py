"""Parts of the soil sampler. Every function returns a Part shape in robot coordinates, in the park pose (probe up,
chute under the probe tip, cup 0 under the funnel). build_ssa.py moves the carriage (z), the foot (z), the chute
(turn about z) and the carousel (turn about z) as sub-Parts.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ssa_params as P


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




def shell(d_out, d_in, p0, p1):
    return cyl(d_out, p0, p1).cut(cyl(d_in, p0, p1))


def along(local, p0, p1, up=(0.0, 0.0, 1.0)):
    """Place a shape drawn along +x from the origin (z = 'up') on the line p0 -> p1."""
    a, b = V(*p0), V(*p1)
    X = b - a
    X.normalize()
    u = V(*up)
    Z = u - X * u.dot(X)
    Z.normalize()
    Y = Z.cross(X)
    s = local.copy()
    s.transformShape(App.Matrix(X.x, Y.x, Z.x, a.x, X.y, Y.y, Z.y, a.y, X.z, Y.z, Z.z, a.z, 0, 0, 0, 1))
    return s


PARK_C = P.carriage_z(P.tip_park)


# ---------------------------------------------------------------------
# Mount: 2 bridges on the inner upper beams
# ---------------------------------------------------------------------
def bridges():
    out = []
    for yr in (P.bridge_front_y, P.bridge_rear_y):
        t = tube_span(P.bridge_x, yr, P.bridge_z, 3.0, "x")
        yc = (yr[0] + yr[1]) / 2.0
        for sx in (-1, 1):
            t = t.cut(cyl(P.m10_hole, (sx * P.bridge_bolt_x, yc, 600), (sx * P.bridge_bolt_x, yc, 800)))
        if yr == P.bridge_front_y:
            for sx in (-1, 1):
                t = t.cut(cyl(8.4, (sx * 60.0, 0.0, P.bridge_z[0] + 20.0), (sx * 60.0, 200.0, P.bridge_z[0] + 20.0)))
        if yr == P.bridge_rear_y:
            t = t.cut(cyl(P.car_shaft_d + 2.0, (P.car_c[0], P.car_c[1], 600), (P.car_c[0], P.car_c[1], 800)))
        out.append(t)
    return Part.makeCompound(out)


def bridge_bolts():
    out = []
    for yr in (P.bridge_front_y, P.bridge_rear_y):
        yc = (yr[0] + yr[1]) / 2.0
        for sx in (-1, 1):
            out.append(bolt_z(10.0, sx * P.bridge_bolt_x, yc, P.robot_upper_beam_z[0], P.bridge_z[1]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Z axis (fixed part)
# ---------------------------------------------------------------------
def mast():
    """Mast plate 10 mm against the front bridge, with the bottom bearing block and the motor plate on top."""
    z0, z1 = P.mast_z
    plate = box_span((-P.mast_x, P.mast_x), P.mast_y, (z0, z1))
    for sx in (-1, 1):
        plate = plate.cut(cyl(8.4, (sx * 60.0, 40.0, P.bridge_z[0] + 20.0), (sx * 60.0, 120.0, P.bridge_z[0] + 20.0)))
    bottom = box_span((-30.0, 30.0), (P.screw_y - 18.0, P.mast_y[0]), (z0, z0 + 25.0))
    top = box_span((-45.0, 45.0), (P.screw_y - 40.0, P.mast_y[1]), (z1, z1 + 10.0))
    s = plate.fuse(bottom).fuse(top).removeSplitter()
    return s.cut(cyl(P.screw_d + 1.0, (0, P.screw_y, z0 - 1), (0, P.screw_y, z1 + 11)))


def mast_bolts():
    return Part.makeCompound([bolt_axis(8.0, (sx * 60.0, P.mast_y[0], P.bridge_z[0] + 20.0),
                                        (sx * 60.0, P.bridge_front_y[1], P.bridge_z[0] + 20.0), 13.0, 5.3, 6.8)
                              for sx in (-1, 1)])


def rails():
    """2 x SBR20: support (y 40..50) with the O20 shaft (centre y 30)."""
    z0, z1 = P.mast_z[0] + 30.0, P.mast_z[1] - 5.0
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        out.append(box_span((x - 12.0, x + 12.0), (P.rail_y[0] + 20.0, P.rail_y[1]), (z0, z1)))
        out.append(cyl(20.0, (x, P.rail_y[0] + 10.0, z0), (x, P.rail_y[0] + 10.0, z1)))
    return Part.makeCompound(out)


def screw():
    z0, z1 = P.mast_z
    return cyl(P.screw_d, (0, P.screw_y, z0 + 2.0), (0, P.screw_y, z1 + 40.0))


def z_motor():
    z1 = P.mast_z[1] + 10.0
    a, L = P.motor
    return Part.makeCompound([cyl(30.0, (0, P.screw_y, z1), (0, P.screw_y, z1 + 35.0)),
                              box_span((-a / 2.0, a / 2.0), (P.screw_y - a / 2.0, P.screw_y + a / 2.0),
                                       (z1 + 35.0, z1 + 35.0 + L))])


# ---------------------------------------------------------------------
# Carriage (moves in z): plate, 4 rail blocks, nut block, probe holder; probe and ejector
# ---------------------------------------------------------------------
def carriage():
    c = PARK_C
    h = P.carriage_h
    parts = [box_span((-P.carriage_w, P.carriage_w), (P.carriage_y[0], 0.0), (c, c + h)),
             box_span((-25.0, 25.0), (0.0, P.screw_y + 14.0), (c + 40.0, c + 100.0)),
             box_span((-60.0, 60.0), P.holder_y, (c, c + P.holder_h))]
    for sx in (-1, 1):
        for z in (c + 5.0, c + h - 45.0):
            parts.append(box_span((sx * P.rail_x - 22.0, sx * P.rail_x + 22.0), (0.0, P.rail_y[0]), (z, z + 40.0)))
    s = fuse_all(parts)
    s = s.cut(cyl(P.screw_d + 1.0, (0, P.screw_y, c - 1), (0, P.screw_y, c + h + 1)))
    s = s.cut(cyl(P.probe_d + 0.5, (0, P.probe_y, c - 1), (0, P.probe_y, c + P.holder_h + 1)))
    for sx in (-1, 1):
        s = s.cut(cyl(11.0, (sx * P.foot_rod_x, P.probe_y, c - 1), (sx * P.foot_rod_x, P.probe_y, c + P.holder_h + 1)))
    return s


def probe():
    """Gouge: tube O25 with a O19 bore, open along one side over the lower 160 mm, collar on top."""
    top = PARK_C + P.holder_h
    tip = top - P.probe_len
    t = shell(P.probe_d, P.probe_core_d, (0, P.probe_y, tip), (0, P.probe_y, top))
    t = t.cut(box_span((-6.0, 6.0), (P.probe_y - 20.0, P.probe_y - 4.0), (tip + 30.0, tip + 190.0)))
    return t.fuse(shell(P.probe_d + 10.0, P.probe_d, (0, P.probe_y, top), (0, P.probe_y, top + 10.0))).removeSplitter()


def ejector():
    """24 V actuator on a plate on top of the holder; its rod runs down inside the probe."""
    d, L = P.ejector
    z0 = PARK_C + P.holder_h + 10.0
    return Part.makeCompound([box_span((-30.0, 30.0), (P.probe_y - 25.0, P.probe_y + 25.0), (z0, z0 + 5.0)),
                              cyl(d, (0, P.probe_y, z0 + 5.0), (0, P.probe_y, z0 + 5.0 + L)),
                              cyl(10.0, (0, P.probe_y, z0 - 60.0), (0, P.probe_y, z0))])


# ---------------------------------------------------------------------
# Foot (moves with the carriage until it touches the ground)
# ---------------------------------------------------------------------
def foot():
    z0 = P.tip_park - P.foot_drop
    out = [shell(P.foot_d, P.probe_d + 6.0, (0, P.probe_y, z0), (0, P.probe_y, z0 + P.foot_t))]
    for sx in (-1, 1):
        x = sx * P.foot_rod_x
        ztop = z0 + P.foot_t + P.foot_rod_len
        out.append(cyl(10.0, (x, P.probe_y, z0 + P.foot_t), (x, P.probe_y, ztop)))
        out.append(cyl(18.0, (x, P.probe_y, ztop), (x, P.probe_y, ztop + 8.0)))
        out.append(shell(22.0, 14.0, (x, P.probe_y, z0 + P.foot_t), (x, P.probe_y, z0 + P.foot_t + 20.0)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Chute (turns about z at the chute pivot), servo, funnel, bracket
# ---------------------------------------------------------------------
def chute_ends():
    px, py = P.chute_pivot
    return (0.0, P.probe_y - 5.0, P.tip_park - 40.0), (px, py, P.funnel_z[1] + 15.0)


def chute():
    """Half pipe O50 (open at the top) from under the probe tip to above the funnel, and the servo arm."""
    a, b = chute_ends()
    L = (V(*b) - V(*a)).Length
    local = Part.makeCylinder(25.0, L, V(0, 0, 0), V(1, 0, 0)).cut(Part.makeCylinder(23.0, L, V(0, 0, 0), V(1, 0, 0)))
    local = local.cut(Part.makeBox(L + 2, 60, 30, V(-1, -30, 0)))
    trough = along(local, a, b)
    px, py = P.chute_pivot
    arm = box_span((px - 10.0, px + 10.0), (py - 10.0, py + 10.0), (b[2] - 25.0, P.funnel_z[1] + 70.0))
    return trough.fuse(arm).removeSplitter()


def chute_servo():
    px, py = P.chute_pivot
    z = P.funnel_z[1] + 70.0
    return box_span((px - 20.0, px + 20.0), (py - 30.0, py + 10.0), (z, z + 40.0))


def funnel():
    px, py = P.chute_pivot
    z0, z1 = P.funnel_z
    d1, d0 = P.funnel_d
    outer = Part.makeCone(d0 / 2.0 + 2.0, d1 / 2.0 + 2.0, z1 - z0, V(px, py, z0))
    inner = Part.makeCone(d0 / 2.0, d1 / 2.0, z1 - z0 + 0.02, V(px, py, z0 - 0.01))
    return outer.cut(inner)


def funnel_bracket():
    """Flat bar 30 x 6 from the rear bridge down to a tab on the funnel rim and the servo plate."""
    px, py = P.chute_pivot
    z1 = P.funnel_z[1]
    yb = py - P.funnel_d[0] / 2.0 - 30.0
    top = (0.0, P.bridge_rear_y[1] + 3.0, P.bridge_z[0] - 3.0)
    low = (0.0, yb + 3.0, z1 + 110.0 + 3.0)
    bar = rect_tube(top, low, 30.0, 6.0, up=(0.0, 1.0, 0.0))
    tab_v = box_span((-15.0, 15.0), (yb, yb + 6.0), (z1 - 4.0, z1 + 116.0))
    ring_tab = box_span((-15.0, 15.0), (yb, py - P.funnel_d[0] / 2.0 - 4.0), (z1 - 4.0, z1))
    servo_plate = box_span((-25.0, 25.0), (yb, py - 30.0), (z1 + 110.0, z1 + 116.0))
    return fuse_all([bar, tab_v, ring_tab, servo_plate])


# ---------------------------------------------------------------------
# Carousel (turns about z at car_c)
# ---------------------------------------------------------------------
def turntable():
    cx, cy = P.car_c
    t = cyl(P.car_d, (cx, cy, P.car_z), (cx, cy, P.car_z + P.car_t))
    hub = cyl(50.0, (cx, cy, P.car_z + P.car_t), (cx, cy, P.car_z + P.car_t + 30.0))
    return t.fuse(hub).removeSplitter().cut(cyl(P.car_shaft_d, (cx, cy, P.car_z + 10.0), (cx, cy, P.car_z + 40.0)))


def cups():
    cx, cy = P.car_c
    z0 = P.car_z + P.car_t
    out = []
    for i in range(P.n_cups):
        a = math.radians(90.0 + 360.0 * i / P.n_cups)
        x, y = cx + P.cup_r * math.cos(a), cy + P.cup_r * math.sin(a)
        out.append(cyl(P.cup_d, (x, y, z0), (x, y, z0 + P.cup_h)).cut(
            cyl(P.cup_d - 4.0, (x, y, z0 + 2.0), (x, y, z0 + P.cup_h + 1.0))))
    return Part.makeCompound(out)


def car_shaft():
    cx, cy = P.car_c
    return cyl(P.car_shaft_d, (cx, cy, P.car_z + 10.0), (cx, cy, P.bridge_z[1] + 30.0))


def car_drive():
    """Flange bearings on top and under the rear bridge, coupling, NEMA17 with 5:1 gearbox on top (fixed)."""
    cx, cy = P.car_c
    z = P.bridge_z[1]
    a, L = P.car_motor
    hole = cyl(P.car_shaft_d + 0.5, (cx, cy, 500), (cx, cy, z + 31))
    bearing = box_span((cx - 45.0, cx + 45.0), (cy - 20.0, cy + 20.0), (z, z + 12.0)).fuse(
        cyl(40.0, (cx, cy, z + 12.0), (cx, cy, z + 30.0))).cut(hole)
    lower = box_span((cx - 30.0, cx + 30.0), (cy - 20.0, cy + 20.0), (P.bridge_z[0] - 12.0, P.bridge_z[0])).cut(hole)
    motor = Part.makeCompound([cyl(25.0, (cx, cy, z + 30.0), (cx, cy, z + 70.0)),
                               box_span((cx - a / 2.0, cx + a / 2.0), (cy - a / 2.0, cy + a / 2.0),
                                        (z + 70.0, z + 110.0 + L))])
    return Part.makeCompound([bearing, lower, motor])
