"""Parts of the insect vacuum. Every function returns a Part shape in robot coordinates (hood at the middle height
step of the drop-on-demand boom). Rails, posts, hood shell, brush skirt, post brackets and pins are ddb_parts'.
"""
import math

import Part
from FreeCAD import Vector as V

import isv_params as P
import ssp_parts as SG
import ddb_parts as DG

box_span = SG.box_span
cyl_x = SG.cyl_x
cyl_y = SG.cyl_y
cyl_z = SG.cyl_z
fuse_all = SG.fuse_all
hose = SG.hose
bolt_z = SG.bolt_z
HT = P.HT

NOZ = [(sx * abs(P.crop_rows[0]), P.noz_y) for sx in (-1, 1)]


# ---------------------------------------------------------------------
# Mount: belly rails (own bolts: no control-box plate here), posts of the boom
# ---------------------------------------------------------------------
rails = DG.rails
posts = DG.posts
post_bolts = DG.post_bolts


def rail_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], P.D.rail_z[0]) for (x, y) in DG.RAIL_BOLTS])


# ---------------------------------------------------------------------
# Hood (the boom's) with the holes for the 2 suction stubs and the knife inlet
# ---------------------------------------------------------------------
def hood_shell():
    s = DG.hood_shell()
    holes = [cyl_z(P.stub_d + 1.0, HT - 5, HT + 5, x, y) for (x, y) in NOZ]
    holes.append(cyl_z(P.exh_d + 1.0, HT - 5, HT + 5, P.exh_in[0], P.exh_in[1]))
    return s.cut(holes)


holder = DG.holder
brush = DG.brush
post_brackets = DG.post_brackets
bracket_bolts = DG.bracket_bolts
pins = DG.pins


# ---------------------------------------------------------------------
# Suction nozzles (slot -> round, lofted), stainless 1.5
# ---------------------------------------------------------------------
def _rect_wire(x, y, z, wx, wy):
    pts = [V(x - wx / 2, y - wy / 2, z), V(x + wx / 2, y - wy / 2, z), V(x + wx / 2, y + wy / 2, z),
           V(x - wx / 2, y + wy / 2, z), V(x - wx / 2, y - wy / 2, z)]
    return Part.makePolygon(pts)


def _circle_wire(x, y, z, d):
    return Part.Wire(Part.makeCircle(d / 2.0, V(x, y, z), V(0, 0, 1)))


def nozzle(x, y):
    t = P.noz_t
    z0, z1 = P.slot_z, P.slot_z + P.loft_h
    outer = Part.makeLoft([_rect_wire(x, y, z0, P.slot_w + 2 * t, P.slot_l + 2 * t), _circle_wire(x, y, z1, P.stub_d)],
                          True)
    inner = Part.makeLoft([_rect_wire(x, y, z0 - 0.01, P.slot_w, P.slot_l), _circle_wire(x, y, z1 + 0.01, P.stub_d - 2 * t)],
                          True)
    body = outer.cut(inner)
    stub = cyl_z(P.stub_d, z1, P.stub_top, x, y).cut(cyl_z(P.stub_d - 2 * t, z1 - 1, P.stub_top + 1, x, y))
    collar = cyl_z(P.stub_d + 30.0, TOP_OUT, TOP_OUT + 3.0, x, y).cut(cyl_z(P.stub_d - 2 * t, TOP_OUT - 1, TOP_OUT + 4, x, y))
    return fuse_all([body, stub, collar])


TOP_OUT = HT


def nozzles():
    return Part.makeCompound([nozzle(x, y) for (x, y) in NOZ])


# ---------------------------------------------------------------------
# Air knives, risers, cross pipe, inlet stub
# ---------------------------------------------------------------------
def _pipe_y(d, y0, y1, x, z, t=1.5):
    return cyl_y(d, y0, y1, x, z).cut(cyl_y(d - 2 * t, y0 - 1, y1 + 1, x, z))


def knives():
    out = []
    y0, y1 = -P.knife_slot[1] / 2.0, P.knife_slot[1] / 2.0
    for sx in (-1, 1):
        x = sx * P.knife_x
        p = cyl_y(P.knife_d, P.riser_y - P.knife_d / 2.0, y1 + 10.0, x, P.knife_z)
        p = p.cut(cyl_y(P.knife_d - 3.0, P.riser_y - P.knife_d / 2.0 + 3.0, y1 + 7.0, x, P.knife_z))
        # slot, facing inward and up at knife_angle
        a = math.radians(P.knife_angle)
        slit = box_span((0.0, P.knife_d), (y0, y1), (-P.knife_slot[0] / 2.0, P.knife_slot[0] / 2.0))
        slit.rotate(V(0, 0, 0), V(0, 1, 0), -math.degrees(a))
        if sx > 0:
            slit.rotate(V(0, 0, 0), V(0, 0, 1), 180.0)
        slit.translate(V(x, 0.0, P.knife_z))
        p = p.cut(slit)
        riser = cyl_z(P.knife_d, P.knife_z, P.cross_z, x, P.riser_y).cut(
            cyl_z(P.knife_d - 3.0, P.knife_z, P.cross_z + 1, x, P.riser_y))
        out.append(fuse_all([p, riser]))
    return Part.makeCompound(out)


def knife_feed():
    """Cross pipe O50 under the hood top from riser to riser, a short bend up into the inlet stub O80."""
    x0 = P.knife_x
    cross = cyl_x(P.cross_d, -x0, x0, P.riser_y, P.cross_z).cut(cyl_x(P.cross_d - 3.0, -x0 + 1, x0 - 1, P.riser_y, P.cross_z))
    ex, ey = P.exh_in
    zs = HT - P.D.hood_t - 25.0
    stub = cyl_z(P.exh_d, zs, P.stub_top, ex, ey).cut(cyl_z(P.exh_d - 3.0, zs - 1, P.stub_top + 1, ex, ey))
    link = hose([(ex, P.riser_y, P.cross_z), (ex, ey, zs + 1.0)], od=P.cross_d)
    return fuse_all([cross, stub, link])


TOP_IN_Z = P.TOP_IN


def curtain():
    """PVC strips 100 x 3 from a flat bar under the hood top, 10 mm apart, across the bed."""
    w, t = P.curtain_strip
    bar = box_span((-P.hood_x + 5.0, P.hood_x - 5.0), (P.curtain_y - 15.0, P.curtain_y + 15.0), (TOP_IN_Z - 6.0, TOP_IN_Z))
    strips = []
    n = int((2 * P.hood_x - 20.0) // (w + P.curtain_gap))
    x0 = -0.5 * (n * w + (n - 1) * P.curtain_gap)
    for i in range(n):
        xs = x0 + i * (w + P.curtain_gap)
        strips.append(box_span((xs, xs + w), (P.curtain_y - t / 2.0, P.curtain_y + t / 2.0), (P.curtain_z, TOP_IN_Z - 6.0)))
    return bar, Part.makeCompound(strips)


def curtain_bar():
    return curtain()[0]


def curtain_strips():
    return curtain()[1]


# ---------------------------------------------------------------------
# Catch box on the upper beams
# ---------------------------------------------------------------------
BAR_Y = [(sy * P.hole_y - P.bar / 2.0, sy * P.hole_y + P.bar / 2.0) for sy in (-1, 1)]
BOLTS = [(sx * bx, sy * P.hole_y) for sx in (-1, 1) for bx in P.bar_bolt_x for sy in (-1, 1)]


def _tube_x(x, y, z, wall):
    o = box_span(x, y, z)
    return o.cut(box_span((x[0] - 1, x[1] + 1), (y[0] + wall, y[1] - wall), (z[0] + wall, z[1] - wall)))


def _tube_y(x, y, z, wall):
    o = box_span(x, y, z)
    return o.cut(box_span((x[0] + wall, x[1] - wall), (y[0] - 1, y[1] + 1), (z[0] + wall, z[1] - wall)))


def bars():
    out = []
    for y in BAR_Y:
        t = _tube_x((-P.bar_x, P.bar_x), y, P.bar_z, P.bar_wall)
        t = t.cut([cyl_z(P.m10_hole, P.bar_z[0] - 1, P.bar_z[1] + 1, bx, by) for (bx, by) in BOLTS if y[0] < by < y[1]])
        out.append(t)
    return Part.makeCompound(out)


def bar_bolts():
    return Part.makeCompound([bolt_z(x, y, P.bar_z[1], P.upper_beam_z[0]) for (x, y) in BOLTS])


def box_rails():
    h = P.rail / 2.0
    return Part.makeCompound([_tube_y((sx * P.rail_x - h, sx * P.rail_x + h), P.rail_y, P.rail_z, 2.0) for sx in (-1, 1)])


def catch_box():
    t = P.box_t
    (y0, y1), (z0, z1) = P.box_y, P.box_z
    o = box_span((-P.box_x, P.box_x), (y0, y1), (z0, z1))
    i = box_span((-P.box_x + t, P.box_x - t), (y0 + t, y1 - t), (z0 + t, z1 + 1))
    s = o.cut(i)
    flange = box_span((-P.box_x - 10.0, P.box_x + 10.0), (y0 - 10.0, y1 + 10.0), (z1 - 3.0, z1)).cut(
        box_span((-P.box_x, P.box_x), (y0, y1), (z1 - 4.0, z1 + 1.0)))
    s = fuse_all([s, flange])
    s = s.cut([cyl_z(P.inlet_d - 3.0, z0 - 1, z0 + t + 1, sx * P.inlet_x, 0.0) for sx in (-1, 1)])
    stubs = [cyl_z(P.inlet_d, z0 - 40.0, z0, sx * P.inlet_x, 0.0).cut(cyl_z(P.inlet_d - 3.0, z0 - 41, z0 + 1, sx * P.inlet_x, 0.0))
             for sx in (-1, 1)]
    return fuse_all([s] + stubs)


def basket():
    """Stainless mesh basket (drawn as 1 mm sheet), open at the top, hung on the box rim by its own flange; 2 short
    sleeves over the inlet stubs keep the insects inside."""
    g = P.basket_gap
    t = 1.0
    (y0, y1), (z0, z1) = P.box_y, P.box_z
    o = box_span((-P.box_x + g, P.box_x - g), (y0 + g, y1 - g), (z0 + g, z1 - 3.0))
    i = box_span((-P.box_x + g + t, P.box_x - g - t), (y0 + g + t, y1 - g - t), (z0 + g + t, z1))
    s = o.cut(i)
    rim = box_span((-P.box_x + 2.0, P.box_x - 2.0), (y0 + 2.0, y1 - 2.0), (z1 - 3.0 - t, z1 - 3.0)).cut(
        box_span((-P.box_x + g + t, P.box_x - g - t), (y0 + g + t, y1 - g - t), (z1 - 5.0, z1)))
    s = s.cut([cyl_z(P.inlet_d - 3.0, z0 + g - 1, z0 + g + t + 1, sx * P.inlet_x, 0.0) for sx in (-1, 1)])
    sleeves = [cyl_z(P.inlet_d - 3.0, z0 + g + t, z0 + g + 60.0, sx * P.inlet_x, 0.0).cut(
        cyl_z(P.inlet_d - 5.0, z0 + g, z0 + g + 61.0, sx * P.inlet_x, 0.0)) for sx in (-1, 1)]
    return fuse_all([s, rim] + sleeves)


LID_Z = (P.box_z[1], P.box_z[1] + P.lid_t)


def lid():
    (y0, y1) = P.box_y
    s = box_span((-P.box_x - 10.0, P.box_x + 10.0), (y0 - 10.0, y1 + 10.0), LID_Z)
    return s.cut(cyl_z(P.fan_d * 0.45, LID_Z[0] - 1, LID_Z[1] + 1, P.fan_xy[0], P.fan_xy[1]))


FAN_Z = (LID_Z[1], LID_Z[1] + P.fan_h)


def fan():
    fx, fy = P.fan_xy
    vol = cyl_z(P.fan_d, FAN_Z[0], FAN_Z[1], fx, fy)
    dw, dh = P.duct
    duct = box_span((fx - dw / 2.0, fx + dw / 2.0), (P.exh_y - P.exh_od / 2.0, fy), (FAN_Z[0] + 10.0, FAN_Z[0] + 10.0 + dh))
    elbow = box_span((fx - dw / 2.0, fx + dw / 2.0), (P.exh_y - P.exh_od / 2.0, P.exh_y + P.exh_od / 2.0),
                     (FAN_Z[0] - 30.0, FAN_Z[0] + 10.0 + dh))
    return fuse_all([vol, duct, elbow])


def fan_motor():
    fx, fy = P.fan_xy
    d, h = P.fan_motor
    return fuse_all([cyl_z(d, FAN_Z[1], FAN_Z[1] + h, fx, fy),
                     box_span((fx + d / 2.0 - 5.0, fx + d / 2.0 + 25.0), (fy - 20.0, fy + 20.0), (FAN_Z[1] + 20.0, FAN_Z[1] + 60.0))])


# ---------------------------------------------------------------------
# Hoses
# ---------------------------------------------------------------------
def suction_hoses():
    z0 = P.box_z[0] - 40.0
    return Part.makeCompound([hose([(x, y, P.stub_top - 25.0), (x, y, z0 + 25.0)], od=P.hose_od) for (x, y) in NOZ])


def exhaust_hose():
    ex, ey = P.exh_in
    z_top = FAN_Z[0] - 30.0
    return hose([(ex, P.exh_y, z_top + 20.0), (ex, P.exh_y, 560.0), (ex, ey, P.stub_top + 40.0), (ex, ey, P.stub_top - 25.0)],
                od=P.exh_od)


# ---------------------------------------------------------------------
# Scene: bed with strawberry plants (images)
# ---------------------------------------------------------------------
def plants(y0, y1, spacing=300.0):
    out = []
    for x in P.crop_rows:
        y, k = y0 + 100.0, 0
        while y < y1 - 100.0:
            out.append(_plant(x, y, k))
            y += spacing
            k += 1
    return Part.makeCompound(out)


def _plant(x, y, seed):
    import random
    rnd = random.Random(seed * 7 + int(x))
    leaves = []
    for i in range(7):
        a = 2 * math.pi * i / 7 + rnd.uniform(-0.3, 0.3)
        r = rnd.uniform(50, 100)
        z = rnd.uniform(140, P.canopy_h - 15)
        leaves.append(Part.makeSphere(38.0, V(x + r * math.cos(a), y + r * math.sin(a), z)).common(
            box_span((x - 200, x + 200), (y - 200, y + 200), (z - 8, z + 8))))
        leaves.append(Part.makeCylinder(3.0, z, V(x + 0.4 * r * math.cos(a), y + 0.4 * r * math.sin(a), 0.0),
                                        V(0.6 * r * math.cos(a) / z, 0.6 * r * math.sin(a) / z, 1)))
    return Part.makeCompound(leaves)


def bed(y0, y1, w=800.0, h=150.0):
    return box_span((-w / 2.0, w / 2.0), (y0, y1), (-h, 0.0))
