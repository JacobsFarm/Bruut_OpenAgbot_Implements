"""Calculations for the windbreak inspector, in pure Python (same parameters as the model).

    import wbi_calc
    wbi_calc.report()          # prints and returns all key figures
"""
import math

import wbi_params as P

LIDAR_Z = P.lidar_z / 1000.0
DIST = (P.row_x - P.mast_xy[0]) / 1000.0        # sensor to the row face (m), roughly


def lidar():
    """Highest point of the row the lidar sees at the row distance, point spacing there, profile spacing."""
    up = math.radians((P.lidar_fov - 180.0) / 2.0 + 90.0)       # 270 deg fov: 135 deg up from horizontal
    top = LIDAR_Z + DIST * math.tan(min(up, math.radians(85.0)))
    spacing_mm = DIST * math.radians(P.lidar_res_deg) * 1000.0
    out = {"row_distance_m": round(DIST, 2), "sees_up_to_m": round(top, 1) if up < math.radians(90) else "overhead",
           "point_spacing_at_row_mm": round(spacing_mm, 1),
           "profile_every_mm": round(P.speed / P.lidar_hz * 1000.0)}
    for h in P.row_heights:
        d = math.hypot(DIST, h - LIDAR_Z)
        out["spacing_at_top_%gm_mm" % h] = round(d * math.radians(P.lidar_res_deg) * 1000.0)
    return out


def cameras():
    """Height covered by the stereo cameras at the row, pixel size there, stereo depth error."""
    z = [v / 1000.0 for v in P.stereo_z]
    half = DIST * math.tan(math.radians(P.cam_vfov / 2.0))
    cover = (max(0.0, min(z) - half), max(z) + half)
    px = 2.0 * half / P.cam_px_v * 1000.0
    f_px = P.cam_px_v / (2.0 * math.tan(math.radians(P.cam_vfov / 2.0)))
    dz = DIST ** 2 / (P.stereo_base / 1000.0 * f_px) * P.disparity_err * 1000.0
    crown_top = max(z) + DIST * math.tan(math.radians(P.cam_up_deg + P.crown_cam_vfov / 2.0))
    return {"stereo_covers_m": (round(cover[0], 2), round(cover[1], 2)), "mm_per_px": round(px, 2),
            "depth_error_mm": round(dz, 1), "crown_cam_up_to_m": round(crown_top, 1)}


def wind():
    """Wind load on the head and the moment at the mast foot (base plate bolts)."""
    bx, by, bz = P.head_box
    area = by / 1000.0 * bz / 1000.0
    f = 0.5 * 1.25 * P.wind_ms ** 2 * P.cd_head * area
    h = (P.head_z0 + bz / 2.0 - 707.0) / 1000.0
    return {"force_N": round(f), "moment_Nm": round(f * h)}


def capacity():
    drag = P.crr * (P.robot_mass + P.MODEL_MASS["kg"]) * P.g
    w = drag * P.speed / P.eta_drive + P.p_sensors
    hours = P.battery_wh / w
    return {"km_h": round(P.speed * 3.6, 1), "power_W": round(w), "hours": round(hours, 1),
            "km_per_charge": round(P.speed * 3.6 * hours, 1)}


def side():
    m = P.MODEL_MASS
    x = m["kg"] * m["cg_x"] / (P.robot_mass + m["kg"])
    return {"cg_x_mm": round(x), "right_share": round(0.5 + x / (2.0 * P.robot_wheel_x), 3)}


def report():
    out = {"lidar": lidar(), "cameras": cameras(), "wind": wind(), "capacity": capacity(), "side": side()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
