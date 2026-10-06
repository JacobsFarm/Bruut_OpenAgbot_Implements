"""Berekeningen voor de onderbouwing en de animatie (puur Python, geen FreeCAD nodig).

Gebruik:  import fpa_calc; fpa_calc.report()
Massa's van het werktuig komen uit het FreeCAD-model (build_fpa.mass_properties), zie MODEL.
Krachten in robotcoordinaten: x = rechts (voerhek), y = voor; de robot rijdt bij het voerschuiven naar -y.
"""
import math

import fpa_params as P

G_ACC = 9.81

# laatste meting uit het model (build_fpa.mass_properties: staal 7850 kg/m3, motor als vaste massa)
MODEL = {
    "pusher_kg": 118.4,
    "pusher_cg": (-120.0, -878.0, 302.0),
    "rotor_kg": 27.7,
    "ballast_kg": 40.2,
    "ballast_cg": (0.0, 575.0, 712.0),
}

# aannames robot (niet gemeten, zelfde als bij de vloeibare-mesttoediener)
ROBOT = {
    "robot_kg": 150.0,
    "robot_cg": (0.0, 0.0, 450.0),
    "mu_tire": 0.6,             # rubber op (natte, bevuilde) betonvloer
    "c_rr": 0.03,               # rolweerstand op beton
    "k_corner": 0.12,           # bandstijfheid: zijkracht per graad slip, per N wiellast
}

WHEELS = (("RL", -P.robot_wheel_x, P.robot_axle_y), ("RR", P.robot_wheel_x, P.robot_axle_y),
          ("FL", -P.robot_wheel_x, -P.robot_axle_y), ("FR", P.robot_wheel_x, -P.robot_axle_y))
HALF_BASE = -P.robot_axle_y          # 500
HALF_TRACK = P.robot_wheel_x         # 375


# ---------------------------------------------------------------------
# Vijzel
# ---------------------------------------------------------------------
def kinematics(rpm=P.auger_rpm):
    omega = rpm * 2.0 * math.pi / 60.0
    v_theory = P.blade_pitch / 1000.0 * rpm / 60.0
    return {"rpm": rpm, "omega": omega, "v_theory": v_theory, "v_ax": v_theory * P.conveying_eff}


def free_area():
    return math.pi / 4.0 * ((P.blade_d / 1000.0) ** 2 - (P.core_d / 1000.0) ** 2)


def capacity(rpm=P.auger_rpm):
    """Maximale transportcapaciteit (open vijzel, vulgraad fill_max)."""
    q_cap = P.feed_density * free_area() * P.fill_max            # kg per m vijzel
    flow = q_cap * kinematics(rpm)["v_ax"]                       # kg/s
    return {"q_cap_kg_m": q_cap, "flow_kg_s": flow, "flow_t_h": flow * 3.6,
            "flow_m3_h": flow / P.feed_density * 3600.0}


def helix_angle_deg(r=None):
    r = r if r is not None else (P.blade_d + P.core_d) / 4.0
    return math.degrees(math.atan(P.blade_pitch / (2.0 * math.pi * r)))


def feed_forces(m_feed, v_robot, rpm=P.auger_rpm):
    """Krachten bij m_feed kg voer in de vijzel (glijdt over de vloer met snelheid (v_ax, -v_robot)).

    F_ax   : kracht van het voer op de vijzel in x (reactie op het verschuiven naar het hek), negatief = van het hek af
    F_push : kracht van het voer op de vijzel in y (tegen de rijrichting in), positief
    T      : askoppel, P_mech, P_el (accu), I (A bij 24 V), F_chain (kettingkracht)
    """
    k = kinematics(rpm)
    v_ax = k["v_ax"] if rpm > 0 else 0.0
    v = math.hypot(v_ax, v_robot)
    f = P.mu_floor * m_feed * G_ACC
    F_ax = f * v_ax / v if v > 1e-9 else 0.0
    F_push = f * v_robot / v if v > 1e-9 else 0.0
    # vermogen voor het transport langs de vijzel (CEMA: lambda m g v); minimaal de vloerwrijving via de schroef
    r_m = (P.blade_d + P.core_d) / 4000.0
    p_cema = P.lambda_conv * m_feed * G_ACC * v_ax
    t_screw = F_ax * r_m * math.tan(math.radians(helix_angle_deg()) + math.atan(P.mu_blade))
    T = (P.idle_torque + max(p_cema / k["omega"], t_screw)) if rpm > 0 else 0.0
    p_mech = T * k["omega"]
    p_el = p_mech / P.eta_drive if rpm > 0 else 0.0
    r_s = P.pitch_d(P.z_auger) / 2000.0
    return {"F_ax": -F_ax, "F_push": F_push, "T": T, "P_mech": p_mech, "P_el": p_el,
            "I": p_el / P.battery_v, "F_chain": T / r_s, "m_feed": m_feed}


def drive_check():
    """Nominaal koppel, piekkoppel en breekbout."""
    om_m = P.motor_rpm * 2 * math.pi / 60.0
    t_motor = P.motor_P / om_m
    ratio = P.z_auger / float(P.z_motor)
    t_auger = t_motor * ratio * 0.97
    t_peak = 2.5 * t_auger                                       # aanloopstroom DC-motor
    d = P.shaft_d
    tau = 16 * t_peak * 1000.0 / (math.pi * d ** 3) * 1.25       # 1,25 voor de spiebaan
    r_stub = d / 2.0
    a_m6 = 20.1
    t_break = 2 * 0.6 * 400.0 * a_m6 * r_stub / 1000.0           # M6 4.6 in dubbele afschuiving op de asstomp
    a_m10 = 58.0
    t_m10 = 2 * 0.6 * 800.0 * a_m10 * r_stub / 1000.0
    r_s = P.pitch_d(P.z_auger) / 2000.0
    f_chain = t_peak / r_s
    return {"T_motor": t_motor, "T_auger": t_auger, "T_peak": t_peak, "tau_peak_MPa": tau,
            "T_shear_pin": t_break, "T_pin_M10": t_m10, "F_chain_peak": f_chain,
            "chain_safety": 18200.0 / f_chain, "chain_safety_at_pin": 18200.0 / (t_break / r_s)}


def deflection():
    """Doorbuiging kernbuis (scharnierend tussen de lagers) onder eigen gewicht + voerkracht."""
    E = 210000.0
    D, t = P.core_d, P.core_t
    I = math.pi * (D ** 4 - (D - 2 * t) ** 4) / 64.0
    L = P.inner_width + 2 * P.plate_t + 2 * 20
    q = (MODEL["rotor_kg"] * G_ACC + 2 * drive_check()["T_peak"] / ((P.blade_d + P.core_d) / 4000.0) * 0.5) / L
    delta = 5 * q * L ** 4 / (384 * E * I)
    sigma = q * L ** 2 / 8.0 / (I / (D / 2.0))
    return {"delta_mm": delta, "sigma_MPa": sigma}


# ---------------------------------------------------------------------
# Robot: wiellasten, zijkrachten, scheefloop
# ---------------------------------------------------------------------
def masses(ballast=True, pusher=True):
    out = [(ROBOT["robot_kg"], ROBOT["robot_cg"])]
    if pusher:
        out.append((MODEL["pusher_kg"], MODEL["pusher_cg"]))
    if ballast:
        out.append((MODEL["ballast_kg"], MODEL["ballast_cg"]))
    return out


def robot_reaction(F_ax=0.0, F_push=0.0, point=(0.0, P.auger_y - 150.0, 60.0), ballast=True, pusher=True):
    """Statisch evenwicht van robot + voerschuif bij voerkrachten (F_ax in x, F_push in y) in point.

    Geeft per wiel: N (wiellast), lat (zijkracht van de grond, +x), trac (aandrijfkracht motor), use (benutting
    van de grip), slip (slip-hoek, graden), plus psi (scheefstand robot, graden, + = linksom) en delta
    (stuurhoek voorwielen t.o.v. de robot, graden).
    """
    ms = masses(ballast, pusher)
    W = sum(m for m, _ in ms) * G_ACC
    xf, yf, zf = point
    # langs: momenten om de x-as door de oorsprong (grond)
    my = sum(m * G_ACC * c[1] for m, c in ms)
    n_front = (W * HALF_BASE + my + zf * F_push) / (2 * HALF_BASE)
    n_rear = W - n_front
    # dwars: momenten om de y-as
    mx = sum(m * G_ACC * c[0] for m, c in ms)
    d_lr = (mx - zf * (-F_ax)) / HALF_TRACK                      # N_right - N_left (totaal)
    loads = {}
    for tag, n_axle in (("R", n_rear), ("F", n_front)):
        share = n_axle / W
        loads[tag + "L"] = n_axle / 2.0 - d_lr * share / 2.0
        loads[tag + "R"] = n_axle / 2.0 + d_lr * share / 2.0
    # zijkrachten: som = -F_ax, momenten om z
    m_trac = sum(x * (-F_push * loads[t] / W) for t, x, _ in WHEELS)
    m_feed = xf * F_push - yf * F_ax
    s = -F_ax
    d = -(m_feed + m_trac) / HALF_BASE                           # F_rear - F_front
    f_rear, f_front = (s + d) / 2.0, (s - d) / 2.0
    k = ROBOT["k_corner"] * 180.0 / math.pi                      # per rad
    c_rear = k * (loads["RL"] + loads["RR"])
    c_front = k * (loads["FL"] + loads["FR"])
    psi = f_rear / c_rear
    delta = f_front / c_front - psi
    wheels = {}
    for tag, x, y in WHEELS:
        axle = "R" if tag[0] == "R" else "F"
        n = loads[tag]
        n_axle = loads[axle + "L"] + loads[axle + "R"]
        lat = (f_rear if axle == "R" else f_front) * n / n_axle
        trac = F_push * n / W + ROBOT["c_rr"] * n
        slip = math.degrees(psi if axle == "R" else psi + delta)
        wheels[tag] = {"N": n, "lat": lat, "trac": trac, "use": math.hypot(lat, trac) / (ROBOT["mu_tire"] * n),
                       "slip": slip}
    return {"wheels": wheels, "psi": math.degrees(psi), "delta": math.degrees(delta), "F_rear": f_rear,
            "F_front": f_front, "W": W, "n_front": n_front, "n_rear": n_rear}


def axle_loads():
    """Aslasten (kg) zonder werktuig, met voerschuif, met voerschuif + contragewicht."""
    out = {}
    for name, pusher, ballast in (("robot", False, False), ("met voerschuif", True, False),
                                  ("met voerschuif + contragewicht", True, True)):
        r = robot_reaction(pusher=pusher, ballast=ballast)
        out[name] = (round(r["n_rear"] / G_ACC, 1), round(r["n_front"] / G_ACC, 1))
    return out


def mount_check():
    """Belasting van de 4 armen en de M10-bouten in de flenzen van de wielbeugels (statisch x 2 voor stoten)."""
    m = MODEL["pusher_kg"]
    lever = (P.wf_face_y - MODEL["pusher_cg"][1]) / 1000.0
    M = m * G_ACC * lever * 2.0                                  # Nm, totaal
    zs = P.wf_hole_z
    zc = sum(zs) / len(zs)
    i = sum((z - zc) ** 2 for z in zs) / 1e6                     # m2
    per_arm = M / 4.0
    f_bolt = per_arm * (max(zs) - zc) / 1000.0 / i               # trek bovenste bout (draaiing om het midden)
    shear = m * G_ACC * 2.0 / 16.0
    return {"moment_Nm": M, "bolt_tension_N": f_bolt, "bolt_shear_N": shear,
            "flange_bearing_MPa": shear / (P.m10_hole * P.wf_t)}


def report():
    k = kinematics()
    c = capacity()
    dc = drive_check()
    df = deflection()
    typical = feed_forces(12.0, P.drive_speed)
    rr = robot_reaction(typical["F_ax"], typical["F_push"])
    lines = [
        "=== Voerschuifvijzel advanced: kernwaarden ===",
        "Vijzel %.0f omw/min, spoed %.0f -> voer %.2f m/s langs de vijzel (theorie %.2f)" % (
            k["rpm"], P.blade_pitch, k["v_ax"], k["v_theory"]),
        "Capaciteit %.1f kg per m vijzel, %.1f kg/s = %.0f t/h (%.0f m3/h)" % (
            c["q_cap_kg_m"], c["flow_kg_s"], c["flow_t_h"], c["flow_m3_h"]),
        "Bij %.2f m/s rijden: tot %.1f kg voer per m voergang verwerken" % (
            P.drive_speed, c["flow_kg_s"] / P.drive_speed),
        "Motor %.1f Nm, vijzel %.1f Nm nominaal, %.0f Nm piek; torsie as %.0f MPa" % (
            dc["T_motor"], dc["T_auger"], dc["T_peak"], dc["tau_peak_MPa"]),
        "Breekbout M6 4.6 breekt bij %.0f Nm (M10 8.8 pas bij %.0f Nm); ketting %.0f x veilig bij piek" % (
            dc["T_shear_pin"], dc["T_pin_M10"], dc["chain_safety"]),
        "Doorbuiging kernbuis %.2f mm, buigspanning %.0f MPa" % (df["delta_mm"], df["sigma_MPa"]),
        "12 kg voer in de vijzel: F_ax %.0f N, duwkracht %.0f N, koppel %.1f Nm, %.0f W el. (%.1f A)" % (
            typical["F_ax"], typical["F_push"], typical["T"], typical["P_el"], typical["I"]),
        "  zijkracht achteras %.0f N, vooras %.0f N, scheefstand %.2f graden, stuurcorrectie %.2f graden" % (
            rr["F_rear"], rr["F_front"], rr["psi"], rr["delta"]),
        "Aslasten (achter, voor) kg: %s" % axle_loads(),
        "Armen: %s" % {kk: round(v, 1) for kk, v in mount_check().items()},
    ]
    print("\n".join(lines))
    return lines
