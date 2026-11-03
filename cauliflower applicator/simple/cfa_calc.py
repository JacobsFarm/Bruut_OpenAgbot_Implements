"""Calculations for the cauliflower root-crown applicator (pure Python, no FreeCAD): nozzle flow and pulse length,
dose per plant and per hectare, pump and accumulator, tank range, capacity, battery, parallelogram float, skid
pressure and drag, sensor timing, axle loads.

    python cfa_calc.py          (or in FreeCAD: import cfa_calc; cfa_calc.report())
"""
import math

import cfa_params as P

G_ACC = 9.81

# last measurement from the model (build_cfa.mass_properties: steel 7850, PE 950, UHMW 940 kg/m3, bought parts
# with their catalogue mass). Tank empty; the liquid is added here.
MODEL = {"kg": 56.5, "cg": (7.0, -71.0, 586.0), "row_unit_kg": 8.2, "tank_kg": 16.1}


# ---------------------------------------------------------------------
# Nozzle and pulse
# ---------------------------------------------------------------------
def nozzle_flow(p=P.pressure, d=P.orifice):
    """Flow of one open nozzle (ml/s): orifice equation."""
    a = math.pi * (d / 2000.0) ** 2
    v = math.sqrt(2.0 * p * 1e5 / (P.liquid_density * 1000.0))
    return P.cd * a * v * 1e6


def pulse(dose=P.dose_ml, v=P.speed, p=P.pressure):
    """Pulse length (ms) for the dose per side, and the length of soil it covers (mm)."""
    q = nozzle_flow(p)
    open_ms = dose / q * 1000.0
    t = open_ms + P.valve_ms                    # opening + closing time roughly cancel; add one for the delay
    return {"q_ml_s": round(q, 1), "open_ms": round(open_ms), "pulse_ms": round(t),
            "band_mm": round(v * open_ms), "q_l_min": round(q * 0.06, 2)}


def dose(v=P.speed):
    plants_ha = 1e10 / (P.row_pitch * P.plant_pitch)
    per_plant = 2.0 * P.dose_ml
    rate = len(P.rows_x) * v * 1000.0 / P.plant_pitch            # plants per second
    return {"plants_ha": round(plants_ha), "ml_plant": per_plant, "l_ha": round(plants_ha * per_plant / 1000.0),
            "plants_s": round(rate, 2), "ml_s": round(rate * per_plant, 1),
            "l_min_mean": round(rate * per_plant * 0.06, 2)}


def pump(v=P.speed):
    """Peak: all 4 valves open together (rows in step); the accumulator gives what the pump cannot."""
    q4 = 4.0 * nozzle_flow()
    qp = P.pump_q_2bar / 0.06
    t = pulse(v=v)["open_ms"] / 1000.0
    deficit = max(0.0, (q4 - qp) * t)
    mean = dose(v)["ml_s"]
    return {"peak_ml_s": round(q4), "pump_ml_s": round(qp), "deficit_ml": round(deficit, 1),
            "duty": round(mean / qp, 2), "headroom": round(qp / mean, 1)}


def tank(v=P.speed):
    d = dose(v)
    plants = P.tank_nominal * 1000.0 / d["ml_plant"]
    t_min = P.tank_nominal * 1000.0 / d["ml_s"] / 60.0
    return {"plants": round(plants), "ha": round(plants / d["plants_ha"], 2), "min": round(t_min),
            "row_m": round(plants / len(P.rows_x) * P.plant_pitch / 1000.0)}


def capacity(v=P.speed):
    width = len(P.rows_x) * P.row_pitch / 1000.0
    ha_h = width * v * 3600.0 / 1e4
    return {"width_m": width, "ha_h": round(ha_h, 3), "ha_h_eff": round(ha_h * P.field_eff, 3)}


def power(v=P.speed):
    pu = pump(v)
    p_open = 4.0 * P.valve_w * pulse(v=v)["pulse_ms"] / 1000.0 * dose(v)["plants_s"] / 2.0
    w = P.drive_w + P.controller_w + P.pump_w * min(1.0, pu["duty"] * 1.5) + p_open
    return {"w": round(w), "h": round(P.battery_kwh * 1000.0 / w, 1),
            "ha_per_charge": round(P.battery_kwh * 1000.0 / w * capacity(v)["ha_h_eff"], 2)}


# ---------------------------------------------------------------------
# Row unit
# ---------------------------------------------------------------------
def float_pose(dz):
    """Parallelogram: head moves dz (mm, + up). Returns the arm angle (deg, + up) and the head y shift."""
    s = max(-1.0, min(1.0, dz / P.pl_len))
    a = math.asin(s)
    return math.degrees(a), P.pl_len * (1.0 - math.cos(a))


def skid(kg=None):
    """Ground pressure and drag of the two skids (unit weight only, no spring)."""
    m = kg if kg is not None else MODEL["row_unit_kg"] * 0.8       # part of the arm weight hangs on the toolbar
    area = 2.0 * (P.skid_dx[1] - P.skid_dx[0]) * (P.skid_y[1] - P.skid_y[0]) * 1e-6
    f = m * G_ACC
    return {"load_n": round(f), "kpa": round(f / area / 1000.0, 2), "drag_n": round(P.skid_mu * f)}


def timing(v=P.speed):
    """Sensor to nozzle: the controller waits this long after the crown peak (odometry, not time)."""
    t = P.sensor_lead / (v * 1000.0)
    err = v * 1000.0 * 0.02                     # 20 ms jitter (sensor 50 Hz)
    return {"lead_mm": round(P.sensor_lead), "delay_s": round(t, 2), "jitter_mm": round(err)}


def clearances():
    return {"arch_over_crop": round(P.arch_z[0] - P.plant_h),
            "toolbar_over_ground": round(P.bar_z[0]),
            "leg_to_stem": round(P.leg_dx[0]),
            "lifter_tip_to_stem": round(P.lifter_tip[0]),
            "tip_landing_dx": round(P.target_dx)}


def axle_loads(litres=P.tank_nominal):
    """Static axle loads (kg): robot + implement + liquid; liquid centre over the tank centre."""
    items = [(P.robot_kg, P.robot_cg[1]), (MODEL["kg"], MODEL["cg"][1]),
             (litres * P.liquid_density, (P.tank_y[0] + P.tank_y[1]) / 2.0)]
    m = sum(i[0] for i in items)
    y = sum(i[0] * i[1] for i in items) / m
    front = m * (y + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    return {"total_kg": round(m, 1), "cg_y": round(y), "front_kg": round(front, 1), "rear_kg": round(m - front, 1)}


def report():
    print("nozzle / pulse     ", pulse())
    print("dose               ", dose())
    print("pump               ", pump())
    print("tank %d l          " % P.tank_nominal, tank())
    print("capacity           ", capacity())
    print("power              ", power())
    print("float +-60         ", [tuple(round(x, 1) for x in float_pose(dz)) for dz in P.float_range])
    print("skids              ", skid())
    print("timing             ", timing())
    print("clearances         ", clearances())
    print("axle loads full    ", axle_loads())
    print("axle loads empty   ", axle_loads(0.0))


if __name__ == "__main__":
    report()
