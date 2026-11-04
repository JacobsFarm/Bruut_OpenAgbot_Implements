"""Calculations for the security patrol, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B scp_calc.py      (or in FreeCAD: import scp_calc; scp_calc.report())

Detection ranges (Johnson criteria for the thermal camera, EN 62676-4 pixel densities for the day/night and fixed
cameras), time of a 360 degree thermal sweep, patrol energy (rounds per charge and per night), wind on the mast
(bending stress at the foot and tipping), axle loads.
"""
import math

import scp_params as P


def thermal_ranges():
    """Range (m) per target and Johnson level: target size over 2 px per cycle times the pixel angle (IFOV)."""
    ifov = P.ir_pitch_um / 1000.0 / P.ir_f_mm               # rad per pixel
    hfov = math.degrees(2 * math.atan(P.ir_px[0] * P.ir_pitch_um / 1000.0 / 2.0 / P.ir_f_mm))
    out = {"ifov_mrad": round(ifov * 1000, 2), "hfov_deg": round(hfov, 1)}
    for t, dim in P.TARGETS.items():
        out[t] = {k: round(dim / (2 * c * ifov)) for k, c in P.JOHNSON.items()}
    return out


def _range_for(px, hfov_deg, px_per_m):
    width_m = px / px_per_m
    return width_m / (2 * math.tan(math.radians(hfov_deg) / 2))


def visible_ranges():
    """Day/night camera at wide and tele, fixed cameras: range (m) for each DORI pixel density."""
    out = {}
    for name, f in (("wide", P.vis_f_mm[0]), ("tele", P.vis_f_mm[1])):
        hfov = math.degrees(2 * math.atan(P.vis_sensor_mm / 2 / f))
        out[name] = {"hfov_deg": round(hfov, 1)}
        out[name].update({k: round(_range_for(P.vis_px, hfov, v)) for k, v in P.DORI_PX_M.items()})
    out["fixed"] = {k: round(_range_for(P.fix_px, P.fix_hfov, v), 1) for k, v in P.DORI_PX_M.items()}
    out["fixed"]["all_round_overlap_deg"] = round(4 * P.fix_hfov - 360.0)
    out["ir_night_m"] = P.ir_range_m
    return out


def sweep():
    hfov = thermal_ranges()["hfov_deg"]
    n = math.ceil(360.0 / (hfov * (1 - P.sweep_overlap)))
    return {"frames": n, "seconds": round(n * P.settle_s, 1)}


def _total_kg():
    return P.robot_mass + P.MODEL_MASS["kg"]


def patrol():
    """Average power and rounds of the route per charge and per night."""
    m = _total_kg()
    p_drive = m * P.g * P.crr * P.speed / P.eta_drive
    p_sens = sum(P.p_sensors.values())
    t_drive = P.route_m / P.speed
    stops = math.ceil(P.route_m / P.stop_every_m)
    t_stop = stops * sweep()["seconds"]
    t_round = t_drive + t_stop
    wh_round = (p_drive * t_drive + p_sens * t_round) / 3600.0
    rounds_night = P.night_h * 3600.0 / t_round
    wh_night = wh_round * rounds_night
    return {"drive_W": round(p_drive), "sensors_W": round(p_sens), "round_min": round(t_round / 60.0, 1),
            "stops_per_round": stops, "Wh_per_round": round(wh_round), "rounds_per_charge": round(P.battery_wh / wh_round, 1),
            "Wh_per_night_nonstop": round(wh_night), "hours_per_charge": round(P.battery_wh / wh_round * t_round / 3600.0, 1),
            "parked_watch_h": round(P.battery_wh / p_sens, 1)}


def wind():
    """Wind from the side: drag of the head, horns, box and mast; bending at the mast foot; tipping about the wheels."""
    q = 0.5 * P.rho_air * P.wind_ms ** 2                     # N/m2
    items = [  # (area m2, height of the centre mm)
        (0.25 * 0.32, P.tilt_z),                             # pan/tilt head with cameras
        (0.14 * 0.07, P.mast_top + 40.0),                    # pan base
        (0.20 * 0.14 * 2, P.horn_z),                         # horns side view
        (0.15 * 0.26, P.box_z + 130.0),                      # electronics box side
        (P.mast_w / 1000.0 * (P.mast_top - 709.0) / 1000.0, (P.mast_top + 709.0) / 2),
        (0.11 * 0.13, P.beacon_z + 65.0),
    ]
    f = sum(a * q * P.cd for a, _ in items)
    m_foot = sum(a * q * P.cd * (z - 709.0) / 1000.0 for a, z in items)          # Nm at the mast foot
    w = P.mast_w
    wi = w - 2 * P.mast_wall
    W = (w ** 4 - wi ** 4) / (6 * w)                                              # mm3 section modulus
    sigma = m_foot * 1000.0 / W
    m_tip = sum(a * q * P.cd * z / 1000.0 for a, z in items)                     # Nm about the tyre contact line
    m_hold = _total_kg() * P.g * P.robot_wheel_x / 1000.0
    v_tip = P.wind_ms * math.sqrt(m_hold / m_tip)
    return {"force_N": round(f), "foot_Nm": round(m_foot), "stress_N_mm2": round(sigma, 1),
            "safety_yield": round(P.mast_yield / sigma, 1), "tip_safety": round(m_hold / m_tip, 1),
            "tipping_wind_m_s": round(v_tip)}


def axle_loads():
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg[1]), (m["kg"], m["cg"][1])]
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2.0 * P.robot_axle_y)
    cg_z = (P.robot_mass * P.robot_cg[2] + m["kg"] * m["cg"][2]) / total
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "cg_z_mm": round(cg_z), "side_tilt_limit_deg": round(math.degrees(math.atan(P.robot_wheel_x / cg_z)))}


def report():
    out = {"thermal_m": thermal_ranges(), "visible_m": visible_ranges(), "sweep": sweep(), "patrol": patrol(),
           "wind": wind(), "axle": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
