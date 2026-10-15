"""Onderdelen van de dockweed drill v3: een functie per onderdeel, geeft een Part-shape in robotcoordinaten.

Intern wordt getekend in het portaalframe (x, v, z): v = afstand achter de achterkant van de achterste onderbalk
van de robot. to_robot() spiegelt dat naar robot-y (y = robot_beam_rear_face - v).
Bewegende groepen worden in hun referentiestand getekend:
- X-slede op x = 0;
- Z-slede (mast met spil, gereedschap) met de onderkant van het gereedschap op z_ref (rijstand);
- pot hangend onder de spilbok bij z_ref (rand op z_ref - pot_rim).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd3_params as P

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
    s["mast"] = (P.mast_v - P.mast_w / 2, P.mast_v + P.mast_w / 2)
    s["spindle"] = P.mast_v                             # de spilas loopt door de mast
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


# Z-aandrijving en rolkooien (vast op de X-slede)
def _corners():
    """(sx, sv) per hoek van de mast: sx, sv = -1/+1."""
    return [(sx, sv) for sx in (-1, 1) for sv in (-1, 1)]


def _mast_outline(z0, z1, grow=0.0):
    h = P.mast_w / 2 + grow
    return box(-h, h, P.mast_v - h, P.mast_v + h, z0, z1)


def _roller_centre(sx, sv, zc):
    h = P.mast_w / 2
    d = P.roller_c / math.sqrt(2.0)
    return V(sx * (h + d), P.mast_v + sv * (h + d), zc)


def _roller_axis(sx, sv):
    a = V(-sv, sx, 0)                       # loodrecht op de diagonaal, horizontaal
    a.normalize()
    return a


def rollers():
    """8 V-groefrollen op de hoeken van de mast; de groef is de mastomtrek (raakt precies)."""
    out = []
    for zc in P.cage_z:
        for sx, sv in _corners():
            c = _roller_centre(sx, sv, zc)
            ax = _roller_axis(sx, sv)
            r = cyl(P.roller_d / 2, c - ax * (P.roller_w / 2), ax, P.roller_w).cut(cyl(5, c - ax * 20, ax, 40))
            out.append(r.cut(_mast_outline(zc - 30, zc + 30)))
    return to_robot(compound(out))


def roller_axles():
    """As (M10) door elke rol met een blokje naar de kooiplaat."""
    out = []
    for zc in P.cage_z:
        z_plate = zc - P.roller_d / 2 - 2
        for sx, sv in _corners():
            c = _roller_centre(sx, sv, zc)
            ax = _roller_axis(sx, sv)
            pin = cyl(5, c - ax * (P.roller_w / 2 + 12), ax, P.roller_w + 24)
            for s in (-1, 1):
                b = c + ax * (s * (P.roller_w / 2 + 8))
                post = cyl(7, V(b.x, b.y, z_plate), UP, zc - z_plate - 5)
                pin = pin.fuse(post)
            out.append(pin.cut(_mast_outline(zc - 40, zc + 40, 1.0)))
    return to_robot(compound(out))


def cage_plates():
    """2 kooiplaten (8 mm) om de mast, vast tegen de achterkant van de X-slede."""
    out = []
    v1 = S["slide"][1]
    h = P.cage_half_x
    for zc in P.cage_z:
        z1 = zc - P.roller_d / 2 - 2
        pl = box(-h, h, v1, P.mast_v + h, z1 - P.cage_t, z1)
        pl = pl.cut(_mast_outline(z1 - P.cage_t - 1, z1 + 1, 2.0))
        pl = pl.cut(box(-10, 10, S["mast"][0] - P.rack_size - 2, S["mast"][0], z1 - P.cage_t - 1, z1 + 1))
        out.append(pl)
    return to_robot(compound(out))


def _pinion_v():
    return S["mast"][0] - P.rack_size + 2.0 - P.rack_m * P.pinion_z_teeth / 2.0   # steekcirkel raakt de steeklijn


def pinion():
    r = P.rack_m * P.pinion_z_teeth / 2.0
    return to_robot(cyl(r, V(-7.5, _pinion_v(), P.pinion_z), V(1, 0, 0), 15.0))


def worm_shaft():
    return to_robot(cyl(7, V(-70.0, _pinion_v(), P.pinion_z), V(1, 0, 0), 62.5))


def worm_gearbox():
    """NMRV030 i=30 (vereenvoudigd blok), op de achterkant van de X-slede links van de mast."""
    v0 = S["slide"][1] + 5.0
    return to_robot(box(-150, -70, v0, v0 + 75, P.pinion_z - 40, P.pinion_z + 40))


def z_motor():
    """NEMA 23 closed-loop zonder rem op de wormkast, as langs -x."""
    vc = S["slide"][1] + 5.0 + 37.5
    z = P.pinion_z
    return to_robot(box(-262, -150, vc - 28.5, vc + 28.5, z - 28.5, z + 28.5).fuse(
        box(-285, -262, vc - 25, vc + 25, z - 25, z + 25)))


def chain_driver():
    """Meenemer kabelrups (op de X-slede)."""
    xm = -80.0
    tv = S["tube"]
    zk = P.chain_z
    v0, v1 = S["slide"]
    return to_robot(box(xm - 20, xm + 20, tv - 25, v1, zk + 80, zk + 86).fuse(
        box(xm - 20, xm + 20, v0 - 3, v0, P.slide_z[1] - 8, zk + 86)))


SPIRAL_X = P.spiral_x        # naast de mast op +x, boven de X-motor
SPIRAL_Z0 = P.spiral_z0      # onderste anker op de X-slede
SPIRAL_V = 185.0             # tussen de X-slede en de mast


def cable_bracket_x():
    v1 = S["slide"][1]
    return to_robot(box(SPIRAL_X - 20, SPIRAL_X + 20, v1, SPIRAL_V + 15, SPIRAL_Z0 - 8, SPIRAL_Z0))


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
# Z-slede = mast met de spil erin (beweegt in z; getekend bij onderkant gereedschap = z_ref)
# ---------------------------------------------------------------------
def _zc():
    return P.z_ref


def _mb():
    return _zc() + P.mast_bottom


def _mt():
    return _mb() + P.mast_L


def mast():
    h = P.mast_w / 2
    return to_robot(tube_rect(-h, h, S["mast"][0], S["mast"][1], _mb(), _mt(), P.mast_wall, "z"))


def rack():
    """Tandheugel M2 op de voorkant van de mast (getekend tot de steeklijn)."""
    v1 = S["mast"][0]
    return to_robot(box(-7.5, 7.5, v1 - P.rack_size + 2.0, v1, _mb() + 150, _mb() + 720))


def mast_bottom_plate():
    z = _mb()
    vs = S["spindle"]
    p = box(-125, 125, vs - 60, vs + 60, z - 10, z)
    p = holes_z(p, [(0, vs)], 20, z - 10, 10)
    return to_robot(holes_z(p, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 10.5, z - 10, 10))


def mast_top_plate():
    z = _mt()
    vs = S["spindle"]
    p = box(-60, 60, vs - 60, vs + 60, z, z + 10)
    return to_robot(holes_z(p, [(0, vs)], 21, z, 10))


def bearing_cartridge():
    """Lagerpatroon: dikwandige buis O100 met 2 lagers 6207 (O72), gelast onder de bodemplaat."""
    zc = _zc()
    return to_robot(pipe(50, 36, V(0, S["spindle"], zc + P.cart_z[0]), UP, P.mast_bottom - 10 - P.cart_z[0]))


def bearings():
    zc = _zc()
    vs = S["spindle"]
    return to_robot(compound([pipe(36, P.shaft_d / 2, V(0, vs, zc + bz - 8.5), UP, 17) for bz in P.bearing_z]))


def spindle_shaft():
    zc = _zc()
    return to_robot(cyl(P.shaft_d / 2, V(0, S["spindle"], zc + 112), UP, P.mast_bottom + 20 - 112))


def _flange_holes(sh, v, z0, t):
    """Steekcirkel O80 met 4x M10 (gereedschapswissel)."""
    for k in range(4):
        a = math.radians(45 + 90 * k)
        sh = sh.cut(cyl(5.5, V(40 * math.cos(a), v + 40 * math.sin(a), z0 - 1), UP, t + 2))
    return sh


def spindle_flange():
    z = _zc() + 100
    return to_robot(_flange_holes(cyl(55, V(0, S["spindle"], z), UP, 12), S["spindle"], z, 12))


def couplings():
    """Klauwkoppeling onder in de mast (spilas - aandrijfas) en boven (aandrijfas - motor)."""
    vs = S["spindle"]
    lo = _mb() + 10
    hi = _mt() - 60
    c1 = cyl(30, V(0, vs, lo), UP, 50).cut(cyl(P.shaft_d / 2, V(0, vs, lo - 1), UP, 11))
    c2 = cyl(30, V(0, vs, hi), UP, 50)
    return to_robot(compound([c1, c2]))


def drive_shaft():
    vs = S["spindle"]
    d, t = P.drive_shaft
    z0 = _mb() + 60
    return to_robot(pipe(d / 2, d / 2 - t, V(0, vs, z0), UP, _mt() - 60 - z0))


def spindle_motor():
    z0 = _mt() + 10
    vs = S["spindle"]
    m = box(-55, 55, vs - 55, vs + 55, z0, z0 + 12).fuse(cyl(55, V(0, vs, z0 + 12), UP, 160))
    m = m.fuse(box(-30, 30, vs + 50, vs + 80, z0 + 50, z0 + 110)).fuse(cyl(30, V(0, vs, z0 + 172), UP, 12))
    return to_robot(m)


def cable_bracket_z():
    z = _mt() + 10
    return to_robot(box(60, SPIRAL_X + 20, SPIRAL_V - 15, S["spindle"] - 55, z, z + 6))


def pot_bushes():
    z = _mb()
    vs = S["spindle"]
    return to_robot(compound([pipe(19, 8.5, V(s * P.pot_rod_dx, vs, z), UP, 25) for s in (-1, 1)]))


def _ring_z():
    return _mb() + 25 + 1


def pot_sensor():
    vs = S["spindle"]
    return to_robot(cyl(6, V(P.pot_rod_dx, vs + 20, _ring_z() + 6), ALONG_V, 20))


def pot_sensor_bracket():
    vs = S["spindle"]
    return to_robot(box(P.pot_rod_dx - 8, P.pot_rod_dx + 8, vs + 40, vs + 43, _mb(), _ring_z() + 16))


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
    return to_robot(pipe(32, 18, V(0, S["spindle"], _rim() + P.pot_h + P.pot_lid_t), UP, 8))


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
    """Spiraalkabel van de X-slede naar de mastkop (rekt mee met de Z-slag)."""
    z_a = SPIRAL_Z0
    z_top = z_tool + P.mast_bottom + P.mast_L + 10
    z_c = max(z_top, z_a + 60)
    n = P.spiral_turns
    pitch = (z_c - z_a) / n
    rings = [Part.makeTorus(22, 4.5, V(x + SPIRAL_X, SPIRAL_V, z_a + pitch * (k + 0.5)), UP) for k in range(n)]
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
