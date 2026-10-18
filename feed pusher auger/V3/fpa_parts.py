import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fpa_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)
AY = P.auger_y
AZ = P.auger_z


# ---------------------------------------------------------------------
# Basisfuncties (zelfde stijl als agbot_parts.py / lfa_parts.py)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl_x(d, x0, x1, y, z):
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_y(d, y0, y1, x, z):
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def tube_x(x, y, z, wall):
    return box_span(x, y, z).cut(box_span((x[0] - 1, x[1] + 1), (y[0] + wall, y[1] - wall), (z[0] + wall, z[1] - wall)))


def moved(shape, x=0.0, y=0.0, z=0.0):
    s = shape.copy()
    s.translate(V(x, y, z))
    return s


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
    """Gesloten polygoon in het y-z vlak, (y, z) wereld, geëxtrudeerd over +x."""
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0))


def poly_vz(points, x0, t):
    """Als poly_yz, maar met v = y - auger_y."""
    return poly_yz([(AY + v, z) for (v, z) in points], x0, t)


def hex_x(af, x0, x1, y, z):
    r = af / math.sqrt(3.0)
    pts = [V(x0, y + r * math.cos(math.radians(60 * i + 30)), z + r * math.sin(math.radians(60 * i + 30)))
           for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(x1 - x0, 0, 0))


def hex_y(af, y0, y1, x, z):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y0, z + r * math.sin(math.radians(60 * i))) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, y1 - y0, 0))


def hex_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def bolt_y(d, af, y_head, y_end, x, z):
    """Bout langs y: kop aan y_head (buitenkant), schacht tot y_end, moer net voor y_end."""
    s = 1.0 if y_end > y_head else -1.0
    k = 0.65 * d
    head = hex_y(af, y_head - s * k, y_head, x, z) if s > 0 else hex_y(af, y_head, y_head + k, x, z)
    lo, hi = sorted((y_head, y_end))
    shank = cyl_y(d, lo, hi, x, z)
    m = 0.8 * d
    nut_y = y_end - s * (m + 3.0)
    nut = hex_y(af, *sorted((nut_y, nut_y + s * m)), x=x, z=z)
    return [head, shank, nut]


def hull2d(pts):
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def stadium(c1, r1, c2, r2, n=72):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        pts.append((c1[0] + r1 * math.cos(a), c1[1] + r1 * math.sin(a)))
        pts.append((c2[0] + r2 * math.cos(a), c2[1] + r2 * math.sin(a)))
    return hull2d(pts)


# ---------------------------------------------------------------------
# Vijzel (draait mee: Placement-rotatie om de vijzelas)
# ---------------------------------------------------------------------
BUSH_X0 = P.x_sprocket - 20.0          # buiteneind lagertap (naaf kettingwiel)


def shear_bolt_x():
    return P.core_x[0] + P.shear_bolt_dx


def drive_bush():
    """Aandrijfbus (één draaistuk C45): lagertap Ø30 met spiebaan, kraag, holle insteek Ø53,7 x 200 in de kernbuis."""
    x0 = P.core_x[0]
    c0, c1 = P.bush_collar_x
    journal = cyl_x(P.shaft_d, BUSH_X0, c0 + 1.0, AY, AZ)
    collar = cyl_x(P.core_d, c0, c1, AY, AZ)
    spigot = cyl_x(P.bush_spigot_d, c1 - 1.0, x0 + P.bush_spigot_len, AY, AZ)
    b = fuse_all([journal, collar, spigot])
    b = b.cut(cyl_x(P.bush_spigot_id, c1, x0 + P.bush_spigot_len + 1, AY, AZ))
    key = box_span((BUSH_X0 + 3, BUSH_X0 + 48), (AY - 4, AY + 4), (AZ + P.shaft_d / 2 - 4, AZ + P.shaft_d / 2 + 1))
    hole = cyl_z(P.shear_hole_d, AZ - 40, AZ + 40, shear_bolt_x(), AY)
    return b.cut([key, hole])


def core():
    """V3 kernbuis Ø60 x 3 (binnen Ø54), 1420 lang, met het gat Ø12,4 voor de M12 breekbout."""
    x0, x1 = P.core_x
    r = P.core_d / 2.0
    tube = cyl_x(P.core_d, x0, x1, AY, AZ).cut(cyl_x(P.core_d - 2 * P.core_t, x0 - 1, x1 + 1, AY, AZ))
    return tube.cut(cyl_z(P.shear_hole_d, AZ - r - 5, AZ + r + 5, shear_bolt_x(), AY))


def bolt_bosses():
    """V3: 2 ringen op de kernbuis gelast, boven en onder het breekboutgat, met een vlakke kant op 35 mm uit het hart
    zodat kop en borgmoer recht zitten (zoals op de bestaande wokkel)."""
    x = shear_bolt_x()
    outer = cyl_x(P.core_d, P.core_x[0] - 1, P.core_x[1] + 1, AY, AZ)
    out = []
    for s in (1, -1):
        z0, z1 = sorted((AZ + s * (P.core_d / 2.0 - P.core_t), AZ + s * P.boss_top))
        out.append(cyl_z(P.boss_d, z0, z1, x, AY).cut([outer, cyl_z(P.shear_hole_d, z0 - 1, z1 + 1, x, AY)]))
    return out


def shear_bolt():
    """M12 breekbout met borgmoer, kop boven en moer onder op de vlakke ringen."""
    t = P.boss_top
    x = shear_bolt_x()
    return [cyl_z(P.shear_bolt_d, AZ + t - P.shear_bolt_len, AZ + t, x, AY),
            hex_z(18, AZ + t, AZ + t + 7.5, x, AY),
            hex_z(18, AZ - t - P.lock_nut_h, AZ - t, x, AY)]


# ---------------------------------------------------------------------
# Vrije kant: hangende strip met opgelaste pen Ø20, kunststof ring in de wokkel
# ---------------------------------------------------------------------
PIN_PLATE_X = (P.xo, P.xo + P.pin_plate_t)


def pin_plate():
    """Hangende strip 10 mm met 2 opgezette randen (zoals de oude ophanging), 4 gaten M12 boven de uitsparing."""
    xa, xb = PIN_PLATE_X
    v0, v1 = P.pin_plate_v
    z = P.pin_plate_z
    base = box_span((xa, xb), (AY + v0, AY + v1), z)
    lips = [box_span((xb - 1.0, xa + P.pin_lip), (AY + v, AY + v + P.pin_plate_t), z)
            for v in (v0, v1 - P.pin_plate_t)]
    pl = fuse_all([base] + lips)
    cuts = [cyl_x(P.pin_d, xa - 1, xb + 1, AY, AZ)]
    for v, zb in pin_bolt_spots():
        cuts.append(cyl_x(P.m12_hole, xa - 1, xb + 1, AY + v, zb))
    return pl.cut(cuts)


def pin():
    """Pen Ø20, door de strip gestoken en aan beide kanten gelast; steekt 35 mm uit de strip, de kunststof ring in."""
    return cyl_x(P.pin_d, P.pin_end_x, PIN_PLATE_X[1], AY, AZ)


def pin_bolt_spots():
    """(v, z wereld) van de 4 bouten, boven de uitsparing en buiten het bereik van het blad."""
    return [(v, z) for v in P.pin_bolt_v for z in P.pin_bolt_z]


def pin_plate_bolts():
    """M12 x 35: kop buiten op de strip, moer binnen tegen de eindplaat (boven de kap)."""
    out = []
    xn = PIN_PLATE_X[1]
    for v, z in pin_bolt_spots():
        y = AY + v
        out += [hex_x(19, xn, xn + 8.0, y, z), cyl_x(12.0, P.xi - 10.8 - 3.0, xn, y, z),
                hex_x(19, P.xi - 10.8, P.xi, y, z)]
    return out


def wear_bush():
    """V3: slijtvaste kunststof ring Ø54 / Ø20 x 30 in het rechter eind van de kernbuis (draait mee met de wokkel)."""
    x1 = P.core_x[1]
    x0 = x1 - P.wear_bush_len
    od = P.core_d - 2 * P.core_t
    return cyl_x(od, x0, x1, AY, AZ).cut(cyl_x(P.wear_bush_bore, x0 - 1, x1 + 1, AY, AZ))


def blade():
    r_in = P.core_d / 2.0 + 0.05       # tegen de kernbuis (lasnaad niet getekend)
    r_out = P.blade_d / 2.0
    t = P.blade_t
    length = P.blade_x[1] - P.blade_x[0]
    helix = Part.makeHelix(P.blade_pitch, length, r_out)
    prof = Part.makePolygon([V(r_in, 0, -t / 2), V(r_out, 0, -t / 2), V(r_out, 0, t / 2), V(r_in, 0, t / 2),
                             V(r_in, 0, -t / 2)])
    sweep = Part.Wire(helix).makePipeShell([prof], True, True)
    solid = sweep if sweep.ShapeType == "Solid" else Part.Solid(sweep)
    solid.rotate(V(0, 0, 0), Y, 90)          # z -> x (rechtsgangig blijft rechtsgangig)
    solid.translate(V(P.blade_x[0], AY, AZ))
    return solid


def sprocket(z_teeth, x0, y, z, bore, key=None):
    """Vereenvoudigd kettingwiel (rollen roller_d), naaf aan de buitenkant (-x). key = (b, t2): naafgroef boven."""
    d_p = P.pitch_d(z_teeth)
    w = P.sprocket_w
    body = cyl_x(d_p + 0.6 * P.roller_d, x0, x0 + w, y, z)
    for i in range(z_teeth):
        a = 2 * math.pi * i / z_teeth
        body = body.cut(cyl_x(P.roller_d + 0.2, x0 - 1, x0 + w + 1, y + d_p / 2 * math.cos(a), z + d_p / 2 * math.sin(a)))
    body = body.fuse(cyl_x(min(d_p * 0.7, 60), x0 - 18, x0, y, z)).removeSplitter()
    cuts = [cyl_x(bore, x0 - 20, x0 + w + 2, y, z)]
    if key is not None:
        b, t2 = key
        cuts.append(box_span((x0 - 20, x0 + w + 2), (y - b / 2, y + b / 2), (z, z + bore / 2 + t2)))
    return body.cut(cuts)


def auger_sprocket():
    return sprocket(P.z_auger, P.x_sprocket, AY, AZ, P.shaft_d, key=(8.0, 3.3))


def auger_key():
    """Spie 8x7 x 30 in de aandrijfbus (asgroef 4 diep), vrij van het UCF206-lager."""
    x0 = BUSH_X0 + 3.0
    zb = AZ + P.shaft_d / 2 - 4.0
    return box_span((x0, x0 + 30.0), (AY - 4.0, AY + 4.0), (zb, zb + 7.0))


# ---------------------------------------------------------------------
# Frame: kap, dwarsligger, zijplaat, lagerplaat
# ---------------------------------------------------------------------
def hood():
    w = Part.makePolygon([V(-P.xi, AY + v, AZ + dz) for (v, dz) in P.hood_pts])
    face = Part.Face(w.makeOffset2D(P.hood_t / 2.0, 0, False, False))
    h = face.extrude(V(2 * P.xi, 0, 0))
    z = P.hood_top_z
    return h.cut([cyl_z(11.0, z - 5, z + 5, x, AY + v) for (x, v) in P.foot_holes])


def hood_flat_length():
    pts = P.hood_pts
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def flap():
    v0 = P.hood_pts[0][0] + P.hood_t / 2.0
    return box_span((-P.xi, P.xi), (AY + v0, AY + v0 + P.flap_t), P.flap_z)


def clamp_strip():
    v0 = P.hood_pts[0][0] + P.hood_t / 2.0 + P.flap_t
    return box_span((-P.xi, P.xi), (AY + v0, AY + v0 + P.strip_t), P.strip_z)


def beam():
    x = (-P.xi + P.cap_t, P.xi - P.cap_t)
    return tube_x(x, (AY + P.beam_v[0], AY + P.beam_v[1]), P.beam_z, P.beam_wall)


def end_plate_holes(x0):
    """2x M12 door kopplaat en zijplaat (langs x), boven de ligger."""
    return [cyl_x(P.m12_hole, x0 - 1, x0 + P.plate_t + P.cap_t + 1, AY + v, P.cap_bolt_z) for v in P.cap_bolt_v]


def beam_caps():
    out = []
    for x0 in (-P.xi, P.xi - P.cap_t):
        cap = box_span((x0, x0 + P.cap_t), (AY + P.cap_v[0], AY + P.cap_v[1]), P.cap_z)
        out.append(cap.cut(end_plate_holes(min(x0, -P.xo) if x0 < 0 else x0)))
    return out


def ucf_hole_cuts(x0):
    out = [cyl_x(P.shaft_d + 14, x0 - 1, x0 + P.plate_t + 1, AY, AZ)]
    for dy in (-P.ucf_J / 2, P.ucf_J / 2):
        for dz in (-P.ucf_J / 2, P.ucf_J / 2):
            out.append(cyl_x(P.m12_hole, x0 - 1, x0 + P.plate_t + 1, AY + dy, AZ + dz))
    return out


def side_plate_left():
    x0 = -P.xo
    pl = poly_vz(P.side_left_pts, x0, P.plate_t)
    pl = pl.cut(ucf_hole_cuts(x0) + end_plate_holes(x0) + skid_holes())
    # draaipunt kettingspanner
    pl = pl.cut(cyl_x(12.5, x0 - 1, x0 + P.plate_t + 1, AY + P.tens_pivot[0], P.tens_pivot[1]))
    return pl


def bearing_plate_right():
    x0 = P.xi
    pl = poly_vz(P.side_right_pts, x0, P.plate_t)
    cuts = [cyl_x(P.m12_hole, x0 - 1, x0 + P.plate_t + 1, AY + v, z) for v, z in pin_bolt_spots()]
    return pl.cut(cuts + end_plate_holes(P.xi - P.cap_t))


def hood_brackets():
    """Zethoekjes 40x40x3 (als blok getekend) binnen de kap, waarmee de kap aan zijplaat en lagerplaat zit."""
    out = []
    h = P.hood_t / 2.0
    back_y = (AY + P.hood_pts[0][0] - h - 15.0, AY + P.hood_pts[0][0] - h)
    top_z = (P.hood_top_z - h - 15.0, P.hood_top_z - h)
    spots = {-P.xi: [("back", -60.0), ("back", 100.0), ("top", -60.0), ("top", 60.0)],
             P.xi - 40.0: [("back", 100.0), ("top", 0.0)]}
    for x0, items in spots.items():
        for kind, pos in items:
            if kind == "back":
                out.append(box_span((x0, x0 + 40.0), back_y, (AZ + pos - 15.0, AZ + pos + 15.0)))
            else:
                out.append(box_span((x0, x0 + 40.0), (AY + pos - 15.0, AY + pos + 15.0), top_z))
    return out


def skid():
    x0, x1 = -P.xo - (P.skid_w - P.plate_t) / 2.0, -P.xi + (P.skid_w - P.plate_t) / 2.0
    s = box_span((x0, x1), (AY + P.skid_v[0], AY + P.skid_v[1]), P.skid_z)
    slot = box_span((-P.xo - 0.2, -P.xi + 0.2), (AY + P.skid_v[0] - 1, AY + P.skid_v[1] + 1), (15.0, P.skid_z[1] + 1))
    return s.cut([slot] + skid_holes())


def skid_holes():
    return [cyl_x(8.4, -P.xo - 30.0, -P.xi + 30.0, AY + v, 24.0) for v in (P.skid_v[0] + 22.0, P.skid_v[1] - 22.0)]


def skid_bolts():
    out = []
    for v in (P.skid_v[0] + 22.0, P.skid_v[1] - 22.0):
        out.append(cyl_x(8.0, -P.xo - 14.0, -P.xi + 14.0, AY + v, 24.0))
        out.append(hex_x(13, -P.xo - 19.0, -P.xo - 14.0, AY + v, 24.0))
        out.append(hex_x(13, -P.xi + 14.0, -P.xi + 20.5, AY + v, 24.0))
    return out


# ---------------------------------------------------------------------
# Lagers
# ---------------------------------------------------------------------
def ucf206(x_face, s):
    """UCF206 vierkante flens, s = +1: flens tegen het vlak x_face, naar +x; -1: naar -x."""
    L, J, tf = P.ucf_L, P.ucf_J, P.ucf_tf
    x0 = x_face if s > 0 else x_face - tf
    fl = box_span((x0, x0 + tf), (AY - L / 2, AY + L / 2), (AZ - L / 2, AZ + L / 2))
    edges = [e for e in fl.Edges if abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) > 1]
    fl = fl.makeFillet(18.0, edges)
    bx = x0 + tf if s > 0 else x0 - 24.0
    boss = cyl_x(80, bx, bx + 24.0, AY, AZ)
    rx = x_face + tf - 12.0 if s > 0 else x_face - tf - 32.0
    ring = cyl_x(48, rx, rx + 44.0, AY, AZ)
    h = fl.fuse([boss, ring]).removeSplitter()
    for dy in (-J / 2, J / 2):
        for dz in (-J / 2, J / 2):
            h = h.cut(cyl_x(14, x0 - 1, x0 + tf + 1, AY + dy, AZ + dz))
    return h.cut(cyl_x(P.shaft_d + 0.4, x_face - 60, x_face + 60, AY, AZ))


def ucf_bolts(x_face, s):
    J = P.ucf_J
    out = []
    for dy in (-J / 2, J / 2):
        for dz in (-J / 2, J / 2):
            y, z = AY + dy, AZ + dz
            if s < 0:     # flens links buiten, plaat x -728..-720
                xa, xb = x_face - P.ucf_tf, x_face + P.plate_t
                out += [hex_x(19, xa - 8.0, xa, y, z), cyl_x(12, xa, xb + 14.0, y, z), hex_x(19, xb, xb + 10.8, y, z)]
            else:         # flens rechts buiten, plaat x 720..728
                xa, xb = x_face - P.plate_t, x_face + P.ucf_tf
                out += [hex_x(19, xa - 10.8, xa, y, z), cyl_x(12, xa - 14.0, xb, y, z), hex_x(19, xb, xb + 8.0, y, z)]
    return out


def cap_bolts():
    out = []
    z = P.cap_bolt_z
    for v in P.cap_bolt_v:
        y = AY + v
        out += [hex_x(19, -P.xo - 8.0, -P.xo, y, z), cyl_x(12, -P.xo, -P.xi + P.cap_t + 14.0, y, z),
                hex_x(19, -P.xi + P.cap_t, -P.xi + P.cap_t + 10.8, y, z)]
        out += [hex_x(19, P.xo, P.xo + 8.0, y, z), cyl_x(12, P.xi - P.cap_t - 14.0, P.xo, y, z),
                hex_x(19, P.xi - P.cap_t - 10.8, P.xi - P.cap_t, y, z)]
    return out


# ---------------------------------------------------------------------
# Aandrijving: voetmotor op de kap, ketting, spanner, kast
# ---------------------------------------------------------------------
MY = AY + P.motor_v
MZ = P.motor_z


def motor_base():
    """Motorplaat op de kap met opstaande rand tegen de ligger: de kettingtrek gaat via de ligger, niet via de kap."""
    z0 = P.hood_top_outer
    plate = box_span(P.base_x, (AY + P.base_v[0], AY + P.base_v[1]), (z0, z0 + P.base_t))
    up = box_span(P.base_x, (AY + P.base_v[1] - P.base_t, AY + P.base_v[1]), (z0 + P.base_t, z0 + P.base_up_z))
    plate = plate.fuse(up).removeSplitter()
    for (x, v) in P.foot_holes:
        # langgaten 20 mm in v: uitlijnen van de kettingwielen
        plate = plate.cut(box_span((x - 5.5, x + 5.5), (AY + v - 10, AY + v + 10), (z0 - 1, z0 + P.base_t + 1)))
    for x in P.base_bolt_x:
        plate = plate.cut(cyl_y(11.0, AY + P.base_v[1] - P.base_t - 1, AY + P.base_v[1] + 1, x, base_bolt_z()))
    return plate


def base_bolt_z():
    return P.hood_top_outer + (P.base_t + P.base_up_z) / 2.0


def base_bolts():
    out = []
    for x in P.base_bolt_x:
        out += bolt_y(10.0, 17, AY + P.base_v[1] - P.base_t, AY + P.beam_v[1] + 12.0, x, base_bolt_z())
    return out


def gearmotor():
    """Tandwielmotor 800 W met voet (maattekening parts/800 watt motor): neus, tandwielkast met ring, motorhuis, voet."""
    zf = P.hood_top_outer + P.base_t
    mx = P.motor_x
    d0, d1, da, db = P.motor_nose
    nose = Part.makeCone(da / 2.0, db / 2.0, d1 - d0, V(mx(d0), MY, MZ), X)
    ring = cyl_x(P.motor_ring[2], mx(P.motor_ring[0]), mx(P.motor_ring[1]), MY, MZ)
    body = cyl_x(P.motor_body[2], mx(P.motor_body[0]), mx(P.motor_body[1]), MY, MZ)
    cap = cyl_x(P.motor_cap[2], mx(P.motor_cap[0]), mx(P.motor_cap[1]), MY, MZ)
    foot = box_span(P.foot_x, (AY + P.foot_v[0], AY + P.foot_v[1]), (zf, zf + P.foot_t))
    saddle = box_span((P.foot_x[0] + 8.0, P.foot_x[1] - 8.0), (MY - 24.0, MY + 24.0), (zf + P.foot_t - 1.0, MZ - 30.0))
    for (x, v) in P.foot_holes:
        foot = foot.cut(cyl_z(P.motor_foot_hole, zf - 1, zf + P.foot_t + 1, x, AY + v))
    return fuse_all([nose, ring, body, cap, foot, saddle])


def foot_bolts():
    """M8 door voet, motorplaat en kap; moer onder de kap."""
    zf = P.hood_top_outer
    out = []
    for (x, v) in P.foot_holes:
        y = AY + v
        out += [cyl_z(8, zf - P.hood_t - 12, zf + P.base_t + P.foot_t + 3, x, y),
                hex_z(13, zf + P.base_t + P.foot_t, zf + P.base_t + P.foot_t + 5.3, x, y),
                hex_z(13, zf - P.hood_t - 6.4, zf - P.hood_t, x, y)]
    return out


def motor_shaft():
    """Uitgaande as Ø19 h6 met spiebaan 6 x 3,5 (DIN 6885), 35 mm uit de neus."""
    x0 = P.motor_shaft_end_x
    s = cyl_x(P.motor_shaft_d, x0, P.motor_x(P.motor_nose[0]), MY, MZ)
    b, h, t1, t2, length = P.motor_key
    r = P.motor_shaft_d / 2.0
    groove = box_span((x0 + 2.0, x0 + 2.0 + length), (MY - b / 2, MY + b / 2), (MZ + r - t1, MZ + r + 1))
    return s.cut(groove)


def motor_key():
    """Spie 6x6 x 25 (DIN 6885 A) in de motoras, onder het kettingwiel."""
    x0 = P.motor_shaft_end_x
    b, h, t1, t2, length = P.motor_key
    zb = MZ + P.motor_shaft_d / 2.0 - t1
    return box_span((x0 + 2.0, x0 + 2.0 + length), (MY - b / 2, MY + b / 2), (zb, zb + h))


def motor_sprocket():
    return sprocket(P.z_motor, P.x_sprocket, MY, MZ, P.motor_shaft_d, key=(P.motor_key[0], P.motor_key[3]))


def chain_centers():
    return (AY, AZ, P.pitch_d(P.z_auger) / 2.0), (MY, MZ, P.pitch_d(P.z_motor) / 2.0)


def chain():
    (y1, z1, r1), (y2, z2, r2) = chain_centers()
    x0 = P.x_sprocket - 2.0
    # getekend als band van de schakelplaten buiten de tandtoppen (rollen niet getekend)
    ro, ri = 0.75 * P.chain_pitch, 0.35 * P.roller_d + 0.3      # schakelplaten buiten de tandtoppen
    outer = poly_yz(stadium((y1, z1), r1 + ro, (y2, z2), r2 + ro), x0, P.sprocket_w + 4)
    inner = poly_yz(stadium((y1, z1), r1 + ri, (y2, z2), r2 + ri), x0 - 1, P.sprocket_w + 6)
    return outer.cut(inner)


def strand(side):
    """Rechte kettingpart tussen de wielen aan de kant side (+1 = naar de robot, -1 = voorkant)."""
    (y1, z1, r1), (y2, z2, r2) = chain_centers()
    dy, dz = y2 - y1, z2 - z1
    d = math.hypot(dy, dz)
    a = math.atan2(dz, dy)
    b = math.acos((r1 - r2) / d)
    ang = a - side * b
    p1 = (y1 + r1 * math.cos(ang), z1 + r1 * math.sin(ang))
    p2 = (y2 + r2 * math.cos(ang), z2 + r2 * math.sin(ang))
    return p1, p2, (math.cos(ang), math.sin(ang))


def tensioner():
    """Kettingspanner aan de slappe kant (robotzijde), binnen de lus: arm + nylon spanwiel, rubber torsie-element."""
    p1, p2, n = strand(1)
    px, pz = AY + P.tens_pivot[0], P.tens_pivot[1]
    # punt op de part het dichtst bij het draaipunt
    ty, tz = p2[0] - p1[0], p2[1] - p1[1]
    tl = math.hypot(ty, tz)
    ty, tz = ty / tl, tz / tl
    s = (px - p1[0]) * ty + (pz - p1[1]) * tz
    s = max(0.35 * tl, min(0.65 * tl, s))
    cy, cz = p1[0] + s * ty, p1[1] + s * tz
    r = P.tens_idler_d / 2.0
    iy, iz = cy - n[0] * (r + 4.0), cz - n[1] * (r + 4.0)      # tegen de binnenkant van de ketting
    xw = P.x_sprocket
    idler = cyl_x(P.tens_idler_d, xw - 1.0, xw + P.sprocket_w + 1.0, iy, iz).cut(
        cyl_x(10.0, xw - 2.0, xw + P.sprocket_w + 2.0, iy, iz))
    x_arm = (-P.xo - 30.0, -P.xo - 20.0)
    body = box_span((-P.xo - 20.0, -P.xo), (px - 22, px + 22), (pz - 22, pz + 22))
    arm = poly_yz([(px - 10, pz), (px + 10, pz), (iy + 10, iz), (iy - 10, iz)], x_arm[0], 10.0)
    arm = arm.fuse([cyl_x(28, x_arm[0], x_arm[1], px, pz), cyl_x(28, x_arm[0], x_arm[1], iy, iz)])
    holes = [cyl_x(12.4, x_arm[0] - 1, -P.xo + 1, px, pz), cyl_x(10.4, x_arm[0] - 1, x_arm[1] + 1, iy, iz)]
    body = body.cut(holes)
    arm = arm.cut(holes)
    stud = cyl_x(10.0, xw - 1.0, x_arm[1], iy, iz)
    bolt = [cyl_x(12.0, -P.xo - 34.0, -P.xi + 14.0, px, pz), hex_x(19, -P.xo - 42.0, -P.xo - 34.0, px, pz),
            hex_x(19, -P.xi, -P.xi + 10.8, px, pz)]
    return fuse_all([body, arm]), idler, [stud] + bolt


def chain_guard():
    (y1, z1, r1), (y2, z2, r2) = chain_centers()
    x_out = P.x_sprocket - 24.0          # buiten de naven
    x_in = -P.xo - P.ucf_tf - 40.0       # open naar de zijplaat, buiten het lager
    t = 2.0
    g = P.guard_gap
    out = poly_yz(stadium((y1, z1), r1 + g, (y2, z2), r2 + g), x_out - t, x_in - x_out + t)
    inn = poly_yz(stadium((y1, z1), r1 + g - t, (y2, z2), r2 + g - t), x_out, x_in - x_out + 1)
    return out.cut(inn)


# ---------------------------------------------------------------------
# Armen naar de wielmodules (4x): adapterplaat op de achterste flens, schot, eindplaat op de ligger
# ---------------------------------------------------------------------
def arm_spots():
    """(x gat, kant van het schot) voor de 4 armen. Het schot zit aan de kant weg van de band."""
    out = []
    for sx in (-1, 1):
        xw = sx * P.robot_wheel_x
        out.append((xw - sx * P.wf_hole_dx, -sx))    # binnenflens, schot naar het robotmidden
        out.append((xw + sx * P.wf_hole_dx, sx))     # buitenflens, schot naar buiten
    return out


def arm(x_hole, web_side):
    t = P.arm_t
    y_face = P.wf_face_y
    y_end = AY + P.beam_v[1]                  # voorvlak ligger (robotzijde)
    a0, a1 = x_hole - P.adapter_w / 2.0, x_hole + P.adapter_w / 2.0
    adapter = box_span((a0, a1), (y_face - t, y_face), P.adapter_z)
    for z in P.wf_hole_z:
        adapter = adapter.cut(cyl_y(11.0, y_face - t - 1, y_face + 1, x_hole, z))
    xw0 = a1 - t if web_side > 0 else a0
    yb = y_end + t
    ez = (P.cap_z[0] - 10.0, P.cap_z[1])
    web = poly_yz([(y_face - t, P.adapter_z[1]), (yb, ez[1]), (yb, ez[0]), (y_face - t, P.adapter_z[0] + 30.0)], 0.0, t)
    web.translate(V(xw0, 0, 0))
    web = web.cut(box_span((xw0 - 1, xw0 + t + 1), (y_face - t - 1, y_face + 1), (0, 1000)))
    xc = xw0 + t / 2.0
    end = box_span((xc - P.end_w / 2.0, xc + P.end_w / 2.0), (y_end, yb), ez)
    for dx in (-P.end_bolt_dx, P.end_bolt_dx):
        for zc in P.end_bolt_z:
            sl = box_span((xc + dx - 6.5, xc + dx + 6.5), (y_end - 1, yb + 1), (zc - P.end_slot / 2, zc + P.end_slot / 2))
            sl = sl.fuse([cyl_y(13.0, y_end - 1, yb + 1, xc + dx, zc - P.end_slot / 2),
                          cyl_y(13.0, y_end - 1, yb + 1, xc + dx, zc + P.end_slot / 2)])
            end = end.cut(sl)
    return fuse_all([adapter, web, end]), xc


def arm_bolts(x_hole, xc):
    out = []
    for z in P.wf_hole_z:          # M10 x 35 door adapterplaat + flens
        out += bolt_y(10.0, 17, P.wf_face_y - P.arm_t, P.wf_face_y + P.wf_t + 12.0, x_hole, z)
    y0 = AY + P.beam_v[1] + P.arm_t
    y1 = AY + P.beam_v[0] - 14.0
    for dx in (-P.end_bolt_dx, P.end_bolt_dx):
        for zc in P.end_bolt_z:   # M12 door eindplaat en ligger
            out += bolt_y(12.0, 19, y0, y1, xc + dx, zc)
    return out


def beam_arm_holes(xcs):
    tools = [cyl_y(11.0, AY + P.beam_v[0] - 1, AY + P.beam_v[1] + 1, x, base_bolt_z()) for x in P.base_bolt_x]
    for xc in xcs:
        for dx in (-P.end_bolt_dx, P.end_bolt_dx):
            for zc in P.end_bolt_z:
                tools.append(cyl_y(13.0, AY + P.beam_v[0] - 1, AY + P.beam_v[1] + 1, xc + dx, zc))
    return tools


# ---------------------------------------------------------------------
# Contragewicht voorop
# ---------------------------------------------------------------------
def ballast():
    z0 = P.robot_lower_beam_z[1]
    out = []
    for sx in (-1, 1):
        x = sorted((sx * P.ballast_x[0], sx * P.ballast_x[1]))
        b = box_span(x, P.ballast_y, (z0, z0 + P.ballast_h))
        for xh in (sx * 175.0, sx * 225.0):
            b = b.cut(cyl_z(11.0, z0 - 1, z0 + P.ballast_h + 1, xh, P.robot_front_beam_y))
        out.append(b)
    return out


def ballast_bolts():
    z0 = P.robot_lower_beam_z[0]
    z1 = P.robot_lower_beam_z[1] + P.ballast_h
    out = []
    for sx in (-1, 1):
        for xh in (sx * 175.0, sx * 225.0):    # gaten in het 50 mm-raster van de balk
            out += [cyl_z(10.0, z0 - 12.0, z1 + 10.0, xh, P.robot_front_beam_y), hex_z(17, z1, z1 + 6.4, xh, P.robot_front_beam_y),
                    hex_z(17, z0 - 8.4, z0, xh, P.robot_front_beam_y)]
    return out
