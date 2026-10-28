"""Rijplan en simulatie van een heel veld: de werkrobot (precisie-applicator V2, 5 rijen) met een van de refillers.

Puur rekenwerk (geen document): bouwt de route van de werkrobot over alle banen en kopakkers, rijdt die met
snelheden, sturen, heffen en zakken, houdt het niveau in de werktank bij en laat de refiller zijn werk doen. Het
resultaat is een lijst frames op videotijd: het tempo (x echte tijd) hangt af van wat er gebeurt (snel midden in
de baan, langzaam in de bocht en bij het bijvullen). animate_fld.py zet die frames in FreeCAD om.

Scenario's (fld_params.SCENARIOS):
- simple:  banen overslaan (1, 7, 2, 8, ...), elke bocht een U-bocht; de IBC-refiller staat binnen de U-bocht op de
           kopakker en vult bij terwijl de werkrobot op het rechte stuk stilstaat; daarna 1 m verder.
- liquid:  aaneengesloten banen met driepuntsbochten (boog, achteruit langs de kopakker, boog); de refiller met
           giek en aanhanger zet de tuit in de trechter en rijdt mee terwijl de werkrobot achteruit rijdt.
- station: banen overslaan; een IBC-aanhanger staat stil op de kopakker naast het veld; als de werktank te laag is
           voor de volgende twee banen rijdt de werkrobot er na zijn baan heen, vult en draait terug.

Gebruik (ook buiten de GUI, in de Python van FreeCAD):
    import fld_plan
    run = fld_plan.simulate("simple")
    fld_plan.summary(run)
"""
import math
import os
import sys

import fld_params as P

FOLDER = os.path.dirname(os.path.abspath(__file__))
PA_ROOT = os.path.dirname(FOLDER)
ROOT = os.path.dirname(os.path.dirname(PA_ROOT))
CMB2_FOLDER = os.path.join(PA_ROOT, "combined_v2")
MR_FOLDER = os.path.join(ROOT, "mobile refiller")
REFILLER_FOLDERS = (os.path.join(MR_FOLDER, "simple"), os.path.join(MR_FOLDER, "liquid"),
                    os.path.join(MR_FOLDER, "stationary"), os.path.join(MR_FOLDER, "stationary", "ibc_trailer"))
L = P.FIELD_LEN


def setup_path():
    """combined_v2 (en via die de robot, pomp en applicator) vooraan; de refillers achteraan."""
    if CMB2_FOLDER not in sys.path:
        sys.path.insert(0, CMB2_FOLDER)
    import build_cmb2
    build_cmb2.setup_path()
    for folder in REFILLER_FOLDERS:
        if folder not in sys.path:
            sys.path.append(folder)
    if FOLDER in sys.path:
        sys.path.remove(FOLDER)
    sys.path.insert(0, FOLDER)


setup_path()


# ---------------------------------------------------------------------
# Applicator: mespunt en aandrukwiel t.o.v. het robotmidden, pomp
# ---------------------------------------------------------------------
class AppGeometry:
    def __init__(self):
        import build_cmb2
        build_cmb2.configure(5)
        import pa_params as PA
        import pa2_params as P2
        import animate_cmb as A
        self.PA, self.P2, self.A = PA, P2, A
        self.tip = A.knife_tip_local_y()
        self.rows = PA.n_discs
        self.row_x = list(PA.disc_x())
        self.r_disc = PA.disc_d / 2.0 - PA.work_depth / 2.0
        self.r_press = P2.pw_wheel_d / 2.0
        self.depth = PA.work_depth
        self.lift_max = PA.lift_max

    def knife_y(self, lift):
        return self.PA.mount_y + self.PA.implement_offset(lift)[0] + self.tip

    def press_y(self, lift):
        return self.PA.mount_y + self.PA.implement_offset(lift)[0] + self.P2.pw_wheel_c[0]

    def pump_rpm(self, v):
        return self.A.pump_rpm(v)


# ---------------------------------------------------------------------
# Geometrie: lijnen, bogen, kopakkers
# ---------------------------------------------------------------------
def px(p):
    return (p - 1) * P.W


def line(p0, p1, step=50.0):
    n = max(1, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / step))
    return [(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n) for i in range(n + 1)]


def arc(c, r, a0, a1, step=50.0):
    n = max(2, int(abs(math.radians(a1 - a0)) * r / step))
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def to_end(pts, end):
    """Kopakker-assenstelsel (veldrand y = 0, kopakker y > 0) -> veld: R = zelfde, F = gespiegeld voorbij -L."""
    return list(pts) if end == "R" else [(x, -L - y) for x, y in pts]


def heading(psi):
    a = math.radians(psi)
    return -math.sin(a), math.cos(a)


def local_to_world(rear, psi, local):
    """Punt (x, y t.o.v. het robotmidden) -> veld, bij achteras (rear) en koers psi (0 = +y)."""
    hx, hy = heading(psi)
    rx, ry = hy, -hx
    cx, cy = rear[0] + P.AXLE_Y * hx, rear[1] + P.AXLE_Y * hy
    return cx + local[0] * rx + local[1] * hx, cy + local[0] * ry + local[1] * hy


def robot_centre(rear, psi):
    return local_to_world(rear, psi, (0.0, 0.0))


class Piece:
    def __init__(self, kind, pts, cap, tag=None):
        self.kind, self.pts, self.cap, self.tag = kind, pts, cap, dict(tag or {})


class Move:
    """Doorlopend stuk rijden in een richting (dir +1 vooruit, -1 achteruit), eindigt in stilstand (stop)."""

    def __init__(self, direction):
        self.dir = direction
        self.pieces = []
        self.stop, self.info = None, {}

    def finish(self):
        self.pts, self.steer, self.piece_of = [], [], []
        self.piece_s = []
        for k, pc in enumerate(self.pieces):
            pts = pc.pts[1:] if self.pts else pc.pts
            self.piece_s.append(len(self.pts))
            sign = 0.0
            if pc.kind in ("arc",):
                (x0, y0), (x1, y1), (x2, y2) = pc.pts[0], pc.pts[len(pc.pts) // 2], pc.pts[-1]
                cross = (x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)
                sign = math.copysign(1.0, cross) * self.dir
            steer = sign * math.degrees(math.atan(P.WHEELBASE / P.R))
            for p in pts:
                self.pts.append(p)
                self.steer.append(steer)
                self.piece_of.append(k)
        self.cum = [0.0]
        for p, q in zip(self.pts[:-1], self.pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
        self.length = self.cum[-1]
        self.piece_s = [self.cum[i] for i in self.piece_s]
        return self

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
        return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f), psi

    def steer_at(self, s):
        return self.steer[min(self.index(max(0.0, min(self.length, s))), len(self.steer) - 1)]

    def piece(self, s):
        return self.pieces[self.piece_of[min(self.index(max(0.0, min(self.length, s))), len(self.piece_of) - 1)]]

    def v_allowed(self, s, a):
        v = math.sqrt(max(0.0, 2.0 * a * (self.length - s)))
        cur = self.pieces[0].cap
        for s0, pc in zip(self.piece_s, self.pieces):
            if s0 > s:
                v = min(v, math.sqrt(pc.cap * pc.cap + 2.0 * a * (s0 - s)))
            else:
                cur = pc.cap
        return min(v, cur)


class Route:
    """Lijst Moves; add() voegt een stuk toe (nieuwe Move bij richtingwissel), stop() sluit de Move af."""

    def __init__(self):
        self.moves = []
        self.open = None

    def add(self, kind, pts, cap, tag=None, direction=1):
        if self.open is None or self.open.dir != direction:
            if self.open is not None:
                self.stop("steer")
            self.open = Move(direction)
        self.open.pieces.append(Piece(kind, pts, cap, tag))

    def stop(self, label, **info):
        self.open.stop, self.open.info = label, info
        self.moves.append(self.open.finish())
        self.open = None


# ---------------------------------------------------------------------
# Baanvolgorde en bochten
# ---------------------------------------------------------------------
def skip_n():
    return int(math.ceil(2.0 * P.R / P.W)) + 1


def field_order(pattern):
    if pattern == "adjacent":
        return list(range(1, P.N_PASSES + 1))
    n = skip_n()
    out = []
    for k in range(1, n + 1):
        out.extend((k, k + n))
    return out[:P.N_PASSES]


def pass_piece(route, p, y0, y1):
    route.add("pass", line((px(p), y0), (px(p), y1), 100.0), P.V_WORK, {"pass": p, "dir_y": 1 if y1 > y0 else -1})


def u_turn(route, xa, xb, end, tag, stop_x=None, stop_info=None):
    """U-bocht van baan xa (de kopakker in) naar xb, in het kopakkerstelsel; stop_x: stoppen op het rechte stuk."""
    s = 1.0 if xb > xa else -1.0
    c1, c2 = (xa + s * P.R, P.Y_TURN), (xb - s * P.R, P.Y_TURN)
    a_in, a_out = (180.0, 0.0) if s > 0 else (0.0, 180.0)
    route.add("arc", to_end(arc(c1, P.R, a_in, 90.0), end), P.V_HEAD, tag)
    if stop_x is None:
        route.add("straight", to_end(line((c1[0], P.YS), (c2[0], P.YS)), end), P.V_HEAD, tag)
    else:
        route.add("straight", to_end(line((c1[0], P.YS), (stop_x, P.YS), 20.0), end), P.V_HEAD, tag)
        route.stop("refill", **(stop_info or {}))
        route.add("straight", to_end(line((stop_x, P.YS), (c2[0], P.YS), 20.0), end), P.V_HEAD, tag)
    route.add("arc", to_end(arc(c2, P.R, 90.0, a_out), end), P.V_HEAD, tag)


def three_point_turn(route, xa, xb, end, tag, dock=None):
    """Boog vooruit de kopakker op, achteruit langs de kopakker, boog vooruit de volgende baan in (xb = xa +- W).
    dock: stops 'dock' en 'rev_end' voor het bijvullen tijdens het achteruitrijden (anders 'steer')."""
    s = 1.0 if xb > xa else -1.0
    c1, c2 = (xa + s * P.R, P.Y_TURN), (xb - s * P.R, P.Y_TURN)
    a_in, a_out = (180.0, 0.0) if s > 0 else (0.0, 180.0)
    route.add("arc", to_end(arc(c1, P.R, a_in, 90.0), end), P.V_HEAD, tag)
    route.stop("dock" if dock else "steer", **(dock or {}))
    route.add("reverse", to_end(line((c1[0], P.YS), (c2[0], P.YS), 20.0), end), P.V_REV, tag, direction=-1)
    route.stop("rev_end" if dock else "steer", **(dock or {}))
    route.add("arc", to_end(arc(c2, P.R, 90.0, a_out), end), P.V_HEAD, tag)


def station_visit(route, xa, xb, xr, tag, info):
    """Linksaf de kopakker op naar het station (achteras gedokt op xr, koers -x), omkeren met een boog vooruit en
    een boog achteruit, terug langs de kopakker en rechtsaf baan xb in (alleen kopakker R)."""
    route.add("arc", arc((xa - P.R, P.Y_TURN), P.R, 0.0, 90.0), P.V_HEAD, tag)
    route.add("straight", line((xa - P.R, P.YS), (xr + P.DOCK_SLOW, P.YS)), P.V_HEAD, tag)
    route.add("dock", line((xr + P.DOCK_SLOW, P.YS), (xr, P.YS), 20.0), P.V_DOCK, tag)
    route.stop("station", **info)
    route.add("arc", arc((xr, P.Y_TURN), P.R, 90.0, 180.0), P.V_HEAD, tag)
    route.stop("steer")
    route.add("arc", list(reversed(arc((xr - 2.0 * P.R, P.Y_TURN), P.R, 90.0, 0.0))), P.V_REV, tag, direction=-1)
    route.stop("steer")
    route.add("straight", line((xr - 2.0 * P.R, P.YS), (xb - P.R, P.YS)), P.V_HEAD, tag)
    route.add("arc", arc((xb - P.R, P.Y_TURN), P.R, 90.0, 0.0), P.V_HEAD, tag)


def pass_use_l():
    return P.DOSE * 1e-4 * (P.W / 1000.0) * (L / 1000.0)


def station_visits(scn, order):
    """Na welke banen (de kopakker R in) de werkrobot naar het station gaat: als er na die baan te weinig in de tank
    zit voor de volgende twee banen plus de reserve."""
    level, visits = scn["rx_start"], []
    for i, p in enumerate(order):
        level -= pass_use_l()
        if i % 2 == 0 and i + 1 < len(order):
            if level - 2.0 * pass_use_l() < P.RX_RESERVE_L:
                visits.append(i)
                level = scn["rx_full"]
    return visits


def station_dock_x():
    return px(1) - P.R - P.SCENARIOS["station"]["dock_from_field"]


def funnel_offset():
    """Achteras -> trechter langs de koers."""
    return P.AXLE_Y + P.funnel_xy[1]


def build_route(key):
    scn = P.SCENARIOS[key]
    order = field_order(scn["pattern"])
    visits = station_visits(scn, order) if scn["refiller"] == "station" else []
    route = Route()
    pass_piece(route, order[0], -L - P.START_IN, P.Y_TURN)
    turns_r = 0
    for i in range(len(order) - 1):
        a, b = order[i], order[i + 1]
        end = "R" if i % 2 == 0 else "F"
        xa, xb = px(a), px(b)
        tag = {"turn": (a, b), "end": end, "turn_i": i}
        if scn["pattern"] == "adjacent":
            dock = {"k": turns_r, "turn": (a, b)} if (end == "R" and scn["refiller"] == "liquid") else None
            three_point_turn(route, xa, xb, end, tag, dock)
        elif end == "R" and scn["refiller"] == "simple":
            s = 1.0 if xb > xa else -1.0
            xm = 0.5 * (xa + xb)
            u_turn(route, xa, xb, end, tag, stop_x=xm - s * funnel_offset(), stop_info={"k": turns_r, "turn": (a, b)})
        elif end == "R" and i in visits:
            tag = dict(tag, visit=True)
            station_visit(route, xa, xb, station_dock_x(), tag, {"turn": (a, b)})
        else:
            u_turn(route, xa, xb, end, tag)
        if end == "R":
            turns_r += 1
        y_end = -L - P.START_IN if i + 1 == len(order) - 1 else (-L - P.Y_TURN if end == "R" else P.Y_TURN)
        pass_piece(route, b, P.Y_TURN if end == "R" else -L - P.Y_TURN, y_end)
    route.stop("end")
    return route, order, visits


# ---------------------------------------------------------------------
# Refillers
# ---------------------------------------------------------------------
def profile(d, v, a, t):
    """Positie langs een trapeziumbeweging van lengte d (teken blijft) op tijd t."""
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
    s = abs(d)
    if s <= 0:
        return 0.0
    if s <= v * v / a:
        return 2.0 * math.sqrt(s / a)
    return s / v + v / a


class SimpleRefiller:
    """mobile refiller/simple: IBC, mast met arm, hangende slang; staat binnen de U-bocht (koers +x, arm links =
    naar het rechte stuk). Na het bijvullen, zodra de werkrobot weer in het veld is, 1 m verder."""
    kind = "simple"
    busy_states = ("check", "pumping", "closing")

    def __init__(self, route, scn):
        import mrs_params as MP
        import mrs_calc as MC
        self.MP = MP
        self.q = MC.pump_q_ls()
        self.t_check, self.t_close = MC.T_CHECK, MC.T_CLOSE
        self.v, self.a = 1000.0 * MP.v_full, 1000.0 * MP.a_full
        self.spots = []
        for mv in route.moves:
            if mv.stop == "refill":
                a, b = mv.info["turn"]
                self.spots.append((0.5 * (px(a) + px(b)) - MP.mast_xy[1], P.YS - MP.dock_d))
        self.k = 0
        self.x, self.y = self.spots[0]
        self.state, self.t0, self.x0 = "waiting", 0.0, self.x
        self.ibc = 0.8 * MP.ibc_nominal_l
        self.flow = 0.0
        self.spin = 0.0
        self.count = 0

    def nozzle(self):
        nx, ny = self.MP.NOZZLE_XY          # refiller koers +x: lokaal (x, y) -> veld (y, -x)
        return self.x + ny, self.y - nx

    def step(self, t, dt, w):
        x_old = self.x
        tt = t - self.t0
        self.flow = 0.0
        st = self.state
        if st == "waiting" and w["mode"] == "stop" and w["stop"] == "refill":
            self.state, self.t0 = "check", t
        elif st == "check" and tt >= self.t_check:
            self.state, self.t0 = "pumping", t
        elif st == "pumping":
            self.flow = self.q
            self.ibc -= self.q * dt
            if w["level"] + self.q * dt >= w["full"]:
                self.state, self.t0 = "closing", t
                self.count += 1
        elif st == "closing" and tt >= self.t_close:
            self.state, self.t0 = "done", t
        elif st == "done" and w["mode"] == "drive" and w["rear"][1] < -600.0 and self.k + 1 < len(self.spots):
            self.state, self.t0, self.x0 = "moving", t, self.x
        elif st == "moving":
            d = self.spots[self.k + 1][0] - self.x0
            self.x = self.x0 + profile(d, self.v, self.a, tt)
            if tt >= move_time(d, self.v, self.a):
                self.k += 1
                self.x = self.spots[self.k][0]
                self.state, self.t0 = "waiting", t
        self.spin += (self.x - x_old) / P.TIRE_R
        return self.flow

    def release(self, label):
        return label != "refill" or self.state == "done"

    def busy(self):
        return self.state in self.busy_states

    TEXT = {"waiting": "waits inside the U-turn, nozzle over the straight", "check": "radio + RTK: funnel under the nozzle",
            "pumping": "pumping from the IBC into the work tank", "closing": "work tank full: pump off, nozzle closes",
            "done": "waits until the working robot is back in the field",
            "moving": "drives 1 m on to the middle of the next turn"}

    def frame(self):
        return {"pose": (self.x, self.y), "spin": self.spin, "ibc": self.ibc, "flow": self.flow, "state": self.state,
                "text": self.TEXT[self.state], "tank": (self.ibc, self.MP.ibc_nominal_l), "count": self.count,
                "stream": self.nozzle() if self.flow > 0 else None}


class LiquidRefiller:
    """mobile refiller/liquid: tank, giek met loopkat en tuit, aangedreven aanhanger; wacht naast het rechte
    (achteruit) stuk van de driepuntsbocht, buiten de bocht (koers -x). Tuit in de trechter, pomp aan, rijdt mee
    tijdens het achteruitrijden; daarna achteruit (met de aanhanger) naar de bocht twee banen verder."""
    kind = "liquid"
    busy_states = ("camera", "spout_down", "pumping", "spout_up")

    def __init__(self, route, scn):
        import mrl_params as LP
        import mrl_calc as LC
        self.LP = LP
        self.q = LC.fill_rate_ls()
        self.cx, self.cy = LP.col_xy
        self.docks = []
        for mv in route.moves:
            if mv.stop == "dock":
                rear, psi = mv.pose(mv.length)
                fw = local_to_world(rear, psi, P.funnel_xy)
                self.docks.append((fw[0] + self.cy, fw))
        self.y0 = P.YS + LP.dock_d
        self.k = 0
        self.x, self.y = self.docks[0][0] + 3500.0, self.y0
        self.phi, self.rr, self.s = LP.phi_park, LP.r_park, 0.0
        self.state, self.t0, self.x0 = "approach", 0.0, self.x
        self.mr = 0.85 * self.capacity("refiller")
        self.tr = 0.95 * self.capacity("trailer")
        self.flow, self.spin, self.count = 0.0, 0.0, 0
        self.dock_x0 = None
        self.frm = None

    def capacity(self, kind):
        import mrl_calc as LC
        return LC.capacity_l(kind)

    def ik(self, tx, ty):
        dx, dy = tx - self.cx, ty - self.cy
        r = math.sqrt(max(0.0, dx * dx + dy * dy - self.LP.spout_u ** 2))
        phi = math.degrees(math.atan2(dy, dx) - math.atan2(r, self.LP.spout_u))
        return phi, max(self.LP.r_park, min(self.LP.r_max, r))

    def target(self, fw):
        """Giekhoek en loopkat boven veldpunt fw (refiller op (x, y), koers -x: lokaal = (Y - y, -(X - x)))."""
        return self.ik(fw[1] - self.y, -(fw[0] - self.x))

    @staticmethod
    def unwrap(phi, ref):
        while phi - ref > 180.0:
            phi -= 360.0
        while phi - ref < -180.0:
            phi += 360.0
        return phi

    def boom_move_time(self):
        p0, r0, p1, r1 = self.frm
        LP = self.LP
        return max(move_time(math.radians(p1 - p0) * 1000.0, math.radians(LP.slew_rate) * 1000.0,
                             math.radians(LP.slew_acc) * 1000.0), move_time(r1 - r0, LP.trolley_v, LP.trolley_a))

    def boom_step(self, tt):
        p0, r0, p1, r1 = self.frm
        LP = self.LP
        self.phi = p0 + profile(p1 - p0, LP.slew_rate, LP.slew_acc, tt)
        self.rr = r0 + profile(r1 - r0, LP.trolley_v, LP.trolley_a, tt)
        return tt >= self.boom_move_time()

    def step(self, t, dt, w):
        LP = self.LP
        x_old = self.x
        tt = t - self.t0
        self.flow = 0.0
        st = self.state
        x_dock, fw_stop = self.docks[self.k]
        if st in ("approach", "reposition"):
            d = x_dock - self.x0
            v, a = (1000.0 * LP.v_drive, 500.0) if d < 0 else (700.0, 350.0)
            self.x = self.x0 + profile(d, v, a, tt)
            if tt >= move_time(d, v, a):
                self.x = x_dock
                phi_t, r_t = self.target(fw_stop)
                self.frm = (self.phi, self.rr, self.unwrap(phi_t, self.phi), r_t)
                self.state, self.t0 = "boom_out", t
        elif st == "boom_out":
            if self.boom_step(tt):
                self.state, self.t0 = "ready", t
        elif st == "ready":
            if w["mode"] == "stop" and w["stop"] == "dock":
                self.state, self.t0 = "camera", t
        elif st == "camera":
            if tt >= 0.5:
                self.state, self.t0 = "spout_down", t
        elif st == "spout_down":
            self.s = profile(LP.spout_stroke, LP.spout_v_speed, 400.0, tt)
            if tt >= move_time(LP.spout_stroke, LP.spout_v_speed, 400.0):
                self.s = LP.spout_stroke
                self.state, self.t0 = "pumping", t
                self.dock_x0 = w["rear"][0]
        if self.state in ("pumping", "spout_up", "boom_back", "follow") and w["kind"] == "reverse":
            self.x = x_dock + (w["rear"][0] - self.dock_x0) + LP.dock_lag * w["a"]
        if self.state == "pumping":
            self.flow = self.q
            if self.mr > 1.0:
                self.mr -= self.q * dt
            else:
                self.tr -= self.q * dt
            phi_t, r_t = self.target(w["funnel"])
            self.phi, self.rr = self.unwrap(phi_t, self.phi), r_t
            if w["level"] + self.q * dt >= w["full"]:
                self.state, self.t0 = "spout_up", t
                self.count += 1
        elif self.state == "spout_up":
            phi_t, r_t = self.target(w["funnel"])
            self.phi, self.rr = self.unwrap(phi_t, self.phi), r_t
            self.s = LP.spout_stroke - profile(LP.spout_stroke, LP.spout_v_speed, 400.0, t - self.t0)
            if t - self.t0 >= move_time(LP.spout_stroke, LP.spout_v_speed, 400.0):
                self.s = 0.0
                self.frm = (self.phi, self.rr, self.unwrap(LP.phi_park, self.phi), LP.r_park)
                self.state, self.t0 = "boom_back", t
        elif self.state == "boom_back":
            if self.boom_step(t - self.t0):
                self.state, self.t0 = "follow", t
        elif self.state == "follow":
            if w["mode"] == "drive" and w["kind"] != "reverse" and w["stop_prev"] == "rev_end":
                self.state, self.t0 = "stopped", t
        elif self.state == "stopped":
            if t - self.t0 > 0.8 and self.k + 1 < len(self.docks):
                self.k += 1
                self.state, self.t0, self.x0 = "reposition", t, self.x
            elif self.k + 1 >= len(self.docks):
                self.state = "parked"
        self.spin += -(self.x - x_old) / P.TIRE_R
        return self.flow

    def release(self, label):
        if label == "dock":
            return self.state == "pumping"
        if label == "rev_end":
            return self.state in ("boom_back", "follow")
        return True

    def busy(self):
        return self.state in self.busy_states

    TEXT = {"approach": "drives along the headland to the next turn", "boom_out": "swings the boom out over the stop point",
            "ready": "boom out, spout raised: waits for the working robot", "camera": "camera sees the target next to the funnel",
            "spout_down": "spout down into the funnel", "pumping": "pumping while both drive along the headland",
            "spout_up": "work tank full: pump off, spout up", "boom_back": "boom swings back",
            "follow": "drives along", "stopped": "stops",
            "reposition": "reverses with the trailer to the turn two passes further", "parked": "parked: field done"}

    def frame(self):
        return {"pose": (self.x, self.y), "spin": self.spin, "boom": (self.phi, self.rr, self.s), "mr": self.mr,
                "tr": self.tr, "flow": self.flow, "state": self.state, "text": self.TEXT[self.state],
                "tank": (self.mr + self.tr, self.capacity("refiller") + self.capacity("trailer")), "count": self.count,
                "stream": None}


class StationRefiller:
    """mobile refiller/stationary/ibc_trailer (1 IBC): staat stil op de kopakker links van het veld, arm naar het
    veld, tuit boven de doklijn; de werkrobot komt met koers -x en stopt met zijn trechter onder de tuit."""
    kind = "station"
    busy_states = ("check", "pumping", "closing")

    def __init__(self, route, scn):
        import sit_params as SP
        import sit_calc as SC
        import stc_params as CP
        import stc_calc as K
        self.c = SP.cfg(1)
        self.q = K.fill_q(*SC.pump_geometry(1)) / 60.0
        self.t_check, self.t_close = CP.t_check, CP.t_close
        xr = station_dock_x()
        fw = local_to_world((xr, P.YS), 90.0, P.funnel_xy)
        self.nozzle_xy = fw
        # stationsstelsel 90 graden gedraaid (lokaal (x, y) -> (-y, x)); tuit lokaal (-reach, mast_y)
        self.placement = ((fw[0] + self.c["mast_y"], fw[1] + self.c["reach"]), 90.0)
        self.ibc = 0.8 * CP.ibc_nominal_l
        self.cap = CP.ibc_nominal_l
        self.state, self.t0, self.flow, self.count = "ready", 0.0, 0.0, 0

    def step(self, t, dt, w):
        tt = t - self.t0
        self.flow = 0.0
        st = self.state
        if st == "ready" and w["mode"] == "stop" and w["stop"] == "station":
            self.state, self.t0 = "check", t
        elif st == "check" and tt >= self.t_check:
            self.state, self.t0 = "pumping", t
        elif st == "pumping":
            self.flow = self.q
            self.ibc -= self.q * dt
            if w["level"] + self.q * dt >= w["full"]:
                self.state, self.t0 = "closing", t
                self.count += 1
        elif st == "closing" and tt >= self.t_close:
            self.state, self.t0 = "done", t
        elif st == "done" and w["mode"] == "drive":
            self.state = "ready"
        return self.flow

    def release(self, label):
        return label != "station" or self.state == "done"

    def busy(self):
        return self.state in self.busy_states

    TEXT = {"ready": "ready (green): arm out, nozzle above the docking line", "check": "radio + RTK: funnel under the nozzle",
            "pumping": "pumping from the IBC (beacon amber)", "closing": "work tank full: pump off, nozzle closes",
            "done": "done: the working robot drives back"}

    def frame(self):
        return {"pose": self.placement[0], "flow": self.flow, "state": self.state, "text": self.TEXT[self.state],
                "tank": (self.ibc, self.cap), "count": self.count, "ibc": self.ibc,
                "stream": self.nozzle_xy if self.flow > 0 else None,
                "beacon": "amber" if self.state in ("check", "pumping", "closing") else "green"}


REFILLERS = {"simple": SimpleRefiller, "liquid": LiquidRefiller, "station": StationRefiller}


# ---------------------------------------------------------------------
# Simulatie
# ---------------------------------------------------------------------
def approach(cur, target, rate, dt):
    d = target - cur
    step = rate * dt
    return target if abs(d) <= step else cur + math.copysign(step, d)


WHEELS = {"RL": (-P.WHEEL_X, -P.AXLE_Y), "RR": (P.WHEEL_X, -P.AXLE_Y),
          "FL": (-P.WHEEL_X, P.AXLE_Y), "FR": (P.WHEEL_X, P.AXLE_Y)}


def wheel_angles(delta):
    length, half = P.WHEELBASE, P.WHEEL_X
    t = math.tan(math.radians(delta))
    return (math.degrees(math.atan2(length * t, length - half * t)),
            math.degrees(math.atan2(length * t, length + half * t)))


def lift_target(piece, rear, psi, geo, lift):
    """0 (werkstand) in een baan als de messen tussen de randen liggen (met voorloop), anders geheven."""
    if piece.kind != "pass":
        return geo.lift_max
    d = piece.tag["dir_y"]
    ky = local_to_world(rear, psi, (0.0, geo.knife_y(lift)))[1]
    u, u_in, u_out = ky * d, (-L if d > 0 else 0.0) * d, (0.0 if d > 0 else -L) * d
    return 0.0 if u_in - P.LOWER_LEAD <= u <= u_out - P.RAISE_LEAD else geo.lift_max


def text_robot(w, mv, piece, order_pos):
    tag = piece.tag
    if w["mode"] == "stop":
        lab = mv.stop
        return {"refill": "stopped on the straight of the U-turn: funnel under the nozzle",
                "dock": "stopped after the first arc: waits for the spout", "rev_end": "end of the reverse",
                "station": "stopped at the station: funnel under the nozzle",
                "steer": "stopped: steers over", "end": "field done, applicator lifted"}.get(lab, lab)
    if piece.kind == "pass":
        if w["lift"] < 1.0:
            return "injects pass %d (%d of %d)" % (tag["pass"], order_pos + 1, P.N_PASSES)
        if w["lift_target"] == 0.0:
            return "pass %d: lowers the applicator at the field edge" % tag["pass"]
        if w["lift"] < w["lift_target"] - 0.5:
            return "pass %d: lifts the applicator at the field edge" % tag["pass"]
        return "pass %d: on the headland, applicator lifted" % tag["pass"]
    a, b = tag.get("turn", (0, 0))
    end = "far headland" if tag.get("end") == "F" else "headland"
    if tag.get("visit"):
        return "%s: to the station and back, then pass %d" % (end, b)
    if piece.kind == "reverse":
        return "%s: reverses along the headland (turn %d -> %d)" % (end, a, b)
    return "%s: turn %d -> %d" % (end, a, b)


def simulate(key, max_t=3000.0):
    """Twee keer rijden: eerst het gewenste tempo per stap, dan met het afgevlakte tempo (vooruit en achteruit
    begrensd, zodat het voor een bocht of het bijvullen al afremt) de frames op videotijd."""
    targets = _simulate(key, max_t)
    return _simulate(key, max_t, smooth_speeds(targets))


def smooth_speeds(targets):
    """Tempo per stap: nergens sneller dan gewenst, en hooguit SPEED_RATE keer sneller of trager per seconde video."""
    s = list(targets)
    for rng in (range(1, len(s)), range(len(s) - 2, -1, -1)):
        for i in rng:
            j = i - 1 if rng.step > 0 else i + 1
            s[i] = min(s[i], s[j] * P.SPEED_RATE ** (P.DT / s[j]))
    return s


def _simulate(key, max_t, speeds=None):
    scn = P.SCENARIOS[key]
    geo = AppGeometry()
    route, order, visits = build_route(key)
    ref = REFILLERS[scn["refiller"]](route, scn)
    dt = P.DT
    w = {"mode": "drive", "stop": None, "stop_prev": None, "level": scn["rx_start"], "full": scn["rx_full"],
         "lift": geo.lift_max, "lift_target": geo.lift_max, "steer": 0.0, "v": 0.0, "a": 0.0}
    mi, s, t, t_stop = 0, 0.0, 0.0, 0.0
    spin = {k: 0.0 for k in WHEELS}
    disc = press = pump = 0.0
    slots = {}
    prev_wheels = None
    applied = 0.0
    # tempo en frames
    speed_s = P.S_TURN
    targets, step = [], 0
    vt, next_tick = 0.0, 0.0
    frames = []
    events = {"refills": [], "stops": [], "standstill": {}}
    order_pos = 0
    refill_t0 = None
    turn_seen = {"R": 0, "F": 0}
    last_turn = None
    while True:
        mv = route.moves[mi]
        if w["mode"] == "drive":
            vmax = mv.v_allowed(s, P.ACCEL)
            v_new = min(w["v"] + P.ACCEL * dt, vmax)
            w["a"] = (v_new - w["v"]) / dt
            w["v"] = v_new
            s += w["v"] * dt
            w["steer"] = approach(w["steer"], mv.steer_at(s + 0.35 * w["v"]), P.STEER_RATE, dt)
            if s >= mv.length - 0.5 or (w["v"] < 1.0 and mv.length - s < 5.0 and s > 10.0):
                s, w["v"], w["a"] = mv.length, 0.0, 0.0
                w["mode"], w["stop"], t_stop = "stop", mv.stop, t
                events["stops"].append((mv.stop, t))
        else:
            w["a"] = 0.0
            events["standstill"][mv.stop] = events["standstill"].get(mv.stop, 0.0) + dt
            nxt = route.moves[mi + 1] if mi + 1 < len(route.moves) else None
            target = nxt.steer_at(0.0) if nxt else 0.0
            w["steer"] = approach(w["steer"], target, P.STEER_RATE, dt)
            if nxt is None:
                if t - t_stop > 0.5:
                    break
            elif abs(w["steer"] - target) < 0.05 and t - t_stop >= 0.3 and ref.release(mv.stop):
                w["stop_prev"] = mv.stop
                mi, s, w["mode"], w["stop"] = mi + 1, 0.0, "drive", None
                mv = route.moves[mi]
        rear, psi = mv.pose(s)
        piece = mv.piece(s)
        w["kind"] = piece.kind
        if piece.kind == "pass" and order_pos < len(order) and order[order_pos] != piece.tag["pass"]:
            order_pos = order.index(piece.tag["pass"])
        if "turn_i" in piece.tag and piece.tag["turn_i"] != last_turn:
            last_turn = piece.tag["turn_i"]
            turn_seen[piece.tag["end"]] += 1
        # applicator
        w["lift_target"] = lift_target(piece, rear, psi, geo, w["lift"])
        w["lift"] = approach(w["lift"], w["lift_target"], P.ACT_SPEED, dt)
        in_soil = w["lift"] < geo.depth
        ds = w["v"] * dt
        rpm = geo.pump_rpm(w["v"]) if in_soil and w["v"] > 0 else 0.0
        if in_soil:
            disc += ds / geo.r_disc
            use = rpm / 60.0 * 10.0 * geo.rows * dt / 1000.0       # 10 ml per omwenteling per kanaal
            w["level"] -= use
            applied += use
            p = piece.tag.get("pass", -1)
            ky = local_to_world(rear, psi, (0.0, geo.knife_y(w["lift"])))[1]
            sp = slots.setdefault(p, [ky, ky, None, None])
            sp[0], sp[1] = min(sp[0], ky), max(sp[1], ky)
        if w["lift"] <= 0.5:
            press += ds / geo.r_press
            p = piece.tag.get("pass")
            if p in slots:
                py = local_to_world(rear, psi, (0.0, geo.press_y(w["lift"])))[1]
                sp = slots[p]
                sp[2] = py if sp[2] is None else min(sp[2], py)
                sp[3] = py if sp[3] is None else max(sp[3], py)
        pump += rpm / 60.0 * 360.0 * dt
        wheels = {k: local_to_world(rear, psi, loc) for k, loc in WHEELS.items()}
        if prev_wheels is not None and w["v"] > 0:
            for k in WHEELS:
                spin[k] += mv.dir * math.hypot(wheels[k][0] - prev_wheels[k][0],
                                               wheels[k][1] - prev_wheels[k][1]) / P.TIRE_R
        prev_wheels = wheels
        w["rear"], w["psi"] = rear, psi
        w["funnel"] = local_to_world(rear, psi, P.funnel_xy)
        flow = ref.step(t, dt, w)
        w["level"] = min(w["full"], w["level"] + flow * dt)
        if flow > 0 and refill_t0 is None:
            refill_t0 = (t, w["level"])
        if flow == 0 and refill_t0 is not None:
            events["refills"].append({"t": refill_t0[0], "pump_s": t - refill_t0[0],
                                      "litres": w["level"] - refill_t0[1]})
            refill_t0 = None

        # tempo: snel in de baan ver van de randen, langzaam in bochten en bij het bijvullen
        n_ref = len(events["refills"])
        if ref.busy() or (w["mode"] == "stop" and mv.stop in ("refill", "dock", "station")):
            target_speed = P.S_REFILL if n_ref < 1 else P.S_REFILL_LATER
            if ref.state == "pumping":
                rest = (w["full"] - w["level"]) / ref.q
                target_speed = max(target_speed, min(P.S_PUMP_MAX, rest / P.PUMP_VIDEO_S))
        elif piece.kind == "pass" and -L < rear[1] < 0.0:
            d = min(abs(rear[1]), abs(rear[1] + L))
            f = max(0.0, min(1.0, (d - P.SLOW_ZONE[0]) / (P.SLOW_ZONE[1] - P.SLOW_ZONE[0])))
            slow = P.S_TURN if min(turn_seen.values()) < 1 else P.S_TURN_LATER
            target_speed = math.exp(math.log(slow) + f * (math.log(P.S_FAST) - math.log(slow)))
        else:
            end = piece.tag.get("end", "R")
            target_speed = P.S_TURN if turn_seen[end] <= 1 else P.S_TURN_LATER
        if speeds is None:
            targets.append(target_speed)
            speed_s = target_speed
        else:
            speed_s = speeds[min(step, len(speeds) - 1)]
        step += 1
        vt += dt / speed_s
        if vt >= next_tick - 1e-12 or not frames:
            frames.append({
                "t": t, "speed": speed_s, "mode": w["mode"], "stop": w["stop"], "rear": rear, "psi": psi,
                "centre": robot_centre(rear, psi), "steer": w["steer"], "spin": dict(spin), "lift": w["lift"],
                "v": w["v"] * mv.dir, "level": w["level"], "rpm": rpm, "disc": disc, "press": press, "pump": pump,
                "applied": applied, "slots": {k: tuple(v) for k, v in slots.items()}, "pass_pos": order_pos,
                "piece": piece.kind, "w_text": text_robot(w, mv, piece, order_pos), "ref": ref.frame(),
                "funnel": w["funnel"], "in_soil": in_soil})
            next_tick += 1.0 / P.VIDEO_FPS
        t += dt
        if t > max_t:
            raise RuntimeError("simulatie loopt niet af: move %d %s %s" % (mi, w["mode"], ref.frame()["state"]))
    if speeds is None:
        return targets
    hold = [dict(frames[0]) for _ in range(int(P.HOLD_START * P.VIDEO_FPS))]
    tail = [dict(frames[-1]) for _ in range(int(P.HOLD_END * P.VIDEO_FPS))]
    frames = hold + frames + tail
    return {"key": key, "scn": scn, "frames": frames, "events": events, "order": order, "visits": visits,
            "route": route, "geo": geo, "ref_kind": scn["refiller"]}


# ---------------------------------------------------------------------
# Camera (zuiver rekenwerk; animate_fld zet hem in FreeCAD)
# ---------------------------------------------------------------------
def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


CAM_OVERVIEW_DIR = (-0.42, -0.62, 0.66)     # van het doel naar het oog: van linksvoor, hoog boven het veld
CAM_CLOSE_R = {"simple": (-0.30, 0.62, 0.72),     # kopakker R: IBC-refiller binnen de bocht, dus vanaf het hek
               "liquid": (0.30, -0.70, 0.65),     # refiller buiten de bocht: vanuit het veld naar de kopakker
               "station": (0.30, -0.70, 0.65)}
CAM_CLOSE_F = (-0.30, 0.70, 0.65)            # verre kopakker: vanaf de andere kant
DIST_OVERVIEW = 44000.0
DIST_CLOSE = 7500.0


def ref_point(f):
    r = f["ref"]
    if r.get("stream"):
        return r["stream"]
    return r["pose"]


def camera_path(run):
    """Per frame (oog, doel): overzicht van het veld bij hoog tempo, dichtbij (robot en refiller) bij laag tempo."""
    frames = run["frames"]
    lo, hi = math.log(P.S_TURN_LATER), math.log(P.S_FAST * 0.8)
    field_c = (px(P.N_PASSES) / 2.0, -L / 2.0 + 2500.0, 0.0)
    out = []
    eye_s = tgt_s = None
    fps = P.VIDEO_FPS
    intro, outro = (P.HOLD_START + 1.0) * fps, len(frames) - (P.HOLD_END + 1.0) * fps
    for i, f in enumerate(frames):
        k = 1.0 - max(0.0, min(1.0, (math.log(f["speed"]) - lo) / (hi - lo)))
        k *= smoothstep((i - intro) / (2.0 * fps)) * (1.0 - smoothstep((i - outro) / (2.0 * fps)))
        k = k * k * (3.0 - 2.0 * k)
        cx, cy = f["centre"]
        rx, ry = ref_point(f)
        near = math.hypot(rx - cx, ry - cy) < 9000.0
        tx, ty = ((cx + rx) / 2.0, (cy + ry) / 2.0) if near else (cx, cy)
        sep = math.hypot(rx - cx, ry - cy) if near else 0.0
        end_r = cy > -L / 2.0
        d_close = _unit(CAM_CLOSE_R[run["ref_kind"]] if end_r else CAM_CLOSE_F)
        dist_close = max(DIST_CLOSE, 0.9 * sep + 5000.0)
        d_over = _unit(CAM_OVERVIEW_DIR)
        over_t = (0.7 * field_c[0] + 0.3 * cx, 0.7 * field_c[1] + 0.3 * cy, 0.0)
        tgt = [over_t[i] + (c - over_t[i]) * k for i, c in enumerate((tx, ty, 400.0))]
        dirv = _unit([d_over[i] + (d_close[i] - d_over[i]) * k for i in range(3)])
        dist = math.exp(math.log(DIST_OVERVIEW) + (math.log(dist_close) - math.log(DIST_OVERVIEW)) * k)
        eye = [tgt[i] + dirv[i] * dist for i in range(3)]
        if eye_s is None:
            eye_s, tgt_s = eye, tgt
        else:
            a = 0.12
            eye_s = [eye_s[i] + (eye[i] - eye_s[i]) * a for i in range(3)]
            tgt_s = [tgt_s[i] + (tgt[i] - tgt_s[i]) * a for i in range(3)]
        out.append((tuple(eye_s), tuple(tgt_s)))
    return out


# ---------------------------------------------------------------------
# Kerngetallen
# ---------------------------------------------------------------------
def work_time(run):
    """Tijd met de messen in de grond (s): de werklengte van alle banen bij werksnelheid."""
    return sum((v[1] - v[0]) for v in run["frames"][-1]["slots"].values()) / P.V_WORK


def summary(run):
    frames, ev = run["frames"], run["events"]
    real = frames[-1]["t"]
    stops = {}
    for lab, _ in ev["stops"]:
        stops[lab] = stops.get(lab, 0) + 1
    return {"scenario": run["key"], "order": run["order"], "station_visits_after_pass":
            [run["order"][i] for i in run["visits"]], "real_time_s": round(real, 1),
            "video_s": round(len(frames) / float(P.VIDEO_FPS), 1), "frames": len(frames),
            "applied_l": round(frames[-1]["applied"], 2), "pass_use_l": round(pass_use_l(), 2),
            "refills": [(round(r["t"], 1), round(r["litres"], 2), round(r["pump_s"], 1)) for r in ev["refills"]],
            "stops": stops, "standstill_s": {k: round(v, 1) for k, v in ev["standstill"].items() if k != "end"},
            "work_s": round(work_time(run), 1),
            "level_end_l": round(frames[-1]["level"], 1),
            "min_level_l": round(min(f["level"] for f in frames), 1),
            "slots_m": {p: round((v[1] - v[0]) / 1000.0, 2) for p, v in sorted(frames[-1]["slots"].items())},
            "pressed_m": {p: round((v[3] - v[2]) / 1000.0, 2) for p, v in sorted(frames[-1]["slots"].items())
                          if v[2] is not None}}


if __name__ == "__main__":
    import json
    for k in (sys.argv[1:] or list(P.SCENARIOS)):
        print(json.dumps(summary(simulate(k)), indent=1))
