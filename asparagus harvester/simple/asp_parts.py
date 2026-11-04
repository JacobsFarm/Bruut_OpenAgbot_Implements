"""Parts of the asparagus harvester. Every function returns a Part shape in robot coordinates.
The carriage (x) and the tool slide (z) are drawn at x 0 and with the tube tip at tip_top (retracted); build_asp moves
them with sub-Part placements."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import asp_params as P
import flm_parts as FG
from ssp_parts import box_span, cyl_x, cyl_y, cyl_z, fuse_all, bolt_z

rails = FG.rails
rail_bolts = FG.rail_bolts


def rect_tube_x(x0, x1, y, z, w, wall):
    o = box_span((x0, x1), (y - w / 2.0, y + w / 2.0), z)
    i = box_span((x0 + 3.0, x1 - 3.0), (y - w / 2.0 + wall, y + w / 2.0 - wall), (z[0] + wall, z[1] - wall))
    return o.cut(i)


# ---------------------------------------------------------------------
# Gantry (fixed)
# ---------------------------------------------------------------------
def gantry():
    """40 x 40 x 3 across, bolted up against the underside of the belly rails (2 x M8 per end)."""
    return rect_tube_x(P.gantry_x[0], P.gantry_x[1], 0.0, P.gantry_z, 40.0, 3.0)


def lin_rail():
    w, h = P.lin_rail
    return box_span((-P.x_travel - 80.0, P.x_travel + 80.0), (P.gantry_y[0] - w, P.gantry_y[0]),
                    (0.5 * sum(P.gantry_z) - h / 2.0, 0.5 * sum(P.gantry_z) + h / 2.0))


def x_motor():
    a, ln = P.x_motor
    x0 = P.x_travel + 80.0 + 5.0
    return box_span((x0, x0 + ln), (P.gantry_y[0] - a, P.gantry_y[0]), (P.gantry_z[0] - a, P.gantry_z[0]))


def hood_plate():
    (x0, x1), (y0, y1), (z0, z1) = P.hood
    return box_span((-P.rail_x - 20.0, P.rail_x + 20.0), (y0, y1), (P.rail_z[0] - P.hood_plate_t, P.rail_z[0]))


def hood():
    (x0, x1), (y0, y1), (z0, z1) = P.hood
    o = box_span((x0, x1), (y0, y1), (z0, z1))
    i = box_span((x0 + 2, x1 - 2), (y0 + 2, y1 - 2), (z0 - 1, z1 - 2))
    return o.cut(i)


def camera():
    (x0, x1), (y0, y1), (z0, z1) = P.hood
    yc = 0.5 * (y0 + y1)
    cam = box_span((-35.0, 35.0), (yc - 35.0, yc + 35.0), (z1 - 2 - 70.0, z1 - 2))
    lens = cyl_z(30.0, z1 - 2 - 85.0, z1 - 2 - 70.0, 0.0, yc)
    led = [box_span((x0 + 10, x1 - 10), (y, y + 20.0), (z1 - 2 - 15.0, z1 - 2)) for y in (y0 + 10.0, y1 - 30.0)]
    laser = cyl_z(16.0, z1 - 2 - 50.0, z1 - 2, x1 - 30.0, yc)
    return fuse_all([cam, lens, laser] + led)


# ---------------------------------------------------------------------
# Carriage (moves in x) with the Z profile
# ---------------------------------------------------------------------
def carriage():
    cx, cy, cz = P.carriage
    y1 = P.gantry_y[0] - P.lin_rail[0]
    return box_span((-cx / 2.0, cx / 2.0), (y1 - cy, y1), (0.5 * sum(P.gantry_z) - cz / 2.0, 0.5 * sum(P.gantry_z) + cz / 2.0))


def z_profile():
    a, b = P.z_prof
    y0, y1 = P.z_prof_y
    o = box_span((-a / 2.0, a / 2.0), (y0, y1), P.z_prof_z)
    slots = [box_span((-a / 2.0 - 1, -a / 2.0 + 4), (y0 + 15 + k * 40.0, y0 + 25 + k * 40.0), P.z_prof_z) for k in range(2)]
    slots += [box_span((a / 2.0 - 4, a / 2.0 + 1), (y0 + 15 + k * 40.0, y0 + 25 + k * 40.0), P.z_prof_z) for k in range(2)]
    return o.cut(slots)


def z_motor():
    a, ln = P.z_motor
    y0, y1 = P.z_prof_y
    return box_span((-a / 2.0, a / 2.0), (0.5 * (y0 + y1) - a / 2.0, 0.5 * (y0 + y1) + a / 2.0), (P.z_prof_z[1], P.z_prof_z[1] + ln))


# ---------------------------------------------------------------------
# Tool slide (moves in z), drawn retracted: tip at tip_top
# ---------------------------------------------------------------------
TIP = P.tip_top


def slide():
    sx, sy, sz = P.slide
    y1 = P.z_prof_y[0]
    z0 = TIP + 260.0
    plate = box_span((-sx / 2.0, sx / 2.0), (y1 - sy, y1), (z0, z0 + sz))
    clamp = [box_span((-25.0, 25.0), (P.tube_y, y1 - sy), (z, z + 30.0)) for z in (z0 + 10.0, z0 + sz - 40.0)]
    return fuse_all([plate] + clamp)


def tube():
    """Knife tube O30 (a rotating blade at the tip cuts the spear) with 2 gripper fingers at the lower end."""
    t = cyl_z(P.tube_d, TIP, TIP + P.tube_len, 0.0, P.tube_y).cut(cyl_z(P.tube_d - 4.0, TIP - 1, TIP + P.tube_len + 1, 0.0, P.tube_y))
    ft, fl = P.gripper
    fingers = []
    for s in (-1, 1):
        x0, x1 = sorted((s * (P.tube_d / 2.0), s * (P.tube_d / 2.0 + ft)))
        fingers.append(box_span((x0, x1), (P.tube_y - 8.0, P.tube_y + 8.0), (TIP + 5.0, TIP + 5.0 + fl)))
    motor = cyl_z(40.0, TIP + P.tube_len, TIP + P.tube_len + 70.0, 0.0, P.tube_y)
    return fuse_all([t, motor] + fingers)


def spear_bin():
    bx, by, bz = P.bin_box
    y1 = P.tube_y - P.tube_d / 2.0 - 5.0
    z0 = TIP + P.bin_dz
    o = box_span((-bx / 2.0, bx / 2.0), (y1 - by, y1), (z0, z0 + bz))
    i = box_span((-bx / 2.0 + 2, bx / 2.0 - 2), (y1 - by + 2, y1 - 2), (z0 + 2, z0 + bz + 1))
    return o.cut(i)


# ---------------------------------------------------------------------
# Rear deck and crate
# ---------------------------------------------------------------------
BOLTS = [(x, y) for y in P.cross_y for x in P.robot_upper_beam_x]


def cross_tubes():
    w, h, wall = P.cross
    z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + h)
    out = [rect_tube_x(-P.cross_half, P.cross_half, y, z, w, wall) for y in P.cross_y]
    return Part.makeCompound(out).cut([cyl_z(P.m10_hole, z[0] - 1, z[1] + 1, x, y) for (x, y) in BOLTS])


def cross_bolts():
    z1 = P.robot_upper_beam_z[1] + P.cross[1]
    return Part.makeCompound([bolt_z(x, y, z1, P.robot_upper_beam_z[0], k=4.0) for (x, y) in BOLTS])


DECK_Z = P.robot_upper_beam_z[1] + P.cross[1] + 6.0      # over the bolt heads


def deck():
    (x0, x1), (y0, y1), t = P.deck
    return box_span((x0, x1), (y0, y1), (DECK_Z, DECK_Z + t))


def deck_spacers():
    (x0, x1), (y0, y1), t = P.deck
    return Part.makeCompound([box_span((x - 15.0, x + 15.0), (y - 20.0, y + 20.0), (DECK_Z - 6.0, DECK_Z))
                              for y in P.cross_y for x in (-200.0, 0.0, 200.0)])


def crate():
    (x0, x1), (y0, y1), h = P.crate
    z0 = DECK_Z + P.deck[2]
    o = box_span((x0, x1), (y0, y1), (z0, z0 + h))
    i = box_span((x0 + 4, x1 - 4), (y0 + 4, y1 - 4), (z0 + 4, z0 + h + 1))
    return o.cut(i)


# ---------------------------------------------------------------------
# Render only: ridge with spears
# ---------------------------------------------------------------------
def ridge(y0, y1):
    b, t, h = P.ridge_base / 2.0, P.ridge_top_w / 2.0, P.ridge_h
    pts = [V(-b, y0, 0), V(b, y0, 0), V(t, y0, h), V(-t, y0, h)]
    r = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, y1 - y0, 0))
    ground = box_span((-1200.0, 1200.0), (y0, y1), (-40.0, 0.0))
    return r, ground


def spears(y0, y1):
    out = []
    k = 0
    for y in range(int(y0) + 100, int(y1), 300):
        k += 1
        x = 60.0 * ((k * 7) % 5 - 2) / 2.0
        top = P.ridge_h - 30.0 + 40.0 * ((k * 3) % 2)
        out.append(fuse_all([cyl_z(18.0, top - 220.0, top - 10.0, x, y), Part.makeSphere(9.0, V(x, y, top - 10.0))]))
    return Part.makeCompound(out)
