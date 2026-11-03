"""Parts of the fence inspector. Every function returns a Part shape in robot coordinates. Fixed parts on the mast;
the carriage parts are drawn at the work height (wire_z) and moved in z by build_fin (Carriage sub-Part); the arm
parts are drawn straight out (+x) and swing about the vertical hinge (Arm sub-Part).
"""
import math

import Part
from FreeCAD import Vector as V

import fin_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all

MX, MY = P.mast_xy
HW = P.mast_w / 2.0
X_IN = MX - HW                  # inner face of the mast (plate side)
X_OUT = MX + HW
ZC = P.wire_z                   # carriage / arm / head centre in the work pose


def plate_xz(pts, y0, t):
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, t, 0))


# ---------------------------------------------------------------------
# Fixed: base plate, mast, gussets, screw, bearing blocks, stepper, camera, bolts
# ---------------------------------------------------------------------
def _bolts_xy():
    return [(sum(b) / 2.0, sy * P.hole_y) for b in P.upper_beam_x for sy in (-1, 1)]


def base_plate():
    z0 = P.upper_beam_top
    s = box_span((P.plate_x[0], X_IN), P.plate_y, (z0, z0 + P.plate_t))
    for x, y in _bolts_xy():
        s = s.cut(cyl(10.5, (x, y, z0 - 1), (x, y, z0 + P.plate_t + 1)))
    return s


def plate_bolts():
    z0 = P.upper_beam_top
    return Part.makeCompound([PP.bolt_z(10.0, x, y, z0 - 40.0, z0 + P.plate_t) for x, y in _bolts_xy()])


def mast():
    return tube_span((X_IN, X_OUT), (MY - HW, MY + HW), P.mast_z, P.mast_wall, "z")


def gussets():
    z0 = P.upper_beam_top + P.plate_t
    pts = ((P.plate_x[0] + 60.0, z0), (X_IN, z0), (X_IN, z0 + 180.0))
    return Part.makeCompound([plate_xz(pts, sy * (HW - 4.0) - (P.gusset_t if sy > 0 else 0.0) + (0 if sy > 0 else 0),
                                       P.gusset_t) for sy in (-1, 1)])


def screw():
    return cyl(P.screw_d, (MX, P.screw_y, P.screw_z[0]), (MX, P.screw_y, P.screw_z[1]))


def screw_blocks():
    """2 bearing blocks welded to the back of the mast, and the stepper bracket on top."""
    out = []
    for z0, z1 in ((P.screw_z[0] - 20.0, P.screw_z[0]), (P.screw_z[1], P.screw_z[1] + 20.0)):
        b = box_span((MX - 25.0, MX + 25.0), (P.screw_y - 22.0, MY - HW), (z0, z1))
        out.append(b.cut(cyl(P.screw_d + 1.0, (MX, P.screw_y, z0 - 1), (MX, P.screw_y, z1 + 1))))
    return Part.makeCompound(out)


def stepper():
    sx, sy, sz = P.stepper
    z0 = P.screw_z[1] + 20.0
    return box_span((MX - sx / 2.0, MX + sx / 2.0), (P.screw_y - sy / 2.0, P.screw_y + sy / 2.0), (z0, z0 + sz))


def camera():
    w, d, h = P.cam_box
    z0 = P.mast_z[1]
    body = box_span((MX - w / 2.0, MX + w / 2.0), (MY - d / 2.0 + 20.0, MY + d / 2.0 + 20.0), (z0, z0 + h))
    lens = cyl(40.0, (MX + w / 2.0, MY + 20.0, z0 + h / 2.0), (MX + w / 2.0 + 25.0, MY + 20.0, z0 + h / 2.0))
    return fuse_all([body, lens])


# ---------------------------------------------------------------------
# Carriage (moves in z): C-sleeve open on the plate side, nut block, hinge lug and pin
# ---------------------------------------------------------------------
def carriage():
    g = 2.0                                     # PE glide gap
    t = P.sleeve_t
    z = (ZC - P.sleeve_h / 2.0, ZC + P.sleeve_h / 2.0)
    yo = HW + g + t
    outer = box_span((X_OUT + g, X_OUT + g + t), (-yo, yo), z)
    sides = [box_span((X_IN + 6.0, X_OUT + g + t), (sy * (HW + g), sy * yo), z) if sy > 0 else
             box_span((X_IN + 6.0, X_OUT + g + t), (-yo, -(HW + g)), z) for sy in (-1, 1)]
    nut = box_span((MX - 20.0, MX + 20.0), (P.screw_y - 18.0, -yo), (z[0], z[0] + 50.0))
    nut = nut.cut(cyl(P.screw_d + 0.5, (MX, P.screw_y, z[0] - 1), (MX, P.screw_y, z[0] + 51)))
    hx, hy = P.hinge_xy
    lug = [box_span((X_OUT + g + t, hx + 18.0), (hy - 20.0, hy + 20.0), (z0, z0 + 12.0))
           for z0 in (ZC - P.arm_w / 2.0 - 16.0, ZC + P.arm_w / 2.0 + 4.0)]
    s = fuse_all([outer, nut] + sides + lug)
    return s.cut(cyl(P.hinge_d + 0.5, (hx, hy, ZC - 100), (hx, hy, ZC + 100)))


def hinge_pin():
    hx, hy = P.hinge_xy
    return cyl(P.hinge_d, (hx, hy, ZC - P.arm_w / 2.0 - 22.0), (hx, hy, ZC + P.arm_w / 2.0 + 22.0))


# ---------------------------------------------------------------------
# Arm (swings about the hinge): knuckle, tube, sensor head, bumper
# ---------------------------------------------------------------------
def arm():
    hx, hy = P.hinge_xy
    w = P.arm_w
    knuckle = cyl(34.0, (hx, hy, ZC - w / 2.0 - 2.0), (hx, hy, ZC + w / 2.0 + 2.0))
    tube = tube_span((hx, P.arm_x1), (hy - w / 2.0, hy + w / 2.0), (ZC - w / 2.0, ZC + w / 2.0), 3.0, "x")
    s = fuse_all([knuckle, tube])
    return s.cut(cyl(P.hinge_d + 0.5, (hx, hy, ZC - 100), (hx, hy, ZC + 100)))


def head():
    x0, x1 = P.head_x
    return box_span((x0, x1), (-P.head_y / 2.0, P.head_y / 2.0), (ZC - P.head_z / 2.0, ZC + P.head_z / 2.0))


def bumper():
    """PE nose in front of the head: a wedge that turns the arm back when it touches a post."""
    x0, x1 = P.head_x
    y1 = P.head_y / 2.0
    pts = [V(x0, y1, 0), V(x1, y1, 0), V(x0 + 10.0, y1 + 90.0, 0)]
    w = Part.makePolygon(pts + [pts[0]])
    f = Part.Face(w).extrude(V(0, 0, P.head_z))
    f.translate(V(0, 0, ZC - P.head_z / 2.0))
    return f


# ---------------------------------------------------------------------
# Fence (render only, not part of the implement)
# ---------------------------------------------------------------------
def fence(y=(-2500.0, 3000.0)):
    out = []
    n0 = int(math.ceil(y[0] / P.post_step))
    for i in range(n0, int(y[1] / P.post_step) + 1):
        py = i * P.post_step + 1500.0
        if y[0] < py < y[1]:
            out.append(cyl(P.post_d, (P.post_x, py, -50.0), (P.post_x, py, 1250.0)))
            for z in P.WIRE_Z:
                out.append(box_span((P.wire_x - 5.0, P.post_x - P.post_d / 2.0), (py - 12.0, py + 12.0), (z - 12.0, z + 12.0)))
    for z in P.WIRE_Z:
        out.append(cyl(2 * P.wire_r * 2.0, (P.wire_x, y[0], z), (P.wire_x, y[1], z)))
    return Part.makeCompound(out)
