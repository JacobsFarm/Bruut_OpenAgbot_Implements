import math

# =====================================================================
# Battery pack (simple) - parameters
# Two exchangeable 48 V LiFePO4 pods for the Bruut OpenAgbot (standard robot), one per side, hanging under the upper
# beams between the front and rear wheels (low and centred between the axles). Each pod: an aluminium box with 16 cells
# of 50 Ah (51.2 V, 2.56 kWh), BMS and an Anderson connector, with 2 hook strips on top that hang on 2 U-hangers bolted
# to the upper beams, locked by 2 over-centre latches; 2 handles. The pods are paralleled into the robot's 48 V bus
# through diodes / a pack combiner (estimated: the robot's own battery is not in the model).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py" and the model, that folder is not in git)
# ---------------------------------------------------------------------
robot_axle_y = 500.0
robot_wheel_x = 375.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_steer_deg = 30.0
robot_upper_beam_x = (325.0, 425.0)     # centres of the upper beams per side (40 wide)
robot_upper_beam_z = (659.0, 699.0)
robot_mass = 160.0                      # kg, estimated
robot_battery_wh = 1900.0               # usable (2.4 kWh, as in solar/sol_params.py), estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Hangers: 2 per side, flat bar 40 x 8 bent into a U under both upper beams of that side, M10 up through the beams
# ---------------------------------------------------------------------
hanger_y = (-200.0, 200.0)              # centres
hanger = (40.0, 8.0)                    # width (y), thickness
hanger_x = (295.0, 455.0)               # outer faces of the U legs (beams at x 305..445)
hanger_drop = 40.0                      # the bottom bar hangs this far under the beams: room for the hooks

# ---------------------------------------------------------------------
# Pod: aluminium box 3 mm, lid with 2 hook strips, handles and connector on the outer face
# ---------------------------------------------------------------------
pod_x = (300.0, 470.0)                  # inner and outer face (right side; left mirrored)
pod_y = (-255.0, 255.0)                 # clear of the tyres (y +-285, steered front tyre from y 289)
pod_z = (320.0, 600.0)
pod_wall = 3.0
hook = (40.0, 6.0, 30.0)                # hook strip: width (y), thickness, height above the lid
latch = (30.0, 20.0, 40.0)
handle = (120.0, 25.0, 12.0)            # length (y), stand-off (x), bar O12
connector = (60.0, 30.0, 50.0)          # Anderson SB50 housing on the outer face

# cells (inside the box, for the drawing and the mass): 16 prismatic 50 Ah, 2 rows of 8
cell = (148.0, 27.0, 130.0)             # x, y, z (LiFePO4 50 Ah, ~1.0 kg)
cells_n = 16
cell_kg = 1.05
cell_v = 3.2
cell_ah = 50.0
bms_kg = 0.8
dod = 0.9                               # usable depth of discharge

# ---------------------------------------------------------------------
# Work (bpk_calc)
# ---------------------------------------------------------------------
g = 9.81
alu = 2.7e-6
steel = 7.85e-6
charger_w = 1000.0                      # per pod, at the shed (estimated)
# average electric power of the implements at their working speed, from their own calcs (drive + implement)
LOADS_W = {"inter_row_hoe": 1018.0, "grassland_harrow": 1260.0, "grassland_aerator": 520.0,
           "three_point_hitch_cultivator": 1077.0, "push_blade": 880.0, "crate_carrier_shuttle": 250.0}
base_load_w = 60.0                      # computer, GNSS, steering (estimated)
# from build_bpk.mass_properties() (update after a change of the model)
MODEL_MASS = {"pod_kg": 26.0, "hangers_kg": 0.0}    # pod_kg includes its 2 hangers and bolts


def pod_xs(sx):
    """(inner, outer) x of the pod on side sx as a sorted span."""
    return tuple(sorted((sx * pod_x[0], sx * pod_x[1])))


def cell_positions(sx):
    """(x0, y0, z0) of the cells in the pod on side sx: one row of 16 along y, standing on the floor."""
    x0 = pod_xs(sx)[0] + (pod_x[1] - pod_x[0] - cell[0]) / 2.0
    y0 = -cells_n * cell[1] / 2.0
    z0 = pod_z[0] + pod_wall + 2.0
    return [(x0, y0 + i * cell[1], z0) for i in range(cells_n)]
