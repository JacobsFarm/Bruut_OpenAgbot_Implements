import math

# =====================================================================
# Seat, canopy and frame extension (simple) - parameters
# A seat so a person can ride on the Bruut OpenAgbot (standard robot) and drive it by hand, a roll bar with a light
# canopy, and side extensions of the frame for wider implements.
#   - 4 cross tubes 40 x 40 x 3 on the upper beams (2 x M10 per beam, the vertical holes at |y| 275..625):
#     y -625 and -375 are long (x +-800): a stiff pair of side extensions at the rear (over the front wheels the
#     steering bearing plates leave no room); -375 and 275 also carry the seat plate and the footplate
#   - seat over the rear axle: base plate on the rear tubes, pedestal, tractor seat with a seat switch (dead man),
#     armrest console on the right with a joystick and an emergency stop mushroom
#   - footplate (checker plate 3 mm) with a toe board between the seat and the GNSS antenna
#   - roll bar (tube O42 x 3) standing on the rear extension outside the seat, with a polycarbonate canopy forward
# The operator sits in the middle of the robot, over the rear axle: his weight is shared by the axles and stays inside
# the track.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

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
m10_hole = 10.4

# ---------------------------------------------------------------------
# Cross tubes on the upper beams
# ---------------------------------------------------------------------
tube = 40.0
tube_wall = 3.0
tube_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + tube)       # 699 .. 739
CROSS = {                       # y: half length
    -625.0: 800.0,              # rear side extension (also carries the roll bar)
    -375.0: 800.0,              # rear side extension (pair with -625), seat plate and footplate
    275.0: 460.0,               # footplate front
}
end_cap_t = 3.0
ext_holes_x = tuple(500.0 + 50.0 * i for i in range(6))    # 50 mm grid on the extensions (x 500 .. 750), M10

# ---------------------------------------------------------------------
# Seat
# ---------------------------------------------------------------------
seat_y = -510.0                 # seat centre (over the rear axle)
seat_plate = ((-200.0, 200.0), (-645.0, -395.0), 8.0)   # on the tubes at y -625 and -375
pedestal = (80.0, 230.0)        # square tube 80 x 80, height above the plate (with the seat slide)
seat_pan = (460.0, 440.0, 70.0) # x, y, thickness (cushion)
seat_back = (460.0, 60.0, 480.0)  # x, thickness, height
seat_back_tilt = 12.0           # degrees backward
armrest = (60.0, 300.0, 40.0)   # x, y, z
console = (110.0, 160.0, 90.0)  # right armrest console: x, y, z
joystick = (14.0, 120.0, 40.0)  # stick d, length, knob d
estop = (60.0, 40.0)            # mushroom d, height (with collar)

# ---------------------------------------------------------------------
# Footplate with toe board
# ---------------------------------------------------------------------
foot = ((-260.0, 260.0), (-390.0, 300.0), 3.0)     # on the tubes at y -375 and 275 (in front of the seat plate)
toe_h = 80.0                    # toe board at the front edge
gnss_clear = (90.0, (480.0, 660.0))                 # the robot's GNSS dome: x half width, y range

# ---------------------------------------------------------------------
# Roll bar and canopy
# ---------------------------------------------------------------------
rops_d = 42.0
rops_wall = 3.0
rops_x = 600.0                  # legs at x +-600 on the rear extension, outside the seat and armrests
rops_top = 2050.0               # top of the bar (operator head ~1950 at 1.85 m)
rops_foot = (120.0, 80.0, 10.0) # foot plate x, y, t (2 x M10 into the tube)
canopy = ((-650.0, 650.0), (-700.0, 300.0), 6.0)    # polycarbonate, on 2 side rails from the bar
canopy_rail = 30.0              # square tube 30 x 30 x 2 under the canopy edges
canopy_z = rops_top + 10.0

# ---------------------------------------------------------------------
# Operator (for the renders and the calc only)
# ---------------------------------------------------------------------
operator_kg = 90.0
operator_cg = (0.0, -430.0, 1200.0)     # seated, estimated
operator_h = 1850.0

# ---------------------------------------------------------------------
# Riding rules and checks (sfe_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
pc = 1.2e-6                     # polycarbonate
foam = 0.15e-6                  # seat cushion bulk (estimated)
ride_speed_max = 1.5            # m/s with an operator on board (manual mode)
turn_r_min = 3.0                # m smallest turn radius at that speed (steering 30 deg, estimated)
slope_max_deg = 10.0            # sideways slope allowed when riding (rule)
implement_ext_kg = 15.0         # mass per side on an extension (e.g. a marker arm), at x 700
implement_ext_x = 700.0

# from build_sfe.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 93.7, "cg": (5.0, -377.0, 1185.0)}
