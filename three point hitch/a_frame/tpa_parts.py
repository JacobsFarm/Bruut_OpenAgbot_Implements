"""Parts of the A-frame hitch. Every function returns a Part shape in robot coordinates, in the work pose (lift frame at
0 degrees, cultivator level on its gauge wheels), except the coupler and LA36 helpers that take a base point.

Shared with the parallel and lift variants (they import this module):
- male_frame(base), male_latch(base), female(base): the A-frame coupler at a coupler origin base (y, z);
- la36_body(), la36_rod(L0) and la36_placement(): the Linak LA36 in its own frame, placed per pose;
- cultivator(base): the small cultivator of three point hitch/simple with the female triangle.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tpa_params as P
import tph_params as TP
import tph_parts as TG
from tph_parts import box_span, cyl, tube_span, rect_tube, fuse_all, plate_yz  # noqa: F401


def compound(shapes):
    return Part.makeCompound([s for s in shapes if s is not None])


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both_sides(shape):
    """Shape drawn on the right side (+x) and its mirror image."""
    return [shape, mirror_x(shape)]


def pin_x(x0, x1, y, z, d, head_d=None, head_t=4.0):
    """Pin along x from x0 to x1 with a head outside x1."""
    head_d = head_d or d + 10.0
    s = 1.0 if x1 >= x0 else -1.0
    return Part.makeCompound([cyl(d, (x0, y, z), (x1, y, z)), cyl(head_d, (x1, y, z), (x1 + s * head_t, y, z))])


# ---------------------------------------------------------------------
# Coupler frame: local (x = u, y = v, z = w) -> robot
# ---------------------------------------------------------------------
def cp_matrix(base, lean=None):
    ev, ew = P.cp_axes(lean)
    return App.Matrix(1, 0, 0, 0,
                      0, ev[0], ew[0], base[0],
                      0, ev[1], ew[1], base[1],
                      0, 0, 0, 1)


def to_robot(shape, base, lean=None):
    s = shape.copy()
    s.transformShape(cp_matrix(base, lean))
    return s


def _leg_u(v):
    u0, u1 = P.cp_leg_u
    return u0 + (u1 - u0) * v / P.cp_leg_v


def _leg_line(v0, v1, offset=0.0, sx=1):
    """Points (u, v) on the right leg centre line, shifted 'offset' outwards in the triangle plane."""
    du, dv = P.cp_leg_u[1] - P.cp_leg_u[0], P.cp_leg_v
    n = math.hypot(du, dv)
    nu, nv = dv / n, -du / n                  # outward normal (+u side)
    p0 = (sx * (_leg_u(v0) + offset * nu), v0 + offset * nv)
    p1 = (sx * (_leg_u(v1) + offset * nu), v1 + offset * nv)
    return p0, p1


# ---------------------------------------------------------------------
# Male triangle (on the hitch)
# ---------------------------------------------------------------------
def _slot_x(x0, x1, p, q, d):
    """Slot (stadium) of width d from p to q (y, z) through x0..x1."""
    a = Part.makeCompound([cyl(d, (x0, p[0], p[1]), (x1, p[0], p[1])), cyl(d, (x0, q[0], q[1]), (x1, q[0], q[1]))])
    xm = (x0 + x1) / 2.0
    return a.fuse(rect_tube((xm, p[0], p[1]), (xm, q[0], q[1]), d, x1 - x0, up=(1.0, 0.0, 0.0)))


def slot_dir_local():
    """Unit (v, w) of the LA36 slot in the apex lugs: away from the tower, along the LA36 in the work pose."""
    d = P.act_d(0.0)
    dy, dz = d[0] - P.act_c[0], d[1] - P.act_c[1]
    n = math.hypot(dy, dz)
    ev, ew = P.cp_axes()
    return (dy * ev[0] + dz * ev[1]) / n, (dy * ew[0] + dz * ew[1]) / n


def male_local(act_lugs=True, brace_lugs=True):
    """act_lugs / brace_lugs: the LA36 slot lugs on the apex and the pitch brace lugs (a_frame only)."""
    t = P.cp_tube / 2.0
    parts = []
    for sx in (-1, 1):
        p0, p1 = _leg_line(-15.0, P.cp_top_v[0] + 5.0, sx=sx)
        parts.append(rect_tube((p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), P.cp_tube, P.cp_tube, P.cp_wall,
                               up=(0.0, 0.0, 1.0)))
        x0, x1 = sorted((sx * 215.0, sx * P.cp_foot_u[1]))
        parts.append(box_span((x0, x1), (-22.0, 22.0), (-t, t)))
    parts.append(box_span((-P.cp_top_u, P.cp_top_u), P.cp_top_v, (-t, t)))
    ub = _leg_u(sum(P.cp_bottom_v) / 2.0) + 5.0
    parts.append(tube_span((-ub, ub), P.cp_bottom_v, (-t, t), P.cp_wall, "x"))
    vm = P.cp_brace_pin[0]
    um = _leg_u(vm) + 3.0
    parts.append(tube_span((-um, um), (vm - 20.0, vm + 20.0), (-t, t), P.cp_wall, "x"))
    # LA36 lugs on the apex: the rod eye (27.8 wide) runs between them in a slot away from the tower
    va, wa = P.cp_act_pin
    sv, sw = slot_dir_local()
    ve, we = va + P.float_slot * sv, wa + P.float_slot * sw
    xi = P.act_rod_eye_c / 2.0 + P.act_eye_clear
    # the lugs reach only 20 mm towards the tower: the outer tube ends 14 mm from them when fully lifted
    lug = [(ve - 25.0, -t + 2.0), (va + 12.0, -t + 2.0), (va + 8.0, wa - 18.0), (ve - 8.0, we - 20.0),
           (ve - 25.0, we - 10.0)]
    slots = []
    for sx in ((-1, 1) if act_lugs else ()):
        x0 = xi if sx > 0 else -xi - 8.0
        pl = plate_yz(lug, x0, 8.0)
        pl = pl.fuse([cyl(40.0, (x0, va, wa), (x0 + 8.0, va, wa)), cyl(40.0, (x0, ve, we), (x0 + 8.0, ve, we))])
        parts.append(pl)
        slots.append(_slot_x(x0 - 1.0, x0 + 9.0, (va, wa), (ve, we), P.act_pin_d + 0.4))
    # brace lugs on the middle cross tube
    vb, wb = P.cp_brace_pin
    xb = P.brace_eye[1] / 2.0 + 1.0
    blug = [(vb - 20.0, -t + 2.0), (vb + 20.0, -t + 2.0), (vb + 18.0, wb), (vb - 18.0, wb)]
    for sx in ((-1, 1) if brace_lugs else ()):
        x0 = xb if sx > 0 else -xb - 8.0
        parts.append(plate_yz(blug, x0, 8.0).fuse(cyl(36.0, (x0, vb, wb), (x0 + 8.0, vb, wb))))
    s = fuse_all(parts)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 200.0, sx * 250.0))
        s = s.cut(cyl(P.cp_pin_d + 0.5, (x0, 0.0, 0.0), (x1, 0.0, 0.0)))
    for sl in slots:
        s = s.cut(sl)
    if brace_lugs:
        s = s.cut(cyl(16.4, (-40.0, vb, wb), (40.0, vb, wb)))
    return s.cut(cyl(P.cp_latch_d + 1.0, (0.0, P.cp_latch_v, -30.0), (0.0, P.cp_latch_v, 30.0)))


def male_frame(base=None, lean=None, act_lugs=True, brace_lugs=True):
    return to_robot(male_local(act_lugs, brace_lugs), base or P.lower_b, lean)


def male_latch(base=None, lean=None):
    """Spring latch O20 along w through the bottom cross tube into the female lock plate, with a T-handle in front."""
    w0, w1 = P.cp_latch_w
    v = P.cp_latch_v
    s = Part.makeCompound([cyl(P.cp_latch_d, (0.0, v, w0), (0.0, v, w1)),
                           cyl(12.0, (-50.0, v, w0 - 6.0), (50.0, v, w0 - 6.0)),
                           cyl(12.0, (0.0, v, w0 - 12.0), (0.0, v, w0 + 1.0))])
    return to_robot(s, base or P.lower_b, lean)


# ---------------------------------------------------------------------
# Female triangle (on the implement)
# ---------------------------------------------------------------------
def female_local():
    t = P.cp_tube / 2.0
    w_pl = t + P.cf_gap + P.cf_t / 2.0
    parts = []
    for sx in (-1, 1):
        p0, p1 = _leg_line(P.cf_plate_v[0], P.cf_plate_v[1], offset=5.0, sx=sx)
        parts.append(rect_tube((p0[0], p0[1], w_pl), (p1[0], p1[1], w_pl), P.cf_plate_w, P.cf_t, up=(0.0, 0.0, 1.0)))
        lip_off = t + P.cf_gap + P.cf_lip_t / 2.0
        q0, q1 = _leg_line(P.cf_lip_v[0], P.cf_lip_v[1], offset=lip_off, sx=sx)
        w_lo, w_hi = P.cf_lip_w, t + P.cf_gap + P.cf_t
        wc = (w_lo + w_hi) / 2.0
        parts.append(rect_tube((q0[0], q0[1], wc), (q1[0], q1[1], wc), P.cf_lip_t, w_hi - w_lo, up=(0.0, 0.0, 1.0)))
    v_hook = P.cp_top_v[1] + P.cf_gap
    w_back = (t + P.cf_gap, t + P.cf_gap + P.cf_t)
    parts.append(box_span((-P.cf_hook_u, P.cf_hook_u), (v_hook, v_hook + P.cf_t), (P.cf_hook_w, w_back[1])))
    parts.append(box_span((-P.cf_hook_u, P.cf_hook_u), (330.0, v_hook + P.cf_t), w_back))
    lock = box_span((-P.cf_lock_u, P.cf_lock_u), P.cf_lock_v, w_back)
    lock = lock.cut(cyl(P.cp_latch_d + 1.0, (0.0, P.cp_latch_v, 0.0), (0.0, P.cp_latch_v, 60.0)))
    parts.append(lock)
    return fuse_all(parts)


def female(base=None, lean=None):
    return to_robot(female_local(), base or P.lower_b, lean)


def female_point(vw, base=None, lean=None):
    y, z = P.cp_point(base or P.lower_b, vw, lean)
    return y, z


# ---------------------------------------------------------------------
# Linak LA36 in its own frame: z = axis from the back fixture (body pin, origin) to the rod eye; x = robot x;
# y = act_motor_side * direction of the motor. la36_placement() puts it between two pins.
# ---------------------------------------------------------------------
def _hex_prism(af, h, z0):
    r = af / math.sqrt(3.0)
    pts = [V(r * math.cos(math.radians(60 * i)), r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, h))


def _rounded_box(x, y, z, r):
    b = box_span(x, y, z)
    try:
        edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1.0]
        return b.makeFillet(r, edges)
    except Exception:
        return b


def la36_body(motor_side=None, retracted=None, roll=0.0):
    """Housing with the parallel motor, back fixture with hex nut, outer tube (aluminium) and end cap.
    roll: housing and motor turned about the spindle axis (deg); the back fixture keeps its hole along x (the LA36
    is sold with the back fixture at 0 or 90 degrees)."""
    s = P.act_motor_side if motor_side is None else motor_side
    retracted = retracted or P.act_retracted
    top = P.act_house_h - P.act_house_below
    hw = P.act_house_w / 2.0
    z0 = P.act_house_start
    z_gear = z0 + P.act_gear_len
    z_end = z0 + P.act_house_len
    ys = sorted((-s * P.act_house_below, s * top))
    back = Part.makeCylinder(P.act_back_c / 2.0, P.act_back_f, V(0, 0, -P.act_back_d))
    back = back.cut(cyl(P.act_eye_hole, (-20.0, 0.0, 0.0), (20.0, 0.0, 0.0)))
    af, _ = P.act_back_nut
    z_nut = P.act_back_f - P.act_back_d
    nut = _hex_prism(af, z0 - z_nut + 2.0, z_nut)
    gear = _rounded_box((-hw, hw), ys, (z0, z_gear), 12.0)
    motor_c = s * (top - P.act_motor_d / 2.0)
    motor = Part.makeCylinder(P.act_motor_d / 2.0, z_end - z_gear, V(0, motor_c, z_gear))
    web = box_span((-hw + 18.0, hw - 18.0), sorted((s * 10.0, motor_c)), (z_gear - 2.0, z_end - 25.0))
    t = P.act_tube / 2.0
    tube_end = retracted - P.act_tube_end_gap
    tube = _rounded_box((-t, t), (-t, t), (z_gear - 5.0, tube_end), 4.0)
    cap = Part.makeCylinder(t - 2.0, 6.0, V(0, 0, tube_end - 3.0))
    house = fuse_all([nut, gear, motor, web, tube, cap])
    if roll:
        house.rotate(V(0, 0, 0), V(0, 0, 1), roll)
    return fuse_all([back, house])


def la36_rod(length, retracted=None, pin_half=None, stroke=None):
    """Inner tube with the solid rod eye at z = length, and the rod pin O12 through the eye (pin_half: half length).
    The inner tube is drawn over the whole stroke (inside the outer tube when retracted), so the rod can slide by
    its placement."""
    stroke = stroke or P.act_stroke
    eye_z0 = length - (P.act_rod_eye_f - P.act_rod_eye_d)
    rod_z0 = eye_z0 - stroke - 25.0
    rod = Part.makeCylinder(P.act_rod_d / 2.0, eye_z0 - rod_z0 + 1.0, V(0, 0, rod_z0))
    eye = Part.makeCylinder(P.act_rod_eye_c / 2.0, P.act_rod_eye_f, V(0, 0, eye_z0))
    eye = eye.cut(cyl(P.act_eye_hole, (-20.0, 0.0, length), (20.0, 0.0, length)))
    s = fuse_all([rod, eye])
    if pin_half:
        s = Part.makeCompound([s, pin_x(-pin_half, pin_half, 0.0, length, P.act_pin_d, head_d=20.0)])
    return s


def la36_rotation(body_pin, rod_pin):
    dy, dz = rod_pin[0] - body_pin[0], rod_pin[1] - body_pin[1]
    L = math.hypot(dy, dz)
    return App.Rotation(V(1, 0, 0), math.degrees(math.atan2(-dy / L, dz / L))), L


def la36_placements(body_pin, rod_pin, length_ref, x=0.0):
    """Placements of the body and the rod (drawn with its eye at z = length_ref) between two pins (y, z)."""
    rot, L = la36_rotation(body_pin, rod_pin)
    base = V(x, body_pin[0], body_pin[1])
    u = V(0, (rod_pin[0] - body_pin[0]) / L, (rod_pin[1] - body_pin[1]) / L)
    return App.Placement(base, rot), App.Placement(base + u * (L - length_ref), rot), L


def la36_shapes(body_pin, rod_pin, x=0.0, motor_side=None, retracted=None, pin_half=None):
    """Body and rod as shapes in robot coordinates (for the static model and checks)."""
    rot, L = la36_rotation(body_pin, rod_pin)
    body = la36_body(motor_side, retracted)
    rod = la36_rod(L, retracted, pin_half)
    pl = App.Placement(V(x, body_pin[0], body_pin[1]), rot)
    body.Placement = pl
    rod.Placement = pl
    return body, rod, L


# ---------------------------------------------------------------------
# Mount: rear toolbar, hangers, lower lugs (three point hitch/simple) and the tower for the LA36
# ---------------------------------------------------------------------
def pivot_pins():
    """Lower arm pivot pins O16 through the lugs of the simple hitch (with heads), fixed to the mount."""
    out = []
    yp, zp = P.lower_a
    for sx in (-1, 1):
        x_in = sx * (P.lower_ax - P.arm_t / 2.0 - 3.0 - TP.lug_t - 4.0)
        x_out = sx * (P.lower_ax + P.arm_t / 2.0 + 3.0 + TP.lug_t + 4.0)
        out.append(pin_x(x_in, x_out, yp, zp, P.cp_pin_d, head_d=26.0))
    return compound(out)


def tower():
    """Post 60 x 60 x 4 on the toolbar with a cap plate."""
    h = P.tower / 2.0
    post = tube_span((-h, h), P.tower_y, (P.tb_z[1], P.tower_top), 4.0, "z")
    cap = box_span((-h, h), P.tower_y, (P.tower_top, P.tower_top + 6.0))
    gussets = []
    yc = (P.tower_y[0] + P.tower_y[1]) / 2.0
    z0 = P.tb_z[1]
    for sx in (-1, 1):
        pts = [V(sx * h, yc - 4.0, z0), V(sx * (h + 90.0), yc - 4.0, z0), V(sx * h, yc - 4.0, z0 + 180.0)]
        gussets.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 8.0, 0)))
    return fuse_all([post, cap] + gussets)


def tower_clevis():
    """2 plates 8 mm behind the post with the hole for the LA36 back fixture (body pin act_c)."""
    c = P.act_c
    xi = P.act_back_c / 2.0 + P.act_eye_clear
    y_post = P.tower_y[0]
    # the hex of the back fixture starts 14.9 mm from the pin: the plates stay within r 14 around it
    pts = ((y_post, c[1] + 26.0), (y_post, c[1] - 40.0), (c[0] + 14.0, c[1] - 8.0), (c[0], c[1] + 14.0))
    out = []
    for sx in (-1, 1):
        x0 = xi if sx > 0 else -xi - 8.0
        pl = plate_yz(pts, x0, 8.0).fuse(cyl(28.0, (x0, c[0], c[1]), (x0 + 8.0, c[0], c[1])))
        out.append(pl.cut(cyl(P.act_pin_d + 0.4, (x0 - 1.0, c[0], c[1]), (x0 + 9.0, c[0], c[1]))))
    return compound(out)


def tower_pin():
    c = P.act_c
    x = P.act_back_c / 2.0 + P.act_eye_clear + 8.0 + 4.0
    return pin_x(-x, x, c[0], c[1], P.act_pin_d, head_d=20.0)


# ---------------------------------------------------------------------
# Lift frame (moves as one body about lower_a)
# ---------------------------------------------------------------------
def arm(sx):
    """Lower arm, flat bar 50 x 20, from the pivot to the lower pin, bosses O44 at both ends."""
    ya, za = P.lower_a
    yb, zb = P.lower_b
    xa, xb = sx * P.lower_ax, sx * P.cp_pin_u
    t = P.arm_t / 2.0
    bar = rect_tube((xa, ya, za), (xb, yb, zb), P.arm_t, P.arm_h)
    boss_a = cyl(P.cp_boss_d, (xa - t, ya, za), (xa + t, ya, za))
    boss_b = cyl(P.cp_boss_d, (xb - t, yb, zb), (xb + t, yb, zb))
    s = bar.fuse([boss_a, boss_b]).removeSplitter()
    s = s.cut(cyl(P.cp_pin_d + 0.5, (xa - 15, ya, za), (xa + 15, ya, za)))
    return s.cut(cyl(P.cp_pin_d + 0.5, (xb - 15, yb, zb), (xb + 15, yb, zb)))


def arm_cross():
    """Cross tube 40 x 40 x 3 between the arms with the 2 lugs for the pitch brace."""
    f = P.arm_cross_frac
    y = P.lower_a[0] + f * (P.lower_b[0] - P.lower_a[0])
    z = P.lower_a[1] + f * (P.lower_b[1] - P.lower_a[1])
    xi = P.lower_ax + f * (P.cp_pin_u - P.lower_ax) - P.arm_t / 2.0 + 1.0
    h = P.arm_cross / 2.0
    parts = [tube_span((-xi, xi), (y - h, y + h), (z - h, z + h), 3.0, "x")]
    e = P.brace_e()
    xb = P.brace_eye[1] / 2.0 + 1.0
    for sx in (-1, 1):
        x0 = xb if sx > 0 else -xb - 8.0
        lug = box_span((x0, x0 + 8.0), (e[0] - 18.0, e[0] + 18.0), (z + h - 2.0, e[1]))
        parts.append(lug.fuse(cyl(36.0, (x0, e[0], e[1]), (x0 + 8.0, e[0], e[1]))))
    s = fuse_all(parts)
    return s.cut(cyl(16.4, (-40.0, e[0], e[1]), (40.0, e[0], e[1])))


def brace():
    """Pitch brace: turnbuckle O26 between 2 eyes O36 x 20 (sets the pitch of the triangle on the arms)."""
    e, f = P.brace_e(), P.brace_f()
    a, b = V(0, e[0], e[1]), V(0, f[0], f[1])
    u = b - a
    u.normalize()
    w = P.brace_eye[1] / 2.0
    r = P.brace_eye[0] / 2.0
    eyes = [cyl(P.brace_eye[0], p - V(w, 0, 0), p + V(w, 0, 0)).cut(cyl(16.4, p - V(15, 0, 0), p + V(15, 0, 0)))
            for p in (a, b)]
    necks = [cyl(16.0, a + u * (r - 3.0), a + u * (r + 7.0)), cyl(16.0, b - u * (r + 7.0), b - u * (r - 3.0))]
    tube = cyl(P.brace_d, a + u * (r + 6.0), b - u * (r + 6.0))
    nuts = [cyl(P.brace_d + 8.0, a + u * (r + 6.0), a + u * (r + 16.0)),
            cyl(P.brace_d + 8.0, b - u * (r + 16.0), b - u * (r + 6.0))]
    return compound(eyes + necks + [tube] + nuts)


def frame_pins():
    """Lower pins (foot of the triangle + arm boss, linch pin outside), brace pins and the LA36 body pin."""
    yb, zb = P.lower_b
    out = []
    for sx in (-1, 1):
        x0 = sx * (P.cp_foot_u[0] - 4.0)
        x1 = sx * (P.cp_pin_u + P.arm_t / 2.0 + 10.0)
        out.append(pin_x(x0, x1, yb, zb, P.cp_pin_d, head_d=28.0))
    xb = P.brace_eye[1] / 2.0 + 1.0 + 8.0 + 4.0
    for p in (P.brace_e(), P.brace_f()):
        out.append(pin_x(-xb, xb, p[0], p[1], 16.0, head_d=24.0))
    return compound(out)


# ---------------------------------------------------------------------
# Implement: the small cultivator of three point hitch/simple with a female triangle (work pose)
# ---------------------------------------------------------------------
def _cult_shift(base):
    """Shift of the simple cultivator so that it hangs in the female triangle at the coupler origin 'base'."""
    return V(0, P.cult_dy + base[0] - P.lower_b[0], base[1] - P.lower_b[1])


def cultivator_frame(base=None):
    """Weldment: toolbar 60 x 60 x 4, gauge wheel arms (as simple), female triangle, base plate and 2 stays."""
    base = base or P.lower_b
    d = _cult_shift(base)
    ty = (TP.imp_tb_y[0] + P.cult_dy, TP.imp_tb_y[1] + P.cult_dy)
    zb = TP.lower_b[1]
    tz = (zb - TP.imp_tb / 2.0, zb + TP.imp_tb / 2.0)
    parts = [tube_span((-TP.imp_tb_x, TP.imp_tb_x), ty, tz, 4.0, "x")]
    zw = TP.wheel_d / 2.0
    wy = TP.wheel_y + P.cult_dy
    for sx in (-1, 1):
        g0, g1 = sorted((sx * TP.gauge_arm_x[0], sx * TP.gauge_arm_x[1]))
        armp = ((ty[1] - 5.0, tz[1]), (ty[0], tz[1]), (wy - 25.0, zw + 25.0), (wy - 25.0, zw - 25.0),
                (wy + 25.0, zw - 25.0), (ty[1] - 5.0, tz[0]))
        parts.append(plate_yz(armp, g0, g1 - g0))
    s = fuse_all(parts).cut(cyl(20.5, (-700, wy, zw), (700, wy, zw)))
    s.translate(V(0, d.y - P.cult_dy, d.z))
    # female triangle + base plate on the toolbar + stays from the hook to the back of the toolbar
    fem = female(base)
    ty = (ty[0] + d.y - P.cult_dy, ty[1] + d.y - P.cult_dy)
    top = tz[1] + d.z
    w_back = P.cp_tube / 2.0 + P.cf_gap
    y_front = P.cp_point(base, (P.cf_lock_v[0], w_back))[0]
    plate = box_span((-P.cf_lock_u - 40.0, P.cf_lock_u + 40.0), (ty[0], y_front), (top, top + P.imp_base_t))
    stays = []
    hy, hz = P.cp_point(base, (P.cp_top_v[1] - 10.0, w_back + P.cf_t + P.imp_stay[1] / 2.0))
    for sx in (-1, 1):
        stays.append(rect_tube((sx * 50.0, hy, hz), (sx * 150.0, ty[0] + 15.0, top + P.imp_base_t - 2.0),
                               P.imp_stay[1], P.imp_stay[0], up=(1.0, 0.0, 0.0)))
    return fuse_all([s, fem, plate] + stays)


def _shifted(shape, base):
    s = shape.copy()
    s.translate(_cult_shift(base))
    return s


def cult_tines(base=None):
    return _shifted(TG.tines(), base or P.lower_b)


def cult_clamps(base=None):
    return _shifted(TG.tine_clamps(), base or P.lower_b)


def cult_shares(base=None):
    return _shifted(TG.shares(), base or P.lower_b)


def cult_wheels(base=None):
    return _shifted(TG.gauge_wheels(), base or P.lower_b)


def cult_axles(base=None):
    return _shifted(TG.wheel_axles(), base or P.lower_b)


def cult_wheel_centre(base=None):
    """(y, z) of the gauge wheel axle in the work pose."""
    d = _cult_shift(base or P.lower_b)
    return TP.wheel_y + d.y, TP.wheel_d / 2.0 + d.z


def cult_share_points(base=None):
    """(x, y, z) of the share tips in the work pose."""
    d = _cult_shift(base or P.lower_b)
    yt, _ = TP.tine_pts[-1]
    return [(x, yt + d.y, -TP.work_depth + d.z) for x in TP.tine_x]
