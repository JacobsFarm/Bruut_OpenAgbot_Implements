"""Animation: the working robot skips passes so that it can turn in one go, and the refiller with the IBC waits
inside that turn on the headland.

The working robot (standard Bruut with the liquid fertilizer applicator advanced and the receiver kit) works the
field in the order 1, 7, 2, 8, 3, 9, ... (+6 / -5 passes): every turn is a U-turn (6 m on this headland, 5 m on the
far one), never reversing. The refiller stands in the middle of the turn, inside the loop, with its arm over the
straight part of the turn. The working robot lifts its applicator, drives the first arc, stops on the straight with
its funnel under the hanging nozzle, is topped up (pump on, level sensor stops it, drip-stop nozzle closes), drives
on into its next pass and lowers the applicator. Once it is back in the field the refiller drives 1 m further, to the
middle of the next turn on this headland. Two refills are shown: turn 3 -> 9 and, after a time skip (pass 9 down,
U-turn at the far end, pass 4 back up), turn 4 -> 10.

Builds a separate document (the robot files in "agbot design" and the applicator are not changed).

Use in FreeCAD:
    import animate_mrs
    animate_mrs.build()                              # build the document
    animate_mrs.play()                               # play live, animate_mrs.stop()
    animate_mrs.summary()                            # key figures of the run
    animate_mrs.check_fit()                          # overlap refiller - working robot around the refills
    animate_mrs.render_all(r"C:\\temp\\mrs_frames")
    import make_gif_mrs; make_gif_mrs.main(r"C:\\temp\\mrs_frames", r"previews\\animation_refill_in_u_turn.gif")
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrs_params as P
import mrs_calc as C
import mrs_parts as G
import build_mrs as B

DOC_NAME = "Mobile_refiller_simple_animation"

# ---------------------------------------------------------------------
# Field and plan (mm, mm/s). x along the headland (pass p at x = (p - 1) W), y = 0 is the field edge, headland at
# y > 0. Rear-axle centre of the working robot.
# ---------------------------------------------------------------------
W = C.WORK_WIDTH
R = C.R_TURN
N = C.skip_n()
Y_TURN = P.y_turn
YS = C.YS
Y_START = -3200.0
Y_END = -3200.0
FIELD_START = -15000.0
FENCE_Y = 1000.0 * C.headland_depth() + 900.0
V_WORK, V_HEAD = 1000.0 * C.V_WORK, 1000.0 * C.V_HEAD
ACCEL = 1000.0 * C.ACCEL
STEER_RATE = 35.0                   # deg/s
ARC_STEER = math.degrees(math.atan(P.robot_wheelbase / R))
ACT_SPEED = 60.0                    # applicator lift
LIFT = 140.0
RAISE_Y = -500.0                    # lifting starts when the knives are here (0.5 m before the edge)
LOWER_Y = 900.0                     # lowering starts when the knives (behind the robot) are here on the way back
KNIFE_DEPTH = 35.0
SEGMENTS = ((3, 3 + N), (4, 4 + N))  # the two refills shown
DONE_BEFORE = (1, 1 + N, 2, 2 + N)   # passes worked before the animation starts

# refiller
V_R, A_R = 1000.0 * P.v_full, 1000.0 * P.a_full
MOVE_WHEN_Y = -600.0                # the refiller moves on when the working robot is back in the field

# liquid: the working robot used 2 passes since the last refill on this headland
DOSE = 550.0                        # l/ha
FIELD_LEN = 200.0                   # m
RX_FULL = 145.0                     # l, level sensor stops the pump here (work tank 147 l)
RX_START = RX_FULL - C.per_round_l(DOSE, FIELD_LEN)
IBC_START = 640.0
Q_FILL = C.pump_q_ls()              # l/s

FPS = 5                             # frames per second of real time; the GIF plays at 10 fps = 2 x speed
DT = 0.02
SKIP_FRAMES = 12
HOLD_END = 2.0

COLOR = {"field": (0.45, 0.62, 0.30), "headland": (0.56, 0.68, 0.40), "edge": (0.97, 0.97, 0.95),
         "slot": (0.22, 0.14, 0.08), "post": (0.45, 0.33, 0.20), "wire": (0.75, 0.75, 0.75),
         "stream": (0.15, 0.50, 0.80), "path": (0.93, 0.93, 0.90)}
SLOT_HALF = 6.0
PASSES = tuple(range(1, 2 * N + 1))

_timer = None
_play = {}
_cache = {"act": {}, "slots": {}}
_doc = {}


def px(p):
    return (p - 1) * W


# ---------------------------------------------------------------------
# Paths of the working robot (rear-axle centre)
# ---------------------------------------------------------------------
def _line(p0, p1, step=10.0):
    return C._line(p0, p1, step)


def _arc(c, r, a0, a1, step=10.0):
    return C._arc(c, r, a0, a1, step)


class Path:
    def __init__(self, pieces, direction=1):
        """pieces: [(points, steer_deg, v_cap)], direction +1 forward, -1 reverse."""
        self.pts, self.steer, self.starts = [], [], []
        for pts, steer, cap in pieces:
            if self.pts:
                pts = pts[1:]
            self.starts.append(len(self.pts))
            for p in pts:
                self.pts.append(p)
                self.steer.append(steer)
        self.cum = [0.0]
        for p, q in zip(self.pts[:-1], self.pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
        self.length = self.cum[-1]
        self.dir = direction
        self.piece_s = [self.cum[i] for i in self.starts]
        self.piece_cap = [pc[2] for pc in pieces]

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

    def piece(self, s):
        k = 0
        for i, s0 in enumerate(self.piece_s):
            if s >= s0:
                k = i
        return k

    def v_allowed(self, s, a):
        v = math.sqrt(max(0.0, 2.0 * a * (self.length - s)))
        cur = self.piece_cap[0]
        for s0, cap in zip(self.piece_s, self.piece_cap):
            if s0 > s:
                v = min(v, math.sqrt(cap * cap + 2.0 * a * (s0 - s)))
            else:
                cur = cap
        return min(v, cur)


def seg_paths(pa, pb):
    """m1: pass pa up, first arc, onto the straight up to the stop under the nozzle; m2: rest of the straight,
    second arc, pass pb down."""
    xa, xb = px(pa), px(pb)
    s = 1.0 if xb > xa else -1.0
    spot = C.refill_spot(xa, xb)
    steer = -s * ARC_STEER
    c1, c2 = (xa + s * R, Y_TURN), (xb - s * R, Y_TURN)
    a_in, a_top = (180.0, 90.0) if s > 0 else (0.0, 90.0)
    a_out = 0.0 if s > 0 else 180.0
    m1 = Path([(_line((xa, Y_START), (xa, Y_TURN)), 0.0, V_WORK), (_arc(c1, R, a_in, a_top), steer, V_HEAD),
               (_line((c1[0], YS), (spot["stop_x"], YS)), 0.0, V_HEAD)])
    m2 = Path([(_line((spot["stop_x"], YS), (c2[0], YS)), 0.0, V_HEAD), (_arc(c2, R, a_top, a_out), steer, V_HEAD),
               (_line((xb, Y_TURN), (xb, Y_END)), 0.0, V_WORK)])
    return m1, m2, spot


def turn_path_points(pa, pb):
    pts, _ = C.u_turn_points(px(pa), px(pb), y_in=-1500.0, y_out=-1500.0, step=60.0)
    return pts


# ---------------------------------------------------------------------
# Kinematics helpers
# ---------------------------------------------------------------------
heading = C.heading


def to_world(rear, psi, local):
    """Local robot point (x, y relative to the robot centre) -> world, given the rear-axle centre and heading."""
    hx, hy = heading(psi)
    rx, ry = hy, -hx
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
    """Position along a trapezoid move of length d (sign kept) at time t."""
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


def refiller_placement(xc, yc):
    """Refiller heading along the headland (+x), arm to the left = towards the straight of the turn."""
    return App.Placement(V(xc, yc, 0.0), App.Rotation(V(0, 0, 1), -90.0))


def worker_placement(rear, psi):
    hx, hy = heading(psi)
    return App.Placement(V(rear[0] + P.robot_axle_y * hx, rear[1] + P.robot_axle_y * hy, 0.0),
                         App.Rotation(V(0, 0, 1), psi))


def funnel_world(rear, psi):
    return to_world(rear, psi, P.funnel_xy)


def nozzle_world(xc, yc):
    p = refiller_placement(xc, yc).multVec(V(G.NX, G.NY, 0.0))
    return p.x, p.y


# ---------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------
def _knife_dy():
    LP = B.load_lfa().P
    return LP.robot_mount_y + LP.disc_y + LP.knife_tip_rel[0]


def simulate():
    knife_dy = _knife_dy()
    frames, events = [], {}
    slots = {p: [FIELD_START, -60.0] for p in DONE_BEFORE}
    t = 0.0
    next_frame = 0.0
    spin_w = {k: 0.0 for k in WHEELS}
    spin_r = 0.0
    ibc = IBC_START
    first_spot = C.refill_spot(px(SEGMENTS[0][0]), px(SEGMENTS[0][1]))
    r = {"x": first_spot["xc"], "y": first_spot["yc"]}
    for k, (pa, pb) in enumerate(SEGMENTS):
        m1, m2, spot = seg_paths(pa, pb)
        nxt = C.refill_spot(px(pa + 1), px(pb + 1))
        ev = {}
        w = {"state": "work", "s": 0.0, "v": V_WORK, "steer": 0.0, "lift": 0.0, "level": RX_START}
        r.update({"state": "waiting", "t0": t, "t_seg": t, "pump": 0.0, "x0": r["x"], "v": 0.0})
        prev_wheels = None
        knife0 = to_world(m1.pose(0.0)[:2], m1.pose(0.0)[2], (0.0, knife_dy))
        slots[pa] = [FIELD_START, knife0[1]]
        slots.setdefault(pb, None)
        t_end = None
        while True:
            path = m1 if w["state"] in ("work", "stopped") else m2
            if w["state"] in ("work", "go"):
                vmax = path.v_allowed(w["s"], ACCEL)
                w["v"] = min(w["v"] + ACCEL * DT, vmax)
                w["s"] += w["v"] * DT
                look = w["s"] + 0.35 * w["v"]
                w["steer"] = approach(w["steer"], path.steer_at(look), STEER_RATE, DT)
                if w["s"] >= path.length - 0.5 or (w["v"] < 1.0 and path.length - w["s"] < 5.0 and t > ev.get("go", 0.0) + 1.0):
                    w["s"], w["v"] = path.length, 0.0
                    if w["state"] == "work":
                        w["state"] = "stopped"
                        ev["stop"] = t
                    else:
                        w["state"] = "away"
                        ev["away"] = t
            elif w["state"] == "stopped":
                w["steer"] = approach(w["steer"], 0.0, STEER_RATE, DT)
                if r["state"] == "done":
                    w["state"], w["s"], w["v"] = "go", 0.0, 0.0
                    ev["go"] = t
            path = m1 if w["state"] in ("work", "stopped") else m2
            rx_, ry_, psi = path.pose(w["s"])
            rear = (rx_, ry_)
            knife = to_world(rear, psi, (0.0, knife_dy))
            if path is m1:
                target = LIFT if knife[1] >= RAISE_Y else 0.0
            else:
                target = 0.0 if (path.piece(w["s"]) == 2 and knife[1] <= LOWER_Y) else LIFT
            w["lift"] = approach(w["lift"], target, ACT_SPEED, DT)
            in_soil = w["lift"] < KNIFE_DEPTH
            if path is m1 and in_soil:
                slots[pa][1] = knife[1]
            if path is m2 and in_soil:
                if slots[pb] is None:
                    slots[pb] = [knife[1], knife[1]]
                    ev["knives_in"] = t
                slots[pb][0] = knife[1]
            if path is m1 and not in_soil and "knives_out" not in ev:
                ev["knives_out"] = t
            if in_soil and w["v"] > 0:
                w["level"] -= DOSE * 1e-4 * (W / 1000.0) * (w["v"] / 1000.0) * DT
            wheels = {kk: to_world(rear, psi, loc) for kk, loc in WHEELS.items()}
            if prev_wheels is not None and w["v"] > 0:
                for kk in WHEELS:
                    spin_w[kk] += math.hypot(wheels[kk][0] - prev_wheels[kk][0],
                                             wheels[kk][1] - prev_wheels[kk][1]) / (P.robot_tire_d / 2.0)
            prev_wheels = wheels
            fw = funnel_world(rear, psi)

            # ---------------- refiller ----------------
            x_old = r["x"]
            st, tt = r["state"], t - r["t0"]
            if st == "waiting" and w["state"] == "stopped":
                r["state"], r["t0"] = "check", t
                ev["check"] = t
            elif st == "check" and tt >= C.T_CHECK:
                r["state"], r["t0"] = "pumping", t
                ev["pump_on"] = t
            elif st == "pumping":
                q = Q_FILL
                r["pump"] = q
                w["level"] += q * DT
                ibc -= q * DT
                if w["level"] >= RX_FULL:
                    w["level"] = RX_FULL
                    r["pump"] = 0.0
                    r["state"], r["t0"] = "closing", t
                    ev["full"] = t
            elif st == "closing" and tt >= C.T_CLOSE:
                r["state"], r["t0"] = "done", t
                ev["closed"] = t
            elif st == "done" and w["state"] in ("go", "away") and rear[1] < MOVE_WHEN_Y:
                r["state"], r["t0"], r["x0"] = "moving", t, r["x"]
                ev["move"] = t
            elif st == "moving":
                d = nxt["xc"] - r["x0"]
                r["x"] = r["x0"] + profile(d, V_R, A_R, tt)
                if tt >= move_time(d, V_R, A_R):
                    r["x"] = nxt["xc"]
                    r["state"], r["t0"] = "ready", t
                    ev["ready"] = t
            r["v"] = (r["x"] - x_old) / DT
            spin_r += (r["x"] - x_old) / (P.robot_tire_d / 2.0)

            if t >= next_frame - 1e-9:
                frames.append({
                    "t": t, "seg": k, "pair": (pa, pb), "skip": False, "w_state": w["state"], "r_state": r["state"],
                    "rear": rear, "psi": psi, "steer": w["steer"], "spin_w": dict(spin_w), "lift": w["lift"],
                    "v_w": w["v"], "rx_level": w["level"], "r_pose": (r["x"], r["y"]), "spin_r": spin_r,
                    "v_r": r["v"], "ibc": ibc, "pump": r["pump"], "funnel": fw, "knife": knife,
                    "slots": {p: (tuple(v) if v else None) for p, v in slots.items()},
                    "nozzle": nozzle_world(r["x"], r["y"])})
                next_frame += 1.0 / FPS
            t += DT
            if w["state"] == "away" and r["state"] == "ready":
                if t_end is None:
                    t_end = t
                if t > t_end + (HOLD_END if k == len(SEGMENTS) - 1 else 0.6):
                    break
            if t > r["t_seg"] + 300.0:
                raise RuntimeError("animation did not finish: %s / %s" % (w["state"], r["state"]))
        events[k] = ev
        if k < len(SEGMENTS) - 1:
            # time skip: pass pb down to the far end, U-turn of (N - 1) W, pass pa + 1 back up (fast forward)
            gap = 2.0 * (FIELD_LEN - abs(Y_END) / 1000.0) / C.V_WORK + C.u_turn_time((N - 1) * W / 1000.0)
            slots[pb][0] = FIELD_START
            last = dict(frames[-1])
            far = 12000.0
            for i in range(SKIP_FRAMES):
                frac = (i + 1.0) / (SKIP_FRAMES + 1.0)
                if frac < 0.5:
                    rear, psi = (px(pb), Y_END - far * frac / 0.5), 180.0
                else:
                    rear, psi = (px(pa + 1), Y_START - far * (1.0 - frac) / 0.5), 0.0
                    knife = to_world(rear, psi, (0.0, knife_dy))
                    slots[pa + 1] = [FIELD_START, knife[1]]
                f = dict(last)
                f.update({"skip": True, "skip_s": gap, "t": last["t"] + gap * frac, "rear": rear, "psi": psi,
                          "path_pair": SEGMENTS[k + 1],
                          "steer": 0.0, "lift": 0.0, "funnel": funnel_world(rear, psi),
                          "slots": {p: (tuple(v) if v else None) for p, v in slots.items()}, "pump": 0.0,
                          "v_w": V_WORK, "v_r": 0.0})
                frames.append(f)
            t = frames[-1]["t"] + 1.0 / FPS
            next_frame = t
            events.setdefault("skips", []).append((last["t"], gap))
    return frames, events


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
X_RANGE = (-6000.0, 16000.0)


def ground_shapes():
    field = G.box_span(X_RANGE, (FIELD_START, 0.0), (-40.0, 0.0))
    head = G.box_span(X_RANGE, (0.0, FENCE_Y + 1500.0), (-40.0, 0.0))
    edge = G.box_span(X_RANGE, (-25.0, 25.0), (0.0, 1.5))
    posts, wires = [], []
    x = X_RANGE[0]
    while x <= X_RANGE[1]:
        posts.append(G.cyl_z(100.0, 0.0, 1200.0, x, FENCE_Y))
        x += 2500.0
    for z in (500.0, 900.0, 1150.0):
        wires.append(G.cyl_x(8.0, X_RANGE[0], X_RANGE[1], FENCE_Y, z))
    return field, head, edge, Part.makeCompound(posts), Part.makeCompound(wires)


def slot_rows(x0, y0, y1):
    if y0 is None or y1 is None or abs(y1 - y0) < 5.0:
        return Part.Shape()
    lo, hi = sorted((y0, y1))
    key = (x0, round(lo / 20.0), round(hi / 20.0))
    if key not in _cache["slots"]:
        _cache["slots"][key] = Part.makeCompound([G.box_span((x0 + rx - SLOT_HALF, x0 + rx + SLOT_HALF), (lo, hi),
                                                             (0.0, 1.0)) for rx in (-400.0, -200.0, 0.0, 200.0, 400.0)])
    return _cache["slots"][key]


def build():
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Mobile refiller simple - refill in the U-turn"
    doc.Comment = "Generated by animate_mrs.py (no need to save). Robots from agbot design, applicator advanced."
    worker, wobjs = B.build_robot(doc, "working_robot_with_applicator")
    BL = B.load_lfa()
    BL.build_into(doc, worker, 0.0, BL.translation(0.0, BL.P.robot_mount_y, 0.0))
    B.build_receiver_into(doc, worker, RX_START)
    robot, robjs = B.build_robot(doc, "refiller_robot")
    B.hide_robot_gnss(robjs)
    B.build_refiller_into(doc, robot, 0.0, IBC_START)
    for name, shape, color in zip(("anim_field", "anim_headland", "anim_edge", "anim_posts", "anim_wires"),
                                  ground_shapes(), ("field", "headland", "edge", "post", "wire")):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        o.ViewObject.ShapeColor = COLOR[color]
        o.ViewObject.LineColor = COLOR[color]
    for p in PASSES:
        o = doc.addObject("Part::Feature", "anim_slots_%d" % p)
        o.ViewObject.ShapeColor = COLOR["slot"]
        o.ViewObject.LineColor = COLOR["slot"]
    path = doc.addObject("Part::Feature", "anim_path")
    path.ViewObject.ShapeColor = COLOR["path"]
    path.ViewObject.LineColor = COLOR["path"]
    st = doc.addObject("Part::Feature", "anim_stream")
    st.ViewObject.ShapeColor = COLOR["stream"]
    doc.recompute()
    _doc.clear()
    _doc.update({"worker": worker, "w": wobjs, "robot": robot, "r": robjs, "BL": BL, "path_key": None,
                 "slot_keys": {}})
    _cache["act"].clear()
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
    B.set_levels(ibc=f["ibc"], receiver=f["rx_level"], doc=doc)
    for p in PASSES:
        v = f["slots"].get(p)
        key = None if not v else (round(v[0] / 20.0), round(v[1] / 20.0))
        if _doc["slot_keys"].get(p, "x") != key:
            doc.getObject("anim_slots_%d" % p).Shape = slot_rows(px(p), *v) if v else Part.Shape()
            _doc["slot_keys"][p] = key
    pair = f.get("path_pair", f["pair"])
    if _doc["path_key"] != pair:
        doc.getObject("anim_path").Shape = G.ground_line(turn_path_points(*pair), w=30.0, z=1.5)
        _doc["path_key"] = pair
    if f["pump"] > 0:
        nx, ny = f["nozzle"]
        doc.getObject("anim_stream").Shape = G.stream(nx, ny, P.nozzle_tip_z, G.RX_TOP + P.funnel_neck)
    else:
        doc.getObject("anim_stream").Shape = Part.Shape()


# ---------------------------------------------------------------------
# Camera and rendering
# ---------------------------------------------------------------------
CAM_WIDE = (0.10, -0.60, 0.80)       # direction from the target to the eye (from the field, looking at the headland)
CAM_CLOSE = (-0.35, 0.70, 0.62)      # from the fence side: the working robot in front, the refiller behind it
CAM_SKIP = (0.0, -0.35, 0.94)
DIST_CLOSE = 5200.0


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def camera_pose(f):
    """Wide shot that keeps both robots in view, close-up of nozzle and funnel while filling, high overview in the
    time skip."""
    ev = _sim["events"][f["seg"]]
    t = f["t"]
    wx, wy = to_world(f["rear"], f["psi"], (0.0, -300.0))
    rx, ry = f["r_pose"]
    sep = math.hypot(rx - wx, ry - wy)
    wide_t = ((wx + rx) / 2.0, (wy + ry) / 2.0 + 300.0, 300.0)
    wide_d = max(9000.0, 1.1 * sep + 5000.0)
    nx, ny = f["nozzle"]
    close_t = (nx, ny - 300.0, 900.0)
    k = smooth((t - (ev["stop"] - 3.5)) / 3.0) * (1.0 - smooth((t - (ev["go"] + 1.0)) / 3.0))
    tgt = [wide_t[i] + (close_t[i] - wide_t[i]) * k for i in range(3)]
    d = _unit([CAM_WIDE[i] + (CAM_CLOSE[i] - CAM_WIDE[i]) * k for i in range(3)])
    dist = wide_d + (DIST_CLOSE - wide_d) * k
    if f["skip"]:
        tgt = [rx - 500.0, ry + 600.0, 0.0]
        d = _unit(CAM_SKIP)
        dist = 15000.0
    return [tgt[i] + d[i] * dist for i in range(3)], tgt


def track_camera(f, fov=40.0):
    import FreeCADGui as Gui
    from pivy import coin
    eye, tgt = camera_pose(f)
    cam = Gui.ActiveDocument.ActiveView.getCameraNode()
    cam.position.setValue(coin.SbVec3f(*eye))
    cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
    cam.heightAngle.setValue(math.radians(fov))
    cam.nearDistance.setValue(50.0)
    cam.farDistance.setValue(90000.0)


W_STATE = {"work": "works pass %(a)d, lifts the applicator at the edge, U-turn towards pass %(b)d",
           "stopped": "stopped on the straight of the turn: funnel under the nozzle",
           "go": "drives on: second arc into pass %(b)d, lowers the applicator", "away": "works pass %(b)d"}
R_STATE = {"waiting": "waits inside the turn, nozzle above the straight", "check": "radio: both positions agree",
           "pumping": "pumping from the IBC into the work tank", "closing": "work tank full: pump off, nozzle closes",
           "done": "waits until the working robot is back in the field",
           "moving": "drives 1 m further: middle of the next turn on this headland",
           "ready": "waits at the next turn (pass %(a1)d -> %(b1)d)"}


def meta(f):
    wx, wy = to_world(f["rear"], f["psi"], (0.0, 0.0))
    pa, pb = f["pair"]
    names = {"a": pa, "b": pb, "a1": pa + 1, "b1": pb + 1}
    m = {"t": round(f["t"], 2), "skip": f["skip"], "w_state": f["w_state"], "r_state": f["r_state"],
         "w_text": W_STATE[f["w_state"]] % names, "r_text": R_STATE[f["r_state"]] % names,
         "w_pos": [round(wx), round(wy), round(f["psi"], 1)], "r_pos": [round(f["r_pose"][0]), round(f["r_pose"][1])],
         "v_w": round(f["v_w"]), "v_r": round(f["v_r"]), "rx": round(f["rx_level"], 1),
         "rx_cap": round(C.capacity_l("receiver"), 1), "rx_full": RX_FULL, "ibc": round(f["ibc"], 1),
         "ibc_cap": P.ibc_nominal_l, "pump_lpm": round(60.0 * f["pump"]), "lift": round(f["lift"]),
         "dose": DOSE, "field_len": FIELD_LEN, "need": round(RX_FULL - RX_START, 1), "pair": [pa, pb],
         "path_pair": list(f.get("path_pair", f["pair"])),
         "slots": {str(p): ([round(v[0]), round(v[1])] if v else None) for p, v in f["slots"].items()},
         "plan": {"w": W, "n": N, "r": R, "y_turn": Y_TURN, "ys": YS, "fence": FENCE_Y, "passes": len(PASSES),
                  "order": C.field_order(1)}}
    if f["skip"]:
        m["skip_text"] = ("time skip %d min %02d s: pass %d down to the far end, U-turn of %d m, pass %d back up" % (
            int(f["skip_s"] // 60), int(f["skip_s"] % 60), pb, N - 1, pa + 1))
    return m


def summary(frames=None):
    frames = frames or prepare()
    ev = _sim["events"]
    out = {"frames": len(frames), "duration_s": round(frames[-1]["t"], 1), "flow_lpm": round(60.0 * Q_FILL),
           "pumped_l": round(RX_FULL - RX_START, 1), "ibc_l": (IBC_START, round(frames[-1]["ibc"], 1))}
    for k in range(len(SEGMENTS)):
        e = ev[k]
        out["refill_%d" % (k + 1)] = {"turn": "%d -> %d" % SEGMENTS[k],
                                      "standstill_s": round(e["go"] - e["stop"], 1),
                                      "pump_s": round(e["full"] - e["pump_on"], 1),
                                      "refiller_move_s": round(e["ready"] - e["move"], 1),
                                      "events_s": {n: round(v, 1) for n, v in sorted(e.items(), key=lambda kv: kv[1])}}
    out["refiller_moved_m"] = round((C.refill_spot(px(SEGMENTS[1][0]), px(SEGMENTS[1][1]))["xc"] -
                                     C.refill_spot(px(SEGMENTS[0][0]), px(SEGMENTS[0][1]))["xc"]) / 1000.0, 2)
    out["max_nozzle_to_funnel_mm"] = round(max(math.hypot(f["nozzle"][0] - f["funnel"][0],
                                                          f["nozzle"][1] - f["funnel"][1])
                                               for f in frames if f["pump"] > 0), 1)
    out["time_skip_s"] = [round(g) for _, g in ev.get("skips", [])]
    return out


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
        track_camera(frames[i])
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
                track_camera(f)
        except Exception:
            stop()
            raise

    _timer = QtCore.QTimer()
    _timer.timeout.connect(step)
    _timer.start(int(1000 / (fps * speed)))


def outline_gap(f):
    """Smallest gap (mm) between the outlines of the two robots in a frame (mrs_calc rectangles: everything of the
    refiller below 1.3 m, the working robot with its applicator)."""
    w = C.worker_poly(f["rear"][0], f["rear"][1], f["psi"])
    return min(C.poly_dist(w, r) for r in C.refiller_polys(*f["r_pose"]))


def check_fit(doc=None, tol=1.0, step=2, gap=150.0, log=None):
    """Overlap between the refiller (robot, kit) and the working robot (robot, applicator, receiver kit) in every
    'step'-th frame while the working robot is on the headland. Frames where the outlines are more than 'gap' apart
    are only checked in 2D (above 1.3 m the refiller has only the arm, nozzle and antenna, which are above the
    working robot's highest point, the funnel rim at 1144 mm); the frames while it stands under the nozzle are
    always checked in 3D. Returns (overlaps, smallest outline gap, number of frames checked in 3D). Overlaps must be
    empty."""
    doc = doc or App.getDocument(DOC_NAME)
    frames = prepare()
    sel = [f for f in frames if not f["skip"] and f["rear"][1] > 0.0][::step]
    out, n3d, smallest, n_stop = {}, 0, 1e9, 0
    for i, f in enumerate(sel):
        g = outline_gap(f)
        smallest = min(smallest, g)
        if f["w_state"] == "stopped":
            n_stop += 1                             # standing still: the scene only changes in the liquid levels
        if g > gap and not (f["w_state"] == "stopped" and n_stop % 7 == 1):
            continue
        n3d += 1
        apply_frame(doc, f)
        a = [(o, B.global_shape(o)) for o in _doc["robot"].OutListRecursive if o.TypeId == "Part::Feature"
             and not o.Shape.isNull() and B.base_name(o.Name) not in B.SKIP]
        b = [(o, B.global_shape(o)) for o in _doc["worker"].OutListRecursive if o.TypeId == "Part::Feature"
             and not o.Shape.isNull() and B.base_name(o.Name) not in B.SKIP]
        hits = B._overlaps([(x, y) for x in a for y in b], tol)
        if hits:
            out[round(f["t"], 1)] = hits
        if log:
            with open(log, "a", encoding="utf-8") as handle:
                handle.write("%d/%d t %.1f gap %.0f hits %s\n" % (i, len(sel), f["t"], g, hits))
    return out, round(smallest, 1), n3d
