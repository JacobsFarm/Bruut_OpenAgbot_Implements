import math

# =====================================================================
# In-row weeder with double arms for 2 rows of broccoli - parameters
# Like the finger variant (../finger), but every row has TWO swing arms, one on each side of the row, each on its own
# stepper motor (4 in total). Between the plants both knives are in: each covers one half of the row band and they
# overlap a little in the row line. Just before a plant both swing out (each to its own side), past the plant both
# swing back in. Each knife moves only 77 mm instead of 115, so the swings are shorter and quicker, and the soil on
# both sides of the stem is hoed up to the safe zone. The two knives of a row run 75 mm apart along the travel, so they
# never touch. A camera under the front beams finds the plants; odometry carries every stem back to the knives.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres at (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = 500.0            # wheel centres at y = +-500
robot_axle_z = 215.0            # ground_to_axle
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_tire_rear_front = -robot_axle_y + robot_tire_d / 2.0      # -285: front of the rear tread
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)             # centres of the x-direction beams (40 x 40)
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)             # centres of the y-direction beams
robot_upper_beam_z = (659.0, 699.0)
robot_beam = 40.0
robot_steer_max = 30.0          # degrees
robot_kg = 161.5                # agbot comparison (not weighed)
robot_cg = (0.0, 95.0, 543.0)   # agbot comparison (estimated)
robot_track = 2.0 * robot_wheel_x
robot_wheelbase = 2.0 * robot_axle_y
grid = 50.0                     # beam holes M10: lower beams x = +-125 .. +-475, upper beams |y| = 275 .. 625
m10_hole = 10.4
wheel_load_max = 500.0          # kg per wheel (Quinder hub motor datasheet)

# ---------------------------------------------------------------------
# Crop: broccoli planted in two rows per robot pass. The rows lie at half the track on both sides of the centre, so
# the robot wheels run in the middle of the inter-rows (row spacing = track / 2 = 375 mm, the next pass has its rows
# at 562.5 and 937.5).
# ---------------------------------------------------------------------
row_x = (-robot_track / 4.0, robot_track / 4.0)     # -187.5, 187.5
row_spacing = robot_track / 2.0                      # 375
plant_spacing = 450.0           # in the row (planted with a transplanter: +-30 mm scatter, the odd gap)
plant_scatter = 30.0            # along the row
plant_offset = 15.0             # max sideways offset of a stem from the row line
stem_d = 15.0                   # broccoli stem at the soil, 2-5 weeks after planting
canopy_d = (150.0, 260.0)       # leaf rosette at weeding time
safe_r = 50.0                   # no soil movement closer than this to the stem (knife edge to stem centre)

# ---------------------------------------------------------------------
# Frame: two rails 40 x 40 x 3 under the lower beams at x = +-225 (M10 through beam and rail, 4 per rail),
# a toolbar 50 x 50 x 4 under the rails at y 260 (in front of the units, behind the steering sweep).
# ---------------------------------------------------------------------
rail_x = 225.0
rail = 40.0
rail_wall = 3.0
rail_y = (-600.0, 600.0)
rail_z = (robot_lower_beam_z[0] - rail, robot_lower_beam_z[0])      # 579 .. 619
toolbar = 50.0
toolbar_wall = 4.0
toolbar_y = 260.0               # centre (235 .. 285)
toolbar_z = (rail_z[0] - toolbar, rail_z[0])                         # 529 .. 579
toolbar_half = 400.0            # out to the lift actuator lugs (x +-367.5), above the front tyres' reach
toolbar_clamp = (60.0, 6.0)     # U-clamp plates where toolbar meets the rails: width, thickness

# ---------------------------------------------------------------------
# Row unit (right unit; the left one is its mirror). Local u = x - row_x (+ = outwards, towards the robot wheel).
# Parallelogram from the toolbar back to the unit head: links 170 long, pins 80 apart.
# ---------------------------------------------------------------------
brk_plate_t = 8.0               # toolbar brackets (2 per unit) at u = link_u -+ (link_gap / 2 + ...)
link_u = 20.0                   # centre of the link pairs: head cheeks at link_u +- 30, link bars at +- 38,
                                # toolbar brackets at +- 46 (plate centres)
link_bar = (30.0, 8.0)          # flat bar height x thickness
link_len = 170.0
link_pin_d = 16.0
pin_y_front = 230.0             # pins on the toolbar brackets
pin_z = (500.0, 420.0)          # upper, lower pin (working position)
pin_y_rear = pin_y_front - link_len                 # 60: pins on the unit head
lift_travel = 50.0              # unit raised for the headland: knife 30 mm above the soil (more: links meet the rails)
float_travel = 40.0             # free float up / down in work (slot in the lift actuator rod end)

# Unit head: deck plate with two cheeks for the link pins, two flange bearings under the deck, two gearboxes and motors
deck_t = 8.0
deck_u = (-145.0, 232.0)
deck_y = (-115.0, 80.0)
deck_z = (370.0, 370.0 + deck_t)                    # 370 .. 378
cheek_t = 8.0
cheek_y = (20.0, 80.0)
cheek_z = (deck_z[1], 525.0)

# Two swing arms per row. Side +1 = outer arm (shaft towards the robot wheel), -1 = inner arm (shaft towards the
# middle of the robot). Arm angle theta: 0 = straight back; the finger is at u = side x (shaft_u - arm_r sin theta).
SIDES = (1, -1)
shaft_u = 110.0                 # shafts at u = +-110
shaft_y = {1: 30.0, -1: -45.0}  # the inner arm sits 75 mm further back: the two knives of a row never meet
stagger = shaft_y[1] - shaft_y[-1]
shaft_d = 20.0
shaft_z = (280.0, deck_z[1] + 10.0)
bearing = (86.0, 30.0, 33.0)    # flange bearing UCFL204 class: body width, height, centre height under the deck
hub_d = 45.0                    # clamp hub on the shaft at the arm
arm_r = 220.0
arm_bar = (40.0, 12.0)          # width x thickness (flat bar, aluminium 6082)
arm_z = (280.0, 280.0 + arm_bar[1])          # above the broccoli leaves
in_u = 22.5                     # knife centre when in: each knife covers its half of the row band (+5 mm overlap)
out_u = 100.0                   # knife centre when out (stems up to 15 mm off the row line, knife turned with the arm)
theta_in = math.degrees(math.asin((shaft_u - in_u) / arm_r))       # 23.4
theta_out = math.degrees(math.asin((shaft_u - out_u) / arm_r))     # 2.6
theta_park = theta_out          # headland: knives out beside the row

# Finger: spring-steel shank (flat 30 x 8, vertical, a coil at the top for give), knife at the bottom
shank = (30.0, 8.0)
shank_coil = (40.0, 50.0)       # coil spring OD, length, just under the arm
knife_w = 50.0                  # across the row: half the band + overlap
knife_l = 35.0                  # along the travel
knife_t = 4.0
work_depth = 20.0               # knife bottom below the soil surface
knife_z = (-work_depth, -work_depth + knife_t)
band = 2.0 * in_u + knife_w     # 95: row band hoed when both knives are in

# Gauge wheel in the robot's wheel track (inter-row centre, x = +-375): sets the knife depth
gauge_u = robot_track / 2.0 - row_x[1]              # 187.5
gauge_d = 200.0
gauge_w = 60.0
gauge_y = -40.0
gauge_fork_t = 6.0
gauge_holes = 3                 # axle holes in the fork: knife depth 5 / 20 / 35 mm
gauge_hole_pitch = 15.0

# Stepper + planetary gearbox on the deck, coaxial with each shaft
gear_d = 60.0                   # planetary gearbox flange / body
gear_len = 75.0
motor_sq = 57.0                 # NEMA 23
motor_len = 112.0               # closed-loop motor with encoder
motor_kg = 1.4
gear_kg = 1.0
gear_ratio = 10.0
gear_eff = 0.90
motor_T_hold = 3.0              # Nm, NEMA 23 closed loop (e.g. 23HS45 / 57HSE3N class)
motor_T_curve = ((0.0, 2.8), (300.0, 2.6), (600.0, 2.1), (900.0, 1.6), (1200.0, 1.2), (1500.0, 0.9))  # rpm, Nm at 48 V
motor_rpm_max = 1500.0
J_rotor = 0.48e-4               # kg m2 (rotor)
J_gear = 0.10e-4                # gearbox, at the motor side
stepper_w_idle = 15.0           # W per motor holding (closed loop reduces current at rest)
stepper_w_move = 70.0           # W per motor while swinging (estimated)

# Lift actuator per unit, on the outer side: from a lug on the toolbar to a lug on the deck, slotted rod end (float)
act_base = (180.0, 260.0, 615.0)        # (u, y, z) pin on the lug on top of the toolbar
act_end = (180.0, -10.0, 395.0)         # (u, y, z) pin on the deck lug (working position, middle of the slot)
act_body_d = 40.0
act_rod_d = 16.0
act_closed = 260.0              # pin-pin retracted
act_stroke = 100.0
act_force = 500.0               # N, 24 V, 15 mm/s
act_speed = 15.0
act_kg = 1.1
lug_t = 6.0

# ---------------------------------------------------------------------
# Camera under the front inner beam, looking down at both rows (tilted 15 degrees forward)
# ---------------------------------------------------------------------
cam_plate = ((-150.0, 150.0), (380.0, 475.0), (robot_lower_beam_z[0] - 6.0, robot_lower_beam_z[0]))
cam_plate_bolt_x = (-125.0, 125.0)
cam_xyz = (0.0, 410.0, 545.0)   # optical centre (tilt pivot 15 mm above it)
cam_pitch = 15.0                # degrees forward of straight down
cam_box = (60.0, 50.0, 55.0)    # housing x, y, z (axis down)
cam_lens = (30.0, 18.0)
cam_px = (1920, 1200)           # 2.3 MP global shutter (IMX174 class), 5.86 um
cam_pixel = 0.00586
cam_f = 6.0                     # mm (wide angle, 86 x 61 degrees)
cam_fps = 20.0
infer_ms = 40.0                 # plant detection per frame (estimated, Jetson Orin Nano class)
led_bar = (200.0, 30.0, 20.0)   # two LED bars beside the camera (shade under the robot), length x width x height
led_x = 125.0
led_y = 458.0                   # in front of the plate bolts

# Control box on the upper inner beams, behind the units: computer, 4 stepper drivers, 2 actuator relays, DC-DC
box_x = (-280.0, 280.0)
box_y = (-390.0, -260.0)
box_h = 120.0
box_base = ((-345.0, 345.0), (-400.0, -250.0), 4.0)
box_bolt = ((-325.0, 325.0), (-375.0, -275.0))     # M10 into the upper inner beams (holes |y| 275 .. 625)

# ---------------------------------------------------------------------
# Operation (ird_calc and the animation)
# ---------------------------------------------------------------------
speed = 0.5                     # m/s working speed (1.8 km/h)
margin = 15.0                   # extra distance before / after the safe zone (odometry, plant position)
odo_err = 0.01                  # odometry error, fraction of the distance carried
soil_specific = 4.0             # N per cm2 of worked cross-section (knife width x depth; sideways: knife length x
                                # depth), shallow hoeing in a loose seedbed (estimated, 2-6 N/cm2 in the literature)
soil_shank = 1.0                # N per cm2 of shank face in the soil (thin edge leading)
torque_use = 0.70               # share of the stepper's torque curve used (closed loop, no stall)
field_eff = 0.80                # headland turns
battery_kwh = 2.4
drive_w = 300.0                 # W driving on soil at 0.5 m/s (estimated)
computer_w = 30.0
c_rr = 0.10
