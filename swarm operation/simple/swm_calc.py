"""Calculations for swarm operation, in pure Python (same parameters as the model).

    import swm_calc
    swm_calc.report()          # prints and returns all key figures

The field is worked in passes of pass_w along its length; n units take passes in turn (units on neighbouring passes
are a pass apart). Each turn at the headland costs turn_s, plus corridor_wait_s per extra unit that shares the
headland corridor at the same time. Charging is shared: with fewer chargers than units, units queue.
"""
import math

import swm_params as P


def field_time(n):
    """Hours to do the field with n units (working time only, no charging) and the speed-up against 1 unit."""
    L, W = P.field
    passes = math.ceil(W / P.pass_w)
    per_pass = L / P.speed + P.turn_s + P.corridor_wait_s * (n - 1)
    hours = math.ceil(passes / n) * per_pass / 3600.0
    return hours


def scaling():
    t1 = field_time(1)
    out = {}
    for n in P.units:
        t = field_time(n)
        out[n] = {"hours": round(t, 1), "speed_up": round(t1 / t, 2), "efficiency": round(t1 / t / n, 2)}
    return out


def charging(n):
    """Share of the time a unit works when n units share the chargers (each works battery_h, charges charge_h)."""
    cycle = P.battery_h + P.charge_h
    demand = n * P.charge_h / cycle                 # chargers needed on average
    if demand <= P.chargers:
        return round(P.battery_h / cycle, 2)
    return round(P.battery_h / cycle * P.chargers / demand, 2)


def radio(n):
    load = n * P.msg_bytes * 8 * P.msg_hz / 1000.0
    return {"kbps": round(load, 1), "share_of_link": round(load / P.radio_kbps, 2)}


def compaction():
    """Ground pressure (kPa) of a unit against a tractor doing the same job."""
    unit = P.unit_mass * 9.81 / (4 * P.tyre_contact_m2) / 1000.0
    tr = P.tractor["mass"] * 9.81 / (P.tractor["wheels"] * P.tractor["contact_m2"]) / 1000.0
    return {"unit_kPa": round(unit), "tractor_kPa": round(tr)}


def report():
    out = {"scaling": scaling(), "work_share_with_1_charger": {n: charging(n) for n in P.units},
           "radio": {n: radio(n) for n in (4, 8)}, "compaction": compaction()}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
