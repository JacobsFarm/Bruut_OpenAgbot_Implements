# =====================================================================
# Cover crop undersower (simple) - parameters
# Sows a cover crop (green manure) into a standing crop of 2 rows (375 apart) between the wheels of the Bruut OpenAgbot
# (standard robot). A 25 l hopper on a bearer across the upper beams feeds 3 fluted metering cells on one shaft
# (speed-following 12 V gearmotor); hoses take the seed to fishtail deflectors that lay it in 3 bands: the free
# inter-row in the middle of the bed (x 0) and the 2 wheel inter-rows behind the rear tyres (x +-375). Spring tines on a
# bar high over the crop rows scratch the seed in. The crop rows themselves are not touched.
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
robot_steer_deg = 30.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Crop: 2 rows in the bed between the wheels; the undersower keeps out of the row band below crop_h
# ---------------------------------------------------------------------
row_x = 187.5
row_band = 80.0                 # half width of the crop row (plants) kept free
crop_h = 400.0                  # highest crop the bar and hoses pass over (belly at 619)

# ---------------------------------------------------------------------
# Bearer: 40 x 40 x 3 across the 4 upper beams at y -325 (beam holes), 4 x M10
# ---------------------------------------------------------------------
bearer = 40.0
bearer_wall = 3.0
bearer_x = 470.0
bearer_y = -325.0
bearer_bolt_x = (325.0, 425.0)

# ---------------------------------------------------------------------
# Hopper: PE 4 mm, box 400 x 260 with a V-bottom (55 degrees) to the metering housing; on 2 brackets on the bearer
# ---------------------------------------------------------------------
hop_x = 200.0                   # half width
hop_y = (-330.0, -70.0)         # in front of the bearer
hop_z = (840.0, 1060.0)         # straight part
hop_t = 4.0
hop_out = (180.0, 40.0)         # outlet slot (x half width, y) at the bottom of the V (front and rear walls 55 deg)
hop_out_y = -200.0
hop_out_z = 683.0
lid_t = 4.0
bracket = (40.0, 6.0)           # flat bar brackets on the hopper sides, down onto the bearer top

# Metering housing: aluminium block under the outlet, 3 fluted rollers O40 x 30 on one shaft (along x)
meter_x = 190.0
meter_y = (-225.0, -175.0)
meter_z = (613.0, 683.0)        # between the inner upper beams, in front of the bearer
cell_x = (-120.0, 0.0, 120.0)
roller_d = 40.0
roller_w = 30.0
flutes = 8
roller_ml = 7.5                 # ml per turn per cell: 8 flutes O9 half in the roller, 30 long (~half filled)
gm = (36.0, 70.0)               # 12 V gearmotor O36 x 70 on the right end of the shaft

# ---------------------------------------------------------------------
# Hoses O32 from the cells to the deflectors; side hoses go back under the rear beams first, then out behind the tyres
# ---------------------------------------------------------------------
hose_d = 32.0
hose_wall = 3.0
spout_z = 595.0                 # bottom of the cell spouts
defl_y = -770.0                 # deflectors behind the rear tyres (tyre back at y -715)
defl_z = 120.0                  # bottom of the deflectors
side_z = 560.0                  # side hoses: back at x +-120, across over the crop row and the hanger web at z 560,
                                # then straight down behind the tyre
band_w = (150.0, 100.0)         # band width in the middle / behind each wheel
band_x = (0.0, -375.0, 375.0)   # band centres for the 3 cells (cell_x order)

# ---------------------------------------------------------------------
# Tine bar and hangers: bar 40 x 40 x 3 at z 430..470 over the crop, on 2 hangers under the rear lower beams
# ---------------------------------------------------------------------
bar_y = (-890.0, -850.0)
bar_z = (430.0, 470.0)
bar_x = 450.0
hanger_x = 200.0                # web at x +-200, top plate bolted with 4 x M10 at x +-175 / +-225
hanger_bolt_dx = 25.0
hanger_top = (100.0, 10.0)      # width (x), thickness
hanger_top_y = (-610.0, -390.0)
web_t = 8.0
web_pts = ((-395.0, 609.0), (-600.0, 609.0), (-895.0, 475.0), (-895.0, 425.0), (-845.0, 425.0), (-560.0, 555.0),
           (-395.0, 555.0))
# spring tines O8: coil at the bar, leg down and back to the tip on the ground
tine_d = 8.0
coil = (40.0, 36.0)             # coil O40 x 36 (along x) under the bar
tine_tip = (-975.0, 0.0)        # (y, z) of the tip
tine_x = (-50.0, 0.0, 50.0, -400.0, -350.0, 350.0, 400.0)

# ---------------------------------------------------------------------
# Work (for ccu_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
pe = 0.95e-6
alu = 2.7e-6
pass_w = 750.0                  # mm per pass (one bed)
speed = 1.0                     # m/s
field_eff = 0.8
gm_rpm_max = 60.0
gm_kg = 0.4
SPECIES = {                     # field seed rate (kg/ha, broadcast over the whole field) and bulk density (kg/l), estimated
    "italian_ryegrass": (25.0, 0.38),
    "white_clover": (6.0, 0.77),
    "phacelia": (10.0, 0.50),
    "winter_rye": (100.0, 0.72),
}
tine_force_N = 15.0             # draft per spring tine scratching 10-20 mm (estimated)
crr = 0.08
robot_battery_wh = 1900.0
eta_drive = 0.75
# from build_ccu.mass_properties() and hopper_volume() (update after a change of the model)
MODEL_MASS = {"kg": 26.3, "cg_y": -516.0, "volume_l": 28.3}
