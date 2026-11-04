"""Calculations for the charging robot, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B chg_calc.py      (or in FreeCAD: import chg_calc; chg_calc.report())

Energy on board, charge per working robot (time, losses), number of charges per trip, extra working hours per day
compared with driving back to the shed, own driving energy, recharge at the shed, axle and tyre loads.
"""
import math

import chg_params as P


def energy():
    usable = P.pods_n * P.pod_wh * P.pod_dod
    return {"pods_kWh": round(P.pods_n * P.pod_wh / 1000.0, 2), "usable_kWh": round(usable / 1000.0, 2),
            "pods_kg": round(P.pods_n * (P.B.cells_n * P.B.cell_kg + P.B.bms_kg + 4.0), 1)}


def _total_kg():
    return P.robot_mass + P.MODEL_MASS["kg"]


def drive_wh_per_km():
    return _total_kg() * P.g * P.crr * 1000.0 / P.eta_drive / 3600.0


def charge():
    """One charge of the working robot from 20 to 100 %: energy, time (CC + slower CV tail), losses."""
    need = P.robot_battery_wh * (P.work_soc[1] - P.work_soc[0])
    i = P.dcdc_w / P.v_charge
    loss_contact = i ** 2 * P.contact_r
    t_cc = need * (1 - P.cv_share) / P.dcdc_w
    t_cv = need * P.cv_share / (P.dcdc_w * 0.4)
    from_pods = need / P.dcdc_eff + loss_contact * (t_cc + t_cv)
    return {"need_Wh": round(need), "current_A": round(i, 1), "contact_loss_W": round(loss_contact, 1),
            "time_min": round((t_cc + t_cv) * 60 + P.dock_s / 60.0), "from_pods_Wh": round(from_pods)}


def trip():
    """Charges per trip: usable energy minus the drive to the field and back."""
    e = energy()["usable_kWh"] * 1000.0
    own = drive_wh_per_km() * 2 * P.shed_km
    n = (e - own) / charge()["from_pods_Wh"]
    return {"own_drive_Wh": round(own), "charges_per_trip": round(n, 1),
            "shed_recharge_h": round(e / P.shed_charger_w / 0.92, 1)}


def workday():
    """Hours of work per day for a working robot: alone (back to the shed to charge) versus with the charger."""
    out = {}
    c = charge()
    t_shed = 2 * P.shed_km * 1000.0 / P.speed / 3600.0
    for k, w in P.work_loads_w.items():
        run = P.robot_battery_wh * (P.work_soc[1] - P.work_soc[0]) / w
        alone = 24.0 * run / (run + t_shed + c["time_min"] / 60.0 + 0.5)    # 0.5 h shed charging overhead
        with_c = 24.0 * run / (run + c["time_min"] / 60.0 + 0.1)
        out[k] = {"run_h": round(run, 1), "per_day_alone_h": round(alone, 1), "per_day_with_charger_h": round(with_c, 1),
                  "charges_per_day": round(24.0 / (run + c["time_min"] / 60.0 + 0.1), 1),
                  "charger_trips_per_day": round(24.0 / (run + c["time_min"] / 60.0 + 0.1) / trip()["charges_per_trip"], 1)}
    return out


def axle_loads():
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg[1]), (m["kg"], m["cg"][1])]
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2.0 * P.robot_axle_y)
    cg_z = (P.robot_mass * P.robot_cg[2] + m["kg"] * m["cg"][2]) / total
    tyre = max(front, total - front) / 2.0
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "max_tyre_kg": round(tyre, 1), "tyre_reserve": round(P.tyre_rating_kg / tyre, 2), "cg_z_mm": round(cg_z),
            "side_tilt_limit_deg": round(math.degrees(math.atan(P.robot_wheel_x / cg_z))),
            "drive_Wh_per_km": round(drive_wh_per_km())}


def report():
    out = {"energy": energy(), "charge": charge(), "trip": trip(), "workday": workday(), "axle": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
