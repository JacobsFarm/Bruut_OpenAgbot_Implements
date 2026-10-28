"""Calculations for the biological-control spreader, in pure Python (same parameters as the model).

    import bcs_calc
    bcs_calc.report()          # prints and returns all key figures
"""
import math

import bcs_params as P

MODEL_KG = 17.9                  # build_bcs.mass_properties() (update after a change of the model)


def hopper_l():
    """Volume (l) of one hopper: cylinder plus cone."""
    r = (P.hopper_d - 2 * P.hopper_wall) / 2.0
    cyl = math.pi * r ** 2 * P.hopper_h
    cone = math.pi * P.cone_h / 3.0 * (r ** 2 + r * 17.0 + 17.0 ** 2)
    return (cyl + cone) * 1e-6


def product(name):
    """Carrier flow per hopper (ml/s), metering wheel speed, area per fill, time per fill."""
    pr = P.PRODUCTS[name]
    ml_m2 = pr["dose_m2"] / pr["per_l"] * 1000.0
    area_s = P.band_w * P.speed                                     # m2/s for both rows
    ml_s = ml_m2 * area_s / 2.0                                     # per hopper
    rpm = ml_s / P.meter_ml_rev * 60.0
    fill_ml = 2 * hopper_l() * 1000.0
    area = fill_ml / ml_m2
    return {"ml_per_m2": round(ml_m2, 2), "ml_s_per_hopper": round(ml_s, 2), "meter_rpm": round(rpm, 2),
            "rpm_ok": rpm <= P.meter_rpm_max, "m2_per_fill": round(area), "ha_per_fill": round(area / 1e4, 2),
            "h_per_fill": round(area / area_s / 3600.0, 1)}


def air():
    a = math.pi / 4.0 * ((P.hose_d - 4.0) * 1e-3) ** 2
    return {"l_s_per_hose": round(a * P.air_v * 1000.0, 1), "air_v_m_s": P.air_v}


def capacity():
    area_h = P.band_w * P.speed * 3600.0
    p = P.p_fan + 2 * P.p_meter + P.crr * (P.robot_mass + MODEL_KG) * P.g * P.speed / P.eta_drive
    return {"m2_per_hour": round(area_h), "power_W": round(p), "hours_per_battery": round(P.battery_wh / p, 1),
            "ha_per_battery": round(area_h * P.battery_wh / p / 1e4, 2)}


def report():
    out = {"hopper_l": round(hopper_l(), 1), "air": air(), "capacity": capacity()}
    for k in P.PRODUCTS:
        out[k] = product(k)
    for k, v in out.items():
        print(k, v)
    return out
