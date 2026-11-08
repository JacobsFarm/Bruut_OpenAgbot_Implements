"""Calculations for the lift mast, in pure Python (same parameters as the model).

    import tpl_calc
    tpl_calc.report()

Masses come from build_tpl.mass_properties() (copied into tpl_params.MODEL_MASS after a rebuild).
"""
import tpl_params as P
import tpa_params as Q


def actuator(machine_kg=None, machine_cg_y=None):
    """Pull in the LA36 (N): weight of carriage and machine plus the friction of the bushes. The load hangs behind
    the columns: its moment is taken by the 2 housing levels (300 apart) as a force couple N; friction mu x 2 N."""
    m = P.MODEL_MASS
    mk = m["machine_kg"] if machine_kg is None else machine_kg
    my = m["machine_cg"][0] if machine_cg_y is None else machine_cg_y
    w_c, w_m = m["carriage_kg"] * P.g, mk * P.g
    moment = w_c * (P.col_y - m["carriage_cg"][0]) + w_m * (P.col_y - my)      # N mm
    spacing = P.housing_dz[1] - P.housing_dz[0]
    n_bush = moment / spacing
    friction = P.mu_bush * 2.0 * n_bush
    f = w_c + w_m + friction
    d = Q.LA36_24V[P.act_variant]
    v = Q.act_speed(f, P.act_variant)
    L0, L1 = P.act_length(0.0), P.act_length(P.travel)
    return {"weight_N": round(w_c + w_m), "bush_normal_N": round(n_bush), "friction_N": round(friction),
            "pull_N": round(f), "load_ratio": round(f / d[0], 2), "speed_mm_s": round(v, 1),
            "lift_time_s": round(P.travel / v, 1), "current_A": round(Q.act_current(f, P.act_variant), 1),
            "length_low_high": (round(L0, 1), round(L1, 1)),
            "fits_stroke": P.act_retracted <= L1 and L0 + P.float_slot * 0 <= P.act_extended,
            "margins_mm": (round(L1 - P.act_retracted, 1), round(P.act_extended - L0, 1)),
            "lowering_time_s": round(P.travel / Q.act_speed(0.0, P.act_variant), 1),
            "capacity_machine_kg": round((d[0] - w_c * (1 + 2 * P.mu_bush * (P.col_y - m["carriage_cg"][0]) / spacing))
                                         / (P.g * (1 + 2 * P.mu_bush * (P.col_y - my) / spacing)))}


def lift_table():
    return {dz: {"act_len": round(P.act_length(dz), 1), "coupler_z": round(P.cp_base(dz)[1]),
                 "machine_lift": round(P.machine_dz(dz))} for dz in P.DZ_POSES}


def axle_loads(machine_kg=None, machine_cg_y=None, ballast=True, lifted=True):
    m = P.MODEL_MASS
    mk = m["machine_kg"] if machine_kg is None else machine_kg
    my = m["machine_cg"][0] if machine_cg_y is None else machine_cg_y
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["act_kg"], P.act_y),
             (m["carriage_kg"], m["carriage_cg"][0])]
    if lifted:
        items.append((mk, my))
    if ballast:
        items.append((P.ballast_kg if ballast is True else float(ballast), P.ballast_cg_y))
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "front_share": round(front / total, 3)}


def capacity():
    """Heaviest machine the robot can carry lifted with front_share_min on the front axle; cg imp_cg_behind behind
    the coupler origin, and at the cg of the demo machine."""
    out = {}
    for label, y in (("cg_150_behind", P.cp_base_low[0] - P.imp_cg_behind),
                     ("cg_demo_machine", P.MODEL_MASS["machine_cg"][0])):
        for ballast in (False, True):
            lo, hi = 0.0, 400.0
            for _ in range(40):
                mid = (lo + hi) / 2.0
                if axle_loads(mid, y, ballast)["front_share"] >= P.front_share_min:
                    lo = mid
                else:
                    hi = mid
            out["%s_%s" % (label, "with_ballast" if ballast else "no_ballast")] = round(lo)
    return out


def ballast_needed(lifted=True):
    """Front counterweight (kg, at ballast_cg_y) for front_share_min with the demo machine lifted."""
    m = P.MODEL_MASS
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["act_kg"], P.act_y),
             (m["carriage_kg"], m["carriage_cg"][0])] + ([(m["machine_kg"], m["machine_cg"][0])] if lifted else [])
    lo, hi = 0.0, 300.0
    for _ in range(40):
        b = (lo + hi) / 2.0
        it = items + [(b, P.ballast_cg_y)]
        total = sum(k for k, _ in it)
        front = sum(k * (y + P.robot_axle_y) for k, y in it) / (2 * P.robot_axle_y)
        if front / total >= P.front_share_min:
            hi = b
        else:
            lo = b
    return round(hi, 1)


def report():
    out = {"lift": lift_table(), "actuator": actuator(), "actuator_empty": actuator(machine_kg=0.0),
           "capacity_kg": capacity(), "axle_lifted": axle_loads(), "axle_lifted_no_ballast": axle_loads(ballast=False),
           "axle_empty_no_ballast": axle_loads(ballast=False, lifted=False),
           "ballast_needed_kg": ballast_needed(), "axle_lifted_6_plates": axle_loads(ballast=66.0), "legs_off_ground_mm": round(P.machine_dz(P.travel)), "act_mass_kg": round(P.act_mass(), 2)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
