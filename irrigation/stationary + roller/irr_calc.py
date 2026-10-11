"""Calculations for the irrigation hose reel (pure Python, no FreeCAD needed).

Use:  import irr_calc; irr_calc.report()
Masses of the implement come from the FreeCAD model (build_irr.mass_properties), see MODEL.
Hose positions s are in m along the hose, measured from the hydrant.
"""
import math

import irr_params as P

G_ACC = 9.81
RHO = 1000.0

# last measurement from the model (build_irr.mass_properties, steel 7850, aluminium 2700, PE 950 kg/m3,
# bought parts with a fixed mass), reel full, hose empty
MODEL = {"kg": 146.3, "cg": (-12.0, -205.0, 1058.0), "mount_kg": 7.6, "frame_kg": 34.7, "reel_kg": 21.3,
         "drive_kg": 10.9, "pinch_kg": 10.3, "hose_kg": 61.5}

# robot 4WD ready to drive, from agbots/agbot comparison/weight_traction.json (estimated, not weighed)
ROBOT = {
    "robot_kg": P.robot_kg,
    "robot_cg": (0.0, 95.0, 543.0),
    "axle_spec_kg": 500.0,      # per axle, hub motor spec
    "traction_mu": 0.35,        # wet grass
}
HALF_BASE = P.robot_axle_y      # 500
RUN_M = 2.0                     # m of hose on the robot between the coil and the ground (animate_irr.run_len())


# ---------------------------------------------------------------------
# Hose and coil
# ---------------------------------------------------------------------
def area_m2(d_mm=P.hose_id):
    return math.pi / 4.0 * (d_mm / 1000.0) ** 2


def litre_per_m():
    return area_m2() * 1000.0


def coil_r(l_m):
    """Outer radius (mm) of the coil with l_m metres of hose on the reel."""
    r0 = P.core_od / 2.0
    return math.sqrt(r0 * r0 + l_m * 1000.0 * P.coil_t / math.pi)


def reel_angle(l_m):
    """Reel rotation (rad) from an empty core to l_m metres on the reel: d(angle) = dL / r."""
    r0 = P.core_od / 2.0
    return 2.0 * math.pi * (coil_r(l_m) - r0) / P.coil_t


def s_ground():
    """Hose length lying in the field when the robot is at the end of the strip (m)."""
    return P.hose_len - P.reel_reserve - RUN_M


def outlets(s_max=None):
    """Positions (m from the hydrant) of the outlets on the ground."""
    s_max = s_ground() if s_max is None else s_max
    out = []
    s = P.outlet_first
    while s <= s_max - 0.5:
        out.append(s)
        s += P.outlet_pitch
    return out


def hose():
    n = len(outlets(P.hose_len))
    m = P.hose_kg_per_m * P.hose_len + n * P.outlet_kg
    return {"flat_w": round(P.hose_flat_w, 1), "flat_t": P.hose_flat_t, "l_per_m": round(litre_per_m(), 2),
            "full_l": round(litre_per_m() * s_ground()), "full_kg_on_ground": round(litre_per_m() * s_ground() +
                                                                                   P.hose_kg_per_m * s_ground()),
            "mass_empty_kg": round(m, 1), "outlets_total": n, "outlets_on_ground": len(outlets()),
            "coil_d_full": round(2 * coil_r(P.hose_len)), "coil_d_reserve": round(2 * coil_r(P.reel_reserve)),
            "flange_margin": round(P.flange_d / 2.0 - coil_r(P.hose_len), 1),
            "reel_turns": round(reel_angle(P.hose_len) / (2 * math.pi), 1)}


# ---------------------------------------------------------------------
# Hydraulics: lay-flat hose with outlets (Hazen-Williams, orifices)
# ---------------------------------------------------------------------
def hw_j(q_m3h, d_mm=P.hose_id, c=P.hw_c):
    """Friction loss (m per m) of a full round pipe."""
    if q_m3h <= 0.0:
        return 0.0
    q = q_m3h / 3600.0
    return 10.67 * q ** 1.852 / (c ** 1.852 * (d_mm / 1000.0) ** 4.87)


def orifice_q(h_m, d_mm=P.outlet_d):
    """Flow (m3/h) of one outlet at head h (m above the outlet)."""
    if h_m <= 0.0:
        return 0.0
    return P.outlet_cd * area_m2(d_mm) * math.sqrt(2.0 * G_ACC * h_m) * 3600.0


def _march(h_end, pos, slope):
    """From the last outlet back to the hydrant. Returns head at the hydrant, total flow, outlet flows."""
    h = h_end
    q_tot = 0.0
    flows = []
    for i in range(len(pos) - 1, -1, -1):
        q = orifice_q(h)
        flows.append(q)
        q_tot += q
        prev = pos[i - 1] if i > 0 else 0.0
        ds = pos[i] - prev
        h += hw_j(q_tot) * ds + slope * ds     # going back towards the hydrant: lower if the strip runs uphill
    flows.reverse()
    return h, q_tot, flows


def strip_flow(h_in, slope=P.slope, pos=None):
    """Outlet flows for an inlet head h_in (m, at the hydrant, ground level). Shooting on the head at the end."""
    pos = outlets() if pos is None else pos
    lo, hi = 0.0, h_in + abs(slope) * pos[-1] + 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        h0, _, _ = _march(mid, pos, slope)
        if h0 > h_in:
            hi = mid
        else:
            lo = mid
    h0, q, flows = _march(lo, pos, slope)
    return {"h_in": h_in, "h_end": lo, "q": q, "flows": flows, "pos": pos}


def uniformity(flows):
    mean = sum(flows) / len(flows)
    cu = 1.0 - sum(abs(f - mean) for f in flows) / (len(flows) * mean)
    low = sorted(flows)[: max(1, len(flows) // 4)]
    return {"cu": cu, "du_lq": (sum(low) / len(low)) / mean, "min_max": min(flows) / max(flows)}


def q_target():
    """Flow (m3/h) at which each outlet's water spreads over pitch x strip_w and just infiltrates."""
    per_outlet = P.infiltration / 1000.0 * P.outlet_pitch * P.strip_w     # m3/h
    return per_outlet * len(outlets())


def design(slope=P.slope):
    """Inlet head that gives the target flow."""
    target = q_target()
    lo, hi = 0.05, 20.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if strip_flow(mid, slope)["q"] > target:
            hi = mid
        else:
            lo = mid
    r = strip_flow(lo, slope)
    r.update(uniformity(r["flows"]))
    r["target"] = target
    r["p_end_bar"] = r["h_end"] * RHO * G_ACC / 1e5
    r["loss_m"] = r["h_in"] - r["h_end"] - slope * r["pos"][-1]
    return r


def pump(q_m3h, h_in):
    """Operating point of the petrol pump: throttle (speed fraction), head, power, fuel."""
    scale = (q_m3h / 10.0) ** 2
    h_pump = h_in + P.suction_lift + (P.suction_loss + P.valve_loss) * scale
    k = P.pump_h0 / P.pump_qmax ** 2
    n = math.sqrt((h_pump + k * q_m3h ** 2) / P.pump_h0)
    p_hyd = RHO * G_ACC * q_m3h / 3600.0 * h_pump
    eta = P.pump_eta * min(1.0, q_m3h / (0.5 * P.pump_qmax * max(n, 0.01)))      # far left of the best point
    p_shaft = p_hyd / max(eta, 0.08)
    fuel = max(P.pump_fuel_idle, p_shaft / 1000.0 * P.pump_fuel_l_kwh)
    return {"h_pump": h_pump, "throttle": n, "below_min": n < P.pump_n_min, "p_hyd_w": p_hyd,
            "p_shaft_w": p_shaft, "fuel_l_h": fuel}


# ---------------------------------------------------------------------
# Reel drive and forces
# ---------------------------------------------------------------------
def reel_omega_max():
    return P.motor_rpm / P.chain_ratio * 2.0 * math.pi / 60.0


def reel_drive():
    r_full = coil_r(P.hose_len) / 1000.0
    r_min = coil_r(P.reel_reserve) / 1000.0
    torque_need = P.tension_wind * r_full
    torque_have = P.motor_nm * P.chain_ratio * P.chain_eta
    return {"torque_need_nm": torque_need, "torque_have_nm": torque_have, "reserve": torque_have / torque_need,
            "reel_rpm_max": P.motor_rpm / P.chain_ratio,
            "v_wind_min": reel_omega_max() * r_min, "v_wind_full": reel_omega_max() * r_full,
            "power_w": P.tension_wind * P.v_rollup_max / P.chain_eta / 0.7}


def wind_speed(l_reel):
    return min(P.v_rollup_max, reel_omega_max() * coil_r(l_reel) / 1000.0)


def pinch():
    """The pinch rollers close the hose during irrigation. Pull of the water on the robot = p x area of the hose."""
    d = design()
    p = d["h_end"] * RHO * G_ACC                         # Pa at the robot
    pull = p * area_m2()
    clamp = 2.0 * P.spring_k * P.spring_pre
    # the flat hose seals when the line load exceeds p x (wall-to-wall width) (estimated with a 10 mm contact band)
    need = p / 1e6 * P.hose_flat_w * 10.0
    robot_hold = ROBOT["traction_mu"] * (ROBOT["robot_kg"] + MODEL["kg"]) * G_ACC
    return {"p_end_kpa": p / 1000.0, "pull_n": pull, "clamp_n": clamp, "clamp_need_n": need,
            "clamp_reserve": clamp / max(need, 1e-6), "robot_grip_n": robot_hold}


# ---------------------------------------------------------------------
# Cycle and capacity
# ---------------------------------------------------------------------
def cycle():
    """Durations (s) per strip."""
    d = design()
    sg = s_ground()
    t_lay = sg / P.v_layout
    t_fill = litre_per_m() * sg / 1000.0 / d["q"] * 3600.0 * P.fill_time_extra
    t_irr = P.gift / P.infiltration * 3600.0
    t_drain = P.drain_min * 60.0
    t_wind = 0.0
    n = 400
    for i in range(n):
        l_reel = P.reel_reserve + RUN_M + sg * (i + 0.5) / n
        t_wind += sg / n / wind_speed(l_reel)
    t_shift = P.shift_min * 60.0
    return {"lay_out": t_lay, "fill": t_fill, "irrigate": t_irr, "drain": t_drain, "roll_up": t_wind,
            "shift": t_shift, "total": t_lay + t_fill + t_irr + t_drain + t_wind + t_shift}


def capacity():
    c = cycle()
    d = design()
    l_wet = len(outlets()) * P.outlet_pitch                      # m of strip that gets water
    area = l_wet * P.strip_w                                     # m2 per strip
    strips_day = 24.0 * 3600.0 / c["total"]
    water_strip = d["q"] * (c["irrigate"] + c["fill"]) / 3600.0  # m3
    pump_h = (c["irrigate"] + c["fill"]) / 3600.0
    mm_day_on_ha = strips_day * area * P.gift / 1e4              # mm per day spread over 1 ha
    pp = pump(d["q"], d["h_in"])
    return {"strip_len_m": l_wet, "strip_area_m2": area, "strips_day": strips_day,
            "ha_day_at_gift": strips_day * area / 1e4, "water_strip_m3": water_strip,
            "pump_share": pump_h * strips_day / 24.0, "ha_at_et": mm_day_on_ha / P.et_day,
            "fuel_l_day": pp["fuel_l_h"] * pump_h * strips_day,
            "fuel_l_mm_ha": pp["fuel_l_h"] * pump_h / (area * P.gift / 1e4)}


def energy():
    c = cycle()
    sg = s_ground()
    drive_wh = 2.0 * sg / P.v_layout * P.drive_w / 3600.0
    reel_wh = reel_drive()["power_w"] * c["roll_up"] / 3600.0
    idle_wh = P.idle_w * c["total"] / 3600.0
    per_strip = drive_wh + reel_wh + idle_wh
    strips_day = 24.0 * 3600.0 / c["total"]
    return {"wh_strip": per_strip, "wh_day": per_strip * strips_day, "days_per_charge": P.battery_wh / (per_strip *
                                                                                                         strips_day)}


# ---------------------------------------------------------------------
# Axle loads and stability
# ---------------------------------------------------------------------
def axle_loads(extra_kg=0.0, extra_cg=None):
    items = [(ROBOT["robot_kg"], ROBOT["robot_cg"]), (MODEL["kg"], MODEL["cg"])]
    if extra_kg:
        items.append((extra_kg, extra_cg))
    m = sum(i[0] for i in items)
    cg = [sum(i[0] * i[1][k] for i in items) / m for k in range(3)]
    front = m * (HALF_BASE + cg[1]) / (2.0 * HALF_BASE)
    return {"kg": m, "cg": cg, "front_kg": front, "rear_kg": m - front,
            "tip_side_deg": math.degrees(math.atan(P.robot_wheel_x / cg[2])),
            "tip_rear_deg": math.degrees(math.atan((HALF_BASE + cg[1]) / cg[2]))}


def report():
    h = hose()
    d = design()
    pp = pump(d["q"], d["h_in"])
    rd = reel_drive()
    pc = pinch()
    c = cycle()
    cap = capacity()
    e = energy()
    al = axle_loads()
    print("Hose: 3\" lay-flat %.0f m, flat %.0f x %.1f mm, %.1f kg empty, %d outlets (%d on the ground)"
          % (P.hose_len, h["flat_w"], h["flat_t"], h["mass_empty_kg"], h["outlets_total"], h["outlets_on_ground"]))
    print("  %.2f l/m; full strip %d l = %d kg in the field (the robot never carries it)" % (
        h["l_per_m"], h["full_l"], h["full_kg_on_ground"]))
    print("  coil O%d mm full (flange O%.0f, margin %.0f mm), O%d with the reserve, %.0f turns"
          % (h["coil_d_full"], P.flange_d, h["flange_margin"], h["coil_d_reserve"], h["reel_turns"]))
    print("Hydraulics: target %.1f m3/h (%.0f l/h per outlet, %.0f mm/h on %.0f x %.0f m)"
          % (d["target"], d["target"] / len(d["pos"]) * 1000, P.infiltration, P.outlet_pitch, P.strip_w))
    print("  inlet %.2f m (%.3f bar), end %.2f m, friction %.2f m, outlets O%.1f: %.0f .. %.0f l/h"
          % (d["h_in"], d["h_in"] * 0.0981, d["h_end"], d["loss_m"], P.outlet_d, min(d["flows"]) * 1000,
             max(d["flows"]) * 1000))
    print("  CU %.1f %%, DU(lq) %.1f %%, min/max %.2f" % (d["cu"] * 100, d["du_lq"] * 100, d["min_max"]))
    for s in (-0.005, 0.005):
        ds = design(s)
        print("  slope %+.1f %%: inlet %.2f m, CU %.1f %%, min/max %.2f" % (s * 100, ds["h_in"], ds["cu"] * 100,
                                                                          ds["min_max"]))
    print("Pump: %.2f m head, throttle %.2f%s, hydraulic %.0f W, shaft %.0f W, %.2f l/h petrol"
          % (pp["h_pump"], pp["throttle"], " (below the lowest throttle: bypass)" if pp["below_min"] else "",
             pp["p_hyd_w"], pp["p_shaft_w"], pp["fuel_l_h"]))
    print("Reel: need %.0f Nm (%.0f N at O%d), have %.0f Nm (x %.1f); %.0f rpm max; winding %.2f .. %.2f m/s; %.0f W"
          % (rd["torque_need_nm"], P.tension_wind, h["coil_d_full"], rd["torque_have_nm"], rd["reserve"],
             rd["reel_rpm_max"], rd["v_wind_min"], min(rd["v_wind_full"], P.v_rollup_max), rd["power_w"]))
    print("Pinch: %.1f kPa at the robot, pull on the robot %.0f N (grip %.0f N); clamp %.0f N, needs ~%.0f N"
          % (pc["p_end_kpa"], pc["pull_n"], pc["robot_grip_n"], pc["clamp_n"], pc["clamp_need_n"]))
    print("Cycle per strip (min): " + ", ".join("%s %.1f" % (k, v / 60.0) for k, v in c.items()))
    print("Capacity: strip %.0f x %.0f m = %.0f m2, %.1f strips/day, %.2f ha/day at %.0f mm, %.0f m3 per strip"
          % (cap["strip_len_m"], P.strip_w, cap["strip_area_m2"], cap["strips_day"], cap["ha_day_at_gift"], P.gift,
             cap["water_strip_m3"]))
    print("  pump runs %.0f %% of the time; keeps up with %.1f mm/day on %.1f ha; petrol %.1f l/day (%.1f l per mm.ha)"
          % (cap["pump_share"] * 100, P.et_day, cap["ha_at_et"], cap["fuel_l_day"], cap["fuel_l_mm_ha"]))
    print("Robot energy: %.0f Wh/strip, %.0f Wh/day, %.1f days per charge" % (e["wh_strip"], e["wh_day"],
                                                                             e["days_per_charge"]))
    print("Mass: implement %.1f kg (model), robot + implement %.0f kg, cg z %.0f; front %.0f kg, rear %.0f kg"
          % (MODEL["kg"], al["kg"], al["cg"][2], al["front_kg"], al["rear_kg"]))
    print("  static tipping: sideways %.0f deg, backwards %.0f deg" % (al["tip_side_deg"], al["tip_rear_deg"]))


if __name__ == "__main__":
    report()
