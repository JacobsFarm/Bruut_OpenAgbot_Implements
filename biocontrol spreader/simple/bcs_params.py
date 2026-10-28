import math

# =====================================================================
# Biological-control spreader (simple) - parameters
# Releases beneficials (predatory mites in bran or vermiculite, parasitic-wasp mummies in sawdust) over two crop rows
# between the wheels of the Bruut OpenAgbot (standard robot): 2 hoppers with a slow agitator and a metering wheel
# each, a small blower whose air carries the carrier through 2 hoses to deflector nozzles just above the rows.
# The dose follows the driving speed (or a task map from the disease scout / pest counts): no chemicals, low wind.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_mass = 160.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Mount: bearer 40 x 40 x 3 across the upper beams at y -60; hopper rings on 2 arms forward of it
# ---------------------------------------------------------------------
bearer = 40.0
bearer_x = 470.0
bearer_y = -60.0
row_x = 187.5                   # 2 rows 375 apart in the bed between the wheels
hopper_y = 70.0
arm = (30.0, 6.0)               # flat bars from the bearer to the hopper rings

# Hoppers: PE, cylinder O200 x 220 on a 60 degree cone, lid with the agitator motor, 5 l each
hopper_d = 200.0
hopper_h = 220.0
cone_h = 120.0
hopper_z0 = 800.0               # bottom of the cylinder part
hopper_wall = 3.0
agitator_motor = (40.0, 60.0)   # O, length on the lid
meter_box = (90.0, 80.0, 70.0)  # metering wheel housing with a NEMA17 (x, y, z), under each cone

# Blower and air lines
fan_d = 200.0                   # centrifugal fan housing O200 x 90, 24 V 60 W, on the bearer at x 0
fan_w = 90.0
manifold_d = 40.0               # air pipe from the fan to the 2 venturis
venturi = (60.0, 80.0)          # O, length (along z) of the venturi under each metering box
hose_d = 40.0
nozzle_z = 450.0                # deflector nozzle outlet above the ground (crop up to ~350)
deflector_d = 140.0             # cone deflector spreads the carrier into a band ~0.3 m

# ---------------------------------------------------------------------
# Work (bcs_calc)
# ---------------------------------------------------------------------
g = 9.81
pe = 0.95e-6
steel = 7.85e-6
hopper_l = None                 # computed in bcs_calc from the dimensions
PRODUCTS = {                    # carrier per bottle (l) and organisms per l, dose per m2 of crop (estimated, label values)
    "predatory_mite_cucumeris": {"per_l": 50000.0, "dose_m2": 100.0},
    "predatory_mite_swirskii": {"per_l": 50000.0, "dose_m2": 50.0},
    "parasitic_wasp_mummies": {"per_l": 20000.0, "dose_m2": 5.0},
}
band_w = 0.75                   # m of bed covered per pass (2 bands round the 2 rows)
speed = 0.5                     # m/s
meter_ml_rev = 4.0              # carrier per revolution of the metering wheel (estimated)
meter_rpm_max = 30.0
air_v = 8.0                     # m/s in the hoses: carries bran, gentle on the mites (estimated)
p_fan = 60.0
p_meter = 15.0
crr = 0.06
eta_drive = 0.75
battery_wh = 1900.0
