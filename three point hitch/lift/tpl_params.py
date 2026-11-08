import math
import os
import sys

# =====================================================================
# Three-point hitch, lift variant - parameters
# A lift mast for raising and lowering machines straight up and down: 2 fixed round columns O50 x 4 behind the rear
# toolbar of three point hitch/simple, a carriage on 4 plain-bush housings with the male A-frame triangle of the
# a_frame variant, and a Linak LA36 (stroke 300) between the carriage and the top cross of the mast. The rod eye runs
# in a short slot at the top, so an implement on its own wheels can float a little.
# Demo: a machine (a box on a frame with 4 parking legs and a female triangle) that the robot picks up by reversing
# under it with the carriage low, lifting (the triangle centres it and the latch drops in), driving off, and sets down
# again somewhere else.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot. All dimensions are here; never hardcode.
# =====================================================================
FOLDER = os.path.dirname(os.path.abspath(__file__))
TPA_FOLDER = os.path.join(os.path.dirname(FOLDER), "a_frame")
TPH_FOLDER = os.path.join(os.path.dirname(FOLDER), "simple")
for _f in (TPH_FOLDER, TPA_FOLDER):
    if _f not in sys.path:
        sys.path.append(_f)

import tpa_params as Q                    # noqa: E402
import tph_params as TP                   # noqa: E402

robot_wheel_x = Q.robot_wheel_x
robot_axle_y = Q.robot_axle_y
robot_tire_d = Q.robot_tire_d
robot_tire_w = Q.robot_tire_w
robot_mass = Q.robot_mass
robot_cg_y = Q.robot_cg_y
tb_y = Q.tb_y
tb_z = Q.tb_z

# ---------------------------------------------------------------------
# Mast (fixed): 2 columns O50 x 4 between a bottom and a top cross tube, 2 side uprights 40 x 40 x 3, 2 brackets to
# the rear face of the toolbar (clear of the hanger webs at x 155..161 and 239..245, which reach y -890)
# ---------------------------------------------------------------------
col_d = 50.0
col_wall = 4.0
col_x = 170.0
col_y = -940.0
cross = (60.0, 40.0)           # bottom and top cross tube 60 (z) x 40 (y) x 3
cross_x = 295.0
bottom_cross_z = 80.0          # bottom of the bottom cross tube
top_cross_z = 1115.0           # bottom of the top cross tube: the rod eye stays clear at the top of the slot
upright = 40.0
upright_x = 275.0              # centre of the side uprights
bracket_z = (458.0, 522.0)     # brackets on the toolbar rear face

# ---------------------------------------------------------------------
# Carriage: plate 10 mm behind 4 bush housings (2 per column, 300 apart), 2 wedge brackets to the male triangle
# ---------------------------------------------------------------------
cp_base_low = (-1090.0, 220.0)  # (y, z) coupler origin with the carriage at the bottom
travel = 280.0                  # carriage travel (LA36 stroke 300 with 10 mm to both end stops)
housing = (76.0, 60.0)          # bush housing: tube O76 x 60 high with an iglidur bush on O50, web to the plate
housing_dz = (60.0, 360.0)      # housing centres above the coupler origin
cr_plate_y = (-988.0, -980.0)   # 8 mm, with 3 windows
cr_plate_x = 230.0
cr_plate_dz = (-10.0, 430.0)    # plate above the coupler origin
cr_bracket_x = 120.0            # wedge brackets (8 mm) centre
mu_bush = 0.15                  # plain bush on a steel tube, dry (estimated)

# ---------------------------------------------------------------------
# LA36: body on the carriage (lugs on the plate, low), rod up to the top cross; the motor is turned along x so the
# housing fits between the toolbar and the carriage plate
# ---------------------------------------------------------------------
act_variant = "20F"
act_stroke = 300.0
act_retracted = Q.act_bid_base + act_stroke     # 500
act_extended = act_retracted + act_stroke       # 800
act_y = -930.0
act_body_dz = 40.0               # body pin above the coupler origin
act_top_z = cp_base_low[1] + act_body_dz + act_extended - 10.0   # rod pin (slot end) on the top cross: 1050
float_slot = 40.0                # the carriage can rise 40 mm when the implement is carried by its own wheels
act_roll = 90.0                  # motor along +x (deg about the actuator axis)
act_motor_side = 1


def act_mass():
    return Q.act_mass(act_stroke)


# ---------------------------------------------------------------------
# Demo machine: a box on a frame with 4 parking legs and the female triangle
# ---------------------------------------------------------------------
couple_dz = 60.0                 # the male triangle passes 60 mm under the female and lifts into it
mc_base = (cp_base_low[0], cp_base_low[1] + couple_dz)  # female origin of the standing machine (robot at y 0)
mc_cross = 60.0                  # front cross tube 60 x 60 x 3 behind the female
mc_cross_y = 12.0                # gap between the female lock plate and the cross tube
mc_rail = 50.0                   # side rails 50 x 50 x 3
mc_rail_x = 400.0
mc_len = 760.0                   # rails from the cross tube backwards
mc_leg = 40.0                    # parking legs 40 x 40 x 3 with a foot plate 100 x 100 x 8
mc_leg_y = (-70.0, -700.0)       # leg centres behind the female origin
mc_foot = (100.0, 8.0)
mc_box = (840.0, 560.0, 380.0)   # box (x, y, z) on the rails, 4 mm wall
mc_box_y0 = -110.0               # front of the box behind the female origin
mc_load_kg = 15.0                # content of the box (demo: seed / fertilizer)
mc_box_wall = 4.0

# ---------------------------------------------------------------------
# Work, robot
# ---------------------------------------------------------------------
g = Q.g
steel = Q.steel
pe_density = 0.95e-6
front_share_min = Q.front_share_min
ballast_kg = Q.ballast_kg
ballast_cg_y = Q.ballast_cg_y
imp_cg_behind = Q.imp_cg_behind
# from build_tpl.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 44.2, "mount_cg_y": -830.0, "carriage_kg": 21.7, "carriage_cg": (-1002.0, 407.0),
              "machine_kg": 50.1, "machine_cg": (-1427.0, 330.0), "act_kg": 5.5}

DZ_POSES = (0.0, 30.0, couple_dz, 140.0, travel)


def cp_base(dz=0.0):
    return cp_base_low[0], cp_base_low[1] + dz


def body_pin(dz=0.0):
    return act_y, cp_base_low[1] + act_body_dz + dz


def act_length(dz):
    """LA36 length with the rod pin at the slot end (carrying)."""
    return act_top_z - body_pin(dz)[1]


def act_pin(dz, act_len=None):
    """(y, z) of the rod pin: carrying (None) at the slot end, else the pin floats up in the slot."""
    if act_len is None:
        return act_y, act_top_z
    z = body_pin(dz)[1] + act_len
    return act_y, max(act_top_z, min(act_top_z + float_slot, z))


def dz_for_length(L):
    return act_top_z - L - cp_base_low[1] - act_body_dz


def machine_dz(dz):
    """Lift of the machine: it stands on its legs until the male triangle has lifted into the female."""
    return max(0.0, dz - couple_dz)
