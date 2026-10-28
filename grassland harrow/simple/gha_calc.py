"""Calculations for the grassland harrow, in pure Python (same parameters as the model).

    import gha_calc
    gha_calc.report()          # prints and returns all key figures

Masses come from build_gha.mass_properties() (copied into gha_params.MODEL_MASS after a rebuild).
"""
import math

import gha_params as P


def n_tines():
    return len(P.tine_x(0)) + len(P.tine_x(1))


def width_m():
    return 2 * P.frame_x / 1000.0


def ground_share():
    """Mass (kg) of the harrow that rests on the ground when the actuator floats (moment about the pivot); split
    over board and tines by their distance behind the pivot."""
    m = P.MODEL_MASS
    lift_kg = m["lift_kg"]
    y_board = P.board_y - P.board_leg / 2.0
    y_tines = sum(P.bar_y) / 2.0 - P.tine_tip_back
    # 2 supports (board, tines) + the pivot: the harrow weight rests on them; pivot takes the rest
    # moment about the pivot: W * (cg - pivot) = Fb * (yb - pivot) + Ft * (yt - pivot), Fb = Ft * share_b (estimated)
    share_b = 0.4
    lw = lift_kg * (m["lift_cg_y"] - P.pivot[0])
    ft = lw / (share_b * (y_board - P.pivot[0]) + (y_tines - P.pivot[0]))
    fb = share_b * ft
    return {"board_kg": round(fb, 1), "tines_kg": round(ft, 1), "per_tine_N": round(ft * P.g / n_tines(), 1),
            "pivot_kg": round(lift_kg - fb - ft, 1)}


def tine_deflection():
    """Tip deflection (mm) of a tine under its share of the weight plus its working force."""
    gs = ground_share()
    return round(gs["per_tine_N"] * math.hypot(1.0, P.c_tine) / P.spring_rate, 1)


def draft():
    """Pull force (N) of the harrow: tines (c_tine x their load) + board sliding + one molehill of soil pushed by the
    board + rolling of the robot. A floating harrow can only pull as hard as its own weight lets it dig in."""
    gs = ground_share()
    tines = P.c_tine * gs["tines_kg"] * P.g
    board = P.mu_board * P.molehill_kg * P.g
    board_friction = P.mu_board * gs["board_kg"] * P.g
    total_robot = P.robot_mass + P.MODEL_MASS["mount_kg"] + P.MODEL_MASS["lift_kg"] - gs["board_kg"] - gs["tines_kg"]
    roll = P.crr_grass * total_robot * P.g
    grip = P.mu_tyre_grass * total_robot * P.g
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    work = tines + board + board_friction
    return {"tines_N": round(tines), "board_N": round(board + board_friction), "rolling_N": round(roll),
            "total_N": round(work + roll), "grip_N": round(grip), "motor_cont_N": round(motors),
            "margin": round(min(grip, motors) / (work + roll), 2),
            "power_W": round((work + roll) * P.speed / P.eta_drive)}


def molehills():
    """Soil per hectare from molehills and the distance the board can carry one hill before it is spread."""
    soil_kg_ha = P.molehill_kg * P.molehills_per_ha
    spread_m2 = P.molehill_kg / 1400.0 / 0.010            # spread 10 mm thick
    return {"soil_kg_ha": round(soil_kg_ha), "one_hill_spread_m2": round(spread_m2, 2),
            "one_hill_spread_length_m": round(spread_m2 / width_m(), 2)}


def actuator():
    m = P.MODEL_MASS
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        r = P.rotate_yz(P.act_rod, lift)
        uy, uz = r[0] - P.act_base[0], r[1] - P.act_base[1]
        L = math.hypot(uy, uz)
        lever = abs((r[0] - P.pivot[0]) * uz / L - (r[1] - P.pivot[1]) * uy / L)
        cg = P.rotate_yz((m["lift_cg_y"], m["lift_cg_z"]), lift)
        moment = m["lift_kg"] * P.g * abs(cg[0] - P.pivot[0]) / 1000.0
        out["lift_%g" % lift] = {"length": round(L, 1), "lever_mm": round(lever, 1), "moment_Nm": round(moment),
                                 "force_N": round(moment / lever * 1000.0)}
    lens = [P.act_length(x) for x in P.LIFT_POSES]
    out["length_range"] = (round(min(lens), 1), round(max(lens), 1))
    out["fits_stroke"] = P.act_retracted <= min(lens) and max(lens) <= P.act_retracted + P.act_stroke
    out["lift_time_s"] = round((max(lens) - min(lens)) / P.act_speed, 1)
    return out


def axle_loads():
    """Load (kg) on the front and rear axle, harrow lifted (transport)."""
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["lift_kg"], m["lift_cg_y"])]
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3)}


def report():
    out = {"tines": n_tines(), "width_m": width_m(), "track_spacing_mm": P.tine_pitch / 2.0,
           "ground_share": ground_share(), "tine_deflection_mm": tine_deflection(), "draft": draft(),
           "molehills": molehills(), "actuator": actuator(), "axle_transport": axle_loads(),
           "ha_per_hour": round(width_m() * P.speed * 3600 / 10000.0 * 0.8, 2)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
