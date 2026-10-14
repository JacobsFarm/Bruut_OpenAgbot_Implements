import math
import os
import sys

# =====================================================================
# Stationary refill station - common parameters (all three carriers: IBC trailer, three-point frame, flat wagon)
# A standard 1000 l IBC (or several) stands on a carrier at the headland. The station has its own control box with
# the pump, its motor and all electronics (battery, controller, RTK receiver, radio), a mast with a swinging arm and a
# drop pipe to a drip-stop nozzle, and an RTK antenna straight above the nozzle. The working robot drives to the
# station when its work tank is low and stops with its funnel under the nozzle.
#
# Each carrier folder has its own <p>_params.py with the carrier dimensions; this file holds what they share.
# Axes as the robot model: x = right, y = forward (towards the tractor / tow eye), z = up, ground = z 0, mm.
# =====================================================================

STATIONARY_FOLDER = os.path.dirname(os.path.abspath(__file__))
SIMPLE_FOLDER = os.path.join(os.path.dirname(STATIONARY_FOLDER), "simple")
if SIMPLE_FOLDER not in sys.path:
    sys.path.append(SIMPLE_FOLDER)

import mrs_params as S      # noqa: E402  simple variant: IBC, nozzle, receiver kit (single source of truth)

# ---------------------------------------------------------------------
# Liquid and IBC (the IBC shapes come from simple/mrs_parts.py, moved to IBC-local coordinates:
# origin = middle of the footprint on the underside of the pallet, 1200 along x, 1000 along y, valve on the -x face)
# ---------------------------------------------------------------------
liquid_density = S.liquid_density
liquid_viscosity = S.liquid_viscosity
ibc_nominal_l = S.ibc_nominal_l
ibc_kg = sum(S.ibc_kg.values())                 # 58
ibc_len = 2.0 * S.ibc_x                         # 1200
ibc_wid = S.ibc_y[1] - S.ibc_y[0]               # 1000
ibc_h = S.ibc_h                                 # 1160 (cap 10 mm higher)
IBC_LOCAL = (0.0, -S.IBC_CY, -S.IBC_Z0)          # translation robot coordinates of simple -> IBC local
valve_z = S.valve_z                             # 200 above the IBC base
VALVE_END = -S.bottle_x - S.valve_body[1] - S.valve_spigot[1]     # -664: end of the spigot (local x)
elbow_x = VALVE_END - 27.0                      # camlock elbow axis (local x), elbow points down
bottle_z0 = S.pallet_h                          # 145: bottom of the bottle above the IBC base
ibc_top = S.pallet_h + S.bottle_h + 10.0 + S.ibc_cap[3]           # 1180 with the cap
strap_w = S.strap_w
strap_t = S.strap_t
ratchet = S.ratchet

# ---------------------------------------------------------------------
# Working robot and docking (receiver kit as the simple variant)
# ---------------------------------------------------------------------
funnel_xy = S.funnel_xy                         # (0, -35) on the working robot
FUNNEL_RIM_Z = S.FUNNEL_RIM_Z                   # 1144
nozzle_tip_z = S.nozzle_tip_z                   # 1250: 106 mm above the funnel rim
worker_half_w = S.WORKER_OUTLINE[0]             # 500
dock_clear = 250.0                              # gap between the working robot and the widest part of the station
dock_round = 50.0                               # reach rounded up to

# ---------------------------------------------------------------------
# Control box: powder-coated steel enclosure IP55, front door with lock, rain roof. Local coordinates: origin = middle
# of the bottom face, x = width, door on the +y face. Suction port low on the -x face, discharge port high on the +x
# face. Contents: 24 V transfer pump (motor), LiFePO4 battery, DIN plate with controller, RTK receiver, radio,
# DC-DC / charger, fuses; flow meter and motorised ball valve in the discharge line.
# ---------------------------------------------------------------------
box = (600.0, 400.0, 450.0)                     # width (x), depth (y), height
box_wall = 2.0
box_roof = (25.0, 3.0)                          # overhang all round, thickness
box_door_inset = 25.0
box_foot = (40.0, 20.0)                         # 2 mounting rails under the box: width (y), height (in the box height)
pump_axis = (80.0, 110.0)                       # (y, z) local
pump_inlet_x = (-298.0, -250.0)                 # through the -x wall
pump_head_x = (-250.0, -170.0)
pump_motor_x = (-170.0, 40.0)
pump_head_d = 130.0
pump_motor_d = 100.0
pump_outlet_x = -210.0
discharge_z = 300.0                             # discharge line and port height (local)
flowmeter_x = (-110.0, 10.0)
flowmeter_d = 70.0
motor_valve_x = 120.0
battery = ((-130.0, 130.0), (-190.0, -20.0), (box_foot[1], box_foot[1] + 210.0))   # 25.6 V 50 Ah LiFePO4
din_plate = ((-270.0, 270.0), (-197.0, -194.0), (250.0, 420.0))
din_modules = (                                  # x0, x1, depth, z0, z1 (on the plate, towards +y)
    ("controller", -260.0, -110.0, 60.0, 290.0, 400.0),
    ("rtk_receiver", -95.0, 15.0, 40.0, 300.0, 380.0),
    ("radio", 30.0, 110.0, 35.0, 300.0, 370.0),
    ("dc_dc_charger", 125.0, 255.0, 55.0, 280.0, 410.0))
gland_d = 25.0
estop = (40.0, 30.0)                            # mushroom diameter, height (on the door)
port_len = 40.0                                 # bulkhead fittings outside the wall
SUCTION_PORT = (-box[0] / 2.0 - port_len, pump_axis[0], pump_axis[1])
DISCHARGE_PORT = (box[0] / 2.0 + port_len, pump_axis[0], discharge_z)

# ---------------------------------------------------------------------
# Mast, arm, drop pipe, nozzle, antenna (as the simple variant; the arm turns on the mast top:
# 0 = out to the left (-x), 90 = folded backwards (-y), 180 = out to the right, -90 = folded forwards)
# ---------------------------------------------------------------------
mast_tube = (80.0, 4.0)
arm_tube = S.arm_tube                           # 60 x 3
arm_z = S.arm_z                                 # 1965 .. 2025
arm_tip = S.arm_tip
arm_sleeve = S.arm_sleeve
pivot_pin = S.pivot_pin
top_plate = S.mast_top_plate                    # 130 x 10
lock_r = S.lock_r
mast_window = 60.0                              # hose window width
drop_pipe = S.drop_pipe
nozzle = S.nozzle
ant_stem = S.ant_stem
ant_dome = S.ant_dome
hose_od = S.hose_od
hose_d = S.hose_d
gusset_t = 10.0
beacon = (70.0, 160.0)                          # status beacon (green ready / amber pumping / red fault): d, h

# ---------------------------------------------------------------------
# Pump, battery, operation
# ---------------------------------------------------------------------
pump_kg = S.pump_kg
pump_eff = S.pump_eff
pump_q_fill = S.pump_q_fill                     # 120 l/min
pump_h0 = 18.0                                  # m shut-off head (same curve as the other variants, estimated)
pump_q0 = 190.0
battery_wh = 25.6 * 50.0                        # 1280 Wh
standby_w = 7.0                                 # RTK receiver 2 W, controller 2 W, radio 1.5 W, beacon, losses
solar_w = 100.0                                 # optional panel (not modelled)
box_kg = {"enclosure": 22.0, "battery": 12.0, "electronics": 3.0, "flow_valve": 3.5}

# Working robot (liquid fertilizer applicator advanced with the receiver kit)
work_width = S.work_width
dose_std = 505.0                                # l/ha
v_work = 0.75
v_head = 0.5                                    # m/s on the headland
v_dock = 0.3                                    # last metres to the nozzle
rx_tank_l = 147.0                               # work tank (simple: capacity_l("receiver"))
rx_refill_l = 120.0                             # the working robot comes when 27 l are left
t_dock = 25.0                                   # s: leave the turn, line up beside the station, stop, check
t_check = 0.5
t_close = 1.0
