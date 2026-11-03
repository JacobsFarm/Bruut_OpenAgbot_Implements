"""Parts of the drinking trough check. Mast, base plate, screw, carriage and hinge pin come from the fence inspector
(fin_parts); this file adds the long arm with the sensor head (drawn at the carriage reference height ZC, straight out),
the tank on its cross bars, the pump and the trough for the renders.
"""
import Part
from FreeCAD import Vector as V

import dck_params as P
import pbl_parts as PP
import fin_parts as FP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all
ZC = P.ZC

base_plate = FP.base_plate
plate_bolts = FP.plate_bolts
mast = FP.mast
gussets = FP.gussets
screw = FP.screw
screw_blocks = FP.screw_blocks
stepper = FP.stepper
carriage = FP.carriage
hinge_pin = FP.hinge_pin


# ---------------------------------------------------------------------
# Arm and sensor head
# ---------------------------------------------------------------------
def arm():
    hx, hy = P.hinge_xy
    w = P.arm_w
    knuckle = cyl(34.0, (hx, hy, ZC - w / 2.0 - 2.0), (hx, hy, ZC + w / 2.0 + 2.0))
    tube = tube_span((hx, P.arm_x1), (hy - w / 2.0, hy + w / 2.0), (ZC - w / 2.0, ZC + w / 2.0), 3.0, "x")
    return fuse_all([knuckle, tube]).cut(cyl(P.F.hinge_d + 0.5, (hx, hy, ZC - 100), (hx, hy, ZC + 100)))


def _head_z():
    return ZC - P.arm_w / 2.0 - P.head_h, ZC - P.arm_w / 2.0


def head():
    z0, z1 = _head_z()
    return box_span(P.head_x, (-P.head_y / 2.0, P.head_y / 2.0), (z0, z1))


def sensors():
    """Ultrasonic level sensor and camera lens under the head, looking down."""
    z0, _ = _head_z()
    xc = sum(P.head_x) / 2.0
    us = cyl(P.us_d, (xc + 30.0, -40.0, z0 - P.us_l), (xc + 30.0, -40.0, z0))
    cam = cyl(P.cam_d, (xc - 30.0, 40.0, z0 - 25.0), (xc - 30.0, 40.0, z0))
    return Part.makeCompound([us, cam])


def nozzle():
    z0, _ = _head_z()
    xc = sum(P.head_x) / 2.0
    pipe = cyl(P.nozzle_d, (xc, 30.0, z0 - P.nozzle_l), (xc, 30.0, z0))
    return pipe.cut(cyl(P.nozzle_d - 4.0, (xc, 30.0, z0 - P.nozzle_l - 1), (xc, 30.0, z0 + 1)))


# ---------------------------------------------------------------------
# Tank on the left upper beams
# ---------------------------------------------------------------------
BAR_Z = (P.upper_beam_top, P.upper_beam_top + P.bar_wh[1])
TANK_Z = (BAR_Z[1] + P.pad_h, BAR_Z[1] + P.pad_h + P.tank_h)


def cross_bars():
    w = P.bar_wh[0]
    out = [tube_span(P.bar_x, (sy * P.hole_y - w / 2.0, sy * P.hole_y + w / 2.0), BAR_Z, 3.0, "x") for sy in (-1, 1)]
    s = Part.makeCompound(out)
    for x in P.left_beams_x:
        for sy in (-1, 1):
            s = s.cut(cyl(10.5, (x, sy * P.hole_y, BAR_Z[0] - 1), (x, sy * P.hole_y, BAR_Z[1] + 1)))
    return s


def bar_bolts():
    return Part.makeCompound([PP.bolt_z(10.0, x, sy * P.hole_y, P.upper_beam_top - 40.0, BAR_Z[1])
                              for x in P.left_beams_x for sy in (-1, 1)])


def pads():
    out = []
    for sy in (-1, 1):
        y = sy * P.hole_y
        for x in (-375.0, -100.0, 200.0):
            out.append(box_span((x - 30.0, x + 30.0), (y - 30.0, y + 30.0), (BAR_Z[1], BAR_Z[1] + P.pad_h)))
    return Part.makeCompound(out)


def tank():
    t = P.tank_wall
    outer = box_span(P.tank_x, P.tank_y, TANK_Z)
    inner = box_span((P.tank_x[0] + t, P.tank_x[1] - t), (P.tank_y[0] + t, P.tank_y[1] - t), (TANK_Z[0] + t, TANK_Z[1] - t))
    cap = cyl(P.tank_cap_d, (-95.0, 0.0, TANK_Z[1]), (-95.0, 0.0, TANK_Z[1] + 30.0))
    return fuse_all([outer.cut(inner), cap])


def pump():
    """24 V diaphragm pump on the tank lid, front left (suction through the lid)."""
    w, d, h = P.pump_box
    return box_span((-400.0, -400.0 + w), (200.0, 200.0 + d), (TANK_Z[1], TANK_Z[1] + h))


# ---------------------------------------------------------------------
# Trough and water (render only)
# ---------------------------------------------------------------------
def trough():
    t = P.trough_t
    outer = box_span(P.trough_x, P.trough_y, (0.0, P.trough_h))
    inner = box_span((P.trough_x[0] + t, P.trough_x[1] - t), (P.trough_y[0] + t, P.trough_y[1] - t), (t, P.trough_h + 1))
    return outer.cut(inner)


def water():
    t = P.trough_t
    return box_span((P.trough_x[0] + t, P.trough_x[1] - t), (P.trough_y[0] + t, P.trough_y[1] - t), (t, P.water_z))
