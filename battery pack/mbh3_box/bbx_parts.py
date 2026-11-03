"""Battery rack MBH3+ - one function per part, in robot coordinates (mm).

The MBH3+ is a drop-in battery with its own housing: the rack is open (tray, guides, hold-down), no closed box.
Upright racks (top, well): x = battery width, y = slot direction, the rack centred on x 0, y 0.
Saddle cradles: per side, slots along x (from the inner face outwards), batteries lying with their length along y.
sx = +1 right, -1 left.
"""
import FreeCAD as App
import Part
from FreeCAD import Vector as V

import bbx_params as P


def box_span(xs, ys, zs):
    x0, x1 = sorted(xs)
    y0, y1 = sorted(ys)
    z0, z1 = sorted(zs)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def tube_span(xs, ys, zs, axis, t=2.0):
    """Square tube along axis ('x', 'y' or 'z'), wall t."""
    outer = box_span(xs, ys, zs)
    spans = [sorted(xs), sorted(ys), sorted(zs)]
    inner = []
    for i, a in enumerate("xyz"):
        lo, hi = spans[i]
        inner.append((lo - 1.0, hi + 1.0) if a == axis else (lo + t, hi - t))
    return outer.cut(box_span(*inner))


def cyl_x(d, x0, x1, y, z):
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), V(1, 0, 0))


def cyl_y(d, y0, y1, x, z):
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cyl_z(d, z0, z1, x, y):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), V(0, 0, 1))


# ---------------------------------------------------------------------
# MBH3+ placeholder (local: x width, y thickness, z height, origin = centre of the bottom face)
# ---------------------------------------------------------------------
def battery_body_local():
    bx, by, bz = P.bat_body
    f = P.bat_frame
    panel = box_span((-bx / 2.0 + f, bx / 2.0 - f), (-by / 2.0, by / 2.0), (f, bz - f))
    frame = box_span((-bx / 2.0, bx / 2.0), (-by / 2.0 + f, by / 2.0 - f), (0.0, bz))
    return panel.fuse(frame).removeSplitter()


def battery_top_local():
    bz = P.bat_body[2]
    hx, hy, hz = P.bat_handle
    grip = box_span((-hx / 2.0, hx / 2.0), (-hy / 2.0, hy / 2.0), (bz + hz - 12.0, bz + hz))
    legs = [box_span((s * hx / 2.0 - s * 14.0, s * hx / 2.0), (-hy / 2.0, hy / 2.0), (bz, bz + hz - 12.0))
            for s in (-1, 1)]
    cx, cy, cz = P.bat_connector
    plug = box_span((P.bat_connector_x - cx / 2.0, P.bat_connector_x + cx / 2.0), (-cy / 2.0, cy / 2.0),
                    (bz, bz + cz))
    return Part.makeCompound([grip] + legs + [plug])


def _upright(shape, x, y, z):
    s = shape.copy()
    s.translate(V(x, y, z))
    return s


# lying in a saddle cradle: battery z -> robot +y, battery x -> robot z, battery y -> robot x
LYING = App.Matrix(0, 1, 0, 0,
                   0, 0, 1, 0,
                   1, 0, 0, 0,
                   0, 0, 0, 1)


def _lying(shape, x, y, z):
    s = shape.copy()
    s.transformShape(LYING)
    s.translate(V(x, y, z))
    return s


# ---------------------------------------------------------------------
# Upright rack (top, well): n tray segments, end frames, guides, separators, mat, hold-down bar, combiner
# ---------------------------------------------------------------------
def trays(n, concept):
    """One tray per slot (floor with two low side lips), joint strips under the seams."""
    z0, _, _ = P.rack_z(concept)
    tx, t = P.tray_x, P.tray_t
    out = []
    for c in P.slot_centres(n):
        ys = (c - P.slot_pitch / 2.0, c + P.slot_pitch / 2.0)
        out.append(box_span((-tx, tx), ys, (z0, z0 + t)))
        for s in (-1, 1):
            out.append(box_span((s * (tx - 3.0), s * tx), ys, (z0 + t, z0 + t + P.tray_lip)))
    for i in range(1, n):
        y = -P.rack_half(n) + i * P.slot_pitch
        out.append(box_span((-tx + 20.0, tx - 20.0), (y - 20.0, y + 20.0), (z0 - t, z0)))
    return out


def end_frames(n, concept):
    """Per end: 2 posts beside the tray, a bottom and a top cross tube (end stops), tube 30 x 30 x 2."""
    z0, _, zt = P.rack_z(concept)
    tx, tb, h = P.tray_x, P.tube, P.rack_half(n)
    out = []
    for s in (-1, 1):
        ys = (s * h, s * (h + tb))
        for sx in (-1, 1):
            out.append(tube_span((sx * tx, sx * (tx + tb)), (s * (h - tb), s * h), (z0, zt), "z"))
        out.append(tube_span((-tx - tb, tx + tb), ys, (z0, z0 + tb), "x"))
        out.append(tube_span((-tx - tb, tx + tb), ys, (zt - tb, zt), "x"))
    return out


def guides(n, concept):
    """Flat bar on edge along each side, between the posts: keeps the batteries upright."""
    _, zb, _ = P.rack_z(concept)
    gh, gt = P.guide
    h = P.rack_half(n)
    return [box_span((s * P.inner_x / 2.0, s * (P.inner_x / 2.0 + gt)), (-h, h), (zb + P.guide_z, zb + P.guide_z + gh))
            for s in (-1, 1)]


def separators(n, concept):
    _, zb, _ = P.rack_z(concept)
    ix = P.inner_x / 2.0 - 1.0
    out = []
    for i in range(1, n):
        y = -P.rack_half(n) + i * P.slot_pitch
        out.append(box_span((-ix, ix), (y - P.separator / 2.0, y + P.separator / 2.0), (zb, zb + P.separator_h)))
    return out


def floor_mat(n, concept):
    z0, zb, _ = P.rack_z(concept)
    ix, h = P.inner_x / 2.0, P.rack_half(n)
    return box_span((-ix, ix), (-h, h), (z0 + P.tray_t, zb))


def hold_down(n, concept):
    """Bar over the tops of the batteries, hinged on the rear top tube, star knob on the front one."""
    _, _, zt = P.rack_z(concept)
    w, t = P.hold
    h = P.rack_half(n) + P.tube
    x0, x1 = P.hold_x - w / 2.0, P.hold_x + w / 2.0
    return [box_span((x0, x1), (-h, h), (zt, zt + t)),
            cyl_x(P.hinge_d, x0 - 10.0, x1 + 10.0, -h + P.tube / 2.0, zt + t + P.hinge_d / 2.0)]


def hold_knob(n, concept):
    _, _, zt = P.rack_z(concept)
    return [cyl_z(20.0, zt + P.hold[1], zt + P.hold[1] + 25.0, P.hold_x, P.rack_half(n) + P.tube / 2.0)]


def combiner_box(n, concept):
    """Bus box on the rear end frame: one AS150U-F socket per slot, main fuse, CAN, out to the robot."""
    z0, _, _ = P.rack_z(concept)
    cx, cy, cz = P.combiner
    y = -(P.rack_half(n) + P.tube)
    return box_span((-cx / 2.0, cx / 2.0), (y - cy, y), (z0 + 150.0, z0 + 150.0 + cz))


def batteries_upright(k, n, concept):
    """Bodies and tops of the first k batteries in an n-slot rack."""
    _, zb, _ = P.rack_z(concept)
    cs = P.slot_centres(n)[:k]
    return ([_upright(battery_body_local(), 0.0, c, zb) for c in cs],
            [_upright(battery_top_local(), 0.0, c, zb) for c in cs])


def ears(n, concept):
    """Well: angle brackets on both top cross tubes that rest on the cross rails."""
    _, _, zt = P.rack_z(concept)
    ze = P.robot_lower_z[1]
    ew, et = P.ear
    h = P.rack_half(n) + P.tube
    out = []
    for s in (-1, 1):
        out.append(box_span((-40.0, 40.0), (s * h, s * (h + ew)), (ze, ze + et)))
        out.append(box_span((-40.0, 40.0), (s * h, s * (h + et)), (ze + et, zt)))
    return out


def rails(n, concept):
    """Cross rails 40 x 40 x 3 over the two inner upper beams (top) or under them (well)."""
    w, hgt, t = P.rail
    z0 = P.robot_upper_z[0] - hgt if concept.endswith("well") else P.robot_upper_z[1]
    return [tube_span((-P.rail_x, P.rail_x), (y - w / 2.0, y + w / 2.0), (z0, z0 + hgt), "x", t)
            for y in P.rail_y(n, concept)]


def rail_bolts(n, concept):
    """1 x M10 per rail and beam, through the beam and the rail."""
    xm = sum(P.robot_upper_inner_x) / 2.0
    z0 = (P.robot_upper_z[0] - P.rail[1]) if concept.endswith("well") else P.robot_upper_z[0]
    z1 = P.robot_upper_z[1] if concept.endswith("well") else P.robot_upper_z[1] + P.rail[1]
    out = []
    for y in P.rail_y(n, concept):
        for sx in (-1, 1):
            out.append(cyl_z(10.0, z0 - 8.0, z1 + 8.0, sx * xm, y))
    return out


# ---------------------------------------------------------------------
# Saddle cradle (per side): k segments along x (floor and roof plate), inner plate, end posts, separator,
# 2 retaining bars on the outside hinged at the bottom, hangers under the two upper beams of the side
# ---------------------------------------------------------------------
def _sx_span(sx, a, b):
    return tuple(sorted((sx * a, sx * b)))


def _seg_x(i):
    return P.saddle_x_in + P.saddle_plate + i * P.slot_pitch


def saddle_outer_x(k):
    return _seg_x(k)


def saddle_cradle(sx, k):
    z0, zt = P.saddle_z()
    hy = P.saddle_inner_y / 2.0 + P.tube
    t = P.saddle_plate
    out = []
    for i in range(k):
        xs = _sx_span(sx, _seg_x(i), _seg_x(i + 1))
        out.append(box_span(xs, (-hy, hy), (z0, z0 + t)))
        out.append(box_span(xs, (-hy, hy), (zt - t, zt)))
    out.append(box_span(_sx_span(sx, P.saddle_x_in, P.saddle_x_in + t), (-hy, hy), (z0, zt)))
    return out


def saddle_posts(sx, k):
    """Square tube 30 x 30 at both ends of each segment, on its outer edge: end stops and spacers."""
    z0, zt = P.saddle_z()
    hy = P.saddle_inner_y / 2.0
    t = P.saddle_plate
    out = []
    for i in range(k):
        xs = _sx_span(sx, _seg_x(i + 1) - P.tube, _seg_x(i + 1))
        for s in (-1, 1):
            out.append(tube_span(xs, (s * hy, s * (hy + P.tube)), (z0 + t, zt - t), "z"))
    return out


def saddle_bars(sx, k):
    """2 retaining bars 30 x 8 on the outer side, hinged at the bottom, over-centre latch at the top."""
    z0, zt = P.saddle_z()
    xo = saddle_outer_x(k)
    out = []
    for y in P.saddle_bar_y:
        out.append(box_span(_sx_span(sx, xo, xo + 8.0), (y - 15.0, y + 15.0), (z0 + 12.0, zt - 8.0)))
        out.append(cyl_y(P.hinge_d, y - 15.0, y + 15.0, sx * (xo + P.hinge_d / 2.0), z0 + 6.0))
    return out


def saddle_latches(sx, k):
    _, zt = P.saddle_z()
    xo = saddle_outer_x(k) + 8.0
    return [box_span(_sx_span(sx, xo, xo + 20.0), (y - 15.0, y + 15.0), (zt - 45.0, zt - 10.0))
            for y in P.saddle_bar_y]


def saddle_separator(sx, k):
    z0, _ = P.saddle_z()
    hy = P.saddle_inner_y / 2.0 - 1.0
    zb = z0 + P.saddle_plate + P.pad
    out = []
    for i in range(1, k):
        x = sx * _seg_x(i)
        out.append(box_span((x - P.separator / 2.0, x + P.separator / 2.0), (-hy, hy), (zb, zb + 200.0)))
    return out


def saddle_mat(sx, k):
    z0, _ = P.saddle_z()
    hy = P.saddle_inner_y / 2.0
    return box_span(_sx_span(sx, _seg_x(0), saddle_outer_x(k)), (-hy, hy),
                    (z0 + P.saddle_plate, z0 + P.saddle_plate + P.pad))


def saddle_batteries(sx, k):
    z0, _ = P.saddle_z()
    zb = z0 + P.saddle_plate + P.pad + P.bat_body[0] / 2.0
    y0 = -P.bat_height / 2.0
    bodies, tops = [], []
    for i in range(k):
        x = sx * (_seg_x(i) + P.slot_pitch / 2.0)
        bodies.append(_lying(battery_body_local(), x, y0, zb))
        tops.append(_lying(battery_top_local(), x, y0, zb))
    return bodies, tops


def saddle_combiner(sx, k):
    """Bus box on the inner plate."""
    z0, _ = P.saddle_z()
    cx, cy, cz = P.combiner
    return box_span(_sx_span(sx, P.saddle_x_in - cy, P.saddle_x_in), (-cx / 2.0, cx / 2.0),
                    (z0 + 100.0, z0 + 100.0 + cz))


def saddle_hangers(sx, k):
    """Flat bar 40 x 8 under both upper beams of the side, 2 spacer blocks 40 high; the roof plate is bolted
    to it with 2 star knobs."""
    w, t = P.saddle_hanger
    zb = P.robot_upper_z[0] - 40.0
    x0 = P.robot_upper_inner_x[0] - 10.0
    x1 = P.robot_upper_outer_x[1] + 10.0
    out = []
    for y in P.saddle_hanger_y:
        out.append(box_span(_sx_span(sx, x0, x1), (y - w / 2.0, y + w / 2.0), (zb - t, zb)))
        for xb in (P.robot_upper_inner_x, P.robot_upper_outer_x):
            out.append(box_span(_sx_span(sx, xb[0], xb[1]), (y - w / 2.0, y + w / 2.0), (zb, P.robot_upper_z[0])))
    return out


def saddle_bolts(sx, k):
    w, t = P.saddle_hanger
    zb = P.robot_upper_z[0] - 40.0 - t
    out = []
    for y in P.saddle_hanger_y:
        for xb in (P.robot_upper_inner_x, P.robot_upper_outer_x):
            out.append(cyl_z(10.0, zb - 1.0, P.robot_upper_z[1] + 8.0, sx * sum(xb) / 2.0, y))
    return out


def saddle_knobs(sx, k):
    """Star knobs under the hanger bar into the roof plate (2 per hanger)."""
    _, zt = P.saddle_z()
    zb = P.robot_upper_z[0] - 40.0 - P.saddle_hanger[1]
    xm = (P.saddle_x_in + saddle_outer_x(k)) / 2.0
    return [cyl_z(8.0, zt, zb, sx * xm, y) for y in P.saddle_hanger_y]


# ---------------------------------------------------------------------
# Closed cabinet (cabinet_well, cabinet_top): built in its local frame (u = slide direction, door at +u, v = width,
# z = robot z), then turned about z and put on the robot centre. One level of 100 mm per battery, lying flat.
# ---------------------------------------------------------------------
def _cab_place(shapes, concept):
    out = []
    for s in shapes:
        s = s.copy()
        s.rotate(V(0, 0, 0), V(0, 0, 1), P.cab_turn[concept])
        out.append(s)
    return out


def _cab_dims():
    return P.cab_inner_u / 2.0, P.cab_inner_v / 2.0, P.cab_wall


def _level_z(n, concept, i):
    return P.cab_z0(n, concept) + P.cab_wall + i * P.cab_pitch


def cabinet_shell(n, concept):
    """Floor, roof, back wall and side walls per level (alu 3 mm), flange ring between two levels."""
    hu, hv, w = _cab_dims()
    z0 = P.cab_z0(n, concept)
    zt = z0 + P.cab_height(n)
    out = [box_span((-hu - w, hu), (-hv - w, hv + w), (z0, z0 + w)),
           box_span((-hu - w, hu), (-hv - w, hv + w), (zt - w, zt))]
    for i in range(n):
        zs = (_level_z(n, concept, i), _level_z(n, concept, i + 1))
        out.append(box_span((-hu - w, -hu), (-hv, hv), zs))
        for s in (-1, 1):
            out.append(box_span((-hu - w, hu), (s * hv, s * (hv + w)), zs))
    fw, ft = P.cab_flange
    for i in range(1, n):
        z = _level_z(n, concept, i)
        ring = box_span((-hu - w - fw, hu), (-hv - w - fw, hv + w + fw), (z - ft / 2.0, z + ft / 2.0))
        out.append(ring.cut(box_span((-hu - w, hu + 1.0), (-hv - w, hv + w), (z - ft, z + ft))))
    return _cab_place(out, concept)


def cabinet_shelves(n, concept):
    """Shelf per level (alu 4 with an HDPE slide strip, drawn as one plate)."""
    hu, hv, _ = _cab_dims()
    out = []
    for i in range(n):
        z = _level_z(n, concept, i)
        out.append(box_span((-hu, hu), (-hv, hv), (z, z + P.cab_shelf)))
    return _cab_place(out, concept)


def cabinet_doors(n, concept):
    """Drop-down door per level on the +u face, 2 hinges at the bottom."""
    hu, hv, w = _cab_dims()
    d, hd = P.cab_door, P.cab_hinge_d
    out = []
    for i in range(n):
        z = _level_z(n, concept, i)
        z_lo = z + 2.0 if i > 0 else P.cab_z0(n, concept) + 2.0
        z_hi = _level_z(n, concept, i + 1) - 2.0 if i < n - 1 else _level_z(n, concept, n) + w - 2.0
        out.append(box_span((hu, hu + d), (-hv - w, hv + w), (z_lo, z_hi)))
        for s in (-1, 1):
            out.append(cyl_y(hd, s * (hv - 60.0) - 25.0, s * (hv - 60.0) + 25.0, hu + d + hd / 2.0, z_lo + hd / 2.0))
    return _cab_place(out, concept)


def cabinet_latches(n, concept):
    """Over-centre latch at the top of each door."""
    hu, _, _ = _cab_dims()
    out = []
    for i in range(n):
        zt = _level_z(n, concept, i + 1)
        out.append(box_span((hu + P.cab_door, hu + P.cab_door + 15.0), (-20.0, 20.0), (zt - 24.0, zt - 8.0)))
    return _cab_place(out, concept)


# lying flat in the cabinet: battery z (height) -> u, battery x (width) -> v, battery y (thickness) -> z
FLAT = App.Matrix(0, 0, 1, 0,
                  1, 0, 0, 0,
                  0, 1, 0, 0,
                  0, 0, 0, 1)


def cabinet_batteries(k, n, concept):
    """The first k batteries, from the bottom level up, handle and plug towards the door."""
    hu, _, _ = _cab_dims()
    bodies, tops = [], []
    for i in range(k):
        z = _level_z(n, concept, i) + P.cab_shelf + P.bat_body[1] / 2.0
        for shape, out in ((battery_body_local(), bodies), (battery_top_local(), tops)):
            s = shape.copy()
            s.transformShape(FLAT)
            s.translate(V(-hu + 10.0, 0.0, z))
            out.append(s)
    return _cab_place(bodies, concept), _cab_place(tops, concept)


def cabinet_combiner(n, concept):
    """Bus box on the -v side wall near the doors (the battery plugs face the doors), 16 mm off the wall."""
    hu, hv, w = _cab_dims()
    cx, cy, cz = P.combiner
    z0 = P.cab_z0(n, concept)
    v0 = hv + w + P.cab_flange[0] + 1.0
    return _cab_place([box_span((hu - 10.0 - cx, hu - 10.0), (-v0 - cy, -v0), (z0 + 20.0, z0 + 20.0 + cz))], concept)


def cabinet_ears(n, concept):
    """cabinet_well: angle brackets on both side walls, flush with the roof, resting on the cross rails."""
    hu, hv, w = _cab_dims()
    zt = P.cab_z0(n, concept) + P.cab_height(n)
    et = P.ear[1]
    ry = P.cab_rail_y[concept] + P.rail[0] / 2.0
    out = []
    for s in (-1, 1):
        for u in (-hu / 2.0, hu / 2.0):
            out.append(box_span((u - 40.0, u + 40.0), (s * (hv + w), s * ry), (zt - et, zt)))
            out.append(box_span((u - 40.0, u + 40.0), (s * (hv + w), s * (hv + w + et)), (zt - 60.0, zt - et)))
    return _cab_place(out, concept)


# ---------------------------------------------------------------------
# MU3+ placeholder (MegaUMPF3+; local: x 167, y 197, z up, origin = centre of the bottom face)
# ---------------------------------------------------------------------
def mu3_body_local():
    """Silver body between the bumpers."""
    sx, sy, sz = P.mu3_size
    i = P.mu3_inset
    return box_span((-sx / 2.0 + i, sx / 2.0 - i), (-sy / 2.0 + i, sy / 2.0 - i),
                    (P.mu3_bumper[0], sz - P.mu3_bumper[1]))


def mu3_top_local():
    """Bottom bumper, top frame with the recess, handle (9.5 above the frame) and AS150U socket in the recess."""
    sx, sy, sz = P.mu3_size
    r = P.mu3_recess
    zb, zt = P.mu3_bumper
    bumper = box_span((-sx / 2.0, sx / 2.0), (-sy / 2.0, sy / 2.0), (0.0, zb))
    frame = box_span((-sx / 2.0, sx / 2.0), (-sy / 2.0, sy / 2.0), (sz - zt, sz))
    frame = frame.cut(box_span((-sx / 2.0 + r, sx / 2.0 - r), (-sy / 2.0 + r, sy / 2.0 - r), (sz - r, sz + 1.0)))
    zr = sz - r
    grip = box_span((-55.0, 55.0), (-10.0, 10.0), (sz + P.mu3_handle_up - 10.0, sz + P.mu3_handle_up))
    legs = [box_span((s * 55.0 - 12.0, s * 55.0 + 12.0), (-10.0, 10.0), (zr, sz + P.mu3_handle_up - 10.0))
            for s in (-1, 1)]
    socket = box_span((-17.0, 17.0), (P.mu3_socket_y - 12.0, P.mu3_socket_y + 12.0), (zr, zr + 12.0))
    return Part.makeCompound([bumper, frame, grip] + legs + [socket])


def battery_local(kind):
    """(body, top) placeholder shapes of a battery type."""
    if kind == "MU3+":
        return mu3_body_local(), mu3_top_local()
    return battery_body_local(), battery_top_local()


# ---------------------------------------------------------------------
# Wooden box (wood_side, wood_side_mu3): 18 mm multiplex on the two right upper beams, 2 compartments,
# batteries upright, plugs up
# ---------------------------------------------------------------------
def wood_box(concept="wood_side"):
    """Bottom, 4 walls and the divider (glued and screwed), cable slot at the top of the rear wall."""
    x0, x1, y0, y1, z0, zt = P.wood_outer(concept)
    w = P.wood_t
    sw, sh = P.wood_slot
    walls = []
    if P.WOOD[concept]["along"] == "x":
        walls += [box_span((x0, x1), (y0, y0 + w), (z0 + w, zt)), box_span((x0, x1), (y1 - w, y1), (z0 + w, zt))]
        walls += [box_span((c[0] - w, c[0]), (y0 + w, y1 - w), (z0 + w, zt)) for c in P.wood_cells(concept)]
        walls.append(box_span((x1 - w, x1), (y0 + w, y1 - w), (z0 + w, zt)))
    else:
        walls += [box_span((x0, x0 + w), (y0, y1), (z0 + w, zt)), box_span((x1 - w, x1), (y0, y1), (z0 + w, zt))]
        walls += [box_span((x0 + w, x1 - w), (c[2] - w, c[2]), (z0 + w, zt)) for c in P.wood_cells(concept)]
        walls.append(box_span((x0 + w, x1 - w), (y1 - w, y1), (z0 + w, zt)))
    slot = box_span((P.wood_x_c - sw / 2.0, P.wood_x_c + sw / 2.0), (y0 - 1.0, y0 + w + 1.0), (zt - sh, zt + 1.0))
    return [box_span((x0, x1), (y0, y1), (z0, z0 + w))] + [s.cut(slot) for s in walls]


def wood_lid(concept="wood_side"):
    x0, x1, y0, y1, _, zt = P.wood_outer(concept)
    o = P.wood_lid_over
    return [box_span((x0 - o, x1 + o), (y0 - o, y1 + o), (zt, zt + P.wood_t))]


def wood_fittings(concept="wood_side"):
    """2 hinges on the rear edge, a hasp on the front, 2 handles on the lid."""
    x0, x1, y0, y1, _, zt = P.wood_outer(concept)
    o = P.wood_lid_over
    out = []
    for xc in (x0 + 45.0, x1 - 45.0):
        out.append(cyl_x(P.hinge_d, xc - 30.0, xc + 30.0, y0 - o - P.hinge_d / 2.0, zt))
    out.append(box_span((P.wood_x_c - 20.0, P.wood_x_c + 20.0), (y1, y1 + 6.0), (zt - 60.0, zt - 10.0)))
    out.append(box_span((P.wood_x_c - 20.0, P.wood_x_c + 20.0), (y1 + o, y1 + o + 6.0), (zt - 25.0, zt + P.wood_t)))
    for yc in (y0 + 70.0, y1 - 70.0):
        out.append(box_span((P.wood_x_c - 50.0, P.wood_x_c + 50.0), (yc - 10.0, yc + 10.0),
                            (zt + P.wood_t, zt + P.wood_t + 25.0)))
    return out


def wood_mats(concept="wood_side"):
    z0 = P.wood_outer(concept)[4] + P.wood_t
    return [box_span(c[0:2], c[2:4], (z0, z0 + P.wood_mat)) for c in P.wood_cells(concept)]


def wood_bolts(concept="wood_side"):
    """4 x M10 through the bottom and the two upper beams (countersunk head flush with the bottom, under the mat)."""
    z0 = P.wood_outer(concept)[4]
    out = []
    for xb in (P.robot_upper_inner_x, P.robot_upper_outer_x):
        for y in P.WOOD[concept]["bolt_y"]:
            out.append(cyl_z(10.0, P.robot_upper_z[0] - 8.0, z0 + P.wood_t, sum(xb) / 2.0, y))
    return out


def wood_batteries(concept="wood_side"):
    """Upright in the middle of each compartment, plug at the rear (-y)."""
    cfg = P.WOOD[concept]
    zb = P.wood_outer(concept)[4] + P.wood_t + P.wood_mat
    bodies, tops = [], []
    for c in P.wood_cells(concept):
        xc, yc = (c[0] + c[1]) / 2.0, (c[2] + c[3]) / 2.0
        for shape, out in zip(battery_local(cfg["kind"]), (bodies, tops)):
            s = shape.copy()
            s.rotate(V(0, 0, 0), V(0, 0, 1), cfg["turn"])
            s.translate(V(xc, yc, zb))
            out.append(s)
    return bodies, tops
