"""Calculations for the cover crop undersower, in pure Python (same parameters as the model).

    import ccu_calc
    ccu_calc.report()          # prints and returns all key figures
"""
import math

import ccu_params as P


def sown_share():
    """Share of the pass width that gets seed (3 bands)."""
    return (P.band_w[0] + 2 * P.band_w[1]) / P.pass_w


def seed_per_band(species, kg_ha=None):
    """Seed per 100 m of each band (g) and roller speed (rpm) at the working speed. The field rate is put into the
    bands only (same seed per m2 of field, so a higher density in the band)."""
    rate, rho = P.SPECIES[species]
    rate = rate if kg_ha is None else kg_ha
    flow_g_s = rate * 1000.0 / 1e4 * (P.pass_w / 1000.0) * P.speed      # g/s for the whole pass
    ml_s = flow_g_s / rho                                               # ml/s (rho kg/l = g/ml)
    shares = [P.band_w[0] / (P.band_w[0] + 2 * P.band_w[1])] + [P.band_w[1] / (P.band_w[0] + 2 * P.band_w[1])] * 2
    rpm = [ml_s * s / P.roller_ml * 60.0 for s in shares]
    return {"g_per_s": round(flow_g_s, 2), "roller_rpm_mid_side": (round(rpm[0], 1), round(rpm[1], 1)),
            "ok": max(rpm) <= P.gm_rpm_max, "band_density_x": round(1.0 / sown_share(), 2)}


def area_per_fill(species):
    rate, rho = P.SPECIES[species]
    kg = P.MODEL_MASS["volume_l"] * rho
    return {"kg": round(kg, 1), "ha": round(kg / rate, 2)}


def drive():
    tot = P.robot_mass + P.MODEL_MASS["kg"] + P.MODEL_MASS["volume_l"] * 0.7
    roll = P.crr * tot * P.g
    draft = P.tine_force_N * len(P.tine_x)
    w = (roll + draft) * P.speed / P.eta_drive + 15.0          # + metering motor
    ha_h = P.pass_w / 1000.0 * P.speed * 3600.0 / 1e4 * P.field_eff
    return {"rolling_N": round(roll), "tines_N": round(draft), "power_W": round(w), "ha_h": round(ha_h, 2),
            "ha_per_charge": round(ha_h * P.robot_battery_wh / w, 1)}


def axle_loads():
    m = P.MODEL_MASS
    load = m["volume_l"] * 0.72
    items = [(P.robot_mass, 0.0), (m["kg"], m["cg_y"]), (load, (P.hop_y[0] + P.hop_y[1]) / 2.0)]
    tot = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2.0 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(tot - front, 1), "rear_share": round((tot - front) / tot, 3)}


def report():
    out = {"sown_share": round(sown_share(), 2),
           "per_species": {k: dict(seed_per_band(k), **{"fill": area_per_fill(k)}) for k in P.SPECIES},
           "drive": drive(), "axle_full_rye": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
