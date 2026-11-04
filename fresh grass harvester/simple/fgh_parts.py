"""Parts of the fresh grass harvester. Every function returns a Part shape in robot coordinates."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fgh_params as P
from ssp_parts import box_span, cyl_x, cyl_y, cyl_z, fuse_all, bolt_z

SIDES = (-1, 1)


def rect_tube_y(y0, y1, x, z, w, wall):
    o = box_span((x - w / 2.0, x + w / 2.0), (y0, y1), z)
    i = box_span((x - w / 2.0 + wall, x + w / 2.0 - wall), (y0 + 3.0, y1 - 3.0), (z[0] + wall, z[1] - wall))
    return o.cut(i)


def rect_tube_x(x0, x1, y, z, w, wall):
    o = box_span((x0, x1), (y - w / 2.0, y + w / 2.0), z)
    i = box_span((x0 + 3.0, x1 - 3.0), (y - w / 2.0 + wall, y + w / 2.0 - wall), (z[0] + wall, z[1] - wall))
    return o.cut(i)


# ---------------------------------------------------------------------
# Front arms, trough, auger, cutter bar
# ---------------------------------------------------------------------
ARM_BOLTS = [(s * P.arm_x, y) for s in SIDES for y in P.arm_bolt_y]


def arms():
    w, h, t = P.arm
    out = [rect_tube_y(P.arm_y[0], P.arm_y[1], s * P.arm_x, P.arm_z, w, t) for s in SIDES]
    return Part.makeCompound(out).cut([cyl_z(P.m10_hole, P.arm_z[0] - 1, P.arm_z[1] + 1, x, y) for (x, y) in ARM_BOLTS])


def arm_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], P.arm_z[0]) for (x, y) in ARM_BOLTS])


Y_REAR = P.auger_y - P.trough_r - P.trough_t      # outside of the trough rear wall


def drop_plates():
    """8 mm plates from the arm ends down the back of the trough rear wall."""
    t, d = P.drop_plate
    return Part.makeCompound([box_span((s * P.arm_x - t / 2.0, s * P.arm_x + t / 2.0), (Y_REAR - d, Y_REAR),
                                       (P.auger_z, P.arm_z[0])) for s in SIDES])


def trough():
    """Rear wall up to z 330, a quarter-round bottom (rear -> bottom), a flat floor forward to the cutter bar, end plate
    on the left (the right end opens into the elevator foot)."""
    r, t = P.trough_r, P.trough_t
    x0, x1 = P.trough_x
    yc, zc = P.auger_y, P.auger_z
    ring = cyl_x(2 * (r + t), x0, x1, yc, zc).cut(cyl_x(2 * r, x0 - 1, x1 + 1, yc, zc))
    quarter = ring.common(box_span((x0, x1), (yc - r - t - 1, yc), (zc - r - t - 1, zc)))
    rear = box_span((x0, x1), (yc - r - t, yc - r), (zc, P.rear_wall_top))
    floor = box_span((x0, x1), (yc, P.bar_y[0]), (zc - r - t, zc - r))
    end = box_span((x0 - t, x0), (yc - r - t, P.bar_y[0]), (zc - r - t, P.rear_wall_top))
    return fuse_all([quarter, rear, floor, end])


def auger_shaft():
    return cyl_x(40.0, P.auger_x[0] - 15.0, P.auger_x[1] - 2.0, P.auger_y, P.auger_z)


def auger_flight():
    """Staircase helix of annular sectors (24 per turn) around the x axis, pushing toward +x."""
    steps = 24
    n = int((P.auger_x[1] - P.auger_x[0]) / P.auger_pitch * steps)
    dx = P.auger_pitch / steps
    out = []
    for i in range(n):
        x = P.auger_x[0] + i * dx
        sec = Part.makeCylinder(P.auger_d / 2.0, P.flight_t, V(0, 0, 0), V(0, 0, 1), 16.0)
        sec = sec.cut(Part.makeCylinder(19.0, P.flight_t + 2.0, V(0, 0, -1)))
        sec.rotate(V(0, 0, 0), V(0, 0, 1), i * 15.0)
        sec.rotate(V(0, 0, 0), V(0, 1, 0), 90.0)       # axis z -> x
        sec.translate(V(x, P.auger_y, P.auger_z))
        out.append(sec)
    return Part.makeCompound(out)


def cutter_bar():
    """Flat bar on the trough floor's front edge, knife sections (triangles) and guard fingers."""
    bar = box_span(P.bar_x, P.bar_y, P.bar_z)
    secs = []
    n = int((P.bar_x[1] - P.bar_x[0]) / P.section_pitch)
    for i in range(n):
        x = P.bar_x[0] + (i + 0.5) * P.section_pitch
        pts = [V(x - P.section_pitch / 2.0 + 3, P.bar_y[1], P.bar_z[1]), V(x + P.section_pitch / 2.0 - 3, P.bar_y[1], P.bar_z[1]),
               V(x + 6, P.bar_y[1] + P.section_len, P.bar_z[1]), V(x - 6, P.bar_y[1] + P.section_len, P.bar_z[1])]
        secs.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, 3.0)))
        g = [V(x - 8, P.bar_y[1], P.bar_z[0] - 6), V(x + 8, P.bar_y[1], P.bar_z[0] - 6),
             V(x + 3, P.bar_y[1] + P.section_len + 25, P.bar_z[0] + 4), V(x - 3, P.bar_y[1] + P.section_len + 25, P.bar_z[0] + 4)]
        secs.append(Part.Face(Part.makePolygon(g + [g[0]])).extrude(V(0, 0, 6.0)))
    return fuse_all([bar] + secs)


def skids():
    sx, sy, h = P.skid
    return Part.makeCompound([box_span((x - sx / 2.0, x + sx / 2.0), (P.bar_y[1] - sy, P.bar_y[1] + 40.0), (0.0, P.bar_z[0]))
                              for x in P.skid_x])


def sickle_drive():
    (x0, x1), (y0, y1), (z0, z1) = P.sickle_drive
    box = box_span((x0, x1), (y0, y1), (z0, z0 + 90.0))
    mot = cyl_z(80.0, z0 + 90.0, z1, 0.5 * (x0 + x1), 0.5 * (y0 + y1))
    return fuse_all([box, mot])


# ---------------------------------------------------------------------
# Elevator: local frame (x across, s along the belt from the lower roller, n normal up from the belt)
# ---------------------------------------------------------------------
_S = V(0.5 * (P.elev_x[0] + P.elev_x[1]), P.elev_s[0], P.elev_s[1])
_E = V(_S.x, P.elev_e[0], P.elev_e[1])
U = (_E - _S) * (1.0 / (_E - _S).Length)          # along the belt, up and back
N = V(0.0, U.z, -U.y)                             # normal to the belt, up and forward
ELEN = (_E - _S).Length
EW = P.elev_x[1] - P.elev_x[0]


def _M():
    """Local (x, s, n) -> world. Columns X = (-1, 0, 0), U, N (right-handed); origin at the lower roller axis."""
    return App.Matrix(-1.0, U.x, N.x, _S.x,
                      0.0, U.y, N.y, _S.y,
                      0.0, U.z, N.z, _S.z,
                      0.0, 0.0, 0.0, 1.0)


def _loc(shape):
    return shape.transformGeometry(_M())


def lbox(x, s, n):
    return _loc(box_span(x, s, n))


def elevator_channel():
    """Bottom plate under the belt return, 2 side walls; local x = -EW/2 .. EW/2."""
    w = EW / 2.0
    r = P.roller_d / 2.0
    s = (-r - 40.0, ELEN + r + 20.0)
    bottom = box_span((-w, w), s, (-r - 15.0 - P.elev_t, -r - 15.0))
    walls = [box_span((x0, x0 + P.elev_t), s, (-r - 15.0 - P.elev_t, r + P.elev_wall)) for x0 in (-w, w - P.elev_t)]
    return _loc(fuse_all([bottom] + walls))


def belt():
    w = EW / 2.0 - P.elev_t - 5.0
    r = P.roller_d / 2.0
    top = box_span((-w, w), (0.0, ELEN), (r, r + 4.0))
    ret = box_span((-w, w), (0.0, ELEN), (-r - 4.0, -r))
    slats = []
    s = 40.0
    while s < ELEN - 30.0:
        slats.append(box_span((-w, w), (s, s + P.slat[0]), (r + 4.0, r + 4.0 + P.slat[1])))
        s += P.slat_pitch
    return _loc(fuse_all([top, ret] + slats))


def rollers():
    w = EW / 2.0 - P.elev_t
    r = P.roller_d / 2.0
    return _loc(Part.makeCompound([Part.makeCylinder(r - 0.5, 2 * w, V(-w, s, 0), V(1, 0, 0)) for s in (0.0, ELEN)]))


def elevator_motor():
    """On the upper roller, outside the right side wall (local x < -EW/2 -> world x > elev_x[1])."""
    d, ln = P.elev_motor
    w = EW / 2.0
    return _loc(Part.makeCylinder(d / 2.0, ln, V(-w - ln, ELEN, 0), V(1, 0, 0)))


def spout():
    """Chute from the elevator top inward over the container: bottom plate and 2 side walls, sloping down inward."""
    r = P.roller_d / 2.0
    top = _E + N * (r + 10.0)
    y0, y1 = top.y - 160.0, top.y + 160.0
    x0, x1 = P.spout_x
    z1 = top.z - 40.0
    z0 = z1 - P.spout_drop
    pts = [V(x1, y0, z1), V(x0, y0, z0), V(x0, y1, z0), V(x1, y1, z1)]
    plate = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, -3.0))
    walls = []
    for y in (y0, y1 - 3.0):
        q = [V(x1, y, z1), V(x0, y, z0), V(x0, y, z0 + 120.0), V(x1, y, z1 + 120.0)]
        walls.append(Part.Face(Part.makePolygon(q + [q[0]])).extrude(V(0, 3.0, 0)))
    return fuse_all([plate] + walls)


def stay():
    """Strut O30 from the right end of the cross tube at y 275 up to the elevator underside at 3/4 length."""
    r = P.roller_d / 2.0
    p1 = _S + U * (0.75 * ELEN) - N * (r + 15.0 + P.elev_t)
    p1 = V(P.elev_x[0] + 60.0, p1.y, p1.z)
    p0 = V(P.cross_x[1] - 20.0, P.stay_y, P.cross_z[1])
    rod = Part.makeCylinder(15.0, (p1 - p0).Length, p0, p1 - p0)
    foot = box_span((p0.x - 25.0, p0.x + 25.0), (p0.y - 25.0, p0.y + 25.0), (P.cross_z[1], P.cross_z[1] + 8.0))
    return fuse_all([rod, foot])


# ---------------------------------------------------------------------
# Container
# ---------------------------------------------------------------------
BOLTS = [(x, y) for y in P.cross_y for x in P.robot_upper_beam_x]


def cross_tubes():
    w, h, wall = P.cross
    out = [rect_tube_x(P.cross_x[0], P.cross_x[1], y, P.cross_z, w, wall) for y in P.cross_y]
    return Part.makeCompound(out).cut([cyl_z(P.m10_hole, P.cross_z[0] - 1, P.cross_z[1] + 1, x, y) for (x, y) in BOLTS])


def cross_bolts():
    return Part.makeCompound([bolt_z(x, y, P.cross_z[1], P.robot_upper_beam_z[0], k=4.0) for (x, y) in BOLTS])


def hinge_brackets():
    hx, hz = P.hinge
    out = []
    for y in P.box_cross_y:
        out.append(box_span((hx - 14.0, hx + 14.0), (y + 32.0, y + 40.0), (P.cross_z[1], hz + 14.0)))
    return Part.makeCompound(out).cut(cyl_y(16.5, P.box_y[0] - 50.0, P.box_y[1] + 50.0, hx, hz))


def hinge_pins():
    hx, hz = P.hinge
    return Part.makeCompound([cyl_y(16.0, y + 20.0, y + 50.0, hx, hz) for y in P.box_cross_y])


def tip_frame():
    """Ring 40 x 40 under the container, with hinge lugs on the left."""
    a = 40.0
    x0, x1 = P.box_x
    y0, y1 = P.box_y
    z = P.tip_frame_z
    ring = [rect_tube_x(x0, x1, y, z, a, 3.0) for y in (y0 + a / 2.0, y1 - a / 2.0)]
    ring += [rect_tube_y(y0 + a, y1 - a, x, z, a, 3.0) for x in (x0 + a / 2.0, x1 - a / 2.0)]
    ring += [rect_tube_x(x0, x1, y, z, a, 3.0) for y in P.cross_y if y0 + a < y < y1 - a]
    hx, hz = P.hinge
    lugs = [box_span((hx - 20.0, x0 + 20.0), (y + 20.0, y + 30.0), (hz - 20.0, z[1])) for y in P.box_cross_y]
    s = fuse_all(ring + lugs)
    return s.cut(cyl_y(16.5, y0 - 50.0, y1 + 50.0, hx, hz))


def container():
    x0, x1 = P.box_x
    y0, y1 = P.box_y
    z0, z1 = P.box_z
    t = P.box_t
    o = box_span((x0, x1), (y0, y1), (z0, z1))
    i = box_span((x0 + t, x1 - t), (y0 + t, y1 - t), (z0 + t, z1 + 1))
    rim = box_span((x0 - 15.0, x1 + 15.0), (y0 - 15.0, y1 + 15.0), (z1 - 25.0, z1)).cut(box_span((x0, x1), (y0, y1), (z1 - 26, z1 + 1)))
    lugs = [box_span((x1, P.act_x + 10.0), (y - 10.0, y + 10.0), (1060.0, 1080.0)) for y in P.box_cross_y]
    return fuse_all([o.cut(i), rim] + lugs)


def tip_actuators():
    d, ln = P.act_body
    return Part.makeCompound([cyl_z(d, P.cross_z[1], P.cross_z[1] + ln, P.act_x, y) for y in P.box_cross_y] +
                             [cyl_z(20.0, P.cross_z[1] + ln, 1062.0, P.act_x, y) for y in P.box_cross_y])


def ballast():
    """60 kg block behind the robot, bolted to the back face of the rear cross tube (2 x M12)."""
    x, y, z = P.ballast
    blk = box_span(x, y, z)
    return blk


# ---------------------------------------------------------------------
# Render only
# ---------------------------------------------------------------------
def grass_field(y0, y1, cut_y, x=(-1500.0, 1500.0)):
    out = [box_span(x, (y0, y1), (-40.0, 0.0))]
    k = 0
    for yy in range(int(y0), int(y1), 60):
        for xx in range(int(x[0]) + 20, int(x[1]), 60):
            k += 1
            h = 220.0 + 80.0 * ((k * 37) % 5) / 4.0
            if yy < cut_y and P.bar_x[0] < xx < P.bar_x[1]:
                h = 50.0
            out.append(Part.makeCylinder(5.0, h, V(xx + 12.0 * ((k * 13) % 3 - 1), yy, 0)))
    return Part.makeCompound(out)


def grass_load(level=0.7):
    x0, x1 = P.box_x
    y0, y1 = P.box_y
    z0, z1 = P.box_z
    h = (z1 - z0) * level
    return box_span((x0 + 4, x1 - 4), (y0 + 4, y1 - 4), (z0 + 4, z0 + h))
