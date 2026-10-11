"""Animation: the mobile refiller tops up the working robot in the straight part of its headland turn.

The working robot (standard Bruut with the liquid fertilizer applicator advanced and the receiver kit) finishes a
pass, lifts the applicator and turns with three points (forward arc right, straight reverse along the headland,
forward arc right into the next pass), as in "agbot slim". The refiller waits on the headland beside the straight,
on the outside of the turn. It already swings its boom out over the place where the funnel will stop (the head stays
~100 mm above the funnel). When the working robot stops: camera check, spout down, pump on. Both robots then drive
along the headland side by side (the boom follows the funnel; the refiller lags its set point a little when the
working robot accelerates); the pump stops when the work tank is full (level sensor), the spout goes up and the boom
swings back. The working robot turns into its next pass and lowers the applicator; the refiller reverses with its
trailer to the place of the next turn on this headland (two passes further).

Builds a separate document (the robot files in "agbot design" and the applicator are not changed).

Use in FreeCAD:
    import animate_mrl
    animate_mrl.build()                              # build the document
    animate_mrl.play()                               # play live, animate_mrl.stop()
    animate_mrl.summary()                            # key figures of the run
    animate_mrl.check_fit()                          # overlap refiller - working robot in the docked frames
    animate_mrl.render_all(r"C:\\temp\\mrl_frames")
    import make_gif_mrl; make_gif_mrl.main(r"C:\\temp\\mrl_frames", r"previews\\animation_refill_in_turn.gif")
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrl_params as P
import mrl_calc as C
import mrl_parts as G
import build_mrl as B

DOC_NAME = "Mobile_refiller_animation"

# ---------------------------------------------------------------------
# Field and plan (mm, mm/s). y = 0 is the field edge, headland at y > 0. Rear-axle centre of the working robot.
# ---------------------------------------------------------------------
W = C.WORK_WIDTH                    # 1000: passes are W apart
R = C.R_TURN                        # 2400
X_A, X_B, X_PREV = 0.0, W, -W
Y_TURN = 1800.0                     # start of the first arc
YS = Y_TURN + R                     # the headland straight
Y_START = -1900.0
Y_STOP = -1500.0
FIELD_START = -15000.0
FENCE_Y = YS + P.dock_d + P.robot_half_width + 1000.0
V_WORK, V_HEAD, V_REV = 1000.0 * C.V_WORK, 1000.0 * C.V_HEAD, 1000.0 * C.V_REV
ACCEL = 1000.0 * C.ACCEL
STEER_RATE = 35.0                   # deg/s
ARC_STEER = -math.degrees(math.atan(P.robot_wheelbase / R))     # middle angle on the arcs (right turn)
ACT_SPEED = 60.0                    # applicator lift
LIFT = 140.0
RAISE_Y = -500.0                    # lifting starts when the knives are here (0.5 m before the edge)
LOWER_Y = 900.0                     # lowering starts when the knives (behind the robot) are here on the way back
KNIFE_DEPTH = 35.0

# refiller
V_R, A_R = 1000.0 * P.v_drive, 500.0
V_R_REV, A_R_REV = 700.0, 350.0     # reversing with the trailer (powered trailer wheels keep it straight)
APPROACH = 3500.0                   # the refiller starts this far along the headland
WOBBLE = 12.0                       # mm, lateral wander of the refiller while following

# liquid: the working robot used 2 passes since the last visit on this headland
DOSE = 550.0                        # l/ha
FIELD_LEN = 200.0                   # m
RX_FULL = 145.0                     # l, level sensor stops the pump here (work tank 147 l)
RX_START = RX_FULL - C.per_round_l(DOSE, FIELD_LEN)
MR_START = 0.85 * C.capacity_l("refiller")
TR_START = 0.95 * C.capacity_l("trailer")
Q_FILL = C.fill_rate_ls()           # l/s

FPS = 5                             # frames per second of real time; the GIF plays at 10 fps = 2 x speed
DT = 0.02
HOLD_END = 2.5

COLOR = {"field": (0.45, 0.62, 0.30), "headland": (0.56, 0.68, 0.40), "edge": (0.97, 0.97, 0.95),
         "slot": (0.22, 0.14, 0.08), "post": (0.45, 0.33, 0.20), "wire": (0.75, 0.75, 0.75),
         "stream": (0.15, 0.50, 0.80)}
SLOT_HALF = 6.0

_timer = None
_play = {}
_cache = {"act": {}, "strut": {}, "hose": {}}
_doc = {}


# ---------------------------------------------------------------------
# Paths of the working robot (rear-axle centre)
# ---------------------------------------------------------------------
def _line(p0, p1, step=10.0):
    n = max(1, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / step))
    return [(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n) for i in range(n + 1)]


def _arc(c, r, a0, a1, step=10.0):
    n = max(1, int(abs(math.radians(a1 - a0)) * r / step))
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


class Path:
    def __init__(self, pieces, direction):
        """pieces: [(points, steer_deg, v_cap)], direction +1 forward, -1 reverse."""
        self.pts, self.steer, self.cap, self.starts = [], [], [], []
        for pts, steer, cap in pieces:
            if self.pts:
                pts = pts[1:]
            self.starts.append(len(self.pts))
            for p in pts:
                self.pts.append(p)
                self.steer.append(steer)
                self.cap.append(cap)
        self.cum = [0.0]
        for p, q in zip(self.pts[:-1], self.pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
        self.length = self.cum[-1]
        self.dir = direction
        self.piece_s = [self.cum[i] for i in self.starts]
        self.piece_cap = [pieces[k][2] for k in range(len(pieces))]

    def index(self, s):
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        return lo

    def pose(self, s):
        s = max(0.0, min(self.length, s))
        i = min(self.index(s), len(self.pts) - 2)
        (x0, y0), (x1, y1) = self.pts[i], self.pts[i + 1]
        seg = self.cum[i + 1] - self.cum[i] or 1.0
        f = (s - self.cum[i]) / seg
        tx, ty = (x1 - x0) / seg, (y1 - y0) / seg
        psi = math.degrees(math.atan2(-tx, ty)) + (180.0 if self.dir < 0 else 0.0)
        return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, psi

    def steer_at(self, s):
        return self.steer[min(self.index(max(0.0, min(self.length, s))), len(self.steer) - 1)]

    def v_allowed(self, s, a):
        v = math.sqrt(max(0.0, 2.0 * a * (self.length - s)))
        for s0, cap in zip(self.piece_s, self.piece_cap):
            if s0 > s:
                v = min(v, math.sqrt(cap * cap + 2.0 * a * (s0 - s)))
            elif s >= s0:
                cur = cap
        return min(v, cur)


def paths():
    m1 = Path([(_line((X_A, Y_START), (X_A, Y_TURN)), 0.0, V_WORK),
               (_arc((X_A + R, Y_TURN), R, 180.0, 90.0), ARC_STEER, V_HEAD)], 1)
    m2 = Path([(_line((X_A + R, YS), (X_B - R, YS)), 0.0, V_REV)], -1)
    m3 = Path([(_arc((X_B - R, Y_TURN), R, 90.0, 0.0), ARC_STEER, V_HEAD),
               (_line((X_B, Y_TURN), (X_B, Y_STOP)), 0.0, V_WORK)], 1)
    return m1, m2, m3


# ---------------------------------------------------------------------
# Kinematics helpers
# ---------------------------------------------------------------------
def heading(psi):
    a = math.radians(psi)
    return -math.sin(a), math.cos(a)


def to_world(rear, psi, local):
    """Local robot point (x, y relative to the robot centre) -> world, given the rear-axle centre and heading."""
    hx, hy = heading(psi)
    rx, ry = hy, -hx                    # right
    cx, cy = rear[0] + P.robot_axle_y * hx, rear[1] + P.robot_axle_y * hy
    return cx + local[0] * rx + local[1] * hx, cy + local[0] * ry + local[1] * hy


def wheel_angles(delta):
    length, half = P.robot_wheelbase, P.robot_wheel_x
    t = math.tan(math.radians(delta))
    return (math.degrees(math.atan2(length * t, length - half * t)),
            math.degrees(math.atan2(length * t, length + half * t)))


WHEELS = {"RL": (-P.robot_wheel_x, -P.robot_axle_y), "RR": (P.robot_wheel_x, -P.robot_axle_y),
          "FL": (-P.robot_wheel_x, P.robot_axle_y), "FR": (P.robot_wheel_x, P.robot_axle_y)}


def approach(cur, target, rate, dt):
    d = target - cur
    step = rate * dt
    return target if abs(d) <= step else cur + math.copysign(step, d)


def profile(d, v, a, t):
    """Position along a trapezoid move of length d (sign kept) at time t (as mrk animation)."""
    s = abs(d)
    if s == 0.0:
        return 0.0
    d_acc = v * v / a
    if s <= d_acc:
        tm = math.sqrt(s / a)
        x = 0.5 * a * t * t if t <= tm else s - 0.5 * a * max(0.0, 2 * tm - t) ** 2
    else:
        ta, tc = v / a, (s - d_acc) / v
        if t <= ta:
            x = 0.5 * a * t * t
        elif t <= ta + tc:
            x = 0.5 * v * ta + v * (t - ta)
        else:
            x = s - 0.5 * a * max(0.0, 2 * ta + tc - t) ** 2
    return math.copysign(min(s, x), d)


def move_time(d, v, a):
    return C.profile_time(abs(d) / 1000.0, v / 1000.0, a / 1000.0) if d else 0.0


def refiller_placement(xr, yr):
    return App.Placement(V(xr, yr, 0.0), App.Rotation(V(0, 0, 1), 90.0))


def worker_placement(rear, psi):
    hx, hy = heading(psi)
    return App.Placement(V(rear[0] + P.robot_axle_y * hx, rear[1] + P.robot_axle_y * hy, 0.0),
                         App.Rotation(V(0, 0, 1), psi))


def funnel_world(rear, psi):
    return to_world(rear, psi, P.funnel_xy)


def boom_target(xr, yr, fw):
    """Slew angle and trolley radius for the spout above world point fw, refiller at (xr, yr)."""
    p = refiller_placement(xr, yr).inverse().multVec(V(fw[0], fw[1], 0.0))
    return B.ik(p.x, p.y)


def unwrap(phi, ref):
    while phi - ref > 180.0:
        phi -= 360.0
    while phi - ref < -180.0:
        phi += 360.0
    return phi


# ---------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------
def simulate():
    m1, m2, m3 = paths()
    moves = {"m1": m1, "m2": m2, "m3": m3}
    LP = B.load_lfa().P
    knife_dy = LP.robot_mount_y + LP.disc_y + LP.knife_tip_rel[0]
    fw_stop = funnel_world((X_A + R, YS), -90.0)        # funnel where the working robot stops after the arc
    x_dock = fw_stop[0] + G.CY                          # column (local y -500) is at world x = xr + 500
    yr0 = YS + P.dock_d
    xr_next = x_dock + 2.0 * W

    w = {"state": "work", "move": "m1", "s": 0.0, "v": V_WORK, "steer": 0.0, "lift": 0.0, "level": RX_START,
         "a": 0.0}
    r = {"state": "approach", "x": x_dock + APPROACH, "y": yr0, "t0": 0.0, "phi": P.phi_park, "rr": P.r_park,
         "s": 0.0, "v": 0.0, "level": MR_START, "trailer": TR_START, "pump": 0.0, "lag": 0.0, "from": None}
    spin_w = {k: 0.0 for k in WHEELS}
    spin_r = 0.0
    prev_wheels = None
    slots_a_end = None
    slots_b_start = None
    t = 0.0
    frames = []
    next_frame = 0.0
    dock_x0 = None
    events = {}
    while True:
        # ---------------- working robot ----------------
        path = moves[w["move"]] if w["move"] else None
        rear_prev = path.pose(w["s"]) if path else None
        if w["state"] in ("work", "reverse", "arc_b"):
            vmax = path.v_allowed(w["s"], ACCEL)
            v_new = min(w["v"] + ACCEL * DT, vmax)
            w["a"] = (v_new - w["v"]) / DT
            w["v"] = v_new
            w["s"] += w["v"] * DT
            look = w["s"] + 0.35 * w["v"]
            w["steer"] = approach(w["steer"], path.steer_at(look), STEER_RATE, DT)
            if w["s"] >= path.length - 0.5 or (w["v"] < 1.0 and path.length - w["s"] < 5.0 and t > 1.0):
                w["s"] = path.length
                w["v"] = 0.0
                w["a"] = 0.0
                if w["state"] == "work":
                    w["state"] = "stop1"
                    events["stop1"] = t
                elif w["state"] == "reverse":
                    w["state"] = "stop2"
                    events["stop2"] = t
                else:
                    w["state"] = "done"
                    events["done"] = t
        elif w["state"] == "stop1":
            w["a"] = 0.0
            w["steer"] = approach(w["steer"], 0.0, STEER_RATE, DT)
            if r["state"] == "pumping" and abs(w["steer"]) < 0.1:
                w["state"], w["move"], w["s"], w["v"] = "reverse", "m2", 0.0, 0.0
                events["reverse"] = t
        elif w["state"] == "stop2":
            w["a"] = 0.0
            w["steer"] = approach(w["steer"], ARC_STEER, STEER_RATE, DT)
            if r["s"] < 0.5 and r["state"] not in ("pumping", "spout_down", "camera") and \
                    abs(w["steer"] - ARC_STEER) < 0.1:
                w["state"], w["move"], w["s"], w["v"] = "arc_b", "m3", 0.0, 0.0
                events["arc_b"] = t
        elif w["state"] == "done":
            w["a"] = 0.0
        path = moves[w["move"]]
        rx_, ry_, psi = path.pose(w["s"])
        rear = (rx_, ry_)
        # applicator: lift and lower by knife position
        knife = to_world(rear, psi, (0.0, knife_dy))
        if w["move"] == "m1":
            target = LIFT if knife[1] >= RAISE_Y else 0.0
        elif w["move"] == "m3":
            target = 0.0 if (w["s"] > m3.piece_s[1] and knife[1] <= LOWER_Y) else LIFT
        else:
            target = LIFT
        w["lift"] = approach(w["lift"], target, ACT_SPEED, DT)
        in_soil = w["lift"] < KNIFE_DEPTH
        if w["move"] == "m1" and in_soil:
            slots_a_end = knife[1]
        if w["move"] == "m3" and in_soil:
            if slots_b_start is None:
                slots_b_start = knife[1]
                events["knives_in"] = t
        if w["move"] == "m1" and not in_soil and "knives_out" not in events:
            events["knives_out"] = t
        # consumption while working (pump on the applicator follows the speed)
        if in_soil and w["v"] > 0:
            w["level"] -= DOSE * 1e-4 * (W / 1000.0) * (w["v"] / 1000.0) * DT
        # wheels of the working robot
        wheels = {k: to_world(rear, psi, loc) for k, loc in WHEELS.items()}
        if prev_wheels is not None:
            sgn = path.dir if w["v"] > 0 else 0.0
            for k in WHEELS:
                spin_w[k] += sgn * math.hypot(wheels[k][0] - prev_wheels[k][0],
                                              wheels[k][1] - prev_wheels[k][1]) / (P.robot_tire_d / 2.0)
        prev_wheels = wheels
        fw = funnel_world(rear, psi)

        # ---------------- refiller ----------------
        x_old = r["x"]
        st = r["state"]
        tt = t - r["t0"]
        if st == "approach":
            d = -APPROACH
            r["x"] = x_dock + APPROACH + profile(d, V_R, A_R, tt)
            if tt >= move_time(d, V_R, A_R):
                r["x"] = x_dock
                r["state"], r["t0"] = "boom_out", t
                phi_t, r_t = boom_target(x_dock, yr0, fw_stop)
                r["from"] = (r["phi"], r["rr"], unwrap(phi_t, r["phi"]), r_t)
                events["parked"] = t
        elif st == "boom_out":
            p0, r0, p1, r1 = r["from"]
            r["phi"] = p0 + profile(p1 - p0, P.slew_rate, P.slew_acc, tt)
            r["rr"] = r0 + profile(r1 - r0, P.trolley_v, P.trolley_a, tt)
            if tt >= max(move_time(1000.0 * math.radians(p1 - p0), 1000.0 * math.radians(P.slew_rate),
                                   1000.0 * math.radians(P.slew_acc)),
                         move_time(r1 - r0, P.trolley_v, P.trolley_a)):
                r["phi"], r["rr"] = p1, r1
                r["state"], r["t0"] = "ready", t
                events["boom_ready"] = t
        elif st == "ready":
            if w["state"] == "stop1":
                r["state"], r["t0"] = "camera", t
                events["camera"] = t
        elif st == "camera":
            if tt >= 0.5:
                r["state"], r["t0"] = "spout_down", t
        elif st == "spout_down":
            r["s"] = profile(P.spout_stroke, P.spout_v_speed, 400.0, tt)
            if tt >= move_time(P.spout_stroke, P.spout_v_speed, 400.0):
                r["s"] = P.spout_stroke
                r["state"], r["t0"] = "pumping", t
                events["pump_on"] = t
                dock_x0 = rear[0]
        elif st in ("pumping", "spout_up", "boom_back"):
            pass
        if st in ("pumping", "spout_up", "boom_back", "follow"):
            if w["state"] in ("reverse", "stop1"):
                r["lag"] = P.dock_lag * w["a"]          # lags behind (+x) when the working robot speeds up
                r["x"] = x_dock + (rear[0] - dock_x0) + r["lag"]
                r["y"] = yr0 + WOBBLE * math.sin(2.0 * math.pi * (t - events.get("pump_on", 0.0)) / 3.7) * \
                    min(1.0, abs(w["v"]) / 200.0)
            else:
                r["lag"] = 0.0
        if r["state"] == "pumping":
            q = Q_FILL
            r["pump"] = q
            w["level"] += q * DT
            r["level"] -= q * DT
            phi_t, r_t = boom_target(r["x"], r["y"], fw)
            r["phi"], r["rr"] = unwrap(phi_t, r["phi"]), r_t
            if w["level"] >= RX_FULL:
                w["level"] = RX_FULL
                r["pump"] = 0.0
                r["state"], r["t0"] = "spout_up", t
                events["full"] = t
        elif r["state"] == "spout_up":
            r["pump"] = 0.0
            phi_t, r_t = boom_target(r["x"], r["y"], fw)
            r["phi"], r["rr"] = unwrap(phi_t, r["phi"]), r_t
            r["s"] = P.spout_stroke - profile(P.spout_stroke, P.spout_v_speed, 400.0, t - r["t0"])
            if t - r["t0"] >= move_time(P.spout_stroke, P.spout_v_speed, 400.0):
                r["s"] = 0.0
                r["state"], r["t0"] = "boom_back", t
                r["from"] = (r["phi"], r["rr"], unwrap(P.phi_park, r["phi"]), P.r_park)
                events["spout_up"] = t
        elif r["state"] == "boom_back":
            p0, r0, p1, r1 = r["from"]
            tt = t - r["t0"]
            r["phi"] = p0 + profile(p1 - p0, P.slew_rate, P.slew_acc, tt)
            r["rr"] = r0 + profile(r1 - r0, P.trolley_v, P.trolley_a, tt)
            done = tt >= max(move_time(1000.0 * math.radians(p1 - p0), 1000.0 * math.radians(P.slew_rate),
                                       1000.0 * math.radians(P.slew_acc)), move_time(r1 - r0, P.trolley_v, P.trolley_a))
            if done:
                r["phi"], r["rr"] = p1, r1
                r["state"], r["t0"] = "follow", t
                events["boom_parked"] = t
        if r["state"] == "follow" and w["state"] in ("stop2", "arc_b", "done"):
            r["state"], r["t0"] = "stopped", t
            r["x0"] = r["x"]
            r["y"] = yr0
        if r["state"] == "stopped" and w["state"] in ("arc_b", "done") and t - r["t0"] > 0.8:
            r["state"], r["t0"] = "reposition", t
            r["x0"] = r["x"]
            events["reposition"] = t
        if r["state"] == "reposition":
            d = xr_next - r["x0"]
            r["x"] = r["x0"] + profile(d, V_R_REV, A_R_REV, t - r["t0"])
            if t - r["t0"] >= move_time(d, V_R_REV, A_R_REV):
                r["x"] = xr_next
                r["state"], r["t0"] = "waiting", t
                events["next_spot"] = t
        dx_r = r["x"] - x_old
        r["v"] = -dx_r / DT                                   # + = forward (the refiller heads -x)
        spin_r += -dx_r / (P.robot_tire_d / 2.0)

        # ---------------- frame ----------------
        if t >= next_frame - 1e-9:
            frames.append({
                "t": t, "w_state": w["state"], "r_state": r["state"], "rear": rear, "psi": psi,
                "steer": w["steer"], "spin_w": dict(spin_w), "lift": w["lift"], "v_w": w["v"] * path.dir,
                "rx_level": w["level"], "r_pose": (r["x"], r["y"]), "spin_r": spin_r, "v_r": r["v"],
                "boom": (r["phi"], r["rr"], r["s"]), "mr_level": r["level"], "tr_level": r["trailer"],
                "pump": r["pump"], "lag": r["lag"], "funnel": fw, "knife": knife,
                "slots_a": slots_a_end, "slots_b": (slots_b_start, knife[1]) if slots_b_start is not None else None,
                "spout_err": spout_error(r, fw)})
            next_frame += 1.0 / FPS
        t += DT
        end = events.get("done")
        if end is not None and r["state"] in ("waiting",) and t > end + HOLD_END and \
                t > events.get("next_spot", 0.0) + HOLD_END:
            break
        if t > 120.0:
            raise RuntimeError("animation did not finish: %s / %s" % (w["state"], r["state"]))
    return frames, events


def spout_error(r, fw):
    """Horizontal distance spout axis - funnel axis (mm), 0 when the boom follows exactly."""
    pl = refiller_placement(r["x"], r["y"])
    phi = math.radians(r["phi"])
    u, v = P.spout_u, r["rr"]
    lx = G.CX + u * math.cos(phi) - v * math.sin(phi)
    ly = G.CY + u * math.sin(phi) + v * math.cos(phi)
    p = pl.multVec(V(lx, ly, 0.0))
    return math.hypot(p.x - fw[0], p.y - fw[1])


_sim = {}


def prepare(fps=FPS):
    global FPS
    if fps != FPS or "frames" not in _sim:
        FPS = fps
        _sim["frames"], _sim["events"] = simulate()
    return _sim["frames"]


# ---------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------
def ground_shapes():
    field = G.box_span((-6000.0, 12000.0), (FIELD_START, 0.0), (-40.0, 0.0))
    head = G.box_span((-6000.0, 12000.0), (0.0, FENCE_Y + 1500.0), (-40.0, 0.0))
    edge = G.box_span((-6000.0, 12000.0), (-25.0, 25.0), (0.0, 1.5))
    posts, wires = [], []
    x = -6000.0
    while x <= 12000.0:
        posts.append(G.cyl_z(100.0, 0.0, 1200.0, x, FENCE_Y))
        x += 2500.0
    for z in (500.0, 900.0, 1150.0):
        wires.append(G.cyl_x(8.0, -6000.0, 12000.0, FENCE_Y, z))
    return field, head, edge, Part.makeCompound(posts), Part.makeCompound(wires)


def slot_rows(x0, y0, y1):
    if y0 is None or y1 is None or abs(y1 - y0) < 5.0:
        return Part.Shape()
    lo, hi = sorted((y0, y1))
    return Part.makeCompound([G.box_span((x0 + rx - SLOT_HALF, x0 + rx + SLOT_HALF), (lo, hi), (0.0, 1.0))
                              for rx in (-400.0, -200.0, 0.0, 200.0, 400.0)])


def build():
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Mobile refiller - refill in the turn"
    doc.Comment = "Generated by animate_mrl.py (no need to save). Robots from agbot design, applicator advanced."
    worker, wobjs = B.build_robot(doc, "working_robot_with_applicator")
    BL = B.load_lfa()
    BL.build_into(doc, worker, 0.0, BL.translation(0.0, BL.P.robot_mount_y, 0.0))
    B.build_receiver_into(doc, worker, RX_START)
    robot, robjs = B.build_robot(doc, "refiller_robot")
    B.build_refiller_into(doc, robot, fill=MR_START / C.capacity_l("refiller"))
    B.set_levels(trailer=TR_START, doc=doc)
    for name, shape, color in zip(("anim_field", "anim_headland", "anim_edge", "anim_posts", "anim_wires"),
                                  ground_shapes(), ("field", "headland", "edge", "post", "wire")):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = COLOR[color]
        o.ViewObject.LineColor = COLOR[color]
    prev = doc.addObject("Part::Feature", "anim_slots_prev")
    prev.Shape = Part.makeCompound([slot_rows(X_PREV, FIELD_START, -60.0), slot_rows(X_A, FIELD_START, Y_START - 900.0)])
    for name in ("anim_slots_prev", "anim_slots_a", "anim_slots_b"):
        o = doc.getObject(name) or doc.addObject("Part::Feature", name)
        o.ViewObject.ShapeColor = COLOR["slot"]
        o.ViewObject.LineColor = COLOR["slot"]
    st = doc.addObject("Part::Feature", "anim_stream")
    st.ViewObject.ShapeColor = COLOR["stream"]
    doc.recompute()
    _doc.clear()
    _doc.update({"worker": worker, "w": wobjs, "robot": robot, "r": robjs, "BL": BL})
    for c in _cache.values():
        c.clear()
    return doc


def _lfa_shapes(lift):
    BL = _doc["BL"]
    key = round(lift)
    if key not in _cache["act"]:
        LP = BL.P
        disc_rel = (LP.disc_y - LP.u_pivot[0], LP.disc_z - LP.u_pivot[1])
        drop = BL.contact_drop(disc_rel, key, LP.unit_drop_deg)
        a, b = BL.actuator_points(key)
        body, rod = BL.G.actuator(b, a)
        strut = BL.G.u_strut(drop)
        hoses = [BL.G.outlet_hose(i, x, drop) for i, x in enumerate(LP.row_x)]
        beta = BL.press_beta(drop, BL.lift_state(key)[2]) if LP.press_wheel else 0.0
        _cache["act"][key] = (drop, body, rod, strut, hoses, beta)
    return _cache["act"][key]


def apply_lift(doc, lift):
    BL = _doc["BL"]
    LP = BL.P
    theta, dy, dz = BL.lift_state(lift)
    drop, body, rod, strut, hoses, beta = _lfa_shapes(lift)
    doc.getObject("Toolbar_assembly").Placement = BL.translation(0.0, dy, dz)
    for lv, z in (("upper", LP.pin_upper_z), ("lower", LP.pin_lower_z)):
        for sd in ("left", "right"):
            doc.getObject("link_%s_%s" % (lv, sd)).Placement = BL.rotation_x(-theta, (LP.pin_front_y, z))
    doc.getObject("act_body").Shape = body
    doc.getObject("act_rod").Shape = rod
    for i in range(len(LP.row_x)):
        n = i + 1
        doc.getObject("Unit_%d_arm" % n).Placement = BL.rotation_x(drop, LP.u_pivot)
        doc.getObject("U%d_strut_rod" % n).Shape = strut[0]
        doc.getObject("U%d_spring" % n).Shape = strut[1]
        doc.getObject("hose_%d" % n).Shape = hoses[i]
        if LP.press_wheel:
            doc.getObject("Unit_%d_press_arm" % n).Placement = BL.rotation_x(beta, LP.pw_pivot)


def apply_frame(doc, f):
    w, r = _doc["w"], _doc["r"]
    _doc["worker"].Placement = worker_placement(f["rear"], f["psi"])
    left, right = wheel_angles(f["steer"])
    w["FL_steered"].Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), left))
    w["FR_steered"].Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), right))
    for tag in ("RL", "RR", "FL", "FR"):
        rot = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -math.degrees(f["spin_w"][tag])))
        for part in ("tire", "rim", "hub"):
            w["%s_%s" % (tag, part)].Placement = rot
    apply_lift(doc, f["lift"])
    _doc["robot"].Placement = refiller_placement(*f["r_pose"])
    rot = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -math.degrees(f["spin_r"])))
    for tag in ("RL", "RR", "FL", "FR"):
        for part in ("tire", "rim", "hub"):
            r["%s_%s" % (tag, part)].Placement = rot
    for tag in ("TL", "TR"):
        for part in ("tire", "rim", "hub"):
            doc.getObject("tr_%s_%s" % (tag, part)).Placement = rot
    phi, rr, s = f["boom"]
    B.apply_pose(doc, phi, rr, s)
    B.set_levels(refiller=f["mr_level"], trailer=f["tr_level"], receiver=f["rx_level"], doc=doc)
    doc.getObject("anim_slots_a").Shape = slot_rows(X_A, Y_START - 900.0, f["slots_a"])
    doc.getObject("anim_slots_b").Shape = slot_rows(X_B, *f["slots_b"]) if f["slots_b"] else Part.Shape()
    if f["pump"] > 0:
        fx, fy = f["funnel"]
        doc.getObject("anim_stream").Shape = G.stream(fx, fy, P.SPOUT_TIP_DOWN, G.RX_TOP + P.funnel_neck)
    else:
        doc.getObject("anim_stream").Shape = Part.Shape()


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_WIDE = (0.32, -0.62, 0.72)       # direction from the target to the eye
CAM_CLOSE = (0.52, -0.62, 0.58)
CAM_END = (0.18, -0.45, 0.88)
DIST_CLOSE = 5600.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def camera_pose(f, frames):
    """Wide shot that keeps both robots in view, close-up of spout and funnel while docked, overview at the end."""
    ev = _sim["events"]
    t = f["t"]
    wx, wy = to_world(f["rear"], f["psi"], (0.0, -300.0))
    rx, ry = f["r_pose"]
    rx += 900.0                                         # refiller + trailer: centre of the train
    sep = math.hypot(rx - wx, ry - wy)
    wide_t = ((wx + rx) / 2.0, (wy + ry) / 2.0, 400.0)
    wide_d = max(7500.0, 1.05 * sep + 3800.0)
    fx, fy = f["funnel"]
    close_t = (fx - 200.0, fy + 600.0, 800.0)
    k = smooth((t - (ev["camera"] - 5.0)) / 3.5) * (1.0 - smooth((t - (ev["boom_parked"] - 0.5)) / 3.5))
    end = smooth((t - (frames[-1]["t"] - 7.0)) / 4.0)
    tgt = [wide_t[i] + (close_t[i] - wide_t[i]) * k for i in range(3)]
    d = [CAM_WIDE[i] + (CAM_CLOSE[i] - CAM_WIDE[i]) * k for i in range(3)]
    d = _unit([d[i] + (CAM_END[i] - d[i]) * end for i in range(3)])
    dist = wide_d + (DIST_CLOSE - wide_d) * k
    return [tgt[i] + d[i] * dist for i in range(3)], tgt


def track_camera(f, frames, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    eye, tgt = camera_pose(f, frames)
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(*eye))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(50.0)
    cam.farDistance.setValue(80000.0)


W_STATE = {"work": "working, lifts the applicator at the edge, arc onto the headland", "stop1": "stopped: wheels straight",
           "reverse": "reversing along the headland", "stop2": "stopped: steers for the arc",
           "arc_b": "arc into the next pass, lowers the applicator", "done": "working the next pass"}
R_STATE = {"approach": "drives to the next turn of the working robot", "boom_out": "boom out over the stop point",
           "ready": "waiting, spout above the stop point", "camera": "camera finds the funnel target",
           "spout_down": "spout down into the funnel", "pumping": "pumping, drives along, boom follows the funnel",
           "spout_up": "work tank full: spout up", "boom_back": "boom back to park", "follow": "drives along",
           "stopped": "stopped", "reposition": "reverses to the next turn (2 passes further)",
           "waiting": "waiting for the next turn"}


def meta(f):
    wx, wy = to_world(f["rear"], f["psi"], (0.0, 0.0))
    return {"t": round(f["t"], 2), "w_state": f["w_state"], "r_state": f["r_state"], "w_text": W_STATE[f["w_state"]],
            "r_text": R_STATE[f["r_state"]], "w_pos": [round(wx), round(wy), round(f["psi"], 1)],
            "r_pos": [round(f["r_pose"][0]), round(f["r_pose"][1])], "v_w": round(f["v_w"]), "v_r": round(f["v_r"]),
            "rx": round(f["rx_level"], 1), "rx_cap": round(C.capacity_l("receiver"), 1), "rx_full": RX_FULL,
            "mr": round(f["mr_level"], 1), "mr_cap": round(C.capacity_l("refiller"), 1),
            "tr": round(f["tr_level"], 1), "tr_cap": round(C.capacity_l("trailer"), 1),
            "pump_lpm": round(60.0 * f["pump"]), "lag": round(f["lag"], 1), "spout_err": round(f["spout_err"], 1),
            "boom": [round(f["boom"][0], 1), round(f["boom"][1]), round(f["boom"][2])], "lift": round(f["lift"]),
            "dose": DOSE, "field_len": FIELD_LEN, "need": round(RX_FULL - RX_START, 1),
            "plan": {"x_a": X_A, "x_b": X_B, "ys": YS, "r": R, "y_turn": Y_TURN, "yr": YS + P.dock_d,
                     "fence": FENCE_Y}}


def summary(frames=None):
    frames = frames or prepare()
    ev = _sim["events"]
    pumping = [f for f in frames if f["pump"] > 0]
    moving = [f for f in pumping if abs(f["v_w"]) > 1.0]
    return {"frames": len(frames), "duration_s": round(frames[-1]["t"], 1),
            "events_s": {k: round(v, 1) for k, v in sorted(ev.items(), key=lambda kv: kv[1])},
            "standstill_stop1_s": round(ev["reverse"] - ev["stop1"], 1),
            "standstill_stop2_s": round(ev["arc_b"] - ev["stop2"], 1),
            "pumped_l": round(RX_FULL - RX_START, 1), "pump_s": round(ev["full"] - ev["pump_on"], 1),
            "pump_while_driving_pct": round(100.0 * len(moving) / max(1, len(pumping))),
            "flow_lpm": round(60.0 * Q_FILL), "max_lag_mm": round(max(abs(f["lag"]) for f in frames), 1),
            "max_spout_err_mm": round(max((f["spout_err"] for f in pumping), default=0.0), 1),
            "boom_r_range": (round(min(f["boom"][1] for f in pumping)), round(max(f["boom"][1] for f in pumping))),
            "refiller_reposition_m": round((2.0 * W + R_STRAIGHT()) / 1000.0, 1)}


def R_STRAIGHT():
    return 2.0 * R - W


def render_frames(folder, first=0, count=None, fps=FPS, size=(720, 480)):
    import FreeCADGui as Gui
    doc = App.getDocument(DOC_NAME)
    frames = prepare(fps)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
        json.dump([meta(f) for f in frames], handle)
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    last = len(frames) if count is None else min(len(frames), first + count)
    for i in range(first, last):
        apply_frame(doc, frames[i])
        track_camera(frames[i], frames)
        Gui.updateGui()
        view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
    return last, len(frames)


def render_all(folder, fps=FPS, size=(720, 480)):
    build()
    first, total = 0, 1
    while first < total:
        first, total = render_frames(folder, first, 40, fps, size)
    return total


def stop():
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None


def play(fps=FPS, loop=False, follow=True, speed=2.0):
    import FreeCADGui as Gui
    from PySide import QtCore
    global _timer
    stop()
    doc = App.getDocument(DOC_NAME)
    frames = prepare(fps)
    Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
    _play.update({"index": 0})

    def step():
        try:
            if _play["index"] >= len(frames):
                if loop:
                    _play["index"] = 0
                else:
                    stop()
                    return
            f = frames[_play["index"]]
            _play["index"] += 1
            apply_frame(doc, f)
            if follow:
                track_camera(f, frames)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / (fps * speed)))


def check_fit(doc=None, tol=1.0, step=2):
    """Overlap between the refiller (robot, kit, trailer) and the working robot (robot, applicator, receiver kit)
    in every 'step'-th frame from boom out to boom parked. Must be empty."""
    doc = doc or App.getDocument(DOC_NAME)
    frames = prepare()
    ev = _sim["events"]
    sel = [f for f in frames if ev["boom_ready"] - 1.0 <= f["t"] <= ev["boom_parked"] + 0.5][::step]
    out = {}
    for f in sel:
        apply_frame(doc, f)
        doc.recompute()
        a = [(o, B.global_shape(o)) for o in _doc["robot"].OutListRecursive if o.TypeId == "Part::Feature"
             and not o.Shape.isNull() and B.base_name(o.Name) not in B.SKIP]
        b = [(o, B.global_shape(o)) for o in _doc["worker"].OutListRecursive if o.TypeId == "Part::Feature"
             and not o.Shape.isNull() and B.base_name(o.Name) not in B.SKIP]
        hits = B._overlaps([(x, y) for x in a for y in b], tol)
        if hits:
            out[round(f["t"], 1)] = hits
    return out
