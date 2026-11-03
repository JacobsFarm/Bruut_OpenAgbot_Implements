import os
import sys

# =====================================================================
# Hot foam weeder (simple) - parameters
# Kills weeds on paths, pavements, fence lines, tree rows and beds with hot water (~95 C) and a little foam concentrate
# that holds the heat on the leaves, under the insulated hood of the flame weeder. No flame on the ground: also where
# flaming is a fire risk (dry grass, straw, buildings).
#   - hood, castors, free parallelogram, mount plate, the 2 x 18 kg propane cylinders and the liquid gas valves are the
#     flame weeder's ("weeds burner/propane_hood", imported, not copied); the burners in the hood are replaced by a
#     foam bar with 12 nozzles
#   - water tank (~100 l) under the belly of the robot, hung from 2 rails under the lower beams (as on the
#     drop-on-demand boom)
#   - rear rack on the rear lower beams: propane continuous-flow boiler (coil heater, 40 kW), water pump, foam can with
#     a dosing pump
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

FLW_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "weeds burner", "propane_hood")
if FLW_FOLDER not in sys.path:
    sys.path.append(FLW_FOLDER)
import flw_params as W          # noqa: E402  (hood, castors, parallelogram, mount, propane cylinders)

# ---------------------------------------------------------------------
# Robot interface (from the flame weeder)
# ---------------------------------------------------------------------
robot_wheel_x = W.robot_wheel_x
robot_axle_y = W.robot_axle_y
robot_axle_z = W.robot_axle_z
robot_tire_d = W.robot_tire_d
robot_tire_w = W.robot_tire_w
robot_lower_beam_y = W.robot_lower_beam_y
robot_lower_beam_z = W.robot_lower_beam_z
robot_upper_beam_x = W.robot_upper_beam_x
robot_kg = W.robot_kg
robot_cg = W.robot_cg
robot_steer_max = 30.0
m10_hole = W.m10_hole

# ---------------------------------------------------------------------
# Belly rails (as on the drop-on-demand boom): 40 x 40 x 3 along y under the lower beams at x +-225, 4 x M10 each.
# Inside the flame-weeder sub plate (x +-170) and the wheel brackets / wooden blocks (from x 261).
# ---------------------------------------------------------------------
rail_x = 225.0
rail = 40.0
rail_wall = 3.0
rail_y = (-595.0, 595.0)
rail_z = (robot_lower_beam_z[0] - rail, robot_lower_beam_z[0])     # 579 .. 619

# Tank frame: 4 hangers 40 x 40 x 3 from the rails down to a rectangular frame of 40 x 40 x 3 under the tank
hanger_y = 262.0                # hangers at (+-225, +-262), outside the tank (y +-238)
hanger_foot = (40.0, 100.0, 8.0)        # foot plate under the rail, 2 x M8 into rivet nuts at y +-30
frame_z = (130.0, 170.0)        # tank frame: tank floor at z 170 -> 170 mm ground clearance under the frame
frame_x = 250.0                 # long tubes at x +-250, cross tubes at y +-262

# Water tank: rotomoulded PE 560 x 476 x 375, wall 6, ~95 l. Filled through a camlock coupling at the rear.
tank_x = 280.0
tank_y = (-238.0, 238.0)
tank_z = (frame_z[1] + 3.0, frame_z[1] + 3.0 + 375.0)              # rubber strip 3 mm
tank_wall = 6.0
tank_r = 40.0
tank_l = 95.0                   # usable litres (to the max mark)
fill_coupling = (-120.0, 50.0)  # x, d: camlock on the rear wall near the top
outlet = (-188.0, 22.0)         # x, d: suction fitting on the rear wall, near the bottom

# ---------------------------------------------------------------------
# Rear rack: 2 tubes 40 x 40 x 3 along y on top of the rear lower beams at x +-225 (M10 down into the beams), a 4 mm
# deck plate behind the robot over the parallelogram and the hood front.
# ---------------------------------------------------------------------
rack_x = 225.0
rack_y = (-600.0, -1100.0)
rack_z = (robot_lower_beam_z[1], robot_lower_beam_z[1] + 40.0)     # 659 .. 699
deck = ((-300.0, 300.0), (-1100.0, -660.0), 4.0)
deck_z = rack_z[1] + deck[2]    # 703

# Boiler: propane continuous-flow coil heater (hot-water pressure-washer type), 40 kW, stainless coil in an insulated
# drum, burner with fan at the bottom side, flue stack with rain cap on top
boiler_xy = (100.0, -880.0)
boiler_d = 360.0
boiler_h = 620.0
burner_fan = (110.0, 80.0, 80.0, 60.0)    # d, length out of the drum (-x side), y offset, z above the drum bottom
# (the burner fires up inside the bottom of the drum)
flue = (110.0, 180.0)                   # d, height above the drum
boiler_kw = 40.0                        # heat into the water at full fire (estimated, catalogue class)
boiler_eff = 0.85
boiler_fan_w = 60.0
boiler_kg = 38.0

# Water pump: 24 V diaphragm pump 11 l/min, 3 bar (as on the spot sprayer), on the deck, left front
pump_xy = (-215.0, -735.0)
pump_box = (90.0, 160.0, 110.0)
pump_w = 110.0
pump_kg = 3.0

# Foam concentrate: 10 l can and a dosing pump (0.5 %), on the deck, left rear
can_xy = (-220.0, -985.0)
can_box = (150.0, 200.0, 290.0)
doser_box = (70.0, 70.0, 90.0)
doser_xy = (-105.0, -1035.0)
foam_share = 0.005

# ---------------------------------------------------------------------
# Foam bar in the hood (instead of the burners): stainless pipe 3/4" along x, 12 foam nozzles (flat jet with an air
# inlet, 125 mm pitch) aimed down, tips 110 mm above the ground
# ---------------------------------------------------------------------
bar_y = W.hood_y[1] - 70.0      # -1000
bar_z = 190.0
bar_d = 26.9
bar_x = 720.0
n_nozzles = 12
nozzle_pitch = W.work_w / n_nozzles      # 125
nozzle_x = tuple(-W.work_w / 2.0 + nozzle_pitch * (i + 0.5) for i in range(n_nozzles))
nozzle = (18.0, 70.0)           # body d, length (down from the bar)
bar_clamps_x = (-500.0, 0.0, 500.0)
hose_d = 22.0                   # insulated hot-water hose (outside)
hose_x = 340.0                  # hot hose down into the hood at this x (outside the deck, x +-300)

# ---------------------------------------------------------------------
# Process (hfw_calc and the animation)
# ---------------------------------------------------------------------
cp_water = 4.19                 # kJ/kg K
t_in = 12.0                     # C, water in the tank
t_out = 96.0                    # C at the boiler outlet
hose_loss_k = 3.0               # K lost in the hose and the bar (estimated)
dose_l_m2 = 0.4                 # l/m2 of foam solution (estimated, hot-foam practice 0.3 .. 1)
lethal_s = 2.0                  # s above ~60 C on the leaf kills seedlings (estimated)
foam_hold_s = 20.0              # s the foam keeps the leaf above ~60 C (estimated, without foam ~3 s)
lhv = W.lhv                     # MJ/kg propane
cyl_kg_gas = W.cyl_kg_gas
flame_kg_ha = W.dose_target     # propane per ha of the flame weeder, for comparison
drive_w = 250.0                 # W driving at 0.15 m/s with this load (estimated)
control_w = 25.0
battery_kwh = 2.4
field_eff = 0.8
water_price = 0.002             # EUR/l (estimated)
gas_price = W.gas_price
foam_price = 6.0                # EUR/l concentrate (estimated)
g = 9.81
steel = 7.85e-6
pe = 0.95e-6

# from build_hfw.mass_properties() (update after a change of the model); robot_kg + these + water + gas
MODEL_MASS = {"robot_side_kg": 152.5, "robot_side_cg_y": -418.0, "hood_kg": 71.6, "total_kg": 224.1}
