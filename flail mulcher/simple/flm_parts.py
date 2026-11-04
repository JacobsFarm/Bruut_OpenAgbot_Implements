"""Parts of the flail mulcher, in robot coordinates. The housing, rotor and roller are drawn in the work position;
build_flm puts the lifting parts in a sub-Part that moves up by P.lift for transport."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import flm_params as P
from ssp_parts import box_span, cyl_x, cyl_y, cyl_z, fuse_all, bolt_z

SIDES = (-1, 1)
HX = P.hood_x
Y0, Y1 = P.hood_y
TZ = P.top_z


def sq_tube_y(y0, y1, x, z, a, wall):
    o = box_span((x - a / 2.0, x + a / 2.0), (y0, y1), z)
    i = box_span((x - a / 2.0 + wall, x + a / 2.0 - wall), (y0 - 1, y1 + 1), (z[0] + wall, z[1] - wall))
    return o.cut(i)


def sq_tube_z(z0, z1, x, y, a, wall):
    o = box_span((x - a / 2.0, x + a / 2.0), (y - a / 2.0, y + a / 2.0), (z0, z1))
    i = box_span((x - a / 2.0 + wall, x + a / 2.0 - wall), (y - a / 2.0 + wall, y + a / 2.0 - wall), (z0 - 1, z1 + 1))
    return o.cut(i)


# ---------------------------------------------------------------------
# Belly rails (fixed)
# ---------------------------------------------------------------------
RAIL_BOLTS = [(s * P.rail_x, y) for s in SIDES for y in P.rail_bolt_y]


def rails():
    out = []
    for s in SIDES:
        x = s * P.rail_x
        t = sq_tube_y(P.rail_y[0], P.rail_y[1], x, P.rail_z, P.rail, P.rail_wall)
        caps = [box_span((x - P.rail / 2.0, x + P.rail / 2.0), (y, y + 3.0), P.rail_z) for y in (P.rail_y[0], P.rail_y[1] - 3.0)]
        t = fuse_all([t] + caps)
        out.append(t.cut([cyl_z(P.m10_hole, P.rail_z[0] - 1, P.rail_z[1] + 1, bx, by) for (bx, by) in RAIL_BOLTS if bx == x]))
    return Part.makeCompound(out)


def rail_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], P.rail_z[0]) for (x, y) in RAIL_BOLTS])


def side_brackets():
    """4 mm plates on the rail outer faces: sleeves for the guide posts, and a tall bracket with a top tab for the
    actuator clevis."""
    out = []
    for s in SIDES:
        xf = s * (P.rail_x + P.rail / 2.0)
        xp0, xp1 = sorted((xf, xf + s * 4.0))
        for y in P.guide_y:
            out.append(box_span((xp0, xp1), (y - 40.0, y + 40.0), P.sleeve_z))
            a, w, ln = P.sleeve
            out.append(sq_tube_z(P.sleeve_z[0], P.sleeve_z[1], s * P.guide_x, y, a, w))
        top = P.act_top + 12.0
        out.append(box_span((xp0, xp1), (P.act_y - 30.0, P.act_y + 30.0), (P.rail_z[0], top)))
        out.append(box_span(tuple(sorted((xf, s * (P.act_x + P.act_body[0] / 2.0)))), (P.act_y - 30.0, P.act_y + 30.0),
                            (P.act_top, top)))
    return Part.makeCompound(out)


def actuator_bodies():
    d, ln = P.act_body
    return Part.makeCompound([cyl_z(d, P.act_top - ln, P.act_top, s * P.act_x, P.act_y) for s in SIDES])


# ---------------------------------------------------------------------
# Lifting group (drawn in the work position)
# ---------------------------------------------------------------------
def actuator_rods():
    z0 = TZ + P.top_t + P.lug_h
    return Part.makeCompound([cyl_z(P.act_rod, z0 - 10.0, P.act_top - P.act_body[1] + 20.0, s * P.act_x, P.act_y)
                              for s in SIDES])


def guide_posts():
    a, w = P.post
    return Part.makeCompound([sq_tube_z(TZ + P.top_t, P.post_top_work, s * P.guide_x, y, a, w)
                              for s in SIDES for y in P.guide_y])


def top_lugs():
    """Lugs on the housing top for the actuator rods, and gusset feet for the guide posts."""
    out = []
    z0 = TZ + P.top_t
    for s in SIDES:
        out.append(box_span((s * P.act_x - 15.0, s * P.act_x + 15.0), (P.act_y - 4.0, P.act_y + 4.0), (z0, z0 + P.lug_h + 10.0)))
        for y in P.guide_y:
            out.append(box_span((s * P.guide_x - 30.0, s * P.guide_x + 30.0), (y - 30.0, y + 30.0), (z0, z0 + 6.0)))
    return Part.makeCompound(out)


def housing():
    """Top sheet 3 mm with a fold-down rim, side plates 6 mm, front wall, rear wall (above the roller)."""
    top = box_span((-HX, HX), (Y0, Y1), (TZ, TZ + P.top_t))
    sides = []
    for s in SIDES:
        x0, x1 = sorted((s * HX, s * (HX - P.side_t)))
        sp = box_span((x0, x1), (Y0, Y1), (P.skid_z + P.skid[2], TZ))
        sp = sp.cut(cyl_x(P.shaft_d + 2.0, x0 - 1, x1 + 1, P.rotor_y, P.rotor_z))
        sides.append(sp)
    front = box_span((-HX + P.side_t, HX - P.side_t), (Y1 - 3.0, Y1), (P.front_wall_z, TZ))
    rear = box_span((-HX + P.side_t, HX - P.side_t), (Y0, Y0 + 3.0), (P.rear_wall_z, TZ))
    return fuse_all([top, front, rear] + sides)


def skids():
    out = []
    for s in SIDES:
        x0, x1 = sorted((s * HX, s * (HX - P.skid[0])))
        out.append(box_span((x0, x1), (Y1 - P.skid[1], Y1), (P.skid_z, P.skid_z + P.skid[2])))
    return Part.makeCompound(out)


def front_flap():
    return box_span((-HX + P.side_t, HX - P.side_t), (Y1 - 9.0, Y1 - 3.0), (P.flap_z, P.front_wall_z + 30.0))


def shear_bar():
    """Angle 40 x 40 x 6 across, behind the rotor at the tip circle + 8 mm."""
    a, t = P.shear_bar
    r = P.rotor_d / 2.0 + 8.0
    yc = P.rotor_y - r * math.cos(math.radians(30.0))
    zc = P.rotor_z + r * math.sin(math.radians(30.0))
    x = (-HX + P.side_t, HX - P.side_t)
    leg1 = box_span(x, (yc - t, yc), (zc, zc + a))
    leg2 = box_span(x, (yc - a, yc), (zc + a - t, zc + a))
    return fuse_all([leg1, leg2])


def bearings():
    """Rotor and roller bearings on the outside of the side plates (left); the right rotor bearing sits in the belt
    guard."""
    out = []
    for s in SIDES:
        x0 = s * HX
        out.append(cyl_x(70.0, x0, x0 + s * 25.0, P.roller_y, P.roller_z))
        if s < 0:
            out.append(cyl_x(95.0, x0, x0 + s * 30.0, P.rotor_y, P.rotor_z))
    return Part.makeCompound(out)


def belt_guard():
    """Guard on the outside of the right side plate around the 2 pulleys (motor shaft and rotor shaft)."""
    x0, x1 = P.belt_case
    r = P.pulley[0] / 2.0 + 18.0
    body = box_span((x0, x1), (P.rotor_y - r, P.rotor_y + r), (P.rotor_z, P.motor_z))
    return fuse_all([body, cyl_x(2 * r, x0, x1, P.rotor_y, P.rotor_z), cyl_x(2 * r, x0, x1, P.motor_y, P.motor_z)])


def motor():
    body = cyl_x(P.motor_d, P.motor_x[0], P.motor_x[1], P.motor_y, P.motor_z)
    fins = [cyl_x(P.motor_d + 8.0, x, x + 6.0, P.motor_y, P.motor_z) for x in (P.motor_x[0] + 40.0, P.motor_x[0] + 90.0)]
    shaft = cyl_x(30.0, P.motor_x[1], P.belt_case[0], P.motor_y, P.motor_z)
    feet = [box_span((x - 20.0, x + 20.0), (P.motor_y - 50.0, P.motor_y + 50.0), (TZ + P.top_t, P.motor_z - P.motor_d / 2.0 + 10.0))
            for x in (P.motor_x[0] + 30.0, P.motor_x[1] - 30.0)]
    bearing = box_span((P.belt_case[0] - 80.0, P.belt_case[0]), (P.motor_y - 25.0, P.motor_y + 25.0),
                       (TZ + P.top_t, P.motor_z - 15.0))
    return fuse_all([body, shaft, bearing] + fins + feet)


def roller():
    ln = P.roller_len / 2.0
    t = cyl_x(P.roller_d, -ln, ln, P.roller_y, P.roller_z).cut(cyl_x(P.roller_d - 2 * P.roller_wall, -ln - 1, ln + 1, P.roller_y, P.roller_z))
    axle = cyl_x(25.0, -HX - 25.0, HX + 25.0, P.roller_y, P.roller_z)
    return fuse_all([t, axle])


# ---------------------------------------------------------------------
# Rotor (its own sub-Part, turns about x through (rotor_y, rotor_z))
# ---------------------------------------------------------------------
def rotor_tube():
    ln = P.rotor_len / 2.0
    d, w = P.rotor_tube
    t = cyl_x(d, -ln, ln, P.rotor_y, P.rotor_z).cut(cyl_x(d - 2 * w, -ln - 1, ln + 1, P.rotor_y, P.rotor_z))
    shaft = cyl_x(P.shaft_d, -HX - 30.0, P.belt_case[1] - 5.0, P.rotor_y, P.rotor_z)
    return fuse_all([t, shaft])


def _sets():
    """(x, angle) of every flail set: rows at 90 deg, staggered by pitch / 4."""
    ln = P.rotor_len / 2.0 - 30.0
    out = []
    for r in range(P.flail_rows):
        x = -ln + r * P.flail_pitch / 4.0
        while x <= ln:
            out.append((x, 90.0 * r))
            x += P.flail_pitch
    return out


def lugs():
    out = []
    lx, ly, lh = P.lug
    r0 = P.rotor_tube[0] / 2.0
    for x, a in _sets():
        b = box_span((x - lx / 2.0, x + lx / 2.0), (-ly / 2.0, ly / 2.0), (r0 - 2.0, r0 + lh))
        b.rotate(V(0, 0, 0), V(1, 0, 0), a)
        b.translate(V(0, P.rotor_y, P.rotor_z))
        out.append(b)
    return Part.makeCompound(out)


def flails():
    """Y-knives: 2 blades per shackle, from the lug out to the tip circle, the tips bent apart."""
    out = []
    w, t = P.knife
    r0 = P.rotor_tube[0] / 2.0 + P.lug[2] - 5.0
    r1 = P.rotor_d / 2.0
    for x, a in _sets():
        for dx in (-1.0, 1.0):
            xb = x + dx * (P.lug[0] / 2.0 + t / 2.0 + 1.0)
            blade = box_span((xb - t / 2.0, xb + t / 2.0), (-w / 2.0, w / 2.0), (r0, r1 - 30.0))
            tip = box_span(tuple(sorted((xb - dx * t / 2.0, xb + dx * 14.0))), (-w / 2.0, w / 2.0), (r1 - 30.0, r1))
            b = blade.fuse(tip)
            b.rotate(V(0, 0, 0), V(1, 0, 0), a)
            b.translate(V(0, P.rotor_y, P.rotor_z))
            out.append(b)
    return Part.makeCompound(out)


def pins():
    """Shackle pins O12 through each lug and its 2 knives."""
    out = []
    r = P.rotor_tube[0] / 2.0 + P.lug[2] - 8.0
    for x, a in _sets():
        p = cyl_x(12.0, x - P.lug[0] / 2.0 - 12.0, x + P.lug[0] / 2.0 + 12.0, 0.0, r)
        p.rotate(V(0, 0, 0), V(1, 0, 0), a)
        p.translate(V(0, P.rotor_y, P.rotor_z))
        out.append(p)
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Render only
# ---------------------------------------------------------------------
def grass(y0, y1, x=(-1200.0, 1200.0), cut=None):
    """Grass blades as thin cylinders, tall in front of the mulcher, cut short behind it (inside the strip)."""
    out = [box_span(x, (y0, y1), (-40.0, 0.0))]
    w = P.hood_x - P.side_t
    k = 0
    for yy in range(int(y0), int(y1), 70):
        for xx in range(int(x[0]) + 20, int(x[1]), 70):
            k += 1
            h = 180.0 + 60.0 * ((k * 37) % 5) / 4.0
            if cut is not None and yy < cut and abs(xx) < w:
                h = P.cut_h
            out.append(Part.makeCylinder(6.0, h, V(xx + 15.0 * ((k * 13) % 3 - 1), yy, 0)))
    return Part.makeCompound(out)
