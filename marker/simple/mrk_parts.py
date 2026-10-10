import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrk_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

# ---------------------------------------------------------------------
# Reference pose: every shape is drawn in robot coordinates with the nozzle at (0, y_tool_nom) and the
# Z carriage parked. The slides (App::Part in build_mrk) move the parts from there.
# ---------------------------------------------------------------------
REF = {"x": 0.0, "y": P.y_tool_nom, "zc": P.ZC_PARK, "lift": 0.0}
XC = P.xc_mid + REF["x"]        # X carriage centre
X0 = XC - P.xy_plate_dx         # -x face of the Y plate
XT, YT, ZC = REF["x"], REF["y"], REF["zc"]


def xr(dx):
    return X0 + dx


# ---------------------------------------------------------------------
# Basic shapes (same style as dbr_parts.py)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_y(d, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def tube_z(od, wall, z0, z1, x, y):
    return cyl_z(od, z0, z1, x, y).cut(cyl_z(od - 2 * wall, z0 - 1, z1 + 1, x, y))


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


def _poly(pts):
    pts = list(pts)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


def poly_yz(points, x0, t):
    """Closed polygon in the y-z plane, (y, z) world, extruded over +x from x0."""
    return _poly([V(x0, y, z) for (y, z) in points]).extrude(V(t, 0, 0))


def poly_xz(points, y0, t):
    """Closed polygon in the x-z plane, (x, z) world, extruded over +y from y0."""
    return _poly([V(x, y0, z) for (x, z) in points]).extrude(V(0, t, 0))


def poly_xy(points, z0, t):
    """Closed polygon in the x-y plane, (x, y) world, extruded over +z from z0."""
    return _poly([V(x, y, z0) for (x, y) in points]).extrude(V(0, 0, t))


def _hex(af, p0, axis, length):
    r = af / math.sqrt(3.0)
    if axis == "x":
        pts = [V(p0[0], p0[1] + r * math.cos(math.radians(60 * i + 30)), p0[2] + r * math.sin(math.radians(60 * i + 30)))
               for i in range(6)]
        d = V(length, 0, 0)
    elif axis == "y":
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1], p0[2] + r * math.sin(math.radians(60 * i)))
               for i in range(6)]
        d = V(0, length, 0)
    else:
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1] + r * math.sin(math.radians(60 * i)), p0[2])
               for i in range(6)]
        d = V(0, 0, length)
    return _poly(pts).extrude(d)


def hex_x(af, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return _hex(af, (x0, y, z), "x", x1 - x0)


def hex_y(af, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return _hex(af, (x, y0, z), "y", y1 - y0)


def hex_z(af, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return _hex(af, (x, y, z0), "z", z1 - z0)


AF = {6: 10.0, 8: 13.0, 10: 17.0, 12: 17.0}
NUT_M = {6: 5.2, 8: 6.8, 10: 8.4, 12: 4.0}
HEAD_K = {6: 4.0, 8: 5.3, 10: 6.4}


def frame(shape, origin, u, v, w):
    """Shape drawn in a local frame (local x = u, y = v, z = w) placed in the world. u x v must be w."""
    m = App.Matrix(u.x, v.x, w.x, origin.x,
                   u.y, v.y, w.y, origin.y,
                   u.z, v.z, w.z, origin.z,
                   0.0, 0.0, 0.0, 1.0)
    s = shape.copy()
    s.transformShape(m)
    return s


# ---------------------------------------------------------------------
# Linear modules (bought). Local frame: u along the travel, v across (width), w from the base (w = 0) to the
# carriage. Body u 0..L, v +-W/2, w 0..H; carriage on top at u = uc.
# ---------------------------------------------------------------------
def module_body(L, W, H, end, base_slots=()):
    body = box_span((0.0, L), (-W / 2.0, W / 2.0), (0.0, H))
    cuts = [box_span((end, L - end), (-W / 2.0 + 12.0, W / 2.0 - 12.0), (H - 1.5, H + 1.0))]     # cover strip
    for s in (-1, 1):                                                                              # side T-slots
        cuts.append(box_span((-1.0, L + 1.0), (s * (W / 2.0 - 4.0), s * (W / 2.0 + 1.0)), (H / 2.0 - 4.0, H / 2.0 + 4.0)))
    for v in base_slots:                                                                           # T-slots in the base
        cuts.append(box_span((-1.0, L + 1.0), (v - 4.0, v + 4.0), (-1.0, 6.0)))
    return body.cut(cuts)


def module_carriage(uc, length, W, H, gap, t):
    car = box_span((uc - length / 2.0, uc + length / 2.0), (-W / 2.0, W / 2.0), (H + gap, H + gap + t))
    holes = [cyl_z(5.0, H + gap + t - 8.0, H + gap + t + 1.0, uc + du, dv)
             for du in (-length / 2.0 + 15.0, length / 2.0 - 15.0) for dv in (-W / 2.0 + 12.0, W / 2.0 - 12.0)]
    return car.cut(holes)


def motor_inline(L):
    """NEMA 23 in line behind the end u = L: coupling housing + motor (with encoder). w 0..57 (flush with the base)."""
    n = P.nema
    housing = box_span((L, L + P.coupler_len), (-n / 2.0 + 4.0, n / 2.0 - 4.0), (4.0, n - 4.0))
    motor = box_span((L + P.coupler_len, L + P.coupler_len + P.nema_len), (-n / 2.0, n / 2.0), (0.0, n))
    gland = cyl_x(12.0, L + P.coupler_len + P.nema_len, L + P.coupler_len + P.nema_len + 10.0, 0.0, n / 2.0)
    return fuse_all([housing, motor, gland])


# X module: u = +x, v = +z, w = -y (base at the front)
XM_O = V(P.xm_x[0], P.xm_base_y, (P.xm_z[0] + P.xm_z[1]) / 2.0)
XM_UVW = (X, Z, V(0, -1, 0))


def x_module():
    slots = [z - XM_O.z for z in P.xm_slot_z]
    return frame(module_body(P.xm_len, P.xm_w, P.xm_h, P.xm_end[0], slots), XM_O, *XM_UVW)


def x_carriage():
    uc = XC - P.xm_x[0]
    return frame(module_carriage(uc, P.xm_car_len, P.xm_w, P.xm_h, P.xm_gap, P.xm_car_t), XM_O, *XM_UVW)


def x_motor():
    """Motor standing up on the drive end (-x): housing with the coupling to the pulley shaft, then the motor."""
    n = P.nema
    uc = P.xm_end[0] / 2.0
    w0, w1 = 0.0, n
    z0 = P.xm_w / 2.0
    housing = box_span((uc - n / 2.0 + 4.0, uc + n / 2.0 - 4.0), (z0, z0 + P.coupler_len), (w0 + 4.0, w1 - 4.0))
    motor = box_span((uc - n / 2.0, uc + n / 2.0), (z0 + P.coupler_len, z0 + P.coupler_len + P.nema_len), (w0, w1))
    return frame(fuse_all([housing, motor]), XM_O, *XM_UVW)


# Y module: u = -y (front end first), v = -z, w = +x (base against the Y plate)
YM_O = V(xr(P.ym_x[0]), P.ym_y[0], (P.ym_z[0] + P.ym_z[1]) / 2.0)
YM_UVW = (V(0, -1, 0), V(0, 0, -1), X)


def y_module():
    return frame(module_body(P.ym_len, P.sm_w, P.sm_h, P.sm_end), YM_O, *YM_UVW)


def y_carriage():
    uc = P.ym_y[0] - YT
    return frame(module_carriage(uc, P.sm_car_len, P.sm_w, P.sm_h, P.sm_gap, P.sm_car_t), YM_O, *YM_UVW)


def y_motor():
    return frame(motor_inline(P.ym_len), YM_O, *YM_UVW)


# Z module: u = +z, v = -y, w = +x (base against the Z adapter)
def _zm_origin():
    return V(xr(P.zm_x[0]), YT, P.zm_z[0])


ZM_UVW = (Z, V(0, -1, 0), X)


def z_module():
    return frame(module_body(P.zm_len, P.sm_w, P.sm_h, P.sm_end), _zm_origin(), *ZM_UVW)


def z_carriage():
    uc = ZC - P.zm_z[0]
    return frame(module_carriage(uc, P.sm_car_len, P.sm_w, P.sm_h, P.sm_gap, P.sm_car_t), _zm_origin(), *ZM_UVW)


def z_motor():
    return frame(motor_inline(P.zm_len), _zm_origin(), *ZM_UVW)


# ---------------------------------------------------------------------
# Hangers (2x identical, sx = -1 / +1) and control box
# ---------------------------------------------------------------------
def hanger_bolt_xy(sx):
    xc = sx * P.hanger_x
    return [(xc + dx, y) for dx in (-P.hanger_bolt_dx, P.hanger_bolt_dx) for y in P.robot_rear_beam_y]


def hanger_flange_bolt_xz(sx):
    xc = sx * P.hanger_x
    return [(xc + dx, z) for dx in (-P.hanger_bolt_dx, P.hanger_bolt_dx) for z in P.xm_slot_z]


def hanger(sx):
    """Top plate 10 mm + web 8 mm + flange 8 mm, laser cut with tabs, welded."""
    xc = sx * P.hanger_x
    w = P.hanger_w / 2.0
    z1 = P.robot_lower_beam_z[0]
    top = box_span((xc - w, xc + w), P.hanger_top_y, (z1 - P.hanger_top_t, z1))
    top = top.cut([cyl_z(P.m10_hole, z1 - 20, z1 + 1, x, y) for (x, y) in hanger_bolt_xy(sx)])
    web = poly_yz(P.web_pts, xc - P.web_t / 2.0, P.web_t)
    y0 = P.xm_base_y
    flange = box_span((xc - w, xc + w), (y0, y0 + P.flange_t), (P.xm_z[0], z1 - P.hanger_top_t))
    flange = flange.cut([cyl_y(P.m8_hole, y0 - 1, y0 + P.flange_t + 1, x, z) for (x, z) in hanger_flange_bolt_xz(sx)])
    return fuse_all([top, web, flange])


def hanger_bolts(sx):
    """M10 x 60 from the top through the lower beam and the top plate, nut under the plate;
    M8 x 20 through the flange into T-slot nuts in the base of the X module."""
    out = []
    z_top = P.robot_lower_beam_z[1]
    z_plate = P.robot_lower_beam_z[0] - P.hanger_top_t
    for (x, y) in hanger_bolt_xy(sx):
        out.append(hex_z(AF[10], z_top, z_top + HEAD_K[10], x, y))
        out.append(cyl_z(10.0, z_plate - NUT_M[10] - 3.0, z_top, x, y))
        out.append(hex_z(AF[10], z_plate - NUT_M[10], z_plate, x, y))
    y1 = P.xm_base_y + P.flange_t
    for (x, z) in hanger_flange_bolt_xz(sx):
        out.append(hex_y(AF[8], y1, y1 + HEAD_K[8], x, z))
        out.append(cyl_y(8.0, P.xm_base_y - 6.0, y1, x, z))
    return out


def box_base():
    z0 = P.robot_lower_beam_z[1]
    b = box_span(P.box_base_x, P.box_base_y, (z0, z0 + P.box_base_t))
    return b.cut([cyl_z(8.4, z0 - 1, z0 + 5, x, y) for x in (-125.0, 125.0) for y in P.robot_rear_beam_y])


def control_box():
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    b = box_span(P.box_x, P.box_y, (z0, z0 + P.box_h))
    lid = box_span((P.box_x[0] - 3, P.box_x[1] + 3), (P.box_y[0] - 3, P.box_y[1] + 3), (z0 + P.box_h, z0 + P.box_h + 12))
    glands = [cyl_y(20.0, P.box_y[0] - 18.0, P.box_y[0], x, z0 + 30.0) for x in (-80.0, -40.0, 0.0, 40.0, 80.0)]
    return fuse_all([b, lid] + glands)


def box_bolts():
    out = []
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    zb = P.robot_lower_beam_z[0]
    for x in (-125.0, 125.0):
        for y in P.robot_rear_beam_y:
            out += [hex_z(AF[8], z0, z0 + HEAD_K[8], x, y), cyl_z(8.0, zb - NUT_M[8] - 3.0, z0, x, y),
                    hex_z(AF[8], zb - NUT_M[8], zb, x, y)]
    return out


# ---------------------------------------------------------------------
# XY bracket (moves with X): adapter plate on the X carriage, Y plate, 2 gussets. Steel S235, laser cut, welded.
# ---------------------------------------------------------------------
def xy_adapter():
    d0, d1 = P.xy_adapter_dx
    l0, l1 = P.xy_adapter_low_dx
    z0, z1 = P.xy_adapter_z
    pts = [(XC + d0, z1), (XC + d1, z1), (XC + d1, P.xy_adapter_top_z), (XC + l1, P.xy_adapter_top_z),
           (XC + l1, z0), (XC + l0, z0)]
    plate = poly_xz(pts, P.xy_adapter_y[0], P.xy_adapter_t)
    holes = [cyl_y(P.m6_hole, P.xy_adapter_y[0] - 1, P.xy_adapter_y[1] + 1, XC + du, z)
             for du in (-P.xm_car_len / 2.0 + 15.0, P.xm_car_len / 2.0 - 15.0) for z in (550.0, 590.0)]
    return plate.cut(holes)


def y_plate():
    plate = poly_yz(P.y_plate_pts, X0, P.xy_plate_t)
    holes = [cyl_x(P.m6_hole, X0 - 1, X0 + P.xy_plate_t + 1, y, z)
             for y in (P.ym_y[0] - 40.0, (P.ym_y[0] + P.ym_y[1]) / 2.0, P.ym_y[1] + 40.0) for z in (435.0, 465.0)]
    return plate.cut(holes)


def gussets():
    y0 = P.xy_adapter_y[0]
    top = poly_xy([(X0, y0), (X0 - P.gusset_dx, y0), (X0, y0 - P.gusset_top_len)], P.xy_adapter_z[1] - P.gusset_t,
                  P.gusset_t)
    bot = poly_xy([(X0, y0), (X0 - P.gusset_dx, y0), (X0, y0 - P.gusset_bot_len)], P.xy_adapter_z[0], P.gusset_t)
    return [top, bot]


# ---------------------------------------------------------------------
# Y slide: Z adapter, mast bracket, mast, antenna, receiver box
# ---------------------------------------------------------------------
def z_adapter():
    plate = box_span((xr(P.za_x[0]), xr(P.za_x[1])), (YT - P.za_dy, YT + P.za_dy), P.za_z)
    holes = [cyl_x(P.m6_hole, xr(P.za_x[0]) - 1, xr(P.za_x[1]) + 1, YT + dy, z)
             for dy in (-20.0, 20.0) for z in (435.0, 465.0)]
    lighten = [cyl_x(40.0, xr(P.za_x[0]) - 1, xr(P.za_x[1]) + 1, YT, z) for z in (540.0, 640.0)]
    return plate.cut(holes + lighten)


def mast_bracket():
    z0 = P.za_z[1]
    b = box_span((xr(P.za_x[0]), XT + 25.0), (YT - P.mast_bracket_dy, YT + P.mast_bracket_dy), (z0, z0 + P.mast_bracket_t))
    return b.cut(cyl_z(P.mast_d + 0.5, z0 - 1, z0 + P.mast_bracket_t + 1, XT, YT))


def mast():
    """Aluminium tube 25 x 2 through the bracket, shaft collar below, 5/8" adapter on top (in the stem)."""
    z0 = P.za_z[1] - P.mast_collar[1]
    tube = tube_z(P.mast_d, 2.0, z0, P.mast_z[1], XT, YT)
    collar = tube_z(P.mast_collar[0], (P.mast_collar[0] - P.mast_d) / 2.0, z0, P.za_z[1], XT, YT)
    return [tube, collar]


def antenna():
    z0 = P.mast_z[1]
    stem = cyl_z(P.ant_stem[0], z0, z0 + P.ant_stem[1], XT, YT)
    zd = z0 + P.ant_stem[1]
    r = P.ant_dome[0] / 2.0
    base = cyl_z(P.ant_dome[0], zd, zd + 25.0, XT, YT)
    dome = Part.makeCone(r, r - 25.0, P.ant_dome[1] - 25.0, V(XT, YT, zd + 25.0), Z)
    return fuse_all([stem, base, dome])


def rx_box():
    (x0, x1), (y0, y1), z = P.rx_box
    xa = xr(P.za_x[0])
    return box_span((xa + x0, xa + x1), (YT + y0, YT + y1), z)


# ---------------------------------------------------------------------
# Z slide: head mount plate with 2 hook pins and 2 star knobs
# ---------------------------------------------------------------------
def head_mount():
    plate = box_span((xr(P.hm_x[0]), xr(P.hm_x[1])), (YT - P.hm_dy, YT + P.hm_dy), (ZC + P.hm_dz[0], ZC + P.hm_dz[1]))
    holes = [cyl_x(P.m6_hole, xr(P.hm_x[0]) - 1, xr(P.hm_x[1]) + 1, YT + dy, ZC + dz)
             for dy in (-25.0, 25.0) for dz in (-25.0, 25.0)]
    return plate.cut(holes)


def hook_pins():
    x0 = xr(P.hm_x[1])
    out = []
    for s in (-1, 1):
        y, z = YT + s * P.pin_dy, ZC + P.pin_dz
        out.append(fuse_all([cyl_x(P.pin_d, x0, x0 + P.head_plate_t + 4.0, y, z),
                             cyl_x(20.0, x0 + P.head_plate_t + 4.0, x0 + P.head_plate_t + 8.0, y, z)]))
    return out


def knobs():
    """M8 stud in the head mount plate, star knob Ø32 against the head plate."""
    x0 = xr(P.hm_x[1])
    x1 = xr(P.hp_x[1])
    out = []
    for s in (-1, 1):
        y, z = YT + s * P.pin_dy, ZC + P.knob_dz
        out.append(fuse_all([cyl_x(8.0, x0, x1 + 22.0, y, z), cyl_x(32.0, x1, x1 + 16.0, y, z)]))
    return out


# ---------------------------------------------------------------------
# Paint head (sub-part of the Z slide)
# ---------------------------------------------------------------------
def rod_xy():
    a = math.radians(P.rod_ang)
    return [(XT + P.rod_r * math.cos(a), YT + s * P.rod_r * math.sin(a)) for s in (-1, 1)]


def head_plate():
    """6 mm aluminium, bent 90 degrees: vertical leg on the head mount, bottom leg under the tube
    (nozzle seat, bushings for the shroud rods, sensor)."""
    x0, x1 = xr(P.hp_x[0]), xr(P.hp_x[1])
    vert = box_span((x0, x1), (YT - P.hm_dy, YT + P.hm_dy), (ZC + P.hp_dz[0], ZC + P.hp_dz[1]))
    cuts = []
    for s in (-1, 1):
        y = YT + s * P.pin_dy
        zp = ZC + P.pin_dz
        cuts += [cyl_x(P.pin_d + 0.5, x0 - 1, x1 + 1, y, zp), cyl_x(21.0, x0 - 1, x1 + 1, y, zp + 15.0),
                 box_span((x0 - 1, x1 + 1), (y - (P.pin_d + 0.5) / 2.0, y + (P.pin_d + 0.5) / 2.0), (zp, zp + 15.0))]
        cuts.append(cyl_x(9.0, x0 - 1, x1 + 1, y, ZC + P.knob_dz))
        for dz in P.ubolt_dz:
            cuts.append(cyl_x(P.ubolt_d + 1.0, x0 - 1, x1 + 1, YT + s * (P.tube_od / 2.0 + P.ubolt_d / 2.0 + 0.5), ZC + dz))
    vert = vert.cut(cuts)
    z0, z1 = ZC + P.bp_dz[0], ZC + P.bp_dz[1]
    bottom = box_span((x0, XT + P.bp_dx), (YT - P.bp_dy, YT + P.bp_dy), (z0, z1))
    holes = [cyl_z(P.spray_hole, z0 - 1, z1 + 1, XT, YT), cyl_z(12.2, z0 - 1, z1 + 1, XT + P.sensor_dx, YT)]
    holes += [cyl_z(P.bushing[0], z0 - 1, z1 + 1, x, y) for (x, y) in rod_xy()]
    bottom = bottom.cut(holes)
    return fuse_all([vert, bottom])


def guide_tube():
    return tube_z(P.tube_od, P.tube_wall, ZC + P.tube_dz[0], ZC + P.tube_dz[1], XT, YT)


def spray_can():
    body = cyl_z(P.can_d, ZC + P.can_dz[0], ZC + P.can_dz[1], XT, YT)
    cup = cyl_z(P.can_cup[0], ZC + P.can_cup[1], ZC + P.can_cup[2], XT, YT)
    noz = cyl_z(P.can_nozzle[0], ZC + P.can_nozzle[1], ZC + P.can_nozzle[2], XT, YT)
    return fuse_all([body, cup, noz])


def pusher():
    return cyl_z(P.pusher[0], ZC + P.pusher[1], ZC + P.pusher[2], XT, YT)


def u_bolts():
    """2 U-bolts M8 for 76 mm pipe: bow around the tube, legs through the head plate, washer + nut behind it."""
    r = P.tube_od / 2.0 + P.ubolt_d / 2.0 + 0.5
    xb = xr(P.hp_x[0])
    out = []
    for dz in P.ubolt_dz:
        z = ZC + dz
        bow = Part.makeTorus(r, P.ubolt_d / 2.0, V(XT, YT, z), Z, -180.0, 180.0, 180.0)
        bow.rotate(V(XT, YT, z), Z, -90.0)
        legs = [cyl_x(P.ubolt_d, xb - 14.0, XT, YT + s * r, z) for s in (-1, 1)]
        out.append(fuse_all([bow] + legs))
        for s in (-1, 1):
            out.append(hex_x(AF[8], xb - NUT_M[8] - 1.5, xb - 1.5, YT + s * r, z).cut(
                cyl_x(8.0, xb - 20, xb, YT + s * r, z)))
            out.append(cyl_x(17.0, xb - 1.5, xb, YT + s * r, z).cut(cyl_x(8.4, xb - 3, xb + 1, YT + s * r, z)))
    return out


def servo_bracket():
    (bx0, bx1), (by0, by1), (bz0, bz1) = P.servo_box
    x1 = xr(P.hp_x[1])
    vert = box_span((x1, x1 + 3.0), (YT - 45.0, YT + by1), (ZC + 95.0, ZC + bz0))
    horiz = box_span((x1, x1 + bx1), (YT - 45.0, YT + by1), (ZC + bz0 - 3.0, ZC + bz0))
    return fuse_all([vert, horiz])


def servo():
    """Waterproof servo 35 kg cm (IP67), output shaft along y."""
    (bx0, bx1), (by0, by1), (bz0, bz1) = P.servo_box
    x1 = xr(P.hp_x[1])
    return box_span((x1 + bx0, x1 + bx1), (YT + by0, YT + by1), (ZC + bz0, ZC + bz1))


def lever():
    """Lever on the servo horn with a finger down into the tube onto the pusher (1 mm free)."""
    x1 = xr(P.hp_x[1])
    xs = x1 + P.servo_shaft[0]
    arm = box_span((xs - 5.0, XT + 10.0), (YT - 1.5, YT + 1.5), (ZC + P.lever_dz[0], ZC + P.lever_dz[1]))
    finger = box_span((XT - 3.5, XT + 3.5), (YT - 1.5, YT + 1.5), (ZC + P.pusher[2] + 1.0, ZC + P.lever_dz[0]))
    return fuse_all([arm, finger])


def bushings():
    od, length, fd, ft = P.bushing
    z1 = ZC + P.bp_dz[1]
    out = []
    for (x, y) in rod_xy():
        b = fuse_all([cyl_z(od, z1 - length, z1, x, y), cyl_z(fd, z1, z1 + ft, x, y)])
        out.append(b.cut(cyl_z(P.rod_d + 0.1, z1 - length - 1, z1 + ft + 1, x, y)))
    return out


def springs():
    """Compression springs between the bushings and the shroud ring, drawn at free position (they are left out of the
    interference check: when the shroud lifts they are compressed)."""
    z1 = ZC + P.bp_dz[1] - P.bushing[1]
    z0 = ZC + P.ring_top_dz
    return [tube_z(P.spring_od, (P.spring_od - P.spring_id) / 2.0, z0, z1, x, y) for (x, y) in rod_xy()]


def sensor():
    """M12 inductive proximity sensor (non-flush, Sn 4 mm) through the bottom plate, 2 nuts, M12 connector."""
    x, y = XT + P.sensor_dx, YT
    zf = ZC + P.ring_top_dz + P.sensor_face_gap
    z0, z1 = ZC + P.bp_dz[0], ZC + P.bp_dz[1]
    body = cyl_z(12.0, zf, zf + P.sensor_len, x, y)
    plug = cyl_z(14.0, zf + P.sensor_len, zf + P.sensor_len + 20.0, x, y)
    nuts = [hex_z(17.0, z0 - 4.0, z0, x, y).cut(cyl_z(12.0, z0 - 5, z0 + 1, x, y)),
            hex_z(17.0, z1, z1 + 4.0, x, y).cut(cyl_z(12.0, z1 - 1, z1 + 5, x, y))]
    return [fuse_all([body, plug])] + nuts


# Shroud (moves up against the springs when it touches the ground)
def shroud_ring():
    z1 = ZC + P.ring_top_dz
    z0 = z1 - P.shroud_ring_t
    r = P.shroud_od / 2.0 + 3.0
    parts = [cyl_z(2 * r, z0, z1, XT, YT)]
    for (x, y) in rod_xy() + [(XT + P.sensor_dx, YT)]:
        parts.append(cyl_z(26.0, z0, z1, x, y))
    parts.append(box_span((XT, XT + P.sensor_dx), (YT - 13.0, YT + 13.0), (z0, z1)))     # target for the sensor
    ring = fuse_all(parts)
    return ring.cut(cyl_z(P.shroud_hole, z0 - 1, z1 + 1, XT, YT))


def shroud_tube():
    z1 = ZC + P.ring_top_dz - P.shroud_ring_t
    return tube_z(P.shroud_od, P.shroud_wall, z1 - P.shroud_len, z1, XT, YT)


def rods():
    """Stainless rods Ø10, screwed into the ring, through the bushings; the collars on top hold the free position."""
    z0 = ZC + P.ring_top_dz
    return [cyl_z(P.rod_d, z0, ZC + P.rod_top_dz, x, y) for (x, y) in rod_xy()]


def collars():
    z0 = ZC + P.bp_dz[1] + P.bushing[3]
    return [tube_z(P.collar[0], (P.collar[0] - P.rod_d) / 2.0, z0, z0 + P.collar[1], x, y) for (x, y) in rod_xy()]


# ---------------------------------------------------------------------
# Ground and marks (animation, renders)
# ---------------------------------------------------------------------
def paint_dot(x, y, d, z=0.0, t=0.6):
    return cyl_z(d, z, z + t, x, y)


def target_cross(x, y, size=60.0, z=0.0, w=4.0, t=0.4):
    a = box_span((x - size / 2.0, x + size / 2.0), (y - w / 2.0, y + w / 2.0), (z, z + t))
    b = box_span((x - w / 2.0, x + w / 2.0), (y - size / 2.0, y + size / 2.0), (z, z + t))
    return a.fuse(b)
