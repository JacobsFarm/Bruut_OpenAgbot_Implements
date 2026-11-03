"""Calculations for the potato disease scout (pure Python, no FreeCAD): wing swing kinematics and actuator force,
camera footprint and resolution, flash light and exposure, capacity, energy, data, castor and link loads, kingpin and
arm strength, axle loads and stability.

    python dsc_calc.py          (or in FreeCAD: import dsc_calc; dsc_calc.report())
"""
import math

import dsc_params as P

G_ACC = P.g

# last measurement from the model (build_dsc.mass_properties: steel 7850, aluminium 2700, PVC 1400 kg/m3, bought
# parts with their catalogue mass). Wings out.
MODEL = {"kg": 135.0, "cg": (0.0, 1025.0, 1156.0), "hood_kg": 119.8, "hood_cg": (0.0, 1086.0, 1184.0),
         "wing_kg": 32.0, "wing_cg_rel": (897.0, -209.0), "wing_cg_z": 1174.0, "mount_kg": 15.2,
         "mount_cg": (0.0, 537.0, 928.0), "cg_folded": (0.0, 1678.0, 1184.0)}


# ---------------------------------------------------------------------
# Wing swing (right wing; the left one is the mirror image). Plan view, beta = 0 working, 90 = folded forward.
# Local wing coordinates relative to the kingpin: s along the wing (outwards), t = y - pivot y.
# ---------------------------------------------------------------------
def rot(p, deg):
    a = math.radians(deg)
    return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))


def to_abs(rel, beta):
    r = rot(rel, beta)
    return (P.pivot[0] + r[0], P.pivot[1] + r[1])


def act_end(beta):
    return to_abs(P.act_end_rel, beta)


def act_length(beta):
    ex, ey = act_end(beta)
    return math.hypot(ex - P.act_base[0], ey - P.act_base[1])


def act_angle(beta):
    """Direction of the actuator in plan (deg from +x), from the base pin to the rod end."""
    ex, ey = act_end(beta)
    return math.degrees(math.atan2(ey - P.act_base[1], ex - P.act_base[0]))


def act_arm(beta):
    """Perpendicular distance (mm) from the kingpin axis to the actuator line."""
    ex, ey = act_end(beta)
    bx, by = P.act_base
    px, py = P.pivot
    dx, dy = ex - bx, ey - by
    return abs((px - bx) * dy - (py - by) * dx) / math.hypot(dx, dy)


def beta_of_length(length):
    lo, hi = -1.0, P.fold + 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if act_length(mid) < length:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def fold_time():
    return (act_length(P.fold) - act_length(0.0)) / P.act_speed


def beta_at(t, b0=0.0, b1=P.fold):
    """Swing angle t seconds after the actuator starts from b0 towards b1 (constant actuator speed)."""
    l0, l1 = act_length(b0), act_length(b1)
    s = min(abs(l1 - l0), P.act_speed * max(0.0, t))
    return beta_of_length(l0 + math.copysign(s, l1 - l0))


def swing():
    l0, l1 = act_length(0.0), act_length(P.fold)
    arms = [act_arm(b) for b in range(0, 91, 5)]
    m = MODEL
    w_kg = m["wing_kg"]
    r_cg = math.hypot(*m["wing_cg_rel"])
    # torque about the kingpin: bushing friction (wing weight as a moment on 2 bushings), wind on the wing side,
    # curtains dragged sideways through the haulm (only when swinging in the crop)
    bush_h = P.sleeve[3] - P.sleeve[2]
    moment = w_kg * G_ACC * m["wing_cg_rel"][0] / 1000.0             # N m, wing hanging off the kingpin
    bush_f = 2.0 * moment / (bush_h / 1000.0)
    t_fric = P.pin_mu * (bush_f + w_kg * G_ACC) * P.pin_d / 2000.0
    wing_area = (P.wing_len / 1000.0) * ((P.roof_top - P.curtain_z[0]) / 1000.0)
    q = 0.5 * 1.2 * P.wind ** 2
    t_wind = q * wing_area * 0.8 * (P.hood_d / 1000.0 + P.wing_len / 2000.0)
    t_crop = P.curtain_drag * (P.wing_len / 1000.0) * (P.hood_d / 1000.0 + P.wing_len / 2000.0)
    t_need = t_fric + t_wind + t_crop
    f_need = t_need / (min(arms) / 1000.0)
    return {"act_l0": round(l0, 1), "act_l90": round(l1, 1), "stroke_used": round(l1 - l0, 1),
            "stroke_reserve": round(P.act_stroke - (l1 - l0), 1), "closed_fits": l0 >= P.act_closed - 0.5,
            "fold_s": round(fold_time(), 1), "arm_min": round(min(arms), 1), "arm_max": round(max(arms), 1),
            "torque_friction": round(t_fric, 1), "torque_wind": round(t_wind, 1), "torque_crop": round(t_crop, 1),
            "torque_need": round(t_need, 1), "force_need": round(f_need), "force_reserve": round(P.act_force / f_need, 1),
            "wing_r_cg": round(r_cg)}


def width(beta):
    """Overall width (mm) of the hood with both wings at swing angle beta."""
    s0, s1 = P.centre_half - P.pivot_x, P.half_width - P.pivot_x
    t0, t1 = P.hood_y[0] - P.pivot[1], P.hood_y[1] - P.pivot[1]
    return 2 * max(P.centre_half, max(to_abs((s, t), beta)[0] for s in (s0, s1) for t in (t0, t1)))


def folded_extent():
    """Plan extent (x) of a folded wing: x 60 .. 600, so 1.20 m transport width."""
    pts = [(P.centre_half - P.pivot_x, P.hood_y[0] - P.pivot[1]), (P.half_width - P.pivot_x, P.hood_y[1] - P.pivot[1])]
    xs = [to_abs(p, P.fold)[0] for p in pts]
    ys = [to_abs(p, P.fold)[1] for p in pts]
    return {"x": (round(min(xs)), round(max(xs))), "y": (round(min(ys)), round(max(ys))),
            "transport_width": round(2 * max(xs))}


# ---------------------------------------------------------------------
# Cameras and light
# ---------------------------------------------------------------------
def sensor():
    return (P.cam_px[0] * P.cam_pixel, P.cam_px[1] * P.cam_pixel)


def camera():
    sw, sh = sensor()
    fov = (2 * math.degrees(math.atan(sw / 2 / P.cam_f)), 2 * math.degrees(math.atan(sh / 2 / P.cam_f)))
    out = {"sensor_mm": (round(sw, 2), round(sh, 2)), "fov_deg": (round(fov[0], 1), round(fov[1], 1))}
    rows = []
    for zc in (P.canopy_z[0], 600.0, P.canopy_z[1]):
        dist = P.cam_lens_z0 - zc
        across = sw / P.cam_f * dist
        along = sh / P.cam_f * dist
        step = along * (1.0 - P.overlap_along)
        fps = P.speed * 1000.0 / step
        coc = 2 * P.cam_pixel
        dof = 2 * P.cam_n * coc * dist ** 2 / P.cam_f ** 2
        rows.append({"canopy_z": zc, "distance": round(dist), "across": round(across), "along": round(along),
                     "mm_per_px": round(across / P.cam_px[0], 3), "overlap_across": round(across - P.cam_pitch),
                     "fps": round(fps, 1), "dof": round(dof)})
    out["at"] = rows
    out["hood_inside_y"] = round(P.hood_d - 2 * (P.sheet + P.curtain_t))
    out["blur_mm"] = round(P.speed * P.flash_us / 1000.0, 3)
    out["fps_max"] = max(r["fps"] for r in rows)
    return out


def light():
    """Flash needed for the exposure (EV relation, incident-light constant C = 250) and its average power."""
    t = P.flash_us * 1e-6
    lux = P.cam_n ** 2 * 250.0 / (t * P.iso_gain)
    area = (2 * P.half_width / 1000.0) * (P.hood_d / 1000.0)
    lumen = lux * area / P.utilisation
    bars = 2 * P.n_cam
    pulse_w = lumen / P.led_lm_w
    duty = t * camera()["fps_max"]
    return {"lux_needed": round(lux), "lumen_flash": round(lumen), "bars": bars,
            "lumen_per_bar": round(lumen / bars), "pulse_w_needed": round(pulse_w), "pulse_w_installed": bars * P.led_pulse_w,
            "duty_pct": round(100 * duty, 3), "avg_w": round(bars * P.led_pulse_w * duty, 1),
            "ambient_inside_lux": round(P.ambient_lux * P.leak), "ambient_share_pct": round(100 * P.ambient_lux * P.leak / lux, 1)}


# ---------------------------------------------------------------------
# Field work
# ---------------------------------------------------------------------
def capacity():
    width = 2 * P.half_width / 1000.0
    gross = width * P.speed * 3.6 / 10.0                   # ha/h
    net = gross * P.field_eff
    plants_ha = 1e4 / ((P.row_pitch / 1000.0) * (P.plant_pitch / 1000.0))
    plants_s = P.rows_per_pass * P.speed * 1000.0 / P.plant_pitch
    return {"width_m": width, "ha_h_gross": round(gross, 2), "ha_h_net": round(net, 2),
            "plants_per_ha": round(plants_ha), "plants_per_s": round(plants_s, 1)}


def power():
    lt = light()
    w = P.drive_w + P.computer_w + P.n_cam * P.cam_w + P.switch_w + lt["avg_w"]
    hours = P.battery_kwh * 1000.0 / w
    cap = capacity()
    return {"w_total": round(w), "w_scout": round(w - P.drive_w), "hours": round(hours, 1),
            "ha_per_charge": round(hours * cap["ha_h_net"], 1), "ha_per_week_20h_day": round(7 * 20 * cap["ha_h_net"])}


def data():
    fps = camera()["fps_max"]
    img_s = P.n_cam * fps
    raw = img_s * P.cam_px[0] * P.cam_px[1] / 1e6           # MB/s (8 bit Bayer)
    stored = img_s * P.jpeg_mb * P.store_share * 3600 / 1000.0
    cap = capacity()
    return {"images_s": round(img_s, 1), "raw_mb_s": round(raw), "ms_per_image": round(1000.0 / img_s, 1),
            "stored_gb_h": round(stored, 1), "stored_gb_ha": round(stored / cap["ha_h_net"], 1)}


# ---------------------------------------------------------------------
# Loads
# ---------------------------------------------------------------------
def castor_axle_y():
    return P.castor_stem_y - P.castor_trail


def wing_castor_rel():
    """Wing castor axle in local wing coordinates (s, t) relative to the kingpin."""
    return (P.castor_wing_x - P.pivot_x, castor_axle_y() - P.pivot[1])


def castors(folded=False):
    """The hood rests on 4 castors. Working: all 4 axles on one line (y 1045); the wing castor carries its wing
    (supports: kingpin and castor), the parallelogram only a small pitch couple (links horizontal). Folded: the wing
    castors are in front (y 2385), the hood stands on two rows and there is no couple for the robot."""
    m = MODEL
    kg = m["hood_kg"]
    s_c = wing_castor_rel()[0]
    if folded:
        y_w = P.pivot[1] + s_c
        wing_total = kg * (m["cg_folded"][1] - castor_axle_y()) / (y_w - castor_axle_y())
        wing = wing_total / 2.0
        couple = 0.0
    else:
        wing = m["wing_kg"] * m["wing_cg_rel"][0] / s_c
        couple = kg * G_ACC * (m["hood_cg"][1] - castor_axle_y()) / 1000.0     # N m, + = nose down
    centre = (kg - 2 * wing) / 2.0
    per = max(centre, wing)
    link_f = couple / ((P.link_z[1] - P.link_z[0]) / 1000.0)
    push = P.c_rr_castor * kg * G_ACC + P.curtain_drag * 2 * P.half_width / 1000.0 * (0 if folded else 1)
    return {"kg_centre_castor": round(centre, 1), "kg_wing_castor": round(wing, 1),
            "castor_use_pct": round(100 * per / P.castor_load),
            "pitch_couple_nm": round(couple), "link_axial_n": round(abs(link_f)), "push_n": round(push),
            "contact_kpa": round(per * G_ACC / (P.castor_wheel[1] * 0.4 * P.castor_wheel[0] * 0.25) * 1000)}


def axle_loads(folded=False):
    """Robot axle loads: the robot plus the mount (posts, links) plus the pitch couple of the hood."""
    rk, rcg = P.robot_kg, P.robot_cg
    mk, mcg = MODEL["mount_kg"], MODEL["mount_cg"]
    couple = castors(folded)["pitch_couple_nm"]
    wb = 2 * P.robot_axle_y / 1000.0
    # moments about the rear axle (y -500)
    front = (rk * (rcg[1] + P.robot_axle_y) + mk * (mcg[1] + P.robot_axle_y)) / 1000.0 / wb + couple / G_ACC / wb
    total = rk + mk
    rear = total - front
    return {"front_kg": round(front, 1), "rear_kg": round(rear, 1), "front_pct": round(100 * front / total)}


def stability():
    """Sideways tipping of robot + hood, coupled in roll by the parallelogram; track 750 (robot and castors)."""
    m = MODEL
    items = [(P.robot_kg, P.robot_cg[2]), (m["kg"], m["cg"][2])]
    kg = sum(k for k, _ in items)
    zc = sum(k * z for k, z in items) / kg
    tip = math.degrees(math.atan(P.robot_wheel_x / zc))
    return {"kg": round(kg, 1), "cg_z": round(zc), "tip_deg": round(tip, 1)}


def strength():
    """Kingpin, swing arm and posts (x dyn). Kingpin and arm: worst case, the wing castor off the ground (wing hangs
    on the kingpin only, e.g. over a ditch on the headland)."""
    m = MODEL
    w = m["wing_kg"] * G_ACC
    s_cg = m["wing_cg_rel"][0] + 0.0
    mom = w * s_cg / 1000.0 * P.dyn                                  # N m at the kingpin
    w_pin = math.pi * P.pin_d ** 3 / 32.0
    sigma_pin = mom * 1000.0 / w_pin
    b, h, t = P.arm_sec[0], P.arm_sec[1], P.arm_wall
    i_arm = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12.0
    sigma_arm = mom * 1000.0 * (h / 2) / i_arm                      # without the tie rod (conservative)
    torsion = w * abs(m["wing_cg_rel"][1] - 0.5 * (P.arm_t[0] + P.arm_t[1])) / 1000.0 * P.dyn
    tau_arm = torsion * 1000.0 / (2 * (b - t) * (h - t) * t)
    # posts: push force (curtains through the haulm, castors rolling) at the upper link, x dyn, on 2 posts
    couple = castors(False)["push_n"] * P.dyn * (P.link_z[1] - P.robot_lower_beam_z[1]) / 1000.0 / 2.0
    a, tt = P.post
    i_post = (a ** 4 - (a - 2 * tt) ** 4) / 12.0
    sigma_post = couple * 1000.0 * (a / 2) / i_post
    bolt = couple / ((P.robot_lower_beam_y[3] - P.robot_lower_beam_y[2]) / 1000.0) / 2.0
    return {"kingpin_mpa": round(sigma_pin, 1), "arm_bending_mpa": round(sigma_arm, 1), "arm_torsion_mpa": round(tau_arm, 1),
            "post_mpa": round(sigma_post, 1), "post_bolt_n": round(bolt)}


def report():
    out = {"swing": swing(), "folded": folded_extent(), "camera": camera(), "light": light(), "capacity": capacity(),
           "power": power(), "data": data(), "castors_work": castors(False), "castors_folded": castors(True),
           "axle_work": axle_loads(False), "axle_folded": axle_loads(True), "stability": stability(),
           "strength": strength()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
