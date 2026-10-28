"""Calculations for the charging dock, in pure Python (same parameters as the model).

    import cdk_calc
    cdk_calc.report()          # prints and returns all key figures
"""
import cdk_params as P


def contacts():
    """Charge current, contact force from the springs (half compressed), loss and heat in the contacts."""
    i = P.p_charger * P.eta_charger / P.v_charge
    f = 2 * P.spring_k * P.pad_travel / 2.0
    loss = i ** 2 * 2 * P.r_contact
    area = P.pad[0] * P.pad[2] * 1e-2                  # cm2 copper on copper per pad
    return {"current_A": round(i, 1), "force_per_pad_N": round(f), "loss_W": round(loss, 1),
            "current_density_A_cm2": round(i / area, 2)}


def catch():
    """Lateral catch: the funnel mouth against the PE block, and the bar overlap of the pads after centring."""
    mouth = P.pe_block[0] / 2 + 15.0 + P.funnel_open * 0.75
    throat = P.pe_block[0] / 2 + 15.0
    free = throat - P.pe_block[0] / 2
    pad_in, pad_out = P.pad_x - P.pad[0] / 2, P.pad_x + P.pad[0] / 2
    bar_in, bar_out = P.bar_x - P.bar[0] / 2, P.bar_x + P.bar[0] / 2
    return {"mouth_catch_mm": round(mouth - P.pe_block[0] / 2), "free_play_mm": round(free),
            "pad_on_bar_ok": pad_in - free >= bar_in and pad_out + free <= bar_out, "lat_tol_mm": P.lat_tol}


def charge(pack="robot"):
    """Charge time from 20 % to 100 % with CC/CV at the charger power."""
    e = P.pack_wh[pack] * 0.8
    p = P.p_charger * P.eta_charger
    t_cc = e * (1 - P.cv_share) / p
    t_cv = e * P.cv_share / (p * 0.35)                 # the CV phase averages ~35 % of the power (estimated)
    return round((t_cc + t_cv), 2)


def duty(pack="robot"):
    """For a few implements: hours of work per charge and the share of the day the robot can work with the dock."""
    out = {}
    for name, w in P.loads_w.items():
        work = P.pack_wh[pack] * 0.8 / w
        ch = charge(pack)
        out[name] = {"work_h": round(work, 1), "charge_h": ch, "work_share": round(work / (work + ch), 2),
                     "work_h_per_day": round(24.0 * work / (work + ch), 1)}
    return out


def report():
    out = {"contacts": contacts(), "catch": catch(), "charge_h_robot": charge("robot"),
           "charge_h_with_pack": charge("robot_plus_battery_pack"), "duty_robot": duty("robot"),
           "duty_with_pack": duty("robot_plus_battery_pack")}
    for k, v in out.items():
        print(k, v)
    return out
