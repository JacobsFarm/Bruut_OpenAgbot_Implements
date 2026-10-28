"""Parts of the mulch layer (the implement only; the hitch comes from "three point hitch/simple"). Every function
returns a Part shape in robot coordinates, in the work pose; build_mly moves the implement with the hitch.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mly_params as P



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




def cyl_x(d, x0, x1, y, z):
    return cyl(d, (x0, y, z), (x1, y, z))


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


# ---------------------------------------------------------------------
# Frame (work pose; build_mly moves it with the hitch)
# ---------------------------------------------------------------------
def frame():
    """Weldment: toolbar 60 x 60 x 4, 2 lower hitch lugs, A-frame mast, stands, 2 side beams 50 x 50 x 3, rear cross
    tube, roll holders (V-slot) and guide bar brackets."""
    yb, zb = P.lower_b
    yd, zd = P.top_d
    tz = (zb - P.tb / 2.0, zb + P.tb / 2.0)
    xo = P.side_x[1]
    parts = [tube_span((-xo, xo), P.tb_y, tz, 4.0, "x"),
             tube_span((-xo, xo), P.rear_y, P.side_z, P.wall, "x")]
    for sx in (-1, 1):
        x0, x1 = sorted((sx * P.imp_lug_x[0], sx * P.imp_lug_x[1]))
        parts.append(box_span((x0, x1), (P.tb_y[1] - 5.0, yb), tz).fuse(cyl(50.0, (x0, yb, zb), (x1, yb, zb))))
        top = (sx * (P.top_bracket_x + P.mast_bar[0] / 2.0), yd, zd)
        foot = (sx * P.mast_foot_x, (P.tb_y[0] + P.tb_y[1]) / 2.0, tz[1] - 5.0)
        parts.append(rect_tube(foot, top, P.mast_bar[0], P.mast_bar[1], up=(0.0, 1.0, 0.0)))
        xt0, xt1 = sorted((sx * P.top_bracket_x, sx * (P.top_bracket_x + P.mast_bar[0])))
        parts.append(cyl(46.0, (xt0, yd, zd), (xt1, yd, zd)))
        xs = sorted((sx * P.side_x[0], sx * P.side_x[1]))
        parts.append(tube_span(xs, (P.side_y[0], P.side_y[1]), P.side_z, P.wall, "y"))
        parts.append(box_span(xs, P.tb_y, (tz[1], P.side_z[0])))
        # roll holder: plate inside the side beam with an open V-slot for the roll shaft
        xh = sorted((sx * (P.side_x[0] - P.holder_t), sx * P.side_x[0]))
        h = box_span(xh, (P.roll_y - 45.0, P.roll_y + 45.0), (P.side_z[0], P.roll_z + 40.0))
        slot = box_span((xh[0] - 1, xh[1] + 1), (P.roll_y - P.roll_shaft_d / 2 - 0.5, P.roll_y + P.roll_shaft_d / 2 + 0.5),
                        (P.roll_z, P.roll_z + 50.0))
        parts.append(h.cut(slot).cut(cyl_x(P.roll_shaft_d + 1.0, xh[0] - 1, xh[1] + 1, P.roll_y, P.roll_z)))
        # guide bar bracket
        parts.append(box_span(xh, (P.guide_y - 30.0, P.guide_y + 30.0), (P.guide_z - 25.0, P.side_z[0])))
    s = fuse_all(parts)
    s = s.cut(cyl(P.pin_d + 0.5, (-800, yb, zb), (800, yb, zb)))
    return s.cut(cyl(P.pin_d + 0.5, (-60, yd, zd), (60, yd, zd)))


def hitch_pins():
    yb, zb = P.lower_b
    yd, zd = P.top_d
    out = []
    for sx in (-1, 1):
        x0, x1 = sx * (P.imp_lug_x[0] - 4.0), sx * (P.lower_bx + P.link_t / 2.0 + 12.0)
        out.append(cyl(P.pin_d, (x0, yb, zb), (x1, yb, zb)))
        out.append(cyl(28.0, (x0 - sx * 4.0, yb, zb), (x0, yb, zb)))
    x2 = P.top_bracket_x + P.mast_bar[0] + 6.0
    out.append(cyl(P.pin_d, (-x2, yd, zd), (x2, yd, zd)))
    out.append(cyl(28.0, (x2, yd, zd), (x2 + 4.0, yd, zd)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Foil roll, brake, guide bar
# ---------------------------------------------------------------------
def roll():
    w = P.foil_w / 2.0
    return cyl_x(P.roll_d, -w, w, P.roll_y, P.roll_z).cut(cyl_x(P.core_d - 10.0, -w - 1, w + 1, P.roll_y, P.roll_z))


def roll_core():
    """Cardboard core O76 and 2 cone chucks on the shaft."""
    w = P.foil_w / 2.0
    core = cyl_x(P.core_d, -w, w, P.roll_y, P.roll_z).cut(cyl_x(P.core_d - 10.0, -w - 1, w + 1, P.roll_y, P.roll_z))
    chucks = [Part.makeCone(P.core_d / 2.0 + 8.0, P.roll_shaft_d / 2.0 + 4.0, 14.0, V(sx * (w + 1.0), P.roll_y, P.roll_z),
                            V(sx, 0, 0)).cut(cyl_x(P.roll_shaft_d, -w - 40, w + 40, P.roll_y, P.roll_z)) for sx in (-1, 1)]
    return Part.makeCompound([core] + chucks)


def roll_shaft():
    x = P.side_x[0] + 4.0
    return cyl_x(P.roll_shaft_d, -x, x, P.roll_y, P.roll_z).cut(cyl_x(P.roll_shaft_d - 6.0, -x - 1, x + 1, P.roll_y, P.roll_z))


def brake():
    """Brake drum on the shaft (left) and a band with a spring to the side beam (drawn as a ring)."""
    x0 = -(P.side_x[0] - P.holder_t - 2.0)
    drum = cyl_x(P.brake_d, x0, x0 + 10.0, P.roll_y, P.roll_z).cut(cyl_x(P.roll_shaft_d, x0 - 1, x0 + 11, P.roll_y, P.roll_z))
    band = cyl_x(P.brake_d + 6.0, x0 + 2.0, x0 + 8.0, P.roll_y, P.roll_z).cut(cyl_x(P.brake_d, x0, x0 + 10, P.roll_y, P.roll_z))
    return drum, band


def guide_bar():
    x = P.side_x[0] - P.holder_t
    return cyl_x(P.guide_d, -x, x, P.guide_y, P.guide_z).cut(cyl_x(P.guide_d - 4.0, -x - 1, x + 1, P.guide_y, P.guide_z))


def foil_path():
    """(y, z) points of the lower face of the foil: off the roll, under the guide bar, down to the bed, flat behind."""
    return [(P.roll_y - 10.0, P.roll_z - P.roll_d / 2.0 + 1.0), (P.guide_y, P.guide_z - P.guide_d / 2.0 - 1.5),
            (P.guide_y - 60.0, 0.5), (-2400.0, 0.5)]


def foil():
    pts = foil_path()
    up = [(y, z + 1.0) for y, z in reversed(pts)]
    return plate_yz(pts + up, -P.foil_w / 2.0, P.foil_w)


# ---------------------------------------------------------------------
# Press wheels and covering discs
# ---------------------------------------------------------------------
def press_wheels():
    zc = P.press_d / 2.0
    x0, x1 = P.press_x - P.press_w / 2, P.press_x + P.press_w / 2
    tyre = cyl_x(P.press_d, x0, x1, P.press_y, zc).cut(cyl_x(P.press_d - 40.0, x0 - 1, x1 + 1, P.press_y, zc))
    return both(tyre)


def press_rims():
    """Steel rims (disc 4 mm with a hub) inside the semi-pneumatic press tyres."""
    zc = P.press_d / 2.0
    rim = cyl_x(P.press_d - 40.0, P.press_x - 30.0, P.press_x + 30.0, P.press_y, zc).cut(
        cyl_x(P.press_d - 48.0, P.press_x - 31.0, P.press_x + 31.0, P.press_y, zc))
    web = cyl_x(P.press_d - 44.0, P.press_x - 2.0, P.press_x + 2.0, P.press_y, zc)
    hub = cyl_x(45.0, P.press_x - 40.0, P.press_x + 40.0, P.press_y, zc)
    r = rim.fuse(web).fuse(hub).removeSplitter().cut(cyl_x(20.5, P.press_x - 50, P.press_x + 50, P.press_y, zc))
    return both(r)


def press_arms():
    """Plate 10 mm from the wheel axle up to a block under the side beam, axle O20."""
    zc = P.press_d / 2.0
    x0 = P.press_x + P.press_w / 2 + 5.0
    pts = ((P.press_y - 20.0, zc - 20.0), (P.press_y + 20.0, zc - 20.0), (P.press_y + 120.0, P.side_z[0]),
           (P.press_y + 60.0, P.side_z[0]))
    arm = plate_yz(pts, x0, P.press_arm[0]).fuse(cyl_x(40.0, x0, x0 + P.press_arm[0], P.press_y, zc))
    block = box_span((x0, P.side_x[0]), (P.press_y + 60.0, P.press_y + 120.0), (P.side_z[0] - 40.0, P.side_z[0]))
    arm = arm.fuse(block).removeSplitter()
    axle = cyl_x(20.0, P.press_x - P.press_w / 2 - 6.0, x0 + P.press_arm[0], P.press_y, zc)
    return both(arm.cut(cyl_x(20.5, x0 - 1, x0 + 11, P.press_y, zc))), both(axle)


def _disc_place(shape, sx):
    """Disc built about the x axis at the origin, then tilted (top inwards), angled to the travel, moved to place."""
    zc = P.disc_d / 2.0 - P.disc_depth
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 1, 0), -P.disc_tilt)
    s.rotate(V(0, 0, 0), V(0, 0, 1), P.disc_yaw)
    s.translate(V(P.disc_x, P.disc_y, zc))
    return s if sx > 0 else mirror_x(s)


def discs():
    """Concave discs O350 x 4 (the dish is drawn as a shallow cone), concave side facing the foil."""
    r = P.disc_d / 2.0
    cone = Part.makeCone(r, 40.0, P.disc_dish, V(-P.disc_dish / 2.0, 0, 0), V(1, 0, 0))
    inner = Part.makeCone(r, 40.0, P.disc_dish, V(-P.disc_dish / 2.0 - P.disc_t, 0, 0), V(1, 0, 0))
    d = cone.cut(inner)
    hub = cyl_x(80.0, P.disc_dish / 2.0 - 4.0, P.disc_dish / 2.0 + 25.0, 0.0, 0.0)
    one = d.fuse(hub).removeSplitter()
    return Part.makeCompound([_disc_place(one, sx) for sx in (-1, 1)])


def disc_arms():
    """Stub shaft from the hub out along the disc axis, a block, a flat 60 x 10 up and a plate over to the side beam."""
    stub = cyl_x(P.disc_stub_d, P.disc_dish / 2.0 + 25.0, P.disc_dish / 2.0 + 75.0, 0.0, 0.0)
    blk = box_span((P.disc_dish / 2.0 + 75.0, P.disc_dish / 2.0 + 95.0), (-30.0, 30.0), (-30.0, 30.0))
    s = _disc_place(stub.fuse(blk), 1)
    bb = s.BoundBox
    yc = (bb.YMin + bb.YMax) / 2.0
    xa = bb.XMax
    arm = box_span((xa - 10.0, xa), (yc - 30.0, yc + 30.0), (bb.ZMin, P.side_z[1]))
    top = box_span((P.side_x[1], xa - 10.0), (yc - 30.0, yc + 30.0), (P.side_z[0], P.side_z[1]))
    return both(Part.makeCompound([s, arm, top]))


def ridges():
    """Soil thrown onto the foil edges behind the discs (picture only)."""
    w, h = P.ridge
    out = []
    for sx in (-1, 1):
        xc = sx * (P.foil_w / 2.0 + 10.0)
        pts = [(xc - w / 2.0, 0.0), (xc + w / 2.0, 0.0), (xc, h)]
        wire = Part.makePolygon([V(x, P.disc_y - 60.0, z) for x, z in pts] + [V(pts[0][0], P.disc_y - 60.0, 0.0)])
        out.append(Part.Face(wire).extrude(V(0, -2400.0 - (P.disc_y - 60.0), 0)))
    return Part.makeCompound(out)
