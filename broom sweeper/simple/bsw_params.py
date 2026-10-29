import os
import sys

# =====================================================================
# Broom / sweeper (simple) - parameters
# Front-mounted angle broom for the Bruut OpenAgbot (standard robot). It uses the front toolbar, the lift arms, the
# carrier with the king pin and the lift actuator of the push blade ("push blade/simple", imported, not copied): the
# blade is swapped for a broom head that turns on the same king pin (angle +-25 degrees, same lock pin).
# The head is a roller brush O400 x 1000 under a hood, driven by a 48 V motor with a toothed belt, and runs on 2 castor
# wheels that set the bristle contact; the actuator rod floats in its slot, so the head follows the floor.
# Angled, the brush throws the material to one side into a windrow (no collector in the simple variant).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

PBL_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "push blade", "simple")
if PBL_FOLDER not in sys.path:
    sys.path.append(PBL_FOLDER)
import pbl_params as B          # noqa: E402  (toolbar, lift arms, carrier, king pin, actuator of the push blade)

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
king_y = B.king_y               # king pin axis (x = 0) in the work pose
king_d = B.king_d
head_d = B.head_d               # round swivel plate O260 x 12, as on the blade
plate_t = B.plate_t
swivel_z = B.swivel_z
lock_r = B.lock_r
lock_d = B.lock_d
angle_steps = B.angle_steps     # -25, -12.5, 0, 12.5, 25 degrees
pivot = B.pivot
lift_work = B.lift_work
lift_transport = B.lift_transport
LIFT_POSES = B.LIFT_POSES

# ---------------------------------------------------------------------
# Head frame: swivel plate with a spine plate onto a cross beam 80 x 60 x 4, 2 end plates 8 mm that carry the brush
# bearings. The beam lies under the swivel plate and behind the brush.
# ---------------------------------------------------------------------
beam_y = (1160.0, 1240.0)
beam_z = (180.0, 240.0)         # top of the beam = bottom of the swivel plate
beam_wall = 4.0
spine_x = 90.0                  # spine plate x +-90, from the king pin to the front of the beam, in the swivel plane
end_x = 515.0                   # inside faces of the end plates (x +-515)
end_t = 5.0
# end plate outline (y, z): covers the brush ends, the bearings and the motor flange
end_pts = ((1150.0, 160.0), (1260.0, 80.0), (1690.0, 80.0), (1700.0, 300.0), (1560.0, 450.0), (1380.0, 525.0),
           (1180.0, 525.0), (1150.0, 300.0))

# ---------------------------------------------------------------------
# Brush: roller O400 x 1000, PP bristles on a core tube O114.3 x 3, shaft O40 in 2 flange bearings UCFL 208
# Work: the bristles touch the floor with a set deflection (castor height), the bottom of the brush turns forward.
# ---------------------------------------------------------------------
brush_d = 400.0
brush_l = 1000.0
core_d = 114.3
core_wall = 3.0
fill_d = 130.0                  # bristle body O400 / O130 (bristles in strips on the core)
shaft_d = 40.0
stub_l = 60.0                   # stub shafts welded into the core end discs, 60 mm inside
axis_y = 1460.0                 # brush axis in the work pose, angle 0
deflection = 10.0               # mm bristle deflection on the floor
axis_z = brush_d / 2.0 - deflection
brg_house_d = 80.0              # UCFL 208: housing O80 x 40, 2-bolt flange 150 x 60 x 15
brg_len = 40.0
brg_flange = (15.0, 60.0, 150.0)

# ---------------------------------------------------------------------
# Hood 2 mm over the brush between the end plates, rubber flap 6 mm at the front against flying material
# ---------------------------------------------------------------------
hood_r = 227.0                  # inside radius
hood_t = 2.0                    # aluminium 5754
hood_deg = (15.0, 155.0)        # from the front (+y) over the top to the rear, about the brush axis
flap_y = 1684.0
flap_t = 6.0
flap_z = (30.0, 262.0)

# ---------------------------------------------------------------------
# Drive: 48 V BLDC motor 1000 W with a 1:5 planetary gearbox, on the inside of the right end plate above the hood,
# HTD 8M belt 30T -> 45T outside the right end plate under a guard. 3000 / 5 = 600 rpm -> 400 rpm brush.
# ---------------------------------------------------------------------
motor_yz = (1260.0, 450.0)      # motor / gearbox axis (parallel to x)
motor_d = 100.0
motor_len = 235.0               # body + gearbox, from the end plate inward
motor_flange_d = 120.0
motor_rpm = 3000.0
gear_ratio = 5.0
motor_w = 1000.0
motor_kg = 6.5
pulley_small = (30, 76.4)       # teeth, pitch diameter
pulley_big = (45, 114.6)
pulley_w = 30.0
pulley_x = (578.0, 608.0)       # both pulleys, outside the right end plate (bearing housing up to x 563)
belt_t = 5.0
guard_x = (568.0, 618.0)        # guard: cover + rim, open toward the end plate
guard_gap = 12.0                # rim radius = pulley radius + gap
guard_t = 2.0

# ---------------------------------------------------------------------
# Castor wheels: 2 x swivel castor O125 x 40 (PU) on a 20 mm spacer under the beam; they set the bristle contact.
# Swivel axis at y castor_y, wheel axle trails behind it.
# ---------------------------------------------------------------------
castor_x = 450.0
castor_y = 1200.0
castor_wheel_d = 125.0
castor_wheel_w = 40.0
castor_trail = 40.0
castor_plate = (100.0, 80.0, 6.0)   # top plate x, y, t
castor_height = 160.0           # floor to top plate
spacer_t = beam_z[0] - castor_height     # 20 mm

# ---------------------------------------------------------------------
# Work (for bsw_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.3e-6
alu = 2.7e-6
bristle_bulk = 0.12e-6          # kg/mm3: PP (0.9 g/cm3) at ~13 % fill of the bristle body (estimated)
speed = 1.0                     # m/s working speed (3.6 km/h)
overlap = 100.0                 # mm overlap between passes
contact_N_per_m = 150.0         # bristle force on the floor per m brush at 10 mm deflection (estimated)
mu_bristle = 0.5                # bristle on concrete (estimated)
air_loss_W = 100.0              # windage of the brush at 400 rpm (estimated)
eta_motor = 0.85                # BLDC + gearbox
eta_belt = 0.95
eta_drive = 0.75                # hub motors at this load
crr_floor = 0.03                # rolling resistance of the robot on a yard floor
crr_castor = 0.04
throw_speed = 0.5               # share of the tip speed the material gets (estimated)
# material on the floor (kg/m2) and how it behaves: sweeping load per job (estimated)
MATERIAL = {
    "dry_sand_grit": 1.0,
    "straw_feed_rests": 0.4,
    "wet_leaves": 1.5,
    "dry_snow_30mm": 3.0,
}
hub_torque_nom = B.hub_torque_nom
r_load = B.r_load
n_driven = B.n_driven
act_force = 3000.0              # N, heavy-duty version of the push-blade actuator (same clevis and stroke)
act_speed = 6.0                 # mm/s at 2000 N (typical 3000 N actuator)
act_kg = 3.4
counterweight_y = -500.0        # rear stack of the counterweights (counterweights/simple), over the rear axle
counterweight_plate_kg = 11.0
rear_share_min = 0.25           # least share on the rear axle for traction with a front tool (counterweights)
rear_share_hop = 0.10           # least share on the rear axle for a short lift over a threshold or kerb (estimated)
counterweight_max_plates = 9    # rear stacks of the counterweights: 0..99 kg per axle end
robot_battery_wh = 1900.0       # usable, estimated (battery pack/simple)
# from build_bsw.mass_properties() in the work pose (update after a change of the model)
MODEL_MASS = {"mount_kg": 22.4, "mount_cg_y": 712.0, "lift_kg": 97.8, "lift_cg_y": 1312.0, "lift_cg_z": 251.0,
              "on_castors_kg": 0.0}
