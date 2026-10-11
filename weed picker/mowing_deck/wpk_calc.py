"""Calculations for the weed picker (pure Python, no FreeCAD needed).

Use:  import wpk_calc; wpk_calc.report()
Masses come from the FreeCAD model (build_wpk.mass_properties), see wpk_kin.MODEL. Robot coordinates: x = right,
y = front, z = up, mm. The weed picker hangs in front of the robot.
"""
import math

import wpk_params as P
import wpk_kin as K

G_ACC = 9.81
DYN = 2.0                       # dynamic factor for bumps and hits
DRAG_N = 300.0                  # backward force on the deck: dense weeds pushed over + a molehill (estimated)

# robot 4WD ready to drive, from agbots/agbot comparison (estimated, not weighed)
ROBOT = {
    "robot_kg": 161.5,
    "robot_cg": (0.0, 95.0, 543.0),
    "battery_wh": 2400.0,       # 48 V 50 Ah
    "axle_spec_kg": 500.0,      # per axle, hub motor spec
}
COUNTERWEIGHT_Y = -600.0        # counterweight on the rear lower beams (e.g. the 2 x 20 kg blocks of the feed pusher)
DENSITIES = (0.05, 0.2, 0.5, 1.0, 1.5)      # kg/m2 fresh weed above the cut: scattered .. dense thistle patch
DENSITY_REF = 0.2               # kg/m2: a pasture with scattered weeds (reference for power, run time)


# ---------------------------------------------------------------------
# Rotors
# ---------------------------------------------------------------------
def rotor():
    w = P.rpm * 2 * math.pi / 60.0
    rps = P.rpm / 60.0
    return {"rpm": P.rpm, "omega": w, "v_tip": w * P.blade_r[1] / 1000.0, "cut_w": P.CUT_W, "overlap": P.OVERLAP,
            "chop_mm": P.drive_speed * 1000.0 / (2 * rps), "tip_circle": 2 * P.blade_r[1]}


def blade():
    """Centrifugal force on a swinging blade, the bolt and the blade at its hole, the energy of one blade."""
    w = rotor()["omega"]
    m = K.MODEL["blade_kg"]
    r0, r1 = P.blade_r
    r_cg = (r0 + r1) / 2.0
    f = m * w ** 2 * r_cg / 1000.0
    area_bolt = math.pi * (P.pin_d / 2.0) ** 2 * 0.78           # thread root
    length = (r1 - r0) / 1000.0
    i_blade = m * ((r_cg / 1000.0) ** 2 + length ** 2 / 12.0)
    return {"F_N": f, "tau_bolt": f / area_bolt, "sigma_net": f / ((P.blade_w - P.pin_d - 1.0) * P.blade_t),
            "bearing": f / (P.pin_d * P.blade_t), "E_blade_J": 0.5 * i_blade * w ** 2,
            "E_rotor_J": 0.5 * (K.MODEL["rotor_I"] + 0.002) * w ** 2}


def windage():
    """Air drag of one rotor (W): 2 blades edgewise (thickness blade_t) + the bar (bar_t, r 30 .. bar_r)."""
    w = rotor()["omega"]

    def strip(t, r0, r1):
        return 0.5 * P.rho_air * P.cd_blade * t / 1000.0 * w ** 3 * ((r1 / 1000.0) ** 4 - (r0 / 1000.0) ** 4) / 4.0
    return 2 * strip(P.blade_t, P.blade_r[0], P.blade_r[1]) + 2 * strip(P.bar_t, P.boss_d / 2.0, P.bar_r)


def motor_available():
    """Continuous shaft power (W) of one motor at the rotor speed (rated torque x speed)."""
    return P.motor_P * P.rpm / P.motor_rpm


def power(v=P.drive_speed, density=DENSITY_REF):
    """Shaft and electrical power (W) at v (m/s) in weeds of 'density' kg/m2 (fresh, above the cut)."""
    wd = windage()
    chop = P.e_chop * density * P.CUT_W / 1000.0 * v
    shaft_rotor = wd + P.idle_W + chop / 2.0
    shaft = 2 * shaft_rotor
    el = shaft / P.eta_motor
    return {"windage_W": 2 * wd, "idle_W": 2 * P.idle_W, "chop_W": chop, "shaft_W": shaft, "el_W": el,
            "I_A": el / P.battery_v, "motor_load": shaft_rotor / motor_available(),
            "kg_s": density * P.CUT_W / 1000.0 * v}


def speed_limit(density, load=0.9, v_max=1.0):
    """Highest driving speed (m/s) at which each motor stays below 'load' x its available power."""
    spare = 2 * (load * motor_available() - windage() - P.idle_W)
    v = spare / (P.e_chop * density * P.CUT_W / 1000.0)
    return min(v_max, v)


def capacity(v=P.drive_speed, density=DENSITY_REF):
    pw = power(v, density)
    el = pw["el_W"] + P.drive_W
    hours = 0.8 * ROBOT["battery_wh"] / el
    ha_h = P.CUT_W / 1000.0 * v * 3600.0 / 10000.0
    return {"ha_h": ha_h, "hours": hours, "ha_charge": ha_h * hours, "el_W": el}


def start_up():
    """Time to run one rotor up to speed at the rated motor torque."""
    i_rot = K.MODEL["rotor_I"] + 0.002                       # + motor rotor and coupling (estimated)
    t_motor = P.motor_P / (P.motor_rpm * 2 * math.pi / 60.0)
    return {"t_s": i_rot * rotor()["omega"] / t_motor, "T_Nm": t_motor}


def windrow(density):
    """Windrow behind the deck: kg per metre of driving, cross-section, height of a half-ellipse windrow_w wide."""
    kg_m = density * P.CUT_W / 1000.0 * P.windrow_share
    area = kg_m / P.windrow_bulk
    h = area / (math.pi / 4.0 * P.windrow_w / 1000.0)
    return {"kg_m": kg_m, "area_m2": area, "h_mm": h * 1000.0, "scattered_g_m2": density * (1 - P.windrow_share) * 1000}


# ---------------------------------------------------------------------
# Strength
# ---------------------------------------------------------------------
def strength():
    worst = {"top_N": 0.0, "bottom_N": 0.0, "actuator_N": 0.0}
    for c in (P.cut_range[0], P.cut_h, P.cut_range[1]):
        for drag in (0.0, DYN * DRAG_N):
            f = K.forces(c, drag, DYN)
            for k in worst:
                if abs(f[k]) > abs(worst[k]):
                    worst[k] = f[k]
    f_link = max(abs(worst["top_N"]), abs(worst["bottom_N"])) / 2.0         # per side (2 bars)
    a_net = 2 * (P.link_w - P.pin_d - 1.0) * P.link_t
    i_bar = P.link_w * P.link_t ** 3 / 12.0
    euler = 2 * math.pi ** 2 * 210000.0 * i_bar / P.link_L ** 2                # 2 bars, pinned, weak axis
    a_pin = math.pi * (P.pin_d / 2.0) ** 2
    # mount: moment of the hanging part about the middle between the 2 beams, carried by the 2 bolt rows
    m_hang = K.MODEL["kg"] - K.MODEL["mount_kg"] - K.MODEL["controller_kg"]
    y_mid = sum(P.robot_front_beam_y) / 2.0
    y_hang = (K.MODEL["kg"] * K.MODEL["cg"][1] - K.MODEL["mount_kg"] * 478.0 - K.MODEL["controller_kg"] * -500.0) \
        / m_hang
    m_mount = DYN * m_hang * G_ACC * (y_hang - y_mid) / 1000.0
    f_row = m_mount * 1000.0 / (P.robot_front_beam_y[1] - P.robot_front_beam_y[0])
    return {"forces": worst, "F_link_side_N": f_link, "sigma_link": f_link / a_net, "euler_N": euler,
            "tau_pin": f_link / (2 * a_pin), "F_act_max_N": worst["actuator_N"], "M_mount_Nm": m_mount,
            "F_bolt_N": f_row / 4.0 + DYN * m_hang * G_ACC / 8.0, "y_hang": y_hang}


# ---------------------------------------------------------------------
# Robot
# ---------------------------------------------------------------------
def axle_loads(counterweight=0.0):
    """Axle loads (kg) of the robot with the weed picker (and a counterweight on the rear beams)."""
    ms = [(ROBOT["robot_kg"], ROBOT["robot_cg"]), (K.MODEL["kg"], K.MODEL["cg"])]
    if counterweight:
        ms.append((counterweight, (0.0, COUNTERWEIGHT_Y, 700.0)))
    m = sum(mi for mi, _ in ms)
    cy = sum(mi * c[1] for mi, c in ms) / m
    front = m * (P.robot_axle_y + cy) / (2 * P.robot_axle_y)
    return {"total_kg": m, "front_kg": front, "rear_kg": m - front, "front_share": front / m, "cg_y": cy}


def counterweight_for(rear_share=0.3):
    for kg in range(0, 200):
        if 1.0 - axle_loads(kg)["front_share"] >= rear_share:
            return kg
    return None


# ---------------------------------------------------------------------
# Cost (rough, 2026, excl. VAT)
# ---------------------------------------------------------------------
COST = [
    ("2 x BLDC motor 48 V 750 W 3000 rpm + driver", 350.0),
    ("2 x lawn-tractor deck spindle (2 bearings, 3-bolt)", 70.0),
    ("2 x jaw coupling bore 19 / 19 + spider", 30.0),
    ("Linear actuator 4000 N, 150 mm stroke, 24 V, IP66 + DC-DC 48/24 V + reversing relay", 110.0),
    ("Laser-cut steel (deck 3, skirt 3 rolled, swath boards, mount plate, lugs, 8 link bars, doublers, spacer rings, "
     "motor plates, blade bars)", 260.0),
    ("4 swinging blades 50 x 6 (C45 / Hardox, ground both edges)", 40.0),
    ("RHS 50 x 40 x 3, tube 20 (standoffs), M10 rods", 20.0),
    ("Bolts: 8 x M10, 10 x M16 pins with lock nuts, M8, M16 blade bolts", 40.0),
    ("Controller box IP66, fuses, cable glands, cable", 60.0),
    ("Paint / galvanizing", 60.0),
]


def cost():
    return sum(c for _, c in COST)


# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------
def report():
    r = rotor()
    bl = blade()
    pw = power()
    cap = capacity()
    su = start_up()
    st = strength()
    lines = []
    lines.append("Weed picker (mowing deck)")
    lines.append("Rotors: %.0f rpm, blade tip %.0f m/s, cut width %.0f mm (2 x O%.0f, overlap %.0f, left rotor "
                 "+%.0f mm), chop length %.1f mm at %.1f m/s" % (r["rpm"], r["v_tip"], r["cut_w"], r["tip_circle"], r["overlap"],
                                                      P.rotor_dz, r["chop_mm"], P.drive_speed))
    lines.append("Blade: %.0f N centrifugal, bolt %.0f MPa shear, blade %.0f MPa net section, %.0f MPa bearing; "
                 "%.0f J per blade, %.0f J per rotor" % (bl["F_N"], bl["tau_bolt"], bl["sigma_net"], bl["bearing"],
                                                         bl["E_blade_J"], bl["E_rotor_J"]))
    lines.append("Start-up: %.1f s to speed (rated torque %.1f Nm)" % (su["t_s"], su["T_Nm"]))
    lines.append("Power at %.1f m/s in %.2f kg/m2: windage %.0f W + idle %.0f W + chopping %.0f W = %.0f W shaft, "
                 "%.0f W electric (%.1f A at 48 V), each motor %.0f %% of %.0f W available"
                 % (P.drive_speed, DENSITY_REF, pw["windage_W"], pw["idle_W"], pw["chop_W"], pw["shaft_W"],
                    pw["el_W"], pw["I_A"], 100 * pw["motor_load"], motor_available()))
    lines.append("Driving speed limit (motors at 90 %):")
    for d in DENSITIES:
        v = speed_limit(d)
        w = windrow(d)
        lines.append("  %.2f kg/m2: %.2f m/s (%.2f ha/h); windrow %.2f kg/m, %.0f mm high (%.0f mm wide), "
                     "%.0f g/m2 scattered" % (d, v, P.CUT_W / 1000.0 * v * 0.36, w["kg_m"], w["h_mm"], P.windrow_w,
                                              w["scattered_g_m2"]))
    lines.append("Capacity at %.1f m/s: %.2f ha/h; %.1f h per charge (%.0f W with driving) -> %.2f ha per charge"
                 % (P.drive_speed, cap["ha_h"], cap["hours"], cap["el_W"], cap["ha_charge"]))
    lines.append("Linkage (link %.0f, pivots %.0f apart), actuator %.0f mm closed + %.0f stroke, float link %.0f/%.0f:"
                 % (P.link_L, P.pivot_z[1] - P.pivot_z[0], P.act_closed, P.act_stroke, P.float_len, P.float_slot))
    for row in K.table():
        lines.append("  cut %3d: links %+5.1f deg, rotors at y %4.0f (%+3.0f), deck top %3.0f, actuator %3.0f mm "
                     "(%3.0f out), holds %4.0f N, can float up %3.0f mm"
                     % (row["cut"], row["theta"], row["deck_y"], row["deck_dy"], row["deck_top"], row["act"],
                        row["act_ext"], row["F_act"], row["lift_max"]))
    lines.append("  full range %.0f .. %.0f mm in %.1f s (%.0f mm/s); top link touches the plate at %.1f deg (cut %.0f)"
                 % (P.cut_range[0], P.cut_range[1], K.lift_time(), P.act_speed, K.theta_limit(),
                    K.cut_for_theta(K.theta_limit())))
    f = st["forces"]
    lines.append("Strength (weight x%.0f, drag %.0f N x%.0f): links top %.0f N / bottom %.0f N, actuator %.0f N "
                 "(rated %.0f N)" % (DYN, DRAG_N, DYN, f["top_N"], f["bottom_N"], f["actuator_N"], P.act_F))
    lines.append("  link bars 2 x %.0f x %.0f: %.0f MPa at the hole, Euler %.0f N; pins M16 %.0f MPa (double shear)"
                 % (P.link_w, P.link_t, st["sigma_link"], st["euler_N"], st["tau_pin"]))
    lines.append("  mount: %.0f Nm about the beams -> %.0f N per M10 bolt (proof load 33 kN)"
                 % (st["M_mount_Nm"], st["F_bolt_N"]))
    al = axle_loads()
    cw = counterweight_for(0.3)
    al_cw = axle_loads(cw)
    lines.append("Robot with weed picker: %.0f kg, front %.0f kg / rear %.0f kg (%.0f %% front, axle spec %.0f kg)"
                 % (al["total_kg"], al["front_kg"], al["rear_kg"], 100 * al["front_share"], ROBOT["axle_spec_kg"]))
    lines.append("  with %d kg on the rear beams: front %.0f / rear %.0f kg (%.0f %% rear)"
                 % (cw, al_cw["front_kg"], al_cw["rear_kg"], 100 * (1 - al_cw["front_share"])))
    lines.append("Cost: about EUR %.0f in parts" % cost())
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
