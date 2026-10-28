"""Calculations for the grassland aerator, in pure Python (same parameters as the model).

    import gae_calc
    gae_calc.report()          # prints and returns all key figures

Masses come from build_gae.mass_properties() (copied into gae_params.MODEL_MASS after a rebuild).
"""
import math

import gae_params as P


def pattern():
    """Slit pattern and capacity."""
    along = 2 * math.pi * P.knife_r[1] / P.knife_n
    width = P.disc_n * P.disc_pitch / 1000.0
    return {"width_m": width, "slit_spacing_across_mm": P.disc_pitch, "slit_spacing_along_mm": round(along),
            "slits_per_m2": round(1e6 / (P.disc_pitch * along), 1),
            "ha_per_hour": round(width * P.speed * 3600 / 10000.0 * 0.8, 2)}


def total_weight_N():
    m = P.MODEL_MASS
    return (P.robot_mass + m["mount_kg"] + m["lift_kg"]) * P.g


def static_roller_N():
    """Part of the lift group (with ballast) that rests on the roller when the actuator is free (moment about the
    pivot; the roller axle is the only support behind it)."""
    m = P.MODEL_MASS
    arm = P.pivot[0] - P.axle[0]
    return m["lift_kg"] * P.g * (P.pivot[0] - m["lift_cg_y"]) / arm


def needed_N():
    """Down force to push the knives in: knives below ground per disc x discs x force per knife."""
    return P.disc_n * P.knives_in_ground() * P.knife_force


def max_down_N():
    """Largest roller load at which the wheels still pull the roller with grip_margin_min:
    mu (W - N) >= m (c_roll N + crr (W - N))."""
    W = total_weight_N()
    mm = P.grip_margin_min
    k = P.mu_tyre_grass - mm * P.crr_grass
    return W * k / (k + mm * P.c_roll)


def act_lever(lift_deg):
    """Lever (mm) of the actuator line about the pivot."""
    r = P.rotate_yz(P.rod_pin, lift_deg)
    uy, uz = r[0] - P.act_base[0], r[1] - P.act_base[1]
    L = math.hypot(uy, uz)
    return abs((r[0] - P.pivot[0]) * uz / L - (r[1] - P.pivot[1]) * uy / L)


def down_force():
    """Roller load: static share of the frame and ballast, what the knives need, and the actuator push to make up
    the difference (limited by the grip of the wheels)."""
    stat = static_roller_N()
    need = needed_N()
    limit = max_down_N()
    arm = P.pivot[0] - P.axle[0]
    extra = max(0.0, min(need, limit) - stat)
    f_act = extra * arm / act_lever(P.lift_work)
    return {"knives_in_ground_per_disc": round(P.knives_in_ground(), 2), "needed_N": round(need),
            "static_N": round(stat), "grip_limit_N": round(limit), "actuator_push_N": round(f_act),
            "actuator_ok": f_act <= P.act_force, "reached_N": round(stat + extra),
            "depth_ok": stat + extra >= need}


def pull():
    """Pull force (N) and power at the reached roller load."""
    d = down_force()
    N = d["reached_N"]
    W = total_weight_N()
    wheels = W - N
    roller = P.c_roll * N
    roll = P.crr_grass * wheels
    grip = P.mu_tyre_grass * wheels
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    total = roller + roll
    return {"roller_N": round(roller), "rolling_N": round(roll), "total_N": round(total),
            "on_wheels_kg": round(wheels / P.g, 1), "grip_N": round(grip), "motor_cont_N": round(motors),
            "margin": round(min(grip, motors) / total, 2), "power_W": round(total * P.speed / P.eta_drive)}


def actuator():
    """Force to lift the lift group (with ballast) in work and transport, lengths against the stroke."""
    m = P.MODEL_MASS
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        cg = P.rotate_yz((m["lift_cg_y"], m["lift_cg_z"]), lift)
        moment = m["lift_kg"] * P.g * abs(P.pivot[0] - cg[0]) / 1000.0
        lev = act_lever(lift)
        out["lift_%g" % lift] = {"length": round(P.act_length(lift), 1), "lever_mm": round(lev, 1),
                                 "moment_Nm": round(moment), "force_N": round(moment / lev * 1000.0)}
    lens = [P.act_length(x) for x in P.LIFT_POSES]
    out["length_range"] = (round(min(lens), 1), round(max(lens), 1))
    out["fits_stroke"] = P.act_retracted <= min(lens) and max(lens) <= P.act_retracted + P.act_stroke
    out["lift_time_s"] = round((max(lens) - min(lens)) / P.act_speed, 1)
    tip = P.rotate_yz(P.axle, P.lift_transport)[1] - P.knife_r[1]
    out["knife_tips_transport_mm"] = round(tip)
    return out


def axle_loads():
    """Load (kg) on the front and rear axle, roller lifted (transport): the aerator sits between the axles."""
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["lift_kg"], m["lift_cg_y"])]
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3)}


def report():
    out = {"pattern": pattern(), "down_force": down_force(), "pull": pull(), "actuator": actuator(),
           "axle_transport": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
