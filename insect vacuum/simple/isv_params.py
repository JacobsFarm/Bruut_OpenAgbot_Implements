import math
import os
import sys

# =====================================================================
# Insect vacuum (simple) - parameters
# Sucks pest insects off the crop instead of spraying (lygus bugs in strawberries, Colorado beetles in potatoes).
# Push-pull under the light-tight belly hood of the drop-on-demand boom ("drop on demand boom/simple", imported: rails,
# hanger posts, hood shell, brush skirt): 2 air knives low along the sides of the bed blow across and up through the
# canopy, 2 slot nozzles over the rows suck the dislodged insects up. A strip curtain at the hood front shakes the plants.
# The suction hoses go straight up into a catch box on the upper beams with a mesh basket (insects stay in it, alive
# or dead, for counting); the fan on the lid sucks the clean air out of the box and blows it back down to the air
# knives (closed loop: no second blower, no dust thrown out).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, z 0 = bed top, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DDB_FOLDER = os.path.join(ROOT_DIR, "drop on demand boom", "simple")
SSP_FOLDER = os.path.join(ROOT_DIR, "spotspray unit", "boom")
for _f in (DDB_FOLDER, SSP_FOLDER):
    if _f not in sys.path:
        sys.path.append(_f)
import ddb_params as D          # noqa: E402  (rails, posts, hood)
import ssp_params as S          # noqa: E402

robot_wheel_x = D.robot_wheel_x
robot_axle_y = D.robot_axle_y
robot_axle_z = D.robot_axle_z
robot_tire_d = D.robot_tire_d
robot_tire_w = D.robot_tire_w
robot_lower_beam_y = D.robot_lower_beam_y
robot_lower_beam_z = D.robot_lower_beam_z
robot_steer_max = D.robot_steer_max
robot_kg = D.robot_kg
m10_hole = D.m10_hole
upper_beam_x = ((305.0, 345.0), (405.0, 445.0))
upper_beam_z = (659.0, 699.0)
hole_y = 325.0                  # vertical M10 grid holes in the upper beams at |y| 275, 325 .. 625

# ---------------------------------------------------------------------
# Hood of the drop-on-demand boom (x +-300, y +-262, skirt 60 .. top 420, brush to 10 over the bed), middle step
# ---------------------------------------------------------------------
hood_x = D.hood_x
hood_y = D.hood_y
HT = D.hood_top                 # 420
TOP_IN = HT - D.hood_t
crop_rows = D.crop_rows         # (-150, 150): 2 rows per bed
canopy_h = 250.0                # strawberry canopy top over the bed (estimated)

# ---------------------------------------------------------------------
# Suction nozzles: 2 slot nozzles over the rows, slot 25 (x) x 440 (y), mouth 50 mm over the canopy, lofted up to a
# round stub O90 through the hood top.
# ---------------------------------------------------------------------
slot_w = 25.0
slot_l = 440.0
slot_z = canopy_h + 50.0        # 300
loft_h = 80.0                   # slot -> round
stub_d = 90.0
stub_top = HT + 50.0            # 470
noz_t = 1.5
noz_y = 0.0

# ---------------------------------------------------------------------
# Air knives: 2 pipes O40 along y at x +-255, z 90, slot 8 mm x 440 facing inward-up (30 degrees over horizontal);
# risers at the rear, a cross pipe O50 under the hood top and an inlet stub O80 at (0, -215).
# ---------------------------------------------------------------------
knife_x = 255.0
knife_z = 90.0
knife_d = 40.0
knife_slot = (8.0, 440.0)
knife_angle = 30.0
riser_y = -225.0
cross_z = 375.0                 # under the post-bracket bolt nuts (z 407)
cross_d = 50.0
exh_in = (0.0, -215.0)
exh_d = 80.0

# Strip curtain at the front: PVC strips 100 x 3, hanging from a bar under the hood top at y 240 down to z 150
curtain_y = 240.0
curtain_strip = (100.0, 3.0)
curtain_z = 150.0
curtain_gap = 10.0

# ---------------------------------------------------------------------
# Catch box on the upper beams: 2 cross tubes 40 x 40 x 3 at y +-325, 2 rails 30 x 30 along y at x +-230 on them,
# stainless box 520 x 450 x 300 on the rails, 2 inlet stubs O100 in the bottom (x +-150), a mesh basket inside,
# lid with the fan. Exhaust: duct from the volute to the rear, hose O80 down to the air knives.
# ---------------------------------------------------------------------
bar_x = 470.0
bar = 40.0
bar_wall = 3.0
bar_z = (upper_beam_z[1], upper_beam_z[1] + bar)
bar_bolt_x = (325.0, 425.0)
rail_x = 230.0
rail = 30.0
rail_y = (-345.0, 345.0)
rail_z = (bar_z[1], bar_z[1] + rail)          # 739 .. 769
box_x = 260.0
box_y = (-200.0, 250.0)
box_z = (rail_z[1], rail_z[1] + 300.0)        # 769 .. 1069
box_t = 1.5
inlet_x = 150.0
inlet_d = 100.0
basket_gap = 20.0
basket_mesh = 0.8               # mm opening of the stainless mesh
lid_t = 3.0
fan_d = 320.0                   # centrifugal fan volute O320 x 120, 48 V BLDC on top
fan_h = 120.0
fan_xy = (0.0, 40.0)
fan_motor = (110.0, 130.0)
duct = (110.0, 90.0)            # outlet duct section (x, z) along -y to y -255
exh_y = -258.0                  # exhaust riser y (between the box rear wall and the cross tube)
hose_od = 100.0
exh_od = 84.0

# ---------------------------------------------------------------------
# Air flow and work (for isv_calc)
# ---------------------------------------------------------------------
rho = 1.2
Q = 0.25                        # m3/s total (both nozzles; the same air goes back to the knives)
K_slot = 1.5                    # entry loss of a slot nozzle, x dynamic pressure at the slot
dp_screen = 250.0               # Pa: mesh basket half full (estimated)
dp_hoses = 200.0                # Pa: hoses, box expansion, duct (estimated)
K_knife = 1.2                   # x dynamic pressure at the knife slot
eta_fan = 0.55
speed = 0.4                     # m/s (1.3 s under the hood per plant)
bed_pitch = 1.5                 # m: one bed per pass (bed + path)
drive_w = 250.0
computer_w = 30.0
battery_wh = 1900.0
# insects (estimated): mass mg, length mm, terminal velocity m/s
INSECTS = {"lygus_adult": (6.0, 6.0, 3.5), "lygus_nymph": (1.5, 3.0, 2.5), "colorado_beetle": (130.0, 10.0, 7.5),
           "colorado_larva_L4": (100.0, 12.0, 6.5), "ladybird_beneficial": (25.0, 6.0, 5.0)}
lift_factor = 2.0               # air speed >= this x terminal velocity to lift an insect off a leaf (estimated)

g = 9.81
steel = 7.85e-6
stainless = 7.9e-6
alu = 2.7e-6
pvc = 1.4e-6

# from build_isv.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 67.5, "cg": (0.0, -13.0, 707.0)}
