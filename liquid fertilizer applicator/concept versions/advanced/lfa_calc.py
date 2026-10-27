"""Berekeningen voor de onderbouwing (puur Python, geen FreeCAD nodig).

Gebruik:  import lfa_calc; lfa_calc.report()
Massa's van het werktuig komen uit het FreeCAD-model (build_lfa.mass_properties) en worden als
argument meegegeven; zonder argument worden de waarden uit de laatste meting gebruikt.
"""
import math

import lfa_params as P

G_ACC = 9.81

# laatste meting uit het model (build_lfa.mass_properties: staal 7850 kg/m3, gekochte delen als vaste massa)
MODEL = {
    "implement_kg": 115.5,      # heel werktuig incl. aanbouwbok, pomp met motor, actuator, slangen, 5 aandrukwielen
    "implement_cg_y": -555.0,   # zwaartepunt heel werktuig, werktuig-y
    "moving_kg": 91.7,          # deel dat meegaat met heffen (toolbar + elementen + pomp met motor)
    "moving_cg_y": -676.0,
    "arm_kg": 8.14,             # zwenkende arm van 1 element (vork, schijf, ringen, mes, buisje, as + veren aandrukwiel)
    "arm_cg_y": -770.0,
    "pw_kg": 2.52,              # sleeparm aandrukwiel (strippen, wiel, as, veerbenen), zonder de delen op de vork
    "pw_cg": (-1096.0, 138.0),  # zwaartepunt sleeparm (y, z), armhoek 0
}

# aannames robot (niet gemeten: invullen zodra bekend)
ROBOT = {
    "robot_kg": 150.0,          # robot zonder tank
    "robot_cg_from_rear": 500.0,  # mm voor de achteras
    "tank_l": 150.0,
    "liquid_density": 1.2,      # kg/l (spuiwater/UAN 1,1-1,3)
    "tank_cg_from_rear": 150.0,  # tank zo dicht mogelijk bij de achteras
    "wheelbase": 1000.0,
}


def rot_yz(point, angle_deg, center):
    a = math.radians(angle_deg)
    dy, dz = point[0] - center[0], point[1] - center[1]
    return (center[0] + dy * math.cos(a) - dz * math.sin(a), center[1] + dy * math.sin(a) + dz * math.cos(a))


# ---------------------------------------------------------------------
# Dosering
# ---------------------------------------------------------------------
def pump_ml_per_rev(tube_id=P.pump_tube_id):
    area = math.pi * tube_id ** 2 / 4.0
    return 2.0 * math.pi * P.pump_roller_r * area * P.pump_fill / 1000.0


def pump_rpm(dose=P.dose_l_ha, speed_m_s=1.0, tube_id=P.pump_tube_id):
    """Pomptoerental (omw/min) dat de besturing instelt: n = 6 x dosis [l/ha] x rijafstand [m] x v [m/s] / V [ml]."""
    return 6.0 * dose * (P.row_spacing / 1000.0) * speed_m_s / pump_ml_per_rev(tube_id)


def dose_at_rpm(rpm, speed_m_s=1.0, tube_id=P.pump_tube_id):
    return rpm * pump_ml_per_rev(tube_id) / (6.0 * (P.row_spacing / 1000.0) * speed_m_s)


def dose_table(speeds=(0.5, 1.0, 1.5)):
    """Doseerbereik (l/ha) per pompslang en rijsnelheid, tussen pm_rpm_min en pm_rpm_max van de pompmotor."""
    rows = []
    for tube in (4.8, 6.4, 8.0):
        for v in speeds:
            rows.append((tube, v, round(dose_at_rpm(P.pm_rpm_min, v, tube)), round(dose_at_rpm(P.pm_rpm_max, v, tube))))
    return rows


def flow_l_min(dose, speed_m_s):
    return dose * P.row_spacing / 1000.0 * speed_m_s / 10000.0 * 60.0


def pump_power_w(dose=P.dose_l_ha, speed_m_s=1.0, torque_nm=P.pm_torque):
    """Asvermogen van de pompmotor (W) bij het aangenomen pompkoppel."""
    return torque_nm * pump_rpm(dose, speed_m_s) * 2.0 * math.pi / 60.0


# ---------------------------------------------------------------------
# Veerpoot en neerdruk per element
# ---------------------------------------------------------------------
def strut_geometry(drop=0.0):
    pivot = P.u_pivot
    lug = rot_yz((pivot[0] + P.u_lug_rel[0], pivot[1] + P.u_lug_rel[1]), drop, pivot)
    anchor = (pivot[0] + P.u_anchor_rel[0], pivot[1] + P.u_anchor_rel[1])
    dy, dz = anchor[0] - lug[0], anchor[1] - lug[1]
    dist = math.hypot(dy, dz)
    u = (dy / dist, dz / dist)
    plate_bot = (anchor[1] - P.u_anchor_plate[2] / 2.0 - lug[1]) / u[1]
    spring_len = plate_bot - (P.seat_offset + 4.0) - 0.5
    lever = abs((pivot[0] - lug[0]) * u[1] - (pivot[1] - lug[1]) * u[0])
    return spring_len, lever


def unit_downforce(preload_shift=0.0, drop=0.0, arm_kg=None, arm_cg_y=None):
    """Kracht onder de diepteringen (N). preload_shift = veerschotel hoger zetten (mm)."""
    arm_kg = MODEL["arm_kg"] if arm_kg is None else arm_kg
    arm_cg_y = MODEL["arm_cg_y"] if arm_cg_y is None else arm_cg_y
    spring_len, lever = strut_geometry(drop)
    f_spring = max(0.0, P.spring_rate * (P.spring_free - spring_len + preload_shift))
    disc_lever = abs(P.disc_y - P.u_pivot[0])
    f_weight = arm_kg * G_ACC * abs(arm_cg_y - P.u_pivot[0]) / disc_lever
    return f_spring * lever / disc_lever + f_weight, f_spring, spring_len, lever


def disc_dz(drop):
    """Hoogteverandering van de schijfas t.o.v. de balk bij armhoek drop (mm, + = omhoog)."""
    return rot_yz((P.disc_y, P.disc_z), drop, P.u_pivot)[1] - P.disc_z


# ---------------------------------------------------------------------
# Aandrukwiel: sleeparm op de element-arm met 2 torsieveren
# ---------------------------------------------------------------------
def pw_spring_rate():
    """Beide torsieveren samen (Nmm per graad): k = E d^4 / (64 D n) per veer."""
    k_rad = P.pw_spring_e * P.pw_spring_wire ** 4 / (64.0 * P.pw_spring_dm * P.pw_spring_coils)
    return 2.0 * k_rad * math.pi / 180.0


def pw_preload(setting=None):
    return P.pw_preload_deg[P.pw_preload_index if setting is None else setting]


def pw_spring_stress(beta, setting=None):
    """Buigspanning in de draad (MPa) bij sleeparmhoek beta, met correctiefactor voor de kromming."""
    c = P.pw_spring_dm / P.pw_spring_wire
    ki = (4 * c * c - c - 1) / (4 * c * (c - 1))
    torque = pw_spring_rate() / 2.0 * max(0.0, pw_preload(setting) - beta)
    return ki * 32.0 * torque / (math.pi * P.pw_spring_wire ** 3)


def pw_points(drop, beta):
    """Draaipunt, wielas en zwaartepunt van de sleeparm (y, z) in het balkframe."""
    q0 = P.pw_pivot
    w0 = (q0[0] + P.pw_wheel_rel[0], q0[1] + P.pw_wheel_rel[1])
    cg0 = MODEL["pw_cg"]
    q = rot_yz(q0, drop, P.u_pivot)
    w = rot_yz(rot_yz(w0, beta, q0), drop, P.u_pivot)
    cg = rot_yz(rot_yz(cg0, beta, q0), drop, P.u_pivot)
    return q, w, cg


def press_beta(drop, bar_dz):
    """Sleeparmhoek waarbij het wiel de vlakke grond raakt (balk bar_dz boven de ontwerphoogte).
    Geeft (hoek, contact): zonder contact hangt de arm op de onderaanslag."""
    r = P.pw_d / 2.0

    def gap(b):
        return pw_points(drop, b)[1][1] + bar_dz - r
    lo, hi = P.pw_up_deg, P.pw_down_deg
    if gap(hi) >= 0.0:
        return hi, False
    if gap(lo) <= 0.0:
        return lo, True
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if gap(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), True


def press_force(drop=0.0, beta=0.0, setting=None):
    """Kracht van het aandrukwiel op de grond (N): veermoment + gewicht sleeparm, gedeeld door de arm."""
    if not P.press_wheel:
        return 0.0
    q, w, cg = pw_points(drop, beta)
    torque = pw_spring_rate() * max(0.0, pw_preload(setting) - beta)
    return (torque + MODEL["pw_kg"] * G_ACC * abs(cg[0] - q[0])) / abs(w[0] - q[0])


def unit_forces(drop=0.0, beta=None, setting=None, bar_dz=None, press_contact=True):
    """Grondkrachten van een element (N): schijf (diepteringen), aandrukwiel en totaal.

    Momentenevenwicht om het draaipunt van de element-arm: de kracht op het aandrukwiel werkt met de lange arm
    (draaipunt - wiel) tegen de veerpoot in, het gewicht van de sleeparm erbij. beta None = wiel op vlakke grond,
    met de balk bar_dz boven de ontwerphoogte (standaard: diepteringen op de grond)."""
    fd = unit_downforce(drop=drop)[0]
    if not P.press_wheel:
        return {"disc": fd, "press": 0.0, "total": fd, "beta": None}
    if beta is None:
        dz = -disc_dz(drop) if bar_dz is None else bar_dz
        beta, press_contact = press_beta(drop, dz)
    fp = press_force(drop, beta, setting) if press_contact else 0.0
    q, w, cg = pw_points(drop, beta)
    disc_lever = abs(P.disc_y - P.u_pivot[0])
    fd += (MODEL["pw_kg"] * G_ACC * abs(cg[0] - P.u_pivot[0]) - fp * abs(w[0] - P.u_pivot[0])) / disc_lever
    return {"disc": fd, "press": fp, "total": fd + fp, "beta": beta}


def press_carry_force(drop):
    """Element rust alleen op het aandrukwiel (sleeparm op de bovenaanslag, schijf los): kracht onder het wiel (N)."""
    fd0 = unit_downforce(drop=drop)[0]
    q, w, cg = pw_points(drop, P.pw_up_deg)
    disc_lever = abs(P.disc_y - P.u_pivot[0])
    return (fd0 * disc_lever + MODEL["pw_kg"] * G_ACC * abs(cg[0] - P.u_pivot[0])) / abs(w[0] - P.u_pivot[0])


def lifted_press_clearance():
    """Bodemvrijheid van het aandrukwiel bij hefhoogte lift_height (element en sleeparm op hun onderaanslag)."""
    q, w, cg = pw_points(P.unit_drop_deg, P.pw_down_deg)
    return w[1] + P.lift_height - P.pw_d / 2.0


def float_equilibrium(wheel_n=0.0, moving_kg=None, extra_n=0.0, setting=None):
    """Zweefstand op vlakke grond: armhoek waarbij 5 elementen (schijf + aandrukwiel) het balkgewicht (+ extra_n, bijv.
    gasveren; - wheel_n van een eventueel extra steunwiel) dragen. Geeft (armhoek, kracht per element, balk hoger dan
    ontwerp in mm)."""
    moving_kg = MODEL["moving_kg"] if moving_kg is None else moving_kg
    need = (moving_kg * G_ACC + extra_n - wheel_n) / len(P.row_x)

    def total(a):
        return unit_forces(drop=a, setting=setting)["total"]
    lo, hi = -20.0, P.unit_drop_deg
    if total(hi) > need:
        return hi, total(hi), -disc_dz(hi)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if total(mid) > need:
            lo = mid
        else:
            hi = mid
    a = 0.5 * (lo + hi)
    return a, need, -disc_dz(a)


def stone_lift_spring_len(lift_mm=60.0):
    disc_lever = abs(P.disc_y - P.u_pivot[0])
    angle = -math.degrees(math.asin(lift_mm / disc_lever))
    return strut_geometry(angle)[0]


# ---------------------------------------------------------------------
# Heffen
# ---------------------------------------------------------------------
def lift_state(lift):
    theta = math.asin(lift / P.link_length)
    return P.link_length * (1.0 - math.cos(theta)), lift


def actuator_len(lift):
    # afstand onderkant langgat - onderste pen (= actuatorlengte als de pen onderin het langgat ligt)
    dy, dz = lift_state(lift)
    return math.hypot(P.act_b[0] + dy - P.act_a[0], P.act_b[1] + dz - P.act_a[1])


def lift_for_len(length):
    lo, hi = -0.45 * P.link_length, 0.9 * P.link_length
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if actuator_len(mid) > length:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def float_range():
    """Zweefbereik van de balk in werkstand (actuator volledig uit): (laagste, hoogste) hefhoogte."""
    return lift_for_len(P.act_extended), lift_for_len(P.act_extended - P.act_slot)


def actuator_ratio(lift=0.0):
    # |dl/dh|: lengteverandering actuator per mm hefhoogte (virtuele arbeid: F_vert = F_act * ratio)
    return abs(actuator_len(lift + 1.0) - actuator_len(lift - 1.0)) / 2.0


# ---------------------------------------------------------------------
# Gewichtsverdeling robot
# ---------------------------------------------------------------------
def axle_loads(soil_force, implement_kg=None, implement_cg_y=None, robot=None, lifted=False):
    """Asbelasting robot (N): (voor, achter).

    soil_force = totale opwaartse kracht van de grond op het werktuig (elementen + loopwiel), 0 als geheven.
    Afstanden achter de achteras zijn positief.
    """
    r = dict(ROBOT)
    if robot:
        r.update(robot)
    implement_kg = MODEL["implement_kg"] if implement_kg is None else implement_kg
    implement_cg_y = MODEL["implement_cg_y"] if implement_cg_y is None else implement_cg_y
    if lifted:
        implement_cg_y += lift_state(P.lift_height)[0] * MODEL["moving_kg"] / implement_kg
    w_robot = r["robot_kg"] * G_ACC
    w_tank = r["tank_l"] * r["liquid_density"] * G_ACC
    w_impl = implement_kg * G_ACC
    d_cg = (P.robot_wheel_y - implement_cg_y) / 1000.0
    d_soil = (P.robot_wheel_y - P.disc_y) / 1000.0
    L = r["wheelbase"] / 1000.0
    m_front = (w_robot * r["robot_cg_from_rear"] / 1000.0 + w_tank * r["tank_cg_from_rear"] / 1000.0
               - w_impl * d_cg + soil_force * d_soil)
    n_front = m_front / L
    n_rear = w_robot + w_tank + w_impl - soil_force - n_front
    return n_front, n_rear


def max_soil_force(min_rear_n=600.0, **kw):
    lo, hi = 0.0, 5000.0
    for _ in range(50):
        mid = (lo + hi) / 2.0
        if axle_loads(mid, **kw)[1] > min_rear_n:
            lo = mid
        else:
            hi = mid
    return lo


# ---------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------
def report(model=None):
    if model:
        MODEL.update(model)
    out = {}
    out["work_width_m"] = P.work_width / 1000.0
    out["rows"] = len(P.row_x)
    out["work_depth_mm"] = P.work_depth
    out["pump_ml_rev_6.4"] = round(pump_ml_per_rev(), 2)
    out["dose_default_l_ha"] = P.dose_l_ha
    out["flow_row_l_min_1ms"] = round(flow_l_min(out["dose_default_l_ha"], 1.0), 2)
    out["pump_rpm_1ms"] = round(pump_rpm(P.dose_l_ha, 1.0))
    out["pump_power_W_1ms"] = round(pump_power_w(P.dose_l_ha, 1.0))
    out["dose_range_1ms_l_ha"] = (round(dose_at_rpm(P.pm_rpm_min)), round(dose_at_rpm(P.pm_rpm_max)))
    out["speed_max_at_dose_m_s"] = round(P.pm_rpm_max / pump_rpm(P.dose_l_ha, 1.0), 2)
    f, fs, sl, lever = unit_downforce()
    out["spring_len_design"] = round(sl, 1)
    out["spring_force_design"] = round(fs)
    out["strut_lever"] = round(lever, 1)
    a_eq, f_eq, h_eq = float_equilibrium()
    out["float_arm_angle_deg"] = round(a_eq, 1)
    out["float_unit_force_N"] = round(f_eq)
    out["float_bar_above_design_mm"] = round(h_eq, 1)
    if P.press_wheel:
        uf = unit_forces(drop=a_eq)
        out["float_disc_force_N"] = round(uf["disc"])
        out["float_press_force_N"] = round(uf["press"])
        out["float_press_arm_deg"] = round(uf["beta"], 1)
        out["press_spring_rate_Nmm_deg"] = round(pw_spring_rate(), 1)
        settings = []
        for i in range(len(P.pw_preload_deg)):
            a_i = float_equilibrium(setting=i)[0]
            f_i = unit_forces(drop=a_i, setting=i)
            settings.append((round(f_i["press"]), round(f_i["disc"]), round(a_i, 1)))
        out["press_settings_press_disc_arm"] = settings
        out["press_force_range_N"] = (round(press_force(a_eq, P.pw_down_deg)), round(press_force(a_eq, -20.0)))
        out["press_spring_stress_max_MPa"] = round(pw_spring_stress(P.pw_up_deg, len(P.pw_preload_deg) - 1))
        out["press_clearance_lifted_mm"] = round(lifted_press_clearance(), 1)
    lo, hi = float_range()
    out["float_range_mm"] = (round(lo, 1), round(hi, 1))
    out["unit_down_travel_mm"] = round(-disc_dz(P.unit_drop_deg), 1)
    out["spring_len_stone_60mm"] = round(stone_lift_spring_len(60.0), 1)
    out["solid_len"] = round(P.spring_wire * 10.0, 1)
    out["act_len_work"] = P.act_extended
    out["act_len_lifted"] = round(actuator_len(P.lift_height), 1)
    out["act_ratio_lifted"] = round(actuator_ratio(P.lift_height - 1.0), 2)
    w_mov = MODEL["moving_kg"] * G_ACC
    out["actuator_lift_N"] = round(w_mov * 1.3 / actuator_ratio(P.lift_height - 1.0))
    soil = w_mov                     # zweefstand: de grond draagt het bewegende deel
    out["soil_force_N"] = round(soil)
    nf, nr = axle_loads(soil)
    out["axle_front_N"] = round(nf)
    out["axle_rear_N"] = round(nr)
    nf, nr = axle_loads(0.0, lifted=True)
    out["axle_front_lifted_N"] = round(nf)
    out["axle_rear_lifted_N"] = round(nr)
    r = ROBOT
    out["robot_total_N"] = round((r["robot_kg"] + r["tank_l"] * r["liquid_density"]) * G_ACC)
    out["max_soil_force_N"] = round(max_soil_force())
    out["capacity_ha_h_1ms"] = round(P.work_width / 1000.0 * 1.0 * 3600 / 10000.0, 2)
    return out


if __name__ == "__main__":
    for k, v in report().items():
        print(k, v)
    for row in dose_table():
        print(row)
