"""Calculations for the soil sampler, in pure Python (same parameters as the model).

    import ssa_calc
    ssa_calc.report()          # prints and returns all key figures
"""
import math

import ssa_params as P


def push_force(soil, depth_mm):
    """Force (N) to push the gouge to a depth: cone resistance on the annular tip + side friction outside and
    (half) inside on the core."""
    d, dc = P.probe_d / 1000.0, P.probe_core_d / 1000.0
    h = depth_mm / 1000.0
    tip = P.q_c[soil] * math.pi / 4.0 * (d ** 2 - dc ** 2)
    side = P.f_s * math.pi * d * h + 0.5 * P.f_s * math.pi * dc * h
    return tip + side


def available_force():
    """Push force (N) that may be taken from the robot weight (the wheels stay loaded)."""
    return P.weight_use * (P.robot_mass + P.MODEL_MASS["total_kg"]) * P.g


def forces():
    out = {}
    for soil in P.q_c:
        for depth in (P.depth_grass, P.depth_max, P.depth_arable):
            out["%s_%d" % (soil, depth)] = round(push_force(soil, depth))
    return out


def screw():
    """Torque (Nm) on the ball screw at the largest force that can be used, speed and stroke times."""
    f = available_force()
    torque = f * P.screw_lead / 1000.0 / (2 * math.pi * P.ball_eta)
    v = P.screw_lead * P.motor_rpm / 60.0
    travel_grass = P.tip_park + P.depth_grass
    travel_max = P.tip_park + P.depth_max
    return {"force_N": round(f), "torque_Nm": round(torque, 2), "motor_torque_Nm": P.motor_torque,
            "speed_mm_s": round(v), "down_up_grass_s": round(2 * travel_grass / v, 1),
            "down_up_max_s": round(2 * travel_max / v, 1)}


def sample():
    """Core and sample: core volume, soil per sample, filling of a cup."""
    core_ml = math.pi / 4.0 * P.probe_core_d ** 2 * P.depth_grass / 1000.0
    ml = core_ml * P.cores_per_sample
    return {"core_ml": round(core_ml, 1), "sample_ml": round(ml), "sample_kg_dry": round(ml / 1000.0 * P.soil_rho / 1000.0
                                                                                         * 1000.0) / 1000.0,
            "cup_l": round(P.cup_l(), 2), "cup_fill": round(ml / 1000.0 / P.cup_l(), 2)}


def cycle():
    """Time per core and per composite sample (plot), and plots per trip and per hour."""
    sc = screw()
    t_core = P.t_settle + sc["down_up_grass_s"] + P.t_eject + P.drive_between / P.speed
    t_plot = P.cores_per_sample * t_core
    return {"s_per_core": round(t_core, 1), "min_per_plot": round(t_plot / 60.0, 1),
            "plots_per_hour": round(3600.0 / t_plot, 1), "plots_per_trip": P.n_cups,
            "trip_h": round(P.n_cups * t_plot / 3600.0, 1)}


def report():
    out = {"available_push_N": round(available_force()), "forces_N": forces(), "screw": screw(), "sample": sample(),
           "cycle": cycle()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
