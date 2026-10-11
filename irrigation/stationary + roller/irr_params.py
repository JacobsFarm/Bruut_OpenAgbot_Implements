import math

# =====================================================================
# Irrigation, stationary pump + hose reel on the robot - parameters
#
# A petrol pump stands at the ditch with a hydrant (3-way valve: pump -> hose / hose -> drain). The robot carries a
# reel with ~150 m of 3" lay-flat hose. One strip:
#   1. lay out: the robot drives away from the hydrant, the hose pays out at the rear and lies still on the grass;
#   2. irrigate: the pump runs at low pressure, water leaves through small outlets (every 2 m a take-off with a
#      flat drop tail) and floods a strip of ~4 m wide. The pinch rollers on the robot clamp the hose shut, so
#      the coil on the reel stays empty;
#   3. drain: pump off, valve to drain, the hose runs empty by gravity;
#   4. roll up: the robot drives back (in reverse) and winds the empty hose; the pinch rollers squeeze the rest
#      of the water back towards the hydrant;
#   5. the robot lays the next strip 4 m further (the first 20 m of hose, the lead, has no outlets and runs over
#      the headland from the hydrant to the start of the strip).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot. All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (taken from "agbots/agbot design/agbot_params.py", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0           # align_width / 2
robot_axle_y = 500.0            # wheel centres at y = +-500
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_wheelbase = 1000.0
robot_lower_beam_y = (-575.0, -425.0, 425.0, 575.0)     # x-direction beams (1000 long), 40 x 40
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_x = (-425.0, -325.0, 325.0, 425.0)     # y-direction beams (1300 long), 40 x 40
robot_upper_beam_z = (659.0, 699.0)
robot_upper_beam_len = 1300.0
robot_beam = 40.0
robot_tire_rear_y = -robot_axle_y - robot_tire_d / 2.0  # -715
robot_gnss = (0.0, 575.0, 740.0)
robot_kg = 161.5                # agbot comparison (not weighed)
grid = 50.0                     # beam holes M10 (10.4): upper beams |y| >= 275
m10_hole = 10.4
m8_hole = 8.5

# ---------------------------------------------------------------------
# Hose: 3" lay-flat (PVC, medium duty), blue. Round when full, flat when empty.
# ---------------------------------------------------------------------
hose_id = 76.0
hose_wall = 1.3
hose_flat_w = math.pi * (hose_id + hose_wall) / 2.0    # 121
hose_flat_t = 2.0 * hose_wall                           # 2.6
hose_kg_per_m = 0.38            # empty (catalogue values 0.33 .. 0.42, estimated)
hose_p_max_bar = 4.0            # working pressure (we use < 0.5 bar)
hose_len = 150.0                # m on the reel
lead_len = 20.0                 # m without outlets: hydrant -> start of the strip over the headland
reel_reserve = 3.0              # m that always stays on the reel (end fixed to the core)
hw_c = 140.0                    # Hazen-Williams C, smooth PVC liner (estimated)

# Outlets (option b): take-off grommet in the hose wall with a restrictor and a flat drop tail (25 mm lay-flat,
# 0.5 m) that lies along the hose. Flat enough to be wound with the hose.
outlet_pitch = 2.0              # m
outlet_first = lead_len + 1.0   # m from the hydrant
outlet_d = 3.5                  # mm orifice (filter at the pump: 0.8 mm mesh)
outlet_cd = 0.62
outlet_saddle = (40.0, 60.0, 5.0)       # x, along, thickness on the flat hose (for drawing and coil build-up)
outlet_tail = (40.0, 500.0, 1.5)        # flat tail: width, length, thickness
outlet_kg = 0.05
coil_t = 3.2                    # mean thickness per wrap on the reel: hose 2.6 + saddles and tails (estimated)

# ---------------------------------------------------------------------
# Application (water spreads from each outlet over the surface until it infiltrates)
# ---------------------------------------------------------------------
infiltration = 15.0             # mm/h, grassland on loam (clay 5..10, sand 30+), ESTIMATED: measure on the field
strip_w = 4.0                   # m, spacing between strips = wetted width (estimated, depends on soil and slope)
gift = 25.0                     # mm per turn
et_day = 3.5                    # mm/day, grass in a dry Dutch summer (reference evaporation)
slope = 0.0                     # m/m along the strip (+ = uphill away from the hydrant)

# ---------------------------------------------------------------------
# Pump at the ditch (3" petrol centrifugal pump, class "WB30": 1100 l/min, 28 m head, 4.1 kW). Estimated curve.
# ---------------------------------------------------------------------
pump_h0 = 28.0                  # m shut-off head at full throttle
pump_qmax = 66.0                # m3/h at zero head, full throttle
pump_kw = 4.1
pump_eta = 0.45                 # best efficiency of a small petrol centrifugal pump (estimated)
pump_fuel_l_kwh = 0.55          # petrol per kWh shaft power at part load (estimated)
pump_fuel_idle = 0.35           # l/h at the lowest throttle (estimated)
pump_n_min = 0.35               # lowest throttle (speed fraction) that runs smoothly
suction_lift = 1.5              # m, water level in the ditch below the hydrant
suction_loss = 0.3              # m, 3" suction hose with foot valve and strainer at ~10 m3/h
valve_loss = 0.2                # m, 3-way valve and couplings

# ---------------------------------------------------------------------
# Tank cradle: 2 cross tubes on top of the upper beams, M10 through the beam holes (as the mobile refiller)
# ---------------------------------------------------------------------
cradle_y = (-375.0, 275.0)      # tube centre lines
cradle_tube = 40.0              # 40 x 40 x 3
cradle_wall = 3.0
cradle_half_len = 460.0
cradle_z = (robot_upper_beam_z[1], robot_upper_beam_z[1] + cradle_tube)     # 699 .. 739

# ---------------------------------------------------------------------
# Reel (rotates about x). Core = PE pipe 315 SDR17, flanges aluminium 4 mm, 6 tie rods M10 inside the core,
# 2 weld-on hubs on the shaft O25.
# ---------------------------------------------------------------------
reel_y = -100.0                 # axis
reel_z = 1240.0
core_od = 315.0
core_wall = 18.7
reel_gap = 130.0                # between the flanges (hose 121 + 9)
flange_d = 900.0
flange_t = 4.0
tie_r = 115.0                   # tie rods M10 on this radius (inside the core, ID 278)
tie_n = 6
hub_plate = (120.0, 10.0)       # D, thickness, inside the flange, 4 x M8 on r 45
hub_boss = (50.0, 30.0)
shaft_d = 25.0
shaft_x = (-160.0, 140.0)

# Stands: 2 side plates (steel 6 mm, laser cut), welded feet (10 mm) on the cradle tubes, 2 x M10 per foot
plate_x = 85.0                  # inner face of the plates (+-)
plate_t = 6.0
foot = (60.0, 80.0, 10.0)       # x outwards from the plate inner face .. , y, thickness
plate_pts = ((295.0, 749.0), (295.0, 830.0), (reel_y + 65.0, reel_z + 65.0), (reel_y - 65.0, reel_z + 65.0),
             (-560.0, 920.0), (-845.0, 920.0), (-845.0, 200.0), (-735.0, 200.0), (-735.0, 690.0),
             (-420.0, 749.0))
plate_holes = ((-610.0, 815.0, 120.0), (-790.0, 470.0, 70.0))      # lightening holes y, z, d
# windows (webs >= 55 mm), with a horizontal band across them for the motor standoffs (left) and the box (right)
plate_windows = (((235.0, 804.0), (-20.0, 1170.0), (-20.0, 804.0)),
                 ((-75.0, 804.0), (-75.0, 1160.0), (-236.0, 1160.0), (-520.0, 883.0), (-520.0, 786.0),
                  (-420.0, 804.0)))
plate_band = (960.0, 1020.0)
tie_tubes = ((250.0, 800.0), (-650.0, 715.0))   # cross tubes O30 x 3 between the plates (y, z)
tie_tube_d = 30.0

# Bearings UCF205 on the outer faces of the plates
ucf = (95.0, 70.0, 13.0, 60.0, 36.0)    # square, bolt pitch, flange thickness, hub D, total height from the plate

# Pinch rollers: bottom fixed (with the length encoder), top in vertical slots, pressed down by 2 springs.
# They clamp the hose shut while the strip is irrigated and squeeze out the rest of the water when winding.
pinch_y = -790.0
pinch_d = 80.0                  # PU-coated steel tube
pinch_len = 140.0               # hose 121 + 2 x 9.5; leaves room for the bearing nuts inside the plates
pinch_z_bottom = 740.0
pinch_z_top = pinch_z_bottom + pinch_d + hose_flat_t    # 822.6, rests on the flat hose
nip_z = pinch_z_bottom + pinch_d / 2.0 + hose_flat_t / 2.0
pinch_shaft = 20.0
slot = (22.0, 70.0)             # width, length (z) of the slots for the top roller
block = (50.0, 40.0, 34.0)      # sliding bearing blocks of the top roller (y, z, x thickness), outside the plates
spring = (25.0, 3.0, 50.0)      # OD, wire, free length (2x, 30 N/mm, preload)
spring_k = 30.0                 # N/mm
spring_pre = 5.0                # mm preload -> 150 N per spring
spring_bracket = (60.0, 6.0, 40.0)      # y, thickness (z), x outwards: angle on the plate above the slot

# Lower guide roller: the hose drops vertically from the bottom pinch roller and leaves over this roller
low_y = pinch_y
low_z = 260.0
low_d = 80.0

# Drive: 48 V worm gear motor, chain 08B (1/2") 12 -> 36 teeth onto the reel shaft
motor_rpm = 100.0               # gearbox output, rated
motor_nm = 30.0                 # rated
motor_w = 350.0
motor_kg = 7.0
chain_ratio = 36.0 / 12.0
chain_eta = 0.95
sprocket_big = 145.7            # pitch diameter 36T 1/2"
sprocket_small = 49.0           # 12T
sprocket_x = (-138.0, -131.0)   # chain plane (left, outside the bearing)
motor_dz = -250.0               # gearbox output shaft below the reel axis
gearbox = (90.0, 90.0, 90.0)    # x, y, z
gearbox_x0 = -154.0             # inner face of the gearbox (outboard of the bracket)
motor_body = (80.0, 150.0)      # D, length, pointing down from the gearbox
motor_bracket = (8.0, 280.0, 150.0)     # thickness (x), y, z; at x -146 .. -154
motor_standoff = (30.0, 120.0)  # 2 tubes O30 from the plate to the bracket, at y = reel_y -+ 120

# Controller box (motor driver, encoder input, radio link to the pump): on the outer face of the right plate
box = ((plate_x + plate_t, plate_x + plate_t + 110.0), (-480.0, -260.0), (760.0, 880.0))
box_bolt_z = 778.0              # 2 x M8 through the bottom web of the plate

# ---------------------------------------------------------------------
# Operation
# ---------------------------------------------------------------------
v_layout = 0.6                  # m/s, laying out (back tension 50 N)
v_rollup_max = 0.6              # m/s, the robot never drives faster than this while winding
tension_layout = 50.0           # N back tension
tension_wind = 150.0            # N winding tension (tight coil)
fill_time_extra = 1.2           # filling takes longer than volume / flow (outlets leak while filling)
drain_min = 6.0                 # min, gravity drain before winding
shift_min = 1.5                 # min, turn on the headland and line up for the next strip
battery_wh = 2400.0             # robot 48 V 50 Ah
drive_w = 150.0                 # W driving on grass (estimated)
idle_w = 25.0                   # W electronics, standing
