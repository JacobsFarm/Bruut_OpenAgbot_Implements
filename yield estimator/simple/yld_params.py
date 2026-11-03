import os
import sys

# =====================================================================
# Yield estimator (simple) - parameters
# Counts and sizes the crop (cauliflower and cabbage heads, lettuce, pumpkins, plants) for the Bruut OpenAgbot
# (standard robot) and logs them per GNSS position, so the harvest can be estimated and planned per row and per week.
# The camera bridge of the mole mapper ("mole mapper/simple", imported) carries
#  - 4 RGB cameras looking down at 1.4 m, one per row (rows at 0.45 m, 4 rows = 1.8 m);
#  - 2 depth (ToF) cameras that measure the height and the visible diameter of each head;
#  - 2 LED flash bars synchronised with the cameras, so sun and shade do not change the images.
# Each plant gets a GNSS point with diameter, height and a ripeness class; summed per row and day of harvest.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "mole mapper", "simple"),
           os.path.join(ROOT_DIR, "soil compaction meter", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import mmp_params as M          # noqa: E402  (camera bridge)

robot_steer_deg = M.robot_steer_deg
robot_mass = M.robot_mass
post_y = M.post_y
bar_z = M.bar_z

# ---------------------------------------------------------------------
# Sensors on the bridge (front face of the bar, tilted forward like the mole mapper cameras)
# ---------------------------------------------------------------------
rows = 4
row_spacing = 450.0
cam_x = tuple((i - (rows - 1) / 2.0) * row_spacing for i in range(rows))     # -675 -225 225 675
cam_box = (60.0, 80.0, 70.0)
tof_x = (-450.0, 450.0)         # depth cameras between the row pairs
tof_box = (90.0, 70.0, 40.0)
led_x = ((-880.0, -720.0), (-130.0, 130.0), (720.0, 880.0))   # LED flash bars on the front face of the bar
led_len = 160.0
cam_tilt = M.cam_tilt

# ---------------------------------------------------------------------
# Work (yld_calc)
# ---------------------------------------------------------------------
g = 9.81
cam_hfov = 50.0
cam_px = 3840
cam_height = bar_z[0] - cam_box[2]
tof_hfov = 70.0
tof_px = 640
tof_err_mm = 8.0                # depth noise at 1.2 m (estimated, typical ToF)
crop_height = 300.0             # mm top of the heads above the ground
head_d = (100.0, 220.0)         # mm visible head diameter (young .. ripe cauliflower)
plant_spacing = 500.0           # mm in the row
fps = 10.0                      # flash + exposure rate
speed = 1.0                     # m/s
crr = 0.06
eta_drive = 0.75
p_sensors = 120.0               # W: 4 RGB, 2 ToF, LED bars (flash average), computer
battery_wh = 1900.0
size_cv = 0.12                  # spread of head weight at a given diameter (estimated)
# head mass from the visible diameter (cauliflower, estimated)
mass_a = 2.5e-3                  # g = a * d(mm)^b: 150 mm ~0.7 kg, 220 mm ~1.8 kg
mass_b = 2.5
MODEL_MASS = {"kg": 9.9}
