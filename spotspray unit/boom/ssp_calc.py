"""Calculations for the spot sprayer (pure Python, no FreeCAD): fold kinematics and actuator force, camera footprint
and detection band, latency, spray rate and dose, tank and battery range, capacity, axle loads, stability, boom
strength.

    python ssp_calc.py          (or in FreeCAD: import ssp_calc; ssp_calc.report())
"""
import math

import ssp_params as P

G_ACC = 9.81

# last measurement from the model (build_ssp.mass_properties: steel 7850, aluminium 2700, PE 950 kg/m3, bought parts
# with their catalogue mass). Tank empty; the liquid is added here.
MODEL = {"kg": 90.8, "cg": (0.0, -302.0, 698.0), "wing_kg": 5.28, "wing_cg_r": 552.0, "wing_cg_z": 502.0,
         "boom_kg": 23.6, "boom_cg": (0.0, -843.0, 538.0), "mast_kg": 15.1, "tank_kg": 21.3}

ROBOT = {"robot_kg": P.robot_kg, "robot_cg": (0.0, 95.0, 543.0)}       # agbot comparison (estimated)
TANK_CG = (0.0, (P.tank_y[0] + P.tank_y[1]) / 2.0)                      # liquid centre (x, y); z from the level


# ---------------------------------------------------------------------
# Fold kinematics (right wing; the left wing is the mirror image). Coordinates in the x-z plane relative to the
# hinge axis H. phi = 0 working (horizontal), 90 = folded up.
# ---------------------------------------------------------------------
def rot(p, deg):
    """Rotate (x, z) counter-clockwise (seen from behind, x right, z up) = wing up for the right wing."""
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


BASE_REL = (P.act_base[0] - P.centre_half, P.act_base[1] - P.hinge_z)  # (-420, 63.6)


def lever_rel(phi):
    return rot(P.lever_pin, phi)


def act_length(phi):
    lx, lz = lever_rel(phi)
    return math.hypot(lx - BASE_REL[0], lz - BASE_REL[1])


def act_angle(phi):
    """Angle of the actuator axis above the horizontal (deg), right side, pointing from the base to the lever."""
    lx, lz = lever_rel(phi)
    return math.degrees(math.atan2(lz - BASE_REL[1], lx - BASE_REL[0]))


def act_arm(phi):
    """Perpendicular distance (mm) from the hinge axis to the actuator line."""
    lx, lz = lever_rel(phi)
    dx, dz = lx - BASE_REL[0], lz - BASE_REL[1]
    return abs(BASE_REL[0] * dz - BASE_REL[1] * dx) / math.hypot(dx, dz)


def phi_of_length(length):
    """Fold angle for an actuator length (bisection, the length falls monotonically with phi)."""
    lo, hi = -1.0, P.fold_stop
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if act_length(mid) > length:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def fold_time(phi0=0.0, phi1=P.fold_up):
    return abs(act_length(phi0) - act_length(phi1)) / P.act_speed


def phi_at(t, phi0, phi1):
    """Fold angle t seconds after the actuator starts moving from phi0 to phi1 (constant actuator speed)."""
    l0, l1 = act_length(phi0), act_length(phi1)
    s = min(abs(l1 - l0), P.act_speed * max(0.0, t))
    return phi_of_length(l0 + math.copysign(s, l1 - l0))


def wing_tip(phi):
    """Outer end of the wing (incl. the guard) relative to the hinge: (x, z)."""
    return rot((P.guard_x[1] - P.centre_half, 0.0), phi)


def actuator(wing_kg=None, r_cg=None):
    """Actuator force over the fold (N): gravity torque / arm. Returns a table and the extremes."""
    m = MODEL["wing_kg"] if wing_kg is None else wing_kg
    r = MODEL["wing_cg_r"] if r_cg is None else r_cg
    rows = []
    for phi in range(0, int(P.fold_up) + 1, 10):
        dz = MODEL["wing_cg_z"] - P.hinge_z                            # cg below the hinge axis
        t = m * G_ACC * rot((r, dz), phi)[0] / 1000.0                   # Nm, outward lever of the cg
        arm = act_arm(phi)
        rows.append((phi, round(act_length(phi), 1), round(act_angle(phi), 1), round(arm, 1),
                     round(t, 1), round(1000.0 * t / arm)))
    f_max = max(r_[5] for r_ in rows)
    l_work, l_fold, l_stop = act_length(0.0), act_length(P.fold_up), act_length(P.fold_stop)
    return {"rows": rows, "F_max": f_max, "reserve": P.act_force / f_max, "torque_0": rows[0][4],
            "L_work": l_work, "L_fold": l_fold, "L_stop": l_stop, "stroke_used": l_work - l_fold,
            "fits": P.act_closed <= l_stop and l_work <= P.act_closed + P.act_stroke,
            "t_fold": fold_time(), "power_W": f_max * P.act_speed / 1000.0}


# ---------------------------------------------------------------------
# Camera: rectilinear lens, pitched cam_pitch below the horizontal, at cam_pivot (robot coordinates)
# ---------------------------------------------------------------------
TAN_H = P.cam_px[0] * P.cam_pixel / 2.0 / P.cam_f
TAN_V = P.cam_px[1] * P.cam_pixel / 2.0 / P.cam_f


def cam_ray_ground(a, b, pitch=P.cam_pitch, pivot=P.cam_pivot):
    """Ground point (x, y) of the image point (a, b) = (tan across, tan up), or None above the horizon."""
    p = math.radians(pitch)
    d = (0.0, math.cos(p), -math.sin(p))
    u = (0.0, math.sin(p), math.cos(p))
    ray = (a, d[1] + b * u[1], d[2] + b * u[2])
    if ray[2] >= -1e-6:
        return None
    t = -pivot[2] / ray[2]
    return (pivot[0] + t * ray[0], pivot[1] + t * ray[1])


def row_at(t_slant, pitch=P.cam_pitch):
    """Image row b (tan up) whose centre ray has slant length t_slant to the ground."""
    p = math.radians(pitch)
    return (math.sin(p) - P.cam_pivot[2] / t_slant) / math.cos(p)


def camera(gsd_max=3.0, pitch=P.cam_pitch):
    """Footprint, ground resolution and the detection band: image rows where the image is wider than the boom
    (near limit) and finer than gsd_max mm/px (far limit)."""
    h = P.cam_pivot[2]
    p = math.radians(pitch)
    k = P.cam_pixel / P.cam_f
    t_near = P.work_width / (2.0 * TAN_H)                   # slant at which the image is as wide as the boom
    t_far = gsd_max / k
    out = {"hfov": 2 * math.degrees(math.atan(TAN_H)), "vfov": 2 * math.degrees(math.atan(TAN_V)), "h": h}
    out["axis_y"] = P.cam_pivot[1] + h / math.tan(p)
    out["axis_slant"] = h / math.sin(p)
    out["axis_width"] = 2.0 * out["axis_slant"] * TAN_H
    out["axis_gsd"] = out["axis_slant"] * k
    band = []
    for t in (t_near, t_far):
        b = row_at(t, pitch)
        b = max(-TAN_V, min(TAN_V, b))
        band.append(cam_ray_ground(0.0, b, pitch)[1])
    out["band_y"] = tuple(band)
    out["band_len"] = band[1] - band[0]
    bottom = cam_ray_ground(0.0, -TAN_V, pitch)
    top = cam_ray_ground(0.0, TAN_V, pitch)
    out["bottom_y"] = bottom[1] if bottom else None
    out["top_y"] = top[1] if top else None
    out["latency_dist"] = band[0] - P.boom_y                # last chance to see a weed -> nozzle line
    out["latency_s"] = out["latency_dist"] / (P.speed * 1000.0)
    out["frames_in_band"] = out["band_len"] / (P.speed * 1000.0) * P.cam_fps
    out["frame_step"] = P.speed * 1000.0 / P.cam_fps
    out["budget_ms"] = P.infer_ms + 1000.0 / P.cam_fps + P.valve_ms     # exposure/transfer + inference + valve
    return out


def footprint(y_max=None, n=24, pitch=P.cam_pitch):
    """Ground outline of the image (robot coordinates), cut at y_max ahead (far rows are useless)."""
    c = camera(pitch=pitch)
    y_max = c["band_y"][1] if y_max is None else y_max
    b_top = TAN_V
    top = cam_ray_ground(0.0, TAN_V, pitch)
    if top is None or top[1] > y_max:
        p = math.radians(pitch)
        t = None
        lo, hi = -TAN_V, TAN_V
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            g = cam_ray_ground(0.0, mid, pitch)
            if g is None or g[1] > y_max:
                hi = mid
            else:
                lo = mid
        b_top = lo
    pts = []
    for i in range(n + 1):                                  # bottom edge, left to right
        pts.append(cam_ray_ground(-TAN_H + 2 * TAN_H * i / n, -TAN_V, pitch))
    for i in range(n + 1):                                  # right edge, up
        pts.append(cam_ray_ground(TAN_H, -TAN_V + (b_top + TAN_V) * i / n, pitch))
    for i in range(n + 1):                                  # top (cut) edge, right to left
        pts.append(cam_ray_ground(TAN_H - 2 * TAN_H * i / n, b_top, pitch))
    for i in range(n + 1):                                  # left edge, down
        pts.append(cam_ray_ground(-TAN_H, b_top - (b_top + TAN_V) * i / n, pitch))
    return pts


def sees(x, y_rel, pitch=P.cam_pitch):
    """True when the ground point (x, y relative to the robot) lies in the detection band and inside the image."""
    c = camera(pitch=pitch)
    if not c["band_y"][0] <= y_rel <= c["band_y"][1]:
        return False
    dy = y_rel - P.cam_pivot[1]
    h = P.cam_pivot[2]
    p = math.radians(pitch)
    # camera coordinates of the point
    v = (x, dy, -h)
    d = (0.0, math.cos(p), -math.sin(p))
    u = (0.0, math.sin(p), math.cos(p))
    zc = v[1] * d[1] + v[2] * d[2]
    return zc > 0 and abs(v[0] / zc) <= TAN_H and abs((v[1] * u[1] + v[2] * u[2]) / zc) <= TAN_V


# ---------------------------------------------------------------------
# Spray
# ---------------------------------------------------------------------
def nozzle_flow(p=P.spray_p):
    return P.nozzle_q_3bar * math.sqrt(p / 3.0)


def spray(v=P.speed, p=P.spray_p):
    q = nozzle_flow(p)
    fan_w = 2.0 * P.nozzle_h * math.tan(math.radians(P.nozzle_angle / 2.0))
    rate = q / (P.nozzle_pitch / 1000.0 * v * 60.0) * 10000.0         # l/ha while the nozzle is open
    per_ha = rate * P.weed_cover
    q_all = P.n_nozzles * q
    return {"q_nozzle": q, "fan_w": fan_w, "overlap": fan_w - P.nozzle_pitch, "rate_l_ha": rate,
            "per_field_ha": per_ha, "q_all": q_all, "pump_ok": P.pump_q_3bar >= q_all,
            "q_max_open": P.pump_q_3bar / q, "ha_per_tank": P.tank_nominal / per_ha,
            "patch_extra": 2 * P.spray_margin + v * P.valve_ms, "valve_mm": v * P.valve_ms}


def patch(d_weed, v=P.speed):
    """Sprayed spot for a weed of diameter d_weed: length along y, number of nozzles, litres."""
    length = d_weed + 2 * P.spray_margin
    across = d_weed + 2 * P.spray_margin
    n = int(math.ceil(across / P.nozzle_pitch)) + 1         # worst case: the spot straddles a nozzle border
    t = length / (v * 1000.0)
    return {"length": length, "nozzles": n, "l": n * nozzle_flow() * t / 60.0, "s": t}


def capacity(v=P.speed):
    gross = P.work_width / 1000.0 * v * 3600.0 / 10000.0
    return {"gross_ha_h": gross, "net_ha_h": gross * P.field_eff}


# ---------------------------------------------------------------------
# Power, axle loads, stability, strength
# ---------------------------------------------------------------------
def power(v=P.speed):
    valves = P.n_nozzles * P.weed_cover * P.valve_w
    p_tool = P.pump_w + P.computer_w + valves
    p_total = p_tool + P.drive_w * v
    hours = P.battery_kwh * 1000.0 / p_total
    return {"P_tool": p_tool, "P_total": p_total, "hours": hours, "ha": hours * capacity(v)["net_ha_h"]}


def liquid_cg_z(litres):
    h = litres * 1e6 / ((2 * (P.tank_x - P.tank_wall)) * (P.tank_y[1] - P.tank_y[0] - 2 * P.tank_wall))
    return P.tank_z0 + P.tank_wall + h / 2.0, h


def masses(litres=P.tank_nominal, folded=False):
    """List of (kg, (x, y, z)) for robot, implement (wings out) and liquid."""
    ms = [(ROBOT["robot_kg"], ROBOT["robot_cg"]), (MODEL["kg"], MODEL["cg"])]
    if folded:     # wings up: both wing cg's move from their working height to the hinge + r
        dz = 2 * MODEL["wing_kg"] * (P.hinge_z + MODEL["wing_cg_r"] - MODEL["wing_cg_z"])
        cg = MODEL["cg"]
        ms[1] = (MODEL["kg"], (cg[0], cg[1], cg[2] + dz / MODEL["kg"]))
    if litres > 0:
        z, _ = liquid_cg_z(litres)
        ms.append((litres * P.liquid_density, (TANK_CG[0], TANK_CG[1], z)))
    return ms


def total(ms):
    m = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / m for i in range(3))
    return m, cg


def axle_loads(litres=P.tank_nominal, folded=False):
    m, cg = total(masses(litres, folded))
    front = m * (cg[1] + P.robot_axle_y) / P.robot_wheelbase
    return {"kg": m, "cg": cg, "front_kg": front, "rear_kg": m - front, "front_share": front / m,
            "wheel_max": max(front, m - front) / 2.0}


def stability(litres=P.tank_nominal, folded=True):
    """Static tip-over angle sideways (deg) and the slope at which the uphill wheels unload by half."""
    a = axle_loads(litres, folded)
    h = a["cg"][2]
    tip = math.degrees(math.atan(P.robot_wheel_x / h))
    half = math.degrees(math.atan(0.5 * P.robot_wheel_x / h))
    fwd = math.degrees(math.atan(min(P.robot_axle_y + a["cg"][1], P.robot_axle_y - a["cg"][1]) / h))
    return {"cg_z": h, "tip_side": tip, "half_unload_side": half, "tip_fore_aft": fwd}


def boom_strength(dyn=P.dyn):
    """Wing at the hinge, centre tube at the clamp plates, wing tip deflection, hinge pin."""
    m, r = MODEL["wing_kg"], MODEL["wing_cg_r"]
    w_mod_wing = (P.tube ** 4 - (P.tube - 2 * P.tube_wall_wing) ** 4) / (6.0 * P.tube)
    i_wing = (P.tube ** 4 - (P.tube - 2 * P.tube_wall_wing) ** 4) / 12.0
    m_hinge = m * G_ACC * r * dyn                                       # Nmm
    sig_wing = m_hinge / w_mod_wing
    q = m * G_ACC / P.wing_len
    defl = q * P.wing_len ** 4 / (8 * 70000.0 * i_wing)
    w_mod_c = (P.tube ** 4 - (P.tube - 2 * P.tube_wall_centre) ** 4) / (6.0 * P.tube)
    arm_c = P.centre_half - (P.web_x + P.clamp_x) + r
    centre_part = 0.25 * (MODEL["boom_kg"] - 2 * m) * G_ACC * (P.centre_half - P.web_x) / 2.0
    m_clamp = (m * G_ACC * arm_c + centre_part) * dyn
    sig_c = m_clamp / w_mod_c
    # hinge: the end plates take the compression below the hinge (lever = hinge 25 above the tube top, plate centre
    # 20 below the top -> 45 mm); the pin takes the tension
    f_pin = m_hinge / 45.0
    tau_pin = f_pin / (2 * math.pi * (P.hinge_pin_d / 2.0) ** 2)
    # hangers: boom weight hangs 220 mm behind the rear outer beam, sub plate bolts take it as a couple
    w_boom = MODEL["boom_kg"] * G_ACC * dyn
    lever = abs(MODEL["boom_cg"][1] - P.robot_lower_beam_y[0])
    couple = w_boom * lever / (P.robot_lower_beam_y[1] - P.robot_lower_beam_y[0])
    bolt = (couple + w_boom) / 4.0
    return {"sig_wing": sig_wing, "defl_tip": defl, "sig_centre": sig_c, "pin_tau": tau_pin, "pin_F": f_pin,
            "bolt_N": bolt, "bolt_safety": 0.8 * 640.0 * 58.0 / bolt}


def obstacle(post_d=150.0, clear=100.0, v=P.speed, phi_safe=None):
    """Folding the wing for a post at distance x_post from the robot centre line. Returns the fold angle needed,
    the time to reach it, how long before the post the fold must start and the length of the missed strip."""
    phi_safe = phi_safe if phi_safe is not None else 60.0
    t_up = fold_time(0.0, P.fold_up)
    t_down = t_up
    t_safe = fold_time(0.0, phi_safe)
    lead = v * 1000.0 * t_safe + post_d / 2.0 + clear
    missed = v * 1000.0 * (t_up + t_down) + post_d + 2 * clear
    missed_part = v * 1000.0 * 2 * t_safe + post_d + 2 * clear
    return {"t_up": t_up, "t_safe": t_safe, "lead_mm": lead, "missed_mm": missed, "missed_part_mm": missed_part,
            "phi_safe": phi_safe}


def report():
    a = actuator()
    c = camera()
    s = spray()
    cap = capacity()
    pw = power()
    full = axle_loads(P.tank_nominal)
    empty = axle_loads(0.0)
    st = stability(P.tank_nominal, folded=True)
    b = boom_strength()
    ob = obstacle()
    lines = ["=== Spot sprayer, folding boom: key figures ===",
             "Boom %.2f m, %d nozzles at %.0f mm, tips %.0f mm above the ground; fan %.0f deg -> %.0f mm wide on the "
             "ground (%.0f mm overlap)" % (P.work_width / 1000.0, P.n_nozzles, P.nozzle_pitch, P.nozzle_h,
                                           P.nozzle_angle, s["fan_w"], s["overlap"]),
             "Camera %.0f x %.0f deg FOV, %.2f m high, %.0f deg down: axis on the ground at y %.0f (%.2f m wide, "
             "%.1f mm/px)" % (c["hfov"], c["vfov"], c["h"] / 1000.0, P.cam_pitch, c["axis_y"], c["axis_width"] / 1000.0,
                              c["axis_gsd"]),
             "Detection band y %.0f .. %.0f (image >= boom width, <= 3 mm/px): %.0f frames per weed at %.1f m/s; "
             "last sight -> nozzles %.2f m = %.2f s (budget %.0f ms)" % (
                 c["band_y"][0], c["band_y"][1], c["frames_in_band"], P.speed, c["latency_dist"] / 1000.0,
                 c["latency_s"], c["budget_ms"]),
             "Spray: %.2f l/min per nozzle at %.1f bar -> %.0f l/ha where it sprays, %.1f l/ha over the field at "
             "%.0f %% cover; all 15 open %.1f l/min (pump %.1f l/min at 3 bar: %d nozzles at once)" % (
                 s["q_nozzle"], P.spray_p, s["rate_l_ha"], s["per_field_ha"], 100 * P.weed_cover, s["q_all"],
                 P.pump_q_3bar, int(s["q_max_open"])),
             "Tank %.0f l -> %.1f ha; capacity %.2f ha/h gross, %.2f ha/h net; battery %.1f h (%.0f W) -> %.1f ha" % (
                 P.tank_nominal, s["ha_per_tank"], cap["gross_ha_h"], cap["net_ha_h"], pw["hours"], pw["P_total"],
                 pw["ha"]),
             "Spot for a 300 mm dock: %.0f mm long, %d nozzles, %.3f l (valve %.0f ms = %.0f mm at %.1f m/s)" % (
                 patch(300.0)["length"], patch(300.0)["nozzles"], patch(300.0)["l"], P.valve_ms, s["valve_mm"],
                 P.speed),
             "Fold actuator: %.0f .. %.0f mm pin-pin (range %.0f .. %.0f, fits %s), stroke used %.0f, %.1f s up; "
             "max %.0f N (x %.1f reserve on %.0f N), torque at 0 deg %.0f Nm" % (
                 a["L_fold"], a["L_work"], P.act_closed, P.act_closed + P.act_stroke, a["fits"], a["stroke_used"],
                 a["t_fold"], a["F_max"], a["reserve"], P.act_force, a["torque_0"]),
             "  phi  length  angle  arm  torque  force: " + "; ".join(
                 "%d %.0f %.1f %.0f %.0f %d" % r for r in a["rows"]),
             "Obstacle: wing safe (%.0f deg) after %.1f s -> start folding %.1f m before the post; strip without "
             "spray %.1f m (fold to %.0f deg and back) or %.1f m (fully up and down)" % (
                 ob["phi_safe"], ob["t_safe"], ob["lead_mm"] / 1000.0, ob["missed_part_mm"] / 1000.0, ob["phi_safe"],
                 ob["missed_mm"] / 1000.0),
             "Axle loads full: %.0f kg, rear %.0f / front %.0f kg (%.0f %% front), wheel max %.0f kg of %.0f; "
             "empty: rear %.0f / front %.0f kg" % (full["kg"], full["rear_kg"], full["front_kg"],
                                                    100 * full["front_share"], full["wheel_max"], P.wheel_load_max,
                                                    empty["rear_kg"], empty["front_kg"]),
             "Stability (full, wings up): cg %.0f mm high, tips sideways at %.0f deg, uphill wheels half unloaded at "
             "%.0f deg; fore-aft %.0f deg" % (st["cg_z"], st["tip_side"], st["half_unload_side"], st["tip_fore_aft"]),
             "Boom x %.1f dynamic: wing at the hinge %.0f MPa (alu), tip sags %.1f mm static; centre tube at the "
             "clamps %.0f MPa (steel); hinge pin %.0f N, %.1f MPa; sub plate bolts %.0f N (x %.0f)" % (
                 P.dyn, b["sig_wing"], b["defl_tip"], b["sig_centre"], b["pin_F"], b["pin_tau"], b["bolt_N"],
                 b["bolt_safety"])]
    print("\n".join(lines))
    return lines


if __name__ == "__main__":
    report()
