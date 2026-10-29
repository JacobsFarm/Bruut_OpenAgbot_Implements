"""Calculations for the irrigation pump, in pure Python (same parameters as the model).

    import idp_calc
    idp_calc.report()          # prints and returns all key figures

Pump curve H = h_shutoff * (1 - (Q / q_max)^2); system curve = suction lift + end head + friction of the suction and
discharge hose; the operating point is where they meet.
"""
import math

import idp_params as P


def pump_head(q):
    return P.h_shutoff * (1.0 - (q / P.q_max) ** 2)


def friction(q, length, d, k=0.0):
    """Head loss (m) at q (m3/h) in a hose of 'length' (m) and inner diameter d (m), plus local losses k."""
    v = q / 3600.0 / (math.pi / 4.0 * d * d)
    return (P.lambda_f * length / d + k) * v * v / (2.0 * P.g)


def system_head(q, lift, end):
    return lift + end + friction(q, P.hose_len, P.pipe_id, P.k_local) + friction(q, P.discharge_len, P.discharge_id)


def operating_point(lift, end):
    lo, hi = 0.0, P.q_max
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if pump_head(mid) > system_head(mid, lift, end):
            lo = mid
        else:
            hi = mid
    q = lo
    h = pump_head(q)
    hyd_W = P.rho * P.g * q / 3600.0 * h
    elec_W = hyd_W / P.eta_pump / P.eta_motor + P.idle_W
    hours = P.robot_battery_wh / elec_W
    m3 = q * hours
    return {"q_m3_h": round(q, 1), "head_m": round(h, 1), "elec_W": round(elec_W), "hours": round(hours, 1),
            "m3_per_charge": round(m3, 1), "m2_at_dose": round(m3 / (P.dose_mm / 1000.0)),
            "ok_motor": elec_W - P.idle_W <= P.motor_kw * 1000.0}


def suction_check(lift, q=10.0):
    """NPSH available (m) at a suction lift: 10.1 m atmosphere - lift - suction friction - vapour (0.3 m)."""
    return round(10.1 - lift - friction(q, P.hose_len, P.pipe_id, P.k_local) - 0.3, 1)


def report():
    out = {"points": {"lift_%g_end_%g" % (lf, e): operating_point(lf, e) for lf in P.suction_lift for e in P.end_head},
           "npsh_available_m": {lf: suction_check(lf) for lf in P.suction_lift}}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
