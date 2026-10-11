import math

# =====================================================================
# Around-pole fence mower (simple) - parameters
# Mows the strip under an electric fence, behind the standard Bruut OpenAgbot (right-hand side). The robot drives
# forward (+y) next to the fence; a trailing swing arm carries a low string-trimmer head under the bottom wire.
# When the head meets a post, the post pushes the arm back and in, the head slides around the post on its PE guard
# ring, and a spring swings it back out behind the post. Passive: no sensor, no actuator.
#
#   Mount:  hanger plate under the two rear lower beams (4 x M10 in the hole grid), 2 webs, a fixed pivot post
#           (tube 60.3 x 5) behind the right rear tyre, stop plate with 2 stop bolts and the spring anchor.
#   Swing:  sleeve 76.1 x 5 on the post (2 PE bushes), clevis, lever for the spring. Rotates about the post.
#   Arm:    laser-cut base plate 6 mm with 2 ribs 6 x 50 (a U, belt runs inside, sheet cover on top), hinged on the
#           clevis (floats up/down), carried at the head by an HDPE skid. 48 V BLDC motor at the root, V-belt to a
#           bought lawn-tractor deck spindle at the tip. Under the spindle: steel disc with 4 nylon strings, above
#           it a guard: steel cover and a slice of PE pressure pipe 315 that slides along the post.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot. Arm frame: u = along the arm from the pivot axis, v = u turned 90 deg to the left
# (seen from above), z = up. Swing angle psi: angle of the arm behind the +x axis (0 = straight out to the right,
# 90 = straight back). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = 500.0            # wheel centres at y = +-500
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_rear_beam_y = (-575.0, -425.0)    # centres of the rear lower beams (x direction, 1000 long)
robot_lower_beam_z = (619.0, 659.0)     # bottom / top of the lower beams (world)
robot_bracket_x = 261.0         # inner face of the rear wheel bracket top plate (x 261..489)
robot_half_width = 500.0        # ends of the lower beams
robot_grid = 50.0               # hole grid of the beams, M10 (hole 10.4) at x = +-125, +-175, +-225, ...
m10_hole = 10.4
battery_v = 48.0                # robot battery 48 V 50 Ah LiFePO4 (agbot comparison)

# ---------------------------------------------------------------------
# Hanger: plate under both rear lower beams, 2 x M10 per beam, 2 webs down to the pivot post
# ---------------------------------------------------------------------
hanger_x = (100.0, 250.0)       # 11 mm clear of the wheel bracket (x 261)
hanger_y = (-610.0, -390.0)
hanger_t = 10.0
hanger_bolt_x = (125.0, 225.0)  # grid holes, outside the webs (webs at x 139..145 and 205..211)
web_t = 6.0
web_front_y = -400.0            # webs from under the plate (y -400) back to the post
web_low_z = 580.0               # bottom edge of the webs at the front ...
web_post_z = 345.0              # ... and at the post (above the stop plate)

# ---------------------------------------------------------------------
# Pivot: fixed post behind the right rear tyre, sleeve turns on it
# ---------------------------------------------------------------------
pivot = (175.0, -830.0)         # (x, y) of the post axis; tyre ends at y -715, wheel bracket at x 261
post_d = 60.3                   # tube 60.3 x 5 (S355)
post_wall = 5.0
post_z = (95.0, 609.0)          # bottom end plate below, top under the hanger plate level
end_plate_d = 100.0             # bolted end plate (M12 into a welded plug), carries the sleeve
end_plate_t = 10.0
thrust_t = 3.0                  # PE thrust washer on the end plate
sleeve_d = 76.1                 # tube 76.1 x 5, two PE bushes (bore 60.5) inside
sleeve_wall = 5.0
sleeve_z = (post_z[0] + thrust_t, 300.0)    # 98 .. 300 (end plate 85 .. 95 under the post, washer 95 .. 98)
bush_len = 40.0
collar_d = 80.0                 # collar welded on the post above the sleeve: sleeve cannot climb
collar_z = (302.0, 312.0)

# lever on top of the sleeve (spring), plate 10 mm
lever_offset = 120.0            # deg, lever direction = arm direction + 120 (CCW): at rest it points forward (+y)
lever_r = 145.0                 # outer end
lever_hole_r = 130.0            # spring hook
lever_w = 40.0
lever_z = (290.0, 300.0)

# stop plate (10 mm, welded on the post) with 2 stop bolts M12 and the eye bolt for the spring
stop_plate_z = (330.0, 340.0)
stop_r = 60.0                   # stop bolts at this radius, they touch the side of the lever
stop_bolt_d = 12.0
stop_bolt_z = (286.0, 352.0)    # bolt through the plate, head + lock nut on top
anchor_angle = 160.0            # deg (absolute, from +x), spring anchor = eye bolt M10
anchor_r = 280.0
anchor_bolt_d = 10.0

# swing range
psi_rest = 30.0                 # deg: arm trails 30 deg behind the +x axis at rest (on the rest stop)
psi_max = 85.0                  # deg: max stop, arm almost straight back

# ---------------------------------------------------------------------
# Arm (arm frame u, v, z)
# ---------------------------------------------------------------------
arm_L = 640.0                   # pivot axis -> spindle axis
arm_w = 160.0                   # base plate width (v = +-80)
base_t = 6.0
base_u = (100.0, 720.0)         # base plate from behind the hinge to the end rib
rib_t = 6.0                     # flat bar 6 x 50 on both edges, on top of the base plate
rib_h = 50.0
rib_u0 = 55.0                   # ribs run past the base plate to the hinge (rounded end r 25 around the hinge)
cover_t = 2.0                   # removable sheet cover (belt guard)
base_z0 = 124.0                 # bottom of the base plate (cut height 60): disc 60..64, boss 64..79, housing 79..124

# hinge (float): clevis on the sleeve, M16 bolt along v
hinge_u = 80.0
hinge_z = base_z0 + base_t + rib_h / 2.0     # 155 (middle of the ribs)
hinge_bolt_d = 16.0
clevis_u = (38.0, 48.0)         # back plate 10 mm, perpendicular to the arm, welded to the sleeve
clevis_w = 200.0                # v = +-100
lug_t = 10.0                    # 2 lugs outside the ribs, v = +-(81..91)
lug_u1 = 146.0
clevis_z = (110.0, 202.0)
float_stop_u = (136.0, 146.0)   # 2 bars 10 x 8 welded between the lugs: under the base plate and above the motor plate
float_stop_gap = 6.0            # gap to the base plate (below) and the motor plate (above) at rest
float_deg = 5.0                 # head floats +-5 deg about the hinge (+-49 mm at the head), then a stop bar touches

# skid: HDPE puck under the head, on the rear-inner side (-v), carries the head and sets the cut height
skid_u = arm_L
skid_v = -230.0                 # outside the strings (r 200) and on the side away from the posts
skid_d = 160.0
skid_h = 25.0
skid_leg_w = 50.0               # leg: flat bar 8 x 50, slotted for the cut height
skid_tab_w = 60.0               # tab of the base plate out to the leg (laser cut in one piece with the base)

# ---------------------------------------------------------------------
# Drive: 48 V BLDC motor at the root, V-belt (A / 13 mm) to the deck spindle
# ---------------------------------------------------------------------
motor_u = 200.0                 # motor axis on the arm
motor_P = 750.0                 # W rated
motor_rpm = 3000.0
eta_motor = 0.85                # motor + controller
motor_flange = 90.0             # square flange 90 x 90 x 10 (estimated)
motor_flange_t = 10.0
motor_d = 90.0
motor_len = 140.0
motor_plate_t = 8.0             # welded across the ribs, 4 slots along u = belt tension
motor_plate_len = 140.0
motor_shaft_d = 19.0
pulley_motor_d = 110.0          # pitch diameter
pulley_spindle_d = 90.0         # pitch diameter
pulley_w = 26.0
pulley_z0 = base_z0 + base_t + 16.0          # 146: above the spindle bolt heads, jam nut on top up to the cover
belt_w = 13.0                   # classic V-belt A
belt_t = 8.0
eta_belt = 0.95

# deck spindle (bought, lawn-tractor type, 2 ball bearings, 3-bolt flange; dimensions estimated)
spindle_flange_d = 130.0
spindle_flange_t = 8.0
spindle_housing_d = 62.0
spindle_shaft_d = 19.0
boss_d = 60.0                   # blade boss under the housing
boss_h = 15.0
spindle_bolt_pcd = 110.0

# ---------------------------------------------------------------------
# Head: disc with strings, guard
# ---------------------------------------------------------------------
cut_h = 60.0                    # bottom of the disc above the ground (set with the skid leg: 40 .. 100)
disc_d = 280.0                  # steel disc 4 mm (laser cut)
disc_t = 4.0
string_d = 3.3                  # nylon trimmer line, square or round 3.3 mm
n_strings = 4
string_r = (112.0, 200.0)       # from the clamp to the tip: cut diameter 400
clamp = (36.0, 18.0, 8.0)       # clamp bar (radial length, width, height) with 2 x M6, line folded under it
clamp_r = 112.0                 # middle of the clamp
guard_d = 315.0                 # PE100 pressure pipe 315 SDR 17 (wall 18.7), a 47 mm slice
guard_wall = 18.7
guard_z = (74.0, base_z0 - 3.0)              # above the strings (top 67.3)
guard_cover_t = 3.0             # steel cover disc 3 mm under the base plate

# ---------------------------------------------------------------------
# Return spring: extension spring between the lever and the eye bolt on the stop plate (estimated, from a catalogue:
# wire 4.5, OD 32, k 1.8 N/mm, initial tension 140 N, 200 hook to hook, max extension 190 mm)
# ---------------------------------------------------------------------
spring_od = 32.0
spring_wire = 4.5
spring_k = 1.8                  # N/mm
spring_F0 = 140.0               # N initial tension
spring_free = 200.0             # mm between the hook points, unloaded
spring_z = 295.0                # middle of the lever plate
spring_hook = 22.0              # hook length at each end (straight piece in the model)

# ---------------------------------------------------------------------
# Controller box 130 x 180 x 80 (BLDC driver 48 V / 25 A, fuse, relay) on the rear lower beams
# ---------------------------------------------------------------------
box_x = (-240.0, -110.0)
box_y = (-590.0, -410.0)
box_h = 80.0
box_base_t = 3.0
box_base_x = (-250.0, -100.0)   # M8 through the grid holes at x = -225 and -125 (left of the middle, hanger on the right)
box_base_y = (-600.0, -400.0)

# ---------------------------------------------------------------------
# Fence (for the animation and the checks)
# ---------------------------------------------------------------------
post_offset = 100.0             # post line 100 mm outside the head centre: head straight under the wire, the post
                                # hits the guard on its outer side (29 deg off head-on) and pushes it in, not only back
fence_post_d = 100.0            # wooden post (round, 80..120); T-posts and step-in posts: see README
fence_post_h = 1100.0
wire_z = (300.0, 550.0, 850.0)  # 3 wires (cattle / horses; sheep and wolf fences lower, see README)
wire_inset = 110.0              # insulator: wire 110 mm inside the post centre (towards the robot)
wire_d = 3.0

# ---------------------------------------------------------------------
# Operation (for apm_calc and the animation)
# ---------------------------------------------------------------------
drive_speed = 0.5               # m/s (1.8 km/h), like the Zaunkonig at post contact (~2 km/h)
mu_guard = 0.25                 # PE on (wet) wood
grass_drag = 40.0               # N on the head in tall, dense grass (backwards), estimated
damping = 6.0                   # Nm s/rad, grass + PE bushes on the swinging arm, estimated
cut_energy = 1400.0             # J/m2, rotary impact cutting of grass (4 kW per m at 10 km/h, mulcher/rotary mowers)
cd_string = 1.2                 # drag coefficient of a round string across the flow
rho_air = 1.2
idle_W = 40.0                   # bearings, belt, disc windage


# ---------------------------------------------------------------------
# Derived geometry
# ---------------------------------------------------------------------
def arm_dir(psi):
    """Unit vectors (u, v) of the arm frame in world xy for swing angle psi (deg)."""
    a = math.radians(-psi)
    return (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))


def arm_point(u, v, psi=None):
    """World (x, y) of an arm-frame point (u, v) at swing angle psi (default: rest)."""
    psi = psi_rest if psi is None else psi
    du, dv = arm_dir(psi)
    return (pivot[0] + u * du[0] + v * dv[0], pivot[1] + u * du[1] + v * dv[1])


def head_centre(psi=None):
    return arm_point(arm_L, 0.0, psi)


def lever_tip(psi=None):
    """World (x, y) of the spring hole in the lever."""
    psi = psi_rest if psi is None else psi
    a = math.radians(-psi + lever_offset)
    return (pivot[0] + lever_hole_r * math.cos(a), pivot[1] + lever_hole_r * math.sin(a))


def anchor_point():
    a = math.radians(anchor_angle)
    return (pivot[0] + anchor_r * math.cos(a), pivot[1] + anchor_r * math.sin(a))


def lever_angle(psi):
    """Absolute direction (deg) of the lever for swing angle psi."""
    return -psi + lever_offset


def stop_angles():
    """Absolute angles (deg) of the rest and max stop bolt: on either side of the lever at its end positions."""
    half = math.degrees(math.asin((lever_w / 2.0) / stop_r)) + math.degrees((stop_bolt_d / 2.0 + 0.5) / stop_r)
    return lever_angle(psi_rest) + half, lever_angle(psi_max) - half


HEAD_REST = head_centre()                         # (754, -1150)
POST_X = HEAD_REST[0] + post_offset               # post line of the fence
WIRE_X = POST_X - wire_inset
STRING_TIP_Z = cut_h + disc_t + string_d          # 67.3
HEAD_TOP_Z = base_z0 + base_t + rib_h + cover_t   # 182
