"""Calculations for the parallel hitch, in pure Python (same parameters as the model).

    import tpp_calc
    tpp_calc.report()

Masses come from build_tpp.mass_properties() (copied into tpp_params.MODEL_MASS after a rebuild).
"""
import math

import tpp_params as P
import tpa_params as Q
import tph_params as TP


def linkage_table():
    out = {}
    for th in P.THETA_POSES:
        d = P.shift(th)
        out[th] = {"carrier_dy": round(d[0], 1), "carrier_dz": round(d[1], 1), "act_len": round(P.act_length(th), 1),
                   "lower_pin_z": round(P.cp_base[1] + d[1])}
    out["lift_mm"] = round(P.shift(P.theta_lift)[1])
    return out


def float_range():
    lw = P.act_work_length()
    lo, hi = P.float_limits(lw)
    return {"act_work_length": round(lw, 1), "slot_mm": round(P.float_slot(), 1), "theta": (round(lo, 2), round(hi, 2)),
            "carrier_mm": (round(P.shift(lo)[1]), round(P.shift(hi)[1]))}


def _items(imp_kg=None):
    m = P.MODEL_MASS
    items = [(m["carrier_kg"], 1.0), (m["links_kg"], 0.5)]       # links: their cg moves half as much
    if imp_kg is None:
        items.append((m["imp_kg"], 1.0))
    elif imp_kg > 0:
        items.append((imp_kg, 1.0))
    return items


def actuator(imp_kg=None):
    """Pull in the LA36 (N) by virtual work over the lift (the carrier translates: dz the same for every point)."""
    h = 0.25
    out = {}
    worst = 0.0
    for th in (P.theta_work, -4.0, 8.0, 18.0, P.theta_lift):
        dz = P.shift(th + h)[1] - P.shift(th - h)[1]
        dl = abs(P.act_length(th + h) - P.act_length(th - h))
        f = sum(k * w for k, w in _items(imp_kg)) * P.g * dz / dl
        worst = max(worst, f)
        out["theta_%g" % th] = round(f)
    lw, lt = P.act_work_length(), P.act_length(P.theta_lift)
    out["work_length"] = round(lw, 1)
    out["lifted_length"] = round(lt, 1)
    out["fits_stroke"] = P.act_retracted <= lt and lw <= P.act_extended
    out["margin_retracted_mm"] = round(lt - P.act_retracted, 1)
    out["margin_extended_mm"] = round(P.act_extended - lw, 1)
    v = Q.act_speed(worst, P.act_variant)
    out["speed_mm_s"] = round(v, 1)
    out["lift_time_s"] = round((lw - lt) / v, 1)
    out["current_A"] = round(Q.act_current(worst, P.act_variant), 1)
    out["max_N"] = round(worst)
    out["load_ratio"] = round(worst / Q.LA36_24V[P.act_variant][0], 2)
    out["capacity_kg"] = round((Q.LA36_24V[P.act_variant][0] / worst) * sum(k * w for k, w in _items(imp_kg))
                               - P.MODEL_MASS["carrier_kg"] - 0.5 * P.MODEL_MASS["links_kg"])
    return out


def axle_loads(imp_kg=None, imp_cg_y=None, ballast=True, theta=None):
    m = P.MODEL_MASS
    th = P.theta_lift if theta is None else theta
    dy = P.shift(th)[0]
    imp_kg = m["imp_kg"] if imp_kg is None else imp_kg
    if imp_cg_y is None:
        imp_cg_y = m["imp_cg"][0] + dy
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["act_kg"], -1000.0),
             (m["links_kg"], -1000.0), (m["carrier_kg"], m["carrier_cg"][0] + dy), (imp_kg, imp_cg_y)]
    if ballast:
        items.append((P.ballast_kg, P.ballast_cg_y))
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3)}


def capacity():
    y = P.cp_base[0] + P.shift(P.theta_lift)[0] - P.imp_cg_behind
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
    m = P.MODEL_MASS
    tines = len(TP.tine_x) * TP.k_tine * TP.share_w / 1000.0 * TP.work_depth / 1000.0
    on_robot = P.robot_mass + m["mount_kg"] + m["links_kg"] + m["act_kg"] + P.ballast_kg
    roll = TP.crr * (on_robot + m["imp_kg"] + m["carrier_kg"]) * P.g
    grip = TP.mu_tyre * on_robot * P.g
    motors = TP.n_driven * TP.hub_torque_nom / TP.r_load
    total = tines + roll
    return {"tines_N": round(tines), "rolling_N": round(roll), "total_N": round(total), "grip_N": round(grip),
            "margin": round(min(grip, motors) / total, 2)}


def report():
    out = {"linkage": linkage_table(), "float": float_range(), "actuator": actuator(),
           "actuator_empty": actuator(imp_kg=0), "capacity_kg": capacity(), "axle_lifted": axle_loads(),
           "axle_lifted_no_ballast": axle_loads(ballast=False), "cultivator": draft(),
           "act_mass_kg": round(P.act_mass(), 2)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
