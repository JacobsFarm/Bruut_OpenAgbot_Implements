"""Calculations for the speech speaker, in pure Python (same parameters as the model).

    import spk_calc
    spk_calc.report()          # prints and returns all key figures

Sound pressure of a horn in free field: SPL(r) = sensitivity + 10 log10(P) - 20 log10(r).
"""
import math

import spk_params as P


def spl(power_w, r_m):
    return P.sensitivity_db + 10.0 * math.log10(power_w) - 20.0 * math.log10(r_m)


def reach():
    """Distance (m) at which full power still gives speech speech_margin_db above each noise level."""
    out = {}
    for k, n in P.noise_db.items():
        need = n + P.speech_margin_db
        r = 10.0 ** ((P.sensitivity_db + 10.0 * math.log10(P.amp_w) - need) / 20.0)
        out[k] = round(r)
    return out


def power_for(r_m, noise="farmyard"):
    """Power (W) to talk to a person at r_m in the given noise; the volume control follows the person."""
    need = P.noise_db[noise] + P.speech_margin_db
    return round(10.0 ** ((need - P.sensitivity_db + 20.0 * math.log10(r_m)) / 10.0), 3)


def caps():
    """Largest power near animals (cap at 5 m) and the distance to a house where the full power falls to the cap."""
    p_animal = 10.0 ** ((P.animal_cap_db - P.sensitivity_db + 20.0 * math.log10(5.0)) / 10.0)
    r_house = 10.0 ** ((P.sensitivity_db + 10.0 * math.log10(P.amp_w) - P.neighbour_cap_db) / 20.0)
    return {"max_W_near_animals": round(min(p_animal, P.amp_w), 2), "full_power_quiet_at_house_m": round(r_house)}


def energy():
    avg_w = 2.0 * P.amp_w * P.talk_share * 0.3 / P.amp_eff + 2.0       # speech crest: ~30 % of full power, 2 W idle
    return {"avg_W": round(avg_w, 1), "Wh_per_10h": round(avg_w * 10.0)}


def report():
    out = {"spl_1m_full_dB": round(spl(P.amp_w, 1.0)), "reach_m": reach(),
           "power_W_at": {"2m": power_for(2.0), "10m": power_for(10.0), "30m": power_for(30.0)},
           "caps": caps(), "energy": energy()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
