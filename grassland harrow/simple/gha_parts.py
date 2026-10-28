"""Parts of the grassland harrow. Every function returns a Part shape in robot coordinates, in the work pose
(harrow on the ground). build_gha.py puts the harrow frame in a sub-Part that turns about the pivot axis; only the
actuator is rebuilt per pose. Toolbar, hangers, pivot forks and the actuator are the push blade parts, mirrored.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import gha_params as P


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
# Harrow (turns about the pivot)
# ---------------------------------------------------------------------
def harrow_frame():
    """Weldment: 2 arms 60 x 40 x 3 with pivot bushes, main beam 60 x 60, 2 side members and 2 tine bars 40 x 40,
    actuator lug with the float slot."""
    yp, zp = P.pivot
    mz = P.main_z
    parts = [tube_span((-P.frame_x, P.frame_x), P.main_y, mz, P.main_wall, "x")]
    end = (P.main_y[1], (mz[0] + mz[1]) / 2.0)
    for sx in (-1, 1):
        x = sx * P.arm_x
        parts.append(rect_tube((x, yp, zp), (x, end[0] - 2.0, end[1]), P.arm_h, P.arm_w, P.arm_wall,
                               up=(1.0, 0.0, 0.0)))
        parts.append(cyl(34.0, (x - P.arm_w / 2.0, yp, zp), (x + P.arm_w / 2.0, yp, zp)))
        xs = sx * P.side_x
        parts.append(tube_span((xs - 20.0, xs + 20.0), (P.bar_y[1] - 20.0, P.main_y[0]), P.bar_z, 3.0, "y"))
    for yb in P.bar_y:
        parts.append(tube_span((-P.frame_x, P.frame_x), (yb - 20.0, yb + 20.0), P.bar_z, 3.0, "x"))
    yr, zr = P.act_rod
    for side in (-1, 1):
        x0 = side * 14.0 + (0.0 if side > 0 else -8.0)
        pts = ((P.main_y[0] + 5.0, mz[1]), (P.main_y[1] - 5.0, mz[1]),
               (yr + 25.0, zr + P.float_slot + 20.0), (yr - 25.0, zr + P.float_slot + 20.0))
        parts.append(plate_yz(pts, x0, 8.0))
    s = fuse_all(parts)
    s = s.cut(cyl(P.pivot_d + 0.5, (-700, yp, zp), (700, yp, zp)))
    s = s.cut(box_span((-30, 30), (yr - 6.5, yr + 6.5), (zr - 6.5, zr + P.float_slot + 6.5)))
    for x in P.strap_x:
        s = s.cut(cyl(P.m10_hole + 2.0, (x, P.main_y[0] + 20.0, 0), (x, P.main_y[0] + 20.0, 600)))
    return s


def board():
    """Angle 100 x 100 x 8: upright leg in front (front face at board_y), flat leg trailing back on the ground line
    (minus the working depth)."""
    z0 = -P.board_depth
    yf = P.board_y
    up = box_span((-P.frame_x, P.frame_x), (yf - P.board_t, yf), (z0, z0 + P.board_leg))
    flat = box_span((-P.frame_x, P.frame_x), (yf - P.board_leg, yf), (z0, z0 + P.board_t))
    return up.fuse(flat).removeSplitter()


def board_straps():
    """3 flat bars 60 x 8 on the front of the upright leg, up to a tab under the main beam (M12 through slots)."""
    out = []
    yf = P.board_y
    zt = P.main_z[0]
    for x in P.strap_x:
        bar = box_span((x - P.strap[0] / 2.0, x + P.strap[0] / 2.0), (yf, yf + P.strap[1]),
                       (-P.board_depth + 20.0, zt))
        tab = box_span((x - 30.0, x + 30.0), (yf, P.main_y[0] + 40.0), (zt - 8.0, zt))
        out.append(bar.fuse(tab).removeSplitter())
    return Part.makeCompound(out)


def tine(x, yb):
    """One double spring tine clamped under a tine bar at (x, yb): 2 coils on the bar axis (x), 2 legs down to the
    ground and trailing back by tine_tip_back."""
    zc = P.bar_z[0] - 6.0 - P.coil_d / 2.0 - P.tine_d / 2.0      # coils under the clamp plate
    out = []
    for side in (-1, 1):
        xc = x + side * (P.coil_w / 4.0)
        coil = Part.makeTorus(P.coil_d / 2.0, P.tine_d / 2.0, V(xc, yb, zc), V(1, 0, 0))
        out.append(coil)
        top = V(xc, yb, zc + P.coil_d / 2.0)
        leg0 = V(xc, yb - P.coil_d / 2.0, zc)
        tip = V(xc, yb - P.tine_tip_back, -P.tine_depth)
        out.append(cyl(P.tine_d, leg0, tip))
        out.append(Part.makeSphere(P.tine_d / 2.0, tip))
    # loop between the two coils, held by the clamp
    out.append(cyl(P.tine_d, (x - P.coil_w / 4.0, yb + P.coil_d / 2.0 - 4.0, zc), (x + P.coil_w / 4.0,
                                                                                   yb + P.coil_d / 2.0 - 4.0, zc)))
    return out


def tines():
    shapes = []
    for row, yb in enumerate(P.bar_y):
        for x in P.tine_x(row):
            shapes += tine(x, yb)
    return Part.makeCompound(shapes)


def tine_clamps():
    """Clamp plate 50 x 6 under the bar + U-bolt M8 per tine (drawn as plate + 2 legs)."""
    out = []
    for row, yb in enumerate(P.bar_y):
        for x in P.tine_x(row):
            plate = box_span((x - 25.0, x + 25.0), (yb - 20.0, yb + 20.0), (P.bar_z[0] - 6.0, P.bar_z[0]))
            out.append(plate)
            for dy in (-25.0, 25.0):
                out.append(cyl(8.0, (x, yb + dy, P.bar_z[0] - 10.0), (x, yb + dy, P.bar_z[1] + 4.0)))
            out.append(box_span((x - 6.0, x + 6.0), (yb - 29.0, yb + 29.0), (P.bar_z[1], P.bar_z[1] + 8.0)))
    return Part.makeCompound(out)


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
