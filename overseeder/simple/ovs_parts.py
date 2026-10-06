import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ovs_params as P
import ovs_kin as K

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basisfuncties (zelfde stijl als ../liquid fertilizer applicator/simple_v2/lfs2_parts.py)
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
    # lokaal z -> u (in het y-z vlak), lokaal x -> x, lokaal y -> (uz, -uy) (rechtshandig)
    uy, uz = u
    return App.Matrix(1, 0, 0, origin[0],
                      0, uz, uy, origin[1],
                      0, -uy, uz, origin[2],
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
    """Bout langs +x: kop tegen x0 (kant -x), moer tegen x1, schacht steekt extra door."""
    length = x1 - x0 + m + extra
    b = bolt_z(d, af, k, length, nut_at=x1 - x0, nut_m=m)
    b = rotated(b, 90.0, Y)
    b.translate(V(x0, y, z))
    return b


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


def to_disc(shape):
    """Vorm getekend in schijfcoordinaten (x_l, y = hart schijf + y_l, z) -> scheef element (7 graden om z)."""
    return rotated(shape, P.disc_angle, Z, V(0, P.disc_center[0], 0))


def ubolts(cx, legs_y, z_top, z_nut, d, nut_af, nut_m):
    """Vierkante beugelbouten over de bovenkant van de balk: benen omlaag op legs_y, moer onder z_nut."""
    r = d / 2.0
    items = []
    for x in cx:
        y0, y1 = legs_y
        z_end = z_nut - nut_m - 4.0
        parts = [Part.makeCylinder(r, z_top - z_end, V(x, y, z_end)) for y in (y0, y1)]
        parts.append(Part.makeCylinder(r, abs(y1 - y0), V(x, min(y0, y1), z_top), Y))
        parts += [Part.makeSphere(r, V(x, y, z_top)) for y in (y0, y1)]
        parts += [hex_prism(nut_af, nut_m, z0=z_nut - nut_m, cx=x, cy=y) for y in (y0, y1)]
        items.append(fuse_all(parts))
    return Part.makeCompound(items)


# ---------------------------------------------------------------------
# Aanbouwbok (vast aan de robotbalk), 1 gelast deel: als simple_v2, armen op x = +-62.5
# ---------------------------------------------------------------------
def cheek_x(inner):
    half = P.bush_len / 2.0 + 1.0
    c = P.arm_x
    return (c - half - P.hs_cheek_t, c - half) if inner else (c + half, c + half + P.hs_cheek_t)


def hs_top_plate():
    z0 = P.robot_beam_z_top
    plate = box_span((-P.hs_top_x, P.hs_top_x), P.hs_top_y, (z0, z0 + P.hs_top_t))
    holes = [cyl(P.robot_hole_d, 3 * P.hs_top_t, "z", sx * x, 0.0, z0 + P.hs_top_t / 2.0)
             for x in P.hs_bolt_x for sx in (-1, 1)]
    return plate.cut(holes)


def hs_clamp_strip():
    z1 = P.robot_beam_z_bot
    plate = box_span((-P.hs_top_x, P.hs_top_x), P.hs_clamp_y, (z1 - P.hs_clamp_t, z1))
    holes = [cyl(P.robot_hole_d, 3 * P.hs_clamp_t, "z", sx * x, 0.0, z1 - P.hs_clamp_t / 2.0)
             for x in P.hs_bolt_x for sx in (-1, 1)]
    return plate.cut(holes)


def hs_cheeks():
    items = []
    for side in (-1, 1):
        for inner in (True, False):
            x0, x1 = cheek_x(inner)
            plate = box_span((x0, x1), P.hs_cheek_y, (P.hs_cheek_z_bot, P.robot_beam_z_top))
            plate = plate.cut(cyl_x(P.pivot_bolt_d + 0.5, x0 - 1, x1 + 1, *P.pivot))
            items.append(mirrored_x(plate, side))
    return Part.makeCompound(items)


def lug_x(sx):
    """x-bereik van een oog (sx = -1 / +1) naast het hart van de actuator."""
    return (P.act_x + P.act_lug_gap / 2.0, P.act_x + P.act_lug_gap / 2.0 + P.act_lug_t) if sx > 0 else \
        (P.act_x - P.act_lug_gap / 2.0 - P.act_lug_t, P.act_x - P.act_lug_gap / 2.0)


def hs_act_lugs():
    """2 langgatplaten op de bovenplaat: het stangoog van de actuator schuift in het langgat (zweefstand); de
    platen lopen door tot de bovenste pen van de gasveren."""
    lo, hi = K.slot_ends()
    top = K.gas_anchor()
    u = K.slot_dir()
    nf = (u[1], -u[0])
    r = 16.0
    z0 = P.robot_beam_z_top + P.hs_top_t
    p_lo = K.add(lo, nf, r)
    p_top = K.add(top, nf, r)
    items = []
    for sx in (-1, 1):
        x0 = lug_x(sx)[0]
        base = poly_yz([p_lo, (p_lo[0], z0), (max(p_top[0] + 20.0, P.hs_top_y[0] + 40.0), z0), p_top], x0, P.act_lug_t)
        body = fuse_all([stadium_yz(lo, top, r, x0, P.act_lug_t), base])
        body = body.cut(stadium_yz(lo, hi, P.act_pin_hole / 2.0, x0 - 1, P.act_lug_t + 2))
        items.append(body.cut(cyl_x(P.act_pin_hole, x0 - 1, x0 + P.act_lug_t + 1, *top)))
    return Part.makeCompound(items)


def gas_springs(pin):
    """(huizen, stangen + pen bovenaan): 2 gasveren van de bovenste pen naar de pen in het langgat."""
    top = K.gas_anchor()
    u = K.unit(top, pin)                     # van boven naar het oog in het langgat
    length = K.dist(top, pin)
    er = P.gas_eye_d / 2.0
    bodies, rods = [], []
    for sx in (-1, 1):
        xc = P.act_x + sx * P.gas_dx
        w = P.gas_eye_w
        body = [cyl_x(P.gas_eye_d, -w / 2.0, w / 2.0, 0, 0).cut(cyl_x(P.act_pin_hole, -w, w, 0, 0)),
                Part.makeCylinder(P.gas_body_d / 2.0, P.gas_body_len, V(0, 0, er + 3.0)),
                Part.makeCylinder(5.0, 5.0, V(0, 0, er - 1.0))]
        rod_z0 = er + 3.0 + P.gas_body_len
        rod = [Part.makeCylinder(P.gas_rod_d / 2.0, length - er + 2.0 - rod_z0, V(0, 0, rod_z0)),
               cyl_x(P.gas_eye_d, -w / 2.0, w / 2.0, 0, length).cut(cyl_x(P.act_pin_hole, -w, w, 0, length))]
        origin = (xc, top[0], top[1])
        bodies.append(orient(fuse_all(body), origin, u))
        rods.append(orient(fuse_all(rod), origin, u))
    x0 = P.act_x - P.gas_dx - P.gas_eye_w / 2.0 - 1.0
    x1 = P.act_x + P.gas_dx + P.gas_eye_w / 2.0 + 1.0
    pin_top = bolt_x(P.act_pin_d, 16, 6.4, 8.0, x0, x1, top[0], top[1])
    return Part.makeCompound(bodies), fuse_all(rods + [pin_top])


def hs_bolts():
    items = []
    z_head = P.robot_beam_z_top + P.hs_top_t
    length = z_head - (P.robot_beam_z_bot - P.hs_clamp_t) + P.m10_m + 3.0
    for x in P.hs_bolt_x:
        for sx in (-1, 1):
            b = bolt_z(P.m10_d, P.m10_af, P.m10_k, length, nut_at=length - P.m10_m - 3.0, nut_m=P.m10_m)
            b = rotated(b, 180.0, X)
            b.translate(V(sx * x, 0.0, z_head))
            items.append(b)
    return Part.makeCompound(items)


def hs_pivot_bolts():
    items = []
    for side in (-1, 1):
        x0 = cheek_x(True)[0]
        x1 = cheek_x(False)[1]
        b = bolt_x(P.pivot_bolt_d, P.pivot_bolt_af, P.pivot_bolt_k, P.pivot_bolt_m, x0, x1, *P.pivot)
        items.append(mirrored_x(b, side))
    return Part.makeCompound(items)


def control_box():
    """Kastje met de 2 motorregelaars en de relais voor de actuator, op de bovenplaat van de bok (rechts)."""
    z0 = P.robot_beam_z_top + P.hs_top_t
    body = box_span((60.0, 190.0), (-118.0, -22.0), (z0, z0 + 70.0))
    gland = cyl(16.0, 14.0, "y", 165.0, -125.0, z0 + 25.0)
    return fuse_all([body, gland])


def act_pin_bolt(pin, gap, gas=False):
    """Pen M10 door twee ogen (binnenmaat gap); gas = True: lange pen die ook door de ogen van de gasveren gaat."""
    if gas:
        x0 = P.act_x - P.gas_dx - P.gas_eye_w / 2.0 - 1.0
        x1 = P.act_x + P.gas_dx + P.gas_eye_w / 2.0 + 1.0
    else:
        x0 = P.act_x - gap / 2.0 - P.act_lug_t
        x1 = P.act_x + gap / 2.0 + P.act_lug_t
    return bolt_x(P.act_pin_d, 16, 6.4, 8.0, x0, x1, pin[0], pin[1])


# ---------------------------------------------------------------------
# Hefraam (draait om de draaibouten), coordinaten in werkstand
# ---------------------------------------------------------------------
def bar():
    """Balk 60 x 60 x 4 met aan beide kanten een koppelflens 100 x 100 x 8 (4 gaten M12)."""
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


def arms():
    p0, p1, u = K.arm_axis()
    length = K.dist(p0, p1) + 30.0
    s = P.arm_size / 2.0
    w = P.arm_wall
    local = box_span((-s, s), (-s, s), (0.0, length)).cut(box_span((-s + w, s - w), (-s + w, s - w), (-1.0, length + 1)))
    items = []
    for side in (-1, 1):
        x = side * P.arm_x
        tube = orient(moved(local, x=x), (0.0, p0[0], p0[1]), u)
        tube = tube.cut(box_span((x - 50, x + 50), (P.bar_front - 200.0, P.bar_front), (0.0, 800.0)))
        bush = ring_x(P.bush_od, P.bush_id, x - P.bush_len / 2.0, x + P.bush_len / 2.0, *P.pivot)
        tube = tube.cut(cyl_x(P.bush_od - 1.0, x - 30, x + 30, *P.pivot))
        items.append(fuse_all([tube, bush]))
    return Part.makeCompound(items)


def cross_tube():
    """Dwarsbuis (verstijving) tussen de armen."""
    cy, cz = K.cross_center()
    s = P.cross_size / 2.0
    xi = P.arm_x - P.arm_size / 2.0
    return tube_span((-xi, xi), (cy - s, cy + s), (cz - s, cz + s), P.cross_wall)


def frame_act_lugs():
    """2 ogen bovenop het midden van de balk voor de pen van het actuatorhuis."""
    ly, lz = P.act_l
    r = 16.0
    items = []
    for sx in (-1, 1):
        x0 = lug_x(sx)[0]
        body = fuse_all([cyl_x(2 * r, x0, x0 + P.act_lug_t, ly, lz),
                         box_span((x0, x0 + P.act_lug_t), (ly - r, ly + r), (P.bar_top, lz))])
        items.append(body.cut(cyl_x(P.act_pin_hole, x0 - 1, x0 + P.act_lug_t + 1, ly, lz)))
    return Part.makeCompound(items)


# ---------------------------------------------------------------------
# Actuator tussen de bok en de balk
# ---------------------------------------------------------------------
def actuator(body_pin, rod_pin):
    """Geeft (huis, stang): huis met parallelle motor op body_pin (hefraam), stang naar rod_pin (langgat)."""
    length = K.dist(body_pin, rod_pin)
    u = K.unit(body_pin, rod_pin)
    er = P.act_eye_d / 2.0
    w = P.act_eye_w
    tube_end = P.act_retracted - 25.0
    g0 = 30.0
    md = P.act_motor_d
    off = P.act_motor_offset
    body = [cyl_x(P.act_eye_d, -w / 2.0, w / 2.0, 0, 0).cut(cyl_x(P.act_pin_hole, -w, w, 0, 0)),
            Part.makeCylinder(8.0, g0 + 2.0 - (er - 4.0), V(0, 0, er - 4.0)),
            box_span((-20.0, 20.0), (-off - md / 2.0, 20.0), (g0, g0 + 42.0)),
            Part.makeCylinder(P.act_tube_d / 2.0, tube_end - g0 - 40.0, V(0, 0, g0 + 40.0)),
            Part.makeCylinder(md / 2.0, P.act_motor_len, V(0, -off, g0 + 40.0))]
    rod = [Part.makeCylinder(P.act_rod_d / 2.0, length - 14.0 - tube_end, V(0, 0, tube_end)),
           Part.makeCylinder(8.0, 8.0, V(0, 0, length - 18.0)),
           cyl_x(P.act_eye_d, -w / 2.0, w / 2.0, 0, length).cut(cyl_x(P.act_pin_hole, -w, w, 0, length))]
    origin = (P.act_x, body_pin[0], body_pin[1])
    return orient(fuse_all(body), origin, u), orient(fuse_all(rod), origin, u)


# ---------------------------------------------------------------------
# Zaai-element: houder (vast aan de balk), lokaal x = 0 is het hart van de schijf
# ---------------------------------------------------------------------
def u_cheek_x():
    a0, a1 = P.u_arm_x
    g, t = P.u_cheek_gap, P.u_cheek_t
    return (a0 - g - t, a0 - g), (a1 + g, a1 + g + t)


def ubolt_legs_y():
    r = P.ubolt_d / 2.0
    return (P.bar_front + r, P.bar_rear - r)


def u_holder():
    """Gelaste houder: klemplaat onder de balk, 2 wangen naar het draaipunt, veertoren met ankerplaat."""
    z1 = P.bar_bot
    z0 = z1 - P.u_clamp_t
    plate = box_span(P.u_clamp_x, P.u_clamp_y, (z0, z1))
    plate = plate.cut([cyl(P.ubolt_d + 1.0, 3 * P.u_clamp_t, "z", x, y, z0 + P.u_clamp_t / 2.0)
                       for x in P.ubolt_x for y in ubolt_legs_y()])
    cheeks = []
    for cx in u_cheek_x():
        c = box_span(cx, P.u_cheek_y, (P.u_cheek_z_bot, z0))
        cheeks.append(c.cut(cyl_x(P.u_pin_d + 0.5, cx[0] - 1, cx[1] + 1, *P.u_pivot)))
    tower = box_span(P.u_tower_x, P.u_tower_y, (z0, P.u_anchor_z[1]))
    anchor = box_span(P.u_tower_x, P.u_anchor_y, P.u_anchor_z)
    ay, az = K.u_anchor_point()
    ax = 0.5 * (P.u_arm_x[0] + P.u_arm_x[1])
    anchor = anchor.cut(cyl(P.rod_d + 1.0, 30.0, "z", ax, ay, az))
    return fuse_all([plate, tower, anchor] + cheeks)


def u_ubolts():
    r = P.ubolt_d / 2.0
    return ubolts(P.ubolt_x, ubolt_legs_y(), P.bar_top + r, P.bar_bot - P.u_clamp_t,
                  P.ubolt_d, P.ubolt_nut_af, P.ubolt_nut_m)


def u_pivot_bolt():
    (c0, _), (_, c1) = u_cheek_x()
    return bolt_x(P.u_pin_d, 24, 10.0, 13.0, c0, c1, *P.u_pivot)


# ---------------------------------------------------------------------
# Zaai-element: sleeparm met alles wat meedraait (in werkstand, phi = 0)
# ---------------------------------------------------------------------
def disc_axis_cyl(d, xl0, xl1):
    """Cilinder langs de (scheve) as van de schijf, van x_l = xl0 tot xl1, in elementcoordinaten."""
    cy, cz = P.disc_center
    return to_disc(cyl_x(d, min(xl0, xl1), max(xl0, xl1), cy, cz))


def hub_x():
    """x_l-bereiken (flens, naaf) aan de schaduwkant (-x)."""
    h = P.disc_t / 2.0
    f = (-h - P.hub_flange_t, -h)
    n = (f[0] - P.hub_len, f[0])
    return f, n


def u_arm():
    """Gelaste arm: koker 30 x 30 x 3, draaibus, twee ogen voor de veerpoot, schuine bus voor de schijfas en de
    gat voor het scharnier van de rolarm."""
    u = K.u_arm_dir()
    p0 = P.u_pivot
    a0, a1 = P.u_arm_x
    ac = 0.5 * (a0 + a1)
    s = P.u_arm_size / 2.0
    w = P.u_arm_wall
    length = (P.u_arm_y_end - p0[0]) / u[0]
    local = box_span((a0, a1), (-s, s), (0.0, length)).cut(box_span((a0 + w, a1 - w), (-s + w, s - w), (-1.0, length + 1)))
    tube = orient(local, (0.0, p0[0], p0[1]), u)
    tube = tube.cut(cyl_x(P.u_bush_od - 1.0, a0 - 1, a1 + 1, *p0))
    bush = ring_x(P.u_bush_od, P.u_bush_id, a0, a1, *p0)
    # ogen veerpoot
    g = K.u_lug_point()
    top = K.u_arm_z(P.u_lug_y) + s
    lugs = []
    for sx in (-1, 1):
        x0 = ac + P.eye_w / 2.0 + 0.5 if sx > 0 else ac - P.eye_w / 2.0 - 0.5 - P.u_lug_t
        lug = fuse_all([cyl_x(26.0, x0, x0 + P.u_lug_t, *g),
                        box_span((x0, x0 + P.u_lug_t), (g[0] - 13.0, g[0] + 13.0), (top - 2.0, g[1]))])
        lugs.append(lug.cut(cyl_x(10.5, x0 - 1, x0 + P.u_lug_t + 1, *g)))
    # schuine bus tussen naaf en arm (zet de schijf op 7 graden)
    f, n = hub_x()
    boss = disc_axis_cyl(P.boss_d, n[0], n[0] - 20.0).common(box_span((a1, a1 + 20.0), (-2000, 0), (0, 400)))
    body = fuse_all([tube, bush, boss] + lugs)
    lp = K.pw_link_pivot()
    body = body.cut(cyl_x(P.pw_link_bolt_d + 0.5, a0 - 1, a1 + 1, *lp))
    return body.cut(disc_axis_cyl(P.stub_d + 0.5, 10.0, -120.0))


def u_disc():
    """Vlakke kouterschijf O 300 x 4 met geslepen rand, middengat en 4 boutgaten, 7 graden scheef."""
    cy, cz = P.disc_center
    h = P.disc_t / 2.0
    r = P.disc_d / 2.0
    r_in = P.disc_center_hole / 2.0
    pts = [V(-h, r_in, 0), V(h, r_in, 0), V(h, r - 10.0, 0), V(0.3, r, 0), V(-0.3, r, 0), V(-h, r - 10.0, 0)]
    pts.append(pts[0])
    body = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), X, 360)
    holes = []
    for i in range(4):
        a = math.radians(90 * i + 45)
        holes.append(cyl_x(8.5, -5, 5, P.disc_bolt_r * math.cos(a), P.disc_bolt_r * math.sin(a)))
    body = body.cut(holes)
    body.translate(V(0, cy, cz))
    return to_disc(body)


def u_hub():
    """Lagernaaf met flens aan de schaduwkant, 4 bouten M8 met de koppen aan de andere kant."""
    cy, cz = P.disc_center
    f, n = hub_x()
    h = P.disc_t / 2.0
    items = [ring_x(P.hub_flange_d, P.stub_d + 0.5, f[0], f[1], cy, cz),
             ring_x(P.hub_d, P.stub_d + 0.5, n[0], n[1], cy, cz)]
    for i in range(4):
        a = math.radians(90 * i + 45)
        y, z = cy + P.disc_bolt_r * math.cos(a), cz + P.disc_bolt_r * math.sin(a)
        items += [cyl_x(13.0, h, h + 5.0, y, z), cyl_x(8.0, -h, h, y, z)]
    return to_disc(fuse_all(items))


def u_stub():
    """Asbout M20 door naaf, schuine bus en arm; kop aan de buitenkant van de arm."""
    cy, cz = P.disc_center
    f, n = hub_x()
    x_out = P.u_arm_x[0] / math.cos(math.radians(P.disc_angle)) - 4.0
    shaft = cyl_x(P.stub_d, x_out, f[1], cy, cz)
    head = rotated(hex_prism(30.0, 13.0, z0=0.0), -90.0, Y)
    head.translate(V(x_out, cy, cz))
    return to_disc(fuse_all([shaft, head]))


def boot_points():
    """Omtrek zaaischoen (y_l, z) in het vlak van de schijf: onderaan in de sleuf, voorkant schuin naar achteren."""
    zb = K.boot_bottom_z()
    y0, y1 = P.boot_y
    return [(y0, zb), (y1, zb), (y1 - 8.0, P.boot_top_z), (y0 - 23.0, P.boot_top_z)]


def u_seed_boot():
    """Zaaischoen + zaadbuis 20 x 1,5 + houderstrip naar de arm (1 gelast deel)."""
    cy = P.disc_center[0]
    bx = K.boot_x()
    shoe = poly_yz([(cy + y, z) for y, z in boot_points()], bx[0], bx[1] - bx[0])
    (x0, y0, z0), (x1, y1, z1) = K.tube_ends_local()
    tube = cyl_between((x0, cy + y0, z0), (x1, cy + y1, z1), P.tube_od).cut(
        cyl_between((x0, cy + y0 + 0.01, z0 + 1.0), (x1, cy + y1, z1 + 1.0), P.tube_id))
    local = to_disc(fuse_all([shoe, tube]))
    # houder: strip 30 x 10 van de buis naar de binnenkant van de arm (elementcoordinaten, niet scheef)
    zc = 0.5 * (P.holder_z[0] + P.holder_z[1])
    t = (zc - z0) / (z1 - z0)
    hx, hy, hz = K.disc_to_unit(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, zc)
    holder = box_span((P.u_arm_x[1], hx), (hy - P.holder_dy, hy + P.holder_dy), P.holder_z)
    return fuse_all([local, holder])


def u_band():
    """Dieptering PE-HD O 270 / O 200 x 15 op de +x kant van de schijf (rolt naast de snede op het maaiveld)."""
    cy, cz = P.disc_center
    x0 = P.disc_t / 2.0
    x1 = x0 + P.band_w
    ro = P.band_d / 2.0
    ri = P.band_id / 2.0
    pts = [V(x0, ri, 0), V(x1, ri, 0), V(x1, ro - 4.0, 0), V(x1 - 4.0, ro, 0), V(x0, ro, 0)]
    pts.append(pts[0])
    band = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), X, 360)
    band.translate(V(0, cy, cz))
    return to_disc(band)


def u_pw_link():
    """Rolarm strip 36 x 8 van het scharnier op de sleeparm naar de as van de aandrukrol (werkstand, chi = 0)."""
    lp = K.pw_link_pivot()
    x0, x1 = P.pw_link_x
    link = stadium_yz(lp, P.pw_axle, P.pw_link_w / 2.0, x0, x1 - x0)
    return link.cut([cyl_x(P.pw_link_bolt_d + 0.5, x0 - 1, x1 + 1, *lp), cyl_x(P.pw_axle_d + 0.5, x0 - 1, x1 + 1, *P.pw_axle)])


def u_pw_link_bolt():
    """Scharnierbout M12 door sleeparm, torsieveer en rolarm."""
    lp = K.pw_link_pivot()
    return bolt_x(P.pw_link_bolt_d, 19, 7.5, 10.8, P.u_arm_x[0], P.pw_link_x[1], *lp, extra=1.0)


def u_tspring():
    """Torsieveer om de scharnierbout (benen niet getekend)."""
    lp = K.pw_link_pivot()
    x0, x1 = P.tspring_x
    coil = helix_spring(x1 - x0 - 0.5, (P.tspring_od - P.tspring_wire) / 2.0, P.tspring_wire, coils=2.0)
    coil = rotated(coil, 90.0, Y)
    coil.translate(V(x0 + 0.25, lp[0], lp[1]))
    return coil


def u_pw_axle():
    """Asbout M16 door de aandrukrol, afstandsbus en rolarm; kop aan de buitenkant van de rol, moer aan de
    binnenkant van de rolarm (achter het einde van de sleeparm, dus bereikbaar)."""
    y, z = P.pw_axle
    xr = P.pw_x + P.pw_w / 2.0
    head = rotated(hex_prism(24.0, 10.0, z0=0.0), 90.0, Y)       # kop aan de buitenkant van de rol
    head.translate(V(xr, y, z))
    shank = cyl_x(P.pw_axle_d, P.pw_link_x[0] - 16.0, xr, y, z)
    spacer = ring_x(26.0, P.pw_axle_d + 0.5, P.pw_link_x[1], P.pw_x - P.pw_w / 2.0, y, z)
    nut = rotated(hex_prism(24.0, 13.0, z0=0.0), -90.0, Y)
    nut.translate(V(P.pw_link_x[0], y, z))
    return fuse_all([head, shank, spacer, nut])


def u_press_wheel():
    """(band, velg): massief rubber O 200 x 40 op een kunststof velg met lagers."""
    y, z = P.pw_axle
    x0, x1 = P.pw_x - P.pw_w / 2.0, P.pw_x + P.pw_w / 2.0
    tire = ring_x(P.pw_d, 130.0, x0, x1, y, z)
    try:
        tire = tire.makeFillet(8.0, [e for e in tire.Edges if hasattr(e.Curve, "Radius") and e.Curve.Radius > P.pw_d / 2.0 - 1.0])
    except Exception:
        pass
    rim = fuse_all([ring_x(130.0, 110.0, x0 + 2.0, x1 - 2.0, y, z), ring_x(110.0, P.pw_hub_d, -3.0 + P.pw_x, 3.0 + P.pw_x, y, z),
                    ring_x(P.pw_hub_d, P.pw_axle_d + 0.5, x0, x1, y, z)])
    return tire, rim


def u_strut(phi=0.0):
    """(stang met oog, schotel en moeren; veer) tussen de pen op de arm en de ankerplaat."""
    g, u, spring_len = K.strut_geometry(phi)
    a = K.u_anchor_point()
    t = P.u_anchor_z[1] - P.u_anchor_z[0]
    d_work = (P.u_anchor_z[1] - K.strut_geometry(0.0)[0][1]) / u[1]
    nut_bot = d_work + K.stop_gap() + 0.5
    rod_top = nut_bot + 10.0 + 6.0
    eye_r = P.eye_d / 2.0
    rod = [cyl_x(P.eye_d, -P.eye_w / 2.0, P.eye_w / 2.0, 0, 0).cut(cyl_x(10.5, -20, 20, 0, 0)),
           Part.makeCylinder(P.rod_d / 2.0, rod_top - eye_r + 2.0, V(0, 0, eye_r - 2.0)),
           hex_prism(19.0, 10.0, z0=P.seat_offset - 10.0),
           hex_prism(19.0, 10.0, z0=nut_bot)]
    seat = Part.makeCylinder(P.seat_d / 2.0, 4.0, V(0, 0, P.seat_offset)).cut(
        Part.makeCylinder(P.rod_d / 2.0, 10.0, V(0, 0, P.seat_offset - 1)))
    rod.append(seat)
    spring = helix_spring(spring_len, (P.spring_od - P.spring_wire) / 2.0, P.spring_wire, coils=9)
    spring.translate(V(0, 0, P.seat_offset + 4.0 + 0.25))
    ac = 0.5 * (P.u_arm_x[0] + P.u_arm_x[1])
    origin = (ac, g[0], g[1])
    pin = bolt_x(10.0, 16, 6.4, 8.0, ac - P.eye_w / 2.0 - 0.5 - P.u_lug_t, ac + P.eye_w / 2.0 + 0.5 + P.u_lug_t,
                 g[0], g[1])
    rod_shape = orient(fuse_all(rod), origin, u)
    return fuse_all([rod_shape, pin]), orient(spring, origin, u)


# ---------------------------------------------------------------------
# Zaadbak, doseerhuis en motoren (hefraam, modulecoordinaten)
# ---------------------------------------------------------------------
def _offset_poly(points, w):
    """Platen langs een open polylijn (y, z), dikte w naar binnen (links van de looprichting)."""
    plates = []
    for (y0, z0), (y1, z1) in zip(points[:-1], points[1:]):
        L = math.hypot(y1 - y0, z1 - z0)
        ny, nz = -(z1 - z0) / L, (y1 - y0) / L
        plates.append([(y0, z0), (y1, z1), (y1 + ny * w, z1 + nz * w), (y0 + ny * w, z0 + nz * w)])
    return plates


def hopper():
    """Zaadbak van verzinkt plaatstaal 1,5 mm: voor-, achterwand, trechters, eindplaten en het schuine schot."""
    o = K.hopper_outline()
    # open polylijn van voor-boven via de trechter naar achter-boven (onderkant open boven het doseerhuis)
    front = [o[0], o[1], o[2]]
    rear = [o[3], o[4], o[5]]
    w = P.hop_wall
    x0, x1 = P.hop_x
    items = []
    for chain in (front, rear):
        for quad in _offset_poly(chain, -w):
            items.append(poly_yz(quad, x0, x1 - x0))
    for ex in ((x0, x0 + w), (x1 - w, x1)):
        items.append(poly_yz(o, ex[0], w))
    (db, dt) = K.divider_line()
    L = K.dist(db, dt)
    nd = ((dt[1] - db[1]) / L, -(dt[0] - db[0]) / L)
    div = [db, dt, (dt[0] + nd[0] * w, dt[1] + nd[1] * w), (db[0] + nd[0] * w, db[1] + nd[1] * w)]
    items.append(poly_yz(div, x0 + w, x1 - x0 - 2 * w))
    return fuse_all(items).common(box_span((x0 - 1, x1 + 1), (P.hop_y[0] - 10, P.hop_y[1] + 10), (0, P.hop_top_z)))


def hopper_lid():
    """Deksel in twee delen (scharnieren niet getekend)."""
    x0, x1 = P.hop_x
    y0, y1 = P.hop_y
    z = P.hop_top_z
    return box_span((x0 - 5.0, x1 + 5.0), (y0 - 5.0, y1 + 5.0), (z, z + P.lid_t))


def meter_housing():
    """Doseerhuis (aluminium) met 2 nokkenrollen en 8 uitlopen, plus de asstompen naar de motoren."""
    body = box_span(P.meter_x, P.meter_y, P.meter_z)
    spouts = [cyl(P.spout_d, P.spout_len, "z", x, P.spout_y, P.meter_z[0] - P.spout_len / 2.0) for x in P.row_x]
    return fuse_all([body] + spouts)


def meter_rolls():
    """Zichtbare asstompen van de nokkenrollen aan de motorkant (de rollen zelf zitten in het huis)."""
    x0, x1 = P.meter_x
    return Part.makeCompound([cyl_x(P.shaft_d, x1, x1 + 2.0, P.shaft_main_y, P.shaft_z),
                              cyl_x(P.shaft_d, x0 - 2.0, x0, P.shaft_fine_y, P.shaft_z)])


def meter_motors():
    """(motor gras rechts, motor fijn zaad links): wormwielkast aan het eind van de as, motor staand erop."""
    bx, by, bz = P.motor_box
    out = []
    for side, sy in ((1, P.shaft_main_y), (-1, P.shaft_fine_y)):
        xe = P.meter_x[1] + 2.0 if side > 0 else P.meter_x[0] - 2.0
        xb = (xe, xe + bx) if side > 0 else (xe - bx, xe)
        gear = box_span(xb, (sy - by / 2.0, sy + by / 2.0), (P.shaft_z - 22.0, P.shaft_z - 22.0 + bz))
        xc = 0.5 * (xb[0] + xb[1])
        motor = Part.makeCylinder(P.motor_d / 2.0, P.motor_len, V(xc, sy, P.shaft_z - 22.0 + bz))
        cap = Part.makeCylinder(P.motor_d / 2.0 - 3.0, 14.0, V(xc, sy, P.shaft_z - 22.0 + bz + P.motor_len))
        out.append(fuse_all([gear, motor, cap]))
    return out


def hopper_posts():
    """Steunplaten 8 mm van de bovenkant van de balk naar de trechter en het doseerhuis."""
    o = K.hopper_outline()
    pts = [(P.bar_front, P.bar_top), o[1], o[2], (P.meter_y[1], P.meter_z[0]), (P.bar_rear, P.bar_top)]
    items = []
    for i in P.post_x_rows:
        x = P.row_x[i] + P.post_dx
        items.append(poly_yz(pts, x - P.post_t / 2.0, P.post_t))
    return Part.makeCompound(items)


def spout_bottom(row_x):
    return (row_x, P.spout_y, P.meter_z[0] - P.spout_len)


def seed_hose(row_x, phi=0.0):
    """Zaadslang 20/26 van de uitloop (hefraam) naar de bovenkant van de zaadbuis (arm, draait met phi)."""
    s = spout_bottom(row_x)
    (x0, y0, z0), (x1, y1, z1) = K.tube_ends_local()
    top = K.disc_to_unit(x1, y1, z1)
    below = K.disc_to_unit(x0, y0, z0)
    d = (top[0] - below[0], top[1] - below[1], top[2] - below[2])
    L = math.sqrt(sum(c * c for c in d))
    d = tuple(c / L for c in d)
    up = (top[0] + d[0] * 40.0, top[1] + d[1] * 40.0, top[2] + d[2] * 40.0)

    def arm(p):
        yz = K.arm_point((p[1], p[2]), phi)
        return (row_x + p[0], yz[0], yz[1])
    t, a = arm(top), arm(up)
    pts = [s, (s[0], s[1], s[2] - 40.0), (row_x - 28.0, P.disc_center[0] - 10.0, 330.0),
           (a[0] - 4.0, a[1] + 15.0, a[2] + 40.0), a, t]
    return hose(pts, P.seed_hose_od)


# ---------------------------------------------------------------------
# Referentie robot (alleen ter controle, geen onderdeel van het ontwerp)
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
