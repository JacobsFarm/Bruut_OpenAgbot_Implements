import os
import sys

# =====================================================================
# Hedge trimmer and leaf blower (simple) - parameters
# Trims hedges along a stored RTK line, and blows the clippings and leaves off the path into a windrow.
# On the right of the robot: the mast, lead screw, stepper, carriage and arm of the fence inspector
# ("fence inspector/simple", imported, not copied). At the arm tip: a tilt gearmotor (axis along y) carries a
# double-sided hedge trimmer bar 1000 mm (garden-tool motor and gearbox at its root). Tilt 0: the bar stands up from the
# head and cuts the side of the hedge; tilt 90: the bar lies along +x and cuts the top. The carriage sets the height.
# A ToF distance sensor on the head keeps the bar 60 mm from the hedge face (the arm swings back on its spring hinge
# when the bar meets a post).
# In front: a 48 V axial blower under the front lower beam blows forward-right and down over the path.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# =====================================================================

FIN_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "fence inspector", "simple")
if FIN_FOLDER not in sys.path:
    sys.path.append(FIN_FOLDER)
import fin_params as F          # noqa: E402

robot_steer_deg = F.robot_steer_deg
robot_mass = 161.5
ZC0 = F.wire_z                  # carriage centre z in the fence inspector's work pose (the arm axis)
z_range = (F.screw_z[0] + 80.0, F.screw_z[1] - 80.0)       # usable arm heights (carriage travel)
arm_x1 = F.arm_x1               # 860: arm tube end
hinge_xy = F.hinge_xy

# ---------------------------------------------------------------------
# Tilt head at the arm tip: worm gearmotor 24 V, output along y; the trimmer rotates about (tilt_x, 0, arm axis)
# ---------------------------------------------------------------------
tilt_box = (90.0, 110.0, 90.0)  # x, y, z body at the arm end
tilt_x = arm_x1 + 45.0          # tilt axis x
flange_y = (-60.0, -55.0)       # output flange on the -y face of the body; the trimmer hangs on it
TILT_POSES = (0.0, 45.0, 90.0)  # degrees: 0 = bar up (side cut), 90 = bar along +x (top cut)
swing_max = 45.0                # stop on the spring hinge: at 80 (fence inspector) the head would reach the rear wheel bracket

# Trimmer: root housing (motor + gearbox) on the tilt flange, bar along its own +z (up at tilt 0)
housing = (110.0, 90.0, 160.0)  # x, y, z
housing_dx = 30.0               # housing centre x from the tilt axis (outboard)
housing_y = -105.0              # housing centre y (beside the tilt body, on the flange)
bar_len = 1000.0
bar_w = 32.0                    # blade width (y)
bar_t = 10.0                    # x thickness incl. teeth
tooth_pitch = 30.0
tooth_len = 18.0
guard = (8.0, 40.0)             # finger guard strip (x, y) along the back of the bar
tof = (40.0, 30.0, 30.0)        # distance sensor on the housing, looking +x
bar_gap = 60.0                  # bar to hedge face (controller)

# ---------------------------------------------------------------------
# Leaf blower in front: axial 48 V blower O140 x 360 on a bracket under the front lower beam (x 0), nozzle to
# forward-right and 35 degrees down
# ---------------------------------------------------------------------
front_beam_y = (555.0, 595.0)   # front outer lower beam (y 575)
lower_beam_z = (619.0, 659.0)
blow_d = 140.0
blow_len = 360.0
nozzle_len = 300.0
nozzle_d = (90.0, 60.0)
blow_dir = (0.45, 0.80, -0.40)  # unit-ish direction of the blower axis
blow_start = (120.0, 640.0, 560.0)  # beside the GNSS antenna stem (x 0, y 575)
bracket = (120.0, 80.0, 8.0)

# ---------------------------------------------------------------------
# Work (for hdg_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
speed_side = 0.25               # m/s cutting the side (strokes ~ 3000/min, 30 mm teeth: < 1 stroke per 1.5 mm)
speed_top = 0.25
strokes_min = 3000.0
cut_w = 900.0                   # cutting length of the bar
hedge_h = 1.25                  # m hedge height (garden hedge; the top cut reaches ~1.26 m)
hedge_top_w = 0.8               # m hedge width (top)
trim_w = 600.0                  # W trimmer motor (garden-tool class)
tilt_w = 30.0
blow_w = 900.0                  # W blower at full power (battery leaf blower class, 48 V)
blow_q = 0.15                   # m3/s
blow_v = 45.0                   # m/s at the nozzle
leaf_lift_v = 8.0               # m/s air speed that moves wet leaves on a paved path (estimated)
drive_w = 150.0
computer_w = 30.0
battery_wh = 1900.0
noise_dba_7m = (74.0, 68.0)     # blower / trimmer at 7 m (datasheet class, estimated)

# from build_hdg.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 36.4, "mount_kg": 19.2, "carriage_kg": 12.4, "tilt_kg": 7.0, "blower_kg": 4.8}
