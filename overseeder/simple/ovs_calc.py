"""Berekeningen voor de onderbouwing van de doorzaaimachine (puur Python).

Gebruik:  import ovs_calc; ovs_calc.report()        (of: python ovs_calc.py)
Massa's komen uit het FreeCAD-model (build_ovs.mass_properties) en staan in MODEL. Aannames (bodemkrachten, robot,
zaad) staan bovenaan en zijn geschat, niet gemeten.
"""
import math

import ovs_params as P
import ovs_kin as K

G_ACC = 9.81

# laatste meting uit het model (build_ovs.mass_properties: staal 7850, aluminium 2700 kg/m3, gekochte delen vast)
MODEL = {
    "implement_kg": 136.3,      # heel werktuig, lege zaadbak
    "implement_cg": (-404.0, 313.0),
    "moving_kg": 103.5,         # hefraam: balk, armen, zaadbak + dosering, 8 elementen
    "moving_cg": (-506.0, 245.0),
    "arm_kg": 6.69,             # een sleeparm met schijf, naaf, ring, schoen, rolarm en aandrukrol
    "arm_cg": (-618.0, 122.0),
    "seed_box_kg": 16.5,
}

# zaad in de bak (standaard: grasvak vol, 5 kg klaver in het fijne vak); zwaartepunt ongeveer midden in de bak
SEED = {"kg": 20.0, "cg": (-480.0, 600.0)}

# aannames bodem per element bij 15 mm snijdiepte (schatting voor grasland; meten met een veerunster/weegschaal:
# schijf op een balkje met gewichten de zode in drukken)
#   disc_vertical: kracht die de schijf nodig heeft om 15 mm de zode in te gaan
#   disc_draft: trekkracht schijf (rollen + snijden, 7 graden scheef), boot_draft: schoen in de open sleuf
#   band_min: kracht die op de dieptering moet blijven (anders komt de schijf niet op diepte)
#   de aandrukrol drukt met zijn eigen torsieveer (P.pw_force), los van de diepte
LOADS = {
    "normaal": {"disc_vertical": 90.0, "disc_draft": 25.0, "boot_draft": 8.0, "band_min": 20.0},
    "zwaar": {"disc_vertical": 180.0, "disc_draft": 45.0, "boot_draft": 15.0, "band_min": 20.0},
}
SOIL = {
    "rolling": 0.10,            # rolweerstand smalle aandrukrol en dieptering in gras
    "side": 0.4,                # zijkracht schijf / trekkracht schijf (schijf 7 graden scheef)
}
# aangrijppunten t.o.v. hart schijf (schatting): verticale kracht op het voorste deel van de snede, trek op halve diepte
DISC_FORCE_DY = 30.0
BOOT_POINT = (-40.0, -6.0)      # (y t.o.v. hart schijf, z)

# aannames robot (gelijk aan de toedieners; geen vloeistoftank bij het zaaien)
ROBOT = {
    "robot_kg": 150.0,
    "robot_cg_from_rear": 500.0,    # mm voor de achteras
    "wheelbase": 1000.0,
    "traction_mu": 0.5,             # grip in gras, alle 4 wielen aangedreven
    "front_ballast_kg": 0.0,        # frontgewicht op de vooras
}

ACTUATOR = {"force_n": 3000.0, "speed_mm_s": 12.0}     # 12 V, 3000 N, slag 150 (typisch datablad)

# zaad: storthoogte-dichtheid (kg/l) en zaaihoeveelheid (kg/ha); dichtheden zijn richtwaarden, ijken!
SEEDS = (
    ("Engels raaigras (tetraploid)", 0.35, (15.0, 25.0, 40.0), "main"),
    ("Engels raaigras (diploid)", 0.40, (15.0, 25.0, 40.0), "main"),
    ("witte klaver", 0.78, (3.0, 5.0, 6.0), "fine"),
    ("rode klaver", 0.78, (10.0, 12.0, 13.0), "fine"),
    ("cichorei / smalle weegbree", 0.50, (2.0, 4.0, 6.0), "fine"),
)


# ---------------------------------------------------------------------
# Dosering
# ---------------------------------------------------------------------
def roll_rpm(dose_kg_ha, density_kg_l, roll="main", speed=P.work_speed):
    """Toerental nokkenrol (omw/min) voor een dosis bij een rijsnelheid."""
    g_per_s_row = dose_kg_ha * 0.1 * (P.row_spacing / 1000.0) * speed      # 1 kg/ha = 0,1 g/m2
    cc_per_s = g_per_s_row / density_kg_l
    cc_rev = P.roll_main_cc if roll == "main" else P.roll_fine_cc
    return cc_per_s / cc_rev * 60.0


def dose_table(speed=P.work_speed):
    rows = []
    for name, rho, doses, roll in SEEDS:
        rows.append((name, roll, tuple((d, round(roll_rpm(d, rho, roll, speed), 1)) for d in doses)))
    return rows


def max_speed(dose_kg_ha, density_kg_l, roll="main"):
    """Hoogste rijsnelheid (m/s) waarbij de motor de dosis nog haalt."""
    return P.work_speed * P.motor_rpm_max / roll_rpm(dose_kg_ha, density_kg_l, roll)


def hopper_area_ha(dose_main=40.0, rho_main=0.35, dose_fine=5.0, rho_fine=0.78):
    """Oppervlak (ha) per vulling, per vak."""
    v_main, v_fine = K.hopper_volumes_l()
    return v_main * rho_main / dose_main, v_fine * rho_fine / dose_fine


# ---------------------------------------------------------------------
# Krachten per element en op het hefraam (werkstand, psi = 0, phi = 0)
# ---------------------------------------------------------------------
def unit_points():
    """Aangrijppunten (y, z) in werkstand."""
    c = P.disc_center
    return {"disc_v": (c[0] + DISC_FORCE_DY, -P.disc_depth), "disc_h": (c[0] + DISC_FORCE_DY, -P.disc_depth / 2.0),
            "boot": (c[0] + BOOT_POINT[0], BOOT_POINT[1]), "pw": (P.pw_axle[0], 0.0), "band": (c[0], 0.0)}


def _levers(center):
    """Hefbomen om center: verticale krachten (horizontale afstand), horizontale krachten (hoogte)."""
    pt = unit_points()
    return {"disc_v": center[0] - pt["disc_v"][0], "disc_h": center[1] - pt["disc_h"][1],
            "boot": center[1] - pt["boot"][1], "pw_v": center[0] - pt["pw"][0], "pw_h": center[1] - pt["pw"][1],
            "band_v": center[0] - pt["band"][0], "band_h": center[1] - pt["band"][1]}


def spring_lever():
    """Hefboom (mm) van de veerkracht om het armdraaipunt in werkstand."""
    return K.spring_moment(0.0) / max(K.spring_force(0.0), 1e-9)


def _soil_moment(ld, lv, pw):
    """Moment (Nmm) van de vaste grondkrachten (schijf, schoen, aandrukrol) om het punt van lv."""
    return (ld["disc_vertical"] * lv["disc_v"] + ld["disc_draft"] * lv["disc_h"] + ld["boot_draft"] * lv["boot"]
            + pw * (lv["pw_v"] + SOIL["rolling"] * lv["pw_h"]))


def unit_band(spring_n, case="normaal", pw=None):
    """Kracht op de dieptering (N) bij veerkracht spring_n (armbalans om het armdraaipunt). Negatief = de schijf
    haalt zijn diepte niet."""
    ld = LOADS[case]
    pw = P.pw_force if pw is None else pw
    lv = _levers(P.u_pivot)
    m_w = MODEL["arm_kg"] * G_ACC * (P.u_pivot[0] - MODEL["arm_cg"][0])
    return (spring_n * spring_lever() + m_w - _soil_moment(ld, lv, pw)) / (lv["band_v"] + SOIL["rolling"] * lv["band_h"])


def spring_for_band(band, case="normaal"):
    """Veerkracht (N) die nodig is voor band N op de dieptering."""
    lo, hi = -2000.0, 5000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if unit_band(mid, case) < band:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def frame_balance(case="normaal", seed_kg=None, ballast_kg=0.0, rows=None, gas_n=None):
    """Hefraam zwevend in werkstand. Omlaag: gewicht van hefraam, zaad en ballast plus de gasveren (via de
    actuator, robotgewicht). Omhoog: de grondkrachten van de elementen. De schijf, de schoen en de aandrukrol
    vragen een vaste kracht; wat overblijft draagt de dieptering. De voorspanning van de veren bepaalt alleen op
    welke hoogte het hefraam zweeft, niet hoeveel neerdruk er is."""
    ld = LOADS[case]
    n = len(P.row_x) if rows is None else rows
    seed_kg = SEED["kg"] if seed_kg is None else seed_kg
    gas_n = K.gas_force(0.0) if gas_n is None else gas_n
    lv = _levers(P.pivot)
    m_rows = (len(P.row_x) - n) * (MODEL["arm_kg"] + 2.8)       # uitgezette elementen (arm + houder) eraf
    w = (MODEL["moving_kg"] - m_rows) * G_ACC
    m_down = w * (P.pivot[0] - MODEL["moving_cg"][0]) + seed_kg * G_ACC * (P.pivot[0] - SEED["cg"][0]) \
        + ballast_kg * G_ACC * (P.pivot[0] - P.bar_y)
    m_gas = gas_n * K.act_lever(0.0)
    m_fixed = n * _soil_moment(ld, lv, P.pw_force)
    lever_band = n * (lv["band_v"] + SOIL["rolling"] * lv["band_h"])
    band = (m_down + m_gas - m_fixed) / lever_band
    w_total = w + (seed_kg + ballast_kg) * G_ACC
    ground_v = n * (ld["disc_vertical"] + max(band, 0.0) + P.pw_force)
    draft = n * (ld["disc_draft"] + ld["boot_draft"] + SOIL["rolling"] * (max(band, 0.0) + P.pw_force))
    return {"rows": n, "gas_N": round(gas_n), "weight_N": round(w_total),
            "band_each_N": round(band, 1), "band_ok": band >= ld["band_min"] - 1e-6, "pw_each_N": P.pw_force,
            "unit_down_each_N": round(ld["disc_vertical"] + band + P.pw_force, 1),
            "spring_for_float_N": round(spring_for_band(band, case)),
            "robot_vertical_N": round(w_total - ground_v), "draft_N": round(draft),
            "side_force_N": round(n * SOIL["side"] * ld["disc_draft"]),
            "moment_weight_Nm": round(m_down / 1000.0), "moment_gas_Nm": round(m_gas / 1000.0),
            "moment_soil_Nm": round((m_fixed + band * lever_band) / 1000.0)}


def gas_for(case="normaal", seed_kg=0.0, rows=None, ballast_kg=0.0):
    """Gasveerkracht (N, beide samen) waarmee elke dieptering band_min houdt (standaard: lege bak)."""
    lo, hi = -3000.0, 6000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if frame_balance(case, seed_kg, ballast_kg, rows, mid)["band_each_N"] < LOADS[case]["band_min"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def ballast_for(case="zwaar", seed_kg=0.0, rows=None):
    """Ballast (kg) op de balk die nodig is zonder gasveren (lege bak)."""
    lo, hi = 0.0, 400.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if frame_balance(case, seed_kg, mid, rows, 0.0)["band_each_N"] < LOADS[case]["band_min"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def max_disc_force(seed_kg=0.0, rows=None, gas_n=0.0):
    """Neerdruk per schijf (N) die gewicht (+ gasveren) kan leveren met band_min op de dieptering (lege bak)."""
    lo, hi = 0.0, 1000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        LOADS["_probe"] = dict(LOADS["normaal"], disc_vertical=mid)
        if frame_balance("_probe", seed_kg, 0.0, rows, gas_n)["band_each_N"] >= LOADS["normaal"]["band_min"]:
            lo = mid
        else:
            hi = mid
    LOADS.pop("_probe", None)
    return 0.5 * (lo + hi)


def spring_design():
    """Veer: kracht in werkstand (model) en wat die per element geeft."""
    lever = spring_lever()
    lv = _levers(P.u_pivot)
    dk = P.spring_rate * (P.u_lug_y - P.u_pivot[0]) / (P.disc_center[0] - P.u_pivot[0])    # N veer per mm schijf
    return {"spring_force_work_N": round(K.spring_force(0.0)), "spring_lever_mm": round(lever, 1),
            "band_at_model_setting_N": round(unit_band(K.spring_force(0.0)), 1),
            "band_change_per_10mm_unit_travel_N": round(10.0 * dk * lever / lv["band_v"], 1),
            "preload_nut_per_10N_band_mm": round(10.0 * lv["band_v"] / lever / P.spring_rate, 1)}


def gas_table(case="normaal", rows=None, seed_kg=None, ballast_front=0.0):
    """Per gasveerkracht: kracht op de dieptering, asbelasting, trekkracht en grip."""
    out = []
    for f in (0, 400, 600, 800, 1000, 1300, 1600):
        fb = frame_balance(case, seed_kg, 0.0, rows, float(f))
        nf, nr = axle_loads(True, seed_kg, ballast_front, case, rows=rows, gas_n=float(f))
        out.append((f, fb["band_each_N"], round(nf), round(nr), fb["draft_N"],
                    round(ROBOT["traction_mu"] * (nf + nr))))
    return out


# ---------------------------------------------------------------------
# Heffen en robot
# ---------------------------------------------------------------------
def lift_force(seed_kg=None, safety=1.5):
    seed_kg = SEED["kg"] if seed_kg is None else seed_kg
    out = []
    for psi in (0.0, K.lift_angle()):
        m_w = MODEL["moving_kg"] * G_ACC * (P.pivot[0] - K.rot_up(MODEL["moving_cg"], psi)[0])
        m_w += seed_kg * G_ACC * (P.pivot[0] - K.rot_up(SEED["cg"], psi)[0])
        length = K.dist(P.act_a, K.frame_pin(psi))
        out.append(m_w * safety / K.act_lever(psi, length))
    return out


def clear_angle():
    """Hefhoek waarbij schijf en schoen uit de grond zijn (armen hangen op de aanslag)."""
    def low(psi):
        stop = -P.u_stop_deg if psi > 1.0 else 0.0
        d = K.rot_up(K.arm_point(P.disc_center, stop), psi)[1] - P.disc_d / 2.0
        return d
    lo, hi = 0.0, K.lift_angle()
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if low(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def lift_times():
    v = ACTUATOR["speed_mm_s"]
    free = P.act_extended - K.dist(P.act_a, K.frame_pin(0.0))
    clear = P.act_extended - K.dist(P.act_a, K.frame_pin(clear_angle()))
    return free, clear, P.act_stroke, (free / v, clear / v, P.act_stroke / v)


def axle_loads(working=True, seed_kg=None, ballast_front=None, case="normaal", rows=None, gas_n=None):
    """Asbelasting robot (N): (voor, achter)."""
    r = dict(ROBOT)
    if ballast_front is not None:
        r["front_ballast_kg"] = ballast_front
    seed_kg = SEED["kg"] if seed_kg is None else seed_kg
    ax = P.robot_wheel_y
    L = r["wheelbase"] / 1000.0
    m_fixed = MODEL["implement_kg"] - MODEL["moving_kg"]
    cg_fixed_y = (MODEL["implement_kg"] * MODEL["implement_cg"][0] - MODEL["moving_kg"] * MODEL["moving_cg"][0]) / m_fixed
    loads = [(m_fixed * G_ACC, (ax - cg_fixed_y) / 1000.0)]
    if working:
        fb = frame_balance(case, seed_kg, 0.0, rows, gas_n)
        loads.append((fb["robot_vertical_N"], (ax - P.pivot[0]) / 1000.0))
        pull = fb["draft_N"] * P.pivot[1] / 1000.0
    else:
        psi = K.lift_angle()
        loads.append((MODEL["moving_kg"] * G_ACC, (ax - K.rot_up(MODEL["moving_cg"], psi)[0]) / 1000.0))
        loads.append((seed_kg * G_ACC, (ax - K.rot_up(SEED["cg"], psi)[0]) / 1000.0))
        pull = 0.0
    w_robot = r["robot_kg"] * G_ACC
    w_ball = r["front_ballast_kg"] * G_ACC
    m_front = w_robot * r["robot_cg_from_rear"] / 1000.0 + w_ball * L
    m_front -= sum(f * d for f, d in loads) + pull
    n_front = m_front / L
    n_rear = w_robot + w_ball + sum(f for f, d in loads) - n_front
    return n_front, n_rear


def front_ballast_for(min_share=0.25, seed_kg=None):
    """Frontgewicht (kg) zodat de vooras geheven nog min_share van het robotgewicht (+ ballast) draagt."""
    lo, hi = 0.0, 200.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        nf, nr = axle_loads(False, seed_kg, mid)
        if nf < min_share * (ROBOT["robot_kg"] + mid) * G_ACC:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def traction(case="normaal", seed_kg=None, ballast_front=0.0, rows=None, gas_n=None):
    fb = frame_balance(case, seed_kg, 0.0, rows, gas_n)
    nf, nr = axle_loads(True, seed_kg, ballast_front, case, rows, gas_n)
    return fb["draft_N"], ROBOT["traction_mu"] * (nf + nr)


def module_table():
    """Trekkracht per breedte en rijafstand t.o.v. de grip van de robot (normaal / zwaar), per meter gerekend."""
    out = []
    for width in (1, 2, 3):
        for rows in (8, 4):
            n = width * rows
            d_n = n * (LOADS["normaal"]["disc_draft"] + LOADS["normaal"]["boot_draft"]
                       + SOIL["rolling"] * (LOADS["normaal"]["band_min"] + P.pw_force))
            d_h = n * (LOADS["zwaar"]["disc_draft"] + LOADS["zwaar"]["boot_draft"]
                       + SOIL["rolling"] * (LOADS["zwaar"]["band_min"] + P.pw_force))
            out.append((width, rows, int(1000 / rows), round(d_n), round(d_h)))
    return out


# ---------------------------------------------------------------------
# Vergelijking met de toediener simple_v2 (zelfde robot, zelfde bok)
# ---------------------------------------------------------------------
V2 = {"draft_normal_N": 461, "draft_heavy_N": 875, "moving_kg": 70.2, "depth_mm": 45}


# ---------------------------------------------------------------------
# Kosten (indicatief, euro excl. btw, prijsniveau 2026, losse aankoop in NL/webshop)
# ---------------------------------------------------------------------
COST = (
    ("staal: strip, koker, plaat (ca. 40 kg, zagen, boren, lassen zelf)", 120),
    ("8 vlakke kouterschijven O 300 x 3, gehard", 170),
    ("8 lagernaven 4-gats (2 x 6203-2RS), asbouten M20", 200),
    ("8 massief rubber wielen O 200 x 40 met lagers, 8 rolarmen + torsieveren", 150),
    ("8 diepteringen PE-HD O 270 (+ wisselsets 280 en 260: 16 stuks extra)", 120),
    ("8 drukveren 32 x 4,5, stangen M12 met oog, moeren", 70),
    ("8 zaaischoenen (slijtvast staal 12 mm, laser) + RVS-buis 20 x 1,5", 90),
    ("beugelbouten M12 (16), bouten M8-M20, borgmoeren", 75),
    ("zaadslang 20/26 (6 m)", 30),
    ("zaadbak aluminium 2 mm (lasersnijden + zetten) met deksel", 190),
    ("doseerhuis aluminium, 2 nokkenrollen (POM/PETG), lagers, assen", 130),
    ("2 wormwielmotoren 12 V met encoder", 70),
    ("2 motorregelaars, microcontroller, kastje, kabel naar de robot", 70),
    ("lineaire actuator 12 V, 3000 N, slag 150, IP65", 130),
    ("2 gasveren 400 N, slag 100 (+ set 650 N voor zware zode)", 60),
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
    out["disc_depth_mm"] = P.disc_depth
    out["seed_depth_mm"] = P.disc_depth - P.boot_lift
    out["hopper_l"] = tuple(round(v, 1) for v in K.hopper_volumes_l())
    out["hopper_ha_40kg_grass_5kg_clover"] = tuple(round(v, 2) for v in hopper_area_ha())
    out["capacity_ha_h"] = round(P.work_width / 1000.0 * P.work_speed * 3600 / 10000.0, 2)
    out["spring"] = spring_design()
    out["gas_force_work_N"] = round(K.gas_force(0.0))
    out["frame_normal"] = frame_balance("normaal")
    out["frame_normal_empty"] = frame_balance("normaal", 0.0)
    out["gas_needed_normal_empty_N"] = round(gas_for("normaal"))
    sh = gas_for("zwaar", 0.0)
    out["gas_needed_heavy_empty_N"] = round(sh)
    out["frame_heavy_full_gas_heavy"] = frame_balance("zwaar", None, 0.0, None, sh)
    sh4 = gas_for("zwaar", 0.0, 4)
    out["gas_needed_heavy_empty_4rows_N"] = round(sh4)
    out["frame_heavy_4_rows_full"] = frame_balance("zwaar", None, 0.0, 4, sh4)
    out["ballast_without_gas_normal_empty_kg"] = round(ballast_for("normaal", 0.0), 1)
    out["max_disc_force_weight_only_empty_N"] = round(max_disc_force(0.0))
    out["max_disc_force_with_gas_empty_N"] = round(max_disc_force(0.0, None, K.gas_force(0.0)))
    out["float_range_deg"] = tuple(round(a, 1) for a in K.float_range())
    out["lift_angle_deg"] = round(K.lift_angle(), 1)
    out["clear_angle_deg"] = round(clear_angle(), 1)
    out["act_lever_mm"] = (round(K.act_lever(0.0)), round(K.act_lever(K.lift_angle(), P.act_retracted)))
    out["act_force_N_full"] = tuple(round(f) for f in lift_force())
    free, clear, total, times = lift_times()
    out["act_free_travel_mm"] = round(free)
    out["act_stroke_until_out_of_soil_mm"] = round(clear)
    out["lift_time_s"] = tuple(round(t, 1) for t in times)
    for name, kw in (("work", dict(working=True)), ("lifted_full", dict(working=False)),
                     ("lifted_empty", dict(working=False, seed_kg=0.0)),
                     ("lifted_full_ballast40", dict(working=False, ballast_front=40.0))):
        nf, nr = axle_loads(**kw)
        out["axle_" + name + "_N"] = (round(nf), round(nr))
    out["front_ballast_kg_for_25pct"] = round(front_ballast_for(0.25), 1)
    need, grip = traction()
    out["draft_normal_N"] = need
    out["grip_N"] = round(grip)
    d, g = traction("zwaar", gas_n=sh)
    out["draft_grip_heavy_N"] = (d, round(g))
    d, g = traction("zwaar", rows=4, gas_n=sh4)
    out["draft_grip_heavy_4rows_N"] = (d, round(g))
    d, g = traction("zwaar", gas_n=sh, ballast_front=40.0)
    out["draft_grip_heavy_ballast40_N"] = (d, round(g))
    d, g = traction("normaal", ballast_front=40.0)
    out["draft_grip_normal_ballast40_N"] = (d, round(g))
    out["v2_draft_N"] = (V2["draft_normal_N"], V2["draft_heavy_N"])
    out["cost_eur"] = cost_total()
    return out


if __name__ == "__main__":
    for k, v in report().items():
        print(k, v)
    print("dosering: zaad, rol, (kg/ha, omw/min) bij %.2f m/s" % P.work_speed)
    for row in dose_table():
        print(row)
    for case, rows in (("normaal", None), ("zwaar", None), ("zwaar", 4)):
        print("gasveren %s, %s rijen, volle bak: gasveer N, dieptering N, vooras N, achteras N, trek N, grip N"
              % (case, rows or 8))
        for row in gas_table(case, rows):
            print(row)
    print("breedte m, rijen/m, rijafstand mm, trekkracht normaal N, zwaar N")
    for row in module_table():
        print(row)
