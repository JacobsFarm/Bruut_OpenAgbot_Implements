import os
import sys

# =====================================================================
# Irrigation pump (simple) - parameters
# Direct pump for the Bruut OpenAgbot (standard robot): the robot drives to a ditch, unrolls a 1.5" suction hose with a
# strainer and foot valve into the water, and a self-priming centrifugal pump on a 48 V BLDC motor delivers to a
# 1.5" Camlock coupling at the rear (a lay-flat hose, the hose reel irrigator or a spray boom). The mount (bearers and
# base plate) is the one of the hydraulic power pack ("hydraulic pump/simple", imported, not copied).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

HPU_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "hydraulic pump", "simple")
if HPU_FOLDER not in sys.path:
    sys.path.append(HPU_FOLDER)
import hpu_params as H          # noqa: E402  (bearers, base plate, robot interface)

robot_wheel_x = H.robot_wheel_x
robot_axle_y = H.robot_axle_y
robot_axle_z = H.robot_axle_z
robot_tire_d = H.robot_tire_d
robot_tire_w = H.robot_tire_w
robot_mass = H.robot_mass
robot_cg_z = H.robot_cg_z
robot_steer_deg = H.robot_steer_deg
TOP = H.robot_upper_beam_z[1] + 40.0 + H.plate_t       # top of the base plate (z 744)

# ---------------------------------------------------------------------
# Pump: self-priming centrifugal, casing O220 x 80 (axis along x), priming chamber on top, 1.5" in / out;
# BLDC motor 48 V 1.5 kW O110 x 140 on 2 feet
# ---------------------------------------------------------------------
pump_y = -415.0
pump_z = 870.0                  # shaft axis
casing = (220.0, (-100.0, -20.0))      # O, x range
prime = (120.0, 120.0, 90.0)    # priming chamber x, y, z on top of the casing
motor = (110.0, (-240.0, -100.0))      # O, x range
motor_kw = 1.5
pump_kg = 9.0
motor_kg = 5.5

# ---------------------------------------------------------------------
# Suction hose reel: drum O300 x 180 (tube 3 mm), flanges O520, 8 m of 1.5" spiral suction hose (O48), hollow axle with a rotary
# union on the right end, crank knob on the left flange; 2 side plates 8 mm
# ---------------------------------------------------------------------
reel_x = (30.0, 210.0)          # drum between the flanges (side plates clear of the plate bolts at x 240)
reel_y = pump_y
reel_z = TOP + 275.0            # axle
drum_d = 300.0
flange_d = 520.0                # holds 2 layers of hose (8 m)
flange_t = 3.0
drum_t = 3.0
hose_layers = 2
side_t = 8.0
axle_d = 40.0
hose_d = 48.0
hose_len = 8.0                  # m
strainer = (90.0, 160.0)        # O, length: strainer with foot valve, clipped to the right side plate
coupling_d = 60.0               # 1.5" Camlock, pointing back at the rear edge

# ---------------------------------------------------------------------
# Work (for idp_calc)
# ---------------------------------------------------------------------
g = 9.81
rho = 1000.0
steel = 7.85e-6
h_shutoff = 32.0                # m, pump curve H = h0 * (1 - (Q / q_max)^2) (estimated for a 1.5 kW self-priming pump)
q_max = 16.0                    # m3/h
eta_pump = 0.50                 # best, self-priming pumps are not efficient
eta_motor = 0.88
suction_lift = (1.5, 3.0, 5.0)  # m, water level below the pump
pipe_id = 0.038                 # m, 1.5" hose
lambda_f = 0.025                # friction factor (smooth hose)
k_local = 6.0                   # strainer, foot valve, rotary union, bends
discharge_len = 50.0            # m of lay-flat hose to the field
discharge_id = 0.038
end_head = (0.0, 10.0, 20.0)    # m at the end: open hose, drip line, sprinkler
robot_battery_wh = 1900.0
idle_W = 30.0
dose_mm = 10.0                  # irrigation gift
# from build_idp.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 61.8, "cg_y": -414.0, "cg_z": 908.0}
