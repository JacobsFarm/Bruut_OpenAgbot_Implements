"""Calculations for the dumper barrow, in pure Python (same parameters as the model).

    import dmb_calc
    dmb_calc.report()          # prints and returns all key figures
"""
import math

import dmb_params as P

MODEL = {"fixed_kg": 21.5, "fixed_cg": (-175.0, 702.0), "tip_kg": 50.9, "tip_cg": (-185.0, 890.0)}   # (y, z)


def load(material):
    """Load (kg) of a material: the bin full to the rim or the payload, whichever is less; its cg (y, z) bin down."""
    rho = P.LOADS[material]
    v = P.bin_volume()
    kg = min(v * rho, P.payload_max)
    frac = kg / (v * rho)
    h = P.bin_h * frac
    y0, y1 = P.bin_y
    cg = ((y0 + y1) / 2.0 - 40.0, P.rail_z[1] + P.sheet + h / 2.0)
    return {"kg": round(kg), "fill": round(frac, 2), "litres": round(kg / rho * 1000), "cg": cg}


def combined(material, deg=0.0):
    """Total mass and cg (y, z) of robot + dumper + load at a tip angle (load still in the bin)."""
    ld = load(material)
    items = [(P.robot_mass, (P.robot_cg_y, P.robot_cg_z)), (MODEL["fixed_kg"], MODEL["fixed_cg"]),
             (MODEL["tip_kg"], P.rotate(MODEL["tip_cg"], deg)), (ld["kg"], P.rotate(ld["cg"], deg))]
    tot = sum(k for k, _ in items)
    return tot, sum(k * c[0] for k, c in items) / tot, sum(k * c[1] for k, c in items) / tot


def axles(material):
    tot, y, z = combined(material)
    front = tot * (y + P.wheelbase_half) / (2 * P.wheelbase_half)
    return {"total_kg": round(tot), "front_share": round(front / tot, 3), "cg_z": round(z),
            "side_tip_deg": round(math.degrees(math.atan(P.track_half / z)), 1)}


def tipping(material):
    """Actuator force per actuator over the tip (virtual work, load still in), the rear stability at full tip and the
    tip time."""
    ld = load(material)
    worst = 0.0
    for deg in range(0, int(P.tip_max) + 1, 4):
        d = 0.5
        dz = 0.0
        for m, c in ((MODEL["tip_kg"], MODEL["tip_cg"]), (ld["kg"], ld["cg"])):
            dz += m * (P.rotate(c, deg + d)[1] - P.rotate(c, deg - d)[1])
        dl = P.act_length(deg + d) - P.act_length(deg - d)
        worst = max(worst, P.g * dz / (2 * dl))
    _, y, z = combined(material, P.tip_max)
    lens = (P.act_length(0.0), P.act_length(P.tip_max))
    return {"force_per_act_N": round(worst), "ok": worst <= P.act_force, "cg_y_tipped": round(y),
            "behind_rear_axle": y < -P.wheelbase_half, "time_s": round((lens[1] - lens[0]) / P.act_speed),
            "act_mm": (round(lens[0]), round(lens[1]))}


def slope(material, deg=10.0):
    tot, _, _ = combined(material)
    a = math.radians(deg)
    need = tot * P.g * (P.crr * math.cos(a) + math.sin(a))
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    grip = P.mu_tyre * tot * P.g * math.cos(a)
    return {"need_N": round(need), "margin": round(min(motors, grip) / need, 2)}


def shuttle(material):
    ld = load(material)
    t = P.load_s + P.trip_m / P.speed_loaded + P.dump_s + tipping(material)["time_s"] * 2 + P.trip_m / P.speed_empty
    tot, _, _ = combined(material)
    e = P.crr * P.g * P.trip_m * (2 * tot - ld["kg"]) / P.eta_drive / 3600.0
    return {"trip_s": round(t), "kg_per_hour": round(ld["kg"] * 3600.0 / t), "wh_per_trip": round(e, 1),
            "trips_per_battery": int(P.battery_wh / e)}


def report():
    out = {"bin_l": round(P.bin_volume() * 1000)}
    for m in P.LOADS:
        out[m] = {"load": {k: v for k, v in load(m).items() if k != "cg"}, "axles": axles(m), "tipping": tipping(m),
                  "slope_10": slope(m), "shuttle": shuttle(m)}
    for k, v in out.items():
        print(k, v)
    return out
