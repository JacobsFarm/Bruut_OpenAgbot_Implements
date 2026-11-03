"""Process model for the renders and the animation: potato rows with a few sick plants, the drive along the rows,
the moment each plant is photographed, and the wing swing at the end of the field.

Pure Python (no FreeCAD), so the figures can be checked outside FreeCAD:
    python dsc_field.py
"""
import math
import random

import dsc_params as P
import dsc_calc as C

SEED = 1
SICK_SHARE = 0.08               # share of plants with symptoms in the animation (seed potato field, illustrative)
Y_FIELD = (-4000.0, 9000.0)
X_FIELD = (-2300.0, 2300.0)
Y_START = -2500.0               # robot centre at t = 0
Y_STOP = 5500.0                 # robot stops here (headland) and folds the wings
HOLD_START = 1.0                # s standing still before driving
HOLD_END = 2.0                  # s after the fold
TOP = 600.0                     # haulm top in the animation (just under the robot's beams at z 619)


def plants(x_range=X_FIELD, y_range=Y_FIELD, top=TOP, seed=None):
    """(x, y, top, size, sick) per plant on the ridges at 0, +-750, ... inside the ranges."""
    rnd = random.Random(SEED if seed is None else seed)
    out = []
    k0 = int(math.ceil(x_range[0] / P.row_pitch))
    k1 = int(math.floor(x_range[1] / P.row_pitch))
    for k in range(k0, k1 + 1):
        x = k * P.row_pitch
        y = y_range[0] + rnd.uniform(0, P.plant_pitch)
        while y < y_range[1]:
            sick = rnd.random() < SICK_SHARE
            out.append((x + rnd.uniform(-25, 25), y, top - rnd.uniform(0, 70), rnd.uniform(0.85, 1.08), sick))
            y += P.plant_pitch * rnd.uniform(0.85, 1.15)
    return out


def drive_time():
    return (Y_STOP - Y_START) / (P.speed * 1000.0)


def t_fold_start():
    return HOLD_START + drive_time()


def total_time():
    return t_fold_start() + C.fold_time() + HOLD_END


def robot_y(t):
    s = min(max(t - HOLD_START, 0.0), drive_time())
    return Y_START + s * P.speed * 1000.0


def beta(t):
    return min(P.fold, max(0.0, C.beta_at(t - t_fold_start()))) if t >= t_fold_start() else 0.0


def in_strip(x):
    return abs(x) <= P.half_width + 60.0     # jitter of the plants in the row


def frame_state(t, pl=None):
    pl = pl or plants()
    y = robot_y(t)
    cam_y = y + P.hood_yc
    seen = [p for p in pl if in_strip(p[0]) and p[1] <= cam_y]      # the rows behind the start were scanned on the way in
    sick = [p for p in seen if p[4]]
    moving = HOLD_START <= t < t_fold_start()
    fps = C.camera()["at"][1]["fps"]             # canopy at 600
    driven = (y - Y_START) / 1000.0
    if t < HOLD_START:
        phase = "start"
    elif moving:
        phase = "scout"
    elif t < t_fold_start() + C.fold_time():
        phase = "fold"
    else:
        phase = "done"
    return {"t": t, "y": y, "beta": beta(t), "phase": phase, "moving": moving, "seen": len(seen),
            "sick": [(p[0], p[1], p[2]) for p in sick], "images": int(P.n_cam * fps * driven / (P.speed)),
            "driven_m": driven, "area_m2": driven * 2 * P.half_width / 1000.0}


def summary():
    pl = plants()
    f = frame_state(total_time(), pl)
    strip = [p for p in pl if in_strip(p[0]) and p[1] <= f["y"] + P.hood_yc]
    return {"drive_s": round(drive_time(), 1), "fold_s": round(C.fold_time(), 1), "total_s": round(total_time(), 1),
            "plants_seen": f["seen"], "plants_in_strip": len(strip), "sick_found": len(f["sick"]),
            "images": f["images"], "area_m2": round(f["area_m2"], 1)}


if __name__ == "__main__":
    print(summary())
