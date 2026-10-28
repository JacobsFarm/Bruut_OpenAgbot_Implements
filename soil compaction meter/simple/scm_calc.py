"""Calculations for the soil compaction meter, in pure Python (same parameters as the model).

    import scm_calc
    scm_calc.report()          # prints and returns all key figures
"""
import math

import scm_params as P


def push():
    """Push force: what the ball screw gives at the measuring feed and at the fast feed, what the robot weight allows,
    and the highest cone resistance that can be measured."""
    out = {}
    for feed, torque in P.motor_torque.items():
        out["screw_N_at_%g" % feed] = round(2 * math.pi * P.ball_eta * torque / (P.screw_lead * 1e-3))
    weight = (P.robot_mass + P.MODEL_MASS["total_kg"]) * P.g * P.weight_use
    out["weight_limit_N"] = round(weight)
    f = min(weight, out["screw_N_at_%g" % P.feed_push])
    out["limit_N"] = round(f)
    out["cone_area_cm2"] = round(P.cone_area() * 1e4, 2)
    out["max_cone_MPa"] = round(f / P.cone_area() / 1e6, 1)
    out["force_at_3MPa_N"] = round(P.q_limit * P.cone_area())
    return out


def rod():
    """Euler buckling of the free rod between the clamp (fixed) and the foot bush (pinned) at full length."""
    E = 200e3                                           # N/mm2
    I = math.pi * P.rod_d ** 4 / 64.0
    L = P.rod_len
    return {"free_mm": L, "buckling_N": round(math.pi ** 2 * E * I / (0.7 * L) ** 2)}


def resolution():
    return {"mm_per_reading": round(P.feed_push / P.read_hz, 2), "readings_per_profile": int(P.depth_max / P.feed_push * P.read_hz)}


def per_point():
    """Time for one profile: down fast to the ground, push to depth at 30 mm/s, back up fast, settle."""
    down = P.tip_park / P.feed_fast
    meas = P.depth_max / P.feed_push
    up = (P.depth_max + P.tip_park) / P.feed_fast
    t = down + meas + up + P.t_settle
    return {"profile_s": round(t, 1), "measure_s": round(meas, 1)}


def capacity():
    t_pt = per_point()["profile_s"]
    t_drive = P.drive_between / P.speed
    pts_h = 3600.0 / (t_pt + t_drive)
    tot = P.robot_mass + P.MODEL_MASS["total_kg"]
    e_drive = P.crr * tot * P.g * P.drive_between / P.eta_drive / 3600.0
    e_axis = P.p_axis * per_point()["measure_s"] / 3600.0
    e = e_drive + e_axis
    return {"points_per_hour": round(pts_h), "ha_per_hour": round(pts_h / P.points_per_ha, 1),
            "wh_per_point": round(e, 2), "points_per_battery": int(P.battery_wh / e)}


def report():
    out = {"push": push(), "rod": rod(), "resolution": resolution(), "per_point": per_point(), "capacity": capacity(),
           "mass_kg": P.MODEL_MASS["total_kg"]}
    for k, v in out.items():
        print(k, v)
    return out
