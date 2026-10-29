# =====================================================================
# Straw spreader (simple) - parameters
# Lays a strip of straw mulch in the free middle inter-row of a 2-row bed (rows 375 apart) under the Bruut OpenAgbot
# (standard robot). 2 small bales lie in a chamber on the upper beams; a slatted floor chain moves them slowly back
# against a spiked shredder drum that tears the straw loose; it falls through a chute to a 190 mm outlet 300 mm above
# the ground at x 0. The floor speed sets the dose (follows the driving speed), the drum speed is fixed.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_lower_beam_z = (619.0, 659.0)
robot_rear_beam_y = (-575.0, -425.0)
robot_mass = 160.0
robot_cg_z = 450.0
robot_track = 750.0
robot_steer_deg = 30.0
m10_hole = 10.4

# Crop: 2 rows at x +-187.5; the strip goes in the middle inter-row; the chute stays out of the row space below crop_h
row_x = 187.5
row_band = 80.0
crop_h = 400.0

# ---------------------------------------------------------------------
# Mount: 2 bearers 40 x 40 x 3 across the 4 upper beams at y +-325 (beam holes), 2 rails 40 x 40 x 3 along y on them
# ---------------------------------------------------------------------
bearer = 40.0
bearer_x = 470.0
bearer_y = (-325.0, 325.0)
bearer_bolt_x = (325.0, 425.0)
rail_x = 250.0                  # rail centres
rail_y = (-900.0, 360.0)
rail_bolt_y = bearer_y          # rails bolted to the bearers (M10, rail on bearer)

# ---------------------------------------------------------------------
# Floor chain: 2 roller chains 08B at x +-150 on sprockets O80 (shafts O25 in UCP 204 on the rails), slats 25 x 20
# every 150 mm across; a 2 mm floor plate under the top strand carries the bales.
# ---------------------------------------------------------------------
shaft_z = 812.0                 # UCP 204 centre height 33 on the rails (top z 779)
sprocket_y = (270.0, -500.0)    # front (drive), rear
sprocket_r = 40.0
chain_x = 150.0
chain_w = 12.0
chain_t = 8.0
slat = (25.0, 20.0)             # angle 25 x 20 x 3: y, z
slat_x = 220.0
slat_pitch = 150.0
floor_y = (-470.0, 240.0)
floor_z = (842.0, 845.0)
shaft_d = 25.0
pillow = (40.0, 127.0, 45.0)    # UCP 204 block: y, x, z (approx.)

# ---------------------------------------------------------------------
# Bale chamber: side walls 2 mm inside the rails, front wall; 2 small bales 460 x 360 x 900 stacked
# ---------------------------------------------------------------------
wall_x = 240.0                  # inside of the side walls
wall_t = 2.0                    # aluminium
wall_y = (-540.0, 330.0)
wall_top = 1620.0
wall_z0 = 850.0                 # walls start over the UCP blocks (top z 845); held by 4 posts on the rails
post_y = (-250.0, 50.0)          # clear of the rail bolts at y +-325
front_wall_y = 345.0
bale = (460.0, 360.0, 880.0)    # x, z, y of a small bale (as loaded)
bale_y0 = -560.0                # rear face of the bales (against the drum teeth)
bale_z0 = 880.0                 # on the slats
n_bales = 2
bale_kg = 13.0

# ---------------------------------------------------------------------
# Shredder drum: tube O160 x 4 with 4 rows of spikes O16 x 80 (tip O320), x +-220, axis behind the bales
# 48 V 750 W motor with a 1:10 gearbox on the right; housing 6 mm side plates, top and rear plate
# ---------------------------------------------------------------------
drum_y = -700.0
drum_z = 1060.0
drum_d = 160.0
drum_wall = 4.0
drum_x = 220.0
spike_d = 16.0
spike_l = 80.0
spike_rows = 4
spike_pitch = 55.0              # along x
drum_shaft_d = 30.0
house_x = 250.0                 # inside of the housing side plates
house_t = 3.0
house_y = (-900.0, -560.0)
house_top = 1320.0
drum_motor = (90.0, 160.0)      # O, length (along x) outside the right side plate
drum_rpm = 250.0
drum_w = 750.0
floor_gm = (60.0, 110.0)        # 24 V gearmotor O60 x 110 on the front shaft, right side

# ---------------------------------------------------------------------
# Chute: funnel 2 mm from under the drum (z 870) to the outlet 190 x 60 at z 300, x 0
# ---------------------------------------------------------------------
chute_top_z = 870.0
chute_top = ((-220.0, 220.0), (-895.0, -580.0))     # x, y at the top
chute_out_z = 300.0
chute_out = ((-80.0, 80.0), (-760.0, -700.0))   # stays out of the crop rows below 400
chute_t = 2.0                   # aluminium

# ---------------------------------------------------------------------
# Work (for stw_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
straw_rho = 120.0               # kg/m3 in a small bale (estimated)
strip_w = 0.20                  # m, strip width on the ground (outlet 160 + spread)
dose = (0.3, 0.5, 0.8)          # kg/m2 of strip: ~2.5 / 4 / 6 cm of straw (estimated)
speed = 0.5                     # m/s
specific_energy = 5.4           # kJ/kg to tear straw loose from a bale (1.5 kWh/t, estimated; chopping takes ~3x)
drum_idle_W = 100.0
crr = 0.08
eta_drive = 0.75
eta_drum = 0.8
robot_battery_wh = 1900.0
# from build_stw.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 101.5, "cg_y": -366.0, "cg_z": 971.0}
