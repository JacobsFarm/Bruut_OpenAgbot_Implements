"""Calculations for the pheromone trap service, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B phs_calc.py      (or in FreeCAD: import phs_calc; phs_calc.report())

Image resolution on the sticky card (pixels per insect), time per trap visit, the weekly round (time, energy),
lure capsules per round and revolver refills, actuator and Z-axis loads, axle loads.
"""
import math

import phs_params as P


def image():
    """Card seen by the camera: field of view at cam_dist, pixels per mm and per insect."""
    w = 2 * P.cam_dist * math.tan(math.radians(P.cam_hfov) / 2)
    h = w * P.cam_px[1] / P.cam_px[0]
    px_mm = P.cam_px[0] / w
    fits = w >= P.card[1] * 0.98 and h >= P.card[0] * 0.98
    out = {"view_mm": (round(w), round(h)), "card_fits": fits, "px_per_mm": round(px_mm, 1)}
    out["px_per_insect"] = {k: round(v * px_mm) for k, v in P.insect_mm.items()}
    out["countable"] = {k: v * px_mm >= P.px_per_insect_min for k, v in P.insect_mm.items()}
    return out


def visit(lure=False):
    """Seconds at one trap: align, Z to the drawer, reach out, hook (Z up), pull, photo, (lure), push back, retract."""
    t_z = 300.0 / (P.screw_lead * P.stepper_rpm / 60.0)            # mean Z move 300 mm
    t_reach = P.stroke / P.act_speed
    t_pull = 2 * P.drawer_pull / P.act_speed                       # out and back in
    t_hook = 2 * 15.0 / (P.screw_lead * P.stepper_rpm / 60.0) + 1.0
    t_back = (P.stroke - P.drawer_pull) / P.act_speed
    t = P.t_stop_align + t_z + t_reach + t_hook + t_pull + P.t_photo + t_back + (P.t_lure if lure else 0.0)
    return {"z_s": round(t_z, 1), "reach_s": round(t_reach, 1), "pull_push_s": round(t_pull, 1),
            "total_s": round(t, 1)}


def round_trip():
    """Weekly round of all traps: driving + visits; lure swapped every lure_weeks."""
    share_lure = P.visit_every_days / (P.lure_weeks * 7.0)
    t_visit = visit(False)["total_s"] * (1 - share_lure) + visit(True)["total_s"] * share_lure
    dist = P.traps * P.trap_spacing_m * 1.3                        # route detours ~30 %
    m = P.robot_mass + P.MODEL_MASS["kg"]
    p_drive = m * 9.81 * P.crr * P.speed / P.eta_drive
    t_drive = dist / P.speed
    t_all = t_drive + P.traps * t_visit
    e = (p_drive * t_drive + P.p_sensors * t_all + P.p_act * P.traps * 30.0) / 3600.0
    lures = P.traps * share_lure
    return {"route_km": round(dist / 1000.0, 1), "time_h": round(t_all / 3600.0, 2), "Wh": round(e),
            "battery_share": round(e / P.battery_wh, 2), "lures_per_round": round(lures),
            "revolver_refills_per_round": round(lures / P.revolver_n, 1)}


def loads():
    """Actuator force pulling the drawer; Z stepper torque lifting the carriage + head."""
    m_car = P.MODEL_MASS["carriage_kg"]
    f_z = m_car * P.g + 30.0                                      # + guide friction
    eff = 0.35                                                    # Tr16x4 trapezoidal screw
    torque = f_z * P.screw_lead / (2 * math.pi * eff) / 1000.0
    return {"drawer_N": P.drawer_force, "actuator_reserve": round(P.act_force / P.drawer_force, 1),
            "z_force_N": round(f_z), "z_torque_Nm": round(torque, 2)}


def axle_loads():
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg[1]), (m["kg"], m["cg"][1])]
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2.0 * P.robot_axle_y)
    right = (P.robot_mass * 0.0 + m["kg"] * m["cg"][0]) / total
    left_right = (total / 2 - total * right / (2 * P.robot_wheel_x), total / 2 + total * right / (2 * P.robot_wheel_x))
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "left_right_kg": tuple(round(v, 1) for v in left_right)}


def report():
    out = {"image": image(), "visit": visit(), "visit_with_lure": visit(True), "round": round_trip(),
           "loads": loads(), "axle": axle_loads()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
