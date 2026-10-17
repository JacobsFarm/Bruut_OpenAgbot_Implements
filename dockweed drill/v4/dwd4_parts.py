"""Onderdelen van de dockweed drill v4: een functie per onderdeel, geeft een Part-shape in robotcoordinaten.

Intern wordt getekend in het portaalframe (x, v, z): v = afstand achter de achterkant van de achterste onderbalk
van de robot. to_robot() spiegelt dat naar robot-y (y = robot_beam_rear_face - v).
Bewegende groepen worden in hun referentiestand getekend:
- X-slede op x = 0;
- Z-slede (binnenbuis steunpoot, spilbok, spil) met de onderkant van het gereedschap op z_ref (rijstand);
- pot hangend onder de spilbok bij z_ref (rand op z_ref - pot_rim).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd4_params as P

UP = V(0, 0, 1)
ALONG_V = V(0, 1, 0)


# ---------------------------------------------------------------------
# Basisvormen (portaalframe)
# ---------------------------------------------------------------------
def to_robot(shape):
    s = shape.mirror(V(0, 0, 0), V(0, 1, 0))
    s.translate(V(0, P.robot_beam_rear_face, 0))
    return s


def box(x0, x1, v0, v1, z0, z1):
    return Part.makeBox(x1 - x0, v1 - v0, z1 - z0, V(x0, v0, z0))


def tube_rect(x0, x1, v0, v1, z0, z1, t, axis):
    o = box(x0, x1, v0, v1, z0, z1)
    if axis == "x":
        i = box(x0 - 1, x1 + 1, v0 + t, v1 - t, z0 + t, z1 - t)
    elif axis == "v":
        i = box(x0 + t, x1 - t, v0 - 1, v1 + 1, z0 + t, z1 - t)
    else:
        i = box(x0 + t, x1 - t, v0 + t, v1 - t, z0 - 1, z1 + 1)
    return o.cut(i)


def cyl(r, p, d, L):
    return Part.makeCylinder(r, L, p, d)


def pipe(ro, ri, p, d, L):
    d = V(d)
    d.normalize()
    return cyl(ro, p, d, L).cut(cyl(ri, p - d * 1.0, d, L + 2.0))


def holes_z(sh, pts, r, z0, h):
    for (px, pv) in pts:
        sh = sh.cut(cyl(r, V(px, pv, z0 - 1), UP, h + 2))
    return sh


def fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def compound(shapes):
    return Part.makeCompound(list(shapes))


def poly_vz(pts, x0, t):
    """Plaat in het v-z-vlak (punten (v, z)), dikte t vanaf x0."""
    w = Part.makePolygon([V(x0, v, z) for v, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(t, 0, 0))


def lemon_x(x0, x1, vc, zc, b, h):
    """Massief citroenprofiel langs x: b = lengte in z (tip tot tip), h = dikte in v. Twee cirkelbogen."""
    R = (b * b / 4.0 + h * h / 4.0) / h
    d = R - h / 2.0
    c1 = Part.makeCylinder(R, x1 - x0, V(x0, vc + d, zc), V(1, 0, 0))
    c2 = Part.makeCylinder(R, x1 - x0, V(x0, vc - d, zc), V(1, 0, 0))
    return c1.common(c2)


def lemon_ring(x0, x1, vc, zc, bo, ho, bi, hi):
    return lemon_x(x0, x1, vc, zc, bo, ho).cut(lemon_x(x0 - 1, x1 + 1, vc, zc, bi, hi))


def m10_bolt_z(x, v, z_head, z_nut):
    """M10 van boven: kop op z_head (naar boven), moer onder z_nut (naar beneden)."""
    shank = cyl(P.m10_d / 2.0, V(x, v, z_nut - P.m10_nut_m - 3.0), UP, z_head - z_nut + P.m10_nut_m + 3.0)
    head = cyl(P.m10_head_r, V(x, v, z_head), UP, P.m10_head_k)
    nut = cyl(P.m10_head_r, V(x, v, z_nut - P.m10_nut_m), UP, P.m10_nut_m)
    return [shank.fuse(head).fuse(nut)]


# ---------------------------------------------------------------------
# Afgeleide maten (v-opbouw van de robot af naar achteren)
# ---------------------------------------------------------------------
def stack():
    s = {}
    s["up"] = (P.up_v0, P.up_v1)
    s["flange"] = (P.up_v1, P.up_v1 + P.flange_t)
    s["tube"] = P.tube_v
    s["slide"] = (P.slide_v0, P.slide_v0 + P.slide_t)
    s["belt_ref"] = P.tube_v + 4.0                      # riem en riemklemmen
    s["jack_plate"] = (s["slide"][1], s["slide"][1] + P.jack_mount_t)
    s["jack"] = (s["jack_plate"][1], s["jack_plate"][1] + P.jack_outer[0])   # buitenbuis steunpoot
    s["jack_c"] = (s["jack"][0] + s["jack"][1]) / 2.0
    s["inner"] = (s["jack_c"] - P.jack_inner[0] / 2, s["jack_c"] + P.jack_inner[0] / 2)
    s["sb_back"] = (s["inner"][1], s["inner"][1] + P.sb_back_t)
    s["spindle"] = s["sb_back"][1] + P.spindle_dv
    return s


S = stack()


def spindle_y():
    return P.v_to_y(S["spindle"])


def pot_rim_ref():
    return P.z_ref - P.pot_rim


# ---------------------------------------------------------------------
# Aanbouwbok (vast aan de robot), side = -1 links / +1 rechts
# ---------------------------------------------------------------------
def _hs_bolt_pts(side):
    xc = side * P.hs_x
    return [(xc - P.hs_bolt_dx, P.hs_bolt_v), (xc + P.hs_bolt_dx, P.hs_bolt_v)]


def hs_top_plate(side):
    xc = side * P.hs_x
    z0 = P.robot_lower_beam_z[1]
    p = box(xc - P.hs_plate_half_x, xc + P.hs_plate_half_x, -P.robot_beam, 0.0, z0, z0 + P.hs_plate_t)
    return to_robot(holes_z(p, _hs_bolt_pts(side), 5.5, z0, P.hs_plate_t))


def hs_clamp_plate(side):
    xc = side * P.hs_x
    z1 = P.robot_lower_beam_z[0]
    p = box(xc - P.hs_plate_half_x, xc + P.hs_plate_half_x, -P.robot_beam, 0.0, z1 - P.hs_plate_t, z1)
    return to_robot(holes_z(p, _hs_bolt_pts(side), 5.5, z1 - P.hs_plate_t, P.hs_plate_t))


def hs_back_plate(side):
    xc = side * P.hs_x
    return to_robot(box(xc - P.hs_plate_half_x, xc + P.hs_plate_half_x, 0.0, P.hs_plate_t,
                        P.up_z0, P.robot_lower_beam_z[1] + P.hs_plate_t))


def hs_bolts(side):
    z_head = P.robot_lower_beam_z[1] + P.hs_plate_t
    z_nut = P.robot_lower_beam_z[0] - P.hs_plate_t
    out = []
    for (x, v) in _hs_bolt_pts(side):
        out += m10_bolt_z(x, v, z_head, z_nut)
    return to_robot(compound(out))


def upright(side):
    xc = side * P.hs_x
    h = P.up_size / 2.0
    u = tube_rect(xc - h, xc + h, P.up_v0, P.up_v1, P.up_z0, P.up_z1, P.up_wall, "z")
    for zp in P.xbar_z:                          # gaten voor de bouten van de steunflenzen
        for dx in (-22, 22):
            for dz in (-30, 30):
                u = u.cut(cyl(5.5, V(xc + dx, P.up_v0 - 1, zp + dz), ALONG_V, P.up_size + 2))
    return to_robot(u)


def upright_cap(side):
    xc = side * P.hs_x
    h = P.up_size / 2.0
    return to_robot(box(xc - h, xc + h, P.up_v0, P.up_v1, P.up_z1, P.up_z1 + P.up_cap_t))


def gusset(side):
    xc = side * P.hs_x
    z0 = P.robot_lower_beam_z[1] + P.hs_plate_t
    pts = [(-P.robot_beam, z0), (P.up_v0, z0), (P.up_v0, z0 + P.gusset_h)]
    return to_robot(poly_vz(pts, xc - P.gusset_t / 2.0, P.gusset_t))


def cross_tube():
    x = P.hs_x - P.up_size / 2.0
    return to_robot(tube_rect(-x, x, P.up_v0, P.up_v1, P.cross_z[0], P.cross_z[1], P.cross_wall, "x"))


# ---------------------------------------------------------------------
# X-as v2: aftakasbuizen (vast)
# ---------------------------------------------------------------------
def pto_tube(zp):
    L = P.xbar_L
    return to_robot(lemon_x(-L / 2, L / 2, S["tube"], zp, P.pto_b, P.pto_h).cut(
        lemon_x(-L / 2 - 1, L / 2 + 1, S["tube"], zp, P.pto_b - 2 * P.pto_t, P.pto_h - 2 * P.pto_t)))


def support_flange(side, zp):
    xs = side * P.hs_x
    v0, v1 = S["flange"]
    fl = box(xs - P.flange_half_x, xs + P.flange_half_x, v0, v1, zp - P.flange_half_z, zp + P.flange_half_z)
    for dx in (-22, 22):
        for dz in (-30, 30):
            fl = fl.cut(cyl(5.5, V(xs + dx, v0 - 1, zp + dz), ALONG_V, P.flange_t + 2))
    return to_robot(fl)


def support_flange_bolts(side, zp):
    xs = side * P.hs_x
    out = []
    v1 = S["flange"][1]
    for dx in (-22, 22):
        for dz in (-30, 30):
            p0 = V(xs + dx, P.up_v0 - 10.0, zp + dz)
            shank = cyl(5.0, p0, ALONG_V, v1 + 7.0 - (P.up_v0 - 10.0))
            head = cyl(P.m10_head_r, V(xs + dx, v1, zp + dz), ALONG_V, 7.0)
            nut = cyl(P.m10_head_r, V(xs + dx, P.up_v0 - P.m10_nut_m, zp + dz), ALONG_V, P.m10_nut_m)
            out.append(shank.fuse(head).fuse(nut))
    return to_robot(compound(out))


def support_rib(side, zp):
    xs = side * P.hs_x
    r = box(xs - P.rib_half_x, xs + P.rib_half_x, S["flange"][1], S["tube"], zp - P.rib_t / 2, zp + P.rib_t / 2)
    return to_robot(r.cut(lemon_x(xs - 40, xs + 40, S["tube"], zp, P.pto_b, P.pto_h)))


def end_plate(side):
    L = P.xbar_L
    zl, zh = P.xbar_z
    x0 = L / 2 - P.end_plate_t if side > 0 else -L / 2
    tv = S["tube"]
    ep = box(x0, x0 + P.end_plate_t, tv - 30, tv + 30, zl - 40, zh + 40)
    ep = ep.cut(box(x0 - 1, x0 + P.end_plate_t + 1, tv - 20, tv + 20, zl + 55, zh - 55))
    for zp in (zl, zh):
        ep = ep.cut(lemon_x(x0 - 1, x0 + P.end_plate_t + 1, tv, zp, P.pto_b, P.pto_h))
    return to_robot(ep)


def _clamp_x():
    """Binnenkant riemklem: buiten het bereik van de spanrollen bij x = x_max."""
    return P.xbar_L / 2 - P.end_plate_t - 3.0 - 15.0


def belt_clamp_bracket(side):
    L = P.xbar_L
    xe = side * (L / 2 - P.end_plate_t)
    br = S["belt_ref"]
    return to_robot(box(min(xe, xe - side * 55), max(xe, xe - side * 55), br - 20, br, 850, 910))


def belt_clamp(side):
    x0 = _clamp_x()
    br = S["belt_ref"]
    return to_robot(box(min(side * x0, side * (x0 + 15)), max(side * x0, side * (x0 + 15)), br, br + 26, 862, 898))


def belt():
    br = S["belt_ref"]
    x = _clamp_x()
    return to_robot(box(-x, x, br + 6, br + 6 + P.belt_w, P.belt_z - 1.7, P.belt_z + 1.7))


def limit_switch():
    """Inductieve eindschakelaar X-min op de linker eindplaat."""
    x0 = -(P.xbar_L / 2 - P.end_plate_t)
    return to_robot(cyl(6, V(x0, S["tube"] + 18, 930), V(1, 0, 0), 28))


def end_stop():
    x0 = P.xbar_L / 2 - P.end_plate_t
    return to_robot(cyl(10, V(x0, S["tube"] + 18, 930), V(-1, 0, 0), 28))


# ---------------------------------------------------------------------
# X-slede (beweegt in x; getekend op x = 0)
# ---------------------------------------------------------------------
def sleeve_positions():
    """(x, lengte, z) van de 3 hulzen."""
    zl, zh = P.xbar_z
    h = P.sleeve_pitch / 2
    return [(-h, P.sleeve_L, zh), (h, P.sleeve_L, zh), (0.0, P.sleeve_low_L, zl)]


def sleeves():
    out = []
    tv = S["tube"]
    for xh, Lh, zp in sleeve_positions():
        sl = lemon_ring(xh - Lh / 2, xh + Lh / 2, tv, zp, P.sl_b, P.sl_h, P.sl_b - 2 * P.sl_t, P.sl_h - 2 * P.sl_t)
        sl = sl.cut(box(xh - Lh / 2 - 1, xh + Lh / 2 + 1, tv - P.sl_h / 2 - 2, tv - P.sl_h / 2 + P.sl_t + 2.5,
                        zp - P.sleeve_slot / 2, zp + P.sleeve_slot / 2))
        out.append(sl)
    return to_robot(compound(out))


def _pad_bolt_pts(xh, Lh, zp):
    return [(xh + dx, zp + dz) for dx in (-(Lh / 2 - 20), Lh / 2 - 20) for dz in (-40, 40)]


def sleeve_pads():
    out = []
    tv = S["tube"]
    v0 = tv + P.sl_h / 2 - 2
    for xh, Lh, zp in sleeve_positions():
        pad = box(xh - Lh / 2, xh + Lh / 2, v0, S["slide"][0], zp - P.pad_half_z, zp + P.pad_half_z)
        pad = pad.cut(lemon_x(xh - Lh / 2 - 1, xh + Lh / 2 + 1, tv, zp, P.sl_b, P.sl_h))
        for (bx, bz) in _pad_bolt_pts(xh, Lh, zp):
            pad = pad.cut(cyl(4.0, V(bx, v0 - 1, bz), ALONG_V, S["slide"][0] - v0 + 2))
        out.append(pad)
    return to_robot(compound(out))


def sleeve_bolts():
    out = []
    v0 = S["tube"] + P.sl_h / 2 + 2
    v1 = S["slide"][1]
    for xh, Lh, zp in sleeve_positions():
        for (bx, bz) in _pad_bolt_pts(xh, Lh, zp):
            out.append(cyl(4, V(bx, v0, bz), ALONG_V, v1 + 5 - v0).fuse(cyl(6.5, V(bx, v1, bz), ALONG_V, 5)))
    return to_robot(compound(out))


def scrapers():
    out = []
    tv = S["tube"]
    for xh, Lh, zp in sleeve_positions():
        for xw in (xh - Lh / 2 - P.scraper_t, xh + Lh / 2):
            sc = lemon_ring(xw, xw + P.scraper_t, tv, zp, P.sl_b + 3, P.sl_h + 3, P.pto_b, P.pto_h)
            out.append(sc.cut(box(xw - 1, xw + P.scraper_t + 1, tv - P.sl_h / 2 - 4, tv - P.pto_h / 2 + 3,
                                  zp - P.sleeve_slot / 2, zp + P.sleeve_slot / 2)))
    return to_robot(compound(out))


def grease_nipples():
    out = []
    for xh, Lh, zp in sleeve_positions():
        out.append(cyl(3.2, V(xh, S["tube"], zp + P.sl_b / 2), UP, 12))
    return to_robot(compound(out))


def x_slide():
    v0, v1 = S["slide"]
    h = P.slide_half_x
    sl = box(-h, h, v0, v1, P.slide_z[0], P.slide_z[1])
    sl = sl.cut(cyl(9, V(P.motor_dx, v0 - 1, P.pulley_z), ALONG_V, P.slide_t + 2))
    for (gx, gz) in ((-100, 910), (70, 830)):
        sl = sl.cut(cyl(20, V(gx, v0 - 1, gz), ALONG_V, P.slide_t + 2))
    for xh, Lh, zp in sleeve_positions():
        for (bx, bz) in _pad_bolt_pts(xh, Lh, zp):
            if zp == P.xbar_z[1]:
                sl = sl.cut(cyl(4.5, V(bx, v0 - 1, bz), ALONG_V, P.slide_t + 2))
            else:                                   # onderste huls: sleufgaten (tolerantie in z)
                sl = sl.cut(box(bx - 4.5, bx + 4.5, v0 - 1, v1 + 1, bz - 8, bz + 8))
    return to_robot(sl)


def x_gearbox():
    v1 = S["slide"][1]
    xm = P.motor_dx
    return to_robot(box(xm - 30, xm + 30, v1, v1 + 55, P.pulley_z - 30, P.pulley_z + 30))


def x_motor():
    v1 = S["slide"][1]
    xm = P.motor_dx
    z = P.pulley_z
    return to_robot(box(xm - 28.5, xm + 28.5, v1 + 55, v1 + 167, z - 28.5, z + 28.5).fuse(
        box(xm - 25, xm + 25, v1 + 167, v1 + 190, z - 25, z + 25)))


def x_pulley():
    br = S["belt_ref"]
    xm = P.motor_dx
    z = P.pulley_z
    return to_robot(cyl(15.9, V(xm, br + 6, z), ALONG_V, 15).fuse(cyl(18.5, V(xm, br + 4, z), ALONG_V, 2)).fuse(
        cyl(18.5, V(xm, br + 21, z), ALONG_V, 2)))


def x_idlers():
    br = S["belt_ref"]
    return to_robot(compound([cyl(15, V(P.motor_dx + dx, br + 5, 897), ALONG_V, 18) for dx in (-32, 32)]))


# Steunpoot: vaste delen op de X-slede
def jack_mount_plate():
    v0, v1 = S["jack_plate"]
    p = box(-60, 60, v0, v1, P.jack_mount_z[0], P.jack_mount_z[1])
    for dx in (-45, 45):
        for z in (P.jack_mount_z[0] + 20, P.jack_mount_z[1] - 20):
            p = p.cut(cyl(5.5, V(dx, v0 - 1, z), ALONG_V, P.jack_mount_t + 2))
    return to_robot(p)


def jack_outer_tube():
    h = P.jack_outer[0] / 2
    v0, v1 = S["jack"]
    return to_robot(tube_rect(-h, h, v0, v1, P.jack_outer_z[0], P.jack_outer_z[1], P.jack_outer[1], "z"))


def jack_guide_bush():
    """PE-bus onder in de buitenbuis: neemt de speling tussen binnen- en buitenbuis weg."""
    hi = P.jack_outer[0] / 2 - P.jack_outer[1]
    hb = P.jack_inner[0] / 2
    c = S["jack_c"]
    z0 = P.jack_outer_z[0]
    return to_robot(box(-hi, hi, c - hi, c + hi, z0, z0 + P.guide_bush_L).cut(
        box(-hb, hb, c - hb, c + hb, z0 - 1, z0 + P.guide_bush_L + 1)))


def jack_head():
    """Kegelwielhuis met de slingeras naar +x."""
    c = S["jack_c"]
    z = P.jack_outer_z[1]
    h = box(-45, 45, c - 38, c + 38, z, z + P.jack_head)
    return to_robot(h.fuse(cyl(18, V(45, c, z + 50), V(1, 0, 0), 15)))


def jack_screw():
    """Trapeziumspindel Tr20 in de poot (vast aan de kop)."""
    return to_robot(cyl(10, V(0, S["jack_c"], 1110.0), UP, P.jack_outer_z[1] - 1110.0))


def jack_motor():
    """NEMA 23 closed-loop op de slingeras (koppeling en beugel vereenvoudigd)."""
    c = S["jack_c"]
    z = P.jack_outer_z[1] + 50
    m = cyl(12, V(60, c, z), V(1, 0, 0), 30).fuse(box(90, 98, c - 35, c + 35, z - 35, z + 35))
    m = m.fuse(box(98, 210, c - 28.5, c + 28.5, z - 28.5, z + 28.5)).fuse(box(210, 233, c - 25, c + 25, z - 25, z + 25))
    return to_robot(m)


def chain_driver():
    """Meenemer kabelrups (op de X-slede)."""
    xm = -80.0
    tv = S["tube"]
    zk = P.chain_z
    v0, v1 = S["slide"]
    return to_robot(box(xm - 20, xm + 20, tv - 25, v1, zk + 80, zk + 86).fuse(
        box(xm - 20, xm + 20, v0 - 3, v0, P.slide_z[1] - 8, zk + 86)))


SPIRAL_X = P.spiral_x        # links van de spilbok
SPIRAL_Z0 = P.spiral_z0      # bovenste anker aan de buitenbuis van de steunpoot


def _spiral_v():
    return S["spindle"] - 40.0


def cable_bracket_x():
    """Arm aan de buitenbuis van de steunpoot: bovenste anker van de spiraalkabel."""
    v0 = S["jack"][1] - 18
    return to_robot(box(SPIRAL_X - 26, -P.jack_outer[0] / 2, v0, _spiral_v() + 15, SPIRAL_Z0 - 6, SPIRAL_Z0))


# ---------------------------------------------------------------------
# Camera: vast, hoog boven de werkstrook (zoals Robot Ruud)
# ---------------------------------------------------------------------
def camera_mast():
    x = P.cam_mast_x
    v0 = P.up_v0 + 5
    return to_robot(tube_rect(x - 20, x + 20, v0, v0 + 40, P.up_z1 + P.up_cap_t, P.cam_z, 3, "z"))


def camera_arm():
    x = P.cam_mast_x
    v0 = P.up_v0 + 5
    return to_robot(tube_rect(x - 20, x + 20, v0 + 40, P.cam_v + 20, P.cam_z - 40, P.cam_z, 3, "v"))


def camera_crossbar():
    return to_robot(tube_rect(P.cam_x - 20, P.cam_mast_x - 20, P.cam_v - 20, P.cam_v + 20, P.cam_z - 40, P.cam_z, 3, "x"))


def camera():
    xc, cv = P.cam_x, P.cam_v
    z1 = P.cam_z - 40
    return to_robot(box(xc - 30, xc + 30, cv - 28, cv + 28, z1 - 65, z1).fuse(cyl(14, V(xc, cv, z1 - 90), UP, 25)))


def led_bar():
    cv = P.cam_v
    z1 = P.cam_z - 40
    return to_robot(box(P.cam_x + 40, P.cam_x + 200, cv - 15, cv + 15, z1 - 30, z1))


# ---------------------------------------------------------------------
# Z-slede = binnenbuis van de steunpoot met de spilbok eronder (beweegt in z; getekend bij z_ref)
# ---------------------------------------------------------------------
def _zc():
    return P.z_ref


def _zt_bottom():
    """Onderkant binnenbuis (de achterplaat van de spilbok is daar vastgezet)."""
    return _zc() + P.inner_bottom


def inner_tube():
    h = P.jack_inner[0] / 2
    v0, v1 = S["inner"]
    b = _zt_bottom()
    return to_robot(tube_rect(-h, h, v0, v1, b, b + P.inner_L, P.jack_inner[1], "z"))


def inner_guide_ring():
    """PE-ring boven op de binnenbuis (loopt in de buitenbuis)."""
    hi = P.jack_outer[0] / 2 - P.jack_outer[1]
    hb = P.jack_inner[0] / 2
    c = S["jack_c"]
    z1 = _zt_bottom() + P.inner_L
    return to_robot(box(-hi, hi, c - hi, c + hi, z1 - 60, z1).cut(box(-hb, hb, c - hb, c + hb, z1 - 61, z1 + 1)))


def inner_foot_plate():
    """Voetplaat onder de binnenbuis (vervangt de voet van de steunpoot), gelast aan de achterplaat."""
    h = P.jack_inner[0] / 2
    b = _zt_bottom()
    return to_robot(box(-h - 10, h + 10, S["inner"][0] - 10, S["sb_back"][0], b - 10, b))


def _sb():
    """(onderste plaat, bovenplaat) in z bij z_ref."""
    zc = _zc()
    return zc + P.sb_lo, zc + P.sb_mo


def _bearing_z():
    zc = _zc()
    return zc + P.bearing_lo, zc + P.bearing_hi


def _motor_xv():
    """Hart spilmotor (x, v): achter de spil op hartafstand ketting = chain_center(), voet naar de spil (-v)."""
    return 0.0, S["spindle"] + P.spindle_motor_dv


def _motor_plate_v():
    """(voorkant, achterkant) van de motorplaat; de voet zit tegen de achterkant."""
    vf = _motor_xv()[1] - P.motor_foot_h
    return vf - P.motor_plate_t, vf


def _chain_z():
    return _zc() + P.drive_chain_z


def _motor_z(d):
    """z op afstand d langs de motoras vanaf het einde van de uitgaande as (as wijst omhoog)."""
    return _chain_z() + P.sprocket_w / 2 + 2.0 - d


def sb_back_plate():
    """Achterplaat van de spilbok (aan de binnenbuis van de steunpoot)."""
    z_lo, z_mo = _sb()
    v0, v1 = S["sb_back"]
    p = box(-80, 80, v0, v1, z_lo, _zc() + P.sb_back_top)
    for (wz0, wz1) in ((z_lo + 30, z_lo + 120), (z_lo + 150, _zt_bottom() - 25)):     # lichtgaten
        p = p.cut(box(-32, 32, v0 - 1, v1 + 1, wz0, wz1))
    for dx, dz in _sb_back_bolts():
        p = p.cut(cyl(5.5, V(dx, v0 - 1, z_lo + dz), ALONG_V, 10))
    return to_robot(p)


def _sb_back_bolts():
    b = _zt_bottom()
    z_lo = _sb()[0]
    return [(dx, dz) for dx in (-55, 55) for dz in (60, 145, 260) if b < z_lo + dz < _zc() + P.sb_back_top]


def sb_back_bolts():
    z_lo = _sb()[0]
    v1 = S["sb_back"][1]
    return to_robot(compound([cyl(8.5, V(dx, v1, z_lo + dz), ALONG_V, 7) for dx, dz in _sb_back_bolts()]))


def sb_plate_lower():
    z_lo = _sb()[0]
    v1, vs = S["sb_back"][1], S["spindle"]
    p = box(-75, 75, v1, vs + 80, z_lo, z_lo + 8).fuse(box(-125, 125, vs - 25, vs + 45, z_lo, z_lo + 8)).removeSplitter()
    p = holes_z(p, [(0, vs)], 25, z_lo, 8)
    p = holes_z(p, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 10.5, z_lo, 8)
    return to_robot(p)


def sb_top_plate():
    """Bovenplaat boven het bovenste lager, onder de ketting (sluit de spilbok, draagt de spiraalkabelbeugel)."""
    z_mo = _sb()[1]
    v1, vs = S["sb_back"][1], S["spindle"]
    return to_robot(holes_z(box(-75, 75, v1, vs + 80, z_mo, z_mo + 8), [(0, vs)], P.shaft_d / 2 + 2, z_mo, 8))


def sb_side_plate(side):
    z_lo, z_mo = _sb()
    v1, vs = S["sb_back"][1], S["spindle"]
    x = side * 78
    p = box(x - 2.5, x + 2.5, v1, _motor_plate_v()[0], z_lo + 8, z_mo)
    p = p.cut(box(x - 4, x + 4, vs - 20, vs + 55, z_lo + 40, z_mo - 25))
    for (v, z) in _motor_tab_bolts():                        # sleuven voor de lippen van de motorplaat
        p = p.cut(box(x - 4, x + 4, v - 5.5 - P.motor_slot / 2, v + 5.5 + P.motor_slot / 2, z - 5.5, z + 5.5))
    return to_robot(p)


def _bearing_plate_v():
    vb = S["spindle"] - P.ucp_h
    return vb - P.bearing_plate_t, vb


def sb_bearing_plate():
    """Staande lagerplaat tussen de zijplaten: de voeten van de 2 UCP 204 zitten ertegen (M12, sleufgaten in z)."""
    z_lo, z_mo = _sb()
    v0, v1 = _bearing_plate_v()
    p = box(-75.5, 75.5, v0, v1, z_lo + 8, z_mo)
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            p = p.cut(box(dx - 6.5, dx + 6.5, v0 - 1, v1 + 1, zb - 9.5, zb + 9.5))
    return to_robot(p)


def ucp204(zb):
    """UCP 204 staand lagerblok (as O20): voet tegen de lagerplaat (v), as verticaal op z = zb."""
    vs = S["spindle"]
    vb = vs - P.ucp_h
    a, b, tf = P.ucp_L, P.ucp_b, P.ucp_foot_t
    foot = box(-a / 2, a / 2, vb, vb + tf, zb - b / 2, zb + b / 2)
    for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
        foot = foot.cut(box(dx - P.ucp_slot[0] / 2, dx + P.ucp_slot[0] / 2, vb - 1, vb + tf + 1,
                            zb - P.ucp_slot[1] / 2, zb + P.ucp_slot[1] / 2))
    r = P.ucp_ring_d / 2
    body = box(-r * 0.8, r * 0.8, vb + tf - 1, vs, zb - b / 2 + 4, zb + b / 2 - 4)
    ring = cyl(r, V(0, vs, zb - b / 2 + 4), UP, b - 8)
    inner = cyl(P.ucp_d / 2 + 6, V(0, vs, zb - P.ucp_ring_w / 2), UP, P.ucp_ring_w)
    h = foot.fuse(body).fuse(ring).fuse(inner).removeSplitter()
    return to_robot(h.cut(cyl(P.ucp_d / 2, V(0, vs, zb - b), UP, 2 * b)))


def bearing_lower():
    return ucp204(_bearing_z()[0])


def bearing_upper():
    return ucp204(_bearing_z()[1])


def bearing_bolts():
    """4x M12 door de lagerplaat (moer aan de voorkant)."""
    v0, v1 = _bearing_plate_v()
    vt = v1 + P.ucp_foot_t
    out = []
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            out.append(cyl(6, V(dx, v0 - 12, zb), ALONG_V, vt - v0 + 20).fuse(cyl(10, V(dx, vt, zb), ALONG_V, 7.5)).fuse(
                cyl(10, V(dx, v0 - 10, zb), ALONG_V, 10)))
    return to_robot(compound(out))


def spindle_shaft():
    """Spilas O20 C45: door beide lagers, onderin 30 mm in de prop van de spilbuis gelast, bovenin het kettingwiel."""
    z0 = _zc() + P.spindle_tube_top - 30
    return to_robot(cyl(P.shaft_d / 2, V(0, S["spindle"], z0), UP, _zc() + P.shaft_top - z0))


def spindle_tube():
    """Buis 42,4 x 4 over de overhang (spilflens tot onder het onderste lager), bovenin een prop met boring O20."""
    ro = P.spindle_tube[0] / 2
    ri = ro - P.spindle_tube[1]
    z0, z1 = _zc() + 112, _zc() + P.spindle_tube_top
    vs = S["spindle"]
    return to_robot(pipe(ro, ri, V(0, vs, z0), UP, z1 - z0).fuse(pipe(ri + 0.5, P.shaft_d / 2, V(0, vs, z1 - 30), UP, 30)))


def _flange_holes(sh, v, z0, t):
    """Steekcirkel O80 met 4x M10 (gereedschapswissel)."""
    for k in range(4):
        a = math.radians(45 + 90 * k)
        sh = sh.cut(cyl(5.5, V(40 * math.cos(a), v + 40 * math.sin(a), z0 - 1), UP, t + 2))
    return sh


def spindle_flange():
    z = _zc() + 100
    return to_robot(_flange_holes(cyl(55, V(0, S["spindle"], z), UP, 12), S["spindle"], z, 12))


# Aandrijving spil: 800 W tandwielmotor rechtop (as omhoog) achter de spilbok, 10B-1 ketting 38T -> 12T
def _sprocket(z, x, v, bore, hub_d, hub_len, up):
    """Kettingwiel (tanden als schijf over de tandtoppen) met naaf boven (up) of onder het kettingvlak."""
    zc = _chain_z()
    r = P.pitch_d(z) / 2 + 0.3 * P.chain_pitch
    w = P.sprocket_w
    s = cyl(r, V(x, v, zc - w / 2), UP, w)
    hz = zc + w / 2 - 0.01 if up else zc - w / 2 - hub_len + 0.01
    s = s.fuse(cyl(hub_d / 2, V(x, v, hz), UP, hub_len)).removeSplitter()
    return s.cut(cyl(bore / 2, V(x, v, zc - w / 2 - hub_len - 1), UP, w + 2 * hub_len + 2))


def spindle_sprocket():
    """10B-1 12T, boring 20 + spie, naaf naar boven tot de bovenkant van de as."""
    hub = _zc() + P.shaft_top - (_chain_z() + P.sprocket_w / 2)
    return to_robot(_sprocket(P.z_spindle_sprocket, 0, S["spindle"], P.shaft_d, 40, hub, True))


def motor_sprocket():
    """10B-1 38T Taper-Lock 2012 met bus 19, naaf naar beneden (naar de motor)."""
    mx, vm = _motor_xv()
    return to_robot(_sprocket(P.z_motor_sprocket, mx, vm, P.motor_shaft_d, 80, 22, False))


def _hull(c1, r1, c2, r2, z0, h):
    """Omhullende van twee cirkels (x, v) in het x-v-vlak, hoogte h vanaf z0 (ketting- en kastvorm)."""
    (x1, v1), (x2, v2) = c1, c2
    d = math.hypot(x2 - x1, v2 - v1)
    phi = math.atan2(v2 - v1, x2 - x1)
    al = math.acos((r1 - r2) / d)
    pts = [V(x1 + r1 * math.cos(phi + al), v1 + r1 * math.sin(phi + al), z0),
           V(x2 + r2 * math.cos(phi + al), v2 + r2 * math.sin(phi + al), z0),
           V(x2 + r2 * math.cos(phi - al), v2 + r2 * math.sin(phi - al), z0),
           V(x1 + r1 * math.cos(phi - al), v1 + r1 * math.sin(phi - al), z0)]
    quad = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, h))
    return fuse([cyl(r1, V(x1, v1, z0), UP, h), cyl(r2, V(x2, v2, z0), UP, h), quad])


def _chain_circles(extra):
    mx, vm = _motor_xv()
    return (0.0, S["spindle"]), P.pitch_d(P.z_spindle_sprocket) / 2 + extra, (mx, vm), \
        P.pitch_d(P.z_motor_sprocket) / 2 + extra


def drive_chain():
    """10B-1 ketting, getekend als band van de schakelplaten (rollen niet getekend)."""
    zc = _chain_z()
    c1, r1, c2, r2 = _chain_circles(0.75 * P.chain_pitch)
    outer = _hull(c1, r1, c2, r2, zc - 7, 14)
    c1, r1, c2, r2 = _chain_circles(0.3 * P.chain_pitch + 1.0)
    return to_robot(outer.cut(_hull(c1, r1, c2, r2, zc - 8, 16)))


def chain_guard():
    """Kettingkast 2 mm: rand rond de ketting en deksel, open aan de onderkant; aan de bovenplaat geschroefd."""
    zc = _chain_z()
    g = P.chain_guard_gap
    z0, z1 = zc - 14, _zc() + P.shaft_top + 3
    c1, r1, c2, r2 = _chain_circles(0.75 * P.chain_pitch + g)
    inner = _hull(c1, r1, c2, r2, z0 - 1, z1 - z0 + 1)
    outer = _hull(c1, r1 + 2, c2, r2 + 2, z0, z1 - z0 + 2)
    return to_robot(outer.cut(inner))


def motor_plate():
    """Motorplaat 10 mm achter de spilbok, met 2 lippen 6 mm langs de zijplaten (M10 in sleuven: kettingspanning
    in v). Motorvoet met 4x M8 tegen de achterkant."""
    mx, vm = _motor_xv()
    v0, v1 = _motor_plate_v()
    za, zb = _motor_z(P.motor_foot[1]), _motor_z(P.motor_foot[0])
    p = box(-80.5, 80.5, v0, v1, za - 12, zb + 12)
    for side in (-1, 1):
        xo = side * 80.5
        p = p.fuse(box(min(xo, xo + 6 * side), max(xo, xo + 6 * side), v0 - 45, v1, za - 12, zb + 12))
    p = p.removeSplitter()
    for d in P.motor_foot_holes:
        for dx in (-P.motor_foot_hole_dx / 2, P.motor_foot_hole_dx / 2):
            p = p.cut(cyl(4.25, V(mx + dx, v0 - 1, _motor_z(d)), ALONG_V, P.motor_plate_t + 2))
    for (v, z) in _motor_tab_bolts():
        for x in (-83.5, 83.5):
            p = p.cut(cyl(5.5, V(x - 4, v, z), V(1, 0, 0), 8))
    return to_robot(p)


def _motor_tab_bolts():
    """(v, z) van de 2 M10 per lip (door de sleuven in de zijplaten)."""
    v0 = _motor_plate_v()[0]
    za, zb = _motor_z(P.motor_foot[1]), _motor_z(P.motor_foot[0])
    return [(v0 - 25, za + 5), (v0 - 25, zb - 5)]


def spindle_motor():
    """800 W tandwielmotor met voet (maattekening parts/800 watt motor), as omhoog, voet naar de spil (-v)."""
    mx, vm = _motor_xv()
    zs = _motor_z(0)
    d0, d1, da, db = P.motor_nose
    nose = Part.makeCone(db / 2, da / 2, d1 - d0, V(mx, vm, zs - d1), UP)
    parts = [nose]
    for (a, b, dia) in (P.motor_ring, P.motor_body, P.motor_cap):
        parts.append(cyl(dia / 2, V(mx, vm, zs - b), UP, b - a))
    vf = vm - P.motor_foot_h
    za, zb = _motor_z(P.motor_foot[1]), _motor_z(P.motor_foot[0])
    foot = box(mx - P.motor_foot_w / 2, mx + P.motor_foot_w / 2, vf, vf + P.motor_foot_t, za, zb)
    for d in P.motor_foot_holes:
        for dx in (-P.motor_foot_hole_dx / 2, P.motor_foot_hole_dx / 2):
            foot = foot.cut(cyl(4.25, V(mx + dx, vf - 1, _motor_z(d)), ALONG_V, P.motor_foot_t + 2))
    saddle = box(mx - 30, mx + 30, vf + P.motor_foot_t - 1, vm - 40, za + 8, zb - 8)
    parts += [foot, saddle]
    return to_robot(fuse(parts))


def spindle_motor_shaft():
    """Uitgaande as O19 h6 van de motor, 35 mm uit de neus (omhoog), door het kettingwiel."""
    mx, vm = _motor_xv()
    zs = _motor_z(0)
    return to_robot(cyl(P.motor_shaft_d / 2, V(mx, vm, zs - P.motor_shaft_out), UP, P.motor_shaft_out))


def cable_bracket_z():
    """Beugel op de bovenplaat van de spilbok: onderste anker van de spiraalkabel."""
    z = _sb()[1] + 8
    v = _spiral_v()
    return to_robot(box(SPIRAL_X - 26, -75, v - 15, v + 15, z, z + 6))


def pot_bushes():
    z = _sb()[0] + 8
    vs = S["spindle"]
    return to_robot(compound([pipe(19, 8.5, V(s * P.pot_rod_dx, vs, z), UP, 25) for s in (-1, 1)]))


def _ring_z():
    """Onderkant stelring: rust 1 mm boven de PE-bus."""
    return _sb()[0] + 8 + 25 + 1


def pot_sensor():
    vs = S["spindle"]
    return to_robot(cyl(6, V(P.pot_rod_dx, vs + 20, _ring_z() + 6), ALONG_V, 20))


def pot_sensor_bracket():
    vs = S["spindle"]
    z0 = _sb()[0] + 8
    return to_robot(box(P.pot_rod_dx - 8, P.pot_rod_dx + 8, vs + 40, vs + 43, z0, _ring_z() + 16))


# ---------------------------------------------------------------------
# Bus (zoals Robot Ruud): stuk stalen pijp met deksel; hangt in rust, getekend met de rand op pot_rim_ref()
# ---------------------------------------------------------------------
def _rim():
    return pot_rim_ref()


def pot_shell():
    R = P.pot_d / 2
    return to_robot(pipe(R, R - P.pot_t, V(0, S["spindle"], _rim()), UP, P.pot_h))


def pot_lid():
    R = P.pot_d / 2
    vs = S["spindle"]
    z = _rim() + P.pot_h
    d = holes_z(cyl(R, V(0, vs, z), UP, P.pot_lid_t), [(0, vs)], 25, z, P.pot_lid_t)
    return to_robot(holes_z(d, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 8, z, P.pot_lid_t))


def shaft_seal():
    return to_robot(pipe(32, P.spindle_tube[0] / 2 + 0.5, V(0, S["spindle"], _rim() + P.pot_h + P.pot_lid_t), UP, 8))


def _rod_len():
    """Stang van bovenkant deksel tot bovenkant stelring; de ring rust in rust op de bus van de bodemplaat."""
    ring0 = _ring_z()
    return ring0 + 12 - (_rim() + P.pot_h + P.pot_lid_t)


def pot_rods():
    z = _rim() + P.pot_h + P.pot_lid_t
    vs = S["spindle"]
    return to_robot(compound([cyl(P.pot_rod_d / 2, V(s * P.pot_rod_dx, vs, z), UP, _rod_len()) for s in (-1, 1)]))


def pot_set_rings():
    z = _ring_z()
    vs = S["spindle"]
    return to_robot(compound([pipe(14, 8, V(s * P.pot_rod_dx, vs, z), UP, 12) for s in (-1, 1)]))


# ---------------------------------------------------------------------
# Gereedschap (draait om de spilas; getekend op x = 0, onderkant op z_ref)
# ---------------------------------------------------------------------
def _cross(L, b, t, hole=0.0):
    k = Part.makeBox(L, b, t, V(-L / 2, -b / 2, 0)).fuse(Part.makeBox(b, L, t, V(-b / 2, -L / 2, 0)))
    k = k.fuse(cyl(b * 1.25, V(0, 0, 0), UP, t)).removeSplitter()
    if hole > 0:
        k = k.cut(cyl(hole, V(0, 0, -1), UP, t + 2))
    for i in range(4):          # snijkant: afschuining op de voorlopende onderkant van elke arm
        pts = [V(22, b / 2 + 0.01, -0.01), V(22, b / 2 - 9, -0.01), V(22, b / 2 + 0.01, t * 0.55)]
        wedge = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(L / 2 - 20, 0, 0))
        wedge.rotate(V(0, 0, 0), UP, 90 * i)
        k = k.cut(wedge)
    return k


def cutter_parts():
    """Vermorzelfrees O180: (naam, shape, kleur) in robotcoordinaten. Onderkant tanden op z_ref."""
    zc = _zc()
    vs = S["spindle"]
    R = P.cutter_d / 2
    out = []
    lo = _cross(2 * (R - 8), 30, 10)
    lo.translate(V(0, vs, zc + 25))
    out.append(("cutter_cross_lower", lo, "hardox"))
    teeth = []
    for i in range(P.cutter_teeth):
        t = Part.makeBox(18, 10, 25, V(R - 18, 5, 0))       # tand aan de voorlopende kant van de arm
        t.rotate(V(0, 0, 0), UP, 90 * i)
        t.translate(V(0, vs, zc))
        teeth.append(t)
    out.append(("cutter_teeth", compound(teeth), "hardox"))
    hi = _cross(2 * (R - 5), 28, 10, hole=24.4)
    hi.rotate(V(0, 0, 0), UP, 45)
    hi.translate(V(0, vs, zc + 60))
    out.append(("cutter_cross_upper", hi, "hardox"))
    out.append(("cutter_core_tube", pipe(24.15, 19.15, V(0, vs, zc + 35), UP, 55), "steel"))
    out.append(("cutter_flange", _flange_holes(cyl(55, V(0, vs, zc + 90), UP, 10), vs, zc + 90, 10), "steel"))
    out.append(("cutter_centre_point", Part.makeCone(1.0, 12.0, 60, V(0, vs, zc - 35), UP), "chrome"))
    return [(n, to_robot(s), c) for n, s, c in out]


def mower_parts():
    """Maaischijf O200 met 3 scharnierende mesjes (tipcirkel O230). Onderkant mesjes op z_ref."""
    zb = _zc()
    vs = S["spindle"]
    out = []
    s = cyl(100, V(0, vs, zb + 4), UP, 4)
    for i in range(3):
        a = math.radians(60 + 120 * i)
        s = s.cut(cyl(22, V(55 * math.cos(a), vs + 55 * math.sin(a), zb + 3), UP, 6))
    out.append(("mower_disc", s, "chrome"))
    out.append(("mower_core_tube", pipe(24.15, 19.15, V(0, vs, zb + 8), UP, 82), "steel"))
    out.append(("mower_flange", _flange_holes(cyl(55, V(0, vs, zb + 90), UP, 10), vs, zb + 90, 10), "steel"))
    blades = []
    for i in range(3):
        m = Part.makeBox(35, 18, 1.0, V(80, -9, 0))
        m.rotate(V(80, 0, 0), UP, -15)
        m = m.fuse(cyl(4, V(85, 0, -3), UP, 15))
        m.rotate(V(0, 0, 0), UP, 120 * i)
        m.translate(V(0, vs, zb))
        blades.append(m)
    out.append(("mower_blades", compound(blades), "chrome"))
    return [(n, to_robot(s), c) for n, s, c in out]


# ---------------------------------------------------------------------
# Elektra (vast) en kabels (vervormen met x en z)
# ---------------------------------------------------------------------
def ebox_plate():
    w = P.ebox[0] / 2
    return to_robot(box(-w, w, P.up_v0 - P.ebox_plate_t, P.up_v0, P.cross_z[0], P.ebox_z0 + P.ebox[1] + 5))


def ebox():
    w, h, d = P.ebox[0] / 2, P.ebox[1], P.ebox[2]
    v1 = P.up_v0 - P.ebox_plate_t
    return to_robot(box(-w, w, v1 - d, v1, P.ebox_z0, P.ebox_z0 + h))


def ebox_glands():
    v = P.up_v0 - P.ebox_plate_t - P.ebox[2] / 2
    return to_robot(compound([cyl(10, V(-P.ebox[0] / 2 + 30 + 60 * k, v, P.ebox_z0 - 20), UP, 20) for k in range(4)]))


def chain_bracket():
    """Steun onder het vaste eind van de kabelrups, op de linker eindplaat."""
    x0 = -P.xbar_L / 2
    tv = S["tube"]
    zk = P.chain_z
    z_ep = P.xbar_z[1] + 40.0
    return to_robot(box(x0, x0 + 90, tv - 25, tv + 25, zk - 6, zk).fuse(
        box(x0, x0 + P.end_plate_t, tv - 25, tv + 25, z_ep, zk - 6)))


def chain_shapes(x):
    """Kabelrups bij slede-stand x: (onderpart, bovenpart, bocht)."""
    x_fixed = -P.xbar_L / 2 + 30
    x_mov = x - 80
    x_b = max(x_fixed, x_mov) + 120
    tv = S["tube"]
    v0, v1 = tv - 25, tv + 25
    zk = P.chain_z
    lower = box(x_fixed, x_b, v0, v1, zk, zk + 25)
    upper = box(x_mov, x_b, v0, v1, zk + 55, zk + 80)
    bend = box(x_b, x_b + 25, v0, v1, zk, zk + 80)
    return to_robot(lower), to_robot(upper), to_robot(bend)


def spiral_cable(x, z_tool):
    """Spiraalkabel van de motorplaat van de spilbok (beweegt) omhoog naar de arm aan de steunpoot (vast)."""
    z_a = z_tool + P.sb_mo + 8 + 6
    z_c = SPIRAL_Z0 - 6
    n = P.spiral_turns
    pitch = (z_c - z_a) / n
    v = _spiral_v()
    rings = [Part.makeTorus(22, 4.5, V(x + SPIRAL_X, v, z_a + pitch * (k + 0.5)), UP) for k in range(n)]
    return to_robot(compound(rings))


# ---------------------------------------------------------------------
# Omgeving (alleen voor afbeeldingen en animatie)
# ---------------------------------------------------------------------
def leaf(length, width, thick):
    e = Part.Ellipse(V(0, 0, 0), length / 2, width / 2)
    s = Part.Face(Part.Wire(e.toShape())).extrude(V(0, 0, thick))
    s.translate(V(length / 2, 0, 0))
    return s


def dock_plant(x, y, scale=1.0, z=0.0, spin=0.0):
    """Ridderzuring: rozet van 7 bladeren, wortelkop en penwortel. Geeft (bladeren, wortel)."""
    leaves = []
    for i in range(7):
        b = leaf((230 - 15 * (i % 3)) * scale, 85 * scale, 3)
        b.rotate(V(0, 0, 0), V(0, 1, 0), -22)
        b.rotate(V(0, 0, 0), UP, i * 360.0 / 7 + 10 + spin)
        b.translate(V(x, y, z + 12 * scale))
        leaves.append(b)
    root = cyl(22 * scale, V(x, y, z - 10), UP, 26 * scale).fuse(
        Part.makeCone(2.0, 20.0 * scale, 320 * scale, V(x, y, z - 10 - 320 * scale), UP))
    return compound(leaves), root
