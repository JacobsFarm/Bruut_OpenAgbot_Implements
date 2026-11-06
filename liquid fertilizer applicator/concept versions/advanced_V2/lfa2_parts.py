"""Onderdelen van de vloeibare-mest toediener advanced V2; een functie per onderdeel, Part-shapes in
werktuigcoordinaten (zie lfa2_params). Aanbouwbok, parallellogram, actuator, toolbar en veerpoot zoals advanced;
nieuw: V-schijfpaar met hangplaten en dwarskoker, dubbel mes (uit precision_applicator/parts), slangen van de
rollenpomp op de robot naar de messen."""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import lfa2_params as P
import ikd_params as K
import ikd_parts
import rp_params as RP

RP.configure(P.pump_channels)

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basisfuncties (zelfde stijl als agbot_parts.py)
# ---------------------------------------------------------------------
def box(sx, sy, sz, cx=0.0, cy=0.0, cz=0.0):
    return Part.makeBox(sx, sy, sz, V(cx - sx / 2.0, cy - sy / 2.0, cz - sz / 2.0))


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


def rot_yz(point, angle_deg, center):
    # rotatie in het y-z vlak om een as evenwijdig aan x (positief volgens rechterhand om +x:
    # punten achter het draaipunt gaan omlaag), zelfde teken als App.Rotation(X, hoek)
    a = math.radians(angle_deg)
    dy, dz = point[0] - center[0], point[1] - center[1]
    return (center[0] + dy * math.cos(a) - dz * math.sin(a), center[1] + dy * math.sin(a) + dz * math.cos(a))


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
    # lokaal z -> u (in het y-z vlak), lokaal x -> x, lokaal y -> x cross... (rechtshandig)
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
    # kop z -k..0, schacht z 0..length, optionele moer vanaf nut_at
    parts = [hex_prism(af, k, z0=-k), Part.makeCylinder(d / 2.0, length)]
    if nut_at is not None:
        parts.append(hex_prism(af, nut_m, z0=nut_at))
    return fuse_all(parts)


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
    # punten = stuurpunten (poles): de slang loopt door begin- en eindpunt, raakt daar het eerste/laatste
    # segment en blijft binnen het stuurpolygoon (geen doorschieten zoals bij interpoleren)
    pts = [V(*p) for p in points]
    bs = Part.BSplineCurve()
    bs.buildFromPoles(pts, False, 3)
    edge = bs.toShape()
    tangent = edge.tangentAt(edge.FirstParameter)
    profile = Part.Wire(Part.makeCircle(od / 2.0, pts[0], tangent))
    return Part.Wire(edge).makePipeShell([profile], True, True)


def mirrored_x(shape, side):
    return shape if side > 0 else mirror_x(shape)


# ---------------------------------------------------------------------
# Aanbouwbok (vast aan de robotbalk), side = +1 rechts, -1 links
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
        # binnenwang kraagt boven de bovenplaat uit naar de dwarsbuis van de actuator
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


def act_slot_end():
    # bovenkant van het langgat: act_slot verder van B af, langs de actuator-as in werkstand
    ay, az = P.act_a
    by, bz = P.act_b
    d = math.hypot(by - ay, bz - az)
    return (ay - P.act_slot * (by - ay) / d, az - P.act_slot * (bz - az) / d)


def hs_cross_top():
    s = P.hs_cross_size
    x_in = hs_cheek_x(True)[0]
    tube = tube_span((-x_in, x_in), (P.hs_cross_y - s / 2.0, P.hs_cross_y + s / 2.0),
                     (P.hs_cross_z - s / 2.0, P.hs_cross_z + s / 2.0), 3.0)
    lo = P.act_a
    hi = act_slot_end()
    z_tube = P.hs_cross_z - s / 2.0
    half = act_lug_half(rod=True)
    d = math.hypot(hi[0] - lo[0], hi[1] - lo[1])
    ny, nz = -(hi[1] - lo[1]) / d, (hi[0] - lo[0]) / d          # loodrecht op het langgat, naar de buis toe
    lugs = []
    for sx in (-1, 1):
        x0 = half if sx > 0 else -half - 6.0
        web = poly_yz([(lo[0] + 12.0 * ny, lo[1] + 12.0 * nz), (hi[0] + 12.0 * ny, hi[1] + 12.0 * nz),
                       (P.hs_cross_y + s / 2.0 - 2.0, z_tube + 2.0), (P.hs_cross_y - s / 2.0 + 2.0, z_tube + 2.0)],
                      x0, 6.0)
        lugs.append(fuse_all([stadium_yz(lo, hi, 14.0, x0, 6.0), web]))
    body = fuse_all([tube] + lugs)
    return body.cut(stadium_yz(lo, hi, P.act_pin_hole / 2.0, -30.0, 60.0))


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
        b = rotated(b, 180.0, X)            # kop boven, schacht omlaag
        b.translate(V(x, 0.0, z_head))
        items.append(b)
    return mirrored_x(Part.makeCompound(items), side)


def pin_x(x0, x1, y, z, d=P.pin_d, head_d=26.0, head_t=4.0):
    parts = [cyl_x(d, x0 - head_t, x1 + head_t, y, z), cyl_x(head_d, x0 - head_t, x0, y, z),
             cyl_x(head_d, x1, x1 + head_t, y, z)]
    return fuse_all(parts)


def hs_pins(side):
    x0 = hs_cheek_x(True)[0]
    x1 = hs_cheek_x(False)[1]
    pins = [pin_x(x0, x1, P.pin_front_y, z) for z in (P.pin_upper_z, P.pin_lower_z)]
    return mirrored_x(Part.makeCompound(pins), side)


# ---------------------------------------------------------------------
# Parallellogramstang, lokaal: voorste pen in de oorsprong (y, z = 0), stang langs -y
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
# Toolbar + achterframe (bewegen mee bij heffen)
# ---------------------------------------------------------------------
def toolbar():
    half = P.bar_length / 2.0
    s = P.bar_size
    tube = tube_span((-half, half), (P.bar_rear, P.bar_front), (P.bar_bot, P.bar_top), P.bar_wall)
    caps = [box_span((x0, x0 + P.bar_cap_t), (P.bar_rear, P.bar_front), (P.bar_bot, P.bar_top))
            for x0 in (-half - P.bar_cap_t, half)]
    return fuse_all([tube] + caps)


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
    half = act_lug_half(rod=False)
    y_face = P.rf_cross_y + s / 2.0
    lugs = []
    for sx in (-1, 1):
        x0 = half if sx > 0 else -half - 6.0
        lug = stadium_yz((by, bz), (y_face - 2.0, bz), 12.0, x0, 6.0)
        lugs.append(lug)
    body = fuse_all([tube] + lugs)
    return body.cut(cyl_x(P.act_pin_hole, -30, 30, by, bz))


def rf_pins(side):
    x0 = hs_cheek_x(True)[0]
    x1 = hs_cheek_x(False)[1]
    pins = [pin_x(x0, x1, P.pin_rear_y, z) for z in (P.pin_upper_z, P.pin_lower_z)]
    return mirrored_x(Part.makeCompound(pins), side)


# ---------------------------------------------------------------------
# Elektrische lineaire actuator tussen A (aanbouwbok) en B (achterframe)
# ---------------------------------------------------------------------
def act_lug_half(rod):
    """Halve binnenmaat tussen de twee lipjes van een actuatoroog (oogbreedte + speling per kant)."""
    c = P.act_rod_eye_c if rod else P.act_back_c
    return c / 2.0 + P.act_eye_clear


def _rounded_box(x, y, z, r):
    """Blok met afgeronde ribben langs lokaal z (de actuator-as)."""
    b = box_span(x, y, z)
    try:
        edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1.0]
        return b.makeFillet(r, edges)
    except Exception:
        return b


def actuator(body_pin, rod_pin):
    """Linak LA36 (reinforced housing, massief achteroog 0 graden en massief stangoog; maten datasheet blz. 20-26).
    Geeft (huis, stang) in werktuigcoordinaten: huis met parallelle motor op body_pin (achterframe), stang naar
    rod_pin (pen in het langgat van de aanbouwbok); beide (y, z). Lokaal: z = as van achteroog naar stangoog,
    y = act_motor_side * richting van de motor."""
    dy, dz = rod_pin[0] - body_pin[0], rod_pin[1] - body_pin[1]
    length = math.hypot(dy, dz)
    u = (dy / length, dz / length)
    s = P.act_motor_side
    top = P.act_house_h - P.act_house_below            # 111: as -> motorkant
    hw = P.act_house_w / 2.0
    z0 = P.act_house_start
    z_gear = z0 + P.act_gear_len
    z_end = z0 + P.act_house_len
    ys = sorted((-s * P.act_house_below, s * top))
    # achteroog: massieve bus met gat langs x, zeskant tegen het huis
    back = Part.makeCylinder(P.act_back_c / 2.0, P.act_back_f, V(0, 0, -P.act_back_d))
    back = back.cut(cyl_x(P.act_eye_hole, -20.0, 20.0, 0.0, 0.0))
    af, nut_t = P.act_back_nut
    z_nut = P.act_back_f - P.act_back_d
    nut = hex_prism(af, z0 - z_nut + 2.0, z_nut)
    gear = _rounded_box((-hw, hw), ys, (z0, z_gear), 12.0)
    motor_c = s * (top - P.act_motor_d / 2.0)
    motor = Part.makeCylinder(P.act_motor_d / 2.0, z_end - z_gear, V(0, motor_c, z_gear))
    web_y = sorted((s * 10.0, motor_c))
    web = box_span((-hw + 18.0, hw - 18.0), web_y, (z_gear - 2.0, z_end - 25.0))
    t = P.act_tube / 2.0
    tube_end = P.act_retracted - P.act_tube_end_gap
    tube = _rounded_box((-t, t), (-t, t), (z_gear - 5.0, tube_end), 4.0)
    cap = Part.makeCylinder(t - 2.0, 6.0, V(0, 0, tube_end - 3.0))
    body = fuse_all([back, nut, gear, motor, web, tube, cap])
    # stang (binnenbuis) en massief stangoog met gat langs x
    eye_z0 = length - (P.act_rod_eye_f - P.act_rod_eye_d)
    rod_z0 = tube_end + 3.0                             # stang begint aan de eindkap (huis en stang raken niet)
    rod = Part.makeCylinder(P.act_rod_d / 2.0, eye_z0 - rod_z0 + 1.0, V(0, 0, rod_z0))
    eye = Part.makeCylinder(P.act_rod_eye_c / 2.0, P.act_rod_eye_f, V(0, 0, eye_z0))
    eye = eye.cut(cyl_x(P.act_eye_hole, -20.0, 20.0, 0.0, length))
    origin = (0.0, body_pin[0], body_pin[1])
    return orient(body, origin, u), orient(fuse_all([rod, eye]), origin, u)


def actuator_pins(body_pin, rod_pin, head_d=20.0, head_t=4.0):
    """Pennen Ø 12 door de lipjes en de ogen: B aan het achterframe, A in het langgat van de aanbouwbok."""
    pins = []
    for (y, z), rod in ((body_pin, False), (rod_pin, True)):
        x1 = act_lug_half(rod) + 6.0 + 0.5
        pins.append(pin_x(-x1, x1, y, z, d=P.act_pin_d, head_d=head_d, head_t=head_t))
    return Part.makeCompound(pins)


def actuator_length(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


# ---------------------------------------------------------------------
# Injectie-element, vast deel (lokaal: x = 0 is het hart van de rij)
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
            b = rotated(b, 90.0, X)          # schacht langs -y
            b.translate(V(sx * P.u_bolt_dx, y_head, P.bar_z + sz * P.u_bolt_dz))
            items.append(b)
    return Part.makeCompound(items)


def u_anchor_point():
    return (P.u_pivot[0] + P.u_anchor_rel[0], P.u_pivot[1] + P.u_anchor_rel[1])


def u_tongue():
    t = P.u_tongue_t
    x0 = -t / 2.0
    py, pz = P.u_pivot
    ay, az = u_anchor_point()
    y_face = P.bar_rear - P.u_clamp_t
    parts = [box_span((x0, -x0), (y_face - 10.0, y_face), (P.u_clamp_z[0] + 5.0, P.u_clamp_z[1] - 5.0)),
             stadium_yz((y_face - 18.0, P.bar_z), (py, pz), 18.0, x0, t),
             stadium_yz((y_face - 12.0, P.u_clamp_z[1] - 20.0), (ay + 32.0, az - 4.0), 12.0, x0, t)]
    body = fuse_all(parts)
    return body.cut(cyl_x(P.u_pin_d + 0.4, x0 - 1, -x0 + 1, py, pz))


def u_anchor_plate():
    ay, az = u_anchor_point()
    ly, lx, t = P.u_anchor_plate
    plate = box_span((-lx / 2.0, lx / 2.0), (ay - ly / 2.0 - 0.0, ay + ly / 2.0), (az - t / 2.0, az + t / 2.0))
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


def u_lug_point(drop):
    lug = (P.u_pivot[0] + P.u_lug_rel[0], P.u_pivot[1] + P.u_lug_rel[1])
    return rot_yz(lug, drop, P.u_pivot)


def u_strut(drop):
    """Veerpoot tussen de pen op de arm (draait mee) en de veerplaat (vast)."""
    g = u_lug_point(drop)
    g_work = u_lug_point(0.0)
    ay, az = u_anchor_point()
    t = P.u_anchor_plate[2]
    dy, dz = ay - g[0], az - g[1]
    dist = math.hypot(dy, dz)
    u = (dy / dist, dz / dist)
    dist_work = math.hypot(ay - g_work[0], az - g_work[1])
    plate_bot = (az - t / 2.0 - g[1]) / u[1]
    nut_bot = dist_work + t / 2.0 + P.stop_gap
    rod_top = nut_bot + 10.0 + 6.0
    eye_r = P.eye_d / 2.0
    rod = [cyl_x(P.eye_d, -P.eye_w / 2.0, P.eye_w / 2.0, 0, 0).cut(cyl_x(P.rod_d + 0.4, -20, 20, 0, 0)),
           Part.makeCylinder(P.rod_d / 2.0, rod_top - eye_r + 2.0, V(0, 0, eye_r - 2.0)),
           hex_prism(19.0, 10.0, z0=P.seat_offset - 10.0),
           hex_prism(19.0, 10.0, z0=nut_bot)]
    seat = Part.makeCylinder(P.seat_d / 2.0, 4.0, V(0, 0, P.seat_offset)).cut(
        Part.makeCylinder(P.rod_d / 2.0, 10.0, V(0, 0, P.seat_offset - 1)))
    rod.append(seat)
    spring_len = plate_bot - (P.seat_offset + 4.0) - 0.5
    spring = helix_spring(spring_len, (P.spring_od - P.spring_wire) / 2.0, P.spring_wire, coils=8)
    spring.translate(V(0, 0, P.seat_offset + 4.0 + 0.25))
    origin = (0.0, g[0], g[1])
    return orient(fuse_all(rod), origin, u), orient(spring, origin, u), spring_len


# ---------------------------------------------------------------------
# Injectie-element, arm (draait om het draaipunt)
# ---------------------------------------------------------------------


def u_disc_center():
    """Hart van de schijfas in het y-z vlak (beide schijven, armhoek 0); x van de rechter schijf: P.DISC_CX."""
    return (P.disc_y, P.disc_z)


def disc_matrix(side=1):
    """Placement-matrix van het schijfframe (x = as naar buiten, y = voor, z = boven) naar de schijf rechts (+1) of
    links (-1, spiegelbeeld)."""
    ex, ey, ez = P.disc_rot((1, 0, 0)), P.disc_rot((0, 1, 0)), P.disc_rot((0, 0, 1))
    c = P.DISC_C
    m = App.Matrix(ex[0], ey[0], ez[0], c[0],
                   ex[1], ey[1], ez[1], c[1],
                   ex[2], ey[2], ez[2], c[2],
                   0, 0, 0, 1)
    if side < 0:
        m = App.Matrix(-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1).multiply(m)
    return m


def to_disc(shape, side):
    """Shape in schijfcoordinaten naar de rechter of linker schijf (spiegelen geeft een geldige solid)."""
    s = shape.copy()
    s.transformShape(disc_matrix(1), True)
    return s if side > 0 else mirror_x(s)


def disc_axis_point(w, side=1):
    """Punt op de as van de schijf op axiale afstand w (+ = naar buiten)."""
    a = P.disc_axis()
    c = P.DISC_C
    return V(side * (c[0] + w * a[0]), c[1] + w * a[1], c[2] + w * a[2])


def hanger_w(x):
    """Axiale afstand w waarop de schijfas het vlak x (rechts) snijdt."""
    return (x - P.DISC_CX) / P.disc_axis()[0]


def rel_disc(p):
    return (P.disc_y + p[0], P.disc_z + p[1])


def yoke_box():
    """Buitenmaat van de dwarskoker (om uit de vork- en hangplaten te snijden: lasnaad, geen overlap)."""
    h = P.yoke_size / 2.0
    xo = P.hanger_in + P.hanger_t
    y, z = P.yoke_c
    return box_span((-xo, xo), (y - h, y + h), (z - h, z + h))


def u_yoke():
    """Dwarskoker 40 x 40 x 3 boven de schijven, tussen de hangplaten; gelast aan de vorkplaten."""
    h = P.yoke_size / 2.0
    xo = P.hanger_in
    y, z = P.yoke_c
    return tube_span((-xo, xo), (y - h, y + h), (z - h, z + h), P.yoke_wall)


def u_fork_plate(side):
    """Vorkplaat (2x, x +-u_fork_in): draaipunt, veerpootpen, dwarskoker, de twee mesbouten en het oor van de sleeparm.
    De plaat loopt boven de schijven langs naar de koker en dan tussen de schijven door naar het mes."""
    py, pz = P.u_pivot
    g = u_lug_point(0.0)
    yk = P.yoke_c
    s1, s2 = P.knife_slots()
    t = P.u_fork_t
    x0 = P.u_fork_in if side > 0 else -P.u_fork_in - t
    q = P.pw_pivot
    s = pw_stop_point()
    parts = [stadium_yz((py, pz), g, 18.0, x0, t),
             stadium_yz(g, yk, 15.0, x0, t),
             stadium_yz((py, pz), yk, 14.0, x0, t),
             stadium_yz(yk, s1, 16.0, x0, t),
             stadium_yz(s1, s2, 16.0, x0, t),
             stadium_yz(s2, q, P.pw_ear_r, x0, t),                # oor voor de sleeparm van het aandrukwiel
             stadium_yz(q, s, P.pw_sleeve_d / 2.0 + 6.0, x0, t)]
    body = fuse_all(parts).cut(yoke_box())
    holes = [cyl_x(P.u_pin_d + 0.4, x0 - 1, x0 + t + 1, py, pz),
             cyl_x(P.rod_d + 0.4, x0 - 1, x0 + t + 1, g[0], g[1]),
             cyl_x(P.pw_pin_d + 0.4, x0 - 1, x0 + t + 1, q[0], q[1]),
             cyl_x(P.pw_stop_d + 0.4, x0 - 1, x0 + t + 1, s[0], s[1])]
    for kp in (s1, s2):
        holes.append(cyl_x(P.knife_bolt_d + 0.4, x0 - 1, x0 + t + 1, kp[0], kp[1]))
    return body.cut(holes)


def u_lug_pin():
    g = u_lug_point(0.0)
    xo = P.u_fork_in + P.u_fork_t
    parts = [pin_x(-xo, xo, g[0], g[1], d=P.rod_d, head_d=20.0, head_t=3.0)]
    for sx in (-1, 1):
        a, b = sorted((sx * P.eye_w / 2.0, sx * P.u_fork_in))
        parts.append(ring_x(20.0, P.rod_d + 0.4, a, b, g[0], g[1]))
    return Part.makeCompound(parts)


def u_hanger(side):
    """Hangplaat buiten de schijf: van de dwarskoker omlaag naar de lagerbus van de stompe as (bus schuin, langs de
    schijfas, in de plaat gelast)."""
    x0, x1 = P.hanger_in, P.hanger_in + P.hanger_t
    w_mid = hanger_w(0.5 * (x0 + x1))
    c = disc_axis_point(w_mid)
    yk = P.yoke_c
    plate = stadium_yz(yk, (c.y, c.z), P.hanger_r, x0, P.hanger_t)
    a = P.disc_axis()
    w0 = P.hub_w[1] + P.boss_gap
    w1 = hanger_w(x1) + 2.0
    p0 = disc_axis_point(w0)
    boss = Part.makeCylinder(P.boss_d / 2.0, w1 - w0, p0, V(*a))
    body = fuse_all([plate, boss])
    body = body.cut(box_span((x1, x1 + 40.0), (c.y - 60.0, c.y + 60.0), (c.z - 60.0, c.z + 60.0)))   # bus vlak met de plaat
    body = body.cut(Part.makeCylinder(P.axle_d / 2.0 + 0.2, w1 - w0 + 40.0, disc_axis_point(w0 - 20.0), V(*a)))
    return mirrored_x(body, side)


def u_stub_axle(side):
    """Stompe as Ø 25 door naaf en lagerbus, met moer buiten de hangplaat."""
    a = V(*P.disc_axis())
    w0 = P.hub_w[0] + 2.0
    w1 = hanger_w(P.hanger_in + P.hanger_t) + 2.0
    axle = Part.makeCylinder(P.axle_d / 2.0, w1 + 14.0 - w0, disc_axis_point(w0), a)
    nut = rotated(hex_prism(36.0, 12.0, z0=0.0), 0.0, Z)
    m = disc_matrix(1)
    nut_l = rotated(nut, 90.0, Y)                         # hex langs +x (schijfframe)
    nut_l.translate(V(w1 + 3.0, 0, 0))
    nut_l.transformShape(m, True)
    cap = Part.makeCylinder(P.hub_d / 2.0 - 4.0, 4.0, disc_axis_point(P.hub_w[0] - 4.0), a)
    return mirrored_x(Part.makeCompound([axle, nut_l, cap]), side)


def u_hub(side):
    """Naaf met lagers (Ø 60) en twee flenzen waartussen de schijf zit."""
    hub = ring_x(P.hub_d, P.axle_d + 0.4, P.hub_w[0], P.hub_w[1], 0, 0)
    flanges = [ring_x(P.hub_flange_d, P.hub_d - 2.0, a, b, 0, 0)
               for (a, b) in ((-5.5, -P.disc_t / 2.0), (P.disc_t / 2.0, 5.5))]
    return to_disc(fuse_all([hub] + flanges), side)


def u_disc(side):
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
    return to_disc(disc.cut(holes), side)


def u_band(side):
    """Dieptering op de buitenkant van de schijf (rubber); bepaalt de werkdiepte."""
    x0 = P.disc_t / 2.0
    x1 = x0 + P.band_w
    ro = P.band_d / 2.0
    ri = P.band_r_in
    ca, cr = P.band_chamfer
    pts = [V(x0, ri, 0), V(x1, ri, 0), V(x1, ro - cr, 0), V(x1 - ca, ro, 0), V(x0, ro, 0)]
    pts.append(pts[0])
    band = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), X, 360)
    return to_disc(band, side)


# ---------------------------------------------------------------------
# Dubbel mes (precision_applicator/parts/injector_knife_double), slepend, in het midden tussen de schijven
# ---------------------------------------------------------------------
def knife_placement():
    """Placement van het mes (mescoordinaten: x = lengte, y = breedte, z = dikte) in de element-arm."""
    (dy, dz), (ny, nz) = P.knife_axes()
    oy, oz = P.KNIFE_ORIGIN
    return App.Placement(App.Matrix(0, 0, 1, -K.blade_t / 2.0,
                                    dy, ny, 0, oy,
                                    dz, nz, 0, oz,
                                    0, 0, 0, 1))


def _placed(shape):
    s = shape.copy()
    s.transformShape(knife_placement().toMatrix(), True)
    return s


def u_knife():
    return _placed(ikd_parts.blade())


def u_knife_tube(index):
    """Buisje A (0, tegen de rugkant) of B (1, erachter)."""
    return _placed(ikd_parts.tube(index))


def u_knife_welds():
    return _placed(Part.makeCompound(ikd_parts.welds()))


def knife_tube_end(index):
    """(slangeinde, richting naar buiten) van buisje A (0) of B (1), in het elementframe (armhoek 0)."""
    end, d = ikd_parts.hose_end_dirs()[index]
    pl = knife_placement()
    p = pl.multVec(end)
    return p, pl.multVec(end + d) - p


def u_knife_hardware():
    """Twee M10-bouten door de langgaten van het mes en beide vorkplaten, afstandsbussen tussen mes en plaat."""
    xo = P.u_fork_in + P.u_fork_t
    items = []
    for y, z in P.knife_slots():
        items.append(cyl_x(P.knife_bolt_d, -xo - 1, xo + 9.4, y, z))
        head = rotated(hex_prism(P.knife_bolt_af, 6.4, z0=0.0), -90.0, Y)
        head.translate(V(-xo, y, z))
        nut = rotated(hex_prism(P.knife_bolt_af, 8.4, z0=0.0), 90.0, Y)
        nut.translate(V(xo, y, z))
        items += [head, nut]
        for sx in (-1, 1):
            a, b = sorted((sx * K.blade_t / 2.0, sx * P.u_fork_in))
            items.append(ring_x(20.0, P.knife_bolt_d + 0.4, a, b, y, z))
    return Part.makeCompound(items)


# ---------------------------------------------------------------------
# Aandrukwiel (optie per rij): sleeparm op het oor van de vorkplaten, lokaal zoals het element
# (x = 0 hart van de rij, armhoek 0). De sleeparm draait om pw_pivot; build_lfa2 zet hem in een eigen sub-Part.
# ---------------------------------------------------------------------
def pw_stop_point():
    return (P.pw_pivot[0] + P.pw_stop_rel[0], P.pw_pivot[1] + P.pw_stop_rel[1])


def pw_wheel_center():
    return (P.pw_pivot[0] + P.pw_wheel_rel[0], P.pw_pivot[1] + P.pw_wheel_rel[1])


def pw_strap_x(side):
    x0 = P.pw_strap_in
    return (x0, x0 + P.pw_strap_t) if side > 0 else (-x0 - P.pw_strap_t, -x0)


def pw_coil_len():
    return (P.pw_spring_coils + 1) * P.pw_spring_wire


def pw_leg_x(moving):
    # bewegend veerbeen aan de binnenkant van de wikkeling (bij de veerpen), vast been aan de buitenkant
    w = P.pw_spring_wire
    if moving:
        return P.pw_spring_x0 - w / 2.0 - 0.5
    return P.pw_spring_x0 + pw_coil_len() + w / 2.0 + 0.5


def pw_stop_slot_angles():
    # de aanslagbout ligt vast; t.o.v. de strip beschrijft hij een boog tussen de twee aanslagen
    a = math.degrees(math.atan2(P.pw_stop_rel[1], P.pw_stop_rel[0]))
    return a - P.pw_down_deg, a - P.pw_up_deg


def arc_slot_yz(center, r, a0, a1, w, x0, t):
    """Booggat (y-z vlak) rond center, straal r, van hoek a0 tot a1 (graden), breedte w."""
    cy, cz = center
    ro, ri, h = r + w / 2.0, r - w / 2.0, w / 2.0
    b0, b1 = math.radians(a0), math.radians(a1)
    bm = 0.5 * (b0 + b1)

    def pt(rad, b):
        return V(x0, cy + rad * math.cos(b), cz + rad * math.sin(b))

    def cap(b, sign):
        c = pt(r, b)
        return V(x0, c.y - sign * h * math.sin(b), c.z + sign * h * math.cos(b))

    edges = [Part.Arc(pt(ro, b0), pt(ro, bm), pt(ro, b1)).toShape(),
             Part.Arc(pt(ro, b1), cap(b1, 1), pt(ri, b1)).toShape(),
             Part.Arc(pt(ri, b1), pt(ri, bm), pt(ri, b0)).toShape(),
             Part.Arc(pt(ri, b0), cap(b0, -1), pt(ro, b0)).toShape()]
    return Part.Face(Part.Wire(edges)).extrude(V(t, 0, 0))


def pw_peg_point(index=None):
    i = P.pw_preload_index if index is None else index
    a = math.radians(P.pw_peg_angles[i])
    q = P.pw_pivot
    return (q[0] + P.pw_peg_r * math.cos(a), q[1] + P.pw_peg_r * math.sin(a))


def pw_strap(side):
    q = P.pw_pivot
    w = pw_wheel_center()
    x0, x1 = pw_strap_x(side)
    t = x1 - x0
    body = fuse_all([Part.makeCylinder(P.pw_head_r, t, V(x0, q[0], q[1]), X),
                     stadium_yz(q, w, P.pw_strap_r, x0, t),
                     Part.makeCylinder(P.pw_strap_r + 2.0, t, V(x0, w[0], w[1]), X)])
    a0, a1 = pw_stop_slot_angles()
    r_stop = math.hypot(*P.pw_stop_rel)
    holes = [cyl_x(P.pw_pin_d + 0.4, x0 - 1, x1 + 1, q[0], q[1]),
             cyl_x(P.pw_axle_d + 0.4, x0 - 1, x1 + 1, w[0], w[1]),
             arc_slot_yz(q, r_stop, a0, a1, P.pw_stop_d + 1.0, x0 - 1, t + 2)]
    for i in range(len(P.pw_peg_angles)):
        p = pw_peg_point(i)
        holes.append(cyl_x(10.4, x0 - 1, x1 + 1, p[0], p[1]))
    return body.cut(holes)


def pw_peg(side):
    # veerpen (M10 met bus) in het gekozen gat, steekt buiten de strip uit tot voorbij het bewegende veerbeen
    p = pw_peg_point()
    x_out = pw_leg_x(True) + P.pw_spring_wire / 2.0 + 4.0
    x0 = P.pw_strap_in
    body = fuse_all([cyl_x(10.0, x0, x_out, p[0], p[1]), cyl_x(16.0, x_out, x_out + 3.0, p[0], p[1])])
    return mirrored_x(body, side)


def pw_pivot_hardware():
    q = P.pw_pivot
    xe = P.pw_spring_x0 + pw_coil_len() + 0.5
    parts = [pin_x(-xe, xe, q[0], q[1], d=P.pw_pin_d, head_d=22.0, head_t=4.0),
             ring_x(26.0, P.pw_pin_d, -P.u_fork_in, P.u_fork_in, q[0], q[1])]       # bus tussen de vorkplaten
    for sx in (-1, 1):
        a, b = sorted((sx * (P.u_fork_in + P.u_fork_t), sx * P.pw_strap_in))
        parts.append(ring_x(26.0, P.pw_pin_d, a, b, q[0], q[1]))                 # sluitring vork - strip
    return Part.makeCompound(parts)


def pw_stop_hardware():
    s = pw_stop_point()
    # bus tot net voorbij het vaste veerbeen, dunne borgmoer: buitenste rij blijft binnen de robotbreedte
    xs = pw_leg_x(False) + P.pw_spring_wire / 2.0 + 1.0
    parts = [cyl_x(P.pw_stop_d, -xs - 6.4, xs + 5.0, s[0], s[1]),
             ring_x(P.pw_sleeve_d, P.pw_stop_d, -P.u_fork_in, P.u_fork_in, s[0], s[1])]
    for sx in (-1, 1):
        a, b = sorted((sx * (P.pw_strap_in + P.pw_strap_t + 0.5), sx * xs))
        parts.append(ring_x(P.pw_sleeve_d, P.pw_stop_d, a, b, s[0], s[1]))
    head = rotated(hex_prism(17.0, 6.4, z0=0.0), -90.0, Y)
    head.translate(V(-xs, s[0], s[1]))
    nut = rotated(hex_prism(17.0, 5.0, z0=0.0), 90.0, Y)
    nut.translate(V(xs, s[0], s[1]))
    return Part.makeCompound(parts + [head, nut])


def _leg(x, start_pt, end_pt):
    r = P.pw_spring_wire / 2.0
    a = V(x, start_pt[0], start_pt[1])
    b = V(x, end_pt[0], end_pt[1])
    return fuse_all([Part.makeCylinder(r, (b - a).Length, a, b - a), Part.makeSphere(r, b)])


def _tangent_start(contact, sign):
    # punt op de gemiddelde wikkelstraal waar een raaklijn naar contact begint
    q = P.pw_pivot
    dy, dz = contact[0] - q[0], contact[1] - q[1]
    d = math.hypot(dy, dz)
    r = P.pw_spring_dm / 2.0
    a = math.atan2(dz, dy) + sign * math.acos(r / d)
    return (q[0] + r * math.cos(a), q[1] + r * math.sin(a))


def pw_fixed_leg_contact():
    # vast veerbeen tegen de voorkant van de bus op de aanslagbout (veer duwt de bus naar achteren)
    s = pw_stop_point()
    return (s[0] + P.pw_sleeve_d / 2.0 + P.pw_spring_wire / 2.0 + 0.3, s[1])


def pw_coil(side):
    """Torsieveer: wikkeling + vast been (zit vast aan de element-arm)."""
    q = P.pw_pivot
    coil = helix_spring(pw_coil_len(), P.pw_spring_dm / 2.0, P.pw_spring_wire, coils=P.pw_spring_coils)
    coil = rotated(coil, 90.0, Y)
    coil.translate(V(P.pw_spring_x0, q[0], q[1]))
    c = pw_fixed_leg_contact()
    leg = _leg(pw_leg_x(False), _tangent_start(c, 1.0), c)
    return mirrored_x(Part.makeCompound([coil, leg]), side)


def pw_moving_leg(side):
    """Bewegend veerbeen op de veerpen (draait mee met de sleeparm): duwt het wiel omlaag."""
    p = pw_peg_point()
    a = math.radians(P.pw_peg_angles[P.pw_preload_index])
    off = 5.0 + P.pw_spring_wire / 2.0 + 0.3
    c = (p[0] + off * math.sin(a), p[1] - off * math.cos(a))
    return mirrored_x(_leg(pw_leg_x(True), _tangent_start(c, -1.0), c), side)


def pw_tire():
    w = pw_wheel_center()
    h = P.pw_w / 2.0
    r_in = P.pw_rim_d / 2.0
    r = P.pw_d / 2.0
    pts = [V(-h, r_in, 0), V(h, r_in, 0), V(h, r - 10.0, 0), V(h - 7.0, r, 0), V(-h + 7.0, r, 0), V(-h, r - 10.0, 0)]
    pts.append(pts[0])
    tire = Part.Face(Part.makePolygon(pts)).revolve(V(0, 0, 0), X, 360)
    tire.translate(V(0, w[0], w[1]))
    return tire


def pw_rim():
    # kunststof velg (PA): rand + schijf met 6 gaten
    w = pw_wheel_center()
    h = P.pw_w / 2.0
    rim = ring_x(P.pw_rim_d, P.pw_rim_d - 10.0, -h + 2.0, h - 2.0, 0, 0)
    web = ring_x(P.pw_rim_d - 9.0, P.pw_hub_d, -3.0, 3.0, 0, 0)
    holes = [cyl_x(30.0, -5, 5, 52.0 * math.cos(math.radians(60 * i + 30)), 52.0 * math.sin(math.radians(60 * i + 30)))
             for i in range(6)]
    body = fuse_all([rim, web.cut(holes)])
    body.translate(V(0, w[0], w[1]))
    return body


def pw_hub():
    w = pw_wheel_center()
    return ring_x(P.pw_hub_d, P.pw_axle_d, -P.pw_hub_half, P.pw_hub_half, w[0], w[1])


def pw_axle():
    w = pw_wheel_center()
    xo = P.pw_strap_in + P.pw_strap_t
    parts = [cyl_x(P.pw_axle_d, -xo, xo + P.u_bolt_m + 3.0, w[0], w[1])]
    head = rotated(hex_prism(P.u_bolt_af, P.u_bolt_k, z0=0.0), -90.0, Y)
    head.translate(V(-xo, w[0], w[1]))
    nut = rotated(hex_prism(P.u_bolt_af, P.u_bolt_m, z0=0.0), 90.0, Y)
    nut.translate(V(xo, w[0], w[1]))
    for sx in (-1, 1):
        a, b = sorted((sx * P.pw_hub_half, sx * P.pw_strap_in))
        parts.append(ring_x(24.0, P.pw_axle_d, a, b, w[0], w[1]))
    return Part.makeCompound(parts + [head, nut])



# ---------------------------------------------------------------------
# Slangen van de rollenpomp (op de robot) naar de buisjes van de dubbele messen
# ---------------------------------------------------------------------
def rc_to_impl(p):
    """Robotcoordinaten naar werktuigcoordinaten (y = 0 hart achterste onderbalk)."""
    return V(p.x, p.y - P.robot_mount_y, p.z)


def pump_placement_vec():
    """Plaats van de pomp (pomp-oorsprong: midden zijplaten, vloer) in werktuigcoordinaten."""
    return V(P.pump_x, P.pump_y_rc - P.robot_mount_y, P.pump_z_rc)


def pump_outlet(ch):
    """Eind van de pompslang van kanaal ch en de richting waarin hij uitkomt (werktuigcoordinaten)."""
    end, prev = RP.tube_outlet[-1], RP.tube_outlet[-2]
    p = pump_placement_vec() + V(RP.ch_x[ch], end[0], end[1])
    d = V(0, end[0] - prev[0], end[1] - prev[1])
    d.normalize()
    return p, d


def channel(liquid, row):
    return P.CHANNEL[liquid][row]


def element_point(row, p, drop, lift):
    """Punt p (elementframe, armhoek 0, x t.o.v. het hart van de rij) naar werktuigcoordinaten bij armhoek drop en
    hefhoogte lift (toolbar dy, dz)."""
    y, z = rot_yz((p.y, p.z), drop, P.u_pivot)
    theta = math.asin(max(-0.5, min(0.95, lift / P.link_length)))
    dy = P.link_length * (1.0 - math.cos(theta))
    return V(P.row_x[row] + p.x, y + dy, z + lift)


def hose_poles(row, liquid, drop=0.0, lift=0.0):
    """Stuurpunten van de slang: boog uit de pompslang over de dwarskoker van de bok, op de eigen laag schuin opzij
    naar de baan van de rij, boven de veerpoot langs naar achteren en van boven op het slangeinde van het buisje."""
    li = P.LIQUIDS.index(liquid)
    p0, d0 = pump_outlet(channel(liquid, row))
    zl = P.layer_z[liquid]
    zb = P.layer_z["B"]
    xl = P.row_x[row] + P.lane_dx[liquid]
    pts = [p0, p0 + d0 * 12.0, V(p0.x, p0.y - 22.0, zb)]
    if zl > zb:
        pts += [V(p0.x, p0.y - 45.0, zb + 4.0), V(p0.x, p0.y - 70.0, zl)]
    else:
        pts += [V(p0.x, p0.y - 55.0, zb)]
    y0, y1 = P.lateral_y
    pts += [V(p0.x, y0, zl), V(xl, y1, zl), V(xl, P.drop_y[liquid], zl)]
    pe, de = knife_tube_end(li)
    top = (pe + de * P.end_lead)
    over = V(P.lane_dx[liquid], P.knife_hose_over[liquid][0], P.over_unit_z[liquid])
    above = V(0.0, top.y, P.knife_hose_over[liquid][1])
    for q in (over, above, top, pe):
        pts.append(element_point(row, q, drop, lift))
    return pts


def hose_curve(row, liquid, drop=0.0, lift=0.0):
    bs = Part.BSplineCurve()
    bs.buildFromPoles(hose_poles(row, liquid, drop, lift), False, 3)
    return bs


def outlet_hose(row, liquid, drop=0.0, lift=0.0):
    edge = hose_curve(row, liquid, drop, lift).toShape()
    p0 = edge.valueAt(edge.FirstParameter)
    profile = Part.Wire(Part.makeCircle(P.hose_od / 2.0, p0, edge.tangentAt(edge.FirstParameter)))
    return Part.Wire(edge).makePipeShell([profile], True, True)


def hose_length(row, liquid, drop=0.0, lift=0.0):
    return hose_curve(row, liquid, drop, lift).length()


def min_bend_radius(row, liquid, drop=0.0, lift=0.0, samples=400):
    c = hose_curve(row, liquid, drop, lift)
    a, b = c.FirstParameter, c.LastParameter
    k = max(c.curvature(a + (b - a) * s / samples) for s in range(samples + 1))
    return 1.0 / k if k > 0 else float("inf")


def pump_risers():
    """Vier blokken 40 x 60 tussen de dwarskokers van de pompsteun en de onderstelbalken van de pomp (pomp 100 hoger
    dan in combined_v3, zodat de slangen over de dwarskoker van de bok gaan)."""
    p = pump_placement_vec()
    bx, by = P.riser_size
    out = []
    z0 = P.robot_upper_beam_z_top + 40.0
    for y in RP.bar_y:
        for x in (RP.bar_x[0] + bx, RP.bar_x[1] - bx - 60.0):
            out.append(box_span((p.x + x - bx / 2.0, p.x + x + bx / 2.0), (p.y + y - by / 2.0, p.y + y + by / 2.0),
                                (z0, P.pump_z_rc)))
    return out


# ---------------------------------------------------------------------
# Referentie robot (alleen ter controle, geen onderdeel van het ontwerp)
# ---------------------------------------------------------------------
def robot_beam_x(y):
    p = P.robot_beam_profile
    half = P.robot_beam_length / 2.0
    zc = P.robot_beam_z_bot + p / 2.0
    tube = tube_span((-half, half), (y - p / 2.0, y + p / 2.0), (P.robot_beam_z_bot, P.robot_beam_z_top),
                     P.robot_beam_wall)
    holes = []
    x = P.robot_hole_x_min
    while x <= P.robot_hole_x_max + 1e-6:
        holes += [cyl(P.robot_hole_d, p + 10, "z", x, y, zc), cyl(P.robot_hole_d, p + 10, "z", -x, y, zc)]
        x += P.robot_grid
    return tube.cut(holes)


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
