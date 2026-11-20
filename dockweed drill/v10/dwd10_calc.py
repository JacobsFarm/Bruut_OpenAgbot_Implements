"""Calculations of the dockweed drill v10 (pure Python, no FreeCAD needed).

v10 = v8 with the X motor fixed at the right side plate (as v9) and the Z axis on linear guides (2 rails HGR20 on 2
rail beams RHS 50 x 40 x 4 on the X slide, 4 carriages HGH20CA on the Z sled).
Here: spindle and cutter, cutting energy, Z axis (Linak LA36: force, speed, current, duty and heat per plant
interval), Z guide (carriage loads, life, rail beam deflection, bolts to the slide, friction), X guide (2 round tubes
between the side plates, 3 plain bushes), belt drive, cross beams, cycle per plant, spindle shaft, headstock, axle loads.

    import dwd10_calc
    dwd10_calc.report()
"""
import math

import dwd10_params as P

G_ACC = 9.81
E_STEEL = 210e3                      # N/mm2

# last measurement from the model (build_dwd10.mass_properties: steel 7850 kg/m3, bought parts as fixed masses)
MODEL = {
    "implement_kg": 131.2,
    "implement_cg": (105.0, -793.0, 740.0),   # robot coordinates, working pose x 150, cutter 150 deep
    "x_moving_kg": 75.4,                      # everything that moves with the X axis (slide, housings, rails, Z sled, can)
    "x_moving_cg": (154.0, -869.0, 600.0),
    "z_moving_kg": 39.2,
    "z_moving_cg": (157.0, -913.0, 448.0),
    "pot_kg": 5.9,
    "tool_kg": 2.5,
}

# geometry from the parameters (same stack as dwd10_parts.stack)
SLIDE_V1 = P.slide_v1
SPINDLE_V = P.sb_back_v0 + P.sb_back_t + P.spindle_dv
SPINDLE_Y = P.v_to_y(SPINDLE_V)
CARRIAGE_V = P.rail_v0 + (P.blk_H1 + P.blk_H) / 2          # load centre of the carriages in v
REAR_AXLE_Y = -P.robot_wheel_y
FRONT_AXLE_Y = P.robot_wheel_y
WHEELBASE = FRONT_AXLE_Y - REAR_AXLE_Y
TRACK = 2 * P.robot_wheel_x


def rect_tube_I(b, t):
    return (b ** 4 - (b - 2 * t) ** 4) / 12.0


def rhs_I(h, b, t):
    """I (mm4) of a rectangular hollow section for bending in the direction of h (h = depth in the load direction)."""
    return (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12.0


def round_tube(D, t):
    """(area mm2, I mm4) of a round tube."""
    d = D - 2 * t
    return math.pi / 4 * (D * D - d * d), math.pi / 64 * (D ** 4 - d ** 4)


# ---------------------------------------------------------------------
# Spindle and cutter (as v6..v8)
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
# Z guide: 2 rails HGR20 on 2 rail beams (cantilevers from the X slide), 4 carriages HGH20CA on the sled
# ---------------------------------------------------------------------
def z_lift_force():
    return (MODEL["z_moving_kg"] + MODEL["pot_kg"]) * G_ACC


def _cantilever_defl(P_n, a, x, EI):
    """Deflection at x of a cantilever (fixed at 0) with a point load P_n at a."""
    if x <= a:
        return P_n * x * x * (3 * a - x) / (6 * EI)
    return P_n * a * a * (3 * x - a) / (6 * EI)


def z_guide(F_side=P.side_force, z=-P.depth_max, direction="x"):
    """Z guide on linear rails with the tool underside at z. Side force F_side at the cutting level (40 above the
    tool underside), in x (across the rails) or v (towards the robot).
    - carriage loads: the sled is a rigid body on 4 carriages, 2 levels blk_z apart (they move with the tool, so the
      arm from the cut to the carriages is constant); the Z force on the spindle (behind the actuator) and the
      side force in x (behind the rail plane) add couples that the carriages take as forces in v;
    - deflection of the cutter: the 2 rail beams are cantilevers from the lowest bolt in the slide (both beams
      together in x, each beam in v), the sled is rigid between its 2 carriage levels; carriage and rail stiffness
      (preload ZA, about 250 N/um) are neglected (< 0.01 mm);
    - friction: balls (mu 0.005) and the seals of 4 carriages."""
    z_cut = z + 40.0
    z_lo, z_hi = z + P.blk_z[0], z + P.blk_z[1]
    d = z_hi - z_lo
    arm = z_lo - z_cut
    R_lo = F_side * (arm + d) / d                       # per level (2 carriages)
    R_hi = F_side * arm / d
    e_v = SPINDLE_V - CARRIAGE_V                        # spindle behind the load centre of the carriages
    T_side = F_side * e_v if direction == "x" else 0.0  # couple about z from a side force in x
    R_twist = T_side / (2 * P.zr_dx) / 2.0              # per carriage, in v
    lever_v = SPINDLE_V - P.act_v
    R_zf = P.z_force_limit * lever_v / d / 2.0          # per carriage, in v (Z force on the spindle, actuator in front)
    W = MODEL["z_moving_kg"] * G_ACC
    cg_v = P.robot_beam_rear_face - MODEL["z_moving_cg"][1]
    R_w = W * abs(cg_v - P.act_v) / d / 2.0             # weight hanging behind the actuator
    # equivalent load per carriage (HIWIN: P = |radial| + |lateral|), lower carriage is the worst
    if direction == "x":
        lat, rad = R_lo / 2.0, R_twist + R_zf + R_w
    else:
        lat, rad = 0.0, R_lo / 2.0 + R_zf + R_w
    P_eq = lat + rad
    L10_km = (P.blk_C / P_eq) ** 3 * 50.0
    # rail beams: fixed at the lowest bolt, loads at the carriage levels (distances below the fixed point)
    z_fix = P.zb_bolt_z[0]
    a_lo, a_hi, a_cut = z_fix - z_lo, z_fix - z_hi, z_fix - z_cut
    dv, dx, t = P.zb_size
    I = 2 * rhs_I(dx, dv, t) if direction == "x" else 2 * rhs_I(dv, dx, t)
    EI = E_STEEL * I

    def defl(at):
        out = 0.0
        for Pn, a in ((R_lo, a_lo), (-R_hi, a_hi)):
            if a > 0:
                out += _cantilever_defl(Pn, a, at, EI) if at > 0 else 0.0
        return out
    d_lo, d_hi = defl(max(a_lo, 0.0)), defl(max(a_hi, 0.0))
    slope = (d_lo - d_hi) / d
    d_cut = d_lo + slope * arm
    twist = 0.0
    if direction == "x" and a_lo > 0:                   # sled turns about z: the 2 beams bend opposite in v
        EI_v = E_STEEL * rhs_I(dv, dx, t)
        F_t = T_side / (2 * P.zr_dx)
        dv_beam = F_t * a_lo ** 3 / (3 * EI_v)
        twist = 2 * dv_beam / (2 * P.zr_dx) * e_v
    loads_total = 2 * (R_lo + R_hi) + 4 * (R_zf + R_w) + 2 * T_side / (2 * P.zr_dx)
    f_cut = P.blk_mu * loads_total + 4 * P.blk_seal_n
    f_idle = P.blk_mu * 4 * (R_w * 2) + 4 * P.blk_seal_n
    return {"arm_mm": arm, "carriage_pitch_mm": d, "level_lower_n": R_lo, "level_upper_n": R_hi,
            "per_carriage_lower_lateral_n": lat, "per_carriage_lower_radial_n": rad,
            "from_side_force_twist_n": R_twist, "from_z_force_n": R_zf, "from_weight_n": R_w,
            "equivalent_load_n": P_eq, "static_safety": P.blk_C0 / P_eq, "L10_km": L10_km,
            "beam_free_length_mm": a_lo, "defl_lower_carriage_mm": d_lo, "defl_cut_mm": d_cut + twist,
            "friction_cutting_n": f_cut, "friction_idle_n": f_idle,
            "rails_kg": 2 * P.rail_kg_m * (P.rail_z[1] - P.rail_z[0]) / 1000.0}


def rail_beam_bolts(F_side=P.side_force):
    """4x M8 per rail beam through the slide (z 725..995) at the deepest pose: a side force in x twists the bolt
    group in the plane of the slide (shear); a side force in v pries the beam off the slide (tension, pivot at the
    lower edge of the slide)."""
    z_cut = -P.depth_max + 40.0
    zs = P.zb_bolt_z
    zc = sum(zs) / len(zs)
    M = F_side * (zc - z_cut) / 2.0                     # per beam [Nmm]
    r2 = sum((z - zc) ** 2 for z in zs)
    shear = M * max(abs(z - zc) for z in zs) / r2 + F_side / 2.0 / len(zs)
    piv = P.slide_z[0]
    Mv = F_side * (piv - z_cut) / 2.0
    s2 = sum((z - piv) ** 2 for z in zs)
    tension = Mv * (zs[-1] - piv) / s2
    slip = 0.2 * 18000.0                                # M8 8.8 preload about 18 kN, mu 0.2 steel on alu
    return {"shear_per_bolt_n": shear, "tension_per_bolt_n": tension, "slip_per_bolt_n": slip,
            "safety_slip": slip / shear}


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
    """(phase, duration s, current A) of the actuator per plant."""
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
    """Heat in the motor of the LA36 ~ I^2 R: mean I^2 over a plant interval against I_max^2 x 20 % (rule of thumb,
    copper loss; as v7 / v8)."""
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
# X axis: 2 round tubes D50 x 4 between the side plates, slide on 3 plain bushes, belt drive with the motor fixed
# ---------------------------------------------------------------------
def x_force_max():
    """Holding force of the belt drive (N): 5:1 gearbox, efficiency 0.95."""
    r = P.x_pulley_T * P.htd_pitch / (2 * math.pi) / 1000.0
    return P.stepper_T * P.x_gear * 0.95 / r


def _span():
    return P.xbar_L - 2 * P.end_plate_t


def guide(x=0.0, x_moving_kg=None, z_force=P.z_force_limit):
    """X guide with the slide at x (as v8). Weight: 2 housings on the upper tube and 1 on the lower tube; the upper
    tube carries 2/3 (estimated). Z force on the spindle behind the tubes -> couple about the x axis -> force in v on
    each tube. Simply supported (bolts in the plug) and fixed (stiff side plate) as limits; point load at x."""
    m_x = MODEL["x_moving_kg"] if x_moving_kg is None else x_moving_kg
    A, I = round_tube(P.xg_d, P.xg_t)
    L = _span()
    a = L / 2 + x
    b = L - a
    F_z = m_x * G_ACC * 2.0 / 3.0                       # most loaded tube (upper)
    zl, zh = P.xbar_z
    cg_v = P.robot_beam_rear_face - MODEL["x_moving_cg"][1]
    F_w = m_x * G_ACC * (cg_v - P.tube_v) / (zh - zl)   # tipping moment of the weight -> force in v per tube
    F_c = z_force * (SPINDLE_V - P.tube_v) / (zh - zl)  # Z force -> force in v per tube
    F_v = F_w + F_c

    def simple(F):
        return F * a * a * b * b / (3 * E_STEEL * I * L)

    def fixed(F):
        return F * a ** 3 * b ** 3 / (3 * E_STEEL * I * L ** 3)

    d_v = simple(F_v)
    R = math.hypot(F_z / 2.0, F_v / 2.0)                # per housing on the upper tube (2 housings)
    bush_p = R / (P.xg_d * P.xg_house[1])
    F_fr = P.xg_mu * (abs(F_z) + m_x * G_ACC / 3.0 + 2 * F_v)
    return {"span_mm": L, "area_mm2": A, "I_mm4": I, "load_z_upper_tube_n": F_z, "force_v_per_tube_n": F_v,
            "from_weight_v_n": F_w, "from_z_force_v_n": F_c,
            "defl_z_simple_mm": simple(F_z), "defl_z_fixed_mm": fixed(F_z),
            "defl_v_simple_mm": d_v, "defl_v_fixed_mm": fixed(F_v),
            "twist_deg": math.degrees(2 * d_v / (zh - zl)), "house_upper_n": R, "bush_pressure_mpa": bush_p,
            "friction_n": F_fr, "accel_m_s2": (x_force_max() - F_fr) / m_x,
            "tubes_kg": 2 * A * L * 7.85e-6, "plate_reaction_n": F_z * max(a, b) / L}


def belt():
    """Belt HTD5M 15 mm round 2 pulleys 20T (as v9): length, wrap, the force the belt must carry."""
    g = guide(0.0)
    F = min(x_force_max(), g["friction_n"] + MODEL["x_moving_kg"] * 2.0)   # friction + 2 m/s2 acceleration
    return {"length_mm": P.belt_len, "pulley_centres_mm": 2 * P.pulley_x, "working_force_n": F,
            "holding_force_n": x_force_max(), "htd5m_15_allowed_n": 1100.0,
            "motor_cable_moves": False}


def tube_bolts():
    """2x M10 per tube end in the plug: shear (weight + Z force), slide at x_max."""
    g = guide(x=P.x_max)
    R = math.hypot(g["plate_reaction_n"], g["force_v_per_tube_n"])      # per tube end
    return {"shear_per_bolt_n": R / 2.0, "m10_8_8_shear_n": 0.6 * 800 * 58.0}


def frame_beams():
    """Cross beams 40 x 40 x 3: cantilever from upright (x hs_x) to side plate; the reaction of the side plate
    (slide at x_max) spread over the 2 beams. The fixed X motor (2.5 kg) hangs on the right side plate."""
    g = guide(x=P.x_max)
    a = P.xbar_L / 2 - P.end_plate_t - P.hs_x
    I = rect_tube_I(P.xbeam[0], P.xbeam[1])
    F = (g["plate_reaction_n"] * 1.5 + 2.5 * G_ACC) / 2.0
    d = F * a ** 3 / (3 * E_STEEL * I)
    d_v = g["force_v_per_tube_n"] * a ** 3 / (3 * E_STEEL * I)
    sigma = max(F, g["force_v_per_tube_n"]) * a / (I / (P.xbeam[0] / 2))
    return {"cantilever_mm": a, "force_per_beam_n": F, "defl_z_mm": d, "defl_v_mm": d_v, "stress_mpa": sigma}


# ---------------------------------------------------------------------
# Cycle per plant (X moves while the robot drives: overlap)
# ---------------------------------------------------------------------
def cycle(depth=P.depth_std, dx=333.0):
    """Phases per plant (s). dx = mean X move (1/3 of the stroke). The can touches the sward when the cutter
    underside is still pot_rim above the ground; from there the cutter plunges pot_rim + depth at plunge_v and comes
    back turning until the can comes free (2x as fast)."""
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
    e_x = 60.0 * ph["x_move"]                            # stepper + gearbox during the X move (estimated)
    return (e_spin + e_act + e_x + 60.0 * cycle_time(depth)) / 3600.0      # + 60 W electronics and camera


# ---------------------------------------------------------------------
# Spindle shaft
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


def cutter_deflection(F=P.side_force, z=-P.depth_max):
    """Total deflection of the cutter at side force F in x: rail beams + spindle shaft (X tubes: see guide)."""
    return z_guide(F, z)["defl_cut_mm"] + shaft(F)["defl_mm"]


# ---------------------------------------------------------------------
# Robot: axle loads and headstock
# ---------------------------------------------------------------------
def axle_loads(x=None, soil_force=0.0, pot_on_ground=False, robot_kg=P.robot_kg, robot_cg_y=P.robot_cg_y):
    """Wheel loads with the spindle at x and an upward force of the ground on the cutter (soil_force, N)."""
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
# Report
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
        "z_guide_x_300N_deepest": _r(z_guide(), 2),
        "z_guide_v_300N_deepest": _r(z_guide(direction="v"), 2),
        "z_guide_x_100N_deepest": _r(z_guide(P.side_force_normal), 2),
        "z_guide_x_300N_driving": _r(z_guide(z=P.drive_z), 2),
        "rail_beam_bolts": _r(rail_beam_bolts(), 1),
        "cutter_deflection_mm (300 N / 100 N, deepest, rails + shaft)": (round(cutter_deflection(), 2),
                                                                          round(cutter_deflection(P.side_force_normal), 2)),
        "x_force_max_n": round(x_force_max()),
        "x_guide_x0": _r(guide(0.0)),
        "x_guide_x_max": _r(guide(P.x_max)),
        "x_belt": _r(belt(), 0),
        "x_tube_bolts": _r(tube_bolts(), 0),
        "frame_beams": _r(frame_beams()),
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
