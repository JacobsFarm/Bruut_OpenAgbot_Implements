"""Onderdelen voor de veldanimaties: de werktank met vultrechter op de werkrobot (robotcoordinaten) en het veld met
banen, kopakkers en de sporen van de applicator (veldcoordinaten, zie fld_params.py)."""
import math

import Part
from FreeCAD import Vector as V

import fld_params as P

Z = V(0, 0, 1)


def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def rbox(x, y, z, r):
    """Blok met afgeronde staande ribben."""
    b = box_span(x, y, z)
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1.0]
    return b.makeFillet(r, edges) if r > 0 else b


def cyl_z(d, z0, z1, x, y):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


# ---------------------------------------------------------------------
# Werktank met trechter (robotcoordinaten)
# ---------------------------------------------------------------------
RX_TOP = P.rx_tank_z0 + P.rx_tank_h
CRADLE_Z = (P.rx_tank_z0 - 5.0 - 40.0, P.rx_tank_z0 - 5.0)


def cradle_tubes():
    out = []
    for y in P.cradle_y:
        outer = box_span((-P.cradle_half_len, P.cradle_half_len), (y - 20.0, y + 20.0), CRADLE_Z)
        inner = box_span((-P.cradle_half_len - 1, P.cradle_half_len + 1), (y - 17.0, y + 17.0),
                         (CRADLE_Z[0] + 3.0, CRADLE_Z[1] - 3.0))
        out.append(outer.cut(inner))
    return Part.makeCompound(out)


def cradle_pads():
    return Part.makeCompound([box_span((-300.0, 300.0), (y - 20.0, y + 20.0), (CRADLE_Z[1], P.rx_tank_z0))
                              for y in P.cradle_y])


def tank_inner():
    w = P.rx_wall
    return rbox((-P.rx_tank_x + w, P.rx_tank_x - w), (P.rx_tank_y[0] + w, P.rx_tank_y[1] - w),
                (P.rx_tank_z0 + w, RX_TOP - w), P.rx_tank_r - w)


def tank_shell():
    return rbox((-P.rx_tank_x, P.rx_tank_x), P.rx_tank_y, (P.rx_tank_z0, RX_TOP), P.rx_tank_r).cut(tank_inner())


def tank_volume_l():
    return tank_inner().Volume / 1e6


def level_z(litres):
    """Vloeistofhoogte (z) bij een inhoud: de tank is prismatisch."""
    w = P.rx_wall
    area = tank_inner().Volume / (P.rx_tank_h - 2.0 * w)
    return P.rx_tank_z0 + w + max(0.0, litres) * 1e6 / area


def liquid(litres):
    z = min(level_z(litres), RX_TOP - P.rx_wall - 0.5)
    if z <= P.rx_tank_z0 + P.rx_wall + 0.5:
        return Part.Shape()
    return tank_inner().common(box_span((-1000, 1000), (-1000, 1000), (0.0, z)))


def straps():
    t, w = 3.0, 50.0
    out = []
    for y in P.cradle_y:
        yy = (y - w / 2.0, y + w / 2.0)
        out.append(box_span((-P.rx_tank_x - t, P.rx_tank_x + t), yy, (RX_TOP, RX_TOP + t)))
        for s in (-1, 1):
            x = (s * P.rx_tank_x, s * (P.rx_tank_x + t))
            out.append(box_span((min(x), max(x)), yy, (CRADLE_Z[1], RX_TOP + t)))
    return Part.makeCompound(out)


def funnel():
    x, y = P.funnel_xy
    z0 = RX_TOP + P.funnel_neck
    rim, out_d = P.funnel_d
    cone = Part.makeCone(out_d / 2.0, rim / 2.0, P.funnel_h, V(x, y, z0), Z)
    inner = Part.makeCone(out_d / 2.0 - 3.0, rim / 2.0 - 3.0, P.funnel_h + 0.02, V(x, y, z0 + 0.01), Z)
    neck = cyl_z(out_d, RX_TOP - 2.0, z0 + 1.0, x, y).cut(cyl_z(out_d - 6.0, RX_TOP - 3.0, z0 + 2.0, x, y))
    return cone.cut(inner).fuse(neck)


def strainer():
    """Zeef onderin de trechter (als de ontvangerkit van de refillers): onder de tuit van de giek-refiller, die tot
    z 1080 zakt."""
    x, y = P.funnel_xy
    z = RX_TOP + P.funnel_neck + 10.0
    return cyl_z(P.funnel_d[1] + 18.0, z, z + 2.0, x, y)


def level_sensor():
    return cyl_z(50.0, RX_TOP, RX_TOP + 80.0, 260.0, 220.0)


def vent():
    return cyl_z(20.0, RX_TOP, RX_TOP + 60.0, 260.0, -80.0)


def feed_pipe():
    """Uitloop van de tank (achter, laag) naar de verdeelbuis van de pomp: kort stuk slang."""
    x, y = 0.0, P.rx_tank_y[0]
    return Part.makeCylinder(12.0, 60.0, V(x, y, P.rx_tank_z0 + 30.0), V(0, -1, 0))


# ---------------------------------------------------------------------
# Veld (veldcoordinaten)
# ---------------------------------------------------------------------
X_RANGE = (-13000.0, 17000.0)
R_DEPTH = P.YS + 3600.0             # kopakker R tot aan het hek
F_DEPTH = P.YS + 2600.0


def ground():
    L = P.FIELD_LEN
    field = box_span((-P.W / 2.0, (P.N_PASSES - 0.5) * P.W), (-L, 0.0), (-40.0, 0.0))
    head = Part.makeCompound([box_span(X_RANGE, (0.0, R_DEPTH), (-40.0, -0.5)),
                              box_span(X_RANGE, (-L - F_DEPTH, -L), (-40.0, -0.5)),
                              box_span((X_RANGE[0], -P.W / 2.0), (-L, 0.0), (-40.0, -0.5)),
                              box_span(((P.N_PASSES - 0.5) * P.W, X_RANGE[1]), (-L, 0.0), (-40.0, -0.5))])
    return field, head


def pass_lines():
    """Grenzen tussen de banen (dunne lichte lijnen) en de veldranden."""
    L = P.FIELD_LEN
    out = [box_span(((k - 0.5) * P.W - 8.0, (k - 0.5) * P.W + 8.0), (-L, 0.0), (0.0, 0.6)) for k in range(P.N_PASSES + 1)]
    for y in (0.0, -L):
        out.append(box_span((-P.W / 2.0, (P.N_PASSES - 0.5) * P.W), (y - 25.0, y + 25.0), (0.0, 0.8)))
    return Part.makeCompound(out)


def fence():
    posts, wires = [], []
    for y in (R_DEPTH - 300.0, -P.FIELD_LEN - F_DEPTH + 300.0):
        x = X_RANGE[0] + 500.0
        while x <= X_RANGE[1] - 500.0:
            posts.append(cyl_z(100.0, 0.0, 1200.0, x, y))
            x += 3000.0
        for z in (500.0, 900.0, 1150.0):
            wires.append(Part.makeCylinder(4.0, X_RANGE[1] - X_RANGE[0] - 1000.0, V(X_RANGE[0] + 500.0, y, z),
                                           V(1, 0, 0)))
    return Part.makeCompound(posts), Part.makeCompound(wires)


def band(x, y0, y1, z=0.9):
    """Behandelde baan (1 m breed, iets donkerder groen)."""
    if y0 is None or y1 - y0 < 5.0:
        return Part.Shape()
    return box_span((x - P.W / 2.0 + 30.0, x + P.W / 2.0 - 30.0), (y0, y1), (0.0, z))


def rows(x, row_x, y0, y1, w, z0, z1):
    if y0 is None or y1 is None or y1 - y0 < 5.0:
        return Part.Shape()
    return Part.makeCompound([box_span((x + rx - w / 2.0, x + rx + w / 2.0), (y0, y1), (z0, z1)) for rx in row_x])


def stream(x, y, z0, z1, d=22.0):
    return cyl_z(d, z1, z0, x, y)


def path_line(points, w=40.0, z=1.2):
    """Gestippelde lijn over de grond (route van de werkrobot op de kopakker)."""
    out = []
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(points[:-1], points[1:])):
        if i % 2:
            continue
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy)
        if n < 1.0:
            continue
        nx, ny = -dy / n * w / 2.0, dx / n * w / 2.0
        poly = Part.makePolygon([V(x0 + nx, y0 + ny, z), V(x1 + nx, y1 + ny, z), V(x1 - nx, y1 - ny, z),
                                 V(x0 - nx, y0 - ny, z), V(x0 + nx, y0 + ny, z)])
        out.append(Part.Face(poly))
    return Part.makeCompound(out) if out else Part.Shape()
