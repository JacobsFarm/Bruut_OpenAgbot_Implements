"""Calculations of the barn pressure washer (pure Python, no FreeCAD).

    import bpw_calc; bpw_calc.report()

Jet speed and reaction force (and what the tilt motor and the robot feel), surface per pen and time per pen, water
use, the hose length per reel, battery time (the pump is stationary), and why the pump is not on board.
"""
import math

import bpw_params as P


def jet():
    j = P.jet()
    up = j["force_N"] * math.sin(math.radians(60.0))       # floor pose: the reaction lifts the head
    return {"v": j["v"], "F": j["force_N"], "up_60": up}


def pen():
    L, W, H = P.pen
    floor = L * W
    walls = 2 * (L + W) * H
    area = floor + walls * 2                                   # partitions washed from both sides over the row
    t = area / P.clean_m2_min * 60.0 + P.pen_change_s
    water = P.q_lmin * (t - P.pen_change_s) / 60.0
    return {"area": area, "min": t / 60.0, "water_l": water}


def battery():
    w = P.reel_w * 0.3 + P.arm_w + P.drive_w * 0.2 + P.computer_w
    return {"W": w, "hours": P.battery_wh / w}


def onboard_pump():
    """Electric power of an on-board pump for the same jet (hydraulic power / efficiency 0.65)."""
    p_h = P.p_bar * 1e5 * P.q_lmin / 60000.0
    w = p_h / 0.65
    return {"hydraulic_W": p_h, "electric_W": w, "hours": P.battery_wh / (w + 100.0)}


def report():
    j = jet()
    p = pen()
    b = battery()
    o = onboard_pump()
    lines = [
        "Barn pressure washer (simple)",
        "  jet %.0f bar, %.0f l/min: %.0f m/s, reaction %.0f N along the lance (back toward the mast); at 60 deg down %.0f N up"
        % (P.p_bar, P.q_lmin, j["v"], j["F"], j["up_60"]),
        "  pen %.0f x %.0f m, walls %.0f m: %.0f m2, ~%.0f min and ~%.0f l of water per pen (%.1f m2/min)"
        % (P.pen[0], P.pen[1], P.pen[2], p["area"], p["min"], p["water_l"], P.clean_m2_min),
        "  hose %.0f m on the reel: pens within %.0f m of the stationary pump" % (P.hose_len, P.hose_len - 2.0),
        "  robot only drives, reels and aims: ~%.0f W, ~%.0f h per charge" % (b["W"], b["hours"]),
        "  an on-board pump would need %.0f W hydraulic, ~%.0f W electric: %.1f h per charge -> pump stays in the barn"
        % (o["hydraulic_W"], o["electric_W"], o["hours"]),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
