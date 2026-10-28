"""Calculations for the mulch layer, in pure Python (same parameters as the model). The linkage and the lift rods are
those of the three-point hitch (tph_calc is used for the lift force).

    import mly_calc
    mly_calc.report()          # prints and returns all key figures

Masses come from build_mly.mass_properties() (copied into mly_params.MODEL_MASS after a rebuild).
"""
import math

import mly_params as P
import tph_calc as TC
import tph_params as HP

FRONT_STACKS = 4                # counterweights/simple: 4 stacks on the front lower beams
PLATE_KG = 11.0
BASE_KG = 5.5
BALLAST_Y = 500.0


def roll():
    """Foil on a full roll: length, mass, area and beds of bed_len."""
    L = P.roll_length()
    return {"length_m": round(L), "mass_kg": round(P.roll_mass(), 1), "area_m2": round(L * P.foil_w / 1000.0),
            "beds": int(L // P.bed_len)}


def imp(full=True):
    """Implement mass and cg (y, z) in work with a full or an empty roll (core only)."""
    m, (x, y, z) = P.MODEL_MASS["imp_kg"], P.MODEL_MASS["imp_cg"]
    if full:
        return m, (y, z)
    r = P.roll_mass()
    return m - r, ((m * y - r * P.roll_y) / (m - r), (m * z - r * P.roll_z) / (m - r))


def lift(full=True):
    m, cg = imp(full)
    a = TC.actuator(m, cg)
    return {"max_N_per_rod": a["max_N"], "rods_ok": a["max_N"] <= HP.act_force, "lift_time_s": a["lift_time_s"]}


def ballast_kg(plates):
    return 0.0 if plates == 0 else FRONT_STACKS * (BASE_KG + plates * PLATE_KG)


def axle_loads(full=True, plates=0):
    """Front axle share with the implement lifted (transport), with counterweight plates per front stack."""
    m, cg = imp(full)
    y = TC._cg(HP.lift_transport, cg)[0]
    mm = HP.MODEL_MASS
    items = [(HP.robot_mass, HP.robot_cg_y), (mm["mount_kg"], mm["mount_cg_y"]),
             (mm["links_kg"], (HP.lower_a[0] + HP.lower_b[0]) / 2.0), (m, y), (ballast_kg(plates), BALLAST_Y)]
    total = sum(k for k, _ in items)
    front = sum(k * (yy + HP.robot_axle_y) for k, yy in items) / (2 * HP.robot_axle_y)
    return {"total_kg": round(total), "front_share": round(front / total, 3)}


def plates_needed(full=True):
    for n in range(5):
        if axle_loads(full, n)["front_share"] >= HP.front_share_min:
            return n
    return None


def draft(plates):
    """Pull (N) in work: two covering discs, press wheels, foil tension and rolling of the robot; grip and motors."""
    m, _ = imp(True)
    on_robot = HP.robot_mass + HP.MODEL_MASS["mount_kg"] + HP.MODEL_MASS["links_kg"] + ballast_kg(plates)
    discs = 2 * P.disc_draft
    press = 2 * P.press_load * P.press_crr
    tension = P.web_tension * P.foil_w / 1000.0
    robot = P.crr * on_robot * P.g
    imp_roll = P.crr * m * P.g * 0.5                     # half the implement rides on its press wheels (estimated)
    total = discs + press + tension + robot + imp_roll
    grip = P.mu_tyre * on_robot * P.g
    motors = P.n_driven * P.hub_torque_nom / P.r_load
    return {"discs_N": round(discs), "press_N": round(press), "tension_N": round(tension), "rolling_N": round(robot + imp_roll),
            "total_N": round(total), "grip_N": round(grip), "margin": round(min(grip, motors) / total, 2),
            "power_W": round(total * P.speed / P.eta_drive)}


def capacity(plates):
    """Beds per hour and per roll, time per roll, energy."""
    t_bed = P.bed_len / P.speed + P.turn_s
    r = roll()
    d = draft(plates)
    e_bed = d["total_N"] * P.bed_len / P.eta_drive / 3600.0
    return {"beds_per_hour": round(3600.0 / t_bed, 1), "m_per_hour": round(3600.0 / t_bed * P.bed_len),
            "m2_per_hour": round(3600.0 / t_bed * P.bed_len * P.foil_w / 1000.0), "roll_h": round(r["beds"] * t_bed / 3600.0, 1),
            "wh_per_bed": round(e_bed, 1), "beds_per_battery": int(P.battery_wh / e_bed),
            "foil_eur_per_100m": round(P.cost_foil * P.foil_w / 1000.0 * 100.0)}


def report():
    n_full, n_empty = plates_needed(True), plates_needed(False)
    out = {"roll": roll(), "lift_full": lift(True), "lift_empty": lift(False),
           "axles_lifted_full_no_ballast": axle_loads(True, 0), "plates_full": n_full,
           "axles_lifted_full_ballast": axle_loads(True, n_full or 4), "plates_empty": n_empty,
           "draft": draft(n_full or 4), "capacity": capacity(n_full or 4)}
    for k, v in out.items():
        print(k, v)
    return out
