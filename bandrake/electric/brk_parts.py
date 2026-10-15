"""Parts of the electric belt rake: one function per part, in robot coordinates, working position (comb mode, rake
down on its castors). The tine bars are built once at the bottom centre of the loop (bar_local) and placed along the
belt by build_brk (Placement from brk_calc.path). Crop / litter shapes for the renders are at the end."""
import math
import random

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import brk_params as P
import brk_calc as C

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)
DZ = P.drum_z
RY = P.rake_y
Y_RP = (P.side_y[0], P.side_y[0] + P.side_t)                    # rear side plate
Y_FP = (P.side_y[1], P.side_y[1] + P.side_t)                    # front side plate
Y_RR = (Y_RP[0] - P.rail[1], Y_RP[0])                           # rear rail
Y_FR = (Y_FP[1], Y_FP[1] + P.rail[1])                           # front rail
Y_RB = (Y_RR[0] - P.brg_plate[2], Y_RR[0])                      # rear bearing plate
Y_FB = (Y_FR[1], Y_FR[1] + P.brg_plate[2])                      # front bearing plate
Y_RBRG = (Y_RB[0] - P.bearing[1], Y_RB[0])                      # rear bearing
Y_FBRG = (Y_FB[1], Y_FB[1] + P.bearing[1])                      # front bearing


# ---------------------------------------------------------------------
# Basic shapes
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


def fuse_all(shapes):
    shapes = list(shapes)
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


def poly_xy(points, z0, t):
    return _poly([V(x, y, z0) for (x, y) in points]).extrude(V(0, 0, t))


def poly_yz(points, x0, t):
    return _poly([V(x0, y, z) for (y, z) in points]).extrude(V(t, 0, 0))


def tube_y(y0, y1, x, z, w, h, wall):
    o = box_span((x - w / 2, x + w / 2), (y0, y1), (z - h / 2, z + h / 2))
    i = box_span((x - w / 2 + wall, x + w / 2 - wall), (y0 - 1, y1 + 1), (z - h / 2 + wall, z + h / 2 - wall))
    return o.cut(i)


def tube_x(x0, x1, y, z, w, h, wall):
    """Rectangular tube along x: w along y, h along z."""
    o = box_span((x0, x1), (y - w / 2, y + w / 2), (z - h / 2, z + h / 2))
    i = box_span((x0 - 1, x1 + 1), (y - w / 2 + wall, y + w / 2 - wall), (z - h / 2 + wall, z + h / 2 - wall))
    return o.cut(i)


def tube_z(z0, z1, x, y, s, wall):
    o = box_span((x - s / 2, x + s / 2), (y - s / 2, y + s / 2), (z0, z1))
    i = box_span((x - s / 2 + wall, x + s / 2 - wall), (y - s / 2 + wall, y + s / 2 - wall), (z0 - 1, z1 + 1))
    return o.cut(i)


def hex_prism_z(af, z0, z1, x, y):
    r = af / math.sqrt(3.0)
    pts = [V(x + r * math.cos(math.radians(60 * i)), y + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    return _poly(pts).extrude(V(0, 0, z1 - z0))


def bolt_z(x, y, z_head, z_nut, d=10.0, af=17.0, k=6.4, m=8.4):
    head = hex_prism_z(af, z_head, z_head + k, x, y)
    shank = cyl_z(d, z_nut - m - 4.0, z_head, x, y)
    nut = hex_prism_z(af, z_nut - m, z_nut, x, y).cut(cyl_z(d, z_nut - m - 1, z_nut + 1, x, y))
    return fuse_all([head, shank, nut])


def pin_x(x0, x1, y, z, d=P.pin_d):
    return fuse_all([cyl_x(d, x0 - 4.0, x1 + 4.0, y, z), cyl_x(d + 10.0, x1 + 4.0, x1 + 8.0, y, z),
                     cyl_x(d + 8.0, x0 - 6.0, x0 - 4.0, y, z)])


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both_sides(shape):
    return Part.makeCompound([shape, mirror_x(shape)])


def stadium_xz(r, y0, t, cx=P.drum_x, cz=DZ):
    """Stadium (two circles of radius r around (+-cx, cz) and the box between) in the x-z plane, y0 .. y0 + t."""
    b = box_span((-cx, cx), (y0, y0 + t), (cz - r, cz + r))
    return fuse_all([b, cyl_y(2 * r, y0, y0 + t, -cx, cz), cyl_y(2 * r, y0, y0 + t, cx, cz)])


# ---------------------------------------------------------------------
# Rake frame: side plates (aluminium), side rails, bearing plates, cross tubes, roll stub
# ---------------------------------------------------------------------
def _frame_holes(y0, y1):
    holes = [cyl_y(P.drum_shaft_d + 2.0, y0 - 1, y1 + 1, sx * P.drum_x, DZ) for sx in (-1, 1)]
    return holes


def side_plates():
    out = []
    for (y0, y1) in (Y_RP, Y_FP):
        pl = stadium_xz(P.side_r, y0, P.side_t)
        pl = pl.cut(_frame_holes(y0, y1))
        out.append(pl)
    return Part.makeCompound(out)


def rails():
    out = []
    for (y0, y1) in (Y_RR, Y_FR):
        r = tube_x(-P.rail_x, P.rail_x, (y0 + y1) / 2.0, DZ, P.rail[1], P.rail[0], P.rail[2])
        if y0 == Y_RR[0]:
            r = r.cut(cyl_y(P.stub_d + 1.0, y0 - 1, y1 + 1, 0.0, DZ))
        out.append(r)
    return Part.makeCompound(out)


def bearing_plates():
    w, h, t = P.brg_plate
    out = []
    for (y0, y1) in (Y_RB, Y_FB):
        for sx in (-1, 1):
            pl = box_span((sx * P.drum_x - w / 2.0, sx * P.drum_x + w / 2.0), (y0, y1), (DZ - h / 2.0, DZ + h / 2.0))
            if sx < 0:      # tension side: slot for the shaft
                slot = box_span((-P.drum_x - P.tension_slot / 2.0, -P.drum_x + P.tension_slot / 2.0), (y0 - 1, y1 + 1),
                                (DZ - P.drum_shaft_d / 2.0 - 1, DZ + P.drum_shaft_d / 2.0 + 1))
                pl = pl.cut(slot)
            else:
                pl = pl.cut(cyl_y(P.drum_shaft_d + 2.0, y0 - 1, y1 + 1, P.drum_x, DZ))
            out.append(pl)
    # the bearing plates are welded to the rail ends: a web between rail end and plate centre line
    return Part.makeCompound(out)


def cross_tubes():
    out = []
    for x in P.cross_x:
        out.append(tube_y(Y_RP[0], Y_FP[1], x, DZ, P.cross_tube, P.cross_tube, P.cross_wall))
    return Part.makeCompound(out)


def stub():
    """Roll stub: round bar welded into the centre cross tube, out through the rear rail."""
    return cyl_y(P.stub_d, P.stub_end_y, Y_RP[1] + 40.0, 0.0, DZ)


def guide():
    """Bottom-run guide: steel flat with a UHMW strip, on two posts under the outer cross tubes."""
    L, w, h = P.guide
    z_top = DZ - P.drum_d / 2.0 + 0.0 + h                       # inside the loop, touching the belt from above
    z0 = DZ - P.drum_d / 2.0
    strip = box_span((-L / 2.0, L / 2.0), (RY - w / 2.0, RY + w / 2.0), (z0, z0 + 10.0))
    flat = box_span((-L / 2.0, L / 2.0), (RY - w / 2.0, RY + w / 2.0), (z0 + 10.0, z_top))
    posts = [box_span((x - 15.0, x + 15.0), (RY - 15.0, RY + 15.0), (z_top, DZ - P.cross_tube / 2.0)) for x in
             (P.cross_x[0], P.cross_x[2])]
    return strip, fuse_all([flat] + posts)


def guide_strip():
    return guide()[0]


def guide_flat():
    return guide()[1]


# ---------------------------------------------------------------------
# Drums, shafts, bearings, belt
# ---------------------------------------------------------------------
def drums():
    out = []
    y0, y1 = RY - P.drum_len / 2.0, RY + P.drum_len / 2.0
    for sx in (-1, 1):
        xc = sx * P.drum_x
        di = P.drum_d - 2 * P.drum_wall
        shell = cyl_y(P.drum_d, y0, y1, xc, DZ).cut(cyl_y(di, y0 - 1, y1 + 1, xc, DZ))
        discs = []
        for y in (y0 + 20.0, y1 - 20.0 - P.drum_disc):
            d = cyl_y(di, y, y + P.drum_disc, xc, DZ).cut(cyl_y(P.drum_shaft_d + 20.0, y - 1, y + P.drum_disc + 1, xc, DZ))
            d = d.fuse(cyl_y(P.drum_shaft_d + 20.0, y - 15.0, y + P.drum_disc + 15.0, xc, DZ))     # hub
            d = d.cut(cyl_y(P.drum_shaft_d, y - 16, y + P.drum_disc + 16, xc, DZ))
            for k in range(4):
                a = math.radians(45.0 + 90.0 * k)
                d = d.cut(cyl_y(55.0, y - 1, y + P.drum_disc + 1, xc + 58.0 * math.cos(a), DZ + 58.0 * math.sin(a)))
            discs.append(d)
        out.append(fuse_all([shell] + discs))
    return Part.makeCompound(out)


def shafts():
    out = []
    for sx in (-1, 1):
        y1 = Y_FBRG[1] + (60.0 if sx == P.drive_side else 10.0)        # drive shaft into the gearbox
        out.append(cyl_y(P.drum_shaft_d, Y_RBRG[0] - 10.0, y1, sx * P.drum_x, DZ))
    return Part.makeCompound(out)


def bearings():
    f, h, d = P.bearing
    out = []
    for (y0, y1) in (Y_RBRG, Y_FBRG):
        for sx in (-1, 1):
            x = sx * P.drum_x
            flange = box_span((x - f / 2.0, x + f / 2.0), (y0, y0 + 12.0) if y0 > RY else (y1 - 12.0, y1),
                              (DZ - f / 2.0, DZ + f / 2.0))
            house = cyl_y(d, y0, y1, x, DZ)
            out.append(fuse_all([flange, house]).cut(cyl_y(P.drum_shaft_d, y0 - 1, y1 + 1, x, DZ)))
    return Part.makeCompound(out)


def belt():
    y0, y1 = RY - P.belt_w / 2.0, RY + P.belt_w / 2.0
    ro = P.r_pitch + P.belt_t / 2.0
    ri = P.r_pitch - P.belt_t / 2.0
    return stadium_xz(ro, y0, P.belt_w).cut(stadium_xz(ri, y0 - 1, P.belt_w + 2))


def bar_local():
    """One tine bar with its tines, pitch point at the origin (x 0, z 0), belt normal pointing down (-z)."""
    zb = -P.belt_t / 2.0
    b, _, wall = P.bar
    bar = tube_y(RY - P.bar_len / 2.0, RY + P.bar_len / 2.0, 0.0, zb - b / 2.0, b, b, wall)
    bolts = [cyl_z(8.0, zb - b, P.belt_t / 2.0, 0.0, RY + dy) for dy in (-100.0, 100.0)]     # countersunk, flush
    legs, coils = [], []
    z_top = zb - b
    zc = z_top - P.tine_coil[0] / 2.0
    z_tip = zb - b - P.tine_len
    pairs = P.n_legs // 2
    for k in range(pairs):
        yc = RY + (k - (pairs - 1) / 2.0) * 2.0 * P.leg_pitch
        coils.append(cyl_y(P.tine_coil[0], yc - P.tine_coil[1] / 2.0, yc + P.tine_coil[1] / 2.0, 0.0, zc).cut(
            cyl_y(P.tine_coil[0] - 2 * P.tine_wire, yc - P.tine_coil[1], yc + P.tine_coil[1], 0.0, zc)))
        for s in (-1, 1):
            yl = yc + s * P.leg_pitch / 2.0
            legs.append(cyl_z(P.tine_wire, z_tip, zc, 0.0, yl))
            legs.append(cyl_y(P.tine_wire, min(yl, yc + s * P.tine_coil[1] / 2.0),
                              max(yl, yc + s * P.tine_coil[1] / 2.0), 0.0, zc - P.tine_coil[0] / 2.0 + P.tine_wire / 2))
    return bar, Part.makeCompound(bolts), Part.makeCompound(coils + legs)


def bar_placement(s, z0=DZ):
    """Placement of a bar at belt position s (mm along the loop)."""
    x, z, n = C.path(s, P.r_pitch, z0)
    nv = V(math.cos(math.radians(n)), 0, math.sin(math.radians(n)))
    rot = App.Rotation(V(0, 0, -1), nv)
    return App.Placement(V(x, 0, z), rot)


# ---------------------------------------------------------------------
# Drive
# ---------------------------------------------------------------------
def gearbox():
    gx, gz, gl = P.gear_box
    x = P.drive_side * P.drum_x
    y0 = Y_FBRG[1]
    house = box_span((x - gx / 2.0, x + gx / 2.0), (y0, y0 + gl), (DZ - gz / 2.0, DZ + gz / 2.0))
    edges = [e for e in house.Edges if abs(e.Vertexes[0].Point.y - e.Vertexes[-1].Point.y) > 1e-6]
    return house.makeFillet(10.0, edges).cut(cyl_y(P.drum_shaft_d, y0 - 1, y0 + 60.0, x, DZ))


def motor():
    x = P.drive_side * P.drum_x
    y0 = Y_FBRG[1] + P.gear_box[2]
    body = cyl_y(P.motor_d, y0, y0 + P.motor_len, x, DZ)
    fins = [box_span((x - P.motor_d / 2.0 - 4.0, x + P.motor_d / 2.0 + 4.0), (y0 + 20.0 + 25.0 * k, y0 + 24.0 + 25.0 * k),
                     (DZ - 6.0, DZ + 6.0)) for k in range(5)]
    term = box_span((x - 30.0, x + 30.0), (y0 + 30.0, y0 + 90.0), (DZ + P.motor_d / 2.0 - 10.0, DZ + P.motor_d / 2.0 + 30.0))
    return fuse_all([body, term] + fins)


# ---------------------------------------------------------------------
# Castors (2) on arms in front of the front rail
# ---------------------------------------------------------------------
YS = P.caster_y + P.caster_offset                   # swivel axis (y)
CACT_Z0 = P.caster_h + 6.0 + P.cact_ext_work        # actuator body bottom (comb mode)


def castor_arms():
    """Arm (tube 40 x 40) from the front rail to a clamp ring around each castor actuator."""
    out = []
    s, _, wall = P.caster_arm
    ro = P.cact_body[0] / 2.0 + 10.0
    for sx in (-1, 1):
        x = sx * P.caster_x
        arm = tube_y(Y_FR[1], YS - ro + 4.0, x, DZ, s, s, wall)
        ring = cyl_z(2 * ro, DZ - s / 2.0, DZ + s / 2.0, x, YS).cut(cyl_z(P.cact_body[0], DZ - 30, DZ + 30, x, YS))
        out += [arm, ring]
    return Part.makeCompound(out)


def castor_act_bodies():
    """24 V linear actuators, vertical, body in the clamp ring; bore for the rod."""
    out = []
    d, L = P.cact_body
    for sx in (-1, 1):
        x = sx * P.caster_x
        body = cyl_z(d, CACT_Z0, CACT_Z0 + L, x, YS).cut(cyl_z(P.cact_rod_d + 2.0, CACT_Z0 - 1, CACT_Z0 + 200.0, x, YS))
        motor = cyl_z(40.0, CACT_Z0 + 60.0, CACT_Z0 + L - 20.0, x + sx * 0.0, YS + d / 2.0 + 18.0)
        out += [body, motor]
    return Part.makeCompound(out)


def castor_act_rods():
    """Rods from inside the body down to the castor swivel plate (comb mode); they move with the castors."""
    out = []
    for sx in (-1, 1):
        x = sx * P.caster_x
        out.append(cyl_z(P.cact_rod_d, P.caster_h + 6.0, CACT_Z0 + 190.0 - P.cact_ext_work, x, YS))
    return Part.makeCompound(out)


def castors():
    """Swivel castor Ø200 x 60: top plate, swivel, fork, wheel (the wheel trails behind the swivel)."""
    out = []
    ys = YS
    yw = P.caster_y
    az = P.caster_d / 2.0
    for sx in (-1, 1):
        x = sx * P.caster_x
        plate = box_span((x - 50.0, x + 50.0), (ys - 50.0, ys + 50.0), (P.caster_h, P.caster_h + 6.0))
        swivel = cyl_z(70.0, P.caster_h - 18.0, P.caster_h, x, ys)
        fork = []
        for s in (-1, 1):
            fork.append(poly_yz([(ys - 20.0, P.caster_h - 18.0), (ys + 20.0, P.caster_h - 18.0), (yw + 15.0, az - 12.0),
                                 (yw - 15.0, az - 12.0)], x + s * (P.caster_w / 2.0 + 4.0) - (4.0 if s > 0 else 0.0),
                                4.0))
        wheel = cyl_x(P.caster_d, x - P.caster_w / 2.0, x + P.caster_w / 2.0, yw, az).cut(
            cyl_x(P.caster_d - 70.0, x - P.caster_w / 2.0 - 1, x + P.caster_w / 2.0 + 1, yw, az))
        hub = cyl_x(P.caster_d - 70.0, x - P.caster_w / 2.0 + 6.0, x + P.caster_w / 2.0 - 6.0, yw, az)
        axle = cyl_x(12.0, x - P.caster_w / 2.0 - 10.0, x + P.caster_w / 2.0 + 10.0, yw, az)
        out.append((fuse_all([plate, swivel] + fork + [axle]), wheel, hub))
    return out


def castor_frames():
    return Part.makeCompound([c[0] for c in castors()])


def castor_tyres():
    return Part.makeCompound([c[1] for c in castors()])


def castor_hubs():
    return Part.makeCompound([c[2] for c in castors()])


# ---------------------------------------------------------------------
# Swath board at the left end
# ---------------------------------------------------------------------
def swath_board():
    x = P.board_x
    board = box_span((x - P.board_t, x), P.board_y, P.board_z)
    # turned-in rear edge so the windrow stays narrow
    lip = box_span((x - P.board_t, x + 120.0), (P.board_y[0], P.board_y[0] + P.board_t), P.board_z)
    return fuse_all([board, lip])


def board_support():
    s, z, y = P.board_arm
    post = tube_z(DZ + P.rail[0] / 2.0, z + s / 2.0, P.board_post_x, y, s, 3.0)
    arm = tube_x(P.board_x, P.board_post_x + s / 2.0, y, z, s, s, 3.0)
    hinge = cyl_z(16.0, P.board_z[1] - 60.0, z - s / 2.0, P.board_x + 10.0, y)
    return fuse_all([post, arm, hinge])


# ---------------------------------------------------------------------
# Rake head on the roll stub (moves with the rake)
# ---------------------------------------------------------------------
def head():
    y0, y1 = P.pin_head_y - 25.0, P.pin_head_y + 25.0
    sleeve = cyl_y(P.head_sleeve[0], P.pin_head_y - P.head_sleeve[1] / 2.0, P.pin_head_y + P.head_sleeve[1] / 2.0, 0.0,
                   DZ).cut(cyl_y(P.stub_d + 1.0, y0 - 30, y1 + 30, 0.0, DZ))
    lugs = []
    for sx in (-1, 1):
        x = sx * P.head_x
        lug = poly_yz([(y0, P.pin_z[1] - 24.0), (y1, P.pin_z[1] - 24.0), (y1, P.pin_z[0] + 22.0),
                       (y0, P.pin_z[0] + 22.0)], x - 4.0, 8.0)
        for z in P.pin_z:
            lug = lug.cut(cyl_x(P.pin_d + 0.5, x - 10, x + 10, P.pin_head_y, z))
        lug = lug.cut(cyl_y(P.stub_d + 1.0, y0 - 1, y1 + 1, 0.0, DZ))
        lugs.append(lug)
    return fuse_all([sleeve] + lugs)


def head_pins():
    """Short pins, one per side (the stub and the actuator are in the middle)."""
    x0, x1 = P.head_x - 4.0, P.arm_x + P.arm_tube[0] / 2.0
    return Part.makeCompound([pin_x(sx * x0, sx * x1, P.pin_head_y, z) if sx > 0 else
                              mirror_x(pin_x(x0, x1, P.pin_head_y, z)) for z in P.pin_z for sx in (-1, 1)])


def stub_collar():
    """Collar with a split pin behind the sleeve (holds the rake head on the stub)."""
    y = P.pin_head_y - P.head_sleeve[1] / 2.0
    return cyl_y(P.stub_d + 16.0, y - 12.0, y - 1.0, 0.0, DZ).cut(cyl_y(P.stub_d, y - 13.0, y, 0.0, DZ))


# ---------------------------------------------------------------------
# Mount on the robot: plate under the front lower beams, headstock plates, lug for the actuator
# ---------------------------------------------------------------------
def mount_plate():
    (x0, x1), (y0, y1), (z0, z1) = P.mount_plate
    pl = box_span((x0, x1), (y0, y1), (z0, z1))
    pl = pl.cut(cyl_z(P.gnss_hole, z0 - 1, z1 + 1, P.robot_gnss[0], P.robot_gnss[1]))
    for x in P.mount_bolt_x:
        for y in (P.robot_lower_beam_y[2], P.robot_lower_beam_y[3]):
            pl = pl.cut(cyl_z(P.m10_hole, z0 - 1, z1 + 1, x, y))
    return pl


def headstock():
    z1 = P.mount_plate[2][0]
    out = []
    for sx in (-1, 1):
        x = sx * P.stock_x
        y0, y1 = P.stock_y
        pl = poly_yz([(y0, z1), (y1, z1), (P.pin_front_y + 35.0, P.pin_z[1] - 30.0), (P.pin_front_y - 35.0,
                                                                                      P.pin_z[1] - 30.0)],
                     x - P.stock_t / 2.0, P.stock_t)
        for z in P.pin_z:
            pl = pl.cut(cyl_x(P.pin_d + 0.5, x - 10, x + 10, P.pin_front_y, z))
        out.append(pl)
    return Part.makeCompound(out)


def mount_bolts():
    out = []
    for x in P.mount_bolt_x:
        for y in (P.robot_lower_beam_y[2], P.robot_lower_beam_y[3]):
            out.append(bolt_z(x, y, P.robot_lower_beam_z[1], P.mount_plate[2][0]))
    return Part.makeCompound(out)


def front_pins():
    """Short pins, one per side, through the arm and the headstock plate (the actuator runs between them)."""
    x0, x1 = P.arm_x - P.arm_tube[0] / 2.0, P.stock_x + P.stock_t / 2.0
    return Part.makeCompound([pin_x(x0, x1, P.pin_front_y, z) if sx > 0 else mirror_x(pin_x(x0, x1, P.pin_front_y, z))
                              for z in P.pin_z for sx in (-1, 1)])


# ---------------------------------------------------------------------
# Parallelogram arms (each pair its own sub-Part, rotating about its front pin)
# ---------------------------------------------------------------------
def arm_pair(z, cross=False):
    w, h, wall = P.arm_tube
    out = []
    for sx in (-1, 1):
        x = sx * P.arm_x
        a = tube_y(P.pin_front_y - 22.0, P.pin_head_y + 22.0, x, z, w, h, wall)
        for y in (P.pin_front_y, P.pin_head_y):
            a = a.cut(cyl_x(P.pin_d + 0.5, x - 30, x + 30, y, z))
            a = a.fuse(cyl_x(P.pin_d + 12.0, x - w / 2.0, x + w / 2.0, y, z).cut(
                cyl_x(P.pin_d + 0.5, x - 30, x + 30, y, z)))
        out.append(a)
    if cross:
        c = box_span((-P.arm_x + w / 2.0, P.arm_x - w / 2.0), (P.lower_cross_y - 20.0, P.lower_cross_y + 20.0),
                     (z - 20.0, z + 20.0))
        out.append(c)
    return fuse_all(out)


def upper_arms():
    return arm_pair(P.pin_z[0])


def lower_arms():
    return arm_pair(P.pin_z[1], cross=True)


# ---------------------------------------------------------------------
# Control box on the upper inner beams
# ---------------------------------------------------------------------
def box_base():
    (x0, x1), (y0, y1), t = P.box_base
    z0 = P.robot_upper_beam_z[1]
    pl = box_span((x0, x1), (y0, y1), (z0, z0 + t))
    for x in P.box_bolt[0]:
        for y in P.box_bolt[1]:
            pl = pl.cut(cyl_z(P.m10_hole, z0 - 1, z0 + t + 1, x, y))
    return pl


def box_bolts():
    z0 = P.robot_upper_beam_z[1]
    return Part.makeCompound([bolt_z(x, y, z0 + P.box_base[2], P.robot_upper_beam_z[0]) for x in P.box_bolt[0]
                              for y in P.box_bolt[1]])


def control_box():
    z0 = P.robot_upper_beam_z[1] + P.box_base[2]
    b = box_span(P.box_x, P.box_y, (z0, z0 + P.box_h))
    lid = box_span((P.box_x[0] - 4, P.box_x[1] + 4), (P.box_y[0] - 4, P.box_y[1] + 4), (z0 + P.box_h, z0 + P.box_h + 12))
    glands = [cyl_y(16.0, P.box_y[1], P.box_y[1] + 14.0, x, z0 + 30.0) for x in (-200.0, 200.0)]
    return fuse_all([b, lid] + glands)


# ---------------------------------------------------------------------
# Scene: litter / hay bits, nursery seedlings, windrow
# ---------------------------------------------------------------------
def straw(x, y, l, rot, z=1.0, w=4.0, t=2.0):
    s = Part.makeBox(l, w, t, V(-l / 2.0, -w / 2.0, 0))
    s.rotate(V(0, 0, 0), Z, rot)
    s.translate(V(x, y, z))
    return s


def tree(x, y, h=250.0, seed=0):
    """Small conifer seedling (nursery bed): stem and three stacked cones."""
    rnd = random.Random(seed)
    parts = [cyl_z(6.0, 0.0, h * 0.4, x, y)]
    for k in range(3):
        r = (0.32 - 0.08 * k) * h * rnd.uniform(0.85, 1.1)
        z0 = h * (0.25 + 0.22 * k)
        parts.append(Part.makeCone(r, 2.0, h * 0.35, V(x, y, z0)))
    return Part.makeCompound(parts)


def weed(x, y, s=1.0):
    a = cyl_z(3.0, 0.0, 15.0 * s, x, y)
    leaves = []
    for k in (-1, 1):
        lf = Part.makeCylinder(8.0 * s, 1.5, V(0, 0, 0), Z)
        m = App.Matrix()
        m.scale(1.0, 0.6, 1.0)
        lf = lf.transformGeometry(m)
        lf.translate(V(k * 8.0 * s, 0, 15.0 * s))
        lf.rotate(V(0, 0, 15.0 * s), Z, (x * 7.0 + y * 3.0) % 180.0)
        lf.translate(V(x, y, 0))
        leaves.append(lf)
    return Part.makeCompound([a] + leaves)
