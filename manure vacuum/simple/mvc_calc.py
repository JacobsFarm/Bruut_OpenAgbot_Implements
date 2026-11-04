"""Calculations of the manure vacuum collector (pure Python, no FreeCAD).

    import mvc_calc; mvc_calc.report()

Tank volume and fill time, alley length per fill, trips to the pit, the daily work for a herd, pump time to the
working vacuum, axle loads full, grip on the wet floor and energy.
"""
import math

import mvc_params as P


def fill():
    v = P.tank_litres()
    rate = P.manure_l_m2 * P.nozzle_w * P.speed            # l/s picked up
    t = v / rate
    alley = t * P.speed
    return {"litres": v, "kg": v * P.manure_density, "l_s": rate, "fill_s": t, "alley_m": alley}


def pump_down():
    """Seconds to evacuate the empty tank (air) to the working vacuum: isothermal, constant volume flow."""
    v = P.tank_litres() / 1000.0
    q = P.pump_m3h / 3600.0
    return v / q * math.log(1.0 / (1.0 - P.vacuum_bar))


def lift_height():
    """Height (m) of manure the vacuum can lift (static)."""
    return P.vacuum_bar * 1e5 / (P.manure_density * 1000.0 * P.g)


def day():
    per_day = P.cows * P.manure_cow_day * P.alley_share
    f = fill()
    trips = per_day / f["litres"]
    cycle = f["fill_s"] + 2 * P.pit_dist / P.transit + P.dump_s + pump_down()
    return {"l_day": per_day, "trips": trips, "cycle_s": cycle, "hours": trips * cycle / 3600.0}


def axle_loads():
    m_imp = P.MODEL_MASS["total_kg"]
    y_imp = P.MODEL_MASS["cg_y"]
    f = fill()
    tank_y = (P.tank_y[0] + P.tank_y[1]) / 2.0
    ya = -P.robot_axle_y
    L = 2 * P.robot_axle_y
    parts = [(P.robot_mass, 0.0), (m_imp, y_imp), (f["kg"], tank_y)]
    m = sum(p[0] for p in parts)
    front = sum(mi * (yi - ya) for mi, yi in parts) / L
    return {"total_kg": m, "front_kg": front, "rear_kg": m - front}


def grip():
    a = axle_loads()
    lift_on_robot = 0.6 * P.MODEL_MASS["lift_kg"]           # castors carry the rest of the head
    m = a["total_kg"] - (P.MODEL_MASS["lift_kg"] - lift_on_robot)
    g = P.mu_floor * m * P.g
    need = P.lip_drag + P.crr * a["total_kg"] * P.g
    return {"grip": g, "need": need, "margin": g / need}


def energy():
    d = day()
    drive = (P.crr * axle_loads()["total_kg"] * P.g + P.lip_drag) * P.speed / 0.75 + 80.0
    w = drive + P.pump_w + P.computer_w
    wh = w * d["hours"]
    return {"W": w, "Wh_day": wh, "charges_day": wh / P.battery_wh}


def report():
    f = fill()
    d = day()
    a = axle_loads()
    gr = grip()
    e = energy()
    lines = [
        "Manure vacuum collector (simple)",
        "  tank %.0f l (%.0f kg full); picks up %.2f l/s (%.1f l/m2 x %.1f m x %.2f m/s): full in %.0f s = %.0f m of alley"
        % (f["litres"], f["kg"], f["l_s"], P.manure_l_m2, P.nozzle_w, P.speed, f["fill_s"], f["alley_m"]),
        "  pump %.0f m3/h: %.0f s to %.1f bar vacuum; lifts manure up to %.1f m" % (P.pump_m3h, pump_down(), P.vacuum_bar, lift_height()),
        "  %d cows: %.0f l/day on the alleys = %.0f trips, cycle %.0f s (fill, %d m to the pit and back, dump): %.1f h/day"
        % (P.cows, d["l_day"], d["trips"], d["cycle_s"], P.pit_dist, d["hours"]),
        "  full: %.0f kg, front %.0f / rear %.0f kg" % (a["total_kg"], a["front_kg"], a["rear_kg"]),
        "  grip on the wet floor %.0f N for %.0f N (lip + rolling): margin %.1f" % (gr["grip"], gr["need"], gr["margin"]),
        "  energy %.0f W while collecting, %.0f Wh/day = %.1f charges a day" % (e["W"], e["Wh_day"], e["charges_day"]),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
