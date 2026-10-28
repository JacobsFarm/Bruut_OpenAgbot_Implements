"""Calculations for the bedding rake, in pure Python (same parameters as the model).

    import bdr_calc
    bdr_calc.report()          # prints and returns all key figures
"""
import math

import bdr_params as P

MODEL = {"kg": 37.3, "cg": (884.0, 7.0, 521.0), "arm_kg": 24.3, "arm_cg_x": 1254.0}     # build_bdr.mass_properties() (update after a change)


def reach():
    """What the rotor covers of the bed: from the curb to the rotor tips, and the room under the divider loops."""
    x0, x1 = P.rotor_x
    hz = P.head_z + P.arm_h / 2.0
    return {"groomed_x_from_curb_mm": (round(x0 - P.curb_x), round(x1 - P.curb_x)),
            "head_top_under_loop_mm": round(P.bed_z + P.loop_bottom - hz)}


def rotor():
    tip = 2 * math.pi * P.tip_r * 1e-3 * P.rotor_rpm / 60.0
    p = P.p_rotor_per_m * P.rotor_len * 1e-3 + P.p_idle
    torque = p / (2 * math.pi * P.rotor_rpm / 60.0)
    side = torque / (P.tip_r * 1e-3)                  # along the alley (the rotor turns in the y-z plane)
    return {"tip_m_s": round(tip, 1), "power_W": round(p), "torque_Nm": round(torque, 1), "tine_force_N": round(side)}


def stability():
    """Side tip angle to the right with the arm out: robot + rake (the arm hangs out on the right)."""
    tot = P.robot_mass + MODEL["kg"]
    x = MODEL["kg"] * MODEL["cg"][0] / tot
    z = (P.robot_mass * P.robot_cg_z + MODEL["kg"] * MODEL["cg"][2]) / tot
    yaw_grip = 0.4 * tot * P.g
    return {"cg_x": round(x), "cg_z": round(z), "tip_right_deg": round(math.degrees(math.atan((P.robot_wheel_x - x) / z)), 1),
            "side_grip_N": round(yaw_grip)}


def lift():
    """Actuator force to hold the arm in work (moment of the arm about the pivot over the crank radius; the actuator
    lies almost square to the crank)."""
    m = MODEL["arm_kg"] * P.g * (MODEL["arm_cg_x"] - P.pivot[0]) * 1e-3
    return {"arm_moment_Nm": round(m), "actuator_N": round(m / (P.crank_r * 1e-3))}


def capacity():
    t_cub = P.cubicle_w * 1e-3 / P.speed
    t_row = P.row_cubicles * t_cub + P.turn_s
    per_h = P.row_cubicles * 3600.0 / t_row
    p = rotor()["power_W"] + P.crr * (P.robot_mass + MODEL["kg"]) * P.g * P.speed / P.eta_drive
    return {"s_per_cubicle": round(t_cub, 1), "cubicles_per_hour": round(per_h), "power_W": round(p),
            "cubicles_per_battery": round(P.battery_wh / p * per_h)}


def report():
    out = {"reach": reach(), "rotor": rotor(), "lift": lift(), "stability": stability(), "capacity": capacity()}
    for k, v in out.items():
        print(k, v)
    return out
