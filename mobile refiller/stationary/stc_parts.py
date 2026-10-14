"""Parts shared by the three stationary refill stations: IBC (from the simple variant, in IBC-local coordinates), the
control box with the pump and the electronics, the mast with the swinging arm, drop pipe, nozzle and RTK antenna,
the status beacon, and carrier hardware (wheels, mudguards, jockey wheel, drop legs, tow eye, lights).

Local coordinates:
- IBC: origin = middle of the footprint at the underside of the pallet, 1200 along x, 1000 along y, valve on -x.
- Control box: origin = middle of the bottom (under the mounting rails), door on +y, suction port on -x (low),
  discharge port on +x (high).
- Mast and arm: in carrier coordinates, from a spec dict M (see mast_spec); arm parts are drawn with the arm out to
  the left (-x); the arm sub-Part in the build rotates them about the mast axis.
"""
import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import stc_params as P
import mrs_parts as MP
import mrs_calc as MC
from mrs_parts import (box_span, cyl_x, cyl_y, cyl_z, tube_z, fuse_all, rbox, rtube, hose, poly_xz,  # noqa: F401
                       ground_line, stream)

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Placement helpers (rotations about z only, in multiples of 90 deg in practice)
# ---------------------------------------------------------------------
def placement(x=0.0, y=0.0, z=0.0, rot=0.0):
    return App.Placement(V(x, y, z), App.Rotation(Z, rot))


def xform(pt, pl):
    """Point (tuple) from local to carrier coordinates."""
    v = pl.multVec(V(*pt))
    return (v.x, v.y, v.z)


def placed(shape, pl):
    s = shape.copy()
    s.transformShape(pl.toMatrix())
    return s


# ---------------------------------------------------------------------
# IBC (bought; shapes from simple/mrs_parts.py moved to IBC-local coordinates)
# ---------------------------------------------------------------------
_IBC = {}


def _local(shape):
    s = shape.copy()
    s.translate(V(*P.IBC_LOCAL))
    return s


def ibc_local():
    if not _IBC:
        _IBC.update({"pallet": _local(MP.pallet()), "bottle": _local(MP.bottle()), "cage": _local(MP.cage()),
                     "valve": _local(MP.ibc_valve()), "cap": _local(MP.ibc_cap()),
                     "inner": _local(MP.bottle_inner())})
    return _IBC


_LIQ = {}


def ibc_liquid_local(litres):
    key = round(litres * 2.0) / 2.0
    if key not in _LIQ:
        lvl = MC.level_for("ibc", key) - MP.P.IBC_Z0
        s = MP.liquid(ibc_local()["inner"], lvl)
        _LIQ[key] = s if s is not None else Part.Shape()
    return _LIQ[key]


def ibc_level_z(litres):
    """Liquid level above the IBC base (mm)."""
    return MC.level_for("ibc", litres) - MP.P.IBC_Z0


def camlock_elbow():
    """Camlock coupler on the valve spigot with a 90 degree elbow down (IBC local). Outlet at ELBOW_OUT."""
    z = P.valve_z
    return fuse_all([cyl_x(62.0, P.VALVE_END + 10.0, P.elbow_x, 0.0, z), Part.makeSphere(31.0, V(P.elbow_x, 0, z)),
                     cyl_z(62.0, z - 50.0, z, P.elbow_x, 0.0)])


ELBOW_OUT = (P.elbow_x, 0.0, P.valve_z - 45.0)
STRAP_O = MP.STRAP_X                            # 601: strap outside the cage
STRAP_POS = 300.0


def ibc_straps(axis="y", z_bottom=12.0):
    """Two ratchet straps over the IBC (local). axis 'y': straps run along y over the 1000 width (legs on the +-y
    faces, at x +-300); axis 'x': along x over the 1200 length (legs on the +-x faces, at y +-300).
    z_bottom: where the legs end (local z, may be below the IBC base to reach the carrier)."""
    t, w = P.strap_t, P.strap_w
    zt = MP.P.cage_top + MP.P.cage_bar / 2.0
    half_y = 0.5 * P.ibc_wid + 1.0
    out = []
    for c in (-STRAP_POS, STRAP_POS):
        cc = (c - w / 2.0, c + w / 2.0)
        if axis == "x":
            parts = [box_span((-STRAP_O - t, STRAP_O + t), cc, (zt, zt + t))]
            parts += [box_span((s * STRAP_O, s * (STRAP_O + t)), cc, (z_bottom, zt + t)) for s in (-1, 1)]
        else:
            parts = [box_span(cc, (-half_y - t, half_y + t), (zt, zt + t))]
            parts += [box_span(cc, (s * half_y, s * (half_y + t)), (z_bottom, zt + t)) for s in (-1, 1)]
        out.append(fuse_all(parts))
    return Part.makeCompound(out)


def ibc_ratchets(axis="y", z=410.0):
    rx, rz, ry = P.ratchet
    half_y = 0.5 * P.ibc_wid + 1.0 + P.strap_t
    out = []
    for c in (-STRAP_POS, STRAP_POS):
        if axis == "x":
            out.append(box_span((STRAP_O + P.strap_t, STRAP_O + P.strap_t + rx), (c - ry / 2.0, c + ry / 2.0),
                                (z, z + rz)))
        else:
            out.append(box_span((c - ry / 2.0, c + ry / 2.0), (half_y, half_y + rx), (z, z + rz)))
    return Part.makeCompound(out)


def corner_guides(x0, x1, y0, y1, z, leg=50.0, t=5.0, h=140.0):
    """Angle 50 x 5 outside the four corners of the rectangle (carrier coordinates)."""
    zz = (z, z + h)
    out = []
    for sx, xe in ((-1, x0), (1, x1)):
        for sy, ye in ((-1, y0), (1, y1)):
            a = box_span((xe - sx * leg, xe + sx * t), (ye, ye + sy * t), zz)
            b = box_span((xe, xe + sx * t), (ye - sy * leg, ye + sy * t), zz)
            out.append(fuse_all([a, b]))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Control box (local): enclosure, door, roof, contents
# ---------------------------------------------------------------------
BW, BD, BH = P.box
FZ = P.box_foot[1]                              # 20: shell bottom
FLOOR = FZ + P.box_wall                         # 22: inside floor
PY, PZ = P.pump_axis


def box_rails():
    w, h = P.box_foot
    return Part.makeCompound([rtube((-BW / 2.0, BW / 2.0), (y - w / 2.0, y + w / 2.0), (0.0, h), 2.0, "x")
                              for y in (-BD / 2.0 + 40.0, BD / 2.0 - 40.0)])


def box_shell():
    t = P.box_wall
    outer = box_span((-BW / 2.0, BW / 2.0), (-BD / 2.0, BD / 2.0), (FZ, BH))
    inner = box_span((-BW / 2.0 + t, BW / 2.0 - t), (-BD / 2.0 + t, BD / 2.0 - t), (FZ + t, BH - t))
    holes = [cyl_x(52.0, -BW / 2.0 - 1.0, -BW / 2.0 + t + 1.0, PY, PZ),
             cyl_x(52.0, BW / 2.0 - t - 1.0, BW / 2.0 + 1.0, PY, P.discharge_z)]
    return outer.cut(inner).cut(holes)


def box_roof():
    o, t = P.box_roof
    return box_span((-BW / 2.0 - o, BW / 2.0 + o), (-BD / 2.0 - o, BD / 2.0 + o), (BH, BH + t))


DOOR_X = (-BW / 2.0 + P.box_door_inset, BW / 2.0 - P.box_door_inset)
DOOR_Z = (FZ + P.box_door_inset, BH - P.box_door_inset)
DOOR_Y = (BD / 2.0, BD / 2.0 + 2.0)


def box_door():
    """Door with hinges (left) and a lock handle (right)."""
    door = box_span(DOOR_X, DOOR_Y, DOOR_Z)
    hinges = [cyl_z(12.0, z - 30.0, z + 30.0, DOOR_X[0] - 6.0, DOOR_Y[1] + 4.0) for z in (DOOR_Z[0] + 60.0,
                                                                                          DOOR_Z[1] - 60.0)]
    zc = 0.5 * (DOOR_Z[0] + DOOR_Z[1])
    handle = fuse_all([cyl_y(40.0, DOOR_Y[1], DOOR_Y[1] + 12.0, DOOR_X[1] - 50.0, zc),
                       box_span((DOOR_X[1] - 58.0, DOOR_X[1] - 42.0), (DOOR_Y[1] + 12.0, DOOR_Y[1] + 30.0),
                                (zc - 70.0, zc + 10.0))])
    return fuse_all([door] + hinges + [handle])


def estop():
    """Emergency stop on the door: yellow base and red mushroom (two shapes)."""
    d, h = P.estop
    x, z = DOOR_X[1] - 80.0, DOOR_Z[1] - 70.0
    base = box_span((x - 40.0, x + 40.0), (DOOR_Y[1], DOOR_Y[1] + 35.0), (z - 40.0, z + 40.0))
    knob = fuse_all([cyl_y(24.0, DOOR_Y[1] + 35.0, DOOR_Y[1] + 50.0, x, z),
                     cyl_y(d, DOOR_Y[1] + 50.0, DOOR_Y[1] + 35.0 + h, x, z)])
    return base, knob


def box_glands():
    """Cable glands in the bottom (antenna, beacon, charging socket) and the bulkhead fittings of the ports."""
    g = [cyl_z(P.gland_d, FZ - 12.0, FZ, x, -60.0) for x in (-120.0, -60.0, 0.0)]
    t = P.box_wall
    g.append(cyl_x(70.0, -BW / 2.0 - 8.0, -BW / 2.0, PY, PZ).cut(cyl_x(40.0, -BW / 2.0 - 9, -BW / 2.0 + 1, PY, PZ)))
    g.append(cyl_x(70.0, BW / 2.0, BW / 2.0 + 8.0, PY, P.discharge_z).cut(
        cyl_x(40.0, BW / 2.0 - 1, BW / 2.0 + 9, PY, P.discharge_z)))
    return fuse_all(g) if t else None


def pump():
    """24 V centrifugal transfer pump 1.5": motor (fins), head, axial inlet to the suction port, outlet up."""
    motor = cyl_x(P.pump_motor_d, P.pump_motor_x[0], P.pump_motor_x[1], PY, PZ)
    fins = cyl_x(P.pump_motor_d + 8.0, P.pump_motor_x[0] + 30.0, P.pump_motor_x[1] - 30.0, PY, PZ).cut(motor)
    head = cyl_x(P.pump_head_d, P.pump_head_x[0], P.pump_head_x[1], PY, PZ)
    inlet = cyl_x(48.0, -BW / 2.0 - P.port_len, P.pump_head_x[0] + 5.0, PY, PZ)
    outlet = cyl_z(48.0, PZ, P.discharge_z, P.pump_outlet_x, PY)
    cbox = box_span((-120.0, -40.0), (PY - 35.0, PY + 35.0), (PZ + 45.0, PZ + 72.0))
    return fuse_all([motor, fins, head, inlet, outlet, cbox])


def pump_feet():
    f_head = box_span((P.pump_head_x[0] + 10.0, P.pump_head_x[1] - 10.0), (PY - 40.0, PY + 40.0),
                      (FLOOR, PZ - P.pump_head_d / 2.0))
    f_motor = box_span((-110.0, -20.0), (PY - 35.0, PY + 35.0), (FLOOR, PZ - P.pump_motor_d / 2.0 - 4.0))
    return fuse_all([f_head, f_motor])


def discharge_line():
    """Elbow on the pump outlet, flow meter, motorised ball valve, pipe to the discharge port."""
    z = P.discharge_z
    x0 = P.pump_outlet_x
    parts = [Part.makeSphere(24.0, V(x0, PY, z)), cyl_x(48.0, x0, BW / 2.0 + P.port_len, PY, z)]
    return fuse_all(parts)


def flow_meter():
    x0, x1 = P.flowmeter_x
    return fuse_all([cyl_x(P.flowmeter_d, x0, x1, PY, P.discharge_z),
                     box_span((x0 + 20.0, x1 - 20.0), (PY - 25.0, PY + 25.0),
                              (P.discharge_z + 30.0, P.discharge_z + 60.0))])


def motor_valve():
    x = P.motor_valve_x
    z = P.discharge_z
    return fuse_all([cyl_x(64.0, x - 35.0, x + 35.0, PY, z), cyl_z(20.0, z + 30.0, z + 45.0, x, PY),
                     box_span((x - 40.0, x + 40.0), (PY - 35.0, PY + 35.0), (z + 45.0, z + 110.0))])


def battery():
    (x0, x1), (y0, y1), (z0, z1) = P.battery
    z0 = max(z0, FLOOR)
    body = box_span((x0, x1), (y0, y1), (z0, z0 + (P.battery[2][1] - P.battery[2][0])))
    zt = body.BoundBox.ZMax
    poles = [cyl_z(18.0, zt, zt + 15.0, x, 0.5 * (y0 + y1)) for x in (x0 + 40.0, x1 - 40.0)]
    return fuse_all([body] + poles)


def din_plate():
    return box_span(*P.din_plate)


def din_modules():
    y0 = P.din_plate[1][1]
    return Part.makeCompound([box_span((x0, x1), (y0, y0 + d), (z0, z1)) for _, x0, x1, d, z0, z1 in P.din_modules])


SUCTION_PORT = P.SUCTION_PORT
DISCHARGE_PORT = P.DISCHARGE_PORT


# ---------------------------------------------------------------------
# Mast and arm (carrier coordinates), from a spec dict
# ---------------------------------------------------------------------
def mast_spec(x, y, z0, reach, tube=None, arm_z=None, nozzle_z=None, in_face="-y", in_z=None, folds=(0, 90, 180)):
    """x, y: mast axis; z0: mast foot; reach: mast axis -> nozzle; in_face / in_z: lower hose window."""
    tube = P.mast_tube if tube is None else tube
    arm_z = P.arm_z if arm_z is None else arm_z
    return {"x": x, "y": y, "z0": z0, "z1": arm_z[0] - 15.0, "tube": tube, "reach": reach,
            "arm_z": arm_z, "nozzle_z": P.nozzle_tip_z if nozzle_z is None else nozzle_z, "in_face": in_face,
            "in_z": in_z, "folds": folds,
            "lock_r": max(P.lock_r, tube[0] / 2.0 + 15.0), "plate": max(P.top_plate[0], tube[0] + 50.0)}


def _top_z(M):
    return (M["z1"], M["z1"] + P.top_plate[1])


def _sleeve_z(M):
    z = _top_z(M)[1]
    return (z, z + 70.0)


def nozzle_xy(M):
    return (M["x"] - M["reach"], M["y"])


def _face_vec(face):
    return {"-x": (-1, 0), "+x": (1, 0), "-y": (0, -1), "+y": (0, 1)}[face]


def mast_top_window(M):
    return (M["arm_z"][0] - 115.0, M["arm_z"][0] - 35.0)


def mast(M):
    m, t = M["tube"]
    mx, my = M["x"], M["y"]
    tube = rtube((mx - m / 2.0, mx + m / 2.0), (my - m / 2.0, my + m / 2.0), (M["z0"], M["z1"]), t, "z")
    w = P.mast_window
    z0, z1 = mast_top_window(M)
    cuts = [box_span((mx - m / 2.0 - 1.0, mx - m / 2.0 + t + 1.0), (my - w / 2.0, my + w / 2.0), (z0, z1))]
    if M["in_z"] is not None:
        fx, fy = _face_vec(M["in_face"])
        zi = M["in_z"]
        if fx:
            xs = (mx + fx * (m / 2.0 + 1.0), mx + fx * (m / 2.0 - t - 1.0))
            cuts.append(box_span(xs, (my - w / 2.0, my + w / 2.0), (zi - 40.0, zi + 40.0)))
        else:
            ys = (my + fy * (m / 2.0 + 1.0), my + fy * (m / 2.0 - t - 1.0))
            cuts.append(box_span((mx - w / 2.0, mx + w / 2.0), ys, (zi - 40.0, zi + 40.0)))
    return tube.cut(cuts)


def lock_holes(M):
    out = []
    for a in M["folds"]:
        r = math.radians(a)
        out.append((M["x"] - M["lock_r"] * math.sin(r), M["y"] + M["lock_r"] * math.cos(r)))
    return out


def lock_hole0(M):
    """Lock-pin hole of the arm itself (the arm is drawn at 0 deg)."""
    return (M["x"], M["y"] + M["lock_r"])


def mast_top_plate(M):
    s = M["plate"] / 2.0
    tz = _top_z(M)
    plate = box_span((M["x"] - s, M["x"] + s), (M["y"] - s, M["y"] + s), tz)
    holes = [cyl_z(13.0, tz[0] - 1, tz[1] + 1, x, y) for x, y in lock_holes(M)]
    holes.append(cyl_z(P.pivot_pin[0], tz[0] - 1, tz[1] + 1, M["x"], M["y"]))
    return plate.cut(holes)


def pivot_pin(M):
    d, ln = P.pivot_pin
    tz, sz = _top_z(M), _sleeve_z(M)
    pin = cyl_z(d, tz[0], tz[1] + ln, M["x"], M["y"])
    washer = cyl_z(44.0, sz[1], sz[1] + 4.0, M["x"], M["y"])
    clip = cyl_y(4.0, M["y"] - 22.0, M["y"] + 22.0, M["x"], sz[1] + 12.0)
    return fuse_all([pin, washer, clip])


def arm(M):
    """60 x 60 x 3 arm welded to a boss on the pivot pin, with the lock-pin tab (drawn out to the left)."""
    b, t = P.arm_tube
    mx, my = M["x"], M["y"]
    sz = _sleeve_z(M)
    nx, _ = nozzle_xy(M)
    tip_x = nx - P.arm_tip
    boss = cyl_z(P.arm_sleeve[0], sz[0], sz[1], mx, my).cut(cyl_z(P.pivot_pin[0] + 1.0, sz[0] - 1, sz[1] + 1, mx, my))
    x_root = mx - math.sqrt((P.arm_sleeve[0] / 2.0) ** 2 - (b / 2.0) ** 2) + 2.0
    tube = rtube((x_root, tip_x), (my - b / 2.0, my + b / 2.0), M["arm_z"], t, "x")
    cap = box_span((tip_x, tip_x + t), (my - b / 2.0, my + b / 2.0), M["arm_z"])
    lx, ly = lock_hole0(M)
    tab =box_span((lx - 15.0, lx + 15.0), (my + P.arm_sleeve[0] / 2.0 - 3.0, ly + 15.0), (sz[0], sz[0] + 8.0))
    return fuse_all([boss, tube, cap, tab]).cut(cyl_z(13.0, sz[0] - 1, sz[0] + 9, lx, ly))


def lock_pin(M):
    lx, ly = lock_hole0(M)
    tz, sz = _top_z(M), _sleeve_z(M)
    return fuse_all([cyl_z(12.0, tz[0] - 20.0, sz[0] + 25.0, lx, ly), cyl_x(10.0, lx - 20.0, lx + 20.0, ly, sz[0] + 25.0)])


def _drop_top(M):
    return M["arm_z"][0] - 10.0


def tip_plate(M):
    nx, ny = nozzle_xy(M)
    return box_span((nx - P.arm_tip, nx + 40.0), (ny - 40.0, ny + 40.0), (_drop_top(M), M["arm_z"][0]))


def _inlet_z(M):
    return _drop_top(M) - 40.0


def drop_pipe(M):
    d, w = P.drop_pipe
    nx, ny = nozzle_xy(M)
    z0 = M["nozzle_z"] + P.nozzle[1] + P.nozzle[2]
    top = _drop_top(M)
    pipe = tube_z(d, w, z0, top, nx, ny)
    flange = cyl_z(80.0, top - 8.0, top, nx, ny).cut(cyl_z(d - 2 * w, 0, 5000, nx, ny))
    inlet = cyl_y(40.0, ny + d / 2.0 - 3.0, ny + 60.0, nx, _inlet_z(M)).cut(cyl_z(d - 2 * w, 0, 5000, nx, ny))
    return fuse_all([pipe, flange, inlet])


def nozzle(M):
    d, h, c = P.nozzle
    nx, ny = nozzle_xy(M)
    z0 = M["nozzle_z"]
    return fuse_all([cyl_z(d, z0 + c, z0 + c + h, nx, ny), Part.makeCone(12.5, 20.0, c, V(nx, ny, z0), Z)])


def antenna(M):
    nx, ny = nozzle_xy(M)
    z0 = M["arm_z"][1]
    stem = cyl_z(P.ant_stem[0], z0, z0 + P.ant_stem[1], nx, ny)
    z1 = z0 + P.ant_stem[1]
    dome = cyl_z(P.ant_dome[0], z1, z1 + P.ant_dome[1] * 0.6, nx, ny)
    top = Part.makeSphere(P.ant_dome[0] / 2.0, V(nx, ny, z1 + P.ant_dome[1] * 0.6)).common(
        box_span((nx - 80, nx + 80), (ny - 80, ny + 80), (z1 + P.ant_dome[1] * 0.6, z1 + P.ant_dome[1])))
    return fuse_all([stem, dome, top])


def antenna_top(M):
    return M["arm_z"][1] + P.ant_stem[1] + P.ant_dome[1]


def window_out(M):
    z0, z1 = mast_top_window(M)
    return (M["x"] - M["tube"][0] / 2.0 - 45.0, M["y"], 0.5 * (z0 + z1))


def arm_hose(M):
    """From the top window of the mast (flexible loop over the pivot) along the arm to the side inlet of the drop pipe."""
    nx, ny = nozzle_xy(M)
    wo = window_out(M)
    hy = M["y"] + P.arm_tube[0] / 2.0 + P.hose_od / 2.0 + 8.0
    hz = 0.5 * (M["arm_z"][0] + M["arm_z"][1])
    iz = _inlet_z(M)
    pts = [wo, (wo[0] - 15.0, hy, wo[2] + 30.0), (wo[0] - 55.0, hy, hz), (nx + 80.0, hy, hz),
           (nx, hy + 20.0, iz + 45.0), (nx, hy + 20.0, iz), (nx, ny + 58.0, iz)]
    return hose(pts)


def mast_in_points(M):
    """Hose inside the mast: from outside the lower window up to the top window and out (carrier coordinates)."""
    fx, fy = _face_vec(M["in_face"])
    m = M["tube"][0]
    zi = M["in_z"]
    wo = window_out(M)
    return [(M["x"] + fx * (m / 2.0 + 45.0), M["y"] + fy * (m / 2.0 + 45.0), zi), (M["x"], M["y"], zi),
            (M["x"], M["y"], wo[2]), wo]


def mast_gussets(M, z_base, faces=("+x", "-x"), h=220.0, l=None):
    """Triangular gussets 10 mm from the mast to the plate it stands on (z_base), on the given faces."""
    m = M["tube"][0]
    l = h * 0.6 if l is None else l
    t = P.gusset_t
    out = []
    for face in faces:
        fx, fy = _face_vec(face)
        if fx:
            x0 = M["x"] + fx * m / 2.0
            pts = [(x0, z_base), (x0 + fx * l, z_base), (x0, z_base + h)]
            out.append(poly_xz(pts, M["y"] - t / 2.0, t))
        else:
            y0 = M["y"] + fy * m / 2.0
            g = poly_xz([(0.0, z_base), (fy * l, z_base), (0.0, z_base + h)], -t / 2.0, t)
            g.rotate(V(0, 0, 0), Z, 90.0)       # x -> y
            g.translate(V(M["x"], y0, 0))
            out.append(g)
    return Part.makeCompound(out)


def beacon(x, y, z, face="+x", m=80.0):
    """Status beacon on a bracket beside the mast face: bracket, green / amber / red segments (4 shapes)."""
    fx, fy = _face_vec(face)
    d, h = P.beacon
    cx, cy = x + fx * (m / 2.0 + 60.0), y + fy * (m / 2.0 + 60.0)
    bx = (min(x + fx * m / 2.0, cx), max(x + fx * m / 2.0, cx)) if fx else (cx - 20.0, cx + 20.0)
    by = (min(y + fy * m / 2.0, cy), max(y + fy * m / 2.0, cy)) if fy else (cy - 20.0, cy + 20.0)
    bracket = fuse_all([box_span(bx, by, (z - 6.0, z)), cyl_z(d + 10.0, z, z + 20.0, cx, cy)])
    seg = (h - 20.0) / 3.0
    lamps = [cyl_z(d, z + 20.0 + i * seg, z + 20.0 + (i + 1) * seg - 2.0, cx, cy) for i in range(3)]
    return bracket, lamps[0], lamps[1], lamps[2]


# ---------------------------------------------------------------------
# Carrier hardware
# ---------------------------------------------------------------------
def tyre(xc, yc, zc, d, w, rim_d):
    t = cyl_x(d, xc - w / 2.0, xc + w / 2.0, yc, zc)
    try:
        t = t.makeFillet(min(0.3 * w, 0.2 * (d - rim_d)), t.Edges)
    except Exception:
        pass
    return t.cut(cyl_x(rim_d, xc - w, xc + w, yc, zc))


def rim(xc, yc, zc, w, rim_d, side=1):
    """Steel rim with a dished centre (side = +1: hub on the +x side of the tyre middle, i.e. the inner side for
    a left wheel)."""
    wr = w - 30.0
    outer = cyl_x(rim_d, xc - wr / 2.0, xc + wr / 2.0, yc, zc).cut(cyl_x(rim_d - 16.0, xc - wr, xc + wr, yc, zc))
    disc = cyl_x(rim_d - 10.0, xc + side * 10.0 - 4.0, xc + side * 10.0 + 4.0, yc, zc)
    hub = cyl_x(0.35 * rim_d, xc - side * 25.0, xc + side * 25.0, yc, zc)
    return fuse_all([outer, disc, hub])


def mudguard(xc, yc, zc, r, w, a0=15.0, a1=165.0, t=3.0):
    """Mudguard sheet over a wheel (axis along x): a ring segment from angle a0 to a1 measured from +y."""
    ring = cyl_x(2 * (r + t), xc - w / 2.0, xc + w / 2.0, yc, zc).cut(cyl_x(2 * r, xc - w, xc + w, yc, zc))
    pts = [V(xc - w, yc, zc)]
    for a in range(int(a0), int(a1) + 1, 15):
        ra = math.radians(a)
        pts.append(V(xc - w, yc + 2 * r * math.cos(ra), zc + 2 * r * math.sin(ra)))
    pts.append(V(xc - w, yc, zc))
    wedge = Part.Face(Part.makePolygon(pts)).extrude(V(2 * w, 0, 0))
    return ring.common(wedge)


def jockey_wheel(x, y, z_clamp, wheel_d=200.0, wheel_w=70.0):
    """Jockey wheel (down): tube 60 with a crank on top, fork and wheel on the ground; clamp at z_clamp."""
    r = wheel_d / 2.0
    z_axle = r
    z_fork = z_axle + r + 15.0                  # fork bridge above the wheel
    tube = cyl_z(60.0, z_fork + 70.0, z_clamp + 260.0, x, y)
    inner = cyl_z(48.0, z_fork + 10.0, z_fork + 70.0, x, y)
    sides = [box_span((x + s * (wheel_w / 2.0 + 4.0), x + s * (wheel_w / 2.0 + 12.0)), (y - 25.0, y + 25.0),
                      (z_axle - 10.0, z_fork + 10.0)) for s in (-1, 1)]
    bridge = box_span((x - wheel_w / 2.0 - 12.0, x + wheel_w / 2.0 + 12.0), (y - 25.0, y + 25.0),
                      (z_fork, z_fork + 10.0))
    crank = fuse_all([box_span((x - 8.0, x + 8.0), (y, y + 160.0), (z_clamp + 260.0, z_clamp + 275.0)),
                      cyl_z(25.0, z_clamp + 275.0, z_clamp + 375.0, x, y + 150.0)])
    pin = cyl_x(16.0, x - wheel_w / 2.0 - 12.0, x + wheel_w / 2.0 + 12.0, y, z_axle)
    wheel = cyl_x(wheel_d, x - wheel_w / 2.0, x + wheel_w / 2.0, y, z_axle).cut(
        cyl_x(17.0, x - wheel_w, x + wheel_w, y, z_axle))
    return fuse_all([tube, inner] + sides + [bridge, crank, pin]), wheel


def drop_leg(x, y, z_top, sleeve=60.0, leg=50.0, foot=(150.0, 10.0), sleeve_len=250.0):
    """Drop-down parking leg: sleeve welded to the frame (top at z_top), inner leg down to a foot plate on the
    ground, pin."""
    sl = rtube((x - sleeve / 2.0, x + sleeve / 2.0), (y - sleeve / 2.0, y + sleeve / 2.0),
               (z_top - sleeve_len, z_top), 4.0, "z")
    inner = rtube((x - leg / 2.0, x + leg / 2.0), (y - leg / 2.0, y + leg / 2.0), (foot[1], z_top - 20.0), 4.0, "z")
    pl = box_span((x - foot[0] / 2.0, x + foot[0] / 2.0), (y - foot[0] / 2.0, y + foot[0] / 2.0), (0.0, foot[1]))
    pin = cyl_x(16.0, x - sleeve / 2.0 - 30.0, x + sleeve / 2.0 + 30.0, y, z_top - sleeve_len + 60.0)
    return fuse_all([sl]), fuse_all([inner, pl]), pin


def tow_eye(x, y, z, l=200.0, d_ring=40.0):
    """Tow eye (DIN 74054, 40 mm): ring plate with a shank towards -y."""
    ring = cyl_z(110.0, z - 15.0, z + 15.0, x, y).cut(cyl_z(d_ring, z - 20.0, z + 20.0, x, y))
    shank = box_span((x - 30.0, x + 30.0), (y - l, y - 45.0), (z - 30.0, z + 30.0))
    return fuse_all([ring, shank])


def light_box(x, y_face, z, w=300.0, h=130.0, d=60.0, n=2, facing=-1):
    """Rear light cluster on a face at y_face, pointing to facing (-1 = rearwards): housing and lenses."""
    y0, y1 = sorted((y_face, y_face + facing * d))
    housing = box_span((x - w / 2.0, x + w / 2.0), (y0, y1), (z - h / 2.0, z + h / 2.0))
    lens_y = y_face + facing * d
    lenses = [cyl_y(80.0, lens_y, lens_y + facing * 6.0, x + (i - (n - 1) / 2.0) * 110.0, z) for i in range(n)]
    return housing, fuse_all(lenses)


def plate_tube_y(x0, x1, y0, y1, z0, z1, t=4.0):
    return rtube((x0, x1), (y0, y1), (z0, z1), t, "y")


def plate_tube_x(x0, x1, y0, y1, z0, z1, t=4.0):
    return rtube((x0, x1), (y0, y1), (z0, z1), t, "x")


def beam_between(p0, p1, b=100.0, h=50.0, t=4.0, z_mid=None):
    """Rectangular tube b (horizontal) x h (vertical) between two points in the x-y plane at height z_mid (centre)."""
    (x0, y0), (x1, y1) = p0, p1
    ln = math.hypot(x1 - x0, y1 - y0)
    tube = rtube((0.0, ln), (-b / 2.0, b / 2.0), (z_mid - h / 2.0, z_mid + h / 2.0), t, "x")
    tube.rotate(V(0, 0, 0), Z, math.degrees(math.atan2(y1 - y0, x1 - x0)))
    tube.translate(V(x0, y0, 0))
    return tube


def strut(p0, p1, d=50.0):
    """Round tube between two 3D points."""
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(d / 2.0, (b - a).Length, a, b - a).cut(
        Part.makeCylinder(d / 2.0 - 3.0, (b - a).Length + 2.0, a - (b - a).normalize(), b - a))
