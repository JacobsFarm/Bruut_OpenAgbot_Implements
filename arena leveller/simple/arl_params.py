import os
import sys

# =====================================================================
# Riding arena leveller (simple) - parameters
# Loosens and levels the footing of a horse riding arena (sand, sand with fibres) at night, in a fixed pattern.
# Rear-mounted on the toolbar, hangers, pivot lugs, lift arms, actuator and the welded frame of the grassland harrow
# ("grassland harrow/simple", imported, not copied). New tools on that frame:
#  - 11 rigid loosening tines (flat bar 40 x 12, curved, reversible point) on the front tine bar, 35 mm deep;
#    a second hole pair sets them 50 mm higher for driving over the hard yard (the tool stays on its roller);
#  - a levelling board (angle 100 x 100 x 8) under the rear tine bar, heel on the levelled surface;
#  - a rod roller O220 behind on 2 side plates: it carries the frame and so sets the tine depth (actuator in its
#    float slot); it firms the surface so hooves do not sink.
#  - a 360 degree lidar on a post on the toolbar: an indoor arena has no RTK; the lidar matches the arena walls
#    (and optional UWB anchors) for the position.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, z 0 = footing surface, mm.
# =====================================================================

GHA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "grassland harrow", "simple")
if GHA_FOLDER not in sys.path:
    sys.path.append(GHA_FOLDER)
import gha_params as H          # noqa: E402

robot_axle_y = H.robot_axle_y
robot_tire_d = H.robot_tire_d
robot_mass = 161.5
pivot = H.pivot
frame_x = H.frame_x             # 650: working width 1300
bar_y = H.bar_y                 # (-1170, -1320): front and rear tine bar centres
bar_z = H.bar_z                 # (286, 326)
lift_work = 0.0
lift_transport = H.lift_transport
LIFT_POSES = (-4.0, 0.0, 12.0, lift_transport)

# ---------------------------------------------------------------------
# Rigid loosening tines: flat bar 40 x 12 clamped to the front of the front tine bar (2 x U-bolt M10), shank down and
# curved forward, reversible point 40 x 12 x 90 (hardened). 11 tines at 100 .. 140 mm: the positions skip the side
# members of the frame (x +-430 .. 470) and the clamps sit on the front face of the front tine bar.
# ---------------------------------------------------------------------
TINE_X = (-610.0, -510.0, -370.0, -245.0, -120.0, 0.0, 120.0, 245.0, 370.0, 510.0, 610.0)
tine_n = len(TINE_X)
tine_pitch = 1220.0 / (len(TINE_X) - 1)        # mean
tine_bar = (40.0, 12.0)         # width (x), thickness (y)
tine_depth = 35.0               # point below the surface: the robot pulls 11 tines to ~38 mm in loose sand (arl_calc)
transport_dz = 50.0             # second hole pair in the shanks: tines 50 mm higher, tips 15 mm over a hard yard
tine_rake = 25.0                # degrees forward lean of the lower shank (the point leads)
point_len = 90.0
clamp_plate = (60.0, 8.0, 80.0)  # x, y(t), z

# ---------------------------------------------------------------------
# Levelling board: angle 100 x 100 x 8 under the rear tine bar on 3 straps 60 x 8 with height holes (25 mm steps)
# ---------------------------------------------------------------------
board_y = bar_y[1] - 30.0       # front face of the upright leg (behind the rear bar)
board_leg = 100.0
board_t = 8.0
board_z0 = 0.0                  # heel on the surface
strap_x = (-500.0, 0.0, 500.0)
strap = (60.0, 8.0)

# ---------------------------------------------------------------------
# Rod roller: 2 end discs O220 x 8, 12 rods O16 round them, centre tube O60 x 4, shaft O25 in 2 UCFL 205 on side
# plates 8 mm bolted to the ends of the rear tine bar.
# ---------------------------------------------------------------------
roll_d = 220.0
roll_y = -1560.0
roll_z = roll_d / 2.0           # on the surface in the work pose
roll_x = 620.0                  # half length of the rod cage (inside the side plates)
roll_rods = 12
roll_rod_d = 16.0
roll_core_d = 60.0
roll_shaft_d = 25.0
side_t = 8.0
side_x = frame_x                # inner face of the side plates = end of the rear tine bar (welded on)
brg = (12.0, 50.0, 110.0)       # UCFL 205: flange t, y, z (bolted on the outside of the side plates)
roll_kg_est = 38.0

# ---------------------------------------------------------------------
# Lidar post on the toolbar centre: square tube 40 x 40 x 3 up to z 1000, lidar O80 x 70 on top
# ---------------------------------------------------------------------
post = 40.0
post_xy = (100.0, -880.0)       # behind the toolbar (y -860 .. -780), beside the lift actuator at x 0
post_z = (H.tb_z[0], 1000.0)
lidar = (80.0, 70.0)

# ---------------------------------------------------------------------
# Footing and work (for arl_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
sand_density = 1.6              # t/m3 loose arena sand (estimated)
k_tine = 0.025                  # N/mm2 on tine width x depth: re-loosening loose arena sand every night (estimated)
mu_board = 0.5
board_load_frac = 0.25          # share of the frame weight on the board (rest on the roller, estimated)
crr_roller = 0.12               # rolling resistance of the roller on loose sand
crr_tyre_sand = 0.10            # robot tyres on arena sand
mu_tyre_sand = 0.40
hub_torque_nom = H.hub_torque_nom
r_load = H.r_load
n_driven = H.n_driven
eta_drive = H.eta_drive
speed = 0.8                     # m/s
overlap = 100.0                 # mm between passes
arena = (20.0, 40.0)            # m (dressage arena 20 x 40)
arena_big = (20.0, 60.0)
turn_s = 10.0                   # s per headland turn
battery_wh = 1900.0
computer_w = 40.0               # lidar + computer
robot_cg_y = 0.0
ballast_kg = 44.0               # 4 front plates of the counterweights implement (11 kg each) at y 575: grip
ballast_y = 575.0

# from build_arl.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 25.0, "lift_kg": 129.7, "lift_cg_y": -1370.0, "post_kg": 3.1}   # mount incl. actuator


def tine_x():
    return list(TINE_X)
