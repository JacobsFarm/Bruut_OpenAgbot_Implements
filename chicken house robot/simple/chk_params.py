import os
import sys

# =====================================================================
# Chicken house robot (simple) - parameters
# The Bruut OpenAgbot (standard robot) drives slowly through a broiler or layer house:
#  - turns the litter with a tine rotor in the broom head ("broom sweeper/simple", imported, on the push-blade arms):
#    the PP bristle roller is swapped for a core with 6 rows of spring tines O6, tip circle O360, so the tips work the
#    litter (60 mm on the concrete floor) down to 10 mm above the floor and never touch the concrete; the BLDC runs at
#    150 rpm. Turning loosens caked litter, dries it and lowers ammonia;
#  - measures the climate at bird height with a sensor box under the rear lower beam (NH3, CO2, temperature, relative
#    humidity, through a small fan inlet at 300 mm);
#  - watches the flock with a 360 degree camera on a post at 1.4 m (distribution, dead or lame birds, floor eggs with a
#    GNSS-less position from the house's UWB beacons).
# Floor eggs are logged, not picked up, in the simple variant.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "broom sweeper", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import bsw_params as S          # noqa: E402  (broom head, brush axis and drive)

robot_steer_deg = S.robot_steer_deg
robot_mass = S.robot_mass
rear_beam_y = (-595.0, -555.0)  # rear outer lower beam (x direction), z 619..659
lower_beam_z = (619.0, 659.0)
bolt_x = (-225.0, -175.0, 175.0, 225.0)     # grid holes in the lower beams used for the brackets
upper_beam_top = 699.0
hole_y = 325.0                  # upper-beam grid hole line used for the camera post bar

# ---------------------------------------------------------------------
# Tine rotor (replaces the bristles; same core, stub shafts and bearings as the broom)
# ---------------------------------------------------------------------
axis = (S.axis_y, S.axis_z)
core_d = S.core_d
tine_d = 6.0
tip_r = 180.0                   # tip circle O360
tine_rows = 6
tines_per_row = 10
tine_x0 = -450.0                # first tine (x), step along x
tine_step = 100.0
litter_depth = 60.0

# ---------------------------------------------------------------------
# Sensor box under the rear outer lower beam: 2 hangers (flat 40 x 6) down to a box at bird height
# ---------------------------------------------------------------------
hanger_x = (-200.0, 200.0)
box = (300.0, 120.0, 150.0)     # x, y, z
box_y0 = -700.0                 # behind the rear beam
box_z0 = 300.0                  # inlet at bird height
inlet_d = 30.0

# Camera post: tube 40 x 40 x 3 on a flat bar 8 mm across the inner upper beams at y -325
bar_x = (-345.0, 345.0)
bar_w = 60.0
post = (40.0, 1400.0)           # width, top height
cam360 = (110.0, 90.0)          # O, height

# ---------------------------------------------------------------------
# Work (chk_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rotor_rpm = 150.0               # BLDC at ~40 % of the broom speed (1000 W motor at ~80 %)
speed = 0.3                     # m/s among the birds
overlap = 100.0
k_litter = 4000.0               # N/m2 of tine-swept face: resistance of caked litter (estimated)
tine_engaged = 0.05             # m of the tine length in the litter
eta_drive_tool = 0.70
house = (100.0, 15.0)           # m broiler house
birds_m2 = 18.0
bird_escape = 0.5               # m/s a broiler walks away from a slow object (estimated)
crr = 0.04                      # on litter over concrete
eta_drive = 0.75
p_sensors = 25.0
battery_wh = 1900.0
nh3_limit_ppm = 20.0
