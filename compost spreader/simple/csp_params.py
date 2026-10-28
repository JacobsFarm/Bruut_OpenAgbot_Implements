import math

# =====================================================================
# Compost spreader (simple) - parameters
# Bin on the upper beams of the Bruut OpenAgbot (standard robot) with a moving floor belt that carries the compost
# backwards under a slide gate to a beater rotor behind the robot. The beater breaks the compost up and throws it down
# in an even layer over the bed between the wheels (top-dressing of market-garden beds, grassland, orchard strips).
# Dose = belt speed x gate opening, set by the robot from the driving speed and a task map.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py" and the model, that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_upper_beam_x = (325.0, 425.0)     # centres of the upper beams per side (40 wide), y -650..650
robot_upper_beam_z = (659.0, 699.0)
robot_front_stack_y = 405.0     # steering plates and motors of the front units start here (to z 1032)
robot_rear_bolts = (-584.0, -416.0, 705.0)   # frame bolts of the rear units stick out to z 705
robot_mass = 160.0              # kg, estimated
robot_cg_y = 0.0
robot_cg_z = 380.0              # estimated (batteries low in the frame)
m10_hole = 10.4

# ---------------------------------------------------------------------
# Bearers: 3 x tube 40 x 40 x 3 across, on the upper beams, 4 x M10 each (clear of the rear unit bolts)
# ---------------------------------------------------------------------
bearer = 40.0
bearer_y = (-330.0, -20.0, 180.0)       # centres
bearer_x = 525.0                        # half length: under the feet of the side plates
bearer_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + bearer)

# ---------------------------------------------------------------------
# Conveyor frame: 2 side plates 4 mm, bin walls in the lower part, carry the drums and the beater
# Outline in (y, z); the plates stand on the bearers on angle feet
# ---------------------------------------------------------------------
side_t = 4.0                            # folded sheet, stiffened by the flare walls and the cross tube
side_x = 475.0                          # inside face of the side plates (x = +-475)
side_pts = ((333.0, bearer_z[1]), (-800.0, bearer_z[1]), (-880.0, 640.0), (-1210.0, 640.0), (-1210.0, 1000.0),
            (-730.0, 1060.0), (333.0, 1060.0))
foot = (40.0, 4.0, 90.0)                # angle 40 x 40 x 4, 90 long, outside the plates at every bearer

# ---------------------------------------------------------------------
# Floor belt: rubber conveyor belt 920 wide, 5 thick (2-ply with cleats drawn flat) round 2 drums O100
# Rear drum drives (pulls the top run backwards), front drum is the take-up (slotted bearings)
# ---------------------------------------------------------------------
belt_w = 920.0
belt_t = 5.0
drum_d = 100.0
drum_len = 930.0
drum_z = 815.0
drum_y_front = 270.0
drum_y_rear = -820.0
shaft_d = 25.0
belt_top = drum_z + drum_d / 2.0 + belt_t      # top face of the top run
bed_t = 10.0                            # UHMW-PE slide bed under the top run
bed_gap = 1.0
bed_y = (drum_y_rear + drum_d / 2.0 + 10.0, drum_y_front - drum_d / 2.0 - 10.0)
bed_rail = (20.0, 20.0)                 # angle strips welded inside the side plates, carry the bed

# bearings UCFL204 (shaft 20..25), flange square 86, outside the plates
brg_sq = 86.0
brg_flange = 13.0
brg_body_d = 62.0
brg_depth = 33.0

# ---------------------------------------------------------------------
# Bin: vertical side plates up to z 1060, flared walls 3 mm up to z 1160, front wall, fixed rear wall above the gate
# ---------------------------------------------------------------------
bin_y = (-720.0, 333.0)                 # rear wall (gate) .. front wall
bin_flare_z = (1060.0, 1160.0)
bin_top_x = 560.0                       # half width at the top
wall_t = 3.0
skirt_t = 8.0                           # rubber skirts from the side plate down onto the belt edge
skirt_low_x = 450.0                     # inner bottom edge of the skirt (belt edge at 460)
skirt_top_z = 965.0

# Slide gate behind the rear wall: plate 6 mm, 940 x 300, set by hand in 2 slotted guides with 2 star knobs
gate_t = 6.0
gate_y = (-729.0, -723.0)
gate_w = 940.0
gate_h = 300.0
gate_open = 80.0                        # default opening above the belt (mm)
GATE_RANGE = (30.0, 150.0)
guide = (20.0, 4.0)                     # flat bars behind the gate edges, welded to the side plates
knob_d = 50.0

# ---------------------------------------------------------------------
# Beater: tube O114 with 4 rows of 7 paddles (flat 50 x 8), tip O280, stub shafts O30 in 2 x UCFL206
# ---------------------------------------------------------------------
beater_y = -1040.0
beater_z = 820.0
beater_tube = 114.0
beater_len = 930.0
beater_tip_r = 140.0
paddle = (50.0, 8.0)
paddle_rows = 4
paddles_per_row = 7
beater_shaft = 30.0
beater_brg_sq = 108.0
beater_brg_flange = 14.0
beater_brg_body_d = 80.0
beater_brg_depth = 40.0
hood_r = 175.0                          # deflector hood over and behind the rotor, 3 mm
hood_ang = (95.0, 215.0)                # degrees in the y-z plane from +y towards +z
top_tube = 40.0                         # cross tube 40 x 40 x 3 on top of the hood, stiffens the rear

# ---------------------------------------------------------------------
# Drives
# ---------------------------------------------------------------------
# belt: 24 V worm gearmotor 60:1 (~120 W) on the rear drum shaft, left side, torque arm to the side plate
belt_gm_box = (90.0, 110.0, 110.0)      # x, y, z of the worm box
belt_motor_d = 80.0
belt_motor_l = 150.0
# beater: 48 V BLDC 1 kW, 1500 rpm, poly-V belt 1 : 5 down to 300 rpm, right side, motor over the rear drum
beater_motor_d = 110.0
beater_motor_l = 170.0
beater_motor_pos = (-850.0, 990.0)      # (y, z) motor axis
guard = (40.0, 2.0)                     # belt guard: depth (x) and sheet thickness
pulley_small = 50.0
pulley_big = 250.0

# ---------------------------------------------------------------------
# Load and work (csp_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
uhmw = 0.94e-6
rubber = 1.3e-6
alu = 2.7e-6
payload_max = 150.0                     # kg, what the robot carries on the top (estimated, as the crate carrier)
COMPOST = {                             # bulk density kg/m3 (estimated, depends on moisture)
    "green_compost_dry": 450.0,
    "green_compost_moist": 600.0,
    "mushroom_compost": 400.0,
    "farmyard_manure_rotted": 750.0,
}
compost_ref = "green_compost_moist"
DOSES = {                               # kg/m2 (1 kg/m2 = 10 t/ha), spread width
    "grassland_topdress": 1.0,
    "orchard_strip": 2.0,
    "market_garden_bed": 3.0,
}
fill_factor = 0.85                      # how well the belt is filled under the gate (estimated)
spread_w = 1.1                          # m, width of the layer behind the beater (bed between the wheel tracks)
drive_speed = {"grassland_topdress": 0.8, "orchard_strip": 0.5, "market_garden_bed": 0.3}   # m/s
belt_v_max = 30.0                       # mm/s (drum 3.8 rpm with the 60:1 worm and a 1:4 chain)
mu_belt_bed = 0.25                      # rubber belt on UHMW, estimated
mu_wall = 0.5                           # compost on steel walls, estimated
k_wall = 0.4                            # lateral pressure ratio of compost on the walls (estimated)
e_beater = 0.6                          # kJ/kg to break up and throw the compost (estimated from muck spreaders)
p_beater_idle = 150.0                   # W
beater_rpm = 300.0
eta_drive = 0.75
crr = 0.06
mu_tyre = 0.45
hub_torque_nom = 55.0
r_load = 0.20
n_driven = 4
battery_wh = 1900.0
track_half = robot_wheel_x
wheelbase_half = robot_axle_y
refill_s = 240.0                        # fill the bin from a heap with a front loader / pallet fork (estimated)
headland_m = 80.0                       # average drive from the heap to the bed and back (estimated)
# from build_csp.mass_properties() (update after a change of the model)
MODEL_MASS = {"spreader_kg": 190.3, "spreader_cg": (16, -513, 874), "load_cg": (0, -194, 995)}
# front ballast: the counterweights implement, 4 stacks (base 5.5 kg + plates of 11 kg) on the front lower beams
ballast_stacks = 4
ballast_base_kg = 5.5
ballast_plate_kg = 11.0
ballast_plates_max = 4
ballast_cg = (500.0, 700.0)             # (y, z), estimated from counterweights/simple
front_share_min = 0.25                  # wanted front axle share for steering grip (estimated)


def bin_section(z):
    """Half width (mm) of the bin inside at height z."""
    if z <= bin_flare_z[0]:
        return side_x
    f = min(1.0, (z - bin_flare_z[0]) / (bin_flare_z[1] - bin_flare_z[0]))
    return side_x + f * (bin_top_x - side_x)


def bin_volume(z_fill, n=40):
    """Volume (m3) of compost from the belt up to z_fill."""
    L = bin_y[1] - bin_y[0]
    a = 0.0
    dz = (z_fill - belt_top) / n
    for i in range(n):
        z = belt_top + (i + 0.5) * dz
        a += 2.0 * bin_section(z) * dz
    return a * L * 1e-9


def fill_level(mass_kg, rho):
    """Height z (mm) of the compost surface for a mass in kg (flat surface)."""
    lo, hi = belt_top, bin_flare_z[1]
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if bin_volume(mid) * rho < mass_kg:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
