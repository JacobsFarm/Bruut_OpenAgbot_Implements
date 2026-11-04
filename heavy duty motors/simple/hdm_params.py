import math

# =====================================================================
# Heavy-duty electric motors (simple) - parameters
# A universal motor module for bought battery garden-tool motors (EGO Power+ / Greenworks class, 56-60 V brushless
# lawnmower motors, ~2 kW): an interface plate that every motor fits through a brand adapter ring, a dovetail
# receiver on the implement with a lock pin (quick change), a generic BLDC controller fed from the robot's 48 V bus
# (or, as an option, the tool's own battery in a clip). Shown on a demonstrator: a 530 mm mid-mower deck under the
# belly of the Bruut OpenAgbot (standard robot), hung from 2 rails under the lower beams with 3 cutting heights.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)
robot_lower_beam_z = (619.0, 659.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Belly rails (as on the drop-on-demand boom): 40 x 40 x 3 under the lower beams at x +-225, 4 x M10 each
# ---------------------------------------------------------------------
rail_x = 225.0
rail = 40.0
rail_y = (-595.0, 595.0)
rail_z = (robot_lower_beam_z[0] - rail, robot_lower_beam_z[0])     # 579 .. 619

# Hangers: 4 flat bars 40 x 8 from a foot under the rail down to the deck lugs, 3 hole pairs (cutting height steps)
hanger_xy = [(sx * rail_x, sy * 200.0) for sx in (-1, 1) for sy in (-1, 1)]
hanger_bar = (40.0, 8.0)
hanger_foot = (60.0, 100.0, 8.0)
height_steps = (-20.0, 0.0, 20.0)          # cutting height 40 / 60 / 80 mm
hole_pitch = 20.0

# ---------------------------------------------------------------------
# Demonstrator: mower deck, single blade 530 mm
# ---------------------------------------------------------------------
cut_h = 60.0                    # blade height (middle step)
deck_d = 600.0                  # deck outside
deck_h = 110.0                  # skirt height
deck_t = 2.5                    # steel
deck_skirt_bottom = cut_h - 25.0
deck_top = deck_skirt_bottom + deck_h          # 145
deck_c = (0.0, 0.0)
discharge = (180.0, 120.0)      # side discharge chute (x out, y width) on the right, rear half
lug = (40.0, 60.0, 8.0)         # deck lugs for the hangers (x, y, t) at the hanger positions
blade_d = 530.0
blade = (530.0, 50.0, 4.0)
blade_boss = (60.0, 25.0)       # adapter boss on the motor shaft
rollers = (60.0, 50.0)          # 2 anti-scalp rollers at the front: d, width
roller_y = 330.0

# ---------------------------------------------------------------------
# Motor module (the subject of this idea)
# ---------------------------------------------------------------------
plate = (260.0, 260.0, 8.0)     # interface plate (aluminium), slides into the receiver
pcd = 150.0                     # 4 x M8 for the brand adapter ring
dovetail = (260.0, 30.0, 12.0)  # 2 receiver rails on the deck top (x length, y width, height), 60 deg flanks
lock_pin = (12.0, 90.0)         # d, length (spring plunger with a T handle)
ring = (190.0, 12.0)            # brand adapter ring: O, thickness (different hole pattern per brand)
motor = (150.0, 115.0)          # body O, height (EGO / Greenworks 56-60 V mower motor class)
shaft = (22.2, 60.0)            # output shaft below the plate (keyed, 3/8"-24 bolt)
motor_kw = 2.0                  # continuous mechanical (estimated, class of 56 V self-propelled mowers)
motor_rpm = 3300.0              # blade speed under load
motor_kg = 4.2
controller_box = (140.0, 90.0, 60.0)    # BLDC controller (VESC 75 V class) in an IP67 box on the plate
controller_eff = 0.96
motor_eff = 0.88
bus_v = 48.0                    # robot bus (LiFePO4 16S, 51 V nominal); the motor runs at reduced top speed
motor_v = 56.0
battery_clip = (150.0, 95.0, 120.0)     # optional tool battery in its clip (56 V 5 Ah = 280 Wh)
tool_battery_wh = 280.0
cable_d = 14.0                  # 2 x 10 mm2 to the robot's bus (Anderson SB50 plug)

# ---------------------------------------------------------------------
# Mowing (hdm_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
speed = 1.0                     # m/s
overlap = 60.0                  # mm between passes
mow_w_per_m = 2000.0            # W per m cutting width in dense grass at 1 m/s (estimated)
idle_w = 250.0                  # W blade windage and losses at full speed, no grass (estimated)
tip_limit = 96.5                # m/s blade tip speed limit (ISO 5395 class)
drive_w = 300.0                 # W driving at 1 m/s on grass with the deck (estimated)
battery_kwh = 2.4
field_eff = 0.80

# from build_hdm.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 39.4, "module_kg": 7.9}
