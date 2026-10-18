import math

import Part
from FreeCAD import Vector as V

import aug_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


def cyl_x(d, x0, x1):
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, 0, 0), X)


def cyl_z(d, z0, z1, x):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, 0, z0), Z)


def hex_z(af, z0, z1, x):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(30 + 60 * k)), r * math.sin(math.radians(30 + 60 * k)), z0)
           for k in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def core():
    """Kernbuis Ø60 x 3 (binnen Ø54), 1420 lang, met het M12-gat (Ø12,4) 35 mm vanaf de aandrijfkant."""
    r = P.core_d / 2.0
    tube = cyl_x(P.core_d, 0.0, P.length).cut(cyl_x(P.core_id, -1.0, P.length + 1.0))
    return tube.cut(cyl_z(P.shear_hole_d, -r - 5, r + 5, P.shear_hole_x))


def blade():
    """Vijzelblad Ø300, rechtsgangig, gelast op de kernbuis."""
    r_in = P.core_d / 2.0 + 0.05
    r_out = P.blade_d / 2.0
    t = P.blade_t
    x0, x1 = P.blade_x
    helix = Part.makeHelix(P.blade_pitch, x1 - x0, r_out)
    prof = Part.makePolygon([V(r_in, 0, -t / 2), V(r_out, 0, -t / 2), V(r_out, 0, t / 2), V(r_in, 0, t / 2),
                             V(r_in, 0, -t / 2)])
    sweep = Part.Wire(helix).makePipeShell([prof], True, True)
    solid = sweep if sweep.ShapeType == "Solid" else Part.Solid(sweep)
    solid.rotate(V(0, 0, 0), Y, 90)          # z -> x (rechtsgangig blijft rechtsgangig)
    solid.translate(V(x0, 0, 0))
    return solid


def wear_bush():
    """Slijtvaste kunststof ring in de buis aan de passieve kant: Ø54 / Ø20 x 30, gelijk met de kopse kant."""
    x1 = P.length
    return cyl_x(P.bush_od, x1 - P.bush_len, x1).cut(cyl_x(P.bush_bore, x1 - P.bush_len - 1, x1 + 1))


def bolt_bosses():
    """2 opgelaste ringen Ø24 boven en onder het breekboutgat, met een vlakke kant op 35 uit het hart,
    zodat kop en borgmoer recht zitten (zoals op de foto van de oude wokkel)."""
    x = P.shear_hole_x
    outer = cyl_x(P.core_d, -1.0, P.length + 1.0)
    out = []
    for s in (1, -1):
        z0, z1 = sorted((s * (P.core_id / 2.0), s * P.boss_top))
        ring = cyl_z(P.boss_d, z0, z1, x).cut([outer, cyl_z(P.shear_hole_d, z0 - 1, z1 + 1, x)])
        out.append(ring)
    return out


def shear_bolt():
    """M12 breekbout met borgmoer, kop en moer op de vlakke ringen (de insteek van de aandrijving is niet getekend)."""
    t = P.boss_top
    x = P.shear_hole_x
    zb = t - P.shear_bolt_len
    return [cyl_z(12.0, zb, t, x), hex_z(18, t, t + 7.5, x), hex_z(18, -t - P.lock_nut_h, -t, x)]
