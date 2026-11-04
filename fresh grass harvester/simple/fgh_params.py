import math
import os
import sys

# =====================================================================
# Fresh grass harvester (zero grazing), simple - parameters
# Mows fresh grass, loads it and brings it to the feed fence, many small loads a day.
#   - front: 2 arms 40 x 60 under the front lower beams (x +-225, grid holes), a 1.2 m sickle bar on skids, an auger
#     trough behind it with a cross auger O200 that pushes the grass to the right
#   - a slatted elevator (300 wide) outside the right front wheel, from the auger end (y 900) up and back to y 300,
#     z 1.42 m, with a spout over the container
#   - a tipping container 0.41 m3 on 2 cross tubes on the upper beams (y -375, 275), hinged on the left (x -450) and
#     tipped 55 degrees by 2 actuators: it unloads on the left side, along the feed fence
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
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
robot_battery_kwh = 1.9
m10_hole = 10.4

# ---------------------------------------------------------------------
# Front arms
# ---------------------------------------------------------------------
arm_x = 225.0
arm = (40.0, 40.0, 3.0)         # width x, height z, wall (z 579 .. 619: the steered top plates sweep z 560 .. 564)
arm_z = (robot_lower_beam_z[0] - arm[1], robot_lower_beam_z[0])       # 559 .. 619
arm_y = (405.0, 860.0)
arm_bolt_y = (425.0, 575.0)

# ---------------------------------------------------------------------
# Auger trough and cutter bar
# ---------------------------------------------------------------------
auger_y = 910.0
auger_z = 170.0
auger_d = 200.0
auger_pitch = 200.0
auger_x = (-610.0, 560.0)
flight_t = 4.0
trough_r = 115.0                # inner radius of the bottom
trough_t = 3.0
trough_x = (-625.0, 560.0)
rear_wall_top = 330.0
drop_plate = (8.0, 60.0)        # thickness x, depth y
bar_x = (-600.0, 600.0)         # 1.2 m cutting width
bar_y = (1030.0, 1110.0)
bar_z = (45.0, 53.0)
section_pitch = 76.2
section_len = 70.0
skid = (60.0, 220.0, 45.0)      # x, y, height (bar on skids: cut height ~50 mm)
skid_x = (-570.0, 500.0)        # right skid inside the elevator foot
sickle_drive = ((-700.0, -625.0), (960.0, 1080.0), (60.0, 220.0))   # crank box + motor at the left end

# ---------------------------------------------------------------------
# Elevator (outside the right front wheel)
# ---------------------------------------------------------------------
elev_x = (560.0, 800.0)
elev_s = (900.0, 150.0)         # (y, z) of the lower roller axis
elev_e = (0.0, 1420.0)          # (y, z) of the upper roller axis (over the container front)
elev_wall = 150.0               # side wall height above the belt
elev_t = 3.0
roller_d = 100.0
slat_pitch = 200.0
slat = (20.0, 25.0)             # thickness along the belt, height
elev_motor = (90.0, 150.0)      # d, length (on the upper roller, outside right)
spout_x = (460.0, elev_x[0])    # short spout: ends outside the container's tipping path (x > 455); the
                                # slatted belt (~2 m/s) throws the grass over it into the container
spout_drop = 40.0
stay_y = 275.0                  # stay from the extended cross tube up to the elevator

# ---------------------------------------------------------------------
# Container
# ---------------------------------------------------------------------
cross_y = (-625.0, -375.0, 275.0)   # 2 under the container, 1 in front for the elevator stay
box_cross_y = (-625.0, -375.0)
cross = (60.0, 40.0, 3.0)
cross_x = (-490.0, 640.0)
cross_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + cross[1])     # 699 .. 739
tip_frame_z = (cross_z[1] + 6.0, cross_z[1] + 46.0)                      # 745 .. 785, over the bolt heads
box_x = (-440.0, 440.0)
box_y = (-820.0, 80.0)          # moved back for the balance (overhangs the beam ends by 170)
box_z = (tip_frame_z[1], 1300.0)
box_t = 2.0
hinge = (-465.0, tip_frame_z[0] + 20.0)          # (x, z) of the hinge axis (along y)
tip_max = 55.0                  # degrees, tipping to the left
act_x = 470.0                   # tip actuators on the right, body from the cross tube up
act_body = (50.0, 300.0)
ballast = ((-420.0, -120.0), (-775.0, -655.0), (525.0, 737.0))   # 60 kg steel block behind the robot, on the
                                # rear cross tube (front share and the right-hand elevator)

# ---------------------------------------------------------------------
# Operation (fgh_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
grass_density = 200.0           # kg/m3 fresh cut grass, loose in the container (estimated)
fill = 0.9
yield_dm_t_ha = 1.5             # per cut
dm_share = 0.18
mow_speed = 0.5                 # m/s
road_speed = 1.5                # m/s
distance_m = 300.0              # field to feed fence, one way
unload_min = 2.0
bar_w_per_m = 300.0             # sickle bar drive (sickle bar mower calc, ~)
auger_w = 150.0
elevator_w = 200.0
drive_w = 300.0
electronics_w = 40.0
cow_kg_day = 60.0               # fresh grass per cow per day (as the main feed)

# from build_fgh.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 286.3, "cg": (110.0, 59.0, 677.0), "box_kg": 70.2}
