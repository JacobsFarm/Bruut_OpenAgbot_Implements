import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import sol_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basic functions (same style as the other implements)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl_z(d, z0, z1, x, y):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out


def tube_x(x, y, z, wall):
    return box_span(x, y, z).cut(box_span((x[0] - 1, x[1] + 1), (y[0] + wall, y[1] - wall), (z[0] + wall, z[1] - wall)))


def tube_y(x, y, z, wall):
    return box_span(x, y, z).cut(box_span((x[0] + wall, x[1] - wall), (y[0] - 1, y[1] + 1), (z[0] + wall, z[1] - wall)))


def tube_z(x, y, z, wall):
    return box_span(x, y, z).cut(box_span((x[0] + wall, x[1] - wall), (y[0] + wall, y[1] - wall), (z[0] - 1, z[1] + 1)))


def round_tube(p0, p1, d, wall):
    """Round tube between two points (centre line)."""
    p0, p1 = V(*p0), V(*p1)
    d_vec = p1 - p0
    outer = Part.makeCylinder(d / 2.0, d_vec.Length, p0, d_vec)
    inner = Part.makeCylinder(d / 2.0 - wall, d_vec.Length, p0, d_vec)
    return outer.cut(inner)


def hex_head(x, y, z0, z1, af):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))


# ---------------------------------------------------------------------
# Layout of the panels
# ---------------------------------------------------------------------
def total_width():
    return P.n_panels * P.panel_w + (P.n_panels - 1) * P.panel_gap


def panel_centres():
    x0 = -total_width() / 2.0 + P.panel_w / 2.0
    return [x0 + i * (P.panel_w + P.panel_gap) for i in range(P.n_panels)]


def mast_x():
    """Centre of the first gap between the panels (x = 0 for 2 panels)."""
    return -total_width() / 2.0 + P.panel_w + P.panel_gap / 2.0


def cross_half():
    return total_width() / 2.0


def z_panel_top():
    return P.z_cross_top + P.panel_t


# ---------------------------------------------------------------------
# Base frame
# ---------------------------------------------------------------------
def long_tubes():
    return [tube_x((-P.long_tube_half, P.long_tube_half), (y - P.tube / 2, y + P.tube / 2),
                   (P.z_long_bot, P.z_long_top), P.tube_wall) for y in P.long_tube_y]


def mount_points():
    return [(sx * x, y) for x in P.upper_beam_x for sx in (-1, 1) for y in P.long_tube_y]


def mount_sleeves():
    return fuse([cyl_z(P.mount_sleeve_d, P.z_long_bot + P.tube_wall, P.z_long_top - P.tube_wall, x, y).cut(
        cyl_z(P.mount_bolt_d, P.z_long_bot, P.z_long_top, x, y)) for x, y in mount_points()])


def mount_bolts():
    out = []
    z_top = P.z_long_top
    for x, y in mount_points():
        out.append(cyl_z(P.mount_bolt_d, z_top - P.mount_bolt_len, z_top, x, y))
        out.append(hex_head(x, y, z_top, z_top + P.bolt_head_k, P.bolt_head_af))
        z_beam_bot = P.upper_beam_top - P.upper_beam_w
        out.append(hex_head(x, y, z_beam_bot - P.nut_m, z_beam_bot, P.bolt_head_af))
    return fuse(out)


def stringers():
    h = P.stringer / 2.0
    return [tube_y((sx * P.stringer_x - h, sx * P.stringer_x + h), (-P.stringer_half, P.stringer_half),
                   (P.z_str_bot, P.z_str_top), P.stringer_wall) for sx in (-1, 1)]


# ---------------------------------------------------------------------
# Canopy frame
# ---------------------------------------------------------------------
def posts():
    h = P.post / 2.0
    out = []
    for sx in (-1, 1):
        for y in P.post_y:
            x = sx * P.post_x
            out.append(tube_z((x - h, x + h), (y - h, y + h), (P.z_str_top, P.z_rail_bot), P.post_wall))
    return out


def rails():
    h = P.rail / 2.0
    return [tube_y((sx * P.post_x - h, sx * P.post_x + h), (-P.rail_half, P.rail_half),
                   (P.z_rail_bot, P.z_rail_top), P.rail_wall) for sx in (-1, 1)]


def cross_members():
    h = P.cross / 2.0
    return [tube_x((-cross_half(), cross_half()), (y - h, y + h), (P.z_rail_top, P.z_cross_top), P.cross_wall)
            for y in P.cross_y]


def struts():
    """Diagonal tubes (x-z plane) from the end of each long tube up to the overhanging cross member."""
    z0 = (P.z_long_bot + P.z_long_top) / 2.0
    x1 = cross_half() - P.strut_x_out_from_edge
    out = []
    for sx in (-1, 1):
        for y in P.long_tube_y:
            p0 = (sx * (P.strut_x_in + P.brace_d / 2.0), y, z0)
            p1 = (sx * x1, y, P.z_rail_top - P.brace_d / 2.0)
            out.append(round_tube(p0, p1, P.brace_d, P.brace_wall))
    return out


def y_braces():
    """Diagonal tubes (y-z plane) from the middle of the stringers up to the posts: stiffness in driving direction."""
    out = []
    z0 = P.z_str_top + P.brace_d / 2.0 + 1.0
    z1 = P.z_rail_bot - P.brace_d
    for sx in (-1, 1):
        x = sx * P.post_x
        for sy in (-1, 1):
            p0 = (x, sy * P.brace_y_in, z0)
            p1 = (x, sy * (abs(P.post_y[0]) - P.post / 2.0 - P.brace_d / 2.0 - 1.0), z1)
            out.append(round_tube(p0, p1, P.brace_d, P.brace_wall))
    return out


# ---------------------------------------------------------------------
# Solar panels
# ---------------------------------------------------------------------
def z_lam_top():
    return P.panel_t - 2.0


def panel_frame(cx):
    z0 = P.z_cross_top
    outer = box_span((cx - P.panel_w / 2, cx + P.panel_w / 2), (-P.panel_l / 2, P.panel_l / 2), (z0, z0 + P.panel_t))
    inner = box_span((cx - P.panel_w / 2 + P.panel_frame_w, cx + P.panel_w / 2 - P.panel_frame_w),
                     (-P.panel_l / 2 + P.panel_frame_w, P.panel_l / 2 - P.panel_frame_w),
                     (z0 - 1, z0 + P.panel_t + 1))
    return outer.cut(inner)


def panel_laminate(cx):
    z1 = P.z_cross_top + z_lam_top()
    return box_span((cx - P.panel_w / 2 + P.panel_frame_w, cx + P.panel_w / 2 - P.panel_frame_w),
                    (-P.panel_l / 2 + P.panel_frame_w, P.panel_l / 2 - P.panel_frame_w),
                    (z1 - P.laminate_t, z1))


def panel_cells(cx):
    """Cell grid as thin plates on the laminate (one compound)."""
    z1 = P.z_cross_top + z_lam_top()
    wx = P.panel_w - 2 * P.panel_frame_w
    wy = P.panel_l - 2 * P.panel_frame_w
    px = wx / P.cell_cols
    py = wy / P.cell_rows
    cells = []
    for i in range(P.cell_cols):
        for j in range(P.cell_rows):
            x0 = cx - wx / 2 + i * px + P.cell_gap / 2
            y0 = -wy / 2 + j * py + P.cell_gap / 2
            cells.append(box_span((x0, x0 + px - P.cell_gap), (y0, y0 + py - P.cell_gap), (z1, z1 + 0.4)))
    return Part.makeCompound(cells)


def panel_junction_box(cx):
    """Junction box under the laminate, inside the frame, near the rear end of the panel."""
    jx, jy, jz = P.junction_box
    z_under = P.z_cross_top + z_lam_top() - P.laminate_t
    y1 = P.panel_l / 2 - P.panel_frame_w - 60.0
    return box_span((cx - jx / 2, cx + jx / 2), (y1 - jy, y1), (z_under - jz, z_under))


def panel_bolts():
    """M8 bolts through the long side frames of every panel into the cross members, nut below."""
    out = []
    zt = z_panel_top()
    z_nut = P.z_cross_top - P.cross - 6.8
    for cx in panel_centres():
        for sx in (-1, 1):
            x = cx + sx * (P.panel_w / 2 - P.panel_frame_w / 2)
            for y in P.cross_y:
                out.append(cyl_z(P.bolt_d, z_nut, zt, x, y))
                out.append(hex_head(x, y, zt, zt + P.bolt_head_k8, P.bolt_head_af8))
                out.append(hex_head(x, y, z_nut, z_nut + 6.8, P.bolt_head_af8))
    return fuse(out)


# ---------------------------------------------------------------------
# Electronics, GNSS
# ---------------------------------------------------------------------
def mppt_plate():
    x, y, z = P.mppt
    return box_span((-x / 2 - 10, x / 2 + 10), (P.mppt_y - y / 2 - 10, P.mppt_y + y / 2 + 10),
                    (P.z_long_top, P.z_long_top + P.mppt_plate_t))


def mppt_box():
    x, y, z = P.mppt
    z0 = P.z_long_top + P.mppt_plate_t
    return box_span((-x / 2, x / 2), (P.mppt_y - y / 2, P.mppt_y + y / 2), (z0, z0 + z))


def gnss_mast():
    return cyl_z(P.gnss_mast_d, P.z_cross_top, P.z_cross_top + P.gnss_mast_h, mast_x(), P.gnss_mast_y)


def gnss_antenna():
    z0 = P.z_cross_top + P.gnss_mast_h
    stem = cyl_z(P.gnss_stem_d, z0, z0 + P.gnss_stem_h, mast_x(), P.gnss_mast_y)
    a = P.gnss_dome_d / 2.0
    h = P.gnss_dome_h
    r = (a * a + h * h) / (2.0 * h)
    zc = z0 + P.gnss_stem_h
    sph = Part.makeSphere(r, V(mast_x(), P.gnss_mast_y, zc + h - r))
    keep = box_span((mast_x() - a - 1, mast_x() + a + 1), (P.gnss_mast_y - a - 1, P.gnss_mast_y + a + 1), (zc, zc + h + 1))
    return fuse([stem, sph.common(keep)])
