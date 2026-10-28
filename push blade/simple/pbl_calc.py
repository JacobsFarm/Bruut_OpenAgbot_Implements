"""Calculations for the push blade, in pure Python (same parameters as the model).

    import pbl_calc
    pbl_calc.report()          # prints and returns all key figures

Masses come from build_pbl.mass_properties() (copied into pbl_params.MODEL_MASS after a rebuild).
"""
import math

import pbl_params as P


def axle_loads(lifted=True):
    """Load (kg) on the front and rear axle. Lifted: the whole blade hangs on the robot (transport).
    Work: part of the lift group rests on the floor through the rubber edge (float)."""
    m = P.MODEL_MASS
    ground = 0.0 if lifted else edge_ground_load()
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["lift_kg"], m["lift_cg_y"])]
    total = sum(k for k, _ in items) - ground
    moment = sum(k * (y - (-P.robot_axle_y)) for k, y in items) - ground * (P.edge_y + P.robot_axle_y)
    front = moment / (2.0 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "on_floor_kg": round(ground, 1),
            "rear_share": round((total - front) / total, 3)}


def edge_ground_load():
    """Mass (kg) of the lift group that rests on the rubber edge when the actuator floats (moment about the pivot)."""
    m = P.MODEL_MASS
    return m["lift_kg"] * (m["lift_cg_y"] - P.pivot[0]) / (P.edge_y - P.pivot[0])


def drive_limit():
    """Push force (N) the 4 hub motors give: continuous and peak."""
    f = P.n_driven / P.r_load
    return P.hub_torque_nom * f, P.hub_torque_peak * f


def push_force(floor, held=False):
    """Net push force (N) at the blade on a floor: the smaller of grip and motor (continuous), minus rolling
    resistance of the robot and friction of the rubber edge on the floor. held: the actuator holds the blade at a set
    height (grading), the whole blade weight is on the wheels and the edge does not rub."""
    a = axle_loads(lifted=held)
    on_wheels = a["front_kg"] + a["rear_kg"]
    grip = P.mu_tyre[floor] * on_wheels * P.g
    cont, peak = drive_limit()
    roll = P.crr[floor] * on_wheels * P.g
    edge = P.mu_edge * a["on_floor_kg"] * P.g
    return {"grip_N": round(grip), "motor_cont_N": round(cont), "motor_peak_N": round(peak),
            "rolling_N": round(roll), "edge_friction_N": round(edge),
            "net_cont_N": round(min(grip, cont) - roll - edge), "net_peak_N": round(min(grip, peak) - roll - edge),
            "limited_by": "grip" if grip < cont else "motors"}


def pile(material, angle_deg=0.0):
    """Material that a full blade holds (kg): triangle in front of the blade at the angle of repose, at most
    pile_len_max long, over the effective width."""
    mt = P.MATERIAL[material]
    h = (P.blade_h - 30.0) / 1000.0
    w = P.blade_w * math.cos(math.radians(angle_deg)) / 1000.0
    length = min(h / math.tan(math.radians(mt["repose"])), P.pile_len_max)
    area = 0.5 * h * length
    mass = area * w * mt["rho"]
    return mass, mt["mu_floor"] * mass * P.g


def materials():
    out = {}
    for name, mt in P.MATERIAL.items():
        f = push_force(mt["floor"], held=mt.get("held", False))
        full_kg, full_N = pile(name)
        max_kg = max(f["net_cont_N"], 0) / (mt["mu_floor"] * P.g)
        out[name] = {"full_blade_kg": round(full_kg), "full_blade_N": round(full_N), "net_cont_N": f["net_cont_N"],
                     "max_pile_kg": round(max_kg), "full_blade_ok": full_N <= f["net_cont_N"]}
    return out


def grading_depth(angle_deg=0.0):
    """Cut depth (mm) at the start of a cut in loose topsoil (blade held by the actuator, no pile yet) and the
    distance (m) after which the pile in front of the blade reaches the most the robot can push."""
    f = push_force("loose_soil", held=True)["net_cont_N"]
    w = P.blade_w * math.cos(math.radians(angle_deg)) / 1000.0
    depth = max(0.0, f / (P.k_cut * w))                              # m
    max_kg = f / (P.MATERIAL["loose_soil"]["mu_floor"] * P.g)
    cut_d = P.grading_cut / 1000.0
    dist = max_kg / (P.MATERIAL["loose_soil"]["rho"] * w * cut_d)
    return {"start_cut_mm": round(depth * 1000.0), "max_pile_kg": round(max_kg),
            "distance_at_%gmm_m" % P.grading_cut: round(dist, 2)}


def actuator():
    """Lever arm of the actuator about the pivot, force needed to lift the blade and lengths over the poses."""
    m = P.MODEL_MASS
    out = {}
    for lift in (P.lift_work, P.lift_transport):
        a = math.radians(lift)
        dy, dz = P.act_rod[0] - P.pivot[0], P.act_rod[1] - P.pivot[1]
        ry = P.pivot[0] + dy * math.cos(a) - dz * math.sin(a)
        rz = P.pivot[1] + dy * math.sin(a) + dz * math.cos(a)
        uy, uz = ry - P.act_base[0], rz - P.act_base[1]
        L = math.hypot(uy, uz)
        lever = abs((ry - P.pivot[0]) * uz / L - (rz - P.pivot[1]) * uy / L)      # mm
        cy = P.pivot[0] + (m["lift_cg_y"] - P.pivot[0]) * math.cos(a) - (m["lift_cg_z"] - P.pivot[1]) * math.sin(a)
        moment = m["lift_kg"] * P.g * (cy - P.pivot[0]) / 1000.0                  # Nm
        out["lift_%g" % lift] = {"length": round(L, 1), "lever_mm": round(lever, 1), "moment_Nm": round(moment),
                                 "force_N": round(moment / lever * 1000.0)}
    lens = [P.act_length(x) for x in P.LIFT_POSES]
    out["length_range"] = (round(min(lens), 1), round(max(lens), 1))
    out["fits_stroke"] = P.act_retracted <= min(lens) and max(lens) <= P.act_retracted + P.act_stroke
    out["edge_lift_transport_mm"] = round(P.edge_lift(P.lift_transport), 1)
    out["lift_time_s"] = round((P.act_length(P.lift_work) - P.act_length(P.lift_transport)) / P.act_speed, 1)
    return out


def power(floor="concrete_dry"):
    """Electrical power (W) at the continuous push force and working speed (motor efficiency eta_drive)."""
    f = push_force(floor)
    return round(min(f["grip_N"], f["motor_cont_N"]) * P.speed / P.eta_drive)


def report():
    out = {"axle_transport": axle_loads(True), "axle_work": axle_loads(False),
           "push": {k: push_force(k) for k in P.mu_tyre}, "push_held_loose_soil": push_force("loose_soil", True), "materials": materials(),
           "grading": grading_depth(), "grading_25deg": grading_depth(25.0),
           "actuator": actuator(), "power_W": power(),
           "effective_width_25deg": round(P.blade_w * math.cos(math.radians(25.0)))}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
