"""Calculations for the propane flame weeder (pure Python, no FreeCAD): gas flow and dose, burner pressure, heat on
the soil and exposure time, vaporiser, cylinder pressure and run time, capacity and cost, what happens when the robot
stops, the hood's heat towards the robot, axle loads.

    python flw_calc.py          (or in FreeCAD: import flw_calc; flw_calc.report())
"""
import math

import flw_params as P

G_ACC = 9.81

# last measurement from the model (build_flw.mass_properties: steel 7850, aluminium 2700, ceramic blanket 128 kg/m3,
# bought parts with their catalogue mass; cylinders empty). MODEL is updated by hand after a rebuild.
MODEL = {"kg": 130.9, "cg": (0.0, -727.0, 463.0), "hood_kg": 69.2, "hood_cg": (-1.0, -1188.0, 216.0),
         "gas_kg": 40.8, "gas_cg": (0.0, -1.0, 865.0), "mount_kg": 21.0, "mount_cg": (4.0, -616.0, 497.0)}


# ---------------------------------------------------------------------
# Gas flow, dose
# ---------------------------------------------------------------------
def burner_flow(bar=P.burner_bar):
    """kg/h per burner: through a fixed orifice the mass flow goes with sqrt(dp x density) and the density with the
    absolute pressure, so q ~ sqrt(p (p + 1)); scaled from the catalogue point at 2 bar."""
    return P.burner_kg_h_2bar * math.sqrt((bar + 1.0) / (2.0 + 1.0)) * (bar / 2.0) ** 0.5


def flow(bar=P.burner_bar):
    q = P.n_burners * burner_flow(bar)
    return {"kg_h": q, "kW": q * P.lhv * 1000.0 / 3600.0, "per_burner": burner_flow(bar)}


def area_rate(v=P.speed):
    return P.work_w / 1000.0 * v * 3600.0          # m2/h


def dose(v=P.speed, bar=P.burner_bar):
    f = flow(bar)
    kg_ha = f["kg_h"] / (area_rate(v) / 10000.0)
    kJ_m2 = kg_ha * P.lhv * 1000.0 / 10000.0       # burner energy per m2
    return {"kg_ha": kg_ha, "kJ_m2": kJ_m2, "soil_kJ_m2": kJ_m2 * P.hood_eff,
            "exposure_s": (P.hood_y[1] - P.hood_y[0]) / 1000.0 / v}


def pressure_for_dose(target=P.dose_target, v=P.speed):
    """Burner pressure (bar) that gives the target dose at speed v (bisection)."""
    lo, hi = 0.3, 4.0
    for _ in range(50):
        mid = (lo + hi) / 2.0
        if dose(v, mid)["kg_ha"] < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def speed_for_dose(target, bar=P.burner_bar):
    f = flow(bar)["kg_h"]
    return f / (target / 10000.0) / (P.work_w / 1000.0) / 3600.0


# ---------------------------------------------------------------------
# Gas supply: cylinders, vaporiser
# ---------------------------------------------------------------------
def vapour_pressure(temp_c):
    pts = P.vapour_bar
    if temp_c <= pts[0][0]:
        return pts[0][1]
    for (t0, p0), (t1, p1) in zip(pts[:-1], pts[1:]):
        if temp_c <= t1:
            return p0 + (p1 - p0) * (temp_c - t0) / (t1 - t0)
    return pts[-1][1]


def min_temp_for(bar=P.burner_bar, margin=0.8):
    """Lowest cylinder temperature (C) where the vapour pressure still exceeds the burner pressure + margin."""
    for t10 in range(-200, 300):
        t = t10 / 10.0
        if vapour_pressure(t) >= bar + margin:
            return t
    return None


def supply(v=P.speed, bar=P.burner_bar):
    f = flow(bar)
    gas = 2 * P.cyl_kg_gas
    hours = gas * 0.95 / f["kg_h"]                  # 5 % left in the cylinders
    ha = hours * area_rate(v) / 10000.0 * P.field_eff
    vap_kW = f["kg_h"] / 3600.0 * (P.latent + 0.002 * 150.0) * 1000.0  # evaporate + superheat ~150 K (cp ~2 kJ/kg K)
    coil_len = P.coil_passes * 2.0 * P.coil_x
    coil_area = math.pi * P.coil_d / 1000.0 * coil_len / 1000.0
    flux = vap_kW * 1000.0 / coil_area              # W/m2 needed on the coil
    return {"gas_kg": gas, "hours": hours, "ha": ha, "vap_kW": vap_kW, "coil_m": coil_len / 1000.0,
            "coil_m2": coil_area, "flux_kW_m2": flux / 1000.0, "min_temp": min_temp_for(bar),
            "share_vap": vap_kW / f["kW"]}


# ---------------------------------------------------------------------
# Capacity, cost, battery
# ---------------------------------------------------------------------
def capacity(v=P.speed):
    gross = area_rate(v) / 10000.0
    return {"gross_ha_h": gross, "net_ha_h": gross * P.field_eff, "km_h": v * 3.6}


def cost(v=P.speed, bar=P.burner_bar):
    d = dose(v, bar)
    return {"eur_ha": d["kg_ha"] * P.gas_price}


def battery(v=P.speed):
    tot = P.drive_w + P.control_w
    return {"P": tot, "hours": P.battery_kwh * 1000.0 / tot}


# ---------------------------------------------------------------------
# Standing still: the soil under the hood gets the full heat; valves must close
# ---------------------------------------------------------------------
def standstill(t_close=0.5, v=P.speed, bar=P.burner_bar):
    """Extra heat on the strip under the flames if the robot stops and the valves close after t_close seconds."""
    f = flow(bar)
    flame_area = P.work_w / 1000.0 * 0.30           # m2 directly under the flames (~300 mm long)
    kJ = f["kW"] * t_close * P.hood_eff / flame_area
    return {"t_close": t_close, "kJ_m2": kJ, "x_dose": kJ / dose(v, bar)["soil_kJ_m2"]}


# ---------------------------------------------------------------------
# Heat towards the robot (radiation from the hood's front, behind the aluminium shield)
# ---------------------------------------------------------------------
def heat_to_robot(T_wall=350.0, T_shield=120.0):
    """Radiant flux on the rear tyre (W/m2) from the front wall (emissivity 0.8) without and with the shield
    (polished aluminium, emissivity 0.1 outside), view factor ~0.15 at 215 mm."""
    s = 5.67e-8
    T0 = 293.0
    q_bare = 0.8 * s * ((T_wall + 273.0) ** 4 - T0 ** 4) * 0.15
    q_shield = 0.1 * s * ((T_shield + 273.0) ** 4 - T0 ** 4) * 0.15
    return {"bare_W_m2": q_bare, "shield_W_m2": q_shield, "sun_W_m2": 1000.0}


# ---------------------------------------------------------------------
# Parallelogram (free): the hood follows the ground on its castors
# ---------------------------------------------------------------------
def head_offset(h):
    """Translation (dy, dz) of the hood for a float h (mm, + = up) and the arm angle (deg)."""
    b = math.asin(max(-1.0, min(1.0, h / P.arm_len)))
    return (P.arm_len * (1.0 - math.cos(b)), h, math.degrees(b))


# ---------------------------------------------------------------------
# Axle loads: the castors carry the hood; the robot carries the cylinders and the mount
# ---------------------------------------------------------------------
def axle_loads(gas_kg=None):
    gas_kg = 2 * P.cyl_kg_gas if gas_kg is None else gas_kg
    parts = [(P.robot_kg, P.robot_cg[1]), (MODEL["mount_kg"], MODEL["mount_cg"][1]),
             (MODEL["gas_kg"] + gas_kg, MODEL["gas_cg"][1])]
    m = sum(k for k, _ in parts)
    y = sum(k * yy for k, yy in parts) / m
    # pitch moment of the hood through the parallelogram: castors at caster_y, hood cg
    M = MODEL["hood_kg"] * (P.caster_y - MODEL["hood_cg"][1])
    front = m * (0.5 + y / P.robot_wheelbase) + M / P.robot_wheelbase
    return {"kg": m, "front_kg": front, "rear_kg": m - front, "front_share": front / m,
            "wheel_max": max(front, m - front) / 2.0}


def report():
    f = flow()
    d = dose()
    pr = pressure_for_dose()
    s = supply()
    cap = capacity()
    c = cost()
    st = standstill()
    h = heat_to_robot()
    full, empty = axle_loads(), axle_loads(0.0)
    b = battery()
    lines = ["=== Propane flame weeder with hood: key figures ===",
             "Hood %.2f m wide, %.2f m long; %d burners at %.0f mm, %.0f deg down; %.2f kg/h each at %.1f bar -> "
             "%.1f kg/h, %.0f kW" % (P.work_w / 1000.0, (P.hood_y[1] - P.hood_y[0]) / 1000.0, P.n_burners,
                                     P.burner_pitch, P.burner_angle, f["per_burner"], P.burner_bar, f["kg_h"],
                                     f["kW"]),
             "At %.1f m/s (%.1f km/h): %.0f m2/h, dose %.0f kg/ha = %.0f kJ/m2 from the burners, ~%.0f kJ/m2 on the soil "
             "(lethal for cotyledon .. 4 leaves: %.0f .. %.0f), %.2f s under the hood" % (
                 P.speed, cap["km_h"], area_rate(), d["kg_ha"], d["kJ_m2"], d["soil_kJ_m2"], P.lethal_kJ_m2[0],
                 P.lethal_kJ_m2[1], d["exposure_s"]),
             "Pressure for %.0f kg/ha at %.1f m/s: %.2f bar; speed for 25 / 35 / 50 kg/ha at %.1f bar: %.2f / %.2f / "
             "%.2f m/s" % (P.dose_target, P.speed, pr, P.burner_bar, speed_for_dose(25.0), speed_for_dose(35.0),
                           speed_for_dose(50.0)),
             "Gas 2 x %.0f kg (liquid withdrawal): %.1f h, %.2f ha per filling; works down to %.0f C cylinder "
             "temperature (vapour pressure > %.1f + 0.8 bar)" % (P.cyl_kg_gas, s["hours"], s["ha"], s["min_temp"],
                                                                 P.burner_bar),
             "Vaporiser: %.2f kW (%.1f %% of the burner heat) on a coil of %.1f m (%.3f m2): %.0f kW/m2 needed, "
             "flame gas at 600-800 C gives 30-60" % (s["vap_kW"], 100 * s["share_vap"], s["coil_m"], s["coil_m2"],
                                                    s["flux_kW_m2"]),
             "Capacity %.2f ha/h gross, %.2f net; gas ~EUR %.0f/ha; battery %.0f W -> %.1f h (gas runs out first)" % (
                 cap["gross_ha_h"], cap["net_ha_h"], c["eur_ha"], b["P"], b["hours"]),
             "Standing still: valves closed after %.1f s still put %.0f kJ/m2 under the flames (%.1f x the dose): "
             "close at once when the speed drops below 0.2 m/s" % (st["t_close"], st["kJ_m2"], st["x_dose"]),
             "Heat to the rear tyre: %.0f W/m2 from a bare front wall at 350 C, %.0f W/m2 behind the shield (sun %.0f)" % (
                 h["bare_W_m2"], h["shield_W_m2"], h["sun_W_m2"]),
             "Mass %.0f kg empty (hood %.0f on its castors, cylinders + cradle %.0f, mount + gas panel %.0f); robot + "
             "full cylinders: %.0f kg, front %.0f / rear %.0f kg (%.0f %% front), max %.0f kg per wheel of %.0f; "
             "empty cylinders: front %.0f / rear %.0f" % (MODEL["kg"], MODEL["hood_kg"], MODEL["gas_kg"],
                                                         MODEL["mount_kg"], full["kg"], full["front_kg"],
                                                         full["rear_kg"], 100 * full["front_share"], full["wheel_max"],
                                                         P.wheel_load_max, empty["front_kg"], empty["rear_kg"])]
    print("\n".join(lines))
    return lines


if __name__ == "__main__":
    report()
