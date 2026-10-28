import math

# =====================================================================
# Bedding rake (simple) - parameters
# Cubicle groomer for the Bruut OpenAgbot (standard robot): a side arm on the right reaches over the curb into the
# cubicle beds, under the divider loops, with a tine rotor whose axis lies along the bed (across the alley): it covers
# the rear 1 m of the bed, where the cow lies, loosens the bedding and levels it as the robot drives along. The robot drives along the alley;
# at the row end a linear actuator swings the arm up. The barn (curb, beds, dividers) is drawn for the checks.
# Prefix "bdr" (the belt rake already uses "brk").
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
robot_outer_beam_x = 445.0
robot_mass = 160.0
robot_cg_z = 380.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Barn (for the checks and pictures): curb, cubicle beds, cantilever divider loops every 1200 mm
# ---------------------------------------------------------------------
curb_x = 620.0                  # rear edge of the beds (curb face), robot drives at this distance
bed_z = 200.0                   # bed surface above the alley
bed_len = 2300.0                # curb to neck rail post
cubicle_w = 1200.0
divider_y = (-600.0, 600.0)     # dividers in the model (the robot stands at a cubicle centre)
divider_d = 48.0                # tube O48
loop_bottom = 380.0             # bottom rail above the bed
loop_top = 1050.0
loop_rear_x = 950.0             # rear end of the loop (from the robot centre); the rear 330 mm of the bed is open

# ---------------------------------------------------------------------
# Mount: plate bracket on the outer face of the right outer upper beam (4 x M10 through the beam sides), pivot lugs
# ---------------------------------------------------------------------
bracket = (8.0, 220.0, 160.0)   # thickness (x), length (y), height (z) of the plate on the beam face
bracket_z = (560.0, 780.0)
pivot = (490.0, 760.0)          # (x, z) arm pivot axis (along y), above the beams: the crank swings over them
pivot_d = 20.0
lug_t = 10.0
lug_gap = 102.0                 # inside distance between the 2 pivot lugs (boss 100 long, crank plate on it)

# ---------------------------------------------------------------------
# Arm: rect tube 60 (y) x 40 (z) x 3 from the pivot steeply down to an elbow, then out over the bed to the head end;
# 2 hangers 8 mm (at the elbow and at the end) carry the rotor bearings
# ---------------------------------------------------------------------
arm_w = 60.0
arm_h = 40.0
head_x = 1720.0                 # end of the arm (x, work)
head_z = 470.0                  # end of the arm (z, work): under the divider loops (bed + 380 = 580)
elbow = (700.0, 520.0)          # (x, z) the arm drops steeply from the pivot to here, then runs under the loops
head_len = 820.0
hanger_t = 8.0

# ---------------------------------------------------------------------
# Rotor: tube O60 with 4 rows of spring tines O7 (tip O240), axis along x (along the bed), 48 V 400 W gearmotor at
# the outer end
# ---------------------------------------------------------------------
rotor_x = (720.0, 1690.0)       # rotor tube from .. to (x)
rotor_len = rotor_x[1] - rotor_x[0]
rotor_tube = 60.0
tip_r = 120.0
tine_d = 7.0
tine_rows = 4
tines_per_row = 16
tine_depth = 20.0               # tines into the bedding
rotor_rpm = 180.0
gm_d = 90.0
gm_len = 150.0

# Lift: a crank plate on the arm, 160 above the pivot; a 24 V 1500 N actuator lies across the robot top from a lug on
# a bearer (across the upper beams at y 0) to the crank pin; pulling swings the arm up to 40 degrees
bearer = 40.0
bearer_x = 440.0
crank_r = 160.0
act_y = 62.0                    # plane of the crank pin and the actuator (in front of the arm and the bearer)
act_base = (-100.0, 930.0)      # (x, z) base pin on the bearer lug
act_body_d = 50.0
act_rod_d = 16.0
act_stroke = 150.0
LIFT_POSES = (0.0, 20.0, 40.0)  # degrees the arm swings up (about the pivot)

# ---------------------------------------------------------------------
# Work (bdr_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
speed = 0.3                     # m/s along the cubicles
p_rotor_per_m = 250.0           # W per m of rotor in loose sawdust / chopped straw (estimated)
p_idle = 60.0
crr = 0.03
eta_drive = 0.75
battery_wh = 1900.0
row_cubicles = 40
turn_s = 60.0


def rotor_z():
    return bed_z + tip_r - tine_depth


def arm_end():
    """(x, z) of the arm end (centre of the head beam) in work."""
    return head_x, head_z
