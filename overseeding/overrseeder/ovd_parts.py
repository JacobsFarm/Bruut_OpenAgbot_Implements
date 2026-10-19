"""Parts of the drop seeder. Every function returns a Part shape in robot coordinates; uy = robot y of the drop line
(the seeder unit is drawn in unit coordinates x, v, z and moved by uy). The tow hitch, the coupling head and the
drawbar come from the Cambridge roll (cbr_parts).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ovd_params as P
import cbr_parts as C

box_span = C.box_span
cyl = C.cyl
fuse_all = C.fuse_all


def _at(shape, uy):
    s = shape.copy()
    s.translate(V(0, uy, 0))
    return s


def _xs(x0, x1):
    return (min(x0, x1), max(x0, x1))


# ---------------------------------------------------------------------
# Hopper
# ---------------------------------------------------------------------
def _wall_line(s):
    """Inner line of the front (s = 1) or rear (s = -1) wall: (v, z) at the throat and at the top."""
    return (s * P.throat_v, P.throat_z), (s * P.top_v, P.top_z)


def _wall_normal(s):
    (v0, z0), (v1, z1) = _wall_line(s)
    dv, dz = v1 - v0, z1 - z0
    n = math.hypot(dv, dz)
    return (s * abs(dz) / n, -abs(dv) / n)      # outward (away from the inside), pointing down


def walls(uy=P.unit_y):
    out = []
    for s in (1, -1):
        (v0, z0), (v1, z1) = _wall_line(s)
        nv, nz = _wall_normal(s)
        t = P.sheet
        pts = [V(-P.width / 2.0, v0, z0), V(-P.width / 2.0, v1, z1), V(-P.width / 2.0, v1 + nv * t, z1 + nz * t),
               V(-P.width / 2.0, v0 + nv * t, z0 + nz * t)]
        out.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(P.width, 0, 0)))
    return _at(Part.makeCompound(out), uy)


def outside_of_wall(s, x=(-700.0, 700.0)):
    """Prism of everything inside the hopper (behind the outer face of a wall), to trim brackets."""
    (v0, z0), (v1, z1) = _wall_line(s)
    nv, nz = _wall_normal(s)
    t = P.sheet
    a = (v0 + nv * t, z0 + nz * t)
    d = (v1 - v0, z1 - z0)
    pts = [(a[0] - 3 * d[0], a[1] - 3 * d[1]), (a[0] + 3 * d[0], a[1] + 3 * d[1])]
    pts += [(pts[1][0] - nv * 2000.0, pts[1][1] - nz * 2000.0), (pts[0][0] - nv * 2000.0, pts[0][1] - nz * 2000.0)]
    poly = [V(x[0], v, z) for (v, z) in pts]
    return Part.Face(Part.makePolygon(poly + [poly[0]])).extrude(V(x[1] - x[0], 0, 0))


def end_plates(uy=P.unit_y):
    out = []
    w = P.width / 2.0
    for s in (-1, 1):
        x = _xs(s * w, s * (w + P.end_plate_t))
        plate = box_span(x, P.end_plate_v, P.end_plate_z)
        plate = plate.cut(cyl(P.meter_shaft_d + 2.0, (x[0] - 1, 0, P.roller_z), (x[1] + 1, 0, P.roller_z)))
        for dz in (-20.0, 20.0):
            plate = plate.cut(cyl(6.6, (x[0] - 1, 0, P.roller_z + dz), (x[1] + 1, 0, P.roller_z + dz)))
        out.append(plate)
    return _at(Part.makeCompound(out), uy)


def lid(uy=P.unit_y):
    w = P.width / 2.0 + P.end_plate_t
    z = (P.top_z, P.top_z + P.lid_t)
    return _at(box_span((-w, w), P.lid_v, z), uy)


def hinge(uy=P.unit_y):
    w = P.width / 2.0 - 50.0
    return _at(cyl(P.hinge_d, (-w, P.lid_v[0] + P.hinge_d / 2.0, P.top_z + P.lid_t + P.hinge_d / 2.0),
                   (w, P.lid_v[0] + P.hinge_d / 2.0, P.top_z + P.lid_t + P.hinge_d / 2.0)), uy)


# ---------------------------------------------------------------------
# Metering: housing, brush, flaps, roller, bearings
# ---------------------------------------------------------------------
def housing(uy=P.unit_y):
    w = P.width / 2.0
    out = [box_span((-w, w), _xs(s * (P.housing_v - 2.0), s * P.housing_v), (P.housing_z[0], P.throat_z - 2.0))
           for s in (-1, 1)]
    return _at(Part.makeCompound(out), uy)


def brush(uy=P.unit_y):
    w = P.width / 2.0
    t, h = P.brush
    v1 = P.housing_v - 2.0
    return _at(box_span((-w, w), (v1 - t, v1), (P.roller_z + 5.0, P.roller_z + 5.0 + h)), uy)


def flaps(uy=P.unit_y):
    w = P.width / 2.0
    t, z0 = P.flap
    out = [box_span((-w, w), _xs(s * (P.housing_v - t), s * P.housing_v), (z0, P.housing_z[0]))
           for s in (-1, 1)]
    return _at(Part.makeCompound(out), uy)


_ROLLER = None


def _roller_local():
    global _ROLLER
    if _ROLLER is None:
        w = P.width / 2.0 - 1.0
        r = P.roller_d / 2.0
        body = cyl(P.roller_d, (-w, 0, 0), (w, 0, 0))
        fw, fd = P.flute
        groove = box_span((-w - 1, w + 1), (-fw / 2.0, fw / 2.0), (r - fd, r + 1.0))
        cuts = []
        for i in range(P.flutes):
            g = groove.copy()
            g.rotate(V(0, 0, 0), V(1, 0, 0), 360.0 * i / P.flutes)
            cuts.append(g)
        body = body.cut(Part.makeCompound(cuts))
        _ROLLER = body.cut(cyl(P.meter_shaft_d, (-w - 1, 0, 0), (w + 1, 0, 0)))
    return _ROLLER


def roller(uy=P.unit_y):
    s = _roller_local().copy()
    s.translate(V(0, uy, P.roller_z))
    return s


def meter_shaft(uy=P.unit_y):
    return cyl(P.meter_shaft_d, (-P.meter_shaft_x, uy, P.roller_z), (P.meter_shaft_x + 7.0, uy, P.roller_z))


def meter_bearings(uy=P.unit_y):
    lz, wv, t, bd, bl = P.meter_bearing
    out = []
    for s in (-1, 1):
        xo = s * (P.width / 2.0 + P.end_plate_t)
        x0 = xo if s > 0 else xo - t
        flange = C.stadium_x(lz, wv, t, x0, 0.0, P.roller_z)
        boss = cyl(bd, (xo + s * (t - 1.0), 0, P.roller_z), (xo + s * (t + bl), 0, P.roller_z))
        body = fuse_all([flange, boss]).cut(cyl(P.meter_shaft_d, (s * 400.0, 0, P.roller_z), (s * 700.0, 0,
                                                                                               P.roller_z)))
        out.append(body)
    return _at(Part.makeCompound(out), uy)


# ---------------------------------------------------------------------
# Drive: coupling, worm gearmotor, bracket
# ---------------------------------------------------------------------
def gm_coupling(uy=P.unit_y):
    d, x0, x1 = P.gm_coupling
    c = cyl(d, (x0, 0, P.roller_z), (x1, 0, P.roller_z)).cut(cyl(P.meter_shaft_d, (x0 - 1, 0, P.roller_z),
                                                                  (x1 + 1, 0, P.roller_z)))
    return _at(c, uy)


def gearmotor(uy=P.unit_y):
    x, v, z = P.gm_box
    gb = box_span(x, v, z)
    xc = sum(x) / 2.0
    motor = cyl(P.gm_motor[0], (xc, 0, P.gm_motor[1]), (xc, 0, z[0]))
    out_shaft = cyl(8.0, (P.gm_coupling[2] - 8.0, 0, P.roller_z), (x[0], 0, P.roller_z))
    return _at(Part.makeCompound([gb, motor, out_shaft]), uy)


def gm_bracket(uy=P.unit_y):
    x, v, z = P.gm_bracket
    web = box_span(x, v, z)
    foot = box_span((x[0], x[0] + 4.0), (v[0] - 40.0, v[1]), z)      # against the end plate
    foot = foot.cut(cyl(80.0, (x[0] - 1, 0, P.roller_z), (x[0] + 5, 0, P.roller_z)))
    tab = box_span((P.gm_box[0][0], P.gm_box[0][1]), (P.gm_box[1][1], v[0]), (z[0], z[0] + 4.0))
    return _at(fuse_all([web, foot, tab]).cut(box_span(*P.gm_box)), uy)


# ---------------------------------------------------------------------
# Camera mast, camera, control box
# ---------------------------------------------------------------------
def mast(uy=P.unit_y):
    w, t = P.mast
    return _at(C.tube_span(P.mast_x, P.mast_v, P.mast_z, t, "z"), uy)


def mast_clamps(uy=P.unit_y):
    out = []
    for z in P.mast_clamps:
        b = box_span((-20.0, 20.0), (80.0, P.mast_v[0]), z)
        out.append(b.cut(outside_of_wall(1)))
    return _at(Part.makeCompound(out), uy)


def camera(uy=P.unit_y):
    bx, bl, bh = P.cam_box
    x, v, z = P.cam_pos
    body = box_span((-bx / 2.0, bx / 2.0), (-bl / 2.0, bl / 2.0), (-bh / 2.0, bh / 2.0))
    lens = cyl(24.0, (0, 0, -bh / 2.0 - 8.0), (0, 0, -bh / 2.0 + 1.0))
    hood = box_span((-bx / 2.0 - 5.0, bx / 2.0 + 5.0), (-bl / 2.0 - 5.0, bl / 2.0 + 20.0), (bh / 2.0, bh / 2.0 + 3.0))
    s = Part.makeCompound([body, lens, hood])
    s.rotate(V(0, 0, 0), V(1, 0, 0), P.cam_pitch)       # lens tilts forward
    s.translate(V(x, v, z))
    plate = box_span((-20.0 - 22.0, 20.0 + 22.0), (P.mast_v[0], P.mast_v[1] + 12.0), (P.mast_z[1], P.mast_z[1] + 6.0))
    cheeks = [box_span(_xs(sx * (bx / 2.0 + 1.0), sx * (bx / 2.0 + 5.0)), (v - 20.0, v + 20.0),
                       (P.mast_z[1] + 6.0, z - 3.0)) for sx in (-1, 1)]
    return _at(Part.makeCompound([s, fuse_all([plate] + cheeks)]), uy)


def control_box(uy=P.unit_y):
    return _at(box_span(*P.box), uy)


def box_brackets(uy=P.unit_y):
    x, v, z = P.box
    out = []
    for xx in (x[0] + 20.0, x[1] - 40.0):
        b = box_span((xx, xx + 20.0), (90.0, v[0]), (z[1] - 30.0, z[1] - 10.0))
        out.append(b.cut(outside_of_wall(1)))
    return _at(Part.makeCompound(out), uy)


# ---------------------------------------------------------------------
# Stand-alone trailer: cross bars, wheels, forks, drawbar (from the roll)
# ---------------------------------------------------------------------
def cross_bars(uy=P.unit_y):
    w = P.width / 2.0
    t = P.bar[1]
    return _at(Part.makeCompound([C.tube_span((-w, w), P.front_bar_v, P.bar_z, t, "x"),
                                  C.tube_span((-w, w), P.rear_bar_v, P.bar_z, t, "x")]), uy)


def wheels(uy=P.unit_y):
    r = P.wheel_d / 2.0
    out = []
    for s in (-1, 1):
        xc = s * P.wheel_x
        tyre = cyl(P.wheel_d, (xc - P.wheel_w / 2.0, P.wheel_v, r), (xc + P.wheel_w / 2.0, P.wheel_v, r))
        hd, hl = P.wheel_hub
        hub = cyl(hd, (xc - hl / 2.0, P.wheel_v, r), (xc + hl / 2.0, P.wheel_v, r))
        w = fuse_all([tyre, hub]).cut(cyl(P.wheel_axle_d + 1.0, (xc - 50, P.wheel_v, r), (xc + 50, P.wheel_v, r)))
        out.append(w)
    return _at(Part.makeCompound(out), uy)


def wheel_axles(uy=P.unit_y):
    r = P.wheel_d / 2.0
    t = P.fork[0]
    hl = P.wheel_hub[1] / 2.0
    out = []
    for s in (-1, 1):
        xc = s * P.wheel_x
        out.append(cyl(P.wheel_axle_d, (xc - hl - t - 12.0, P.wheel_v, r), (xc + hl + t + 12.0, P.wheel_v, r)))
    return _at(Part.makeCompound(out), uy)


def forks(uy=P.unit_y):
    """Two flat bars per wheel from the rear cross bar down to the axle."""
    r = P.wheel_d / 2.0
    t, w = P.fork
    hl = P.wheel_hub[1] / 2.0
    out = []
    for s in (-1, 1):
        xc = s * P.wheel_x
        for side in (-1, 1):
            x = _xs(xc + side * (hl + 1.0), xc + side * (hl + 1.0 + t))
            bar = box_span(x, (P.wheel_v - w / 2.0, P.wheel_v + w / 2.0), (r - 25.0, P.bar_z[0]))
            out.append(bar.cut(cyl(P.wheel_axle_d + 0.5, (x[0] - 1, P.wheel_v, r), (x[1] + 1, P.wheel_v, r))))
    return _at(Part.makeCompound(out), uy)


def cross_y(uy=P.unit_y):
    """y of the rear face of the 'cross beam' for the drawbar functions of the roll (front bar here)."""
    return uy + P.front_bar_v[1] - 40.0
