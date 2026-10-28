import os
import sys

# =====================================================================
# Bag trailer (simple) - parameters
# Small two-wheeled trailer behind the Bruut OpenAgbot (standard robot) on the 50 mm tow ball of the cambridge roll
# ("overseeding/cambridge roll": hitch, coupling head, drawbar and braces are imported from build_cbr, not copied).
# A plywood deck with side boards and a drop tailgate carries 12 bags of 25 kg (seed, fertilizer, feed, pellets) to a
# fixed point in the field or yard, where they are taken off by hand or tipped off the tailgate.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

CBR_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "overseeding", "cambridge roll")
if CBR_FOLDER not in sys.path:
    sys.path.append(CBR_FOLDER)
import cbr_params as C          # noqa: E402  (ball, coupling, drawbar, cross beam, arm sections)

ball = C.ball                   # (x, y) of the tow ball, y -830
ball_z = C.ball_z
cross_y = C.cross_y             # rear face of the front cross beam (-1650): the cbr drawbar and braces fit to it
frame_x = C.arm_x               # side rails 40 x 40 x 3 at x +-(515..555), as the roll frame arms
frame_z = C.arm_z               # z 300..340
rhs_t = C.rhs_t

# ---------------------------------------------------------------------
# Frame and deck
# ---------------------------------------------------------------------
rail_y = (-3020.0, cross_y)                # side rails from the rear to the front cross beam
cross_members_y = (-2990.0, -2600.0, -2200.0, -1900.0)
ply_t = 18.0
deck_x = 555.0
deck_y = (-3020.0, cross_y + C.cross_w)
deck_z = frame_z[1] + ply_t     # loading height 358
board_h = 280.0                 # side and front boards (plywood 18 on posts 30 x 30)
post = 30.0
tailgate_hinge_z = deck_z

# ---------------------------------------------------------------------
# Axle and wheels: square tube 50 x 50 x 4 under the rails on 2 hanger plates, stub spindles, wheels 4.00-8 (O400)
# ---------------------------------------------------------------------
axle_y = -2380.0
wheel_d = 400.0
wheel_w = 100.0
wheel_x = 680.0                 # wheel centre x (outside the rails)
axle_tube = 50.0
hanger_t = 8.0
mudguard = (130.0, 2.0)         # width, thickness; 50 mm over the tyre

# ---------------------------------------------------------------------
# Load: 12 bags of 25 kg (650 x 450 x 120), 2 x 2 per layer, 3 layers
# ---------------------------------------------------------------------
bag = (450.0, 650.0, 120.0)     # x, y, z
bag_kg = 25.0
bag_layers = 3
bag_y0 = -2980.0

# ---------------------------------------------------------------------
# Work (bgt_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
ply = 0.65e-6
rubber = 1.2e-6
robot_mass = 160.0
robot_axle_y = 500.0
robot_cg_y = 0.0
mu_tyre = {"wet_grass": 0.45, "dry_grass": 0.65, "concrete": 0.6}
crr_robot = {"wet_grass": 0.08, "dry_grass": 0.06, "concrete": 0.02}
crr_trailer = {"wet_grass": 0.10, "dry_grass": 0.08, "concrete": 0.02}
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
eta_drive = 0.75
speed = 1.2
battery_wh = 1900.0
# from build_bgt.mass_properties() (update after a change of the model)
MODEL_MASS = {"trailer_kg": 0.0, "trailer_cg_y": 0.0, "hitch_kg": 0.0}


def bag_positions():
    out = []
    for k in range(bag_layers):
        for j in range(2):
            for i in range(2):
                x0 = -bag[0] - 10.0 if i == 0 else 10.0
                out.append((x0, bag_y0 + j * (bag[1] + 10.0), deck_z + k * bag[2]))
    return out
