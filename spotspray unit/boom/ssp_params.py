import math

# =====================================================================
# Spot sprayer with a folding boom - parameters
# A camera on a mast in front of the robot looks at the strip ahead. A computer detects the weeds (dock, thistle,
# nettle, ...) and the boom behind the robot sprays only those spots: every nozzle has its own solenoid valve.
#
#   Boom:   3.75 m working width, 15 nozzles at 250 mm. Centre section 1.25 m, fixed under the rear of the robot;
#           two wings of 1.25 m fold up (vertical) with an electric linear actuator each, also in the field
#           (posts, trees, gates, a ditch side) and down again.
#   Tank:   ~120 l on a cradle on the upper beams, pump, filter and pressure regulator under the rear beams.
#   Camera: wide-angle global-shutter camera on a mast at the front, 1.48 m high, looking 55 degrees down.
#           The robot's GNSS antenna moves to the top of the mast (the mast would otherwise shade it).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres at (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = 500.0            # wheel centres at y = +-500
robot_axle_z = 215.0            # ground_to_axle
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_tire_rear_y = -robot_axle_y - robot_tire_d / 2.0     # -715
robot_front = robot_axle_y + robot_tire_d / 2.0            # 715
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)        # x-direction beams (chassis_beam_1), x -500 .. 500
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)        # y-direction beams (chassis_beam_2), y -650 .. 650
robot_upper_beam_z = (659.0, 699.0)
robot_beam = 40.0
robot_bracket_x = (261.0, 489.0)        # wheel brackets: inner and outer face
robot_half_width = 489.0
robot_gnss = (0.0, 575.0, 659.0)        # robot antenna: stem on the front outer beam (stud down to z 594)
robot_gnss_nut_z = 610.6                # M8 nut under that beam
robot_steer_max = 30.0                  # degrees
robot_kg = 161.5                        # agbot comparison (not weighed)
robot_track = 2.0 * robot_wheel_x
robot_wheelbase = 2.0 * robot_axle_y
grid = 50.0                     # beam holes M10 (10.4): lower beams x = +-125 .. +-475, upper beams |y| = 275 .. 625
m10_hole = 10.4
m8_hole = 8.5

# ---------------------------------------------------------------------
# Liquid
# ---------------------------------------------------------------------
liquid_density = 1.0            # kg/l, herbicide diluted in water

# ---------------------------------------------------------------------
# Tank (rotomoulded PE, wall 6) on a cradle: 2 cross tubes 40 x 40 x 3 on the upper beams (M10 through the holes at
# y -375 and 275), rubber strip, 2 flat straps. Front stays behind the steering stacks (plates from y 405).
# ---------------------------------------------------------------------
cradle_y = (-375.0, 275.0)
cradle_tube = 40.0
cradle_wall = 3.0
cradle_half_len = 460.0
cradle_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + cradle_tube)     # 699 .. 739
pad_t = 5.0
tank_z0 = cradle_z[1] + pad_t   # 744
strap_w = 50.0
strap_t = 3.0
tank_wall = 6.0
tank_x = 400.0                  # half width
tank_y = (-400.0, 320.0)
tank_h = 240.0
tank_z = (tank_z0, tank_z0 + tank_h)        # 744 .. 984
tank_r = 60.0                   # radius of the vertical edges
tank_nominal = 120.0            # l, filled to the 120 l mark (gross ~126 l)
fill_cap = (-230.0, 150.0, 150.0, 36.0)     # x, y, diameter, height (screw lid with a basket strainer)
level_sensor = (250.0, 150.0, 50.0, 80.0)   # ultrasonic level sensor: x, y, d, h
vent = (250.0, -300.0, 20.0, 50.0)
outlet_xy = (0.0, -250.0)       # bottom fitting to the suction filter (between the cradle tubes)
return_xy = (90.0, -250.0)      # bottom fitting for the bypass return (submerged: no foam)
bulkhead = (40.0, 20.0)         # bulkhead nut under the tank: diameter, height

# ---------------------------------------------------------------------
# Rear subframe: one plate under the two rear lower beams (8 x M10), carries the two boom hangers (welded webs),
# the pump, the suction filter and the pressure regulator block.
# ---------------------------------------------------------------------
sub_x = (-200.0, 200.0)
sub_y = (-600.0, -400.0)
sub_t = 10.0
sub_z = (robot_lower_beam_z[0] - sub_t, robot_lower_beam_z[0])   # 609 .. 619
sub_bolt_x = (-175.0, -125.0, 125.0, 175.0)
web_x = 150.0                   # boom hanger webs at x = +-150 (t 8): clear of the pump and of the wheel brackets
web_t = 8.0

# Pump: 24 V diaphragm pump with a pressure switch, 11 l/min free flow, 4 bar (e.g. Seaflo 33-series / Shurflo 8000)
pump_head = ((-40.0, 40.0), (-505.0, -440.0), (515.0, 600.0))
pump_motor = (85.0, -505.0, -620.0, 555.0)  # diameter, y0, y1, z axis (x = 0)
pump_foot = ((-30.0, 30.0), (-570.0, -545.0))
pump_q_free = 11.0              # l/min
pump_q_3bar = 9.5               # l/min at 3 bar (estimated from typical curves)
pump_w = 110.0                  # W electrical at 3 bar (estimated)
pump_kg = 3.0
filter_xy = (-100.0, -470.0)    # suction filter (bowl), 50 mesh
filter_d = 60.0
filter_z = (480.0, 590.0)
port_z = 560.0                  # filter outlet / pump inlet / pump outlet height
regulator = ((40.0, 110.0), (-505.0, -445.0), (530.0, 600.0))   # pressure regulator + bypass + pressure sensor
hose_d = 16.0                   # 1/2" spray hose (outside ~16 in the model)
hose_z = 575.0                  # suction and return hoses run under the rear beams at this height
feed_x = 90.0                   # pressure hose to the boom: x of the tee on the boom pipe

# ---------------------------------------------------------------------
# Boom (section in y-z). Square carrier tube, the wet pipe (stainless 1/2") under it, the nozzle bodies under the pipe.
# ---------------------------------------------------------------------
n_nozzles = 15
nozzle_pitch = 250.0
work_width = n_nozzles * nozzle_pitch       # 3750
centre_half = 625.0             # centre section x -625 .. 625 (5 nozzles)
wing_len = 1250.0               # each wing (5 nozzles)
wing_gap = 0.0                  # end plates of centre and wing tube touch at 0 degrees: hard stop below the hinge
end_plate = 4.0                 # end plates (steel 4 mm) welded on the inner wing end and the centre tube ends
nozzle_h = 400.0                # nozzle tip above the ground (300 .. 500 by moving the tube on the clamp plates)
boom_y = -840.0                 # carrier tube centre: 105 mm behind the rear tyres (-715) + 20 half tube
tube = 40.0                     # centre: steel 40 x 40 x 2 galvanised; wings: aluminium 40 x 40 x 3
tube_wall_centre = 2.0
tube_wall_wing = 3.0
tube_z = (nozzle_h + 100.0, nozzle_h + 140.0)   # 500 .. 540
pipe_od = 21.3                  # stainless 1/2" (wet boom), filled with spray liquid
pipe_wall = 1.6
pipe_z = tube_z[0] - 16.0       # 484: pipe top 5.35 under the tube (nozzle clamp ring OD 30)
pipe_end_centre = 612.0         # centre pipe x +-612, riser behind the tube up to the hinge swivel
riser_y = boom_y - 38.0         # -878
pipe_end_wing = 650.0           # wing pipe starts here (riser), ends at the wing tip
nozzle_x = tuple(-0.5 * (n_nozzles - 1) * nozzle_pitch + i * nozzle_pitch for i in range(n_nozzles))
clip_x = (-375.0, -125.0, 125.0, 375.0)     # pipe clips on the centre tube (wings: between the nozzles)

# Nozzle body (clamp-on, 12/24 V PWM solenoid), from the bottom: flat-fan tip, cap, body, clamp ring on the pipe
nz_tip = (16.0, nozzle_h, nozzle_h + 28.0)  # d, z0, z1
nz_cap = (30.0, nozzle_h + 28.0, nozzle_h + 50.0)
nz_body = (26.0, nozzle_h + 50.0, pipe_z - 15.0)  # square, z0, z1 (450 .. 472)
nz_clamp = (30.0, 26.0)         # ring OD, length (x), around the pipe
nz_coil = (28.0, 40.0)          # solenoid coil: d, length behind the body (-y)
nz_coil_z = nozzle_h + 61.0
nozzle_angle = 40.0             # flat fan, e.g. TeeJet TP40015E / Lechler ST 40-015
nozzle_q_3bar = 0.59            # l/min per nozzle at 3 bar (size 015)
spray_p = 3.0                   # bar
valve_ms = 25.0                 # solenoid opening / closing time (estimated)
kg_nozzle = 0.25                # body + coil + cap + tip

# Clamp plates (welded to the ends of the hanger webs): tube bolted with 2 x M10 through-bolts per plate,
# 3 hole pairs 50 mm apart give nozzle heights 350 / 400 / 450.
clamp_x = 40.0                  # plate x = web_x +- 40
clamp_y = (boom_y + tube / 2.0, boom_y + tube / 2.0 + 8.0)  # -820 .. -812 (against the front face of the tube)
clamp_z = (tube_z[0] - 50.0, sub_z[0])      # 450 .. 609
bolt_z = (tube_z[0] + 10.0, tube_z[0] + 30.0)   # 510, 530
height_steps = (-50.0, 0.0, 50.0)

# ---------------------------------------------------------------------
# Hinge and fold actuator. Hinge axis along y at (+-625, z 565). Fold angle phi: 0 = working (horizontal),
# 90 = folded up (vertical). Lever pin on the wing at 90 mm from the hinge, 45 degrees up-out; actuator base pin on
# the centre tube at 420 mm inside the hinge, same height as the lever pin -> the actuator is horizontal at both ends.
# ---------------------------------------------------------------------
hinge_z = tube_z[1] + 25.0      # 565
hinge_pin_d = 16.0
lug_t = 8.0                     # 2 fixed lugs per hinge at y = boom_y +- (8 .. 16)
lug_gap = 8.0
knuckle_t = 12.0                # wing knuckle / lever plate, y = boom_y +- 6
lever_r = 90.0
lever_ang = 45.0
lever_pin = (lever_r * math.cos(math.radians(lever_ang)), lever_r * math.sin(math.radians(lever_ang)))  # (63.6, 63.6)
act_base_dx = 420.0             # base pin at x = +-(625 - 420) = +-205
act_pin_d = 10.0
act_base = (centre_half - act_base_dx, hinge_z + lever_pin[1])      # (205, 628.6) right side
act_stroke = 150.0              # 24 V linear actuator, 1000 N, 40 mm/s, IP66 (e.g. Linak LA36 class / generic)
act_closed = 350.0              # pin-pin retracted
act_force = 1000.0              # N
act_speed = 40.0                # mm/s
act_w = 60.0                    # W at full load (estimated)
act_body_d = 45.0
act_body_u = (25.0, 300.0)      # body tube along the actuator axis from the base pin
act_rod_d = 20.0
act_rod_len = 300.0
act_motor = (40.0, 40.0, 200.0, 40.0)       # motor alongside: d, u0, u1, offset (up)
act_kg = 2.6
fold_up = 90.0
fold_stop = 92.0                # end of the actuator travel past vertical (rest)

# Wing tip guard: bent tube Ø20 around the outer end, protects the last nozzle against posts and the ground
guard_d = 20.0
guard_x = (work_width / 2.0 - 15.0, work_width / 2.0 + 35.0)    # 1860 .. 1910
guard_z = (nozzle_h - 15.0, tube_z[0] + 20.0)                   # 385 .. 520

# Hose across the hinge: a swivel coaxial with the hinge axis (the hose does not bend when folding)
swivel = (24.0, riser_y - 15.0, riser_y + 9.0)      # d, y0, y1 (behind the hinge pin head)

# ---------------------------------------------------------------------
# Camera mast at the front: plate under the two front lower beams (8 x M10), square tube 50 x 50 x 3 in front of the
# beams, two braces to the inner front beam, camera on a tilt bracket, GNSS antenna on the top.
# ---------------------------------------------------------------------
mast_plate = ((-200.0, 200.0), (400.0, 770.0), (robot_lower_beam_z[0] - 8.0, robot_lower_beam_z[0]))
mast_plate_taper = (600.0, 680.0, 80.0)     # full width up to y 600, narrows to x +-80 at y 680 (in front of the beams)
mast_plate_window = ((-95.0, 95.0), (460.0, 540.0))     # lightening hole between the two front beams
mast_plate_bolt_x = (-175.0, -125.0, 125.0, 175.0)
gnss_clear_hole = 40.0          # hole in the plate around the old antenna stud / nut
mast_xy = (0.0, 720.0)
mast_tube = 50.0
mast_wall = 3.0
mast_z = (mast_plate[2][1], 1560.0)
gusset_t = 8.0
brace_d = 25.0
brace_top_z = 1050.0
brace_foot = (125.0, robot_lower_beam_y[2], robot_lower_beam_z[1])     # on the inner front beam, M10 at x +-125
brace_end_dy = 38.0             # brace lands 38 mm in front of the bolt (foot plate overhangs the beam)
cap_t = 6.0

# Camera: industrial global-shutter camera, 2/3" 5 MP (2448 x 2048, 3.45 um), f = 4 mm lens, IP67 housing
cam_pivot = (0.0, 830.0, 1480.0)
cam_pitch = 55.0                # degrees below horizontal
cam_box = (70.0, 120.0, 70.0)   # x, along the optical axis, z (local, axis = +y before tilting)
cam_lens = (44.0, 25.0)         # lens tube d, length in front of the housing
cam_hood = (70.0, 160.0, 3.0)   # sun / rain hood on top: width, length, thickness
cam_arm = ((38.0, 44.0), (mast_xy[1] + mast_tube / 2.0, 845.0), (1455.0, 1500.0))   # 2 arms: |x|, y, z
cam_px = (2448, 2048)
cam_pixel = 0.00345             # mm
cam_f = 4.0                     # mm
cam_fps = 20.0
infer_ms = 60.0                 # detection on the computer (Jetson class), per frame (estimated)

# GNSS antenna (the robot's own, moved from the front beam to the mast top)
gnss_on_mast = True
ant_stem = (30.0, 25.0)
ant_dome = (150.0, 55.0)

# ---------------------------------------------------------------------
# Control box on top of the rear lower beams, behind the tank: vision computer, 16-channel valve driver, pump and
# actuator drivers, DC-DC 48 -> 24 / 12 V
# ---------------------------------------------------------------------
box_x = (-250.0, 250.0)
box_y = (-590.0, -412.0)
box_h = 150.0
box_base = ((-295.0, 295.0), (-600.0, -405.0), 4.0)
box_bolt_x = (-275.0, 275.0)

# ---------------------------------------------------------------------
# Operation (for ssp_calc and the animation)
# ---------------------------------------------------------------------
speed = 1.0                     # m/s working speed
spray_margin = 50.0             # mm sprayed before and after the weed (along y) and beside it (across)
weed_cover = 0.05               # fraction of the field area that gets sprayed (patchy docks/thistles, estimated)
field_eff = 0.80                # headland turns, refilling
battery_kwh = 2.4
drive_w = 450.0                 # W driving on grass at 1 m/s with this load (estimated)
computer_w = 40.0               # vision computer + camera
valve_w = 8.0                   # W per open solenoid valve (PWM holding lower)
c_rr = 0.08
wheel_load_max = 500.0          # kg per wheel (Quinder hub motor datasheet)
dyn = 2.5                       # dynamic factor for bumps on the boom (vertical)
