"""Pure calculation of the three two-liquid refill animations (no FreeCAD): paths of the working robot and the mobile
refiller, applicator lift, pumps and liquid levels, trailer arm lift, playback speed and camera, per video frame.

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B tla_plan.py turn station cycle      (summary per scenario)

A frame is a dict: t (real s), worker / refiller (rear-axle pose x, y, psi, steer, spin, visible), lift (applicator,
mm), arm_lift (trailer arm, mm), levels {worker A/B, refiller A/B, trailer A/B} (litres), pumps {name: (liquid, from,
to)}, strips {pass: (y_far, y_near)}, cam (eye, target).
"""
import bisect
import math
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import tla_params as P      # noqa: E402

for _f in (P.SIT2_FOLDER, P.MRD_FOLDER):
    if _f not in sys.path:
        sys.path.insert(0, _f)
import sit2_params as SP    # noqa: E402
import mrd_params as MP     # noqa: E402

TRAILER = SP.cfg()
REACH = {"A": TRAILER["reach_A"], "B": TRAILER["reach_B"], "mid": TRAILER["reach"]}
MAST_Y = TRAILER["mast_y"]
LIQ = ("A", "B")


# ---------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------
def heading(psi):
    a = math.radians(psi)
    return -math.sin(a), math.cos(a)


def to_world(pose, local, axle):
    """Robot-local point (x right, y forward, from the robot centre) -> field, for a rear-axle pose."""
    x, y, psi = pose[:3]
    hx, hy = heading(psi)
    rx, ry = hy, -hx
    cx, cy = x + axle * hx, y + axle * hy
    return cx + local[0] * rx + local[1] * hx, cy + local[0] * ry + local[1] * hy


def centre(pose, axle):
    return to_world(pose, (0.0, 0.0), axle)


def trailer_world(local, origin):
    """Trailer-local point -> field; the trailer heads +x (local +y -> +x, local +x -> -y)."""
    ox, oy = origin
    return ox + local[1], oy - local[0]


def pass_x(p):
    return (p - 1) * P.W


# ---------------------------------------------------------------------
# Paths: lists of (x, y, psi, kappa) of the rear axle, with a speed limit per point
# ---------------------------------------------------------------------
def line(p0, p1, v, reverse=False, step=20.0):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = max(1, int(math.hypot(dx, dy) / step))
    psi = math.degrees(math.atan2(-dx, dy)) + (180.0 if reverse else 0.0)
    return [(p0[0] + dx * i / n, p0[1] + dy * i / n, psi, 0.0, v) for i in range(n + 1)]


def arc(c, r, a0, a1, v, step=20.0):
    """Arc about c from angle a0 to a1 (deg), driven forward."""
    n = max(2, int(abs(math.radians(a1 - a0)) * r / step))
    ccw = a1 > a0
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = c[0] + r * math.cos(a), c[1] + r * math.sin(a)
        tx, ty = (-math.sin(a), math.cos(a)) if ccw else (math.sin(a), -math.cos(a))
        out.append((x, y, math.degrees(math.atan2(-tx, ty)), (1.0 if ccw else -1.0) / r, v))
    return out


def join(*parts):
    out = []
    for p in parts:
        out.extend(p[1:] if out else p)
    return out


def slow_end(path, dist, v):
    """Speed limit v over the last 'dist' mm of the path (creep to a stop under a nozzle)."""
    s, out = 0.0, list(path)
    for i in range(len(out) - 1, 0, -1):
        s += math.hypot(out[i][0] - out[i - 1][0], out[i][1] - out[i - 1][1])
        if s > dist:
            break
        x, y, psi, k, vl = out[i - 1]
        out[i - 1] = (x, y, psi, k, min(vl, v))
    return out


def profile(path, accel=P.ACCEL):
    """Time stamps along a path that starts and ends at rest, speed limit per point, accel limit. Returns cumulative
    times and distances."""
    n = len(path)
    ds = [0.0] + [math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]) for i in range(1, n)]
    v = [p[4] for p in path]
    v[0] = v[-1] = 0.0
    for i in range(1, n):
        v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * accel * ds[i]))
    for i in range(n - 2, -1, -1):
        v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * accel * ds[i + 1]))
    t = [0.0]
    for i in range(1, n):
        vm = max(0.5 * (v[i] + v[i - 1]), 5.0)
        t.append(t[-1] + ds[i] / vm)
    s = [0.0]
    for i in range(1, n):
        s.append(s[-1] + ds[i])
    return t, s


class Actor:
    """Schedule of one robot: moves (path with profile) and stands still in between. Pose at any time."""

    def __init__(self, pose, axle, wb):
        self.items = []         # (t0, t1, path, times, dists, sign)
        self.pose0 = pose
        self.axle, self.wb = axle, wb
        self.t_end = 0.0

    def move(self, t0, path, sign=1.0):
        times, dists = profile(path)
        self.items.append((t0, t0 + times[-1], path, times, dists, sign))
        self.t_end = t0 + times[-1]
        return self.t_end

    def raw(self, t):
        """(x, y, psi, kappa, travelled distance, moving)"""
        pose, dist = self.pose0, 0.0
        for t0, t1, path, times, dists, sign in self.items:
            if t < t0:
                break
            if t >= t1:
                pose = path[-1][:3]
                dist += sign * dists[-1]
                continue
            i = max(1, bisect.bisect_left(times, t - t0))
            a = (t - t0 - times[i - 1]) / max(1e-9, times[i] - times[i - 1])
            p, q = path[i - 1], path[i]
            dpsi = (q[2] - p[2] + 180.0) % 360.0 - 180.0
            pose = (p[0] + a * (q[0] - p[0]), p[1] + a * (q[1] - p[1]), p[2] + a * dpsi)
            return pose + (p[3] * (1 if sign > 0 else 1), dist + sign * (dists[i - 1] + a * (dists[i] - dists[i - 1])),
                           True)
        return tuple(pose) + (0.0, dist, False)


# ---------------------------------------------------------------------
# Scenarios: each returns a dict with the actors and the event lists
# ---------------------------------------------------------------------
def worker_turn_path(x_from, x_to, stop_x, y_start=-4500.0, y_end=-4500.0):
    """U-turn to the right (x_to > x_from) with a stop on the straight at rear-axle x = stop_x. Returns (to the stop,
    after the stop)."""
    c1, c2 = (x_from + P.R, P.Y_TURN), (x_to - P.R, P.Y_TURN)
    first = join(line((x_from, y_start), (x_from, -2000.0), P.V_WORK), line((x_from, -2000.0), (x_from, P.Y_TURN),
                                                                            P.V_HEAD),
                 arc(c1, P.R, 180.0, 90.0, P.V_HEAD), line((c1[0], P.YS), (stop_x, P.YS), P.V_HEAD))
    first = slow_end(first, 700.0, P.V_SLOW)
    second = join(line((stop_x, P.YS), (c2[0], P.YS), P.V_HEAD), arc(c2, P.R, 90.0, 0.0, P.V_HEAD),
                  line((x_to, P.Y_TURN), (x_to, -1500.0), P.V_HEAD), line((x_to, -1500.0), (x_to, y_end), P.V_WORK))
    return first, second


def refill_spot(p_from):
    """Mobile refiller (centre, heading +x) inside the U-turn p_from -> p_from + SKIP, and the stop of the working
    robot (rear-axle x) with its funnels under the two nozzles."""
    xc, yc = pass_x(p_from) + P.REFILL_DX, P.YS - P.DOCK_D
    stop_x = xc + P.FILL_Y - P.FUNNEL_Y - P.WORKER_AXLE
    return xc, yc, stop_x


def refiller_pose(xc, yc):
    """Rear-axle pose of the mobile refiller from its centre, heading +x."""
    return (xc - P.REFILLER_AXLE, yc, -90.0)


def pump_time(litres):
    return max(0.0, litres) / P.Q_PUMP


def scenario_turn():
    S = P.TURN
    pf = S["pass_from"]
    pt = pf + P.SKIP
    xc, yc, stop_x = refill_spot(pf)
    worker = Actor((pass_x(pf), -4500.0, 0.0), P.WORKER_AXLE, P.WORKER_WB)
    refiller = Actor(refiller_pose(xc, yc), P.REFILLER_AXLE, P.REFILLER_WB)
    first, second = worker_turn_path(pass_x(pf), pass_x(pt), stop_x)
    t = P.HOLD_START
    t_stop = worker.move(t, first)
    fill = {liq: P.WORKER_FULL_L - S["worker_l"][i] for i, liq in enumerate(LIQ)}
    t_pump = t_stop + 1.0 + P.T_CHECK
    t_done = t_pump + max(pump_time(v) for v in fill.values())
    t_go = t_done + P.T_CLOSE
    t_back = worker.move(t_go, second)
    # the refiller moves 1 m on once the working robot is back in its pass
    t_r = t_go + 0.75 * (t_back - t_go)
    rp = refiller_pose(xc, yc)
    t_r_end = refiller.move(t_r, line(rp[:2], (rp[0] + P.W, rp[1]), P.V_REFILLER * 0.6))
    pumps = []
    for i, liq in enumerate(LIQ):
        pumps.append({"src": "refiller", "dst": "worker", "liq": liq, "t0": t_pump, "t1": t_pump + pump_time(fill[liq]),
                      "litres": fill[liq]})
    end = max(t_back, t_r_end) + P.HOLD_END
    phases = [(0.0, "drive"), (t_stop - 3.0, "refill"), (t_go + 2.0, "drive")]
    return {"key": "turn", "worker": worker, "refiller": refiller, "trailer": None, "pumps": pumps, "end": end,
            "phases": phases, "passes": (pf, pt), "done": S["done"], "levels0": {
                "worker": S["worker_l"], "refiller": S["refiller_l"], "trailer": (0.0, 0.0)},
            "arm": [], "focus": [(0.0, "pair")]}


def trailer_origin_station():
    S = P.STATION
    return (pass_x(S["pass_from"]) + S["trailer_dx"], P.YS - REACH["mid"])


def scenario_station():
    S = P.STATION
    pf, pt = S["pass_from"], S["pass_to"]
    T = trailer_origin_station()
    nozzle_x = T[0] + MAST_Y
    stop_x = nozzle_x - P.FUNNEL_Y - P.WORKER_AXLE
    worker = Actor((pass_x(pf), -4500.0, 0.0), P.WORKER_AXLE, P.WORKER_WB)
    c1 = (pass_x(pf) + P.R, P.Y_TURN)
    first = join(line((pass_x(pf), -4500.0), (pass_x(pf), -2000.0), P.V_WORK),
                 line((pass_x(pf), -2000.0), (pass_x(pf), P.Y_TURN), P.V_HEAD), arc(c1, P.R, 180.0, 90.0, P.V_HEAD),
                 line((c1[0], P.YS), (stop_x, P.YS), P.V_HEAD))
    first = slow_end(first, 2000.0, P.V_SLOW)
    t = P.HOLD_START
    t_stop = worker.move(t, first)
    fill = {liq: P.WORKER_FULL_L - S["worker_l"][i] for i, liq in enumerate(LIQ)}
    t_pump = t_stop + 1.0 + P.T_CHECK
    t_done = t_pump + max(pump_time(v) for v in fill.values())
    t_go = t_done + P.T_CLOSE
    x0 = pass_x(pt) - P.R
    t_rev = worker.move(t_go, line((stop_x, P.YS), (x0, P.YS), P.V_REV, reverse=True), sign=-1.0)
    c2 = (x0, P.YS - P.R)
    third = join(arc(c2, P.R, 90.0, 0.0, P.V_HEAD), line((pass_x(pt), P.Y_TURN), (pass_x(pt), -1500.0), P.V_HEAD),
                 line((pass_x(pt), -1500.0), (pass_x(pt), -5000.0), P.V_WORK))
    t_end = worker.move(t_rev + 1.5, third)
    pumps = [{"src": "trailer", "dst": "worker", "liq": liq, "t0": t_pump, "t1": t_pump + pump_time(fill[liq]),
              "litres": fill[liq]} for liq in LIQ]
    phases = [(0.0, "drive"), (t_stop - 3.0, "refill"), (t_go + 2.0, "drive")]
    return {"key": "station", "worker": worker, "refiller": None, "trailer": T, "pumps": pumps,
            "end": t_end + P.HOLD_END, "phases": phases, "passes": (pf, pt), "done": S["done"],
            "levels0": {"worker": S["worker_l"], "refiller": (0.0, 0.0), "trailer": S["trailer_l"]}, "arm": [],
            "focus": [(0.0, "worker_trailer")]}


def time_at(actor, pred, t0, t1, dt=0.05):
    """First time in [t0, t1] at which pred(centre x, centre y) holds for the actor (t1 if never)."""
    t = t0
    while t < t1:
        x, y, psi = actor.raw(t)[:3]
        if pred(*centre((x, y, psi), actor.axle)):
            return t
        t += dt
    return t1


def reload_trip(refiller, t_dep, xc_from, xc_to, yc, T, lv_from, fill_to):
    """The mobile refiller drives from its spot to the trailer, the trailer lifts its arm (up before the refiller's
    front comes near the drop pipes), fills both IBCs, lowers the arm once the refiller has reversed out from under it,
    and the refiller reverses to its next spot. Returns times, pumps and arm moves."""
    nozzle_x = T[0] + MAST_Y
    dock_c = nozzle_x - P.FILL_Y                    # refiller centre with its fill funnels under the nozzles
    p0, p1, p2 = refiller_pose(xc_from, yc), refiller_pose(dock_c, yc), refiller_pose(xc_to, yc)
    t_dock = refiller.move(t_dep, slow_end(line(p0[:2], p1[:2], P.V_REFILLER), 1500.0, P.V_SLOW))
    lift_t = SP.lift_high / P.ARM_LIFT_SPEED
    front = P.REFILLER_AXLE + 215.0                 # front of the tyres from the centre (1315)
    t_near = time_at(refiller, lambda x, y: x + front > nozzle_x - P.ARM_MARGIN, t_dep, t_dock)
    t_up1 = min(t_near, t_dock + 1.0 + lift_t)
    t_up0 = t_up1 - lift_t
    t_pump = max(t_dock + 1.0, t_up1) + P.T_CHECK
    fill = {liq: fill_to[i] - lv_from[i] for i, liq in enumerate(LIQ)}
    t_done = t_pump + max(pump_time(v) for v in fill.values())
    t_rev0 = t_done + P.T_CLOSE + 0.5
    t_back = refiller.move(t_rev0, line(p1[:2], p2[:2], P.V_REV, reverse=True), sign=-1.0)
    t_dn0 = time_at(refiller, lambda x, y: x + front < nozzle_x - P.ARM_MARGIN, t_rev0, t_back)
    t_dn1 = t_dn0 + lift_t
    pumps = [{"src": "trailer", "dst": "refiller", "liq": liq, "t0": t_pump, "t1": t_pump + pump_time(fill[liq]),
              "litres": fill[liq]} for liq in LIQ]
    return {"t_dock": t_dock, "t_pump": t_pump, "t_done": t_done, "t_rev0": t_rev0, "t_back": t_back,
            "arm": [(t_up0, t_up1, 0.0, SP.lift_high), (t_dn0, t_dn1, SP.lift_high, 0.0)], "pumps": pumps,
            "t_up0": t_up0, "t_dn1": t_dn1}


def worker_fill(worker, t0, pf, stop_x, lv, y_start=-4500.0, y_end=-4500.0, appear_at=None):
    """The working robot comes out of pass pf, stops in its U-turn under the refiller's nozzles, is filled, and drives
    into pass pf + SKIP. With appear_at, it starts out of sight so that it comes into the picture (y -4000) then."""
    first, second = worker_turn_path(pass_x(pf), pass_x(pf + P.SKIP), stop_x, y_start=y_start, y_end=y_end)
    if appear_at is not None:
        times, _ = profile(first)
        i_vis = next(i for i, q in enumerate(first) if q[1] > -4000.0)
        t0 = appear_at - times[i_vis]
    t_stop = worker.move(t0, first)
    fill = {liq: P.WORKER_FULL_L - lv[i] for i, liq in enumerate(LIQ)}
    t_pump = t_stop + 1.0 + P.T_CHECK
    t_go = t_pump + max(pump_time(v) for v in fill.values()) + P.T_CLOSE
    t_back = worker.move(t_go, second)
    pumps = [{"src": "refiller", "dst": "worker", "liq": liq, "t0": t_pump, "t1": t_pump + pump_time(fill[liq]),
              "litres": fill[liq]} for liq in LIQ]
    return {"t0": t0, "t_stop": t_stop, "t_go": t_go, "t_back": t_back, "pumps": pumps, "first": first}


def use(t0, t1, lv_from, lv_to):
    """The working robot applies liquid in the field between two turns (levels only, no stream)."""
    return [{"src": "worker", "dst": "field", "liq": liq, "t0": t0, "t1": t1, "litres": lv_from[i] - lv_to[i]}
            for i, liq in enumerate(LIQ)]


def scenario_cycle():
    S = P.CYCLE
    pf = S["pass_from"]
    pt = pf + P.SKIP
    T = (S["trailer_x"], P.YS - P.DOCK_D - REACH["mid"])
    xc0, yc, _ = refill_spot(pf - 1)                 # where it filled the working robot at the previous turn
    xc1, _, stop_x = refill_spot(pf)                 # the spot of the next turn
    refiller = Actor(refiller_pose(xc0, yc), P.REFILLER_AXLE, P.REFILLER_WB)
    trip = reload_trip(refiller, P.HOLD_START, xc0, xc1, yc, T, S["refiller_l"], S["refiller_fill_to"])
    # the working robot comes out of its pass a little after the refiller is back in place
    worker = Actor(None, P.WORKER_AXLE, P.WORKER_WB)
    wf = worker_fill(worker, 0.0, pf, stop_x, S["worker_l"], y_start=-60000.0, appear_at=trip["t_back"] + 4.0)
    worker.pose0 = wf["first"][0][:3]
    pumps = trip["pumps"] + wf["pumps"]
    phases = [(0.0, "transfer"), (trip["t_dock"] - 2.0, "drive"), (trip["t_pump"] + 3.0, "fill_ibc"),
              (trip["t_done"] - 3.0, "drive"), (trip["t_rev0"] + 2.0, "transfer"), (trip["t_back"] - 2.0, "drive"),
              (wf["t_stop"] - 3.0, "refill"), (wf["t_go"] + 2.0, "drive")]
    return {"key": "cycle", "worker": worker, "refiller": refiller, "trailer": T, "pumps": pumps,
            "end": wf["t_back"] + P.HOLD_END, "phases": phases, "passes": (pf, pt), "done": S["done"],
            "levels0": {"worker": S["worker_l"], "refiller": S["refiller_l"], "trailer": S["trailer_l"]},
            "arm": trip["arm"], "worker_visible_from": trip["t_back"] + 3.0,
            "focus": [(0.0, "refiller_trailer"), (trip["t_back"] - 6.0, "pair")]}


def scenario_rounds():
    """Two refills in the turn, the refiller reloads at the trailer, one more refill in the turn."""
    S = P.ROUNDS
    p1 = S["pass_from"]
    T = (S["trailer_x"], P.YS - P.DOCK_D - REACH["mid"])
    wl = S["worker_l"]
    spots = [refill_spot(p1 + k) for k in range(3)]  # (xc, yc, stop_x) of the turns p1, p1 + 1, p1 + 2
    yc = spots[0][1]
    worker = Actor((pass_x(p1), -4500.0, 0.0), P.WORKER_AXLE, P.WORKER_WB)
    refiller = Actor(refiller_pose(spots[0][0], yc), P.REFILLER_AXLE, P.REFILLER_WB)
    pumps, phases = [], [(0.0, "drive")]
    # turn 1: pass p1 -> p1 + 6, then down that pass out of sight
    f1 = worker_fill(worker, P.HOLD_START, p1, spots[0][2], wl[0], y_end=P.Y_FAR)
    pumps += f1["pumps"]
    # the refiller moves 1 m on once the working robot is back in its pass
    t_in1 = time_at(worker, lambda x, y: y < -2500.0, f1["t_go"], f1["t_back"])
    pa, pb = refiller_pose(spots[0][0], yc), refiller_pose(spots[1][0], yc)
    refiller.move(t_in1, line(pa[:2], pb[:2], P.V_REFILLER * 0.6))
    # turn 2: the working robot comes up the next pass (it turned at the far end)
    f2 = worker_fill(worker, f1["t_back"] + 1.0, p1 + 1, spots[1][2], wl[1], y_start=P.Y_FAR, y_end=P.Y_FAR)
    pumps += f2["pumps"] + use(f1["t_go"] + 8.0, f2["t_stop"] - 2.0, (P.WORKER_FULL_L,) * 2, wl[1])
    phases += [(f1["t_stop"] - 3.0, "refill"), (f1["t_go"] + 2.0, "drive"), (t_in1 + 4.0, "away"),
               (f2["t_stop"] - 12.0, "drive"), (f2["t_stop"] - 3.0, "refill"), (f2["t_go"] + 2.0, "drive")]
    # the refiller goes to the trailer once the working robot is back in its pass, and returns to the third spot
    t_in2 = time_at(worker, lambda x, y: y < -2500.0, f2["t_go"], f2["t_back"])
    lv_r = tuple(S["refiller_l"][i] - sum(p["litres"] for p in f1["pumps"] + f2["pumps"] if p["liq"] == liq)
                 for i, liq in enumerate(LIQ))
    trip = reload_trip(refiller, t_in2, spots[1][0], spots[2][0], yc, T, lv_r, S["refiller_fill_to"])
    pumps += trip["pumps"]
    phases += [(t_in2 + 3.0, "transfer"), (trip["t_dock"] - 2.0, "drive"), (trip["t_pump"] + 3.0, "fill_ibc"),
               (trip["t_done"] - 3.0, "drive"), (trip["t_rev0"] + 2.0, "transfer"), (trip["t_back"] - 2.0, "drive")]
    # turn 3: the working robot comes out of the next pass after the refiller is back
    f3 = worker_fill(worker, 0.0, p1 + 2, spots[2][2], wl[2], y_start=P.Y_FAR, appear_at=trip["t_back"] + 4.0)
    pumps += f3["pumps"] + use(f2["t_go"] + 8.0, f3["t_stop"] - 2.0, (P.WORKER_FULL_L,) * 2, wl[2])
    phases += [(f3["t_stop"] - 3.0, "refill"), (f3["t_go"] + 2.0, "drive")]
    passes = (p1, p1 + 6, p1 + 1, p1 + 7, p1 + 2, p1 + 8)
    return {"key": "rounds", "worker": worker, "refiller": refiller, "trailer": T, "pumps": pumps,
            "end": f3["t_back"] + P.HOLD_END, "phases": phases, "passes": passes, "done": S["done"],
            "levels0": {"worker": wl[0], "refiller": S["refiller_l"], "trailer": S["trailer_l"]},
            "arm": trip["arm"],
            "focus": [(0.0, "pair"), (t_in2 + 2.0, "refiller_trailer"), (trip["t_back"] - 6.0, "pair")]}


SCENARIOS = {"turn": scenario_turn, "station": scenario_station, "cycle": scenario_cycle,
             "rounds": scenario_rounds}


# ---------------------------------------------------------------------
# Simulation on a fine time grid: steering (rate-limited), applicator lift, strips, levels
# ---------------------------------------------------------------------
def wheel_angles(delta, wb):
    t = math.tan(math.radians(delta))
    half = P.WHEEL_X
    return (math.degrees(math.atan2(wb * t, wb - half * t)), math.degrees(math.atan2(wb * t, wb + half * t)))


def _approach(cur, target, rate, dt):
    d = target - cur
    step = rate * dt
    return target if abs(d) <= step else cur + math.copysign(step, d)


def arm_lift(sc, t):
    for t0, t1, a, b in sc["arm"]:
        if t0 <= t <= t1:
            return a + (b - a) * (t - t0) / (t1 - t0)
    done = [b for t0, t1, a, b in sc["arm"] if t > t1]
    return done[-1] if done else 0.0


def levels(sc, t):
    lv = {k: list(v) for k, v in sc["levels0"].items()}
    for p in sc["pumps"]:
        f = max(0.0, min(1.0, (t - p["t0"]) / max(1e-9, p["t1"] - p["t0"])))
        i = LIQ.index(p["liq"])
        lv[p["src"]][i] -= f * p["litres"]
        if p["dst"] in lv:
            lv[p["dst"]][i] += f * p["litres"]
    return {k: tuple(v) for k, v in lv.items()}


def pumping(sc, t):
    """Pumps running at t (not the working robot's own use in the field: no stream)."""
    return [(p["src"], p["dst"], p["liq"]) for p in sc["pumps"] if p["t0"] <= t < p["t1"] and p["dst"] != "field"]


def simulate(key):
    sc = SCENARIOS[key]()
    n = int(sc["end"] / P.DT) + 1
    st = {"w_steer": 0.0, "r_steer": 0.0, "lift": P.LIFT_MAX * 0.0, "strip": {}}
    samples = []
    for k in range(n):
        t = k * P.DT
        s = {"t": t}
        w = sc["worker"]
        if w is not None and w.pose0 is not None:
            x, y, psi, kap, dist, moving = w.raw(t)
            target = math.degrees(math.atan(w.wb * kap))
            st["w_steer"] = _approach(st["w_steer"], target, P.STEER_RATE, P.DT)
            # applicator: up when the knives come near the field edge going out, down going in
            hx, hy = heading(psi)
            kx, ky = x - P.KNIFE_BEHIND * hx, y - P.KNIFE_BEHIND * hy
            going_out = hy > 0.5
            going_in = hy < -0.5
            if going_out and ky > -P.RAISE_LEAD:
                lt = P.LIFT_MAX
            elif going_in and ky < P.LOWER_LEAD:
                lt = 0.0
            elif abs(hy) <= 0.5 or y > 0.0:
                lt = P.LIFT_MAX
            else:
                lt = st["lift"]
            st["lift"] = _approach(st["lift"], lt, P.ACT_SPEED, P.DT)
            if st["lift"] < 25.0 and ky < 0.0:
                pk = int(round(kx / P.W)) + 1
                lo, hi = st["strip"].get(pk, (ky, ky))
                st["strip"][pk] = (min(lo, ky), max(hi, ky))
            vis = t >= sc.get("worker_visible_from", -1.0) and y > P.Y_HIDE
            s["worker"] = (x, y, psi, st["w_steer"], dist / P.TIRE_R, vis)
        if sc["refiller"] is not None:
            r = sc["refiller"]
            x, y, psi, kap, dist, moving = r.raw(t)
            st["r_steer"] = _approach(st["r_steer"], math.degrees(math.atan(r.wb * kap)), P.STEER_RATE, P.DT)
            s["refiller"] = (x, y, psi, st["r_steer"], dist / P.TIRE_R, True)
        s["lift"] = st["lift"]
        s["arm_lift"] = arm_lift(sc, t)
        s["strips"] = dict(st["strip"])
        samples.append(s)
    return sc, samples


# ---------------------------------------------------------------------
# Playback speed and frames
# ---------------------------------------------------------------------
def phase_at(sc, t):
    name = sc["phases"][0][1]
    for t0, nm in sc["phases"]:
        if t >= t0:
            name = nm
    return name


def speed_curve(sc):
    """Real seconds per video second on the fine grid, smoothed (log scale, +-2.5 s) so the pace changes gently."""
    n = int(sc["end"] / P.DT) + 1
    raw = [math.log(P.SPEED[phase_at(sc, k * P.DT)]) for k in range(n)]
    w = int(2.5 / P.DT)
    pre = [0.0]
    for v in raw:
        pre.append(pre[-1] + v)
    out = []
    for k in range(n):
        a, b = max(0, k - w), min(n, k + w + 1)
        out.append(math.exp((pre[b] - pre[a]) / (b - a)))
    return out


def frame_times(sc):
    sp = speed_curve(sc)
    t, out = 0.0, []
    while t <= sc["end"]:
        out.append(t)
        k = min(len(sp) - 1, int(t / P.DT))
        t += sp[k] / P.FPS
    hold = [0.0] * int(P.HOLD_START * P.FPS)
    return hold + out + [out[-1]] * int(P.HOLD_END * P.FPS)


# ---------------------------------------------------------------------
# Camera: wide over both actors, closer while filling; smoothed over +-1.2 s of video
# ---------------------------------------------------------------------
# direction from the target to the eye: from the fence side and high, so that the robot on the headland is in front of
# the refiller or the trailer (they stand between it and the field)
CAM_DIR = {"pair": (0.18, 0.60, 0.78), "worker_trailer": (0.10, 0.62, 0.78), "refiller_trailer": (-0.12, 0.60, 0.79)}
CAM_CLOSE = (-0.22, 0.70, 0.68)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def focus_at(sc, t):
    name = sc["focus"][0][1]
    for t0, nm in sc["focus"]:
        if t >= t0:
            name = nm
    return name


def camera_raw(sc, s):
    pts = []        # (x, y, weight): the working robot fades out of the shot as it drives down its pass
    if "worker" in s and s["worker"][5]:
        wx, wy = centre(s["worker"], P.WORKER_AXLE)
        wgt = max(0.0, min(1.0, (wy - P.CAM_WORKER_Y[0]) / (P.CAM_WORKER_Y[1] - P.CAM_WORKER_Y[0])))
        if wgt > 0.0:
            pts.append((wx, wy, wgt))
    if "refiller" in s:
        pts.append(centre(s["refiller"], P.REFILLER_AXLE) + (1.0,))
    focus = focus_at(sc, s["t"])
    if sc["trailer"] is not None and focus != "pair":
        tx, ty = trailer_world((0.0, MAST_Y - 800.0), sc["trailer"])
        pts.append((tx, ty, 1.0))
    if not pts:
        pts = [(0.0, 0.0, 1.0)]
    sw = sum(p[2] for p in pts)
    cx = sum(p[0] * p[2] for p in pts) / sw
    cy = sum(p[1] * p[2] for p in pts) / sw
    spread = max([p[2] * math.hypot(p[0] - cx, p[1] - cy) for p in pts] + [0.0])
    close = 1.0 if pumping(sc, s["t"]) else 0.0
    d = _unit(CAM_DIR[focus])
    dist = max(8000.0, 2.1 * spread + 5800.0)
    tgt = [cx, cy, 500.0]
    return tgt, d, dist, close


def cameras(sc, samples, times):
    raw = [camera_raw(sc, samples[min(len(samples) - 1, int(t / P.DT))]) for t in times]
    w = int(1.2 * P.FPS)
    out = []
    for i in range(len(raw)):
        a, b = max(0, i - w), min(len(raw), i + w + 1)
        m = b - a
        tgt = [sum(r[0][j] for r in raw[a:b]) / m for j in range(3)]
        d = [sum(r[1][j] for r in raw[a:b]) / m for j in range(3)]
        dist = sum(r[2] for r in raw[a:b]) / m
        k = sum(r[3] for r in raw[a:b]) / m
        k = k * k * (3 - 2 * k)
        d = _unit([d[j] + (CAM_CLOSE[j] - d[j]) * k * 0.6 for j in range(3)])
        dist = dist * (1.0 - 0.28 * k)
        tgt[2] = 500.0 + 450.0 * k
        out.append(([tgt[j] + d[j] * dist for j in range(3)], tgt))
    return out


def frames(key):
    sc, samples = simulate(key)
    times = frame_times(sc)
    cams = cameras(sc, samples, times)
    out = []
    for t, cam in zip(times, cams):
        s = dict(samples[min(len(samples) - 1, int(t / P.DT))])
        s["t"] = t
        s["levels"] = levels(sc, t)
        s["pumps"] = pumping(sc, t)
        s["cam"] = cam
        out.append(s)
    return sc, out


# ---------------------------------------------------------------------
# Checks without FreeCAD: outlines of the working robot (with the lifted applicator) and the mobile refiller
# ---------------------------------------------------------------------
WORKER_OUTLINE = [(-500.0, -1767.0), (500.0, -1767.0), (500.0, 765.0), (-500.0, 765.0)]
REFILLER_OUTLINES = [
    [(-500.0, -1315.0), (500.0, -1315.0), (500.0, 1315.0), (-500.0, 1315.0)],           # robot with tyres
    [(-606.0, -1126.0), (606.0, -1126.0), (606.0, 986.0), (-606.0, 986.0)],             # IBCs with guides
    [(-780.0, -140.0), (-606.0, -140.0), (-606.0, 0.0), (-780.0, 0.0)]]                 # mast, hoses, outrigger


def _poly_world(pose, outline, axle):
    return [to_world(pose, p, axle) for p in outline]


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
    if not _separated(a, b):
        return 0.0
    d = 1e18
    for poly, other in ((a, b), (b, a)):
        for p in poly:
            for i in range(len(other)):
                d = min(d, _seg_dist(p, other[i], other[(i + 1) % len(other)]))
    return d


def min_gap(key, step=5):
    """Smallest plan-view gap (mm) between the working robot and the mobile refiller over the run."""
    sc, samples = simulate(key)
    best = (1e9, None)
    for s in samples[::step]:
        if "worker" not in s or "refiller" not in s or not s["worker"][5]:
            continue
        wp = _poly_world(s["worker"], WORKER_OUTLINE, P.WORKER_AXLE)
        for o in REFILLER_OUTLINES:
            d = poly_dist(wp, _poly_world(s["refiller"], o, P.REFILLER_AXLE))
            if d < best[0]:
                best = (round(d), round(s["t"], 1))
    return best


# trailer, trailer-local (x across, y along, from the middle of the axle): everything below z 1300 (frame, tyres,
# IBC cages, control box, drawbar; from the STEP of ../stationary/ibc_trailer_two_liquids), and the arm with its drop
# pipes over the left side (local -x) at the mast
TRAILER_FOOTPRINT = [(-885.0, -1391.0), (885.0, -1391.0), (885.0, 3580.0), (-885.0, 3580.0)]
TRAILER_ARM = [(-1980.0, MAST_Y - 160.0), (0.0, MAST_Y - 160.0), (0.0, MAST_Y + 160.0), (-1980.0, MAST_Y + 160.0)]


def trailer_gap(key, step=5):
    """Plan-view checks against the trailer over the run: smallest gap (mm, time) of the working robot and of the
    mobile refiller to the trailer's footprint, and the times the refiller's IBCs are under the arm while it is not
    fully up (must be none)."""
    sc, samples = simulate(key)
    if sc["trailer"] is None:
        return None
    foot = [trailer_world(p, sc["trailer"]) for p in TRAILER_FOOTPRINT]
    arm = [trailer_world(p, sc["trailer"]) for p in TRAILER_ARM]
    best = {"worker": (1e9, None), "refiller": (1e9, None)}
    under_low_arm = []
    for s in samples[::step]:
        if "worker" in s and s["worker"][5]:
            d = poly_dist(_poly_world(s["worker"], WORKER_OUTLINE, P.WORKER_AXLE), foot)
            if d < best["worker"][0]:
                best["worker"] = (round(d), round(s["t"], 1))
        if "refiller" in s:
            for o in REFILLER_OUTLINES:
                d = poly_dist(_poly_world(s["refiller"], o, P.REFILLER_AXLE), foot)
                if d < best["refiller"][0]:
                    best["refiller"] = (round(d), round(s["t"], 1))
            ibcs = _poly_world(s["refiller"], REFILLER_OUTLINES[1], P.REFILLER_AXLE)
            if poly_dist(ibcs, arm) == 0.0 and s["arm_lift"] < SP.lift_high - 1.0:
                under_low_arm.append(round(s["t"], 1))
    return {"worker": best["worker"], "refiller": best["refiller"],
            "under_low_arm": (under_low_arm[0], under_low_arm[-1]) if under_low_arm else None}


def summary(key):
    sc, fr = frames(key)
    lv0, lv1 = fr[0]["levels"], fr[-1]["levels"]
    lines = ["%s: %.1f s real, %d frames = %.1f s video at %d fps" % (key, sc["end"], len(fr), len(fr) / P.FPS, P.FPS)]
    lines.append("  levels start %s" % {k: tuple(round(v, 1) for v in vs) for k, vs in lv0.items()})
    lines.append("  levels end   %s" % {k: tuple(round(v, 1) for v in vs) for k, vs in lv1.items()})
    for p in sc["pumps"]:
        lines.append("  pump %s %s -> %s: %.1f l, %.1f .. %.1f s" % (p["liq"], p["src"], p["dst"], p["litres"], p["t0"],
                                                                    p["t1"]))
    if sc["worker"] is not None and sc["refiller"] is not None:
        lines.append("  smallest gap working robot - refiller (plan view): %s mm at %s s" % min_gap(key))
    if sc["trailer"] is not None:
        g = trailer_gap(key)
        lines.append("  smallest gap to the trailer (plan view): working robot %s, refiller %s (mm, s); refiller under "
                     "the arm while not up: %s" % (g["worker"], g["refiller"], g["under_low_arm"]))
    return "\n".join(lines)


if __name__ == "__main__":
    for k in sys.argv[1:] or list(SCENARIOS):
        print(summary(k))
