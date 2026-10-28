import math

# =====================================================================
# Dumper barrow (simple) - parameters
# Tipping skip on the upper beams of the Bruut OpenAgbot (standard robot): a 2 mm steel bin with a sloping rear lip on
# a subframe that hinges at the rear end of the robot; two 24 V actuators under the bin tip it backwards to 48 degrees
# and the load slides out behind the rear wheels. For soil, gravel, compost, wood chips, weeds and prunings around the
# farm; follows a person (as the crate carrier) or drives an RTK route.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_upper_beam_y = (-650.0, 650.0)
robot_front_stack_y = 405.0
robot_rear_bolts = (-584.0, -416.0, 705.0)
robot_mass = 160.0
robot_cg_y = 0.0
robot_cg_z = 380.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Bearers (tube 40 x 40 x 3 across the upper beams, 4 x M10 each): front (rest pads), actuator, hinge
# ---------------------------------------------------------------------
bearer = 40.0
bearer_x = 470.0
bearer_y = {"front": 250.0, "act": -330.0, "hinge": -620.0}
bearer_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bearer)
rest_pad = (60.0, 60.0, 10.0)   # rubber pads on the front bearer under the subframe rails

# ---------------------------------------------------------------------
# Subframe (tips with the bin): 2 rails 40 x 40 x 3 along y at x +-300, a cross tube for the actuators, hinge bosses
# ---------------------------------------------------------------------
rail_x = 270.0                  # inside the bearer bolts at x 325
rail_y = (-655.0, 330.0)
rail_z = (bearer_z[1] + rest_pad[2], bearer_z[1] + rest_pad[2] + 40.0)
hinge = (-640.0, 765.0)         # (y, z) hinge axis (along x)
hinge_pin_d = 20.0
cross_y = (150.0, 190.0)        # actuator cross tube 40 x 40 between the rails

# ---------------------------------------------------------------------
# Bin: floor on the rails, front wall, side walls, rear lip sloping out at 30 degrees from vertical
# ---------------------------------------------------------------------
bin_x = 450.0
bin_y = (-660.0, 360.0)         # floor rear edge .. front wall (45 short of the steering stacks)
bin_h = 350.0
lip_deg = 30.0
sheet = 2.0
rim = (30.0, 30.0, 3.0)         # angle round the top edge

# ---------------------------------------------------------------------
# Tipping: 2 x 24 V 3000 N actuators, stroke 300, retracted 450, from lugs under the actuator bearer to the cross tube
# ---------------------------------------------------------------------
act_x = 120.0                   # actuators at x +-120
act_base = (-270.0, 630.0)      # (y, z) base pin, on a lug hanging in front of the actuator bearer
act_rod = (170.0, rail_z[0] - 20.0)     # (y, z) rod pin under the cross tube, bin down
act_retracted = 450.0
act_stroke = 300.0
act_force = 3000.0
act_speed = 8.0                 # mm/s at load (estimated)
act_body_d = 60.0
act_rod_d = 22.0
tip_max = 48.0
TIP_POSES = (0.0, 24.0, 48.0)

# ---------------------------------------------------------------------
# Work (dmb_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.2e-6
payload_max = 150.0             # kg on top of the robot (estimated, as the crate carrier)
LOADS = {"wet_soil": 1500.0, "gravel": 1600.0, "compost": 600.0, "wood_chips": 300.0, "green_waste": 150.0}  # kg/m3
crr = 0.06
mu_tyre = 0.45
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
eta_drive = 0.75
battery_wh = 1900.0
trip_m = 100.0                  # one way (example)
load_s = 300.0                  # filling by hand / with a shovel (estimated)
dump_s = 30.0
speed_loaded = 1.0
speed_empty = 1.5
track_half = robot_wheel_x
wheelbase_half = robot_axle_y
# from build_dmb.mass_properties() (update after a change of the model)
MODEL_MASS = {"fixed_kg": 0.0, "fixed_cg": (0, 0, 0), "tip_kg": 0.0, "tip_cg": (0, 0, 0)}


def rotate(p, deg, c=hinge):
    """Point (y, z) turned about the hinge by deg (+ = tipped back: points in front of the hinge go up)."""
    a = math.radians(deg)
    dy, dz = p[0] - c[0], p[1] - c[1]
    return c[0] + dy * math.cos(a) - dz * math.sin(a), c[1] + dy * math.sin(a) + dz * math.cos(a)


def act_length(deg):
    r = rotate(act_rod, deg)
    return math.hypot(r[0] - act_base[0], r[1] - act_base[1])


def bin_volume():
    """Inside volume (m3) of the bin up to the rim."""
    h = bin_h
    L = bin_y[1] - bin_y[0]
    extra = h * math.tan(math.radians(lip_deg)) / 2.0
    return (L + extra) * h * 2 * bin_x * 1e-9
