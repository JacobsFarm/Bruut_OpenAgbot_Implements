import math

# =====================================================================
# Triple sickle bar mower - parameters
# Three double-knife cutter bars on the standard Bruut OpenAgbot: one of 1.25 m in front of the robot and two wings of
# 1.0 m left and right in the middle of the frame (between the front and rear wheels). Working width 3.25 m.
#
#   Front:   mount plate under both front lower beams (as the weed picker), parallel linkage (2 x 2 flat bars), a
#            head frame on the links and the bar frame on a roll pin (along y) in the head frame, so the bar follows
#            the ground across. Electric actuator on the diagonal with a slotted float link: the bar rests on its
#            shoes and floats up and down; the actuator lifts it 300 mm for turning and transport.
#   Middle:  mid frame = 2 rails under the outer top beams (4 x M10 each, grid holes y +-275, +-325) with a cross
#            tube under them at y 0. At each end 2 hanger plates down to the wing hinge (pin along y). In the middle a
#            post with the anchors of the two wing actuators (pins in slots: float).
#   Wings:   the bar hangs on the hinge with its inner shoe; a lever (2 plates) on the hinge tube, an actuator from
#            the post folds the wing up to vertical (transport width 1.44 m). The knife drive sits at the outer end.
#   Bars:    the same module for all three: flat bar 80 x 8 with an RHS 50 x 30 behind it, upper and lower knife
#            (sections 50 mm pitch, 4 mm, riveted to a knife back 25 x 5), hold-down clips, 2 shoes (skids), a
#            gearbox with 2 cranks (stroke 50, 180 deg apart) and con-rods to the knife heads, 48 V BLDC motor on top.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm. Origin = centre of the
# robot. A bar is drawn in its own frame (u along the bar from the start of the knife towards the drive end, w
# forward from the knife back edge, z up) and mapped to robot coordinates in sbm_parts. All dimensions are here.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = 500.0            # wheel centres at y = +-500
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_front_beam_y = (425.0, 575.0)     # centres of the front lower beams (x direction, 1000 long, x -500 .. 500)
robot_rear_beam_y = (-575.0, -425.0)
robot_lower_beam_z = (619.0, 659.0)     # bottom / top of the lower beams (world)
robot_upper_beam_x = (325.0, 425.0)     # centres of the top beams (y direction, 1300 long), both sides
robot_upper_beam_z = (659.0, 699.0)
robot_upper_hole_y = (275.0, 325.0)     # first grid holes of the top beams (they start at |y| 275)
robot_beam = 40.0
robot_grid = 50.0
m10_hole = 10.4
gnss_xy = (0.0, 575.0)          # GNSS stud through the front outer beam, sticks out 50 mm below it
steer_max = 30.0                # deg, front wheels
battery_v = 48.0                # robot battery 48 V 50 Ah LiFePO4

# ---------------------------------------------------------------------
# Working width
# ---------------------------------------------------------------------
front_L = 1250.0                # cut width of the front bar, x -625 .. 625
wing_L = 1000.0                 # cut width of each wing, x 625 .. 1625 (no overlap: total 3.25 m as asked)
cut_h = 60.0                    # cut plane above the ground (between the knives), set by the shoes
cut_range = (40.0, 90.0)        # shoe soles can be bolted in 3 holes (not modelled)

# ---------------------------------------------------------------------
# Cutter bar module (local frame u, w, z; the knife spans u 0 .. L)
# ---------------------------------------------------------------------
pitch = 50.0                    # section pitch = stroke (double knife: each section passes one full section)
stroke = 50.0
crank_rpm = 600.0               # 10 cycles/s: knife mean speed 1.0 m/s, relative 2.0 m/s
sec_back = -25.0                # section from w -25 (under the knife back) ...
sec_tip = 60.0                  # ... to the tip at w 60
sec_tip_w = 12.0                # width of the blunt tip
sec_gap = 2.0                   # between neighbouring sections
sec_t = 4.0
kback = (25.0, 5.0)             # knife back flat 25 x 5 (w -25 .. 0)
beam = (80.0, 8.0)              # bar: flat 80 x 8, w -95 .. -15, top 9 below the cut plane
beam_w0 = -95.0
stiff = (50.0, 30.0, 3.0)       # RHS 50 x 30 x 3 behind the flat bar (w -145 .. -95), bottom flush with the flat bar
clip_n = {"front": 5, "wing": 4}
clip_wu = 40.0                  # hold-down clip: 40 wide (u), top 6 thick over the upper knife back, web 12
clip_t = 6.0
clip_web = 12.0
shoe_in = (-95.0, -35.0)        # inner shoe (u), the knives reach u -25 at the end of the stroke
shoe_w = (-260.0, 60.0)         # shoes: sole from w -260 to the nose at w 60, pressed from 5 mm plate (open on top)
shoe_t = 5.0
shoe_out = 80.0                 # outer shoe under the drive: u L+150 .. L+230
head_u = (5.0, 35.0)            # knife heads at u L+5 .. L+35, pins at u L+20
head_pin_w = (-10.0, -44.0)     # upper, lower knife head pin (w)
crank_u = (130.0, 200.0)        # crank axes (u - L): upper knife, lower knife (2 output shafts of the gearbox)
crank_w = (-10.0, -44.0)
rod_z = ((30.0, 38.0), (20.0, 28.0))    # con-rods above the cut plane: upper, lower
rod_w = 16.0
box_u = (100.0, 240.0)          # gearbox (u - L), w -110 .. 20, z c+50 .. c+130 (cast housing, bought)
box_w = (-110.0, 20.0)
box_z = (50.0, 130.0)
motor_uw = (160.0, -45.0)       # motor axis (u - L, w)
gear_d, gear_h = 90.0, 70.0     # planetary 5:1 on the gearbox
motor_d, motor_h = 110.0, 150.0     # 48 V BLDC 1000 W, 3000 rpm
drive_plate_u = (222.0, 234.0)  # plate between the outer shoe and the gearbox

# motor and drive (estimated)
motor_P = 1000.0                # W continuous at 3000 rpm
motor_rpm = 3000.0
gear_ratio = 5.0
eta_motor = 0.85                # motor + driver
eta_gear = 0.90                 # planetary + crank gearbox

# ---------------------------------------------------------------------
# Front: mount, linkage, head frame, bar frame
# ---------------------------------------------------------------------
y_front = 1020.0                # knife back edge (w 0) of the front bar
x_front0 = -front_L / 2.0       # u 0 of the front bar (drive end on the right)
mount_x = (-200.0, 200.0)
mount_y = (400.0, 600.0)
mount_t = 8.0
mount_bolt_x = (-175.0, -125.0, 125.0, 175.0)    # grid holes; 8 x M10 (2 beams)
gnss_hole = 24.0
lug_x = 100.0                   # link lugs at x = +-100 (robot and head side), 10 mm plate
lug_t = 10.0
pivot_y = 440.0                 # robot-side pivots of the links
pivot_z = (390.0, 510.0)        # bottom, top
lug_z0 = 355.0
act_A = (470.0, 540.0)          # (y, z) robot-side pin of the front actuator, x 0
link_L = 440.0
link_w = 40.0
link_t = 6.0
link_gap = 1.0
pin_d = 16.0                    # M16 pins
head_y = 820.0                  # head-side link pivots in work position (z follows from link_L)
head_plate_y = (850.0, 860.0)   # head frame front plate 10 mm (x -160 .. 160, z 110 .. 330)
head_plate_x = 160.0
head_plate_z = (110.0, 330.0)
head_lug_y = (790.0, 850.0)
act_lug_x = 10.0                # double actuator lug on the head frame, plates x +-(10..18)
act_lug_t = 8.0
roll_z = 230.0                  # roll pin (along y) at x 0
roll_pin_d = 30.0               # M30 bolt
roll_max = 6.0                  # deg, stops (rubber buffers, not modelled)
tube_y = (880.0, 920.0)         # bar frame cross tube RHS 60 x 40 x 3 (z roll_z +-30), x -500 .. 500
tube_x = 500.0
tube_h = 60.0
tube_t = 3.0
arm_x = 420.0                   # 2 arm plates 10 mm at x +-420 from the stiffener up to the tube
arm_t = 10.0
lift_work = -40.0               # actuator setting in work: 40 mm below the ground, the bar rests on its shoes
lift_max = 300.0                # lifted for turning / transport

# front actuator (bought): 24 V, 4000 N, 150 mm stroke, 300 pin to pin closed; float link 105 with a 60 mm slot
act_closed = 300.0
act_stroke = 150.0
act_F = 4000.0
act_speed = 15.0                # mm/s under load
act_tube_d = 50.0
act_rod_d = 20.0
act_motor = (60.0, 50.0, 110.0)
float_len = 105.0             # rear eye to the end of the slot: the eye stays 45 mm from pin A
float_slot = 60.0
float_bar = (30.0, 6.0)

# ---------------------------------------------------------------------
# Middle: mid frame, wings
# ---------------------------------------------------------------------
x_wing0 = front_L / 2.0         # u 0 of the right wing (left wing mirrored)
y_wing = 140.0                  # knife back edge (w 0) of the wings
rail_y = 350.0                  # 2 rails RHS 40 x 40 x 3 under the outer top beams, y -350 .. 350
cross = (80.0, 60.0, 4.0)       # cross tube RHS 80 (y) x 60 (z) x 4 under the rails, x -610 .. 610
cross_x = 610.0
hanger_x = (510.0, 610.0)       # hanger plates 12 mm at y +-(40 .. 52), from the hinge up to the cross tube
hanger_t = 12.0
hanger_box_z = 360.0            # above this the 2 hanger plates are closed to a box by 2 webs 12 mm (x 510, 598)
hinge = (560.0, 160.0)          # wing hinge (x, z), pin along y
hinge_pin_d = 30.0
hinge_tube = (60.0, 31.0)       # on the wing, y -38 .. 38
lever_r = 150.0                 # lever: pin B at 150 from the hinge, 45 deg up and out in work
lever_deg = 45.0
lever_plate_y = (12.0, 20.0)    # 2 lever plates at y +-(12 .. 20), 8 mm
post_x = 75.0                   # actuator post under the cross tube: 2 plates 8 mm at y +-(11 .. 19), x -75 .. 75
post_y = (11.0, 19.0)
anchor_x = (20.0, 70.0)         # slot of each wing actuator anchor pin (right wing; left mirrored)
anchor_slack = 15.0             # in work the pin sits 15 mm in from the outer end: the wing can float down

# wing actuators (bought): 24 V, 4000 N, 250 mm stroke, 375 pin to pin closed (estimated)
wact_closed = 375.0
wact_stroke = 250.0
wact_F = 4000.0
wact_speed = 20.0               # mm/s
wact_tube_d = 50.0
wact_rod_d = 20.0
fold_max = 90.0                 # deg, transport

# ---------------------------------------------------------------------
# Controller box 300 x 180 x 90 (3 BLDC drivers 48 V / 30 A, DC-DC 48/24 V, 3 relays for the actuators, fuses) on the
# rear lower beams, M8 through the grid holes x +-175 (beside the box)
# ---------------------------------------------------------------------
box_x = (-150.0, 150.0)
box_y = (-590.0, -410.0)
box_h = 90.0
box_base_t = 3.0
box_base_x = (-200.0, 200.0)
box_bolt_x = (-175.0, 175.0)
box_base_y = (-600.0, -400.0)

# ---------------------------------------------------------------------
# Operation (for sbm_calc and the animation; estimated, not measured)
# ---------------------------------------------------------------------
drive_speed = 1.0               # m/s (3.6 km/h)
idle_W_m = 120.0                # W per metre of knife: friction of the knives and the gearbox at 600 rpm
e_cut = 400.0                   # J/m2: cutting a dense sward (~ 3 t DM/ha), estimated from finger-bar data
mu_shoe = 0.4                   # shoe on grass
drag_N_m = 60.0                 # cutting resistance against the driving direction per metre of bar (estimated)
drive_W = 300.0                 # driving on grassland (estimated)
grass_h = 220.0                 # standing grass in the animation and the renders


# ---------------------------------------------------------------------
# Derived geometry
# ---------------------------------------------------------------------
WIDTH = front_L + 2 * wing_L                    # 3250
OMEGA = crank_rpm * 2.0 * math.pi / 60.0
ECC = stroke / 2.0


def head_pivot(lift=0.0):
    """(y, z) of the bottom head pivot for a lift (mm above the work position)."""
    z0 = pivot_z[0] - math.sqrt(link_L ** 2 - (head_y - pivot_y) ** 2)
    z = z0 + lift
    return pivot_y + math.sqrt(link_L ** 2 - (z - pivot_z[0]) ** 2), z


def theta(lift=0.0):
    """Link angle (deg, + = head end up)."""
    y, z = head_pivot(lift)
    return math.degrees(math.atan2(z - pivot_z[0], y - pivot_y))


def head_shift(lift):
    y1, z1 = head_pivot(lift)
    y0, z0 = head_pivot(0.0)
    return y1 - y0, z1 - z0


def act_length(lift):
    """Pin A to pin B (bottom head pivot, x 0)."""
    yb, zb = head_pivot(lift)
    return math.hypot(yb - act_A[0], zb - act_A[1])


def lever_pin(fold=0.0):
    """(x, z) of the wing lever pin B (right wing) for a fold angle (deg, + = outer end up)."""
    a = math.radians(lever_deg + fold)
    return hinge[0] + lever_r * math.cos(a), hinge[1] + lever_r * math.sin(a)


ANCHOR_Z = lever_pin(0.0)[1]                    # slot of the anchor pins at the height of B in work


def wact_length(fold, pin_x=None):
    """Wing actuator pin to pin for a fold angle and an anchor pin position (default: outer end of the slot)."""
    bx, bz = lever_pin(fold)
    ax = anchor_x[1] if pin_x is None else pin_x
    return math.hypot(bx - ax, bz - ANCHOR_Z)


WACT_WORK = wact_length(0.0, anchor_x[1] - anchor_slack)     # actuator setting in work


def wing_float_range():
    """(down, up) fold angles (deg) the wing can reach with the actuator at the work setting (anchor in its slot)."""
    def pin_for(fold):
        bx, bz = lever_pin(fold)
        return bx - math.sqrt(max(0.0, WACT_WORK ** 2 - (bz - ANCHOR_Z) ** 2))
    lo, hi = -30.0, 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if pin_for(mid) > anchor_x[1]:
            lo = mid
        else:
            hi = mid
    down = hi
    lo, hi = 0.0, 40.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if pin_for(mid) < anchor_x[0]:
            hi = mid
        else:
            lo = mid
    return down, lo


def wing_pin_x(fold, act=None):
    """Anchor pin position (x, right wing) for a fold angle with the actuator at length act (None: work setting),
    clamped to the slot (outer end when the actuator pulls)."""
    act = WACT_WORK if act is None else act
    bx, bz = lever_pin(fold)
    x = bx - math.sqrt(max(0.0, act ** 2 - (bz - ANCHOR_Z) ** 2))
    return min(anchor_x[1], max(anchor_x[0], x))
