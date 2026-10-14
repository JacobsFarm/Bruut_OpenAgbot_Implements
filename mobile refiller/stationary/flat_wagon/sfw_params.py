import math
import os
import sys

# =====================================================================
# Stationary refill station on a standard flat wagon (bale wagon) - parameters
# A standard two-axle flat wagon (turntable steering, 8 x 2.48 m deck) carries rows of standard 1000 l IBCs, two
# across, valves to the rear. A suction header runs along the middle of the deck to the rear and down through the
# deck to the control box (pump + motor, battery, controller, RTK receiver, radio), which hangs under the deck
# behind the rear axle. A small skid with the mast stands on the rear left corner of the deck; the arm swings out
# to the left with the drop pipe, the nozzle and the RTK antenna. The wagon itself only gets two holes in the deck
# and two box hangers.
#
# Axes: x = right, y = forward (drawbar), z = up, ground = z 0, mm. Origin = middle of the deck on the ground.
# The wagon is modelled simplified (no brakes, no lights wiring, springs as blocks). Common dimensions in
# ../stc_params.py.
# =====================================================================

FOLDER = os.path.dirname(os.path.abspath(__file__))
STATIONARY = os.path.dirname(FOLDER)
if STATIONARY not in sys.path:
    sys.path.insert(0, STATIONARY)

import stc_params as C       # noqa: E402

# ---------------------------------------------------------------------
# Wagon (estimated from a typical 8 m bale wagon)
# ---------------------------------------------------------------------
deck_l = 8000.0
deck_w = 2480.0
deck_top = 1250.0
deck_t = 5.0                            # chequer plate
border = (200.0, 5.0)                   # side and end profile: height, thickness
cross = (50.0, 100.0, 4.0)              # cross members under the plate: width (y), height, wall
cross_pitch = 600.0
beam = (100.0, 200.0, 8.5, 5.6)         # IPE 200 main beams: flange width, height, flange, web
beam_x = 450.0
axle_y = 2300.0                         # front axle at +2300 (turntable), rear at -2300
axle_sq = (120.0, 12.0)                 # square hollow axle beam, wall
tyre = (940.0, 450.0, 432.0, "500/50-17")   # d, width, rim d
wheel_x = deck_w / 2.0 - tyre[1] / 2.0 - 25.0
turntable = (1000.0, 100.0, 30.0)       # ring diameter, ring width, height of each ring
bolster = (1100.0, 160.0, 6.0)          # front: axle -> lower ring, x length, y width, wall
spring = (80.0, 1000.0, 80.0)           # rear leaf springs: width, length, height
hanger_t = 12.0
drawbar = (1900.0, 400.0)               # length from the front axle, half spread at the axle
eye_ahead = 100.0
wagon_payload = 10000.0                 # kg (typical for this size, estimated)
wagon_kg_est = 2600.0                   # dry wagon, for comparison with the model

# ---------------------------------------------------------------------
# IBCs: rows of two (1000 across, 1200 along, valve to the rear), centred at x = +-640: 280 mm gap in the middle
# for the header
# ---------------------------------------------------------------------
n_rows = 3
ibc_x = 640.0
row_gap = 500.0                         # between the rows: valve, elbow and the hoses to the header
skid = ((-1230.0, -430.0), (-3990.0, -3390.0), 40.0)    # mast skid: x, y, height (80 x 40 x 3 frame)
valve_clear = 500.0                     # skid front -> rear face of the first row
header_z = deck_top + 40.0
header_hole_y = -3150.0                 # header goes down through the deck here (x = 0)
deck_hole = 70.0

# ---------------------------------------------------------------------
# Control box under the deck, behind the rear axle, turned 180 deg (door to the rear), on two supports hung from
# the main beams
# ---------------------------------------------------------------------
box_y = -3500.0
box_sup = (40.0, 40.0, 3.0)
hanger = (40.0, 8.0)                    # flat bar

# ---------------------------------------------------------------------
# Mast on the skid (rear left corner of the deck), arm higher than the IBC tops so the antenna sees the sky
# ---------------------------------------------------------------------
mast_xy = (-1160.0, -3850.0)
mast_base = (160.0, 12.0)
arm_z = (2460.0, 2520.0)
nozzle_z = C.nozzle_tip_z + 20.0        # 1270: 20 mm above the deck when the arm is folded forwards
dock_x = None                           # computed: nozzle x when docking on the left


def ibc_top():
    return deck_top + C.ibc_top


def rows(n=None):
    """Row centres (y), rear row first: centred between the axles, but not closer to the mast skid than
    valve_clear."""
    n = n_rows if n is None else n
    pitch = C.ibc_len + row_gap
    y_min = skid[1][1] + valve_clear + C.ibc_len / 2.0
    y0 = max(y_min, -0.5 * (n - 1) * pitch)
    return [y0 + i * pitch for i in range(n)]


def ibc_positions():
    return [(sx * ibc_x, y) for y in rows() for sx in (-1, 1)]


def nozzle_x():
    half = deck_w / 2.0
    return -math.ceil((half + C.dock_clear + C.worker_half_w) / C.dock_round) * C.dock_round


def reach():
    return mast_xy[0] - nozzle_x()


def box_z():
    """Box hangs with its roof just under the main beams."""
    return deck_top - deck_t - cross[1] - beam[1] - 10.0 - C.box[2] - C.box_roof[1]
