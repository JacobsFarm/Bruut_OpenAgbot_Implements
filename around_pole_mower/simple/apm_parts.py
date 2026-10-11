"""Parts of the around-pole fence mower (simple). One function per part, returns a Part shape in robot coordinates
(arm parts at the rest position psi_rest). Arm parts are drawn in the arm frame (u, v, z: origin on the pivot axis
at the ground, u along the arm) and placed with to_world()."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import apm_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

AF = {6: 10.0, 8: 13.0, 10: 17.0, 12: 19.0, 16: 24.0}
NUT_M = {6: 5.2, 8: 6.8, 10: 8.4, 12: 10.8, 16: 13.0}
HEAD_K = {6: 4.0, 8: 5.3, 10: 6.4, 12: 7.5, 16: 10.0}

PX, PY = P.pivot
ZB0 = P.base_z0                                 # 124: bottom of the arm base plate
ZB1 = P.base_z0 + P.base_t                      # 130
ZR1 = ZB1 + P.rib_h                             # 180: top of the ribs
VI = P.arm_w / 2.0 - P.rib_t                    # 74: inner face of the ribs
R_POST_TUBE = P.post_d / 2.0
R_SLEEVE = P.sleeve_d / 2.0


# ---------------------------------------------------------------------
# Basic functions (same style as dbr_parts.py)
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
    if axis == "y":
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1], p0[2] + r * math.sin(math.radians(60 * i)))
               for i in range(6)]
        d = V(0, length, 0)
    else:
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1] + r * math.sin(math.radians(60 * i)), p0[2])
               for i in range(6)]
        d = V(0, 0, length)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(d)


def hex_z(af, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return _hex(af, (x, y, z0), "z", z1 - z0)


def hex_y(af, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return _hex(af, (x, y0, z), "y", y1 - y0)


def bar_z(p0, p1, w, z0, z1):
    """Flat bar from (x, y) p0 to p1, width w, between z0 and z1 (square ends)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    b = Part.makeBox(length, w, z1 - z0, V(0, -w / 2.0, z0))
    b.rotate(V(0, 0, 0), Z, math.degrees(math.atan2(dy, dx)))
    b.translate(V(p0[0], p0[1], 0))
    return b


# ---------------------------------------------------------------------
# Arm frame
# ---------------------------------------------------------------------
def arm_placement(psi=None):
    psi = P.psi_rest if psi is None else psi
    return App.Placement(V(PX, PY, 0), App.Rotation(Z, -psi))


def to_world(shapes, psi=None):
    """Arm frame -> robot coordinates (rest position). Accepts a shape or a list."""
    m = arm_placement(psi).toMatrix()
    if isinstance(shapes, (list, tuple)):
        return [to_world(s, psi) for s in shapes]
    s = shapes.copy()
    s.transformShape(m)
    return s


def wp(u, v=0.0):
    """World (x, y) of an arm-frame point at rest."""
    return P.arm_point(u, v)


def hull_face(u1, r1, u2, r2, z):
    """Convex hull of two circles on the u axis (arm frame), as a face at height z (belt outline)."""
    d = u2 - u1
    th = math.acos((r1 - r2) / d)
    n = lambda a: (math.cos(a), math.sin(a))
    a1, b1 = n(th), n(-th)
    p1a = V(u1 + r1 * a1[0], r1 * a1[1], z)
    p1b = V(u1 + r1 * b1[0], r1 * b1[1], z)
    p2a = V(u2 + r2 * a1[0], r2 * a1[1], z)
    p2b = V(u2 + r2 * b1[0], r2 * b1[1], z)
    arc1 = Part.Arc(p1a, V(u1 - r1, 0, z), p1b).toShape()
    arc2 = Part.Arc(p2b, V(u2 + r2, 0, z), p2a).toShape()
    wire = Part.Wire([arc1, Part.LineSegment(p1b, p2b).toShape(), arc2, Part.LineSegment(p2a, p1a).toShape()])
    return Part.Face(wire)


# ---------------------------------------------------------------------
# Mount: hanger, webs, post, stop plate (fixed to the robot)
# ---------------------------------------------------------------------
Z_PLATE = P.robot_lower_beam_z[0] - P.hanger_t          # 609


def hanger_bolt_xy():
    return [(x, y) for x in P.hanger_bolt_x for y in P.robot_rear_beam_y]


def hanger_plate():
    b = box_span(P.hanger_x, P.hanger_y, (Z_PLATE, P.robot_lower_beam_z[0]))
    return b.cut([cyl_z(P.m10_hole, Z_PLATE - 1, Z_PLATE + 20, x, y) for x, y in hanger_bolt_xy()])


def hanger_bolts():
    """M10 8.8 x 70 from the top through the lower beam and the plate, nut under the plate."""
    out = []
    z_top = P.robot_lower_beam_z[1]
    for (x, y) in hanger_bolt_xy():
        out.append(hex_z(AF[10], z_top, z_top + HEAD_K[10], x, y))
        out.append(cyl_z(10.0, Z_PLATE - NUT_M[10] - 3.0, z_top, x, y))
        out.append(hex_z(AF[10], Z_PLATE - NUT_M[10], Z_PLATE, x, y))
    return out


def webs():
    pts = [(P.web_front_y, Z_PLATE), (PY, Z_PLATE), (PY, P.web_post_z), (P.web_front_y, P.web_low_z)]
    return [poly_yz(pts, PX + R_POST_TUBE, P.web_t), poly_yz(pts, PX - R_POST_TUBE - P.web_t, P.web_t)]


def post():
    return tube_z(P.post_d, P.post_d - 2 * P.post_wall, P.post_z[0], P.post_z[1], PX, PY)


def post_cap():
    return cyl_z(P.post_d, P.post_z[1], P.post_z[1] + 5.0, PX, PY)


def end_plate():
    z1 = P.post_z[0]
    plug = cyl_z(P.post_d - 2 * P.post_wall, z1, z1 + 25.0, PX, PY)       # welded plug with an M12 thread
    plate = cyl_z(P.end_plate_d, z1 - P.end_plate_t, z1, PX, PY)
    return [s.cut(cyl_z(12.0, z1 - 20.0, z1 + 30.0, PX, PY)) for s in (plate, plug)]


def end_bolt():
    z0 = P.post_z[0] - P.end_plate_t
    return [hex_z(AF[12], z0 - HEAD_K[12], z0, PX, PY), cyl_z(12.0, z0, z0 + 30.0, PX, PY)]


def thrust_washer():
    z0 = P.post_z[0]
    return tube_z(P.end_plate_d - 10.0, P.post_d + 0.5, z0, z0 + P.thrust_t, PX, PY)


def collar():
    return tube_z(P.collar_d, P.post_d, P.collar_z[0], P.collar_z[1], PX, PY)


def stop_points():
    """World (x, y) of the rest stop bolt and the max stop bolt."""
    out = []
    for a in P.stop_angles():
        r = math.radians(a)
        out.append((PX + P.stop_r * math.cos(r), PY + P.stop_r * math.sin(r)))
    return out


def stop_plate():
    z0, z1 = P.stop_plate_z
    ax, ay = P.anchor_point()
    parts = [cyl_z(110.0, z0, z1, PX, PY), bar_z((PX, PY), (ax, ay), 40.0, z0, z1), cyl_z(44.0, z0, z1, ax, ay)]
    for (x, y) in stop_points():
        parts.append(cyl_z(36.0, z0, z1, x, y))
    plate = fuse_all(parts)
    holes = [cyl_z(P.post_d, z0 - 1, z1 + 1, PX, PY), cyl_z(P.anchor_bolt_d + 0.5, z0 - 1, z1 + 1, ax, ay)]
    holes += [cyl_z(P.stop_bolt_d + 0.5, z0 - 1, z1 + 1, x, y) for (x, y) in stop_points()]
    return plate.cut(holes)


def stop_bolts():
    """M12 set screws with a lock nut on top: the rest stop sets psi_rest, the max stop psi_max."""
    out = []
    z0, z1 = P.stop_bolt_z
    zt = P.stop_plate_z[1]
    for (x, y) in stop_points():
        out += [cyl_z(P.stop_bolt_d, z0, z1, x, y), hex_z(AF[12], zt, zt + NUT_M[12], x, y),
                hex_z(AF[12], z1, z1 + HEAD_K[12], x, y)]
    return out


def anchor_bolt():
    """Eye bolt M10 hanging from the stop plate (spring hook at spring_z), 2 nuts: preload adjustment."""
    ax, ay = P.anchor_point()
    zp0, zp1 = P.stop_plate_z
    zs = P.spring_z
    rod = cyl_z(P.anchor_bolt_d, zs + 8.0, zp1 + 25.0, ax, ay)
    eye = Part.makeTorus(9.0, 3.5, V(ax, ay, zs), Y)
    nuts = [hex_z(AF[10], zp1, zp1 + NUT_M[10], ax, ay), hex_z(AF[10], zp0 - NUT_M[10], zp0, ax, ay)]
    return [rod, eye] + nuts


def _lever_exit(tip, direction, psi):
    """Distance from the lever hole to the outline of the lever plate along 'direction' (unit, world)."""
    la = math.radians(P.lever_angle(psi))
    da = direction[0] * math.cos(la) + direction[1] * math.sin(la)
    db = -direction[0] * math.sin(la) + direction[1] * math.cos(la)
    ts = []
    if da > 1e-6:
        ts.append((P.lever_r - P.lever_hole_r) / da)
    if abs(db) > 1e-6:
        ts.append((P.lever_w / 2.0) / abs(db))
    return min(ts)


def spring_shape(psi=None):
    """Extension spring from the lever hole to the eye bolt (straight hooks, coils as rings)."""
    psi = P.psi_rest if psi is None else psi
    tx, ty = P.lever_tip(psi)
    ax, ay = P.anchor_point()
    length = math.hypot(ax - tx, ay - ty)
    d = ((ax - tx) / length, (ay - ty) / length)
    zs = P.spring_z
    s0 = _lever_exit((tx, ty), d, psi) + 4.0
    s1 = length - 13.0
    h = P.spring_hook
    pa = V(tx + d[0] * s0, ty + d[1] * s0, zs)
    pb = V(tx + d[0] * (s0 + h), ty + d[1] * (s0 + h), zs)
    pc = V(tx + d[0] * (s1 - h), ty + d[1] * (s1 - h), zs)
    pe = V(tx + d[0] * s1, ty + d[1] * s1, zs)
    out = [Part.makeCylinder(P.spring_wire / 2.0, (pb - pa).Length, pa, V(d[0], d[1], 0)),
           Part.makeCylinder(P.spring_wire / 2.0, (pe - pc).Length, pc, V(d[0], d[1], 0))]
    body = (pc - pb).Length
    n = max(4, int(body / (P.spring_wire * 1.6)))
    rm = (P.spring_od - P.spring_wire) / 2.0
    for i in range(n):
        c = pb + V(d[0], d[1], 0) * (P.spring_wire / 2.0 + i * (body - P.spring_wire) / (n - 1))
        out.append(Part.makeTorus(rm, P.spring_wire / 2.0, c, V(d[0], d[1], 0)))
    return out


# ---------------------------------------------------------------------
# Swing: sleeve, bushes, clevis, lever, hinge bolt (turns about the post)
# ---------------------------------------------------------------------
def sleeve():
    return tube_z(P.sleeve_d, P.sleeve_d - 2 * P.sleeve_wall, P.sleeve_z[0], P.sleeve_z[1], PX, PY)


def bushes():
    idia = P.post_d + 0.2
    od = P.sleeve_d - 2 * P.sleeve_wall
    z0, z1 = P.sleeve_z
    return [tube_z(od, idia, z0 + 2.0, z0 + 2.0 + P.bush_len, PX, PY),
            tube_z(od, idia, z1 - 2.0 - P.bush_len, z1 - 2.0, PX, PY)]


def _sleeve_cut():
    return cyl_z(P.sleeve_d + 0.1, P.sleeve_z[0] - 10, P.sleeve_z[1] + 10, 0, 0)


def clevis():
    """Back plate perpendicular to the arm (welded to the sleeve) + 2 lugs outside the ribs, hinge hole 17."""
    z = P.clevis_z
    w = P.clevis_w / 2.0
    vi = P.arm_w / 2.0 + 1.0
    back = box_span(P.clevis_u, (-w, w), z)
    lugs = [box_span((P.clevis_u[0], P.lug_u1), (vi, vi + P.lug_t), z),
            box_span((P.clevis_u[0], P.lug_u1), (-vi - P.lug_t, -vi), z)]
    zt = ZR1 + P.motor_plate_t + P.float_stop_gap               # above the motor plate
    zb = ZB0 - P.float_stop_gap                                 # under the base plate
    vs = (-vi - P.lug_t, vi + P.lug_t)
    bars = [box_span(P.float_stop_u, vs, (zb - 8.0, zb)), box_span(P.float_stop_u, vs, (zt, zt + 8.0))]
    s = fuse_all([back] + lugs + bars).cut(_sleeve_cut())
    s = s.cut(cyl_y(P.hinge_bolt_d + 1.0, -w - 20, w + 20, P.hinge_u, P.hinge_z))
    return to_world(s)


def lever():
    z0, z1 = P.lever_z
    b = box_span((0.0, P.lever_r), (-P.lever_w / 2.0, P.lever_w / 2.0), (z0, z1))
    b = b.cut(cyl_z(12.0, z0 - 1, z1 + 1, P.lever_hole_r, 0.0))
    b.rotate(V(0, 0, 0), Z, P.lever_offset)
    return to_world(b.cut(_sleeve_cut()))


def hinge_bolt():
    vi = P.arm_w / 2.0 + 1.0 + P.lug_t
    u, z = P.hinge_u, P.hinge_z
    parts = [cyl_y(P.hinge_bolt_d, -vi, vi, u, z), hex_y(AF[16], vi, vi + HEAD_K[16], u, z),
             hex_y(AF[16], -vi - NUT_M[16], -vi, u, z)]
    return to_world(parts)


# ---------------------------------------------------------------------
# Arm: base plate, ribs, cover, motor, belt, spindle, guard, skid (floats about the hinge)
# ---------------------------------------------------------------------


def base_plate():
    w = P.arm_w / 2.0
    body = box_span(P.base_u, (-w, w), (ZB0, ZB1))
    tab = box_span((P.skid_u - P.skid_tab_w / 2.0, P.skid_u + P.skid_tab_w / 2.0), (P.skid_v - 8.0, -w + 1.0),
                   (ZB0, ZB1))
    s = fuse_all([body, tab])
    holes = [cyl_z(P.spindle_housing_d + 0.5, ZB0 - 1, ZB1 + 1, P.arm_L, 0.0)]
    holes += [cyl_z(8.5, ZB0 - 1, ZB1 + 1, x, y) for (x, y) in spindle_bolt_uv()]
    return to_world(s.cut(holes))


def ribs():
    out = []
    for s in (1, -1):
        v = (VI, P.arm_w / 2.0) if s > 0 else (-P.arm_w / 2.0, -VI)
        b = box_span((P.hinge_u, P.base_u[1] - P.rib_t), v, (ZB1, ZR1))
        r = cyl_y(P.rib_h, v[0], v[1], P.hinge_u, P.hinge_z)
        b = fuse_all([b, r]).cut(cyl_y(P.hinge_bolt_d + 1.0, v[0] - 1, v[1] + 1, P.hinge_u, P.hinge_z))
        out.append(b)
    out.append(box_span((P.base_u[1] - P.rib_t, P.base_u[1]), (-P.arm_w / 2.0, P.arm_w / 2.0), (ZB1, ZR1)))
    return to_world(out)


def motor_plate_u():
    return (P.motor_u - P.motor_plate_len / 2.0, P.motor_u + P.motor_plate_len / 2.0)


def cover():
    u0 = motor_plate_u()[1]
    return to_world(box_span((u0, P.base_u[1]), (-P.arm_w / 2.0, P.arm_w / 2.0), (ZR1, ZR1 + P.cover_t)))


def motor_plate():
    b = box_span(motor_plate_u(), (-P.arm_w / 2.0, P.arm_w / 2.0), (ZR1, ZR1 + P.motor_plate_t))
    return to_world(b.cut(cyl_z(40.0, ZR1 - 1, ZR1 + 20, P.motor_u, 0.0)))


def motor():
    """48 V BLDC 750 W, square flange 90, body O90 x 140, terminal box on the side (dimensions estimated)."""
    z0 = ZR1 + P.motor_plate_t
    f = P.motor_flange / 2.0
    u = P.motor_u
    flange = box_span((u - f, u + f), (-f, f), (z0, z0 + P.motor_flange_t))
    body = cyl_z(P.motor_d, z0 + P.motor_flange_t, z0 + P.motor_flange_t + P.motor_len, u, 0.0)
    tbox = box_span((u - 25.0, u + 25.0), (-P.motor_d / 2.0 - 30.0, -P.motor_d / 2.0 + 5.0),
                    (z0 + 60.0, z0 + 100.0))
    return to_world(fuse_all([flange, body, tbox]))


def motor_shaft():
    z1 = ZR1 + P.motor_plate_t
    return to_world(cyl_z(P.motor_shaft_d, P.pulley_z0 + P.pulley_w, z1, P.motor_u, 0.0))


def _pulley(u, d_pitch, bore):
    z0 = P.pulley_z0
    z1 = z0 + P.pulley_w
    core = cyl_z(d_pitch - 8.0, z0, z1, u, 0.0)
    fl = [cyl_z(d_pitch + 10.0, z0, z0 + 4.0, u, 0.0), cyl_z(d_pitch + 10.0, z1 - 4.0, z1, u, 0.0)]
    return fuse_all([core] + fl).cut(cyl_z(bore, z0 - 1, z1 + 1, u, 0.0))


def motor_pulley():
    return to_world(_pulley(P.motor_u, P.pulley_motor_d, 1.0))


def belt():
    zc = P.pulley_z0 + P.pulley_w / 2.0 - P.belt_w / 2.0
    r1, r2 = P.pulley_motor_d / 2.0, P.pulley_spindle_d / 2.0
    t = P.belt_t / 2.0
    outer = hull_face(P.motor_u, r1 + t, P.arm_L, r2 + t, zc).extrude(V(0, 0, P.belt_w))
    inner = hull_face(P.motor_u, r1 - t, P.arm_L, r2 - t, zc - 1).extrude(V(0, 0, P.belt_w + 2))
    return to_world(outer.cut(inner))


def spindle_bolt_uv():
    r = P.spindle_bolt_pcd / 2.0
    return [(P.arm_L + r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in (30.0, 150.0, 270.0)]


def spindle_housing():
    """Bought deck spindle: housing O62 through the base plate, flange O130 on top, bore for the shaft."""
    z_bot = P.cut_h + P.disc_t + P.boss_h        # 79
    zf = ZB1 + P.spindle_flange_t
    h = cyl_z(P.spindle_housing_d, z_bot, ZB1, P.arm_L, 0.0)
    f = cyl_z(P.spindle_flange_d, ZB1, zf, P.arm_L, 0.0)
    top = cyl_z(40.0, zf, P.pulley_z0 - 1.0, P.arm_L, 0.0)
    s = fuse_all([h, f, top]).cut(cyl_z(P.spindle_shaft_d + 0.5, z_bot - 1, P.pulley_z0, P.arm_L, 0.0))
    s = s.cut([cyl_z(8.5, ZB1 - 1, zf + 1, x, y) for (x, y) in spindle_bolt_uv()])
    return to_world(s)


def spindle_bolts():
    """3 x M8 through flange, base plate and guard cover: they also clamp the guard."""
    zf = ZB1 + P.spindle_flange_t
    zc = ZB0 - P.guard_cover_t
    out = []
    for (x, y) in spindle_bolt_uv():
        out += [hex_z(AF[8], zf, zf + HEAD_K[8], x, y), cyl_z(8.0, zc - NUT_M[8] - 2.0, zf, x, y),
                hex_z(AF[8], zc - NUT_M[8], zc, x, y)]
    return to_world(out)


def guard_cover():
    z1 = ZB0
    z0 = z1 - P.guard_cover_t
    c = cyl_z(P.guard_d, z0, z1, P.arm_L, 0.0).cut(cyl_z(P.spindle_housing_d + 2.0, z0 - 1, z1 + 1, P.arm_L, 0.0))
    return to_world(c.cut([cyl_z(8.5, z0 - 1, z1 + 1, x, y) for (x, y) in spindle_bolt_uv()]))


def guard_ring():
    return to_world(tube_z(P.guard_d, P.guard_d - 2 * P.guard_wall, P.guard_z[0], P.guard_z[1], P.arm_L, 0.0))


def skid_leg():
    """Flat bar 8 x 50 under the tab (slotted: cut height), foot plate for the puck."""
    zf = P.skid_h
    u0, u1 = P.skid_u - P.skid_leg_w / 2.0, P.skid_u + P.skid_leg_w / 2.0
    leg = box_span((u0, u1), (P.skid_v - 4.0, P.skid_v + 4.0), (zf + 8.0, ZB0))
    foot = box_span((P.skid_u - 35.0, P.skid_u + 35.0), (P.skid_v - 35.0, P.skid_v + 35.0), (zf, zf + 8.0))
    return to_world(fuse_all([leg, foot]))


def skid():
    return to_world(cyl_z(P.skid_d, 0.0, P.skid_h, P.skid_u, P.skid_v))


# ---------------------------------------------------------------------
# Rotor: shaft, pulley, boss, disc, clamps, strings (turns with the spindle)
# ---------------------------------------------------------------------
def spindle_shaft():
    z0 = P.cut_h + P.disc_t + P.boss_h
    return to_world(cyl_z(P.spindle_shaft_d, z0, P.pulley_z0, P.arm_L, 0.0))


def spindle_pulley():
    zt = P.pulley_z0 + P.pulley_w
    p = _pulley(P.arm_L, P.pulley_spindle_d, 1.0)
    nut = hex_z(AF[16], zt, zt + 8.0, P.arm_L, 0.0)                    # M16 jam nut
    return to_world(fuse_all([p, nut]))


def boss():
    z0 = P.cut_h + P.disc_t
    return to_world(cyl_z(P.boss_d, z0, z0 + P.boss_h, P.arm_L, 0.0))


def disc():
    return to_world(cyl_z(P.disc_d, P.cut_h, P.cut_h + P.disc_t, P.arm_L, 0.0))


def _radial(shape, i):
    shape.rotate(V(P.arm_L, 0, 0), Z, 360.0 / P.n_strings * i + 45.0)
    return shape


def clamps():
    z0 = P.cut_h + P.disc_t
    L, W, H = P.clamp
    out = []
    for i in range(P.n_strings):
        b = box_span((P.arm_L + P.clamp_r - L / 2.0, P.arm_L + P.clamp_r + L / 2.0), (-W / 2.0, W / 2.0),
                     (z0, z0 + H))
        heads = [hex_z(AF[6], z0 + H, z0 + H + HEAD_K[6], P.arm_L + P.clamp_r + s * 10.0, 0.0) for s in (-1, 1)]
        out.append(_radial(fuse_all([b] + heads), i))
    return to_world(out)


def strings():
    z = P.cut_h + P.disc_t + P.string_d / 2.0
    r0 = P.clamp_r + P.clamp[0] / 2.0
    out = [_radial(cyl_x(P.string_d, P.arm_L + r0, P.arm_L + P.string_r[1], 0.0, z), i) for i in range(P.n_strings)]
    return to_world(out)


# ---------------------------------------------------------------------
# Controller box on the rear lower beams
# ---------------------------------------------------------------------
BOX_BOLT_X = (-225.0, -125.0)


def box_base():
    z0 = P.robot_lower_beam_z[1]
    b = box_span(P.box_base_x, P.box_base_y, (z0, z0 + P.box_base_t))
    return b.cut([cyl_z(8.4, z0 - 1, z0 + 5, x, y) for x in BOX_BOLT_X for y in P.robot_rear_beam_y])


def controller_box():
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    b = box_span(P.box_x, P.box_y, (z0, z0 + P.box_h))
    lid = box_span((P.box_x[0] - 3, P.box_x[1] + 3), (P.box_y[0] - 3, P.box_y[1] + 3), (z0 + P.box_h, z0 + P.box_h + 12))
    glands = [cyl_y(20.0, P.box_y[0] - 18.0, P.box_y[0], x, z0 + 30.0) for x in (P.box_x[0] + 35.0, P.box_x[1] - 35.0)]
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
# Fence (renders, animation)
# ---------------------------------------------------------------------
def fence_post(y):
    r = P.fence_post_d / 2.0
    body = cyl_z(P.fence_post_d, -300.0, P.fence_post_h - 30.0, P.POST_X, y)
    top = Part.makeCone(r, r * 0.35, 30.0, V(P.POST_X, y, P.fence_post_h - 30.0), Z)
    return fuse_all([body, top])


def insulators(y):
    """Ring insulators on the inside of the post (towards the robot), one per wire."""
    out = []
    for z in P.wire_z:
        out.append(cyl_x(8.0, P.WIRE_X + 14.0, P.POST_X - P.fence_post_d / 2.0 + 5.0, y, z))
        out.append(Part.makeTorus(10.0, 4.0, V(P.WIRE_X, y, z), Y))
    return out


def wires(y0, y1):
    return [cyl_y(P.wire_d, y0, y1, P.WIRE_X, z) for z in P.wire_z]
