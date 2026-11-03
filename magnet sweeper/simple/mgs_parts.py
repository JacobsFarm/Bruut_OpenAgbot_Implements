"""Parts of the magnet head. Every function returns a Part shape in robot coordinates, in the work pose (arms down,
core down on the skin). The toolbar, lift arms, carrier, king pin and lift actuator come from "push blade/simple"
(pbl_parts), the castor wheels from "broom sweeper/simple" (bsw_parts). build_mgs.py puts the head in the same sub-Part
as the blade (on the king pin) and the magnet core in its own sub-Part (moves up by core_lift to release).
"""
import Part

import mgs_params as P
import pbl_parts as PP
import bsw_parts as SP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all
plate_yz = PP.plate_yz

SKIN_TOP = P.box_z[0] + P.skin_t
LID_Z = (P.box_z[1] - P.lid_t, P.box_z[1])
MAG_Z = (SKIN_TOP + P.core_gap, SKIN_TOP + P.core_gap + P.mag_size[2])
CORE_Z = (MAG_Z[1], MAG_Z[1] + P.core_t)
PIN_Z = CORE_Z[1] + 21.0            # clevis pin of the release actuator
FLANGE_Y = (P.box_y[0] - P.bracket_flange[1], P.box_y[0])


def _box_bolts():
    return [(sx * P.bracket_x + dx, z) for sx in (-1, 1) for dx in (-P.box_bolt_dx, P.box_bolt_dx)
            for z in P.box_bolt_z]


def _guides():
    return [(sx * P.guide_x, y) for sx in (-1, 1) for y in P.guide_y]


# ---------------------------------------------------------------------
# Head frame (weldment): swivel plate, spine, cross beam, 2 brackets with flanges
# ---------------------------------------------------------------------
def head_frame():
    sz = P.swivel_z
    parts = [cyl(P.head_d, (0, P.king_y, sz[0]), (0, P.king_y, sz[1])),
             box_span((-P.spine_x, P.spine_x), (P.king_y, P.beam_y[1]), sz),
             tube_span((-P.beam_x, P.beam_x), P.beam_y, P.beam_z, P.beam_wall, "x")]
    fw, ft = P.bracket_flange
    for sx in (-1, 1):
        x = sx * P.bracket_x
        side = ((P.beam_y[1], P.beam_z[1]), (FLANGE_Y[0], P.bracket_z[1]), (FLANGE_Y[0], P.bracket_z[0]),
                (P.beam_y[1], P.beam_z[0]))
        parts.append(plate_yz(side, x - P.bracket_t / 2.0, P.bracket_t))
        parts.append(box_span((x - fw / 2.0, x + fw / 2.0), FLANGE_Y, P.bracket_z))
    s = fuse_all(parts)
    s = s.cut(cyl(P.king_d + 1.0, (0, P.king_y, 0), (0, P.king_y, 500)))
    import math
    for a in P.angle_steps:
        ang = math.radians(-90.0 - a)
        x, y = P.lock_r * math.cos(ang), P.king_y + P.lock_r * math.sin(ang)
        s = s.cut(cyl(P.lock_d + 1.0, (x, y, 0), (x, y, 500)))
    for x, z in _box_bolts():
        s = s.cut(cyl(11.0, (x, FLANGE_Y[0] - 5.0, z), (x, P.box_y[0] + 30.0, z)))
    for x, y in SP._castor_bolts():
        s = s.cut(cyl(9.0, (x, y, 100), (x, y, 200)))
    return s


def box_bolts():
    out = []
    for x, z in _box_bolts():
        out.append(PP.bolt_axis(10.0, (x, FLANGE_Y[0], z), (x, P.box_y[0] + P.wall_t, z), 17.0, 6.4, 8.4))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Magnet box: walls and lid (aluminium), skin (stainless), skids (PE), guide rods (stainless)
# ---------------------------------------------------------------------
def box_walls():
    x, y = P.box_x, P.box_y
    t = P.wall_t
    outer = box_span((-x, x), y, (SKIN_TOP, LID_Z[0]))
    inner = box_span((-x + t, x - t), (y[0] + t, y[1] - t), (SKIN_TOP - 1.0, LID_Z[0] + 1.0))
    s = outer.cut(inner)
    for bx, z in _box_bolts():
        s = s.cut(cyl(11.0, (bx, y[0] - 5.0, z), (bx, y[0] + 20.0, z)))
    return s


def lid():
    s = box_span((-P.box_x, P.box_x), P.box_y, LID_Z)
    s = s.cut(cyl(P.rel_rod_d + 4.0, (0, P.mag_y, LID_Z[0] - 1), (0, P.mag_y, LID_Z[1] + 1)))
    for x, y in _guides():
        s = s.cut(cyl(8.5, (x, y, LID_Z[0] - 1), (x, y, LID_Z[1] + 1)))
    return s


def skin():
    s = box_span((-P.box_x, P.box_x), P.box_y, (P.box_z[0], SKIN_TOP))
    for x, y in _guides():
        s = s.cut(cyl(8.5, (x, y, P.box_z[0] - 1), (x, y, SKIN_TOP + 1)))
    return s


def skids():
    out = []
    w = P.skid_w
    for sx in (-1, 1):
        x1 = sx * P.box_x
        x0 = x1 - sx * w
        for y0, y1 in ((P.box_y[0], P.box_y[0] + 3 * w), (P.box_y[1] - 3 * w, P.box_y[1])):
            out.append(box_span((min(x0, x1), max(x0, x1)), (y0, y1), (P.box_z[0] - P.skid_h, P.box_z[0])))
    return Part.makeCompound(out)


def guide_rods():
    """4 stainless rods O16 from the skin top to the lid, M8 screws through skin and lid (shown as the rod)."""
    return Part.makeCompound([cyl(P.guide_d, (x, y, SKIN_TOP), (x, y, LID_Z[0])) for x, y in _guides()])


# ---------------------------------------------------------------------
# Magnet core (own sub-Part): back plate, ferrite blocks, PE bushes, clevis
# ---------------------------------------------------------------------
def back_plate():
    s = box_span((-P.core_x, P.core_x), P.core_y, CORE_Z)
    for x, y in _guides():
        s = s.cut(cyl(P.guide_d + 1.0, (x, y, CORE_Z[0] - 1), (x, y, CORE_Z[1] + 1)))
    return s


def magnets():
    """mag_rows x mag_n NdFeB blocks with 0.5 mm glue joints; rows centred about mag_y."""
    mx, my, _ = P.mag_size
    x0 = -P.mag_n * mx / 2.0
    out = []
    for r in range(P.mag_rows):
        yc = P.mag_y + (r - (P.mag_rows - 1) / 2.0) * my
        out += [box_span((x0 + i * mx + 0.5, x0 + (i + 1) * mx - 0.5), (yc - my / 2.0 + 0.5, yc + my / 2.0 - 0.5),
                         MAG_Z) for i in range(P.mag_n)]
    return Part.makeCompound(out)


def bushes():
    out = []
    for x, y in _guides():
        b = cyl(P.bush_d, (x, y, CORE_Z[1]), (x, y, CORE_Z[1] + P.bush_h))
        out.append(b.cut(cyl(P.guide_d + 0.5, (x, y, CORE_Z[1] - 1), (x, y, CORE_Z[1] + P.bush_h + 1))))
    return Part.makeCompound(out)


def clevis():
    out = []
    for sx in (-1, 1):
        x0 = sx * 13.0 if sx > 0 else -19.0
        pl = box_span((x0, x0 + 6.0), (P.mag_y - 20.0, P.mag_y + 20.0), (CORE_Z[1], PIN_Z + 14.0))
        out.append(pl.cut(cyl(10.5, (x0 - 1, P.mag_y, PIN_Z), (x0 + 7, P.mag_y, PIN_Z))))
    return Part.makeCompound(out)


def clevis_pin():
    return cyl(10.0, (-24.0, P.mag_y, PIN_Z), (24.0, P.mag_y, PIN_Z))


def release_rod():
    """Rod with an eye on the clevis pin; it slides in the actuator body (moves with the core)."""
    eye = cyl(26.0, (-12.0, P.mag_y, PIN_Z), (12.0, P.mag_y, PIN_Z)).cut(
        cyl(10.5, (-13.0, P.mag_y, PIN_Z), (13.0, P.mag_y, PIN_Z)))
    rod = cyl(P.rel_rod_d, (0, P.mag_y, PIN_Z + 12.0), (0, P.mag_y, LID_Z[1] + 70.0))
    return fuse_all([eye, rod])


# ---------------------------------------------------------------------
# Release actuator body on the lid
# ---------------------------------------------------------------------
def release_body():
    z0 = LID_Z[1]
    base = cyl(80.0, (0, P.mag_y, z0), (0, P.mag_y, z0 + 8.0))
    body = cyl(P.rel_body_d, (0, P.mag_y, z0 + 8.0), (0, P.mag_y, z0 + P.rel_body_l))
    mx, my, mz = P.rel_motor
    motor = box_span((P.rel_body_d / 2.0 - 5.0, P.rel_body_d / 2.0 - 5.0 + mx), (P.mag_y - my / 2.0, P.mag_y + my / 2.0),
                     (z0 + P.rel_body_l - mz, z0 + P.rel_body_l))
    s = fuse_all([base, body, motor])
    return s.cut(cyl(P.rel_rod_d + 1.0, (0, P.mag_y, z0 - 1), (0, P.mag_y, z0 + P.rel_body_l - 30.0)))


# ---------------------------------------------------------------------
# Collecting tray (ground, release pose only)
# ---------------------------------------------------------------------
def tray(y_centre):
    sx, sy, sz = P.tray_size
    t = P.tray_t
    outer = box_span((-sx / 2.0, sx / 2.0), (y_centre - sy / 2.0, y_centre + sy / 2.0), (0.0, sz))
    inner = box_span((-sx / 2.0 + t, sx / 2.0 - t), (y_centre - sy / 2.0 + t, y_centre + sy / 2.0 - t), (t, sz + 1))
    return outer.cut(inner)


# castor wheels of the broom (same beam, same place)
castor_spacers = SP.castor_spacers
castors = SP.castors
castor_wheels = SP.castor_wheels
castor_bolts = SP.castor_bolts
