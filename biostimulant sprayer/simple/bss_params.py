import os
import sys

# =====================================================================
# Biostimulant sprayer (simple) - parameters
# Sprays biostimulants over the whole field at the right moment: compost tea, seaweed extract, or nitrogen-fixing
# bacteria (e.g. Corteva Utrisha N). No plant-by-plant precision; every pass is logged (product, rate, time, weather,
# GNSS track) so treated and untreated strips can be compared afterwards.
# The spot sprayer ("spotspray unit/boom") is used as it is - tank, pump, filter, regulator, control box and the 3.75 m
# folding boom, imported, not copied - with these changes:
#   - all 15 nozzles open, twin flat-fan turbulence tips size 02 (orifice ~0.9 mm, coarse from 1 bar) instead of 015
#     flat fans: compost tea through the 50-mesh filter does not block them, and coarse drops do not drift
#   - an aerator: 12 V air pump on the end of the rear cradle tube, air hose to a diffuser on the tank floor, to keep
#     compost tea aerobic and seaweed / bacteria products mixed
#   - a weather mast instead of the camera mast: an all-in-one weather sensor (wind, temperature, humidity, rain) on a
#     1.45 m mast on the rear lower beams; the controller only sprays inside the weather window and logs it
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

SSP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "spotspray unit", "boom")
if SSP_FOLDER not in sys.path:
    sys.path.append(SSP_FOLDER)
import ssp_params as S          # noqa: E402  (the whole spot sprayer except the camera mast)

robot_kg = S.robot_kg
robot_axle_y = S.robot_axle_y
robot_lower_beam_y = S.robot_lower_beam_y
robot_lower_beam_z = S.robot_lower_beam_z
m10_hole = S.m10_hole

# ---------------------------------------------------------------------
# Weather mast: square tube 30 x 30 x 2 on a foot plate that shares the 2 right-hand control-box bolts (x 275) on the
# rear lower beams; 2 braces to the box base plate. Sensor on top above the tank and the folded wings' hinges.
# ---------------------------------------------------------------------
mast_xy = (275.0, -500.0)
mast = 30.0
mast_wall = 2.0
mast_foot = ((250.0, 300.0), (-600.0, -400.0), 6.0)     # x, y, t: on top of the box base plate (4 mm)
mast_top_z = 1450.0
brace_d = 16.0
brace_top_z = 1000.0
brace_y = (-548.0, -452.0)      # brace feet on the foot plate, between the 2 box bolts (y -575, -425)
sensor = (150.0, 180.0)         # all-in-one weather sensor (ultrasonic wind, T, RH, rain): d, h
sensor_arm = 60.0               # sensor sits on a short adapter above the mast cap

# ---------------------------------------------------------------------
# Aerator: 12 V diaphragm air pump 30 l/min clamped on the rear tank strap, air hose into a bulkhead in the tank top and
# a stainless down-tube to a diffuser ring on the tank floor
# ---------------------------------------------------------------------
air_pump_xy = (0.0, S.cradle_y[0])
air_pump_box = (110.0, 50.0, 90.0)
air_inlet_xy = (0.0, -300.0)    # bulkhead in the tank top
air_q = 30.0                    # l/min of air
air_w = 25.0
air_hose_d = 10.0
diffuser_r = 150.0              # ring on the tank floor, around the tank centre
diffuser_d = 16.0
diffuser_xy = (0.0, -40.0)

# ---------------------------------------------------------------------
# Nozzles and spray (the bodies of the spot sprayer stay; only the tips change)
# ---------------------------------------------------------------------
tip_q_3bar = 0.79               # l/min of a size 02 tip at 3 bar (ISO 02)
spray_p = 1.5                   # bar: coarse drops, gentle on living organisms
speed = 2.0                     # m/s (7.2 km/h) on grassland
mesh_um = 300.0                 # 50-mesh suction filter of the spot sprayer
orifice_mm = 0.9                # size 02 turbulence tip (estimated)
max_particle_ratio = 1.0 / 3.0  # particles below 1/3 of the orifice pass without bridging (rule of thumb)
pump_q = S.pump_q_3bar          # l/min, the diaphragm pump at 3 bar (more at 2 bar: conservative)
shear_ok_bar = 4.0              # diaphragm pumps below ~4 bar keep most bacteria / fungi alive (estimated)

# Weather window for living products (estimated, product labels and practice): spray when all are inside
WINDOW = {"wind_max_m_s": 3.5, "t_min_c": 8.0, "t_max_c": 25.0, "rh_min_pct": 60.0, "no_rain_h": 2.0,
          "uv_low": True}
# a day of weather for the spray window example (hour, wind m/s, T C, RH %, rain mm) - a May day, estimated
DAY = ((4, 1.0, 9.0, 92, 0.0), (5, 1.2, 9.5, 90, 0.0), (6, 1.5, 11.0, 85, 0.0), (7, 2.0, 13.0, 78, 0.0),
       (8, 2.5, 15.0, 70, 0.0), (9, 3.0, 17.5, 62, 0.0), (10, 3.8, 19.5, 55, 0.0), (11, 4.2, 21.0, 50, 0.0),
       (12, 4.5, 22.5, 46, 0.0), (13, 4.6, 23.5, 44, 0.0), (14, 4.4, 24.0, 44, 0.0), (15, 4.0, 23.5, 47, 0.0),
       (16, 3.5, 22.5, 51, 0.0), (17, 3.0, 21.0, 56, 0.0), (18, 2.4, 19.0, 63, 0.0), (19, 1.8, 17.0, 70, 0.0),
       (20, 1.2, 15.0, 77, 0.0), (21, 0.8, 13.5, 83, 0.0), (22, 0.6, 12.0, 87, 0.0))

# Products (rate l/ha of spray liquid, product per ha, note)
PRODUCTS = {
    "compost_tea": {"rate_l_ha": 150.0, "product": "50-100 l tea per ha, diluted", "aerate": True},
    "seaweed_extract": {"rate_l_ha": 150.0, "product": "2-4 l/ha concentrate", "aerate": False},
    "n_fixing_bacteria": {"rate_l_ha": 150.0, "product": "333 g/ha (Utrisha N label class)", "aerate": False},
}

field_eff = 0.80                # turns at the headland, refills on the field edge
refill_min = 8.0                # minutes per refill from the mobile refiller at the field edge (estimated)
battery_kwh = S.battery_kwh
drive_w_per_m_s = S.drive_w     # W per m/s on grass (as the spot sprayer)
logger_w = 15.0                 # controller, GNSS logging, weather sensor, LTE

# from build_bss.mass_properties() (update after a change of the model)
MODEL_MASS = {"total_kg": 82.5, "cg": (11.0, -481.0, 687.0)}
