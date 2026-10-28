"""Calculations for the sawdust spreader, in pure Python (same parameters as the model).

    import sds_calc
    sds_calc.report()          # prints and returns all key figures
"""
import math

import sds_params as P


def load(material):
    rho = P.MATERIAL[material]
    kg = min(P.bin_volume() * rho, P.payload_max)
    return {"bin_l": round(P.bin_volume() * 1000), "kg": round(kg), "cubicles": int(kg / P.dose_kg[material])}


def auger_capacity(material, rpm):
    """kg/s the auger moves at a speed (rpm)."""
    area = math.pi / 4.0 * ((P.auger_d * 1e-3) ** 2 - (P.auger_shaft * 1e-3) ** 2)
    return area * P.auger_pitch * 1e-3 * rpm / 60.0 * P.auger_fill * P.MATERIAL[material]


def auger_rpm(material):
    """Auger speed for the dose per cubicle at the driving speed."""
    q = P.dose_kg[material] / P.cubicle_w * P.speed               # kg/s
    q_rev = auger_capacity(material, 60.0)                         # kg/s at 1 rev/s
    rpm = q / q_rev * 60.0
    return {"kg_s": round(q, 2), "rpm": round(rpm, 1), "ok": rpm <= P.auger_rpm_max}


def throw():
    """Throw width: tip speed of the disc and the flight to the bed (cubicle bed ~0.2 m above the alley)."""
    tip = math.pi * P.disc_d * 1e-3 * P.spinner_rpm / 60.0
    drop = (P.disc_z - 200.0) * 1e-3
    t = math.sqrt(2 * drop / P.g)
    reach = tip * t * P.throw_eff + (P.housing_x[1] - P.robot_wheel_x) * 1e-3
    return {"tip_m_s": round(tip, 1), "reach_from_wheel_m": round(reach, 2)}


def axle_and_tip(material):
    """Full: total mass, cg height and side tip angle (the spinner hangs out on the right)."""
    m = P.MODEL_MASS
    kg = load(material)["kg"]
    items = [(P.robot_mass, (0.0, P.robot_cg_z)), (m["spreader_kg"], (m["spreader_cg"][0], m["spreader_cg"][2])),
             (kg, (0.0, 1000.0))]
    tot = sum(k for k, _ in items)
    x = sum(k * c[0] for k, c in items) / tot
    z = sum(k * c[1] for k, c in items) / tot
    return {"total_kg": round(tot), "cg_x": round(x), "cg_z": round(z),
            "tip_right_deg": round(math.degrees(math.atan((P.robot_wheel_x - x) / z)), 1)}


def per_fill(material):
    ld = load(material)
    row_m = ld["cubicles"] * P.cubicle_w
    t_spread = row_m / P.speed
    t = t_spread + P.refill_s + P.travel_m / 1.0
    p = P.p_auger + P.p_spinner + P.crr * axle_and_tip(material)["total_kg"] * P.g * P.speed / P.eta_drive
    e = p * t_spread / 3600.0
    return {"cubicles": ld["cubicles"], "spread_s": round(t_spread), "cycle_s": round(t),
            "cubicles_per_hour": round(ld["cubicles"] * 3600.0 / t), "wh_per_fill": round(e, 1),
            "fills_per_battery": int(P.battery_wh / e)}


def report():
    out = {"bin_l": round(P.bin_volume() * 1000), "throw": throw()}
    for mat in P.MATERIAL:
        out[mat] = {"load": load(mat), "auger": auger_rpm(mat), "full": axle_and_tip(mat), "per_fill": per_fill(mat)}
    for k, v in out.items():
        print(k, v)
    return out
