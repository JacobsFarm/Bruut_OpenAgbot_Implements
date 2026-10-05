import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ova_params as P
import ova_kin as K

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basisfuncties (zelfde stijl als ../../liquid fertilezer applicator/advanved/lfa_parts.py)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, h, axis="z", cx=0.0, cy=0.0, cz=0.0):
    r = d / 2.0
    if axis == "x":
        return Part.makeCylinder(r, h, V(cx - h / 2.0, cy, cz), X)
    if axis == "y":
        return Part.makeCylinder(r, h, V(cx, cy - h / 2.0, cz), Y)
    return Part.makeCylinder(r, h, V(cx, cy, cz - h / 2.0), Z)


def cyl_x(d, x0, x1, y, z):
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def ring_x(d_out, d_in, x0, x1, y, z):
    return cyl_x(d_out, x0, x1, y, z).cut(cyl_x(d_in, x0 - 1, x1 + 1, y, z))


def tube_span(x, y, z, wall):
    outer = box_span(x, y, z)
    sx, sy, sz = x[1] - x[0], y[1] - y[0], z[1] - z[0]
    if sx >= sy and sx >= sz:
        inner = box_span((x[0] - 1, x[1] + 1), (y[0] + wall, y[1] - wall), (z[0] + wall, z[1] - wall))
    elif sy >= sz:
        inner = box_span((x[0] + wall, x[1] - wall), (y[0] - 1, y[1] + 1), (z[0] + wall, z[1] - wall))
    else:
        inner = box_span((x[0] + wall, x[1] - wall), (y[0] + wall, y[1] - wall), (z[0] - 1, z[1] + 1))
    return outer.cut(inner)


def moved(shape, x=0.0, y=0.0, z=0.0):
    s = shape.copy()
    s.translate(V(x, y, z))
    return s


def rotated(shape, angle, axis=Z, base=V(0, 0, 0)):
    s = shape.copy()
    s.rotate(base, axis, angle)
    return s


def mirror_x(shape):
    return shape.mirror(V(0, 0, 0), X)


def mirrored_x(shape, side):
    return shape if side > 0 else mirror_x(shape)


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


def poly_yz(points, x0, t):
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0))


def stadium_yz(p1, p2, r, x0, t):
    (y1, z1), (y2, z2) = p1, p2
    length = math.hypot(y2 - y1, z2 - z1)
    ang = math.degrees(math.atan2(z2 - z1, y2 - y1))
    parts = [Part.makeCylinder(r, t, V(x0, y1, z1), X), Part.makeCylinder(r, t, V(x0, y2, z2), X)]
    if length > 1e-6:
        b = Part.makeBox(t, length, 2 * r, V(x0, 0, -r))
        b.rotate(V(0, 0, 0), X, ang)
        b.translate(V(0, y1, z1))
        parts.append(b)
    return fuse_all(parts)


def hex_prism(af, h, z0=0.0, cx=0.0, cy=0.0):
    r = af / math.sqrt(3.0)
    pts = [V(cx + r * math.cos(math.radians(60 * i)), cy + r * math.sin(math.radians(60 * i)), z0) for i in range(6)]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def frame_matrix(origin, u):
    uy, uz = u
    ny, nz = uz, -uy
    return App.Matrix(1, 0, 0, origin[0],
                      0, ny, uy, origin[1],
                      0, nz, uz, origin[2],
                      0, 0, 0, 1)


def orient(shape, origin, u):
    s = shape.copy()
    s.transformShape(frame_matrix(origin, u))
    return s


def bolt_z(d, af, k, length, nut_at=None, nut_m=None):
    parts = [hex_prism(af, k, z0=-k), Part.makeCylinder(d / 2.0, length)]
    if nut_at is not None:
        parts.append(hex_prism(af, nut_m, z0=nut_at))
    return fuse_all(parts)


def bolt_x(d, af, k, m, x0, x1, y, z, extra=3.0):
    """Bout langs +x: kop tegen x0 (kant -x), moer tegen x1."""
    length = x1 - x0 + m + extra
    b = bolt_z(d, af, k, length, nut_at=x1 - x0, nut_m=m)
    b = rotated(b, 90.0, Y)
    b.translate(V(x0, y, z))
    return b


def helix_spring(length, mean_r, wire, coils=None):
    if coils is None:
        coils = max(3.0, length / (wire * 2.6))
    pitch = length / coils
    usable = length - wire
    helix = Part.makeHelix(pitch, usable, mean_r)
    helix.translate(V(0, 0, wire / 2.0))
    edge = helix.Edges[0]
    start = edge.valueAt(edge.FirstParameter)
    tangent = edge.tangentAt(edge.FirstParameter)
    profile = Part.Wire(Part.makeCircle(wire / 2.0, start, tangent))
    return Part.Wire(helix.Edges).makePipeShell([profile], True, True)


def hose(points, od):
    pts = [V(*p) for p in points]
    bs = Part.BSplineCurve()
    bs.buildFromPoles(pts, False, 3)
    edge = bs.toShape()
    tangent = edge.tangentAt(edge.FirstParameter)
    profile = Part.Wire(Part.makeCircle(od / 2.0, pts[0], tangent))
    return Part.Wire(edge).makePipeShell([profile], True, True)


def cyl_between(p0, p1, d):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def pin_x(x0, x1, y, z, d=P.pin_d, head_d=26.0, head_t=4.0):
    parts = [cyl_x(d, x0 - head_t, x1 + head_t, y, z), cyl_x(head_d, x0 - head_t, x0, y, z),
             cyl_x(head_d, x1, x1 + head_t, y, z)]
    return fuse_all(parts)


# ---------------------------------------------------------------------
# Aanbouwbok (vast aan de robotbalk), side = +1 rechts, -1 links (als de toediener)
# ---------------------------------------------------------------------
def hs_cheek_x(inner):
    c = P.hs_x
    half = P.hs_link_gap / 2.0
    return (c - half - P.plate_t, c - half) if inner else (c + half, c + half + P.plate_t)


def hs_top_plate(side):
    t = P.plate_t
    plate = box_span(P.hs_top_x, P.hs_top_y, (P.robot_beam_z_top, P.robot_beam_z_top + t))
    holes = [cyl(P.robot_hole_d, 3 * t, "z", x, 0.0, P.robot_beam_z_top + t / 2.0) for x in P.hs_bolt_x]
    return mirrored_x(plate.cut(holes), side)


def hs_clamp_plate(side):
    t = P.plate_t
    plate = box_span(P.hs_clamp_x, P.hs_clamp_y, (P.robot_beam_z_bot - t, P.robot_beam_z_bot))
    holes = [cyl(P.robot_hole_d, 3 * t, "z", x, 0.0, P.robot_beam_z_bot - t / 2.0) for x in P.hs_bolt_x]
    return mirrored_x(plate.cut(holes), side)


def hs_back_plate(side):
    plate = box_span(P.hs_top_x, P.hs_back_y, (P.hs_z_bot, P.robot_beam_z_top))
    return mirrored_x(plate, side)


def hs_cheek(side, inner):
    y0, y1 = P.hs_back_y[0], P.hs_cheek_y_rear
    if inner:
        ty, tz, s = P.hs_cross_y, P.hs_cross_z, P.hs_cross_size
        z_plate = P.robot_beam_z_top + P.plate_t
        pts = [(y0, P.hs_z_bot), (y1, P.hs_z_bot), (y1, 625.0), (-40.0, 700.0), (ty - s / 2.0, tz + s / 2.0),
               (ty + s / 2.0, tz + s / 2.0), (ty + s / 2.0, tz - s / 2.0 - 10.0), (P.hs_top_y[1], z_plate),
               (y0, z_plate)]
    else:
        pts = [(y0, P.hs_z_bot), (y1, P.hs_z_bot), (y1, 625.0), (-60.0, 655.0), (y0, 655.0)]
    x0, x1 = hs_cheek_x(inner)
    plate = poly_yz(pts, x0, x1 - x0)
    holes = [cyl_x(P.pin_hole, x0 - 1, x1 + 1, P.pin_front_y, z) for z in (P.pin_upper_z, P.pin_lower_z)]
    return mirrored_x(plate.cut(holes), side)


def slot_ends():
    lo = P.act_a
    hi = K.add(P.act_a, K.slot_dir(), P.act_slot)
    return lo, hi


def hs_cross_top():
    """Bovenste dwarsbuis met de langgatplaten van de actuator, doorgetrokken tot de bovenste pen van de gasveren."""
    s = P.hs_cross_size
    x_in = hs_cheek_x(True)[0]
    tube = tube_span((-x_in, x_in), (P.hs_cross_y - s / 2.0, P.hs_cross_y + s / 2.0),
                     (P.hs_cross_z - s / 2.0, P.hs_cross_z + s / 2.0), 3.0)
    lo, hi = slot_ends()
    top = K.gas_anchor()
    z_tube = P.hs_cross_z - s / 2.0
    half = P.act_rod_eye_w / 2.0 + 0.5
    u = K.slot_dir()
    ny, nz = -u[1], u[0]                    # loodrecht op het langgat, naar boven-achter (naar de buis)
    lugs = []
    for sx in (-1, 1):
        x0 = half if sx > 0 else -half - 6.0
        web = poly_yz([(lo[0] + 12.0 * ny, lo[1] + 12.0 * nz), (top[0] + 12.0 * ny, top[1] + 12.0 * nz),
                       (P.hs_cross_y + s / 2.0 - 2.0, z_tube + 2.0), (P.hs_cross_y - s / 2.0 + 2.0, z_tube + 2.0)],
                      x0, 6.0)
        lug = fuse_all([stadium_yz(lo, top, 14.0, x0, 6.0), web])
        lugs.append(lug.cut(cyl_x(P.pin_hole, x0 - 1, x0 + 7.0, top[0], top[1])))
    body = fuse_all([tube] + lugs)
    return body.cut(stadium_yz(lo, hi, P.pin_hole / 2.0, -30.0, 60.0))


def hs_cross_low():
    s = P.hs_low_cross_size
    x_in = hs_cheek_x(True)[0]
    return tube_span((-x_in, x_in), (P.hs_low_cross_y - s / 2.0, P.hs_low_cross_y + s / 2.0),
                     (P.hs_low_cross_z - s / 2.0, P.hs_low_cross_z + s / 2.0), 3.0)


def hs_bolts(side):
    items = []
    z_head = P.robot_beam_z_top + P.plate_t
    length = z_head - (P.robot_beam_z_bot - P.plate_t) + P.m10_m + 3.0
    for x in P.hs_bolt_x:
        b = bolt_z(P.m10_d, P.m10_af, P.m10_k, length, nut_at=length - P.m10_m - 3.0, nut_m=P.m10_m)
        b = rotated(b, 180.0, X)
        b.translate(V(x, 0.0, z_head))
        items.append(b)
    return mirrored_x(Part.makeCompound(items), side)


def hs_pins(side):
    x0 = hs_cheek_x(True)[0]
    x1 = hs_cheek_x(False)[1]
    pins = [pin_x(x0, x1, P.pin_front_y, z) for z in (P.pin_upper_z, P.pin_lower_z)]
    return mirrored_x(Part.makeCompound(pins), side)


def gas_springs(pin):
    """(huizen, stangen + bovenste pen): 2 gasveren van de bovenste pen naar de pen in het langgat."""
    top = K.gas_anchor()
    u = K.unit(top, pin)
    length = K.dist(top, pin)
    er = P.gas_eye_d / 2.0
    w = P.gas_eye_w
    bodies, rods = [], []
    for sx in (-1, 1):
        xc = sx * P.gas_dx
        z_body = er + 6.0                    # vrij van de zeskantkop van de bovenste pen
        body = [cyl_x(P.gas_eye_d, -w / 2.0, w / 2.0, 0, 0).cut(cyl_x(P.pin_hole, -w, w, 0, 0)),
                Part.makeCylinder(5.0, z_body - er + 0.5, V(0, 0, er + 0.5)),
                Part.makeCylinder(P.gas_body_d / 2.0, P.gas_body_len, V(0, 0, z_body))]
        z_rod = z_body + P.gas_body_len + 0.5
        rod = [Part.makeCylinder(P.gas_rod_d / 2.0, length - er - z_rod, V(0, 0, z_rod)),
               cyl_x(P.gas_eye_d, -w / 2.0, w / 2.0, 0, length).cut(cyl_x(P.pin_hole, -w, w, 0, length))]
        origin = (xc, top[0], top[1])
        bodies.append(orient(fuse_all(body), origin, u))
        rods.append(orient(fuse_all(rod), origin, u))
    x0 = -P.gas_dx - w / 2.0 - 1.0
    x1 = P.gas_dx + w / 2.0 + 1.0
    pin_top = bolt_x(P.pin_d, 24, 8.0, 10.0, x0, x1, top[0], top[1])
    return Part.makeCompound(bodies), fuse_all(rods + [pin_top])


def slot_pin(pin):
    """Pen in het langgat, lang genoeg voor de ogen van de gasveren."""
    x0 = -P.gas_dx - P.gas_eye_w / 2.0 - 1.0
    x1 = P.gas_dx + P.gas_eye_w / 2.0 + 1.0
    return bolt_x(P.pin_d, 24, 8.0, 10.0, x0, x1, pin[0], pin[1])


# ---------------------------------------------------------------------
# Parallellogramstang, lokaal: voorste pen in de oorsprong, stang langs -y
# ---------------------------------------------------------------------
def link_local(side):
    s = P.link_tube
    gap = P.hs_link_gap
    x0 = P.hs_x - gap / 2.0
    L = P.link_length
    r = P.link_boss_d / 2.0
    tube = tube_span((P.hs_x - s / 2.0, P.hs_x + s / 2.0), (-L + r - 2, -r + 2), (-s / 2.0, s / 2.0), P.link_wall)
    bosses = [cyl_x(P.link_boss_d, x0, x0 + gap, y, 0.0) for y in (0.0, -L)]
    body = fuse_all([tube] + bosses)
    body = body.cut([cyl_x(P.pin_hole, x0 - 1, x0 + gap + 1, y, 0.0) for y in (0.0, -L)])
    return mirrored_x(body, side)


# ---------------------------------------------------------------------
# Balk + achterframe (bewegen mee bij heffen), coordinaten bij h = 0
# ---------------------------------------------------------------------
def toolbar():
    x0, x1 = P.bar_x
    tube = tube_span((x0, x1), (P.bar_rear, P.bar_front), (P.bar_bot, P.bar_top), P.bar_wall)
    h = P.flange_size / 2.0
    items = [tube]
    for fx in ((x0 - P.flange_t, x0), (x1, x1 + P.flange_t)):
        fl = box_span(fx, (P.bar_y - h, P.bar_y + h), (P.bar_z - h, P.bar_z + h))
        holes = [cyl_x(P.flange_bolt_d + 1.0, fx[0] - 1, fx[1] + 1, P.bar_y + sy * P.flange_hole_off,
                       P.bar_z + sz * P.flange_hole_off) for sy in (-1, 1) for sz in (-1, 1)]
        items.append(fl.cut(holes))
    return fuse_all(items)


def rf_plate(side, inner):
    x0, x1 = hs_cheek_x(inner)
    plate = box_span((x0, x1), P.rf_y, P.rf_z)
    holes = [cyl_x(P.pin_hole, x0 - 1, x1 + 1, P.pin_rear_y, z) for z in (P.pin_upper_z, P.pin_lower_z)]
    return mirrored_x(plate.cut(holes), side)


def rf_cross():
    s = P.rf_cross
    x_in = hs_cheek_x(True)[0]
    tube = tube_span((-x_in, x_in), (P.rf_cross_y - s / 2.0, P.rf_cross_y + s / 2.0),
                     (P.rf_cross_z - s / 2.0, P.rf_cross_z + s / 2.0), 3.0)
    by, bz = P.act_b
    half = P.act_eye_w / 2.0 + 0.5
    y_face = P.rf_cross_y + s / 2.0
    lugs = []
    for sx in (-1, 1):
        x0 = half if sx > 0 else -half - 6.0
        lugs.append(stadium_yz((by, bz), (y_face - 2.0, bz), 12.0, x0, 6.0))
    body = fuse_all([tube] + lugs)
    return body.cut(cyl_x(P.pin_hole, -30, 30, by, bz))


def rf_pins(side):
    x0 = hs_cheek_x(True)[0]
    x1 = hs_cheek_x(False)[1]
    pins = [pin_x(x0, x1, P.pin_rear_y, z) for z in (P.pin_upper_z, P.pin_lower_z)]
    return mirrored_x(Part.makeCompound(pins), side)


def act_b_pin():
    by, bz = P.act_b
    half = P.act_eye_w / 2.0 + 0.5
    return pin_x(-half - 6.0, half + 6.0, by, bz, d=P.pin_d, head_d=24.0, head_t=3.0)


# ---------------------------------------------------------------------
# Actuator tussen pen B (achterframe) en de pen in het langgat (bok), als de toediener
# ---------------------------------------------------------------------
def actuator(body_pin, rod_pin):
    dy, dz = rod_pin[0] - body_pin[0], rod_pin[1] - body_pin[1]
    length = math.hypot(dy, dz)
    u = (dy / length, dz / length)
    eye_r = P.act_eye_d / 2.0
    w = P.act_eye_w
    wr = P.act_rod_eye_w
    tube_end = P.act_retracted - 40.0
    body = [cyl_x(P.act_eye_d, -w / 2.0, w / 2.0, 0, 0).cut(cyl_x(P.pin_hole, -w, w, 0, 0)),
            Part.makeCylinder(7.0, 22.0 - (eye_r - 4.0), V(0, 0, eye_r - 4.0)),
            Part.makeCylinder(P.act_tube_d / 2.0, tube_end - 20.0, V(0, 0, 20.0))]
    mx, my, ml = P.act_motor
    off = P.act_motor_offset
    body.append(box_span((-mx / 2.0, mx / 2.0), (off - my / 2.0, off + my / 2.0), (35.0, 35.0 + ml)))
    body.append(box_span((-mx / 2.0 + 8, mx / 2.0 - 8), (0.0, off), (40.0, 95.0)))
    rod = [Part.makeCylinder(P.act_rod_d / 2.0, length - 16.0 - tube_end, V(0, 0, tube_end)),
           Part.makeCylinder(7.0, 9.0, V(0, 0, length - 18.0)),
           cyl_x(P.act_eye_d, -wr / 2.0, wr / 2.0, 0, length).cut(cyl_x(P.pin_hole, -wr, wr, 0, length))]
    origin = (0.0, body_pin[0], body_pin[1])
    return orient(fuse_all(body), origin, u), orient(fuse_all(rod), origin, u)


# ---------------------------------------------------------------------
# Zaai-element, vast deel (lokaal: x = 0 is het hart van de rij), als de toediener
# ---------------------------------------------------------------------
def u_clamp_plate(front):
    half = P.u_clamp_w / 2.0
    t = P.u_clamp_t
    y = (P.bar_front, P.bar_front + t) if front else (P.bar_rear - t, P.bar_rear)
    plate = box_span((-half, half), y, P.u_clamp_z)
    holes = [cyl(P.u_bolt_d + 0.4, 3 * t, "y", sx * P.u_bolt_dx, (y[0] + y[1]) / 2.0, P.bar_z + sz * P.u_bolt_dz)
             for sx in (-1, 1) for sz in (-1, 1)]
    return plate.cut(holes)


def u_clamp_bolts():
    items = []
    y_head = P.bar_front + P.u_clamp_t
    y_nut = P.bar_rear - P.u_clamp_t
    length = y_head - y_nut + P.u_bolt_m + 3.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            b = bolt_z(P.u_bolt_d, P.u_bolt_af, P.u_bolt_k, length, nut_at=y_head - y_nut, nut_m=P.u_bolt_m)
            b = rotated(b, 90.0, X)
            b.translate(V(sx * P.u_bolt_dx, y_head, P.bar_z + sz * P.u_bolt_dz))
            items.append(b)
    return Part.makeCompound(items)


def u_tongue():
    t = P.u_tongue_t
    x0 = -t / 2.0
    py, pz = P.u_pivot
    ay, az = K.anchor_point()
    y_face = P.bar_rear - P.u_clamp_t
    parts = [box_span((x0, -x0), (y_face - 10.0, y_face), (P.u_clamp_z[0] + 5.0, P.u_clamp_z[1] - 5.0)),
             stadium_yz((y_face - 18.0, P.bar_z), (py, pz), 18.0, x0, t),
             stadium_yz((y_face - 12.0, P.u_clamp_z[1] - 20.0), (ay + 32.0, az - 4.0), 12.0, x0, t)]
    body = fuse_all(parts)
    return body.cut(cyl_x(P.u_pin_d + 0.4, x0 - 1, -x0 + 1, py, pz))


def u_anchor_plate():
    ay, az = K.anchor_point()
    ly, lx, t = P.u_anchor_plate
    plate = box_span((-lx / 2.0, lx / 2.0), (ay - ly / 2.0, ay + ly / 2.0), (az - t / 2.0, az + t / 2.0))
    plate = plate.cut(cyl(P.rod_d + 2.0, 3 * t, "z", 0.0, ay, az))
    return plate.cut(box_span((-P.u_tongue_t / 2.0, P.u_tongue_t / 2.0), (ay + 20.0, ay + ly), (az - 10, az + 10)))


def u_pivot_pin():
    py, pz = P.u_pivot
    xo = P.u_fork_in + P.u_fork_t
    parts = [pin_x(-xo, xo, py, pz, d=P.u_pin_d, head_d=32.0, head_t=4.0)]
    for sx in (-1, 1):
        a, b = sorted((sx * P.u_tongue_t / 2.0, sx * P.u_fork_in))
        parts.append(ring_x(32.0, P.u_pin_d, a, b, py, pz))
    return Part.makeCompound(parts)


def u_strut(drop):
    """Veerpoot tussen de pen op de arm (draait mee) en de veerplaat (vast)."""
    g, u, spring_len = K.strut(drop)
    g_work = K.lug_point(0.0)
    ay, az = K.anchor_point()
    t = P.u_anchor_plate[2]
    dist_work = math.hypot(ay - g_work[0], az - g_work[1])
    nut_bot = dist_work + t / 2.0 + K.stop_gap() + 0.5
    rod_top = nut_bot + 10.0 + 6.0
    eye_r = P.eye_d / 2.0
    rod = [cyl_x(P.eye_d, -P.eye_w / 2.0, P.eye_w / 2.0, 0, 0).cut(cyl_x(P.rod_d + 0.4, -20, 20, 0, 0)),
           Part.makeCylinder(P.rod_d / 2.0, rod_top - eye_r + 2.0, V(0, 0, eye_r - 2.0)),
           hex_prism(19.0, 10.0, z0=P.seat_offset - 10.0),
           hex_prism(19.0, 10.0, z0=nut_bot)]
    seat = Part.makeCylinder(P.seat_d / 2.0, 4.0, V(0, 0, P.seat_offset)).cut(
        Part.makeCylinder(P.rod_d / 2.0, 10.0, V(0, 0, P.seat_offset - 1)))
    rod.append(seat)
    spring = helix_spring(spring_len, (P.spring_od - P.spring_wire) / 2.0, P.spring_wire, coils=8)
    spring.translate(V(0, 0, P.seat_offset + 4.0 + 0.25))
    origin = (0.0, g[0], g[1])
    return orient(fuse_all(rod), origin, u), orient(spring, origin, u)


# ---------------------------------------------------------------------
# Zaai-element, arm (draait om het draaipunt), coordinaten bij drop = 0
# ---------------------------------------------------------------------
def u_fork_plate(side):
    py, pz = P.u_pivot
    g = K.lug_point(0.0)
    d = K.disc_center()
    k = K.rel_disc(P.boot_clamp_rel)
    q = K.pw_pivot()
    t = P.u_fork_t
    x0 = P.u_fork_in if side > 0 else -P.u_fork_in - t
    parts = [stadium_yz((py, pz), g, 16.0, x0, t),
             stadium_yz(g, d, 13.0, x0, t),
             stadium_yz(d, k, 22.0, x0, t),
             stadium_yz(d, q, 14.0, x0, t),
             stadium_yz(k, q, 14.0, x0, t),
             Part.makeCylinder(22.0, t, V(x0, d[0], d[1]), X)]
    body = fuse_all(parts)
    holes = [cyl_x(P.u_pin_d + 0.4, x0 - 1, x0 + t + 1, py, pz),
             cyl_x(P.rod_d + 0.4, x0 - 1, x0 + t + 1, g[0], g[1]),
             cyl_x(P.axle_d + 0.4, x0 - 1, x0 + t + 1, d[0], d[1]),
             cyl_x(12.4, x0 - 1, x0 + t + 1, q[0], q[1])]
    for kb in P.boot_bolt_rel:
        kp = K.rel_disc(kb)
        holes.append(cyl_x(10.4, x0 - 1, x0 + t + 1, kp[0], kp[1]))
    return body.cut(holes)


def u_lug_pin():
    g = K.lug_point(0.0)
    xo = P.u_fork_in + P.u_fork_t
    parts = [pin_x(-xo, xo, g[0], g[1], d=P.rod_d, head_d=20.0, head_t=3.0)]
    for sx in (-1, 1):
        a, b = sorted((sx * P.eye_w / 2.0, sx * P.u_fork_in))
        parts.append(ring_x(20.0, P.rod_d + 0.4, a, b, g[0], g[1]))
    return Part.makeCompound(parts)


def u_axle():
    d = K.disc_center()
    xo = P.u_fork_in + P.u_fork_t
    parts = [cyl_x(P.axle_d, -xo - 2, xo + 18, d[0], d[1])]
    head = rotated(hex_prism(30.0, 13.0, z0=0.0), -90.0, Y)
    head.translate(V(-xo, d[0], d[1]))
    nut = rotated(hex_prism(30.0, 16.0, z0=0.0), 90.0, Y)
    nut.translate(V(xo, d[0], d[1]))
    parts += [head, nut]
    for sx in (-1, 1):
        a, b = sorted((sx * P.hub_half, sx * P.u_fork_in))
        parts.append(ring_x(30.0, P.axle_d + 0.4, a, b, d[0], d[1]))
    return Part.makeCompound(parts)


def u_hub():
    d = K.disc_center()
    hub = ring_x(P.hub_d, P.axle_d, -P.hub_half, P.hub_half, d[0], d[1])
    flanges = [ring_x(90.0, P.hub_d, a, b, d[0], d[1]) for (a, b) in ((-5.5, -P.disc_t / 2.0),
                                                                        (P.disc_t / 2.0, 5.5))]
    return fuse_all([hub] + flanges)


def u_disc():
    d = K.disc_center()
    h = P.disc_t / 2.0
    r = P.disc_d / 2.0
    r_in = P.hub_d / 2.0 + 1.0
    pts = [V(-h, r_in, 0), V(h, r_in, 0), V(h, r - 9.0, 0), V(0.3, r, 0), V(-0.3, r, 0), V(-h, r - 9.0, 0)]
    pts.append(pts[0])
    disc = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), X, 360)
    holes = []
    for i in range(6):
        a = math.radians(60 * i + 30)
        holes.append(cyl_x(30.0, -5, 5, 62.0 * math.cos(a), 62.0 * math.sin(a)))
    disc = disc.cut(holes)
    disc.translate(V(0, d[0], d[1]))
    return disc


def u_band(side):
    """Dieptering PE-HD O 270 aan een kant van de schijf (binnen O 170, buiten de naafflens O 90)."""
    d = K.disc_center()
    x0 = P.disc_t / 2.0
    x1 = x0 + P.band_w
    ro = P.band_d / 2.0
    ri = P.band_r_in
    pts = [V(x0, ri, 0), V(x1, ri, 0), V(x1, ro - 5.0, 0), V(x1 - 4.0, ro, 0), V(x0, ro, 0)]
    pts.append(pts[0])
    band = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), X, 360)
    if side < 0:
        band = mirror_x(band)
    band.translate(V(0, d[0], d[1]))
    return band


def u_seed_boot():
    """Gebogen zaaikouter 16 mm met de zaadbuis erin gelast (1 deel)."""
    pts = [K.rel_disc(p) for p in K.boot_points()]
    t = P.boot_t
    boot = poly_yz(pts, -t / 2.0, t)
    boot = boot.cut([cyl_x(10.4, -t, t, *K.rel_disc(kb)) for kb in P.boot_bolt_rel])
    b = K.seed_tube_bottom()
    tube = Part.makeCylinder(P.seed_tube_od / 2.0, P.seed_tube_top_z - b[1], V(0, b[0], b[1])).cut(
        Part.makeCylinder(P.seed_tube_id / 2.0, P.seed_tube_top_z - b[1] + 2.0, V(0, b[0], b[1] - 1.0)))
    return fuse_all([boot, tube])


def u_boot_hardware():
    xo = P.u_fork_in + P.u_fork_t
    items = []
    for kb in P.boot_bolt_rel:
        y, z = K.rel_disc(kb)
        items.append(cyl_x(10.0, -xo - 1, xo + 9.4, y, z))
        head = rotated(hex_prism(17.0, 6.4, z0=0.0), -90.0, Y)
        head.translate(V(-xo, y, z))
        nut = rotated(hex_prism(17.0, 8.4, z0=0.0), 90.0, Y)
        nut.translate(V(xo, y, z))
        items += [head, nut]
        for sx in (-1, 1):
            a, b = sorted((sx * P.boot_t / 2.0, sx * P.u_fork_in))
            items.append(ring_x(20.0, 10.4, a, b, y, z))
    return Part.makeCompound(items)


def u_pw_pivot_bolts():
    """2 schouderbouten M12 van buitenaf door de gaffel in een moer die op de vorkplaat is gelast."""
    q = K.pw_pivot()
    items = []
    for sx in (-1, 1):
        x_in = P.u_fork_in
        x_out = P.pw_yoke_x[1] + 9.5                      # ruimte voor de torsieveer tussen gaffel en kop
        shank = cyl_x(12.0, x_in, x_out, q[0], q[1])
        head = rotated(hex_prism(19.0, 7.5, z0=0.0), 90.0, Y)
        head.translate(V(x_out, q[0], q[1]))
        items.append(mirrored_x(fuse_all([shank, head]), sx))
    return Part.makeCompound(items)


def u_pw_yoke():
    """Gaffel van de aandrukrol: 2 strips 30 x 5 aan de buitenkant van de vorkplaten (werkstand, chi = 0)."""
    q = K.pw_pivot()
    a = K.pw_axle(0.0)
    x0, x1 = P.pw_yoke_x
    items = []
    for sx in (-1, 1):
        plate = stadium_yz(q, a, P.pw_yoke_w / 2.0, x0, x1 - x0)
        plate = plate.cut([cyl_x(12.4, x0 - 1, x1 + 1, q[0], q[1]), cyl_x(P.pw_axle_d + 0.4, x0 - 1, x1 + 1, a[0], a[1])])
        items.append(mirrored_x(plate, sx))
    return Part.makeCompound(items)


def u_pw_axle():
    a = K.pw_axle(0.0)
    x1 = P.pw_yoke_x[1]
    bolt = bolt_x(P.pw_axle_d, 24, 10.0, 13.0, -x1, x1, a[0], a[1])
    spacers = [ring_x(26.0, P.pw_axle_d + 0.5, P.pw_w / 2.0, P.pw_yoke_x[0], a[0], a[1]),
               ring_x(26.0, P.pw_axle_d + 0.5, -P.pw_yoke_x[0], -P.pw_w / 2.0, a[0], a[1])]
    return fuse_all([bolt] + spacers)


def u_press_wheel():
    """(band, velg): massief rubber O 200 x 40."""
    y, z = K.pw_axle(0.0)
    x0, x1 = -P.pw_w / 2.0, P.pw_w / 2.0
    tire = ring_x(P.pw_d, 130.0, x0, x1, y, z)
    try:
        tire = tire.makeFillet(8.0, [e for e in tire.Edges if hasattr(e.Curve, "Radius") and e.Curve.Radius > P.pw_d / 2.0 - 1.0])
    except Exception:
        pass
    rim = fuse_all([ring_x(130.0, 110.0, x0 + 2.0, x1 - 2.0, y, z), ring_x(110.0, P.pw_hub_d, -3.0, 3.0, y, z),
                    ring_x(P.pw_hub_d, P.pw_axle_d + 0.5, x0, x1, y, z)])
    return tire, rim


def u_pw_spring():
    """Torsieveer om de rechter schouderbout, tussen gaffel en kop (benen niet getekend)."""
    q = K.pw_pivot()
    x0 = P.pw_yoke_x[1] + 0.5
    s = helix_spring(8.5, 10.5, 3.0, coils=2.0)
    s = rotated(s, 90.0, Y)
    s.translate(V(x0, q[0], q[1]))
    return s


# ---------------------------------------------------------------------
# Luchtzaaier op de robot (vast aan de bok en de binnenste achterbalk)
# ---------------------------------------------------------------------
def seed_frame():
    """Draagframe koker 40 x 40 x 3 met poten: achter platen op de bok, voor kokers op de binnenste achterbalk."""
    (x0, x1), (y0, y1), (z0, z1) = P.sf_x, P.sf_y, P.sf_z
    s = P.sf_tube
    w = 3.0
    items = [tube_span((x0, x1), (y0, y0 + s), (z0, z1), w), tube_span((x0, x1), (y1 - s, y1), (z0, z1), w),
             tube_span((x0, x1), (110.0, 150.0), (z0, z1), w)]
    for xs in ((x0, x0 + s), (x1 - s, x1)):
        items.append(tube_span(xs, (y0 + s, y1 - s), (z0, z1), w))
    z_plate = P.robot_beam_z_top + P.plate_t
    for sx in (-1, 1):
        lx = P.sf_rear_leg_x if sx > 0 else (-P.sf_rear_leg_x[1], -P.sf_rear_leg_x[0])
        items.append(box_span(lx, P.sf_rear_leg_y, (z_plate, z0)))
        fx = P.sf_front_leg_x if sx > 0 else (-P.sf_front_leg_x[1], -P.sf_front_leg_x[0])
        items.append(tube_span(fx, P.sf_front_leg_y, (P.robot_beam_z_top, z0), w))
        items.append(box_span(fx, (P.sf_front_leg_y[0] - 10.0, P.sf_front_leg_y[1] + 10.0),
                              (P.robot_beam_z_top, P.robot_beam_z_top + 6.0)))
    # zadels onder het luchtkanaal
    for xs in (-200.0, 200.0):
        items.append(box_span((xs - 20.0, xs + 20.0), (P.duct_y - 25.0, P.duct_y + 25.0),
                              (z1, P.duct_z - P.duct_d / 2.0 + 4.0)).cut(cyl_x(P.duct_d, xs - 30, xs + 30, P.duct_y, P.duct_z)))
    return fuse_all(items)


def air_duct():
    """Luchtkanaal PVC O 60 met 8 venturi-nippels naar achteren en eindkap."""
    x0, x1 = P.duct_x
    r = P.duct_d / 2.0
    body = [ring_x(P.duct_d, P.duct_d - 6.0, x0, x1, P.duct_y, P.duct_z), cyl_x(P.duct_d, x1, x1 + 4.0, P.duct_y, P.duct_z)]
    for x in P.outlet_x:
        body.append(Part.makeCylinder(P.outlet_d / 2.0, P.outlet_len, V(x, P.duct_y - r + 4.0, P.duct_z),
                                      V(0, -1, 0)))
        body.append(Part.makeCylinder(P.drop_d / 2.0, P.meter_z[0] - P.duct_z, V(x, P.duct_y, P.duct_z)))
    return fuse_all(body)


def outlet_end(x):
    return (x, P.duct_y - P.duct_d / 2.0 - P.outlet_len + 4.0, P.duct_z)


def meter_housing():
    body = box_span(P.meter_x, P.meter_y, P.meter_z)
    return body


def meter_motors():
    bx, by, bz = P.motor_box
    out = []
    for side, sy in ((1, P.shaft_main_y), (-1, P.shaft_fine_y)):
        xe = P.meter_x[1] if side > 0 else P.meter_x[0]
        xb = (xe, xe + bx) if side > 0 else (xe - bx, xe)
        gear = box_span(xb, (sy - by / 2.0, sy + by / 2.0), (P.shaft_z - 22.0, P.shaft_z - 22.0 + bz))
        xc = 0.5 * (xb[0] + xb[1])
        motor = Part.makeCylinder(P.motor_d / 2.0, P.motor_len, V(xc, sy, P.shaft_z - 22.0 + bz))
        out.append(fuse_all([gear, motor]))
    return out


def _offset_poly(points, w):
    plates = []
    for (y0, z0), (y1, z1) in zip(points[:-1], points[1:]):
        L = math.hypot(y1 - y0, z1 - z0)
        ny, nz = -(z1 - z0) / L, (y1 - y0) / L
        plates.append([(y0, z0), (y1, z1), (y1 + ny * w, z1 + nz * w), (y0 + ny * w, z0 + nz * w)])
    return plates


def hopper():
    o = K.hopper_outline()
    w = P.hop_wall
    x0, x1 = P.hop_x
    items = []
    for chain in ([o[0], o[1], o[2]], [o[3], o[4], o[5]]):
        for quad in _offset_poly(chain, -w):
            items.append(poly_yz(quad, x0, x1 - x0))
    for ex in ((x0, x0 + w), (x1 - w, x1)):
        items.append(poly_yz(o, ex[0], w))
    db, dt = P.hop_divider
    L = K.dist(db, dt)
    nd = ((dt[1] - db[1]) / L, -(dt[0] - db[0]) / L)
    items.append(poly_yz([db, dt, (dt[0] + nd[0] * w, dt[1] + nd[1] * w), (db[0] + nd[0] * w, db[1] + nd[1] * w)],
                         x0 + w, x1 - x0 - 2 * w))
    return fuse_all(items).common(box_span((x0 - 1, x1 + 1), (P.hop_y[0] - 10, P.hop_y[1] + 10),
                                           (P.meter_z[1], P.hop_top_z)))


def hopper_posts():
    """2 steunplaten van het draagframe (dwarsbuis en voorste buis) naar de schuine bodem van de zaadbak."""
    o = K.hopper_outline()
    (y1, z1), (y0, z0) = o[1], o[2]

    def z_slope(y):
        return z0 + (y - y0) * (z1 - z0) / (y1 - y0)
    ya, yb = 165.0, P.sf_y[1]
    pts = [(ya, P.sf_z[1]), (yb, P.sf_z[1]), (yb, z_slope(yb)), (ya, z_slope(ya))]
    items = []
    for sx in (-1, 1):
        x0 = sx * P.hop_post_x - P.hop_post_t / 2.0
        items.append(poly_yz(pts, x0, P.hop_post_t))
    return Part.makeCompound(items)


def hopper_lid():
    x0, x1 = P.hop_x
    y0, y1 = P.hop_y
    return box_span((x0 - 5.0, x1 + 5.0), (y0 - 5.0, y1 + 5.0), (P.hop_top_z, P.hop_top_z + P.lid_t))


def fan():
    """(ventilator met motor en uitlaat naar -x, persleiding O 50 naar het open eind van het luchtkanaal)."""
    fx, fy = P.fan_xy
    z0 = P.sf_z[1]
    zc = z0 + 50.0
    xs = fx - P.fan_d / 2.0 - 25.0
    body = fuse_all([Part.makeCylinder(P.fan_d / 2.0, P.fan_h, V(fx, fy, z0 + 6.0)),
                     box_span((fx - 60.0, fx + 60.0), (fy - 60.0, fy + 60.0), (z0, z0 + 6.0)),
                     Part.makeCylinder(30.0, 40.0, V(fx, fy, z0 + 6.0 + P.fan_h)),
                     cyl_x(P.fan_outlet_d, xs, fx - P.fan_d / 2.0 + 20.0, fy, zc)])
    end = (P.duct_x[0], P.duct_y, P.duct_z)
    pipe = hose([(xs, fy, zc), (xs - 40.0, fy, zc), (end[0] - 45.0, fy - 60.0, zc), (end[0] - 45.0, P.duct_y, end[2]),
                 (end[0] - 20.0, P.duct_y, end[2]), end], P.fan_outlet_d)
    return body, pipe


def control_box():
    z0 = P.sf_z[1]
    return box_span((120.0, 250.0), (110.0, 215.0), (z0, z0 + 70.0))


def seed_hose(row_x, x_out, drop=0.0, h=0.0):
    """Zaadslang 20/26 van de venturi (op de robot) naar de bovenkant van de zaadbuis (element, draait mee)."""
    s = outlet_end(x_out)
    b = K.seed_tube_bottom()
    top = K.rot_yz((b[0], P.seed_tube_top_z), drop, P.u_pivot)
    up = K.rot_yz((b[0], P.seed_tube_top_z + 45.0), drop, P.u_pivot)
    dy, dz = K.bar_shift(h)
    lane = row_x + P.hose_lane_dx
    t = (row_x, top[0] + dy, top[1] + dz)
    u = (row_x, up[0] + dy, up[1] + dz)
    pts = [s, (x_out, s[1] - 60.0, s[2]),
           (0.5 * (x_out + lane), -300.0, P.hose_high_z),
           (lane, -640.0 + dy, P.hose_high_z),
           (lane, u[1] + 40.0, u[2] + 120.0),
           (row_x, u[1], u[2]),
           t]
    return hose(pts, P.seed_hose_od)


# ---------------------------------------------------------------------
# Referentie robot (alleen ter controle)
# ---------------------------------------------------------------------
def robot_beam_x(y):
    p = P.robot_beam_profile
    half = P.robot_beam_length / 2.0
    zc = P.robot_beam_z_bot + p / 2.0
    t = tube_span((-half, half), (y - p / 2.0, y + p / 2.0), (P.robot_beam_z_bot, P.robot_beam_z_top),
                  P.robot_beam_wall)
    holes = []
    x = P.robot_hole_x_min
    while x <= P.robot_hole_x_max + 1e-6:
        holes += [cyl(P.robot_hole_d, p + 10, "z", x, y, zc), cyl(P.robot_hole_d, p + 10, "z", -x, y, zc)]
        x += P.robot_grid
    return t.cut(holes)


def robot_upper_beams():
    p = P.robot_beam_profile
    items = []
    for xc in P.robot_upper_beam_x:
        for sx in (-1, 1):
            x = sx * xc
            items.append(tube_span((x - p / 2.0, x + p / 2.0), (P.robot_upper_beam_y_rear, P.robot_upper_beam_y_front),
                                   (P.robot_beam_z_top, P.robot_upper_beam_z_top), P.robot_beam_wall))
    return Part.makeCompound(items)


def robot_wheel_unit(side):
    x = side * P.robot_wheel_x
    y = P.robot_wheel_y
    z = P.robot_axle_z
    tire = cyl_x(P.robot_tire_d, x - P.robot_tire_w / 2.0, x + P.robot_tire_w / 2.0, y, z)
    try:
        tire = tire.makeFillet(25.0, tire.Edges)
    except Exception:
        pass
    half_w = P.robot_bracket_w / 2.0
    half_l = P.robot_bracket_l / 2.0
    plates = [box_span((x + s * half_w - (4.0 if s > 0 else 0.0), x + s * half_w + (0.0 if s > 0 else 4.0)),
                       (y - half_l, y + half_l), (z - 40.0, P.robot_bracket_plate_z)) for s in (-1, 1)]
    top = box_span((x - half_w, x + half_w), (y - half_l, y + half_l), (P.robot_bracket_plate_z, P.robot_bracket_top_z))
    block = box_span((x - P.robot_block_w / 2.0, x + P.robot_block_w / 2.0),
                     (y - P.robot_block_l / 2.0, y + P.robot_block_l / 2.0), (P.robot_bracket_top_z, P.robot_beam_z_bot))
    return tire, fuse_all(plates + [top, block])
