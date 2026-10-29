"""Calculations for the straw spreader, in pure Python (same parameters as the model).

    import stw_calc
    stw_calc.report()          # prints and returns all key figures
"""
import math

import stw_params as P


def load_kg():
    return P.n_bales * P.bale_kg


def bale_density():
    bx, bz, by = P.bale
    return P.bale_kg / (bx * bz * by / 1e9)


def per_dose(dose):
    """Straw flow (kg/s), floor speed (mm/s), length of strip and minutes per fill at the working speed."""
    flow = dose * P.strip_w * P.speed
    bx, bz, _ = P.bale
    area = bx * bz * P.n_bales / 1e6                      # m2 face of the bale stack
    floor = flow / (bale_density() * area) * 1000.0
    length = load_kg() / (dose * P.strip_w)
    drum_W = flow * P.specific_energy * 1000.0 / P.eta_drum + P.drum_idle_W
    return {"flow_kg_s": round(flow, 3), "floor_mm_s": round(floor, 2), "strip_m_per_fill": round(length),
            "min_per_fill": round(length / P.speed / 60.0, 1), "drum_W": round(drum_W),
            "drum_load": round(drum_W / P.drum_w, 2)}


def drum():
    tip = P.drum_rpm * math.pi * (P.drum_d + 2 * P.spike_l) / 1000.0 / 60.0
    return {"rpm": P.drum_rpm, "tip_m_s": round(tip, 1)}


def axle_and_tipping():
    m = P.MODEL_MASS
    items = [(P.robot_mass, 0.0, P.robot_cg_z), (m["kg"], m["cg_y"], m["cg_z"]),
             (load_kg(), P.bale_y0 + P.bale[2] / 2.0, P.bale_z0 + P.n_bales * P.bale[1] / 2.0)]
    tot = sum(k for k, _, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y, _ in items) / (2.0 * P.robot_axle_y)
    cg_z = sum(k * z for k, _, z in items) / tot
    return {"total_kg": round(tot, 1), "front_kg": round(front, 1), "rear_kg": round(tot - front, 1),
            "rear_share": round((tot - front) / tot, 3), "cg_z": round(cg_z),
            "side_slope_deg": round(math.degrees(math.atan(P.robot_track / 2.0 / cg_z)), 1)}


def energy(dose=0.5):
    a = axle_and_tipping()
    drive_W = P.crr * a["total_kg"] * P.g * P.speed / P.eta_drive
    w = drive_W + per_dose(dose)["drum_W"]
    hours = P.robot_battery_wh / w
    return {"drive_W": round(drive_W), "total_W": round(w), "hours": round(hours, 1),
            "strip_m_per_charge": round(hours * 3600.0 * P.speed * 0.6)}   # 60 % of the time laying, rest refilling


def report():
    out = {"load_kg": load_kg(), "bale_density": round(bale_density()), "drum": drum(),
           "dose": {d: per_dose(d) for d in P.dose}, "axle": axle_and_tipping(), "energy_0.5": energy(0.5)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
