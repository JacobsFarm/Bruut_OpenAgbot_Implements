"""Calculations for the in-row finger weeder (pure Python, no FreeCAD): arm kinematics, knife forces, stepper move
time (torque curve, inertia, soil load), the zone left around each plant, camera footprint and latency, parallelogram
lift and actuator, capacity, power, axle loads.

    python irw_calc.py          (or in FreeCAD: import irw_calc; irw_calc.report())
"""
import math

import irw_params as P

G_ACC = 9.81

# last measurement from the model (build_irw.mass_properties: steel 7850 kg/m3, bought parts with their catalogue
# mass). MODEL is updated by hand after a rebuild.
MODEL = {"kg": 55.1, "cg": (0.0, 13.0, 485.0), "unit_kg": 14.5, "arm_kg": 1.58, "arm_J": 0.0488, "frame_kg": 15.6}


# ---------------------------------------------------------------------
# Arm kinematics. Right unit, local u = x - row_x (+ = outwards), y as the robot. theta = 0: arm straight back.
# ---------------------------------------------------------------------
def finger_uv(theta):
    a = math.radians(theta)
    return (P.shaft_uv[0] - P.arm_r * math.sin(a), P.shaft_uv[1] - P.arm_r * math.cos(a))


def knife_corners(theta, row="right"):
    """Knife outline (4 points, x-y in robot coordinates) for the arm angle theta. The knife lies across the travel at
    theta_in and turns with the arm."""
    fu, fv = finger_uv(theta)
    d = math.radians(-(theta - P.theta_in))          # rotation of the arm in the u-y plane (seen from above)
    c, s = math.cos(d), math.sin(d)
    pts = []
    for du, dv in ((-P.knife_w / 2, -P.knife_l / 2), (P.knife_w / 2, -P.knife_l / 2), (P.knife_w / 2, P.knife_l / 2),
                   (-P.knife_w / 2, P.knife_l / 2)):
        u = fu + du * c - dv * s
        v = fv + du * s + dv * c
        pts.append((u, v))
    sx = 1.0 if row == "right" else -1.0
    x0 = P.row_x[1] if row == "right" else P.row_x[0]
    return [(x0 + sx * u, v) for (u, v) in pts]


def swing():
    """Swing in -> out: angle, how far the finger moves sideways and backwards."""
    fi, fo = finger_uv(P.theta_in), finger_uv(P.theta_out)
    return {"d_theta": P.theta_in - P.theta_out, "du": fo[0] - fi[0], "dv": fo[1] - fi[1], "in": fi, "out": fo,
            "inner_edge_out": fo[0] - P.knife_w / 2.0}


# ---------------------------------------------------------------------
# Knife forces in the soil
# ---------------------------------------------------------------------
def knife_forces(depth=P.work_depth):
    """Draft (along the travel) and the sideways resistance when the knife swings, per finger (N)."""
    shank_cm2 = P.shank[1] * max(0.0, depth - P.knife_t) / 100.0
    draft = P.soil_specific * P.knife_w * depth / 100.0 + P.soil_shank * shank_cm2
    lateral = P.soil_specific * P.knife_l * depth / 100.0 + P.soil_specific * P.shank[0] * max(0.0, depth - P.knife_t) / 100.0
    return {"draft": draft, "lateral": lateral}


def load_torque(theta, inward=True):
    """Soil torque on the shaft (Nm) against the motion: the draft pulls the finger back (straight behind the shaft),
    so it helps the swing out and works against the swing in; the sideways resistance always works against."""
    f = knife_forces()
    du = P.shaft_uv[0] - finger_uv(theta)[0]           # lever of the draft about the shaft
    t_draft = f["draft"] * du / 1000.0
    t_lat = f["lateral"] * P.arm_r * math.cos(math.radians(theta)) / 1000.0
    return t_lat + (t_draft if inward else -t_draft)


def holding_torque():
    """Torque to hold the finger in the row line against the draft (Nm at the shaft and at the motor)."""
    t = load_torque(P.theta_in, inward=True) - knife_forces()["lateral"] * P.arm_r * math.cos(math.radians(P.theta_in)) / 1000.0
    return {"shaft": t, "motor": t / (P.gear_ratio * P.gear_eff), "reserve": P.motor_T_hold * P.gear_ratio * P.gear_eff / t}


# ---------------------------------------------------------------------
# Stepper move (time-optimal with the torque curve, used share torque_use, symmetric accel / decel)
# ---------------------------------------------------------------------
def motor_torque(rpm):
    pts = P.motor_T_curve
    if rpm <= pts[0][0]:
        return pts[0][1]
    for (r0, t0), (r1, t1) in zip(pts[:-1], pts[1:]):
        if rpm <= r1:
            return t0 + (t1 - t0) * (rpm - r0) / (r1 - r0)
    return pts[-1][1]


def inertia(arm_J=None):
    """Inertia at the shaft (kg m2): arm + finger (from the model) + rotor and gearbox through the ratio squared."""
    arm_J = MODEL["arm_J"] if arm_J is None else arm_J
    return arm_J + (P.J_rotor + P.J_gear) * P.gear_ratio ** 2


def move(theta0, theta1, dt=0.0005):
    """Simulate a swing theta0 -> theta1 (deg). Accelerate with the usable torque minus the soil load, brake the same
    way (mirror), speed limited by motor_rpm_max. Returns time, peak speed and the profile [(t, theta)]."""
    J = inertia()
    total = abs(theta1 - theta0)
    sgn = 1.0 if theta1 > theta0 else -1.0
    inward = theta1 > theta0
    w_max = P.motor_rpm_max / P.gear_ratio * 2.0 * math.pi / 60.0
    th, w, t = 0.0, 0.0, 0.0
    prof = [(0.0, 0.0)]
    acc_ang, acc_t = 0.0, 0.0
    while th < total / 2.0:
        rpm = abs(w) * 60.0 / (2.0 * math.pi) * P.gear_ratio
        avail = P.torque_use * motor_torque(rpm) * P.gear_ratio * P.gear_eff
        load = load_torque(theta0 + sgn * th, inward)
        a = max(0.0, (avail - load) / J)
        if w >= w_max:
            a, w = 0.0, w_max
            break
        w += a * dt
        th += math.degrees(w * dt)
        t += dt
        prof.append((t, th))
    acc_ang, acc_t = th, t
    cruise = total - 2.0 * acc_ang
    t_cruise = math.radians(max(0.0, cruise)) / w if w > 0 else 0.0
    t_move = 2.0 * acc_t + t_cruise
    # full profile: accel, cruise, mirrored decel
    full = list(prof)
    if t_cruise > 0:
        full.append((acc_t + t_cruise, acc_ang + cruise))
    for (ta, tha) in reversed(prof[:-1]):
        full.append((t_move - ta, total - tha))
    return {"t": t_move, "w_peak": w, "rpm_peak": w * 60.0 / (2.0 * math.pi) * P.gear_ratio, "J": J,
            "load_max": max(load_torque(theta0 + sgn * total * k / 10.0, inward) for k in range(11)),
            "T_avail_0": P.torque_use * motor_torque(0.0) * P.gear_ratio * P.gear_eff,
            "profile": [(tt, theta0 + sgn * a) for (tt, a) in full], "theta0": theta0, "theta1": theta1}


_MOVES = {}


def moves():
    if not _MOVES:
        _MOVES["out"] = move(P.theta_in, P.theta_out)
        _MOVES["in"] = move(P.theta_out, P.theta_in)
    return _MOVES


def theta_during(kind, tau):
    """Arm angle tau seconds after the start of a swing ('out' or 'in')."""
    m = moves()[kind]
    prof = m["profile"]
    if tau <= 0.0:
        return prof[0][1]
    if tau >= m["t"]:
        return prof[-1][1]
    lo, hi = 0, len(prof) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if prof[mid][0] <= tau:
            lo = mid
        else:
            hi = mid
    (t0, a0), (t1, a1) = prof[lo], prof[hi]
    return a0 + (a1 - a0) * (tau - t0) / (t1 - t0) if t1 > t0 else a1


# ---------------------------------------------------------------------
# The zone around each plant
# ---------------------------------------------------------------------
def plant_zone(v=P.speed):
    """When to swing out and back in, relative to the plant (knife centre y - plant y, mm), and the length of the row
    line that the knife does not pass over per plant."""
    m = moves()
    clear = P.safe_r + P.knife_l / 2.0 + P.margin            # knife centre to the stem along y, knife fully out
    vm = v * 1000.0
    out_start = -(clear + vm * m["out"]["t"])                 # start the swing out so it ends at -clear
    in_start = clear
    # row line (u = 0) is covered while the knife's inner edge is at u <= 0: in the swing out until the finger has
    # moved knife_w / 2, in the swing in from that point on
    frac_out = _cover_frac("out")
    frac_in = _cover_frac("in")
    gap = (in_start + vm * m["in"]["t"] * frac_in - P.knife_l / 2.0) - (out_start + vm * m["out"]["t"] * frac_out +
                                                                        P.knife_l / 2.0)
    return {"clear": clear, "out_start": out_start, "in_start": in_start, "gap": gap,
            "gap_share": gap / P.plant_spacing, "t_cycle": P.plant_spacing / (v * 1000.0),
            "t_swings": m["out"]["t"] + m["in"]["t"]}


def _cover_frac(kind, n=200):
    """Share of the swing time during which the knife still covers the row line (inner edge at u <= 0)."""
    m = moves()[kind]
    t_hit = None
    for i in range(n + 1):
        tau = m["t"] * i / float(n)
        u = finger_uv(theta_during(kind, tau))[0] - P.knife_w / 2.0
        covers = u <= 0.0
        if kind == "out" and not covers:
            t_hit = tau
            break
        if kind == "in" and covers:
            t_hit = tau
            break
    return (t_hit if t_hit is not None else m["t"]) / m["t"]


# ---------------------------------------------------------------------
# Camera (pinhole, pitched forward by cam_pitch from straight down)
# ---------------------------------------------------------------------
def cam_ray_ground(a, b, pitch=P.cam_pitch):
    """Ground point (x, y) of the ray at sensor offsets a (across, mm, + = right) and b (along, mm, + = forward)."""
    cx, cy, cz = P.cam_xyz
    p = math.radians(pitch)
    # camera axis: down, tilted forward; image 'up' = forward
    ax = (0.0, math.sin(p), -math.cos(p))
    fw = (0.0, math.cos(p), math.sin(p))
    rt = (1.0, 0.0, 0.0)
    d = [ax[i] * P.cam_f + rt[i] * a + fw[i] * b for i in range(3)]
    if d[2] >= -1e-9:
        return None
    s = -cz / d[2]
    return (cx + s * d[0], cy + s * d[1])


def camera():
    sw = P.cam_px[0] * P.cam_pixel / 2.0
    sh = P.cam_px[1] * P.cam_pixel / 2.0
    hfov = 2.0 * math.degrees(math.atan(sw / P.cam_f))
    vfov = 2.0 * math.degrees(math.atan(sh / P.cam_f))
    corners = [cam_ray_ground(a, b) for a, b in ((-sw, -sh), (sw, -sh), (sw, sh), (-sw, sh))]
    near = cam_ray_ground(0.0, -sh)[1]
    far = cam_ray_ground(0.0, sh)[1]
    w_near = corners[1][0] - corners[0][0]
    gsd_nadir = P.cam_xyz[2] * P.cam_pixel / P.cam_f
    knife_y = finger_uv(P.theta_in)[1]
    seen = (far - near) / (P.speed * 1000.0)
    latency = (near - knife_y) / (P.speed * 1000.0)
    budget = 1000.0 / P.cam_fps + P.infer_ms
    rows_in = all(abs(x) + P.canopy_d[1] / 2.0 <= w_near / 2.0 for x in P.row_x)
    return {"hfov": hfov, "vfov": vfov, "corners": corners, "near": near, "far": far, "w_near": w_near,
            "gsd": gsd_nadir, "frames": seen * P.cam_fps, "latency_s": latency, "dist_to_knife": near - knife_y,
            "odo_mm": P.odo_err * (far - knife_y), "budget_ms": budget, "rows_in": rows_in}


def footprint():
    return camera()["corners"]


# ---------------------------------------------------------------------
# Parallelogram, lift actuator
# ---------------------------------------------------------------------
def head_offset(lift):
    """Translation (dy, dz) of the unit head for a lift at the pins (mm), and the link angle (deg)."""
    b = math.asin(max(-1.0, min(1.0, lift / P.link_len)))
    return (P.link_len * (1.0 - math.cos(b)), lift, math.degrees(b))


def act_length(lift=0.0):
    dy, dz, _ = head_offset(lift)
    bu, by, bz = P.act_base
    eu, ey, ez = P.act_end
    return math.hypot((ey + dy) - by, (ez + dz) - bz)


def act_angle(lift=0.0):
    """Angle of the actuator axis in the y-z plane (deg, atan2(dz, dy)) from the base to the end pin."""
    dy, dz, _ = head_offset(lift)
    return math.degrees(math.atan2((P.act_end[2] + dz) - P.act_base[2], (P.act_end[1] + dy) - P.act_base[1]))


def lift(unit_kg=None):
    unit_kg = MODEL["unit_kg"] if unit_kg is None else unit_kg
    l0, l1 = act_length(0.0), act_length(P.lift_travel)
    # force along the actuator to hold the unit: weight / sin of the actuator angle (actuator pulls up-forward)
    ang = math.radians(abs(act_angle(P.lift_travel)))
    f = unit_kg * G_ACC / max(0.2, math.sin(ang))
    return {"L_work": l0, "L_lift": l1, "stroke_used": l0 - l1, "fits": P.act_closed <= l1 and l0 <= P.act_closed +
            P.act_stroke, "F": f, "reserve": P.act_force / f, "t": (l0 - l1) / P.act_speed}


# ---------------------------------------------------------------------
# Capacity, power, loads
# ---------------------------------------------------------------------
def capacity(v=P.speed):
    w = 2.0 * P.row_spacing / 1000.0
    gross = w * v * 3600.0 / 10000.0
    return {"width_m": w, "gross_ha_h": gross, "net_ha_h": gross * P.field_eff,
            "plants_h": 2.0 * v * 3600.0 * 1000.0 / P.plant_spacing * P.field_eff}


def power(v=P.speed):
    pz = plant_zone(v)
    duty = pz["t_swings"] / pz["t_cycle"]
    stepper = 2.0 * (P.stepper_w_idle + duty * (P.stepper_w_move - P.stepper_w_idle))
    draft = 2.0 * knife_forces()["draft"] * v
    total = P.drive_w + draft + stepper + P.computer_w + 20.0     # 20 W camera + LEDs
    hours = P.battery_kwh * 1000.0 / total
    return {"stepper": stepper, "duty": duty, "draft_W": draft, "P_total": total, "hours": hours,
            "ha": hours * capacity(v)["net_ha_h"]}


def axle_loads(kg=None, cg=None):
    kg = MODEL["kg"] if kg is None else kg
    cg = MODEL["cg"] if cg is None else cg
    m = P.robot_kg + kg
    y = (P.robot_kg * P.robot_cg[1] + kg * cg[1]) / m
    z = (P.robot_kg * P.robot_cg[2] + kg * cg[2]) / m
    front = m * (0.5 + y / P.robot_wheelbase)
    return {"kg": m, "cg_y": y, "cg_z": z, "front_kg": front, "rear_kg": m - front,
            "wheel_max": max(front, m - front) / 2.0}


def report():
    sw = swing()
    f = knife_forces()
    m = moves()
    h = holding_torque()
    pz = plant_zone()
    c = camera()
    lf = lift()
    cap = capacity()
    pw = power()
    ax = axle_loads()
    lines = ["=== In-row finger weeder, 2 rows: key figures ===",
             "Rows at x %+.1f / %+.1f (%.0f mm apart, robot wheels in the inter-row centre); plants every %.0f mm" % (
                 P.row_x[0], P.row_x[1], P.row_spacing, P.plant_spacing),
             "Arm %.0f mm on a vertical shaft %.0f mm beside the row: in %.1f deg (finger on the row line), out %.1f deg"
             " -> swing %.1f deg, finger %.0f mm sideways, %.0f mm back; knife inner edge %.0f mm from the row when "
             "out (safe zone %.0f)" % (P.arm_r, P.shaft_uv[0], P.theta_in, P.theta_out, sw["d_theta"], sw["du"],
                                       -sw["dv"], sw["inner_edge_out"], P.safe_r),
             "Knife %.0f x %.0f mm at %.0f mm deep: draft %.0f N, sideways %.0f N per finger; holding in the row %.1f "
             "Nm at the shaft = %.2f Nm at the motor (x %.1f of the holding torque)" % (
                 P.knife_w, P.knife_l, P.work_depth, f["draft"], f["lateral"], h["shaft"], h["motor"], h["reserve"]),
             "Stepper NEMA 23 %.1f Nm + %d:1: inertia at the shaft %.4f kg m2 (arm %.4f); usable %.1f Nm at the shaft "
             "at standstill; swing out %.0f ms, in %.0f ms (soil load up to %.1f Nm, peak %.0f rpm at the motor)" % (
                 P.motor_T_hold, P.gear_ratio, m["out"]["J"], MODEL["arm_J"], m["in"]["T_avail_0"],
                 1000 * m["out"]["t"], 1000 * m["in"]["t"], m["in"]["load_max"], m["in"]["rpm_peak"]),
             "Around each plant: swing out starts %.0f mm before the stem, back in %.0f mm after it; row line not "
             "passed by the knife %.0f mm of %.0f (%.0f %%); %.2f s per plant, swings take %.2f s" % (
                 -pz["out_start"], pz["in_start"], pz["gap"], P.plant_spacing, 100 * pz["gap_share"], pz["t_cycle"],
                 pz["t_swings"]),
             "Camera %.0f x %.0f deg, %.0f mm high, %.0f deg forward: ground y %.0f .. %.0f, %.0f mm wide at the near "
             "edge (both rows + leaves: %s), %.2f mm/px; plant seen in %.0f frames; image edge -> knife %.0f mm = "
             "%.2f s (needs %.0f ms), odometry error <= %.0f mm" % (
                 c["hfov"], c["vfov"], P.cam_xyz[2], P.cam_pitch, c["near"], c["far"], c["w_near"], c["rows_in"],
                 c["gsd"], c["frames"], c["dist_to_knife"], c["latency_s"], c["budget_ms"], c["odo_mm"]),
             "Lift: actuator %.0f -> %.0f mm (closed %.0f, stroke %.0f, fits %s), %.0f N to hold the unit (x %.1f), "
             "%.1f s up %.0f mm" % (lf["L_work"], lf["L_lift"], P.act_closed, P.act_stroke, lf["fits"], lf["F"],
                                   lf["reserve"], lf["t"], P.lift_travel),
             "Capacity %.2f m at %.1f m/s: %.3f ha/h gross, %.3f ha/h net, %.0f plants/h" % (
                 cap["width_m"], P.speed, cap["gross_ha_h"], cap["net_ha_h"], cap["plants_h"]),
             "Power: steppers %.0f W (duty %.0f %%), knife draft %.0f W, total %.0f W -> %.1f h, %.2f ha on %.1f kWh" % (
                 pw["stepper"], 100 * pw["duty"], pw["draft_W"], pw["P_total"], pw["hours"], pw["ha"], P.battery_kwh),
             "Mass %.1f kg (model), cg (%.0f, %.0f, %.0f); robot + weeder %.0f kg: front %.0f / rear %.0f kg, "
             "max %.0f kg per wheel of %.0f" % (MODEL["kg"], MODEL["cg"][0], MODEL["cg"][1], MODEL["cg"][2], ax["kg"],
                                               ax["front_kg"], ax["rear_kg"], ax["wheel_max"], P.wheel_load_max)]
    print("\n".join(lines))
    return lines


if __name__ == "__main__":
    report()
