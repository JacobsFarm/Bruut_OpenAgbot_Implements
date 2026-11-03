"""Parts of the biostimulant sprayer that are not the spot sprayer's: weather mast, control-box bolts that also hold
the mast foot, aerator (air pump, hose, down-tube, diffuser ring). Every function returns a Part shape in robot
coordinates. Everything else comes from ssp_parts (imported) in build_bss.py.
"""
import math

import Part
from FreeCAD import Vector as V

import bss_params as P
import ssp_parts as SG

S = P.S
box_span = SG.box_span
cyl_z = SG.cyl_z
cyl_y = SG.cyl_y
fuse_all = SG.fuse_all
bolt_z = SG.bolt_z
hose = SG.hose
square_tube_z = SG.square_tube_z

BASE_TOP = S.robot_lower_beam_z[1] + S.box_base[2]          # 663: top of the control-box base plate
FOOT_TOP = BASE_TOP + P.mast_foot[2]
MX, MY = P.mast_xy
FOOT_BOLTS = [(x, y) for x in S.box_bolt_x if x > 0 for y in S.robot_lower_beam_y[:2]]


# ---------------------------------------------------------------------
# Weather mast
# ---------------------------------------------------------------------
def mast_foot():
    (x0, x1), (y0, y1), t = P.mast_foot
    f = box_span((x0, x1), (y0, y1), (BASE_TOP, FOOT_TOP))
    return f.cut([cyl_z(P.m10_hole, BASE_TOP - 1, FOOT_TOP + 1, x, y) for (x, y) in FOOT_BOLTS])


def mast_tube():
    t = square_tube_z(FOOT_TOP, P.mast_top_z, MX, MY, P.mast, P.mast_wall)
    cap = box_span((MX - P.mast / 2.0, MX + P.mast / 2.0), (MY - P.mast / 2.0, MY + P.mast / 2.0),
                   (P.mast_top_z, P.mast_top_z + 4.0))
    return fuse_all([t, cap])


def braces():
    """2 round bars from the foot plate (front and rear) to the mast."""
    out = []
    for y in P.brace_y:
        dy = MY - y
        p0 = V(MX, y, FOOT_TOP)
        p1 = V(MX, MY - math.copysign(P.mast / 2.0, dy), P.brace_top_z)
        out.append(Part.makeCylinder(P.brace_d / 2.0, (p1 - p0).Length, p0, p1 - p0))
    return Part.makeCompound(out)


def weather_sensor():
    d, h = P.sensor
    z0 = P.mast_top_z + 4.0
    adapter = cyl_z(30.0, z0, z0 + P.sensor_arm, MX, MY)
    zb = z0 + P.sensor_arm
    body = cyl_z(d * 0.6, zb, zb + h * 0.45, MX, MY)
    head = cyl_z(d, zb + h * 0.45, zb + h * 0.6, MX, MY)
    posts = [cyl_z(8.0, zb + h * 0.6, zb + h * 0.9, MX + 50.0 * math.cos(a), MY + 50.0 * math.sin(a))
             for a in (0.0, 2.094, 4.189)]
    top = cyl_z(d, zb + h * 0.9, zb + h, MX, MY)
    return fuse_all([adapter, body, head, top] + posts)


def box_bolts():
    """The 4 control-box bolts of the spot sprayer; the 2 on the right also clamp the mast foot (longer)."""
    out = []
    for x in S.box_bolt_x:
        for y in S.robot_lower_beam_y[:2]:
            out.append(bolt_z(x, y, FOOT_TOP if x > 0 else BASE_TOP, S.robot_lower_beam_z[0]))
    return Part.makeCompound(out)


def sensor_cable():
    """Cable from the sensor down the mast and along the base plate to the control box gland side."""
    return hose([(MX - P.mast / 2.0 - 5.0, MY, P.mast_top_z), (MX - P.mast / 2.0 - 5.0, MY, FOOT_TOP + 10.0),
                 (MX - P.mast / 2.0 - 5.0, S.box_y[0] - 8.0, FOOT_TOP + 10.0)], od=7.0)


# ---------------------------------------------------------------------
# Aerator
# ---------------------------------------------------------------------
STRAP_TOP = S.tank_z[1] + S.strap_t


def air_pump():
    x, y = P.air_pump_xy
    bx, by, bz = P.air_pump_box
    body = box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0, y + by / 2.0), (STRAP_TOP + 6.0, STRAP_TOP + bz))
    clamp = box_span((x - bx / 2.0 - 10.0, x + bx / 2.0 + 10.0), (y - by / 2.0, y + by / 2.0),
                     (STRAP_TOP, STRAP_TOP + 6.0))
    nipple = cyl_y(10.0, y + by / 2.0, y + by / 2.0 + 15.0, x + 30.0, STRAP_TOP + 40.0)
    return fuse_all([body, clamp, nipple])


def air_bulkhead():
    x, y = P.air_inlet_xy
    z0 = S.tank_z[1]
    return fuse_all([cyl_z(30.0, z0, z0 + 12.0, x, y), cyl_z(14.0, z0 + 12.0, z0 + 30.0, x, y)])


def air_hose():
    x, y = P.air_pump_xy
    by = P.air_pump_box[1]
    xi, yi = P.air_inlet_xy
    z = STRAP_TOP + 40.0
    return hose([(x + 30.0, y + by / 2.0 + 14.0, z), (x + 30.0, yi - 30.0, z), (xi, yi - 30.0, z),
                 (xi, yi, z), (xi, yi, S.tank_z[1] + 29.0)], od=P.air_hose_d)


def diffuser():
    """Down-tube from the bulkhead to the floor and a ring O300 with holes, 12 mm above the tank floor."""
    xi, yi = P.air_inlet_xy
    cx, cy = P.diffuser_xy
    z_floor = S.tank_z[0] + S.tank_wall
    zr = z_floor + 12.0 + P.diffuser_d / 2.0
    tube = cyl_z(12.0, zr, S.tank_z[1] + 12.0, xi, yi)
    ring = Part.makeTorus(P.diffuser_r, P.diffuser_d / 2.0, V(cx, cy, zr))
    feed = SG.rod_between((xi, yi, zr), (cx, cy - P.diffuser_r, zr), 12.0)
    feet = [cyl_z(10.0, z_floor, zr, cx + P.diffuser_r * math.cos(a), cy + P.diffuser_r * math.sin(a))
            for a in (0.5, 2.6, 4.7)]
    return fuse_all([tube, ring, feed] + feet)
