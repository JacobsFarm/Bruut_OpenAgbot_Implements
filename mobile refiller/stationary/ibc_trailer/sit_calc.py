"""Calculations for the IBC trailer station (1 or 2 IBCs): masses, axle and nose load, tyres, tipping, pump, the
visit of the working robot, battery, drawbar and mast.

Pure Python (no FreeCAD): python sit_calc.py prints the report for both configurations. Masses of the trailer, box,
mast and hoses come from the model (build_sit.mass_properties()); update DRY when the model changes.
"""
import math
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.dirname(FOLDER), FOLDER):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sit_params as P      # noqa: E402
import stc_params as C      # noqa: E402
import stc_calc as K        # noqa: E402
from stc_calc import nl     # noqa: E402

G_ACC = 9.81

# From the model (build_sit.mass_properties, arm out left). kg, (x, y, z) mm trailer coordinates.
DRY = {
    1: {"trailer": (323.3, (-12.0, 421.0, 407.0)), "box": (67.6, (82.0, 1445.0, 704.0)),
        "mast": (33.0, (-354.0, 1922.0, 1539.0)), "hoses": (1.2, (-2.0, 1547.0, 1036.0))},
    2: {"trailer": (446.2, (-10.0, 444.0, 491.0)), "box": (67.6, (82.0, 2210.0, 781.0)),
        "mast": (32.2, (-362.0, 2687.0, 1567.0)), "hoses": (2.1, (-1.0, 1541.0, 822.0))},
}
IBC_CG_Z = 450.0            # empty IBC (pallet, cage, bottle, valve, straps) cg above its base (model)


def liquid_cg_z(litres):
    """Liquid cg above the IBC base (rounded-rectangle bottle, uniform section)."""
    lvl = C.bottle_z0 + C.S.bottle_wall + litres * 1e6 / _area()
    return 0.5 * (C.bottle_z0 + C.S.bottle_wall + lvl)


def _area():
    w = C.S.bottle_wall
    a, b, rr = 2.0 * (C.S.bottle_x - w), (C.S.bottle_y[1] - C.S.bottle_y[0]) - 2.0 * w, C.S.bottle_r - w
    return a * b - (4.0 - math.pi) * rr * rr


def items(n, fill=1.0, rho=None):
    rho = C.liquid_density if rho is None else rho
    c = P.cfg(n)
    out = list(DRY[n].values())
    for y in c["ibc_y"]:
        out.append((C.ibc_kg, (0.0, y, c["deck_z"] + IBC_CG_Z)))
        litres = fill * C.ibc_nominal_l
        if litres > 0:
            out.append((litres * rho, (0.0, y, c["deck_z"] + liquid_cg_z(litres))))
    return out


def cg(n, fill=1.0, rho=None):
    it = items(n, fill, rho)
    m = sum(i[0] for i in it)
    return m, tuple(sum(i[0] * i[1][k] for i in it) / m for k in range(3))


def loads(n, fill=1.0, rho=None):
    """Axle and nose load (kg): moments about the axle, the tow eye (or the jockey wheel) carries the rest."""
    c = P.cfg(n)
    m, (x, y, z) = cg(n, fill, rho)
    nose = m * y / c["eye_y"]
    jockey = m * y / c["jockey_y"]
    axle = m - nose
    return {"total": m, "nose": nose, "jockey": jockey, "axle": axle, "tyre": axle / 2.0, "cg": (x, y, z),
            "tyre_limit": P.tyre_load[n]}


def tip_angle(n, fill=1.0):
    """Static sideways tipping angle over the wheels (deg), parked on the wheels and the jockey wheel (the line
    wheel - jockey wheel, which is closer to the cg than the wheel track)."""
    c = P.cfg(n)
    m, (x, y, z) = cg(n, fill)
    xw, yj = c["wheel_x"], c["jockey_y"]
    xj = -P.a_x(c, yj) - P.rail[0] / 2.0 - 45.0
    # distance from the cg (x, y) to the line (-xw, 0) - (xj, yj) in the ground plane
    ax, ay, bx, by = -xw, 0.0, xj, yj
    d = abs((bx - ax) * (ay - y) - (ax - x) * (by - ay)) / math.hypot(bx - ax, by - ay)
    return {"wheels": math.degrees(math.atan2(xw - abs(x), z)), "wheel_jockey": math.degrees(math.atan2(d, z)),
            "cg_z": z}


def pump_geometry(n):
    """Lift (m): lowest liquid level -> hose on the arm. Hose length (m): header + up to the box, box, mast, arm,
    drop pipe."""
    c = P.cfg(n)
    low = c["deck_z"] + C.bottle_z0 + C.S.bottle_wall
    lift = (0.5 * (C.arm_z[0] + C.arm_z[1]) - low) / 1000.0
    suction = (c["deck_front"] - c["elbow_y"][-1] + 300.0 + 400.0) / 1000.0
    discharge = (C.arm_z[1] - c["box_z"]) / 1000.0 + c["reach"] / 1000.0 + 0.7 + 0.6
    return lift, suction + discharge


def drawbar_check(n, dyn=2.5):
    """A-frame beams: bending from the nose load at the eye (x dyn for bumps), each beam carries half;
    lever = A length."""
    w, h, t = P.rail
    wb, _ = K.w_rect_tube(w, h, t)
    nose = loads(n)["nose"]
    m = dyn * nose * G_ACC / 2.0 * P.a_len
    return {"nose_kg": nose, "beam_mpa": m / wb}


def report(n=None):
    out = []
    add = out.append
    for n in ((1, 2) if n is None else (n,)):
        c = P.cfg(n)
        add("######## IBC trailer, %d IBC ########" % n)
        add("== Layout ==")
        add("tyres %s on a 70 mm square axle, track %s mm, overall width %s mm; deck at %s mm, IBC top %s mm" % (
            c["tyre_size"], nl(2 * c["wheel_x"]), nl(2 * c["half_width"]), nl(c["deck_z"]),
            nl(c["deck_z"] + C.ibc_top)))
        add("length %s mm (rear %s to tow eye %s); reach of the arm %s mm, transport lock %s deg (nozzle at x -%s)" % (
            nl(c["eye_y"] - c["deck_rear"] + 55.0), nl(c["deck_rear"]), nl(c["eye_y"]), nl(c["reach"]),
            nl(c["fold"], 1), nl(P.transport_x)))
        add("== Masses and loads (kg, %s kg/l) ==" % nl(C.liquid_density, 2))
        for fill in (0.0, 0.5, 1.0):
            L = loads(n, fill)
            add("IBC %4d l each: total %s; axle %s (per tyre %s, limit %s); nose %s at the eye, %s on the jockey "
                "wheel; cg %s mm high" % (fill * C.ibc_nominal_l, nl(L["total"]), nl(L["axle"]), nl(L["tyre"]),
                                          nl(L["tyre_limit"]), nl(L["nose"]), nl(L["jockey"]), nl(L["cg"][2])))
        for fill in (0.0, 1.0):
            ta = tip_angle(n, fill)
            add("tipping sideways (static), IBC %4d l: over the wheels %s deg, over the line wheel - jockey wheel "
                "%s deg" % (fill * C.ibc_nominal_l, nl(ta["wheels"], 1), nl(ta["wheel_jockey"], 1)))
        dc = drawbar_check(n)
        add("drawbar: A-beams %s MPa (x2.5 dynamic, nose %s kg)" % (nl(dc["beam_mpa"]), nl(dc["nose_kg"])))
        mc = K.arm_mast_check(c["reach"], C.arm_z[0] - c["rail_z"][1], C.mast_tube)
        add("mast and arm: %s Nm at the foot, mast %s MPa, arm %s MPa (x2), tip deflection %s mm" % (
            nl(mc["moment_nm"]), nl(mc["mast_mpa"], 1), nl(mc["arm_mpa"], 1), nl(mc["tip_defl_mm"], 2)))
        lift, hose_m = pump_geometry(n)
        out += K.common_report(n, lift, hose_m, "%d IBC" % n)
        add("pump axis %s mm, bottom of the bottle %s mm: the pump stays flooded" % (
            nl(c["box_z"] + C.pump_axis[1]), nl(c["deck_z"] + C.bottle_z0)))
        add("")
    return "\n".join(out)


if __name__ == "__main__":
    print(report())
