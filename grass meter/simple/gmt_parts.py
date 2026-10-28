"""Parts of the grass meter. Every function returns a Part shape in robot coordinates; the plate meter parts take the
compressed sward height h (mm), so build_gmt can redraw them for another height.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import gmt_params as P



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


def plate_xz(pts, y0, y1):
    """Plate in the x-z plane from a list of (x, z) points, from y0 to y1."""
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, y1 - y0, 0))


def cyl_x(d, x0, x1, y, z):
    return cyl(d, (x0, y, z), (x1, y, z))


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


# ---------------------------------------------------------------------
# Front boom
# ---------------------------------------------------------------------
def brackets():
    """Flat 8 mm on a base plate on top of the front outer lower beam, forward and down to the boom."""
    zt = P.robot_lower_beam_z[1]
    y0, y1 = P.robot_front_beam_y
    yf = y1 + 10.0
    x0 = P.bracket_x - P.bracket[0] / 2.0
    pts = ((y0 - 10.0, zt + P.clamp_t), (P.boom_y[1], zt + P.clamp_t), (P.boom_y[1], P.boom_z[0]), (yf, P.boom_z[0]),
           (yf, zt), (y0 - 10.0, zt))
    flat = plate_yz(pts, x0, P.bracket[0])
    base = box_span((P.bracket_x - 35.0, P.bracket_x + 35.0), (y0 - 10.0, y1 + 10.0), (zt, zt + P.clamp_t))
    b = flat.fuse(base).removeSplitter()
    for xb in (125.0, 175.0):
        b = b.cut(cyl(P.m10_hole, (xb, (y0 + y1) / 2.0, zt - 1), (xb, (y0 + y1) / 2.0, zt + P.clamp_t + 1)))
    return both(b.cut(box_span((x0 - 1, x0 + P.bracket[0] + 1), P.boom_y, P.boom_z)))


def bracket_bolts():
    zb = P.robot_lower_beam_z
    yc = sum(P.robot_front_beam_y) / 2.0
    return both(Part.makeCompound([bolt_z(10.0, xb, yc, zb[0], zb[1] + P.clamp_t) for xb in (125.0, 175.0)]))


def boom():
    return tube_span((-P.boom_x, P.boom_x), P.boom_y, P.boom_z, 3.0, "x")


def ndvi_sensors():
    """2 active NDVI sensors in front of the boom on a small angle bracket."""
    w, d, h = P.ndvi_box
    y0 = P.boom_y[1] + 5.0
    box = box_span((P.ndvi_x - w / 2, P.ndvi_x + w / 2), (y0, y0 + d), (P.ndvi_z, P.ndvi_z + h))
    lens = cyl(30.0, (P.ndvi_x, y0 + d / 2, P.ndvi_z - 4.0), (P.ndvi_x, y0 + d / 2, P.ndvi_z))
    return both(box.fuse(lens))


def sensor_brackets():
    """Angle 40 x 4 from the boom front face to each sensor (NDVI x2, lidar)."""
    out = []
    for x, w in ((P.ndvi_x, P.ndvi_box[0]), (-P.ndvi_x, P.ndvi_box[0]), (P.lidar_x, P.lidar_box[0])):
        out.append(box_span((x - w / 2, x + w / 2), (P.boom_y[1], P.boom_y[1] + 5.0), (P.boom_z[0] - 30.0, P.boom_z[1])))
    return Part.makeCompound(out)


def lidar():
    w, d, h = P.lidar_box
    y0 = P.boom_y[1] + 5.0
    z0 = P.boom_z[1] - h
    return box_span((P.lidar_x - w / 2, P.lidar_x + w / 2), (y0, y0 + d), (z0, z0 + h)).fuse(
        cyl(30.0, (P.lidar_x, y0 + d / 2, z0 - 6.0), (P.lidar_x, y0 + d / 2, z0)))


def camera():
    """Mast O25 on the boom (x 200) and an RGB camera at the top, tilted down."""
    xm = 200.0
    yc = sum(P.boom_y) / 2.0
    z0 = P.boom_z[1]
    mast = cyl(P.cam_mast[0], (xm, yc, z0), (xm, yc, z0 + P.cam_mast[1]))
    w, d, h = P.cam_box
    cam = box_span((xm - w / 2, xm + w / 2), (-d / 2, d / 2), (0.0, h)).fuse(cyl(40.0, (xm, d / 2, h / 2), (xm, d / 2 + 25.0, h / 2)))
    cam.rotate(V(xm, 0, 0), V(1, 0, 0), -P.cam_tilt)
    cam.translate(V(0, yc + 20.0, z0 + P.cam_mast[1]))
    return mast, cam


def logger():
    w, d, h = P.logger_box
    yc = sum(P.boom_y) / 2.0
    return box_span((-300.0 - w / 2, -300.0 + w / 2), (yc - d / 2, yc + d / 2), (P.boom_z[1], P.boom_z[1] + h))


# ---------------------------------------------------------------------
# Plate meter (bearer and post fixed, arms and plate move with the sward height)
# ---------------------------------------------------------------------
def bearer():
    y = (P.bearer_y - P.bearer / 2, P.bearer_y + P.bearer / 2)
    z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + P.bearer)
    t = tube_span((-P.bearer_x, P.bearer_x), y, z, 3.0, "x")
    for sx in (-1, 1):
        for xb in P.robot_upper_beam_x:
            t = t.cut(cyl(P.m10_hole, (sx * xb, P.bearer_y, 600), (sx * xb, P.bearer_y, 800)))
    return t


def bearer_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * xb, P.bearer_y, P.robot_upper_beam_z[0], P.robot_upper_beam_z[1] + P.bearer)
                              for sx in (-1, 1) for xb in P.robot_upper_beam_x])


def post():
    """Tube 40 x 40 x 3 hanging from under the bearer to below the pivots, cap plate bolted to the bearer, actuator lug."""
    z1 = P.robot_upper_beam_z[1]
    yb = P.pivot_y
    p = tube_span((-P.post / 2, P.post / 2), (yb - P.post / 2, yb + P.post / 2), (P.pivot_z[1] - 30.0, z1 - 8.0), 3.0, "z")
    cap = box_span((-60.0, 60.0), (yb - P.post / 2 - 20.0, yb + P.post / 2 + 20.0), (z1 - 8.0, z1))
    ya, za = P.act_base
    lug = box_span((P.post / 2, P.act_x - P.act_body_d / 2 - 1.0), (ya - 15.0, ya + 15.0), (za - 15.0, za + 15.0))
    s = p.fuse(cap).fuse(lug).removeSplitter()
    for z in P.pivot_z:
        s = s.cut(cyl_x(10.5, -30, 30, yb, z))
    return s


def post_bolts():
    """The bearer sits on the beams: the post hangs between them from 2 M8 through the bearer bottom wall."""
    z1 = P.robot_upper_beam_z[1]
    return Part.makeCompound([bolt_z(8.0, sx * 45.0, P.pivot_y, z1 - 8.0, z1 + 3.0, head=13.0, k=5.3, m=6.8)
                              for sx in (-1, 1)])


def plate_frame_pts(h):
    """(y, z) of the lower and upper arm ends at a compressed height h."""
    return P.arm_end(P.pivot_z[1], h), P.arm_end(P.pivot_z[0], h)


def arms(h=P.sward_h):
    """4 tubes 20 x 20 x 2 (2 upper, 2 lower) between the post pivots and the plate bracket."""
    out = []
    for i, zp in enumerate((P.pivot_z[1], P.pivot_z[0])):
        e = plate_frame_pts(h)[i]
        for sx in (-1, 1):
            x = sx * P.arm_x
            out.append(rect_tube((x, P.pivot_y, zp), (x, e[0], e[1]), P.arm, P.arm, 2.0, up=(0.0, 0.0, 1.0)))
    yr, zr = act_point(h)
    out.append(rect_tube((-P.arm_x + P.arm / 2, yr, zr), (P.arm_x - P.arm / 2, yr, zr), 16.0, 16.0, 2.0))
    return Part.makeCompound(out)


def act_point(h):
    """(y, z) of the actuator rod pin on the cross bar between the upper arms."""
    (yu, zu) = plate_frame_pts(h)[1]
    return P.pivot_y + P.act_arm * (yu - P.pivot_y), P.pivot_z[0] + P.act_arm * (zu - P.pivot_z[0])


def arm_pins(h=P.sward_h):
    out = [cyl_x(10.0, -P.arm_x - 16.0, P.arm_x + 16.0, P.pivot_y, z) for z in P.pivot_z]
    for e in plate_frame_pts(h):
        out.append(cyl_x(10.0, -P.arm_x - 16.0, P.arm_x + 16.0, e[0], e[1]))
    return Part.makeCompound(out)


def plate(h=P.sward_h):
    """Plate 316 x 316 x 5 PE with a turned-up front lip, centred under the arm ends, and its bracket (2 plates 6 mm)."""
    (yl, zl), (yu, zu) = plate_frame_pts(h)
    s = P.plate_side
    yc = yl - 20.0
    pl = box_span((-s / 2, s / 2), (yc - s / 2, yc + s / 2), (h, h + P.plate_t))
    a = math.radians(30.0)
    lip = box_span((-s / 2, s / 2), (0.0, P.plate_lip), (0.0, P.plate_t))
    lip.rotate(V(0, 0, 0), V(1, 0, 0), 30.0)
    lip.translate(V(0, yc + s / 2, h))
    brk = []
    for sx in (-1, 1):
        x0 = sx * (P.arm_x + P.arm / 2 + 1.0) + (0.0 if sx > 0 else -6.0)
        pts = ((yl - 30.0, h + P.plate_t), (yl + 30.0, h + P.plate_t), (yu + 15.0, zu + 15.0), (yu - 15.0, zu + 15.0))
        brk.append(plate_yz(pts, x0, 6.0))
    return Part.makeCompound([pl, lip]), Part.makeCompound(brk)


def encoder():
    """Angle sensor on the right end of the upper pivot pin."""
    return cyl_x(P.encoder_d, P.arm_x + 18.0, P.arm_x + 48.0, P.pivot_y, P.pivot_z[0])


def actuator(h=P.sward_h):
    """(body, rod, length) of the lift actuator from the post lug to the upper arm."""
    ya, za = P.act_base
    yr, zr = act_point(h)
    A, B = V(P.act_x, ya, za), V(P.act_x, yr, zr)
    u = B - A
    L = u.Length
    u.normalize()
    body = cyl(P.act_body_d, A + u * 10.0, A + u * 150.0)
    rod = Part.makeCompound([cyl(P.act_rod_d, A + u * 140.0, B - u * 20.0), cyl(18.0, B - u * 20.0, B - u * 9.0)])
    return body, rod, L
