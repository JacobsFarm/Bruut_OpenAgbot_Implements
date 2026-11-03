"""Calculations for the debris vacuum, in pure Python (same parameters as the model).

    import dvc_calc
    dvc_calc.report()          # prints and returns all key figures

Air: flow Q = v_hose x hose area; pressure drop = dynamic pressure x (nozzle + hose friction + bends + bin) + screen;
fan power = Q dp / eta. Pick-up: an item is carried when the hose air speed is at least convey_factor x its terminal
speed v_t = sqrt(2 m g / (rho Cd A)); the brush flicks it from the sward into the nozzle.
Masses come from build_dvc.mass_properties() (copied into dvc_params.MODEL_MASS after a rebuild).
"""
import math

import dvc_params as P


def air():
    d = (P.hose_d - 12.0) / 1000.0
    area = math.pi * d * d / 4.0
    q = P.hose_v * area
    dyn = 0.5 * P.rho_air * P.hose_v ** 2
    k = P.K_nozzle + P.f_hose * P.hose_len / d + P.K_bends + P.K_bin
    dp = dyn * k + P.dp_screen
    power = q * dp / P.eta_fan
    return {"Q_m3_s": round(q, 3), "Q_m3_h": round(q * 3600), "slot_m_s": round(q / P.slot_area, 1),
            "dp_Pa": round(dp), "fan_W": round(power), "fan_load": round(power / P.fan_W, 2)}


def items():
    out = {}
    for k, (g, a, cd) in P.ITEMS.items():
        vt = math.sqrt(2.0 * g / 1000.0 * P.g / (P.rho_air * cd * a))
        out[k] = {"v_t_m_s": round(vt, 1), "hose_ok": P.hose_v >= P.convey_factor * vt,
                  "fits_D125": True}
    return out


def brush():
    omega = P.brush_rpm * 2.0 * math.pi / 60.0
    tip = omega * P.brush_d / 2000.0
    f_t = P.mu_bristle * P.brush_N_per_m * P.brush_l / 1000.0
    w = f_t * tip + P.brush_air_W
    return {"tip_m_s": round(tip, 1), "mech_W": round(w), "electric_W": round(w / P.eta_brush)}


def castor_load():
    m = P.MODEL_MASS
    gy = P.S.castor_y - P.S.castor_trail
    return m["lift_kg"] * (m["lift_cg_y"] - P.pivot[0]) / (gy - P.pivot[0])


def axle_loads(lifted=False, load_kg=0.0, counterweight_kg=0.0):
    """Front / rear axle load (kg); load_kg in the bin (at the bin centre)."""
    m = P.MODEL_MASS
    ground = 0.0 if lifted else castor_load()
    gy = P.S.castor_y - P.S.castor_trail
    items = [(P.robot_mass, P.robot_cg_y), (m["mount_kg"], m["mount_cg_y"]), (m["lift_kg"], m["lift_cg_y"]),
             (m["bin_kg"] + load_kg, m["bin_cg_y"]), (m["hose_kg"], 1000.0), (counterweight_kg, P.counterweight_y)]
    total = sum(k for k, _ in items) - ground
    moment = sum(k * (y + P.robot_axle_y) for k, y in items) - ground * (gy + P.robot_axle_y)
    front = moment / (2.0 * P.robot_axle_y)
    return {"front_kg": round(front, 1), "rear_kg": round(total - front, 1), "on_castors_kg": round(ground, 1),
            "rear_share": round((total - front) / total, 3)}


def counterweight(share, load_kg=0.0):
    for n in range(0, P.counterweight_max_plates + 1):
        a = axle_loads(True, load_kg, n * P.counterweight_plate_kg)
        if a["rear_share"] >= share:
            return {"plates": n, "kg": n * P.counterweight_plate_kg, "rear_share": a["rear_share"]}
    return {"plates": None}


def actuator():
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
        out["lift_%g" % lift] = round(m["lift_kg"] * P.g * (cy - B.pivot[0]) / lever)
    out["rating_N"] = P.act_force
    out["ok"] = max(v for k, v in out.items() if k.startswith("lift")) <= P.act_force
    return out


def drive(load_kg=0.0):
    a = axle_loads(False, load_kg)
    roll = P.crr_grass * (a["front_kg"] + a["rear_kg"]) * P.g
    castor = P.crr_castor * a["on_castors_kg"] * P.g
    br = P.mu_bristle * P.brush_N_per_m * P.brush_l / 1000.0
    drag = roll + castor + br
    return {"drag_N": round(drag), "drive_W": round(drag * P.speed / P.eta_drive)}


def capacity():
    width = (P.brush_l - P.overlap) / 1000.0
    m2_h = width * P.speed * 3600.0
    w = air()["fan_W"] + brush()["electric_W"] + drive(P.bin_load_max / 2.0)["drive_W"]
    hours = P.robot_battery_wh / w
    litter_kg = min(P.liner_l / 1000.0 * P.litter_bulk, P.bin_load_max)
    shards_l = P.bin_load_max / P.shard_bulk * 1000.0
    return {"width_m": width, "m2_h": round(m2_h), "ha_h": round(m2_h / 1e4, 2), "power_W": round(w),
            "hours": round(hours, 2), "ha_per_charge": round(m2_h * hours / 1e4, 2),
            "litter_per_bag_kg": round(litter_kg), "bag_every_ha": round(litter_kg / P.litter_per_ha, 2),
            "shards_max_l": round(shards_l)}


def report():
    out = {"air": air(), "items": items(), "brush": brush(), "axle_work_empty": axle_loads(False),
           "axle_work_full": axle_loads(False, P.bin_load_max), "axle_lifted": axle_loads(True),
           "ballast_hop": counterweight(P.rear_share_hop), "ballast_transport": counterweight(P.rear_share_min),
           "actuator": actuator(), "drive_full": drive(P.bin_load_max), "capacity": capacity()}
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
