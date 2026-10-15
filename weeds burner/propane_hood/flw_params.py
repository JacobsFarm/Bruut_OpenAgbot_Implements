import math

# =====================================================================
# Propane flame weeder with a hood, behind the robot - parameters
# Pre-emergence flaming of freshly sown beds (carrot, onion, beetroot, ...): a few days before the crop comes up, the
# hood passes over the bed and the flames kill every weed seedling that has already emerged; the crop seed lies
# 10-20 mm deep and is not touched. The soil is not moved, so no new weed seeds are brought up.
#   - hood 1.5 m wide (one bed), 0.8 m long, insulated top, 6 flat-flame burners at the front, aimed back and down
#   - two 18 kg forklift cylinders (liquid withdrawal) on the robot; the liquid evaporates in a coil inside the hood
#   - main and burner solenoid valves, pressure regulator and sensor, pilot flames with spark igniters, flame sensors
#   - the hood rides on two steel swivel castors; a free parallelogram on the rear of the robot pulls it and keeps it
#     in line; in the headland the main valves close (pilots stay on) and the hood follows the robot on its castors
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres at (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_tire_rear_y = -robot_axle_y - robot_tire_d / 2.0         # -715
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)             # centres of the x-direction beams (40 x 40)
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_beam = 40.0
robot_kg = 161.5                # agbot comparison (not weighed)
robot_cg = (0.0, 95.0, 543.0)
robot_track = 2.0 * robot_wheel_x
robot_wheelbase = 2.0 * robot_axle_y
grid = 50.0
m10_hole = 10.4
wheel_load_max = 500.0

# ---------------------------------------------------------------------
# Hood (behind the robot): 1.5 mm steel skin (top, side walls, front and rear wall), 25 mm ceramic-fibre blanket on the
# top inside, 0.8 mm aluminium cover on top. Open at the bottom; the rear wall stops higher (exhaust slot).
# ---------------------------------------------------------------------
work_w = 1500.0                 # one bed (1.5 m track)
hood_x = work_w / 2.0 + 20.0    # 770: outside of the side walls
hood_y = (-1730.0, -930.0)      # rear wall .. front wall (front 215 mm behind the rear tyres)
hood_h = 260.0                  # top of the skin above the ground
hood_gap = 25.0                 # side and front walls end this far above the ground
exhaust_gap = 70.0              # rear wall ends this far above the ground: the hot gas leaves at the rear
skin = 1.5
blanket = 25.0
cover = 0.8
cover_gap = 15.0                # air gap between blanket and the aluminium top cover (spacers)
front_shield = (4.0, 30.0)      # aluminium heat shield in front of the front wall: thickness, air gap
shield_top = 270.0
rib = (30.0, 30.0, 3.0)         # angle 30 x 30 x 3: stiffeners along the top edges

# ---------------------------------------------------------------------
# Burners: 6 flat-flame burners (250 mm flame width each) on a manifold along the front wall, aimed back and down
# ---------------------------------------------------------------------
n_burners = 6
burner_pitch = work_w / n_burners   # 250
burner_x = tuple(-work_w / 2.0 + burner_pitch * (i + 0.5) for i in range(n_burners))
burner_y = hood_y[1] - 90.0     # nozzle mouth (-1020)
burner_z = 165.0
burner_angle = 40.0             # degrees below horizontal, aimed to the rear
burner_body = (210.0, 70.0, 34.0)   # mouth width (x), length along the axis, height
burner_kW = 28.0                # per burner at 2 bar (catalogue class of flame-weeding burners, ~2.2 kg/h)
burner_kg_h_2bar = 2.17         # propane per burner at 2 bar (estimated from the catalogue class)
manifold_d = 22.0               # steel pipe 1/2", along x behind the burners
manifold_y = hood_y[1] - 15.0     # -945, just behind the front wall
manifold_z = 221.0
manifold_feed_x = -300.0
flame_len = 320.0               # visible flame length (for the drawings)

# pilot flame + spark igniter + flame sensor (thermocouple) per burner
pilot = (12.0, 50.0)            # pilot tube d, length
igniter = (10.0, 60.0)

# Vaporiser: stainless tube 12 x 1, serpentine above the flames, behind the burners
coil_d = 12.0
coil_passes = 4
coil_x = 600.0                  # +-
coil_y0 = hood_y[1] - 150.0     # first pass, then every 40 mm to the rear
coil_pitch = 40.0
coil_z = 225.0

# ---------------------------------------------------------------------
# Castors (2): steel wheels (heat), swivel, outside the side walls at the hood's centre of gravity
# ---------------------------------------------------------------------
caster_x = hood_x + 70.0        # 840
caster_y = -1210.0              # wheel centre, under the hood's centre of gravity (no pitch moment)
caster_offset = 60.0            # swivel axis this far in front of the wheel
caster_d = 200.0
caster_w = 50.0
caster_h = 236.0                # swivel plate top
caster_holes = 3                # height: hood edge 10 / 25 / 40 mm above the soil
caster_kg = 5.0
caster_arm = (40.0, 40.0, 3.0)  # tube from the side wall rib out to the swivel

# ---------------------------------------------------------------------
# Mount: plate under the two rear lower beams, headstock plates, free parallelogram to the hood front
# ---------------------------------------------------------------------
sub_plate = ((-170.0, 170.0), (-625.0, -395.0), (robot_lower_beam_z[0] - 8.0, robot_lower_beam_z[0]))
sub_bolt_x = (-125.0, 125.0)
stock_x = 92.0                  # headstock plates at x = +-92 (t 8)
stock_t = 8.0
stock_y = (-600.0, -420.0)
pin_d = 20.0
pin_rear_y = -640.0             # pins on the headstock (behind the rear beams)
pin_z = (470.0, 320.0)          # upper, lower
arm_len = 270.0
pin_hood_y = pin_rear_y - arm_len               # -910: pins on the hood bracket
arm_tube = (40.0, 40.0, 3.0)
arm_x = 68.0
hood_lug_x = 44.0
float_range = (-60.0, 80.0)     # free float of the parallelogram (stops)

# Gas train. On the robot, under the sub plate between the headstock plates: liquid filter, two main solenoid valves
# (liquid LPG, normally closed), hose to the hood. On the hood front, behind the shield: vaporiser outlet, regulator
# (0.5 - 4 bar, motorised), pressure sensor, burner solenoid valve, pilot regulator and valve.
valve = (40.0, 45.0, 60.0)      # solenoid valve body x, y, z
panel_y = (-560.0, -440.0)
regulator = (70.0, 60.0)        # d, length (along x)
hose_d = 14.0

# ---------------------------------------------------------------------
# Gas: two 18 kg forklift cylinders lying along y on a cradle on the upper beams (liquid withdrawal: the valve end is
# turned down with the locating pin, the dip tube takes liquid)
# ---------------------------------------------------------------------
cyl_d = 300.0
cyl_len = 720.0                 # body incl. the domed ends
cyl_x = (-165.0, 165.0)
cyl_y = (-360.0, 360.0)         # valve end at the rear
cyl_kg_gas = 18.0
cyl_kg_tare = 15.5              # steel forklift cylinder (estimated)
collar = (190.0, 120.0)         # protective collar at the valve end: d, length
cradle_y = (-275.0, 275.0)      # two cross channels on the upper inner beams (M10 into the holes |y| 275 .. 625)
cradle = (40.0, 60.0, 4.0)      # channel height, width, wall
cradle_half = 360.0
saddle_t = 6.0
strap = (40.0, 2.0)

# ---------------------------------------------------------------------
# Propane and the process (flw_calc and the animation)
# ---------------------------------------------------------------------
lhv = 46.3                      # MJ/kg propane
latent = 0.36                   # MJ/kg heat of evaporation at ~10 C
vapour_bar = ((-10.0, 2.4), (0.0, 3.7), (10.0, 5.3), (20.0, 7.4), (30.0, 9.8))   # cylinder temp C, bar(g)
burner_bar = 2.0                # working pressure at the burners
speed = 0.7                     # m/s (2.5 km/h)
dose_target = 35.0              # kg propane per ha (hooded, small seedlings: cotyledon to 2 leaves)
lethal_kJ_m2 = (60.0, 120.0)    # energy on the soil surface that kills cotyledon .. 4-leaf seedlings (estimated)
hood_eff = 0.65                 # share of the burner heat that reaches the soil surface / seedlings under a hood
seed_depth = 15.0               # crop seed depth (carrot 10-20 mm)
field_eff = 0.85
battery_kwh = 2.4
drive_w = 300.0                 # W driving at 0.7 m/s on a seedbed (estimated)
control_w = 25.0                # valves, igniters, sensors, controller
gas_price = 1.6                 # EUR per kg (forklift propane, estimated)
