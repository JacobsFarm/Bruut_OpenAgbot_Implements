"""Calculations for the soil scanner, in pure Python (same parameters as the model).

    import ssc_calc
    ssc_calc.report()          # prints and returns all key figures
"""
import math

import ssc_params as P


# ---------------------------------------------------------------------
# Where the counts come from: uncollided gamma flux from a uniform half-space of soil at a detector height h
# ---------------------------------------------------------------------
def _field(mu_rho, h_cm, r_max=3000.0, d_max=120.0, nr=240, nd=120):
    """Flux contribution per ring (r) and per layer (d). Source uniform in the soil (z < 0), point detector at h.
    Path from (r, -d) to (0, h): length L, share d / (h + d) in soil, the rest in air."""
    mu_s = P.mu_soil(mu_rho)
    mu_a = mu_rho * P.air_rho
    rs = [r_max * ((i + 0.5) / nr) ** 2 for i in range(nr)]      # finer near the detector
    dr = [r_max * (((i + 1) / nr) ** 2 - (i / nr) ** 2) for i in range(nr)]
    ds = [d_max * (j + 0.5) / nd for j in range(nd)]
    dd = d_max / nd
    ring = [0.0] * nr
    layer = [0.0] * nd
    for i, r in enumerate(rs):
        for j, d in enumerate(ds):
            L = math.hypot(r, h_cm + d)
            ls = L * d / (h_cm + d)
            w = math.exp(-mu_s * ls - mu_a * (L - ls)) / (L * L) * r * dr[i] * dd
            ring[i] += w
            layer[j] += w
    return rs, ring, ds, layer


def _quantile(xs, ws, q):
    tot = sum(ws)
    acc = 0.0
    for x, w in zip(xs, ws):
        acc += w
        if acc >= q * tot:
            return x
    return xs[-1]


def footprint(h_mm=600.0):
    """Radius (m) around the detector and depth (cm) in the soil from which 50 / 90 % of the counts come."""
    out = {}
    for iso, (kev, mu) in P.LINES.items():
        rs, ring, ds, layer = _field(mu, h_mm / 10.0)
        out[iso] = {"keV": kev, "r50_m": round(_quantile(rs, ring, 0.5) / 100, 2),
                    "r90_m": round(_quantile(rs, ring, 0.9) / 100, 1),
                    "d90_cm": round(_quantile(ds, layer, 0.9), 0)}
    return out


def height_effect():
    """K-40 footprint at other heights: higher = wider footprint, less detail between the lanes."""
    out = {}
    for h in (300.0, 600.0, 1000.0):
        rs, ring, ds, layer = _field(P.LINES["K-40"][1], h / 10.0)
        out["h_%d" % h] = {"r50_m": round(_quantile(rs, ring, 0.5) / 100, 2), "r90_m": round(_quantile(rs, ring, 0.9) / 100, 1)}
    return out


# ---------------------------------------------------------------------
# Counting statistics per block (one spectrum per second)
# ---------------------------------------------------------------------
def counts(litre=None, speed=None):
    """Counts per window in one spectrum and the 1-sigma relative error (Poisson), per soil type."""
    litre = P.crystal_litre() if litre is None else litre
    speed = P.speed if speed is None else speed
    t = 1.0 / P.spectrum_hz
    t = t * P.speed / speed                         # slower driving = more time over the same 1.2 m block
    out = {}
    for soil, conc in P.SOILS.items():
        row = {}
        for (iso, s), c in zip(P.SENS.items(), conc):
            n = s * litre * c * t
            row[iso.split(" ")[0]] = {"counts": round(n), "err_pct": round(100.0 / math.sqrt(n), 1) if n > 0 else None}
        out[soil] = row
    return out


def crystal_compare():
    out = {}
    for name, litre in P.crystal_options.items():
        c = counts(litre)
        out[name] = {"sand_K_err_pct": c["sand"]["K-40"]["err_pct"], "clay_K_err_pct": c["clay"]["K-40"]["err_pct"],
                     "sand_Th_err_pct": c["sand"]["Th-232"]["err_pct"],
                     "crystal_kg": round(litre * P.csi_rho, 1)}
    return out


def speed_for_sand(target_err=10.0):
    """Speed at which a 1.2 m block in sand still gets the K error below target_err % (4 l crystal)."""
    n_target = (100.0 / target_err) ** 2
    rate = P.SENS["K-40"] * P.crystal_litre() * P.SOILS["sand"][0]       # cps
    t = n_target / rate
    return {"time_per_block_s": round(t, 2), "speed_m_s": round(P.block_len() / t, 2)}


# ---------------------------------------------------------------------
# Field work
# ---------------------------------------------------------------------
def data_points():
    return {"block_m": (P.lane, round(P.block_len(), 2)), "points_per_ha": round(10000.0 / (P.lane * P.block_len()))}


def capacity(area_ha=None, dims=None):
    """Scan of a rectangular field: lanes of 10 m, headland half-turns of radius 5 m."""
    area_ha = P.example_field_ha if area_ha is None else area_ha
    L, W = dims or P.example_field
    lanes = int(math.ceil(W / P.lane))
    dist = lanes * L + (lanes - 1) * math.pi * P.turn_r
    t = dist / P.speed
    m = P.robot_mass + P.MODEL_MASS["total_kg"]
    p_drive = P.crr * m * P.g * P.speed / P.eta_drive
    e = (p_drive + P.p_scanner + P.p_logger) * t / 3600.0
    return {"field_ha": area_ha, "lanes": lanes, "km": round(dist / 1000, 2), "hours": round(t / 3600, 2),
            "ha_per_hour": round(area_ha / (t / 3600), 2), "drive_W": round(p_drive), "wh": round(e),
            "wh_per_ha": round(e / area_ha), "ha_per_battery": round(P.battery_wh / (e / area_ha), 1),
            "spectra": round(t * P.spectrum_hz)}


def calibration(area_ha=None):
    """Calibration samples (Interra: at least 4 per field and 2 per ha) and the time with the soil sampler."""
    area_ha = P.example_field_ha if area_ha is None else area_ha
    n = max(P.samples_min, int(math.ceil(P.samples_per_ha * area_ha)))
    t_site = P.cores_per_sample * P.t_core
    side = math.sqrt(area_ha * 1e4)
    drive = n * side / math.sqrt(n) * 1.2          # spread points: ~ field side / sqrt(n) between them
    t = n * t_site + drive / P.speed
    return {"samples": n, "s_per_sample": round(t_site), "hours": round(t / 3600, 2)}


def axle_load():
    """Front axle share with the scanner (the robot CG is in the middle)."""
    m = P.MODEL_MASS["total_kg"]
    tot = P.robot_mass + m
    cg = m * P.MODEL_MASS["cg_y"] / tot
    front = 0.5 + cg / P.robot_wheelbase
    return {"total_kg": round(tot, 1), "cg_y_mm": round(cg), "front_share": round(front, 2)}


def report():
    out = {"data_points": data_points(), "footprint_600": footprint(), "height_effect": height_effect(),
           "counts_4l": counts(), "crystal_compare": crystal_compare(), "speed_for_sand": speed_for_sand(),
           "capacity_18ha": capacity(), "calibration_18ha": calibration(), "axle_load": axle_load(),
           "mass_kg": P.MODEL_MASS["total_kg"]}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
