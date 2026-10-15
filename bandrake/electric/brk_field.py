"""Process model for the animation (pure Python): grassland with loose litter (moss, thatch, dead grass after
scarifying) and the windrow of the previous pass. The robot works from the outside of the field inwards: the previous
pass laid its windrow inside this pass's width, so this pass carries it along together with the new litter and lays
one bigger windrow to the left. At the end the castor actuators lift the rake for the headland and the belt stops.

Every piece of litter is a straw. When the tine band (the bottom run, rake_y +- band / 2 relative to the robot) reaches
a piece within the working width, the tines carry it to the left at carry_eff x belt speed, while it moves along with
the robot; past the left end it is thrown against the swath board and lands in the windrow.

    import brk_field as F
    F.simulate(); F.summary()
"""
import math
import random

import brk_params as P
import brk_calc as C

MODE = "rake"
Y_START = -1500.0               # robot centre at t = 0
DRIVE = 5400.0                  # mm driven while raking
HOLD_END = 1.0
DT = 0.05
SEED = 12
CARRY_EFF = 0.8                 # material moves at 0.8 x the belt speed
PIECE_KG = 0.002                # one drawn straw stands for 2 g of litter
WINDROW_X = P.board_x + 90.0    # windrow centre, just inside the swath board
PREV_X = WINDROW_X + 1410.0     # windrow of the previous pass (one working width to the right)


def mode():
    return P.modes[MODE]


def drive_time():
    return DRIVE / (mode()["v"] * 1000.0)


def lift_time():
    return P.lift_travel / P.cact_speed


def t_end():
    return drive_time() + lift_time() + HOLD_END


def robot_y(t):
    return Y_START + mode()["v"] * 1000.0 * min(t, drive_time())


def lift_at(t):
    """Rake height above the working height (mm): castor actuators push it up after the drive."""
    if t <= drive_time():
        return 0.0
    return min(P.lift_travel, (t - drive_time()) * P.cact_speed)


def belt_phase(t):
    """Belt position (mm): runs at u while raking and while lifting; stops when the rake is up."""
    return mode()["u"] * 1000.0 * min(t, drive_time() + lift_time())


def zone(t):
    """Tine band in the field: x range (working width) and y range."""
    x0, x1 = C.working_width(MODE, reach=mode()["reach"])
    band = (P.n_legs - 1) * P.leg_pitch / 2.0 + 30.0
    yc = robot_y(t) + P.rake_y
    return x0, x1, yc - band, yc + band


_PIECES = {}


def pieces(seed=SEED):
    if seed in _PIECES:
        return _PIECES[seed]
    rnd = random.Random(seed)
    y0 = Y_START + P.rake_y - 150.0
    y1 = Y_START + DRIVE + P.rake_y + 600.0
    n = int(P.litter_kg_m2 * 1.7 * (y1 - y0) / 1000.0 / PIECE_KG)           # over x -850 .. 850
    out = []
    for _ in range(n):
        out.append({"x": rnd.uniform(-850.0, 850.0), "y": rnd.uniform(y0, y1), "l": rnd.uniform(45.0, 110.0),
                    "rot": rnd.uniform(0.0, 180.0), "z": 0.5, "prev": False})
    k_prev = int(P.litter_kg_m2 * 1.41 * (y1 - y0) / 1000.0 / PIECE_KG)     # previous pass: one width of litter
    for _ in range(k_prev):
        out.append({"x": rnd.gauss(PREV_X, 45.0), "y": rnd.uniform(y0, y1), "l": rnd.uniform(45.0, 110.0),
                    "rot": rnd.uniform(0.0, 180.0), "z": rnd.uniform(0.5, 30.0), "prev": True})
    _PIECES[seed] = out
    return out


_SIM = {}


def simulate(seed=SEED):
    """States of all pieces per time step: list of (t, [(x, y, z, state)]); state 0 lying, 1 carried, 2 in the new
    windrow."""
    if seed in _SIM:
        return _SIM[seed]
    rnd = random.Random(seed + 1)
    ps = pieces(seed)
    state = [0] * len(ps)
    pos = [[p["x"], p["y"], p["z"]] for p in ps]
    pile = {}
    u = mode()["u"] * 1000.0 * CARRY_EFF
    v = mode()["v"] * 1000.0
    steps = []
    n = int(math.ceil(t_end() / DT)) + 1
    for k in range(n):
        t = k * DT
        x0, x1, y0, y1 = zone(t)
        working = t <= drive_time() and lift_at(t) < 20.0
        for i in range(len(ps)):
            if state[i] == 0 and working and x0 <= pos[i][0] <= x1 and y0 <= pos[i][1] <= y1:
                state[i] = 1
                pos[i][2] = 15.0
            if state[i] == 1:
                if working:
                    pos[i][0] -= u * DT
                    pos[i][1] += v * DT
                if pos[i][0] < x0 or not working:
                    state[i] = 2
                    wx = WINDROW_X + max(-100.0, min(100.0, rnd.gauss(0.0, 45.0)))
                    wy = pos[i][1] - rnd.uniform(0.0, 150.0)
                    key = (int(wx // 50), int(wy // 50))
                    pile[key] = pile.get(key, 0) + 1
                    pos[i] = [wx, wy, min(80.0, 1.0 + 5.0 * pile[key])]
        steps.append((t, [(p[0], p[1], p[2], s) for p, s in zip(pos, state)]))
    _SIM[seed] = steps
    return steps


def at(t):
    steps = simulate()
    k = max(0, min(len(steps) - 1, int(round(t / DT))))
    return steps[k][1]


def summary():
    steps = simulate()
    final = steps[-1][1]
    ps = pieces()
    moved = sum(1 for s in final if s[3] == 2)
    prev_moved = sum(1 for p, s in zip(ps, final) if p["prev"] and s[3] == 2)
    driven = DRIVE / 1000.0
    return {"pieces": len(ps), "moved_kg": round(moved * PIECE_KG, 2), "previous_windrow_taken": prev_moved,
            "previous_windrow_total": sum(1 for p in ps if p["prev"]),
            "windrow_kg_per_m": round(moved * PIECE_KG / driven, 3), "drive_s": round(drive_time(), 2),
            "lift_s": round(lift_time(), 2), "t_end": round(t_end(), 2)}
