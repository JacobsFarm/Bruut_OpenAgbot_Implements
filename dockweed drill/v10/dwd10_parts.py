"""Parts of the dockweed drill v10: one function per part, returns a Part shape in robot coordinates.

v10 = v8 (X axis on 2 round tubes D50 x 4 in plain-bush housings, LA36, spindle, can) with the X drive of v9 (motor
fixed at the right side plate, belt round 2 pulleys, lower run clamped on the slide) and the Z axis on linear guides
(2 rails HGR20 on 2 rail beams on the X slide, 4 carriages HGH20CA on the Z sled), after the photos in inspiration/.
Drawn in the gantry frame (x, v, z): v = distance behind the rear face of the rear lower beam of the robot.
to_robot() mirrors that to robot y (y = robot_beam_rear_face - v).
Moving groups are drawn in their reference pose:
- X slide at x = 0 (3 X housings, rail beams, rails and the fixed part of the actuator);
- Z sled (sled, carriages, actuator rod, spindle bracket, spindle, motor) with the tool underside at z_ref
  (driving, actuator retracted);
- can hanging under the spindle bracket at z_ref (rim at z_ref - pot_rim).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dwd10_params as P

UP = V(0, 0, 1)
ALONG_V = V(0, 1, 0)
ALONG_X = V(1, 0, 0)


# ---------------------------------------------------------------------
# Basic shapes (gantry frame)
# ---------------------------------------------------------------------
def to_robot(shape):
    s = shape.mirror(V(0, 0, 0), V(0, 1, 0))
    s.translate(V(0, P.robot_beam_rear_face, 0))
    return s


def box(x0, x1, v0, v1, z0, z1):
    return Part.makeBox(x1 - x0, v1 - v0, z1 - z0, V(x0, v0, z0))


def tube_rect(x0, x1, v0, v1, z0, z1, t, axis):
    o = box(x0, x1, v0, v1, z0, z1)
    if axis == "x":
        i = box(x0 - 1, x1 + 1, v0 + t, v1 - t, z0 + t, z1 - t)
    elif axis == "v":
        i = box(x0 + t, x1 - t, v0 - 1, v1 + 1, z0 + t, z1 - t)
    else:
        i = box(x0 + t, x1 - t, v0 + t, v1 - t, z0 - 1, z1 + 1)
    return o.cut(i)


def cyl(r, p, d, L):
    return Part.makeCylinder(r, L, p, d)


def pipe(ro, ri, p, d, L):
    d = V(d)
    d.normalize()
    return cyl(ro, p, d, L).cut(cyl(ri, p - d * 1.0, d, L + 2.0))


def holes_z(sh, pts, r, z0, h):
    for (px, pv) in pts:
        sh = sh.cut(cyl(r, V(px, pv, z0 - 1), UP, h + 2))
    return sh


def fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def compound(shapes):
    return Part.makeCompound(list(shapes))


def poly_vz(pts, x0, t):
    """Plate in the v-z plane (points (v, z)), thickness t from x0."""
    w = Part.makePolygon([V(x0, v, z) for v, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(t, 0, 0))


def m10_bolt_z(x, v, z_head, z_nut):
    """M10 from above: head on z_head (upwards), nut below z_nut (downwards)."""
    shank = cyl(P.m10_d / 2.0, V(x, v, z_nut - P.m10_nut_m - 3.0), UP, z_head - z_nut + P.m10_nut_m + 3.0)
    head = cyl(P.m10_head_r, V(x, v, z_head), UP, P.m10_head_k)
    nut = cyl(P.m10_head_r, V(x, v, z_nut - P.m10_nut_m), UP, P.m10_nut_m)
    return [shank.fuse(head).fuse(nut)]


def bolt_v(x, v_head, v_nut, z, d, head_r, head_k, nut_m):
    """Bolt along v: head at the back (v_head, towards +v), nut at the front (v_nut, towards -v)."""
    shank = cyl(d / 2.0, V(x, v_nut - nut_m - 3.0, z), ALONG_V, v_head - v_nut + nut_m + 3.0)
    head = cyl(head_r, V(x, v_head, z), ALONG_V, head_k)
    nut = cyl(head_r, V(x, v_nut - nut_m, z), ALONG_V, nut_m)
    return shank.fuse(head).fuse(nut)


# ---------------------------------------------------------------------
# Derived dimensions (v stack from the robot backwards)
# ---------------------------------------------------------------------
def stack():
    s = {}
    s["up"] = (P.up_v0, P.up_v1)
    s["xbeam"] = P.xbeam_v
    s["tube"] = P.tube_v                                # centre of the X tubes
    s["slide"] = (P.slide_v0, P.slide_v1)              # X slide
    s["zb"] = P.zb_v                                    # rail beams of the Z axis
    s["rail"] = (P.rail_v0, P.rail_v0 + P.rail_h)       # rail HGR20
    s["act"] = P.act_v                                  # actuator axis
    s["sb_back"] = (P.sb_back_v0, P.sb_back_v0 + P.sb_back_t)    # Z sled = back plate of the spindle bracket
    s["spindle"] = s["sb_back"][1] + P.spindle_dv
    return s


S = stack()


def spindle_y():
    return P.v_to_y(S["spindle"])


def pot_rim_ref():
    return P.z_ref - P.pot_rim


# ---------------------------------------------------------------------
# Headstock (fixed to the robot), side = -1 left / +1 right (as v6 / v8)
# ---------------------------------------------------------------------
def _hs_bolt_pts(side):
    xc = side * P.hs_x
    return [(xc - P.hs_bolt_dx, P.hs_bolt_v), (xc + P.hs_bolt_dx, P.hs_bolt_v)]


def hs_top_plate(side):
    xc = side * P.hs_x
    z0 = P.robot_lower_beam_z[1]
    p = box(xc - P.hs_plate_half_x, xc + P.hs_plate_half_x, -P.robot_beam, 0.0, z0, z0 + P.hs_plate_t)
    return to_robot(holes_z(p, _hs_bolt_pts(side), 5.5, z0, P.hs_plate_t))


def hs_clamp_plate(side):
    xc = side * P.hs_x
    z1 = P.robot_lower_beam_z[0]
    p = box(xc - P.hs_plate_half_x, xc + P.hs_plate_half_x, -P.robot_beam, 0.0, z1 - P.hs_plate_t, z1)
    return to_robot(holes_z(p, _hs_bolt_pts(side), 5.5, z1 - P.hs_plate_t, P.hs_plate_t))


def hs_back_plate(side):
    xc = side * P.hs_x
    return to_robot(box(xc - P.hs_plate_half_x, xc + P.hs_plate_half_x, 0.0, P.hs_plate_t,
                        P.up_z0, P.robot_lower_beam_z[1] + P.hs_plate_t))


def hs_bolts(side):
    z_head = P.robot_lower_beam_z[1] + P.hs_plate_t
    z_nut = P.robot_lower_beam_z[0] - P.hs_plate_t
    out = []
    for (x, v) in _hs_bolt_pts(side):
        out += m10_bolt_z(x, v, z_head, z_nut)
    return to_robot(compound(out))


def upright(side):
    """Upright 40 x 40 x 3 with an M12 hole (along v) at the height of each cross beam."""
    xc = side * P.hs_x
    h = P.up_size / 2.0
    u = tube_rect(xc - h, xc + h, P.up_v0, P.up_v1, P.up_z0, P.up_z1, P.up_wall, "z")
    for zp in P.xbar_z:
        u = u.cut(cyl(6.5, V(xc, P.up_v0 - 1, zp), ALONG_V, P.up_size + 2))
    return to_robot(u)


def upright_cap(side):
    xc = side * P.hs_x
    h = P.up_size / 2.0
    return to_robot(box(xc - h, xc + h, P.up_v0, P.up_v1, P.up_z1, P.up_z1 + P.up_cap_t))


def gusset(side):
    xc = side * P.hs_x
    z0 = P.robot_lower_beam_z[1] + P.hs_plate_t
    pts = [(-P.robot_beam, z0), (P.up_v0, z0), (P.up_v0, z0 + P.gusset_h)]
    return to_robot(poly_vz(pts, xc - P.gusset_t / 2.0, P.gusset_t))


def cross_tube():
    x = P.hs_x - P.up_size / 2.0
    return to_robot(tube_rect(-x, x, P.up_v0, P.up_v1, P.cross_z[0], P.cross_z[1], P.cross_wall, "x"))


# ---------------------------------------------------------------------
# X frame (as v8): 2 cross beams 40 x 40 x 3 behind the uprights, 2 side plates, the round X tubes between them
# ---------------------------------------------------------------------
def _inner_x():
    """Inside of the side plate (= end of the tubes and cross beams)."""
    return P.xbar_L / 2 - P.end_plate_t


def x_beam(zp):
    """Cross beam at tube height zp: from side plate to side plate (welded), M12 holes at the uprights."""
    xi = _inner_x()
    h = P.xbeam[0] / 2
    v0, v1 = S["xbeam"]
    b = tube_rect(-xi, xi, v0, v1, zp - h, zp + h, P.xbeam[1], "x")
    for s in (-1, 1):
        b = b.cut(cyl(6.5, V(s * P.hs_x, v0 - 1, zp), ALONG_V, P.xbeam[0] + 2))
    return to_robot(b)


def x_beam_bolts():
    """4x M12 through upright and cross beam (head at the back, nut at the front of the upright)."""
    out = [bolt_v(s * P.hs_x, S["xbeam"][1], P.up_v0, zp, P.m12_d, P.m12_head_r, P.m12_head_k, P.m10_nut_m)
           for s in (-1, 1) for zp in P.xbar_z]
    return to_robot(compound(out))


def x_guide_tube(zp):
    """Precision tube D50 x 4 (E355, cold drawn seamless) from side plate to side plate."""
    xi = _inner_x()
    return to_robot(pipe(P.xg_d / 2, P.xg_d / 2 - P.xg_t, V(-xi, S["tube"], zp), ALONG_X, 2 * xi))


def _tube_bolt_pts():
    return [(zp, zp + dz) for zp in P.xbar_z for dz in (-P.tube_bolt_dz, P.tube_bolt_dz)]


def tube_plugs():
    """Round plug D42 (= bore of the tube), 25 long, welded in each tube end, tapped 2x M10 (hole drawn D10)."""
    xi = _inner_x()
    tv = S["tube"]
    r = P.xg_d / 2 - P.xg_t
    out = []
    for s in (-1, 1):
        x0 = xi - P.plug_L if s > 0 else -xi
        for zp in P.xbar_z:
            p = cyl(r, V(x0, tv, zp), ALONG_X, P.plug_L)
            for z in (zp - P.tube_bolt_dz, zp + P.tube_bolt_dz):
                p = p.cut(cyl(5.0, V(x0 - 1, tv, z), ALONG_X, P.plug_L + 2))
            out.append(p)
    return to_robot(compound(out))


def tube_bolts(side):
    """2x M10 per tube end from outside through the side plate into the plug (20 mm engaged)."""
    xi = _inner_x()
    tv = S["tube"]
    out = []
    for zp, z in _tube_bolt_pts():
        shank = cyl(P.m10_d / 2.0, V(xi - 20.0, tv, z), ALONG_X, 20.0 + P.end_plate_t)
        head = cyl(P.m10_head_r, V(xi + P.end_plate_t, tv, z), ALONG_X, P.m10_head_k)
        b = shank.fuse(head)
        if side < 0:
            b = b.mirror(V(0, 0, 0), V(1, 0, 0))
        out.append(b)
    return to_robot(compound(out))


def end_plate(side):
    """Side plate 12 mm: cross beams and drive bracket welded, tubes bolted with 2x M10 per end; light hole in the
    middle; reaches to behind the slide (limit switch left, end stop right)."""
    xi = _inner_x()
    x0 = xi if side > 0 else -xi - P.end_plate_t
    tv = S["tube"]
    v0, v1 = P.side_plate_v
    zl, zh = P.xbar_z
    ep = box(x0, x0 + P.end_plate_t, v0, v1, P.side_plate_z[0], P.side_plate_z[1])
    ep = ep.cut(box(x0 - 1, x0 + P.end_plate_t + 1, v0 + 12, P.drive_bracket_v[0] - 10, zl + 50, zh - 50))
    for zp, z in _tube_bolt_pts():
        ep = ep.cut(cyl(5.5, V(x0 - 1, tv, z), ALONG_X, P.end_plate_t + 2))
    if side < 0:
        lv, lz = P.limit_vz
        ep = ep.cut(cyl(6.0, V(x0 - 1, lv, lz), ALONG_X, P.end_plate_t + 2))
    return to_robot(ep)


def drive_bracket(side):
    """Bracket plate 10 mm (normal v) welded to the side plate: right the 5:1 gearbox of the X motor (hole for the
    output shaft), left the tension pulley (slot along x to tension the belt). (As v9.)"""
    xi = _inner_x()
    v0, v1 = P.drive_bracket_v
    xa, xb = sorted((side * (xi - P.drive_bracket_dx), side * xi))
    z = P.belt_z
    dz = P.drive_bracket_dz
    p = box(xa, xb, v0, v1, z - dz, z + dz)
    px = side * P.pulley_x
    if side > 0:
        p = p.cut(cyl(9.0, V(px, v0 - 1, z), ALONG_V, v1 - v0 + 2))
    else:
        p = p.cut(box(px - 15.0, px + 15.0, v0 - 1, v1 + 1, z - 5.0, z + 5.0))
    return to_robot(p)


def x_gearbox():
    """Planetary gearbox 5:1 (60 x 60) on the front of the right bracket plate (fixed)."""
    xm, z = P.pulley_x, P.belt_z
    v0 = P.drive_bracket_v[0]
    return to_robot(box(xm - 30, xm + 30, v0 - 55, v0, z - 30, z + 30))


def x_motor():
    """NEMA 23 closed-loop, fixed: the motor cable does not move with the slide."""
    xm, z = P.pulley_x, P.belt_z
    v0 = P.drive_bracket_v[0] - 55
    return to_robot(box(xm - 28.5, xm + 28.5, v0 - 112, v0, z - 28.5, z + 28.5).fuse(
        box(xm - 25, xm + 25, v0 - 135, v0 - 112, z - 25, z + 25)))


def x_pulleys():
    """2 pulleys HTD5M 20T with flanges: right on the output shaft of the gearbox, left the tension pulley."""
    v0, v1 = P.belt_v
    z = P.belt_z
    out = []
    for s, bore in ((1, 7.0), (-1, 5.0)):
        px = s * P.pulley_x
        p = fuse([cyl(P.pulley_r, V(px, v0, z), ALONG_V, v1 - v0), cyl(P.pulley_flange_r, V(px, v0 - 2, z), ALONG_V, 2),
                  cyl(P.pulley_flange_r, V(px, v1, z), ALONG_V, 2)])
        out.append(p.cut(cyl(bore, V(px, v0 - 3, z), ALONG_V, v1 - v0 + 6)))
    return to_robot(compound(out))


def x_pulley_shafts():
    """Right: output shaft D14 of the gearbox through the bracket; left: M10 as axle in the slot, with spacer and nut."""
    v0, v1 = P.drive_bracket_v
    z = P.belt_z
    px = P.pulley_x
    right = cyl(7.0, V(px, v0, z), ALONG_V, P.belt_v[1] + 2 - v0)
    left = fuse([cyl(5.0, V(-px, v0 - 6, z), ALONG_V, P.belt_v[1] + 10 - v0 + 6), cyl(8.0, V(-px, v0 - 6, z), ALONG_V, 6),
                 cyl(8.0, V(-px, P.belt_v[1] + 2, z), ALONG_V, 8)])
    spacer = pipe(8.0, 5.0, V(-px, v1, z), ALONG_V, P.belt_v[0] - 2 - v1)
    return to_robot(compound([right, left, spacer]))


def belt_upper():
    """Upper belt run from pulley to pulley, with the 2 half wraps (fixed)."""
    px = P.pulley_x
    v0, v1 = P.belt_v
    z = P.belt_z
    r0, r1 = P.belt_r
    parts = [box(-px, px, v0, v1, z + r0, z + r1)]
    for s in (-1, 1):
        ring = pipe(r1, r0, V(s * px, v0, z), ALONG_V, v1 - v0)
        xa, xb = (px, px + 30) if s > 0 else (-px - 30, -px)
        parts.append(ring.common(box(xa, xb, v0 - 1, v1 + 1, z - 30, z + 30)))
    return to_robot(fuse(parts))


def belt_lower(x):
    """Lower belt run from the left pulley to the clamp and from the clamp to the right pulley (slide at x)."""
    px = P.pulley_x
    v0, v1 = P.belt_v
    z0, z1 = P.belt_z - P.belt_r[1], P.belt_z - P.belt_r[0]
    c = P.belt_clamp_half_x
    return to_robot(compound([box(-px, x - c, v0, v1, z0, z1), box(x + c, px, v0, v1, z0, z1)]))


def limit_switch():
    """Inductive limit switch M12 X-min through the left side plate, sees the edge of the slide (3 mm at x_min)."""
    xi = _inner_x()
    lv, lz = P.limit_vz
    x_tip = P.x_min - P.slide_half_x - 3.0
    x0 = -xi - P.end_plate_t - 18.0
    return to_robot(cyl(6, V(x0, lv, lz), ALONG_X, x_tip - x0))


def end_stop():
    """Rubber end stop X-max on the right side plate (1 mm from the slide at x_max)."""
    lv, lz = P.limit_vz
    xi = _inner_x()
    x_tip = P.x_max + P.slide_half_x + 1.0
    return to_robot(cyl(10, V(xi, lv, lz), V(-1, 0, 0), xi - x_tip))


def chain_bracket():
    """Support under the fixed end of the cable chain, on the left side plate."""
    x0 = -P.xbar_L / 2
    tv = S["tube"]
    zk = P.chain_z
    z_ep = P.side_plate_z[1]
    return to_robot(box(x0, x0 + 90, tv - 25, tv + 25, zk - 6, zk).fuse(
        box(x0, x0 + P.end_plate_t, tv - 25, tv + 25, z_ep, zk - 6)))


# ---------------------------------------------------------------------
# X slide (moves in x; drawn at x = 0): slide, 3 X housings in front, belt clamp; rail beams and rails at the back
# ---------------------------------------------------------------------
def x_house_positions():
    """(x, z) of the 3 X housings: 2 on the upper tube, 1 in the middle of the lower tube."""
    zl, zh = P.xbar_z
    h = P.xg_upper_pitch / 2
    return [(-h, zh), (h, zh), (0.0, zl)]


def _x_house_bolt_pts():
    bx, bz = P.xg_house_bolt
    return [(xh + dx, zh + dz, zh == P.xbar_z[0]) for xh, zh in x_house_positions() for dx in (-bx, bx)
            for dz in (-bz, bz)]


def x_houses():
    """X housing (block): from the slide to 32 in front of the tube centre, bore = outside of the bush (axis along
    x); 4 holes M8 with a counterbore for the head at the front (robot side)."""
    v_front = S["tube"] - P.xg_house[2]
    v1 = S["slide"][0]
    w, L, _ = P.xg_house
    out = []
    for xh, zh in x_house_positions():
        b = box(xh - L / 2, xh + L / 2, v_front, v1, zh - w / 2, zh + w / 2)
        b = b.cut(cyl(P.xg_bush_d / 2, V(xh - L / 2 - 1, S["tube"], zh), ALONG_X, L + 2))
        for (bx, bz, _) in _x_house_bolt_pts():
            if abs(bx - xh) < L / 2 and abs(bz - zh) < w / 2:
                b = b.cut(cyl(4.5, V(bx, v_front - 1, bz), ALONG_V, v1 - v_front + 2))
                b = b.cut(cyl(7.0, V(bx, v_front - 1, bz), ALONG_V, 9))
        out.append(b)
    return to_robot(compound(out))


def x_bushes():
    """Plain bush (iglidur) D50 inside, D60 outside, as long as the housing, axis along x."""
    L = P.xg_house[1]
    return to_robot(compound([pipe(P.xg_bush_d / 2, P.xg_d / 2 + 0.1, V(xh - L / 2, S["tube"], zh), ALONG_X, L)
                              for xh, zh in x_house_positions()]))


def x_house_bolts():
    """M8 from the front through the housing into the slide (Helicoil in the alu), head counterbored in the housing."""
    v_front = S["tube"] - P.xg_house[2]
    v_end = S["slide"][1] - 2.0
    return to_robot(compound([cyl(4, V(bx, v_front + 8, bz), ALONG_V, v_end - v_front - 8).fuse(
        cyl(6.5, V(bx, v_front + 2.5, bz), ALONG_V, 5.5)) for bx, bz, _ in _x_house_bolt_pts()]))


def x_wipers():
    """Wiper (rubber) left and right of each X housing, round the tube."""
    L = P.xg_house[1]
    out = []
    for xh, zh in x_house_positions():
        for x0 in (xh - L / 2 - P.xg_wiper_t, xh + L / 2):
            out.append(pipe(P.xg_d / 2 + 6, P.xg_d / 2, V(x0, S["tube"], zh), ALONG_X, P.xg_wiper_t))
    return to_robot(compound(out))


def x_grease_nipples():
    """Grease nipple under each X housing (the cable chain runs on top, the cross beam in front)."""
    w = P.xg_house[0]
    return to_robot(compound([cyl(3.2, V(xh, S["tube"], zh - w / 2 - 12), UP, 12) for xh, zh in x_house_positions()]))


def _zb_bolt_pts():
    return [(s * P.zr_dx, z) for s in (-1, 1) for z in P.zb_bolt_z]


def x_slide():
    """X slide alu 12 mm with an extension for the top actuator pin (as v8, without the X motor).
    Holes: M8 of the X housings (lower housing: slots in z), M8 of the rail beams, cable hole."""
    v0, v1 = S["slide"]
    h = P.slide_half_x
    tx0, tx1, tz1 = P.slide_tab
    p = box(-h, h, v0, v1, P.slide_z[0], P.slide_z[1]).fuse(box(tx0, tx1, v0, v1, P.slide_z[1] - 1, tz1)).removeSplitter()
    for (bx, bz, lower) in _x_house_bolt_pts():
        if lower:
            p = p.cut(box(bx - 4.5, bx + 4.5, v0 - 1, v1 + 1, bz - 8, bz + 8))
        else:
            p = p.cut(cyl(4.0, V(bx, v0 - 1, bz), ALONG_V, P.slide_t + 2))
    for (bx, bz) in _zb_bolt_pts():
        p = p.cut(cyl(4.5, V(bx, v0 - 1, bz), ALONG_V, P.slide_t + 2))
    p = p.cut(cyl(25, V(0, v0 - 1, 980.0), ALONG_V, P.slide_t + 2))         # cable hole
    return to_robot(p)


def belt_clamp():
    """Belt clamp with bracket on the front of the slide, round the lower belt run (x -30..30). (As v9.)"""
    c = P.belt_clamp_half_x
    v0 = P.belt_v[0] - 4.0
    z0, z1 = P.belt_z - P.belt_r[1] - 6.0, P.belt_z - P.belt_r[0] + 6.0
    return to_robot(box(-c, c, v0, S["slide"][0], z0, z1))


def chain_driver():
    """Driver of the cable chain (on the front of the X slide)."""
    xm = -80.0
    tv = S["tube"]
    zk = P.chain_z
    v0 = S["slide"][0]
    return to_robot(box(xm - 20, xm + 20, tv - 25, v0, zk + 80, zk + 86).fuse(
        box(xm - 20, xm + 20, v0 - 3, v0, P.slide_z[1] - 8, zk + 86)))


# ---------------------------------------------------------------------
# Z rail frame (fixed on the X slide): 2 rail beams RHS 50 x 40 x 4, 2 rails HGR20, end stops
# ---------------------------------------------------------------------
def rail_beam(side):
    """Rail beam RHS 50 x 40 x 4 (50 in v) at x = side * zr_dx against the back of the X slide, from z 210 to the top
    of the slide; front wall tapped M8 (4x) for the bolts through the slide, back wall carries the rail (M5)."""
    xc = side * P.zr_dx
    d, w, t = P.zb_size
    v0, v1 = S["zb"]
    z0, z1 = P.zb_z
    b = tube_rect(xc - w / 2, xc + w / 2, v0, v1, z0, z1, t, "z")
    for (bx, bz) in _zb_bolt_pts():
        if bx * side > 0:
            b = b.cut(cyl(4.0, V(bx, v0 - 1, bz), ALONG_V, t + 2))
    for z in _rail_holes_z():
        b = b.cut(cyl(2.5, V(xc, v1 - t - 1, z), ALONG_V, t + 2))
    return to_robot(b)


def rail_beam_caps():
    """End cap 5 mm welded under each rail beam (closes the tube against dirt)."""
    d, w, t = P.zb_size
    v0, v1 = S["zb"]
    z0 = P.zb_z[0]
    return to_robot(compound([box(s * P.zr_dx - w / 2, s * P.zr_dx + w / 2, v0, v1, z0 - P.zb_cap_t, z0)
                              for s in (-1, 1)]))


def rail_beam_bolts():
    """8x M8 from the front through the X slide into the front wall of the rail beams (tapped / rivet nut)."""
    v0 = S["slide"][0]
    v_end = S["zb"][0] + P.zb_size[2] + 4.0
    out = []
    for (bx, bz) in _zb_bolt_pts():
        out.append(cyl(4.0, V(bx, v0, bz), ALONG_V, v_end - v0).fuse(cyl(6.5, V(bx, v0 - 8.0, bz), ALONG_V, 8.0)))
    return to_robot(compound(out))


def _rail_holes_z():
    z0, z1 = P.rail_z
    n = int((z1 - z0) // P.rail_pitch)
    e = (z1 - z0 - n * P.rail_pitch) / 2.0
    return [z0 + e + k * P.rail_pitch for k in range(n + 1)]


def hgr20_rail(xc):
    """Profile rail HGR20 along z, foot on v = rail_v0, standing to +v; ball grooves at the sides; counterbored M5
    holes every 60 mm."""
    z0, z1 = P.rail_z
    v0 = P.rail_v0
    w = P.rail_w / 2
    r = box(xc - w, xc + w, v0, v0 + P.rail_h, z0, z1)
    for s in (-1, 1):
        xg = xc + s * w
        r = r.cut(box(xg - 2.0, xg + 2.0, v0 + 9.0, v0 + 13.0, z0 - 1, z1 + 1))
    for z in _rail_holes_z():
        r = r.cut(cyl(3.0, V(xc, v0 - 1, z), ALONG_V, P.rail_h + 2))
        r = r.cut(cyl(4.75, V(xc, v0 + P.rail_h - 8.5, z), ALONG_V, 9.5))
    return r


def z_rails():
    return to_robot(compound([hgr20_rail(s * P.zr_dx) for s in (-1, 1)]))


def rail_bolts():
    """M5 x 25 cap screws in the counterbores of the rails, into the back wall of the rail beams (tapped M5)."""
    v0 = P.rail_v0
    out = []
    for s in (-1, 1):
        for z in _rail_holes_z():
            xc = s * P.zr_dx
            head = cyl(4.0, V(xc, v0 + P.rail_h - 8.5 + 2.0, z), ALONG_V, 5.0)
            shank = cyl(2.5, V(xc, v0 - P.zb_size[2], z), ALONG_V, P.rail_h - 8.5 + 2.0 + P.zb_size[2])
            out.append(head.fuse(shank))
    return to_robot(compound(out))


def rail_stops():
    """Rubber end stops under and above each rail, on the back of the rail beam."""
    w, d, h = P.rail_stop
    v0 = P.rail_v0
    z0, z1 = P.rail_z
    out = []
    for s in (-1, 1):
        xc = s * P.zr_dx
        out.append(box(xc - w / 2, xc + w / 2, v0, v0 + d, z0 - h, z0))
        out.append(box(xc - w / 2, xc + w / 2, v0, v0 + d, z1, P.zb_z[1]))
    return to_robot(compound(out))


# Actuator Linak LA36 (fixed part on the X slide): top pin, housing, outer tube. Dimensions from the datasheet.
def _act_pin_z():
    return P.act_pin_z


def _act_eye_z():
    """Rod eye at z_ref (drawn in the Z sled): retracted = driving position."""
    return P.z_ref + P.act_eye_dz


def _act_house_z():
    top = _act_pin_z() - P.act_house_dz
    return top - P.act_house_L, top


def _clevis(xc, vc, zc, v_base, inner, z_lo=-22.0, z_hi=25.0):
    """2 cheeks 8 mm (v-z plane) from v_base to behind the pin, pin hole along x; inner = half the inside width."""
    out = []
    for s in (-1, 1):
        x0 = xc + inner if s > 0 else xc - inner - 8.0
        c = box(x0, x0 + 8.0, v_base, vc + 25, zc + z_lo, zc + z_hi)
        out.append(c.cut(cyl(P.act_pin_d / 2, V(x0 - 1, vc, zc), ALONG_X, 10)))
    return out


def act_top_bracket():
    """Top bracket: base plate 8 mm on the extension of the X slide + 2 cheeks 8 mm."""
    v1 = S["slide"][1]
    zp = _act_pin_z()
    xc = P.act_x
    tx0, tx1, tz1 = P.slide_tab
    base = box(tx0, tx1, v1, v1 + 8, zp - 22, tz1)
    return to_robot(fuse([base] + _clevis(xc, S["act"], zp, v1 + 8, P.act_back_c / 2 + 1.0)))


def act_pin_top():
    zp = _act_pin_z()
    return to_robot(cyl(P.act_pin_d / 2 - 0.1, V(P.act_x - 24, S["act"], zp), ALONG_X, 48))


def act_body():
    """LA36: housing 76 wide, 148 high (36 in front / 112 behind the axis), 230 long; rear mount D25.2;
    outer tube 44.5 x 50 to act_tube_end above the rod eye (retracted)."""
    xc, vc = P.act_x, S["act"]
    zp = _act_pin_z()
    z0, z1 = _act_house_z()
    w = P.act_house_w / 2
    hf, hb = P.act_house_h
    house = box(xc - w, xc + w, vc - hf, vc + hb, z0, z1)
    lug = cyl(P.act_back_c / 2, V(xc, vc, z1 - 1), UP, zp + 13.0 - z1 + 1)
    lug = lug.cut(cyl(P.act_pin_d / 2, V(xc - 20, vc, zp), ALONG_X, 40))
    tz0 = _act_eye_z() + P.act_tube_end
    tw, tv = P.act_tube
    tube = box(xc - tw / 2, xc + tw / 2, vc - tv / 2, vc + tv / 2, tz0, z0 + 1)
    tube = tube.cut(cyl(P.act_rod_d / 2 + 0.5, V(xc, vc, tz0 - 1), UP, z0 - tz0 + 1))
    return to_robot(fuse([house, lug, tube]))


SPIRAL_X = P.spiral_x
SPIRAL_Z0 = P.spiral_z0


def cable_bracket_x():
    """Bracket on the back of the X slide at the top right: fixed anchor of the spiral cable."""
    v1 = S["slide"][1]
    return to_robot(box(SPIRAL_X - 26, SPIRAL_X + 26, v1, P.spiral_v + 15, SPIRAL_Z0 - 6, SPIRAL_Z0))


# ---------------------------------------------------------------------
# Camera: fixed, high above the spindle line (as v5..v8)
# ---------------------------------------------------------------------
def camera_mast():
    x = P.cam_mast_x
    v0 = P.up_v0
    return to_robot(tube_rect(x - 20, x + 20, v0, v0 + 40, P.up_z1 + P.up_cap_t, P.cam_z, 3, "z"))


def camera_arm():
    x = P.cam_mast_x
    v0 = P.up_v0
    return to_robot(tube_rect(x - 20, x + 20, v0 + 40, P.cam_v + 20, P.cam_z - 40, P.cam_z, 3, "v"))


def camera_crossbar():
    return to_robot(tube_rect(P.cam_x - 20, P.cam_mast_x - 20, P.cam_v - 20, P.cam_v + 20, P.cam_z - 40, P.cam_z, 3, "x"))


def camera():
    xc, cv = P.cam_x, P.cam_v
    z1 = P.cam_z - 40
    return to_robot(box(xc - 30, xc + 30, cv - 28, cv + 28, z1 - 65, z1).fuse(cyl(14, V(xc, cv, z1 - 90), UP, 25)))


def led_bar():
    cv = P.cam_v
    z1 = P.cam_z - 40
    return to_robot(box(P.cam_x + 40, P.cam_x + 200, cv - 15, cv + 15, z1 - 30, z1))


# ---------------------------------------------------------------------
# Z sled with carriages, spindle bracket, spindle and motor (moves in z; drawn at z_ref)
# ---------------------------------------------------------------------
def _zc():
    return P.z_ref


def _sled_z():
    zc = _zc()
    return zc + P.sled_z[0], zc + P.sled_z[1]


def carriage_positions():
    """(x, z) of the 4 carriages HGH20CA at z_ref."""
    zc = _zc()
    return [(s * P.zr_dx, zc + zb) for s in (-1, 1) for zb in P.blk_z]


def _blk_bolt_pts():
    bx, bz = P.blk_bolt
    return [(xc + dx, zc + dz) for xc, zc in carriage_positions() for dx in (-bx / 2, bx / 2) for dz in (-bz / 2, bz / 2)]


def hgh20_carriage(xc, zc):
    """Carriage HGH20CA on a z rail: steel body (L1 50.5) + end caps with seals (to L 77.5); the inside clears the
    rail by 0.5 mm (the balls are not drawn); 4 tapped M5 in the top face."""
    v0 = P.rail_v0
    w = P.blk_W / 2
    top = v0 + P.blk_H
    low = v0 + P.blk_H1
    body = box(xc - w, xc + w, low, top, zc - P.blk_L1 / 2, zc + P.blk_L1 / 2)
    caps = [box(xc - w + 1.5, xc + w - 1.5, low + 1.0, top - 1.5, zc + P.blk_L1 / 2, zc + P.blk_L / 2),
            box(xc - w + 1.5, xc + w - 1.5, low + 1.0, top - 1.5, zc - P.blk_L / 2, zc - P.blk_L1 / 2)]
    b = fuse([body] + caps)
    b = b.cut(box(xc - P.rail_w / 2 - 0.5, xc + P.rail_w / 2 + 0.5, low - 1, v0 + P.rail_h + 0.5,
                  zc - P.blk_L / 2 - 1, zc + P.blk_L / 2 + 1))
    bx, bz = P.blk_bolt
    for dx in (-bx / 2, bx / 2):
        for dz in (-bz / 2, bz / 2):
            b = b.cut(cyl(2.5, V(xc + dx, top - 8.0, zc + dz), ALONG_V, 9.0))
    return b


def z_carriages():
    return to_robot(compound([hgh20_carriage(xc, zc) for xc, zc in carriage_positions()]))


def carriage_grease_nipples():
    """Grease nipple on the upper end cap of each carriage (M6, along z)."""
    v = P.rail_v0 + (P.blk_H1 + P.blk_H) / 2 + 4.0
    out = []
    for xc, zc in carriage_positions():
        out.append(cyl(3.0, V(xc + 15.0, v, zc + P.blk_L / 2), UP, 10.0))
    return to_robot(compound(out))


def carriage_bolts():
    """16x M5 x 16 from the back of the sled into the carriages, head on the back of the sled."""
    v_sled = S["sb_back"]
    v_top = P.rail_v0 + P.blk_H
    out = []
    for (bx, bz) in _blk_bolt_pts():
        shank = cyl(2.5, V(bx, v_top - 8.0, bz), ALONG_V, v_sled[1] - v_top + 8.0)
        head = cyl(4.25, V(bx, v_sled[1], bz), ALONG_V, 5.0)
        out.append(shank.fuse(head))
    return to_robot(compound(out))


def z_sled():
    """Z sled = back plate of the spindle bracket: 6 mm plate bent into a U (web 252 wide, flanges 26 forward, beside
    the carriages, like the rusty sled in the photo). 16 holes M5 for the carriages, 2 lightening windows. The lower
    plate, side plates and top plate of the spindle bracket and the rod-eye bracket are welded to it."""
    z0, z1 = _sled_z()
    v0, v1 = S["sb_back"]
    h = P.sled_half_x
    t = P.sled_t
    web = box(-h, h, v0, v1, z0, z1)
    flanges = [box(h - t, h, v0 - P.sled_flange, v0, z0, z1), box(-h, -h + t, v0 - P.sled_flange, v0, z0, z1)]
    p = fuse([web] + flanges)
    for (bx, bz) in _blk_bolt_pts():
        p = p.cut(cyl(2.75, V(bx, v0 - 1, bz), ALONG_V, t + 2))
    (wx0, wx1), (wz0, wz1) = P.sled_win
    for s in (-1, 1):
        xa, xb = sorted((s * wx0, s * wx1))
        p = p.cut(box(xa, xb, v0 - 1, v1 + 1, _zc() + wz0, _zc() + wz1))
    return to_robot(p)


def sled_blank():
    """Flat blank of the sled for the laser (before bending): web + 2 flanges unfolded at the neutral line (k 0.4),
    with the carriage holes and windows. Drawn in the v plane (normal y) at z_ref."""
    z0, z1 = _sled_z()
    v0, v1 = S["sb_back"]
    t = P.sled_t
    r_in = t                                            # inner bend radius = thickness
    bend = math.pi / 2 * (r_in + 0.4 * t)               # arc length of one 90 degree bend
    flat_flange = P.sled_flange - t - r_in              # straight part of the flange
    web = 2 * (P.sled_half_x - t - r_in)                # straight part of the web
    h = web / 2 + bend + flat_flange
    p = box(-h, h, v0, v1, z0, z1)
    for (bx, bz) in _blk_bolt_pts():
        p = p.cut(cyl(2.75, V(bx, v0 - 1, bz), ALONG_V, t + 2))
    (wx0, wx1), (wz0, wz1) = P.sled_win
    for s in (-1, 1):
        xa, xb = sorted((s * wx0, s * wx1))
        p = p.cut(box(xa, xb, v0 - 1, v1 + 1, _zc() + wz0, _zc() + wz1))
    return to_robot(p)


def act_eye_bracket():
    """Bracket on the front of the sled (x 0): bottom 8 mm + 2 cheeks 8 mm round the rod eye (the bracket with the
    hole in the middle of the photo)."""
    xc, vc = P.act_x, S["act"]
    ze = _act_eye_z()
    inner = P.act_eye_c / 2 + 1.0
    v0, v1 = vc - 22, S["sb_back"][0]
    bottom = box(xc - inner - 8, xc + inner + 8, v0, v1, ze - 38, ze - 30)
    cheeks = []
    for x0 in (xc - inner - 8, xc + inner):
        c = box(x0, x0 + 8, v0, v1, ze - 30, ze + 18)
        cheeks.append(c.cut(cyl(P.act_pin_d / 2, V(x0 - 1, vc, ze), ALONG_X, 10)))
    return to_robot(fuse([bottom] + cheeks))


def act_rod():
    """Inner tube with solid rod eye D27.8 (hole 13.5 from the end); drawn retracted (driving position)."""
    xc, vc = P.act_x, S["act"]
    ze = _act_eye_z()
    top = _act_house_z()[0] - 2.0
    eye = cyl(P.act_eye_c / 2, V(xc, vc, ze - 13.5), UP, 30.0)
    eye = eye.cut(cyl(P.act_pin_d / 2, V(xc - 20, vc, ze), ALONG_X, 40))
    rod = cyl(P.act_rod_d / 2, V(xc, vc, ze + 16.0), UP, top - ze - 16.0)
    return to_robot(rod.fuse(eye).removeSplitter())


def act_pin_eye():
    return to_robot(cyl(P.act_pin_d / 2 - 0.1, V(P.act_x - 26, S["act"], _act_eye_z()), ALONG_X, 52))


def _sb():
    zc = _zc()
    return zc + P.sb_lo, zc + P.sb_mo


def _bearing_z():
    zc = _zc()
    return zc + P.bearing_lo, zc + P.bearing_hi


def _sb_rear_v():
    """The side plates and the wide part of the top plate stop here: behind it run the rods of the can."""
    return S["spindle"] - 22.0


def sb_plate_lower():
    z_lo = _sb()[0]
    v1, vs = S["sb_back"][1], S["spindle"]
    w = P.sb_side_x + 2.5
    p = box(-w, w, v1, vs + 80, z_lo, z_lo + 8).fuse(box(-125, 125, vs - 25, vs + 45, z_lo, z_lo + 8)).removeSplitter()
    p = holes_z(p, [(0, vs)], 25, z_lo, 8)
    p = holes_z(p, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 10.5, z_lo, 8)
    return to_robot(p)


def sb_top_plate():
    z_mo = _sb()[1]
    v1, vs, vr = S["sb_back"][1], S["spindle"], _sb_rear_v()
    w = P.sb_side_x + 2.5
    p = box(-w, w, v1, vr, z_mo, z_mo + 8).fuse(box(-84, 84, vr - 1, vs + 80, z_mo, z_mo + 8)).removeSplitter()
    return to_robot(holes_z(p, [(0, vs)], P.shaft_d / 2 + 2, z_mo, 8))


def sb_side_plate(side):
    z_lo, z_mo = _sb()
    x = side * P.sb_side_x
    return to_robot(box(x - 2.5, x + 2.5, S["sb_back"][1], _sb_rear_v(), z_lo + 8, z_mo))


def _bearing_plate_v():
    vb = S["spindle"] - P.ucp_h
    return vb - P.bearing_plate_t, vb


def sb_bearing_plate():
    z_lo, z_mo = _sb()
    v0, v1 = _bearing_plate_v()
    w = P.sb_side_x - 2.5
    p = box(-w, w, v0, v1, z_lo + 8, z_mo)
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            p = p.cut(box(dx - 7.5, dx + 7.5, v0 - 1, v1 + 1, zb - 10.5, zb + 10.5))
    return to_robot(p)


def ucp(zb):
    vs = S["spindle"]
    vb = vs - P.ucp_h
    a, b, tf = P.ucp_L, P.ucp_b, P.ucp_foot_t
    foot = box(-a / 2, a / 2, vb, vb + tf, zb - b / 2, zb + b / 2)
    for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
        foot = foot.cut(box(dx - P.ucp_slot[0] / 2, dx + P.ucp_slot[0] / 2, vb - 1, vb + tf + 1,
                            zb - P.ucp_slot[1] / 2, zb + P.ucp_slot[1] / 2))
    r = P.ucp_ring_d / 2
    body = box(-r * 0.8, r * 0.8, vb + tf - 1, vs, zb - b / 2 + 4, zb + b / 2 - 4)
    ring = cyl(r, V(0, vs, zb - b / 2 + 4), UP, b - 8)
    inner = cyl(P.ucp_d / 2 + 7, V(0, vs, zb - P.ucp_ring_w / 2), UP, P.ucp_ring_w)
    h = foot.fuse(body).fuse(ring).fuse(inner).removeSplitter()
    return to_robot(h.cut(cyl(P.ucp_d / 2, V(0, vs, zb - b), UP, 2 * b)))


def bearing_lower():
    return ucp(_bearing_z()[0])


def bearing_upper():
    return ucp(_bearing_z()[1])


def bearing_bolts():
    v0, v1 = _bearing_plate_v()
    vt = v1 + P.ucp_foot_t
    out = []
    for zb in _bearing_z():
        for dx in (-P.ucp_bolt / 2, P.ucp_bolt / 2):
            out.append(cyl(7, V(dx, v0 - 12, zb), ALONG_V, vt - v0 + 20).fuse(cyl(11.5, V(dx, vt, zb), ALONG_V, 8.8)).fuse(
                cyl(11.5, V(dx, v0 - 11, zb), ALONG_V, 11)))
    return to_robot(compound(out))


def spindle_shaft():
    z0 = _zc() + 100
    return to_robot(cyl(P.shaft_d / 2, V(0, S["spindle"], z0), UP, _zc() + P.shaft_top - z0))


def _flange_holes(sh, v, z0, t):
    for k in range(4):
        a = math.radians(45 + 90 * k)
        sh = sh.cut(cyl(5.5, V(40 * math.cos(a), v + 40 * math.sin(a), z0 - 1), UP, t + 2))
    return sh


def spindle_flange():
    z = _zc() + 100
    vs = S["spindle"]
    f = cyl(55, V(0, vs, z), UP, 12).cut(cyl(P.shaft_d / 2, V(0, vs, z - 1), UP, 14))
    return to_robot(_flange_holes(f, vs, z, 12))


def jaw_coupling():
    vs = S["spindle"]
    z0 = _zc() + P.jaw_z0
    r = P.jaw_d / 2
    hub = P.jaw_hub_L
    lo = pipe(r, P.shaft_d / 2, V(0, vs, z0), UP, hub)
    star = pipe(r - 1.5, 6.0, V(0, vs, z0 + hub), UP, P.jaw_star)
    hi = pipe(r, P.motor_shaft_d / 2, V(0, vs, z0 + hub + P.jaw_star), UP, hub)
    return to_robot(compound([lo, star, hi]))


def _motor_z(d):
    return _zc() + P.motor_shaft_end + d


def spindle_motor():
    vs = S["spindle"]
    zs = _motor_z(0)
    d0, d1, da, db = P.motor_nose
    parts = [Part.makeCone(da / 2, db / 2, d1 - d0, V(0, vs, zs + d0), UP)]
    for (a, b, dia) in (P.motor_ring, P.motor_body, P.motor_cap):
        parts.append(cyl(dia / 2, V(0, vs, zs + a), UP, b - a))
    xf = P.motor_foot_h
    za, zb = _motor_z(P.motor_foot[0]), _motor_z(P.motor_foot[1])
    foot = box(xf - P.motor_foot_t, xf, vs - P.motor_foot_w / 2, vs + P.motor_foot_w / 2, za, zb)
    for d in P.motor_foot_holes:
        for dv in (-P.motor_foot_hole_dx / 2, P.motor_foot_hole_dx / 2):
            foot = foot.cut(cyl(4.25, V(xf - P.motor_foot_t - 1, vs + dv, _motor_z(d)), ALONG_X, P.motor_foot_t + 2))
    saddle = box(40, xf - P.motor_foot_t + 1, vs - 30, vs + 30, za + 8, zb - 8)
    parts += [foot, saddle]
    return to_robot(fuse(parts))


def spindle_motor_shaft():
    zs = _motor_z(0)
    return to_robot(cyl(P.motor_shaft_d / 2, V(0, S["spindle"], zs), UP, P.motor_shaft_out))


def motor_plate():
    vs = S["spindle"]
    z0 = _sb()[1] + 8
    x0 = P.motor_foot_h
    v0, v1 = vs + P.motor_plate_v[0], vs + P.motor_plate_v[1]
    p = box(x0, x0 + P.motor_plate_t, v0, v1, z0, _motor_z(P.motor_foot[1]) + 12)
    for d in P.motor_foot_holes:
        for dv in (-P.motor_foot_hole_dx / 2, P.motor_foot_hole_dx / 2):
            z = _motor_z(d)
            p = p.cut(box(x0 - 1, x0 + P.motor_plate_t + 1, vs + dv - 4.25, vs + dv + 4.25, z - 7, z + 7))
    return to_robot(p)


def motor_gussets():
    vs = S["spindle"]
    z0 = _sb()[1] + 8
    x1 = P.motor_foot_h
    out = []
    for v in (vs + P.motor_plate_v[0], vs + P.motor_plate_v[1] - P.gusset_mp_t):
        pts = [V(x1, v, z0), V(x1, v, z0 + 95), V(x1 - 60, v, z0)]
        out.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, P.gusset_mp_t, 0)))
    return to_robot(compound(out))


def cable_bracket_z():
    """Arm welded on the outside of the right sled flange: moving anchor of the spiral cable."""
    z1 = _zc() + P.spiral_dz
    h = P.sled_half_x
    v = P.spiral_v
    return to_robot(box(h, SPIRAL_X + 26, v - 15, v + 15, z1 - 6, z1))


def pot_bushes():
    z = _sb()[0] + 8
    vs = S["spindle"]
    return to_robot(compound([pipe(19, 8.5, V(s * P.pot_rod_dx, vs, z), UP, 25) for s in (-1, 1)]))


def _ring_z():
    return _sb()[0] + 8 + 25 + 1


def pot_sensor():
    vs = S["spindle"]
    return to_robot(cyl(6, V(P.pot_rod_dx, vs + 20, _ring_z() + 6), ALONG_V, 20))


def pot_sensor_bracket():
    vs = S["spindle"]
    z0 = _sb()[0] + 8
    return to_robot(box(P.pot_rod_dx - 8, P.pot_rod_dx + 8, vs + 40, vs + 43, z0, _ring_z() + 16))


# ---------------------------------------------------------------------
# Can (as Robot Ruud): piece of steel pipe with lid; hangs at rest, drawn with the rim at pot_rim_ref()
# ---------------------------------------------------------------------
def _rim():
    return pot_rim_ref()


def pot_shell():
    R = P.pot_d / 2
    return to_robot(pipe(R, R - P.pot_t, V(0, S["spindle"], _rim()), UP, P.pot_h))


def pot_lid():
    R = P.pot_d / 2
    vs = S["spindle"]
    z = _rim() + P.pot_h
    d = holes_z(cyl(R, V(0, vs, z), UP, P.pot_lid_t), [(0, vs)], 25, z, P.pot_lid_t)
    return to_robot(holes_z(d, [(-P.pot_rod_dx, vs), (P.pot_rod_dx, vs)], 8, z, P.pot_lid_t))


def shaft_seal():
    return to_robot(pipe(28, P.shaft_d / 2 + 0.5, V(0, S["spindle"], _rim() + P.pot_h + P.pot_lid_t), UP, 8))


def _rod_len():
    ring0 = _ring_z()
    return ring0 + 12 - (_rim() + P.pot_h + P.pot_lid_t)


def pot_rods():
    z = _rim() + P.pot_h + P.pot_lid_t
    vs = S["spindle"]
    return to_robot(compound([cyl(P.pot_rod_d / 2, V(s * P.pot_rod_dx, vs, z), UP, _rod_len()) for s in (-1, 1)]))


def pot_set_rings():
    z = _ring_z()
    vs = S["spindle"]
    return to_robot(compound([pipe(14, 8, V(s * P.pot_rod_dx, vs, z), UP, 12) for s in (-1, 1)]))


# ---------------------------------------------------------------------
# Tool (turns about the spindle axis; drawn at x = 0, underside at z_ref)
# ---------------------------------------------------------------------
def _cross(L, b, t, hole=0.0):
    k = Part.makeBox(L, b, t, V(-L / 2, -b / 2, 0)).fuse(Part.makeBox(b, L, t, V(-b / 2, -L / 2, 0)))
    k = k.fuse(cyl(b * 1.25, V(0, 0, 0), UP, t)).removeSplitter()
    if hole > 0:
        k = k.cut(cyl(hole, V(0, 0, -1), UP, t + 2))
    for i in range(4):          # cutting edge: chamfer on the leading underside of each arm
        pts = [V(22, b / 2 + 0.01, -0.01), V(22, b / 2 - 9, -0.01), V(22, b / 2 + 0.01, t * 0.55)]
        wedge = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(L / 2 - 20, 0, 0))
        wedge.rotate(V(0, 0, 0), UP, 90 * i)
        k = k.cut(wedge)
    return k


def cutter_parts():
    """Crushing cutter D180: (name, shape, colour) in robot coordinates. Underside of the teeth at z_ref."""
    zc = _zc()
    vs = S["spindle"]
    R = P.cutter_d / 2
    out = []
    lo = _cross(2 * (R - 8), 30, 10)
    lo.translate(V(0, vs, zc + 25))
    out.append(("cutter_cross_lower", lo, "hardox"))
    teeth = []
    for i in range(P.cutter_teeth):
        t = Part.makeBox(18, 10, 25, V(R - 18, 5, 0))
        t.rotate(V(0, 0, 0), UP, 90 * i)
        t.translate(V(0, vs, zc))
        teeth.append(t)
    out.append(("cutter_teeth", compound(teeth), "hardox"))
    hi = _cross(2 * (R - 5), 28, 10, hole=24.4)
    hi.rotate(V(0, 0, 0), UP, 45)
    hi.translate(V(0, vs, zc + 60))
    out.append(("cutter_cross_upper", hi, "hardox"))
    out.append(("cutter_core_tube", pipe(24.15, 19.15, V(0, vs, zc + 35), UP, 55), "steel"))
    out.append(("cutter_flange", _flange_holes(cyl(55, V(0, vs, zc + 90), UP, 10), vs, zc + 90, 10), "steel"))
    out.append(("cutter_centre_point", Part.makeCone(1.0, 12.0, 60, V(0, vs, zc - 35), UP), "chrome"))
    return [(n, to_robot(s), c) for n, s, c in out]


# ---------------------------------------------------------------------
# Electrics (fixed) and cables (follow x and z)
# ---------------------------------------------------------------------
def ebox_plate():
    w = P.ebox[0] / 2
    return to_robot(box(-w, w, P.up_v0 - P.ebox_plate_t, P.up_v0, P.cross_z[0], P.ebox_z0 + P.ebox[1] + 5))


def ebox():
    w, h, d = P.ebox[0] / 2, P.ebox[1], P.ebox[2]
    v1 = P.up_v0 - P.ebox_plate_t
    return to_robot(box(-w, w, v1 - d, v1, P.ebox_z0, P.ebox_z0 + h))


def ebox_glands():
    v = P.up_v0 - P.ebox_plate_t - P.ebox[2] / 2
    return to_robot(compound([cyl(10, V(-P.ebox[0] / 2 + 30 + 60 * k, v, P.ebox_z0 - 20), UP, 20) for k in range(4)]))


def chain_shapes(x):
    """Cable chain with the slide at x: (lower run, upper run, bend) (as v6 / v8)."""
    x_fixed = -P.xbar_L / 2 + 30
    x_mov = x - 80
    x_b = max(x_fixed, x_mov) + 120
    tv = S["tube"]
    v0, v1 = tv - 25, tv + 25
    zk = P.chain_z
    lower = box(x_fixed, x_b, v0, v1, zk, zk + 25)
    upper = box(x_mov, x_b, v0, v1, zk + 55, zk + 80)
    bend = box(x_b, x_b + 25, v0, v1, zk, zk + 80)
    return to_robot(lower), to_robot(upper), to_robot(bend)


def spiral_cable(x, z_tool):
    """Spiral cable from the bracket at the top of the X slide (fixed) down to the arm on the sled flange (moves)."""
    z_a = SPIRAL_Z0 - 6.0
    z_c = z_tool + P.spiral_dz
    n = P.spiral_turns
    pitch = (z_c - z_a) / n
    rings = [Part.makeTorus(22, 4.5, V(x + SPIRAL_X, P.spiral_v, z_a + pitch * (k + 0.5)), UP) for k in range(n)]
    return to_robot(compound(rings))


# ---------------------------------------------------------------------
# Surroundings (only for images and animation)
# ---------------------------------------------------------------------
def leaf(length, width, thick):
    e = Part.Ellipse(V(0, 0, 0), length / 2, width / 2)
    s = Part.Face(Part.Wire(e.toShape())).extrude(V(0, 0, thick))
    s.translate(V(length / 2, 0, 0))
    return s


def dock_plant(x, y, scale=1.0, z=0.0, spin=0.0):
    """Broad-leaved dock: rosette of 7 leaves, root crown and tap root. Returns (leaves, root)."""
    leaves = []
    for i in range(7):
        b = leaf((230 - 15 * (i % 3)) * scale, 85 * scale, 3)
        b.rotate(V(0, 0, 0), V(0, 1, 0), -22)
        b.rotate(V(0, 0, 0), UP, i * 360.0 / 7 + 10 + spin)
        b.translate(V(x, y, z + 12 * scale))
        leaves.append(b)
    root = cyl(22 * scale, V(x, y, z - 10), UP, 26 * scale).fuse(
        Part.makeCone(2.0, 20.0 * scale, 320 * scale, V(x, y, z - 10 - 320 * scale), UP))
    return compound(leaves), root
