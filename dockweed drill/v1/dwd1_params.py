import math

# =====================================================================
# Dockweed drill v1 (ridderzuringfrees, X-as op alu-profielen met HGR15-rails) - parameters
# Portaal achter op de Bruut OpenAgbot: X-as (links-rechts, slag 1000) + Z-as (op-neer),
# de robot is de Y-as. Snellopende vermorzelfrees O180 in een pot O250 die op de zode landt.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong = midden van de robot. Het portaal hangt achter de achterste onderbalk (rear_outer).
# Hulpmaat v = afstand achter de achterkant van die balk: robot-y = robot_beam_rear_face - v.
# De onderdelen worden in (x, v, z) getekend en daarna gespiegeld naar robotcoordinaten (dwd1_parts.to_robot).
# Alle maten staan hier; nooit hardcoden in dwd1_parts.py / build_dwd1.py.
# =====================================================================

VARIANT = "v1"

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbots/agbot design/agbot_params.py")
# ---------------------------------------------------------------------
robot_beam = 40                     # kokerbalk 40 x 40 x 2
robot_beam_wall = 2
robot_beam_length = 1000            # onderste balken (x-richting), x = -500..500
robot_rear_beam_y = -575            # hart rear_outer onderbalk (align_length/2 + bracket_top_hole_dist_y/2)
robot_beam_rear_face = robot_rear_beam_y - robot_beam / 2.0      # -595: v = 0
robot_lower_beam_z = (619.0, 659.0)  # ground_to_axle 215 + z_lower_beam_bot 404
robot_upper_beam_z = (659.0, 699.0)
robot_upper_beam_x = (325.0, 425.0)  # bovenste balken (y-richting), hart
robot_upper_beam_end_y = -650.0
robot_grid = 50                     # gatenraster M10 in de balken
robot_hole_d = 10.4
robot_hole_x = tuple(125.0 + 50.0 * i for i in range(8))         # gaten onderbalk op x = +-125 .. +-475
robot_wheel_x = 375.0
robot_wheel_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_bracket_half_x = 114.0        # wielbeugel buitenmaat 228
robot_bracket_half_y = 120.0
robot_bracket_top_z = 564.0
robot_block_half_x = 70.0           # houten blok achter (140 x 190)
robot_block_half_y = 95.0
robot_frame_bolt_x = (325.0, 425.0)  # frame_bolts van de wielunit (bezet)

# robot (geschat, niet gemeten): massa en zwaartepunt zonder werktuig
robot_kg = 150.0
robot_cg_y = 0.0                    # midden tussen de assen
robot_cg_z = 450.0
battery_forward_cg_y = 150.0        # robotzwaartepunt als de accu (ca. 45 kg) 500 mm naar voren gaat (geschat)


def v_to_y(v):
    """Hulpmaat v (achter de balk) naar robot-y."""
    return robot_beam_rear_face - v


# ---------------------------------------------------------------------
# Stand van de machine (build): X van het spilhart en hoogte onderkant gereedschap
# ---------------------------------------------------------------------
x_stroke = 1000.0
x_min, x_max = -x_stroke / 2.0, x_stroke / 2.0
depth_std = 150.0                   # standaard freesdiepte (Ruud: 15 cm)
depth_max = 200.0
drive_z = 280.0                     # onderkant frees boven maaiveld tijdens rijden
z_ref = drive_z                     # referentiestand van de Z-slede in de build (rijstand)
work_x = 150.0                      # stand voor de standaardafbeeldingen
work_z = -depth_std

# ---------------------------------------------------------------------
# Aanbouwbok (headstock): 2 staanders achter de onderbalk, op het gatenraster
# Vrije gaten in rear_outer: x = +-225 en +-275 (+-325/+-425 = frame_bolts, +-375 boven het houten blok).
# ---------------------------------------------------------------------
hs_x = 250.0                        # hart staander
hs_bolt_dx = 25.0                   # M10 op x = hs_x +- 25 (gaten 225 en 275)
hs_bolt_v = -robot_beam / 2.0       # hart onderbalk
hs_plate_half_x = 50.0
hs_plate_t = 8.0                    # bovenplaat, klemplaat, achterplaat
up_size = 50.0                      # staander 50 x 50 x 3
up_wall = 3.0
up_v0 = hs_plate_t                  # voorkant staander (tegen de achterplaat)
up_v1 = up_v0 + up_size
up_z0 = robot_lower_beam_z[0] - hs_plate_t        # 611: onderkant klemplaat
up_z1 = 1110.0
up_cap_t = 6.0
gusset_t = 6.0
gusset_h = 130.0                    # schoor boven de bovenplaat, tegen de staander
cross_size = 40.0                   # dwarskoker tussen de staanders (draagt de E-kast)
cross_wall = 3.0
cross_z = (up_z0 + 4.0, up_z0 + 4.0 + cross_size)
m10_d = 10.0
m10_head_r = 9.2                    # AF17 over de hoeken / 2 (rond getekend)
m10_head_k = 6.4
m10_nut_m = 8.4

# ---------------------------------------------------------------------
# X-as v1: 2 alu-profielen 40 x 80 (sleuf 8) met elk een HGR15-rail, 4 wagens HGH15CA op de slede
# ---------------------------------------------------------------------
xbar_L = 1300.0                     # lengte alu-profielen
xbar_z = (760.0, 1060.0)            # hart onderste / bovenste profiel
prof_d = 80.0                       # profiel 80 diep (v), 40 hoog (z)
prof_h = 40.0
prof_v0 = up_v1                     # profiel met M8 + hamermoer tegen de staander
prof_v1 = prof_v0 + prof_d
rail_x_h = 28.0                     # HGR15 + HGH15CA
x_block_dx = 90.0                   # 2 wagens per rail op x = +-90 van het spilhart
end_plate_t = 10.0                  # kopplaat alu, buiten de profieleinden
belt_ref = prof_v1                  # riem en riemklemmen achter het profiel
clamp_x = (685.0, 715.0)            # riemklemmen buiten de kopplaten
slide_t = 10.0                      # X-slede alu
slide_v0 = prof_v1 + rail_x_h
slide_half_x = 150.0
slide_z = (700.0, 1120.0)
belt_z = 880.0
belt_w = 15.0
pulley_z = 923.0
motor_dx = 120.0                    # NEMA 23 + 5:1 naast het spilhart

# ---------------------------------------------------------------------
# Z-as: koker 120 x 60 x 3 met 2 HGR15-rails, SFU1610, NEMA 23 met rem
# ---------------------------------------------------------------------
rail_h = 28.0                       # HGR15 + HGH15CA
riser_t = 23.0
zt_w, zt_d, zt_wall = 120.0, 60.0, 3.0
zt_L = 950.0
zt_bottom = 400.0                   # onderkant Z-slede boven onderkant gereedschap
z_rail_dx = 40.0
screw_dv = 25.0                     # spindel 25 voor de Z-koker
nut_z = (890.0, 930.0)              # moerhuis op de X-slede

# ---------------------------------------------------------------------
# Spilbok, spil, motor
# ---------------------------------------------------------------------
sb_back_t = 6.0
spindle_dv = 75.0                   # hart spil achter de achterplaat
sb_lo = 368.0                       # onderste lagerplaat boven onderkant gereedschap
sb_hi = 528.0                       # bovenste lagerplaat
sb_mo = 660.0                       # motorplaat
shaft_d = 35.0
bearing_dist = sb_hi - sb_lo        # 160
motor_P = 1500.0                    # BLDC 48 V
motor_rpm = 3000.0
motor_peak = 2.0                    # VESC stroomgrens x nominaal
cutter_rpm = 1500.0
mower_rpm = 3000.0
idle_w = 80.0                       # verlies spil + lagers bij 1500 rpm (geschat)

# ---------------------------------------------------------------------
# Pot (rust met eigen gewicht op de zode, sensor = maaiveldreferentie)
# ---------------------------------------------------------------------
pot_d = 250.0
pot_h = 150.0
pot_t = 2.0
pot_rim = 30.0                      # potrand hangt in rust zoveel onder de freesonderkant
pot_rod_dx = 100.0
pot_rod_d = 16.0
pot_kg_est = 4.0
flap = True                         # rubber spatflap om de pot (maaien met opgetilde pot)

# ---------------------------------------------------------------------
# Gereedschap
# ---------------------------------------------------------------------
cutter_d = 180.0                    # vermorzelfrees: gat O180
cutter_teeth = 4
mower_tip_d = 230.0                 # maaischijf O200 met 3 mesjes
mower_rim = 30.0                    # mesjes 30 mm boven de grond als de pot erop staat

# ---------------------------------------------------------------------
# Aandrijving en proces
# ---------------------------------------------------------------------
stepper_T = 3.0                     # NEMA 23 closed-loop [Nm]
x_gear = 5.0
x_pulley_T = 20
htd_pitch = 5.0
z_lead = 10.0                       # SFU1610
plunge_v = 25.0                     # insteeksnelheid [mm/s]
rapid_x = 200.0
rapid_z = 100.0
dwell_s = 1.0
z_force_limit = 600.0               # software-begrenzing [N]
cut_energy = (0.5e6, 2.0e6)         # specifieke snij-energie grond + wortels [J/m3] (geschat)
cut_energy_std = 1.0e6
thrust_n = (150.0, 1.0)             # neerwaartse freeskracht: F0 + k * diepte [N, N/mm] (geschat)
side_force = 300.0                  # zijkracht op de frees (steen, wortel) [N]
drive_speed = 500.0                 # rijsnelheid tussen de planten [mm/s]
stop_start_s = 4.0                  # robot remmen, positioneren, optrekken

# ---------------------------------------------------------------------
# Camera, licht, elektra
# ---------------------------------------------------------------------
cam_dx = 110.0                      # +x: vrij van de spiraalkabel (-x)
cam_mast_z = (1000.0, 1420.0)
cam_reach_v = 300.0                 # camera zoveel achter het spilhart (kijkt voor de spil uit, rijrichting -y)
ebox = (300.0, 250.0, 120.0)        # IP65 kast (x, z, v)
ebox_z0 = 745.0
ebox_plate_t = 3.0                  # montageplaat E-kast op de dwarskoker
chain_z = xbar_z[1] + prof_h / 2.0 + 3.0   # kabelrups op het bovenste profiel (strip 3 mm)
spiral_turns = 26
