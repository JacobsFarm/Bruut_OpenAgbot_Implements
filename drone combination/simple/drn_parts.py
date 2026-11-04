"""Parts of the drone landing platform, in robot coordinates; drone() is a simple stand-in for the renders."""
import Part
from FreeCAD import Vector as V

import drn_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all

BAR_Z = (P.upper_beam_top, P.upper_beam_top + P.bar_wh[1])
PX, PY, PT = P.plate
X0, X1 = -PX / 2.0, PX / 2.0
Y0, Y1 = P.plate_y0, P.plate_y0 + PY
FZ = (P.plate_z - P.frame_wh[1], P.plate_z)
TOP = P.plate_z + PT


def _bar_bolt_x():
    return [sx * sum(b) / 2.0 for sx in (-1, 1) for b in P.upper_beam_x]


def cross_bars():
    w, h = P.bar_wh
    s = Part.makeCompound([tube_span((-P.bar_x, P.bar_x), (sy * P.hole_y - w / 2.0, sy * P.hole_y + w / 2.0), BAR_Z,
                                     3.0, "x") for sy in (-1, 1)])
    for x in _bar_bolt_x():
        for sy in (-1, 1):
            s = s.cut(cyl(10.5, (x, sy * P.hole_y, BAR_Z[0] - 1), (x, sy * P.hole_y, BAR_Z[1] + 1)))
    return s


def bar_bolts():
    return Part.makeCompound([PP.bolt_z(10.0, x, sy * P.hole_y, P.upper_beam_top - 40.0, BAR_Z[1])
                              for x in _bar_bolt_x() for sy in (-1, 1)])


def posts():
    w = P.post_w / 2.0
    return Part.makeCompound([tube_span((sx * P.post_x - w, sx * P.post_x + w), (sy * P.hole_y - w, sy * P.hole_y + w),
                                        (BAR_Z[1], FZ[0]), 3.0, "z") for sx in (-1, 1) for sy in (-1, 1)])


def frame():
    """Perimeter frame 30 x 30 x 2 under the plate and 2 cross members over the posts."""
    w, h = P.frame_wh
    parts = [tube_span((X0, X1), (Y0, Y0 + w), FZ, 2.0, "x"), tube_span((X0, X1), (Y1 - w, Y1), FZ, 2.0, "x"),
             tube_span((X0, X0 + w), (Y0 + w, Y1 - w), FZ, 2.0, "y"), tube_span((X1 - w, X1), (Y0 + w, Y1 - w), FZ, 2.0, "y")]
    for sy in (-1, 1):
        y = sy * P.hole_y
        parts.append(tube_span((X0 + w, X1 - w), (y - w / 2.0, y + w / 2.0), FZ, 2.0, "x"))
    return fuse_all(parts)


def deck():
    return box_span((X0, X1), (Y0, Y1), (P.plate_z, TOP))


def wedges():
    """PE wedges along the 4 edges: from the plate at the landing zone up to wedge_h at the edge (corners left open)."""
    out = []
    w, h = P.wedge_w, P.wedge_h
    c = (X0 + X1) / 2.0, (Y0 + Y1) / 2.0
    for ax in ("x", "y"):
        for s in (-1, 1):
            if ax == "x":
                e = c[0] + s * PX / 2.0
                pts = [V(e, Y0 + w, TOP), V(e - s * w, Y0 + w, TOP), V(e, Y0 + w, TOP + h)]
                f = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, PY - 2 * w, 0))
            else:
                e = c[1] + s * PY / 2.0
                pts = [V(X0 + w, e, TOP), V(X0 + w, e - s * w, TOP), V(X0 + w, e, TOP + h)]
                f = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(PX - 2 * w, 0, 0))
            out.append(f)
    return Part.makeCompound(out)


def strips():
    sx, sy, sz = P.strip
    yc = (Y0 + Y1) / 2.0
    return Part.makeCompound([box_span((x - sx / 2.0, x + sx / 2.0), (yc - sy / 2.0, yc + sy / 2.0), (TOP, TOP + sz))
                              for x in (-P.strip_x, P.strip_x)])


def tag():
    tx, ty, tz = P.tag
    yc = (Y0 + Y1) / 2.0
    return box_span((-tx / 2.0, tx / 2.0), (yc - ty / 2.0, yc + ty / 2.0), (TOP, TOP + tz))


def gnss():
    x, y = P.gnss_post
    post = cyl(25.0, (x, y, TOP), (x, y, TOP + P.gnss_post_h))
    d, h = P.gnss_dome
    r = d / 2.0
    dome = Part.makeSphere(r, V(x, y, TOP + P.gnss_post_h)).common(
        box_span((x - r, x + r), (y - r, y + r), (TOP + P.gnss_post_h, TOP + P.gnss_post_h + h)))
    return fuse_all([post, dome])


def drone():
    """Stand-in: body 300 x 200 x 90 on 2 skids over the strips, 4 arms and propeller discs (render only)."""
    yc = (Y0 + Y1) / 2.0
    z0 = TOP + P.strip[2]
    skids = [box_span((x - 8.0, x + 8.0), (yc - 150.0, yc + 150.0), (z0, z0 + 12.0)) for x in (-P.strip_x, P.strip_x)]
    legs = [cyl(10.0, (x, yc + dy, z0 + 12.0), (x * 0.6, yc + dy, z0 + 90.0)) for x in (-P.strip_x, P.strip_x)
            for dy in (-100.0, 100.0)]
    body = box_span((-100.0, 100.0), (yc - 150.0, yc + 150.0), (z0 + 90.0, z0 + 180.0))
    arms, props = [], []
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = V(sx * 190.0, yc + sy * 170.0, z0 + 170.0)
            arms.append(cyl(20.0, (sx * 60.0, yc + sy * 60.0, z0 + 160.0), (p.x, p.y, p.z)))
            props.append(cyl(240.0, (p.x, p.y, p.z + 15.0), (p.x, p.y, p.z + 18.0)))
    return fuse_all(skids + legs + [body] + arms), Part.makeCompound(props)
