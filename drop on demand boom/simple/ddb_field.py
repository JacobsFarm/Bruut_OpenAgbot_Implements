"""Process model of the drop-on-demand boom (pure Python): a bed with 2 rows of young lettuce and weed seedlings, the
drive, detection in the hood camera, which injector fires when, the drops on the weeds and the liquid used.

The robot drives straight along +y at x = 0 over the bed. World coordinates; the robot centre is at (0, Y).
Used by animate_ddb.py and make_gif_ddb.py; timing and drop figures from ddb_calc.
"""
import math
import random

import ddb_params as P
import ddb_calc as C

SEED = 11
Y_START = -1200.0               # robot centre at t = 0
Y_END = 5200.0
ACC = 0.4                       # m/s2 at the start and the end
V = P.speed
HOLD_END = 1.5
BED_Y = (Y_START - 900.0, Y_END + 900.0)
WEED_Y = (300.0, 4600.0)        # weeds only in this part of the bed (the camera is past the start)
WEED_DENSITY = 12.0             # per m2 in the animation (fewer than in the calc, to keep it readable)
CROP_D = 120.0                  # young lettuce, 3 weeks after planting


def crops():
    """(x, y, d, seed) of the lettuce plants."""
    out = []
    for i, x in enumerate(P.crop_rows):
        y = BED_Y[0] + 150.0 + 0.5 * P.crop_spacing * i
        while y < BED_Y[1] - 150.0:
            out.append((x, y, CROP_D, int(y) * 3 + i))
            y += P.crop_spacing
    return out


def weeds():
    """(x, y, d, seed): seedlings spread over the bed; none on top of a crop plant."""
    rnd = random.Random(SEED)
    area = P.work_width / 1000.0 * (WEED_Y[1] - WEED_Y[0]) / 1000.0
    n = int(round(WEED_DENSITY * area))
    cr = crops()
    out = []
    while len(out) < n:
        x = rnd.uniform(-P.work_width / 2.0 + 20.0, P.work_width / 2.0 - 20.0)
        y = rnd.uniform(*WEED_Y)
        d = rnd.uniform(*P.weed_d)
        if any(math.hypot(x - c[0], y - c[1]) < (d + c[2]) / 2.0 for c in cr):
            continue
        out.append((x, y, d, rnd.randint(0, 9999)))
    return sorted(out, key=lambda w: w[1])


# ---------------------------------------------------------------------
# Drive: accelerate, constant speed, brake. Y(t) in mm.
# ---------------------------------------------------------------------
def _profile():
    v = V * 1000.0
    a = ACC * 1000.0
    ta = v / a
    da = 0.5 * a * ta * ta
    tc = (Y_END - Y_START - 2 * da) / v
    return v, a, ta, tc


def drive_time():
    v, a, ta, tc = _profile()
    return 2 * ta + tc


def robot_y(t):
    v, a, ta, tc = _profile()
    if t <= 0:
        return Y_START
    if t <= ta:
        return Y_START + 0.5 * a * t * t
    if t <= ta + tc:
        return Y_START + 0.5 * a * ta * ta + v * (t - ta)
    t3 = min(t - ta - tc, ta)
    return Y_START + 0.5 * a * ta * ta + v * tc + v * t3 - 0.5 * a * t3 * t3


def robot_v(t):
    v, a, ta, tc = _profile()
    if t <= 0 or t >= 2 * ta + tc:
        return 0.0
    if t <= ta:
        return a * t
    if t <= ta + tc:
        return v
    return v - a * (t - ta - tc)


def time_at(y):
    lo, hi = 0.0, drive_time()
    if y <= Y_START:
        return 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if robot_y(mid) < y:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------
# Detection and drops
# ---------------------------------------------------------------------
VIEW = C.camera()["view_in_hood_y"]
FALL = C.drop_flight()["fall_ms"] / 1000.0


def detect_time(w):
    """The weed enters the image at the front of the hood; 2 frames + inference later it is confirmed."""
    lat = C.latency()["t_need_s"]
    return time_at(w[1] - VIEW[1]) + lat


def plan():
    """Per weed: the drops (x of the injector, y on the ground, release time) on a grid of inj_pitch x drop_grid in the
    leaf circle; drops closer to a crop plant than its radius + crop_protect are left out."""
    cr = crops()
    out = []
    for w in weeds():
        x, y, d = w[0], w[1], w[2]
        r = d / 2.0
        inj = [i for i, xi in enumerate(P.inj_x) if abs(xi - x) <= max(r, P.inj_pitch / 2.0)]
        n_y = max(1, int(round(d / P.drop_grid)))
        ys = [y + (k - 0.5 * (n_y - 1)) * P.drop_grid for k in range(n_y)]
        drops, skipped = [], 0
        for i in inj:
            for yy in ys:
                if n_y > 1 and len(inj) > 1 and math.hypot(P.inj_x[i] - x, yy - y) > r + 2.0:
                    continue
                if any(math.hypot(P.inj_x[i] - c[0], yy - c[1]) < c[2] / 2.0 + P.crop_protect for c in cr):
                    skipped += 1
                    continue
                t = time_at(yy - P.inj_y) - FALL         # released early: the drop keeps the forward speed
                drops.append({"i": i, "x": P.inj_x[i], "y": yy, "t": t})
        out.append({"weed": w, "detect": detect_time(w), "drops": drops, "skipped": skipped})
    return out


def frame_state(t, plan_=None, dt=1.0 / 6.0):
    """State at t: robot, which injectors fired in (t - dt, t], drops in flight, wet dots, weed states, liquid."""
    plan_ = plan_ or plan()
    y_r = robot_y(t)
    fired = [0] * P.n_inj
    jets, dots, weed_state = [], [], []
    n_drops = 0
    for p in plan_:
        hit = 0
        for dr in p["drops"]:
            if dr["t"] <= t:
                n_drops += 1
                hit += 1
                if dr["t"] + FALL <= t:
                    dots.append((dr["x"], dr["y"]))
                if dr["t"] > t - dt:
                    fired[dr["i"]] = 1
                    jets.append((dr["x"], dr["y"]))
        weed_state.append({"detected": t >= p["detect"], "treated": hit > 0 and hit == len(p["drops"]),
                           "partly": 0 < hit, "protected": p["skipped"] > 0 and not p["drops"]})
    driven = max(0.0, y_r - Y_START) / 1000.0
    blanket = driven * P.work_width / 1000.0 / 1e4 * P.blanket_rate
    return {"t": t, "y": y_r, "v": robot_v(t), "fired": fired, "jets": jets, "dots": dots, "weeds": weed_state,
            "ml": n_drops * P.drop_ul / 1000.0, "drops": n_drops, "blanket_l": blanket, "driven_m": driven}


def summary():
    pl = plan()
    end = frame_state(drive_time(), pl)
    lead = min(p["drops"][0]["t"] - p["detect"] for p in pl if p["drops"]) if pl else 0.0
    return {"weeds": len(pl), "crops": len(crops()), "drops": sum(len(p["drops"]) for p in pl),
            "skipped_near_crop": sum(p["skipped"] for p in pl),
            "untreated_near_crop": sum(1 for p in pl if not p["drops"]),
            "ml": round(end["ml"], 2), "blanket_l": round(end["blanket_l"], 3),
            "saving": round(1.0 - end["ml"] / 1000.0 / end["blanket_l"], 4), "lead_s_min": round(lead, 2),
            "duration_s": round(drive_time(), 1)}


if __name__ == "__main__":
    print(summary())
