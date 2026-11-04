"""Calculations of the hedge trimmer and leaf blower (pure Python, no FreeCAD).

    import hdg_calc; hdg_calc.report()

Reach of the bar (side and top cut), cutting speed vs stroke rate, hedge length per hour and per charge, blower air
speed on the path, tipping of the robot with the arm out, noise.
"""
import math

import hdg_params as P


def reach():
    lo, hi = P.z_range
    hz = P.housing[2] / 2.0
    side = (lo + hz, hi + hz + P.bar_len)                   # bar up from the housing top
    top_max = hi - 30.0                                       # bar along +x at the axis height - 30
    x_top = P.tilt_x + P.housing_dx + P.housing[0] / 2.0 + P.bar_len
    return {"side_z": side, "top_z_max": top_max, "top_x": (P.tilt_x + 80.0, x_top)}


def cutting():
    v = P.speed_side * 1000.0                                 # mm/s
    strokes_s = P.strokes_min / 60.0
    feed_per_stroke = v / strokes_s
    return {"feed_mm": feed_per_stroke, "ok": feed_per_stroke < P.tooth_pitch / 2.0}


def hedge_rate():
    """m of hedge per hour: one pass per side (face 0.9 m high per pass), one pass for the top."""
    passes_side = math.ceil(P.hedge_h * 1000.0 / P.cut_w)
    passes_top = math.ceil(P.hedge_top_w * 1000.0 / P.cut_w)
    passes = 2 * passes_side + passes_top
    m_h = P.speed_side * 3600.0 / passes
    w = P.trim_w + P.tilt_w + P.drive_w + P.computer_w
    hours = P.battery_wh / w
    return {"passes": passes, "m_h": m_h, "W": w, "hours": hours, "m_charge": m_h * hours}


def blower():
    """Air speed on the path at the distance of the nozzle (free round jet: u = 6.2 u0 d / x)."""
    d0 = P.nozzle_d[1] / 1000.0
    x = 0.6
    u = min(P.blow_v, 6.2 * P.blow_v * d0 / x)
    hours = P.battery_wh / (P.blow_w + P.drive_w + P.computer_w)
    return {"u_path": u, "moves_leaves": u >= P.leaf_lift_v, "hours_full": hours}


def tipping(m_arm=7.0 + 12.4, x_arm=900.0):
    """Moment of the arm and trimmer about the right wheel line (x 375) against the robot."""
    m_r = P.robot_mass + 19.2 + 4.8
    stab = m_r * 375.0
    tip = m_arm * (x_arm - 375.0)
    return {"ratio": stab / tip}


def report():
    r = reach()
    c = cutting()
    h = hedge_rate()
    b = blower()
    t = tipping()
    lines = [
        "Hedge trimmer and leaf blower (simple)",
        "  side cut: bar from z %.0f to %.0f (arm %.0f .. %.0f); top cut up to z %.0f, x %.0f .. %.0f"
        % (r["side_z"][0], r["side_z"][1], P.z_range[0], P.z_range[1], r["top_z_max"], r["top_x"][0], r["top_x"][1]),
        "  %.2f m/s at %d strokes/min: %.1f mm feed per stroke (teeth %d mm): %s"
        % (P.speed_side, P.strokes_min, c["feed_mm"], P.tooth_pitch, "clean cut" if c["ok"] else "too fast"),
        "  hedge %.2f m high, %.1f m wide: %d passes, %.0f m of hedge per hour; %.0f W, %.1f h, ~%.0f m per charge"
        % (P.hedge_h, P.hedge_top_w, h["passes"], h["m_h"], h["W"], h["hours"], h["m_charge"]),
        "  blower %.0f m/s at the nozzle, ~%.0f m/s on the path 0.6 m away (moves wet leaves: %s); %.1f h at full power"
        % (P.blow_v, b["u_path"], b["moves_leaves"], b["hours_full"]),
        "  arm and trimmer out at x ~900: stability %.0fx against tipping over the right wheels" % t["ratio"],
        "  noise at 7 m: blower ~%d dB(A), trimmer ~%d dB(A) (estimated)" % P.noise_dba_7m,
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
