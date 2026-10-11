"""Kinematics and dynamics of the swing arm going around a fence post (pure Python, no FreeCAD needed).

The robot drives at constant speed along the fence. In robot coordinates a post moves backwards (-y) along the post
line x = POST_X. The guard ring of the head (circle, radius R_GUARD) may not overlap the post (circle, radius
R_POST). Each time step (1 ms):
  1. free motion of the arm: I psi'' = M_grass - M_spring(psi) - c psi'   (psi = swing angle, + = backwards);
  2. end stops (rest, max);
  3. if the guard now overlaps the post, the arm is pushed to the smallest psi without overlap: the post supplies
     the torque M_post = I (omega_new - omega_free) / dt, from which the normal force follows (with friction mu).

Use:  import apm_kin; run = apm_kin.simulate(posts=[1500.0]); apm_kin.peak(run)
"""
import math

import apm_params as P

# rotating mass of the swing group about the post axis, from the FreeCAD model (build_apm.mass_properties)
MODEL = {"I_swing": 6.5, "swing_kg": 31.4}     # kg m2, kg (sleeve, arm, motor, spindle, head)

R_GUARD = P.guard_d / 2.0
R_POST = P.fence_post_d / 2.0
R_STRING = P.string_r[1]


def spring(psi):
    """Spring length (hook to hook, mm), force (N) and return torque (Nm, + = towards the rest stop) at psi (deg)."""
    tx, ty = P.lever_tip(psi)
    ax, ay = P.anchor_point()
    dx, dy = ax - tx, ay - ty
    length = math.hypot(dx, dy)
    force = P.spring_F0 + P.spring_k * max(0.0, length - P.spring_free)
    rx, ry = tx - P.pivot[0], ty - P.pivot[1]
    torque = (rx * dy - ry * dx) / length * force / 1000.0      # z component, CCW = towards rest
    return {"length": length, "F": force, "M": torque, "stretch": length - P.spring_free}


def grass_torque(psi, drag=P.grass_drag):
    """Torque (Nm, + = backwards) of the grass drag on the head (force -y at the head centre)."""
    hx, _ = P.head_centre(psi)
    return drag * (hx - P.pivot[0]) / 1000.0


def gap(psi, post):
    """Clearance (mm) between the guard ring and the post, post = (x, y) in robot coordinates."""
    hx, hy = P.head_centre(psi)
    return math.hypot(hx - post[0], hy - post[1]) - (R_GUARD + R_POST)


def resolve(psi, post):
    """Smallest psi >= psi without overlap with the post (None if even psi_max overlaps)."""
    if gap(psi, post) >= 0.0:
        return psi
    lo, hi = psi, psi
    step = 0.5
    while gap(hi, post) < 0.0:
        lo = hi
        hi += step
        if hi > P.psi_max:
            return None
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if gap(mid, post) < 0.0:
            lo = mid
        else:
            hi = mid
    return hi


def unit_torque(psi, post, omega, v_robot):
    """Torque about the pivot (Nm, + = backwards) of a unit normal force (1 N) of the post on the guard, with
    friction mu against the sliding direction. Returns (torque per N, contact point)."""
    hx, hy = P.head_centre(psi)
    nx, ny = hx - post[0], hy - post[1]
    d = math.hypot(nx, ny)
    nx, ny = nx / d, ny / d                                   # from the post to the head
    cx, cy = post[0] + nx * R_POST, post[1] + ny * R_POST       # contact point
    rx, ry = cx - P.pivot[0], cy - P.pivot[1]
    w = -math.radians(omega)                                   # rad/s about +z (psi + = clockwise)
    vgx, vgy = -w * ry / 1000.0, w * rx / 1000.0               # m/s of the guard point
    vrx, vry = vgx - 0.0, vgy + v_robot                        # relative to the post (post moves -v in y)
    tx, ty = -ny, nx
    s = vrx * tx + vry * ty
    fx, fy = nx, ny
    if abs(s) > 1e-6:
        sign = -1.0 if s > 0 else 1.0
        fx += sign * P.mu_guard * tx
        fy += sign * P.mu_guard * ty
    mz = (rx * fy - ry * fx) / 1000.0                          # CCW
    return -mz, (cx, cy)


def simulate(posts=(1500.0,), y_end=None, v=P.drive_speed, dt=0.001, drag=P.grass_drag, inertia=None,
             damping=P.damping, out_dt=0.02, y_start=0.0):
    """Robot drives from y_start to y_end (mm, robot origin) at v (m/s) along posts at world y 'posts' (x = POST_X).
    Returns a list of samples every out_dt seconds: t, y (robot), psi, omega, M_spring, N (normal force), F (total
    post force), contact (post index or None), head (x, y) in world."""
    inertia = MODEL["I_swing"] if inertia is None else inertia
    if y_end is None:
        y_end = max(posts) + 2000.0
    psi, omega = P.psi_rest, 0.0
    t, y = 0.0, y_start
    out = []
    next_out = 0.0
    n_filt = 0.0
    hit_max = False
    while y <= y_end:
        sp = spring(psi)["M"]
        alpha = math.degrees((grass_torque(psi, drag) - sp - damping * math.radians(omega)) / inertia)
        omega_f = omega + alpha * dt
        psi_f = psi + omega_f * dt
        if psi_f <= P.psi_rest:
            psi_f, omega_f = P.psi_rest, max(0.0, omega_f)
        y_new = y + v * 1000.0 * dt
        contact, n_force = None, 0.0
        psi_new, omega_new = psi_f, omega_f
        for i, yp in enumerate(posts):
            post = (P.POST_X, yp - y_new)
            if abs(post[1] - P.head_centre(psi_f)[1]) > 900.0:
                continue
            res = resolve(psi_f, post)
            if res is None:
                res, hit_max = P.psi_max, True
            if res > psi_f + 1e-9:
                psi_new = res
                omega_new = (res - psi) / dt
                m_post = inertia * math.radians(omega_new - omega_f) / dt
                ut, _ = unit_torque(res, post, omega_new, v)
                n_force = m_post / ut if ut > 1e-6 else 0.0
                contact = i
        if psi_new >= P.psi_max:
            psi_new, omega_new, hit_max = P.psi_max, min(0.0, omega_new), True
        psi, omega = psi_new, omega_new
        n_filt += (n_force - n_filt) * min(1.0, dt / 0.03)          # 30 ms filter (the PE and the post give a bit)
        t += dt
        y = y_new
        if t >= next_out - 1e-9:
            next_out += out_dt
            hx, hy = P.head_centre(psi)
            out.append({"t": t, "y": y, "psi": psi, "omega": omega, "M_spring": spring(psi)["M"],
                        "N": max(0.0, n_filt), "F": max(0.0, n_filt) * math.hypot(1.0, P.mu_guard),
                        "contact": contact, "head": (hx, hy + y), "hit_max": hit_max})
    return out


def peak(run):
    """Key figures of a run."""
    psi_max = max(s["psi"] for s in run)
    f_max = max(s["F"] for s in run)
    return {"psi_max_deg": round(psi_max, 1), "swing_deg": round(psi_max - P.psi_rest, 1), "F_post_max_N": round(f_max),
            "hit_max_stop": any(s["hit_max"] for s in run)}


def missed_area(v=P.drive_speed, cell=10.0, strip=(None, None)):
    """Uncut area (cm2) around one post: points of the strip x0..x1 (default: string reach at rest, minus 20 mm) that
    no string ever passes over, except the post itself. Also returns the strip and the length behind the post that
    stays uncut on the post line side."""
    yp = 2000.0
    run = simulate(posts=(yp,), y_start=0.0, y_end=yp + 2500.0, v=v, out_dt=0.005)
    hx0 = P.HEAD_REST[0]
    x0 = hx0 - R_STRING + 20.0 if strip[0] is None else strip[0]
    x1 = hx0 + R_STRING - 20.0 if strip[1] is None else strip[1]
    ys = [yp - 800.0 + cell * i for i in range(int(1600.0 / cell))]
    xs = [x0 + cell * i for i in range(int((x1 - x0) / cell) + 1)]
    heads = [s["head"] for s in run]
    missed = 0
    worst_behind = 0.0
    for x in xs:
        for yy in ys:
            if math.hypot(x - P.POST_X, yy - yp) <= R_POST:
                continue
            hit = False
            for hx, hy in heads:
                if (hx - x) ** 2 + (hy - yy) ** 2 <= R_STRING ** 2:
                    hit = True
                    break
            if not hit:
                missed += 1
                if yy < yp:
                    worst_behind = max(worst_behind, yp - yy)
    return {"missed_cm2": round(missed * cell * cell / 100.0), "strip_x": (round(x0), round(x1)),
            "behind_mm": round(worst_behind)}
