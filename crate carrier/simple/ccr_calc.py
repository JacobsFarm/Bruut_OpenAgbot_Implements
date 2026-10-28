"""Calculations for the crate carrier, in pure Python (same parameters as the model).

    import ccr_calc
    ccr_calc.report()          # prints and returns all key figures

Masses come from build_ccr.mass_properties() (copied into ccr_params.MODEL_MASS after a rebuild).
"""
import math

import ccr_params as P


def n_crates():
    return 4 * P.crate_layers


def payload(crop):
    """Mass (kg) of the load: crates with their net content."""
    return n_crates() * (P.crate_empty_kg + P.CROPS[crop])


def combined(crop):
    """Total mass and centre of gravity (y, z) of robot + deck + loaded crates."""
    m = P.MODEL_MASS
    items = [(P.robot_mass, (P.robot_cg_y, P.robot_cg_z)), (m["deck_kg"], m["deck_cg"][1:]),
             (payload(crop), m["crates_cg"][1:])]
    tot = sum(k for k, _ in items)
    y = sum(k * c[0] for k, c in items) / tot
    z = sum(k * c[1] for k, c in items) / tot
    return tot, y, z


def axle_loads(crop):
    tot, y, _ = combined(crop)
    front = tot * (y + P.wheelbase_half) / (2 * P.wheelbase_half)
    return {"front_kg": round(front, 1), "rear_kg": round(tot - front, 1), "front_share": round(front / tot, 3)}


def stability(crop):
    """Static tip angles (deg): sideways over the wheel line and lengthways (front / rear) over the axles."""
    tot, y, z = combined(crop)
    side = math.degrees(math.atan(P.track_half / z))
    fwd = math.degrees(math.atan((P.wheelbase_half - y) / z))
    back = math.degrees(math.atan((P.wheelbase_half + y) / z))
    return {"cg_z": round(z), "cg_y": round(y), "side_deg": round(side, 1), "forward_deg": round(fwd, 1),
            "backward_deg": round(back, 1)}


def slope_pull(crop, slope_deg=10.0):
    """Drive force (N) for rolling plus climbing a slope, against grip and the hub motors."""
    tot, _, _ = combined(crop)
    a = math.radians(slope_deg)
    need = tot * P.g * (P.crr * math.cos(a) + math.sin(a))
    grip = P.mu_tyre * tot * P.g * math.cos(a)
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    return {"slope_deg": slope_deg, "need_N": round(need), "grip_N": round(grip), "motor_cont_N": round(motors),
            "margin": round(min(grip, motors) / need, 2)}


def shuttle(crop):
    """One trip: loaded to the field edge, unload, empty back. Crates per hour and energy per trip."""
    tot, _, _ = combined(crop)
    empty = tot - n_crates() * P.CROPS[crop]
    t = P.trip_m / P.speed_loaded + P.handover_s + P.trip_m / P.speed_empty
    e = P.crr * P.g * P.trip_m * (tot + empty) / P.eta_drive / 3600.0
    return {"trip_s": round(t), "crates_per_hour": round(3600.0 / t * n_crates()),
            "kg_per_hour": round(3600.0 / t * n_crates() * P.CROPS[crop]), "wh_per_trip": round(e, 1),
            "trips_per_battery": int(P.battery_wh / e)}


def report():
    out = {"crates": n_crates(), "loading_height_mm": P.deck_z,
           "top_of_stack_mm": P.deck_z + P.crate_layers * P.crate[2]}
    for crop in P.CROPS:
        out[crop] = {"payload_kg": round(payload(crop), 1), "within_rating": payload(crop) <= P.payload_max,
                     "axles": axle_loads(crop), "stability": stability(crop), "slope_10": slope_pull(crop),
                     "shuttle": shuttle(crop)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
