"""Calculations for the feed mixer wagon, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B fmw_calc.py      (or in FreeCAD: import fmw_calc; fmw_calc.report())

Bin volume and feed load, mixing power, auger torque, energy per batch and batches per charge, animals fed per batch,
axle and wheel loads with a full bin, centre of gravity height and side tip angle, load cell capacity.
"""
import math

import fmw_params as P


def volume():
    r0, r1, h = P.bin_r[0] / 1000.0, P.bin_r[1] / 1000.0, P.bin_h / 1000.0
    v = math.pi * h / 3.0 * (r0 * r0 + r0 * r1 + r1 * r1)
    load = v * P.fill * P.feed_density
    return {"bin_m3": round(v, 3), "load_kg": round(load, 1)}


def mixing():
    v = volume()["bin_m3"] * P.fill
    p = P.mix_kw_per_m3 * v * 1000.0
    w = P.auger_rpm * 2 * math.pi / 60.0
    t = p / w
    return {"mix_W": round(p), "motor_load": round(p / P.gear_eff / P.motor_w, 2), "auger_Nm": round(t),
            "motor_Nm": round(t / P.gear_ratio / P.gear_eff, 1), "motor_rpm_needed": round(P.auger_rpm * P.gear_ratio)}


def batch():
    mx = mixing()
    p_mix = mx["mix_W"] / P.gear_eff
    e_mix = p_mix * P.mix_min / 60.0
    e_dis = 0.6 * p_mix * P.discharge_min / 60.0 + P.drive_w * P.discharge_min / 60.0
    e_drive = (P.drive_w + P.electronics_w) * P.trip_min / 60.0
    e = e_mix + e_dis + e_drive
    n = P.robot_battery_kwh * 1000.0 * 0.85 / e
    load = volume()["load_kg"]
    return {"Wh_per_batch": round(e), "batches_per_charge": round(n, 1), "kg_per_charge": round(n * load),
            "cows_per_charge": round(n * load / P.ration_cow_kg, 1), "calves_per_charge": round(n * load / P.ration_calf_kg),
            "min_per_batch": P.mix_min + P.discharge_min + P.trip_min}


def axle_loads(full=True):
    m = P.MODEL_MASS
    ms = [(P.robot_kg, P.robot_cg), (m["total_kg"], m["cg"])]
    if full:
        load = volume()["load_kg"]
        h = P.bin_h * P.fill
        ms.append((load, (P.bin_c[0], P.bin_c[1], P.bin_z0 + 0.45 * h)))
    tot = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / tot for i in range(3))
    front = tot * (cg[1] + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    arm = P.robot_wheel_x - abs(cg[0])
    return {"total_kg": round(tot, 1), "cg": tuple(round(c) for c in cg), "front_share": round(front / tot, 3),
            "wheel_max_kg": round(max(front, tot - front) / 2.0, 1),
            "tip_side_deg": round(math.degrees(math.atan(arm / cg[2])), 1)}


def load_cells():
    m = P.MODEL_MASS.get("bin_kg", 0.0) + volume()["load_kg"]
    per = m / 4.0
    return {"weighed_kg": round(m, 1), "per_cell_kg": round(per, 1), "cell_rating_kg": 300,
            "factor_bump_x2": round(300 / (2 * per), 2)}


def report():
    out = {"volume": volume(), "mixing": mixing(), "batch": batch(), "axle_full": axle_loads(True),
           "axle_empty": axle_loads(False), "load_cells": load_cells()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
