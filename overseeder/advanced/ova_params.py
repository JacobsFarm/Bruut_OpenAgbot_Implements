import math

# =====================================================================
# Doorzaaimachine, geavanceerde versie (overseeder advanced) - parameters
# Basis: de geavanceerde toediener (../../liquid fertilezer applicator/advanved): aanbouwbok, parallellogram,
# zwevende balk met actuator en langgat, elementen met vorkarm, schijf tussen twee vorkplaten, diepteringen aan
# beide kanten en een veerpoot. Anders dan de toediener:
#   - 8 rijen op 125 mm; per rij een gebogen zaaikouter direct achter de schijf en een aandrukrol in een gaffel;
#   - 2 gasveren in het langgat duwen de zwevende balk omlaag met robotgewicht (net als de eenvoudige versie);
#   - luchtzaaier: zaadbak, dosering en 12 V-ventilator op een frame boven de achteras van de robot (niet op de
#     balk, die hangt al ver achter de robot); de lucht blaast het zaad door slangen naar de zaaikouters;
#   - geen loopwiel: de doseermotoren volgen de rijsnelheid van de robot.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong werktuig: x = 0 midden, y = 0 hart van de achterste onderbalk van de robot
# (chassis_beam_1 "rear_outer"), z = 0 grond. Op de robot: wereld-y = y + robot_mount_y.
# Alle maten staan hier; nooit hardcoden in ova_parts.py / build_ova.py.
# Modulenamen beginnen met ova_ (eenvoudige versie: ovs_, toedieners: lfa_, lfs_, lfs2_).
# =====================================================================

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbot design/agbot_params.py")
# ---------------------------------------------------------------------
robot_mount_y = -575
robot_beam_profile = 40
robot_beam_wall = 2
robot_beam_length = 1000
robot_beam_z_bot = 619
robot_beam_z_top = robot_beam_z_bot + robot_beam_profile          # 659
robot_upper_beam_z_top = robot_beam_z_top + robot_beam_profile    # 699
robot_grid = 50
robot_hole_d = 10.4
robot_hole_x_min = 125
robot_hole_x_max = 475
robot_inner_beam_y = 150        # rear_inner onderbalk (wereld -425)
robot_wheel_x = 375
robot_wheel_y = 75              # achteras: wereld -500
robot_axle_z = 215
robot_tire_d = 430
robot_tire_w = 100
robot_bracket_w = 228
robot_bracket_l = 240
robot_bracket_plate_z = 560
robot_bracket_top_z = 564
robot_block_w = 140
robot_block_l = 190
robot_upper_beam_x = (325.0, 425.0)
robot_upper_beam_y_rear = -75
robot_upper_beam_y_front = 500

# ---------------------------------------------------------------------
# Rijen en zaaidiepte
# ---------------------------------------------------------------------
row_spacing = 125.0
rows_per_module = 8
module_pitch = 1000.0
row_x = tuple(-437.5 + row_spacing * i for i in range(rows_per_module))
work_width = row_spacing * rows_per_module          # 1000 mm
work_speed = 0.75               # m/s

# ---------------------------------------------------------------------
# Gereedschapsbalk 60 x 60 x 4 met koppelflenzen (module 1000 mm van flens tot flens)
# ---------------------------------------------------------------------
bar_size = 60
bar_wall = 4
bar_x = (-492.0, 492.0)
bar_y = -395
bar_z = 400
bar_front = bar_y + bar_size / 2.0          # -365
bar_rear = bar_y - bar_size / 2.0           # -425
bar_top = bar_z + bar_size / 2.0            # 430
bar_bot = bar_z - bar_size / 2.0            # 370
flange_t = 8.0
flange_size = 100.0
flange_hole_off = 38.0
flange_bolt_d = 12.0

# ---------------------------------------------------------------------
# Aanbouwbok (2 stuks gespiegeld), gelijk aan de toediener maar met de stangen op x = +-125
# (in de opening tussen element 5 en 6: de klemmen van de elementen zitten op x = 62,5 +- 28 en 187,5 +- 28)
# ---------------------------------------------------------------------
plate_t = 8
hs_x = 125                      # hart van de parallellogramstangen
hs_link_gap = 44                # binnenmaat tussen de wangen
hs_bolt_x = (125.0, 175.0)      # M10 door de robotbalk (gatenraster)
hs_top_x = (62.0, 200.0)
hs_top_y = (-28.0, 34.0)
hs_clamp_x = (100.0, 200.0)
hs_clamp_y = (-20.0, 34.0)
hs_back_y = (-28.0, -20.0)
hs_z_bot = 375
hs_cheek_y_rear = -110
hs_cross_size = 40
hs_cross_y = 40
hs_cross_z = 800
hs_low_cross_size = 30
hs_low_cross_y = -43
hs_low_cross_z = 400
m10_d = 10.0
m10_af = 17
m10_k = 6.4
m10_m = 8.4

# ---------------------------------------------------------------------
# Parallellogram en hefinrichting (gelijk aan de toediener)
# ---------------------------------------------------------------------
pin_front_y = -80
pin_upper_z = 600
pin_lower_z = 420
link_length = 260
link_tube = 30
link_wall = 3
link_boss_d = 32
pin_d = 16
pin_hole = 16.4
pin_rear_y = pin_front_y - link_length       # -340

rf_y = (bar_front, -318.0)
rf_z = (375.0, 622.0)
rf_cross = 30
rf_cross_y = -350
rf_cross_z = 480

lift_height = 150                # toediener: 140; actuator in = 290 mm
unit_drop_deg = 8.0

# actuator 24 V, 2500 N, slag 150, omgedraaid: huis op het achterframe (B), stang in het langgat (A)
act_a = (5.0, 706.0)             # 6 mm hoger dan de toediener: stang blijft in de laagste zweefstand vrij van de robotbalk
act_b = (-320.0, 470.0)
act_stroke = 150
act_retracted = 290
act_extended = act_retracted + act_stroke     # 440: werkstand
act_slot = 85
act_tube_d = 54
act_rod_d = 25
act_eye_d = 26
act_eye_w = 16
act_rod_eye_w = 26
act_motor = (70.0, 70.0, 150.0)
act_motor_offset = 58

# 2 gasveren naast de langgatplaten: duwen de pen in het langgat naar beneden (naar B). Onderin het langgat
# (heffen) drukken ze tegen de bok zelf en belasten ze de actuator niet.
gas_force = (420.0, 560.0)      # N, beide samen: pen onderin / bovenin het langgat
gas_len_ext = 225.0             # oog-oog met de pen onderin het langgat (bovenin: 140)
gas_body_d = 19.0
gas_body_len = 100.0
gas_rod_d = 8.0
gas_eye_d = 18.0
gas_eye_w = 8.0
gas_dx = 34.0                   # hart gasveer t.o.v. x = 0 (buiten de langgatplaten, die op +-13,5..19,5 staan)

# ---------------------------------------------------------------------
# Zaai-element (8x), lokale x = 0 is het hart van de rij (gelijk aan het element van de toediener, behalve
# kouter, dieptering, korter en de aandrukrol)
# ---------------------------------------------------------------------
u_clamp_w = 56
u_clamp_t = 8
u_clamp_z = (340.0, 460.0)
u_bolt_d = 12
u_bolt_af = 19
u_bolt_k = 7.5
u_bolt_m = 10.8
u_bolt_dx = 19
u_bolt_dz = 46

u_tongue_t = 10
u_pivot = (bar_y - 95.0, 270.0)          # (-490, 270) draaipunt arm
u_pin_d = 20
u_fork_t = 5                             # lasergesneden, 5 mm (toediener: 6)
u_fork_in = 21.5                         # binnenkant vorkplaat (x)
u_lug_rel = (-70.0, 40.0)                # pen veerpoot t.o.v. draaipunt (toediener: -140): korte hefboom,
                                         # meer voorspanning, de kracht wisselt minder met de armhoek
u_anchor_rel = (-75.0, 220.0)            # gat in de veerplaat t.o.v. draaipunt
u_anchor_plate = (56.0, 50.0, 8.0)       # y, x, dikte
u_disc_dx = 200                          # horizontale afstand draaipunt -> schijfas (toediener: 240)

# snijschijf + diepteringen aan beide kanten
disc_d = 300
disc_t = 3
band_d = 270                             # diepte = (300 - 270) / 2 = 15 mm; wisselringen 290 / 280 / 260 / 250
band_w = 15
band_r_in = 85
band_sizes = (290.0, 280.0, 270.0, 260.0, 250.0)
work_depth = (disc_d - band_d) / 2.0     # 15 mm
disc_y = u_pivot[0] - u_disc_dx          # -690
disc_z = band_d / 2.0                    # 135: de ringen rollen op de grond
hub_d = 60
hub_half = 18
axle_d = 20

# zaaikouter (gebogen, 16 mm dik, slijtvast staal) direct achter de schijf, in het vlak van de schijf.
# Omtrek t.o.v. hart schijf (y, z): voorkant volgt de schijf op 5 mm, punt 3 mm boven de onderkant van de schijf.
boot_t = 16.0
boot_r = 155.0                           # voorkant op deze straal rond het hart van de schijf
boot_lift = 3.0                          # punt zoveel boven de onderkant van de schijf: zaad op ca. 12 mm
boot_arc_deg = (17.0, 90.0)              # boog van de voorkant, gemeten vanaf recht onder het hart naar achteren
boot_top_z_rel = 12.0
boot_rear_rel = ((-200.0, 12.0), (-160.0, -100.0), (-85.0, -150.0))
boot_bolt_rel = ((-178.0, -5.0), (-168.0, -40.0))
boot_clamp_rel = (-175.0, -20.0)         # vorkplaten lopen tot hier (r 30) en houden de kouter met 2 bouten M10
seed_tube_od = 16.0                      # RVS 16 x 1,5, in de kouter tot de bodem van de sleuf
seed_tube_id = 13.0
seed_tube_rel_y = -182.0
seed_tube_top_z = 300.0                  # wereld z, bovenkant zaadbuis; slang 20/26 erover

# aandrukrol O 200 x 40 in een gaffel (2 strips 30 x 5) aan de buitenkant van de vorkplaten, torsieveer
pw_d = 200.0
pw_w = 40.0
pw_hub_d = 50.0
pw_axle_rel = (-335.0, -35.0)            # t.o.v. hart schijf: rol op het maaiveld
pw_pivot_rel = (-200.0, 40.0)            # scharnier gaffel op de vorkplaten (2 schouderbouten M12)
pw_yoke_t = 5.0
pw_yoke_w = 30.0
pw_yoke_x = (28.0, 33.0)                 # buitenkant vorkplaat 27,5 -> gaffel
pw_range = (-35.0, 22.0)                 # graden gaffelhoek: 35 omhoog, 22 omlaag (aanslagen)
pw_force = 35.0                          # N op de rol in werkstand (torsieveer, aangenomen)
pw_rate = 0.6                            # N per graad
pw_axle_d = 16.0

# veerpoot (gelijk aan de toediener)
rod_d = 12
spring_od = 35
spring_wire = 5
spring_free = 237                        # voorgespannen: ca. 440 N in werkstand (stelt de zweefhoogte)
spring_rate = 4.0
eye_d = 28
eye_w = 20
seat_d = 40
seat_offset = 45

# ---------------------------------------------------------------------
# Luchtzaaier op de robot: draagframe op de bok en de binnenste achterbalk, zaadbak met 2 vakken, 2 nokkenrollen,
# 8 venturi's in een luchtkanaal, 12 V-ventilator. Slangen 20/26 naar de zaaikouters.
# ---------------------------------------------------------------------
sf_x = (-300.0, 300.0)          # draagframe koker 40 x 40 x 3
sf_y = (-60.0, 260.0)
sf_z = (870.0, 910.0)
sf_tube = 40.0
sf_rear_leg_x = (106.0, 146.0)  # achterste poten: platen 40 x 8 op de bovenplaat van de bok, naast de bouten
sf_rear_leg_y = (-26.0, -18.0)
sf_front_leg_x = (230.0, 270.0) # voorste poten: koker 40 x 40 op de binnenste achterbalk (M10 in het raster)
sf_front_leg_y = (130.0, 170.0)

duct_d = 60.0                   # luchtkanaal (PVC) langs x, venturi per rij
duct_y = 0.0
duct_z = 945.0
duct_x = (-285.0, 285.0)
outlet_x = tuple(-245.0 + 70.0 * i for i in range(rows_per_module))
outlet_len = 45.0               # nippel naar achteren (-y)
outlet_d = 26.0
drop_d = 24.0                   # valbuisje van de doseerrol naar de venturi

meter_x = (-290.0, 290.0)
meter_y = (-38.0, 38.0)
meter_z = (995.0, 1055.0)
shaft_main_y = -15.0
shaft_fine_y = 17.0
shaft_z = 1025.0
shaft_d = 12.0
motor_box = (32.0, 45.0, 60.0)
motor_d = 37.0
motor_len = 70.0

hop_x = (-280.0, 280.0)         # smaller dan het doseerhuis: de motoren staan ernaast
hop_wall = 2.0                  # aluminium
hop_y = (-60.0, 340.0)          # steekt 80 mm voor het draagframe uit
hop_side_z = 1150.0
hop_top_z = 1450.0
hop_divider = ((1.0, 1055.0), (40.0, 1450.0))    # schot onderaan tussen de rollen; achter = fijn zaad
lid_t = 3.0

hop_post_x = 270.0              # 2 steunplaten 6 mm van de voorste framebuis naar de trechter (x = +-270)
hop_post_t = 6.0
fan_xy = (-170.0, 125.0)        # radiaalventilator 12 V, staand op het frame onder de trechter
fan_d = 170.0
fan_h = 90.0
fan_outlet_d = 50.0

roll_main_cc = 2.0              # cm3 per omwenteling per uitloop (ijken)
roll_fine_cc = 0.15
motor_rpm_max = 60.0
seed_hose_od = 26.0
hose_lane_dx = 50.0             # slang loopt tussen de elementen door omhoog (x_rij + 50)
hose_high_z = 830.0             # hoogte waarop de slangen naar voren lopen (boven parallellogram en actuator)
