import math

# =====================================================================
# Cambridge roll, simple - parameters
# A 1 m ring roller trailed behind the robot on a simple tow hitch (50 mm tow ball). It firms the seedbed and
# presses seed into the soil after overseeding. Cheap: bought cast-iron Cambridge rings, a bright steel shaft,
# two flange bearings, standard rectangular tube and one laser-cut plate set.
#
# The tow hitch (bracket under the robot + ball) is defined here; the overseeder and the combination use it.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres at (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = -500.0           # rear axle (front axle +500)
robot_wheelbase = 1000.0
robot_track = 750.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_tire_rear_y = robot_axle_y - robot_tire_d / 2.0     # -715
robot_rear_beam_y = (-575.0, -425.0)    # centre lines of the rear lower beams (40 x 40)
robot_beam = 40.0
robot_lower_beam_z = (619.0, 659.0)     # bottom and top of the lower beams (world)
robot_bracket_x = 261.0                 # inner face of the rear wheel brackets
robot_grid = 50.0               # hole grid of the beams, M10 (hole 10.4)
robot_max_steer = 30.0          # degrees, steering stop of the front wheels
robot_mass = 150.0              # kg, estimated (batteries included)
robot_mu = (0.45, 0.65)         # traction coefficient of the 4.00-8 tractor tyres on wet / dry grass (estimated)
m10_hole = 10.4
m20_hole = 21.0

# ---------------------------------------------------------------------
# Tow hitch: top plate under both rear lower beams (4 x M10 in the grid), a vertical leg and a horizontal bar of
# square tube 60 x 60 x 5, gusset, and a bolt-on tow ball 50 mm (ISO 1103) on the end of the bar.
# The ball is 115 mm behind the rear tyres: the coupling head (front at -785) stays clear of them.
# ---------------------------------------------------------------------
hitch_plate = ((-200.0, 200.0), (-610.0, -390.0), (robot_lower_beam_z[0] - 10.0, robot_lower_beam_z[0]))
hitch_bolts = ((-175.0, 175.0), robot_rear_beam_y)      # x, y of the 4 M10 bolts
hitch_tube = 60.0               # square tube 60 x 60 x 5
hitch_tube_t = 5.0
hitch_leg_y = (-500.0, -440.0)
hitch_bar_y = (-880.0, -440.0)
hitch_bar_z = (205.0, 265.0)
hitch_gusset = (8.0, -500.0, -650.0, 420.0)     # thickness, y at the leg, y at the bar end, z at the top of the leg
ball = (0.0, -830.0)            # x, y of the ball axis
ball_d = 50.0
ball_flange = (60.0, 12.0)      # diameter, thickness (on top of the bar, M20 stud through the bar)
ball_neck = (32.0, 28.0)        # diameter, height
ball_z = hitch_bar_z[1] + ball_flange[1] + ball_neck[1] + ball_d / 2.0      # 330, ball centre
ball_stud = (20.0, 95.0)        # M20 stud below the flange, nut under the bar

# Coupling head (bought, 50 mm ball, for a 60 x 60 drawbar). Drawn as a block with a socket; the drawbar slides
# into the back and is bolted with 2 x M12. It rotates about the ball centre.
coupling_y = (-950.0, ball[1] + 45.0)   # rear end, front of the rounded nose (-785)
coupling_w = 80.0
coupling_z = (312.0, 372.0)
coupling_nose_d = 90.0
coupling_handle = (24.0, 140.0)  # width, length of the latch handle on top
coupling_socket = 20.0          # drawbar inside the head
drawbar_z = (coupling_z[0], coupling_z[1])      # drawbar 60 x 60 centred in the head
DRAWBAR_FRONT_Y = coupling_y[0] + coupling_socket   # -930, front end of every drawbar

# ---------------------------------------------------------------------
# Roll: 20 Cambridge rings (cast iron, bought as spare parts) on a shaft O40, rings turn freely and independently
# (that is what lets a Cambridge roll turn without tearing the sward). Ring outline (x along the axle, r):
# hub r 21..32 over the full width, web 8 mm, rim r 110..116, ridge (V) r 116..140, base 30, tip 6.
# ---------------------------------------------------------------------
ring_n = 20
ring_w = 50.0
ring_bore = 42.0                # loose on the O40 shaft
ring_hub_r = 32.0
ring_web = (21.0, 29.0)         # x of the web inside the ring
ring_rim_r = (110.0, 116.0)
ring_ridge = (10.0, 40.0, 22.0, 28.0)   # base x0, x1, tip x0, x1
ring_od = 280.0
roll_x = (-ring_n * ring_w / 2.0, ring_n * ring_w / 2.0)  # -500 .. 500
axle_z = ring_od / 2.0          # 140
cast_iron = 7.2e-6              # kg/mm3

shaft_d = 40.0                  # bright steel C45
shaft_x = 595.0                 # shaft from -595 to 595
collar = (65.0, 13.0)           # shaft collar (OD, width) inside the side plates, holds the rings together

# Side plates (10 mm, laser cut) with the bearings on the outside
side_plate_x = (515.0, 525.0)
side_plate_dy = 110.0           # y = axle +- 110
side_plate_z = (40.0, 300.0)
# UCFL208 2-bolt flange bearing (O40): oval flange along z, boss outwards
bearing_flange = (175.0, 100.0, 15.0)   # length (z), width (y), thickness
bearing_bolts = 144.0           # bolt distance (z)
bearing_boss = (85.0, 35.0)     # diameter, length beyond the flange
bearing_kg = 2.1

# Frame: two arms (square tube 40 x 40 x 3) on top of the side plates, a front cross beam of the same tube, and a
# drawbar 60 x 60 x 4 to the coupling head, braced by two 40 x 40 x 3 tubes.
arm_x = (side_plate_x[0], side_plate_x[0] + 40.0)       # 515 .. 555
arm_z = (side_plate_z[1], side_plate_z[1] + 40.0)       # 300 .. 340
rhs_t = 3.0
cross_w = 40.0                  # front cross beam: 40 in y, 40 high
drawbar = (60.0, 4.0)
brace = (40.0, 3.0)
brace_y = 380.0                 # braces meet the drawbar this far in front of the cross beam
roll_front_gap = 250.0          # stand-alone roll: cross beam (rear face) this far in front of the axle

# Position of the stand-alone roll
roll_axle_y = -1900.0
cross_y = roll_axle_y + roll_front_gap      # -1650 (rear face)

# Parking leg: square tube 40 x 40 pinned on a lug on the side of the drawbar, swung up (stowed) in the work
# position, above the braces
park_leg = (40.0, 3.0, 300.0)   # tube, wall, length
park_leg_y = 300.0              # pin this far behind the front end of the drawbar (same for every drawbar length)

steel = 7.85e-6

# ---------------------------------------------------------------------
# Operation (cbr_calc)
# ---------------------------------------------------------------------
work_speed = 0.5                # m/s
field_eff = 0.75                # turning, refilling
f_roll = {"firm lawn": 0.06, "moist lawn": 0.09, "loose seedbed (bare patch)": 0.15}    # rolling resistance (estimated)
slope_deg = 5.0                 # design slope for the draft force


def ring_profile():
    """Half section of one ring (x along the axle from the ring face, r), counter-clockwise."""
    b, h = ring_bore / 2.0, ring_hub_r
    w0, w1 = ring_web
    r0, r1 = ring_rim_r
    a0, a1, t0, t1 = ring_ridge
    R = ring_od / 2.0
    return [(0.0, b), (ring_w, b), (ring_w, h), (w1, h), (w1, r0), (ring_w, r0), (ring_w, r1), (a1, r1), (t1, R),
            (t0, R), (a0, r1), (0.0, r1), (0.0, r0), (w0, r0), (w0, h), (0.0, h)]


def ring_volume():
    """Pappus: area x 2 pi x centroid radius of the profile (mm3)."""
    pts = ring_profile()
    a = cx = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        c = x0 * y1 - x1 * y0
        a += c
        cx += (y0 + y1) * c
    a *= 0.5
    yc = cx / (6.0 * a)
    return abs(a) * 2.0 * math.pi * abs(yc)
