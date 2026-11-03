import os
import sys

# =====================================================================
# Fence inspector (simple) - parameters
# Electric-fence inspector for the Bruut OpenAgbot (standard robot). The robot drives along the fence with the fence
# line 1.0 m to the right of its centre. A sensor head at the end of a side arm holds a capacitive E-field plate and a
# pickup coil 80 mm from the live wire, without touching it: the plate gives the voltage of every energizer pulse, the
# coil the pulse current (direction and size). One reading per pulse (~1 per metre at 1 m/s) is logged with the GNSS
# position: breaks (no voltage beyond a point), shorts and leaks (current that disappears into vegetation or a post)
# and voltage drops end up on a map. A camera on top of the mast photographs every post (lean, broken insulator).
# The arm rides on a carriage on a vertical mast (lead screw + stepper) so any wire between 300 and 1100 mm can be
# followed; the arm swings back on a spring hinge when it touches a post or a branch.
# Post straightening is not in the simple variant (the photo gives the lean angle for a work list).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

PBL_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "push blade", "simple")
if PBL_FOLDER not in sys.path:
    sys.path.append(PBL_FOLDER)

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
robot_cg_y = 0.0
robot_gnss = (0.0, 575.0)
upper_beam_x = ((305.0, 345.0), (405.0, 445.0))   # right inner and outer upper beams, z 659..699
upper_beam_top = 699.0
hole_y = 300.0                  # vertical M10 grid holes at |y| 275..625

# ---------------------------------------------------------------------
# Base plate 8 mm on the 2 right upper beams (4 x M10 at y +-300) and the mast 60 x 60 x 3 at its outer edge
# ---------------------------------------------------------------------
plate_x = (300.0, 525.0)
plate_y = (-330.0, 330.0)
plate_t = 8.0
mast_xy = (485.0, 0.0)          # mast centre
mast_w = 60.0
mast_wall = 3.0
mast_z = (200.0, 1400.0)
gusset_t = 8.0

# Lead screw Tr16 x 4 behind the mast (y -), bearing blocks top and bottom, NEMA 23 stepper on top
screw_d = 16.0
screw_y = -62.0                 # screw axis (x = mast x)
screw_z = (225.0, 1370.0)
stepper = (57.0, 57.0, 76.0)

# Carriage: PE-lined steel sleeve 80 x 80 x 4, 120 high, with a nut block on the screw and a hinge lug outside
sleeve_w = 80.0
sleeve_t = 4.0
sleeve_h = 120.0
hinge_xy = (545.0, 0.0)         # vertical hinge axis of the arm
hinge_d = 16.0

# Arm: tube 40 x 40 x 3 from the hinge to the sensor head; spring hinge (torsion spring) swings back up to 80 degrees
arm_w = 40.0
arm_x1 = 860.0
swing_max = 80.0

# Sensor head: ABS box 60 (x) x 220 (y) x 140 (z), face 80 mm from the wire; PE bumper nose in front (deflects posts)
head_x = (arm_x1, arm_x1 + 60.0)
head_y = 220.0
head_z = 140.0
plate_area = 50.0 * 50.0        # mm2 capacitive E-field plate behind the face
coil_turns = 500
coil_area = 100.0               # mm2
lidar_box = (30.0, 40.0, 30.0)  # small ToF distance sensor in the head, to the wire

# Camera on the mast top, looking right and a little forward at the posts
cam_box = (70.0, 90.0, 60.0)

# Wire heights (render and poses)
wire_x = 1000.0                 # fence line (wires) at x 1000; posts behind the wires at x 1100
WIRE_Z = (400.0, 700.0, 1000.0)
wire_z = 1000.0                 # followed wire in the work pose (top wire, usually the live one)
Z_RANGE = (300.0, 1100.0)       # wire heights the head can follow
post_d = 100.0
post_x = 1100.0
post_step = 4000.0

# ---------------------------------------------------------------------
# Work (fin_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
abs_ = 1.05e-6
pe = 0.95e-6
eps0 = 8.854e-12
mu0 = 4e-7 * 3.141592653589793
fence_kV = 6.0                  # typical pulse voltage on a good fence
fault_kV = 3.0                  # below this the fence does not hold cattle (estimated, common advice 3-4 kV)
wire_r = 1.25                   # mm, 2.5 mm high-tensile wire
probe_d = 80.0                  # mm sensor face to wire
probe_d_err = 4.0               # mm error of the ToF distance (estimated)
neighbour_share = 0.08          # field share of the other wires at the probe after the plate's directivity (est.)
c_integr = 1e-9                 # F integrating capacitor of the E-field plate
pulse_current = (1.0, 15.0)     # A, range of pulse currents (good fence .. heavy short)
pulse_s = 100e-6                # s, rise time of the pulse used for the pickup coil
pulse_hz = 1.0                  # energizer pulses per second
speed = 1.0                     # m/s along the fence
p_sensors = 20.0                # W: head, camera, logger
crr = 0.06
eta_drive = 0.75
battery_wh = 1900.0
screw_lead = 4.0                # mm per rev
stepper_rpm = 600.0
spring_N = 15.0                 # N at the head to swing the arm back (estimated torsion spring)
# from build_fin.mass_properties() in the work pose (update after a change of the model)
MODEL_MASS = {"kg": 22.7, "cg_x": 485.0, "cg_y": -9.0}
