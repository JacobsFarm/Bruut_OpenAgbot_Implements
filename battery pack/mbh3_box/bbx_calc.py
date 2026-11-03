"""Battery rack MBH3+ - energy, runtime, current and charging per number of batteries (pure Python)."""
import bbx_params as P


def pack(n):
    wh = n * P.bat_wh()
    return {
        "n": n,
        "kwh": round(wh / 1000.0, 2),
        "kwh_usable": round(wh * P.dod / 1000.0, 2),
        "cells_kg": round(n * P.bat_kg, 1),
        "cont_a": n * P.bat_cont_a,
        "peak_a": n * P.bat_peak_a,
        # peak current of the robot with one battery out (hot-swap): must stay under the continuous rating
        "swap_margin_a": round((n - 1) * P.bat_cont_a - P.peak_bus_a, 0),
        "charge_h": round(P.bat_ah * 1.05 / P.charger_a, 1),
        "price_eur": round(n * P.bat_price_eur, 2),
    }


def runtime_h(n, load_w):
    return n * P.bat_wh() * P.dod / (load_w + P.base_load_w)


def report(ns=(2, 3, 4)):
    lines = []
    for n in ns:
        p = pack(n)
        lines.append("%d x MBH3+: %.2f kWh (%.2f usable), %.1f kg batteries, %d A cont / %d A peak, "
                     "hot-swap margin %+d A, EUR %.0f" % (n, p["kwh"], p["kwh_usable"], p["cells_kg"], p["cont_a"],
                                                          p["peak_a"], p["swap_margin_a"], p["price_eur"]))
    lines.append("runtime (h)        " + "  ".join("%5d" % n for n in ns))
    for name, w in P.LOADS_W.items():
        lines.append("%-18s %s" % (name[:18], "  ".join("%5.1f" % runtime_h(n, w) for n in ns)))
    lines.append("charging per battery at %.0f A: %.1f h" % (P.charger_a, pack(1)["charge_h"]))
    text = "\n".join(lines)
    print(text)
    return text
