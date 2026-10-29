"""Parts of the electric weeder. Every function returns a Part shape in robot coordinates, in the work pose (lift 0).
build_elw.py puts the upper arm, the lower arm and the carrier (with the applicator) in their own sub-Parts:
the arms turn about their pivots, the carrier moves parallel; the actuator is rebuilt per pose.
"""
import math

import Part
from FreeCAD import Vector as V

import elw_params as P


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def cyl_x(d, yz, x0, x1):
    return cyl(d, (x0, yz[0], yz[1]), (x1, yz[0], yz[1]))


def tube_span(x, y, z, t, axis):
    outer = box_span(x, y, z)
    spans = {"x": list(x), "y": list(y), "z": list(z)}
    for k in spans:
        if k == axis:
            spans[k] = [spans[k][0] - 1.0, spans[k][1] + 1.0]
        else:
            spans[k] = [spans[k][0] + t, spans[k][1] - t]
    return outer.cut(box_span(spans["x"], spans["y"], spans["z"]))


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def plate_yz(pts, x0, t):
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(t, 0, 0))


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def lug_pair(yz, gap, t=6.0, r=18.0, back=(-25.0, 0.0), hole=None):
    """2 lugs (plates in y-z) at x +-gap/2 .. +-(gap/2 + t) round a pin at yz, reaching 'back' (dy range) to weld on."""
    y, z = yz
    hole = P.pin_d + 0.5 if hole is None else hole
    out = []
    for sx in (-1, 1):
        x0 = gap / 2.0 if sx > 0 else -gap / 2.0 - t
        plate = box_span((x0, x0 + t), (y + back[0], y + back[1]), (z - r, z + r))
        out.append(fuse_all([plate, cyl_x(2 * r, yz, x0, x0 + t)]).cut(cyl_x(hole, yz, x0 - 1, x0 + t + 1)))
    return out


# ---------------------------------------------------------------------
# Fixed: bearer, post, lugs, HV box, camera
# ---------------------------------------------------------------------
BEARER_Z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + 40.0)
BEARER_Y = (P.bearer_y - 20.0, P.bearer_y + 20.0)
ARM_GAP = P.arm[0] + 2.0
ACT_GAP = P.act_body_d + 4.0


def bearer():
    s = tube_span((-P.bearer_x, P.bearer_x), BEARER_Y, BEARER_Z, 3.0, "x")
    for sx in (-1, 1):
        for x in P.bearer_bolt_x:
            s = s.cut(cyl(P.m10_hole, (sx * x, P.bearer_y, 600), (sx * x, P.bearer_y, 800)))
    return s


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * x, P.bearer_y, P.robot_upper_beam_z[0], BEARER_Z[1])
                              for sx in (-1, 1) for x in P.bearer_bolt_x])


def post():
    """Post 40 x 40 x 3 under the bearer with the arm lugs, the actuator lugs and the coulter-arm lugs."""
    parts = [tube_span((-20.0, 20.0), BEARER_Y, (P.post_z0, BEARER_Z[0]), 3.0, "z")]
    for z in P.pivot_z:
        parts += lug_pair((P.pivot_y, z), ARM_GAP, back=(BEARER_Y[1] - P.pivot_y - 1.0, 0.0))
    parts += lug_pair(P.act_base, ACT_GAP, back=(BEARER_Y[1] - P.act_base[0] - 1.0, 0.0))
    parts += lug_pair((P.bearer_y, P.post_z0 - 15.0), 40.0, t=6.0, r=16.0, back=(-15.0, 15.0))   # coulter arm
    return fuse_all(parts)


def hv_box():
    bx, by, bz = P.hv_box
    box = box_span((-bx / 2.0, bx / 2.0), (P.hv_box_y - by / 2.0, P.hv_box_y + by / 2.0), (BEARER_Z[1], BEARER_Z[1] + bz))
    return box


def beacon():
    x, y = P.hv_box[0] / 2.0 - 50.0, P.hv_box_y
    z0 = BEARER_Z[1] + P.hv_box[2]
    return cyl(P.beacon[0], (x, y, z0), (x, y, z0 + P.beacon[1]))


CAM_Z = P.robot_lower_beam_z[0]
CAM_Y = P.cam_plate_y


def cam_plate():
    s = box_span((-P.cam_plate[0] / 2.0, P.cam_plate[0] / 2.0), CAM_Y, (CAM_Z - P.cam_plate[1], CAM_Z))
    for sx in (-1, 1):
        for y in P.robot_front_beam_y[:1]:
            s = s.cut(cyl(P.m10_hole, (sx * P.cam_bolt_x, y, 500), (sx * P.cam_bolt_x, y, 700)))
    return s


def cam_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * P.cam_bolt_x, y, CAM_Z - P.cam_plate[1], P.robot_lower_beam_z[1])
                              for sx in (-1, 1) for y in P.robot_front_beam_y[:1]])


def camera():
    bx, by, bz = P.cam_box
    yc = (CAM_Y[0] + CAM_Y[1]) / 2.0
    z1 = CAM_Z - P.cam_plate[1]
    box = box_span((-bx / 2.0, bx / 2.0), (yc - by / 2.0, yc + by / 2.0), (z1 - bz, z1))
    lens = cyl(30.0, (0, yc, z1 - bz - 10.0), (0, yc, z1 - bz))
    return fuse_all([box, lens])


# ---------------------------------------------------------------------
# Lift (work pose): arms, carrier with applicator, pins
# ---------------------------------------------------------------------
CARRIER_Y = P.pivot_y + P.arm_len


def arm(i):
    """Upper (0) or lower (1) arm: rect tube 20 x 30 x 2 between its 2 pins, with bushes."""
    z = P.pivot_z[i]
    s = tube_span((-P.arm[0] / 2.0, P.arm[0] / 2.0), (P.pivot_y, CARRIER_Y), (z - P.arm[1] / 2.0, z + P.arm[1] / 2.0),
                  2.0, "y")
    bushes = [cyl_x(26.0, (y, z), -P.arm[0] / 2.0, P.arm[0] / 2.0) for y in (P.pivot_y, CARRIER_Y)]
    s = fuse_all([s] + bushes)
    for y in (P.pivot_y, CARRIER_Y):
        s = s.cut(cyl_x(P.pin_d + 0.5, (y, z), -50, 50))
    return s


def act_lug():
    """2 lugs on the top of the upper arm for the actuator rod pin."""
    y, z = P.upper_arm_point(0.0, P.act_arm)
    out = []
    for sx in (-1, 1):
        x0 = P.arm[0] / 2.0 if sx > 0 else -P.arm[0] / 2.0 - 5.0
        plate = box_span((x0, x0 + 5.0), (y - 18.0, y + 18.0), (z, z + P.act_pin_up + 15.0))
        out.append(plate.cut(cyl_x(P.pin_d + 0.5, (y, z + P.act_pin_up), x0 - 1, x0 + 6)))
    return Part.makeCompound(out)


def carrier():
    """2 plates 6 mm either side of the arms from the upper pin down to a foot plate that holds the applicator."""
    out = []
    ztop = P.pivot_z[0] + 20.0
    zfoot = P.holder_z[1]
    for sx in (-1, 1):
        x0 = ARM_GAP / 2.0 if sx > 0 else -ARM_GAP / 2.0 - 6.0
        out.append(box_span((x0, x0 + 6.0), (CARRIER_Y - 18.0, CARRIER_Y + 18.0), (zfoot + 8.0, ztop)))
    out.append(box_span((-P.holder_x, P.holder_x), P.holder_y, (zfoot, zfoot + 8.0)))
    s = fuse_all(out)
    for z in P.pivot_z:
        s = s.cut(cyl_x(P.pin_d + 0.5, (CARRIER_Y, z), -50, 50))
    return s


def holder():
    return box_span((-P.holder_x, P.holder_x), P.holder_y, P.holder_z)


def fingers():
    out = []
    yc = (P.holder_y[0] + P.holder_y[1]) / 2.0
    span = 2 * (P.holder_x - 15.0)
    for i in range(P.finger_n):
        x = -P.holder_x + 15.0 + span * i / (P.finger_n - 1)
        out.append(cyl(P.finger_d, (x, yc, P.holder_z[0] + 10.0), (x, P.finger_tip[0], P.finger_tip[1] + P.finger_d / 2.0)))
    return Part.makeCompound(out)


def curtains():
    out = []
    for sx in (-1, 1):
        x0 = P.holder_x if sx > 0 else -P.holder_x - P.curtain_t
        out.append(box_span((x0, x0 + P.curtain_t), P.curtain_y, P.curtain_z))
    return Part.makeCompound(out)


def pins_fixed():
    """Pins of the arms in the post lugs and of the actuator base."""
    w = ARM_GAP / 2.0 + 6.0 + 4.0
    out = [cyl_x(P.pin_d, (P.pivot_y, z), -w, w) for z in P.pivot_z]
    wa = ACT_GAP / 2.0 + 6.0 + 4.0
    out.append(cyl_x(P.pin_d, P.act_base, -wa, wa))
    return Part.makeCompound(out)


def pins_carrier():
    w = ARM_GAP / 2.0 + 6.0 + 4.0
    return Part.makeCompound([cyl_x(P.pin_d, (CARRIER_Y, z), -w, w) for z in P.pivot_z])


# ---------------------------------------------------------------------
# Actuator (rebuilt per pose)
# ---------------------------------------------------------------------
def actuator(lift_deg=P.lift_work):
    """(body, rod): 24 V actuator from the base pin to the rod pin on the upper arm."""
    yb, zb = P.act_base
    yr, zr = P.act_rod_pin(lift_deg)
    a0, b0 = V(0, yb, zb), V(0, yr, zr)
    u = b0 - a0
    u.normalize()
    body_len = P.act_retracted - 75.0
    body = Part.makeCompound([cyl(P.act_body_d, a0 + u * 18.0, a0 + u * (18.0 + body_len)),
                              cyl(26.0, a0 - V(ACT_GAP / 2.0 - 1.0, 0, 0), a0 + V(ACT_GAP / 2.0 - 1.0, 0, 0)).cut(
                                  cyl(P.pin_d + 0.5, a0 - V(40, 0, 0), a0 + V(40, 0, 0))),
                              cyl(20.0, a0 + u * 8.0, a0 + u * 18.0)])
    rod = Part.makeCompound([cyl(P.act_rod_d, a0 + u * (18.0 + body_len - 10.0), b0 - u * 10.0),
                             cyl(24.0, b0 - V(P.arm[0] / 2.0 - 1.0, 0, 0), b0 + V(P.arm[0] / 2.0 - 1.0, 0, 0)).cut(
                                 cyl(P.pin_d + 0.5, b0 - V(40, 0, 0), b0 + V(40, 0, 0))),
                             cyl(P.pin_d, b0 - V(P.arm[0] / 2.0 + 8.0, 0, 0), b0 + V(P.arm[0] / 2.0 + 8.0, 0, 0))])
    return body, rod


# ---------------------------------------------------------------------
# Coulter disc (earth return) on 2 arm plates from the post bottom
# ---------------------------------------------------------------------
DISC_PIVOT = (P.bearer_y, P.post_z0 - 15.0)              # under the post (lugs reach 1 mm into it)


DISC_GAP = 40.0 + 2 * 6.0 + 2.0          # coulter arms outside the 6 mm lugs on the post


def disc_arms():
    gap = DISC_GAP
    out = []
    for sx in (-1, 1):
        y0, z0 = DISC_PIVOT
        y1, z1 = P.disc_c
        dy, dz = y1 - y0, z1 - z0
        L = math.hypot(dy, dz)
        ny, nz = -dz / L * 15.0, dy / L * 15.0
        pts = ((y0 + ny, z0 + nz), (y1 + ny, z1 + nz), (y1 - ny, z1 - nz), (y0 - ny, z0 - nz))
        xa = gap / 2.0 if sx > 0 else -gap / 2.0 - P.disc_arm_t
        p = plate_yz(pts, xa, P.disc_arm_t)
        p = fuse_all([p, cyl_x(30.0, DISC_PIVOT, xa, xa + P.disc_arm_t), cyl_x(30.0, P.disc_c, xa, xa + P.disc_arm_t)])
        p = p.cut(cyl_x(P.pin_d + 0.5, DISC_PIVOT, -60, 60)).cut(cyl_x(16.5, P.disc_c, -60, 60))
        out.append(p)
    return Part.makeCompound(out)


def disc():
    gap = DISC_GAP
    d = cyl_x(P.disc_d, P.disc_c, -P.disc_t / 2.0, P.disc_t / 2.0)
    hub = cyl_x(60.0, P.disc_c, -gap / 2.0 + 1.0, gap / 2.0 - 1.0)
    axle = cyl_x(16.0, P.disc_c, -gap / 2.0 - P.disc_arm_t - 5.0, gap / 2.0 + P.disc_arm_t + 5.0)
    return fuse_all([d, hub, axle])


def disc_pin():
    w = DISC_GAP / 2.0 + P.disc_arm_t + 4.0
    return cyl_x(P.pin_d, DISC_PIVOT, -w, w)


# ---------------------------------------------------------------------
# Crop and row space
# ---------------------------------------------------------------------
def crop(y=(-1000.0, 1000.0), step=125.0, h=300.0):
    out = []
    n = int((y[1] - y[0]) // step)
    for sx in (-1, 1):
        for i in range(n + 1):
            out.append(Part.makeCone(10.0, 70.0, h, V(sx * P.row_x, y[0] + i * step, 0)))
    return Part.makeCompound(out)


def row_bands():
    return Part.makeCompound([box_span((sx * P.row_x - P.row_band, sx * P.row_x + P.row_band), (-1100.0, 1000.0),
                                       (0.0, P.crop_h)) for sx in (-1, 1)])


def weeds(n=6, seed=3):
    """A few weeds in the band (images)."""
    import random
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(-70, 70), rnd.uniform(-700, 900)
        out.append(Part.makeCone(25.0, 3.0, 40.0, V(x, y, 0)))
    return Part.makeCompound(out)
