"""Calculations for the A-frame hitch with the LA36 as top link, in pure Python (same parameters as the model).

    import tpa_calc
    tpa_calc.report()          # prints and returns all key figures

Masses come from build_tpa.mass_properties() (copied into tpa_params.MODEL_MASS after a rebuild).
"""
import math

import tpa_params as P
import tph_params as TP


def _cg(lift, cg):
    return P.rotate_yz(cg, lift)


def float_range():
    """Frame angles (deg) between which the rod pin floats in the slot with the LA36 at its work length, and the
    travel of the lower pins and the gauge wheels."""
    L = P.act_work_length()
    lo = P.lift_for_length(L)                       # frame down: pin at the slot end, the LA36 carries
    a, b = -10.0, 30.0
    for _ in range(60):                             # frame up: pin at the far end of the slot
        mid = (a + b) / 2.0
        d, u = P.act_d(mid), P.slot_dir(mid)
        e = (d[0] + P.float_slot * u[0], d[1] + P.float_slot * u[1])
        if math.hypot(e[0] - P.act_c[0], e[1] - P.act_c[1]) > L:
            a = mid
        else:
            b = mid
    hi = (a + b) / 2.0
    wy, wz = TP.wheel_y + P.cult_dy, TP.wheel_d / 2.0
    return {"act_work_length": round(L, 1), "deg": (round(lo, 2), round(hi, 2)),
            "lower_pin_mm": (round(P.lower_pin(lo)[1] - P.lower_b[1]), round(P.lower_pin(hi)[1] - P.lower_b[1])),
            "gauge_wheel_mm": (round(P.rotate_yz((wy, wz), lo)[1] - wz), round(P.rotate_yz((wy, wz), hi)[1] - wz))}


def linkage_table():
    out = {}
    for lift in P.LIFT_POSES:
        d = P.act_d(lift)
        out[lift] = {"lower_pin_z": round(P.lower_pin(lift)[1]), "act_len": round(P.act_length(lift), 1),
                     "apex_pin": (round(d[0]), round(d[1])), "pitch_deg": round(lift, 1)}
    out["lift_range_mm"] = round(P.lower_pin(P.lift_transport)[1] - P.lower_b[1])
    return out


def moving_loads(imp_kg=None, imp_cg=None):
    m = P.MODEL_MASS
    items = [(m["frame_kg"], m["frame_cg"])]
    if imp_kg is None:
        items.append((m["imp_kg"], m["imp_cg"]))
    elif imp_kg > 0:
        items.append((imp_kg, imp_cg))
    return items


def actuator(imp_kg=None, imp_cg=None):
    """Pull in the LA36 (N) over the lift by virtual work: sum m g dz_cg = F dL; stroke check, speed, time, current."""
    items = moving_loads(imp_kg, imp_cg)
    h = 0.25
    out = {}
    worst = 0.0
    for lift in P.LIFT_POSES[1:]:
        dz = sum(k * P.g * (_cg(lift + h, c)[1] - _cg(lift - h, c)[1]) for k, c in items)
        dl = abs(P.act_length(lift + h) - P.act_length(lift - h))
        f = dz / dl
        worst = max(worst, f)
        out["lift_%g" % lift] = round(f)
    L_w, L_t = P.act_work_length(), P.act_length(P.lift_transport)
    out["work_length"] = round(L_w, 1)
    out["transport_length"] = round(L_t, 1)
    out["fits_stroke"] = (P.act_retracted <= L_t) and (L_w <= P.act_extended)
    out["margin_retracted_mm"] = round(L_t - P.act_retracted, 1)
    out["margin_extended_mm"] = round(P.act_extended - L_w, 1)
    v = P.act_speed(worst)
    out["speed_mm_s"] = round(v, 1)
    out["lift_time_s"] = round((L_w - L_t) / v, 1)
    out["current_A"] = round(P.act_current(worst), 1)
    out["max_N"] = round(worst)
    out["load_ratio"] = round(worst / P.LA36_24V[P.act_variant][0], 2)
    arm = _arm(P.lift_work)
    out["lever_arm_mm"] = (round(arm), round(_arm(P.lift_transport)))
    out["capacity_kg_at_cg"] = round(P.LA36_24V[P.act_variant][0] * min(arm, _arm(P.lift_transport)) /
                                     (P.g * abs(P.MODEL_MASS["imp_cg"][0] - P.lower_a[0])) -
                                     P.MODEL_MASS["frame_kg"] * 0.6)
    return out


def _arm(lift):
    """Lever arm (mm) of the LA36 about the pivots."""
    d = P.act_d(lift)
    c = P.act_c
    uy, uz = c[0] - d[0], c[1] - d[1]
    n = math.hypot(uy, uz)
    ay, az = P.lower_a[0] - d[0], P.lower_a[1] - d[1]
    return abs(ay * uz / n - az * uy / n)


def axle_loads(imp_kg=None, imp_cg_y=None, ballast=True, lift=None):
    """Load (kg) on the front and rear axle with the implement lifted (transport)."""
    m = P.MODEL_MASS
    lift = P.lift_transport if lift is None else lift
    imp_kg = m["imp_kg"] if imp_kg is None else imp_kg
    if imp_cg_y is None:
        imp_cg_y = _cg(lift, m["imp_cg"])[0]
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["act_kg"], -1000.0),
             (m["frame_kg"], _cg(lift, m["frame_cg"])[0]), (imp_kg, imp_cg_y)]
    if ballast:
        items.append((P.ballast_kg, P.ballast_cg_y))
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3)}


def capacity():
    """Heaviest implement the robot can carry lifted with front_share_min on the front axle (with and without the
    2 x 20 kg front counterweight), its cg imp_cg_behind behind the lower pins."""
    y = P.lower_pin(P.lift_transport)[0] - P.imp_cg_behind
    out = {}
    for ballast in (False, True):
        lo, hi = 0.0, 400.0
        for _ in range(40):
            mid = (lo + hi) / 2.0
            if axle_loads(mid, y, ballast)["front_share"] >= P.front_share_min:
                lo = mid
            else:
                hi = mid
        out["with_ballast" if ballast else "no_ballast"] = round(lo)
    return out


def draft():
    """Pull of the cultivator (as three point hitch/simple): shares and rolling of the robot."""
    m = P.MODEL_MASS
    tines = len(TP.tine_x) * TP.k_tine * TP.share_w / 1000.0 * TP.work_depth / 1000.0
    on_robot = P.robot_mass + m["mount_kg"] + m["frame_kg"] + m["act_kg"] + P.ballast_kg
    roll = TP.crr * (on_robot + m["imp_kg"]) * P.g
    grip = TP.mu_tyre * on_robot * P.g
    motors = TP.n_driven * TP.hub_torque_nom / TP.r_load
    total = tines + roll
    return {"tines_N": round(tines), "rolling_N": round(roll), "total_N": round(total), "grip_N": round(grip),
            "margin": round(min(grip, motors) / total, 2)}


def report():
    out = {"linkage": linkage_table(), "float": float_range(), "actuator": actuator(),
           "actuator_empty": actuator(imp_kg=0), "capacity_kg": capacity(),
           "axle_transport": axle_loads(), "axle_transport_no_ballast": axle_loads(ballast=False),
           "cultivator": draft(), "brace_len": round(P.brace_len(), 1), "act_mass_kg": round(P.act_mass(), 2)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
