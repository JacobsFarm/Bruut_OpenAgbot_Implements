"""Onderdelen van de dockweed drill v6: een functie per onderdeel, geeft een Part-shape in robotcoordinaten.

Intern wordt getekend in het portaalframe (x, v, z): v = afstand achter de achterkant van de achterste onderbalk
van de robot. to_robot() spiegelt dat naar robot-y (y = robot_beam_rear_face - v).
Bewegende groepen worden in hun referentiestand getekend:
- X-slede op x = 0 (met de 4 hulzen van de Z-geleiding en het vaste deel van de actuator);
- Z-slede (2 staande aftakasbuizen, juk, stang van de actuator, spilbok, spil) met de onderkant van het gereedschap op z_ref
  (rijstand, actuator ingetrokken);
- pot hangend onder de spilbok bij z_ref (rand op z_ref - pot_rim).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd6_params as P

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

def m12_bolt_v(x, v_head, v_nut, z):
    """M12 langs v: kop aan de achterkant (v_head, naar +v), moer aan de voorkant (v_nut, naar -v)."""
    shank = cyl(P.m12_d / 2.0, V(x, v_nut - P.m10_nut_m - 3.0, z), ALONG_V, v_head - v_nut + P.m10_nut_m + 3.0)
    head = cyl(P.m12_head_r, V(x, v_head, z), ALONG_V, P.m12_head_k)
    nut = cyl(P.m12_head_r, V(x, v_nut - P.m10_nut_m, z), ALONG_V, P.m10_nut_m)
    return shank.fuse(head).fuse(nut)


# ---------------------------------------------------------------------
# Afgeleide maten (v-opbouw van de robot af naar achteren)
# ---------------------------------------------------------------------
def stack():
    s = {}
    s["up"] = (P.up_v0, P.up_v1)
    s["xbeam"] = P.xbeam_v
    s["tube"] = P.tube_v
    s["slide"] = (P.slide_v0, P.slide_v0 + P.slide_t)
    s["belt_ref"] = P.tube_v + 4.0                      # riem en riemklemmen
    s["zg"] = P.zg_v                                    # hart staande aftakasbuizen (Z-geleiding)
    s["act"] = P.act_v                                  # hart actuator
    s["sb_back"] = (P.sb_back_v0, P.sb_back_v0 + P.sb_back_t)
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
    """Staander 40 x 40 x 3 met een M12-gat (langs v) op elke buishoogte voor de dwarsbalken."""
    xc = side * P.hs_x
    h = P.up_size / 2.0
    u = tube_rect(xc - h, xc + h, P.up_v0, P.up_v1, P.up_z0, P.up_z1, P.up_wall, "z")
    for zp in P.xbar_z:
        u = u.cut(cyl(6.5, V(xc, P.up_v0 - 1, zp), ALONG_V, P.up_size + 2))
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
# X-frame (v6): 2 dwarsbalken 40 x 40 x 3 achter de staanders, 2 zijplaten, de aftakasbuizen ertussen
# ---------------------------------------------------------------------
def _inner_x():
    """Binnenkant zijplaat (= eind van de buizen en de dwarsbalken)."""
    return P.xbar_L / 2 - P.end_plate_t


def x_beam(zp):
    """Dwarsbalk op buishoogte zp: van zijplaat tot zijplaat (gelast), M12-gaten bij de staanders."""
    xi = _inner_x()
    h = P.xbeam[0] / 2
    v0, v1 = S["xbeam"]
    b = tube_rect(-xi, xi, v0, v1, zp - h, zp + h, P.xbeam[1], "x")
    for s in (-1, 1):
        b = b.cut(cyl(6.5, V(s * P.hs_x, v0 - 1, zp), ALONG_V, P.xbeam[0] + 2))
    return to_robot(b)


def x_beam_bolts():
    """4x M12 door staander en dwarsbalk (kop achter, moer voor op de staander)."""
    out = [m12_bolt_v(s * P.hs_x, S["xbeam"][1], P.up_v0, zp) for s in (-1, 1) for zp in P.xbar_z]
    return to_robot(compound(out))


def pto_tube(zp):
    xi = _inner_x()
    return to_robot(lemon_x(-xi, xi, S["tube"], zp, P.pto_b, P.pto_h).cut(
        lemon_x(-xi - 1, xi + 1, S["tube"], zp, P.pto_b - 2 * P.pto_t, P.pto_h - 2 * P.pto_t)))


def _tube_bolt_pts():
    return [(zp, zp + dz) for zp in P.xbar_z for dz in (-P.tube_bolt_dz, P.tube_bolt_dz)]


def tube_plugs():
    """Prop (binnenprofiel, gelast) in elk buiseind met 2x M10 getapt (gat getekend op O10)."""
    xi = _inner_x()
    tv = S["tube"]
    out = []
    for s in (-1, 1):
        x0 = xi - P.plug_L if s > 0 else -xi
        for zp in P.xbar_z:
            p = lemon_x(x0, x0 + P.plug_L, tv, zp, P.pto_b - 2 * P.pto_t, P.pto_h - 2 * P.pto_t)
            for z in (zp - P.tube_bolt_dz, zp + P.tube_bolt_dz):
                p = p.cut(cyl(5.0, V(x0 - 1, tv, z), V(1, 0, 0), P.plug_L + 2))
            out.append(p)
    return to_robot(compound(out))


def tube_bolts(side):
    """2x M10 per buiseind van buiten door de zijplaat in de prop (20 mm ingeschroefd)."""
    xi = _inner_x()
    tv = S["tube"]
    out = []
    for zp, z in _tube_bolt_pts():
        shank = cyl(P.m10_d / 2.0, V(xi - 20.0, tv, z), V(1, 0, 0), 20.0 + P.end_plate_t)
        head = cyl(P.m10_head_r, V(xi + P.end_plate_t, tv, z), V(1, 0, 0), P.m10_head_k)
        b = shank.fuse(head)
        if side < 0:
            b = b.mirror(V(0, 0, 0), V(1, 0, 0))
        out.append(b)
    return to_robot(compound(out))


def end_plate(side):
    """Zijplaat 12 mm: dwarsbalken gelast, buizen met 2x M10 per eind los te bouten; lichtgat in het midden."""
    xi = _inner_x()
    x0 = xi if side > 0 else -xi - P.end_plate_t
    tv = S["tube"]
    v0, v1 = P.side_plate_v
    zl, zh = P.xbar_z
    ep = box(x0, x0 + P.end_plate_t, v0, v1, P.side_plate_z[0], P.side_plate_z[1])
    ep = ep.cut(box(x0 - 1, x0 + P.end_plate_t + 1, v0 + 12, tv - 12, zl + 50, zh - 50))
    for zp, z in _tube_bolt_pts():
        ep = ep.cut(cyl(5.5, V(x0 - 1, tv, z), V(1, 0, 0), P.end_plate_t + 2))
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
    """Inductieve eindschakelaar X-min op de linker zijplaat."""
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
    """Hulzen van de buitenbuis, dicht (v6: geen steunribben meer, dus geen sleuf)."""
    out = []
    tv = S["tube"]
    for xh, Lh, zp in sleeve_positions():
        out.append(lemon_ring(xh - Lh / 2, xh + Lh / 2, tv, zp, P.sl_b, P.sl_h, P.sl_b - 2 * P.sl_t, P.sl_h - 2 * P.sl_t))
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
    """M8 in de opzetplaat getapt, kop verzonken in de slede (achterkant vlak voor de zadelblokken van de Z-hulzen)."""
    out = []
    v0 = S["tube"] + P.sl_h / 2 + 2
    v1 = S["slide"][1]
    for xh, Lh, zp in sleeve_positions():
        for (bx, bz) in _pad_bolt_pts(xh, Lh, zp):
            out.append(cyl(4, V(bx, v0, bz), ALONG_V, v1 - v0).fuse(cyl(6.5, V(bx, v1 - 5.5, bz), ALONG_V, 5.5)))
    return to_robot(compound(out))


def scrapers():
    out = []
    tv = S["tube"]
    for xh, Lh, zp in sleeve_positions():
        for xw in (xh - Lh / 2 - P.scraper_t, xh + Lh / 2):
            out.append(lemon_ring(xw, xw + P.scraper_t, tv, zp, P.sl_b + 3, P.sl_h + 3, P.pto_b, P.pto_h))
    return to_robot(compound(out))


def grease_nipples():
    out = []
    for xh, Lh, zp in sleeve_positions():
        out.append(cyl(3.2, V(xh, S["tube"], zp + P.sl_b / 2), UP, 12))
    return to_robot(compound(out))


def x_slide():
    """X-slede alu 10 mm, met een verlengstuk in het midden boven voor de bovenste pen van de actuator.
    Verzonken gaten voor de M8 van de X-hulzen (achterkant vlak), gaten voor de M8 van de zadelblokken (Z-hulzen)."""
    v0, v1 = S["slide"]
    h = P.slide_half_x
    tx0, tx1, tz1 = P.slide_tab
    sl = box(-h, h, v0, v1, P.slide_z[0], P.slide_z[1]).fuse(box(tx0, tx1, v0, v1, P.slide_z[1] - 1, tz1)).removeSplitter()
    sl = sl.cut(cyl(9, V(P.motor_dx, v0 - 1, P.pulley_z), ALONG_V, P.slide_t + 2))
    for (gx, gz) in ((-100, 910), (0, 905)):
        sl = sl.cut(cyl(20, V(gx, v0 - 1, gz), ALONG_V, P.slide_t + 2))
    for xh, Lh, zp in sleeve_positions():
        for (bx, bz) in _pad_bolt_pts(xh, Lh, zp):
            if zp == P.xbar_z[1]:
                sl = sl.cut(cyl(4.5, V(bx, v0 - 1, bz), ALONG_V, P.slide_t + 2))
            else:                                   # onderste huls: sleufgaten (tolerantie in z)
                sl = sl.cut(box(bx - 4.5, bx + 4.5, v0 - 1, v1 + 1, bz - 8, bz + 8))
            sl = sl.cut(cyl(7.0, V(bx, v1 - 5.5, bz), ALONG_V, 6.5))        # verzinking kop
    for (bx, bz) in _zg_bolt_pts():
        sl = sl.cut(cyl(4.5, V(bx, v0 - 1, bz), ALONG_V, P.slide_t + 2))
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


# Z-geleiding: 2 x 2 hulzen (buitenbuis) in zadelblokken op de achterkant van de X-slede
def lemon_z(z0, z1, xc, vc, b, h):
    """Massief citroenprofiel langs z: b = lengte in v (tip tot tip), h = dikte in x."""
    R = (b * b / 4.0 + h * h / 4.0) / h
    d = R - h / 2.0
    c1 = Part.makeCylinder(R, z1 - z0, V(xc + d, vc, z0), UP)
    c2 = Part.makeCylinder(R, z1 - z0, V(xc - d, vc, z0), UP)
    return c1.common(c2)


def lemon_ring_z(z0, z1, xc, vc, bo, ho, bi, hi):
    return lemon_z(z0, z1, xc, vc, bo, ho).cut(lemon_z(z0 - 1, z1 + 1, xc, vc, bi, hi))


def zg_sleeve_positions():
    """(x, z) van de 4 Z-hulzen: links en rechts, op de hoogte van de onderste en bovenste X-buis."""
    return [(s * P.zg_dx, zp) for s in (-1, 1) for zp in P.zg_sleeve_z]


def _zg_bolt_pts():
    """4x M8 per zadelblok, buiten de huls (x hart +- 31), z hart +- 35."""
    return [(xs + dx, zs + dz) for xs, zs in zg_sleeve_positions() for dx in (-31.0, 31.0) for dz in (-35.0, 35.0)]


def z_sleeves():
    v = S["zg"]
    L = P.zg_sleeve_L
    return to_robot(compound([lemon_ring_z(zs - L / 2, zs + L / 2, xs, v, P.sl_b, P.sl_h,
                                           P.sl_b - 2 * P.sl_t, P.sl_h - 2 * P.sl_t) for xs, zs in zg_sleeve_positions()]))


def z_saddles():
    """Zadelblok staal (x hart +- 34, van de slede tot het hart van de huls), om de huls gelast."""
    v1 = S["slide"][1]
    v = S["zg"]
    L = P.zg_sleeve_L
    out = []
    for xs, zs in zg_sleeve_positions():
        b = box(xs - P.zg_pad_half_x, xs + P.zg_pad_half_x, v1, v, zs - L / 2, zs + L / 2)
        b = b.cut(lemon_z(zs - L / 2 - 1, zs + L / 2 + 1, xs, v, P.sl_b, P.sl_h))
        for (bx, bz) in _zg_bolt_pts():
            if abs(bx - xs) < 40 and abs(bz - zs) < 50:
                b = b.cut(cyl(4.5, V(bx, v1 - 1, bz), ALONG_V, v - v1 + 2))
        out.append(b)
    return to_robot(compound(out))


def z_saddle_bolts():
    """M8 van achteren door het zadelblok in de slede (kop op het zadelblok)."""
    v0 = S["slide"][0]
    v = S["zg"]
    return to_robot(compound([cyl(4, V(bx, v0 + 1, bz), ALONG_V, v - v0 - 1).fuse(cyl(6.5, V(bx, v, bz), ALONG_V, 5.5))
                              for bx, bz in _zg_bolt_pts()]))


def z_scrapers():
    v = S["zg"]
    L = P.zg_sleeve_L
    out = []
    for xs, zs in zg_sleeve_positions():
        for z0 in (zs - L / 2 - P.scraper_t, zs + L / 2):
            out.append(lemon_ring_z(z0, z0 + P.scraper_t, xs, v, P.sl_b + 3, P.sl_h + 3, P.pto_b, P.pto_h))
    return to_robot(compound(out))


def z_grease_nipples():
    """Smeernippel op de achterste punt van elke Z-huls (+v, vrij van het zadelblok)."""
    v = S["zg"] + P.sl_b / 2
    return to_robot(compound([cyl(3.2, V(xs, v, zs), ALONG_V, 12) for xs, zs in zg_sleeve_positions()]))


def chain_driver():
    """Meenemer kabelrups (voor op de X-slede)."""
    xm = -80.0
    tv = S["tube"]
    zk = P.chain_z
    v0 = S["slide"][0]
    return to_robot(box(xm - 20, xm + 20, tv - 25, v0, zk + 80, zk + 86).fuse(
        box(xm - 20, xm + 20, v0 - 3, v0, P.slide_z[1] - 8, zk + 86)))


# Actuator Linak LA36 (vast deel op de X-slede): bovenste pen, huis, buitenbuis. Maten uit de datasheet.
def _act_pin_z():
    """Bovenste pen (vast, op het verlengstuk van de slede)."""
    return P.act_pin_z


def _act_eye_z():
    """Stangoog bij z_ref (getekend in de Z-slede): ingetrokken = rijstand."""
    return P.z_ref + P.act_eye_dz


def _act_house_z():
    """(onderkant, bovenkant) van het huis."""
    top = _act_pin_z() - P.act_house_dz
    return top - P.act_house_L, top


def _clevis(xc, vc, zc, v_base, inner, z_lo=-22.0, z_hi=25.0):
    """2 wangen 8 mm (v-z-vlak) van v_base tot achter de pen, pengat langs x; inner = halve binnenmaat."""
    out = []
    for s in (-1, 1):
        x0 = xc + inner if s > 0 else xc - inner - 8.0
        c = box(x0, x0 + 8.0, v_base, vc + 25, zc + z_lo, zc + z_hi)
        out.append(c.cut(cyl(P.act_pin_d / 2, V(x0 - 1, vc, zc), V(1, 0, 0), 10)))
    return out


def act_top_bracket():
    """Bovenste beugel: voetplaat 8 mm op het verlengstuk van de slede + 2 wangen 8 mm om de achterbevestiging."""
    v1 = S["slide"][1]
    zp = _act_pin_z()
    xc = P.act_x
    tx0, tx1, tz1 = P.slide_tab
    base = box(tx0, tx1, v1, v1 + 8, zp - 22, tz1)
    return to_robot(fuse([base] + _clevis(xc, S["act"], zp, v1 + 8, P.act_back_c / 2 + 1.0)))


def act_pin_top():
    zp = _act_pin_z()
    return to_robot(cyl(P.act_pin_d / 2 - 0.1, V(P.act_x - 24, S["act"], zp), V(1, 0, 0), 48))


def act_body():
    """LA36: huis 76 breed, 148 hoog (36 voor / 112 achter het hart), 230 lang; achterbevestiging O25,2;
    buitenbuis 44,5 x 50 tot act_tube_end boven het stangoog (ingetrokken)."""
    xc, vc = P.act_x, S["act"]
    zp = _act_pin_z()
    z0, z1 = _act_house_z()
    w = P.act_house_w / 2
    hf, hb = P.act_house_h
    house = box(xc - w, xc + w, vc - hf, vc + hb, z0, z1)
    lug = cyl(P.act_back_c / 2, V(xc, vc, z1 - 1), UP, zp + 13.0 - z1 + 1)
    lug = lug.cut(cyl(P.act_pin_d / 2, V(xc - 20, vc, zp), V(1, 0, 0), 40))
    tz0 = _act_eye_z() + P.act_tube_end
    tw, tv = P.act_tube
    tube = box(xc - tw / 2, xc + tw / 2, vc - tv / 2, vc + tv / 2, tz0, z0 + 1)
    tube = tube.cut(cyl(P.act_rod_d / 2 + 0.5, V(xc, vc, tz0 - 1), UP, z0 - tz0 + 1))
    return to_robot(fuse([house, lug, tube]))


SPIRAL_X = P.spiral_x        # rechts naast de rechter Z-buis, boven de X-motor
SPIRAL_Z0 = P.spiral_z0      # onderste (vaste) anker op de X-slede


def _spiral_v():
    return S["act"]


def cable_bracket_x():
    """Beugel op de X-slede boven de X-motor: vast anker van de spiraalkabel."""
    v1 = S["slide"][1]
    return to_robot(box(SPIRAL_X - 26, SPIRAL_X + 26, v1, _spiral_v() + 15, SPIRAL_Z0 - 6, SPIRAL_Z0))


# ---------------------------------------------------------------------
# Camera: vast, hoog boven de werkstrook (zoals v5)
# ---------------------------------------------------------------------
def camera_mast():
    x = P.cam_mast_x
    v0 = P.up_v0
    return to_robot(tube_rect(x - 20, x + 20, v0, v0 + 40, P.up_z1 + P.up_cap_t, P.cam_z, 3, "z"))


def camera_arm():
    x = P.cam_mast_x
    v0 = P.up_v0
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
# Z-slede = 2 staande aftakasbuizen met juk, spilbok, spil en motor (beweegt in z; getekend bij z_ref)
# ---------------------------------------------------------------------
def _zc():
    return P.z_ref


def _zg_z():
    """(onderkant, bovenkant) van de staande aftakasbuizen bij z_ref."""
    return _zc() + P.zg_bottom, _zc() + P.zg_top


def z_guide_tube(side):
    """Staande aftakasbuis (binnenbuis 49 x 39,5 x 4,5, b in v): glijdt met de Z-slede door de 2 hulzen."""
    z0, z1 = _zg_z()
    xs = side * P.zg_dx
    return to_robot(lemon_ring_z(z0, z1, xs, S["zg"], P.pto_b, P.pto_h, P.pto_b - 2 * P.pto_t, P.pto_h - 2 * P.pto_t))


def _zg_plug_bolt_pts():
    return [(s * P.zg_dx, S["zg"] + dv) for s in (-1, 1) for dv in (-P.tube_bolt_dz - 2.0, P.tube_bolt_dz + 2.0)]


def z_tube_plugs():
    """Prop (binnenprofiel, 25 mm, gelast) onderin elke buis, 2x M10 getapt (van onder door het juk)."""
    z0 = _zg_z()[0]
    out = []
    for s in (-1, 1):
        p = lemon_z(z0, z0 + P.plug_L, s * P.zg_dx, S["zg"], P.pto_b - 2 * P.pto_t, P.pto_h - 2 * P.pto_t)
        out.append(holes_z(p, [pt for pt in _zg_plug_bolt_pts() if pt[0] * s > 0], 5.0, z0, P.plug_L))
    return to_robot(compound(out))


def z_yoke():
    """Onderjuk 10 mm onder de buizen, van de buizen tot de achterplaat van de spilbok (gelast)."""
    z0 = _zg_z()[0]
    w = P.zg_yoke_half_x
    p = box(-w, w, S["zg"] - P.pto_b / 2 - 6, S["sb_back"][0], z0 - P.zg_yoke_t, z0)
    return to_robot(holes_z(p, _zg_plug_bolt_pts(), 5.5, z0 - P.zg_yoke_t, P.zg_yoke_t))


def z_yoke_bolts():
    z0 = _zg_z()[0] - P.zg_yoke_t
    out = []
    for (x, v) in _zg_plug_bolt_pts():
        out.append(cyl(P.m10_d / 2, V(x, v, z0), UP, P.zg_yoke_t + 20).fuse(
            cyl(P.m10_head_r, V(x, v, z0 - P.m10_head_k), UP, P.m10_head_k)))
    return to_robot(compound(out))


def z_clamp_plate():
    """Klemplaat 10 mm 60 mm boven het juk: citroengaten om de buizen (gelast aan buis en achterplaat)."""
    z0 = _zc() + P.zg_clamp_z
    w = P.zg_yoke_half_x
    p = box(-w, w, S["zg"] - P.pto_b / 2 - 6, S["sb_back"][0], z0, z0 + P.zg_yoke_t)
    for s in (-1, 1):
        p = p.cut(lemon_z(z0 - 1, z0 + P.zg_yoke_t + 1, s * P.zg_dx, S["zg"], P.pto_b, P.pto_h))
    p = p.cut(box(-22, 22, S["zg"] - P.pto_b / 2 - 7, S["zg"] + 6, z0 - 1, z0 + P.zg_yoke_t + 1))   # lichtgat
    return to_robot(p)


def act_eye_bracket():
    """Beugel op de achterplaat van de spilbok (x 0): bodem 8 mm + 2 wangen 8 mm om het stangoog."""
    xc, vc = P.act_x, S["act"]
    ze = _act_eye_z()
    inner = P.act_eye_c / 2 + 1.0
    v0, v1 = vc - 22, S["sb_back"][0]
    bottom = box(xc - inner - 8, xc + inner + 8, v0, v1, ze - 38, ze - 30)
    cheeks = []
    for x0 in (xc - inner - 8, xc + inner):
        c = box(x0, x0 + 8, v0, v1, ze - 30, ze + 18)
        cheeks.append(c.cut(cyl(P.act_pin_d / 2, V(x0 - 1, vc, ze), V(1, 0, 0), 10)))
    return to_robot(fuse([bottom] + cheeks))


def act_rod():
    """Binnenbuis met massief stangoog O27,8 (gat 13,5 van het eind); getekend ingetrokken (rijstand)."""
    xc, vc = P.act_x, S["act"]
    ze = _act_eye_z()
    top = _act_house_z()[0] - 2.0
    eye = cyl(P.act_eye_c / 2, V(xc, vc, ze - 13.5), UP, 30.0)
    eye = eye.cut(cyl(P.act_pin_d / 2, V(xc - 20, vc, ze), V(1, 0, 0), 40))
    rod = cyl(P.act_rod_d / 2, V(xc, vc, ze + 16.0), UP, top - ze - 16.0)
    return to_robot(rod.fuse(eye).removeSplitter())


def act_pin_eye():
    return to_robot(cyl(P.act_pin_d / 2 - 0.1, V(P.act_x - 26, S["act"], _act_eye_z()), V(1, 0, 0), 52))


def _sb():
    """(onderste plaat, bovenplaat) in z bij z_ref."""
    zc = _zc()
    return zc + P.sb_lo, zc + P.sb_mo


def _bearing_z():
    zc = _zc()
    return zc + P.bearing_lo, zc + P.bearing_hi


def _sb_rear_v():
    """Zijplaten en het brede deel van de bovenplaat stoppen hier: daarachter lopen de stangen van de bus."""
    return S["spindle"] - 22.0


def sb_back_plate():
    """Achterplaat van de spilbok (6 mm); onderjuk, klemplaat en de beugel van het stangoog zijn ertegen gelast."""
    z_lo, z_mo = _sb()
    v0, v1 = S["sb_back"]
    p = box(-80, 80, v0, v1, z_lo, _zc() + P.sb_back_top)
    for (wz0, wz1) in ((z_lo + 95, z_lo + 120), (z_lo + 200, z_lo + 280)):     # lichtgaten (vrij van juk en beugel)
        p = p.cut(box(-32, 32, v0 - 1, v1 + 1, wz0, wz1))
    return to_robot(p)


def sb_plate_lower():
    z_lo = _sb()[0]
    v1, vs = S["sb_back"][1], S["spindle"]
    w = P.sb_side_x + 2.5
    p = box(-w, w, v1, vs + 80, z_lo, z_lo + 8).fuse(box(-125, 125, vs - 25, vs + 45, z_lo, z_lo + 8)).removeSplitter()
    p = holes_z(p, [(0, vs)], 25, z_lo, 8)
    p = holes_z(p, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 10.5, z_lo, 8)
    return to_robot(p)


def sb_top_plate():
    """Bovenplaat boven het bovenste lager; achterste deel smaller (de stelringen van de bus komen hier langs)."""
    z_mo = _sb()[1]
    v1, vs, vr = S["sb_back"][1], S["spindle"], _sb_rear_v()
    w = P.sb_side_x + 2.5
    p = box(-w, w, v1, vr, z_mo, z_mo + 8).fuse(box(-84, 84, vr - 1, vs + 80, z_mo, z_mo + 8)).removeSplitter()
    return to_robot(holes_z(p, [(0, vs)], P.shaft_d / 2 + 2, z_mo, 8))


def sb_side_plate(side):
    z_lo, z_mo = _sb()
    x = side * P.sb_side_x
    return to_robot(box(x - 2.5, x + 2.5, S["sb_back"][1], _sb_rear_v(), z_lo + 8, z_mo))


def _bearing_plate_v():
    vb = S["spindle"] - P.ucp_h
    return vb - P.bearing_plate_t, vb


def sb_bearing_plate():
    """Staande lagerplaat tussen de zijplaten: voeten van de 2 UCP 206 ertegen (M14, sleufgaten in z)."""
    z_lo, z_mo = _sb()
    v0, v1 = _bearing_plate_v()
    w = P.sb_side_x - 2.5
    p = box(-w, w, v0, v1, z_lo + 8, z_mo)
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            p = p.cut(box(dx - 7.5, dx + 7.5, v0 - 1, v1 + 1, zb - 10.5, zb + 10.5))
    return to_robot(p)


def ucp(zb):
    """UCP staand lagerblok: voet tegen de lagerplaat (v), as verticaal op z = zb."""
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
    inner = cyl(P.ucp_d / 2 + 7, V(0, vs, zb - P.ucp_ring_w / 2), UP, P.ucp_ring_w)
    h = foot.fuse(body).fuse(ring).fuse(inner).removeSplitter()
    return to_robot(h.cut(cyl(P.ucp_d / 2, V(0, vs, zb - b), UP, 2 * b)))


def bearing_lower():
    return ucp(_bearing_z()[0])


def bearing_upper():
    return ucp(_bearing_z()[1])


def bearing_bolts():
    """4x M14 door de lagerplaat (moer aan de voorkant)."""
    v0, v1 = _bearing_plate_v()
    vt = v1 + P.ucp_foot_t
    out = []
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            out.append(cyl(7, V(dx, v0 - 12, zb), ALONG_V, vt - v0 + 20).fuse(cyl(11.5, V(dx, vt, zb), ALONG_V, 8.8)).fuse(
                cyl(11.5, V(dx, v0 - 11, zb), ALONG_V, 11)))
    return to_robot(compound(out))


def spindle_shaft():
    """Spilas O30 C45 massief: van de spilflens (ingelast) door beide lagers tot in de klauwkoppeling."""
    z0 = _zc() + 100
    return to_robot(cyl(P.shaft_d / 2, V(0, S["spindle"], z0), UP, _zc() + P.shaft_top - z0))


def _flange_holes(sh, v, z0, t):
    """Steekcirkel O80 met 4x M10 (gereedschapswissel)."""
    for k in range(4):
        a = math.radians(45 + 90 * k)
        sh = sh.cut(cyl(5.5, V(40 * math.cos(a), v + 40 * math.sin(a), z0 - 1), UP, t + 2))
    return sh


def spindle_flange():
    """Spilflens O110 x 12, om de as gelast."""
    z = _zc() + 100
    vs = S["spindle"]
    f = cyl(55, V(0, vs, z), UP, 12).cut(cyl(P.shaft_d / 2, V(0, vs, z - 1), UP, 14))
    return to_robot(_flange_holes(f, vs, z, 12))


# Aandrijving spil: 800 W tandwielmotor recht boven de spil (as omlaag), flexibele klauwkoppeling O19 / O30
def jaw_coupling():
    """Klauwkoppeling: 2 naven met klauwen en een elastische ster (getekend als 3 schijven), boring 30 onder, 19 boven."""
    vs = S["spindle"]
    z0 = _zc() + P.jaw_z0
    r = P.jaw_d / 2
    hub = P.jaw_hub_L
    lo = pipe(r, P.shaft_d / 2, V(0, vs, z0), UP, hub)
    star = pipe(r - 1.5, 6.0, V(0, vs, z0 + hub), UP, P.jaw_star)
    hi = pipe(r, P.motor_shaft_d / 2, V(0, vs, z0 + hub + P.jaw_star), UP, hub)
    return to_robot(compound([lo, star, hi]))


def _motor_z(d):
    """z op afstand d langs de motoras vanaf het einde van de uitgaande as (as wijst omlaag)."""
    return _zc() + P.motor_shaft_end + d


def spindle_motor():
    """800 W tandwielmotor met voet (maattekening parts/800 watt motor), op de spilas, voet naar +x."""
    vs = S["spindle"]
    zs = _motor_z(0)
    d0, d1, da, db = P.motor_nose
    parts = [Part.makeCone(da / 2, db / 2, d1 - d0, V(0, vs, zs + d0), UP)]
    for (a, b, dia) in (P.motor_ring, P.motor_body, P.motor_cap):
        parts.append(cyl(dia / 2, V(0, vs, zs + a), UP, b - a))
    xf = P.motor_foot_h
    za, zb = _motor_z(P.motor_foot[0]), _motor_z(P.motor_foot[1])
    foot = box(xf - P.motor_foot_t, xf, vs - P.motor_foot_w / 2, vs + P.motor_foot_w / 2, za, zb)
    for d in P.motor_foot_holes:
        for dv in (-P.motor_foot_hole_dx / 2, P.motor_foot_hole_dx / 2):
            foot = foot.cut(cyl(4.25, V(xf - P.motor_foot_t - 1, vs + dv, _motor_z(d)), V(1, 0, 0), P.motor_foot_t + 2))
    saddle = box(40, xf - P.motor_foot_t + 1, vs - 30, vs + 30, za + 8, zb - 8)
    parts += [foot, saddle]
    return to_robot(fuse(parts))


def spindle_motor_shaft():
    """Uitgaande as O19 h6 van de motor, 35 mm uit de neus (omlaag), in de bovenste naaf van de koppeling."""
    zs = _motor_z(0)
    return to_robot(cyl(P.motor_shaft_d / 2, V(0, S["spindle"], zs), UP, P.motor_shaft_out))


def motor_plate():
    """Staande motorplaat 10 mm (v-z-vlak) op de bovenplaat; 4x M8 voor de motorvoet (sleufgaten in z: uitlijnen)."""
    vs = S["spindle"]
    z0 = _sb()[1] + 8
    x0 = P.motor_foot_h
    v0, v1 = vs + P.motor_plate_v[0], vs + P.motor_plate_v[1]
    p = box(x0, x0 + P.motor_plate_t, v0, v1, z0, _motor_z(P.motor_foot[1]) + 12)
    for d in P.motor_foot_holes:
        for dv in (-P.motor_foot_hole_dx / 2, P.motor_foot_hole_dx / 2):
            z = _motor_z(d)
            p = p.cut(box(x0 - 1, x0 + P.motor_plate_t + 1, vs + dv - 4.25, vs + dv + 4.25, z - 7, z + 7))
    return to_robot(p)


def motor_gussets():
    """2 schoren 6 mm (x-z-vlak) tussen motorplaat en bovenplaat, buiten de motor."""
    vs = S["spindle"]
    z0 = _sb()[1] + 8
    x1 = P.motor_foot_h
    out = []
    for v in (vs + P.motor_plate_v[0], vs + P.motor_plate_v[1] - P.gusset_mp_t):
        pts = [V(x1, v, z0), V(x1, v, z0 + 95), V(x1 - 60, v, z0)]
        out.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, P.gusset_mp_t, 0)))
    return to_robot(compound(out))


def cable_bracket_z():
    """Kapje met arm boven op de rechter Z-buis: bewegend anker van de spiraalkabel."""
    z1 = _zg_z()[1]
    v = _spiral_v()
    return to_robot(box(P.zg_dx - 22, SPIRAL_X + 26, min(S["zg"] - P.pto_b / 2, v - 15), v + 15, z1, z1 + 6))


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
    return to_robot(pipe(28, P.shaft_d / 2 + 0.5, V(0, S["spindle"], _rim() + P.pot_h + P.pot_lid_t), UP, 8))


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
    """Spiraalkabel van de beugel op de X-slede (vast) omhoog naar het kapje op de rechter Z-buis (beweegt)."""
    z_a = SPIRAL_Z0
    z_c = z_tool + P.zg_top
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
