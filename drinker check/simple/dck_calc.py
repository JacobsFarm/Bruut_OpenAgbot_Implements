"""Calculations for the drinking trough check, in pure Python (same parameters as the model).

    import dck_calc
    dck_calc.report()          # prints and returns all key figures
"""
import math

import dck_params as P


def level():
    """Level accuracy (mm) and what it means in litres and in drinking time of the herd."""
    err = math.hypot(P.us_err, P.waves_err)
    litres = err * P.trough_area_m2
    herd_l_min = P.cow_l_day * P.cows / (24.0 * 60.0)
    return {"error_mm": round(err, 1), "error_l": round(litres, 1), "herd_l_min": round(herd_l_min, 2),
            "trend_min": round(litres / herd_l_min, 1)}


def refill():
    """Top-up of a trough that has dropped 100 mm: litres, minutes, how many such top-ups per tank."""
    litres = 100.0 * P.trough_area_m2
    return {"litres_per_100mm": round(litres), "minutes": round(litres / P.pump_l_min, 1),
            "topups_per_tank": round(P.tank_l / litres, 1), "tank_lasts_herd_min": round(P.tank_l / (P.cow_l_day * P.cows / 1440.0))}


def axle_loads(water_l=0.0):
    """Front / rear and left / right share with the tank full or empty (implement centre of gravity from the model)."""
    m = P.MODEL_MASS
    tank_cx = sum(P.tank_x) / 2.0
    mass = P.robot_mass + m["kg"] + water_l
    cx = (m["kg"] * m["cg_x"] + water_l * tank_cx) / mass
    cy = (m["kg"] * m["cg_y"]) / mass
    return {"total_kg": round(mass), "rear_share": round(0.5 - cy / (2.0 * P.robot_axle_y), 3),
            "right_share": round(0.5 + cx / (2.0 * P.robot_wheel_x), 3)}


def round_trip():
    """One round of all troughs: drive time, visits, energy, rounds per charge."""
    m = P.MODEL_MASS
    drag = P.crr * (P.robot_mass + m["kg"] + P.tank_l / 2.0) * P.g
    drive_s = P.route_m / P.speed
    drive_wh = drag * P.speed / P.eta_drive * drive_s / 3600.0
    visit_s = P.troughs * P.visit_min * 60.0
    total_h = (drive_s + visit_s) / 3600.0
    wh = drive_wh + P.p_sensors * total_h
    return {"minutes": round(total_h * 60.0), "Wh": round(wh), "rounds_per_charge": round(P.battery_wh / wh, 1)}


def report():
    out = {"level": level(), "refill": refill(), "axle_full": axle_loads(P.tank_l), "axle_empty": axle_loads(0.0),
           "round": round_trip()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
