"""Rekenwerk Dockweed drill v6 (puur Python, geen FreeCAD nodig).

Spil en frees, snij-energie, Z-as (actuator: kracht, snelheid, stroom, inschakelduur), Z-rails, cyclus per plant,
aftakasbuizen tussen de zijplaten, dwarsbalken, spilas O30 in 2x UCP 206, aanbouwbok (bouten), asbelasting van de
robot (4 hubmotoren, voor stuurt) en energie per plant. v6 heeft geen eigen animatie (beweging als v2/v4).

    import dwd6_calc
    dwd6_calc.report()
"""
import math

import dwd6_params as P

G_ACC = 9.81
E_STEEL = 210e3                      # N/mm2

# laatste meting uit het model (build_dwd6.mass_properties: staal 7850 kg/m3, gekochte delen als vaste massa)
MODEL = {
    "implement_kg": 118.5,
    "implement_cg": (90.0, -792.0, 740.0),    # robotcoordinaten, werkstand x 150, frees 150 diep
    "x_moving_kg": 70.2,                      # alles dat met de X-as meegaat (slede, actuator, Z-slede, spil, bus, frees)
    "x_moving_cg": (146.0, -865.0, 606.0),
    "z_moving_kg": 46.0,
    "pot_kg": 5.9,
    "tool_kg": 2.5,
}

# geometrie uit de parameters (zelfde opbouw als dwd6_parts.stack)
SLIDE_V1 = P.slide_v0 + P.slide_t
ZT_V = SLIDE_V1 + P.rail_h + P.riser_t                 # voorkant Z-koker
SPINDLE_V = ZT_V + P.zt_d + P.sb_back_t + P.spindle_dv
SPINDLE_Y = P.v_to_y(SPINDLE_V)
TUBE_Y = P.v_to_y(P.tube_v)
REAR_AXLE_Y = -P.robot_wheel_y
FRONT_AXLE_Y = P.robot_wheel_y
WHEELBASE = FRONT_AXLE_Y - REAR_AXLE_Y
TRACK = 2 * P.robot_wheel_x


def rect_tube_I(b, t):
    return (b ** 4 - (b - 2 * t) ** 4) / 12.0


# ---------------------------------------------------------------------
# Spil en frees
# ---------------------------------------------------------------------
def motor_torque():
    """Nominaal koppel van de tandwielmotor op de uitgaande as (Nm)."""
    return P.motor_P / (2 * math.pi * P.motor_rpm / 60)


def spindle(rpm=P.cutter_rpm):
    """Direct aangedreven spil (klauwkoppeling): koppel = motorkoppel."""
    T = motor_torque()
    P_nom = T * 2 * math.pi * rpm / 60
    R = P.cutter_d / 2000.0
    return {"torque_nm": T, "power_nom_w": P_nom, "power_peak_w": P_nom * P.motor_peak, "rpm_max": P.motor_rpm,
            "tip_speed_m_s": 2 * math.pi * R * rpm / 60, "tip_force_n": T / R,
            "mower_tip_m_s": math.pi * P.mower_tip_d / 1000.0 * P.mower_rpm / 60}


def coupling():
    """Klauwkoppeling maat 28: piekkoppel van de motor tegen het nominale en maximale koppel van de koppeling."""
    T_peak = motor_torque() * P.motor_peak
    return {"motor_nom_nm": motor_torque(), "motor_peak_nm": T_peak, "coupling_nom_nm": P.jaw_T[0],
            "coupling_max_nm": P.jaw_T[1], "safety_peak_vs_max": P.jaw_T[1] / T_peak}


def chip(plunge=P.plunge_v, rpm=P.cutter_rpm):
    """Insteek per tand per omwenteling (mm): de dikte van de plakjes wortel."""
    return plunge / (rpm / 60.0 * P.cutter_teeth)


def hole_volume(depth=P.depth_std):
    return math.pi * (P.cutter_d / 2000.0) ** 2 * depth / 1000.0


def cut_power(plunge=P.plunge_v, energy=P.cut_energy_std):
    """Snijvermogen tijdens het insteken (W): specifieke energie x doorsnede x snelheid, plus verlies."""
    area = math.pi * (P.cutter_d / 2000.0) ** 2
    return energy * area * plunge / 1000.0 + P.idle_w


def spindle_current(power_w, voltage=P.motor_V):
    return power_w / voltage


def thrust(depth):
    """Neerwaartse kracht van de frees op de grond (N) bij diepte (mm) onder het maaiveld (geschat)."""
    if depth <= 0:
        return 0.0
    return min(P.thrust_n[0] + P.thrust_n[1] * depth, P.z_force_limit)


# ---------------------------------------------------------------------
# Z-as: elektrische actuator 24 V (pen-op-pen) + 2 HGR15-rails
# ---------------------------------------------------------------------
def z_lift_force():
    """Kracht om de Z-slede op te tillen (N): gewicht (de bus hangt eraan als hij los is van de grond)."""
    return (MODEL["z_moving_kg"] + MODEL["pot_kg"]) * G_ACC


def z_forces():
    """Krachten op de actuator: insteken (frees drukt + Z-slede hangt eraan), optillen, en marge t.o.v. nominaal."""
    W = MODEL["z_moving_kg"] * G_ACC
    plunge = max(0.0, P.z_force_limit - W)           # duwen: het gewicht helpt mee
    lift = z_lift_force() + P.thrust_n[0]            # trekken uit de grond (zuiging, wortels): geschat F0 extra
    return {"push_plunge_n": plunge, "pull_lift_n": lift, "rated_n": P.act_force,
            "margin_push": P.act_force / plunge if plunge else float("inf"), "margin_pull": P.act_force / lift}


def act_speed(F):
    """Snelheid van de actuator (mm/s) bij last F: lineair tussen onbelast en de opgave bij 600 N."""
    v0, v1 = P.act_speed
    return max(0.0, v0 - (v0 - v1) * F / 600.0)


def act_current(F, v):
    """Stroom (A) op 24 V bij kracht F (N) en snelheid v (mm/s): mechanisch vermogen / rendement."""
    return F * v / 1000.0 / P.act_eff / P.act_V + 0.8          # + nullast van de motor (geschat)


def act_duty(depth=P.depth_std, overlap_x=False):
    """Inschakelduur van de actuator per plant: looptijd / cyclustijd. Vergelijk met P.act_duty."""
    ph = dict(cycle(depth))
    run = ph["z_down_to_pot"] + ph["plunge"] + ph["rise_mixing"] + ph["z_up"]
    t = cycle_time(depth, overlap_x)
    return {"run_s": run, "cycle_s": t, "duty": run / t, "allowed": P.act_duty,
            "ok": run / t <= P.act_duty, "max_plants_per_hour_at_duty": 3600.0 * P.act_duty / run}


def dcdc():
    """Omvormer 48 -> 24 V: piekstroom van de actuator (blokkeren tot de slipkoppeling) tegen het vermogen."""
    vin, vout, amp = P.dcdc
    I_nom = act_current(P.z_force_limit, act_speed(P.z_force_limit))
    I_peak = act_current(P.act_force * 1.3, act_speed(P.act_force)) if act_speed(P.act_force) > 0 else I_nom * 3
    return {"actuator_nom_a": I_nom, "actuator_peak_a_est": I_peak, "converter_a": amp,
            "converter_w": vout * amp, "input_a_at_48v": vout * amp / vin / 0.92}


def z_rails(F_side=P.side_force, z=-P.depth_std):
    """Wagenkrachten (N) op de HGR15: zijkracht F_side op de frees (op snijniveau), wagens 300 mm uit elkaar.
    Ook het moment van de actuator die naast de koker duwt (act_x) met de Z-kracht."""
    z_cut = z + 40.0
    z_lo, z_hi = P.xbar_z
    arm = z_lo - z_cut                                  # onderste wagen tot snijniveau
    d = z_hi - z_lo
    R_lo = F_side * (arm + d) / d / 2.0                 # per wagen (2 naast elkaar)
    R_hi = F_side * arm / d / 2.0
    M_act = P.z_force_limit * abs(P.act_x)              # Nmm, om de v-as
    R_act = M_act / d / 2.0
    lever_v = SPINDLE_V - (SLIDE_V1 + P.rail_h / 2)     # Z-kracht op de spil achter de wagens: moment om de x-as
    R_tilt = P.z_force_limit * lever_v / d / 2.0
    return {"arm_mm": arm, "block_lower_n": R_lo, "block_upper_n": R_hi, "from_actuator_offset_n": R_act,
            "from_spindle_offset_n": R_tilt, "hgh15ca_C0_n": 15700.0}


def x_force_max():
    """Houdkracht van de riemaandrijving (N): 5:1 kast, rendement 0,95."""
    r = P.x_pulley_T * P.htd_pitch / (2 * math.pi) / 1000.0
    return P.stepper_T * P.x_gear * 0.95 / r


# ---------------------------------------------------------------------
# Cyclus per plant
# ---------------------------------------------------------------------
def cycle(depth=P.depth_std, dx=333.0):
    """Fasen per plant (s). dx = gemiddelde X-verplaatsing (1/3 van de slag).
    De bus raakt de zode als de freesonderkant nog pot_rim boven de grond is (probe = maaiveld); vanaf daar steekt de
    frees pot_rim + depth in met plunge_v en komt hij draaiend terug tot de bus loskomt (2x zo snel)."""
    to_ground = P.drive_z - P.pot_rim
    stroke = P.pot_rim + depth
    phases = [
        ("x_move", dx / P.rapid_x + 0.5),
        ("z_down_to_pot", to_ground / P.rapid_z + 0.3),
        ("plunge", stroke / P.plunge_v),
        ("dwell", P.dwell_s),
        ("rise_mixing", stroke / (2 * P.plunge_v)),
        ("z_up", to_ground / P.rapid_z + 0.3),
        ("robot_stop_start", P.stop_start_s),
    ]
    return phases


def cycle_time(depth=P.depth_std, overlap_x=False):
    ph = dict(cycle(depth))
    t = sum(ph.values())
    if overlap_x:
        t -= ph["x_move"]
    return t


def plants_per_hour(depth=P.depth_std, overlap_x=False):
    return 3600.0 / cycle_time(depth, overlap_x)


def energy_per_plant(depth=P.depth_std):
    """Energie per plant (Wh): spil tijdens draaien + assen (geschat 150 W gemiddeld tijdens de cyclus)."""
    ph = dict(cycle(depth))
    t_spin = ph["z_down_to_pot"] + ph["plunge"] + ph["dwell"] + ph["rise_mixing"]
    e_spin = cut_power() * ph["plunge"] + P.idle_w * (t_spin - ph["plunge"]) + cut_power() * 0.3 * ph["rise_mixing"]
    e_axes = 150.0 * cycle_time(depth)
    return (e_spin + e_axes) / 3600.0


# ---------------------------------------------------------------------
# Aftakasbuizen tussen de zijplaten, dwarsbalken
# ---------------------------------------------------------------------
def lemon_section(b, h, t=None, n=400):
    """Doorsnede van het citroenprofiel (numeriek): (oppervlak mm2, I om de breedte-as = buigen in z, I om de
    dikte-as = buigen in v). b = lengte in z (tip-tip), h = dikte. Met t: holle buis."""
    def half_width(b_, h_, z):
        R = (b_ * b_ / 4.0 + h_ * h_ / 4.0) / h_
        d = R - h_ / 2.0
        w = math.sqrt(max(0.0, R * R - z * z)) - d
        return max(0.0, w)

    A = Iz = Iv = 0.0
    dz = b / n
    for i in range(n):
        z = -b / 2 + (i + 0.5) * dz
        w = half_width(b, h, z)
        wi = half_width(b - 2 * t, h - 2 * t, z) if t and abs(z) < (b / 2 - t) else 0.0
        width = 2 * (w - wi)
        A += width * dz
        Iz += width * dz * z * z
        Iv += (2.0 / 3.0) * (w ** 3 - wi ** 3) * dz
    return A, Iz, Iv


def _span():
    return P.xbar_L - 2 * P.end_plate_t


def guide(x=0.0, x_moving_kg=None, z_force=P.z_force_limit):
    """Doorbuiging van de aftakasbuizen tussen de zijplaten met de slede op x (puntlast per buis).
    Vrij opgelegd (bouten in de prop laten de buis wat draaien) en ingeklemd (stijve zijplaat) als grenzen."""
    m_x = MODEL["x_moving_kg"] if x_moving_kg is None else x_moving_kg
    A, Iz, Iv = lemon_section(P.pto_b, P.pto_h, P.pto_t)
    L = _span()
    a = L / 2 + x
    b = L - a
    F_z = m_x * G_ACC / 2                               # gewicht per buis
    lever = SPINDLE_V - P.tube_v                        # spilhart achter de buizen
    F_c = z_force * lever / (P.xbar_z[1] - P.xbar_z[0])  # koppel om de x-as -> kracht in v op elke buis

    def simple(F, I):
        return F * a * a * b * b / (3 * E_STEEL * I * L)

    def fixed(F, I):
        return F * a ** 3 * b ** 3 / (3 * E_STEEL * I * L ** 3)

    d_v = simple(F_c, Iv)
    mu = 0.15
    F_fr = mu * (2 * F_c + m_x * G_ACC * 0.5)
    tubes_kg = 2 * A * L * 7.85e-6
    return {"span_mm": L, "area_mm2": A, "I_bend_z_mm4": Iz, "I_bend_v_mm4": Iv,
            "defl_z_simple_mm": simple(F_z, Iz), "defl_z_fixed_mm": fixed(F_z, Iz),
            "lever_mm": lever, "force_v_per_tube_n": F_c,
            "defl_v_simple_mm": d_v, "defl_v_fixed_mm": fixed(F_c, Iv),
            "twist_deg": math.degrees(2 * d_v / (P.xbar_z[1] - P.xbar_z[0])),
            "friction_n": F_fr, "accel_m_s2": (x_force_max() - F_fr) / m_x, "tubes_kg": tubes_kg,
            "plate_reaction_n": 2 * F_z * max(a, b) / L}


def tube_bolts():
    """2x M10 per buiseind in de prop: dwarskracht (gewicht + Z-kracht) en trek bij ingeklemde buis."""
    g = guide(x=P.x_max)
    R = math.hypot(g["plate_reaction_n"] / 2.0, g["force_v_per_tube_n"])      # per buiseind, slede op x_max
    return {"shear_per_bolt_n": R / 2.0, "m10_8_8_shear_n": 0.6 * 800 * 58.0}


def frame_beams():
    """Dwarsbalken 40 x 40 x 3: uitkraging van staander (x hs_x) tot zijplaat; de reactie van de zijplaat
    (slede op x_max) verdeeld over de 2 balken. Plus de M12 bij de staander (afschuiving)."""
    g = guide(x=P.x_max)
    a = P.xbar_L / 2 - P.end_plate_t - P.hs_x
    I = rect_tube_I(P.xbeam[0], P.xbeam[1])
    F = (g["plate_reaction_n"] * 2) / 2.0             # 2 buizen naar 1 zijplaat, verdeeld over 2 balken
    M_v = g["force_v_per_tube_n"] * a                 # kracht in v op de balk via de zijplaat
    d = F * a ** 3 / (3 * E_STEEL * I)
    d_v = g["force_v_per_tube_n"] * a ** 3 / (3 * E_STEEL * I)
    sigma = max(F, g["force_v_per_tube_n"]) * a / (I / (P.xbeam[0] / 2))
    return {"cantilever_mm": a, "force_per_beam_n": F, "defl_z_mm": d, "defl_v_mm": d_v, "stress_mpa": sigma,
            "moment_v_nm": M_v / 1000.0}


# ---------------------------------------------------------------------
# Spilas
# ---------------------------------------------------------------------
def shaft(F=P.side_force):
    """Spilas O30 massief in 2x UCP 206: doorbuiging, spanning, lagerkrachten bij zijkracht F op het snijniveau,
    kritisch toerental, en de levensduur van het onderste lager (dynamisch C, 500 rpm, F continu = worst case)."""
    d = P.shaft_d
    EI = E_STEEL * math.pi * d ** 4 / 64
    a = P.bearing_lo - 40.0                 # hart onderste lager tot snijniveau (40 boven de tandonderkant)
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
    """Wiellasten (N) bij X-stand x en een opwaartse kracht van de grond op de frees (soil_force, N).
    Geeft dict met voor/achter en de 4 wielen (RL, RR, FL, FR). Statisch, vlakke grond."""
    x = MODEL["x_moving_cg"][0] if x is None else x
    m_fix = MODEL["implement_kg"] - MODEL["x_moving_kg"]
    cg_i = MODEL["implement_cg"]
    cg_x = MODEL["x_moving_cg"]
    fix_y = (MODEL["implement_kg"] * cg_i[1] - MODEL["x_moving_kg"] * cg_x[1]) / m_fix
    fix_x = (MODEL["implement_kg"] * cg_i[0] - MODEL["x_moving_kg"] * cg_x[0]) / m_fix
    loads = [(robot_kg * G_ACC, 0.0, robot_cg_y), (m_fix * G_ACC, fix_x, fix_y)]
    m_mov = MODEL["x_moving_kg"] - (MODEL["pot_kg"] if pot_on_ground else 0.0)
    loads.append((m_mov * G_ACC, x + cg_x[0] - 150.0, cg_x[1]))
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
            "wheels_kg": {k: v / G_ACC for k, v in wheels.items()}}


def max_down_force(x=0.0, min_kg=20.0):
    """Grootste neerwaartse kracht van de frees (N) tot het lichtste wiel nog min_kg draagt."""
    lo, hi = 0.0, 5000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if min(axle_loads(x, mid, True)["wheels_kg"].values()) > min_kg:
            lo = mid
        else:
            hi = mid
    return lo


def headstock_bolts(accel_g=2.0, z_force=P.z_force_limit):
    """Aanbouwbok: trekkracht in de M10-bouten door de onderbalk (N per bout), zoals v5."""
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
    m_r = P.robot_kg
    m_i = MODEL["implement_kg"]
    m_x = MODEL["x_moving_kg"]
    cx = (m_x * x) / (m_r + m_i)
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
    lift = axle_loads(MODEL["x_moving_cg"][0])
    work = axle_loads(P.x_max, thrust(P.depth_std), True)
    hb = headstock_bolts()
    zf = z_forces()
    out = {
        "spindle": "%.0f rpm (max %.0f), O%.0f: tip %.1f m/s, %.1f Nm, %.0f W nominal / %.0f W peak; mowing %.0f m/s" % (
            P.cutter_rpm, sp["rpm_max"], P.cutter_d, sp["tip_speed_m_s"], sp["torque_nm"], sp["power_nom_w"],
            sp["power_peak_w"], sp["mower_tip_m_s"]),
        "coupling": _r(coupling()),
        "chip_mm": round(chip(), 2),
        "hole_l": round(hole_volume() * 1000, 2),
        "cut_power_w": (round(cut_power(energy=P.cut_energy[0])), round(cut_power()), round(cut_power(energy=P.cut_energy[1]))),
        "z_forces": _r(zf, 1),
        "act_speed_mm_s (push 600 N, lift)": (round(act_speed(zf["push_plunge_n"])), round(act_speed(zf["pull_lift_n"]))),
        "act_current_a (plunge, rapid lift)": (round(act_current(zf["push_plunge_n"], P.plunge_v), 1),
                                               round(act_current(zf["pull_lift_n"], P.rapid_z), 1)),
        "act_duty": _r(act_duty()),
        "dcdc": _r(dcdc(), 1),
        "z_rails": _r(z_rails(), 0),
        "x_force_max_n": round(x_force_max()),
        "cycle_s": {k: round(v, 1) for k, v in cycle()},
        "cycle_total_s": round(cycle_time(), 1),
        "plants_per_hour": round(plants_per_hour()),
        "plants_per_hour_x_overlap": round(plants_per_hour(overlap_x=True)),
        "energy_wh_per_plant": round(energy_per_plant(), 2),
        "shaft": _r(shaft()),
        "guide_x0": _r(guide(0.0)),
        "guide_x_max": _r(guide(P.x_max)),
        "tube_bolts": _r(tube_bolts(), 0),
        "frame_beams": _r(frame_beams()),
        "spindle_y": round(SPINDLE_Y),
        "axle_kg_driving (front, rear)": (round(lift["front_kg"]), round(lift["rear_kg"])),
        "axle_kg_working_x_max (front, rear)": (round(work["front_kg"]), round(work["rear_kg"])),
        "wheels_kg_working_x_max": {k: round(v) for k, v in work["wheels_kg"].items()},
        "axle_kg_driving_battery_forward (front, rear)": tuple(round(axle_loads(robot_cg_y=P.battery_forward_cg_y)[k])
                                                               for k in ("front_kg", "rear_kg")),
        "lightest_wheel_kg_driving_x_max": round(min(axle_loads(P.x_max)["wheels_kg"].values()), 1),
        "max_down_force_n (x 0, lightest wheel >= 20 kg)": round(max_down_force()),
        "max_down_force_n (x max)": round(max_down_force(P.x_max)),
        "headstock_bolt_n (2 g)": round(hb["bolt_tension_n"]),
        "headstock_bolt_safety": round(hb["safety"], 1),
        "lateral_cg_margin_mm": round(tip_lateral()["margin_to_wheel_mm"]),
    }
    return out
