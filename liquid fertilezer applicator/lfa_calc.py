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
    "implement_kg": 105.7,      # heel werktuig incl. aanbouwbok, pomp, actuator, slangen
    "implement_cg_y": -484.0,   # zwaartepunt heel werktuig, werktuig-y
    "moving_kg": 82.8,          # deel dat meegaat met heffen (toolbar + elementen + aandrijving)
    "moving_cg_y": -592.0,
    "arm_kg": 7.02,             # zwenkende arm van 1 element (vork, schijf, ringen, mes, buisje)
    "arm_cg_y": -736.0,
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


def dose_l_ha(z_wheel, z_jack, tube_id=P.pump_tube_id):
    i = z_wheel / float(z_jack)
    per_m = i * pump_ml_per_rev(tube_id) / (P.gw_rolling_circ / 1000.0)    # ml per meter per rij
    return per_m * 10.0 / (P.row_spacing / 1000.0)                          # ml/m -> l/ha


def dose_table():
    rows = []
    for tube in (4.8, 6.4, 8.0):
        for zw, zj in ((15, 24), (20, 18), (24, 15), (30, 15), (36, 15), (40, 12)):
            rows.append((tube, zw, zj, round(zw / float(zj), 2), round(dose_l_ha(zw, zj, tube))))
    return rows


def flow_l_min(dose, speed_m_s):
    return dose * P.row_spacing / 1000.0 * speed_m_s / 10000.0 * 60.0


def pump_rpm(z_wheel, z_jack, speed_m_s):
    return z_wheel / float(z_jack) * speed_m_s / (P.gw_rolling_circ / 1000.0) * 60.0


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


def float_equilibrium(wheel_n=150.0, moving_kg=None, extra_n=0.0):
    """Zweefstand op vlakke grond: armhoek waarbij 5 elementen + loopwiel het balkgewicht (+ extra_n,
    bijv. gasveren) dragen. Geeft (armhoek, kracht per element, balk hoger dan ontwerp in mm)."""
    moving_kg = MODEL["moving_kg"] if moving_kg is None else moving_kg
    need = (moving_kg * G_ACC + extra_n - wheel_n) / len(P.row_x)
    lo, hi = -20.0, P.unit_drop_deg
    if unit_downforce(drop=hi)[0] > need:
        return hi, unit_downforce(drop=hi)[0], -disc_dz(hi)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if unit_downforce(drop=mid)[0] > need:
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
def chain_links():
    p = P.chain_pitch
    c = math.hypot(*P.gw_wheel_rel)
    return 2 * c / p + (P.z_jack + P.z_wheel) / 2.0 + ((P.z_wheel - P.z_jack) / (2 * math.pi)) ** 2 * p / c


def report(model=None):
    if model:
        MODEL.update(model)
    out = {}
    out["work_width_m"] = P.work_width / 1000.0
    out["rows"] = len(P.row_x)
    out["work_depth_mm"] = P.work_depth
    out["pump_ml_rev_6.4"] = round(pump_ml_per_rev(), 2)
    out["ratio_default"] = P.z_wheel / float(P.z_jack)
    out["dose_default_l_ha"] = round(dose_l_ha(P.z_wheel, P.z_jack))
    out["flow_row_l_min_1ms"] = round(flow_l_min(out["dose_default_l_ha"], 1.0), 2)
    out["pump_rpm_1ms"] = round(pump_rpm(P.z_wheel, P.z_jack, 1.0))
    out["chain_links"] = round(chain_links(), 1)
    f, fs, sl, lever = unit_downforce()
    out["spring_len_design"] = round(sl, 1)
    out["spring_force_design"] = round(fs)
    out["strut_lever"] = round(lever, 1)
    a_eq, f_eq, h_eq = float_equilibrium()
    out["float_arm_angle_deg"] = round(a_eq, 1)
    out["float_unit_force_N"] = round(f_eq)
    out["float_bar_above_design_mm"] = round(h_eq, 1)
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
