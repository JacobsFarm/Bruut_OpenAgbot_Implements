import math

# =====================================================================
# Soil compaction meter (simple) - parameters
# Automatic cone penetrometer for the Bruut OpenAgbot (standard robot), in the middle of the robot (as the soil
# sampler) so the robot weight is the reaction. A ball-screw Z axis pushes a rod O9.5 with a 30 degree cone O12.83
# (ASABE S313 small cone) into the soil at 30 mm/s down to 600 mm; an S-type load cell between the carriage and the rod
# gives the force, the screw position gives the depth. A sprung foot finds the ground surface (zero depth) and carries
# a capacitive moisture probe that reads the topsoil moisture at the same point (cone resistance depends on it).
# Readings are logged per GNSS point: a compaction map per depth layer.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_mass = 160.0              # kg, estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Bridges: 2 x tube 40 x 40 x 3 on the inner upper beams (as the soil sampler), the rear one carries the logger
# ---------------------------------------------------------------------
bridge = 40.0
bridge_x = (-365.0, 365.0)
bridge_front_y = (60.0, 100.0)
bridge_rear_y = (-260.0, -220.0)
bridge_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bridge)
bridge_bolt_x = 325.0
# stays (flat 40 x 6) from the bottom of the mast back to the rear bridge: the push reaction on a long mast
stay = (40.0, 6.0)

# ---------------------------------------------------------------------
# Z axis: mast plate 10 mm on the front bridge, 2 x SBR20, ball screw SFU1605, NEMA23 (closed loop)
# ---------------------------------------------------------------------
mast_x = 110.0
mast_y = (50.0, 60.0)
mast_z = (120.0, 1150.0)
rail_x = 70.0
rail_y = (20.0, 50.0)
screw_y = 35.0
screw_d = 16.0
screw_lead = 5.0
motor = (57.0, 100.0)
motor_torque = {75.0: 1.3, 30.0: 2.0}   # Nm the NEMA23 gives at a feed of 75 and 30 mm/s (estimated)
carriage_w = 100.0
carriage_h = 140.0
carriage_y = (-12.0, 20.0)
rod_y = -60.0                   # rod axis (x = 0)
holder_y = (-90.0, -12.0)
holder_h = 60.0
loadcell = (50.0, 60.0, 20.0)   # S-type 2 kN (x, z, y): between the holder and the rod clamp block
clamp_h = 40.0

# rod and cone (ASABE S313.3 small cone: 30 deg, base O12.83, 1.29 cm2; rod O9.5)
rod_d = 9.5
rod_len = 700.0                 # below the clamp block
cone_d = 12.83
cone_angle = 30.0
# the rod is guided at the ground by a PTFE bush in the foot ring (free length at most 700 mm)

# foot: PE ring O140 x 15 on 2 rods O10 through the holder, moisture probe (2 tines 60 mm) beside the rod
foot_d = 140.0
foot_t = 15.0
foot_rod_x = 50.0
foot_drop = 40.0
foot_rod_len = 885.0
moist_box = (40.0, 25.0, 50.0)
moist_tine = (4.0, 60.0)
logger_box = (200.0, 120.0, 80.0)

# poses: tip height above the ground (- = in the soil)
tip_park = 150.0
depth_max = 600.0
TIP_POSES = (150.0, 0.0, -300.0, -600.0)

# ---------------------------------------------------------------------
# Work (scm_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
pe = 0.96e-6
ball_eta = 0.90
weight_use = 0.70               # share of the robot weight used as push force (wheels stay loaded)
feed_push = 30.0                # mm/s while measuring (ASABE: 30 mm/s)
feed_fast = 75.0                # mm/s down to the ground and back up
read_hz = 80.0                  # load cell sampling
q_limit = 3.0e6                 # Pa: above ~3 MPa roots hardly grow (common threshold)
points_per_ha = 4.0             # grid of 50 x 50 m (estimated practice)
drive_between = 50.0            # m between points
speed = 1.2                     # m/s
t_settle = 3.0                  # s stop, GNSS fix, foot down, moisture reading
m_motor = 1.4
m_loadcell = 0.3
m_logger = 1.0
battery_wh = 1900.0
crr = 0.06
eta_drive = 0.75
p_axis = 80.0                   # W while pushing (motor driver)
MODEL_MASS = {"total_kg": 32.2}  # from build_scm.mass_properties() (update after a change of the model)


def carriage_z(tip):
    """Bottom of the carriage plate (= top of the load cell) for a cone tip height."""
    return tip + rod_len + clamp_h + loadcell[1]


def cone_area():
    return math.pi / 4.0 * (cone_d * 1e-3) ** 2
