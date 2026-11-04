import math
import os
import sys

# =====================================================================
# Sports field line marker (simple) - parameters
# Paints the lines of a sports field (football, hockey) from a stored layout. One paint nozzle in a shroud hangs under
# the belly of the Bruut OpenAgbot on the REAR AXLE LINE (x 0, y -500): with front-wheel steering the middle of the
# rear axle is the point that follows the path without side slip, so a curve the robot steers is the curve the nozzle
# paints (no offset tracking). The nozzle sits on the carriage of a short belt module across the robot (stroke 340,
# x -170 .. +170): it corrects the cross-track error at the nozzle in real time and draws arcs that are tighter than
# the robot can steer (corner arcs r 1 m) while the robot drives straight along the chord.
# Tank (120 l, filled with ~40 l ready-mixed line paint), pump, filter, regulator (bypass = agitation in the tank) and
# the control box are the spot sprayer's ("spotspray unit/boom"); the belly rails are the drop-on-demand boom's
# ("drop on demand boom/simple"); both imported, not copied.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DDB_FOLDER = os.path.join(ROOT_DIR, "drop on demand boom", "simple")
SSP_FOLDER = os.path.join(ROOT_DIR, "spotspray unit", "boom")
for _f in (DDB_FOLDER, SSP_FOLDER):
    if _f not in sys.path:
        sys.path.append(_f)
import ddb_params as D          # noqa: E402  (belly rails)
import ssp_params as S          # noqa: E402  (tank, cradle, pump, regulator, control box)

# ---------------------------------------------------------------------
# Robot interface (from the spot sprayer, which took it from agbot_params.py)
# ---------------------------------------------------------------------
robot_wheel_x = S.robot_wheel_x
robot_axle_y = S.robot_axle_y               # 500: rear axle at y -500
robot_axle_z = S.robot_axle_z
robot_tire_d = S.robot_tire_d
robot_tire_w = S.robot_tire_w
robot_lower_beam_y = S.robot_lower_beam_y
robot_lower_beam_z = S.robot_lower_beam_z
robot_bracket_x = S.robot_bracket_x
robot_steer_max = S.robot_steer_max
robot_wheelbase = S.robot_wheelbase         # 1000
robot_track = S.robot_track                 # 750
robot_gnss = (0.0, 575.0, 740.0)            # top of the robot's antenna (front cross beam)
robot_kg = S.robot_kg
m10_hole = S.m10_hole

# ---------------------------------------------------------------------
# Belly rails of the drop-on-demand boom (x +-225, z 579 .. 619), unchanged
# ---------------------------------------------------------------------
rail_x = D.rail_x
rail = D.rail
rail_z = D.rail_z

# ---------------------------------------------------------------------
# Hanger posts: square tube 30 x 30 x 2 under the rails at the rear axle line, foot plate 8 mm with 2 x M8 into
# rivet nuts in the rail (as the boom's posts), bottom plate 8 mm bolted on top of the belt module (4 x M6 T-nuts).
# The spot-sprayer pump, filter and regulator hang under the sub plate down to z 480 between x -130 and +110: the
# module stays under them (top z 470) and the posts stay outside them (x +-225).
# ---------------------------------------------------------------------
nozzle_y = -robot_axle_y                    # -500: the nozzle line = rear axle line
post = 30.0
post_wall = 2.0
post_x = rail_x
post_foot = (60.0, 70.0, 8.0)
post_plate = (70.0, 60.0, 8.0)              # bottom plate x, y, t (on the module top)

# ---------------------------------------------------------------------
# Belt linear module (bought, e.g. a 60-series belt actuator): aluminium body 60 (y) x 45 (z), carriage UNDER the body
# (module hung upside down), NEMA 23 closed-loop on the -x end. Stroke 340: nozzle x -170 .. +170.
# ---------------------------------------------------------------------
stroke = 340.0
mod_w = 60.0                                # body y
mod_h = 45.0                                # body z
mod_top = 470.0                             # body top (under the bottom plates of the posts)
mod_z = (mod_top - mod_h, mod_top)          # 425 .. 470
car_len = 70.0                              # carriage x
car_t = 12.0
car_w = 70.0                                # carriage y
car_gap = 1.0
car_z = (mod_z[0] - car_gap - car_t, mod_z[0] - car_gap)     # 412 .. 424
mod_end = (25.0, 25.0)               # drive end (-x, fold-back belt box in front of it), idler end (+x): inside the wheel brackets (x 261)
mod_x = (-stroke / 2.0 - car_len / 2.0 - mod_end[0], stroke / 2.0 + car_len / 2.0 + mod_end[1])   # -230 .. 230
pulley_pd = 31.83                           # HTD-5M 20 teeth: 100 mm per turn
mod_kg_per_m = 4.2
car_kg = 0.5
nema = 57.0
nema_len = 102.0
nema_kg = 1.4
nema_torque_run = 1.0                       # Nm usable at 600 rpm (estimated)
coupler_len = 35.0
mod_speed = 300.0                           # mm/s used for the corner arcs (max of the module ~1000)
mod_acc = 2000.0                            # mm/s2

# ---------------------------------------------------------------------
# Paint head (own sub-Part, moves in x with the carriage): carriage plate 6 mm, a stem tube 25 x 25 x 2 down to the
# shroud top, a 12 V solenoid valve with the nozzle body under it, an even flat-fan tip (fan across, line along y),
# and the shroud: aluminium 1.5 mm box, open at the bottom, with a brush skirt. Nozzle height in 3 clamp holes sets
# the line width.
# ---------------------------------------------------------------------
head_plate = (70.0, 90.0, 6.0)              # x, y, t under the carriage
stem = 25.0
stem_wall = 2.0
shroud_x = 75.0                             # half width (across: 120 line + margins); at x +-170 the brush stays inside the wheel brackets (x 261)
shroud_y = (-150.0, 150.0)                  # relative to nozzle_y: long in the driving direction
shroud_h = 150.0
shroud_t = 1.5
shroud_bottom = 50.0                        # skirt edge over the ground (turf mown at ~25 mm)
brush_h = 30.0                              # brush skirt (tips 20 mm over the ground)
brush_t = 6.0
valve_body = (40.0, 40.0, 55.0)             # x, y, z solenoid valve 12 V, 3/8" (on the shroud top)
nozzle_body = (22.0, 50.0)                  # d, length (body + cap) under the valve, inside the shroud
tip_z = 140.0                               # nozzle orifice over the ground (middle hole)
tip_steps = (103.0, 140.0, 165.0)           # 75 mm hockey / 100 mm / 120 mm football lines
fan_angle = 40.0                            # degrees, even flat fan (E tip): constant rate over the whole width
chain = (15.0, 20.0)                        # drag chain inner: 15 (y) x 20 (z) outer section in the model
chain_r = 25.0                              # bend radius (centre line)
chain_y = (-580.0, -560.0)                  # behind the module (y)
chain_tray_z = 405.0                        # tray top; lower run lies on it
chain_fix_x = 0.0
chain_free = 190.0                          # chain length minus pi*r: bend from x 10 (carriage -170) to x 180 (+170)

# ---------------------------------------------------------------------
# Paint, nozzle, pump (for lmk_calc)
# ---------------------------------------------------------------------
tip_q40 = 0.76                              # l/min of a 4002E tip at 2.76 bar (40 psi), datasheet class
tip_p_ref = 2.76
spray_p = 3.0                               # bar (regulator of the spot sprayer)
paint_density = 1.3                         # kg/l ready-mixed line paint (estimated)
paint_fill_l = 40.0                         # usual fill: ~3 football fields
paint_dilution = 2.0                        # concentrate : water = 1 : 1 -> 2 l ready mix per l concentrate
speed_paint = 1.0                           # m/s painting a straight line
speed_curve = 0.6                           # m/s on the centre circle / penalty arcs
speed_transit = 1.5                         # m/s between lines (nozzle off)
turn_s = 8.0                                # s per line end: stop, turn, line up (estimated)
valve_ms = (25.0, 15.0)                     # opening / closing delay of the solenoid valve (estimated)
valve_jitter_ms = 3.0
line_w = {"football": 100.0, "football_max": 120.0, "hockey": 75.0}

# GNSS / attitude error budget (1 sigma, estimated from datasheet classes)
rtk_h = 8.0                                 # mm horizontal RTK (short baseline)
heading_err = 0.15                          # degrees heading (dual antenna or from the track)
tilt_err = 0.2                              # degrees residual roll/pitch after IMU correction
slide_err = 1.0                             # mm belt module position error
odo_lag_ms = 20.0                           # control loop lag cross-track -> slide (estimated)

# ---------------------------------------------------------------------
# Field layouts (m)
# ---------------------------------------------------------------------
FOOTBALL = {"length": 105.0, "width": 68.0, "centre_r": 9.15, "pen_depth": 16.5, "pen_width": 40.32,
            "goal_depth": 5.5, "goal_width": 18.32, "pen_spot": 11.0, "arc_r": 9.15, "corner_r": 1.0}
HOCKEY = {"length": 91.4, "width": 55.0, "circle_r": 14.63, "goal_w": 3.66, "line_23": 22.9}

# ---------------------------------------------------------------------
# Energy, mass
# ---------------------------------------------------------------------
battery_wh = 1900.0
drive_w = 250.0                             # W driving on turf at 1 m/s (estimated)
computer_w = 30.0
pump_w = S.pump_w                           # 110 W at 3 bar
slide_w = 25.0                              # W average of the belt module (estimated)
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
nylon = 0.35e-6

# from build_lmk.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 61.9, "cg": (-5.0, -266.0, 677.0), "slide_kg": 3.8, "head_kg": 2.2}


def tip_flow(p=None):
    """l/min of the tip at pressure p (bar): Q ~ sqrt(p)."""
    p = spray_p if p is None else p
    return tip_q40 * math.sqrt(p / tip_p_ref)


def line_width(h=None):
    """Width (mm) of the fan on the ground for a tip height h (mm)."""
    h = tip_z if h is None else h
    return 2.0 * h * math.tan(math.radians(fan_angle / 2.0))
