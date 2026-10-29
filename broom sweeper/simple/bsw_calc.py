"""Calculations for the broom / sweeper, in pure Python (same parameters as the model).

    import bsw_calc
    bsw_calc.report()          # prints and returns all key figures

Masses come from build_bsw.mass_properties() (copied into bsw_params.MODEL_MASS after a rebuild).
"""
import math

import bsw_params as P


def brush_speed():
    """Brush speed (rpm), tip speed (m/s) and the speed ratio of the belt."""
    belt = P.pulley_small[0] / float(P.pulley_big[0])
    rpm = P.motor_rpm / P.gear_ratio * belt
    tip = rpm * math.pi * P.brush_d / 1000.0 / 60.0
    return {"brush_rpm": round(rpm), "tip_m_s": round(tip, 1), "belt_ratio": round(1.0 / belt, 2)}


def brush_power(material="dry_sand_grit", angle_deg=25.0):
    """Mechanical and electrical power (W) of the brush: bristle friction on the floor, throwing the material, windage."""
    sp = brush_speed()
    omega = sp["brush_rpm"] * 2.0 * math.pi / 60.0
    L = P.brush_l / 1000.0
    f_n = P.contact_N_per_m * L
    f_t = P.mu_bristle * f_n                            # tangential force at the bristle tips
    torque = f_t * P.brush_d / 2000.0
    friction_W = torque * omega
    width = P.brush_l * math.cos(math.radians(angle_deg)) / 1000.0
    m_dot = P.MATERIAL[material] * width * P.speed      # kg/s swept
    v = P.throw_speed * sp["tip_m_s"]
    throw_W = 0.5 * m_dot * v * v
    mech = friction_W + throw_W + P.air_loss_W
    elec = mech / (P.eta_belt * P.eta_motor)
    return {"contact_N": round(f_n), "tangential_N": round(f_t), "torque_Nm": round(torque, 1),
            "friction_W": round(friction_W), "throw_W": round(throw_W), "mech_W": round(mech),
            "electric_W": round(elec), "motor_load": round(mech / P.eta_belt / P.motor_w, 2), "swept_kg_s": round(m_dot, 2)}


def axle_loads(lifted=True, counterweight_kg=0.0):
    """Load (kg) on the front and rear axle. Lifted: the whole broom hangs on the robot (transport).
    Work: the castors carry their share of the lift group (the actuator floats)."""
    m = P.MODEL_MASS
    ground = 0.0 if lifted else castor_load()
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["lift_kg"], m["lift_cg_y"]),
             (counterweight_kg, P.counterweight_y)]
    total = sum(k for k, _ in items) - ground
    ground_y = P.castor_y - P.castor_trail
    moment = sum(k * (y + P.robot_axle_y) for k, y in items) - ground * (ground_y + P.robot_axle_y)
    front = moment / (2.0 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "on_castors_kg": round(ground, 1),
            "rear_share": round((total - front) / total, 3)}


def castor_load():
    """Mass (kg) of the lift group on the castors and bristles when the actuator floats (moment about the pivot).
    The bristle force is taken off, the rest is on the castors."""
    m = P.MODEL_MASS
    ground_y = P.castor_y - P.castor_trail
    on_ground = m["lift_kg"] * (m["lift_cg_y"] - P.pivot[0]) / (ground_y - P.pivot[0])
    bristle_kg = P.contact_N_per_m * P.brush_l / 1000.0 / P.g
    return on_ground - bristle_kg * (P.axis_y - ground_y) / (ground_y - P.pivot[0])


def counterweight(share=None):
    """Ballast plates (11 kg) on the rear stacks so the rear axle keeps 'share' with the head lifted; None if the
    counterweights (at most counterweight_max_plates) are not enough."""
    share = P.rear_share_min if share is None else share
    for n in range(0, P.counterweight_max_plates + 1):
        a = axle_loads(True, n * P.counterweight_plate_kg)
        if a["rear_share"] >= share:
            return {"plates": n, "kg": n * P.counterweight_plate_kg, "rear_share": a["rear_share"]}
    a = axle_loads(True, P.counterweight_max_plates * P.counterweight_plate_kg)
    return {"plates": None, "rear_share_with_max": a["rear_share"]}


def actuator():
    """Lever arm of the actuator about the pivot and force to lift the lift group (same geometry as the push blade)."""
    B = P.B
    m = P.MODEL_MASS
    out = {}
    for lift in (P.lift_work, P.lift_transport):
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
    out["push_blade_actuator_ok"] = need <= B.act_force
    out["ok"] = need <= P.act_force
    out["lift_time_s"] = round(abs(B.act_length(P.lift_transport) - B.act_length(P.lift_work)) / P.act_speed, 1)
    return out


def drive(angle_deg=25.0):
    """Drag on the robot (N): rolling resistance, castors and the brush reaction, and the side force of an angled
    brush (the material is thrown sideways); compared with the 4 hub motors."""
    a = axle_loads(False)
    on_wheels = a["front_kg"] + a["rear_kg"]
    bp = brush_power(angle_deg=angle_deg)
    roll = P.crr_floor * on_wheels * P.g
    castor = P.crr_castor * a["on_castors_kg"] * P.g
    brush = bp["tangential_N"]                         # bottom turns forward: pushes the robot back
    along = roll + castor + brush * math.cos(math.radians(angle_deg))
    side = brush * math.sin(math.radians(angle_deg))
    cont = P.hub_torque_nom * P.n_driven / P.r_load
    drive_W = along * P.speed / P.eta_drive
    return {"rolling_N": round(roll), "castor_N": round(castor), "brush_N": round(brush), "drag_N": round(along),
            "side_N": round(side), "motor_cont_N": round(cont), "drive_W": round(drive_W)}


def capacity(angle_deg=25.0, material="dry_sand_grit"):
    """Area per hour (m2/h) and per battery charge (m2), brush + drive power."""
    width = (P.brush_l * math.cos(math.radians(angle_deg)) - P.overlap) / 1000.0
    m2_h = width * P.speed * 3600.0
    w = brush_power(material, angle_deg)["electric_W"] + drive(angle_deg)["drive_W"]
    hours = P.robot_battery_wh / w
    return {"width_m": round(width, 2), "m2_h": round(m2_h), "power_W": round(w), "hours": round(hours, 2),
            "m2_per_charge": round(m2_h * hours)}


def report():
    out = {"brush": brush_speed(), "power": {k: brush_power(k) for k in P.MATERIAL},
           "axle_transport": axle_loads(True), "axle_work": axle_loads(False), "counterweight_lifted_transport": counterweight(),
           "counterweight_hop": counterweight(P.rear_share_hop),
           "actuator": actuator(), "drive_25deg": drive(25.0), "capacity_25deg": capacity(25.0),
           "capacity_straight": capacity(0.0)}
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    report()
