"""Kinematica van de eenvoudige toediener (puur Python, geen FreeCAD nodig).

Hoeken psi in graden: + = achterkant van het hefraam omhoog (rotatie om de draaibouten van de bok).
Punten (y, z) in werktuigcoordinaten; frame-punten gelden in werkstand (psi = 0).
"""
import math

import lfs2_params as P


def rot_up(pt, psi, center=P.pivot):
    """Draai punt (y, z) om center over psi graden, + = punten achter center gaan omhoog."""
    a = math.radians(psi)
    dy, dz = pt[0] - center[0], pt[1] - center[1]
    return (center[0] + dy * math.cos(a) + dz * math.sin(a), center[1] + dz * math.cos(a) - dy * math.sin(a))


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def unit(a, b):
    d = dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def add(p, v, s=1.0):
    return (p[0] + v[0] * s, p[1] + v[1] * s)


# ---------------------------------------------------------------------
# Hefraam: arm van het draaipunt naar de voorkant van de balk
# ---------------------------------------------------------------------
def arm_axis():
    """Hartlijn arm: van het draaipunt naar het hart van de balk, afgesneden op de voorkant van de balk."""
    u = unit(P.pivot, (P.bar_y, P.bar_z))
    t = (P.bar_front - P.pivot[0]) / u[0]
    return P.pivot, add(P.pivot, u, t), u


def arm_angle():
    """Helling van de arm (graden, + = arm loopt naar voren omhoog)."""
    u = arm_axis()[2]
    return math.degrees(math.atan2(-u[1], -u[0]))


def arm_center_z(y):
    p0, p1, u = arm_axis()
    return p0[1] + (y - p0[0]) * u[1] / u[0]


def cross_center():
    return (P.cross_y, arm_center_z(P.cross_y) - P.cross_drop)


# ---------------------------------------------------------------------
# Actuator en langgat
#   huis op het hefraam (pen act_l, draait mee), stangoog in een langgat in de bok (vast).
#   Het langgat loopt vanaf act_a (onderkant) langs de actuator-as van het hefraam af.
# ---------------------------------------------------------------------
def _bisect(f, lo, hi, n=60):
    """f(lo) en f(hi) hebben een verschillend teken."""
    flo = f(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if (f(mid) > 0) == (flo > 0):
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return 0.5 * (lo + hi)


def frame_pin(psi=0.0):
    """Pen van het actuatorhuis op het hefraam bij hefhoek psi."""
    return rot_up(P.act_l, psi)


def slot_dir():
    """Richting van het langgat in de bok: langs de actuator-as (werkstand), van het hefraam af."""
    return unit(P.act_l, P.act_a)


def slot_len():
    """Langgat zo lang dat het hefraam float_up_deg omhoog kan zweven met de actuator helemaal uit."""
    u = slot_dir()
    return _bisect(lambda s: dist(add(P.act_a, u, s), frame_pin(P.float_up_deg)) - P.act_extended, 0.0, 300.0)


def slot_ends():
    """(onderkant, bovenkant) van het langgat in de bok (vast)."""
    return P.act_a, add(P.act_a, slot_dir(), slot_len())


def float_range():
    """(laagste, hoogste) hefhoek in werkstand (actuator helemaal uit, stangoog vrij in het langgat)."""
    lo_end, hi_end = slot_ends()
    lo = _bisect(lambda a: dist(lo_end, frame_pin(a)) - P.act_extended, -40.0, 5.0)
    hi = _bisect(lambda a: dist(hi_end, frame_pin(a)) - P.act_extended, -5.0, 40.0)
    return lo, hi


def lift_angle():
    """Hefhoek met de actuator helemaal in (stangoog trekt aan de onderkant van het langgat)."""
    return _bisect(lambda a: dist(P.act_a, frame_pin(a)) - P.act_retracted, -10.0, 70.0)


def act_length(psi, lifting=None):
    """Lengte (oog-oog) van de actuator bij hefhoek psi. Zweven: helemaal uit. Heffen (standaard boven het
    zweefbereik): het stangoog trekt aan de onderkant van het langgat."""
    if lifting is None:
        lifting = psi > float_range()[1] + 1e-6
    if not lifting:
        return P.act_extended
    return dist(P.act_a, frame_pin(psi))


def slot_pin(psi, length=None):
    """Positie van het stangoog in het langgat bij hefhoek psi en actuatorlengte length."""
    if length is None:
        length = act_length(psi)
    f = frame_pin(psi)
    lo_end, hi_end = slot_ends()
    if dist(lo_end, f) >= length:
        return lo_end
    if dist(hi_end, f) <= length:
        return hi_end
    u = slot_dir()
    s = _bisect(lambda t: dist(add(lo_end, u, t), f) - length, 0.0, slot_len())
    return add(lo_end, u, s)


def act_lever(psi=0.0, length=None):
    """Hefboomsarm (mm) van de actuatorkracht om het draaipunt."""
    f = frame_pin(psi)
    pin = slot_pin(psi, length)
    u = unit(f, pin)
    fy, fz = f[0] - P.pivot[0], f[1] - P.pivot[1]
    return abs(fy * u[1] - fz * u[0])


# ---------------------------------------------------------------------
# Mes (lokaal per rij, x = 0)
# ---------------------------------------------------------------------
def knife_dirs():
    a = math.radians(P.knife_angle)
    d = (math.sin(a), -math.cos(a))        # langs het mes, naar voren-onder
    n = (math.cos(a), math.sin(a))         # loodrecht, naar voren-boven (snijkant)
    return d, n


def _edge_at_z(offset, z):
    d, n = knife_dirs()
    p = add(P.knife_pivot, n, offset)
    t = (z - p[1]) / d[1]
    return add(p, d, t)


def knife_points():
    """Omtrek mes (y, z): boven voor, punt, onder achter, boven achter."""
    d, n = knife_dirs()
    h = P.knife_w / 2.0
    top_front = _edge_at_z(h, P.knife_top_z)
    tip = _edge_at_z(h, -P.knife_depth)
    top_rear = _edge_at_z(-h, P.knife_top_z)
    r = math.radians(P.knife_rake_deg)
    b = (-math.cos(r), math.sin(r))
    rear0 = add(P.knife_pivot, n, -h)
    # tip + s*b = rear0 + d*t
    det = b[0] * (-d[1]) - b[1] * (-d[0])
    rx, ry = rear0[0] - tip[0], rear0[1] - tip[1]
    s = (rx * (-d[1]) - ry * (-d[0])) / det
    rear_bottom = add(tip, b, s)
    return top_front, tip, rear_bottom, top_rear


def knife_tip():
    return knife_points()[1]


def shear_point():
    d, n = knife_dirs()
    return add(P.knife_pivot, d, P.shear_dist)


def disc_center():
    return P.disc_center


def disc_knife_gap():
    """Kleinste afstand (mm) tussen de omtrek van de schijf en de voorkant van het mes (zelfde vlak)."""
    top_front, tip, rear_bottom, top_rear = knife_points()
    c = P.disc_center
    best = 1e9
    for i in range(201):
        t = i / 200.0
        p = (top_front[0] + (tip[0] - top_front[0]) * t, top_front[1] + (tip[1] - top_front[1]) * t)
        best = min(best, dist(p, c))
    return best - P.disc_d / 2.0


def disc_exit_y():
    """y waar de schijf achter het hart uit de grond komt (snede aan het maaiveld)."""
    c = P.disc_center
    r = P.disc_d / 2.0
    return c[0] - math.sqrt(max(0.0, r * r - c[1] * c[1]))


def tube_offset():
    return -(P.knife_w / 2.0 + P.tube_gap + P.tube_od / 2.0)


def tube_ends():
    """(onderkant = uitstroom, bovenkant) van het RVS-buisje achter het mes."""
    off = tube_offset()
    return _edge_at_z(off, P.tube_out_z), _edge_at_z(off, P.tube_top_z)


def clip_points():
    off = tube_offset()
    return [_edge_at_z(off, z) for z in P.clip_z]


def clip_bolt_points():
    off = -(P.knife_w / 2.0 - 9.0)
    return [_edge_at_z(off, z) for z in P.clip_z]


# ---------------------------------------------------------------------
# Dieptewiel
# ---------------------------------------------------------------------
def stem_center_y():
    return 0.5 * (P.sleeve_y[0] + P.sleeve_y[1])


def crown_point():
    return (stem_center_y(), P.stem_z_bot - P.crown_t / 2.0)


def depth_pin_z():
    return P.sleeve_z[1] - 20.0


# ---------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------
def summary():
    lo, hi = float_range()
    lift = lift_angle()
    tip = knife_tip()
    wheel_low = P.gw_axle[1] - P.gw_d / 2.0
    out = {
        "arm_angle_deg": round(arm_angle(), 1),
        "slot_len": round(slot_len(), 1),
        "float_range_deg": (round(lo, 1), round(hi, 1)),
        "lift_angle_deg": round(lift, 1),
        "lever_work_mm": round(act_lever(0.0), 1),
        "lever_lifted_mm": round(act_lever(lift, P.act_retracted), 1),
        "free_travel_mm": round(P.act_extended - dist(P.act_a, frame_pin(0.0)), 1),
        "knife_tip": (round(tip[0], 1), round(tip[1], 1)),
        "tip_lifted": tuple(round(v, 1) for v in rot_up(tip, lift)),
        "wheel_lifted_clearance": round(rot_up(P.gw_axle, lift)[1] - P.gw_d / 2.0, 1),
        "wheel_float_mm": (round(rot_up(P.gw_axle, lo)[1] - P.gw_axle[1], 1),
                           round(rot_up(P.gw_axle, hi)[1] - P.gw_axle[1], 1)),
        "tip_float_mm": (round(rot_up(tip, lo)[1] - tip[1], 1), round(rot_up(tip, hi)[1] - tip[1], 1)),
        "wheel_bottom_z": wheel_low,
        "disc_knife_gap_mm": round(disc_knife_gap(), 1),
        "disc_exit_y": round(disc_exit_y(), 1),
        "knife_behind_disc_exit_mm": round(disc_exit_y() - (tip[0] - P.knife_depth * math.tan(math.radians(P.knife_angle))), 1),
        "disc_lifted_clearance": round(rot_up(P.disc_center, lift)[1] - P.disc_d / 2.0, 1),
    }
    return out


if __name__ == "__main__":
    for k, v in summary().items():
        print(k, v)
