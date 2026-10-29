"""Calculations for the electric weeder, in pure Python (same parameters as the model).

    import elw_calc
    elw_calc.report()          # prints and returns all key figures
"""
import elw_params as P


def contact():
    """Time a weed is under the comb (s) and the energy the generator can put in (kJ)."""
    t = P.comb_len / P.speed
    return {"contact_s": round(t, 2), "kJ_max": round(P.hv_power_W * t / 1000.0, 2)}


def max_speed(stage):
    """Highest speed (m/s) at which the generator still gives a weed its kill energy in one pass."""
    return round(P.hv_power_W * P.comb_len / (P.weed_energy_kJ[stage] * 1000.0), 2)


def spot(weeds_m2, stage="4_leaf"):
    """Spot mode: battery energy per m2 of band and m2 / ha per charge."""
    e_weed = P.weed_energy_kJ[stage] * 1000.0 / P.eta_hv                 # J from the battery per weed
    hv_J_m2 = weeds_m2 * e_weed
    t_m2 = 1.0 / (P.band_w * P.speed)                                    # s to do 1 m2 of band
    drive_W = P.crr * (P.robot_mass + P.MODEL_MASS["kg"]) * P.g * P.speed / P.eta_drive
    J_m2 = hv_J_m2 + (P.idle_W + drive_W) * t_m2
    band_m2 = P.robot_battery_wh * 3600.0 / J_m2
    field_ha = band_m2 / P.band_w * P.pass_w / 1e4
    duty = hv_J_m2 / t_m2 / (P.hv_power_W / P.eta_hv)
    return {"weeds_per_charge": round(band_m2 * weeds_m2), "band_m2_per_charge": round(band_m2),
            "field_ha_per_charge": round(field_ha, 2), "hv_duty": round(duty, 2),
            "ok": duty <= 1.0}


def broadcast():
    """Continuous mode over the band (all HV on), for comparison."""
    kwh_band_ha = P.broadcast_kWh_ha
    band_ha = P.robot_battery_wh / 1000.0 / kwh_band_ha
    return {"band_ha_per_charge": round(band_ha, 3), "field_ha_per_charge": round(band_ha / P.band_w * P.pass_w, 2)}


def work_rate():
    ha_h = P.pass_w * P.speed * 3600.0 / 1e4 * P.field_eff
    return {"field_ha_h": round(ha_h, 3), "band_m2_h": round(P.band_w * P.speed * 3600.0 * P.field_eff)}


def actuator():
    lens = [P.act_length(a) for a in P.LIFT_POSES]
    return {"length_range": (round(min(lens), 1), round(max(lens), 1)),
            "fits_stroke": P.act_retracted <= min(lens) and max(lens) <= P.act_retracted + P.act_stroke,
            "comb_lift_mm": round(P.arm_len * __import__("math").sin(__import__("math").radians(P.lift_transport)))}


def report():
    out = {"contact": contact(), "max_speed_m_s": {k: max_speed(k) for k in P.weed_energy_kJ},
           "spot_4_leaf": {w: spot(w) for w in P.weeds_m2}, "broadcast": broadcast(), "work_rate": work_rate(),
           "actuator": actuator()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
