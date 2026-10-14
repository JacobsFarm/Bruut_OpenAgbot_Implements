"""Calculations shared by the three stationary refill stations (pure Python, no FreeCAD).

- pump and hose: operating point for a given lift and hose length (same pump curve as the other refillers);
- a refill at the station: standstill of the working robot, and the detour to the station along the headland;
- field efficiency compared with driving to the farm and with the mobile refiller;
- battery: refills and days per charge;
- steel sections.

The carrier folders call these with their own geometry (<p>_calc.py).
"""
import math

import stc_params as P

G_ACC = 9.81


# ---------------------------------------------------------------------
# Pump and hose
# ---------------------------------------------------------------------
K_MINOR = 8.0       # IBC valve, camlock, bends, flow meter, motorised ball valve, drip-stop nozzle (estimated)


def pump_head(q_lpm):
    return P.pump_h0 * (1.0 - (q_lpm / P.pump_q0) ** 2)


def system_head(q_lpm, lift_m, hose_m):
    q = q_lpm / 60000.0
    d = P.hose_d / 1000.0
    v = q / (math.pi * d * d / 4.0)
    if v <= 0:
        return lift_m
    re = v * d / P.liquid_viscosity
    f = 64.0 / re if re < 2300 else 0.316 * re ** -0.25
    return lift_m + (f * hose_m / d + K_MINOR + 1.0) * v * v / (2.0 * G_ACC)


def operating_point(lift_m, hose_m):
    lo, hi = 0.0, P.pump_q0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if pump_head(mid) > system_head(mid, lift_m, hose_m):
            lo = mid
        else:
            hi = mid
    q = 0.5 * (lo + hi)
    h = system_head(q, lift_m, hose_m)
    p = P.liquid_density * 1000.0 * G_ACC * (q / 60000.0) * h / P.pump_eff
    return {"q_lpm": q, "head_m": h, "p_el_w": p}


def fill_power(lift_m, hose_m, q=None):
    q = P.pump_q_fill if q is None else q
    return P.liquid_density * 1000.0 * G_ACC * (q / 60000.0) * system_head(q, lift_m, hose_m) / P.pump_eff


def fill_q(lift_m, hose_m):
    return min(operating_point(lift_m, hose_m)["q_lpm"], P.pump_q_fill)


# ---------------------------------------------------------------------
# Refill at the station
# ---------------------------------------------------------------------
def refill_time(litres, q_lpm):
    """Standstill at the nozzle (s): check, pump, close (the docking itself is in t_dock)."""
    return P.t_check + litres / q_lpm * 60.0 + P.t_close


def per_pass_l(dose, field_len_m):
    return dose * 1e-4 * (P.work_width / 1000.0) * field_len_m


def visit(dose, field_len_m, field_w_m, q_lpm, station_x=None):
    """The working robot calls at the station when its work tank is low. It refills rx_refill_l. Between visits it
    works k passes (always an even number: it is on the station headland again). Average detour along the headland
    to a station at station_x (default: the middle of the headland) and back: 2 x mean |x - xs|.
    Returns the time per visit and the share of the working time."""
    per = per_pass_l(dose, field_len_m)
    k = max(2, 2 * int(P.rx_refill_l / per // 2))              # passes between visits (even)
    litres = k * per
    xs = field_w_m / 2.0 if station_x is None else station_x
    # mean |x - xs| for x uniform over the field width
    a, b = xs, field_w_m - xs
    mean = (a * a + b * b) / (2.0 * field_w_m)
    detour = 2.0 * mean / P.v_head
    t = detour + P.t_dock + refill_time(litres, q_lpm)
    work = k * (field_len_m / P.v_work + 15.0)                 # passes + their turns (U-turn ~15 s)
    return {"passes": k, "litres": litres, "detour_s": detour, "visit_s": t, "share": t / (work + t),
            "ha_per_visit": litres / dose}


def visit_table(q_lpm, doses=(250.0, 505.0, 1000.0), widths=(50.0, 100.0, 200.0), field_len_m=200.0):
    rows = []
    for dose in doses:
        rows.append((dose, [visit(dose, field_len_m, w, q_lpm) for w in widths]))
    return rows


def farm_trip_share(dist_m, dose=None, field_len_m=200.0):
    """Without any refiller: the working robot drives to a farm tank at dist_m (both ways at 1 m/s) and fills
    its whole tank at 200 l/min with 3 min handling."""
    dose = P.dose_std if dose is None else dose
    per = per_pass_l(dose, field_len_m)
    k = max(2, 2 * int(P.rx_refill_l / per // 2))
    work = k * (field_len_m / P.v_work + 15.0)
    t = 2.0 * dist_m / 1.0 + k * per / 200.0 * 60.0 + 180.0
    return t / (work + t)


# ---------------------------------------------------------------------
# Station: capacity and battery
# ---------------------------------------------------------------------
def station_ha(n_ibc, dose=None):
    dose = P.dose_std if dose is None else dose
    return n_ibc * P.ibc_nominal_l / dose


def work_hours(n_ibc, dose=None, eff=0.8):
    dose = P.dose_std if dose is None else dose
    rate = P.v_work * 3.6 * P.work_width / 1000.0 / 10.0 * eff         # ha/h
    return station_ha(n_ibc, dose) / rate


def battery_days(n_ibc, lift_m, hose_m, days_solar=False):
    """Battery 25.6 V 50 Ah (80 % usable): Wh to pump all IBCs, standby per day, days until empty."""
    q = P.pump_q_fill
    pump_wh = fill_power(lift_m, hose_m) * n_ibc * P.ibc_nominal_l / q / 60.0
    day = P.standby_w * 24.0
    usable = 0.8 * P.battery_wh
    days = (usable - pump_wh) / day
    return {"pump_wh": pump_wh, "standby_wh_day": day, "days": days,
            "solar_wh_day": P.solar_w * 3.0}       # 3 equivalent full-sun hours (NL, spring/summer, estimated)


def nozzle_tolerance():
    """Allowed offset (mm) of the stream from the funnel axis and the error budget (2 sigma). The station stands
    still: the antenna position is averaged over minutes (better than the moving refiller)."""
    stream = 25.0
    tol = P.S.funnel_d[0] / 2.0 - stream / 2.0 - 10.0
    budget = {"antenna above the nozzle (RTK, averaged while parked)": 15.0,
              "tilt of the mast x 0.75 m (IMU in the box)": 10.0,
              "working robot: GNSS + heading x funnel offset": 25.0, "working robot: stopping position": 30.0}
    return {"tolerance": tol, "budget": budget, "rss": math.sqrt(sum(v * v for v in budget.values()))}


# ---------------------------------------------------------------------
# Steel sections
# ---------------------------------------------------------------------
def w_rect_tube(b, h, t):
    """Section modulus (mm3) and I (mm4) of a rectangular tube b wide, h high, wall t (bending about the axis
    parallel to b)."""
    i = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12.0
    return i / (h / 2.0), i


def arm_mast_check(reach, mast_h, mast_tube, arm_tube=P.arm_tube, drop_m=0.7, dyn=2.0):
    """Moment at the mast foot from the arm out (Nm), stress in mast and arm (x dyn), tip deflection (mm)."""
    arm_len = reach + P.arm_tip
    b, t = arm_tube
    arm_kg = 7.85e-6 * (b * b - (b - 2 * t) ** 2) * arm_len
    tip_kg = 0.9 * drop_m + 2.0 * drop_m * P.liquid_density + 0.5 + 1.2
    hose_kg = (0.6 + 1.13 * P.liquid_density) * arm_len / 1000.0
    moment = G_ACC * ((arm_kg + hose_kg) * arm_len / 2000.0 + tip_kg * reach / 1000.0)
    w_m, i_m = w_rect_tube(mast_tube[0], mast_tube[0], mast_tube[1])
    w_a, i_a = w_rect_tube(b, b, t)
    e = 210e9
    rot = moment * mast_h / 1000.0 / (e * i_m * 1e-12)
    l = reach / 1000.0
    defl = rot * l + tip_kg * G_ACC * l ** 3 / (3 * e * i_a * 1e-12) + (arm_kg + hose_kg) * G_ACC * l ** 3 / (
        8 * e * i_a * 1e-12)
    return {"moment_nm": moment, "mast_mpa": dyn * moment * 1000.0 / w_m, "arm_mpa": dyn * moment * 1000.0 / w_a,
            "tip_defl_mm": defl * 1000.0}


def nl(v, d=0):
    return ("%%.%df" % d) % v


def common_report(n_ibc, lift_m, hose_m, label):
    out = []
    add = out.append
    op = operating_point(lift_m, hose_m)
    q = fill_q(lift_m, hose_m)
    add("== Pump and hose (%s) ==" % label)
    add("lift from the lowest level to the arm %s m, hose %s m; free operating point %s l/min at %s m; filling at "
        "%s l/min: %s W" % (nl(lift_m, 2), nl(hose_m, 1), nl(op["q_lpm"]), nl(op["head_m"], 1), nl(q),
                             nl(fill_power(lift_m, hose_m, q))))
    nt = nozzle_tolerance()
    add("nozzle: stream may be %s mm off the funnel axis; error 2 sigma %s mm" % (nl(nt["tolerance"]), nl(nt["rss"])))
    add("== Capacity (%d IBC) ==" % n_ibc)
    add("%s l: %s ha at %s l/ha, %s h of work for one working robot (1 m, %s m/s, 80 %%)" % (
        nl(n_ibc * P.ibc_nominal_l), nl(station_ha(n_ibc), 2), nl(P.dose_std), nl(work_hours(n_ibc), 1),
        nl(P.v_work, 2)))
    add("== Visit to the station (field 200 m long, station in the middle of the headland) ==")
    add("refill %s l per visit; docking %s s (leave the turn, line up, stop, check); detour along the headland at "
        "%s m/s" % (nl(P.rx_refill_l), nl(P.t_dock), nl(P.v_head, 1)))
    for dose, row in visit_table(q):
        add("  %5d l/ha: %s" % (dose, "; ".join(
            "field %d m wide: every %d passes, %s l, %s s (%s %%)" % (w, r["passes"], nl(r["litres"]), nl(r["visit_s"]),
                                                                  nl(100 * r["share"], 1))
            for w, r in zip((50, 100, 200), row))))
    add("without a refiller (farm tank 500 / 1000 m away): %s / %s %% of the time" % (
        nl(100 * farm_trip_share(500.0), 1), nl(100 * farm_trip_share(1000.0), 1)))
    b = battery_days(n_ibc, lift_m, hose_m)
    add("== Battery 25.6 V 50 Ah ==")
    add("pumping %d IBC: %s Wh; standby %s Wh/day; %s days on one charge (a 100 W panel gives about %s Wh/day)" % (
        n_ibc, nl(b["pump_wh"]), nl(b["standby_wh_day"]), nl(b["days"], 1), nl(b["solar_wh_day"])))
    return out
