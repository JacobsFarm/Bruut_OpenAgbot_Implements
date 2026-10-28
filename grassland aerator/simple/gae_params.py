import math

# =====================================================================
# Grassland aerator (simple) - parameters
# Slitter aerator in the middle of the Bruut OpenAgbot (standard robot), between the axles, so the robot weight and a
# ballast stack press the knives in and both axles share the reaction. A passive roller with 8 star discs (6 slitting
# knives each, O450) cuts slits 150 mm apart, 70 mm deep, in grassland. The roller turns in 2 flange bearings in two
# side arms that pivot on hangers from a front bridge; a cross beam behind the roller carries 4 ballast blocks; a
# 24 V actuator from a mast on the rear bridge lifts the roller (retracts) and can add down force (pushes).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_upper_beam_x = (325.0, 425.0)     # centres of the upper beams per side, along y (40 wide)
robot_upper_beam_z = (659.0, 699.0)
robot_steer_deg = 30.0
robot_mass = 160.0              # kg, estimated
robot_cg_y = 0.0                # estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Bridges: 2 x tube 60 x 60 x 4 across, on top of the upper beams, 4 x M10 each (x +-325, +-425), out to x +-680
# Front bridge clear of the steered front tyres (y > 289), rear bridge clear of the rear wheel-unit bolts (y -425)
# ---------------------------------------------------------------------
bridge = 60.0
bridge_wall = 4.0
bridge_x = (-680.0, 680.0)
bridge_front_y = (230.0, 290.0)
bridge_rear_y = (-370.0, -310.0)
bridge_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bridge)

# Hangers: plate 10 mm at each end of the front bridge, down to the arm pivot (outside the steering sweep, x > 525)
hanger_x = (625.0, 635.0)
pivot = (420.0, 300.0)          # (y, z) arm pivot, pin O25
pivot_d = 25.0
hanger_pts = ((230.0, 699.0), (290.0, 699.0), (455.0, 335.0), (455.0, 265.0), (385.0, 265.0), (230.0, 560.0))

# Actuator mast: 2 plates 8 mm on top of the rear bridge, reaching forward to the base clevis at the top
act_base = (-260.0, 1050.0)     # (y, z) base pin, in front of the rear bridge
mast_plate_x = 34.0             # inner face of the mast plates (x +-34 .. +-42)

# ---------------------------------------------------------------------
# Roller frame (turns about the pivot): 2 side arms 10 mm, cross beam 80 x 80 x 4, ballast tray
# ---------------------------------------------------------------------
arm_x = (612.0, 622.0)
axle = (0.0, 155.0)             # (y, z) roller axle in work (knife tips 70 mm deep)
arm_pts = ((452.0, 332.0), (452.0, 268.0), (40.0, 85.0), (-40.0, 85.0), (-245.0, 385.0), (-245.0, 475.0),
           (-155.0, 475.0), (388.0, 335.0))
cross_y = (-240.0, -160.0)
cross_z = (390.0, 470.0)
cross_wall = 4.0
tray_y = (-275.0, -125.0)
tray_x = 240.0
tray_t = 8.0
rod_pin = (-260.0, 500.0)       # (y, z) actuator rod pin on 2 lugs behind the cross beam, work pose

# Ballast: the 20 kg blocks of the disc brushes / fertilizer spreader (160 x 150 x 106), 2 stacks of 2,
# between the inner upper beams (x < 305) so they can rise between them
ballast_x = (60.0, 220.0)
ballast_h = 106.0
ballast_n = 2                   # blocks per stack
ballast_kg = 20.0

# ---------------------------------------------------------------------
# Roller: hex shaft O40 (drawn round), 8 star discs, 2 flange bearings UCFL208
# ---------------------------------------------------------------------
shaft_d = 40.0
shaft_x = 650.0
disc_n = 8
disc_pitch = 150.0              # slit spacing across
hub_d = 230.0
hub_t = 8.0
knife_n = 6
knife_t = 6.0
knife_r = (110.0, 225.0)        # from the hub out to the tip (O450)
knife_w = (60.0, 16.0)          # width at the root and at the tip
work_depth = 70.0
bearing_flange = (16.0, 64.0, 130.0)   # x thickness, y, z of the 2-bolt flange
bearing_body = (90.0, 34.0)            # O, length inward

# ---------------------------------------------------------------------
# Actuator: 24 V 2000 N, stroke 200 (retracted 390 pin to pin); retracts to lift, pushes (extends) to press down
# ---------------------------------------------------------------------
act_body_d = 60.0
act_rod_d = 20.0
act_retracted = 390.0
act_stroke = 200.0
act_force = 2000.0
act_kg = 3.6
act_speed = 15.0                # mm/s at 1300 N (2000 N, 24 V type with 15..20 mm/s)

lift_work = 0.0
lift_transport = 14.0           # degrees, + = roller up
LIFT_POSES = (-3.0, 0.0, 7.0, 14.0)    # -3: hollow in the sward

# ---------------------------------------------------------------------
# Work (gae_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
speed = 1.2                     # m/s (4.3 km/h)
knife_force = 160.0             # N to push one slitting knife (6 mm) 70 mm into moist grassland (estimated)
c_roll = 0.12                   # pull of the knife roller / its vertical load (estimated)
mu_tyre_grass = 0.45
crr_grass = 0.06
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
eta_drive = 0.75
grip_margin_min = 1.3           # the actuator may only push so far that the wheels keep this pull margin
# from build_gae.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 30.4, "mount_cg_y": 23.0, "lift_kg": 166.8, "lift_cg_y": -107.0, "lift_cg_z": 409.0,
              "ballast_kg": 80.0}


def rotate_yz(p, deg, c=pivot):
    """Point (y, z) turned about c by deg (+ = lifts a point behind the pivot)."""
    a = math.radians(-deg)
    dy, dz = p[0] - c[0], p[1] - c[1]
    return (c[0] + dy * math.cos(a) - dz * math.sin(a), c[1] + dy * math.sin(a) + dz * math.cos(a))


def act_length(lift_deg):
    r = rotate_yz(rod_pin, lift_deg)
    return math.hypot(r[0] - act_base[0], r[1] - act_base[1])


def disc_x():
    return [-(disc_n - 1) * disc_pitch / 2.0 + i * disc_pitch for i in range(disc_n)]


def knives_in_ground():
    """Average number of knives per disc below the ground line at the working depth."""
    r = knife_r[1]
    half = math.acos((r - work_depth) / r)
    return 2.0 * half / (2.0 * math.pi / knife_n)
