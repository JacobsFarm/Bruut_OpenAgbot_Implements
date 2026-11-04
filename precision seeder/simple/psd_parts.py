"""Parts of the precision seeder. Every function returns a Part shape in robot coordinates in the work pose. The
implement frame, gauge wheels and the hitch are the three-point hitch's (tph_parts); this file adds the seeding units
(one per row, drawn with unit(x)), the vacuum blower and its hoses.
"""
import math

import Part
from FreeCAD import Vector as V

import psd_params as P
import tph_parts as TG

box_span = TG.box_span
cyl = TG.cyl
fuse_all = TG.fuse_all
plate_yz = TG.plate_yz

Y0, Y1 = P.UNIT_Y0, P.UNIT_Y1
GZ = P.gauge_d / 2.0                                       # gauge wheel centre z (on the ground)
DZ = P.disc_d / 2.0 - P.seed_depth                         # disc centre z
CROSS = (-1790.0, 345.0)                                   # shank cross tube (y, z), in front of the seed tube
PRESS_Z = P.press_d / 2.0


def _sides(ux, dx, t):
    return [(ux + dx - t / 2.0, ux + dx + t / 2.0), (ux - dx - t / 2.0, ux - dx + t / 2.0)]


# ---------------------------------------------------------------------
# Brackets on the toolbar, links, pins
# ---------------------------------------------------------------------
def brackets(ux):
    pts = ((P.tb_y[0], 270.0), (P.tb_y[0], 140.0), (Y0 - 22.0, 140.0), (Y0 - 22.0, 270.0))
    out = []
    for x0, x1 in _sides(ux, P.bracket_dx, P.plate_t):
        p = plate_yz(pts, x0, x1 - x0)
        for z in P.link_z:
            p = p.cut(cyl(P.pin_d + 0.4, (x0 - 1, Y0, z), (x1 + 1, Y0, z)))
        out.append(p)
    return Part.makeCompound(out)


def links(ux):
    h, t = P.link_w
    out = []
    for x0, x1 in _sides(ux, P.link_dx, t):
        for z in P.link_z:
            bar = box_span((x0, x1), (Y1, Y0), (z - h / 2.0, z + h / 2.0))
            ends = [cyl(h, (x0, y, z), (x1, y, z)) for y in (Y0, Y1)]
            s = fuse_all([bar] + ends)
            s = s.cut([cyl(P.pin_d + 0.4, (x0 - 1, y, z), (x1 + 1, y, z)) for y in (Y0, Y1)])
            out.append(s)
    return Part.makeCompound(out)


def pins(ux):
    out = []
    for z in P.link_z:
        out.append(cyl(P.pin_d, (ux - P.bracket_dx - 8.0, Y0, z), (ux + P.bracket_dx + 8.0, Y0, z)))
        out.append(cyl(P.pin_d, (ux - P.plate_dx - 8.0, Y1, z), (ux + P.plate_dx + 8.0, Y1, z)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Unit frame: 2 side plates, shank with cross tube, press arms
# ---------------------------------------------------------------------
PLATE_PTS = ((Y1 + 20.0, 265.0), (Y1 + 20.0, 140.0), (-1700.0, 110.0), (-1900.0, 110.0), (-1960.0, 170.0),
             (-1960.0, 380.0), (-1840.0, 550.0), (-1630.0, 550.0), (Y1 + 20.0, 460.0))


def side_plates(ux):
    out = []
    s_out = math.copysign(1.0, ux)
    for x0, x1 in _sides(ux, P.plate_dx, P.plate_t):
        p = plate_yz(PLATE_PTS, x0, x1 - x0)
        for z in P.link_z:
            p = p.cut(cyl(P.pin_d + 0.4, (x0 - 1, Y1, z), (x1 + 1, Y1, z)))
        p = p.cut(cyl(22.0, (x0 - 1, P.meter_y, P.meter_z), (x1 + 1, P.meter_y, P.meter_z)))   # meter shaft
        if (x0 - ux) * s_out < 0:                                                           # inboard plate: vacuum port
            p = p.cut(cyl(P.vac_hose + 2.0, (x0 - 1, P.meter_y, P.meter_z - 50.0), (x1 + 1, P.meter_y, P.meter_z - 50.0)))
        out.append(p)
    return Part.makeCompound(out)


def shank(ux):
    """Centre shank 10 mm between the discs, welded to a cross tube O30 between the side plates."""
    s = box_span((ux - 5.0, ux + 5.0), (-1850.0, -1775.0), (DZ, CROSS[1] + 15.0))
    tube = cyl(30.0, (ux - P.plate_dx + P.plate_t / 2.0, CROSS[0], CROSS[1]), (ux + P.plate_dx - P.plate_t / 2.0, CROSS[0], CROSS[1]))
    hubs = [cyl(60.0, (ux + sx * 5.0, P.opener_y, DZ), (ux + sx * (P.disc_dx - 1.5), P.opener_y, DZ)) for sx in (-1, 1)]
    return fuse_all([s, tube] + hubs)


def discs(ux):
    return Part.makeCompound([cyl(P.disc_d, (ux + sx * (P.disc_dx - 1.5), P.opener_y, DZ), (ux + sx * (P.disc_dx + 1.5), P.opener_y, DZ))
                              for sx in (-1, 1)])


def gauge_wheels(ux):
    out = []
    for sx in (-1, 1):
        xi = ux + sx * (P.gauge_dx - P.gauge_w / 2.0)
        xo = ux + sx * (P.gauge_dx + P.gauge_w / 2.0)
        tyre = cyl(P.gauge_d, (xi, P.opener_y, GZ), (xo, P.opener_y, GZ)).cut(
            cyl(P.gauge_d - 60.0, (xi - sx, P.opener_y, GZ), (xo + sx, P.opener_y, GZ)))
        rim = cyl(P.gauge_d - 60.0, (xi, P.opener_y, GZ), (xo, P.opener_y, GZ)).cut(
            cyl(P.gauge_d - 120.0, (xi - sx, P.opener_y, GZ), (xo + sx, P.opener_y, GZ)))
        hub = cyl(60.0, (xi, P.opener_y, GZ), (xo, P.opener_y, GZ))
        web = cyl(P.gauge_d - 118.0, (ux + sx * P.gauge_dx - 3.0, P.opener_y, GZ), (ux + sx * P.gauge_dx + 3.0, P.opener_y, GZ))
        out.append(fuse_all([tyre, rim, hub, web]))
    return Part.makeCompound(out)


def gauge_stubs(ux):
    """Stub axles O20 from the side plates to the depth wheels (depth set by an eccentric on the plate)."""
    return Part.makeCompound([cyl(20.0, (ux + sx * (P.gauge_dx + P.gauge_w / 2.0 - 1.0), P.opener_y, GZ),
                                  (ux + sx * (P.plate_dx - P.plate_t / 2.0 + 1.0), P.opener_y, GZ)) for sx in (-1, 1)])


def press_arms(ux):
    pts = ((-1945.0, 215.0), (-1955.0, 170.0), (P.press_y - 15.0, PRESS_Z - 15.0), (P.press_y + 15.0, PRESS_Z + 15.0))
    out = [plate_yz(pts, x0, x1 - x0) for x0, x1 in _sides(ux, P.plate_dx - P.plate_t, P.plate_t)]
    return Part.makeCompound(out)


def press_wheel(ux):
    w = P.press_w
    tyre = cyl(P.press_d, (ux - w / 2.0, P.press_y, PRESS_Z), (ux + w / 2.0, P.press_y, PRESS_Z))
    axle = cyl(16.0, (ux - P.plate_dx + 1.5 * P.plate_t, P.press_y, PRESS_Z), (ux + P.plate_dx - 1.5 * P.plate_t, P.press_y, PRESS_Z))
    return tyre, axle


# ---------------------------------------------------------------------
# Metering, hopper, seed tube, sensor, stepper
# ---------------------------------------------------------------------
def meter(ux):
    h = cyl(P.meter_d, (ux - P.meter_w / 2.0, P.meter_y, P.meter_z), (ux + P.meter_w / 2.0, P.meter_y, P.meter_z))
    sx = math.copysign(1.0, ux)
    port = cyl(P.vac_hose, (ux - sx * P.meter_w / 2.0, P.meter_y, P.meter_z - 50.0),
               (ux - sx * (P.plate_dx - P.plate_t / 2.0 - 1.0), P.meter_y, P.meter_z - 50.0))
    shaft = cyl(20.0, (ux + sx * P.meter_w / 2.0, P.meter_y, P.meter_z), (ux + sx * (P.plate_dx + P.plate_t / 2.0), P.meter_y, P.meter_z))
    return fuse_all([h, port, shaft])


def stepper(ux):
    sx = math.copysign(1.0, ux)
    x0 = ux + sx * (P.plate_dx + P.plate_t / 2.0)
    m = P.nema17
    gear = cyl(36.0, (x0, P.meter_y, P.meter_z), (x0 + sx * P.gear17_len, P.meter_y, P.meter_z))
    xb = x0 + sx * P.gear17_len
    body = box_span(sorted((xb, xb + sx * P.nema17_len)), (P.meter_y - m / 2.0, P.meter_y + m / 2.0),
                    (P.meter_z - m / 2.0, P.meter_z + m / 2.0))
    return fuse_all([gear, body])


def hopper(ux):
    hx, hy, hz = P.hopper
    z0 = P.hopper_z0
    o = box_span((ux - hx / 2.0, ux + hx / 2.0), (P.hopper_y - hy / 2.0, P.hopper_y + hy / 2.0), (z0 + 5.0, z0 + hz))
    i = box_span((ux - hx / 2.0 + 3, ux + hx / 2.0 - 3), (P.hopper_y - hy / 2.0 + 3, P.hopper_y + hy / 2.0 - 3), (z0 + 8.0, z0 + hz + 1))
    s = o.cut(i)
    flange = box_span((ux - P.plate_dx - P.plate_t / 2.0, ux + P.plate_dx + P.plate_t / 2.0),
                      (P.hopper_y - hy / 2.0, P.hopper_y + hy / 2.0), (z0, z0 + 5.0))
    flange = flange.cut(cyl(40.0, (ux, P.hopper_y, z0 - 1), (ux, P.hopper_y, z0 + 9)))
    lid = box_span((ux - hx / 2.0 - 4, ux + hx / 2.0 + 4), (P.hopper_y - hy / 2.0 - 4, P.hopper_y + hy / 2.0 + 4),
                   (z0 + hz, z0 + hz + 4.0))
    neck = cyl(40.0, (ux, P.hopper_y, P.meter_z + P.meter_d / 2.0 - 8.0), (ux, P.hopper_y, z0)).cut(
        cyl(34.0, (ux, P.hopper_y, P.meter_z), (ux, P.hopper_y, z0 + 1)))
    return fuse_all([s, flange, lid, neck])


TUBE_A = (P.meter_y - 95.0, P.meter_z - 30.0)
TUBE_B = (-1915.0, 280.0)


def seed_tube(ux):
    a = V(ux, TUBE_A[0], TUBE_A[1])
    b = V(ux, TUBE_B[0], TUBE_B[1])
    d = b - a
    t = Part.makeCylinder(P.tube_d / 2.0, d.Length, a, d).cut(Part.makeCylinder(P.tube_d / 2.0 - 2.0, d.Length + 2, a - d * (1.0 / d.Length), d))
    return t


def seed_sensor(ux):
    a = V(ux, TUBE_A[0], TUBE_A[1])
    b = V(ux, TUBE_B[0], TUBE_B[1])
    m = a + (b - a) * 0.55
    sx, sy, sz = P.sensor
    s = box_span((ux - sx / 2.0, ux + sx / 2.0), (m.y - sy / 2.0, m.y + sy / 2.0), (m.z - sz / 2.0, m.z + sz / 2.0))
    return s.cut(Part.makeCylinder(P.tube_d / 2.0 + 0.5, 300.0, a, b - a))


def unit_names():
    return ("brackets", "links", "pins", "side_plates", "shank", "discs", "gauge_wheels", "gauge_stubs", "press_arms",
            "press_wheel", "press_axle", "meter", "stepper", "hopper", "seed_tube", "seed_sensor")


def unit(ux):
    """All parts of one seeding unit, as {name: shape}."""
    tyre, axle = press_wheel(ux)
    return {"brackets": brackets(ux), "links": links(ux), "pins": pins(ux), "side_plates": side_plates(ux),
            "shank": shank(ux), "discs": discs(ux), "gauge_wheels": gauge_wheels(ux), "gauge_stubs": gauge_stubs(ux),
            "press_arms": press_arms(ux), "press_wheel": tyre, "press_axle": axle, "meter": meter(ux),
            "stepper": stepper(ux), "hopper": hopper(ux), "seed_tube": seed_tube(ux), "seed_sensor": seed_sensor(ux)}


# ---------------------------------------------------------------------
# Vacuum blower and hoses
# ---------------------------------------------------------------------
FZ0 = P.tb_z[1]


def blower():
    d, h = P.fan
    x, y = P.fan_xy
    vol = cyl(d, (x, y, FZ0), (x, y, FZ0 + h))
    motor = cyl(70.0, (x, y, FZ0 + h), (x, y, FZ0 + h + 80.0))
    return fuse_all([vol, motor])


def vac_hoses():
    out = []
    x, y = P.fan_xy
    z = FZ0 + P.fan[1] / 2.0
    for ux in P.ROW_X:
        sx = math.copysign(1.0, ux)
        xp = ux - sx * (P.plate_dx + P.plate_t / 2.0)
        pts = [(sx * 30.0, y - P.fan[0] / 2.0 + 2.0, z), (sx * 30.0, -1500.0, z), (sx * 140.0, -1500.0, 640.0), (sx * 140.0, -1700.0, 640.0),
               (sx * 140.0, P.meter_y, P.meter_z - 50.0), (xp + sx * 1.0, P.meter_y, P.meter_z - 50.0)]
        out.append(TG.fuse_all([Part.makeCylinder(P.vac_hose / 2.0, (V(*b) - V(*a)).Length, V(*a), V(*b) - V(*a))
                                for a, b in zip(pts[:-1], pts[1:])] + [Part.makeSphere(P.vac_hose / 2.0, V(*p)) for p in pts[1:-1]]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Scene: seedbed with the 2 sown rows and seed markers (images)
# ---------------------------------------------------------------------
def seedbed(y0, y1):
    return box_span((-1800.0, 1800.0), (y0, y1), (-60.0, 0.0))


def furrows(y0, y1):
    return Part.makeCompound([box_span((ux - 15.0, ux + 15.0), (y0, y1), (-1.0, 1.5)) for ux in P.ROW_X])


def seed_flags(y0, y1):
    out = []
    for ux in P.ROW_X:
        y = y1
        while y > y0:
            out.append(Part.makeSphere(9.0, V(ux, y, 4.0)))
            y -= P.seed_spacing
    return Part.makeCompound(out)
