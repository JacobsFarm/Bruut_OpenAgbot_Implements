"""Calculations for the rotary tiller, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B pwh_calc.py      (or in FreeCAD: import pwh_calc; pwh_calc.report())

Blade tip speed and bite length, tilling power from a specific energy, rotor and motor torque, forward thrust of the
down-cut rotor against the robot's grip, worked area and battery time, and the front-axle share with the tiller
lifted (ballast).
"""
import math

import pwh_params as P


def rotor():
    tip = math.pi * P.rotor_d / 1000.0 * P.rotor_rpm / 60.0
    out = {"tip_speed_m_s": round(tip, 2)}
    for v in P.speed:
        bite = v * 1000.0 * 60.0 / (P.rotor_rpm * P.blades_per_flange)       # mm per blade on one flange
        out["bite_mm_at_%.2f" % v] = round(bite, 1)
    return out


def power(v=None, e=None):
    """Tilling power = soil volume rate x specific energy; rotor and motor torque."""
    v = P.speed[0] if v is None else v
    e = P.specific_energy[1] if e is None else e
    vol = P.work_w / 1000.0 * P.depth / 1000.0 * v                           # m3/s
    p_rotor = vol * e * 1000.0                                               # W
    p_motor = p_rotor / (P.chain_eff * P.gear_eff)
    t_rotor = p_rotor / (P.rotor_rpm * 2 * math.pi / 60.0)
    return {"speed_m_s": v, "kJ_m3": e, "rotor_W": round(p_rotor), "motor_W": round(p_motor),
            "motor_load": round(p_motor / P.motor_w, 2), "rotor_Nm": round(t_rotor), "motor_Nm": round(t_rotor / P.gear_ratio / P.gear_eff, 1)}


def thrust(v=None):
    """Down-cut rotor: the blades push the soil back and the robot forward. Tangential force at the tip x a share."""
    pw = power(v)
    f_t = pw["rotor_Nm"] / (P.rotor_d / 2000.0)
    push = f_t * P.thrust_share
    grip = P.mu_tyre * (P.robot_mass + P.MODEL_MASS["mount_kg"]) * P.g
    return {"tangential_N": round(f_t), "push_N": round(push), "robot_grip_N": round(grip),
            "note": "the robot must hold back (brake) the push; it is %d %% of its grip" % round(100 * push / grip)}


def work():
    out = {}
    for v in P.speed:
        pw = power(v, P.specific_energy[1])
        p = pw["motor_W"] + P.drive_w + P.electronics_w
        h = P.robot_battery_kwh * 1000.0 * 0.85 / p
        ha_h = P.work_w / 1000.0 * v * 3600.0 / 1e4
        out["%.2f_m_s" % v] = {"total_W": round(p), "battery_h": round(h, 2), "m2_h": round(ha_h * 1e4),
                               "m2_per_charge": round(ha_h * 1e4 * h)}
    return out


def lifted(ballast=None):
    """Front axle share with the tiller lifted; ballast (kg) at y 575."""
    ballast = P.T.ballast_kg if ballast is None else ballast
    ya = -P.robot_axle_y
    L = 2 * P.robot_axle_y
    parts = [(P.robot_mass, 0.0), (P.MODEL_MASS["mount_kg"], P.MODEL_MASS["mount_cg_y"]),
             (P.MODEL_MASS["implement_kg"], P.MODEL_MASS["implement_cg_y"]), (ballast, P.T.ballast_cg_y)]
    m = sum(p[0] for p in parts)
    front = sum(mi * (yi - ya) for mi, yi in parts) / L
    return {"ballast": ballast, "front_kg": round(front, 1), "total_kg": round(m, 1), "share": round(front / m, 3)}


def ballast_for(share=P.T.front_share_min):
    b = 0.0
    while lifted(b)["share"] < share and b < 400.0:
        b += 1.0
    return b


def report():
    out = {"rotor": rotor(), "power_firm": power(P.speed[0], P.specific_energy[1]),
           "power_loose_fast": power(P.speed[1], P.specific_energy[0]), "thrust": thrust(), "work": work(),
           "lifted_no_ballast": lifted(0.0), "lifted_40kg": lifted(), "ballast_for_20pct": ballast_for()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
