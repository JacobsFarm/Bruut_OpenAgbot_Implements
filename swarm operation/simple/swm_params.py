import os
import sys

# =====================================================================
# Swarm operation (simple) - parameters
# Several Bruut units work one field as a swarm. Mostly software (job planner, pass allocation, reserved corridors,
# hand-over of a pass when a unit drops out); the hardware is a swarm kit per robot:
#  - a 40 x 40 post on a flat bar across the inner upper beams at y -325 (grid holes), 1.5 m high;
#  - a 868 MHz mesh radio with a whip antenna on top (position, progress, battery, intent, 5 Hz);
#  - a status light tower (green working, yellow turning / waiting at a corridor, red stopped, blue refilling) so
#    people and the other units see the state;
#  - a small box with the swarm computer and the radio.
# Every unit keeps its own RTK-GNSS; the RTK base at the field edge also relays the mesh to the farm network.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

PBL_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "push blade", "simple")
if PBL_FOLDER not in sys.path:
    sys.path.append(PBL_FOLDER)

robot_steer_deg = 30.0
robot_mass = 160.0
upper_beam_top = 699.0
hole_y = 325.0                  # upper-beam grid holes at |y| 275, 325 .. 625
bar_x = (-345.0, 345.0)
bar_w = 60.0
bar_t = 8.0
post_w = 40.0
post_top = 1500.0
post_x = -150.0                 # left of the centre line (clear of other tools on the centre line)
lights = (70.0, 4, 60.0)        # O, segments, segment height
whip = (12.0, 350.0)            # O, length
box = (160.0, 110.0, 80.0)      # swarm computer + radio on the bar

# ---------------------------------------------------------------------
# Work (swm_calc)
# ---------------------------------------------------------------------
field = (400.0, 250.0)          # m (10 ha)
pass_w = 1.8                    # m working width per unit (e.g. 2 rows of the yield estimator, a 1.8 m spreader)
speed = 1.2                     # m/s working
turn_s = 25.0                   # s per headland turn
corridor_wait_s = 6.0           # s average wait at a shared headland corridor per turn per extra unit (estimated)
units = (1, 2, 3, 4, 6, 8)
msg_bytes = 96                  # position, heading, pass id, progress, battery, intent
msg_hz = 5.0
radio_kbps = 50.0               # usable mesh throughput (868 MHz, estimated)
battery_h = 6.0                 # working hours per charge (light tool)
charge_h = 3.0
chargers = 1
unit_mass = 160.0
tyre_contact_m2 = 0.025         # per wheel, standard robot on soil (estimated)
tractor = {"mass": 6000.0, "contact_m2": 0.35, "wheels": 4}
MODEL_MASS = {"kg": 6.0}
