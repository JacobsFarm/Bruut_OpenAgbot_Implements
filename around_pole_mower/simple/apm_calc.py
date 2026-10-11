"""Calculations for the around-pole fence mower (pure Python, no FreeCAD needed).

Use:  import apm_calc; apm_calc.report()
Masses come from the FreeCAD model (build_apm.mass_properties), see MODEL. The post pass comes from apm_kin.
Robot coordinates: x = right, y = front, z = up, mm. The mower is behind the right rear wheel.
"""
import math

import apm_params as P
import apm_kin as K

G_ACC = 9.81

# last measurement from the model (build_apm.mass_properties: steel 7850, PE 950, pulleys 3500 kg/m3 (spoked),
# bought parts with a fixed mass), arm at rest
MODEL = {"kg": 50.3, "cg": (349.0, -892.0, 281.0), "mount_kg": 15.5, "swing_kg": 31.4, "arm_kg": 25.8,
         "arm_cg_u": 470.0, "rotor_kg": 3.2, "I_swing": 6.5, "controller_kg": 3.3}

# robot 4WD ready to drive, from agbots/agbot comparison (estimated, not weighed)
ROBOT = {
    "robot_kg": 161.5,
    "robot_cg": (0.0, 95.0, 543.0),
    "battery_wh": 2400.0,       # 48 V 50 Ah
    "drive_w": 180.0,           # driving slowly on grass along the fence, with the drag of the head (estimated)
    "axle_spec_kg": 500.0,      # per axle, hub motor spec
}

E_STEEL = 210000.0
DYN = 2.0                       # dynamic factor for bumps and post impacts


# ---------------------------------------------------------------------
# Head: speed, reach, power
# ---------------------------------------------------------------------
def head():
    rpm = P.motor_rpm * P.pulley_motor_d / P.pulley_spindle_d
    w = rpm * 2 * math.pi / 60.0
    r_tip = P.string_r[1] / 1000.0
    hx = P.HEAD_REST[0]
    return {"rpm": rpm, "omega": w, "v_tip": w * r_tip, "v_disc_edge": w * P.disc_d / 2000.0,
            "cut_width": 2 * P.string_r[1], "reach_x": (hx - P.string_r[1], hx + P.string_r[1]),
            "inside_wire": P.WIRE_X - (hx - P.string_r[1]), "outside_post": hx + P.string_r[1] - P.POST_X,
            "beyond_guard": P.string_r[1] - P.guard_d / 2.0}


def power(v=P.drive_speed, cut_energy=P.cut_energy):
    """Shaft and electrical power (W) for mowing at v (m/s): cutting + air drag of the strings + idle."""
    h = head()
    w = h["omega"]
    r0 = (P.clamp_r + P.clamp[0] / 2.0) / 1000.0
    r1 = P.string_r[1] / 1000.0
    d = P.string_d / 1000.0
    drag_one = 0.5 * P.rho_air * P.cd_string * d * w ** 3 * (r1 ** 4 - r0 ** 4) / 4.0
    drag = P.n_strings * drag_one
    cut = cut_energy * h["cut_width"] / 1000.0 * v
    shaft = cut + drag + P.idle_W
    motor_out = shaft / P.eta_belt
    el = motor_out / P.eta_motor
    t_motor = motor_out / (P.motor_rpm * 2 * math.pi / 60.0)
    return {"cut_W": cut, "drag_W": drag, "idle_W": P.idle_W, "shaft_W": shaft, "motor_W": motor_out,
            "el_W": el, "I_A": el / P.battery_v, "T_motor_Nm": t_motor, "motor_load": motor_out / P.motor_P}


def runtime(v=P.drive_speed):
    p = power(v)
    hours = 0.8 * ROBOT["battery_wh"] / (p["el_W"] + ROBOT["drive_w"])
    return {"hours": hours, "km_per_charge": hours * v * 3.6, "m_per_hour": v * 3600.0}


def start_up():
    """Time to run the rotor up to speed at the motor's rated torque (rotor + pulleys)."""
    i_rotor = 0.0221 + 0.004                     # kg m2: rotor from the model + motor pulley reflected (estimated)
    t_motor = P.motor_P / (P.motor_rpm * 2 * math.pi / 60.0)
    t_head = t_motor * P.pulley_spindle_d / P.pulley_motor_d * P.eta_belt
    return {"T_head_Nm": t_head, "t_s": i_rotor * head()["omega"] / t_head,
            "energy_J": 0.5 * i_rotor * head()["omega"] ** 2}


# ---------------------------------------------------------------------
# Swing arm: spring, holding, post pass
# ---------------------------------------------------------------------
def spring_table(steps=(30, 40, 50, 60, 70, 85)):
    rows = []
    for psi in steps:
        s = K.spring(psi)
        rows.append({"psi": psi, "len": s["length"], "F": s["F"], "M": s["M"], "M_grass": K.grass_torque(psi),
                     "head": P.head_centre(psi)})
    return rows


def holding():
    """At rest the spring must hold the arm against the grass drag; the rest stop takes the difference."""
    s = K.spring(P.psi_rest)
    m_g = K.grass_torque(P.psi_rest)
    stretch_max = K.spring(P.psi_max)["stretch"]
    return {"M_spring_rest": s["M"], "M_grass": m_g, "margin": s["M"] / m_g, "stop_force_N": (s["M"] - m_g) * 1000.0 /
            P.stop_r, "stretch_max": stretch_max, "stretch_ratio": stretch_max / P.spring_free,
            "F_max": K.spring(P.psi_max)["F"]}


def post_pass(speeds=(0.3, 0.5, 0.8, 1.0)):
    out = []
    for v in speeds:
        run = K.simulate(posts=(1500.0,), v=v)
        pk = K.peak(run)
        slide = [s["F"] for s in run if s["contact"] is not None]
        slide.sort()
        pk["F_post_median_N"] = round(slide[len(slide) // 2]) if slide else 0
        pk["v"] = v
        out.append(pk)
    return out


# ---------------------------------------------------------------------
# Strength
# ---------------------------------------------------------------------
def arm_section():
    """U section: base plate (arm_w x base_t) + 2 ribs (rib_t x rib_h), without the cover."""
    b, t = P.arm_w, P.base_t
    rt, rh = P.rib_t, P.rib_h
    a1, z1 = b * t, t / 2.0
    a2, z2 = 2 * rt * rh, t + rh / 2.0
    a = a1 + a2
    zc = (a1 * z1 + a2 * z2) / a
    i_y = b * t ** 3 / 12.0 + a1 * (z1 - zc) ** 2 + 2 * rt * rh ** 3 / 12.0 + a2 * (z2 - zc) ** 2
    w_y = i_y / max(zc, t + rh - zc)
    i_z = t * b ** 3 / 12.0 + 2 * (rh * rt ** 3 / 12.0 + rh * rt * (b / 2.0 - rt / 2.0) ** 2)
    w_z = i_z / (b / 2.0)
    j = (b * t ** 3 + 2 * rh * rt ** 3) / 3.0                  # open section (cover off)
    return {"A": a, "zc": zc, "I_y": i_y, "W_y": w_y, "I_z": i_z, "W_z": w_z, "J_open": j}


def strength(f_post=None):
    sec = arm_section()
    if f_post is None:
        f_post = max(p["F_post_max_N"] for p in post_pass((P.drive_speed,)))
    w_arm = MODEL["arm_kg"] * G_ACC
    # 1) arm hanging on a float stop (head lifted off the ground, robot over a hump): cantilever from the stop bars
    m_v = DYN * w_arm * (MODEL["arm_cg_u"] - P.hinge_u) / 1000.0
    s_v = m_v * 1000.0 / sec["W_y"]
    f_stop = m_v * 1000.0 / (P.float_stop_u[1] - P.hinge_u)
    # 2) post force at the head, in the plane of the arm
    m_h = DYN * f_post * P.arm_L / 1000.0
    s_h = m_h * 1000.0 / sec["W_z"]
    # 3) torsion from the skid (skid carries the head, offset skid_v), open section
    f_skid = w_arm * (MODEL["arm_cg_u"] - P.hinge_u) / (P.skid_u - P.hinge_u)
    t_skid = DYN * f_skid * abs(P.skid_v) / 1000.0
    tau = t_skid * 1000.0 * max(P.base_t, P.rib_t) / sec["J_open"]
    twist = math.degrees(t_skid * 1000.0 * P.arm_L / (81000.0 * sec["J_open"]))
    # 4) pivot post: post force at the head acts on the sleeve, bending the post below the webs
    d, di = P.post_d, P.post_d - 2 * P.post_wall
    w_post = math.pi * (d ** 4 - di ** 4) / (32.0 * d)
    lever = P.web_post_z - (P.sleeve_z[0] + P.sleeve_z[1]) / 2.0
    s_post = DYN * f_post * lever / w_post
    # 5) hanger bolts: overturning moment of the swing group (weight at its CG) about the hanger
    hx, hy = sum(P.hanger_x) / 2.0, sum(P.hanger_y) / 2.0
    r = math.hypot(496.0 - hx, -1027.0 - hy)                     # swing CG from the model
    m_o = DYN * MODEL["swing_kg"] * G_ACC * r / 1000.0
    f_bolt = m_o * 1000.0 / (P.robot_rear_beam_y[1] - P.robot_rear_beam_y[0]) / 2.0
    return {"sec": sec, "M_vert_Nm": m_v, "sigma_vert": s_v, "F_float_stop_N": f_stop, "M_post_Nm": m_h,
            "sigma_post": s_h, "F_skid_N": f_skid, "T_skid_Nm": t_skid, "tau_twist": tau, "twist_deg": twist,
            "sigma_pivot_post": s_post, "M_hanger_Nm": m_o, "F_bolt_N": f_bolt, "F_post_N": f_post}


# ---------------------------------------------------------------------
# Robot
# ---------------------------------------------------------------------
def axle_loads():
    """Wheel loads (kg) with the mower: rear/front axle and right/left side."""
    ms = [(ROBOT["robot_kg"], ROBOT["robot_cg"]), (MODEL["kg"], MODEL["cg"])]
    m = sum(mi for mi, _ in ms)
    cy = sum(mi * c[1] for mi, c in ms) / m
    cx = sum(mi * c[0] for mi, c in ms) / m
    half_b = P.robot_axle_y
    front = m * (half_b + cy) / (2 * half_b)
    rear = m - front
    right = m * (P.robot_wheel_x + cx) / (2 * P.robot_wheel_x)
    rr = rear * (P.robot_wheel_x + cx) / (2 * P.robot_wheel_x)
    return {"total_kg": m, "rear_kg": rear, "front_kg": front, "front_share": front / m, "right_share": right / m,
            "RR_kg": rr, "cg": (cx, cy)}


def fence():
    """Head height against the wires."""
    lift = (P.arm_L - P.hinge_u) * math.sin(math.radians(P.float_deg))
    return {"head_top": P.HEAD_TOP_Z, "float_up": lift, "min_wire_central": P.HEAD_TOP_Z + lift + 50.0,
            "lowest_wire": min(P.wire_z), "post_x": P.POST_X, "wire_x": P.WIRE_X}


# ---------------------------------------------------------------------
# Cost (rough, 2026, excl. VAT)
# ---------------------------------------------------------------------
COST = [
    ("BLDC motor 48 V 750 W 3000 rpm + driver", 175.0),
    ("Lawn-tractor deck spindle (2 bearings, 3-bolt)", 35.0),
    ("V-pulleys A D110 + D90 (taper lock), V-belt A", 45.0),
    ("Laser-cut steel (base plate, webs, hanger, clevis, stop plate, motor plate, disc, guard cover), bent cover",
     120.0),
    ("Tube 60.3 x 5, tube 76.1 x 5, flat bar 6 x 50, 8 x 50", 35.0),
    ("PE pipe 315 SDR 17 (slice), HDPE puck, PE bushes", 30.0),
    ("Extension spring, eye bolt, stop bolts, M16 hinge bolt, fasteners", 30.0),
    ("Nylon line 3.3 mm (roll), string clamps", 20.0),
    ("Controller box IP66, fuse, relay, cable glands, cable", 45.0),
    ("Paint / galvanizing of the welded parts", 40.0),
]


def cost():
    return sum(c for _, c in COST)


# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------
def report():
    h = head()
    pw = power()
    pw1 = power(1.0)
    rt = runtime()
    su = start_up()
    ho = holding()
    pp = post_pass()
    st = strength()
    al = axle_loads()
    fe = fence()
    ma = K.missed_area()
    lines = []
    lines.append("Around-pole fence mower (simple)")
    lines.append("Head: %.0f rpm, string tip %.0f m/s (disc edge %.0f m/s), cut width %.0f mm; strings %.0f mm beyond "
                 "the guard" % (h["rpm"], h["v_tip"], h["v_disc_edge"], h["cut_width"], h["beyond_guard"]))
    lines.append("Reach: x %.0f .. %.0f; %.0f mm inside the wire, %.0f mm beyond the post line"
                 % (h["reach_x"][0], h["reach_x"][1], h["inside_wire"], h["outside_post"]))
    lines.append("Power at %.1f m/s: cut %.0f W + string drag %.0f W + idle %.0f W = %.0f W shaft, %.0f W electric "
                 "(%.1f A at 48 V), motor %.0f %% of rated" % (P.drive_speed, pw["cut_W"], pw["drag_W"], pw["idle_W"],
                                                              pw["shaft_W"], pw["el_W"], pw["I_A"],
                                                              100 * pw["motor_load"]))
    lines.append("Power at 1.0 m/s: %.0f W electric (%.0f %% of rated)" % (pw1["el_W"], 100 * pw1["motor_load"]))
    lines.append("Run time: %.1f h with driving -> %.1f km of fence per charge, %.0f m/h"
                 % (rt["hours"], rt["km_per_charge"], rt["m_per_hour"]))
    lines.append("Start-up: %.1f s to full speed, %.0f J in the rotor" % (su["t_s"], su["energy_J"]))
    lines.append("Spring: rest %.1f Nm vs grass %.1f Nm (x %.1f), rest stop %.0f N; max stretch %.0f mm (%.0f %% of "
                 "free length), F max %.0f N" % (ho["M_spring_rest"], ho["M_grass"], ho["margin"], ho["stop_force_N"],
                                                ho["stretch_max"], 100 * ho["stretch_ratio"], ho["F_max"]))
    for r in spring_table():
        lines.append("  psi %3d: spring %.0f mm, %.0f N, %.1f Nm (grass %.1f Nm), head (%.0f, %.0f)"
                     % (r["psi"], r["len"], r["F"], r["M"], r["M_grass"], r["head"][0], r["head"][1]))
    lines.append("Post pass (post D%.0f, mu %.2f, I %.1f kg m2):" % (P.fence_post_d, P.mu_guard, K.MODEL["I_swing"]))
    for p in pp:
        lines.append("  %.1f m/s: swing %.1f deg (to %.1f), post force max %d N, while sliding %d N, max stop hit: %s"
                     % (p["v"], p["swing_deg"], p["psi_max_deg"], p["F_post_max_N"], p["F_post_median_N"],
                        p["hit_max_stop"]))
    lines.append("Uncut per post: %d cm2 (strip x %d..%d), up to %d mm behind the post"
                 % (ma["missed_cm2"], ma["strip_x"][0], ma["strip_x"][1], ma["behind_mm"]))
    s = st["sec"]
    lines.append("Arm U section: I_y %.0f cm4, W_y %.1f cm3, W_z %.0f cm3" % (s["I_y"] / 1e4, s["W_y"] / 1e3,
                                                                       s["W_z"] / 1e3))
    lines.append("  on a float stop (x%.0f): %.0f Nm, %.0f MPa, %.0f N on the stop bar" % (DYN, st["M_vert_Nm"],
                                                                                    st["sigma_vert"],
                                                                                    st["F_float_stop_N"]))
    lines.append("  post force %.0f N (x%.0f) at the head: %.0f Nm, %.1f MPa" % (st["F_post_N"], DYN, st["M_post_Nm"],
                                                                            st["sigma_post"]))
    lines.append("  skid %.0f N, torsion %.0f Nm (x%.0f): %.0f MPa, twist %.1f deg (cover off)"
                 % (st["F_skid_N"], st["T_skid_Nm"], DYN, st["tau_twist"], st["twist_deg"]))
    lines.append("  pivot post: %.1f MPa; hanger: %.0f Nm -> %.0f N per bolt pair (M10 8.8 proof load 33 kN)"
                 % (st["sigma_pivot_post"], st["M_hanger_Nm"], st["F_bolt_N"]))
    lines.append("Robot with mower: %.0f kg, rear %.0f kg / front %.0f kg (%.0f %% front), right side %.0f %%, RR wheel "
                 "%.0f kg" % (al["total_kg"], al["rear_kg"], al["front_kg"], 100 * al["front_share"],
                              100 * al["right_share"], al["RR_kg"]))
    lines.append("Fence: head top %.0f mm (+%.0f float) -> bottom wire >= %.0f mm to mow straight under it; post line "
                 "x %.0f, wire x %.0f" % (fe["head_top"], fe["float_up"], fe["min_wire_central"], fe["post_x"],
                                          fe["wire_x"]))
    lines.append("Cost: about EUR %.0f in parts" % cost())
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
