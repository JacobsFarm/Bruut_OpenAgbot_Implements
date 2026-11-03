import os
import sys

# =====================================================================
# Debris vacuum (simple) - parameters
# Litter and shard vacuum for the Bruut OpenAgbot (standard robot): picks up cups, cans, bottles, caps, cigarette butts
# after a festival, and glass shards of burnt solar panels, from grassland and paths.
#  - Nozzle in front: a steel hood 1000 wide with rubber flaps and a PP brush roller O200 that flicks the litter out of
#    the sward into the air stream, on the head frame and castors of the magnet sweeper (king pin, lift arms and
#    toolbar of the push blade, castors of the broom; all imported, not copied).
#  - Hose O125 (PU, wear resistant) from the nozzle outlet up to a bin of 270 l on the upper beams.
#  - Clean-air fan: a 48 V centrifugal fan on the lid sucks the air out of the bin through a screen, so litter and glass
#    never pass the impeller; a liner bag in the bin, emptied through the rear door.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "broom sweeper", "simple"),
           os.path.join(ROOT_DIR, "magnet sweeper", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import pbl_params as B          # noqa: E402  (toolbar, lift arms, carrier, king pin, actuator)
import bsw_params as S          # noqa: E402  (castor wheels)
import mgs_params as M          # noqa: E402  (head frame with brackets: the nozzle hangs where the magnet box hangs)

# ---------------------------------------------------------------------
# Robot interface
# ---------------------------------------------------------------------
robot_wheel_x = B.robot_wheel_x
robot_axle_y = B.robot_axle_y
robot_axle_z = B.robot_axle_z
robot_tire_d = B.robot_tire_d
robot_tire_w = B.robot_tire_w
robot_steer_deg = B.robot_steer_deg
robot_mass = B.robot_mass
robot_cg_y = B.robot_cg_y
upper_beam_x = ((305.0, 345.0), (405.0, 445.0))   # inner and outer upper beam (both sides), z 659..699
upper_beam_top = 699.0
upper_hole_y = 300.0            # vertical M10 grid holes in the upper beams at |y| 275..625: cross bars at y +-300
pivot = B.pivot
king_y = B.king_y
lift_work = 0.0
lift_hop = 9.0
lift_transport = 18.0
LIFT_POSES = (-4.0, 0.0, lift_hop, lift_transport)

# ---------------------------------------------------------------------
# Nozzle (on the magnet-sweeper head frame: its brackets carry a flange at y 1300..1310)
# Hood: steel 2 mm, open at the bottom, end plates 5 mm; rubber flaps front and rear down to flap_gap over the ground.
# ---------------------------------------------------------------------
noz_x = 515.0                   # outside of the end plates (x +-515)
noz_y = (M.box_y[0], 1610.0)    # rear wall on the bracket flanges .. front wall
noz_z = (40.0, 330.0)           # bottom of the steel walls, top of the hood
sheet_t = 2.0
end_t = 5.0
flap_t = 6.0
flap_gap_front = 25.0           # front flap ends 25 mm over the ground (litter passes under it)
flap_gap_rear = 10.0
outlet_d = 125.0                # outlet stub on the hood top, rear of the brush
outlet_y = 1520.0
outlet_h = 90.0

# Brush roller: PP bristles O200 x 990 on a core tube O60, shaft O25 in 2 flange bearings UCFL 205 outside the end
# plates; 48 V 250 W gearmotor (1:10) straight on the left shaft end. Bottom turns backward: throws up and to the rear.
brush_d = 200.0
brush_l = 990.0
brush_core_d = 60.0
brush_shaft_d = 25.0
brush_axis = (1440.0, 92.0)     # (y, z): 8 mm bristle deflection on the ground
brush_rpm = 400.0
brg_flange = (12.0, 50.0, 110.0)   # UCFL 205: flange t, y, z
brg_house = (62.0, 32.0)
gm_d = 90.0                     # gearmotor body O90 x 200 + gearbox O100 x 70
gm_len = 270.0

# ---------------------------------------------------------------------
# Bin on the upper beams: 2 cross bars (rect tube 60 x 40 x 3) at y +-300, aluminium 3 mm, rear door hinged at the top
# ---------------------------------------------------------------------
bar_x = 470.0
bar_wh = (60.0, 40.0)
bin_x = 450.0
bin_y = (-380.0, 370.0)         # clear of the rear frame bolts (y -416) and the front stepper plates (y 405)
pad_h = 15.0                    # PE pads on the cross bars (the bar bolt nuts stay under the bin)
bin_z = (upper_beam_top + 40.0 + pad_h, upper_beam_top + 455.0)
bin_t = 3.0
door_gap = 2.0
inlet_z = 1075.0                # hose inlet stub in the front wall (x 0)
inlet_len = 60.0
liner_l = 250.0                 # litres of the liner bag (estimated, fills the bin)

# Fan on the lid: centrifugal fan O420 x 160 volute, 48 V BLDC 1.2 kW on top, outlet duct to the rear; screen in the lid
fan_d = 420.0
fan_h = 160.0
fan_y = -60.0
fan_motor = (120.0, 140.0)      # O, height
fan_outlet = (150.0, 120.0)     # duct section (x, z), along -y to the bin rear edge
screen_d = 300.0

# Hose: PU O125 (outside O137), from the outlet stub up to the inlet stub, through one mid point (bends)
hose_d = 137.0
hose_mid = (0.0, 1250.0, 800.0)  # mid point in the work pose (shifts with the lift, see dvc_parts.hose_points)

# ---------------------------------------------------------------------
# Work (dvc_calc)
# ---------------------------------------------------------------------
g = 9.81
rho_air = 1.2
steel = 7.85e-6
alu = 2.7e-6
rubber = 1.3e-6
pe = 0.95e-6
bristle_bulk = 0.12e-6
hose_v = 22.0                   # m/s air in the hose
hose_len = 1.4                  # m (from the model, ground_contact)
f_hose = 0.04                   # friction factor of a corrugated PU hose
K_nozzle = 2.0                  # entry loss of the nozzle (incl. brush and flaps), x dynamic pressure in the hose
K_bends = 1.0
K_bin = 1.0                     # sudden expansion into the bin
dp_screen = 400.0               # Pa: screen + liner bag mesh, half loaded (estimated)
eta_fan = 0.50                  # fan x motor x controller
fan_W = 1200.0
slot_area = 1.0 * (flap_gap_front + flap_gap_rear) / 1000.0     # m2 of air inlet under the flaps
# litter: mass (g), drag area (m2, lying flat), drag coefficient (estimated)
ITEMS = {
    "cigarette_butt": (0.3, 0.0002, 1.0),
    "bottle_cap": (2.0, 0.0006, 1.1),
    "plastic_cup": (5.0, 0.005, 1.1),
    "crushed_can": (15.0, 0.004, 1.1),
    "pet_bottle_0.5l": (25.0, 0.012, 0.9),
    "glass_shard_6g": (6.0, 0.0012, 1.1),
    "pv_glass_50x50x3.2": (20.0, 0.0025, 1.1),
}
convey_factor = 1.8             # hose air speed >= this x the terminal speed for safe transport
brush_N_per_m = 60.0            # bristle force on the sward per m (estimated, light contact)
mu_bristle = 0.6
brush_air_W = 30.0
eta_brush = 0.75
speed = 0.8                     # m/s
overlap = 100.0
crr_grass = 0.06
crr_castor = 0.08
eta_drive = 0.75
robot_battery_wh = 1900.0
litter_bulk = 60.0              # kg/m3 mixed festival litter in the bag (estimated)
shard_bulk = 1300.0             # kg/m3 glass shards (estimated)
bin_load_max = 60.0             # kg payload in the bin (estimated)
litter_per_ha = 25.0            # kg left on a ha after the hand clean-up (estimated)
hub_torque_nom = B.hub_torque_nom
r_load = B.r_load
n_driven = B.n_driven
act_force = S.act_force         # 3000 N version of the lift actuator (as the broom and the magnet sweeper)
act_speed = S.act_speed
act_kg = S.act_kg
counterweight_y = -500.0
counterweight_plate_kg = 11.0
rear_share_min = 0.25
rear_share_hop = 0.10
counterweight_max_plates = 9
# from build_dvc.mass_properties() in the work pose (update after a change of the model)
MODEL_MASS = {"mount_kg": 22.4, "mount_cg_y": 712.0, "lift_kg": 81.6, "lift_cg_y": 1296.0, "lift_cg_z": 199.0,
              "bin_kg": 44.8, "bin_cg_y": -29.0, "hose_kg": 4.1}
