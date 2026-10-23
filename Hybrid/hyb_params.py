import math

# =====================================================================
# Hybrid range-extender train (hyb) - parameters
# Steel base of 2 long + 4 short square tubes on the robot, with on top an in-line train:
# petrol engine -> jaw coupling -> generator, then controller (rectifier / DC-DC / BMS) and battery.
# The engine charges the battery while driving at light load; the battery delivers the peak for the hub motors.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot, so the implement stands directly in robot coordinates.
# All dimensions live here; never hardcode them in hyb_parts.py / build_hyb.py.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375                 # wheel centres x = +-375
robot_wheel_y = 500                 # wheel centres y = +-500
robot_axle_z = 215
robot_tire_d = 430
robot_tire_w = 100
upper_beam_x = (325.0, 425.0)       # the 4 upper beams (y direction), centres x = +-325, +-425, 40 x 40
upper_beam_w = 40.0
upper_beam_top = 699.0              # world z of the top of the upper beams (215 + 484)
robot_grid = 50
m10_hole = 10.4
# steering stack above the front wheels (stepper plate 190 x 160 at x +-375, y +-500): stay clear of x > 295 for |y| > 405
steer_stack_x_inner = 295.0
steer_stack_y_inner = 405.0

# ---------------------------------------------------------------------
# Base frame: steel square tube (2 long across the width, 4 short along y on top)
# ---------------------------------------------------------------------
tube = 50.0                         # square tube 50 x 50 x 3
tube_wall = 3.0
long_tube_y = (-350.0, 350.0)       # on the 50 mm grid of the upper beams
long_tube_half = 480.0              # length 960 (x -480..480), overhangs the outer beams by 35 mm
short_tube_x = (-200.0, -100.0, 100.0, 200.0)
short_tube_half = 480.0             # length 960 (y -480..480)
mount_bolt_d = 10.0                 # M10 x 130 through tube, spacer sleeve, beam
mount_sleeve_d = 16.0               # spacer sleeve D16 x 44 in the tube, so the tube does not crush
mount_bolt_len = 130.0
bolt_head_af = 17.0
bolt_head_k = 6.4
nut_m = 8.4

z_long_bot = upper_beam_top
z_long_top = z_long_bot + tube
z_short_bot = z_long_top
z_short_top = z_short_bot + tube
z_deck = z_short_top                # top of the frame, all components stand on this (world 799)

# ---------------------------------------------------------------------
# Train along y, rear -> front: battery, controller, generator, coupling, engine
# ---------------------------------------------------------------------
plate_t = 6.0                       # base plates under engine / battery / controller

# Battery 60 V (16S, nominal 59 V) 40 Ah = 2.4 kWh
batt_x = (-160.0, 160.0)
batt_y = (-470.0, -220.0)
batt_h = 210.0
batt_mass = 17.0                    # estimated, incl. BMS and case
batt_voltage = 59.2
batt_ah = 40.0
batt_usable = 0.8
strap_w = 30.0
strap_t = 3.0

# Controller box: rectifier (3-phase PM generator), DC-DC for 12 V, contactor, fuses
ctl_x = (-150.0, 150.0)
ctl_y = (-200.0, -80.0)
ctl_h = 140.0
ctl_mass = 5.0                      # estimated

# Generator: 3-phase permanent magnet alternator, direct on the engine shaft
gen_d = 160.0
gen_y = (-40.0, 120.0)
gen_cap_d = 140.0
gen_cap_y = (-65.0, -40.0)
gen_flange_d = 190.0                # bell housing / adapter plate to the engine
gen_flange_y = (120.0, 140.0)
gen_power = 3000.0                  # W continuous electrical, estimated
gen_eff = 0.88
gen_mass = 9.0                      # estimated
gen_saddle_x = 120.0                # saddle block under the generator
gen_box = (70.0, 50.0, 40.0)        # terminal box x, y, z

coupling_d = 70.0                   # jaw coupling with spider
coupling_y = (140.0, 175.0)

# Engine: 212 cc petrol, horizontal shaft (Honda GX200 type), PTO towards the generator
eng_pto_z = 100.0                   # shaft height above the engine base plate top
eng_plate_x = (-180.0, 180.0)
eng_plate_y = (165.0, 470.0)
crank_x = (-130.0, 130.0)
crank_y = (175.0, 335.0)
crank_h = 170.0                     # crankcase height above plate top
cyl_d = 100.0
cyl_x = 40.0
cyl_y = 255.0
cyl_h = 120.0
head = (140.0, 120.0, 60.0)         # cylinder head x, y, z
tank_x = (-150.0, -35.0)
tank_y = (185.0, 335.0)
tank_h = 160.0
fan_d = 190.0
fan_y = (335.0, 420.0)
recoil_d = 140.0
recoil_y = (420.0, 450.0)
muffler_d = 90.0
muffler_x = 190.0
muffler_y = (220.0, 420.0)
muffler_z = 90.0
filter_d = 100.0
filter_x = 135.0
filter_y = 300.0
filter_h = 60.0
eng_power = 4800.0                  # W rated shaft power, estimated
eng_mass = 18.0                     # dry + oil, estimated
eng_sfc = 0.45                      # L/kWh at part load, estimated

# ---------------------------------------------------------------------
# Load assumptions (for hyb_calc.py)
# ---------------------------------------------------------------------
n_hubmotors = 4
hub_power = 550.0                   # W continuous each (standard robot)
hub_peak_factor = 2.0               # peak = 2 x continuous
light_task_w = 900.0                # W, e.g. driving with a light implement
heavy_task_w = 2200.0               # W, all hub motors continuous
robot_mass = 150.0                  # kg, estimated (not measured)
frame_density = 7850.0              # kg/m3
