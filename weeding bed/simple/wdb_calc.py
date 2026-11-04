"""Calculations for the weeding bed, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B wdb_calc.py      (or in FreeCAD: import wdb_calc; wdb_calc.report())

Axle and wheel loads with 0, 1 and 2 workers, sideways tip margin with one worker on board (driving) and when a
worker steps on the outer edge (why the parking stands go down), cantilever bending of the cross tubes and the bolt
tension at the outer upper beam, worked area per hour and battery time at creep speed.
"""
import math

import wdb_params as P


def masses(workers=2):
    """workers: 0, 1 (right side) or 2."""
    m = P.MODEL_MASS
    out = [(P.robot_kg, P.robot_cg), (m["total_kg"], m["cg"])]
    sides = {0: (), 1: (1,), 2: (-1, 1)}[workers]
    for s in sides:
        out.append((P.worker_kg, (s * P.worker_cg[0], P.worker_cg[1], P.worker_cg[2])))
    return out


def combined(ms):
    tot = sum(k for k, _ in ms)
    cg = tuple(sum(k * c[i] for k, c in ms) / tot for i in range(3))
    return tot, cg


def wheel_loads(workers=2):
    """Static load per wheel (kg): split fore-aft by the axles, sideways by the track."""
    tot, cg = combined(masses(workers))
    front = tot * (cg[1] + P.robot_axle_y) / (2.0 * P.robot_axle_y)
    rear = tot - front
    right = (cg[0] + P.robot_wheel_x) / (2.0 * P.robot_wheel_x)
    w = {"FL": front * (1 - right), "FR": front * right, "RL": rear * (1 - right), "RR": rear * right}
    return {"total_kg": round(tot, 1), "cg": tuple(round(c) for c in cg), "front_share": round(front / tot, 3),
            "wheels_kg": {k: round(v, 1) for k, v in w.items()}, "lightest_kg": round(min(w.values()), 1)}


def tip_side(workers=1):
    """Sideways tip about the right wheel line (x 375) with workers on the right: restoring / tipping moment and the
    static side slope at which the load leaves the inner wheels."""
    tot, cg = combined(masses(workers))
    arm = P.robot_wheel_x - cg[0]                   # cg inside the wheel line: > 0
    slope = math.degrees(math.atan(arm / cg[2]))
    return {"cg_x": round(cg[0]), "cg_z": round(cg[2]), "margin_mm": round(arm), "tip_slope_deg": round(slope, 1)}


def boarding():
    """Bed without workers, one worker steps on the outer edge of the board (dynamic, boarding_kg): factor against
    tipping about the wheel line, stands up. With the stands down the load goes into the stand pad."""
    tot, cg = combined(masses(0))
    restore = tot * (P.robot_wheel_x - cg[0])
    tip = P.boarding_kg * (P.boarding_x - P.robot_wheel_x)
    # also the other worker already lying on the far side helps; worst case is the empty bed
    return {"restore_kgm": round(restore / 1000.0, 1), "tip_kgm": round(tip / 1000.0, 1),
            "factor": round(restore / tip, 2), "stands_needed": restore / tip < 1.5}


def cross_tube():
    """One side: worker + half the bed mass hang on 4 cross tubes at x ~880; bending at the outer upper beam (x 445)
    and bolt tension of the pair of M10 per tube end (beam bolts 100 mm apart), dynamic factor 2."""
    m_side = P.worker_kg + 0.5 * P.MODEL_MASS["total_kg"] * 0.8      # the canopy and stands part of the frame
    f_tube = m_side * P.g * 2.0 / 4.0
    arm = P.worker_x - 445.0
    mom = f_tube * arm
    a, w = P.tube, P.tube_wall
    wz = (a ** 4 - (a - 2 * w) ** 4) / (6.0 * a)
    # stub at y 625: only the two beams of its side, bolts 100 mm apart -> lever couple
    bolt_t = mom / 100.0
    return {"load_per_tube_N": round(f_tube), "moment_Nm": round(mom / 1000.0, 1), "stress_MPa": round(mom / wz),
            "ok": mom / wz < 235.0 / 1.5, "stub_bolt_tension_N": round(bolt_t),
            "m10_8_8_proof_N": 33700, "bolt_ok": bolt_t < 33700 / 3.0}


def work_rate():
    """Worked area per hour and battery time at creep speed."""
    out = {}
    for v in P.speed_m_h:
        out["%d_m_h" % v] = {"m2_h_2_workers": round(2 * P.strip_w * v), "ha_per_8h": round(2 * P.strip_w * v * 8 / 1e4, 2)}
    p = P.drive_power_w + P.electronics_w
    out["power_W"] = p
    out["battery_h"] = round(P.robot_battery_kwh * 1000.0 * 0.85 / p, 1)
    return out


def report():
    out = {"wheels_2_workers": wheel_loads(2), "wheels_1_worker": wheel_loads(1), "wheels_empty": wheel_loads(0),
           "tip_1_worker": tip_side(1), "tip_2_workers": tip_side(2), "boarding": boarding(),
           "cross_tube": cross_tube(), "work_rate": work_rate(),
           "crop_clearance_mm": P.crop_clear}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
