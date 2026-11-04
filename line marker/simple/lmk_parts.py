"""Parts of the sports field line marker. Every function returns a Part shape in robot coordinates. The paint head is
drawn with the carriage at x = 0; build_lmk.py puts it in its own sub-Part that moves in x (Placement), and the drag
chain is regenerated for the carriage position (chain(c)).

Tank, cradle, pump, filter, regulator, suction / return hoses and the control box are the spot sprayer's (ssp_parts);
the rail bolts and the control-box base plate with the extra holes are the drop-on-demand boom's (ddb_parts); this file
adds the belly rails with the post holes, the hanger posts, the belt module, the drag chain and the paint head.
"""
import math

import Part
from FreeCAD import Vector as V

import lmk_params as P
import ssp_parts as SG
import ddb_parts as DG

box_span = SG.box_span
cyl_x = SG.cyl_x
cyl_y = SG.cyl_y
cyl_z = SG.cyl_z
fuse_all = SG.fuse_all
hose = SG.hose
square_tube_z = SG.square_tube_z
square_tube_y = DG.square_tube_y

NY = P.nozzle_y
POSTS = [(sx * P.post_x, NY) for sx in (-1, 1)]
POST_TOP = P.rail_z[0] - P.post_foot[2]                 # 571: underside of the foot plate
POST_BOT = P.mod_top + P.post_plate[2]                  # 478: top of the bottom plate
MOD_Y = (NY - P.mod_w / 2.0, NY + P.mod_w / 2.0)        # -530 .. -470
CAR_Y = (NY - P.car_w / 2.0, NY + P.car_w / 2.0)
HP_Z = (P.car_z[0] - P.head_plate[2], P.car_z[0])       # head plate 406 .. 412
SHROUD_TOP = P.shroud_bottom + P.shroud_h               # 200
CH_Y = P.chain_y
CH_H = P.chain[1]
LOW_Z = (P.chain_tray_z, P.chain_tray_z + CH_H)         # lower run 405 .. 425
UP_Z = (LOW_Z[0] + 2.0 * P.chain_r, LOW_Z[1] + 2.0 * P.chain_r)   # upper run 455 .. 475
ARM_Y = (CH_Y[1] + 3.0, CH_Y[1] + 9.0)                  # vertical chain plate of the head, in front of the chain
TRAY_Y = (CH_Y[0] - 5.0, ARM_Y[0] - 1.0)               # lower run only: the head arm and hose pass in front
TRAY_X = (P.mod_x[0] - 6.0, P.mod_x[1] + 6.0)            # end plates on the end faces of the module
HANGER_X = ((TRAY_X[0], P.mod_x[0]), (P.mod_x[1], TRAY_X[1]))
FOLD_X = (P.mod_x[0], P.mod_x[0] + 25.0)                # fold-back belt box on the front face of the drive end
MOTOR_Y = MOD_Y[1] + 10.0 + P.nema / 2.0                # motor beside the body, in front of it
MOTOR_Z = (P.mod_z[0] + P.mod_z[1]) / 2.0


# ---------------------------------------------------------------------
# Belly rails (as the drop-on-demand boom's, with the foot holes of these posts)
# ---------------------------------------------------------------------
def _foot_bolts():
    return [(x, y + dy) for (x, y) in POSTS for dy in (-22.0, 22.0)]


def rails():
    zc = (P.rail_z[0] + P.rail_z[1]) / 2.0
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        t = square_tube_y(P.D.rail_y[0], P.D.rail_y[1], x, zc, P.rail, P.D.rail_wall)
        ends = [box_span((x - P.rail / 2.0, x + P.rail / 2.0), (y0, y0 + 3.0), P.rail_z)
                for y0 in (P.D.rail_y[0], P.D.rail_y[1] - 3.0)]
        t = fuse_all([t] + ends)
        holes = [cyl_z(P.m10_hole, P.rail_z[0] - 1, P.rail_z[1] + 1, bx, by) for (bx, by) in DG.RAIL_BOLTS if bx == x]
        holes += [cyl_z(8.5, P.rail_z[0] - 1, P.rail_z[0] + P.D.rail_wall + 1, bx, by) for (bx, by) in _foot_bolts()
                  if bx == x]
        out.append(t.cut(holes))
    return Part.makeCompound(out)


rail_bolts = DG.rail_bolts
box_base = DG.box_base


# ---------------------------------------------------------------------
# Hanger posts and their bolts
# ---------------------------------------------------------------------
def _plate_bolts():
    """4 x M6 per bottom plate into T-nuts in the top slots of the module."""
    return [(x + math.copysign(dx, x), NY + dy) for (x, _) in POSTS for dx in (-45.0, -25.0) for dy in (-15.0, 15.0)]


def posts():
    fx, fy, ft = P.post_foot
    px, py, pt = P.post_plate
    out = []
    for (x, y) in POSTS:
        tube = square_tube_z(POST_BOT, POST_TOP, x, y, P.post, P.post_wall)
        foot = box_span((x - fx / 2.0, x + fx / 2.0), (y - fy / 2.0, y + fy / 2.0), (POST_TOP, P.rail_z[0]))
        foot = foot.cut([cyl_z(8.5, POST_TOP - 1, P.rail_z[0] + 1, bx, by) for (bx, by) in _foot_bolts()
                         if bx == x])
        sx = math.copysign(1.0, x)
        plate = box_span((x - sx * (px - 15.0), x + sx * 15.0), (y - py / 2.0, y + py / 2.0), (P.mod_top, POST_BOT))
        plate = plate.cut([cyl_z(6.6, P.mod_top - 1, POST_BOT + 1, bx, by) for (bx, by) in _plate_bolts()
                           if abs(bx - x) < 60.0])
        out.append(fuse_all([tube, foot, plate]))
    return Part.makeCompound(out)


def post_bolts():
    """M8 from below into rivet nuts in the rail (feet); M6 from above into T-nuts in the module (bottom plates)."""
    out = []
    for (x, y) in _foot_bolts():
        head = SG.hex_prism_z(13.0, POST_TOP - 5.3, POST_TOP, x, y)
        shank = cyl_z(8.0, POST_TOP, P.rail_z[0] + P.D.rail_wall + 6.0, x, y)
        out.append(fuse_all([head, shank]))
    for (x, y) in _plate_bolts():
        head = cyl_z(10.0, POST_BOT, POST_BOT + 6.0, x, y)
        shank = cyl_z(6.0, P.mod_top - 5.0, POST_BOT, x, y)
        out.append(fuse_all([head, shank]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Belt module (hung upside down: carriage under the body), fold-back motor in front of the body
# ---------------------------------------------------------------------
def module_body():
    body = box_span(P.mod_x, MOD_Y, P.mod_z)
    for z in (P.mod_z[1] - 1.0, P.mod_z[0] + 1.0):          # T-slots top and bottom (8 mm, 6 deep)
        for dy in (-15.0, 15.0):
            zz = (z - 6.0, z + 1.0) if z > P.mod_z[0] + 5 else (z - 1.0, z + 6.0)
            body = body.cut(box_span((P.mod_x[0] + 1, P.mod_x[1] - 1), (NY + dy - 4.0, NY + dy + 4.0), zz))
    return body


def module_carriage(c=0.0):
    return box_span((c - P.car_len / 2.0, c + P.car_len / 2.0), CAR_Y, P.car_z)


def fold_box():
    """Fold-back belt box at the drive end: pulley of the module and of the motor, 1:1."""
    return box_span(FOLD_X, (MOD_Y[1], MOTOR_Y + P.nema / 2.0), P.mod_z)


def motor():
    x0 = FOLD_X[1]
    flange = box_span((x0, x0 + 8.0), (MOTOR_Y - P.nema / 2.0, MOTOR_Y + P.nema / 2.0),
                      (MOTOR_Z - P.nema / 2.0, MOTOR_Z + P.nema / 2.0))
    body = box_span((x0 + 8.0, x0 + 8.0 + P.nema_len), (MOTOR_Y - P.nema / 2.0 + 2, MOTOR_Y + P.nema / 2.0 - 2),
                    (MOTOR_Z - P.nema / 2.0 + 2, MOTOR_Z + P.nema / 2.0 - 2))
    plug = box_span((x0 + 8.0 + P.nema_len - 30.0, x0 + 8.0 + P.nema_len - 10.0),
                    (MOTOR_Y + P.nema / 2.0 - 2, MOTOR_Y + P.nema / 2.0 + 10.0), (MOTOR_Z - 10.0, MOTOR_Z + 10.0))
    return fuse_all([flange, body, plug])


def chain_tray():
    """Aluminium tray 3 mm behind the module for the lower run of the drag chain, on 2 hanger plates bolted to the
    rear face of the module (outside the carriage travel)."""
    tray = box_span(TRAY_X, TRAY_Y, (P.chain_tray_z - 3.0, P.chain_tray_z))
    lip = box_span(TRAY_X, (TRAY_Y[0], TRAY_Y[0] + 3.0), (P.chain_tray_z, P.chain_tray_z + 12.0))
    hangers = [box_span(hx, (TRAY_Y[0], MOD_Y[0] + 30.0), (P.chain_tray_z - 3.0, P.mod_z[1])) for hx in HANGER_X]
    return fuse_all([tray, lip] + hangers)


def chain(c=0.0):
    """Drag chain: fixed end at chain_fix_x on the tray, lower run on the tray, bend, upper run back to the moving end
    at the carriage x (c). Drawn as a solid band of the chain's outer section."""
    b = P.chain_fix_x + (P.chain_free + c) / 2.0          # x of the bend (start of the half circle)
    r_in, r_out = P.chain_r - CH_H / 2.0, P.chain_r + CH_H / 2.0
    zc = LOW_Z[0] + CH_H / 2.0 + P.chain_r
    low = box_span((P.chain_fix_x, b), CH_Y, LOW_Z) if b > P.chain_fix_x + 0.5 else None
    up = box_span((c, b), CH_Y, UP_Z) if b > c + 0.5 else None
    ring = Part.makeCylinder(r_out, CH_Y[1] - CH_Y[0], V(b, CH_Y[0], zc), V(0, 1, 0)).cut(
        Part.makeCylinder(r_in, CH_Y[1] - CH_Y[0] + 2, V(b, CH_Y[0] - 1, zc), V(0, 1, 0)))
    ring = ring.common(box_span((b, b + r_out + 1), (CH_Y[0] - 1, CH_Y[1] + 1), (zc - r_out - 1, zc + r_out + 1)))
    parts = [p for p in (low, up, ring) if p is not None]
    fix = box_span((P.chain_fix_x - 20.0, P.chain_fix_x), CH_Y, LOW_Z)     # fixed end bracket
    return fuse_all(parts + [fix])


def chain_length():
    return P.chain_free + math.pi * P.chain_r


def feed_hose():
    """Pressure hose from the spot-sprayer regulator (3 bar) down behind the pump into the fixed end of the chain."""
    x = P.S.feed_x
    z_run = P.mod_z[1] + 22.0                               # 492: under the pump motor (z 512) and the filter (480)
    yc = (CH_Y[0] + CH_Y[1]) / 2.0
    xf = P.chain_fix_x - 30.0
    return hose([(x, -475.0, P.S.regulator[2][0]), (x, -475.0, z_run), (x, yc, z_run), (xf, yc, z_run),
                 (xf, yc, LOW_Z[1] + 1.0)], od=12.0)


# ---------------------------------------------------------------------
# Paint head (moves in x with the carriage; drawn at c = 0)
# ---------------------------------------------------------------------
STEM_X = -35.0
VALVE_Z = (SHROUD_TOP, SHROUD_TOP + P.valve_body[2])


def head_plate():
    px, py, pt = P.head_plate
    plate = box_span((-px / 2.0, px / 2.0), (NY - py / 2.0, NY + py / 2.0), HP_Z)
    # arm to the moving end of the drag chain: back past the module, then a vertical plate up beside the chain
    arm = box_span((-20.0, 20.0), (ARM_Y[1], NY - py / 2.0), (HP_Z[0], HP_Z[0] + 6.0))
    up = box_span((-20.0, 20.0), ARM_Y, (HP_Z[0], UP_Z[1]))
    return fuse_all([plate, arm, up])


def stem():
    t = square_tube_z(SHROUD_TOP, HP_Z[0], STEM_X, NY, P.stem, P.stem_wall)
    foot = box_span((STEM_X - 25.0, STEM_X + 12.5), (NY - 25.0, NY + 25.0), (SHROUD_TOP, SHROUD_TOP + 5.0))
    gusset = SG.poly_xz([(STEM_X - 12.5, SHROUD_TOP + 5.0), (STEM_X - 12.5, SHROUD_TOP + 60.0),
                         (STEM_X - 45.0, SHROUD_TOP + 5.0)], NY - 2.5, 5.0)
    return fuse_all([t, foot, gusset])


def shroud():
    x, (y0, y1), t = P.shroud_x, P.shroud_y, P.shroud_t
    y0, y1 = NY + y0, NY + y1
    zb = P.shroud_bottom
    outer = box_span((-x, x), (y0, y1), (zb, SHROUD_TOP))
    inner = box_span((-x + t, x - t), (y0 + t, y1 - t), (zb - 1.0, SHROUD_TOP - t))
    s = outer.cut(inner)
    return s.cut(cyl_z(P.nozzle_body[0] + 2.0, SHROUD_TOP - 5, SHROUD_TOP + 1, 0.0, NY))


def brush():
    """Brush skirt round the shroud bottom (nylon 6 mm, in a folded holder): wind shield, sharp line edges."""
    x, (y0, y1) = P.shroud_x, P.shroud_y
    y0, y1 = NY + y0, NY + y1
    zb = P.shroud_bottom
    bt = P.brush_t
    o = box_span((-x - bt, x + bt), (y0 - bt, y1 + bt), (zb - P.brush_h + 10.0, zb + 20.0))
    i = box_span((-x, x), (y0, y1), (zb - P.brush_h, zb + 21.0))
    return o.cut(i)


def valve():
    vx, vy, vz = P.valve_body
    body = box_span((-vx / 2.0, vx / 2.0), (NY - vy / 2.0, NY + vy / 2.0), VALVE_Z)
    coil = cyl_z(32.0, VALVE_Z[1], VALVE_Z[1] + 30.0, 0.0, NY)
    plug = box_span((-8.0, 8.0), (NY + 16.0, NY + 30.0), (VALVE_Z[1] + 8.0, VALVE_Z[1] + 26.0))
    port = cyl_x(14.0, vx / 2.0, vx / 2.0 + 12.0, NY, VALVE_Z[0] + 25.0)
    return fuse_all([body, coil, plug, port])


def nozzle():
    d, _ = P.nozzle_body
    body = cyl_z(d, P.tip_z + 25.0, SHROUD_TOP + 1.0, 0.0, NY)
    cap = cyl_z(d + 6.0, P.tip_z + 6.0, P.tip_z + 25.0, 0.0, NY)
    tip = cyl_z(12.0, P.tip_z, P.tip_z + 6.0, 0.0, NY)
    return fuse_all([body, cap, tip])


def head_hose():
    """Hose from the moving end of the drag chain through the chain plate, down between the module and the plate,
    outside the head plate, into the valve port."""
    yc = (CH_Y[0] + CH_Y[1]) / 2.0
    yg = (MOD_Y[0] + ARM_Y[0]) / 2.0 - 1.0                  # gap between the module rear face and the chain plate
    xh = P.head_plate[0] / 2.0 + 10.0
    zt = (UP_Z[0] + UP_Z[1]) / 2.0
    vz = VALVE_Z[0] + 25.0
    xv = P.valve_body[0] / 2.0 + 12.0
    return hose([(8.0, yc, zt), (8.0, yg, zt), (xh, yg, zt), (xh, yg, 330.0), (xh, NY, 330.0), (xv + 10.0, NY, vz),
                 (xv - 1.0, NY, vz)], od=12.0)


def fan(t=4.0):
    """Spray fan (for the images): a thin triangle across, from the tip to the ground."""
    w = P.line_width() / 2.0
    return SG.poly_xz([(0.0, P.tip_z), (-w, 2.0), (w, 2.0)], NY - t / 2.0, t)


# ---------------------------------------------------------------------
# Ground with painted lines (images)
# ---------------------------------------------------------------------
def line_strip(x0, y0, x1, y1, w=100.0, z=1.0, t=0.8):
    """Painted line from (x0, y0) to (x1, y1)."""
    a, b = V(x0, y0, z), V(x1, y1, z)
    d = b - a
    L = d.Length
    s = Part.makeBox(L, w, t, V(0, -w / 2.0, 0))
    s.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(math.atan2(d.y, d.x)))
    s.translate(a)
    return s


def arc_strip(cx, cy, r, a0, a1, w=100.0, z=1.0, t=0.8):
    o = Part.makeCylinder(r + w / 2.0, t, V(cx, cy, z))
    i = Part.makeCylinder(r - w / 2.0, t + 2, V(cx, cy, z - 1))
    ring = o.cut(i)
    pts = [V(cx, cy, z - 2)]
    n = 24
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append(V(cx + 2 * (r + w) * math.cos(a), cy + 2 * (r + w) * math.sin(a), z - 2))
    pts.append(V(cx, cy, z - 2))
    wedge = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, t + 4))
    return ring.common(wedge)
