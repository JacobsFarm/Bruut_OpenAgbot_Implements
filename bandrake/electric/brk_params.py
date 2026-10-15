import math

# =====================================================================
# Electric belt rake (band rake) in front of the robot - parameters
# A rubber belt runs around two drums with their axes along the driving direction. Tine bars on the belt carry
# spring tines; on the bottom run the tines comb the surface and carry everything sideways to the left end, where it
# is laid in a small windrow behind a swath board. A 48 V gearmotor drives the right drum.
#   - nursery beds (small trees): the tines comb 10-15 mm deep and pull out fine weed seedlings, between the trees
#   - grassland: rake out dead grass, moss and thatch before overseeding, working from the outside of the field
#     inwards so that it ends as one small windrow; or rake real hay / silage grass into small windrows
# The rake rides on two swivel castors, each on a 24 V linear actuator: they set the working depth and lift the tines
# out for the headland, so the robot never carries the rake's weight. A free parallelogram on the front of the robot
# pushes the rake, takes its side force and keeps it level; a pin along the driving direction lets it roll across.
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
robot_front = robot_axle_y + robot_tire_d / 2.0                 # 715
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)             # centres of the x-direction beams (40 x 40)
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_beam = 40.0
robot_gnss = (0.0, 575.0)       # antenna stem through the front outer beam, mount down to z 594
robot_steer_max = 30.0
robot_kg = 161.5                # agbot comparison (not weighed)
robot_cg = (0.0, 95.0, 543.0)
robot_track = 2.0 * robot_wheel_x
robot_wheelbase = 2.0 * robot_axle_y
grid = 50.0
m10_hole = 10.4
wheel_load_max = 500.0          # kg per wheel (Quinder hub motor datasheet)

# ---------------------------------------------------------------------
# Belt loop (in the x-z plane), drums with their axes along y
# ---------------------------------------------------------------------
rake_y = 960.0                  # centre of the belt (y): rear frame just in front of the steering sweep (y 721)
drum_x = 580.0                  # drum axes at x = +-580 (drive right, tension left)
drum_d = 220.0                  # drum (steel tube with crowned ends)
drum_wall = 3.0
drum_disc = 4.0                 # end discs with 4 lightening holes
drum_len = 280.0                # along y
drum_shaft_d = 30.0
belt_w = 260.0                  # rubber belt, 2 ply
belt_t = 8.0
r_pitch = drum_d / 2.0 + belt_t / 2.0      # 114: belt centre line on the drum
n_bars = 15
bar = (25.0, 25.0, 2.5)         # square tube 25 x 25 x 2.5, along y, bolted through the belt
bar_len = 250.0
n_legs = 6                      # tine legs per bar (3 double tines)
leg_pitch = 40.0                # along y
tine_wire = 5.5                 # spring steel wire
tine_coil = (32.0, 22.0)        # coil OD, length (along y) of each double tine
tine_len = 200.0                # leg length from the bar
r_tip = drum_d / 2.0 + belt_t + bar[0] + tine_len              # 343: tine tip radius on the drums

# working height: tine tips 10 mm into the soil (comb mode); for raking grass the castor actuators push 25 mm further
tip_z_comb = -10.0
tip_z_rake = 15.0
drum_z = r_tip + tip_z_comb     # 333: drum axes above the ground (comb mode, the model)
belt_len = 2.0 * (2.0 * drum_x) + 2.0 * math.pi * r_pitch      # pitch length of the loop
bar_pitch = belt_len / n_bars

# Bottom run guide: UHMW-PE strip on a steel flat, pushes the bottom run of the belt down (no sag)
guide = (1000.0, 60.0, 16.0)    # length (x), width (y), height (UHMW 10 + steel 6)
guide_z_top = drum_z - drum_d / 2.0 + 0.0  # touches the inside of the belt at the drum bottom tangent

# ---------------------------------------------------------------------
# Frame: two side plates (stadium shape, aluminium 3 mm, also the guards) on both sides of the belt, each stiffened by
# a steel tube 60 x 30 x 2 along x that carries the drum bearings; 3 cross tubes through the loop join front and rear
# ---------------------------------------------------------------------
side_t = 3.0
side_gap = 30.0                 # belt edge -> side plate
side_y = (rake_y - belt_w / 2.0 - side_gap - side_t, rake_y + belt_w / 2.0 + side_gap)  # rear plate y0, front plate y0
side_r = 175.0                  # stadium radius around the drum axes
rail = (60.0, 30.0, 2.0)        # side rail: height (z), width (y), wall; outside each side plate
rail_x = drum_x - 75.0          # rails end at x +-505, the bearing plates (150 x 150) carry on to the drum axes
brg_plate = (150.0, 150.0, 6.0) # bearing plate on the outer face of each rail end (x, z, thickness y)
bearing = (110.0, 28.0, 62.0)   # UCF206 class flange bearing: square flange, height along y, housing d
bearing_kg = 1.6
cross_x = (-380.0, 0.0, 380.0)
cross_tube = 50.0
cross_wall = 3.0
bearing_flange = (110.0, 28.0)  # UCF206 class: square flange, height along y
tension_slot = 40.0             # tension travel of the left drum bearings

# ---------------------------------------------------------------------
# Drive: 48 V BLDC gearmotor on the right drum shaft, outside the front side plate
# ---------------------------------------------------------------------
motor_d = 110.0
motor_len = 160.0
gear_box = (120.0, 120.0, 95.0) # in-line planetary gearbox: square housing x, z, length (y)
motor_P = 750.0                 # W rated
motor_rpm = 3000.0
gear_ratio = 20.0
gear_eff = 0.92
motor_eff = 0.85
motor_kg = 5.5
gear_kg = 4.0
drive_side = 1                  # +1: motor on the right drum (+x)

# ---------------------------------------------------------------------
# Casters (2) in front of the front side plate, height in holes 30 mm apart
# ---------------------------------------------------------------------
caster_x = robot_wheel_x         # 375: the castors run in the robot's own wheel tracks (free lanes in a bed)
caster_d = 200.0
caster_w = 60.0
caster_y = rake_y + belt_w / 2.0 + side_gap + side_t + rail[1] + 145.0   # 1298: wheel centre
caster_offset = 70.0            # trail: swivel axis this far in front of the wheel centre
caster_h = 236.0                # swivel plate top above the ground (Ø200 castor)
caster_kg = 4.5
caster_arm = (40.0, 40.0, 3.0)  # tube from the front rail to the actuator clamp

# castor actuators: body vertical in a clamp on the castor arm, rod down to the swivel plate
cact_body = (50.0, 240.0)       # body d, length
cact_rod_d = 20.0
cact_ext_work = 40.0            # rod out in comb mode (tine tips -10)
cact_stroke = 150.0             # rod out 0 .. 150
cact_force = 1000.0             # N each, 24 V, with hall sensor (position = working depth)
cact_speed = 30.0               # mm/s at load
cact_kg = 2.6

# ---------------------------------------------------------------------
# Swath board at the left (delivery) end
# ---------------------------------------------------------------------
board_x = -(drum_x + r_tip + 90.0)             # -1013
board_y = (rake_y - 380.0, rake_y + 260.0)
board_z = (40.0, 480.0)
board_t = 3.0
board_arm = (40.0, 450.0, 1185.0)   # tube 40 x 40: size, z, y (in front of the front rail, above the front bearing)
board_post_x = -400.0

# ---------------------------------------------------------------------
# Mount on the robot: plate under the two front lower beams, headstock with the parallelogram pins,
# parallelogram (upper and lower arm pair), rake head on the roll stub, lift actuator
# ---------------------------------------------------------------------
mount_plate = ((-160.0, 160.0), (395.0, 625.0), (robot_lower_beam_z[0] - 8.0, robot_lower_beam_z[0]))
stock_y = (400.0, 610.0)        # headstock plates under the mount plate
mount_bolt_x = (-125.0, 125.0)
gnss_hole = 40.0
stock_x = 92.0                  # headstock plates at x = +-92 (t 8)
stock_t = 8.0
pin_d = 20.0
arm_len = 295.0
pin_front_y = 440.0             # pins on the headstock (under the front beams)
pin_z = (480.0, 330.0)          # upper, lower (working position); pins are short, one per side
pin_head_y = pin_front_y + arm_len      # 735: pins on the rake head (behind the rear rail)
arm_tube = (40.0, 40.0, 3.0)
arm_x = 68.0                    # arms at x = +-68 (between the head lugs and the headstock plates)
head_x = 44.0                   # rake head lugs at x = +-44 (t 8), welded on the sides of the sleeve
stub_d = 50.0                   # roll stub (round bar welded into the centre cross tube)
head_sleeve = (80.0, 50.0)      # sleeve on the roll stub: OD, length
stub_end_y = pin_head_y - head_sleeve[1] / 2.0 - 15.0     # 695: rear end of the stub (behind the collar)
lift_travel = 100.0             # rake raised on its castors for the headland (tine tips 90 mm above the ground)
float_up = 130.0                # the parallelogram floats freely up to here (stop under the mount plate)
roll_max = 8.0                  # degrees, free roll about the stub (stops)

lower_cross_y = 640.0           # cross tube 40 x 40 between the lower arms (torsion stiffness)

# control box (48 V motor controller, actuator relay, contactor) on the upper inner beams, in front
box_x = (-280.0, 280.0)
box_y = (262.0, 378.0)
box_h = 110.0
box_base = ((-345.0, 345.0), (250.0, 390.0), 4.0)
box_bolt = ((-325.0, 325.0), (275.0, 375.0))

# ---------------------------------------------------------------------
# Operation (brk_calc and the animation)
# ---------------------------------------------------------------------
modes = {
    # speed m/s, belt m/s, tine tip z, legs count as working below z 'reach', force N per working leg, what
    "comb": {"v": 0.6, "u": 1.0, "tip_z": tip_z_comb, "reach": 5.0, "leg_N": 5.0,
             "label": "nursery bed: comb out weed seedlings"},
    "rake": {"v": 1.2, "u": 1.5, "tip_z": tip_z_rake, "reach": 40.0, "leg_N": 3.0,
             "label": "grassland: rake out moss / thatch"},
}
litter_kg_m2 = 0.10             # dead grass / moss raked out per pass in the grassland mode (kg/m2 fresh, estimated)
mu_material = 0.6               # friction of the material on the ground
bearing_loss_W = 60.0           # belt, drums and bearings
c_rr_caster = 0.10
battery_kwh = 2.4
drive_w = {"comb": 320.0, "rake": 500.0}   # W driving at the mode's speed (estimated)
field_eff = 0.80
mu_tire = 0.5                   # lateral grip of the robot tyres on soil / grass
