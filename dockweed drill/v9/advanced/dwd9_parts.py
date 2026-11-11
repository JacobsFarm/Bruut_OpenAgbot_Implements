"""Onderdelen van de dockweed drill v9: een functie per onderdeel, geeft een Part-shape in robotcoordinaten.

v9 = proces, spilbok, spil, bus en LA36 van v8, maar X- en Z-geleiding op skeelerwielen O80 x 24 in UPE 100.
Intern wordt getekend in het portaalframe (x, v, z): v = afstand achter de achterkant van de achterste onderbalk
van de robot. to_robot() spiegelt dat naar robot-y (y = robot_beam_rear_face - v).
Het wielblok wordt getekend in het lokale frame van zijn profiel (u langs het profiel, s dwars over de opening met
+s naar de slede, d vanaf de binnenkant van het lijf) en met een rotatie op zijn plaats gezet (_block_frames).
Bewegende groepen worden in hun referentiestand getekend:
- X-slede op x = 0 (4 X-wielblokken, 4 Z-wielblokken, riemklem en het vaste deel van de actuator);
- Z-slede (2 UPE 100, juk, stang van de actuator, spilbok, spil) met de onderkant van het gereedschap op z_ref
  (rijstand, actuator ingetrokken);
- pot hangend onder de spilbok bij z_ref (rand op z_ref - pot_rim).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd9_params as P

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


def bolt_v(x, v_head, v_nut, z, d, head_r, head_k, nut_m):
    """Bout langs v: kop aan de achterkant (v_head, naar +v), moer aan de voorkant (v_nut, naar -v)."""
    shank = cyl(d / 2.0, V(x, v_nut - nut_m - 3.0, z), ALONG_V, v_head - v_nut + nut_m + 3.0)
    head = cyl(head_r, V(x, v_head, z), ALONG_V, head_k)
    nut = cyl(head_r, V(x, v_nut - nut_m, z), ALONG_V, nut_m)
    return shank.fuse(head).fuse(nut)


# ---------------------------------------------------------------------
# Afgeleide maten (v-opbouw van de robot af naar achteren)
# ---------------------------------------------------------------------
def stack():
    s = {}
    s["up"] = (P.up_v0, P.up_v1)
    s["xch"] = P.xch_v                                  # midden X-profielen (v 48..148)
    s["slide"] = (P.slide_v0, P.slide_v0 + P.slide_t)  # X-slede
    s["zch"] = P.zch_v                                  # midden Z-profielen (v 190..290)
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
# Aanbouwbok (vast aan de robot), side = -1 links / +1 rechts (zoals v6)
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
    """Staander 40 x 40 x 3 met 2 gaten M8 (langs v) per X-profiel: verzonken bouten door de voorflens."""
    xc = side * P.hs_x
    h = P.up_size / 2.0
    u = tube_rect(xc - h, xc + h, P.up_v0, P.up_v1, P.up_z0, P.up_z1, P.up_wall, "z")
    for (x, z) in _xch_bolt_pts(side):
        u = u.cut(cyl(4.5, V(x, P.up_v0 - 1, z), ALONG_V, P.up_size + 2))
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
# X-frame (v9): 2 UPE 100 met de openingen naar elkaar toe, aan de uiteinden gelast aan 2 eindplaten 10 mm.
# De voorflens ligt tegen de achterkant van de staanders: 2x M8 verzonken per kruising.
# ---------------------------------------------------------------------
def _inner_x():
    """Binnenkant eindplaat (= eind van de profielen)."""
    return P.xbar_L / 2 - P.end_plate_t


def _xch_v():
    return P.xch_v - P.ch_h / 2, P.xch_v + P.ch_h / 2


def _xch_bolt_pts_lvl(lvl):
    zw = P.xch_web_z[lvl]
    z = zw + P.xch_bolt_d if lvl == 0 else zw - P.xch_bolt_d
    return [(s * P.hs_x + dx, z) for s in (-1, 1) for dx in (-P.xch_bolt_dx, P.xch_bolt_dx)]


def _xch_bolt_pts(side):
    return [(x, z) for lvl in (0, 1) for x, z in _xch_bolt_pts_lvl(lvl) if x * side > 0]


def _csk(x, v_face, z):
    """Verzinking M8 (DIN 7991): kegel O8 -> O16 over 4 mm, de grote kant op v_face (wielzijde)."""
    return Part.makeCone(4.0, 8.0, 4.0, V(x, v_face - 4.0, z), ALONG_V)


def x_channel(lvl):
    """UPE 100 van eindplaat tot eindplaat. lvl 0 = onder (open naar boven), 1 = boven (open naar beneden).
    Verzonken M8-gaten in de voorflens bij de staanders; onderste profiel: afwateringsgaten O10 in het lijf."""
    xi = _inner_x()
    v0, v1 = _xch_v()
    zw = P.xch_web_z[lvl]
    sg = 1.0 if lvl == 0 else -1.0

    def zr(d0, d1):
        a, b = zw + sg * d0, zw + sg * d1
        return min(a, b), max(a, b)

    web = box(-xi, xi, v0, v1, *zr(-P.ch_tw, 0.0))
    ff = box(-xi, xi, v0, v0 + P.ch_tf, *zr(-P.ch_tw, P.ch_depth))
    rf = box(-xi, xi, v1 - P.ch_tf, v1, *zr(-P.ch_tw, P.ch_depth))
    c = fuse([web, ff, rf])
    for x, z in _xch_bolt_pts_lvl(lvl):
        c = c.cut(cyl(4.5, V(x, v0 - 1, z), ALONG_V, P.ch_tf + 2))
        c = c.cut(_csk(x, v0 + P.ch_tf, z))
        c = c.cut(cyl(8.0, V(x, v0 + P.ch_tf, z), ALONG_V, 1.0))
    if lvl == 0:
        pitch = P.xch_drain_pitch
        n = int(2 * (xi - 100.0) // pitch) + 1
        x0 = -(n - 1) * pitch / 2
        for k in range(n):
            for s in (-1, 1):
                c = c.cut(cyl(5.0, V(x0 + k * pitch, P.xch_v + s * P.xch_drain_s, zw - P.ch_tw - 1), UP, P.ch_tw + 2))
    return to_robot(c)


def x_channel_bolts():
    """8x M8 DIN 7991: kop vlak in de voorflens (aan de wielkant), door de staander, moer voor op de staander."""
    v_in = _xch_v()[0] + P.ch_tf
    out = []
    for lvl in (0, 1):
        for x, z in _xch_bolt_pts_lvl(lvl):
            head = _csk(x, v_in, z)
            shank = cyl(4.0, V(x, P.up_v0 - 9.0, z), ALONG_V, v_in - 4.0 - P.up_v0 + 9.0)
            nut = cyl(6.5, V(x, P.up_v0 - 6.5, z), ALONG_V, 6.5)
            out.append(fuse([head, shank, nut]))
    return to_robot(compound(out))


def x_end_plate(side):
    """Eindplaat 10 mm, gelast aan beide profieleinden; reikt tot achter de slede (eindschakelaar / aanslag)."""
    xi = _inner_x()
    t = P.end_plate_t
    x0 = xi if side > 0 else -xi - t
    v0, v1 = P.end_plate_v
    p = box(x0, x0 + t, v0, v1, P.end_plate_z0, P.xch_web_z[1] + P.ch_tw)
    p = p.cut(box(x0 - 1, x0 + t + 1, 65.0, 135.0, 775.0, 855.0))           # lichtgat
    if side < 0:
        lv, lz = P.limit_vz
        p = p.cut(cyl(6.0, V(x0 - 1, lv, lz), V(1, 0, 0), t + 2))
    return to_robot(p)


def drive_bracket(side):
    """Beugelplaat 10 mm (vlak normaal v) aan de eindplaat gelast: rechts de 5:1-kast van de X-motor (gat voor de
    uitgaande as), links de spanpoelie (sleuf langs x voor het spannen van de riem)."""
    xi = _inner_x()
    v0, v1 = P.drive_bracket_v
    xa, xb = sorted((side * (xi - 75.0), side * xi))
    z = P.belt_z
    p = box(xa, xb, v0, v1, z - 45.0, z + 45.0)
    px = side * P.pulley_x
    if side > 0:
        p = p.cut(cyl(9.0, V(px, v0 - 1, z), ALONG_V, v1 - v0 + 2))
    else:
        p = p.cut(box(px - 15.0, px + 15.0, v0 - 1, v1 + 1, z - 5.0, z + 5.0))
    return to_robot(p)


def x_gearbox():
    """Planetaire kast 5:1 (60 x 60) voor op de rechter beugelplaat."""
    xm, z = P.pulley_x, P.belt_z
    v0 = P.drive_bracket_v[0]
    return to_robot(box(xm - 30, xm + 30, v0 - 55, v0, z - 30, z + 30))


def x_motor():
    """NEMA 23 closed-loop (vast, de kabel beweegt niet mee)."""
    xm, z = P.pulley_x, P.belt_z
    v0 = P.drive_bracket_v[0] - 55
    return to_robot(box(xm - 28.5, xm + 28.5, v0 - 112, v0, z - 28.5, z + 28.5).fuse(
        box(xm - 25, xm + 25, v0 - 135, v0 - 112, z - 25, z + 25)))


def x_pulleys():
    """2 poelies HTD5M 20T met flenzen: rechts op de uitgaande as van de kast, links de spanpoelie."""
    v0, v1 = P.belt_v
    z = P.belt_z
    out = []
    for s, bore in ((1, 7.0), (-1, 5.0)):
        px = s * P.pulley_x
        p = fuse([cyl(P.pulley_r, V(px, v0, z), ALONG_V, v1 - v0), cyl(20.0, V(px, v0 - 2, z), ALONG_V, 2),
                  cyl(20.0, V(px, v1, z), ALONG_V, 2)])
        out.append(p.cut(cyl(bore, V(px, v0 - 3, z), ALONG_V, v1 - v0 + 6)))
    return to_robot(compound(out))


def x_pulley_shafts():
    """Rechts: uitgaande as O14 van de kast door de beugel; links: M10 als as in de sleuf, met afstandsbus en moer."""
    v0, v1 = P.drive_bracket_v
    z = P.belt_z
    px = P.pulley_x
    right = cyl(7.0, V(px, v0, z), ALONG_V, P.belt_v[1] + 2 - v0)
    left = fuse([cyl(5.0, V(-px, v0 - 6, z), ALONG_V, P.belt_v[1] + 10 - v0 + 6), cyl(8.0, V(-px, v0 - 6, z), ALONG_V, 6),
                 cyl(8.0, V(-px, P.belt_v[1] + 2, z), ALONG_V, 8)])
    spacer = pipe(8.0, 5.0, V(-px, v1, z), ALONG_V, P.belt_v[0] - 2 - v1)
    return to_robot(compound([right, left, spacer]))


def belt_upper():
    """Bovenste riempart van poelie tot poelie, met de 2 halve omslagen (vast)."""
    px = P.pulley_x
    v0, v1 = P.belt_v
    z = P.belt_z
    r0, r1 = P.belt_r
    parts = [box(-px, px, v0, v1, z + r0, z + r1)]
    for s in (-1, 1):
        ring = pipe(r1, r0, V(s * px, v0, z), ALONG_V, v1 - v0)
        xa, xb = (px, px + 30) if s > 0 else (-px - 30, -px)
        parts.append(ring.common(box(xa, xb, v0 - 1, v1 + 1, z - 30, z + 30)))
    return to_robot(fuse(parts))


def belt_lower(x):
    """Onderste riempart van de linker poelie tot de klem en van de klem tot de rechter poelie (slede op x)."""
    px = P.pulley_x
    v0, v1 = P.belt_v
    z0, z1 = P.belt_z - P.belt_r[1], P.belt_z - P.belt_r[0]
    return to_robot(compound([box(-px, x - 30, v0, v1, z0, z1), box(x + 30, px, v0, v1, z0, z1)]))


def limit_switch():
    """Inductieve eindschakelaar M12 X-min in de linker eindplaat, ziet de rand van de slede."""
    xi = _inner_x()
    lv, lz = P.limit_vz
    return to_robot(cyl(6, V(-xi - P.end_plate_t - 18, lv, lz), V(1, 0, 0), 18 + P.end_plate_t))


def end_stop():
    """Rubberen aanslag X-max op de rechter eindplaat (1 mm vrij van de slede bij x_max)."""
    lv, lz = P.limit_vz
    return to_robot(cyl(10, V(_inner_x(), lv, lz), V(-1, 0, 0), 4))


def chain_bracket():
    """Steunplaat 6 mm boven op het linker eind van het bovenste X-profiel, vast eind van de kabelrups."""
    x0 = -P.xbar_L / 2
    tv = S["xch"]
    z0 = P.xch_web_z[1] + P.ch_tw
    return to_robot(box(x0, x0 + 90, tv - 25, tv + 25, z0, P.chain_z))


# ---------------------------------------------------------------------
# Wielblok (8x, zelfde blok op X en Z): L-beugel staal 10 mm met 2 flenswielen en 2 lijfwielen (skeelerwiel O80 x 24)
# Getekend in het lokale frame (u, s, d) van zijn profiel: u -> X, s -> Y, d -> Z; _to_frame zet het op zijn plaats.
# ---------------------------------------------------------------------
LU, LS, LD = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def _lbox(u0, u1, s0, s1, d0, d1):
    return Part.makeBox(u1 - u0, s1 - s0, d1 - d0, V(u0, s0, d0))


def block_frames():
    """(naam, oorsprong, U, S, D) van de 8 wielblokken in het portaalframe bij x = 0 (X-slede). Oorsprong = binnenkant
    lijf op de as van het profiel; U langs het profiel, S naar de slede, D van het lijf naar de opening. Alle
    rotaties zijn rechtshandig (det +1)."""
    out = []
    for i, xb in enumerate((-P.xblk_x, P.xblk_x)):
        out.append(("x_lower_%d" % i, V(xb, P.xch_v, P.xch_web_z[0]), V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)))
        out.append(("x_upper_%d" % i, V(xb, P.xch_v, P.xch_web_z[1]), V(-1, 0, 0), V(0, 1, 0), V(0, 0, -1)))
    for i, zb in enumerate(P.zblk_z):
        out.append(("z_left_%d" % i, V(-P.zch_x, P.zch_v, zb), V(0, 0, 1), V(0, -1, 0), V(1, 0, 0)))
        out.append(("z_right_%d" % i, V(P.zch_x, P.zch_v, zb), V(0, 0, -1), V(0, -1, 0), V(-1, 0, 0)))
    return out


def _to_frame(shape, f):
    _, o, U, Sv, D = f
    m = App.Matrix(U.x, Sv.x, D.x, o.x, U.y, Sv.y, D.y, o.y, U.z, Sv.z, D.z, o.z, 0, 0, 0, 1)
    s = shape.copy()
    s.transformShape(m)
    return s


def _pt(f, u, s, d):
    _, o, U, Sv, D = f
    return o + U * u + Sv * s + D * d


def _fw_pos():
    """(u, s) van de 2 flenswielen: -u tegen de +s-flens, +u tegen de -s-flens (samen spelingvrij in s)."""
    return [(-P.fw_u, P.fw_s), (P.fw_u, -P.fw_s)]


def _ww_pos():
    return [(0.0, -P.ww_s), (0.0, P.ww_s)]


def _block_plate_local():
    """Bodemplaat (boven de flenspunten, venster voor de lijfwielen, sleufgaten in s voor de assen van de flenswielen),
    montageflens (sleufgaten in d voor 4x M8) en 2 oren 5 mm voor de as van de lijfwielen; gelast."""
    t = P.blk_t
    hu = P.blk_half_u
    d0 = P.blk_d0
    base = _lbox(-hu, hu, P.blk_s0, P.blk_flange_s + t, d0, d0 + t)
    flange = _lbox(-hu, hu, P.blk_flange_s, P.blk_flange_s + t, d0, P.blk_flange_d1)
    e0, e1 = P.ear_s
    ears = [_lbox(-P.ear_half_u, P.ear_half_u, a, b, P.ww_d - 12.0, d0) for a, b in ((e0, e1), (-e1, -e0))]
    p = fuse([base, flange] + ears)
    p = p.cut(_lbox(-P.win_half_u, P.win_half_u, -P.win_half_s, P.win_half_s, d0 - 1, d0 + t + 1))
    for u, s in _fw_pos():
        p = p.cut(_lbox(u - 4.5, u + 4.5, s - P.fw_slot - 4.5, s + P.fw_slot + 4.5, d0 - 1, d0 + t + 1))
    p = p.cut(cyl(4.5, V(0, -e1 - 1, P.ww_d), LS, 2 * e1 + 2))
    for u, d in P.blk_bolt:
        p = p.cut(_lbox(u - 4.5, u + 4.5, P.blk_flange_s - 1, P.blk_flange_s + t + 1, d - 9.5, d + 9.5))
    return p


def _wheel_local(c, axis):
    """Skeelerwiel O80 x 24: (PU-loopvlak met afgeronde randen, kern met 2x 608)."""
    w = P.wheel_w
    R = P.wheel_d / 2
    p0 = c - axis * (w / 2)
    tire = cyl(R, p0, axis, w)
    edges = [e for e in tire.Edges if isinstance(e.Curve, Part.Circle)]
    tire = tire.makeFillet(P.wheel_edge_r, edges)
    tire = tire.cut(cyl(P.wheel_hub_d / 2, p0 - axis, axis, w + 2))
    hub = pipe(P.wheel_hub_d / 2, P.wheel_bore / 2, p0, axis, w)
    return tire, hub


def _block_wheels_local():
    tires, hubs = [], []
    for u, s in _fw_pos():
        t, h = _wheel_local(V(u, s, P.fw_d), LD)
        tires.append(t)
        hubs.append(h)
    for u, s in _ww_pos():
        t, h = _wheel_local(V(u, s, P.ww_d), LS)
        tires.append(t)
        hubs.append(h)
    return tires, hubs


def _block_bolts_local():
    """M8 als as (8.8): flenswielen van onderen (kop bij het lijf, afstandsbus, moer op de bodemplaat); lijfwielen
    1 bout door beide oren met tussenbus; montage 4x M8 door de sleuven in de slede (Helicoil)."""
    out = []
    t = P.blk_t
    d0 = P.blk_d0
    w = P.wheel_w
    dw0 = P.fw_d - w / 2                                # onderkant flenswiel (14)
    for u, s in _fw_pos():
        out.append(cyl(6.5, V(u, s, dw0 - 5.3), LD, 5.3))
        out.append(cyl(4.0, V(u, s, dw0), LD, d0 + t + 8.5 - dw0))
        out.append(pipe(7.0, 4.0, V(u, s, P.fw_d + w / 2), LD, d0 - P.fw_d - w / 2))
        out.append(cyl(6.5, V(u, s, d0 + t), LD, 6.5))
    e0, e1 = P.ear_s
    gap_in = P.ww_s - w / 2                             # 3: halve tussenbus
    out.append(cyl(6.5, V(0, -e1 - 5.3, P.ww_d), LS, 5.3))
    out.append(cyl(4.0, V(0, -e1, P.ww_d), LS, 2 * e1 + 6.5))
    out.append(cyl(6.5, V(0, e1, P.ww_d), LS, 6.5))
    out.append(pipe(6.0, 4.0, V(0, -gap_in, P.ww_d), LS, 2 * gap_in))
    for s0 in (P.ww_s + w / 2, -e0):
        out.append(pipe(6.0, 4.0, V(0, s0, P.ww_d), LS, e0 - P.ww_s - w / 2))
    for u, d in P.blk_bolt:
        out.append(cyl(6.5, V(u, P.blk_flange_s - 5.3, d), LS, 5.3))
        out.append(cyl(4.0, V(u, P.blk_flange_s, d), LS, t + 10.0))
    return out


_BLOCK_CACHE = {}


def _block_local():
    if not _BLOCK_CACHE:
        tires, hubs = _block_wheels_local()
        _BLOCK_CACHE.update({"plate": _block_plate_local(), "tires": tires, "hubs": hubs,
                             "bolts": _block_bolts_local()})
    return _BLOCK_CACHE


def wheel_blocks(axis):
    """axis 'x' of 'z': dict met compounds (robotcoordinaten) van de 4 blokken van die as:
    plate (beugel), tires (PU), hubs (kern + lagers), bolts (assen, bussen, montagebouten)."""
    loc = _block_local()
    frames = [f for f in block_frames() if f[0].startswith(axis)]
    out = {}
    for key in ("plate", "tires", "hubs", "bolts"):
        items = loc[key] if isinstance(loc[key], list) else [loc[key]]
        out[key] = to_robot(compound([_to_frame(s, f) for f in frames for s in items]))
    return out


def block_bolt_pts(axis=None):
    """(x, z) van de M8-montagebouten van de wielblokken in de slede (bij x = 0)."""
    pts = []
    for f in block_frames():
        if axis and not f[0].startswith(axis):
            continue
        for u, d in P.blk_bolt:
            p = _pt(f, u, P.blk_flange_s + P.blk_t, d)
            pts.append((p.x, p.z))
    return pts


def wheel_contacts(axis):
    """Ter controle: (naam, wielhart (x, v, z), as) van alle wielen van een as in het portaalframe."""
    out = []
    for f in block_frames():
        if not f[0].startswith(axis):
            continue
        for u, s in _fw_pos():
            out.append((f[0] + "_flange", _pt(f, u, s, P.fw_d), f[4]))
        for u, s in _ww_pos():
            out.append((f[0] + "_web", _pt(f, u, s, P.ww_d), f[3]))
    return out


# ---------------------------------------------------------------------
# X-slede (beweegt in x; getekend op x = 0): slede, 4 X-wielblokken voor, 4 Z-wielblokken achter, riemklem
# ---------------------------------------------------------------------
def x_slide():
    """X-slede alu 12 mm met verlengstuk voor de bovenste actuatorpen; gaten M8 (Helicoil) voor de 8 wielblokken,
    kabeldoorvoer."""
    v0, v1 = S["slide"]
    h = P.slide_half_x
    tx0, tx1, tz1 = P.slide_tab
    p = box(-h, h, v0, v1, P.slide_z[0], P.slide_z[1]).fuse(box(tx0, tx1, v0, v1, P.slide_z[1] - 1, tz1)).removeSplitter()
    for (x, z) in block_bolt_pts():
        p = p.cut(cyl(4.0, V(x, v0 - 1, z), ALONG_V, P.slide_t + 2))
    p = p.cut(cyl(30, V(0, v0 - 1, 980.0), ALONG_V, P.slide_t + 2))        # kabeldoorvoer
    return to_robot(p)


def belt_clamp():
    """Riemklem met beugel op de voorkant van de slede, om het onderste riempart (x -30..30)."""
    v0 = P.belt_v[0] - 4.0
    z0, z1 = P.belt_z - P.belt_r[1] - 6.0, P.belt_z - P.belt_r[0] + 6.0
    return to_robot(box(-30, 30, v0, S["slide"][0], z0, z1))


def chain_driver():
    """Meenemer kabelrups (voor op de X-slede, boven het bovenste X-profiel)."""
    xm = -80.0
    tv = S["xch"]
    zk = P.chain_z
    v0 = S["slide"][0]
    return to_robot(box(xm - 20, xm + 20, tv - 25, v0, zk + 80, zk + 86).fuse(
        box(xm - 20, xm + 20, v0 - 3, v0, P.slide_z[1] - 8, zk + 86)))


# Actuator Linak LA36 (vast deel op de X-slede): bovenste pen, huis, buitenbuis. Maten uit de datasheet.
def _act_pin_z():
    return P.act_pin_z


def _act_eye_z():
    """Stangoog bij z_ref (getekend in de Z-slede): ingetrokken = rijstand."""
    return P.z_ref + P.act_eye_dz


def _act_house_z():
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
    """Bovenste beugel: voetplaat 8 mm op het verlengstuk van de X-slede + 2 wangen 8 mm."""
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


SPIRAL_X = P.spiral_x
SPIRAL_Z0 = P.spiral_z0


def _spiral_v():
    return S["zch"]


def cable_bracket_x():
    """Beugel achter op de X-slede, rechts naast het rechter Z-profiel: vast anker van de spiraalkabel."""
    v1 = S["slide"][1]
    return to_robot(box(SPIRAL_X - 26, SPIRAL_X + 26, v1, _spiral_v() + 15, SPIRAL_Z0 - 6, SPIRAL_Z0))


# ---------------------------------------------------------------------
# Camera: vast, hoog boven de spillijn (zoals v5 / v6)
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
# Z-slede = 2 UPE 100 met juk, spilbok, spil en motor (beweegt in z; getekend bij z_ref)
# ---------------------------------------------------------------------
def _zc():
    return P.z_ref


def _zg_z():
    """(onderkant, bovenkant) van de Z-profielen bij z_ref."""
    return _zc() + P.zg_bottom, _zc() + P.zg_top


def _zch_v():
    return P.zch_v - P.ch_h / 2, P.zch_v + P.ch_h / 2


def z_channel(side):
    """UPE 100 staand op x = side * zch_x (binnenkant lijf), opening naar x 0; loopt met de Z-slede door de 2 Z-blokken."""
    z0, z1 = _zg_z()
    v0, v1 = _zch_v()
    xw = side * P.zch_x
    xo = xw + side * P.ch_tw
    xt = xw - side * P.ch_depth

    def xr(a, b):
        return min(a, b), max(a, b)

    web = box(*xr(xw, xo), v0, v1, z0, z1)
    ff = box(*xr(xo, xt), v0, v0 + P.ch_tf, z0, z1)
    rf = box(*xr(xo, xt), v1 - P.ch_tf, v1, z0, z1)
    return to_robot(fuse([web, ff, rf]))


def z_channel_cap():
    """Kapje 3 mm op het linker Z-profiel (het rechter krijgt de beugel van de spiraalkabel)."""
    z1 = _zg_z()[1]
    v0, v1 = _zch_v()
    return to_robot(box(-P.zch_x - P.ch_tw, -P.zch_x + P.ch_depth, v0, v1, z1, z1 + 3.0))


def z_yoke():
    """Onderjuk 12 mm onder beide Z-profielen, tot de achterplaat van de spilbok; de profielen staan erop en zijn
    rondom gelast (met de profielen in de wielblokken als mal, zodat ze evenwijdig staan)."""
    z0 = _zg_z()[0]
    w = P.zg_yoke_half_x
    return to_robot(box(-w, w, _zch_v()[0], S["sb_back"][0], z0 - P.zg_yoke_t, z0))


def z_gussets():
    """2 schoren 6 mm buiten de profielen, tussen het lijf en het juk (houden de profielen haaks op het juk)."""
    z0 = _zg_z()[0]
    t, h = P.zg_gusset
    out = []
    for s in (-1, 1):
        xo = s * (P.zch_x + P.ch_tw)
        xe = s * P.zg_yoke_half_x
        pts = [V(xo, P.zch_v - t / 2, z0), V(xe, P.zch_v - t / 2, z0), V(xo, P.zch_v - t / 2, z0 + h)]
        out.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, t, 0)))
    return to_robot(compound(out))


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
    for (wz0, wz1) in ((z_lo + 95, z_lo + 120), (z_lo + 200, z_lo + 280)):     # lichtgaten
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
    z_lo, z_mo = _sb()
    v0, v1 = _bearing_plate_v()
    w = P.sb_side_x - 2.5
    p = box(-w, w, v0, v1, z_lo + 8, z_mo)
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            p = p.cut(box(dx - 7.5, dx + 7.5, v0 - 1, v1 + 1, zb - 10.5, zb + 10.5))
    return to_robot(p)


def ucp(zb):
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
    v0, v1 = _bearing_plate_v()
    vt = v1 + P.ucp_foot_t
    out = []
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            out.append(cyl(7, V(dx, v0 - 12, zb), ALONG_V, vt - v0 + 20).fuse(cyl(11.5, V(dx, vt, zb), ALONG_V, 8.8)).fuse(
                cyl(11.5, V(dx, v0 - 11, zb), ALONG_V, 11)))
    return to_robot(compound(out))


def spindle_shaft():
    z0 = _zc() + 100
    return to_robot(cyl(P.shaft_d / 2, V(0, S["spindle"], z0), UP, _zc() + P.shaft_top - z0))


def _flange_holes(sh, v, z0, t):
    for k in range(4):
        a = math.radians(45 + 90 * k)
        sh = sh.cut(cyl(5.5, V(40 * math.cos(a), v + 40 * math.sin(a), z0 - 1), UP, t + 2))
    return sh


def spindle_flange():
    z = _zc() + 100
    vs = S["spindle"]
    f = cyl(55, V(0, vs, z), UP, 12).cut(cyl(P.shaft_d / 2, V(0, vs, z - 1), UP, 14))
    return to_robot(_flange_holes(f, vs, z, 12))


def jaw_coupling():
    vs = S["spindle"]
    z0 = _zc() + P.jaw_z0
    r = P.jaw_d / 2
    hub = P.jaw_hub_L
    lo = pipe(r, P.shaft_d / 2, V(0, vs, z0), UP, hub)
    star = pipe(r - 1.5, 6.0, V(0, vs, z0 + hub), UP, P.jaw_star)
    hi = pipe(r, P.motor_shaft_d / 2, V(0, vs, z0 + hub + P.jaw_star), UP, hub)
    return to_robot(compound([lo, star, hi]))


def _motor_z(d):
    return _zc() + P.motor_shaft_end + d


def spindle_motor():
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
    zs = _motor_z(0)
    return to_robot(cyl(P.motor_shaft_d / 2, V(0, S["spindle"], zs), UP, P.motor_shaft_out))


def motor_plate():
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
    vs = S["spindle"]
    z0 = _sb()[1] + 8
    x1 = P.motor_foot_h
    out = []
    for v in (vs + P.motor_plate_v[0], vs + P.motor_plate_v[1] - P.gusset_mp_t):
        pts = [V(x1, v, z0), V(x1, v, z0 + 95), V(x1 - 60, v, z0)]
        out.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, P.gusset_mp_t, 0)))
    return to_robot(compound(out))


def cable_bracket_z():
    """Kapje met arm boven op het rechter Z-profiel: bewegend anker van de spiraalkabel."""
    z1 = _zg_z()[1]
    v0, v1 = _zch_v()
    return to_robot(box(P.zch_x - P.ch_depth, SPIRAL_X + 26, v0, v1, z1, z1 + 6))


def pot_bushes():
    z = _sb()[0] + 8
    vs = S["spindle"]
    return to_robot(compound([pipe(19, 8.5, V(s * P.pot_rod_dx, vs, z), UP, 25) for s in (-1, 1)]))


def _ring_z():
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
        t = Part.makeBox(18, 10, 25, V(R - 18, 5, 0))
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


# ---------------------------------------------------------------------
# Elektra (vast) en kabel (vervormt met z)
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


def chain_shapes(x):
    """Kabelrups bij slede-stand x: (onderpart, bovenpart, bocht), boven op het bovenste X-profiel."""
    x_fixed = -P.xbar_L / 2 + 30
    x_mov = x - 80
    x_b = max(x_fixed, x_mov) + 120
    tv = S["xch"]
    v0, v1 = tv - 25, tv + 25
    zk = P.chain_z
    lower = box(x_fixed, x_b, v0, v1, zk, zk + 25)
    upper = box(x_mov, x_b, v0, v1, zk + 55, zk + 80)
    bend = box(x_b, x_b + 25, v0, v1, zk, zk + 80)
    return to_robot(lower), to_robot(upper), to_robot(bend)


def spiral_cable(x, z_tool):
    """Spiraalkabel van de beugel op de X-slede (vast) omhoog naar het kapje op het rechter Z-profiel (beweegt)."""
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
