"""One function per part of the flat-wagon station: the (simplified) standard wagon, the mast skid, the box
hangers and the hoses. All shapes in wagon coordinates (origin = middle of the deck on the ground, y forward).
The IBCs, the control box and the mast with the arm come from ../stc_parts.py.
"""
import math

import Part
from FreeCAD import Vector as V

import sfw_params as P
import stc_params as C
import stc_parts as G
from stc_parts import box_span, cyl_x, cyl_y, cyl_z, rtube, fuse_all, hose

HL, HW = P.deck_l / 2.0, P.deck_w / 2.0
DZ = (P.deck_top - P.deck_t, P.deck_top)
CZ = (DZ[0] - P.cross[1], DZ[0])
BZ = (CZ[0] - P.beam[1], CZ[0])                 # main beams
AZ = P.tyre[0] / 2.0                            # axle centre
MX, MY = P.mast_xy


# ---------------------------------------------------------------------
# Placements and spec
# ---------------------------------------------------------------------
def ibc_placement(x, y):
    """IBC turned 90 deg: 1200 along y, valve to the rear."""
    return G.placement(x, y, P.deck_top, 90.0)


def box_placement():
    return G.placement(0.0, P.box_y, P.box_z(), 180.0)


def mast_spec():
    z0 = P.deck_top + P.skid[2] + P.mast_base[1]
    return G.mast_spec(MX, MY, z0, P.reach(), arm_z=P.arm_z, nozzle_z=P.nozzle_z, in_z=None, folds=(-90.0, 0.0))


# ---------------------------------------------------------------------
# Wagon: deck, border, cross members, main beams
# ---------------------------------------------------------------------
def hole_xy():
    return [(0.0, P.header_hole_y), (MX, MY)]


def deck_plate():
    plate = box_span((-HW + P.border[1], HW - P.border[1]), (-HL + P.border[1], HL - P.border[1]), DZ)
    return plate.cut([cyl_z(P.deck_hole, DZ[0] - 1, DZ[1] + 1, x, y) for x, y in hole_xy()])


def border():
    h, t = P.border
    z = (P.deck_top - h, P.deck_top)
    parts = [box_span((s * HW, s * (HW - t)), (-HL, HL), z) for s in (-1, 1)]
    parts += [box_span((-HW + t, HW - t), (s * HL, s * (HL - t)), z) for s in (-1, 1)]
    return fuse_all(parts)


def cross_positions():
    out = []
    y = -HL + 200.0
    while y < HL - 100.0:
        yy = y
        for _, hy in hole_xy():
            if abs(yy - hy) < 70.0:
                yy = hy - 100.0 if yy < hy else hy + 100.0
        out.append(yy)
        y += P.cross_pitch
    return out


def cross_members():
    w, h, t = P.cross
    return Part.makeCompound([rtube((-HW + P.border[1], HW - P.border[1]), (y - w / 2.0, y + w / 2.0), CZ, t, "x")
                              for y in cross_positions()])


def main_beams():
    """IPE 200 at x = +-450, under the cross members, full length."""
    b, h, tf, tw = P.beam
    out = []
    for s in (-1, 1):
        x = s * P.beam_x
        y = (-HL + P.border[1], HL - P.border[1])
        out.append(fuse_all([box_span((x - b / 2.0, x + b / 2.0), y, (BZ[0], BZ[0] + tf)),
                             box_span((x - b / 2.0, x + b / 2.0), y, (BZ[1] - tf, BZ[1])),
                             box_span((x - tw / 2.0, x + tw / 2.0), y, (BZ[0] + tf, BZ[1] - tf))]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Running gear
# ---------------------------------------------------------------------
def _axle(y):
    a, t = P.axle_sq
    xi = P.wheel_x - P.tyre[1] / 2.0 - 5.0
    beam = rtube((-xi, xi), (y - a / 2.0, y + a / 2.0), (AZ - a / 2.0, AZ + a / 2.0), t, "x")
    stubs = [cyl_x(80.0, s * xi, s * (P.wheel_x - 20.0), y, AZ) for s in (-1, 1)]
    return fuse_all([beam] + stubs)


def axles():
    return Part.makeCompound([_axle(P.axle_y), _axle(-P.axle_y)])


def tyres():
    d, w, rim_d, _ = P.tyre
    return Part.makeCompound([G.tyre(s * P.wheel_x, sy * P.axle_y, AZ, d, w, rim_d) for s in (-1, 1) for sy in (-1, 1)])


def rims():
    d, w, rim_d, _ = P.tyre
    return Part.makeCompound([G.rim(s * P.wheel_x, sy * P.axle_y, AZ, w, rim_d, side=-s)
                              for s in (-1, 1) for sy in (-1, 1)])


def turntable():
    """Upper ring (on the main beams) and lower ring (on the bolster), at the front axle."""
    d, w, h = P.turntable
    y = P.axle_y
    upper = cyl_z(d, BZ[0] - h, BZ[0], 0.0, y).cut(cyl_z(d - 2 * w, 0, 5000, 0.0, y))
    lower = cyl_z(d, BZ[0] - 2 * h, BZ[0] - h, 0.0, y).cut(cyl_z(d - 2 * w, 0, 5000, 0.0, y))
    return upper, lower


def bolster():
    lx, wy, t = P.bolster
    a = P.axle_sq[0]
    y = P.axle_y
    return rtube((-lx / 2.0, lx / 2.0), (y - wy / 2.0, y + wy / 2.0), (AZ + a / 2.0, BZ[0] - 2 * P.turntable[2]), t, "x")


def springs():
    """Rear leaf springs (blocks) on the axle, hangers up to the main beams."""
    w, ln, h = P.spring
    a = P.axle_sq[0]
    y = -P.axle_y
    z0 = AZ + a / 2.0
    out = []
    for s in (-1, 1):
        x = s * P.beam_x
        out.append(box_span((x - w / 2.0, x + w / 2.0), (y - ln / 2.0, y + ln / 2.0), (z0, z0 + h)))
        for e in (-1, 1):
            ye = y + e * (ln / 2.0 - P.hanger_t / 2.0)
            out.append(box_span((x - w / 2.0, x + w / 2.0), (ye - P.hanger_t / 2.0, ye + P.hanger_t / 2.0),
                                (z0 + h, BZ[0])))
    return fuse_all(out)


def drawbar():
    ln, sp = P.drawbar
    y0 = P.axle_y + P.axle_sq[0] / 2.0
    apex = (0.0, P.axle_y + ln)
    return fuse_all([G.beam_between((s * sp, y0), apex, b=80.0, h=100.0, t=5.0, z_mid=AZ) for s in (-1, 1)])


def tow_eye():
    return G.tow_eye(0.0, P.axle_y + P.drawbar[0] + P.eye_ahead, AZ, l=P.eye_ahead + 160.0)


def drawbar_stand():
    y = P.axle_y + P.drawbar[0] - 300.0
    sl, leg, pin = G.drop_leg(0.0, y, AZ - 50.0, sleeve_len=200.0)
    plate = box_span((-100.0, 100.0), (y - 30.0, y + 30.0), (AZ - 50.0, AZ - 40.0))
    return fuse_all([sl, plate]), leg, pin


def rear_lights():
    hs, ls = [], []
    for s in (-1, 1):
        a, b = G.light_box(s * 900.0, -HL, P.deck_top - 100.0, w=300.0, h=120.0)
        hs.append(a)
        ls.append(b)
    plate = box_span((-260.0, 260.0), (-HL - 4.0, -HL), (P.deck_top - 155.0, P.deck_top - 45.0))
    return Part.makeCompound(hs), Part.makeCompound(ls), plate


# ---------------------------------------------------------------------
# Mast skid on the deck (rear left corner), box hangers under the deck
# ---------------------------------------------------------------------
SZ = (P.deck_top, P.deck_top + P.skid[2])


def skid():
    (x0, x1), (y0, y1), h = P.skid
    t = 3.0
    parts = [rtube((x0, x0 + 80.0), (y0, y1), SZ, t, "y"), rtube((x1 - 80.0, x1), (y0, y1), SZ, t, "y"),
             rtube((x0 + 80.0, x1 - 80.0), (y0, y0 + 80.0), SZ, t, "x"),
             rtube((x0 + 80.0, x1 - 80.0), (y1 - 80.0, y1), SZ, t, "x")]
    return fuse_all(parts).cut(cyl_z(56.0, SZ[0] - 1, SZ[1] + 1, MX, MY))


def mast_base():
    s, t = P.mast_base
    return box_span((MX - s / 2.0, MX + s / 2.0), (MY - s / 2.0, MY + s / 2.0), (SZ[1], SZ[1] + t)).cut(
        cyl_z(56.0, SZ[1] - 1, SZ[1] + t + 1, MX, MY))


def mast_struts(M):
    """Two round tubes from the mast down to the skid (right side and front)."""
    (x0, x1), (y0, y1), h = P.skid
    m = M["tube"][0] / 2.0
    zt = M["arm_z"][0] - 700.0
    return fuse_all([G.strut((MX + m, MY, zt), (x1 - 60.0, MY, SZ[1] + 15.0), 42.0),
                     G.strut((MX, MY + m, zt), (MX, y1 - 60.0, SZ[1] + 15.0), 42.0)])


def box_supports():
    w, h, t = P.box_sup
    z = (P.box_z() - h, P.box_z())
    return Part.makeCompound([rtube((-P.beam_x - 4.0, P.beam_x + 4.0), (y - w / 2.0, y + w / 2.0), z, t, "x")
                              for y in (P.box_y - 160.0, P.box_y + 160.0)])


def box_hangers():
    w, t = P.hanger
    z = (P.box_z() - P.box_sup[1], BZ[0])
    return Part.makeCompound([box_span((s * P.beam_x - t / 2.0, s * P.beam_x + t / 2.0), (y - w / 2.0, y + w / 2.0), z)
                              for s in (-1, 1) for y in (P.box_y - 160.0, P.box_y + 160.0)])


def corner_guides():
    return Part.makeCompound([G.corner_guides(x - C.ibc_wid / 2.0, x + C.ibc_wid / 2.0, y - C.ibc_len / 2.0,
                                              y + C.ibc_len / 2.0, P.deck_top) for x, y in P.ibc_positions()])


# ---------------------------------------------------------------------
# Hoses
# ---------------------------------------------------------------------
def elbows():
    return [G.xform(G.ELBOW_OUT, ibc_placement(x, y)) for x, y in P.ibc_positions()]


def suction_hoses():
    """Every IBC elbow -> down to the deck -> across to the header in the middle; header along the middle to the
    rear, down through the deck, under the deck to the suction port of the box."""
    hz = P.header_z
    out = []
    for ex, ey, ez in elbows():
        s = 1.0 if ex > 0 else -1.0
        out.append(hose([(ex, ey, ez), (ex, ey, hz + 30.0), (ex - s * 40.0, ey, hz), (s * 30.0, ey, hz),
                         (0.0, ey + 0.0, hz)]))
    y_front = max(e[1] for e in elbows())
    hy = P.header_hole_y
    px, py, pz = G.xform(C.SUCTION_PORT, box_placement())
    out.append(hose([(0.0, y_front, hz), (0.0, hy + 40.0, hz), (0.0, hy, hz - 40.0), (0.0, hy, 1000.0),
                     (px + 40.0, hy - 150.0, 700.0), (px + 40.0, py, pz + 60.0), (px + 40.0, py, pz), (px, py, pz)]))
    return fuse_all(out)


def discharge_hose(M):
    """Box (discharge port, left) -> under the deck to the left -> up through the deck and the skid into the mast
    -> out of the top window."""
    px, py, pz = G.xform(C.DISCHARGE_PORT, box_placement())
    wo = G.window_out(M)
    pts = [(px, py, pz), (px - 30.0, py, pz), (MX + 160.0, py, pz), (MX, MY, pz + 120.0), (MX, MY, wo[2]), wo]
    return hose(pts)
