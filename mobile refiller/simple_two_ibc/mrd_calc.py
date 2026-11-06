"""Calculations for the mobile refiller with two IBCs (pure Python, no FreeCAD): masses, wheel loads, how full the two
IBCs may be, tipping angles, traction, fill times. Robot coordinates, mm and kg.

Run with FreeCAD's Python:  "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B mrd_calc.py
"""
import math
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mrd_params as P      # noqa: E402
import mrs_params as S      # noqa: E402

G_ACC = 9.81
BED_KG = 62.0               # 9 cross tubes 1100 + 2 side rails 2110 of 60 x 40 x 3 (4.5 kg/m), guides, eyes (estimated)
BOTTLE_H = S.bottle_h


def items(litres=(1000.0, 1000.0), rho=None):
    """(name, kg, x, y, z) of everything on the lengthened robot; litres = (A, B)."""
    rho = P.liquid_density if rho is None else rho
    z_ibc = P.IBC_Z0
    out = [("robot", P.robot_kg, 0.0, 0.0, 450.0),
           ("bed", BED_KG, -20.0, 0.5 * (P.bed_side_y[0] + P.bed_side_y[1]), 720.0),
           ("mast_arm", P.kit_extra_kg["mast_arm_2_drop_pipes"], P.mast_xy[0] - 250.0, P.mast_xy[1], 1700.0),
           ("hoses_electrics", P.kit_extra_kg["hoses_2x"] + P.kit_extra_kg["electrics"], -500.0, -70.0, 1000.0)]
    for liq, l in zip(P.LIQUIDS, litres):
        cy = P.ibc_cy(liq)
        out.append(("ibc_" + liq, P.ibc_kg, 0.0, cy, z_ibc + 500.0))
        out.append(("pump_" + liq, P.pump_kg, -150.0, cy, 540.0))
        h = l / (1.15 * 0.95) * 1e-3 * 1e3      # mm of liquid (bottle 1150 x 950 inside, roughly)
        out.append(("liquid_" + liq, l * rho, 0.0, cy, z_ibc + S.pallet_h + h / 2.0))
    return out


def cg(litres=(1000.0, 1000.0), rho=None):
    it = items(litres, rho)
    m = sum(i[1] for i in it)
    return (m, sum(i[1] * i[2] for i in it) / m, sum(i[1] * i[3] for i in it) / m, sum(i[1] * i[4] for i in it) / m)


def wheel_loads(litres=(1000.0, 1000.0), rho=None):
    """Static load per wheel (kg): rigid frame on 4 wheels, split by lever arms in x and y."""
    m, x, y, _ = cg(litres, rho)
    front = m * (P.axle_y + y) / P.wheelbase
    rear = m - front
    left = (P.wheel_x - x) / (2.0 * P.wheel_x)
    return {"FL": front * left, "FR": front * (1 - left), "RL": rear * left, "RR": rear * (1 - left), "total": m}


def max_wheel(litres=(1000.0, 1000.0), rho=None):
    w = wheel_loads(litres, rho)
    return max(w[k] for k in ("FL", "FR", "RL", "RR"))


def max_fill_equal(rho=None, limit=None):
    """Largest equal fill of both IBCs (litres each) that keeps every wheel at or under the datasheet load."""
    limit = P.wheel_load_max if limit is None else limit
    lo, hi = 0.0, P.ibc_nominal_l
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if max_wheel((mid, mid), rho) <= limit:
            lo = mid
        else:
            hi = mid
    return lo


def tip_angles(litres=(1000.0, 1000.0), rho=None):
    """Static tipping angles (deg) sideways (to the mast side, the worst) and backwards."""
    m, x, y, z = cg(litres, rho)
    side = math.degrees(math.atan((P.wheel_x + x) / z))
    back = math.degrees(math.atan((P.axle_y + y) / z))
    return {"side_deg": round(side, 1), "back_deg": round(back, 1), "cg_z": round(z)}


def traction(litres=(1000.0, 1000.0), surface="grass"):
    """Rolling resistance against the hub motors (kgf)."""
    m = cg(litres)[0]
    need = m * S.c_rr[surface]
    return {"mass_kg": round(m), "rolling_kgf": round(need, 1), "continuous_kgf": 4 * P.motor_cont_kgf,
            "peak_kgf": 4 * P.motor_peak_kgf}


def max_fill_continuous(surface="grass"):
    """Equal fill (litres each) at which rolling resistance equals the continuous force of the 4 hub motors."""
    lo, hi = 0.0, P.ibc_nominal_l
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if traction((mid, mid), surface)["rolling_kgf"] <= 4 * P.motor_cont_kgf:
            lo = mid
        else:
            hi = mid
    return lo


def fill_time_s(litres):
    """Pumping time for one liquid (both pumps run at the same time, one per IBC)."""
    return litres / P.pump_q_fill * 60.0


def report():
    lines = []
    fill = max_fill_equal()
    lines.append("Max equal fill for 500 kg/wheel: %.0f l per IBC (liquid %.2f kg/l)" % (fill, P.liquid_density))
    lines.append("UAN 1.32 kg/l: %.0f l per IBC" % max_fill_equal(rho=1.32))
    for l in (0.0, 400.0, round(fill / 10.0) * 10.0, 1000.0):
        w = wheel_loads((l, l))
        t = tip_angles((l, l))
        lines.append("%4.0f l each: total %5.0f kg, wheels FL %3.0f FR %3.0f RL %3.0f RR %3.0f, tip side %.1f back %.1f, "
                     "cg z %d" % (l, w["total"], w["FL"], w["FR"], w["RL"], w["RR"], t["side_deg"], t["back_deg"],
                                  t["cg_z"]))
    lines.append("Continuous traction on grass up to %.0f l each, on a track up to %.0f l each"
                  % (max_fill_continuous("grass"), max_fill_continuous("track")))
    tr = traction((fill, fill))
    lines.append("At the max fill on grass: rolling %.0f kgf, motors %d continuous / %d peak"
                 % (tr["rolling_kgf"], tr["continuous_kgf"], tr["peak_kgf"]))
    lines.append("Fill time per refill of 2 x 20 l: %.0f s (both pumps at once)" % fill_time_s(20.0))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
