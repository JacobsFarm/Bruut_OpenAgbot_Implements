"""Calculations for the fertilizer spreader, in pure Python (same parameters as the model).

    import fsp_calc
    fsp_calc.report()          # prints and returns all key figures

Masses come from build_fsp.mass_properties() (copied into fsp_params.MODEL_MASS after a rebuild).
"""
import math

import fsp_params as P


def throw(rpm=P.disc_rpm, h=None, dt=1e-4):
    """Throw distance (m) of a granule from the disc rim: exit speed = v_factor x tip speed, launched horizontally from
    the vane top, quadratic air drag. Returns (distance from the disc centre, exit speed m/s, flight time s)."""
    h = (P.disc_z + P.disc_t + P.vane_h / 2.0) / 1000.0 if h is None else h
    r = P.disc_d / 2000.0
    v0 = P.v_factor * rpm * 2 * math.pi / 60.0 * r
    m = P.granule_rho * math.pi / 6.0 * P.granule_d ** 3
    k = 0.5 * P.air_rho * P.cd * math.pi / 4.0 * P.granule_d ** 2 / m
    a = math.radians(P.launch_deg)
    x, z, vx, vz, t = 0.0, h, v0 * math.cos(a), v0 * math.sin(a), 0.0
    while z > 0.0:
        v = math.hypot(vx, vz)
        vx -= k * v * vx * dt
        vz -= (P.g + k * v * vz) * dt
        x += vx * dt
        z += vz * dt
        t += dt
    return x + r, v0, t


def width(rpm=P.disc_rpm):
    """Throw width (both sides, m) and driving width (m) with overlap for an even (triangular) pattern."""
    d, _, _ = throw(rpm)
    return 2 * d, 2 * d * P.overlap


def dose_rate(kg_ha, rpm=P.disc_rpm, speed=P.speed):
    """Mass flow (kg/s) and metering roller speed (rpm) for a dose (kg/ha)."""
    _, w = width(rpm)
    flow = kg_ha * w * speed / 10000.0
    ml_s = flow / P.fill_density * 1000.0
    return flow, ml_s / P.roller_ml_per_rev() * 60.0


def doses():
    out = {}
    for kg in P.dose_kg_ha:
        flow, n = dose_rate(kg)
        out["%d_kg_ha" % kg] = {"flow_kg_s": round(flow, 3), "roller_rpm": round(n, 1),
                                "ok": n <= P.meter_rpm_max, "ha_per_fill": round(P.MODEL_MASS["fill_kg"] / kg, 2),
                                "min_per_fill": round(P.MODEL_MASS["fill_kg"] / flow / 60.0, 1)}
    _, w = width()
    out["max_dose_at_speed_kg_ha"] = round(P.meter_rpm_max / 60.0 * P.roller_ml_per_rev() / 1000.0 * P.fill_density
                                           / (w * P.speed) * 10000.0)
    return out


def spinner_power(kg_ha=300.0, rpm=P.disc_rpm):
    """Mechanical power (W): kinetic energy given to the granules (x2 for slip on the vanes) + air drag of the vanes."""
    flow, _ = dose_rate(kg_ha, rpm)
    _, v0, _ = throw(rpm)
    granules = 2.0 * 0.5 * flow * v0 ** 2
    w = rpm * 2 * math.pi / 60.0
    # vanes as flat plates: drag torque = sum(0.5 rho Cd h (w r)^2 r dr), Cd 1.2
    r0, r1 = P.vane_r[0] / 1000.0, P.vane_r[1] / 1000.0
    air = P.n_vanes * 0.5 * P.air_rho * 1.2 * (P.vane_h / 1000.0) * w ** 3 * (r1 ** 4 - r0 ** 4) / 4.0
    return round(granules + air, 1)


def axle_loads(full=True, ballast=False):
    """Load (kg) on the front and rear axle with the spreader (full or empty hopper, with or without the front
    counterweight), and the side slope (degrees) at which the robot would tip over sideways (static)."""
    m = P.MODEL_MASS
    key = "full" if full else "empty"
    items = [(P.robot_mass, P.robot_cg_y, P.robot_cg_z), (m[key + "_kg"], m[key + "_cg_y"], m[key + "_cg_z"])]
    if ballast:
        items.append((m["ballast_kg"], m["ballast_cg_y"], m["ballast_cg_z"]))
    total = sum(k for k, _, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y, _ in items) / (2 * P.robot_axle_y)
    zc = sum(k * z for k, _, z in items) / total
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3),
            "cg_z": round(zc), "tip_slope_deg": round(math.degrees(math.atan2(P.robot_track / 2.0, zc)), 1)}


def report():
    w_throw, w_drive = width()
    d, v0, t = throw()
    out = {"hopper_l": round(P.hopper_volume(), 1), "funnel_deg": {k: round(v, 1) for k, v in P.funnel_angles().items()},
           "roller_ml_rev": round(P.roller_ml_per_rev(), 1), "exit_speed_m_s": round(v0, 1),
           "throw_width_m": round(w_throw, 2), "driving_width_m": round(w_drive, 2),
           "width_by_rpm": {rpm: round(width(rpm)[1], 2) for rpm in (500, 700, 900)},
           "doses": doses(), "spinner_W_300kg": spinner_power(), "spinner_W_900rpm": spinner_power(300.0, 900.0),
           "ha_per_hour": round(w_drive * P.speed * 3600 / 10000.0 * 0.8, 2),
           "axle_full": axle_loads(True), "axle_full_ballast": axle_loads(True, True),
           "axle_empty": axle_loads(False)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
