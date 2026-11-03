"""Calculations for the laser weeder, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B lzw_calc.py      (or in FreeCAD: import lzw_calc; lzw_calc.report())

Scan field per head, energy and time per weed, laser use and the highest speed, time a weed stays in the scan field,
electric power, capacity per hour and per charge, axle loads.
"""
import math

import lzw_params as P

D = P.D
ROBOT_CG = (0.0, 95.0, 543.0)


def lens_z():
    return D.hood_top - D.hood_t - P.head_box[2] - P.lens[1]


def scan_field():
    h = lens_z()
    half = h * math.tan(math.radians(P.scan_half_deg))
    return {"lens_z": round(h), "field_mm": round(2 * half), "covers_half_bed": 2 * half >= P.work_width / 2.0,
            "y_range": (round(P.head_y - half), round(P.head_y + half))}


def per_weed():
    """Mean energy and firing time per weed (mix of sizes), incl. the galvo jump."""
    e = sum(j * s for j, s in zip(P.kill_j, P.weed_mix))
    t = e / P.laser_w + P.retarget_ms / 1000.0
    return {"mean_J": round(e, 1), "time_s": round(t, 3), "fluence_J_mm2": round(e / (math.pi / 4 * P.spot_mm ** 2), 1)}


def throughput(v=P.speed):
    """Weeds per second per head, laser duty, highest speed (duty 1), time in the scan field."""
    per_head = P.weed_density * (P.work_width / 2.0 / 1000.0) * v
    t = per_weed()["time_s"]
    duty = per_head * t
    v_max = v / duty
    window = scan_field()["field_mm"] / (v * 1000.0)
    return {"weeds_s_per_head": round(per_head, 2), "laser_duty": round(duty, 2), "ok": duty <= 0.8,
            "v_max_m_s": round(v_max, 2), "seconds_in_field": round(window, 1)}


def power(v=P.speed):
    duty = min(1.0, throughput(v)["laser_duty"])
    laser = 2 * P.laser_w / P.laser_eff * duty
    total = laser + P.cooling_w + P.drive_w + P.computer_w + P.led_w + 20.0      # 20 W galvos idle
    hours = P.battery_wh / total
    m2_h = P.work_width / 1000.0 * v * 3600.0 * P.field_eff
    return {"laser_W": round(laser), "total_W": round(total), "hours": round(hours, 1), "m2_h": round(m2_h),
            "m2_per_charge": round(m2_h * hours), "bed_m_per_charge": round(v * 3600.0 * P.field_eff * hours)}


def axle_loads():
    m = P.MODEL_MASS
    items = [(P.robot_kg, ROBOT_CG[1]), (m["total_kg"], m["cg_y"])]
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2.0 * P.robot_axle_y)
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1)}


def report():
    out = {"scan_field": scan_field(), "per_weed": per_weed(), "throughput": throughput(), "power": power(),
           "axle": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
