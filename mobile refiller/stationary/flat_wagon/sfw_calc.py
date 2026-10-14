"""Calculations for the flat-wagon station: masses, axle and tyre loads for 1 to 4 rows of IBCs, tipping, pump and
header, the visit of the working robot, battery, mast.

Pure Python (no FreeCAD): python sfw_calc.py prints the report. Masses of the wagon and the kit come from the model
(build_sfw.mass_properties()); update DRY when the model changes.
"""
import math
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.dirname(FOLDER), FOLDER):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sfw_params as P      # noqa: E402
import stc_params as C      # noqa: E402
import stc_calc as K        # noqa: E402
from stc_calc import nl     # noqa: E402

G_ACC = 9.81

# From the model (build_sfw.mass_properties, arm out left). kg, (x, y, z) mm wagon coordinates.
DRY = {"wagon": (2506.6, (0.0, 130.0, 950.0)), "kit": (40.6, (-331.0, -2588.0, 1091.0)),
       "box": (67.6, (15.0, -3498.0, 706.0)), "mast": (27.0, (-1279.0, -3835.0, 2048.0)),
       "hoses": (6.9, (-210.0, -2044.0, 1264.0))}
IBC_CG_Z = 450.0
TYRE_LOAD = 2575.0          # kg per tyre, 500/50-17 at 40 km/h (estimated, flotation tyre)


def _area():
    w = C.S.bottle_wall
    a, b, rr = 2.0 * (C.S.bottle_x - w), (C.S.bottle_y[1] - C.S.bottle_y[0]) - 2.0 * w, C.S.bottle_r - w
    return a * b - (4.0 - math.pi) * rr * rr


def liquid_cg_z(litres):
    return C.bottle_z0 + C.S.bottle_wall + 0.5 * litres * 1e6 / _area()


def rows(n):
    return P.rows(n)


def items(n_rows=P.n_rows, fill=1.0, rho=None):
    rho = C.liquid_density if rho is None else rho
    out = list(DRY.values())
    for y in rows(n_rows):
        for sx in (-1, 1):
            out.append((C.ibc_kg, (sx * P.ibc_x, y, P.deck_top + IBC_CG_Z)))
            litres = fill * C.ibc_nominal_l
            if litres > 0:
                out.append((litres * rho, (sx * P.ibc_x, y, P.deck_top + liquid_cg_z(litres))))
    return out


def cg(n_rows=P.n_rows, fill=1.0, rho=None):
    it = items(n_rows, fill, rho)
    m = sum(i[0] for i in it)
    return m, tuple(sum(i[0] * i[1][k] for i in it) / m for k in range(3))


def loads(n_rows=P.n_rows, fill=1.0, rho=None):
    m, (x, y, z) = cg(n_rows, fill, rho)
    front = m * (y + P.axle_y) / (2.0 * P.axle_y)
    rear = m - front
    payload = m - DRY["wagon"][0]
    side = math.degrees(math.atan2(P.wheel_x - abs(x), z))
    return {"total": m, "front": front, "rear": rear, "tyre": max(front, rear) / 2.0, "payload": payload,
            "cg": (x, y, z), "tip_side": side}


def pump_geometry():
    low = P.deck_top + C.bottle_z0 + C.S.bottle_wall
    lift = (0.5 * (P.arm_z[0] + P.arm_z[1]) - low) / 1000.0
    header = (max(rows(P.n_rows)) - P.header_hole_y) / 1000.0 + 0.7 + 1.0
    discharge = 1.3 + (P.arm_z[1] - P.box_z()) / 1000.0 + P.reach() / 1000.0 + 1.2
    return lift, header + discharge


def report():
    out = []
    add = out.append
    n_ibc = 2 * P.n_rows
    add("######## Flat wagon, %d rows = %d IBC ########" % (P.n_rows, n_ibc))
    add("== Layout ==")
    add("deck %s x %s mm at %s mm, IBC top %s mm; rows at y %s; mast on the rear left corner, reach %s mm "
        "(nozzle at x %s), arm at %s mm, nozzle %s mm" % (
            nl(P.deck_l), nl(P.deck_w), nl(P.deck_top), nl(P.ibc_top()), ", ".join(nl(y) for y in rows(P.n_rows)),
            nl(P.reach()), nl(P.nozzle_x()), nl(P.arm_z[0]), nl(P.nozzle_z)))
    add("== Masses and axle loads (kg, %s kg/l; wagon %s kg from the model) ==" % (nl(C.liquid_density, 2),
                                                                                  nl(DRY["wagon"][0])))
    for n in (1, 2, 3, 4):
        L = loads(n, 1.0)
        add("%d rows (%d IBC) full: total %s, payload %s (wagon ~%s); front axle %s, rear %s, per tyre %s (limit %s); "
            "cg %s mm high, tipping sideways %s deg" % (
                n, 2 * n, nl(L["total"]), nl(L["payload"]), nl(P.wagon_payload), nl(L["front"]), nl(L["rear"]),
                nl(L["tyre"]), nl(TYRE_LOAD), nl(L["cg"][2]), nl(L["tip_side"], 1)))
    mc = K.arm_mast_check(P.reach(), P.arm_z[0] - P.deck_top, C.mast_tube, drop_m=1.1)
    add("mast and arm: %s Nm at the foot, mast %s MPa, arm %s MPa (x2), tip deflection %s mm" % (
        nl(mc["moment_nm"]), nl(mc["mast_mpa"], 1), nl(mc["arm_mpa"], 1), nl(mc["tip_defl_mm"], 2)))
    lift, hose_m = pump_geometry()
    out += K.common_report(n_ibc, lift, hose_m, "%d IBC" % n_ibc)
    add("pump axis %s mm (box under the deck), bottom of the bottles %s mm: the pump stays flooded" % (
        nl(P.box_z() + C.pump_axis[1]), nl(P.deck_top + C.bottle_z0)))
    return "\n".join(out)


if __name__ == "__main__":
    print(report())
