"""Calculations for the field marker (pure Python, no FreeCAD needed).

Use:  import mrk_calc; mrk_calc.report()
Masses of the implement come from the FreeCAD model (build_mrk.mass_properties), see MODEL.
Robot coordinates: x = right, y = front, z = up, mm. The marker is behind the robot.
"""
import math

import mrk_params as P

G_ACC = 9.81

# last measurement from the model (build_mrk.mass_properties, steel 7850, aluminium 2700, PVC 1400 kg/m3,
# bought parts with a fixed mass), nozzle in the middle, parked
MODEL = {"kg": 35.2, "cg": (-98.0, -734.0, 566.0), "fixed_kg": 17.7, "x_slide_kg": 17.5, "y_slide_kg": 8.55,
         "z_slide_kg": 3.1, "control_box_kg": 3.5}

# robot 4WD ready to drive, from agbots/agbot comparison/weight_traction.json (estimated, not weighed)
ROBOT = {
    "robot_kg": 161.5,
    "robot_cg": (0.0, 95.0, 543.0),
    "battery_wh": 2400.0,       # 48 V 50 Ah
    "drive_w": 150.0,           # average driving between the points (stop and go, grass), estimated
    "axle_spec_kg": 500.0,      # per axle, hub motor spec
}
HALF_BASE = -P.robot_axle_y     # 500

# stage, estimated: friction of the carriages and seals, efficiency of the ball screw, stiffness of the X profile
FRICTION_N = 20.0
ETA_SCREW = 0.9
XM_I = 90e4                     # mm4, 80 x 55 belt module profile, bending in the vertical plane (estimated)
XM_W = 22e3                     # mm3
E_ALU = 70000.0


# ---------------------------------------------------------------------
# Envelope and geometry
# ---------------------------------------------------------------------
def envelope():
    zc0, zc1 = P.zc_range
    return {"x": (-P.x_stroke / 2.0, P.x_stroke / 2.0),
            "y": (P.y_tool_front - P.y_stroke, P.y_tool_front),
            "shroud_bottom": (zc0 + P.SHROUD_BOTTOM_DZ, zc1 + P.SHROUD_BOTTOM_DZ),
            "behind_tyre": P.robot_tire_rear_y - P.y_tool_front,
            "antenna_phase_z": antenna_height(),
            "nozzle_height": nozzle_height()}


def antenna_height():
    """Phase centre of the mast antenna above the ground (mast is fixed in z)."""
    return P.mast_z[1] + P.ant_stem[1] + P.ant_phase_dz


def nozzle_height(lift=None):
    """Nozzle above the ground while the shroud rests on it (lift = compression at the touch-off)."""
    lift = P.ZC_WORK - P.zc_for_ground(0.0, 0.0) if lift is None else lift
    return P.NOZZLE_DZ - P.SHROUD_BOTTOM_DZ - abs(lift)


# ---------------------------------------------------------------------
# Accuracy
# ---------------------------------------------------------------------
def accuracy(source="rtk", h=None, lever=0.0):
    """Error budget (mm, 1 sigma, horizontal). lever = horizontal distance antenna -> nozzle (0: coaxial mast)."""
    h = antenna_height() if h is None else h
    items = {
        "position": P.rtk_sigma if source == "rtk" else P.ts_sigma,
        "tilt (IMU)": h * math.tan(math.radians(P.imu_sigma_deg)),
        "heading": lever * math.tan(math.radians(P.heading_sigma_deg)),
        "stage": P.stage_sigma,
        "tool and ground": P.tool_sigma,
    }
    sigma = math.sqrt(sum(v ** 2 for v in items.values()))
    return {"items": items, "sigma": sigma, "p95": 2.0 * sigma}


def tilt_error(deg, h=None):
    """Shift of the nozzle point when the robot tilts 'deg' degrees and nothing corrects it (mm)."""
    h = antenna_height() if h is None else h
    return h * math.tan(math.radians(deg))


def robot_antenna_lever():
    """Horizontal distance from the robot's own antenna to the nozzle (nominal): the lever arm if the mast
    antenna were left out."""
    return math.hypot(P.robot_gnss[0], P.robot_gnss[1] - P.y_tool_nom)


# ---------------------------------------------------------------------
# Robot: axle loads and the allowed press force
# ---------------------------------------------------------------------
def axle_loads(press=0.0, y_tool=P.y_tool_nom):
    """(rear, front) in kg. 'press' = downward force of the tool on the ground (N): it pushes the robot up at the
    tool, behind the rear axle, and unloads the rear axle by (500 + 500 - y_tool) / 1000 x press."""
    ms = [(ROBOT["robot_kg"], ROBOT["robot_cg"]), (MODEL["kg"], MODEL["cg"])]
    W = sum(m for m, _ in ms) * G_ACC - press
    my = sum(m * G_ACC * cg[1] for m, cg in ms) - press * y_tool
    n_front = (W * HALF_BASE + my) / (2 * HALF_BASE)
    n_rear = W - n_front
    return {"rear_kg": n_rear / G_ACC, "front_kg": n_front / G_ACC, "front_share": n_front / W}


def press_limit(rear_share_min=0.5, y_tool=P.y_tool_front - P.y_stroke):
    """Press force (N) at which the rear axle keeps 'rear_share_min' of its load without pressing, rear-most tool."""
    r0 = axle_loads(0.0, y_tool)["rear_kg"] * G_ACC
    k = (HALF_BASE - y_tool) / (2 * HALF_BASE)          # unloading of the rear axle per N press force
    return {"F_half": (1.0 - rear_share_min) * r0 / k, "F_lift": r0 / k, "k": k}


# ---------------------------------------------------------------------
# Drives
# ---------------------------------------------------------------------
def move_time(d, v, a):
    """Trapezoid (or triangle) profile: time (s) for a move of d mm at max speed v (mm/s), acceleration a (mm/s2)."""
    d = abs(d)
    d_acc = v * v / a
    if d <= d_acc:
        return 2.0 * math.sqrt(d / a)
    return 2.0 * v / a + (d - d_acc) / v


def drives():
    """Forces and motor torques. X: belt on a 20 tooth HTD-5M pulley. Y, Z: SFU1605 ball screw."""
    r_p = P.xm_pulley_pd / 2000.0
    fx = MODEL["x_slide_kg"] * P.x_a / 1000.0 + FRICTION_N
    tx = fx * r_p
    fy = MODEL["y_slide_kg"] * P.y_a / 1000.0 + FRICTION_N
    ty = fy * P.sm_lead / 1000.0 / (2 * math.pi * ETA_SCREW)
    fz = MODEL["z_slide_kg"] * (G_ACC + P.z_a / 1000.0) + FRICTION_N
    tz = fz * P.sm_lead / 1000.0 / (2 * math.pi * ETA_SCREW)
    f_max = 2 * math.pi * ETA_SCREW * P.nema_torque_run / (P.sm_lead / 1000.0)
    t_press = P.press_max * P.sm_lead / 1000.0 / (2 * math.pi * ETA_SCREW)
    # ball screw runs back: the Z slide falls without power unless the motor has a brake
    t_back = MODEL["z_slide_kg"] * G_ACC * P.sm_lead / 1000.0 * ETA_SCREW / (2 * math.pi)
    rpm = {"x": P.x_v / (math.pi * P.xm_pulley_pd) * 60.0, "y": P.y_v / P.sm_lead * 60.0, "z": P.z_v / P.sm_lead * 60.0}
    return {"F_x": fx, "T_x": tx, "F_y": fy, "T_y": ty, "F_z": fz, "T_z": tz, "F_z_max": f_max, "T_press": t_press,
            "T_backdrive": t_back, "rpm": rpm, "reserve_x": P.nema_torque_run / tx}


# ---------------------------------------------------------------------
# Paint
# ---------------------------------------------------------------------
def spray():
    h = nozzle_height()
    d = 2.0 * h * math.tan(math.radians(P.spray_angle / 2.0)) + 5.0
    area = math.pi * (d / 2000.0) ** 2
    per_can = P.can_line_m * P.can_line_w / (area * P.dot_overhead)
    to_ring = P.NOZZLE_DZ - (P.ring_top_dz - P.shroud_ring_t)        # nozzle -> underside of the ring
    cone_at_ring = 2.0 * to_ring * math.tan(math.radians(P.spray_angle / 2.0)) + 5.0
    return {"nozzle_h": h, "dot_d": d, "dots_per_can": per_can, "cone_at_ring": cone_at_ring,
            "ring_hole": P.shroud_hole}


def flyby_smear(v=0.3, t=0.15):
    """Length added to a dot when spraying while driving at v (m/s) with a valve time t (s): fly-by mode."""
    return v * t * 1000.0


# ---------------------------------------------------------------------
# Cycle time and capacity
# ---------------------------------------------------------------------
def cycle(spacing=3.0, dx=200.0, dy=60.0):
    """Time per point (s): drive 'spacing' m, settle, measure, stage correction (dx, dy mm, X and Y together),
    Z down (fast, then slow until touch-off), spray, Z up, photo + log."""
    t = {}
    t["drive"] = move_time(spacing * 1000.0, P.drive_speed * 1000.0, P.drive_acc * 1000.0)
    t["settle"] = P.settle_s
    t["measure"] = P.measure_s
    t["stage"] = max(move_time(dx, P.x_v, P.x_a), move_time(dy, P.y_v, P.y_a))
    z_fast = P.ZC_PARK - P.ZC_WORK - P.z_touch_zone
    t["z_down"] = move_time(z_fast, P.z_v, P.z_a) + P.z_touch_zone / P.z_touch_v
    t["spray"] = 2 * P.servo_s + P.spray_s
    t["z_up"] = move_time(P.ZC_PARK - P.ZC_WORK, P.z_v, P.z_a)
    t["photo_log"] = P.photo_s
    total = sum(t.values())
    return {"times": t, "total": total, "per_hour": 3600.0 / total}


def cycle_flyby(spacing=3.0, v=0.3):
    t = spacing / v
    return {"total": t, "per_hour": 3600.0 / t, "smear_mm": flyby_smear(v, P.servo_s)}


# ---------------------------------------------------------------------
# Mount and X profile
# ---------------------------------------------------------------------
def mount_check(dyn=2.0):
    """Hangers: the weight hangs behind both rear lower beams. The plate tips about the rear bolts (y -575) and
    presses against the front beam (y -425); the rear M10 (4) take the tension. Factor 'dyn' for shocks."""
    m = MODEL["kg"] - MODEL["control_box_kg"]
    W = m * G_ACC * dyn
    y_bolt, y_front = P.robot_rear_beam_y
    c = W * (y_bolt - MODEL["cg"][1]) / (y_front - y_bolt)
    t_rear = W + c
    per_bolt = t_rear / 4.0
    # X profile: X slide at the far end of the stroke, cantilever from the nearest hanger
    arm = max(abs(P.xm_x[0]) - P.hanger_x, P.xm_x[1] - P.hanger_x)
    arm_slide = abs(P.xc_mid - P.x_stroke / 2.0) - P.hanger_x
    f = MODEL["x_slide_kg"] * G_ACC * dyn
    M = f * arm_slide
    sigma = M / XM_W
    defl = f * arm_slide ** 3 / (3.0 * E_ALU * XM_I)
    return {"bolt_tension_N": per_bolt, "bolt_safety": 46000.0 / per_bolt, "x_overhang": arm,
            "x_bending_MPa": sigma, "x_deflection_mm": defl}


def power():
    """Average electrical power (W) of the marker: 3 closed-loop steppers mostly holding, servo, GNSS, controller."""
    p = 3 * 15.0 + 10.0 + 3.0 + 5.0
    hours = 0.8 * ROBOT["battery_wh"] / (p + ROBOT["drive_w"])
    return {"P_marker_W": p, "hours": hours}


def report():
    e = envelope()
    a = accuracy("rtk")
    ts = accuracy("ts")
    lines = ["=== Field marker (simple): key figures ===",
             "Nozzle: x %+.0f..%+.0f, y %.0f..%.0f (%.0f mm behind the rear tyres), shroud bottom %+.0f..%+.0f mm" % (
                 e["x"][0], e["x"][1], e["y"][0], e["y"][1], e["behind_tyre"], e["shroud_bottom"][0],
                 e["shroud_bottom"][1]),
             "Antenna phase centre %.0f mm above the ground, coaxial with the nozzle" % e["antenna_phase_z"],
             "Accuracy RTK: %s -> 1 sigma %.1f mm, 95 %% %.0f mm" % (
                 ", ".join("%s %.1f" % kv for kv in a["items"].items()), a["sigma"], a["p95"]),
             "Accuracy total station: 1 sigma %.1f mm, 95 %% %.0f mm" % (ts["sigma"], ts["p95"]),
             "Without tilt correction: 3 degrees roll = %.0f mm; robot antenna instead of the mast (lever %.0f mm): "
             "+%.0f mm from heading" % (tilt_error(3.0), robot_antenna_lever(),
                                       robot_antenna_lever() * math.tan(math.radians(P.heading_sigma_deg)))]
    for press in (0.0, 30.0, P.press_max):
        al = axle_loads(press)
        lines.append("Axle loads, tool press %.0f N: rear %.0f kg, front %.0f kg (%.0f %% front)" % (
            press, al["rear_kg"], al["front_kg"], 100 * al["front_share"]))
    pl = press_limit()
    lines.append("Press force rear-most: %.0f N keeps half the rear axle load, %.0f N lifts the rear wheels "
                 "(%.2f N per N)" % (pl["F_half"], pl["F_lift"], pl["k"]))
    d = drives()
    lines.append("X: %.0f N, %.2f Nm (%.1f x reserve at %.1f Nm), %.0f rpm; Y: %.0f N, %.3f Nm; Z: %.0f N, %.3f Nm" % (
        d["F_x"], d["T_x"], d["reserve_x"], P.nema_torque_run, d["rpm"]["x"], d["F_y"], d["T_y"], d["F_z"], d["T_z"]))
    lines.append("Z: up to %.0f N at %.1f Nm -> limit the current to %.2f Nm for %.0f N; back-drive torque %.3f Nm "
                 "(detent ~%.2f Nm holds it unpowered; brake motor for rough fields)" % (
                     d["F_z_max"], P.nema_torque_run, d["T_press"], P.press_max, d["T_backdrive"], P.nema_detent))
    s = spray()
    lines.append("Spray: nozzle %.0f mm above the ground, dot ~Ø%.0f mm, ~%.0f dots per 500 ml can; cone Ø%.0f at "
                 "the ring hole Ø%.0f" % (s["nozzle_h"], s["dot_d"], s["dots_per_can"], s["cone_at_ring"], s["ring_hole"]))
    c = cycle()
    lines.append("Cycle at 3 m spacing: %s -> %.1f s, %.0f points/h" % (
        ", ".join("%s %.1f" % kv for kv in c["times"].items()), c["total"], c["per_hour"]))
    f = cycle_flyby()
    lines.append("Fly-by (no stop, no shroud) at 0.3 m/s: %.0f points/h, dot %.0f mm longer" % (f["per_hour"],
                                                                                               f["smear_mm"]))
    m = mount_check()
    lines.append("Hangers: %.0f N per rear M10 (x %.0f safe); X module %.0f mm overhang, %.1f MPa, %.2f mm "
                 "deflection (x 2 shock)" % (m["bolt_tension_N"], m["bolt_safety"], m["x_overhang"], m["x_bending_MPa"],
                                            m["x_deflection_mm"]))
    pw = power()
    lines.append("Power: marker ~%.0f W, with driving -> %.1f h on a full battery" % (pw["P_marker_W"], pw["hours"]))
    print("\n".join(lines))
    return lines


if __name__ == "__main__":
    report()
