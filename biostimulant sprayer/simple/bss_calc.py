"""Calculations for the biostimulant sprayer, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B bss_calc.py      (or in FreeCAD: import bss_calc; bss_calc.report())

Spray rate with all 15 nozzles open, pump and filter check for compost tea, aeration, weather window over a day,
area per tank and per day with refills, battery, axle loads (the spot sprayer's model plus the new parts).
"""
import math

import bss_params as P

S = P.S
ROBOT_CG = (0.0, 95.0, 543.0)       # agbot comparison (estimated), as in ssp_calc


def nozzle_flow(p=P.spray_p):
    return P.tip_q_3bar * math.sqrt(p / 3.0)


def spray(v=P.speed, p=P.spray_p):
    """Rate (l/ha) with all nozzles open, total flow against the pump, area per tank and time per tank."""
    q = nozzle_flow(p)
    rate = q / (S.nozzle_pitch / 1000.0 * v * 60.0) * 1e4
    q_all = S.n_nozzles * q
    ha_h = S.work_width / 1000.0 * v * 3600.0 / 1e4
    ha_tank = S.tank_nominal / rate
    return {"q_nozzle_l_min": round(q, 2), "rate_l_ha": round(rate), "q_all_l_min": round(q_all, 1),
            "pump_l_min": P.pump_q, "pump_ok": q_all <= P.pump_q, "gross_ha_h": round(ha_h, 2),
            "ha_per_tank": round(ha_tank, 2), "min_per_tank": round(ha_tank / ha_h * 60.0, 1)}


def speed_for(rate):
    """Speed (m/s) that gives a rate (l/ha) with all nozzles open at spray_p."""
    q = nozzle_flow()
    return q / (S.nozzle_pitch / 1000.0 * rate * 60.0) * 1e4


def filter_check():
    """Particles that pass the 50-mesh filter against the orifice of the 02 tip; pump pressure for living products."""
    passed = P.mesh_um / 1000.0
    limit = P.orifice_mm * P.max_particle_ratio
    return {"filter_mm": passed, "tip_orifice_mm": P.orifice_mm, "bridging_limit_mm": round(limit, 2),
            "tip_ok": passed <= limit, "pressure_bar": P.spray_p, "gentle": P.spray_p <= P.shear_ok_bar}


def aeration(litres=S.tank_nominal):
    """Air per litre of tank content per minute (compost tea brewers use ~0.05-0.1 l air per l per min)."""
    vvm = P.air_q / litres
    return {"air_l_min": P.air_q, "vvm": round(vvm, 3), "ok": 0.05 <= vvm <= 0.5}


def window_ok(w, t, rh, rain):
    W = P.WINDOW
    return w <= W["wind_max_m_s"] and W["t_min_c"] <= t <= W["t_max_c"] and rh >= W["rh_min_pct"] and rain <= 0.0


def weather_window(day=P.DAY):
    """Hours of the example day inside the window, and the hectares that fit in them (with refills)."""
    hours = [h for (h, w, t, rh, rain) in day if window_ok(w, t, rh, rain)]
    blocks = []
    for h in hours:
        if blocks and h == blocks[-1][1] + 1:
            blocks[-1][1] = h
        else:
            blocks.append([h, h])
    sp = spray()
    per_h = per_hour_with_refills(sp)
    return {"hours": len(hours), "blocks": [(a, b + 1) for a, b in blocks], "ha_per_h_incl_refill": round(per_h, 2),
            "ha_per_day": round(per_h * len(hours), 1)}


def per_hour_with_refills(sp=None):
    sp = sp or spray()
    t_tank = sp["min_per_tank"] / P.field_eff + P.refill_min
    return sp["ha_per_tank"] / (t_tank / 60.0)


def power(v=P.speed):
    w = S.pump_w + P.air_w + P.logger_w + P.drive_w_per_m_s * v
    h = P.battery_kwh * 1000.0 / w
    return {"total_W": round(w), "hours": round(h, 1), "ha_per_charge": round(h * per_hour_with_refills(), 1)}


def axle_loads(litres=S.tank_nominal):
    m = P.MODEL_MASS
    tank_y = 0.5 * (S.tank_y[0] + S.tank_y[1])
    items = [(P.robot_kg, ROBOT_CG[1]), (m["total_kg"], m["cg"][1]), (litres * S.liquid_density, tank_y)]
    total = sum(k for k, _ in items)
    moment = sum(k * (y + P.robot_axle_y) for k, y in items)
    front = moment / (2.0 * P.robot_axle_y)
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "rear_share": round((total - front) / total, 3)}


def report():
    out = {"spray": spray(), "speed_for_100_150_200_l_ha": {r: round(speed_for(r), 2) for r in (100, 150, 200)},
           "filter": filter_check(), "aeration": aeration(), "weather_window": weather_window(), "power": power(),
           "axle_full": axle_loads(), "axle_empty": axle_loads(0.0)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
