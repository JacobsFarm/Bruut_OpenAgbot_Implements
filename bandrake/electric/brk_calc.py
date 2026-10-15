"""Calculations for the electric belt rake (pure Python, no FreeCAD): belt path and tine positions, working width,
comb line spacing, tine forces in both modes, drive torque and power, the side force on the robot, parallelogram and
lift actuator, axle loads in work and lifted, capacity and battery.

    python brk_calc.py          (or in FreeCAD: import brk_calc; brk_calc.report())
"""
import math

import brk_params as P

G_ACC = 9.81

# last measurement from the model (build_brk.mass_properties: steel 7850, aluminium 2700, rubber 1200 kg/m3, bought
# parts with their catalogue mass). MODEL is updated by hand after a rebuild.
MODEL = {"kg": 134.3, "cg": (10.0, 940.0, 361.0), "rake_kg": 110.4, "rake_cg": (12.0, 1041.0, 322.0),
         "mount_kg": 23.9, "mount_cg": (0.0, 476.0, 546.0)}


# ---------------------------------------------------------------------
# Belt path (x-z plane). s = 0 at the bottom centre, running towards -x on the bottom run (delivery to the left),
# up around the left drum, +x on the top run, down around the right drum.
# ---------------------------------------------------------------------
def path(s, r=P.r_pitch, z0=None):
    """Point (x, z) on the loop at radius r from the drum axes (r_pitch: belt centre) and the outward normal angle
    (deg, 0 = +x, -90 = down) and the travel direction (deg)."""
    z0 = P.drum_z if z0 is None else z0
    L = 2.0 * P.drum_x
    arc = math.pi * P.r_pitch
    s = s % P.belt_len
    half = L / 2.0
    if s < half:                                        # bottom run, from x 0 to -drum_x
        x, n = -s, -90.0
        return (x, z0 - r, n)
    s -= half
    if s < arc:                                         # left arc, from bottom to top
        a = math.radians(-90.0 - math.degrees(s / P.r_pitch))   # -90 -> -270 (= +90)
        return (-P.drum_x + r * math.cos(a), z0 + r * math.sin(a), math.degrees(a))
    s -= arc
    if s < L:                                           # top run, from -drum_x to +drum_x
        return (-P.drum_x + s, z0 + r, 90.0)
    s -= L
    if s < arc:                                         # right arc, top to bottom
        a = math.radians(90.0 - math.degrees(s / P.r_pitch))     # 90 -> -90
        return (P.drum_x + r * math.cos(a), z0 + r * math.sin(a), math.degrees(a))
    s -= arc
    return (P.drum_x - s, z0 - r, -90.0)                # bottom run, from +drum_x back to 0


def tip(s, z0=None):
    """Tine tip (x, z) of a bar at belt position s (tines radial, from the belt outer surface)."""
    x, z, n = path(s, P.r_pitch, z0)
    d = P.belt_t / 2.0 + P.bar[0] + P.tine_len
    return (x + d * math.cos(math.radians(n)), z + d * math.sin(math.radians(n)))


def drum_z(mode="comb"):
    return P.r_tip + P.modes[mode]["tip_z"]


def working_width(mode="comb", reach=40.0, n=4000):
    """Width (x) over which the tine tips are lower than the ground + reach (mm)."""
    z0 = drum_z(mode)
    xs = []
    for i in range(n):
        x, z = tip(P.belt_len * i / float(n), z0)
        if z <= reach:
            xs.append(x)
    return min(xs), max(xs)


def legs_working(mode="comb", n_phase=40):
    """Average number of tine legs with the tip lower than the mode's reach (in the soil, or in the litter layer)."""
    z0 = drum_z(mode)
    reach = P.modes[mode]["reach"]
    tot = 0
    for k in range(n_phase):
        ph = P.bar_pitch * k / float(n_phase)
        for b in range(P.n_bars):
            x, z = tip(ph + b * P.bar_pitch, z0)
            if z <= reach:
                tot += P.n_legs
    return tot / float(n_phase)


def comb(mode="comb"):
    m = P.modes[mode]
    v, u = m["v"], m["u"]
    f_bar = u * 1000.0 / P.bar_pitch                   # bars per second passing a point
    advance = v * 1000.0 / f_bar                        # robot advance between two bars
    band = (P.n_legs - 1) * P.leg_pitch + P.tine_wire
    return {"bars_per_s": f_bar, "advance": advance, "line_spacing": advance / P.n_legs, "band": band,
            "overlap": band / advance, "angle": math.degrees(math.atan2(v, u))}


# ---------------------------------------------------------------------
# Forces and drive
# ---------------------------------------------------------------------
def forces(mode="comb"):
    m = P.modes[mode]
    v, u = m["v"], m["u"]
    n = legs_working(mode)
    w = math.hypot(u, v)
    F = n * m["leg_N"]
    lat = F * u / w                                     # on the rake towards +x (material and soil pushed to -x)
    drag = F * v / w                                    # against the travel
    x0, x1 = working_width(mode)
    width = (x1 - x0) / 1000.0
    litter = 0.0
    if mode == "rake":
        # material: everything on the width is carried on average half the width and pushed over the ground
        mdot = P.litter_kg_m2 * width * v               # kg/s raked
        litter = mdot * (width / 2.0) / u * G_ACC * P.mu_material   # N of friction, average material on the belt
        lat += litter
    return {"legs": n, "F": F, "lat": lat, "drag": drag, "litter_N": litter, "width": width}


def drive(mode="comb", rake_kg=None):
    m = P.modes[mode]
    f = forces(mode)
    u = m["u"]
    T_drum = f["lat"] * P.r_pitch / 1000.0             # Nm
    rpm_drum = u * 1000.0 / P.r_pitch * 60.0 / (2.0 * math.pi)
    rpm_motor = rpm_drum * P.gear_ratio
    P_belt = f["lat"] * u + P.bearing_loss_W
    P_el = P_belt / (P.gear_eff * P.motor_eff)
    T_motor = (T_drum + P.bearing_loss_W / (u * 1000.0 / P.r_pitch)) / (P.gear_ratio * P.gear_eff)
    T_rated = P.motor_P / (P.motor_rpm * 2.0 * math.pi / 60.0)
    rake_kg = MODEL["rake_kg"] if rake_kg is None else rake_kg
    roll = rake_kg * G_ACC * P.c_rr_caster
    return {"T_drum": T_drum, "rpm_drum": rpm_drum, "rpm_motor": rpm_motor, "P_belt": P_belt, "P_el": P_el,
            "T_motor": T_motor, "T_rated": T_rated, "load": P_el / P.motor_P, "push": f["drag"] + roll,
            "P_push": (f["drag"] + roll) * m["v"]}


def side_force(mode="comb"):
    """The side force of the rake must be taken by the robot tyres: front and rear axle lateral forces (N), against
    the grip mu_tire x axle load, in work."""
    f = forces(mode)
    ax = axle_loads(lifted=False)
    y = MODEL["rake_cg"][1]
    Ff = f["lat"] * (y + P.robot_axle_y) / P.robot_wheelbase
    Fr = f["lat"] - Ff
    grip_f = P.mu_tire * ax["front_kg"] * G_ACC
    grip_r = P.mu_tire * ax["rear_kg"] * G_ACC
    return {"lat": f["lat"], "front": Ff, "rear": Fr, "grip_front": grip_f, "grip_rear": grip_r,
            "use_front": abs(Ff) / grip_f, "use_rear": abs(Fr) / grip_r, "yaw_Nm": f["lat"] * y / 1000.0}


# ---------------------------------------------------------------------
# Parallelogram and lift
# ---------------------------------------------------------------------
def head_offset(lift):
    b = math.asin(max(-1.0, min(1.0, lift / P.arm_len)))
    return (-P.arm_len * (1.0 - math.cos(b)), lift, math.degrees(b))     # rake moves back a little when it rises


def lift(rake_kg=None):
    """Castor actuators: force to carry the rake (all of its weight is on the castors) and lift it for the headland."""
    rake_kg = MODEL["rake_kg"] if rake_kg is None else rake_kg
    F = rake_kg * G_ACC / 2.0
    ext = {"comb": P.cact_ext_work, "rake": P.cact_ext_work + (P.tip_z_rake - P.tip_z_comb),
           "headland": P.cact_ext_work + P.lift_travel}
    return {"F": F, "reserve": P.cact_force / F, "ext": ext, "fits": max(ext.values()) <= P.cact_stroke,
            "t": P.lift_travel / P.cact_speed, "beta_float": head_offset(P.float_up)[2],
            "beta_lift": head_offset(P.lift_travel)[2]}


# ---------------------------------------------------------------------
# Axle loads
# ---------------------------------------------------------------------
def axle_loads(lifted=False):
    """Robot + rake. In work the casters carry the rake; the parallelogram floats (no vertical force) but holds the
    rake level: the robot gets the moment rake weight x (caster - cg). Lifted: the whole rake hangs on the robot."""
    rk, (_, ry, rz) = MODEL["rake_kg"], MODEL["rake_cg"]
    mk, (_, my, mz) = MODEL["mount_kg"], MODEL["mount_cg"]
    W_rob = P.robot_kg + mk
    y_rob = (P.robot_kg * P.robot_cg[1] + mk * my) / W_rob
    if lifted:
        m = W_rob + rk
        y = (W_rob * y_rob + rk * ry) / m
        front = m * (0.5 + y / P.robot_wheelbase)
    else:
        caster_y = P.caster_y - P.caster_offset
        M = rk * (caster_y - ry)                          # kg mm, nose-up moment on the robot
        m = W_rob
        front = W_rob * (0.5 + y_rob / P.robot_wheelbase) - M / P.robot_wheelbase
    rear = m - front
    return {"kg": m, "front_kg": front, "rear_kg": rear, "rear_share": rear / m, "wheel_max": max(front, rear) / 2.0}


def capacity(mode="comb"):
    m = P.modes[mode]
    w = forces(mode)["width"]
    gross = w * m["v"] * 3600.0 / 10000.0
    return {"gross_ha_h": gross, "net_ha_h": gross * P.field_eff}


def power(mode="comb"):
    d = drive(mode)
    tot = P.drive_w[mode] + d["P_push"] + d["P_el"] + 15.0      # 15 W controller / sensors
    hours = P.battery_kwh * 1000.0 / tot
    return {"P_total": tot, "hours": hours, "ha": hours * capacity(mode)["net_ha_h"]}


def windrow(passes=4, mode="rake"):
    """Material in the windrow when working from the outside inwards: every pass carries the windrow of the previous
    pass along, so pass n delivers n x width x litter (kg per m of windrow)."""
    w = forces(mode)["width"]
    return [(n, n * w * P.litter_kg_m2) for n in range(1, passes + 1)]


def report():
    lines = ["=== Electric belt rake: key figures ==="]
    x0, x1 = working_width("comb")
    lines.append("Belt loop: drums %.0f mm apart (Ø%.0f), belt %.0f mm wide, %.0f mm long; %d bars every %.0f mm, "
                 "%d tine legs each (%.0f mm long, tip radius %.0f)" % (2 * P.drum_x, P.drum_d, P.belt_w, P.belt_len,
                                                                      P.n_bars, P.bar_pitch, P.n_legs, P.tine_len,
                                                                      P.r_tip))
    for mode in ("comb", "rake"):
        m = P.modes[mode]
        c = comb(mode)
        f = forces(mode)
        d = drive(mode)
        sf = side_force(mode)
        cap = capacity(mode)
        pw = power(mode)
        x0, x1 = working_width(mode)
        lines += ["-- %s (%s): %.1f m/s, belt %.1f m/s, tine tips at z %+.0f" % (mode, m["label"], m["v"], m["u"],
                                                                                  m["tip_z"]),
                  "   working width %.2f m (x %.0f .. %.0f); %.1f bars/s, robot moves %.0f mm between two bars: comb "
                  "lines %.0f mm apart on average, each point combed by %.1f bars, tines at %.0f deg to the travel" % (
                      f["width"], x0, x1, c["bars_per_s"], c["advance"], c["line_spacing"], c["overlap"],
                      90 - c["angle"]),
                  "   %.0f legs working x %.1f N = %.0f N: sideways %.0f N (material %.1f N), drag %.0f N" % (
                      f["legs"], m["leg_N"], f["F"], f["lat"], f["litter_N"], f["drag"]),
                  "   drum %.0f rpm, %.1f Nm; motor %.0f rpm (rated %.0f), %.2f Nm of %.2f; belt %.0f W, electric "
                  "%.0f W (%.0f %% of %.0f W)" % (d["rpm_drum"], d["T_drum"], d["rpm_motor"], P.motor_rpm,
                                                  d["T_motor"], d["T_rated"], d["P_belt"], d["P_el"], 100 * d["load"],
                                                  P.motor_P),
                  "   side force on the robot %.0f N: front tyres %.0f N (%.0f %% of grip), rear %.0f N (%.0f %%), "
                  "yaw %.0f Nm" % (sf["lat"], sf["front"], 100 * sf["use_front"], sf["rear"], 100 * sf["use_rear"],
                                   sf["yaw_Nm"]),
                  "   push %.0f N (%.0f W); capacity %.2f ha/h gross, %.2f net; %.0f W total -> %.1f h, %.1f ha on "
                  "%.1f kWh" % (d["push"], d["P_push"], cap["gross_ha_h"], cap["net_ha_h"], pw["P_total"],
                                pw["hours"], pw["ha"], P.battery_kwh)]
    lf = lift()
    work, up = axle_loads(False), axle_loads(True)
    lines += ["Castor actuators: %.0f N each to carry the rake (x %.1f of %.0f N); rod out comb %.0f / rake %.0f / "
              "headland %.0f mm of %.0f (fits %s); headland lift %.0f mm in %.1f s; parallelogram %.0f deg at the "
              "headland, float stop %.0f deg" % (lf["F"], lf["reserve"], P.cact_force, lf["ext"]["comb"],
                                                lf["ext"]["rake"], lf["ext"]["headland"], P.cact_stroke, lf["fits"],
                                                P.lift_travel, lf["t"], lf["beta_lift"], lf["beta_float"]),
              "Mass %.0f kg (rake %.0f, mount %.0f); the castors carry the rake: robot front %.0f / rear %.0f kg "
              "(the rake's moment lifts the front a little); if the rake hung on the robot: front %.0f / rear %.0f kg "
              "(rear %.0f %%: not done)" % (MODEL["kg"], MODEL["rake_kg"], MODEL["mount_kg"], work["front_kg"],
                                           work["rear_kg"], up["front_kg"], up["rear_kg"], 100 * up["rear_share"]),
              "Windrow from outside to inside (%.2f kg/m2 litter): " % P.litter_kg_m2 + ", ".join(
                  "pass %d %.2f kg/m" % r for r in windrow())]
    print("\n".join(lines))
    return lines


if __name__ == "__main__":
    report()
