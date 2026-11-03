"""Calculations for the fence inspector, in pure Python (same parameters as the model).

    import fin_calc
    fin_calc.report()          # prints and returns all key figures

Voltage: a wire of radius r at height h over the ground carries lambda = 2 pi eps0 V / ln(2h / r); at the probe
distance d (d << h) the field is E = V / (d ln(2h / r)). The plate (area A) collects Q = eps0 E A on an integrating
capacitor C: U = Q / C. The voltage reading scales with 1 / d, so the ToF distance error sets the accuracy.
Current: the pulse current I gives B = mu0 I / (2 pi d) at the coil; a coil of N turns and area a gives N a B / t_rise.
"""
import math

import fin_params as P


def e_field(kv=None, h=None):
    kv = P.fence_kV if kv is None else kv
    h = P.wire_z if h is None else h
    return kv * 1000.0 / (P.probe_d / 1000.0 * math.log(2.0 * h / P.wire_r))


def voltage_reading():
    out = {}
    for h in (P.Z_RANGE[0], P.wire_z):
        e = e_field(h=h)
        q = P.eps0 * e * P.plate_area / 1e6
        u = q / P.c_integr
        err = math.hypot(P.probe_d_err / P.probe_d, P.neighbour_share)
        out["wire_%d" % h] = {"E_kV_m": round(e / 1000.0, 1), "plate_V": round(u, 3), "error_pct": round(err * 100, 1)}
    ln_ratio = math.log(2.0 * P.Z_RANGE[1] / P.wire_r) / math.log(2.0 * P.Z_RANGE[0] / P.wire_r)
    out["height_factor"] = round(ln_ratio, 2)          # ln(2h/r) changes with the wire height: corrected per height
    err = math.hypot(P.probe_d_err / P.probe_d, P.neighbour_share)
    out["fault_found"] = P.fence_kV * (1.0 - 2.0 * err) > P.fault_kV
    return out


def current_reading():
    out = {}
    for i in P.pulse_current:
        b = P.mu0 * i / (2.0 * math.pi * P.probe_d / 1000.0)
        emf = P.coil_turns * P.coil_area / 1e6 * b / P.pulse_s
        out["I_%g_A" % i] = {"B_uT": round(b * 1e6, 1), "emf_mV": round(emf * 1000.0, 2)}
    return out


def resolution():
    step = P.speed / P.pulse_hz
    return {"m_per_reading": step, "post_step_m": P.post_step / 1000.0,
            "readings_per_post_span": round(P.post_step / 1000.0 / step)}


def carriage():
    """Time to move the head over the full height and the stepper speed."""
    v = P.stepper_rpm / 60.0 * P.screw_lead
    return {"mm_s": round(v), "full_range_s": round((P.Z_RANGE[1] - P.Z_RANGE[0]) / v, 1)}


def capacity():
    m = P.MODEL_MASS
    drag = P.crr * (P.robot_mass + m["kg"]) * P.g
    drive_w = drag * P.speed / P.eta_drive
    w = drive_w + P.p_sensors
    hours = P.battery_wh / w
    km_h = P.speed * 3.6
    return {"km_h": round(km_h, 1), "power_W": round(w), "hours": round(hours, 1),
            "km_per_charge": round(km_h * hours, 1)}


def side_load():
    """Lateral centre of gravity of robot + inspector and the share on the right wheels."""
    m = P.MODEL_MASS
    x = m["kg"] * m["cg_x"] / (P.robot_mass + m["kg"])
    right = 0.5 + x / (2.0 * P.robot_wheel_x)
    return {"cg_x_mm": round(x), "right_share": round(right, 3)}


def report():
    out = {"voltage": voltage_reading(), "current": current_reading(), "resolution": resolution(),
           "carriage": carriage(), "capacity": capacity(), "side_load": side_load()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
