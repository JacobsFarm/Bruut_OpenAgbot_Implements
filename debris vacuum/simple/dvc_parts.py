"""Parts of the debris vacuum. Every function returns a Part shape in robot coordinates, in the work pose. The head
frame and castors come from the magnet sweeper (mgs_parts), the toolbar, arms, carrier, king pin and lift actuator
from the push blade (pbl_parts). The nozzle parts are drawn in the lift group frame (work pose); hose_points() maps the
outlet with the lift angle, so the hose is rebuilt per pose.
"""
import math

import Part
from FreeCAD import Vector as V

import dvc_params as P
import pbl_parts as PP
import mgs_parts as MP

box_span = PP.box_span
cyl = PP.cyl
fuse_all = PP.fuse_all
plate_yz = PP.plate_yz

head_frame = MP.head_frame
box_bolts = MP.box_bolts
castor_spacers = MP.castor_spacers
castors = MP.castors
castor_wheels = MP.castor_wheels
castor_bolts = MP.castor_bolts

AX = P.brush_axis
X_IN = P.noz_x - P.end_t                # inside of the end plates
BRG_DZ = 45.0                           # bearing flange bolts at the axis +-45 (z)


def cyl_x(d, yz, x0, x1):
    return cyl(d, (x0, yz[0], yz[1]), (x1, yz[0], yz[1]))


# ---------------------------------------------------------------------
# Nozzle
# ---------------------------------------------------------------------
def hood():
    """Steel 2 mm: rear wall, top, front wall between the end plates; bolt holes for the bracket flanges; outlet hole."""
    y0, y1 = P.noz_y
    z0, z1 = P.noz_z
    t = P.sheet_t
    parts = [box_span((-X_IN, X_IN), (y0, y0 + t), (z0, z1)),
             box_span((-X_IN, X_IN), (y0, y1), (z1 - t, z1)),
             box_span((-X_IN, X_IN), (y1 - t, y1), (z0 + 20.0, z1))]
    s = fuse_all(parts)
    for x, z in MP._box_bolts():
        s = s.cut(cyl(11.0, (x, y0 - 5, z), (x, y0 + 10, z)))
    s = s.cut(cyl(P.outlet_d - 4.0, (0, P.outlet_y, z1 - 10), (0, P.outlet_y, z1 + 10)))
    return s


def end_plates():
    y0, y1 = P.noz_y
    z0, z1 = P.noz_z
    out = []
    for sx in (-1, 1):
        x0 = X_IN if sx > 0 else -P.noz_x
        p = box_span((x0, x0 + P.end_t), (y0, y1), (z0, z1))
        p = p.cut(cyl_x(P.brush_shaft_d + 2.0, AX, x0 - 1, x0 + P.end_t + 1))
        for dz in (-BRG_DZ, BRG_DZ):
            p = p.cut(cyl_x(11.0, (AX[0], AX[1] + dz), x0 - 1, x0 + P.end_t + 1))
        out.append(p)
    return Part.makeCompound(out)


def flaps():
    """Rubber 6 mm: front flap in front of the front wall, rear flap behind the rear wall."""
    y0, y1 = P.noz_y
    front = box_span((-X_IN, X_IN), (y1, y1 + P.flap_t), (P.flap_gap_front, P.noz_z[0] + 60.0))
    rear = box_span((-X_IN, X_IN), (y0 - P.flap_t, y0), (P.flap_gap_rear, P.noz_z[0] + 50.0))
    return Part.makeCompound([front, rear])


def outlet():
    z1 = P.noz_z[1]
    tube = cyl(P.outlet_d, (0, P.outlet_y, z1), (0, P.outlet_y, z1 + P.outlet_h))
    return tube.cut(cyl(P.outlet_d - 4.0, (0, P.outlet_y, z1 - 5), (0, P.outlet_y, z1 + P.outlet_h + 5)))


def bristles():
    L = P.brush_l / 2.0
    return cyl_x(P.brush_d, AX, -L, L).cut(cyl_x(P.brush_core_d, AX, -L - 1, L + 1))


def brush_core():
    """Core tube O60 x 3 with 2 end discs 10 mm on the shaft."""
    L = P.brush_l / 2.0 + 2.0
    di = P.brush_core_d - 6.0
    tube = cyl_x(P.brush_core_d, AX, -L, L).cut(cyl_x(di, AX, -L - 1, L + 1))
    discs = [cyl_x(di, AX, -L, -L + 10.0), cyl_x(di, AX, L - 10.0, L)]
    return fuse_all([tube] + discs).cut(cyl_x(P.brush_shaft_d, AX, -L - 1, L + 1))


def brush_shaft():
    x1 = P.noz_x + P.brg_flange[0] + P.brg_house[1] + 5.0
    return cyl_x(P.brush_shaft_d, AX, -x1 - 40.0, x1)


def bearings():
    ft, fy, fz = P.brg_flange
    out = []
    for sx in (-1, 1):
        x0 = sx * P.noz_x
        fl = box_span(sorted((x0, x0 + sx * ft)), (AX[0] - fy / 2.0, AX[0] + fy / 2.0), (AX[1] - fz / 2.0, AX[1] + fz / 2.0))
        hs = cyl_x(P.brg_house[0], AX, *sorted((x0, x0 + sx * (ft + P.brg_house[1]))))
        b = fl.fuse(hs).cut(cyl_x(P.brush_shaft_d, AX, -900, 900))
        for dz in (-BRG_DZ, BRG_DZ):
            b = b.cut(cyl_x(11.0, (AX[0], AX[1] + dz), -900, 900))
        out.append(b)
    return Part.makeCompound(out)


def bearing_bolts():
    out = []
    for sx in (-1, 1):
        for dz in (-BRG_DZ, BRG_DZ):
            z = AX[1] + dz
            out.append(PP.bolt_axis(10.0, (sx * (P.noz_x + P.brg_flange[0]), AX[0], z), (sx * X_IN, AX[0], z),
                                    17.0, 6.4, 8.4))
    return Part.makeCompound(out)


def gearmotor():
    """Right-angle worm gearmotor on the left shaft end: gearbox 100 x 100 x 100, motor O90 pointing up-back."""
    x0 = -(P.noz_x + P.brg_flange[0] + P.brg_house[1] + 8.0)
    gb = box_span((x0 - 100.0, x0), (AX[0] - 50.0, AX[0] + 50.0), (AX[1] - 50.0, AX[1] + 50.0))
    gb = gb.cut(cyl_x(P.brush_shaft_d + 0.5, AX, x0 - 101, x0 + 1))
    xm = x0 - 50.0
    motor = cyl(P.gm_d, (xm, AX[0], AX[1] + 50.0), (xm, AX[0], AX[1] + 50.0 + P.gm_len - 100.0))
    return fuse_all([gb, motor])


# ---------------------------------------------------------------------
# Bin, cross bars, fan
# ---------------------------------------------------------------------
BAR_Z = (P.upper_beam_top, P.upper_beam_top + P.bar_wh[1])


def cross_bars():
    w, h = P.bar_wh
    out = []
    for sy in (-1, 1):
        y = sy * P.upper_hole_y
        out.append(PP.tube_span((-P.bar_x, P.bar_x), (y - w / 2.0, y + w / 2.0), BAR_Z, 3.0, "x"))
    s = Part.makeCompound(out)
    for x in _bar_bolt_x():
        for sy in (-1, 1):
            s = s.cut(cyl(10.5, (x, sy * P.upper_hole_y, BAR_Z[0] - 1), (x, sy * P.upper_hole_y, BAR_Z[1] + 1)))
    return s


def _bar_bolt_x():
    return [sx * sum(b) / 2.0 for sx in (-1, 1) for b in P.upper_beam_x]


def bar_bolts():
    out = []
    for x in _bar_bolt_x():
        for sy in (-1, 1):
            out.append(PP.bolt_z(10.0, x, sy * P.upper_hole_y, P.upper_beam_top - 40.0, BAR_Z[1]))
    return Part.makeCompound(out)


def pads():
    """PE pads 15 mm under the bin on the cross bars, between the bolts."""
    out = []
    for sy in (-1, 1):
        y = sy * P.upper_hole_y
        for x in (-375.0, 0.0, 375.0):
            out.append(box_span((x - 30.0, x + 30.0), (y - 30.0, y + 30.0), (BAR_Z[1], BAR_Z[1] + P.pad_h)))
    return Part.makeCompound(out)


def bin_body():
    """Bottom, front wall, side walls and lid (aluminium 3 mm); open at the rear (door). Inlet and screen holes."""
    x, (y0, y1), (z0, z1), t = P.bin_x, P.bin_y, P.bin_z, P.bin_t
    outer = box_span((-x, x), (y0, y1), (z0, z1))
    inner = box_span((-x + t, x - t), (y0 - 1, y1 - t), (z0 + t, z1 - t))
    s = outer.cut(inner)
    s = s.cut(cyl(P.hose_d - 12.0 + 1.0, (0, y1 - t - 1, P.inlet_z), (0, y1 + 1, P.inlet_z)))
    s = s.cut(cyl(P.screen_d, (0, P.fan_y, z1 - t - 1), (0, P.fan_y, z1 + 1)))
    return s


def inlet():
    y1 = P.bin_y[1]
    d = P.hose_d - 12.0
    return cyl(d, (0, y1 - P.bin_t, P.inlet_z), (0, y1 + P.inlet_len, P.inlet_z)).cut(
        cyl(d - 6.0, (0, y1 - 10, P.inlet_z), (0, y1 + P.inlet_len + 1, P.inlet_z)))


def door():
    x, (z0, z1), t = P.bin_x, P.bin_z, P.bin_t
    y0 = P.bin_y[0]
    plate = box_span((-x, x), (y0 - t, y0), (z0, z1 - P.door_gap))
    hinge = cyl_x(16.0, (y0 - t - 8.0, z1 - 8.0), -x + 40.0, x - 40.0)
    return fuse_all([plate, hinge])


def screen():
    z1 = P.bin_z[1]
    return cyl(P.screen_d, (0, P.fan_y, z1 - P.bin_t), (0, P.fan_y, z1 - P.bin_t + 1.0))


def fan():
    z1 = P.bin_z[1]
    vol = cyl(P.fan_d, (0, P.fan_y, z1), (0, P.fan_y, z1 + P.fan_h))
    w, h = P.fan_outlet
    duct = box_span((-w / 2.0, w / 2.0), (P.bin_y[0], P.fan_y - P.fan_d / 2.0 + 20.0),
                    (z1 + 20.0, z1 + 20.0 + h))
    return fuse_all([vol, duct])


def fan_motor():
    z = P.bin_z[1] + P.fan_h
    d, h = P.fan_motor
    return cyl(d, (0, P.fan_y, z), (0, P.fan_y, z + h))


# ---------------------------------------------------------------------
# Hose (rebuilt per pose)
# ---------------------------------------------------------------------
def _rot(p, lift_deg):
    a = math.radians(lift_deg)
    dy, dz = p[1] - P.pivot[0], p[2] - P.pivot[1]
    return V(p[0], P.pivot[0] + dy * math.cos(a) - dz * math.sin(a), P.pivot[1] + dy * math.sin(a) + dz * math.cos(a))


def hose_points(lift_deg=0.0):
    """Outlet top, bend over the outlet (both move with the lift group), bend in front of the inlet, inlet stub end."""
    top = P.noz_z[1] + P.outlet_h
    a = _rot((0.0, P.outlet_y, top - 20.0), lift_deg)
    b = _rot((0.0, P.outlet_y, top + 120.0), lift_deg)
    c0 = V(0.0, P.bin_y[1] + P.inlet_len + 60.0, P.inlet_z)
    c = V(0.0, P.bin_y[1] + P.inlet_len - 20.0, P.inlet_z)
    return [a, b, c0, c]


def hose(lift_deg=0.0):
    pts = hose_points(lift_deg)
    d = P.hose_d
    parts = [cyl(d, pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    parts += [Part.makeSphere(d / 2.0, p) for p in pts[1:-1]]
    s = fuse_all(parts)
    inner = [cyl(d - 12.0, pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    inner += [Part.makeSphere(d / 2.0 - 6.0, p) for p in pts[1:-1]]
    return s.cut(fuse_all(inner))


def hose_length(lift_deg=0.0):
    pts = hose_points(lift_deg)
    return sum((pts[i + 1] - pts[i]).Length for i in range(len(pts) - 1))
