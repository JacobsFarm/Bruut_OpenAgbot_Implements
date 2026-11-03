import os
import sys

# =====================================================================
# Magnet sweeper (simple) - parameters
# Flat permanent-magnet plate that the robot carries low over grassland, festival fields, paths and yards to pick up
# nails, screws, tent pegs, wire, bottle caps and other loose iron. Front-mounted on the toolbar, lift arms, carrier
# and king pin of the push blade ("push blade/simple", imported, not copied) and on the castor wheels of the broom
# ("broom sweeper/simple"). The magnet box hangs straight (lock pin in the middle hole).
#
# Box: aluminium with a non-magnetic stainless bottom (skin). Inside, a magnet core (steel back plate with 2 rows of
# NdFeB blocks, the front row north down, the rear row south down) lies on the skin while working: the iron sticks to the underside of the skin.
# Emptying: a small actuator on the lid lifts the core 100 mm inside the box; the field at the skin collapses and the
# iron drops off into a flat collecting tray (10 mm high, it fits under the skin) that lies at the field edge: the robot
# drives the box over it in the work pose, so emptying needs no lift and no ballast. Nothing touches the iron.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PBL_FOLDER = os.path.join(ROOT_DIR, "push blade", "simple")
BSW_FOLDER = os.path.join(ROOT_DIR, "broom sweeper", "simple")
for _f in (PBL_FOLDER, BSW_FOLDER):
    if _f not in sys.path:
        sys.path.append(_f)
import pbl_params as B          # noqa: E402  (toolbar, lift arms, carrier, king pin, actuator of the push blade)
import bsw_params as S          # noqa: E402  (head beam and castor wheels of the broom)

# ---------------------------------------------------------------------
# Robot and push-blade interface (taken over, not changed)
# ---------------------------------------------------------------------
robot_wheel_x = B.robot_wheel_x
robot_axle_y = B.robot_axle_y
robot_axle_z = B.robot_axle_z
robot_tire_d = B.robot_tire_d
robot_tire_w = B.robot_tire_w
robot_steer_deg = B.robot_steer_deg
robot_mass = B.robot_mass
robot_cg_y = B.robot_cg_y
king_y = B.king_y
king_d = B.king_d
head_d = B.head_d
swivel_z = B.swivel_z
lock_r = B.lock_r
lock_d = B.lock_d
angle_steps = B.angle_steps     # the swivel plate keeps the 5 lock holes (same interface as blade and broom)
pivot = B.pivot
lift_work = 0.0
lift_hop = 9.0                  # arms up 9 degrees: over a kerb (only with ballast, see mgs_calc)
lift_transport = 18.0
LIFT_POSES = (-4.0, 0.0, lift_hop, lift_transport)

# ---------------------------------------------------------------------
# Head frame: swivel plate + spine plate (as the broom) onto the cross beam 80 x 60 x 4 of the broom, same place
# (castor spacers and castors underneath). The magnet box is bolted against the front face of the beam.
# ---------------------------------------------------------------------
beam_y = S.beam_y               # (1160, 1240)
beam_z = S.beam_z               # (180, 240): top = bottom of the swivel plate
beam_wall = S.beam_wall
beam_x = 500.0                  # beam x +-500
spine_x = S.spine_x

# ---------------------------------------------------------------------
# Magnet box: aluminium 5754 walls 4 mm, lid 5 mm, stainless 304 skin 3 mm (non-magnetic) as the bottom.
# The box stands 70 mm in front of the beam, so the broom castors under the beam can swivel round (reversing)
# without touching it: 2 brackets (side plate 10 mm welded to the beam, flange 10 mm) and 2 x 2 M10 into the rear wall.
# ---------------------------------------------------------------------
box_x = 550.0                   # outside x +-550 (as wide as the push blade)
box_y = (1310.0, 1550.0)        # outside
bracket_x = 300.0               # side plates at x +-300
bracket_t = 10.0
bracket_flange = (80.0, 10.0)   # flange width (x) and thickness (y), against the rear wall
bracket_z = (130.0, 240.0)
box_z = (20.0, 240.0)           # skin bottom 20 mm over the floor (castors on a hard floor), lid top 240
wall_t = 4.0
lid_t = 5.0
skin_t = 3.0
box_bolt_dx = 25.0              # flange bolts at x +-300 +-25
box_bolt_z = (160.0, 215.0)
# 4 x skids (PE 10 mm) under the skin corners: a bump lifts the box, the skin never scrapes
skid_h = 8.0
skid_w = 30.0

# ---------------------------------------------------------------------
# Magnet core (own sub-Part, moves up inside the box): steel back plate 15 mm, 2 rows of 10 NdFeB N35 blocks
# 100 (x) x 100 (y) x 10 (z), NiCuNi coated, glued and potted; front row north down, rear row south down (one pole pair
# across the driving direction: a strong field gradient, a single pole would give almost none). 4 guide rods O16
# (stainless) stand in the box from skin to lid outside the magnet rows, the back plate slides on them in PE bushes.
# ---------------------------------------------------------------------
core_x = 535.0                  # back plate x +-535
core_y = (1325.0, 1535.0)
core_t = 15.0
mag_n = 10
mag_size = (100.0, 100.0, 10.0)
mag_rows = 2
mag_y = 1430.0                  # centre between the 2 magnet rows
core_gap = 1.0                  # PE glide strip between magnet face and skin
core_lift = 100.0               # release stroke
guide_d = 16.0
guide_x = 520.0
guide_y = (1360.0, 1500.0)
bush_d = 28.0
bush_h = 20.0

# ---------------------------------------------------------------------
# Release actuator: 24 V linear actuator 3000 N, stroke 100, standing on the lid (x 0, y mag_y); the rod goes through
# the lid to a clevis on the back plate. Extended = core down (work), retracted = core up (release).
# ---------------------------------------------------------------------
rel_body_d = 50.0
rel_body_l = 260.0              # body + motor above the lid
rel_rod_d = 20.0
rel_motor = (60.0, 70.0, 120.0)  # motor box beside the body (x, y, z)
rel_force = 3000.0
rel_speed = 6.0                 # mm/s at 2000 N (typical 3000 N actuator)
rel_kg = 3.4
contact_parts = 75              # parts touching the skin on the pole lines with a full load (estimated)

# ---------------------------------------------------------------------
# Collecting tray at the field edge (not part of the implement, drawn for the release): PE tray 1200 x 320 x 10,
# under the skin (skids at 12 mm) in the work pose; the castors stop in front of it.
# ---------------------------------------------------------------------
tray_size = (1200.0, 320.0, 10.0)
tray_t = 3.0

# ---------------------------------------------------------------------
# Work (for mgs_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
ndfeb = 7.5e-6
pe = 0.95e-6
mu0 = 4e-7 * 3.141592653589793
Br = 1.17                       # T, remanence of NdFeB N35
backplate_factor = 1.5          # steel back plate: field as from a magnet ~1.5x as thick (mirror, partly saturated)
Ms_steel = 1.6e6                # A/m, saturation of mild steel (mu0 Ms ~ 2.0 T)
pick_margin = 2.0               # magnetic force / weight needed to lift a part out of the grass (estimated)
grass_bury = 15.0               # mm a part lies below the skid line in the thatch of a mown sward (estimated)
# parts to pick up: mass (g), soft-iron volume (mm3), demagnetizing factor in a vertical field (lying flat)
ITEMS = {
    "bottle_cap_crown": {"g": 2.2, "N": 0.85},
    "nail_3x70": {"g": 3.9, "N": 0.5},
    "screw_4x40": {"g": 3.0, "N": 0.5},
    "nut_M10": {"g": 11.0, "N": 0.4},
    "wire_2.5x200": {"g": 7.7, "N": 0.5},
    "tent_peg_6x230": {"g": 50.0, "N": 0.5},
    "steel_tent_peg_V_300": {"g": 95.0, "N": 0.6},
}
speed = 1.2                     # m/s working speed on mown grass (4.3 km/h)
overlap = 100.0                 # mm overlap between passes
fringe = 25.0                   # mm the field picks up beyond each end of the magnet rows (estimated)
iron_per_ha = 4.0               # kg loose iron per ha after a festival (estimated)
skin_load_max = 3.0             # kg on the skin before parts start to fall off in front (estimated)
crr_grass = 0.06
crr_castor = 0.08               # castor O125 on grass
eta_drive = 0.75
hub_torque_nom = B.hub_torque_nom
r_load = B.r_load
n_driven = B.n_driven
act_force = S.act_force         # lift actuator: heavy-duty 3000 N version (as the broom), same clevis and stroke
act_speed = S.act_speed
act_kg = S.act_kg
counterweight_y = -500.0
counterweight_plate_kg = 11.0
rear_share_min = 0.25
rear_share_hop = 0.10
counterweight_max_plates = 9
robot_battery_wh = 1900.0
electronics_W = 40.0            # GNSS, control, logging of the covered area
# from build_mgs.mass_properties() in the work pose (update after a change of the model)
MODEL_MASS = {"mount_kg": 22.4, "mount_cg_y": 712.0, "lift_kg": 99.4, "lift_cg_y": 1311.0, "lift_cg_z": 138.0,
              "core_kg": 41.9}
