"""Kinematica van de doorzaaimachine (puur Python, geen FreeCAD nodig).

Twee draaipunten:
- hefraam om de draaibouten van de bok, hoek psi (graden, + = achterkant omhoog), zoals simple_v2;
- elke sleeparm om zijn eigen draaipunt onder de balk, hoek phi (graden, + = arm achter omhoog, t.o.v. het hefraam).
Punten (y, z) in werktuigcoordinaten; frame- en armpunten gelden in werkstand (psi = 0, phi = 0).
De schijf staat 7 graden scheef: lokale schijfcoordinaten (x_l, y_l = y - y_schijf, z) worden om de verticale as
door het hart van de schijf gedraaid (disc_to_unit).
"""
import math

import ovs_params as P


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


def _bisect(f, lo, hi, n=60):
    """f(lo) en f(hi) hebben een verschillend teken."""
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
# Hefraam
# ---------------------------------------------------------------------
def arm_axis():
    """Hartlijn arm hefraam: van het draaipunt naar het hart van de balk, afgesneden op de voorkant van de balk."""
    u = unit(P.pivot, (P.bar_y, P.bar_z))
    t = (P.bar_front - P.pivot[0]) / u[0]
    return P.pivot, add(P.pivot, u, t), u


def arm_center_z(y):
    p0, p1, u = arm_axis()
    return p0[1] + (y - p0[0]) * u[1] / u[0]


def cross_center():
    return (P.cross_y, arm_center_z(P.cross_y))


# ---------------------------------------------------------------------
# Actuator en langgat (zelfde opzet als simple_v2)
# ---------------------------------------------------------------------
def frame_pin(psi=0.0):
    return rot_up(P.act_l, psi)


def slot_dir():
    return unit(P.act_l, P.act_a)


def slot_len():
    u = slot_dir()
    return _bisect(lambda s: dist(add(P.act_a, u, s), frame_pin(P.float_up_deg)) - P.act_extended, 0.0, 400.0)


def slot_ends():
    return P.act_a, add(P.act_a, slot_dir(), slot_len())


def float_range(length=P.act_extended):
    """(laagste, hoogste) hefhoek bij actuatorlengte length: stangoog onderin / bovenin het langgat."""
    lo_end, hi_end = slot_ends()
    lo = _bisect(lambda a: dist(lo_end, frame_pin(a)) - length, -40.0, 40.0)
    hi = _bisect(lambda a: dist(hi_end, frame_pin(a)) - length, -40.0, 40.0)
    return lo, hi


def lift_angle():
    """Hefhoek met de actuator helemaal in (stangoog trekt aan de onderkant van het langgat)."""
    return _bisect(lambda a: dist(P.act_a, frame_pin(a)) - P.act_retracted, -10.0, 40.0)


def act_length(psi, lifting=None):
    if lifting is None:
        lifting = psi > float_range()[1] + 1e-6
    if not lifting:
        return P.act_extended
    return dist(P.act_a, frame_pin(psi))


def slot_pin(psi, length=None):
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


def slot_pos(psi, length=None):
    """Positie van het stangoog langs het langgat (0 = onderkant, slot_len = bovenkant)."""
    return dist(P.act_a, slot_pin(psi, length))


def gas_force(psi, length=None):
    """Kracht (N) van de 2 gasveren op het stangoog, langs het langgat naar beneden. Onderin het langgat drukken
    ze tegen de bok zelf: dan geen kracht op het hefraam."""
    s = slot_pos(psi, length)
    if s <= 1e-6:
        return 0.0
    f0, f1 = P.gas_force
    return f0 + (f1 - f0) * s / slot_len()


def gas_moment(psi, length=None):
    """Moment (Nmm) van de gasveren om de draaibouten (+ = hefraam omlaag)."""
    return gas_force(psi, length) * act_lever(psi, length)


def gas_anchor():
    """Bovenste pen van de gasveren in de verlengde langgatplaten."""
    return add(P.act_a, slot_dir(), P.gas_len_ext)


def act_lever(psi=0.0, length=None):
    """Hefboomsarm (mm) van de actuatorkracht om het draaipunt."""
    f = frame_pin(psi)
    pin = slot_pin(psi, length)
    u = unit(f, pin)
    fy, fz = f[0] - P.pivot[0], f[1] - P.pivot[1]
    return abs(fy * u[1] - fz * u[0])


# ---------------------------------------------------------------------
# Sleeparm (lokaal per rij, x = 0 is het hart van de schijf)
# ---------------------------------------------------------------------
def u_arm_dir():
    """Richting van de arm: van het draaipunt door het hart van de schijf (naar achteren, licht dalend)."""
    return unit(P.u_pivot, P.disc_center)


def u_arm_z(y):
    u = u_arm_dir()
    return P.u_pivot[1] + (y - P.u_pivot[0]) * u[1] / u[0]


def u_lug_point():
    """Pen van de veerpoot op de arm (werkstand)."""
    return (P.u_lug_y, u_arm_z(P.u_lug_y) + P.u_arm_size / 2.0 + P.u_lug_h)


def u_anchor_point():
    """Gat in de ankerplaat (hart plaat)."""
    return (P.u_lug_y, 0.5 * (P.u_anchor_z[0] + P.u_anchor_z[1]))


def arm_point(pt, phi):
    """Punt van de sleeparm (werkstand) bij armhoek phi, in hefraam-coordinaten."""
    return rot_up(pt, phi, P.u_pivot)


def strut_geometry(phi):
    """(pen, richting naar de ankerplaat, lengte veer) bij armhoek phi."""
    g = arm_point(u_lug_point(), phi)
    a = u_anchor_point()
    u = unit(g, a)
    plate_bot = (P.u_anchor_z[0] - g[1]) / u[1]
    spring_len = plate_bot - (P.seat_offset + 4.0) - 0.5
    return g, u, spring_len


def spring_force(phi):
    """Veerkracht (N) bij armhoek phi (drukveer, + = drukt de arm omlaag)."""
    return max(0.0, P.spring_rate * (P.spring_free - strut_geometry(phi)[2]))


def spring_moment(phi):
    """Moment (Nmm) van de veerpoot om het draaipunt van de arm; + = arm omlaag."""
    g, u, _ = strut_geometry(phi)
    f = spring_force(phi)
    # kracht op de arm wijst van de ankerplaat naar de pen: -u
    fy, fz = -u[0] * f, -u[1] * f
    ry, rz = g[0] - P.u_pivot[0], g[1] - P.u_pivot[1]
    # moment om x (+ = achterkant omlaag voor punten achter het draaipunt): - (ry * fz - rz * fy) met ry < 0
    return ry * fz - rz * fy


def stop_gap():
    """Afstand (mm) waarover de stelmoer boven de ankerplaat zit: de arm zakt dan u_stop_deg."""
    return strut_geometry(-P.u_stop_deg)[2] - strut_geometry(0.0)[2]


# ---------------------------------------------------------------------
# Schijf, schoen, zaadbuis en aandrukrol
# ---------------------------------------------------------------------
def disc_to_unit(xl, yl, z):
    """Lokale schijfcoordinaten (x_l, y_l t.o.v. hart schijf, z) -> (x, y, z) van het element."""
    a = math.radians(P.disc_angle)
    return (xl * math.cos(a) - yl * math.sin(a), P.disc_center[0] + xl * math.sin(a) + yl * math.cos(a), z)


def disc_plane_x(y):
    """x van het middenvlak van de schijf op hoogte y (element)."""
    return -(y - P.disc_center[0]) * math.tan(math.radians(P.disc_angle))


def disc_exit_y():
    """y waar de schijf achter het hart uit de grond komt."""
    c = P.disc_center
    r = P.disc_d / 2.0
    return c[0] - math.sqrt(max(0.0, r * r - c[1] * c[1]))


def boot_x():
    """x_l-bereik van de zaaischoen (schaduwkant, -x)."""
    x1 = -P.disc_t / 2.0 - P.boot_gap
    return (x1 - P.boot_t, x1)


def boot_bottom_z():
    return -(P.disc_depth - P.boot_lift)


def tube_ends_local():
    """((x_l, y_l, z) onder, (x_l, y_l, z) boven) van de zaadbuis."""
    return ((P.tube_x[0], P.tube_bot[0], P.tube_bot[1]), (P.tube_x[1], P.tube_top[0], P.tube_top[1]))


def tube_top():
    return disc_to_unit(*tube_ends_local()[1])


def pw_link_pivot():
    """Scharnier van de rolarm op de sleeparm (werkstand)."""
    return (P.pw_link_y, u_arm_z(P.pw_link_y))


def pw_axle(chi=0.0):
    """As van de aandrukrol bij rolarmhoek chi (graden, + = rol omhoog t.o.v. de sleeparm)."""
    return rot_up(P.pw_axle, chi, pw_link_pivot())


def pw_force(chi=0.0):
    """Kracht van de rol op de grond (N) bij rolarmhoek chi (torsieveer)."""
    return max(0.0, P.pw_force + P.pw_rate * chi)


def depth_for_band(band_d):
    """Snijdiepte (mm) bij een dieptering van band_d."""
    return (P.disc_d - band_d) / 2.0


# ---------------------------------------------------------------------
# Zaadbak
# ---------------------------------------------------------------------
def hopper_outline():
    """Buitenomtrek zaadbak (y, z), linksom: voor-boven, voor-onder, trechter, achter."""
    return [(P.hop_y[1], P.hop_top_z), (P.hop_y[1], P.hop_side_z), (P.meter_y[1], P.meter_z[1]),
            (P.meter_y[0], P.meter_z[1]), (P.hop_y[0], P.hop_side_z), (P.hop_y[0], P.hop_top_z)]


def divider_line():
    """Schot: onderaan tussen de twee nokkenrollen, bovenaan verder naar achteren (groot vak voor gras)."""
    return ((0.5 * (P.shaft_main_y + P.shaft_fine_y), P.meter_z[1]), (P.hop_divider_y, P.hop_top_z))


def _area(poly):
    s = 0.0
    for i in range(len(poly)):
        y0, z0 = poly[i]
        y1, z1 = poly[(i + 1) % len(poly)]
        s += y0 * z1 - y1 * z0
    return abs(s) / 2.0


def hopper_volumes_l():
    """(vak gras, vak fijn zaad) in liter, binnenmaat tot de rand."""
    o = hopper_outline()
    (db, dt) = divider_line()
    front = [o[0], o[1], o[2], db, dt]
    rear = [dt, db, o[3], o[4], o[5]]
    w = (P.hop_x[1] - P.hop_x[0]) - 2 * P.hop_wall
    return _area(front) * w / 1.0e6, _area(rear) * w / 1.0e6


# ---------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------
def summary():
    lo, hi = float_range()
    lift = lift_angle()
    stop = -P.u_stop_deg
    disc_l = rot_up(arm_point(P.disc_center, stop), lift)
    pw_l = rot_up(arm_point(pw_axle(P.pw_link_range[0]), stop), lift)
    boot_l = rot_up(arm_point(disc_to_unit(boot_x()[1], P.boot_y[1], boot_bottom_z())[1:], stop), lift)
    return {
        "slot_len": round(slot_len(), 1),
        "float_range_deg": (round(lo, 1), round(hi, 1)),
        "lift_angle_deg": round(lift, 1),
        "work_length_mm": round(dist(P.act_a, frame_pin(0.0)), 1),
        "free_travel_mm": round(P.act_extended - dist(P.act_a, frame_pin(0.0)), 1),
        "lever_work_mm": round(act_lever(0.0), 1),
        "lever_lifted_mm": round(act_lever(lift, P.act_retracted), 1),
        "slot_pos_work_mm": round(slot_pos(0.0), 1),
        "gas_force_work_N": round(gas_force(0.0)),
        "disc_lifted_clearance": round(disc_l[1] - P.disc_d / 2.0, 1),
        "pw_lifted_clearance": round(pw_l[1] - P.pw_d / 2.0, 1),
        "boot_lifted_z": round(boot_l[1], 1),
        "disc_exit_y": round(disc_exit_y(), 1),
        "arm_angle_deg": round(math.degrees(math.atan2(-u_arm_dir()[1], -u_arm_dir()[0])), 1),
        "spring_len_work": round(strut_geometry(0.0)[2], 1),
        "spring_force_work_N": round(spring_force(0.0), 1),
        "spring_moment_work_Nm": round(spring_moment(0.0) / 1000.0, 2),
        "stop_gap_mm": round(stop_gap(), 1),
        "hopper_l": tuple(round(v, 1) for v in hopper_volumes_l()),
        "depth_per_band_mm": [(b, depth_for_band(b)) for b in P.band_sizes],
        "tube_top": tuple(round(v, 1) for v in tube_top()),
        "boot_bottom_z": boot_bottom_z(),
    }


if __name__ == "__main__":
    for k, v in summary().items():
        print(k, v)
