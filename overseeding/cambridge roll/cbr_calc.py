"""Calculations for the Cambridge roll (pure Python, no FreeCAD): mass, load on the tow ball, line load, draft force,
pull the robot can deliver, shaft and bearings, capacity.

    import cbr_calc; cbr_calc.report()

The masses here come from the same parameters as the model (tube lengths x mass per metre, ring volume with
Pappus). build_cbr.mass_properties() measures them on the solids; both should agree within a few kg.
"""
import math

import cbr_params as P

G = 9.81


def tube_kg_per_m(w, h, t, dens=P.steel):
    return (w * h - (w - 2 * t) * (h - 2 * t)) * dens * 1000.0


def ring_kg():
    return P.ring_volume() * P.cast_iron


def drawbar_parts(cross_y):
    """(name, kg, y of the centre) of the drawbar group for a cross beam at cross_y."""
    y0, y1 = cross_y + P.cross_w, P.DRAWBAR_FRONT_Y
    bar = tube_kg_per_m(P.drawbar[0], P.drawbar[0], P.drawbar[1]) * (y1 - y0) / 1000.0
    dx = P.arm_x[1] - 70.0
    brace_len = math.hypot(dx, P.brace_y + 60.0)
    br = 2 * tube_kg_per_m(P.brace[0], P.brace[0], P.brace[1]) * brace_len / 1000.0
    leg = tube_kg_per_m(P.park_leg[0], P.park_leg[0], P.park_leg[1]) * P.park_leg[2] / 1000.0 + 0.6
    return [("drawbar", bar, (y0 + y1) / 2.0), ("braces", br, y0 + P.brace_y / 2.0),
            ("coupling", 3.5, P.ball[1] - 40.0), ("parking leg", leg, y1 - P.park_leg_y + 120.0)]


def frame_parts(axle_y=P.roll_axle_y, cross_y=P.cross_y):
    """(name, kg, y of the centre) of every group of the trailer."""
    rings = P.ring_n * ring_kg()
    shaft = math.pi / 4.0 * P.shaft_d ** 2 * 2 * P.shaft_x * P.steel
    sq = tube_kg_per_m(40.0, 40.0, P.rhs_t)
    arm_len = cross_y - (axle_y - P.side_plate_dy)
    plate = 2 * (2 * P.side_plate_dy) * (P.side_plate_z[1] - P.side_plate_z[0]) * 10.0 * P.steel * 0.93
    parts = [("rings", rings, axle_y), ("shaft + collars", shaft + 0.6, axle_y),
             ("side plates", plate, axle_y), ("bearings", 2 * P.bearing_kg + 0.4, axle_y),
             ("arms", 2 * sq * arm_len / 1000.0, (axle_y - P.side_plate_dy + cross_y) / 2.0),
             ("cross beam", sq * 2 * P.arm_x[1] / 1000.0, cross_y + P.cross_w / 2.0)]
    return parts + drawbar_parts(cross_y)


def trailer(parts=None, axle_y=P.roll_axle_y):
    parts = parts or frame_parts()
    m = sum(p[1] for p in parts)
    cg_y = sum(p[1] * p[2] for p in parts) / m
    ball = m * G * (cg_y - axle_y) / (P.ball[1] - axle_y)
    return {"mass_kg": m, "cg_y": cg_y, "ball_N": ball, "roll_N": m * G - ball}


def draft(mass_kg, ball_N, surface, slope_deg=0.0, roll_N=None):
    """Pull (N) on the ball: rolling resistance of the part carried by the roll + slope component of the whole
    trailer (uphill)."""
    roll_N = mass_kg * G - ball_N if roll_N is None else roll_N
    a = math.radians(slope_deg)
    return P.f_roll[surface] * roll_N * math.cos(a) + mass_kg * G * math.sin(a)


def robot_pull(ball_N, mu, slope_deg=0.0, f_robot=0.08):
    """Pull the robot can deliver on the ball: traction of the 4 driven wheels minus its own rolling resistance and
    slope (uphill)."""
    a = math.radians(slope_deg)
    w = P.robot_mass * G + ball_N
    return mu * w * math.cos(a) - f_robot * w * math.cos(a) - P.robot_mass * G * math.sin(a)


def shaft_stress(roll_N, ring_total_kg):
    """Bending of the shaft: the frame load (what the roll carries minus the rings) is pushed up by the rings over
    1000 mm and held by the bearings at the side plates (simply supported)."""
    F = max(0.0, roll_N - ring_total_kg * G)
    span = 2 * (P.side_plate_x[1] + P.bearing_flange[2] + P.bearing_boss[1] / 2.0)
    c = P.roll_x[1] - P.roll_x[0]
    M = F / 8.0 * (2 * span - c)
    W = math.pi * P.shaft_d ** 3 / 32.0
    return {"frame_load_N": F, "bearing_N": F / 2.0, "span_mm": span, "M_Nmm": M, "sigma_MPa": M / W}


def contact(roll_N):
    """Line load and ground pressure of the ridges (estimated contact patch: ridge tip + sinkage)."""
    width_m = (P.roll_x[1] - P.roll_x[0]) / 1000.0
    out = {"line_load_kg_per_m": roll_N / G / width_m}
    for sink in (5.0, 15.0):
        # chord of the ring at this sinkage x the width of the ridge at that depth
        r = P.ring_od / 2.0
        chord = 2.0 * math.sqrt(2 * r * sink - sink * sink)
        a0, a1, t0, t1 = P.ring_ridge
        h = r - P.ring_rim_r[1]
        w = (t1 - t0) + ((a1 - a0) - (t1 - t0)) * min(1.0, sink / h)
        area = P.ring_n * chord * w * 0.5            # half: the patch is a lens, not a rectangle
        out["pressure_kPa_at_%dmm" % sink] = roll_N / area * 1000.0
    return out


def capacity():
    v = P.work_speed
    w = (P.roll_x[1] - P.roll_x[0]) / 1000.0
    return {"m2_per_h": v * w * 3600.0 * P.field_eff, "ha_per_h": v * w * 3600.0 * P.field_eff / 10000.0}


def report():
    parts = frame_parts()
    tr = trailer(parts)
    print("Cambridge roll, simple")
    print("  ring: %.2f kg (OD %d, width %d), %d rings = %.0f kg" % (ring_kg(), P.ring_od, P.ring_w, P.ring_n,
                                                                     P.ring_n * ring_kg()))
    for name, kg, y in parts:
        print("    %-16s %6.1f kg  at y %6.0f" % (name, kg, y))
    print("  trailer %.0f kg, centre of gravity y %.0f; on the ball %.0f N (%.1f kg), on the roll %.0f N"
          % (tr["mass_kg"], tr["cg_y"], tr["ball_N"], tr["ball_N"] / G, tr["roll_N"]))
    c = contact(tr["roll_N"])
    print("  line load %.0f kg/m; ridge pressure %.0f kPa at 5 mm sinkage, %.0f kPa at 15 mm"
          % (c["line_load_kg_per_m"], c["pressure_kPa_at_5mm"], c["pressure_kPa_at_15mm"]))
    for surf in P.f_roll:
        print("  draft on %-28s %4.0f N level, %4.0f N up %g deg"
              % (surf, draft(tr["mass_kg"], tr["ball_N"], surf), draft(tr["mass_kg"], tr["ball_N"], surf, P.slope_deg),
                 P.slope_deg))
    for mu in P.robot_mu:
        print("  robot pull at mu %.2f: %4.0f N level, %4.0f N up %g deg"
              % (mu, robot_pull(tr["ball_N"], mu), robot_pull(tr["ball_N"], mu, P.slope_deg), P.slope_deg))
    s = shaft_stress(tr["roll_N"], P.ring_n * ring_kg())
    print("  shaft O%d: frame load %.0f N, %.0f N per bearing, bending %.1f MPa" % (P.shaft_d, s["frame_load_N"],
                                                                                    s["bearing_N"], s["sigma_MPa"]))
    cap = capacity()
    worst = draft(tr["mass_kg"], tr["ball_N"], "loose seedbed (bare patch)", P.slope_deg)
    print("  capacity %.0f m2/h at %.1f m/s; extra drive power %.0f W (worst case %.0f N)"
          % (cap["m2_per_h"], P.work_speed, worst * P.work_speed, worst))
    return tr
