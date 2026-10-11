"""One function per part of the mobile refiller (liquid), the trailer and the receiver kit.

Every shape is drawn in robot coordinates (x right, y forward, z up, ground z 0, mm).
- Boom parts are drawn with the boom pointing forward (phi = 0) and the trolley at REF_R; the Slew, Trolley and
  Spout parts in build_mrl move them from there.
- Trailer parts are drawn straight behind the robot (articulation 0); the Trailer part rotates about the hitch pin.
- Receiver-kit parts are drawn in the coordinates of the working robot.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrl_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

REF_R = P.r_park                # trolley radius in which the boom parts are drawn
CX, CY = P.col_xy


# ---------------------------------------------------------------------
# Basic shapes (same style as mrk_parts.py)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_y(d, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def tube_z(od, wall, z0, z1, x, y):
    return cyl_z(od, z0, z1, x, y).cut(cyl_z(od - 2 * wall, z0 - 1, z1 + 1, x, y))


def fuse_all(shapes):
    shapes = [s for s in shapes if s is not None]
    result = shapes[0]
    if len(shapes) > 1:
        result = result.fuse(shapes[1:])
    try:
        result = result.removeSplitter()
    except Exception:
        pass
    return result


def _poly(pts):
    pts = list(pts)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


def poly_yz(points, x0, t):
    """Closed polygon in the y-z plane, (y, z), extruded over +x from x0."""
    return _poly([V(x0, y, z) for (y, z) in points]).extrude(V(t, 0, 0))


def rbox(x, y, z, r):
    """Box with rounded vertical edges (rotomoulded tank)."""
    b = box_span(x, y, z)
    if r <= 0:
        return b
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    return b.makeFillet(r, edges)


def rod_between(p0, p1, d):
    p0, p1 = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (p1 - p0).Length, p0, p1 - p0)


def bar_between(p0, p1, w, h=None, wall=None):
    """Square/rectangular bar or tube (wall) between two points (w across in the horizontal plane, h vertical)."""
    h = w if h is None else h
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    length = d.Length
    b = Part.makeBox(w, length, h, V(-w / 2.0, 0, -h / 2.0))
    if wall:
        b = b.cut(Part.makeBox(w - 2 * wall, length + 2, h - 2 * wall, V(-w / 2.0 + wall, -1, -h / 2.0 + wall)))
    yaw = math.degrees(math.atan2(-d.x, d.y))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    b.rotate(V(0, 0, 0), X, pitch)
    b.rotate(V(0, 0, 0), Z, yaw)
    b.translate(p0)
    return b


def hose(points, od=P.hose_od):
    """Hose / pipe along a polyline, with a ball at every bend."""
    pts = [V(*p) for p in points]
    parts = [Part.makeCylinder(od / 2.0, (b - a).Length, a, b - a) for a, b in zip(pts[:-1], pts[1:])
             if (b - a).Length > 1e-6]
    parts += [Part.makeSphere(od / 2.0, p) for p in pts[1:-1]]
    return fuse_all(parts)


def bolt_down(x, y, z_head, length, d=10.0, af=17.0, k=6.4, nut_m=8.4):
    """Hex bolt with the head on top at z_head (underside of the head), shank down, nut at the end."""
    head = Part.makePolygon([V(x + af / math.sqrt(3) * math.cos(math.radians(a)),
                               y + af / math.sqrt(3) * math.sin(math.radians(a)), z_head) for a in range(0, 361, 60)])
    head = Part.Face(head).extrude(V(0, 0, k))
    shank = cyl_z(d, z_head - length, z_head, x, y)
    return fuse_all([head, shank])


# Tank volume: same rounded-rectangle sections as the shapes
from mrl_calc import tank_sections  # noqa: E402


# ---------------------------------------------------------------------
# Cradle and straps (shared)
# ---------------------------------------------------------------------
def cradle_tubes(ys=P.cradle_y, half=P.cradle_half_len):
    t, w = P.cradle_tube, P.cradle_wall
    out = []
    for y in ys:
        outer = box_span((-half, half), (y - t / 2, y + t / 2), P.cradle_z)
        inner = box_span((-half - 1, half + 1), (y - t / 2 + w, y + t / 2 - w), (P.cradle_z[0] + w, P.cradle_z[1] - w))
        holes = [cyl_z(P.m10_hole, P.cradle_z[0] - 1, P.cradle_z[1] + 1, x, y) for x in P.robot_upper_beam_x[1:3]]
        out.append(outer.cut(inner).cut(holes))
    return Part.makeCompound(out)


def cradle_pads(ys=P.cradle_y, half_x=300.0):
    return Part.makeCompound([box_span((-half_x, half_x), (y - 18.0, y + 18.0), (P.cradle_z[1], P.tank_z0))
                              for y in ys])


def cradle_bolts(ys=P.cradle_y):
    """M10 button-head bolts down through the cradle tube and the upper beam (nut under the beam)."""
    out = []
    for y in ys:
        for x in P.robot_upper_beam_x[1:3]:      # inner beams; the outer ones are under the strap feet
            out.append(bolt_down(x, y, P.cradle_z[1], P.cradle_tube + P.robot_beam + 14.0, k=4.0))
            out.append(cyl_z(17.0, P.robot_upper_beam_z[0] - 8.4, P.robot_upper_beam_z[0], x, y))
    return Part.makeCompound(out)


def straps(hx, top_z, ys=P.cradle_y):
    """Flat steel straps over the tank, with a foot on each end of the cradle tube."""
    t, w = P.strap_t, P.strap_w
    out = []
    for y in ys:
        yy = (y - w / 2.0, y + w / 2.0)
        parts = [box_span((-hx - t, hx + t), yy, (top_z, top_z + t))]
        for s in (-1, 1):
            parts.append(box_span((s * hx, s * (hx + t)), yy, (P.cradle_z[1], top_z + t)))
            parts.append(box_span((s * (hx + t), s * (hx + t + 22.0)), yy, (P.cradle_z[1], P.cradle_z[1] + t)))
        out.append(fuse_all(parts))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Refiller tank
# ---------------------------------------------------------------------
def _refiller_tank(inset=0.0):
    i = inset
    upper = rbox((-P.tank_x + i, P.tank_x - i), (P.tank_y[0] + i, P.tank_y[1] - i),
                 (P.tank_z[0] + i, P.tank_z[1] - i), max(1.0, P.tank_r - i))
    sump = rbox((-P.sump_x + i, P.sump_x - i), (P.sump_y[0] + i, P.sump_y[1] - i),
                (P.sump_z0 + i, P.tank_z[0] + i + (1.0 if i else 20.0)), max(1.0, P.sump_r - i))
    return fuse_all([upper, sump])


def tank_inner():
    return _refiller_tank(P.tank_wall)


def tank_shell():
    return _refiller_tank(0.0).cut(tank_inner())


def fill_cap(x, y, d, h, z0):
    neck = cyl_z(d - 30.0, z0, z0 + h * 0.4, x, y)
    lid = cyl_z(d, z0 + h * 0.4, z0 + h, x, y)
    grips = [box_span((x - d / 2.0 + 10, x + d / 2.0 - 10), (y - 6, y + 6), (z0 + h, z0 + h + 10))]
    return fuse_all([neck, lid] + grips)


def level_sensor(x, y, d, h, z0):
    return fuse_all([cyl_z(d + 20.0, z0, z0 + 12.0, x, y), cyl_z(d, z0 + 12.0, z0 + h, x, y),
                     cyl_z(16.0, z0 + h, z0 + h + 20.0, x, y)])


def tank_fittings():
    cap = fill_cap(P.fill_cap[0], P.fill_cap[1], P.fill_cap[2], P.fill_cap[3], P.tank_z[1])
    vent = fuse_all([cyl_z(20.0, P.tank_z[1], P.tank_z[1] + 50.0, -320.0, -330.0),
                     cyl_x(20.0, -320.0, -280.0, -330.0, P.tank_z[1] + 40.0)])
    return Part.makeCompound([cap, vent])


def tank_level_sensor():
    return level_sensor(*P.level_sensor, z0=P.tank_z[1])


# ---------------------------------------------------------------------
# Suction side: sump outlet, valve, tee, pump inlet; branch to the trailer camlock
# ---------------------------------------------------------------------
TEE = (P.outlet[0], -440.0, P.outlet[2] + 7.0)
PUMP_IN = (P.pump_inlet[2], P.pump_axis[0], P.pump_axis[1])
CAMLOCK_ROBOT = (80.0, P.hitch[1] - 40.0, 455.0)


def suction_hose():
    ox, oy, oz = P.outlet
    pts = [(ox, oy - 0.5, oz), (ox, -400.0, oz), TEE, (ox, PUMP_IN[1], PUMP_IN[2]), PUMP_IN]
    return hose(pts)


def outlet_valve():
    """Electric ball valve on the sump outlet (tank shut-off) and one on the trailer branch at the tee."""
    ox, oy, oz = P.outlet
    s = P.valve_box / 2.0
    v1 = fuse_all([box_span((ox - s, ox + s), (-385.0, -325.0), (oz - s + 2, oz + s + 2)),
                   box_span((ox - 25, ox + 25), (-380.0, -330.0), (oz + s + 2, oz + s + 62))])
    return v1


def trailer_branch():
    tx, ty, tz = TEE
    pts = [TEE, (tx, -620.0, 400.0), (CAMLOCK_ROBOT[0], CAMLOCK_ROBOT[1] + 60.0, CAMLOCK_ROBOT[2]),
           (CAMLOCK_ROBOT[0], CAMLOCK_ROBOT[1], CAMLOCK_ROBOT[2])]
    v2 = box_span((tx - 30, tx + 30), (-560.0, -500.0), (tz + 6.0, tz + 66.0))
    return hose(pts), v2


def camlock(x, y, z, length=40.0):
    return fuse_all([cyl_y(62.0, y - length, y, x, z), cyl_y(80.0, y - length * 0.6, y - length * 0.4, x, z)])


# ---------------------------------------------------------------------
# Pump (hangs under the rear lower beams, axis along x)
# ---------------------------------------------------------------------
def pump_body():
    y, z = P.pump_axis
    motor = cyl_x(P.pump_motor[0], P.pump_motor[1], P.pump_motor[2], y, z)
    fins = cyl_x(P.pump_motor[0] + 8.0, P.pump_motor[1] + 30.0, P.pump_motor[2] - 30.0, y, z).cut(motor)
    head = cyl_x(P.pump_head[0], P.pump_head[1], P.pump_head[2], y, z)
    inlet = cyl_x(P.pump_inlet[0], P.pump_inlet[1], P.pump_inlet[2] - 5.0, y, z)
    outlet = cyl_z(P.pump_inlet[0], z, z + P.pump_head[0] / 2.0 + 30.0, P.pump_outlet_x, y)
    box = box_span((-120.0, -40.0), (y - 40.0, y + 40.0), (z + 50.0, z + 85.0))      # terminal box
    return fuse_all([motor, fins, head, inlet, outlet, box])


PUMP_OUT = (P.pump_outlet_x, P.pump_axis[0], P.pump_axis[1] + P.pump_head[0] / 2.0 + 30.0)


def discharge_hose():
    """From the pump straight up, under the hitch side plates through, into the column (up to the swivel)."""
    x, y, z = PUMP_OUT
    return hose([(x, y, z - 5.0), (x, y, z + 35.0), (CX, CY, z + 70.0), (CX, CY, P.col_z[1] - 10.0)])


def pump_cradle():
    """Floor plate with 2 hangers to the sub plate; feet under motor and volute."""
    y, z = P.pump_axis
    fz = P.pump_floor_z
    floor = box_span(P.pump_cradle_x, (y - 75.0, y + 75.0), fz)
    left = box_span((P.pump_cradle_x[0], P.pump_cradle_x[0] + 8.0), (y - 25.0, y + 25.0), (fz[0], P.sub_plate[2][0]))
    right = box_span((P.pump_cradle_x[1] - 8.0, P.pump_cradle_x[1]), (y - 75.0, y - 30.0), (fz[0], P.sub_plate[2][0]))
    foot_m = box_span((-140.0, 0.0), (y - 35.0, y + 35.0), (fz[1], z - P.pump_motor[0] / 2.0 - 4.5))
    foot_h = box_span((45.0, 95.0), (y - 45.0, y + 45.0), (fz[1], z - P.pump_head[0] / 2.0))
    return fuse_all([floor, left, right, foot_m, foot_h])


# ---------------------------------------------------------------------
# Rear sub-frame and hitch
# ---------------------------------------------------------------------
def sub_plate():
    plate = box_span(*P.sub_plate)
    holes = [cyl_z(P.m10_hole, P.sub_plate[2][0] - 1, P.sub_plate[2][1] + 1, x, y)
             for x in P.sub_bolt_x for y in P.robot_lower_beam_y[:2]]
    holes.append(cyl_z(60.0, P.sub_plate[2][0] - 1, P.sub_plate[2][1] + 1, CX, CY))
    return plate.cut(holes)


def hitch_side_plates():
    hz = P.hitch[2]
    g, t = P.clevis_gap / 2.0, P.clevis_plate_t
    pts = [(-560.0, P.sub_plate[2][0]), (-610.0, P.sub_plate[2][0]), (-770.0, hz + g + t),
           (-770.0, hz - g - t), (-720.0, hz - g - t), (-560.0, 480.0)]
    x0, x1 = P.hitch_side_x
    return Part.makeCompound([poly_yz(pts, x0, x1 - x0), poly_yz(pts, -x1, x1 - x0)])


def clevis_plates():
    hx, hy, hz = P.hitch
    g, t = P.clevis_gap / 2.0, P.clevis_plate_t
    out = []
    for z in ((hz + g, hz + g + t), (hz - g - t, hz - g)):
        plate = box_span((-P.hitch_side_x[0], P.hitch_side_x[0]), (hy - 40.0, -720.0), z)
        out.append(plate.cut(cyl_z(P.hitch_pin_d + 1.0, z[0] - 1, z[1] + 1, hx, hy)))
    return Part.makeCompound(out)


def hitch_pin():
    hx, hy, hz = P.hitch
    top = hz + P.clevis_gap / 2.0 + P.clevis_plate_t
    return fuse_all([cyl_z(P.hitch_pin_d, hz - P.clevis_gap / 2.0 - P.clevis_plate_t - 15.0, top + 8.0, hx, hy),
                     cyl_z(40.0, top + 8.0, top + 16.0, hx, hy)])


def frame_bolts():
    """8 x M10 through column base plate, lower beam and sub plate."""
    out = []
    for x in P.sub_bolt_x:
        for y in P.robot_lower_beam_y[:2]:
            out.append(bolt_down(x, y, P.base_plate[2][1], P.base_plate[2][1] - P.sub_plate[2][0] + 12.0))
            out.append(cyl_z(17.0, P.sub_plate[2][0] - 8.4, P.sub_plate[2][0], x, y))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Column (fixed)
# ---------------------------------------------------------------------
def base_plate():
    plate = box_span(*P.base_plate)
    holes = [cyl_z(P.m10_hole, P.base_plate[2][0] - 1, P.base_plate[2][1] + 1, x, y)
             for x in P.sub_bolt_x for y in P.robot_lower_beam_y[:2]]
    holes.append(cyl_z(60.0, P.base_plate[2][0] - 1, P.base_plate[2][1] + 1, CX, CY))
    return plate.cut(holes)


def column():
    tube = tube_z(P.col_od, P.col_wall, P.col_z[0], P.col_z[1], CX, CY)
    flange = cyl_z(P.col_flange[0], P.col_z[1], P.col_z[1] + P.col_flange[1], CX, CY).cut(
        cyl_z(60.0, P.col_z[1] - 1, P.col_z[1] + P.col_flange[1] + 1, CX, CY))
    r = P.col_od / 2.0
    gl, gh = P.gusset
    z0 = P.col_z[0]
    gussets = []
    for s in (-1, 1):
        tri = _poly([V(0, 0, 0), V(gl, 0, 0), V(0, 0, gh)]).extrude(V(0, P.gusset_t, 0))
        if s < 0:
            tri.rotate(V(0, 0, 0), Z, 180.0)
            tri.translate(V(0, P.gusset_t, 0))
        tri.translate(V(CX + s * (r - 2.0), CY - P.gusset_t / 2.0, z0))
        gussets.append(tri)
    return fuse_all([tube, flange] + gussets)


def slew_drive():
    housing = cyl_z(P.slew_housing[0], P.slew_z0, P.slew_z0 + P.slew_housing[1], CX, CY)
    motor = cyl_y(56.0, CY - 55.0, CY + 55.0, CX + 125.0, P.slew_z0 + 30.0)
    neck = box_span((CX + 80.0, CX + 100.0), (CY - 25.0, CY + 25.0), (P.slew_z0 + 10.0, P.slew_z0 + 50.0))
    return fuse_all([housing, motor, neck])


def control_box():
    return box_span(*P.ctrl_box)


def control_box_bracket():
    x, y, z = P.ctrl_box
    return Part.makeCompound([box_span((-30.0, 30.0), (y[1], CY - P.col_od / 2.0 + 2.0), (zz, zz + 40.0))
                              for zz in (z[0] + 40.0, z[1] - 80.0)]).cut(cyl_z(P.col_od, 0, 2000, CX, CY))


# ---------------------------------------------------------------------
# Boom (rotates with the slew; drawn pointing forward, phi = 0)
# ---------------------------------------------------------------------
def bf(u, v, z):
    """Boom frame (u across, v along the boom from the column axis) -> robot coordinates at phi = 0."""
    return (CX + u, CY + v, z)


def box_uvz(u, v, z):
    return box_span((CX + u[0], CX + u[1]), (CY + v[0], CY + v[1]), z)


def root_plate():
    u, v, t = P.root_plate
    return box_uvz((-u / 2.0, u / 2.0), (-v / 2.0, v / 2.0), (P.boom_z[0] - t, P.boom_z[0]))


def boom_module():
    w, h = P.boom_w, P.boom_h
    body = box_uvz((-w / 2.0, w / 2.0), P.boom_v, P.boom_z)
    slot = box_uvz((w / 2.0 - 4.0, w / 2.0 + 1.0), (P.boom_v[0] + 70.0, P.boom_v[1] - 50.0),
                   (P.boom_z[0] + 30.0, P.boom_z[1] - 30.0))
    return body.cut(slot)


def boom_motor():
    m, length = P.boom_motor
    v = P.boom_v[0] + 35.0
    return fuse_all([box_uvz((-m / 2.0, m / 2.0), (v - m / 2.0, v + m / 2.0), (P.boom_z[1], P.boom_z[1] + length)),
                     cyl_z(30.0, P.boom_z[1] + length, P.boom_z[1] + length + 12.0, CX, CY + v)])


def drag_chain(r):
    """Hose carrier on top of the boom from the root to the trolley at radius r (shape depends on r)."""
    w, h = P.chain
    v0 = P.boom_v[0] + 75.0
    v1 = max(v0 + 20.0, r)
    return box_uvz((-w / 2.0, w / 2.0), (v0, v1), (P.boom_z[1], P.boom_z[1] + h))


# Trolley (moves along the boom): drawn at r = REF_R
def carriage():
    u0 = P.boom_w / 2.0 + P.car_gap
    return box_uvz((u0, u0 + P.car_t), (REF_R - P.car_len / 2.0, REF_R + P.car_len / 2.0), P.boom_z)


def head_plate():
    u = P.head_u
    plate = box_uvz(u, (REF_R + P.camera[1][0] - 10.0, REF_R + P.head_dv), P.head_z)
    top = box_uvz((P.boom_w / 2.0 + P.car_gap, u[1]), (REF_R - 60.0, REF_R + 60.0), (P.boom_z[1], P.boom_z[1] + 8.0))
    return fuse_all([plate, top])


SLEEVE_Z = (1255.0, 1295.0)     # PE sleeve around the spout, at the bottom of the head plate


def spout_sleeve():
    x, y = CX + P.spout_u, CY + REF_R
    ring = tube_z(P.spout_d + 12.0, 4.5, SLEEVE_Z[0], SLEEVE_Z[1], x, y)
    web = box_uvz((P.head_u[1], P.spout_u - P.spout_d / 2.0 - 4.0), (REF_R - 8.0, REF_R + 8.0), SLEEVE_Z)
    return fuse_all([ring, web])


ACT_V = -60.0                   # spout actuator beside the spout (along the boom from the spout axis)
ACT_U = 75.0
ACT_Z = (1150.0, 1350.0)        # body, rod up to the arm on the spout cap


def spout_actuator_body():
    x, y = CX + ACT_U, CY + REF_R + ACT_V
    body = tube_z(P.act_d, 10.0, ACT_Z[0], ACT_Z[1], x, y)
    bracket = box_uvz((P.head_u[1], ACT_U - P.act_d / 2.0 + 2.0), (REF_R + ACT_V - 10.0, REF_R + ACT_V + 10.0),
                      (1300.0, 1340.0))
    return fuse_all([body, bracket])


def camera():
    u, v, z = P.camera
    body = box_uvz(u, (REF_R + v[0], REF_R + v[1]), z)
    lens = cyl_z(22.0, z[0] - 18.0, z[0], CX + sum(u) / 2.0, CY + REF_R + sum(v) / 2.0)
    bracket = box_uvz((P.head_u[1], u[0]), (REF_R + v[0] + 10.0, REF_R + v[1] - 10.0), (z[0] + 10.0, z[1] - 10.0))
    return fuse_all([body, lens, bracket])


# Spout (moves up/down in the trolley): drawn raised (tip at spout_tip_up)
CAP_TOP = P.spout_tip_up + P.spout_len + 10.0
ARM_T = 12.0


def spout():
    x, y = CX + P.spout_u, CY + REF_R
    t0 = P.spout_tip_up
    tube = tube_z(P.spout_d, 3.0, t0 + 20.0, t0 + P.spout_len, x, y)
    nozzle = Part.makeCone(18.0, P.spout_d / 2.0, 20.0, V(x, y, t0), Z).cut(cyl_z(28.0, t0 - 1, t0 + 21, x, y))
    cap = cyl_z(P.spout_d + 6.0, t0 + P.spout_len, CAP_TOP, x, y)
    return fuse_all([tube, nozzle, cap])


SPOUT_HOSE_Z = P.spout_tip_up + 245.0


def spout_inlet():
    x, y = CX + P.spout_u, CY + REF_R
    return fuse_all([cyl_y(40.0, y + P.spout_d / 2.0 - 3.0, y + 60.0, x, SPOUT_HOSE_Z)])


def spout_clamp_rod():
    """Arm on the spout cap and the actuator rod (moves with the spout, slides inside the hollow body)."""
    x, y = CX + ACT_U, CY + REF_R + ACT_V
    arm = box_uvz((ACT_U - 12.0, P.spout_u), (REF_R + ACT_V - 12.0, REF_R + 12.0), (CAP_TOP, CAP_TOP + ARM_T))
    rod = cyl_z(16.0, CAP_TOP - P.spout_stroke - 15.0, CAP_TOP, x, y)
    return fuse_all([arm, rod])


MAST_LEN = 150.0
MAST_Z0 = CAP_TOP + ARM_T


def mast():
    x, y = CX + P.spout_u, CY + REF_R
    z0 = MAST_Z0
    return fuse_all([cyl_z(P.mast_d, z0, z0 + MAST_LEN, x, y), cyl_z(40.0, z0 + MAST_LEN - 10.0, z0 + MAST_LEN + 2.0, x, y)])


def antenna():
    x, y = CX + P.spout_u, CY + REF_R
    z0 = MAST_Z0 + MAST_LEN + 2.0
    stem = cyl_z(P.ant_stem[0], z0, z0 + P.ant_stem[1], x, y)
    dome = cyl_z(P.ant_dome[0], z0 + P.ant_stem[1], z0 + P.ant_stem[1] + P.ant_dome[1] * 0.6, x, y)
    top = Part.makeSphere(P.ant_dome[0] / 2.0, V(x, y, z0 + P.ant_stem[1] + P.ant_dome[1] * 0.6))
    top = top.common(box_span((x - 80, x + 80), (y - 80, y + 80),
                              (z0 + P.ant_stem[1] + P.ant_dome[1] * 0.6, z0 + P.ant_stem[1] + P.ant_dome[1])))
    return fuse_all([stem, dome, top])


ANT_TOP_UP = MAST_Z0 + MAST_LEN + 2.0 + P.ant_stem[1] + P.ant_dome[1]


def spout_hose(s):
    """Hose from the end of the hose carrier to the spout inlet (spout lowered s mm; shape depends on s)."""
    zh = SPOUT_HOSE_Z - s
    p0 = bf(0.0, REF_R + 20.0, P.boom_z[1] + 22.0)
    pts = [p0, bf(0.0, REF_R + 115.0, P.boom_z[1] + 30.0), bf(P.spout_u, REF_R + 115.0, max(zh, P.boom_z[1] + 30.0)),
           bf(P.spout_u, REF_R + 115.0, zh), bf(P.spout_u, REF_R + 60.0, zh)]
    clean = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, clean[-1]) > 1.0:
            clean.append(p)
    return hose(clean, 40.0)


# ---------------------------------------------------------------------
# Trailer (trailer coordinates = robot coordinates at 0 articulation)
# ---------------------------------------------------------------------
def trailer_tank_shell():
    outer = rbox((-P.tr_tank_x, P.tr_tank_x), P.tr_tank_y, (P.tank_z0, P.tank_z0 + P.tr_tank_h), P.tr_tank_r)
    return outer.cut(trailer_tank_inner())


def trailer_tank_inner():
    w = P.tank_wall
    return rbox((-P.tr_tank_x + w, P.tr_tank_x - w), (P.tr_tank_y[0] + w, P.tr_tank_y[1] - w),
                (P.tank_z0 + w, P.tank_z0 + P.tr_tank_h - w), P.tr_tank_r - w)


def trailer_fittings():
    top = P.tank_z0 + P.tr_tank_h
    cap = fill_cap(P.tr_fill_cap[0], P.tr_fill_cap[1], P.tr_fill_cap[2], P.tr_fill_cap[3], top)
    ox, oy, oz = P.tr_outlet
    stub = cyl_y(P.hose_od, oy, oy + 35.0, ox, oz)
    valve = box_span((ox - 30, ox + 30), (oy + 35.0, oy + 95.0), (oz - 30.0, oz + 30.0))
    return Part.makeCompound([cap, stub, valve])


CAMLOCK_TRAILER = (CAMLOCK_ROBOT[0], CAMLOCK_ROBOT[1] - 40.0, CAMLOCK_ROBOT[2])


def trailer_hose():
    ox, oy, oz = P.tr_outlet
    pts = [(ox, oy + 95.0, oz), (ox, oy + 150.0, oz), (170.0, -1330.0, 700.0), (110.0, -1150.0, 560.0),
           (CAMLOCK_TRAILER[0], -990.0, CAMLOCK_TRAILER[2]), CAMLOCK_TRAILER]
    return hose(pts)


def drawbar():
    hx, hy, hz = P.hitch
    t = P.drawbar_tube
    front_y = P.tr_lower_y[2]
    z_tube = P.robot_lower_beam_z[0] - t / 2.0
    nose_y = hy - 180.0
    parts = []
    for s in (-1, 1):
        parts.append(bar_between((s * P.drawbar_rear_x, front_y, z_tube),
                                 (s * 30.0, nose_y - 10.0, hz), t, wall=3.0))
    ring_t = P.eye[1]
    nose = _poly([V(-45.0, nose_y - 40.0, hz - ring_t / 2.0), V(45.0, nose_y - 40.0, hz - ring_t / 2.0),
                  V(20.0, hy - 25.0, hz - ring_t / 2.0), V(-20.0, hy - 25.0, hz - ring_t / 2.0)]).extrude(V(0, 0, ring_t))
    eye = cyl_z(P.eye[0], hz - ring_t / 2.0, hz + ring_t / 2.0, hx, hy)
    body = fuse_all(parts + [nose, eye])
    return body.cut(cyl_z(P.hitch_pin_d + 1.0, hz - 50, hz + 50, hx, hy))


def jack():
    d, (x, y), z = P.jack
    tube = tube_z(d, 4.0, z[0] + 120.0, z[1], x, y)
    inner = cyl_z(d - 12.0, z[0], z[0] + 140.0, x, y)
    foot = cyl_z(120.0, z[0] - 10.0, z[0], x, y)
    crank = fuse_all([cyl_z(14.0, z[1], z[1] + 40.0, x, y), cyl_x(12.0, x, x + 90.0, y, z[1] + 40.0)])
    return fuse_all([tube, inner, foot, crank])


def jack_bracket():
    d, (x, y), z = P.jack
    # from the jack tube to the underside of the front lower beam
    fy = P.tr_lower_y[2] - P.robot_beam / 2.0
    return box_span((x - 35.0, x + 35.0), (y, fy), (560.0, P.robot_lower_beam_z[0])).cut(cyl_z(d, 500, 650, x, y))


# ---------------------------------------------------------------------
# Receiver kit on the working robot
# ---------------------------------------------------------------------
def rx_tank_inner():
    w = P.tank_wall
    return rbox((-P.rx_tank_x + w, P.rx_tank_x - w), (P.rx_tank_y[0] + w, P.rx_tank_y[1] - w),
                (P.tank_z0 + w, P.tank_z0 + P.rx_tank_h - w), P.rx_tank_r - w)


def rx_tank_shell():
    outer = rbox((-P.rx_tank_x, P.rx_tank_x), P.rx_tank_y, (P.tank_z0, P.tank_z0 + P.rx_tank_h), P.rx_tank_r)
    return outer.cut(rx_tank_inner())


RX_TOP = P.tank_z0 + P.rx_tank_h


def funnel():
    x, y = P.funnel_xy
    z0 = RX_TOP + P.funnel_neck
    d0, d1 = P.funnel_d
    w = P.funnel_wall
    outer = Part.makeCone(d1 / 2.0, d0 / 2.0, P.funnel_h, V(x, y, z0), Z)
    inner = Part.makeCone(d1 / 2.0 - w, d0 / 2.0 - w, P.funnel_h + 0.01, V(x, y, z0 + 0.01), Z)
    cone = outer.cut(inner)
    neck = tube_z(d1, w, RX_TOP, z0 + 0.5, x, y)
    flange = cyl_z(d1 + 50.0, RX_TOP, RX_TOP + 6.0, x, y).cut(cyl_z(d1 - 2 * w, RX_TOP - 1, RX_TOP + 7, x, y))
    rim = cyl_z(d0 + 10.0, z0 + P.funnel_h - 8.0, z0 + P.funnel_h, x, y).cut(
        cyl_z(d0 - 2 * w, z0 + P.funnel_h - 9.0, z0 + P.funnel_h + 1.0, x, y))
    return fuse_all([cone, neck, flange, rim])


def strainer():
    x, y = P.funnel_xy
    z = RX_TOP + P.funnel_neck + 10.0
    return cyl_z(P.funnel_d[1] + 18.0, z, z + 2.0, x, y)


def target_plate():
    x, y, s = P.target
    return box_span((x - s / 2.0, x + s / 2.0), (y - s / 2.0, y + s / 2.0), (RX_TOP, RX_TOP + 3.0))


def target_marks():
    """Black squares of the fiducial (border + a 4 x 4 code), slightly proud of the plate."""
    x, y, s = P.target
    c = s / 8.0
    z = (RX_TOP + 3.0, RX_TOP + 3.6)
    code = ((1, 1), (2, 1), (4, 1), (1, 2), (3, 2), (4, 2), (2, 3), (4, 3), (1, 4), (3, 4))
    out = []
    for i in range(8):
        for j in range(8):
            border = i in (1, 6) or j in (1, 6)
            inner = 1 <= i - 1 <= 4 and 1 <= j - 1 <= 4 and (i - 1, j - 1) in code
            if (border and 1 <= i <= 6 and 1 <= j <= 6) or inner:
                out.append(box_span((x - s / 2.0 + i * c, x - s / 2.0 + (i + 1) * c),
                                    (y - s / 2.0 + j * c, y - s / 2.0 + (j + 1) * c), z))
    return fuse_all(out)


def rx_level_sensor():
    return level_sensor(*P.rx_level_sensor, z0=RX_TOP)


def rx_vent():
    x, y, d, h = P.rx_vent
    return fuse_all([cyl_z(d, RX_TOP, RX_TOP + h, x, y), cyl_x(d, x, x + 40.0, y, RX_TOP + h - 10.0)])


# ---------------------------------------------------------------------
# Liquid (animation and mass): inner volume up to a level
# ---------------------------------------------------------------------
def liquid(inner, level_z):
    bb = inner.BoundBox
    if level_z <= bb.ZMin + 0.5:
        return None
    cut = box_span((bb.XMin - 1, bb.XMax + 1), (bb.YMin - 1, bb.YMax + 1), (bb.ZMin - 1, min(level_z, bb.ZMax - 0.5)))
    return inner.common(cut)


def stream(x, y, z0, z1, d=22.0):
    """Liquid jet from the spout tip into the funnel."""
    return Part.makeCone(d / 2.0, d / 2.0 * 0.8, z0 - z1, V(x, y, z1), Z)


def target_cross(x, y, size=60.0, z=0.0, w=4.0, t=0.4):
    return Part.makeCompound([box_span((x - size / 2.0, x + size / 2.0), (y - w / 2.0, y + w / 2.0), (z, z + t)),
                              box_span((x - w / 2.0, x + w / 2.0), (y - size / 2.0, y + size / 2.0), (z, z + t))])
