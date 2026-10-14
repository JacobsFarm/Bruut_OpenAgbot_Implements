import math
import os
import sys

# =====================================================================
# Stationary refill station in a three-point-linkage frame - parameters
# A welded frame with four legs carries one standard 1000 l IBC. The tractor lifts it on its three-point linkage
# (category 2), drives it to the headland and sets it down on its legs. The control box (pump + motor, battery,
# controller, RTK receiver, radio) hangs protected under the platform; the mast is also the hitch tower: the top
# link attaches to it and the arm with the drop pipe and the RTK antenna turns on its top.
#
# Axes: x = right, y = forward (towards the tractor), z = up, ground = z 0, mm. Origin = middle of the IBC
# footprint on the ground. Common dimensions in ../stc_params.py.
# =====================================================================

FOLDER = os.path.dirname(os.path.abspath(__file__))
STATIONARY = os.path.dirname(FOLDER)
if STATIONARY not in sys.path:
    sys.path.insert(0, STATIONARY)

import stc_params as C       # noqa: E402

# ---------------------------------------------------------------------
# Frame: platform of 80 x 40 x 3 (lying) on four legs 60 x 60 x 4; the IBC (valve to the right) stands on the side
# rails; a lower frame 60 x 40 x 3 between the legs carries the control box.
# ---------------------------------------------------------------------
plat_z = 650.0                          # top of the platform = IBC base
rail = (80.0, 40.0, 3.0)                # width (lying), height, wall
side_x = (560.0, 640.0)                 # side rails under the pallet edges (+-)
end_y = (500.0, 560.0)                  # front / rear rails outside the pallet (+-), 60 wide
leg = (60.0, 4.0)
leg_xy = (610.0, 530.0)                 # leg axes (+-)
foot = (160.0, 10.0)
low_z = (110.0, 150.0)                  # lower cross rails (y = +-530) and box supports (top flush)
box_sup_x = 250.0                       # 2 box supports along y (+-), 40 x 40 x 3
box_sup = (40.0, 40.0, 3.0)
brace_d = 42.0                          # side and rear diagonal braces (round tube)

# ---------------------------------------------------------------------
# Three-point hitch, category 2 (ISO 730): lower pins 28 mm, 825 mm apart (shoulders), top link pin 25 mm,
# mast height 610 mm. The mast (100 x 100 x 5) is the hitch tower.
# ---------------------------------------------------------------------
cat2_spread = 825.0
lower_pin = (28.0, 90.0)                # diameter, length outside the plate
pin_collar = (45.0, 8.0)
lower_pin_yz = (680.0, 350.0)           # with the frame on its legs
hitch_plate = (12.0, (500.0, 720.0), (low_z[0], plat_z))   # thickness, y range, z range
mast_height_iso = 610.0                 # lower pins -> top link pin
top_plate = (12.0, 52.0, 120.0, 130.0)  # thickness, inner gap, length (y), height
top_pin = 25.0
mast_tube = (100.0, 5.0)
mast_y = 670.0                          # mast axis
mast_foot = (80.0, 80.0, 4.0)           # cross beam under the mast between the hitch plates (y width, height)
in_z = 450.0                            # discharge hose enters the mast here (-x face)

# ---------------------------------------------------------------------
# Control box under the platform, turned 180 deg: door to the rear, suction port to the right (valve side)
# ---------------------------------------------------------------------
box_xyz = (0.0, 0.0, low_z[1])

# ---------------------------------------------------------------------
# Tractor (for the calculation only; a 75 kW tractor as an example)
# ---------------------------------------------------------------------
tractor_kg = 4300.0
tractor_front_kg = 1750.0
tractor_wheelbase = 2450.0
tractor_rear_to_pins = 1050.0           # rear axle -> lower link points
lift_capacity_610 = 3500.0              # kg at 610 mm behind the lower link points (example)
front_share_min = 0.20                  # front axle at least 20 % of the combination (steering, braking)
lift_height = 300.0                     # transport: frame lifted this much


def ibc_top():
    return plat_z + C.ibc_top


def half_widths():
    """Left (legs, feet) and right (valve, elbow, suction hose) extent of the station below the arm."""
    left = leg_xy[0] + foot[0] / 2.0
    right = max(left, -C.elbow_x + 31.0 + C.hose_od / 2.0)
    return left, right


def reach():
    return math.ceil((max(half_widths()) + C.dock_clear + C.worker_half_w) / C.dock_round) * C.dock_round


def top_pin_z():
    return lower_pin_yz[1] + mast_height_iso
