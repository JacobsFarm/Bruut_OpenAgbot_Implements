"""Parts of the soil moisture sensor placer that are not the soil sampler's: gripper, sensors, magazine star, its shaft,
cantilever plate and drive. Every function returns a Part shape in robot coordinates; the gripper is drawn at the
soil sampler's park carriage height (build_smp moves it with the carriage), the star with the index fork at +y.
"""
import math

import Part
from FreeCAD import Vector as V

import smp_params as P
import ssa_parts as AG

A = P.A
box_span = AG.box_span
cyl = AG.cyl
fuse_all = AG.fuse_all
bolt_z = AG.bolt_z
PARK_C = AG.PARK_C                  # carriage bottom of the soil sampler's park pose (the carriage part is drawn there)
GX, GY = 0.0, P.probe_y
MX, MY = P.mag_c


# ---------------------------------------------------------------------
# Gripper on the carriage (drawn at PARK_C, moves with the carriage)
# ---------------------------------------------------------------------
def gripper():
    bx, by, bz = P.grip_box
    c = PARK_C
    body = box_span((GX - bx / 2.0, GX + bx / 2.0), (GY - by / 2.0, GY + by / 2.0), (c - bz, c))
    flange = box_span((GX - 45.0, GX + 45.0), (GY - 35.0, GY + 35.0), (c - 6.0, c))
    return fuse_all([body, flange])


def jaws(closed=True):
    jx, jy, jl = P.jaw
    c = PARK_C - P.grip_box[2]
    gap = P.knob[0] / 2.0 + (0.0 if closed else P.jaw_open)
    out = []
    for s in (-1, 1):
        x0 = GX + s * gap
        x1 = x0 + s * jx
        out.append(box_span((min(x0, x1), max(x0, x1)), (GY - jy / 2.0, GY + jy / 2.0), (c - jl, c)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Sensor (local: cap bottom at z 0, axis at x 0, y 0)
# ---------------------------------------------------------------------
def sensor_local():
    kd, kh = P.knob
    cd, ch = P.cap
    sd, sl = P.stem
    stem = cyl(sd, (0, 0, -(sl - P.cone_h)), (0, 0, 0))
    cone = Part.makeCone(sd / 2.0, 1.0, P.cone_h, V(0, 0, -(sl - P.cone_h)), V(0, 0, -1))
    cap = cyl(cd, (0, 0, 0), (0, 0, ch))
    kn = cyl(kd, (0, 0, ch), (0, 0, ch + kh))
    rings = [cyl(P.ring[0], (0, 0, -z - P.ring[1] / 2.0), (0, 0, -z + P.ring[1] / 2.0)) for z in P.ring_z]
    return fuse_all([stem, cone, cap, kn] + rings)


def sensor_at(x, y, cap_bottom_z):
    s = sensor_local()
    s.translate(V(x, y, cap_bottom_z))
    return s


def sensor_held(cap_bottom_z=None):
    """The sensor in the gripper at the park carriage height (moves with the carriage)."""
    z = PARK_C - P.grip_dz - P.knob[1] - P.cap[1] if cap_bottom_z is None else cap_bottom_z
    return sensor_at(GX, GY, z)


def _index_angle(i):
    return math.radians(90.0 + 360.0 * i / P.n_sensors)


def sensors_in_magazine(skip=()):
    out = []
    for i in range(P.n_sensors):
        if i in skip:
            continue
        a = _index_angle(i)
        out.append(sensor_at(MX + P.mag_r * math.cos(a), MY + P.mag_r * math.sin(a), P.arm_top))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Magazine star, shaft, cantilever plate, drive
# ---------------------------------------------------------------------
def star():
    z0, z1 = P.arm_top - P.arm_t, P.arm_top
    parts = [cyl(P.hub_d, (MX, MY, z0 - 20.0), (MX, MY, z1))]
    for i in range(P.n_sensors):
        a = _index_angle(i)
        arm = box_span((0.0, P.arm_len), (-P.arm_w / 2.0, P.arm_w / 2.0), (z0, z1))
        arm = arm.cut(box_span((P.mag_r, P.arm_len + 1.0), (-P.slot_w / 2.0, P.slot_w / 2.0), (z0 - 1, z1 + 1)))
        arm = arm.cut(cyl(P.slot_w, (P.mag_r, 0, z0 - 1), (P.mag_r, 0, z1 + 1)))
        arm.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(a))
        arm.translate(V(MX, MY, 0))
        parts.append(arm)
    s = fuse_all(parts)
    return s.cut(cyl(P.shaft_d, (MX, MY, z0 - 25.0), (MX, MY, z1 + 1)))


PLATE_Z = (P.bridge_z[1], P.bridge_z[1] + P.plate[2])


def shaft():
    return cyl(P.shaft_d, (MX, MY, P.arm_top - P.arm_t - 18.0), (MX, MY, PLATE_Z[1] + 30.0))


def mag_plate():
    (x0, x1), (y0, y1), t = P.plate
    pl = box_span((x0, x1), (y0, y1), PLATE_Z)
    pl = pl.cut(cyl(P.shaft_d + 0.5, (MX, MY, PLATE_Z[0] - 1), (MX, MY, PLATE_Z[1] + 1)))
    for x in (-35.0, 35.0):
        pl = pl.cut(cyl(8.4, (x, -380.0, PLATE_Z[0] - 1), (x, -380.0, PLATE_Z[1] + 1)))
    return pl


def plate_bolts():
    """2 x M8 through the plate and the rear bridge (nut under the bridge)."""
    return Part.makeCompound([bolt_z(8.0, x, -380.0, PLATE_Z[1], P.bridge_z[0], head=13.0, k=5.3, m=6.8)
                              for x in (-35.0, 35.0)])


def mag_drive():
    """Flange bearing on the plate, a lower bearing on a hanger under it, NEMA17 + 5:1 gearbox on top."""
    hole = cyl(P.shaft_d + 0.5, (MX, MY, 0), (MX, MY, 2000))
    z = PLATE_Z[1]
    bearing = box_span((MX - 45.0, MX + 45.0), (MY - 20.0, MY + 20.0), (z, z + 12.0)).fuse(
        cyl(40.0, (MX, MY, z + 12.0), (MX, MY, z + 30.0))).cut(hole)
    a, L = P.mag_motor
    coupler = cyl(25.0, (MX, MY, z + 30.0), (MX, MY, z + 70.0))
    motor = box_span((MX - a / 2.0, MX + a / 2.0), (MY - a / 2.0, MY + a / 2.0), (z + 70.0, z + 110.0 + L))
    under = box_span((MX - 30.0, MX + 30.0), (MY - 20.0, MY + 20.0), (PLATE_Z[0] - 12.0, PLATE_Z[0])).cut(hole)
    return Part.makeCompound([bearing, coupler, motor, under])


# ---------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------
def grass(y0, y1, x=(-1200.0, 1200.0)):
    return box_span(x, (y0, y1), (-40.0, 0.0))
