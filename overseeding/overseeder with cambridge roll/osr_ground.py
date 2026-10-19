"""Process model for the animation (pure Python, no FreeCAD): the lawn with bare patches, the drive path, the
kinematics of the robot and the trailer, the camera, the on/off control of the seeder and what happens to the soil.

World coordinates: x = east, y = north, mm. Heading psi = angle of the driving direction from +y, counter-clockwise
(the robot model rotated by psi about z).

    import osr_ground as GR
    sim = GR.simulate()         # list of states at DT (20 Hz), all the figures of the run
    GR.stats(sim[-1])           # coverage and waste at the end

Ground: cells of CELL mm. Only the bare cells are tracked (bare / seen by the camera / seeded / rolled). The seeded
area on green grass (waste) is the swept area of the drop line while seed falls, minus the bare cells it hits.
"""
import math
import random

import osr_params as P
import osr_calc as OC
import ovd_calc as VC
import cbr_calc as CC

DT = 0.05                       # s, simulation step
CELL = P.O.cell                 # 50 mm

# ---------------------------------------------------------------------
# Field: two passes of 1 m with a U turn (right) between them. Patches of bare soil in both lanes.
# ---------------------------------------------------------------------
RADIUS = 2250.0                 # rear axle radius in the turn (smallest: osr_calc.min_radius() = 2107)
LANE_X = (0.0, 2.0 * RADIUS)    # x of the two passes
Y_START = -1600.0               # rear axle at the start (the drop line is 1.46 m behind it)
Y_TURN = 5200.0                 # turn starts here
Y_END = -2000.0                 # pass 2 ends here: the roll has passed the last patch
SPEED = P.O.work_speed * 1000.0     # mm/s
ACC = 400.0                     # mm/s2

# Patches: centre x, y, radius x, radius y, shape seed. Kept inside the 1 m strips (the strip edges at +-500).
PATCHES = [(-120.0, 900.0, 300.0, 210.0, 1), (230.0, 2350.0, 190.0, 330.0, 2), (-60.0, 3800.0, 360.0, 290.0, 3),
           (4380.0, 4000.0, 150.0, 140.0, 4), (4620.0, 2700.0, 240.0, 200.0, 5), (4440.0, 1150.0, 300.0, 260.0, 6)]
NOISE_CELLS = [(330.0, 3050.0), (4180.0, 3400.0)]      # single bare cells: below the threshold, must not switch on


def _inside(x, y, patch):
    cx, cy, rx, ry, seed = patch
    dx, dy = (x - cx) / rx, (y - cy) / ry
    r = math.hypot(dx, dy)
    a = math.atan2(dy, dx)
    rnd = random.Random(seed)
    p1, p2 = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
    edge = 1.0 + 0.18 * math.sin(3 * a + p1) + 0.10 * math.sin(5 * a + p2)
    return r <= edge


def bare_cells():
    """Set of (i, j): cell i covers x i*CELL .. (i+1)*CELL."""
    out = set()
    for patch in PATCHES:
        cx, cy, rx, ry, _ = patch
        for i in range(int((cx - 1.4 * rx) // CELL), int((cx + 1.4 * rx) // CELL) + 1):
            for j in range(int((cy - 1.4 * ry) // CELL), int((cy + 1.4 * ry) // CELL) + 1):
                if _inside((i + 0.5) * CELL, (j + 0.5) * CELL, patch):
                    out.add((i, j))
    for x, y in NOISE_CELLS:
        out.add((int(x // CELL), int(y // CELL)))
    return out


def centre(c):
    return ((c[0] + 0.5) * CELL, (c[1] + 0.5) * CELL)


# ---------------------------------------------------------------------
# Path of the rear axle centre: straight north, half circle to the right, straight south
# ---------------------------------------------------------------------
L1 = Y_TURN - Y_START
LT = math.pi * RADIUS
L2 = Y_TURN - Y_END
LENGTH = L1 + LT + L2


def path(s):
    """(x, y, psi, curvature) of the rear axle centre at path length s."""
    if s <= L1:
        return LANE_X[0], Y_START + s, 0.0, 0.0
    if s <= L1 + LT:
        a = (s - L1) / RADIUS                   # turning right: psi goes from 0 to -pi
        cx = LANE_X[0] + RADIUS
        return cx - RADIUS * math.cos(a), Y_TURN + RADIUS * math.sin(a), -a, -1.0 / RADIUS
    d = s - L1 - LT
    return LANE_X[1], Y_TURN - d, -math.pi, 0.0


def speed_profile():
    """List of (t, s, v) at DT: accelerate, drive at SPEED, brake at the end."""
    out = []
    t = s = v = 0.0
    while s < LENGTH - 0.5:
        brake = v * v / (2 * ACC)
        if LENGTH - s <= brake + 1.0:
            v = max(30.0, v - ACC * DT)
        else:
            v = min(SPEED, v + ACC * DT)
        s = min(LENGTH, s + v * DT)
        t += DT
        out.append((t, s, v))
    return out


def fwd(psi):
    return (-math.sin(psi), math.cos(psi))


def right(psi):
    return (math.cos(psi), math.sin(psi))


def robot_pose(s):
    """Robot centre (x, y), heading, curvature, steering (left, right) in degrees (+ = to the left)."""
    x, y, psi, k = path(s)
    f = fwd(psi)
    half_l = P.C.robot_wheelbase / 2.0
    w = P.C.robot_track / 2.0
    dl = math.degrees(math.atan(P.C.robot_wheelbase * k / (1.0 - k * w))) if k else 0.0
    dr = math.degrees(math.atan(P.C.robot_wheelbase * k / (1.0 + k * w))) if k else 0.0
    return (x + f[0] * half_l, y + f[1] * half_l), psi, k, (dl, dr)


def local_to_world(c, psi, lx, ly):
    r, f = right(psi), fwd(psi)
    return (c[0] + r[0] * lx + f[0] * ly, c[1] + r[1] * lx + f[1] * ly)


def in_quad(p, q):
    """Point in a convex quad (4 corners in order)."""
    sign = 0
    for k in range(4):
        a, b = q[k], q[(k + 1) % 4]
        cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if cr != 0:
            if sign == 0:
                sign = 1 if cr > 0 else -1
            elif (cr > 0) != (sign > 0):
                return False
    return True


def trailer_point(ball, theta, dist, lateral=0.0):
    """Point 'dist' behind the ball along the trailer axis (heading theta), 'lateral' to the right."""
    f, r = fwd(theta), right(theta)
    return (ball[0] - f[0] * dist + r[0] * lateral, ball[1] - f[1] * dist + r[1] * lateral)


def line(ball, theta, dist, half=P.O.width / 2.0):
    return trailer_point(ball, theta, dist, -half), trailer_point(ball, theta, dist, half)


# ---------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------
def simulate():
    bare = bare_cells()
    timing = VC.timing()
    t_on, t_off = timing["t_on_s"], timing["t_off_s"]


    min_cells = max(1, int(round(P.O.bare_threshold * P.O.width / CELL)))
    trailer = OC.trailer(True)
    seen, seeded, rolled = set(), set(), set()
    seeded_on_bare_now = set()
    band = []                   # roll swept quads (rolled lawn)
    states = []
    prof = speed_profile()
    c0, psi0, _, _ = robot_pose(0.0)
    ball = local_to_world(c0, psi0, P.C.ball[0], P.C.ball[1])
    theta = psi0
    cmd_hist = []               # (t, command)
    flow = False
    motor = False
    swept = 0.0                 # mm2 of ground under falling seed
    seed_g = 0.0
    spin = {tag: 0.0 for tag in ("FL", "FR", "RL", "RR")}
    wheel_prev = None
    roll_angle = meter_angle = 0.0
    prev_drop = prev_roll = None
    on_time = 0.0
    for t, s, v in prof:
        c, psi, k, steer = robot_pose(s)
        new_ball = local_to_world(c, psi, P.C.ball[0], P.C.ball[1])
        # trailer: the roll follows the ball (pursuit at fixed distance)
        tail = trailer_point(ball, theta, P.L_roll)
        dx, dy = new_ball[0] - tail[0], new_ball[1] - tail[1]
        theta = math.atan2(-dx, dy)
        ball = new_ball
        drop = line(ball, theta, P.L_drop)
        roll = line(ball, theta, P.L_roll)
        roll_mid = trailer_point(ball, theta, P.L_roll)
        # camera: analysed strip (trailer frame) -> bare cells seen
        cam = [trailer_point(ball, theta, P.L_cam[0], -P.O.width / 2.0),
               trailer_point(ball, theta, P.L_cam[0], P.O.width / 2.0),
               trailer_point(ball, theta, P.L_cam[1], P.O.width / 2.0),
               trailer_point(ball, theta, P.L_cam[1], -P.O.width / 2.0)]
        for cell in bare:
            if cell not in seen and in_quad(centre(cell), cam):
                seen.add(cell)
        # controller: bare cells (known) in the window [lead_off, lead_on] ahead of the drop line
        lead_on = v * t_on + P.O.on_margin
        lead_off = v * t_off - P.O.off_margin
        win = [trailer_point(ball, theta, P.L_drop - lead_off, -P.O.width / 2.0 - CELL / 2.0),
               trailer_point(ball, theta, P.L_drop - lead_off, P.O.width / 2.0 + CELL / 2.0),
               trailer_point(ball, theta, P.L_drop - lead_on, P.O.width / 2.0 + CELL / 2.0),
               trailer_point(ball, theta, P.L_drop - lead_on, -P.O.width / 2.0 - CELL / 2.0)]
        ahead = sum(1 for cell in seen if cell not in seeded and in_quad(centre(cell), win))
        command = ahead >= min_cells
        cmd_hist.append((t, command))

        def cmd_at(tt):
            val = False
            for th, cv in cmd_hist:
                if th <= tt + 1e-9:
                    val = cv
                else:
                    break
            return val
        if len(cmd_hist) > 200:
            cmd_hist = cmd_hist[-200:]
        motor = cmd_at(t - P.O.motor_start) if not motor else cmd_at(t - P.O.motor_stop)
        if not flow and cmd_at(t - t_on):
            flow = True
        elif flow and not cmd_at(t - t_off):
            flow = False
        # seed on the ground: the swept quad of the drop line while seed falls
        if prev_drop is not None:
            q = [prev_drop[0], prev_drop[1], drop[1], drop[0]]
            if flow:
                ds = math.hypot((drop[0][0] + drop[1][0] - prev_drop[0][0] - prev_drop[1][0]) / 2.0,
                                (drop[0][1] + drop[1][1] - prev_drop[0][1] - prev_drop[1][1]) / 2.0)
                swept += ds * P.O.width
                seed_g += ds * P.O.width / 1e6 * P.O.seed_rate
                on_time += DT
                for cell in bare:
                    if cell not in seeded and in_quad(centre(cell), q):
                        seeded.add(cell)
            qr = [prev_roll[0], prev_roll[1], roll[1], roll[0]]
            band.append(qr)
            for cell in bare:
                if cell not in rolled and in_quad(centre(cell), qr):
                    rolled.add(cell)
            roll_angle += math.hypot(roll_mid[0] - prev_mid[0], roll_mid[1] - prev_mid[1]) / (P.C.ring_od / 2.0)
        if motor:
            meter_angle += VC.rpm_for(max(v, 50.0) / 1000.0) / 60.0 * 2 * math.pi * DT
        # wheel spin of the robot (distance of each wheel along its own path)
        wheels = {tag: local_to_world(c, psi, sx * P.C.robot_wheel_x, sy * P.C.robot_wheelbase / 2.0)
                  for tag, sx, sy in (("FL", -1, 1), ("FR", 1, 1), ("RL", -1, -1), ("RR", 1, -1))}
        if wheel_prev is not None:
            for tag in spin:
                spin[tag] += math.hypot(wheels[tag][0] - wheel_prev[tag][0], wheels[tag][1] - wheel_prev[tag][1]) / (
                    P.C.robot_tire_d / 2.0)
        wheel_prev = wheels
        prev_drop, prev_roll, prev_mid = drop, roll, roll_mid
        art = math.degrees((theta - psi + math.pi) % (2 * math.pi) - math.pi)

        states.append({"t": t, "s": s, "v": v, "centre": c, "psi": psi, "steer": steer, "theta": theta,
                       "articulation": art, "ball": ball, "drop": drop, "roll": roll, "cam": cam, "window": win,
                       "command": command, "motor": motor, "flow": flow, "ahead": ahead,
                       "seen": len(seen), "seeded_set": frozenset(seeded), "rolled_set": frozenset(rolled),
                       "band_n": len(band), "spin": dict(spin), "roll_angle": roll_angle,
                       "meter_angle": meter_angle, "swept_mm2": swept, "seed_g": seed_g, "on_time": on_time,
                       "bare_n": len(bare), "draft_N": draft_now(trailer, roll, bare)})
    return {"states": states, "bare": bare, "band": band}


def draft_now(tr, roll, bare):
    """Draft of the roll: moist lawn, or loose seedbed for the share of the roll line on bare soil."""
    a, b = roll
    n = 20
    on_bare = 0
    for k in range(n):
        f = (k + 0.5) / n
        p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        if (int(p[0] // CELL), int(p[1] // CELL)) in bare:
            on_bare += 1
    share = on_bare / float(n)

    lawn = CC.draft(tr["mass_kg"], tr["ball_N"], "moist lawn")
    soil = CC.draft(tr["mass_kg"], tr["ball_N"], "loose seedbed (bare patch)")
    return lawn + (soil - lawn) * share


def stats(state, bare_n=None):
    """Coverage and waste at a state."""
    n = bare_n or state["bare_n"]
    noise = len(NOISE_CELLS)
    patch_n = n - noise
    seeded = state["seeded_set"]
    seeded_bare_area = len(seeded) * CELL * CELL
    waste = 1.0 - seeded_bare_area / state["swept_mm2"] if state["swept_mm2"] > 0 else 0.0
    return {"bare_m2": round(patch_n * CELL * CELL / 1e6, 2), "seeded_pct": round(100.0 * len(seeded) / patch_n, 1),
            "rolled_pct": round(100.0 * len(state["rolled_set"]) / n, 1), "seed_g": round(state["seed_g"], 1),
            "seeded_area_m2": round(state["swept_mm2"] / 1e6, 2), "on_green_pct": round(100.0 * max(0.0, waste), 1),
            "on_time_s": round(state["on_time"], 1)}
