"""Calculations for the asparagus harvester, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B asp_calc.py      (or in FreeCAD: import asp_calc; asp_calc.report())

Cycle time per spear, metres of ridge per hour, hours per hectare per harvest day, battery time, spears per crate,
axle loads.
"""
import math

import asp_params as P


def cycle():
    stroke = (P.tip_top - P.tip_work) / 1000.0
    t_z = 2 * stroke / P.z_speed
    t_x = (P.x_travel / 1000.0) / P.x_speed
    t = t_z + t_x + P.grip_cut_s
    return {"stroke_m": round(stroke, 2), "z_s": round(t_z, 2), "x_s": round(t_x, 2), "cycle_s": round(t, 1)}


def cycle_short():
    """Lift only 250 mm above the ridge top between spears; go to the top to empty the bin every ~15 spears."""
    stroke = (P.ridge_h + 250.0 - P.tip_work) / 1000.0
    t = 2 * stroke / P.z_speed + (P.x_travel / 1000.0) / P.x_speed + P.grip_cut_s
    return round(t, 1)


def output():
    t_sp = cycle_short()
    s_per_m = P.spears_per_m * t_sp + P.move_s_per_m
    m_h = 3600.0 / s_per_m
    ridge_m_ha = 1e4 / P.row_spacing
    h_ha = ridge_m_ha / m_h
    batt_h = P.robot_battery_kwh * 1000.0 * 0.85 / P.power_w
    kg_h = m_h * P.spears_per_m * P.spear_g / 1000.0
    (x0, x1), (y0, y1), h = P.crate
    crate_kg = (x1 - x0) * (y1 - y0) * h / 1e9 * 0.6 * 1000.0 * 0.45      # spears lying, ~45 % packing
    return {"cycle_short_s": t_sp, "s_per_m": round(s_per_m, 1), "ridge_m_h": round(m_h), "kg_h": round(kg_h, 1),
            "h_per_ha_per_day": round(h_ha, 1), "battery_h": round(batt_h, 1), "crate_kg": round(crate_kg, 1),
            "crate_h": round(crate_kg / kg_h, 1)}


def axle_loads():
    m = P.MODEL_MASS
    ms = [(P.robot_kg, P.robot_cg), (m["total_kg"], m["cg"])]
    tot = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / tot for i in range(3))
    front = tot * (cg[1] + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    return {"total_kg": round(tot, 1), "front_share": round(front / tot, 3), "cg_z": round(cg[2])}


def report():
    out = {"cycle_full": cycle(), "output": output(), "axle": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
