"""Calculations for the flail mulcher, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B flm_calc.py      (or in FreeCAD: import flm_calc; flm_calc.report())

Tip speed, number of knives and cuts per metre, mulching power per material and speed, battery time and area per
charge, axle loads (the mulcher hangs between the axles), lift force of the actuators.
"""
import math

import flm_params as P


def rotor():
    rpm = P.motor_rpm * P.pulley[0] / P.pulley[1]
    tip = math.pi * P.rotor_d / 1000.0 * rpm / 60.0
    ln = P.rotor_len - 60.0
    sets = P.flail_rows * (int(ln // P.flail_pitch) + 1)
    work_w = P.rotor_len / 1000.0
    cuts_per_m = rpm / 60.0 * P.flail_rows / 0.5               # at 0.5 m/s: cuts per metre along a line
    return {"rotor_rpm": round(rpm), "tip_speed_m_s": round(tip, 1), "knife_sets": sets, "knives": 2 * sets,
            "work_width_m": round(work_w, 3), "cuts_per_m_at_0.5": round(cuts_per_m),
            "full_hood_needed": tip > P.throw_check_v}


def power(material="grass", v=0.5):
    w = rotor()["work_width_m"]
    p_cut = w * v * P.energy_kJ_m2[material] * 1000.0
    p_motor = (p_cut + P.idle_w) / P.belt_eff
    return {"material": material, "speed": v, "cut_W": round(p_cut), "motor_W": round(p_motor),
            "motor_load": round(p_motor / P.motor_w, 2)}


def max_speed(material):
    """Speed at which the motor reaches its rating."""
    w = rotor()["work_width_m"]
    p_avail = P.motor_w * P.belt_eff - P.idle_w
    return round(min(P.speed[1], p_avail / (w * P.energy_kJ_m2[material] * 1000.0)), 2)


def work():
    out = {}
    for mat in P.energy_kJ_m2:
        v = max_speed(mat)
        pw = power(mat, v)
        p = pw["motor_W"] + P.drive_w + P.electronics_w
        h = P.robot_battery_kwh * 1000.0 * 0.85 / p
        m2_h = rotor()["work_width_m"] * v * 3600.0
        out[mat] = {"speed_m_s": v, "total_W": round(p), "battery_h": round(h, 2), "m2_h": round(m2_h),
                    "m2_per_charge": round(m2_h * h)}
    return out


def axle_loads():
    m = P.MODEL_MASS
    ms = [(P.robot_kg, P.robot_cg), (m["total_kg"], m["cg"])]
    tot = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / tot for i in range(3))
    front = tot * (cg[1] + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    return {"total_kg": round(tot, 1), "cg": tuple(round(c) for c in cg), "front_share": round(front / tot, 3),
            "wheel_max_kg": round(max(front, tot - front) / 2.0, 1)}


def lift():
    f_need = P.MODEL_MASS.get("lift_kg", 0.0) * P.g
    return {"lift_N": round(f_need), "actuators_N": 2 * 1500, "factor": round(2 * 1500 / f_need, 1) if f_need else None}


def report():
    out = {"rotor": rotor(), "grass_0.5": power("grass", 0.5), "work": work(), "axle": axle_loads(), "lift": lift()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
