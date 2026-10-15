"""Animation of a refill visit at a stationary refill station, shared by the carriers (IBC trailer, three-point
frame, flat wagon). Each carrier has a thin animate_<p>.py that makes a Visit with its Carrier and exposes build(),
play(), stop(), summary(), check_docked(), check_fit() and render_all(folder).

The station stands on the headland, parallel to the field edge, with its arm pinned out to the left (towards the
field). The working robot (standard Bruut with the liquid fertilizer applicator advanced and the receiver kit)
finishes pass p, lifts its applicator at the field edge, turns left onto the headland and drives along it to the
station. It slows down for the last metres and stops with its funnel under the nozzle (the docked pose of
stc_build.worker_placement). The station checks both positions, pumps the litres of one visit from the IBC(s) into
the work tank (beacon amber), closes the drip-stop nozzle and the robot drives on. It turns round on the headland
(forward arc towards the field, reverse arc back onto the docking line), drives back along the headland under the
arm, turns right into pass p + 1 (the next pass of the field) and lowers its applicator.

The litres per visit, the flow and the standstill come from stc_calc.visit() / refill_time() with the carrier's
pump geometry, so the animation and the report give the same figures. At 1000 l/ha and a 200 m field the robot
works 6 passes per visit: 120 l.

World coordinates: x along the headland, y = 0 is the field edge, headland at y > 0. Pass p at x = 0, pass p + 1 at
x = -W (the field is worked towards -x; the passes at x > 0 are done). Paths are rear-axle centres.
"""
import json
import math
import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import stc_params as CP
import stc_parts as G
import stc_build as B
import stc_calc as K
import mrs_params as MP
import mrs_calc as MC

W = CP.work_width
R = MP.r_turn                       # 2400: planner radius (as the simple variant)
Y_TURN = MP.y_turn                  # 1800: arc starts here (applicator lifted, clear of the crop)
YS = Y_TURN + R                     # 4200: docking line on the headland (robot centre line)
Y_START = -3400.0
Y_END = -3400.0
FIELD_START = -15000.0
ARC_STEER = math.degrees(math.atan(MP.robot_wheelbase / R))
STEER_RATE = 35.0                   # deg/s
V_WORK, V_HEAD, V_DOCK = 1000.0 * CP.v_work, 1000.0 * CP.v_head, 1000.0 * CP.v_dock
V_TURN, V_REV = 400.0, 1000.0 * MC.V_REV
ACCEL = 1000.0 * MC.ACCEL
DOCK_SLOW = 2000.0                  # last 2 m at v_dock
PAUSE = 1.0                         # s: stop between forward and reverse in the turn-round (steering over)
ACT_SPEED = 60.0                    # applicator lift (mm/s)
LIFT = 140.0
RAISE_Y = -500.0                    # lifting starts when the knives are here (0.5 m before the edge)
LOWER_Y = 900.0                     # lowering starts when the knives are here on the way back into the field
KNIFE_DEPTH = 35.0
HEAD_RUN = 9000.0                   # straight on the headland from the end of the first arc to the docked pose

DOSE = 1000.0                       # l/ha: 20 l per 200 m pass, 6 passes per visit = 120 l
FIELD_LEN = 200.0                   # m
FIELD_W = 100.0                     # m (for visit(): station in the middle of the headland)
IBC_START = 0.8 * CP.ibc_nominal_l  # per IBC
RX_LOW = CP.rx_tank_l - CP.rx_refill_l      # 27 l left when the robot leaves the field for the station

FPS = 2                             # frames per second of real time (GIF at 10 fps = 5 x speed)
FPS_PUMP = 0.5                      # while it stands at the nozzle and pumps (GIF: 20 x speed)
DT = 0.02
HOLD_END = 1.5

COLOR = {"field": (0.45, 0.62, 0.30), "headland": (0.56, 0.68, 0.40), "edge": (0.97, 0.97, 0.95),
         "slot": (0.22, 0.14, 0.08), "post": (0.45, 0.33, 0.20), "wire": (0.75, 0.75, 0.75),
         "stream": (0.15, 0.50, 0.80), "path": (0.93, 0.93, 0.90)}
BEACON = {"green": (0.10, 0.80, 0.25), "amber": (1.00, 0.55, 0.05), "red": (0.85, 0.08, 0.06)}
BEACON_OFF = 0.28                   # unlit segments: colour x 0.28
SLOT_HALF = 6.0
DONE_X = [k * W for k in range(1, 7)]          # passes done before (x > 0)
PASS_A, PASS_B = 0.0, -W                       # pass p, pass p + 1

X_DOCK_REAR = -R - HEAD_RUN                     # rear axle of the docked robot (heading -x)
X_DOCK = X_DOCK_REAR - MP.robot_axle_y          # robot centre

CAM_FOLLOW = (0.30, -0.78, 0.55)     # direction from the target to the eye: from the field, the station behind
CAM_DOCK = (0.62, -0.55, 0.56)       # close-up of the nozzle, the funnel and the IBC
DIST_FOLLOW = 10500.0
DIST_DOCK = 5600.0


class Carrier:
    """What the animation needs from a station:
    key, title, doc_name: names; build_into(doc) -> (list of root Part names, mast spec M), with the arm at 0 (out
    to the left) and IBC_START litres in every IBC; ibc_tags; pump_geometry() -> (lift m, hose m);
    check_docked(doc) -> list of overlaps between the station (and its carrier) and the working robot ('Robot');
    ok: allowed contacts (stc_build.pair_ok)."""

    def __init__(self, key, title, doc_name, build_into, ibc_tags, pump_geometry, check_docked, ok):
        self.key, self.title, self.doc_name = key, title, doc_name
        self.build_into, self.ibc_tags, self.pump_geometry = build_into, ibc_tags, pump_geometry
        self.check_docked, self.ok = check_docked, ok


# ---------------------------------------------------------------------
# Paths of the working robot (rear-axle centre)
# ---------------------------------------------------------------------
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


def legs():
    """approach: pass p up, left arc onto the headland, along it to the nozzle (last 2 m slow);
    turn_1: forward left arc towards the field; turn_2: reverse arc back onto the docking line, heading +x;
    back: along the headland under the arm, right arc into pass p + 1, down the pass."""
    line, arc = MC._line, MC._arc
    xa, xb, xr = PASS_A, PASS_B, X_DOCK_REAR
    approach = Path([(line((xa, Y_START), (xa, Y_TURN), 10.0), 0.0, V_WORK),
                     (arc((xa - R, Y_TURN), R, 0.0, 90.0, 10.0), ARC_STEER, V_HEAD),
                     (line((xa - R, YS), (xr + DOCK_SLOW, YS), 10.0), 0.0, V_HEAD),
                     (line((xr + DOCK_SLOW, YS), (xr, YS), 10.0), 0.0, V_DOCK)])
    turn_1 = Path([(arc((xr, Y_TURN), R, 90.0, 180.0, 10.0), ARC_STEER, V_TURN)])
    turn_2 = Path([(arc((xr - 2.0 * R, Y_TURN), R, 0.0, 90.0, 10.0), -ARC_STEER, V_REV)], direction=-1)
    back = Path([(line((xr - 2.0 * R, YS), (xb - R, YS), 10.0), 0.0, V_HEAD),
                 (arc((xb - R, Y_TURN), R, 90.0, 0.0, 10.0), -ARC_STEER, V_HEAD),
                 (line((xb, Y_TURN), (xb, Y_END), 10.0), 0.0, V_WORK)])
    return [("approach", approach), ("turn_1", turn_1), ("turn_2", turn_2), ("back", back)]


def path_points():
    pts = []
    for _, p in legs():
        pts += p.pts
    return pts


# ---------------------------------------------------------------------
# Kinematics helpers
# ---------------------------------------------------------------------
heading = MC.heading


def to_world(rear, psi, local):
    """Local robot point (x, y relative to the robot centre) -> world, given the rear-axle centre and heading."""
    hx, hy = heading(psi)
    rx, ry = hy, -hx
    cx, cy = rear[0] + MP.robot_axle_y * hx, rear[1] + MP.robot_axle_y * hy
    return cx + local[0] * rx + local[1] * hx, cy + local[0] * ry + local[1] * hy


def wheel_angles(delta):
    length, half = MP.robot_wheelbase, MP.robot_wheel_x
    t = math.tan(math.radians(delta))
    return (math.degrees(math.atan2(length * t, length - half * t)),
            math.degrees(math.atan2(length * t, length + half * t)))


WHEELS = {"RL": (-MP.robot_wheel_x, -MP.robot_axle_y), "RR": (MP.robot_wheel_x, -MP.robot_axle_y),
          "FL": (-MP.robot_wheel_x, MP.robot_axle_y), "FR": (MP.robot_wheel_x, MP.robot_axle_y)}


def approach_value(cur, target, rate, dt):
    d = target - cur
    step = rate * dt
    return target if abs(d) <= step else cur + math.copysign(step, d)


def worker_placement(rear, psi):
    hx, hy = heading(psi)
    return App.Placement(V(rear[0] + MP.robot_axle_y * hx, rear[1] + MP.robot_axle_y * hy, 0.0),
                         App.Rotation(V(0, 0, 1), psi))


def funnel_world(rear, psi):
    return to_world(rear, psi, MP.funnel_xy)


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def _knife_dy():
    LP = B.load_mrs().load_lfa().P
    return LP.robot_mount_y + LP.disc_y + LP.knife_tip_rel[0]


W_TEXT = {"approach": "works pass p, lifts the applicator at the edge, drives along the headland to the station",
          "docked": "stopped beside the station: funnel under the nozzle",
          "turn_1": "turns round on the headland: forward towards the field",
          "turn_2": "turns round on the headland: reverse back onto the line",
          "back": "drives back along the headland, under the arm, into pass p + 1, lowers the applicator",
          "away": "works pass p + 1"}
S_TEXT = {"ready": "ready (green): arm out to the left, nozzle above the docking line",
          "check": "radio: both positions agree",
          "pumping": "pumping from the IBC into the work tank (amber)",
          "closing": "%d l in: pump off, drip-stop nozzle closes",
          "done": "done (green): the working robot drives on"}


# ---------------------------------------------------------------------
# One visit at one station
# ---------------------------------------------------------------------
class Visit:
    def __init__(self, carrier, mast_spec):
        self.c = carrier
        self.M = mast_spec
        self.sim = {}
        self.doc_ = {}
        self.cache = {"act": {}, "slots": {}, "ibc": {}}
        self.timer = None
        self.play_state = {}

    # ---------------- figures ----------------
    def flow_lpm(self):
        return K.fill_q(*self.c.pump_geometry())

    def visit(self):
        return K.visit(DOSE, FIELD_LEN, FIELD_W, self.flow_lpm())

    def litres(self):
        return self.visit()["litres"]

    def n_ibc(self):
        return len(self.c.ibc_tags)

    # ---------------- station on the headland ----------------
    def station_placement(self):
        """Station turned +90 deg: its y along -x, its left (the arm) towards the field. Placed so that the docked
        robot (stc_build.worker_placement, arm 0) has its centre at (X_DOCK, YS)."""
        d = B.worker_placement(self.M, 0.0, 0.0).Base
        rot = App.Rotation(V(0, 0, 1), 90.0)
        w = rot.multVec(d)
        return App.Placement(V(X_DOCK - w.x, YS - w.y, 0.0), rot)

    def nozzle_world(self):
        a = math.radians(0.0)
        p = self.station_placement().multVec(V(self.M["x"] - self.M["reach"] * math.cos(a),
                                               self.M["y"] - self.M["reach"] * math.sin(a), 0.0))
        return p.x, p.y

    def mast_world(self):
        p = self.station_placement().multVec(V(self.M["x"], self.M["y"], 0.0))
        return p.x, p.y

    # ---------------- simulation ----------------
    def simulate(self):
        knife_dy = _knife_dy()
        q = self.flow_lpm() / 60.0                       # l/s
        need = self.litres()
        n = self.n_ibc()
        route = legs()
        frames, ev = [], {}
        slots = {x: [FIELD_START, -60.0] for x in DONE_X}
        slots[PASS_A] = [FIELD_START, FIELD_START]
        slots[PASS_B] = None
        t, next_frame = 0.0, 0.0
        spin = {k: 0.0 for k in WHEELS}
        leg = 0
        w = {"state": "drive", "s": 0.0, "v": V_WORK, "steer": 0.0, "lift": 0.0, "used": 0.0, "t0": 0.0}
        st = {"state": "ready", "t0": 0.0, "pumped": 0.0, "q": 0.0}
        ibc = IBC_START * n
        prev_wheels = None
        t_end = None
        head_t = {"to": 0.0, "back": 0.0}
        while True:
            name, path = route[leg]
            if w["state"] == "drive":
                vmax = path.v_allowed(w["s"], ACCEL)
                w["v"] = min(w["v"] + ACCEL * DT, vmax)
                w["s"] += w["v"] * DT
                w["steer"] = approach_value(w["steer"], path.steer_at(w["s"] + 0.35 * w["v"]), STEER_RATE, DT)
                if w["s"] >= path.length - 0.5 or (w["v"] < 1.0 and path.length - w["s"] < 5.0):
                    w["s"], w["v"] = path.length, 0.0
                    ev[name + "_end"] = t
                    if leg == len(route) - 1:
                        w["state"] = "away"
                    elif name == "approach":
                        w["state"] = "docked"
                    else:
                        w["state"], w["t0"] = "pause", t
            elif w["state"] == "docked":
                if st["state"] == "done":
                    leg, w["s"], w["state"] = leg + 1, 0.0, "drive"
                    ev["leave"] = t
            elif w["state"] == "pause":
                w["steer"] = approach_value(w["steer"], route[leg + 1][1].steer_at(0.0), STEER_RATE, DT)
                if t - w["t0"] >= PAUSE and abs(w["steer"] - route[leg + 1][1].steer_at(0.0)) < 0.5:
                    leg, w["s"], w["state"] = leg + 1, 0.0, "drive"
            name, path = route[leg]
            rx_, ry_, psi = path.pose(w["s"])
            rear = (rx_, ry_)
            knife = to_world(rear, psi, (0.0, knife_dy))
            if name == "approach":
                target = LIFT if knife[1] >= RAISE_Y else 0.0
            elif name == "back":
                target = 0.0 if (path.piece(w["s"]) == 2 and knife[1] <= LOWER_Y) else LIFT
            else:
                target = LIFT
            w["lift"] = approach_value(w["lift"], target, ACT_SPEED, DT)
            in_soil = w["lift"] < KNIFE_DEPTH
            if name == "approach" and in_soil:
                slots[PASS_A][1] = knife[1]
            if name == "approach" and not in_soil and "knives_out" not in ev:
                ev["knives_out"] = t
            if name == "back" and in_soil:
                if slots[PASS_B] is None:
                    slots[PASS_B] = [knife[1], knife[1]]
                    ev["knives_in"] = t
                slots[PASS_B][0] = knife[1]
            if in_soil and w["v"] > 0 and w["state"] == "drive":
                w["used"] += DOSE * 1e-4 * (W / 1000.0) * (w["v"] / 1000.0) * DT
            if w["state"] == "drive" and name == "approach" and path.piece(w["s"]) >= 2:
                head_t["to"] += DT
            if w["state"] == "drive" and name == "back" and path.piece(w["s"]) == 0:
                head_t["back"] += DT
            wheels = {kk: to_world(rear, psi, loc) for kk, loc in WHEELS.items()}
            if prev_wheels is not None and w["v"] > 0:
                for kk in WHEELS:
                    spin[kk] += path.dir * math.hypot(wheels[kk][0] - prev_wheels[kk][0],
                                                      wheels[kk][1] - prev_wheels[kk][1]) / (MP.robot_tire_d / 2.0)
            prev_wheels = wheels

            # ---------------- station ----------------
            tt = t - st["t0"]
            if st["state"] == "ready" and w["state"] == "docked":
                st["state"], st["t0"] = "check", t
                ev["stop"] = t
            elif st["state"] == "check" and tt >= CP.t_check - 1e-9:
                st["state"], st["t0"] = "pumping", t
                ev["pump_on"] = t
            elif st["state"] == "pumping":
                st["q"] = q
                dl = min(q * DT, need - st["pumped"])
                st["pumped"] += dl
                ibc -= dl
                if st["pumped"] >= need - 1e-9:
                    st["q"] = 0.0
                    st["state"], st["t0"] = "closing", t + DT
                    ev["full"] = t + DT
            elif st["state"] == "closing" and tt >= CP.t_close - 1e-9:
                st["state"], st["t0"] = "done", t
                ev["closed"] = t
            elif st["state"] == "done" and leg >= 3 and ry_ < 0.0:
                st["state"] = "ready"

            interval = 1.0 / (FPS_PUMP if w["state"] == "docked" and st["state"] == "pumping" else FPS)
            if t >= next_frame - 1e-9:
                frames.append({
                    "t": t, "leg": name, "w_state": w["state"], "s_state": st["state"], "rear": rear, "psi": psi,
                    "steer": w["steer"], "spin": dict(spin), "lift": w["lift"], "v": w["v"] * path.dir,
                    "used": w["used"], "pumped": st["pumped"], "ibc": ibc, "q": st["q"],
                    "funnel": funnel_world(rear, psi), "knife": knife,
                    "slots": {x: (tuple(v) if v else None) for x, v in slots.items()},
                    "stand": (t - ev["stop"]) if "stop" in ev and "leave" not in ev else None})
                next_frame += interval
            t += DT
            if w["state"] == "away":
                if t_end is None:
                    t_end = t
                if t > t_end + HOLD_END:
                    break
            if t > 600.0:
                raise RuntimeError("animation did not finish: %s / %s" % (w["state"], st["state"]))
        # work tank: the robot arrives at the station with RX_LOW
        used_dock = max(f["used"] for f in frames if f["leg"] == "approach")
        for f in frames:
            f["rx"] = RX_LOW + used_dock - f["used"] + f["pumped"]
        ev["head_to_s"], ev["head_back_s"] = head_t["to"], head_t["back"]
        return frames, ev

    def prepare(self):
        if "frames" not in self.sim:
            self.sim["frames"], self.sim["events"] = self.simulate()
        return self.sim["frames"]

    def reset(self):
        self.sim.clear()

    # ---------------- document ----------------
    def ground_shapes(self, xr, fy):
        field = G.box_span(xr, (FIELD_START, 0.0), (-40.0, 0.0))
        head = G.box_span(xr, (0.0, fy + 1500.0), (-40.0, 0.0))
        edge = G.box_span(xr, (-25.0, 25.0), (0.0, 1.5))
        posts, wires = [], []
        x = xr[0]
        while x <= xr[1]:
            posts.append(G.cyl_z(100.0, 0.0, 1200.0, x, fy))
            x += 2500.0
        for z in (500.0, 900.0, 1150.0):
            wires.append(G.cyl_x(8.0, xr[0], xr[1], fy, z))
        return field, head, edge, Part.makeCompound(posts), Part.makeCompound(wires)

    def slot_rows(self, x0, y0, y1):
        if y0 is None or y1 is None or abs(y1 - y0) < 5.0:
            return Part.Shape()
        lo, hi = sorted((y0, y1))
        key = (x0, round(lo / 20.0), round(hi / 20.0))
        if key not in self.cache["slots"]:
            self.cache["slots"][key] = Part.makeCompound([
                G.box_span((x0 + rx - SLOT_HALF, x0 + rx + SLOT_HALF), (lo, hi), (0.0, 1.0))
                for rx in (-400.0, -200.0, 0.0, 200.0, 400.0)])
        return self.cache["slots"][key]

    def set_beacon(self, doc, lit):
        for name, rgb in BEACON.items():
            o = doc.getObject("beacon_" + name)
            if o is not None and o.ViewObject is not None:
                o.ViewObject.ShapeColor = rgb if name == lit else tuple(BEACON_OFF * v for v in rgb)

    def station_objects(self, doc):
        out = []
        for r in self.doc_["roots"]:
            out += B.checked(B.kit_objects(doc, r))
        return out

    def build(self):
        name = self.c.doc_name
        if name in App.listDocuments():
            App.closeDocument(name)
        doc = App.newDocument(name)
        doc.Label = "%s - refill visit" % self.c.title
        doc.Comment = ("Generated by animate_%s.py / stc_anim.py (no need to save). Robot from agbot design, "
                       "applicator advanced, receiver kit from mobile refiller/simple." % self.c.key)
        roots, M = self.c.build_into(doc)
        pl = self.station_placement()
        for r in roots:
            doc.getObject(r).Placement = pl
        doc.recompute()
        self.doc_.clear()
        self.doc_["roots"] = roots
        bb = B.bbox(doc, [o for r in roots for o in B.kit_objects(doc, r) if not B.in_arm(o)])
        self.doc_["station_bb"] = (bb.XMin, bb.XMax, bb.YMin, bb.YMax)
        fy = bb.YMax + 1300.0
        xr = (min(bb.XMin, X_DOCK_REAR - 2.0 * R - 2500.0) - 3500.0, 7500.0)
        self.doc_["fence"], self.doc_["x_range"] = fy, xr
        BM = B.load_mrs()
        worker = B.build_worker(doc, worker_placement((PASS_A, Y_START), 0.0), lift=0.0, rx_fill=RX_LOW)
        wobjs = {B.base_name(o.Name): o for o in worker.OutListRecursive}
        for nm, shape, color in zip(("anim_field", "anim_headland", "anim_edge", "anim_posts", "anim_wires"),
                                    self.ground_shapes(xr, fy), ("field", "headland", "edge", "post", "wire")):
            o = doc.addObject("Part::Feature", nm)
            o.Shape = shape
            o.ViewObject.ShapeColor = COLOR[color]
            o.ViewObject.LineColor = COLOR[color]
        for i, x in enumerate(DONE_X + [PASS_A, PASS_B]):
            o = doc.addObject("Part::Feature", "anim_slots_%d" % i)
            o.ViewObject.ShapeColor = COLOR["slot"]
            o.ViewObject.LineColor = COLOR["slot"]
        path = doc.addObject("Part::Feature", "anim_path")
        path.Shape = G.ground_line(path_points()[::6], w=30.0, z=1.5)
        path.ViewObject.ShapeColor = COLOR["path"]
        path.ViewObject.LineColor = COLOR["path"]
        s = doc.addObject("Part::Feature", "anim_stream")
        s.ViewObject.ShapeColor = COLOR["stream"]
        self.set_beacon(doc, "green")
        doc.recompute()
        self.doc_.update({"worker": worker, "w": wobjs, "BL": BM.load_lfa(), "BM": BM, "slot_keys": {},
                          "ibc_key": None, "beacon": "green"})
        self.cache["act"].clear()
        return doc

    def doc(self):
        return App.getDocument(self.c.doc_name)

    def _lfa_shapes(self, lift):
        BL = self.doc_["BL"]
        key = round(lift)
        if key not in self.cache["act"]:
            LP = BL.P
            disc_rel = (LP.disc_y - LP.u_pivot[0], LP.disc_z - LP.u_pivot[1])
            drop = BL.contact_drop(disc_rel, key, LP.unit_drop_deg)
            a, b = BL.actuator_points(key)
            body, rod = BL.G.actuator(b, a)
            strut = BL.G.u_strut(drop)
            hoses = [BL.G.outlet_hose(i, x, drop) for i, x in enumerate(LP.row_x)]
            beta = BL.press_beta(drop, BL.lift_state(key)[2]) if LP.press_wheel else 0.0
            self.cache["act"][key] = (drop, body, rod, strut, hoses, beta)
        return self.cache["act"][key]

    def apply_lift(self, lift):
        BL, w = self.doc_["BL"], self.doc_["w"]
        LP = BL.P
        theta, dy, dz = BL.lift_state(lift)
        drop, body, rod, strut, hoses, beta = self._lfa_shapes(lift)
        w["Toolbar_assembly"].Placement = BL.translation(0.0, dy, dz)
        for lv, z in (("upper", LP.pin_upper_z), ("lower", LP.pin_lower_z)):
            for sd in ("left", "right"):
                w["link_%s_%s" % (lv, sd)].Placement = BL.rotation_x(-theta, (LP.pin_front_y, z))
        w["act_body"].Shape = body
        w["act_rod"].Shape = rod
        for i in range(len(LP.row_x)):
            n = i + 1
            w["Unit_%d_arm" % n].Placement = BL.rotation_x(drop, LP.u_pivot)
            w["U%d_strut_rod" % n].Shape = strut[0]
            w["U%d_spring" % n].Shape = strut[1]
            w["hose_%d" % n].Shape = hoses[i]
            if LP.press_wheel:
                w["Unit_%d_press_arm" % n].Placement = BL.rotation_x(beta, LP.pw_pivot)

    def _ibc_shape(self, litres_):
        key = round(litres_ / 2.0) * 2.0
        if key not in self.cache["ibc"]:
            self.cache["ibc"][key] = G.ibc_liquid_local(key)
        return key, self.cache["ibc"][key]

    def apply_frame(self, doc, f):
        w = self.doc_["w"]
        self.doc_["worker"].Placement = worker_placement(f["rear"], f["psi"])
        left, right = wheel_angles(f["steer"])
        w["FL_steered"].Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), left))
        w["FR_steered"].Placement = App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), right))
        for tag in ("RL", "RR", "FL", "FR"):
            rot = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -math.degrees(f["spin"][tag])))
            for part in ("tire", "rim", "hub"):
                w["%s_%s" % (tag, part)].Placement = rot
        self.apply_lift(f["lift"])
        self.doc_["BM"].set_levels(receiver=f["rx"], objs=w)
        key, shape = self._ibc_shape(f["ibc"] / self.n_ibc())          # all IBCs on one suction header
        if self.doc_["ibc_key"] != key:
            for tag in self.c.ibc_tags:
                doc.getObject(tag + "_liquid").Shape = shape
            self.doc_["ibc_key"] = key
        for i, x in enumerate(DONE_X + [PASS_A, PASS_B]):
            v = f["slots"].get(x)
            k = None if not v else (round(v[0] / 20.0), round(v[1] / 20.0))
            if self.doc_["slot_keys"].get(i, "x") != k:
                doc.getObject("anim_slots_%d" % i).Shape = self.slot_rows(x, *v) if v else Part.Shape()
                self.doc_["slot_keys"][i] = k
        lit = "amber" if f["s_state"] == "pumping" else "green"
        if self.doc_["beacon"] != lit:
            self.set_beacon(doc, lit)
            self.doc_["beacon"] = lit
        if f["q"] > 0:
            nx, ny = self.nozzle_world()
            doc.getObject("anim_stream").Shape = G.stream(nx, ny, self.M["nozzle_z"], CP.FUNNEL_RIM_Z - 120.0)
        else:
            doc.getObject("anim_stream").Shape = Part.Shape()

    # ---------------- camera, meta, summary ----------------
    def camera_pose(self, f):
        """Follows the working robot; a closer view of the nozzle and the IBC while it stands at the station."""
        ev = self.sim["events"]
        t = f["t"]
        cx, cy = to_world(f["rear"], f["psi"], (0.0, -300.0))
        follow = (cx, cy + 900.0, 300.0)
        nx, ny = self.nozzle_world()
        dist_dock, z_dock = getattr(self.c, "dock_view", (DIST_DOCK, 800.0))
        dock = (nx + 200.0, ny + 700.0, z_dock)
        k = smooth((t - (ev["stop"] - 5.0)) / 4.0) * (1.0 - smooth((t - (ev["leave"] + 0.5)) / 4.0))
        tgt = [follow[i] + (dock[i] - follow[i]) * k for i in range(3)]
        d = _unit([CAM_FOLLOW[i] + (CAM_DOCK[i] - CAM_FOLLOW[i]) * k for i in range(3)])
        dist = DIST_FOLLOW + (dist_dock - DIST_FOLLOW) * k
        return [tgt[i] + d[i] * dist for i in range(3)], tgt

    def track_camera(self, f, fov=40.0):
        import FreeCADGui as Gui
        from pivy import coin
        eye, tgt = self.camera_pose(f)
        cam = Gui.ActiveDocument.ActiveView.getCameraNode()
        cam.position.setValue(coin.SbVec3f(*eye))
        cam.pointAt(coin.SbVec3f(*tgt), coin.SbVec3f(0, 0, 1))
        cam.heightAngle.setValue(math.radians(fov))
        cam.nearDistance.setValue(50.0)
        cam.farDistance.setValue(90000.0)

    def meta(self, f):
        wx, wy = to_world(f["rear"], f["psi"], (0.0, 0.0))
        vi = self.visit()
        q = self.flow_lpm()
        ws = "docked" if f["w_state"] == "docked" else ("away" if f["w_state"] == "away" else f["leg"])
        st = S_TEXT[f["s_state"]]
        if "%d" in st:
            st = st % round(vi["litres"])
        n = self.n_ibc()
        return {"t": round(f["t"], 2), "w_state": ws, "s_state": f["s_state"], "w_text": W_TEXT[ws], "s_text": st,
                "w_pos": [round(wx), round(wy), round(f["psi"], 1)], "v": round(f["v"]), "rx": round(f["rx"], 1),
                "rx_cap": CP.rx_tank_l, "rx_low": RX_LOW, "ibc": round(f["ibc"], 1),
                "ibc_cap": n * CP.ibc_nominal_l, "n_ibc": n, "pump_lpm": round(60.0 * f["q"]),
                "pumped": round(f["pumped"], 1), "lift": round(f["lift"]),
                "stand": None if f["stand"] is None else round(f["stand"], 1),
                "fps": FPS_PUMP if (f["w_state"] == "docked" and f["s_state"] == "pumping") else FPS,
                "plan": {"title": self.c.title, "dose": DOSE, "field_len": FIELD_LEN, "field_w": FIELD_W, "w": W,
                         "passes": vi["passes"], "litres": vi["litres"], "flow": q,
                         "refill_s": K.refill_time(vi["litres"], q), "visit_s": vi["visit_s"], "share": vi["share"],
                         "t_dock": CP.t_dock, "ys": YS, "fence": self.doc_.get("fence", YS + 3500.0),
                         "station_bb": [round(v) for v in self.doc_.get("station_bb", (0, 0, 0, 0))],
                         "mast": [round(v) for v in self.mast_world()],
                         "nozzle": [round(v) for v in self.nozzle_world()],
                         "done": DONE_X, "pass_a": PASS_A, "pass_b": PASS_B,
                         "path": [[round(x), round(y)] for x, y in path_points()[::25]]},
                "slots": {str(int(x)): ([round(v[0]), round(v[1])] if v else None) for x, v in f["slots"].items()}}

    def summary(self, frames=None):
        frames = frames or self.prepare()
        ev = self.sim["events"]
        vi = self.visit()
        q = self.flow_lpm()
        nx, ny = self.nozzle_world()
        return {"station": self.c.title, "frames": len(frames), "duration_s": round(frames[-1]["t"], 1),
                "flow_lpm": round(q, 1), "pumped_l": round(frames[-1]["pumped"], 1),
                "work_tank_l": (round(min(f["rx"] for f in frames), 1), round(max(f["rx"] for f in frames), 1)),
                "ibc_total_l": (round(IBC_START * self.n_ibc()), round(frames[-1]["ibc"], 1)),
                "standstill_s": round(ev["leave"] - ev["stop"], 1),
                "refill_time_s (stc_calc)": round(K.refill_time(vi["litres"], q), 1),
                "pump_s": round(ev["full"] - ev["pump_on"], 1),
                "headland_to_station_s": round(ev["head_to_s"], 1), "headland_back_s": round(ev["head_back_s"], 1),
                "turn_round_s": round(ev["turn_2_end"] - ev["leave"], 1),
                "edge_to_nozzle_m": round(abs(nx - PASS_A) / 1000.0, 1),
                "visit (stc_calc, %d l/ha, field %d x %d m)" % (DOSE, FIELD_LEN, FIELD_W): {
                    "passes": vi["passes"], "litres": vi["litres"], "detour_s": round(vi["detour_s"], 1),
                    "t_dock_s": CP.t_dock, "visit_s": round(vi["visit_s"], 1),
                    "share_pct": round(100 * vi["share"], 1)},
                "speed_mm_s": (round(min(f["v"] for f in frames)), round(max(f["v"] for f in frames))),
                "lift_mm": (round(min(f["lift"] for f in frames)), round(max(f["lift"] for f in frames))),
                "max_nozzle_to_funnel_mm": round(max(math.hypot(nx - f["funnel"][0], ny - f["funnel"][1])
                                                     for f in frames if f["q"] > 0), 1),
                "events_s": {k: round(v, 1) for k, v in sorted(ev.items(), key=lambda kv: kv[1])
                             if not k.startswith("head_")}}

    # ---------------- rendering and playing ----------------
    def render_frames(self, folder, first=0, count=None, size=(720, 480)):
        import FreeCADGui as Gui
        doc = self.doc()
        frames = self.prepare()
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "frames.json"), "w", encoding="utf-8") as handle:
            json.dump([self.meta(f) for f in frames], handle)
        Gui.ActiveDocument = Gui.getDocument(doc.Name)
        view = Gui.ActiveDocument.ActiveView
        view.setCameraType("Perspective")
        last = len(frames) if count is None else min(len(frames), first + count)
        for i in range(first, last):
            self.apply_frame(doc, frames[i])
            self.track_camera(frames[i])
            Gui.updateGui()
            view.saveImage(os.path.join(folder, "frame_%04d.png" % i), size[0], size[1], "White")
        return last, len(frames)

    def render_all(self, folder, size=(720, 480)):
        self.build()
        first, total = 0, 1
        while first < total:
            first, total = self.render_frames(folder, first, 40, size)
        return total

    def stop(self):
        if self.timer is not None:
            self.timer.stop()
            self.timer = None

    def play(self, loop=False, follow=True, speed=5.0):
        import FreeCADGui as Gui
        from PySide import QtCore
        self.stop()
        doc = self.doc()
        frames = self.prepare()
        Gui.ActiveDocument.ActiveView.setCameraType("Perspective")
        self.play_state["index"] = 0

        def step():
            try:
                if self.play_state["index"] >= len(frames):
                    if loop:
                        self.play_state["index"] = 0
                    else:
                        self.stop()
                        return
                f = frames[self.play_state["index"]]
                self.play_state["index"] += 1
                self.apply_frame(doc, f)
                if follow:
                    self.track_camera(f)
            except Exception:
                self.stop()
                raise

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(step)
        self.timer.start(int(1000 / (FPS * speed)))

    # ---------------- checks ----------------
    def _station_rects(self, doc):
        """Footprints (world, axis-parallel: the station is turned 90 deg) of the station parts below 1.3 m."""
        out = []
        for o in self.station_objects(doc):
            bb = B.global_shape(o).BoundBox
            if bb.ZMin < 1300.0:
                out.append([(bb.XMin, bb.YMin), (bb.XMax, bb.YMin), (bb.XMax, bb.YMax), (bb.XMin, bb.YMax)])
        return out

    def check_docked(self, doc=None, tol=1.0):
        """Station - working robot in the docked frame (the carrier's build_*.check_docked on this document)."""
        doc = doc or self.doc()
        f = [f for f in self.prepare() if f["w_state"] == "docked"][0]
        self.apply_frame(doc, f)
        doc.recompute()
        return self.c.check_docked(doc)

    def check_fit(self, doc=None, tol=1.0, step=2, gap=400.0, log=None):
        """Overlap between the station and the working robot (robot, applicator, receiver kit) in every 'step'-th
        frame. Frames where the outlines (station parts below 1.3 m as boxes, the robot as its rectangle) are more
        than 'gap' apart are only checked in 2D; the others in 3D (common volume, bounding-box pre-filter). The
        docked frames are checked once (the scene only changes in the liquid levels). Returns (overlaps, smallest
        outline gap, number of frames checked in 3D). Overlaps must be empty."""
        doc = doc or self.doc()
        frames = self.prepare()
        rects = self._station_rects(doc)
        station = None
        out, n3d, smallest, docked_done = {}, 0, 1e9, False
        for i, f in enumerate(frames[::step]):
            wp = MC.worker_poly(f["rear"][0], f["rear"][1], f["psi"])
            g = min(MC.poly_dist(wp, r) for r in rects)
            smallest = min(smallest, g)
            if f["w_state"] == "docked":
                if docked_done:
                    continue
                docked_done = True
            elif g > gap:
                continue
            n3d += 1
            self.apply_frame(doc, f)
            if station is None:
                station = [(o, B.global_shape(o)) for o in self.station_objects(doc)]
            wk = [(o, B.global_shape(o)) for o in self.doc_["worker"].OutListRecursive if o.TypeId == "Part::Feature"
                  and not o.Shape.isNull() and not o.Name.endswith("liquid")]
            hits = B.overlaps([(a, b) for a in station for b in wk], self.c.ok, tol)
            if hits:
                out[round(f["t"], 1)] = hits
            if log:
                with open(log, "a", encoding="utf-8") as handle:
                    handle.write("%d t %.1f gap %.0f hits %s\n" % (i, f["t"], g, hits))
        return out, round(smallest, 1), n3d
