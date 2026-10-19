import os
import sys

# =====================================================================
# Overseeder, simple drop seeder - parameters
# A 1 m drop seeder (gravity box) that lets grass seed fall on the lawn in a curtain. A fluted metering roller in
# the throat of the hopper is turned by a small 24 V worm gearmotor: motor on = seed, motor off = nothing (the
# brush strip stops the flow). A camera on a short mast looks at the strip in front of the hopper and sees bare
# soil (no green), so the motor only runs over bare patches.
#
# The seeder unit (hopper, end plates, meter, motor, camera, control box) is one module. Here it rides on its own
# two small wheels and a drawbar; in "overseeder with cambridge roll" the same module hangs between the arms of
# the roll. The tow hitch and the coupling head come from the Cambridge roll (cbr_params / cbr_parts).
#
# Unit coordinates: x = right, v = forward (= robot y minus unit_y), z = up; origin = middle of the drop line on
# the ground. The parts are moved to robot coordinates with unit_y (the y of the drop line).
# =====================================================================
FOLDER = os.path.dirname(os.path.abspath(__file__))
CBR_FOLDER = os.path.join(os.path.dirname(FOLDER), "cambridge roll")
if CBR_FOLDER not in sys.path:
    sys.path.insert(0, CBR_FOLDER)

import cbr_params as H          # robot interface, tow hitch, coupling head, drawbar tube  # noqa: E402

# ---------------------------------------------------------------------
# Hopper: galvanised sheet 1.5 mm, two sloping walls between two end plates (5 mm). Throat at the bottom over the
# metering roller. Lid on top (hinged at the back).
# ---------------------------------------------------------------------
width = 1000.0                  # inside, = working width
sheet = 1.5
throat_v = 30.0                 # throat v = +-30
throat_z = 240.0
top_v = 160.0                   # top opening v = +-160
top_z = 500.0
end_plate_t = 5.0
end_plate_v = (-170.0, 170.0)
end_plate_z = (150.0, 500.0)
lid_t = 2.0
lid_v = (-175.0, 175.0)
hinge_d = 12.0

# Metering: fluted roller (aluminium extrusion or PVC with milled grooves) O50, 12 flutes, shaft O15 in two
# flange bearings (2-bolt, 15 mm) on the outside of the end plates.
roller_d = 50.0
roller_z = 205.0                # axis
flutes = 12
flute = (6.0, 5.0)              # width, depth
roller_fill = 0.8               # filling of the flutes (estimated)
meter_shaft_d = 15.0
meter_shaft_x = 545.0           # shaft from -545 to +545 (into the coupling at +x)
meter_bearing = (60.0, 32.0, 6.0, 26.0, 18.0)   # flange length (z), width (v), thickness, boss O, boss length
housing_v = 32.0                # housing walls at v = +-30 .. +-32, from the throat down to the roller axis
housing_z = (roller_z - 15.0, throat_z)
brush = (3.0, 20.0)             # brush strip on the front wall: thickness, height (closes the gap to the roller)
flap = (2.0, 60.0)              # rubber wind flaps under the housing walls: thickness, bottom z

# Drive: 24 V worm gearmotor (output O8, about 20 rpm, 2 Nm), motor pointing down, on a bracket at +x
gm_box = ((560.0, 600.0), (-25.0, 25.0), (180.0, 235.0))       # gearbox x, v, z
gm_motor = (37.0, 110.0)        # motor diameter, bottom z (motor from the gearbox down)
gm_bracket = ((505.0, 600.0), (30.0, 34.0), (170.0, 245.0))     # angle bracket x, v, z (bolted to the end plate)
gm_coupling = (25.0, 540.0, 560.0)              # flexible coupling diameter, x0, x1
gm_rpm = 20.0
gm_torque = 2.0                 # Nm
gm_w = 12.0                     # W electrical while running (estimated)
gm_kg = 0.45

# Camera: USB/CSI camera (wide angle) in a small housing on a mast at the front, looking down at the strip in
# front of the hopper. Excess green index per 50 mm cell -> bare / green.
mast = (25.0, 2.0)              # square tube
mast_v = (178.0, 203.0)
mast_x = (-12.5, 12.5)
mast_z = (430.0, 800.0)
mast_clamps = ((440.0, 460.0), (475.0, 495.0))  # z of the two brackets welded on the front wall
cam_box = (70.0, 50.0, 45.0)    # x, length along the view axis, height
cam_pos = (0.0, 215.0, 850.0)   # centre of the camera housing (x, v, z)
cam_pitch = 35.0                # degrees from vertical, looking forward
cam_fov = (90.0, 70.0)          # horizontal, vertical field of view (degrees)
cell = 50.0                     # analysis cell on the ground
cam_use_v = (400.0, 1200.0)     # strip of the image that is analysed (v on the ground): sharp, little perspective

# Control box (IP65): Raspberry Pi / ESP32, motor driver, DC-DC 48 -> 24 V; on the front wall, right
box = ((150.0, 330.0), (172.0, 242.0), (380.0, 480.0))
box_kg = 1.6

# ---------------------------------------------------------------------
# Stand-alone trailer: front and rear cross bar (square tube 40 x 40 x 3) between the end plates, two solid rubber
# wheels 200 x 50 behind the drop line (they also press the seed in two tracks), drawbar + coupling as on the roll.
# ---------------------------------------------------------------------
unit_y = -1650.0                # drop line of the stand-alone overseeder
bar = (40.0, 3.0)
front_bar_v = (130.0, 170.0)
rear_bar_v = (-170.0, -130.0)
bar_z = (300.0, 340.0)
wheel_d = 200.0
wheel_w = 50.0
wheel_hub = (60.0, 70.0)        # hub diameter, length
wheel_x = 440.0
wheel_v = -160.0
wheel_axle_d = 20.0
fork = (6.0, 30.0)              # flat bar thickness, width
wheel_kg = 2.2
f_wheel = 0.10                  # rolling resistance of the small wheels on lawn (estimated)

# ---------------------------------------------------------------------
# Seed and operation (ovd_calc and the animation)
# ---------------------------------------------------------------------
seed_density = 0.35             # kg/l, perennial ryegrass / lawn mixture (estimated, 0.25 - 0.40)
seed_rate = 35.0                # g/m2 for bare patches (repair: 30 - 50; overseeding a full sward 15 - 25)
work_speed = H.work_speed       # m/s
motor_start = 0.15              # s, motor to speed (estimated)
motor_stop = 0.10
fall_h = roller_z - roller_d / 2.0  # m from the bottom of the roller to the ground
bare_threshold = 0.10           # fraction of the 1 m strip that must be bare to switch on (2 cells of 50 mm): a single bare cell is ignored
off_margin = 50.0               # mm: keep seeding this far past the end of a patch
on_margin = 50.0                # mm: start this far before a patch
steel = H.steel
unit_kg = 34.7                  # seeder unit without seed, measured on the model (build_ovd.mass_properties)
trailer_kg = 60.6               # stand-alone trailer without seed, idem
