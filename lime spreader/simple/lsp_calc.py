"""Calculations for the lime spreader, in pure Python (same parameters as the model).

    import lsp_calc
    lsp_calc.report()          # prints and returns all key figures

Masses and the hopper volume come from build_lsp (copied into lsp_params.MODEL_MASS after a rebuild).
"""
import math

import lsp_params as P


def width_m():
    return 2.0 * P.cross_x / 1000.0


def load_kg(kind="granulated"):
    return P.MODEL_MASS["volume_l"] * P.rho_lime[kind]


def auger_l_per_rev():
    """Volume (l) one turn of an auger moves at the fill factor."""
    a = math.pi / 4.0 * (P.auger_d ** 2 - P.auger_shaft_d ** 2)
    return a * P.auger_pitch * P.fill_auger / 1e6


def dose(kg_ha, kind="granulated", speed=P.speed):
    """Flow (kg/s), auger speed (rpm), area (ha) and distance per fill for a dose."""
    flow = kg_ha * width_m() * speed / 1e4
    rpm = flow / (auger_l_per_rev() * P.rho_lime[kind]) * 60.0
    ha = load_kg(kind) / kg_ha
    return {"flow_kg_s": round(flow, 3), "auger_rpm": round(rpm, 1), "ok": rpm <= P.auger_rpm_max,
            "ha_per_fill": round(ha, 3), "m_per_fill": round(ha * 1e4 / width_m()),
            "fill_min": round(ha * 1e4 / (width_m() * speed) / 60.0, 1)}


def max_dose(kind="granulated", speed=P.speed):
    flow = P.auger_rpm_max / 60.0 * auger_l_per_rev() * P.rho_lime[kind]
    return round(flow * 1e4 / (width_m() * speed))


def auger_power(kg_ha=2000.0, kind="granulated"):
    """Power (W) of the 2 augers: lambda * flow * g * length + idle (screw conveyor rule)."""
    flow = dose(kg_ha, kind)["flow_kg_s"]
    L = (P.long_y[0] - P.long_y[1]) / 1000.0 + P.cross_x / 1000.0
    return round(P.lambda_screw * flow * P.g * L + 2 * P.auger_idle_W)


def axle_loads(kind="granulated", full=True):
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg_y, P.robot_cg_z), (m["kg"], m["cg_y"], m["cg_z"])]
    if full:
        items.append((load_kg(kind), m["fill_cg_y"], m["fill_cg_z"]))
    total = sum(k for k, _, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y, _ in items) / (2.0 * P.robot_axle_y)
    cg_z = sum(k * z for k, _, z in items) / total
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "rear_share": round((total - front) / total, 3), "cg_z": round(cg_z),
            "per_tyre_kg": round(total / 4.0, 1)}


def tipping(kind="granulated"):
    """Static side slope (deg) before the robot tips: atan(half track / cg height)."""
    a = axle_loads(kind)
    return round(math.degrees(math.atan(P.robot_track / 2.0 / a["cg_z"])), 1)


def drive(kind="granulated"):
    a = axle_loads(kind)
    roll = P.crr_field * a["total_kg"] * P.g
    cont = P.hub_torque_nom * P.n_driven / P.r_load
    return {"rolling_N": round(roll), "motor_cont_N": round(cont), "drive_W": round(roll * P.speed / P.eta_drive),
            "slope_deg_left": round(math.degrees(math.asin(max(0.0, (cont - roll) / (a["total_kg"] * P.g)))), 1)}


def capacity(kg_ha=1000.0):
    ha_h = width_m() * P.speed * 3600.0 / 1e4 * P.field_eff
    w = drive()["drive_W"] + auger_power(kg_ha)
    return {"ha_h": round(ha_h, 2), "power_W": w, "hours_per_charge": round(P.robot_battery_wh / w, 1),
            "fills_per_charge": round(P.robot_battery_wh / w / (dose(kg_ha)["fill_min"] / 60.0 / P.field_eff), 1)}


def report():
    out = {"load": {k: round(load_kg(k)) for k in P.rho_lime}, "width_m": width_m(),
           "auger_l_per_rev": round(auger_l_per_rev(), 3),
           "dose": {kg: dose(kg) for kg in P.dose_kg_ha}, "max_dose_kg_ha": max_dose(),
           "auger_power_W_2000": auger_power(2000.0), "axle_full": axle_loads(), "axle_empty": axle_loads(full=False),
           "tipping_deg": tipping(), "drive": drive(), "capacity_1000": capacity(1000.0)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
