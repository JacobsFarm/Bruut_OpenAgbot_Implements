import hyb_params as P


def energy():
    """Battery energy (Wh), usable energy (Wh)."""
    total = P.batt_voltage * P.batt_ah
    return total, total * P.batt_usable


def generator_electrical_w():
    """Electrical power the train delivers continuously (limited by the generator and by the engine)."""
    return min(P.gen_power, P.eng_power * P.gen_eff)


def balance(load_w):
    """Net battery power (W) at a given robot load: + charging, - discharging."""
    return generator_electrical_w() - load_w


def runtime_min(load_w):
    """Minutes the usable battery lasts at this load with the engine running; None = never empties."""
    net = balance(load_w)
    if net >= 0:
        return None
    return energy()[1] / -net * 60.0


def fuel_lph():
    """Fuel use (L/h) at full generator output."""
    shaft_kw = generator_electrical_w() / P.gen_eff / 1000.0
    return shaft_kw * P.eng_sfc


def mass_total():
    return P.eng_mass + P.gen_mass + P.batt_mass + P.ctl_mass


def report():
    total, usable = energy()
    peak = P.n_hubmotors * P.hub_power * P.hub_peak_factor
    print("battery %.0f V %.0f Ah = %.0f Wh (usable %.0f Wh)" % (P.batt_voltage, P.batt_ah, total, usable))
    print("generator electrical %.0f W, fuel %.2f L/h" % (generator_electrical_w(), fuel_lph()))
    for name, load in (("light task", P.light_task_w), ("heavy task", P.heavy_task_w), ("peak (2x)", peak)):
        net = balance(load)
        rt = runtime_min(load)
        print("%-10s load %5.0f W -> battery %+6.0f W%s" % (
            name, load, net, "" if rt is None else ", empty in %.0f min" % rt))
    print("components mass %.0f kg (without frame)" % mass_total())
