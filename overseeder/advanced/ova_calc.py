"""Berekeningen voor de onderbouwing van de geavanceerde doorzaaimachine (puur Python).

Gebruik:  import ova_calc; ova_calc.report()        (of: python ova_calc.py)
Massa's komen uit het FreeCAD-model (build_ova.mass_properties) en staan in MODEL. Aannames (bodemkrachten, robot,
zaad) zijn geschat, niet gemeten; de bodemkrachten zijn gelijk aan de eenvoudige versie, behalve de zaaikouter.
"""
import math

import ova_params as P
import ova_kin as K

G_ACC = 9.81

# laatste meting uit het model (werkstand, lege bak)
MODEL = {
    "implement_kg": 159.9,
    "implement_cg": (-411.0, 453.0),
    "moving_kg": 98.8,          # balk, achterframe, 8 elementen (zonder slangen)
    "moving_cg": (-660.0, 231.0),
    "seeder_kg": 32.4,          # luchtzaaier op de robot (frame, bak, dosering, ventilator, kastje)
    "seeder_cg": (94.0, 1023.0),
    "hoses_kg": 2.8,            # half op de balk, half op de robot gerekend
    "arm_kg": 7.99,             # een sleeparm met schijf, ringen, kouter, gaffel en aandrukrol
    "arm_cg": (-784.0, 137.0),
}
SEED = {"kg": 25.0, "cg": (120.0, 1200.0)}      # zaad in de bak op de robot (grasvak vol: 62 l x 0,35 = 22 kg)

# bodemkrachten per element bij 15 mm (schatting; zie ../simple/ovs_calc.py). De zaaikouter staat in het vlak van
# de schijf en zet de sleuf open tot 16 mm: iets meer trekkracht dan de schoen in de schaduw van de scheve schijf.
LOADS = {
    "normaal": {"disc_vertical": 90.0, "disc_draft": 25.0, "boot_draft": 15.0, "band_min": 20.0},
    "zwaar": {"disc_vertical": 180.0, "disc_draft": 45.0, "boot_draft": 25.0, "band_min": 20.0},
}
SOIL = {"rolling": 0.10}
DISC_FORCE_DY = 30.0

ROBOT = {
    "robot_kg": 150.0,
    "robot_cg_from_rear": 500.0,
    "wheelbase": 1000.0,
    "traction_mu": 0.5,
    "front_ballast_kg": 0.0,
}
ACTUATOR = {"force_n": 2500.0, "speed_mm_s": 30.0}       # 24 V, slag 150 (toediener: >= 40 mm/s bij 1200 N)

SEEDS = (
    ("Engels raaigras (tetraploid)", 0.35, (15.0, 25.0, 40.0), "main"),
    ("Engels raaigras (diploid)", 0.40, (15.0, 25.0, 40.0), "main"),
    ("witte klaver", 0.78, (3.0, 5.0, 6.0), "fine"),
    ("rode klaver", 0.78, (10.0, 12.0, 13.0), "fine"),
    ("cichorei / smalle weegbree", 0.50, (2.0, 4.0, 6.0), "fine"),
)
FAN = {"power_w": 150.0, "air_m_s": 20.0}               # 12 V radiaalventilator (typisch), luchtsnelheid in de slang


# ---------------------------------------------------------------------
# Dosering (zelfde rollen als de eenvoudige versie)
# ---------------------------------------------------------------------
def roll_rpm(dose_kg_ha, density_kg_l, roll="main", speed=P.work_speed):
    g_per_s_row = dose_kg_ha * 0.1 * (P.row_spacing / 1000.0) * speed
    cc_rev = P.roll_main_cc if roll == "main" else P.roll_fine_cc
    return g_per_s_row / density_kg_l / cc_rev * 60.0


def dose_table(speed=P.work_speed):
    return [(name, roll, tuple((d, round(roll_rpm(d, rho, roll, speed), 1)) for d in doses))
            for name, rho, doses, roll in SEEDS]


def hopper_area_ha(dose_main=40.0, rho_main=0.35, dose_fine=5.0, rho_fine=0.78):
    v_main, v_fine = K.hopper_volumes_l()
    return v_main * rho_main / dose_main, v_fine * rho_fine / dose_fine


# ---------------------------------------------------------------------
# Element (arm om zijn draaipunt) en balk (zwevend aan het parallellogram)
# ---------------------------------------------------------------------
def unit_points():
    c = K.disc_center()
    return {"disc_v": (c[0] + DISC_FORCE_DY, -P.work_depth), "disc_h": (c[0] + DISC_FORCE_DY, -P.work_depth / 2.0),
            "boot": (K.boot_tip()[0] - 20.0, -P.work_depth / 2.0), "band": (c[0], 0.0),
            "pw": (K.pw_axle()[0], 0.0)}


def spring_lever():
    return K.spring_moment(0.0) / max(K.spring_force(0.0), 1e-9)


def unit_band(spring_n, case="normaal", pw=None):
    """Kracht op de diepteringen samen (N) bij veerkracht spring_n (armbalans)."""
    ld = LOADS[case]
    pw = P.pw_force if pw is None else pw
    pv = P.u_pivot
    pt = unit_points()
    m_w = MODEL["arm_kg"] * G_ACC * (pv[0] - MODEL["arm_cg"][0])
    m_soil = (ld["disc_vertical"] * (pv[0] - pt["disc_v"][0]) + ld["disc_draft"] * (pv[1] - pt["disc_h"][1])
              + ld["boot_draft"] * (pv[1] - pt["boot"][1]) + pw * (pv[0] - pt["pw"][0] + SOIL["rolling"] * pv[1]))
    lever = pv[0] - pt["band"][0] + SOIL["rolling"] * pv[1]
    return (spring_n * spring_lever() + m_w - m_soil) / lever


def spring_for_band(band, case="normaal"):
    lo, hi = -3000.0, 6000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if unit_band(mid, case) < band:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def bar_balance(case="normaal", rows=None, gas_n=None, ballast_kg=0.0):
    """Balk zwevend: de grond draagt het hele bewegende gewicht plus de neerwaartse kracht van de gasveren (het
    parallellogram neemt geen verticale kracht op). Wat na schijf en aandrukrol overblijft, dragen de ringen."""
    ld = LOADS[case]
    n = len(P.row_x) if rows is None else rows
    m_rows = (len(P.row_x) - n) * (MODEL["arm_kg"] + 3.0)
    w = (MODEL["moving_kg"] - m_rows + MODEL["hoses_kg"] / 2.0 + ballast_kg) * G_ACC
    gas_v = K.gas_vertical(0.0) if gas_n is None else gas_n * K.act_ratio(0.0)
    band = (w + gas_v) / n - ld["disc_vertical"] - P.pw_force
    draft = n * (ld["disc_draft"] + ld["boot_draft"] + SOIL["rolling"] * (max(band, 0.0) + P.pw_force))
    return {"rows": n, "weight_N": round(w), "gas_vertical_N": round(gas_v), "band_each_N": round(band, 1),
            "band_ok": band >= ld["band_min"] - 1e-6, "unit_down_each_N": round((w + gas_v) / n, 1),
            "spring_for_float_N": round(spring_for_band(band, case)), "draft_N": round(draft)}


def gas_for(case="normaal", rows=None):
    """Gasveerkracht (beide samen, N) voor band_min op de ringen."""
    lo, hi = -2000.0, 8000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if bar_balance(case, rows, mid)["band_each_N"] < LOADS[case]["band_min"]:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------
# Robot: asbelasting (momenten om het contactpunt van de achterwielen), grip, heffen
# ---------------------------------------------------------------------
def fixed_mass_cg():
    """Massa en zwaartepunt-y van wat vast aan de robot zit, zonder luchtzaaier en zaad (bok, stangen, actuator)."""
    m_fix = MODEL["implement_kg"] - MODEL["moving_kg"] - MODEL["seeder_kg"] - MODEL["hoses_kg"]
    s = (MODEL["implement_kg"] * MODEL["implement_cg"][0] - MODEL["moving_kg"] * MODEL["moving_cg"][0]
         - MODEL["seeder_kg"] * MODEL["seeder_cg"][0] - MODEL["hoses_kg"] * -400.0)
    return m_fix, s / m_fix


def axle_loads(working=True, seed_kg=None, ballast_front=0.0, case="normaal", rows=None, gas_n=None):
    r = dict(ROBOT)
    seed_kg = SEED["kg"] if seed_kg is None else seed_kg
    ax = P.robot_wheel_y
    L = r["wheelbase"] / 1000.0
    m_fix, y_fix = fixed_mass_cg()
    weights = [(r["robot_kg"], ax + r["robot_cg_from_rear"]), (ballast_front, ax + r["wheelbase"]),
               (m_fix, y_fix), (MODEL["seeder_kg"], MODEL["seeder_cg"][0]), (seed_kg, SEED["cg"][0]),
               (MODEL["hoses_kg"], -400.0)]
    n = len(P.row_x) if rows is None else rows
    m_rows = (len(P.row_x) - n) * (MODEL["arm_kg"] + 3.0)
    m_mov = MODEL["moving_kg"] - m_rows
    ground = []
    if working:
        weights.append((m_mov, MODEL["moving_cg"][0]))
        bb = bar_balance(case, rows, gas_n)
        ld = LOADS[case]
        pt = unit_points()
        band = max(bb["band_each_N"], 0.0)
        ground = [(n * ld["disc_vertical"], pt["disc_v"][0]), (n * band, pt["band"][0]), (n * P.pw_force, pt["pw"][0])]
    else:
        dy, _ = K.bar_shift(P.lift_height)
        weights.append((m_mov, MODEL["moving_cg"][0] + dy))
    w_tot = sum(m for m, _ in weights) * G_ACC
    m_rear = sum(m * G_ACC * (y - ax) for m, y in weights) - sum(f * (y - ax) for f, y in ground)
    n_front = m_rear / L / 1000.0
    n_rear = w_tot - sum(f for f, _ in ground) - n_front
    return n_front, n_rear


def front_ballast_for(min_share=0.25, seed_kg=None):
    lo, hi = 0.0, 300.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        nf, nr = axle_loads(False, seed_kg, mid)
        if nf < min_share * (ROBOT["robot_kg"] + mid) * G_ACC:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def traction(case="normaal", rows=None, gas_n=None, ballast_front=0.0):
    bb = bar_balance(case, rows, gas_n)
    nf, nr = axle_loads(True, None, ballast_front, case, rows, gas_n)
    return bb["draft_N"], ROBOT["traction_mu"] * (nf + nr)


def lift_force(safety=1.3):
    """Actuatorkracht (N) om de balk te heffen, begin (h = 0) en eind (h = lift_height)."""
    w = (MODEL["moving_kg"] + MODEL["hoses_kg"] / 2.0) * G_ACC
    return tuple(w * safety / K.act_ratio(h) for h in (0.0, P.lift_height))


def lift_times():
    v = ACTUATOR["speed_mm_s"]
    free = K.slot_pos(0.0)
    lift = K.ab_length(0.0) - K.ab_length(P.lift_height)
    return free, lift, ((free) / v, (free + lift) / v)


def gas_table(case="normaal", rows=None):
    out = []
    for f in (0, 300, 480, 700, 1000, 1400):
        bb = bar_balance(case, rows, float(f))
        nf, nr = axle_loads(True, None, 0.0, case, rows, float(f))
        out.append((f, bb["band_each_N"], round(nf), round(nr), bb["draft_N"], round(ROBOT["traction_mu"] * (nf + nr))))
    return out


def module_table():
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


COST = (
    ("staal: bok, stangen, balk, achterframe, vorkplaten (laser), draagframe (ca. 60 kg)", 260),
    ("8 kouterschijven O 300 x 3 met naaf en as", 300),
    ("16 diepteringen PE O 270 (+ wisselsets 280 en 260)", 180),
    ("8 zaaikouters slijtvast staal, gelast, met RVS-buis 16 x 1,5", 160),
    ("8 aandrukrollen O 200 x 40, gaffels, torsieveren, schouderbouten", 170),
    ("8 drukveren 35 x 5, veerstangen, pennen", 90),
    ("bouten, pennen en bussen (parallellogram, klemmen)", 110),
    ("lineaire actuator 24 V, 2500 N, slag 150, ca. 30 mm/s, IP66", 280),
    ("2 gasveren 250 N, slag 100", 50),
    ("zaadbak aluminium 2 mm met deksel", 170),
    ("doseerhuis, 2 nokkenrollen, 2 wormwielmotoren met encoder", 200),
    ("12 V radiaalventilator ca. 150 W, luchtkanaal PVC, 8 venturi's", 160),
    ("zaadslang 20/26 (14 m)", 60),
    ("motor- en ventilatorregelaars, microcontroller, kastje, kabel", 90),
)


def cost_total():
    return sum(c for _, c in COST)


def report(model=None):
    if model:
        MODEL.update(model)
    out = {}
    out["work_width_m"] = P.work_width / 1000.0
    out["rows"] = len(P.row_x)
    out["disc_depth_mm"] = P.work_depth
    out["seed_depth_mm"] = P.work_depth - P.boot_lift
    out["hopper_l"] = tuple(round(v, 1) for v in K.hopper_volumes_l())
    out["hopper_ha_40kg_grass_5kg_clover"] = tuple(round(v, 2) for v in hopper_area_ha())
    out["float_range_mm"] = tuple(round(v, 1) for v in K.float_range())
    out["gas_force_work_N"] = round(K.gas_force(0.0))
    out["spring_force_work_N"] = round(K.spring_force(0.0))
    out["band_at_model_spring_N"] = round(unit_band(K.spring_force(0.0)), 1)
    out["bar_normal"] = bar_balance("normaal")
    out["bar_normal_no_gas"] = bar_balance("normaal", None, 0.0)
    out["gas_needed_normal_N"] = round(gas_for("normaal"))
    out["gas_needed_heavy_N"] = round(gas_for("zwaar"))
    gh4 = gas_for("zwaar", 4)
    out["gas_needed_heavy_4rows_N"] = round(gh4)
    out["bar_heavy_4rows"] = bar_balance("zwaar", 4, gh4)
    out["lift_force_N"] = tuple(round(f) for f in lift_force())
    free, lift, times = lift_times()
    out["act_free_mm_lift_mm"] = (round(free), round(lift))
    out["lift_time_s"] = tuple(round(t, 1) for t in times)
    out["lift_clearance_disc_boot_pw_mm"] = (round(K.summary()["disc_lifted_clearance"]),
                                             round(K.summary()["boot_lifted_z"]),
                                             round(K.summary()["pw_lifted_clearance"]))
    for name, kw in (("work", dict(working=True)), ("lifted_full", dict(working=False)),
                     ("lifted_empty", dict(working=False, seed_kg=0.0)),
                     ("lifted_full_ballast40", dict(working=False, ballast_front=40.0))):
        nf, nr = axle_loads(**kw)
        out["axle_" + name + "_N"] = (round(nf), round(nr))
    out["front_ballast_kg_for_25pct"] = round(front_ballast_for(0.25), 1)
    d, g = traction()
    out["draft_grip_normal_N"] = (d, round(g))
    gh = gas_for("zwaar")
    d, g = traction("zwaar", gas_n=gh)
    out["draft_grip_heavy_8rows_N"] = (d, round(g))
    d, g = traction("zwaar", 4, gh4)
    out["draft_grip_heavy_4rows_N"] = (d, round(g))
    out["fan_power_w"] = FAN["power_w"]
    out["cost_eur"] = cost_total()
    return out


if __name__ == "__main__":
    for k, v in report().items():
        print(k, v)
    print("dosering: zaad, rol, (kg/ha, omw/min) bij %.2f m/s" % P.work_speed)
    for row in dose_table():
        print(row)
    for case, rows in (("normaal", None), ("zwaar", None), ("zwaar", 4)):
        print("gasveren %s, %s rijen: gasveer N, ringen N, vooras N, achteras N, trek N, grip N" % (case, rows or 8))
        for row in gas_table(case, rows):
            print(row)
    print("breedte m, rijen/m, rijafstand mm, trekkracht normaal N, zwaar N")
    for row in module_table():
        print(row)
