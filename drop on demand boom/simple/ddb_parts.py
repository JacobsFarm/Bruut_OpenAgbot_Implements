"""Parts of the drop-on-demand boom. Every function returns a Part shape in robot coordinates, hood at the middle
height step. Tank, cradle, pump, filter, regulator, suction / return hoses and the control box are the spot sprayer's
(ssp_parts, imported); this file adds the belly rails, the hanger posts, the hood with camera, LEDs and the injector
rail, and the feed hose. build_ddb.py puts the hood in its own sub-Part (moves with the height step).
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import ddb_params as P
import ssp_parts as SG

box_span = SG.box_span
cyl_x = SG.cyl_x
cyl_y = SG.cyl_y
cyl_z = SG.cyl_z
fuse_all = SG.fuse_all
hose = SG.hose
bolt_z = SG.bolt_z
bolt_y = SG.bolt_y
square_tube_z = SG.square_tube_z

RAIL_BOLTS = [(sx * P.rail_x, y) for sx in (-1, 1) for y in P.rail_bolt_y]
POSTS = [(sx * P.rail_x, y) for sx in (-1, 1) for y in P.post_y]
HT = P.hood_top
TOP_IN = HT - P.hood_t                      # underside of the top sheet


def square_tube_y(y0, y1, x, z, size, wall):
    s = box_span((x - size / 2.0, x + size / 2.0), (y0, y1), (z - size / 2.0, z + size / 2.0))
    i = box_span((x - size / 2.0 + wall, x + size / 2.0 - wall), (y0 - 1, y1 + 1),
                 (z - size / 2.0 + wall, z + size / 2.0 - wall))
    return s.cut(i)


# ---------------------------------------------------------------------
# Belly rails and the extra holes in the spot-sprayer control-box base plate
# ---------------------------------------------------------------------
def _foot_bolts():
    """2 x M8 per post foot, into rivet nuts in the bottom wall of the rail."""
    return [(x, y + dy) for (x, y) in POSTS for dy in (-22.0, 22.0)]


def rails():
    zc = (P.rail_z[0] + P.rail_z[1]) / 2.0
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        t = square_tube_y(P.rail_y[0], P.rail_y[1], x, zc, P.rail, P.rail_wall)
        ends = [box_span((x - P.rail / 2.0, x + P.rail / 2.0), (y0, y0 + 3.0), P.rail_z)
                for y0 in (P.rail_y[0], P.rail_y[1] - 3.0)]           # end caps 3 mm
        t = fuse_all([t] + ends)
        holes = [cyl_z(P.m10_hole, P.rail_z[0] - 1, P.rail_z[1] + 1, bx, by) for (bx, by) in RAIL_BOLTS if bx == x]
        holes += [cyl_z(8.5, P.rail_z[0] - 1, P.rail_z[0] + P.rail_wall + 1, bx, by) for (bx, by) in _foot_bolts()
                  if bx == x]
        out.append(t.cut(holes))
    return Part.makeCompound(out)


def box_base():
    """Control-box base plate of the spot sprayer with 4 extra M10 holes for the rear rail bolts."""
    z = (P.robot_lower_beam_z[1], P.robot_lower_beam_z[1] + P.S.box_base[2])
    return SG.box_base().cut([cyl_z(P.m10_hole, z[0] - 1, z[1] + 1, x, y) for (x, y) in RAIL_BOLTS if y < 0])


def rail_bolts():
    """M10 through the lower beams and the rails; at the rear also through the control-box base plate."""
    out = []
    for (x, y) in RAIL_BOLTS:
        top = P.robot_lower_beam_z[1] + (P.S.box_base[2] if y < 0 else 0.0)
        out.append(bolt_z(x, y, top, P.rail_z[0]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Hanger posts (fixed to the rails); the hood hangs on them with cross pins
# ---------------------------------------------------------------------
POST_TOP = P.rail_z[0] - P.post_foot[2]
POST_BOT = HT + P.post_bottom_dz


def posts():
    fx, fy, ft = P.post_foot
    out = []
    for (x, y) in POSTS:
        tube = square_tube_z(POST_BOT, POST_TOP, x, y, P.post, P.post_wall)
        foot = box_span((x - fx / 2.0, x + fx / 2.0), (y - fy / 2.0, y + fy / 2.0), (POST_TOP, P.rail_z[0]))
        foot = foot.cut([cyl_z(8.5, POST_TOP - 1, P.rail_z[0] + 1, bx, by) for (bx, by) in _foot_bolts()
                         if bx == x and abs(by - y) < 30.0])
        s = fuse_all([tube, foot])
        for dz in P.height_steps:
            z = HT + P.pin_dz + dz                  # hood raised by dz -> the bracket pin sits dz higher
            s = s.cut(cyl_x(P.pin_d + 0.4, x - 30.0, x + 30.0, y, z))
        out.append(s)
    return Part.makeCompound(out)


def post_bolts():
    """M8 from below: head under the foot plate, into a rivet nut in the bottom wall of the rail."""
    out = []
    for (x, y) in _foot_bolts():
        head = SG.hex_prism_z(13.0, POST_TOP - 5.3, POST_TOP, x, y)
        shank = cyl_z(8.0, POST_TOP, P.rail_z[0] + P.rail_wall + 6.0, x, y)
        out.append(fuse_all([head, shank]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Hood (own sub-Part): shell, brush strip, post brackets, cross pins
# ---------------------------------------------------------------------
HOLE_FEED = (P.lp_xy[0], P.inj_y - 10.0)
BOLT_DY = 25.0                              # bracket bolts M8 in front of and behind the post, outside the cheeks


def hood_shell():
    x, (y0, y1), t = P.hood_x, P.hood_y, P.hood_t
    zb = P.skirt_bottom
    outer = box_span((-x, x), (y0, y1), (zb, HT))
    inner = box_span((-x + t, x - t), (y0 + t, y1 - t), (zb - 1.0, HT - t))
    s = outer.cut(inner)
    s = s.cut(cyl_z(P.hose_d + 4.0, HT - 5, HT + 5, HOLE_FEED[0], HOLE_FEED[1]))
    s = s.cut(cyl_z(20.0, HT - 5, HT + 5, 0.0, P.cam_xy[1] - 60.0))           # camera cable gland
    for (px, py) in POSTS:
        for dx in (-15.0, 15.0):
            s = s.cut(cyl_z(8.5, HT - 5, HT + 5, px, py + dx * BOLT_DY / 15.0))
    return s


def brush_strip():
    """Nylon brush strip 8 mm in an aluminium holder clamped round the outside of the skirt."""
    x, (y0, y1) = P.hood_x, P.hood_y
    hw, hh = P.brush_holder
    zb = P.skirt_bottom
    ring_o = box_span((-x - hw, x + hw), (y0 - hw, y1 + hw), (zb - 10.0, zb + hh))
    ring_i = box_span((-x, x), (y0, y1), (zb - 20.0, zb + hh + 1))
    holder = ring_o.cut(ring_i)
    b0 = (hw - P.brush_t) / 2.0
    br_o = box_span((-x - b0 - P.brush_t, x + b0 + P.brush_t), (y0 - b0 - P.brush_t, y1 + b0 + P.brush_t),
                    (zb - P.brush_h, zb - 10.0))
    br_i = box_span((-x - b0, x + b0), (y0 - b0, y1 + b0), (zb - P.brush_h - 1, zb))
    return holder, br_o.cut(br_i)


def holder():
    return brush_strip()[0]


def brush():
    return brush_strip()[1]


def post_brackets():
    bx, by, bt, bh = P.post_bracket
    out = []
    for (x, y) in POSTS:
        base = box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0 - 10.0, y + by / 2.0 + 10.0), (HT, HT + bt))
        cheeks = [box_span((x + s * (P.post / 2.0 + 1.0), x + s * (P.post / 2.0 + 1.0 + bt)),
                           (y - by / 2.0, y + by / 2.0), (HT + bt, HT + bh)) for s in (-1, 1)]
        b = fuse_all([base] + cheeks)
        b = b.cut(cyl_x(P.pin_d + 0.4, x - 40.0, x + 40.0, y, HT + P.pin_dz))
        b = b.cut([cyl_z(8.5, HT - 1, HT + bt + 1, x, y + dy) for dy in (-BOLT_DY, BOLT_DY)])
        out.append(b)
    return Part.makeCompound(out)


def bracket_bolts():
    out = []
    for (x, y) in POSTS:
        for dy in (-BOLT_DY, BOLT_DY):
            out.append(bolt_z(x, y + dy, HT + P.post_bracket[2], TOP_IN, d=8.0, af=13.0, k=5.3, m=6.8))
    return Part.makeCompound(out)


def pins():
    """M10 cross pins (with R-clip) through the bracket cheeks and the post."""
    bt = P.post_bracket[2]
    out = []
    for (x, y) in POSTS:
        x0, x1 = x - P.post / 2.0 - 1.0 - bt - 4.0, x + P.post / 2.0 + 1.0 + bt + 4.0
        z = HT + P.pin_dz
        out.append(fuse_all([cyl_x(P.pin_d, x0, x1, y, z), cyl_x(16.0, x0 - 4.0, x0, y, z)]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Camera and LED bars under the top sheet
# ---------------------------------------------------------------------
CAM_Z1 = TOP_IN - 20.0                      # top of the camera housing
CAM_Z0 = CAM_Z1 - P.cam_box[2]
LENS_Z0 = CAM_Z0 - P.cam_lens[1]


def camera_bracket():
    """Angle 5 mm: horizontal flange under the top sheet, vertical plate behind the camera."""
    cx, cy = P.cam_xy
    w = P.cam_box[0]
    t = P.cam_bracket_t
    y_back = cy - P.cam_box[1] / 2.0
    plate = box_span((cx - w / 2.0, cx + w / 2.0), (y_back - t, y_back), (CAM_Z0 + 10.0, TOP_IN))
    flange = box_span((cx - w / 2.0, cx + w / 2.0), (y_back - t, y_back + 40.0), (TOP_IN - t, TOP_IN))   # over the camera
    return fuse_all([plate, flange])


def camera():
    cx, cy = P.cam_xy
    bx, by, bz = P.cam_box
    body = box_span((cx - bx / 2.0, cx + bx / 2.0), (cy - by / 2.0, cy + by / 2.0), (CAM_Z0, CAM_Z1))
    lens = cyl_z(P.cam_lens[0], LENS_Z0, CAM_Z0, cx, cy)
    return fuse_all([body, lens])


def camera_glass():
    cx, cy = P.cam_xy
    return cyl_z(P.cam_lens[0] - 6.0, LENS_Z0 - 1.0, LENS_Z0, cx, cy)


def led_bars():
    lx, ly, lz = P.led_bar
    return Part.makeCompound([box_span((-lx / 2.0, lx / 2.0), (y - ly / 2.0, y + ly / 2.0), (TOP_IN - lz, TOP_IN))
                              for y in P.led_y])


def led_lenses():
    lx, ly, lz = P.led_bar
    return Part.makeCompound([box_span((-lx / 2.0 + 10.0, lx / 2.0 - 10.0), (y - ly / 2.0 + 4.0, y + ly / 2.0 - 4.0),
                                       (TOP_IN - lz - 2.0, TOP_IN - lz)) for y in P.led_y])


# ---------------------------------------------------------------------
# Injector rail: manifold, brackets, 24 injectors, bleed valve
# ---------------------------------------------------------------------
MANI_Z = (P.mani_z0, P.mani_z0 + P.mani[2])
MANI_Y = (P.inj_y - P.mani[1] / 2.0, P.inj_y + P.mani[1] / 2.0)
MANI_ZC = (MANI_Z[0] + MANI_Z[1]) / 2.0


def manifold():
    hx = P.mani[0] / 2.0 - 5.0                  # 590 long, inside the hood walls
    m = box_span((-hx, hx), MANI_Y, MANI_Z)
    m = m.cut(cyl_x(P.mani_bore, -hx + 8.0, hx - 8.0, P.inj_y, MANI_ZC))
    m = m.cut([cyl_z(P.inj_nozzle[0] + 2.0, MANI_Z[0] - 1, MANI_ZC, x, P.inj_y) for x in P.inj_x])
    m = m.cut(cyl_z(8.0, MANI_ZC, MANI_Z[1] + 1, HOLE_FEED[0], P.inj_y))
    m = m.cut(cyl_z(6.0, MANI_ZC, MANI_Z[1] + 1, P.bleed_xy[0], P.inj_y))
    return m


def manifold_brackets():
    t = P.mani_bracket_t
    out = []
    for sx in (-1, 1):
        x = sx * P.mani_bracket_x
        plate = box_span((x - t / 2.0, x + t / 2.0), MANI_Y, (MANI_Z[1], TOP_IN - t))
        flange = box_span((x - t / 2.0 - 25.0 * (sx < 0), x + t / 2.0 + 25.0 * (sx > 0)), MANI_Y, (TOP_IN - t, TOP_IN))
        foot = box_span((x - t / 2.0 - 25.0 * (sx < 0), x + t / 2.0 + 25.0 * (sx > 0)), MANI_Y, (MANI_Z[1], MANI_Z[1] + t))
        out.append(fuse_all([plate, flange, foot]))
    return Part.makeCompound(out)


def injectors():
    out = []
    zt = P.tip_z
    for x in P.inj_x:
        noz = cyl_z(P.inj_nozzle[0], zt, zt + P.inj_nozzle[1], x, P.inj_y)
        body = cyl_z(P.inj_body[0], zt + P.inj_nozzle[1], MANI_Z[0], x, P.inj_y)
        px, py, pz = P.inj_plug
        y1 = P.inj_y - P.inj_body[0] / 2.0 + 1.0
        plug = box_span((x - px / 2.0, x + px / 2.0), (y1 - py, y1), (MANI_Z[0] - 20.0 - pz, MANI_Z[0] - 20.0))
        out.append(fuse_all([noz, body, plug]))
    return Part.makeCompound(out)


def bleed_valve():
    x, y = P.bleed_xy
    return fuse_all([cyl_z(14.0, MANI_Z[1], MANI_Z[1] + 25.0, x, y), cyl_x(8.0, x, x + 22.0, y, MANI_Z[1] + 18.0)])


# ---------------------------------------------------------------------
# Low-pressure regulator, accumulator, feed hose
# ---------------------------------------------------------------------
LP = (P.lp_xy[0], P.lp_xy[1], HT)


def lp_regulator():
    bx, by, bz = P.lp_reg
    x, y, z = LP
    body = box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0, y + by / 2.0), (z, z + bz))
    gauge = cyl_x(36.0, x + bx / 2.0, x + bx / 2.0 + 12.0, y, z + bz - 22.0)     # on the right face
    knob = cyl_z(30.0, z + bz, z + bz + 20.0, x, y)
    return fuse_all([body, gauge, knob])


def accumulator():
    d, ln = P.accu
    x, y = P.accu_xy
    x1 = P.lp_xy[0] - P.lp_reg[0] / 2.0 - 8.0
    x0 = x1 - ln
    z = HT + d / 2.0 + 4.0
    body = cyl_x(d, x0, x1, y, z)
    nip = cyl_x(14.0, x1, x1 + 8.0, y, z)
    saddles = [box_span((xs - 10.0, xs + 10.0), (y - d / 2.0 + 8.0, y + d / 2.0 - 8.0), (HT, z - d / 2.0 + 6.0))
               for xs in (x0 + 25.0, x1 - 25.0)]
    s = fuse_all([body, nip] + saddles)
    return s


def feed_hose():
    """Pressure hose from the spot-sprayer regulator (3 bar) down to the low-pressure regulator on the hood top."""
    x = P.S.feed_x
    z_run = HT + 35.0
    y_in = LP[1] - P.lp_reg[1] / 2.0 + 1.0                  # into the rear face of the low-pressure regulator
    return hose([(x, -475.0, P.S.regulator[2][0]), (x, -475.0, z_run), (x, y_in, z_run)])


def drop_hose():
    """Short hose from the low-pressure regulator through the top sheet to the manifold."""
    x, y = HOLE_FEED
    return hose([(x, y, HT + 1.0), (x, y, MANI_Z[1] + 1.0)], od=P.hose_d - 4.0)


# ---------------------------------------------------------------------
# Field objects for the renders and the animation
# ---------------------------------------------------------------------
def lettuce(x, y, d, seed=0):
    import random
    rnd = random.Random(seed)
    leaves = []
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.2, 0.2)
        ln = d / 2.0 * rnd.uniform(0.8, 1.0)
        leaf = Part.makeSphere(1.0)
        m = App.Matrix()
        m.scale(ln / 2.0, ln / 3.5, 8.0)
        leaf = leaf.transformGeometry(m)
        leaf.rotate(V(0, 0, 0), V(0, 1, 0), -rnd.uniform(20.0, 40.0))
        leaf.translate(V(ln / 2.0, 0, 10.0))
        leaf.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(a))
        leaves.append(leaf)
    heart = Part.makeSphere(d / 6.0, V(0, 0, d / 8.0))
    c = Part.makeCompound(leaves + [heart])
    c.translate(V(x, y, 0.0))
    return c


def weed(x, y, d, seed=0):
    """Weed seedling: 2..6 small leaves flat on the soil."""
    import random
    rnd = random.Random(seed)
    n = rnd.randint(2, 6)
    leaves = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.3, 0.3)
        ln = d / 2.0 * rnd.uniform(0.7, 1.0)
        leaf = Part.makeSphere(1.0)
        m = App.Matrix()
        m.scale(ln / 2.0, ln / 5.0, 2.0)
        leaf = leaf.transformGeometry(m)
        leaf.translate(V(ln / 2.0, 0, 3.0))
        leaf.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(a))
        leaves.append(leaf)
    c = Part.makeCompound(leaves)
    c.translate(V(x, y, 0.0))
    return c


def drop(x, y, z):
    return Part.makeSphere(max(P.drop_d(), 4.0) / 2.0 * 1.6, V(x, y, z))


def wet_dot(x, y, z=6.0):
    return cyl_z(12.0, z, z + 0.8, x, y)


def bed(y0, y1, w=P.bed_width + 200.0, h=60.0):
    """Raised bed (soil), flat top at z 0, slopes down 60 mm to the wheel paths."""
    pts = [(-w / 2.0 - 120.0, -h), (w / 2.0 + 120.0, -h), (w / 2.0, 0.0), (-w / 2.0, 0.0)]
    return SG.poly_xz(pts, y0, y1 - y0)
