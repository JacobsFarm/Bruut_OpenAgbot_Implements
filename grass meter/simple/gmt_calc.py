"""Calculations for the grass meter, in pure Python (same parameters as the model).

    import gmt_calc
    gmt_calc.report()          # prints and returns all key figures
"""
import math

import gmt_params as P

MODEL_KG = 22.0                 # build_gmt.mass_properties() (update after a change of the model)


def plate():
    """Plate pressure and the height resolution of the angle sensor over the measuring range."""
    area = (P.plate_side / 1000.0) ** 2
    lo, hi = P.H_RANGE
    a_lo, a_hi = P.arm_angle(lo), P.arm_angle(hi)
    step = 360.0 / 2 ** P.encoder_bits
    # dh per encoder step at the steepest and the flattest arm angle: dh = L cos(a) da
    res = [P.arm_len * math.cos(math.radians(a)) * math.radians(step) for a in (a_lo, a_hi)]
    return {"area_m2": round(area, 3), "pressure_kg_m2": round(P.plate_mass / area, 1),
            "arm_deg": (round(a_lo, 1), round(a_hi, 1)), "resolution_mm": (round(min(res), 2), round(max(res), 2)),
            "lifted_mm": P.lift_h}


def dry_matter(h_mm):
    """kg DM/ha from the compressed height (farm calibration needed)."""
    return P.dm_a * h_mm / 10.0 + P.dm_b


def sampling():
    """Spacing of the readings along the track at the mapping speed."""
    return {k: round(P.speed / hz * 1000.0) for k, hz in P.rate_hz.items()}


def ndvi_footprint():
    """Width of the NDVI spot (field of view about 45 x 10 degrees at the lens height) and the strips per pass."""
    h = P.ndvi_z / 1000.0
    w = 2 * h * math.tan(math.radians(45.0 / 2))
    return {"spot_w_m": round(w, 2), "strips_x_m": (-P.ndvi_x / 1000.0, P.ndvi_x / 1000.0)}


def capacity():
    """Area mapped per hour on transects, run time and area per battery charge."""
    t_m = P.transect / P.speed
    turn = P.turn_s
    run_len = 100.0                                    # m per transect (example field 100 m long)
    ha_h = (run_len * P.transect) / (run_len / P.speed + turn) * 3600.0 / 10000.0
    tot = P.robot_mass + MODEL_KG
    p_drive = P.crr * tot * P.g * P.speed / P.eta_drive
    p = p_drive + P.p_sensors
    hours = P.battery_wh / p
    return {"ha_per_hour": round(ha_h, 2), "power_W": round(p), "hours_per_battery": round(hours, 1),
            "ha_per_battery": round(hours * ha_h, 1), "plate_readings_per_ha": round(10000.0 / P.transect / (P.speed / P.rate_hz["plate"]))}


def report():
    out = {"plate": plate(), "dm_kg_ha": {h: round(dry_matter(h)) for h in (30, 60, 100, 150)},
           "sampling_mm": sampling(), "ndvi": ndvi_footprint(), "capacity": capacity(), "mass_kg": MODEL_KG}
    for k, v in out.items():
        print(k, v)
    return out
