import math

# =====================================================================
# Solar canopy (sol) - parameters
# A roof of 2 (or 3) solar panels on a steel tube frame above the robot. The canopy is wider and longer
# than the robot, charges the battery through an MPPT charge controller. The GNSS antenna moves to the roof.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground z 0, mm.
# Origin = centre of the robot, so the implement stands directly in robot coordinates.
# All dimensions live here; never hardcode them in sol_parts.py / build_sol.py.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375                 # wheel centres x = +-375
robot_wheel_y = 500                 # wheel centres y = +-500
robot_axle_z = 215
robot_tire_d = 430
robot_tire_w = 100
robot_track_outer = robot_wheel_x + robot_tire_w / 2.0      # 425, outer edge of the tires (tipping line)
upper_beam_x = (325.0, 425.0)       # the 4 upper beams (y direction), centres x = +-325, +-425, 40 x 40
upper_beam_w = 40.0
upper_beam_half = 650.0             # upper beams are 1300 long (y -650..650)
upper_beam_top = 699.0              # world z of the top of the upper beams (215 + 484)
robot_grid = 50
m10_hole = 10.4
steer_stack_x_inner = 295.0         # steering stack of the front wheels: stay clear of x > 295 for |y| > 405
steer_stack_y_inner = 405.0

# ---------------------------------------------------------------------
# Base frame (same as the hybrid: 2 long tubes across the width bolted on the upper beams)
# ---------------------------------------------------------------------
tube = 50.0                         # square tube 50 x 50 x 3
tube_wall = 3.0
long_tube_y = (-350.0, 350.0)       # on the 50 mm grid of the upper beams
long_tube_half = 480.0              # length 960 (x -480..480)
mount_bolt_d = 10.0                 # M10 x 130 through tube, spacer sleeve, beam
mount_sleeve_d = 16.0
mount_bolt_len = 130.0
bolt_head_af = 17.0
bolt_head_k = 6.4
nut_m = 8.4

z_long_bot = upper_beam_top
z_long_top = z_long_bot + tube      # 749

# stringers along y on top of the long tubes under each row of posts
stringer = 40.0                     # square tube 40 x 40 x 3
stringer_wall = 3.0
stringer_x = 375.0                  # between the bolt rows x = 325 and 425 (bolt heads stay clear)
stringer_half = 380.0               # length 760 (y -380..380): stays clear of the steering stacks (|y| > 405)
z_str_bot = z_long_top
z_str_top = z_str_bot + stringer    # 789

# ---------------------------------------------------------------------
# Canopy
# ---------------------------------------------------------------------
post = 40.0                         # square tube 40 x 40 x 3
post_wall = 3.0
post_y = (-350.0, 350.0)            # over the long tubes
post_x = 375.0
rail = 40.0                         # top rails along y (40 x 40 x 3), on the posts
rail_wall = 3.0
rail_half = 700.0                   # length 1400
cross = 40.0                        # cross members along x (40 x 40 x 3), on the rails, under the panels
cross_wall = 3.0
cross_y = (-350.0, 350.0)           # carry the panel at 2 lines
z_rail_bot = 1450.0
z_rail_top = z_rail_bot + rail
z_cross_top = z_rail_top + cross    # 1530 = underside of the panels

brace_d = 25.0                      # round tube D25 x 2 for all braces
brace_wall = 2.0
strut_x_in = 480.0                  # strut start: end of the long tube
strut_x_out_from_edge = 120.0       # strut end: this far inside the end of the cross member
brace_y_in = 60.0                   # y-brace start on the stringer, this far from the centre
brace_z_end_from_top = 60.0         # y-brace end: this far below the post top

# ---------------------------------------------------------------------
# Solar panels (generic 60-cell class panel, not a specific brand)
# ---------------------------------------------------------------------
n_panels = 2                        # 2 or 3, side by side in x
panel_w = 1000.0                    # x
panel_l = 1650.0                    # y
panel_t = 35.0                      # aluminium frame height
panel_gap = 40.0                    # gap between the panels (GNSS mast passes through the first gap)
panel_frame_w = 30.0                # width of the aluminium frame profile
laminate_t = 6.0                    # glass / cells laminate, flush with the top of the frame
cell_cols = 6
cell_rows = 10
cell_gap = 4.0
panel_wp = 320.0                    # Wp per panel (about 195 W/m2), estimated
panel_mass = 17.0                   # kg per panel, estimated
junction_box = (110.0, 70.0, 20.0)  # on the underside, x y z
bolt_d = 8.0                        # M8 bolts through the panel frame into the cross members
bolt_head_af8 = 13.0
bolt_head_k8 = 5.3

# MPPT charge controller on the rear long tube
mppt = (220.0, 140.0, 70.0)         # x y z
mppt_y = -350.0
mppt_plate_t = 6.0
mppt_mass = 1.5                     # estimated, incl. fuse and cable gland

# GNSS antenna, moved from the robot to the roof
gnss_dome_d = 150.0
gnss_dome_h = 55.0
gnss_stem_d = 30.0
gnss_stem_h = 25.0
gnss_mast_d = 25.0
gnss_mast_h = 110.0                 # above the cross member top
gnss_mast_y = 350.0                 # on the front cross member
gnss_mass = 0.3                     # kg, estimated, incl. mast

# ---------------------------------------------------------------------
# Assumptions for sol_calc.py (all estimated)
# ---------------------------------------------------------------------
frame_density = 7850.0              # kg/m3
robot_mass = 150.0                  # kg, estimated (not measured)
robot_cg_z = 450.0                  # mm, estimated height of the robot centre of gravity
extra_cg_z = 0.0                    # mass of other implements ignored
batt_voltage = 59.2                 # 16S (as in the hybrid)
batt_ah = 40.0
batt_usable = 0.8
light_task_w = 900.0                # W, driving with a light implement
heavy_task_w = 2200.0               # W, all hub motors continuous
system_derate = 0.75                # MPPT, cables, temperature, dirt, flat mounting, shade of mast / implements
# kWh per kWp per day at The Netherlands, flat panel (estimated), per month Jan..Dec
psh_month = (0.7, 1.4, 2.5, 3.8, 4.6, 4.8, 4.7, 4.0, 3.0, 1.8, 0.9, 0.5)
work_h_day = 8.0                    # h/day the robot works at the light task
wind_v = 20.0                       # m/s design gust
air_rho = 1.225
wind_cn_up = 1.0                    # normal force coefficient on the flat panel roof (uplift, conservative)
wind_cn_side = 0.3                  # side force on the roof edge-on (gust with attack angle)
steel_yield = 235.0                 # MPa, S235
steel_E = 210000.0                  # MPa
