"""Calculations for the fresh grass harvester, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B fgh_calc.py      (or in FreeCAD: import fgh_calc; fgh_calc.report())

Load per trip, mowing distance and time per load, trip cycle, energy per trip and trips per charge, cows fed per
charge, axle loads (empty / full / tipped) and the side tip angle.
"""
import math

import fgh_params as P


def load():
    x0, x1 = P.box_x
    y0, y1 = P.box_y
    z0, z1 = P.box_z
    v = (x1 - x0) * (y1 - y0) * (z1 - z0) / 1e9
    kg = v * P.fill * P.grass_density
    fresh_kg_m2 = P.yield_dm_t_ha * 1000.0 / 1e4 / P.dm_share
    w = (P.bar_x[1] - P.bar_x[0]) / 1000.0
    area = kg / fresh_kg_m2
    return {"container_m3": round(v, 3), "load_kg": round(kg, 1), "fresh_kg_m2": round(fresh_kg_m2, 2),
            "area_m2": round(area), "strip_m": round(area / w)}


def trip():
    ld = load()
    t_mow = ld["strip_m"] / P.mow_speed
    t_road = 2 * P.distance_m / P.road_speed
    t = t_mow + t_road + P.unload_min * 60.0
    w = (P.bar_x[1] - P.bar_x[0]) / 1000.0
    p_mow = w * P.bar_w_per_m + P.auger_w + P.elevator_w + P.drive_w + P.electronics_w
    p_road = P.drive_w + P.electronics_w
    e = (p_mow * t_mow + p_road * (t_road + P.unload_min * 60.0)) / 3600.0
    n = P.robot_battery_kwh * 1000.0 * 0.85 / e
    return {"mow_s": round(t_mow), "trip_min": round(t / 60.0, 1), "mow_W": round(p_mow), "Wh_per_trip": round(e),
            "trips_per_charge": round(n, 1), "kg_per_charge": round(n * ld["load_kg"]),
            "cows_per_charge": round(n * ld["load_kg"] / P.cow_kg_day, 1),
            "hours_per_charge": round(n * t / 3600.0, 1)}


def axle_loads(full=True):
    m = P.MODEL_MASS
    ms = [(P.robot_kg, P.robot_cg), (m["total_kg"], m["cg"])]
    if full:
        x0, x1 = P.box_x
        y0, y1 = P.box_y
        z0, z1 = P.box_z
        ms.append((load()["load_kg"], (0.5 * (x0 + x1), 0.5 * (y0 + y1), z0 + 0.45 * (z1 - z0))))
    tot = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / tot for i in range(3))
    front = tot * (cg[1] + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    right = (cg[0] + P.robot_wheel_x) / (2.0 * P.robot_wheel_x)
    return {"total_kg": round(tot, 1), "cg": tuple(round(c) for c in cg), "front_share": round(front / tot, 3),
            "front_right_kg": round(front * right, 1), "rear_left_kg": round((tot - front) * (1 - right), 1),
            "tip_right_deg": round(math.degrees(math.atan((P.robot_wheel_x - cg[0]) / cg[2])), 1)}


def report():
    out = {"load": load(), "trip": trip(), "axle_empty": axle_loads(False), "axle_full": axle_loads(True)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
