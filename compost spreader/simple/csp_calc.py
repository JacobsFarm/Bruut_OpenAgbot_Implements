"""Calculations for the compost spreader, in pure Python (same parameters as the model).

    import csp_calc
    csp_calc.report()          # prints and returns all key figures

Masses come from build_csp.mass_properties() (copied into csp_params.MODEL_MASS after a rebuild).
"""
import math

import csp_params as P


def gate_width():
    return 2.0 * P.side_x * 1e-3        # m, the gate spans the bin between the side plates


def capacity(rho):
    """Bin volume to the top, the volume of a full payload and its fill level."""
    v_top = P.bin_volume(P.bin_flare_z[1])
    m_top = v_top * rho
    m = min(m_top, P.payload_max)
    return {"bin_l": round(v_top * 1000), "bin_full_kg": round(m_top), "load_kg": round(m),
            "load_l": round(m / rho * 1000), "fill_z": round(P.fill_level(m, rho)),
            "payload_limited": m_top > P.payload_max}


def mass_flow(dose, v):
    """kg/s for a dose (kg/m2) at a driving speed v (m/s) over the spread width."""
    return dose * P.spread_w * v


def belt_speed(q, rho, opening):
    """Belt speed (mm/s) that delivers q kg/s through a gate opening (mm)."""
    return q / (rho * P.fill_factor * gate_width() * opening * 1e-3) * 1000.0


def setting(dose, rho, v):
    """Smallest gate opening (10 mm steps) that keeps the belt under 80 % of its top speed, and that belt speed."""
    q = mass_flow(dose, v)
    op = P.GATE_RANGE[0]
    while op <= P.GATE_RANGE[1]:
        bv = belt_speed(q, rho, op)
        if bv <= 0.8 * P.belt_v_max:
            return {"kg_s": round(q, 2), "gate_mm": op, "belt_mm_s": round(bv, 1), "ok": True}
        op += 10.0
    bv = belt_speed(q, rho, P.GATE_RANGE[1])
    return {"kg_s": round(q, 2), "gate_mm": P.GATE_RANGE[1], "belt_mm_s": round(bv, 1), "ok": bv <= P.belt_v_max}


def belt_drive(rho):
    """Pull on the belt with a full load: belt on the bed plus compost on the two side walls; torque on the drum."""
    m = capacity(rho)["load_kg"]
    h = (P.fill_level(m, rho) - P.belt_top) * 1e-3
    L = (P.bin_y[1] - P.bin_y[0]) * 1e-3
    f_bed = P.mu_belt_bed * m * P.g
    f_wall = 2.0 * P.mu_wall * P.k_wall * rho * P.g * h * h / 2.0 * L
    f = f_bed + f_wall
    r = (P.drum_d / 2.0 + P.belt_t) * 1e-3
    rpm = P.belt_v_max * 1e-3 / (2 * math.pi * r) * 60.0
    return {"pull_N": round(f), "drum_Nm": round(f * r, 1), "drum_rpm_max": round(rpm, 2),
            "power_W": round(f * P.belt_v_max * 1e-3 / 0.5, 1)}


def beater(q):
    """Beater power (W) for q kg/s and the tip speed."""
    tip = 2 * math.pi * P.beater_tip_r * 1e-3 * P.beater_rpm / 60.0
    return {"power_W": round(P.e_beater * 1000.0 * q + P.p_beater_idle), "tip_m_s": round(tip, 1)}


def ballast_kg(plates):
    """Front ballast (kg) with a number of plates per stack (0 = no counterweights fitted)."""
    return 0.0 if plates == 0 else P.ballast_stacks * (P.ballast_base_kg + plates * P.ballast_plate_kg)


def combined(load_kg, plates=0):
    """Total mass and centre of gravity (y, z) of robot + spreader + compost + front ballast."""
    m = P.MODEL_MASS
    items = [(P.robot_mass, (P.robot_cg_y, P.robot_cg_z)), (m["spreader_kg"], m["spreader_cg"][1:]),
             (load_kg, m["load_cg"][1:]), (ballast_kg(plates), P.ballast_cg)]
    tot = sum(k for k, _ in items)
    y = sum(k * c[0] for k, c in items) / tot
    z = sum(k * c[1] for k, c in items) / tot
    return tot, y, z


def axle_loads(load_kg, plates=0):
    tot, y, _ = combined(load_kg, plates)
    front = tot * (y + P.wheelbase_half) / (2 * P.wheelbase_half)
    return {"total_kg": round(tot), "front_kg": round(front, 1), "rear_kg": round(tot - front, 1),
            "front_share": round(front / tot, 3)}


def stability(load_kg, plates=0):
    """Static tip angles (deg): sideways over the wheel line and lengthways over the axles."""
    tot, y, z = combined(load_kg, plates)
    return {"cg_y": round(y), "cg_z": round(z), "side_deg": round(math.degrees(math.atan(P.track_half / z)), 1),
            "backward_deg": round(math.degrees(math.atan((P.wheelbase_half + y) / z)), 1),
            "forward_deg": round(math.degrees(math.atan((P.wheelbase_half - y) / z)), 1)}


def slope_pull(load_kg, plates=0, slope_deg=10.0):
    tot, _, _ = combined(load_kg, plates)
    a = math.radians(slope_deg)
    need = tot * P.g * (P.crr * math.cos(a) + math.sin(a))
    grip = P.mu_tyre * tot * P.g * math.cos(a)
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    return {"need_N": round(need), "grip_N": round(grip), "motor_cont_N": round(motors),
            "margin": round(min(grip, motors) / need, 2)}


def plates_needed(load_kg):
    """Fewest ballast plates per stack that keep front_share_min on the front axle (None if 4 are not enough)."""
    for n in range(P.ballast_plates_max + 1):
        if axle_loads(load_kg, n)["front_share"] >= P.front_share_min:
            return n
    return None


def max_slope(load_kg, plates):
    """Steepest slope (deg) the hub motors climb continuously."""
    tot, _, _ = combined(load_kg, plates)
    f = P.n_driven * P.hub_torque_nom / P.r_load
    a = 0.0
    while tot * P.g * (P.crr * math.cos(math.radians(a)) + math.sin(math.radians(a))) < f and a < 45:
        a += 0.1
    return round(a, 1)


def per_load(job, rho, plates=0):
    """One bin: spread length, area and time, refill and travel; area per hour and energy per load."""
    dose = P.DOSES[job]
    v = P.drive_speed[job]
    load = capacity(rho)["load_kg"]
    area = load / dose
    length = area / P.spread_w
    t_spread = length / v
    t_cycle = t_spread + P.refill_s + P.headland_m / 1.2
    q = mass_flow(dose, v)
    tot, _, _ = combined(load / 2.0, plates)
    e_drive = P.crr * P.g * tot * (length + P.headland_m) / P.eta_drive / 3600.0
    e_beat = beater(q)["power_W"] * t_spread / 3600.0
    e_belt = belt_drive(rho)["power_W"] * t_spread / 3600.0
    e = e_drive + e_beat + e_belt
    return {"dose_kg_m2": dose, "speed_m_s": v, "setting": setting(dose, rho, v), "area_m2": round(area),
            "length_m": round(length), "spread_s": round(t_spread), "cycle_s": round(t_cycle),
            "m2_per_hour": round(area * 3600.0 / t_cycle), "t_per_hour": round(load * 3600.0 / t_cycle / 1000.0, 2),
            "wh_per_load": round(e, 1), "loads_per_battery": int(P.battery_wh / e),
            "beater_W": beater(q)["power_W"]}


def report():
    rho = P.COMPOST[P.compost_ref]
    out = {"capacity": {k: capacity(r) for k, r in P.COMPOST.items()}, "belt_drive": belt_drive(rho),
           "beater_tip": beater(0.0)["tip_m_s"]}
    full = capacity(rho)["load_kg"]
    n = plates_needed(full)
    out["ballast"] = {"plates_per_stack": n, "kg": ballast_kg(n)}
    for state, kg in (("empty", 0.0), ("full", full)):
        out[state] = {"axles_no_ballast": axle_loads(kg), "axles_ballast": axle_loads(kg, n),
                      "stability": stability(kg, n), "slope_10": slope_pull(kg, n), "max_slope_deg": max_slope(kg, n)}
    for job in P.DOSES:
        out[job] = per_load(job, rho, n)
    for k, v in out.items():
        print(k, v)
    return out
