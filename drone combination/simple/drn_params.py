import os
import sys

# =====================================================================
# Drone combination (simple) - parameters
# A landing platform on the Bruut OpenAgbot (standard robot) so a mapping drone (Mavic-3-class, ~1 kg, 77 Wh) uses the
# robot as a mobile base station: it takes off from the robot, maps the plot, lands back on the platform, sends its
# images over the robot's link and charges from the robot battery while the robot works the task map.
#  - Platform: aluminium plate 1000 x 1000 x 6 at z 1100, above the steering stacks (top 1032), on 4 posts 40 x 40 on
#    2 cross bars bolted to the upper beams at y +-325.
#  - 4 PE guide wedges along the edges turn a landing up to +-250 mm off-centre into the middle (passive centring).
#  - 2 copper charging strips under the landing skids (a charging adapter in the drone's landing gear).
#  - An AprilTag plate in the middle for the visual landing aid (with RTK for the approach).
#  - The robot's GNSS antenna moves from its dome (now under the platform) to a short post on the front-right corner.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

PBL_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "push blade", "simple")
if PBL_FOLDER not in sys.path:
    sys.path.append(PBL_FOLDER)

robot_steer_deg = 30.0
robot_mass = 160.0
upper_beam_x = ((305.0, 345.0), (405.0, 445.0))  # inner and outer upper beams (both sides), z 659..699
upper_beam_top = 699.0
hole_y = 325.0                  # vertical M10 grid holes in the upper beams at |y| 275, 325 .. 625
stepper_top = 1032.0

# Cross bars 60 x 40 x 3 at y +-325 over all 4 upper beams; 4 posts 40 x 40 x 3 at x +-375 (between the beams of a side)
bar_x = 470.0
bar_wh = (60.0, 40.0)
post_x = 375.0
post_w = 40.0
plate_z = 1100.0                # underside of the platform plate
plate = (1000.0, 1000.0, 6.0)
plate_y0 = -500.0               # platform y -500 .. 500
frame_wh = (30.0, 30.0)         # perimeter frame tube under the plate

# Guide wedges (PE): along each edge, rising from the landing zone to the edge
wedge_w = 120.0                 # width (from the edge inward)
wedge_h = 60.0
landing_zone = 760.0            # flat square in the middle

# Charging strips (copper on a PE base), along y, under the drone skids
strip_x = 110.0                 # strips at x +-110 (skid track of the drone)
strip = (25.0, 400.0, 4.0)

magnet_N = 20.0                 # magnets under the charging strips pull the steel skid pads (holds the drone in wind)
tag = (180.0, 250.0, 1.0)       # AprilTag plate between the charging strips

# GNSS antenna moved to a post on the front-right corner of the platform (outside the landing zone)
gnss_post = (440.0, 440.0)
gnss_post_h = 150.0
gnss_dome = (150.0, 56.0)

# ---------------------------------------------------------------------
# Work (drn_calc)
# ---------------------------------------------------------------------
g = 9.81
alu = 2.7e-6
pe = 0.95e-6
steel = 7.85e-6
drone_kg = 1.05
drone_wh = 77.0
drone_flight_min = 40.0
charge_w = 100.0
charge_eff = 0.88
landing_err = (0.10, 0.25)      # m: RTK + tag typical, worst case still caught by the wedges
fly_alt = 100.0                 # m
cam_hfov = 84.0
side_overlap = 0.7
fly_speed = 10.0                # m/s
reserve = 0.25                  # battery kept for the return and landing
wind_max = 12.0                 # m/s
robot_battery_wh = 1900.0
MODEL_MASS = {"kg": 42.0, "cg_z": 1021.0}
