import math
import os
import sys

# =====================================================================
# Stationary refill station on a dedicated IBC trailer - parameters
# A small single-axle trailer carries 1 or 2 standard 1000 l IBCs (valves forward). A tractor, pick-up or ATV parks
# it on the headland: jockey wheel down, two drop legs at the rear. On the A-frame: the control box (pump + motor,
# battery, controller, RTK receiver, radio) and the mast with the swinging arm; the RTK antenna sits straight above
# the nozzle. The working robot drives to the station when its work tank is low.
#
# Axes: x = right, y = forward (towards the tow eye), z = up, ground = z 0, mm. Origin = middle of the axle on the
# ground. Two configurations: cfg(1) and cfg(2). Common dimensions in ../stc_params.py.
# =====================================================================

FOLDER = os.path.dirname(os.path.abspath(__file__))
STATIONARY = os.path.dirname(FOLDER)
if STATIONARY not in sys.path:
    sys.path.insert(0, STATIONARY)

import stc_params as C       # noqa: E402

# ---------------------------------------------------------------------
# Running gear: rigid axle (square 70) bolted under the side rails, wheels outside the frame
# ---------------------------------------------------------------------
tyre = {1: (690.0, 264.0, 305.0, "10.0/80-12"), 2: (845.0, 295.0, 389.0, "11.5/80-15.3")}  # d, width, rim d
tyre_load = {1: 1030.0, 2: 1700.0}      # kg per tyre at 25 km/h (estimated, implement tyres)
axle_sq = 70.0
wheel_gap = 30.0                        # side rail -> tyre
guard = (40.0, 3.0)                     # mudguard: radial gap, thickness (width = tyre + 40)

# ---------------------------------------------------------------------
# Frame: side rails and front / rear rails 100 x 50 x 4 (100 high), cross members 80 x 40 x 3 (top flush),
# 3 mm floor plate. IBCs turned so that the 1200 side runs along the trailer and the valve points forward.
# ---------------------------------------------------------------------
rail = (50.0, 100.0, 4.0)               # width, height, wall
rail_x = (490.0, 540.0)                 # side rails (+-)
cross = (40.0, 80.0, 3.0)
cross_pitch = 450.0
floor_t = 3.0
ibc_gap = 250.0                         # between two IBCs: the rear IBC's valve and elbow
front_space = 260.0                     # deck in front of the (front) IBC: valve, elbow, hole to the header
rear_space = 40.0
ibc_offset = {1: 0.0, 2: 40.0}          # middle of the IBC group ahead of the axle (nose load)
deck_hole = 70.0                        # floor hole for the elbow / suction hose
header_x = 0.0                          # suction header under the floor (through the cross members)

# ---------------------------------------------------------------------
# A-frame drawbar with the control box and the mast
# ---------------------------------------------------------------------
a_len = 1800.0                          # from the front rail to the tow eye
a_x0 = 515.0                            # A-beams start at the front corners (beam centre)
box_gap = 300.0                         # front rail -> rear face of the control box (suction hose rises here)
box_x = 80.0                            # box shifted right so that both ports lie on x = 0 (box above the A-beams)
box_cross = (60.0, 40.0, 3.0)           # 2 cross members between the A-beams under the box
mast_gap = 160.0                        # front face of the box -> mast axis
mast_cross = (100.0, 100.0, 4.0)        # cross beam under the mast (y width, height, wall)
eye_ahead = 100.0                       # tow eye ring centre ahead of the A apex
jockey_ya = 1250.0                      # jockey wheel along the A-frame (from the front rail), left beam
leg_y = 60.0                            # drop legs: from the rear end, outside the side rails
transport_x = 700.0                     # arm locked for transport with the nozzle beside the IBC (x = -700)
lights = (380.0, 300.0, 130.0)          # rear light clusters: x, width, height


def cfg(n):
    """All derived dimensions for n IBCs (1 or 2)."""
    d, w, rim_d, size = tyre[n]
    r = d / 2.0
    c = {"n": n, "tyre_d": d, "tyre_w": w, "rim_d": rim_d, "tyre_size": size, "axle_z": r}
    c["rail_z"] = (r + axle_sq / 2.0, r + axle_sq / 2.0 + rail[1])
    c["deck_z"] = c["rail_z"][1] + floor_t                  # IBC base
    off = ibc_offset[n]
    if n == 1:
        centres = [off]
    else:
        h = 0.5 * (C.ibc_len + ibc_gap)
        centres = [off + h, off - h]
    c["ibc_y"] = centres                                    # front first
    c["deck_front"] = centres[0] + C.ibc_len / 2.0 + front_space
    c["deck_rear"] = centres[-1] - C.ibc_len / 2.0 - rear_space
    c["wheel_x"] = rail_x[1] + wheel_gap + w / 2.0
    c["guard_r"] = r + guard[0]
    c["guard_w"] = w + 40.0
    c["half_width"] = c["wheel_x"] + c["guard_w"] / 2.0 + guard[1]
    # elbows: IBC turned -90 deg, valve at local -x -> +y
    c["elbow_y"] = [y - C.elbow_x for y in centres]
    c["elbow_out_z"] = c["deck_z"] + C.valve_z - 45.0
    c["header_z"] = 0.5 * (c["rail_z"][0] + c["rail_z"][1])
    # cross members (between the side rails), avoiding nothing in particular
    y0, y1 = c["deck_rear"] + rail[0], c["deck_front"] - rail[0]
    k = max(1, int(math.ceil((y1 - y0) / cross_pitch)))
    c["cross_y"] = [y0 + (y1 - y0) * i / k for i in range(1, k)]
    # A-frame
    c["a_y0"] = c["deck_front"]
    c["eye_y"] = c["deck_front"] + a_len + eye_ahead
    c["eye_z"] = c["header_z"]
    c["box_y"] = c["deck_front"] + box_gap + C.box[0] / 2.0          # box turned 90 deg: width along y
    c["box_z"] = c["rail_z"][1]                                      # on the cross members (top flush)
    c["box_cross_y"] = (c["box_y"] - C.box[0] / 2.0 + 100.0, c["box_y"] + C.box[0] / 2.0 - 100.0)
    c["mast_y"] = c["box_y"] + C.box[0] / 2.0 + mast_gap
    c["reach"] = math.ceil((c["half_width"] + C.dock_clear + C.worker_half_w) / C.dock_round) * C.dock_round
    c["fold"] = math.degrees(math.acos(transport_x / c["reach"]))   # transport lock angle (left, backwards)
    c["jockey_y"] = c["deck_front"] + jockey_ya
    c["leg_y"] = c["deck_rear"] + leg_y
    return c


def a_x(c, y):
    """Centre x of the right A-beam at y (left = -)."""
    return a_x0 * (1.0 - (y - c["a_y0"]) / a_len)
