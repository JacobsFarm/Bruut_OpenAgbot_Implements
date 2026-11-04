"""Calculations for the chicken house robot, in pure Python (same parameters as the model).

    import chk_calc
    chk_calc.report()          # prints and returns all key figures
"""
import math

import chk_params as P


def rotor():
    """Tip speed, tine passes per metre of travel, and the power to drag the tines through caked litter."""
    omega = P.rotor_rpm * 2.0 * math.pi / 60.0
    tip = omega * P.tip_r / 1000.0
    passes_m = P.rotor_rpm / 60.0 * P.tine_rows / P.speed           # rows passing a point per metre of travel
    width = P.tines_per_row * P.tine_step / 1000.0
    area = width * P.tine_engaged                                    # face of litter cut per rotor turn row
    force = P.k_litter * area
    power = force * tip / P.eta_drive_tool
    return {"tip_m_s": round(tip, 2), "passes_per_m": round(passes_m), "tine_spacing_mm": round(P.tine_step / 2.0),
            "force_N": round(force), "electric_W": round(power), "broom_motor_load": round(power / P.S.motor_w, 2)}


def house_time():
    width = (P.tines_per_row * P.tine_step - P.overlap) / 1000.0
    area = P.house[0] * P.house[1]
    m2_h = width * P.speed * 3600.0
    hours = area / m2_h
    drag = P.crr * (P.robot_mass + 124.0) * P.g
    w = drag * P.speed / P.eta_drive + rotor()["electric_W"] + P.p_sensors
    return {"house_m2": area, "m2_h": round(m2_h), "hours_per_house": round(hours, 1), "power_W": round(w),
            "battery_h": round(P.battery_wh / w, 1), "houses_per_charge": round(P.battery_wh / w / hours, 2)}


def birds():
    """Birds met per minute in front of the 1.1 m wide head and whether they can walk away in time."""
    per_min = P.birds_m2 * 1.1 * P.speed * 60.0
    return {"birds_met_per_min": round(per_min), "escape_faster_than_robot": P.bird_escape > P.speed,
            "margin_s_per_0.5m": round(0.5 / P.speed - 0.5 / P.bird_escape, 1)}


def report():
    out = {"rotor": rotor(), "house": house_time(), "birds": birds()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
