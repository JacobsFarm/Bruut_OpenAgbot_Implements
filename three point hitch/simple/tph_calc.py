"""Calculations for the three-point hitch with the small cultivator, in pure Python (same parameters as the model).

    import tph_calc
    tph_calc.report()          # prints and returns all key figures

Masses come from build_tph.mass_properties() (copied into tph_params.MODEL_MASS after a rebuild).
"""
import math

import tph_params as P


def linkage_table():
    """Height of the lower pins, top pin and pitch of the implement over the lift poses."""
    out = {}
    for lift in P.LIFT_POSES:
        b, d, pitch = P.linkage(lift)
        out[lift] = {"lower_pin_z": round(b[1]), "top_pin": (round(d[0]), round(d[1])), "pitch_deg": round(pitch, 1)}
    out["lift_range_mm"] = round(P.linkage(P.lift_transport)[0][1] - P.lower_b[1])
    return out


def _cg(lift, cg=None):
    """Implement centre of gravity (y, z) at a lift angle (rigid move with the linkage)."""
    cg = cg or (P.MODEL_MASS["imp_cg_y"], P.MODEL_MASS["imp_cg_z"])
    b, _, pitch = P.linkage(lift)
    a = math.radians(pitch)
    dy, dz = cg[0] - P.lower_b[0], cg[1] - P.lower_b[1]
    return (b[0] + dy * math.cos(a) - dz * math.sin(a), b[1] + dy * math.sin(a) + dz * math.cos(a))


def actuator(mass=None, cg=None):
    """Force per lift rod (N) over the lift range by virtual work: m g dz_cg = 2 F dL (both rods)."""
    m = mass if mass is not None else P.MODEL_MASS["imp_kg"]
    worst = 0.0
    out = {}
    h = 0.5
    for lift in P.LIFT_POSES[1:]:
        dz = _cg(lift + h, cg)[1] - _cg(lift - h, cg)[1]
        dl = abs(P.act_length(lift + h) - P.act_length(lift - h))
        f = m * P.g * dz / (2 * dl)
        worst = max(worst, f)
        out["lift_%g" % lift] = round(f)
    lens = [P.act_length(x) for x in P.LIFT_POSES]
    out["length_range"] = (round(min(lens), 1), round(max(lens), 1))
    out["fits_stroke"] = P.act_retracted <= min(lens) and max(lens) <= P.act_retracted + P.act_stroke
    out["lift_time_s"] = round((max(lens) - min(lens)) / P.act_speed, 1)
    out["max_N"] = round(worst)
    out["lift_capacity_kg"] = round(m * P.act_force / worst) if worst > 0 else None
    return out


def axle_loads(imp_kg=None, imp_cg_y=None, ballast=True):
    """Load (kg) on the front and rear axle with the implement lifted (transport)."""
    m = P.MODEL_MASS
    imp_kg = m["imp_kg"] if imp_kg is None else imp_kg
    if imp_cg_y is None:
        imp_cg_y = _cg(P.lift_transport)[0]
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]),
             (m["links_kg"], (P.lower_a[0] + P.lower_b[0]) / 2.0), (imp_kg, imp_cg_y)]
    if ballast:
        items.append((P.ballast_kg, P.ballast_cg_y))
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3)}


def capacity():
    """Heaviest implement the robot can carry lifted with front_share_min on the front axle (with and without the
    front counterweight), its cg imp_cg_behind behind the lower pins."""
    b = P.linkage(P.lift_transport)[0]
    y = b[0] - P.imp_cg_behind
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
    """Pull force (N) of the cultivator: duckfoot shares (k_tine x share width x depth) and rolling of the robot."""
    m = P.MODEL_MASS
    tines = len(P.tine_x) * P.k_tine * P.share_w / 1000.0 * P.work_depth / 1000.0
    on_robot = P.robot_mass + m["mount_kg"] + m["links_kg"] + P.ballast_kg
    roll = P.crr * (on_robot + m["imp_kg"]) * P.g
    grip = P.mu_tyre * on_robot * P.g
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    total = tines + roll
    width = (P.tine_x[-1] - P.tine_x[0] + 200.0) / 1000.0
    return {"tines_N": round(tines), "rolling_N": round(roll), "total_N": round(total), "grip_N": round(grip),
            "motor_cont_N": round(motors), "margin": round(min(grip, motors) / total, 2),
            "power_W": round(total * P.speed / P.eta_drive), "width_m": width,
            "ha_per_hour": round(width * P.speed * 3600 / 10000.0 * 0.8, 2)}


def report():
    out = {"linkage": linkage_table(), "actuator": actuator(), "capacity_kg": capacity(),
           "axle_transport": axle_loads(), "axle_transport_no_ballast": axle_loads(ballast=False),
           "cultivator": draft()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
