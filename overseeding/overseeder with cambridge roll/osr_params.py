import os
import sys

# =====================================================================
# Overseeder with Cambridge roll - parameters
# The seeder unit of the drop seeder ("overrseeder") hangs between the arms of the Cambridge roll ("cambridge roll"),
# in front of the rings. No wheels of its own: the trailer rests on the tow ball and the roll. Seed falls on a bare
# patch and the rings press it in 300 mm later. The roll always rolls; the seeder only runs over bare soil.
#
# Only the positions and the parts that are new for the combination are here; everything else is read from
# cbr_params and ovd_params (same parameters, not copied).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# =====================================================================
FOLDER = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(FOLDER)
for sub in ("cambridge roll", "overrseeder"):
    path = os.path.join(BASE, sub)
    if path not in sys.path:
        sys.path.insert(0, path)

import cbr_params as C          # noqa: E402  robot interface, hitch, roll, frame
import ovd_params as O          # noqa: E402  seeder unit, seed, timing

# ---------------------------------------------------------------------
# Positions (robot coordinates, trailer straight behind the robot)
# ---------------------------------------------------------------------
unit_y = -1960.0                # drop line
drop_to_roll = 300.0            # the rings touch the ground 300 mm behind the drop line
axle_y = unit_y - drop_to_roll  # -2260
cross_gap = 250.0               # front cross beam (rear face) this far in front of the drop line: clear of the unit
cross_y = unit_y + cross_gap    # -1710; the braces end in front of the parking leg lug

# Hangers: the end plates of the unit (x +-505) are bolted to the inside of the arms (x +-515) with a spacer block
hanger_v = ((-140.0, -100.0), (100.0, 140.0))   # v of the two spacer blocks per side (outside the hopper walls)
hanger_x = (O.width / 2.0 + O.end_plate_t, C.arm_x[0])     # 505 .. 515
hanger_z = C.arm_z

# Distances along the trailer from the ball (for the kinematics of the animation)
L_drop = C.ball[1] - unit_y     # 1130
L_roll = C.ball[1] - axle_y     # 1430
L_cam = (L_drop - O.cam_use_v[1], L_drop - O.cam_use_v[0])     # analysed strip of the camera
hitch_behind_axle = C.robot_axle_y - C.ball[1]                  # 330, ball behind the rear axle of the robot
