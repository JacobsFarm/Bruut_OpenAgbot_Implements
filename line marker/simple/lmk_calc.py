"""Calculations of the sports field line marker (pure Python, no FreeCAD).

    import lmk_calc; lmk_calc.report()

Line lengths of the football and hockey layouts, paint use, time per field, line accuracy at the nozzle (error budget),
how the curves are drawn (steering on the rear-axle point, or chord + slide for the corner arcs), the slide drive and
the energy.
"""
import math

import lmk_params as P


# ---------------------------------------------------------------------
# Layouts: list of (kind, length m) per element
# ---------------------------------------------------------------------
def football_elements(f=None):
    f = f or P.FOOTBALL
    L, W = f["length"], f["width"]
    pen_half = math.degrees(math.acos((f["pen_depth"] - f["pen_spot"]) / f["arc_r"]))
    els = [("straight", L)] * 2 + [("straight", W)] * 2 + [("straight", W)]               # touch, goal, halfway
    els += [("straight", f["pen_depth"])] * 4 + [("straight", f["pen_width"])] * 2      # penalty areas
    els += [("straight", f["goal_depth"])] * 4 + [("straight", f["goal_width"])] * 2    # goal areas
    els += [("circle", 2 * math.pi * f["centre_r"])]
    els += [("arc", math.radians(2 * pen_half) * f["arc_r"])] * 2                       # penalty arcs
    els += [("corner", 0.5 * math.pi * f["corner_r"])] * 4
    els += [("spot", 0.0)] * 3                                                          # centre + 2 penalty spots
    return els


def hockey_elements(h=None):
    h = h or P.HOCKEY
    L, W, r = h["length"], h["width"], h["circle_r"]
    gw = h["goal_w"]
    els = [("straight", L)] * 2 + [("straight", W)] * 2 + [("straight", W)] + [("straight", W)] * 2   # + 23 m lines
    # shooting circle: 2 quarter circles r 14.63 round the posts + a straight of the goal width
    els += [("arc", 0.5 * math.pi * r)] * 4 + [("straight", gw)] * 2
    return els


def line_total(els):
    return sum(l for _, l in els)


# ---------------------------------------------------------------------
# Paint
# ---------------------------------------------------------------------
def paint_rate(w=None, v=None):
    """l/m2 of ready mix at the tip flow, line width w (mm) and speed v (m/s)."""
    w = (P.line_w["football"] if w is None else w) / 1000.0
    v = P.speed_paint if v is None else v
    return P.tip_flow() / 60.0 / (v * w)


def paint_per_field(els, w=None, v=None):
    v = P.speed_paint if v is None else v
    q = P.tip_flow() / 60.0                                 # l/s
    t = 0.0
    for k, l in els:
        if k == "spot":
            t += 1.5                                        # spot: 1.5 s stand still, nozzle rotating disc 200 mm
        else:
            t += l / (P.speed_curve if k in ("circle", "arc", "corner") else v)
    return q * t


# ---------------------------------------------------------------------
# Time per field
# ---------------------------------------------------------------------
def field_time(els, transit_m=None):
    """s: painting + line ends + transit between elements (transit ~ 25 % of the line length, estimated)."""
    paint = 0.0
    for k, l in els:
        if k == "spot":
            paint += 1.5
        elif k == "corner":
            paint += corner_arc()["time_s"]
        elif k in ("circle", "arc"):
            paint += l / P.speed_curve
        else:
            paint += l / P.speed_paint
    transit_m = 0.25 * line_total(els) if transit_m is None else transit_m
    ends = len(els) * P.turn_s
    return {"paint_s": paint, "ends_s": ends, "transit_s": transit_m / P.speed_transit,
            "total_s": paint + ends + transit_m / P.speed_transit}


# ---------------------------------------------------------------------
# Curves
# ---------------------------------------------------------------------
def steer_for_radius(r_m):
    """Front steering angle (deg) for a circle of radius r (m) of the rear-axle midpoint (= the nozzle)."""
    return math.degrees(math.atan(P.robot_wheelbase / 1000.0 / r_m))


def min_radius():
    return P.robot_wheelbase / 1000.0 / math.tan(math.radians(P.robot_steer_max))


def corner_arc(r_m=None, angle_deg=90.0):
    """Corner arc drawn with the robot driving straight along the chord and the slide following the arc.
    The chord is shifted half the sagitta toward the arc, so the slide moves +-sagitta/2 around its middle."""
    r = (P.FOOTBALL["corner_r"] if r_m is None else r_m) * 1000.0
    half = math.radians(angle_deg / 2.0)
    chord = 2 * r * math.sin(half)
    sag = r * (1 - math.cos(half))
    # slide speed: offset s(y) = sqrt(r^2 - y^2) - r cos(half); ds/dy = -y / sqrt(r^2-y^2), max at the ends = tan(half)
    v_robot = P.mod_speed / math.tan(half)                  # mm/s, slide at its set speed at the arc ends
    t = chord / v_robot
    return {"chord_mm": chord, "sagitta_mm": sag, "slide_needed_mm": sag, "stroke_mm": P.stroke,
            "fits": sag <= P.stroke - 2 * 20.0, "v_robot_mm_s": v_robot, "time_s": t}


def tightest_arc_by_slide(angle_deg=90.0, margin=20.0):
    """Largest radius whose sagitta still fits the stroke (chord + slide method)."""
    half = math.radians(angle_deg / 2.0)
    return (P.stroke - 2 * margin) / (1 - math.cos(half)) / 1000.0


# ---------------------------------------------------------------------
# Accuracy at the nozzle (1 sigma, mm)
# ---------------------------------------------------------------------
def accuracy():
    ax, ay, az = P.robot_gnss
    lever = abs(ay - P.nozzle_y)                            # 1075 mm antenna -> nozzle along y
    h_ant = az                                              # antenna height over the ground
    e_rtk = P.rtk_h
    e_head = lever * math.radians(P.heading_err)
    e_tilt = h_ant * math.radians(P.tilt_err)               # roll residual moves the antenna sideways
    e_slide = P.slide_err
    e_lag = 0.05 * P.odo_lag_ms                             # cross-track drift ~50 mm/s on turf x lag (estimated)
    rss = math.sqrt(e_rtk ** 2 + e_head ** 2 + e_tilt ** 2 + e_slide ** 2 + e_lag ** 2)
    roll_uncorr = h_ant * math.sin(math.radians(3.0))
    ends = P.speed_paint * P.valve_jitter_ms                # mm spread of the line ends (timing compensated)
    no_comp = P.speed_paint * P.valve_ms[0]                 # mm a line start would be late without look-ahead
    return {"rtk": e_rtk, "heading": e_head, "tilt": e_tilt, "slide": e_slide, "lag": e_lag, "rss_1s": rss,
            "rss_95": 2 * rss, "roll_3deg_uncorrected": roll_uncorr, "line_end_spread": ends,
            "line_start_late_no_lookahead": no_comp}


# ---------------------------------------------------------------------
# Slide drive
# ---------------------------------------------------------------------
HEAD_KG = 3.2                                               # carriage + head + half the chain + paint in the head (est.)


def slide_drive(head_kg=HEAD_KG):
    f_acc = head_kg * P.mod_acc / 1000.0                    # N
    f_fric = 15.0                                           # N carriage + chain friction (estimated)
    f = f_acc + f_fric
    torque = f * P.pulley_pd / 2000.0
    rpm = P.mod_speed / (math.pi * P.pulley_pd) * 60.0
    return {"force_N": f, "torque_Nm": torque, "reserve": P.nema_torque_run / torque, "rpm": rpm}


# ---------------------------------------------------------------------
# Energy, axle loads
# ---------------------------------------------------------------------
def energy(field_s):
    w = P.drive_w + P.computer_w + P.pump_w + P.slide_w
    wh = w * field_s / 3600.0
    return {"W": w, "Wh_field": wh, "fields_per_charge": P.battery_wh / wh}


def axle_loads(paint_l=None):
    paint_l = P.paint_fill_l if paint_l is None else paint_l
    m_imp = P.MODEL_MASS["total_kg"]
    cg_y = P.MODEL_MASS["cg"][1]
    m_paint = paint_l * P.paint_density
    paint_y = (P.S.tank_y[0] + P.S.tank_y[1]) / 2.0
    m = P.robot_kg + m_imp + m_paint
    my = P.robot_kg * 0.0 + m_imp * cg_y + m_paint * paint_y
    yc = my / m
    front = m * (yc + P.robot_axle_y) / (2 * P.robot_axle_y)
    return {"total_kg": m, "cg_y": yc, "front_kg": front, "rear_kg": m - front, "front_share": front / m}


def report():
    fb = football_elements()
    hk = hockey_elements()
    tf = field_time(fb)
    th = field_time(hk)
    pf = paint_per_field(fb)
    ph = paint_per_field(hk, w=P.line_w["hockey"])
    acc = accuracy()
    ca = corner_arc()
    sd = slide_drive()
    en = energy(tf["total_s"])
    ax = axle_loads()
    lines = [
        "Sports field line marker (simple)",
        "  football 105 x 68: %.0f m of line, %d elements; hockey: %.0f m" % (line_total(fb), len(fb), line_total(hk)),
        "  tip 4002E at %.1f bar: %.2f l/min, line %d mm at tip %d mm, %.3f l/m2 at %.1f m/s"
        % (P.spray_p, P.tip_flow(), round(P.line_width()), P.tip_z, paint_rate(), P.speed_paint),
        "  tip heights %s -> widths %s mm" % (P.tip_steps, [round(P.line_width(h)) for h in P.tip_steps]),
        "  paint per field: football %.1f l, hockey %.1f l ready mix; %.0f l fill = %.1f football fields"
        % (pf, ph, P.paint_fill_l, P.paint_fill_l / pf),
        "  time football: paint %.0f s, line ends %.0f s, transit %.0f s = %.0f min"
        % (tf["paint_s"], tf["ends_s"], tf["transit_s"], tf["total_s"] / 60.0),
        "  time hockey: %.0f min" % (th["total_s"] / 60.0),
        "  curves: centre circle r 9.15 -> steering %.1f deg; min radius by steering %.2f m"
        % (steer_for_radius(9.15), min_radius()),
        "  corner arc r 1: chord %.0f mm, sagitta %.0f mm (stroke %.0f, fits %s), robot %.0f mm/s, %.1f s"
        % (ca["chord_mm"], ca["sagitta_mm"], ca["stroke_mm"], ca["fits"], ca["v_robot_mm_s"], ca["time_s"]),
        "  largest quarter arc by slide alone: r %.2f m (tighter than steering above %.2f m)"
        % (tightest_arc_by_slide(), min_radius()),
        "  accuracy 1 sigma: RTK %.1f, heading %.1f, tilt %.1f, slide %.1f, lag %.1f -> %.1f mm (95 %% ~ %.0f mm)"
        % (acc["rtk"], acc["heading"], acc["tilt"], acc["slide"], acc["lag"], acc["rss_1s"], acc["rss_95"]),
        "  3 deg roll uncorrected: %.0f mm; line-end spread %.0f mm; start late without look-ahead %.0f mm"
        % (acc["roll_3deg_uncorrected"], acc["line_end_spread"], acc["line_start_late_no_lookahead"]),
        "  slide: %.1f N, %.3f Nm (reserve %.0fx), %.0f rpm" % (sd["force_N"], sd["torque_Nm"], sd["reserve"], sd["rpm"]),
        "  energy: %.0f W, %.0f Wh per football field, %.1f fields per charge"
        % (en["W"], en["Wh_field"], en["fields_per_charge"]),
        "  axle loads with %.0f l paint: total %.0f kg, front %.0f kg / rear %.0f kg (%.0f %% front)"
        % (P.paint_fill_l, ax["total_kg"], ax["front_kg"], ax["rear_kg"], 100 * ax["front_share"]),
    ]
    text = "\n".join(lines)
    print(text)
    return text


if __name__ == "__main__":
    report()
