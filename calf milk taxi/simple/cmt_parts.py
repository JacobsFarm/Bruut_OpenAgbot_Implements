"""Parts of the calf milk taxi. Every function returns a Part shape in robot coordinates. The swing arm is drawn parked
(angle 0, along -y from the pivot); build_cmt.py puts it in a sub-Part that rotates about the vertical pivot axis.
"""
import math

import Part
from FreeCAD import Vector as V

import cmt_params as P

X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
TX, TY = P.tank_xy


def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def fuse_all(shapes):
    shapes = [s for s in shapes if s is not None]
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    try:
        return out.removeSplitter()
    except Exception:
        return out


def hex_prism_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    head = hex_prism_z(af, z_head, z_head + k, x, y)
    shank = cyl_z(d, z_nut - m - 4.0, z_head, x, y)
    nut = hex_prism_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))
    return fuse_all([head, shank, nut])


def hose(points, od):
    pts = [V(*p) for p in points]
    parts = [Part.makeCylinder(od / 2.0, (b - a).Length, a, b - a) for a, b in zip(pts[:-1], pts[1:])
             if (b - a).Length > 1e-6]
    parts += [Part.makeSphere(od / 2.0, p) for p in pts[1:-1]]
    return fuse_all(parts)


# ---------------------------------------------------------------------
# Cross tubes, bolts, base plate
# ---------------------------------------------------------------------
BAR_Y = [(sy * P.hole_y - P.bar / 2.0, sy * P.hole_y + P.bar / 2.0) for sy in (-1, 1)]
BOLTS = [(sx * bx, sy * P.hole_y) for sx in (-1, 1) for bx in P.bar_bolt_x for sy in (-1, 1)]


def bars():
    out = []
    for y in BAR_Y:
        o = box_span((-P.bar_x, P.bar_x), y, P.bar_z)
        i = box_span((-P.bar_x - 1, P.bar_x + 1), (y[0] + P.bar_wall, y[1] - P.bar_wall),
                     (P.bar_z[0] + P.bar_wall, P.bar_z[1] - P.bar_wall))
        t = o.cut(i).cut([cyl_z(P.m10_hole, P.bar_z[0] - 1, P.bar_z[1] + 1, bx, by) for (bx, by) in BOLTS
                          if y[0] < by < y[1]])
        out.append(t)
    return Part.makeCompound(out)


def bar_bolts():
    """M10 through plate, cross tube and upper beam (head on the plate)."""
    return Part.makeCompound([bolt_z(x, y, P.plate_z[1], P.upper_beam_z[0]) for (x, y) in BOLTS])


def plate():
    s = box_span((-P.plate_x, P.plate_x), P.plate_y, P.plate_z)
    return s.cut([cyl_z(P.m10_hole, P.plate_z[0] - 1, P.plate_z[1] + 1, x, y) for (x, y) in BOLTS])


# ---------------------------------------------------------------------
# Tank
# ---------------------------------------------------------------------
R_IN = P.tank_d / 2.0
R_JK = R_IN + P.tank_t + P.insul + P.jacket_t
Z_JK0 = P.tank_z0
Z_CONE = Z_JK0 + P.jacket_t + P.insul                     # tip of the inner cone (outside)
Z_CYL = Z_CONE + P.cone_h
Z_TOP = Z_CYL + P.tank_h
LID_Z = (Z_TOP, Z_TOP + P.insul + 2 * P.lid_t)
FEET = [(TX + 200.0 * math.cos(math.radians(a)), TY + 200.0 * math.sin(math.radians(a))) for a in (30, 150, 270)]


def tank_inner():
    """Inner stainless shell: cylinder + conical bottom (outlet at the cone tip)."""
    cyl = cyl_z(P.tank_d + 2 * P.tank_t, Z_CYL, Z_TOP, TX, TY).cut(cyl_z(P.tank_d, Z_CYL - 1, Z_TOP + 1, TX, TY))
    cone_o = Part.makeCone(P.outlet_d / 2.0 + P.tank_t, R_IN + P.tank_t, P.cone_h, V(TX, TY, Z_CONE), Z)
    cone_i = Part.makeCone(P.outlet_d / 2.0, R_IN, P.cone_h, V(TX, TY, Z_CONE + P.tank_t * 1.2), Z)
    cone = cone_o.cut(cone_i).cut(cyl_z(P.outlet_d, Z_CONE - 1, Z_CONE + 10, TX, TY))
    rim = cyl_z(P.tank_d + 2 * P.tank_t + 2 * P.insul + 2.0, Z_TOP - 3.0, Z_TOP, TX, TY).cut(
        cyl_z(P.tank_d, Z_TOP - 4, Z_TOP + 1, TX, TY))
    return fuse_all([cyl, cone, rim])


def insulation():
    o = cyl_z(2 * (R_JK - P.jacket_t), Z_JK0 + P.jacket_t, Z_TOP - 3.0, TX, TY)
    i = cyl_z(P.tank_d + 2 * P.tank_t, Z_CYL, Z_TOP, TX, TY)
    cone = Part.makeCone(P.outlet_d / 2.0 + P.tank_t, R_IN + P.tank_t, P.cone_h, V(TX, TY, Z_CONE), Z)
    return o.cut([i, cone, cyl_z(P.outlet_d + 2 * P.tank_t, Z_JK0, Z_CONE + 1, TX, TY)])


def jacket():
    o = cyl_z(2 * R_JK, Z_JK0, Z_TOP - 3.0, TX, TY)
    i = cyl_z(2 * (R_JK - P.jacket_t), Z_JK0 + P.jacket_t, Z_TOP, TX, TY)
    return o.cut(i).cut(cyl_z(P.outlet_d + 2 * P.tank_t, Z_JK0 - 1, Z_JK0 + 2, TX, TY))


def feet():
    out = []
    for (x, y) in FEET:
        out.append(cyl_z(P.foot_d, P.plate_z[1], Z_JK0, x, y))
        out.append(cyl_z(P.foot_d + 30.0, P.plate_z[1], P.plate_z[1] + 5.0, x, y))
    return fuse_all(out)


def lid():
    o = cyl_z(2 * R_JK, LID_Z[0], LID_Z[1], TX, TY)
    o = o.cut(cyl_z(P.fill_d, LID_Z[0] - 1, LID_Z[1] + 1, TX - 110.0, TY))
    cover = cyl_z(P.fill_d + 30.0, LID_Z[1], LID_Z[1] + 4.0, TX - 110.0, TY)
    knob = cyl_z(30.0, LID_Z[1] + 4.0, LID_Z[1] + 30.0, TX - 110.0, TY)
    return fuse_all([o, cover, knob])


def stirrer_motor():
    d, h = P.stirrer_motor
    return cyl_z(d, LID_Z[1], LID_Z[1] + h, TX + 60.0, TY)


def stirrer():
    """Shaft O12 from the lid down to a paddle just over the cone."""
    L, H, t = P.paddle
    x = TX + 60.0
    shaft = cyl_z(12.0, Z_CYL + 20.0, LID_Z[1], x, TY)
    blade = box_span((x - L / 2.0 + 60.0, x + L / 2.0 - 60.0), (TY - t / 2.0, TY + t / 2.0), (Z_CYL + 15.0, Z_CYL + 15.0 + H))
    return fuse_all([shaft, blade])


def outlet():
    """Outlet pipe O25 from the cone tip down, with a butterfly valve body (drawn as a block)."""
    pipe = cyl_z(P.outlet_d + 2 * P.tank_t, Z_JK0 - 40.0, Z_CONE + 2.0, TX, TY).cut(
        cyl_z(P.outlet_d, Z_JK0 - 41.0, Z_CONE + 3.0, TX, TY))
    valve = box_span((TX - 25.0, TX + 25.0), (TY - 20.0, TY + 20.0), (Z_JK0 - 32.0, Z_JK0 - 8.0))
    return fuse_all([pipe, valve.cut(cyl_z(P.outlet_d, Z_JK0 - 41.0, Z_JK0, TX, TY))])


# ---------------------------------------------------------------------
# Pump, control box
# ---------------------------------------------------------------------
PX, PY = P.pump_xy
PZ = P.plate_z[1] + P.pump_head[0] / 2.0 + 5.0           # rotor axis (x direction)
HEAD_X = (PX - P.pump_head[1] / 2.0, PX + P.pump_head[1] / 2.0)
PORT_IN = (HEAD_X[0] - 15.0, PY + 25.0, PZ)
PORT_OUT = (HEAD_X[0] - 15.0, PY - 25.0, PZ)


def pump():
    head = cyl_x(P.pump_head[0], HEAD_X[0], HEAD_X[1], PY, PZ)
    motor = cyl_x(P.pump_motor[0], HEAD_X[1], HEAD_X[1] + P.pump_motor[1], PY, PZ)
    foot = box_span((HEAD_X[0], HEAD_X[1] + P.pump_motor[1]), (PY - 40.0, PY + 40.0), (P.plate_z[1], P.plate_z[1] + 6.0))
    ports = [cyl_x(26.0, HEAD_X[0] - 15.0, HEAD_X[0] + 1.0, PY + dy, PZ) for dy in (25.0, -25.0)]
    return fuse_all([head, motor, foot] + ports)


def control_box():
    bx, by, bz = P.box
    x, y = P.box_xy
    return box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0, y + by / 2.0), (P.plate_z[1], P.plate_z[1] + bz))


# ---------------------------------------------------------------------
# Pivot post, gearmotor, hoses (fixed)
# ---------------------------------------------------------------------
QX, QY = P.pivot
HOSE_Z = P.plate_z[1] + 25.0                              # under the tank (jacket bottom at 835)
ENTRY_Z = HOSE_Z


def post():
    p = cyl_z(P.post_d, P.plate_z[1], P.post_top, QX, QY).cut(cyl_z(P.post_d - 2 * P.post_wall, P.plate_z[1] + 6,
                                                                     P.post_top + 1, QX, QY))
    flange = cyl_z(140.0, P.plate_z[1], P.plate_z[1] + 8.0, QX, QY).cut(cyl_z(P.post_d - 2 * P.post_wall, P.plate_z[1] - 1,
                                                                             P.plate_z[1] + 9.0, QX, QY))
    p = fuse_all([p, flange])
    hole = Part.makeCylinder((P.hose_od + 4.0) / 2.0, 60.0, V(QX, QY, ENTRY_Z), V(0, -1, 0))
    return p.cut(hole)


def gearmotor():
    gx, gy, gz = P.gm
    body = box_span((QX - gx / 2.0, QX + gx / 2.0), (QY - gy / 2.0, QY + gy / 2.0), (P.post_top, P.post_top + gz))
    motor = cyl_x(70.0, QX + gx / 2.0, QX + gx / 2.0 + 110.0, QY, P.post_top + gz / 2.0)
    body = body.cut(cyl_z(P.hose_od + 6.0, P.post_top - 1, P.post_top + gz + 1, QX, QY))   # hollow output shaft
    return fuse_all([body, motor])


def feed_hose():
    """Tank outlet -> pump inlet; pump outlet -> under the tank -> into the post (up inside the post and the hollow shaft)."""
    a = hose([(TX, TY, Z_JK0 - 40.0), (TX, TY, HOSE_Z), (PORT_IN[0] - 20.0, PORT_IN[1], HOSE_Z),
              (PORT_IN[0] - 20.0, PORT_IN[1], PZ), (PORT_IN[0] + 1.0, PORT_IN[1], PZ)], P.hose_od)
    b = hose([(PORT_OUT[0] + 1.0, PORT_OUT[1], PZ), (PORT_OUT[0] - 60.0, PORT_OUT[1], PZ),
              (PORT_OUT[0] - 60.0, PORT_OUT[1], HOSE_Z), (QX, QY - 70.0, HOSE_Z), (QX, QY, HOSE_Z),
              (QX, QY, P.hub_z[0])], P.hose_od)
    return Part.makeCompound([a, b])


# ---------------------------------------------------------------------
# Swing arm (sub-Part; drawn parked along -y)
# ---------------------------------------------------------------------
TIP = (QX, QY - P.arm_len + 20.0)


def hub():
    return cyl_z(90.0, P.hub_z[0], P.hub_z[1], QX, QY).cut(cyl_z(P.hose_od + 6.0, P.hub_z[0] - 1, P.hub_z[1] + 1, QX, QY))


def arm_tube():
    h = P.arm / 2.0
    o = box_span((QX - h, QX + h), (QY - P.arm_len, QY + h), P.arm_z)
    i = box_span((QX - h + P.arm_wall, QX + h - P.arm_wall), (QY - P.arm_len - 1, QY + h - P.arm_wall),
                 (P.arm_z[0] + P.arm_wall, P.arm_z[1] - P.arm_wall))
    s = o.cut(i)
    return s.cut([cyl_z(P.hose_od + 4.0, P.arm_z[0] - 1, P.arm_z[0] + P.arm_wall + 1, QX, QY),
                  cyl_z(P.nozzle_d + 2.0, P.arm_z[0] - 1, P.arm_z[0] + P.arm_wall + 1, TIP[0], TIP[1]),
                  cyl_z(P.hose_od * 0.6 + 4.0, P.arm_z[1] - P.arm_wall - 1, P.arm_z[1] + 1, QX, QY),
                  cyl_z(P.hose_od * 0.6 + 4.0, P.arm_z[1] - P.arm_wall - 1, P.arm_z[1] + 1, TIP[0], TIP[1])])


def nozzle():
    x, y = TIP
    tube = cyl_z(P.nozzle_d, P.arm_z[0] - P.nozzle_drop, P.arm_z[0] + 1.0, x, y).cut(
        cyl_z(P.nozzle_d - 3.0, P.arm_z[0] - P.nozzle_drop - 1, P.arm_z[0] + 2.0, x, y))
    drip = Part.makeCone(P.nozzle_d / 2.0, 6.0, 25.0, V(x, y, P.arm_z[0] - P.nozzle_drop), V(0, 0, -1))
    return fuse_all([tube, drip])


def reader():
    """RFID reader and a small camera on a bracket beside the nozzle, looking down at the bucket holder."""
    rx, ry, rz = P.rfid
    x, y = TIP
    z1 = P.arm_z[0]
    bracket = box_span((x + P.arm / 2.0, x + P.arm / 2.0 + 5.0), (y - 40.0, y + 40.0), (z1 - 120.0, P.arm_z[1]))
    rf = box_span((x + P.arm / 2.0 + 5.0, x + P.arm / 2.0 + 5.0 + rx), (y - ry / 2.0, y + ry / 2.0), (z1 - 120.0, z1 - 120.0 + rz))
    cam = box_span((x + P.arm / 2.0 + 5.0, x + P.arm / 2.0 + 45.0), (y + 20.0, y + 50.0), (z1 - 60.0, z1 - 25.0))
    return fuse_all([bracket, rf, cam])


def arm_hose():
    """Hose from the hollow shaft over the arm to the nozzle (rides along with the arm)."""
    zt = P.arm_z[1] + P.hose_od / 2.0 + 2.0
    return hose([(QX, QY, P.hub_z[0] + 2.0), (QX, QY, zt), (QX, QY - 60.0, zt), (TIP[0], TIP[1] + 60.0, zt),
                 (TIP[0], TIP[1], zt), (TIP[0], TIP[1], P.arm_z[1] - 2.0)], P.hose_od * 0.6)


# ---------------------------------------------------------------------
# Scene: calf hutch with bucket holder and bucket (images)
# ---------------------------------------------------------------------
def hutch(y, x0=1000.0):
    """Plastic calf hutch 1.4 x 1.1 (front at x0) with a wire front fence and a bucket holder on it."""
    body = box_span((x0 + 600.0, x0 + 2000.0), (y - 600.0, y + 600.0), (0.0, 1250.0))
    door = box_span((x0 + 590.0, x0 + 601.0), (y - 300.0, y + 300.0), (0.0, 950.0))
    body = body.cut(box_span((x0 + 589.0, x0 + 620.0), (y - 300.0, y + 300.0), (0.0, 950.0)))
    fence = []
    for yy in (y - 600.0, y + 600.0):
        fence.append(box_span((x0, x0 + 600.0), (yy - 10.0, yy + 10.0), (0.0, 900.0)))
    fence.append(box_span((x0 - 10.0, x0 + 10.0), (y - 600.0, y + 600.0), (880.0, 900.0)))
    fence.append(box_span((x0 - 10.0, x0 + 10.0), (y - 600.0, y + 600.0), (450.0, 470.0)))
    for yy in range(int(y - 600), int(y + 601), 150):
        fence.append(box_span((x0 - 4.0, x0 + 4.0), (yy - 4.0, yy + 4.0), (0.0, 900.0)))
    return Part.makeCompound([body] + fence), door


def bucket(y, x=None):
    x = P.bucket_xz[0] if x is None else x
    rim = P.bucket_xz[1]
    b = Part.makeCone(110.0, 140.0, 280.0, V(x, y, rim - 280.0), Z)
    b = b.cut(Part.makeCone(107.0, 137.0, 279.0, V(x, y, rim - 278.0), Z))
    teat = cyl_z(30.0, rim - 330.0, rim - 280.0, x + 60.0, y)
    holder = box_span((x - 150.0, x + 110.0), (y - 160.0, y + 160.0), (rim - 120.0, rim - 110.0)).cut(
        cyl_z(240.0, rim - 130.0, rim - 100.0, x, y))
    tag = box_span((x - 150.0, x - 120.0), (y - 30.0, y + 30.0), (rim - 110.0, rim - 105.0))
    return Part.makeCompound([b, teat, holder, tag])
