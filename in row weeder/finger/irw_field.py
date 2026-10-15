"""Process model for the animation and the field figures (pure Python): two broccoli rows with weed seedlings, the
robot driving at constant speed, the camera that sees each plant, the swing schedule of both fingers and the soil that
the knives work (killing the seedlings they pass).

Each finger: in the row line between the plants; it starts the swing out so that it is fully out when its front edge
is safe_r + margin before the stem, and starts back in when its rear edge is safe_r + margin past it. When the next
plant comes before the finger is back, it stays out.

    import irw_field as F
    s = F.simulate(); F.summary()
"""
import math
import random

import irw_params as P
import irw_calc as C

Y_START = 0.0                   # robot centre at t = 0
DRIVE = 4500.0                  # mm driven
HOLD_END = 1.0                  # s standing still at the end
DT = 0.01                       # s, sub-step of the simulation
SEED = 21
ROWS = ("left", "right")


def row_x(row):
    return P.row_x[0] if row == "left" else P.row_x[1]


def drive_time(v=P.speed):
    return DRIVE / (v * 1000.0)


def robot_y(t, v=P.speed):
    return Y_START + v * 1000.0 * min(t, drive_time(v))


# ---------------------------------------------------------------------
# Field
# ---------------------------------------------------------------------
_FIELD = {}


def field(seed=SEED):
    if seed in _FIELD:
        return _FIELD[seed]
    rnd = random.Random(seed)
    plants = []
    y_first = Y_START + 450.0
    y_last = Y_START + DRIVE + 800.0
    for row in ROWS:
        y = y_first + rnd.uniform(0.0, P.plant_spacing)
        k = 0
        while y < y_last:
            missing = (row == "left" and k == 5)          # one plant missing (transplanter gap)
            if not missing:
                plants.append({"row": row, "x": row_x(row) + rnd.uniform(-P.plant_offset, P.plant_offset),
                               "y": y + rnd.uniform(-P.plant_scatter, P.plant_scatter),
                               "d": rnd.uniform(*P.canopy_d), "h": rnd.uniform(190.0, 260.0), "seed": rnd.randint(0, 999)})
            y += P.plant_spacing
            k += 1
    weeds = []
    for row in ROWS:
        x0 = row_x(row)
        for _ in range(int(DRIVE / 1000.0 * 26)):              # in the row band: ~26 per m per row
            weeds.append({"x": x0 + rnd.gauss(0.0, 28.0), "y": rnd.uniform(y_first - 300.0, y_last),
                          "s": rnd.uniform(0.6, 1.2)})
    for _ in range(int(DRIVE / 1000.0 * 20)):                  # elsewhere (inter-row is hoed by another pass)
        weeds.append({"x": rnd.uniform(-700.0, 700.0), "y": rnd.uniform(y_first - 300.0, y_last),
                      "s": rnd.uniform(0.6, 1.2)})
    # no weed right in a crop plant
    weeds = [w for w in weeds if all(math.hypot(w["x"] - p["x"], w["y"] - p["y"]) > 25.0 for p in plants)]
    _FIELD[seed] = {"plants": plants, "weeds": weeds}
    return _FIELD[seed]


# ---------------------------------------------------------------------
# Swing schedule
# ---------------------------------------------------------------------
def schedule(row, v=P.speed):
    """List of (t_start, kind) swings of the finger in this row."""
    pz = C.plant_zone(v)
    m = C.moves()
    vm = v * 1000.0
    y_in = C.finger_uv(P.theta_in)[1]
    y_out = C.finger_uv(P.theta_out)[1]
    ys = sorted(p["y"] for p in field()["plants"] if p["row"] == row)
    events = []
    out_until = -1e9
    for yp in ys:
        t_out = (yp + pz["out_start"] - y_in - Y_START) / vm          # knife centre (in) at out_start before the stem
        t_in = (yp + pz["in_start"] - y_out - Y_START) / vm           # knife centre (out) at in_start after the stem
        if events and t_out < out_until + m["in"]["t"]:
            # next plant too close: stay out, drop the previous swing in
            events.pop()
        else:
            events.append((t_out, "out"))
        events.append((t_in, "in"))
        out_until = t_in
    return [e for e in events if e[0] < drive_time(v) + 1.0]


_SCHED = {}


def theta(row, t, v=P.speed):
    key = (row, v)
    if key not in _SCHED:
        _SCHED[key] = schedule(row, v)
    ev = _SCHED[key]
    if t > drive_time(v):
        t = drive_time(v)
    last = None
    for e in ev:
        if e[0] <= t:
            last = e
        else:
            break
    if last is None:
        return P.theta_in
    return C.theta_during(last[1], t - last[0])


def knife(row, t, v=P.speed):
    """Knife outline (x, y) in the field at time t."""
    yr = robot_y(t, v)
    return [(x, y + yr) for (x, y) in C.knife_corners(theta(row, t, v), row)]


# ---------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------
def _inside(pt, poly):
    """Point in convex polygon (counter-clockwise)."""
    x, y = pt
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0) < -1e-9:
            return False
    return True


def _hull(points):
    pts = sorted(set((round(p[0], 3), round(p[1], 3)) for p in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _dist_rect(pt, poly):
    """Distance from a point to a convex polygon (0 inside)."""
    if _inside(pt, poly):
        return 0.0
    best = 1e9
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        u = max(0.0, min(1.0, ((pt[0] - ax) * dx + (pt[1] - ay) * dy) / L2)) if L2 > 0 else 0.0
        best = min(best, math.hypot(pt[0] - ax - u * dx, pt[1] - ay - u * dy))
    return best


_SIM = {}


def simulate(v=P.speed):
    """Swept polygons per sub-step, weeds killed (time), closest knife approach to each stem."""
    if v in _SIM:
        return _SIM[v]
    fld = field()
    t_end = drive_time(v)
    n = int(t_end / DT)
    strips = {r: [] for r in ROWS}
    killed = {}
    closest = {}
    prev = {r: knife(r, 0.0, v) for r in ROWS}
    near = {r: [i for i, w in enumerate(fld["weeds"]) if abs(w["x"] - row_x(r)) < 160.0] for r in ROWS}
    stems = {r: [(i, p) for i, p in enumerate(fld["plants"]) if p["row"] == r] for r in ROWS}
    for k in range(1, n + 1):
        t = k * DT
        for r in ROWS:
            cur = knife(r, t, v)
            hull = _hull(prev[r] + cur)
            strips[r].append((t, hull))
            ys = [p[1] for p in hull]
            y0, y1 = min(ys), max(ys)
            for i in near[r]:
                w = fld["weeds"][i]
                if i not in killed and y0 <= w["y"] <= y1 and _inside((w["x"], w["y"]), hull):
                    killed[i] = t
            for i, p in stems[r]:
                if y0 - 200.0 <= p["y"] <= y1 + 200.0:
                    d = _dist_rect((p["x"], p["y"]), cur)
                    if d < closest.get(i, 1e9):
                        closest[i] = d
            prev[r] = cur
    _SIM[v] = {"strips": strips, "killed": killed, "closest": closest, "t_end": t_end}
    return _SIM[v]


def coverage(v=P.speed, step=5.0):
    """Share of the in-row band (row line +- knife_w / 2) that a knife passed over, over the stretch where the knives
    worked; and the same share outside the safe circles around the stems (what can be hoed)."""
    sim = simulate(v)
    fld = field()
    out = {}
    y_from = Y_START + C.finger_uv(P.theta_in)[1] + 100.0
    y_to = robot_y(sim["t_end"], v) + C.finger_uv(P.theta_in)[1] - 100.0
    for r in ROWS:
        x0 = row_x(r)
        polys = sim["strips"][r]
        stems = [p for p in fld["plants"] if p["row"] == r]
        tot = cov = tot_s = cov_s = 0
        y = y_from
        while y < y_to:
            cand = [h for (_, h) in polys if min(p[1] for p in h) - 1 <= y <= max(p[1] for p in h) + 1]
            for xi in range(int(P.knife_w / step) + 1):
                x = x0 - P.knife_w / 2.0 + xi * step
                hit = any(_inside((x, y), h) for h in cand)
                tot += 1
                cov += hit
                if all(math.hypot(x - p["x"], y - p["y"]) > P.safe_r for p in stems):
                    tot_s += 1
                    cov_s += hit
            y += step
        out[r] = {"band": cov / float(tot), "outside_safe": cov_s / float(tot_s)}
    return out


def summary(v=P.speed):
    sim = simulate(v)
    fld = field()
    in_band = [i for i, w in enumerate(fld["weeds"]) if min(abs(w["x"] - x) for x in P.row_x) <= P.knife_w / 2.0
               and Y_START + C.finger_uv(P.theta_in)[1] < w["y"] < robot_y(sim["t_end"], v) + C.finger_uv(P.theta_in)[1]]
    killed_band = [i for i in in_band if i in sim["killed"]]
    cov = coverage(v)
    swings = {r: len(schedule(r, v)) for r in ROWS}
    return {"plants_passed": len(sim["closest"]), "closest_mm": round(min(sim["closest"].values()), 1),
            "weeds_in_band": len(in_band), "killed_in_band": len(killed_band),
            "kill_share": round(len(killed_band) / float(max(1, len(in_band))), 3),
            "band_cover": {r: round(cov[r]["band"], 3) for r in ROWS},
            "cover_outside_safe": {r: round(cov[r]["outside_safe"], 3) for r in ROWS},
            "swings": swings, "drive_s": round(sim["t_end"], 2)}
