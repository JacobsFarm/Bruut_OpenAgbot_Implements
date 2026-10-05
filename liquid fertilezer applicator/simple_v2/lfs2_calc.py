"""Berekeningen voor de onderbouwing van de eenvoudige toediener versie 2, met snijschijven (puur Python).

Gebruik:  import lfs2_calc; lfs2_calc.report()        (of: python lfs2_calc.py)
Massa's komen uit het FreeCAD-model (build_lfs2.mass_properties) en staan in MODEL; geef nieuwe waarden mee
met report(model={...}). Aannames (trekkracht, zuigkracht, robot) staan bovenaan en zijn geschat, niet gemeten.
"""
import math

import lfs2_params as P
import lfs2_kin as K

G_ACC = 9.81

# laatste meting uit het model (build_lfs2.mass_properties: staal 7850 kg/m3, gekochte delen als vaste massa)
MODEL = {
    "implement_kg": 101.4,      # heel werktuig incl. bok, doseerunit, actuator, slangen
    "implement_cg": (-317.0, 299.0),
    "moving_kg": 70.2,          # hefraam: balk, armen, 5 elementen (schijf + mes), 2 dieptewielen
    "moving_cg": (-420.0, 204.0),
    "knife_unit_kg": 9.1,       # een element: houder, schijfarm, schijf met naaf, mes, buisje
    "gauge_wheel_kg": 7.0,
}

# aannames bodem per element (schatting voor grasland; meten in de veldproef met een veerunster)
#   disc_vertical: kracht die de schijf nodig heeft om 40 mm de zode in te gaan (drukt het hefraam omhoog)
#   disc_draft: trekkracht van de schijf (rollen + snijden); knife_draft: mes in de voorgesneden snede
LOADS = {
    "normaal": {"disc_vertical": 100.0, "disc_draft": 30.0, "knife_draft": 60.0},
    "zwaar": {"disc_vertical": 200.0, "disc_draft": 50.0, "knife_draft": 125.0},
}
SOIL = {
    "suction": 0.3,             # neerwaartse kracht op de mespunt / trekkracht mes (zuighoek 15 graden)
    "rolling": 0.08,            # rolweerstand kruiwagenwiel in gras
}

# aannames robot (gelijk aan de geavanceerde variant, lfa_calc.ROBOT)
ROBOT = {
    "robot_kg": 150.0,          # robot zonder tank
    "robot_cg_from_rear": 500.0,  # mm voor de achteras
    "tank_l": 150.0,
    "liquid_density": 1.2,      # kg/l
    "tank_cg_from_rear": 150.0,
    "wheelbase": 1000.0,
    "traction_mu": 0.5,         # grip banden in gras (alle 4 wielen aangedreven)
}

# actuator (koopdeel): kracht en snelheid uit een typische datasheet 12 V, 200 mm slag
ACTUATOR = {"force_n": 1500.0, "speed_mm_s": 20.0}

# breekbout M6 klasse 4.6, dubbelsnedig (mes tussen twee zijplaten)
SHEAR = {"fub": 400.0, "area": 20.1}


# ---------------------------------------------------------------------
# Dosering: doseerplaatje onder constante druk, dosis volgt de rijsnelheid
# ---------------------------------------------------------------------
def orifice_flow_l_min(d_mm, p_bar=P.pressure_bar, cd=P.orifice_cd, rho=P.liquid_density):
    """Debiet door een doseerplaatje (l/min). Drukval = regeldruk - openingsdruk antidruppelklep."""
    dp = max(0.0, (p_bar - P.check_valve_bar)) * 1.0e5
    area = math.pi * (d_mm / 1000.0) ** 2 / 4.0
    q = cd * area * math.sqrt(2.0 * dp / (rho * 1000.0))       # m3/s
    return q * 1000.0 * 60.0


def dose_l_ha(d_mm, speed=P.work_speed, p_bar=P.pressure_bar):
    area_per_min = P.row_spacing / 1000.0 * speed * 60.0          # m2 per minuut per rij
    return orifice_flow_l_min(d_mm, p_bar) / area_per_min * 10000.0


def dose_table(speeds=(0.5, 0.75, 1.0), p_bar=P.pressure_bar):
    rows = []
    for d in P.orifice_sizes:
        rows.append((d, round(orifice_flow_l_min(d, p_bar), 2)) + tuple(round(dose_l_ha(d, v, p_bar)) for v in speeds))
    return rows


def orifice_for_dose(dose, speed=P.work_speed, p_bar=P.pressure_bar):
    """Benodigde doorlaat (mm) voor een dosis (l/ha) bij een snelheid."""
    lo, hi = 0.1, 5.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if dose_l_ha(mid, speed, p_bar) < dose:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------
# Hefraam in werkstand: trekkracht, gewicht, zuigkracht en dieptewielen (momenten om het draaipunt)
# ---------------------------------------------------------------------
def levers(psi=0.0):
    """Hefbomen om het draaipunt (mm): gewicht, mespunt (horizontaal en verticaal), schijf (contactpunt
    horizontaal, trekkracht verticaal op halve diepte) en dieptewiel."""
    pv = P.pivot
    cg = K.rot_up(MODEL["moving_cg"], psi)
    tip = K.rot_up(K.knife_tip(), psi)
    wheel = K.rot_up(P.gw_axle, psi)
    disc = K.rot_up(P.disc_center, psi)
    return {"weight": pv[0] - cg[0], "tip_h": pv[0] - tip[0], "tip_v": pv[1] - tip[1],
            "disc_h": pv[0] - disc[0], "disc_v": pv[1] + P.work_depth / 2.0, "wheel": pv[0] - wheel[0]}


def frame_forces(case="normaal", extra_kg=0.0, psi=0.0, disc_vertical=None):
    """Krachten op het hefraam in zweefstand (5 elementen). Geeft dict met de kracht op de dieptewielen
    (totaal 2 wielen) en in het draaipunt. extra_kg = ballast op de balk (op het zwaartepunt gedacht)."""
    ld = dict(LOADS[case])
    if disc_vertical is not None:
        ld["disc_vertical"] = disc_vertical
    n = len(P.row_x)
    fk = ld["knife_draft"] * n
    fdd = ld["disc_draft"] * n
    fdv = ld["disc_vertical"] * n
    s = SOIL["suction"] * fk
    w = (MODEL["moving_kg"] + extra_kg) * G_ACC
    lv = levers(psi)
    m_down = w * lv["weight"] + s * lv["tip_h"]
    m_up = fk * lv["tip_v"] + fdd * lv["disc_v"] + fdv * lv["disc_h"]
    wheel_n = (m_down - m_up) / lv["wheel"]
    return {"draft_total_N": round(fk + fdd), "disc_vertical_N": round(fdv), "suction_N": round(s),
            "weight_N": round(w), "moment_down_Nm": round(m_down / 1000.0, 1),
            "moment_up_Nm": round(m_up / 1000.0, 1),
            "moment_up_parts_Nm": {"knife_draft": round(fk * lv["tip_v"] / 1000.0, 1),
                                   "disc_draft": round(fdd * lv["disc_v"] / 1000.0, 1),
                                   "disc_vertical": round(fdv * lv["disc_h"] / 1000.0, 1)},
            "wheel_load_N": round(wheel_n), "wheel_load_each_N": round(wheel_n / 2.0),
            "pivot_vertical_N": round(w + s - wheel_n - fdv), "pivot_horizontal_N": round(fk + fdd),
            "rolling_resistance_N": round(max(0.0, wheel_n) * SOIL["rolling"])}


def max_disc_force(case="normaal", extra_kg=0.0):
    """Neerdruk per schijf die het hefraam kan leveren voordat de dieptewielen loskomen (N)."""
    lo, hi = 0.0, 2000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if frame_forces(case, extra_kg, disc_vertical=mid)["wheel_load_N"] > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def ballast_for(case="zwaar", wheel_n=0.0):
    """Ballast (kg) op de balk waarmee de dieptewielen nog wheel_n N dragen."""
    lo, hi = 0.0, 300.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if frame_forces(case, mid)["wheel_load_N"] < wheel_n:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------
# Mes: sterkte en breekbout
# ---------------------------------------------------------------------
def knife_section():
    w, t = P.knife_w, P.knife_t
    return {"W_fore_aft_mm3": t * w * w / 6.0, "W_side_mm3": w * t * t / 6.0}


def shear_trip_force():
    """Horizontale kracht op de mespunt waarbij de breekbout (dubbelsnedig) breekt (N)."""
    f_bolt = 2.0 * 0.6 * SHEAR["fub"] * SHEAR["area"]
    m = f_bolt * P.shear_dist
    lever = P.knife_pivot[1] - K.knife_tip()[1]
    return f_bolt, m / lever, m


def knife_stress(force_n):
    """Buigspanning (MPa) in het mes bij de draaibout door een horizontale kracht op de punt."""
    lever = P.knife_pivot[1] - K.knife_tip()[1]
    return force_n * lever / knife_section()["W_fore_aft_mm3"]


# ---------------------------------------------------------------------
# Heffen
# ---------------------------------------------------------------------
def tip_clear_angle(clear=0.0):
    """Hefhoek waarbij mespunt en schijf allebei clear mm boven het maaiveld komen."""
    tip = K.knife_tip()
    r = P.disc_d / 2.0

    def low(psi):
        return min(K.rot_up(tip, psi)[1], K.rot_up(P.disc_center, psi)[1] - r)
    lo, hi = 0.0, 60.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if low(mid) < clear:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def lift_force(safety=1.5):
    """Actuatorkracht (N) om het hefraam te heffen: gewichtsmoment x veiligheid / hefboom, aan het begin en
    het eind van de slag."""
    w = MODEL["moving_kg"] * G_ACC
    out = []
    for psi in (0.0, K.lift_angle()):
        lever_w = P.pivot[0] - K.rot_up(MODEL["moving_cg"], psi)[0]
        length = K.dist(P.act_a, K.frame_pin(psi))
        out.append(w * lever_w * safety / K.act_lever(psi, length))
    return out


def lift_times():
    """(vrije slag mm, slag tot de messen boven de grond mm, totale slag mm, tijden s)."""
    free = P.act_extended - K.dist(P.act_a, K.frame_pin(0.0))
    psi_c = tip_clear_angle(0.0)
    clear = P.act_extended - K.dist(P.act_a, K.frame_pin(psi_c))
    total = P.act_stroke
    v = ACTUATOR["speed_mm_s"]
    return free, clear, total, (free / v, clear / v, total / v)


# ---------------------------------------------------------------------
# Gewichtsverdeling van de robot
# ---------------------------------------------------------------------
def axle_loads(working=True, robot=None, case="normaal", tank_full=True, extra_kg=0.0):
    """Asbelasting robot (N): (voor, achter). Werkstand: het hefraam rust op de dieptewielen en messen, de robot
    draagt de bok + doseerunit, de kracht in het draaipunt en de trekkracht (aangrijpend op de hoogte van het
    draaipunt). Geheven: het hele werktuig hangt aan de robot."""
    r = dict(ROBOT)
    if robot:
        r.update(robot)
    ax = P.robot_wheel_y                                  # achteras in werktuig-y
    L = r["wheelbase"] / 1000.0
    w_robot = r["robot_kg"] * G_ACC
    w_tank = r["tank_l"] * r["liquid_density"] * G_ACC if tank_full else 0.0
    m_fixed = MODEL["implement_kg"] - MODEL["moving_kg"]
    m_mov = MODEL["moving_kg"] + extra_kg
    cg_all = MODEL["implement_cg"]
    cg_mov = MODEL["moving_cg"]
    # zwaartepunt van het vaste deel (bok, doseerunit, actuator) uit het totaal en het bewegende deel
    cg_fixed_y = (MODEL["implement_kg"] * cg_all[0] - MODEL["moving_kg"] * cg_mov[0]) / m_fixed
    loads = []                                            # (kracht N omlaag, afstand achter de achteras m)
    if working:
        ff = frame_forces(case, extra_kg)
        loads.append((m_fixed * G_ACC, (ax - cg_fixed_y) / 1000.0))
        loads.append((ff["pivot_vertical_N"], (ax - P.pivot[0]) / 1000.0))
        pull = ff["pivot_horizontal_N"] * P.pivot[1] / 1000.0          # trekkracht op hoogte draaipunt: neus omhoog
    else:
        psi = K.lift_angle()
        cg_l = K.rot_up(cg_mov, psi)
        loads.append((m_fixed * G_ACC, (ax - cg_fixed_y) / 1000.0))
        loads.append((m_mov * G_ACC, (ax - cg_l[0]) / 1000.0))
        pull = 0.0
    m_front = w_robot * r["robot_cg_from_rear"] / 1000.0 + w_tank * r["tank_cg_from_rear"] / 1000.0
    m_front -= sum(f * d for f, d in loads) + pull
    n_front = m_front / L
    n_rear = w_robot + w_tank + sum(f for f, d in loads) - n_front
    return n_front, n_rear


def traction_check(case="normaal", extra_kg=0.0):
    """Benodigde trekkracht (schijven, messen, rolweerstand dieptewielen) t.o.v. de grip van de robot (lege tank)."""
    ff = frame_forces(case, extra_kg)
    need = ff["draft_total_N"] + ff["rolling_resistance_N"]
    nf, nr = axle_loads(True, case=case, tank_full=False, extra_kg=extra_kg)
    grip = ROBOT["traction_mu"] * (nf + nr)
    return need, grip


# ---------------------------------------------------------------------
# Kosten (indicatief, euro excl. btw, prijsniveau 2026, losse aankoop in NL/webshop)
# ---------------------------------------------------------------------
COST = (
    ("staal: strip, koker, plaat (ca. 52 kg, zagen en boren)", 135),
    ("5 vlakke kouterschijven O 300 x 4, gehard", 125),
    ("5 lagernaven met 4-gats flens (2 x 6204-2RS), asbouten M20", 160),
    ("beugelbouten M12 (10) en M10 (4) voor koker 60x60", 45),
    ("bouten en moeren M10, M12, M16, M20, breekbouten M6 (reserve)", 30),
    ("2 kruiwagenwielen 3.00-4 met lagers, as 20 mm", 35),
    ("lineaire actuator 12 V, 1500 N, slag 200, IP65", 110),
    ("membraanpomp 12 V met interne bypass, ca. 7 l/min, 4 bar", 70),
    ("zuigfilter 50 mesh, camlock 1\", zuigslang", 40),
    ("vaste drukregelaar 2,0 bar en manometer", 25),
    ("verdeelblok 5x en 5 spuitdophouders met membraanklep, doseerplaatjes (set)", 75),
    ("RVS-buis 10 x 1 (2 m), P-clips, PVC-slang 8 x 12 (10 m), slangklemmen", 45),
    ("relais, zekering, kabel naar de robot", 20),
)


def cost_total():
    return sum(c for _, c in COST)


# ---------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------
def report(model=None):
    if model:
        MODEL.update(model)
    out = {}
    out["work_width_m"] = P.work_width / 1000.0
    out["rows"] = len(P.row_x)
    out["work_depth_mm"] = P.work_depth
    out["orifice_flow_l_min_1.0mm"] = round(orifice_flow_l_min(P.orifice_d), 3)
    out["dose_l_ha_1.0mm_0.75ms"] = round(dose_l_ha(P.orifice_d))
    out["pump_flow_needed_l_min_1.0mm"] = round(orifice_flow_l_min(P.orifice_d) * len(P.row_x), 2)
    out["orifice_for_500_l_ha_mm"] = round(orifice_for_dose(500.0), 2)
    out["orifice_for_100_l_ha_mm"] = round(orifice_for_dose(100.0), 2)
    out["dose_change_speed_+10pct"] = round(100.0 * (1.0 / 1.1 - 1.0), 1)
    out["dose_change_pressure_+0.1bar"] = round(100.0 * (math.sqrt((P.pressure_bar + 0.1 - P.check_valve_bar)
                                                                 / (P.pressure_bar - P.check_valve_bar)) - 1.0), 1)
    lv = levers()
    out["levers_mm"] = {k: round(v) for k, v in lv.items()}
    out["frame_normal"] = frame_forces("normaal")
    out["frame_heavy"] = frame_forces("zwaar")
    out["max_disc_force_normal_N"] = round(max_disc_force("normaal"))
    out["ballast_heavy_kg"] = round(ballast_for("zwaar"), 1)
    out["ballast_heavy_100N_wheels_kg"] = round(ballast_for("zwaar", 100.0), 1)
    out["frame_heavy_with_ballast"] = frame_forces("zwaar", round(ballast_for("zwaar", 100.0)))
    f_bolt, trip, m = shear_trip_force()
    out["shear_bolt_N"] = round(f_bolt)
    out["shear_trip_tip_N"] = round(trip)
    out["knife_stress_at_trip_MPa"] = round(knife_stress(trip))
    out["knife_stress_normal_MPa"] = round(knife_stress(LOADS["normaal"]["knife_draft"]), 1)
    out["float_range_deg"] = tuple(round(a, 1) for a in K.float_range())
    lo, hi = K.float_range()
    out["float_wheel_mm"] = (round(K.rot_up(P.gw_axle, lo)[1] - P.gw_axle[1]),
                             round(K.rot_up(P.gw_axle, hi)[1] - P.gw_axle[1]))
    out["knife_angle_range_deg"] = (round(P.knife_angle - hi, 1), round(P.knife_angle - lo, 1))   # + psi = steiler
    out["lift_angle_deg"] = round(K.lift_angle(), 1)
    out["tip_lifted"] = tuple(round(v) for v in K.rot_up(K.knife_tip(), K.lift_angle()))
    out["disc_lifted_clearance_mm"] = round(K.rot_up(P.disc_center, K.lift_angle())[1] - P.disc_d / 2.0)
    out["disc_knife_gap_mm"] = round(K.disc_knife_gap(), 1)
    out["wheel_lifted_clearance_mm"] = round(K.rot_up(P.gw_axle, K.lift_angle())[1] - P.gw_d / 2.0)
    out["act_lever_mm"] = (round(K.act_lever(0.0)), round(K.act_lever(K.lift_angle(), P.act_retracted)))
    out["act_force_N"] = tuple(round(f) for f in lift_force())
    free, clear, total, times = lift_times()
    out["act_free_travel_mm"] = round(free)
    out["act_stroke_until_knives_out_mm"] = round(clear)
    out["lift_time_s"] = tuple(round(t, 1) for t in times)
    out["slot_len_mm"] = round(K.slot_len())
    for name, kw in (("work_full", dict(working=True)), ("work_empty", dict(working=True, tank_full=False)),
                     ("lifted_full", dict(working=False)), ("lifted_empty", dict(working=False, tank_full=False))):
        nf, nr = axle_loads(**kw)
        out["axle_" + name + "_N"] = (round(nf), round(nr))
    nf, nr = axle_loads(False, tank_full=False, extra_kg=round(ballast_for("zwaar", 100.0)))
    out["axle_lifted_empty_with_ballast_N"] = (round(nf), round(nr))
    need, grip = traction_check()
    out["traction_need_N"] = round(need)
    out["traction_grip_empty_N"] = round(grip)
    need_h, _ = traction_check("zwaar")
    out["traction_need_heavy_N"] = round(need_h)
    out["capacity_ha_h_0.75ms"] = round(P.work_width / 1000.0 * P.work_speed * 3600 / 10000.0, 2)
    out["cost_eur"] = cost_total()
    return out


if __name__ == "__main__":
    for k, v in report().items():
        print(k, v)
    print("doseerplaatje (mm), debiet (l/min), l/ha bij 0,5 / 0,75 / 1,0 m/s")
    for row in dose_table():
        print(row)
