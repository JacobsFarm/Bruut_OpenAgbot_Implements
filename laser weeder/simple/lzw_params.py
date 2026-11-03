import math
import os
import sys

# =====================================================================
# Laser weeder (simple) - parameters
# Kills weed seedlings with a laser, without chemicals and without moving the soil. The light-tight hood of the
# drop-on-demand boom ("drop on demand boom/simple": belly rails, hanger posts, hood with brush strip, camera, LED bars;
# imported, not copied) hangs under the belly over one bed of 0.6 m. Instead of the injector rail it holds 2 galvo scan
# heads (one per 300 mm half of the bed) that aim the beam of a fibre-coupled 60 W diode laser at the growing point of
# every weed the camera finds. The 2 laser sources and their drivers sit in one air-cooled box on a cradle on top of the
# robot; 2 armoured fibre cables go straight down to the heads.
# Class 4 laser: it only fires inside the closed hood (brush strip on the ground), with interlocks on the hood height,
# the robot's tilt and a stop when the camera sees a reflection or an opening.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

DDB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "drop on demand boom", "simple")
if DDB_FOLDER not in sys.path:
    sys.path.append(DDB_FOLDER)
import ddb_params as D          # noqa: E402  (hood, posts, rails, camera, LEDs, field figures)

robot_kg = D.robot_kg
robot_axle_y = D.robot_axle_y
robot_lower_beam_y = D.robot_lower_beam_y
robot_lower_beam_z = D.robot_lower_beam_z
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
m10_hole = D.m10_hole

# ---------------------------------------------------------------------
# Scan heads: 2-axis galvo with an f-theta lens, under the hood top, one per half of the bed
# ---------------------------------------------------------------------
head_x = (-150.0, 150.0)
head_y = -110.0                 # behind the camera image (the camera looks at the front half)
head_box = (110.0, 110.0, 90.0)
lens = (60.0, 30.0)             # f-theta lens d, length below the head
scan_half_deg = 27.0            # optical scan angle each way (x and y): 300 mm field per head
spot_mm = 1.5                   # spot diameter on the ground (estimated, f-theta 254 mm class)

# ---------------------------------------------------------------------
# Laser box on a cradle on the inner upper beams (y -375 and 275), fibres down to the heads
# ---------------------------------------------------------------------
cradle_y = (-375.0, 275.0)
cradle_half = 380.0
cradle_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + 40.0)
box = ((-220.0, 220.0), (-395.0, 295.0), 140.0)     # x, y, height: rests on both cradle tubes
box_fan = (120.0, 30.0)                             # 2 fans in the rear face: d, depth
fibre_d = 14.0                                      # armoured fibre cable with the head's control cable

laser_w = 60.0                  # optical W per source (fibre-coupled diode, 976 nm class)
laser_eff = 0.35                # wall plug efficiency (estimated)
cooling_w = 60.0                # fans and TEC of the box (estimated)
kill_j = (8.0, 20.0, 40.0)      # J per weed: cotyledon / 2 leaves / 4 leaves (estimated from CO2/diode trials)
weed_mix = (0.4, 0.4, 0.2)      # share of the 3 sizes in a typical flush
retarget_ms = 5.0               # galvo jump + settle between weeds
speed = 0.20                    # m/s
weed_density = D.weed_density   # 20 / m2
work_width = 2 * 300.0
battery_wh = D.battery_wh
drive_w = D.drive_w
computer_w = D.computer_w + 20.0    # more vision (growing point) than for drops
led_w = D.led_w
field_eff = D.field_eff
box_kg = 14.0
head_kg = 1.6

# from build_lzw.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 47.5, "cg_y": -26.0}
