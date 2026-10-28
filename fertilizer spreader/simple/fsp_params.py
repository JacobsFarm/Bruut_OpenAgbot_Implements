import math

# =====================================================================
# Fertilizer spreader (simple) - parameters
# Spinning-disc spreader for granular fertilizer on the Bruut OpenAgbot (standard robot).
# An 80 l hopper sits over and behind the rear axle on two rails bolted on top of the inner upper beams; its funnel
# ends behind the rear lower beams in a fluted metering roller (dose follows the driving speed, variable rate from a
# task map) that drops the granules on a vaned disc behind the robot. A curved guard keeps the throw off the robot.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_axle_y = 500.0
robot_upper_beam_x = (325.0, 425.0)     # centres of the 2 upper beams per side (40 x 40), along y, y = +-650
robot_upper_beam_z = (659.0, 699.0)
robot_upper_beam_y_end = 650.0
robot_rear_beam_y = (-575.0, -425.0)    # centres of the rear lower beams
robot_lower_beam_z = (619.0, 659.0)
robot_beam = 40.0
robot_tire_d = 430.0
robot_mass = 160.0              # kg, estimated (agbot comparison)
robot_cg_y = 0.0                # estimated
robot_cg_z = 450.0              # estimated (battery low in the frame)
robot_track = 750.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Rails: 2 x rect tube 40 x 40 x 3 on top of the inner upper beams (x = +-325), 3 x M10 each in the hole grid,
# running back past the beam ends to carry the hopper and the spinner frame
# ---------------------------------------------------------------------
rail_x = 325.0
rail = 40.0
rail_wall = 3.0
rail_y = (-1090.0, -150.0)
spacer_h = 25.0                 # spacer blocks under the rails: clear of the wheel-unit bolts sticking up at x 325 / 425
rail_z = (robot_upper_beam_z[1] + spacer_h, robot_upper_beam_z[1] + spacer_h + rail)
rail_bolt_y = (-625.0, -500.0, -250.0)   # between the wheel-unit bolts at y -425 and -575

# ---------------------------------------------------------------------
# Hopper: PE (8 mm drawn as 4 mm walls), straight upper part on a steel ring, pyramid funnel down to the outlet.
# Funnel walls >= 44 degrees, so fertilizer runs freely (angle of repose ~30..35).
# ---------------------------------------------------------------------
hop_x = 300.0                   # half width of the straight part
hop_y = (-1080.0, -600.0)
hop_z = (900.0, 1100.0)         # straight part
hop_t = 4.0
out_x = 50.0                    # outlet: half width (x), and y range, bottom of the funnel
out_y = (-910.0, -810.0)
out_z = 640.0
ring = (40.0, 4.0)              # angle 40 x 40 x 4 around the straight part, resting on 4 posts
post = 40.0                     # posts 40 x 40 x 3 from the rails up to the ring
post_y = (-1040.0, -640.0)
lid_t = 3.0
fill_density = 1.0              # kg/l, granular fertilizer (CAN 1.0..1.1, urea 0.75)

# ---------------------------------------------------------------------
# Metering: fluted roller O80 x 120 (10 flutes), housing under the outlet, 12 V gearmotor on the side
# ---------------------------------------------------------------------
roller_d = 80.0
roller_len = 120.0
flutes = 10
flute_depth = 12.0
flute_w = 16.0
roller_axis = (-860.0, 595.0)   # (y, z)
housing_z = (550.0, out_z)
housing_y = (-920.0, -800.0)
housing_x = 75.0                # half width (outside), 3 mm sheet
meter_motor = (45.0, 70.0)      # gearmotor O45 x 70 (+ gearbox) on the right side
meter_rpm_max = 90.0              # gearmotor 100 rpm
chute_drop = (-845.0, 505.0)    # (y, z) end of the drop chute above the disc: 35 mm in front of the disc centre

# ---------------------------------------------------------------------
# Spinner: disc O400 x 3 with 4 vanes (h 35), on a 48 V BLDC gearmotor (300 W) under the disc
# ---------------------------------------------------------------------
disc_y = -880.0
disc_d = 400.0
disc_t = 3.0
disc_z = 470.0                  # bottom of the disc
vane_h = 35.0
vane_t = 3.0
n_vanes = 4
vane_r = (40.0, 195.0)
disc_rpm = 700.0                # nominal; 500..900 sets the width
spin_motor_d = 90.0
spin_motor_z = (345.0, 455.0)
guard_r = 225.0                 # guard sheet 2 mm round the front half of the disc
guard_ang = (15.0, 165.0)       # degrees, 90 = front (+y)
guard_z = (440.0, 560.0)

# Spinner frame: 2 legs 40 x 40 down from the rail ends, a cross tube at the bottom and an arm forward to the
# motor plate (all behind and under the disc, out of the throw)
leg_y = (-1090.0, -1050.0)
frame_z = (300.0, 340.0)
motor_plate = (140.0, 8.0)      # square plate under the motor

# ---------------------------------------------------------------------
# Work (fsp_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
pe = 0.96e-6
speed = 1.0                     # m/s (3.6 km/h)
granule_d = 3.5e-3              # m
granule_rho = 1500.0            # kg/m3 (particle)
cd = 0.44
air_rho = 1.2
v_factor = 1.30                 # exit speed / tip speed (radial + tangential, slip on the vanes)
launch_deg = 0.0
overlap = 0.5                   # driving width = overlap * throw width (both sides), estimated for a triangular pattern
fill_factor = 0.85              # filling of the flutes
dose_kg_ha = (100.0, 300.0, 500.0)
m_meter_motor = 0.6
m_spin_motor = 3.2


def hopper_volume():
    """Volume (l) of the hopper: straight part + funnel (frustum of two rectangles)."""
    a1 = (2 * hop_x) * (hop_y[1] - hop_y[0])
    a2 = (2 * out_x) * (out_y[1] - out_y[0])
    h = hop_z[0] - out_z
    funnel = h / 3.0 * (a1 + a2 + math.sqrt(a1 * a2))
    straight = a1 * (hop_z[1] - hop_z[0])
    return (funnel + straight) / 1e6


def funnel_angles():
    """Slope (degrees from horizontal) of the four funnel walls: front, rear, side."""
    h = hop_z[0] - out_z
    return {"front": math.degrees(math.atan2(h, hop_y[1] - out_y[1])),
            "rear": math.degrees(math.atan2(h, out_y[0] - hop_y[0])),
            "side": math.degrees(math.atan2(h, hop_x - out_x))}


def roller_ml_per_rev():
    return flutes * flute_w * flute_depth * roller_len * fill_factor / 1000.0
# from build_fsp.mass_properties() (update after a change of the model)
MODEL_MASS = {"empty_kg": 42.1, "empty_cg_y": -818.0, "empty_cg_z": 652.0, "full_kg": 130.2, "full_cg_y": -834.0,
              "full_cg_z": 846.0, "fill_kg": 88.1, "ballast_kg": 40.1, "ballast_cg_y": 575.0, "ballast_cg_z": 712.0}

# Counterweight (optional, same 2 blocks as the disc brushes) on the front lower beams, for a full hopper
ballast_x = (110.0, 270.0)      # both sides of the GNSS antenna
ballast_y = (500.0, 650.0)
ballast_h = 106.0               # 2 x ~20 kg
ballast_z0 = robot_lower_beam_z[1]
