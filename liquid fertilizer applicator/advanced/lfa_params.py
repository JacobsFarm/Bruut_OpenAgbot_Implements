import math

# =====================================================================
# Liquid fertilizer applicator (renure / vloeibare kunstmest) - parameters
# Los werktuig, ontworpen rond de achterbalk van de Bruut OpenAgbot.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong werktuig: x = 0 midden, y = 0 hart van de achterste onderbalk van de robot
# (chassis_beam_1 "rear_outer"), z = 0 grond. Op de robot: wereld-y = y + robot_mount_y.
# Alle maten staan hier; nooit hardcoden in lfa_parts.py / build_lfa.py.
# =====================================================================

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbot design/agbot_params.py")
# ---------------------------------------------------------------------
robot_mount_y = -575            # align_length/2 + bracket_top_hole_dist_y/2
robot_beam_profile = 40         # kokerbalk 40 x 40 x 2
robot_beam_wall = 2
robot_beam_length = 1000
robot_beam_z_bot = 619          # ground_to_axle 215 + z_lower_beam_bot 404
robot_beam_z_top = robot_beam_z_bot + robot_beam_profile          # 659
robot_upper_beam_z_top = robot_beam_z_top + robot_beam_profile    # 699
robot_grid = 50                 # gatenraster M10 in de balken
robot_hole_d = 10.4
robot_hole_x_min = 125          # gaten chassis_beam_1 op x = +-125, +-175 ... +-475
robot_hole_x_max = 475
robot_inner_beam_y = 150        # rear_inner onderbalk (wereld -425)
robot_wheel_x = 375
robot_wheel_y = 75              # achteras: wereld -500
robot_axle_z = 215
robot_tire_d = 430
robot_tire_w = 100
robot_bracket_w = 228           # wielbeugel buitenmaat x
robot_bracket_l = 240           # wielbeugel y
robot_bracket_plate_z = 560     # onderkant top plate
robot_bracket_top_z = 564
robot_block_w = 140             # houten blok
robot_block_l = 190
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_y_rear = -75   # bovenste balken steken 75 mm achter de onderbalk uit
robot_upper_beam_y_front = 500  # alleen het achterste stuk tekenen

# ---------------------------------------------------------------------
# Rijen en werkbreedte
# ---------------------------------------------------------------------
row_spacing = 200
row_x = (-400.0, -200.0, 0.0, 200.0, 400.0)
work_width = row_spacing * len(row_x)       # 1000 mm

# ---------------------------------------------------------------------
# Gereedschapsbalk (toolbar) 60 x 60 x 4; 900 lang zodat alles binnen de robotbreedte (+-489) blijft.
# De werkbreedte is 5 x 200 = 1000 mm (elke rij bedient een strook van 200 mm).
# ---------------------------------------------------------------------
bar_size = 60
bar_wall = 4
bar_length = 900
bar_y = -395
bar_z = 400
bar_front = bar_y + bar_size / 2.0          # -365
bar_rear = bar_y - bar_size / 2.0           # -425
bar_top = bar_z + bar_size / 2.0            # 430
bar_bot = bar_z - bar_size / 2.0            # 370
bar_cap_t = 3

# ---------------------------------------------------------------------
# Aanbouwbok (headstock), vast aan de robotbalk, 2 stuks gespiegeld
# ---------------------------------------------------------------------
plate_t = 8
hs_x = 100                      # hart van de parallellogramstangen
hs_link_gap = 44                # binnenmaat tussen de wangen
hs_bolt_x = (125.0, 175.0)      # M10 door de robotbalk (gatenraster)
hs_top_x = (62.0, 200.0)
hs_top_y = (-28.0, 34.0)
hs_clamp_x = (100.0, 200.0)
hs_clamp_y = (-20.0, 34.0)
hs_back_y = (-28.0, -20.0)      # achterplaat tegen de achterkant van de balk
hs_z_bot = 375
hs_cheek_y_rear = -110
hs_cross_size = 40
hs_cross_y = 40                 # bovenste dwarsbuis boven de robotbalk; binnenwangen kragen daarvoor uit
hs_cross_z = 800                # draagt de langgatplaten van de actuator
hs_low_cross_size = 30
hs_low_cross_y = -43
hs_low_cross_z = 400
m10_d = 10.0
m10_af = 17
m10_k = 6.4
m10_m = 8.4

# ---------------------------------------------------------------------
# Parallellogram en hefinrichting
# ---------------------------------------------------------------------
pin_front_y = -80
pin_upper_z = 600
pin_lower_z = 420
link_length = 260
link_tube = 30                  # koker 30 x 30 x 3
link_wall = 3
link_boss_d = 32
pin_d = 16
pin_hole = 16.4
pin_rear_y = pin_front_y - link_length       # -340

rf_y = (bar_front, -318.0)      # achterframe-platen, gelast op de toolbar
rf_z = (375.0, 622.0)
rf_cross = 30                   # dwarsbuis tussen de achterframes (ophangpunt actuator)
rf_cross_y = -350
rf_cross_z = 480                # tussen de achterste pennen, boven de klemmen van element 3

lift_height = 140               # toolbar omhoog op de kopakker
unit_drop_deg = 8.0             # elementen zakken op hun aanslag (stelmoer) als de balk omhoog is
wheel_drop_deg = 12.0           # loopwiel zakt op zijn aanslag (ca. 60 mm uitslag naar beneden)

# elektrische lineaire actuator (bijv. 24 V, 2500 N, slag 150)
# Zweefstand: de bovenste pen zit in een langgat (act_slot) langs de actuator-as. In het werk staat de
# actuator volledig uit en kan de balk vrij zweven; bij heffen trekt de actuator het langgat dicht.
# Vlakke ligging (ca. 35 graden): weinig slag per mm hefhoogte, zodat 140 mm heffen en ruim zweven
# samen binnen 150 mm slag passen.
act_a = (5.0, 700.0)            # (y, z) onderkant langgat (pen ligt hier bij heffen), boven de robotbalk
act_b = (-320.0, 470.0)         # (y, z) onderste pen, aan het achterframe (beweegt mee)
act_stroke = 150
act_retracted = 290
act_extended = act_retracted + act_stroke     # 440: werkstand
act_slot = 85                   # langgat: balk zweeft ca. -75 / +64 mm rond de ontwerphoogte
act_tube_d = 54
act_rod_d = 25
act_eye_d = 26
act_eye_w = 16                  # oog van het huis, onderaan op het achterframe
act_rod_eye_w = 26              # stangoog bovenin; langgatplaten staan 27 mm uit elkaar zodat de stang ertussen schuift
act_motor = (70.0, 70.0, 150.0)  # parallelle motor, doorsnede x, y en lengte
act_motor_offset = 58

# ---------------------------------------------------------------------
# Injectie-element (5x), lokale x = 0 is het hart van de rij
# ---------------------------------------------------------------------
u_clamp_w = 60
u_clamp_t = 8
u_clamp_z = (340.0, 460.0)
u_bolt_d = 12
u_bolt_af = 19
u_bolt_k = 7.5
u_bolt_m = 10.8
u_bolt_dx = 20
u_bolt_dz = 46                  # bouten op bar_z +- 46, boven en onder de koker

u_tongue_t = 10
u_pivot = (bar_y - 95.0, 270.0)          # (y, z) draaipunt arm
u_pin_d = 20
u_fork_t = 6
u_fork_in = 21.5                         # binnenkant vorkplaat (x)
u_lug_rel = (-140.0, 40.0)               # pen veerpoot t.o.v. draaipunt
u_anchor_rel = (-150.0, 220.0)           # gat in de veerplaat t.o.v. draaipunt
u_anchor_plate = (56.0, 50.0, 8.0)       # y, x, dikte
u_disc_dx = 240                          # horizontale afstand draaipunt -> schijfas

# snijschijf + diepteringen (depth bands)
disc_d = 300
disc_t = 3
band_d = 220
band_w = 15
band_r_in = 85
work_depth = (disc_d - band_d) / 2.0     # 40 mm
disc_y = u_pivot[0] - u_disc_dx          # -730
disc_z = band_d / 2.0                    # 110: de ringen rollen op de grond
hub_d = 60
hub_half = 18
axle_d = 20

# mes (achter de schijf) en injectiebuisje, t.o.v. hart schijf (y, z)
knife_t = 8
knife_chord = 30
knife_tip_rel = (-125.0, -145.0)         # 5 mm minder diep dan de schijf
knife_edge_rel = (-165.0, 10.0)          # bovenpunt voorkant (lijn tip -> hier)
knife_top_z_rel = 40.0
knife_bolt_rel = ((-173.0, -15.0), (-184.0, 25.0))
knife_clamp_rel = (-185.0, 5.0)
tube_od = 8
tube_id = 6
tube_top_z = 200                         # wereld z, bovenkant buisje
valve_d = 18
valve_len = 40
barb_d = 10
barb_len = 15

# veerpoot
rod_d = 12
spring_od = 35
spring_wire = 5
spring_free = 160
spring_rate = 4.0                        # N/mm: zachte veer verdeelt het balkgewicht over de elementen
eye_d = 28
eye_w = 20
seat_d = 40
seat_offset = 45                         # lagere veerschotel boven de pen
stop_gap = 20                            # stelmoer = onderaanslag (arm zakt unit_drop_deg)

# ---------------------------------------------------------------------
# Loopwiel + aandrijving pomp
# ---------------------------------------------------------------------
gw_x = 312                      # hart loopwiel
gw_w = 40
gw_rim_d = 360
gw_d = 400                      # over de spikes
gw_spikes = 16
gw_spike_base = 28
gw_spike_w = 30
gw_hub_d = 60
gw_web_t = 4
gw_rolling_circ = 1190.0        # effectieve rolomtrek in gras (ijken in het veld)

jack = (bar_y - 45.0, 505.0)    # (y, z) as hulpas = draaipunt loopwielarm = pompas
jack_d = 20
jack_x = (160.0, 375.0)
gw_wheel_rel = (-300.0, -305.0)  # wielas t.o.v. hulpas
gw_arm_x = (278.0, 288.0)
gw_arm_w = 40
gw_axle_x = (262.0, 336.0)

chain_pitch = 12.7              # 08B-1 (1/2")
z_jack = 15
z_wheel = 30
sprocket_x = (266.5, 273.5)
chain_x = (266.0, 274.0)

bearing_plates_x = ((240.0, 248.0), (340.0, 348.0))
bearing_flange = (113.0, 60.0, 11.0)     # UCFL204: lengte, breedte, dikte
bearing_boss_d = 52
bearing_boss_len = 14
bearing_bolt_pitch = 90
torsion_x = (291.0, 324.0)
torsion_r = 26

sensor_d = 18
sensor_len = 50

# ---------------------------------------------------------------------
# Peristaltische pomp (5 kanalen, rollenpomp) en filter
# ---------------------------------------------------------------------
pump_x = (50.0, 150.0)
pump_half = 50.0                # behuizing 100 x 100 rond de pompas
pump_channels = 5
pump_tube_id = 6.4              # standaard slang, 1,6 mm wand
pump_roller_r = 35.0            # hart slang op de rollenbaan
pump_fill = 0.85                # vulgraad (afknijpen, rollen)
coupling_d = 40
coupling_x = (152.0, 172.0)
nipple_d = 10
nipple_len = 15
outlet_z = 475
inlet_y = -415
filter_d = 70
filter_z = (555.0, 700.0)
filter_y = -460
manifold_d = 22
manifold_z = 572
hose_od = 12
camlock_y = -250
