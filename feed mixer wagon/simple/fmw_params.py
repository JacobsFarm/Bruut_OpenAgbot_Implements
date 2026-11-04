import os
import sys

# =====================================================================
# Feed mixing and distribution wagon (simple) - parameters
# A small vertical mixer on the Bruut OpenAgbot (standard robot): loaded at a feed kitchen (by hand or from a hopper),
# weighed on 4 load cells, mixed by a vertical auger and laid along the feed fence through a side door and chute.
#   - 2 cross tubes 60 x 40 on the upper beams (y -375 and 275, grid holes, 2 x M10 per beam)
#   - 4 single-point load cells (x +-300) under a square sub-frame 40 x 40 with a 6 mm floor
#   - conical bin O640 -> O900, 700 high, 2 mm steel (0.33 m3), centred at y -50 (clear of the steering stacks and
#     the GNSS dome)
#   - vertical auger: shaft O60, a conical flight of 2 turns (r 290 -> 90), 2 knives; planetary gearbox under the
#     floor, a 48 V 2 kW motor lying along y under the floor
#   - discharge door on the right with an actuator, chute out to x 720 (feed fence on the right)
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

_HERE = os.path.dirname(os.path.abspath(__file__))
SSP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "spotspray unit", "boom")
if SSP_FOLDER not in sys.path:
    sys.path.append(SSP_FOLDER)

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
robot_battery_kwh = 1.9
m10_hole = 10.4

# ---------------------------------------------------------------------
# Cross tubes, load cells, sub-frame
# ---------------------------------------------------------------------
cross_y = (-375.0, 275.0)
cross = (60.0, 40.0, 3.0)       # y width, height, wall
cross_half = 470.0
cross_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + cross[1])          # 699 .. 739
cell_x = (-240.0, 240.0)        # between the cross-tube bolts (x 325) and the bin axis
cell = (130.0, 30.0, 30.0)      # x, y, z (single-point shear beam, 300 kg each)
cell_z = (cross_z[1], cross_z[1] + cell[2])                                   # 739 .. 769
sub = 40.0                      # sub-frame square ring 40 x 40 x 3
sub_z = (cell_z[1], cell_z[1] + sub)                                          # 769 .. 809
sub_x = 250.0                   # ring centre lines x +-250 (over the cells)
floor_t = 6.0
floor_z = (sub_z[1], sub_z[1] + floor_t)                                      # 809 .. 815

# ---------------------------------------------------------------------
# Bin
# ---------------------------------------------------------------------
bin_c = (0.0, -50.0)
bin_r = (320.0, 450.0)          # bottom, top radius
bin_h = 700.0
bin_t = 2.0
bin_z0 = floor_z[1]
rim = (30.0, 4.0)               # top rim flat bar (radial width, thickness)

# ---------------------------------------------------------------------
# Auger
# ---------------------------------------------------------------------
shaft_d = 60.0
shaft_top = bin_z0 + bin_h - 120.0
flight_turns = 2.0
flight_r = (290.0, 90.0)        # outer radius at the bottom and at the top
flight_z = (bin_z0 + 20.0, bin_z0 + 560.0)
flight_t = 8.0
flight_steps = 24               # sectors per turn (staircase approximation)
knife = (120.0, 40.0, 6.0)      # on the flight edge, 2x
auger_rpm = 30.0

# ---------------------------------------------------------------------
# Drive under the floor
# ---------------------------------------------------------------------
gearbox = (170.0, 170.0, 95.0)  # x, y, z (planetary, i = 100)
motor_d = 110.0
motor_y = (bin_c[1] - 85.0 - 200.0, bin_c[1] - 85.0)   # along -y from the gearbox, clear of the cross tube at -375
motor_z = 750.0                 # under the floor (809), above the robot centre (no beams at x 0)
motor_w = 2000.0
motor_rpm = 3000.0
gear_ratio = 100.0
gear_eff = 0.9

# ---------------------------------------------------------------------
# Discharge (right side)
# ---------------------------------------------------------------------
door_a = 50.0                   # angular width of the opening (deg), centred on +x
door_z = (bin_z0 + 15.0, bin_z0 + 215.0)
door_t = 3.0
door_lift = 180.0               # door slides up on 2 guides
chute_w = 260.0
chute_x = (bin_r[0] + 5.0, 720.0)
chute_z = (bin_z0 + 10.0, bin_z0 - 110.0)       # inner edge (at the floor), outer edge
chute_side_h = 80.0
chute_t = 3.0

# ---------------------------------------------------------------------
# Operation (fmw_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
feed_density = 330.0            # kg/m3 TMR (grass silage, maize, concentrate), estimated
fill = 0.85                     # usable share of the bin volume
mix_kw_per_m3 = 5.0             # vertical mixer, full bin (estimated from tractor mixers)
mix_min = 6.0
discharge_min = 3.0
drive_w = 300.0                 # robot drive with a full bin
electronics_w = 40.0
trip_min = 6.0                  # drive kitchen -> feed fence -> back
ration_cow_kg = 45.0            # fresh TMR per cow per day
ration_calf_kg = 8.0            # young stock / calves (estimated)

# from build_fmw.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 135.8, "cg": (37.0, -59.0, 946.0), "bin_kg": 122.8}
