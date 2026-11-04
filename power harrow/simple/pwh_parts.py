"""Parts of the rotary tiller, in robot coordinates in the work pose (lift 0). The hitch (mount, links, toolbar frame,
gauge wheels) comes from tph_parts."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import pwh_params as P
from tph_parts import box_span, cyl, fuse_all, plate_yz

YR, ZR = P.rotor_y, P.rotor_z


def _cx(d, x0, x1, y=YR, z=ZR):
    x0, x1 = sorted((x0, x1))
    return cyl(d, (x0, y, z), (x1, y, z))


def _arc_pts(r, a0, a1, n=24, y=YR, z=ZR):
    return [(y + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), z + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


# ---------------------------------------------------------------------
# Rotor
# ---------------------------------------------------------------------
def rotor_tube():
    x = P.side_x[0] - 5.0
    t = _cx(P.tube[0], -x, x).cut(_cx(P.tube[0] - 2 * P.tube[1], -x - 1, x + 1))
    shaft = _cx(P.shaft_d, -P.side_x[1] - 30.0, P.case_x[0] + 20.0)
    return fuse_all([t, shaft])


def flanges():
    return Part.makeCompound([_cx(P.flange[0], x - P.flange[1] / 2.0, x + P.flange[1] / 2.0) for x in P.flange_x])


def blades():
    """L-blades: a radial shank bolted to the flange and a tip bent sideways (alternating), 4 per flange at 90 deg,
    flanges offset 22.5 deg so the blades enter the soil one after another."""
    out = []
    w, t = P.blade
    r1 = P.rotor_d / 2.0
    for i, xf in enumerate(P.flange_x):
        for k in range(P.blades_per_flange):
            side = 1.0 if k % 2 == 0 else -1.0
            xs = xf + side * (P.flange[1] / 2.0 + t / 2.0)
            shank = box_span((xs - t / 2.0, xs + t / 2.0), (-w / 2.0, w / 2.0), (P.blade_r0, r1 - 8.0))
            tip = box_span(sorted((xs - side * t / 2.0, xs + side * P.blade_bend)), (-w / 2.0, w / 2.0), (r1 - 8.0, r1))
            b = shank.fuse(tip)
            a = 360.0 / P.blades_per_flange * k + 22.5 * i
            b.rotate(V(0, 0, 0), V(1, 0, 0), a)
            b.translate(V(0, YR, ZR))
            out.append(b)
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Housing
# ---------------------------------------------------------------------
def side_plates():
    """5 mm plates: a disc r 228 around the rotor axis, cut flat 25 mm above the ground (skid), with the hood edge."""
    out = []
    for s in (-1, 1):
        x0, x1 = sorted((s * P.side_x[0], s * P.side_x[1]))
        d = _cx(2 * P.side_r, x0, x1)
        d = d.common(box_span((x0, x1), (YR - 300, YR + 300), (25.0, 600.0)))
        out.append(d.cut(_cx(P.shaft_d + 2.0, x0 - 1, x1 + 1)))
    return Part.makeCompound(out)


def bearings():
    """Left bearing housing on the outside of the left side plate (the right one is in the chain case)."""
    x0 = -P.side_x[1]
    return _cx(P.bearing_d, x0 - 30.0, x0)


def hood():
    ro, ri = P.hood_r[1], P.hood_r[0]
    pts = _arc_pts(ro, P.hood_a[0], P.hood_a[1]) + list(reversed(_arc_pts(ri, P.hood_a[0], P.hood_a[1])))
    return plate_yz(pts, -P.hood_x, 2 * P.hood_x)


def skirt():
    y = YR + P.hood_r[0]
    return box_span((-P.hood_x, P.hood_x), (y - P.skirt[0], y), (P.skirt[1], ZR))


def flap_hinge():
    y = YR - P.hood_r[1] - P.flap_hinge_d / 2.0
    return cyl(P.flap_hinge_d, (-P.hood_x, y, ZR), (P.hood_x, y, ZR))


def flap():
    w, ln, t = P.flap
    y0 = YR - P.hood_r[1] - P.flap_hinge_d
    a = math.radians(P.flap_angle)
    p0 = (y0, ZR)
    p1 = (y0 - ln * math.sin(a), ZR - ln * math.cos(a))
    n = (math.cos(a) * t, -math.sin(a) * t)
    pts = [p0, p1, (p1[0] - n[0], p1[1] - n[1]), (p0[0] - n[0], p0[1] - n[1])]
    return plate_yz(pts, -w / 2.0, w)


def brackets():
    """2 plates 10 mm from the toolbar top/rear face back over the hood top."""
    out = []
    surf = [(y, z) for (y, z) in _arc_pts(P.hood_r[1], 40.0, 105.0, 16)]
    surf = sorted(surf, key=lambda p: p[0])
    for x in P.bracket_x:
        pts = [(P.tb_y[1], P.tb_z[1]), (P.tb_y[1], P.tb_z[1] + 50.0), (P.tb_y[0] - 60.0, P.bracket_top),
               (surf[0][0], P.bracket_top)] + surf + [(P.tb_y[0], P.tb_z[1])]
        out.append(plate_yz(pts, x - P.bracket_t / 2.0, P.bracket_t))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Drive
# ---------------------------------------------------------------------
def chain_case():
    x0, x1 = P.case_x
    r = P.sprocket_d / 2.0 + 15.0
    body = box_span((x0, x1), (YR - r, YR + r), (ZR, P.motor_z)).fuse(_cx(2 * r, x0, x1)).fuse(_cx(2 * r, x0, x1, z=P.motor_z))
    return body


def motor():
    gy, gz = P.gear
    box = box_span(P.gear_x, (YR - gy / 2.0, YR + gy / 2.0), (P.motor_z - gz / 2.0, P.motor_z + gz / 2.0))
    body = _cx(P.motor_d, P.motor_x[0], P.motor_x[1], z=P.motor_z)
    fins = [_cx(P.motor_d + 8.0, x, x + 6.0, z=P.motor_z) for x in (170.0, 210.0, 250.0)]
    cap = _cx(60.0, P.motor_x[0] - 25.0, P.motor_x[0], z=P.motor_z)
    return fuse_all([box, body, cap] + fins)


def motor_bracket():
    """Stand under the gearmotor on the hood top: 2 webs and a top plate, 6 mm."""
    gy, gz = P.gear
    z1 = P.motor_z - gz / 2.0
    z0 = ZR + P.hood_r[1]
    x = (P.gear_x[0] - 60.0, P.side_x[0] - 2.0)
    return Part.makeCompound([box_span(x, (YR + dy - 3.0, YR + dy + 3.0), (z0, z1)) for dy in (-37.0, 37.0)] +
                             [box_span(x, (YR - 40.0, YR + 40.0), (z1 - 6.0, z1))])


# ---------------------------------------------------------------------
# Render only: soil with a tilled strip
# ---------------------------------------------------------------------
def soil(y0, y1, x=(-1400.0, 1400.0)):
    return box_span(x, (y0, y1), (-120.0, 0.0))


def tilled_strip(y0, y1):
    """Loose, slightly raised soil behind the rotor."""
    out = []
    w = P.work_w / 2.0
    out.append(box_span((-w, w), (y0, y1), (0.0, 15.0)))
    for i, yy in enumerate(range(int(y0), int(y1), 90)):
        for xx in range(int(-w) + 40, int(w) - 40, 110):
            dx = 25.0 * ((i * 7 + xx) % 3 - 1)
            out.append(Part.makeSphere(22.0, V(xx + dx, yy + 30.0, 15.0)))
    return Part.makeCompound(out)
