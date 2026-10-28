"""Parts of the grassland aerator. Every function returns a Part shape in robot coordinates, in the work pose
(knives 70 mm in the ground). build_gae.py puts the roller frame (arms, cross beam, roller, ballast) in a sub-Part that
turns about the pivot axis; only the actuator is rebuilt per pose.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import gae_params as P


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
# Mount: 2 bridges on the upper beams, hangers, actuator mast (fixed to the robot)
# ---------------------------------------------------------------------
def bridges():
    out = []
    for yr in (P.bridge_front_y, P.bridge_rear_y):
        t = tube_span(P.bridge_x, yr, P.bridge_z, P.bridge_wall, "x")
        yc = (yr[0] + yr[1]) / 2.0
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                t = t.cut(cyl(P.m10_hole, (sx * xb, yc, 600), (sx * xb, yc, 800)))
        out.append(t)
    return Part.makeCompound(out)


def bridge_bolts():
    out = []
    for yr in (P.bridge_front_y, P.bridge_rear_y):
        yc = (yr[0] + yr[1]) / 2.0
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                out.append(bolt_z(10.0, sx * xb, yc, P.robot_upper_beam_z[0], P.bridge_z[1]))
    return Part.makeCompound(out)


def hangers():
    """Plate 10 mm welded to each end face of the front bridge, down and forward to the arm pivot."""
    yp, zp = P.pivot
    out = []
    for sx in (-1, 1):
        x0 = P.hanger_x[0] if sx > 0 else -P.hanger_x[1]
        t = P.hanger_x[1] - P.hanger_x[0]
        pl = plate_yz(P.hanger_pts, x0, t).fuse(cyl(60.0, (x0, yp, zp), (x0 + t, yp, zp)))
        out.append(pl.cut(cyl(P.pivot_d + 0.5, (x0 - 1, yp, zp), (x0 + t + 1, yp, zp))).removeSplitter())
    return Part.makeCompound(out)


def pivot_pins():
    yp, zp = P.pivot
    out = []
    for sx in (-1, 1):
        x_in, x_out = sx * (P.arm_x[0] - 4.0), sx * (P.hanger_x[1] + 6.0)
        out.append(cyl(P.pivot_d, (x_in, yp, zp), (x_out, yp, zp)))
        out.append(cyl(38.0, (x_out, yp, zp), (x_out + sx * 5.0, yp, zp)))             # head outside
        out.append(cyl(5.0, (x_in + sx * 2.0, yp - 20.0, zp), (x_in + sx * 2.0, yp + 20.0, zp)))   # R-clip
    return Part.makeCompound(out)


def act_mast():
    """2 plates 8 mm on top of the rear bridge, leaning forward to the base clevis of the actuator."""
    yb, zb = P.act_base
    y0, y1 = P.bridge_rear_y
    z0 = P.bridge_z[1]
    pts = ((y0, z0), (y1, z0), (yb + 25.0, zb - 60.0), (yb + 25.0, zb + 22.0), (yb - 25.0, zb + 22.0),
           (y0, z0 + 120.0))
    out = []
    for side in (-1, 1):
        x0 = side * P.mast_plate_x + (0.0 if side > 0 else -8.0)
        pl = plate_yz(pts, x0, 8.0)
        out.append(pl.cut(cyl(12.5, (x0 - 1, yb, zb), (x0 + 9, yb, zb))))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Roller frame (turns about the pivot)
# ---------------------------------------------------------------------
def frame():
    """Weldment: 2 side arms 10 mm, cross beam 80 x 80 x 4 between them, ballast tray, 2 rod lugs."""
    parts = [tube_span((-P.arm_x[0], P.arm_x[0]), P.cross_y, P.cross_z, P.cross_wall, "x"),
             box_span((-P.tray_x, P.tray_x), P.tray_y, (P.cross_z[1], P.cross_z[1] + P.tray_t))]
    t = P.arm_x[1] - P.arm_x[0]
    for sx in (-1, 1):
        x0 = P.arm_x[0] if sx > 0 else -P.arm_x[1]
        parts.append(plate_yz(P.arm_pts, x0, t))
        parts.append(cyl(50.0, (x0, P.pivot[0], P.pivot[1]), (x0 + t, P.pivot[0], P.pivot[1])))
    yr, zr = P.rod_pin
    lug = ((P.cross_y[1] - 10.0, P.cross_z[1]), (P.cross_y[0], P.cross_z[1]), (yr - 25.0, zr - 5.0),
           (yr - 25.0, zr + 25.0), (yr + 20.0, zr + 25.0), (P.cross_y[1] - 10.0, zr + 10.0))
    for side in (-1, 1):
        x0 = side * 14.0 + (0.0 if side > 0 else -8.0)
        parts.append(plate_yz(lug, x0, 8.0))
    s = fuse_all(parts)
    s = s.cut(cyl(P.pivot_d + 0.5, (-700, P.pivot[0], P.pivot[1]), (700, P.pivot[0], P.pivot[1])))
    s = s.cut(cyl(13.0, (-40, yr, zr), (40, yr, zr)))
    ya, za = P.axle
    return s.cut(cyl(P.shaft_d + 4.0, (-700, ya, za), (700, ya, za)))


def ballast():
    """2 stacks of 2 blocks of 20 kg on the tray (bolted through with an M12 rod)."""
    out = []
    z0 = P.cross_z[1] + P.tray_t
    for sx in (-1, 1):
        x = sorted((sx * P.ballast_x[0], sx * P.ballast_x[1]))
        for i in range(P.ballast_n):
            out.append(box_span(x, P.tray_y, (z0 + i * P.ballast_h + 0.5 * i, z0 + (i + 1) * P.ballast_h + 0.5 * i)))
    return Part.makeCompound(out)


def bearings():
    """UCFL208 2-bolt flange bearings on the inner faces of the arms."""
    ya, za = P.axle
    t, wy, hz = P.bearing_flange
    d, L = P.bearing_body
    out = []
    for sx in (-1, 1):
        xf = sx * P.arm_x[0]
        fl = box_span(sorted((xf, xf - sx * t)), (ya - wy / 2.0, ya + wy / 2.0), (za - hz / 2.0, za + hz / 2.0))
        body = cyl(d, (xf - sx * t, ya, za), (xf - sx * (t + L), ya, za))
        out.append(fl.fuse(body).cut(cyl(P.shaft_d + 0.5, (xf + sx, ya, za), (xf - sx * 80, ya, za))))
    return Part.makeCompound(out)


def shaft():
    ya, za = P.axle
    return cyl(P.shaft_d, (-P.shaft_x, ya, za), (P.shaft_x, ya, za))


def star(xd, phase):
    """Hub disc with knife_n slitting knives (trapezoid in the disc plane, root at knife_r[0], tip at knife_r[1])."""
    ya, za = P.axle
    hub = cyl(P.hub_d, (xd - P.hub_t / 2.0, ya, za), (xd + P.hub_t / 2.0, ya, za))
    s = hub
    r0, r1 = P.knife_r
    w0, w1 = P.knife_w
    for k in range(P.knife_n):
        a = math.radians(phase + k * 360.0 / P.knife_n)
        u = V(0, math.cos(a), math.sin(a))
        n = V(0, -math.sin(a), math.cos(a))
        c = V(xd - P.knife_t / 2.0, ya, za)
        pts = [c + u * (r0 - 10.0) + n * (w0 / 2.0), c + u * (r1 - 8.0) + n * (w1 / 2.0), c + u * r1,
               c + u * (r1 - 8.0) - n * (w1 / 2.0), c + u * (r0 - 10.0) - n * (w0 / 2.0)]
        s = s.fuse(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(P.knife_t, 0, 0)))
    return s.removeSplitter().cut(cyl(P.shaft_d + 0.5, (xd - 10, ya, za), (xd + 10, ya, za)))


def roller():
    """8 stars, each turned half a knife pitch against its neighbour so the knives enter one after the other."""
    step = 360.0 / P.knife_n / 2.0
    return Part.makeCompound([star(x, -90.0 + (i % 2) * step) for i, x in enumerate(P.disc_x())])


# ---------------------------------------------------------------------
# Actuator (rebuilt per pose)
# ---------------------------------------------------------------------
def actuator(lift_deg=P.lift_work):
    yb, zb = P.act_base
    yr, zr = P.rotate_yz(P.rod_pin, lift_deg)
    a, b = V(0, yb, zb), V(0, yr, zr)
    u = b - a
    L = u.Length
    u.normalize()
    body_len = P.act_retracted - 75.0
    body = Part.makeCompound([cyl(P.act_body_d, a + u * 20.0, a + u * (20.0 + body_len)),
                              rect_tube(a - u * 14.0, a + u * 20.0, 34.0, 30.0, up=(1.0, 0.0, 0.0)),
                              cyl(12.0, a - V(48, 0, 0), a + V(48, 0, 0))])
    rod = Part.makeCompound([cyl(P.act_rod_d, a + u * (20.0 + body_len - 10.0), b - u * 12.0),
                             rect_tube(b - u * 14.0, b + u * 12.0, 22.0, 26.0, up=(1.0, 0.0, 0.0)),
                             cyl(12.0, b - V(30, 0, 0), b + V(30, 0, 0))])
    return body, rod, L
