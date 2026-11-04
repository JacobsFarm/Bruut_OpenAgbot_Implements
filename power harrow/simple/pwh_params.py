import math
import os
import sys

# =====================================================================
# Power harrow / rotary tiller (simple) - parameters
# A narrow rotary tiller for seedbeds in strips and for loosening the soil between rows, in the category 0
# three-point hitch of "three point hitch/simple" (mount, links, lift rods, toolbar frame and its 2 gauge wheels,
# imported). Behind the toolbar: a 700 mm rotor with L-blades (4 flanges x 4 blades, O350) under a hood, driven by a
# 48 V gearmotor through a chain case on the right; a rubber front skirt and a hinged rear levelling flap.
# The rotor turns forward (down-cut, like a tractor tiller): it pushes the light robot forward instead of pulling it
# back. The gauge wheels of the hitch frame set the depth.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Implement parts are drawn in the work pose (lift 0); the hitch rotates them for other lift angles.
# =====================================================================

TPH_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "three point hitch", "simple")
if TPH_FOLDER not in sys.path:
    sys.path.append(TPH_FOLDER)
import tph_params as T          # noqa: E402

robot_axle_y = T.robot_axle_y
robot_mass = 161.5
robot_battery_kwh = 1.9
tb_y = T.imp_tb_y               # toolbar -1360 .. -1300
tb_z = (T.lower_b[1] - T.imp_tb / 2.0, T.lower_b[1] + T.imp_tb / 2.0)   # 190 .. 250
lift_work = T.lift_work
lift_transport = T.lift_transport

# ---------------------------------------------------------------------
# Rotor
# ---------------------------------------------------------------------
depth = 60.0                    # working depth below the surface (set by sliding the rotor in the side plate slots)
rotor_d = 350.0                 # blade tip circle
rotor_y = -1580.0
rotor_z = rotor_d / 2.0 - depth  # 115
work_w = 700.0
flange_x = (-270.0, -90.0, 90.0, 270.0)
flange = (180.0, 10.0)          # flange O, thickness
blades_per_flange = 4
blade = (60.0, 7.0)             # width (tangential), thickness
blade_r0 = 55.0                 # blade root radius (bolted to the flange)
blade_bend = 60.0               # L-tip bent sideways (alternating left / right)
tube = (60.0, 5.0)              # rotor tube O60 x 5
shaft_d = 40.0
rotor_rpm = 250.0

# ---------------------------------------------------------------------
# Housing
# ---------------------------------------------------------------------
side_x = (357.0, 362.0)         # side plates 5 mm (skid at the bottom)
side_r = 228.0
hood_r = (218.0, 220.0)         # hood 2 mm, from the front (0 deg = +y) over the top to the rear (180 deg)
hood_a = (0.0, 180.0)
hood_x = 357.0
skirt = (6.0, 20.0)             # front rubber skirt: thickness, bottom height above the ground
flap = (700.0, 140.0, 4.0)      # rear levelling flap: width x, length, thickness (tip ~10 mm above the surface)
flap_angle = 40.0               # degrees from vertical, trailing
flap_hinge_d = 16.0
bracket_x = (-200.0, 200.0)     # 2 brackets 10 mm toolbar -> hood top
bracket_t = 10.0
bracket_top = 360.0

# ---------------------------------------------------------------------
# Drive: gearmotor on the hood, chain case on the right
# ---------------------------------------------------------------------
case_x = (side_x[1], side_x[1] + 40.0)    # 362 .. 402, bolted to the right side plate
motor_z = 480.0                 # motor / upper sprocket axis
motor_d = 120.0
motor_x = (140.0, 300.0)        # motor body along x (inboard)
gear_x = (300.0, case_x[0])     # gearbox between the motor and the chain case
gear = (110.0, 130.0)           # gearbox y, z
sprocket_d = 110.0
bearing_d = 95.0                # left bearing housing O95
motor_w = 1500.0                # rated (48 V BLDC, estimated)
motor_kg = 9.0
gear_ratio = 12.0               # 3000 / 250 rpm, chain 1:1
chain_eff = 0.95
gear_eff = 0.9

# ---------------------------------------------------------------------
# Operation (pwh_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.2e-6
speed = (0.10, 0.20)            # m/s working speed range
specific_energy = (60.0, 150.0)  # kJ/m3 tilled (loose sandy loam .. firm loam, estimated for a shallow tiller)
drive_w = 250.0                 # robot drive with the tiller pushing (estimated)
electronics_w = 40.0
mu_tyre = 0.5
thrust_share = 0.3              # share of the blade tangential force that pushes forward (estimated)

# from build_pwh.mass_properties() (update after a change of the model)
MODEL_MASS = {"implement_kg": 93.9, "implement_cg_y": -1547.0, "mount_kg": 25.8, "mount_cg_y": -733.0}
