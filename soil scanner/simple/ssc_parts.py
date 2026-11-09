"""Parts of the soil scanner. Every function returns a Part shape in robot coordinates. Nothing moves: the detector
is fixed 600 mm above the ground (the robot does not pitch or lift it).
"""
import Part
from FreeCAD import Vector as V

import ssc_params as P


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def shell(d_out, d_in, p0, p1):
    return cyl(d_out, p0, p1).cut(cyl(d_in, p0, p1))


def plate_yz(pts, x0, t):
    """Plate in the y-z plane from (y, z) points, thickness t from x0 along +x."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(t, 0, 0))


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    """Vertical bolt: head under z_head, shank up to the nut on top of z_nut."""
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def polyline_rod(pts, d):
    """Solid rod along a polyline with balls at the corners (guard, cable)."""
    out = [cyl(d, pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    out += [Part.makeSphere(d / 2.0, V(*p)) for p in pts[1:-1]]
    s = out[0]
    for o in out[1:]:
        s = s.fuse(o)
    return s.removeSplitter()


def ax(x):
    """Point on the detector axis."""
    return (x, P.det_y, P.det_z)


SIDES = (-1, 1)


# ---------------------------------------------------------------------
# Brackets
# ---------------------------------------------------------------------
def brackets():
    out = []
    zb = P.robot_lower_beam_z[1]
    for sx in SIDES:
        xc = sx * P.bracket_x
        b = box_span((xc - P.base[0] / 2, xc + P.base[0] / 2), P.base_y, (zb, zb + P.base[2]))
        for dx in (-P.bolt_dx, P.bolt_dx):
            b = b.cut(cyl(P.m10_hole, (xc + dx, sum(P.robot_front_beam_y) / 2, zb - 5), (xc + dx, sum(P.robot_front_beam_y) / 2, zb + 20)))
        side = plate_yz(P.side_pts, xc - P.side_t / 2, P.side_t)
        arm = box_span((xc - P.arm_w / 2, xc + P.arm_w / 2), P.arm_y, P.arm_z)
        for y in P.mount_y:
            arm = arm.cut(cyl(8.4, (xc, y, P.arm_z[0] - 1), (xc, y, P.arm_z[1] + 1)))
        out.append(b.fuse([side, arm]).removeSplitter())
    return Part.makeCompound(out)


def bracket_bolts():
    out = []
    yc = sum(P.robot_front_beam_y) / 2
    for sx in SIDES:
        for dx in (-P.bolt_dx, P.bolt_dx):
            out.append(bolt_z(10.0, sx * P.bracket_x + dx, yc, P.robot_lower_beam_z[0], P.robot_lower_beam_z[1] + P.base[2]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Clamp rings, liner, lugs, rubber mounts
# ---------------------------------------------------------------------
def ring_d():
    return P.tube_d + 2 * P.liner_t + 2 * P.ring_t


def clamps():
    """Ring with a lug on top (for the rubber mounts) and 2 ears at the bottom (clamp bolt)."""
    out = []
    D = ring_d()
    for sx in SIDES:
        x0, x1 = sx * P.bracket_x - P.ring_w / 2, sx * P.bracket_x + P.ring_w / 2
        ring = shell(D, P.tube_d + 2 * P.liner_t, ax(x0), ax(x1))
        lug = box_span((sx * P.bracket_x - P.lug[0] / 2, sx * P.bracket_x + P.lug[0] / 2),
                       (P.det_y - P.lug[1] / 2, P.det_y + P.lug[1] / 2), (P.det_z + 80.0, P.lug_z[1]))
        lug = lug.cut(cyl(D - 0.2, ax(x0 - 1), ax(x1 + 1)))
        ears = []
        zb = P.det_z - D / 2
        for sy in (-1, 1):
            e = box_span((x0, x1), tuple(sorted((P.det_y + sy * 5.0, P.det_y + sy * P.ear[1]))),
                         (zb - P.ear[2] + 4.0, zb + 12.0))
            ears.append(e.cut(cyl(D - 0.2, ax(x0 - 1), ax(x1 + 1))))
        out.append(ring.fuse([lug] + ears).removeSplitter())
    return Part.makeCompound(out)


def clamp_bolts():
    out = []
    z = P.det_z - ring_d() / 2 - P.ear[2] / 2 + 4.0
    for sx in SIDES:
        x = sx * P.bracket_x
        out.append(cyl(8.0, (x, P.det_y - P.ear[1] - 6.0, z), (x, P.det_y + P.ear[1] + 9.0, z)))
        out.append(cyl(14.5, (x, P.det_y - P.ear[1] - 5.5, z), (x, P.det_y - P.ear[1], z)))
        out.append(cyl(14.5, (x, P.det_y + P.ear[1], z), (x, P.det_y + P.ear[1] + 6.5, z)))
    return Part.makeCompound(out)


def liners():
    out = []
    for sx in SIDES:
        out.append(shell(P.tube_d + 2 * P.liner_t, P.tube_d, ax(sx * P.bracket_x - P.ring_w / 2 - 3),
                         ax(sx * P.bracket_x + P.ring_w / 2 + 3)))
    return Part.makeCompound(out)


def rubber_mounts():
    out = []
    for sx in SIDES:
        for y in P.mount_y:
            out.append(cyl(P.mount_d, (sx * P.bracket_x, y, P.lug_z[1]), (sx * P.bracket_x, y, P.arm_z[0])))
    return Part.makeCompound(out)


def mount_nuts():
    """M8 studs of the rubber mounts: nut on top of the arm plate."""
    out = []
    for sx in SIDES:
        for y in P.mount_y:
            out.append(cyl(8.0, (sx * P.bracket_x, y, P.arm_z[0]), (sx * P.bracket_x, y, P.arm_z[1] + 10.0)))
            out.append(cyl(14.5, (sx * P.bracket_x, y, P.arm_z[1]), (sx * P.bracket_x, y, P.arm_z[1] + 6.5)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------
def tube():
    return shell(P.tube_d, P.tube_d - 2 * P.tube_t, ax(-P.tube_half), ax(P.tube_half))


def caps():
    out = []
    for sx in SIDES:
        x0 = sx * P.tube_half
        x1 = sx * (P.tube_half + P.cap_len)
        xi = sx * (P.tube_half + P.cap_len - P.cap_wall)
        c = cyl(P.cap_d, ax(min(x0, x1)), ax(max(x0, x1))).cut(cyl(P.cap_d - 2 * P.cap_wall, ax(min(x0, xi)), ax(max(x0, xi))))
        if sx > 0:
            c = c.cut(cyl(P.gland_d - 4, (xi - 1, P.det_y - P.gland_r, P.det_z), (x1 + 1, P.det_y - P.gland_r, P.det_z)))
        out.append(c)
    return Part.makeCompound(out)


def labels():
    out = []
    for sx in SIDES:
        x = sx * (P.tube_half + P.cap_len)
        out.append(cyl(P.label_d, ax(min(x, x + sx * 1.0)), ax(max(x, x + sx * 1.0))))
    return Part.makeCompound(out)


def crystal():
    lx, ly, lz = P.crystal
    return box_span((P.crystal_x0, P.crystal_x0 + lx), (P.det_y - ly / 2, P.det_y + ly / 2),
                    (P.det_z - lz / 2, P.det_z + lz / 2))


def foam():
    x0, x1 = P.crystal_x0 - 5.0, P.crystal_x0 + P.crystal[0] + 5.0
    sleeve = shell(P.tube_d - 2 * P.tube_t - 2.0, P.foam_d, ax(x0), ax(x1))
    plug = cyl(P.tube_d - 2 * P.tube_t - 2.0, ax(-P.tube_half + 5.0), ax(x0))
    return Part.makeCompound([sleeve, plug])


def pmt():
    x0 = P.crystal_x0 + P.crystal[0]
    return cyl(P.pmt_d, ax(x0), ax(x0 + P.pmt_len))


def mca():
    x0 = P.crystal_x0 + P.crystal[0] + P.pmt_len + 5.0
    return cyl(P.mca_d, ax(x0), ax(x0 + P.mca_t))


def gland():
    x0 = P.tube_half + P.cap_len
    return cyl(P.gland_d, (x0, P.det_y - P.gland_r, P.det_z), (x0 + P.gland_len, P.det_y - P.gland_r, P.det_z))




def cable_pts():
    x0 = P.tube_half + P.cap_len + P.gland_len
    bx = P.ebox_xy[0] + P.ebox[0] / 2
    return ((x0 - 2.0, P.det_y - P.gland_r, P.det_z), (x0 + 22.0, P.det_y - P.gland_r - 15.0, P.det_z + 40.0),
            (x0 + 22.0, P.ebox_xy[1] + 10.0, P.arm_z[1] + 30.0), (bx - 2.0, P.ebox_xy[1], P.arm_z[1] + 45.0))


def cable():
    return polyline_rod(cable_pts(), P.cable_d)


# ---------------------------------------------------------------------
# Guard and processor box
# ---------------------------------------------------------------------
def guard():
    return polyline_rod(P.guard_pts, P.guard_d)


def ebox():
    x, y = P.ebox_xy
    lx, ly, lz = P.ebox
    b = box_span((x - lx / 2, x + lx / 2), (y - ly / 2, y + ly / 2), (P.arm_z[1], P.arm_z[1] + lz))
    lid = box_span((x - lx / 2 - 3, x + lx / 2 + 3), (y - ly / 2 - 3, y + ly / 2 + 3),
                   (P.arm_z[1] + lz - 18.0, P.arm_z[1] + lz))
    ant = cyl(14.0, (x - lx / 2 + 25, y + ly / 2 - 25, P.arm_z[1] + lz), (x - lx / 2 + 25, y + ly / 2 - 25,
                                                                          P.arm_z[1] + lz + 110.0))
    return b.fuse([lid, ant]).removeSplitter()


# ---------------------------------------------------------------------
# Ground / map helpers for the animation
# ---------------------------------------------------------------------
def map_block(x0, x1, y0, y1, h=6.0):
    return box_span((x0, x1), (y0, y1), (0.0, h))


def sample_marker(x, y, s=700.0, h=12.0):
    """Blue square as on the Interra map (calibration sample)."""
    return box_span((x - s / 2, x + s / 2), (y - s / 2, y + s / 2), (0.0, h)).cut(
        box_span((x - s / 2 + 90, x + s / 2 - 90), (y - s / 2 + 90, y + s / 2 - 90), (-1.0, h + 1)))
