"""Parts of the tray setter. Every function returns a Part shape in robot coordinates. The gantry parts that move are
drawn with the X beam at y 0 and the picker at x 0 (build_tst moves them: Y group in y, picker in x, Z group in z);
the shoes and press wheels at the middle of their rows.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tst_params as P


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


def fuse_all(shapes):
    shapes = list(shapes)
    r = shapes[0].fuse(shapes[1:]) if len(shapes) > 1 else shapes[0]
    try:
        return r.removeSplitter()
    except Exception:
        return r


def tube(x, y, z, wall):
    """Rectangular tube between the spans x, y, z; open along its longest side."""
    o = box_span(x, y, z)
    spans = [abs(x[1] - x[0]), abs(y[1] - y[0]), abs(z[1] - z[0])]
    k = spans.index(max(spans))
    lim = [sorted(x), sorted(y), sorted(z)]
    inner = []
    for i in range(3):
        a, b = lim[i]
        inner.append((a - 1, b + 1) if i == k else (a + wall, b - wall))
    return o.cut(box_span(*inner))


def hex_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    """Head on top of z_head, nut under z_nut."""
    return fuse_all([hex_z(af, z_head, z_head + k, x, y), cyl_z(d, z_nut - m - 4.0, z_head, x, y),
                     hex_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))])


def screw_up(x, y, z_head, z_top, d=8.0, af=13.0, k=5.3):
    """Bolt from below: head under z_head, shank up to z_top (into a rivet nut)."""
    return fuse_all([hex_z(af, z_head - k, z_head, x, y), cyl_z(d, z_head, z_top, x, y)])


# ---------------------------------------------------------------------
# Tray table
# ---------------------------------------------------------------------
CRADLE_BOLTS = [(x, y) for x in (P.robot_upper_beam_x[1], P.robot_upper_beam_x[2]) for y in P.cradle_y]
FUNNELS = [(x, P.funnel_y) for x in P.row_x]


def cradle():
    zc = P.cradle_z
    out = [tube((-P.cradle_half, P.cradle_half), (y - 20.0, y + 20.0), zc, 3.0) for y in P.cradle_y]
    s = Part.makeCompound(out)
    return s.cut([cyl_z(P.m10_hole, zc[0] - 1, zc[1] + 1, x, y) for (x, y) in CRADLE_BOLTS])


def cradle_bolts():
    return Part.makeCompound([bolt_z(x, y, P.table_z[1], P.robot_upper_beam_z[0], k=4.0) for (x, y) in CRADLE_BOLTS])


def table():
    (x0, x1), (y0, y1), _ = P.table
    t = box_span((x0, x1), (y0, y1), P.table_z)
    t = t.cut([cyl_z(P.funnel_d[1], P.table_z[0] - 1, P.table_z[1] + 1, x, y) for (x, y) in FUNNELS])
    t = t.cut([cyl_z(P.m10_hole, P.table_z[0] - 1, P.table_z[1] + 1, x, y) for (x, y) in CRADLE_BOLTS])
    w, ln, _ = P.tray
    stops = []
    for tx in P.tray_x:
        x0s, x1s = tx - w / 2.0 - 3.0, tx + w / 2.0 + 3.0
        y0s, y1s = P.tray_y - ln / 2.0 - 3.0, P.tray_y + ln / 2.0 + 3.0
        z = (P.table_z[1], P.table_z[1] + 20.0)
        stops += [box_span((x0s - P.tray_stops, x0s), (y0s, y1s), z), box_span((x1s, x1s + P.tray_stops), (y0s, y1s), z),
                  box_span((x0s - P.tray_stops, x1s + P.tray_stops), (y0s - P.tray_stops, y0s), z)]
    return fuse_all([t] + stops)


def _cell_wall(x, y, z0, h):
    """Tapered cell, 1 mm wall, closed bottom with a drain hole."""
    outer = Part.makeCone(8.0, P.plug[0] / 2.0 + 1.0, h, V(x, y, z0), V(0, 0, 1))
    inner = Part.makeCone(7.0, P.plug[0] / 2.0, h, V(x, y, z0 + 1.0), V(0, 0, 1))
    return outer.cut(inner)


def trays():
    w, ln, h = P.tray
    nx, ny = P.tray_cells
    out = []
    z0 = P.table_z[1]
    for i, tx in enumerate(P.tray_x):
        t = box_span((tx - w / 2.0, tx + w / 2.0), (P.tray_y - ln / 2.0, P.tray_y + ln / 2.0), (z0 + h - 2.0, z0 + h))
        cells = [cyl_z(P.plug[0] + 2.0, z0 + h - 3.0, z0 + h + 1.0, *P.cell_xy(i, a, b)) for a in range(nx) for b in range(ny)]
        t = t.cut(Part.makeCompound(cells))
        walls = Part.makeCompound([_cell_wall(*P.cell_xy(i, a, b), z0, h - 2.0) for a in range(nx) for b in range(ny)])
        out.append(fuse_all([t]))
        out.append(walls)
    return Part.makeCompound(out)


def seedling(x, y, z_plug_bottom, leaves=True):
    plug = Part.makeCone(7.0, P.plug[0] / 2.0, P.plug[1], V(x, y, z_plug_bottom), V(0, 0, 1))
    if not leaves:
        return plug
    top = z_plug_bottom + P.plug[1]
    lv = []
    for k in range(4):
        leaf = Part.makeSphere(1.0)
        m = App.Matrix()
        m.scale(14.0, 6.0, 2.0)
        leaf = leaf.transformGeometry(m)
        leaf.rotate(V(0, 0, 0), V(0, 1, 0), -50.0)
        leaf.translate(V(10.0, 0, 35.0))
        leaf.rotate(V(0, 0, 0), V(0, 0, 1), 45.0 + 90.0 * k)
        leaf.translate(V(x, y, top))
        lv.append(leaf)
    stem = cyl_z(4.0, top, top + 40.0, x, y)
    return Part.makeCompound([plug, stem] + lv)


def seedlings_in_trays(taken=0):
    """Seedlings in the cells; the first 'taken' cells of tray 0 (front row first) are empty."""
    nx, ny = P.tray_cells
    z = P.table_z[1] + P.tray[2] - P.plug[1]
    out = []
    k = 0
    for i in range(2):
        for b in range(ny - 1, -1, -1):
            for a in range(nx):
                if k >= taken:
                    out.append(seedling(*P.cell_xy(i, a, b), z))
                k += 1
    return Part.makeCompound(out)


def funnels():
    out = []
    for (x, y) in FUNNELS:
        z0 = P.table_z[1]
        cone = Part.makeCone(P.funnel_d[1] / 2.0, P.funnel_d[0] / 2.0, P.funnel_h, V(x, y, z0), V(0, 0, 1))
        inner = Part.makeCone(P.funnel_d[1] / 2.0 - 2.0, P.funnel_d[0] / 2.0 - 2.0, P.funnel_h + 0.1, V(x, y, z0 - 0.05),
                              V(0, 0, 1))
        out.append(cone.cut(inner))
    return Part.makeCompound(out)


def drop_tubes():
    out = []
    for (x, y) in FUNNELS:
        out.append(cyl_z(P.tube_d[0], P.shoe_top - 20.0, P.table_z[0], x, y).cut(
            cyl_z(P.tube_d[1], P.shoe_top - 30.0, P.table_z[0] + 10.0, x, y)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Gantry: fixed Y rails with end plates and the Y motor; moving: Y carriages + posts + X beam (Y group),
# picker carriage (X group), Z rod + needle head (Z group)
# ---------------------------------------------------------------------
RAIL_Z = (P.table_z[1], P.table_z[1] + P.y_rail[1])


def y_rails():
    out = []
    for sx in (-1, 1):
        x = sx * P.y_rail_x
        out.append(tube((x - P.y_rail[0] / 2.0, x + P.y_rail[0] / 2.0), P.y_rail_y, RAIL_Z, 3.0))
        for y in P.y_rail_y:
            out.append(box_span((x - 25.0, x + 25.0), (y - (6.0 if y > 0 else 0.0), y + (0.0 if y > 0 else 6.0)),
                                (RAIL_Z[0], RAIL_Z[1] + 30.0)))
    return Part.makeCompound(out)


def gantry_motors():
    """Y motor on the front end plate of the right rail (drives both sides by a shaft), X motor on the X beam end."""
    a, ln = P.motor
    x = P.y_rail_x
    y = P.y_rail_y[1]
    return box_span((x - a / 2.0, x + a / 2.0), (y, y + ln), (RAIL_Z[1] - 10.0, RAIL_Z[1] - 10.0 + a))


def y_carriages(py=0.0):
    cx, cy, ct = P.y_car
    out = []
    for sx in (-1, 1):
        x = sx * P.y_rail_x
        plate = box_span((x - cx / 2.0, x + cx / 2.0), (py - cy / 2.0, py + cy / 2.0), (RAIL_Z[1], RAIL_Z[1] + ct))
        post = tube((x - 20.0, x + 20.0), (py - 20.0, py + 20.0), (RAIL_Z[1] + ct, P.gantry_z), 3.0)
        out.append(fuse_all([plate, post]))
    return Part.makeCompound(out)


def x_beam(py=0.0):
    by, bz = P.x_beam
    b = tube(P.x_beam_x, (py - by / 2.0, py + by / 2.0), (P.gantry_z, P.gantry_z + bz), 3.0)
    a, ln = P.motor
    m = box_span((P.x_beam_x[1], P.x_beam_x[1] + ln), (py - a / 2.0, py + a / 2.0), (P.gantry_z, P.gantry_z + a))
    return fuse_all([b, m])


PX0 = 0.0                                   # picker drawn at x 0
PICK_Y = P.picker_dy                        # picker axis y at py = 0


def picker_carriage():
    """Carriage on the X beam, a bracket behind it with the Z actuator body standing up."""
    bx, by, bz = P.picker
    c = box_span((-bx / 2.0, bx / 2.0), (-P.x_beam[0] / 2.0 - 10.0, P.x_beam[0] / 2.0 + 10.0),
                 (P.gantry_z + P.x_beam[1], P.gantry_z + P.x_beam[1] + 20.0))
    bracket = box_span((-bx / 2.0, bx / 2.0), (PICK_Y + 25.0, -P.x_beam[0] / 2.0 - 10.0),
                       (P.gantry_z + P.x_beam[1] - 10.0, P.gantry_z + P.x_beam[1] + 20.0))
    act = cyl_z(P.z_act[0], P.gantry_z + P.x_beam[1] + 20.0, P.gantry_z + P.x_beam[1] + 20.0 + P.z_act[1], 0.0, PICK_Y)
    guide = cyl_z(30.0, P.gantry_z - 30.0, P.gantry_z + P.x_beam[1] - 10.0, 0.0, PICK_Y)
    return fuse_all([c, bracket, act, guide]).cut(cyl_z(13.0, P.gantry_z - 40.0, P.gantry_z + 300.0, 0.0, PICK_Y))


NEEDLE_TIP_PICK = P.table_z[1] + P.tray[2] - P.pick_depth          # needle tips in the plug at pick
NEEDLE_D = (-P.needle_dx, P.needle_dx)
HEAD_Z_PICK = NEEDLE_TIP_PICK + P.needles[1]                        # bottom of the needle head at pick


def z_group():
    """Rod O12 and the needle head with 4 needles and a stripper plate, drawn at the pick height."""
    hx, hy, hz = P.needle_head
    z0 = HEAD_Z_PICK
    rod = cyl_z(12.0, z0 + hz, P.gantry_z + P.x_beam[1] + 20.0 + 40.0, 0.0, PICK_Y)
    head = box_span((-hx / 2.0, hx / 2.0), (PICK_Y - hy / 2.0, PICK_Y + hy / 2.0), (z0 + 6.0, z0 + hz))
    stripper = box_span((-hx / 2.0, hx / 2.0), (PICK_Y - hy / 2.0, PICK_Y + hy / 2.0), (z0, z0 + 3.0)).cut(
        Part.makeCompound([cyl_z(3.0, z0 - 1, z0 + 4, dx, PICK_Y + dy) for dx in NEEDLE_D for dy in NEEDLE_D]))
    pins = [cyl_z(P.needles[0], z0 - P.needles[1], z0 + 6.0, dx, PICK_Y + dy) for dx in NEEDLE_D for dy in NEEDLE_D]
    return fuse_all([rod, head] + pins), stripper


# ---------------------------------------------------------------------
# Belly: rails, cross beams, shoe posts, shoes, press wheels
# ---------------------------------------------------------------------
RAIL_BOLTS = [(sx * P.rail_x, y) for sx in (-1, 1) for y in P.robot_lower_beam_y]
CROSS_BOLTS = [(sx * P.rail_x, y) for sx in (-1, 1) for y in P.cross_y]      # M8 into rivet nuts in the rails


def rails():
    zc = P.rail_z
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        t = tube((x - 20.0, x + 20.0), P.rail_y, zc, 3.0)
        t = t.cut([cyl_z(P.m10_hole, zc[0] - 1, zc[1] + 1, bx, by) for (bx, by) in RAIL_BOLTS if bx == x])
        t = t.cut([cyl_z(8.5, zc[0] - 1, zc[0] + 4, bx, by) for (bx, by) in CROSS_BOLTS if bx == x])
        out.append(t)
    return Part.makeCompound(out)


def rail_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], P.rail_z[0]) for (x, y) in RAIL_BOLTS])


def cross_beams():
    out = []
    for y in P.cross_y:
        t = tube((-P.rail_x - 25.0, P.rail_x + 25.0), (y - 20.0, y + 20.0), P.cross_z, 3.0)
        out.append(t.cut([cyl_z(8.5, P.cross_z[0] - 1, P.cross_z[1] + 1, x, y) for (x, yy) in CROSS_BOLTS if yy == y]))
    return Part.makeCompound(out)


def cross_bolts():
    return Part.makeCompound([screw_up(x, y, P.cross_z[0], P.rail_z[0] + 3.0 + 6.0) for (x, y) in CROSS_BOLTS])


def shoes():
    """Per row: post 40 x 40 from the front cross beam, runner blade 10 mm (sharp front, 60 mm into the soil), boot."""
    out = []
    y0, y1 = P.shoe_y
    by = P.boot[1]
    for x in P.row_x:
        post = tube((x - 20.0, x + 20.0), (P.cross_y[0] - 20.0, P.cross_y[0] + 20.0), (P.shoe_top, P.cross_z[0]), 3.0)
        pts = [(y1, P.shoe_top), (y0, P.shoe_top), (y0, -P.shoe_depth), (y1 - 40.0, -P.shoe_depth), (y1 + 30.0, 40.0),
               (y1, 140.0)]
        face = Part.Face(Part.makePolygon([V(x - P.shoe_t / 2.0, py, pz) for (py, pz) in pts + [pts[0]]]))
        blade = face.extrude(V(P.shoe_t, 0, 0))
        boot = tube((x - P.boot[0] / 2.0, x + P.boot[0] / 2.0), by, (-P.shoe_depth + 10.0, P.shoe_top), 3.0)
        cap = box_span((x - P.boot[0] / 2.0 - 5.0, x + P.boot[0] / 2.0 + 5.0), (by[0] - 5.0, y1),
                       (P.shoe_top, P.shoe_top + 8.0)).cut(cyl_z(P.tube_d[0] + 1.0, P.shoe_top - 1, P.shoe_top + 9,
                                                                 x, P.funnel_y))
        out.append(fuse_all([post, blade, boot, cap]))
    return Part.makeCompound(out)


def press_hangers():
    out = []
    for x in P.row_x:
        hang = tube((x - 20.0, x + 20.0), (P.press_y - 20.0, P.press_y + 20.0), (P.yoke_z[1], P.cross_z[0]), 3.0)
        yoke = box_span((x - P.press_dx - 45.0, x + P.press_dx + 45.0), (P.press_y - 30.0, P.press_y + 30.0), P.yoke_z)
        legs = []
        for s in (-1, 1):
            xl = x + s * (P.press_dx + 38.0)
            legs.append(box_span((xl - 4.0, xl + 4.0), (P.press_y - 25.0, P.press_y + 25.0),
                                 (P.press_d / 2.0 - 5.0, P.yoke_z[0])))
        out.append(fuse_all([hang, yoke] + legs))
    return Part.makeCompound(out)


def _wheel(x, s):
    r = P.press_d / 2.0
    w = cyl_x(P.press_d, -P.press_w / 2.0, P.press_w / 2.0, 0.0, 0.0)
    w = w.cut(cyl_x(60.0, -P.press_w, P.press_w, 0.0, 0.0)).fuse(cyl_x(70.0, -P.press_w / 2.0 - 5.0, P.press_w / 2.0 + 5.0,
                                                                         0.0, 0.0))
    axle = cyl_x(16.0, -P.press_w / 2.0 - 5.0, P.press_w / 2.0 + 34.0, 0.0, 0.0) if s > 0 else \
        cyl_x(16.0, -P.press_w / 2.0 - 34.0, P.press_w / 2.0 + 5.0, 0.0, 0.0)
    w = w.fuse(axle)
    w.rotate(V(0, 0, 0), V(0, 1, 0), s * P.press_tilt)       # tops apart
    w.translate(V(x, P.press_y, r * math.cos(math.radians(P.press_tilt)) - 5.0))
    return w


def press_wheels():
    return Part.makeCompound([_wheel(x + s * P.press_dx, s) for x in P.row_x for s in (-1, 1)])


# ---------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------
def bed(y0, y1, w=900.0):
    return box_span((-w / 2.0, w / 2.0), (y0, y1), (-60.0, 0.0))
