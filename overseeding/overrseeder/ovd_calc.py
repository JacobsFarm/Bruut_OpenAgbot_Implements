"""Calculations for the drop seeder (pure Python, no FreeCAD): hopper, metering roller and motor speed, on/off
timing with the camera look-ahead, camera footprint, draft, seed saved by spot seeding.

    import ovd_calc; ovd_calc.report()

The animation of "overseeder with cambridge roll" uses timing() and rpm_for() from here.
"""
import math

import ovd_params as P

G = 9.81


def hopper():
    litres = (2 * P.throat_v + 2 * P.top_v) / 2.0 * (P.top_z - P.throat_z) * P.width / 1e6
    kg = litres * P.seed_density
    return {"litres": litres, "seed_kg": kg, "m2_per_fill": kg * 1000.0 / P.seed_rate}


def ml_per_rev():
    """Volume carried by the flutes per revolution (ml)."""
    fw, fd = P.flute
    return P.flutes * fw * fd * P.width * P.roller_fill / 1000.0


def g_per_rev():
    return ml_per_rev() * P.seed_density


def rpm_for(speed=P.work_speed, rate=P.seed_rate):
    """Roller speed (rpm) for a seed rate (g/m2) at a driving speed (m/s)."""
    g_per_s = rate * speed * P.width / 1000.0
    return g_per_s / g_per_rev() * 60.0


def max_speed(rate=P.seed_rate):
    """Driving speed (m/s) at which the gearmotor reaches its full speed."""
    return P.gm_rpm / rpm_for(1.0, rate)


def fall_time():
    return math.sqrt(2.0 * P.fall_h / 1000.0 / G)


def timing(speed=P.work_speed):
    """Distances (mm) on the ground. The seed lands later than the command: motor start + fall time; it stops later
    by motor stop + fall time. The controller switches on 'lead_on' before the patch reaches the drop line and off
    'lead_off' before the end has passed, so the seed lands from on_margin before to off_margin after the patch."""
    v = speed * 1000.0
    t_on = P.motor_start + fall_time()
    t_off = P.motor_stop + fall_time()
    return {"t_on_s": t_on, "t_off_s": t_off, "lead_on_mm": v * t_on + P.on_margin,
            "lead_off_mm": v * t_off - P.off_margin, "look_ahead_mm": P.cam_use_v[0],
            "max_speed_m_s": (P.cam_use_v[0] - P.on_margin) / 1000.0 / t_on}


def camera_footprint():
    """Ground seen by the camera (v range and width at the near and far edge of the analysed strip)."""
    x, v, z = P.cam_pos
    hfov, vfov = P.cam_fov
    near = v + z * math.tan(math.radians(max(0.0, P.cam_pitch - vfov / 2.0)))
    far_angle = P.cam_pitch + vfov / 2.0
    far = v + z * math.tan(math.radians(min(80.0, far_angle)))

    def half_width(vg):
        dist = math.hypot(z, vg - v)
        return dist * math.tan(math.radians(hfov / 2.0))
    u0, u1 = P.cam_use_v
    return {"near_v": near, "far_v": far, "use_v": (u0, u1), "half_width_at_use": (half_width(u0), half_width(u1)),
            "cell": P.cell, "cells_across": int(P.width / P.cell)}


def spot_saving(bare_fraction, mean_patch_len_m=0.8):
    """Seed used by spot seeding as a fraction of seeding the whole strip: bare area + the margins before and after
    each patch (the strip is always 1 m wide, a patch is narrower)."""
    margin = (P.on_margin + P.off_margin) / 1000.0
    used = bare_fraction * (1.0 + margin / mean_patch_len_m) / max(0.3, min(1.0, mean_patch_len_m))
    return min(1.0, used)


def draft(trailer_kg, ball_N):
    return P.f_wheel * (trailer_kg * G - ball_N)


def report():
    h = hopper()
    print("Overseeder, simple drop seeder")
    print("  hopper %.0f l = %.1f kg seed at %.2f kg/l -> %.0f m2 of bare patch at %.0f g/m2"
          % (h["litres"], h["seed_kg"], P.seed_density, h["m2_per_fill"], P.seed_rate))
    print("  fluted roller O%d, %d flutes %gx%g: %.0f ml = %.0f g per revolution"
          % (P.roller_d, P.flutes, P.flute[0], P.flute[1], ml_per_rev(), g_per_rev()))
    for v in (0.3, P.work_speed, 0.8):
        print("    %.1f m/s: %.1f rpm for %.0f g/m2" % (v, rpm_for(v), P.seed_rate))
    print("  gearmotor %.0f rpm -> up to %.2f m/s at %.0f g/m2" % (P.gm_rpm, max_speed(), P.seed_rate))
    t = timing()
    print("  fall %.2f s; on %.2f s / off %.2f s after the command -> switch on %.0f mm before a patch, off %.0f mm "
          "before its end" % (fall_time(), t["t_on_s"], t["t_off_s"], t["lead_on_mm"], t["lead_off_mm"]))
    print("  camera looks %.0f mm ahead -> on/off in time up to %.2f m/s" % (t["look_ahead_mm"], t["max_speed_m_s"]))
    c = camera_footprint()
    print("  camera footprint v %.0f .. %.0f mm, analysed %.0f .. %.0f mm, half width %.0f / %.0f mm (needs 500)"
          % (c["near_v"], c["far_v"], c["use_v"][0], c["use_v"][1], c["half_width_at_use"][0],
             c["half_width_at_use"][1]))
    for frac in (0.05, 0.10, 0.20):
        print("  lawn with %2.0f %% bare: spot seeding uses %.0f %% of the seed of blanket seeding"
              % (frac * 100, 100 * spot_saving(frac)))
    return h
