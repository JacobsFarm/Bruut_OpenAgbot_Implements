import os
import sys

# =====================================================================
# Asparagus harvester (simple) - parameters
# A module under the belly of the Bruut OpenAgbot (standard robot) that straddles one ridge of white asparagus: the
# wheels run in the furrows, a camera hood at the front looks at the ridge top for spear tips that crack the soil, and
# a cutting tool on an X-Z gantry goes 220 mm into the ridge, cuts the spear and lifts it out.
#   - belly rails 40 x 40 under the lower beams at x +-225 (imported from the flail mulcher)
#   - X: a gantry 40 x 40 at y 0 under the rails with a HGR15 rail, carriage travel x +-120 (NEMA 23 + belt)
#   - Z: a 40 x 80 profile behind the gantry from z 380 to 1450 (no beams at y 0, x +-150), a slide with a knife tube
#     O30 and a 2-finger gripper, stroke 820 (tip z 180 .. 1000)
#   - a spear bin on the slide; at the top it empties to the rear into a crate on a deck on the upper beams
#   - camera hood with LED and a line laser at the front, between the gantry and the front lower beams
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground (furrow bottom) = z 0, mm.
# =====================================================================

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (os.path.join(_ROOT, "spotspray unit", "boom"), os.path.join(_ROOT, "flail mulcher", "simple")):
    if _p not in sys.path:
        sys.path.append(_p)
import flm_params as F          # noqa: E402  (belly rails)

robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_lower_beam_z = (619.0, 659.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
robot_battery_kwh = 1.9
m10_hole = 10.4

rail_x = F.rail_x
rail_z = F.rail_z               # 579 .. 619

# ---------------------------------------------------------------------
# Ridge (render and checks)
# ---------------------------------------------------------------------
ridge_base = 600.0              # between the tyres (inner faces at x +-325)
ridge_top_w = 260.0
ridge_h = 400.0
row_spacing = 1.8               # m

# ---------------------------------------------------------------------
# X gantry
# ---------------------------------------------------------------------
gantry_z = (rail_z[0] - 40.0, rail_z[0])        # 539 .. 579
gantry_x = (-rail_x - 20.0, rail_x + 20.0)
gantry_y = (-20.0, 20.0)
hanger = (60.0, 8.0)            # plates under the rails at the gantry ends (y length, t)
lin_rail = (15.0, 15.0)         # HGR15 on the rear face
x_travel = 120.0
carriage = (120.0, 10.0, 140.0)  # x, y, z plate
x_motor = (57.0, 76.0)          # NEMA 23 square, length

# ---------------------------------------------------------------------
# Z axis
# ---------------------------------------------------------------------
z_prof = (40.0, 80.0)           # x, y
z_prof_y = (-125.0, -45.0)
z_prof_z = (430.0, 1450.0)      # bottom above the ridge top (400)
slide = (80.0, 10.0, 150.0)
tube_d = 30.0
tube_len = 380.0
tube_y = -165.0
tip_work = 180.0                # 220 mm below the ridge top: cut depth
tip_top = 1000.0
gripper = (12.0, 60.0)          # finger thickness, length
z_motor = (57.0, 76.0)

# ---------------------------------------------------------------------
# Spear bin on the slide, crate on the rear deck
# ---------------------------------------------------------------------
bin_box = (120.0, 70.0, 130.0)  # x, y, z (behind the tube)
bin_dz = 390.0                  # bin bottom above the tube tip
cross_y = (-625.0, -375.0)
cross = (60.0, 40.0, 3.0)
cross_half = 470.0
deck = ((-320.0, 320.0), (-660.0, -260.0), 4.0)
crate = ((-300.0, 300.0), (-650.0, -270.0), 240.0)   # 600 x 380 x 240, ~25 kg of spears

# ---------------------------------------------------------------------
# Camera hood
# ---------------------------------------------------------------------
hood = ((-160.0, 160.0), (120.0, 330.0), (450.0, rail_z[0] - 8.0))  # under a plate on the rails, open at the bottom
hood_plate_t = 8.0

# ---------------------------------------------------------------------
# Operation (asp_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
z_speed = 0.5                   # m/s
x_speed = 0.3
grip_cut_s = 1.2
spears_per_m = 3.0              # per harvest day (plants at 0.3 m, ~1 spear per plant per day, estimated)
move_s_per_m = 3.0              # robot moves at ~0.33 m/s between stops
spear_g = 25.0
power_w = 250.0                 # drive at creep + axes + computer
field_ha = 1.0

# from build_asp.mass_properties()
MODEL_MASS = {"total_kg": 43.7, "cg": (8.0, -142.0, 727.0)}
