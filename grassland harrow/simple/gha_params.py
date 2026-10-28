import math

# =====================================================================
# Grassland harrow (simple) - parameters
# Rear-mounted pasture harrow for the Bruut OpenAgbot (standard robot): a levelling board spreads molehills and
# dung pats, two rows of spring tines behind it rake out moss and dead grass and work in overseeded seed.
# A rear toolbar under the rear lower beams carries two lift arms (same geometry as the push blade, mirrored);
# the harrow frame hangs on the arms and floats on the ground (actuator rod pin in a slot), lifted by a linear actuator.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_axle_y = 500.0
robot_rear_beam_y = (-575.0, -425.0)    # centres of the rear lower beams (40 x 40)
robot_lower_beam_z = (619.0, 659.0)
robot_tire_d = 430.0
robot_mass = 160.0              # kg, estimated (agbot comparison)
robot_cg_y = 0.0                # estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Rear toolbar (mirror of the front toolbar of the push blade): 80 x 80 x 4 on 2 hangers, 2 x M10 per beam
# ---------------------------------------------------------------------
tb = 80.0
tb_wall = 4.0
tb_x = (-450.0, 450.0)
tb_y = (-860.0, -780.0)         # rear of the tyre at y -715
tb_z = (450.0, 530.0)
hanger_x = 200.0
hanger_bolt_dx = 25.0
hanger_top_t = 10.0
hanger_top_w = 100.0
hanger_top_y = (-610.0, -390.0)
web_t = 6.0
web_dx = 42.0
web_pts = ((-395.0, 609.0), (-700.0, 609.0), (-890.0, 545.0), (-890.0, 440.0), (-770.0, 440.0), (-560.0, 560.0),
           (-395.0, 560.0))

# ---------------------------------------------------------------------
# Lift arms (mirror of the push blade): rect tube 60 x 40 x 3 on O20 pins in forks under the toolbar
# ---------------------------------------------------------------------
arm_x = 300.0
arm_w = 40.0
arm_h = 60.0
arm_wall = 3.0
pivot = (-840.0, 410.0)
pivot_d = 20.0
lug_t = 8.0
lug_gap = arm_w + 2.0

# ---------------------------------------------------------------------
# Harrow frame (weldment on the arm ends)
# ---------------------------------------------------------------------
main = 60.0                     # main beam 60 x 60 x 4 across
main_wall = 4.0
main_y = (-1020.0, -960.0)
main_z = (266.0, 326.0)
frame_x = 650.0                 # half working width (1300 mm, wider than the tyres: 850)
side_x = 450.0                  # 2 side members 40 x 40 x 3 back to the rear tine bar
bar = 40.0                      # tine bars 40 x 40 x 3
bar_y = (-1170.0, -1320.0)      # centres of the 2 tine bars
bar_z = (286.0, 326.0)

# Levelling board: angle 100 x 100 x 8, upright leg in front (pushes the soil), flat leg trailing (smooths); on 3 flat
# bars 60 x 8 with 4 holes (depth +-20). Trailing leg: it does not tip down when the harrow is lifted.
board_y = -1050.0               # front face of the upright leg
board_leg = 100.0
board_t = 8.0
board_depth = 15.0              # heel below the ground line in work (the board scrapes the hills, floats on the sward)
strap_x = (-500.0, 0.0, 500.0)
strap = (60.0, 8.0)

# Spring tines O8, 2 rows, clamped under the tine bars, 2 coils O50, leg trailing back
tine_d = 8.0
tine_pitch = 75.0               # per row; the second row is offset half a pitch: 37.5 mm between the tracks
coil_d = 50.0
coil_w = 2 * 2 * tine_d + 4.0   # 2 coils, double tine: coil block width
tine_tip_back = 170.0           # tip behind the bar (y), angle of the leg
tine_depth = 15.0               # tip below the ground line in work (raking into the thatch)

# ---------------------------------------------------------------------
# Lift actuator (as the push blade, mirrored): 24 V 1500 N, stroke 100, retracted 240
# ---------------------------------------------------------------------
act_base = (-700.0, 660.0)
act_rod = (-990.0, 520.0)
act_body_d = 60.0
act_rod_d = 20.0
act_retracted = 240.0
act_stroke = 100.0
act_force = 1500.0
float_slot = 40.0
act_kg = 2.6
act_speed = 10.0                # mm/s at 1000 N

lift_work = 0.0
lift_transport = 25.0           # + = harrow up
LIFT_POSES = (-4.0, 0.0, 12.0, 25.0)

# ---------------------------------------------------------------------
# Work (gha_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
speed = 1.5                     # m/s (5.4 km/h), harrowing grassland
mu_tyre_grass = 0.45            # estimated
crr_grass = 0.06
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
c_tine = 1.5                    # horizontal / vertical force of a tine raking the thatch (estimated)
mu_board = 0.6                  # board sliding on the sward (estimated)
molehill_kg = 8.0               # kg soil in an average molehill (estimated)
molehills_per_ha = 300.0
spring_rate = 1.2               # N/mm at the tip of an O8 spring tine (estimated)
eta_drive = 0.75
# from build_gha.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 22.4, "mount_cg_y": -712.0, "lift_kg": 60.4, "lift_cg_y": -1144.0, "lift_cg_z": 196.0}


def tine_x(row):
    """x positions of the tines of row 0 (front) or 1 (rear)."""
    n = int((2 * frame_x - 2 * tine_pitch) // tine_pitch) + 1
    x0 = -(n - 1) * tine_pitch / 2.0 + (0.0 if row == 0 else tine_pitch / 2.0)
    xs = [x0 + i * tine_pitch for i in range(n)]
    return [x for x in xs if abs(x) <= frame_x - 20.0]


def rotate_yz(p, deg, c=pivot):
    """Point (y, z) turned about c by deg (+ = lifts a point behind the pivot)."""
    a = math.radians(-deg)
    dy, dz = p[0] - c[0], p[1] - c[1]
    return (c[0] + dy * math.cos(a) - dz * math.sin(a), c[1] + dy * math.sin(a) + dz * math.cos(a))


def act_length(lift_deg):
    r = rotate_yz(act_rod, lift_deg)
    return math.hypot(r[0] - act_base[0], r[1] - act_base[1])
