"""Parts of the soil compaction meter. Every function returns a Part shape in robot coordinates (moving parts in the
park pose; build_scm moves the Carriage and Foot groups).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import scm_params as P



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




def shell(d_out, d_in, p0, p1):
    return cyl(d_out, p0, p1).cut(cyl(d_in, p0, p1))


PARK_C = P.carriage_z(P.tip_park)


# ---------------------------------------------------------------------
# Mount: 2 bridges, stays, logger
# ---------------------------------------------------------------------
def bridges():
    out = []
    for yr in (P.bridge_front_y, P.bridge_rear_y):
        t = tube_span(P.bridge_x, yr, P.bridge_z, 3.0, "x")
        yc = (yr[0] + yr[1]) / 2.0
        for sx in (-1, 1):
            t = t.cut(cyl(P.m10_hole, (sx * P.bridge_bolt_x, yc, 600), (sx * P.bridge_bolt_x, yc, 800)))
        if yr == P.bridge_front_y:
            for sx in (-1, 1):
                t = t.cut(cyl(8.4, (sx * 60.0, 0.0, P.bridge_z[0] + 20.0), (sx * 60.0, 200.0, P.bridge_z[0] + 20.0)))
        out.append(t)
    return Part.makeCompound(out)


def bridge_bolts():
    out = []
    for yr in (P.bridge_front_y, P.bridge_rear_y):
        yc = (yr[0] + yr[1]) / 2.0
        for sx in (-1, 1):
            out.append(bolt_z(10.0, sx * P.bridge_bolt_x, yc, P.robot_upper_beam_z[0], P.bridge_z[1]))
    return Part.makeCompound(out)


def stays():
    """Flat 40 x 6 from the bottom corners of the mast plate up to the rear bridge."""
    w, t = P.stay
    out = []
    for sx in (-1, 1):
        x0 = sx * (P.mast_x + 2.0) + (0.0 if sx > 0 else -t)
        a = (P.mast_y[1] - 5.0, P.mast_z[0] + 40.0)
        b = (P.bridge_rear_y[1] - 5.0, P.bridge_z[0])
        d = V(0, b[0] - a[0], b[1] - a[1])
        d.normalize()
        n = V(0, -d.z, d.y) * (w / 2.0)
        pts = ((a[0] + n.y, a[1] + n.z), (b[0] + n.y, b[1] + n.z), (b[0] - n.y, b[1] - n.z), (a[0] - n.y, a[1] - n.z))
        out.append(plate_yz(pts, x0, t))
        # tabs: to the mast side edge and under the rear bridge
        out.append(box_span((min(x0, sx * P.mast_x), max(x0 + t, sx * P.mast_x)), P.mast_y,
                            (P.mast_z[0] + 15.0, P.mast_z[0] + 65.0)))
        out.append(box_span((x0, x0 + t), (b[0] - 25.0, P.bridge_rear_y[1]), (P.bridge_z[0] - 30.0, P.bridge_z[0])))
    return Part.makeCompound(out)


def logger():
    w, d, h = P.logger_box
    yc = sum(P.bridge_rear_y) / 2.0
    return box_span((-w / 2, w / 2), (yc - d / 2, yc + d / 2), (P.bridge_z[1], P.bridge_z[1] + h))


# ---------------------------------------------------------------------
# Z axis (fixed part)
# ---------------------------------------------------------------------
def mast():
    """Mast plate 10 mm against the front bridge, bottom bearing block, motor plate on top."""
    z0, z1 = P.mast_z
    plate = box_span((-P.mast_x, P.mast_x), P.mast_y, (z0, z1))
    for sx in (-1, 1):
        plate = plate.cut(cyl(8.4, (sx * 60.0, 40.0, P.bridge_z[0] + 20.0), (sx * 60.0, 120.0, P.bridge_z[0] + 20.0)))
    bottom = box_span((-30.0, 30.0), (P.screw_y - 18.0, P.mast_y[0]), (z0, z0 + 25.0))
    top = box_span((-45.0, 45.0), (P.screw_y - 40.0, P.mast_y[1]), (z1, z1 + 10.0))
    s = plate.fuse(bottom).fuse(top).removeSplitter()
    return s.cut(cyl(P.screw_d + 1.0, (0, P.screw_y, z0 - 1), (0, P.screw_y, z1 + 11)))


def mast_bolts():
    return Part.makeCompound([bolt_axis(8.0, (sx * 60.0, P.mast_y[0], P.bridge_z[0] + 20.0),
                                        (sx * 60.0, P.bridge_front_y[1], P.bridge_z[0] + 20.0), 13.0, 5.3, 6.8)
                              for sx in (-1, 1)])


def rails():
    z0, z1 = P.mast_z[0] + 30.0, P.mast_z[1] - 5.0
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        out.append(box_span((x - 12.0, x + 12.0), (P.rail_y[0] + 20.0, P.rail_y[1]), (z0, z1)))
        out.append(cyl(20.0, (x, P.rail_y[0] + 10.0, z0), (x, P.rail_y[0] + 10.0, z1)))
    return Part.makeCompound(out)


def screw():
    z0, z1 = P.mast_z
    return cyl(P.screw_d, (0, P.screw_y, z0 + 2.0), (0, P.screw_y, z1 + 40.0))


def z_motor():
    z1 = P.mast_z[1] + 10.0
    a, L = P.motor
    return Part.makeCompound([cyl(30.0, (0, P.screw_y, z1), (0, P.screw_y, z1 + 35.0)),
                              box_span((-a / 2.0, a / 2.0), (P.screw_y - a / 2.0, P.screw_y + a / 2.0),
                                       (z1 + 35.0, z1 + 35.0 + L))])


# ---------------------------------------------------------------------
# Carriage (moves in z, drawn in park): plate, rail blocks, nut, holder; load cell, clamp, rod with cone
# ---------------------------------------------------------------------
def carriage():
    c = PARK_C
    h = P.carriage_h
    parts = [box_span((-P.carriage_w, P.carriage_w), (P.carriage_y[0], 0.0), (c, c + h)),
             box_span((-25.0, 25.0), (0.0, P.screw_y + 14.0), (c + 40.0, c + 100.0)),
             box_span((-70.0, 70.0), P.holder_y, (c, c + P.holder_h))]
    for sx in (-1, 1):
        for z in (c + 5.0, c + h - 45.0):
            parts.append(box_span((sx * P.rail_x - 22.0, sx * P.rail_x + 22.0), (0.0, P.rail_y[0]), (z, z + 40.0)))
    s = fuse_all(parts)
    s = s.cut(cyl(P.screw_d + 1.0, (0, P.screw_y, c - 1), (0, P.screw_y, c + h + 1)))
    for sx in (-1, 1):
        s = s.cut(cyl(11.0, (sx * P.foot_rod_x, P.rod_y, c - 1), (sx * P.foot_rod_x, P.rod_y, c + P.holder_h + 1)))
    return s


def loadcell():
    """S-type load cell under the holder."""
    w, h, d = P.loadcell
    c = PARK_C
    body = box_span((-w / 2, w / 2), (P.rod_y - d / 2, P.rod_y + d / 2), (c - h, c))
    return body.cut(box_span((-w / 2 - 1, w / 2 - 12.0), (P.rod_y - d / 2 - 1, P.rod_y + d / 2 + 1), (c - h + 15.0, c - h / 2 - 3.0))).cut(
        box_span((-w / 2 + 12.0, w / 2 + 1), (P.rod_y - d / 2 - 1, P.rod_y + d / 2 + 1), (c - h / 2 + 3.0, c - 15.0)))


def clamp():
    c = PARK_C - P.loadcell[1]
    blk = box_span((-25.0, 25.0), (P.rod_y - 20.0, P.rod_y + 20.0), (c - P.clamp_h, c))
    return blk.cut(cyl(P.rod_d, (0, P.rod_y, c - P.clamp_h - 1), (0, P.rod_y, c - 10.0)))


def rod():
    """Rod O9.5 with the 30 degree cone O12.83 at the tip."""
    top = PARK_C - P.loadcell[1] - 10.0
    tip = P.tip_park
    cone_h = P.cone_d / 2.0 / math.tan(math.radians(P.cone_angle / 2.0))
    r = cyl(P.rod_d, (0, P.rod_y, tip + cone_h), (0, P.rod_y, top))
    cone = Part.makeCone(0.0, P.cone_d / 2.0, cone_h, V(0, P.rod_y, tip), V(0, 0, 1))
    return r.fuse(cone).removeSplitter()


# ---------------------------------------------------------------------
# Foot with moisture probe (hangs under the holder until it rests on the ground)
# ---------------------------------------------------------------------
def foot():
    z0 = P.tip_park - P.foot_drop
    # PE ring with a PTFE bush that guides the rod at the ground (no buckling of the free rod length)
    out = [shell(P.foot_d, P.rod_d + 0.5, (0, P.rod_y, z0), (0, P.rod_y, z0 + P.foot_t)),
           shell(26.0, P.rod_d + 0.5, (0, P.rod_y, z0 + P.foot_t), (0, P.rod_y, z0 + P.foot_t + 25.0))]
    for sx in (-1, 1):
        x = sx * P.foot_rod_x
        ztop = z0 + P.foot_t + P.foot_rod_len
        out.append(cyl(10.0, (x, P.rod_y, z0 + P.foot_t), (x, P.rod_y, ztop)))
        out.append(cyl(18.0, (x, P.rod_y, ztop), (x, P.rod_y, ztop + 8.0)))
    return Part.makeCompound(out)


def moisture_probe():
    """Capacitive probe on the foot ring (y +), 2 tines 60 mm into the soil when the foot is down."""
    z0 = P.tip_park - P.foot_drop
    w, d, h = P.moist_box
    y = P.rod_y + P.foot_d / 2.0 - d / 2.0 - 5.0
    box = box_span((-w / 2, w / 2), (y - d / 2, y + d / 2), (z0 + P.foot_t, z0 + P.foot_t + h))
    tines = [cyl(P.moist_tine[0], (sx * 10.0, y, z0 - P.moist_tine[1]), (sx * 10.0, y, z0 + P.foot_t)) for sx in (-1, 1)]
    return Part.makeCompound([box] + tines)
