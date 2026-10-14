"""Calculations for the mobile refiller, simple (IBC): the skip pattern of the working robot (U-turns only), where the
refiller stands inside the turn and how much room it has, the refill standstill, wheel loads, traction, tipping,
pump and hose, the bed and the mast, logistics and energy.

Pure Python (no FreeCAD): python mrs_calc.py prints the report. The animation (animate_mrs.py) uses the same
functions. Masses of the kit come from the model (build_mrs.mass_properties()); update DRY when the model changes.

World coordinates of the field (calc and animation): x along the headland (pass p at x = (p - 1) W), y = 0 at the
field edge, headland at y > 0, mm. Headings psi as in the animation: 0 = +y (out of the field), + = counter-clockwise.
"""
import math

import mrs_params as P

G_ACC = 9.81

# ---------------------------------------------------------------------
# From the model (build_mrs.mass_properties, arm out). kg, (x, y, z) mm robot coordinates.
# ---------------------------------------------------------------------
DRY = {
    "robot": (P.robot_kg, (0.0, 0.0, 450.0)),          # estimated: robot not weighed, cg in the middle
    "kit": (74.6, (-293.0, -79.0, 979.0)),             # bed, mast, arm, pump, hoses, straps (arm out)
    "ibc": (sum(P.ibc_kg.values()), (-12.0, P.IBC_CY, 1184.0)),       # empty IBC (pallet, bottle, cage, valve, cap)
}

# Working robot (liquid fertilizer applicator advanced) and its turns
WORK_WIDTH = P.work_width
R_TURN = P.r_turn
R_MIN = 2107.0                   # agbot slim: rear-axle centre, inner front wheel 30 deg
V_WORK = 0.75                    # m/s
V_HEAD = 0.5
V_REV = 0.4
ACCEL = 0.5                      # m/s2
DOSE_STD = 505.0                 # l/ha (applicator advanced, standard)
T_CHECK = 0.5                    # s: radio handshake + both positions agree before the pump starts
T_CLOSE = 1.0                    # s: pump off, drip-stop nozzle closes, last drops
YS = P.y_turn + R_TURN           # straight part of the turn on the refiller headland


# ---------------------------------------------------------------------
# Tanks
# ---------------------------------------------------------------------
def _area(hx, y, r, w):
    a, b, rr = 2.0 * (hx - w), (y[1] - y[0]) - 2.0 * w, max(0.0, r - w)
    return a * b - (4.0 - math.pi) * rr * rr


BOTTLE_Z0 = P.IBC_Z0 + P.pallet_h


def tank_sections(kind):
    """Inner sections ((z0, z1, area mm2), ...) bottom up (rounded rectangles)."""
    if kind == "ibc":
        w = P.bottle_wall
        return ((BOTTLE_Z0 + w, BOTTLE_Z0 + P.bottle_h - w, _area(P.bottle_x, P.bottle_y, P.bottle_r, w)),)
    w = P.tank_wall
    return ((P.tank_z0 + w, P.tank_z0 + P.rx_tank_h - w, _area(P.rx_tank_x, P.rx_tank_y, P.rx_tank_r, w)),)


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
    lvl = level_for(kind, litres)
    m, mz = 0.0, 0.0
    for z0, z1, a in tank_sections(kind):
        h = max(0.0, min(lvl, z1) - z0)
        m += a * h
        mz += a * h * (z0 + h / 2.0)
    return mz / m if m > 0 else tank_sections(kind)[0][0]


# ---------------------------------------------------------------------
# Skip pattern: every turn a U-turn. Order 1, 1+N, 2, 2+N, ... in blocks of 2N passes; every other block mirrored
# (first pass N+1 further) so that the block change is a U-turn too.
# ---------------------------------------------------------------------
def skip_n(w=WORK_WIDTH, r=R_TURN):
    """Smallest jump N with (N - 1) W >= 2 R: U-turns of N W on the refiller headland and (N - 1) W or (N + 1) W
    on the far headland."""
    return int(math.ceil(2.0 * r / w)) + 1


def field_order(blocks=2, n=None):
    """Pass order (1-based) for 'blocks' blocks of 2N passes. Pass 1 starts at the far headland and goes into the
    refiller headland. Odd blocks: k, k+N; even blocks: k+N, k."""
    n = skip_n() if n is None else n
    out = []
    for b in range(blocks):
        base = 2 * n * b
        for k in range(1, n + 1):
            pair = (base + k, base + k + n) if b % 2 == 0 else (base + k + n, base + k)
            out.extend(pair)
    return out


def turns(order):
    """[(from, to, headland, width_m, middle_x_mm)]: headland 'R' = refiller headland (odd steps), 'F' = far end."""
    res = []
    for i, (a, b) in enumerate(zip(order[:-1], order[1:])):
        head = "R" if i % 2 == 0 else "F"
        res.append((a, b, head, abs(b - a) * WORK_WIDTH / 1000.0, (a + b - 2) * WORK_WIDTH / 2.0))
    return res


def refiller_moves(order):
    """Distances (m) the refiller drives between two refills (middles of successive refiller-headland turns)."""
    mids = [t[4] for t in turns(order) if t[2] == "R"]
    return [(b - a) / 1000.0 for a, b in zip(mids[:-1], mids[1:])]


# ---------------------------------------------------------------------
# Turn geometry: rear-axle path of a U-turn on the refiller headland (pass going +y, arc, straight, arc, pass
# going -y). Poses (x, y, psi).
# ---------------------------------------------------------------------
def _arc(c, r, a0, a1, step):
    n = max(1, int(abs(math.radians(a1 - a0)) * r / step))
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _line(p0, p1, step):
    n = max(1, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / step))
    return [(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n) for i in range(n + 1)]


def u_turn_points(x_from, x_to, y_turn=P.y_turn, r=R_TURN, y_in=-3000.0, y_out=-3000.0, step=20.0):
    """Rear-axle points of a U-turn from pass x_from (going +y) to pass x_to (going -y). Returns (points, pieces)
    with pieces = [(first index, kind, steer sign)] (kind: line / arc; sign -1 = right turn)."""
    s = 1.0 if x_to > x_from else -1.0
    c1 = (x_from + s * r, y_turn)
    c2 = (x_to - s * r, y_turn)
    a_in, a_top = (180.0, 90.0) if s > 0 else (0.0, 90.0)
    a_out = 0.0 if s > 0 else 180.0
    segs = [(_line((x_from, y_in), (x_from, y_turn), step), "line", 0.0),
            (_arc(c1, r, a_in, a_top, step), "arc", -s),
            (_line((c1[0], y_turn + r), (c2[0], y_turn + r), step), "line", 0.0),
            (_arc(c2, r, a_top, a_out, step), "arc", -s),
            (_line((x_to, y_turn), (x_to, y_out), step), "line", 0.0)]
    pts, pieces = [], []
    for seg, kind, sign in segs:
        if pts:
            seg = seg[1:]
        pieces.append((len(pts), kind, sign))
        pts.extend(seg)
    return pts, pieces


def poses(points):
    out = []
    for i, p in enumerate(points):
        q = points[min(i + 1, len(points) - 1)]
        o = points[max(i - 1, 0)]
        tx, ty = q[0] - o[0], q[1] - o[1]
        out.append((p[0], p[1], math.degrees(math.atan2(-tx, ty))))
    return out


def heading(psi):
    a = math.radians(psi)
    return -math.sin(a), math.cos(a)


def worker_poly(x, y, psi, outline=P.WORKER_OUTLINE):
    """Outline of the working robot (rectangle) for a rear-axle pose."""
    half, y0, y1 = outline
    hx, hy = heading(psi)
    rx, ry = hy, -hx
    cx, cy = x + P.robot_axle_y * hx, y + P.robot_axle_y * hy
    return [(cx + sx * half * rx + ly * hx, cy + sx * half * ry + ly * hy)
            for sx, ly in ((-1, y0), (1, y0), (1, y1), (-1, y1))]


def refiller_polys(xc, yc, rot=-90.0):
    """Outline rectangles of the refiller (robot, IBC + guides, left side) in the field; rot = heading of the
    refiller's +y (-90 = along +x)."""
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x0, x1, y0, y1 in P.REFILLER_OUTLINE:
        out.append([(xc + x * ca - y * sa, yc + x * sa + y * ca) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])
    return out


def _seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    l2 = ax * ax + ay * ay
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / l2))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def _separated(a, b):
    for poly in (a, b):
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            nx, ny = q[1] - p[1], p[0] - q[0]
            pa = [nx * v[0] + ny * v[1] for v in a]
            pb = [nx * v[0] + ny * v[1] for v in b]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return True
    return False


def poly_dist(a, b):
    """Distance between two convex polygons (0 when they overlap)."""
    if not _separated(a, b):
        return 0.0
    d = 1e18
    for poly, other in ((a, b), (b, a)):
        for p in poly:
            for i in range(len(other)):
                d = min(d, _seg_dist(p, other[i], other[(i + 1) % len(other)]))
    return d


def refill_spot(x_from, x_to):
    """Where the refiller stands (centre, heading +x) and where the working robot stops (rear axle) for a refill in
    the U-turn x_from -> x_to: nozzle above the middle of the straight, refiller inside the turn."""
    xm = 0.5 * (x_from + x_to)
    s = 1.0 if x_to > x_from else -1.0
    xc, yc = xm - P.mast_xy[1], YS - P.dock_d          # nozzle at refiller y = mast_y -> world x = xc + mast_y
    funnel = P.robot_axle_y + P.funnel_xy[1]            # funnel in front of the rear axle
    stop_x = xm - s * funnel
    return {"xc": xc, "yc": yc, "stop_x": stop_x, "straight": (xm - s * (0.5 * abs(x_to - x_from) - R_TURN),
                                                                xm + s * (0.5 * abs(x_to - x_from) - R_TURN))}


def loop_clearance(n=None, step=20.0):
    """Smallest gap (mm) between the working robot (with the applicator) and the refiller during a whole U-turn
    on the refiller headland, for a turn to the right and to the left; and the deepest point the working robot
    reaches on the headland (mm from the field edge)."""
    n = skip_n() if n is None else n
    out = {}
    for name, (a, b) in (("right", (0.0, n * WORK_WIDTH)), ("left", (n * WORK_WIDTH, 0.0))):
        spot = refill_spot(a, b)
        ref = refiller_polys(spot["xc"], spot["yc"])
        pts, _ = u_turn_points(a, b, step=step)
        best, where, ymax = 1e9, None, 0.0
        for x, y, psi in poses(pts):
            w = worker_poly(x, y, psi)
            ymax = max(ymax, max(p[1] for p in w))
            for r in ref:
                if abs(r[0][0] - x) > 6000.0:
                    continue
                d = poly_dist(w, r)
                if d < best:
                    best, where = d, (round(x), round(y), round(psi))
        out[name] = (best, where)
    out["depth"] = ymax
    return out


def straight_gap():
    """Gap between the refiller (widest point on the left) and the working robot on the straight."""
    left = -min(r[0] for r in P.REFILLER_OUTLINE)
    return P.dock_d - P.WORKER_OUTLINE[0] - left


# ---------------------------------------------------------------------
# Times
# ---------------------------------------------------------------------
def profile_time(dist, v, a):
    """Time for a move of dist (m) from standstill to standstill (trapezoid)."""
    if dist <= 0:
        return 0.0
    if dist <= v * v / a:
        return 2.0 * math.sqrt(dist / a)
    return dist / v + v / a


def u_turn_length(width_m, r=R_TURN):
    return (math.pi * r + max(0.0, width_m * 1000.0 - 2.0 * r)) / 1000.0


def u_turn_time(width_m, r=R_TURN):
    """Driving through a U-turn at V_HEAD (decelerate from and back to V_WORK not counted)."""
    return u_turn_length(width_m, r) / V_HEAD


def three_point_time(w=WORK_WIDTH, r=R_TURN, steer_stop=1.0):
    """Turn to the neighbouring pass with three points (as the liquid variant): arc, straight reverse, arc."""
    arc = math.pi / 2.0 * r / 1000.0
    rev = (2.0 * r - w) / 1000.0
    return 2.0 * profile_time(arc, V_HEAD, ACCEL) + profile_time(rev, V_REV, ACCEL) + 2.0 * steer_stop


def pump_q_ls():
    """Flow used in the animation and the tables (l/s): operating point, limited to pump_q_fill."""
    return min(operating_point()["q_lpm"], P.pump_q_fill) / 60.0


def per_round_l(dose, field_len_m, work_width=WORK_WIDTH):
    """Liquid used between two visits on the refiller headland: 2 passes (there and back)."""
    return dose * 1e-4 * (work_width / 1000.0) * 2.0 * field_len_m


def refill_standstill(litres):
    """Standstill of the working robot per refill (s): stop and start (V_HEAD / ACCEL lost), check, pump, close."""
    return V_HEAD / ACCEL + T_CHECK + litres / pump_q_ls() + T_CLOSE


def round_trip_time(field_len_m, n=None):
    """Two passes plus the two U-turns (refiller headland N W, far headland (N - 1) W), without refill (s)."""
    n = skip_n() if n is None else n
    return 2.0 * field_len_m / V_WORK + u_turn_time(n * WORK_WIDTH / 1000.0) + u_turn_time((n - 1) * WORK_WIDTH / 1000.0)


def turn_table(doses=(100.0, 250.0, 505.0, 1000.0, 2000.0), lengths=(100.0, 200.0, 400.0)):
    """Standstill per refill (s) and as a share of the round trip (%), for each dose and field length."""
    rows = []
    for dose in doses:
        row = []
        for length in lengths:
            need = per_round_l(dose, length)
            if need > capacity_l("receiver"):
                row.append((need, None, None))
                continue
            t = refill_standstill(need)
            row.append((need, t, 100.0 * t / (round_trip_time(length) + t)))
        rows.append((dose, row))
    return rows


def headland_depth():
    """Headland depth (m) from the field edge: U-turns with the refiller inside (the refiller adds nothing) and the
    turn with three points beside the refiller of the liquid variant (6.4 m)."""
    return loop_clearance()["depth"] / 1000.0 + 0.3


# ---------------------------------------------------------------------
# Masses, wheel loads, stability
# ---------------------------------------------------------------------
def items(fill=1.0, rho=None):
    rho = P.liquid_density if rho is None else rho
    litres = fill * P.ibc_nominal_l
    m_l = litres * rho
    return [DRY["robot"], DRY["kit"], DRY["ibc"], (m_l, (0.0, P.IBC_CY, liquid_cg_z("ibc", litres)))]


def cg(fill=1.0, rho=None):
    it = items(fill, rho)
    m = sum(i[0] for i in it)
    return m, tuple(sum(i[0] * i[1][k] for i in it) / m for k in range(3))


def loads(fill=1.0, rho=None):
    """Wheel loads (kg) with the IBC filled to 'fill' x 1000 l. Axles at y = +-500."""
    m, (x, y, z) = cg(fill, rho)
    front = m * (y + P.robot_axle_y) / P.robot_wheelbase
    rear = m - front
    left = (P.robot_wheel_x - x) / (2.0 * P.robot_wheel_x)
    return {"total": m, "front_wheel": front / 2.0, "rear_wheel": rear / 2.0, "left_share": left, "cg": (x, y, z),
            "max_wheel": max(front, rear) * max(left, 1.0 - left)}


def max_fill_for_wheels(rho=None):
    lo, hi = 0.0, 1.06
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if loads(mid, rho)["max_wheel"] <= P.wheel_load_max:
            lo = mid
        else:
            hi = mid
    return lo


def tip_angles(fill=1.0, rho=None):
    """Static tipping angles (deg): sideways (to the heavier side) and over the rear / front axle."""
    m, (x, y, z) = cg(fill, rho)
    side = math.degrees(math.atan2(P.robot_wheel_x - abs(x), z))
    rear = math.degrees(math.atan2(P.robot_axle_y + y, z))
    front = math.degrees(math.atan2(P.robot_axle_y - y, z))
    return {"side": side, "rear": rear, "front": front, "cg_z": z}


# ---------------------------------------------------------------------
# Traction: per driven wheel min(mu x load, motor), minus rolling and grade resistance
# ---------------------------------------------------------------------
def traction(fill=1.0, surface="grass", mu=None, grade=0.0, peak=False):
    mu = P.mu["wet"] if mu is None else mu
    L = loads(fill)
    motor = P.motor_peak_kgf if peak else P.motor_cont_kgf
    wheels = [L["front_wheel"]] * 2 + [L["rear_wheel"]] * 2
    drive = sum(min(mu * w, motor) for w in wheels)
    resist = L["total"] * (P.c_rr[surface] + grade)
    return {"drive_kgf": drive, "resist_kgf": resist, "ok": drive >= resist}


def max_grade(fill=1.0, surface="grass", mu=None, peak=False):
    if not traction(fill, surface, mu, 0.0, peak)["ok"]:
        return None
    lo, hi = 0.0, 0.5
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if traction(fill, surface, mu, mid, peak)["ok"]:
            lo = mid
        else:
            hi = mid
    return lo


def max_fill_continuous(surface="grass", mu=None):
    lo, hi = 0.0, 1.06
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if traction(mid, surface, mu)["ok"]:
            lo = mid
        else:
            hi = mid
    return lo


# ---------------------------------------------------------------------
# Pump and hose (same pump curve as the liquid variant)
# ---------------------------------------------------------------------
HOSE_LEN = {"suction": 1.0, "discharge": 0.9 + 1.3 + 0.9 + 0.7}   # m: under the beams, mast, arm, drop pipe
K_MINOR = 7.0                    # IBC valve, camlock, bends, drip-stop nozzle (estimated)
PUMP_H0 = 18.0                   # m shut-off head
PUMP_Q0 = 190.0                  # l/min free flow (estimated curve H = H0 (1 - (Q/Q0)^2))
ARM_HOSE_Z = 0.5 * (P.arm_z[0] + P.arm_z[1])


def static_lift():
    """From the lowest level in the IBC to the hose on the arm (m): what the pump must lift to get the flow going.
    Once the hose is full it works partly as a siphon (nozzle at 1.25 m)."""
    return (ARM_HOSE_Z - tank_sections("ibc")[0][0]) / 1000.0


def system_head(q_lpm):
    q = q_lpm / 60000.0
    d = P.hose_d / 1000.0
    v = q / (math.pi * d * d / 4.0)
    if v <= 0:
        return static_lift()
    re = v * d / P.liquid_viscosity
    f = 64.0 / re if re < 2300 else 0.316 * re ** -0.25
    hv = v * v / (2.0 * G_ACC)
    return static_lift() + (f * sum(HOSE_LEN.values()) / d + K_MINOR + 1.0) * hv


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
    return {"q_lpm": q, "head_m": h, "p_hyd_w": p_hyd, "p_el_w": p_hyd / P.pump_eff}


def power_at_fill():
    """Electric power at the throttled flow pump_q_fill (W), speed-controlled pump (estimated: hydraulic power at
    the system curve / efficiency)."""
    q = P.pump_q_fill
    return P.liquid_density * 1000.0 * G_ACC * (q / 60000.0) * system_head(q) / P.pump_eff


# ---------------------------------------------------------------------
# Nozzle position: antenna straight above the nozzle; the working robot stops its funnel under it
# ---------------------------------------------------------------------
def nozzle_tolerance():
    """Allowed offset (mm) of the stream from the funnel axis and the error budget (2 sigma)."""
    stream = 25.0
    tol = P.funnel_d[0] / 2.0 - stream / 2.0 - 10.0           # 10 mm for wind drift over the 0.1 m fall
    budget = {"antenna above the nozzle (RTK)": 20.0, "tilt of the mast x 0.85 m (IMU corrected)": 15.0,
              "working robot: GNSS + heading x funnel offset": 25.0, "working robot: stopping position": 30.0}
    return {"tolerance": tol, "budget": budget, "rss": math.sqrt(sum(v * v for v in budget.values()))}


# ---------------------------------------------------------------------
# Bed and mast (steel S235)
# ---------------------------------------------------------------------
def _w_rect_tube(b, h, t):
    """Section modulus (mm3) of a rectangular tube for bending about the axis parallel to b."""
    i = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12.0
    return i / (h / 2.0), i


def bed_check(dyn=2.0, fill=1.0):
    """Cross tube cantilever from the outer upper beam to the side rail, side rail span between the cross tubes,
    bolts (shear from braking / sloshing 0.5 g), straps."""
    m = sum(P.ibc_kg.values()) + fill * P.ibc_nominal_l * P.liquid_density
    w_bed, _ = _w_rect_tube(P.bed_tube[0], P.bed_tube[1], P.bed_tube[2])
    per_side = dyn * m * G_ACC / 2.0                       # pallet edges on the side rails
    n_cross = len(P.bed_cross_y) + 1
    lever = 0.5 * sum(P.bed_side_x) - (P.robot_upper_beam_x[3] + P.robot_beam / 2.0)
    m_cross = per_side / n_cross * lever
    spans = sorted(list(P.bed_cross_y) + [P.bed_mast_y, P.bed_y[0], P.bed_y[1]])
    span = max(b - a for a, b in zip(spans[:-1], spans[1:]))
    q = per_side / (P.bed_y[1] - P.bed_y[0])
    m_rail = q * span ** 2 / 8.0
    shear = m * G_ACC * 0.5 / (len(P.bed_cross_y) * len(P.bed_bolt_x))
    return {"cross_mpa": m_cross / w_bed, "rail_mpa": m_rail / w_bed, "bolt_shear_n": shear,
            "lever_mm": lever, "span_mm": span}


def mast_check(dyn=2.0):
    """Moment at the mast foot (Nm), stress in the mast and the arm, tip deflection (mm)."""
    arm_len = abs(P.NOZZLE_XY[0] - P.mast_xy[0]) + P.arm_tip
    b, t = P.arm_tube
    arm_kg = 7.85e-6 * (b * b - (b - 2 * t) ** 2) * arm_len
    tip_kg = 0.6 + 1.4 * P.liquid_density + 0.5 + 1.2      # drop pipe, liquid in it, antenna, nozzle + hose end
    hose_kg = (0.6 + 1.13 * P.liquid_density) * arm_len / 1000.0
    moment = G_ACC * ((arm_kg + hose_kg) * arm_len / 2000.0 + tip_kg * (arm_len - P.arm_tip) / 1000.0)
    w_mast, i_mast = _w_rect_tube(P.mast_tube[0], P.mast_tube[0], P.mast_tube[1])
    w_arm, i_arm = _w_rect_tube(b, b, t)
    h = (P.mast_z[1] - P.mast_z[0]) / 1000.0
    e = 210e9
    rot = moment * h / (e * i_mast * 1e-12)
    l = (arm_len - P.arm_tip) / 1000.0
    defl = rot * l + tip_kg * G_ACC * l ** 3 / (3 * e * i_arm * 1e-12) + (arm_kg + hose_kg) * G_ACC / l * l ** 4 / (
        8 * e * i_arm * 1e-12)
    return {"moment_nm": moment, "mast_mpa": dyn * moment * 1000.0 / w_mast, "arm_mpa": dyn * moment * 1000.0 / w_arm,
            "tip_defl_mm": defl * 1000.0, "arm_len_mm": arm_len}


# ---------------------------------------------------------------------
# Logistics and energy
# ---------------------------------------------------------------------
def worker_rate_ha_h(v=V_WORK, eff=0.8):
    return v * 3.6 * WORK_WIDTH / 1000.0 / 10.0 * eff


def logistics(dose=DOSE_STD, dist_m=500.0, swap_min=5.0):
    """One IBC per load. The refiller drives full at v_full, empty at v_empty to the yard where a telehandler or
    forklift swaps the IBC."""
    cap = P.ibc_nominal_l
    rate = worker_rate_ha_h()
    ha = cap / dose
    trip = (dist_m / P.v_full + dist_m / P.v_empty) / 60.0 + swap_min
    work_tank = capacity_l("receiver")
    h_tank = work_tank / dose / rate
    self_trip = (2.0 * dist_m / P.v_empty) / 60.0 + work_tank / 200.0 + 3.0
    return {"ha_per_ibc": ha, "h_per_ibc": ha / rate, "trip_min": trip, "buffer_min": h_tank * 60.0,
            "eff_without": h_tank * 60.0 / (h_tank * 60.0 + self_trip), "rate_ha_h": rate}


def energy(dist_m=500.0, eff_drive=0.6):
    """Wh per IBC: pumping 1000 l, driving to the yard and back (track), and the 1 m moves on the headland."""
    q = P.pump_q_fill
    pump = power_at_fill() * P.ibc_nominal_l / q / 60.0
    full, empty = loads(1.0)["total"], loads(0.0)["total"]
    drive = G_ACC * P.c_rr["track"] * (full + empty) * dist_m / eff_drive / 3600.0
    moves = G_ACC * P.c_rr["grass"] * 0.5 * (full + empty) * 1.0 * (P.ibc_nominal_l / 20.0) / eff_drive / 3600.0
    return {"pump_wh": pump, "drive_wh": drive, "moves_wh": moves,
            "ibc_per_battery": P.battery_kwh * 1000.0 * 0.8 / (pump + drive + moves + 40.0)}


# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------
def nl(v, d=0):
    return ("%%.%df" % d) % v


def report():
    out = []
    add = out.append
    n = skip_n()
    add("== Capacity ==")
    add("IBC %s l nominal, bottle %s l to the brim (model); work tank on the working robot %s l" % (
        nl(P.ibc_nominal_l), nl(capacity_l("ibc")), nl(capacity_l("receiver"))))
    add("== Skip pattern (U-turns only) ==")
    order = field_order(2)
    tt = turns(order)
    add("N = %d: order %s ..." % (n, ", ".join(str(p) for p in order[:14])))
    widths = {}
    for a, b, head, w, _ in tt:
        widths.setdefault(head, set()).add(w)
    add("turns on the refiller headland %s m, on the far headland %s m (R %s m, R_min %s m)" % (
        " / ".join(nl(w) for w in sorted(widths["R"])), " / ".join(nl(w) for w in sorted(widths["F"])),
        nl(R_TURN / 1000.0, 1), nl(R_MIN / 1000.0, 1)))
    mv = refiller_moves(order)
    add("refiller moves between refills: %s m (block change every %d refills: %s m)" % (
        nl(min(mv)), n, nl(max(mv))))
    add("U-turn %d m: %s m path, %s s at %s m/s; straight part %s m. Turn with three points to the neighbouring pass "
        "(liquid variant): %s s" % (n, nl(u_turn_length(n), 1), nl(u_turn_time(n), 1), nl(V_HEAD, 1),
                                     nl(n - 2.0 * R_TURN / 1000.0, 1), nl(three_point_time(), 1)))
    lc = loop_clearance()
    add("refiller inside the turn: smallest gap to the working robot %s mm (turn right) / %s mm (turn left); "
        "on the straight %s mm" % (nl(lc["right"][0]), nl(lc["left"][0]), nl(straight_gap())))
    add("headland depth %s m (deepest point of the working robot %s m + 0.3 m): the refiller adds nothing "
        "(liquid variant: 6.4 m)" % (nl(headland_depth(), 1), nl(lc["depth"] / 1000.0, 2)))
    add("== Refill (working robot stands still on the straight) ==")
    add("flow %s l/min; standstill = stop/start %s s + check %s s + pump + close %s s" % (
        nl(60.0 * pump_q_ls()), nl(V_HEAD / ACCEL, 1), nl(T_CHECK, 1), nl(T_CLOSE, 1)))
    add("standstill per refill (s and % of the round trip), field length 100 / 200 / 400 m:")
    for dose, row in turn_table():
        add("  %5d l/ha: %s" % (dose, ", ".join(
            ("%s l -> %s s (%s %%)" % (nl(need, 1), nl(t, 0), nl(pct, 1))) if t is not None else
            "%s l: more than the work tank" % nl(need) for need, t, pct in row)))
    add("== Masses and wheel loads (kg, liquid %s kg/l) ==" % nl(P.liquid_density, 2))
    for fill in (0.0, 0.5, 1.0):
        L = loads(fill)
        add("IBC %4d l: total %s; per wheel front %s, rear %s, heaviest (left rear, mast side) %s (limit %d)" % (
            fill * P.ibc_nominal_l, nl(L["total"]), nl(L["front_wheel"]), nl(L["rear_wheel"]), nl(L["max_wheel"]),
            P.wheel_load_max))
    for rho in (1.0, 1.32):
        L = loads(1.0, rho)
        add("full with %s kg/l: rear wheels %s kg, heaviest %s kg; IBC allowed up to %s l" % (
            nl(rho, 2), nl(L["rear_wheel"]), nl(L["max_wheel"]),
            nl(min(1.0, max_fill_for_wheels(rho)) * P.ibc_nominal_l)))
    add("== Stability (static tipping angle) ==")
    for fill in (0.0, 0.5, 1.0):
        ta = tip_angles(fill)
        add("IBC %4d l: cg %s mm high; sideways %s deg, backwards %s deg, forwards %s deg" % (
            fill * P.ibc_nominal_l, nl(ta["cg_z"]), nl(ta["side"], 1), nl(ta["rear"], 1), nl(ta["front"], 1)))
    add("== Traction (4 hub motors, %s kgf continuous / %s kgf peak each) ==" % (nl(P.motor_cont_kgf),
                                                                              nl(P.motor_peak_kgf)))
    for fill in (0.0, 0.5, 1.0):
        parts = []
        for surface in ("grass", "track"):
            t = traction(fill, surface)
            g = max_grade(fill, surface)
            gp = max_grade(fill, surface, peak=True)
            parts.append("%s: %s vs %s kgf, max grade %s %% (peak %s %%)" % (
                surface, nl(t["drive_kgf"]), nl(t["resist_kgf"]), "-" if g is None else nl(100 * g, 1),
                "-" if gp is None else nl(100 * gp, 1)))
        add("IBC %4d l: %s" % (fill * P.ibc_nominal_l, "; ".join(parts)))
    add("continuous on wet grass up to %s l in the IBC; full IBC on grass only in short moves (peak torque)" % (
        nl(max_fill_continuous() * P.ibc_nominal_l)))
    add("== Pump and hose ==")
    op = operating_point()
    add("lift to the arm %s m, free operating point %s l/min at %s m; throttled to %s l/min: %s W electric" % (
        nl(static_lift(), 2), nl(op["q_lpm"]), nl(op["head_m"], 1), nl(P.pump_q_fill), nl(power_at_fill())))
    nt = nozzle_tolerance()
    add("nozzle: stream may be %s mm off the funnel axis; error 2 sigma %s mm (no camera)" % (
        nl(nt["tolerance"]), nl(nt["rss"])))
    add("== Bed and mast ==")
    bc = bed_check()
    add("bed (x2 dynamic): cross tube %s MPa (lever %s mm), side rail %s MPa (span %s mm); bolt shear %s N per M10" % (
        nl(bc["cross_mpa"]), nl(bc["lever_mm"]), nl(bc["rail_mpa"]), nl(bc["span_mm"]), nl(bc["bolt_shear_n"])))
    mc = mast_check()
    add("mast: %s Nm at the foot (static), mast %s MPa, arm %s MPa (x2 dynamic), tip deflection %s mm" % (
        nl(mc["moment_nm"]), nl(mc["mast_mpa"], 1), nl(mc["arm_mpa"], 1), nl(mc["tip_defl_mm"], 2)))
    add("== Logistics (505 l/ha) ==")
    for d in (200.0, 500.0, 1000.0, 2000.0):
        lg = logistics(dist_m=d)
        add("yard %4d m: one IBC = %s ha = %s h of work; IBC swap trip %s min (work tank buffer %s min); "
            "without refiller %s %%" % (d, nl(lg["ha_per_ibc"], 2), nl(lg["h_per_ibc"], 1), nl(lg["trip_min"]),
                                        nl(lg["buffer_min"]), nl(100 * lg["eff_without"])))
    e = energy()
    add("energy per IBC: pump %s Wh, trip 2 x 500 m %s Wh, moves on the headland %s Wh; about %s IBCs per battery" % (
        nl(e["pump_wh"]), nl(e["drive_wh"]), nl(e["moves_wh"]), nl(e["ibc_per_battery"], 1)))
    return "\n".join(out)


if __name__ == "__main__":
    print(report())
