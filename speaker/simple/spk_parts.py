"""Parts of the speech speaker, in robot coordinates. horn(origin, direction) is generic, so other implements (the
security patrol) can mount the same horn elsewhere.
"""
import Part
from FreeCAD import Vector as V

import spk_params as P
import pbl_parts as PP

box_span = PP.box_span
cyl = PP.cyl
fuse_all = PP.fuse_all


def horn(origin=(0.0, 0.0, 0.0), sy=1):
    """Horn along +y (sy = 1) or -y (sy = -1): mouth at origin + sy * depth, driver behind the throat at origin."""
    mx, mz = P.horn_mouth
    tx, tz = P.horn_throat
    ox, oy, oz = origin
    y1 = oy + sy * P.horn_depth
    throat = Part.makePolygon([V(ox - tx / 2, oy, oz - tz / 2), V(ox + tx / 2, oy, oz - tz / 2),
                               V(ox + tx / 2, oy, oz + tz / 2), V(ox - tx / 2, oy, oz + tz / 2),
                               V(ox - tx / 2, oy, oz - tz / 2)])
    mouth = Part.makePolygon([V(ox - mx / 2, y1, oz - mz / 2), V(ox + mx / 2, y1, oz - mz / 2),
                              V(ox + mx / 2, y1, oz + mz / 2), V(ox - mx / 2, y1, oz + mz / 2),
                              V(ox - mx / 2, y1, oz - mz / 2)])
    body = Part.makeLoft([throat, mouth], True)
    dl, dd = P.driver[1], P.driver[0]
    drv = cyl(dd, (ox, oy - sy * dl, oz), (ox, oy, oz))
    return fuse_all([body, drv])


def _bolts_xy(sy):
    return [(x, sy * P.hole_y) for x in P.bolt_x]


def brackets():
    out = []
    z0 = P.upper_beam_top
    for sy in (-1, 1):
        y = sy * P.hole_y
        base = box_span(P.plate_x, (y - P.plate_w / 2.0, y + P.plate_w / 2.0), (z0, z0 + P.plate_t))
        # upright plate behind the driver (towards the robot centre)
        yu = y - sy * (P.plate_w / 2.0)
        up = box_span(P.upright_x, sorted((yu, yu + sy * P.plate_t)), (z0 + P.plate_t, z0 + P.plate_t + P.upright_h))
        b = base.fuse(up)
        for x, yy in _bolts_xy(sy):
            b = b.cut(cyl(10.5, (x, yy, z0 - 1), (x, yy, z0 + P.plate_t + 1)))
        out.append(b)
    return Part.makeCompound(out)


def bracket_bolts():
    z0 = P.upper_beam_top
    return Part.makeCompound([PP.bolt_z(10.0, x, y, z0 - 40.0, z0 + P.plate_t) for sy in (-1, 1)
                              for x, y in _bolts_xy(sy)])


def horns():
    """Driver back face against the upright plate, horn pointing out (front +y, rear -y)."""
    out = []
    for sy in (-1, 1):
        yu = sy * (P.hole_y - P.plate_w / 2.0 + P.plate_t)
        throat_y = yu + sy * P.driver[1]
        out.append(horn((P.horn_x, throat_y, P.horn_z), sy))
    return Part.makeCompound(out)


def amp():
    w, d, h = P.amp_box
    z0 = P.upper_beam_top + P.plate_t
    y0 = -P.hole_y - P.plate_w / 2.0
    return box_span((150.0, 150.0 + w), (y0, y0 + d), (z0, z0 + h))


def mic():
    w, d, h = P.amp_box
    z0 = P.upper_beam_top + P.plate_t + h
    y = -P.hole_y - P.plate_w / 2.0 + d / 2.0
    return cyl(P.mic_d, (230.0, y, z0), (230.0, y, z0 + 40.0))
