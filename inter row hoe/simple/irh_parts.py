"""Parts of the inter-row hoe. Every function returns a Part shape in robot coordinates, in the work pose
(hoe on the ground, shift 0). build_irh.py puts the carrier in a sub-Part that turns about the pivot axis and the shift
plate with the units in a sub-Part in it that slides along x; only the actuator is rebuilt per pose. Toolbar, hangers,
pivot forks and the lift actuator are the grassland harrow parts.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import irh_params as P


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def tube_span(x, y, z, t, axis):
    """Axis-aligned rectangular tube (wall t) filling the box x, y, z, open along 'axis'."""
    outer = box_span(x, y, z)
    spans = {"x": list(x), "y": list(y), "z": list(z)}
    for k in spans:
        if k == axis:
            spans[k] = [spans[k][0] - 1.0, spans[k][1] + 1.0]
        else:
            spans[k] = [spans[k][0] + t, spans[k][1] - t]
    return outer.cut(box_span(spans["x"], spans["y"], spans["z"]))


def rect_tube(p0, p1, w, h, t=0.0, up=(0.0, 0.0, 1.0)):
    """Rectangular tube (or solid bar for t = 0) from p0 to p1, w across, h along 'up'."""
    a, b = V(*p0), V(*p1)
    X = b - a
    length = X.Length
    X.normalize()
    u = V(*up)
    Z = u - X * u.dot(X)
    Z.normalize()
    Y = Z.cross(X)
    m = App.Matrix(X.x, Y.x, Z.x, a.x, X.y, Y.y, Z.y, a.y, X.z, Y.z, Z.z, a.z, 0, 0, 0, 1)
    s = Part.makeBox(length, w, h, V(0, -w / 2.0, -h / 2.0))
    if t > 0.0:
        s = s.cut(Part.makeBox(length + 2.0, w - 2 * t, h - 2 * t, V(-1.0, -w / 2.0 + t, -h / 2.0 + t)))
    s.transformShape(m)
    return s


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def plate_yz(pts, x0, t):
    """Plate in the y-z plane from a list of (y, z) points, thickness t from x0 along +x."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(t, 0, 0))


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    """Vertical bolt: head under z_head, shank up to the nut on top of z_nut."""
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def bolt_axis(d, p_head, p_nut, head, k, m):
    """Bolt along any axis: head outside p_head, nut outside p_nut."""
    a, b = V(*p_head), V(*p_nut)
    u = b - a
    u.normalize()
    return Part.makeCompound([cyl(head * 1.1, a - u * k, a), cyl(d, a, b + u * (m + 3.0)), cyl(head * 1.1, b, b + u * m)])


# ---------------------------------------------------------------------
# Mount: rear toolbar and hangers (fixed to the robot)
# ---------------------------------------------------------------------
def toolbar():
    return tube_span(P.tb_x, P.tb_y, P.tb_z, P.tb_wall, "x")


def toolbar_caps():
    return Part.makeCompound([box_span((x0, x0 + 3.0), P.tb_y, P.tb_z) for x0 in (P.tb_x[0] - 3.0, P.tb_x[1])])


def hanger_top(sx):
    xc = sx * P.hanger_x
    p = box_span((xc - P.hanger_top_w / 2.0, xc + P.hanger_top_w / 2.0), P.hanger_top_y,
                 (P.robot_lower_beam_z[0] - P.hanger_top_t, P.robot_lower_beam_z[0]))
    for y in P.robot_rear_beam_y:
        for dx in (-P.hanger_bolt_dx, P.hanger_bolt_dx):
            p = p.cut(cyl(P.m10_hole, (xc + dx, y, 500.0), (xc + dx, y, 700.0)))
    return p


def hanger_webs(sx):
    xc = sx * P.hanger_x
    cut = box_span((-2000, 2000), P.tb_y, P.tb_z)
    webs = [plate_yz(P.web_pts, xc + dx - P.web_t / 2.0, P.web_t).cut(cut) for dx in (-P.web_dx, P.web_dx)]
    return Part.makeCompound(webs)


def hanger_bolts(sx):
    xc = sx * P.hanger_x
    out = []
    for y in P.robot_rear_beam_y:
        for dx in (-P.hanger_bolt_dx, P.hanger_bolt_dx):
            out.append(bolt_z(10.0, xc + dx, y, P.robot_lower_beam_z[0] - P.hanger_top_t, P.robot_lower_beam_z[1]))
    return Part.makeCompound(out)


def pivot_lugs():
    """Fork of 2 lugs per arm under the toolbar, with the hole for the pivot pin."""
    out = []
    yp, zp = P.pivot
    for sx in (-1, 1):
        for side in (-1, 1):
            x0 = sx * P.arm_x + side * (P.lug_gap / 2.0) + (0.0 if side > 0 else -P.lug_t)
            lug = box_span((x0, x0 + P.lug_t), (yp - 25.0, yp + 25.0), (zp, P.tb_z[0]))
            lug = lug.fuse(cyl(50.0, (x0, yp, zp), (x0 + P.lug_t, yp, zp)))
            out.append(lug.cut(cyl(P.pivot_d + 0.5, (x0 - 1, yp, zp), (x0 + P.lug_t + 1, yp, zp))).removeSplitter())
    return Part.makeCompound(out)


def pivot_pins():
    yp, zp = P.pivot
    out = []
    for sx in (-1, 1):
        x0 = sx * P.arm_x - P.lug_gap / 2.0 - P.lug_t - 6.0
        x1 = sx * P.arm_x + P.lug_gap / 2.0 + P.lug_t + 6.0
        out.append(cyl(P.pivot_d, (x0, yp, zp), (x1, yp, zp)))
        out.append(cyl(32.0, (x0 - 4.0, yp, zp), (x0, yp, zp)))            # head
        out.append(cyl(4.0, (x1 - 3.0, yp - 20.0, zp), (x1 - 3.0, yp + 20.0, zp)))   # R-clip
    return Part.makeCompound(out)


def act_mast():
    """2 plates on top of the toolbar that carry the base clevis of the actuator (leaning forward, mirror of the
    push blade)."""
    yb, zb = P.act_base
    pts = ((P.tb_y[1], P.tb_z[1]), (P.tb_y[0], P.tb_z[1]), (yb - 30.0, zb + 10.0), (yb + 22.0, zb + 22.0),
           (yb + 22.0, zb - 20.0))
    out = []
    for side in (-1, 1):
        x0 = side * (P.act_body_d / 2.0 + 3.0) + (0.0 if side > 0 else -8.0)
        pl = plate_yz(pts, x0, 8.0).fuse(cyl(44.0, (x0, yb, zb), (x0 + 8.0, yb, zb)))
        out.append(pl.cut(cyl(12.5, (x0 - 1, yb, zb), (x0 + 9, yb, zb))).removeSplitter())
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Carrier with the side-shift axis (turns about the pivot)
# ---------------------------------------------------------------------
def carrier():
    """Weldment: 2 arms 60 x 40 x 3 with pivot bushes, main beam 60 x 60 x 4, rail plate 10 mm on its rear face,
    actuator lug with the float slot."""
    yp, zp = P.pivot
    mz = P.main_z
    cx = (-P.carrier_x, P.carrier_x)
    parts = [tube_span(cx, P.main_y, mz, P.main_wall, "x"), box_span(cx, P.rail_plate_y, P.rail_plate_z)]
    end = (P.main_y[1], (mz[0] + mz[1]) / 2.0)
    for sx in (-1, 1):
        x = sx * P.arm_x
        parts.append(rect_tube((x, yp, zp), (x, end[0] - 2.0, end[1]), P.arm_h, P.arm_w, P.arm_wall,
                               up=(1.0, 0.0, 0.0)))
        parts.append(cyl(34.0, (x - P.arm_w / 2.0, yp, zp), (x + P.arm_w / 2.0, yp, zp)))
    yr, zr = P.act_rod
    for side in (-1, 1):
        x0 = side * 14.0 + (0.0 if side > 0 else -8.0)
        pts = ((P.main_y[0] + 5.0, mz[1]), (P.main_y[1] - 5.0, mz[1]),
               (yr + 25.0, zr + P.float_slot + 20.0), (yr - 25.0, zr + P.float_slot + 20.0))
        parts.append(plate_yz(pts, x0, 8.0))
    s = fuse_all(parts)
    s = s.cut(cyl(P.pivot_d + 0.5, (-700, yp, zp), (700, yp, zp)))
    return s.cut(box_span((-30, 30), (yr - 6.5, yr + 6.5), (zr - 6.5, zr + P.float_slot + 6.5)))


def rails():
    y = (P.rail_plate_y[0] - P.rail, P.rail_plate_y[0])
    return Part.makeCompound([box_span((-P.rail_x, P.rail_x), y, (z - P.rail / 2.0, z + P.rail / 2.0))
                              for z in P.rail_z])


def bearings():
    """BK12 (fixed) and BF12 (floating) support blocks of the ball screw, bored for the screw."""
    out = []
    for bx in P.bearing_x:
        b = box_span(bx, P.bearing_y, P.bearing_z)
        out.append(b.cut(cyl(P.screw_d + 1.0, (bx[0] - 1, P.screw_y, P.screw_z), (bx[1] + 1, P.screw_y, P.screw_z))))
    return Part.makeCompound(out)


def screw():
    return cyl(P.screw_d, (P.screw_x[0], P.screw_y, P.screw_z), (P.screw_x[1], P.screw_y, P.screw_z))


def motor():
    """NEMA23 closed-loop stepper on a flange plate welded to the end of the rail plate, coupling to the screw."""
    y, z = P.screw_y, P.screw_z
    h = P.motor / 2.0
    fl = box_span(P.motor_flange_x, (y - h - 3.0, P.rail_plate_y[0]), (z - h - 3.0, z + h + 3.0))
    fl = fl.cut(cyl(P.coupling[2] + 2.0, (P.motor_flange_x[0] - 1, y, z), (P.motor_flange_x[1] + 1, y, z)))
    x0 = P.motor_flange_x[1]
    body = box_span((x0, x0 + P.motor_len), (y - h, y + h), (z - h, z + h))
    return fl, body


def coupling():
    x0, x1, d = P.coupling
    return cyl(d, (x0, P.screw_y, P.screw_z), (x1, P.screw_y, P.screw_z))


# ---------------------------------------------------------------------
# Shift group (slides along x on the rails; drawn at shift 0)
# ---------------------------------------------------------------------
def carriages():
    out = []
    for xc in P.car_x:
        for z in P.rail_z:
            out.append(box_span((xc - P.car_len / 2.0, xc + P.car_len / 2.0), P.car_y,
                                (z - P.car_w / 2.0, z + P.car_w / 2.0)))
    return Part.makeCompound(out)


def shift_plate():
    return box_span((-P.shift_x, P.shift_x), P.shift_y, P.shift_z)


def nut_housing():
    """Ball nut in a housing bolted to the front face of the shift plate."""
    w, h = P.nut_box
    b = box_span((-w / 2.0, w / 2.0), (P.shift_y[1], P.rail_plate_y[0] - 3.0),
                 (P.screw_z - h / 2.0, P.screw_z + h / 2.0))
    return b


def mast():
    m = tube_span((-20.0, 20.0), P.mast_y, P.mast_z, 3.0, "z")
    top = box_span((-30.0, 30.0), (P.mast_y[0] - 30.0, P.mast_y[1]), (P.mast_z[1], P.mast_z[1] + 6.0))
    return m.fuse(top).removeSplitter()


def camera():
    """Camera box on the mast head, tilted cam_tilt degrees down, looking backward (-y)."""
    cx, cy, cz = P.cam_box
    yc, zc = P.mast_y[0] - 30.0, P.mast_z[1] + 6.0 + cz / 2.0 + 15.0
    b = box_span((-cx / 2.0, cx / 2.0), (yc - cy / 2.0, yc + cy / 2.0), (zc - cz / 2.0, zc + cz / 2.0))
    lens = cyl(36.0, (0, yc - cy / 2.0, zc), (0, yc - cy / 2.0 - 15.0, zc))
    s = b.fuse(lens)
    s.rotate(V(0, yc, zc), V(1, 0, 0), P.cam_tilt)
    return s


def camera_bracket():
    yc, zc = P.mast_y[0] - 30.0, P.mast_z[1] + 6.0
    return Part.makeCompound([box_span((sx * 60.0 - 4.0 * (sx < 0), sx * 60.0 + 4.0 * (sx > 0)),
                                       (yc - 30.0, yc + 30.0), (zc, zc + 60.0)) for sx in (-1, 1)])


# ---------------------------------------------------------------------
# Hoe unit (parallelogram, gauge wheel, shares); xu = unit centre
# ---------------------------------------------------------------------
def head(xu):
    """Head bracket: plate on the rear face of the shift plate with 2 cheeks for the links."""
    s = box_span((xu - P.head_plate_u, xu + P.head_plate_u), P.head_plate_y, P.head_z)
    for sd in (-1, 1):
        u0, u1 = P.cheek_u
        s = s.fuse(box_span(sorted((xu + sd * u0, xu + sd * u1)), P.head_cheek_y, P.head_z))
    return s.removeSplitter()


def links(xu):
    out = []
    for sd in (-1, 1):
        x0, x1 = sorted((xu + sd * P.link_u[0], xu + sd * P.link_u[1]))
        for z in P.link_z:
            a, b = P.link_y
            bar = box_span((x0, x1), (b - 15.0, a + 15.0), (z - P.link_h / 2.0, z + P.link_h / 2.0))
            out.append(bar)
    return Part.makeCompound(out)


def pins(xu):
    out = []
    for y in P.link_y:
        for z in P.link_z:
            out.append(cyl(P.pin_d, (xu - P.link_u[1] - 6.0, y, z), (xu + P.link_u[1] + 6.0, y, z)))
    return Part.makeCompound(out)


def unit_frame(xu):
    """Weldment: post 120 x 40 x 4, beam 50 x 50 x 3 back, cross bar 40 x 40 x 3, fork plate and 2 fork arms."""
    parts = [tube_span((xu - P.post_u, xu + P.post_u), P.post_y, P.post_z, 4.0, "z"),
             tube_span((xu - 25.0, xu + 25.0), (P.beam_y[1], P.beam_y[0]), P.beam_z, 3.0, "y"),
             tube_span((xu - P.cross_u, xu + P.cross_u), P.cross_y, P.cross_z, 3.0, "x"),
             box_span((xu - 52.0, xu + 52.0), P.fork_plate_y, (P.post_z[0] - 40.0, P.post_z[0] + 40.0))]
    zw = P.wheel_d / 2.0
    for sd in (-1, 1):
        x0, x1 = sorted((xu + sd * P.fork_u[0], xu + sd * P.fork_u[1]))
        parts.append(plate_yz(((P.fork_plate_y[0], P.post_z[0] - 40.0), (P.fork_plate_y[0], P.post_z[0] + 20.0),
                               (P.wheel_y - 20.0, zw + 25.0), (P.wheel_y + 25.0, zw + 25.0),
                               (P.wheel_y + 25.0, zw - 20.0)), x0, x1 - x0))
    s = fuse_all(parts)
    for y in P.link_y[1:]:
        for z in P.link_z:
            s = s.cut(cyl(P.pin_d + 0.5, (xu - 80, y, z), (xu + 80, y, z)))
    return s.cut(cyl(16.5, (xu - 60, P.wheel_y, zw), (xu + 60, P.wheel_y, zw)))


def gauge_wheel(xu):
    zw = P.wheel_d / 2.0
    w = P.wheel_w / 2.0
    tyre = cyl(P.wheel_d, (xu - w, P.wheel_y, zw), (xu + w, P.wheel_y, zw))
    return tyre.cut(cyl(17.0, (xu - w - 1, P.wheel_y, zw), (xu + w + 1, P.wheel_y, zw)))


def wheel_axle(xu):
    zw = P.wheel_d / 2.0
    return cyl(16.0, (xu - 58.0, P.wheel_y, zw), (xu + 58.0, P.wheel_y, zw))


def goosefoot(xu):
    """A-share: swept wings 250 wide, flat at the working depth, on a rigid shank."""
    z0 = -P.work_depth
    h = P.share_w / 2.0
    pts = [V(xu, P.share_tip_y, z0), V(xu + h, P.share_back_y, z0), V(xu + h - 25.0, P.share_back_y, z0),
           V(xu, P.share_back_y + 40.0, z0), V(xu - h + 25.0, P.share_back_y, z0), V(xu - h, P.share_back_y, z0)]
    share = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, P.share_t))
    sh = box_span((xu - P.shank[0] / 2.0, xu + P.shank[0] / 2.0), P.shank_y, (z0 + P.share_t - 1.0, P.beam_z[0]))
    return share, sh


def lblades(xu):
    """2 L-blades: upright wall next to the row (outside), horizontal knife pointing inward to the unit centre."""
    z0 = -P.work_depth
    out, shanks = [], []
    for sd in (-1, 1):
        u0, u1 = P.lblade_u
        knife = box_span(sorted((xu + sd * u0, xu + sd * u1)), P.lblade_y, (z0, z0 + P.lblade_t))
        wall = box_span(sorted((xu + sd * (u1 - P.lblade_t), xu + sd * u1)), P.lblade_y,
                        (z0 + P.lblade_t, z0 + P.lblade_wall_h))
        out.append(knife.fuse(wall).removeSplitter())
        shanks.append(box_span(sorted((xu + sd * P.lshank_u[0], xu + sd * P.lshank_u[1])), P.lshank_y,
                               (z0 + P.lblade_wall_h - 10.0, P.cross_z[0])))
    return out, shanks



# ---------------------------------------------------------------------
# Actuator (rebuilt per pose)
# ---------------------------------------------------------------------
def actuator(lift_deg=P.lift_work):
    yb, zb = P.act_base
    yr, zr = P.rotate_yz(P.act_rod, lift_deg)
    a, b = V(0, yb, zb), V(0, yr, zr)
    u = b - a
    L = u.Length
    u.normalize()
    body_len = P.act_retracted - 75.0          # leaves room for the rod clevis and the lug at the shortest length
    body = Part.makeCompound([cyl(P.act_body_d, a + u * 20.0, a + u * (20.0 + body_len)),
                              rect_tube(a - u * 14.0, a + u * 20.0, 34.0, 30.0, up=(1.0, 0.0, 0.0)),
                              cyl(12.0, a - V(45, 0, 0), a + V(45, 0, 0))])
    rod = Part.makeCompound([cyl(P.act_rod_d, a + u * (20.0 + body_len - 10.0), b - u * 12.0),
                             rect_tube(b - u * 14.0, b + u * 12.0, 22.0, 26.0, up=(1.0, 0.0, 0.0)),
                             cyl(12.0, b - V(30, 0, 0), b + V(30, 0, 0))])
    return body, rod, L
