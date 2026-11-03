"""Calculations for the hot foam weeder, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B hfw_calc.py      (or in FreeCAD: import hfw_calc; hfw_calc.report())

Boiler: water flow at full fire, the speed that gives the dose, propane use; energy on the soil against the flame
weeder; time under the hood and how long the foam holds the heat; water, gas, foam and battery range; cost per 100 m2;
axle loads with a full and an empty tank.
Masses come from build_hfw.mass_properties() (copied into hfw_params.MODEL_MASS after a rebuild).
"""
import hfw_params as P

W = P.W


def boiler():
    """Water flow (l/min) the boiler heats from t_in to t_out at full fire, and the propane it burns (kg/h)."""
    dt = P.t_out - P.t_in
    q_kg_s = P.boiler_kw / (P.cp_water * dt)
    gas_kg_h = P.boiler_kw / P.boiler_eff / (P.lhv * 1000.0) * 3600.0
    return {"dT_K": dt, "water_l_min": round(q_kg_s * 60.0, 2), "gas_kg_h": round(gas_kg_h, 2),
            "pump_ok": q_kg_s * 60.0 < 11.0}


def work():
    """Speed for the dose over the full hood width, area rate, time under the hood, and the heat on the soil."""
    b = boiler()
    q_l_s = b["water_l_min"] / 60.0
    width = W.work_w / 1000.0
    v = q_l_s / (width * P.dose_l_m2)                       # m/s
    m2_h = q_l_s / P.dose_l_m2 * 3600.0
    hood_len = (W.hood_y[1] - W.hood_y[0]) / 1000.0
    under = hood_len / v
    t_soil = P.t_out - P.hose_loss_k
    kj_m2 = P.dose_l_m2 * P.cp_water * (t_soil - P.t_in)
    flame_kj_m2 = P.flame_kg_ha * P.lhv * 1000.0 / 1e4
    gas_kg_ha = b["gas_kg_h"] / (m2_h / 1e4)
    return {"speed_m_s": round(v, 3), "m2_h": round(m2_h), "ha_h": round(m2_h / 1e4, 3),
            "under_hood_s": round(under, 1), "lethal_s": P.lethal_s, "foam_hold_s": P.foam_hold_s,
            "heat_on_soil_kJ_m2": round(kj_m2), "flame_weeder_kJ_m2": round(flame_kj_m2),
            "gas_kg_ha": round(gas_kg_ha), "flame_gas_kg_ha": P.flame_kg_ha,
            "gas_vs_flame": round(gas_kg_ha / P.flame_kg_ha, 1)}


def ranges():
    """Area per tank of water, per propane fill (2 x 18 kg), per 10 l foam can and per battery charge."""
    w = work()
    b = boiler()
    m2_tank = P.tank_l / P.dose_l_m2
    t_tank_min = P.tank_l / b["water_l_min"]
    m2_gas = 2 * P.cyl_kg_gas / b["gas_kg_h"] * w["m2_h"]
    m2_foam = 10.0 / P.foam_share / P.dose_l_m2
    power = P.drive_w + P.control_w + P.pump_w + P.boiler_fan_w + 15.0      # 15 W doser
    hours = P.battery_kwh * 1000.0 / power
    return {"m2_per_tank": round(m2_tank), "minutes_per_tank": round(t_tank_min, 1),
            "m2_per_gas_fill": round(m2_gas), "m2_per_foam_can": round(m2_foam), "power_W": round(power),
            "battery_h": round(hours, 1), "m2_per_charge": round(hours * w["m2_h"] * P.field_eff),
            "path_m_per_tank": round(m2_tank / (W.work_w / 1000.0))}


def cost():
    """Running cost (EUR) per 100 m2: water, propane, foam concentrate."""
    w = work()
    a = 100.0
    water = a * P.dose_l_m2 * P.water_price
    gas = w["gas_kg_ha"] * a / 1e4 * P.gas_price
    foam = a * P.dose_l_m2 * P.foam_share * P.foam_price
    return {"water": round(water, 2), "gas": round(gas, 2), "foam": round(foam, 2), "total": round(water + gas + foam, 2)}


def axle_loads(water_l=P.tank_l, gas_kg=2 * P.cyl_kg_gas):
    """Front and rear axle (kg). The hood rides on its castors (as on the flame weeder); the robot carries the rest.
    Water centre at y 0 (belly tank), gas at the cylinders' centre (y 0)."""
    m = P.MODEL_MASS
    items = [(P.robot_kg, P.robot_cg[1]), (m["robot_side_kg"], m["robot_side_cg_y"]), (water_l, 0.0), (gas_kg, 0.0)]
    total = sum(k for k, _ in items)
    moment = sum(k * (y + P.robot_axle_y) for k, y in items)
    front = moment / (2.0 * P.robot_axle_y)
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "rear_share": round((total - front) / total, 3), "per_wheel_max_kg": round(max(front, total - front) / 2.0, 1)}


def report():
    out = {"boiler": boiler(), "work": work(), "ranges": ranges(), "cost_per_100m2": cost(),
           "axle_full": axle_loads(), "axle_empty": axle_loads(0.0, 0.0)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
