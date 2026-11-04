"""Parts of the charging robot, in robot coordinates of the charger. The pods are the battery-pack pods (bpk_parts,
drawn on the right side under the beams) moved onto the deck; the contact head, bars and funnel are those of the
charging dock (cdk_parts, drawn in front of a docked robot at the origin) moved back by dock_d. docked_bracket() gives
the dock bracket of the working robot (render and checks only).
"""
import Part
from FreeCAD import Vector as V

import chg_params as P
import pbl_parts as PP
import bpk_parts as BK
import cdk_parts as CK

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all

Z0 = P.upper_beam_top
DECK_Z = Z0 + P.bar[1]
POD_Z = DECK_Z + P.deck_t


def _moved(shape, dx=0.0, dy=0.0, dz=0.0):
    s = shape.copy()
    s.translate(V(dx, dy, dz))
    return s


# ---------------------------------------------------------------------
# Deck
# ---------------------------------------------------------------------
def deck_bars():
    w, t = P.bar
    out = []
    for y in P.bar_y:
        b = box_span(P.bar_x, (y - w / 2, y + w / 2), (Z0, Z0 + t))
        for x in P.upper_bolt_x:
            b = b.cut(cyl(10.5, (x, y, Z0 - 1), (x, y, Z0 + t + 1)))
        out.append(b)
    return Part.makeCompound(out)


def deck_bolts():
    """M10 from under the upper beams up through bar and deck plate."""
    return Part.makeCompound([PP.bolt_z(10.0, x, y, Z0 - 40.0, DECK_Z + P.deck_t)
                              for y in P.bar_y for x in P.upper_bolt_x])


def deck_plate():
    p = box_span(P.deck_x, P.deck_y, (DECK_Z, DECK_Z + P.deck_t))
    for y in P.bar_y:
        for x in P.upper_bolt_x:
            p = p.cut(cyl(10.5, (x, y, DECK_Z - 1), (x, y, DECK_Z + P.deck_t + 1)))
    return p


# ---------------------------------------------------------------------
# Pods (bpk pod of the right side, moved)
# ---------------------------------------------------------------------
def _pod_shift(i):
    return (P.pod_x0 + i * P.pod_pitch - P.B.pod_x[0], 0.0, POD_Z - P.B.pod_z[0])


def pods():
    return Part.makeCompound([_moved(BK.pod_box(1), *_pod_shift(i)) for i in range(P.pods_n)])


def pod_cells():
    return Part.makeCompound([_moved(BK.cells(1), *_pod_shift(i)) for i in range(P.pods_n)] +
                             [_moved(BK.bms(1), *_pod_shift(i)) for i in range(P.pods_n)])


def pod_fittings():
    return Part.makeCompound([_moved(BK.outer_fittings(1), *_pod_shift(i)) for i in range(P.pods_n)])


def straps():
    """2 steel straps over the pods, down to the deck at both ends."""
    w, t = P.strap
    zt = POD_Z + (P.B.pod_z[1] - P.B.pod_z[0])
    x0 = P.pod_x0 - 15.0
    x1 = P.pod_x0 + (P.pods_n - 1) * P.pod_pitch + (P.B.pod_x[1] - P.B.pod_x[0]) + 40.0
    out = []
    for y in P.strap_y:
        ys = (y - w / 2, y + w / 2)
        top = box_span((x0, x1), ys, (zt, zt + t))
        legs = [box_span((x0, x0 + t), ys, (POD_Z, zt)), box_span((x1 - t, x1), ys, (POD_Z, zt))]
        out.append(fuse_all([top] + legs))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# DC/DC charger, fuse box
# ---------------------------------------------------------------------
def dcdc():
    x, y, z = P.dcdc
    return box_span((-x / 2, x / 2), (P.dcdc_y1 - y, P.dcdc_y1), (POD_Z, POD_Z + z))


def fuse_box():
    x, y, z = P.fuse_box
    x0 = P.dcdc[0] / 2 + 20.0
    return box_span((x0, x0 + x), (P.dcdc_y1 - y, P.dcdc_y1), (POD_Z, POD_Z + z))


# ---------------------------------------------------------------------
# Rear contact head
# ---------------------------------------------------------------------
def rear_bracket():
    """Plate 6 mm on the rear face of the rear outer lower beam, top flange over the beam (2 x M10)."""
    y0, y1 = P.rear_beam_y
    zt = P.lower_beam_z[1]
    plate = box_span((-P.bk_x, P.bk_x), (y0 - P.bk_t, y0), (P.bk_z0, zt + P.bk_t))
    flange = box_span((-P.bk_x, P.bk_x), (y0 - P.bk_t, y1), (zt, zt + P.bk_t))
    s = plate.fuse(flange).removeSplitter()
    for x in P.bk_bolt_x:
        s = s.cut(cyl(10.4, (x, (y0 + y1) / 2, zt - 1), (x, (y0 + y1) / 2, zt + P.bk_t + 1)))
    return s


def rear_bracket_bolts():
    y = sum(P.rear_beam_y) / 2.0
    return Part.makeCompound([PP.bolt_z(10.0, x, y, P.lower_beam_z[0], P.lower_beam_z[1] + P.bk_t)
                              for x in P.bk_bolt_x])


def rear_arm():
    hy1 = CK.head_y()[1] - P.dock_d
    return tube_span((-P.arm[0] / 2, P.arm[0] / 2), (hy1, P.rear_beam_y[0] - P.bk_t), P.arm_z, 3.0, "y")


def head():
    return _moved(CK.arm_and_head()[1], dy=-P.dock_d)


def funnel():
    return _moved(CK.funnel(), dy=-P.dock_d)


def bars():
    return _moved(CK.bars(), dy=-P.dock_d)


# ---------------------------------------------------------------------
# Working robot's dock bracket (render / check only)
# ---------------------------------------------------------------------
def docked_bracket():
    parts = [CK.robot_bracket(), CK.bracket_bolts(), CK.pe_carrier(), CK.pads(), CK.springs(), CK.pilot()]
    return [_moved(s, dy=-P.dock_d) for s in parts]
