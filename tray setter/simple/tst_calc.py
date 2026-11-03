"""Calculations for the tray setter, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B tst_calc.py      (or in FreeCAD: import tst_calc; tst_calc.report())

Pick-and-drop cycle of the gantry against the planting rate, the highest speed it allows, plants and bed length per
hour and per set of trays, draft of the shoes, battery, axle loads.
"""
import math

import tst_params as P


def move_time(dist, v=P.v_xy, a=P.a_xy):
    """Time (s) for a point-to-point move with a trapezoid (or triangle) speed profile."""
    d_acc = v * v / a
    if dist <= d_acc:
        return 2.0 * math.sqrt(dist / a)
    return 2.0 * v / a + (dist - d_acc) / v


def cycle(tray_i=0, a=0, b=None, row=0):
    """One plant: down into the plug, grip, up, travel to the funnel of the row, release, travel back."""
    b = P.tray_cells[1] - 1 if b is None else b
    cx, cy = P.cell_xy(tray_i, a, b)
    fx, fy = P.row_x[row], P.funnel_y
    d = math.hypot(fx - cx, fy - cy)
    z = P.carry_lift / P.v_z
    t = 2 * z + 2 * P.t_grip + 2 * move_time(d)
    return round(t, 2), round(d)


def worst_cycle():
    """The far cell (rear corner of the other tray) to the farthest funnel."""
    return cycle(1, P.tray_cells[0] - 1, 0, 0)


def rates():
    """Plants per second the 2 rows need at the speed; the cycle the gantry has per plant; the highest speed."""
    need = 2 * P.speed * 1000.0 / P.spacing                      # plants / s
    t_avail = 1.0 / need
    v_max = P.spacing / 2.0 / worst_cycle()[0] / 1000.0           # every cycle may be the far one
    return {"plants_s": round(need, 2), "t_avail_s": round(t_avail, 2), "t_cycle_near_s": cycle()[0],
            "t_cycle_far_s": worst_cycle()[0], "ok": worst_cycle()[0] <= t_avail, "v_max_m_s": round(v_max, 3)}


def capacity():
    plants = 2 * P.tray_cells[0] * P.tray_cells[1]
    per_h = 2 * P.speed * 3600.0 * 1000.0 / P.spacing * P.field_eff
    t_trays = plants / (2 * P.speed * 1000.0 / P.spacing)
    bed_m = plants / 2 * P.spacing / 1000.0
    return {"plants_per_set": plants, "bed_m_per_set": round(bed_m, 1), "minutes_per_set": round(t_trays / 60.0, 1),
            "plants_per_h": round(per_h * t_trays / (t_trays + P.tray_change_s)),
            "bed_m_per_h": round(P.speed * 3600.0 * P.field_eff * t_trays / (t_trays + P.tray_change_s))}


def draft():
    shoes = 2 * P.draft_n_per_shoe
    w = P.drive_w + P.gantry_w
    h = P.battery_kwh * 1000.0 / w
    return {"draft_N": shoes, "power_W": w, "hours": round(h, 1),
            "plants_per_charge": round(h * capacity()["plants_per_h"])}


def axle_loads():
    m = P.MODEL_MASS
    items = [(P.robot_kg, P.robot_cg[1]), (m["total_kg"], m["cg_y"])]
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2.0 * P.robot_axle_y)
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1)}


def report():
    out = {"cycle_near": cycle(), "cycle_far": worst_cycle(), "rates": rates(), "capacity": capacity(),
           "draft_power": draft(), "axle": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
