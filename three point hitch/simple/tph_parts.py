"""Parts of the three-point hitch and the cultivator. Every function returns a Part shape in robot coordinates, in the
work pose (lower links at 0 degrees, implement level on its gauge wheels). build_tph.py turns the lower links about their
pivot and moves the implement with the linkage; the top link and the lift rods are rebuilt per pose.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import tph_params as P


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




def lower_lugs():
    """2 lugs per lower link under the toolbar, with the pivot hole."""
    out = []
    yp, zp = P.lower_a
    for sx in (-1, 1):
        for side in (-1, 1):
            x0 = sx * P.lower_ax + side * (P.link_t / 2.0 + 3.0) + (0.0 if side > 0 else -P.lug_t)
            lug = box_span((x0, x0 + P.lug_t), (yp - 25.0, yp + 25.0), (zp, P.tb_z[0]))
            lug = lug.fuse(cyl(50.0, (x0, yp, zp), (x0 + P.lug_t, yp, zp)))
            out.append(lug.cut(cyl(P.pin_d + 0.5, (x0 - 1, yp, zp), (x0 + P.lug_t + 1, yp, zp))).removeSplitter())
    return Part.makeCompound(out)


def top_bracket():
    """2 plates 8 mm on top of the toolbar with the top link pin hole."""
    yc, zc = P.top_c
    pts = ((P.tb_y[0], P.tb_z[1]), (P.tb_y[1], P.tb_z[1]), (yc + 25.0, zc + 25.0), (yc - 25.0, zc + 25.0))
    out = []
    for side in (-1, 1):
        x0 = side * P.top_bracket_x + (0.0 if side > 0 else -8.0)
        pl = plate_yz(pts, x0, 8.0).fuse(cyl(50.0, (x0, yc, zc), (x0 + 8.0, yc, zc)))
        out.append(pl.cut(cyl(P.pin_d + 0.5, (x0 - 1, yc, zc), (x0 + 9, yc, zc))).removeSplitter())
    return Part.makeCompound(out)


def act_lugs():
    """2 plates per lift rod on top of the toolbar, base pin O12."""
    yb, zb = P.act_base
    pts = ((P.tb_y[0], P.tb_z[1]), (P.tb_y[1], P.tb_z[1]), (yb + 22.0, zb + 20.0), (yb - 22.0, zb + 20.0))
    out = []
    for sx in (-1, 1):
        for side in (-1, 1):
            x0 = sx * P.act_x + side * 21.0 + (0.0 if side > 0 else -8.0)
            pl = plate_yz(pts, x0, 8.0).fuse(cyl(40.0, (x0, yb, zb), (x0 + 8.0, yb, zb)))
            out.append(pl.cut(cyl(12.5, (x0 - 1, yb, zb), (x0 + 9, yb, zb))).removeSplitter())
    return Part.makeCompound(out)


def pins():
    """Lower link pivot pins O16 and top link pin O16 (with heads), fixed to the mount."""
    out = []
    yp, zp = P.lower_a
    for sx in (-1, 1):
        x_in = sx * (P.lower_ax - P.link_t / 2.0 - 3.0 - P.lug_t - 4.0)
        x_out = sx * (P.lower_ax + P.link_t / 2.0 + 3.0 + P.lug_t + 4.0)
        out.append(cyl(P.pin_d, (x_in, yp, zp), (x_out, yp, zp)))
        out.append(cyl(26.0, (x_out, yp, zp), (x_out + sx * 4.0, yp, zp)))
    yc, zc = P.top_c
    x1 = P.top_bracket_x + 8.0 + 4.0
    out.append(cyl(P.pin_d, (-x1, yc, zc), (x1, yc, zc)))
    out.append(cyl(26.0, (x1, yc, zc), (x1 + 4.0, yc, zc)))
    return Part.makeCompound(out)


def lower_link(sx):
    """Flat bar 50 x 20 from the pivot boss to the ball end, with the lift rod pin stub welded on the outside."""
    ya, za = P.lower_a
    yb, zb = P.lower_b
    xa, xb = sx * P.lower_ax, sx * P.lower_bx
    t = P.link_t / 2.0
    bar = rect_tube((xa, ya, za), (xb, yb, zb), P.link_t, P.link_h)
    boss = cyl(P.ball_d, (xa - t, ya, za), (xa + t, ya, za))
    ball = cyl(P.ball_d, (xb - t, yb, zb), (xb + t, yb, zb))
    yf, zf = P.lift_pin()
    xf = xa + P.lift_frac * (xb - xa)
    stub = cyl(P.pin_d, (xf, yf, zf), (sx * (P.act_x + 15.0), yf, zf))
    s = bar.fuse([boss, ball, stub]).removeSplitter()
    s = s.cut(cyl(P.pin_d + 0.5, (xa - 15, ya, za), (xa + 15, ya, za)))
    return s.cut(cyl(P.pin_d + 0.5, (xb - 15, yb, zb), (xb + 15, yb, zb)))


def top_link(lift_deg=P.lift_work):
    """Turnbuckle O30 between 2 eyes O40 x 22, from the bracket pin C to the mast pin D (rebuilt per pose)."""
    _, d, _ = P.linkage(lift_deg)
    c = V(0, P.top_c[0], P.top_c[1])
    dd = V(0, d[0], d[1])
    u = dd - c
    u.normalize()
    w = P.top_eye[1] / 2.0
    eyes = [cyl(P.top_eye[0], p - V(w, 0, 0), p + V(w, 0, 0)).cut(cyl(P.pin_d + 0.5, p - V(15, 0, 0), p + V(15, 0, 0)))
            for p in (c, dd)]
    tube = cyl(P.top_link_d, c + u * 40.0, dd - u * 40.0)
    return Part.makeCompound(eyes + [tube])


def actuator(sx, lift_deg=P.lift_work):
    """Lift rod: actuator body with base clevis and pin, rod with an eye that has a slot towards the base."""
    yb, zb = P.act_base
    yr, zr = P.rotate_yz(P.lift_pin(), lift_deg)
    x = sx * P.act_x
    a, b = V(x, yb, zb), V(x, yr, zr)
    u = b - a
    L = u.Length
    u.normalize()
    body_len = P.act_retracted - 75.0
    body = Part.makeCompound([cyl(P.act_body_d, a + u * 20.0, a + u * (20.0 + body_len)),
                              rect_tube(a - u * 14.0, a + u * 20.0, 34.0, 30.0, up=(1.0, 0.0, 0.0)),
                              cyl(12.0, a - V(32, 0, 0), a + V(32, 0, 0))])
    eye = rect_tube(b - u * (P.float_slot + 30.0), b + u * 22.0, 44.0, 20.0, up=(1.0, 0.0, 0.0))
    slot = rect_tube(b - u * (P.float_slot + 8.5), b + u * 8.5, P.pin_d + 1.0, 30.0, up=(1.0, 0.0, 0.0))
    rod = Part.makeCompound([cyl(P.act_rod_d, a + u * (20.0 + body_len - 10.0), b - u * (P.float_slot + 30.0)),
                             eye.cut(slot)])
    return body, rod, L


# ---------------------------------------------------------------------
# Implement: small cultivator on a category 0 frame (work pose, level)
# ---------------------------------------------------------------------
def imp_frame():
    """Weldment: toolbar 60 x 60 x 4, 2 lower hitch lugs, A-frame mast to the top pin, 2 gauge wheel arms."""
    yb, zb = P.lower_b
    yd, zd = P.top_d()
    tz = (zb - P.imp_tb / 2.0, zb + P.imp_tb / 2.0)
    parts = [tube_span((-P.imp_tb_x, P.imp_tb_x), P.imp_tb_y, tz, 4.0, "x")]
    for sx in (-1, 1):
        x0, x1 = sorted((sx * P.imp_lug_x[0], sx * P.imp_lug_x[1]))
        lug = box_span((x0, x1), (P.imp_tb_y[1] - 5.0, yb), tz).fuse(cyl(50.0, (x0, yb, zb), (x1, yb, zb)))
        parts.append(lug)
        top = (sx * (P.top_bracket_x + P.mast_bar[0] / 2.0), yd, zd)
        foot = (sx * P.mast_foot_x, (P.imp_tb_y[0] + P.imp_tb_y[1]) / 2.0, tz[1] - 5.0)
        parts.append(rect_tube(foot, top, P.mast_bar[0], P.mast_bar[1], up=(0.0, 1.0, 0.0)))
        xt0, xt1 = sorted((sx * P.top_bracket_x, sx * (P.top_bracket_x + P.mast_bar[0])))
        parts.append(cyl(46.0, (xt0, yd, zd), (xt1, yd, zd)))
        g0, g1 = sorted((sx * P.gauge_arm_x[0], sx * P.gauge_arm_x[1]))
        zw = P.wheel_d / 2.0
        arm = ((P.imp_tb_y[1] - 5.0, tz[1]), (P.imp_tb_y[0], tz[1]), (P.wheel_y - 25.0, zw + 25.0),
               (P.wheel_y - 25.0, zw - 25.0), (P.wheel_y + 25.0, zw - 25.0), (P.imp_tb_y[1] - 5.0, tz[0]))
        parts.append(plate_yz(arm, g0, g1 - g0))
    s = fuse_all(parts)
    s = s.cut(cyl(P.pin_d + 0.5, (-600, yb, zb), (600, yb, zb)))
    s = s.cut(cyl(P.pin_d + 0.5, (-60, yd, zd), (60, yd, zd)))
    zw = P.wheel_d / 2.0
    return s.cut(cyl(20.5, (-700, P.wheel_y, zw), (700, P.wheel_y, zw)))


def hitch_pins():
    """Lower hitch pins O16 through lug and ball (linch pin outside) and the top pin through the mast (on the
    implement, they move with it)."""
    yb, zb = P.lower_b
    yd, zd = P.top_d()
    out = []
    for sx in (-1, 1):
        x0, x1 = sx * (P.imp_lug_x[0] - 4.0), sx * (P.lower_bx + P.link_t / 2.0 + 12.0)
        out.append(cyl(P.pin_d, (x0, yb, zb), (x1, yb, zb)))
        out.append(cyl(28.0, (x0 - sx * 4.0, yb, zb), (x0, yb, zb)))
    x2 = P.top_bracket_x + P.mast_bar[0] + 6.0
    out.append(cyl(P.pin_d, (-x2, yd, zd), (x2, yd, zd)))
    out.append(cyl(28.0, (x2, yd, zd), (x2 + 4.0, yd, zd)))
    return Part.makeCompound(out)


def tines():
    """S-tines (flat 32 x 10) as straight segments through tine_pts, clamped under the toolbar."""
    out = []
    for x in P.tine_x:
        pts = P.tine_pts
        for p, q in zip(pts[:-1], pts[1:]):
            out.append(rect_tube((x, p[0], p[1]), (x, q[0], q[1]), P.tine_t, P.tine_w, up=(1.0, 0.0, 0.0)))
    return Part.makeCompound(out)


def tine_clamps():
    zb = P.lower_b[1] - P.imp_tb / 2.0
    y0 = P.tine_pts[0][0]
    return Part.makeCompound([box_span((x - 25.0, x + 25.0), (y0 - 25.0, y0 + 25.0), (zb - 10.0, zb))
                              for x in P.tine_x])


def shares():
    """Duckfoot share 100 wide at each tine tip, flat at the working depth."""
    out = []
    yt, zt = P.tine_pts[-1]
    z0 = -P.work_depth
    for x in P.tine_x:
        pts = [V(x, yt + 25.0, z0), V(x + P.share_w / 2.0, yt + 25.0 - P.share_len, z0),
               V(x - P.share_w / 2.0, yt + 25.0 - P.share_len, z0)]
        out.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, 5.0)))
    return Part.makeCompound(out)


def gauge_wheels():
    zw = P.wheel_d / 2.0
    out = []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (P.wheel_x - P.wheel_w / 2.0), sx * (P.wheel_x + P.wheel_w / 2.0)))
        out.append(cyl(P.wheel_d, (x0, P.wheel_y, zw), (x1, P.wheel_y, zw))
                   .cut(cyl(21.0, (x0 - 1, P.wheel_y, zw), (x1 + 1, P.wheel_y, zw))))
    return Part.makeCompound(out)


def wheel_axles():
    zw = P.wheel_d / 2.0
    return Part.makeCompound([cyl(20.0, (sx * (P.gauge_arm_x[0] - 5.0), P.wheel_y, zw),
                                  (sx * (P.wheel_x + P.wheel_w / 2.0 + 6.0), P.wheel_y, zw)) for sx in (-1, 1)])
