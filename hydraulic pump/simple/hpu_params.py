# =====================================================================
# Hydraulic power pack (simple) - parameters
# 48 V hydraulic power unit on the rear half of the Bruut OpenAgbot (standard robot): a BLDC motor with a 4 cc gear
# pump, a 19 l tank with return filter, a 2-section solenoid valve block with a relief valve, and 2 pairs of ISO-A 1/2"
# quick couplers at the rear for hydraulic implements (cylinders, small motors). High force at slow speed, where linear
# actuators are too weak or too slow.
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
robot_upper_beam_z = (659.0, 699.0)
robot_mass = 160.0
robot_cg_z = 450.0
robot_track = 750.0
robot_steer_deg = 30.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Mount: 2 bearers 40 x 40 x 3 across the 4 upper beams at y -325 / -475 (beam holes, clear of the wheel-unit bolts at
# y -425 / -575), base plate 5 mm on top
# ---------------------------------------------------------------------
bearer_x = 470.0
bearer_y = (-475.0, -325.0)
bearer_bolt_x = (325.0, 425.0)
plate_x = 250.0
plate_y = (-560.0, -270.0)
plate_t = 5.0
plate_bolts = ((-240.0, -475.0), (240.0, -475.0), (-40.0, -325.0), (240.0, -325.0))   # plate to bearers, M8, clear of tank and motor feet

# ---------------------------------------------------------------------
# Tank: steel 2 mm, 180 x 180 x 520 (16 l), filler / breather, return filter, sight glass, suction at the bottom
# ---------------------------------------------------------------------
tank_x = (-240.0, -60.0)
tank_y = (-460.0, -280.0)
tank_h = 520.0
tank_t = 2.0
filter = (70.0, 120.0)          # return filter O70, height above the lid
cap = (50.0, 40.0)

# ---------------------------------------------------------------------
# Motor and pump: BLDC 48 V 3.5 kW O120 x 200 along y, bell housing, gear pump 4 cc/rev (group 1)
# ---------------------------------------------------------------------
motor_x = 170.0
motor_y = (-300.0, -490.0)      # front, rear end of the motor body
motor_d = 120.0
motor_z = 744.0 + 75.0          # axis (on 2 feet)
bell = (100.0, 40.0)            # O, length
pump = (80.0, 70.0, 80.0)       # x, y, z of the pump body behind the bell housing
motor_rpm = 3000.0
pump_cc = 4.0
motor_kw = 3.5
motor_kg = 9.0
pump_kg = 1.8

# ---------------------------------------------------------------------
# Valve block at the rear of the plate: inlet section (relief valve, gauge) and 2 sections CETOP 3 side by side, 24 V
# solenoids on top; the 2 pairs of ISO-A 1/2" quick couplers screw straight into its rear face
# ---------------------------------------------------------------------
valve_x = (-220.0, 20.0)
valve_y = (-560.0, -480.0)
valve_z = (790.0, 870.0)
section_x = (-160.0, -60.0)     # centres of the 2 work sections; inlet section at x -5
solenoid = (36.0, 50.0)         # O, height above the block
gauge = (63.0, 30.0)
valve_kg = 7.0
cpl_x = (-185.0, -135.0, -85.0, -35.0)   # A1 B1 A2 B2
cpl_z = 830.0
cpl_d = 34.0
cpl_len = 70.0
hose_d = 19.0                   # 3/8" hose outside
controller = ((60.0, 230.0), (-296.0, -270.0), (749.0, 900.0))   # motor controller box, x y z (in front of the motor)

# ---------------------------------------------------------------------
# Work (for hpu_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
oil_rho = 0.87                  # kg/l
oil_cp = 1.9                    # kJ/kg K
eta_vol = 0.92                  # gear pump volumetric efficiency
eta_hm = 0.85                   # gear pump hydraulic-mechanical efficiency
eta_motor = 0.90                # BLDC + controller
p_relief = 150.0                # bar: the motor holds ~149 bar at full flow
p_work = (50.0, 100.0, 150.0)   # bar
cylinders = {"40_20_200": (40.0, 20.0, 200.0), "50_25_300": (50.0, 25.0, 300.0)}   # bore, rod, stroke (mm)
robot_battery_wh = 1900.0
battery_peak_kw = 4.8           # 48 V x 100 A (estimated)
tank_surface_w_k = 4.5          # W per K heat loss of the tank (~0.44 m2 at 10 W/m2K, estimated)
t_ambient = 20.0
t_max = 60.0
# from build_hpu.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 48.5, "cg_y": -427.0, "cg_z": 872.0}
