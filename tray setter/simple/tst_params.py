import math

# =====================================================================
# Tray setter (simple) - parameters
# Transplanter for the Bruut OpenAgbot (standard robot): takes plug seedlings out of 2 plug trays on a table on top of
# the robot and sets them out in 2 rows (x +-150, e.g. lettuce on a bed) at the planting distance.
#   - tray table: aluminium plate on 2 cross tubes on the inner upper beams; 2 plug trays of 128 cells (8 x 16)
#   - gantry: 2 Y rails along the table edges (x +-360), an X beam on 2 Y carriages, a picker carriage on the X beam
#     with a Z actuator and a 4-needle gripper (needles go into the plug, the stripper plate pushes it off)
#   - 2 funnels in the table in front of the trays, drop tubes O50 straight down to 2 planting shoes under the belly
#   - per row: a runner shoe (opens a slot 60 mm deep, the plug drops through its boot) and 2 press wheels O250 at
#     +-15 degrees that close the slot; hung from a cross beam under the belly rails (as on the drop-on-demand boom)
# The robot drives slowly (0.048 m/s); a plant is dropped when the shoe is at the next planting point (odometry / RTK).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Tray table on 2 cross tubes 40 x 40 x 3 (M10 into the inner upper beams at y -375 and 275)
# ---------------------------------------------------------------------
cradle_y = (-375.0, 275.0)
cradle_half = 380.0
cradle_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + 40.0)       # 699 .. 739
table = ((-385.0, 385.0), (-590.0, 300.0), 4.0)
table_z = (cradle_z[1], cradle_z[1] + table[2])                        # 739 .. 743

# Plug trays: 128 cells (8 across x, 16 along y), 280 x 540 x 50, side by side
tray = (280.0, 540.0, 50.0)
tray_cells = (8, 16)
tray_x = (-145.0, 145.0)        # tray centres
tray_y = -300.0                 # tray centre (both)
tray_stops = 6.0                # angle stops round the trays
plug = (25.0, 45.0)             # plug d (top), length
seedling_h = 90.0               # leaves above the plug (4 true leaves, estimated)

# Funnels in the table, one per row, in front of the trays
row_x = (-150.0, 150.0)
funnel_y = 60.0
funnel_d = (110.0, 52.0)        # top, bottom
funnel_h = 70.0
tube_d = (50.0, 44.0)           # drop tube, outside / inside (PE)

# ---------------------------------------------------------------------
# Gantry: Y rails (aluminium profile 40 x 40 with a linear guide), X beam 60 x 40, picker carriage, belt drives
# ---------------------------------------------------------------------
y_rail_x = 360.0                # outside the cradle bolt heads (x +-325)
y_rail = (40.0, 40.0)           # profile w, h
y_rail_y = (-590.0, 300.0)
gantry_z = 1000.0               # bottom of the X beam
y_post_h = gantry_z - table_z[1] - 60.0    # Y carriage posts from the Y carriage up to the X beam
x_beam = (60.0, 40.0)           # y, z section
x_beam_x = (-390.0, 390.0)
y_car = (70.0, 90.0, 20.0)      # Y carriage plate x, y, t
picker = (70.0, 60.0, 90.0)     # picker carriage on the X beam: x, y, z (incl. the belt clamp)
z_act = (40.0, 220.0)           # Z actuator body d, length (belt / small linear axis, 150 mm stroke)
z_stroke = 220.0
needle_head = (40.0, 40.0, 30.0)
needles = (2.0, 45.0)           # 4 needles d, length
needle_dx = 5.0                 # needles at +-5 mm: they stay inside the tapered plug
motor = (42.0, 48.0)            # NEMA17 for X and Y

# picker poses (picker axis x, y) and needle tip height
pick_depth = 30.0               # needles into the plug
carry_lift = 140.0              # plug lifted this far above its cell (plug 45 + leaves 90 + margin)
picker_dy = -60.0               # picker axis behind the X beam (so the rearmost cells are within the Y travel)

# ---------------------------------------------------------------------
# Belly: rails 40 x 40 x 3 under the lower beams at x +-225 (as on the drop-on-demand boom), a cross beam under them,
# per row a post down to the shoe and a press-wheel arm
# ---------------------------------------------------------------------
rail_x = 225.0
rail = 40.0
rail_y = (-595.0, 595.0)
rail_z = (robot_lower_beam_z[0] - rail, robot_lower_beam_z[0])     # 579 .. 619
cross_y = (150.0, -190.0)       # front (shoe posts) and rear (press wheel hangers) cross beams 40 x 40 x 3 under the rails
cross_z = (rail_z[0] - 40.0, rail_z[0])     # 539 .. 579
post = 40.0                     # shoe post 40 x 40 x 3 at (row x, cross_y[0]) down to the shoe
shoe_y = (90.0, 170.0)          # runner blade, sharp front at 170
shoe_t = 10.0
shoe_depth = 60.0               # below the ground
shoe_top = 230.0
boot = (60.0, (30.0, 90.0))     # boot behind the blade: width, y range; the plug drops through it (axis y 60)
press_y = -190.0                # press wheel axles
press_d = 250.0
press_w = 40.0
press_tilt = 15.0               # degrees, tops apart: the wheels press the slot walls together
press_dx = 55.0                 # wheel centres at row x +- press_dx
yoke_z = (290.0, 300.0)         # yoke plate over the 2 wheels of a row, hung from the rear cross beam
# ---------------------------------------------------------------------
# Work (tst_calc)
# ---------------------------------------------------------------------
spacing = 300.0                 # mm in the row (lettuce)
speed = 0.048                   # m/s: the gantry sets the pace (far cell, see tst_calc.rates)
v_xy = 800.0                    # mm/s gantry travel (GT2 belt, NEMA17)
a_xy = 4000.0                   # mm/s2
v_z = 600.0                     # mm/s
t_grip = 0.15                   # s needles in / out, stripper
t_drop = 0.4                    # s plug falls through the tube (0.55 m)
gantry_w = 40.0                 # W average (2 NEMA17 + Z + controller)
drive_w = 220.0                 # W driving at 0.1 m/s with the shoes in the soil (estimated)
draft_n_per_shoe = 120.0        # N draft of a runner shoe 60 mm deep in a seedbed (estimated)
press_n = 150.0                 # N on each pair of press wheels (spring, estimated)
battery_kwh = 2.4
field_eff = 0.70                # turns and tray changes
tray_change_s = 30.0            # a person (or a tray rack) changes 2 trays
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
pe = 0.95e-6
rubber = 1.2e-6

# from build_tst.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 67.9, "cg_y": -84.0}


def cell_xy(tray_i, i, j):
    """Centre of cell (i across x, j along y) of tray 0 (left) or 1 (right)."""
    w, ln, _ = tray
    nx, ny = tray_cells
    return (tray_x[tray_i] - w / 2.0 + (i + 0.5) * w / nx, tray_y - ln / 2.0 + (j + 0.5) * ln / ny)
