"""Calculations of the insect vacuum (pure Python, no FreeCAD).

    import isv_calc; isv_calc.report()

Air speeds at the suction slots and in the canopy (Dallavalle slot formula), the air-knife jet across the bed (plane
jet decay), which insects are lifted, the fan pressure and power, the area per hour and per charge.
"""
import math

import isv_params as P


def slot_area():
    return 2 * P.slot_w * P.slot_l / 1e6                 # m2, both nozzles


def knife_area():
    return 2 * P.knife_slot[0] * P.knife_slot[1] / 1e6


def v_slot():
    return P.Q / slot_area()


def v_suction(x_mm):
    """Centre-line speed (m/s) at distance x in front of a plain slot (Dallavalle: Q = 3.7 L V x)."""
    q = P.Q / 2.0
    return q / (3.7 * P.slot_l / 1000.0 * x_mm / 1000.0)


def v_knife():
    return P.Q / knife_area()


def v_jet(x_mm):
    """Centre-line speed of the plane jet at distance x from the knife slot: u = 2.4 u0 sqrt(b / x) (x > 5 b)."""
    b = P.knife_slot[0]
    u0 = v_knife()
    return min(u0, 2.4 * u0 * math.sqrt(b / x_mm))


def fan():
    q = 0.5 * P.rho
    dp_slot = P.K_slot * q * v_slot() ** 2
    dp_knife = P.K_knife * q * v_knife() ** 2
    dp = dp_slot + P.dp_screen + P.dp_hoses + dp_knife
    w = P.Q * dp / P.eta_fan
    return {"dp_slot": dp_slot, "dp_knife": dp_knife, "dp_Pa": dp, "W": w}


def lifted():
    """For each insect: jet speed in the middle of the bed vs lift_factor x terminal velocity."""
    x_mid = P.knife_x - abs(P.crop_rows[0])               # knife to row
    v_row = v_jet(x_mid)
    v_far = v_jet(2 * P.knife_x - abs(P.crop_rows[0]))    # to the far row
    out = {}
    for name, (mg, mm, vt) in P.INSECTS.items():
        need = P.lift_factor * vt
        out[name] = {"need": need, "near_row": v_row >= need, "far_row": v_far >= need}
    return v_row, v_far, out


def work():
    f = fan()
    w = f["W"] + P.drive_w + P.computer_w
    area_h = P.speed * P.bed_pitch * 3600.0
    hours = P.battery_wh / w
    t_under = (P.hood_y[1] - P.hood_y[0]) / 1000.0 / P.speed
    return {"W": w, "m2_h": area_h, "hours": hours, "ha_charge": area_h * hours / 1e4, "s_under_hood": t_under}


def report():
    f = fan()
    v_row, v_far, li = lifted()
    wk = work()
    lines = [
        "Insect vacuum (simple)",
        "  air flow %.2f m3/s (closed loop: suction -> basket -> fan -> air knives)" % P.Q,
        "  suction slots 2 x %d x %d: %.1f m/s in the slot, %.1f m/s at 50 mm, %.1f m/s at 100 mm"
        % (P.slot_w, P.slot_l, v_slot(), v_suction(50.0), v_suction(100.0)),
        "  air knives 2 x %d x %d: %.0f m/s at the slot, jet %.1f m/s at the near row, %.1f m/s at the far row"
        % (P.knife_slot[0], P.knife_slot[1], v_knife(), v_row, v_far),
        "  lifted by the jet (>= %.0f x terminal velocity): %s" % (
            P.lift_factor, ", ".join("%s %s" % (k, "near+far" if v["far_row"] else ("near" if v["near_row"] else "no"))
                                     for k, v in li.items())),
        "  fan: slot %.0f + basket %.0f + hoses %.0f + knives %.0f = %.0f Pa, %.0f W at %.0f %%"
        % (f["dp_slot"], P.dp_screen, P.dp_hoses, f["dp_knife"], f["dp_Pa"], f["W"], 100 * P.eta_fan),
        "  %.1f m/s, bed pitch %.1f m: %.0f m2/h, %.1f s under the hood per plant"
        % (P.speed, P.bed_pitch, wk["m2_h"], wk["s_under_hood"]),
        "  %.0f W in all: %.1f h, %.2f ha per charge" % (wk["W"], wk["hours"], wk["ha_charge"]),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
