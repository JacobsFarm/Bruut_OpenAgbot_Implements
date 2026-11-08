"""Parts of the parallel hitch. Every function returns a Part shape in robot coordinates in the work pose (links at
theta_work, carrier and cultivator in work). build_tpp.py turns the links about their front pins, translates the
carrier and the implement and places the LA36. The coupler, the LA36 and the cultivator come from ../a_frame
(tpa_parts), the toolbar and hangers from ../simple (tph_parts).
"""
import math

import Part
from FreeCAD import Vector as V

import tpp_params as P
import tpa_params as Q
import tpa_parts as GA
from tph_parts import box_span, cyl, tube_span, rect_tube, fuse_all, plate_yz  # noqa: F401
from tpa_parts import compound, pin_x


def _xs_cheeks(sx):
    """x ranges (sorted) of the inner and outer cheek of the link pair on side sx."""
    a = P.link_x - P.link_tube / 2.0 - P.cheek_gap
    b = P.link_x + P.link_tube / 2.0 + P.cheek_gap
    rng = ((a - P.cheek_t, a), (b, b + P.cheek_t))
    return [tuple(sorted((sx * r[0], sx * r[1]))) for r in rng]


# ---------------------------------------------------------------------
# Headstock on the toolbar (fixed)
# ---------------------------------------------------------------------
def hs_cheeks():
    """4 cheeks 8 mm, notched around the toolbar and welded to it, with the front pin holes."""
    lo, hi = P.front_pins()
    y0, y1 = P.hs_y
    pts = ((y0, P.hs_z_bot + 10.0), (lo[0] + 20.0, P.hs_z_bot), (y1, P.tb_z[0] - 10.0),
           (y1, P.hs_cross_c[1] + P.hs_cross / 2.0), (P.hs_cross_c[0] - P.hs_cross / 2.0 - 5.0,
                                                       P.hs_cross_c[1] + P.hs_cross / 2.0),
           (hi[0] - 22.0, hi[1] + 10.0), (y0, P.tb_z[1] - 20.0))
    tb = box_span((-600.0, 600.0), P.tb_y, P.tb_z)
    out = []
    for sx in (-1, 1):
        for x0, x1 in _xs_cheeks(sx):
            pl = plate_yz(pts, x0, x1 - x0)
            pl = pl.fuse([cyl(40.0, (x0, p[0], p[1]), (x1, p[0], p[1])) for p in (lo, hi)]).cut(tb)
            for p in (lo, hi):
                pl = pl.cut(cyl(P.pin_d + 0.4, (x0 - 1.0, p[0], p[1]), (x1 + 1.0, p[0], p[1])))
            out.append(pl.removeSplitter())
    return compound(out)


def hs_cross():
    """Top cross tube 40 x 40 x 3 between the inner cheeks: carries the slot plates of the LA36."""
    xi = _xs_cheeks(1)[0][0]
    h = P.hs_cross / 2.0
    y, z = P.hs_cross_c
    return tube_span((-xi, xi), (y - h, y + h), (z - h, z + h), 3.0, "x")


def slot_end():
    u = P.slot_dir()
    s = P.float_slot()
    return P.act_a[0] + s * u[0], P.act_a[1] + s * u[1]


def hs_slot_plates():
    """2 plates 8 mm under the cross tube with the slot for the LA36 rod pin (closes when lifting)."""
    a, e = P.act_a, slot_end()
    xi = Q.act_rod_eye_c / 2.0 + Q.act_eye_clear
    h = P.hs_cross / 2.0
    yc, zc = P.hs_cross_c
    pts = ((yc - h + 2.0, zc - h + 1.0), (yc + h - 2.0, zc - h + 1.0), (e[0] + 18.0, e[1] + 8.0),
           (e[0] + 6.0, e[1] - 20.0), (a[0] - 6.0, a[1] - 21.0), (a[0] - 20.0, a[1] + 4.0))
    out = []
    for sx in (-1, 1):
        x0 = xi if sx > 0 else -xi - 8.0
        x1 = x0 + 8.0
        pl = plate_yz(pts, x0, 8.0).fuse([cyl(40.0, (x0, p[0], p[1]), (x1, p[0], p[1])) for p in (a, e)])
        out.append(pl.cut(GA._slot_x(x0 - 1.0, x1 + 1.0, a, e, Q.act_pin_d + 0.4)).removeSplitter())
    return compound(out)


def hs_pins():
    """Front pins O16 through both cheeks and the link bosses (head outside)."""
    out = []
    for sx in (-1, 1):
        (ai, bi), (ao, bo) = _xs_cheeks(sx)
        x_in = ai - 4.0 if sx > 0 else bi + 4.0
        x_out = bo + 4.0 if sx > 0 else ao - 4.0
        for p in P.front_pins():
            out.append(pin_x(x_in, x_out, p[0], p[1], P.pin_d, head_d=26.0))
    return compound(out)


# ---------------------------------------------------------------------
# Links (work pose; each turns about its front pin)
# ---------------------------------------------------------------------
def link(sx, upper):
    f = P.front_pins()[1 if upper else 0]
    r = P.rear_pins0()[1 if upper else 0]
    x = sx * P.link_x
    w = P.link_tube / 2.0
    bar = rect_tube((x, f[0], f[1]), (x, r[0], r[1]), P.link_tube, P.link_tube, P.link_wall)
    bosses = [cyl(P.link_boss_d, (x - w, p[0], p[1]), (x + w, p[0], p[1])) for p in (f, r)]
    s = bar.fuse(bosses).removeSplitter()
    for p in (f, r):
        s = s.cut(cyl(P.pin_d + 0.4, (x - w - 1, p[0], p[1]), (x + w + 1, p[0], p[1])))
    return s


# ---------------------------------------------------------------------
# Carrier (rear frame, translates) with the male triangle
# ---------------------------------------------------------------------
def carrier_plates():
    """2 plate pairs 8 mm on the front of the male triangle (bolted to its bottom and middle cross tubes), with the
    rear pin holes, and the 2 lugs for the LA36 back fixture."""
    v0, v1 = P.cr_v
    w0, w1 = P.cr_w
    prof = ((v0, w0), (v1, w0), (v1 - 12.0, w1), (v0 + 12.0, w1))
    pins = (P.rear_pin_lo, P.rear_pin_hi)
    loc = []
    for sx in (-1, 1):
        for x0, x1 in _xs_cheeks(sx):
            pl = plate_yz(prof, x0, x1 - x0)
            pl = pl.fuse([cyl(40.0, (x0, p[0], p[1]), (x1, p[0], p[1])) for p in pins])
            for p in pins:
                pl = pl.cut(cyl(P.pin_d + 0.4, (x0 - 1.0, p[0], p[1]), (x1 + 1.0, p[0], p[1])))
            loc.append(pl.removeSplitter())
    # LA36 back fixture lugs: within r 14 of the pin towards the actuator (the hex of the fixture starts at 14.9)
    vb, wb = P.act_body_pin
    xi = Q.act_back_c / 2.0 + Q.act_eye_clear
    lug = ((vb - 12.0, w0 + 2.0), (vb + 35.0, w0 + 2.0), (vb + 10.0, wb + 7.0), (vb - 10.0, wb - 3.0))
    for sx in (-1, 1):
        x0 = xi if sx > 0 else -xi - 8.0
        pl = plate_yz(lug, x0, 8.0).fuse(cyl(28.0, (x0, vb, wb), (x0 + 8.0, vb, wb)))
        loc.append(pl.cut(cyl(Q.act_pin_d + 0.4, (x0 - 1.0, vb, wb), (x0 + 9.0, vb, wb))))
    return GA.to_robot(compound(loc), P.cp_base)


def carrier_pins():
    """Rear pins O16 (through the plates and the link bosses) and the LA36 body pin O12."""
    out = []
    for sx in (-1, 1):
        (ai, bi), (ao, bo) = _xs_cheeks(sx)
        x_in = ai - 4.0 if sx > 0 else bi + 4.0
        x_out = bo + 4.0 if sx > 0 else ao - 4.0
        for p in (P.rear_pin_lo, P.rear_pin_hi):
            out.append(pin_x(x_in, x_out, p[0], p[1], P.pin_d, head_d=26.0))
    vb, wb = P.act_body_pin
    xa = Q.act_back_c / 2.0 + Q.act_eye_clear + 8.0 + 4.0
    out.append(pin_x(-xa, xa, vb, wb, Q.act_pin_d, head_d=20.0))
    return GA.to_robot(compound(out), P.cp_base)


def male_frame():
    return GA.male_frame(P.cp_base, act_lugs=False, brace_lugs=False)


def male_latch():
    return GA.male_latch(P.cp_base)
