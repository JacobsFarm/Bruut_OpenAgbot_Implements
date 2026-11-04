import os
import sys

# =====================================================================
# Pheromone trap service (simple) - parameters
# The Bruut OpenAgbot (standard robot) visits pheromone / sticky traps along the field edges on a weekly round. Each
# trap is a delta trap on a post with a pull-out drawer at the bottom (the robot-friendly trap of this implement): the
# drawer holds the sticky card and, in a clip at its front, the lure capsule. At a trap the robot stops with the post
# line 1.35 m to its right, the head on the side arm reaches out, hooks the drawer handle and pulls the drawer out
# 160 mm; a 12 MP camera with an LED ring photographs the sticky card from above (catch count by image), a revolver of
# 12 lure capsules pushes a fresh capsule into the clip when the lure is due (the old one drops into a bin on the
# head) and the drawer is pushed back. A full card is put on a work list for a person (simple variant).
# Mast, lead screw, stepper and carriage are those of the fence inspector ("fence inspector/simple", imported); the
# base plate is its own here (8 M10 in the grid holes y +-275 / +-325 of the 2 right upper beams). Instead of the
# swinging sensor arm a fixed arm tube carries a linear guide and a 24 V actuator (stroke 220) with the service head.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "fence inspector", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import fin_params as F          # noqa: E402  (mast, screw, carriage)

robot_wheel_x = F.robot_wheel_x
robot_axle_y = F.robot_axle_y
robot_steer_deg = F.robot_steer_deg
robot_mass = F.robot_mass
robot_cg = (0.0, 95.0, 543.0)
upper_beam_x = F.upper_beam_x
upper_beam_top = F.upper_beam_top
hole_y = (275.0, 325.0)         # grid holes used (both signs)

# Own base plate (the fin plate bolts at y +-300, between the grid holes)
plate_x = F.plate_x
plate_y = (-360.0, 360.0)
plate_t = F.plate_t

# Carriage centre height (fin draws the carriage at F.wire_z); range of the screw
zc_ref = F.wire_z
ZC_RANGE = F.Z_RANGE            # carriage centre 300..1100

# ---------------------------------------------------------------------
# Arm: tube 40 x 40 x 3 from the fin hinge lugs (pin + lock pin, fixed) out to arm_x1
# Linear guide MGN12 on top, actuator beside it (y +), slider with the head
# ---------------------------------------------------------------------
arm_w = F.arm_w
arm_x1 = 960.0
rail = (12.0, 8.0)              # width (y), height (z)
rail_x = (600.0, 955.0)
block = (45.0, 27.0, 13.0)      # MGN12H: length (x), width (y), height (z)
act_d = 32.0                    # actuator body
act_x = (580.0, 840.0)
act_y = 42.0                    # actuator axis beside the arm (y)
act_rod_d = 12.0
stroke = 220.0                  # head travel out
SLIDE_POSES = (0.0, 110.0, 220.0)
slide_x0 = 760.0                # slider block start (x) when retracted

# Head (on the slider, moves in x): plate, hook with servo, lure revolver, plunger, used-capsule bin, camera with LED
head_plate = (290.0, 185.0, 8.0)         # x, y, z; from slide_x0 out, y from -105
hook_x = 990.0                           # upturned hook tip x (retracted)
hook_drop = 95.0                        # hook tip below the arm centre
revolver = (90.0, 50.0)                 # d, h; 12 capsules O16 on r 30
revolver_n = 12
capsule = (16.0, 30.0)
cam_box = (50.0, 50.0, 60.0)
cam_mast_h = 230.0                      # camera above the arm centre
led_ring = (80.0, 12.0)
bin_box = (60.0, 60.0, 70.0)

# ---------------------------------------------------------------------
# Trap (render only): post line at trap_x, drawer front facing the robot
# ---------------------------------------------------------------------
trap_post_x = 1540.0
post_d = 50.0
trap_body = (230.0, 280.0, 170.0)       # x, y, z
drawer = (200.0, 250.0, 14.0)           # x, y, z
drawer_pull = 160.0                     # head goes back from stroke to stroke - pull
trap_drawer_z = F.wire_z - 90.0          # drawer bottom in the render pose (carriage at F.wire_z)

# ---------------------------------------------------------------------
# Work (phs_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
cam_px = (4000, 3000)
cam_hfov = 70.0
cam_dist = 400.0                # mm lens to the card centre (camera on the post, 55 degrees down)
card = (190.0, 240.0)           # sticky area
insect_mm = {"leek moth": 8.0, "carrot fly": 5.0, "thrips": 1.2}
px_per_insect_min = 12.0        # px across an insect for a reliable count (estimated)
act_speed = 20.0                # mm/s actuator at no load
act_force = 200.0               # N
drawer_force = 15.0             # N pull out (friction + magnet catch, estimated)
screw_lead = F.screw_lead
stepper_rpm = F.stepper_rpm
# visit
t_stop_align = 8.0              # s stop and fine-align on the trap (camera/AprilTag on the trap)
t_photo = 3.0
t_lure = 6.0
lure_weeks = 4.0                # lure life
visit_every_days = 7.0
traps = 40                      # traps on the farm
trap_spacing_m = 150.0          # along the field edges
speed = 1.2                     # m/s between traps
crr = 0.06
eta_drive = 0.75
p_sensors = 35.0                # W camera, computer, servos idle
p_act = 40.0
battery_wh = 1900.0
# from build_phs.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 27.3, "cg": (538.0, -8.0, 868.0), "carriage_kg": 8.6}
