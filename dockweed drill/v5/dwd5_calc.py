"""Rekenwerk Dockweed drill v5 (puur Python, geen FreeCAD nodig).

Spil en frees, snij-energie, assen, cyclus per plant, aftakas-geleiding (doorbuiging, wrijving), spilas,
aanbouwbok (bouten), asbelasting van de robot (4 hubmotoren, voor stuurt) en energie per plant.
v5 heeft geen eigen animatie (zie v4); het rapport gebruikt dezelfde parameters als het model.

    import dwd5_calc
    dwd5_calc.report()
"""
import math

import dwd5_params as P

G_ACC = 9.81
E_STEEL = 210e3                      # N/mm2

# laatste meting uit het model (build_dwd5.mass_properties: staal 7850 kg/m3, gekochte delen als vaste massa)
MODEL = {
    "implement_kg": 102.2,
    "implement_cg": (106.0, -774.0, 802.0),    # robotcoordinaten, werkstand x 150, frees 150 diep
    "x_moving_kg": 64.7,                      # alles dat met de X-as meegaat (slede, Z-slede, spil, pot, frees)
    "x_moving_cg": (163.0, -828.0, 726.0),
    "z_moving_kg": 35.1,
    "pot_kg": 5.9,
    "tool_kg": 2.5,
}

# geometrie uit de parameters (zelfde opbouw als dwd5_parts.stack)
SLIDE_V1 = P.slide_v0 + P.slide_t
SPINDLE_V = SLIDE_V1 + P.jack_mount_t + P.jack_outer[0] / 2 + P.jack_inner[0] / 2 + P.sb_back_t + P.spindle_dv
SPINDLE_Y = P.v_to_y(SPINDLE_V)
TUBE_Y = P.v_to_y(P.tube_v)
REAR_AXLE_Y = -P.robot_wheel_y
FRONT_AXLE_Y = P.robot_wheel_y
WHEELBASE = FRONT_AXLE_Y - REAR_AXLE_Y
TRACK = 2 * P.robot_wheel_x


# ---------------------------------------------------------------------
# Spil en frees
# ---------------------------------------------------------------------
def motor_torque():
    """Nominaal koppel van de tandwielmotor op de uitgaande as (Nm)."""
    return P.motor_P / (2 * math.pi * P.motor_rpm / 60)


def spindle(rpm=P.cutter_rpm):
    """Direct aangedreven spil (klauwkoppeling): koppel = motorkoppel; vermogen bij rpm (de regelaar knijpt de
    spanning, het koppel blijft)."""
    T = motor_torque()
    P_nom = T * 2 * math.pi * rpm / 60
    R = P.cutter_d / 2000.0
    return {"torque_nm": T, "power_nom_w": P_nom, "power_peak_w": P_nom * P.motor_peak, "rpm_max": P.motor_rpm,
            "tip_speed_m_s": 2 * math.pi * R * rpm / 60, "tip_force_n": T / R,
            "mower_tip_m_s": math.pi * P.mower_tip_d / 1000.0 * P.mower_rpm / 60}


def coupling():
    """Klauwkoppeling: piekkoppel van de motor tegen het nominale en maximale koppel van de koppeling."""
    T_peak = motor_torque() * P.motor_peak
    return {"motor_nom_nm": motor_torque(), "motor_peak_nm": T_peak, "coupling_nom_nm": P.jaw_T[0],
            "coupling_max_nm": P.jaw_T[1], "safety_peak_vs_max": P.jaw_T[1] / T_peak}


def chip(plunge=P.plunge_v, rpm=P.cutter_rpm):
    """Insteek per tand per omwenteling (mm): de dikte van de plakjes wortel."""
    return plunge / (rpm / 60.0 * P.cutter_teeth)


def hole_volume(depth=P.depth_std):
    """Volume van het gat (m3)."""
    return math.pi * (P.cutter_d / 2000.0) ** 2 * depth / 1000.0


def cut_power(plunge=P.plunge_v, energy=P.cut_energy_std):
    """Snijvermogen tijdens het insteken (W): specifieke energie x doorsnede x snelheid, plus verlies."""
    area = math.pi * (P.cutter_d / 2000.0) ** 2
    return energy * area * plunge / 1000.0 + P.idle_w


def thrust(depth):
    """Neerwaartse kracht van de frees op de grond (N) bij diepte (mm) onder het maaiveld (geschat)."""
    if depth <= 0:
        return 0.0
    return min(P.thrust_n[0] + P.thrust_n[1] * depth, P.z_force_limit)


def spindle_current(power_w, voltage=48.0):
    return power_w / voltage


# ---------------------------------------------------------------------
# Assen
# ---------------------------------------------------------------------
def z_force_max(motor_T=None):
    """Z-kracht (N) van de steunpoot: F = 2 pi T eta / spoed. Standaard bij het insteektoerental (250 rpm)."""
    T = P.jack_motor_T[0] if motor_T is None else motor_T
    return 2 * math.pi * T * P.jack_eff / (P.jack_lead / 1000.0)


def z_drive(v=P.rapid_z):
    """Slingertoerental (rpm) en beschikbare kracht (N) bij Z-snelheid v (mm/s)."""
    rpm = v / P.jack_lead * 60.0
    T = P.jack_motor_T[1] if rpm > 300 else P.jack_motor_T[0]
    return {"crank_rpm": rpm, "force_n": z_force_max(T), "within_jack_rating": rpm <= P.jack_rpm_max}


def jack_self_locking():
    """Trapeziumspindel: zelfremmend als het rendement van de spindel < 0,5 (spoedhoek < wrijvingshoek)."""
    eta_screw = P.jack_eff / 0.9
    return {"screw_efficiency": eta_screw, "self_locking": eta_screw < 0.5}


def z_guide(F_side=P.side_force, z=-P.depth_std):
    """Binnenbuis in de buitenbuis: speling en doorbuiging bij zijkracht F_side op de frees (frees op diepte z).
    Overlap tussen de PE-bus onder in de buitenbuis en de PE-ring boven op de binnenbuis; vrije lengte van de
    binnenbuis onder de buitenbuis; daaronder de stijve spilbok tot het snijniveau."""
    zc = z
    outer_bottom = P.jack_outer_z[0]
    inner_bottom = zc + P.inner_bottom
    inner_top = inner_bottom + P.inner_L
    overlap = (inner_top - 30.0) - (outer_bottom + P.guide_bush_L / 2.0)     # hart ring tot hart bus
    L1 = outer_bottom - inner_bottom                                           # vrije lengte binnenbuis
    a = inner_bottom - (zc + 40.0)                                             # binnenbuis tot snijniveau
    lever = L1 + a
    w, t = P.jack_inner
    EI = E_STEEL * (w ** 4 - (w - 2 * t) ** 4) / 12.0
    d_tube = F_side * L1 ** 3 / (3 * EI) + F_side * a * L1 ** 2 / (2 * EI)
    slope = F_side * L1 ** 2 / (2 * EI) + F_side * a * L1 / EI
    d_bend = d_tube + slope * a
    d_play = P.jack_play * lever / overlap
    R_bush = F_side * (lever + overlap) / overlap
    return {"overlap_mm": overlap, "free_length_mm": L1, "lever_mm": lever, "bending_mm": d_bend,
            "play_mm": d_play, "total_mm": d_bend + d_play, "bush_force_n": R_bush}


def x_force_max():
    """Houdkracht van de riemaandrijving (N): 5:1 kast, rendement 0,95."""
    r = P.x_pulley_T * P.htd_pitch / (2 * math.pi) / 1000.0
    return P.stepper_T * P.x_gear * 0.95 / r


# ---------------------------------------------------------------------
# Cyclus per plant
# ---------------------------------------------------------------------
def cycle(depth=P.depth_std, dx=333.0):
    """Fasen per plant (s). dx = gemiddelde X-verplaatsing (1/3 van de slag).
    De pot raakt de zode als de freesonderkant nog pot_rim boven de grond is (probe = maaiveld); vanaf daar steekt de
    frees pot_rim + depth in met plunge_v en komt hij draaiend terug tot de pot loskomt (2x zo snel)."""
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
    """Tijd per plant (s); overlap_x = X beweegt al tijdens het rijden naar de plant."""
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
# Aftakas-geleiding
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


def guide(x_moving_kg=None, z_force=P.z_force_limit):
    """Doorbuiging van de aftakasbuizen met de slede op de uiterste stand (overhangende ligger)."""
    m_x = MODEL["x_moving_kg"] if x_moving_kg is None else x_moving_kg
    A, Iz, Iv = lemon_section(P.pto_b, P.pto_h, P.pto_t)
    a = P.x_max + P.sleeve_pitch / 2 - P.hs_x          # uitkraging tot het uiterste hulscentrum
    L = 2 * P.hs_x                                      # tussen de steunen
    F_z = m_x * G_ACC / 2                               # gewicht per buis
    d_z = F_z * a ** 2 * (a + L) / (3 * E_STEEL * Iz)
    lever = SPINDLE_V - P.tube_v                        # spilhart achter de buizen
    F_c = z_force * lever / (P.xbar_z[1] - P.xbar_z[0])  # koppel om de x-as -> kracht in v op elke buis
    d_v = F_c * a ** 2 * (a + L) / (3 * E_STEEL * Iv)
    twist = math.degrees(2 * d_v / (P.xbar_z[1] - P.xbar_z[0]))
    mu = 0.15                                           # gesmeerd staal op de PE-strips
    F_fr = mu * (2 * F_c + m_x * G_ACC * 0.5)
    tubes_kg = 2 * A * P.xbar_L * 7.85e-6
    return {"area_mm2": A, "I_bend_z_mm4": Iz, "I_bend_v_mm4": Iv, "overhang_mm": a, "defl_z_mm": d_z,
            "lever_mm": lever, "force_v_per_tube_n": F_c, "defl_v_mm": d_v, "twist_deg": twist,
            "friction_n": F_fr, "accel_m_s2": (x_force_max() - F_fr) / m_x, "tubes_kg": tubes_kg}


# ---------------------------------------------------------------------
# Spilas
# ---------------------------------------------------------------------
def shaft(F=P.side_force):
    """Spilas O20 in 2x UCP 204, overhang in een buis 42,4 x 4: doorbuiging (arbeidsmethode, getrapte EI),
    spanningen, lagerkrachten bij zijkracht F op het snijniveau, en kritisch toerental."""
    d = P.shaft_d
    EI_s = E_STEEL * math.pi * d ** 4 / 64
    D, t = P.spindle_tube
    EI_t = E_STEEL * math.pi * (D ** 4 - (D - 2 * t) ** 4) / 64
    a = P.bearing_lo - 40.0                 # hart onderste UCP 204 tot snijniveau (40 boven de tandonderkant)
    a_t = P.spindle_tube_top - 40.0         # tot de bovenkant van de buis: daarboven alleen O20
    L = P.bearing_dist
    n = 400
    ds = a / n
    integral = sum(((i + 0.5) * ds) ** 2 / (EI_t if (i + 0.5) * ds < a_t else EI_s) for i in range(n)) * ds
    delta = F * (integral + a ** 2 * L / (3 * EI_s))
    sigma_shaft = F * a / (math.pi * d ** 3 / 32)
    sigma_tube = F * a_t / (math.pi * (D ** 4 - (D - 2 * t) ** 4) / (32 * D))
    k = F / delta * 1000.0
    n_cr = math.sqrt(k / MODEL["tool_kg"]) * 60 / (2 * math.pi)
    return {"overhang_mm": a, "defl_mm": delta, "stress_shaft_at_bearing_mpa": sigma_shaft,
            "stress_tube_mpa": sigma_tube, "bearing_lower_n": F * (a + L) / L, "bearing_upper_n": F * a / L,
            "critical_rpm": n_cr, "cutter_pct_of_critical": 100.0 * P.cutter_rpm / n_cr}


# ---------------------------------------------------------------------
# Robot: asbelasting en aanbouwbok
# ---------------------------------------------------------------------
def axle_loads(x=None, soil_force=0.0, pot_on_ground=False, robot_kg=P.robot_kg, robot_cg_y=P.robot_cg_y):
    """Wiellasten (N) bij X-stand x en een opwaartse kracht van de grond op de frees (soil_force, N).
    Geeft dict met voor/achter en de 4 wielen (RL, RR, FL, FR). Statisch, vlakke grond.
    pot_on_ground: de pot rust met zijn eigen gewicht op de grond (dat gewicht draagt de robot dan niet)."""
    x = MODEL["x_moving_cg"][0] if x is None else x
    m_fix = MODEL["implement_kg"] - MODEL["x_moving_kg"]
    cg_i = MODEL["implement_cg"]
    cg_x = MODEL["x_moving_cg"]
    # vast deel: zwaartepunt volgt uit het geheel minus het bewegende deel (beide gemeten bij x 150)
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
    # verdeling links/rechts: per as evenredig (starre robot, statisch bepaald benaderd)
    lat = Mx / TRACK                                    # rechts zoveel zwaarder dan het gemiddelde (beide assen)
    share = front / W if W else 0.5                     # verdeeld over de assen naar hun aandeel
    wheels = {"RL": rear / 2 - lat * (1 - share), "RR": rear / 2 + lat * (1 - share),
              "FL": front / 2 - lat * share, "FR": front / 2 + lat * share}
    return {"total_n": W, "front_n": front, "rear_n": rear, "front_kg": front / G_ACC, "rear_kg": rear / G_ACC,
            "wheels_kg": {k: v / G_ACC for k, v in wheels.items()}}


def max_down_force(x=0.0, min_kg=20.0):
    """Grootste neerwaartse kracht van de frees (N) tot het lichtste wiel nog min_kg draagt.
    De frees zit achter de achteras: de grondkracht licht de achterwielen en drukt de voorwielen."""
    lo, hi = 0.0, 5000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if min(axle_loads(x, mid, True)["wheels_kg"].values()) > min_kg:
            lo = mid
        else:
            hi = mid
    return lo


def headstock_bolts(accel_g=2.0, z_force=P.z_force_limit):
    """Aanbouwbok: trekkracht in de M10-bouten door de onderbalk (N per bout).
    Het moment van het werktuig om de onderkant van de achterplaat (bovenkant klemplaat) wordt opgenomen door de
    bouten (arm = hart bout tot achterkant balk + halve balkhoogte, vereenvoudigd). accel_g = stootfactor bij rijden."""
    m = MODEL["implement_kg"]
    cg_y = MODEL["implement_cg"][1]
    arm_load = (P.robot_beam_rear_face - cg_y)              # zwaartepunt achter de balk
    M = m * G_ACC * accel_g * arm_load / 1000.0             # Nm, beide kanten samen
    M_z = z_force * (P.robot_beam_rear_face - SPINDLE_Y) / 1000.0
    lever = abs(P.hs_bolt_v) + 0.0                           # bout 20 mm voor de achterkant van de balk
    lever_v = P.robot_lower_beam_z[1] - P.robot_lower_beam_z[0] + P.hs_plate_t   # bovenplaat tot onderkant achterplaat
    # bouten (4 stuks) trekken de bovenplaat neer; de achterplaat drukt onderaan tegen de balk
    F_bolt = (M + M_z) * 1000.0 / (lever + lever_v) / 4.0
    return {"moment_nm": M, "moment_z_force_nm": M_z, "bolt_tension_n": F_bolt,
            "m10_8_8_proof_n": 33700.0, "safety": 33700.0 / F_bolt if F_bolt else float("inf")}


def tip_lateral(x=P.x_max):
    """Zijdelingse stabiliteit: afstand (mm) van het totale zwaartepunt tot de wiellijn bij de X-stand x."""
    m_r = P.robot_kg
    m_i = MODEL["implement_kg"]
    m_x = MODEL["x_moving_kg"]
    cx = (m_x * x) / (m_r + m_i)
    return {"cg_x_mm": cx, "margin_to_wheel_mm": P.robot_wheel_x - abs(cx)}


# ---------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------
def report(model=None):
    if model:
        MODEL.update(model)
    sp = spindle()
    sh = shaft()
    gd = guide()
    lift = axle_loads(MODEL["x_moving_cg"][0])
    work = axle_loads(P.x_max, thrust(P.depth_std), True)
    hb = headstock_bolts()
    out = {
        "spindle": "%.0f rpm (max %.0f), O%.0f: tip %.1f m/s, %.1f Nm, %.0f W nominal / %.0f W peak; mowing %.0f m/s" % (
            P.cutter_rpm, sp["rpm_max"], P.cutter_d, sp["tip_speed_m_s"], sp["torque_nm"], sp["power_nom_w"],
            sp["power_peak_w"], sp["mower_tip_m_s"]),
        "coupling": {k: round(v, 2) for k, v in coupling().items()},
        "chip_mm": round(chip(), 2),
        "hole_l": round(hole_volume() * 1000, 2),
        "cut_power_w": (round(cut_power(energy=P.cut_energy[0])), round(cut_power()), round(cut_power(energy=P.cut_energy[1]))),
        "z_force_max_n (plunge, rapid)": (round(z_force_max()), round(z_drive()["force_n"])),
        "jack_crank_rpm_rapid": round(z_drive()["crank_rpm"]),
        "jack": {k: (round(v, 2) if isinstance(v, float) else v) for k, v in jack_self_locking().items()},
        "z_guide": {k: round(v, 2) for k, v in z_guide().items()},
        "x_force_max_n": round(x_force_max()),
        "cycle_s": {k: round(v, 1) for k, v in cycle()},
        "cycle_total_s": round(cycle_time(), 1),
        "plants_per_hour": round(plants_per_hour()),
        "plants_per_hour_x_overlap": round(plants_per_hour(overlap_x=True)),
        "energy_wh_per_plant": round(energy_per_plant(), 2),
        "shaft": {k: round(v, 2) for k, v in sh.items()},
        "guide": {k: round(v, 2) for k, v in gd.items()},
        "spindle_y": round(SPINDLE_Y),
        "axle_kg_driving (front, rear)": (round(lift["front_kg"]), round(lift["rear_kg"])),
        "axle_kg_working_x_max (front, rear)": (round(work["front_kg"]), round(work["rear_kg"])),
        "wheels_kg_working_x_max": {k: round(v) for k, v in work["wheels_kg"].items()},
        "axle_kg_driving_battery_forward (front, rear)": tuple(round(axle_loads(robot_cg_y=P.battery_forward_cg_y)[k])
                                                               for k in ("front_kg", "rear_kg")),
        "lightest_wheel_kg_driving_x_max": round(min(axle_loads(P.x_max)["wheels_kg"].values()), 1),
        "lightest_wheel_kg_driving_x_max_battery_forward": round(min(axle_loads(
            P.x_max, robot_cg_y=P.battery_forward_cg_y)["wheels_kg"].values()), 1),
        "axle_kg_robot_only (front, rear)": (round(P.robot_kg * (P.robot_cg_y - REAR_AXLE_Y) / WHEELBASE),
                                             round(P.robot_kg * (FRONT_AXLE_Y - P.robot_cg_y) / WHEELBASE)),
        "max_down_force_n (x 0, lightest wheel >= 20 kg)": round(max_down_force()),
        "max_down_force_n (x max)": round(max_down_force(P.x_max)),
        "headstock_bolt_n (2 g)": round(hb["bolt_tension_n"]),
        "headstock_bolt_safety": round(hb["safety"], 1),
        "lateral_cg_margin_mm": round(tip_lateral()["margin_to_wheel_mm"]),
    }
    return out
