import math
import os
import sys

# =====================================================================
# Precision seeder (simple) - parameters
# Sows row crops (sugar beet, maize, vegetables) seed by seed and logs the RTK position of every seed, so a later
# weeding pass can hoe around each plant before it is visible.
# In the category 0 three-point hitch of "three point hitch/simple" (mount, links, lift rods, and the cultivator's
# toolbar frame with its 2 gauge wheels, imported, not copied). On the toolbar: 2 seeding units on parallelograms for
# 2 rows at 500 mm and a 24 V vacuum blower. Each unit: hopper 4 l, vacuum metering disc (30 holes) turned by its own
# stepper, seed tube with an optical seed sensor, a double-disc opener between 2 depth wheels, a press wheel.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# =====================================================================

TPH_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "three point hitch", "simple")
if TPH_FOLDER not in sys.path:
    sys.path.append(TPH_FOLDER)
import tph_params as T          # noqa: E402

robot_axle_y = T.robot_axle_y
robot_mass = 161.5
tb_y = T.imp_tb_y               # implement toolbar (-1360 .. -1300)
tb_z = (T.lower_b[1] - T.imp_tb / 2.0, T.lower_b[1] + T.imp_tb / 2.0)   # 190 .. 250
lift_work = T.lift_work
lift_transport = T.lift_transport

# ---------------------------------------------------------------------
# Units: 2 rows at 500 mm (sugar beet, maize at 0.75 m needs a wider toolbar: not here)
# ---------------------------------------------------------------------
ROW_X = (-250.0, 250.0)
# parallelogram: 2 x 2 links 40 x 10, 250 long, pins O12; brackets 8 mm on the toolbar's rear face
link_len = 250.0
link_z = (240.0, 165.0)         # upper and lower link pins (horizontal links in work)
link_w = (40.0, 10.0)           # height z, thickness x (aluminium 6082)
link_dx = 55.0                  # link centre x from the unit centre
bracket_dx = 64.0               # bracket plate centre x
plate_dx = 74.0                 # unit side plate centre x (aluminium 8 mm, laser cut)
plate_t = 8.0
pin_d = 12.0
spring = (28.0, 14.0)           # down-pressure spring: coil O28 and rod O14

UNIT_Y0 = tb_y[0] - 25.0        # front link pins (-1385)
UNIT_Y1 = UNIT_Y0 - link_len    # rear link pins (-1625)

# metering: vacuum disc O180, 30 holes, in a housing O200 x 60 (axis along x), stepper NEMA 17 + 5:1 on the +x side
meter_y = -1730.0
meter_z = 450.0
meter_d = 200.0
meter_w = 60.0
disc_holes = 30
nema17 = 42.0
nema17_len = 60.0
gear17_len = 30.0
# hopper 4 l on the side plates, funnel to the meter inlet
hopper = (130.0, 170.0, 200.0)  # x, y, z
hopper_z0 = meter_z + meter_d / 2.0 + 5.0
hopper_y = meter_y + 10.0
# seed tube O22 from the meter's release point down to the opener; optical sensor ring on it
tube_d = 22.0
sensor = (40.0, 40.0, 30.0)
# double-disc opener: 2 discs O300 x 3 at a 10 degree V, depth 30 mm; depth wheels O320 x 40 beside them
opener_y = -1820.0
disc_d = 300.0
seed_depth = 30.0
disc_dx = 9.0
gauge_d = 320.0
gauge_w = 40.0
gauge_dx = 42.0                 # centre x from the unit centre (inner face at 22)
# press wheel O250 x 40 on a trailing arm behind
press_y = -2110.0
press_d = 250.0
press_w = 40.0

# vacuum blower on the toolbar centre, 2 hoses O38 to the meters
fan = (180.0, 120.0)            # volute O, height
fan_xy = (0.0, -1330.0)
vac_hose = 38.0

# ---------------------------------------------------------------------
# Seeding and logging (for psd_calc)
# ---------------------------------------------------------------------
seed_spacing = 180.0            # mm, sugar beet (final stand)
speed = 0.8                     # m/s (FarmDroid class robots sow at 0.25-0.5 m/s; 0.8 with 2 units)
row_spacing = 500.0
pass_width = 2 * row_spacing
fall_time = 0.12                # s from the release point to the furrow bottom (tube ~350 mm, estimated)
fall_jitter = 0.006             # s, 1 sigma (estimated)
bounce = 6.0                    # mm 1 sigma roll in the furrow (estimated)
rtk = 10.0                      # mm 1 sigma at the antenna
heading_err = 0.15              # degrees
antenna_to_seed = 2300.0        # mm from the robot antenna (y 575) back to the seed
sensor_jitter_ms = 1.0
miss_rate = 0.02                # singulation (estimated, pelleted beet)
double_rate = 0.02
vac_pa = 4000.0                 # vacuum at the disc
vac_q = 0.010                   # m3/s for 2 meters incl. leaks (estimated)
eta_fan = 0.4
stepper_w = 8.0
drive_w = 350.0                 # robot driving with the seeder in a seedbed (estimated)
computer_w = 30.0
battery_wh = 1900.0
field_eff = 0.80
seeds_per_unit_l = 33000.0      # pelleted beet seeds per litre (estimated)
draft_per_unit = 120.0          # N opener + press wheel (estimated)
mu_tyre = T.mu_tyre
crr = T.crr
g = 9.81
steel = 7.85e-6
pe = 0.95e-6
rubber = 1.2e-6
alu = 2.7e-6

# from build_psd.mass_properties() (update after a change of the model)
MODEL_MASS = {"implement_kg": 63.9, "implement_cg_y": -1652.0, "mount_kg": 25.8, "mount_cg_y": -733.0}


def meter_rpm():
    seeds_s = speed * 1000.0 / seed_spacing
    return seeds_s / disc_holes * 60.0
