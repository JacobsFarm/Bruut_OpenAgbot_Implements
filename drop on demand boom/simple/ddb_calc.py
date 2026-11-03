"""Calculations for the drop-on-demand boom, in pure Python (same parameters as the model).

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" -B ddb_calc.py      (or in FreeCAD: import ddb_calc; ddb_calc.report())

Camera footprint and resolution, timing from image to drop (latency budget), aiming error, drop flight, dose per weed
and per hectare against a broadcast pass, flow and pump, firing rate, capacity and battery, axle loads.
Masses come from build_ddb.mass_properties() (copied into ddb_params.MODEL_MASS after a rebuild).
"""
import math

import ddb_params as P

ROBOT_CG = (0.0, 95.0, 543.0)       # agbot comparison (estimated), as in ssp_calc


def lens_z():
    """Height of the lens above the ground at the middle step (same numbers as ddb_parts)."""
    top_in = P.hood_top - P.hood_t
    return top_in - 20.0 - P.cam_box[2] - P.cam_lens[1]


def camera():
    """Ground footprint (mm, long side across), resolution (mm/px), the part of the image inside the hood and the
    motion blur in one exposure."""
    h = lens_z()
    sw, sh = P.cam_px[0] * P.cam_pixel, P.cam_px[1] * P.cam_pixel
    w, ln = h * sw / P.cam_f, h * sh / P.cam_f
    cy = P.cam_xy[1]
    y0, y1 = cy - ln / 2.0, cy + ln / 2.0
    inner = (max(y0, P.hood_y[0] + P.hood_t), min(y1, P.hood_y[1] - P.hood_t))
    gsd = h * P.cam_pixel / P.cam_f
    blur = P.speed * P.exposure_ms                  # mm (m/s x ms)
    # the injector line must not be in the image (drops would be seen as weeds) and the image must cover the bed
    return {"lens_z": round(h), "width_mm": round(w), "length_mm": round(ln), "view_y": (round(y0), round(y1)),
            "view_in_hood_y": (round(inner[0]), round(inner[1])), "gsd_mm_px": round(gsd, 2),
            "blur_mm": round(blur, 3), "covers_bed": w >= P.work_width, "injectors_out_of_view": P.inj_y < y0}


def latency():
    """Time budget from the first image of a weed to the drop: the weed enters the image at its front edge and the
    injector line is 'gap' behind it. Detection is done on every frame; the drop is fired at the planned time."""
    c = camera()
    gap = c["view_in_hood_y"][1] - P.inj_y              # mm from first sight to the injector line
    t_avail = gap / P.speed / 1000.0
    frame = 1.0 / P.cam_fps
    # worst case: weed comes in just after a frame, needs 2 frames to be sure (track), inference, valve driver
    t_need = 2.0 * frame + P.infer_ms / 1000.0 + 0.010
    seen = c["view_in_hood_y"][1] - c["view_in_hood_y"][0]
    frames_seen = seen / P.speed / 1000.0 * P.cam_fps
    return {"gap_mm": round(gap), "t_avail_s": round(t_avail, 2), "t_need_s": round(t_need, 3),
            "margin_s": round(t_avail - t_need, 2), "frames_per_weed": round(frames_seen, 1),
            "max_speed_m_s": round(gap / 1000.0 / t_need, 2)}


def drop_flight():
    """Fall of a drop from the tip to the ground (no air drag, inside the hood: no wind). The drop leaves with the
    robot's forward speed, so it lands straight under the tip; only the time is needed."""
    v0 = P.drop_v0
    h = P.tip_z / 1000.0
    t = (-v0 + math.sqrt(v0 * v0 + 2 * P.g * h)) / P.g
    v_hit = v0 + P.g * t
    d = P.drop_d()
    # splash check: Weber number on a leaf (water, sigma 0.072 N/m); above ~ 80..100 the drop shatters
    we = 1000.0 * v_hit ** 2 * d / 1000.0 / 0.072
    return {"drop_d_mm": round(d, 2), "fall_ms": round(t * 1000.0, 1), "v_impact_m_s": round(v_hit, 2),
            "weber": round(we), "splash_risk": we > 100.0}


def aiming():
    """Error (mm) of the drop on the ground along y (odometry over the gap, valve jitter, frame position) and across
    (half the injector pitch, at worst)."""
    gap = latency()["gap_mm"]
    odo = P.odo_err * gap
    jit = P.speed * P.jitter_ms
    pix = 2.0 * camera()["gsd_mm_px"]
    along = math.sqrt(odo ** 2 + jit ** 2 + pix ** 2)
    across = P.inj_pitch / 2.0
    lead = P.speed * drop_flight()["fall_ms"]           # fired this much early: the drop keeps the forward speed
    return {"flight_lead_mm": round(lead, 1), "odometry_mm": round(odo, 2), "jitter_mm": round(jit, 2), "image_mm": round(pix, 2),
            "along_mm": round(along, 2), "across_max_mm": across, "smallest_weed_hit_mm": round(2 * across)}


def drops_per_weed(d):
    """Drops on one weed of leaf diameter d: grid of inj_pitch (across) x drop_grid (along), at least one."""
    n_x = max(1, int(round(d / P.inj_pitch)))
    n_y = max(1, int(round(d / P.drop_grid)))
    # drops in the circle of the grid
    return max(1, int(round(n_x * n_y * math.pi / 4.0))) if n_x * n_y > 2 else n_x * n_y


def dose():
    """Liquid per weed and per hectare against a broadcast pass over the whole bed."""
    d_small, d_big = P.weed_d
    d_mid = 0.5 * (d_small + d_big)
    per = {"small": drops_per_weed(d_small), "mid": drops_per_weed(d_mid), "big": drops_per_weed(d_big)}
    ul_mid = per["mid"] * P.drop_ul
    l_ha = P.weed_density * 1e4 * ul_mid * 1e-6
    return {"drops": per, "ul_per_weed_mid": ul_mid, "l_ha": round(l_ha, 2),
            "blanket_l_ha": P.blanket_rate, "saving": round(1.0 - l_ha / P.blanket_rate, 4),
            "ha_per_fill": round(P.fill_l / l_ha, 1)}


def firing():
    """Firing rate of one injector at the drop grid and the speed, against its maximum; peak flow if all 24 fire."""
    hz = P.speed * 1000.0 / P.drop_grid
    peak_l_min = P.n_inj * hz * P.drop_ul * 1e-6 * 60.0
    weed_rate = P.weed_density * P.work_width / 1000.0 * P.speed       # weeds per second under the rail
    mean_l_min = weed_rate * dose()["ul_per_weed_mid"] * 1e-6 * 60.0
    duty = hz * P.open_ms / 1000.0
    return {"hz": round(hz), "hz_max": P.fire_hz_max, "ok": hz <= P.fire_hz_max, "duty": round(duty, 3),
            "peak_l_min": round(peak_l_min, 3), "pump_l_min": P.S.pump_q_3bar, "pump_ok": peak_l_min < P.S.pump_q_3bar,
            "weeds_s": round(weed_rate, 1), "mean_ml_min": round(mean_l_min * 1000.0, 1),
            "max_speed_m_s": round(P.fire_hz_max * P.drop_grid / 1000.0, 1)}


def power():
    """Electric power (W): drive, computer + camera, LEDs, pump on its duty, injectors in use."""
    f = firing()
    in_use = min(P.n_inj, f["weeds_s"] * 3.0 * 0.2 + 1.0)     # ~3 injectors per weed, 0.2 s each (estimated)
    pump = P.S.pump_w * P.pump_duty
    w = P.drive_w + P.computer_w + P.led_w + pump + in_use * P.inj_w
    return {"drive_W": P.drive_w, "computer_W": P.computer_w, "led_W": P.led_w, "pump_W": round(pump),
            "injectors_W": round(in_use * P.inj_w, 1), "total_W": round(w)}


def capacity():
    ha_h = P.work_width / 1000.0 * P.speed * 3600.0 / 1e4 * P.field_eff
    w = power()["total_W"]
    hours = P.battery_wh / w
    bed_m = P.speed * 3600.0 * P.field_eff
    return {"ha_h": round(ha_h, 3), "bed_m_h": round(bed_m), "hours": round(hours, 1), "ha_per_charge": round(ha_h * hours, 2),
            "bed_m_per_charge": round(bed_m * hours)}


def axle_loads(litres=P.fill_l):
    """Front and rear axle load (kg) with the tank filled to 'litres' (liquid centre over the tank)."""
    m = P.MODEL_MASS
    tank_y = 0.5 * (P.S.tank_y[0] + P.S.tank_y[1])
    items = [(P.robot_kg, ROBOT_CG[1]), (m["total_kg"], m["cg"][1]), (litres * P.liquid_density, tank_y)]
    total = sum(k for k, _ in items)
    moment = sum(k * (y + P.robot_axle_y) for k, y in items)
    front = moment / (2.0 * P.robot_axle_y)
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "rear_share": round((total - front) / total, 3), "per_wheel_max_kg": round(max(front, total - front) / 2.0, 1)}


def report():
    out = {"camera": camera(), "latency": latency(), "drop": drop_flight(), "aiming": aiming(), "dose": dose(),
           "firing": firing(), "power": power(), "capacity": capacity(), "axle_30l": axle_loads(),
           "axle_120l": axle_loads(P.S.tank_nominal)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
