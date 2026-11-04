"""Parts of the concentrate dispenser. Every function returns a Part shape in robot coordinates. The auger is its own
part (build_cdd puts it in a sub-Part "Auger" that the animation can turn about the x axis at (y 0, z auger_z)).
"""
import math

import Part
from FreeCAD import Vector as V

import cdd_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)
AZ = P.auger_z


def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def fuse_all(shapes):
    shapes = [s for s in shapes if s is not None]
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    try:
        return out.removeSplitter()
    except Exception:
        return out


def hex_prism_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    """Vertical bolt: head on top of z_head, nut under z_nut."""
    head = hex_prism_z(af, z_head, z_head + k, x, y)
    shank = cyl_z(d, z_nut - m - 4.0, z_head, x, y)
    nut = hex_prism_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))
    return fuse_all([head, shank, nut])


def tube_span(x, y, z, wall, axis):
    o = box_span(x, y, z)
    (x0, x1), (y0, y1), (z0, z1) = sorted(x), sorted(y), sorted(z)
    if axis == "x":
        i = box_span((x0 - 1, x1 + 1), (y0 + wall, y1 - wall), (z0 + wall, z1 - wall))
    elif axis == "y":
        i = box_span((x0 + wall, x1 - wall), (y0 - 1, y1 + 1), (z0 + wall, z1 - wall))
    else:
        i = box_span((x0 + wall, x1 - wall), (y0 + wall, y1 - wall), (z0 - 1, z1 + 1))
    return o.cut(i)


# ---------------------------------------------------------------------
# Cross tubes, bolts, load cells, legs, hopper frame
# ---------------------------------------------------------------------
BAR_Y = [(sy * P.hole_y - P.bar / 2.0, sy * P.hole_y + P.bar / 2.0) for sy in (-1, 1)]
BOLTS = [(sx * bx, sy * P.hole_y) for sx in (-1, 1) for bx in P.bar_bolt_x for sy in (-1, 1)]
LEGS = [(sx * P.leg_x, sy * P.hole_y) for sx in (-1, 1) for sy in (-1, 1)]
CELL_Z = (P.bar_z[1], P.bar_z[1] + P.cell[2])


def _cell_bolt_xy():
    out = []
    for (x, y) in LEGS:
        sx = math.copysign(1.0, x)
        out += [(x + sx * P.leg / 2.0 - sx * dx, y) for dx in (95.0, 115.0)]
    return out


def bars():
    out = []
    for y in BAR_Y:
        t = tube_span((-P.bar_x, P.bar_x), y, P.bar_z, P.bar_wall, "x")
        t = t.cut([cyl_z(P.m10_hole, P.bar_z[0] - 1, P.bar_z[1] + 1, bx, by) for (bx, by) in BOLTS
                   if y[0] < by < y[1]])
        t = t.cut([cyl_z(8.5, P.bar_z[1] - P.bar_wall - 1, P.bar_z[1] + 1, bx, by) for (bx, by) in _cell_bolt_xy()
                   if y[0] < by < y[1]])
        out.append(t)
    return Part.makeCompound(out)


def bar_bolts():
    return Part.makeCompound([bolt_z(x, y, P.bar_z[1], P.upper_beam_z[0]) for (x, y) in BOLTS])


def load_cells():
    """Shear-beam cells: fixed end bolted to the cross tube (inboard), the leg stands on the free end (outboard)."""
    cx, cy, cz = P.cell
    out = []
    for (x, y) in LEGS:
        sx = math.copysign(1.0, x)
        x0 = x + sx * P.leg / 2.0
        body = box_span((x0, x0 - sx * cx), (y - cy / 2.0, y + cy / 2.0), CELL_Z)
        out.append(body.cut([cyl_z(8.5, CELL_Z[0] - 1, CELL_Z[1] + 1, bx, by) for (bx, by) in _cell_bolt_xy()
                             if abs(by - y) < 1 and abs(bx - x) < P.cell[0]]))
    return Part.makeCompound(out)


def cell_bolts():
    """2 x M8 per cell at the fixed (inboard) end, into rivet nuts in the cross tube."""
    out = []
    for (x, y) in LEGS:
        sx = math.copysign(1.0, x)
        for dx in (95.0, 115.0):
            bx = x + sx * P.leg / 2.0 - sx * dx
            out.append(fuse_all([hex_prism_z(13.0, CELL_Z[1], CELL_Z[1] + 5.3, bx, y),
                                 cyl_z(8.0, P.bar_z[1] - P.bar_wall - 6.0, CELL_Z[1], bx, y)]))
    return Part.makeCompound(out)


def legs():
    h = P.leg / 2.0
    out = []
    for (x, y) in LEGS:
        out.append(tube_span((x - h, x + h), (y - h, y + h), (CELL_Z[1], P.frame_z[0]), P.leg_wall, "z"))
    return Part.makeCompound(out)


def frame():
    """Hopper frame 30 x 30 x 2: 2 tubes along y over the legs, 2 along x under the band of the hopper."""
    t = P.frame_t
    x0 = P.leg_x - t / 2.0
    ys = P.hole_y + t / 2.0
    parts = [tube_span((sx * x0, sx * (x0 + t)), (-ys, ys), P.frame_z, 2.0, "y") for sx in (-1, 1)]
    yb = P.hopper_y + P.wall_t
    parts += [tube_span((-x0, x0), (sy * yb, sy * (yb + t)), P.frame_z, 2.0, "x") for sy in (-1, 1)]
    return fuse_all(parts)


# ---------------------------------------------------------------------
# Hopper (stainless, open top + lid), U-trough at the bottom
# ---------------------------------------------------------------------
def _profile_pts(off=0.0, top=None):
    """Inner (off=0) or outer (off=wall) section in the yz plane: box part, 60 degree slopes, U-trough."""
    top = P.hopper_top + 1.0 if top is None else top
    hy, r = P.hopper_y + off, P.trough_r + off
    n = 16
    pts = [(-hy, top), (-hy, P.taper_top), (-r, AZ)]
    for k in range(1, n):
        ang = math.pi + math.pi * k / n
        pts.append((r * math.cos(ang), AZ + r * math.sin(ang)))
    pts += [(r, AZ), (hy, P.taper_top), (hy, top)]
    return pts


def _section(pts, x0, x1):
    poly = Part.makePolygon([V(x0, y, z) for (y, z) in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(poly).extrude(V(x1 - x0, 0, 0))


def hopper():
    t = P.wall_t
    outer = _section(_profile_pts(t, P.hopper_top), -P.hopper_x - t, P.hopper_x + t)
    inner = _section(_profile_pts(0.0), -P.hopper_x, P.hopper_x)
    s = outer.cut(inner)
    s = s.cut(cyl_x(P.tube_od + 0.5, P.hopper_x - 1, P.hopper_x + t + 1, 0.0, AZ))   # tube welded in
    s = s.cut(cyl_x(22.0, -P.hopper_x - t - 1, -P.hopper_x + 1, 0.0, AZ))            # drive shaft
    bt, bth = P.band
    yb = P.hopper_y + t
    band = box_span((-P.hopper_x - t - bt + 5.0, P.hopper_x + t + bt - 5.0), (-yb - bt, yb + bt),
                    (P.taper_top, P.taper_top + bth))
    band = band.cut(box_span((-P.hopper_x - t, P.hopper_x + t), (-yb, yb), (P.taper_top - 1, P.taper_top + bth + 1)))
    return fuse_all([s, band])


def lid():
    t = P.wall_t
    x, y = P.hopper_x + t + 10.0, P.hopper_y + t + 10.0
    top = box_span((-x, x), (-y, y), (P.hopper_top, P.hopper_top + P.lid_t))
    rim = box_span((-x, x), (-y, y), (P.hopper_top - 20.0, P.hopper_top)).cut(
        box_span((-x + 2, x - 2), (-y + 2, y - 2), (P.hopper_top - 21.0, P.hopper_top + 1)))
    handle = box_span((-60.0, 60.0), (y - 2.0, y + 18.0), (P.hopper_top - 5.0, P.hopper_top + P.lid_t))
    return fuse_all([top, rim, handle])


def level_sensor():
    """Capacitive low-level sensor M30 in the left taper wall (warns before the hopper runs empty)."""
    z = AZ + 90.0
    a = math.radians(P.slope_deg)
    y = -(P.trough_r + (z - AZ) / math.tan(a)) - P.wall_t
    s = Part.makeCylinder(15.0, 70.0, V(0.0, y, z), V(0, -math.cos(math.radians(90 - P.slope_deg)), 0.5))
    return s


# ---------------------------------------------------------------------
# Tube, outlet, spout, tie rod
# ---------------------------------------------------------------------
TUBE_IN = P.tube_od - 2 * P.tube_wall


def tube():
    x0 = P.hopper_x + P.wall_t
    t = cyl_x(P.tube_od, x0, P.tube_x[1], 0.0, AZ).cut(cyl_x(TUBE_IN, x0 - 1, P.tube_x[1] - P.end_cap_t, 0.0, AZ))
    t = t.cut(cyl_z(TUBE_IN, AZ - P.tube_od, AZ, P.outlet_x, 0.0))                 # outlet hole underneath
    stub = cyl_z(P.tube_od, AZ - P.tube_od / 2.0 - 40.0, AZ - TUBE_IN / 2.0 + 2.0, P.outlet_x, 0.0).cut(
        cyl_z(TUBE_IN, AZ - P.tube_od, AZ, P.outlet_x, 0.0))
    stub = stub.cut(cyl_x(TUBE_IN, x0, P.tube_x[1] - P.end_cap_t, 0.0, AZ))
    lug = box_span((P.tube_x[1] - 30.0, P.tube_x[1] - 10.0), (-4.0, 4.0), (AZ + P.tube_od / 2.0 - 2, AZ + P.tube_od / 2.0 + 18.0))
    lug = lug.cut(Part.makeCylinder(6.5, 10.0, V(P.tube_x[1] - 20.0, -5.0, AZ + P.tube_od / 2.0 + 9.0), Y))
    return fuse_all([t, stub, lug])


def spout():
    z0 = AZ - P.tube_od / 2.0 - 40.0
    s = cyl_z(P.spout_od + 2 * P.spout_t, P.spout_z, z0 + 30.0, P.outlet_x, 0.0)
    s = s.cut(cyl_z(P.spout_od, P.spout_z - 1, z0 + 31.0, P.outlet_x, 0.0))
    clamp = cyl_z(P.spout_od + 2 * P.spout_t + 6.0, z0 + 10.0, z0 + 22.0, P.outlet_x, 0.0).cut(
        cyl_z(P.spout_od + 2 * P.spout_t, z0 + 9.0, z0 + 23.0, P.outlet_x, 0.0))
    return Part.makeCompound([s.cut(cyl_z(P.tube_od, z0 - 1, z0 + 31.0, P.outlet_x, 0.0)), clamp])


def tie_rod():
    """Tie rod O12 from a lug under the right hopper-frame tube to the lug on the tube end (carries the tube)."""
    a = V(P.leg_x, 0.0, P.frame_z[0] - 10.0)
    b = V(P.tube_x[1] - 20.0, 0.0, AZ + P.tube_od / 2.0 + 9.0)
    d = b - a
    rod = Part.makeCylinder(P.tie_d / 2.0, d.Length - 30.0, a + d * (15.0 / d.Length), d)   # eyes not drawn
    lug = box_span((P.leg_x - 12.0, P.leg_x + 12.0), (-4.0, 4.0), (P.frame_z[0] - 20.0, P.frame_z[0]))
    return Part.makeCompound([rod, lug])


# ---------------------------------------------------------------------
# Drive: bearing flange, gearbox, motor (left end)
# ---------------------------------------------------------------------
def drive():
    x0 = -P.hopper_x - P.wall_t
    fx, fy, ft = P.flange
    fl = box_span((x0 - ft, x0), (-fy / 2.0, fy / 2.0), (AZ - fx / 2.0, AZ + fx / 2.0))
    fl = fl.cut(cyl_x(22.0, x0 - ft - 1, x0 + 1, 0.0, AZ))
    gb, gl = P.gearbox
    box = box_span((x0 - ft - gl, x0 - ft), (-gb / 2.0, gb / 2.0), (AZ - gb / 2.0, AZ + gb / 2.0))
    m = P.nema
    mot = box_span((x0 - ft - gl - P.nema_len, x0 - ft - gl), (-m / 2.0, m / 2.0), (AZ - m / 2.0, AZ + m / 2.0))
    plug = box_span((x0 - ft - gl - P.nema_len + 10.0, x0 - ft - gl - P.nema_len + 30.0), (-10.0, 10.0),
                    (AZ + m / 2.0, AZ + m / 2.0 + 12.0))
    return fl, fuse_all([box, mot, plug])


def flange():
    return drive()[0]


def motor():
    return drive()[1]


# ---------------------------------------------------------------------
# Auger (own sub-Part): flight O54 pitch 50 on a core O16, stub shaft O20 through the flange
# ---------------------------------------------------------------------
def auger():
    x0 = -P.hopper_x + 5.0
    x1 = P.auger_end_x
    r_in = P.core_d / 2.0 + 0.05
    r_out = P.flight_d / 2.0
    t = P.flight_t
    length = x1 - x0
    helix = Part.makeHelix(P.flight_pitch, length, r_out)
    prof = Part.makePolygon([V(r_in, 0, -t / 2), V(r_out, 0, -t / 2), V(r_out, 0, t / 2), V(r_in, 0, t / 2),
                             V(r_in, 0, -t / 2)])
    sweep = Part.Wire(helix).makePipeShell([prof], True, True)
    flight = sweep if sweep.ShapeType == "Solid" else Part.Solid(sweep)
    flight.rotate(V(0, 0, 0), Y, 90)
    flight.translate(V(x0, 0.0, AZ))
    core = cyl_x(P.core_d, x0, x1, 0.0, AZ)
    shaft = cyl_x(20.0, -P.hopper_x - P.wall_t - P.flange[2] - 10.0, x0 + 1.0, 0.0, AZ)
    return Part.makeCompound([flight, fuse_all([core, shaft])])


# ---------------------------------------------------------------------
# Feed and pellets for the images
# ---------------------------------------------------------------------
def windrow(y0, y1, x=P.windrow_x, w=500.0, h=250.0):
    """Pushed feed along the fence: a half-elliptic ridge along y."""
    e = Part.makeCylinder(1.0, y1 - y0, V(x, y0, 0.0), Y)
    m = App_matrix(w / 2.0, h)
    e = e.transformGeometry(m)
    return e.common(box_span((x - w, x + w), (y0, y1), (0.0, h + 1.0)))


def App_matrix(a, b):
    import FreeCAD as App
    m = App.Matrix()
    m.A11 = a
    m.A33 = b
    m.A14 = P.windrow_x * (1 - a)
    return m


def pellet_line(y0, y1, x=P.outlet_x, z=None, n=60, seed=1):
    import random
    rnd = random.Random(seed)
    z = 250.0 if z is None else z
    out = []
    for i in range(n):
        y = y0 + (y1 - y0) * (i + rnd.random()) / n
        out.append(Part.makeCylinder(4.0, 14.0, V(x + rnd.uniform(-35, 35), y, z - 6.0 + rnd.uniform(-4, 4)),
                                     V(rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0.3)))
    return Part.makeCompound(out)


def falling_pellets(n=14, seed=2):
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        z = 270.0 + (P.spout_z - 280.0) * rnd.random()
        out.append(Part.makeCylinder(4.0, 14.0, V(P.outlet_x + rnd.uniform(-20, 20), rnd.uniform(-20, 20), z),
                                     V(rnd.uniform(-1, 1), rnd.uniform(-1, 1), 1)))
    return Part.makeCompound(out)


def fence(y0, y1, x=1150.0):
    """Feed fence: neck rail and posts (images only)."""
    out = [box_span((x - 30.0, x + 30.0), (y0, y1), (0.0, 120.0))]          # feed table kerb / fence base
    out += [cyl_z(60.0, 0.0, 1300.0, x + 80.0, y) for y in range(int(y0), int(y1), 750)]
    out.append(Part.makeCylinder(30.0, y1 - y0, V(x + 80.0, y0, 1200.0), Y))
    out.append(Part.makeCylinder(30.0, y1 - y0, V(x + 80.0, y0, 700.0), Y))
    return Part.makeCompound(out)
