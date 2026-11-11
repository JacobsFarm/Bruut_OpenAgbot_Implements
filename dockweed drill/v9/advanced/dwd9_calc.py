"""Rekenwerk Dockweed drill v9 (puur Python, geen FreeCAD nodig).

v9 = proces, spil, frees, bus en Linak LA36 van v8; X- en Z-geleiding op skeelerwielen O80 x 24 (78A, 2x 608ZZ) in
UPE 100. Hier: spil en frees, snij-energie, Z-as (LA36: kracht, snelheid, stroom, inschakelduur, warmte), indrukking
van de wielen, Z-geleiding (2 UPE 100 in 4 wielblokken), X-geleiding (2 UPE 100 op de staanders, 4 wielblokken),
riemaandrijving, bouten van het X-frame, cyclus per plant, spilas, aanbouwbok, asbelasting.

    import dwd9_calc
    dwd9_calc.report()
"""
import math

import dwd9_params as P

G_ACC = 9.81
E_STEEL = 210e3                      # N/mm2

# laatste meting uit het model (build_dwd9.mass_properties: staal 7850 kg/m3, gekochte delen als vaste massa)
MODEL = {
    "implement_kg": 170.1,
    "implement_cg": (112.0, -788.0, 784.0),   # robotcoordinaten, werkstand x 150, frees 150 diep
    "x_moving_kg": 108.8,                     # alles dat met de X-as meegaat (slede, 8 wielblokken, Z-slede, bus)
    "x_moving_cg": (154.0, -845.0, 701.0),
    "z_moving_kg": 56.2,
    "pot_kg": 5.9,
    "tool_kg": 2.5,
}

# geometrie uit de parameters (zelfde opbouw als dwd9_parts.stack)
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


def shore_to_E(shore=P.wheel_shore):
    """Elasticiteitsmodulus (MPa) uit de Shore-A-hardheid (Gent): 78A -> ca. 8 MPa."""
    return 0.0981 * (56 + 7.62336 * shore) / (0.137505 * (254 - 2.54 * shore))


def wheel_deflection(F, shore=P.wheel_shore):
    """Indrukking (mm) van het PU-loopvlak onder F (N): dunne laag (dikte t) op een harde kern, contactlengte
    l = 2 sqrt(D delta) en effectieve breedte b: F = E (delta / t) b l -> delta = (F t / (2 E b sqrt(D)))^(2/3).
    Grove schatting (geen Hertz voor rubber); meet het aan een echt wiel."""
    if F <= 0:
        return 0.0
    E = shore_to_E(shore)
    return (F * P.wheel_tread_t / (2 * E * P.wheel_tread_w * math.sqrt(P.wheel_d))) ** (2.0 / 3.0)


def wheel(F, shore=P.wheel_shore):
    d = wheel_deflection(F, shore)
    return {"load_n": F, "deflection_mm": d, "k_secant_n_mm": F / d if d else float("inf"),
            "vs_ok_load": F / P.wheel_load_ok, "vs_peak_load": F / P.wheel_load_peak,
            "bearing_static_safety": 2 * P.bearing_608_C0 / F if F else float("inf")}


def z_guide(F_side=P.side_force, z=-P.depth_std):
    """Z-geleiding: 2 UPE 100 (bewegen mee) in 4 wielblokken op de X-slede (300 mm uit elkaar).
    Zijkracht F_side op het snijniveau, in v (voor/achter) of in x (links/rechts):
    - in v: per hoogte 1 flenswiel per profiel (2 profielen) + de Z-kracht achter de actuator (moment om x);
    - in x: 1 profiel neemt het op zijn lijf, 2 lijfwielen per blok.
    Uitwijking van de frees = indrukking van de wielen (kantelen tussen de 2 blokken) + buiging van de profielen
    (uitkraging van het onderste blok tot het juk, daaronder de spilbok star). Geen voorspanning gerekend (veilig)."""
    z_cut = z + 40.0
    z_lo, z_hi = P.zblk_z
    d = z_hi - z_lo
    arm = z_lo - z_cut
    lever_v = SPINDLE_V - P.act_v
    R_tilt = P.z_force_limit * lever_v / d / 2.0        # per flenswiel (per profiel, per hoogte)
    v_lo = F_side * (arm + d) / d / 2.0 + R_tilt
    v_hi = F_side * arm / d / 2.0 + R_tilt
    x_lo = F_side * (arm + d) / d / 2.0                  # per lijfwiel (2 per blok, 1 profiel)
    x_hi = F_side * arm / d / 2.0

    def tip(R_lo, R_hi):
        dl, dh = wheel_deflection(R_lo), wheel_deflection(R_hi)
        return dl + (dl + dh) / d * arm

    a = z_lo - (z + P.zg_bottom)                         # uitkraging profiel van het onderste blok tot het juk
    c = (z + P.zg_bottom) - z_cut

    def bend(F, I):
        EI = E_STEEL * I
        M = F * c
        d_tip = F * a * a * (d + a) / (3 * EI) + M * a * (2 * d + 3 * a) / (6 * EI)
        th = F * a * (2 * d + 3 * a) / (6 * EI) + M * (d + 3 * a) / (3 * EI)
        return d_tip + th * c

    bend_v = bend(F_side / 2.0, P.ch_Iy)                 # per profiel, in het vlak van het lijf
    bend_x = bend(F_side / 2.0, P.ch_Iz)                 # loodrecht op het lijf (juk houdt de 2 profielen samen)
    sigma_x = (F_side / 2.0) * arm / (P.ch_Iz / (P.ch_b - 17.0))       # zwaartepunt UPE 100 op ca. 17 van de rug
    n_wheels = 4 * 4
    W = z_lift_force()
    f_cut = P.wheel_crr * (4 * v_lo + 4 * x_lo)
    f_idle = P.wheel_crr * 4 * (W * lever_v / d / 2.0 + 20.0)
    return {"arm_mm": arm, "flange_wheel_lower_n": v_lo, "flange_wheel_upper_n": v_hi,
            "from_spindle_offset_n": R_tilt, "web_wheel_lower_n": x_lo, "web_wheel_upper_n": x_hi,
            "defl_cut_v_mm": tip(v_lo - R_tilt, v_hi - R_tilt) + bend_v,
            "defl_cut_x_mm": tip(x_lo, x_hi) + bend_x,
            "wheels_part_v_mm": tip(v_lo - R_tilt, v_hi - R_tilt), "wheels_part_x_mm": tip(x_lo, x_hi),
            "channel_bend_v_mm": bend_v, "channel_bend_x_mm": bend_x, "stress_channel_mpa": sigma_x,
            "friction_cutting_n": f_cut, "friction_idle_n": f_idle, "wheels": n_wheels,
            "channels_kg": 2 * P.ch_kg_m * (P.zg_top - P.zg_bottom) / 1000.0}


def z_forces():
    W = MODEL["z_moving_kg"] * G_ACC
    fr = z_guide()
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


def _overhang_defl(F, x, I):
    """Doorbuiging (mm) van een X-profiel onder puntlast F op x: 2 steunpunten (staanders op +-hs_x), uitkragend
    daarbuiten. Binnen: vrij opgelegd over 2 hs_x; buiten: uitkraging c met de overspanning erachter."""
    L = 2 * P.hs_x
    EI = E_STEEL * I
    if abs(x) <= P.hs_x:
        a = x + P.hs_x
        b = L - a
        return F * a * a * b * b / (3 * EI * L)
    c = abs(x) - P.hs_x
    return F * c * c * (L + c) / (3 * EI)


def guide(x=0.0, x_moving_kg=None, z_force=P.z_force_limit, F_x=0.0, z=-P.depth_std):
    """X-geleiding met de slede op x.
    - Gewicht: op de 4 lijfwielen van de 2 onderste blokken (2 per blok) in het onderste profiel (open naar boven).
    - Moment om x (gewicht hangt achter de profielen, Z-kracht op de spil nog verder achter): koppel in v tussen de
      flenswielen van het onderste en het bovenste profiel (hart flenswielen 358 uit elkaar), 2 blokken per profiel.
    - Zijkracht F_x op de frees: de riem (op belt_z) neemt de kracht, het moment om v gaat als koppel over de
      lijfwielen van de 2 onderste blokken (2 x xblk_x uit elkaar); de bovenste lijfwielen houden de slede omlaag.
    - Profiel: zwakke as voor de z-last, sterke as voor de v-last; steunpunten op de staanders."""
    m_x = MODEL["x_moving_kg"] if x_moving_kg is None else x_moving_kg
    W = m_x * G_ACC
    zl, zh = P.xch_web_z
    arm_v = (zh - P.fw_d) - (zl + P.fw_d)
    cg_v = P.robot_beam_rear_face - MODEL["x_moving_cg"][1]
    F_w = W * (cg_v - P.xch_v) / arm_v                  # per profiel, in v
    F_c = z_force * (SPINDLE_V - P.xch_v) / arm_v
    F_v = F_w + F_c
    flange = F_v / 2.0                                  # per flenswiel (1 per blok draagt in die richting)
    web_static = W / 4.0
    M_rack = F_x * (P.belt_z - (z + 40.0))
    d_rack = M_rack / (2 * P.xblk_x) / 2.0              # per lijfwiel (2 per blok)
    web_max = web_static + d_rack
    up_needed = d_rack - web_static                     # > 0: het bovenste lijfwiel moet tegenhouden
    defl_z = _overhang_defl(W, x, P.ch_Iz)
    defl_v = _overhang_defl(F_v, x, P.ch_Iy)
    sink = wheel_deflection(web_static)                 # zakking van de slede door indrukking van de lijfwielen
    F_roll = P.x_crr * (W + 4 * flange)
    return {"load_v_per_channel_n": F_v, "from_weight_v_n": F_w, "from_z_force_v_n": F_c,
            "flange_wheel_n": flange, "web_wheel_static_n": web_static, "web_wheel_max_n": web_max,
            "racking_moment_nm": M_rack / 1000.0, "upper_web_wheel_needed_n": max(0.0, up_needed),
            "web_wheel_sink_mm": sink, "flange_wheel_defl_mm": wheel_deflection(flange),
            "channel_defl_z_mm": defl_z, "channel_defl_v_mm": defl_v, "rolling_resistance_n": F_roll,
            "accel_m_s2": (x_force_max() - F_roll) / m_x,
            "channels_kg": 2 * P.ch_kg_m * (P.xbar_L - 2 * P.end_plate_t) / 1000.0}


def channel_bolts(x=P.x_max):
    """Verzonken M8 (8.8) door de voorflens in de staanders: 2 per kruising, 4 kruisingen. Trek door de v-last op het
    bovenste profiel (de slede trekt het van de staanders af), afschuiving door het gewicht; slede op x_max
    (de dichtstbij liggende staander neemt het meeste: hefboom over de 2 staanders)."""
    g = guide(x=x)
    L = 2 * P.hs_x
    c = abs(x) - P.hs_x
    share = (L + c) / L if c > 0 else (P.hs_x + abs(x)) / L    # aandeel van de dichtste staander
    F_t = g["load_v_per_channel_n"] * share / 2.0
    W = MODEL["x_moving_kg"] * G_ACC + 25.0 * G_ACC     # slede + X-frame (ca. 25 kg)
    F_s = W * share / 4.0
    proof = 22000.0                                     # M8 8.8 proefbelasting (As 36,6 x 600)
    return {"tension_per_bolt_n": F_t, "shear_per_bolt_n": F_s, "m8_8_8_proof_n": proof,
            "safety_tension": proof / F_t if F_t else float("inf")}


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


def cutter_deflection(F=P.side_force):
    """Grootste uitwijking van de frees bij zijkracht F (in x of in v): Z-geleiding (wielen + profielen) + spilas."""
    zg = z_guide(F)
    return max(zg["defl_cut_v_mm"], zg["defl_cut_x_mm"]) + shaft(F)["defl_mm"]


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
        "wheel_E_mpa": round(shore_to_E(), 1),
        "wheel_at_ok_load": _r(wheel(P.wheel_load_ok), 2),
        "z_guide_300N": _r(z_guide(), 2),
        "z_guide_100N": _r(z_guide(P.side_force_normal), 2),
        "cutter_deflection_mm (300 N, 100 N)": (round(cutter_deflection(), 1), round(cutter_deflection(P.side_force_normal), 1)),
        "x_force_max_n": round(x_force_max()),
        "x_guide_x0": _r(guide(0.0)),
        "x_guide_x_max_side_300N": _r(guide(P.x_max, F_x=P.side_force)),
        "x_channel_bolts": _r(channel_bolts(), 1),
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
