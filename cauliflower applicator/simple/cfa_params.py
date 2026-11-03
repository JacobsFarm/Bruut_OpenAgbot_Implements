import math

# =====================================================================
# Cauliflower root-crown applicator - parameters
# Insecticide (e.g. against cabbage root fly / soil pests) is dosed in short pulses on the soil on both sides of the
# stem of every cauliflower plant, not sprayed over the crop. The robot straddles two rows (40 cm apart, plants every
# 40 cm in the row); the plants (mid-season, 25 .. 35 cm high) pass under the frame between the wheels.
#
#   Tank:      60 l on a cradle on the upper beams.
#   Plumbing:  plate on the rear lower beams: suction filter, 24 V diaphragm pump, pressure regulator with bypass,
#              small pressure accumulator (steady pressure during the pulses), control box.
#   Toolbar:   square tube 50 x 50 under the upper beams at y 275 (M10 through the beam holes).
#   Row unit:  per row a parallelogram (2 x 2 flat bars) hanging from the toolbar, carrying an arch over the row with
#              two legs on UHMW skids (ground following), leaf lifter rods in front of the legs, and per side a
#              solenoid valve with a drop tube and an angled nozzle aimed at the soil 40 mm beside the stem, inside a
#              splash shroud.
#   Trigger:   a downward distance sensor per row on the toolbar finds the crown (highest point of the plant) and the
#              robot's wheel odometry delays the pulse until the stem is at the nozzles; when a plant is missed the
#              40 cm pitch from odometry fills in.
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
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)        # x-direction beams, x -500 .. 500
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)        # y-direction beams, y -650 .. 650
robot_upper_beam_z = (659.0, 699.0)
robot_beam = 40.0
robot_steer_max = 30.0
robot_kg = 161.5                # agbot comparison (not weighed)
robot_cg = (0.0, 95.0, 543.0)   # estimated
grid = 50.0                     # M10 holes: lower beams x = +-125 .. +-475, upper beams |y| = 275 .. 625
m10_hole = 10.4
upper_bolt_x = 375.0            # hole line in the middle of the upper beams

# ---------------------------------------------------------------------
# Crop
# ---------------------------------------------------------------------
rows_x = (-200.0, 200.0)        # two rows under the robot, 400 apart, centred between the wheels
row_pitch = 400.0
plant_pitch = 400.0             # in the row
plant_h = 350.0                 # mid-season, 250 .. 350
plant_spread = 500.0            # leaf spread (diameter), leaves of neighbouring rows touch
stem_d = 35.0
target_dx = 40.0                # dose lands 40 mm beside the stem (30 .. 50)

# ---------------------------------------------------------------------
# Tank (rotomoulded PE, wall 5) on a cradle: 2 cross tubes 40 x 40 x 3 on the upper beams, rubber strips, 2 straps
# ---------------------------------------------------------------------
cradle_y = (-375.0, 325.0)      # y 275 is used by the toolbar bolts
cradle_tube = 40.0
cradle_wall = 3.0
cradle_half_len = 460.0
cradle_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + cradle_tube)     # 699 .. 739
pad_t = 5.0
tank_z0 = cradle_z[1] + pad_t   # 744
strap_w = 50.0
strap_t = 3.0
tank_wall = 5.0
tank_x = 290.0                  # half width
tank_y = (-405.0, 355.0)        # front stays behind the steering stacks (plates from y 405)
tank_h = 175.0
tank_z = (tank_z0, tank_z0 + tank_h)
tank_r = 50.0
tank_nominal = 60.0             # l (gross ~ 70 l)
fill_cap = (-180.0, 150.0, 120.0, 32.0)     # x, y, d, h
vent = (200.0, 200.0, 20.0, 45.0)
level_sensor = (200.0, -50.0, 40.0, 70.0)   # float switch / ultrasonic: x, y, d, h  (stops the pump when empty)
outlet_x = -150.0               # fittings in the rear wall, low
return_x = 150.0
wall_fitting_z = tank_z0 + 25.0
wall_fitting = (28.0, 22.0)     # d, length behind the rear wall

# ---------------------------------------------------------------------
# Pump plate on top of the rear lower beams (4 x M10), behind the tank
# ---------------------------------------------------------------------
plate_x = (-300.0, 300.0)       # inside the upper beams (x 325)
plate_y = (-600.0, -400.0)      # over both rear lower beams (centres y -575 and -425)
plate_t = 6.0
plate_z = (robot_lower_beam_z[1], robot_lower_beam_z[1] + plate_t)          # 659 .. 665
plate_bolt_x = (-275.0, 275.0)
pz = plate_z[1]

# Pump: 24 V diaphragm pump with pressure switch (Seaflo 42 / Shurflo 2088 class), 5 .. 7 l/min, 3 bar.
# Head on the left (inlet from the filter), motor to the right, axis along x.
pump_y = -505.0
pump_head = ((-200.0, -120.0), (pump_y - 40.0, pump_y + 40.0), (pz, pz + 90.0))
pump_motor = (75.0, -120.0, 20.0)   # d, x0, x1
pump_foot = ((-110.0, 10.0), (pump_y - 30.0, pump_y + 30.0), (pz, pz + 5.0))
pump_q_free = 6.0               # l/min
pump_q_2bar = 4.5               # l/min at 2 bar (estimated from typical curves)
pump_w = 70.0                   # W at 2 bar (estimated)
pump_kg = 2.2
filter_xy = (-250.0, -500.0)    # suction filter, 80 mesh (the nozzle orifice is 1.6 mm)
filter_d = 50.0
filter_h = 100.0
regulator = ((20.0, 75.0), (-480.0, -430.0), (pz, pz + 75.0))      # regulator + bypass + pressure sensor block
accumulator = (120.0, -525.0, 70.0, 150.0)  # x, y, d, h: 0.5 l pressure accumulator
box_x = (170.0, 260.0)          # control box: controller, 4-channel valve driver, sensor inputs, DC-DC 48 -> 24 V
box_y = (-560.0, -440.0)        # between the plate bolts
box_h = 130.0
hose_d = 13.0                   # 3/8" pressure hose (outside)
hose_main_z = 688.0             # main feed under the tank and the rear cradle tube (z 699)

# ---------------------------------------------------------------------
# Toolbar under the upper beams
# ---------------------------------------------------------------------
bar_y = 275.0
bar = 50.0
bar_wall = 3.0
bar_half = 440.0
bar_z = (robot_upper_beam_z[0] - bar, robot_upper_beam_z[0])               # 609 .. 659
manifold = ((-40.0, 40.0), (bar_y - bar / 2.0 - 32.0, bar_y - bar / 2.0), (bar_z[0] + 5.0, bar_z[1] - 5.0))

# Row sensor: ToF / ultrasonic distance sensor, M18, looking down on the crown, on a bracket in front of the toolbar
sensor_dy = 60.0                # sensor axis in front of the toolbar centre
sensor_y = bar_y + sensor_dy    # 335
sensor = (18.0, 70.0)           # d, length
sensor_z = (bar_z[0] - 20.0, bar_z[0] - 20.0 + sensor[1])

# ---------------------------------------------------------------------
# Parallelogram: bracket plates under the toolbar, 2 upper + 2 lower flat bars per row, head plates on the arch.
# Local per row: dx = x - row_x. Pivots: bracket at y 255, head at y 0; upper z 585, lower z 505.
# ---------------------------------------------------------------------
pl_y_bracket = 255.0
pl_y_head = 0.0
pl_len = pl_y_bracket - pl_y_head          # 255
pl_z = (505.0, 585.0)           # lower, upper pivot height (rest = working height)
plate_dx = (26.0, 34.0)         # bracket and head plates (t 8) at dx +-26 .. +-34
arm_dx = (36.0, 44.0)           # arms (flat bar 30 x 8) outside the plates
arm_h = 30.0
pin_d = 12.0
pin_dx = 50.0                   # pin length +-50 (washer + split pin)
bracket_y = (225.0, 285.0)
bracket_z = (pl_z[0] - 25.0, bar_z[0])
head_y = (-30.0, 30.0)
float_range = (-60.0, 60.0)     # head travel (mm) up/down from the working height
float_up_stop = 80.0

# ---------------------------------------------------------------------
# Arch, legs and skids (moving with the head)
# ---------------------------------------------------------------------
arch = 40.0                     # tube 40 x 40 x 3 across the row
arch_wall = 3.0
arch_z = (410.0, 450.0)         # underside 410: crop up to 350 passes, taller leaves are lightly brushed
arch_half = 180.0
leg_dx = (160.0, 170.0)         # leg flat bar 50 x 10
leg_y = (-25.0, 25.0)
skid_dx = (145.0, 185.0)        # UHMW-PE runner 40 wide
skid_y = (-150.0, 120.0)
skid_t = 15.0
skid_nose = (120.0, 185.0, 60.0)   # nose from y 120 to 185, rising to z 60
leg_z = (skid_t, arch_z[0])
gusset = 60.0                   # corner gussets leg / arch

# Leaf lifters: spring steel rod D10 per side, from a low tip near the stem line in front, rising backwards and
# outwards to the leg. They slide under the lower leaves and lift them away from the stem base before the nozzle.
lifter_d = 10.0
lifter_tip = (70.0, 215.0, 30.0)    # dx, y, z
lifter_mid = (120.0, 120.0, 120.0)
lifter_end = (160.0, 25.0, 200.0)   # on the front face of the leg

# Valve + drop nozzle per side, behind the leg (y -40). Bracket flat bar on the leg back face, slotted (dx 50 .. 90).
nz_y = -46.0
valve_dx = 85.0
vbr_z = (200.0, 236.0)          # valve bracket
vbr_t = 6.0
valve_body = (30.0, 30.0, 40.0)     # x, y, z (brass 2/2 direct-acting, 1/4", 24 V, ~10 ms)
valve_z0 = vbr_z[0] - 8.0
coil = (30.0, 32.0)             # d, h on top of the body
drop_d = 8.0                    # stainless drop tube
nozzle_angle = 30.0             # from vertical, aimed inward at the stem side
tip_z = 35.0                    # nozzle tip above the soil
tip_len = 45.0                  # angled tip
shroud = (30.0, 1.5, 55.0)      # splash shroud: od, wall, length (coaxial with the tip, 10 past it)
valve_ms = 10.0                 # opening time (estimated)
kg_valve = 0.35

# ---------------------------------------------------------------------
# Operation (cfa_calc)
# ---------------------------------------------------------------------
speed = 0.5                     # m/s
pressure = 2.0                  # bar at the valves
orifice = 1.6                   # mm, solid-stream orifice in the nozzle
cd = 0.65                       # discharge coefficient
dose_ml = 2.0                   # ml per side, per plant (4 ml per plant)
pulse_min_ms = 40.0
field_eff = 0.75                # headlands, refills
battery_kwh = 2.4
drive_w = 300.0                 # W driving on soil at 0.5 m/s (estimated)
controller_w = 15.0
valve_w = 8.0                   # W per open valve
sensor_lead = sensor_y - nz_y   # 381: distance sensor -> nozzles
skid_mu = 0.4                   # UHMW on moist soil
liquid_density = 1.0
