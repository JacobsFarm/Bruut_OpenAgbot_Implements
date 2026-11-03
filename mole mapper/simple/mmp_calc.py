"""Calculations for the mole and tunnel mapper, in pure Python (same parameters as the model).

    import mmp_calc
    mmp_calc.report()          # prints and returns all key figures
"""
import math

import mmp_params as P


def cameras():
    """Strip width on the ground and ground resolution of the RGB and thermal cameras (looking straight down)."""
    h = P.cam_height
    w1 = 2.0 * h * math.tan(math.radians(P.cam_hfov / 2.0))
    strip = (max(P.cam_x) - min(P.cam_x)) + w1
    px = w1 / P.cam_px
    wt = 2.0 * h * math.tan(math.radians(P.thermal_hfov / 2.0))
    return {"cam_width_mm": round(w1), "strip_m": round(strip / 1000.0, 2), "rgb_mm_px": round(px, 2),
            "thermal_width_mm": round(wt), "thermal_mm_px": round(wt / P.thermal_px, 1),
            "px_per_small_hill": round(P.hill_d[0] / px)}


def mapping():
    strip = cameras()["strip_m"] - P.overlap / 1000.0
    m2_h = strip * P.speed * 3600.0
    drag = P.crr * (P.robot_mass + P.MODEL_MASS["kg"]) * P.g
    w = drag * P.speed / P.eta_drive + P.p_cams
    hours = P.battery_wh / w
    return {"strip_m": round(strip, 2), "ha_h": round(m2_h / 1e4, 2), "power_W": round(w), "hours": round(hours, 1),
            "ha_per_charge": round(m2_h * hours / 1e4, 1)}


def probe():
    """Time per probe point and per hill (ring of points), and what probing costs per ha."""
    fast = (P.tip_park + 0.0) / P.fast_speed            # down to the ground
    push = P.probe_depth / P.probe_speed
    up = (P.probe_depth + P.tip_park) / P.fast_speed
    point_s = fast + push + up + P.move_s
    hill_s = P.ring_n * point_s
    spacing = 2.0 * math.pi * P.ring_r / P.ring_n
    hit = min(1.0, P.tunnel_d * 2.0 / spacing)          # a tunnel crosses the ring twice; chance one probe hits it
    probed = P.hills_per_ha * P.fresh_share * P.probe_share
    return {"point_s": round(point_s, 1), "hill_min": round(hill_s / 60.0, 1), "ring_spacing_mm": round(spacing),
            "tunnel_found": round(hit, 2), "hills_probed_per_ha": round(probed),
            "probe_h_per_ha": round(probed * hill_s / 3600.0, 2)}


def tunnel_signal():
    """Cone in a tunnel: the resistance drops to ~0 over the tunnel diameter; at 30 mm/s and 100 Hz logging that is
    this many samples."""
    samples = P.tunnel_d / P.probe_speed * 100.0
    return {"samples_in_tunnel": round(samples), "depth_window_mm": P.tunnel_depth}


def report():
    out = {"cameras": cameras(), "mapping": mapping(), "probe": probe(), "tunnel": tunnel_signal()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
