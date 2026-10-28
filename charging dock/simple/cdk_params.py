import math

# =====================================================================
# Charging dock (simple) - parameters
# Fixed docking station at the field edge or in the shed for the Bruut OpenAgbot (standard robot), with contacts.
# Robot side: a contact bracket under the front outer lower beam with 2 sprung copper pads (+ and -) and a pilot pin.
# Station: a base plate anchored in the ground, a post with the charger (48 V, 1 kW CC/CV) and a roof, and a contact
# head on an arm that reaches back between the front wheels, above the tyres and under the beams: 2 wide copper bars
# in a V-funnel that centres the robot's bracket. Power is only switched on after the pilot handshake.
# The station is drawn in robot coordinates with the robot docked (robot centre at the origin).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_r = 265.0
robot_tire_w = 100.0
robot_front_beam_y = (555.0, 595.0)     # front outer lower beam, z 619..659
robot_lower_beam_z = (619.0, 659.0)
robot_gnss_mount_x = 15.0       # GNSS mount x +-15 at y 560..590 hangs down to z 594
robot_steer_deg = 30.0
robot_mass = 160.0
battery_wh = 1900.0             # usable (estimated, as the other implements)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Robot side: bracket plate 6 mm on the front face of the front outer lower beam, PE block, 2 copper pads on springs
# ---------------------------------------------------------------------
bk_x = 170.0                    # half width
bk_y = (595.0, 601.0)           # plate against the beam front face
bk_z = (520.0, 659.0)
bk_flange = (601.0, 655.0)      # top flange over the beam (y), 6 mm, bolted down with 2 x M10 (grid x +-125)
pe_block = (300.0, 30.0, 70.0)  # x, y, z: PE carrier in front of the plate
pe_z = 535.0                    # bottom of the PE block
pad = (60.0, 8.0, 40.0)         # copper pad x, y, z
pad_x = 90.0                    # pads at x +-90 (+ right, - left)
pad_travel = 15.0               # spring travel; drawn half compressed (docked)
pilot_d = 10.0                  # pilot pin in the middle (signal: dock present, then power on)
pilot_len = 25.0

# ---------------------------------------------------------------------
# Station (docked pose): base plate on the ground, post, arm back to the contact head, funnel, charger, roof
# ---------------------------------------------------------------------
base = (1000.0, 500.0, 10.0)    # x, y, thickness
base_y0 = 820.0                 # front tyres end at y 765
post = 80.0                     # 80 x 80 x 4
post_y = 1050.0
post_h = 1300.0
arm = (60.0, 40.0)              # tube 60 wide x 40 high, from the post back to the head
arm_z = (480.0, 520.0)
head_y = (637.0, 660.0)         # head plate: its rear face carries the contact bars
head = (420.0, 23.0, 110.0)     # x, y, z of the head plate (PE 20 + steel 3)
head_z = 500.0                  # bottom of the head plate
bar = (150.0, 6.0, 40.0)        # copper contact bar x, y, z: wide in x for the lateral tolerance
bar_x = 90.0
funnel_len = 120.0              # V-plates from the head back towards the robot, opening the catch width
funnel_open = 80.0              # extra half width at the mouth
anchor = (20.0, 400.0)          # 4 ground anchors O20 x 400
charger_box = (300.0, 180.0, 400.0)     # 48 V 1 kW CC/CV charger, IP65, on the post
roof = (800.0, 600.0, 3.0)      # roof sheet over the post top (rain on the contacts and the charger)
gap_docked = 0.0                # pads touch the bars (springs half compressed)

# ---------------------------------------------------------------------
# Work (cdk_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
copper = 8.96e-6
pe = 0.96e-6
v_charge = 54.0                 # V CV setpoint (16S LiFePO4: 3.4 V per cell)
p_charger = 1000.0              # W
eta_charger = 0.92
cv_share = 0.12                 # part of the charge in the slow CV phase (estimated)
spring_k = 4.0                  # N/mm per pad spring (2 springs per pad)
r_contact = 0.5e-3              # Ohm per contact pair (copper, 2 x 40 N), estimated
approach_v = 0.15               # m/s last 0.5 m into the dock
lat_tol = 60.0                  # mm the robot may be off sideways (RTK + camera on the funnel marker)
yaw_tol = 3.0                   # degrees
pack_wh = {"robot": 1900.0, "robot_plus_battery_pack": 1900.0 + 2 * 2560.0 * 0.9}   # usable
loads_w = {"grass_meter": 239.0, "inter_row_hoe": 800.0, "compost_spreader": 1100.0}   # average W in work, estimated


def pads_y():
    """(y front face of the PE block, y front of the pads) on the robot, docked."""
    y0 = bk_y[1] + pe_block[1]
    return y0, y0 + pad[1]
