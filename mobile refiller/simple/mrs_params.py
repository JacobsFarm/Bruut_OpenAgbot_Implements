import math

# =====================================================================
# Mobile refiller, simple (IBC) - parameters
# A standard Bruut OpenAgbot carries a standard 1000 l IBC that is set on with pallet forks. A pump under the IBC,
# a fixed mast with a short arm and a hose that hangs down to a drip-stop nozzle. The working robot skips passes so
# that it can turn in one go (U-turn of 6 passes); the refiller stands inside that turn on the headland and the
# working robot stops on the straight part of the turn with its funnel under the nozzle. At the next turn the refiller
# drives 1 m further. No boom, no trailer, no camera.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot. All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = 500.0            # wheel centres at y = +-500
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_wheelbase = 1000.0
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)     # x-direction beams (chassis_beam_1, 1000 long)
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)     # y-direction beams (chassis_beam_2, 1300 long)
robot_upper_beam_z = (659.0, 699.0)
robot_beam = 40.0
robot_half_width = 500.0        # lower beams (1000 long)
robot_front = 715.0             # front / rear of the tyres
robot_stepper_plate_y = 405.0   # front edge of the free space: stepper-motor plates at y 405 .. 595, x +-295 .. 455
robot_stepper_top = 1032.0
robot_gnss = (0.0, 575.0, 740.0)    # the robot's own antenna: moved to the arm tip on the refiller
robot_kg = 161.5                # agbot comparison (not weighed)
grid = 50.0                     # beam holes M10 (10.4): lower beams |x| 125 .. 475, upper beams |y| 275 .. 625
m10_hole = 10.4

# ---------------------------------------------------------------------
# Liquid
# ---------------------------------------------------------------------
liquid_density = 1.2            # kg/l: mineral concentrate 1.1, UAN 1.32, water 1.0
liquid_viscosity = 3.0e-6       # m2/s (UAN ~ 3x water)

# ---------------------------------------------------------------------
# IBC: standard 1000 l composite IBC (e.g. Schuetz Ecobulk MX 1000): 1200 x 1000 x 1160 mm, brimful 1060 l,
# 4-way-entry pallet, steel tube cage, DN150 screw cap on top, DN50 valve at the bottom of a 1000 mm face.
# On the robot: 1200 across (x), 1000 along (y), valve on the left. The front stays 25 mm behind the stepper-motor
# plates, so the IBC sits low, straight on the bed on the upper beams (and 120 mm behind the middle of the robot).
# ---------------------------------------------------------------------
ibc_x = 600.0                   # half length (1200)
ibc_y = (-620.0, 380.0)         # 1000
IBC_CY = 0.5 * (ibc_y[0] + ibc_y[1])        # -120
ibc_h = 1160.0
ibc_nominal_l = 1000.0
ibc_brimful_l = 1060.0
ibc_kg = {"pallet": 22.0, "cage": 20.0, "bottle": 16.0}    # 58 kg (MX 1000: 56 kg steel pallet, 59 kg plastic)
pallet_h = 145.0                # estimated: fork opening min. 90
pallet_deck_t = 20.0
pallet_runner = (100.0, 25.0)   # 3 runners across (x): width (y), height
pallet_runner_y = (-570.0, -120.0, 330.0)
pallet_foot = 150.0             # 3 x 3 feet between deck and runners (fork openings 100 high)
bottle_x = 575.0                # blow-moulded HDPE, wall 2, inside the cage
bottle_y = (-596.0, 356.0)
bottle_wall = 2.0
bottle_r = 60.0
bottle_h = 980.0
cage_bar = 18.0                 # galvanised steel tube grid
cage_x = 591.0                  # bar axes (outer face at 600)
cage_y = (-611.0, 371.0)
cage_rings = (175.0, 420.0, 665.0, 910.0)   # above the IBC base
cage_top = 1151.0
cage_n = (8, 6)                 # vertical bars on the 1200 faces / the 1000 faces (incl. corners)
ibc_cap = (0.0, IBC_CY, 200.0, 45.0)        # DN150 screw cap: x, y, diameter, height above the bottle
valve_z = 200.0                 # DN50 butterfly valve axis above the IBC base (estimated)
valve_body = (110.0, 54.0)      # diameter, length (out from the bottle face)
valve_spigot = (70.0, 35.0)     # S60x6 thread with a camlock adapter
valve_gap = 90.0                # cage rings open around the valve (+- y)

# ---------------------------------------------------------------------
# Bed (pallet frame) on the upper beams: welded frame of 60 x 40 x 3 tube lying flat. 3 cross tubes bolted with
# 4 x M10 each through the upper-beam holes (bolt heads inside the tube, access holes on top: nothing sticks up),
# 1 cross tube at y 0 (no beam holes there) that carries the mast, side rails under the pallet edges, corner guides.
# ---------------------------------------------------------------------
bed_tube = (60.0, 40.0, 3.0)    # width, height, wall
bed_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bed_tube[1])   # 699 .. 739
bed_cross_y = (-525.0, -275.0, 325.0)       # bolted (upper-beam holes; y -575 / -425 carry the wheel-unit bolts)
bed_mast_y = 0.0                # welded cross tube, runs out to the mast (left)
bed_cross_x = 550.0             # cross tubes end at the side rails
bed_side_x = (550.0, 610.0)     # side rails under the pallet edges (+-)
bed_y = (ibc_y[0] - 5.0, ibc_y[1] + 5.0)     # side rails carry the corner guides too
bed_bolt_x = robot_upper_beam_x
guide = (50.0, 5.0, 140.0)      # corner guides: angle legs, thickness, height above the bed
lash_eye = (40.0, 12.0, 15.0)   # lashing eye on the side rail: length (y), thickness, height
IBC_Z0 = bed_z[1]               # 739: IBC base
IBC_TOP = IBC_Z0 + ibc_h        # 1899

# ---------------------------------------------------------------------
# Ratchet straps over the IBC (2 x 50 mm, LC 2000 daN)
# ---------------------------------------------------------------------
strap_y = (IBC_CY - 300.0, IBC_CY + 300.0)
strap_w = 50.0
strap_t = 2.0
ratchet = (40.0, 110.0, 60.0)   # x, z, y size of the ratchet buckle (right side)

# ---------------------------------------------------------------------
# Mast and arm (left side, in the middle of the IBC length). The hose runs up inside the mast. The arm pivots on
# a pin on the mast top: out (0 deg, pointing left) or folded backwards along the IBC for transport (90 deg),
# locked with a pin.
# ---------------------------------------------------------------------
dock_d = 1450.0                 # refiller centre line -> centre line of the working robot (and the nozzle)
mast_xy = (-660.0, bed_mast_y)
mast_tube = (80.0, 4.0)
mast_z = (bed_z[1], 1950.0)
outrigger_x = (-bed_side_x[1], -700.0)      # cross tube at y 0 runs out under the mast (80 x 40 x 3 there)
gusset_t = 10.0
gusset_h = 220.0                # up the mast from the bed
mast_top_plate = (130.0, 10.0)
pivot_pin = (30.0, 90.0)        # diameter, length above the top plate
mast_window = (60.0, 1850.0, 1930.0)        # slot in the outer face for the hose: width, z0, z1
arm_tube = (60.0, 3.0)
arm_z = (1965.0, 2025.0)
arm_sleeve = (70.0, 5.0)        # sleeve on the pivot pin
arm_tip = 40.0                  # arm beyond the drop-pipe axis
arm_fold = 90.0                 # deg, transport position
lock_r = 55.0                   # lock pin radius from the pivot
NOZZLE_XY = (-dock_d, bed_mast_y)           # drop-pipe axis with the arm out
drop_pipe = (50.0, 3.0)         # PP 50
drop_top = arm_z[0] - 10.0      # under the tip plate
nozzle_tip_z = 1250.0           # 106 mm above the funnel rim of the working robot
nozzle = (60.0, 40.0, 30.0)     # drip-stop valve body: diameter, height; cone below it: height
inlet_z = drop_top - 40.0       # side inlet of the drop pipe (hose from the arm)
ant_stem = (30.0, 25.0)
ant_dome = (150.0, 55.0)

# ---------------------------------------------------------------------
# Pump: 24 V DC centrifugal transfer pump, 1.5", inside the frame under the IBC (protected), axis along x,
# below the IBC valve: always flooded. Hangs on a cradle from the cross tubes at y -275 and 0.
# ---------------------------------------------------------------------
pump_axis = (IBC_CY, 540.0)     # (y, z)
pump_motor = (100.0, -180.0, 20.0)          # diameter, x0, x1
pump_head = (130.0, -260.0, -180.0)         # diameter, x0, x1
pump_inlet = (48.0, -300.0, -260.0)         # axial, towards the left
pump_outlet_x = -220.0          # radial, up from the head
pump_floor_z = (464.0, 470.0)
pump_hanger_x = (-60.0, -20.0)
pump_kg = 8.0
pump_eff = 0.40                 # wire-to-water (estimated)
pump_q_fill = 120.0             # l/min: the stream falls ~0.1 m into an open funnel
hose_d = 38.0                   # 1.5" inner
hose_od = 48.0

# ---------------------------------------------------------------------
# Receiver kit on the working robot (standard robot with the liquid fertilizer applicator advanced):
# work tank on a cradle, funnel O300, level sensor, vent (as the liquid variant, without the camera target)
# ---------------------------------------------------------------------
tank_wall = 6.0
cradle_y = (-375.0, 275.0)
cradle_tube = 40.0
cradle_wall = 3.0
cradle_half_len = 460.0
cradle_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + cradle_tube)     # 699 .. 739
pad_t = 5.0
tank_z0 = cradle_z[1] + pad_t   # 744
strap_w_rx = 50.0
strap_t_rx = 3.0
rx_tank_x = 420.0
rx_tank_y = (-400.0, 330.0)
rx_tank_h = 260.0
rx_tank_r = 50.0
rx_tank_nominal = 150.0
funnel_xy = (0.0, -35.0)
funnel_d = (300.0, 80.0)        # rim, outlet
funnel_h = 120.0
funnel_neck = 20.0
funnel_wall = 3.0
rx_level_sensor = (230.0, 150.0, 50.0, 80.0)
rx_vent = (230.0, -250.0, 20.0, 60.0)
FUNNEL_RIM_Z = tank_z0 + rx_tank_h + funnel_neck + funnel_h       # 1144
WORKER_OUTLINE = (500.0, -1767.0, 765.0)    # working robot with the applicator (lifted): half width, rear, front

# ---------------------------------------------------------------------
# Field pattern: skip passes so that every turn is a U-turn (no reversing)
# ---------------------------------------------------------------------
work_width = 1000.0             # 5 rows at 200
r_turn = 2400.0                 # planner radius (agbot slim: R_min 2107 at the rear axle)
y_turn = 1800.0                 # start of the arc from the field edge (applicator lifted and clear of the crop)
REFILLER_OUTLINE = (             # (x0, x1, y0, y1) in refiller coordinates, everything below 1.3 m
    (-robot_half_width, robot_half_width, -robot_front, robot_front),
    (-ibc_x - guide[1] - 1.0, ibc_x + guide[1] + 1.0, ibc_y[0] - guide[1] - 1.0, ibc_y[1] + guide[1] + 1.0),
    (-725.0, -ibc_x, IBC_CY - 140.0, mast_xy[1] + 50.0))  # valve + lever, suction elbow and hose, mast, gussets

# ---------------------------------------------------------------------
# Traction, stability, operation (for mrs_calc)
# ---------------------------------------------------------------------
motor_cont_kgf = 21.0           # per hub motor, continuous: Quinder 550 W S1 = 44 Nm at 74 rpm, / 0.215 m
motor_peak_kgf = 44.0           # at the controller limit 18 A (~86 Nm)
c_rr = {"grass": 0.08, "track": 0.03}       # rolling resistance: grass headland, hard farm track
mu = {"dry": 0.6, "wet": 0.35}
wheel_load_max = 500.0          # kg per wheel: datasheet max load 500 kg
v_full = 0.5                    # m/s with a full IBC (sloshing, stops)
v_empty = 1.0
a_full = 0.3                    # m/s2
battery_kwh = 2.4
