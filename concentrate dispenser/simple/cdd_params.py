import math
import os
import sys

# =====================================================================
# Concentrate dispenser on the feed table (simple) - parameters
# Doses concentrate pellets or minerals on the feed along the feed fence while the robot pushes feed with the
# feed pusher auger ("feed pusher auger/V3", imported, not copied): a fresh line of concentrate on the freshly pushed
# windrow draws the cows to the fence.
#  - Hopper 45 l (stainless 1.5 mm, 60 degree side walls) in the MIDDLE of the robot on 2 cross tubes over the upper
#    beams at y +-325: the 30 kg of pellets do not change the balance of the feed pusher (which already needs 40 kg
#    of counterweight at the front).
#  - The hopper hangs on 4 load cells: the dose is controlled by loss-in-weight, not by a calibrated auger.
#  - A metering auger O54 in the trough under the hopper runs on in a tube O60 to x 880, past the right wheels and the
#    end of the feed pusher; a rubber spout drops the pellets onto the windrow that the feed pusher just made.
#  - NEMA 23 stepper with a 10:1 planetary gearbox on the left end.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm. Feed fence on the +x
# side (as the feed pusher). Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FPA_FOLDER = os.path.join(ROOT_DIR, "feed pusher auger", "V3")
if FPA_FOLDER in sys.path:
    sys.path.remove(FPA_FOLDER)
sys.path.insert(1, FPA_FOLDER)  # before any other feed pusher version (they share the prefix fpa)
import fpa_params as F          # noqa: E402  (feed pusher auger V3)

# ---------------------------------------------------------------------
# Robot interface
# ---------------------------------------------------------------------
robot_wheel_x = F.robot_wheel_x
robot_axle_y = 500.0
robot_axle_z = F.robot_axle_z
robot_tire_d = F.robot_tire_d
robot_tire_w = F.robot_tire_w
robot_kg = 161.5
upper_beam_x = ((305.0, 345.0), (405.0, 445.0))  # inner and outer upper beams (both sides)
upper_beam_z = (659.0, 699.0)
hole_y = 325.0                  # vertical M10 grid holes in the upper beams at |y| 275, 325 .. 625
m10_hole = 10.4

# ---------------------------------------------------------------------
# Cross tubes 40 x 40 x 3 at y +-325 over the 4 upper beams, 4 x M10 each (through tube and beam)
# ---------------------------------------------------------------------
bar_x = 470.0
bar = 40.0
bar_wall = 3.0
bar_z = (upper_beam_z[1], upper_beam_z[1] + bar)          # 699 .. 739
bar_bolt_x = (325.0, 425.0)

# ---------------------------------------------------------------------
# Load cells: 4 x shear beam 50 kg (C3) on the cross tubes, under the 4 legs of the hopper frame
# ---------------------------------------------------------------------
cell = (130.0, 30.0, 30.0)      # x, y, z (along the tube)
cell_cap_kg = 50.0
cell_res_g = 2.0                # g per cell after filtering (24-bit amplifier, estimated)
leg_x = 268.0                    # leg centre: frame tubes 1 mm outside the hopper end walls
leg = 30.0
leg_wall = 2.0

# ---------------------------------------------------------------------
# Hopper: stainless 1.5 mm. Box part on top, tapered part (60 degrees) down to a U-trough round the auger.
# Hopper frame: 2 tubes 30 x 30 along y (x 250 .. 280) and 2 along x, on the 4 legs; the hopper's top band rests on it.
# ---------------------------------------------------------------------
hopper_x = 250.0                # half length (along x, the auger axis)
hopper_y = 180.0                # half width of the box part
wall_t = 1.5
slope_deg = 60.0                # side walls: pellets and meal slide at >= 45..55 degrees
auger_z = 820.0                 # auger axis
trough_r = 30.0                 # inner radius of the U-trough (auger O54 + 3 mm)
taper_top = auger_z + (hopper_y - trough_r) * math.tan(math.radians(slope_deg))   # ~1080
box_h = 110.0
hopper_top = taper_top + box_h
frame_t = 30.0                  # hopper frame tube 30 x 30 x 2
frame_z = (taper_top - frame_t, taper_top)
band = (30.0, 5.0)              # flat band round the top of the taper (resting on the frame), width, t
lid_t = 2.0
lid_hinge = 20.0

# ---------------------------------------------------------------------
# Metering auger: flight O54 pitch 50, core O16, from the left end wall to the outlet; tube O60 x 2 from the hopper's
# right wall to x 880. Outlet: hole on the underside at x 850 with a flanged stub and a rubber spout O60 down to z 480.
# ---------------------------------------------------------------------
flight_d = 54.0
flight_pitch = 50.0
flight_t = 3.0
core_d = 16.0
tube_od = 60.0
tube_wall = 2.0
tube_x = (hopper_x, 880.0)
outlet_x = 850.0
spout_z = 480.0                 # spout end over the floor (windrow top ~250, estimated)
spout_od = 64.0
spout_t = 4.0
end_cap_t = 5.0
auger_end_x = tube_x[1] - end_cap_t - 2.0
tie_d = 12.0                    # tie rod from the hopper frame to the tube end
tie_top = (hopper_x + 15.0, 0.0, frame_z[0])

# Drive on the left end wall: bearing flange, planetary gearbox 10:1, NEMA 23
gear_ratio = 10.0
gearbox = (60.0, 60.0)          # square, length
nema = 57.0
nema_len = 80.0
nema_torque = 1.9               # Nm holding
nema_torque_run = 1.2           # Nm at 1000 rpm motor (estimated)
gear_eff = 0.85
flange = (80.0, 80.0, 8.0)      # bearing flange (square, t) on the end wall

# ---------------------------------------------------------------------
# Feed, cows and dosing (for cdd_calc)
# ---------------------------------------------------------------------
pellet_density = 0.68           # kg/l dairy concentrate pellets (estimated)
mineral_density = 1.1           # kg/l mineral meal (estimated)
fill = 0.40                     # auger fill at the hopper outlet (pellets, estimated)
place_m = 0.75                  # m of fence per cow (feeding place)
dose_place_g = 100.0            # g per feeding place per round (a "lure" dose, estimated)
cows = 120
rounds_per_day = 8
push_speed = 0.35               # m/s pushing feed (feed pusher V3)
lambda_auger = 2.5              # material factor for the auger power (pellets in a small auger, estimated)
bulk_flow_ratio = 1.0
windrow_x = 900.0               # centre of the windrow next to the robot (feed fence at x ~1150, estimated)
robot_battery_wh = 1900.0
electronics_w = 15.0            # load-cell amplifier, stepper driver idle

g = 9.81
steel = 7.85e-6
stainless = 7.9e-6
alu = 2.7e-6
rubber = 1.2e-6

# from build_cdd.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 37.0, "cg": (54.0, 0.0, 918.0)}


def hopper_volume_l():
    """Usable volume (l) of box + taper (trough cross-section left out)."""
    L = 2 * hopper_x
    box = L * 2 * hopper_y * box_h
    taper = L * (2 * hopper_y + 2 * trough_r) / 2.0 * (taper_top - auger_z)
    return (box + taper) / 1e6
