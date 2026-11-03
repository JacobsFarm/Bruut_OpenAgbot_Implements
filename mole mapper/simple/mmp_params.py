import os
import sys

# =====================================================================
# Mole and tunnel mapper (simple) - parameters
# Maps molehills and mole tunnels in grassland for the Bruut OpenAgbot (standard robot):
#  - a camera bridge in front of the robot, 1.4 m high: 3 RGB cameras and 1 thermal camera looking down cover a 2.4 m
#    strip; fresh hills (dark, moist, cooler/warmer than the sward, not on the last map) get a GNSS point;
#  - the cone penetrometer of the soil compaction meter ("soil compaction meter/simple", imported, not copied) in the
#    middle of the robot probes a ring of points around a fresh hill: a sudden drop of the cone resistance 50-250 mm
#    deep is a tunnel. The tunnel directions go on the map, for traps or for the molehill spreader.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "soil compaction meter", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import scm_params as C          # noqa: E402  (cone penetrometer)

robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_steer_deg = 30.0
robot_mass = 160.0
robot_front_beam_y = (555.0, 595.0)     # front outer lower beam, z 619..659
robot_lower_beam_z = (619.0, 659.0)
robot_gnss = (0.0, 575.0)

# ---------------------------------------------------------------------
# Camera bridge: 2 posts 40 x 40 x 3 on brackets on the front outer lower beam (x +-200, M10 at x +-175 / +-225),
# a cross bar 40 x 40 x 3 at 1.4 m from x -900 to 900, 2 diagonal stays to the posts
# ---------------------------------------------------------------------
post_x = 200.0
post_y = (600.0, 640.0)
post_w = 40.0
bracket = (90.0, 70.0, 8.0)     # base plate x, y, t on the beam (y 545..615) + a front plate down the post
bolt_x = (175.0, 225.0)
bar_z = (1400.0, 1440.0)
bar_x = 900.0
stay_x = 600.0                  # stays from the post at z stay_z0 to the bar at x +-stay_x
stay_z0 = 1100.0
cam_x = (-650.0, 0.0, 650.0)    # RGB cameras under the bar, looking down
cam_box = (60.0, 80.0, 70.0)
cam_tilt = 15.0                 # degrees forward
thermal_x = 100.0
thermal_box = (55.0, 70.0, 65.0)

# ---------------------------------------------------------------------
# Work (mmp_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
cam_hfov = 50.0                 # degrees across (x)
cam_px = 3840                   # pixels across
cam_height = bar_z[0] - cam_box[2]
thermal_hfov = 45.0
thermal_px = 640
hill_d = (250.0, 500.0)         # mm molehill diameter (estimated range)
speed = 1.5                     # m/s mapping
overlap = 200.0
# tunnel probing with the cone penetrometer
ring_r = 300.0                  # mm, points on a ring around the hill
ring_n = 16                     # 118 mm apart: a 50 mm tunnel crossing the ring twice is hit ~85 %
tunnel_depth = (50.0, 250.0)
tunnel_d = 50.0                 # mm mole tunnel diameter
probe_depth = 300.0
probe_speed = C.feed_push          # mm/s while measuring (ASABE)
fast_speed = C.feed_fast           # mm/s down to the ground and back up
tip_park = C.tip_park
move_s = 8.0                    # s to drive the robot 0.2-0.6 m to the next probe point
hills_per_ha = 120.0            # in an infested field (estimated)
probe_share = 0.25              # share of the fresh hills that is probed (one in four)
fresh_share = 0.3
crr = 0.06
eta_drive = 0.75
p_cams = 35.0                   # W: 3 RGB, thermal, computer
p_probe = 60.0                  # W average while probing
battery_wh = 1900.0
# from build_mmp.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 40.0, "cg_y": 112.0}
