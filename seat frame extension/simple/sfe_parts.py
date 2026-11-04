"""Parts of the seat, canopy and frame extension. Every function returns a Part shape in robot coordinates."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import sfe_params as P


def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), V(0, 0, 1))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), V(1, 0, 0))


def cyl_y(d, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), V(0, 1, 0))


def fuse_all(shapes):
    shapes = list(shapes)
    r = shapes[0].fuse(shapes[1:]) if len(shapes) > 1 else shapes[0]
    try:
        return r.removeSplitter()
    except Exception:
        return r


def hex_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    return fuse_all([hex_z(af, z_head, z_head + k, x, y), cyl_z(d, z_nut - m - 4.0, z_head, x, y),
                     hex_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))])


def pipe(p0, p1, d, wall):
    p0, p1 = V(*p0), V(*p1)
    o = Part.makeCylinder(d / 2.0, (p1 - p0).Length, p0, p1 - p0)
    i = Part.makeCylinder(d / 2.0 - wall, (p1 - p0).Length + 2.0, p0 - (p1 - p0).normalize(), p1 - p0)
    return o.cut(i)


TZ = P.tube_z
BEAM_X = P.robot_upper_beam_x
BOLTS = [(x, y) for y in P.CROSS for x in BEAM_X]


# ---------------------------------------------------------------------
# Cross tubes and side extensions
# ---------------------------------------------------------------------
def cross_tubes():
    out = []
    for y, half in P.CROSS.items():
        o = box_span((-half, half), (y - P.tube / 2.0, y + P.tube / 2.0), TZ)
        i = box_span((-half + P.end_cap_t, half - P.end_cap_t), (y - P.tube / 2.0 + P.tube_wall, y + P.tube / 2.0 - P.tube_wall),
                     (TZ[0] + P.tube_wall, TZ[1] - P.tube_wall))
        t = o.cut(i)
        holes = [cyl_z(P.m10_hole, TZ[0] - 1, TZ[1] + 1, x, y) for x in BEAM_X]
        if half > 500.0:
            holes += [cyl_z(P.m10_hole, TZ[0] - 1, TZ[1] + 1, s * x, y) for x in P.ext_holes_x for s in (-1, 1)]
            holes += [cyl_z(P.m10_hole, TZ[0] - 1, TZ[1] + 1, s * P.rops_x + dx, y) for s in (-1, 1)
                      for dx in (-35.0, 35.0)] if y == RY else []
        out.append(t.cut(holes))
    return Part.makeCompound(out)


def cross_bolts():
    """M10 through each tube and the upper beam (button head on the tube, nut under the beam)."""
    return Part.makeCompound([bolt_z(x, y, TZ[1], P.robot_upper_beam_z[0], k=4.0) for (x, y) in BOLTS])


# ---------------------------------------------------------------------
# Seat
# ---------------------------------------------------------------------
PLATE_Z = (TZ[1], TZ[1] + P.seat_plate[2])
PED_TOP = PLATE_Z[1] + P.pedestal[1]
PAN_Z = (PED_TOP, PED_TOP + P.seat_pan[2])


def seat_plate():
    (x0, x1), (y0, y1), t = P.seat_plate
    pl = box_span((x0, x1), (y0, y1), PLATE_Z)
    return pl.cut([cyl_z(14.0, PLATE_Z[0] - 1, PLATE_Z[1] + 1, x, P.seat_y + dy) for x in (-50.0, 50.0)
                   for dy in (-50.0, 50.0)])


def pedestal():
    a, h = P.pedestal
    y = P.seat_y
    t = box_span((-a / 2.0, a / 2.0), (y - a / 2.0, y + a / 2.0), (PLATE_Z[1], PED_TOP - 10.0)).cut(
        box_span((-a / 2.0 + 4.0, a / 2.0 - 4.0), (y - a / 2.0 + 4.0, y + a / 2.0 - 4.0), (PLATE_Z[1] - 1, PED_TOP)))
    foot = box_span((-80.0, 80.0), (y - 80.0, y + 80.0), (PLATE_Z[1], PLATE_Z[1] + 8.0))
    slide = box_span((-150.0, 150.0), (y - 180.0, y + 180.0), (PED_TOP - 10.0, PED_TOP))
    return fuse_all([t, foot, slide])


def seat():
    """Tractor seat: cushion, back tilted back, 2 armrests."""
    w, d, t = P.seat_pan
    y = P.seat_y
    pan = box_span((-w / 2.0, w / 2.0), (y - d / 2.0, y + d / 2.0), PAN_Z)
    bw, bt, bh = P.seat_back
    back = box_span((-bw / 2.0, bw / 2.0), (-bt, 0.0), (0.0, bh))
    back.rotate(V(0, 0, 0), V(1, 0, 0), -P.seat_back_tilt)
    back.translate(V(0, y - d / 2.0 + bt, PAN_Z[1] - 20.0))
    ax, ay, az = P.armrest
    arms = [box_span((s * (w / 2.0 + 5.0), s * (w / 2.0 + 5.0 + ax)), (y - ay / 2.0, y + ay / 2.0),
                     (PAN_Z[1] + 180.0, PAN_Z[1] + 180.0 + az)) for s in (-1, 1)]
    posts = [box_span((s * (w / 2.0 + 5.0 + ax / 2.0) - 10.0, s * (w / 2.0 + 5.0 + ax / 2.0) + 10.0),
                      (y - ay / 2.0 + 20.0, y - ay / 2.0 + 40.0), (PAN_Z[0], PAN_Z[1] + 180.0)) for s in (-1, 1)]
    return fuse_all([pan, back] + arms + posts)


CON_X = P.seat_pan[0] / 2.0 + 5.0 + P.armrest[0] / 2.0
CON_Z = PAN_Z[1] + 180.0 + P.armrest[2]


def console():
    cx, cy, cz = P.console
    y = P.seat_y + P.armrest[1] / 2.0 - cy / 2.0 + 40.0
    return box_span((CON_X - cx / 2.0, CON_X + cx / 2.0), (y - cy / 2.0, y + cy / 2.0), (CON_Z, CON_Z + cz))


def joystick():
    d, ln, k = P.joystick
    cx, cy, cz = P.console
    y = P.seat_y + P.armrest[1] / 2.0 - cy / 2.0 + 40.0
    z0 = CON_Z + cz
    return fuse_all([cyl_z(30.0, z0, z0 + 15.0, CON_X, y + 30.0), cyl_z(d, z0, z0 + ln, CON_X, y + 30.0),
                     Part.makeSphere(k / 2.0, V(CON_X, y + 30.0, z0 + ln))])


def estop():
    d, h = P.estop
    cx, cy, cz = P.console
    y = P.seat_y + P.armrest[1] / 2.0 - cy / 2.0 + 40.0
    z0 = CON_Z + cz
    return fuse_all([cyl_z(36.0, z0, z0 + h * 0.6, CON_X, y - 40.0), cyl_z(d, z0 + h * 0.6, z0 + h, CON_X, y - 40.0)])


# ---------------------------------------------------------------------
# Footplate
# ---------------------------------------------------------------------
def footplate():
    (x0, x1), (y0, y1), t = P.foot
    pl = box_span((x0, x1), (y0, y1), (TZ[1], TZ[1] + t))
    toe = box_span((x0, x1), (y1 - t, y1), (TZ[1], TZ[1] + P.toe_h))
    s = fuse_all([pl, toe])
    return s.cut([cyl_z(P.m10_hole, TZ[1] - 1, TZ[1] + t + 1, x, y) for (x, y) in BOLTS if y0 < y < y1 and x0 < x < x1])


# ---------------------------------------------------------------------
# Roll bar and canopy
# ---------------------------------------------------------------------
RY = -625.0
RZ0 = TZ[1] + P.rops_foot[2]


def rops():
    """Hoop: 2 legs from foot plates on the rear long tube up to the top, a crossbar, a brace to the seat plate tube."""
    d, w = P.rops_d, P.rops_wall
    r = 150.0
    top = P.rops_top - d / 2.0
    parts = []
    for s in (-1, 1):
        x = s * P.rops_x
        parts.append(pipe((x, RY, RZ0), (x, RY, top - r), d, w))
        fx, fy, ft = P.rops_foot
        parts.append(box_span((x - fx / 2.0, x + fx / 2.0), (RY - fy / 2.0, RY + fy / 2.0), (TZ[1], RZ0)).cut(
            Part.makeCompound([cyl_z(P.m10_hole, TZ[1] - 1, RZ0 + 1, x + dx, RY) for dx in (-35.0, 35.0)])))
        bend = Part.makeTorus(r, d / 2.0, V(x - s * r, RY, top - r), V(0, 1, 0)).common(
            box_span((x - s * r, x + s * (d / 2.0 + 1.0)), (RY - d, RY + d), (top - r, top + d / 2.0 + 1.0)))
        parts.append(bend)
    parts.append(pipe((-P.rops_x + r, RY, top), (P.rops_x - r, RY, top), d, w))
    return fuse_all(parts)


def rops_bolts():
    return Part.makeCompound([bolt_z(s * P.rops_x + dx, RY, RZ0, TZ[0]) for s in (-1, 1) for dx in (-35.0, 35.0)])


def canopy_rails():
    """2 rails 30 x 30 from the roll bar top forward under the canopy edges, a cross rail at the front."""
    a = P.canopy_rail
    (x0, x1), (y0, y1), _ = P.canopy
    z = (P.canopy_z - a, P.canopy_z)
    zi = (z[0] + 2.0, z[1] - 2.0)
    rails = [box_span((s * P.rops_x - a / 2.0, s * P.rops_x + a / 2.0), (y0, y1), z).cut(
        box_span((s * P.rops_x - a / 2.0 + 2.0, s * P.rops_x + a / 2.0 - 2.0), (y0 - 1, y1 + 1), zi)) for s in (-1, 1)]
    front = box_span((-P.rops_x, P.rops_x), (y1 - a, y1), z).cut(
        box_span((-P.rops_x - 1, P.rops_x + 1), (y1 - a + 2.0, y1 - 2.0), zi))
    return fuse_all(rails + [front])


def canopy():
    (x0, x1), (y0, y1), t = P.canopy
    return box_span((x0, x1), (y0, y1), (P.canopy_z, P.canopy_z + t))


# ---------------------------------------------------------------------
# Operator (render only)
# ---------------------------------------------------------------------
def operator():
    y = P.seat_y
    z = PAN_Z[1]
    torso = box_span((-180.0, 180.0), (y - 140.0, y + 60.0), (z, z + 560.0))
    head = Part.makeSphere(110.0, V(0, y - 20.0, z + 680.0))
    thighs = [box_span((s * 80.0 - 70.0, s * 80.0 + 70.0), (y - 60.0, y + 380.0), (z, z + 140.0)) for s in (-1, 1)]
    shins = [box_span((s * 110.0 - 60.0, s * 110.0 + 60.0), (y + 330.0, y + 450.0), (TZ[1] + 3.0 + 100.0, z + 60.0))
             for s in (-1, 1)]
    feet = [box_span((s * 110.0 - 55.0, s * 110.0 + 55.0), (y + 330.0, y + 600.0), (TZ[1] + 3.0, TZ[1] + 3.0 + 100.0))
            for s in (-1, 1)]
    arms = [box_span((s * 230.0 - 50.0, s * 230.0 + 50.0), (y - 80.0, y + 220.0), (z + 300.0, z + 380.0)) for s in (-1, 1)]
    return Part.makeCompound([torso, head] + thighs + shins + feet + arms)
