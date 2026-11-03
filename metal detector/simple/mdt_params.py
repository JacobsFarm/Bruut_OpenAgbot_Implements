import os
import sys

# =====================================================================
# Metal detector (simple) - parameters
# Pulse-induction (PI) metal detector for the Bruut OpenAgbot (standard robot): maps buried and hidden metal (nails,
# wire, cans, bolts, horseshoes, plough points) in grassland and arable fields, and logs a GNSS point with the signal
# at every hit. The map goes to the field marker (stake out) or to the magnet sweeper.
# A 600 x 400 mm search coil in a plastic housing slides on 2 PE skids in front of the robot, on a boom of 2 GFRP
# (glass fibre) tubes that pivots on 2 steel brackets clamped on the front outer lower beam, so the coil is ~1.1 m
# away from the steel of the robot and the hub motors. A small actuator lifts the boom at the headland; in work its
# rod pin floats in a slot and the coil follows the ground. No metal in the front 1.2 m of the boom: GFRP tubes and
# plates, nylon bolts, a PE cross plate.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

PBL_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "push blade", "simple")
if PBL_FOLDER not in sys.path:
    sys.path.append(PBL_FOLDER)

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_front_beam_y = (555.0, 595.0)     # front OUTER lower beam (x direction)
robot_lower_beam_z = (619.0, 659.0)
robot_steer_deg = 30.0
robot_mass = 160.0
robot_cg_y = 0.0
robot_gnss = (0.0, 575.0)       # GNSS antenna (x, y)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Root brackets (steel, 2 x): base plate 150 x 60 x 8 on top of the front outer lower beam with 2 M10 into the grid
# holes (x +-125, +-225), and a side plate 8 mm forward and down to the boom pivot in front of the beam. The right
# bracket also carries the mast of the lift actuator (outside, x 168..230). Clear of the GNSS mount at x 0.
# ---------------------------------------------------------------------
bracket_x = 160.0               # side plates x +-160..168
bracket_t = 8.0
base_t = 8.0
base_x = (100.0, 250.0)
bolt_x = (125.0, 225.0)
# side plate outline (y, z)
side_pts = ((545.0, 667.0), (545.0, 720.0), (735.0, 630.0), (735.0, 570.0), (665.0, 570.0), (605.0, 620.0),
            (605.0, 667.0))
pivot = (700.0, 600.0)          # (y, z) boom pivot axis (x), pin O16 stainless
pivot_d = 16.0

# ---------------------------------------------------------------------
# Boom: 2 GFRP square tubes 50 x 50 x 4 at x +-130 (outside face against the side plates, nylon bushes), straight from
# the pivot down to the coil carrier; 2 GFRP cross tubes 40 x 40 x 4 keep them square.
# ---------------------------------------------------------------------
boom_x = 127.0                  # tube centres at x +-127 (outside face 2 mm from the side plate)
boom_w = 50.0
boom_wall = 4.0
boom_end = (1650.0, 105.0)      # (y, z) end of the boom centre line on the carrier plate, work pose
cross_at = (0.30, 0.80)         # GFRP cross tubes at these fractions of the boom length
cross_w = 40.0

# ---------------------------------------------------------------------
# Coil carrier and search coil: GFRP plate 10 mm on the boom ends, PE cross plate, coil housing (ABS 4 mm) 600 x 400
# x 40 with the coil (rectangular loop, 24 turns 0.6 mm litz, shown as a 12 x 12 bundle) and 2 PE skids 15 mm.
# ---------------------------------------------------------------------
coil_c = (0.0, 1800.0)          # coil centre (x, y)
coil_size = (600.0, 400.0)
coil_r = 60.0                   # corner radius of the housing
house_z = (15.0, 55.0)          # housing bottom on the skids, top
house_t = 4.0
wind = 12.0                     # winding bundle cross-section
skid_x = 220.0                  # 2 skids at x +-220, 40 wide, from the rear to the front of the housing
skid_w = 40.0
skid_h = 15.0
skid_nose = 60.0                # turned-up front of the skid
carrier_t = 10.0
carrier_y = (1590.0, 1720.0)

# ---------------------------------------------------------------------
# Electronics: PI board + amplifier in an IP67 box on the rear GFRP cross tube (between the boom tubes), 24 V from
# the robot; coil cable along the left tube
# ---------------------------------------------------------------------
ebox = (180.0, 120.0, 70.0)

# ---------------------------------------------------------------------
# Lift actuator: 24 V 500 N, stroke 100, outside the right bracket: base pin on a mast (2 x 8 mm plates welded to the
# right side plate), rod pin in a 40 mm slot in a GFRP lug on the outside of the right boom tube.
# In work the rod pin sits at the bottom of the slot: the boom floats (coil follows the ground).
# ---------------------------------------------------------------------
act_x = 200.0
act_base = (640.0, 930.0)       # (y, z) base pin
mast_x = ((168.0, 176.0), (222.0, 230.0))   # PE spacer bushes on the pin between plates and eye
lug_x = (152.0, 176.0)          # GFRP lug 24 mm on the outer face of the right tube
act_pin = (1000.0, 520.0)       # (y, z) rod pin in the work pose (bottom of the slot)
act_body_d = 40.0
act_rod_d = 16.0
act_retracted = 450.0
act_stroke = 100.0
float_slot = 40.0
act_force = 500.0
act_speed = 15.0
act_kg = 1.6

lift_work = 0.0
lift_transport = 14.0           # degrees, boom up about the pivot
LIFT_POSES = (-3.0, 0.0, 7.0, 14.0)    # -3: hollow in front of the robot (float down)

# ---------------------------------------------------------------------
# Detection model (mdt_calc): dipole coupling of a loop of equivalent radius a with a small target at depth z,
# S ~ k * r_e^3 * (a^2 / (a^2 + z^2))^3; k / noise from a reference: an equivalent 8 mm sphere (a coin) is found at
# 200 mm by a O250 mono coil (typical hand-held PI)
# ---------------------------------------------------------------------
ref_coil_a = 125.0
ref_target_re = 8.0
ref_depth = 200.0
threshold_snr = 1.0             # detection threshold, equal to the reference
# targets: equivalent sphere radius (mm, estimated from size and conductivity), mass (g)
TARGETS = {
    "nail_3x70": 4.0,
    "bolt_M10x60": 7.0,
    "bottle_cap": 7.0,
    "tent_peg_6x230": 7.0,
    "drink_can_alu": 22.0,
    "horseshoe": 18.0,
    "fence_wire_1m_coil": 30.0,
    "plough_point": 40.0,
}
robot_re = 250.0                # equivalent sphere of the robot front (beam, wheel brackets, hub motors) (estimated)
robot_var = 0.005               # share of the robot signal that changes while driving (vibration, steering, motor currents)
ground_noise = 2.0              # ground mineralisation / clutter after ground balancing, x the reference noise (estimated)

# ---------------------------------------------------------------------
# Work (mdt_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
gfrp = 1.9e-6
abs_ = 1.05e-6
pe = 0.95e-6
copper = 8.9e-6
nylon = 1.15e-6
speed = 1.0                     # m/s
pulse_hz = 400.0                # PI pulse rate
avg_pulses = 16                 # pulses averaged per sample -> 25 samples/s
overlap = 100.0                 # mm between passes
mu_skid = 0.35                  # PE on grass
crr = 0.06
eta_drive = 0.75
p_detector = 8.0                # W
p_logger = 15.0                 # W, logger + GNSS
battery_wh = 1900.0
heading_err_deg = 1.0           # heading of the robot from the dual GNSS / IMU
gnss_err = 20.0                 # mm RTK
# from build_mdt.mass_properties() in the work pose (update after a change of the model)
MODEL_MASS = {"fixed_kg": 8.1, "fixed_cg_y": 662.0, "boom_kg": 9.7, "boom_cg_y": 1419.0, "boom_cg_z": 230.0}
