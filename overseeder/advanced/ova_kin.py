"""Kinematica van de geavanceerde doorzaaimachine (puur Python, geen FreeCAD nodig).

- Balk aan een parallellogram (zoals de geavanceerde toediener): hefhoogte h in mm (+ = omhoog t.o.v. de
  ontwerphoogte); de balk blijft evenwijdig aan de robot en schuift over een boog met straal link_length.
- Actuator tussen pen B (achterframe, beweegt mee) en een pen in het langgat bij A (bok). In werkstand staat de
  actuator uit (440 mm) en zweeft de balk; de gasveren duwen de pen naar A en daarmee de balk omlaag.
- Elk element draait om zijn draaipunt: hoek drop in graden, + = arm achter omlaag (zelfde teken als de
  toediener, lfa_parts.rot_yz). De gaffel van de aandrukrol draait om zijn eigen scharnier (hoek chi, + = omlaag).
Punten (y, z) in werktuigcoordinaten bij h = 0 en drop = 0.
"""
import math

import ova_params as P


def rot_yz(point, angle_deg, center):
    """Draai (y, z) om center; + = punten achter center gaan omlaag (rechterhand om +x)."""
    a = math.radians(angle_deg)
    dy, dz = point[0] - center[0], point[1] - center[1]
    return (center[0] + dy * math.cos(a) - dz * math.sin(a), center[1] + dy * math.sin(a) + dz * math.cos(a))


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def unit(a, b):
    d = dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def add(p, v, s=1.0):
    return (p[0] + v[0] * s, p[1] + v[1] * s)


def _bisect(f, lo, hi, n=60):
    flo = f(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------
# Parallellogram, actuator en langgat (als build_lfa.py van de toediener)
# ---------------------------------------------------------------------
def lift_state(h):
    """(hoek stangen graden, verplaatsing y, verplaatsing z) van de balk bij hefhoogte h."""
    s = max(-0.5, min(0.95, h / P.link_length))
    theta = math.asin(s)
    return math.degrees(theta), P.link_length * (1.0 - math.cos(theta)), h


def bar_shift(h):
    t, dy, dz = lift_state(h)
    return dy, dz


def pin_b(h):
    dy, dz = bar_shift(h)
    return (P.act_b[0] + dy, P.act_b[1] + dz)


def ab_length(h):
    return dist(P.act_a, pin_b(h))


def h_for_ab(ab):
    """Hefhoogte waarbij de afstand A - B gelijk is aan ab (ab neemt af als de balk stijgt)."""
    lo, hi = -0.45 * P.link_length, 0.9 * P.link_length
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ab_length(mid) > ab:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def slot_dir():
    """Richting van het langgat vanaf A, weg van B (vast, langs de actuator in werkstand)."""
    return unit(P.act_b, P.act_a)


def slot_point(t):
    return add(P.act_a, slot_dir(), t)


def slot_pos(h, length=P.act_extended):
    """Positie van de pen langs het langgat (0 = bij A, act_slot = bovenkant) bij hefhoogte h: het punt op het
    langgat op afstand length van pen B."""
    b = pin_b(h)
    if dist(P.act_a, b) >= length:
        return 0.0
    if dist(slot_point(P.act_slot), b) <= length:
        return float(P.act_slot)
    return _bisect(lambda t: dist(slot_point(t), b) - length, 0.0, P.act_slot)


def float_range(length=P.act_extended):
    """(laagste, hoogste) hefhoogte bij actuatorlengte length: pen onderin (bij A) / bovenin het langgat."""
    hi_end = slot_point(P.act_slot)
    lo = h_for_ab(length)
    hi = _bisect(lambda h: dist(hi_end, pin_b(h)) - length, -0.45 * P.link_length, 0.9 * P.link_length)
    return lo, hi


def actuator_points(h, length=None):
    """(pen in het langgat, pen B). Zonder length: werkstand (uit) tot de pen onderin zit, daarboven getrokken."""
    b = pin_b(h)
    if length is None:
        length = P.act_extended if h <= float_range()[1] else ab_length(h)
    return slot_point(slot_pos(h, length)), b


def gas_anchor():
    return add(P.act_a, slot_dir(), P.gas_len_ext)


def gas_force(h, length=P.act_extended):
    """Kracht van de 2 gasveren op de pen (N). Pen bij A: ze duwen tegen de bok zelf, geen kracht op de balk."""
    s = slot_pos(h, length)
    if s <= 1e-6:
        return 0.0
    f0, f1 = P.gas_force
    return f0 + (f1 - f0) * s / P.act_slot


def gas_vertical(h, length=P.act_extended, dh=0.5):
    """Neerwaartse kracht (N) van de gasveren op de balk (virtuele arbeid: F * ds/dh)."""
    ds = (slot_pos(h + dh, length) - slot_pos(h - dh, length)) / (2.0 * dh)
    if ds <= 0.0:
        ds = -(ab_length(h + dh) - ab_length(h - dh)) / (2.0 * dh)
    return gas_force(h, length) * ds


def act_ratio(h):
    """mm actuatorslag per mm hefhoogte."""
    return -(ab_length(h + 0.5) - ab_length(h - 0.5))


# ---------------------------------------------------------------------
# Element (lokaal per rij, x = 0)
# ---------------------------------------------------------------------
def disc_center():
    return (P.disc_y, P.disc_z)


def rel_disc(p):
    return (P.disc_y + p[0], P.disc_z + p[1])


def lug_point(drop=0.0):
    return rot_yz((P.u_pivot[0] + P.u_lug_rel[0], P.u_pivot[1] + P.u_lug_rel[1]), drop, P.u_pivot)


def anchor_point():
    return (P.u_pivot[0] + P.u_anchor_rel[0], P.u_pivot[1] + P.u_anchor_rel[1])


def strut(drop=0.0):
    """(pen, richting naar de veerplaat, veerlengte)."""
    g = lug_point(drop)
    a = anchor_point()
    u = unit(g, a)
    t = P.u_anchor_plate[2]
    plate_bot = (a[1] - t / 2.0 - g[1]) / u[1]
    return g, u, plate_bot - (P.seat_offset + 4.0) - 0.5


def spring_force(drop=0.0):
    return max(0.0, P.spring_rate * (P.spring_free - strut(drop)[2]))


def spring_moment(drop=0.0):
    """Moment (Nmm) van de veerpoot om het draaipunt; + = arm omlaag."""
    g, u, _ = strut(drop)
    f = spring_force(drop)
    fy, fz = -u[0] * f, -u[1] * f
    ry, rz = g[0] - P.u_pivot[0], g[1] - P.u_pivot[1]
    return ry * fz - rz * fy


def stop_gap():
    """Afstand stelmoer - veerplaat in werkstand: de arm zakt dan unit_drop_deg."""
    return strut(P.unit_drop_deg)[2] - strut(0.0)[2]


def boot_points():
    """Omtrek zaaikouter (y_rel, z_rel t.o.v. hart schijf): punt, boog langs de schijf, bovenkant, achterkant."""
    r = P.boot_r
    zt = -(P.disc_d / 2.0 - P.boot_lift)
    a0, a1 = P.boot_arc_deg
    pts = []
    tip_y = -math.sqrt(max(0.0, r * r - zt * zt))
    pts.append((tip_y, zt))
    n = 8
    a_start = math.degrees(math.acos(-zt / r))
    for i in range(1, n + 1):
        a = math.radians(a_start + (a1 - a_start) * i / n)
        pts.append((-r * math.sin(a), -r * math.cos(a)))
    pts.append((-r, P.boot_top_z_rel))
    pts += list(P.boot_rear_rel)
    return pts


def boot_tip():
    return rel_disc(boot_points()[0])


def pw_pivot():
    return rel_disc(P.pw_pivot_rel)


def pw_axle(chi=0.0):
    return rot_yz(rel_disc(P.pw_axle_rel), chi, pw_pivot())


def pw_force(chi=0.0):
    """Kracht van de rol op de grond (N) bij gaffelhoek chi (+ = rol omlaag t.o.v. de arm)."""
    return max(0.0, P.pw_force - P.pw_rate * chi)


def seed_tube_bottom():
    return rel_disc((P.seed_tube_rel_y, P.boot_top_z_rel))


def depth_for_band(band_d):
    return (P.disc_d - band_d) / 2.0


# ---------------------------------------------------------------------
# Luchtzaaier
# ---------------------------------------------------------------------
def hopper_outline():
    """Buitenomtrek zaadbak (y, z): voor-boven, voor-onder, trechter naar het doseerhuis, achter."""
    return [(P.hop_y[1], P.hop_top_z), (P.hop_y[1], P.hop_side_z), (P.meter_y[1], P.meter_z[1]),
            (P.meter_y[0], P.meter_z[1]), (P.hop_y[0], P.hop_side_z), (P.hop_y[0], P.hop_top_z)]


def _area(poly):
    s = 0.0
    for i in range(len(poly)):
        y0, z0 = poly[i]
        y1, z1 = poly[(i + 1) % len(poly)]
        s += y0 * z1 - y1 * z0
    return abs(s) / 2.0


def hopper_volumes_l():
    """(vak gras voor, vak fijn zaad achter) in liter."""
    o = hopper_outline()
    db, dt = P.hop_divider
    front = [o[0], o[1], o[2], db, dt]
    rear = [dt, db, o[3], o[4], o[5]]
    w = (P.hop_x[1] - P.hop_x[0]) - 2 * P.hop_wall
    return _area(front) * w / 1.0e6, _area(rear) * w / 1.0e6


# ---------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------
def summary():
    lo, hi = float_range()
    lift_drop = P.unit_drop_deg
    disc_l = rot_yz(disc_center(), lift_drop, P.u_pivot)[1] + P.lift_height - P.disc_d / 2.0
    tip_l = rot_yz(boot_tip(), lift_drop, P.u_pivot)[1] + P.lift_height
    pw_l = rot_yz(pw_axle(P.pw_range[1]), lift_drop, P.u_pivot)[1] + P.lift_height - P.pw_d / 2.0
    return {
        "float_range_mm": (round(lo, 1), round(hi, 1)),
        "work_ab_mm": round(ab_length(0.0), 1),
        "slot_pos_work_mm": round(slot_pos(0.0), 1),
        "gas_force_work_N": round(gas_force(0.0)),
        "gas_vertical_work_N": round(gas_vertical(0.0)),
        "act_ratio_work_lifted": (round(act_ratio(0.0), 2), round(act_ratio(P.lift_height), 2)),
        "act_length_lifted": round(ab_length(P.lift_height), 1),
        "gas_anchor": tuple(round(v, 1) for v in gas_anchor()),
        "spring_len_work": round(strut(0.0)[2], 1),
        "spring_force_work_N": round(spring_force(0.0)),
        "spring_moment_work_Nm": round(spring_moment(0.0) / 1000.0, 2),
        "disc_lifted_clearance": round(disc_l, 1),
        "boot_tip": tuple(round(v, 1) for v in boot_tip()),
        "boot_lifted_z": round(tip_l, 1),
        "pw_lifted_clearance": round(pw_l, 1),
        "pw_axle": tuple(round(v, 1) for v in pw_axle()),
        "hopper_l": tuple(round(v, 1) for v in hopper_volumes_l()),
        "depth_per_band": [(b, depth_for_band(b)) for b in P.band_sizes],
    }


if __name__ == "__main__":
    for k, v in summary().items():
        print(k, v)
