"""Parts of the feed mixer wagon. Every function returns a Part shape in robot coordinates."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fmw_params as P
from ssp_parts import box_span, cyl_x, cyl_y, cyl_z, fuse_all, bolt_z

SIDES = (-1, 1)
CX, CY = P.bin_c
Z0 = P.bin_z0


def rect_tube_x(x0, x1, y, z, w, wall):
    o = box_span((x0, x1), (y - w / 2.0, y + w / 2.0), z)
    i = box_span((x0 + 3.0, x1 - 3.0), (y - w / 2.0 + wall, y + w / 2.0 - wall), (z[0] + wall, z[1] - wall))
    return o.cut(i)


def rect_tube_y(y0, y1, x, z, w, wall):
    o = box_span((x - w / 2.0, x + w / 2.0), (y0, y1), z)
    i = box_span((x - w / 2.0 + wall, x + w / 2.0 - wall), (y0 + 3.0, y1 - 3.0), (z[0] + wall, z[1] - wall))
    return o.cut(i)


# ---------------------------------------------------------------------
# Frame and weighing
# ---------------------------------------------------------------------
BOLTS = [(x, y) for y in P.cross_y for x in P.robot_upper_beam_x]


def cross_tubes():
    w, h, wall = P.cross
    out = [rect_tube_x(-P.cross_half, P.cross_half, y, P.cross_z, w, wall) for y in P.cross_y]
    return Part.makeCompound(out).cut([cyl_z(P.m10_hole, P.cross_z[0] - 1, P.cross_z[1] + 1, x, y) for (x, y) in BOLTS])


def cross_bolts():
    return Part.makeCompound([bolt_z(x, y, P.cross_z[1], P.robot_upper_beam_z[0], k=4.0) for (x, y) in BOLTS])


def load_cells():
    """Single-point shear beams: the fixed end bolted on the cross tube, the load end under the sub-frame."""
    cx, cy, cz = P.cell
    out = []
    for x in P.cell_x:
        for y in P.cross_y:
            out.append(box_span((x - cx / 2.0, x + cx / 2.0), (y - cy / 2.0, y + cy / 2.0), P.cell_z))
    return Part.makeCompound(out)


def sub_frame():
    a = P.sub
    y0, y1 = P.cross_y
    xs = P.sub_x
    out = [rect_tube_x(-xs - a / 2.0, xs + a / 2.0, y, P.sub_z, a, 3.0) for y in (y0, y1)]
    out += [rect_tube_y(y0 + a / 2.0, y1 - a / 2.0, s * xs, P.sub_z, a, 3.0) for s in SIDES]
    return fuse_all(out)


def floor():
    xs = P.sub_x + P.sub / 2.0
    pl = box_span((-xs, xs), (P.cross_y[0] - P.sub / 2.0, P.cross_y[1] + P.sub / 2.0), P.floor_z)
    pl = pl.fuse(cyl_z(2 * P.bin_r[0] + 20.0, P.floor_z[0], P.floor_z[1], CX, CY))
    return pl.cut(cyl_z(P.shaft_d + 4.0, P.floor_z[0] - 1, P.floor_z[1] + 1, CX, CY))


def junction_box():
    return box_span((-60.0, 60.0), (P.cross_y[1] - 30.0 - 60.0, P.cross_y[1] - 30.0), (P.sub_z[0], P.sub_z[1]))


# ---------------------------------------------------------------------
# Bin with the door opening
# ---------------------------------------------------------------------
def _cone(r0, r1, z0, h):
    return Part.makeCone(r0, r1, h, V(CX, CY, z0))


def _door_cut():
    """Wedge around +x of door_a degrees between door_z."""
    a = math.radians(P.door_a / 2.0)
    r = P.bin_r[1] + 100.0
    pts = [V(CX, CY, P.door_z[0]), V(CX + r * math.cos(a), CY - r * math.sin(a), P.door_z[0]),
           V(CX + r * math.cos(a), CY + r * math.sin(a), P.door_z[0])]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, P.door_z[1] - P.door_z[0]))


def bin_shell():
    t = P.bin_t
    o = _cone(P.bin_r[0], P.bin_r[1], Z0, P.bin_h)
    i = _cone(P.bin_r[0] - t, P.bin_r[1] - t, Z0 - 1.0, P.bin_h + 2.0)
    shell = o.cut(i).cut(_door_cut())
    rw, rt = P.rim
    rim = cyl_z(2 * (P.bin_r[1] + rw), Z0 + P.bin_h - rt, Z0 + P.bin_h, CX, CY).cut(
        cyl_z(2 * (P.bin_r[1] - t), Z0 + P.bin_h - rt - 1, Z0 + P.bin_h + 1, CX, CY))
    return fuse_all([shell, rim])


def _r_at(z):
    return P.bin_r[0] + (P.bin_r[1] - P.bin_r[0]) * (z - Z0) / P.bin_h


TILT = math.degrees(math.atan((P.bin_r[1] - P.bin_r[0]) / P.bin_h))     # cone wall from vertical
R0 = None


def _tilt(shape):
    """Door parts are drawn as if the wall at +x were vertical (radius r at door_z[0]); turn them about the y axis
    through the wall point at the door bottom so they lie along the sloping cone wall."""
    r0 = _r_at(P.door_z[0])
    shape.rotate(V(CX + r0, CY, P.door_z[0]), V(0, 1, 0), TILT)
    return shape


def slide_dir():
    a = math.radians(TILT)
    return V(math.sin(a), 0.0, math.cos(a))


def _door_geo():
    a = math.radians(P.door_a / 2.0)
    r0 = _r_at(P.door_z[0])
    x = CX + r0 + 6.0
    yw = (P.bin_r[0] + 40.0) * math.sin(a) + 20.0
    h = (P.door_z[1] - P.door_z[0]) / math.cos(math.radians(TILT))
    return r0, x, yw, h


def door():
    """Flat door just outside the opening, sliding up along the cone wall on 2 guides."""
    r0, x, yw, h = _door_geo()
    z0 = P.door_z[0]
    return _tilt(box_span((x, x + P.door_t), (CY - yw, CY + yw), (z0 - 3.0, z0 + h + 15.0)))   # just above the chute


def door_guides():
    r0, x, yw, h = _door_geo()
    z0 = P.door_z[0]
    out = []
    for s in SIDES:
        y = CY + s * (yw + 10.0)
        out.append(box_span((x - 4.0, x + P.door_t + 6.0), (y - 10.0, y + 10.0), (z0 - 10.0, z0 + h + P.door_lift + 30.0)))
        xin = CX + math.sqrt(max(r0 * r0 - (y - CY) ** 2, 0.0)) - 8.0
        for z in (z0 - 10.0, z0 + h + P.door_lift + 10.0):
            out.append(box_span((xin, x - 4.0), (y - 8.0, y + 8.0), (z, z + 20.0)))
    return _tilt(Part.makeCompound(out))


def _act_x():
    r0, x, yw, h = _door_geo()
    return x + P.door_t + 25.0


def actuator_body():
    r0, x, yw, h = _door_geo()
    ztop = P.door_z[0] + h
    return _tilt(cyl_z(40.0, ztop + 40.0, ztop + 40.0 + 260.0, _act_x(), CY))


def door_actuator_rod():
    """Rod (60 mm inside the body when closed) and the lug on the door top; moves with the door."""
    r0, x, yw, h = _door_geo()
    ztop = P.door_z[0] + h
    xa = _act_x()
    rod = cyl_z(16.0, ztop - 10.0, ztop + 100.0, xa, CY)
    lug = box_span((x + P.door_t, xa + 10.0), (CY - 10.0, CY + 10.0), (ztop - 10.0, ztop + 5.0))
    return _tilt(fuse_all([rod, lug]))


def act_bracket():
    """From the bin wall out to the top of the door actuator."""
    r0, x, yw, h = _door_geo()
    z = P.door_z[0] + h + 40.0 + 260.0
    xa = _act_x()
    return _tilt(box_span((CX + r0 - 8.0, xa + 25.0), (CY - 15.0, CY + 15.0), (z, z + 8.0)))


def chute():
    """Sloped plate from under the door out to x 720, with side walls; 2 struts to the sub-frame."""
    w = P.chute_w
    x0, x1 = P.chute_x
    z0, z1 = P.chute_z
    pts = [V(x0, CY - w / 2.0, z0), V(x1, CY - w / 2.0, z1), V(x1, CY + w / 2.0, z1), V(x0, CY + w / 2.0, z0)]
    plate = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, -P.chute_t))
    sides = []
    for s in SIDES:
        y = CY + s * w / 2.0
        xs = CX + _r_at(P.door_z[1]) + 6.0 + P.door_t + 12.0         # outside the door and its guides
        zs = z0 + (z1 - z0) * (xs - x0) / (x1 - x0)
        q = [V(xs, y, zs), V(x1, y, z1), V(x1, y, z1 + P.chute_side_h), V(xs, y, zs + P.chute_side_h)]
        sides.append(Part.Face(Part.makePolygon(q + [q[0]])).extrude(V(0, -s * P.chute_t, 0)))
    struts = []
    for s in SIDES:
        y = CY + s * (w / 2.0 - 20.0)
        p0 = V(P.sub_x + P.sub / 2.0, y, P.sub_z[0] + 10.0)
        xm = x0 + 0.55 * (x1 - x0)
        p1 = V(xm, y, z0 + 0.55 * (z1 - z0) - P.chute_t - 1.0)
        struts.append(Part.makeCylinder(8.0, (p1 - p0).Length, p0, p1 - p0))
    return fuse_all([plate] + sides + struts)


# ---------------------------------------------------------------------
# Auger (sub-Part, turns about the bin axis)
# ---------------------------------------------------------------------
def shaft():
    return fuse_all([cyl_z(P.shaft_d, P.floor_z[0] - 20.0, P.shaft_top, CX, CY),
                     Part.makeCone(P.shaft_d / 2.0, 5.0, 60.0, V(CX, CY, P.shaft_top))])


def _flight_r(z):
    f = (z - P.flight_z[0]) / (P.flight_z[1] - P.flight_z[0])
    return P.flight_r[0] + (P.flight_r[1] - P.flight_r[0]) * f


def flight():
    """Conical flight as a staircase of annular sectors (flight_steps per turn), rising along the turns."""
    n = int(P.flight_turns * P.flight_steps)
    dz = (P.flight_z[1] - P.flight_z[0]) / n
    da = 360.0 / P.flight_steps
    out = []
    for i in range(n):
        z = P.flight_z[0] + i * dz
        r = _flight_r(z)
        sec = Part.makeCylinder(r, P.flight_t, V(0, 0, 0), V(0, 0, 1), da + 1.0)
        sec = sec.cut(Part.makeCylinder(P.shaft_d / 2.0 - 1.0, P.flight_t + 2.0, V(0, 0, -1)))
        sec.rotate(V(0, 0, 0), V(0, 0, 1), i * da)
        sec.translate(V(CX, CY, z))
        out.append(sec)
    return Part.makeCompound(out)


def knives():
    """2 knives on the flight edge, half a turn apart, in the lower turn."""
    lx, ly, t = P.knife
    out = []
    for i in (4, 16):
        dz = (P.flight_z[1] - P.flight_z[0]) / (P.flight_turns * P.flight_steps)
        z = P.flight_z[0] + i * dz
        r = _flight_r(z)
        k = box_span((r + 30.0 - lx, r + 30.0), (-ly / 2.0, ly / 2.0), (P.flight_t, P.flight_t + t))
        k.rotate(V(0, 0, 0), V(0, 0, 1), i * 360.0 / P.flight_steps + 7.5)
        k.translate(V(CX, CY, z))
        out.append(k)
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Drive
# ---------------------------------------------------------------------
def gearbox():
    gx, gy, gz = P.gearbox
    box = box_span((CX - gx / 2.0, CX + gx / 2.0), (CY - gy / 2.0, CY + gy / 2.0), (P.floor_z[0] - gz, P.floor_z[0]))
    return box


def motor():
    body = cyl_y(P.motor_d, P.motor_y[0], P.motor_y[1], CX, P.motor_z)
    fins = [cyl_y(P.motor_d + 8.0, y, y + 6.0, CX, P.motor_z) for y in (P.motor_y[0] + 40.0, P.motor_y[0] + 100.0)]
    return fuse_all([body] + fins)


# ---------------------------------------------------------------------
# Render only
# ---------------------------------------------------------------------
def feed_fill(level=0.85):
    """Feed in the bin up to a level (share of the height), as a cone frustum with a heap on top."""
    h = P.bin_h * level
    r1 = _r_at(Z0 + h) - P.bin_t - 2.0
    c = Part.makeCone(P.bin_r[0] - P.bin_t - 2.0, r1, h, V(CX, CY, Z0 + 1.0))
    heap = Part.makeCone(r1, 60.0, 90.0, V(CX, CY, Z0 + h))
    return c.fuse(heap).cut(_door_cut())


def feed_row(y0, y1, x=850.0):
    """A windrow of feed along the fence."""
    out = []
    for yy in range(int(y0), int(y1), 120):
        out.append(Part.makeSphere(110.0, V(x + 20.0 * ((yy // 120) % 3 - 1), yy, 20.0)))
    return Part.makeCompound(out)


def fence(y0, y1, x=1150.0):
    out = [box_span((x, x + 60.0), (y, y + 60.0), (0.0, 1300.0)) for y in range(int(y0), int(y1), 1500)]
    out += [box_span((x, x + 50.0), (y0, y1), (z, z + 50.0)) for z in (700.0, 1150.0)]
    out.append(box_span((x - 450.0, x + 200.0), (y0, y1), (-40.0, 0.0)))
    return Part.makeCompound(out)
