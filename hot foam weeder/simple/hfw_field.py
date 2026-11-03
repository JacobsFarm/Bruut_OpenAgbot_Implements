"""Process model of the hot foam weeder (pure Python): weeds on a paved path, the drive at the dose speed, the foam
laid by the bar, the heat time per weed and the water and gas used.

The robot drives straight along +y at x = 0. World coordinates; the robot centre is at (0, Y).
Used by animate_hfw.py and make_gif_hfw.py; rates from hfw_calc.
"""
import random

import hfw_params as P
import hfw_calc as C

SEED = 4
Y_START = 0.0                   # robot centre at t = 0
Y_END = 3600.0
ACC = 0.2                       # m/s2
V = C.work()["speed_m_s"]
HOLD_END = 6.0                  # s after the stop: the last weeds die under the foam
PATH_Y = (Y_START - 2600.0, Y_END + 1400.0)
WEED_Y = (Y_START - 300.0, Y_END - 1000.0)     # weeds the bar reaches before the stop
N_WEEDS = 40
HALF_W = P.W.work_w / 2.0


def weeds():
    """(x, y, s): weeds in the joints of the path (s = size factor; drawn ~3 x larger to be seen)."""
    rnd = random.Random(SEED)
    out = [(rnd.uniform(-HALF_W + 60.0, HALF_W - 60.0), rnd.uniform(*WEED_Y), rnd.uniform(2.5, 4.0))
           for _ in range(N_WEEDS)]
    return sorted(out, key=lambda w: w[1])


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


def frame_state(t, weeds_=None):
    """State at t: robot, foam strip (y0, y1), per weed: foamed, seconds under heat, dead; water and gas used.
    The bar is on while the robot moves (the flow follows the speed, so the dose stays the same)."""
    weeds_ = weeds_ or weeds()
    y_r = robot_y(t)
    y_bar0 = Y_START + P.bar_y
    y_bar = y_r + P.bar_y
    states = []
    for (x, y, s) in weeds_:
        if y > y_bar:
            states.append({"foamed": False, "heat_s": 0.0, "dead": False})
            continue
        t_hit = time_at(y - P.bar_y)
        heat = min(t - t_hit, P.foam_hold_s)
        states.append({"foamed": True, "heat_s": heat, "dead": heat >= P.lethal_s})
    area = max(0.0, y_bar - y_bar0) / 1000.0 * P.W.work_w / 1000.0
    water = area * P.dose_l_m2
    gas = water / C.boiler()["water_l_min"] * C.boiler()["gas_kg_h"] / 60.0 * 1000.0              # g
    return {"t": t, "y": y_r, "v": robot_v(t), "foam": (y_bar0, y_bar), "weeds": states, "m2": area,
            "water_l": water, "gas_g": gas, "on": robot_v(t) > 1.0}


def summary():
    end = frame_state(drive_time() + HOLD_END)
    return {"weeds": len(end["weeds"]), "dead": sum(1 for s in end["weeds"] if s["dead"]),
            "m2": round(end["m2"], 2), "water_l": round(end["water_l"], 2), "gas_g": round(end["gas_g"]),
            "speed_m_s": V, "duration_s": round(drive_time(), 1)}


if __name__ == "__main__":
    print(summary())
