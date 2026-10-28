"""Calculations for the inter-row hoe, in pure Python (same parameters as the model).

    import irh_calc
    irh_calc.report()          # prints and returns all key figures

Masses come from build_irh.mass_properties() (copied into irh_params.MODEL_MASS after a rebuild).
"""
import math

import irh_params as P


def coverage():
    """Hoed width per unit and per pass, share of the field that is hoed, area per hour."""
    w = P.unit_width()
    n = len(P.unit_x)
    pass_w = n * P.row_spacing / 1000.0
    return {"unit_width_mm": w, "hoed_share": round(w / P.row_spacing, 3), "pass_width_m": pass_w,
            "ha_per_hour": round(pass_w * P.speed * 3600 / 10000.0 * 0.8, 2)}


def draft():
    """Pull force (N): soil cutting at the shares (k_soil x hoed width x depth) and rolling of robot and gauge wheels,
    against grip and the hub motors. Work: the hoe hangs on the gauge wheels, its weight is not on the robot."""
    m = P.MODEL_MASS
    cut = P.k_soil * len(P.unit_x) * P.unit_width() / 1000.0 * P.work_depth / 1000.0
    on_robot = P.robot_mass + m["mount_kg"] + m["lift_kg"] - m["shift_kg"]
    roll = P.crr * (on_robot + m["shift_kg"]) * P.g
    grip = P.mu_tyre * on_robot * P.g
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    total = cut + roll
    return {"cutting_N": round(cut), "rolling_N": round(roll), "total_N": round(total), "grip_N": round(grip),
            "motor_cont_N": round(motors), "margin": round(min(grip, motors) / total, 2),
            "power_W": round(total * P.speed / P.eta_drive)}


def shift_axis():
    """Side-shift drive: speed the row needs, force on the nut, torque and speed of the stepper."""
    m = P.MODEL_MASS
    need = P.row_wander / 1000.0 / (P.row_wander_len / P.speed) * 1000.0     # mm/s to follow a wandering row
    design = 4.0 * need                                                       # margin for steering corrections
    rpm = design / P.screw_lead * 60.0
    side = P.side_factor * P.k_soil * len(P.unit_x) * P.unit_width() / 1000.0 * P.work_depth / 1000.0
    accel = m["shift_kg"] * 1.0                                                # 1 m/s2
    force = side + accel + 0.01 * m["shift_kg"] * P.g                          # + rail friction
    torque = force * P.screw_lead / 1000.0 / (2 * math.pi * P.eta_screw)
    return {"needed_mm_s": round(need, 1), "design_mm_s": round(design), "motor_rpm": round(rpm),
            "nut_force_N": round(force), "torque_Nm": round(torque, 2), "motor_Nm_at_600rpm": P.motor_torque[1],
            "torque_margin": round(P.motor_torque[1] / torque, 1),
            "stroke_time_s": round(2 * P.shift_stroke / design, 2)}


def guidance():
    """Error budget: the band next to the row must take the guidance error, the camera latency and the lag of the
    shift axis. Look-ahead: distance from the camera view to the shares."""
    lat_err = P.row_wander / (P.row_wander_len * 1000.0) * P.speed * 1000.0 * P.cam_latency   # mm drift in latency
    err = math.sqrt(P.row_error_cam ** 2 + lat_err ** 2)
    err_rtk = math.sqrt(P.row_error_rtk ** 2 + lat_err ** 2)
    zc = P.mast_z[1] + 6.0 + 50.0
    view_y = P.mast_y[0] - 30.0 - zc / math.tan(math.radians(P.cam_tilt))
    half = math.radians(P.cam_hfov / 2.0)
    width = 2.0 * zc / math.sin(math.radians(P.cam_tilt)) * math.tan(half)
    return {"band_mm": P.row_band, "camera_error_mm": round(err, 1), "rtk_error_mm": round(err_rtk, 1),
            "band_over_camera": round(P.row_band / err, 1), "band_over_rtk": round(P.row_band / err_rtk, 1),
            "view_centre_y": round(view_y), "view_width_mm": round(width),
            "rows_in_view": 1 + 2 * int(width / 2.0 // P.row_spacing)}


def actuator():
    """Lift actuator force: lift group moment about the pivot over the lever of the actuator (work and transport)."""
    m = P.MODEL_MASS
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        r = P.rotate_yz(P.act_rod, lift)
        uy, uz = r[0] - P.act_base[0], r[1] - P.act_base[1]
        L = math.hypot(uy, uz)
        lever = abs((r[0] - P.pivot[0]) * uz / L - (r[1] - P.pivot[1]) * uy / L)
        cg = P.rotate_yz((m["lift_cg_y"], m["lift_cg_z"]), lift)
        moment = m["lift_kg"] * P.g * abs(cg[0] - P.pivot[0]) / 1000.0
        out["lift_%g" % lift] = {"length": round(L, 1), "lever_mm": round(lever, 1), "moment_Nm": round(moment),
                                 "force_N": round(moment / lever * 1000.0)}
    lens = [P.act_length(x) for x in P.LIFT_POSES]
    out["length_range"] = (round(min(lens), 1), round(max(lens), 1))
    out["fits_stroke"] = P.act_retracted <= min(lens) and max(lens) <= P.act_retracted + P.act_stroke
    out["lift_time_s"] = round((max(lens) - min(lens)) / P.act_speed, 1)
    return out


def axle_loads(ballast=True):
    """Load (kg) on the front and rear axle, hoe lifted (transport), with or without the front counterweight."""
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["lift_kg"], m["lift_cg_y"])]
    if ballast:
        items.append((P.ballast_kg, P.ballast_cg_y))
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3)}


def report():
    out = {"coverage": coverage(), "draft": draft(), "shift_axis": shift_axis(), "guidance": guidance(),
           "actuator": actuator(), "axle_transport": axle_loads(), "axle_transport_no_ballast": axle_loads(False)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
