"""Calculations of the riding arena leveller (pure Python, no FreeCAD).

    import arl_calc; arl_calc.report()

Draft force of tines, board and roller in loose sand, the robot's traction and hub torque against it, the load on the
roller (which carries the frame), front ballast needed to lift the tool, time and energy per arena.
"""
import math

import arl_params as P


def draft(depth=None):
    depth = P.tine_depth if depth is None else depth
    m_lev = P.MODEL_MASS["lift_kg"]
    w = m_lev * P.g
    f_tines = P.tine_n * P.k_tine * P.tine_bar[0] * depth
    f_board = P.mu_board * P.board_load_frac * w
    f_roll = P.crr_roller * (1.0 - P.board_load_frac) * w
    return {"tines": f_tines, "board": f_board, "roller": f_roll, "total": f_tines + f_board + f_roll}


def traction():
    """Robot weight on the wheels in work (the tool rests on its roller, its mount on the robot)."""
    m = P.robot_mass + P.MODEL_MASS["mount_kg"] + P.MODEL_MASS["post_kg"] + P.ballast_kg
    f_grip = P.mu_tyre_sand * m * P.g
    f_roll = P.crr_tyre_sand * m * P.g
    f_hub = P.n_driven * P.hub_torque_nom / P.r_load
    return {"mass_kg": m, "grip": f_grip, "rolling": f_roll, "hub": f_hub,
            "available": min(f_grip, f_hub) - f_roll}


def depth_limit():
    """Largest tine depth (mm) the robot can pull at its grip limit."""
    t = traction()["available"]
    d0 = draft(0.0)
    rest = d0["board"] + d0["roller"]
    return (t - rest) / (P.tine_n * P.k_tine * P.tine_bar[0])


def lifted_balance():
    """Tool lifted: moments about the rear axle (y -500). Front ballast (kg at y +575) for 25 % on the front axle."""
    m_r, y_r = P.robot_mass, P.robot_cg_y
    m_t = P.MODEL_MASS["lift_kg"] + P.MODEL_MASS["mount_kg"] + P.MODEL_MASS["post_kg"]
    y_t = P.MODEL_MASS["lift_cg_y"]
    ya = -P.robot_axle_y
    L = 2 * P.robot_axle_y
    front = (m_r * (y_r - ya) + m_t * (y_t - ya) + P.ballast_kg * (P.ballast_y - ya)) / L
    total = m_r + m_t + P.ballast_kg
    need = 0.25 * total - front
    y_b = 575.0
    ballast = P.ballast_kg + max(0.0, need / ((y_b - ya) / L - 0.25))
    return {"front_kg": front, "total_kg": total, "front_share": front / total, "ballast_kg": ballast}


def arena_time(size=None):
    size = P.arena if size is None else size
    w, l = size
    eff_w = (2 * P.frame_x - P.overlap) / 1000.0
    passes = math.ceil(w / eff_w)
    t = passes * l / P.speed + passes * P.turn_s
    area_h = w * l / (t / 3600.0)
    return {"passes": passes, "min": t / 60.0, "m2_h": area_h}


def energy(size=None):
    d = draft()["total"]
    tr = traction()
    f = d + tr["rolling"]
    w = f * P.speed / P.eta_drive + P.computer_w
    at = arena_time(size)
    wh = w * at["min"] / 60.0
    return {"W": w, "Wh": wh, "arenas_per_charge": P.battery_wh / wh}


def report():
    d = draft()
    tr = traction()
    lb = lifted_balance()
    a = arena_time()
    ab = arena_time(P.arena_big)
    e = energy()
    lines = [
        "Riding arena leveller (simple)",
        "  draft at %d mm: tines %.0f N + board %.0f N + roller %.0f N = %.0f N"
        % (P.tine_depth, d["tines"], d["board"], d["roller"], d["total"]),
        "  traction (with %.0f kg front ballast): %.0f kg on the wheels, grip %.0f N (mu %.2f), hubs %.0f N, rolling %.0f N -> %.0f N for the tool"
        % (P.ballast_kg, tr["mass_kg"], tr["grip"], P.mu_tyre_sand, tr["hub"], tr["rolling"], tr["available"]),
        "  deepest tine depth at the grip limit: %.0f mm" % depth_limit(),
        "  tool lifted (with %.0f kg ballast): front axle %.0f of %.0f kg (%.0f %%): %.0f kg front ballast for 25 %%"
        % (P.ballast_kg, lb["front_kg"], lb["total_kg"], 100 * lb["front_share"], lb["ballast_kg"]),
        "  arena 20 x 40: %d passes, %.0f min (%.0f m2/h); 20 x 60: %.0f min" % (a["passes"], a["min"], a["m2_h"], ab["min"]),
        "  energy %.0f W: %.0f Wh per 20 x 40 arena, %.1f arenas per charge" % (e["W"], e["Wh"], e["arenas_per_charge"]),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
