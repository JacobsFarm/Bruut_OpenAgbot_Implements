import math
import os
import sys

# =====================================================================
# Barn pressure washer (simple) - parameters
# Cleans pens, walls and floors with a high-pressure jet when the barn is empty.
# The high-pressure water comes from the barn's own stationary washer (150 bar, 15 l/min, mains power) through 30 m of
# 3/8" HP hose on a powered reel on the robot: an on-board 2-3 kW pump would empty the robot battery within the hour.
# The robot carries the reel and a 3-axis nozzle: the mast, carriage (z) and arm of the fence inspector with the tilt
# head of the hedge trimmer ("landscaping tools/simple", imported, not copied); on the tilt flange a 400 mm lance with a
# rotating turbo nozzle instead of the trimmer bar. Tilt 0 = jet along +x (walls), +60 = down (floor), -45 = up.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HDG_FOLDER = os.path.join(ROOT_DIR, "landscaping tools", "simple")
if HDG_FOLDER not in sys.path:
    sys.path.append(HDG_FOLDER)
import hdg_params as H          # noqa: E402

robot_mass = 161.5
robot_steer_deg = H.robot_steer_deg
z_range = H.z_range
ZC0 = H.ZC0
tilt_x = H.tilt_x
TILT_POSES = (-45.0, 0.0, 60.0)
floor_min_z = 650.0             # arm height needed for the floor pose (lance tip stays 50 mm over the floor)
swing_max = H.swing_max

# ---------------------------------------------------------------------
# Lance on the tilt flange (where the trimmer housing sat): clamp block, lance O14 x 400 along +x, turbo nozzle
# ---------------------------------------------------------------------
clamp = (80.0, 70.0, 80.0)      # x, y, z block on the flange (centre y = housing_y of the trimmer)
lance_y = H.housing_y
lance_len = 400.0
lance_d = 14.0
turbo = (40.0, 110.0)           # rotating turbo nozzle O, length
swivel = (40.0, 50.0)           # HP swivel O, length (behind the clamp)

# ---------------------------------------------------------------------
# HP hose reel at the rear of the upper beams: drum O360 x 280 (30 m of 3/8" HP hose, OD 15), axis along x at
# y -550, z 980; 2 side plates 8 mm on 2 cross tubes 40 x 40 at y -475 / -625 (grid holes; the fence inspector's
# base plate covers y +-355 on the right beams, the front steering stacks stand at y 500); 24 V gearmotor with slip
# clutch on the left, HP rotary joint on the right.
# ---------------------------------------------------------------------
drum_d = 360.0
drum_w = 280.0
flange_d = 520.0
reel_y = -550.0
reel_z = 1010.0                 # flange bottom 750: clear of the cross tubes (top 739)
side_t = 8.0
bar_x = 470.0
bar = 40.0
bar_z = (699.0, 739.0)
BAR_Y = (-475.0, -625.0)
hose_od = 15.0
hose_len = 30.0                 # m
guide_z = 1380.0                # hose guide roller on the +y face of the mast, over the highest carriage
guide_y = 100.0                 # beside the post camera (y <= 65)

# ---------------------------------------------------------------------
# Washing (for bpw_calc)
# ---------------------------------------------------------------------
p_bar = 150.0
q_lmin = 15.0
rho = 1000.0
clean_m2_min = 1.0              # m2 per minute of soaked pen surface with a turbo nozzle (estimated)
pen = (3.0, 4.0, 1.0)           # pig pen length, width, wall height (m)
pen_change_s = 60.0
reel_w = 60.0
arm_w = 40.0                    # tilt + lift average
drive_w = 100.0
computer_w = 30.0
battery_wh = 1900.0
g = 9.81
steel = 7.85e-6
alu = 2.7e-6

# from build_bpw.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 69.4, "mount_kg": 20.1, "carriage_kg": 11.1, "reel_kg": 38.1}


def jet():
    v = math.sqrt(2.0 * p_bar * 1e5 / rho)
    m_dot = q_lmin / 60.0
    return {"v": v, "force_N": m_dot * v}
