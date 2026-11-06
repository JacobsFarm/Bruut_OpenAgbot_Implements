"""Mobile refiller, simple with two IBCs (two liquids) - parameters.

The simple refiller (../simple, one IBC on a standard Bruut) for the precision applicator V4, which carries two
liquids (A and B) in two work tanks with a funnel each, 455 mm apart. The robot frame is lengthened: wheelbase
2200 instead of 1000 (upper beams 2500 instead of 1300), so two standard 1000 l IBCs stand one behind the other on
one bed: IBC A (blue) in front, IBC B (orange) behind. Each IBC has its own pump under it. Both discharge hoses run
side by side up the outer face of the mast and along the arm to two drop pipes with a drip-stop nozzle each, 455 mm
apart on the arm: nozzle A over funnel A and nozzle B over funnel B of the working robot in one stop.

Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm. Origin = centre of the
robot. The IBC, pump and bed shapes come from ../simple (mrs_parts), moved in y; the mast and arm from
../stationary/stc_parts (a mast spec per nozzle).
"""
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
REFILLER = os.path.dirname(FOLDER)
ROOT = os.path.dirname(REFILLER)
SIMPLE = os.path.join(REFILLER, "simple")
STATIONARY = os.path.join(REFILLER, "stationary")
CMB4 = os.path.join(ROOT, "liquid fertilizer applicator", "precision_applicator", "combined_v4")
for _f in (SIMPLE, STATIONARY):
    if _f not in sys.path:
        sys.path.append(_f)

import mrs_params as S      # noqa: E402  simple variant: IBC, pump, bed tube, arm (single source of truth)

# ---------------------------------------------------------------------
# Lengthened robot (agbots/agbot design with these parameters changed; built by build_mrd.build_robot)
# ---------------------------------------------------------------------
ROBOT_OVERRIDE = {
    "chassis_length": 2200,         # wheel centres y +-1100 (standard 1000)
    "chassis_length_max": 2200,     # grid holes in the upper beams up to |y| 1175
    "beam_length_2": 2500,          # upper beams (y direction) 2500 long (standard 1300)
}
wheelbase = float(ROBOT_OVERRIDE["chassis_length"])
axle_y = wheelbase / 2.0
wheel_x = S.robot_wheel_x           # 375
tire_d = S.robot_tire_d
robot_front = axle_y + tire_d / 2.0                 # 1315: front of the front tyres
stepper_plate_y = axle_y - 95.0                     # 1005: front stepper-motor plates start here
upper_beam_z = S.robot_upper_beam_z
upper_beam_x = S.robot_upper_beam_x
robot_kg = S.robot_kg + 4 * 1.2 * 2.4               # + 4 x 1.2 m of 40 x 40 x 2 upper beam: 173 kg (estimated)
frame_bolt_y = (axle_y - 75.0, axle_y + 75.0)       # wheel-unit bolts stick up through the upper beams here


def grid_hole(y):
    """Upper-beam vertical M10 holes: |y| = 275, 325 ... 1175 (none in the middle)."""
    a = abs(y)
    return 275.0 - 1e-6 <= a <= 1175.0 + 1e-6 and abs((a - 275.0) / 50.0 - round((a - 275.0) / 50.0)) < 1e-6


# ---------------------------------------------------------------------
# Two IBCs on one bed: shift in y of the IBC of ../simple (that one spans y -620 .. 380)
# ---------------------------------------------------------------------
LIQUIDS = ("A", "B")
ibc_dy = {"A": 600.0, "B": -500.0}   # A: y -20 .. 980 (25 mm behind the front stepper plates), B: y -1120 .. -120
liquid_density = S.liquid_density
ibc_nominal_l = S.ibc_nominal_l
ibc_kg = sum(S.ibc_kg.values())


def ibc_y(liq):
    return (S.ibc_y[0] + ibc_dy[liq], S.ibc_y[1] + ibc_dy[liq])


def ibc_cy(liq):
    return S.IBC_CY + ibc_dy[liq]


IBC_Z0 = S.IBC_Z0                    # 739: IBCs on the bed
IBC_TOP = S.IBC_TOP

# Bed: the 4 cross tubes of ../simple per IBC, moved with it. Bolted where the upper beams have a hole, welded to the
# side rails elsewhere. The rear tube of IBC B moves from y -1025 to -975: the wheel-unit bolts stick up at -1025.
bed_cross_y = {"A": (75.0, 325.0, 925.0, 600.0), "B": (-975.0, -775.0, -175.0, -500.0)}
bed_side_y = (ibc_y("B")[0] - 5.0, ibc_y("A")[1] + 5.0)
mast_cross_y = -70.0                 # extra welded cross tube between the IBCs: carries the mast outrigger

# ---------------------------------------------------------------------
# Working robot: precision applicator V4 (combined_v4), two funnels 455 apart (A right, B left), rim z 1354
# ---------------------------------------------------------------------
funnel_pitch = 455.0                 # combined_v4: FUNNEL_PITCH
funnel_y = 170.0                     # combined_v4: funnel axis y on the working robot
funnel_rim_z = 1354.0                # combined_v4: FUNNEL_RIM_Z
nozzle_tip_z = funnel_rim_z + 106.0  # 1460
worker_outline = (500.0, -1767.0, 765.0)    # working robot with the applicator (lifted): half width, rear, front

# ---------------------------------------------------------------------
# Mast and arm: mast at the left between the two IBCs; arm out to the left. The working robot stops beside the
# refiller, same heading, its centre line dock_d from the refiller centre: funnel A (its right) is the near one.
# ---------------------------------------------------------------------
dock_d = S.dock_d                    # 1450
mast_xy = (S.mast_xy[0], mast_cross_y)       # (-660, -70)
mast_z0 = S.bed_z[1]                 # 739
nozzle_x = {"A": -dock_d + funnel_pitch / 2.0, "B": -dock_d - funnel_pitch / 2.0}   # -1222.5 / -1677.5
reach = {k: mast_xy[0] - v for k, v in nozzle_x.items()}                          # 562.5 / 1017.5
antenna_reach = mast_xy[0] + dock_d   # 790: RTK antenna above the middle between the nozzles (= worker centre line)
arm_fold = 90.0                      # transport: arm folded backwards along IBC B

# Hoses: 1.5" (48 outside), up the outer (-x) face of the mast side by side, then along the +y side of the arm
hose_od = S.hose_od
mast_hose_x = mast_xy[0] - S.mast_tube[0] / 2.0 - hose_od / 2.0 - 31.0       # -755: clear of the 130 top plate
mast_hose_dy = {"A": 60.0, "B": -60.0}      # A in front of the arm, B behind it (each clear of the 60 arm)
arm_lane_dy = {"A": 62.0, "B": 130.0}       # along the arm: A next to the arm, B outside it
arm_hose_z = 0.5 * (S.arm_z[0] + S.arm_z[1])
hose_under_z = upper_beam_z[0] - hose_od / 2.0 - 7.0     # 628: under the upper beams
mast_split_z = 1935.0                # fixed part of the hoses ends here (the loop above it moves with the arm and
                                     # stays above the IBC cages, top z 1899, when the arm folds)

# ---------------------------------------------------------------------
# Operation, traction, wheel loads (as ../simple)
# ---------------------------------------------------------------------
wheel_load_max = S.wheel_load_max    # 500 kg per wheel (Quinder datasheet)
motor_cont_kgf = S.motor_cont_kgf
motor_peak_kgf = S.motor_peak_kgf
c_rr = S.c_rr
pump_q_fill = S.pump_q_fill          # 120 l/min per pump
pump_kg = S.pump_kg
kit_extra_kg = {"mast_arm_2_drop_pipes": 32.0, "hoses_2x": 9.0, "electrics": 4.0}  # estimated

# ---------------------------------------------------------------------
# Fill bridge: two funnels over the gap between the IBCs, side by side 455 apart (A right, B left), so that the IBC
# trailer with two liquids (its arm lifted) fills both IBCs in one stop, the way it fills the working robot. Each
# funnel drains through a short PP 50 pipe over the cage into a DN50 bulkhead fitting in the top of its own IBC.
# ---------------------------------------------------------------------
fill_y = mast_cross_y               # -70: above the 100 mm gap between the IBCs
fill_x = {"A": funnel_pitch / 2.0, "B": -funnel_pitch / 2.0}
fill_fitting_y = {"A": 90.0, "B": -230.0}    # bulkhead fittings in the flat top of each bottle (clear of the straps)
fill_funnel = (200.0, 60.0, 100.0)  # rim, outlet, height
fill_pipe = (50.0, 3.0)             # PP 50
fill_pipe_z = 1935.0                # horizontal pipe centre: over the cage top bars (top z 1899)
fill_cone_z0 = fill_pipe_z + 25.0   # funnel outlet (elbow) height
FILL_RIM_Z = fill_cone_z0 + fill_funnel[2]       # 2060
bridge = (140.0, 6.0, 660.0)        # plate: width (y), thickness, length (x), on the cage top bars of both IBCs
bridge_z0 = 1899.0                  # top of the cage top bars
