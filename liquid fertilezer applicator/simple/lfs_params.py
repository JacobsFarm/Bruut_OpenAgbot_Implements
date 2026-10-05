import math

# =====================================================================
# Liquid fertilizer applicator SIMPLE (eenvoudige toediener vloeibare meststof) - parameters
# Goedkope, robuuste variant van de toediener in ../advanved: vaste messen, een draaiend hefraam,
# twee kruiwagenwielen als dieptewiel en een 12 V membraanpomp met doseerplaatjes.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong werktuig: x = 0 midden, y = 0 hart van de achterste onderbalk van de robot
# (chassis_beam_1 "rear_outer"), z = 0 grond. Op de robot: wereld-y = y + robot_mount_y.
# Alle maten staan hier; nooit hardcoden in lfs_parts.py / build_lfs.py.
# Modulenamen beginnen met lfs_ zodat ze niet botsen met lfa_* van de geavanceerde variant.
# =====================================================================

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbot design/agbot_params.py", gelijk aan de geavanceerde variant)
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
# Rijen en werkbreedte (gelijk aan de geavanceerde variant)
# ---------------------------------------------------------------------
row_spacing = 200
row_x = (-400.0, -200.0, 0.0, 200.0, 400.0)
work_width = row_spacing * len(row_x)       # 1000 mm
work_depth = 40                             # mespunt onder maaiveld (ontwerp)

# ---------------------------------------------------------------------
# Aanbouwbok (headstock): 1 gelast deel op de achterste onderbalk
#   bovenplaat strip 150 x 10, klemstrip 50 x 10 onder de balk, 4 wangen strip 100 x 10 achter de balk
# ---------------------------------------------------------------------
hs_top_x = 200.0                # bovenplaat x = -200 .. 200
hs_top_y = (-120.0, 30.0)
hs_top_t = 10.0
hs_clamp_y = (-20.0, 30.0)      # klemstrip onder de balk (achterkant gelijk met de balk, wangen erachter)
hs_clamp_t = 10.0
hs_bolt_x = (125.0, 175.0)      # M10 door de robotbalk (bestaand gatenraster), 4 stuks
m10_d = 10.0
m10_af = 17
m10_k = 6.4
m10_m = 8.4

hs_cheek_t = 10.0
hs_cheek_y = (-120.0, -20.0)    # voorkant wang ligt tegen de achterkant van de robotbalk
hs_cheek_z_bot = 155.0          # wangen strip 100 x 10, 504 lang: draaipunt laag (kleine hefboom voor de trekkracht)
arm_x = 100.0                   # hart van de armen van het hefraam (x = +-100)
bush_len = 60.0                 # draaibus van de arm tussen twee wangen
bush_od = 30.0
bush_id = 16.5
pivot = (-70.0, 200.0)          # (y, z) draaipunt hefraam, bout M16; 240 mm boven de mespunt
pivot_bolt_d = 16.0
pivot_bolt_af = 24
pivot_bolt_k = 10.0
pivot_bolt_m = 13.0

# ---------------------------------------------------------------------
# Hefraam (1 gelast deel): balk 60x60x4, 2 armen 40x40x3 met draaibus, dwarsbuis 40x40x3
# ---------------------------------------------------------------------
bar_size = 60
bar_wall = 4
bar_length = 900
bar_y = -500
bar_z = 330
bar_front = bar_y + bar_size / 2.0          # -470
bar_rear = bar_y - bar_size / 2.0           # -530
bar_top = bar_z + bar_size / 2.0            # 360
bar_bot = bar_z - bar_size / 2.0            # 300
bar_cap_t = 3

arm_size = 40
arm_wall = 3
cross_y = -365.0                # dwarsbuis tussen de armen (draagt het huis van de actuator)
cross_size = 40
cross_wall = 3
cross_drop = 20.0               # bovenkant dwarsbuis gelijk met de hartlijn van de armen

# ---------------------------------------------------------------------
# Heffen: 1 elektrische lineaire actuator 12/24 V, 1500 N, slag 200 (inbouw 310 / uit 510).
# Huis met motor onderaan op de dwarsbuis van het hefraam, stangoog boven in een langgat in de bok (zweefstand).
# Werk = actuator helemaal uit, heffen = helemaal in: alleen de eindschakelaars van de actuator.
# ---------------------------------------------------------------------
act_a = (-130.0, 710.0)         # (y, z) onderkant langgat in de bok (hier trekt de stang bij heffen)
act_l = (-360.0, 309.0)         # (y, z) pen huis op het hefraam, in werkstand
act_retracted = 310.0
act_stroke = 200.0
act_extended = act_retracted + act_stroke    # 510
float_down_deg = 9.0            # (afgeleid) hefraam zakt zoveel graden onder de ontwerpstand: stang onderin het langgat
float_up_deg = 11.0             # hefraam mag zoveel omhoog zweven voordat de stang bovenin het langgat komt
act_pin_d = 10.0                # pennen M10 (standaard ogen van goedkope actuatoren)
act_pin_hole = 10.5
act_tube_d = 38.0               # aluminium buis
act_rod_d = 20.0
act_eye_d = 24.0
act_eye_w = 20.0
act_motor_d = 36.0              # parallelle motor naast de buis
act_motor_len = 110.0
act_motor_offset = 40.0
act_lug_t = 8.0
act_lug_gap = 22.0              # binnenmaat tussen de ogen (oog 20 breed, stang O 20 schuift ertussen)

# ---------------------------------------------------------------------
# Injectiemes (5x), lokale x = 0 is het hart van de rij
#   houder: bodemplaat strip 80x10 onder de balk + 2 zijplaten strip 80x8, vastgezet met 2 beugelbouten M12
#   mes: strip 50 x 10, voorkant geslepen, 25 graden naar achteren hellend (snijkant loopt omhoog naar achteren)
#   draaibout M12 + breekbout M6 (4.6): bij een steen breekt de breekbout en klapt het mes naar achteren
# ---------------------------------------------------------------------
h_plate_w = 80.0                # bodemplaat x
h_plate_y = (-550.0, -450.0)
h_plate_t = 10.0
ubolt_d = 12.0
ubolt_dx = 28.0                 # beugelbouten op rij +- 28
ubolt_nut_af = 19
ubolt_nut_m = 10.8
side_t = 8.0
side_y = (-545.0, -465.0)
side_z_bot = 175.0
knife_t = 10.0
knife_w = 50.0
knife_angle = 25.0              # graden achter de verticaal (punt voorop)
knife_pivot = (-520.0, 262.0)   # (y, z) draaibout M12 door zijplaten en mes
knife_top_z = 287.0             # bovenkant mes (recht afgezaagd)
shear_dist = 50.0               # breekbout 50 mm onder de draaibout, langs de mes-as
shear_d = 6.0
knife_rake_deg = 15.0           # onderkant mes loopt 15 graden op naar achteren: punt voorop, trekt het mes de grond in
clip_z = (40.0, 150.0)          # 2 slangklemmen (P-clips) die het buisje tegen de achterkant van het mes houden
tube_od = 10.0                  # RVS 316 buis 10 x 1
tube_id = 8.0
tube_gap = 1.5
tube_out_z = -25.0              # uitstroom 25 mm onder maaiveld, direct achter het mes
tube_top_z = 340.0
nozzle_d = 26.0                 # spuitdophouder met membraan-antidruppelklep en doseerplaatje (bajonetdop)
nozzle_len = 48.0
nozzle_cap_d = 32.0
nozzle_cap_len = 14.0
nozzle_inlet_d = 10.0
nozzle_inlet_len = 22.0

# ---------------------------------------------------------------------
# Dieptewielen (2x): kruiwagenwiel 3.00-4 (O 260, as 20), vork van strip 40x8,
# steel koker 40x40x3 in een huls 50x50x4 voor op de balk, stelpen O 12 (gaten om de 15 mm)
# ---------------------------------------------------------------------
gw_x = (-300.0, 300.0)
gw_d = 260.0
gw_w = 80.0
gw_rim_d = 102.0                # 4 inch velg
gw_hub_len = 86.0
gw_axle = (-350.0, 130.0)       # (y, z) wielas in werkstand (onder de mespunten)
gw_axle_d = 20.0
gw_fork_t = 8.0
gw_fork_w = 40.0
gw_fork_gap = 88.0              # binnenmaat vork
sleeve_size = 50.0
sleeve_wall = 4.0
sleeve_y = (-460.0, -410.0)     # huls voor de klemplaat
sleeve_z = (280.0, 400.0)
stem_size = 40.0
stem_wall = 3.0
stem_z_bot = 253.0              # onderkant steel = bovenkant kroonplaat vork
stem_len = 230.0
crown_t = 8.0
gw_clamp_w = 100.0              # klemplaat strip 100x10 voor op de balk
gw_clamp_y = (-470.0, -460.0)
gw_clamp_z = (275.0, 400.0)
gw_ubolt_d = 10.0
gw_ubolt_dx = 38.0              # beugelbouten M10 op wiel +- 38
depth_pin_d = 12.0
depth_hole_pitch = 15.0         # 15 mm per gat: werkdiepte 25 / 40 / 55 mm

# ---------------------------------------------------------------------
# Dosering: 12 V membraanpomp met interne bypass -> vaste drukregelaar 2,0 bar -> verdeelblok 5x
# -> 5 slangen -> spuitdophouder met antidruppelklep (0,5 bar) en doseerplaatje -> RVS-buisje achter het mes
# ---------------------------------------------------------------------
pressure_bar = 2.0              # vaste drukregelaar (voorgeprogrammeerd, zoals in druppelirrigatie)
check_valve_bar = 0.5           # openingsdruk membraanklep in de spuitdophouder
orifice_cd = 0.65               # uitstroomcoefficient doseerplaatje (aangenomen; ijken!)
orifice_d = 1.0                 # standaard doseerplaatje (mm)
orifice_sizes = (0.6, 0.8, 1.0, 1.2, 1.5)     # 1,5 mm x 5 rijen = 5,5 l/min: grens van de pomp
liquid_density = 1.2            # kg/l (mineralenconcentraat 1,0-1,1; UAN 1,3)
work_speed = 0.75               # m/s (2,7 km/h), gelijk aan de animatie van de geavanceerde variant
pump_flow_l_min = 7.0           # nominaal debiet pomp (bijv. 1,8 GPM-klasse)
pump_current_a = 5.0            # bij 12 V en 2-3 bar (ca. 60 W)

# doseerunit op de bovenplaat van de bok (vast aan de robot, z = bovenkant plaat 669); alleen de 5 slangen naar de
# messen bewegen mee met het hefraam. Links de pomp (liggend langs x), rechts filter + camlock, drukregelaar,
# verdeelblok met de uitgangen naar achteren.
pump_axis = (-55.0, 708.0)          # (y, z) as motor/pompkop
pump_head_x = (-105.0, -30.0)       # pompkop (binnenkant, naast de langgatplaten)
pump_head = (95.0, 80.0)            # breedte y, hoogte
pump_motor_x = (-205.0, -105.0)
pump_motor_d = 66.0
pump_feet = ((-200.0, -35.0), (-95.0, -15.0))     # x, y voetplaat
filter_xy = (150.0, -50.0)         # zuigfilter staand, camlock 1" bovenop (slang naar de tank op de robot)
filter_d = 60.0
filter_len = 110.0
camlock_len = 62.0
manifold_x = (45.0, 185.0)          # verdeelblok 5 uitgangen, slangpilaren naar achteren
manifold_y = (-118.0, -90.0)
manifold_size = 28.0
regulator_x = 70.0                  # vaste drukregelaar 2,0 bar staand op het verdeelblok, manometer aan de voorkant
regulator_d = 44.0
regulator_len = 55.0
gauge_d = 63.0
hose_od = 12.0                      # PVC 8 x 12 mm
link_hose_od = 16.0                 # verbindingsslang filter -> pomp -> regelaar
