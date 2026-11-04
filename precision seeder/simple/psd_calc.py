"""Calculations of the precision seeder (pure Python, no FreeCAD).

    import psd_calc; psd_calc.report()

Meter speed, seeds per hectare and per hopper, error budget of the logged seed position, area per hour and per
charge, draft and grip, and the front-axle load with the seeder lifted (ballast).
"""
import math

import psd_params as P


def seeding():
    seeds_m = 1000.0 / P.seed_spacing
    seeds_ha = 1e4 / (P.row_spacing / 1000.0) * seeds_m
    hopper_l = P.hopper[0] * P.hopper[1] * (P.hopper[2] - 10.0) / 1e6
    per_hopper_m = hopper_l * P.seeds_per_unit_l / seeds_m
    return {"seeds_m": seeds_m, "seeds_ha": seeds_ha, "rpm": P.meter_rpm(), "hz": P.speed * seeds_m,
            "hopper_l": hopper_l, "m_per_hopper": per_hopper_m, "ha_per_fill": 2 * per_hopper_m * P.row_spacing / 1e7}


def position_error():
    """1 sigma (mm) of the logged seed position along and across the row."""
    v = P.speed * 1000.0
    along = {"rtk": P.rtk, "heading": 0.0, "fall": v * P.fall_jitter, "sensor": v * P.sensor_jitter_ms / 1000.0,
             "bounce": P.bounce}
    across = {"rtk": P.rtk, "heading": P.antenna_to_seed * math.radians(P.heading_err), "fall": 0.0, "sensor": 0.0,
              "bounce": P.bounce * 0.5}
    a = math.sqrt(sum(x * x for x in along.values()))
    c = math.sqrt(sum(x * x for x in across.values()))
    return {"along": along, "across": across, "along_1s": a, "across_1s": c, "offset_uncorrected": v * P.fall_time}


def work():
    area_h = P.speed * P.pass_width / 1000.0 * 3600.0 * P.field_eff
    w_vac = P.vac_q * P.vac_pa / P.eta_fan
    w = P.drive_w + w_vac + 2 * P.stepper_w + P.computer_w
    hours = P.battery_wh / w
    return {"m2_h": area_h, "ha_h": area_h / 1e4, "W": w, "W_vac": w_vac, "hours": hours, "ha_charge": area_h * hours / 1e4}


def draft():
    f = 2 * P.draft_per_unit
    m_wheels = P.robot_mass + P.MODEL_MASS["mount_kg"]
    grip = P.mu_tyre * m_wheels * P.g
    roll = P.crr * (m_wheels + P.MODEL_MASS["implement_kg"]) * P.g
    return {"draft": f, "grip": grip, "rolling": roll, "margin": grip / (f + roll)}


def lifted(ballast=None):
    """Front axle share with the seeder lifted; ballast (kg) at y 575."""
    ballast = P.T.ballast_kg if ballast is None else ballast
    ya = -P.robot_axle_y
    L = 2 * P.robot_axle_y
    parts = [(P.robot_mass, 0.0), (P.MODEL_MASS["mount_kg"], P.MODEL_MASS["mount_cg_y"]),
             (P.MODEL_MASS["implement_kg"], P.MODEL_MASS["implement_cg_y"]), (ballast, P.T.ballast_cg_y)]
    m = sum(p[0] for p in parts)
    front = sum(mi * (yi - ya) for mi, yi in parts) / L
    return {"ballast": ballast, "front_kg": front, "total_kg": m, "share": front / m}


def ballast_for(share=P.T.front_share_min):
    b = 0.0
    while lifted(b)["share"] < share and b < 300.0:
        b += 1.0
    return b


def report():
    s = seeding()
    e = position_error()
    w = work()
    d = draft()
    l0 = lifted(0.0)
    l1 = lifted()
    lines = [
        "Precision seeder (simple)",
        "  %d rows at %d mm, seed every %d mm: %.0f seeds/ha; at %.1f m/s %.1f seeds/s per row, disc (%d holes) %.1f rpm"
        % (len(P.ROW_X), P.row_spacing, P.seed_spacing, s["seeds_ha"], P.speed, s["hz"], P.disc_holes, s["rpm"]),
        "  hopper %.1f l per unit: %.0f m of row, %.2f ha per fill (pelleted beet)" % (s["hopper_l"], s["m_per_hopper"], s["ha_per_fill"]),
        "  logged seed position 1 sigma: along %.1f mm (RTK %.0f, fall %.1f, sensor %.1f, bounce %.0f), across %.1f mm "
        "(heading %.1f)" % (e["along_1s"], P.rtk, e["along"]["fall"], e["along"]["sensor"], P.bounce, e["across_1s"],
                            e["across"]["heading"]),
        "  fall time %.2f s = %.0f mm behind the sensor at %.1f m/s (corrected in the log)"
        % (P.fall_time, e["offset_uncorrected"], P.speed),
        "  %.2f ha/h, %.0f W (vacuum %.0f W): %.1f h, %.1f ha per charge" % (w["ha_h"], w["W"], w["W_vac"], w["hours"], w["ha_charge"]),
        "  draft %.0f N + rolling %.0f N, grip %.0f N: margin %.1f" % (d["draft"], d["rolling"], d["grip"], d["margin"]),
        "  lifted: front axle %.0f %% without ballast, %.0f %% with %.0f kg; %.0f kg for %.0f %%"
        % (100 * l0["share"], 100 * l1["share"], l1["ballast"], ballast_for(), 100 * P.T.front_share_min),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
