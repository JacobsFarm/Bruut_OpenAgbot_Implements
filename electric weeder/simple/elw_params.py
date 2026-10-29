import math

# =====================================================================
# Electric weeder (simple) - parameters
# Spot electric weed control in the free middle inter-row of a 2-row bed (rows 375 apart) under the Bruut OpenAgbot
# (standard robot). A camera under the front beams finds weeds in the band; when one comes under the applicator, a
# 5 kV generator (fed from the 48 V battery) switches on a comb of spring-steel fingers that drags over the band, the
# current runs through the weed into the soil and back through a coulter disc. A parallel-arm lift with a 24 V
# actuator takes the comb off the ground on headlands and roads. Rubber curtains on the sides; HV only on a weed.
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
robot_lower_beam_z = (619.0, 659.0)
robot_front_beam_y = (425.0, 575.0)
robot_mass = 160.0
robot_steer_deg = 30.0
m10_hole = 10.4

# Crop: 2 rows at x +-187.5; everything below crop_h stays out of x row +- row_band
row_x = 187.5
row_band = 80.0
crop_h = 400.0

# ---------------------------------------------------------------------
# Bearer 40 x 40 x 3 across the 4 upper beams at y -325 (beam holes, M10 at x +-325 / +-425); post 40 x 40 x 3 at x 0
# hangs from it down to z 420 and carries the lift arms and the coulter arm. HV box on top of the bearer.
# ---------------------------------------------------------------------
bearer_x = 470.0
bearer_y = -325.0
bearer_bolt_x = (325.0, 425.0)
post_z0 = 400.0
hv_box = (300.0, 200.0, 160.0)  # x, y, z: 48 V -> 5 kV generator, contactor, insulation monitor
hv_box_y = -380.0               # centre; behind the bearer middle so the actuator clears it
beacon = (60.0, 80.0)           # warning light O60 x 80 on the box

# ---------------------------------------------------------------------
# Parallel lift: 2 arms 30 x 20 x 2 (upper and lower) from lugs on the front of the post to a carrier; arms
# horizontal in work (lift 0); 24 V actuator from a lug on the post to the upper arm
# ---------------------------------------------------------------------
pivot_y = -290.0                # arm pivots on the post (y)
pivot_z = (600.0, 450.0)        # upper, lower arm
arm_len = 400.0
arm = (20.0, 30.0)              # x, z of the arm tube
pin_d = 12.0
act_base = (-285.0, 720.0)      # (y, z) actuator base pin on 2 lugs on the front of the bearer
act_arm = 200.0                 # actuator rod pin on the upper arm, distance from its pivot
act_pin_up = 30.0               # rod pin above the arm axis (lug on the arm); rod eye O24 clears the arm
act_body_d = 45.0
act_rod_d = 16.0
act_retracted = 170.0           # pin to pin
act_stroke = 55.0
lift_work = 0.0
lift_transport = 20.0
LIFT_POSES = (-4.0, 0.0, 10.0, 20.0)   # -4: comb follows a hollow

# ---------------------------------------------------------------------
# Applicator: PE holder 190 x 60 x 40 on the carrier foot, 9 spring-steel fingers O4 dragging back on the band,
# rubber curtains 3 mm on both sides (x +-95..98)
# ---------------------------------------------------------------------
holder_x = 95.0
holder_y = (85.0, 145.0)        # relative to nothing: world y in work
holder_z = (120.0, 160.0)
finger_d = 4.0
finger_n = 9
finger_tip = (30.0, 4.0)        # (y, z) of the finger tips in work
curtain_t = 3.0
curtain_y = (15.0, 150.0)
curtain_z = (20.0, 160.0)
band_w = 0.18                   # m, width the fingers cover

# ---------------------------------------------------------------------
# Earth return: coulter disc O250 x 4 at x 0 behind the post, on a sprung arm; 10 mm in the soil
# ---------------------------------------------------------------------
disc_d = 250.0
disc_t = 4.0
disc_c = (-480.0, 115.0)        # (y, z) hub
disc_arm_t = 8.0

# ---------------------------------------------------------------------
# Camera under the front lower beams at x 0 (looks down at the band ~0.5 m ahead of the comb)
# ---------------------------------------------------------------------
cam_plate = (300.0, 10.0)       # x length, thickness; under the inner front lower beam (the GNSS stud is at y 560..590)
cam_plate_y = (395.0, 475.0)
cam_box = (100.0, 70.0, 60.0)
cam_bolt_x = 125.0

# ---------------------------------------------------------------------
# Work (for elw_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
pe = 0.95e-6
alu = 2.7e-6
rubber = 1.3e-6
hv_kV = 5.0
hv_power_W = 3000.0             # generator output while a weed is under the comb
eta_hv = 0.85
comb_len = 0.12                 # m along y in contact with the ground
speed = 0.2                     # m/s, so a weed is under the comb 0.6 s (4-leaf weeds need <= 0.24 m/s)
weed_energy_kJ = {"cotyledon": 0.5, "4_leaf": 1.5, "rosette_50mm": 4.0}    # to kill incl. root (estimated)
weeds_m2 = (5.0, 20.0, 50.0)    # in the band
broadcast_kWh_ha = 60.0         # continuous electric weeding of the full band (literature range 30-200, estimated)
idle_W = 60.0                   # camera, computer, generator stand-by
crr = 0.08
eta_drive = 0.75
robot_battery_wh = 1900.0
field_eff = 0.8
pass_w = 0.75
hv_kg = 9.0
act_kg = 1.2
cam_kg = 0.6
# from build_elw.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 26.7}


def upper_arm_point(lift_deg, dist):
    """(y, z) of a point on the upper arm at 'dist' from its pivot, at a lift angle."""
    a = math.radians(lift_deg)
    return (pivot_y + dist * math.cos(a), pivot_z[0] + dist * math.sin(a))


def act_rod_pin(lift_deg):
    """(y, z) of the actuator rod pin on the upper arm."""
    a = math.radians(lift_deg)
    y, z = upper_arm_point(lift_deg, act_arm)
    return (y - act_pin_up * math.sin(a), z + act_pin_up * math.cos(a))


def act_length(lift_deg):
    y, z = act_rod_pin(lift_deg)
    return math.hypot(y - act_base[0], z - act_base[1])
