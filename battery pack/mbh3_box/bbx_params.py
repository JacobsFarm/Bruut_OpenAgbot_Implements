import math

# =====================================================================
# Battery rack MBH3+ - parameters
# An open rack for BatteryLabs MBH3+ drop-in batteries (14S 48 V 50 Ah, normally-off BMS, AS150U connector, own
# enclosure IP53-64) on the Bruut OpenAgbot (standard robot). The battery is its own housing, so no closed box: a tray
# with guides holds it, a hinged hold-down bar keeps it in. The tray is built from slot segments of 100 mm (one
# battery each, = 2 steps of the 50 mm hole grid) between two end frames: 2 batteries now, 3 or 4 by bolting in more
# segments. One battery at a time is swapped (hot-swap, the BMS does the master/slave on CAN).
# Three ideas for where the rack goes (CONCEPTS):
#   top     on top of the frame, on 2 cross rails over the inner upper beams; batteries upright, lift out from above
#   well    sunk in the centre of the frame, hanging on 2 cross rails under the inner upper beams
#   saddle  a cradle per side under the upper beams between the wheels; batteries lying on edge, slide out sideways
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py" and the model, that folder is not in git)
# ---------------------------------------------------------------------
robot_axle_y = 500.0
robot_wheel_x = 375.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_steer_deg = 30.0
robot_upper_inner_x = (305.0, 345.0)    # inner upper beams (y direction), per side
robot_upper_outer_x = (405.0, 445.0)
robot_upper_z = (659.0, 699.0)
robot_lower_inner_y = (405.0, 445.0)    # inner lower beams (x direction), front and rear
robot_lower_z = (619.0, 659.0)
grid = 50.0
m10_hole = 10.4
robot_mass = 160.0                      # kg, estimated

# ---------------------------------------------------------------------
# Battery: BatteryLabs MBH3+ (SKU 31107), placeholder without details
# local frame: x = width 265, y = thickness 82, z = height; origin = centre of the bottom face
# from MBH3+_BSI_AS150U_mockup.STEP: body 265 x 82 x 383, handle and connector on top, 409.6 overall
# ---------------------------------------------------------------------
bat_body = (265.0, 82.0, 383.0)
bat_frame = 3.0                         # dark end frame, sticks out this much around the panels
bat_handle = (122.0, 24.0, 26.6)        # x, y, height above the body
bat_connector = (17.4, 32.5, 14.4)      # AS150U-M socket, at the left of the top face
bat_connector_x = -94.0                 # centre, from the battery centre
bat_height = bat_body[2] + bat_handle[2]    # 409.6
bat_kg = 11.8                           # MBH3+ (sheet: 10.5 - 11.8 kg)
bat_v = 51.1
bat_ah = 50.0
bat_cont_a = 60.0
bat_peak_a = 100.0
bat_price_eur = 557.85                  # offer 46325020, excl. VAT
dod = 0.9                               # usable depth of discharge

# ---------------------------------------------------------------------
# Rack: tray segments (alu 4 mm, low side lips), HDPE separators, end frames of 30 x 30 tube, side guides,
# a hinged hold-down bar over the tops of the batteries
# ---------------------------------------------------------------------
slot_pitch = 100.0                      # = 2 grid steps: one more battery moves each rail one hole out
separator = 12.0                        # HDPE guide between batteries
separator_h = 300.0
pad = 10.0                              # rubber mat on the tray
side_play = 7.5                         # battery width 265 -> 280 between the guides
tray_t = 4.0
tray_lip = 40.0                         # height of the side lips above the tray
tube = 30.0                             # end frames: square alu tube 30 x 30 x 2
guide = (30.0, 10.0)                    # side guide (flat bar on edge): height, thickness
guide_z = 190.0                         # bottom of the side guides above the battery bottom
hold = (30.0, 6.0)                      # hold-down bar: width, thickness, with a rubber strip
hold_x = 110.0                          # centre of the hold-down bar: right of the handle (x +-61)
hinge_d = 10.0
combiner = (140.0, 70.0, 90.0)          # bus box with an AS150U-F socket per slot, fuse, CAN, on the end frame

# upright racks (top, well): battery x = robot x, battery thickness along y
inner_x = bat_body[0] + 2 * side_play
tray_x = inner_x / 2.0 + guide[1]       # half width of the tray: guides stand on its edge

# cross rails: tube 40 x 40 x 3 along x over / under the two inner upper beams, 1 x M10 per beam
rail = (40.0, 40.0, 3.0)
rail_x = robot_upper_inner_x[1]         # rails run x -345..345
ear = (60.0, 5.0)                       # well: ears on the top cross tubes resting on the rails: length (y), thickness

# saddle: batteries lying on their long edge, length along y, thickness along x, 1 or 2 per side.
# Cradle per segment: floor and roof plate; inner plate per side; end posts; 2 hinged retaining bars on the outside
saddle_x_in = 255.0                     # inner face of the cradle (right side; left mirrored): 2 slots stay inside
                                        # the wheel units (x 489)
saddle_inner_y = bat_height + 2 * 12.0
saddle_inner_z = pad + bat_body[0] + 12.0
saddle_plate = 4.0
saddle_bar_y = (-120.0, 120.0)          # retaining bars on the outer side
saddle_hanger_y = (-150.0, 150.0)
saddle_hanger = (40.0, 8.0)             # flat bar under both upper beams of the side, with 40 mm spacer blocks

# closed cabinet (alu 3 mm): batteries lying flat on shelves, one level of 100 mm per battery (82 + shelf 4 + 14 play),
# handle and plug towards a drop-down door per level (hinged at the bottom, it is also the slide-out ramp).
# Local frame: u = slide direction (door at +u), v = width, z = up; it grows in height, the mount stays the same.
#   cabinet_well  hanging in the centre under the frame, doors to the right (u = +x), swap from the side
#   cabinet_top   on 2 cross rails over the inner upper beams, doors to the rear (u = -y)
cab_wall = 3.0
cab_pitch = 100.0
cab_shelf = 4.0
cab_inner_u = bat_height + 2 * 10.0     # 429.6
cab_inner_v = bat_body[0] + 2 * side_play   # 280
cab_flange = (15.0, 4.0)                # bolted flange ring between two levels: width, thickness
cab_door = 3.0
cab_hinge_d = 8.0
cab_rail_y = {"cabinet_well": 200.0, "cabinet_top": 150.0}
cab_turn = {"cabinet_well": 0.0, "cabinet_top": -90.0}      # rotation of the local frame about z (deg)

# wooden box (wood_side, wood_side_mu3): 18 mm multiplex, 2 compartments (one battery each, upright, plugs up), a
# divider between them, a loose lid with 2 hinges and a hasp; it stands on the two upper beams of one side (right),
# 4 x M10 through the bottom and the beams; cables out through a slot at the top of the rear wall, under the lid.
#   wood_side      MBH3+: side by side across (x), width along y, plug at the rear
#   wood_side_mu3  MU3+ (MegaUMPF3+): one behind the other along y (across it would be 408 wide), plug at the rear
wood_t = 18.0
wood_play = 5.0                         # around the battery in its compartment (foam strips)
wood_mat = 5.0                          # EPDM mat on the bottom
wood_head = 110.0                       # above the battery: AS150U plug with its cable bend
wood_n = 2
wood_x_c = 370.0                        # centre of the box over the right upper beams (x 305..445); stays inside x 489
wood_y_c = 0.0                          # centred between the axles
wood_lid_over = 10.0
wood_slot = (80.0, 40.0)                # cable slot in the rear wall, at the top: width (x), height
plywood = 0.68e-6                       # birch multiplex, kg/mm3

# MU3+ (BatteryLabs MegaUMPF3+, flyer Flyer_MU3+.pdf): 48 V Li-ion 14S 50 Ah (57.5 Ah option), IP67, AS150U on top.
# local frame: x = 167, y = 197, z = up; origin = centre of the bottom face. Rubber bumper at the bottom and a rubber
# frame round the top; the handle and the socket sit in the recessed top, the handle 9.5 above the frame.
mu3_size = (167.0, 197.0, 292.4)
mu3_handle_up = 9.5
mu3_height = mu3_size[2] + mu3_handle_up    # 301.9
mu3_bumper = (30.0, 30.0)               # height of the bottom bumper and of the top frame
mu3_inset = 5.0                         # silver body inside the bumpers, per side
mu3_recess = 15.0                       # top recess depth and rim width of the top frame
mu3_socket_y = 55.0                     # AS150U socket, from the centre (local +y)
mu3_kg = 11.5                           # flyer: 7.3 - 11.8 kg over the range; 48 V 50 Ah near the top (estimated)
mu3_ah = 50.0

WOOD = {
    # cells along x or y; compartment (x, y) inside; battery body height; turn of the battery (deg about z)
    "wood_side": {"along": "x", "cell": (bat_body[1] + 2 * wood_play, bat_body[0] + 2 * wood_play),
                  "bat_h": bat_body[2], "turn": 90.0, "bolt_y": (-100.0, 100.0), "kind": "MBH3+"},
    "wood_side_mu3": {"along": "y", "cell": (mu3_size[0] + 2 * wood_play, mu3_size[1] + 2 * wood_play),
                      "bat_h": mu3_size[2], "turn": 180.0, "bolt_y": (-150.0, 150.0), "kind": "MU3+"},
}

CONCEPTS = ("top", "well", "saddle", "cabinet_well", "cabinet_top", "wood_side", "wood_side_mu3")
CONCEPT_NS = {"wood_side": (2,), "wood_side_mu3": (2,)}    # sizes that exist per concept (default 2, 3, 4)


def wood_inner_z(concept):
    return wood_mat + WOOD[concept]["bat_h"] + wood_head


def wood_outer(concept="wood_side"):
    """(x0, x1, y0, y1, z0, z_top of the walls) of the wooden box."""
    w = wood_t
    cx, cy = WOOD[concept]["cell"]
    if WOOD[concept]["along"] == "x":
        ox, oy = wood_n * cx + (wood_n + 1) * w, cy + 2 * w
    else:
        ox, oy = cx + 2 * w, wood_n * cy + (wood_n + 1) * w
    z0 = robot_upper_z[1]
    return (wood_x_c - ox / 2.0, wood_x_c + ox / 2.0, wood_y_c - oy / 2.0, wood_y_c + oy / 2.0,
            z0, z0 + w + wood_inner_z(concept))


def wood_cells(concept):
    """Inner (x0, x1, y0, y1) of each compartment."""
    x0, _, y0, _, _, _ = wood_outer(concept)
    w = wood_t
    cx, cy = WOOD[concept]["cell"]
    out = []
    for i in range(wood_n):
        if WOOD[concept]["along"] == "x":
            xa, ya = x0 + w + i * (cx + w), y0 + w
        else:
            xa, ya = x0 + w, y0 + w + i * (cy + w)
        out.append((xa, xa + cx, ya, ya + cy))
    return out

# ---------------------------------------------------------------------
# Work (bbx_calc)
# ---------------------------------------------------------------------
g = 9.81
alu = 2.7e-6
steel = 7.85e-6
hdpe = 0.96e-6
rubber = 1.2e-6
charger_a = 25.0                        # max charge current per battery (sheet)
# average electric power of the implements at their working speed (from battery pack/simple/bpk_params.py)
LOADS_W = {"inter_row_hoe": 1018.0, "grassland_harrow": 1260.0, "grassland_aerator": 520.0,
           "three_point_hitch_cultivator": 1077.0, "push_blade": 880.0, "crate_carrier_shuttle": 250.0}
base_load_w = 60.0                      # computer, GNSS, steering (estimated)
peak_bus_a = 90.0                       # 4 hub motors at full pull (estimated)


def bat_wh():
    return bat_v * bat_ah


def rack_half(n):
    """Half length of the battery space (along the slots)."""
    return n * slot_pitch / 2.0


def slot_centres(n):
    """Centre of each slot along the rack, rack centred on 0."""
    return [-n * slot_pitch / 2.0 + slot_pitch / 2.0 + i * slot_pitch for i in range(n)]


def rail_y(n, concept):
    """Rail centres (y): outside the rack ends (well, hanging on its ears) or under the outer slots (top).
    Both on the 50 mm grid; one slot more moves each rail one hole out. The cabinet grows in height: fixed rails."""
    if concept in cab_rail_y:
        return (-cab_rail_y[concept], cab_rail_y[concept])
    if concept == "well":
        return (-(rack_half(n) + grid), rack_half(n) + grid)
    return (-(rack_half(n) - grid), rack_half(n) - grid)


def rack_z(concept):
    """(bottom of the tray, bottom of the batteries, top of the battery bodies = top of the end frames)."""
    if concept == "well":
        top = robot_lower_z[1] + 21.0                   # body tops 20 mm under the top of the frame
        zb = top - bat_body[2]
        return zb - pad - tray_t, zb, top
    z0 = robot_upper_z[1] + rail[1]
    zb = z0 + tray_t + pad
    return z0, zb, zb + bat_body[2]


def cab_height(n):
    return 2 * cab_wall + n * cab_pitch


def cab_z0(n, concept):
    """Bottom of the cabinet: hanging with its roof flush with the ears on the rails (well), or on the rails (top)."""
    if concept == "cabinet_well":
        return robot_upper_z[0] + ear[1] - cab_height(n)
    return robot_upper_z[1] + rail[1]


def saddle_split(n):
    """Batteries per side (left, right): 2 -> 1 + 1, 3 -> 1 + 2, 4 -> 2 + 2."""
    return n // 2, n - n // 2


def saddle_z():
    """(bottom of the floor plate, top of the roof plate): 2 mm under the hanger bar (spacer 40, bar 8)."""
    top = robot_upper_z[0] - 40.0 - saddle_hanger[1] - 2.0
    return top - 2 * saddle_plate - saddle_inner_z, top
