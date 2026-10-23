import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import hyb_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basic functions (same style as the other implements)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl_y(d, y0, y1, x, z):
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out


def tube_x(x, y, z, wall):
    return box_span(x, y, z).cut(box_span((x[0] - 1, x[1] + 1), (y[0] + wall, y[1] - wall), (z[0] + wall, z[1] - wall)))


def tube_y(x, y, z, wall):
    return box_span(x, y, z).cut(box_span((x[0] + wall, x[1] - wall), (y[0] - 1, y[1] + 1), (z[0] + wall, z[1] - wall)))


def hex_head(x, y, z0, z1, af):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def shaft_z():
    return P.z_deck + P.plate_t + P.eng_pto_z


# ---------------------------------------------------------------------
# Base frame
# ---------------------------------------------------------------------
def long_tubes():
    return [tube_x((-P.long_tube_half, P.long_tube_half), (y - P.tube / 2, y + P.tube / 2),
                   (P.z_long_bot, P.z_long_top), P.tube_wall) for y in P.long_tube_y]


def short_tubes():
    return [tube_y((x - P.tube / 2, x + P.tube / 2), (-P.short_tube_half, P.short_tube_half),
                   (P.z_short_bot, P.z_short_top), P.tube_wall) for x in P.short_tube_x]


def mount_points():
    return [(sx * x, y) for x in P.upper_beam_x for sx in (-1, 1) for y in P.long_tube_y]


def mount_sleeves():
    return fuse([cyl_z(P.mount_sleeve_d, P.z_long_bot + P.tube_wall, P.z_long_top - P.tube_wall, x, y).cut(
        cyl_z(P.mount_bolt_d, P.z_long_bot, P.z_long_top, x, y)) for x, y in mount_points()])


def mount_bolts():
    out = []
    z_top = P.z_long_top
    for x, y in mount_points():
        out.append(cyl_z(P.mount_bolt_d, z_top - P.mount_bolt_len, z_top, x, y))
        out.append(hex_head(x, y, z_top, z_top + P.bolt_head_k, P.bolt_head_af))
        z_beam_bot = P.upper_beam_top - P.upper_beam_w
        out.append(hex_head(x, y, z_beam_bot - P.nut_m, z_beam_bot, P.bolt_head_af))
    return fuse(out)


def mount_holes_cut():
    """Not used on the robot beams (read-only); kept for reference of the bolt positions."""
    return [cyl_z(P.m10_hole, P.z_long_bot, P.z_long_top, x, y) for x, y in mount_points()]


# ---------------------------------------------------------------------
# Battery, controller
# ---------------------------------------------------------------------
def battery():
    z0 = P.z_deck + P.plate_t
    return box_span(P.batt_x, P.batt_y, (z0, z0 + P.batt_h))


def battery_plate():
    return box_span((P.batt_x[0] - 20, P.batt_x[1] + 20), (P.batt_y[0] - 10, P.batt_y[1] + 10),
                    (P.z_deck, P.z_deck + P.plate_t))


def battery_strap():
    z0 = P.z_deck + P.plate_t
    y_mid = (P.batt_y[0] + P.batt_y[1]) / 2.0
    ys = (y_mid - P.strap_w / 2, y_mid + P.strap_w / 2)
    top = box_span((P.batt_x[0] - P.strap_t, P.batt_x[1] + P.strap_t), ys, (z0 + P.batt_h, z0 + P.batt_h + P.strap_t))
    left = box_span((P.batt_x[0] - P.strap_t, P.batt_x[0]), ys, (z0, z0 + P.batt_h))
    right = box_span((P.batt_x[1], P.batt_x[1] + P.strap_t), ys, (z0, z0 + P.batt_h))
    return fuse([top, left, right])


def controller():
    z0 = P.z_deck + P.plate_t
    return box_span(P.ctl_x, P.ctl_y, (z0, z0 + P.ctl_h))


def controller_plate():
    return box_span((P.ctl_x[0] - 10, P.ctl_x[1] + 10), (P.ctl_y[0] - 10, P.ctl_y[1] + 10),
                    (P.z_deck, P.z_deck + P.plate_t))


# ---------------------------------------------------------------------
# Generator, coupling
# ---------------------------------------------------------------------
def generator():
    z = shaft_z()
    body = cyl_y(P.gen_d, P.gen_y[0], P.gen_y[1], 0, z)
    cap = cyl_y(P.gen_cap_d, P.gen_cap_y[0], P.gen_cap_y[1], 0, z)
    ymid = (P.gen_y[0] + P.gen_y[1]) / 2.0
    zt = z + P.gen_d / 2 - 5
    tb = box_span((-P.gen_box[0] / 2, P.gen_box[0] / 2), (ymid - P.gen_box[1] / 2, ymid + P.gen_box[1] / 2),
                  (zt, zt + P.gen_box[2]))
    return fuse([body, cap, tb])


def generator_flange():
    return cyl_y(P.gen_flange_d, P.gen_flange_y[0], P.gen_flange_y[1], 0, shaft_z())


def generator_saddle():
    return box_span((-P.gen_saddle_x / 2, P.gen_saddle_x / 2), (P.gen_y[0] + 20, P.gen_y[1] - 20),
                    (P.z_deck, shaft_z() - P.gen_d / 2))


def coupling():
    z = shaft_z()
    return cyl_y(P.coupling_d, P.coupling_y[0], P.coupling_y[1], 0, z)


# ---------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------
def engine_plate():
    return box_span(P.eng_plate_x, P.eng_plate_y, (P.z_deck, P.z_deck + P.plate_t))


def engine():
    z0 = P.z_deck + P.plate_t
    z = shaft_z()
    crank = box_span(P.crank_x, P.crank_y, (z0, z0 + P.crank_h))
    cyl = cyl_z(P.cyl_d, z0 + P.crank_h, z0 + P.crank_h + P.cyl_h, P.cyl_x, P.cyl_y)
    zh = z0 + P.crank_h + P.cyl_h
    head = box_span((P.cyl_x - P.head[0] / 2, P.cyl_x + P.head[0] / 2), (P.cyl_y - P.head[1] / 2, P.cyl_y + P.head[1] / 2),
                    (zh, zh + P.head[2]))
    fan = cyl_y(P.fan_d, P.fan_y[0], P.fan_y[1], 0, z)
    recoil = cyl_y(P.recoil_d, P.recoil_y[0], P.recoil_y[1], 0, z)
    return fuse([crank, cyl, head, fan, recoil])


def fuel_tank():
    z0 = P.z_deck + P.plate_t + P.crank_h
    return box_span(P.tank_x, P.tank_y, (z0, z0 + P.tank_h))


def muffler():
    return cyl_y(P.muffler_d, P.muffler_y[0], P.muffler_y[1], P.muffler_x, P.z_deck + P.plate_t + P.muffler_z)


def air_filter():
    z0 = P.z_deck + P.plate_t + P.crank_h
    return cyl_z(P.filter_d, z0, z0 + P.filter_h, P.filter_x, P.filter_y)
