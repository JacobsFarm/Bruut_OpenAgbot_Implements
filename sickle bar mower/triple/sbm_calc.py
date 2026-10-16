"""Calculations for the triple sickle bar mower (pure Python, no FreeCAD needed).

Use:  import sbm_calc; sbm_calc.report()
Masses and centres of gravity come from the FreeCAD model (build_sbm.mass_properties), see MODEL. Robot coordinates:
x = right, y = front, z = up, mm.
"""
import math

import sbm_params as P

G_ACC = 9.81
DYN = 2.0                       # dynamic factor for bumps when the wings are folded (transport)
HIT_N = 1000.0                  # backwards force on a wing tip when a shoe hits a molehill or a stone (estimated)

# robot 4WD ready to drive, from agbots/agbot comparison (estimated, not weighed)
ROBOT = {
    "robot_kg": 161.5,
    "robot_cg": (0.0, 95.0, 543.0),
    "battery_wh": 2400.0,       # 48 V 50 Ah
    "axle_spec_kg": 500.0,      # per axle, hub motor spec
}

# last measurement from the model (build_sbm.mass_properties, work position)
MODEL = {
    "total_kg": 210.2, "total_cg": (53.0, 302.0, 257.0),
    "front_mount_kg": 10.47, "front_mount_cg": (0.0, 478.0, 561.0),
    "links_kg": 6.94, "front_actuator_kg": 3.82,
    "front_head_kg": 52.2, "front_head_cg": (215.0, 936.0, 140.0),     # head frame + bar (rolls with it)
    "mid_frame_kg": 48.63, "mid_frame_cg": (0.0, 0.0, 453.0),
    "wing_kg": 36.95, "wing_cg": (1329.0, 74.0, 118.0),               # right wing (left mirrored)
    "wing_actuator_kg": 4.36, "controller_kg": 5.52,
    "knife_kg": {"F": (3.32, 3.50), "W": (2.67, 2.86)},               # (upper, lower)
}
DENSITIES = (1.0, 2.0, 3.0, 4.0)        # t DM/ha: thin .. heavy first cut


# ---------------------------------------------------------------------
# Knives
# ---------------------------------------------------------------------
def knife():
    """Kinematics of one knife (stroke 50, 600 rpm) and of the pair."""
    w = P.OMEGA
    e = P.ECC / 1000.0
    v_mean = 2 * P.stroke / 1000.0 * P.crank_rpm / 60.0
    return {"rpm": P.crank_rpm, "strokes_min": 2 * P.crank_rpm, "v_mean": v_mean, "v_max": w * e,
            "v_rel_max": 2 * w * e, "a_max": w ** 2 * e,
            "feed_mm": P.drive_speed * 1000.0 / (2 * P.crank_rpm / 60.0),        # travel per stroke
            "sections": {b: int(round(L / P.pitch)) for b, L in (("front", P.front_L), ("wing", P.wing_L))}}


def knife_forces():
    """Peak inertia force of each knife (N) and the force left over on the gearbox (the knives run 180 deg apart,
    their masses differ by the lower knife's extension)."""
    a = knife()["a_max"]
    out = {}
    for b, key in (("front", "F"), ("wing", "W")):
        up, low = MODEL["knife_kg"][key]
        out[b] = {"upper_N": up * a, "lower_N": low * a, "net_N": abs(up - low) * a,
                  "single_knife_equiv_N": (up + low) * a}
    return out


# ---------------------------------------------------------------------
# Power
# ---------------------------------------------------------------------
def e_cut(density=3.0):
    """Cutting energy (J/m2) for a sward of 'density' t DM/ha: P.e_cut is for 3 t DM/ha, scaled linearly with a
    floor of 40 % (stems are cut even in a thin sward)."""
    return P.e_cut * max(0.4, density / 3.0)


def bar_power(L, v=P.drive_speed, density=3.0):
    """Shaft power at the crank (W) of one bar of cut width L (mm) at v (m/s): idle + cutting."""
    idle = P.idle_W_m * L / 1000.0
    cut = e_cut(density) * L / 1000.0 * v
    return {"idle_W": idle, "cut_W": cut, "crank_W": idle + cut, "motor_shaft_W": (idle + cut) / P.eta_gear,
            "el_W": (idle + cut) / P.eta_gear / P.eta_motor, "load": (idle + cut) / P.eta_gear / P.motor_P}


def power(v=P.drive_speed, density=3.0):
    f = bar_power(P.front_L, v, density)
    w = bar_power(P.wing_L, v, density)
    el = f["el_W"] + 2 * w["el_W"]
    total = el + P.drive_W + draft()["N"] * v / 0.75
    return {"front": f, "wing": w, "mowing_el_W": el, "drive_W": total - el, "total_W": total,
            "I_A": total / P.battery_v}


def speed_limit(density, load=0.9, v_max=1.5):
    """Highest speed (m/s) at which the front motor (the most loaded) stays below 'load' of its rating."""
    v = v_max
    while v > 0.05 and bar_power(P.front_L, v, density)["load"] > load:
        v -= 0.01
    return v


def crank_torque(L, v=P.drive_speed, density=3.0):
    """Mean crank torque (Nm) and the peak from the knife inertia (net force of the pair x eccentricity)."""
    mean = bar_power(L, v, density)["crank_W"] / P.OMEGA
    key = "F" if L == P.front_L else "W"
    up, low = MODEL["knife_kg"][key]
    peak = mean * math.pi / 2.0 + (up + low) * knife()["a_max"] * P.ECC / 1000.0 / 2.0
    return {"mean_Nm": mean, "peak_Nm": peak, "motor_mean_Nm": mean / P.gear_ratio / P.eta_gear}


def capacity(v=P.drive_speed, eff=0.85):
    """Field capacity (ha/h) and area per battery charge."""
    ha_h = P.WIDTH / 1000.0 * v * 3600.0 / 10000.0 * eff
    p = power(v)
    hours = ROBOT["battery_wh"] * 0.9 / p["total_W"]
    return {"ha_h": ha_h, "run_h": hours, "ha_charge": ha_h * hours}


# ---------------------------------------------------------------------
# Forces on the robot
# ---------------------------------------------------------------------
def shoe_loads():
    """Weight on the shoes in work (N): the front bar and head frame rest on the 2 front shoes (float link slack),
    each wing on its 2 shoes (the hinge only locates it)."""
    front = MODEL["front_head_kg"] * G_ACC
    wing = MODEL["wing_kg"] * G_ACC
    return {"front_N": front, "wing_N": wing, "total_N": front + 2 * wing}


def draft():
    """Backwards force on the robot (N): cutting resistance + shoe friction."""
    cut = P.drag_N_m * P.WIDTH / 1000.0
    shoes = P.mu_shoe * shoe_loads()["total_N"]
    return {"cut_N": cut, "shoes_N": shoes, "N": cut + shoes}


def axle_loads(mode="work"):
    """Axle loads (kg) of robot + mower. work: bars on their shoes; transport: everything on the robot."""
    m_r = ROBOT["robot_kg"]
    items = [(m_r, ROBOT["robot_cg"][1])]
    total = MODEL["total_kg"]
    if mode == "work":
        carried = total - MODEL["front_head_kg"] - 2 * MODEL["wing_kg"]
        y = (total * MODEL["total_cg"][1] - MODEL["front_head_kg"] * MODEL["front_head_cg"][1]
             - 2 * MODEL["wing_kg"] * MODEL["wing_cg"][1]) / max(carried, 1e-6)
        items.append((carried, y))
    else:
        # transport: the head moves 53 mm forward with the lift; folded wings lie over the hinge (y unchanged)
        dy = P.head_shift(P.lift_max)[0]
        items.append((total, (total * MODEL["total_cg"][1] + MODEL["front_head_kg"] * dy) / max(total, 1e-6)))
    m = sum(k for k, _ in items)
    y = sum(k * yy for k, yy in items) / m
    wb = 2 * P.robot_axle_y
    front = m * (y + P.robot_axle_y) / wb
    return {"total_kg": m, "cg_y": y, "front_kg": front, "rear_kg": m - front, "front_share": front / m}


def front_actuator_force(lift):
    """Actuator tension (N) holding the head frame + bar at 'lift' (virtual work, dz/dAB numerically)."""
    d = 1.0
    dab = (P.act_length(lift - d) - P.act_length(lift + d)) / (2 * d)
    m = MODEL["front_head_kg"] + 0.5 * MODEL["links_kg"] + 0.5 * MODEL["front_actuator_kg"]
    return m * G_ACC / dab


def front_float():
    """How far the front bar can follow the ground with the actuator in the work setting (mm): down to lift_work,
    up until the float link slot is used up."""
    ab0 = P.act_length(P.lift_work)
    up = P.lift_work
    while ab0 - P.act_length(up + 1.0) <= P.float_slot and up < P.lift_max:
        up += 1.0
    return {"down_mm": P.lift_work, "up_mm": up}


def wing_torque(fold):
    """Torque (Nm) of the wing weight about the hinge at a fold angle (deg)."""
    hx, hz = P.hinge
    cx, cz = MODEL["wing_cg"][0] - hx, MODEL["wing_cg"][2] - hz
    a = math.radians(fold)
    arm = cx * math.cos(a) - cz * math.sin(a)
    return MODEL["wing_kg"] * G_ACC * arm / 1000.0


def wing_actuator_force(fold):
    """Actuator tension (N) to hold the wing at 'fold' (anchor pin at the outer end of its slot): torque / lever arm
    (perpendicular distance of the actuator line from the hinge)."""
    hx, hz = P.hinge
    bx, bz = P.lever_pin(fold)
    ax, az = P.anchor_x[1], P.ANCHOR_Z
    L = math.hypot(bx - ax, bz - az)
    ux, uz = (ax - bx) / L, (az - bz) / L
    arm = abs((bx - hx) * uz - (bz - hz) * ux)
    t = wing_torque(fold)
    return {"fold": fold, "torque_Nm": t, "arm_mm": arm, "F_N": t * 1000.0 / arm, "length": L}


def wing_fold():
    rows = [wing_actuator_force(f) for f in (0, 15, 30, 45, 60, 75, 90)]
    t = (P.wact_length(0.0) - P.wact_length(P.fold_max)) / P.wact_speed
    return {"rows": rows, "F_max_N": max(r["F_N"] for r in rows), "time_s": t,
            "act_range": (P.wact_length(P.fold_max), P.WACT_WORK), "float_deg": P.wing_float_range()}


def wing_stress():
    """Bending stress (MPa) in the bar at the inner end while the wing is lifted horizontally (weight x DYN), and in
    the hanger box when a shoe hits something (HIT_N backwards at the knife, 1.2 m out)."""
    m = MODEL["wing_kg"] * G_ACC * (MODEL["wing_cg"][0] - P.x_wing0) / 1000.0 * DYN
    b, t = P.beam
    flat = b * t ** 2 / 6.0
    sb, sh, st = P.stiff
    i_rhs = (sb * sh ** 3 - (sb - 2 * st) * (sh - 2 * st) ** 3) / 12.0
    w_bar = flat + i_rhs / (sh / 2.0)
    # hanger: 2 plates 80 x 12 below the box (z < 360), box above
    m_hit = HIT_N * (360.0 - P.hinge[1]) / 1000.0
    w_plates = 2 * (P.hanger_x[1] - P.hanger_x[0]) * P.hanger_t ** 2 / 6.0
    torsion = HIT_N * (P.x_wing0 + P.wing_L - P.hinge[0]) / 1000.0         # about z at the hinge
    couple = torsion * 1000.0 / (P.cross[0] + P.hanger_t)                  # along x on each hanger plate
    w_in = P.hanger_t * (P.hanger_x[1] - P.hanger_x[0]) ** 2 / 6.0
    return {"bar_M_Nm": m, "bar_sigma": m * 1000.0 / w_bar, "hanger_M_Nm": m_hit,
            "hanger_sigma": m_hit * 1000.0 / w_plates, "hit_torque_Nm": torsion, "pin_force_N": couple,
            "hanger_inplane_sigma": couple * (P.hanger_box_z - P.hinge[1]) / w_in}


def report():
    k = knife()
    print("Triple sickle bar mower: %g + 2 x %g = %g mm" % (P.front_L, P.wing_L, P.WIDTH))
    print("knife: %d rpm, %d strokes/min, mean %.2f m/s, max %.2f m/s (relative %.2f), %.0f mm travel per stroke"
          % (k["rpm"], k["strokes_min"], k["v_mean"], k["v_max"], k["v_rel_max"], k["feed_mm"]))
    for b, f in knife_forces().items():
        print("  %s knives: inertia %.0f / %.0f N, net on the gearbox %.0f N (single knife: %.0f N)"
              % (b, f["upper_N"], f["lower_N"], f["net_N"], f["single_knife_equiv_N"]))
    p = power()
    print("power at %.1f m/s, 3 t DM/ha: front %.0f W crank (motor %.0f %%), wing %.0f W (%.0f %%); mowing %.0f W el,"
          " total %.0f W (%.1f A)" % (P.drive_speed, p["front"]["crank_W"], 100 * p["front"]["load"],
                                      p["wing"]["crank_W"], 100 * p["wing"]["load"], p["mowing_el_W"], p["total_W"],
                                      p["I_A"]))
    for d in DENSITIES:
        print("  %.0f t DM/ha: speed limit %.2f m/s" % (d, speed_limit(d)))
    for L in (P.front_L, P.wing_L):
        c = crank_torque(L)
        print("  crank torque %g mm bar: mean %.1f Nm, peak %.1f Nm; motor %.2f Nm" % (L, c["mean_Nm"], c["peak_Nm"],
                                                                                    c["motor_mean_Nm"]))
    c = capacity()
    print("capacity %.2f ha/h, %.1f h per charge -> %.2f ha" % (c["ha_h"], c["run_h"], c["ha_charge"]))
    s = shoe_loads()
    d = draft()
    print("shoes: front %.0f N, each wing %.0f N; draft %.0f N (cutting %.0f, shoes %.0f)"
          % (s["front_N"], s["wing_N"], d["N"], d["cut_N"], d["shoes_N"]))
    for mode in ("work", "transport"):
        a = axle_loads(mode)
        print("axle loads %s: %.0f kg, front %.0f (%.0f %%), rear %.0f" % (mode, a["total_kg"], a["front_kg"],
                                                                        100 * a["front_share"], a["rear_kg"]))
    print("front actuator: %.0f N at work, %.0f N lifted; float %s" % (front_actuator_force(0.0),
                                                                     front_actuator_force(P.lift_max), front_float()))
    f = wing_fold()
    print("wing fold: max %.0f N, %.1f s, actuator %.0f .. %.0f, float %.1f .. %.1f deg"
          % (f["F_max_N"], f["time_s"], f["act_range"][0], f["act_range"][1], f["float_deg"][0], f["float_deg"][1]))
    for r in f["rows"]:
        print("   fold %2.0f: torque %5.0f Nm, arm %4.0f mm, F %5.0f N, length %.0f" % (r["fold"], r["torque_Nm"],
                                                                                    r["arm_mm"], r["F_N"],
                                                                                    r["length"]))
    w = wing_stress()
    print("wing bar at the hinge: %.0f Nm -> %.0f MPa; hanger plates %.0f MPa (backwards hit); hit torque %.0f Nm ->"
          " %.0f N on each plate, %.0f MPa in plane" % (w["bar_M_Nm"], w["bar_sigma"], w["hanger_sigma"],
                                                         w["hit_torque_Nm"], w["pin_force_N"],
                                                         w["hanger_inplane_sigma"]))
