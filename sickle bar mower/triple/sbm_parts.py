"""Parts of the triple sickle bar mower. One function per part, returns a Part shape (or a list) in robot coordinates
in the work position (front bar on the ground, wings down, knives in the middle of their stroke).

The cutter bar module is drawn in its own frame (u along the bar from the start of the knife to the drive end,
w forward from the knife back edge, z up) and mapped with place(): front bar u = +x from x -625, right wing u = +x
from x 625, left wing = the right wing mirrored. Moving parts: the knives (sub-Parts, shifted along u), the con-rods
(redrawn per crank angle, rods()), the actuators (redrawn per position)."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import sbm_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

AF = {8: 13.0, 10: 17.0, 16: 24.0, 30: 46.0}
NUT_M = {8: 6.8, 10: 8.4, 16: 13.0, 30: 24.0}
HEAD_K = {8: 5.3, 10: 6.4, 16: 10.0, 30: 18.7}

C = P.cut_h
ZB = C - 9.0 - P.beam[1]                        # bottom of the flat bar = top of the shoes
HOLE_PIN = P.pin_d + 1.0
Z_PLATE = P.robot_lower_beam_z[0] - P.mount_t          # 611
FLOAT_HALF = P.lug_t / 2.0 + 1.0 + P.float_bar[1]
YB0, ZB0 = P.head_pivot(0.0)                    # bottom head pivot in work
ZT0 = ZB0 + (P.pivot_z[1] - P.pivot_z[0])        # top head pivot


# ---------------------------------------------------------------------
# Basic functions
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


def rhs(x, y, z, t, axis):
    """Rectangular hollow section in the box x, y, z (spans), wall t, open along axis 'x', 'y' or 'z'."""
    outer = box_span(x, y, z)
    lo = [x[0] + t, y[0] + t, z[0] + t]
    hi = [x[1] - t, y[1] - t, z[1] - t]
    k = "xyz".index(axis)
    lo[k] -= 1.0
    hi[k] += 1.0
    return outer.cut(box_span((lo[0], hi[0]), (lo[1], hi[1]), (lo[2], hi[2])))


def poly_yz(points, x0, t):
    """Closed polygon in the y-z plane, (y, z), extruded along +x from x0."""
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0))


def poly_uw(points, z0, t):
    """Closed polygon in the u-w (x-y) plane, extruded along +z from z0."""
    pts = [V(u, w, z0) for (u, w) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, t))


def poly_wz(points, u0, t):
    return poly_yz(points, u0, t)


def _hex(af, p0, axis, length):
    r = af / math.sqrt(3.0)
    c = [r * math.cos(math.radians(60 * i)) for i in range(6)]
    s = [r * math.sin(math.radians(60 * i)) for i in range(6)]
    if axis == "x":
        pts = [V(p0[0], p0[1] + c[i], p0[2] + s[i]) for i in range(6)]
        d = V(length, 0, 0)
    elif axis == "y":
        pts = [V(p0[0] + c[i], p0[1], p0[2] + s[i]) for i in range(6)]
        d = V(0, length, 0)
    else:
        pts = [V(p0[0] + c[i], p0[1] + s[i], p0[2]) for i in range(6)]
        d = V(0, 0, length)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(d)


def hex_z(af, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return _hex(af, (x, y, z0), "z", z1 - z0)


def hex_x(af, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return _hex(af, (x0, y, z), "x", x1 - x0)


def hex_y(af, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return _hex(af, (x, y0, z), "y", y1 - y0)


def bar_plan(p0, p1, w, z0, z1, round_ends=False):
    """Plate standing on edge from (x, y) p0 to p1 (plan), width w, between z0 and z1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    b = Part.makeBox(length, w, z1 - z0, V(0, -w / 2.0, z0))
    if round_ends:
        b = fuse_all([b, cyl_z(w, z0, z1, 0.0, 0.0), cyl_z(w, z0, z1, length, 0.0)])
    b.rotate(V(0, 0, 0), Z, math.degrees(math.atan2(dy, dx)))
    b.translate(V(p0[0], p0[1], 0))
    return b


def bar_yz(p0, p1, w, x0, t, holes=(), slot=None):
    """Flat bar in the y-z plane from (y, z) p0 to p1 (hole centres), width w, rounded ends, thickness t from x0
    along +x. holes: distances along the bar; slot: (s0, s1) along the bar, width = pin hole."""
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


def bar_xz(p0, p1, w, y0, t, holes=()):
    """Flat bar in the x-z plane from (x, z) p0 to p1, width w, rounded ends, thickness t from y0 along +y."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dz)
    r = w / 2.0
    b = fuse_all([Part.makeBox(length, t, w, V(0, y0, -r)), cyl_y(w, y0, y0 + t, 0, 0),
                  cyl_y(w, y0, y0 + t, length, 0)])
    if holes:
        b = b.cut([cyl_y(HOLE_PIN, y0 - 1, y0 + t + 1, s, 0) for s in holes])
    b.rotate(V(0, 0, 0), Y, -math.degrees(math.atan2(dz, dx)))
    b.translate(V(p0[0], 0, p0[1]))
    return b


def pin_x(xc, half, y, z, flip=False, d=16):
    """Bolt along x through a joint centred at xc, shank +-half, head on +x (flip: on -x), nut opposite."""
    s = -1 if flip else 1
    return [cyl_x(float(d), xc - half - 2.0, xc + half + 2.0, y, z),
            hex_x(AF[d], xc + s * half, xc + s * (half + HEAD_K[d]), y, z),
            hex_x(AF[d], xc - s * half, xc - s * (half + NUT_M[d]), y, z)]


def pin_y(yc, half, x, z, d=16):
    """Bolt along y through a joint centred at yc, shank +-half, head on -y, nut on +y."""
    return [cyl_y(float(d), yc - half - 2.0, yc + half + 2.0, x, z),
            hex_y(AF[d], yc - half - HEAD_K[d], yc - half, x, z),
            hex_y(AF[d], yc + half, yc + half + NUT_M[d], x, z)]


def mirror_x(shapes):
    if isinstance(shapes, (list, tuple)):
        return [s.mirror(V(0, 0, 0), X) for s in shapes]
    return shapes.mirror(V(0, 0, 0), X)


# ---------------------------------------------------------------------
# Cutter bar module (local u, w, z) and placing it on the robot
# ---------------------------------------------------------------------
BARS = {"F": P.front_L, "R": P.wing_L, "L": P.wing_L}


def place(shapes, bar):
    """Local bar shapes -> robot coordinates (work position). bar: 'F' front, 'R' right wing, 'L' left wing."""
    single = not isinstance(shapes, (list, tuple))
    out = []
    for s in ([shapes] if single else shapes):
        s = s.copy()
        if bar == "F":
            s.translate(V(P.x_front0, P.y_front, 0))
        else:
            s.translate(V(P.x_wing0, P.y_wing, 0))
            if bar == "L":
                s = s.mirror(V(0, 0, 0), X)
        out.append(s)
    return out[0] if single else out


def u_dir(bar):
    """Direction of +u in robot coordinates (knife shift)."""
    return V(-1, 0, 0) if bar == "L" else V(1, 0, 0)


def bar_beam(L):
    """Flat bar 80 x 10 from the inner shoe to the outer shoe, top 9 below the cut plane."""
    return box_span((P.shoe_in[0], L + 230.0), (P.beam_w0, P.beam_w0 + P.beam[0]), (ZB, C - 9.0))


def stiffener(L):
    """RHS 50 x 30 x 3 welded behind the flat bar (w -145 .. -95), bottom flush with the flat bar."""
    w1 = P.beam_w0
    return rhs((P.shoe_in[1], L + 230.0), (w1 - P.stiff[0], w1), (ZB, ZB + P.stiff[1]), P.stiff[2], "x")


def clip_u(L, kind):
    n = P.clip_n[kind]
    return [L * (i + 0.5) / n for i in range(n)]


def clips(L, kind):
    """Hold-down clips: a top plate over the upper knife back and a web down to the flat bar (bolted, M8)."""
    out = []
    for uc in clip_u(L, kind):
        u = (uc - P.clip_wu / 2.0, uc + P.clip_wu / 2.0)
        top = box_span(u, (P.beam_w0, -5.0), (C + 9.0, C + 9.0 + P.clip_t))
        web = box_span(u, (P.beam_w0, P.beam_w0 + P.clip_web), (C - 9.0, C + 9.0))
        out.append(fuse_all([top, web]))
    return out


def shoe(u0, u1):
    """Shoe (skid), pressed from 5 mm plate and open on top: sole from w -260 to the nose at w 60, top flush with
    the bottom of the flat bar."""
    t = ZB
    k = P.shoe_t
    pts = [(-260.0, 14.0), (-240.0, 0.0), (20.0, 0.0), (P.shoe_w[1], 28.0), (P.shoe_w[1], t), (-260.0, t)]
    inner = [(-260.0 + k, 14.0 + k), (-240.0 + k, k), (20.0 - k * 0.4, k), (P.shoe_w[1] - k, 28.0 + k * 0.4),
             (P.shoe_w[1] - k, t + 1.0), (-260.0 + k, t + 1.0)]
    return poly_wz(pts, u0, u1 - u0).cut(poly_wz(inner, u0 + k, u1 - u0 - 2 * k))


def shoes(L):
    return [shoe(*P.shoe_in), shoe(L + 150.0, L + 150.0 + P.shoe_out)]


def sections(L, z0):
    out = []
    n = int(round(L / P.pitch))
    hb = (P.pitch - P.sec_gap) / 2.0
    ht = P.sec_tip_w / 2.0
    for i in range(n):
        uc = (i + 0.5) * P.pitch
        out.append(poly_uw([(uc - hb, P.sec_back), (uc + hb, P.sec_back), (uc + ht, P.sec_tip),
                            (uc - ht, P.sec_tip)], z0, P.sec_t))
    return out


def knife(L, which):
    """Upper or lower knife in the middle of its stroke: knife back, sections, knife head."""
    if which == "upper":
        back = box_span((0.0, L + 40.0), (-P.kback[0], 0.0), (C + P.sec_t, C + P.sec_t + P.kback[1]))
        head = box_span((L + P.head_u[0], L + P.head_u[1]), (-20.0, 0.0), (C + 9.0, C + 20.0))
        return [fuse_all([back, head])] + sections(L, C)
    back = fuse_all([box_span((0.0, L), (-P.kback[0], 0.0), (C - 9.0, C - P.sec_t)),
                     box_span((L, L + 40.0), (-60.0, 0.0), (C - 9.0, C - P.sec_t)),
                     box_span((L + P.head_u[0], L + P.head_u[1]), (-60.0, -28.0), (C - P.sec_t, C + 20.0))])
    return [back] + sections(L, C - P.sec_t)


def crank_pin(L, k, theta):
    """(u, w) of crank pin k (0 upper, 1 lower; 180 deg apart) at crank angle theta (rad)."""
    a = theta + (math.pi if k else 0.0)
    return L + P.crank_u[k] + P.ECC * math.cos(a), P.crank_w[k] + P.ECC * math.sin(a)


def rod_len(k):
    return P.crank_u[k] - (P.head_u[0] + P.head_u[1]) / 2.0


def knife_shift(theta):
    """(upper, lower) knife shift along u (mm) from the middle position at crank angle theta (rad)."""
    out = []
    for k in (0, 1):
        pu, pw = crank_pin(0.0, k, theta)
        head = pu - math.sqrt(rod_len(k) ** 2 - (pw - P.head_pin_w[k]) ** 2)
        mid = P.crank_u[k] - math.sqrt(rod_len(k) ** 2 - P.ECC ** 2)
        out.append(head - mid)
    return out[0], out[1]


THETA0 = math.pi / 2.0          # crank angle of the drawn model: knives in the middle (shift 0)


def rods(L, theta=THETA0):
    """Con-rods with their eyes and pins, crank pins up to the gearbox, at crank angle theta. Knife heads move with
    knife_shift(theta) (relative to the drawn model at THETA0)."""
    shift = knife_shift(theta)
    out = []
    for k in (0, 1):
        z0, z1 = C + P.rod_z[k][0], C + P.rod_z[k][1]
        cu, cw = crank_pin(L, k, theta)
        hu = L + (P.head_u[0] + P.head_u[1]) / 2.0 + shift[k]
        hw = P.head_pin_w[k]
        out.append(bar_plan((hu, hw), (cu, cw), P.rod_w, z0, z1))
        out.append(cyl_z(30.0, z0, z1, hu, hw).cut(cyl_z(12.5, z0 - 1, z1 + 1, hu, hw)))
        out.append(cyl_z(30.0, z0, z1, cu, cw).cut(cyl_z(16.5, z0 - 1, z1 + 1, cu, cw)))
        out.append(cyl_z(12.0, C + 20.0, z1, hu, hw))                                  # head pin
        out.append(cyl_z(16.0, z0, C + P.box_z[0], cu, cw))                              # crank pin
    return out


def gearbox(L):
    """Crank gearbox (cast housing, 2 output shafts at 180 deg)."""
    return box_span((L + P.box_u[0], L + P.box_u[1]), P.box_w, (C + P.box_z[0], C + P.box_z[1]))


def motor(L):
    mu, mw = L + P.motor_uw[0], P.motor_uw[1]
    z0 = C + P.box_z[1]
    gear = cyl_z(P.gear_d, z0, z0 + P.gear_h, mu, mw)
    mot = cyl_z(P.motor_d, z0 + P.gear_h, z0 + P.gear_h + P.motor_h, mu, mw)
    cap = cyl_z(60.0, z0 + P.gear_h + P.motor_h, z0 + P.gear_h + P.motor_h + 20.0, mu, mw)
    return [gear, mot, cap]


def drive_plate(L):
    """Plate on the stiffener that carries the gearbox (behind the con-rods)."""
    return box_span((L + P.box_u[0], L + P.box_u[1]), (P.box_w[0], P.box_w[0] + 12.0),
                    (ZB + P.stiff[1], C + P.box_z[0]))


def module(L, kind):
    """Static parts of a bar module: name -> shape(s) (local)."""
    return {"beam": bar_beam(L), "stiffener": stiffener(L), "clips": clips(L, kind), "shoes": shoes(L),
            "drive_plate": drive_plate(L), "gearbox": gearbox(L), "motor": motor(L)}


# ---------------------------------------------------------------------
# Front mount (as the weed picker): plate under both front lower beams, lugs, pins
# ---------------------------------------------------------------------
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
    ya, za = P.act_A
    r = 22.0
    x0 = -P.lug_t / 2.0
    body = poly_yz([(ya - r, Z_PLATE), (ya + r, Z_PLATE), (ya + r, za), (ya - r, za)], x0, P.lug_t)
    end = cyl_x(2 * r, x0, x0 + P.lug_t, ya, za)
    return fuse_all([body, end]).cut(cyl_x(HOLE_PIN, x0 - 1, x0 + P.lug_t + 1, ya, za))


def link_half():
    return P.lug_t / 2.0 + P.link_gap + P.link_t


def robot_pins():
    out = []
    for s in (1, -1):
        for z in P.pivot_z:
            out += pin_x(s * P.lug_x, link_half(), P.pivot_y, z, flip=s < 0)
    out += pin_x(0.0, FLOAT_HALF, P.act_A[0], P.act_A[1])
    return out


def _links(z_robot, z_head):
    out = []
    for s in (1, -1):
        xc = s * P.lug_x
        for x0 in (xc + P.lug_t / 2.0 + P.link_gap, xc - P.lug_t / 2.0 - P.link_gap - P.link_t):
            out.append(bar_yz((P.pivot_y, z_robot), (YB0, z_head), P.link_w, x0, P.link_t, holes=(0.0, P.link_L)))
    return out


def top_links():
    return _links(P.pivot_z[1], ZT0)


def bottom_links():
    return _links(P.pivot_z[0], ZB0)


# ---------------------------------------------------------------------
# Front head frame (moves with the links) and bar frame (rolls on the roll pin)
# ---------------------------------------------------------------------
def head_frame():
    """Front plate 12 mm with the roll pin hole, 2 link lugs 10 mm and the double actuator lug, welded."""
    x = P.head_plate_x
    plate = box_span((-x, x), P.head_plate_y, P.head_plate_z)
    y0, y1 = P.head_lug_y
    parts = [plate]
    for s in (1, -1):
        x0 = s * P.lug_x - P.lug_t / 2.0
        parts.append(poly_yz([(y0, ZB0 - 23.0), (y1, ZB0 - 23.0), (y1, ZT0 + 27.0), (y0, ZT0 + 27.0)], x0, P.lug_t))
    for s in (1, -1):
        x0 = s * P.act_lug_x if s > 0 else -P.act_lug_x - P.act_lug_t
        parts.append(fuse_all([poly_yz([(YB0, ZB0 - 22.0), (y1, ZB0 - 22.0), (y1, ZB0 + 22.0), (YB0, ZB0 + 22.0)],
                                       x0, P.act_lug_t), cyl_x(44.0, x0, x0 + P.act_lug_t, YB0, ZB0)]))
    frame = fuse_all(parts)
    holes = [cyl_y(P.roll_pin_d + 1.0, P.head_plate_y[0] - 1, P.head_plate_y[1] + 1, 0.0, P.roll_z)]
    holes += [cyl_x(HOLE_PIN, -P.lug_x - 20, P.lug_x + 20, YB0, z) for z in (ZB0, ZT0)]
    return frame.cut(holes)


def head_pins():
    """M16 pins of the links (head side) and of the actuator rod eye."""
    out = []
    for s in (1, -1):
        out += pin_x(s * P.lug_x, link_half(), YB0, ZB0, flip=s < 0)
        out += pin_x(s * P.lug_x, link_half(), YB0, ZT0, flip=s < 0)
    out += pin_x(0.0, P.act_lug_x + P.act_lug_t, YB0, ZB0)
    return out


def roll_pin():
    """M30 bolt along y: head behind the head plate, through a spacer and the cross tube, nut in front."""
    y0 = P.head_plate_y[0]
    y1 = P.tube_y[1]
    return [cyl_y(P.roll_pin_d, y0 - 2.0, y1 + NUT_M[30] + 4.0, 0.0, P.roll_z),
            hex_y(AF[30], y0 - HEAD_K[30], y0, 0.0, P.roll_z),
            hex_y(AF[30], y1, y1 + NUT_M[30], 0.0, P.roll_z)]


def bar_frame():
    """Cross tube RHS 60 x 40 x 3 on the roll pin, 2 arm plates down to the stiffener of the bar, roll spacer."""
    z = (P.roll_z - P.tube_h / 2.0, P.roll_z + P.tube_h / 2.0)
    tube = rhs((-P.tube_x, P.tube_x), P.tube_y, z, P.tube_t, "x")
    arms = []
    yk0 = P.y_front + P.beam_w0 - P.stiff[0]
    for s in (1, -1):
        x0 = s * P.arm_x - P.arm_t / 2.0
        arms.append(box_span((x0, x0 + P.arm_t), (yk0, yk0 + P.stiff[0]), (ZB + P.stiff[1], z[1] + 2.0)))
    spacer = cyl_y(50.0, P.head_plate_y[1] + 1.0, P.tube_y[0], 0.0, P.roll_z)
    frame = fuse_all([tube, spacer] + arms)
    return frame.cut(cyl_y(P.roll_pin_d + 1.0, P.head_plate_y[1], P.tube_y[1] + 1, 0.0, P.roll_z))


# ---------------------------------------------------------------------
# Front actuator with float link (redrawn): A fixed on the mount, B = bottom head pivot at x 0
# ---------------------------------------------------------------------
def _along_yz(shape, a, u):
    shape.rotate(V(0, 0, 0), X, math.degrees(math.atan2(u[1], u[0])))
    shape.translate(V(0, a[0], a[1]))
    return shape


def front_actuator(lift_set=P.lift_work, lift=0.0):
    """(body, rod, float_link) for the actuator set to lift_set, the bar at lift (>= lift_set while the float link
    has slack). The rear eye R hangs in the float link; A slides in its slot."""
    ya, za = P.act_A
    yb, zb = P.head_pivot(lift)
    d = math.hypot(yb - ya, zb - za)
    u = ((yb - ya) / d, (zb - za) / d)
    L = P.act_length(lift_set) - P.float_len
    r0 = (yb - u[0] * L, zb - u[1] * L)
    tube0, tube1 = 35.0, P.act_closed - 45.0
    t_rod = 2 * (P.act_lug_x - 1.0)
    eye = cyl_x(34.0, -P.lug_t / 2.0, P.lug_t / 2.0, 0.0, 0.0).cut(cyl_x(HOLE_PIN, -20, 20, 0.0, 0.0))
    neck = cyl_y(18.0, 17.0, tube0, 0.0, 0.0)
    tube = cyl_y(P.act_tube_d, tube0, tube1, 0.0, 0.0)
    mw, mh, ml = P.act_motor
    mot = Part.makeBox(mw, ml, mh, V(-mw / 2.0, tube0 + 15.0, P.act_tube_d / 2.0 - 5.0))
    body = [_along_yz(s, r0, u) for s in (eye, neck, tube, mot)]
    rod = [cyl_y(P.act_rod_d, tube1, L - 16.0, 0.0, 0.0),
           cyl_x(34.0, -t_rod / 2.0, t_rod / 2.0, L, 0.0).cut(cyl_x(HOLE_PIN, -20, 20, L, 0.0))]
    rod = [_along_yz(s, r0, u) for s in rod]
    f_end = (r0[0] - u[0] * P.float_len, r0[1] - u[1] * P.float_len)
    fw, ft = P.float_bar
    links = []
    for x0 in (P.lug_t / 2.0 + 1.0, -P.lug_t / 2.0 - 1.0 - ft):
        links.append(bar_yz(r0, f_end, fw, x0, ft, holes=(0.0,), slot=(P.float_len - P.float_slot, P.float_len)))
    links += pin_x(0.0, FLOAT_HALF, r0[0], r0[1])
    return body, rod, links


# ---------------------------------------------------------------------
# Mid frame: rails under the outer top beams, cross tube, hanger plates, actuator post
# ---------------------------------------------------------------------
Z_RAIL = (P.robot_upper_beam_z[0] - P.robot_beam, P.robot_upper_beam_z[0])       # 619 .. 659
Z_CROSS = (Z_RAIL[0] - P.cross[1], Z_RAIL[0])                                     # 559 .. 619
RAIL_X = P.robot_upper_beam_x[1]


def rail_bolt_xy():
    return [(s * RAIL_X, sy * y) for s in (1, -1) for sy in (1, -1) for y in P.robot_upper_hole_y]


def mid_frame():
    """Welded mid frame: 2 rails RHS 40 x 40 x 3, cross tube RHS 80 x 60 x 4, 4 hanger plates 12 mm with the hinge
    holes, 2 post plates 10 mm with the anchor slots."""
    b = P.robot_beam / 2.0
    parts = []
    for s in (1, -1):
        parts.append(rhs((s * RAIL_X - b, s * RAIL_X + b), (-P.rail_y, P.rail_y), Z_RAIL, 3.0, "y"))
    cy = P.cross[0] / 2.0
    parts.append(rhs((-P.cross_x, P.cross_x), (-cy, cy), Z_CROSS, P.cross[2], "x"))
    hx, hz = P.hinge
    for s in (1, -1):
        for sy in (1, -1):
            y0 = cy if sy > 0 else -cy - P.hanger_t
            x = (P.hanger_x[0], P.hanger_x[1]) if s > 0 else (-P.hanger_x[1], -P.hanger_x[0])
            w = P.hanger_x[1] - P.hanger_x[0]
            plate = fuse_all([box_span(x, (y0, y0 + P.hanger_t), (hz, Z_CROSS[1])),
                              cyl_y(w, y0, y0 + P.hanger_t, s * hx, hz)])
            parts.append(plate.cut(cyl_y(P.hinge_pin_d + 1.0, y0 - 1, y0 + P.hanger_t + 1, s * hx, hz)))
        for xw in (P.hanger_x[0], P.hanger_x[1] - P.hanger_t):
            x = (xw, xw + P.hanger_t) if s > 0 else (-xw - P.hanger_t, -xw)
            parts.append(box_span(x, (-cy, cy), (P.hanger_box_z, Z_CROSS[0])))
    za = P.ANCHOR_Z
    for sy in (1, -1):
        y = P.post_y if sy > 0 else (-P.post_y[1], -P.post_y[0])
        plate = box_span((-P.post_x, P.post_x), y, (za - 30.0, Z_CROSS[0]))
        slots = []
        for s in (1, -1):
            x0, x1 = P.anchor_x
            slots += [cyl_y(HOLE_PIN, y[0] - 1, y[1] + 1, s * x0, za), cyl_y(HOLE_PIN, y[0] - 1, y[1] + 1, s * x1, za),
                      box_span((x0, x1) if s > 0 else (-x1, -x0), (y[0] - 1, y[1] + 1),
                               (za - HOLE_PIN / 2.0, za + HOLE_PIN / 2.0))]
        parts.append(plate.cut(slots))
    frame = fuse_all(parts)
    holes = [cyl_z(P.m10_hole, Z_RAIL[0] - 1, Z_RAIL[1] + 1, x, y) for x, y in rail_bolt_xy()]
    return frame.cut(holes)


def rail_bolts():
    """M10 8.8 x 90 from the top through the top beam and the rail, nut under the rail."""
    out = []
    z_top = P.robot_upper_beam_z[1]
    for (x, y) in rail_bolt_xy():
        out.append(hex_z(AF[10], z_top, z_top + HEAD_K[10], x, y))
        out.append(cyl_z(10.0, Z_RAIL[0] - NUT_M[10] - 3.0, z_top, x, y))
        out.append(hex_z(AF[10], Z_RAIL[0] - NUT_M[10], Z_RAIL[0], x, y))
    return out


def hinge_pins():
    """M30 hinge bolts along y through both hanger plates and the hinge tube of each wing."""
    out = []
    half = P.cross[0] / 2.0 + P.hanger_t
    for s in (1, -1):
        out += pin_y(0.0, half, s * P.hinge[0], P.hinge[1], d=30)
    return out


# ---------------------------------------------------------------------
# Wing hinge (right wing, robot coordinates; the left one is mirrored)
# ---------------------------------------------------------------------
def wing_hinge():
    """Hinge bracket on the inner shoe, hinge tube and 2 lever plates, welded."""
    hx, hz = P.hinge
    yt = P.cross[0] / 2.0 - 2.0                       # 38: 2 mm from the hanger plates
    bracket = box_span((hx - 12.0, hx + 12.0), (-yt, yt), (ZB, hz))
    tube = cyl_y(P.hinge_tube[0], -yt, yt, hx, hz)
    bx, bz = P.lever_pin(0.0)
    levers = []
    for sy in (1, -1):
        y0 = P.lever_plate_y[0] if sy > 0 else -P.lever_plate_y[1]
        levers.append(bar_xz((hx, hz), (bx, bz), 50.0, y0, P.lever_plate_y[1] - P.lever_plate_y[0]))
    body = fuse_all([bracket, tube] + levers)
    return body.cut([cyl_y(P.hinge_tube[1], -yt - 1, yt + 1, hx, hz),
                     cyl_y(HOLE_PIN, -P.lever_plate_y[1] - 1, P.lever_plate_y[1] + 1, bx, bz)])


def lever_pin():
    bx, bz = P.lever_pin(0.0)
    return pin_y(0.0, P.lever_plate_y[1], bx, bz)


# ---------------------------------------------------------------------
# Wing actuator (redrawn, robot coordinates for the right wing; mirror for the left)
# ---------------------------------------------------------------------
def _along_xz(shape, a, d):
    shape.rotate(V(0, 0, 0), Y, -math.degrees(math.atan2(d[1], d[0])))
    shape.translate(V(a[0], 0, a[1]))
    return shape


def wing_actuator(fold=0.0, act=None):
    """(body, rod, anchor pin) of the right wing actuator for the wing at 'fold' (deg) with the actuator at length
    act (None: work setting; the anchor pin then sits where the slot puts it)."""
    act = P.WACT_WORK if act is None else act
    xa = P.wing_pin_x(fold, act)
    za = P.ANCHOR_Z
    bx0, bz0 = P.lever_pin(0.0)
    hx, hz = P.hinge
    a = math.radians(fold)
    bx = hx + (bx0 - hx) * math.cos(a) - (bz0 - hz) * math.sin(a)
    bz = hz + (bx0 - hx) * math.sin(a) + (bz0 - hz) * math.cos(a)
    L = math.hypot(bx - xa, bz - za)
    d = ((bx - xa) / L, (bz - za) / L)
    tube0, tube1 = 60.0, P.wact_closed - 30.0
    eye = cyl_y(36.0, -10.0, 10.0, 0.0, 0.0).cut(cyl_y(HOLE_PIN, -20, 20, 0.0, 0.0))
    neck = cyl_x(20.0, 17.0, tube0, 0.0, 0.0)
    tube = cyl_x(P.wact_tube_d, tube0, tube1, 0.0, 0.0)
    mot = Part.makeBox(110.0, 50.0, 60.0, V(tube0 + 20.0, -25.0, P.wact_tube_d / 2.0 - 5.0))
    body = [_along_xz(s, (xa, za), d) for s in (eye, neck, tube, mot)]
    rod = [cyl_x(P.wact_rod_d, tube1, L - 16.0, 0.0, 0.0),
           cyl_y(32.0, -10.0, 10.0, L, 0.0).cut(cyl_y(HOLE_PIN, -20, 20, L, 0.0))]
    rod = [_along_xz(s, (xa, za), d) for s in rod]
    pin = pin_y(0.0, P.post_y[1], xa, za)
    return body, rod, pin


# ---------------------------------------------------------------------
# Controller box on the rear lower beams
# ---------------------------------------------------------------------
def box_base():
    z0 = P.robot_lower_beam_z[1]
    b = box_span(P.box_base_x, P.box_base_y, (z0, z0 + P.box_base_t))
    return b.cut([cyl_z(8.4, z0 - 1, z0 + 10, x, y) for x in P.box_bolt_x for y in P.robot_rear_beam_y])


def controller_box():
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    return box_span(P.box_x, P.box_y, (z0, z0 + P.box_h))


def box_bolts():
    z0 = P.robot_lower_beam_z[1]
    out = []
    for x in P.box_bolt_x:
        for y in P.robot_rear_beam_y:
            out.append(cyl_z(8.0, P.robot_lower_beam_z[0] - 9.0, z0 + P.box_base_t + 5.0, x, y))
            out.append(hex_z(AF[8], z0 + P.box_base_t, z0 + P.box_base_t + 5.3, x, y))
            out.append(hex_z(AF[8], P.robot_lower_beam_z[0] - 6.8, P.robot_lower_beam_z[0], x, y))
    return out


# ---------------------------------------------------------------------
# Grass (render and animation): a tuft = 3 crossed thin blades
# ---------------------------------------------------------------------
def tuft(x, y, h, r=28.0, rot=0.0):
    out = []
    for k in range(3):
        a = math.radians(rot + 60.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        p = [V(x - r * ca, y - r * sa, 0.0), V(x + r * ca, y + r * sa, 0.0), V(x + 0.15 * r * ca, y + 0.15 * r * sa, h)]
        p.append(p[0])
        out.append(Part.Face(Part.makePolygon(p)))
    return out
