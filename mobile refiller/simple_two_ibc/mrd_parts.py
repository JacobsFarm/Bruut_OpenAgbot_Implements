"""Parts of the mobile refiller with two IBCs (robot coordinates of the lengthened robot).

- IBC, pump, suction hose, straps, corner guides: the shapes of ../simple/mrs_parts.py, moved in y per IBC.
- Bed: own cross tubes (bolted where the upper beams have holes) and side rails over both IBCs.
- Mast and arm: ../stationary/stc_parts.py with a mast spec per nozzle (A near, B far) and one for the antenna in
  the middle. Arm parts are drawn with the arm out (to the left, -x); the arm sub-Part rotates them about the mast.
- Hoses: two 1.5" hoses side by side, from each pump under the beams to the mast, up its outer face, and along the
  arm to the drop pipe of their own nozzle.
"""
import Part
from FreeCAD import Vector as V

import mrd_params as P
import mrs_params as S
import mrs_parts as MP
import stc_parts as SG
from mrs_parts import box_span, cyl_z, rtube, fuse_all, hose, bolt_down

MX, MY = P.mast_xy
BED_W, BED_H, BED_T = S.bed_tube


def moved(shape, dy):
    s = shape.copy()
    s.translate(V(0, dy, 0))
    return s


# ---------------------------------------------------------------------
# Mast specs (stc_parts): one per nozzle, one for the antenna (middle)
# ---------------------------------------------------------------------
def mast_spec(key):
    reach = P.antenna_reach if key == "mid" else P.reach[key]
    return SG.mast_spec(MX, MY, P.mast_z0, reach, nozzle_z=P.nozzle_tip_z, in_face="-x", in_z=None,
                        folds=(0.0, P.arm_fold))


M = {k: mast_spec(k) for k in ("A", "B", "mid")}


# ---------------------------------------------------------------------
# Bed
# ---------------------------------------------------------------------
def cross_ys():
    return sorted(set(P.bed_cross_y["A"] + P.bed_cross_y["B"] + (P.mast_cross_y,)))


def bed_cross_tubes():
    """60 x 40 x 3 cross tubes lying flat; bolted ones with a bolt hole below and an access hole on top."""
    z0, z1 = S.bed_z
    out = []
    for y in cross_ys():
        tube = rtube((-S.bed_cross_x, S.bed_cross_x), (y - BED_W / 2.0, y + BED_W / 2.0), S.bed_z, BED_T, "x")
        if P.grid_hole(y):
            holes = []
            for x in S.bed_bolt_x:
                holes.append(cyl_z(S.m10_hole, z0 - 1.0, z0 + BED_T + 1.0, x, y))
                holes.append(cyl_z(22.0, z1 - BED_T - 1.0, z1 + 1.0, x, y))
            tube = tube.cut(holes)
        out.append(tube)
    return Part.makeCompound(out)


def bed_side_rails():
    return Part.makeCompound([rtube((s * S.bed_side_x[0], s * S.bed_side_x[1]), P.bed_side_y, S.bed_z, BED_T, "y")
                              for s in (-1, 1)])


def bed_bolts():
    z_head = S.bed_z[0] + BED_T
    z_nut = S.robot_upper_beam_z[0]
    out = []
    for y in cross_ys():
        if not P.grid_hole(y):
            continue
        for x in S.bed_bolt_x:
            out.append(bolt_down(x, y, z_head, z_head - z_nut + 8.4 + 3.0))
            out.append(cyl_z(17.0, z_nut - 8.4, z_nut, x, y))
    return Part.makeCompound(out)


def corner_guides():
    return Part.makeCompound([moved(MP.corner_guides(), P.ibc_dy[k]) for k in P.LIQUIDS])


def lashing_eyes():
    return Part.makeCompound([moved(MP.lashing_eyes(), P.ibc_dy[k]) for k in P.LIQUIDS])


def mast_outrigger():
    """80 x 40 x 3 stub from the left side rail out under the mast (welded to the cross tube between the IBCs)."""
    m = S.mast_tube[0]
    return rtube(S.outrigger_x, (MY - m / 2.0, MY + m / 2.0), S.bed_z, BED_T, "x")


def mast_gussets():
    return moved(MP.mast_gussets(), MY - S.mast_xy[1])


# ---------------------------------------------------------------------
# IBC (per liquid) and pumps
# ---------------------------------------------------------------------
def ibc(liq):
    dy = P.ibc_dy[liq]
    return {"pallet": moved(MP.pallet(), dy), "bottle": moved(MP.bottle(), dy), "cage": moved(MP.cage(), dy),
            "valve": moved(MP.ibc_valve(), dy), "cap": moved(MP.ibc_cap(), dy)}


def ibc_straps(liq):
    return moved(MP.straps(), P.ibc_dy[liq]), moved(MP.ratchets(), P.ibc_dy[liq])


def pump(liq):
    dy = P.ibc_dy[liq]
    return {"pump": moved(MP.pump_body(), dy), "cradle": moved(MP.pump_cradle(), dy),
            "camlock": moved(MP.camlock_elbow(), dy), "suction": moved(MP.suction_hose(), dy)}


def pump_out(liq):
    x, y, z = MP.PUMP_OUT
    return (x, y + P.ibc_dy[liq], z)


# ---------------------------------------------------------------------
# Hoses: fixed part (pump -> under the beams -> up the outer face of the mast) and arm part (over the pivot, along
# the arm, down into the side inlet of the drop pipe)
# ---------------------------------------------------------------------
def mast_hose_y(liq):
    return MY + P.mast_hose_dy[liq]


def hose_fixed(liq):
    x, y, z = pump_out(liq)
    hz, hx, my = P.hose_under_z, P.mast_hose_x, mast_hose_y(liq)
    return hose([(x, y, z - 5.0), (x, y, hz), (x, my, hz), (hx, my, hz), (hx, my, P.mast_split_z)])


def hose_arm(liq):
    hx, my = P.mast_hose_x, mast_hose_y(liq)
    hz = P.arm_hose_z
    m = M[liq]
    nx, ny = SG.nozzle_xy(m)
    iz = SG._inlet_z(m)
    lane = MY + P.arm_lane_dy[liq]
    if liq == "A":
        pts = [(hx, my, P.mast_split_z), (hx, my, hz - 40.0), (hx - 30.0, lane, hz)]
        drop_y = MY + 80.0
    else:                               # B crosses over the arm and A, comes down outside A
        top = S.arm_z[1] + 45.0
        pts = [(hx, my, P.mast_split_z), (hx, my, top), (hx - 20.0, lane, top), (hx - 60.0, lane, hz)]
        drop_y = lane
    pts += [(nx + 80.0, lane, hz), (nx, drop_y, iz + 40.0), (nx, drop_y, iz), (nx, ny + 58.0, iz)]
    return hose(pts)


def mast_clamps():
    """Stand-off brackets with clamps that hold the two hoses on the outer face of the mast."""
    out = []
    for z in (1000.0, 1450.0):
        out.append(box_span((P.mast_hose_x - 30.0, MX - S.mast_tube[0] / 2.0), (MY - 65.0, MY + 65.0), (z, z + 30.0)))
    return Part.makeCompound(out)


def arm_saddles():
    """Saddles under the two hoses, welded to the side of the arm (one between mast and nozzle A, one between A
    and B)."""
    hz = P.arm_hose_z
    za = hz - P.hose_od / 2.0
    xs = (0.5 * (MX + P.nozzle_x["A"]), 0.5 * (P.nozzle_x["A"] + P.nozzle_x["B"]))
    y0 = MY + S.arm_tube[0] / 2.0
    y1 = MY + P.arm_lane_dy["B"] + P.hose_od / 2.0 + 10.0
    out = []
    for x in xs:
        out.append(box_span((x - 15.0, x + 15.0), (y0, y1), (za - 8.0, za)))
        out.append(box_span((x - 15.0, x + 15.0), (y1 - 6.0, y1), (za, za + 30.0)))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Mast and arm (from stc_parts)
# ---------------------------------------------------------------------
def mast():
    return SG.mast(M["B"])


def mast_top_plate():
    return SG.mast_top_plate(M["B"])


def pivot_pin():
    return SG.pivot_pin(M["B"])


def arm():
    return SG.arm(M["B"])


def lock_pin():
    return SG.lock_pin(M["B"])


def tip_plates():
    return Part.makeCompound([SG.tip_plate(M[k]) for k in P.LIQUIDS])


def drop_pipe(liq):
    return SG.drop_pipe(M[liq])


def nozzle(liq):
    return SG.nozzle(M[liq])


def antenna():
    return SG.antenna(M["mid"])


def nozzle_xy(liq, angle=0.0):
    """Nozzle axis in robot coordinates with the arm at 'angle' (0 = out to the left)."""
    import math
    a = math.radians(angle)
    r = P.reach[liq]
    return (MX - r * math.cos(a), MY - r * math.sin(a))


# ---------------------------------------------------------------------
# Fill bridge: two funnels over the gap between the IBCs (filled by the IBC trailer with its arm lifted)
# ---------------------------------------------------------------------
def bridge_plate():
    w, t, ln = P.bridge
    return box_span((-ln / 2.0, ln / 2.0), (P.fill_y - w / 2.0, P.fill_y + w / 2.0), (P.bridge_z0, P.bridge_z0 + t))


def _cone_r(z):
    rim, out, h = P.fill_funnel
    return out / 2.0 + (rim - out) / 2.0 * (z - P.fill_cone_z0) / h


def fill_funnel(liq):
    rim, out, h = P.fill_funnel
    x, y = P.fill_x[liq], P.fill_y
    z0 = P.fill_cone_z0
    cone = Part.makeCone(out / 2.0, rim / 2.0, h, V(x, y, z0))
    inner = Part.makeCone(out / 2.0 - 3.0, rim / 2.0 - 3.0, h + 0.02, V(x, y, z0 + 0.01))
    return cone.cut(inner)


def fill_support(liq):
    """Ring round the cone on two legs to the bridge plate."""
    x, y = P.fill_x[liq], P.fill_y
    z = P.fill_cone_z0 + 45.0
    r = _cone_r(z)
    ring = Part.makeCylinder(r + 14.0, 8.0, V(x, y, z)).cut(Part.makeCylinder(r, 10.0, V(x, y, z - 1.0)))
    legs = [cyl_z(16.0, P.bridge_z0 + P.bridge[1], z + 4.0, x + s * (r + 7.0), y) for s in (-1, 1)]
    return fuse_all([ring] + legs)


def fill_pipe(liq):
    """Funnel outlet down to an elbow, over the cage top to the bulkhead fitting in the top of its own IBC."""
    x, y = P.fill_x[liq], P.fill_y
    yf = P.fill_fitting_y[liq]
    z = P.fill_pipe_z
    top = P.ibc_top_bottle if hasattr(P, "ibc_top_bottle") else S.IBC_Z0 + S.pallet_h + S.bottle_h
    return hose([(x, y, P.fill_cone_z0 + 2.0), (x, y, z), (x, yf, z), (x, yf, top - 5.0)], od=P.fill_pipe[0])


def fill_fitting(liq):
    x, yf = P.fill_x[liq], P.fill_fitting_y[liq]
    top = S.IBC_Z0 + S.pallet_h + S.bottle_h
    return fuse_all([cyl_z(90.0, top - 2.0, top + 10.0, x, yf), cyl_z(64.0, top + 10.0, top + 30.0, x, yf)])
