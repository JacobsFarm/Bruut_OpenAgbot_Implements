import math

# =====================================================================
# Three-point hitch (simple) - parameters
# Category 0 three-point linkage at the rear of the Bruut OpenAgbot (standard robot), with a small cultivator as the
# implement that hangs in it (also covers the "small cultivator" idea).
# The rear toolbar of the grassland harrow / inter-row hoe carries 2 lower links (pivots under the toolbar), a top link
# bracket on top and 2 electric lift rods: 24 V actuators from lugs on the toolbar to a pin on each lower link, with a
# slot in the rod eye so the implement floats on its gauge wheels in work.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_rear_beam_y = (-575.0, -425.0)
robot_lower_beam_z = (619.0, 659.0)
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_mass = 160.0              # kg, estimated
robot_cg_y = 0.0                # estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Rear toolbar (as the grassland harrow / inter-row hoe): 80 x 80 x 4 on 2 hangers, 2 x M10 per beam
# ---------------------------------------------------------------------
tb = 80.0
tb_wall = 4.0
tb_x = (-450.0, 450.0)
tb_y = (-860.0, -780.0)
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
# Linkage, category 0 (lower pins 5/8" = O16, top pin O16, lower hitch spacing 500, mast height 350)
# ---------------------------------------------------------------------
pin_d = 16.0
lower_a = (-820.0, 380.0)       # (y, z) lower link pivot, under the toolbar
lower_ax = 280.0                # x of the lower link centre at the pivot (clear of the hanger webs at x 239..245)
lower_b = (-1270.0, 220.0)      # (y, z) lower hitch point in work
lower_bx = 260.0                # x of the link centre at the ball: inner face of the ball at x 250 (spacing 500)
link_h = 50.0                   # flat bar 50 x 20
link_t = 20.0
ball_d = 44.0
lug_t = 8.0                     # pivot lugs, 2 per link
top_c = (-820.0, 700.0)         # (y, z) top link pin on the bracket on top of the toolbar
top_bracket_x = 12.0            # inner face of the 2 bracket plates (8 mm)
mast_h = 350.0                  # category 0 mast height: top pin above the lower pins
top_link_d = 30.0               # turnbuckle tube
top_eye = (40.0, 22.0)          # eye O and width

# lift rods: 24 V actuator 3000 N, stroke 150, base on lugs on top of the toolbar, rod eye with a 40 mm slot
lift_frac = 0.6                 # rod pin at this fraction of the lower link (from the pivot)
act_x = 310.0
act_base = (-900.0, 700.0)       # behind the toolbar, on lugs leaning back from its top
act_body_d = 60.0
act_rod_d = 20.0
act_retracted = 350.0
act_stroke = 150.0
act_force = 3000.0              # per actuator
act_kg = 3.4
act_speed = 6.0                 # mm/s at 2000 N
float_slot = 40.0

lift_work = 0.0
lift_transport = 25.0           # degrees of the lower links, + = up
LIFT_POSES = (-5.0, 0.0, 12.0, 25.0)

# ---------------------------------------------------------------------
# Implement: small cultivator on a category 0 frame (drawn in the work pose, level)
# ---------------------------------------------------------------------
imp_tb = 60.0                   # toolbar 60 x 60 x 4
imp_tb_x = 510.0
imp_tb_y = (-1360.0, -1300.0)    # clear of the link balls (O44 at y -1270)
imp_lug_x = (238.0, 248.0)      # lower hitch lugs (inside the balls)
mast_bar = (10.0, 40.0)         # A-frame bars (x, y)
mast_foot_x = 150.0
tine_x = (-400.0, -200.0, 0.0, 200.0, 400.0)
tine_w = 32.0                   # S-tine flat 32 x 10
tine_t = 10.0
tine_pts = ((-1330.0, 175.0), (-1420.0, 170.0), (-1470.0, 60.0), (-1445.0, -15.0), (-1415.0, -35.0))
share_w = 100.0                 # duckfoot at the tip
share_len = 80.0
work_depth = 40.0              # light soil, shallow: the robot has ~1.1 kN of pull
wheel_d = 250.0                 # gauge wheels at the toolbar ends
wheel_w = 80.0
wheel_x = 565.0
wheel_y = -1460.0
gauge_arm_x = (510.0, 520.0)

# ---------------------------------------------------------------------
# Work (tph_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.2e-6
speed = 1.0                     # m/s
k_tine = 30e3                   # Pa: draft of a duckfoot tine per share width x depth, light soil (estimated)
mu_tyre = 0.45
crr = 0.08
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
eta_drive = 0.75
front_share_min = 0.20          # least share of the weight on the front axle to steer (estimated)
ballast_kg = 40.0               # 2 x 20 kg on the front lower beams
ballast_cg_y = 575.0
imp_cg_behind = 150.0           # cg of a general implement behind the lower pins, for the capacity (estimated)
# from build_tph.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 25.8, "mount_cg_y": -733.0, "links_kg": 10.5, "imp_kg": 28.3, "imp_cg_y": -1394.0,
              "imp_cg_z": 174.0}


def rotate_yz(p, deg, c=lower_a):
    """Point (y, z) turned about c by deg (+ = lifts a point behind the pivot)."""
    a = math.radians(-deg)
    dy, dz = p[0] - c[0], p[1] - c[1]
    return (c[0] + dy * math.cos(a) - dz * math.sin(a), c[1] + dy * math.sin(a) + dz * math.cos(a))


def lift_pin():
    """(y, z) of the lift rod pin on the lower link, work pose."""
    return (lower_a[0] + lift_frac * (lower_b[0] - lower_a[0]), lower_a[1] + lift_frac * (lower_b[1] - lower_a[1]))


def act_length(lift_deg):
    r = rotate_yz(lift_pin(), lift_deg)
    return math.hypot(r[0] - act_base[0], r[1] - act_base[1])


def top_d():
    return (lower_b[0], lower_b[1] + mast_h)


def top_link_len():
    d = top_d()
    return math.hypot(d[0] - top_c[0], d[1] - top_c[1])


def linkage(lift_deg):
    """Lower hitch point B, top hitch point D and the pitch of the implement (deg, + = nose up) at a lift angle:
    D is where the mast (B, mast_h) meets the top link (C, fixed length)."""
    b = rotate_yz(lower_b, lift_deg)
    c = top_c
    r0, r1 = mast_h, top_link_len()
    dx, dz = c[0] - b[0], c[1] - b[1]
    dist = math.hypot(dx, dz)
    a = (r0 ** 2 - r1 ** 2 + dist ** 2) / (2 * dist)
    h = math.sqrt(max(r0 ** 2 - a ** 2, 0.0))
    my, mz = b[0] + a * dx / dist, b[1] + a * dz / dist
    cands = [(my + h * dz / dist, mz - h * dx / dist), (my - h * dz / dist, mz + h * dx / dist)]
    d = max(cands, key=lambda p: p[1])
    d0 = top_d()
    pitch = math.degrees(math.atan2(d[1] - b[1], d[0] - b[0]) - math.atan2(d0[1] - lower_b[1], d0[0] - lower_b[0]))
    return b, d, pitch
