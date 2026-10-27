import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lfs_params as P
import lfs_kin as K

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basisfuncties (zelfde stijl als ../advanced/lfa_parts.py)
# ---------------------------------------------------------------------
def box(sx, sy, sz, cx=0.0, cy=0.0, cz=0.0):
    return Part.makeBox(sx, sy, sz, V(cx - sx / 2.0, cy - sy / 2.0, cz - sz / 2.0))


def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, h, axis="z", cx=0.0, cy=0.0, cz=0.0):
    r = d / 2.0
    if axis == "x":
        return Part.makeCylinder(r, h, V(cx - h / 2.0, cy, cz), X)
    if axis == "y":
        return Part.makeCylinder(r, h, V(cx, cy - h / 2.0, cz), Y)
    return Part.makeCylinder(r, h, V(cx, cy, cz - h / 2.0), Z)


def cyl_x(d, x0, x1, y, z):
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def ring_x(d_out, d_in, x0, x1, y, z):
    return cyl_x(d_out, x0, x1, y, z).cut(cyl_x(d_in, x0 - 1, x1 + 1, y, z))


def tube_span(x, y, z, wall):
    outer = box_span(x, y, z)
    sx, sy, sz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    if sx >= sy and sx >= sz:
        inner = box_span((x[0] - 1, x[1] + 1), (y[0] + wall, y[1] - wall), (z[0] + wall, z[1] - wall))
    elif sy >= sz:
        inner = box_span((x[0] + wall, x[1] - wall), (y[0] - 1, y[1] + 1), (z[0] + wall, z[1] - wall))
    else:
        inner = box_span((x[0] + wall, x[1] - wall), (y[0] + wall, y[1] - wall), (z[0] - 1, z[1] + 1))
    return outer.cut(inner)


def moved(shape, x=0.0, y=0.0, z=0.0):
    s = shape.copy()
    s.translate(V(x, y, z))
    return s


def rotated(shape, angle, axis=Z, base=V(0, 0, 0)):
    s = shape.copy()
    s.rotate(base, axis, angle)
    return s


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), X)


def mirrored_x(shape, side):
    return shape if side > 0 else mirror_x(shape)


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
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0))


def stadium_yz(p1, p2, r, x0, t):
    (y1, z1), (y2, z2) = p1, p2
    length = math.hypot(y2 - y1, z2 - z1)
    ang = math.degrees(math.atan2(z2 - z1, y2 - y1))
    parts = [Part.makeCylinder(r, t, V(x0, y1, z1), X), Part.makeCylinder(r, t, V(x0, y2, z2), X)]
    if length > 1e-6:
        b = Part.makeBox(t, length, 2 * r, V(x0, 0, -r))
        b.rotate(V(0, 0, 0), X, ang)
        b.translate(V(0, y1, z1))
        parts.append(b)
    return fuse_all(parts)


def hex_prism(af, h, z0=0.0, cx=0.0, cy=0.0):
    r = af / math.sqrt(3.0)
    pts = [V(cx + r * math.cos(math.radians(60 * i)), cy + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def frame_matrix(origin, u):
    # lokaal z -> u (in het y-z vlak), lokaal x -> x, lokaal y -> (uz, -uy) (rechtshandig)
    uy, uz = u
    return App.Matrix(1, 0, 0, origin[0],
                      0, uz, uy, origin[1],
                      0, -uy, uz, origin[2],
                      0, 0, 0, 1)


def orient(shape, origin, u):
    s = shape.copy()
    s.transformShape(frame_matrix(origin, u))
    return s


def bolt_z(d, af, k, length, nut_at=None, nut_m=None):
    # kop z -k..0, schacht z 0..length, optionele moer vanaf nut_at
    parts = [hex_prism(af, k, z0=-k), Part.makeCylinder(d / 2.0, length)]
    if nut_at is not None:
        parts.append(hex_prism(af, nut_m, z0=nut_at))
    return fuse_all(parts)


def bolt_x(d, af, k, m, x0, x1, y, z, extra=3.0):
    """Bout langs +x: kop tegen x0 (kant -x), moer tegen x1, schacht steekt extra door."""
    length = x1 - x0 + m + extra
    b = bolt_z(d, af, k, length, nut_at=x1 - x0, nut_m=m)
    b = rotated(b, 90.0, Y)              # schacht langs +x
    b.translate(V(x0, y, z))
    return b


def hose(points, od):
    # stuurpunten (poles): de slang loopt door begin- en eindpunt en blijft binnen het stuurpolygoon
    pts = [V(*p) for p in points]
    bs = Part.BSplineCurve()
    bs.buildFromPoles(pts, False, 3)
    edge = bs.toShape()
    tangent = edge.tangentAt(edge.FirstParameter)
    profile = Part.Wire(Part.makeCircle(od / 2.0, pts[0], tangent))
    return Part.Wire(edge).makePipeShell([profile], True, True)


def cyl_between(p0, p1, d):
    """Cilinder tussen twee punten (x, y, z)."""
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


# ---------------------------------------------------------------------
# Aanbouwbok (vast aan de robotbalk), 1 gelast deel
# ---------------------------------------------------------------------
def cheek_x(inner):
    half = P.bush_len / 2.0 + 1.0
    c = P.arm_x
    return (c - half - P.hs_cheek_t, c - half) if inner else (c + half, c + half + P.hs_cheek_t)


def hs_top_plate():
    z0 = P.robot_beam_z_top
    plate = box_span((-P.hs_top_x, P.hs_top_x), P.hs_top_y, (z0, z0 + P.hs_top_t))
    holes = [cyl(P.robot_hole_d, 3 * P.hs_top_t, "z", sx * x, 0.0, z0 + P.hs_top_t / 2.0)
             for x in P.hs_bolt_x for sx in (-1, 1)]
    return plate.cut(holes)


def hs_clamp_strip():
    z1 = P.robot_beam_z_bot
    plate = box_span((-P.hs_top_x, P.hs_top_x), P.hs_clamp_y, (z1 - P.hs_clamp_t, z1))
    holes = [cyl(P.robot_hole_d, 3 * P.hs_clamp_t, "z", sx * x, 0.0, z1 - P.hs_clamp_t / 2.0)
             for x in P.hs_bolt_x for sx in (-1, 1)]
    return plate.cut(holes)


def hs_cheeks():
    items = []
    for side in (-1, 1):
        for inner in (True, False):
            x0, x1 = cheek_x(inner)
            plate = box_span((x0, x1), P.hs_cheek_y, (P.hs_cheek_z_bot, P.robot_beam_z_top))
            plate = plate.cut(cyl_x(P.pivot_bolt_d + 0.5, x0 - 1, x1 + 1, *P.pivot))
            items.append(mirrored_x(plate, side))
    return Part.makeCompound(items)


def hs_act_lugs():
    """2 langgatplaten op de bovenplaat: het stangoog van de actuator schuift in het langgat (zweefstand)."""
    lo, hi = K.slot_ends()
    u = K.slot_dir()
    nf = (u[1], -u[0])                   # loodrecht op het langgat, naar voren-onder
    r = 16.0
    z0 = P.robot_beam_z_top + P.hs_top_t
    p_lo = K.add(lo, nf, r)
    p_hi = K.add(hi, nf, r)
    items = []
    for sx in (-1, 1):
        x0 = P.act_lug_gap / 2.0 if sx > 0 else -P.act_lug_gap / 2.0 - P.act_lug_t
        # voet naar voren op de bovenplaat; achter-onder het langgat blijft vrij voor de actuator
        base = poly_yz([p_lo, (p_lo[0], z0), (p_hi[0] + 30.0, z0), p_hi], x0, P.act_lug_t)
        body = fuse_all([stadium_yz(lo, hi, r, x0, P.act_lug_t), base])
        items.append(body.cut(stadium_yz(lo, hi, P.act_pin_hole / 2.0, x0 - 1, P.act_lug_t + 2)))
    return Part.makeCompound(items)


def hs_bolts():
    items = []
    z_head = P.robot_beam_z_top + P.hs_top_t
    length = z_head - (P.robot_beam_z_bot - P.hs_clamp_t) + P.m10_m + 3.0
    for x in P.hs_bolt_x:
        for sx in (-1, 1):
            b = bolt_z(P.m10_d, P.m10_af, P.m10_k, length, nut_at=length - P.m10_m - 3.0, nut_m=P.m10_m)
            b = rotated(b, 180.0, X)            # kop boven, schacht omlaag
            b.translate(V(sx * x, 0.0, z_head))
            items.append(b)
    return Part.makeCompound(items)


def hs_pivot_bolts():
    items = []
    for side in (-1, 1):
        x0 = cheek_x(True)[0]
        x1 = cheek_x(False)[1]
        b = bolt_x(P.pivot_bolt_d, P.pivot_bolt_af, P.pivot_bolt_k, P.pivot_bolt_m, x0, x1, *P.pivot)
        items.append(mirrored_x(b, side))
    return Part.makeCompound(items)


def act_pin_bolt(pin, gap):
    """Pen M10 door twee ogen (binnenmaat gap) met kop en moer."""
    x0 = -gap / 2.0 - P.act_lug_t
    x1 = gap / 2.0 + P.act_lug_t
    return bolt_x(P.act_pin_d, 16, 6.4, 8.0, x0, x1, pin[0], pin[1])


# ---------------------------------------------------------------------
# Hefraam (draait om de draaibouten), coordinaten in werkstand
# ---------------------------------------------------------------------
def bar():
    half = P.bar_length / 2.0
    tube = tube_span((-half, half), (P.bar_rear, P.bar_front), (P.bar_bot, P.bar_top), P.bar_wall)
    caps = [box_span((x0, x0 + P.bar_cap_t), (P.bar_rear, P.bar_front), (P.bar_bot, P.bar_top))
            for x0 in (-half - P.bar_cap_t, half)]
    return fuse_all([tube] + caps)


def arms():
    p0, p1, u = K.arm_axis()
    length = K.dist(p0, p1) + 30.0
    s = P.arm_size / 2.0
    w = P.arm_wall
    local = box_span((-s, s), (-s, s), (0.0, length)).cut(box_span((-s + w, s - w), (-s + w, s - w), (-1.0, length + 1)))
    items = []
    for side in (-1, 1):
        x = side * P.arm_x
        tube = orient(moved(local, x=x), (0.0, p0[0], p0[1]), u)
        tube = tube.cut(box_span((x - 50, x + 50), (P.bar_front - 200.0, P.bar_front), (0.0, 800.0)))
        bush = ring_x(P.bush_od, P.bush_id, x - P.bush_len / 2.0, x + P.bush_len / 2.0, *P.pivot)
        tube = tube.cut(cyl_x(P.bush_od - 1.0, x - 30, x + 30, *P.pivot))
        items.append(fuse_all([tube, bush]))
    return Part.makeCompound(items)


def cross_tube():
    """Dwarsbuis tussen de armen met de 2 ogen voor het actuatorhuis erop gelast."""
    cy, cz = K.cross_center()
    s = P.cross_size / 2.0
    xi = P.arm_x - P.arm_size / 2.0
    tube = tube_span((-xi, xi), (cy - s, cy + s), (cz - s, cz + s), P.cross_wall)
    return fuse_all([tube] + frame_act_lugs().Solids)


def frame_act_lugs():
    ly, lz = P.act_l
    cy, cz = K.cross_center()
    top = cz + P.cross_size / 2.0
    r = 16.0
    items = []
    for sx in (-1, 1):
        x0 = P.act_lug_gap / 2.0 if sx > 0 else -P.act_lug_gap / 2.0 - P.act_lug_t
        base = poly_yz([(ly - r, lz), (ly + r, lz), (cy + 18.0, top - 2.0), (cy - 18.0, top - 2.0)], x0, P.act_lug_t)
        body = fuse_all([Part.makeCylinder(r, P.act_lug_t, V(x0, ly, lz), X), base])
        items.append(body.cut(cyl_x(P.act_pin_hole, x0 - 1, x0 + P.act_lug_t + 1, ly, lz)))
    return Part.makeCompound(items)


# ---------------------------------------------------------------------
# Actuator tussen act_a (bok) en de pen in het langgat (hefraam), wereldcoordinaten
# ---------------------------------------------------------------------
def actuator(body_pin, rod_pin):
    """Geeft (huis, stang) in werktuigcoordinaten: huis met parallelle motor op body_pin (hefraam),
    stang naar rod_pin (stangoog in het langgat van de bok); beide (y, z). De motor ligt in het y-z vlak
    aan de achter-bovenkant van de buis, zodat de actuator smal blijft (tussen de ogen en de pompplaat door)."""
    length = K.dist(body_pin, rod_pin)
    u = K.unit(body_pin, rod_pin)
    er = P.act_eye_d / 2.0
    w = P.act_eye_w
    tube_end = P.act_retracted - 25.0
    g0 = 30.0
    md = P.act_motor_d
    off = P.act_motor_offset
    body = [cyl_x(P.act_eye_d, -w / 2.0, w / 2.0, 0, 0).cut(cyl_x(P.act_pin_hole, -w, w, 0, 0)),
            Part.makeCylinder(8.0, g0 + 2.0 - (er - 4.0), V(0, 0, er - 4.0)),
            box_span((-20.0, 20.0), (-off - md / 2.0, 20.0), (g0, g0 + 42.0)),
            Part.makeCylinder(P.act_tube_d / 2.0, tube_end - g0 - 40.0, V(0, 0, g0 + 40.0)),
            Part.makeCylinder(md / 2.0, P.act_motor_len, V(0, -off, g0 + 40.0))]
    rod = [Part.makeCylinder(P.act_rod_d / 2.0, length - 14.0 - tube_end, V(0, 0, tube_end)),
           Part.makeCylinder(8.0, 8.0, V(0, 0, length - 18.0)),
           cyl_x(P.act_eye_d, -w / 2.0, w / 2.0, 0, length).cut(cyl_x(P.act_pin_hole, -w, w, 0, length))]
    # lokaal y = (uz, -uy) wijst naar voren-onder; de motor zit aan de -y kant (achter-boven)
    origin = (0.0, body_pin[0], body_pin[1])
    return orient(fuse_all(body), origin, u), orient(fuse_all(rod), origin, u)


# ---------------------------------------------------------------------
# Injectiemes (lokaal: x = 0 is het hart van de rij)
# ---------------------------------------------------------------------
def h_bottom_plate():
    hw = P.h_plate_w / 2.0
    z1 = P.bar_bot
    plate = box_span((-hw, hw), P.h_plate_y, (z1 - P.h_plate_t, z1))
    holes = [cyl(P.ubolt_d + 1.0, 3 * P.h_plate_t, "z", sx * P.ubolt_dx, y, z1 - P.h_plate_t / 2.0)
             for sx in (-1, 1) for y in ubolt_legs_y()]
    return plate.cut(holes)


def ubolt_legs_y():
    r = P.ubolt_d / 2.0
    return (P.bar_front + r, P.bar_rear - r)


def side_x(side):
    a = P.knife_t / 2.0 + 0.5
    return (a, a + P.side_t) if side > 0 else (-a - P.side_t, -a)


def h_side_plates():
    z1 = P.bar_bot - P.h_plate_t
    sp = K.shear_point()
    items = []
    for side in (-1, 1):
        x0, x1 = side_x(side)
        plate = box_span((x0, x1), P.side_y, (P.side_z_bot, z1))
        plate = plate.cut([cyl_x(12.5, x0 - 1, x1 + 1, *P.knife_pivot), cyl_x(P.shear_d + 0.5, x0 - 1, x1 + 1, *sp)])
        items.append(plate)
    return Part.makeCompound(items)


def ubolts(cx, legs_y, z_top, z_nut, d, nut_af, nut_m):
    """Vierkante beugelbouten over de bovenkant van de balk: benen omlaag op legs_y, moer onder z_nut."""
    r = d / 2.0
    items = []
    for x in cx:
        y0, y1 = legs_y
        z_end = z_nut - nut_m - 4.0
        parts = [Part.makeCylinder(r, z_top - z_end, V(x, y, z_end)) for y in (y0, y1)]
        parts.append(Part.makeCylinder(r, abs(y1 - y0), V(x, min(y0, y1), z_top), Y))
        parts += [Part.makeSphere(r, V(x, y, z_top)) for y in (y0, y1)]
        parts += [hex_prism(nut_af, nut_m, z0=z_nut - nut_m, cx=x, cy=y) for y in (y0, y1)]
        items.append(fuse_all(parts))
    return Part.makeCompound(items)


def h_ubolts():
    r = P.ubolt_d / 2.0
    return ubolts((-P.ubolt_dx, P.ubolt_dx), ubolt_legs_y(), P.bar_top + r, P.bar_bot - P.h_plate_t,
                  P.ubolt_d, P.ubolt_nut_af, P.ubolt_nut_m)


def knife():
    pts = list(K.knife_points())
    t = P.knife_t
    body = poly_yz(pts, -t / 2.0, t)
    holes = [cyl_x(12.5, -t, t, *P.knife_pivot), cyl_x(P.shear_d + 0.5, -t, t, *K.shear_point())]
    holes += [cyl_x(6.5, -t, t, *p) for p in K.clip_bolt_points()]
    return body.cut(holes)


def knife_bolts():
    x0 = side_x(-1)[0]
    x1 = side_x(1)[1]
    pivot = bolt_x(12.0, 19, 7.5, 10.8, x0, x1, *P.knife_pivot)
    shear = bolt_x(P.shear_d, 10, 4.0, 5.0, x0, x1, *K.shear_point())
    return Part.makeCompound([pivot, shear])


def tube():
    p0, p1 = K.tube_ends()
    outer = cyl_between((0.0, p0[0], p0[1]), (0.0, p1[0], p1[1]), P.tube_od)
    inner = cyl_between((0.0, p0[0], p0[1]), (0.0, p1[0], p1[1]), P.tube_id)
    d, n = K.knife_dirs()
    inner.translate(V(0, -d[0] * 1.0, -d[1] * 1.0))
    return outer.cut(inner)


def tube_clips():
    """2 P-clips (RVS) om het buisje, met een bout M6 door het mes."""
    d, n = K.knife_dirs()
    items = []
    u = (-d[0], -d[1])                 # langs het buisje omhoog
    for c, b in zip(K.clip_points(), K.clip_bolt_points()):
        band = cyl_between((0.0, c[0] - u[0] * 6, c[1] - u[1] * 6), (0.0, c[0] + u[0] * 6, c[1] + u[1] * 6),
                           P.tube_od + 2.0).cut(
            cyl_between((0.0, c[0] - u[0] * 7, c[1] - u[1] * 7), (0.0, c[0] + u[0] * 7, c[1] + u[1] * 7),
                        P.tube_od + 0.2))
        tab = []
        for sx in (-1, 1):
            x0 = P.knife_t / 2.0 if sx > 0 else -P.knife_t / 2.0 - 1.5
            tab.append(stadium_yz(c, b, 6.0, x0, 1.5))
        bolt = bolt_x(6.0, 10, 4.0, 5.0, -P.knife_t / 2.0 - 1.5, P.knife_t / 2.0 + 1.5, b[0], b[1], extra=2.0)
        items.append(fuse_all([band] + tab + [bolt]))
    return Part.makeCompound(items)


def nozzle_axis():
    p0, p1 = K.tube_ends()
    d, n = K.knife_dirs()
    u = (-d[0], -d[1])
    return p1, u


def nozzle():
    """Spuitdophouder (membraanklep) met bajonetdop en doseerplaatje, slangpilaar boven."""
    p1, u = nozzle_axis()
    cap0 = p1                                # buisje steekt in de dop (knelkoppeling)
    cap1 = K.add(cap0, u, P.nozzle_cap_len)
    body1 = K.add(cap1, u, P.nozzle_len)
    barb1 = K.add(body1, u, P.nozzle_inlet_len)
    parts = [cyl_between((0, cap0[0], cap0[1]), (0, cap1[0], cap1[1]), P.nozzle_cap_d),
             cyl_between((0, cap1[0], cap1[1]), (0, body1[0], body1[1]), P.nozzle_d),
             cyl_between((0, body1[0], body1[1]), (0, barb1[0], barb1[1]), P.nozzle_inlet_d)]
    return fuse_all(parts)


def nozzle_inlet():
    p1, u = nozzle_axis()
    return K.add(p1, u, P.nozzle_cap_len + P.nozzle_len + P.nozzle_inlet_len)


# ---------------------------------------------------------------------
# Dieptewiel (lokaal: x = 0 is het hart van het wiel)
# ---------------------------------------------------------------------
def gw_clamp_plate():
    hw = P.gw_clamp_w / 2.0
    plate = box_span((-hw, hw), P.gw_clamp_y, P.gw_clamp_z)
    r = P.gw_ubolt_d / 2.0
    holes = [cyl(P.gw_ubolt_d + 1.0, 30, "y", sx * P.gw_ubolt_dx, P.gw_clamp_y[0] + 5, z)
             for sx in (-1, 1) for z in (P.bar_top + r, P.bar_bot - r)]
    return plate.cut(holes)


def gw_ubolts():
    """Beugelbouten M10 om de achterkant van de balk, benen naar voren door de klemplaat."""
    r = P.gw_ubolt_d / 2.0
    y_back = P.bar_rear - r
    y_nut = P.gw_clamp_y[1]
    nut_m = 8.4
    items = []
    for sx in (-1, 1):
        x = sx * P.gw_ubolt_dx
        y_end = y_nut + nut_m + 3.0
        parts = [Part.makeCylinder(r, y_end - y_back, V(x, y_back, z), Y) for z in (P.bar_top + r, P.bar_bot - r)]
        parts.append(Part.makeCylinder(r, P.bar_size + 2 * r, V(x, y_back, P.bar_bot - r)))
        parts += [Part.makeSphere(r, V(x, y_back, z)) for z in (P.bar_top + r, P.bar_bot - r)]
        for z in (P.bar_top + r, P.bar_bot - r):
            nut = rotated(hex_prism(17, nut_m), -90.0, X)
            nut.translate(V(x, y_nut, z))
            parts.append(nut)
        items.append(fuse_all(parts))
    return Part.makeCompound(items)


def gw_sleeve():
    s = P.sleeve_size / 2.0
    sleeve = tube_span((-s, s), P.sleeve_y, P.sleeve_z, P.sleeve_wall)
    return sleeve.cut(cyl_x(P.depth_pin_d + 0.5, -40, 40, K.stem_center_y(), K.depth_pin_z()))


def gw_stem():
    s = P.stem_size / 2.0
    yc = K.stem_center_y()
    z0 = P.stem_z_bot
    stem = tube_span((-s, s), (yc - s, yc + s), (z0, z0 + P.stem_len), P.stem_wall)
    holes = []
    z = K.depth_pin_z() - 2 * P.depth_hole_pitch
    while z < z0 + P.stem_len - 12.0:
        holes.append(cyl_x(P.depth_pin_d + 0.5, -30, 30, yc, z))
        z += P.depth_hole_pitch
    return stem.cut(holes)


def gw_fork():
    hw = P.gw_fork_gap / 2.0
    yc, zc = K.crown_point()
    t = P.gw_fork_t
    crown = box_span((-hw - t, hw + t), (yc - 20.0, yc + 20.0), (P.stem_z_bot - P.crown_t, P.stem_z_bot))
    plates = []
    for sx in (-1, 1):
        x0 = hw if sx > 0 else -hw - t
        pl = stadium_yz((yc, zc - 2.0), P.gw_axle, P.gw_fork_w / 2.0, x0, t)
        pl = pl.cut(cyl_x(P.gw_axle_d + 0.5, x0 - 1, x0 + t + 1, *P.gw_axle))
        plates.append(pl)
    return fuse_all([crown] + plates)


def gw_pin():
    yc = K.stem_center_y()
    z = K.depth_pin_z()
    s = P.sleeve_size / 2.0
    pin = cyl_x(P.depth_pin_d, -s - 8.0, s + 14.0, yc, z)
    head = cyl_x(22.0, -s - 12.0, -s - 8.0, yc, z)
    clip = ring_x(16.0, 12.0, s + 6.0, s + 8.0, yc, z + 9.0)
    return fuse_all([pin, head, clip])


def gw_axle_bolt():
    hw = P.gw_fork_gap / 2.0 + P.gw_fork_t
    return bolt_x(P.gw_axle_d, 30, 13.0, 16.0, -hw, hw, *P.gw_axle)


def gw_wheel():
    """Kruiwagenwiel 3.00-4: band O 260 x 80, stalen velg 4", naaf met lagers."""
    y, z = P.gw_axle
    hw = P.gw_w / 2.0
    tire = ring_x(P.gw_d, P.gw_rim_d + 4.0, -hw, hw, 0, 0)
    try:
        tire = tire.makeFillet(22.0, [e for e in tire.Edges if e.Curve.Radius > P.gw_d / 2.0 - 1.0])
    except Exception:
        pass
    rim = ring_x(P.gw_rim_d + 4.0, P.gw_rim_d - 10.0, -hw + 10.0, hw - 10.0, 0, 0)
    disc = ring_x(P.gw_rim_d - 9.0, 34.0, -2.0, 2.0, 0, 0)
    hub = ring_x(34.0, P.gw_axle_d + 0.5, -P.gw_hub_len / 2.0, P.gw_hub_len / 2.0, 0, 0)
    tire.translate(V(0, y, z))
    rest = fuse_all([rim, disc, hub])
    rest.translate(V(0, y, z))
    return tire, rest


# ---------------------------------------------------------------------
# Doseerunit op de bovenplaat van de bok (wereldcoordinaten, vast aan de robot)
# ---------------------------------------------------------------------
def deck_z():
    return P.robot_beam_z_top + P.hs_top_t


def pump_shapes():
    """(pomp, filter + camlock, drukregelaar + manometer, verdeelblok): 12 V membraanpomp liggend langs x,
    staand zuigfilter met camlock 1" bovenop, vaste drukregelaar 2,0 bar, verdeelblok met 5 slangpilaren."""
    z0 = deck_z()
    py, pz = P.pump_axis
    (fx0, fx1), (fy0, fy1) = P.pump_feet
    hw, hh = P.pump_head
    feet = box_span((fx0, fx1), (fy0, fy1), (z0, z0 + 6.0))
    head = box_span(P.pump_head_x, (py - hw / 2.0, py + hw / 2.0), (z0 + 6.0, z0 + 6.0 + hh))
    motor = cyl_x(P.pump_motor_d, P.pump_motor_x[0], P.pump_motor_x[1], py, pz)
    ports = [Part.makeCylinder(7.0, 22.0, V(x, py, z0 + 6.0 + hh)) for x in pump_ports_x()]
    pump = fuse_all([feet, head, motor] + ports)

    fx, fy = P.filter_xy
    fr = P.filter_d / 2.0
    top = z0 + P.filter_len
    filt = fuse_all([box_span((fx - 25.0, fx + 25.0), (fy - 25.0, fy + 25.0), (z0, z0 + 6.0)),
                     Part.makeCylinder(fr - 4.0, P.filter_len - 30.0, V(fx, fy, z0 + 6.0)),
                     Part.makeCylinder(fr, 24.0, V(fx, fy, top - 24.0)),
                     Part.makeCylinder(9.0, 16.0, V(fx - fr + 2.0, fy, top - 12.0), V(-1, 0, 0)),
                     Part.makeCylinder(12.0, 14.0, V(fx, fy, top)),
                     Part.makeCylinder(18.0, 18.0, V(fx, fy, top + 14.0)),
                     Part.makeCylinder(14.0, P.camlock_len - 32.0, V(fx, fy, top + 32.0))])

    m = P.manifold_size
    my = sum(P.manifold_y) / 2.0
    mani = [box_span(P.manifold_x, P.manifold_y, (z0, z0 + m))]
    for x in manifold_barb_x():
        mani.append(Part.makeCylinder(5.0, 20.0, V(x, P.manifold_y[0], z0 + m / 2.0), V(0, -1, 0)))
    mani = fuse_all(mani)

    rx = P.regulator_x
    rr = P.regulator_d / 2.0
    r0 = z0 + m
    gz = r0 + 30.0
    reg = fuse_all([Part.makeCylinder(10.0, 6.0, V(rx, my, r0)),
                    Part.makeCylinder(rr, P.regulator_len, V(rx, my, r0 + 6.0)),
                    Part.makeCylinder(8.0, 16.0, V(rx, my, r0 + 6.0 + P.regulator_len)),
                    Part.makeCylinder(5.0, 22.0, V(rx, my + rr - 2.0, gz), Y),
                    Part.makeCylinder(P.gauge_d / 2.0, 24.0, V(rx, my + rr + 20.0, gz + 10.0), Y)])
    return pump, filt, reg, mani


def regulator_inlet():
    return (P.regulator_x, sum(P.manifold_y) / 2.0, deck_z() + P.manifold_size + 6.0 + P.regulator_len + 16.0)


def pump_ports_x():
    return (P.pump_head_x[0] + 20.0, P.pump_head_x[1] - 20.0)


def manifold_barb_x():
    x0, x1 = P.manifold_x
    step = (x1 - x0 - 20.0) / (len(P.row_x) - 1)
    return [x0 + 10.0 + i * step for i in range(len(P.row_x))]


def manifold_outlet(i):
    return (manifold_barb_x()[i], P.manifold_y[0] - 20.0, deck_z() + P.manifold_size / 2.0)


def link_hoses():
    """Verbindingsslangen: filter -> zuigkant pomp en perskant pomp -> drukregelaar, allebei voor de
    langgatplaten langs (op verschillende hoogte). De drukregelaar zit direct op het verdeelblok."""
    z0 = deck_z()
    fx, fy = P.filter_xy
    fr = P.filter_d / 2.0
    top = z0 + P.filter_len
    hh = P.pump_head[1]
    py = P.pump_axis[0]
    p_in, p_out = pump_ports_x()
    port_z = z0 + 6.0 + hh + 22.0
    f_out = (fx - fr - 14.0, fy, top - 12.0)
    h1 = hose([f_out, (f_out[0] - 25.0, fy, f_out[2]), (f_out[0] - 45.0, 24.0, 870.0), (p_in + 40.0, 24.0, 870.0),
               (p_in, -20.0, 860.0), (p_in, py, port_z + 40.0), (p_in, py, port_z)], P.link_hose_od)
    ri = regulator_inlet()
    h2 = hose([(p_out, py, port_z), (p_out, py, port_z + 30.0), (p_out + 10.0, 8.0, 815.0), (ri[0] - 30.0, 8.0, 815.0),
               (ri[0], ri[1] + 40.0, ri[2] + 45.0), (ri[0], ri[1], ri[2] + 30.0), ri], P.link_hose_od)
    return Part.makeCompound([h1, h2])


def outlet_hose(i, row_x, psi=0.0):
    """Slang van het verdeelblok (bok, vast) naar de spuitdophouder van rij i (hefraam, draait mee met psi)."""
    start = manifold_outlet(i)
    p1, u = nozzle_axis()
    top = nozzle_inlet()
    up = K.add(top, u, 45.0)
    up2 = (up[0] + 25.0, up[1] + 60.0)
    t, a, a2 = K.rot_up(top, psi), K.rot_up(up, psi), K.rot_up(up2, psi)
    lane = 640.0 + 22.0 * abs(i - (len(P.row_x) - 1) / 2.0)
    pts = [start,
           (start[0], start[1] - 35.0, start[2]),
           (start[0] + (row_x - start[0]) * 0.3, start[1] - 110.0, lane),
           (row_x, a2[0] + 40.0, max(a2[1] + 40.0, lane - 60.0)),
           (row_x, a2[0], a2[1]),
           (row_x, a[0], a[1]),
           (row_x, t[0], t[1])]
    return hose(pts, P.hose_od)


# ---------------------------------------------------------------------
# Referentie robot (alleen ter controle, geen onderdeel van het ontwerp)
# ---------------------------------------------------------------------
def robot_beam_x(y):
    p = P.robot_beam_profile
    half = P.robot_beam_length / 2.0
    zc = P.robot_beam_z_bot + p / 2.0
    t = tube_span((-half, half), (y - p / 2.0, y + p / 2.0), (P.robot_beam_z_bot, P.robot_beam_z_top),
                  P.robot_beam_wall)
    holes = []
    x = P.robot_hole_x_min
    while x <= P.robot_hole_x_max + 1e-6:
        holes += [cyl(P.robot_hole_d, p + 10, "z", x, y, zc), cyl(P.robot_hole_d, p + 10, "z", -x, y, zc)]
        x += P.robot_grid
    return t.cut(holes)


def robot_upper_beams():
    p = P.robot_beam_profile
    items = []
    for xc in P.robot_upper_beam_x:
        for sx in (-1, 1):
            x = sx * xc
            items.append(tube_span((x - p / 2.0, x + p / 2.0), (P.robot_upper_beam_y_rear, P.robot_upper_beam_y_front),
                                   (P.robot_beam_z_top, P.robot_upper_beam_z_top), P.robot_beam_wall))
    return Part.makeCompound(items)


def robot_wheel_unit(side):
    x = side * P.robot_wheel_x
    y = P.robot_wheel_y
    z = P.robot_axle_z
    tire = cyl_x(P.robot_tire_d, x - P.robot_tire_w / 2.0, x + P.robot_tire_w / 2.0, y, z)
    try:
        tire = tire.makeFillet(25.0, tire.Edges)
    except Exception:
        pass
    half_w = P.robot_bracket_w / 2.0
    half_l = P.robot_bracket_l / 2.0
    plates = [box_span((x + s * half_w - (4.0 if s > 0 else 0.0), x + s * half_w + (0.0 if s > 0 else 4.0)),
                       (y - half_l, y + half_l), (z - 40.0, P.robot_bracket_plate_z)) for s in (-1, 1)]
    top = box_span((x - half_w, x + half_w), (y - half_l, y + half_l), (P.robot_bracket_plate_z, P.robot_bracket_top_z))
    block = box_span((x - P.robot_block_w / 2.0, x + P.robot_block_w / 2.0),
                     (y - P.robot_block_l / 2.0, y + P.robot_block_l / 2.0), (P.robot_bracket_top_z, P.robot_beam_z_bot))
    return tire, fuse_all(plates + [top, block])
