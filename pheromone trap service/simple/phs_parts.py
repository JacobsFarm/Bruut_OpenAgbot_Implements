"""Parts of the pheromone trap service, in robot coordinates. Mast, screw, stepper, carriage and hinge pin come from the
fence inspector (fin_parts). The carriage parts here (arm, rail, actuator) are drawn at the fin work height F.wire_z
and moved in z by the Carriage sub-Part; the head parts are drawn retracted and moved in x by the Slide sub-Part.
trap() is the trap on its post, for the render only.
"""
import math

import Part
from FreeCAD import Vector as V

import phs_params as P
import pbl_parts as PP
import fin_parts as FP

box_span = PP.box_span
cyl = PP.cyl
tube_span = PP.tube_span
fuse_all = PP.fuse_all

ZC = P.zc_ref
HX, HY = P.F.hinge_xy
W = P.arm_w / 2.0
X0 = P.slide_x0

# from fin: fixed and carriage parts
mast = FP.mast
gussets = FP.gussets
screw = FP.screw
screw_blocks = FP.screw_blocks
stepper = FP.stepper
carriage = FP.carriage
hinge_pin = FP.hinge_pin


def _bolts_xy():
    return [(sum(b) / 2.0, s * y) for b in P.upper_beam_x for y in P.hole_y for s in (-1, 1)]


def base_plate():
    z0 = P.upper_beam_top
    s = box_span((P.plate_x[0], FP.X_IN), P.plate_y, (z0, z0 + P.plate_t))
    for x, y in _bolts_xy():
        s = s.cut(cyl(10.5, (x, y, z0 - 1), (x, y, z0 + P.plate_t + 1)))
    return s


def plate_bolts():
    z0 = P.upper_beam_top
    return Part.makeCompound([PP.bolt_z(10.0, x, y, z0 - 40.0, z0 + P.plate_t) for x, y in _bolts_xy()])


# ---------------------------------------------------------------------
# Carriage (moves in z): fixed arm, rail, actuator body
# ---------------------------------------------------------------------
def arm():
    knuckle = cyl(34.0, (HX, HY, ZC - W - 2.0), (HX, HY, ZC + W + 2.0))
    tube = tube_span((HX, P.arm_x1), (HY - W, HY + W), (ZC - W, ZC + W), 3.0, "x")
    cap = box_span((P.arm_x1 - 3.0, P.arm_x1), (HY - W, HY + W), (ZC - W, ZC + W))
    s = fuse_all([knuckle, tube, cap])
    return s.cut(cyl(P.F.hinge_d + 0.5, (HX, HY, ZC - 100), (HX, HY, ZC + 100)))


def rail():
    w, h = P.rail
    return box_span(P.rail_x, (-w / 2, w / 2), (ZC + W, ZC + W + h))


def actuator_body():
    """24 V actuator beside the arm (y +), on 2 clamp blocks."""
    y = P.act_y
    body = cyl(P.act_d, (P.act_x[0], y, ZC), (P.act_x[1], y, ZC))
    clamps = [box_span((x, x + 20.0), (W, y + P.act_d / 2.0), (ZC - P.act_d / 2.0, ZC - P.act_d / 2.0 + 8.0))
              for x in (P.act_x[0] + 20.0, P.act_x[1] - 60.0)]
    return fuse_all([body] + clamps)


# ---------------------------------------------------------------------
# Slide (moves in x): block, head plate, hook + servo, revolver + plunger, guide tube, bin, camera post, camera, LED
# ---------------------------------------------------------------------
def _ztop():
    return ZC + W + P.rail[1] + P.block[2]


def block():
    l, w, h = P.block
    z0 = ZC + W + P.rail[1] - 4.0                      # the block wraps the rail 4 mm
    return box_span((X0, X0 + l), (-w / 2, w / 2), (z0, z0 + h + 4.0))


def head_plate():
    lx, ly, t = P.head_plate
    z = _ztop()
    return box_span((X0, X0 + lx), (-105.0, -105.0 + ly), (z, z + t))


def act_rod():
    """Rod from inside the actuator body to the tab under the head plate."""
    y = P.act_y
    tab_x = X0 + 120.0
    rod = cyl(P.act_rod_d, (tab_x - P.stroke - 40.0, y, ZC), (tab_x, y, ZC))
    tab = box_span((tab_x, tab_x + 8.0), (y - 15.0, y + 15.0), (ZC - 15.0, _ztop()))
    return fuse_all([rod, tab])


def hook():
    """Vertical bar ahead of the arm end, finger out along x and an upturned tip (P.hook_x)."""
    z = _ztop()
    x0 = P.arm_x1 + 5.0
    zt = ZC - P.hook_drop
    bar = box_span((x0, x0 + 10.0), (-10.0, 10.0), (zt, z))
    finger = box_span((x0, P.hook_x + 10.0), (-10.0, 10.0), (zt, zt + 8.0))
    tip = box_span((P.hook_x, P.hook_x + 10.0), (-10.0, 10.0), (zt, zt + 25.0))
    return fuse_all([bar, finger, tip])


def hook_servo():
    z = _ztop() + P.head_plate[2]
    return box_span((P.arm_x1 - 35.0, P.arm_x1 + 15.0), (10.0, 50.0), (z, z + 30.0))


GUIDE_DX = 37.0                 # guide tube axis ahead of the hook tip


def _guide_xy():
    return (P.hook_x + GUIDE_DX, -55.0)


def _rev_xy():
    gx, gy = _guide_xy()
    return (gx - 30.0, gy)


def revolver():
    """12 lure capsules on r 30 in a drum O90 (stepped by a small servo); the plunger is over slot 0 (= guide tube)."""
    d, h = P.revolver
    x, y = _rev_xy()
    z = _ztop() + P.head_plate[2]
    drum = cyl(d, (x, y, z), (x, y, z + h))
    for i in range(P.revolver_n):
        a = 2 * math.pi * i / P.revolver_n
        drum = drum.cut(cyl(P.capsule[0] + 1.0, (x + 30.0 * math.cos(a), y + 30.0 * math.sin(a), z - 1.0),
                            (x + 30.0 * math.cos(a), y + 30.0 * math.sin(a), z + h + 1.0)))
    plunger = cyl(22.0, (x + 30.0, y, z + h + 2.0), (x + 30.0, y, z + h + 72.0))
    return drum, plunger


def capsules():
    d, l = P.capsule
    x, y = _rev_xy()
    z = _ztop() + P.head_plate[2] + 6.0
    out = []
    for i in range(1, P.revolver_n):                   # slot 0 (at the plunger) is empty: just used
        a = 2 * math.pi * i / P.revolver_n
        cx, cy = x + 30.0 * math.cos(a), y + 30.0 * math.sin(a)
        out.append(cyl(d, (cx, cy, z), (cx, cy, z + l)))
    return Part.makeCompound(out)


def clip_top():
    return P.trap_drawer_z + 4.0 + 20.0


def guide_tube():
    """From the plate down to just above the lure clip of the drawer: the plunger pushes the new capsule down into the
    clip, which pushes the old one out at the bottom of the clip into the chute of the bin."""
    x, y = _guide_xy()
    z = _ztop()
    t = cyl(24.0, (x, y, clip_top() + 2.0), (x, y, z))
    return t.cut(cyl(P.capsule[0] + 2.0, (x, y, clip_top()), (x, y, z + 1.0)))


def bin_box():
    w, d, h = P.bin_box
    x, y = _rev_xy()
    return box_span((x - 45.0 - w, x - 45.0), (y - d / 2, y + d / 2), (_ztop() - h, _ztop()))


def cam_post():
    z = _ztop() + P.head_plate[2]
    x = P.arm_x1 - 60.0
    return box_span((x, x + 15.0), (60.0, 75.0), (z, ZC + P.cam_mast_h))


CAM_TILT = -55.0


def camera():
    """12 MP camera at the post top, looking down and forward at the pulled-out drawer; LED ring around the lens."""
    w, d, h = P.cam_box
    x = P.arm_x1 - 60.0
    z = ZC + P.cam_mast_h
    body = box_span((x, x + w), (67.5 - d / 2, 67.5 + d / 2), (z, z + h))
    c = V(x + w, 67.5, z + h / 2)
    a = math.radians(CAM_TILT)
    u = V(math.cos(a), 0, math.sin(a))
    lens = cyl(30.0, c - u * 15.0, c + u * 20.0)
    led = cyl(P.led_ring[0], c + u * 20.0, c + u * (20.0 + P.led_ring[1]))
    led = led.cut(cyl(34.0, c + u * 19.0, c + u * (21.0 + P.led_ring[1])))
    return fuse_all([body, lens, led])


# ---------------------------------------------------------------------
# Trap on its post (render only)
# ---------------------------------------------------------------------
def drawer_front(slide):
    """x of the drawer front when the hook (head at 'slide') holds the handle bar."""
    return P.hook_x + 70.0 + slide


def trap(slide=P.stroke, zc=ZC):
    """Housing, post, drawer (with handle frame and lure clip) and sticky card; the drawer follows the hook of a head
    at 'slide' (slide = stroke: drawer closed)."""
    dzz = zc - ZC
    dz = P.trap_drawer_z + dzz
    dx, dy, dh = P.drawer
    bx, by, bh = P.trap_body
    front = drawer_front(P.stroke)
    x_far = front + dx
    post = cyl(P.post_d, (P.trap_post_x, 0, 0), (P.trap_post_x, 0, dz + bh + 300.0))
    floor = box_span((front - 5.0, x_far + 15.0), (-by / 2, by / 2), (dz + dh, dz + dh + 4.0))
    apex = (front + x_far) / 2 + 5.0
    tri = Part.makePolygon([V(front - 5.0, -by / 2, dz + dh + 4.0), V(x_far + 15.0, -by / 2, dz + dh + 4.0),
                            V(apex, -by / 2, dz + bh), V(front - 5.0, -by / 2, dz + dh + 4.0)])
    body = Part.Face(tri).extrude(V(0, by, 0))
    inner = Part.makePolygon([V(front + 12.0, -by / 2 - 1, dz + dh + 8.0), V(x_far - 2.0, -by / 2 - 1, dz + dh + 8.0),
                              V(apex, -by / 2 - 1, dz + bh - 14.0), V(front + 12.0, -by / 2 - 1, dz + dh + 8.0)])
    body = body.cut(Part.Face(inner).extrude(V(0, by + 2, 0)))
    bracket = box_span((x_far + 15.0, P.trap_post_x - P.post_d / 2 + 2.0), (-20.0, 20.0), (dz - 4.0, dz + bh * 0.6))
    rails = [box_span((front - 5.0, x_far + 15.0), (dy / 2 + 2.0, dy / 2 + 8.0), (dz - 4.0, dz + dh)),
             box_span((front - 5.0, x_far + 15.0), (-dy / 2 - 8.0, -dy / 2 - 2.0), (dz - 4.0, dz + dh))]
    housing = fuse_all([floor, body, bracket] + rails)
    f = drawer_front(slide)
    tray = box_span((f, f + dx), (-dy / 2, dy / 2), (dz, dz + dh))
    tray = tray.cut(box_span((f + 5.0, f + dx - 5.0), (-dy / 2 + 5.0, dy / 2 - 5.0), (dz + 4.0, dz + dh + 1.0)))
    card = box_span((f + 6.0, f + dx - 6.0), (-dy / 2 + 6.0, dy / 2 - 6.0), (dz + 4.0, dz + 5.0))
    zb = ZC - P.hook_drop + 10.0 + dzz
    frame = [box_span((f - 80.0, f - 72.0), (-70.0, 70.0), (zb, zb + 8.0))]
    frame += [box_span((f - 80.0, f), (s * 70.0 - 4.0, s * 70.0 + 4.0), (zb, zb + 8.0)) for s in (-1, 1)]
    shelf = box_span((f - 50.0, f), (-74.0, 74.0), (dz, dz + 4.0))
    gx, gy = _guide_xy()
    cx = gx + (f - drawer_front(0.0))
    clip = cyl(P.capsule[0] + 6.0, (cx, gy, dz + 4.0), (cx, gy, dz + 24.0))
    clip = clip.cut(cyl(P.capsule[0] + 0.5, (cx, gy, dz + 3.0), (cx, gy, dz + 25.0)))
    drawer = fuse_all([tray, shelf, clip] + frame)
    return housing, post, drawer, card
