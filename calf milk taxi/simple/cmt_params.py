import math

# =====================================================================
# Calf milk taxi (simple) - parameters
# Brings warm milk from the calf milk kitchen to the calves in their hutches and doses each calf's portion into the
# teat bucket on the hutch fence.
#  - Insulated stainless tank 80 l (inner O480 x 1.5, 40 mm PU, stainless jacket) with a stirrer and a 300 W heating
#    mat, on a base plate on 2 cross tubes over the upper beams at y +-325, in the middle of the robot.
#  - Peristaltic pump 24 V (food tube 19 x 32, ~6 l/min): dose by pump turns, self-priming, only the tube touches the
#    milk, no valves; it also pumps the cleaning water.
#  - Swing arm on the right rear: parked along -y inside the robot outline, swung out 90 degrees to +x by a worm
#    gearmotor on the pivot post; the nozzle at the tip is over the bucket at x ~900. An RFID reader at the tip reads
#    the tag on the bucket holder (which calf, which dose), a small camera checks that a bucket is there.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_steer_max = 30.0
robot_kg = 161.5
upper_beam_x = ((305.0, 345.0), (405.0, 445.0))
upper_beam_z = (659.0, 699.0)
hole_y = 325.0                  # vertical M10 grid holes in the upper beams at |y| 275, 325 .. 625
m10_hole = 10.4
stack_top = 1032.0              # front steering stacks (x +-375, y 500): keep the arm out of the front quadrants

# ---------------------------------------------------------------------
# Cross tubes and base plate
# ---------------------------------------------------------------------
bar_x = 470.0
bar = 40.0
bar_wall = 3.0
bar_z = (upper_beam_z[1], upper_beam_z[1] + bar)          # 699 .. 739
bar_bolt_x = (325.0, 425.0)
plate_x = 360.0                 # base plate x +-360, y -360 .. 360, 6 mm aluminium
plate_y = (-360.0, 360.0)
plate_t = 6.0
plate_z = (bar_z[1], bar_z[1] + plate_t)                  # 739 .. 745

# ---------------------------------------------------------------------
# Tank: inner shell O480 x 1.5, 450 high (81 l), conical bottom 30 mm to the outlet; PU 40; jacket O563 x 1.0.
# 3 feet (tube O40, 90 high) on the base plate; outlet on the side of the bottom cone (+x side) to the pump.
# ---------------------------------------------------------------------
tank_xy = (0.0, 40.0)
tank_d = 480.0
tank_t = 1.5
tank_h = 450.0
cone_h = 30.0
insul = 40.0
jacket_t = 1.0
feet_h = 90.0
foot_d = 40.0
tank_z0 = plate_z[1] + feet_h                             # 835: underside of the jacket
lid_t = 3.0
fill_d = 200.0                  # fill opening with a hinged cover
stirrer_motor = (90.0, 120.0)   # 24 V gearmotor on the lid (O, h)
paddle = (300.0, 60.0, 4.0)     # length, height, t near the bottom
outlet_d = 25.0
heater_w = 300.0

# ---------------------------------------------------------------------
# Pump on the base plate (right rear), control box (left rear)
# ---------------------------------------------------------------------
pump_xy = (200.0, -265.0)
pump_head = (150.0, 70.0)       # rotor housing O150 x 70 (axis along y)
pump_motor = (80.0, 150.0)      # O, length along +x behind the head
pump_rev_ml = 100.0             # ml per rotor turn (tube 19 mm, estimated)
pump_rpm = 60.0                 # -> 6 l/min
pump_w = 90.0
box_xy = (-200.0, -300.0)
box = (200.0, 120.0, 220.0)     # control box x, y, z
hose_od = 32.0

# ---------------------------------------------------------------------
# Swing arm: post O60 x 4 at (pivot) on the plate, worm gearmotor with vertical output on top, arm 40 x 40 x 3,
# 620 long from the pivot; nozzle at the tip pointing down; RFID reader and camera under the tip.
# arm angle 0 = parked along -y, 90 = out along +x.
# ---------------------------------------------------------------------
pivot = (320.0, 240.0)             # flange clear of the plate bolts at (325, 325)
post_d = 60.0
post_wall = 4.0
post_top = 1010.0
gm = (110.0, 90.0, 120.0)       # worm gearmotor box x, y, z on the post top
hub_z = (post_top + gm[2], post_top + gm[2] + 20.0)       # output flange
arm = 40.0
arm_wall = 3.0
arm_len = 620.0
arm_z = (hub_z[1], hub_z[1] + arm)                        # arm on the flange
nozzle_drop = 200.0             # nozzle tube down from the arm at the tip
nozzle_d = 22.0
rfid = (80.0, 80.0, 20.0)
ARM_PARK = 0.0
ARM_OUT = 90.0
arm_rpm = 3.0                   # output speed (90 degrees in 5 s)

# ---------------------------------------------------------------------
# Calves, milk, round (for cmt_calc)
# ---------------------------------------------------------------------
calves = 40
dose_l = 3.0                    # l per calf per feed (estimated)
hutch_pitch = 2.5               # m between hutches
bucket_xz = (900.0, 750.0)      # bucket centre x, rim z (on the hutch fence)
speed = 0.8                     # m/s between hutches
stop_s = 6.0                    # stop, swing out, read tag, swing back (estimated)
milk_temp = 40.0                # deg C at filling
min_temp = 36.0
air_temp = 5.0
lambda_pu = 0.025
cp_milk = 3.9                   # kJ/kgK
rho_milk = 1.03
drive_w = 200.0
stir_w = 20.0
computer_w = 20.0
battery_wh = 1900.0
cip_l = 20.0                    # cleaning water per rinse (estimated)

g = 9.81
steel = 7.85e-6
stainless = 7.9e-6
alu = 2.7e-6
pu = 0.04e-6

# from build_cmt.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 76.2, "cg": (55.0, -1.0, 1001.0)}


def tank_litres():
    r = tank_d / 2.0
    return (math.pi * r * r * tank_h + math.pi * r * r * cone_h / 3.0) / 1e6
