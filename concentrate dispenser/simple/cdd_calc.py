"""Calculations of the concentrate dispenser (pure Python, no FreeCAD).

    import cdd_calc; cdd_calc.report()

Hopper capacity, auger output per turn, auger speed for a dose per feeding place at the pushing speed, the drive torque,
dose accuracy by loss-in-weight, rounds per fill and the effect on the axle loads.
"""
import math

import cdd_params as P


def capacity(density=None):
    density = P.pellet_density if density is None else density
    v = P.hopper_volume_l()
    return {"litres": v, "kg": v * density}


def g_per_rev(density=None, fill=None):
    density = P.pellet_density if density is None else density
    fill = P.fill if fill is None else fill
    area = math.pi / 4.0 * (P.flight_d ** 2 - P.core_d ** 2)          # mm2
    vol = area * P.flight_pitch * fill / 1e6                          # l per turn
    return vol * density * 1000.0


def dose(dose_g=None, speed=None, density=None):
    """Auger speed (rpm) and motor speed for dose_g per feeding place at the pushing speed."""
    dose_g = P.dose_place_g if dose_g is None else dose_g
    speed = P.push_speed if speed is None else speed
    g_m = dose_g / P.place_m
    g_s = g_m * speed
    rpm = g_s / g_per_rev(density) * 60.0
    return {"g_per_m": g_m, "g_per_s": g_s, "auger_rpm": rpm, "motor_rpm": rpm * P.gear_ratio}


def dose_range(rpm_max=150.0, rpm_min=5.0):
    """Doses per place (g) that the auger can give at the pushing speed between rpm_min and rpm_max."""
    g_s = lambda rpm: rpm / 60.0 * g_per_rev()
    t_place = P.place_m / P.push_speed
    return g_s(rpm_min) * t_place, g_s(rpm_max) * t_place


def torque(rpm=None):
    """Running power from the auger formula P = m_dot g L lambda, plus a starting torque under a full hopper."""
    d = dose()
    rpm = d["auger_rpm"] if rpm is None else rpm
    L = (P.tube_x[1] - (-P.hopper_x)) / 1000.0
    m_dot = d["g_per_s"] / 1000.0
    p_run = m_dot * P.g * L * P.lambda_auger
    t_run = p_run / (2 * math.pi * rpm / 60.0)
    # start: pellets press on the trough length under the hopper; friction on the flight edge (estimated)
    head = (P.hopper_top - P.auger_z) / 1000.0
    p_bulk = P.pellet_density * 1000.0 * P.g * head * 0.4            # Pa, Janssen-reduced (0.4, estimated)
    area = 2 * P.hopper_x / 1000.0 * P.flight_d / 1000.0             # m2 projected under the hopper
    mu = 0.45
    t_start = p_bulk * area * mu * (P.flight_d / 2000.0)
    t_avail = P.nema_torque_run * P.gear_ratio * P.gear_eff
    return {"run_W": p_run, "run_Nm": t_run, "start_Nm": t_start, "avail_Nm": t_avail,
            "reserve": t_avail / max(t_start, t_run)}


def loss_in_weight(window_s=10.0):
    """Dose error of a weighed window: 4 cells of cell_res_g each (rss) on the window's mass flow."""
    d = dose()
    m = d["g_per_s"] * window_s
    noise = 2.0 * math.sqrt(4) * P.cell_res_g                       # start and end weighing
    vib = 0.01 * m                                                  # residual vibration while driving (estimated)
    err = math.sqrt(noise ** 2 + vib ** 2)
    return {"window_g": m, "err_g": err, "err_pct": 100.0 * err / m}


def round_figures():
    fence_m = P.cows * P.place_m
    per_round = P.cows * P.dose_place_g / 1000.0
    cap = capacity()["kg"]
    t = fence_m / P.push_speed
    return {"fence_m": fence_m, "kg_per_round": per_round, "rounds_per_fill": cap / per_round,
            "fills_per_day": P.rounds_per_day * per_round / cap, "dose_time_s": t}


def axle_loads():
    m_imp = P.MODEL_MASS["total_kg"]
    full = capacity()["kg"]
    y = P.MODEL_MASS["cg"][1]
    m = m_imp + full
    front = m * (y + P.robot_axle_y) / (2 * P.robot_axle_y)
    return {"added_kg": m, "front_kg": front, "rear_kg": m - front}


def report():
    cap = capacity()
    capm = capacity(P.mineral_density)
    d = dose()
    lo, hi = dose_range()
    tq = torque()
    lw = loss_in_weight()
    rf = round_figures()
    ax = axle_loads()
    lines = [
        "Concentrate dispenser (simple)",
        "  hopper %.0f l: %.0f kg pellets (%.2f kg/l) or %.0f kg minerals" % (cap["litres"], cap["kg"],
                                                                             P.pellet_density, capm["kg"]),
        "  auger O%d pitch %d, fill %.0f %%: %.1f g pellets per turn" % (P.flight_d, P.flight_pitch, 100 * P.fill,
                                                                      g_per_rev()),
        "  %d g per place (%.2f m) at %.2f m/s: %.0f g/m, %.1f g/s -> auger %.0f rpm, motor %.0f rpm"
        % (P.dose_place_g, P.place_m, P.push_speed, d["g_per_m"], d["g_per_s"], d["auger_rpm"], d["motor_rpm"]),
        "  dose range at this speed (5 .. 150 rpm): %.0f .. %.0f g per place" % (lo, hi),
        "  drive: run %.1f W / %.2f Nm, start %.1f Nm under a full hopper, %.1f Nm available (%.1fx)"
        % (tq["run_W"], tq["run_Nm"], tq["start_Nm"], tq["avail_Nm"], tq["reserve"]),
        "  loss-in-weight over 10 s: %.0f g +- %.1f g (%.1f %%)" % (lw["window_g"], lw["err_g"], lw["err_pct"]),
        "  %d cows: fence %.0f m, %.1f kg per round, %.1f rounds per fill, %.1f fills per day (%d rounds), %.0f s dosing"
        % (P.cows, rf["fence_m"], rf["kg_per_round"], rf["rounds_per_fill"], rf["fills_per_day"], P.rounds_per_day,
           rf["dose_time_s"]),
        "  on the robot, full: +%.0f kg (front %.0f / rear %.0f kg): the feed pusher's balance stays as it is"
        % (ax["added_kg"], ax["front_kg"], ax["rear_kg"]),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
