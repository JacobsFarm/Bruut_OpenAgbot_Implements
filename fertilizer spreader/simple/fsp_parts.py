"""Parts of the fertilizer spreader. Every function returns a Part shape in robot coordinates.
The disc (with vanes and hub) is a separate group in build_fsp.py so the animation only turns its Placement.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import fsp_params as P


# ---------------------------------------------------------------------
# Helpers (same as the push blade)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def tube_span(x, y, z, t, axis):
    outer = box_span(x, y, z)
    spans = {"x": list(x), "y": list(y), "z": list(z)}
    for k in spans:
        if k == axis:
            spans[k] = [spans[k][0] - 1.0, spans[k][1] + 1.0]
        else:
            spans[k] = [spans[k][0] + t, spans[k][1] - t]
    return outer.cut(box_span(spans["x"], spans["y"], spans["z"]))


def rect_tube(p0, p1, w, h, t=0.0, up=(0.0, 0.0, 1.0)):
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


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def rect_wire(x, y, z):
    return Part.makePolygon([V(x[0], y[0], z), V(x[1], y[0], z), V(x[1], y[1], z), V(x[0], y[1], z), V(x[0], y[0], z)])


# ---------------------------------------------------------------------
# Mount: rails on the upper beams, spacers, bolts
# ---------------------------------------------------------------------
def rails():
    return rail_holes(Part.makeCompound([tube_span((sx * P.rail_x - P.rail / 2.0, sx * P.rail_x + P.rail / 2.0), P.rail_y, P.rail_z,
                                        P.rail_wall, "y") for sx in (-1, 1)]))


def spacers():
    out = []
    for sx in (-1, 1):
        for y in P.rail_bolt_y:
            b = box_span((sx * P.rail_x - 20.0, sx * P.rail_x + 20.0), (y - 20.0, y + 20.0),
                         (P.robot_upper_beam_z[1], P.rail_z[0]))
            out.append(b.cut(cyl(P.m10_hole, (sx * P.rail_x, y, 600), (sx * P.rail_x, y, 800))))
    return Part.makeCompound(out)


def rail_holes(shape):
    for sx in (-1, 1):
        for y in P.rail_bolt_y:
            shape = shape.cut(cyl(P.m10_hole, (sx * P.rail_x, y, 600), (sx * P.rail_x, y, 800)))
    return shape


def rail_bolts():
    """M10 from under the upper beam up through beam, spacer and rail, nut on top of the rail."""
    return Part.makeCompound([bolt_z(10.0, sx * P.rail_x, y, P.robot_upper_beam_z[0], P.rail_z[1])
                              for sx in (-1, 1) for y in P.rail_bolt_y])


def posts():
    out = []
    for sx in (-1, 1):
        for y in P.post_y:
            out.append(tube_span((sx * P.rail_x - P.post / 2.0, sx * P.rail_x + P.post / 2.0),
                                 (y - P.post / 2.0, y + P.post / 2.0), (P.rail_z[1], P.hop_z[0]), 3.0, "z"))
    return Part.makeCompound(out)


def ring():
    """Angle 40 x 40 x 4 frame round the straight part of the hopper: flange outwards on the posts, leg up against
    the wall (the hopper is bolted to the leg with M8)."""
    a, t = P.ring
    x0 = P.hop_x + P.hop_t
    y0, y1 = P.hop_y[0] - P.hop_t, P.hop_y[1] + P.hop_t
    z0 = P.hop_z[0]
    flange = box_span((-x0 - a, x0 + a), (y0 - a, y1 + a), (z0, z0 + t)).cut(
        box_span((-x0, x0), (y0, y1), (z0 - 1, z0 + t + 1)))
    leg = box_span((-x0 - t, x0 + t), (y0 - t, y1 + t), (z0, z0 + a)).cut(
        box_span((-x0, x0), (y0, y1), (z0 - 1, z0 + a + 1)))
    return flange.fuse(leg).removeSplitter()


# ---------------------------------------------------------------------
# Hopper
# ---------------------------------------------------------------------
def _hopper_solid(off):
    """Hopper volume grown by 'off' sideways (off = 0: inside, off = t: outside)."""
    x, y0, y1 = P.hop_x + off, P.hop_y[0] - off, P.hop_y[1] + off
    straight = box_span((-x, x), (y0, y1), (P.hop_z[0], P.hop_z[1] + (0.0 if off > 0 else 2.0)))
    top = rect_wire((-x, x), (y0, y1), P.hop_z[0] + 0.01)
    bot = rect_wire((-P.out_x - off, P.out_x + off), (P.out_y[0] - off, P.out_y[1] + off), P.out_z - (0 if off else 2))
    funnel = Part.makeLoft([bot, top], True, True)
    return straight.fuse(funnel)


def hopper():
    return _hopper_solid(P.hop_t).cut(_hopper_solid(0.0)).removeSplitter()


def lid():
    x, y0, y1 = P.hop_x + P.hop_t + 8.0, P.hop_y[0] - P.hop_t - 8.0, P.hop_y[1] + P.hop_t + 8.0
    top = box_span((-x, x), (y0, y1), (P.hop_z[1], P.hop_z[1] + P.lid_t))
    skirt = box_span((-x, x), (y0, y1), (P.hop_z[1] - 30.0, P.hop_z[1])).cut(
        box_span((-x + 3.0, x - 3.0), (y0 + 3.0, y1 - 3.0), (P.hop_z[1] - 31.0, P.hop_z[1] + 1.0)))
    return top.fuse(skirt).fuse(cyl(30.0, (0, y1 - 30.0, P.hop_z[1] + P.lid_t),
                                    (0, y1 - 30.0, P.hop_z[1] + P.lid_t + 25.0))).removeSplitter()


# ---------------------------------------------------------------------
# Metering
# ---------------------------------------------------------------------
def housing():
    """3 mm sheet box under the outlet, open at the top (outlet) and with the drop opening at the bottom; the roller
    shaft runs in the side walls."""
    hx = P.housing_x
    outer = box_span((-hx, hx), P.housing_y, P.housing_z)
    inner = box_span((-hx + 3.0, hx - 3.0), (P.housing_y[0] + 3.0, P.housing_y[1] - 3.0),
                     (P.housing_z[0] + 3.0, P.housing_z[1] + 1.0))
    s = outer.cut(inner)
    yr, zr = P.roller_axis
    s = s.cut(box_span((-30.0, 30.0), (yr - 20.0, yr + 20.0), (P.housing_z[0] - 1, P.housing_z[0] + 4)))
    flange = box_span((-hx - 15.0, hx + 15.0), (P.housing_y[0] - 15.0, P.housing_y[1] + 15.0),
                      (P.housing_z[1] - 3.0, P.housing_z[1])).cut(
        box_span((-P.out_x - P.hop_t, P.out_x + P.hop_t), (P.out_y[0] - P.hop_t, P.out_y[1] + P.hop_t), (0, 2000)))
    s = s.fuse(flange)
    return s.cut(cyl(13.0, (-200, yr, zr), (200, yr, zr))).removeSplitter()


def roller():
    yr, zr = P.roller_axis
    L = P.roller_len
    r = cyl(P.roller_d, (-L / 2.0, yr, zr), (L / 2.0, yr, zr))
    for i in range(P.flutes):
        a = 2 * math.pi * i / P.flutes
        cy, cz = yr + (P.roller_d / 2.0) * math.cos(a), zr + (P.roller_d / 2.0) * math.sin(a)
        f = cyl(P.flute_w, (-L / 2.0 + 8.0, cy, cz), (L / 2.0 - 8.0, cy, cz))
        r = r.cut(f)
    return r.fuse(cyl(12.0, (-P.housing_x - 8.0, yr, zr), (P.housing_x + 6.0, yr, zr))).removeSplitter()


def meter_motor():
    yr, zr = P.roller_axis
    d, L = P.meter_motor
    x0 = P.housing_x + 6.0
    return Part.makeCompound([box_span((x0, x0 + 30.0), (yr - 27.0, yr + 27.0), (zr - 27.0, zr + 27.0)),
                              cyl(d, (x0 + 30.0, yr, zr), (x0 + 30.0 + L, yr, zr))])


def chute():
    yr, _ = P.roller_axis
    return rect_tube((0, yr, P.housing_z[0] - 12.0), (0, P.chute_drop[0], P.chute_drop[1]), 44.0, 64.0, 2.0,
                     up=(1.0, 0.0, 0.0))


# ---------------------------------------------------------------------
# Spinner
# ---------------------------------------------------------------------
def spinner_frame():
    """Weldment: 2 legs from the rail ends down, cross tube, arm forward under the disc, motor plate."""
    zf = P.frame_z
    parts = [tube_span((-P.rail_x - 20.0, P.rail_x + 20.0), P.leg_y, zf, 3.0, "x"),
             tube_span((-20.0, 20.0), (P.leg_y[1], P.disc_y), zf, 3.0, "y"),
             box_span((-P.motor_plate[0] / 2.0, P.motor_plate[0] / 2.0),
                      (P.disc_y - P.motor_plate[0] / 2.0, P.disc_y + P.motor_plate[0] / 2.0),
                      (zf[1], zf[1] + P.motor_plate[1]))]
    for sx in (-1, 1):
        parts.append(tube_span((sx * P.rail_x - 20.0, sx * P.rail_x + 20.0), P.leg_y, (zf[1], P.rail_z[0]), 3.0, "z"))
    return fuse_all(parts)


def spin_motor():
    z0 = P.frame_z[1] + P.motor_plate[1]
    return Part.makeCompound([cyl(P.spin_motor_d, (0, P.disc_y, z0), (0, P.disc_y, P.spin_motor_z[1])),
                              cyl(20.0, (0, P.disc_y, P.spin_motor_z[1]), (0, P.disc_y, P.disc_z)),
                              box_span((P.spin_motor_d / 2.0 - 5.0, P.spin_motor_d / 2.0 + 25.0),
                                       (P.disc_y - 20.0, P.disc_y + 20.0), (z0 + 20.0, z0 + 60.0))])


def disc():
    d = cyl(P.disc_d, (0, P.disc_y, P.disc_z), (0, P.disc_y, P.disc_z + P.disc_t))
    hub = cyl(50.0, (0, P.disc_y, P.spin_motor_z[1] + 2.0), (0, P.disc_y, P.disc_z))
    bore = cyl(20.5, (0, P.disc_y, P.spin_motor_z[1]), (0, P.disc_y, P.disc_z))
    return d.fuse(hub).removeSplitter().cut(bore)


def vanes():
    """Vanes curved backwards (against the turning direction), as on fertilizer spreaders."""
    out = []
    for i in range(P.n_vanes):
        a0 = 2 * math.pi * i / P.n_vanes
        pts = []
        n = 8
        for k in range(n + 1):
            r = P.vane_r[0] + (P.vane_r[1] - P.vane_r[0]) * k / n
            a = a0 - 0.5 * (r - P.vane_r[0]) / (P.vane_r[1] - P.vane_r[0])
            pts.append(V(r * math.cos(a), P.disc_y + r * math.sin(a), P.disc_z + P.disc_t))
        for k in range(n):
            out.append(rect_tube(pts[k], pts[k + 1], P.vane_t, P.vane_h * 2.0).common(
                box_span((-500, 500), (-2000, 0), (P.disc_z + P.disc_t, P.disc_z + P.disc_t + P.vane_h))))
    return fuse_all(out)


def guard():
    r0, r1 = P.guard_r, P.guard_r + 2.0
    h = P.guard_z[1] - P.guard_z[0]
    span = P.guard_ang[1] - P.guard_ang[0]
    c = V(0, P.disc_y, P.guard_z[0])
    s = Part.makeCylinder(r1, h, c, V(0, 0, 1), span).cut(Part.makeCylinder(r0, h + 2, c - V(0, 0, 1), V(0, 0, 1), span))
    s.rotate(c, V(0, 0, 1), P.guard_ang[0])
    return s


def guard_straps():
    """2 flat bars 30 x 5 from the top of the guard to tabs under the rear outer lower beam (M10 at x = +-125)."""
    out = []
    zb = P.robot_lower_beam_z[0]
    yb = P.robot_rear_beam_y[0]
    for sx in (-1, 1):
        x = sx * 125.0
        yg = P.disc_y + math.sqrt((P.guard_r + 3.0) ** 2 - x ** 2)
        tab = box_span((x - 20.0, x + 20.0), (yb - 20.0, yb + 20.0), (zb - 6.0, zb))
        tab = tab.cut(cyl(P.m10_hole, (x, yb, zb - 10), (x, yb, zb + 10)))
        bar = rect_tube((x, yg + 12.0, P.guard_z[1] - 40.0), (x, yb - 18.0, zb - 3.0), 30.0, 5.0, up=(0.0, 1.0, 0.3))
        out.append(tab.fuse(bar).removeSplitter())
    return Part.makeCompound(out)


def strap_bolts():
    zb = P.robot_lower_beam_z
    yb = P.robot_rear_beam_y[0]
    return Part.makeCompound([bolt_z(10.0, sx * 125.0, yb, zb[0] - 6.0, zb[1]) for sx in (-1, 1)])


# ---------------------------------------------------------------------
# Counterweight (optional) on the front lower beams
# ---------------------------------------------------------------------
def ballast():
    out = []
    for sx in (-1, 1):
        x = sorted((sx * P.ballast_x[0], sx * P.ballast_x[1]))
        b = box_span(x, P.ballast_y, (P.ballast_z0, P.ballast_z0 + P.ballast_h))
        out.append(b.cut(cyl(P.m10_hole, (sx * 175.0, 575.0, 600), (sx * 175.0, 575.0, 900))))
    return Part.makeCompound(out)


def ballast_bolts():
    return Part.makeCompound([bolt_z(10.0, sx * 175.0, 575.0, P.robot_lower_beam_z[0], P.ballast_z0 + P.ballast_h)
                              for sx in (-1, 1)])
