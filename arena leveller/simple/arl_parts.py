"""Parts of the riding arena leveller. Every function returns a Part shape in robot coordinates in the work pose (roller
on the surface). The frame weldment, mount and actuator are the grassland harrow's (gha_parts); build_arl.py puts the
frame and the new tools in one sub-Part that turns about the pivot axis.
"""
import math

import Part
from FreeCAD import Vector as V

import arl_params as P
import gha_parts as HG

box_span = HG.box_span
cyl = HG.cyl
tube_span = HG.tube_span
fuse_all = HG.fuse_all
plate_yz = HG.plate_yz
bolt_axis = HG.bolt_axis

BAR_F = (P.bar_y[0] - 20.0, P.bar_y[0] + 20.0)            # front tine bar y (-1190 .. -1150)
BAR_R = (P.bar_y[1] - 20.0, P.bar_y[1] + 20.0)            # rear tine bar y (-1340 .. -1300)
BZ = P.bar_z
TINE_TOP = BZ[1] + 44.0
KINK_Z = 100.0


# ---------------------------------------------------------------------
# Rigid loosening tines on the front face of the front bar
# ---------------------------------------------------------------------
def _tine_pts():
    t = P.tine_bar[1]
    y0 = BAR_F[1]
    dy = (KINK_Z + P.tine_depth) * math.tan(math.radians(P.tine_rake))
    return [(y0, TINE_TOP), (y0 + t, TINE_TOP), (y0 + t, KINK_Z), (y0 + t + dy, -P.tine_depth),
            (y0 + dy, -P.tine_depth), (y0, KINK_Z)]


def tine(x):
    w = P.tine_bar[0]
    return plate_yz(_tine_pts(), x - w / 2.0, w)


def tines():
    s = clamp_holes(Part.makeCompound([tine(x) for x in P.tine_x()]))
    for x in P.tine_x():                    # transport hole pair, 50 mm lower in the shank
        for z in (BZ[0] - 12.0, BZ[1] + 17.0):
            zz = z - P.transport_dz
            s = s.cut(cyl(10.4, (x, BAR_F[1] - 1.0, zz), (x, BAR_F[1] + P.tine_bar[1] + 1.0, zz)))
    return s


def points():
    """Reversible hardened points (40 x 14 x 90) on the lower end of the shanks."""
    t = P.tine_bar[1]
    y0 = BAR_F[1]
    a = math.radians(P.tine_rake)
    dy = (KINK_Z + P.tine_depth) * math.tan(a)
    zt = -P.tine_depth
    L = P.point_len
    pts = [(y0 + t + dy, zt), (y0 + t + dy - L * math.sin(a), zt + L * math.cos(a)),
           (y0 + t + dy - L * math.sin(a) + 3.0, zt + L * math.cos(a)), (y0 + t + dy + 3.0, zt - 2.0)]
    return Part.makeCompound([plate_yz(pts, x - P.tine_bar[0] / 2.0 - 1.0, P.tine_bar[0] + 2.0) for x in P.tine_x()])


def tine_clamps():
    """Clamp plate behind the bar and 2 x M10 along y above and below the bar, through the shank."""
    cx, ct, cz = P.clamp_plate
    out = []
    for x in P.tine_x():
        out.append(box_span((x - cx / 2.0, x + cx / 2.0), (BAR_F[0] - ct, BAR_F[0]), (BZ[0] - 22.0, TINE_TOP)))
    return clamp_holes(Part.makeCompound(out))


def frame():
    """The grassland harrow's weldment with 3 extra holes O10.4 through the rear tine bar for the board straps."""
    s = HG.harrow_frame()
    return s.cut([cyl(10.4, (x, BAR_R[0] - 5.0, BZ[0] + 20.0), (x, BAR_R[1] + 5.0, BZ[0] + 20.0)) for x in P.strap_x])


def tine_bolts():
    out = []
    for x in P.tine_x():
        for z in (BZ[0] - 12.0, BZ[1] + 17.0):
            out.append(bolt_axis(10.0, (x, BAR_F[1] + P.tine_bar[1], z), (x, BAR_F[0] - P.clamp_plate[1], z), 17.0, 6.4, 8.4))
    return Part.makeCompound(out)


def clamp_holes(shape):
    for x in P.tine_x():
        for z in (BZ[0] - 12.0, BZ[1] + 17.0):
            shape = shape.cut(cyl(10.4, (x, BAR_F[0] - 20.0, z), (x, BAR_F[1] + 30.0, z)))
    return shape


# ---------------------------------------------------------------------
# Levelling board behind the rear bar
# ---------------------------------------------------------------------
def board():
    yf = P.board_y
    z0 = P.board_z0
    up = box_span((-P.frame_x, P.frame_x), (yf - P.board_t, yf), (z0, z0 + P.board_leg))
    flat = box_span((-P.frame_x, P.frame_x), (yf - P.board_leg, yf), (z0, z0 + P.board_t))
    s = up.fuse(flat).removeSplitter()
    for x in P.strap_x:
        for z in (40.0, 75.0):
            s = s.cut(cyl(10.4, (x, yf - 20.0, z), (x, yf + 5.0, z)))
    return s


def straps():
    """Straps 60 x 8 on the back face of the rear bar, down to the board; 4 height holes (25 mm), M10 along y."""
    w, t = P.strap
    y1 = BAR_R[0]
    out = []
    for x in P.strap_x:
        s = box_span((x - w / 2.0, x + w / 2.0), (y1 - t, y1), (20.0, BZ[1] + 10.0))
        for z in (40.0, 75.0, 100.0, 125.0, BZ[0] + 20.0):
            s = s.cut(cyl(10.4, (x, y1 - t - 1.0, z), (x, y1 + 1.0, z)))
        out.append(s)
    return Part.makeCompound(out)


def strap_bolts():
    out = []
    y1 = BAR_R[0]
    for x in P.strap_x:
        out.append(bolt_axis(10.0, (x, BAR_R[1], BZ[0] + 20.0), (x, y1 - P.strap[1], BZ[0] + 20.0), 17.0, 6.4, 8.4))
        for z in (40.0, 75.0):
            out.append(bolt_axis(10.0, (x, y1, z), (x, P.board_y - P.board_t, z), 17.0, 6.4, 8.4))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Rod roller on side plates
# ---------------------------------------------------------------------
RY, RZ = P.roll_y, P.roll_z


def side_plates():
    pts = ((BAR_R[1], BZ[1]), (BAR_R[1], BZ[0] - 10.0), (RY + 40.0, RZ - 50.0), (RY - 60.0, RZ - 50.0),
           (RY - 60.0, RZ + 60.0), (BAR_R[0] - 80.0, BZ[1]))
    out = []
    for sx in (-1, 1):
        x0 = P.side_x if sx > 0 else -P.side_x - P.side_t
        p = plate_yz(pts, x0, P.side_t)
        p = p.cut(cyl(P.roll_shaft_d + 2.0, (x0 - 1, RY, RZ), (x0 + P.side_t + 1, RY, RZ)))
        out.append(p)
    return Part.makeCompound(out)


def bearings():
    t, by, bz = P.brg
    out = []
    for sx in (-1, 1):
        x0 = P.side_x + P.side_t if sx > 0 else -P.side_x - P.side_t - t
        fl = box_span((x0, x0 + t), (RY - by / 2.0, RY + by / 2.0), (RZ - bz / 2.0, RZ + bz / 2.0))
        xh = (x0 + t, x0 + t + 20.0) if sx > 0 else (x0 - 20.0, x0)
        house = cyl(62.0, (xh[0], RY, RZ), (xh[1], RY, RZ))
        out.append(fuse_all([fl, house]).cut(cyl(P.roll_shaft_d, (x0 - 30, RY, RZ), (x0 + 50, RY, RZ))))
    return Part.makeCompound(out)


def roller():
    r = P.roll_d / 2.0
    discs = [cyl(P.roll_d, (sx * P.roll_x - (8.0 if sx > 0 else 0.0), RY, RZ),
                 (sx * P.roll_x + (0.0 if sx > 0 else 8.0), RY, RZ)) for sx in (-1, 1)]
    rods = []
    for i in range(P.roll_rods):
        a = 2 * math.pi * i / P.roll_rods
        y, z = RY + (r - P.roll_rod_d / 2.0) * math.cos(a), RZ + (r - P.roll_rod_d / 2.0) * math.sin(a)
        rods.append(cyl(P.roll_rod_d, (-P.roll_x, y, z), (P.roll_x, y, z)))
    core = cyl(P.roll_core_d, (-P.roll_x, RY, RZ), (P.roll_x, RY, RZ))
    shaft = cyl(P.roll_shaft_d, (-P.side_x - P.side_t - P.brg[0] - 20.0, RY, RZ), (P.side_x + P.side_t + P.brg[0] + 20.0, RY, RZ))
    return fuse_all(discs + rods + [core, shaft])


# ---------------------------------------------------------------------
# Lidar post on the toolbar (fixed)
# ---------------------------------------------------------------------
def lidar_post():
    x, y = P.post_xy
    h = P.post / 2.0
    tube = tube_span((x - h, x + h), (y - h, y + h), (P.post_z[0] - 20.0, P.post_z[1]), 3.0, "z")
    plate = box_span((x - 30.0, x + 30.0), (P.H.tb_y[0] - 6.0, P.H.tb_y[0]), (P.H.tb_z[0] - 20.0, P.H.tb_z[1]))
    cap = box_span((x - h - 10.0, x + h + 10.0), (y - h - 10.0, y + h + 10.0), (P.post_z[1], P.post_z[1] + 5.0))
    return fuse_all([tube, plate, cap])


def lidar():
    x, y = P.post_xy
    d, h = P.lidar
    z0 = P.post_z[1] + 5.0
    return fuse_all([cyl(d, (x, y, z0), (x, y, z0 + h * 0.6)), cyl(d * 0.85, (x, y, z0 + h * 0.6), (x, y, z0 + h))])


# ---------------------------------------------------------------------
# Scene: arena footing with a loosened, levelled band behind the tool (images)
# ---------------------------------------------------------------------
def footing(y0, y1, x0=-2500.0, x1=2500.0):
    return box_span((x0, x1), (y0, y1), (-150.0, 0.0))


def worked_band(y0, y1):
    return box_span((-P.frame_x, P.frame_x), (y0, y1), (0.0, 2.0))


def hoof_prints(y0, y1, n=40, seed=4):
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(-2400, 2400)
        if abs(x) < P.frame_x + 50:
            continue
        y = rnd.uniform(y0, y1)
        out.append(Part.makeCylinder(55.0, 4.0, V(x, y, -2.0)))
    return Part.makeCompound(out)
