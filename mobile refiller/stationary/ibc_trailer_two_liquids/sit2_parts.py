"""Parts of the two-liquid IBC trailer that differ from ../ibc_trailer: frame members with holes for two suction
lines, the deeper control box with two pumps, the two suction and two discharge hoses, the arm with two drop pipes and
nozzles. Trailer coordinates (origin = middle of the axle on the ground, y forward). c = sit2_params.cfg().
Box parts are in box-local coordinates (as ../stc_parts: x = width, door on +y); arm parts are drawn with the arm out
to the left (-x).
"""
import math

import Part
from FreeCAD import Vector as V

import sit2_params as P
import sit_params as TP
import sit_parts as TG
import stc_params as C
import stc_parts as G
from stc_parts import box_span, cyl_x, cyl_y, cyl_z, rtube, fuse_all, hose

LIQ = P.LIQUIDS


def moved(shape, dx=0.0, dy=0.0, dz=0.0):
    s = shape.copy()
    s.translate(V(dx, dy, dz))
    return s


# ---------------------------------------------------------------------
# Frame: cross members and end rails with a hole per suction line
# ---------------------------------------------------------------------
def _hole(x, y0, y1, c):
    return Part.makeCylinder(28.0, y1 - y0 + 2.0, V(x, y0 - 1.0, c["header_z"]), V(0, 1, 0))


def _holes(y, y0, y1, c):
    """Holes for the lines that pass this y: line A ahead of the front elbow, line B ahead of the rear one."""
    out = []
    for i, liq in enumerate(LIQ):
        if y > c["elbow_y"][i]:
            out.append(_hole(P.header_x[liq], y0, y1, c))
    return out


def cross_members(c):
    w, h, t = TP.cross
    z = (c["rail_z"][1] - h, c["rail_z"][1])
    out = []
    for y in TG._cross_positions(c):
        m = rtube((-TP.rail_x[0], TP.rail_x[0]), (y - w / 2.0, y + w / 2.0), z, t, "x")
        hs = _holes(y, y - w / 2.0, y + w / 2.0, c)
        out.append(m.cut(hs) if hs else m)
    return Part.makeCompound(out)


def end_rails(c):
    w, h, t = TP.rail
    x = (-TP.rail_x[0], TP.rail_x[0])
    y0 = c["deck_front"] - w
    front = rtube(x, (y0, c["deck_front"]), c["rail_z"], t, "x").cut(_holes(1e9, y0, c["deck_front"], c))
    rear = rtube(x, (c["deck_rear"], c["deck_rear"] + w), c["rail_z"], t, "x")
    return Part.makeCompound([front, rear])


# ---------------------------------------------------------------------
# Control box with two pumps (box local)
# ---------------------------------------------------------------------
BW, BH = C.box[0], C.box[2]
BY0, BY1 = P.box_y
FZ = G.FZ
PY, PZ = C.pump_axis
DZ = C.discharge_z


def box_placement(c):
    return G.placement(P.box_x, c["box_y"], c["box_z"], 90.0)


def box_rails():
    w, h = C.box_foot
    return Part.makeCompound([rtube((-BW / 2.0, BW / 2.0), (y - w / 2.0, y + w / 2.0), (0.0, h), 2.0, "x")
                              for y in P.box_rail_y])


def box_shell():
    t = C.box_wall
    outer = box_span((-BW / 2.0, BW / 2.0), (BY0, BY1), (FZ, BH))
    inner = box_span((-BW / 2.0 + t, BW / 2.0 - t), (BY0 + t, BY1 - t), (FZ + t, BH - t))
    holes = []
    for liq in LIQ:
        y = PY + P.pump_dy[liq]
        holes += [cyl_x(52.0, -BW / 2.0 - 1.0, -BW / 2.0 + t + 1.0, y, PZ),
                  cyl_x(52.0, BW / 2.0 - t - 1.0, BW / 2.0 + 1.0, y, DZ)]
    return outer.cut(inner).cut(holes)


def box_roof():
    o, t = C.box_roof
    return box_span((-BW / 2.0 - o, BW / 2.0 + o), (BY0 - o, BY1 + o), (BH, BH + t))


def box_door():
    """The door of the 1-pump box, on the deeper front face."""
    return moved(G.box_door(), dy=BY1 - G.DOOR_Y[0])


def estop():
    base, knob = G.estop()
    d = BY1 - G.DOOR_Y[0]
    return moved(base, dy=d), moved(knob, dy=d)


def box_glands():
    t = C.box_wall
    g = [cyl_z(C.gland_d, FZ - 12.0, FZ, x, -60.0) for x in (-120.0, -60.0, 0.0)]
    for liq in LIQ:
        y = PY + P.pump_dy[liq]
        g.append(cyl_x(70.0, -BW / 2.0 - 8.0, -BW / 2.0, y, PZ).cut(cyl_x(40.0, -BW / 2.0 - 9, -BW / 2.0 + 1, y, PZ)))
        g.append(cyl_x(70.0, BW / 2.0, BW / 2.0 + 8.0, y, DZ).cut(cyl_x(40.0, BW / 2.0 - 1, BW / 2.0 + 9, y, DZ)))
    return fuse_all(g) if t else None


def pump(liq):
    return moved(G.pump(), dy=P.pump_dy[liq])


def pump_feet(liq):
    return moved(G.pump_feet(), dy=P.pump_dy[liq])


def discharge_line(liq):
    return moved(G.discharge_line(), dy=P.pump_dy[liq])


def flow_meter(liq):
    return moved(G.flow_meter(), dy=P.pump_dy[liq])


def motor_valve(liq):
    return moved(G.motor_valve(), dy=P.pump_dy[liq])


def suction_port(c, liq):
    x, y, z = C.SUCTION_PORT
    return G.xform((x, y + P.pump_dy[liq], z), box_placement(c))


def discharge_port(c, liq):
    x, y, z = C.DISCHARGE_PORT
    return G.xform((x, y + P.pump_dy[liq], z), box_placement(c))


# ---------------------------------------------------------------------
# Hoses
# ---------------------------------------------------------------------
def suction_hose(c, liq):
    """From the elbow of its IBC down through the floor to its own line under the floor, forward through the cross
    members and the front rail, up to its suction port on the back of the control box."""
    i = LIQ.index(liq)
    hx = P.header_x[liq]
    hz = c["header_z"]
    ey = c["elbow_y"][i]
    px, py, pz = suction_port(c, liq)
    df = c["deck_front"]
    pts = [(0.0, ey, c["elbow_out_z"]), (0.0, ey, hz + 30.0), (hx, ey + 30.0, hz), (hx, df + 60.0, hz),
           (px, df + 170.0, pz), (px, py, pz)]
    return hose(pts)


def mast_specs(c):
    """Mast spec per nozzle (A near, B far) and one for the antenna in the middle, drawn with the arm low."""
    out = {}
    for key, reach in (("A", c["reach_A"]), ("B", c["reach_B"]), ("mid", c["reach"])):
        out[key] = G.mast_spec(0.0, c["mast_y"], c["rail_z"][1], reach, tube=P.mast_round, nozzle_z=P.nozzle_tip_z,
                               in_face="-y", in_z=None, folds=(c["fold"], 0.0, -180.0))
    return out


# ---------------------------------------------------------------------
# Round mast with a lifting sleeve (carriage) and an electric linear actuator
# ---------------------------------------------------------------------
def mast_r():
    return P.mast_round[0] / 2.0


def sleeve_z(M):
    """Sleeve (low position): from under the arm to just above it."""
    d, t, below, above = P.sleeve
    return (M["arm_z"][0] - below, M["arm_z"][1] + above)


def mast_top(M):
    return sleeve_z(M)[1] + P.lift_high + P.mast_top_extra


def mast_base_z(c):
    return c["rail_z"][1] + P.base_plate[1]


def mast_tube(c, M):
    d, t = P.mast_round
    z0, z1 = mast_base_z(c), mast_top(M)
    tube = cyl_z(d, z0, z1, M["x"], M["y"]).cut(cyl_z(d - 2 * t, z0 - 1.0, z1 - 6.0, M["x"], M["y"]))
    return tube


def mast_base(c, M):
    s, t = P.base_plate
    z = c["rail_z"][1]
    plate = box_span((M["x"] - s / 2.0, M["x"] + s / 2.0), (M["y"] - s / 2.0, M["y"] + s / 2.0), (z, z + t))
    return plate


def mast_gussets(c, M):
    """Four gussets 10 mm from the round mast to the foot plate (front and back stay clear of the hoses and the
    actuator bracket: on the +-x faces and diagonally)."""
    Mg = dict(M)
    Mg["tube"] = (2.0 * mast_r(), M["tube"][1])
    return G.mast_gussets(Mg, mast_base_z(c), ("+x", "-x"), h=200.0, l=100.0)


def actuator_xy(M):
    return (M["x"], M["y"] + P.actuator_dy)


def actuator_body_z(M):
    """Body of the actuator: top just under the lug of the thrust collar in the low position."""
    top = sleeve_z(M)[0] - P.collar[1] - 15.0
    return (top - P.actuator[2], top)


def actuator_body(c, M):
    d, rd, bl, rl = P.actuator
    x, y = actuator_xy(M)
    z0, z1 = actuator_body_z(M)
    body = cyl_z(d, z0, z1, x, y)
    gland = cyl_z(d - 20.0, z1, z1 + 10.0, x, y)
    motor = cyl_z(70.0, z0 + 80.0, z0 + 280.0, x, y + d / 2.0 + 30.0)
    gear = box_span((x - 35.0, x + 35.0), (y, y + d / 2.0 + 30.0), (z0 + 80.0, z0 + 180.0))
    return fuse_all([body, gland, motor, gear])


def actuator_bracket(c, M):
    """Clevis bracket from the mast to the foot of the actuator."""
    x, y = actuator_xy(M)
    z0 = actuator_body_z(M)[0]
    r = mast_r()
    plate = box_span((x - 50.0, x + 50.0), (M["y"] + r - 5.0, y + 45.0), (z0 - 30.0, z0))
    return plate.cut(cyl_z(P.mast_round[0] - 1.0, z0 - 31.0, z0 + 1.0, M["x"], M["y"]))


def collar_lug(M):
    """Thrust collar under the sleeve (does not turn) with the lug for the actuator rod (Lift part, low position)."""
    w, h = P.collar
    r = mast_r()
    z1 = sleeve_z(M)[0]
    z0 = z1 - h
    ring = cyl_z(2.0 * (r + w), z0, z1, M["x"], M["y"]).cut(cyl_z(2.0 * r + 2.0, z0 - 1.0, z1 + 1.0, M["x"], M["y"]))
    x, y = actuator_xy(M)
    lug = box_span((x - 25.0, x + 25.0), (M["y"] + r + w - 3.0, y + 25.0), (z0, z1))
    return fuse_all([ring, lug])


def actuator_rod(M):
    d, rd, bl, rl = P.actuator
    x, y = actuator_xy(M)
    z1 = sleeve_z(M)[0] - P.collar[1]
    return cyl_z(rd, z1 - rl, z1, x, y)


def sleeve(M):
    """Sleeve on the mast with the arm welded to it (Arm part: drawn low, arm out to the left)."""
    d, t, below, above = P.sleeve
    z0, z1 = sleeve_z(M)
    return cyl_z(d, z0, z1, M["x"], M["y"]).cut(cyl_z(P.mast_round[0] + 2.0, z0 - 1.0, z1 + 1.0, M["x"], M["y"]))


def arm_tube(Ms):
    """60 x 60 x 3 arm from the sleeve to past the far nozzle, with a gusset under the root."""
    M = Ms["B"]
    b, t = C.arm_tube
    mx, my = M["x"], M["y"]
    nx, _ = G.nozzle_xy(M)
    x_root = mx - P.sleeve[0] / 2.0 + 3.0
    tip_x = nx - C.arm_tip
    tube = rtube((tip_x, x_root), (my - b / 2.0, my + b / 2.0), M["arm_z"], t, "x")
    cap = box_span((tip_x - t, tip_x), (my - b / 2.0, my + b / 2.0), M["arm_z"])
    z0 = sleeve_z(M)[0]
    g = G.poly_xz([(x_root, M["arm_z"][0]), (x_root - 200.0, M["arm_z"][0]), (x_root, z0 + 10.0)], my - 5.0, 10.0)
    return fuse_all([tube, cap, g])


# ---------------------------------------------------------------------
# Hoses
# ---------------------------------------------------------------------
def hose_x(liq):
    return P.mast_hose_x[liq]


def hose_y(M):
    return M["y"] - P.mast_hose_off


def lane_z(M):
    return 0.5 * (M["arm_z"][0] + M["arm_z"][1])


def discharge_hose(c, liq, M):
    """Discharge port -> forward and sideways to its half of the rear face of the mast -> up to fixed_top_z. Port A
    lies right of the mast and B left of it, so the two hoses never cross."""
    px, py, pz = discharge_port(c, liq)
    hy = hose_y(M)
    hx = hose_x(liq)
    return hose([(px, py, pz), (px, py + 15.0, pz), (hx, hy, pz + 70.0), (hx, hy, P.fixed_top_z)])


def entry_z(M, lift=0.0):
    return lane_z(M) - P.arm_entry_dz + lift


def loop_length(M):
    return entry_z(M, P.lift_high) - P.fixed_top_z + 60.0


def hose_loop(liq, M, lift=0.0):
    """Slack loop from the top of the fixed hose up to the arm; it bows out sideways when the arm is low."""
    hx, hy = hose_x(liq), hose_y(M)
    z0, z1 = P.fixed_top_z, entry_z(M, lift)
    dz = z1 - z0
    half = loop_length(M) / 2.0
    s = math.sqrt(max(0.0, half * half - (dz / 2.0) ** 2)) * P.loop_side[liq]
    pts = [(hx, hy, z0 - 1.0), (hx + 0.55 * s, hy, z0 + 0.22 * dz), (hx + s, hy, z0 + 0.5 * dz),
           (hx + 0.55 * s, hy, z0 + 0.78 * dz), (hx, hy, z1 + 1.0)]
    return hose(pts)


def mast_clamps(c, M):
    hy = hose_y(M)
    r = mast_r()
    out = []
    for z in (1100.0, 1450.0):
        out.append(box_span((-65.0, 65.0), (hy - 30.0, M["y"] - r + 3.0), (z, z + 30.0)))
    return Part.makeCompound(out)


def _mirror_y(shape, y):
    return shape.mirror(V(0, y, 0), V(0, 1, 0))


def drop_pipe(M):
    """Drop pipe of stc_parts with the side inlet turned to the -y side (the hoses run on that side of the arm)."""
    return _mirror_y(G.drop_pipe(M), M["y"])


def arm_hose(liq, Ms):
    """From the top of the slack loop to its lane on the -y side of the arm, along the arm and down into the side inlet
    of its drop pipe. A (outer lane) crosses over B. Drawn with the arm low and out to the left (Arm part)."""
    M = Ms[liq]
    my = M["y"]
    hy = hose_y(M)
    hx = hose_x(liq)
    hz = lane_z(M)
    nx, ny = G.nozzle_xy(M)
    iz = G._inlet_z(M)
    lane = my + P.arm_lane_dy[liq]
    ez = entry_z(M)
    if abs(P.arm_lane_dy[liq]) < 100.0:          # inner lane: straight onto it
        pts = [(hx, hy, ez), (hx, hy, hz - 40.0), (hx - 85.0, lane, hz)]
        drop_y = my - 80.0
    else:                                       # outer lane: over the arm and the inner hose
        top = M["arm_z"][1] + 45.0
        pts = [(hx, hy, ez), (hx, hy, top), (hx - 50.0, lane, top), (hx - 110.0, lane, hz)]
        drop_y = lane
    pts += [(nx + 80.0, lane, hz), (nx, drop_y, iz + 40.0), (nx, drop_y, iz), (nx, ny - 58.0, iz)]
    return hose(pts)


def arm_saddles(Ms):
    M = Ms["B"]
    my = M["y"]
    za = lane_z(M) - C.hose_od / 2.0
    xa, _ = G.nozzle_xy(Ms["A"])
    xb, _ = G.nozzle_xy(Ms["B"])
    y0 = my - C.arm_tube[0] / 2.0
    y1 = my + min(P.arm_lane_dy.values()) - C.hose_od / 2.0 - 10.0
    out = []
    for x in (0.5 * (M["x"] + xa) - 60.0, 0.5 * (xa + xb)):
        out.append(box_span((x - 15.0, x + 15.0), (y1, y0), (za - 8.0, za)))
        out.append(box_span((x - 15.0, x + 15.0), (y1, y1 + 6.0), (za, za + 30.0)))
    return Part.makeCompound(out)
