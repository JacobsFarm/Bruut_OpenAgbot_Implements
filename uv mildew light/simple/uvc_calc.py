"""Calculations for the UV-C mildew light, in pure Python (same parameters as the model).

    import uvc_calc
    uvc_calc.report()          # prints and returns all key figures
"""
import uvc_params as P

MODEL_KG = 21.2                 # build_uvc.mass_properties() (update after a change of the model)


def exposure_len():
    """Length (m) over which a plant is under the lamps: between the brush curtains."""
    return 2 * (P.hood_y - P.brush[0]) / 1000.0


def irradiance():
    """Average UV-C irradiance (W/m2) on the canopy plane under the hood."""
    uv = P.n_lamps * P.p_lamp * P.uv_eff
    area = 2 * (P.hood_x - P.sheet) / 1000.0 * exposure_len()
    return {"uv_W": round(uv, 1), "area_m2": round(area, 3), "E_W_m2": round(uv * P.reflect / area),
            "lamp_to_canopy_mm": P.lamp_z - P.canopy_z}


def speed_for(dose):
    """Driving speed (m/s) that gives a dose (J/m2) per pass: dose = E x L / v."""
    return irradiance()["E_W_m2"] * exposure_len() / dose


def run(dose):
    v = speed_for(dose)
    width = 2 * (P.hood_x - P.sheet) / 1000.0
    t_bed = P.bed_len / v + P.turn_s
    m2_h = width * P.bed_len * 3600.0 / t_bed
    p_lamps = P.n_lamps * P.p_lamp / P.ballast_eta
    p_drive = P.crr * (P.robot_mass + MODEL_KG) * P.g * v / P.eta_drive + P.p_drive_base
    p = p_lamps + p_drive
    h = P.battery_wh / p
    return {"dose_J_m2": dose, "speed_m_s": round(v, 2), "m2_per_hour": round(m2_h), "power_W": round(p),
            "hours_per_battery": round(h, 1), "m2_per_battery": round(m2_h * h),
            "beds_100m_per_battery": round(h * 3600.0 / t_bed, 1), "wh_per_100m2": round(p / m2_h * 100.0, 1)}


def report():
    out = {"exposure_m": exposure_len(), "irradiance": irradiance()}
    for k, d in P.dose_target.items():
        out[k] = run(d)
    for k, v in out.items():
        print(k, v)
    return out
