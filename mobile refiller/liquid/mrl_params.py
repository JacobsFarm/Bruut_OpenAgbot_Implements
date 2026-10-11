import math

# =====================================================================
# Mobile refiller, liquid - parameters
# A standard Bruut OpenAgbot as a support robot: it carries liquid (fertilizer, water, ...) to a working robot and
# tops up that robot's tank on the headland, in the straight part of its turn, while both drive.
#
#   Refiller robot: T-shaped tank (upper part on the beams, sump down between the beams), transfer pump hanging under
#                   the rear beams (always flooded), column with a slewing boom, a trolley on the boom and a spout
#                   that goes down into the funnel of the working robot. RTK antenna straight above the spout,
#                   camera next to it.
#   Trailer:        towed tank built from the same parts as the robot (2 rear wheel units, beams), hub motors driven:
#                   6 driven wheels in total.
#   Receiver kit:   on the working robot: tank, funnel O300, camera target, level sensor.
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
robot_upper_beam_len = 1300.0
robot_beam = 40.0
robot_bracket_x = (261.0, 489.0)        # wheel brackets (inner, outer face)
robot_half_width = 489.0
robot_front = 715.0             # front of the front tyres
robot_stepper_top = 1032.0      # stepper motors above the front wheels (x +-375, y 500)
robot_gnss = (0.0, 575.0, 740.0)
robot_kg = 161.5                # agbot comparison (not weighed)
grid = 50.0                     # beam holes M10 (10.4): lower beams x = +-125 .. +-475, upper beams |y| >= 275
m10_hole = 10.4

# ---------------------------------------------------------------------
# Liquid
# ---------------------------------------------------------------------
liquid_density = 1.2            # kg/l: mineral concentrate 1.1, UAN 1.32, water 1.0
liquid_viscosity = 3.0e-6       # m2/s (UAN ~ 3x water)

# ---------------------------------------------------------------------
# Tank cradle (refiller and receiver kit): 2 cross tubes on top of the upper beams, M10 through the beam holes.
# Not across the middle: the sump of the refiller tank hangs down between them.
# ---------------------------------------------------------------------
cradle_y = (-375.0, 275.0)      # tube centre lines (upper-beam holes at y = -375 and 275)
cradle_tube = 40.0
cradle_wall = 3.0
cradle_half_len = 460.0
cradle_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + cradle_tube)     # 699 .. 739
pad_t = 5.0                     # rubber strip on the tubes
tank_z0 = cradle_z[1] + pad_t   # 744: bottom of the tanks on the cradle
strap_w = 50.0
strap_t = 3.0

# ---------------------------------------------------------------------
# Refiller tank (rotomoulded PE, wall 6): upper part 860 x 760 on the cradle, sump 500 x 530 down between the beams
# (inside the upper beams x +-305 and the inner lower beams y +-405; front: away from the steering sweep)
# ---------------------------------------------------------------------
tank_wall = 6.0
tank_x = 430.0                  # half width of the upper part
tank_y = (-430.0, 330.0)        # rear: column at y -500 (r 57); front: stepper plates at y 405
tank_h = 260.0
tank_z = (tank_z0, tank_z0 + tank_h)        # 744 .. 1004
tank_r = 60.0                   # radius vertical edges
sump_x = 250.0
sump_y = (-300.0, 230.0)
sump_z0 = 300.0                 # ground clearance under the sump
sump_r = 40.0
fill_cap = (-250.0, 150.0, 200.0, 36.0)     # x, y, diameter, height (screw lid with a basket strainer)
level_sensor = (250.0, 150.0, 50.0, 80.0)   # ultrasonic level sensor
outlet = (200.0, sump_y[0], sump_z0 + 45.0)  # sump outlet on the rear face (x, y, z), 1.5"

# ---------------------------------------------------------------------
# Rear sub-frame under the rear lower beams: carries the pump and the hitch. The column base plate on top of the
# beams uses the same 8 x M10 (sandwich).
# ---------------------------------------------------------------------
sub_plate = ((-200.0, 200.0), (-610.0, -390.0), (robot_lower_beam_z[0] - 10.0, robot_lower_beam_z[0]))
sub_bolt_x = (-175.0, -125.0, 125.0, 175.0)
hitch = (0.0, -830.0, 380.0)    # vertical hitch pin (x, y, z): behind the rear tyres (-715)
hitch_pin_d = 20.0
clevis_plate_t = 12.0
clevis_gap = 40.0               # between the clevis plates (drawbar eye 36)
hitch_side_x = (50.0, 60.0)     # side plates at x +-50 .. +-60
pump_cradle_y = (-555.0, -385.0)            # front and rear plate of the pump cradle (outer faces)
pump_cradle_t = 8.0
pump_cradle_x = (-195.0, 165.0)
pump_floor_z = (272.0, 280.0)

# ---------------------------------------------------------------------
# Transfer pump: 24 V DC centrifugal (self-priming), 1.5", about 150 l/min free flow, 120 l/min at 1 bar.
# Chemical version: PP housing, FKM/EPDM seals. Hangs below the tank: always flooded.
# ---------------------------------------------------------------------
pump_axis = (-470.0, 360.0)     # (y, z)
pump_motor = (110.0, -170.0, 30.0)          # diameter, x0, x1
pump_head = (150.0, 30.0, 110.0)
pump_inlet = (48.0, 110.0, 150.0)           # axial, +x
pump_outlet_x = 70.0            # discharge straight up from the volute
pump_kg = 9.0
pump_q_max = 150.0              # l/min free flow (estimated catalogue curve)
pump_h_max = 20.0               # m shut-off head
pump_eff = 0.40                 # wire-to-water (estimated)
pump_q_fill = 150.0             # l/min used in the animation and the turn calculation (with 1.5" hose, open funnel)
hose_d = 38.0                   # 1.5" inner
hose_od = 48.0
valve_box = 60.0

# ---------------------------------------------------------------------
# Column with slewing boom (on the rear, between the two rear lower beams so the hose goes up inside the column)
# ---------------------------------------------------------------------
col_xy = (0.0, -500.0)
col_od = 114.3
col_wall = 4.0
base_plate = ((-290.0, 290.0), (-610.0, -390.0), (robot_lower_beam_z[1], robot_lower_beam_z[1] + 12.0))
col_z = (base_plate[2][1], 1270.0)
gusset_t = 8.0
gusset = (100.0, 160.0)         # out from the tube, height
col_flange = (200.0, 10.0)      # top flange: diameter, thickness
slew_housing = (170.0, 60.0)    # worm slew drive (e.g. 3"): diameter, height
slew_motor = (80.0, 80.0, 110.0)
slew_z0 = col_z[1] + col_flange[1]          # 1280
root_plate = (120.0, 300.0, 10.0)           # u, v, thickness: rotates with the boom
boom_h = 80.0                   # belt linear module 80 (standing, carriage on the side)
boom_w = 55.0
boom_z0 = slew_z0 + slew_housing[1] + root_plate[2]
boom_z = (boom_z0, boom_z0 + boom_h)        # 1350 .. 1430
boom_v = (-190.0, 1625.0)       # along the boom from the column axis
boom_motor = (57.0, 102.0)      # NEMA 23 standing on the root end
boom_kg_per_m = 5.5
car_len = 150.0
car_t = 17.5
car_gap = 0.5
r_park = 350.0                  # trolley (spout axis) radius at park
r_max = 1500.0                  # stroke 1150
phi_park = 180.0                # degrees, + = counter-clockwise from +y: parked pointing backwards over the hitch
slew_rate = 30.0                # deg/s
slew_acc = 30.0                 # deg/s2
trolley_v = 400.0               # mm/s
trolley_a = 800.0

# Head on the trolley (u = across the boom, + = carriage side; v = along the boom; z world)
head_u = (boom_w / 2.0 + car_gap + car_t, boom_w / 2.0 + car_gap + car_t + 8.0)     # head plate
head_dv = 60.0
head_z = (1260.0, boom_z[1])
spout_u = 100.0                 # spout axis from the boom axis
spout_d = 50.0                  # PP pipe 50 (1.5")
spout_len = 280.0
spout_tip_up = 1265.0           # tip, spout raised: the head stays ~100 mm above the funnel rim
spout_stroke = 185.0            # lowered: 64 mm into the funnel of the working robot
spout_v_speed = 100.0           # mm/s (24 V linear actuator)
guide = (70.0, 30.0, 12.0)      # two guide blocks on the head plate: width (v), height, thickness
act_d = 40.0                    # spout actuator body
mast_d = 25.0
ant_stem = (30.0, 25.0)
ant_dome = (150.0, 55.0)
camera = ((75.0, 115.0), (-160.0, -110.0), (1260.0, 1300.0))   # u, v, z
chain = (50.0, 30.0)            # hose carrier on top of the boom: width, height
ctrl_box = ((-100.0, 100.0), (-655.0, -560.0), (800.0, 1050.0))  # on the back of the column

# ---------------------------------------------------------------------
# Trailer: same frame parts as the robot (2 rear wheel units, chassis beams), hub motors driven
# Trailer coordinates = robot coordinates at 0 articulation (straight behind the robot)
# ---------------------------------------------------------------------
tr_drawbar = 1450.0             # hitch pin -> trailer axle
tr_axle_y = hitch[1] - tr_drawbar           # -2280
tr_upper_y = tr_axle_y + 350.0  # centre of the 1300 long upper beams: wheel-unit bolts (axle +-75) on the holes
tr_lower_y = (tr_axle_y - 75.0, tr_axle_y + 75.0, tr_upper_y + 575.0)   # 2 at the wheel units, 1 at the front
tr_cradle_y = (tr_upper_y - 625.0, tr_upper_y - 325.0)              # on upper-beam holes, clear of the wheel-unit bolts
tr_tank_x = 430.0
tr_tank_y = (tr_axle_y - 400.0, tr_axle_y + 500.0)     # tank centre 50 mm in front of the axle: small hitch load
tr_tank_h = 340.0
tr_tank_r = 60.0
tr_fill_cap = (-250.0, tr_axle_y + 300.0, 200.0, 36.0)
tr_outlet = (200.0, tr_tank_y[1], tank_z0 + 45.0)
drawbar_tube = 50.0
drawbar_rear_x = 300.0
eye = (60.0, 36.0)              # drawbar eye: outer diameter, thickness
jack = (60.0, (-150.0, tr_lower_y[2] - 65.0), (250.0, 650.0))   # parking leg (raised) behind the front beam: d, (x, y), z

# ---------------------------------------------------------------------
# Receiver kit on the working robot (standard robot with the liquid fertilizer applicator advanced)
# ---------------------------------------------------------------------
rx_tank_x = 420.0
rx_tank_y = (-400.0, 330.0)
rx_tank_h = 260.0
rx_tank_r = 50.0
rx_tank_nominal = 150.0         # l, same as the applicator rationale
funnel_xy = (0.0, -35.0)
funnel_d = (300.0, 80.0)        # rim, outlet
funnel_h = 120.0
funnel_neck = 20.0
funnel_wall = 3.0
target = (-235.0, -35.0, 160.0)     # camera target (ArUco / AprilTag plate): x, y, size
rx_level_sensor = (230.0, 150.0, 50.0, 80.0)
rx_vent = (230.0, -250.0, 20.0, 60.0)

FUNNEL_RIM_Z = tank_z0 + rx_tank_h + funnel_neck + funnel_h       # 1144
SPOUT_TIP_DOWN = spout_tip_up - spout_stroke                       # 1080

# ---------------------------------------------------------------------
# Docking: robots side by side, opposite heading, centre lines D apart. Refiller beside the headland straight of the
# working robot, on the outside: the corners of the working robot sweep up to 0.73 m outside its path in the arcs
# (R 2.4 m) and must stay clear of the refiller.
# ---------------------------------------------------------------------
dock_d = 1450.0                 # 472 mm between the widest points
dock_lag = 0.06                 # s2: the refiller lags its set point by accel x dock_lag (relative error shown)

# ---------------------------------------------------------------------
# Traction, stability, operation (for mrl_calc)
# ---------------------------------------------------------------------
motor_cont_kgf = 21.0           # per hub motor, continuous: datasheet Quinder 10101025, 550 W S1 = 44 Nm at 74 rpm, / 0.215 m
motor_peak_kgf = 44.0           # at the controller limit 18 A (~86 Nm); 20 A gives ~95 Nm = 45 kgf
c_rr = 0.08                     # rolling resistance on grass / headland
mu = {"dry": 0.6, "wet": 0.35}
wheel_load_max = 500.0          # kg per wheel: datasheet max load 500 kg
v_drive = 1.0                   # m/s on the headland / track (empty and full)
battery_kwh = 2.4
