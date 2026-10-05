import math

# =====================================================================
# Doorzaaimachine (overseeder) voor de Bruut OpenAgbot - parameters
# Eenvoudige versie (zie ../advanced voor de geavanceerde).
# Basis: de eenvoudige toediener versie 2 (../../liquid fertilezer applicator/simple_v2): dezelfde bok, hetzelfde
# hefraam met actuator en langgat. Anders:
#   - per rij een zaai-element aan een eigen sleeparm met veerpoot (bodemvolging per rij),
#   - een vlakke schijf onder 7 graden snijdt een ondiepe V-sleuf (15 mm), een zaaischoen in de schaduw van de
#     schijf legt het zaad op de bodem van de sleuf; een dieptering op de schijf bepaalt de diepte precies
#     waar gesneden wordt, een smalle aandrukrol op een eigen verende arm drukt de sleuf dicht,
#   - zaadbak met twee vakken (gras / fijn zaad) en twee nokkenrollen op het hefraam i.p.v. de pomp,
#   - 8 rijen op 125 mm per module van 1000 mm; modules met flenzen naast elkaar te koppelen.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong werktuig: x = 0 midden, y = 0 hart van de achterste onderbalk van de robot
# (chassis_beam_1 "rear_outer"), z = 0 grond. Op de robot: wereld-y = y + robot_mount_y.
# Alle maten staan hier; nooit hardcoden in ovs_parts.py / build_ovs.py.
# Modulenamen beginnen met ovs_ zodat ze niet botsen met lfs_/lfs2_/lfa_ in dezelfde FreeCAD-sessie.
# =====================================================================

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbot design/agbot_params.py", gelijk aan de toedieners)
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
# Rijen, module en zaaidiepte
# ---------------------------------------------------------------------
row_spacing = 125.0
rows_per_module = 8
module_pitch = 1000.0           # van flens tot flens: naast elkaar gekoppeld blijft de rijafstand 125 mm
row_x = tuple(-437.5 + row_spacing * i for i in range(rows_per_module))
work_width = row_spacing * rows_per_module          # 1000 mm
disc_depth = 15.0               # snijdiepte schijf (ontwerp) = (schijf - dieptering) / 2; wisselringen 5..25 mm
boot_lift = 3.0                 # onderkant zaaischoen zoveel boven de onderkant van de schijf: zaad op ca. 12 mm
work_speed = 0.75               # m/s (2,7 km/h), gelijk aan de toedieners

# ---------------------------------------------------------------------
# Aanbouwbok (headstock): gelijk aan simple_v2, alleen de armen staan op x = +-62.5 (tussen de elementen door)
#   bovenplaat strip 150 x 10, klemstrip 50 x 10 onder de balk, 4 wangen strip 100 x 10 achter de balk
# ---------------------------------------------------------------------
hs_top_x = 200.0                # bovenplaat x = -200 .. 200
hs_top_y = (-120.0, 30.0)
hs_top_t = 10.0
hs_clamp_y = (-20.0, 30.0)
hs_clamp_t = 10.0
hs_bolt_x = (125.0, 175.0)      # M10 door de robotbalk (bestaand gatenraster), 4 stuks
m10_d = 10.0
m10_af = 17
m10_k = 6.4
m10_m = 8.4

hs_cheek_t = 10.0
hs_cheek_y = (-120.0, -20.0)
hs_cheek_z_bot = 155.0
arm_x = 62.5                    # hart van de armen van het hefraam: in de opening tussen element 4/5 en hun buren
bush_len = 60.0
bush_od = 30.0
bush_id = 16.5
pivot = (-70.0, 200.0)          # (y, z) draaipunt hefraam, bout M16 (gelijk aan simple_v2)
pivot_bolt_d = 16.0
pivot_bolt_af = 24
pivot_bolt_k = 10.0
pivot_bolt_m = 13.0

# ---------------------------------------------------------------------
# Hefraam (1 gelast deel): balk 60x60x4 met koppelflenzen, 2 armen 40x40x3 met draaibus, dwarsbuis 40x40x3
# ---------------------------------------------------------------------
bar_size = 60
bar_wall = 4
bar_y = -330.0
bar_z = 330.0
bar_front = bar_y + bar_size / 2.0          # -300
bar_rear = bar_y - bar_size / 2.0           # -360
bar_top = bar_z + bar_size / 2.0            # 360
bar_bot = bar_z - bar_size / 2.0            # 300
bar_x = (-544.0, 440.0)         # koker; de flenzen zitten erbuiten (-552 .. 448 = 1000 mm, module_pitch)
flange_t = 8.0                  # koppelflens 100 x 100 x 8 met 4 gaten M12: volgende module ertegen bouten
flange_size = 100.0
flange_hole_off = 38.0          # gaten op +-38 van het hart van de balk (buiten de koker)
flange_bolt_d = 12.0

arm_size = 40
arm_wall = 3
cross_y = -200.0                # dwarsbuis (verstijving) tussen de armen, voor de balk
cross_size = 40
cross_wall = 3

# ---------------------------------------------------------------------
# Heffen: 1 elektrische lineaire actuator 12 V, slag 150 (inbouw 265 / uit 415), 3000 N.
# Stangoog in een langgat in de bok (langgatplaten op de bovenplaat, als simple_v2 maar lager), huis met een pen
# op ogen bovenop het midden van de balk. Werk = actuator helemaal uit, heffen = helemaal in.
# ---------------------------------------------------------------------
act_x = -2.5                    # hart actuator: in de opening tussen de beugelbouten van element 5 (x = 62.5)
act_a = (-130.0, 700.0)         # (y, z) onderkant langgat in de bok (hier trekt de stang bij heffen)
act_l = (-330.0, 388.0)         # (y, z) pen huis op de balk, in werkstand
act_retracted = 265.0
act_stroke = 150.0
act_extended = act_retracted + act_stroke    # 415
float_up_deg = 9.0              # hefraam mag zoveel omhoog zweven voordat het stangoog bovenin het langgat komt

# 2 gasveren naast de langgatplaten duwen het stangoog (en via de actuator het hefraam) omlaag: bijna constante
# neerdruk met robotgewicht terwijl het hefraam vrij zweeft. Bij heffen ligt het oog onderin het langgat; de
# gasveren duwen dan tegen de bok zelf en belasten de actuator niet.
gas_force = (750.0, 1000.0)     # N, beide samen: oog onderin / bovenin het langgat (progressie gasveer 1,33)
gas_len_ext = 250.0             # oog-oog uitgeschoven (oog onderin het langgat)
gas_body_d = 19.0
gas_body_len = 120.0
gas_rod_d = 8.0
gas_eye_d = 18.0
gas_eye_w = 8.0
gas_dx = 31.0                   # hart gasveer t.o.v. hart actuator (buiten de langgatplaten)
act_pin_d = 10.0
act_pin_hole = 10.5
act_tube_d = 38.0
act_rod_d = 20.0
act_eye_d = 24.0
act_eye_w = 20.0
act_motor_d = 36.0
act_motor_len = 110.0
act_motor_offset = 40.0
act_lug_t = 8.0
act_lug_gap = 22.0

# ---------------------------------------------------------------------
# Zaai-element (8x per module), lokaal: x = 0 is het hart van de schijf (de sleuf), y en z werktuigcoordinaten.
#   houder: klemplaat 76 x 10 onder de balk met 2 beugelbouten M12, 2 wangen strip 40 x 8 naar het draaipunt,
#           veertoren strip 50 x 8 achter de balk met ankerplaat voor de veerpoot
#   arm: koker 30 x 30 x 3 aan de -x kant (schaduwkant van de schijf), draaibus O 30 op een bout M16
#   schijf: vlakke kouterschijf O 300 x 4 op lagernaaf (als simple_v2), 7 graden scheef t.o.v. de rijrichting
#   dieptering PE op de schijf (+x kant), zaaischoen + zaadbuis 20 x 1,5 in de schaduw van de schijf,
#   aandrukrol O 200 x 40 op een verende arm (torsieveer) achter de schijf
# ---------------------------------------------------------------------
u_pivot = (-330.0, 150.0)       # (y, z) draaipunt sleeparm, recht onder de balk: laag = weinig opdrukken door trek
u_arm_x = (-80.0, -50.0)        # arm 30 x 30 x 3
u_arm_size = 30.0
u_arm_wall = 3.0
u_arm_y_end = -760.0           # arm eindigt voor de aandrukrol; de rolarm scharniert aan het armeinde
u_bush_od = 30.0
u_bush_id = 16.5
u_pin_d = 16.0
u_cheek_t = 6.0
u_cheek_gap = 1.0               # ring tussen arm en wang
u_cheek_y = (-352.0, -308.0)
u_cheek_z_bot = 125.0
u_clamp_x = (-103.0, -27.0)     # klemplaat onder de balk
u_clamp_y = (-378.0, -282.0)
u_clamp_t = 8.0
ubolt_d = 12.0
ubolt_x = (-93.0, -37.0)        # beugelbouten M12 (hart arm +- 28)
ubolt_nut_af = 19
ubolt_nut_m = 10.8
u_tower_x = (-90.0, -40.0)      # veertoren strip 50 x 8 achter de klemplaat
u_tower_y = (-386.0, -378.0)
u_anchor_y = (-460.0, -386.0)   # ankerplaat 50 x 8 naar achteren, gat voor de veerstang
u_anchor_z = (372.0, 380.0)
u_lug_y = -420.0                # pen veerpoot op de arm (90 mm achter het draaipunt)
u_lug_h = 18.0                  # pen zoveel boven de bovenkant van de arm
u_lug_t = 6.0
u_stop_deg = 12.0                # de arm mag zoveel graden onder de werkstand zakken (stelmoer op de ankerplaat)

# veerpoot: stang M12 met oog onderaan, veerschotel, drukveer tot onder de ankerplaat, stelmoer erboven
rod_d = 12.0
spring_od = 41.0                # draad 4, gem. diameter 37, 12 werkzame windingen: ca. 4 N/mm
spring_wire = 4.0
spring_free = 245.0             # vrije lengte; voorspanning stellen met de moer onder de schotel (+- 25 mm)
spring_rate = 4.0               # N/mm: zacht met veel voorspanning (ca. 375 N in werkstand); de voorspanning
                                # bepaalt op welke hoogte het hefraam zweeft, de gasveren bepalen de neerdruk
eye_d = 26.0
eye_w = 16.0
seat_d = 46.0
seat_offset = 40.0              # veerschotel boven de pen

disc_d = 300.0
disc_t = 3.0                    # dun en scherp: minder neerdruk nodig, 1,6 kg
disc_angle = 7.0                # graden t.o.v. de rijrichting: voorkant naar -x, de +x zijde duwt de grond opzij
disc_center = (u_pivot[0] - 210.0, disc_d / 2.0 - disc_depth)    # (y, z) = (-540, 135)
disc_bolt_r = 30.0              # 4 bouten M8 op steekcirkel O 60
disc_center_hole = 25.0
hub_d = 62.0                    # lagernaaf (2 lagers 6203-2RS), flens O 100
hub_len = 32.0
hub_flange_d = 100.0
hub_flange_t = 5.0
stub_d = 20.0                   # asbout M20 door de arm
boss_d = 32.0                   # schuin afgezaagde afstandsbus tussen naaf en arm (zet de schijf op 7 graden)

# zaaischoen (gehard, gelast aan de zaadbuis), lokaal in het vlak van de schijf: x_l < 0 = schaduwkant
boot_t = 12.0
boot_gap = 0.5                  # tussen schoen en schijf
boot_y = (-12.0, -62.0)         # t.o.v. hart schijf: voorkant / achterkant onderaan
boot_top_z = 40.0
tube_od = 20.0                  # zaadbuis RVS 20 x 1,5
tube_id = 17.0
tube_bot = (-58.0, 30.0)        # (y t.o.v. hart schijf, z) onderkant buis in de schoen
tube_top = (-78.0, 180.0)       # bovenkant: zaadslang 20/26 erover
tube_x = (-13.0, -32.0)         # x_l onder / boven: de buis loopt van de schijf af
holder_z = (115.0, 125.0)       # strip van de zaadbuis naar de binnenkant van de arm
holder_dy = 15.0

# dieptering: PE-HD ring op de +x kant van de schijf (4 bouten M8 door de schijf), rolt naast de snede op het
# maaiveld. Diepte wisselen = ring wisselen: O 290 -> 5 mm, 280 -> 10, 270 -> 15, 260 -> 20, 250 -> 25 mm
band_d = disc_d - 2.0 * disc_depth   # 270
band_id = 200.0
band_w = 15.0
band_sizes = (290.0, 280.0, 270.0, 260.0, 250.0)

# aandrukrol: massief rubber O 200 x 40 op een rolarm (strip 36 x 8) die met een bout M12 aan het eind van de
# sleeparm scharniert; een torsieveer om de bout drukt de rol op de sleuf (ca. 45 N), los van de diepte
pw_d = 200.0
pw_w = 40.0
pw_hub_d = 50.0
pw_x = 0.0                      # hart rol op de sleuf
pw_axle = (-835.0, 100.0)       # (y, z) in werkstand: rol op het maaiveld
pw_axle_d = 16.0
pw_link_y = -745.0              # scharnier rolarm (in de sleeparm)
pw_link_x = (-42.0, -34.0)      # rolarm aan de binnenkant, tussen torsieveer en rol
pw_link_w = 36.0
pw_link_bolt_d = 12.0
pw_link_range = (-40.0, 30.0)   # graden: rolarm mag zoveel zakken / omhoog (aanslagen)
tspring_x = (-50.0, -42.0)      # torsieveer om de scharnierbout
tspring_od = 28.0
tspring_wire = 3.5
pw_force = 35.0                 # N op de rol in werkstand (voorspanning torsieveer, aangenomen; 0,9 N/mm rolbreedte)
pw_rate = 0.6                   # N per graad rolarmhoek (aangenomen)

# ---------------------------------------------------------------------
# Zaadbak en dosering (op het hefraam): 2 vakken, 2 nokkenrollen in een gezamenlijk doseerhuis, 8 uitlopen,
# 2 wormwielmotoren 12 V met encoder (toerental volgt de rijsnelheid van de robot)
# ---------------------------------------------------------------------
hop_x = (-460.0, 460.0)
hop_wall = 2.0                  # aluminium 2 mm (licht: de robot moet alles achter zijn achteras tillen)
hop_top_z = 770.0
hop_y = (-620.0, -360.0)        # voor- en achterwand (achter de balk: bij heffen vrij van de bok)
hop_side_z = 600.0              # tot hier rechte wanden, daaronder trechter naar het doseerhuis
hop_divider_y = -575.0          # schot bovenaan (onderaan tussen de rollen): voor = gras, achter = fijn zaad
lid_t = 3.0

meter_y = (-545.0, -445.0)      # doseerhuis (aluminium) onder de trechters
meter_z = (425.0, 485.0)
meter_x = (-465.0, 465.0)
shaft_main_y = -480.0           # nokkenrol gras O 40, schroefvormige groeven
shaft_fine_y = -515.0           # nokkenrol fijn zaad O 30
shaft_z = 455.0
shaft_d = 12.0
roll_main_d = 40.0
roll_fine_d = 30.0
roll_w = 25.0                   # actieve breedte per uitloop
spout_d = 26.0
spout_len = 20.0
spout_y = -497.0                # uitloop per rij (onder beide rollen), zaadslang 20/26 naar de zaadbuis
seed_hose_od = 26.0
motor_box = (32.0, 45.0, 60.0)  # wormwielkast x, y, z aan het eind van de as
motor_d = 37.0                  # motor staand op de kast
motor_len = 70.0

post_x_rows = (0, 3, 6)         # steunplaten van de zaadbak op de balk, naast deze rijen (+24 mm)
post_dx = 18.0
post_t = 6.0

# doseerrollen (ontwerpwaarden, IJKEN met een afdraaiproef)
roll_main_cc = 2.0              # cm3 per omwenteling per uitloop
roll_fine_cc = 0.15
motor_rpm_max = 60.0            # wormwielmotor 12 V, 70 tpm onbelast; geregeld op encoder
