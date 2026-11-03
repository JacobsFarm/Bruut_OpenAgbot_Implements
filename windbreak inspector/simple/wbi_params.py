import os
import sys

# =====================================================================
# Windbreak and tree-row inspector (simple) - parameters
# The Bruut OpenAgbot (standard robot) drives along a hedgerow, windbreak or orchard row with the row 1.5 m to its
# right and logs, per tree / per metre:
#  - the profile of the row (height, width, density, gaps) from a 2D lidar that scans a vertical plane across the row
#    (one profile every 0.15 m);
#  - photos from a stereo camera pair (side view, 0.3-2.9 m) and a camera tilted up at the crowns (dead wood, damage,
#    flowering, fruit); the stereo pair gives the distance to every trunk, so each tree gets its own GNSS point.
# The sensor head stands on the fence-inspector mast and base plate ("fence inspector/simple", imported) with an
# extension tube to 2.1 m; no carriage or arm (the head looks across, nothing reaches into the row).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "fence inspector", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import fin_params as F          # noqa: E402  (base plate and mast)

robot_steer_deg = F.robot_steer_deg
robot_mass = F.robot_mass
robot_wheel_x = F.robot_wheel_x
mast_xy = F.mast_xy
mast_w = F.mast_w
mast_top = F.mast_z[1]

# ---------------------------------------------------------------------
# Extension: tube 50 x 50 x 3 inside the top of the mast (300 mm overlap, 2 M10 through both), up to ext_top
# ---------------------------------------------------------------------
ext_w = 50.0
ext_overlap = 300.0
ext_top = 2100.0
ext_bolt_z = (mast_top - 80.0, mast_top - 220.0)

# Head: aluminium box on the extension top, facing +x
head_box = (120.0, 260.0, 420.0)        # x, y, z
head_z0 = ext_top - 340.0               # the box straddles the tube top
lidar_d = 80.0                          # 2D lidar, scan plane x-z (rotation axis along y), 270 degrees
lidar_h = 80.0
lidar_z = ext_top + 50.0                # on top of the head
stereo_z = (head_z0 + 80.0, head_z0 + 330.0)   # 2 cameras one above the other (vertical baseline 250 mm)
cam_up_deg = 35.0                       # crown camera tilt
lens_d = 40.0

# Row (render only): hedge 1.5 m right of the robot centre, trees 3-6 m tall
row_x = 1500.0
tree_step = 2500.0

# ---------------------------------------------------------------------
# Work (wbi_calc)
# ---------------------------------------------------------------------
g = 9.81
alu = 2.7e-6
steel = 7.85e-6
lidar_fov = 270.0
lidar_res_deg = 0.33
lidar_hz = 10.0
lidar_range = 25.0              # m
cam_vfov = 90.0                 # degrees, stereo cameras (portrait)
cam_px_v = 3000
crown_cam_vfov = 60.0
stereo_base = 250.0
disparity_err = 0.25            # px
row_heights = (2.0, 6.0)        # m hedges / windbreak trees
speed = 1.5                     # m/s
crr = 0.06
eta_drive = 0.75
p_sensors = 40.0                # W lidar, 3 cameras, computer
battery_wh = 1900.0
wind_ms = 15.0                  # design wind on the head (stops above)
cd_head = 1.2
# from build_wbi.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 25.9, "cg_x": 457.0, "cg_z": 1290.0}
