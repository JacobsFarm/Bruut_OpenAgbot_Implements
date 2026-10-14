"""One function per part of the IBC trailer (frame, running gear, drawbar, parking gear, lights, hoses).
All shapes in trailer coordinates (origin = middle of the axle on the ground, y forward). c = sit_params.cfg(n).
The IBC, the control box and the mast with the arm come from ../stc_parts.py.
"""
import math

import Part
from FreeCAD import Vector as V

import sit_params as P
import stc_params as C
import stc_parts as G
from stc_parts import box_span, cyl_x, cyl_z, rtube, fuse_all, hose


# ---------------------------------------------------------------------
# Placements of the bought / common assemblies
# ---------------------------------------------------------------------
def ibc_placement(c, i):
    """IBC i (0 = front) turned -90 deg: 1200 along y, valve forward."""
    return G.placement(0.0, c["ibc_y"][i], c["deck_z"], -90.0)


def box_placement(c):
    """Control box turned 90 deg: door to the left, suction port backwards, discharge port forwards (both x = 0)."""
    return G.placement(P.box_x, c["box_y"], c["box_z"], 90.0)


def mast_spec(c):
    fold = c["fold"]
    return G.mast_spec(0.0, c["mast_y"], c["rail_z"][1], c["reach"], in_face="-y",
                       in_z=c["box_z"] + C.discharge_z, folds=(fold, 0.0, -180.0))


# ---------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------
def _cross_positions(c):
    """Cross members, moved away from the elbow hoses that come down through the floor."""
    out = []
    for y in c["cross_y"]:
        for ey in c["elbow_y"]:
            if abs(y - ey) < 70.0:
                y = ey - 90.0 if y < ey else ey + 90.0
        out.append(y)
    return out


def side_rails(c):
    w, h, t = P.rail
    return Part.makeCompound([rtube((s * P.rail_x[0], s * P.rail_x[1]), (c["deck_rear"], c["deck_front"]), c["rail_z"],
                                    t, "y") for s in (-1, 1)])


def _header_hole(y0, y1, c):
    return Part.makeCylinder(28.0, y1 - y0 + 2.0, V(P.header_x, y0 - 1.0, c["header_z"]), V(0, 1, 0))


def end_rails(c):
    """Front and rear rails between the side rails; the front one with the hole for the suction header."""
    w, h, t = P.rail
    x = (-P.rail_x[0], P.rail_x[0])
    front = rtube(x, (c["deck_front"] - w, c["deck_front"]), c["rail_z"], t, "x")
    front = front.cut(_header_hole(c["deck_front"] - w, c["deck_front"], c))
    rear = rtube(x, (c["deck_rear"], c["deck_rear"] + w), c["rail_z"], t, "x")
    return Part.makeCompound([front, rear])


def cross_members(c):
    w, h, t = P.cross
    z = (c["rail_z"][1] - h, c["rail_z"][1])
    out = []
    for y in _cross_positions(c):
        m = rtube((-P.rail_x[0], P.rail_x[0]), (y - w / 2.0, y + w / 2.0), z, t, "x")
        if y > c["elbow_y"][-1]:
            m = m.cut(_header_hole(y - w / 2.0, y + w / 2.0, c))
        out.append(m)
    return Part.makeCompound(out)


def floor_plate(c):
    z = (c["rail_z"][1], c["rail_z"][1] + P.floor_t)
    plate = box_span((-P.rail_x[1], P.rail_x[1]), (c["deck_rear"], c["deck_front"]), z)
    holes = [cyl_z(P.deck_hole, z[0] - 1.0, z[1] + 1.0, 0.0, ey) for ey in c["elbow_y"]]
    return plate.cut(holes)


def corner_guides(c):
    return Part.makeCompound([G.corner_guides(-C.ibc_wid / 2.0, C.ibc_wid / 2.0, y - C.ibc_len / 2.0,
                                              y + C.ibc_len / 2.0, c["deck_z"]) for y in c["ibc_y"]])


# ---------------------------------------------------------------------
# Running gear
# ---------------------------------------------------------------------
def axle(c):
    a = P.axle_sq
    z = c["axle_z"]
    beam = box_span((-P.rail_x[1], P.rail_x[1]), (-a / 2.0, a / 2.0), (z - a / 2.0, z + a / 2.0))
    stubs = [cyl_x(50.0, s * P.rail_x[1], s * (c["wheel_x"] - 20.0), 0.0, z) for s in (-1, 1)]
    plates = [box_span((s * (P.rail_x[0] - 10.0), s * (P.rail_x[1] + 10.0)), (-60.0, 60.0),
                       (z + a / 2.0 - 0.0, z + a / 2.0 + 10.0)) for s in (-1, 1)]
    return fuse_all([beam] + stubs), Part.makeCompound(plates)


def tyres(c):
    return Part.makeCompound([G.tyre(s * c["wheel_x"], 0.0, c["axle_z"], c["tyre_d"], c["tyre_w"], c["rim_d"])
                              for s in (-1, 1)])


def rims(c):
    return Part.makeCompound([G.rim(s * c["wheel_x"], 0.0, c["axle_z"], c["tyre_w"], c["rim_d"], side=-s)
                              for s in (-1, 1)])


def mudguards(c):
    out = []
    r = c["guard_r"]
    for s in (-1, 1):
        x = s * c["wheel_x"]
        g = G.mudguard(x, 0.0, c["axle_z"], r, c["guard_w"], t=P.guard[1])
        x_in = s * (c["wheel_x"] - c["guard_w"] / 2.0)
        sup = box_span((s * P.rail_x[1], x_in + s * 2.0), (-25.0, 25.0), (c["rail_z"][1] - 60.0, c["axle_z"] + r + 2.0))
        out.append(fuse_all([g, sup]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# A-frame drawbar, box and mast supports, tow eye, jockey wheel
# ---------------------------------------------------------------------
def a_frame(c):
    w, h, t = P.rail
    apex = (0.0, c["a_y0"] + P.a_len)
    beams = [G.beam_between((s * P.a_x0, c["a_y0"]), apex, b=w, h=h, t=t, z_mid=c["header_z"]) for s in (-1, 1)]
    return fuse_all(beams)


def box_cross(c):
    w, h, t = P.box_cross
    z = (c["rail_z"][1] - h, c["rail_z"][1])
    return Part.makeCompound([rtube((-P.a_x(c, y), P.a_x(c, y)), (y - w / 2.0, y + w / 2.0), z, t, "x")
                              for y in c["box_cross_y"]])


def mast_cross(c):
    w, h, t = P.mast_cross
    y = c["mast_y"]
    return rtube((-P.a_x(c, y), P.a_x(c, y)), (y - w / 2.0, y + w / 2.0), c["rail_z"], t, "x")


def tow_eye(c):
    return G.tow_eye(0.0, c["eye_y"], c["eye_z"], l=P.eye_ahead + 140.0)


def jockey(c):
    y = c["jockey_y"]
    xb = -P.a_x(c, y)
    x = xb - P.rail[0] / 2.0 - 45.0
    clamp = box_span((x - 40.0, xb), (y - 40.0, y + 40.0), (c["header_z"] - 45.0, c["header_z"] + 45.0)).cut(
        cyl_z(62.0, 0.0, 2000.0, x, y))
    body, wheel = G.jockey_wheel(x, y, c["header_z"])
    return clamp, body, wheel


def drop_legs(c):
    out_s, out_l, out_p = [], [], []
    for s in (-1, 1):
        sl, leg, pin = G.drop_leg(s * (P.rail_x[1] + 30.0), c["leg_y"], c["rail_z"][1])
        out_s.append(sl)
        out_l.append(leg)
        out_p.append(pin)
    return Part.makeCompound(out_s), Part.makeCompound(out_l), Part.makeCompound(out_p)


def rear_lights(c):
    x, w, h = P.lights
    hs, ls = [], []
    for s in (-1, 1):
        a, b = G.light_box(s * x, c["deck_rear"], c["header_z"], w=w, h=h)
        hs.append(a)
        ls.append(b)
    plate = box_span((-220.0, 220.0), (c["deck_rear"] - 4.0, c["deck_rear"]), (c["header_z"] - 50.0,
                                                                            c["header_z"] + 50.0))
    return Part.makeCompound(hs), Part.makeCompound(ls), plate


# ---------------------------------------------------------------------
# Hoses
# ---------------------------------------------------------------------
def suction_port(c):
    return G.xform(C.SUCTION_PORT, box_placement(c))


def discharge_port(c):
    return G.xform(C.DISCHARGE_PORT, box_placement(c))


def suction_hoses(c):
    """From every IBC elbow down through the floor to the header under the floor, forward through the cross
    members and the front rail, up to the suction port at the back of the control box."""
    hx = P.header_x
    hz = c["header_z"]
    out = []
    for ey in c["elbow_y"]:
        out.append(hose([(0.0, ey, c["elbow_out_z"]), (0.0, ey, hz + 30.0), (hx, ey + 30.0, hz)]))
    px, py, pz = suction_port(c)
    df = c["deck_front"]
    out.append(hose([(hx, c["elbow_y"][-1] + 30.0, hz), (hx, df + 60.0, hz), (px, df + 170.0, pz), (px, py, pz)]))
    return fuse_all(out)


def discharge_hose(c, M):
    px, py, pz = discharge_port(c)
    pts = [(px, py, pz)] + G.mast_in_points(M)
    return hose(pts)
