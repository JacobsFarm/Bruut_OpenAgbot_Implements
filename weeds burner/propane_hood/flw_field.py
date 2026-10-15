"""Process model for the animation (pure Python): a freshly sown bed with weed seedlings (cotyledon to 4 leaves), the
robot driving at constant speed with the flames on, then stopping at the end of the bed: the valves close at once and
only the pilot flames stay on.

Every seedling under the hood collects heat: the soil dose (flw_calc.dose: soil_kJ_m2) spread over the time the hood
needs to pass. A seedling dies when it has had its lethal energy (60 kJ/m2 for the smallest, 120 for a 4-leaf one);
bigger seedlings that get less than that survive (they are shown as damaged).

    import flw_field as F
    F.simulate(); F.summary()
"""
import math
import random

import flw_params as P
import flw_calc as C

Y_START = 0.0
DRIVE = 4200.0                  # mm driven with the flames on
T_CLOSE = 0.3                   # s from 'stop' to the main valve closed (flames out, pilots on)
HOLD_END = 1.5
DT = 0.02
SEED = 9


def v():
    return P.speed * 1000.0


def drive_time():
    return DRIVE / v()


def t_end():
    return drive_time() + HOLD_END


def robot_y(t):
    return Y_START + v() * min(t, drive_time())


def flame_scale(t):
    """1 = full flames, 0.15 = pilots only."""
    if t <= drive_time():
        return 1.0
    k = min(1.0, (t - drive_time()) / T_CLOSE)
    return 1.0 - 0.85 * k


def hood_span(t):
    """Field y range under the hood (inside the walls) at time t."""
    y = robot_y(t)
    return y + P.hood_y[0], y + P.hood_y[1]


_W = {}


def weeds(seed=SEED):
    if seed in _W:
        return _W[seed]
    rnd = random.Random(seed)
    y0 = Y_START + P.hood_y[0] - 300.0
    y1 = Y_START + DRIVE + 2500.0
    n = int((y1 - y0) / 1000.0 * 1.5 * 55)          # ~55 seedlings per m2
    out = []
    for _ in range(n):
        s = rnd.uniform(0.6, 1.25)                  # size: 0.6 = cotyledons .. 1.25 = 4 leaves
        out.append({"x": rnd.uniform(-740.0, 740.0), "y": rnd.uniform(y0, y1), "s": s,
                    "lethal": P.lethal_kJ_m2[0] + (s - 0.6) / 0.65 * (P.lethal_kJ_m2[1] - P.lethal_kJ_m2[0])})
    _W[seed] = out
    return out


_SIM = {}


def simulate(seed=SEED):
    """Energy per seedling over time; the time it died (or None)."""
    if seed in _SIM:
        return _SIM[seed]
    ws = weeds(seed)
    d = C.dose()
    rate = d["soil_kJ_m2"] / d["exposure_s"]        # kJ/m2 per second under the hood at full flames
    energy = [0.0] * len(ws)
    died = [None] * len(ws)
    passed = [False] * len(ws)
    hist = []
    n = int(math.ceil(t_end() / DT)) + 1
    for k in range(n):
        t = k * DT
        y0, y1 = hood_span(t)
        f = flame_scale(t)
        for i, w in enumerate(ws):
            if abs(w["x"]) <= P.work_w / 2.0 and y0 <= w["y"] <= y1:
                energy[i] += rate * f * DT
                if died[i] is None and energy[i] >= w["lethal"]:
                    died[i] = t
            elif w["y"] < y0 and energy[i] > 0:
                passed[i] = True
        if k % 5 == 0:
            hist.append((t, list(energy)))
    _SIM[seed] = {"energy": energy, "died": died, "passed": passed, "hist": hist}
    return _SIM[seed]


def state(t):
    """Per seedling: 0 alive (not reached), 1 under the hood, 2 killed, 3 passed but survived (damaged)."""
    sim = simulate()
    ws = weeds()
    y0, y1 = hood_span(t)
    out = []
    for i, w in enumerate(ws):
        if sim["died"][i] is not None and sim["died"][i] <= t:
            out.append(2)
        elif abs(w["x"]) <= P.work_w / 2.0 and Y_START + P.hood_y[0] < w["y"] < y0:
            out.append(3)                           # was under the hood, survived
        elif abs(w["x"]) <= P.work_w / 2.0 and y0 <= w["y"] <= y1:
            out.append(1)
        else:
            out.append(0)
    return out


def gas_used(t):
    """kg of propane used up to t (main flames + pilots ~1 % of it)."""
    f = C.flow()["kg_h"] / 3600.0
    if t <= drive_time():
        return f * t
    return f * drive_time() + f * 0.5 * min(T_CLOSE, t - drive_time()) + 0.01 * f * max(0.0, t - drive_time())


def summary():
    sim = simulate()
    ws = weeds()
    # the seedlings that the whole hood passed over (not the ones already under it at the start)
    under = [i for i, w in enumerate(ws) if abs(w["x"]) <= P.work_w / 2.0 and sim["passed"][i]
             and w["y"] > Y_START + P.hood_y[1]]
    killed = [i for i in under if sim["died"][i] is not None]
    big = [i for i in under if ws[i]["s"] > 1.05]
    big_killed = [i for i in big if sim["died"][i] is not None]
    small = [i for i in under if ws[i]["s"] <= 0.9]
    small_killed = [i for i in small if sim["died"][i] is not None]
    return {"seedlings_passed": len(under), "killed": len(killed), "kill_share": round(len(killed) / float(max(1, len(under))), 3),
            "kill_small": round(len(small_killed) / float(max(1, len(small))), 3),
            "kill_4leaf": round(len(big_killed) / float(max(1, len(big))), 3),
            "gas_g": round(1000.0 * gas_used(t_end()), 0), "drive_s": round(drive_time(), 2)}
