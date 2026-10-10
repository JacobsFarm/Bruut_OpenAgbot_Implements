import math

# =====================================================================
# Field marker, simple - parameters
# Stakes out points from a coordinate list: the robot stops roughly on the point, a stage behind the robot
# (X across, Y along the driving direction, Z down) puts a spray-paint head on the exact spot.
# The GNSS antenna sits on a mast straight above the spray nozzle.
#
# Built from bought linear modules (one belt module, two ball-screw modules), laser-cut steel and aluminium
# plates and standard pipe: no machining, only drilling, bending and a few welds.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres at (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = -500.0           # rear axle
robot_axle_z = 215.0            # ground_to_axle
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_tire_rear_y = robot_axle_y - robot_tire_d / 2.0     # -715, back of the rear tyres at axle height
robot_rear_beam_y = (-575.0, -425.0)    # centre lines of the rear lower beams (rear_outer, rear_inner)
robot_lower_beam_z = (619.0, 659.0)     # bottom and top of the lower beams (world)
robot_upper_beam_end_y = -650.0         # the upper beams (y direction, x +-325 / +-425) end here
robot_bracket_x = 261.0                 # inner face of the rear wheel brackets (x 261..489, y -620..-380)
robot_bracket_y = -620.0
robot_grid = 50.0               # hole grid of the beams, M10 (hole 10.4) at x = +-125, +-175, ... +-475
robot_gnss = (0.0, 575.0, 740.0)        # top of the robot's own antenna (front cross beam)
m10_hole = 10.4
m8_hole = 8.5
m6_hole = 6.6

# ---------------------------------------------------------------------
# Working envelope of the spray nozzle (robot coordinates)
# ---------------------------------------------------------------------
x_stroke = 800.0                # tool x from -400 to +400: as wide as the robot, two points 0.8 m apart per stop
y_stroke = 200.0                # capture window in the driving direction: the robot stops within +-100 mm
z_stroke = 300.0
y_tool_front = -800.0           # front-most tool axis: tube, shroud and rods stay >= 15 mm behind the rear tyres (-716)
y_tool_nom = y_tool_front - y_stroke / 2.0      # -890

# ---------------------------------------------------------------------
# Motors: 3 x NEMA 23 closed-loop stepper 2.2 Nm (with encoder), driver for 24-50 V
# ---------------------------------------------------------------------
nema = 57.0                     # flange
nema_len = 102.0                # body 80 + encoder 22
nema_torque = 2.2               # Nm holding torque; usable at speed ~1.2 Nm
nema_torque_run = 1.2
nema_detent = 0.06              # Nm without power (estimated)
nema_kg = 1.4
coupler_len = 40.0              # coupling housing / motor adapter between module and motor

# ---------------------------------------------------------------------
# X axis: belt-driven linear module, 80 mm profile, stroke 800 (generic, e.g. "belt linear module 80, 800 mm")
# Base to the front against the two hangers (T-slot nuts M8), carriage at the back.
# Drive end with the motor standing up at -x, idler end at +x.
# ---------------------------------------------------------------------
xm_w = 80.0                     # body width (world z)
xm_h = 55.0                     # body depth (world y), base face at the front
xm_car_len = 150.0              # carriage (x)
xm_car_t = 17.5                 # carriage plate (y)
xm_gap = 0.5
xm_end = (60.0, 40.0)           # drive end (-x), idler end (+x)
xm_base_y = -640.0              # base face (front)
xm_z = (530.0, 610.0)
xm_slot_z = (550.0, 590.0)      # 2 T-slots (8 mm) in the base face
xm_pulley_pd = 31.83            # HTD-5M 20 teeth
xm_belt_w = 25.0
xm_kg_per_m = 5.5               # body + belt; carriage 0.8 kg
xm_car_kg = 0.8

# ---------------------------------------------------------------------
# Y and Z axis: the same ball-screw linear module (SFU1605, lead 5), 60 mm wide, cover strip, motor in line.
# Length = stroke + carriage + 2 end blocks.
# ---------------------------------------------------------------------
sm_w = 60.0                     # width
sm_h = 45.0                     # base -> carriage seat
sm_car_len = 80.0
sm_car_t = 15.0
sm_gap = 0.5
sm_end = 25.0
sm_lead = 5.0
sm_kg_per_m = 4.0
sm_car_kg = 0.35


def sm_length(stroke):
    return stroke + sm_car_len + 2.0 * sm_end


# ---------------------------------------------------------------------
# The stack, seen from behind (x to the right):
#   X carriage -> XY bracket (steel, welded): adapter plate on the carriage + Y plate (y-z plane) + 2 gussets
#   Y module on its side against the Y plate, carriage facing +x
#   Z adapter plate (aluminium) on the Y carriage, Z module upright against it, carriage facing +x
#   head mount plate on the Z carriage, the paint head hangs on it (2 pins + 2 star knobs)
# x0 = -x face of the Y plate. Offsets from x0 along +x:
# ---------------------------------------------------------------------
xy_plate_t = 8.0
xy_plate_dx = 110.0             # x0 = X carriage centre - 110
xy_adapter_t = 8.0
z_adapter_t = 10.0
head_mount_t = 8.0
head_plate_t = 6.0
tube_od = 75.0                  # PVC pipe 75 x 1.8 (standard drain pipe) as guide for the spray can
tube_wall = 1.8

ym_x = (xy_plate_t, xy_plate_t + sm_h)                          # Y module body (x - x0)
ym_car_x = (ym_x[1] + sm_gap, ym_x[1] + sm_gap + sm_car_t)      # Y carriage
za_x = (ym_car_x[1], ym_car_x[1] + z_adapter_t)                 # Z adapter
zm_x = (za_x[1], za_x[1] + sm_h)                                # Z module body
zm_car_x = (zm_x[1] + sm_gap, zm_x[1] + sm_gap + sm_car_t)      # Z carriage
hm_x = (zm_car_x[1], zm_car_x[1] + head_mount_t)                # head mount plate
hp_x = (hm_x[1], hm_x[1] + head_plate_t)                        # head plate
tool_from_x0 = hp_x[1] + tube_od / 2.0                          # 190
tool_dx = tool_from_x0 - xy_plate_dx                            # tool axis - X carriage centre (80)

# X travel: the tool axis runs from -x_stroke/2 to +x_stroke/2
xc_mid = -tool_dx                                               # X carriage centre with the tool at x = 0
xm_x = (xc_mid - x_stroke / 2.0 - xm_car_len / 2.0 - xm_end[0],
        xc_mid + x_stroke / 2.0 + xm_car_len / 2.0 + xm_end[1])
xm_len = xm_x[1] - xm_x[0]
xm_car_y = (xm_base_y - xm_h - xm_gap - xm_car_t, xm_base_y - xm_h - xm_gap)   # (-713, -695.5)

# XY bracket (y is fixed, x moves with the carriage; x relative to the X carriage centre)
xy_adapter_y = (xm_car_y[0] - xy_adapter_t, xm_car_y[0])        # (-721, -713)
xy_adapter_dx = (-150.0, 75.0)
xy_adapter_z = (410.0, 620.0)
xy_adapter_low_dx = (-150.0, -50.0)                             # lower leg down to the Y plate bottom
xy_adapter_top_z = 530.0                                        # the rest only over the carriage (z 530..620)

# Y module: front end just behind the adapter plate
ym_len = sm_length(y_stroke)                                    # 330
ym_y = (y_tool_front + sm_car_len / 2.0 + sm_end, 0.0)          # front end -725
ym_y = (ym_y[0], ym_y[0] - ym_len)                              # (-725, -1055)
ym_z = (420.0, 480.0)
# Y plate outline (y, z), x0 .. x0 + 8
y_plate_pts = ((xy_adapter_y[0], 620.0), (-830.0, 620.0), (-900.0, 490.0), (ym_y[1], 490.0), (ym_y[1], 410.0),
               (xy_adapter_y[0], 410.0))
gusset_t = 8.0
gusset_dx = 40.0                # on the -x side of the Y plate, top and bottom
gusset_top_len = 100.0
gusset_bot_len = 150.0

# Z module (fixed to the Y carriage), stands upright
zm_len = sm_length(z_stroke)                                    # 430
zm_z = (150.0, 150.0 + zm_len)                                  # (150, 580)
za_dy = 40.0                                                    # Z adapter y = tool y +- 40
za_z = (380.0, 732.0)
zc_range = (zm_z[0] + sm_end + sm_car_len / 2.0, zm_z[1] - sm_end - sm_car_len / 2.0)   # Z carriage centre (215, 515)

# ---------------------------------------------------------------------
# Paint head (z relative to the Z carriage centre zc, y relative to the tool axis)
# Inverted marking-paint spray can (500 ml, Ø65) in a PVC guide tube. The nozzle rests on the bottom plate;
# a waterproof servo pushes the can 5 mm down -> the valve opens. A spray shroud (PVC 110) hangs on 2 sprung
# rods under the head: it rests on the ground while spraying (wind shield, clean dot, fixed nozzle height)
# and an inductive sensor sees it lift = ground contact (touch-off).
# ---------------------------------------------------------------------
hm_dy = 60.0                    # head mount plate and head plate: y +-60
hm_dz = (-60.0, 60.0)
pin_dy = 50.0                   # 2 hook pins (top) and 2 star knobs M8 (bottom)
pin_dz = 40.0
knob_dz = -40.0
pin_d = 12.0
hp_dz = (-179.0, 145.0)         # head plate (vertical leg of the bent plate)
bp_t = 6.0                      # bottom plate (horizontal leg), under the tube
bp_dz = (-185.0, -179.0)
bp_dx = 95.0                    # bottom plate to tool axis + 95 (sensor)
bp_dy = 70.0
ubolt_dz = (-150.0, -95.0)      # 2 U-bolts M8 for 76 mm pipe around the tube
ubolt_d = 8.0
tube_dz = (-179.0, 90.0)
can_d = 65.0
can_dz = (-168.0, 77.0)         # can body (the bottom of the can is up)
can_cup = (35.0, -176.0, -168.0)
can_nozzle = (20.0, -179.0, -176.0)     # actuator cap, rests on the bottom plate
can_press = 5.0                 # valve stroke
pusher = (60.0, 77.0, 83.0)     # disc on top of the can
spray_hole = 14.0
servo_box = ((5.0, 45.0), (-40.0, -2.0), (118.0, 138.0))   # x from hp_x[1], y, z
servo_shaft = (15.0, 128.0)     # x from hp_x[1], z
lever_dz = (123.0, 133.0)

# shroud
shroud_od = 110.0               # PVC pipe 110 x 3.2
shroud_wall = 3.2
shroud_ring_t = 4.0
ring_top_dz = -215.0            # ring top in the free position
shroud_len = 100.0
shroud_hole = 60.0
rod_d = 10.0
rod_r = 70.0                    # rods on a circle R70 around the tool axis, at +-45 degrees from +x
rod_ang = 45.0                  # (not straight to the front: they stay away from the tyres)
rod_top_dz = -160.0
spring_od = 17.0
spring_id = 11.0
collar = (20.0, 9.0)            # shaft collar Ø10, OD 20, rests on the bushing flange
bushing = (12.0, 10.0, 18.0, 2.0)       # OD, length, flange OD, flange thickness
shroud_travel = 8.0             # lift until the springs are solid (chamber 26, solid 18): 1 mm before the sensor face
sensor_dx = 75.0                # M12 inductive sensor at tool x + 75
sensor_face_gap = 9.0           # sensor face above the ring (target ear) in the free position
sensor_sn = 4.0                 # switching distance -> switches after ~5 mm lift
sensor_len = 60.0
spring_k = 1.0                  # N/mm per spring
spring_pre = 10.0               # N per spring in the free position

SHROUD_BOTTOM_DZ = ring_top_dz - shroud_ring_t - shroud_len     # -319
NOZZLE_DZ = can_nozzle[1]                                       # -179


def zc_for_ground(ground_z=0.0, lift=0.0):
    """Z carriage centre at which the shroud rests on the ground (lifted 'lift' mm against the springs)."""
    return ground_z - SHROUD_BOTTOM_DZ - lift


ZC_PARK = zc_range[1]           # shroud 196 mm above the ground
ZC_WORK = zc_for_ground(0.0, 6.0)   # touch-off: the sensor has switched, 6 mm compression

# ---------------------------------------------------------------------
# Mast with the second GNSS antenna, coaxial with the nozzle, on top of the Z adapter
# ---------------------------------------------------------------------
mast_bracket_t = 10.0
mast_bracket_dy = 25.0
mast_d = 25.0                   # aluminium tube 25 x 2, 5/8"-11 adapter on top
mast_z = (za_z[1] + mast_bracket_t, 940.0)
mast_collar = (40.0, 12.0)
ant_stem = (30.0, 25.0)         # same antenna as the robot: stem + dome Ø150 x 55
ant_dome = (150.0, 55.0)
ant_phase_dz = 20.0             # phase centre above the dome base (estimated)
rx_box = ((-50.0, 0.0), (-50.0, 50.0), (625.0, 695.0))     # receiver + IMU box: x from za_x[0], y, z

# ---------------------------------------------------------------------
# Hangers (2x, identical): top plate under both rear lower beams (4 x M10 in the grid), web, flange for the
# base of the X module (4 x M8 in its T-slots). Laser cut, welded.
# ---------------------------------------------------------------------
hanger_x = 200.0
hanger_bolt_dx = 25.0           # M10 at x = 175 and 225
hanger_w = 100.0                # x 150..250: 11 mm clear of the wheel bracket (x 261)
hanger_top_t = 10.0
hanger_top_y = (xm_base_y, -405.0)
flange_t = 8.0
web_t = 8.0
web_pts = ((-405.0, robot_lower_beam_z[0] - hanger_top_t), (xm_base_y + flange_t, robot_lower_beam_z[0] - hanger_top_t),
           (xm_base_y + flange_t, xm_z[0]), (-575.0, xm_z[0]), (-450.0, 590.0), (-405.0, 590.0))

# ---------------------------------------------------------------------
# Control box on the rear lower beams: 3 stepper drivers, DC-DC 48 -> 36 V, controller, servo supply
# ---------------------------------------------------------------------
box_x = (-110.0, 110.0)         # between the bolt heads (x +-125); drivers on edge inside
box_y = (-590.0, -410.0)
box_h = 100.0
box_base_t = 3.0
box_base_x = (-140.0, 140.0)    # M8 through the grid holes at x = +-125
box_base_y = (-600.0, -400.0)

# ---------------------------------------------------------------------
# Operation (for mrk_calc and the animation)
# ---------------------------------------------------------------------
battery_v = 48.0
drive_speed = 0.5               # m/s between points
drive_acc = 0.5                 # m/s2
settle_s = 1.5                  # standstill before measuring
measure_s = 2.5                 # averaging GNSS + IMU
x_v, x_a = 500.0, 2000.0        # mm/s, mm/s2
y_v, y_a = 150.0, 1000.0        # SFU1605 at 1800 rpm
z_v, z_a = 150.0, 1000.0
z_touch_v = 40.0                # last 40 mm before the expected ground: slow, until the sensor switches
z_touch_zone = 40.0
servo_s = 0.15
spray_s = 0.6
photo_s = 0.5
press_max = 300.0               # N, software limit of the Z axis (motor current) for heavier heads later

# Paint (500 ml marking spray, estimated from typical can data: 60-80 m of 50 mm line per can)
can_line_m = 70.0
can_line_w = 0.05
spray_angle = 22.0              # full cone angle of the marking nozzle (estimated)
dot_overhead = 3.0              # overspray, start/stop of the valve

# Accuracy (1 sigma, estimated)
rtk_sigma = 10.0                # mm horizontal, fixed solution, base < 10 km
ts_sigma = 2.0                  # robotic total station with a 360 degree prism on the mast
imu_sigma_deg = 0.1
heading_sigma_deg = 0.5
stage_sigma = 1.0
tool_sigma = 3.0                # dot centre on the ground
