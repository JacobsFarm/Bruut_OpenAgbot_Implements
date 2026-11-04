"""Calculations for the heavy-duty motor module on the mower-deck demonstrator, in pure Python.

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B hdm_calc.py      (or in FreeCAD: import hdm_calc; hdm_calc.report())

Blade tip speed against the safety limit, mowing power against the motor, speed on the robot's 48 V bus, current,
area per robot charge and per tool battery, torque at the shaft.
"""
import math

import hdm_params as P


def blade():
    tip = P.motor_rpm * math.pi * P.blade_d / 1000.0 / 60.0
    rpm_48 = P.motor_rpm * P.bus_v / P.motor_v                  # BLDC speed scales with the voltage (no field weakening)
    tip_48 = rpm_48 * math.pi * P.blade_d / 1000.0 / 60.0
    return {"tip_m_s": round(tip, 1), "limit": P.tip_limit, "ok": tip <= P.tip_limit, "rpm_on_48V": round(rpm_48),
            "tip_on_48V_m_s": round(tip_48, 1)}


def power(v=P.speed):
    width = (P.blade_d - P.overlap) / 1000.0
    mech = P.mow_w_per_m * P.blade_d / 1000.0 * v + P.idle_w
    elec = mech / (P.motor_eff * P.controller_eff)
    torque = mech / (P.motor_rpm * 2 * math.pi / 60.0)
    return {"width_m": round(width, 2), "mech_W": round(mech), "motor_load": round(mech / (P.motor_kw * 1000.0), 2),
            "electric_W": round(elec), "current_A_at_48V": round(elec / P.bus_v, 1), "torque_Nm": round(torque, 1)}


def capacity(v=P.speed):
    p = power(v)
    m2_h = p["width_m"] * v * 3600.0 * P.field_eff
    total = p["electric_W"] + P.drive_w
    h_robot = P.battery_kwh * 1000.0 / total
    h_tool = P.tool_battery_wh / p["electric_W"]
    return {"m2_h": round(m2_h), "total_W": round(total), "robot_hours": round(h_robot, 1),
            "m2_per_robot_charge": round(m2_h * h_robot), "tool_battery_min": round(h_tool * 60.0),
            "m2_per_tool_battery": round(m2_h * h_tool)}


def report():
    out = {"blade": blade(), "power": power(), "capacity": capacity(), "module_kg": P.MODEL_MASS["module_kg"]}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
