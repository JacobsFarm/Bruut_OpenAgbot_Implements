"""Onderdelen van de dockweed drill v1: een functie per onderdeel, geeft een Part-shape in robotcoordinaten.

Intern wordt getekend in het portaalframe (x, v, z): v = afstand achter de achterkant van de achterste onderbalk
van de robot. to_robot() spiegelt dat naar robot-y (y = robot_beam_rear_face - v).
Bewegende groepen worden in hun referentiestand getekend:
- X-slede op x = 0;
- Z-slede (spil, gereedschap) met de onderkant van het gereedschap op z_ref (rijstand);
- pot hangend onder de spilbok bij z_ref (rand op z_ref - pot_rim).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd1_params as P

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
    s["prof"] = (P.prof_v0, P.prof_v1)
    s["tube"] = (P.prof_v0 + P.prof_v1) / 2.0           # hart profielen (kabelrups)
    s["slide"] = (P.slide_v0, P.slide_v0 + P.slide_t)
    s["belt_ref"] = P.belt_ref                          # riem en riemklemmen
    s["zr"] = s["slide"][1] + P.rail_h                  # railvoet Z-rails
    s["zt"] = (s["zr"] + P.riser_t, s["zr"] + P.riser_t + P.zt_d)
    s["screw"] = s["zt"][0] - P.screw_dv
    s["sb_back"] = (s["zt"][1], s["zt"][1] + P.sb_back_t)
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
    for zp in P.xbar_z:                          # gaten voor de M8 naar de hamermoeren in het profiel
        for dx in (-12, 12):
            u = u.cut(cyl(4.5, V(xc + dx, P.up_v0 - 1, zp), ALONG_V, P.up_size + 2))
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
# X-as v1: alu-profielen 40 x 80 met HGR15-rails (vast)
# ---------------------------------------------------------------------
def alu_profile(zp):
    """Alu-constructieprofiel 40 x 80 met sleuf 8, lengte langs x, 80 diep (v) en 40 hoog (z)."""
    L = P.xbar_L
    x0, x1 = -L / 2, L / 2
    v0 = P.prof_v0
    z0 = zp - P.prof_h / 2
    p = box(x0, x1, v0, v0 + 80, z0, z0 + 40)
    sw, sd = 8.2, 9.0
    p = p.cut(box(x0 - 1, x1 + 1, v0 - 1, v0 + sd, zp - sw / 2, zp + sw / 2))
    p = p.cut(box(x0 - 1, x1 + 1, v0 + 80 - sd, v0 + 81, zp - sw / 2, zp + sw / 2))
    for vc in (v0 + 20, v0 + 60):
        p = p.cut(box(x0 - 1, x1 + 1, vc - sw / 2, vc + sw / 2, z0 - 1, z0 + sd))
        p = p.cut(box(x0 - 1, x1 + 1, vc - sw / 2, vc + sw / 2, z0 + 40 - sd, z0 + 41))
        p = p.cut(box(x0 - 1, x1 + 1, vc - 10, vc + 10, zp - 10, zp + 10))        # holle kamer
        p = p.fuse(pipe(7, 3.4, V(x0, vc, zp), V(1, 0, 0), L))                    # kernboring
    return to_robot(p.removeSplitter())


def profile_bolts(side):
    """M8 door de staander in een hamermoer in de voorste sleuf van elk profiel."""
    xs = side * P.hs_x
    out = []
    for zp in P.xbar_z:
        for dx in (-12, 12):
            out.append(cyl(4, V(xs + dx, P.up_v0, zp), ALONG_V, P.prof_v0 + 8 - P.up_v0).fuse(
                cyl(6.5, V(xs + dx, P.up_v0 - 5, zp), ALONG_V, 5)))
    return to_robot(compound(out))


def hgr15_rail_x(x0, x1, vf, zc):
    """HGR15-rail langs x op vlak v = vf, steekt uit naar +v."""
    r = box(x0, x1, vf, vf + 15, zc - 7.5, zc + 7.5)
    r = r.cut(box(x0 - 1, x1 + 1, vf + 8, vf + 11, zc - 8.5, zc - 5.0))
    return r.cut(box(x0 - 1, x1 + 1, vf + 8, vf + 11, zc + 5.0, zc + 8.5))


def x_rails():
    L = P.xbar_L
    return to_robot(compound([hgr15_rail_x(-L / 2 + 10, L / 2 - 10, P.prof_v1, zp) for zp in P.xbar_z]))


def end_plate(side):
    """Kopplaat alu 10 mm op de profieleinden, verbindt de 2 profielen."""
    L = P.xbar_L
    zl, zh = P.xbar_z
    x0 = L / 2 if side > 0 else -L / 2 - P.end_plate_t
    v0, v1 = P.prof_v0, P.prof_v1
    ep = box(x0, x0 + P.end_plate_t, v0, v1, zl - 40, zh + 40)
    return to_robot(ep.cut(box(x0 - 1, x0 + P.end_plate_t + 1, v0 + 18, v1 - 18, zl + 50, zh - 50)))


def belt_clamp_bracket(side):
    """Hoekbeugel op de buitenkant van de kopplaat, draagt de riemklem."""
    L = P.xbar_L
    xe = L / 2 + P.end_plate_t
    br = S["belt_ref"]
    x0, x1 = xe, P.clamp_x[1]
    return to_robot(box(side * x0 if side > 0 else -x1, x1 if side > 0 else -x0, br - 20, br, 850, 910))


def belt_clamp(side):
    br = S["belt_ref"]
    x0, x1 = P.clamp_x
    return to_robot(box(x0 if side > 0 else -x1, x1 if side > 0 else -x0, br, br + 26, 862, 898))


def belt():
    br = S["belt_ref"]
    x = P.clamp_x[0]
    return to_robot(box(-x, x, br + 6, br + 6 + P.belt_w, P.belt_z - 1.7, P.belt_z + 1.7))


def limit_switch():
    """Inductieve eindschakelaar X-min aan de achterkant van het bovenste profiel."""
    x = -(P.xbar_L / 2 - 10)
    return to_robot(cyl(6, V(x, P.prof_v1, P.xbar_z[1] - 14), ALONG_V, 20))


def end_stop():
    x = P.xbar_L / 2 - 10
    return to_robot(cyl(6, V(x, P.prof_v1, P.xbar_z[1] - 14), ALONG_V, 20))


# ---------------------------------------------------------------------
# X-slede (beweegt in x; getekend op x = 0)
# ---------------------------------------------------------------------
def hgh15_block_x(xc, vf, zc):
    """HGH15CA-wagen op een x-rail (railvoet op v = vf); bovenvlak op vf + 28."""
    b = box(xc - 30.7, xc + 30.7, vf + 4.3, vf + 28, zc - 17, zc + 17)
    return b.cut(box(xc - 31, xc + 31, vf + 4.0, vf + 15.3, zc - 7.8, zc + 7.8))


def x_blocks():
    return to_robot(compound([hgh15_block_x(dx, P.prof_v1, zp) for zp in P.xbar_z
                              for dx in (-P.x_block_dx, P.x_block_dx)]))


def x_slide():
    v0, v1 = S["slide"]
    h = P.slide_half_x
    sl = box(-h, h, v0, v1, P.slide_z[0], P.slide_z[1])
    sl = sl.cut(cyl(9, V(P.motor_dx, v0 - 1, P.pulley_z), ALONG_V, P.slide_t + 2))
    for (gx, gz) in ((-100, 910), (70, 830)):
        sl = sl.cut(cyl(20, V(gx, v0 - 1, gz), ALONG_V, P.slide_t + 2))
    for zp in P.xbar_z:                                 # 4x M4 per wagen (HGH15CA: 38 x 30)
        for dx in (-P.x_block_dx, P.x_block_dx):
            for (bx, bz) in ((dx - 19, zp - 15), (dx + 19, zp - 15), (dx - 19, zp + 15), (dx + 19, zp + 15)):
                sl = sl.cut(cyl(2.25, V(bx, v0 - 1, bz), ALONG_V, P.slide_t + 2))
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


def hgh15_block_z(zc, vf, xc):
    """HGH15CA-wagen op een Z-rail (railvoet op v = vf); bovenvlak op vf - 28."""
    b = box(xc - 17, xc + 17, vf - 28, vf - 4.3, zc - 30.7, zc + 30.7)
    return b.cut(box(xc - 7.8, xc + 7.8, vf - 15.3, vf - 4.0, zc - 31, zc + 31))


def z_blocks():
    return to_robot(compound([hgh15_block_z(zp, S["zr"], dx) for zp in P.xbar_z for dx in (-P.z_rail_dx, P.z_rail_dx)]))


def nut_housing():
    v1 = S["slide"][1]
    return to_robot(box(-26, 26, v1, S["zt"][0] - 1, P.nut_z[0], P.nut_z[1]).cut(
        cyl(14.5, V(0, S["screw"], P.nut_z[0] - 1), UP, 42)))


def ball_nut():
    z = P.nut_z[1]
    return to_robot(pipe(24, 8.6, V(0, S["screw"], z), UP, 10).fuse(pipe(14, 8.6, V(0, S["screw"], z + 10), UP, 30)))


def chain_driver():
    """Meenemer kabelrups (op de X-slede)."""
    xm = -80.0
    tv = S["tube"]
    zk = P.chain_z
    v0, v1 = S["slide"]
    return to_robot(box(xm - 20, xm + 20, tv - 25, v1, zk + 80, zk + 86).fuse(
        box(xm - 20, xm + 20, v0 - 3, v0, P.slide_z[1] - 8, zk + 86)))


SPIRAL_X = -95.0        # naast de Z-koker, aan de kant van de cameramast (de X-motor zit op +x)
SPIRAL_Z0 = 850.0       # onderste anker op de X-slede: ruim onder de Z-kopplaat, ook op max. diepte


def cable_bracket_x():
    v1 = S["slide"][1]
    vs = S["zt"][0] + 15.0
    return to_robot(box(SPIRAL_X - 20, SPIRAL_X + 20, v1, vs + 15, SPIRAL_Z0 - 8, SPIRAL_Z0))


def camera_mast():
    xc = P.cam_dx
    v1 = S["slide"][1]
    return to_robot(tube_rect(xc - 15, xc + 15, v1, v1 + 30, P.cam_mast_z[0], P.cam_mast_z[1], 2, "z"))


def _cam_v():
    return S["spindle"] + P.cam_reach_v


def camera_arm():
    xc = P.cam_dx
    v1 = S["slide"][1]
    z1 = P.cam_mast_z[1]
    return to_robot(tube_rect(xc - 15, xc + 15, v1 + 30, _cam_v() + 20, z1 - 30, z1, 2, "v"))


def camera():
    xc = P.cam_dx
    cv = _cam_v()
    z1 = P.cam_mast_z[1] - 30
    return to_robot(box(xc - 30, xc + 30, cv - 28, cv + 28, z1 - 65, z1).fuse(cyl(14, V(xc, cv, z1 - 90), UP, 25)))


def led_bar():
    xc = P.cam_dx
    cv = _cam_v() - 70
    z1 = P.cam_mast_z[1] - 30
    return to_robot(box(xc - 150, xc + 150, cv - 15, cv + 15, z1 - 30, z1).fuse(
        box(xc - 150, xc + 150, cv - 13, cv + 13, z1 - 34, z1 - 30)))


# ---------------------------------------------------------------------
# Z-slede, spilbok en spil (beweegt in z; getekend bij onderkant gereedschap = z_ref)
# ---------------------------------------------------------------------
def _zc():
    return P.z_ref


def _zt_bottom():
    return _zc() + P.zt_bottom


def z_tube():
    v0, v1 = S["zt"]
    b = _zt_bottom()
    return to_robot(tube_rect(-P.zt_w / 2, P.zt_w / 2, v0, v1, b, b + P.zt_L, P.zt_wall, "z"))


def z_top_plate():
    b = _zt_bottom() + P.zt_L
    return to_robot(box(-45, 45, S["screw"] - 35, S["zt"][1], b, b + 8))


def z_risers():
    b = _zt_bottom()
    return to_robot(compound([box(dx - 12.5, dx + 12.5, S["zr"], S["zt"][0], b + 45, b + 893)
                              for dx in (-P.z_rail_dx, P.z_rail_dx)]))


def hgr15_rail_z(z0, z1, vf, xc):
    """HGR15-rail langs z, railvoet op v = vf, steekt uit naar -v."""
    r = box(xc - 7.5, xc + 7.5, vf - 15, vf, z0, z1)
    r = r.cut(box(xc - 8.5, xc - 5.0, vf - 11, vf - 8, z0 - 1, z1 + 1))
    return r.cut(box(xc + 5.0, xc + 8.5, vf - 11, vf - 8, z0 - 1, z1 + 1))


def z_rails():
    b = _zt_bottom()
    return to_robot(compound([hgr15_rail_z(b + 45, b + 893, S["zr"], dx) for dx in (-P.z_rail_dx, P.z_rail_dx)]))


def screw_bearings():
    """BF12 (onder) en BK12 (boven) aan de Z-koker."""
    b = _zt_bottom()
    v0 = S["zt"][0]
    bf = box(-30, 30, v0 - 43, v0, b + 15, b + 35).cut(cyl(8, V(0, S["screw"], b + 14), UP, 22))
    bk = box(-30, 30, v0 - 43, v0, b + 895, b + 920).cut(cyl(8, V(0, S["screw"], b + 894), UP, 27))
    return to_robot(compound([bf, bk]))


def ball_screw():
    b = _zt_bottom()
    return to_robot(cyl(8, V(0, S["screw"], b + 20), UP, 902))


def screw_coupling():
    b = _zt_bottom()
    return to_robot(cyl(12.5, V(0, S["screw"], b + 922), UP, 28))


def z_motor():
    b = _zt_bottom() + P.zt_L + 8
    s = S["screw"]
    return to_robot(box(-28.5, 28.5, s - 28.5, s + 28.5, b, b + 152))


def cable_bracket_z():
    b = _zt_bottom() + P.zt_L + 8
    v0 = S["zt"][0]
    return to_robot(box(SPIRAL_X - 20, -45, v0, v0 + 30, b, b + 6))


def _sb():
    zc = _zc()
    return zc + P.sb_lo, zc + P.sb_hi, zc + P.sb_mo


def _bearing_bolts():
    vs = S["spindle"]
    return [(dx, vs + dv) for dx in (-46, 46) for dv in (-46, 46)]


def sb_back_plate():
    z_lo, z_bo, z_mo = _sb()
    v0, v1 = S["sb_back"]
    p = box(-80, 80, v0, v1, z_lo, z_mo + 10)
    for (wz0, wz1) in ((z_lo + 30, z_lo + 135), (z_lo + 175, z_mo - 25)):     # lichtgaten
        p = p.cut(box(-32, 32, v0 - 1, v1 + 1, wz0, wz1))
    for dx, dz in _sb_back_bolts():
        p = p.cut(cyl(5.5, V(dx, v0 - 1, z_lo + dz), ALONG_V, 10))
    return to_robot(p)


def _sb_back_bolts():
    b = _zt_bottom()
    z_lo = _sb()[0]
    return [(dx, dz) for dx in (-55, 55) for dz in (60, 145, 260) if b < z_lo + dz]


def sb_back_bolts():
    z_lo = _sb()[0]
    v1 = S["sb_back"][1]
    return to_robot(compound([cyl(8.5, V(dx, v1, z_lo + dz), ALONG_V, 7) for dx, dz in _sb_back_bolts()]))


def sb_plate_lower():
    z_lo = _sb()[0]
    v1, vs = S["sb_back"][1], S["spindle"]
    p = box(-75, 75, v1, vs + 80, z_lo, z_lo + 8).fuse(box(-125, 125, vs - 25, vs + 45, z_lo, z_lo + 8)).removeSplitter()
    p = holes_z(p, [(0, vs)], 25, z_lo, 8)
    p = holes_z(p, _bearing_bolts(), 7, z_lo, 8)
    p = holes_z(p, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 10.5, z_lo, 8)
    return to_robot(p)


def sb_plate_upper():
    z_bo = _sb()[1]
    v1, vs = S["sb_back"][1], S["spindle"]
    p = box(-75, 75, v1, vs + 80, z_bo, z_bo + 6)
    return to_robot(holes_z(holes_z(p, [(0, vs)], 25, z_bo, 6), _bearing_bolts(), 7, z_bo, 6))


def sb_motor_plate():
    z_mo = _sb()[2]
    v1, vs = S["sb_back"][1], S["spindle"]
    p = box(-75, 75, v1, vs + 80, z_mo, z_mo + 8)
    return to_robot(holes_z(holes_z(p, [(0, vs)], 21, z_mo, 8), _bearing_bolts(), 5.5, z_mo, 8))


def sb_side_plate(side):
    z_lo, z_bo, z_mo = _sb()
    v1, vs = S["sb_back"][1], S["spindle"]
    x = side * 78
    p = box(x - 2.5, x + 2.5, v1, vs + 80, z_lo + 8, z_mo)
    p = p.cut(box(x - 4, x + 4, v1 + 28, vs + 55, z_lo + 40, z_bo - 12))
    p = p.cut(box(x - 4, x + 4, v1 + 28, vs + 55, z_bo + 40, z_mo - 22))
    return to_robot(p)


def ucf207(zf):
    """UCF207 vierkant flenslager (as 35): flens op z = zf, huis naar boven."""
    vs = S["spindle"]
    A, J, tf = 117.0, 92.0, 14.0
    fl = box(-A / 2, A / 2, vs - A / 2, vs + A / 2, zf, zf + tf)
    fl = fl.common(cyl(A * 0.64, V(0, vs, zf - 1), UP, tf + 2))
    h = fl.fuse(cyl(42, V(0, vs, zf + tf), UP, 20)).fuse(cyl(27, V(0, vs, zf + tf + 20), UP, 9)).removeSplitter()
    for dx in (-J / 2, J / 2):
        for dv in (-J / 2, J / 2):
            h = h.cut(cyl(7, V(dx, vs + dv, zf - 1), UP, tf + 2))
    return to_robot(h.cut(cyl(P.shaft_d / 2 + 0.3, V(0, vs, zf - 1), UP, tf + 32)))


def bearing_lower():
    return ucf207(_sb()[0] + 8)


def bearing_upper():
    return ucf207(_sb()[1] + 8)


def spindle_shaft():
    return to_robot(cyl(P.shaft_d / 2, V(0, S["spindle"], _zc() + 112), UP, 528))


def _flange_holes(sh, v, z0, t):
    """Steekcirkel O80 met 4x M10 (gereedschapswissel)."""
    for k in range(4):
        a = math.radians(45 + 90 * k)
        sh = sh.cut(cyl(5.5, V(40 * math.cos(a), v + 40 * math.sin(a), z0 - 1), UP, t + 2))
    return sh


def spindle_flange():
    z = _zc() + 100
    return to_robot(_flange_holes(cyl(55, V(0, S["spindle"], z), UP, 12), S["spindle"], z, 12))


def jaw_coupling():
    z = _zc() + 584
    return to_robot(cyl(32.5, V(0, S["spindle"], z), UP, 76).cut(cyl(P.shaft_d / 2, V(0, S["spindle"], z - 1), UP, 57)))


def spindle_motor():
    z_mo = _sb()[2]
    vs = S["spindle"]
    m = box(-55, 55, vs - 55, vs + 55, z_mo + 10, z_mo + 22).fuse(cyl(55, V(0, vs, z_mo + 22), UP, 160))
    m = m.fuse(box(-30, 30, vs + 50, vs + 80, z_mo + 60, z_mo + 120)).fuse(cyl(30, V(0, vs, z_mo + 182), UP, 12))
    return to_robot(m)


def pot_bushes():
    z = _sb()[0] + 8
    vs = S["spindle"]
    return to_robot(compound([pipe(19, 8.5, V(s * P.pot_rod_dx, vs, z), UP, 25) for s in (-1, 1)]))


def _ring_z():
    return _sb()[0] + 8 + 25 + 7


def pot_sensor():
    vs = S["spindle"]
    return to_robot(cyl(6, V(P.pot_rod_dx, vs + 20, _ring_z()), ALONG_V, 20))


def pot_sensor_bracket():
    vs = S["spindle"]
    z0 = _sb()[0] + 8
    return to_robot(box(P.pot_rod_dx - 8, P.pot_rod_dx + 8, vs + 40, vs + 43, z0, _ring_z() + 10))


# ---------------------------------------------------------------------
# Pot (hangt in rust; getekend met de rand op pot_rim_ref())
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
    d = holes_z(cyl(R, V(0, vs, z), UP, 3), [(0, vs)], 25, z, 3)
    return to_robot(holes_z(d, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 8, z, 3))


def pot_rubber_rim():
    R = P.pot_d / 2
    return to_robot(pipe(R + 3, R, V(0, S["spindle"], _rim()), UP, 25))


def pot_flap():
    R = P.pot_d / 2
    z = _rim() + P.pot_h - 60
    p = V(0, S["spindle"], z)
    return to_robot(Part.makeCone(R + 50, R + 3, 50, p, UP).cut(Part.makeCone(R + 47, R, 50, p, UP)))


def shaft_seal():
    return to_robot(pipe(32, 18, V(0, S["spindle"], _rim() + P.pot_h + 3), UP, 8))


def pot_rods():
    z = _rim() + P.pot_h + 3
    vs = S["spindle"]
    return to_robot(compound([cyl(P.pot_rod_d / 2, V(s * P.pot_rod_dx, vs, z), UP, 291) for s in (-1, 1)]))


def pot_set_rings():
    z = _rim() + P.pot_h + 3 + 279
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
    """Strip onder het vaste eind van de kabelrups, op het bovenste profiel."""
    x0 = -P.xbar_L / 2
    tv = S["tube"]
    z0 = P.xbar_z[1] + P.prof_h / 2
    return to_robot(box(x0, x0 + 90, tv - 25, tv + 25, z0, P.chain_z))


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
    """Spiraalkabel van de X-slede naar de Z-slede (rekt mee met de Z-slag)."""
    z_a = SPIRAL_Z0
    z_top = z_tool + P.zt_bottom + P.zt_L + 8
    z_c = max(z_top, z_a + 60)
    n = P.spiral_turns
    pitch = (z_c - z_a) / n
    vs = S["zt"][0] + 15.0
    rings = [Part.makeTorus(22, 4.5, V(x + SPIRAL_X, vs, z_a + pitch * (k + 0.5)), UP) for k in range(n)]
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
