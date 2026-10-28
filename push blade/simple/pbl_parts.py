"""Parts of the push blade. Every function returns a Part shape in robot coordinates, in the work pose
(arms down, blade straight). build_pbl.py puts the arms in a sub-Part that turns about the pivot axis and the blade in
a sub-Part that turns about the king pin; only the actuator is rebuilt per pose (it spans the two).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import pbl_params as P


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
# Mount: front toolbar and hangers (fixed to the robot)
# ---------------------------------------------------------------------
def toolbar():
    return tube_span(P.tb_x, P.tb_y, P.tb_z, P.tb_wall, "x")


def toolbar_caps():
    return Part.makeCompound([box_span((x0, x0 + 3.0), P.tb_y, P.tb_z) for x0 in (P.tb_x[0] - 3.0, P.tb_x[1])])


def hanger_top(sx):
    xc = sx * P.hanger_x
    p = box_span((xc - P.hanger_top_w / 2.0, xc + P.hanger_top_w / 2.0), P.hanger_top_y,
                 (P.robot_lower_beam_z[0] - P.hanger_top_t, P.robot_lower_beam_z[0]))
    for y in P.robot_front_beam_y:
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
    for y in P.robot_front_beam_y:
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
    """2 plates on top of the toolbar that carry the base clevis of the actuator."""
    yb, zb = P.act_base
    pts = ((P.tb_y[0], P.tb_z[1]), (P.tb_y[1], P.tb_z[1]), (yb + 30.0, zb + 10.0), (yb - 22.0, zb + 22.0),
           (yb - 22.0, zb - 20.0))
    out = []
    for side in (-1, 1):
        x0 = side * (P.act_body_d / 2.0 + 3.0) + (0.0 if side > 0 else -8.0)
        pl = plate_yz(pts, x0, 8.0).fuse(cyl(44.0, (x0, yb, zb), (x0 + 8.0, yb, zb)))
        out.append(pl.cut(cyl(12.5, (x0 - 1, yb, zb), (x0 + 9, yb, zb))).removeSplitter())
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Lift group (turns about the pivot): carrier weldment
# ---------------------------------------------------------------------
CROSS_Y = (P.king_y - 100.0, P.king_y - 40.0)


def carrier():
    """Weldment: 2 arms (60 x 40 x 3 with a pivot bush), cross tube 60 x 60, round head plate, actuator lug."""
    yp, zp = P.pivot
    hz = P.head_z
    parts = [tube_span(P.cross_x, CROSS_Y, (hz[1], hz[1] + P.cross), P.cross_wall, "x"),
             cyl(P.head_d, (0, P.king_y, hz[0]), (0, P.king_y, hz[1]))]
    end = (CROSS_Y[0], hz[1] + P.cross / 2.0)
    for sx in (-1, 1):
        x = sx * P.arm_x
        parts.append(rect_tube((x, yp, zp), (x, end[0] + 2.0, end[1]), P.arm_h, P.arm_w, P.arm_wall,
                               up=(1.0, 0.0, 0.0)))
        parts.append(cyl(34.0, (x - P.arm_w / 2.0, yp, zp), (x + P.arm_w / 2.0, yp, zp)))
    # actuator lug: 2 plates 8 mm on the cross tube, slot for the rod pin (float)
    yr, zr = P.act_rod
    for side in (-1, 1):
        x0 = side * 14.0 + (0.0 if side > 0 else -8.0)
        pts = ((CROSS_Y[0] + 5.0, hz[1] + P.cross), (CROSS_Y[1] - 5.0, hz[1] + P.cross),
               (yr + 25.0, zr + P.float_slot + 20.0), (yr - 25.0, zr + P.float_slot + 20.0))
        parts.append(plate_yz(pts, x0, 8.0))
    shape = fuse_all(parts)
    hole = cyl(P.pivot_d + 0.5, (-600, yp, zp), (600, yp, zp))
    slot = box_span((-30, 30), (yr - 6.5, yr + 6.5), (zr - 6.5 + 0.0, zr + P.float_slot + 6.5))
    king = cyl(P.king_d + 1.0, (0, P.king_y, hz[0] - 1), (0, P.king_y, hz[1] + 1))
    lock = cyl(P.lock_d + 1.0, (0, P.king_y - P.lock_r, hz[0] - 1), (0, P.king_y - P.lock_r, hz[1] + 1))
    return shape.cut(hole).cut(slot).cut(king).cut(lock)


def lock_pin():
    y = P.king_y - P.lock_r
    return Part.makeCompound([cyl(P.lock_d, (0, y, P.swivel_z[0] - 12.0), (0, y, P.head_z[1] + 2.0)),
                              cyl(24.0, (0, y, P.head_z[1] + 2.0), (0, y, P.head_z[1] + 8.0)),
                              rect_tube((0, y, P.head_z[1] + 30.0), (60, y, P.head_z[1] + 30.0), 8.0, 8.0),
                              cyl(8.0, (0, y, P.head_z[1] + 8.0), (0, y, P.head_z[1] + 30.0))])


def king_pin():
    """M30 bolt from below with a nut on the head plate, PE washer between the plates."""
    y = P.king_y
    return Part.makeCompound([bolt_z(P.king_d, 0, y, P.swivel_z[0], P.head_z[1], head=46.0, k=19.0, m=25.0),
                              cyl(2.0 * (P.lock_r - P.lock_d / 2.0 - 4.0), (0, y, P.swivel_z[1]), (0, y, P.head_z[0])).cut(
                                  cyl(P.king_d + 1.0, (0, y, 0), (0, y, 500)))])


# ---------------------------------------------------------------------
# Blade group (turns about the king pin, inside the lift group)
# ---------------------------------------------------------------------
def _curve(offset, z0=None, z1=None, n=24):
    """Points (y, z) on the moldboard at a normal offset (+ = forward face) from the centre line."""
    z0 = P.steel_bottom if z0 is None else z0
    z1 = P.blade_h if z1 is None else z1
    out = []
    cz = P.steel_bottom
    for i in range(n + 1):
        phi = math.asin((z0 - cz) / P.blade_r) + (math.asin((z1 - cz) / P.blade_r) -
                                                 math.asin((z0 - cz) / P.blade_r)) * i / n
        r = P.blade_r - offset
        out.append((P.edge_y + P.blade_r - r * math.cos(phi), cz + r * math.sin(phi)))
    return out


def moldboard():
    t = P.blade_t
    front = _curve(t / 2.0)
    back = _curve(-t / 2.0)
    pts = front + back[::-1]
    x0 = -P.blade_w / 2.0
    face = Part.Face(Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])]))
    s = face.extrude(V(P.blade_w, 0, 0))
    for x in _edge_bolt_x():
        s = s.cut(cyl(11.0, (x, P.edge_y - 50, _edge_bolt_z()), (x, P.edge_y + 50, _edge_bolt_z())))
    return s


def _edge_bolt_x():
    n = P.edge_bolts
    return [-P.blade_w / 2.0 + 60.0 + (P.blade_w - 120.0) * i / (n - 1) for i in range(n)]


def _edge_bolt_z():
    return P.steel_bottom + 35.0


def rubber_edge():
    y1 = P.edge_y - P.blade_t / 2.0
    s = box_span((-P.blade_w / 2.0, P.blade_w / 2.0), (y1 - P.edge_t, y1), (0.0, P.edge_h))
    for x in _edge_bolt_x():
        s = s.cut(cyl(11.0, (x, y1 - 50, _edge_bolt_z()), (x, y1 + 10, _edge_bolt_z())))
    return s


def clamp_bar():
    y1 = P.edge_y - P.blade_t / 2.0 - P.edge_t
    zc = _edge_bolt_z()
    s = box_span((-P.blade_w / 2.0, P.blade_w / 2.0), (y1 - P.clamp_t, y1), (zc - P.clamp_w / 2.0, zc + P.clamp_w / 2.0))
    for x in _edge_bolt_x():
        s = s.cut(cyl(11.0, (x, y1 - 20, zc), (x, y1 + 10, zc)))
    return s


def edge_bolts():
    yf = _curve(P.blade_t / 2.0, _edge_bolt_z() + 11.0, _edge_bolt_z() + 11.0, 1)[0][0]   # head clear of the curve
    yb = P.edge_y - P.blade_t / 2.0 - P.edge_t - P.clamp_t
    zc = _edge_bolt_z()
    return Part.makeCompound([bolt_axis(10.0, (x, yf, zc), (x, yb, zc), 20.0, 5.0, 8.4) for x in _edge_bolt_x()])


def side_plates():
    """End plates (6 mm) that keep the material in front of the blade."""
    ytop = _curve(P.blade_t / 2.0)[-1][0]
    pts = ((P.edge_y - 40.0, P.steel_bottom), (P.edge_y + 90.0, P.steel_bottom), (ytop + 60.0, P.blade_h),
           (P.edge_y - 40.0, P.blade_h))
    out = []
    for sx in (-1, 1):
        x0 = P.blade_w / 2.0 if sx > 0 else -P.blade_w / 2.0 - P.side_plate_t
        out.append(plate_yz(pts, x0, P.side_plate_t))
    return Part.makeCompound(out)


def blade_frame():
    """Weldment behind the moldboard: beam 80 x 60 x 4, 3 ribs, round swivel plate with the angle-lock holes."""
    y0 = P.edge_y
    bz = P.beam_z
    parts = [tube_span(P.beam_x, (y0 + P.beam_y[0], y0 + P.beam_y[1]), bz, 4.0, "x"),
             cyl(P.head_d, (0, P.king_y, P.swivel_z[0]), (0, P.king_y, P.swivel_z[1])),
             box_span((-90, 90), (P.king_y, y0 + P.beam_y[1]), P.swivel_z)]
    back = _curve(-P.blade_t / 2.0 - 1.0, 125.0, P.blade_h - 15.0, 16)
    rib_pts = back + [(back[-1][0] - 50.0, back[-1][1]), (y0 + P.beam_y[0], bz[1] + 5.0),
                      (y0 + P.beam_y[0], bz[0]), (back[0][0] - 30.0, back[0][1])]
    for x in P.rib_x:
        parts.append(plate_yz(rib_pts, x - P.rib_t / 2.0, P.rib_t))
    s = fuse_all(parts)
    s = s.cut(cyl(P.king_d + 1.0, (0, P.king_y, 0), (0, P.king_y, 500)))
    s = s.cut(cyl(P.head_d + 12.0, (0, P.king_y, P.swivel_z[1]), (0, P.king_y, 600)))   # middle rib clears the head
    for a in P.angle_steps:
        # hole for blade angle a: under the lock pin (rear, -y) when the blade is turned by a
        ang = math.radians(-90.0 - a)
        x, y = P.lock_r * math.cos(ang), P.king_y + P.lock_r * math.sin(ang)
        s = s.cut(cyl(P.lock_d + 1.0, (x, y, 0), (x, y, 500)))
    return s


# ---------------------------------------------------------------------
# Actuator (rebuilt per pose)
# ---------------------------------------------------------------------
def rod_point(lift_deg):
    a = math.radians(lift_deg)
    dy, dz = P.act_rod[0] - P.pivot[0], P.act_rod[1] - P.pivot[1]
    return (P.pivot[0] + dy * math.cos(a) - dz * math.sin(a), P.pivot[1] + dy * math.sin(a) + dz * math.cos(a))


def actuator(lift_deg=P.lift_work):
    """(body, rod) of the linear actuator between the base clevis and the rod pin at this lift angle."""
    yb, zb = P.act_base
    yr, zr = rod_point(lift_deg)
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
