import os
import sys

# =====================================================================
# Drinking trough check (simple) - parameters
# The Bruut OpenAgbot (standard robot) visits the drinking troughs in a field at stored GNSS positions, parks with the
# trough to its right, swings a sensor head over the water and
#  - measures the water level (ultrasonic sensor looking down, +-3 mm),
#  - photographs the water and the trough (camera in the head: dirt, algae, dead animal, broken float valve),
#  - tops the trough up from its own tank (160 l, 24 V diaphragm pump, hose to a nozzle in the head) when the float
#    valve or the supply has failed.
# The mast, the carriage on the lead screw and the spring hinge come from the fence inspector ("fence inspector/simple",
# imported, not copied); only the arm is longer and carries the head. The tank sits on 2 cross bars on the left upper
# beams. Cleaning (scrubbing) is not in the simple variant.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "fence inspector", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import fin_params as F          # noqa: E402  (mast, carriage, hinge)

robot_wheel_x = F.robot_wheel_x
robot_axle_y = F.robot_axle_y
robot_steer_deg = F.robot_steer_deg
robot_mass = F.robot_mass
upper_beam_top = F.upper_beam_top
left_beams_x = (-425.0, -325.0)         # bolt lines of the left upper beams
hole_y = F.hole_y
hinge_xy = F.hinge_xy
ZC = F.wire_z                   # carriage parts are drawn at this height and moved by the Carriage placement

# ---------------------------------------------------------------------
# Arm and head (on the fence-inspector hinge): tube 40 x 40 x 3 to x 1180, head box under the arm end
# ---------------------------------------------------------------------
arm_w = 40.0
arm_x1 = 1180.0
head_x = (1120.0, 1260.0)
head_y = 160.0
head_h = 90.0                   # head box under the arm
us_d = 40.0                     # ultrasonic sensor, looking down
us_l = 50.0
cam_d = 35.0                    # camera lens, looking down and forward
nozzle_d = 22.0                 # fill nozzle (3/4"), down from the head
nozzle_l = 120.0
head_work_z = 950.0             # carriage height while measuring (arm 950, head bottom ~840)
head_park_z = 1100.0            # carriage up while driving
swing_park = 80.0               # arm swung back along the robot while driving (deg)

# ---------------------------------------------------------------------
# Tank: PE 700 x 700 x 330 (160 l) on 2 cross bars 60 x 40 x 3 at y +-300 on the left upper beams (and PE pads)
# The right upper beams carry the fence-inspector base plate, so the bars end at x 290.
# ---------------------------------------------------------------------
bar_x = (-470.0, 290.0)
bar_wh = (60.0, 40.0)
pad_h = 15.0
tank_x = (-445.0, 255.0)
tank_y = (-350.0, 350.0)
tank_h = 330.0
tank_wall = 5.0
tank_cap_d = 150.0
pump_box = (140.0, 90.0, 90.0)          # 24 V diaphragm pump, 20 l/min, on the front of the left bar

# ---------------------------------------------------------------------
# Trough (render and poses only): galvanised 1500 x 600, rim 750 high, 250 l; robot parks 300 mm beside it
# ---------------------------------------------------------------------
trough_x = (800.0, 1400.0)
trough_y = (-750.0, 750.0)
trough_h = 750.0
trough_t = 2.0
water_z = 650.0

# ---------------------------------------------------------------------
# Work (dck_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
pe = 0.95e-6
tank_l = 160.0
pump_l_min = 20.0
pump_W = 60.0
us_err = 3.0                    # mm, ultrasonic level sensor
waves_err = 4.0                 # mm, water moving (animals drinking), averaged over 5 s (estimated)
trough_area_m2 = 0.85           # inside water area of the trough at the level
cow_l_day = 80.0                # l per cow per day (lactating dairy cow, estimated)
cows = 30
visit_min = 4.0                 # minutes per trough visit without filling (park, measure, photo)
troughs = 6
route_m = 2500.0                # m driven per round of all troughs
speed = 1.2
crr = 0.06
eta_drive = 0.75
p_sensors = 15.0
battery_wh = 1900.0
# from build_dck.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 42.6, "cg_x": 230.0, "cg_y": 8.0}
