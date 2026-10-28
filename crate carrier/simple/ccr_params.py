import math

# =====================================================================
# Crate carrier (simple) - parameters
# Flat deck on the upper beams of the Bruut OpenAgbot (standard robot) for 8 harvest crates 600 x 400 x 300 (2 x 2 per
# layer, 2 layers), with crate guides, a headboard in front of the stack, ratchet straps, a follow-me UWB anchor pair on
# the headboard, a stop/go button box at the rear and a mast that lifts the GNSS antenna above the stack.
# Same deck carries tools, stakes or a 200 l water tank (covers the tool and material cart idea).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py" and the model, that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_upper_beam_x = (325.0, 425.0)     # centres of the upper beams per side (40 wide), y -650..650
robot_upper_beam_z = (659.0, 699.0)
robot_front_stack_y = 405.0     # steering plates and motors of the front units start here (to z 1032)
robot_rear_bolts = (-584.0, -416.0, 705.0)   # frame bolts of the rear units stick out to z 705
robot_gnss = (0.0, 575.0, 740.0)             # top of the GNSS dome
robot_mass = 160.0              # kg, estimated
robot_cg_y = 0.0
robot_cg_z = 380.0              # estimated (batteries low in the frame)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Bearers: 3 x tube 40 x 40 x 3 across, on the upper beams, 4 x M10 each (clear of the rear unit bolts)
# ---------------------------------------------------------------------
bearer = 40.0
bearer_y = (-350.0, 0.0, 330.0)         # centres
deck_x = 650.0                          # half width: 2 crates of 600 + divider + guides
deck_y = (-620.0, 380.0)
bearer_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bearer)
side_rail = 40.0                        # 2 side rails 40 x 40 x 3 along y at the deck edges, between the bearers ends
ply_t = 18.0                            # film-faced plywood
deck_z = bearer_z[1] + ply_t            # top of the deck (loading height)

# Crate guides: angle 30 x 30 x 3 along both sides and the rear edge, flat bar divider in the middle
guide = (30.0, 3.0)
divider = (30.0, 40.0)                  # thickness x height, along y at x = 0

# Headboard: square tube 25 x 2 frame with 2 mm mesh (drawn as a plate), in front of the crates
head_y = (355.0, 380.0)
head_h = 620.0

# ---------------------------------------------------------------------
# Crates (Euro harvest crate 600 x 400 x 300, stacking)
# ---------------------------------------------------------------------
crate = (600.0, 400.0, 300.0)           # x, y, z
crate_wall = 4.0
crate_y0 = -447.0                       # rear edge of the rear row (2 rows of 400 along y, up to the headboard)
crate_layers = 2
crate_empty_kg = 1.6

# Ratchet straps 25 mm over the top layer, hooked in the side rails
strap_y = (-247.0, 153.0)
strap = (25.0, 2.0)

# Follow-me and controls
uwb_box = (80.0, 30.0, 120.0)           # UWB anchor, one at each top corner of the headboard
button_box = (160.0, 90.0, 100.0)       # stop / go / follow box on the rear guide, x = right side
gnss_mast_d = 30.0                      # mast on the headboard carrying the GNSS antenna above the stack
gnss_mast_top = 1500.0

# ---------------------------------------------------------------------
# Work (ccr_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
ply = 0.65e-6
pp = 0.95e-6                            # crate plastic
CROPS = {"strawberries": 4.5, "apples": 16.0, "potatoes": 18.0, "cabbage": 14.0}   # kg net per crate (estimated)
speed_loaded = 1.2                      # m/s
speed_empty = 1.8
trip_m = 150.0                          # one way, row to field edge (example)
handover_s = 60.0                       # unload 8 crates at the edge (estimated)
crr = 0.06                              # rolling resistance, grass headland
mu_tyre = 0.45
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
eta_drive = 0.75
battery_wh = 1900.0                     # usable (2.4 kWh, as in solar/sol_params.py), estimated
track_half = robot_wheel_x
wheelbase_half = robot_axle_y
payload_max = 150.0                     # kg, what the robot is rated for on the top (estimated)
# from build_ccr.mass_properties() (update after a change of the model)
MODEL_MASS = {"deck_kg": 50.4, "deck_cg": (0.0, -25.0, 816.0), "crates_cg": (0.0, -47.0, 1057.0)}


def crate_positions():
    """(x0, y0, z0) of every crate, 2 across x, 2 along y, crate_layers high."""
    out = []
    for k in range(crate_layers):
        for j in range(2):
            for i in range(2):
                x0 = -(divider[0] / 2.0 + 2.0) - crate[0] if i == 0 else divider[0] / 2.0 + 2.0
                out.append((x0, crate_y0 + j * crate[1], deck_z + k * crate[2]))
    return out
