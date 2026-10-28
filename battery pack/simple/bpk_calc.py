"""Calculations for the battery pack, in pure Python (same parameters as the model).

    import bpk_calc
    bpk_calc.report()          # prints and returns all key figures

Masses come from build_bpk.mass_properties() (copied into bpk_params.MODEL_MASS after a rebuild).
"""
import bpk_params as P


def pod():
    """Voltage, capacity and energy of one pod (16S1P)."""
    v = P.cells_n * P.cell_v
    wh = v * P.cell_ah
    return {"nominal_V": v, "Ah": P.cell_ah, "Wh": round(wh), "usable_Wh": round(wh * P.dod),
            "kg": P.MODEL_MASS["pod_kg"], "Wh_per_kg": round(wh / P.MODEL_MASS["pod_kg"])}


def runtime():
    """Working hours per implement: robot battery alone and with the 2 pods."""
    usable = 2 * pod()["usable_Wh"]
    out = {}
    for name, w in P.LOADS_W.items():
        load = w + P.base_load_w
        out[name] = {"W": round(load), "robot_only_h": round(P.robot_battery_wh / load, 1),
                     "with_pods_h": round((P.robot_battery_wh + usable) / load, 1)}
    return out


def traction():
    """Extra pull (N) the pods give through their weight (grip 0.45, they sit centred between the axles)."""
    m = 2 * P.MODEL_MASS["pod_kg"] + P.MODEL_MASS["hangers_kg"]
    return {"added_kg": round(m, 1), "extra_grip_N": round(0.45 * m * P.g),
            "extra_rolling_N_grass": round(0.06 * m * P.g)}


def charge():
    p = pod()
    return {"charger_W": P.charger_w, "hours_per_pod": round(p["Wh"] / P.charger_w / 0.9, 1),
            "swap_minutes": 5}


def report():
    out = {"pod": pod(), "total_usable_Wh": 2 * pod()["usable_Wh"] + P.robot_battery_wh, "runtime": runtime(),
           "traction": traction(), "charge": charge()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
