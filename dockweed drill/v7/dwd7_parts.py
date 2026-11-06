"""Onderdelen van de dockweed drill v7: een functie per onderdeel, geeft een Part-shape in robotcoordinaten.

v7 heeft geen X-as: de spil staat vast op x 0 en de robot stuurt naar de plant.
Intern wordt getekend in het portaalframe (x, v, z): v = afstand achter de achterkant van de achterste onderbalk
van de robot. to_robot() spiegelt dat naar robot-y (y = robot_beam_rear_face - v).
Bewegende groepen worden in hun referentiestand getekend:
- Z-slede (2 ronde buizen, juk, stang van de actuator, spilbok, spil) met de onderkant van het gereedschap op z_ref
  (rijstand, actuator ingetrokken);
- pot hangend onder de spilbok bij z_ref (rand op z_ref - pot_rim).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd7_params as P

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
    s["xbeam"] = P.xbeam_v
    s["mp"] = (P.mp_v0, P.mp_v0 + P.mp_t)              # Z-montageplaat
    s["zg"] = P.zg_v                                    # hart ronde buizen (Z-geleiding)
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
    """Staander 40 x 40 x 3 met een M12-gat (langs v) op de hoogte van elke dwarsbalk."""
    xc = side * P.hs_x
    h = P.up_size / 2.0
    u = tube_rect(xc - h, xc + h, P.up_v0, P.up_v1, P.up_z0, P.up_z1, P.up_wall, "z")
    for zp in P.beam_z:
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
# Z-frame (vast): 2 dwarsbalken achter de staanders, montageplaat, 4 lagerhuizen, bovenste actuatorbeugel
# ---------------------------------------------------------------------
def z_beam(zp):
    """Dwarsbalk 40 x 40 x 3 op hoogte zp, 20 mm voorbij de staanders; M12 bij de staanders, M10 bij de plaat."""
    L = P.xbeam_half_L
    h = P.xbeam[0] / 2
    v0, v1 = S["xbeam"]
    b = tube_rect(-L, L, v0, v1, zp - h, zp + h, P.xbeam[1], "x")
    for s in (-1, 1):
        b = b.cut(cyl(6.5, V(s * P.hs_x, v0 - 1, zp), ALONG_V, P.xbeam[0] + 2))
        b = b.cut(cyl(5.5, V(s * P.mp_bolt_x, v0 - 1, zp), ALONG_V, P.xbeam[0] + 2))
    return to_robot(b)


def z_beam_bolts():
    """4x M12 door staander en dwarsbalk (kop achter, moer voor op de staander)."""
    out = [bolt_v(s * P.hs_x, S["xbeam"][1], P.up_v0, zp, P.m12_d, P.m12_head_r, P.m12_head_k, P.m10_nut_m)
           for s in (-1, 1) for zp in P.beam_z]
    return to_robot(compound(out))


def mount_plate_bolts():
    """4x M10 door montageplaat en dwarsbalk (kop achter op de plaat, moer voor op de balk)."""
    out = [bolt_v(s * P.mp_bolt_x, S["mp"][1], S["xbeam"][0], zp, P.m10_d, P.m10_head_r, P.m10_head_k, P.m10_nut_m)
           for s in (-1, 1) for zp in P.beam_z]
    return to_robot(compound(out))


def house_positions():
    """(x, z) van de 4 lagerhuizen: links en rechts, op de hoogte van de dwarsbalken."""
    return [(s * P.zg_dx, zp) for s in (-1, 1) for zp in P.zg_house_z]


def _house_bolt_pts():
    bx, bz = P.zg_house_bolt
    return [(xs + dx, zs + dz) for xs, zs in house_positions() for dx in (-bx, bx) for dz in (-bz, bz)]


def mount_plate():
    """Z-montageplaat staal 10 mm met verlengstuk voor de bovenste actuatorpen; gaten M10 (balken), M8 getapt
    (lagerhuizen, getekend op O8)."""
    v0, v1 = S["mp"]
    h = P.mp_half_x
    tx0, tx1, tz1 = P.mp_tab
    p = box(-h, h, v0, v1, P.mp_z[0], P.mp_z[1]).fuse(box(tx0, tx1, v0, v1, P.mp_z[1] - 1, tz1)).removeSplitter()
    for s in (-1, 1):
        for zp in P.beam_z:
            p = p.cut(cyl(5.5, V(s * P.mp_bolt_x, v0 - 1, zp), ALONG_V, P.mp_t + 2))
    for (bx, bz) in _house_bolt_pts():
        p = p.cut(cyl(4.0, V(bx, v0 - 1, bz), ALONG_V, P.mp_t + 2))
    for gz in (910.0,):                                   # lichtgat in het midden (kabeldoorvoer)
        p = p.cut(cyl(30, V(0, v0 - 1, gz), ALONG_V, P.mp_t + 2))
    return to_robot(p)


def z_houses():
    """Lagerhuis (blok) om de glijbus: van de montageplaat tot 32 achter het buishart; boring = buitenmaat bus;
    4 gaten M8 met verzinking voor de kop aan de achterkant."""
    v1 = S["mp"][1]
    v = S["zg"]
    w, L, back = P.zg_house
    out = []
    for xs, zs in house_positions():
        b = box(xs - w / 2, xs + w / 2, v1, v + back, zs - L / 2, zs + L / 2)
        b = b.cut(cyl(P.zg_bush_d / 2, V(xs, v, zs - L / 2 - 1), UP, L + 2))
        for (bx, bz) in _house_bolt_pts():
            if abs(bx - xs) < w / 2 and abs(bz - zs) < L / 2:
                b = b.cut(cyl(4.5, V(bx, v1 - 1, bz), ALONG_V, v + back - v1 + 2))
                b = b.cut(cyl(7.0, V(bx, v + back - 8, bz), ALONG_V, 9))
        out.append(b)
    return to_robot(compound(out))


def z_bushes():
    """Kunststof glijbus (iglidur / POM) O50 binnen, O60 buiten, zo lang als het huis."""
    v = S["zg"]
    L = P.zg_house[1]
    return to_robot(compound([pipe(P.zg_bush_d / 2, P.zg_d / 2 + 0.1, V(xs, v, zs - L / 2), UP, L)
                              for xs, zs in house_positions()]))


def z_house_bolts():
    """M8 van achteren door het huis in de getapte montageplaat (kop verzonken in het huis)."""
    v0 = S["mp"][0]
    v_back = S["zg"] + P.zg_house[2]
    return to_robot(compound([cyl(4, V(bx, v0 + 1, bz), ALONG_V, v_back - 8 - v0 - 1 + 5.5).fuse(
        cyl(6.5, V(bx, v_back - 8, bz), ALONG_V, 5.5)) for bx, bz in _house_bolt_pts()]))


def z_wipers():
    """Schraapring (rubber) boven en onder elk huis, om de buis."""
    v = S["zg"]
    L = P.zg_house[1]
    out = []
    for xs, zs in house_positions():
        for z0 in (zs - L / 2 - P.zg_wiper_t, zs + L / 2):
            out.append(pipe(P.zg_d / 2 + 6, P.zg_d / 2, V(xs, v, z0), UP, P.zg_wiper_t))
    return to_robot(compound(out))


def z_grease_nipples():
    """Smeernippel achter op elk huis (+v)."""
    v = S["zg"] + P.zg_house[2]
    return to_robot(compound([cyl(3.2, V(xs, v, zs), ALONG_V, 12) for xs, zs in house_positions()]))


# Actuator Linak LA36 (vast deel op de montageplaat): bovenste pen, huis, buitenbuis. Maten uit de datasheet.
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
    """Bovenste beugel: voetplaat 8 mm op het verlengstuk van de montageplaat + 2 wangen 8 mm."""
    v1 = S["mp"][1]
    zp = _act_pin_z()
    xc = P.act_x
    tx0, tx1, tz1 = P.mp_tab
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
    return S["act"]


def cable_bracket_fixed():
    """Beugel op de montageplaat: vast anker van de spiraalkabel."""
    v1 = S["mp"][1]
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
# Z-slede = 2 ronde buizen met juk, spilbok, spil en motor (beweegt in z; getekend bij z_ref)
# ---------------------------------------------------------------------
def _zc():
    return P.z_ref


def _zg_z():
    """(onderkant, bovenkant) van de ronde buizen bij z_ref."""
    return _zc() + P.zg_bottom, _zc() + P.zg_top


def z_guide_tube(side):
    """Precisiebuis O50 x 4 (E355, koudgetrokken naadloos): glijdt met de Z-slede door de 2 lagerhuizen."""
    z0, z1 = _zg_z()
    return to_robot(pipe(P.zg_d / 2, P.zg_d / 2 - P.zg_t, V(side * P.zg_dx, S["zg"], z0), UP, z1 - z0))


def z_tube_caps():
    """Dop 3 mm op de bovenkant van de linker buis (de rechter krijgt het kapje van de spiraalkabel)."""
    z1 = _zg_z()[1]
    return to_robot(cyl(P.zg_d / 2, V(-P.zg_dx, S["zg"], z1), UP, 3.0))


def _yoke_v():
    return S["zg"] - P.zg_d / 2 - 6, S["sb_back"][0]


def z_yoke():
    """Onderjuk 10 mm onder de buizen, van de buizen tot de achterplaat van de spilbok. De buizen staan erop en
    zijn rondom gelast (met de buizen in de lagerhuizen als mal, zodat ze evenwijdig staan)."""
    z0 = _zg_z()[0]
    w = P.zg_yoke_half_x
    v0, v1 = _yoke_v()
    return to_robot(box(-w, w, v0, v1, z0 - P.zg_yoke_t, z0))


def z_clamp_plate():
    """Klemplaat 10 mm 60 mm boven het juk: ronde gaten om de buizen (gelast aan buis en achterplaat)."""
    z0 = _zc() + P.zg_clamp_z
    w = P.zg_yoke_half_x
    v0, v1 = _yoke_v()
    p = box(-w, w, v0, v1, z0, z0 + P.zg_yoke_t)
    for s in (-1, 1):
        p = p.cut(cyl(P.zg_d / 2 + 0.5, V(s * P.zg_dx, S["zg"], z0 - 1), UP, P.zg_yoke_t + 2))
    p = p.cut(box(-22, 22, v0 - 1, S["zg"] + 6, z0 - 1, z0 + P.zg_yoke_t + 1))   # uitsparing voor het stangoog
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
    """Kapje met arm boven op de rechter Z-buis: bewegend anker van de spiraalkabel."""
    z1 = _zg_z()[1]
    v = _spiral_v()
    return to_robot(box(P.zg_dx - P.zg_d / 2, SPIRAL_X + 26, min(S["zg"] - P.zg_d / 2, v - 15),
                        max(S["zg"] + P.zg_d / 2, v + 15), z1, z1 + 6))


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


def spiral_cable(z_tool):
    """Spiraalkabel van de beugel op de montageplaat (vast) omhoog naar het kapje op de rechter Z-buis (beweegt)."""
    z_a = SPIRAL_Z0
    z_c = z_tool + P.zg_top
    n = P.spiral_turns
    pitch = (z_c - z_a) / n
    v = _spiral_v()
    rings = [Part.makeTorus(22, 4.5, V(SPIRAL_X, v, z_a + pitch * (k + 0.5)), UP) for k in range(n)]
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
