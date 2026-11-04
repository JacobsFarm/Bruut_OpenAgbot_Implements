"""Calculations of the calf milk taxi (pure Python, no FreeCAD).

    import cmt_calc; cmt_calc.report()

Tank volume, heat loss and how long the milk stays warm, heater power to hold it, dose time and accuracy of the
peristaltic pump, time per round, energy and the load on the axles.
"""
import math

import cmt_params as P


def tank():
    v = P.tank_litres()
    return {"litres": v, "calves_per_fill": v / P.dose_l, "milk_kg": v * P.rho_milk}


def heat_loss():
    """W lost through the PU insulation (jacket area, lid, bottom) at the start temperature."""
    r = (P.tank_d / 2.0 + P.tank_t + P.insul / 2.0) / 1000.0
    h = (P.tank_h + P.cone_h) / 1000.0
    area = 2 * math.pi * r * h + 2 * math.pi * r * r
    u = P.lambda_pu / (P.insul / 1000.0)
    dT = P.milk_temp - P.air_temp
    w = u * area * dT * 1.3                                     # +30 % for the outlet, feet, lid rim (estimated)
    return {"area_m2": area, "U": u, "W": w}


def cooling(litres=None):
    """Hours until the milk drops from milk_temp to min_temp without the heater."""
    litres = tank()["litres"] if litres is None else litres
    m = litres * P.rho_milk
    w = heat_loss()["W"]
    k = w / (P.milk_temp - P.air_temp)                          # W/K
    tau = m * P.cp_milk * 1000.0 / k / 3600.0                   # h
    t = tau * math.log((P.milk_temp - P.air_temp) / (P.min_temp - P.air_temp))
    return {"tau_h": tau, "hours_to_min": t, "K_per_h": w / (m * P.cp_milk * 1000.0) * 3600.0}


def dose():
    q = P.pump_rev_ml * P.pump_rpm / 1000.0                     # l/min
    t = P.dose_l / q * 60.0
    revs = P.dose_l * 1000.0 / P.pump_rev_ml
    err = 100.0 * 1.0 / revs + 1.5                              # 1 rev resolution (ends) + tube wear/pressure (est.)
    return {"l_min": q, "s_per_calf": t, "revs": revs, "err_pct": err}


def round_time():
    d = dose()
    drive = P.hutch_pitch / P.speed
    per_calf = drive + P.stop_s + d["s_per_calf"]
    n = min(P.calves, int(tank()["calves_per_fill"]))
    return {"s_per_calf": per_calf, "calves": n, "min": n * per_calf / 60.0}


def energy():
    r = round_time()
    h = r["min"] / 60.0
    w_avg = P.drive_w * (P.hutch_pitch / P.speed) / r["s_per_calf"] + P.pump_w * dose()["s_per_calf"] / r["s_per_calf"] \
        + P.stir_w + P.computer_w
    wh = w_avg * h
    return {"W_avg": w_avg, "Wh_round": wh, "rounds_per_charge": P.battery_wh / (wh + 0.0)}


def axle_loads():
    m_imp = P.MODEL_MASS["total_kg"]
    milk = tank()["milk_kg"]
    y = P.MODEL_MASS["cg"][1]
    m = m_imp + milk
    yc = (m_imp * y + milk * P.tank_xy[1]) / m
    front = m * (yc + P.robot_axle_y) / (2 * P.robot_axle_y)
    return {"added_kg": m, "front_kg": front, "rear_kg": m - front, "cg_z": P.MODEL_MASS["cg"][2]}


def report():
    t = tank()
    hl = heat_loss()
    c = cooling()
    d = dose()
    r = round_time()
    e = energy()
    a = axle_loads()
    lines = [
        "Calf milk taxi (simple)",
        "  tank %.0f l (%.0f kg milk): %.0f calves at %.1f l" % (t["litres"], t["milk_kg"], t["calves_per_fill"], P.dose_l),
        "  heat loss %.0f W at %.0f/%.0f C (U %.2f W/m2K, %.2f m2): %.1f K/h, %.1f h to %.0f C without the heater"
        % (hl["W"], P.milk_temp, P.air_temp, hl["U"], hl["area_m2"], c["K_per_h"], c["hours_to_min"], P.min_temp),
        "  heater %.0f W: holds the milk and reheats ~%.1f K/h when full" % (P.heater_w, P.heater_w / (t["milk_kg"] * P.cp_milk * 1000.0) * 3600.0),
        "  peristaltic pump %.1f l/min: %.0f s per %.1f l (%.0f turns), +-%.1f %% (estimated)"
        % (d["l_min"], d["s_per_calf"], P.dose_l, d["revs"], d["err_pct"]),
        "  per calf: drive %.1f s + stop %.0f s + dose %.0f s = %.0f s; %d calves in %.0f min"
        % (P.hutch_pitch / P.speed, P.stop_s, d["s_per_calf"], r["s_per_calf"], r["calves"], r["min"]),
        "  energy %.0f W average, %.0f Wh per round (heater off): %.1f rounds per charge"
        % (e["W_avg"], e["Wh_round"], e["rounds_per_charge"]),
        "  on the robot full: +%.0f kg (front %.0f / rear %.0f kg), centre of gravity of the taxi at z %.0f"
        % (a["added_kg"], a["front_kg"], a["rear_kg"], a["cg_z"]),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
