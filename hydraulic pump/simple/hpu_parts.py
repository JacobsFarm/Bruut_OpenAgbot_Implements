"""Parts of the hydraulic power pack. Every function returns a Part shape in robot coordinates."""
import Part
from FreeCAD import Vector as V

import hpu_params as P


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl(d, p0, p1):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a)


def tube_span(x, y, z, t, axis):
    outer = box_span(x, y, z)
    spans = {"x": list(x), "y": list(y), "z": list(z)}
    for k in spans:
        if k == axis:
            spans[k] = [spans[k][0] - 1.0, spans[k][1] + 1.0]
        else:
            spans[k] = [spans[k][0] + t, spans[k][1] - t]
    return outer.cut(box_span(spans["x"], spans["y"], spans["z"]))


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def bolt_z(d, x, y, z_head, z_nut, head=17.0, k=6.4, m=8.4):
    return Part.makeCompound([cyl(head * 1.1, (x, y, z_head - k), (x, y, z_head)),
                              cyl(d, (x, y, z_head), (x, y, z_nut + m + 3.0)),
                              cyl(head * 1.1, (x, y, z_nut), (x, y, z_nut + m))])


def hose_path(points, d=None):
    """Hose along a polyline (solid, drawn only): cylinders and balls at the bends."""
    d = P.hose_d if d is None else d
    out = [cyl(d, points[i], points[i + 1]) for i in range(len(points) - 1)]
    out += [Part.makeSphere(d / 2.0, V(*p)) for p in points[1:-1]]
    return fuse_all(out)


# ---------------------------------------------------------------------
# Mount
# ---------------------------------------------------------------------
BEARER_Z = (P.robot_upper_beam_z[1], P.robot_upper_beam_z[1] + 40.0)
PLATE_Z = (BEARER_Z[1], BEARER_Z[1] + P.plate_t)
TOP = PLATE_Z[1]


def bearers():
    out = []
    for y in P.bearer_y:
        b = tube_span((-P.bearer_x, P.bearer_x), (y - 20.0, y + 20.0), BEARER_Z, 3.0, "x")
        for sx in (-1, 1):
            for x in P.bearer_bolt_x:
                b = b.cut(cyl(P.m10_hole, (sx * x, y, 600), (sx * x, y, 800)))
        for x, yb in P.plate_bolts:
            if yb == y:
                b = b.cut(cyl(8.4, (x, y, 600), (x, y, 800)))
        out.append(b)
    return Part.makeCompound(out)


def plate():
    s = box_span((-P.plate_x, P.plate_x), P.plate_y, PLATE_Z)
    for x, y in P.plate_bolts:
        s = s.cut(cyl(8.4, (x, y, 600), (x, y, 800)))
    return s


def bolts():
    out = [bolt_z(10.0, sx * x, y, P.robot_upper_beam_z[0], BEARER_Z[1]) for sx in (-1, 1) for x in P.bearer_bolt_x
           for y in P.bearer_y]
    out += [bolt_z(8.0, x, y, BEARER_Z[1] - 3.0, PLATE_Z[1], head=13.0, k=5.3, m=6.8) for x, y in P.plate_bolts]
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Tank
# ---------------------------------------------------------------------
TANK_Z = (TOP, TOP + P.tank_h)


def tank():
    s = box_span(P.tank_x, P.tank_y, TANK_Z)
    t = P.tank_t
    s = s.cut(box_span((P.tank_x[0] + t, P.tank_x[1] - t), (P.tank_y[0] + t, P.tank_y[1] - t), (TANK_Z[0] + t, TANK_Z[1] - t)))
    return s


def tank_fittings():
    """Return filter and filler cap on the lid, sight glass on the front."""
    xc = (P.tank_x[0] + P.tank_x[1]) / 2.0
    filt = cyl(P.filter[0], (xc, P.tank_y[0] + 60.0, TANK_Z[1]), (xc, P.tank_y[0] + 60.0, TANK_Z[1] + P.filter[1]))   # return
    capf = cyl(P.cap[0], (xc, P.tank_y[1] - 50.0, TANK_Z[1]), (xc, P.tank_y[1] - 50.0, TANK_Z[1] + P.cap[1]))
    glass = box_span((xc - 15.0, xc + 15.0), (P.tank_y[1], P.tank_y[1] + 8.0), (TANK_Z[0] + 120.0, TANK_Z[0] + 320.0))
    return Part.makeCompound([filt, capf, glass])


def oil(level=0.85):
    t = P.tank_t
    return box_span((P.tank_x[0] + t, P.tank_x[1] - t), (P.tank_y[0] + t, P.tank_y[1] - t),
                    (TANK_Z[0] + t, TANK_Z[0] + t + (P.tank_h - 2 * t) * level))


# ---------------------------------------------------------------------
# Motor, bell housing, pump, controller
# ---------------------------------------------------------------------
MZ = P.motor_z


def motor():
    x = P.motor_x
    body = cyl(P.motor_d, (x, P.motor_y[0], MZ), (x, P.motor_y[1], MZ))
    feet = [box_span((x - 50.0, x + 50.0), (y - 20.0, y + 20.0), (TOP, MZ - 30.0)) for y in (P.motor_y[0] - 40.0, P.motor_y[1] + 40.0)]
    return fuse_all([body] + feet)


def bell_pump():
    x = P.motor_x
    y0 = P.motor_y[1]
    bell = cyl(P.bell[0], (x, y0, MZ), (x, y0 - P.bell[1], MZ))
    px, py, pz = P.pump
    pmp = box_span((x - px / 2.0, x + px / 2.0), (y0 - P.bell[1] - py, y0 - P.bell[1]), (MZ - pz / 2.0, MZ + pz / 2.0))
    return fuse_all([bell, pmp])


def controller():
    return box_span(*P.controller)


# ---------------------------------------------------------------------
# Valve block, couplers, hoses
# ---------------------------------------------------------------------
VZ = (P.valve_z[0] + P.valve_z[1]) / 2.0
VY = (P.valve_y[0] + P.valve_y[1]) / 2.0


def valve_block():
    blk = box_span(P.valve_x, P.valve_y, P.valve_z)
    stand = box_span((P.valve_x[0] + 10.0, P.valve_x[1] - 10.0), (P.valve_y[0] + 10.0, P.valve_y[1] - 10.0), (TOP, P.valve_z[0]))
    return fuse_all([blk, stand])


def solenoids():
    """2 solenoids per work section on top, gauge and relief valve on the inlet section."""
    out = []
    for x in P.section_x:
        for y in (P.valve_y[0] + 20.0, P.valve_y[1] - 20.0):
            out.append(cyl(P.solenoid[0], (x, y, P.valve_z[1]), (x, y, P.valve_z[1] + P.solenoid[1])))
    out.append(cyl(P.gauge[0], (-5.0, VY, P.valve_z[1]), (-5.0, VY, P.valve_z[1] + P.gauge[1])))
    return Part.makeCompound(out)


def couplers():
    y1 = P.valve_y[0]
    out = []
    for x in P.cpl_x:
        body = cyl(P.cpl_d, (x, y1, P.cpl_z), (x, y1 - P.cpl_len, P.cpl_z))
        nut = cyl(P.cpl_d + 4.0, (x, y1, P.cpl_z), (x, y1 - 12.0, P.cpl_z))
        out.append(fuse_all([body, nut]))
    return Part.makeCompound(out)


def hose_points():
    """Suction (tank -> pump), pressure (pump -> valve inlet), return (valve -> filter on the tank)."""
    x = P.motor_x
    py = P.motor_y[1] - P.bell[1] - P.pump[1] / 2.0          # pump centre (y)
    pxl = x - P.pump[0] / 2.0                                 # pump left face
    tx = (P.tank_x[0] + P.tank_x[1]) / 2.0
    tz1 = TANK_Z[1]
    return {
        "suction": [(P.tank_x[1], P.tank_y[0] + 15.0, TOP + 30.0), (90.0, P.tank_y[0] + 15.0, TOP + 30.0),
                    (90.0, py - 10.0, TOP + 30.0), (pxl, py - 10.0, MZ - 15.0)],
        "pressure": [(pxl, py + 15.0, MZ + 25.0), (P.valve_x[1], VY, MZ + 25.0)],
        "return": [(P.valve_x[0] + 20.0, VY, P.valve_z[1]), (P.valve_x[0] + 20.0, VY, tz1 + P.filter[1] + 30.0),
                   (tx, P.tank_y[0] + 60.0, tz1 + P.filter[1] + 30.0), (tx, P.tank_y[0] + 60.0, tz1 + P.filter[1])],
    }


def hoses():
    return Part.makeCompound([hose_path(pts) for pts in hose_points().values()])
