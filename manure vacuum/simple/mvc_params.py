import math
import os
import sys

# =====================================================================
# Manure vacuum collector (simple) - parameters
# Sucks fresh manure from a solid barn floor into a vacuum tank and empties it at the pit, instead of pushing it.
# In front: the debris vacuum's nozzle hood on the magnet sweeper's head frame and castors, on the push blade's lift
# arms, king pin and actuator ("debris vacuum/simple", imported, not copied), WITHOUT the brush roller: a rubber
# squeegee lip at the rear of the hood touches the floor and gathers the manure, the front flap rides 40 mm high.
# The same PU hose O125 goes up to a sealed stainless vacuum tank (130 l, cylinder O460 along y) on 2 cross bars over
# the upper beams; a float valve and a moisture trap on the tank top protect the rotary-vane vacuum pump behind it. A
# knife-gate dump valve O150 in the bottom at the rear opens over the pit grid.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# =====================================================================

DVC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "debris vacuum", "simple")
if DVC_FOLDER not in sys.path:
    sys.path.append(DVC_FOLDER)
import dvc_params as D          # noqa: E402

robot_axle_y = D.robot_axle_y
robot_mass = 161.5
upper_beam_top = D.upper_beam_top
lift_work = D.lift_work
lift_transport = D.lift_transport
LIFT_POSES = D.LIFT_POSES

# ---------------------------------------------------------------------
# Nozzle changes: no brush roller; front flap 40 mm over the floor, rear squeegee lip 12 mm rubber, 20 mm interference
# ---------------------------------------------------------------------
flap_gap_front = 40.0
lip_t = 12.0
lip_h = 120.0                   # free height of the lip below the rear wall
lip_press = 5.0                 # lip reaches 5 mm into the floor line (it bends back)

# ---------------------------------------------------------------------
# Vacuum tank: stainless 2.5 mm cylinder O460 along y, dished ends (drawn flat 4 mm); inlet stub = the debris
# vacuum's bin inlet position (front end at y 370, stub at z 1075), on 2 saddles on the cross bars.
# ---------------------------------------------------------------------
tank_d = 460.0
tank_t = 2.5
tank_y = (-430.0, D.bin_y[1])   # -430 .. 370
saddle_h = 25.0
bar_top = upper_beam_top + D.bar_wh[1]                    # 739
tank_axis_z = bar_top + saddle_h + tank_d / 2.0           # 994
inlet_z = D.inlet_z             # 1075
saddle_y = (-325.0, 325.0)
saddle_w = 60.0
float_xy = (0.0, -250.0)        # float valve on the top, rear
float_d = (110.0, 180.0)        # housing O, height
trap = (120.0, 200.0)           # moisture trap O, height (beside the float valve)
trap_xy = (150.0, -330.0)
dump_d = 150.0                  # knife-gate dump valve under the rear end
dump_y = -170.0                 # clear of the rear cross bar (y -355 .. -295)
dump_body = (220.0, 60.0)       # valve body square, height
dump_act = (40.0, 260.0)        # actuator O, length (along x)

# Vacuum pump behind the tank on a shelf on the rear cross bar
pump_box = (300.0, 200.0, 220.0)    # rotary vane pump + 48 V motor, x, y, z
pump_y = -560.0
shelf = (360.0, 260.0, 6.0)

# ---------------------------------------------------------------------
# Work (for mvc_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
stainless = 7.9e-6
rubber = 1.3e-6
manure_density = 1.02           # kg/l, fresh cow manure + urine
vacuum_bar = 0.5                # working vacuum
pump_m3h = 60.0                 # free air (rotary vane, oil-free, estimated)
pump_w = 900.0
manure_l_m2 = 1.5               # l of manure per m2 of alley between cleanings (8 rounds a day, 100 cows, estimated)
alley_w = 3.0                   # m alley width (3 passes of ~1 m)
nozzle_w = 1.0
speed = 0.25                    # m/s collecting
transit = 0.8                   # m/s to and from the pit
pit_dist = 60.0                 # m average to the pit
dump_s = 30.0
mu_floor = 0.30                 # tyres on a wet concrete floor
crr = 0.04
lip_drag = 150.0                # N squeegee on the floor (estimated)
battery_wh = 1900.0
computer_w = 30.0
cows = 100
manure_cow_day = 55.0           # l per cow per day; ~ 40 % lands on the alleys (estimated)
alley_share = 0.40

# from build_mvc.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 181.5, "cg_y": 435.0, "lift_kg": 60.6, "lift_cg_y": 1242.0, "tank_kg": 89.5}


def tank_litres():
    r = tank_d / 2.0 - tank_t
    return math.pi * r * r * (tank_y[1] - tank_y[0]) / 1e6
