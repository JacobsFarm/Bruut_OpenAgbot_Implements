import math

# =====================================================================
# Push blade (simple) - parameters
# Front-mounted dozer / grader blade for the Bruut OpenAgbot (standard robot).
# A front toolbar under the front lower beams carries two lift arms; the arms carry a carrier frame with a king pin,
# the blade turns about the king pin (angle +-25 degrees, locked with a pin) and a linear actuator lifts the arms.
# The actuator rod end runs in a slot, so in work the blade floats on its rubber edge.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375
robot_axle_y = 500              # front axle
robot_axle_z = 215
robot_tire_d = 430
robot_tire_w = 100
robot_front_beam_y = (425.0, 575.0)     # centres of the front lower cross beams (40 x 40)
robot_lower_beam_z = (619.0, 659.0)     # bottom and top of the lower beams (world)
robot_beam = 40
robot_grid = 50                 # hole grid of the beams, M10 (hole 10.4) at x = +-125, +-175, ... +-475
robot_bracket_x = 375.0 - 114.0 # inside of the wheel bracket top plates (x 261..489)
robot_steer_deg = 30.0          # largest steering angle of the front forks
robot_mass = 160.0              # kg, estimated (agbot comparison, 4WD with battery)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Front toolbar: tube 80 x 80 x 4 across the front, welded to 2 hangers under the front lower beams.
# Same tube as the rear toolbar of the disc brushes, so other front tools (broom, rake) can use it.
# Front of the tyre in the steering sweep: y ~ 721 at axle height; the toolbar stays in front and above that.
# ---------------------------------------------------------------------
tb = 80.0
tb_wall = 4.0
tb_x = (-450.0, 450.0)
tb_y = (780.0, 860.0)
tb_z = (450.0, 530.0)

hanger_x = 200.0                # centre of each hanger (both sides): bolts at x 175 and 225 (grid holes)
hanger_bolt_dx = 25.0
hanger_top_t = 10.0
hanger_top_w = 100.0            # x 150..250, inside the wheel bracket (x 261)
hanger_top_y = (390.0, 610.0)
web_t = 6.0
web_dx = 42.0                   # webs at hanger_x +- 42
# web outline (y, z); the toolbar is cut out of it, so the webs wrap the top and front of the toolbar
web_pts = ((395.0, 609.0), (700.0, 609.0), (890.0, 545.0), (890.0, 440.0), (770.0, 440.0), (560.0, 560.0),
           (395.0, 560.0))

# ---------------------------------------------------------------------
# Lift arms: 2 x rect tube 60 x 40 x 3, pivot pin O20 in a fork of 2 x 8 mm lugs under the toolbar
# ---------------------------------------------------------------------
arm_x = 300.0                   # arm centres at x = +-300
arm_w = 40.0                    # across (x)
arm_h = 60.0
arm_wall = 3.0
pivot = (840.0, 410.0)          # (y, z) of the arm pivot axis
pivot_d = 20.0
lug_t = 8.0
lug_gap = arm_w + 2.0           # inside distance between the 2 lugs of one fork

# ---------------------------------------------------------------------
# Carrier (weldment on the arm ends): cross tube 60 x 60 x 4 and a head plate with the king pin
# ---------------------------------------------------------------------
king_y = 1060.0                 # king pin axis (x = 0) in the work position
cross = 60.0
cross_wall = 4.0
cross_x = (-330.0, 330.0)
head_d = 260.0                  # round head plate (carrier) and swivel plate (blade), both 12 mm
plate_t = 12.0
swivel_z = (240.0, 252.0)       # blade swivel plate
head_z = (254.0, 266.0)         # carrier head plate; 2 mm PE washer between them
king_d = 30.0
lock_r = 115.0                  # angle lock: pin O16 at the rear of the head plate, holes in the swivel plate
lock_d = 16.0
angle_steps = (-25.0, -12.5, 0.0, 12.5, 25.0)

# ---------------------------------------------------------------------
# Blade: steel moldboard 3 mm, curved forward, with a replaceable rubber edge (concrete) or a steel edge (soil)
# Blade frame: cutting edge on the ground at y = edge_y (angle 0)
# ---------------------------------------------------------------------
blade_w = 1100.0                # wider than the robot track over the tyres (850)
blade_h = 450.0                 # top of the moldboard
blade_t = 3.0
blade_r = 700.0                 # radius of the moldboard; vertical at the bottom, curls forward at the top
steel_bottom = 40.0             # bottom of the steel moldboard; the rubber edge reaches the ground below it
edge_y = 1290.0                 # front face of the bottom of the moldboard (world, angle 0, work)
edge_h = 110.0                  # rubber strip 110 x 15, 6 x M10 through the moldboard and a clamp bar 40 x 6
edge_t = 15.0
clamp_w = 40.0
clamp_t = 6.0
edge_bolts = 6
side_plate_t = 6.0              # end plates keep the material in front of the blade
beam_y = (-140.0, -60.0)        # blade beam (rect tube 80 x 60 x 4) relative to edge_y
beam_z = (180.0, 240.0)
beam_x = (-380.0, 380.0)
rib_x = (-300.0, 0.0, 300.0)    # ribs 8 mm between moldboard and beam
rib_t = 8.0

# ---------------------------------------------------------------------
# Lift actuator: 24 V linear actuator 1500 N, stroke 100 (via a 48/24 V converter in the robot)
# Base clevis on a lug on top of the toolbar, rod end in a slot in a lug on the carrier (float)
# ---------------------------------------------------------------------
act_base = (700.0, 660.0)       # (y, z) base clevis pin, on a mast on top of the toolbar
act_rod = (990.0, 520.0)        # (y, z) rod end pin in the work position (bottom of the float slot)
act_body_d = 60.0
act_rod_d = 20.0
act_retracted = 260.0           # pin to pin, retracted
act_stroke = 100.0
act_force = 1500.0              # N, push/pull
float_slot = 40.0               # slot length in the carrier lug: blade can follow the floor 40 mm up / down
act_kg = 2.6

# poses: lift angle of the arms (degrees, + = blade up), checked by check_poses()
lift_work = 0.0
lift_transport = 18.0
LIFT_POSES = (-4.0, 0.0, 9.0, 18.0)          # -4: hollow in the floor (float down), 18: transport

# ---------------------------------------------------------------------
# Work (for pbl_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6                 # kg/mm3
rubber = 1.3e-6
hub_torque_nom = 55.0           # Nm per Quinder 48 V 550 W hub motor (continuous)
hub_torque_peak = 97.4
r_load = 0.20                   # m, loaded tyre radius
n_driven = 4
mu_tyre = {"concrete_dry": 0.60, "concrete_manure": 0.35, "grass": 0.45, "loose_soil": 0.40}   # estimated
crr = {"concrete_dry": 0.02, "concrete_manure": 0.03, "grass": 0.06, "loose_soil": 0.10}
# material in front of the blade: density (kg/m3), friction on the floor, friction blade-material, angle of repose
MATERIAL = {
    "silage_feed": {"rho": 350.0, "mu_floor": 0.45, "repose": 45.0, "floor": "concrete_dry"},
    "manure_slurry": {"rho": 1000.0, "mu_floor": 0.25, "repose": 10.0, "floor": "concrete_manure"},
    "wet_snow": {"rho": 400.0, "mu_floor": 0.15, "repose": 35.0, "floor": "concrete_dry"},
    "loose_soil": {"rho": 1400.0, "mu_floor": 0.60, "repose": 35.0, "floor": "loose_soil", "held": True},
}
k_cut = 30e3                    # Pa, cutting resistance of loose topsoil (grading)
speed = 0.6                     # m/s working speed (2.2 km/h)


def blade_section(n=24):
    """Moldboard centre line in the blade frame (v = forward from the bottom front face, z): list of (v, z)."""
    zs = [steel_bottom + (blade_h - steel_bottom) * i / n for i in range(n + 1)]
    return [(blade_r - math.sqrt(blade_r ** 2 - (z - steel_bottom) ** 2), z) for z in zs]


def act_length(lift_deg):
    """Actuator pin-to-pin length (mm) at a lift angle of the arms."""
    a = math.radians(lift_deg)
    dy, dz = act_rod[0] - pivot[0], act_rod[1] - pivot[1]
    ry = pivot[0] + dy * math.cos(a) - dz * math.sin(a)
    rz = pivot[1] + dy * math.sin(a) + dz * math.cos(a)
    return math.hypot(ry - act_base[0], rz - act_base[1])


def edge_lift(lift_deg):
    """Height (mm) of the middle of the cutting edge above the floor at a lift angle."""
    a = math.radians(lift_deg)
    dy, dz = edge_y - pivot[0], 0.0 - pivot[1]
    return pivot[1] + dy * math.sin(a) + dz * math.cos(a)


# ---------------------------------------------------------------------
# Extra for pbl_calc
# ---------------------------------------------------------------------
robot_cg_y = 0.0                # centre of gravity of the robot (estimated: midway between the axles)
mu_edge = 0.6                   # rubber edge on concrete (estimated); the actuator can carry part of the blade
grading_cut = 20.0              # mm, cut depth of a grading pass
pile_len_max = 0.6              # m, a pile longer than this flows round the blade ends (estimated)
act_speed = 10.0                # mm/s at 1000 N (typical 1500 N actuator)
eta_drive = 0.75                # hub motor + controller at this load
# from build_pbl.mass_properties() in the work pose (update after a change of the model)
MODEL_MASS = {"mount_kg": 22.4, "mount_cg_y": 712.0, "lift_kg": 56.0, "lift_cg_y": 1197.0, "lift_cg_z": 248.0}
