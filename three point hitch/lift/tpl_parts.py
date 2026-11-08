"""Parts of the lift mast and the demo machine. Robot coordinates; the carriage parts are drawn at the bottom of the
travel (dz = 0), the machine standing on its legs with the robot at y 0. build_tpl.py translates the carriage and the
machine. The male triangle, latch, female triangle and LA36 come from ../a_frame (tpa_parts), the toolbar and
hangers from ../simple (tph_parts).
"""
import Part
from FreeCAD import Vector as V

import tpl_params as P
import tpa_params as Q
import tpa_parts as GA
from tph_parts import box_span, cyl, tube_span, rect_tube, fuse_all, plate_yz  # noqa: F401
from tpa_parts import compound, pin_x


# ---------------------------------------------------------------------
# Mast (fixed)
# ---------------------------------------------------------------------
def _cross(z0):
    h, d = P.cross
    y0 = P.col_y - d / 2.0
    s = tube_span((-P.cross_x, P.cross_x), (y0, y0 + d), (z0, z0 + h), 3.0, "x")
    for sx in (-1, 1):
        s = s.cut(cyl(P.col_d + 0.5, (sx * P.col_x, P.col_y, z0 - 1.0), (sx * P.col_x, P.col_y, z0 + h + 1.0)))
    return s


def mast_frame():
    """Bottom and top cross tubes, 2 side uprights, 2 brackets to the rear face of the toolbar (one weldment)."""
    zb, zt = P.bottom_cross_z, P.top_cross_z
    h, d = P.cross
    parts = [_cross(zb), _cross(zt)]
    u = P.upright / 2.0
    y0 = P.col_y - d / 2.0
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (P.upright_x - u), sx * (P.upright_x + u)))
        parts.append(tube_span((x0, x1), (y0, y0 + P.upright), (zb + h, zt), 3.0, "z"))
        parts.append(box_span((x0, x1), (y0 + P.upright, P.tb_y[0]), P.bracket_z))
    return fuse_all(parts)


def columns():
    """2 round columns O50 x 4 (precision tube), through both cross tubes, with end caps."""
    out = []
    z0, z1 = P.bottom_cross_z, P.top_cross_z + P.cross[0]
    for sx in (-1, 1):
        x = sx * P.col_x
        tube = cyl(P.col_d, (x, P.col_y, z0), (x, P.col_y, z1)).cut(
            cyl(P.col_d - 2 * P.col_wall, (x, P.col_y, z0 - 1.0), (x, P.col_y, z1 + 1.0)))
        out.append(tube)
        out.append(cyl(P.col_d + 10.0, (x, P.col_y, z1), (x, P.col_y, z1 + 5.0)))
    return compound(out)


def slot_plates():
    """2 plates 8 mm under the top cross tube with the vertical slot for the LA36 rod pin."""
    xi = Q.act_rod_eye_c / 2.0 + Q.act_eye_clear
    a = (P.act_y, P.act_top_z)
    e = (P.act_y, P.act_top_z + P.float_slot)
    y0 = P.col_y - P.cross[1] / 2.0
    out = []
    for sx in (-1, 1):
        x0 = xi if sx > 0 else -xi - 8.0
        x1 = x0 + 8.0
        pl = box_span((x0, x1), (y0 + 2.0, a[0] + 20.0), (a[1] - 20.0, P.top_cross_z + 1.0))
        pl = pl.fuse(cyl(40.0, (x0, a[0], a[1]), (x1, a[0], a[1])))
        out.append(pl.cut(GA._slot_x(x0 - 1.0, x1 + 1.0, a, e, Q.act_pin_d + 0.4)))
    return compound(out)


# ---------------------------------------------------------------------
# Carriage (translates up), drawn at dz = 0
# ---------------------------------------------------------------------
def housings():
    """4 bush housings: tube O76 x 60 with a web to the carriage plate (welded), an iglidur bush inside."""
    d, hz = P.housing
    yb, zb = P.cp_base_low
    out = []
    for sx in (-1, 1):
        x = sx * P.col_x
        for dz in P.housing_dz:
            z = zb + dz
            ring = cyl(d, (x, P.col_y, z - hz / 2.0), (x, P.col_y, z + hz / 2.0))
            web = box_span((x - 12.0, x + 12.0), (P.cr_plate_y[1], P.col_y - d / 2.0 + 5.0), (z - hz / 2.0, z + hz / 2.0))
            out.append(ring.fuse(web).cut(cyl(P.col_d + 6.0, (x, P.col_y, z - hz), (x, P.col_y, z + hz))))
    return compound(out)


def bushes():
    """iglidur bushes (3 mm wall) in the housings, running on the columns."""
    yb, zb = P.cp_base_low
    hz = P.housing[1]
    out = []
    for sx in (-1, 1):
        x = sx * P.col_x
        for dz in P.housing_dz:
            z = zb + dz
            out.append(cyl(P.col_d + 6.0, (x, P.col_y, z - hz / 2.0), (x, P.col_y, z + hz / 2.0)).cut(
                cyl(P.col_d + 0.2, (x, P.col_y, z - hz), (x, P.col_y, z + hz))))
    return compound(out)


def carriage_plate():
    """Plate 10 mm, 2 wedge brackets to the front of the male triangle, 2 lugs for the LA36 back fixture."""
    yb, zb = P.cp_base_low
    z0, z1 = zb + P.cr_plate_dz[0], zb + P.cr_plate_dz[1]
    plate = box_span((-P.cr_plate_x, P.cr_plate_x), P.cr_plate_y, (z0, z1))
    yw = (P.cr_plate_y[0] - 1.0, P.cr_plate_y[1] + 1.0)
    for xw in ((-95.0, 95.0), (145.0, 205.0), (-205.0, -145.0)):
        plate = plate.cut(box_span(xw, yw, (zb + 100.0, zb + 320.0)))
    parts = [plate]
    lo = Q.cp_point(P.cp_base_low, (40.0, -Q.cp_tube / 2.0))
    hi = Q.cp_point(P.cp_base_low, (400.0, -Q.cp_tube / 2.0))
    wedge = ((P.cr_plate_y[0], z0 + 20.0), (P.cr_plate_y[0], min(z1, hi[1])), (hi[0], hi[1]), (lo[0], lo[1]))
    for sx in (-1, 1):
        parts.append(plate_yz(wedge, sx * P.cr_bracket_x - 4.0, 8.0))
    # LA36 back fixture lugs on the front of the plate (within r 14 of the pin upwards: the hex starts at 14.9)
    yp, zp = P.body_pin(0.0)
    xi = Q.act_back_c / 2.0 + Q.act_eye_clear
    lug = ((P.cr_plate_y[1] - 1.0, zp - 30.0), (P.cr_plate_y[1] - 1.0, zp + 12.0), (yp, zp + 12.0), (yp + 14.0, zp),
           (yp, zp - 30.0))
    for sx in (-1, 1):
        x0 = xi if sx > 0 else -xi - 8.0
        pl = plate_yz(lug, x0, 8.0).fuse(cyl(28.0, (x0, yp, zp), (x0 + 8.0, yp, zp)))
        parts.append(pl.cut(cyl(Q.act_pin_d + 0.4, (x0 - 1.0, yp, zp), (x0 + 9.0, yp, zp))))
    return fuse_all(parts)


def carriage_pins():
    yp, zp = P.body_pin(0.0)
    xa = Q.act_back_c / 2.0 + Q.act_eye_clear + 8.0 + 4.0
    return pin_x(-xa, xa, yp, zp, Q.act_pin_d, head_d=20.0)


def male_frame():
    return GA.male_frame(P.cp_base_low, act_lugs=False, brace_lugs=False)


def male_latch():
    return GA.male_latch(P.cp_base_low)


# ---------------------------------------------------------------------
# Demo machine (standing on its legs, robot at y 0): female triangle, front cross tube, side rails, box, legs
# ---------------------------------------------------------------------
def _mc_front():
    """(y, z) range of the front cross tube: behind the female lock plate."""
    w_back = Q.cp_tube / 2.0 + Q.cf_gap + Q.cf_t
    y_lock = Q.cp_point(P.mc_base, (Q.cf_lock_v[0], w_back))[0]
    y1 = y_lock - P.mc_cross_y
    zc = P.mc_base[1] + 10.0
    return (y1 - P.mc_cross, y1), (zc - P.mc_cross / 2.0, zc + P.mc_cross / 2.0)


def machine_frame():
    """Weldment: female triangle, base plate, front cross tube 60 x 60, side rails 50 x 50, 4 parking legs with
    foot plates, 2 stays from the hook to the rails."""
    yb, zb = P.mc_base
    cy, cz = _mc_front()
    w_back = Q.cp_tube / 2.0 + Q.cf_gap
    parts = [GA.female(P.mc_base)]
    parts.append(tube_span((-P.mc_rail_x - P.mc_rail / 2.0, P.mc_rail_x + P.mc_rail / 2.0), cy, cz, 3.0, "x"))
    y_front = Q.cp_point(P.mc_base, (Q.cf_lock_v[0], w_back))[0]
    parts.append(box_span((-Q.cf_lock_u - 30.0, Q.cf_lock_u + 30.0), (cy[0], y_front), (cz[1], cz[1] + 8.0)))
    rz = (cz[1] - P.mc_rail, cz[1])
    ry = (cy[0] - P.mc_len, cy[0])
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (P.mc_rail_x - P.mc_rail / 2.0), sx * (P.mc_rail_x + P.mc_rail / 2.0)))
        parts.append(tube_span((x0, x1), ry, rz, 3.0, "y"))
        for ly in P.mc_leg_y:
            y = yb + ly
            h = P.mc_leg / 2.0
            parts.append(tube_span((sx * P.mc_rail_x - h, sx * P.mc_rail_x + h), (y - h, y + h),
                                   (P.mc_foot[1], rz[0]), 3.0, "z"))
            f = P.mc_foot[0] / 2.0
            parts.append(box_span((sx * P.mc_rail_x - f, sx * P.mc_rail_x + f), (y - f, y + f), (0.0, P.mc_foot[1])))
    # rear cross tube
    parts.append(tube_span((-P.mc_rail_x, P.mc_rail_x), (ry[0], ry[0] + P.mc_rail), rz, 3.0, "x"))
    hy, hz = Q.cp_point(P.mc_base, (Q.cp_top_v[1] - 10.0, w_back + Q.cf_t + 5.0))
    for sx in (-1, 1):
        parts.append(rect_tube((sx * 50.0, hy, hz), (sx * 200.0, cy[0] + 15.0, cz[1] + 8.0), 10.0, 40.0,
                               up=(1.0, 0.0, 0.0)))
    return fuse_all(parts)


def machine_box():
    """Box (PE, 4 mm wall) on the rails, open at the top."""
    yb, _ = P.mc_base
    _, cz = _mc_front()
    bx, by, bh = P.mc_box
    y1 = yb + P.mc_box_y0
    z0 = cz[1] + 1.0
    t = P.mc_box_wall
    outer = box_span((-bx / 2.0, bx / 2.0), (y1 - by, y1), (z0, z0 + bh))
    inner = box_span((-bx / 2.0 + t, bx / 2.0 - t), (y1 - by + t, y1 - t), (z0 + t, z0 + bh + 1.0))
    return outer.cut(inner)


def machine_load():
    """Content of the box (a layer of seed), for the picture and the mass."""
    yb, _ = P.mc_base
    _, cz = _mc_front()
    bx, by, bh = P.mc_box
    y1 = yb + P.mc_box_y0
    z0 = cz[1] + 1.0 + P.mc_box_wall
    t = P.mc_box_wall
    h = P.mc_load_kg / (0.75e-6 * (bx - 2 * t) * (by - 2 * t))      # bulk density 0.75 kg/l
    return box_span((-bx / 2.0 + t, bx / 2.0 - t), (y1 - by + t, y1 - t), (z0, z0 + h))
