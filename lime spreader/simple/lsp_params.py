# =====================================================================
# Lime spreader (simple) - parameters
# Drop spreader for granulated or ground lime on the Bruut OpenAgbot (standard robot). A V-hopper of ~200 l sits on 2
# rails on the inner upper beams, centred over the robot so the load is shared by both axles. A trough auger in the
# bottom of the hopper carries the lime backward in a tube under the rear lower beams to a cross auger behind the rear
# wheels; the cross auger spreads it over 1.3 m and lets it fall through a row of outlet holes, 0.2 m above the ground,
# inside a rubber dust skirt. No spinner: no dust cloud and no drift onto neighbouring crops.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_upper_beam_x = (325.0, 425.0)     # centres of the 2 upper beams per side (40 x 40), along y, y = +-650
robot_upper_beam_z = (659.0, 699.0)
robot_lower_beam_z = (619.0, 659.0)
robot_rear_beam_y = (-575.0, -425.0)    # centres of the rear lower beams (40 x 40, along x)
robot_beam = 40.0
robot_mass = 160.0              # kg, estimated (agbot comparison)
robot_cg_y = 0.0                # estimated
robot_cg_z = 450.0              # estimated
robot_track = 750.0
robot_steer_deg = 30.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Rails: 2 x rect tube 40 x 40 x 3 on 25 mm spacers on the inner upper beams (x = +-325), as on the fertilizer
# spreader (the spacers clear the wheel-unit bolts). They run back past the beam ends to carry the cross auger.
# ---------------------------------------------------------------------
rail_x = 325.0
rail = 40.0
rail_wall = 3.0
rail_y = (-870.0, 330.0)
spacer_h = 25.0
rail_z = (robot_upper_beam_z[1] + spacer_h, robot_upper_beam_z[1] + spacer_h + rail)
rail_bolt_y = (-625.0, -475.0, -325.0, 275.0)   # beam holes at y +-275..+-625 (none in the middle); clear of
                                                # the wheel-unit bolts at y -425 / -575

# ---------------------------------------------------------------------
# Hopper: steel 2 mm, painted (lime is alkaline, not very corrosive), V-section across x extruded along y.
# Upper funnel from x +-450 at the top down to x +-300 on the rails, lower funnel between the inner upper beams down to
# a U-trough round the auger. Walls 57 and 51 degrees: granulated lime runs (repose ~35..40 degrees).
# ---------------------------------------------------------------------
hop_y = (-400.0, 300.0)
hop_t = 2.0
hop_top_z = 1000.0
hop_top_x = 450.0
hop_mid = (300.0, 764.0)        # (x, z) where the funnel crosses the rails (on top of them)
trough_x = 60.0                 # trough half width (vertical walls)
trough_top_z = 470.0
auger_z = 420.0                 # axis of the trough auger
trough_r = 60.0                 # U-bottom radius about the auger axis
bar = (60.0, 6.0)               # flat bars welded along the hopper, resting on the rails (x 300..360)
lid_t = 2.0                     # aluminium
fill_level = 960.0              # lime level when full (40 mm under the lid)

# ---------------------------------------------------------------------
# Trough auger: flights O100 pitch 100 on a shaft O30, from the front wall back to the drop chute
# Tube O114.3 x 3 from the rear wall to the chute; gearmotor 24 V on the front wall.
# ---------------------------------------------------------------------
auger_d = 100.0
auger_pitch = 100.0
auger_shaft_d = 30.0
flight_t = 4.0
tube_d = 114.3
tube_wall = 3.0
long_y = (hop_y[1] - 10.0, -850.0)      # trough auger from the front wall to over the cross auger
long_tube_y = (hop_y[0], -880.0)
gm_box = 80.0                   # worm gearmotor 24 V: gearbox 80 x 80 x 80, motor O80 x 120 (estimated)
gm_motor = (80.0, 120.0)
gm_kg = 3.5

# ---------------------------------------------------------------------
# Cross auger: flights O100 in a tube O114.3 behind the rear wheels, left-hand on one half and right-hand on the other,
# so the lime goes from the middle to both ends. Outlet holes O20 in the bottom, every 50 mm, with a slide plate.
# Own 24 V gearmotor on the right end.
# ---------------------------------------------------------------------
cross_y = -840.0                # behind the rear tyres (y -715)
cross_z = 260.0                 # axis
cross_x = 650.0                 # tube x +-650 (width 1.3 m, wider than the robot's track over the tyres, 850)
hole_d = 20.0
hole_pitch = 50.0
chute = 100.0                   # square drop chute from the trough tube into the cross tube
skirt_t = 4.0                   # rubber skirt round the cross tube, to 20 mm above the ground
skirt_gap = 20.0
skirt_x = cross_x + 20.0
skirt_y = (cross_y - 90.0, cross_y + 90.0)
leg = 40.0                      # 2 legs 40 x 40 x 3 from the rail ends down to the cross tube (x = +-325)
leg_y = (rail_y[0], rail_y[0] + 40.0)
saddle_t = 6.0

# ---------------------------------------------------------------------
# Work (for lsp_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.3e-6
alu = 2.7e-6
rho_lime = {"granulated": 1.15, "ground_dry": 1.0, "ground_damp": 1.25}   # kg/l bulk (estimated)
dose_kg_ha = (500.0, 1000.0, 2000.0)    # maintenance lime on grass / vegetables .. repair dose
speed = 0.8                     # m/s working speed
fill_auger = 0.45               # filling of the auger flights (estimated)
auger_rpm_max = 60.0            # gearmotor output
lambda_screw = 4.0              # material factor of a screw conveyor for lime (estimated)
auger_idle_W = 15.0             # per auger, no load
crr_field = 0.08                # rolling resistance on tilled soil / grass (estimated)
eta_drive = 0.75
hub_torque_nom = 55.0           # Nm per Quinder 48 V 550 W hub motor (continuous)
r_load = 0.20
n_driven = 4
robot_battery_wh = 1900.0       # usable, estimated (battery pack/simple)
field_eff = 0.8
# from build_lsp.mass_properties() and hopper_volume() (update after a change of the model)
MODEL_MASS = {"kg": 97.4, "cg_y": -389.0, "cg_z": 522.0, "volume_l": 178.5, "fill_cg_y": -50.0, "fill_cg_z": 760.0}
