"""Parts of the cover crop undersower. Every function returns a Part shape in robot coordinates."""
import math

import Part
from FreeCAD import Vector as V

import ccu_params as P


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


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def plate_yz(pts, x0, t):
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(t, 0, 0))


def plate_xz(pts, y0, t):
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, t, 0))


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def hose_path(points, d=None, wall=None):
    """Hose along a polyline: tubes between the points, balls at the bends (hollow)."""
    d = P.hose_d if d is None else d
    wall = P.hose_wall if wall is None else wall
    outer = [cyl(d, points[i], points[i + 1]) for i in range(len(points) - 1)]
    outer += [Part.makeSphere(d / 2.0, V(*p)) for p in points[1:-1]]
    inner = [cyl(d - 2 * wall, points[i], points[i + 1]) for i in range(len(points) - 1)]
    inner += [Part.makeSphere(d / 2.0 - wall, V(*p)) for p in points[1:-1]]
    return fuse_all(outer).cut(fuse_all(inner))


# ---------------------------------------------------------------------
# Bearer and hopper
# ---------------------------------------------------------------------
BEARER_Z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + P.bearer)
BEARER_Y = (P.bearer_y - P.bearer / 2.0, P.bearer_y + P.bearer / 2.0)


def _bearer_holes(s):
    for sx in (-1, 1):
        for x in P.bearer_bolt_x:
            s = s.cut(cyl(P.m10_hole, (sx * x, P.bearer_y, 600), (sx * x, P.bearer_y, 800)))
    return s


def bearer():
    return _bearer_holes(tube_span((-P.bearer_x, P.bearer_x), BEARER_Y, BEARER_Z, P.bearer_wall, "x"))


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * x, P.bearer_y, P.robot_upper_beam_z[0], BEARER_Z[1])
                              for sx in (-1, 1) for x in P.bearer_bolt_x])


def _hop_section():
    """Outer section of the hopper in the y-z plane (V to the outlet slot)."""
    y0, y1 = P.hop_y
    z0, z1 = P.hop_z
    oy, w = P.hop_out_y, P.hop_out[1] / 2.0
    return [(y0, z1), (y1, z1), (y1, z0), (oy + w, P.hop_out_z), (oy - w, P.hop_out_z), (y0, z0)]


def hopper():
    sec = _hop_section()
    outer = plate_yz(sec, -P.hop_x, 2 * P.hop_x)
    f = Part.Face(Part.makePolygon([V(0, y, z) for y, z in sec] + [V(0, sec[0][0], sec[0][1])]))
    inner = f.makeOffset2D(-P.hop_t, join=2)
    inner.translate(V(-P.hop_x + P.hop_t, 0, 0))
    inner = inner.extrude(V(2 * (P.hop_x - P.hop_t), 0, 0))
    s = outer.cut(inner)
    s = s.cut(box_span((-P.hop_x + P.hop_t, P.hop_x - P.hop_t), (P.hop_y[0] + P.hop_t, P.hop_y[1] - P.hop_t),
                       (P.hop_z[1] - 10.0, P.hop_z[1] + 1.0)))
    s = s.cut(box_span((-P.hop_out[0], P.hop_out[0]), (P.hop_out_y - P.hop_out[1] / 2.0 + 2, P.hop_out_y + P.hop_out[1] / 2.0 - 2),
                       (P.hop_out_z - 1.0, P.hop_out_z + 20.0)))
    return s


def lid():
    return box_span((-P.hop_x - 4.0, P.hop_x + 4.0), (P.hop_y[0] - 4.0, P.hop_y[1] + 4.0),
                    (P.hop_z[1], P.hop_z[1] + P.lid_t))


def brackets():
    """Flat bars 40 x 6 on the hopper ends, from the straight part down onto the bearer top."""
    out = []
    for sx in (-1, 1):
        x0 = P.hop_x if sx > 0 else -P.hop_x - P.bracket[1]
        out.append(box_span((x0, x0 + P.bracket[1]), (BEARER_Y[0] + 15.0, BEARER_Y[0] + 15.0 + P.bracket[0]),
                            (BEARER_Z[1], P.hop_z[0] + 60.0)))
        foot = box_span((x0 - 30.0 if sx > 0 else x0 - 24.0, x0 + 30.0 if sx > 0 else x0 + 6.0 + 24.0),
                        (BEARER_Y[0], BEARER_Y[1]), (BEARER_Z[1], BEARER_Z[1] + 6.0))
        out.append(foot)
    return fuse_all(out)


# ---------------------------------------------------------------------
# Metering
# ---------------------------------------------------------------------
METER_YC = (P.meter_y[0] + P.meter_y[1]) / 2.0
METER_ZC = (P.meter_z[0] + P.meter_z[1]) / 2.0


def meter_housing():
    s = box_span((-P.meter_x, P.meter_x), P.meter_y, P.meter_z)
    for c in P.cell_x:
        s = s.cut(cyl(P.roller_d + 2.0, (c - P.roller_w / 2.0 - 1, METER_YC, METER_ZC),
                      (c + P.roller_w / 2.0 + 1, METER_YC, METER_ZC)))
        s = s.cut(box_span((c - 15, c + 15), (METER_YC - 15, METER_YC + 15), (P.meter_z[1] - 20, P.meter_z[1] + 1)))
        s = s.cut(cyl(P.hose_d - 2 * P.hose_wall, (c, METER_YC, P.meter_z[0] - 1), (c, METER_YC, METER_ZC)))
    s = s.cut(cyl(12.0, (-P.meter_x - 1, METER_YC, METER_ZC), (P.meter_x + 1, METER_YC, METER_ZC)))
    spouts = [cyl(P.hose_d, (c, METER_YC, P.spout_z), (c, METER_YC, P.meter_z[0])).cut(
        cyl(P.hose_d - 2 * P.hose_wall, (c, METER_YC, P.spout_z - 1), (c, METER_YC, P.meter_z[0] + 1))) for c in P.cell_x]
    return fuse_all([s] + spouts)


def rollers():
    out = [cyl(10.0, (-P.meter_x - 5.0, METER_YC, METER_ZC), (P.meter_x + 10.0, METER_YC, METER_ZC))]
    for c in P.cell_x:
        r = cyl(P.roller_d, (c - P.roller_w / 2.0, METER_YC, METER_ZC), (c + P.roller_w / 2.0, METER_YC, METER_ZC))
        r = r.cut(cyl(10.0, (c - 20, METER_YC, METER_ZC), (c + 20, METER_YC, METER_ZC)))
        for i in range(P.flutes):
            a = 2 * math.pi * i / P.flutes
            p = (METER_YC + 18.0 * math.cos(a), METER_ZC + 18.0 * math.sin(a))
            r = r.cut(cyl(9.0, (c - 20, p[0], p[1]), (c + 20, p[0], p[1])))
        out.append(r)
    return fuse_all(out)


def gearmotor():
    x0 = P.meter_x
    return cyl(P.gm[0], (x0, METER_YC, METER_ZC), (x0 + P.gm[1], METER_YC, METER_ZC)).cut(
        cyl(10.0, (x0 - 1, METER_YC, METER_ZC), (x0 + 11, METER_YC, METER_ZC)))


# ---------------------------------------------------------------------
# Hoses and deflectors
# ---------------------------------------------------------------------
DEFL_TOP = P.defl_z + 40.0


def hose_points(i):
    c, bx = P.cell_x[i], P.band_x[i]
    start = (c, METER_YC, P.spout_z)
    down = (c, METER_YC, P.spout_z - P.hose_d)             # short vertical piece out of the spout
    if abs(bx - c) < 1.0:
        return [start, down, (bx, P.defl_y, DEFL_TOP)]
    return [start, down, (c, P.defl_y, P.side_z), (bx, P.defl_y, P.side_z), (bx, P.defl_y, DEFL_TOP)]


def hoses():
    return Part.makeCompound([hose_path(hose_points(i)) for i in range(len(P.cell_x))])


def deflectors():
    """Fishtail: flat funnel 2 mm, 40 wide at the hose, band width at the bottom, 30 deep (y), open at the bottom."""
    out = []
    for i, bx in enumerate(P.band_x):
        w = P.band_w[0] if i == 0 else P.band_w[1]
        y0 = P.defl_y - 15.0
        pts = ((bx - 22.0, DEFL_TOP), (bx + 22.0, DEFL_TOP), (bx + w / 2.0, P.defl_z), (bx - w / 2.0, P.defl_z))
        outer = plate_xz(pts, y0, 30.0)
        ipts = ((bx - 20.0, DEFL_TOP - 2.0), (bx + 20.0, DEFL_TOP - 2.0), (bx + w / 2.0 - 2.0, P.defl_z - 1.0),
                (bx - w / 2.0 + 2.0, P.defl_z - 1.0))
        inner = plate_xz(ipts, y0 + 2.0, 26.0)
        d = outer.cut(inner).cut(cyl(P.hose_d - 2 * P.hose_wall, (bx, P.defl_y, DEFL_TOP - 5), (bx, P.defl_y, DEFL_TOP + 5)))
        out.append(d)
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Tine bar, hangers, tines
# ---------------------------------------------------------------------
def bar():
    return tube_span((-P.bar_x, P.bar_x), P.bar_y, P.bar_z, 3.0, "x")


def _hanger_bolt_xy():
    return [(sx * P.hanger_x + dx, y) for sx in (-1, 1) for dx in (-P.hanger_bolt_dx, P.hanger_bolt_dx)
            for y in P.robot_rear_beam_y]


def hangers():
    out = []
    z1 = P.robot_lower_beam_z[0]
    for sx in (-1, 1):
        xc = sx * P.hanger_x
        top = box_span((xc - P.hanger_top[0] / 2.0, xc + P.hanger_top[0] / 2.0), P.hanger_top_y, (z1 - P.hanger_top[1], z1))
        web = plate_yz(P.web_pts, xc - P.web_t / 2.0, P.web_t).cut(box_span((-2000, 2000), P.bar_y, P.bar_z))
        out.append(fuse_all([top, web]))
    s = Part.makeCompound(out)
    for x, y in _hanger_bolt_xy():
        s = s.cut(cyl(P.m10_hole, (x, y, 500), (x, y, 700)))
    return s


def hanger_bolts():
    return Part.makeCompound([bolt_z(10.0, x, y, P.robot_lower_beam_z[0] - P.hanger_top[1], P.robot_lower_beam_z[1])
                              for x, y in _hanger_bolt_xy()])


def tines():
    yc = (P.bar_y[0] + P.bar_y[1]) / 2.0
    out = []
    for x in P.tine_x:
        zc = P.bar_z[0] - P.coil[0] / 2.0
        coil = cyl(P.coil[0], (x - P.coil[1] / 2.0, yc, zc), (x + P.coil[1] / 2.0, yc, zc)).cut(
            cyl(P.coil[0] - 2 * P.tine_d, (x - P.coil[1], yc, zc), (x + P.coil[1], yc, zc)))
        leg = cyl(P.tine_d, (x, yc - 4.0, zc - P.coil[0] / 2.0 + 4.0), (x, P.tine_tip[0], P.tine_tip[1] + 4.0))
        clamp = box_span((x - 15, x + 15), (P.bar_y[0] - 5, P.bar_y[1] + 5), (P.bar_z[1], P.bar_z[1] + 5))
        out.append(fuse_all([coil, leg, clamp]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Crop (for the images and the row check only)
# ---------------------------------------------------------------------
def crop(y=(-1250.0, 1000.0), step=125.0, h=300.0):
    out = []
    n = int((y[1] - y[0]) // step)
    for sx in (-1, 1):
        for i in range(n + 1):
            yy = y[0] + i * step
            out.append(Part.makeCone(10.0, 70.0, h, V(sx * P.row_x, yy, 0)))
    return Part.makeCompound(out)


def row_bands():
    """The space the crop rows need: x row +- row_band, up to crop_h, over the length of the robot and behind it."""
    return Part.makeCompound([box_span((sx * P.row_x - P.row_band, sx * P.row_x + P.row_band), (-1300.0, 1000.0),
                                       (0.0, P.crop_h)) for sx in (-1, 1)])
