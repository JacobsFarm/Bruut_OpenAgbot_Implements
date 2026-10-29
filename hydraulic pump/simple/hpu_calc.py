"""Calculations for the hydraulic power pack, in pure Python (same parameters as the model).

    import hpu_calc
    hpu_calc.report()          # prints and returns all key figures
"""
import math

import hpu_params as P


def flow_lpm():
    return P.pump_cc * P.motor_rpm / 1000.0 * P.eta_vol


def power(p_bar):
    """Hydraulic and electric power (kW) at a pressure, full flow."""
    q = flow_lpm()
    hyd = p_bar * q / 600.0
    shaft = p_bar * P.pump_cc * P.motor_rpm / 1000.0 / 600.0 / P.eta_hm
    elec = shaft / P.eta_motor
    return {"hyd_kW": round(hyd, 2), "elec_kW": round(elec, 2), "ok_motor": shaft <= P.motor_kw,
            "ok_battery": elec <= P.battery_peak_kw, "minutes_full": round(P.robot_battery_wh / 1000.0 / elec * 60.0)}


def max_pressure():
    """Pressure (bar) the motor can hold at full flow."""
    return round(P.motor_kw * P.eta_hm * 600.0 / (P.pump_cc * P.motor_rpm / 1000.0))


def cylinder(name, p_bar=150.0):
    bore, rod, stroke = P.cylinders[name]
    a_push = math.pi / 4.0 * bore ** 2 / 100.0                      # cm2
    a_pull = math.pi / 4.0 * (bore ** 2 - rod ** 2) / 100.0
    q = flow_lpm() * 1000.0 / 60.0                                  # cm3/s
    return {"push_kN": round(p_bar * a_push / 100.0, 1), "pull_kN": round(p_bar * a_pull / 100.0, 1),
            "out_mm_s": round(q / a_push * 10.0), "in_mm_s": round(q / a_pull * 10.0),
            "stroke_out_s": round(stroke / (q / a_push * 10.0), 1)}


def heat(p_bar=100.0, duty=0.5):
    """Oil temperature rise: losses (shaft power - useful power) heat the oil, the tank loses tank_surface_w_k per K.
    Minutes from ambient to t_max, and the steady temperature at this duty."""
    pw = power(p_bar)
    shaft = pw["elec_kW"] * P.eta_motor
    loss_W = (shaft - pw["hyd_kW"]) * 1000.0 * duty + pw["hyd_kW"] * 1000.0 * duty * 0.3   # 30 % of the work lost in valves
    oil_kg = (P.tank_h - 100.0) / P.tank_h * (P.tank_x[1] - P.tank_x[0]) * (P.tank_y[1] - P.tank_y[0]) * P.tank_h / 1e6 * P.oil_rho
    steady = P.t_ambient + loss_W / P.tank_surface_w_k
    if steady <= P.t_max:
        minutes = None
    else:
        k = P.tank_surface_w_k / (oil_kg * P.oil_cp * 1000.0)
        minutes = round(-math.log(1.0 - (P.t_max - P.t_ambient) * P.tank_surface_w_k / loss_W) / k / 60.0)
    return {"loss_W": round(loss_W), "oil_kg": round(oil_kg, 1), "steady_C": round(steady), "minutes_to_max": minutes}


def axle():
    m = P.MODEL_MASS
    oil_kg = heat()["oil_kg"]
    items = [(P.robot_mass, 0.0, P.robot_cg_z), (m["kg"] + oil_kg, m["cg_y"], m["cg_z"])]
    tot = sum(k for k, _, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y, _ in items) / (2.0 * P.robot_axle_y)
    return {"total_kg": round(tot, 1), "front_kg": round(front, 1), "rear_kg": round(tot - front, 1),
            "rear_share": round((tot - front) / tot, 3)}


def report():
    out = {"flow_lpm": round(flow_lpm(), 1), "power": {p: power(p) for p in P.p_work}, "max_pressure_bar": max_pressure(),
           "cylinders_150bar": {k: cylinder(k) for k in P.cylinders}, "heat_100bar_50pct": heat(100.0, 0.5),
           "heat_150bar_100pct": heat(150.0, 1.0), "axle": axle()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
