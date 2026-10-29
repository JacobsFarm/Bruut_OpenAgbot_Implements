"""Parts of the lime spreader. Every function returns a Part shape in robot coordinates."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lsp_params as P


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def ring(d_out, d_in, p0, p1):
    return cyl(d_out, p0, p1).cut(cyl(d_in, p0, p1))


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


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    """Vertical bolt: head under z_head, shank up to the nut on top of z_nut."""
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


# ---------------------------------------------------------------------
# Mount: rails, spacers, bolts
# ---------------------------------------------------------------------
def _rail_holes(shape):
    for sx in (-1, 1):
        for y in P.rail_bolt_y:
            shape = shape.cut(cyl(P.m10_hole, (sx * P.rail_x, y, 600), (sx * P.rail_x, y, 800)))
    return shape


def rails():
    return _rail_holes(Part.makeCompound([tube_span((sx * P.rail_x - P.rail / 2.0, sx * P.rail_x + P.rail / 2.0),
                                                    P.rail_y, P.rail_z, P.rail_wall, "y") for sx in (-1, 1)]))


def spacers():
    out = []
    for sx in (-1, 1):
        for y in P.rail_bolt_y:
            out.append(box_span((sx * P.rail_x - 20.0, sx * P.rail_x + 20.0), (y - 20.0, y + 20.0),
                                (P.robot_upper_beam_z[1], P.rail_z[0])))
    return _rail_holes(Part.makeCompound(out))


def _in_hopper(y):
    return P.hop_y[0] < y < P.hop_y[1]


def rail_bolts():
    """M10 from under the upper beam up through beam, spacer, rail (and the hopper bar), nut on top."""
    out = []
    for sx in (-1, 1):
        for y in P.rail_bolt_y:
            top = P.rail_z[1] + (P.bar[1] if _in_hopper(y) else 0.0)
            out.append(bolt_z(10.0, sx * P.rail_x, y, P.robot_upper_beam_z[0], top))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Hopper
# ---------------------------------------------------------------------
def _section(n=12):
    """Outer section of the hopper in the x-z plane: list of (x, z), clockwise from the top right."""
    right = [(P.hop_top_x, P.hop_top_z), P.hop_mid, (P.trough_x, P.trough_top_z), (P.trough_x, P.auger_z)]
    arc = [(P.trough_r * math.cos(-math.pi * i / n), P.auger_z + P.trough_r * math.sin(-math.pi * i / n))
           for i in range(1, n)]
    left = [(-x, z) for x, z in right[::-1]]
    return right + arc + left


def _face_xz(pts, y0):
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w)


def _inner_prism():
    """Inside of the hopper, open at the top (the top 10 mm of the walls is a rolled rim)."""
    f = _face_xz(_section(), P.hop_y[0] + P.hop_t).makeOffset2D(-P.hop_t, join=2)
    s = f.extrude(V(0, P.hop_y[1] - P.hop_y[0] - 2 * P.hop_t, 0))
    top = box_span((-P.hop_top_x + 10.0, P.hop_top_x - 10.0), (P.hop_y[0] + P.hop_t, P.hop_y[1] - P.hop_t),
                   (P.hop_top_z - 10.0, P.hop_top_z + 1.0))
    return s.fuse(top).removeSplitter()


def hopper():
    """Steel shell 2 mm with flat bars on the rails, hole for the auger tube (rear) and the shaft (front)."""
    outer = _face_xz(_section(), P.hop_y[0]).extrude(V(0, P.hop_y[1] - P.hop_y[0], 0))
    s = outer.cut(_inner_prism())
    bars = [box_span((sx * P.hop_mid[0], sx * (P.hop_mid[0] + P.bar[0])) if sx > 0 else
                     (-(P.hop_mid[0] + P.bar[0]), -P.hop_mid[0]), P.hop_y, (P.rail_z[1], P.rail_z[1] + P.bar[1]))
            for sx in (-1, 1)]
    s = fuse_all([s] + bars)
    s = s.cut(cyl(P.tube_d, (0, P.hop_y[0] - 1, P.auger_z), (0, P.hop_y[0] + P.hop_t + 1, P.auger_z)))
    s = s.cut(cyl(P.auger_shaft_d + 2.0, (0, P.hop_y[1] - P.hop_t - 1, P.auger_z), (0, P.hop_y[1] + 1, P.auger_z)))
    for sx in (-1, 1):
        for y in P.rail_bolt_y:
            if _in_hopper(y):
                s = s.cut(cyl(P.m10_hole, (sx * P.rail_x, y, 600), (sx * P.rail_x, y, 900)))
    return s


def lid():
    return box_span((-P.hop_top_x - 2.0, P.hop_top_x + 2.0), (P.hop_y[0] - 2.0, P.hop_y[1] + 2.0),
                    (P.hop_top_z, P.hop_top_z + P.lid_t))


def lime_fill(level=P.fill_level):
    """Lime in the hopper up to 'level' (for the image and the volume); the auger and tube are not taken off."""
    return _inner_prism().common(box_span((-500, 500), P.hop_y, (0.0, level)))


# ---------------------------------------------------------------------
# Augers, tubes, chute
# ---------------------------------------------------------------------
def _flights(axis, a0, a1, c):
    """Flights drawn as discs O100 x 4 every pitch, along 'axis' ('x' or 'y') from a0 to a1; c = the other 2 coords."""
    out = []
    n = int(abs(a1 - a0) // P.auger_pitch)
    step = P.auger_pitch if a1 > a0 else -P.auger_pitch
    for i in range(n + 1):
        a = a0 + i * step
        if axis == "y":
            p0, p1 = (c[0], a, c[1]), (c[0], a + P.flight_t, c[1])
        else:
            p0, p1 = (a, c[0], c[1]), (a + P.flight_t, c[0], c[1])
        out.append(ring(P.auger_d, P.auger_shaft_d, p0, p1))
    return out


def long_auger():
    y0, y1 = P.long_y
    shaft = cyl(P.auger_shaft_d, (0, P.long_tube_y[1] + 6.0, P.auger_z), (0, P.hop_y[1] + P.gm_box / 2.0, P.auger_z))
    return Part.makeCompound([shaft] + _flights("y", y0 - 20.0, y1, (0.0, P.auger_z)))


def long_tube():
    y0, y1 = P.long_tube_y
    t = ring(P.tube_d, P.tube_d - 2 * P.tube_wall, (0, y1, P.auger_z), (0, y0, P.auger_z))
    cap = cyl(P.tube_d, (0, y1 - 6.0, P.auger_z), (0, y1, P.auger_z)).cut(
        cyl(P.auger_shaft_d + 2.0, (0, y1 - 7, P.auger_z), (0, y1 + 1, P.auger_z)))
    t = fuse_all([t, cap])
    return t.cut(box_span((-P.chute / 2.0 + 2, P.chute / 2.0 - 2), (P.cross_y - P.chute / 2.0 + 2, P.cross_y + P.chute / 2.0 - 2),
                          (P.auger_z - 80.0, P.auger_z)))


def chute():
    c = P.chute
    z = (P.cross_z + 30.0, P.auger_z - 30.0)
    s = tube_span((-c / 2.0, c / 2.0), (P.cross_y - c / 2.0, P.cross_y + c / 2.0), z, 2.0, "z")
    return s.cut(cyl(P.tube_d, (-100, P.cross_y, P.cross_z), (100, P.cross_y, P.cross_z))).cut(
        cyl(P.tube_d, (0, P.long_tube_y[1] - 10, P.auger_z), (0, P.long_tube_y[0], P.auger_z)))


def _hole_x():
    n = int(2 * (P.cross_x - 50.0) // P.hole_pitch)
    return [-(P.cross_x - 50.0) + i * P.hole_pitch for i in range(n + 1)]


def cross_tube():
    t = ring(P.tube_d, P.tube_d - 2 * P.tube_wall, (-P.cross_x, P.cross_y, P.cross_z), (P.cross_x, P.cross_y, P.cross_z))
    t = t.cut(box_span((-P.chute / 2.0 + 2, P.chute / 2.0 - 2), (P.cross_y - P.chute / 2.0 + 2, P.cross_y + P.chute / 2.0 - 2),
                       (P.cross_z, P.cross_z + 80.0)))
    for x in _hole_x():
        t = t.cut(cyl(P.hole_d, (x, P.cross_y, P.cross_z - 80.0), (x, P.cross_y, P.cross_z)))
    return t


def end_plates():
    """End plates 6 mm on the cross tube ends: close the tube, carry the shaft bearing and the skirt."""
    out = []
    for sx in (-1, 1):
        x0 = P.cross_x if sx > 0 else -P.cross_x - 6.0
        p = box_span((x0, x0 + 6.0), P.skirt_y, (P.cross_z - 70.0, P.cross_z + 80.0))
        out.append(p.cut(cyl(P.auger_shaft_d + 2.0, (x0 - 1, P.cross_y, P.cross_z), (x0 + 7, P.cross_y, P.cross_z))))
    return Part.makeCompound(out)


def cross_auger():
    """Flights from the middle to both ends (left-hand on the left half, right-hand on the right half)."""
    shaft = cyl(P.auger_shaft_d, (-P.cross_x - 6.0, P.cross_y, P.cross_z),
                (P.cross_x + 6.0 + P.gm_box / 2.0, P.cross_y, P.cross_z))
    c = (P.cross_y, P.cross_z)
    fl = _flights("x", 60.0, P.cross_x - 30.0, c) + _flights("x", -60.0 - P.flight_t, -P.cross_x + 30.0, c)
    return Part.makeCompound([shaft] + fl)


def skirt():
    """Rubber 4 mm: front and rear walls between the end plates, 20 mm above the ground."""
    z = (P.skirt_gap, P.cross_z + 80.0)
    x = (-P.cross_x, P.cross_x)
    return Part.makeCompound([box_span(x, (P.skirt_y[0], P.skirt_y[0] + P.skirt_t), z),
                              box_span(x, (P.skirt_y[1] - P.skirt_t, P.skirt_y[1]), z)])


def legs():
    """2 legs 40 x 40 x 3 from the rail ends down to a saddle on the cross tube."""
    out = []
    top_saddle = P.cross_z + P.tube_d / 2.0 + 8.0
    for sx in (-1, 1):
        x = sx * P.rail_x
        lg = tube_span((x - P.leg / 2.0, x + P.leg / 2.0), P.leg_y, (top_saddle - 4.0, P.rail_z[0]), 3.0, "z")
        sad = ring(P.tube_d + 16.0, P.tube_d, (x - P.leg / 2.0, P.cross_y, P.cross_z), (x + P.leg / 2.0, P.cross_y, P.cross_z))
        sad = sad.common(box_span((x - 30, x + 30), (P.cross_y - 80, P.cross_y + 80), (P.cross_z, P.cross_z + 100)))
        out.append(fuse_all([lg, sad]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Gearmotors (24 V worm): gearbox on the shaft, motor at right angles
# ---------------------------------------------------------------------
def gearmotor_long():
    b = P.gm_box
    y0 = P.hop_y[1] + 2.0
    box = box_span((-b / 2.0, b / 2.0), (y0, y0 + b), (P.auger_z - b / 2.0, P.auger_z + b / 2.0))
    mot = cyl(P.gm_motor[0], (0, y0 + b / 2.0, P.auger_z + b / 2.0), (0, y0 + b / 2.0, P.auger_z + b / 2.0 + P.gm_motor[1]))
    return fuse_all([box, mot]).cut(cyl(P.auger_shaft_d, (0, y0 - 1, P.auger_z), (0, y0 + b / 2.0 + 1, P.auger_z)))


def gearmotor_cross():
    b = P.gm_box
    x0 = P.cross_x + 6.0
    box = box_span((x0, x0 + b), (P.cross_y - b / 2.0, P.cross_y + b / 2.0), (P.cross_z - b / 2.0, P.cross_z + b / 2.0))
    mot = cyl(P.gm_motor[0], (x0 + b / 2.0, P.cross_y + b / 2.0, P.cross_z),
              (x0 + b / 2.0, P.cross_y + b / 2.0 + P.gm_motor[1], P.cross_z))
    return fuse_all([box, mot]).cut(cyl(P.auger_shaft_d, (x0 - 1, P.cross_y, P.cross_z),
                                        (x0 + b / 2.0 + 1, P.cross_y, P.cross_z)))
