import math
import os
import sys

# =====================================================================
# Soil moisture sensor placer (simple) - parameters
# Places wireless soil moisture sensors at set GNSS points, reads them out by radio on every visit, and picks them up
# again at the end of the season. Mounted in the middle of the robot so its weight is the push force.
# The Z axis of the soil sampler ("soil sampler/simple": bridges, mast plate, SBR20 rails, ball screw SFU1605, NEMA23,
# carriage) is imported, not copied. On the carriage a 24 V gripper holds a sensor by its top knob instead of the gouge.
# Magazine: a star of 6 fork arms turning about a vertical shaft behind the Z axis; each sensor hangs in a fork by its
# cap. Pick: the index fork stands under the gripper, the gripper takes the knob and lifts the sensor out of the fork,
# the star turns half a step (a gap under the gripper), the Z axis pushes the sensor into the soil and the gripper
# lets go. Pick-up is the reverse.
# Sensor: cap O60 x 70 (electronics, LoRa radio, 2 x AA lithium) with a knob O30 on top, stem O20 x 300 with a cone tip;
# the capacitive moisture rings sit in the stem at 100 and 250 mm depth.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

SSA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "soil sampler", "simple")
if SSA_FOLDER not in sys.path:
    sys.path.append(SSA_FOLDER)
import ssa_params as A          # noqa: E402  (bridges, mast, rails, ball screw, motor, carriage)

robot_mass = A.robot_mass
robot_bracket_x = A.robot_bracket_x
bridge_z = A.bridge_z
bridge_rear_y = A.bridge_rear_y
probe_y = A.probe_y             # gripper axis (x = 0, y -60): the soil sampler's probe axis
holder_h = A.holder_h

# ---------------------------------------------------------------------
# Sensor (one of 6)
# ---------------------------------------------------------------------
knob = (30.0, 30.0)             # d, h: gripped by the jaws
cap = (60.0, 70.0)              # d, h: electronics, radio, battery
stem = (20.0, 300.0)            # d, length below the cap (incl. the cone): thin, so the robot weight pushes it in
cone_h = 30.0
ring_z = (100.0, 250.0)         # moisture rings below the cap bottom (= depth in the soil)
ring = (21.0, 12.0)
sensor_len = knob[1] + cap[1] + stem[1]        # 400
sensor_kg = 0.35

# ---------------------------------------------------------------------
# Gripper: 24 V electric parallel gripper under the carriage holder, 2 jaws 80 long reaching down round the knob
# ---------------------------------------------------------------------
grip_box = (80.0, 60.0, 50.0)   # x, y, z under the holder
jaw = (14.0, 24.0, 80.0)        # x, y, length down
jaw_open = 25.0                 # gap to the knob when open (each side)
grip_dz = 100.0                 # knob top is this far below the carriage bottom when held (jaw grip over 30 mm)

# carriage bottom (c) heights for the poses; the soil sampler's carriage stays the same part
c_park = 950.0                  # sensor tip (if held) 450 above the ground: under the robot's beams


def c_for_cap_bottom(z):
    """Carriage bottom height when the held sensor's cap bottom is at z."""
    return z + cap[1] + knob[1] + grip_dz


# ---------------------------------------------------------------------
# Magazine: star of 6 fork arms 50 x 8 on a hub, shaft O20 up to a cantilever plate on the rear bridge, NEMA17 + 5:1
# The index fork (sensor axis under the gripper) points to +y. The arm top is the hanging plane of the caps.
# ---------------------------------------------------------------------
n_sensors = 6
mag_r = 220.0                   # radius of the sensor axes
mag_c = (0.0, probe_y - mag_r)  # (0, -280)
arm_w = 50.0
arm_t = 8.0
arm_len = mag_r + 30.0          # from the hub centre
slot_w = stem[0] + 4.0          # fork slot, open to the outside
arm_top = 75.0 + stem[1] + arm_t   # stem tip of a hanging sensor 75 mm above the ground
hub_d = 90.0
shaft_d = 20.0
plate = ((-60.0, 60.0), (bridge_rear_y[1] - 40.0, mag_c[1] + 50.0), 10.0)   # cantilever plate on the rear bridge
mag_motor = (42.0, 48.0)

c_pick = c_for_cap_bottom(arm_top)                  # gripper on the knob of the index sensor
c_lift = c_pick + stem[1] + 15.0                  # whole sensor lifted out of the fork (the slot opens outward)
c_plant = c_for_cap_bottom(0.0)                     # cap bottom on the ground: stem 300 deep

# ---------------------------------------------------------------------
# Work (smp_calc)
# ---------------------------------------------------------------------
g = A.g
q_c = A.q_c                     # Pa cone resistance per soil state
f_s = A.f_s                     # Pa side friction
weight_use = A.weight_use
ball_eta = A.ball_eta
screw_lead = A.screw_lead
motor_torque = A.motor_torque
motor_rpm = A.motor_rpm
push_speed = 10.0               # mm/s while pushing (slow: the sensor must go in straight)
t_mag = 3.0                     # s to turn the star half a step
t_settle = 2.0                  # s stop, GNSS fix
speed = 1.0                     # m/s between points
points_per_ha = 2.0             # sensors per ha (one per management zone, estimated)
read_interval_min = 30.0        # sensor wakes up every 30 min, measures, stores; sends when the robot passes or a gateway
sleep_ua = 8.0                  # sleep current (estimated)
active_ma = 12.0                # measure + store
active_s = 2.0
tx_ma = 45.0                    # LoRa transmit
tx_s = 1.5
tx_per_day = 4                  # gateway or robot reads 4 times a day (estimated)
battery_mah = 2 * 3000.0 * 0.8  # 2 x AA lithium, 80 % usable
shelf_years = 10.0              # lithium AA self-discharge limit
radio_range_m = 2000.0          # LoRa to a farm gateway in open field (estimated)
m_gripper = 0.6
m_mag_motor = 0.4

# from build_smp.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 36.4}
