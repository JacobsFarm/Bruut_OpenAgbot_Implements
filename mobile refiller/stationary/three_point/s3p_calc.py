"""Calculations for the three-point frame station: masses, what the tractor must lift, front ballast, top link and
lower pins, the mast as hitch tower, tipping on the legs, pump, the visit of the working robot, battery.

Pure Python (no FreeCAD): python s3p_calc.py prints the report. Masses of the frame, box, mast and hoses come from
the model (build_s3p.mass_properties()); update DRY when the model changes.
"""
import math
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.dirname(FOLDER), FOLDER):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import s3p_params as P      # noqa: E402
import stc_params as C      # noqa: E402
import stc_calc as K        # noqa: E402
from stc_calc import nl     # noqa: E402

G_ACC = 9.81

# From the model (build_s3p.mass_properties, arm out left). kg, (x, y, z) mm frame coordinates.
DRY = {"frame": (119.1, (0.0, 189.0, 384.0)), "box": (67.6, (15.0, 2.0, 374.0)),
       "mast": (43.3, (-226.0, 672.0, 1380.0)), "hoses": (2.1, (60.0, 407.0, 776.0))}
IBC_CG_Z = 450.0


def _area():
    w = C.S.bottle_wall
    a, b, rr = 2.0 * (C.S.bottle_x - w), (C.S.bottle_y[1] - C.S.bottle_y[0]) - 2.0 * w, C.S.bottle_r - w
    return a * b - (4.0 - math.pi) * rr * rr


def liquid_cg_z(litres):
    z0 = C.bottle_z0 + C.S.bottle_wall
    return z0 + 0.5 * litres * 1e6 / _area()


def items(fill=1.0, rho=None):
    rho = C.liquid_density if rho is None else rho
    out = list(DRY.values())
    out.append((C.ibc_kg, (0.0, 0.0, P.plat_z + IBC_CG_Z)))
    litres = fill * C.ibc_nominal_l
    if litres > 0:
        out.append((litres * rho, (0.0, 0.0, P.plat_z + liquid_cg_z(litres))))
    return out


def cg(fill=1.0, rho=None):
    it = items(fill, rho)
    m = sum(i[0] for i in it)
    return m, tuple(sum(i[0] * i[1][k] for i in it) / m for k in range(3))


def tractor(fill=1.0, rho=None):
    """Lifted on the tractor: distance lower pins -> cg, load equivalent at 610 mm, front axle share, ballast,
    top link force, lower pin shear."""
    m, (x, y, z) = cg(fill, rho)
    d = P.lower_pin_yz[0] - y                                  # cg behind the lower pins (mm)
    at610 = m * d / 610.0
    front = P.tractor_front_kg - m * (P.tractor_rear_to_pins + d) / P.tractor_wheelbase
    total = P.tractor_kg + m
    share = front / total
    # front ballast 1.0 m ahead of the front axle: (front + b (wb + 1000) / wb) / (total + b) >= share_min
    k = (P.tractor_wheelbase + 1000.0) / P.tractor_wheelbase
    need = (P.front_share_min * total - front) / (k - P.front_share_min)
    f_top = m * G_ACC * d / P.mast_height_iso                    # N, horizontal pair with the lower links
    per_pin = math.hypot(m * G_ACC / 2.0, f_top / 2.0)
    tau = per_pin / (math.pi * P.lower_pin[0] ** 2 / 4.0)
    w, _ = K.w_rect_tube(P.mast_tube[0], P.mast_tube[0], P.mast_tube[1])
    mast = 2.0 * f_top * (P.top_pin_z() - P.plat_z) / w          # x2 dynamic, cantilever above the platform
    return {"mass": m, "d": d, "at610": at610, "front_kg": front, "share": share, "ballast": max(0.0, need),
            "f_top_n": f_top, "pin_n": per_pin, "pin_mpa": tau, "mast_mpa": mast}


def tip_angle(fill=1.0):
    """Static tipping angle on the legs (deg): sideways (to the left, the arm side) and backwards."""
    m, (x, y, z) = cg(fill)
    edge_x = P.leg_xy[0] + P.foot[0] / 2.0
    edge_y = P.leg_xy[1] + P.foot[0] / 2.0
    return {"side": math.degrees(math.atan2(edge_x - abs(x), z)), "back": math.degrees(math.atan2(edge_y + y, z)),
            "cg_z": z}


def pump_geometry():
    low = P.plat_z + C.bottle_z0 + C.S.bottle_wall
    lift = (0.5 * (C.arm_z[0] + C.arm_z[1]) - low) / 1000.0
    suction = 1.3
    discharge = 0.4 + 0.7 + (C.arm_z[1] - P.in_z) / 1000.0 + P.reach() / 1000.0 + 0.7
    return lift, suction + discharge


def report():
    out = []
    add = out.append
    left, right = P.half_widths()
    add("######## Three-point frame, 1 IBC ########")
    add("== Layout ==")
    add("frame %s x %s mm on 4 legs, platform at %s mm, IBC top %s mm; lower pins cat. 2 at z %s, top link pin at "
        "z %s; arm reach %s mm" % (nl(2 * (P.leg_xy[0] + P.foot[0] / 2.0)), nl(2 * (P.leg_xy[1] + P.foot[0] / 2.0)),
                                   nl(P.plat_z), nl(P.ibc_top()), nl(P.lower_pin_yz[1]), nl(P.top_pin_z()),
                                   nl(P.reach())))
    add("== Masses (kg, %s kg/l) ==" % nl(C.liquid_density, 2))
    for fill in (0.0, 0.5, 1.0):
        m, (x, y, z) = cg(fill)
        add("IBC %4d l: total %s, cg (%s, %s, %s) mm" % (fill * C.ibc_nominal_l, nl(m), nl(x), nl(y), nl(z)))
    add("== On the tractor (example: %s kg, front axle %s kg, wheelbase %s mm, lift capacity %s kg at 610 mm) ==" % (
        nl(P.tractor_kg), nl(P.tractor_front_kg), nl(P.tractor_wheelbase), nl(P.lift_capacity_610)))
    for fill in (0.0, 1.0):
        t = tractor(fill)
        add("IBC %4d l: %s kg, cg %s mm behind the lower pins = %s kg at 610 mm; front axle %s kg = %s %% "
            "(min. %d %%): front ballast %s kg" % (fill * C.ibc_nominal_l, nl(t["mass"]), nl(t["d"]), nl(t["at610"]),
                                                   nl(t["front_kg"]), nl(100 * t["share"], 1),
                                                   100 * P.front_share_min, nl(t["ballast"])))
    t = tractor(1.0)
    add("full: top link %s kN; per lower pin %s kN (D28: %s MPa shear); mast above the platform %s MPa (x2, "
        "without the braces)" % (nl(t["f_top_n"] / 1000.0, 1), nl(t["pin_n"] / 1000.0, 1), nl(t["pin_mpa"]),
                                  nl(t["mast_mpa"])))
    add("== Standing on the legs ==")
    for fill in (0.0, 1.0):
        ta = tip_angle(fill)
        add("IBC %4d l: tipping sideways %s deg, backwards %s deg (cg %s mm high)" % (
            fill * C.ibc_nominal_l, nl(ta["side"], 1), nl(ta["back"], 1), nl(ta["cg_z"])))
    mc = K.arm_mast_check(P.reach(), C.arm_z[0] - P.plat_z, P.mast_tube)
    add("arm out: %s Nm at the mast, mast %s MPa, arm %s MPa (x2), tip deflection %s mm" % (
        nl(mc["moment_nm"]), nl(mc["mast_mpa"], 1), nl(mc["arm_mpa"], 1), nl(mc["tip_defl_mm"], 2)))
    lift, hose_m = pump_geometry()
    out += K.common_report(1, lift, hose_m, "1 IBC")
    add("pump axis %s mm, bottom of the bottle %s mm: the pump stays flooded" % (
        nl(P.box_xyz[2] + C.pump_axis[1]), nl(P.plat_z + C.bottle_z0)))
    return "\n".join(out)


if __name__ == "__main__":
    print(report())
