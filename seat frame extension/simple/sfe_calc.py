"""Calculations for the seat, canopy and frame extension, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B sfe_calc.py      (or in FreeCAD: import sfe_calc; sfe_calc.report())

Axle and wheel loads with the operator, centre of gravity height, static tip angles, lateral acceleration in a turn at
the riding speed, the slope rule, and the moment of implements on the side extensions.
"""
import math

import sfe_params as P


def masses(operator=True):
    m = P.MODEL_MASS
    out = [(P.robot_kg, P.robot_cg), (m["total_kg"], m["cg"])]
    if operator:
        out.append((P.operator_kg, P.operator_cg))
    return out


def combined(operator=True):
    ms = masses(operator)
    tot = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / tot for i in range(3))
    return tot, cg


def axle_loads(operator=True):
    tot, cg = combined(operator)
    front = tot * (cg[1] + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    return {"total_kg": round(tot, 1), "front_kg": round(front, 1), "rear_kg": round(tot - front, 1),
            "rear_share": round((tot - front) / tot, 3), "wheel_max_kg": round(max(front, tot - front) / 2.0, 1)}


def stability(operator=True):
    """Static tip angles (deg) sideways and fore-aft; lateral acceleration in the tightest turn at riding speed and the
    acceleration that tips (track / 2 / cg height x g); allowed sideways slope with a factor of 2."""
    tot, cg = combined(operator)
    h = cg[2]
    side = math.degrees(math.atan(P.robot_wheel_x / h))
    fore = math.degrees(math.atan(min(P.robot_axle_y + cg[1], P.robot_axle_y - cg[1]) / h))
    a_turn = P.ride_speed_max ** 2 / P.turn_r_min
    a_tip = P.robot_wheel_x / h * P.g
    slope_2 = math.degrees(math.atan(0.5 * P.robot_wheel_x / h))
    return {"cg_z": round(h), "tip_side_deg": round(side, 1), "tip_fore_aft_deg": round(fore, 1),
            "a_turn_m_s2": round(a_turn, 2), "a_tip_m_s2": round(a_tip, 2), "turn_factor": round(a_tip / a_turn, 1),
            "slope_factor2_deg": round(slope_2, 1), "slope_rule_ok": P.slope_max_deg <= slope_2}


def extension():
    """Bending in the extension tube at the last upper beam (x 425) with an implement at implement_ext_x."""
    f = P.implement_ext_kg * P.g * 2.5                     # dynamic factor 2.5 for bumps
    arm = P.implement_ext_x - 425.0
    mom = f * arm                                          # Nmm
    t, w = P.tube, P.tube_wall
    wz = (t ** 4 - (t - 2 * w) ** 4) / (6.0 * t)
    return {"moment_Nm": round(mom / 1000.0, 1), "stress_MPa": round(mom / wz), "ok": mom / wz < 235.0 / 1.5}


def report():
    out = {"axle_with_operator": axle_loads(True), "axle_without": axle_loads(False),
           "stability_with_operator": stability(True), "stability_without": stability(False), "extension": extension()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
