import math

# =====================================================================
# UV-C mildew light (simple) - parameters
# A reflecting hood with UV-C lamps under the Bruut OpenAgbot (standard robot), between the axles, over the bed the
# robot straddles (strawberries, lettuce, herbs, nursery stock). It drives at night (no photo-repair of the fungus) and
# gives the crop a low UV-C dose against powdery mildew, without chemicals. Brush curtains front and rear and rubber
# side skirts keep the UV-C inside; the lamps only burn while the hood is down and the robot moves.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_r = 265.0            # lugged tyre in the model
robot_tire_w = 100.0
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_z = (659.0, 699.0)
robot_steer_deg = 30.0
robot_mass = 160.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Mount: 2 bearers 40 x 40 x 3 across the upper beams, 4 hangers (flat 40 x 6 with a slot: hood height +-75)
# ---------------------------------------------------------------------
bearer_y = (180.0, -180.0)
bearer = 40.0
bearer_x = 470.0
hanger = (40.0, 6.0)
hanger_x = 250.0                # hangers at x +-250, inside the hood width
slot = 150.0                    # height adjustment

# ---------------------------------------------------------------------
# Hood: aluminium 2 mm (anodised, UV reflecting), between the axles. The steered front tyres reach y ~297 at x ~200
# (axle height), the rear tyres start at y -235: the hood stays within y +-220.
# ---------------------------------------------------------------------
hood_x = 290.0                  # half width outside (tyre inner face x 325)
hood_y = 220.0                  # half length
hood_top = 640.0                # top of the hood roof (under the upper beams? no: the beams are at x 305+, the hood
                                # roof spans x +-290 between them)
hood_bottom = 300.0             # bottom edge of the side walls (above the crop rows edge)
sheet = 2.0
skirt = (6.0, 150.0)            # rubber side skirts, thickness, height below the walls (down to z 150)
brush = (25.0, 470.0)           # brush curtains front and rear: thickness (y), height from the roof down to z 150
rib = (20.0, 20.0, 2.0)         # stiffening angles across the roof (also the lamp holders)

# Lamps: 6 x UV-C compact tubes (PL-L 55 W class, 535 long, 2 x O19 legs) across x, under the roof
n_lamps = 6
lamp_len = 535.0
lamp_tube_d = 19.0
lamp_leg_gap = 22.0             # centre distance of the 2 legs of a PL-L tube
lamp_z = 590.0                  # lamp axis
lamp_holder = (30.0, 40.0, 25.0)        # socket block x, y, z
guard_d = 3.0                   # wire guard bars under the lamps (2 per lamp)

# Driver box (6 electronic ballasts, interlock relay) on the rear bearer; lid switch / tilt sensor inside
driver_box = (360.0, 160.0, 90.0)

# ---------------------------------------------------------------------
# Work (uvc_calc)
# ---------------------------------------------------------------------
p_lamp = 55.0                   # W electric per lamp
uv_eff = 0.31                   # UV-C (254 nm) output / electric input of a low-pressure tube (17 W of 55 W)
ballast_eta = 0.90
reflect = 0.65                  # share of the UV-C that reaches the canopy plane (reflector, guards, losses), estimated
canopy_z = 300.0                # top of the crop (strawberries); lamp distance = lamp_z - canopy_z
dose_target = {"strawberry_mildew": 200.0, "low": 100.0, "high": 400.0}   # J/m2 per pass (literature 85..400)
passes_per_week = 2
p_drive_base = 40.0             # W driving at low speed on a headland-free bed (estimated: rolling only)
crr = 0.06
eta_drive = 0.75
g = 9.81
battery_wh = 1900.0
bed_len = 100.0                 # m
turn_s = 30.0
alu = 2.7e-6
steel = 7.85e-6
rubber = 1.2e-6
