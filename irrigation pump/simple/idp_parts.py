"""Parts of the irrigation pump. Every function returns a Part shape in robot coordinates.
Bearers, base plate and their bolts come from the hydraulic power pack (hpu_parts)."""
import math

import Part
from FreeCAD import Vector as V

import idp_params as P
import hpu_parts as HP

box_span = HP.box_span
cyl = HP.cyl
fuse_all = HP.fuse_all
hose_path = HP.hose_path
bearers = HP.bearers
plate = HP.plate
bolts = HP.bolts


def cyl_x(d, yz, x0, x1):
    return cyl(d, (x0, yz[0], yz[1]), (x1, yz[0], yz[1]))


AX = (P.pump_y, P.pump_z)


# ---------------------------------------------------------------------
# Pump and motor
# ---------------------------------------------------------------------
def pump():
    d, (x0, x1) = P.casing
    body = cyl_x(d, AX, x0, x1)
    px, py, pz = P.prime
    xc = (x0 + x1) / 2.0
    ch = box_span((xc - px / 2.0, xc + px / 2.0), (P.pump_y - py / 2.0, P.pump_y + py / 2.0),
                  (P.pump_z + d / 2.0 - 20.0, P.pump_z + d / 2.0 + pz))
    eye = cyl(60.0, (xc, P.pump_y + d / 2.0 - 10.0, P.pump_z), (xc, P.pump_y + d / 2.0 + 25.0, P.pump_z))   # inlet, front
    outlet = cyl(60.0, (xc, P.pump_y - py / 2.0 + 30.0, P.pump_z + d / 2.0 + pz),
                 (xc, P.pump_y - py / 2.0 + 30.0, P.pump_z + d / 2.0 + pz + 25.0))
    feet = box_span((x0 + 10.0, x1 - 10.0), (P.pump_y - 60.0, P.pump_y + 60.0), (P.TOP, P.pump_z - d / 2.0 + 10.0))
    return fuse_all([body, ch, eye, outlet, feet])


def motor():
    d, (x0, x1) = P.motor
    body = cyl_x(d, AX, x0, x1)
    feet = box_span((x0 + 10.0, x1 - 10.0), (P.pump_y - 50.0, P.pump_y + 50.0), (P.TOP, P.pump_z - d / 2.0 + 10.0))
    return fuse_all([body, feet])


# ---------------------------------------------------------------------
# Reel
# ---------------------------------------------------------------------
RA = (P.reel_y, P.reel_z)


def reel_stand():
    """2 side plates 8 mm with the axle bearings, outside the flanges."""
    out = []
    half = 140.0                                    # feet stay on the base plate
    for x0 in (P.reel_x[0] - P.flange_t - P.side_t - 4.0, P.reel_x[1] + P.flange_t + 4.0):
        pts = [(P.reel_y - half, P.TOP), (P.reel_y + half, P.TOP), (P.reel_y + 40.0, P.reel_z + 30.0),
               (P.reel_y - 40.0, P.reel_z + 30.0)]
        w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
        pl = Part.Face(w).extrude(V(P.side_t, 0, 0))
        pl = fuse_all([pl, cyl_x(80.0, RA, x0, x0 + P.side_t)]).cut(cyl_x(P.axle_d + 1.0, RA, x0 - 1, x0 + P.side_t + 1))
        out.append(pl)
    return Part.makeCompound(out)


def reel():
    """Drum, flanges, hollow axle (with the rotary union on the pump side) and crank."""
    x0, x1 = P.reel_x
    drum = cyl_x(P.drum_d, RA, x0, x1).cut(cyl_x(P.drum_d - 2 * P.drum_t, RA, x0 - 1, x1 + 1))
    hub = [cyl_x(P.drum_d, RA, x, x + 3.0).cut(cyl_x(P.axle_d, RA, x - 1, x + 4)) for x in (x0, (x0 + x1) / 2.0)]
    fl = [cyl_x(P.flange_d, RA, x0 - P.flange_t, x0), cyl_x(P.flange_d, RA, x1, x1 + P.flange_t)]
    xe = x1 + P.flange_t + 4.0 + P.side_t + 20.0
    axle = cyl_x(P.axle_d, RA, x0 - P.flange_t - 4.0 - P.side_t - 5.0, xe)
    union = cyl_x(70.0, RA, xe, xe + 40.0)                              # rotary union, right end
    knob = cyl_x(30.0, (P.reel_y, P.reel_z + P.flange_d / 2.0 - 30.0), x0 - P.flange_t - 50.0, x0 - P.flange_t)   # crank knob
    return fuse_all([drum, axle, union, knob] + fl + hub)


def hose_wound():
    """The suction hose wound on the drum (3 layers, drawn as a ring)."""
    x0, x1 = P.reel_x
    layers = P.hose_layers
    return cyl_x(P.drum_d + 2 * layers * P.hose_d, RA, x0 + 1.0, x1 - 1.0).cut(cyl_x(P.drum_d, RA, x0, x1))


def strainer():
    x = P.reel_x[1] + P.flange_t + 4.0 + P.side_t
    y = P.reel_y - P.flange_d / 2.0 - 20.0          # behind the reel, clear of the suction pipe
    return cyl(P.strainer[0], (x + P.strainer[0] / 2.0, y, P.TOP + 20.0), (x + P.strainer[0] / 2.0, y, P.TOP + 20.0 + P.strainer[1]))


# ---------------------------------------------------------------------
# Pipes and coupling
# ---------------------------------------------------------------------
def pipe_points():
    """Suction: pump inlet (front) forward past the reel flange, across, back into the rotary union (right end).
    Discharge: from the priming chamber up and back to the Camlock coupling at the rear edge."""
    d, (cx0, cx1) = P.casing
    xc = (cx0 + cx1) / 2.0
    xu = P.reel_x[1] + P.flange_t + 4.0 + P.side_t + 20.0 + 40.0       # outer end of the rotary union
    yf = P.reel_y + P.flange_d / 2.0 + 35.0                             # in front of the reel flanges
    out_z = P.pump_z + d / 2.0 + P.prime[2] + 25.0
    oy = P.pump_y - P.prime[1] / 2.0 + 30.0
    return {"suction": [(xc, P.pump_y + d / 2.0 + 25.0, P.pump_z), (xc, yf, P.pump_z), (xu + 30.0, yf, P.pump_z),
                        (xu + 30.0, yf, P.reel_z), (xu + 30.0, P.reel_y, P.reel_z), (xu, P.reel_y, P.reel_z)],
            "discharge": [(xc, oy, out_z), (xc, oy, out_z + 40.0), (xc, H_REAR + 40.0, out_z + 40.0),
                          (xc, H_REAR, out_z + 40.0)]}


H_REAR = P.H.plate_y[0] - 30.0


def pipes():
    return Part.makeCompound([hose_path(p, P.hose_d) for p in pipe_points().values()])


def coupling():
    p = pipe_points()["discharge"][-1]
    return cyl(P.coupling_d, p, (p[0], p[1] - 60.0, p[2]))
