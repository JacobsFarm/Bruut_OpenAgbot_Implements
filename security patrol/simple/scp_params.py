import os
import sys

# =====================================================================
# Security patrol (simple) - parameters
# A camera mast on the Bruut OpenAgbot (standard robot) that patrols the farmyard, the sheds and the field edges at
# night. On top of a 2 m mast a pan/tilt head carries a 4 MP 30x zoom day/night camera, a 640 x 512 thermal camera
# and an 850 nm IR illuminator. Lower on the mast 4 fixed wide-angle cameras look out to all sides for motion, so the
# robot sees all round while the pan/tilt head looks at one thing. Two horn speakers (the horn of the speech speaker,
# imported) warn intruders, an amber beacon shows that the robot is on duty, a microphone listens. An IP65 box on the
# back of the mast holds the video recorder, the LTE router and the PoE switch.
# The robot drives a set route, stops at viewpoints for a 360 degree thermal sweep and alerts the farmer by phone
# with a clip when the thermal camera sees a person or a vehicle where none should be (or an animal out of its pen).
#
# The mast stands on a 10 mm base plate across the 4 upper beams at y -300 (2 M10 in each beam, y -325 and -275), behind the robot
# centre so that it stays far from the steering stacks and the GNSS antenna (y 575).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "speaker", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import spk_params as S          # noqa: E402  (horn speaker)

# ---------------------------------------------------------------------
# Robot interface
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_steer_deg = 30.0
robot_mass = 160.0
robot_cg = (0.0, 95.0, 543.0)
upper_beam_top = 699.0
bolt_x = (-425.0, -325.0, 325.0, 425.0)    # centre lines of the 4 upper beams
hole_y = (-325.0, -275.0)                   # vertical M10 grid holes in the upper beams (|y| 275..625 step 50)

# ---------------------------------------------------------------------
# Base plate 8 mm across the 4 upper beams, mast 60 x 60 x 3 welded on, 4 gussets
# ---------------------------------------------------------------------
plate_x = (-450.0, 450.0)
plate_y = (-360.0, -240.0)
plate_t = 8.0
mast_xy = (0.0, -300.0)
mast_w = 60.0
mast_wall = 3.0
mast_top = 2000.0
gusset_t = 8.0
gusset_h = 220.0
gusset_reach_x = 260.0          # from the mast centre along x (onto the outer beams' plate)
gusset_reach_y = 58.0           # from the mast centre along y (to the plate edge)
top_flange = (140.0, 8.0)       # square, thickness

# ---------------------------------------------------------------------
# Pan/tilt head on the top flange
# ---------------------------------------------------------------------
pan_base_d = 140.0
pan_base_h = 70.0
yoke_w = 250.0                  # outer width (x) of the U-yoke
yoke_d = 80.0                   # depth (y) of the yoke
yoke_t = 8.0
tilt_z = 2230.0                 # tilt axis height
tilt_axle_d = 20.0
cam_vis = (90.0, 170.0, 90.0)   # day/night 30x zoom camera body x, y, z (left of the axis, x -)
cam_vis_lens = (70.0, 30.0)     # lens hood d, length
cam_ir = (90.0, 130.0, 80.0)    # thermal camera body (right, x +)
cam_ir_lens = (50.0, 30.0)
cam_gap = 10.0                  # each camera from the centre plane
illum = (180.0, 50.0, 40.0)     # IR illuminator on top of the cameras (x, y, z)
PAN_POSES = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0)
TILT_POSES = (-30.0, 0.0, 30.0)  # negative = looking down

# 4 fixed wide-angle cameras on the mast faces
ring_z = 1700.0
fixed_cam = (60.0, 60.0, 50.0)  # along the face normal, across, height
fixed_lens = (30.0, 12.0)

# Horns (spk) on the mast faces front and rear, axis at horn_z
horn_z = 1350.0

# Beacon on a bracket behind the mast, microphone on the right face
beacon_bracket = (60.0, 110.0, 6.0)      # x, y (out from the mast face), t
beacon_z = 1820.0                        # bracket top
beacon = (110.0, 130.0)                  # d, h
mic = (20.0, 50.0)
mic_z = 1550.0

# Electronics box on the back of the mast (video recorder, LTE router, PoE switch), 2 LTE antennas on top
box = (300.0, 150.0, 260.0)              # x, y (out from the mast face), z
box_z = 950.0
antenna = (16.0, 230.0)

# ---------------------------------------------------------------------
# Work (scp_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
rho_air = 1.2
# thermal camera: 640 x 512, 12 um pitch, 25 mm lens
ir_px = (640, 512)
ir_pitch_um = 12.0
ir_f_mm = 25.0
# day/night camera: 2560 px across, 1/2.8" sensor (5.1 mm wide), 4.8-144 mm (30x)
vis_px = 2560
vis_sensor_mm = 5.1
vis_f_mm = (4.8, 144.0)
# fixed cameras: 1920 px, 100 degree horizontal
fix_px = 1920
fix_hfov = 100.0
# Johnson criteria (cycles over the critical dimension; 1 cycle = 2 px)
JOHNSON = {"detect": 1.0, "recognise": 4.0, "identify": 8.0}
TARGETS = {"person": 0.75, "cow": 1.5, "car": 2.3}       # m critical dimension
DORI_PX_M = {"detect": 25.0, "observe": 63.0, "recognise": 125.0, "identify": 250.0}   # EN 62676-4
ir_range_m = 60.0               # IR illuminator reach (datasheet class, estimated)
# sweep
sweep_overlap = 0.1
settle_s = 0.6                  # pan move + settle per frame
# patrol
speed = 0.8                     # m/s on the route at night
route_m = 2000.0
stop_every_m = 80.0             # viewpoint with a thermal sweep
crr = 0.06
eta_drive = 0.75
battery_wh = 1900.0
p_sensors = {"ptz_cam": 12.0, "thermal": 5.0, "fixed_cams": 16.0, "recorder_lte_poe": 18.0, "ir": 20.0,
             "beacon": 3.0, "pan_tilt": 10.0, "speaker_idle": 2.0}
night_h = 10.0
# wind on the mast
wind_ms = 20.0
cd = 1.2
mast_yield = 235.0              # N/mm2 S235
# from build_scp.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 38.4, "cg": (1.0, -314.0, 1356.0)}
