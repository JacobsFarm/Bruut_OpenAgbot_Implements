"""Calculations for the drone landing platform, in pure Python (same parameters as the model).

    import drn_calc
    drn_calc.report()          # prints and returns all key figures
"""
import math

import drn_params as P


def landing():
    """Does the platform catch the drone? Flat landing zone and the wedges that slide it to the middle."""
    half_zone = P.landing_zone / 2000.0
    half_plate = P.plate[0] / 2000.0
    foot = 0.15                                     # m half the skid length
    return {"flat_zone_m": P.landing_zone / 1000.0, "typical_err_m": P.landing_err[0],
            "lands_flat": P.landing_err[0] + foot <= half_zone,
            "caught_by_wedges": P.landing_err[1] + foot <= half_plate,
            "wedge_slope_deg": round(math.degrees(math.atan(P.wedge_h / P.wedge_w)))}


def flight():
    """Area mapped per flight at fly_alt with side_overlap, and photos' ground resolution (20 MP, 5280 px)."""
    swath = 2.0 * P.fly_alt * math.tan(math.radians(P.cam_hfov / 2.0))
    step = swath * (1.0 - P.side_overlap)
    t = P.drone_flight_min * 60.0 * (1.0 - P.reserve)
    ha = step * P.fly_speed * t / 1e4
    return {"swath_m": round(swath), "line_spacing_m": round(step), "ha_per_flight": round(ha),
            "gsd_cm": round(swath / 5280.0 * 100.0, 1)}


def charging():
    wh = P.drone_wh / P.charge_eff
    minutes = P.drone_wh / P.charge_w / P.charge_eff * 60.0 * 1.15            # CV tail
    share = wh / P.robot_battery_wh
    return {"robot_Wh_per_charge": round(wh), "minutes": round(minutes), "share_of_robot_battery_pct":
            round(share * 100.0, 1), "flights_per_robot_battery": round(P.robot_battery_wh * 0.3 / wh, 1)}


def stability():
    """Height of the centre of gravity of the platform; wind on the drone sitting on the platform."""
    area = 0.35 * 0.2
    f = 0.5 * 1.25 * P.wind_max ** 2 * 1.2 * area
    hold = P.drone_kg * P.g * 0.5 + 0.5 * P.magnet_N  # skid friction (0.5) plus the strip magnets
    return {"wind_N_on_drone": round(f, 1), "hold_N": round(hold, 1),
            "held": f < hold}


def report():
    out = {"landing": landing(), "flight": flight(), "charging": charging(), "wind": stability()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
