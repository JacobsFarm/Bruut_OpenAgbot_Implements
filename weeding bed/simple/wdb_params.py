import os
import sys

# =====================================================================
# Weeding bed (lying platform), simple - parameters
# Two workers lie face down on padded boards beside the Bruut OpenAgbot (standard robot), one on each side, and weed
# or harvest the row under them by hand while the robot creeps along the bed.
#   - 4 cross tubes 40 x 40 x 3 on the upper beams (2 x M10 per beam, vertical holes at |y| 275..625):
#     y -625, -375 and 375 run across (x +-1200); at y 625 the GNSS dome sits in the middle, so there are 2 stubs
#     (x 260..1200 per side)
#   - per side: 4 hangers down to 2 side rails (x 600 and 1160, z 480..520, y -1050..1000), a leg board, a chest board
#     and a face rest with an opening (plywood + foam), above the tyres and outside the steering sweep
#   - per side: a hold-to-run pendant at the front of the board and an emergency stop on the outer rail
#   - per side: 2 drop-leg parking stands on the outer rail (down for getting on and off, up while driving)
#   - per side: a sun canopy on 2 posts, separate from the robot's GNSS antenna in the middle
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# helpers (box_span, bolt_z, ...) come from the seat frame extension
SFE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "seat frame extension", "simple")
if SFE_FOLDER not in sys.path:
    sys.path.append(SFE_FOLDER)

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
robot_battery_kwh = 1.9
gnss_dome = ((-75.0, 75.0), (500.0, 650.0))     # x, y of the dome (keep the stubs and canopies away)
steer_sweep_x = 534.0                            # outer x of the front top plate / tyre at 30 deg steering (model)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Cross tubes on the upper beams
# ---------------------------------------------------------------------
tube = 40.0
tube_wall = 3.0
tube_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + tube)     # 699 .. 739
half_len = 620.0                               # tubes end at the outer face of the hangers
CROSS_FULL = (-625.0, -375.0, 375.0)           # full tubes x +-620
CROSS_STUB = (625.0,)                          # 2 stubs x 260..620 (GNSS dome in the middle)
stub_inner = 260.0
end_cap_t = 3.0

# ---------------------------------------------------------------------
# Side frame (per side, mirrored): 4 C-frames (cross tube - hanger - cross arm under the bed), 2 rails on the arms
# Nothing crosses over the worker: the bed hangs from the inner hangers only.
# ---------------------------------------------------------------------
hanger_x = 600.0                               # 40 x 40 x 4, 46 mm outside the front steering sweep
hanger_wall = 4.0
hanger_y = CROSS_FULL + CROSS_STUB             # one C-frame under each cross tube
arm_z = (440.0, 480.0)                         # cross arm 40 x 40 x 4 under the rails, x 580 .. 1190
arm_x = (hanger_x - 20.0, 1190.0)
gusset = 70.0                                  # 6 mm gusset in the top corner (cross tube - hanger), robot side
rail_x = (660.0, 1160.0)                       # inner / outer side rail centre, on the arms
rail_z = (arm_z[1], arm_z[1] + 40.0)           # 40 x 40 x 3
rail_y = (-1050.0, 1000.0)
slat_y = (-900.0, -300.0, 200.0, 800.0, 960.0) # cross slats 40 x 20 x 2 between the rails under the boards

# ---------------------------------------------------------------------
# Lying boards (plywood 18 + foam 50, synthetic leather)
# ---------------------------------------------------------------------
board_x = (hanger_x + 30.0, rail_x[1] + 20.0)  # 630 .. 1180 = 550 wide, next to the hangers
ply = 18.0
foam = 50.0
leg_board_y = (-1050.0, 150.0)
chest_board_y = (180.0, 780.0)
chest_raise = 40.0                             # chest pad thicker (wedge), the head a bit higher
face_rest_y = (800.0, 1000.0)                  # face rest with an oval opening, worker looks down at the crop
face_hole = (120.0, 150.0)                     # x, y of the opening
board_z = rail_z[1]                            # plywood bottom

# ---------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------
pendant = (70.0, 110.0, 45.0)                  # hold-to-run box: x, y, z (2 buttons + speed knob), on the inner rail
pendant_y = 900.0
estop_d = 60.0
estop_y = 700.0

# ---------------------------------------------------------------------
# Parking stands (drop-leg, crank), on the outside of the outer rail
# ---------------------------------------------------------------------
stand_y = (-950.0, 880.0)
stand_tube = (60.0, 50.0)                      # outer tube, inner leg
stand_x = rail_x[1] + 20.0 + 12.0 + 30.0     # centre of the outer tube (12 mm clamp plate on the rail side)
stand_top = rail_z[1] + 140.0
stand_len = 380.0                              # outer tube length
stand_pad = (140.0, 10.0)
stand_pad_z_up = 150.0                         # pad height when raised (driving)

# ---------------------------------------------------------------------
# Sun canopy per side
# ---------------------------------------------------------------------
post = 30.0                                    # square tube 30 x 30 x 2 (sun canopy only)
post_x = rail_x[1] + 20.0 + 12.0 + post / 2.0  # posts clamped to the outside of the outer rail (12 mm plate)
post_y = (-625.0, 625.0)
canopy_z = 1400.0                              # underside of the canopy
canopy_x = (560.0, 1290.0)
canopy_y = (-1100.0, 1100.0)
canopy_t = 4.0                                 # twin-wall polycarbonate / tarp on a light frame

# ---------------------------------------------------------------------
# Workers (renders and calc only)
# ---------------------------------------------------------------------
worker_kg = 85.0
worker_x = 905.0                               # centre of the board
worker_cg = (worker_x, 100.0, 680.0)           # prone, cg near the hips (estimated)
worker_len = 1850.0
reach = 650.0                                  # arm length, shoulder to fingertips

# ---------------------------------------------------------------------
# Operation and checks (wdb_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
plywood = 0.6e-6
foam_rho = 0.05e-6
pc = 1.2e-6
speed_m_h = (100.0, 400.0)                     # creep speed range (m/h), set by the workers
strip_w = 0.5                                  # worked strip per worker (m)
drive_power_w = 120.0                          # drive power at creep speed with 2 workers (estimated)
electronics_w = 40.0                           # controller, GNSS, sensors
boarding_kg = 110.0                            # one worker stepping on the outer edge (incl. dynamic factor)
boarding_x = board_x[1]
crop_clear = arm_z[0]                          # clearance under the cross arms

# from build_wdb.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 177.7, "cg": (0.0, 7.0, 592.0)}
