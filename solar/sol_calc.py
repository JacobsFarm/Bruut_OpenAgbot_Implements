import math

import sol_params as P

G = 9.81
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def area_m2():
    """Panel area (m2)."""
    return P.n_panels * P.panel_w * P.panel_l / 1e6


def peak_wp():
    return P.n_panels * P.panel_wp


def footprint_mm():
    """Canopy width (x) and length (y) in mm, including the gaps."""
    return P.n_panels * P.panel_w + (P.n_panels - 1) * P.panel_gap, P.panel_l


def overhang_mm():
    """Overhang of the canopy beyond the outer tire edge (x, each side) and beyond the wheel track (y)."""
    w, l = footprint_mm()
    return w / 2.0 - P.robot_track_outer, l / 2.0 - (P.robot_wheel_y + P.robot_tire_d / 2.0)


def battery_wh():
    total = P.batt_voltage * P.batt_ah
    return total, total * P.batt_usable


def day_yield_kwh(month):
    """Energy delivered to the battery on an average day of the month (0..11), kWh."""
    return peak_wp() / 1000.0 * P.psh_month[month] * P.system_derate


def year_yield_kwh():
    days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    return sum(day_yield_kwh(m) * days[m] for m in range(12))


def noon_power_w(sun_fraction=0.8):
    """Electrical power at the battery with a clear sky (fraction of Wp x derate)."""
    return peak_wp() * sun_fraction * P.system_derate


def task_energy_kwh(load_w):
    return load_w * P.work_h_day / 1000.0


def solar_share(month, load_w):
    """Fraction of the daily energy of the task that the canopy covers (max 1)."""
    return min(1.0, day_yield_kwh(month) / task_energy_kwh(load_w))


def runtime_h(load_w, solar_w):
    """Hours the usable battery lasts at this load with this solar power; None = never empties."""
    net = solar_w - load_w
    if net >= 0:
        return None
    return battery_wh()[1] / -net


def mass_panels():
    return P.n_panels * P.panel_mass


# ---------------------------------------------------------------------
# Wind and stability (rough hand calculation)
# ---------------------------------------------------------------------
def wind_pressure_pa():
    return 0.5 * P.air_rho * P.wind_v ** 2


def wind_uplift_n():
    """Uplift (or downforce) on the flat panel roof."""
    return wind_pressure_pa() * P.wind_cn_up * area_m2()


def wind_side_n():
    """Horizontal force on the roof in a gust with some angle of attack."""
    return wind_pressure_pa() * P.wind_cn_side * area_m2()


def tipping(canopy_mass, canopy_cg_z_mm):
    """Safety factor against tipping sideways over the outer tire edge, wind on the roof at full gust.
    Overturning: horizontal wind force at roof height. Restoring: weight minus uplift, arm = half track."""
    m_total = P.robot_mass + canopy_mass
    weight = m_total * G
    z_cg = (P.robot_mass * P.robot_cg_z + canopy_mass * canopy_cg_z_mm) / m_total
    f_side = wind_side_n()
    z_force = P.z_cross_top + P.panel_t / 2.0
    m_over = f_side * z_force / 1000.0
    m_rest = (weight - wind_uplift_n()) * P.robot_track_outer / 1000.0
    static_deg = math.degrees(math.atan(P.robot_track_outer / z_cg))
    return {
        "mass_kg": m_total,
        "cg_z_mm": z_cg,
        "static_tilt_deg": static_deg,
        "overturn_nm": m_over,
        "restoring_nm": m_rest,
        "safety": m_rest / m_over if m_over > 0 else None,
    }


# ---------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------
def tube_section(b, t):
    """Square tube b x b x t: second moment (mm4) and section modulus (mm3)."""
    i = (b ** 4 - (b - 2 * t) ** 4) / 12.0
    return i, i / (b / 2.0)


def cross_member_stress():
    """Stress (MPa) in a cross member between the rails: wind uplift plus panel weight, simply supported."""
    i, w = tube_section(P.cross, P.cross_wall)
    span = 2.0 * P.post_x
    load_n_mm = (wind_pressure_pa() * P.wind_cn_up * 1e-6 + P.panel_mass * G / (P.panel_w * P.panel_l)) \
        * P.panel_l / 2.0
    m = load_n_mm * span ** 2 / 8.0
    defl = 5.0 * load_n_mm * span ** 4 / (384.0 * P.steel_E * i)
    return m / w, defl


def strut_buckling_safety():
    """Euler buckling of one diagonal strut against the wind uplift shared by 4 struts, pinned ends."""
    od, wall = P.brace_d, P.brace_wall
    i = math.pi / 64.0 * (od ** 4 - (od - 2 * wall) ** 4)
    z0 = (P.z_long_bot + P.z_long_top) / 2.0
    dx = (total_x_end() - P.strut_x_out_from_edge) - (P.strut_x_in + od / 2.0)
    dz = (P.z_rail_top - od / 2.0) - z0
    length = math.hypot(dx, dz)
    pcr = math.pi ** 2 * P.steel_E * i / length ** 2
    load = (wind_uplift_n() / 4.0) * (length / dz)
    return length, pcr, load, pcr / load


def total_x_end():
    return (P.n_panels * P.panel_w + (P.n_panels - 1) * P.panel_gap) / 2.0


def report(canopy_mass=None, canopy_cg_z=None):
    w, l = footprint_mm()
    ox, oy = overhang_mm()
    total, usable = battery_wh()
    print("canopy %.0f x %.0f mm (%d panels), area %.2f m2, %.0f Wp" % (w, l, P.n_panels, area_m2(), peak_wp()))
    print("overhang beyond outer tires %.0f mm per side (x), %.0f mm beyond the tires front/rear (y)" % (ox, oy))
    print("noon power at the battery (clear sky): %.0f W" % noon_power_w())
    print("yield per day: " + ", ".join("%s %.1f" % (MONTHS[m], day_yield_kwh(m)) for m in range(12)) + " kWh")
    print("yield per year: %.0f kWh" % year_yield_kwh())
    for name, load in (("light task", P.light_task_w), ("heavy task", P.heavy_task_w)):
        e = task_energy_kwh(load)
        print("%-10s %.0f W x %.0f h = %.1f kWh/day; canopy covers %.0f %% in June, %.0f %% in March, %.0f %% in Dec" % (
            name, load, P.work_h_day, e, 100 * solar_share(5, load), 100 * solar_share(2, load),
            100 * solar_share(11, load)))
        rt = runtime_h(load, noon_power_w())
        rt0 = runtime_h(load, 0.0)
        print("           battery %.0f Wh usable: %.1f h without solar, %s at noon with solar" % (
            usable, rt0, "never empties" if rt is None else "%.1f h" % rt))
    print("wind %.0f m/s: pressure %.0f Pa, uplift %.0f N, side %.0f N" % (
        P.wind_v, wind_pressure_pa(), wind_uplift_n(), wind_side_n()))
    s, d = cross_member_stress()
    print("cross member: stress %.1f MPa (yield %.0f), deflection %.2f mm" % (s, P.steel_yield, d))
    length, pcr, load, sf = strut_buckling_safety()
    print("strut L %.0f mm, buckling load %.0f N, load %.0f N, safety %.0f" % (length, pcr, load, sf))
    if canopy_mass is not None:
        t = tipping(canopy_mass, canopy_cg_z)
        print("tipping: robot + canopy %.0f kg, CG z %.0f mm, static tilt limit %.0f deg, safety against %.0f m/s gust %.1f" % (
            t["mass_kg"], t["cg_z_mm"], t["static_tilt_deg"], P.wind_v, t["safety"]))
