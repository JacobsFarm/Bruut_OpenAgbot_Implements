"""Trekkracht en neerdruk: werkt advanced V2 (V-schijfpaar + slepend dubbel mes) zwaarder of lichter dan advanced
(een schijf + naar voren hellend mes)? Puur Python.

    import lfa2_draft; lfa2_draft.report()          (of: python lfa2_draft.py)

Per element, opgeteld uit dezelfde onderdelen voor beide versies, met dezelfde bodemgetallen:
  1. snijden van de schijfrand            k_edge x snijdiepte, per schijf
  2. rolweerstand van de diepteringen     crr x kracht op de ringen (zweefstand, lfa_calc / lfa2_calc)
  3. grond opzij duwen met de V-schijven  sigma_disc x doorsnede van de open V (2D-breuk, zoals een ploeg)
  4. mes in de voorgesneden sleuf          sigma_knife x doorsnede die het mes nog moet verdringen x hellingsfactor
                                          (smal mes: 3D-breuk, veel hogere specifieke weerstand dan bij 3.)
  5. rolweerstand aandrukwiel             crr x aandrukkracht
Neerdruk: de schijven moeten de zode in (k_pen per mm diepte per schijf), het mes duwt omhoog (slepend) of trekt
omlaag (naar voren hellend): verticaal = zuigfactor x mestrekkracht.

ALLE BODEMGETALLEN ZIJN SCHATTINGEN (niet gemeten). Ze zijn zo gekozen dat ze aansluiten op wat elders in de map al
is aangenomen (simple_v2 LOADS: schijf 30/50 N bij 40 mm, mes 60/125 N, schijf 100/200 N neerdruk) en op ASABE D497
(ploeg ca. 5 N/cm2 in middelzware grond). De vergelijking (verhouding V2 / advanced) is betrouwbaarder dan de
absolute getallen: dezelfde aannames gelden voor beide. Meten in de veldproef met een trekunster.
"""
import importlib.util
import math
import os
import sys

import lfa2_params as P
import lfa2_calc as C

ADV_FOLDER = os.path.join(os.path.dirname(P.FOLDER), "advanced")

# bodem per element, "normaal" (grasland, vochtig, middelzwaar) en "zwaar" (droge klei, dichte zode)
SOIL = {
    "normaal": {"k_edge": 0.75,        # N per mm snijdiepte per schijfrand (simple_v2: 30 N bij 40 mm)
                "k_pen": 2.5,          # N neerdruk per mm diepte per schijf (simple_v2: 100 N bij 40 mm)
                "sigma_disc": 0.05,    # N/mm2 grond opzij duwen met een rollende schuine schijf (ASABE ploeg, F 0,7)
                "sigma_knife": 0.34},  # N/mm2 smal mes in een voorgesneden sleuf (simple_v2: 60 N op 175 mm2)
    "zwaar": {"k_edge": 1.25, "k_pen": 5.0, "sigma_disc": 0.10, "sigma_knife": 0.71},
}
CRR = 0.08                  # rolweerstand dieptering en aandrukwiel in gras
# hellingsfactor mes t.o.v. verticaal (Godwin & Spoor: de trekkracht stijgt met de hellingshoek; een naar voren hellend
# mes trekt zich de grond in, een slepend mes wordt omhoog geduwd). Schatting.
RAKE = {"forward_15": 0.85, "vertical": 1.0, "trailing_20": 1.3}
SUCTION = {"forward_15": -0.3, "trailing_20": 0.35}     # verticale kracht / trekkracht mes (- = trekt omlaag)
SPEED = 0.75                # m/s


def _load_advanced():
    """lfa_params en lfa_calc van ../advanced als eigen modules (namen verschillen van lfa2_*)."""
    mods = {}
    for name in ("lfa_params", "lfa_calc"):
        if name in sys.modules and os.path.dirname(os.path.abspath(sys.modules[name].__file__)) == ADV_FOLDER:
            mods[name] = sys.modules[name]
            continue
        spec = importlib.util.spec_from_file_location(name, os.path.join(ADV_FOLDER, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        mods[name] = mod
    return mods["lfa_params"], mods["lfa_calc"]


# ---------------------------------------------------------------------
# Geometrie
# ---------------------------------------------------------------------
def v_section(step=1.0):
    """Doorsnede van de open V die het schijfpaar maakt (mm2): per diepte de grootste afstand tussen de binnenkanten
    van de schijven zolang de schijf op die diepte nog in de grond zit, min de snede die er al was (meet_gap).
    Geeft (oppervlak, breedte bovenaan, breedte op halve diepte)."""
    depth = P.work_depth
    area, widths = 0.0, []
    z = -step / 2.0
    while z > -depth:
        best = 0.0
        y = P.disc_y - P.disc_d / 2.0
        while y < P.disc_y + P.disc_d / 2.0:
            x, inside = P.disc_inner_x(y, z)
            if inside:
                best = max(best, 2.0 * x)
            y += 2.0
        w = max(0.0, best - P.disc_meet_gap)
        widths.append(w)
        area += w * step
        z -= step
    return area, widths[0], widths[len(widths) // 2]


def knife_v2_section():
    """Doorsnede die het dubbele mes nog moet verdringen: alleen onder de schijven (in de open V is het vrij,
    knife_gap 6 mm aan beide kanten). Mes + buisjes 10 breed, van de schijfdiepte tot de punt."""
    tip = -P.knife_tip()[1]
    return P.K.blade_t * max(0.0, tip - P.work_depth), tip


def knife_adv_section(AP):
    """Advanced: mes 8 dik in de snede van de schijf (3 dik) tot zijn punt (35 diep)."""
    tip = -(AP.disc_z + AP.knife_tip_rel[1])
    return (AP.knife_t - AP.disc_t) * tip, tip


# ---------------------------------------------------------------------
# Krachten per element
# ---------------------------------------------------------------------
def element_v2(case="normaal"):
    s = SOIL[case]
    a = C.float_equilibrium()[0]
    f = C.unit_forces(drop=a)
    av, w_top, w_mid = v_section()
    ak, tip = knife_v2_section()
    out = {
        "disc_cut": 2 * s["k_edge"] * P.work_depth,
        "band_roll": CRR * f["disc"],
        "v_opening": s["sigma_disc"] * av,
        "knife": s["sigma_knife"] * ak * RAKE["trailing_20"],
        "press_roll": CRR * f["press"],
    }
    out["total"] = sum(out.values())
    out["penetration_needed"] = 2 * s["k_pen"] * P.work_depth
    out["knife_vertical"] = SUCTION["trailing_20"] * out["knife"]
    out["down_available"] = f["disc"]
    out["geometry"] = {"discs": 2, "depth": round(P.work_depth, 1), "V_mm2": round(av), "V_width_top": round(w_top, 1),
                       "V_width_mid": round(w_mid, 1), "knife_mm2": round(ak), "knife_tip": round(tip, 1)}
    return out


def element_adv(case="normaal"):
    AP, AC = _load_advanced()
    s = SOIL[case]
    a = AC.float_equilibrium()[0]
    f = AC.unit_forces(drop=a)
    ak, tip = knife_adv_section(AP)
    out = {
        "disc_cut": s["k_edge"] * AP.work_depth,
        "band_roll": CRR * f["disc"],
        "v_opening": 0.0,
        "knife": s["sigma_knife"] * ak * RAKE["forward_15"],
        "press_roll": CRR * f["press"],
    }
    out["total"] = sum(out.values())
    out["penetration_needed"] = s["k_pen"] * AP.work_depth
    out["knife_vertical"] = SUCTION["forward_15"] * out["knife"]
    out["down_available"] = f["disc"]
    out["geometry"] = {"discs": 1, "depth": AP.work_depth, "V_mm2": 0, "knife_mm2": round(ak), "knife_tip": tip}
    return out


def compare(case="normaal"):
    """Per element en voor de hele machine (5 rijen): trekkracht, vermogen bij SPEED, neerdruk."""
    rows = len(P.row_x)
    adv, v2 = element_adv(case), element_v2(case)
    res = {}
    for name, e in (("advanced", adv), ("V2", v2)):
        need = e["penetration_needed"] + e["knife_vertical"]
        res[name] = {
            "per_element_N": {k: round(e[k], 1) for k in ("disc_cut", "band_roll", "v_opening", "knife", "press_roll",
                                                          "total")},
            "machine_draft_N": round(rows * e["total"]),
            "machine_draft_kgf": round(rows * e["total"] / 9.81, 1),
            "power_W": round(rows * e["total"] * SPEED),
            "down_needed_per_element_N": round(need),
            "down_on_discs_float_N": round(e["down_available"]),
            "reaches_depth": e["down_available"] >= need,
            "geometry": e["geometry"],
        }
    res["ratio_draft_V2_over_advanced"] = round(v2["total"] / adv["total"], 2)
    res["extra_draft_N"] = round(rows * (v2["total"] - adv["total"]))
    return res


# robot: 4 hubmotoren 8" (simple_v2/lfs2_layout.ROBOT, geschat): 55 Nm continu op 0,20 m belaste straal; grip
# droog 0,6, nat 0,35; rolweerstand robot 0,08; werk continu met 70 % van wat over is
TRACTION = {"torque_cont_nm": 55.0, "r_load": 0.20, "wheels": 4, "mu_dry": 0.6, "mu_wet": 0.35, "crr": 0.08,
            "usable": 0.7}


def robot_traction(soil_force_n, tank_full=True):
    """Netto trekkracht van de robot (N): het kleinste van grip en motorkracht, min de eigen rolweerstand.
    soil_force_n = wat de grond van het werktuig draagt (in zweefstand het bewegende deel): dat drukt niet op de robot.
    Gewicht op de wielen: robot + tank (lfa2_calc.ROBOT) + vast deel werktuig + pompset (met volle jerrycans 50 kg)."""
    r = C.ROBOT
    kit = C.MODEL["pump_kit_kg"] + (50.0 if tank_full else 0.0)
    tank = r["tank_l"] * r["liquid_density"] if tank_full else 0.0
    wheels_n = (r["robot_kg"] + tank + C.MODEL["implement_kg"] + kit) * C.G_ACC - soil_force_n
    motor = TRACTION["wheels"] * TRACTION["torque_cont_nm"] / TRACTION["r_load"]
    out = {}
    for name, mu in (("droog", TRACTION["mu_dry"]), ("nat", TRACTION["mu_wet"])):
        net = min(mu * wheels_n, motor) - TRACTION["crr"] * wheels_n
        out[name] = round(TRACTION["usable"] * net)
    out["wheel_load_N"] = round(wheels_n)
    return out


def report():
    soil = C.MODEL["moving_kg"] * C.G_ACC
    trac = robot_traction(soil)
    for case in SOIL:
        r = compare(case)
        print("== %s ==" % case)
        for name in ("advanced", "V2"):
            print(name, r[name])
        print("V2 / advanced trekkracht: %.2f  (+%d N voor 5 rijen)" % (r["ratio_draft_V2_over_advanced"],
                                                                          r["extra_draft_N"]))
    print("robot, bruikbare trekkracht (70 % van netto, N):", trac)
    return {case: compare(case) for case in SOIL}, trac


if __name__ == "__main__":
    report()
