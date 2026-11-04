import os
import sys

# =====================================================================
# Air-assisted orchard sprayer (simple) - parameters
# Sprays the canopy of low fruit trees, vines or hedges on both sides of the alley with an air stream that carries
# the droplets into the leaves. A lidar per side measures the canopy and switches each height section on and off.
#   - tank (120 l), cradle, pump, filter, regulator and control box of the spot sprayer (imported, unchanged)
#   - a tower behind the robot: 2 arms 40 x 60 under the rear lower beams (x +-225), a cross beam, a mast 80 x 80
#   - per side 3 fan pods (axial fan O300, 48 V) at 0.8, 1.35 and 1.9 m, blowing sideways (+-x), each with a
#     nozzle ring and 2 hollow-cone nozzles, a section valve per pod (6 sections) in a manifold on the mast
#   - per side a 2D lidar (vertical scan plane) on an arm 190 mm ahead of the fans, for the canopy per section
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

_HERE = os.path.dirname(os.path.abspath(__file__))
SSP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "spotspray unit", "boom")
if SSP_FOLDER not in sys.path:
    sys.path.append(SSP_FOLDER)

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
robot_upper_beam_z = (659.0, 699.0)
robot_steer_max = 30.0
robot_kg = 161.5
robot_cg = (0.0, 95.0, 543.0)
robot_battery_kwh = 1.9
m10_hole = 10.4

# ---------------------------------------------------------------------
# Tower mount: 2 arms under the rear lower beams, a cross beam at the rear end
# ---------------------------------------------------------------------
arm_x = 225.0                   # grid hole line on the lower beams (inside the wheel brackets from x 261, outside
                                # the spot sprayer's sub plate x +-200)
arm_w = 40.0
arm_h = 60.0
arm_wall = 3.0
arm_z = (robot_lower_beam_z[0] - arm_h, robot_lower_beam_z[0])     # 559 .. 619
arm_y = (-395.0, -910.0)
arm_bolt_y = (-575.0, -425.0)   # through the rear lower beams (and the control box base plate on top)
mast_y = -880.0
cross_beam = (60.0, 4.0)        # 60 x 60 x 4, x +-245 between the arm ends
cross_y = (mast_y - 30.0, mast_y + 30.0)

# ---------------------------------------------------------------------
# Mast
# ---------------------------------------------------------------------
mast = 80.0
mast_wall = 4.0
mast_z = (arm_z[1], 2150.0)
mast_gusset = 150.0             # gusset 8 mm mast - cross beam at the front (the manifold sits at the rear)

# ---------------------------------------------------------------------
# Fan pods (right side; the left side is mirrored)
# ---------------------------------------------------------------------
pod_z = (800.0, 1350.0, 1900.0)
fan_d = 300.0
shroud_d = (330.0, 320.0)       # outer, inner (PE or aluminium shroud)
pod_x = (120.0, 280.0)          # shroud from x 120 (80 mm intake gap to the mast) to 280
bar = (8.0, 40.0)               # flat bars above and below the shroud, from the mast side face
rotor_x = (150.0, 170.0)
hub_d = 90.0
blades = 6
blade_w = 50.0
blade_pitch = 30.0              # degrees
motor = (100.0, 175.0, 255.0)   # diameter, x0, x1 (outlet side, on 3 spokes)
guard_t = 3.0
fan_q_m3_h = 1700.0             # per fan at the working point (estimated, 48 V axial O300)
fan_w = 200.0                   # electrical per fan (estimated)
fan_kg = 4.5                    # fan, motor, shroud and guard

# ---------------------------------------------------------------------
# Liquid: manifold, section lines, nozzle rings
# ---------------------------------------------------------------------
ring_x = pod_x[1] + 8.0         # nozzle ring at the outlet
ring_r = 150.0
ring_d = 10.0
nozzle = (20.0, 25.0)           # nozzle body d, length (hollow cone, pointing outward)
nozzles_per_pod = 2
nozzle_l_min = 0.3              # per nozzle at 7 bar (ATR lilac class, estimated)
line_d = 8.0
line_y = mast_y - mast / 2.0 - 10.0        # vertical lines behind the mast (y -930)
line_x = {1900.0: 12.0, 1350.0: 24.0, 800.0: 36.0}   # top pod line innermost
line_drop = 190.0               # horizontal run under each pod: z = pod_z - line_drop
manifold = ((-48.0, 48.0), (mast_y - 80.0, line_y + 9.0), (540.0, 600.0))   # 6 solenoid valves on the mast rear
hose_z = 500.0                  # pressure hose from the regulator to the manifold, under the arms

# ---------------------------------------------------------------------
# Canopy sensing: 2D lidar per side on an arm ahead of the fans
# ---------------------------------------------------------------------
lidar_arm_y = (mast_y + mast / 2.0, -690.0)
lidar_arm_z = 1600.0
lidar = (60.0, 70.0, 80.0)      # box x, y, z per lidar
lidar_y = (lidar_arm_y[1], lidar_arm_y[1] + lidar[1])          # -690 .. -620, ahead of the arm end
lidar_lead = 0.5 * (lidar_y[0] + lidar_y[1]) - mast_y           # 225 mm ahead of the fan / nozzle plane

# ---------------------------------------------------------------------
# Operation (oas_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
liquid_density = 1.0
tank_l = 120.0
pump_bar = 7.0
pump_w = 150.0                  # electrical at 7 bar (estimated, higher-pressure version of the spot sprayer pump)
drive_w = 300.0                 # drive with a full tank at 0.5 m/s in the alley (estimated)
electronics_w = 60.0            # controller, 2 lidars, valves
row_spacing = 3.0               # m between tree rows (alley centre to centre)
canopy_h = (0.6, 2.1)           # m, canopy band to cover
canopy_depth = 1.2              # m, canopy width across the row
air_factor = 1.0                # air needed = v x canopy height x half row spacing x factor (replace the air)
dose_l_ha = (200.0, 500.0)      # usual range
valve_latency_s = 0.08
canopy_gap_share = 0.30         # share of the row without canopy (gaps, young trees) that sensing saves
liquid_kg = tank_l * liquid_density

# from build_oas.mass_properties() (update after a change of the model; empty tank, spot sprayer parts included)
MODEL_MASS = {"total_kg": 104.8, "cg": (0.0, -601.0, 1026.0)}
