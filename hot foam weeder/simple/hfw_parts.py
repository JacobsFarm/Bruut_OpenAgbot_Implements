"""Parts of the hot foam weeder. Every function returns a Part shape in robot coordinates, hood on the ground (float 0).
The hood shell, castors, mount plate, headstock, parallelogram, liquid gas valves and the propane cylinders are the
flame weeder's (flw_parts, imported); this file adds the belly rails and the water tank, the rear rack with the
boiler, pump and foam can, the foam bar in the hood and the hoses. The hood shell gets the holes for the hot hose.
"""
import math

import Part
from FreeCAD import Vector as V

import hfw_params as P
import flw_parts as FG

W = P.W
box_span = FG.box_span
cyl_x = FG.cyl_x
cyl_y = FG.cyl_y
cyl_z = FG.cyl_z
fuse_all = FG.fuse_all
bolt_z = FG.bolt_z
hex_prism_z = FG.hex_prism_z
tube_path = FG.tube_path
tube_y = FG.tube_y
tube_x = FG.tube_x

HY1 = W.hood_y[1]
HZ = W.hood_h
Z_COVER = FG.Z_COVER
BAR_ZC = P.bar_z
HOSE_IN = (P.hose_x, P.bar_y)                   # where the hot hose goes down through the hood top


def square_z(z0, z1, x, y, s, wall):
    o = box_span((x - s / 2.0, x + s / 2.0), (y - s / 2.0, y + s / 2.0), (z0, z1))
    return o.cut(box_span((x - s / 2.0 + wall, x + s / 2.0 - wall), (y - s / 2.0 + wall, y + s / 2.0 - wall),
                          (z0 - 1, z1 + 1)))


# ---------------------------------------------------------------------
# Hood shell of the flame weeder with the hole for the hot hose
# ---------------------------------------------------------------------
def _hose_hole(z0, z1):
    return cyl_z(P.hose_d + 4.0, z0, z1, HOSE_IN[0], HOSE_IN[1])


def hood_skin():
    return FG.hood_skin().cut(_hose_hole(HZ - 10.0, HZ + 10.0))


def blanket():
    return FG.blanket().cut(_hose_hole(HZ - 40.0, HZ + 10.0))


def top_cover():
    return FG.top_cover().cut(_hose_hole(Z_COVER - 5.0, Z_COVER + 5.0))


# ---------------------------------------------------------------------
# Belly rails, hangers, tank frame, tank
# ---------------------------------------------------------------------
RAIL_BOLTS = [(sx * P.rail_x, y) for sx in (-1, 1) for y in P.robot_lower_beam_y]
FRONT_RAIL_BOLTS = [(x, y) for (x, y) in RAIL_BOLTS if y > 0]     # the rear ones are the long rack bolts
HANGERS = [(sx * P.rail_x, sy * P.hanger_y) for sx in (-1, 1) for sy in (-1, 1)]
FOOT_Z = P.rail_z[0] - P.hanger_foot[2]


def _foot_bolts():
    return [(x, y + dy) for (x, y) in HANGERS for dy in (-30.0, 30.0)]


def rails():
    zc = (P.rail_z[0] + P.rail_z[1]) / 2.0
    out = []
    for sx in (-1, 1):
        x = sx * P.rail_x
        t = tube_y(P.rail_y[0], P.rail_y[1], x, zc, P.rail, P.rail, P.rail_wall)
        ends = [box_span((x - P.rail / 2.0, x + P.rail / 2.0), (y0, y0 + 3.0), P.rail_z)
                for y0 in (P.rail_y[0], P.rail_y[1] - 3.0)]
        t = fuse_all([t] + ends)
        holes = [cyl_z(P.m10_hole, P.rail_z[0] - 1, P.rail_z[1] + 1, bx, by) for (bx, by) in RAIL_BOLTS if bx == x]
        holes += [cyl_z(8.5, P.rail_z[0] - 1, P.rail_z[0] + P.rail_wall + 1, bx, by) for (bx, by) in _foot_bolts()
                  if bx == x]
        out.append(t.cut(holes))
    return Part.makeCompound(out)


def rail_bolts():
    return Part.makeCompound([bolt_z(x, y, P.robot_lower_beam_z[1], P.rail_z[0]) for (x, y) in FRONT_RAIL_BOLTS])


def hangers():
    """Vertical 40 x 40 x 3 with a foot plate under the rail, welded onto the tank frame."""
    fx, fy, ft = P.hanger_foot
    out = []
    for (x, y) in HANGERS:
        tube = square_z(P.frame_z[1], FOOT_Z, x, y, 40.0, 3.0)
        foot = box_span((x - fx / 2.0, x + fx / 2.0), (y - fy / 2.0, y + fy / 2.0), (FOOT_Z, P.rail_z[0]))
        foot = foot.cut([cyl_z(8.5, FOOT_Z - 1, P.rail_z[0] + 1, x, by) for by in (y - 30.0, y + 30.0)])
        out.append(fuse_all([tube, foot]))
    return Part.makeCompound(out)


def hanger_bolts():
    out = []
    for (x, y) in _foot_bolts():
        out.append(fuse_all([hex_prism_z(13.0, FOOT_Z - 5.3, FOOT_Z, x, y),
                             cyl_z(8.0, FOOT_Z, P.rail_z[0] + P.rail_wall + 6.0, x, y)]))
    return Part.makeCompound(out)


def tank_frame():
    zc = (P.frame_z[0] + P.frame_z[1]) / 2.0
    fx, fy = P.frame_x, P.hanger_y
    longs = [tube_y(-fy - 20.0, fy + 20.0, sx * fx, zc, 40.0, 40.0, 3.0) for sx in (-1, 1)]
    cross = [tube_x(-P.rail_x - 20.0, P.rail_x + 20.0, sy * fy, zc, 40.0, 40.0, 3.0) for sy in (-1, 1)]
    stubs = [tube_x(sx * (fx - 20.0), sx * (P.rail_x + 20.0), sy * fy, zc, 40.0, 40.0, 3.0)
             for sx in (-1, 1) for sy in (-1, 1)] if P.rail_x + 20.0 > fx + 20.0 else []
    return fuse_all(longs + cross + stubs)


def tank_pads():
    return Part.makeCompound([box_span((sx * P.frame_x - 20.0, sx * P.frame_x + 20.0), (P.tank_y[0] + 10.0,
                                                                                         P.tank_y[1] - 10.0),
                                       (P.frame_z[1], P.tank_z[0])) for sx in (-1, 1)])


def _rbox(x, y, z, r):
    (x0, x1), (y0, y1), (z0, z1) = x, y, z
    b = box_span((x0, x1), (y0, y1), (z0, z1))
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1.0]
    return b.makeFillet(r, edges)


def tank_shell():
    t = P.tank_wall
    out = _rbox((-P.tank_x, P.tank_x), P.tank_y, P.tank_z, P.tank_r)
    inn = _rbox((-P.tank_x + t, P.tank_x - t), (P.tank_y[0] + t, P.tank_y[1] - t), (P.tank_z[0] + t, P.tank_z[1] - t),
                P.tank_r - t)
    return out.cut(inn)


def tank_fittings():
    """Camlock fill coupling (rear, top) and suction fitting (rear, bottom), level sensor on the top."""
    y0 = P.tank_y[0]
    fx, fd = P.fill_coupling
    fill = fuse_all([cyl_y(fd, y0 - 45.0, y0 + 1.0, fx, P.tank_z[1] - 45.0),
                     cyl_y(fd + 14.0, y0 - 20.0, y0 - 10.0, fx, P.tank_z[1] - 45.0)])
    ox, od = P.outlet
    suct = cyl_y(od + 10.0, y0 - 30.0, y0 + 1.0, ox, P.tank_z[0] + 40.0)
    level = cyl_z(45.0, P.tank_z[1] - 1.0, P.tank_z[1] + 20.0, 0.0, 0.0)
    return Part.makeCompound([fill, suct, level])


# ---------------------------------------------------------------------
# Rear rack and deck
# ---------------------------------------------------------------------
RACK_BOLTS = [(sx * P.rack_x, y) for sx in (-1, 1) for y in P.robot_lower_beam_y[:2]]


def rack():
    zc = (P.rack_z[0] + P.rack_z[1]) / 2.0
    out = []
    for sx in (-1, 1):
        x = sx * P.rack_x
        t = tube_y(P.rack_y[1], P.rack_y[0], x, zc, 40.0, 40.0, 3.0)
        t = t.cut([cyl_z(P.m10_hole, P.rack_z[0] - 1, P.rack_z[1] + 1, bx, by) for (bx, by) in RACK_BOLTS if bx == x])
        out.append(t)
    return Part.makeCompound(out)


def rack_bolts():
    """Long M10: rack tube, rear lower beam and belly rail in one stack."""
    return Part.makeCompound([bolt_z(x, y, P.rack_z[1], P.rail_z[0]) for (x, y) in RACK_BOLTS])


def deck_plate():
    (x0, x1), (y0, y1), t = P.deck
    return box_span((x0, x1), (y0, y1), (P.rack_z[1], P.deck_z))


# ---------------------------------------------------------------------
# Boiler, pump, foam can and doser on the deck
# ---------------------------------------------------------------------
BX, BY = P.boiler_xy
BZ0 = P.deck_z + 30.0                           # on 4 feet
BZ1 = BZ0 + P.boiler_h


def boiler_feet():
    r = P.boiler_d / 2.0 - 40.0
    return Part.makeCompound([box_span((BX + dx - 20.0, BX + dx + 20.0), (BY + dy - 20.0, BY + dy + 20.0), (P.deck_z, BZ0))
                              for dx in (-r, r) for dy in (-r * 0.6, r * 0.6)])


def boiler():
    drum = cyl_z(P.boiler_d, BZ0, BZ1, BX, BY)
    lid = cyl_z(P.boiler_d - 30.0, BZ1, BZ1 + 30.0, BX, BY)
    fd, fh = P.flue
    stack = cyl_z(fd, BZ1 + 30.0, BZ1 + 30.0 + fh, BX, BY)
    cap = cyl_z(fd + 70.0, BZ1 + 40.0 + fh, BZ1 + 46.0 + fh, BX, BY)
    cap_posts = [cyl_z(6.0, BZ1 + 30.0 + fh, BZ1 + 40.0 + fh, BX + dx, BY) for dx in (-40.0, 40.0)]
    return fuse_all([drum, lid, stack, cap] + cap_posts)


FAN_X1 = BX - P.boiler_d / 2.0 + 10.0
FAN = (FAN_X1 - P.burner_fan[1], BY + P.burner_fan[2], BZ0 + P.burner_fan[3])     # outer end x, y, z of the fan


def burner():
    """Burner fan with the gas valve on the -x side of the drum, near the bottom (the burner fires up inside)."""
    d, ln, dy, dz = P.burner_fan
    x0, y, z = FAN
    fan = cyl_x(d, x0, FAN_X1, y, z)
    valve = box_span((x0 + 10.0, x0 + 50.0), (y + d / 2.0 - 5.0, y + d / 2.0 + 25.0), (z - 20.0, z + 20.0))
    return fuse_all([fan, valve])


def water_ports():
    """Inlet (cold, front) and outlet (hot, rear) of the coil."""
    zi, zo = BZ0 + 80.0, BZ1 - 80.0
    r = P.boiler_d / 2.0
    return Part.makeCompound([cyl_y(28.0, BY + r - 5.0, BY + r + 25.0, BX + 60.0, zi),
                              cyl_y(28.0, BY - r - 25.0, BY - r + 5.0, BX + 60.0, zo)])


def pump():
    x, y = P.pump_xy
    bx, by, bz = P.pump_box
    head = box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0, y - by / 2.0 + 60.0), (P.deck_z + 10.0, P.deck_z + 10.0 + bz))
    motor = cyl_y(bz - 10.0, y - by / 2.0 + 60.0, y + by / 2.0, x, P.deck_z + 10.0 + bz / 2.0)
    feet = box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0, y + by / 2.0), (P.deck_z, P.deck_z + 10.0))
    return fuse_all([head, motor, feet])


def foam_can():
    x, y = P.can_xy
    bx, by, bz = P.can_box
    can = box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0, y + by / 2.0), (P.deck_z, P.deck_z + bz))
    cap = cyl_z(50.0, P.deck_z + bz, P.deck_z + bz + 25.0, x - 50.0, y)
    return fuse_all([can, cap])


def doser():
    x, y = P.doser_xy
    dx, dy, dz = P.doser_box
    return box_span((x - dx / 2.0, x + dx / 2.0), (y - dy / 2.0, y + dy / 2.0), (P.deck_z, P.deck_z + dz))


def can_bracket():
    """Angle frame round the foot of the can and a strap over it."""
    x, y = P.can_xy
    bx, by, bz = P.can_box
    ring = box_span((x - bx / 2.0 - 3.0, x + bx / 2.0 + 3.0), (y - by / 2.0 - 3.0, y + by / 2.0 + 3.0),
                    (P.deck_z, P.deck_z + 40.0)).cut(box_span((x - bx / 2.0, x + bx / 2.0), (y - by / 2.0, y + by / 2.0),
                                                              (P.deck_z - 1, P.deck_z + 41.0)))
    strap = box_span((x - bx / 2.0 - 3.0, x + bx / 2.0 + 3.0), (y - 15.0, y + 15.0), (P.deck_z + bz, P.deck_z + bz + 2.0))
    sides = [box_span((x + s * (bx / 2.0 + 1.5) - 1.5, x + s * (bx / 2.0 + 1.5) + 1.5), (y - 15.0, y + 15.0),
                      (P.deck_z + 40.0, P.deck_z + bz + 2.0)) for s in (-1, 1)]
    return fuse_all([ring, strap] + sides)


# ---------------------------------------------------------------------
# Foam bar in the hood
# ---------------------------------------------------------------------
def foam_bar():
    pipe = cyl_x(P.bar_d, -P.bar_x, P.bar_x, P.bar_y, BAR_ZC)
    caps = [cyl_x(P.bar_d + 6.0, s * P.bar_x - (8.0 if s > 0 else 0.0), s * P.bar_x + (0.0 if s > 0 else 8.0),
                  P.bar_y, BAR_ZC) for s in (-1, 1)]
    tee = cyl_z(P.bar_d, BAR_ZC, BAR_ZC + 25.0, P.hose_x, P.bar_y)
    return fuse_all([pipe, tee] + caps)


def nozzles():
    out = []
    z1 = BAR_ZC - P.bar_d / 2.0 + 2.0
    for x in P.nozzle_x:
        body = cyl_z(P.nozzle[0], z1 - P.nozzle[1], z1, x, P.bar_y)
        tip = box_span((x - 12.0, x + 12.0), (P.bar_y - 4.0, P.bar_y + 4.0), (z1 - P.nozzle[1] - 10.0, z1 - P.nozzle[1]))
        air = cyl_y(8.0, P.bar_y - 18.0, P.bar_y, x, z1 - 25.0)
        out.append(fuse_all([body, tip, air]))
    return Part.makeCompound(out)


def bar_clamps():
    """Flat bars 30 x 5 from the bar up to the hood top (through the blanket, bolted to the skin)."""
    z0 = BAR_ZC
    z1 = HZ - W.skin
    out = []
    for x in P.bar_clamps_x:
        strap = box_span((x - 15.0, x + 15.0), (P.bar_y + P.bar_d / 2.0, P.bar_y + P.bar_d / 2.0 + 5.0), (z0 - 20.0, z1))
        out.append(strap)
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Hoses
# ---------------------------------------------------------------------
def suction_hose():
    """Tank outlet (rear wall) -> up in front of the rear beams -> over them -> down onto the pump head."""
    ox = P.outlet[0]
    y0 = P.tank_y[0] - 30.0
    z0 = P.tank_z[0] + 40.0
    px, py = P.pump_xy
    y_up = P.robot_lower_beam_y[1] + 35.0                               # -390: in front of the rear inner beam
    z_over = P.rack_z[1] + 20.0                                         # over the rear beams, under the collars
    y_back = P.robot_lower_beam_y[0] + 15.0                             # -560
    z_top = P.deck_z + 10.0 + P.pump_box[2] + 30.0
    xi = px - 20.0
    yi = py - P.pump_box[1] / 2.0 + 30.0
    return tube_path([(ox, y0, z0), (ox, y_up, z0), (ox, y_up, z_over), (ox, y_back, z_over), (ox, y_back, z_top),
                      (xi, yi, z_top), (xi, yi, z_top - 29.0)], 20.0)


def pressure_hose():
    """Pump outlet -> boiler inlet (front port)."""
    px, py = P.pump_xy
    zi = BZ0 + 80.0
    y_in = BY + P.boiler_d / 2.0 + 25.0
    y_p = py + 35.0
    z = P.deck_z + 40.0
    return tube_path([(px + P.pump_box[0] / 2.0 - 1.0, y_p, z), (px + 110.0, y_p, z), (px + 110.0, y_in + 25.0, zi),
                      (BX + 60.0, y_in + 25.0, zi), (BX + 60.0, y_in - 1.0, zi)], 18.0)


def hot_hose():
    """Boiler outlet (rear port) -> past the rear of the deck -> down into the hood to the tee of the foam bar."""
    zo = BZ1 - 80.0
    y_out = BY - P.boiler_d / 2.0 - 25.0
    yd = P.deck[1][0] - 40.0                    # behind the deck
    return tube_path([(BX + 60.0, y_out + 1.0, zo), (BX + 60.0, yd, zo), (P.hose_x, yd, zo),
                      (P.hose_x, HOSE_IN[1], Z_COVER + 120.0), (P.hose_x, HOSE_IN[1], BAR_ZC + 24.0)], P.hose_d)


def foam_hose():
    """Can -> doser -> pump head (foam is dosed into the suction side)."""
    x, y = P.doser_xy
    cx, cy = P.can_xy
    z = P.deck_z + 60.0
    px, py = P.pump_xy
    yh = py - P.pump_box[1] / 2.0
    a = tube_path([(cx + P.can_box[0] / 2.0 - 1.0, y, z), (x - P.doser_box[0] / 2.0 + 1.0, y, z)], 10.0)
    b = tube_path([(x, y + P.doser_box[1] / 2.0 - 1.0, z), (x, yh - 60.0, z), (px + 20.0, yh - 60.0, z),
                   (px + 20.0, yh + 1.0, z)], 10.0)
    return Part.makeCompound([a, b])


def cylinder_hoses():
    """Liquid propane: cylinder valves -> between the rear beams -> filter (as on the flame weeder)."""
    z1 = W.sub_plate[2][0]
    zc = FG.cyl_axis_z()
    out = []
    for x in W.cyl_x:
        out.append(tube_path([(x, W.cyl_y[0] - 40.0, zc - 60.0), (x, -500.0, zc - 60.0), (x * 0.25, -500.0, z1 + 30.0),
                              (-40.0 if x < 0 else -20.0, -500.0, z1 + 30.0), (-40.0 if x < 0 else -20.0, -500.0, z1)],
                             W.hose_d))
    return Part.makeCompound(out)


def gas_hose():
    """Main valves -> behind the rear beams -> up to the burner on the deck (the burner has its own vaporiser in the
    flue and its own regulator and valve)."""
    yc = (W.panel_y[0] + W.panel_y[1]) / 2.0
    z1 = W.sub_plate[2][0]
    yb = P.deck[1][1] + 20.0                    # between the sub plate (-625) and the deck (-660)
    x0 = 75.0                                   # between the headstock plates
    x1, yf, zf = FAN[0] + 25.0, FAN[1], FAN[2]
    y_in = yf + P.burner_fan[0] / 2.0 + 1.0
    return tube_path([(x0, yc, z1 - 50.0), (x0, yb, z1 - 50.0), (x0, yb, P.rack_z[0] - 20.0),
                      (x1, yb, P.rack_z[0] - 20.0), (x1, yb, P.deck_z + 60.0), (x1, y_in + 40.0, zf),
                      (x1, y_in - 2.0, zf)], W.hose_d)


# ---------------------------------------------------------------------
# Scene: path, weeds alive and killed, foam
# ---------------------------------------------------------------------
def path_strip(y0, y1, w=1800.0):
    return box_span((-w / 2.0, w / 2.0), (y0, y1), (-40.0, 0.0))


def weed(x, y, s=1.0):
    return FG.weed(x, y, s)


def weed_dead(x, y, s=1.0):
    return FG.weed_scorched(x, y, s)


def foam(x0, x1, y0, y1, z=0.0, h=12.0):
    return box_span((x0, x1), (y0, y1), (z, z + h))
