"""Calculations for the magnet sweeper, in pure Python (same parameters as the model).

    import mgs_calc
    mgs_calc.report()          # prints and returns all key figures

Magnet model (2D, across the driving direction, valid away from the bar ends): every magnet row is a pair of charged
strips (pole face and back face) of +-Br; the steel back plate is taken as a mirror (back face backplate_factor x the
magnet thickness away). For a strip from y1 to y2 at depth dz:
    Bz = c [atan((y2-y)/dz) - atan((y1-y)/dz)],  By = c/2 ln(((y-y1)^2+dz^2) / ((y-y2)^2+dz^2)),  c = +-Br/(2 pi)
A loose steel part (soft iron, demagnetizing factor N) gets M = min(Ms, |B| / (mu0 N)) and a pull F = M V d|B|/dz.
It is picked up when F > pick_margin x weight.
Masses come from build_mgs.mass_properties() (copied into mgs_params.MODEL_MASS after a rebuild).
"""
import math

import mgs_params as P

FACE_OVER_SKIN = P.skin_t + P.core_gap         # magnet face above the underside of the skin, core down (mm)


def _rows():
    """(y centre relative to mag_y, sign) of the magnet rows, m."""
    w = P.mag_size[1] / 1000.0
    return [((r - (P.mag_rows - 1) / 2.0) * w, 1 if r % 2 == 0 else -1) for r in range(P.mag_rows)]


def b_field(z_mm, y_mm=0.0):
    """|B| (T) at z_mm below the magnet face and y_mm from the centre between the rows."""
    w = P.mag_size[1] / 1000.0
    L = P.mag_size[2] * P.backplate_factor / 1000.0
    z = max(z_mm, 0.1) / 1000.0
    y = y_mm / 1000.0
    by = bz = 0.0
    for yc, sign in _rows():
        y1, y2 = yc - w / 2.0, yc + w / 2.0
        for zf, sf in ((0.0, 1), (-L, -1)):
            dz = z - zf
            c = sign * sf * P.Br / (2.0 * math.pi)
            bz += c * (math.atan((y2 - y) / dz) - math.atan((y1 - y) / dz))
            by += c * 0.5 * math.log(((y - y1) ** 2 + dz * dz) / ((y - y2) ** 2 + dz * dz))
    return math.hypot(by, bz)


def gradient(z_mm, y_mm=0.0, h=0.5):
    """|d|B|/dz| (T/m)."""
    return abs(b_field(z_mm + h, y_mm) - b_field(z_mm - h, y_mm)) / (2.0 * h / 1000.0)


def pull(item, z_mm, y_mm=0.0):
    """Magnetic pull (N) on a part at z_mm below the magnet face."""
    it = P.ITEMS[item]
    vol = it["g"] / 1000.0 / (P.steel * 1e9)         # m3 (steel 7850 kg/m3)
    m = min(P.Ms_steel, b_field(z_mm, y_mm) / (P.mu0 * it["N"]))
    return m * vol * gradient(z_mm, y_mm)


Y_SAMPLES = (-100.0, -75.0, -50.0, -25.0, 0.0, 25.0, 50.0, 75.0, 100.0)   # mm across the 200 mm magnet face


def reach(item, margin=None):
    """Distance (mm) from the magnet face up to which the part is picked up (pull > margin x weight): the worst and
    the best place across the face (y samples)."""
    margin = P.pick_margin if margin is None else margin
    w = P.ITEMS[item]["g"] / 1000.0 * P.g * margin
    out = []
    for y in Y_SAMPLES:
        z = FACE_OVER_SKIN
        while z < 300.0 and pull(item, z + 1.0, y) > w:
            z += 1.0
        out.append(z)
    return min(out), max(out)


def pickup():
    """Per part: reach, distance to a part on a hard floor and on mown grass (in the thatch), and whether it falls off
    the skin when the core is lifted (pull at the skin < weight)."""
    floor = P.box_z[0] + FACE_OVER_SKIN                 # face over a hard floor (on the castors)
    grass = floor + P.grass_bury
    rel = FACE_OVER_SKIN + P.core_lift
    out = {}
    for k, it in P.ITEMS.items():
        r0, r1 = reach(k)
        wt = it["g"] / 1000.0 * P.g
        hold = min(pull(k, FACE_OVER_SKIN, y) for y in Y_SAMPLES) / wt
        drop = max(pull(k, rel, y) for y in Y_SAMPLES) / wt
        out[k] = {"reach_mm": (r0, r1), "floor": "all" if r0 >= floor else ("part" if r1 >= floor else "no"),
                  "grass": "all" if r0 >= grass else ("part" if r1 >= grass else "no"),
                  "hold_x_weight": round(hold, 1), "released_x_weight": round(drop, 2), "drops": drop < 1.0}
    return out


def field():
    """Field (mT) under the middle of a row at the distances that matter."""
    floor = P.box_z[0] + FACE_OVER_SKIN
    yr = P.mag_size[1] / 2.0
    pts = {"at_skin": FACE_OVER_SKIN, "floor": floor, "grass": floor + P.grass_bury,
           "released_at_skin": FACE_OVER_SKIN + P.core_lift}
    return {k: {"mm": round(z, 1), "mT": round(b_field(z, yr) * 1000.0), "grad_T_m": round(gradient(z, yr), 1)}
            for k, z in pts.items()}


def release_force(item="nail_3x70"):
    """Force (N) on the release actuator at the start of the lift: core weight, the pull on the parts that touch the
    skin on the 3 pole lines (contact_parts, pull averaged over the lines) and guide friction; lifting time."""
    core_N = P.MODEL_MASS["core_kg"] * P.g
    lines = [i * P.mag_size[1] for i in range(-P.mag_rows // 2, P.mag_rows // 2 + 1)]
    per_part = sum(pull(item, FACE_OVER_SKIN + 1.0, y) for y in lines) / len(lines)
    iron_N = P.contact_parts * per_part
    friction = 0.1 * iron_N
    need = core_N + iron_N + friction
    return {"core_N": round(core_N), "iron_N": round(iron_N), "per_part_N": round(per_part, 1), "need_N": round(need),
            "rating_N": P.rel_force, "ok": need <= P.rel_force, "time_s": round(P.core_lift / P.rel_speed, 1)}


def ground_point():
    return P.S.castor_y - P.S.castor_trail


def castor_load():
    """Mass (kg) of the lift group on the castors when the lift actuator floats (moment about the pivot)."""
    m = P.MODEL_MASS
    return m["lift_kg"] * (m["lift_cg_y"] - P.pivot[0]) / (ground_point() - P.pivot[0])


def axle_loads(lifted=True, counterweight_kg=0.0):
    """Load (kg) on the front and rear axle. Lifted: the whole head hangs on the robot (release / transport)."""
    m = P.MODEL_MASS
    ground = 0.0 if lifted else castor_load()
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["lift_kg"], m["lift_cg_y"]),
             (counterweight_kg, P.counterweight_y)]
    total = sum(k for k, _ in items) - ground
    moment = sum(k * (y + P.robot_axle_y) for k, y in items) - ground * (ground_point() + P.robot_axle_y)
    front = moment / (2.0 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "on_castors_kg": round(ground, 1),
            "rear_share": round((total - front) / total, 3)}


def counterweight(share=None):
    share = P.rear_share_min if share is None else share
    for n in range(0, P.counterweight_max_plates + 1):
        a = axle_loads(True, n * P.counterweight_plate_kg)
        if a["rear_share"] >= share:
            return {"plates": n, "kg": n * P.counterweight_plate_kg, "rear_share": a["rear_share"]}
    a = axle_loads(True, P.counterweight_max_plates * P.counterweight_plate_kg)
    return {"plates": None, "rear_share_with_max": a["rear_share"]}


def actuator():
    """Force of the push-blade lift actuator to lift the lift group to the release and transport pose."""
    B = P.B
    m = P.MODEL_MASS
    out = {}
    for lift in (P.lift_work, P.lift_hop, P.lift_transport):
        a = math.radians(lift)
        dy, dz = B.act_rod[0] - B.pivot[0], B.act_rod[1] - B.pivot[1]
        ry = B.pivot[0] + dy * math.cos(a) - dz * math.sin(a)
        rz = B.pivot[1] + dy * math.sin(a) + dz * math.cos(a)
        uy, uz = ry - B.act_base[0], rz - B.act_base[1]
        L = math.hypot(uy, uz)
        lever = abs((ry - B.pivot[0]) * uz / L - (rz - B.pivot[1]) * uy / L)
        cy = B.pivot[0] + (m["lift_cg_y"] - B.pivot[0]) * math.cos(a) - (m["lift_cg_z"] - B.pivot[1]) * math.sin(a)
        moment = m["lift_kg"] * P.g * (cy - B.pivot[0]) / 1000.0
        out["lift_%g" % lift] = {"lever_mm": round(lever, 1), "moment_Nm": round(moment),
                                 "force_N": round(moment / lever * 1000.0)}
    need = max(v["force_N"] for v in out.values())
    out["rating_N"] = P.act_force
    out["ok"] = need <= P.act_force
    out["lift_time_s"] = round(abs(B.act_length(P.lift_hop) - B.act_length(P.lift_work)) / P.act_speed, 1)
    return out


def drive():
    """Drag (N) on grass: rolling resistance of the robot and the castors; drive power (W)."""
    a = axle_loads(False)
    roll = P.crr_grass * (a["front_kg"] + a["rear_kg"]) * P.g
    castor = P.crr_castor * a["on_castors_kg"] * P.g
    drag = roll + castor
    cont = P.hub_torque_nom * P.n_driven / P.r_load
    return {"rolling_N": round(roll), "castor_N": round(castor), "drag_N": round(drag), "motor_cont_N": round(cont),
            "drive_W": round(drag * P.speed / P.eta_drive)}


def capacity():
    """Work rate, area per battery charge and how often the skin must be emptied."""
    width = (P.mag_n * P.mag_size[0] + 2.0 * P.fringe - P.overlap) / 1000.0
    m2_h = width * P.speed * 3600.0
    w = drive()["drive_W"] + P.electronics_W
    hours = P.robot_battery_wh / w
    kg_h = m2_h / 10000.0 * P.iron_per_ha
    return {"width_m": round(width, 2), "m2_h": round(m2_h), "ha_h": round(m2_h / 10000.0, 2), "power_W": round(w),
            "hours": round(hours, 1), "ha_per_charge": round(m2_h * hours / 10000.0, 1),
            "iron_kg_h": round(kg_h, 2), "empty_every_ha": round(P.skin_load_max / P.iron_per_ha, 2),
            "empty_every_min": round(P.skin_load_max / kg_h * 60.0) if kg_h > 0 else None}


def report():
    out = {"field": field(), "pickup": pickup(), "release": release_force(), "axle_work": axle_loads(False),
           "release_bottle_caps": release_force("bottle_cap_crown"), "axle_lifted": axle_loads(True), "counterweight_lifted": counterweight(),
           "counterweight_hop": counterweight(P.rear_share_hop), "actuator": actuator(), "drive": drive(),
           "capacity": capacity()}
    for k, v in out.items():
        if isinstance(v, dict) and all(isinstance(x, dict) for x in v.values()):
            print(k)
            for kk, vv in v.items():
                print("   ", kk, vv)
        else:
            print(k, v)
    return out


if __name__ == "__main__":
    report()
