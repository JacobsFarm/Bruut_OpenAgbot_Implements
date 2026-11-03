import math
import os
import sys

# =====================================================================
# Drop-on-demand boom (simple) - parameters
# A dark hood under the belly of the Bruut OpenAgbot (standard robot), between the wheels, over one bed of ~0.6 m.
# Inside the hood: a camera looking straight down at the front half, 2 LED bars (constant light, day and night), and
# at the rear a rail of 24 solenoid micro-injectors at 25 mm pitch that fire single coarse drops (5 ul) straight down
# onto every weed the camera found. No fan, no drift: the drops fall 80 mm inside a closed hood.
# Tank, pump, filter, regulator and control box come from the spot sprayer ("spotspray unit/boom", imported, not
# copied); the folding boom and the camera mast of the spot sprayer are not used.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

SSP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "spotspray unit", "boom")
if SSP_FOLDER not in sys.path:
    sys.path.append(SSP_FOLDER)
import ssp_params as S          # noqa: E402  (tank, cradle, pump, regulator, control box of the spot sprayer)

# ---------------------------------------------------------------------
# Robot interface (from the spot sprayer, which took it from agbot_params.py)
# ---------------------------------------------------------------------
robot_wheel_x = S.robot_wheel_x
robot_axle_y = S.robot_axle_y
robot_axle_z = S.robot_axle_z
robot_tire_d = S.robot_tire_d
robot_tire_w = S.robot_tire_w
robot_lower_beam_y = S.robot_lower_beam_y       # centres of the 4 lower cross beams 40 x 40
robot_lower_beam_z = S.robot_lower_beam_z       # 619 .. 659
robot_bracket_x = S.robot_bracket_x             # wheel brackets and wooden blocks from x 261 outward: stay inside
robot_steer_max = S.robot_steer_max
robot_kg = S.robot_kg
m10_hole = S.m10_hole

# ---------------------------------------------------------------------
# Belly rails: 2 x square tube 40 x 40 x 3 along y under the lower beams at x +-225 (grid holes), 4 x M10 each.
# At the rear the bolts also go through the control-box base plate of the spot sprayer (2 extra holes per side).
# Inside the sub plate (x +-200) and the wheel brackets (x 261).
# ---------------------------------------------------------------------
rail_x = 225.0
rail = 40.0
rail_wall = 3.0
rail_y = (-595.0, 595.0)
rail_z = (robot_lower_beam_z[0] - rail, robot_lower_beam_z[0])     # 579 .. 619
rail_bolt_y = robot_lower_beam_y                                    # -575, -425, 425, 575

# ---------------------------------------------------------------------
# Hood: aluminium 2 mm box, open at the bottom, between the tyres and inside the front steering sweep.
# A steered front tyre (30 deg) reaches y ~289 (outer corner) and x ~224 at y ~339; the rear tyres start at y -285.
# Height in 3 steps of 25 mm (pins through the hanger posts): skirt bottom 35 / 60 / 85 above the ground.
# A brush strip (nylon, 50 mm) closes the gap to the ground: dark and wind-free inside.
# ---------------------------------------------------------------------
hood_x = 300.0                  # half width (outside)
hood_y = (-262.0, 262.0)
hood_t = 2.0
hood_h = 360.0                  # top to skirt bottom
skirt_bottom = 60.0             # middle height step
height_steps = (-25.0, 0.0, 25.0)
hood_top = skirt_bottom + hood_h            # 420 (top face of the top sheet)
brush_h = 50.0                  # brush strip under the skirt: tips 10 mm above the ground at the middle step
brush_t = 8.0
brush_holder = (12.0, 15.0)     # aluminium U-holder around the brush back: width, height
flange = 25.0                   # top sheet folded down 25 mm round the edge (stiffness)

# Hanger posts: square tube 30 x 30 x 2 from a foot plate under the rail down to a bracket on the hood top,
# M10 cross-pin through 3 hole pairs (25 mm apart) = the height steps.
post = 30.0
post_wall = 2.0
post_y = (-190.0, 190.0)
post_foot = (60.0, 70.0, 8.0)   # foot plate x, y, t (welded to the post, 2 x M8 into the rail underside)
post_bracket = (50.0, 50.0, 6.0, 95.0)      # U-bracket on the hood top: x, y, plate t, cheek height
pin_dz = 75.0                   # cross pin above the hood top (one hole in the bracket cheeks)
post_bottom_dz = 35.0           # post end above the hood top at the middle step (25 mm room to raise the hood)
pin_d = 10.0

# ---------------------------------------------------------------------
# Camera inside the hood: global-shutter 5 MP (same as the spot sprayer), f = 3.5 mm, straight down, at the front.
# It sees the ground in front of the injector line; the image long side lies across.
# ---------------------------------------------------------------------
cam_xy = (0.0, 175.0)
cam_box = (70.0, 70.0, 90.0)    # x, y, z (housing incl. lens)
cam_lens = (30.0, 15.0)         # lens tube d, length below the housing
cam_bracket_t = 5.0
cam_px = S.cam_px               # 2448 x 2048
cam_pixel = S.cam_pixel         # 3.45 um
cam_f = 3.5                     # mm (wider than on the mast)
cam_fps = S.cam_fps             # 20
infer_ms = S.infer_ms           # 60 ms detection per frame (Jetson class)
exposure_ms = 0.1               # LED light is bright and constant: short exposure, no motion blur

# LED bars: 2 x aluminium profile 600 x 30 x 15, under the top sheet, across, before and behind the camera
led_y = (95.0, 240.0)           # centre y of the 2 bars (front bar just inside the front wall)
led_bar = (560.0, 30.0, 15.0)
led_w = 2 * 24.0                # W, 2 x 24 W (estimated)

# ---------------------------------------------------------------------
# Injector rail: aluminium manifold 600 x 30 x 25 with a bore O10 (liquid), 24 micro-injectors at 25 mm pitch
# underneath, tips 80 mm above the ground. Hung from the hood top by 2 brackets.
# Injector: 12 V solenoid micro-valve (inkjet / fuel-injector type), O14 x 45 + nozzle O6 x 15, orifice 0.3 mm.
# ---------------------------------------------------------------------
n_inj = 24
inj_pitch = 25.0
work_width = n_inj * inj_pitch              # 600
inj_y = -205.0                  # injector line
inj_x = tuple(-0.5 * (n_inj - 1) * inj_pitch + i * inj_pitch for i in range(n_inj))
tip_z = 80.0                    # drop release height above the ground (middle step)
inj_body = (14.0, 45.0)         # d, length
inj_nozzle = (6.0, 15.0)
inj_plug = (10.0, 12.0, 8.0)    # connector on the rear side: x, y, z
mani = (600.0, 30.0, 25.0)      # x, y, z
mani_z0 = tip_z + inj_nozzle[1] + inj_body[1]               # 140
mani_bore = 10.0
mani_bracket_x = 250.0          # 2 brackets at x +-250, 4 mm plate
mani_bracket_t = 4.0

drop_ul = 5.0                   # volume per drop (coarse: ~2.1 mm)
fire_hz_max = 200.0             # max firing rate of one injector (typical micro-valve, estimated)
open_ms = 1.5                   # valve open time per drop at 1 bar (estimated)
inj_w = 3.0                     # W per injector at the duty cycle of a weed (peak-and-hold driver, estimated)
drop_v0 = 1.0                   # m/s exit speed of the drop at 0.5 bar (estimated)
dod_p = 0.5                     # bar at the manifold (second, low-pressure regulator)

# Low-pressure regulator + accumulator on the hood top at the rear, fed from the spot-sprayer regulator (3 bar)
lp_reg = (60.0, 45.0, 70.0)     # x, y, z body
lp_xy = (90.0, -225.0)
accu = (60.0, 130.0)            # accumulator O60 x 130 lying along x behind the regulator
accu_xy = (-10.0, -225.0)
hose_d = S.hose_d
bleed_xy = (-285.0, -205.0)     # bleed valve on the left end of the manifold (air out after filling)

# ---------------------------------------------------------------------
# Field and operation (for ddb_calc and the animation)
# ---------------------------------------------------------------------
speed = 0.5                     # m/s
bed_width = 600.0               # bed between the wheel tracks (750 track - 100 tyre - margins)
crop_rows = (-150.0, 150.0)     # 2 rows of lettuce / onion per bed
crop_spacing = 300.0
crop_protect = 40.0             # mm keep-out around a crop plant (no drop inside its leaves + this)
drop_grid = 25.0                # along y: one drop per 25 mm (the across pitch is the injector pitch)
weed_d = (15.0, 70.0)           # weed seedlings: leaf diameter range (2..6 leaf stage)
weed_density = 20.0             # weeds per m2 in the bed (estimated, medium pressure)
blanket_rate = 200.0            # l/ha of a conventional broadcast pass for comparison
odo_err = 0.005                 # wheel odometry error (fraction of the distance, estimated)
jitter_ms = 1.0                 # valve timing jitter (estimated)
field_eff = 0.75                # headlands, refilling
battery_wh = 1900.0             # usable, estimated (battery pack/simple)
drive_w = 300.0                 # W driving at 0.5 m/s in a bed (estimated)
computer_w = 40.0
pump_duty = 0.25                # pump runs on its pressure switch: low flow, short duty (estimated)
liquid_density = S.liquid_density
fill_l = 30.0                   # usual fill of the 120 l spot-sprayer tank: drop-on-demand uses very little
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
nylon = 0.35e-6                 # brush strip bulk (bristles + back, estimated)

# from build_ddb.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 73.5, "cg": (0.0, -181.0, 611.0), "hood_kg": 17.1, "tank_kg": 21.3, "mount_kg": 29.1}


def drop_d():
    """Drop diameter (mm) of one drop of drop_ul."""
    return (6.0 * drop_ul / math.pi) ** (1.0 / 3.0)
