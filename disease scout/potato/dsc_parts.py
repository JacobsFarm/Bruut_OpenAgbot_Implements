"""Parts of the potato disease scout: one function per part, in robot coordinates, wings in the working position
(beta = 0). The right wing, its swing arm and actuator are drawn; the left ones are mirrored (mirror_x). The actuator
is drawn in its own frame: origin on the base pin, axis along +x at height act_z (build_dsc places it)."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dsc_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)

Y0, Y1 = P.hood_y
FZ0, FZ1 = P.frame_z
S = P.sheet
F = P.frame


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


def ring_z(od, bore, z0, z1, x, y):
    return cyl_z(od, z0, z1, x, y).cut(cyl_z(bore, z0 - 1, z1 + 1, x, y))


def ring_x(od, bore, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return cyl_x(od, x0, x1, y, z).cut(cyl_x(bore, x0 - 1, x1 + 1, y, z))


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


def compound(shapes):
    return Part.makeCompound(list(shapes))


def rod_between(p0, p1, d):
    p0, p1 = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (p1 - p0).Length, p0, p1 - p0)


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def both(shape):
    """The shape and its mirror image in x (one compound)."""
    return compound([shape, mirror_x(shape)])


def tube_x(x0, x1, y, z, b, h, wall):
    """Rectangular tube along x: width b (y), height h (z), centred on (y, z)."""
    o = box_span((x0, x1), (y - b / 2, y + b / 2), (z - h / 2, z + h / 2))
    i = box_span((x0 - 1, x1 + 1), (y - b / 2 + wall, y + b / 2 - wall), (z - h / 2 + wall, z + h / 2 - wall))
    return o.cut(i)


def tube_y(y0, y1, x, z, b, h, wall):
    o = box_span((x - b / 2, x + b / 2), (y0, y1), (z - h / 2, z + h / 2))
    i = box_span((x - b / 2 + wall, x + b / 2 - wall), (y0 - 1, y1 + 1), (z - h / 2 + wall, z + h / 2 - wall))
    return o.cut(i)


def tube_z(z0, z1, x, y, b, wall):
    o = box_span((x - b / 2, x + b / 2), (y - b / 2, y + b / 2), (z0, z1))
    i = box_span((x - b / 2 + wall, x + b / 2 - wall), (y - b / 2 + wall, y + b / 2 - wall), (z0 - 1, z1 + 1))
    return o.cut(i)


def ellipsoid(c, r):
    s = Part.makeSphere(1.0)
    m = App.Matrix()
    m.scale(r[0], r[1], r[2])
    s = s.transformGeometry(m)
    s.translate(V(*c))
    return s


# ---------------------------------------------------------------------
# Hood sections (centre: x0 -600 .. 600; right wing: x 600 .. 1500)
# ---------------------------------------------------------------------
WING = (P.centre_half, P.half_width)
CENTRE = (-P.centre_half, P.centre_half)


def roof(x):
    return box_span(x, (Y0, Y1), (P.roof_top - S, P.roof_top))


def walls(x, end=False):
    z = (P.wall_bottom, P.roof_top - S)
    parts = [box_span(x, (Y1 - S, Y1), z), box_span(x, (Y0, Y0 + S), z)]
    if end:
        parts.append(box_span((x[1] - S, x[1]), (Y0 + S, Y1 - S), z))
    return compound(parts)


def frame(x, cross, end=False):
    """Roof frame: front and rear tubes along x, cross tubes along y between them."""
    xin = (x[0], x[1] - S) if end else x
    zc = 0.5 * (FZ0 + FZ1)
    parts = [tube_x(xin[0], xin[1], Y1 - S - F / 2, zc, F, F, P.frame_wall),
             tube_x(xin[0], xin[1], Y0 + S + F / 2, zc, F, F, P.frame_wall)]
    for cx in cross:
        parts.append(tube_y(Y0 + S + F, Y1 - S - F, cx, zc, F, F, P.frame_wall))
    return compound(parts)


def rails(x, end=False):
    xin = (x[0], x[1] - S) if end else x
    zc = 0.5 * (P.rail_z[0] + P.rail_z[1])
    return compound([tube_x(xin[0], xin[1], ry, zc, P.rail[0], P.rail[1], P.frame_wall) for ry in P.rail_y])


def _strips(x0, x1, y0, y1):
    n = max(1, int(round((x1 - x0) / P.curtain_strip)))
    gap = 1.0
    w = (x1 - x0 - (n - 1) * gap) / n
    return [box_span((x0 + i * (w + gap), x0 + i * (w + gap) + w), (y0, y1), P.curtain_z) for i in range(n)]


def curtain_x(x, end=False):
    """Strip curtains inside the front and rear walls over the x range."""
    x0, x1 = x
    if end:
        x1 -= S
    t = P.curtain_t
    return compound(_strips(x0, x1, Y1 - S - t, Y1 - S) + _strips(x0, x1, Y0 + S, Y0 + S + t))


def clamps_x(x, end=False):
    x0, x1 = x
    if end:
        x1 -= S
    t, c = P.curtain_t, P.clamp
    z = (P.wall_bottom, P.wall_bottom + c[0])
    return compound([box_span((x0, x1), (Y1 - S - t - c[1], Y1 - S - t), z),
                     box_span((x0, x1), (Y0 + S + t, Y0 + S + t + c[1]), z)])


def cams(xs):
    b = P.cam_body
    z0 = P.rail_z[0] - b[2]
    return compound([box_span((x - b[0] / 2, x + b[0] / 2), (P.hood_yc - b[1] / 2, P.hood_yc + b[1] / 2), (z0, P.rail_z[0]))
                     for x in xs] +
                    [cyl_z(P.cam_lens[0], P.cam_lens_z0, z0, x, P.hood_yc) for x in xs])


def lenses(xs):
    return compound([cyl_z(P.cam_lens[0] - 6.0, P.cam_lens_z0 - 1.0, P.cam_lens_z0, x, P.hood_yc) for x in xs])


def leds(xs):
    a, h = P.led_sec
    z = (P.rail_z[0] - h, P.rail_z[0])
    return compound([box_span((x - P.led_len / 2, x + P.led_len / 2), (ry - a / 2, ry + a / 2), z)
                     for x in xs for ry in (P.rail_y[0], P.rail_y[2])])


def diffusers(xs):
    a, h = P.led_sec
    z1 = P.rail_z[0] - h
    return compound([box_span((x - P.led_len / 2 + 5, x + P.led_len / 2 - 5), (ry - a / 2 + 4, ry + a / 2 - 4),
                              (z1 - P.led_diffuser, z1))
                     for x in xs for ry in (P.rail_y[0], P.rail_y[2])])


CENTRE_CAMS = tuple(x for x in P.cam_x if abs(x) < P.centre_half)
WING_CAMS = tuple(x for x in P.cam_x if x > P.centre_half)


def centre_roof():
    return roof(CENTRE)


def centre_walls():
    return walls(CENTRE)


def centre_frame():
    xs = sorted(set([c for c in P.cross_x_centre] + [-c for c in P.cross_x_centre]))
    return frame(CENTRE, xs)


def centre_rails():
    return rails(CENTRE)


def centre_curtains():
    g = P.curtain_end_gap
    return curtain_x((-P.centre_half + g, P.centre_half - g))


def centre_clamps():
    g = P.curtain_end_gap
    return clamps_x((-P.centre_half + g, P.centre_half - g))


def centre_cameras():
    return cams(CENTRE_CAMS)


def centre_lenses():
    return lenses(CENTRE_CAMS)


def centre_leds():
    return leds(CENTRE_CAMS)


def centre_diffusers():
    return diffusers(CENTRE_CAMS)


def uprights():
    """Headstock: 2 uprights inside the rear wall, a plate outside it, 2 ear pairs per side for the links."""
    yi = Y0 + S + P.curtain_t + P.clamp[1]                        # 787.5
    parts = []
    for s in (1, -1):
        x = s * P.upright_x
        parts.append(tube_z(P.wall_bottom + P.clamp[0], FZ0, x, yi + F / 2, F, P.frame_wall))
    return compound(parts)


def headstock():
    parts = []
    t = P.ear_t
    for s in (1, -1):
        x = s * P.post_x
        parts.append(box_span((x - 30, x + 30), (Y0 - 6.0, Y0), (P.link_z[0] - 40, P.link_z[1] + 40)))
        for z in P.link_z:
            for side in (-1, 1):
                xe = x + side * (P.link_sec / 2 + t / 2)
                ear = box_span((xe - t / 2, xe + t / 2), (P.link_y[1] - 15, Y0 - 6.0), (z - 25, z + 25))
                parts.append(ear.cut(cyl_x(P.link_pin_d + 0.5, xe - 5, xe + 5, P.link_y[1], z)))
    return compound(parts)


# ---------------------------------------------------------------------
# Right wing (working position)
# ---------------------------------------------------------------------
def wing_roof_right():
    return roof(WING)


def wing_walls_right():
    return walls(WING, end=True)


def wing_frame_right():
    return frame(WING, P.cross_x_wing, end=True)


def wing_rails_right():
    return rails(WING, end=True)


def wing_curtains_right():
    return curtain_x(WING, end=True)


def wing_clamps_right():
    return clamps_x(WING, end=True)


def wing_brush_right():
    """Brush strip on the inside of the end wall: holder flat and bristles (the outer ridge runs under it)."""
    x1 = P.half_width - S
    yr = (Y0 + S + P.curtain_t + P.clamp[1], Y1 - S - P.curtain_t - P.clamp[1])
    return compound([box_span((x1 - P.clamp[1], x1), yr, (P.wall_bottom, P.wall_bottom + P.clamp[0])),
                     box_span((x1 - P.brush_t, x1), yr, P.brush_z)])


def wing_cameras_right():
    return cams(WING_CAMS)


def wing_lenses_right():
    return lenses(WING_CAMS)


def wing_leds_right():
    return leds(WING_CAMS)


def wing_diffusers_right():
    return diffusers(WING_CAMS)


def wing_pads_right():
    t0, t1 = P.arm_t
    return compound([box_span((P.pivot_x + s - 20, P.pivot_x + s + 20), (P.pivot[1] + t0, P.pivot[1] + t1),
                              (P.roof_top, P.arm_z[0])) for s in P.pad_s])


def swing_arm_right():
    """Sleeve on the kingpin, arm 40 x 60 x 3 along the front edge to the wing tip, tie rod from the sleeve top."""
    px, py = P.pivot
    od, bore, z0, z1 = P.sleeve
    t0, t1 = P.arm_t
    zc = 0.5 * (P.arm_z[0] + P.arm_z[1])
    arm = tube_x(px + od / 2 - 5.0, px + P.arm_s1, py + 0.5 * (t0 + t1), zc, P.arm_sec[0], P.arm_sec[1], P.arm_wall)
    arm = arm.fuse(box_span((px + P.arm_s1 - 4.0, px + P.arm_s1), (py + t0, py + t1), P.arm_z))   # end cap
    tie = rod_between((px + 22.0, py - 20.0, z1 - 12.0), (px + P.tie_s, py - 20.0, P.arm_z[1] - 2.0), P.tie_d)
    sl = ring_z(od, bore, z0, z1, px, py)
    return fuse_all([sl, arm, tie])


def rod_end_bracket_right():
    ex, ey = P.pivot[0] + P.act_end_rel[0], P.pivot[1] + P.act_end_rel[1]
    plate = box_span((ex - 20, ex + 20), (P.pivot[1] + P.arm_t[0], P.pivot[1] + P.arm_t[1]),
                     (P.arm_z[1], P.arm_z[1] + 6.0))
    return plate


def rod_end_pin_right():
    ex, ey = P.pivot[0] + P.act_end_rel[0], P.pivot[1] + P.act_end_rel[1]
    return cyl_z(P.act_pin_d, P.arm_z[1] + 6.0, P.act_z + P.act_eye[2] / 2 + 7.0, ex, ey)


# ---------------------------------------------------------------------
# Kingpins, actuator bases (fixed on the centre roof)
# ---------------------------------------------------------------------
def kingpin_plate():
    return box_span(*P.pin_plate)


def kingpins():
    out = []
    for s in (1, -1):
        x = s * P.pivot_x
        out.append(cyl_z(P.pin_d, P.pin_z[0], P.sleeve[3] + 2.0, x, P.pivot[1]))
        out.append(cyl_z(P.pin_d + 10.0, P.sleeve[3] + 2.0, P.sleeve[3] + 10.0, x, P.pivot[1]))
    return compound(out)


def act_base_posts():
    bx, by = P.act_base
    z1 = P.act_z - P.act_eye[2] / 2 - 5.0
    return both(tube_z(P.roof_top, z1, bx, by, 30.0, 3.0).fuse(box_span((bx - 25, bx + 25), (by - 25, by + 25),
                                                                       (P.roof_top, P.roof_top + 6.0))))


def act_base_pins():
    bx, by = P.act_base
    z0 = P.act_z - P.act_eye[2] / 2 - 5.0
    return both(cyl_z(P.act_pin_d, z0, P.act_z + P.act_eye[2] / 2 + 7.0, bx, by))


# ---------------------------------------------------------------------
# Actuator (own frame: base pin at the origin, axis +x, height act_z)
# ---------------------------------------------------------------------
def act_body():
    od, bore, x0, x1 = P.act_body
    eo, eb, eh = P.act_eye
    z = P.act_z
    eye = ring_z(eo, eb, z - eh / 2, z + eh / 2, 0.0, 0.0)
    neck = box_span((eb / 2 + 3.0, x0 + 1.0), (-8, 8), (z - 8, z + 8))
    body = cyl_x(od, x0, x1, 0.0, z).cut(cyl_x(bore, x0 + 10.0, x1 + 1, 0.0, z))
    motor = cyl_x(38.0, x0 + 20.0, x0 + 150.0, -od / 2 - 14.0, z)     # motor alongside (towards -y local)
    web = box_span((x0 + 30.0, x0 + 140.0), (-od / 2 - 4.0, -od / 2 + 6.0), (z - 10, z + 10))
    return fuse_all([eye.cut(cyl_z(eb, z - eh, z + eh, 0, 0)), neck, body, motor, web])


def act_rod():
    """Rod at the retracted length act_closed (build_dsc slides it along +x)."""
    d, length = P.act_rod
    eo, eb, eh = P.act_eye
    z = P.act_z
    L = P.act_closed
    rod = cyl_x(d, L - length, L - eo / 2 + 1.0, 0.0, z)
    eye = ring_z(eo, eb, z - eh / 2, z + eh / 2, L, 0.0)
    return fuse_all([rod, eye])


# ---------------------------------------------------------------------
# Castors (right; the left one mirrored). Wheel separately (it rotates about its axle).
# ---------------------------------------------------------------------
def castor_axle_y():
    return P.castor_stem_y - P.castor_trail


def castor_housing_right(x=P.castor_x):
    d, h = P.castor_housing
    return ring_z(d, P.castor_stem_d + 0.5, P.rail_z[0] - h + 20.0, FZ0, x, P.castor_stem_y)


def castor_fork_right(x=P.castor_x):
    ys = P.castor_stem_y
    cx, cy, ct, cz = P.castor_crown
    ya = castor_axle_y()
    lt, lw = P.castor_leg
    axle_z = P.castor_wheel[0] / 2.0
    stem = cyl_z(P.castor_stem_d, cz + ct, FZ0 - 8.0, x, ys)
    crown = box_span((x - cx / 2, x + cx / 2), (ya - lw / 2, ys + P.castor_stem_d / 2 + 5.0), (cz, cz + ct))
    gap = P.castor_wheel[1] / 2 + 6.0
    legs = [box_span((x + s * gap, x + s * (gap + lt)), (ya - lw / 2, ya + lw / 2), (axle_z - 15.0, cz))
            for s in (1, -1)]
    axle = cyl_x(P.castor_axle_d, x - gap - lt - 4.0, x + gap + lt + 4.0, ya, axle_z)
    return fuse_all([stem, crown] + legs + [axle])


def castor_wheel_right(x=P.castor_x):
    d, w = P.castor_wheel
    tyre = cyl_x(d, x - w / 2, x + w / 2, castor_axle_y(), d / 2.0)
    tyre = tyre.cut(cyl_x(P.castor_axle_d + 0.5, x - w, x + w, castor_axle_y(), d / 2.0))
    edges = [e for e in tyre.Edges if e.Curve.TypeId == "Part::GeomCircle" and abs(e.Curve.Radius - d / 2) < 1e-3]
    try:
        tyre = tyre.makeFillet(18.0, edges)
    except Exception:
        pass
    return tyre


def castor_rim_right(x=P.castor_x):
    d, w = P.castor_wheel
    ya, za = castor_axle_y(), d / 2.0
    return compound([ring_x(130.0, P.castor_axle_d + 0.5, x + s * w / 2, x + s * (w / 2 + 2.0), ya, za)
                     for s in (1, -1)])


# ---------------------------------------------------------------------
# Mount on the robot: posts and the parallelogram links
# ---------------------------------------------------------------------
def post_plates():
    (x0, x1), y, t = P.post_plate
    z0 = P.robot_lower_beam_z[1]
    plate = box_span((x0, x1), y, (z0, z0 + t))
    for x in P.post_bolt_x:
        for yb in (P.robot_lower_beam_y[2], P.robot_lower_beam_y[3]):
            plate = plate.cut(cyl_z(P.m10_hole + 0.6, z0 - 1, z0 + t + 1, x, yb))
    return both(plate)


def post_bolts():
    z_top = P.robot_lower_beam_z[1] + P.post_plate[2]
    out = []
    for x in P.post_bolt_x:
        for y in (P.robot_lower_beam_y[2], P.robot_lower_beam_y[3]):
            head = cyl_z(17.0, z_top, z_top + 7.0, x, y)
            shank = cyl_z(10.0, P.robot_lower_beam_z[0] - 9.0, z_top, x, y)
            nut = cyl_z(17.0, P.robot_lower_beam_z[0] - 9.0, P.robot_lower_beam_z[0], x, y)
            out.append(fuse_all([head, shank, nut]))
    return both(compound(out))


def posts():
    a, t = P.post
    z0 = P.robot_lower_beam_z[1] + P.post_plate[2]
    p = tube_z(z0, P.post_top, P.post_x, P.post_y, a, t)
    cap = box_span((P.post_x - a / 2, P.post_x + a / 2), (P.post_y - a / 2, P.post_y + a / 2),
                   (P.post_top, P.post_top + 6.0))
    return both(p.fuse(cap))


def post_ears():
    a = P.post[0]
    t = P.ear_t
    out = []
    for z in P.link_z:
        for side in (-1, 1):
            xe = P.post_x + side * (P.link_sec / 2 + t / 2)
            ear = box_span((xe - t / 2, xe + t / 2), (P.post_y + a / 2, P.link_y[0] + 16.0), (z - 25, z + 25))
            out.append(ear.cut(cyl_x(P.link_pin_d + 0.5, xe - 5, xe + 5, P.link_y[0], z)))
    return both(compound(out))


def links():
    out = []
    for z in P.link_z:
        b = P.link_sec
        x0, x1 = P.post_x - b / 2, P.post_x + b / 2
        bar = box_span((x0, x1), (P.link_y[0], P.link_y[1]), (z - b / 2, z + b / 2))
        bar = bar.cut(box_span((x0 + 3, x1 - 3), (P.link_y[0] + 15, P.link_y[1] - 15), (z - b / 2 + 3, z + b / 2 - 3)))
        bosses = [cyl_x(P.link_boss, x0, x1, y, z) for y in P.link_y]
        s = fuse_all([bar] + bosses)
        for y in P.link_y:
            s = s.cut(cyl_x(P.link_pin_d + 0.5, x0 - 1, x1 + 1, y, z))
        out.append(s)
    return both(compound(out))


def link_pins():
    out = []
    for z in P.link_z:
        for y in P.link_y:
            out.append(cyl_x(P.link_pin_d, P.post_x - P.link_sec / 2 - P.ear_t - 4.0,
                             P.post_x + P.link_sec / 2 + P.ear_t + 4.0, y, z))
    return both(compound(out))


# ---------------------------------------------------------------------
# Roof equipment
# ---------------------------------------------------------------------
def control_box():
    return box_span(P.box_xy[0], P.box_xy[1], (P.roof_top, P.roof_top + P.box_h))


def antenna():
    x, y = 0.0, 0.5 * (P.box_xy[1][0] + P.box_xy[1][1])
    z0 = P.roof_top + P.box_h
    stem = cyl_z(P.ant_stem[0], z0, z0 + P.ant_stem[1], x, y)
    dome = cyl_z(P.ant_dome[0], z0 + P.ant_stem[1], z0 + P.ant_stem[1] + P.ant_dome[1], x, y)
    edges = [e for e in dome.Edges if e.Curve.TypeId == "Part::GeomCircle" and e.Vertexes[0].Point.z > z0 + 30]
    try:
        dome = dome.makeFillet(30.0, edges)
    except Exception:
        pass
    return stem.fuse(dome)


# ---------------------------------------------------------------------
# Render / field helpers
# ---------------------------------------------------------------------
def footprint(x, zc):
    """Camera image on the canopy plane at height zc: a thin plate."""
    sw, sh = P.cam_px[0] * P.cam_pixel, P.cam_px[1] * P.cam_pixel
    dist = P.cam_lens_z0 - zc
    a, b = sw / P.cam_f * dist / 2, sh / P.cam_f * dist / 2
    return box_span((x - a, x + a), (P.hood_yc - b, P.hood_yc + b), (zc, zc + 2.0))


def ridges(x_range, y_range):
    """Potato ridges along y: furrow bottom z 0 (100 wide), ridge top 250 (220 wide), ridges at 0, +-750 ..."""
    out = []
    k0 = int(math.floor(x_range[0] / P.row_pitch)) - 1
    k1 = int(math.ceil(x_range[1] / P.row_pitch)) + 1
    for k in range(k0, k1 + 1):
        xr = k * P.row_pitch
        half_base = P.row_pitch / 2 - P.furrow_w / 2
        pts = [(xr - half_base, 0.0), (xr + half_base, 0.0), (xr + P.ridge_top_w / 2 + 40, P.ridge_h - 25),
               (xr + P.ridge_top_w / 2, P.ridge_h), (xr - P.ridge_top_w / 2, P.ridge_h),
               (xr - P.ridge_top_w / 2 - 40, P.ridge_h - 25)]
        face = Part.Face(Part.makePolygon([V(x, y_range[0], z) for (x, z) in pts] + [V(pts[0][0], y_range[0], pts[0][1])]))
        out.append(face.extrude(V(0, y_range[1] - y_range[0], 0)))
    out.append(box_span((x_range[0] - P.row_pitch, x_range[1] + P.row_pitch), y_range, (-40.0, 0.0)))
    return compound(out)


def plant(x, y, top, size=1.0):
    """A potato plant: 3 overlapping ellipsoids, the top at height 'top'."""
    h = top - P.ridge_h
    r = 210.0 * size
    return compound([ellipsoid((x, y, P.ridge_h + 0.55 * h), (r, 0.85 * r, 0.45 * h)),
                     ellipsoid((x - 0.35 * r, y + 0.2 * r, P.ridge_h + 0.45 * h), (0.6 * r, 0.6 * r, 0.42 * h)),
                     ellipsoid((x + 0.3 * r, y - 0.25 * r, P.ridge_h + 0.5 * h), (0.6 * r, 0.6 * r, 0.45 * h))])


def flag(x, y, z0, h=500.0):
    """Marker of a suspect plant in the map (drawn in the animation only): stick and a flag."""
    stick = cyl_z(20.0, z0, z0 + h, x, y)
    fl = box_span((x, x + 180.0), (y - 4.0, y + 4.0), (z0 + h - 120.0, z0 + h))
    return compound([stick, fl])
