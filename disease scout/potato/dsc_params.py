import math

# =====================================================================
# Disease scout for potatoes - parameters
# A light-tight camera hood in front of the Bruut OpenAgbot (standard robot), 3.0 m wide, over 4 potato rows at 750 mm.
# The haulm passes through strip curtains into the hood; 10 downward cameras (one per 300 mm) and 20 LED strobe bars
# take a sharp, evenly lit picture of every plant, day and night. A vision computer looks for virus (PVY mosaic, leaf
# roll), blackleg and late blight and stores every suspect plant with its GNSS position (cf. Doorgrond Croptiscan).
#
#   Hood:    centre section 1.2 m, two wings of 0.9 m. The wings swing forward about a vertical kingpin on the roof
#            (24 V linear actuator each); folded the hood is 1.20 m wide.
#   Carried: on 2 castor wheels in the furrows (the same furrows as the robot's wheels), pushed by a parallelogram
#            (2 x 2 links) from two posts on the robot's front beams: the hood floats over the ridges at a constant
#            height and puts (almost) no weight on the robot.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = furrow bottom z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2: the wheels run in the furrows at x +-375
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_front = robot_axle_y + robot_tire_d / 2.0             # 715
robot_steer_max = 30.0
robot_steer_reach = 221.0       # tyre corner radius about the steering axis (215, 50)
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)         # x-direction beams, centres; holes at x +-125 .. +-475
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_beam = 40.0
robot_kg = 161.5                # agbot comparison (not weighed)
robot_cg = (0.0, 95.0, 543.0)   # estimated (agbot comparison)
robot_gnss = (0.0, 575.0, 659.0)
m10_hole = 10.4
battery_kwh = 2.4

# ---------------------------------------------------------------------
# Crop: potatoes on ridges at 750 mm (the robot's track): furrows at x +-375, +-1125, ridges at 0, +-750, +-1500
# ---------------------------------------------------------------------
row_pitch = 750.0
ridge_h = 250.0                 # ridge top above the furrow bottom
ridge_top_w = 220.0
furrow_w = 100.0                # flat furrow bottom (wheel track)
plant_pitch = 330.0             # in the row
canopy_z = (450.0, 750.0)       # top of the haulm: 3 weeks after emergence .. closed canopy (estimated)
rows_per_pass = 4               # 3 whole rows + 2 half rows at the hood ends = 4 rows per 3.0 m pass

# ---------------------------------------------------------------------
# Hood (aluminium sheet 1.5 mm on a frame of 40 x 40 x 2 aluminium tube). Inside matt white (diffuse light).
# ---------------------------------------------------------------------
hood_y = (780.0, 1320.0)        # rear and front outside face; the front tyres reach y 721 (30 deg steering)
hood_d = hood_y[1] - hood_y[0]  # 540
hood_yc = 0.5 * (hood_y[0] + hood_y[1])         # 1050
centre_half = 600.0             # centre section x -600 .. 600
wing_len = 900.0                # each wing x 600 .. 1500
half_width = centre_half + wing_len             # 1500: working width 3.0 m
roof_top = 1450.0
sheet = 1.5
wall_bottom = 800.0             # bottom of the rigid walls (above the tallest haulm)
frame = 40.0                    # roof frame tube 40 x 40 x 2
frame_wall = 2.0
frame_z = (roof_top - sheet - frame, roof_top - sheet)   # 1408.5 .. 1448.5
cross_x_centre = (0.0, 200.0, 375.0, 580.0)     # cross tubes (along y) in the centre section, +- (580: end tube)
cross_x_wing = (620.0, 900.0, 1125.0, 1478.5)   # cross tubes in the wing (620: inner end, 1125: castor, 1478.5: end)
rail = (40.0, 20.0)             # rails along x under the cross tubes (aluminium 40 x 20 x 2): cameras and LED bars
rail_y = (900.0, 1050.0, 1200.0)                # LED, camera, LED
rail_z = (frame_z[0] - rail[1], frame_z[0])     # 1388.5 .. 1408.5

# Strip curtains (black PVC 2 mm, strips 100 wide) inside the front and rear walls, clamped with a flat 30 x 4 that
# also stiffens the bottom edge. Outer ends of the wings: brush strip (the outermost ridge runs under it).
curtain_t = 2.0
curtain_strip = 100.0
curtain_z = (350.0, wall_bottom + 30.0)         # 350 .. 830 (100 above the ridge top)
clamp = (30.0, 4.0)
curtain_end_gap = 3.0           # centre curtains end 3 mm before x +-600 (the wing swings past)
brush_z = (650.0, wall_bottom)  # end brush bristles
brush_t = 8.0
upright_x = 200.0               # 2 uprights inside the rear wall (headstock of the parallelogram), alu 40 x 40

# ---------------------------------------------------------------------
# Cameras and light. 10 cameras on 300 mm pitch (x +-150 .. +-1350), straight down; per camera 2 LED bars along x,
# 150 mm in front of and behind it.
# ---------------------------------------------------------------------
n_cam = 10
cam_pitch = 300.0
cam_x = tuple(-0.5 * (n_cam - 1) * cam_pitch + i * cam_pitch for i in range(n_cam))
cam_body = (45.0, 45.0, 60.0)   # GigE PoE industrial camera, x y z
cam_lens = (32.0, 30.0)         # lens tube d, length
cam_lens_z0 = rail_z[0] - cam_body[2] - cam_lens[1]      # 1298.5: front of the lens
cam_px = (2448, 2048)           # 2/3" 5 MP global shutter (Sony IMX264 class), 3.45 um
cam_pixel = 0.00345
cam_f = 12.0                    # mm lens
cam_n = 5.6                     # aperture
cam_kg = 0.35                   # body + lens

led_len = 260.0
led_sec = (40.0, 30.0)          # bar y, z (aluminium profile with diffuser)
led_diffuser = 2.0
led_lm_w = 110.0                # lm/W of the LEDs in pulse overdrive (estimated)
led_pulse_w = 110.0             # W per bar during the flash (each bar: 24 x 5 W LEDs at ~1 A overdrive)
led_kg = 0.55
flash_us = 200.0                # flash = exposure time (global shutter)
utilisation = 0.65              # share of the LED light that reaches the canopy plane (white hood, estimated)
iso_gain = 400.0                # sensor sensitivity as ISO equivalent (gain ~ 12 dB)
ambient_lux = 100000.0          # full sun
leak = 0.03                     # share of daylight that gets in through curtains and gaps (estimated)
overlap_along = 0.30            # frame-to-frame overlap in the driving direction

# ---------------------------------------------------------------------
# Wing swing. Kingpin (vertical) at (+-60, front edge y 1320) on the roof: the wing rotates 90 deg forward about it
# and lies in front of the centre section, x 60 .. 600. Because the pivot is on the front line of the hood, 540 mm
# from the hinge line x 600, neither section ever enters the other (no gap at the corner).
# ---------------------------------------------------------------------
pivot_x = centre_half - hood_d  # 60
pivot = (pivot_x, hood_y[1])    # (60, 1320) right; left mirrored
fold = 90.0
pin_d = 40.0
pin_z = (roof_top + 10.0, roof_top + 240.0)     # 1460 .. 1690
pin_plate = ((-135.0, 135.0), (1240.0, 1345.0), (roof_top, roof_top + 10.0))
sleeve = (56.0, 40.5, roof_top + 14.0, roof_top + 200.0)    # od, bore, z0, z1
arm_sec = (40.0, 50.0)          # swing arm tube 40 (y) x 50 (z) x 2.5 steel, along the front edge
arm_wall = 2.5
arm_t = (-40.0, 0.0)            # arm in local wing coordinates: t = y - 1320
arm_z = (roof_top + 12.0, roof_top + 12.0 + arm_sec[1])     # 1462 .. 1522
arm_s1 = 1100.0                 # arm along the wing roof to x 1160 (the wing box carries the rest)
pad_s = (640.0, 1060.0) # 12 mm spacer pads between the arm and the wing roof (s from the pivot)
tie_d = 16.0
tie_s = 800.0                   # tie rod from the sleeve top to the arm at s 800
# Actuator (horizontal, vertical pins). Base pin on the roof, rod end on the swing arm.
act_base = (200.0, 970.0)       # right side (x, y)
act_end_rel = (150.0, -20.0)    # rod-end pin on the arm, relative to the pivot (s, t) at 0 deg
act_z = 1545.0                  # actuator axis
act_closed = 330.0              # pin-pin retracted
act_stroke = 200.0
act_speed = 25.0                # mm/s
act_force = 2500.0              # N (24 V, IP66, with end switches, e.g. Linak LA36 class)
act_body = (50.0, 22.0, 18.0, 250.0)       # od, bore, from, to (along the axis from the base pin)
act_rod = (20.0, 230.0)         # d, length
act_eye = (30.0, 12.5, 30.0)    # od, bore, height
act_pin_d = 12.0
act_kg = 2.8
act_w = 80.0                    # W at load (estimated)

# ---------------------------------------------------------------------
# Castors: 4 x pneumatic wheel 250 x 60 (load 150 kg each), swivel housing under the roof. 2 under the centre section
# in the robot's furrows (x +-375), 1 under each wing in the next furrow (x +-1125): with the wings folded forward the
# hood stands on all 4 and the robot carries nothing of it.
# ---------------------------------------------------------------------
castor_x = 375.0
castor_wing_x = 1125.0
castor_stem_y = 1125.0
castor_trail = 80.0
castor_wheel = (250.0, 60.0)
castor_stem_d = 40.0
castor_housing = (80.0, 80.0)   # d, height (under the cross tube at x 375)
castor_crown = (100.0, 120.0, 12.0, 300.0)      # x, y, t, z bottom
castor_leg = (6.0, 40.0)
castor_axle_d = 16.0
castor_kg = 4.5                 # wheel + fork + stem + housing (bought)
castor_load = 150.0             # kg rated per castor
c_rr_castor = 0.10              # rolling resistance in a loose furrow (estimated)

# ---------------------------------------------------------------------
# Parallelogram: 2 posts on the front lower beams, 2 x 2 links (30 x 30 x 3) to the headstock on the hood rear wall
# ---------------------------------------------------------------------
post_x = 200.0
post_y = 500.0
post = (60.0, 3.0)              # square tube 60 x 60 x 3 steel
post_plate = ((145.0, 255.0), (395.0, 605.0), 10.0)     # under the post, on both front lower beams
post_bolt_x = (175.0, 225.0)
post_top = 1290.0
link_z = (900.0, 1250.0)        # lower and upper pin height
link_y = (550.0, 755.0)         # pin on the post, pin on the hood
link_sec = 30.0
link_boss = 30.0
link_pin_d = 16.0
ear_t = 6.0
float_mm = 60.0                 # +- vertical float of the hood (end stops)

# ---------------------------------------------------------------------
# Roof: control box (vision computer, PoE switch, strobe drivers, DC-DC) and the GNSS antenna (moved from the robot)
# ---------------------------------------------------------------------
box_xy = ((-140.0, 140.0), (830.0, 990.0))
box_h = 130.0
ant_stem = (30.0, 25.0)
ant_dome = (150.0, 55.0)

# ---------------------------------------------------------------------
# Operation (dsc_calc, animation)
# ---------------------------------------------------------------------
speed = 1.0                     # m/s scouting speed
field_eff = 0.80
drive_w = 420.0                 # W driving in the furrows at 1 m/s with the hood (estimated)
computer_w = 60.0               # Jetson AGX Orin class
cam_w = 3.5                     # W per camera (PoE)
switch_w = 12.0
jpeg_mb = 1.2                   # MB per stored image (JPEG q90, 5 MP)
store_share = 0.10              # share of the images kept (all suspects + 1 in 10 for the record)
curtain_drag = 30.0             # N per m of curtain width through the haulm (estimated)
wind = 10.0                     # m/s gust on a wing while swinging
pin_mu = 0.15                   # bushing friction in the kingpin sleeve
dyn = 2.5                       # dynamic factor for bumps
g = 9.81
