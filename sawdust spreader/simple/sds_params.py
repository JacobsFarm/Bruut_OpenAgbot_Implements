import math

# =====================================================================
# Sawdust spreader (simple) - parameters
# Bedding spreader for the Bruut OpenAgbot (standard robot) in loose housing: a bin on the upper beams with sloping
# front and rear walls down to a trough with an auger across the robot; the auger feeds a spinner disc in a housing on
# the right side that throws sawdust (or fine chopped straw, lime-sawdust mix) sideways into the cubicles while the
# robot drives along the feed or dung alley. Dose per cubicle from the auger speed and the driving speed.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_outer_beam_x = 445.0      # outer face of the outer upper beams
robot_front_stack_y = 405.0     # steering plates and motors from here (to z 1032)
robot_mass = 160.0
robot_cg_z = 380.0
robot_steer_deg = 30.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Bearers: 2 x tube 40 x 40 x 3 across the upper beams, clear of the trough
# ---------------------------------------------------------------------
bearer = 40.0
bearer_y = (-330.0, 250.0)
bearer_x = 440.0
bearer_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bearer)

# ---------------------------------------------------------------------
# Bin: side walls at x +-400, front and rear walls at 45 degrees down to a U-trough round the auger, 2 mm steel;
# 4 legs (angle 40 x 4) from the bearers to the slopes
# ---------------------------------------------------------------------
bin_x = 400.0
trough_y = -40.0                # auger axis y
auger_z = 805.0                 # auger axis z
trough_r = 85.0                 # trough radius (auger O150 + 10 clearance)
slope_deg = 45.0
bin_front_y = 380.0             # 25 mm short of the front steering stacks
bin_rear_y = -460.0
bin_top = 1350.0
wall_t = 2.0
leg = (40.0, 4.0)

# ---------------------------------------------------------------------
# Auger: flight O150 pitch 150 on a shaft O30, across the robot, from the left gearmotor to the spinner housing
# ---------------------------------------------------------------------
auger_d = 150.0
auger_pitch = 150.0
auger_shaft = 30.0
auger_flight_t = 3.0
auger_x = (-395.0, 560.0)
gm_box = (110.0, 110.0, 110.0)  # 24 V 200 W worm gearmotor, left end
gm_motor = (80.0, 140.0)
outlet_tube = (170.0, 2.0)      # tube O170 round the auger from the bin wall to the housing (over the right beams)

# ---------------------------------------------------------------------
# Spinner: housing on the right side, outside the outer upper beam; disc O320 with 4 vanes, vertical axis, 24 V
# motor on the housing roof; opening to the right (+x) and down
# ---------------------------------------------------------------------
housing_x = (455.0, 795.0)
housing_y = (trough_y - 180.0, trough_y + 180.0)
housing_z = (640.0, 940.0)
disc_d = 320.0
disc_z = 660.0
vane_h = 40.0
spinner_motor = (90.0, 120.0)
spinner_x = 625.0               # disc axis x

# ---------------------------------------------------------------------
# Work (sds_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
MATERIAL = {"sawdust": 200.0, "chopped_straw": 70.0, "lime_sawdust_mix": 450.0}   # kg/m3 loose (estimated)
auger_fill = 0.45               # filling of the auger at low speed (estimated)
auger_rpm_max = 120.0
dose_kg = {"sawdust": 1.0, "chopped_straw": 0.4, "lime_sawdust_mix": 1.5}       # per cubicle per day (estimated)
cubicle_w = 1.2                 # m per cubicle along the alley
speed = 0.5                     # m/s along the cubicles
payload_max = 150.0             # kg on the top of the robot (estimated, as the crate carrier)
spinner_rpm = 350.0
throw_eff = 0.5                 # throw distance / ideal flight from the disc tip speed (air drag on sawdust), estimated
refill_s = 180.0                # refill from a big bag over the bin (estimated)
travel_m = 60.0                 # average drive to the refill point and back
p_auger = 120.0                 # W at load (estimated)
p_spinner = 150.0
crr = 0.03                      # concrete floor
eta_drive = 0.75
battery_wh = 1900.0
# from build_sds.mass_properties() (update after a change of the model)
MODEL_MASS = {"spreader_kg": 74.8, "spreader_cg": (81, -40, 907)}


def bin_section():
    """Polygon (y, z) of the bin inside, in the y-z plane (the trough approximated by its tangent lines)."""
    a = math.radians(slope_deg)
    r = trough_r
    # tangent points of the slopes on the trough circle
    yf, zf = trough_y + r * math.sin(a), auger_z - r * math.cos(a)
    yr, zr = trough_y - r * math.sin(a), zf
    zf_top = zf + (bin_front_y - yf) * math.tan(a)
    zr_top = zr + (yr - bin_rear_y) * math.tan(a)
    return [(yr, zr), (yf, zf), (bin_front_y, zf_top), (bin_front_y, bin_top), (bin_rear_y, bin_top),
            (bin_rear_y, zr_top)]


def bin_volume():
    """Inside volume (m3) of the bin above the trough tangent line plus the trough half circle."""
    pts = bin_section()
    a = 0.0
    for i in range(len(pts)):
        y0, z0 = pts[i]
        y1, z1 = pts[(i + 1) % len(pts)]
        a += y0 * z1 - y1 * z0
    area = abs(a) / 2.0 + math.pi * trough_r ** 2 / 2.0 * 0.6
    return area * 2 * bin_x * 1e-9
