"""Parts of the heavy-duty motor module and its mower-deck demonstrator. Every function returns a Part shape in robot
coordinates, deck at the middle cutting height (build_hdm moves the deck group with the height step)."""
import math

import Part
from FreeCAD import Vector as V

import hdm_params as P


def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_z(d, z0, z1, x=0.0, y=0.0):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), V(0, 0, 1))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), V(1, 0, 0))


def fuse_all(shapes):
    shapes = list(shapes)
    r = shapes[0].fuse(shapes[1:]) if len(shapes) > 1 else shapes[0]
    try:
        return r.removeSplitter()
    except Exception:
        return r


def hex_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    return fuse_all([hex_z(af, z_head, z_head + k, x, y), cyl_z(d, z_nut - m - 4.0, z_head, x, y),
                     hex_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))])


DT = P.deck_top
SK = P.deck_skirt_bottom
R = P.deck_d / 2.0


# ---------------------------------------------------------------------
# Belly rails and hangers (fixed)
# ---------------------------------------------------------------------
RAIL_BOLTS = [(sx * P.rail_x, y) for sx in (-1, 1) for y in P.robot_lower_beam_y]
FOOT_Z = P.rail_z[0] - P.hanger_foot[2]
LUG_PIN_Z = DT + 60.0                   # pin through the deck lug at the middle step
BAR_Z0 = DT + max(P.height_steps) + 5.0  # bar end stays above the deck top at the highest step


def rails():
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        t = box_span((x - 20.0, x + 20.0), P.rail_y, P.rail_z).cut(
            box_span((x - 17.0, x + 17.0), (P.rail_y[0] + 3.0, P.rail_y[1] - 3.0), (P.rail_z[0] + 3.0, P.rail_z[1] - 3.0)))
        t = t.cut([cyl_z(P.m10_hole, P.rail_z[0] - 1, P.rail_z[1] + 1, bx, by) for (bx, by) in RAIL_BOLTS if bx == x])
        t = t.cut([cyl_z(8.5, P.rail_z[0] - 1, P.rail_z[0] + 4, x, hy + dy) for (hx, hy) in P.hanger_xy if hx == x
                   for dy in (-30.0, 30.0)])
        out.append(t)
    return Part.makeCompound(out)


def rail_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], P.rail_z[0]) for (x, y) in RAIL_BOLTS])


def _bar_x(x):
    """The hanger bar stands just inside the deck lug (towards x 0)."""
    s = 1.0 if x > 0 else -1.0
    return x - s * (P.lug[2] / 2.0 + P.hanger_bar[1] / 2.0)


def hangers():
    fx, fy, ft = P.hanger_foot
    bw, bt = P.hanger_bar
    out = []
    for (x, y) in P.hanger_xy:
        bx = _bar_x(x)
        foot = box_span((x - fx / 2.0, x + fx / 2.0), (y - fy / 2.0, y + fy / 2.0), (FOOT_Z, P.rail_z[0]))
        foot = foot.cut([cyl_z(8.5, FOOT_Z - 1, P.rail_z[0] + 1, x, y + dy) for dy in (-30.0, 30.0)])
        bar = box_span((bx - bt / 2.0, bx + bt / 2.0), (y - bw / 2.0, y + bw / 2.0), (BAR_Z0, FOOT_Z))
        bar = bar.cut([cyl_x(8.5, bx - 10.0, bx + 10.0, y, LUG_PIN_Z + dz) for dz in P.height_steps])
        out.append(fuse_all([foot, bar]))
    return Part.makeCompound(out)


def hanger_bolts():
    out = []
    for (x, y) in P.hanger_xy:
        for dy in (-30.0, 30.0):
            out.append(fuse_all([hex_z(13.0, FOOT_Z - 5.3, FOOT_Z, x, y + dy),
                                 cyl_z(8.0, FOOT_Z, P.rail_z[0] + 9.0, x, y + dy)]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Deck (moves with the height step)
# ---------------------------------------------------------------------
def deck():
    top = cyl_z(P.deck_d, DT - P.deck_t, DT)
    skirt = cyl_z(P.deck_d, SK, DT).cut(cyl_z(P.deck_d - 2 * P.deck_t, SK - 1, DT + 1))
    s = fuse_all([top, skirt])
    cx, cw = P.discharge
    chute = box_span((R - 20.0, R + cx), (-cw / 2.0, cw / 2.0), (SK, DT)).cut(
        box_span((R - 21.0, R + cx + 1.0), (-cw / 2.0 + P.deck_t, cw / 2.0 - P.deck_t), (SK - 1, DT - P.deck_t)))
    s = s.cut(box_span((R - 30.0, R + 5.0), (-cw / 2.0 + P.deck_t, cw / 2.0 - P.deck_t), (SK - 1, DT - P.deck_t)))
    s = fuse_all([s, chute])
    s = s.cut(cyl_z(40.0, DT - 5.0, DT + 5.0))                     # shaft hole
    return s


def lugs():
    lx, ly, lt = P.lug
    out = []
    for (x, y) in P.hanger_xy:
        p = box_span((x - lt / 2.0, x + lt / 2.0), (y - ly / 2.0, y + ly / 2.0), (DT, LUG_PIN_Z + 20.0))
        s = 1.0 if x > 0 else -1.0
        base = box_span((x - s * lt / 2.0, x + s * (lx - lt / 2.0)), (y - ly / 2.0, y + ly / 2.0), (DT, DT + 6.0))
        out.append(fuse_all([p, base]).cut(cyl_x(8.5, x - 30.0, x + 30.0, y, LUG_PIN_Z)))
    return Part.makeCompound(out)


def lug_bolts():
    """M8 through the hanger bar and the lug (head outside, nut inside)."""
    out = []
    for (x, y) in P.hanger_xy:
        s = 1.0 if x > 0 else -1.0
        bx = _bar_x(x)
        x_out = x + s * P.lug[2] / 2.0
        x_in = bx - s * P.hanger_bar[1] / 2.0
        shank = cyl_x(8.0, x_in - s * 10.0, x_out, y, LUG_PIN_Z)
        head = cyl_x(14.0, x_out, x_out + s * 5.3, y, LUG_PIN_Z)
        nut = cyl_x(14.0, x_in - s * 6.8, x_in, y, LUG_PIN_Z).cut(cyl_x(8.0, x_in - s * 7.0, x_in + s * 1.0, y, LUG_PIN_Z))
        out.append(fuse_all([shank, head, nut]))
    return Part.makeCompound(out)


def rollers():
    d, w = P.rollers
    out = []
    for sx in (-1, 1):
        x = sx * 150.0
        y_edge = math.sqrt(R * R - x * x)
        arm = box_span((x - 25.0 - 5.0, x - 25.0), (y_edge - 20.0, P.roller_y + 15.0), (d / 2.0 + 10.0 - 15.0, DT))
        arm2 = box_span((x + 25.0, x + 25.0 + 5.0), (y_edge - 20.0, P.roller_y + 15.0), (d / 2.0 + 10.0 - 15.0, DT))
        top = box_span((x - 30.0, x + 30.0), (y_edge - 20.0, P.roller_y + 15.0), (DT, DT + 5.0))
        wheel = cyl_x(d, x - w / 2.0, x + w / 2.0, P.roller_y, d / 2.0 + 10.0)
        out.append(fuse_all([arm, arm2, top]))
        out.append(wheel)
    return Part.makeCompound(out)


def blade():
    bl, bw, bt = P.blade
    z = P.cut_h
    b = box_span((-bl / 2.0, bl / 2.0), (-bw / 2.0, bw / 2.0), (z - bt / 2.0, z + bt / 2.0))
    boss = cyl_z(P.blade_boss[0], z + bt / 2.0, z + bt / 2.0 + P.blade_boss[1])
    return fuse_all([b, boss])


# ---------------------------------------------------------------------
# Motor module (on the deck)
# ---------------------------------------------------------------------
PX, PY, PT = P.plate
PLATE_Z = (DT, DT + PT)


def receiver():
    """2 dovetail rails along x on the deck top; the plate slides in from the right and a pin locks it."""
    lx, wy, h = P.dovetail
    out = []
    for s in (-1, 1):
        y0 = s * (PY / 2.0)
        base = box_span((-lx / 2.0, lx / 2.0), (y0, y0 + s * wy), (DT, DT + h))
        lip = box_span((-lx / 2.0, lx / 2.0), (y0 - s * 10.0, y0), (PLATE_Z[1], DT + h))
        out.append(fuse_all([base, lip]))
    stop = box_span((-lx / 2.0 - 10.0, -lx / 2.0), (-PY / 2.0 - wy, PY / 2.0 + wy), (DT, DT + h))
    out.append(stop)
    return fuse_all(out)


def interface_plate():
    p = box_span((-PX / 2.0, PX / 2.0), (-PY / 2.0, PY / 2.0), PLATE_Z)
    p = p.cut(cyl_z(P.shaft[0] + 18.0, PLATE_Z[0] - 1, PLATE_Z[1] + 1))
    p = p.cut([cyl_z(8.5, PLATE_Z[0] - 1, PLATE_Z[1] + 1, P.pcd / 2.0 * math.cos(math.radians(45 + 90 * k)),
                     P.pcd / 2.0 * math.sin(math.radians(45 + 90 * k))) for k in range(4)])
    p = p.cut(cyl_z(P.lock_pin[0] + 0.5, PLATE_Z[0] - 1, PLATE_Z[1] + 1, PX / 2.0 - 25.0, 0.0))
    handle = box_span((PX / 2.0 - 10.0, PX / 2.0 + 30.0), (-40.0, 40.0), (PLATE_Z[1], PLATE_Z[1] + 25.0)).cut(
        box_span((PX / 2.0, PX / 2.0 + 20.0), (-30.0, 30.0), (PLATE_Z[1] - 1, PLATE_Z[1] + 26.0)))
    return fuse_all([p, handle])


def lock_pin():
    d, ln = P.lock_pin
    x = PX / 2.0 - 25.0
    body = cyl_z(d, DT - 20.0, DT - 20.0 + ln)
    body.translate(V(x, 0, 0))
    t = Part.makeCylinder(5.0, 60.0, V(x, -30.0, DT - 20.0 + ln), V(0, 1, 0))      # T handle along y
    return fuse_all([body, t])


def adapter_ring():
    d, t = P.ring
    r = cyl_z(d, PLATE_Z[1], PLATE_Z[1] + t).cut(cyl_z(P.motor[0] - 20.0, PLATE_Z[1] - 1, PLATE_Z[1] + t + 1))
    return r.cut([cyl_z(8.5, PLATE_Z[1] - 1, PLATE_Z[1] + t + 1, P.pcd / 2.0 * math.cos(math.radians(45 + 90 * k)),
                        P.pcd / 2.0 * math.sin(math.radians(45 + 90 * k))) for k in range(4)])


MOTOR_Z0 = PLATE_Z[1] + P.ring[1]


def motor():
    d, h = P.motor
    body = cyl_z(d, MOTOR_Z0, MOTOR_Z0 + h)
    fins = [box_span((-d / 2.0 - 5.0, d / 2.0 + 5.0), (-3.0, 3.0), (MOTOR_Z0 + 20.0, MOTOR_Z0 + h - 10.0))]
    cap = cyl_z(d - 30.0, MOTOR_Z0 + h, MOTOR_Z0 + h + 15.0)
    return fuse_all([body, cap] + fins)


def motor_shaft():
    return cyl_z(P.shaft[0], P.cut_h + P.blade[2] / 2.0, MOTOR_Z0 + 5.0)


def ring_bolts():
    out = []
    for k in range(4):
        x = P.pcd / 2.0 * math.cos(math.radians(45 + 90 * k))
        y = P.pcd / 2.0 * math.sin(math.radians(45 + 90 * k))
        out.append(fuse_all([hex_z(13.0, MOTOR_Z0, MOTOR_Z0 + 5.3, x, y), cyl_z(8.0, PLATE_Z[0] + 1.0, MOTOR_Z0, x, y)]))
    return Part.makeCompound(out)


CTRL_Y = -PY / 2.0 - P.dovetail[1] - 10.0 - P.controller_box[1] / 2.0


def controller():
    cx, cy, cz = P.controller_box
    b = box_span((-cx / 2.0, cx / 2.0), (CTRL_Y - cy / 2.0, CTRL_Y + cy / 2.0), (DT, DT + cz))
    glands = [cyl_x(16.0, cx / 2.0, cx / 2.0 + 15.0, CTRL_Y + dy, DT + 30.0) for dy in (-20.0, 20.0)]
    return fuse_all([b] + glands)


def battery_clip():
    bx, by, bz = P.battery_clip
    y = PY / 2.0 + P.dovetail[1] + 10.0 + by / 2.0
    return box_span((-bx / 2.0, bx / 2.0), (y - by / 2.0, y + by / 2.0), (DT, DT + bz))


def cables():
    """Motor phases to the controller, and the 48 V cable from the controller up to the right rail (to the robot)."""
    cx = P.controller_box[0] / 2.0 + 15.0
    pts = [V(cx, CTRL_Y + 20.0, DT + 30.0), V(cx + 40.0, CTRL_Y + 20.0, DT + 30.0), V(P.rail_x - 40.0, CTRL_Y + 20.0,
                                                                                  P.rail_z[0] - 40.0)]
    segs = [Part.makeCylinder(P.cable_d / 2.0, (b - a_).Length, a_, b - a_) for a_, b in zip(pts[:-1], pts[1:])]
    pts2 = [V(cx, CTRL_Y - 20.0, DT + 30.0), V(cx + 20.0, CTRL_Y - 20.0, DT + 30.0), V(P.motor[0] / 2.0 * 0.7,
                                                                                     -P.motor[0] / 2.0 * 0.7,
                                                                                     MOTOR_Z0 + 40.0)]
    segs += [Part.makeCylinder(10.0 / 2.0, (b - a_).Length, a_, b - a_) for a_, b in zip(pts2[:-1], pts2[1:])]
    return Part.makeCompound(segs)


def grass(y0, y1, w=1600.0):
    return box_span((-w / 2.0, w / 2.0), (y0, y1), (-40.0, 0.0))
