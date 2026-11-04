import os
import sys

# =====================================================================
# Flail mulcher (simple) - parameters
# Shreds tough grass, stubble, crop residues and thin prunings between the rows. The mulcher hangs under the belly of
# the Bruut OpenAgbot (standard robot), between the wheels, so its mass sits between the axles (no ballast) and the
# robot's own wheels run beside the strip.
#   - 2 belly rails 40 x 40 x 3 under the lower beams at x +-225 (grid holes, 4 x M10 each), like the drop-on-demand
#     boom and the insect vacuum
#   - housing (steel 3 mm top, 6 mm side plates) x +-300, y +-262: a flail rotor O320 (Y-knives on shackles, 4 rows)
#     at 2700 rpm (45 m/s tips), a shear bar, a rear roller O140 that sets the cutting height (40 mm), front skids and a rubber flap
#   - a 48 V 2 kW motor on the housing top with a poly-V belt on the right side (0.9 : 1)
#   - 4 guide posts in sleeves on the rails and 2 linear actuators: the housing floats on its roller in work and lifts
#     100 mm for driving to the field
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

_HERE = os.path.dirname(os.path.abspath(__file__))
SSP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "spotspray unit", "boom")
if SSP_FOLDER not in sys.path:
    sys.path.append(SSP_FOLDER)

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
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
robot_battery_kwh = 1.9
m10_hole = 10.4

# ---------------------------------------------------------------------
# Belly rails
# ---------------------------------------------------------------------
rail_x = 225.0
rail = 40.0
rail_wall = 3.0
rail_y = (-595.0, 595.0)
rail_z = (robot_lower_beam_z[0] - rail, robot_lower_beam_z[0])     # 579 .. 619
rail_bolt_y = robot_lower_beam_y

# ---------------------------------------------------------------------
# Housing
# ---------------------------------------------------------------------
hood_x = 300.0                  # half width outside the side plates
hood_y = (-262.0, 262.0)        # 29 mm to a front tyre at 30 deg (drop-on-demand boom check)
side_t = 6.0
top_t = 3.0
cut_h = 40.0                    # flail tips above the ground
rotor_d = 320.0                 # flail tip circle
rotor_y = 70.0
rotor_z = cut_h + rotor_d / 2.0  # 200
top_z = rotor_z + rotor_d / 2.0 + 25.0          # underside of the top sheet (385)
front_wall_z = 110.0            # front wall bottom; a rubber flap below it to z 30
flap_z = 30.0
rear_wall_z = 175.0             # rear wall bottom (the roller closes the rest)
skid = (40.0, 160.0, 8.0)       # front skids under the side plates: x, y, t (bottom at z 15)
skid_z = 15.0

# rotor
rotor_tube = (108.0, 6.0)       # O108 x 6
rotor_len = 2 * (hood_x - side_t) - 40.0        # tube length between the side plates (548)
shaft_d = 35.0
flail_rows = 4
flail_pitch = 60.0              # sets per row along x, rows staggered by pitch / 4
knife = (40.0, 5.0)             # Y-knife blade width, thickness (2 per shackle)
lug = (30.0, 12.0, 25.0)        # shackle lug on the tube: x, y(t), height
rotor_rpm = 2700.0
shear_bar = (40.0, 6.0)         # angle 40 x 40 x 6 behind the rotor

# rear roller
roller_d = 140.0
roller_wall = 4.0
roller_y = -185.0
roller_z = roller_d / 2.0
roller_len = 2 * (hood_x - side_t) - 20.0

# ---------------------------------------------------------------------
# Drive (right side)
# ---------------------------------------------------------------------
motor_d = 130.0
motor_len = 170.0
motor_z = top_z + top_t + motor_d / 2.0 + 2.0   # 455: lifted, the shaft passes 6 mm under the rails
motor_y = rotor_y
motor_x = (30.0, 30.0 + motor_len)            # between the rails (inside x 205), shaft out to the right belt
belt_case = (hood_x, hood_x + 30.0)             # x range of the belt guard on the outside of the right side plate
pulley = (90.0, 100.0)          # motor pulley d, rotor pulley d (3000 -> 2700 rpm)
motor_w = 2000.0                # rated (48 V BLDC, estimated)
motor_rpm = 3000.0
motor_kg = 11.0
belt_eff = 0.95

# ---------------------------------------------------------------------
# Lift: 4 guide posts in sleeves on the outside of the rails, 2 actuators at y 0
# ---------------------------------------------------------------------
guide_x = rail_x + rail / 2.0 + 4.0 + 20.0      # 269: post centre, sleeve on a 4 mm plate on the rail outer face
guide_y = (-190.0, 190.0)
post = (30.0, 2.0)
sleeve = (40.0, 3.0, 70.0)      # square 40 x 3, length
sleeve_z = (rail_z[0] - 30.0, rail_z[0] + 40.0)  # 549 .. 619
post_top_work = 630.0
lift = 100.0                    # mm, work -> transport
act_y = 0.0
act_x = rail_x + rail / 2.0 + 10.0 + 20.0        # 275: between the rail (245) and the inner upper beam (305)
act_body = (40.0, 250.0)        # O, length (24 V, 1500 N, stroke 100)
act_rod = 16.0
act_top = 790.0                 # body top: clevis on a tall 4 mm bracket from the rail side
lug_h = 25.0                    # rod lug on the housing top

# ---------------------------------------------------------------------
# Operation (flm_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.2e-6
speed = (0.3, 0.8)              # m/s
energy_kJ_m2 = {"grass": 1.0, "stubble_residue": 2.0, "prunings": 4.0}   # mulching energy per area (estimated)
idle_w = 350.0                  # windage and bearing losses of the flail rotor at 2500 rpm (estimated)
drive_w = 200.0
electronics_w = 40.0
throw_check_v = 40.0            # m/s: tip speeds above this need the full hood and flaps

# from build_flm.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 115.6, "cg": (23.0, 12.0, 285.0), "lift_kg": 99.1}
