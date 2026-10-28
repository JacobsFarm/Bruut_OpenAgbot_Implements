"""Calculations for the stone picker, in pure Python (same parameters as the model).

    import spk_calc
    spk_calc.report()          # prints and returns all key figures

Masses come from build_spk.mass_properties() (copied into spk_params.MODEL_MASS after a rebuild).
"""
import math

import spk_params as P


def basket():
    """Basket volume and the stone load it holds (usable share)."""
    v = P.basket_volume()
    kg = v * 1e-3 * P.stone_bulk * P.basket_fill
    return {"volume_l": round(v, 1), "stones_kg": round(kg, 1)}


def rotor():
    """Tip speed, soil raking power and the motor power at the working speed."""
    tip = 2 * math.pi * P.tip_r * 1e-3 * P.rotor_rpm / 60.0
    soil = P.work_w * P.depth * 1e-3 * P.speed            # m3/s raked
    p_soil = soil * P.e_soil * 1000.0
    p = (p_soil + P.p_idle) / P.eta_gm
    torque = (p_soil + P.p_idle) / (2 * math.pi * P.rotor_rpm / 60.0)
    return {"tip_m_s": round(tip, 1), "tip_over_speed": round(tip / P.speed, 1), "power_W": round(p),
            "rotor_Nm": round(torque, 1)}


def lift_force(theta, stones_kg):
    """Actuator force (N) that holds the frame at a link angle (virtual work: weight x dz / dL)."""
    m = P.MODEL_MASS["lift_kg"] + P.MODEL_MASS["links_kg"] / 2.0 + stones_kg
    d = 0.5
    dz = P.frame_shift(theta + d)[1] - P.frame_shift(theta - d)[1]
    dl = P.act_length(theta + d) - P.act_length(theta - d)
    return round(abs(m * P.g * dz / dl))


def lift():
    full = basket()["stones_kg"]
    lo, hi = P.act_length(P.theta_work), P.act_length(P.theta_lift)
    fmax = max(lift_force(t, full) for t in (P.theta_work, (P.theta_work + P.theta_lift) / 2.0, P.theta_lift))
    return {"lift_mm": round(P.frame_shift(P.theta_lift)[1]), "forward_mm": round(P.frame_shift(P.theta_lift)[0]),
            "act_mm": (round(hi), round(lo)), "act_range_ok": P.act_retracted <= hi and lo <= P.act_retracted + P.act_stroke,
            "force_full_N": fmax, "force_ok": fmax <= P.act_force, "time_s": round((lo - hi) / P.act_speed)}


def combined(stones_kg):
    m = P.MODEL_MASS
    items = [(P.robot_mass, (P.robot_cg_y, P.robot_cg_z)), (m["picker_kg"], m["picker_cg"][1:]),
             (stones_kg, m["basket_cg"][1:])]
    tot = sum(k for k, _ in items)
    return tot, sum(k * c[0] for k, c in items) / tot, sum(k * c[1] for k, c in items) / tot


def axle_loads(stones_kg):
    tot, y, z = combined(stones_kg)
    front = tot * (y + P.wheelbase_half) / (2 * P.wheelbase_half)
    return {"total_kg": round(tot), "front_share": round(front / tot, 3), "cg_z": round(z),
            "side_tip_deg": round(math.degrees(math.atan(P.track_half / z)), 1)}


def draft(stones_kg):
    """Pull needed (N): rolling of robot + picker and the comb drag, against grip and the motors."""
    tot, _, _ = combined(stones_kg)
    need = P.crr * tot * P.g + P.comb_draft
    grip = P.mu_tyre * tot * P.g
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    return {"need_N": round(need), "margin": round(min(grip, motors) / need, 2)}


def per_basket(job):
    """One basket: area, length and time to fill it, dumping, area per hour, energy."""
    kg = basket()["stones_kg"]
    area = kg / P.STONES[job]
    length = area / P.work_w
    t_work = length / P.speed
    t_cycle = t_work + P.dump_s + P.headland_m / 1.2
    tot, _, _ = combined(kg / 2.0)
    e_drive = (P.crr * tot * P.g + P.comb_draft) * length / P.eta_drive / 3600.0
    e_drive += P.crr * tot * P.g * P.headland_m / P.eta_drive / 3600.0
    e_rotor = rotor()["power_W"] * t_work / 3600.0
    e = e_drive + e_rotor
    return {"kg_m2": P.STONES[job], "area_m2": round(area), "length_m": round(length), "fill_s": round(t_work),
            "cycle_s": round(t_cycle), "m2_per_hour": round(area * 3600.0 / t_cycle),
            "ha_per_day_8h": round(area * 3600.0 / t_cycle * 8 / 10000.0, 2), "wh_per_basket": round(e, 1),
            "hours_per_battery": round(P.battery_wh / (e / t_cycle * 3600.0), 1)}


def report():
    b = basket()
    out = {"basket": b, "rotor": rotor(), "lift": lift(), "empty": {**axle_loads(0.0), **draft(0.0)},
           "full": {**axle_loads(b["stones_kg"]), **draft(b["stones_kg"])}}
    for job in P.STONES:
        out[job] = per_basket(job)
    for k, v in out.items():
        print(k, v)
    return out
