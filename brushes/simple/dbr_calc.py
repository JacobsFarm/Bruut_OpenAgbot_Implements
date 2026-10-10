"""Berekeningen voor de schotelborstels (puur Python, geen FreeCAD nodig).

Gebruik:  import dbr_calc; dbr_calc.report("double_750")      (of "double_650", "single_850")
Massa's van het werktuig komen uit het FreeCAD-model (build_dbr.mass_properties), zie MODEL.
Krachten in robotcoordinaten: x = rechts, y = voor; de robot rijdt bij het borstelen naar -y.
Draairichting: omega > 0 = linksom van boven gezien. Linker borstel linksom = voorkant naar binnen (wiers).
"""
import math

import dbr_params as P

G_ACC = 9.81

# laatste meting uit het model (build_dbr.mass_properties, staal 7850 kg/m3, motor 13 kg, kast 3,5 kg),
# zonder contragewicht. "contact_y": midden van de contactstrook op de vloer (build_dbr.floor_contact)
MODEL = {
    "double_650": {"kg": 103.9, "cg": (0.0, -941.0, 346.0), "brush_kg": 9.6, "contact_y": -1404.0},
    "double_750": {"kg": 110.3, "cg": (0.0, -950.0, 343.0), "brush_kg": 12.8, "contact_y": -1453.0},
    "single_850": {"kg": 74.8, "cg": (15.0, -897.0, 377.0), "brush_kg": 16.5, "contact_y": -1502.0},
}
BALLAST = {"kg": 40.2, "cg": (0.0, 575.0, 712.0)}
MOUNT = {"kg": 26.8 + 5.0}       # toolbar, hangers, regelkast (alles behalve de units)

# robot 4WD rijklaar, uit agbots/agbot comparison/weight_traction.json (geschat, niet gewogen)
ROBOT = {
    "robot_kg": 161.5,
    "robot_cg": (0.0, 95.0, 543.0),
    "mu_tire": 0.6,             # rubber op betonvloer / erfverharding
    "c_rr": 0.03,               # rolweerstand op beton
    "k_corner": 0.12,           # bandstijfheid: zijkracht per graad slip, per N wiellast (als bij de voerschuif)
    "front_min": 0.20,          # minimaal aandeel van het gewicht op de stuurwielen (agbot comparison)
    "battery_wh": 2400.0,       # 48 V 50 Ah
    "drive_w": 250.0,           # rijden op beton bij 0,5 m/s, geschat
}
CONTACT_HALF_DEG = 35.0         # halve hoek van de contactboog aan de voorkant (model: ca. 23 graden bij 2 mm indrukking)

WHEELS = (("RL", -P.robot_wheel_x, P.robot_axle_y), ("RR", P.robot_wheel_x, P.robot_axle_y),
          ("FL", -P.robot_wheel_x, -P.robot_axle_y), ("FR", P.robot_wheel_x, -P.robot_axle_y))
HALF_BASE = -P.robot_axle_y          # 500
HALF_TRACK = P.robot_wheel_x         # 375


def cfg(name):
    return P.config(name)


# ---------------------------------------------------------------------
# Borstel
# ---------------------------------------------------------------------
def kinematics(name, rpm=None):
    c = cfg(name)
    rpm = c["rpm"] if rpm is None else rpm
    omega = rpm * 2.0 * math.pi / 60.0
    v_tip = omega * c["R"] / 1000.0
    return {"rpm": rpm, "omega": omega, "v_tip": v_tip,
            "throw_m": v_tip ** 2 / (2.0 * P.mu_material * G_ACC),       # glijweg van los materiaal na het loslaten
            "tip_to_drive": v_tip / P.drive_speed}


def material_flow(name, mode="spread", v=P.drive_speed, layer=P.layer_kg_m2):
    """Materiaal dat de borstels per seconde oppakken (kg/s), per borstel en totaal, en de wiers (kg/m)."""
    c = cfg(name)
    xs = P.centres_x(c, mode)
    width = c["d"] / 1000.0
    m_brush = layer * width * v
    swept = c["n"] * width
    if c["n"] == 2:
        swept = (xs[1] - xs[0] + c["d"]) / 1000.0        # incl. de ruimte ertussen (ligt er ook nog)
    return {"kg_s_brush": m_brush, "kg_s_total": c["n"] * m_brush, "swept_m": swept,
            "windrow_kg_m": layer * swept, "windrow_m3_m": layer * swept / 250.0}


def torque(name, rpm=None, layer=P.layer_kg_m2, v=P.drive_speed, m_dot=None):
    """Askoppel (Nm) per borstel: wrijving van het haar op de vloer + materiaal verplaatsen + nullast.
    m_dot = materiaal dat de borstel per seconde oppakt (kg/s); standaard uit de laag en de rijsnelheid."""
    c = cfg(name)
    k = kinematics(name, rpm)
    r_c = P.r_contact * c["R"] / 1000.0
    t_floor = P.mu_bristle * c["F_c"] * r_c if k["rpm"] > 0 else 0.0
    m = material_flow(name, v=v, layer=layer)["kg_s_brush"] if m_dot is None else m_dot
    path = math.pi * c["R"] / 2000.0                   # materiaal schuift een kwart omtrek mee
    p_mat = P.mu_material * G_ACC * m * path            # wrijving: m kg/s over een weg path (J/s)
    p_mat += 0.5 * m * k["v_tip"] ** 2                  # kinetische energie (gooien)
    t_mat = p_mat / k["omega"] if k["omega"] > 0 else 0.0
    T = (P.idle_torque + t_floor + t_mat) if k["rpm"] > 0 else 0.0
    p_shaft = T * k["omega"]
    p_motor = p_shaft / P.eta_worm
    p_el = p_motor / P.eta_motor
    return {"T": T, "T_floor": t_floor, "T_mat": t_mat, "P_shaft": p_shaft, "P_motor": p_motor, "P_el": p_el,
            "I": p_el / P.battery_v, "motor_use": p_motor / P.motor_P}


def drive_check(name):
    """Nominaal en piekkoppel van de wormmotor, torsie insteekas, spie, naafbouten."""
    om = P.gm_out_rpm() * 2.0 * math.pi / 60.0
    t_nom = P.motor_P * P.eta_worm / om
    t_peak = 2.5 * t_nom                               # aanloopstroom DC-motor (begrensd door de regelaar)
    d = P.shaft_d
    tau = 16.0 * t_peak * 1000.0 / (math.pi * d ** 3) * 1.4      # 1,4 voor de spiebaan
    key_shear = t_peak * 1000.0 / (d / 2.0) / (8.0 * 40.0)        # spie 8 x 7 x 40
    r_bolt = P.hub_pcd / 2000.0
    bolt_shear = t_peak / r_bolt / 4.0                             # per M10 (in werkelijkheid wrijving)
    t_need = torque(name)["T"]
    return {"T_nom": t_nom, "T_peak": t_peak, "tau_shaft_MPa": tau, "key_MPa": key_shear,
            "hub_bolt_N": bolt_shear, "T_need": t_need, "reserve": t_nom / t_need}


def brush_force(name, omega_sign, v=P.drive_speed, n_seg=24):
    """Kracht (N) van de vloer op één borstel: wrijving tegen de glijsnelheid van het haar, verdeeld over de
    contactboog aan de voorkant. Geeft (Fx, Fy). Rijden naar -y."""
    c = cfg(name)
    k = kinematics(name)
    R = c["R"] / 1000.0 * P.r_contact
    half = math.radians(CONTACT_HALF_DEG)
    fx = fy = 0.0
    dF = P.mu_bristle * c["F_c"] / n_seg
    for i in range(n_seg):
        th = -half + (i + 0.5) * 2 * half / n_seg      # 0 = voorkant (-y)
        rx, ry = R * math.sin(th), -R * math.cos(th)
        vx = -omega_sign * k["omega"] * ry              # omega x r (omega langs +z)
        vy = omega_sign * k["omega"] * rx - v           # plus de rijsnelheid (-y)
        vn = math.hypot(vx, vy)
        fx -= dF * vx / vn
        fy -= dF * vy / vn
    return fx, fy


def omega_signs(name, mode):
    """Draairichting per borstel (+1 linksom), zie dbr_params.brush_signs."""
    return P.brush_signs(cfg(name), mode)


# ---------------------------------------------------------------------
# Robot: aslasten, wiellasten, zijkrachten, scheefloop
# ---------------------------------------------------------------------
def masses(name, ballast=False):
    out = [(ROBOT["robot_kg"], ROBOT["robot_cg"]), (MODEL[name]["kg"], MODEL[name]["cg"])]
    if ballast:
        out.append((BALLAST["kg"], BALLAST["cg"]))
    return out


def axle_loads(name, ballast=False, working=True):
    """(achter, voor) in kg en aandeel voor. Werkend: de aandrukkracht van de borstels gaat naar de vloer."""
    ms = masses(name, ballast)
    W = sum(m for m, _ in ms) * G_ACC
    my = sum(m * G_ACC * cg[1] for m, cg in ms)
    if working:
        c = cfg(name)
        fc = c["n"] * c["F_c"]
        W -= fc
        my -= fc * MODEL[name]["contact_y"]
    n_front = (W * HALF_BASE + my) / (2 * HALF_BASE)
    n_rear = W - n_front
    return {"rear_kg": n_rear / G_ACC, "front_kg": n_front / G_ACC, "front_share": n_front / W}


def robot_reaction(name, mode="spread", ballast=False, v=P.drive_speed):
    """Netto kracht van de borstels op de robot en de reactie: zijkrachten per as, scheefstand (psi) en
    stuurcorrectie (delta) van de voorwielen, trekkracht."""
    c = cfg(name)
    xs = P.centres_x(c, mode if c["n"] == 2 else "spread")
    FX = FY = MZ = 0.0
    yc = MODEL[name]["contact_y"]
    for x, s in zip(xs, omega_signs(name, mode)):
        fx, fy = brush_force(name, s, v)
        FX += fx
        FY += fy
        MZ += x * fy - yc * fx                          # moment om z (Nmm) van de vloerkracht in het contactpunt
    # het motorkoppel is een inwendige kracht (motor <-> borstel); naar buiten werkt alleen de vloerkracht
    al = axle_loads(name, ballast, True)
    n_rear, n_front = al["rear_kg"] * G_ACC, al["front_kg"] * G_ACC
    # zijkrachten van de banden (as achter y -500, voor y +500): F_r + F_f = -FX en MZ + 500 F_r - 500 F_f = 0
    f_rear, f_front = (-FX - MZ / HALF_BASE) / 2.0, (-FX + MZ / HALF_BASE) / 2.0
    k = ROBOT["k_corner"] * 180.0 / math.pi
    psi = f_rear / (k * n_rear)
    delta = f_front / (k * n_front) - psi
    use = max(abs(f_rear) / 2 / (ROBOT["mu_tire"] * n_rear / 2), abs(f_front) / 2 / (ROBOT["mu_tire"] * n_front / 2))
    return {"FX": FX, "FY": FY, "MZ_Nm": MZ / 1000.0, "F_rear": f_rear, "F_front": f_front,
            "psi": math.degrees(psi), "delta": math.degrees(delta), "grip_use": use,
            "pull_N": FY + ROBOT["c_rr"] * (n_rear + n_front)}


def mount_check(name):
    """Hangers: de bovenplaat hangt onder de achterste onderbalken. Het gewicht achter de balken kantelt de plaat om de
    voorste balk (y -425); de 4 M10 in de achterste balk (y -575) nemen de trek. Statisch x 2 voor stoten."""
    m = MODEL[name]["kg"] - 5.0                          # regelkast staat op de balken
    W = m * G_ACC * 2.0
    y_piv, y_bolt = P.robot_rear_beam_y[1], P.robot_rear_beam_y[0]
    t_rear = W * (y_piv - MODEL[name]["cg"][1]) / (y_piv - y_bolt)
    per_bolt = t_rear / 4.0
    # toolbar: unit op het uiteinde, buiging naar de hanger (x 200)
    c = cfg(name)
    xs = P.centres_x(c, "windrow" if c["n"] == 2 else "spread")
    unit_kg = (MODEL[name]["kg"] - MOUNT["kg"]) / c["n"]
    arm = max(0.0, max(abs(x) for x in xs) - P.hanger_x) / 1000.0
    M_tb = unit_kg * G_ACC * 2.0 * arm
    b, t = P.tb, P.tb_wall
    Wb = (b ** 4 - (b - 2 * t) ** 4) / (6.0 * b)
    T_tb = unit_kg * G_ACC * 2.0 * (P.tb_y[0] - (P.head_y0 - P.brush_pos)) / 1000.0  # torsie uit de uitkraging van de kop
    Wt = 2 * t * (b - t) ** 2
    return {"bolt_tension_N": per_bolt, "bolt_safety": 46000.0 / per_bolt, "toolbar_bending_MPa": M_tb * 1000.0 / Wb,
            "toolbar_torsion_MPa": abs(T_tb) * 1000.0 / Wt}


def runtime(name, mode="spread"):
    """Werktijd op een volle accu (80 % bruikbaar) en oppervlak per uur."""
    t = torque(name)
    p = cfg(name)["n"] * t["P_el"] + ROBOT["drive_w"]
    hours = 0.8 * ROBOT["battery_wh"] / p
    width = material_flow(name, mode)["swept_m"]
    return {"P_total_W": p, "hours": hours, "m2_h": width * P.drive_speed * 3600.0}


def report(name=P.DEFAULT_CONFIG):
    c = cfg(name)
    k = kinematics(name)
    t = torque(name)
    dc = drive_check(name)
    lines = ["=== Schotelborstels %s: kernwaarden ===" % name,
             "%d x Ø%d, hart y %.0f, x %s; tilt %.0f graden, aandrukkracht %.0f N per borstel (geschat)" % (
                 c["n"], c["d"], c["yc"], [round(x) for x in P.centres_x(c)], P.tilt_deg, c["F_c"]),
             "%.0f omw/min, omtreksnelheid %.1f m/s (%.0f x de rijsnelheid), glijweg los materiaal tot %.1f m" % (
                 k["rpm"], k["v_tip"], k["tip_to_drive"], k["throw_m"]),
             "Koppel %.1f Nm (vloer %.1f, materiaal %.2f), as %.0f W, motor %.0f W (%.0f %% van 550 W), %.0f W el. = %.1f A bij 48 V" % (
                 t["T"], t["T_floor"], t["T_mat"], t["P_shaft"], t["P_motor"], 100 * t["motor_use"], t["P_el"], t["I"]),
             "Wormmotor: %.0f Nm nominaal (%.1f x nodig), %.0f Nm piek; as %.0f MPa, spie %.0f MPa" % (
                 dc["T_nom"], dc["reserve"], dc["T_peak"], dc["tau_shaft_MPa"], dc["key_MPa"])]
    modes = ("spread", "windrow") if c["n"] == 2 else ("right", "left")
    for mode in modes:
        rr = robot_reaction(name, mode)
        mf = material_flow(name, mode if c["n"] == 2 else "spread")
        lines.append("%-8s zijkracht %+.0f N, trek %.0f N, moment %+.0f Nm -> scheef %+.2f graden, stuur %+.2f graden, "
                     "grip %.0f %%; breedte %.2f m%s" % (
                         mode, rr["FX"], rr["FY"], rr["MZ_Nm"], rr["psi"], rr["delta"], 100 * rr["grip_use"],
                         mf["swept_m"], (", wiers %.1f kg/m" % mf["windrow_kg_m"]) if mode == "windrow" else ""))
    for ballast in (False, True):
        for working in (True, False):
            al = axle_loads(name, ballast, working)
            lines.append("Aslast %s%s: achter %.0f kg, voor %.0f kg (%.0f %% voor, minimaal %.0f %%)" % (
                "werkend" if working else "borstels opgetild", " + contragewicht" if ballast else "",
                al["rear_kg"], al["front_kg"], 100 * al["front_share"], 100 * ROBOT["front_min"]))
    mc = mount_check(name)
    lines.append("Hangers: %.0f N trek per M10 (%.0f x veilig); toolbar buiging %.0f MPa, torsie %.0f MPa (x 2 stoot)" % (
        mc["bolt_tension_N"], mc["bolt_safety"], mc["toolbar_bending_MPa"], mc["toolbar_torsion_MPa"]))
    rt = runtime(name)
    lines.append("Accu: %.0f W met rijden -> %.1f h werk, ca. %.0f m2/h" % (rt["P_total_W"], rt["hours"], rt["m2_h"]))
    print("\n".join(lines))
    return lines


def report_all():
    out = []
    for name in P.CONFIGS:
        out += report(name) + [""]
    return out


if __name__ == "__main__":
    report_all()
