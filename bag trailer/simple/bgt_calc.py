"""Calculations for the bag trailer, in pure Python (same parameters as the model).

    import bgt_calc
    bgt_calc.report()          # prints and returns all key figures
"""
import math

import bgt_params as P

MODEL = {"trailer_kg": 110.3, "trailer_cg_y": -2187.0, "hitch_kg": 16.6, "hitch_cg_y": -572.0}   # build_bgt


def trailer(loaded=True):
    """Trailer mass and cg y with or without the 12 bags (bags cg y from the layout)."""
    m, y = MODEL["trailer_kg"], MODEL["trailer_cg_y"]
    if loaded:
        kb = 4 * P.bag_layers * P.bag_kg
        yb = P.bag_y0 + P.bag[1] + 5.0
        y = (m * y + kb * yb) / (m + kb)
        m += kb
    return m, y


def ball_load(loaded=True):
    m, y = trailer(loaded)
    return m * P.g * (y - P.axle_y) / (P.ball[1] - P.axle_y)


def robot_axles(loaded=True):
    """Robot axle loads with the hitch and the ball load (N on the ball, at y -830)."""
    bl = ball_load(loaded) / P.g
    items = [(P.robot_mass, P.robot_cg_y), (MODEL["hitch_kg"], MODEL["hitch_cg_y"]), (bl, P.ball[1])]
    tot = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return tot, front / tot


def pull(surface, slope_deg=0.0, loaded=True):
    """Pull needed for robot + trailer uphill against what the robot gives (grip on its own weight + ball load, and the
    hub motors)."""
    m, _ = trailer(loaded)
    a = math.radians(slope_deg)
    on_robot, _ = robot_axles(loaded)
    need = (on_robot * (P.crr_robot[surface] * math.cos(a) + math.sin(a)) +
            (m - ball_load(loaded) / P.g) * (P.crr_trailer[surface] * math.cos(a) + math.sin(a))) * P.g
    grip = P.mu_tyre[surface] * on_robot * P.g * math.cos(a)
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    return {"need_N": round(need), "grip_N": round(grip), "motor_N": round(motors),
            "margin": round(min(grip, motors) / need, 2)}


def max_slope(surface, loaded=True):
    a = 0.0
    while pull(surface, a, loaded)["margin"] >= 1.0 and a < 30.0:
        a += 0.5
    return a - 0.5


def hold_downhill(surface, slope_deg, loaded=True):
    """Unbraked trailer: the robot has to hold it downhill with its own grip."""
    m, _ = trailer(loaded)
    a = math.radians(slope_deg)
    push = m * P.g * (math.sin(a) - P.crr_trailer[surface] * math.cos(a))
    on_robot, _ = robot_axles(loaded)
    grip = P.mu_tyre[surface] * on_robot * P.g * math.cos(a) - on_robot * P.g * math.sin(a)
    return {"push_N": round(push), "spare_grip_N": round(grip), "ok": grip >= push}


def report():
    out = {"trailer_loaded": tuple(round(v) for v in trailer(True)), "trailer_empty": tuple(round(v) for v in trailer(False)),
           "ball_load_N": (round(ball_load(True)), round(ball_load(False))),
           "robot_front_share_loaded": round(robot_axles(True)[1], 3)}
    for s in P.mu_tyre:
        out[s] = {"flat": pull(s), "max_slope_deg": max_slope(s), "hold_8deg_down": hold_downhill(s, 8.0)}
    e = pull("dry_grass")["need_N"] * 1000.0 / P.eta_drive / 3600.0
    out["wh_per_km_dry_grass"] = round(e, 1)
    for k, v in out.items():
        print(k, v)
    return out
