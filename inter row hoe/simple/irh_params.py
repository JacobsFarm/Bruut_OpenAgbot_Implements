import math

# =====================================================================
# Inter-row hoe (simple) - parameters
# Single-axis (left/right) guided hoe behind the Bruut OpenAgbot (standard robot), for row crops such as maize.
# The rear toolbar and lift arms are those of the grassland harrow (push blade geometry, mirrored). The arms carry a
# carrier with 2 HGR15 rails across the robot; a shift plate on 4 carriages is moved +-75 mm by a ball screw SFU1610
# and a closed-loop NEMA23. Two hoe units hang on parallelograms from the shift plate, each in one inter-row behind a
# rear wheel, with a gauge wheel, a goosefoot share in the middle and two L-blades next to the rows.
# A camera on a mast on the shift plate looks down at the middle row; the controller keeps the shift plate on it.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_rear_beam_y = (-575.0, -425.0)    # centres of the rear lower beams (40 x 40)
robot_lower_beam_z = (619.0, 659.0)
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_mass = 160.0              # kg, estimated (agbot comparison)
robot_cg_y = 0.0                # estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Crop: rows the hoe is laid out for. The robot straddles one row (x = 0) with its wheels in the two inter-rows
# next to it, the hoe units work those two inter-rows (loosening the wheel tracks at the same time).
# ---------------------------------------------------------------------
row_spacing = 750.0             # maize (also 3 rows of beet at 500 with other units: see RATIONALE)
row_band = 100.0                # untouched band each side of a row (crop safety + guidance error)
unit_x = (-375.0, 375.0)        # unit centres = inter-row centres, at shift 0
work_depth = 20.0               # mm, shares below the ground line (hoeing young weeds: 15..30)

# ---------------------------------------------------------------------
# Rear toolbar (as the grassland harrow): 80 x 80 x 4 on 2 hangers, 2 x M10 per beam
# ---------------------------------------------------------------------
tb = 80.0
tb_wall = 4.0
tb_x = (-450.0, 450.0)
tb_y = (-860.0, -780.0)         # rear of the tyre at y -715
tb_z = (450.0, 530.0)
hanger_x = 200.0
hanger_bolt_dx = 25.0
hanger_top_t = 10.0
hanger_top_w = 100.0
hanger_top_y = (-610.0, -390.0)
web_t = 6.0
web_dx = 42.0
web_pts = ((-395.0, 609.0), (-700.0, 609.0), (-890.0, 545.0), (-890.0, 440.0), (-770.0, 440.0), (-560.0, 560.0),
           (-395.0, 560.0))

# ---------------------------------------------------------------------
# Lift arms (as the grassland harrow): rect tube 60 x 40 x 3 on O20 pins in forks under the toolbar
# ---------------------------------------------------------------------
arm_x = 300.0
arm_w = 40.0
arm_h = 60.0
arm_wall = 3.0
pivot = (-840.0, 410.0)
pivot_d = 20.0
lug_t = 8.0
lug_gap = arm_w + 2.0

# ---------------------------------------------------------------------
# Carrier (weldment on the arm ends): main beam 60 x 60 x 4 across, rail plate 10 mm on its rear face
# ---------------------------------------------------------------------
main_wall = 4.0
main_y = (-1020.0, -960.0)
main_z = (266.0, 326.0)
carrier_x = 545.0               # half length of main beam and rail plate
rail_plate_y = (-1030.0, -1020.0)
rail_plate_z = (200.0, 410.0)

# Linear guide: 2 x HGR15 rail (15 x 15) on the rear face of the rail plate, 2 HGH15CA carriages per rail
rail_z = (230.0, 340.0)         # rail centres
rail = 15.0
rail_x = 460.0                  # half length of the rails
car_len = 61.0                  # carriage along x
car_w = 34.0                    # across (z)
car_y = (-1058.0, -1046.0)      # carriage body behind the rail (the part round the rail is left out)
car_x = (-300.0, 300.0)         # carriage centres at shift 0

# Ball screw SFU1610 (lead 10) between the rails, fixed bearing BK12 left, floating BF12 right, NEMA23 right
screw_d = 16.0
screw_lead = 10.0
screw_z = 285.0
screw_y = -1044.0
screw_x = (-515.0, 522.0)
bearing_x = ((-515.0, -490.0), (495.0, 520.0))   # BK12, BF12 blocks
bearing_y = (-1056.0, -1030.0)
bearing_z = (255.0, 315.0)
coupling = (522.0, 543.0, 25.0)                  # x0, x1, O (jaw coupling 14/10 mm)
motor_flange_x = (545.0, 553.0)   # outside the reach of the right unit head (x 530 at shift +75)
motor = 57.0                    # NEMA23 square
motor_len = 76.0                # 2.0 Nm closed-loop stepper
motor_torque = (2.0, 1.2)       # Nm at 0 and at 600 rpm (typical curve, estimated)
motor_kg = 1.4
nut_box = (60.0, 34.0)          # nut housing x, z

# Shift plate: 8 mm, on the carriages; units and camera mast on its rear face
shift_y = (-1066.0, -1058.0)
shift_x = 380.0                 # half width
shift_z = (205.0, 405.0)
shift_stroke = 75.0             # +- mm
SHIFT_POSES = (-75.0, 0.0, 75.0)

# ---------------------------------------------------------------------
# Hoe unit (one per inter-row), in unit coordinates u = x - unit centre
# ---------------------------------------------------------------------
head_plate_y = (-1076.0, -1066.0)
head_plate_u = 80.0             # half width
head_z = (230.0, 400.0)
cheek_u = (52.0, 60.0)          # cheeks of head and post
head_cheek_y = (-1125.0, -1076.0)
link_u = (61.0, 71.0)           # flat bar links 40 x 10, outside the cheeks
link_h = 40.0
link_z = (260.0, 380.0)         # lower and upper link (parallelogram height 120)
link_y = (-1105.0, -1340.0)     # pin at the head, pin at the post
pin_d = 12.0
post_y = (-1360.0, -1320.0)     # post rect tube 120 x 40 x 4
post_u = 60.0
post_z = (140.0, 410.0)

wheel_d = 250.0                 # gauge wheel O250 x 80, runs in the inter-row in front of the shares
wheel_w = 80.0
wheel_y = -1180.0
fork_plate_y = (-1320.0, -1312.0)
fork_u = (46.0, 52.0)

beam_y = (-1360.0, -1700.0)     # unit beam 50 x 50 x 3 back from the post
beam_z = (180.0, 230.0)
cross_y = (-1640.0, -1600.0)    # cross bar 40 x 40 x 3 for the L-blades
cross_z = (140.0, 180.0)
cross_u = 280.0

share_w = 250.0                 # goosefoot (A-share), wings swept back
share_tip_y = -1380.0
share_back_y = -1470.0
share_t = 5.0
shank = (12.0, 40.0)            # rigid shank flat bar (u, y)
shank_y = (-1440.0, -1400.0)

lblade_u = (110.0, 275.0)       # L-blade: horizontal cutting part inward, upright wall next to the row
lblade_y = (-1665.0, -1600.0)
lblade_wall_h = 70.0
lblade_t = 5.0
lshank_u = (258.0, 270.0)
lshank_y = (-1640.0, -1600.0)

# ---------------------------------------------------------------------
# Camera on a mast (rect tube 40 x 40) on the shift plate, above the middle row
# ---------------------------------------------------------------------
mast_y = (-1106.0, -1066.0)
mast_z = (300.0, 760.0)
cam_box = (110.0, 60.0, 70.0)   # x, y (depth along the view), z
cam_tilt = 80.0                 # degrees down from horizontal (looks almost straight down at the share line)
cam_hfov = 70.0
cam_latency = 0.08              # s, image to shift command (estimated)

# ---------------------------------------------------------------------
# Lift actuator: same place as the grassland harrow, 24 V 3000 N (the shift group is heavier), stroke 100
# ---------------------------------------------------------------------
act_base = (-700.0, 660.0)
act_rod = (-990.0, 520.0)
act_body_d = 60.0
act_rod_d = 20.0
act_retracted = 240.0
act_stroke = 100.0
act_force = 3000.0
float_slot = 40.0
act_kg = 3.4
act_speed = 6.0                 # mm/s at 2000 N

lift_work = 0.0
lift_transport = 25.0           # + = hoe up
LIFT_POSES = (-4.0, 0.0, 12.0, 25.0)

# ---------------------------------------------------------------------
# Work (irh_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.2e-6                 # gauge wheel (solid rubber + plastic rim, as one density)
speed = 1.0                     # m/s (3.6 km/h), hoeing young maize
k_soil = 25e3                   # Pa, specific draft of a shallow sweep in a loam (estimated)
side_factor = 0.5               # lateral soil force on the shares while shifting / draft (estimated)
mu_tyre = 0.45                  # tyre on cultivated soil (estimated)
crr = 0.08                      # rolling resistance on loose soil
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
eta_drive = 0.75
eta_screw = 0.9
row_error_rtk = 20.0            # mm, 2 sigma lateral error of a GNSS row map + RTK (estimated)
row_error_cam = 10.0            # mm, 2 sigma of the camera row fit (estimated)
row_wander = 40.0               # mm, how far a sown row wanders over row_wander_len (estimated)
row_wander_len = 2.0            # m
# from build_irh.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 22.4, "mount_cg_y": -712.0, "lift_kg": 93.6, "lift_cg_y": -1161.0, "lift_cg_z": 266.0,
              "shift_kg": 57.7}


def rotate_yz(p, deg, c=pivot):
    """Point (y, z) turned about c by deg (+ = lifts a point behind the pivot)."""
    a = math.radians(-deg)
    dy, dz = p[0] - c[0], p[1] - c[1]
    return (c[0] + dy * math.cos(a) - dz * math.sin(a), c[1] + dy * math.sin(a) + dz * math.cos(a))


def act_length(lift_deg):
    r = rotate_yz(act_rod, lift_deg)
    return math.hypot(r[0] - act_base[0], r[1] - act_base[1])


def unit_width():
    """Hoed width (mm) of one unit: inter-row minus the band on both sides."""
    return row_spacing - 2 * row_band

# Counterweight on the front lower beams (the 2 x 20 kg blocks of the disc brushes / fertilizer spreader): the lifted
# hoe hangs 1.2 m behind the robot centre
ballast_kg = 40.0
ballast_cg_y = 575.0
