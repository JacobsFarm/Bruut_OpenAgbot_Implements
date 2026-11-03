"""Parts of the laser weeder that are not the drop-on-demand boom's: rail bolts (no control-box plate here), the 2 scan
heads, the laser box on its cradle and the fibre cables. Every function returns a Part shape in robot coordinates,
hood at the middle height step. Rails, posts and the hood come from ddb_parts (imported) in build_lzw.py.
"""
import Part

import lzw_params as P
import ddb_parts as DG

D = P.D
box_span = DG.box_span
cyl_z = DG.cyl_z
cyl_y = DG.cyl_y
fuse_all = DG.fuse_all
bolt_z = DG.bolt_z
square_tube_x = DG.SG.square_tube_x

TOP_IN = DG.TOP_IN
HEAD_Z = (TOP_IN - P.head_box[2], TOP_IN)
LENS_Z = (HEAD_Z[0] - P.lens[1], HEAD_Z[0])
BOX_Z = (P.cradle_z[1], P.cradle_z[1] + P.box[2])


def rail_bolts():
    """M10 through the lower beams and the rails (head on the beam)."""
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], D.rail_z[0]) for (x, y) in DG.RAIL_BOLTS])


def scan_heads():
    bx, by, bz = P.head_box
    out = []
    for x in P.head_x:
        body = box_span((x - bx / 2.0, x + bx / 2.0), (P.head_y - by / 2.0, P.head_y + by / 2.0), HEAD_Z)
        flange = box_span((x - bx / 2.0 - 10.0, x + bx / 2.0 + 10.0), (P.head_y - by / 2.0, P.head_y + by / 2.0),
                          (TOP_IN - 6.0, TOP_IN))
        out.append(fuse_all([body, flange]))
    return Part.makeCompound(out)


def lenses():
    return Part.makeCompound([cyl_z(P.lens[0], LENS_Z[0], LENS_Z[1], x, P.head_y) for x in P.head_x])


def lens_windows():
    """Protective window under each lens (smoke and dust)."""
    return Part.makeCompound([cyl_z(P.lens[0] - 6.0, LENS_Z[0] - 3.0, LENS_Z[0], x, P.head_y) for x in P.head_x])


CRADLE_BOLTS = [(x, y) for x in (P.robot_upper_beam_x[1], P.robot_upper_beam_x[2]) for y in P.cradle_y]


def cradle():
    zc = 0.5 * (P.cradle_z[0] + P.cradle_z[1])
    s = Part.makeCompound([square_tube_x(-P.cradle_half, P.cradle_half, y, zc, 40.0, 3.0) for y in P.cradle_y])
    return s.cut([cyl_z(P.m10_hole, P.cradle_z[0] - 1, P.cradle_z[1] + 1, x, y) for (x, y) in CRADLE_BOLTS])


def cradle_bolts():
    return Part.makeCompound([bolt_z(x, y, P.cradle_z[1], P.robot_upper_beam_z[0], k=4.0) for (x, y) in CRADLE_BOLTS])


def laser_box():
    """Air-cooled box: 2 fibre-coupled diode lasers, drivers, galvo controllers; 2 fans in the rear face."""
    (x0, x1), (y0, y1), _ = P.box
    b = box_span((x0, x1), (y0, y1), BOX_Z)
    lid = box_span((x0 + 8.0, x1 - 8.0), (y0 + 8.0, y1 - 8.0), (BOX_Z[1], BOX_Z[1] + 6.0))
    fd, ft = P.box_fan
    fans = [cyl_y(fd, y0 - ft, y0, x, BOX_Z[0] + P.box[2] / 2.0) for x in (-110.0, 110.0)]
    glands = [cyl_z(24.0, BOX_Z[0] - 15.0, BOX_Z[0], x, P.head_y) for x in P.head_x]
    return fuse_all([b, lid] + fans + glands)


def fibres():
    """Armoured fibre cables from the gland on the hood top up towards the box; the last 60 mm are a slack loop
    (not drawn), so the hood can take its 3 height steps."""
    top = BOX_Z[0] - 15.0 - 60.0
    out = []
    for x in P.head_x:
        gland = cyl_z(24.0, D.hood_top, D.hood_top + 15.0, x, P.head_y)
        cable = cyl_z(P.fibre_d, D.hood_top + 15.0, top, x, P.head_y)
        out.append(fuse_all([gland, cable]))
    return Part.makeCompound(out)


def beam_cones():
    """The scan field of each head down to the ground (for the renders): a square pyramid."""
    import math
    from FreeCAD import Vector as V
    out = []
    h = LENS_Z[0]
    r = h * math.tan(math.radians(P.scan_half_deg))
    for x in P.head_x:
        pts = [V(x - r, P.head_y - r, 1.0), V(x + r, P.head_y - r, 1.0), V(x + r, P.head_y + r, 1.0),
               V(x - r, P.head_y + r, 1.0)]
        base = Part.Face(Part.makePolygon(pts + [pts[0]]))
        out.append(Part.makeLoft([Part.Wire(base.OuterWire), Part.Wire(Part.makePolygon(
            [V(x - 1, P.head_y - 1, h), V(x + 1, P.head_y - 1, h), V(x + 1, P.head_y + 1, h), V(x - 1, P.head_y + 1, h),
             V(x - 1, P.head_y - 1, h)]))], True))
    return Part.makeCompound(out)
