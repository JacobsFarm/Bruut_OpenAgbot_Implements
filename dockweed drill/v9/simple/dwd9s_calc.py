"""Rekenwerk Dockweed drill v9 simple - VOORLOPIG: alleen proces, LA36 en asbelasting (voor de animatie).

De berekening van de geleiding (zijkracht van de wielen op de flenzen, wrijving tegen riem en LA36, axiale last op de
608-lagers, speling aan de frees, platen 4 mm) volgt nog op verzoek van de gebruiker. Tot dan rekent z_forces() zonder
wrijving in de Z-geleiding.

    import dwd9s_calc
    dwd9s_calc.report()
"""
import math

import dwd9s_params as P

G_ACC = 9.81
E_STEEL = 210e3                      # N/mm2

# laatste meting uit het model (build_dwd9s.mass_properties: staal 7850 kg/m3, gekochte delen als vaste massa)
MODEL = {
    "implement_kg": 117.6,
    "implement_cg": (113.0, -741.0, 747.0),   # robotcoordinaten, werkstand x 150, frees 150 diep
    "x_moving_kg": 72.0,
    "x_moving_cg": (154.0, -790.0, 626.0),
    "z_moving_kg": 38.8,
    "pot_kg": 5.9,
    "tool_kg": 2.5,
}

# geometrie uit de parameters (zelfde opbouw als dwd9s_parts.stack)
SPINDLE_V = P.sb_back_v0 + P.sb_back_t + P.spindle_dv
SPINDLE_Y = P.v_to_y(SPINDLE_V)
REAR_AXLE_Y = -P.robot_wheel_y
FRONT_AXLE_Y = P.robot_wheel_y
WHEELBASE = FRONT_AXLE_Y - REAR_AXLE_Y
TRACK = 2 * P.robot_wheel_x


def rect_tube_I(b, t):
    return (b ** 4 - (b - 2 * t) ** 4) / 12.0


def round_tube(D, t):
    """(oppervlak mm2, I mm4) van een ronde buis."""
    d = D - 2 * t
    return math.pi / 4 * (D * D - d * d), math.pi / 64 * (D ** 4 - d ** 4)


# ---------------------------------------------------------------------
# Spil en frees (zoals v6 / v7)
# ---------------------------------------------------------------------
def motor_torque():
    return P.motor_P / (2 * math.pi * P.motor_rpm / 60)


def spindle(rpm=P.cutter_rpm):
    T = motor_torque()
    P_nom = T * 2 * math.pi * rpm / 60
    R = P.cutter_d / 2000.0
    return {"torque_nm": T, "power_nom_w": P_nom, "power_peak_w": P_nom * P.motor_peak,
            "tip_speed_m_s": 2 * math.pi * R * rpm / 60, "tip_force_n": T / R}


def coupling():
    T_peak = motor_torque() * P.motor_peak
    return {"motor_nom_nm": motor_torque(), "motor_peak_nm": T_peak, "coupling_nom_nm": P.jaw_T[0],
            "coupling_max_nm": P.jaw_T[1], "safety_peak_vs_max": P.jaw_T[1] / T_peak}


def chip(plunge=P.plunge_v, rpm=P.cutter_rpm):
    return plunge / (rpm / 60.0 * P.cutter_teeth)


def hole_volume(depth=P.depth_std):
    return math.pi * (P.cutter_d / 2000.0) ** 2 * depth / 1000.0


def cut_power(plunge=P.plunge_v, energy=P.cut_energy_std):
    area = math.pi * (P.cutter_d / 2000.0) ** 2
    return energy * area * plunge / 1000.0 + P.idle_w


def spindle_current(power_w, voltage=P.motor_V):
    return power_w / voltage


def thrust(depth):
    if depth <= 0:
        return 0.0
    return min(P.thrust_n[0] + P.thrust_n[1] * depth, P.z_force_limit)


# ---------------------------------------------------------------------
# Z-as: Linak LA36 24 V (pen-op-pen, midden) + 2 ronde buizen in 4 glijlagers op de X-slede (zoals v7)
# ---------------------------------------------------------------------
def z_lift_force():
    return (MODEL["z_moving_kg"] + MODEL["pot_kg"]) * G_ACC


def z_forces():
    W = MODEL["z_moving_kg"] * G_ACC
    fr = {"friction_cutting_n": 0.0, "friction_idle_n": 0.0}      # geleiding: volgt nog
    plunge = max(0.0, P.z_force_limit - W) + fr["friction_cutting_n"]
    lift = z_lift_force() + P.thrust_n[0] + fr["friction_idle_n"]
    return {"push_plunge_n": plunge, "pull_lift_n": lift, "friction_cutting_n": fr["friction_cutting_n"],
            "rated_n": P.act_force, "selflock_n": P.act_selflock,
            "margin_push": P.act_force / plunge if plunge else float("inf"), "margin_pull": P.act_force / lift}


def act_speed(F):
    v0, v1 = P.act_speed
    return max(0.0, v0 - (v0 - v1) * F / P.act_force)


def act_current(F, v=None):
    if v is not None and v <= 0:
        return 0.0
    i0, i1 = P.act_amp
    return i0 + (i1 - i0) * F / P.act_force


def act_phases(depth=P.depth_std):
    """(fase, duur s, stroom A) van de actuator per plant."""
    ph = dict(cycle(depth))
    zf = z_forces()
    return [("down", ph["z_down_to_pot"], act_current(0.0)),
            ("plunge", ph["plunge"], act_current(zf["push_plunge_n"])),
            ("rise", ph["rise_mixing"], act_current(zf["pull_lift_n"])),
            ("up", ph["z_up"], act_current(zf["pull_lift_n"]))]


def act_duty(depth=P.depth_std):
    run = sum(t for _, t, _ in act_phases(depth))
    t = cycle_time(depth)
    return {"run_s": run, "cycle_s": t, "duty_back_to_back": run / t,
            "duty_at_plant_period": run / max(t, P.plant_period_s), "allowed_full_load": P.act_duty}


def act_thermal(period_s=None, depth=P.depth_std):
    """Warmte in de motor van de LA36 ~ I^2 R: gemiddelde I^2 over een plantinterval tegen I_max^2 x 20 %
    (vuistregel, koperverlies; zoals v7)."""
    period = cycle_time(depth) if period_s is None else max(period_s, cycle_time(depth))
    i2t = sum(t * i * i for _, t, i in act_phases(depth))
    allowed = P.act_amp[1] ** 2 * P.act_duty
    return {"period_s": period, "i2t_per_plant_a2s": i2t, "mean_i2_a2": i2t / period, "allowed_i2_a2": allowed,
            "load_vs_allowed": i2t / period / allowed, "min_period_s": i2t / allowed}


def dcdc():
    vin, vout, amp = P.dcdc
    I_nom = act_current(z_forces()["push_plunge_n"])
    I_peak = act_current(P.act_force) * 1.2
    return {"actuator_nom_a": I_nom, "actuator_peak_a_est": I_peak, "converter_a": amp,
            "converter_w": vout * amp, "input_a_at_48v": vout * amp / vin / 0.92}


# ---------------------------------------------------------------------
# X-as: 2 UPE 100 met de openingen naar elkaar toe op de staanders, slede op 4 wielblokken, riem met vaste motor
# ---------------------------------------------------------------------
def x_force_max():
    """Houdkracht van de riemaandrijving (N): 5:1 kast, rendement 0,95."""
    r = P.x_pulley_T * P.htd_pitch / (2 * math.pi) / 1000.0
    return P.stepper_T * P.x_gear * 0.95 / r


# ---------------------------------------------------------------------
# Cyclus per plant (X verplaatst terwijl de robot rijdt: overlap)
# ---------------------------------------------------------------------
def cycle(depth=P.depth_std, dx=333.0):
    """Fasen per plant (s). dx = gemiddelde X-verplaatsing (1/3 van de slag). De bus raakt de zode als de
    freesonderkant nog pot_rim boven de grond is; vanaf daar steekt de frees pot_rim + depth in met plunge_v en komt
    hij draaiend terug tot de bus loskomt (2x zo snel)."""
    to_ground = P.drive_z - P.pot_rim
    stroke = P.pot_rim + depth
    return [
        ("x_move", dx / P.rapid_x + 0.5),
        ("z_down_to_pot", to_ground / P.rapid_z + 0.3),
        ("plunge", stroke / P.plunge_v),
        ("dwell", P.dwell_s),
        ("rise_mixing", stroke / (2 * P.plunge_v)),
        ("z_up", to_ground / P.rapid_z + 0.3),
        ("robot_stop_start", P.stop_start_s),
    ]


def cycle_time(depth=P.depth_std, overlap_x=True):
    ph = dict(cycle(depth))
    t = sum(ph.values())
    if overlap_x:
        t -= ph["x_move"]
    return t


def plants_per_hour(depth=P.depth_std, overlap_x=True, spacing_m=None):
    t = cycle_time(depth, overlap_x)
    if spacing_m:
        t += spacing_m * 1000.0 / P.drive_speed
    return 3600.0 / t


def energy_per_plant(depth=P.depth_std):
    ph = dict(cycle(depth))
    t_spin = ph["z_down_to_pot"] + ph["plunge"] + ph["dwell"] + ph["rise_mixing"]
    e_spin = cut_power() * ph["plunge"] + P.idle_w * (t_spin - ph["plunge"]) + cut_power() * 0.3 * ph["rise_mixing"]
    e_act = sum(t * i for _, t, i in act_phases(depth)) * P.act_V
    e_x = 60.0 * ph["x_move"]                            # stepper + kast tijdens de X-beweging (geschat)
    return (e_spin + e_act + e_x + 60.0 * cycle_time(depth)) / 3600.0      # + 60 W elektronica en camera


# ---------------------------------------------------------------------
# Spilas
# ---------------------------------------------------------------------
def shaft(F=P.side_force):
    d = P.shaft_d
    EI = E_STEEL * math.pi * d ** 4 / 64
    a = P.bearing_lo - 40.0
    L = P.bearing_dist
    delta = F * a ** 2 * (a + L) / (3 * EI)
    sigma = F * a / (math.pi * d ** 3 / 32)
    k = F / delta * 1000.0
    n_cr = math.sqrt(k / MODEL["tool_kg"]) * 60 / (2 * math.pi)
    R_lo = F * (a + L) / L
    L10_h = (P.ucp_C / R_lo) ** 3 * 1e6 / (60 * P.cutter_rpm)
    return {"overhang_mm": a, "defl_mm": delta, "stress_shaft_at_bearing_mpa": sigma,
            "bearing_lower_n": R_lo, "bearing_upper_n": F * a / L, "critical_rpm": n_cr,
            "cutter_pct_of_critical": 100.0 * P.cutter_rpm / n_cr, "L10_lower_h_at_full_side_force": L10_h}


# ---------------------------------------------------------------------
# Robot: asbelasting en aanbouwbok
# ---------------------------------------------------------------------
def axle_loads(x=None, soil_force=0.0, pot_on_ground=False, robot_kg=P.robot_kg, robot_cg_y=P.robot_cg_y):
    """Wiellasten bij X-stand x (spilhart) en een opwaartse kracht van de grond op de frees (soil_force, N)."""
    x = 0.0 if x is None else x
    m_fix = MODEL["implement_kg"] - MODEL["x_moving_kg"]
    cg_i = MODEL["implement_cg"]
    cg_x = MODEL["x_moving_cg"]
    fix_y = (MODEL["implement_kg"] * cg_i[1] - MODEL["x_moving_kg"] * cg_x[1]) / m_fix
    fix_x = (MODEL["implement_kg"] * cg_i[0] - MODEL["x_moving_kg"] * cg_x[0]) / m_fix
    loads = [(robot_kg * G_ACC, 0.0, robot_cg_y), (m_fix * G_ACC, fix_x, fix_y)]
    m_mov = MODEL["x_moving_kg"] - (MODEL["pot_kg"] if pot_on_ground else 0.0)
    loads.append((m_mov * G_ACC, x + cg_x[0] - P.work_x, cg_x[1]))
    loads.append((-soil_force, x, SPINDLE_Y))
    W = sum(f for f, _, _ in loads)
    My = sum(f * (yy - REAR_AXLE_Y) for f, _, yy in loads)
    Mx = sum(f * xx for f, xx, _ in loads)
    front = My / WHEELBASE
    rear = W - front
    lat = Mx / TRACK
    share = front / W if W else 0.5
    wheels = {"RL": rear / 2 - lat * (1 - share), "RR": rear / 2 + lat * (1 - share),
              "FL": front / 2 - lat * share, "FR": front / 2 + lat * share}
    return {"total_n": W, "front_n": front, "rear_n": rear, "front_kg": front / G_ACC, "rear_kg": rear / G_ACC,
            "front_share": front / W, "wheels_kg": {k: v / G_ACC for k, v in wheels.items()}}


def max_down_force(x=0.0, min_kg=20.0):
    lo, hi = 0.0, 5000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if min(axle_loads(x, mid, True)["wheels_kg"].values()) > min_kg:
            lo = mid
        else:
            hi = mid
    return lo


def headstock_bolts(accel_g=2.0, z_force=P.z_force_limit):
    m = MODEL["implement_kg"]
    cg_y = MODEL["implement_cg"][1]
    arm_load = (P.robot_beam_rear_face - cg_y)
    M = m * G_ACC * accel_g * arm_load / 1000.0
    M_z = z_force * (P.robot_beam_rear_face - SPINDLE_Y) / 1000.0
    lever = abs(P.hs_bolt_v)
    lever_v = P.robot_lower_beam_z[1] - P.robot_lower_beam_z[0] + P.hs_plate_t
    F_bolt = (M + M_z) * 1000.0 / (lever + lever_v) / 4.0
    return {"moment_nm": M, "moment_z_force_nm": M_z, "bolt_tension_n": F_bolt,
            "m10_8_8_proof_n": 33700.0, "safety": 33700.0 / F_bolt if F_bolt else float("inf")}


def tip_lateral(x=P.x_max):
    cx = MODEL["x_moving_kg"] * x / (P.robot_kg + MODEL["implement_kg"])
    return {"cg_x_mm": cx, "margin_to_wheel_mm": P.robot_wheel_x - abs(cx)}


# ---------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------
def _r(d, n=2):
    return {k: (round(v, n) if isinstance(v, float) else v) for k, v in d.items()}


def report(model=None):
    if model:
        MODEL.update(model)
    sp = spindle()
    drive = axle_loads(0.0)
    work = axle_loads(P.x_max, thrust(P.depth_std), True)
    hb = headstock_bolts()
    zf = z_forces()
    out = {
        "spindle": "%.0f rpm, O%.0f: tip %.1f m/s, %.1f Nm, %.0f W nominal / %.0f W peak" % (
            P.cutter_rpm, P.cutter_d, sp["tip_speed_m_s"], sp["torque_nm"], sp["power_nom_w"], sp["power_peak_w"]),
        "coupling": _r(coupling()),
        "chip_mm": round(chip(), 2),
        "cut_power_w": (round(cut_power(energy=P.cut_energy[0])), round(cut_power()), round(cut_power(energy=P.cut_energy[1]))),
        "z_forces": _r(zf, 1),
        "act_speed_mm_s (push, lift)": (round(act_speed(zf["push_plunge_n"])), round(act_speed(zf["pull_lift_n"]))),
        "act_phases (s, A)": [(n, round(t, 1), round(i, 1)) for n, t, i in act_phases()],
        "act_duty": _r(act_duty()),
        "act_thermal_back_to_back": _r(act_thermal(), 1),
        "act_thermal_at_plant_period": _r(act_thermal(P.plant_period_s), 1),
        "dcdc": _r(dcdc(), 1),
        "x_force_max_n": round(x_force_max()),
        "cycle_s": {k: round(v, 1) for k, v in cycle()},
        "cycle_total_s (X while driving)": round(cycle_time(), 1),
        "cycle_total_s (X after the stop)": round(cycle_time(overlap_x=False), 1),
        "plants_per_hour (back to back, 2 m apart, 5 m apart)": (round(plants_per_hour()),
                                                                  round(plants_per_hour(spacing_m=2)),
                                                                  round(plants_per_hour(spacing_m=5))),
        "energy_wh_per_plant": round(energy_per_plant(), 2),
        "shaft": _r(shaft()),
        "spindle_y": round(SPINDLE_Y),
        "tool_behind_rear_axle_mm": round(REAR_AXLE_Y - SPINDLE_Y),
        "axle_kg_driving_x0 (front, rear)": (round(drive["front_kg"]), round(drive["rear_kg"])),
        "front_share_driving": round(drive["front_share"], 3),
        "axle_kg_working_x_max (front, rear)": (round(work["front_kg"]), round(work["rear_kg"])),
        "wheels_kg_working_x_max": {k: round(v) for k, v in work["wheels_kg"].items()},
        "axle_kg_driving_battery_forward (front, rear)": tuple(round(axle_loads(0.0, robot_cg_y=P.battery_forward_cg_y)[k])
                                                               for k in ("front_kg", "rear_kg")),
        "lightest_wheel_kg_driving_x_max": round(min(axle_loads(P.x_max)["wheels_kg"].values()), 1),
        "max_down_force_n (x 0, lightest wheel >= 20 kg)": round(max_down_force()),
        "max_down_force_n (x max)": round(max_down_force(P.x_max)),
        "headstock_bolt_n (2 g)": round(hb["bolt_tension_n"]),
        "headstock_bolt_safety": round(hb["safety"], 1),
        "lateral_cg_margin_mm": round(tip_lateral()["margin_to_wheel_mm"]),
    }
    return out


if __name__ == "__main__":
    for key, value in report().items():
        print(key, value)
