"""Calculations for the overseeder with Cambridge roll (pure Python, no FreeCAD): mass and ball load, draft and the
pull of the robot, turning (smallest radius, articulation and off-tracking of the roll), on/off timing.

    import osr_calc; osr_calc.report()

The animation reads turn_geometry() and the timing from ovd_calc, so the report and the animation agree.
"""
import math

import osr_params as P
import cbr_calc as CC
import ovd_calc as OC

G = 9.81


def parts(seed=True):
    out = CC.frame_parts(P.axle_y, P.cross_y)
    out.append(("seeder unit", P.O.unit_kg, P.unit_y + 20.0))
    out.append(("hangers", 0.9, P.unit_y))
    if seed:
        out.append(("seed (full hopper)", OC.hopper()["seed_kg"], P.unit_y))
    return out


def trailer(seed=True):
    return CC.trailer(parts(seed), P.axle_y)


def min_radius():
    """Smallest radius of the rear axle centre: inner front wheel at the steering stop (Ackermann)."""
    return P.C.robot_wheelbase / math.tan(math.radians(P.C.robot_max_steer)) + P.C.robot_track / 2.0


def steering(radius):
    """Steering angles (deg) of the inner and outer front wheel for a radius of the rear axle centre."""
    L, w = P.C.robot_wheelbase, P.C.robot_track
    return (math.degrees(math.atan(L / (radius - w / 2.0))), math.degrees(math.atan(L / (radius + w / 2.0))))


def turn_geometry(radius):
    """Steady turn: radius of the ball, radius of the roll centre, articulation and off-tracking (roll inside)."""
    a, L = P.hitch_behind_axle, P.L_roll
    r_h = math.hypot(radius, a)
    r_t = math.sqrt(max(0.0, r_h * r_h - L * L))
    gamma = math.degrees(math.atan(a / radius) + math.atan2(L, r_t))
    r_d = math.hypot(r_t, P.L_roll - P.L_drop)         # the drop line lies on the trailer axis, in front of the roll
    return {"r_ball": r_h, "r_roll": r_t, "r_drop": r_d, "articulation_deg": gamma, "offtrack_mm": radius - r_t}


def report():
    print("Overseeder with Cambridge roll")
    full, empty = trailer(True), trailer(False)
    for name, kg, y in parts():
        print("    %-20s %6.1f kg  at y %6.0f" % (name, kg, y))
    for tag, t in (("empty", empty), ("full", full)):
        print("  trailer %-5s %.0f kg, cg y %.0f: ball %.0f N (%.1f kg), roll %.0f N (%.0f kg/m)"
              % (tag, t["mass_kg"], t["cg_y"], t["ball_N"], t["ball_N"] / G, t["roll_N"], t["roll_N"] / G))
    for surf in P.C.f_roll:
        print("  draft on %-28s %4.0f N level, %4.0f N up %g deg"
              % (surf, CC.draft(full["mass_kg"], full["ball_N"], surf),
                 CC.draft(full["mass_kg"], full["ball_N"], surf, P.C.slope_deg), P.C.slope_deg))
    for mu in P.C.robot_mu:
        print("  robot pull at mu %.2f: %4.0f N level, %4.0f N up %g deg"
              % (mu, CC.robot_pull(full["ball_N"], mu), CC.robot_pull(full["ball_N"], mu, P.C.slope_deg),
                 P.C.slope_deg))
    r = min_radius()
    print("  smallest turn: rear axle radius %.0f mm (steering %.1f / %.1f deg)" % ((r,) + steering(r)))
    for radius in (r, 2250.0, 3000.0):
        t = turn_geometry(radius)
        print("    R %.0f: articulation %.0f deg, roll centre radius %.0f -> runs %.0f mm inside the robot track"
              % (radius, t["articulation_deg"], t["r_roll"], t["offtrack_mm"]))
    t = OC.timing()
    print("  drop -> roll %.0f mm = %.1f s at %.1f m/s; switch on %.0f mm before a patch, off %.0f mm before the end"
          % (P.drop_to_roll, P.drop_to_roll / 1000.0 / P.O.work_speed, P.O.work_speed, t["lead_on_mm"],
             t["lead_off_mm"]))
    cap = CC.capacity()
    print("  capacity %.0f m2/h; hopper %.0f l lasts %.0f m2 of bare soil" % (cap["m2_per_h"], OC.hopper()["litres"],
                                                                            OC.hopper()["m2_per_fill"]))
    return full
