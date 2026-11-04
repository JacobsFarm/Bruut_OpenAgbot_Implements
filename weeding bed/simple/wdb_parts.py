"""Parts of the weeding bed. Every function returns a Part shape in robot coordinates (both sides, mirrored in x)."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import wdb_params as P
from sfe_parts import box_span, cyl_z, cyl_x, cyl_y, fuse_all, bolt_z

TZ = P.tube_z
BEAM_X = P.robot_upper_beam_x
SIDES = (-1, 1)


def sq_tube_x(x0, x1, y, z, a, w, cap=True):
    o = box_span((x0, x1), (y - a / 2.0, y + a / 2.0), z)
    e = P.end_cap_t if cap else -1.0
    i = box_span((min(x0, x1) + e, max(x0, x1) - e), (y - a / 2.0 + w, y + a / 2.0 - w), (z[0] + w, z[1] - w))
    return o.cut(i)


def sq_tube_y(y0, y1, x, z, a, w):
    o = box_span((x - a / 2.0, x + a / 2.0), (y0, y1), z)
    i = box_span((x - a / 2.0 + w, x + a / 2.0 - w), (y0 + P.end_cap_t, y1 - P.end_cap_t), (z[0] + w, z[1] - w))
    return o.cut(i)


def sq_tube_z(z0, z1, x, y, a, w):
    o = box_span((x - a / 2.0, x + a / 2.0), (y - a / 2.0, y + a / 2.0), (z0, z1))
    i = box_span((x - a / 2.0 + w, x + a / 2.0 - w), (y - a / 2.0 + w, y + a / 2.0 - w), (z0 + w, z1 - w))
    return o.cut(i)


# ---------------------------------------------------------------------
# Cross tubes on the upper beams
# ---------------------------------------------------------------------
BOLTS = [(x, y) for y in P.CROSS_FULL + P.CROSS_STUB for x in BEAM_X]


def cross_tubes():
    out = []
    holes_x = list(BEAM_X)
    for y in P.CROSS_FULL:
        out.append(sq_tube_x(-P.half_len, P.half_len, y, TZ, P.tube, P.tube_wall))
    for y in P.CROSS_STUB:
        for s in SIDES:
            out.append(sq_tube_x(s * P.stub_inner, s * P.half_len, y, TZ, P.tube, P.tube_wall))
    holes = [cyl_z(P.m10_hole, TZ[0] - 1, TZ[1] + 1, x, y) for (x, y) in BOLTS]
    return Part.makeCompound(out).cut(holes)


def cross_bolts():
    """M10 through each tube and the upper beam (button head on the tube, nut under the beam)."""
    return Part.makeCompound([bolt_z(x, y, TZ[1], P.robot_upper_beam_z[0], k=4.0) for (x, y) in BOLTS])


# ---------------------------------------------------------------------
# Side frame
# ---------------------------------------------------------------------
RZ = P.rail_z


def hangers():
    """40 x 40 x 4 from under each cross tube end down to the cross arm, a 6 mm gusset in the top corner on the robot
    side (x-z plane)."""
    out = []
    g = P.gusset
    for s in SIDES:
        x = s * P.hanger_x
        for y in P.hanger_y:
            out.append(sq_tube_z(P.arm_z[1], TZ[0], x, y, P.tube, P.hanger_wall))
            xi = x - s * P.tube / 2.0
            tri = Part.makePolygon([V(xi, y - 3.0, TZ[0]), V(xi - s * g, y - 3.0, TZ[0]), V(xi, y - 3.0, TZ[0] - g),
                                    V(xi, y - 3.0, TZ[0])])
            out.append(Part.Face(tri).extrude(V(0, 6.0, 0)))
    return fuse_all(out)


def cross_arms():
    """40 x 40 x 4 under the hangers, carrying both rails; the bed hangs as a C-frame from the inner hanger."""
    out = []
    for s in SIDES:
        for y in P.hanger_y:
            out.append(sq_tube_x(s * P.arm_x[0], s * P.arm_x[1], y, P.arm_z, P.tube, P.hanger_wall))
    return Part.makeCompound(out)


def side_rails():
    return Part.makeCompound([sq_tube_y(P.rail_y[0], P.rail_y[1], s * x, RZ, P.tube, P.tube_wall)
                              for s in SIDES for x in P.rail_x])


def slats():
    """Cross slats 40 x 20 x 2 between the rails, the boards screw onto them and the rails."""
    out = []
    for s in SIDES:
        for y in P.slat_y:
            x0, x1 = s * (P.rail_x[0] + 20.0), s * (P.rail_x[1] - 20.0)
            o = box_span((x0, x1), (y - 20.0, y + 20.0), (RZ[1] - 20.0, RZ[1]))
            i = box_span((x0 - 1.0, x1 + 1.0), (y - 18.0, y + 18.0), (RZ[1] - 18.0, RZ[1] - 2.0))
            out.append(o.cut(i))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Lying boards
# ---------------------------------------------------------------------
BZ = P.board_z


def _bx(s):
    return (s * P.board_x[0], s * P.board_x[1])


def boards_ply():
    out = []
    for s in SIDES:
        for (y0, y1) in (P.leg_board_y, P.chest_board_y, P.face_rest_y):
            pl = box_span(_bx(s), (y0, y1), (BZ, BZ + P.ply))
            if (y0, y1) == P.face_rest_y:
                pl = pl.cut(_face_hole(s, BZ - 1, BZ + P.ply + 1))
            out.append(pl)
    return Part.makeCompound(out)


def _face_hole(s, z0, z1):
    hx, hy = P.face_hole
    yc = 0.5 * (P.face_rest_y[0] + P.face_rest_y[1])
    c = Part.makeCylinder(hx / 2.0, z1 - z0, V(0, 0, z0), V(0, 0, 1))
    m = App.Matrix()
    m.scale(1.0, hy / hx, 1.0)
    c = c.transformGeometry(m)
    c.translate(V(s * P.worker_x, yc, 0))
    return c


def cushions():
    """Foam with synthetic leather: leg pad, a thicker chest wedge (head end higher), a face rest with an opening."""
    z0 = BZ + P.ply
    out = []
    for s in SIDES:
        out.append(box_span(_bx(s), P.leg_board_y, (z0, z0 + P.foam)))
        # chest wedge: foam at the rear end, foam + chest_raise at the front end
        y0, y1 = P.chest_board_y
        x0, x1 = sorted(_bx(s))
        prof = Part.makePolygon([V(x0, y0, z0), V(x0, y1, z0), V(x0, y1, z0 + P.foam + P.chest_raise),
                                 V(x0, y0, z0 + P.foam), V(x0, y0, z0)])
        out.append(Part.Face(prof).extrude(V(x1 - x0, 0, 0)))
        fr = box_span(_bx(s), P.face_rest_y, (z0, z0 + P.foam + P.chest_raise))
        out.append(fr.cut(_face_hole(s, z0 - 1, z0 + P.foam + P.chest_raise + 1)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------
def _pendant_xz(s):
    px, py, pz = P.pendant
    x = s * (P.board_x[0] + 40.0)
    z0 = BZ + P.ply + P.foam + P.chest_raise + 5.0
    return x, z0


def pendants():
    """Hold-to-run box at the inner front corner of the face rest (2 buttons + speed knob)."""
    px, py, pz = P.pendant
    out = []
    for s in SIDES:
        x, z0 = _pendant_xz(s)
        box = box_span((x - px / 2.0, x + px / 2.0), (P.pendant_y - py / 2.0, P.pendant_y + py / 2.0), (z0, z0 + pz))
        btn = [cyl_z(18.0, z0 + pz, z0 + pz + 8.0, x, P.pendant_y + dy) for dy in (-30.0, 0.0)]
        knob = cyl_z(22.0, z0 + pz, z0 + pz + 14.0, x, P.pendant_y + 35.0)
        out.append(fuse_all([box] + btn + [knob]))
    return Part.makeCompound(out)


def pendant_brackets():
    """Bent 4 mm plate: a foot under the inner rail, up beside the board edge and over the face rest to the pendant."""
    px, py, pz = P.pendant
    out = []
    for s in SIDES:
        x, z0 = _pendant_xz(s)
        xb = s * (P.board_x[0] - 1.0)
        zr = P.rail_z[0]
        yy = (P.pendant_y - 30.0, P.pendant_y + 30.0)
        out.append(box_span((xb - s * 4.0, s * (P.rail_x[0] + 20.0)), yy, (zr - 4.0, zr)))
        out.append(box_span((xb - s * 4.0, xb), yy, (zr - 4.0, z0)))
        out.append(box_span((xb - s * 4.0, x + s * px / 2.0), yy, (z0 - 4.0, z0)))
    return Part.makeCompound(out)


def estops():
    out = []
    for s in SIDES:
        x = s * (P.rail_x[1] + 20.0)
        base = box_span((x, x + s * 70.0), (P.estop_y - 35.0, P.estop_y + 35.0), (RZ[0], RZ[1] + 40.0))
        z = RZ[1] + 40.0
        mush = fuse_all([cyl_z(40.0, z, z + 20.0, x + s * 40.0, P.estop_y),
                         cyl_z(P.estop_d, z + 20.0, z + 40.0, x + s * 40.0, P.estop_y)])
        out.append((base, mush))
    return Part.makeCompound([b for b, _ in out]), Part.makeCompound([m for _, m in out])


# ---------------------------------------------------------------------
# Parking stands
# ---------------------------------------------------------------------
def stands(down=False):
    """Drop-leg stand: outer tube 60 x 60 clamped to the side of the outer rail, inner leg 50 x 50 with a foot pad,
    crank on top. Returns (outer tubes + brackets, legs + pads)."""
    a, b = P.stand_tube
    fixed, legs = [], []
    for s in SIDES:
        x = s * P.stand_x
        for y in P.stand_y:
            z1 = P.stand_top
            z0 = z1 - P.stand_len
            fixed.append(sq_tube_z(z0, z1, x, y, a, 4.0))
            fixed.append(box_span((s * (P.rail_x[1] + 20.0), x - s * a / 2.0), (y - 40.0, y + 40.0), (RZ[0] - 30.0, RZ[1] + 30.0)))
            fixed.append(cyl_z(16.0, z1, z1 + 30.0, x, y))
            fixed.append(cyl_y(12.0, y, y + 120.0, x, z1 + 25.0))
            pad_z = 0.0 if down else P.stand_pad_z_up
            leg = sq_tube_z(pad_z + P.stand_pad[1], z0 + 120.0, x, y, b - 1.0, 3.0)
            pad = box_span((x - P.stand_pad[0] / 2.0, x + P.stand_pad[0] / 2.0), (y - P.stand_pad[0] / 2.0, y + P.stand_pad[0] / 2.0),
                           (pad_z, pad_z + P.stand_pad[1]))
            legs += [leg, pad]
    return fuse_all(fixed), Part.makeCompound(legs)


# ---------------------------------------------------------------------
# Sun canopy
# ---------------------------------------------------------------------
def canopy_posts():
    """40 x 40 posts clamped to the outside of the outer rail (12 mm plate), a top rail along y, a knee brace from each
    post to the top rail."""
    out = []
    for s in SIDES:
        x = s * P.post_x
        for y in P.post_y:
            out.append(sq_tube_z(P.arm_z[0], P.canopy_z - P.post, x, y, P.post, 2.0))
            out.append(box_span((s * (P.rail_x[1] + 20.0), x - s * P.post / 2.0), (y - 40.0, y + 40.0),
                                (P.rail_z[0] - 30.0, P.rail_z[1] + 30.0)))
            dy = -1.0 if y > 0 else 1.0
            p0 = V(x, y + dy * P.post / 2.0, P.canopy_z - P.post - 250.0)
            p1 = V(x, y + dy * (P.post / 2.0 + 250.0), P.canopy_z - P.post)
            out.append(Part.makeCylinder(8.0, (p1 - p0).Length, p0, p1 - p0))
        out.append(sq_tube_y(P.canopy_y[0] + 100.0, P.canopy_y[1] - 100.0, x, (P.canopy_z - P.post, P.canopy_z), P.post, 2.0))
        # cross bows from the top rail inward under the canopy
        for y in (P.canopy_y[0] + 120.0, 0.0, P.canopy_y[1] - 120.0):
            out.append(sq_tube_x(s * P.canopy_x[0], x - s * P.post / 2.0, y, (P.canopy_z - 20.0, P.canopy_z), 20.0, 2.0))
    return fuse_all(out)


def canopy():
    return Part.makeCompound([box_span((s * P.canopy_x[0], s * P.canopy_x[1]), P.canopy_y,
                                       (P.canopy_z, P.canopy_z + P.canopy_t)) for s in SIDES])


# ---------------------------------------------------------------------
# Worker (render only): prone, head in the face rest, arms down to the crop in front of the board
# ---------------------------------------------------------------------
def worker(s=1):
    x = s * P.worker_x
    z0 = BZ + P.ply + P.foam
    legs = [box_span((x + dx - 70.0, x + dx + 70.0), (-1000.0, 150.0), (z0, z0 + 140.0)) for dx in (-90.0, 90.0)]
    hips = box_span((x - 180.0, x + 180.0), (50.0, 300.0), (z0, z0 + 220.0))
    torso = box_span((x - 200.0, x + 200.0), (280.0, 780.0), (z0 + P.chest_raise * 0.5, z0 + P.chest_raise + 230.0))
    head = Part.makeSphere(105.0, V(x, 900.0, z0 + P.foam + P.chest_raise + 60.0))
    arms = []
    for dx in (-210.0, 210.0):
        sh = V(x + dx, 740.0, z0 + P.chest_raise + 150.0)
        hand = V(x + dx * 0.5, 1120.0, 60.0)
        arms.append(Part.makeCylinder(45.0, (hand - sh).Length, sh, hand - sh))
        arms.append(Part.makeSphere(50.0, hand))
    return Part.makeCompound(legs + [hips, torso, head] + arms)
