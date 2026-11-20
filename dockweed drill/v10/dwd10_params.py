import math

# =====================================================================
# Dockweed drill v10 - parameters
# Gantry behind the Bruut OpenAgbot: X axis (left-right, stroke 1000) + Z axis (up-down), the robot is the Y axis.
# v10 = v8 with two changes:
# - X axis as v8 (2 round precision tubes D50 x 4 between 2 side plates 12 mm, 2 cross beams 40 x 40 x 3, 3 plain-bush
#   housings on the slide), but the drive as v9: NEMA 23 closed-loop + 5:1 FIXED on a bracket at the right side plate,
#   a tension pulley at the left, the belt (HTD5M 15 mm) runs round both pulleys and its lower run is clamped on the
#   slide. The slide carries no motor any more.
# - Z axis on linear guides (after the photos in inspiration/): 2 profile rails HGR20 fixed on 2 rail beams (RHS
#   50 x 40 x 4) bolted to the back of the X slide; 4 carriages HGH20CA on the Z sled, a 6 mm plate bent into a U whose
#   flanges cover the rails at the sides. The sled is also the back plate of the spindle bracket. The Linak LA36 pushes
#   the sled pin to pin in the middle between the rails, as in v8. Spindle, motor, coupling, can and cutter as v8.
#
# Axes as the robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot. The implement hangs behind the rear lower beam (rear_outer).
# Helper v = distance behind the rear face of that beam: robot y = robot_beam_rear_face - v.
# The parts are drawn in (x, v, z) and then mirrored to robot coordinates (dwd10_parts.to_robot).
# All dimensions are here; never hardcode them in dwd10_parts.py / build_dwd10.py.
# =====================================================================

VARIANT = "v10"

# ---------------------------------------------------------------------
# Robot interface (from "agbots/agbot design/agbot_params.py")
# ---------------------------------------------------------------------
robot_beam = 40                     # box beam 40 x 40 x 2
robot_beam_wall = 2
robot_beam_length = 1000            # lower beams (x direction), x = -500..500
robot_rear_beam_y = -575            # centre of the rear_outer lower beam
robot_beam_rear_face = robot_rear_beam_y - robot_beam / 2.0      # -595: v = 0
robot_lower_beam_z = (619.0, 659.0)  # ground_to_axle 215 + z_lower_beam_bot 404
robot_upper_beam_z = (659.0, 699.0)
robot_upper_beam_x = (325.0, 425.0)  # upper beams (y direction), centre
robot_upper_beam_end_y = -650.0
robot_grid = 50                     # M10 hole grid in the beams
robot_hole_d = 10.4
robot_hole_x = tuple(125.0 + 50.0 * i for i in range(8))         # holes in the lower beam at x = +-125 .. +-475
robot_wheel_x = 375.0
robot_wheel_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_bracket_half_x = 114.0        # wheel bracket outside 228
robot_bracket_half_y = 120.0
robot_bracket_top_z = 564.0
robot_block_half_x = 70.0           # wooden block at the rear (140 x 190)
robot_block_half_y = 95.0
robot_frame_bolt_x = (325.0, 425.0)  # frame_bolts of the wheel unit (taken)

# robot (estimated, not measured): mass and centre of gravity without implement
robot_kg = 150.0
robot_cg_y = 0.0                    # half way between the axles
robot_cg_z = 450.0
battery_forward_cg_y = 150.0        # robot CG when the battery (about 45 kg) goes 500 mm forward (estimated)


def v_to_y(v):
    """Helper v (behind the beam) to robot y."""
    return robot_beam_rear_face - v


# ---------------------------------------------------------------------
# Pose of the machine (build): X of the spindle centre (see X axis) and height of the underside of the tool
# ---------------------------------------------------------------------
depth_std = 150.0                   # standard cutting depth (Ruud: 15 cm)
depth_max = 200.0
drive_z = 200.0                     # underside of the cutter above the sward while driving (actuator retracted)
z_ref = drive_z                     # reference pose of the Z sled in the build (driving)
work_z = -depth_std

# ---------------------------------------------------------------------
# Headstock: 2 uprights 40 x 40 x 3 behind the lower beam, on the hole grid (as v6 / v8)
# Free holes in rear_outer: x = +-225 and +-275 (+-325/+-425 = frame_bolts, +-375 above the wooden block).
# ---------------------------------------------------------------------
hs_x = 250.0                        # upright centre
hs_bolt_dx = 25.0                   # M10 at x = hs_x +- 25 (holes 225 and 275)
hs_bolt_v = -robot_beam / 2.0       # centre of the lower beam
hs_plate_half_x = 50.0
hs_plate_t = 8.0                    # top plate, clamp plate, back plate
up_size = 40.0                      # upright 40 x 40 x 3
up_wall = 3.0
up_v0 = hs_plate_t                  # front of the upright (against the back plate)
up_v1 = up_v0 + up_size
up_z0 = robot_lower_beam_z[0] - hs_plate_t        # 611: underside of the clamp plate
up_z1 = 1110.0
up_cap_t = 6.0
gusset_t = 6.0
gusset_h = 75.0                     # gusset above the top plate, against the upright (below the M12 of the cross beam)
cross_size = 40.0                   # cross tube between the uprights (carries the electrics box)
cross_wall = 3.0
cross_z = (up_z0 + 4.0, up_z0 + 4.0 + cross_size)
m10_d = 10.0
m10_head_r = 9.2                    # AF17 across corners / 2 (drawn round)
m10_head_k = 6.4
m10_nut_m = 8.4
m12_d = 12.0
m12_head_r = 11.0                   # AF19 (drawn round)
m12_head_k = 7.5

# ---------------------------------------------------------------------
# X stroke
# ---------------------------------------------------------------------
x_stroke = 1000.0                   # as v6 / v8
x_min, x_max = -x_stroke / 2.0, x_stroke / 2.0
work_x = 150.0                      # pose for the standard images

# ---------------------------------------------------------------------
# X axis (as v8): 2 round precision tubes D50 x 4 between 2 side plates 12 mm. A plug (D42, 25 long) welded in each
# tube end, tapped 2x M10; bolts from outside through the side plate: a tube comes out with 4 bolts. The side plates are
# welded to 2 cross beams 40 x 40 x 3 over the full width (one per tube height, in front of the tubes), bolted with
# 1x M12 per crossing to the back of the uprights. The slide runs on 3 housings with an iglidur bush: 2 on the upper
# tube, 1 in the middle of the lower tube (slotted holes in z: 3 points, no double guidance).
# ---------------------------------------------------------------------
beam_z = (760.0, 1060.0)            # centre of the lower / upper tube and cross beam
xbar_z = beam_z
xbeam = (40.0, 3.0)                 # cross beam 40 x 40 x 3, directly behind the uprights
xbeam_v = (up_v1, up_v1 + xbeam[0])
xg_d = 50.0                         # X tube: precision tube D50 x 4 E355
xg_t = 4.0
xg_house = (100.0, 70.0, 32.0)      # X housing: width (z), length (x), in front of the tube centre
xg_hc = 42.0                        # tube centre to mounting face (estimated)
xg_house_bolt = (22.0, 40.0)        # 4x M8 at centre +- 22 (x) and +- 40 (z)
xg_house_gap = 8.0                  # free space between cross beam and the front of the X housing
tube_v = xbeam_v[1] + xg_house_gap + xg_house[2]     # centre of the X tubes (128)
xg_upper_pitch = 240.0              # 2 housings on the upper tube at x = +-120
xg_bush_d = 60.0                    # plain bush outside (estimated)
xg_wiper_t = 8.0                    # wiper left and right of each housing
xbar_L = 1470.0                     # outside of the side plates (as v8: belt pulleys outside the slide travel)
end_plate_t = 12.0                  # side plate steel
plug_L = 25.0                       # plug in the tube end (welded), tapped 2x M10
tube_bolt_dz = 10.0                 # M10 at z = tube centre +- 10
side_plate_v = (xbeam_v[0], 190.0)  # to behind the slide (v8: 163): limit switch and end stop at slide height
side_plate_z = (xbar_z[0] - 40.0, xbar_z[1] + 40.0)

# X slide (alu 12 mm): X housings on the front, rail beams of the Z axis, LA36 top bracket and spiral cable on the back.
# No X motor any more (v8: x 152), so 380 wide instead of 410.
slide_v0 = tube_v + xg_hc           # front of the slide = mounting face of the X housings (170)
slide_t = 12.0
slide_v1 = slide_v0 + slide_t       # 182: back of the slide
slide_half_x = 190.0                # X housings to x 155, spiral cable bracket to 186
slide_z = (700.0, 1120.0)
slide_tab = (-30.0, 30.0, 1450.0)   # extension in the middle at the top of the slide (x0, x1, z1): top pin of the LA36

# X drive (as v9): HTD5M 15 mm round 2 pulleys 20T near the side plates (axis along v). NEMA 23 closed-loop + 5:1
# FIXED on a bracket plate welded to the right side plate (gearbox and motor towards the robot, between the cross
# beams), tension pulley on an M10 in a slot at the left; the lower run is clamped on the front of the slide.
belt_z = 910.0                      # pulley centre: half way between the tubes, between the lower and upper X housings
belt_w = 15.0
belt_v = (125.0, 140.0)             # belt plane, between the cross beams (v 88) and the slide (v 170)
pulley_x = 690.0                    # outside the X housings at x_max (655), inside the side plate (723)
pulley_r = 15.0                     # 20T HTD5M: pitch diameter 31.8
pulley_flange_r = 20.0
pitch_d = 31.83
belt_r = (15.2, 18.6)               # belt inside / outside (drawn)
drive_bracket_v = (110.0, 120.0)    # bracket plate pulley / motor (welded to the side plate)
drive_bracket_dx = 80.0             # from the side plate inwards
drive_bracket_dz = 45.0
belt_len = 2 * 2 * pulley_x + math.pi * pitch_d    # open length with clamp, about 2860
belt_clamp_half_x = 30.0
limit_vz = (176.0, 1000.0)          # limit switch X-min (left) and rubber end stop (right) at the height of the slide
chain_z = xbar_z[1] + 60.0          # cable chain above the upper X housings

# ---------------------------------------------------------------------
# Z axis (v10): 2 profile rails HGR20 on 2 rail beams, 4 carriages HGH20CA on the Z sled (after the photos).
# The rail beams (RHS 50 x 40 x 4, S355, 50 deep in v) stand at x = +-90 against the back of the X slide (4x M8 each
# through the slide) and hang down to z 210. The rails are bolted on their back face (M5, pitch 60). Between the rail
# beams there is room for the LA36 (x +-38) as in v8; the rod-eye bracket is welded on the front of the sled.
# HIWIN HG20 catalogue values: CHECK them on the rails and carriages you buy.
# ---------------------------------------------------------------------
zr_dx = 90.0                        # rail centre at x = +-90 (as the v8 tubes)
zb_size = (50.0, 40.0, 4.0)         # rail beam RHS: depth (v), width (x), wall
zb_v = (slide_v1, slide_v1 + zb_size[0])        # 182..232
zb_z = (210.0, slide_z[1])          # 210..1120, closed at the bottom with a 5 mm cap
zb_cap_t = 5.0
zb_bolt_z = (725.0, 815.0, 905.0, 995.0)        # 4x M8 per beam through the slide, between the X housings
rail_w = 20.0                       # HGR20: width 20, height 17.5, 2.21 kg/m, M5 every 60 mm
rail_h = 17.5
rail_kg_m = 2.21
rail_pitch = 60.0
rail_z = (225.0, 1110.0)            # 885 long (22.5 + 14 x 60 + 22.5)
rail_v0 = zb_v[1]                   # rail foot = back face of the rail beam (232)
rail_stop = (20.0, 12.0, 12.0)      # rubber end stop under each rail (x, v, z)
blk_H = 30.0                        # HGH20CA: rail foot to top of the carriage
blk_H1 = 4.6                        # rail foot to underside of the carriage
blk_W = 44.0
blk_L = 77.5                        # with end seals
blk_L1 = 50.5                       # steel body
blk_bolt = (32.0, 36.0)             # 4x M5 (across x, along z)
blk_kg = 0.30
blk_C = 17750.0                     # dynamic load rating [N] (catalogue)
blk_C0 = 27760.0                    # static load rating [N]
blk_M = (270.0, 200.0, 200.0)       # static moments MR, MP, MY [Nm] of one carriage (catalogue)
blk_seal_n = 3.0                    # friction of the seals per carriage [N] (estimated, double seal + scraper)
blk_mu = 0.005                      # rolling friction balls
blk_z = (470.0, 860.0)              # carriage centres above the tool underside (on the sled), 390 apart

# Z sled = back plate of the spindle bracket: steel 6 mm bent into a U, flanges 26 forward (towards the slide)
sled_v0 = rail_v0 + blk_H           # 262: front of the sled = top of the carriages
sled_t = 6.0
sled_half_x = 126.0                 # outside the carriages (x 112)
sled_flange = 26.0
sled_z = (408.0, 900.0)             # above the tool underside (lower plate of the spindle bracket .. above the carriages)
sled_win = ((28.0, 60.0), (630.0, 830.0))      # 2 lightening windows (|x|, z above the tool underside)

# Actuator: Linak LA36 (parts/actuator/linear-actuator-la36-data-sheet-eng.pdf), 24 V, 1700 N, spindle 20 mm,
# gear F 1:18, stroke 400, rear mount and rod eye solid D12.2. Pin to pin in the middle between the rail beams (x 0),
# housing at the top, towards the back (+v) above the spindle motor. Retracted = driving position. (As v8.)
act_stroke = depth_max + drive_z    # 400
act_Lr = 250.0 + act_stroke         # retracted pin to pin (datasheet: stroke > 300 -> 250 + stroke) = 650
act_x = 0.0
act_v = slide_v1 + 46.0             # 228: actuator axis; outer tube 203..253 between the slide (182) and the sled (262)
act_pin_z = 1420.0                  # top pin (fixed): housing 20 mm above the spindle motor in the driving position
act_tube = (44.5, 50.0)             # outer profile alu (x, v); 44.5 from the datasheet, 50 estimated
act_rod_d = 28.0                    # inner tube (estimated; rod eye D27.8)
act_tube_end = 45.0                 # end of the outer tube above the centre of the rod eye, retracted (estimated)
act_house_w = 76.0                  # housing: width 76, height 148 of which 36 in front of the axis, length 230
act_house_h = (36.0, 112.0)         # housing in front of (-v) / behind (+v) the axis of the spindle
act_house_L = 230.0
act_house_dz = 25.0                 # centre of the rear pin to the end of the housing
act_eye_dz = act_pin_z - act_Lr - drive_z    # 570: centre of the rod eye above the tool underside
act_pin_d = 12.2
act_eye_c = 27.8
act_back_c = 25.2
act_force = 1700.0                  # max. load [N]; self-locking 2200 N
act_selflock = 2200.0
act_speed = (72.0, 52.0)            # speed unloaded / at 1700 N [mm/s] (datasheet)
act_amp = (2.4, 10.3)               # current unloaded / at 1700 N [A] (datasheet)
act_duty = 0.20                     # duty cycle at full load, stroke <= 600 (datasheet: 4 min on, 16 off)
act_V = 24.0
act_kg = (5.3, 0.7)                 # 6.0 kg total; fixed / rod
dcdc = (48.0, 24.0, 20.0)           # converter 48 -> 24 V, 20 A

# ---------------------------------------------------------------------
# Spindle bracket, spindle, motor (as v8; its back plate is now the sled)
# ---------------------------------------------------------------------
sb_back_v0 = sled_v0
sb_back_t = sled_t
spindle_dv = 75.0                   # spindle centre behind the sled
sb_lo = sled_z[0]                   # lower plate above the tool underside
sb_side_x = 87.5                    # centre of the side plates (5 mm), just outside the bearing feet

# 2x UCP 206 pillow block (shaft 30). Catalogue dimensions: CHECK them on the pillow block you buy.
ucp_d = 30.0
ucp_bolt = 121.0
ucp_L = 165.0
ucp_b = 48.0
ucp_slot = (17.0, 20.0)
ucp_H = 82.0
ucp_h = 42.9
ucp_foot_t = 17.0                   # estimated
ucp_ring_d = 80.0                   # estimated
ucp_ring_w = 38.1
ucp_kg = 1.4
ucp_C = 19500.0                     # dynamic load rating [N] (UC206, catalogue)
bearing_plate_t = 10.0
bearing_lo = sb_lo + 8.0 + ucp_b / 2 + 7.0
bearing_dist = 140.0
bearing_hi = bearing_lo + bearing_dist
sb_mo = bearing_hi + ucp_b / 2 + 4.0
shaft_d = ucp_d                     # spindle shaft D30 C45 solid, welded into the spindle flange at the bottom

# Flexible jaw coupling size 28: hub D19 (motor, key 6) and D30 (spindle, key 8).
jaw_d = 65.0
jaw_L = 90.0
jaw_star = 20.0
jaw_T = (95.0, 190.0)               # nominal / max. torque [Nm] (catalogue, check)
jaw_hub_L = 35.0
jaw_z0 = sb_mo + 8.0 + 7.0
jaw_kg = 0.95
shaft_top = jaw_z0 + jaw_hub_L

# Spindle motor: 800 W gearmotor with foot (in stock, parts/800 watt motor; 48 V brushed, 500 rpm according to the
# advert: CHECK the type plate). Stands straight above the spindle, shaft down into the jaw coupling.
motor_P = 800.0
motor_rpm = 500.0
motor_V = 48.0
motor_peak = 2.0
motor_shaft_d = 19.0
motor_shaft_out = 35.0
motor_total_len = 260.0
motor_nose = (35.0, 65.0, 45.0, 80.0)
motor_ring = (65.0, 110.0, 120.0)
motor_body = (110.0, 255.0, 105.0)
motor_cap = (255.0, 260.0, 95.0)
motor_foot = (119.0, 234.0)
motor_foot_holes = (139.0, 219.0)
motor_foot_w = 90.0                      # ASSUMED
motor_foot_hole_dx = 70.0                # ASSUMED
motor_foot_t = 6.0
motor_foot_h = 64.0
motor_kg = 9.0                           # estimated
motor_shaft_end = jaw_z0 + jaw_L - jaw_hub_L
motor_plate_t = 10.0
motor_plate_v = (-62.0, 72.0)
gusset_mp_t = 6.0

cutter_rpm = motor_rpm
idle_w = 45.0                       # loss of spindle + bearings + coupling at 500 rpm (estimated)

# ---------------------------------------------------------------------
# Can (as v5..v8 / Robot Ruud): steel pipe DN200 with lid, rests on the sward with its own weight
# ---------------------------------------------------------------------
pot_d = 219.1
pot_h = 180.0
pot_t = 3.6
pot_lid_t = 5.0
pot_rim = 30.0
pot_rod_dx = 100.0
pot_rod_d = 16.0

# ---------------------------------------------------------------------
# Tool (only the cutter: 500 rpm is too slow for the mowing disc)
# ---------------------------------------------------------------------
cutter_d = 180.0
cutter_teeth = 4

# ---------------------------------------------------------------------
# Drive and process
# ---------------------------------------------------------------------
stepper_T = 3.0                     # NEMA 23 closed-loop [Nm] (as v6 / v8)
x_gear = 5.0
x_pulley_T = 20
htd_pitch = 5.0
rapid_x = 200.0                     # mm/s
xg_mu = 0.15                        # friction iglidur on the tube (dry to lightly greased)
plunge_v = 25.0                     # plunge speed [mm/s]
rapid_z = act_speed[0] - (act_speed[0] - act_speed[1]) * 800.0 / act_force   # LA36 at about 800 N (lifting)
dwell_s = 1.0
z_force_limit = 600.0               # software limit [N]
cut_energy = (0.5e6, 2.0e6)
cut_energy_std = 1.0e6
thrust_n = (150.0, 1.0)
side_force = 300.0                  # side force on the cutter, design value (peak)
side_force_normal = 100.0           # side force in normal work (estimated)
drive_speed = 500.0                 # mm/s
stop_start_s = 4.0
plant_period_s = 60.0               # typical time between two plants in the field (user: sometimes a minute)
position_tol = 40.0                 # allowed error spindle-plant [mm] (can D219 round a cutter D180)

# ---------------------------------------------------------------------
# Camera, light, electrics
# ---------------------------------------------------------------------
cam_x = 0.0                         # fixed camera high above the spindle line
cam_mast_x = 250.0                  # mast 40 x 40 on the right upright
cam_z = 1900.0
cam_v = 740.0                       # camera behind the spindle line (driving direction -y: it sees the plant first)
ebox = (300.0, 250.0, 120.0)
ebox_z0 = 745.0
ebox_plate_t = 3.0
spiral_turns = 12
spiral_x = 160.0                    # spiral cable right of the right rail beam and the sled flange (x 126)
spiral_v = 240.0                    # between the slide (182) and the sled (262)
spiral_z0 = 1105.0                  # fixed anchor on the back of the X slide, at the top
spiral_dz = 436.0                   # moving anchor on the right sled flange, above the tool underside
