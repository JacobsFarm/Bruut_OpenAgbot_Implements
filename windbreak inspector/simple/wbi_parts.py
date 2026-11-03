"""Parts of the windbreak inspector, in robot coordinates. Base plate, mast and gussets come from the fence inspector
(fin_parts); this file adds the extension tube, its bolts and the sensor head, and the row for the renders.
"""
import math

import Part
from FreeCAD import Vector as V

import wbi_params as P
import pbl_parts as PP
import fin_parts as FP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all

base_plate = FP.base_plate
plate_bolts = FP.plate_bolts
mast = FP.mast
gussets = FP.gussets

MX, MY = P.mast_xy
EW = P.ext_w / 2.0


def extension():
    s = tube_span((MX - EW, MX + EW), (MY - EW, MY + EW), (P.mast_top - P.ext_overlap, P.ext_top), 3.0, "z")
    for z in P.ext_bolt_z:
        s = s.cut(cyl(10.5, (MX - 40, MY, z), (MX + 40, MY, z)))
    return s


def ext_bolts():
    hw = P.mast_w / 2.0
    return Part.makeCompound([PP.bolt_axis(10.0, (MX - hw, MY, z), (MX + hw, MY, z), 17.0, 6.4, 8.4)
                              for z in P.ext_bolt_z])


def mast_bolt_holes():
    """The mast gets the same 2 holes (cut in build from the fin mast)."""
    return Part.makeCompound([cyl(10.5, (MX - 40, MY, z), (MX + 40, MY, z)) for z in P.ext_bolt_z])


def head():
    """Aluminium box clamped round the extension, sensors on the +x face."""
    bx, by, bz = P.head_box
    z0 = P.head_z0
    s = box_span((MX - bx / 2.0, MX + bx / 2.0), (MY - by / 2.0, MY + by / 2.0), (z0, z0 + bz))
    return s.cut(box_span((MX - EW - 0.5, MX + EW + 0.5), (MY - EW - 0.5, MY + EW + 0.5), (z0 - 1, P.ext_top + 0.5)))


def lidar():
    """2D lidar on the head, rotation axis along y: the scan plane is x-z (across the row)."""
    z = P.head_z0 + P.head_box[2]
    xc = MX + P.head_box[0] / 2.0 - P.lidar_d / 2.0
    return cyl(P.lidar_d, (xc, MY - P.lidar_h / 2.0, z + P.lidar_d / 2.0), (xc, MY + P.lidar_h / 2.0, z + P.lidar_d / 2.0)) \
        .fuse(box_span((xc - 30.0, xc + 30.0), (MY - 30.0, MY + 30.0), (z, z + 10.0)))


def cameras():
    x0 = MX + P.head_box[0] / 2.0
    out = [cyl(P.lens_d, (x0, MY, z), (x0 + 25.0, MY, z)) for z in P.stereo_z]
    zc = P.head_z0 + P.head_box[2] - 45.0
    a = math.radians(P.cam_up_deg)
    x1 = x0 + P.lens_d / 2.0 * math.sin(a) + 1.0        # tilted lens clear of the face
    out.append(cyl(P.lens_d, (x1, MY + 70.0, zc), (x1 + 25.0 * math.cos(a), MY + 70.0, zc + 25.0 * math.sin(a))))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Row (render only)
# ---------------------------------------------------------------------
def hedge(y=(-1600.0, 2600.0)):
    return box_span((P.row_x - 200.0, P.row_x + 500.0), y, (0.0, 1900.0))


def trees(y=(-1600.0, 2600.0)):
    out = []
    i = 0
    yy = y[0] + 600.0
    while yy < y[1]:
        h = 3200.0 + 900.0 * (i % 3)
        out.append(cyl(180.0, (P.row_x + 250.0, yy, 0.0), (P.row_x + 250.0, yy, h - 900.0)))
        out.append(Part.makeSphere(700.0 + 100.0 * (i % 2), V(P.row_x + 250.0, yy, h - 500.0)))
        yy += P.tree_step
        i += 1
    return out
