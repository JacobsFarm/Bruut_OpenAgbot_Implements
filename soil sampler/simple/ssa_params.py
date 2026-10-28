import math

# =====================================================================
# Soil sampler (simple) - parameters
# Automatic soil sampler for the Bruut OpenAgbot (standard robot), mounted in the middle of the robot so the whole
# robot weight is available as push force. A ball-screw Z axis pushes a O25 gouge probe into the soil (0-10 cm for
# grassland, up to 0-30 cm for arable land); back up, a swing chute moves under the probe tip and an ejector rod pushes
# the core out, into the cup under the funnel. A carousel holds 10 cups of 1.3 l: one composite sample (about 40 cores)
# per cup, so 10 plots per trip. A sprung foot holds the sod down while the probe comes out and senses the ground.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_upper_beam_x = (325.0, 425.0)     # centres of the upper beams per side, along y
robot_upper_beam_z = (659.0, 699.0)
robot_bracket_x = 261.0                 # inside of the wheel brackets (side plates reach down to the axle)
robot_mass = 160.0              # kg, estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Bridges: 2 x tube 40 x 40 x 3 across, on top of the inner upper beams (x 305..345), 2 x M10 per beam
# Between the wheel-unit bolts (y +-425 / +-575 at x 325 and 425)
# ---------------------------------------------------------------------
bridge = 40.0
bridge_x = (-365.0, 365.0)
bridge_front_y = (60.0, 100.0)
bridge_rear_y = (-400.0, -360.0)
bridge_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bridge)
bridge_bolt_x = 325.0

# ---------------------------------------------------------------------
# Z axis: mast plate 10 mm hanging on the front bridge, 2 round rails SBR20, ball screw SFU1605, NEMA23 + 1:1
# ---------------------------------------------------------------------
mast_x = 110.0                  # half width
mast_y = (50.0, 60.0)           # plate against the rear face of the front bridge
mast_z = (180.0, 1110.0)
rail_x = 70.0
rail_y = (20.0, 50.0)           # SBR20 support rail with O20 shaft
screw_y = 35.0
screw_d = 16.0
screw_lead = 5.0
motor = (57.0, 100.0)           # NEMA23 square, length
motor_torque = 1.3              # Nm available at 900 rpm (2.2 Nm holding), estimated
motor_rpm = 900.0               # NEMA23 still gives ~1.3 Nm here (estimated)
carriage_w = 100.0              # half width
carriage_h = 140.0
carriage_y = (-12.0, 20.0)      # plate + 4 rail blocks
probe_y = -60.0                 # probe axis (x = 0)
holder_y = (-90.0, -12.0)
holder_h = 60.0

# probe: gouge auger O25 (core O19), 450 long from the holder; ejector rod inside, small 24 V actuator on top
probe_d = 25.0
probe_core_d = 19.0
probe_len = 450.0
ejector = (40.0, 220.0)         # actuator O40 x 220 on top of the holder
ejector_stroke = 150.0
foot_d = 120.0                  # sprung foot (PE ring 15 mm) on 2 rods O10 through the holder
foot_t = 15.0
foot_rod_x = 45.0
foot_drop = 40.0                # foot below the probe tip when free (it touches the ground first)
foot_rod_len = 475.0           # collar on top rests on the holder in park

# carriage height (bottom of the carriage plate): park = probe tip 560 above the ground; sample = tip at -depth
tip_park = 560.0                 # high enough for the chute to run at >45 degrees to the funnel
depth_grass = 100.0
depth_arable = 300.0
depth_max = 200.0               # what the Z travel allows below the ground (deeper: arable variant with a longer mast)


def carriage_z(tip):
    """Carriage bottom height for a probe tip height."""
    return tip + probe_len - holder_h


# ---------------------------------------------------------------------
# Carousel: 10 cups O100 x 180 (1.3 l) on a turntable O470 under the robot, on a shaft from the rear bridge,
# NEMA17 + 5:1 on the bridge. The index cup (under the funnel) is the one at +y.
# ---------------------------------------------------------------------
car_c = (0.0, -380.0)           # far enough back that the foot passes the index cup
car_d = 470.0
car_t = 4.0
car_z = 120.0                   # bottom of the turntable
n_cups = 10
cup_d = 100.0
cup_h = 180.0
cup_r = 180.0                   # radius of the cup centres
car_shaft_d = 20.0
car_motor = (42.0, 48.0)

# funnel above the index cup, and the swing chute (servo) from under the probe tip to the funnel
funnel_z = (car_z + car_t + cup_h + 8.0, car_z + car_t + cup_h + 58.0)
funnel_d = (110.0, 60.0)        # top, bottom
chute_pivot = (0.0, car_c[1] + cup_r)     # (x, y) above the funnel = index cup centre
chute_w = 40.0
chute_aside_deg = 90.0          # chute swung away while the probe goes down


# ---------------------------------------------------------------------
# Work (ssa_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
pe = 0.96e-6
alu = 2.7e-6
q_c = {"grass_moist": 1.5e6, "grass_dry": 3.0e6, "arable_loose": 1.0e6, "arable_compact": 2.5e6}   # Pa cone resistance
f_s = 20e3                      # Pa side friction of the soil on the probe (estimated)
ball_eta = 0.90
weight_use = 0.70               # share of the robot weight that may be used as push force (wheels stay loaded)
cores_per_sample = 40           # Dutch practice: 40 cores per plot (grassland 0-10 cm)
soil_rho = 1300.0               # kg/m3 dry bulk density
drive_between = 15.0            # m between cores in a plot (zigzag)
speed = 1.0                     # m/s
t_eject = 3.0                   # s ejector + chute
t_settle = 2.0                  # s stop, GNSS fix and foot down
m_motor = 1.4
m_car_motor = 0.4
m_ejector = 0.8
m_cups = 0.12                   # each, PP


def cup_l():
    """Volume of one cup (l)."""
    return math.pi / 4.0 * (cup_d - 4.0) ** 2 * (cup_h - 2.0) / 1e6


# from build_ssa.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 32.0}
