"""Linkage and actuator of the weed picker (pure Python, no FreeCAD needed).

Parallelogram: robot pivots (pivot_y, pivot_z), links link_L, deck pivots on the deck lugs. The actuator runs from
the robot pin A to the bottom deck pin B; its rear eye hangs on A with a slotted float link, so the deck can lift by
itself (A slides in the slot) but not drop below the set height.
Use:  import wpk_kin; wpk_kin.table(); wpk_kin.forces(200)
"""
import math

import wpk_params as P

G_ACC = 9.81

# last measurement from the model (build_wpk.mass_properties, default cut height 200)
MODEL = {"kg": 82.2, "cg": (-6.0, 840.0, 398.0), "deck_kg": 57.0, "deck_cg": (-9.0, 1045.0, 338.0),
         "links_kg": 6.94, "actuator_kg": 3.29, "mount_kg": 10.47, "controller_kg": 4.55, "rotor_kg": 3.89,
         "rotor_I": 0.0449, "blade_kg": 0.319}


def act_setting(cut):
    """Actuator pin to pin (mm) for a cut height."""
    return P.act_length(cut) - P.float_len


def theta_limit():
    """Link angle (deg) at which the top link touches the front edge of the mount plate."""
    z_plate = P.robot_lower_beam_z[0] - P.mount_t
    for k in range(0, 600):
        t = math.radians(k * 0.1)
        z = P.pivot_z[1] + (P.mount_y[1] - P.pivot_y) * math.tan(t) + P.link_w / 2.0 / math.cos(t)
        if z >= z_plate:
            return k * 0.1
    return 60.0


def cut_for_theta(deg):
    return P.pivot_z[0] + P.link_L * math.sin(math.radians(deg)) - P.deck_pivot_dz - P.DECK_H


def max_lift(cut):
    """How far the deck can float up from cut (mm): until pin A is at the end of the slot or the top link touches
    the mount plate."""
    top = cut_for_theta(theta_limit())
    ab0 = P.act_length(cut)
    lift = 0.0
    while cut + lift + 1.0 <= top and ab0 - P.act_length(cut + lift + 1.0) <= P.float_slot:
        lift += 1.0
    return lift


def forces(cut=P.cut_h, drag=0.0, dyn=1.0):
    """Static forces on the deck (N): weight (x dyn) at the deck CG, drag (backwards, at the blade height). Returns the
    axial force in the top and bottom link pairs (+ = tension) and in the actuator (+ = tension)."""
    w = dyn * MODEL["deck_kg"] * G_ACC
    th = math.radians(P.theta(cut))
    dy, dz = P.deck_shift(cut)
    yb, zb = P.deck_pivot(cut)
    y_cg, z_cg = MODEL["deck_cg"][1] + dy, MODEL["deck_cg"][2] + dz
    h = P.pivot_z[1] - P.pivot_z[0]
    r_wy = y_cg - yb
    r_dz = cut - zb
    t_top = (r_wy * w - r_dz * drag) / (h * math.cos(th))
    el = (-math.cos(th), -math.sin(th))
    ab = math.hypot(P.act_A[0] - yb, P.act_A[1] - zb)
    ea = ((P.act_A[0] - yb) / ab, (P.act_A[1] - zb) / ab)
    # (T_top + T_bot) el + F_a ea = (drag, w)
    ry, rz = drag - t_top * el[0], w - t_top * el[1]
    det = el[0] * ea[1] - el[1] * ea[0]
    t_bot = (ry * ea[1] - rz * ea[0]) / det
    f_a = (el[0] * rz - el[1] * ry) / det
    return {"top_N": t_top, "bottom_N": t_bot, "actuator_N": f_a, "theta": P.theta(cut)}


def actuator_force(cut):
    """Actuator tension (N) to hold the deck, links and actuator: virtual work, dz/dAB numerically."""
    d = 1.0
    dab = (P.act_length(cut - d) - P.act_length(cut + d)) / (2 * d)
    m = MODEL["deck_kg"] + 0.5 * MODEL["links_kg"] + 0.5 * MODEL["actuator_kg"]
    return m * G_ACC / dab


def table(cuts=(100, 150, 200, 250, 300, 350, 400)):
    rows = []
    for c in cuts:
        y, z = P.deck_pivot(c)
        s = act_setting(c)
        rows.append({"cut": c, "theta": P.theta(c), "deck_y": P.rotor_y(c), "deck_dy": P.deck_shift(c)[0],
                     "deck_top": P.deck_top(c), "AB": P.act_length(c), "act": s, "act_ext": s - P.act_closed,
                     "F_act": actuator_force(c), "lift_max": max_lift(c)})
    return rows


def lift_time(c0=P.cut_range[0], c1=P.cut_range[1]):
    return abs(act_setting(c0) - act_setting(c1)) / P.act_speed
