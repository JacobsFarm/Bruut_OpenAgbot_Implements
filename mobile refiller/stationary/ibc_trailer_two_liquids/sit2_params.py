"""Stationary refill station on the IBC trailer, two liquids - parameters.

The 2-IBC trailer of ../ibc_trailer (cfg(2): same frame, axle, tyres, drawbar, parking gear) with one liquid per IBC:
IBC 1 (front) holds liquid A (blue), IBC 2 (rear) liquid B (orange). Each IBC has its own suction line (two lines side
by side under the floor) and its own pump; both pumps sit in one deeper control box with one set of electronics. Both
discharge hoses run side by side up the rear face of the mast and along the arm to two drop pipes with a drip-stop
nozzle each, 455 mm apart (the funnel pitch of the precision applicator V4): the working robot is filled with both
liquids in one stop.

Axes: x = right, y = forward (towards the tow eye), z = up, ground = z 0, mm. Origin = middle of the axle on the
ground (as ../ibc_trailer).
"""
import os
import sys

FOLDER = os.path.dirname(os.path.abspath(__file__))
STATIONARY = os.path.dirname(FOLDER)
TRAILER = os.path.join(STATIONARY, "ibc_trailer")
for _f in (STATIONARY, TRAILER):
    if _f not in sys.path:
        sys.path.insert(0, _f)

import stc_params as C      # noqa: E402
import sit_params as T      # noqa: E402

N_IBC = 2
LIQUIDS = ("A", "B")         # IBC 1 (front) = A, IBC 2 (rear) = B

# ---------------------------------------------------------------------
# Working robot: precision applicator V4 (combined_v4): funnels 455 apart (A right, B left), rim z 1354
# ---------------------------------------------------------------------
funnel_pitch = 455.0
funnel_y = 170.0
funnel_rim_z = 1354.0
nozzle_tip_z = funnel_rim_z + 106.0         # 1460

# ---------------------------------------------------------------------
# Suction: two lines under the floor, A at x 0 (as ../ibc_trailer), B beside it
# ---------------------------------------------------------------------
header_x = {"A": 0.0, "B": -120.0}

# ---------------------------------------------------------------------
# Control box with two pumps (box-local coordinates as ../stc_params: x = width, door on +y). The box of the
# 1-pump station is 400 deep; this one is 660 deep (y -200 .. 460): pump A at y 80 (as before), pump B 250 further
# towards the door, each with its own flow meter and motorised valve. Battery and DIN plate as before.
# ---------------------------------------------------------------------
box_y = (-200.0, 460.0)
pump_dy = {"A": 0.0, "B": 250.0}
box_x = 205.0                                # box shifted right: discharge (and suction) ports A at x 125, B at -125
box_rail_y = (-160.0, 420.0)                 # 2 mounting rails under the box (local y)
pump_b_kg = C.pump_kg + 3.5                  # second pump + flow meter + valve
box_extra_kg = 9.0                           # deeper enclosure

# ---------------------------------------------------------------------
# Lifting arm: the arm sits on a sleeve that slides (and swings) on a round mast, lifted by an electric linear
# actuator. Low: nozzle tips at 1460 for the working robot (as the other stations). High: 706 mm up, nozzle tips at
# 2166, 106 mm over the fill funnels (rim z 2060) on the bridge of the mobile refiller with two IBCs, which then stops
# beside the trailer the way the working robot does.
# ---------------------------------------------------------------------
refiller_funnel_rim_z = 2060.0               # simple_two_ibc: FILL_RIM_Z
lift_high = refiller_funnel_rim_z + 106.0 - nozzle_tip_z     # 706
mast_round = (114.3, 5.0)                    # round mast tube
mast_top_extra = 80.0                        # mast above the top of the sleeve in the high position
sleeve = (140.0, 6.0, 150.0, 50.0)           # outside d, wall, length below the arm, above the arm
base_plate = (220.0, 12.0)                   # mast foot plate on the mast cross beam
actuator = (80.0, 30.0, 950.0, 860.0)        # body d, rod d, body length, rod length (stroke 706)
actuator_dy = 110.0                          # actuator axis in front of the mast axis (+y)
collar = (22.0, 20.0)                        # thrust collar under the sleeve: radial width, height

# ---------------------------------------------------------------------
# Hoses up the rear face of the mast (side by side in x), a slack loop up to the arm (it lifts), along the -y side
# of the arm
# ---------------------------------------------------------------------
mast_hose_off = 100.0                        # hose centre behind the mast axis (sleeve radius 70 + hose 24 + 6)
mast_hose_x = {"A": 27.0, "B": -27.0}        # A on the right half of the face (from port A), B on the left
arm_lane_dy = {"A": -140.0, "B": -62.0}      # along the arm (-y side): B next to the arm, A outside it (A crosses
                                             # over B at the mast top)
fixed_top_z = 1600.0                         # fixed hoses end here (clamped to the mast); a slack loop goes up
loop_side = {"A": 1.0, "B": -1.0}            # the slack loop of A bows out to the right, B to the left
arm_entry_dz = 80.0                          # the arm hose starts this far under the lane height


def cfg():
    """Trailer dimensions of ../ibc_trailer for 2 IBCs, plus the mast specs of the two nozzles."""
    c = T.cfg(N_IBC)
    c["reach_A"] = c["reach"] - funnel_pitch / 2.0     # funnel A (right of the working robot) is the near one
    c["reach_B"] = c["reach"] + funnel_pitch / 2.0
    return c
