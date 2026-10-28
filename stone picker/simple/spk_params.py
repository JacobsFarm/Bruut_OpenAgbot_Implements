import math

# =====================================================================
# Stone picker (simple) - parameters
# Mid-mounted under the Bruut OpenAgbot (standard robot), between the axles: a tine rotor 1 m wide at the front flicks
# stones backwards over a comb into a sieve basket (soil falls through the floor bars). The frame hangs on 4 swing
# links from the upper beams (parallelogram: it stays level), one linear actuator lifts it. At the field edge the
# hinged sieve floor opens and the stones are left in a heap that the robot drives over (it is between the wheels).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_r = 265.0            # lugged tyre in the model (bounding box O530 x 100)
robot_tire_w = 100.0
robot_tire_inner_x = 325.0
robot_bracket_inner_x = 263.0   # inner fork plate of the wheel units, y +-(418..582), z 180..564
robot_upper_beam_x = (325.0, 425.0)     # centres per side, 40 wide, y -650..650
robot_upper_beam_z = (659.0, 699.0)
robot_steer_deg = 30.0
robot_mass = 160.0              # kg, estimated
robot_cg_y = 0.0
robot_cg_z = 380.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Hangers: 4 x (top plate 10 mm under the OUTER upper beam, 2 x M10, web 10 mm down to the link pivot). Between the
# axles (y -235..235) there are no tyres, so the links and side beams run outside the wheel line (x +-505..565).
# ---------------------------------------------------------------------
hanger_y = (-115.0, -355.0)     # front, rear (centre of the web, y); the rear top plate stays in front of the
                                # rear inner lower beam (y -405)
hanger_web_x = (555.0, 565.0)
hanger_top = (395.0, 565.0, 10.0)       # top plate x0, x1, thickness (under the outer upper beam, z 649..659)
hanger_top_len = 80.0           # along y
hanger_pivot_z = 493.0
pin_d = 16.0

# ---------------------------------------------------------------------
# Swing links: flat bar 40 x 8, 250 between pins; angle from vertical (+ = lower end in front of the upper end).
# From 55 to 80 degrees the frame rises 100 mm and moves 41 mm forward, staying level (parallelogram).
# ---------------------------------------------------------------------
link_len = 250.0
link = (40.0, 8.0)
link_x = (546.0, 554.0)         # between the frame side beam and the hanger web
theta_work = 55.0
theta_lift = 80.0
THETA_POSES = (55.0, 67.5, 80.0)

# ---------------------------------------------------------------------
# Frame (work pose): 2 side beams 40 x 40 x 3 at x +-(505..545) that carry the rotor bearing plates, front cross tube
# 60 x 40 x 3 over the rotor, rear cross tube 40 x 40 x 3 that carries the basket, 2 top stays to the basket rear
# ---------------------------------------------------------------------
side_beam_x = (505.0, 545.0)
frame_z = (330.0, 370.0)        # side beams and rear cross tube; the front cross tube is z 300..340
side_beam_y = (-220.0, 110.0)
cross_y = (-30.0, 30.0)
cross_z = (300.0, 340.0)
rear_cross_y = (-200.0, -160.0)
brg_plate_t = 8.0
brg_plate_x = 505.0             # inner face of the bearing plates (x = +-505), under the side beams

# ---------------------------------------------------------------------
# Rotor: tube O114 x 4 with 6 rows of double spring tines (wire O9), tip radius 150, tips 20 mm in the soil
# ---------------------------------------------------------------------
rotor_y = 0.0
rotor_z = 130.0
rotor_tube = 114.0
rotor_len = 990.0
tip_r = 150.0
tine_wire = 9.0
tine_rows = 6
tines_per_row = 8               # double tines (2 legs each) per row, staggered between rows
tine_lean = 25.0                # degrees the tine trails behind the radius (spring tine)
shaft_d = 25.0
brg_sq = 86.0                   # UCFL205
brg_flange = 13.0
brg_body_d = 62.0
brg_depth = 33.0
rotor_rpm = 250.0
# rotor drive: 48 V 750 W BLDC gearmotor (planetary), right end, on the bearing plate
gm_d = 110.0
gm_len = 200.0

# ---------------------------------------------------------------------
# Basket (welded to the frame): walls 3 mm, comb of 12 mm bars at the front, sieve floor hinged at the front
# ---------------------------------------------------------------------
basket_x = 244.0                # outside half width (walls x +-241..244)
basket_y = (-490.0, -200.0)     # rear wall .. front (comb root); x +-244 stays inside the rear forks (263)
basket_top = 340.0
wall_t = 3.0
floor_z = 50.0                  # top of the floor bars at the front hinge (work pose)
floor_bar = 12.0
floor_gap = 25.0                # stones under 25 mm fall through with the soil
comb_tip = (-160.0, 10.0)       # (y, z) of the comb tips
comb_root_z = 62.0
comb_bars = 13
deflector_t = 3.0               # side deflectors from the rotor ends to the basket corners
door_open = 20.0                # degrees the floor drops to empty (lifted: the actuator lug stays 16 mm above the ground)

# Door actuator: 24 V 500 N, stroke 150, behind the basket rear wall (x 0)
door_base = (-540.0, 330.0)     # (y, z) base pin on a lug on the rear wall
door_body_d = 40.0
door_rod_d = 16.0

# ---------------------------------------------------------------------
# Lift actuator: 24 V 1500 N, stroke 150, nearly upright from a lug on a bearer across the upper beams to the rear
# cross tube (it pulls the frame up)
# ---------------------------------------------------------------------
bearer_y = -270.0                # behind the actuator, the lug reaches forward to the base pin
bearer = 40.0
bearer_x = 470.0
act_base = (-210.0, 820.0)      # (y, z) base pin on the lug on top of the bearer
act_rod = (-180.0, 392.0)       # (y, z) rod pin on the lug of the rear cross tube, work pose
act_body_d = 60.0
act_rod_d = 20.0
act_retracted = 300.0
act_stroke = 150.0
act_force = 1500.0
act_speed = 10.0                # mm/s at load (estimated)

# ---------------------------------------------------------------------
# Work (spk_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
stone_bulk = 1550.0             # kg/m3, stones 25..150 mm loose in the basket (estimated)
basket_fill = 0.7               # usable share of the basket (stones pile at the front, estimated)
STONES = {"light_seedbed": 0.05, "stony_seedbed": 0.2, "very_stony": 0.5}     # kg of stones > 25 mm per m2
speed = 0.5                     # m/s working speed
work_w = 1.0                    # m, rotor width
depth = 20.0                    # mm, tine depth
e_soil = 30.0                   # kJ/m3 to rake the top layer with spring tines (estimated)
p_idle = 120.0                  # W rotor, bearings and gearbox losses
eta_gm = 0.8
comb_draft = 150.0              # N, comb and skid drag in work (estimated)
headland_m = 60.0               # average drive to the heap and back per basket (estimated)
dump_s = 40.0                   # lift, open, drive off, close, lower
battery_wh = 1900.0
crr = 0.06
mu_tyre = 0.45
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
eta_drive = 0.75
wheelbase_half = robot_axle_y
track_half = robot_wheel_x
# from build_spk.mass_properties() in the work pose (update after a change of the model)
MODEL_MASS = {"picker_kg": 91.5, "picker_cg": (57, -134, 256), "lift_kg": 73.6, "links_kg": 5.4,
              "basket_cg": (0, -345, 150)}         # basket_cg: stones, estimated from the fill


def link_offset(theta_deg):
    """(dy, dz) of the lower link pin from the upper pin."""
    a = math.radians(theta_deg)
    return link_len * math.sin(a), -link_len * math.cos(a)


def frame_shift(theta_deg):
    """(dy, dz) of the frame relative to the work pose."""
    y0, z0 = link_offset(theta_work)
    y1, z1 = link_offset(theta_deg)
    return y1 - y0, z1 - z0


def act_length(theta_deg):
    dy, dz = frame_shift(theta_deg)
    return math.hypot(act_rod[0] + dy - act_base[0], act_rod[1] + dz - act_base[1])


def basket_volume():
    """Inside volume (l) of the basket above the floor."""
    w = 2.0 * (basket_x - wall_t)
    return w * (basket_y[1] - basket_y[0] - wall_t) * (basket_top - floor_z) * 1e-6
