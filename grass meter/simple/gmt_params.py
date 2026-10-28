import math

# =====================================================================
# Grass meter / crop scanner (simple) - parameters
# Sensor kit for the Bruut OpenAgbot (standard robot) that maps grass cover while driving:
#  - a front boom on the front outer lower beam with 2 active NDVI sensors (red / NIR, own light: works in sun and at
#    night), a down-looking lidar distance sensor for canopy height and an RGB camera on a short mast;
#  - a sledge plate meter under the robot between the axles (0.1 m2 plate on a trailing parallelogram, the arm angle
#    gives the compressed sward height), lifted by a small actuator at the headland.
# Covers the "NIR sensor" idea as well. Height, NDVI and dry matter are logged per GNSS position: task maps for the
# fertilizer spreader and the liquid applicator.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_r = 265.0            # lugged tyre in the model
robot_tire_w = 100.0
robot_front_beam_y = (555.0, 595.0)     # front OUTER lower beam (x direction), z 619..659
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_gnss = (0.0, 575.0)       # dome y 500..650, z 684..740; mount x +-15 hangs to z 594
robot_steer_deg = 30.0
robot_mass = 160.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Front boom: 2 brackets (flat 60 x 8, U-clamp round the front outer lower beam) at x +-150, forward to a cross tube
# 40 x 40 x 3 at y 830..870 above the tyres (tyre top z 480)
# ---------------------------------------------------------------------
bracket_x = 150.0
bracket = (8.0, 60.0)           # thickness (x), height (z) of the bracket bar
clamp_t = 6.0
boom_y = (830.0, 870.0)
boom_z = (600.0, 640.0)
boom_x = 650.0                  # half length

# Sensors on the boom (box sizes x, y, z)
ndvi_x = 550.0                  # 2 active NDVI sensors, lens 560 above the ground, field of view ~0.35 m wide
ndvi_box = (60.0, 120.0, 80.0)
ndvi_z = 560.0                  # bottom (lens)
lidar_x = 0.0                   # lidar distance sensor looking down at the canopy
lidar_box = (60.0, 60.0, 70.0)
cam_mast = (25.0, 400.0)        # O, height of the camera mast above the boom
cam_box = (90.0, 70.0, 60.0)
cam_tilt = 40.0                 # degrees down from horizontal
logger_box = (200.0, 150.0, 90.0)       # logger / GNSS-RTK interface box on the boom, x -300

# ---------------------------------------------------------------------
# Plate meter: bearer 40 x 40 x 3 across the upper beams at y 200, a post 40 x 40 down to the pivots, 2 trailing arms
# (tube 20 x 20 x 2, parallelogram) to a plate 316 x 316 (0.1 m2, PE 5 mm with the front edge turned up)
# ---------------------------------------------------------------------
bearer_y = 200.0
bearer = 40.0
bearer_x = 470.0
post = 40.0
pivot_y = 200.0
pivot_z = (360.0, 300.0)        # upper and lower arm pivots on the post
arm_len = 350.0
arm = 20.0
arm_x = 60.0                    # arms at x +-60 (a pair upper, a pair lower)
plate_side = 316.0
plate_t = 5.0
plate_lip = 40.0                # turned-up front edge, 30 degrees
sward_h = 60.0                  # compressed height in the model (mm)
H_RANGE = (0.0, 200.0)          # measuring range of the compressed height
lift_h = 250.0                  # plate bottom when lifted
encoder_d = 40.0                # angle sensor on the upper pivot
plate_mass = 0.5                # kg on the sward (plate + arms counterbalanced by a spring), 5 kg/m2 like a hand RPM
# lift actuator: 24 V 200 N, stroke 100, beside the post (x 36) from a lug on the post to a cross bar between the
# upper arms; the rod eye is slotted, so in work the plate floats on the sward
act_x = 36.0
act_base = (200.0, 600.0)       # (y, z)
act_arm = 0.45                  # rod pin at this fraction of the upper arm
act_body_d = 24.0
act_rod_d = 12.0

# ---------------------------------------------------------------------
# Work (gmt_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
pe = 0.95e-6
speed = 1.5                     # m/s mapping speed
transect = 10.0                 # m between passes (a plate track every 10 m, NDVI 2 x 0.35 m strips)
turn_s = 15.0
rate_hz = {"ndvi": 10.0, "lidar": 20.0, "plate": 10.0, "camera": 1.0}
p_sensors = 25.0                # W: 2 NDVI, lidar, camera, logger
crr = 0.06
eta_drive = 0.75
battery_wh = 1900.0
# dry matter from compressed height: kg DM/ha = a * h(cm) + b (estimated, ryegrass/clover; calibrate per farm)
dm_a = 140.0
dm_b = 500.0
ndvi_noise = 0.02               # repeatability of an active sensor (estimated)
encoder_bits = 12


def arm_angle(h):
    """Arm angle (deg below horizontal) for a plate bottom at height h (the lower arm pivot sets the geometry)."""
    lower_end_z = h + plate_t + 25.0                     # lower arm pin on the plate bracket, 25 above the plate
    return math.degrees(math.asin((pivot_z[1] - lower_end_z) / arm_len))


def arm_end(z_pivot, h):
    a = math.radians(arm_angle(h))
    return pivot_y - arm_len * math.cos(a), z_pivot - arm_len * math.sin(a)
