"""Calculations for the mobile refiller (liquid): capacity, masses and wheel loads, traction, stability, pump and hose,
the refill window in the headland turn of the working robot, logistics and energy.

Pure Python (no FreeCAD): python mrl_calc.py prints the report. The animation (animate_mrl.py) uses the same functions.
Masses of the kit and the trailer come from the model (build_mrl.mass_properties()); update DRY when the model changes.
"""
import math

import mrl_params as P

G_ACC = 9.81

# ---------------------------------------------------------------------
# From the model (build_mrl.mass_properties, boom parked, trailer straight). kg, (x, y, z) mm robot coordinates.
# ---------------------------------------------------------------------
DRY = {
    "robot": (P.robot_kg, (0.0, 0.0, 450.0)),          # estimated: robot not weighed, cg 500 in front of rear axle
    "kit": (119.8, (0.0, -482.0, 832.0)),              # tank, pump, sub-frame, column, boom (boom parked backwards)
    "trailer": (107.3, (-8.0, -2064.0, 533.0)),        # frame, 2 wheel units with hub motors, tank, drawbar, jack
}
BOOM = (19.6, 1399.0)            # moving part of the boom (kg, cg height); trolley + spout + hose about 5 kg
HEAD_KG = 5.0
TANK_CG = {"refiller": (0.0, -44.0), "trailer": (0.0, -2230.0)}    # (x, y) of the liquid (model)

# Working robot (liquid fertilizer applicator advanced) and the turn
WORK_WIDTH = 1000.0              # mm, 5 rows at 200
R_TURN = 2400.0                  # arcs of the turn with three points (as agbot slim: planner R 2.4 m)
V_WORK = 0.75                    # m/s
V_HEAD = 0.5
V_REV = 0.4
ACCEL = 0.5                      # m/s2
SWEEP_OUT = 734.0                # corner of the working robot outside its path in the arcs (R 2400)
DOSE_STD = 505.0                 # l/ha (applicator advanced, standard)


# ---------------------------------------------------------------------
# Tanks
# ---------------------------------------------------------------------
def tank_sections(kind):
    """Inner sections ((z0, z1, area mm2), ...) of a tank, bottom up (rounded rectangles, wall P.tank_wall)."""
    w = P.tank_wall

    def area(hx, y, r):
        a, b, rr = 2.0 * (hx - w), (y[1] - y[0]) - 2.0 * w, max(0.0, r - w)
        return a * b - (4.0 - math.pi) * rr * rr
    if kind == "refiller":
        return ((P.sump_z0 + w, P.tank_z0 + w, area(P.sump_x, P.sump_y, P.sump_r)),
                (P.tank_z0 + w, P.tank_z[1] - w, area(P.tank_x, P.tank_y, P.tank_r)))
    if kind == "trailer":
        return ((P.tank_z0 + w, P.tank_z0 + P.tr_tank_h - w, area(P.tr_tank_x, P.tr_tank_y, P.tr_tank_r)),)
    return ((P.tank_z0 + w, P.tank_z0 + P.rx_tank_h - w, area(P.rx_tank_x, P.rx_tank_y, P.rx_tank_r)),)


def volume_l(kind, level_z):
    return sum(a * max(0.0, min(level_z, z1) - z0) for z0, z1, a in tank_sections(kind)) / 1e6


def level_for(kind, litres):
    v = litres * 1e6
    secs = tank_sections(kind)
    for z0, z1, a in secs:
        cap = a * (z1 - z0)
        if v <= cap:
            return z0 + v / a
        v -= cap
    return secs[-1][1]


def capacity_l(kind):
    return volume_l(kind, tank_sections(kind)[-1][1])


def liquid_cg_z(kind, litres):
    """Height of the centre of gravity of the liquid (mm)."""
    lvl = level_for(kind, litres)
    m, mz = 0.0, 0.0
    for z0, z1, a in tank_sections(kind):
        h = max(0.0, min(lvl, z1) - z0)
        m += a * h
        mz += a * h * (z0 + h / 2.0)
    return mz / m if m > 0 else tank_sections(kind)[0][0]


# ---------------------------------------------------------------------
# Masses, hitch load, wheel loads
# ---------------------------------------------------------------------
def loads(fill=1.0, trailer=True, trailer_fill=None):
    """Wheel loads (kg) with the tanks filled to 'fill' (0..1). Robot axles at y = +-500, trailer axle tr_axle_y,
    hitch at P.hitch."""
    trailer_fill = fill if trailer_fill is None else trailer_fill
    rho = P.liquid_density
    lr = fill * capacity_l("refiller") * rho
    lt = trailer_fill * capacity_l("trailer") * rho
    items_r = [DRY["robot"], DRY["kit"], (lr, (0.0, TANK_CG["refiller"][1], liquid_cg_z("refiller", lr / rho)))]
    hitch = 0.0
    trail_m = 0.0
    if trailer:
        items_t = [DRY["trailer"], (lt, (0.0, TANK_CG["trailer"][1], liquid_cg_z("trailer", lt / rho)))]
        trail_m = sum(m for m, _ in items_t)
        moment = sum(m * (c[1] - P.tr_axle_y) for m, c in items_t)
        hitch = moment / (P.hitch[1] - P.tr_axle_y)
    m_robot = sum(m for m, _ in items_r)
    y_f, y_r = P.robot_axle_y, -P.robot_axle_y
    mom = sum(m * (c[1] - y_r) for m, c in items_r) + hitch * (P.hitch[1] - y_r)
    front = mom / (y_f - y_r)
    rear = m_robot + hitch - front
    return {"robot_total": m_robot, "hitch": hitch, "front_wheel": front / 2.0, "rear_wheel": rear / 2.0,
            "trailer_total": trail_m, "trailer_wheel": (trail_m - hitch) / 2.0,
            "train_total": m_robot + trail_m, "liquid_robot": lr, "liquid_trailer": lt}


def cg_robot(fill=1.0, boom_side=False):
    """Centre of gravity of the refiller robot (x, z); boom_side: boom fully out to the side with the spout down."""
    rho = P.liquid_density
    lr = fill * capacity_l("refiller") * rho
    items = [DRY["robot"], DRY["kit"], (lr, (0.0, 0.0, liquid_cg_z("refiller", lr / rho)))]
    if boom_side:
        # boom parked over the hitch (in DRY["kit"]) swung to the side: move its mass from x 0 to x -r/2 ... -r
        m_b = BOOM[0]
        items.append((-m_b, (0.0, 0.0, BOOM[1])))
        items.append((m_b - HEAD_KG, (-(P.r_max + P.boom_v[0]) / 2.0 - 100.0, 0.0, BOOM[1])))
        items.append((HEAD_KG + 2.0, (-P.r_max, 0.0, 1300.0)))       # head, spout and hose with liquid
    m = sum(i[0] for i in items)
    x = sum(i[0] * i[1][0] for i in items) / m
    z = sum(i[0] * i[1][2] for i in items) / m
    return m, x, z


def tip_angle(fill=1.0, boom_side=False):
    """Static side tipping angle (degrees) of the refiller robot about the line through the tyre contacts.
    The boom out to the side shifts the cg towards that side (worst case: tipping to the boom side)."""
    m, x, z = cg_robot(fill, boom_side)
    half = P.robot_wheel_x - abs(x)
    return math.degrees(math.atan2(half, z))


def tip_angle_trailer(fill=1.0):
    rho = P.liquid_density
    lt = fill * capacity_l("trailer") * rho
    items = [DRY["trailer"], (lt, (0.0, 0.0, liquid_cg_z("trailer", lt / rho)))]
    m = sum(i[0] for i in items)
    z = sum(i[0] * i[1][2] for i in items) / m
    return math.degrees(math.atan2(P.robot_wheel_x, z))


# ---------------------------------------------------------------------
# Traction (same approach as agbot comparison): per driven wheel min(mu x load, motor), minus rolling resistance
# and grade resistance of the whole train
# ---------------------------------------------------------------------
def traction(fill=1.0, mu=None, grade=0.0, powered_trailer=True, trailer=True):
    mu = P.mu["wet"] if mu is None else mu
    L = loads(fill, trailer)
    wheels = [L["front_wheel"]] * 2 + [L["rear_wheel"]] * 2
    if trailer and powered_trailer:
        wheels += [L["trailer_wheel"]] * 2
    drive = sum(min(mu * w, P.motor_cont_kgf) for w in wheels)
    total = L["train_total"] if trailer else L["robot_total"]
    resist = total * (P.c_rr + grade)
    return {"drive_kgf": drive, "resist_kgf": resist, "margin_kgf": drive - resist, "ok": drive >= resist,
            "motor_limited": sum(1 for w in wheels if mu * w > P.motor_cont_kgf)}


def max_grade(fill=1.0, mu=None, powered_trailer=True, trailer=True):
    lo, hi = 0.0, 0.5
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if traction(fill, mu, mid, powered_trailer, trailer)["ok"]:
            lo = mid
        else:
            hi = mid
    return lo


# ---------------------------------------------------------------------
# Pump and hose
# ---------------------------------------------------------------------
HOSE_LEN = {"suction": 0.9, "discharge": 0.9 + 0.8 + 1.8 + 0.6}     # m: pump -> column, column, carrier, spout
K_MINOR = 9.0                    # elbows, tee, 2 ball valves, swivel, carrier bends, spout nozzle (estimated)
PUMP_H0 = 18.0                   # m shut-off head
PUMP_Q0 = 190.0                  # l/min free flow (centrifugal 24 V, 1.5"; estimated curve H = H0 (1 - (Q/Q0)^2))


def static_lift():
    """From the lowest liquid level in the sump to the spout outlet when docked (m)."""
    return (P.SPOUT_TIP_DOWN - (P.sump_z0 + P.tank_wall)) / 1000.0


def system_head(q_lpm):
    q = q_lpm / 60000.0
    d = P.hose_d / 1000.0
    a = math.pi * d * d / 4.0
    v = q / a
    if v <= 0:
        return static_lift()
    re = v * d / P.liquid_viscosity
    f = 64.0 / re if re < 2300 else 0.316 * re ** -0.25
    length = sum(HOSE_LEN.values())
    hv = v * v / (2.0 * G_ACC)
    return static_lift() + (f * length / d + K_MINOR + 1.0) * hv


def pump_head(q_lpm):
    return PUMP_H0 * (1.0 - (q_lpm / PUMP_Q0) ** 2)


def operating_point():
    lo, hi = 0.0, PUMP_Q0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if pump_head(mid) > system_head(mid):
            lo = mid
        else:
            hi = mid
    q = 0.5 * (lo + hi)
    h = system_head(q)
    p_hyd = P.liquid_density * 1000.0 * G_ACC * (q / 60000.0) * h
    v = (q / 60000.0) / (math.pi * (P.hose_d / 1000.0) ** 2 / 4.0)
    return {"q_lpm": q, "head_m": h, "v_ms": v, "p_hyd_w": p_hyd, "p_el_w": p_hyd / P.pump_eff}


def fill_rate_ls():
    """Flow used in the animation and the turn table (l/s): operating point, limited to pump_q_fill."""
    return min(operating_point()["q_lpm"], P.pump_q_fill) / 60.0


# ---------------------------------------------------------------------
# Refill window in the turn (turn with three points: forward arc, straight reverse, forward arc)
# ---------------------------------------------------------------------
def profile_time(dist, v, a):
    """Time for a move of dist (m) from standstill to standstill (trapezoid)."""
    if dist <= v * v / a:
        return 2.0 * math.sqrt(dist / a)
    return dist / v + v / a


def boom_times(r=None):
    """Swing out (slew 90 deg and trolley out together), spout down, spout up, swing back (s)."""
    r = math.sqrt(P.dock_d ** 2 - P.spout_u ** 2) if r is None else r
    slew = profile_time(math.radians(90.0), math.radians(P.slew_rate), math.radians(P.slew_acc))
    trolley = profile_time((r - P.r_park) / 1000.0, P.trolley_v / 1000.0, P.trolley_a / 1000.0)
    move = max(slew, trolley)
    down = P.spout_stroke / P.spout_v_speed
    return {"out": move, "down": down, "up": down, "back": move, "camera": 0.5}


def turn_window(work_width=WORK_WIDTH, r=R_TURN, v_rev=V_REV, acc=ACCEL):
    straight = (2.0 * r - work_width) / 1000.0
    t_straight = profile_time(straight, v_rev, acc)
    b = boom_times()
    # the boom swings out while the worker sets its wheels straight (standstill); the pump runs from spout down
    # until spout up; spout up at the end of the straight, the boom swings back while the worker steers for the arc
    t_pump = t_straight
    return {"straight_m": straight, "t_straight": t_straight, "t_pump": t_pump, "t_stop_extra": b["out"] + b["camera"] +
            b["down"], "litres": t_pump * fill_rate_ls()}


def per_round_l(dose, field_len_m, work_width=WORK_WIDTH):
    """Liquid used between two visits on the same headland: 2 passes (there and back)."""
    return dose * 1e-4 * (work_width / 1000.0) * 2.0 * field_len_m


def turn_table(doses=(100.0, 250.0, 505.0, 1000.0, 2000.0), lengths=(100.0, 200.0, 400.0)):
    """Extra standstill (s) in the turn to top up what 2 passes used (0 = fits in the straight)."""
    w = turn_window()
    q = fill_rate_ls()
    rows = []
    for dose in doses:
        row = []
        for length in lengths:
            need = per_round_l(dose, length)
            row.append((need, max(0.0, need / q - w["t_pump"])))
        rows.append((dose, row))
    return rows


def headland_depth(y_turn=1.8, r=R_TURN):
    """Headland depth (m) from the field edge: without and with the refiller beside the straight."""
    ys = y_turn + r / 1000.0
    without = ys + SWEEP_OUT / 1000.0 + 0.3
    with_r = ys + (P.dock_d + P.robot_half_width) / 1000.0 + 0.3
    return without, with_r


# ---------------------------------------------------------------------
# Logistics
# ---------------------------------------------------------------------
def worker_rate_ha_h(v=V_WORK, eff=0.8):
    return v * 3.6 * WORK_WIDTH / 1000.0 / 10.0 * eff


def logistics(dose=DOSE_STD, dist_m=500.0, v=P.v_drive, farm_fill_lpm=200.0):
    """With and without the refiller. Distance = one way to the farm tank / IBC."""
    cap = capacity_l("refiller") + capacity_l("trailer")
    work_tank = capacity_l("receiver")
    rate = worker_rate_ha_h()
    ha_load = cap / dose
    h_load = ha_load / rate
    trip_min = (2.0 * dist_m / v) / 60.0 + cap / farm_fill_lpm + 3.0
    ha_tank = work_tank / dose
    h_tank = ha_tank / rate
    # without refiller: the worker drives to the farm (empty tank), fills and comes back
    self_trip_min = (2.0 * dist_m / v) / 60.0 + work_tank / farm_fill_lpm + 3.0
    eff_without = h_tank * 60.0 / (h_tank * 60.0 + self_trip_min)
    return {"capacity_l": cap, "ha_per_load": ha_load, "h_per_load": h_load, "trip_min": trip_min,
            "buffer_min": h_tank * 60.0, "ha_per_work_tank": ha_tank, "self_trip_min": self_trip_min,
            "eff_without": eff_without, "rate_ha_h": rate}


# ---------------------------------------------------------------------
# Energy
# ---------------------------------------------------------------------
def energy_wh_per_load(dist_m=500.0, eff_drive=0.6):
    op = operating_point()
    pump_wh = op["p_el_w"] * (capacity_l("refiller") + capacity_l("trailer")) / op["q_lpm"] / 60.0
    full = loads(1.0)["train_total"]
    empty = loads(0.0)["train_total"]
    drive_wh = (P.c_rr * G_ACC * (full + empty) * dist_m) / eff_drive / 3600.0
    return {"pump_wh": pump_wh, "drive_wh": drive_wh, "loads_per_battery": P.battery_kwh * 1000.0 * 0.8 /
            (pump_wh + drive_wh + 60.0)}


# ---------------------------------------------------------------------
# Boom and column
# ---------------------------------------------------------------------
def boom_loads(shock=2.0):
    """Bending moment at the column foot with the boom fully out (Nm), bolt tension in the base plate (N),
    slew torque at slew_acc (Nm), boom tip deflection (mm)."""
    m_boom = BOOM[0] - HEAD_KG
    r_cg = (P.boom_v[1] + P.boom_v[0]) / 2.0 / 1000.0
    m_head = HEAD_KG + 2.0            # head + hose with liquid
    moment = G_ACC * (m_boom * r_cg + m_head * P.r_max / 1000.0)
    lever = (P.robot_lower_beam_y[1] - P.robot_lower_beam_y[0]) / 1000.0
    bolt = shock * moment / lever / 2.0           # 2 bolts per row in tension
    j = m_boom * ((P.boom_v[1] - P.boom_v[0]) / 1000.0) ** 2 / 12.0 + m_boom * r_cg ** 2 + m_head * (P.r_max / 1000.0) ** 2
    torque = j * math.radians(P.slew_acc)
    e, i = 70e9, 60e-8                                    # aluminium profile 80 x 55: I ~ 60 cm4 (estimated)
    span = P.r_max / 1000.0
    w = m_boom / ((P.boom_v[1] - P.boom_v[0]) / 1000.0) * G_ACC
    defl = (m_head * G_ACC * span ** 3 / (3 * e * i) + w * span ** 4 / (8 * e * i)) * 1000.0
    return {"moment_nm": moment, "bolt_n": bolt, "slew_torque_nm": torque, "tip_defl_mm": defl}


# ---------------------------------------------------------------------
# Docking accuracy
# ---------------------------------------------------------------------
def docking_tolerance():
    """Allowed spout offset (mm) at the rim and at the lowered tip; error budget (2 sigma)."""
    d0, d1 = P.funnel_d
    z0 = P.tank_z0 + P.rx_tank_h + P.funnel_neck
    at_tip = d1 + (d0 - d1) * (P.SPOUT_TIP_DOWN - z0) / P.funnel_h
    nozzle = 36.0
    budget = {"spout RTK (antenna on the spout axis)": 20.0, "working robot: GNSS + heading x funnel offset": 25.0,
              "relative motion while driving (lag, bumps)": 30.0, "tilt of the mast (IMU corrected)": 10.0}
    rss = math.sqrt(sum(v * v for v in budget.values()))
    return {"rim": (d0 - P.spout_d) / 2.0, "at_tip": (at_tip - nozzle) / 2.0, "budget": budget, "rss_gnss": rss,
            "rss_camera": math.sqrt(10.0 ** 2 + 10.0 ** 2)}


# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------
def nl(v, d=0):
    return ("%%.%df" % d) % v


def report():
    out = []
    add = out.append
    add("== Capacity ==")
    add("refiller tank %s l (sump %s l), trailer %s l, total %s l; work tank on the working robot %s l" % (
        nl(capacity_l("refiller")), nl(sum(a * (z1 - z0) for z0, z1, a in tank_sections("refiller")[:1]) / 1e6),
        nl(capacity_l("trailer")), nl(capacity_l("refiller") + capacity_l("trailer")), nl(capacity_l("receiver"))))
    add("== Masses and wheel loads (kg) ==")
    for fill in (0.0, 1.0):
        L = loads(fill)
        add("fill %3d %%: robot %s, trailer %s, train %s; hitch %s; per wheel front %s, rear %s, trailer %s "
            "(limit %d)" % (fill * 100, nl(L["robot_total"]), nl(L["trailer_total"]), nl(L["train_total"]),
                            nl(L["hitch"]), nl(L["front_wheel"]), nl(L["rear_wheel"]), nl(L["trailer_wheel"]),
                            P.wheel_load_max))
    L = loads(1.0, trailer=False)
    add("without trailer, full: robot %s kg, front %s / rear %s per wheel" % (nl(L["robot_total"]), nl(L["front_wheel"]),
                                                                            nl(L["rear_wheel"])))
    add("== Traction (continuous, c_rr %.2f) ==" % P.c_rr)
    for fill in (0.0, 1.0):
        for name, mu in P.mu.items():
            a = traction(fill, mu)
            b = traction(fill, mu, powered_trailer=False)
            add("fill %3d %%, %s: drive %s kgf (6 wheels) / %s kgf (4 wheels) vs resistance %s kgf; max grade %s %% / %s %%"
                % (fill * 100, name, nl(a["drive_kgf"]), nl(b["drive_kgf"]), nl(a["resist_kgf"]),
                   nl(100 * max_grade(fill, mu)), nl(100 * max_grade(fill, mu, False))))
    add("== Stability (static side tipping angle) ==")
    add("refiller robot: empty %s deg, full %s deg, full with the boom out to the side %s deg; trailer full %s deg" % (
        nl(tip_angle(0.0), 1), nl(tip_angle(1.0), 1), nl(tip_angle(1.0, True), 1), nl(tip_angle_trailer(1.0), 1)))
    add("== Pump and hose ==")
    op = operating_point()
    add("static lift %s m, operating point %s l/min at %s m head, %s m/s in the hose, %s W hydraulic, %s W electric" % (
        nl(static_lift(), 2), nl(op["q_lpm"]), nl(op["head_m"], 1), nl(op["v_ms"], 1), nl(op["p_hyd_w"]),
        nl(op["p_el_w"])))
    add("flow used: %s l/s; full refiller + trailer emptied in %s min" % (
        nl(fill_rate_ls(), 2), nl((capacity_l("refiller") + capacity_l("trailer")) / (fill_rate_ls() * 60.0), 1)))
    add("== Refill in the turn ==")
    w = turn_window()
    b = boom_times()
    add("straight reverse %s m in %s s; boom out %s s, camera %s s, spout down %s s; pump %s s = %s l per turn" % (
        nl(w["straight_m"], 1), nl(w["t_straight"], 1), nl(b["out"], 1), nl(b["camera"], 1), nl(b["down"], 1),
        nl(w["t_pump"], 1), nl(w["litres"], 1)))
    add("extra standstill (s) to top up 2 passes, field length 100 / 200 / 400 m:")
    for dose, row in turn_table():
        add("  %5d l/ha: %s" % (dose, ", ".join("%s l -> %s s" % (nl(n, 1), nl(t, 0)) for n, t in row)))
    hw, hr = headland_depth()
    add("headland depth: %s m without, %s m with the refiller beside the straight (+%s m)" % (nl(hw, 1), nl(hr, 1),
                                                                                             nl(hr - hw, 1)))
    add("== Logistics (505 l/ha, farm tank 500 m away) ==")
    lg = logistics()
    add("one load %s l = %s ha = %s h of work; refiller trip to the farm and back %s min; work tank buffer %s min" % (
        nl(lg["capacity_l"]), nl(lg["ha_per_load"], 2), nl(lg["h_per_load"], 1), nl(lg["trip_min"]),
        nl(lg["buffer_min"])))
    add("without refiller: the working robot drives to the farm every %s ha, %s min per trip: field efficiency %s %%"
        % (nl(lg["ha_per_work_tank"], 2), nl(lg["self_trip_min"]), nl(100 * lg["eff_without"])))
    for d in (200.0, 1000.0, 2000.0):
        lg = logistics(dist_m=d)
        add("  farm tank %4d m: refiller trip %s min (buffer %s min), without refiller %s %%" % (
            d, nl(lg["trip_min"]), nl(lg["buffer_min"]), nl(100 * lg["eff_without"])))
    e = energy_wh_per_load()
    add("energy per load (500 m): pump %s Wh, driving %s Wh; about %s loads per battery (%s kWh)" % (
        nl(e["pump_wh"]), nl(e["drive_wh"]), nl(e["loads_per_battery"], 1), nl(P.battery_kwh, 1)))
    add("== Boom ==")
    bl = boom_loads()
    add("moment at the column foot %s Nm (boom out, static), bolt tension %s N per M10 (x2 shock), slew torque %s Nm, "
        "tip deflection %s mm" % (nl(bl["moment_nm"]), nl(bl["bolt_n"]), nl(bl["slew_torque_nm"], 1),
                                  nl(bl["tip_defl_mm"], 1)))
    dt = docking_tolerance()
    add("docking: spout may be %s mm off at the rim, %s mm at the lowered tip; error 2 sigma %s mm with GNSS only, "
        "%s mm with the camera" % (nl(dt["rim"]), nl(dt["at_tip"]), nl(dt["rss_gnss"]), nl(dt["rss_camera"])))
    return "\n".join(out)


if __name__ == "__main__":
    print(report())
