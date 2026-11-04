"""Parts of the air-assisted orchard sprayer. Every function returns a Part shape in robot coordinates.
Tank, pump and control box come from the spot sprayer (ssp_parts, imported in build_oas). Fan pods are drawn for the
right side (+x) and mirrored."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import oas_params as P
from ssp_parts import box_span, cyl_x, cyl_y, cyl_z, fuse_all, hose, bolt_z, mirror_x

SIDES = (-1, 1)


def sq_tube_y(y0, y1, x, z, w, h, wall):
    y0, y1 = sorted((y0, y1))
    o = box_span((x - w / 2.0, x + w / 2.0), (y0, y1), z)
    i = box_span((x - w / 2.0 + wall, x + w / 2.0 - wall), (y0 + 3.0, y1 - 3.0), (z[0] + wall, z[1] - wall))
    return o.cut(i)


def sq_tube_x(x0, x1, y, z, a, wall):
    o = box_span((x0, x1), (y - a / 2.0, y + a / 2.0), z)
    i = box_span((x0 + 3.0, x1 - 3.0), (y - a / 2.0 + wall, y + a / 2.0 - wall), (z[0] + wall, z[1] - wall))
    return o.cut(i)


def sq_tube_z(z0, z1, x, y, a, wall):
    o = box_span((x - a / 2.0, x + a / 2.0), (y - a / 2.0, y + a / 2.0), (z0, z1))
    i = box_span((x - a / 2.0 + wall, x + a / 2.0 - wall), (y - a / 2.0 + wall, y + a / 2.0 - wall), (z0 + 3.0, z1 - 3.0))
    return o.cut(i)


def both(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


# ---------------------------------------------------------------------
# Tower mount
# ---------------------------------------------------------------------
ARM_BOLTS = [(s * P.arm_x, y) for s in SIDES for y in P.arm_bolt_y]


def arms():
    out = []
    for s in SIDES:
        t = sq_tube_y(P.arm_y[0], P.arm_y[1], s * P.arm_x, P.arm_z, P.arm_w, P.arm_h, P.arm_wall)
        out.append(t.cut([cyl_z(P.m10_hole, P.arm_z[0] - 1, P.arm_z[1] + 1, x, y) for (x, y) in ARM_BOLTS]))
    return Part.makeCompound(out)


def arm_bolts():
    """M10 from under the arm up through the lower beam and the control box base plate (4 mm), nut on top."""
    z_top = P.robot_lower_beam_z[1] + 4.0
    return Part.makeCompound([_bolt_up(x, y, P.arm_z[0], z_top) for (x, y) in ARM_BOLTS])


def _bolt_up(x, y, z_head_top, z_nut_bottom, d=10.0, af=17.0, k=6.4, m=8.4):
    """Head under z_head_top (below the arm), shank up, nut on z_nut_bottom."""
    from ssp_parts import hex_prism_z
    head = hex_prism_z(af, z_head_top - k, z_head_top, x, y)
    shank = cyl_z(d, z_head_top, z_nut_bottom + m + 4.0, x, y)
    nut = hex_prism_z(af, z_nut_bottom, z_nut_bottom + m, x, y).cut(cyl_z(d, z_nut_bottom - 1, z_nut_bottom + m + 1, x, y))
    return fuse_all([head, shank, nut])


def cross_beam():
    a, w = P.cross_beam
    x1 = P.arm_x - P.arm_w / 2.0
    return sq_tube_x(-x1, x1, P.mast_y, P.arm_z, a, w)


def mast():
    m = sq_tube_z(P.mast_z[0], P.mast_z[1], 0.0, P.mast_y, P.mast, P.mast_wall)
    cap = box_span((-P.mast / 2.0, P.mast / 2.0), (P.mast_y - P.mast / 2.0, P.mast_y + P.mast / 2.0),
                   (P.mast_z[1], P.mast_z[1] + 4.0))
    g = P.mast_gusset
    y0 = P.mast_y + P.mast / 2.0
    tri = [V(-4.0, y0, P.mast_z[0]), V(-4.0, y0 + g, P.mast_z[0]), V(-4.0, y0, P.mast_z[0] + g)]
    gus = [Part.Face(Part.makePolygon(tri + [tri[0]])).extrude(V(8.0, 0, 0))]
    return fuse_all([m, cap] + gus)


# ---------------------------------------------------------------------
# Fan pods (right side)
# ---------------------------------------------------------------------
def _ax(d, x0, x1, z, y=None):
    return cyl_x(d, x0, x1, P.mast_y if y is None else y, z)


def shroud_right(z):
    do, di = P.shroud_d
    x0, x1 = P.pod_x
    s = _ax(do, x0, x1, z).cut(_ax(di, x0 - 1, x1 + 1, z))
    lip = _ax(do + 30.0, x0, x0 + 6.0, z).cut(_ax(di, x0 - 1, x0 + 7, z))     # intake bell / flange
    return fuse_all([s, lip])


def bars_right(z):
    """2 flat bars from the mast side face along x, above and below the shroud."""
    t, w = P.bar
    ro = P.shroud_d[0] / 2.0
    x0, x1 = P.mast / 2.0, P.pod_x[0] + 0.6 * (P.pod_x[1] - P.pod_x[0])
    y = (P.mast_y - w / 2.0, P.mast_y + w / 2.0)
    return Part.makeCompound([box_span((x0, x1), y, (z + ro, z + ro + t)), box_span((x0, x1), y, (z - ro - t, z - ro))])


def guard_right(z):
    """Intake guard: outer ring, inner ring and a cross, 3 mm."""
    x0 = P.pod_x[0] - P.guard_t
    r = P.shroud_d[1] / 2.0
    ring = _ax(2 * r, x0, P.pod_x[0], z).cut(_ax(2 * r - 16.0, x0 - 1, P.pod_x[0] + 1, z))
    ring2 = _ax(170.0, x0, P.pod_x[0], z).cut(_ax(154.0, x0 - 1, P.pod_x[0] + 1, z))
    bars = [box_span((x0, P.pod_x[0]), (P.mast_y - 5.0, P.mast_y + 5.0), (z - r + 4, z + r - 4)),
            box_span((x0, P.pod_x[0]), (P.mast_y - r + 4, P.mast_y + r - 4), (z - 5.0, z + 5.0))]
    return fuse_all([ring, ring2] + bars)


def motor_right(z):
    d, x0, x1 = P.motor
    body = _ax(d, x0, x1, z)
    r_in = P.shroud_d[1] / 2.0
    spokes = []
    for k in range(3):
        a = math.radians(90.0 + 120.0 * k)
        sp = box_span((x1 - 30.0, x1 - 10.0), (-4.0, 4.0), (d / 2.0 - 5.0, r_in))
        sp.rotate(V(0, 0, 0), V(1, 0, 0), math.degrees(a) - 90.0)
        sp.translate(V(0, P.mast_y, z))
        spokes.append(sp)
    return fuse_all([body] + spokes)


def rotor_right(z):
    x0, x1 = P.rotor_x
    hub = _ax(P.hub_d, x0 - 5.0, x1 + 5.0, z)
    shaft = _ax(20.0, x1 + 5.0, P.motor[1], z)
    tip = P.fan_d / 2.0 - 5.0
    bl = []
    for k in range(P.blades):
        b = box_span((-1.5, 1.5), (-P.blade_w / 2.0, P.blade_w / 2.0), (P.hub_d / 2.0 - 5.0, tip))
        b.rotate(V(0, 0, 0), V(0, 0, 1), P.blade_pitch)
        b.rotate(V(0, 0, 0), V(1, 0, 0), 360.0 / P.blades * k)
        b.translate(V(0.5 * (x0 + x1), P.mast_y, z))
        bl.append(b)
    return fuse_all([hub, shaft] + bl)


def nozzle_ring_right(z):
    ring = Part.makeTorus(P.ring_r, P.ring_d / 2.0, V(P.ring_x, P.mast_y, z), V(1, 0, 0))
    noz = [cyl_x(P.nozzle[0], P.ring_x - 5.0, P.ring_x + P.nozzle[1], P.mast_y, z + dz) for dz in (P.ring_r, -P.ring_r)]
    return fuse_all([ring] + noz)


def ring_tabs_right(z):
    """2 small tabs from the shroud end to the nozzle ring."""
    out = []
    for dy in (1, -1):
        y = P.mast_y + dy * P.ring_r
        out.append(box_span((P.pod_x[1] - 15.0, P.ring_x - P.ring_d / 2.0 + 0.5), (y - 6.0, y + 6.0), (z - 3.0, z + 3.0)))
    return Part.makeCompound(out)


def section_line_right(z):
    """Section line from the manifold up the mast rear (y -930), outward under the pod and up into the ring bottom."""
    x = P.line_x[z]
    zr = z - P.line_drop
    pts = [(x, P.line_y, P.manifold[2][1]), (x, P.line_y, zr), (P.ring_x, P.line_y, zr), (P.ring_x, P.mast_y, zr),
           (P.ring_x, P.mast_y, z - P.ring_r - P.ring_d / 2.0 + 1.0)]
    return hose(pts, od=P.line_d)


def pods(fn):
    """Both sides, all heights, for one pod part function."""
    shapes = [fn(z) for z in P.pod_z]
    right = Part.makeCompound(shapes)
    return Part.makeCompound([right, mirror_x(right)])


# ---------------------------------------------------------------------
# Liquid
# ---------------------------------------------------------------------
def manifold():
    (x0, x1), (y0, y1), (z0, z1) = P.manifold
    body = box_span((x0, x1), (y0, y1), (z0, z1))
    valves = [box_span((x - 9.0, x + 9.0), (y0 - 30.0, y0), (z0 + 10.0, z1 - 10.0)) for x in (-36.0, -24.0, -12.0, 12.0, 24.0, 36.0)]
    brk = box_span((-30.0, 30.0), (y1, P.cross_y[0]), (z0 + 10.0, z1 - 10.0))     # to the cross beam rear face
    return fuse_all([body, brk] + valves)


def pressure_hose():
    """From the spot sprayer regulator (x 90, y -475) down under the arms to the manifold bottom."""
    import ssp_params as SP
    y_m = 0.5 * (P.manifold[1][0] + P.manifold[1][1])
    return hose([(SP.feed_x, -475.0, SP.regulator[2][0]), (SP.feed_x, -475.0, P.hose_z), (SP.feed_x, y_m, P.hose_z),
                 (0.0, y_m, P.hose_z), (0.0, y_m, P.manifold[2][0])])


# ---------------------------------------------------------------------
# Lidar
# ---------------------------------------------------------------------
def lidar_arm():
    z = (P.lidar_arm_z - 20.0, P.lidar_arm_z + 20.0)
    return sq_tube_y(P.lidar_arm_y[0], P.lidar_arm_y[1], 0.0, z, 40.0, 40.0, 3.0)


def lidars():
    """2D lidar per side, scan plane vertical (x-z), looking outward; a plate across the arm end."""
    lx, ly, lz = P.lidar
    y = P.lidar_y
    plate = box_span((-2 * lx - 10.0, 2 * lx + 10.0), (y[0], y[0] + 6.0), (P.lidar_arm_z - lz / 2.0, P.lidar_arm_z + lz / 2.0))
    out = [plate]
    for s in SIDES:
        x0 = s * 10.0
        body = box_span((x0, x0 + s * lx), (y[0] + 6.0, y[1]), (P.lidar_arm_z - lz / 2.0, P.lidar_arm_z + lz / 2.0))
        win = cyl_x(50.0, x0 + s * lx, x0 + s * (lx + 6.0), 0.5 * (y[0] + y[1]) + 3.0, P.lidar_arm_z)
        out.append(fuse_all([body, win]))
    return Part.makeCompound(out)
