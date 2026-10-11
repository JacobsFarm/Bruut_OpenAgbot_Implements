import math

# =====================================================================
# Weed picker (simple) - parameters
# Twin-rotor weed topper in front of the standard Bruut OpenAgbot. Cuts thistles, ragwort and dock above the grass
# (cut height 100 .. 400 mm, set by an electric actuator) and sweeps the cut material into one windrow in the middle,
# between the front wheels. No collecting bin: the weeds lie together in a narrow strip and can be picked up.
#
#   Mount:   8 mm plate under both front lower beams (8 x M10 in the hole grid), 2 lugs for a parallel linkage and a
#            double lug for the actuator.
#   Linkage: 2 top and 2 bottom links (pairs of laser-cut flat bars 40 x 6 that straddle the lugs, M16 pins). Keeps
#            the deck level over the whole height range.
#   Lift:    electric linear actuator (24 V, 4000 N, 150 mm stroke) on the diagonal of the parallelogram, with a slotted
#            float link at the robot end: the deck rests on it but can lift by itself when it touches a hump.
#   Deck:    3 mm stadium-shaped plate with a 3 mm skirt, open at the rear between the rotors (centre discharge),
#            2 short swath boards behind it, a crossbeam 50 x 40 on top with the deck lugs.
#   Rotors:  2 bought lawn-tractor deck spindles, each driven directly (jaw coupling) by a 48 V BLDC motor on 4
#            standoffs. Under each spindle a blade bar 60 x 12 with 2 free-swinging blades 50 x 6. The rotors turn
#            towards each other at the front: in the middle both sweep backwards, out of the discharge. The left rotor
#            sits 24 mm higher, so the blade circles may overlap without timing the two motors.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot. The model is drawn at the default cut height cut_h; the linkage, the deck and the
# actuator move with set_height(). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = 500.0            # wheel centres at y = +-500
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_front_beam_y = (425.0, 575.0)     # centres of the front lower beams (x direction, 1000 long)
robot_rear_beam_y = (-575.0, -425.0)
robot_lower_beam_z = (619.0, 659.0)     # bottom / top of the lower beams (world)
robot_beam = 40.0
robot_grid = 50.0               # M10 holes (10.4) at x = +-125, +-175, ... +-475 (not in the middle)
m10_hole = 10.4
gnss_xy = (0.0, 575.0)          # GNSS stud through the front outer beam, sticks out 50 mm below it
steer_max = 30.0                # deg, front wheels
fork_x = 261.0                  # inner side of the front wheel fork (x 261..489), turns with the wheel
battery_v = 48.0                # robot battery 48 V 50 Ah LiFePO4

# ---------------------------------------------------------------------
# Mount: plate under both front lower beams, lugs for the links and the actuator
# ---------------------------------------------------------------------
mount_x = (-200.0, 200.0)
mount_y = (400.0, 600.0)
mount_t = 8.0
mount_bolt_x = (-175.0, -125.0, 125.0, 175.0)    # grid holes; 8 x M10 (2 beams)
gnss_hole = 24.0                # clearance hole for the GNSS stud
lug_x = 100.0                   # link lugs at x = +-100 (robot and deck side), 10 mm plate
lug_t = 10.0
pivot_y = 440.0                 # robot-side pivots of the links
pivot_z = (390.0, 510.0)        # bottom, top
lug_z0 = 355.0                  # bottom edge of the robot lugs
act_A = (470.0, 540.0)          # (y, z) robot-side pin of the actuator (in the slot of the float link), x 0
act_lug_x = 10.0                # deck side: double lug, plates at x +-(10..18), the rod eye between them
act_lug_t = 8.0

# ---------------------------------------------------------------------
# Linkage: parallelogram, links = 2 flat bars 40 x 6 each, straddling the 10 mm lugs
# ---------------------------------------------------------------------
link_L = 440.0                  # pivot to pivot
link_w = 40.0
link_t = 6.0
link_gap = 1.0                  # washer between lug and bar
pin_d = 16.0                    # M16 pins (8.8 bolts with a lock nut)

# ---------------------------------------------------------------------
# Cut height and rotors
# ---------------------------------------------------------------------
cut_h = 200.0                   # default: bottom of the right-hand blades above the ground (model and STEP)
cut_range = (100.0, 400.0)      # set by the actuator
rotor_x = 240.0                 # rotor axes at x = +-240
rotor_dz = 24.0                 # left rotor higher (2 spacer rings 12 mm): blade circles overlap 30 mm in the middle
rpm = 2400.0                    # both rotors (BLDC speed control)
blade_r = (115.0, 255.0)        # swinging blade from r 115 to the tip at r 255: cut circle 510
blade_pivot_r = 140.0
blade_w = 50.0
blade_t = 6.0                   # flat 50 x 6, both edges bevelled (reversible, same blade left and right)
blade_gap = 1.0                 # washer between blade and bar
bar_r = 170.0                   # blade bar 340 x 60 x 12 (laser cut), rounded ends
bar_w = 60.0
bar_t = 12.0
blade_bolt_head = (30.0, 8.0)   # M16 button head under the blade (d, h): lowest point of the rotor
boss_d = 60.0                   # blade boss of the spindle
boss_h = 15.0

# deck spindle (bought, lawn-tractor type, 2 ball bearings, 3-bolt flange; dimensions estimated)
spindle_housing_d = 62.0
spindle_below = 83.0            # housing from the boss to the flange
spindle_flange_d = 130.0
spindle_flange_t = 8.0
spindle_neck = (40.0, 10.0)     # (d, h) above the flange
spindle_shaft_d = 19.0          # 3/4"
spindle_shaft_top = 45.0        # shaft stub above the flange
spindle_bolt_pcd = 110.0

# motor stand: doubler under the flange, 4 standoffs, motor plate, jaw coupling
doubler_d = 180.0
doubler_t = 6.0
spacer_d = (130.0, 64.0)        # left rotor: 2 laser-cut rings 12 mm under the flange
standoff_xy = 55.0              # standoffs at (+-55, +-55) around the rotor axis
standoff_d = 20.0               # tube 20 with an M10 rod inside
coupling_d = 55.0               # jaw coupling (L-type), bore 19 both sides
coupling_z = (22.0, 92.0)       # above the flange bottom
motor_plate = 150.0
motor_plate_t = 6.0
motor_plate_z = 98.0            # bottom of the motor plate above the flange bottom

# motor: 48 V BLDC, 750 W at 3000 rpm, here run at 2400 rpm (dimensions estimated, as the fence mower)
motor_P = 750.0
motor_rpm = 3000.0
eta_motor = 0.85                # motor + driver
motor_flange = 90.0
motor_flange_t = 10.0
motor_d = 90.0
motor_len = 140.0

# ---------------------------------------------------------------------
# Deck (hood): stadium = 2 circles r hood_r around the rotor axes, joined front and rear
# ---------------------------------------------------------------------
hood_r = 290.0                  # 35 mm outside the blade tips
deck_t = 3.0
skirt_t = 3.0
skirt_below = 10.0              # skirt bottom below the right blades (left: 34 below)
discharge_half = 200.0          # rear opening x -200 .. 200 (between the rotors)
swath_len = 150.0               # 2 swath boards behind the opening, 4 mm, converge to x +-160
swath_end_x = 160.0
swath_t = 4.0
crossbeam = (50.0, 40.0, 3.0)   # RHS 50 x 40 x 3 across the deck (y x z), |x| <= 470
crossbeam_x = 470.0
deck_pivot_dy = 185.0           # rotor axes 185 mm in front of the deck pivots
deck_pivot_dz = 45.0            # bottom deck pivot above the deck top (top pivot +120)
deck_lug_dy = 35.0              # deck lugs y = pivot +-35
deck_lug_h = 190.0
deck_notch = 40.0               # deck plate cut back between the rotors to 40 mm behind the deck pivots (links)

# ---------------------------------------------------------------------
# Actuator (bought): 12/24 V linear actuator 4000 N, 150 mm stroke, 255 mm pin to pin closed (estimated). Rod eye on
# the deck (pin B), rear eye on a float link: 2 flat bars 30 x 6 that hang on the robot pin A with a 60 mm slot
# (rear eye to the end of the slot 90 mm). The deck rests on it and can lift by itself (60 mm along the actuator).
# ---------------------------------------------------------------------
act_closed = 255.0
act_stroke = 150.0
act_F = 4000.0                  # N (holding the deck takes about 1.8 kN: the diagonal has a short lever)
act_speed = 10.0                # mm/s under load
act_tube_d = 50.0
act_rod_d = 20.0
act_eye_t = 10.0
act_motor = (60.0, 50.0, 110.0)     # motor box beside the tube (estimated)
float_len = 90.0
float_slot = 60.0
float_bar = (30.0, 6.0)

# ---------------------------------------------------------------------
# Controller box 260 x 180 x 90 (2 BLDC drivers 48 V / 25 A, DC-DC 48/24 V, relay for the actuator, fuses) on the
# rear lower beams, M8 through the grid holes x +-125
# ---------------------------------------------------------------------
box_x = (-130.0, 130.0)
box_y = (-590.0, -410.0)
box_h = 90.0
box_base_t = 3.0
box_base_x = (-150.0, 150.0)
box_base_y = (-600.0, -400.0)

# ---------------------------------------------------------------------
# Operation (for wpk_calc, the weed model and the animation)
# ---------------------------------------------------------------------
drive_speed = 0.5               # m/s
cd_blade = 1.2                  # blade edgewise (6 mm with a bevel), conservative
rho_air = 1.2
idle_W = 25.0                   # per rotor: spindle bearings, coupling
e_chop = 4000.0                 # J/kg fresh weed: cutting, chopping under the deck and throwing it out (estimated)
windrow_share = 0.85            # of the cut material that ends up in the windrow (rest scattered in the cut strip)
windrow_w = 320.0               # mm, the windrow width behind the swath boards
windrow_bulk = 60.0             # kg/m3, chopped fresh weeds, loose
drive_W = 200.0                 # driving on grassland with the deck (estimated)


# ---------------------------------------------------------------------
# Derived geometry
# ---------------------------------------------------------------------
DECK_H = blade_t + blade_gap + bar_t + boss_h + spindle_below - doubler_t    # 111: deck top above the cut height
CUT_W = 2 * (rotor_x + blade_r[1])                                             # 990
OVERLAP = 2 * blade_r[1] - 2 * rotor_x                                         # 30
TIRE_SWEEP_R = math.hypot(robot_tire_d / 2.0, robot_tire_w / 2.0)              # 221 around the wheel axis


def deck_top(cut=None):
    return (cut_h if cut is None else cut) + DECK_H


def theta(cut=None):
    """Link angle (deg, + = deck end up) for a cut height."""
    return math.degrees(math.asin((deck_top(cut) + deck_pivot_dz - pivot_z[0]) / link_L))


def deck_pivot(cut=None):
    """(y, z) of the bottom deck pivot for a cut height."""
    t = math.radians(theta(cut))
    return pivot_y + link_L * math.cos(t), pivot_z[0] + link_L * math.sin(t)


def deck_shift(cut, cut0=None):
    """(dy, dz) of the deck from its position at cut0 (default cut_h) to cut."""
    y1, z1 = deck_pivot(cut)
    y0, z0 = deck_pivot(cut0)
    return y1 - y0, z1 - z0


def rotor_y(cut=None):
    return deck_pivot(cut)[0] + deck_pivot_dy


def act_length(cut=None):
    """Pin A to pin B (deck side, = bottom deck pivot at x 0)."""
    yb, zb = deck_pivot(cut)
    return math.hypot(yb - act_A[0], zb - act_A[1])


Y_PIVOT0, Z_PIVOT0 = deck_pivot()         # bottom deck pivot at the default cut height
YC0 = rotor_y()                           # rotor axes at the default cut height (1062)
DT0 = deck_top()                          # deck top at the default cut height (311)
