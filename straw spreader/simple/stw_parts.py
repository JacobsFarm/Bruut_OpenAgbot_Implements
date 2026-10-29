"""Parts of the straw spreader. Every function returns a Part shape in robot coordinates."""
import math

import Part
from FreeCAD import Vector as V

import stw_params as P


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def cyl_x(d, yz, x0, x1):
    return cyl(d, (x0, yz[0], yz[1]), (x1, yz[0], yz[1]))


def tube_span(x, y, z, t, axis):
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


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def hull2_x(c1, r1, c2, r2, x0, x1):
    """Convex hull of 2 circles of the same radius in the y-z plane, extruded along x (chain loop)."""
    pts = [(c1[0], c1[1] + r1), (c2[0], c2[1] + r2), (c2[0], c2[1] - r2), (c1[0], c1[1] - r1)]
    return fuse_all([plate_yz(pts, x0, x1 - x0), cyl_x(2 * r1, c1, x0, x1), cyl_x(2 * r2, c2, x0, x1)])


def rect_wire(x, y, z):
    return Part.makePolygon([V(x[0], y[0], z), V(x[1], y[0], z), V(x[1], y[1], z), V(x[0], y[1], z), V(x[0], y[0], z)])


# ---------------------------------------------------------------------
# Mount
# ---------------------------------------------------------------------
BEARER_Z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + P.bearer)
RAIL_Z = (BEARER_Z[1], BEARER_Z[1] + P.bearer)


def bearers():
    out = []
    for y in P.bearer_y:
        b = tube_span((-P.bearer_x, P.bearer_x), (y - 20.0, y + 20.0), BEARER_Z, 3.0, "x")
        for sx in (-1, 1):
            for x in P.bearer_bolt_x + (P.rail_x,):
                b = b.cut(cyl(P.m10_hole, (sx * x, y, 600), (sx * x, y, 800)))
        out.append(b)
    return Part.makeCompound(out)


def rails():
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        r = tube_span((x - 20.0, x + 20.0), P.rail_y, RAIL_Z, 3.0, "y")
        for y in P.rail_bolt_y:
            r = r.cut(cyl(P.m10_hole, (x, y, 600), (x, y, 900)))
        out.append(r)
    return Part.makeCompound(out)


def bolts():
    out = [bolt_z(10.0, sx * x, y, P.robot_upper_beam_z[0], BEARER_Z[1])
           for sx in (-1, 1) for x in P.bearer_bolt_x for y in P.bearer_y]
    out += [bolt_z(10.0, sx * P.rail_x, y, BEARER_Z[0], RAIL_Z[1]) for sx in (-1, 1) for y in P.rail_bolt_y]
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Floor chain
# ---------------------------------------------------------------------
def floor_plate():
    return box_span((-P.slat_x, P.slat_x), P.floor_y, P.floor_z)


def shafts():
    out = []
    for y in P.sprocket_y:
        x1 = P.rail_x + P.pillow[1] / 2.0 + 10.0
        x2 = x1 + 32.0 if y == P.sprocket_y[0] else x1          # the front (drive) shaft goes into the gearmotor
        out.append(cyl_x(P.shaft_d, (y, P.shaft_z), -x1, x2))
    return Part.makeCompound(out)


def pillow_blocks():
    out = []
    py, px, pz = P.pillow
    for y in P.sprocket_y:
        for sx in (-1, 1):
            x = sx * P.rail_x
            b = box_span((x - px / 2.0, x + px / 2.0), (y - py / 2.0, y + py / 2.0), (RAIL_Z[1], RAIL_Z[1] + 14.0))
            h = cyl_x(66.0, (y, P.shaft_z), x - 20.0, x + 20.0)
            ped = box_span((x - 20.0, x + 20.0), (y - py / 2.0, y + py / 2.0), (RAIL_Z[1], P.shaft_z))
            out.append(fuse_all([b, h, ped]).cut(cyl_x(P.shaft_d, (y, P.shaft_z), x - 70, x + 70)))
    return Part.makeCompound(out)


def sprockets():
    out = []
    for y in P.sprocket_y:
        for sx in (-1, 1):
            x = sx * P.chain_x
            out.append(cyl_x(2 * P.sprocket_r, (y, P.shaft_z), x - 4.0, x + 4.0).cut(
                cyl_x(P.shaft_d, (y, P.shaft_z), x - 5, x + 5)))
    return Part.makeCompound(out)


def chains():
    out = []
    c1, c2 = (P.sprocket_y[0], P.shaft_z), (P.sprocket_y[1], P.shaft_z)
    r0, r1 = P.sprocket_r, P.sprocket_r + P.chain_t
    for sx in (-1, 1):
        x0 = sx * P.chain_x - P.chain_w / 2.0
        band = hull2_x(c1, r1, c2, r1, x0, x0 + P.chain_w).cut(hull2_x(c1, r0, c2, r0, x0 - 1, x0 + P.chain_w + 1))
        out.append(band)
    return Part.makeCompound(out)


def slats():
    """Slats on the top strand (the ones on the return strand are not drawn)."""
    z0 = P.shaft_z + P.sprocket_r + P.chain_t
    out = []
    y = P.sprocket_y[1] + 20.0
    while y < P.sprocket_y[0] - 20.0:
        out.append(fuse_all([box_span((-P.slat_x, P.slat_x), (y, y + P.slat[0]), (z0, z0 + 3.0)),
                             box_span((-P.slat_x, P.slat_x), (y, y + 3.0), (z0, z0 + P.slat[1]))]))
        y += P.slat_pitch
    return Part.makeCompound(out)


def floor_gearmotor():
    x0 = P.rail_x + P.pillow[1] / 2.0 + 12.0
    return cyl_x(P.floor_gm[0], (P.sprocket_y[0], P.shaft_z), x0, x0 + P.floor_gm[1]).cut(
        cyl_x(P.shaft_d, (P.sprocket_y[0], P.shaft_z), x0 - 1, x0 + 34))


# ---------------------------------------------------------------------
# Chamber
# ---------------------------------------------------------------------
def walls():
    out = []
    for sx in (-1, 1):
        x0 = P.wall_x if sx > 0 else -P.wall_x - P.wall_t
        out.append(box_span((x0, x0 + P.wall_t), P.wall_y, (P.wall_z0, P.wall_top)))
    out.append(box_span((-P.wall_x - P.wall_t, P.wall_x + P.wall_t), (P.front_wall_y, P.front_wall_y + P.wall_t),
                        (P.bale_z0 + 10.0, P.wall_top)))
    return fuse_all(out)


def posts():
    out = []
    for sx in (-1, 1):
        x0 = P.wall_x + P.wall_t if sx > 0 else -P.wall_x - P.wall_t - 6.0
        for y in P.post_y:
            out.append(box_span((x0, x0 + 6.0), (y - 20.0, y + 20.0), (RAIL_Z[1], P.wall_top)))
    return Part.makeCompound(out)


def bales():
    bx, bz, by = P.bale
    return Part.makeCompound([box_span((-bx / 2.0, bx / 2.0), (P.bale_y0, P.bale_y0 + by),
                                       (P.bale_z0 + i * bz, P.bale_z0 + (i + 1) * bz)) for i in range(P.n_bales)])


# ---------------------------------------------------------------------
# Drum and housing
# ---------------------------------------------------------------------
DRUM = (P.drum_y, P.drum_z)


def drum():
    t = cyl_x(P.drum_d, DRUM, -P.drum_x, P.drum_x).cut(cyl_x(P.drum_d - 2 * P.drum_wall, DRUM, -P.drum_x - 1, P.drum_x + 1))
    caps = [cyl_x(P.drum_d, DRUM, sx * P.drum_x - (6.0 if sx > 0 else 0.0), sx * P.drum_x + (0.0 if sx > 0 else 6.0))
            for sx in (-1, 1)]
    parts = [t] + caps
    n = int(2 * (P.drum_x - 20.0) // P.spike_pitch)
    for i in range(n + 1):
        x = -P.drum_x + 20.0 + i * P.spike_pitch
        a = math.radians(i * (360.0 / P.spike_rows) / 2.0 + (i % P.spike_rows) * 90.0)
        r0, r1 = P.drum_d / 2.0 - 2.0, P.drum_d / 2.0 + P.spike_l
        p0 = (x, P.drum_y + r0 * math.cos(a), P.drum_z + r0 * math.sin(a))
        p1 = (x, P.drum_y + r1 * math.cos(a), P.drum_z + r1 * math.sin(a))
        parts.append(cyl(P.spike_d, p0, p1))
    shaft = cyl_x(P.drum_shaft_d, DRUM, -P.house_x - P.house_t - 25.0, P.house_x + P.house_t + 40.0)
    return fuse_all(parts + [shaft])


def housing():
    out = []
    pts = ((P.house_y[1], RAIL_Z[1]), (P.house_y[1], P.house_top), (P.house_y[0], P.house_top), (P.house_y[0], RAIL_Z[1]))
    for sx in (-1, 1):
        x0 = P.house_x if sx > 0 else -P.house_x - P.house_t
        out.append(plate_yz(pts, x0, P.house_t))
    out.append(box_span((-P.house_x - P.house_t, P.house_x + P.house_t), (P.house_y[0], P.house_y[1]),
                        (P.house_top, P.house_top + 3.0)))
    out.append(box_span((-P.house_x, P.house_x), (P.house_y[0] - 3.0, P.house_y[0]), (P.chute_top_z, P.house_top + 3.0)))
    s = fuse_all(out)
    return s.cut(cyl_x(P.drum_shaft_d + 2.0, DRUM, -400, 400))


def drum_bearing():
    x1 = -P.house_x - P.house_t
    return cyl_x(80.0, DRUM, x1 - 20.0, x1).cut(cyl_x(P.drum_shaft_d, DRUM, x1 - 21, x1 + 1))


def drum_motor():
    x0 = P.house_x + P.house_t
    return cyl_x(P.drum_motor[0], DRUM, x0, x0 + P.drum_motor[1]).cut(cyl_x(P.drum_shaft_d, DRUM, x0 - 1, x0 + 41))


def chute():
    """Funnel 2 mm from the housing bottom to the outlet (open top and bottom)."""
    (tx, ty), (ox, oy) = P.chute_top, P.chute_out
    t = P.chute_t
    outer = Part.makeLoft([rect_wire(tx, ty, P.chute_top_z), rect_wire(ox, oy, P.chute_out_z)], True)
    inner = Part.makeLoft([rect_wire((tx[0] + t, tx[1] - t), (ty[0] + t, ty[1] - t), P.chute_top_z + 1.0),
                           rect_wire((ox[0] + t, ox[1] - t), (oy[0] + t, oy[1] - t), P.chute_out_z - 1.0)], True)
    return outer.cut(inner)


# ---------------------------------------------------------------------
# Crop (images) and row space (check)
# ---------------------------------------------------------------------
def crop(y=(-1250.0, 1000.0), step=125.0, h=300.0):
    out = []
    n = int((y[1] - y[0]) // step)
    for sx in (-1, 1):
        for i in range(n + 1):
            out.append(Part.makeCone(10.0, 70.0, h, V(sx * P.row_x, y[0] + i * step, 0)))
    return Part.makeCompound(out)


def row_bands():
    return Part.makeCompound([box_span((sx * P.row_x - P.row_band, sx * P.row_x + P.row_band), (-1300.0, 1000.0),
                                       (0.0, P.crop_h)) for sx in (-1, 1)])


def mulch_strip(length=900.0, h=40.0):
    """Straw already laid behind the outlet (images)."""
    (ox, oy) = P.chute_out
    w = P.strip_w * 1000.0 / 2.0
    return box_span((-w, w), (oy[0] - length, oy[1] - 30.0), (0.0, h))
