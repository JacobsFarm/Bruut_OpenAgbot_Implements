"""Calculations for the metal detector, in pure Python (same parameters as the model).

    import mdt_calc
    mdt_calc.report()          # prints and returns all key figures

Detection model: a loop of (area-equivalent) radius a sends a field a^2 / (a^2 + z^2)^1.5 to a small target at depth
z; the target (equivalent sphere r_e, eddy currents) gives a dipole ~ r_e^3 x that field and the same loop picks it up
with the same factor (reciprocity):  S ~ r_e^3 a^4 / (a^2 + z^2)^3.
The noise level is set by a reference (an 8 mm equivalent sphere found at 200 mm by a O250 coil) times the ground
noise after ground balancing. The robot's steel is a large target at distance d; only the part of its signal that
changes while driving (robot_var) disturbs the detector.
Masses come from build_mdt.mass_properties() (copied into mdt_params.MODEL_MASS after a rebuild).
"""
import math

import mdt_params as P

WIND_Z = sum(P.house_z) / 2.0          # coil plane above the ground (work)


def coil_a():
    """Area-equivalent radius (mm) of the rectangular coil."""
    return math.sqrt(P.coil_size[0] * P.coil_size[1] / math.pi)


def signal(re, z, a=None):
    a = coil_a() if a is None else a
    return re ** 3 * a ** 4 / (a * a + z * z) ** 3


def threshold():
    return signal(P.ref_target_re, P.ref_depth, P.ref_coil_a) * P.threshold_snr * P.ground_noise


def depth(re):
    """Largest depth (mm below the ground) at which a target of equivalent radius re is detected."""
    t = threshold()
    z = 0.0
    while z < 3000.0 and signal(re, z + 1.0) >= t:
        z += 1.0
    return round(z - WIND_Z)


def targets():
    return {k: {"re_mm": re, "depth_mm": depth(re), "depth_O250_coil_mm": _depth_ref(re)} for k, re in P.TARGETS.items()}


def _depth_ref(re):
    t = threshold()
    z = 0.0
    while z < 3000.0 and signal(re, z + 1.0, P.ref_coil_a) >= t:
        z += 1.0
    return round(z - WIND_Z)


def robot_distance():
    """Distance (mm) from the coil centre to the nearest large steel of the robot (front lower beam, hub motor)."""
    cy = P.coil_c[1]
    beam = math.hypot(cy - P.robot_front_beam_y[1], sum(P.robot_lower_beam_z) / 2.0 - WIND_Z)
    hub = math.hypot(cy - P.robot_axle_y, P.robot_axle_z - WIND_Z)
    return min(beam, hub)


def robot_interference(d=None):
    """Changing part of the robot signal relative to the threshold (must be well below 1), and the least distance at
    which it is 0.3."""
    d = robot_distance() if d is None else d
    ratio = signal(P.robot_re, d) * P.robot_var / threshold()
    dmin = 300.0
    while signal(P.robot_re, dmin) * P.robot_var / threshold() > 0.3:
        dmin += 10.0
    return {"distance_mm": round(d), "ratio_to_threshold": round(ratio, 3), "least_distance_mm": round(dmin),
            "ok": ratio < 0.3}


def sampling():
    rate = P.pulse_hz / P.avg_pulses
    step = P.speed * 1000.0 / rate
    return {"samples_per_s": rate, "mm_per_sample": round(step), "samples_over_coil": round(P.coil_size[1] / step)}


def position_error():
    """Error (mm) of the logged hit position: RTK, heading over the lever arm from the antenna, and the peak of the
    signal along the coil (~1/4 of the coil length, estimated)."""
    arm = math.hypot(P.coil_c[0] - P.robot_gnss[0], P.coil_c[1] - P.robot_gnss[1])
    head = arm * math.radians(P.heading_err_deg)
    peak = P.coil_size[1] / 4.0
    total = math.sqrt(P.gnss_err ** 2 + head ** 2 + peak ** 2)
    return {"lever_arm_mm": round(arm), "heading_mm": round(head), "peak_mm": round(peak), "total_mm": round(total)}


def skid_load():
    """Mass (kg) of the boom on the skids in work (moment about the pivot, the actuator floats)."""
    m = P.MODEL_MASS
    skid_y = P.coil_c[1]
    return m["boom_kg"] * (m["boom_cg_y"] - P.pivot[0]) / (skid_y - P.pivot[0])


def axle_loads(lifted=False):
    m = P.MODEL_MASS
    ground = 0.0 if lifted else skid_load()
    items = [(P.robot_mass, P.robot_cg_y), (m["fixed_kg"], m["fixed_cg_y"]), (m["boom_kg"], m["boom_cg_y"])]
    total = sum(k for k, _ in items) - ground
    moment = sum(k * (y + P.robot_axle_y) for k, y in items) - ground * (P.coil_c[1] + P.robot_axle_y)
    front = moment / (2.0 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "on_skids_kg": round(ground, 1),
            "rear_share": round((total - front) / total, 3)}


def actuator():
    """Force (N) to lift the boom (moment about the pivot / lever of the actuator) and lift time."""
    m = P.MODEL_MASS
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        a = math.radians(lift)
        dy, dz = P.act_pin[0] - P.pivot[0], P.act_pin[1] - P.pivot[1]
        ry = P.pivot[0] + dy * math.cos(a) - dz * math.sin(a)
        rz = P.pivot[1] + dy * math.sin(a) + dz * math.cos(a)
        uy, uz = ry - P.act_base[0], rz - P.act_base[1]
        L = math.hypot(uy, uz)
        lever = abs((ry - P.pivot[0]) * uz / L - (rz - P.pivot[1]) * uy / L)
        cy = P.pivot[0] + (m["boom_cg_y"] - P.pivot[0]) * math.cos(a) - (m["boom_cg_z"] - P.pivot[1]) * math.sin(a)
        moment = m["boom_kg"] * P.g * (cy - P.pivot[0]) / 1000.0
        out["lift_%g" % lift] = {"length_mm": round(L), "lever_mm": round(lever, 1), "force_N": round(moment / lever * 1000.0)}
    lens = [v["length_mm"] for v in out.values()]
    out["stroke_used_mm"] = max(lens) - min(lens)
    out["in_range"] = P.act_retracted <= min(lens) and max(lens) <= P.act_retracted + P.act_stroke
    out["ok"] = max(v["force_N"] for k, v in out.items() if k.startswith("lift")) <= P.act_force
    out["lift_time_s"] = round(out["stroke_used_mm"] / P.act_speed, 1)
    return out


def drive():
    a = axle_loads()
    roll = P.crr * (a["front_kg"] + a["rear_kg"]) * P.g
    skid = P.mu_skid * a["on_skids_kg"] * P.g
    return {"rolling_N": round(roll), "skid_N": round(skid), "drive_W": round((roll + skid) * P.speed / P.eta_drive)}


def capacity():
    swath = (P.coil_size[0] - P.overlap) / 1000.0
    m2_h = swath * P.speed * 3600.0
    w = drive()["drive_W"] + P.p_detector + P.p_logger
    hours = P.battery_wh / w
    return {"swath_m": swath, "m2_h": round(m2_h), "ha_h": round(m2_h / 1e4, 2), "power_W": round(w),
            "hours": round(hours, 1), "ha_per_charge": round(m2_h * hours / 1e4, 1)}


def report():
    out = {"coil_a_mm": round(coil_a()), "targets": targets(), "robot": robot_interference(), "sampling": sampling(),
           "position": position_error(), "axle_work": axle_loads(False), "axle_lifted": axle_loads(True),
           "actuator": actuator(), "drive": drive(), "capacity": capacity()}
    for k, v in out.items():
        if isinstance(v, dict) and all(isinstance(x, dict) for x in v.values()):
            print(k)
            for kk, vv in v.items():
                print("   ", kk, vv)
        else:
            print(k, v)
    return out


if __name__ == "__main__":
    report()
