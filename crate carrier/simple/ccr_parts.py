"""Parts of the crate carrier. Every function returns a Part shape in robot coordinates. Nothing moves: the deck is
bolted on the upper beams, the crates and straps are the load.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ccr_params as P


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
# Deck (bolted on the upper beams)
# ---------------------------------------------------------------------
def bearers():
    """3 tubes 40 x 40 x 3 across, on top of the upper beams, holes for 4 x M10 each."""
    out = []
    xs = (-P.deck_x + P.side_rail, P.deck_x - P.side_rail)
    for yc in P.bearer_y:
        t = tube_span(xs, (yc - P.bearer / 2.0, yc + P.bearer / 2.0), P.bearer_z, 3.0, "x")
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                t = t.cut(cyl(P.m10_hole, (sx * xb, yc, 600), (sx * xb, yc, 800)))
        out.append(t)
    return Part.makeCompound(out)


def bearer_bolts():
    out = []
    for yc in P.bearer_y:
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                out.append(bolt_z(10.0, sx * xb, yc, P.robot_upper_beam_z[0], P.bearer_z[1]))
    return Part.makeCompound(out)


def side_rails():
    """2 tubes 40 x 40 x 3 along y at the deck edges, the bearers end against them."""
    return Part.makeCompound([tube_span(sorted((sx * P.deck_x, sx * (P.deck_x - P.side_rail))), P.deck_y,
                                        P.bearer_z, 3.0, "y") for sx in (-1, 1)])


def plywood():
    s = box_span((-P.deck_x, P.deck_x), P.deck_y, (P.bearer_z[1], P.deck_z))
    for yc in P.bearer_y:                       # clearance for the bolt heads on the bearers
        for sx in (-1, 1):
            for xb in P.robot_upper_beam_x:
                s = s.cut(cyl(30.0, (sx * xb, yc, P.bearer_z[1] - 1), (sx * xb, yc, P.bearer_z[1] + 12.0)))
    return s


def guides():
    """Angle 30 x 30 x 3 on both sides and the rear edge, flat bar divider along x = 0."""
    a, t = P.guide
    z0 = P.deck_z
    out = []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * P.deck_x, sx * (P.deck_x - a)))
        flat = box_span((x0, x1), (P.deck_y[0], P.head_y[0]), (z0, z0 + t))
        xu = sorted((sx * P.deck_x, sx * (P.deck_x - t)))
        up = box_span(xu, (P.deck_y[0], P.head_y[0]), (z0 + t, z0 + a))
        out.append(flat.fuse(up).removeSplitter())
    xr = (-P.deck_x + a, P.deck_x - a)
    rear = box_span(xr, (P.deck_y[0], P.deck_y[0] + a), (z0, z0 + t))
    rear = rear.fuse(box_span(xr, (P.deck_y[0], P.deck_y[0] + t), (z0 + t, z0 + a))).removeSplitter()
    out.append(rear)
    d, h = P.divider
    out.append(box_span((-d / 2.0 + 13.5, d / 2.0 - 13.5), (P.crate_y0, P.head_y[0]), (z0, z0 + h)))
    return Part.makeCompound(out)


def headboard():
    """Frame of square tube 25 x 2 and a welded mesh panel 50 x 50 x 3 (drawn as a 2 mm plate) in front of the crates."""
    y0, y1 = P.head_y
    z0, z1 = P.deck_z, P.deck_z + P.head_h
    w = 25.0
    frame = [tube_span((-P.deck_x, -P.deck_x + w), (y0, y1), (z0, z1), 2.0, "z"),
             tube_span((P.deck_x - w, P.deck_x), (y0, y1), (z0, z1), 2.0, "z"),
             tube_span((-P.deck_x + w, P.deck_x - w), (y0, y1), (z1 - w, z1), 2.0, "x"),
             tube_span((-P.deck_x + w, P.deck_x - w), (y0, y1), (z0 + 200.0, z0 + 200.0 + w), 2.0, "x")]
    mesh = box_span((-P.deck_x + w, P.deck_x - w), (y0 + 11.5, y0 + 13.5), (z0, z1 - w))
    mesh = mesh.cut(box_span((-P.deck_x + w, P.deck_x - w), (y0, y1), (z0 + 200.0, z0 + 200.0 + w)))
    return Part.makeCompound(frame), mesh


def gnss_mast():
    """Mast O30 on the top bar of the headboard with a plate for the relocated GNSS antenna."""
    y = (P.head_y[0] + P.head_y[1]) / 2.0
    z0 = P.deck_z + P.head_h
    m = cyl(P.gnss_mast_d, (0, y, z0), (0, y, P.gnss_mast_top))
    plate = cyl(120.0, (0, y, P.gnss_mast_top), (0, y, P.gnss_mast_top + 5.0))
    return m.fuse(plate)


def gnss_antenna():
    y = (P.head_y[0] + P.head_y[1]) / 2.0
    return Part.makeSphere(75.0, V(0, y, P.gnss_mast_top + 5.0)).common(
        box_span((-80, 80), (y - 80, y + 80), (P.gnss_mast_top + 5.0, P.gnss_mast_top + 90.0)))


def uwb_anchors():
    bx, by, bz = P.uwb_box
    z0 = P.deck_z + P.head_h
    return Part.makeCompound([box_span(sorted((sx * (P.deck_x - 5.0), sx * (P.deck_x - 5.0 - bx))),
                                       (P.head_y[0], P.head_y[0] + by), (z0, z0 + bz)) for sx in (-1, 1)])


def button_box():
    bx, by, bz = P.button_box
    x1 = P.deck_x - P.guide[0] - 10.0
    y0 = P.deck_y[0] + P.guide[1]
    box = box_span((x1 - bx, x1), (y0, y0 + by), (P.deck_z + P.guide[1], P.deck_z + P.guide[1] + bz))
    knobs = [cyl(22.0, (x1 - bx / 2.0 + dx, y0 - 0.0, P.deck_z + 60.0), (x1 - bx / 2.0 + dx, y0 - 12.0,
                                                                          P.deck_z + 60.0))
             for dx in (-45.0, 0.0, 45.0)]
    return box, Part.makeCompound(knobs)


# ---------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------
def crate(x0, y0, z0):
    cx, cy, cz = P.crate
    t = P.crate_wall
    outer = box_span((x0 + 2.0, x0 + cx - 2.0), (y0 + 2.0, y0 + cy - 2.0), (z0, z0 + cz))
    inner = box_span((x0 + 2.0 + t, x0 + cx - 2.0 - t), (y0 + 2.0 + t, y0 + cy - 2.0 - t), (z0 + t, z0 + cz + 1.0))
    s = outer.cut(inner)
    for sx in (-1, 1):                              # hand holes in the short ends
        xc = x0 + cx / 2.0 + sx * (cx / 2.0 - 2.0)
        s = s.cut(box_span((xc - 10, xc + 10), (y0 + cy / 2.0 - 60.0, y0 + cy / 2.0 + 60.0),
                           (z0 + cz - 60.0, z0 + cz - 30.0)))
    return s


def crates():
    return [crate(*p) for p in P.crate_positions()]


def straps():
    """Ratchet strap 25 x 2 over the top layer and down outside the deck to a hook under the side rail."""
    ztop = P.deck_z + P.crate_layers * P.crate[2]
    out = []
    for y in P.strap_y:
        w = P.strap[0] / 2.0
        s = P.strap[1]
        top = box_span((-P.deck_x - s, P.deck_x + s), (y - w, y + w), (ztop, ztop + s))
        legs = [box_span(sorted((sx * P.deck_x, sx * (P.deck_x + s))), (y - w, y + w),
                         (P.bearer_z[0] + 10.0, ztop + s)) for sx in (-1, 1)]
        out.append(top.fuse(legs).removeSplitter())
    return Part.makeCompound(out)
