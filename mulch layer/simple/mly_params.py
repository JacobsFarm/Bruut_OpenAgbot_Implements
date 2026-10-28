import os
import sys

# =====================================================================
# Mulch / foil layer (simple) - parameters
# Category 0 implement for the three-point hitch of the Bruut OpenAgbot ("three point hitch/simple", imported, not
# copied): it lays mulch foil (PE or biodegradable, 1.2 m wide) over the bed behind the robot. Two press wheels run on
# the foil edges and push them down, two angled concave discs behind them throw soil onto the edges and bury them.
# A band brake on the roll keeps the foil tight; at the end of the bed the robot lifts, the foil is cut by hand.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

HITCH_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "three point hitch", "simple")
if HITCH_FOLDER not in sys.path:
    sys.path.append(HITCH_FOLDER)
import tph_params as H          # noqa: E402  (hitch geometry: lower pins B, top pin D, pin size, lift poses)

lower_b = H.lower_b             # (y, z) lower hitch points in work (-1270, 220)
top_d = H.top_d()               # (y, z) top hitch point (-1270, 570)
pin_d = H.pin_d
imp_lug_x = H.imp_lug_x         # lower hitch lugs inside the balls (x +-238..248)
lower_bx = H.lower_bx
link_t = H.link_t
top_bracket_x = H.top_bracket_x
lift_work = H.lift_work
lift_transport = H.lift_transport
LIFT_POSES = H.LIFT_POSES

# ---------------------------------------------------------------------
# Frame: toolbar 60 x 60 x 4 behind the hitch pins, A-frame mast, 2 side beams 50 x 50 x 3 to the rear, rear cross tube
# ---------------------------------------------------------------------
tb = 60.0
tb_x = 520.0                    # half length of the front toolbar
tb_y = (-1360.0, -1300.0)       # clear of the link balls (O44 at y -1270)
mast_bar = (10.0, 40.0)
mast_foot_x = 150.0
side_x = (640.0, 690.0)         # side beams (outside the foil 1.2 m and the discs)
side_y = (-2110.0, -1300.0)
side_z = (300.0, 350.0)         # on stands from the toolbar ends
rear_y = (-2110.0, -2060.0)     # rear cross tube 50 x 50 x 3
wall = 3.0

# ---------------------------------------------------------------------
# Foil roll: 1200 wide, O200 on a core O76, shaft O25 in 2 open V-holders (lift out to change), band brake left
# ---------------------------------------------------------------------
foil_w = 1200.0
roll_d = 200.0
core_d = 76.0
roll_y = -1480.0
roll_z = 470.0
roll_shaft_d = 25.0
holder_t = 8.0
foil_t = 0.025                  # mm, PE 25 um (biodegradable PLA/PBAT 15..20 um)
foil_rho = 0.92e-6              # kg/mm3 (PE)
brake_d = 120.0                 # brake drum on the shaft, left of the roll
# guide bar (tube O40 x 2) low under the roll: the foil runs under it onto the bed, ahead of the press wheels
guide_y = -1500.0
guide_z = 110.0
guide_d = 40.0

# ---------------------------------------------------------------------
# Press wheels: rubber O250 x 80 on the foil edges, on trailing arms with a spring (drawn in work, fixed)
# ---------------------------------------------------------------------
press_d = 250.0
press_w = 80.0
press_x = 545.0                 # wheel centre: on the foil 55 mm inside its edge (x +-600)
press_y = -1700.0
press_arm = (10.0, 40.0)

# ---------------------------------------------------------------------
# Covering discs: concave O350 x 4 (dish 30), centre x +-655, angled 22 deg to the travel and tilted 15 deg, edge
# 50 mm in the soil just outside the foil edge: they throw a ridge of soil onto the edge
# ---------------------------------------------------------------------
disc_d = 350.0
disc_t = 4.0
disc_dish = 30.0
disc_x = 655.0
disc_y = -2020.0
disc_depth = 50.0
disc_yaw = 22.0
disc_tilt = 15.0
disc_stub_d = 30.0

# ---------------------------------------------------------------------
# Work (mly_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.2e-6
speed = 0.5                     # m/s laying speed (the foil has to settle on the bed)
bed_len = 100.0                 # m, a bed (example)
turn_s = 90.0                   # end of bed: stop, lift, cut, turn, start a new foil end by hand (estimated)
web_tension = 25.0              # N/m of foil width to lay without wrinkles (estimated)
disc_draft = 180.0              # N per covering disc at 50 mm in light soil (estimated)
press_crr = 0.12                # rolling resistance of the press wheels on soft soil
press_load = 120.0              # N per press wheel (spring + weight, estimated)
ridge = (120.0, 50.0)           # width, height of the soil ridge on each edge (for the picture)
cost_foil = 0.08                # EUR per m2 PE 25 um (estimated)
mu_tyre = 0.45
crr = 0.08
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
battery_wh = 1900.0
eta_drive = 0.75
# from build_mly.mass_properties() (update after a change of the model)
MODEL_MASS = {"imp_kg": 93.7, "imp_cg": (-6, -1615, 321)}


def roll_length(d=roll_d):
    """Foil length (m) on a roll of outside diameter d."""
    import math
    return math.pi * ((d / 2.0) ** 2 - (core_d / 2.0) ** 2) / foil_t * 1e-3


def roll_mass(d=roll_d):
    import math
    return math.pi * ((d / 2.0) ** 2 - (core_d / 2.0) ** 2) * foil_w * foil_rho
