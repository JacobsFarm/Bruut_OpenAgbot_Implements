"""Parts of the weed picker (mowing deck). One function per part, returns a Part shape in robot coordinates at the default
cut height P.cut_h. The deck parts move as a whole (translation, set by the linkage); the links rotate about their
robot-side pivots; the actuator is redrawn for every height (actuator_shapes)."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import wpk_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

AF = {8: 13.0, 10: 17.0, 16: 24.0}
NUT_M = {8: 6.8, 10: 8.4, 16: 13.0}
HEAD_K = {8: 5.3, 10: 6.4, 16: 10.0}

C0 = P.cut_h                                    # right blades, default cut height
DT = P.DT0                                      # deck top
DB = DT - P.deck_t                              # deck bottom
YC = P.YC0                                      # rotor axes
YP = P.Y_PIVOT0                                 # deck pivots (y)
ZP = (DT + P.deck_pivot_dz, DT + P.deck_pivot_dz + (P.pivot_z[1] - P.pivot_z[0]))     # deck pivots (z)
SKIRT_Z0 = C0 - P.skirt_below
HOLE_PIN = P.pin_d + 1.0
FLOAT_HALF = P.lug_t / 2.0 + 1.0 + P.float_bar[1]        # joint of the float link: 10 mm eye or lug + 2 bars


# ---------------------------------------------------------------------
# Basic functions (same style as apm_parts.py)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_y(d, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def tube_z(od, idia, z0, z1, x, y):
    return cyl_z(od, z0, z1, x, y).cut(cyl_z(idia, z0 - 1, z1 + 1, x, y))


def fuse_all(shapes):
    shapes = list(shapes)
    result = shapes[0]
    if len(shapes) > 1:
        result = result.fuse(shapes[1:])
    try:
        result = result.removeSplitter()
    except Exception:
        pass
    return result


def poly_yz(points, x0, t):
    """Closed polygon in the y-z plane, (y, z) world, extruded along +x from x0."""
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0))


def _hex(af, p0, axis, length):
    r = af / math.sqrt(3.0)
    if axis == "x":
        pts = [V(p0[0], p0[1] + r * math.cos(math.radians(60 * i)), p0[2] + r * math.sin(math.radians(60 * i)))
               for i in range(6)]
        d = V(length, 0, 0)
    else:
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1] + r * math.sin(math.radians(60 * i)), p0[2])
               for i in range(6)]
        d = V(0, 0, length)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(d)


def hex_z(af, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return _hex(af, (x, y, z0), "z", z1 - z0)


def hex_x(af, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return _hex(af, (x0, y, z), "x", x1 - x0)


def bar_plan(p0, p1, w, z0, z1):
    """Plate standing on edge from (x, y) p0 to p1 (plan), thickness w, between z0 and z1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    b = Part.makeBox(length, w, z1 - z0, V(0, -w / 2.0, z0))
    b.rotate(V(0, 0, 0), Z, math.degrees(math.atan2(dy, dx)))
    b.translate(V(p0[0], p0[1], 0))
    return b


def bar_yz(p0, p1, w, x0, t, holes=(), slot=None):
    """Flat bar in the y-z plane from (y, z) p0 to p1 (hole centres), width w, rounded ends r w/2, thickness t from x0
    along +x. holes: distances along the bar; slot: (s0, s1) along the bar, width = hole."""
    dy, dz = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dy, dz)
    r = w / 2.0
    b = fuse_all([Part.makeBox(t, length, w, V(x0, 0, -r)), cyl_x(w, x0, x0 + t, 0, 0),
                  cyl_x(w, x0, x0 + t, length, 0)])
    cuts = [cyl_x(HOLE_PIN, x0 - 1, x0 + t + 1, s, 0) for s in holes]
    if slot is not None:
        s0, s1 = slot
        cuts += [cyl_x(HOLE_PIN, x0 - 1, x0 + t + 1, s0, 0), cyl_x(HOLE_PIN, x0 - 1, x0 + t + 1, s1, 0),
                 Part.makeBox(t + 2, s1 - s0, HOLE_PIN, V(x0 - 1, s0, -HOLE_PIN / 2.0))]
    if cuts:
        b = b.cut(cuts)
    b.rotate(V(0, 0, 0), X, math.degrees(math.atan2(dz, dy)))
    b.translate(V(0, p0[0], p0[1]))
    return b


def pin_x(xc, half, y, z, flip=False):
    """M16 bolt along x through a joint centred at xc, shank +-half, head on +x (flip: on -x), lock nut opposite."""
    s = -1 if flip else 1
    return [cyl_x(P.pin_d, xc - half - 2.0, xc + half + 2.0, y, z),
            hex_x(AF[16], xc + s * half, xc + s * (half + HEAD_K[16]), y, z),
            hex_x(AF[16], xc - s * half, xc - s * (half + NUT_M[16]), y, z)]


# ---------------------------------------------------------------------
# Mount: plate under both front lower beams, link lugs, actuator lug, pins
# ---------------------------------------------------------------------
Z_PLATE = P.robot_lower_beam_z[0] - P.mount_t          # 609


def mount_bolt_xy():
    return [(x, y) for x in P.mount_bolt_x for y in P.robot_front_beam_y]


def mount_plate():
    b = box_span(P.mount_x, P.mount_y, (Z_PLATE, P.robot_lower_beam_z[0]))
    holes = [cyl_z(P.m10_hole, Z_PLATE - 1, Z_PLATE + 20, x, y) for x, y in mount_bolt_xy()]
    holes.append(cyl_z(P.gnss_hole, Z_PLATE - 1, Z_PLATE + 20, P.gnss_xy[0], P.gnss_xy[1]))
    return b.cut(holes)


def mount_bolts():
    """M10 8.8 x 70 from the top through the lower beam and the plate, nut under the plate."""
    out = []
    z_top = P.robot_lower_beam_z[1]
    for (x, y) in mount_bolt_xy():
        out.append(hex_z(AF[10], z_top, z_top + HEAD_K[10], x, y))
        out.append(cyl_z(10.0, Z_PLATE - NUT_M[10] - 3.0, z_top, x, y))
        out.append(hex_z(AF[10], Z_PLATE - NUT_M[10], Z_PLATE, x, y))
    return out


def robot_lugs():
    """2 lugs 10 mm welded under the plate, pivots of the top and bottom links."""
    y0 = P.mount_y[0]
    pts = [(y0, Z_PLATE), (560.0, Z_PLATE), (480.0, 470.0), (480.0, P.lug_z0), (y0, P.lug_z0)]
    out = []
    for s in (1, -1):
        x0 = s * P.lug_x - P.lug_t / 2.0
        lug = poly_yz(pts, x0, P.lug_t)
        lug = lug.cut([cyl_x(HOLE_PIN, x0 - 1, x0 + P.lug_t + 1, P.pivot_y, z) for z in P.pivot_z])
        out.append(lug)
    return out


def actuator_lug():
    """Single lug 10 mm under the plate (x 0) with pin A; the float link bars straddle it."""
    ya, za = P.act_A
    r = 22.0
    x0 = -P.lug_t / 2.0
    body = poly_yz([(ya - r, Z_PLATE), (ya + r, Z_PLATE), (ya + r, za), (ya - r, za)], x0, P.lug_t)
    end = cyl_x(2 * r, x0, x0 + P.lug_t, ya, za)
    return fuse_all([body, end]).cut(cyl_x(HOLE_PIN, x0 - 1, x0 + P.lug_t + 1, ya, za))

def link_half():
    """Half width of a link joint: lug, washers and both bars."""
    return P.lug_t / 2.0 + P.link_gap + P.link_t


def robot_pins():
    out = []
    for s in (1, -1):
        for z in P.pivot_z:
            out += pin_x(s * P.lug_x, link_half(), P.pivot_y, z, flip=s < 0)
    out += pin_x(0.0, FLOAT_HALF, P.act_A[0], P.act_A[1])
    return out


# ---------------------------------------------------------------------
# Linkage: top and bottom links, 2 flat bars per side (drawn at the default cut height)
# ---------------------------------------------------------------------
def _links(z_robot, z_deck):
    out = []
    for s in (1, -1):
        xc = s * P.lug_x
        for x0 in (xc + P.lug_t / 2.0 + P.link_gap, xc - P.lug_t / 2.0 - P.link_gap - P.link_t):
            out.append(bar_yz((P.pivot_y, z_robot), (YP, z_deck), P.link_w, x0, P.link_t,
                              holes=(0.0, P.link_L)))
    return out


def top_links():
    return _links(P.pivot_z[1], ZP[1])


def bottom_links():
    return _links(P.pivot_z[0], ZP[0])


# ---------------------------------------------------------------------
# Actuator with float link (redrawn for each height): A fixed, B = bottom deck pivot at x 0
# ---------------------------------------------------------------------
def _along(shape, a, u):
    """Shape drawn along +y from the origin (x across) -> along unit (uy, uz) from point a (y, z)."""
    shape.rotate(V(0, 0, 0), X, math.degrees(math.atan2(u[1], u[0])))
    shape.translate(V(0, a[0], a[1]))
    return shape


def actuator_shapes(cut_set=None, lift=0.0):
    """(body, rod, float_link) for the actuator set to cut height cut_set, deck lifted by 'lift' mm above it (float).
    The rod eye sits on the deck pin B, the rear eye R on the float link; the robot pin A slides in its slot. The
    actuator length follows cut_set."""
    cut_set = P.cut_h if cut_set is None else cut_set
    ya, za = P.act_A
    yb, zb = P.deck_pivot(cut_set + lift)               # B = bottom deck pivot (x 0)
    d = math.hypot(yb - ya, zb - za)
    u = ((yb - ya) / d, (zb - za) / d)
    L = P.act_length(cut_set) - P.float_len             # actuator pin to pin
    r0 = (yb - u[0] * L, zb - u[1] * L)                 # rear eye R
    tube0, tube1 = 35.0, P.act_closed - 25.0
    t_rod = 2 * (P.act_lug_x - 1.0)
    eye = cyl_x(34.0, -P.lug_t / 2.0, P.lug_t / 2.0, 0.0, 0.0).cut(cyl_x(HOLE_PIN, -20, 20, 0.0, 0.0))
    neck = cyl_y(18.0, 17.0, tube0, 0.0, 0.0)
    tube = cyl_y(P.act_tube_d, tube0, tube1, 0.0, 0.0)
    mw, mh, ml = P.act_motor
    motor = Part.makeBox(mw, ml, mh, V(-mw / 2.0, tube0 + 15.0, -P.act_tube_d / 2.0 - mh + 5.0))
    body = [_along(s, r0, u) for s in (eye, neck, tube, motor)]
    rod = [cyl_y(P.act_rod_d, tube1, L - 16.0, 0.0, 0.0),
           cyl_x(34.0, -t_rod / 2.0, t_rod / 2.0, L, 0.0).cut(cyl_x(HOLE_PIN, -20, 20, L, 0.0))]
    rod = [_along(s, r0, u) for s in rod]
    f_end = (r0[0] - u[0] * P.float_len, r0[1] - u[1] * P.float_len)
    fw, ft = P.float_bar
    links = []
    for x0 in (P.lug_t / 2.0 + 1.0, -P.lug_t / 2.0 - 1.0 - ft):
        links.append(bar_yz(r0, f_end, fw, x0, ft, holes=(0.0,), slot=(P.float_len - P.float_slot, P.float_len)))
    links += pin_x(0.0, FLOAT_HALF, r0[0], r0[1])                        # rear eye pin
    return body, rod, links

# ---------------------------------------------------------------------
# Deck: plate, skirt, swath boards, crossbeam, lugs, pins
# ---------------------------------------------------------------------
def rotor_c(side):
    """Bottom of the blades of a rotor (side +1 right, -1 left) at the default cut height."""
    return C0 + (P.rotor_dz if side < 0 else 0.0)


def flange_z(side):
    """Bottom of the spindle flange."""
    return rotor_c(side) + P.blade_t + P.blade_gap + P.bar_t + P.boss_h + P.spindle_below


def spindle_bolt_xy(side):
    r = P.spindle_bolt_pcd / 2.0
    xc = side * P.rotor_x
    return [(xc + r * math.cos(math.radians(a)), YC + r * math.sin(math.radians(a))) for a in (30.0, 150.0, 270.0)]


def standoff_xy(side):
    xc = side * P.rotor_x
    s = P.standoff_xy
    return [(xc + a, YC + b) for a in (-s, s) for b in (-s, s)]


def _stadium(r, z0, z1):
    return fuse_all([box_span((-P.rotor_x, P.rotor_x), (YC - r, YC + r), (z0, z1)),
                     cyl_z(2 * r, z0, z1, P.rotor_x, YC), cyl_z(2 * r, z0, z1, -P.rotor_x, YC)])


def deck_plate():
    s = _stadium(P.hood_r, DB, DT)
    notch = box_span((-P.discharge_half, P.discharge_half), (YC - P.hood_r - 1.0, YP - P.deck_notch), (DB - 1, DT + 1))
    holes = [notch]
    for side in (1, -1):
        holes.append(cyl_z(P.spindle_housing_d + 1.0, DB - 1, DT + 1, side * P.rotor_x, YC))
        holes += [cyl_z(8.5, DB - 1, DT + 1, x, y) for x, y in spindle_bolt_xy(side)]
    return s.cut(holes)


def skirt():
    """3 mm skirt: 2 rolled half circles (outer sides), straight front, short straight pieces at the rear next to the
    discharge opening (x -200 .. 200 open)."""
    r1, r0 = P.hood_r, P.hood_r - P.skirt_t
    z0, z1 = SKIRT_Z0, DB
    out = []
    for side in (1, -1):
        xc = side * P.rotor_x
        ring = tube_z(2 * r1, 2 * r0, z0, z1, xc, YC)
        keep = box_span((xc, xc + side * (r1 + 5)) if side > 0 else (xc - r1 - 5, xc), (YC - r1 - 5, YC + r1 + 5),
                        (z0 - 1, z1 + 1))
        out.append(ring.common(keep))
        xs = (P.discharge_half, P.rotor_x) if side > 0 else (-P.rotor_x, -P.discharge_half)
        out.append(box_span(xs, (YC - r1, YC - r0), (z0, z1)))
    out.append(box_span((-P.rotor_x, P.rotor_x), (YC + r0, YC + r1), (z0, z1)))
    return out


def swath_boards():
    out = []
    y0 = YC - P.hood_r
    for side in (1, -1):
        p0 = (side * (P.discharge_half - P.swath_t / 2.0), y0)
        p1 = (side * (P.swath_end_x - P.swath_t / 2.0), y0 - P.swath_len)
        out.append(bar_plan(p0, p1, P.swath_t, SKIRT_Z0, DB))
    return out


def crossbeam():
    w, h, t = P.crossbeam
    y = (YP + P.deck_lug_dy, YP + P.deck_lug_dy + w)
    xs = (-P.crossbeam_x, P.crossbeam_x)
    outer = box_span(xs, y, (DT, DT + h))
    inner = box_span((xs[0] - 1, xs[1] + 1), (y[0] + t, y[1] - t), (DT + t, DT + h - t))
    return outer.cut(inner)


def deck_lugs():
    out = []
    y = (YP - P.deck_lug_dy, YP + P.deck_lug_dy)
    for s in (1, -1):
        x0 = s * P.lug_x - P.lug_t / 2.0
        lug = poly_yz([(y[0], DT), (y[1], DT), (y[1], DT + P.deck_lug_h), (y[0], DT + P.deck_lug_h)], x0, P.lug_t)
        out.append(lug.cut([cyl_x(HOLE_PIN, x0 - 1, x0 + P.lug_t + 1, YP, z) for z in ZP]))
    return out


def actuator_deck_lug():
    """Double lug (2 x 8 mm, x +-(10..18)) on the deck for the rod eye, pin B = bottom deck pivot."""
    y = (YP - P.deck_lug_dy, YP + P.deck_lug_dy)
    out = []
    for x0 in (P.act_lug_x, -P.act_lug_x - P.act_lug_t):
        lug = poly_yz([(y[0], DT), (y[1], DT), (y[1], ZP[0] + 25.0), (y[0], ZP[0] + 25.0)], x0, P.act_lug_t)
        out.append(lug.cut(cyl_x(HOLE_PIN, x0 - 1, x0 + P.act_lug_t + 1, YP, ZP[0])))
    return out


def deck_pins():
    out = []
    for s in (1, -1):
        for z in ZP:
            out += pin_x(s * P.lug_x, link_half(), YP, z, flip=s < 0)
    out += pin_x(0.0, P.act_lug_x + P.act_lug_t, YP, ZP[0])
    return out

# ---------------------------------------------------------------------
# Deck: spindles and motor stands (both sides)
# ---------------------------------------------------------------------
def doublers():
    out = []
    for side in (1, -1):
        xc = side * P.rotor_x
        d = cyl_z(P.doubler_d, DT, DT + P.doubler_t, xc, YC)
        cuts = [cyl_z(P.spindle_housing_d + 1.0, DT - 1, DT + P.doubler_t + 1, xc, YC)]
        cuts += [cyl_z(8.5, DT - 1, DT + P.doubler_t + 1, x, y) for x, y in spindle_bolt_xy(side)]
        out.append(d.cut(cuts))
    return out


def spacer_rings():
    """Left rotor: 2 rings 12 mm between the doubler and the spindle flange (rotor 24 mm higher)."""
    xc = -P.rotor_x
    z0 = DT + P.doubler_t
    out = []
    for k in range(2):
        za = z0 + k * P.rotor_dz / 2.0
        ring = tube_z(P.spacer_d[0], P.spacer_d[1], za, za + P.rotor_dz / 2.0, xc, YC)
        out.append(ring.cut([cyl_z(8.5, za - 1, za + 20, x, y) for x, y in spindle_bolt_xy(-1)]))
    return out


def spindle_housings():
    """Bought deck spindle: housing O62 through deck and doubler, flange O130, neck, bore for the shaft."""
    out = []
    for side in (1, -1):
        xc = side * P.rotor_x
        f = flange_z(side)
        z_bot = f - P.spindle_below
        nd, nh = P.spindle_neck
        s = fuse_all([cyl_z(P.spindle_housing_d, z_bot, f, xc, YC),
                      cyl_z(P.spindle_flange_d, f, f + P.spindle_flange_t, xc, YC),
                      cyl_z(nd, f + P.spindle_flange_t, f + P.spindle_flange_t + nh, xc, YC)])
        s = s.cut(cyl_z(P.spindle_shaft_d + 0.5, z_bot - 1, f + 40, xc, YC))
        out.append(s.cut([cyl_z(8.5, f - 1, f + 20, x, y) for x, y in spindle_bolt_xy(side)]))
    return out


def spindle_bolts():
    """3 x M8 per spindle through flange, (spacer rings), doubler and deck, nut under the deck."""
    out = []
    for side in (1, -1):
        zf = flange_z(side) + P.spindle_flange_t
        for (x, y) in spindle_bolt_xy(side):
            out += [hex_z(AF[8], zf, zf + HEAD_K[8], x, y), cyl_z(8.0, DB - NUT_M[8] - 2.0, zf, x, y),
                    hex_z(AF[8], DB - NUT_M[8], DB, x, y)]
    return out


def standoffs():
    out = []
    for side in (1, -1):
        z1 = flange_z(side) + P.motor_plate_z
        out += [cyl_z(P.standoff_d, DT + P.doubler_t, z1, x, y) for x, y in standoff_xy(side)]
    return out


def motor_plates():
    out = []
    for side in (1, -1):
        xc = side * P.rotor_x
        z0 = flange_z(side) + P.motor_plate_z
        h = P.motor_plate / 2.0
        b = box_span((xc - h, xc + h), (YC - h, YC + h), (z0, z0 + P.motor_plate_t))
        cuts = [cyl_z(40.0, z0 - 1, z0 + 20, xc, YC)] + [cyl_z(10.5, z0 - 1, z0 + 20, x, y)
                                                        for x, y in standoff_xy(side)]
        out.append(b.cut(cuts))
    return out


def motors():
    """48 V BLDC 750 W, flange 90 down on the motor plate, body O90 x 140, terminal box towards the robot."""
    out = []
    for side in (1, -1):
        xc = side * P.rotor_x
        z0 = flange_z(side) + P.motor_plate_z + P.motor_plate_t
        f = P.motor_flange / 2.0
        flange = box_span((xc - f, xc + f), (YC - f, YC + f), (z0, z0 + P.motor_flange_t))
        body = cyl_z(P.motor_d, z0 + P.motor_flange_t, z0 + P.motor_flange_t + P.motor_len, xc, YC)
        tbox = box_span((xc - 25.0, xc + 25.0), (YC - P.motor_d / 2.0 - 30.0, YC - P.motor_d / 2.0 + 5.0),
                        (z0 + 60.0, z0 + 100.0))
        out.append(fuse_all([flange, body, tbox]))
    return out


# ---------------------------------------------------------------------
# Rotor (one function per part, side +1 right / -1 left): turns about (side * rotor_x, YC)
# ---------------------------------------------------------------------
def _blade_angles(side):
    return (0.0, 180.0) if side > 0 else (90.0, 270.0)


def _radial(shape, side, angle):
    shape.rotate(V(side * P.rotor_x, YC, 0), Z, angle)
    return shape


def spindle_shaft(side):
    xc = side * P.rotor_x
    c = rotor_c(side)
    z0 = c + P.blade_t + P.blade_gap + P.bar_t + P.boss_h
    return cyl_z(P.spindle_shaft_d, z0, flange_z(side) + P.spindle_flange_t + P.spindle_shaft_top, xc, YC)


def boss(side):
    c = rotor_c(side)
    z0 = c + P.blade_t + P.blade_gap + P.bar_t
    return cyl_z(P.boss_d, z0, z0 + P.boss_h, side * P.rotor_x, YC)


def blade_bar(side):
    """Laser-cut bar 340 x 60 x 12, rounded ends, centre hole, 2 pivot holes for the blades; centre nut below it."""
    xc = side * P.rotor_x
    c = rotor_c(side)
    z0, z1 = c + P.blade_t + P.blade_gap, c + P.blade_t + P.blade_gap + P.bar_t
    r = P.bar_w / 2.0
    b = fuse_all([box_span((xc - P.bar_r + r, xc + P.bar_r - r), (YC - r, YC + r), (z0, z1)),
                  cyl_z(P.bar_w, z0, z1, xc - P.bar_r + r, YC), cyl_z(P.bar_w, z0, z1, xc + P.bar_r - r, YC)])
    b = b.cut([cyl_z(HOLE_PIN, z0 - 1, z1 + 1, xc + s * P.blade_pivot_r, YC) for s in (1, -1)])
    nut = hex_z(27.0, c, z0, xc, YC)
    return _radial(fuse_all([b, nut]), side, _blade_angles(side)[0])


def blades(side):
    """2 free-swinging blades 50 x 6, r 115 .. 255, on M16 bolts at r 140 (drawn radial, as they run)."""
    xc = side * P.rotor_x
    c = rotor_c(side)
    out = []
    for a in _blade_angles(side):
        b = box_span((xc + P.blade_r[0], xc + P.blade_r[1]), (YC - P.blade_w / 2.0, YC + P.blade_w / 2.0),
                     (c, c + P.blade_t))
        b = b.cut(cyl_z(HOLE_PIN, c - 1, c + P.blade_t + 1, xc + P.blade_pivot_r, YC))
        out.append(_radial(b, side, a))
    return out


def blade_bolts(side):
    xc = side * P.rotor_x
    c = rotor_c(side)
    z1 = c + P.blade_t + P.blade_gap + P.bar_t
    hd, hh = P.blade_bolt_head
    out = []
    for a in _blade_angles(side):
        x = xc + P.blade_pivot_r
        parts = [cyl_z(hd, c - hh, c, x, YC), cyl_z(P.pin_d, c, z1, x, YC), hex_z(AF[16], z1, z1 + NUT_M[16], x, YC)]
        out += [_radial(s, side, a) for s in parts]
    return out


def coupling(side):
    f = flange_z(side)
    return tube_z(P.coupling_d, P.spindle_shaft_d + 0.5, f + P.coupling_z[0], f + P.coupling_z[1], side * P.rotor_x,
                  YC)


def motor_shaft(side):
    f = flange_z(side)
    z0 = f + P.spindle_flange_t + P.spindle_shaft_top
    return cyl_z(P.spindle_shaft_d, z0, f + P.motor_plate_z + P.motor_plate_t, side * P.rotor_x, YC)


# ---------------------------------------------------------------------
# Controller box on the rear lower beams
# ---------------------------------------------------------------------
BOX_BOLT_X = (-125.0, 125.0)


def box_base():
    z0 = P.robot_lower_beam_z[1]
    b = box_span(P.box_base_x, P.box_base_y, (z0, z0 + P.box_base_t))
    return b.cut([cyl_z(8.4, z0 - 1, z0 + 5, x, y) for x in BOX_BOLT_X for y in P.robot_rear_beam_y])


def controller_box():
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    b = box_span(P.box_x, P.box_y, (z0, z0 + P.box_h))
    lid = box_span((P.box_x[0] - 3, P.box_x[1] + 3), (P.box_y[0] - 3, P.box_y[1] + 3),
                   (z0 + P.box_h, z0 + P.box_h + 12))
    glands = [cyl_y(20.0, P.box_y[1], P.box_y[1] + 18.0, x, z0 + 30.0) for x in (-80.0, 0.0, 80.0)]
    return fuse_all([b, lid] + glands)


def box_bolts():
    out = []
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    zb = P.robot_lower_beam_z[0]
    for x in BOX_BOLT_X:
        for y in P.robot_rear_beam_y:
            out += [hex_z(AF[8], z0, z0 + HEAD_K[8], x, y), cyl_z(8.0, zb - NUT_M[8] - 3.0, z0, x, y),
                    hex_z(AF[8], zb - NUT_M[8], zb, x, y)]
    return out


# ---------------------------------------------------------------------
# Weeds and chips (renders, animation): plant dicts from wpk_weeds
# ---------------------------------------------------------------------
def weed_shapes(p, cut_z=None):
    """{'stem', 'crown', 'leaves'} shapes of one plant; cut_z: cut off at that height (stub only, no crown)."""
    x, y, h = p["x"], p["y"], p["h"]
    out = {"stem": [], "crown": [], "leaves": []}
    top = h if cut_z is None else min(h, cut_z)
    out["stem"].append(cyl_z(p["stem_d"], 0.0, top, x, y))
    if p["kind"] == "dock":                                       # basal rosette stays under the cut
        for k in range(5):
            a = math.radians(p["rot"] + 72.0 * k)
            leaf = Part.makeBox(220.0, 70.0, 4.0, V(0, -35.0, 0))
            leaf.rotate(V(0, 0, 0), Y, -18.0)
            leaf.rotate(V(0, 0, 0), Z, math.degrees(a))
            leaf.translate(V(x, y, 10.0))
            out["leaves"].append(leaf)
    if cut_z is not None and cut_z < h:
        return out
    cd = p["crown_d"]
    if p["kind"] == "ragwort":                                    # flat yellow umbel
        out["crown"].append(Part.makeCone(cd / 2.0, cd / 2.0 * 0.8, 60.0, V(x, y, h - 60.0), Z))
        for k in range(3):                                        # leafy stem
            a = math.radians(p["rot"] + 120.0 * k)
            zl = h * (0.35 + 0.15 * k)
            out["leaves"].append(Part.makeCone(28.0, 2.0, 120.0, V(x, y, zl), V(math.cos(a), math.sin(a), 0.5)))
    elif p["kind"] == "thistle":                                  # spiny leaves along the stem, purple heads
        for k in range(4):
            a = math.radians(p["rot"] + 90.0 * k)
            zl = h * (0.3 + 0.13 * k)
            out["leaves"].append(Part.makeCone(30.0, 2.0, 150.0, V(x, y, zl), V(math.cos(a), math.sin(a), 0.35)))
        for k in range(3):
            a = math.radians(p["rot"] + 120.0 * k)
            out["crown"].append(Part.makeSphere(28.0, V(x + 50.0 * math.cos(a), y + 50.0 * math.sin(a),
                                                        h - 30.0 - 20.0 * k)))
    else:                                                         # dock: red-brown seed panicle
        out["crown"].append(Part.makeCone(cd / 2.0, 8.0, h * 0.4, V(x, y, h * 0.6), Z))
    return out


def chip_shape(c):
    """One piece of chopped weed lying on the ground (dict from wpk_weeds)."""
    b = Part.makeBox(c["l"], c["w"], 8.0, V(-c["l"] / 2.0, -c["w"] / 2.0, 0))
    b.rotate(V(0, 0, 0), X, c["tilt"])
    b.rotate(V(0, 0, 0), Z, c["rot"])
    b.translate(V(c["x"], c["y"], c["z"]))
    return b
