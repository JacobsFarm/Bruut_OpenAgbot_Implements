"""Process model of the spot sprayer (pure Python): weeds in the field, the post that the right wing folds for, the
drive, detection by the camera, which nozzle is open when, the sprayed spots and the liquid used.

The robot drives straight along +y at x = 0. Everything in world coordinates; the robot reference point (its centre)
is at (0, Y). Used by animate_ssp.py and make_gif_ssp.py; timing and rates from ssp_calc.
"""
import math
import random

import ssp_params as P
import ssp_calc as C

SEED = 7
POST = (1330.0, 9600.0, 150.0, 1500.0)      # x, y, diameter, height: a fence post in the strip of the right wing
POST_CLEAR = 100.0                          # wing (incl. guard) must be clear of the post by this much
Y_START = -1500.0                           # robot centre at t = 0
Y_END = 14500.0
ACC = 0.5                                   # m/s2 at the start and the end
V = P.speed
HOLD_END = 2.0


def weeds():
    """(x, y, d, h, seed): broad-leaved dock rosettes, scattered, a few in patches; one near the post (missed)."""
    rnd = random.Random(SEED)
    out = []
    y = 3200.0
    while y < 12800.0:
        x = rnd.uniform(-1800.0, 1800.0)
        d = rnd.uniform(220.0, 460.0)
        out.append((x, y, d, d * rnd.uniform(0.6, 0.9), rnd.randint(0, 9999)))
        if rnd.random() < 0.3:            # a second plant close by (docks come in patches)
            out.append((x + rnd.uniform(-350.0, 350.0), y + rnd.uniform(150.0, 400.0), d * 0.7, d * 0.5,
                        rnd.randint(0, 9999)))
        y += rnd.uniform(500.0, 1100.0)
    # keep the strip of the right wing around the post free, except the one plant that shows the missed spot
    out = [w for w in out if abs(w[0]) <= 1800.0 and not (w[0] + w[2] / 2.0 > P.centre_half - 100.0 and
                                                           abs(w[1] - POST[1]) < 3800.0)]
    out.append((1500.0, POST[1] + 650.0, 320.0, 220.0, 4242))       # in the folded strip, just past the post
    return sorted(out, key=lambda w: w[1])


# ---------------------------------------------------------------------
# Drive: accelerate, constant speed, brake. Y(t) in mm.
# ---------------------------------------------------------------------
def _profile():
    v = V * 1000.0
    a = ACC * 1000.0
    d = Y_END - Y_START
    ta = v / a
    da = 0.5 * a * ta * ta
    tc = (d - 2 * da) / v
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
    """First time the robot centre reaches y (bisection)."""
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
# Right wing fold for the post. The wing must be fully up when its front face (tube front at boom_y + 20) reaches the
# post minus the clearance, and may come down when its rear (riser, coils at boom_y - 70) has passed it.
# ---------------------------------------------------------------------
BOOM_FRONT = P.boom_y + P.tube / 2.0
BOOM_REAR = P.boom_y - 70.0


def fold_schedule():
    px, py, pd, ph = POST
    t_up = C.fold_time(0.0, P.fold_up)
    t_reach = time_at(py - pd / 2.0 - POST_CLEAR - BOOM_FRONT)
    t_pass = time_at(py + pd / 2.0 + POST_CLEAR - BOOM_REAR)
    return {"up_start": t_reach - t_up, "up_end": t_reach, "down_start": t_pass, "down_end": t_pass + t_up,
            "t_fold": t_up}


def fold_right(t, sched=None):
    s = sched or fold_schedule()
    if t <= s["up_start"]:
        return 0.0
    if t <= s["up_end"]:
        return C.phi_at(t - s["up_start"], 0.0, P.fold_up)
    if t <= s["down_start"]:
        return P.fold_up
    if t <= s["down_end"]:
        return C.phi_at(t - s["down_start"], P.fold_up, 0.0)
    return 0.0


# ---------------------------------------------------------------------
# Detection and spraying
# ---------------------------------------------------------------------
def detect_time(w, step=0.02):
    """First time the weed lies in the detection band and inside the image."""
    x, y = w[0], w[1]
    t = time_at(y - C.camera()["band_y"][1] - 50.0)
    t_end = time_at(y - C.camera()["band_y"][0] + 50.0)
    while t <= t_end:
        if C.sees(x, y - robot_y(t)):
            return t
        t += step
    return None


def nozzle_span(i):
    nx = P.nozzle_x[i]
    return nx - P.nozzle_pitch / 2.0, nx + P.nozzle_pitch / 2.0


def wing_of(i):
    nx = P.nozzle_x[i]
    if nx > P.centre_half:
        return "right"
    if nx < -P.centre_half:
        return "left"
    return "centre"


def plan():
    """Per weed: detection time, the nozzles that cover it and the time window they are open (nozzle line over the
    spot). Valve delay is compensated by switching early (valve_ms)."""
    out = []
    lead = P.valve_ms / 1000.0
    for w in weeds():
        x, y, d = w[0], w[1], w[2]
        r = d / 2.0 + P.spray_margin
        nozzles = [i for i in range(P.n_nozzles) if nozzle_span(i)[1] > x - r and nozzle_span(i)[0] < x + r]
        t_on = time_at(y - r - P.boom_y) - lead
        t_off = time_at(y + r - P.boom_y) - lead
        out.append({"weed": w, "detect": detect_time(w), "nozzles": nozzles, "on": t_on, "off": t_off,
                    "span_y": (y - r, y + r)})
    return out


def frame_state(t, plan_=None, sched=None):
    """State at time t: robot, fold, nozzle valves, weeds (detected / sprayed / missed), sprayed patches, litres."""
    plan_ = plan_ or plan()
    sched = sched or fold_schedule()
    phi_r = fold_right(t, sched)
    y_r = robot_y(t)
    q = C.nozzle_flow() / 60.0              # l/s per nozzle
    open_ = [False] * P.n_nozzles
    patches = []                            # (x0, x1, y0, y1) world, sprayed so far
    litres = 0.0
    weed_state = []
    for p in plan_:
        det = p["detect"] is not None and t >= p["detect"]
        sprayed, missed = False, False
        for i in p["nozzles"]:
            folded = wing_of(i) == "right" and fold_right(0.5 * (p["on"] + p["off"]), sched) > 2.0
            if folded:
                missed = missed or t >= p["on"]
                continue
            if p["detect"] is None:
                continue
            if t >= p["on"]:
                t1 = min(t, p["off"])
                litres += q * (t1 - p["on"])
                x0, x1 = nozzle_span(i)
                y0 = p["span_y"][0]
                y1 = y0 + (p["span_y"][1] - y0) * min(1.0, (t - p["on"]) / max(1e-6, p["off"] - p["on"]))
                patches.append((x0, x1, y0, y1))
                sprayed = True
                if t < p["off"]:
                    open_[i] = True
        weed_state.append({"detected": det, "sprayed": sprayed and not missed, "missed": missed})
    folded_r = phi_r > 2.0
    driven = max(0.0, y_r - Y_START) / 1000.0
    blanket = driven * P.work_width / 1000.0 / 10000.0 * C.spray()["rate_l_ha"]
    return {"t": t, "y": y_r, "v": robot_v(t), "phi_r": phi_r, "open": open_, "patches": patches, "litres": litres,
            "blanket_l": blanket, "weeds": weed_state, "right_folded": folded_r}


def summary():
    pl = plan()
    s = fold_schedule()
    end = frame_state(drive_time(), pl, s)
    return {"weeds": len(pl), "detected": sum(1 for p in pl if p["detect"] is not None),
            "sprayed": sum(1 for w in end["weeds"] if w["sprayed"]),
            "missed_fold": sum(1 for w in end["weeds"] if w["missed"]),
            "lead_s_min": round(min(p["on"] - p["detect"] for p in pl if p["detect"] is not None), 2),
            "litres": round(end["litres"], 3), "blanket_l": round(end["blanket_l"], 2),
            "saving": round(1.0 - end["litres"] / end["blanket_l"], 3), "fold": {k: round(v, 2) for k, v in s.items()},
            "duration_s": round(drive_time(), 1)}
