"""One function per part of the mobile refiller, simple (IBC), and the receiver kit for the working robot.

Every shape is drawn in robot coordinates (x right, y forward, z up, ground z 0, mm).
- Arm parts are drawn with the arm out (pointing left, -x); the MRS_arm part in build_mrs rotates them about the mast.
- Receiver-kit parts are drawn in the coordinates of the working robot.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import mrs_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

MX, MY = P.mast_xy
NX, NY = P.NOZZLE_XY


# ---------------------------------------------------------------------
# Basic shapes (same style as mrl_parts.py)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    x0, x1 = sorted(x)
    y0, y1 = sorted(y)
    z0, z1 = sorted(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_y(d, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def tube_z(od, wall, z0, z1, x, y):
    return cyl_z(od, z0, z1, x, y).cut(cyl_z(od - 2 * wall, z0 - 1, z1 + 1, x, y))


def fuse_all(shapes):
    shapes = [s for s in shapes if s is not None]
    result = shapes[0]
    if len(shapes) > 1:
        result = result.fuse(shapes[1:])
    try:
        result = result.removeSplitter()
    except Exception:
        pass
    return result


def _poly(pts):
    pts = list(pts)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


def poly_xz(points, y0, t):
    """Closed polygon in the x-z plane, (x, z), extruded over +y from y0."""
    return _poly([V(x, y0, z) for (x, z) in points]).extrude(V(0, t, 0))


def rbox(x, y, z, r):
    """Box with rounded vertical edges."""
    b = box_span(x, y, z)
    if r <= 0:
        return b
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    return b.makeFillet(r, edges)


def rtube(x, y, z, t, axis):
    """Rectangular tube (wall t) filling the box x, y, z, open along 'axis' ('x', 'y' or 'z')."""
    outer = box_span(x, y, z)
    ix = (min(x) - 1, max(x) + 1) if axis == "x" else (min(x) + t, max(x) - t)
    iy = (min(y) - 1, max(y) + 1) if axis == "y" else (min(y) + t, max(y) - t)
    iz = (min(z) - 1, max(z) + 1) if axis == "z" else (min(z) + t, max(z) - t)
    return outer.cut(box_span(ix, iy, iz))


def hose(points, od=P.hose_od):
    """Hose / pipe along a polyline, with a ball at every bend."""
    pts = [V(*p) for p in points]
    parts = [Part.makeCylinder(od / 2.0, (b - a).Length, a, b - a) for a, b in zip(pts[:-1], pts[1:])
             if (b - a).Length > 1e-6]
    parts += [Part.makeSphere(od / 2.0, p) for p in pts[1:-1]]
    return fuse_all(parts)


def hex_prism(x, y, z0, af, k):
    pts = [V(x + af / math.sqrt(3) * math.cos(math.radians(a)), y + af / math.sqrt(3) * math.sin(math.radians(a)), z0)
           for a in range(0, 361, 60)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, k))


def bolt_down(x, y, z_head, length, d=10.0, af=17.0, k=6.4):
    """Hex bolt with the underside of the head at z_head, shank down."""
    return fuse_all([hex_prism(x, y, z_head, af, k), cyl_z(d, z_head - length, z_head, x, y)])


# Tank volume: same rounded-rectangle sections as the shapes
from mrs_calc import tank_sections  # noqa: E402,F401


# ---------------------------------------------------------------------
# Bed: welded frame of 60 x 40 x 3 tube lying flat on the upper beams
# ---------------------------------------------------------------------
BED_W, BED_H, BED_T = P.bed_tube


def bed_cross_tubes():
    """3 bolted cross tubes (bolt hole in the bottom wall, access hole in the top wall) and the welded one at y 0
    that runs out under the mast."""
    z0, z1 = P.bed_z
    out = []
    for y in P.bed_cross_y:
        tube = rtube((-P.bed_cross_x, P.bed_cross_x), (y - BED_W / 2.0, y + BED_W / 2.0), P.bed_z, BED_T, "x")
        holes = []
        for x in P.bed_bolt_x:
            holes.append(cyl_z(P.m10_hole, z0 - 1.0, z0 + BED_T + 1.0, x, y))
            holes.append(cyl_z(22.0, z1 - BED_T - 1.0, z1 + 1.0, x, y))
        out.append(tube.cut(holes))
    y = P.bed_mast_y
    out.append(rtube((-P.bed_cross_x, P.bed_cross_x), (y - BED_W / 2.0, y + BED_W / 2.0), P.bed_z, BED_T, "x"))
    return Part.makeCompound(out)


def bed_side_rails():
    out = []
    for s in (-1, 1):
        out.append(rtube((s * P.bed_side_x[0], s * P.bed_side_x[1]), P.bed_y, P.bed_z, BED_T, "y"))
    return Part.makeCompound(out)


def mast_outrigger():
    """80 x 40 x 3 stub from the left side rail out under the mast, with a hole for the hose in both walls."""
    m = P.mast_tube[0]
    stub = rtube(P.outrigger_x, (MY - m / 2.0, MY + m / 2.0), P.bed_z, BED_T, "x")
    return stub.cut(cyl_z(56.0, P.bed_z[0] - 1.0, P.bed_z[1] + 1.0, MX, MY))


def mast_gussets():
    """Two plates on the sides of the stub and the mast, welded to the side rail."""
    pts = [(-P.bed_side_x[1], P.bed_z[0]), (P.outrigger_x[1], P.bed_z[0]),
           (P.outrigger_x[1], P.bed_z[1] + P.gusset_h), (-P.bed_side_x[1], P.bed_z[1] + 40.0)]
    m = P.mast_tube[0] / 2.0
    return Part.makeCompound([poly_xz(pts, MY + m, P.gusset_t), poly_xz(pts, MY - m - P.gusset_t, P.gusset_t)])


def bed_bolts():
    """M10 x 55 with the head inside the cross tube on the bottom wall, through the upper beam, nut under the beam."""
    z_head = P.bed_z[0] + BED_T
    z_nut = P.robot_upper_beam_z[0]
    out = []
    for y in P.bed_cross_y:
        for x in P.bed_bolt_x:
            out.append(bolt_down(x, y, z_head, z_head - z_nut + 8.4 + 3.0))
            out.append(cyl_z(17.0, z_nut - 8.4, z_nut, x, y))
    return Part.makeCompound(out)


def corner_guides():
    """Angle 50 x 5, 140 high, outside the four pallet corners, on the ends of the side rails."""
    leg, t, h = P.guide
    z = (P.bed_z[1], P.bed_z[1] + h)
    out = []
    for sx in (-1, 1):
        for sy, ye in ((-1, P.ibc_y[0]), (1, P.ibc_y[1])):
            a = box_span((sx * (P.ibc_x - leg), sx * (P.ibc_x + t)), (ye, ye + sy * t), z)
            b = box_span((sx * P.ibc_x, sx * (P.ibc_x + t)), (ye - sy * leg, ye + sy * t), z)
            out.append(fuse_all([a, b]))
    return Part.makeCompound(out)


def lashing_eyes():
    ln, t, h = P.lash_eye
    z0 = P.bed_z[0] + 5.0
    out = []
    for s in (-1, 1):
        for y in P.strap_y:
            plate = box_span((s * P.bed_side_x[1], s * (P.bed_side_x[1] + t)), (y - ln / 2.0, y + ln / 2.0), (z0, z0 + 30.0))
            out.append(plate.cut(cyl_x(h, s * P.bed_side_x[1] - 1, s * (P.bed_side_x[1] + t) + 1, y, z0 + 15.0)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Mast (fixed) and the pivot on top
# ---------------------------------------------------------------------
def mast():
    m, t = P.mast_tube
    tube = rtube((MX - m / 2.0, MX + m / 2.0), (MY - m / 2.0, MY + m / 2.0), P.mast_z, t, "z")
    w, z0, z1 = P.mast_window
    window = box_span((MX - m / 2.0 - 1.0, MX - m / 2.0 + t + 1.0), (MY - w / 2.0, MY + w / 2.0), (z0, z1))
    return tube.cut(window)


TOP_Z = (P.mast_z[1], P.mast_z[1] + P.mast_top_plate[1])


def lock_holes():
    """Lock-pin holes in the top plate: arm out (0 deg) and folded (arm_fold)."""
    out = []
    for a in (0.0, P.arm_fold):
        r = math.radians(a)
        out.append((MX - P.lock_r * math.sin(r), MY + P.lock_r * math.cos(r)))
    return out


def mast_top_plate():
    s = P.mast_top_plate[0] / 2.0
    plate = box_span((MX - s, MX + s), (MY - s, MY + s), TOP_Z)
    holes = [cyl_z(13.0, TOP_Z[0] - 1, TOP_Z[1] + 1, x, y) for x, y in lock_holes()]
    holes.append(cyl_z(P.pivot_pin[0], TOP_Z[0] - 1, TOP_Z[1] + 1, MX, MY))     # pin welded in
    return plate.cut(holes)


def pivot_pin():
    d, ln = P.pivot_pin
    pin = cyl_z(d, TOP_Z[0], TOP_Z[1] + ln, MX, MY)
    washer = cyl_z(44.0, SLEEVE_Z[1], SLEEVE_Z[1] + 4.0, MX, MY)
    clip = cyl_y(4.0, MY - 22.0, MY + 22.0, MX, SLEEVE_Z[1] + 12.0)
    return fuse_all([pin, washer, clip])


# ---------------------------------------------------------------------
# Arm (rotates about the mast axis; drawn out, pointing left)
# ---------------------------------------------------------------------
SLEEVE_Z = (TOP_Z[1], TOP_Z[1] + 70.0)
TIP_X = NX - P.arm_tip


def arm():
    """60 x 60 x 3 arm welded to a boss on the pivot pin, with the lock-pin tab."""
    b, t = P.arm_tube
    boss = cyl_z(P.arm_sleeve[0], SLEEVE_Z[0], SLEEVE_Z[1], MX, MY).cut(
        cyl_z(P.pivot_pin[0] + 1.0, SLEEVE_Z[0] - 1, SLEEVE_Z[1] + 1, MX, MY))
    x_root = MX - math.sqrt((P.arm_sleeve[0] / 2.0) ** 2 - (b / 2.0) ** 2) + 2.0
    tube = rtube((x_root, TIP_X), (MY - b / 2.0, MY + b / 2.0), P.arm_z, t, "x")
    cap = box_span((TIP_X, TIP_X + t), (MY - b / 2.0, MY + b / 2.0), P.arm_z)
    lx, ly = lock_holes()[0]
    tab = box_span((lx - 15.0, lx + 15.0), (MY + P.arm_sleeve[0] / 2.0 - 3.0, ly + 15.0), (SLEEVE_Z[0], SLEEVE_Z[0] + 8.0))
    return fuse_all([boss, tube, cap, tab]).cut(cyl_z(13.0, SLEEVE_Z[0] - 1, SLEEVE_Z[0] + 9, lx, ly))


def lock_pin():
    lx, ly = lock_holes()[0]
    return fuse_all([cyl_z(12.0, TOP_Z[0] - 20.0, SLEEVE_Z[0] + 25.0, lx, ly),
                     cyl_x(10.0, lx - 20.0, lx + 20.0, ly, SLEEVE_Z[0] + 25.0)])


def tip_plate():
    return box_span((TIP_X, NX + 40.0), (NY - 40.0, NY + 40.0), (P.drop_top, P.arm_z[0]))


def drop_pipe():
    """PP pipe 50 hanging under the arm tip, flange on top, side inlet for the hose."""
    d, w = P.drop_pipe
    z0 = P.nozzle_tip_z + P.nozzle[1] + P.nozzle[2]
    pipe = tube_z(d, w, z0, P.drop_top, NX, NY)
    flange = cyl_z(80.0, P.drop_top - 8.0, P.drop_top, NX, NY).cut(cyl_z(d - 2 * w, 0, 3000, NX, NY))
    inlet = cyl_y(40.0, NY + d / 2.0 - 3.0, NY + 60.0, NX, P.inlet_z).cut(cyl_z(d - 2 * w, 0, 3000, NX, NY))
    return fuse_all([pipe, flange, inlet])


def nozzle():
    """Drip-stop valve (spring check valve, opens at ~0.3 bar) and a short cone."""
    d, h, c = P.nozzle
    z0 = P.nozzle_tip_z
    body = cyl_z(d, z0 + c, z0 + c + h, NX, NY)
    cone = Part.makeCone(12.5, 20.0, c, V(NX, NY, z0), Z)
    return fuse_all([body, cone])


def antenna():
    """RTK antenna straight above the nozzle (the robot's own antenna, moved here)."""
    z0 = P.arm_z[1]
    stem = cyl_z(P.ant_stem[0], z0, z0 + P.ant_stem[1], NX, NY)
    z1 = z0 + P.ant_stem[1]
    dome = cyl_z(P.ant_dome[0], z1, z1 + P.ant_dome[1] * 0.6, NX, NY)
    top = Part.makeSphere(P.ant_dome[0] / 2.0, V(NX, NY, z1 + P.ant_dome[1] * 0.6)).common(
        box_span((NX - 80, NX + 80), (NY - 80, NY + 80), (z1 + P.ant_dome[1] * 0.6, z1 + P.ant_dome[1])))
    return fuse_all([stem, dome, top])


ANT_TOP = P.arm_z[1] + P.ant_stem[1] + P.ant_dome[1]
WINDOW_OUT = (MX - P.mast_tube[0] / 2.0 - 45.0, MY, 0.5 * (P.mast_window[1] + P.mast_window[2]))


def arm_hose():
    """From the window in the mast (flexible loop over the pivot) along the arm to the side inlet of the drop pipe."""
    hy = MY + P.arm_tube[0] / 2.0 + P.hose_od / 2.0 + 8.0
    hz = 0.5 * (P.arm_z[0] + P.arm_z[1])
    pts = [WINDOW_OUT, (WINDOW_OUT[0] - 15.0, hy, WINDOW_OUT[2] + 30.0), (WINDOW_OUT[0] - 55.0, hy, hz),
           (NX + 80.0, hy, hz), (NX, hy + 20.0, P.inlet_z + 45.0), (NX, hy + 20.0, P.inlet_z),
           (NX, NY + 58.0, P.inlet_z)]
    return hose(pts)


# ---------------------------------------------------------------------
# IBC (bought): pallet, bottle, cage, valve, cap
# ---------------------------------------------------------------------
Z0 = P.IBC_Z0
BOTTLE_Z = (Z0 + P.pallet_h, Z0 + P.pallet_h + P.bottle_h)
VALVE_Z = Z0 + P.valve_z
VALVE_X1 = -P.bottle_x - P.valve_body[1]                 # end of the valve body
SPIGOT_X1 = VALVE_X1 - P.valve_spigot[1]                 # end of the spigot


def pallet():
    """4-way-entry skid pallet: deck, 3 x 3 feet, 3 runners."""
    rw, rh = P.pallet_runner
    deck_z = (Z0 + P.pallet_h - P.pallet_deck_t, Z0 + P.pallet_h)
    parts = [box_span((-P.ibc_x, P.ibc_x), P.ibc_y, deck_z)]
    f = P.pallet_foot
    for x in (-P.ibc_x + f / 2.0, 0.0, P.ibc_x - f / 2.0):
        for y in (P.ibc_y[0] + f / 2.0, P.IBC_CY, P.ibc_y[1] - f / 2.0):
            parts.append(box_span((x - f / 2.0, x + f / 2.0), (y - f / 2.0, y + f / 2.0), (Z0 + rh, deck_z[0])))
    for y in P.pallet_runner_y:
        parts.append(box_span((-P.ibc_x, P.ibc_x), (y - rw / 2.0, y + rw / 2.0), (Z0, Z0 + rh)))
    return Part.makeCompound(parts)


def _bottle(inset):
    i = inset
    return rbox((-P.bottle_x + i, P.bottle_x - i), (P.bottle_y[0] + i, P.bottle_y[1] - i),
                (BOTTLE_Z[0] + i, BOTTLE_Z[1] - i), P.bottle_r - i)


def bottle_inner():
    return _bottle(P.bottle_wall)


def bottle():
    shell = _bottle(0.0).cut(bottle_inner())
    neck = tube_z(170.0, 4.0, BOTTLE_Z[1] - 5.0, BOTTLE_Z[1] + 10.0, P.ibc_cap[0], P.ibc_cap[1])
    return fuse_all([shell, neck])


def cage():
    """Galvanised tube grid: rings, vertical bars, top frame and top bars (open around the valve)."""
    d = P.cage_bar
    cx, (y0, y1) = P.cage_x, P.cage_y
    zb, zt = BOTTLE_Z[0], Z0 + P.cage_top
    bars = []
    for zr in list(P.cage_rings) + [P.cage_top]:
        z = Z0 + zr
        bars.append(cyl_x(d, -cx, cx, y0, z))
        bars.append(cyl_x(d, -cx, cx, y1, z))
        bars.append(cyl_y(d, y0, y1, cx, z))
        if abs(z - VALVE_Z) < P.valve_body[0] / 2.0 + d:
            bars.append(cyl_y(d, y0, P.IBC_CY - P.valve_gap, -cx, z))
            bars.append(cyl_y(d, P.IBC_CY + P.valve_gap, y1, -cx, z))
        else:
            bars.append(cyl_y(d, y0, y1, -cx, z))
    n1, n2 = P.cage_n
    for i in range(n1):
        x = -cx + 2.0 * cx * i / (n1 - 1)
        for y in (y0, y1):
            bars.append(cyl_z(d, zb, zt, x, y))
    for j in range(1, n2 - 1):
        y = y0 + (y1 - y0) * j / (n2 - 1)
        for x in (-cx, cx):
            bars.append(cyl_z(d, zb, zt, x, y))
    for y in P.strap_y:
        bars.append(cyl_x(d, -cx, cx, y, zt))
    for x in (-300.0, 300.0):
        bars.append(cyl_y(d, y0, y1, x, zt))
    return Part.makeCompound(bars)


def ibc_valve():
    """DN50 butterfly valve on the left face, S60x6 spigot, lever (pointing back)."""
    y, z = P.IBC_CY, VALVE_Z
    body = cyl_x(P.valve_body[0], -P.bottle_x, VALVE_X1, y, z)
    spigot = cyl_x(P.valve_spigot[0], VALVE_X1, SPIGOT_X1, y, z)
    xl = VALVE_X1 + 12.0
    stem = cyl_z(16.0, z + P.valve_body[0] / 2.0 - 5.0, z + P.valve_body[0] / 2.0 + 18.0, xl, y)
    lever = box_span((xl - 8.0, xl + 8.0), (y - 140.0, y + 10.0), (z + P.valve_body[0] / 2.0 + 12.0,
                                                                  z + P.valve_body[0] / 2.0 + 24.0))
    return fuse_all([body, spigot, stem, lever])


def ibc_cap():
    x, y, d, h = P.ibc_cap
    z = BOTTLE_Z[1] + 10.0
    lid = cyl_z(d, z, z + h - 10.0, x, y)
    grip = box_span((x - d / 2.0 + 15, x + d / 2.0 - 15), (y - 8, y + 8), (z + h - 10.0, z + h))
    return fuse_all([lid, grip])


# ---------------------------------------------------------------------
# Ratchet straps
# ---------------------------------------------------------------------
STRAP_X = P.cage_x + P.cage_bar / 2.0 + 1.0                # 601


def straps():
    t, w = P.strap_t, P.strap_w
    zt = Z0 + P.cage_top + P.cage_bar / 2.0
    out = []
    for y in P.strap_y:
        yy = (y - w / 2.0, y + w / 2.0)
        parts = [box_span((-STRAP_X - t, STRAP_X + t), yy, (zt, zt + t))]
        for s in (-1, 1):
            parts.append(box_span((s * STRAP_X, s * (STRAP_X + t)), yy, (P.bed_z[1] + 12.0, zt + t)))
        out.append(fuse_all(parts))
    return Part.makeCompound(out)


def ratchets():
    rx, rz, ry = P.ratchet
    return Part.makeCompound([box_span((STRAP_X + P.strap_t, STRAP_X + P.strap_t + rx), (y - ry / 2.0, y + ry / 2.0),
                                       (1150.0, 1150.0 + rz)) for y in P.strap_y])


# ---------------------------------------------------------------------
# Pump (inside the frame, under the IBC) and hoses
# ---------------------------------------------------------------------
PY, PZ = P.pump_axis
PUMP_IN = (P.pump_inlet[1], PY, PZ)
PUMP_OUT = (P.pump_outlet_x, PY, PZ + P.pump_head[0] / 2.0 + 15.0)
ELBOW_X = SPIGOT_X1 - 27.0


def pump_body():
    motor = cyl_x(P.pump_motor[0], P.pump_motor[1], P.pump_motor[2], PY, PZ)
    fins = cyl_x(P.pump_motor[0] + 8.0, P.pump_motor[1] + 30.0, P.pump_motor[2] - 30.0, PY, PZ).cut(motor)
    head = cyl_x(P.pump_head[0], P.pump_head[1], P.pump_head[2], PY, PZ)
    inlet = cyl_x(P.pump_inlet[0], P.pump_inlet[1], P.pump_inlet[2] + 5.0, PY, PZ)
    outlet = cyl_z(P.pump_inlet[0], PZ, PUMP_OUT[2], P.pump_outlet_x, PY)
    box = box_span((-120.0, -40.0), (PY - 35.0, PY + 35.0), (PZ + 45.0, PZ + 70.0))
    return fuse_all([motor, fins, head, inlet, outlet, box])


CRADLE_Y = (P.bed_cross_y[1] + 9.0, P.bed_mast_y - 9.0)     # hangers under the cross tubes at y -275 and 0


def pump_cradle():
    fz = P.pump_floor_z
    floor = box_span((P.pump_head[1] - 10.0, P.pump_motor[2] + 10.0), (CRADLE_Y[0] - 6.0, CRADLE_Y[1] + 6.0), fz)
    hangers = [box_span(P.pump_hanger_x, (y - 3.0, y + 3.0), (fz[1], P.bed_z[0])) for y in CRADLE_Y]
    foot_m = box_span((-140.0, -40.0), (PY - 35.0, PY + 35.0), (fz[1], PZ - P.pump_motor[0] / 2.0 - 4.0))
    foot_h = box_span((-245.0, -195.0), (PY - 40.0, PY + 40.0), (fz[1], PZ - P.pump_head[0] / 2.0))
    return fuse_all([floor] + hangers + [foot_m, foot_h])


def camlock_elbow():
    """Camlock coupler on the valve spigot with a 90 degree elbow down."""
    y, z = P.IBC_CY, VALVE_Z
    return fuse_all([cyl_x(62.0, SPIGOT_X1 + 10.0, ELBOW_X, y, z), Part.makeSphere(31.0, V(ELBOW_X, y, z)),
                     cyl_z(62.0, z - 50.0, z, ELBOW_X, y)])


def suction_hose():
    """IBC valve -> down outside the bed -> under the beams -> pump inlet."""
    y, z = P.IBC_CY, VALVE_Z
    pts = [(ELBOW_X, y, z - 45.0), (ELBOW_X, y, 600.0), (-330.0, y, PZ), (PUMP_IN[0] + 5.0, y, PZ)]
    return hose(pts)


HOSE_UNDER_Z = P.robot_upper_beam_z[0] - P.hose_od / 2.0 - 7.0      # under the upper beams


def discharge_hose():
    """Pump -> under the beams -> up inside the mast -> out of the window at the top."""
    x, y, z = PUMP_OUT
    pts = [(x, y, z - 5.0), (x, y, HOSE_UNDER_Z), (x, MY, HOSE_UNDER_Z), (MX, MY, HOSE_UNDER_Z),
           (MX, MY, WINDOW_OUT[2]), WINDOW_OUT]
    return hose(pts)


# ---------------------------------------------------------------------
# Receiver kit on the working robot (as the liquid variant, without the camera target)
# ---------------------------------------------------------------------
def cradle_tubes(ys=P.cradle_y, half=P.cradle_half_len):
    t, w = P.cradle_tube, P.cradle_wall
    out = []
    for y in ys:
        outer = box_span((-half, half), (y - t / 2, y + t / 2), P.cradle_z)
        inner = box_span((-half - 1, half + 1), (y - t / 2 + w, y + t / 2 - w), (P.cradle_z[0] + w, P.cradle_z[1] - w))
        holes = [cyl_z(P.m10_hole, P.cradle_z[0] - 1, P.cradle_z[1] + 1, x, y) for x in P.robot_upper_beam_x[1:3]]
        out.append(outer.cut(inner).cut(holes))
    return Part.makeCompound(out)


def cradle_pads(ys=P.cradle_y, half_x=300.0):
    return Part.makeCompound([box_span((-half_x, half_x), (y - 18.0, y + 18.0), (P.cradle_z[1], P.tank_z0))
                              for y in ys])


def cradle_bolts(ys=P.cradle_y):
    out = []
    for y in ys:
        for x in P.robot_upper_beam_x[1:3]:
            out.append(bolt_down(x, y, P.cradle_z[1], P.cradle_tube + P.robot_beam + 14.0, k=4.0))
            out.append(cyl_z(17.0, P.robot_upper_beam_z[0] - 8.4, P.robot_upper_beam_z[0], x, y))
    return Part.makeCompound(out)


RX_TOP = P.tank_z0 + P.rx_tank_h


def rx_straps(ys=P.cradle_y):
    t, w, hx = P.strap_t_rx, P.strap_w_rx, P.rx_tank_x
    out = []
    for y in ys:
        yy = (y - w / 2.0, y + w / 2.0)
        parts = [box_span((-hx - t, hx + t), yy, (RX_TOP, RX_TOP + t))]
        for s in (-1, 1):
            parts.append(box_span((s * hx, s * (hx + t)), yy, (P.cradle_z[1], RX_TOP + t)))
            parts.append(box_span((s * (hx + t), s * (hx + t + 22.0)), yy, (P.cradle_z[1], P.cradle_z[1] + t)))
        out.append(fuse_all(parts))
    return Part.makeCompound(out)


def rx_tank_inner():
    w = P.tank_wall
    return rbox((-P.rx_tank_x + w, P.rx_tank_x - w), (P.rx_tank_y[0] + w, P.rx_tank_y[1] - w),
                (P.tank_z0 + w, RX_TOP - w), P.rx_tank_r - w)


def rx_tank_shell():
    return rbox((-P.rx_tank_x, P.rx_tank_x), P.rx_tank_y, (P.tank_z0, RX_TOP), P.rx_tank_r).cut(rx_tank_inner())


def funnel():
    x, y = P.funnel_xy
    z0 = RX_TOP + P.funnel_neck
    d0, d1 = P.funnel_d
    w = P.funnel_wall
    outer = Part.makeCone(d1 / 2.0, d0 / 2.0, P.funnel_h, V(x, y, z0), Z)
    inner = Part.makeCone(d1 / 2.0 - w, d0 / 2.0 - w, P.funnel_h + 0.01, V(x, y, z0 + 0.01), Z)
    neck = tube_z(d1, w, RX_TOP, z0 + 0.5, x, y)
    flange = cyl_z(d1 + 50.0, RX_TOP, RX_TOP + 6.0, x, y).cut(cyl_z(d1 - 2 * w, RX_TOP - 1, RX_TOP + 7, x, y))
    rim = cyl_z(d0 + 10.0, z0 + P.funnel_h - 8.0, z0 + P.funnel_h, x, y).cut(
        cyl_z(d0 - 2 * w, z0 + P.funnel_h - 9.0, z0 + P.funnel_h + 1.0, x, y))
    return fuse_all([outer.cut(inner), neck, flange, rim])


def strainer():
    x, y = P.funnel_xy
    z = RX_TOP + P.funnel_neck + 10.0
    return cyl_z(P.funnel_d[1] + 18.0, z, z + 2.0, x, y)


def level_sensor(x, y, d, h, z0):
    return fuse_all([cyl_z(d + 20.0, z0, z0 + 12.0, x, y), cyl_z(d, z0 + 12.0, z0 + h, x, y),
                     cyl_z(16.0, z0 + h, z0 + h + 20.0, x, y)])


def rx_level_sensor():
    return level_sensor(*P.rx_level_sensor, z0=RX_TOP)


def rx_vent():
    x, y, d, h = P.rx_vent
    return fuse_all([cyl_z(d, RX_TOP, RX_TOP + h, x, y), cyl_x(d, x, x + 40.0, y, RX_TOP + h - 10.0)])


# ---------------------------------------------------------------------
# Liquid, stream, ground marks
# ---------------------------------------------------------------------
def liquid(inner, level_z):
    bb = inner.BoundBox
    if level_z <= bb.ZMin + 0.5:
        return None
    cut = box_span((bb.XMin - 1, bb.XMax + 1), (bb.YMin - 1, bb.YMax + 1), (bb.ZMin - 1, min(level_z, bb.ZMax - 0.5)))
    return inner.common(cut)


def stream(x, y, z0, z1, d=22.0):
    """Liquid jet from the nozzle into the funnel."""
    return Part.makeCone(d / 2.0, d / 2.0 * 0.8, z0 - z1, V(x, y, z1), Z)


def ground_line(points, w=40.0, z=1.0, t=1.0):
    """Flat strip on the ground along a polyline (path markings in the images)."""
    out = []
    for (x0, y0), (x1, y1) in zip(points[:-1], points[1:]):
        ln = math.hypot(x1 - x0, y1 - y0)
        if ln < 1e-6:
            continue
        b = Part.makeBox(ln, w, t, V(0, -w / 2.0, z))
        b.rotate(V(0, 0, 0), Z, math.degrees(math.atan2(y1 - y0, x1 - x0)))
        b.translate(V(x0, y0, 0))
        out.append(b)
    return Part.makeCompound(out)
