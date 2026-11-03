"""Calculations for the soil moisture sensor placer, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B smp_calc.py      (or in FreeCAD: import smp_calc; smp_calc.report())

Push force per soil state against the ball screw and the robot weight, pull-out force, cycle time per sensor, points
per trip and per hour, sensor battery life, radio range.
"""
import math

import smp_params as P


def push_force(soil):
    """Force (N) to push the sensor stem to full depth: cone resistance on the tip area + side friction on the stem."""
    d = P.stem[0] / 1000.0
    depth = P.stem[1] / 1000.0
    tip = P.q_c[soil] * math.pi / 4.0 * d * d
    side = P.f_s * math.pi * d * depth
    return tip + side, side


def screw_force():
    """Axial force (N) of the ball screw at the motor torque."""
    return 2.0 * math.pi * P.motor_torque * P.ball_eta / (P.screw_lead / 1000.0)


def weight_force():
    """Usable share of the robot and placer weight (the wheels must stay loaded)."""
    return (P.robot_mass + P.MODEL_MASS["total_kg"]) * P.g * P.weight_use


def push():
    out = {}
    lim = min(screw_force(), weight_force())
    for soil in P.q_c:
        f, side = push_force(soil)
        out[soil] = {"push_N": round(f), "pull_out_N": round(side), "ok": f <= lim}
    out["screw_N"] = round(screw_force())
    out["weight_N"] = round(weight_force())
    return out


def cycle():
    """Time (s) to place one sensor: settle, Z park -> pick -> lift, star half turn, push to depth, release, back up."""
    v_fast = P.motor_rpm / 60.0 * P.screw_lead          # mm/s
    t = P.t_settle
    t += (P.c_park - P.c_pick) / v_fast + (P.c_lift - P.c_pick) / v_fast + 1.0       # down, grip, lift
    t += P.t_mag
    free = P.c_lift - P.c_for_cap_bottom(P.stem[1])     # down to the tip on the ground
    t += free / v_fast + P.stem[1] / P.push_speed + 1.0   # push slowly, release
    t += (P.c_park - P.c_plant) / v_fast
    t += P.t_mag                                        # star to the next sensor
    return {"z_speed_mm_s": round(v_fast), "place_s": round(t, 1), "pick_up_s": round(t, 1)}


def trip():
    """Sensors per magazine and the time for a field at points_per_ha (driving between the points at speed)."""
    spacing = math.sqrt(1e4 / P.points_per_ha)          # m between points on a square grid
    t_point = cycle()["place_s"] + spacing / P.speed
    return {"per_trip": P.n_sensors, "ha_per_trip": round(P.n_sensors / P.points_per_ha, 1),
            "spacing_m": round(spacing), "s_per_point": round(t_point), "points_per_h": round(3600.0 / t_point)}


def battery_life():
    """Sensor battery life (years): sleep, measuring every read_interval_min, a few transmissions per day."""
    per_day_mas = (P.sleep_ua / 1000.0) * 86400.0
    per_day_mas += (1440.0 / P.read_interval_min) * P.active_ma * P.active_s
    per_day_mas += P.tx_per_day * P.tx_ma * P.tx_s
    mah_day = per_day_mas / 3600.0
    years = P.battery_mah / mah_day / 365.0
    return {"mAh_per_day": round(mah_day, 2), "years_by_use": round(years, 1),
            "years": round(min(years, P.shelf_years), 1)}


def report():
    out = {"push": push(), "cycle": cycle(), "trip": trip(), "battery": battery_life(),
           "poses_carriage_bottom": {"park": P.c_park, "pick": P.c_pick, "lift": P.c_lift, "plant": P.c_plant},
           "mass_kg": P.MODEL_MASS["total_kg"]}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
