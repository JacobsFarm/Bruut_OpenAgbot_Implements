"""Calculations for the air-assisted orchard sprayer, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B oas_calc.py      (or in FreeCAD: import oas_calc; oas_calc.report())

Air volume per side and the forward speed it allows, liquid output and dose per hectare, tank time, power and battery
time, saving by canopy sensing and the lidar lead time, axle loads with a full and an empty tank, mast bending.
"""
import math

import oas_params as P


def air():
    """Air needed to replace the air in the canopy band beside the robot: Q = v x H x (row spacing / 2) x factor.
    The 3 fans per side give 3 x fan_q: the speed at which that is enough."""
    q_side = 3 * P.fan_q_m3_h / 3600.0                               # m3/s
    h = P.canopy_h[1] - P.canopy_h[0]
    v = q_side / (h * P.row_spacing / 2.0 * P.air_factor)
    a_out = math.pi * (P.fan_d / 2000.0) ** 2 - math.pi * (P.hub_d / 2000.0) ** 2
    return {"q_side_m3_h": round(q_side * 3600), "outlet_speed_m_s": round(P.fan_q_m3_h / 3600.0 / a_out, 1),
            "v_max_m_s": round(v, 2), "v_max_km_h": round(v * 3.6, 2)}


def liquid(v=None):
    v = air()["v_max_m_s"] if v is None else v
    q = 2 * 3 * P.nozzles_per_pod * P.nozzle_l_min                  # l/min, all sections open
    ha_h = v * P.row_spacing * 3600.0 / 1e4                          # both half rows = one row spacing per pass
    dose = q * 60.0 / ha_h
    q_sensed = q * (1.0 - P.canopy_gap_share)
    t_tank = P.tank_l / q_sensed
    return {"q_l_min": round(q, 1), "ha_h": round(ha_h, 2), "dose_l_ha": round(dose), "dose_ok": P.dose_l_ha[0] <= dose <= P.dose_l_ha[1],
            "q_with_sensing_l_min": round(q_sensed, 2), "tank_min": round(t_tank), "ha_per_tank": round(ha_h * t_tank / 60.0, 2),
            "liquid_saved_l_ha": round(dose * P.canopy_gap_share)}


def power():
    p = 6 * P.fan_w + P.pump_w + P.drive_w + P.electronics_w
    e = P.robot_battery_kwh * 1000.0 * 0.85
    h = e / p
    lq = liquid()
    return {"power_W": round(p), "fans_W": 6 * P.fan_w, "battery_h": round(h, 2), "tanks_per_charge": round(h * 60.0 / lq["tank_min"], 1),
            "ha_per_charge": round(lq["ha_h"] * h, 2)}


def lidar():
    v = air()["v_max_m_s"]
    t = P.lidar_lead / 1000.0 / v
    return {"lead_mm": round(P.lidar_lead), "lead_s": round(t, 2), "valve_latency_s": P.valve_latency_s,
            "ok": t > 2 * P.valve_latency_s}


def axle_loads(full=True):
    m = P.MODEL_MASS
    ms = [(P.robot_kg, P.robot_cg), (m["total_kg"], m["cg"])]
    if full:
        import ssp_params as SP
        ty = 0.5 * (SP.tank_y[0] + SP.tank_y[1])
        ms.append((P.liquid_kg, (0.0, ty, SP.tank_z[0] + 70.0)))
    tot = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / tot for i in range(3))
    front = tot * (cg[1] + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    side = math.degrees(math.atan(P.robot_wheel_x / cg[2]))
    return {"total_kg": round(tot, 1), "cg": tuple(round(c) for c in cg), "front_share": round(front / tot, 3),
            "rear_wheel_kg": round((tot - front) / 2.0, 1), "tip_side_deg": round(side, 1)}


def mast():
    """Mast foot: pods + mast above the cross beam, fore-aft braking 0.3 g and sideways 0.3 g (bumps, slope), and the
    stress in the 80 x 80 x 4 mast at the foot."""
    m_top = 6 * P.fan_kg + 16.0 + 3.0                                # pods, mast, lidars and arm
    h = 0.5 * (P.pod_z[0] + P.pod_z[-1]) - P.mast_z[0]
    mom = m_top * P.g * 0.3 * h                                      # Nmm
    a, w = P.mast, P.mast_wall
    wz = (a ** 4 - (a - 2 * w) ** 4) / (6.0 * a)
    return {"mass_kg": round(m_top, 1), "moment_Nm": round(mom / 1000.0), "stress_MPa": round(mom / wz, 1)}


def report():
    out = {"air": air(), "liquid": liquid(), "power": power(), "lidar": lidar(), "axle_full": axle_loads(True),
           "axle_empty": axle_loads(False), "mast": mast()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
