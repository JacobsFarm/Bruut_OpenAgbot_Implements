"""Calculations for the yield estimator, in pure Python (same parameters as the model).

    import yld_calc
    yld_calc.report()          # prints and returns all key figures
"""
import math

import yld_params as P


def cameras():
    """Width per camera and pixel size at the crop top; frames per plant; ToF size error."""
    h = P.cam_height - P.crop_height
    w = 2.0 * h * math.tan(math.radians(P.cam_hfov / 2.0))
    px = w / P.cam_px
    frames = P.plant_spacing / (P.speed * 1000.0 / P.fps)
    ht = P.cam_height - P.crop_height
    wt = 2.0 * ht * math.tan(math.radians(P.tof_hfov / 2.0))
    tof_px = wt / P.tof_px
    return {"rgb_width_mm": round(w), "rows_overlap": w > P.row_spacing, "rgb_mm_px": round(px, 2),
            "px_across_small_head": round(P.head_d[0] / px), "frames_per_plant": round(frames, 1),
            "tof_width_mm": round(wt), "tof_mm_px": round(tof_px, 1), "tof_depth_err_mm": P.tof_err_mm}


def head_mass(d):
    return P.mass_a * d ** P.mass_b


def size_error():
    """Diameter from the RGB edge (+-2 px) and the head mass error that follows (m ~ d^b)."""
    px = cameras()["rgb_mm_px"]
    out = {}
    for d in P.head_d:
        dd = 2.0 * px / d
        out["d_%d" % d] = {"mass_g": round(head_mass(d)), "d_err_pct": round(dd * 100.0, 1),
                           "mass_err_pct": round(math.hypot(P.mass_b * dd, P.size_cv) * 100.0, 1)}
    return out


def field_estimate(n_heads=1000):
    """Error of the summed yield of n heads (independent errors shrink with sqrt(n))."""
    e = size_error()["d_%d" % P.head_d[1]]["mass_err_pct"] / 100.0
    return {"heads": n_heads, "sum_err_pct": round(e / math.sqrt(n_heads) * 100.0, 2)}


def capacity():
    width = P.rows * P.row_spacing / 1000.0
    m2_h = width * P.speed * 3600.0
    drag = P.crr * (P.robot_mass + P.MODEL_MASS["kg"]) * P.g
    w = drag * P.speed / P.eta_drive + P.p_sensors
    hours = P.battery_wh / w
    plants_h = m2_h / (P.row_spacing / 1000.0 * P.plant_spacing / 1000.0)
    return {"width_m": width, "ha_h": round(m2_h / 1e4, 2), "plants_h": round(plants_h), "power_W": round(w),
            "hours": round(hours, 1), "ha_per_charge": round(m2_h * hours / 1e4, 1)}


def report():
    out = {"cameras": cameras(), "size_error": size_error(), "field": field_estimate(), "capacity": capacity()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
