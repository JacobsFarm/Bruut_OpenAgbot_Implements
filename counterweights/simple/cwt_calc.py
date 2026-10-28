"""Calculations for the counterweights, in pure Python (same parameters as the model).

    import cwt_calc
    cwt_calc.report()          # prints and returns all key figures

Masses come from build_cwt.mass_properties() (copied into cwt_params.MODEL_MASS after a rebuild).
"""
import cwt_params as P


def stack_y(end):
    y0, y1 = P.end_span(P.stack_y, end)
    return (y0 + y1) / 2.0


def axle_loads(items):
    total = sum(k for k, _ in items)
    front = sum(k * (y + P.robot_axle_y) for k, y in items) / (2 * P.robot_axle_y)
    return {"total_kg": round(total, 1), "front_kg": round(front, 1), "rear_kg": round(total - front, 1),
            "front_share": round(front / total, 3)}


def ballast_items(front, rear):
    """(kg, y) of the ballast: plates per stack at each end (2 stacks per end), base plates where plates are."""
    m = P.MODEL_MASS
    out = []
    for end, n in (("front", front), ("rear", rear)):
        if n:
            out.append((2 * (n * m["plate_kg"] + m["base_kg"]), stack_y(end)))
    return out


def plates_needed(name):
    """Fewest plates per stack (front for a rear implement, rear for a front one) that bring the axle shares within
    the limits; None when 4 per stack are not enough."""
    base = [(P.robot_mass, P.robot_cg_y)] + P.IMPLEMENTS[name]
    bare = axle_loads(base)
    out = {"bare": bare}
    rear_heavy = bare["front_share"] < 0.5
    for n in range(0, P.plates_max + 1):
        items = base + (ballast_items(n, 0) if rear_heavy else ballast_items(0, n))
        a = axle_loads(items)
        ok = a["front_share"] >= P.front_share_min and 1.0 - a["front_share"] >= P.rear_share_min
        if ok:
            out.update({"end": "front" if rear_heavy else "rear", "plates_per_stack": n,
                        "ballast_kg": round(sum(k for k, _ in items[len(base):]), 1), "with": a})
            return out
    out.update({"end": "front" if rear_heavy else "rear", "plates_per_stack": None})
    return out


def report():
    m = P.MODEL_MASS
    out = {"plate_kg": m["plate_kg"], "single_person_ok": m["plate_kg"] <= P.lift_limit_kg,
           "max_per_end_kg": round(2 * (P.plates_max * m["plate_kg"] + m["base_kg"]), 1),
           "stack_top_z_4_plates": P.robot_lower_beam_z[1] + P.base_t + P.plates_max * P.plate[2] + P.clamp[1]
           + P.knob_h}
    for name in P.IMPLEMENTS:
        out[name] = plates_needed(name)
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
