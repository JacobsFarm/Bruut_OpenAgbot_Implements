import math

# =====================================================================
# Dockweed drill v8 (ridderzuringfrees) - parameters
# Portaal achter op de Bruut OpenAgbot: X-as (links-rechts, slag 1000) + Z-as (op-neer), de robot is de Y-as.
# v8 = Z-deel van v7 + X-as van v6, maar met ronde buizen in plaats van aftakasbuizen:
# - X-as: 2 ronde precisiebuizen O50 x 4 (dezelfde als de Z-as) tussen 2 zijplaten 12 mm (prop met 2x M10 per eind),
#   2 dwarsbalken 40 x 40 x 3 over de volle breedte (1x M12 per staander), riem HTD5M met stepper + 5:1 op de slede,
#   kabelrups; de slede loopt op 3 lagerhuizen met iglidur-bus (zelfde type als de Z-as): 2 op de bovenbuis, 1 op
#   de onderbuis (sleufgaten in z, geen dubbele geleiding).
# - De Z-montageplaat van v7 is nu de X-slede (alu 12 mm): voor de X-lagerhuizen, achter de 4 Z-lagerhuizen en de
#   bovenste beugel van de LA36. Z-as, spilbok, spil, motor en bus zoals v7.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong = midden van de robot. Het werktuig hangt achter de achterste onderbalk (rear_outer).
# Hulpmaat v = afstand achter de achterkant van die balk: robot-y = robot_beam_rear_face - v.
# De onderdelen worden in (x, v, z) getekend en daarna gespiegeld naar robotcoordinaten (dwd8_parts.to_robot).
# Alle maten staan hier; nooit hardcoden in dwd8_parts.py / build_dwd8.py.
# =====================================================================

VARIANT = "v8"

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
# Stand van de machine (build): X van het spilhart (zie X-as) en hoogte onderkant gereedschap
# ---------------------------------------------------------------------
depth_std = 150.0                   # standaard freesdiepte (Ruud: 15 cm)
depth_max = 200.0
drive_z = 200.0                     # onderkant frees boven maaiveld tijdens rijden (actuator ingetrokken)
z_ref = drive_z                     # referentiestand van de Z-slede in de build (rijstand)
work_z = -depth_std

# ---------------------------------------------------------------------
# Aanbouwbok (headstock): 2 staanders 40 x 40 x 3 achter de onderbalk, op het gatenraster (zoals v6)
# Vrije gaten in rear_outer: x = +-225 en +-275 (+-325/+-425 = frame_bolts, +-375 boven het houten blok).
# ---------------------------------------------------------------------
hs_x = 250.0                        # hart staander
hs_bolt_dx = 25.0                   # M10 op x = hs_x +- 25 (gaten 225 en 275)
hs_bolt_v = -robot_beam / 2.0       # hart onderbalk
hs_plate_half_x = 50.0
hs_plate_t = 8.0                    # bovenplaat, klemplaat, achterplaat
up_size = 40.0                      # staander 40 x 40 x 3
up_wall = 3.0
up_v0 = hs_plate_t                  # voorkant staander (tegen de achterplaat)
up_v1 = up_v0 + up_size
up_z0 = robot_lower_beam_z[0] - hs_plate_t        # 611: onderkant klemplaat
up_z1 = 1110.0
up_cap_t = 6.0
gusset_t = 6.0
gusset_h = 75.0                     # schoor boven de bovenplaat, tegen de staander (onder de M12 van de dwarsbalk)
cross_size = 40.0                   # dwarskoker tussen de staanders (draagt de E-kast)
cross_wall = 3.0
cross_z = (up_z0 + 4.0, up_z0 + 4.0 + cross_size)
m10_d = 10.0
m10_head_r = 9.2                    # AF17 over de hoeken / 2 (rond getekend)
m10_head_k = 6.4
m10_nut_m = 8.4
m12_d = 12.0
m12_head_r = 11.0                   # AF19 (rond getekend)
m12_head_k = 7.5

# ---------------------------------------------------------------------
# Stand van de X-as
# ---------------------------------------------------------------------
x_stroke = 1000.0                   # zoals v6
x_min, x_max = -x_stroke / 2.0, x_stroke / 2.0
work_x = 150.0                      # stand voor de standaardafbeeldingen

# ---------------------------------------------------------------------
# X-as (v8): 2 ronde precisiebuizen O50 x 4 (zelfde buis als de Z-as) tussen 2 zijplaten 12 mm.
# Per buiseind een ingelaste prop (O42, 25 lang) met 2x M10 getapt; bouten van buiten door de zijplaat: buis los =
# 4 bouten eruit (zoals v6). De zijplaten zijn gelast aan 2 dwarsbalken 40 x 40 x 3 over de volle breedte (een per
# buishoogte, voor de buizen langs), die met 1x M12 per kruising tegen de achterkant van de staanders zitten.
# De slede loopt op 3 lagerhuizen met iglidur-bus (zelfde type als de Z-as, as langs x): 2 op de bovenbuis, 1 in het
# midden op de onderbuis (sleufgaten in z: 3 punten, geen dubbele geleiding). Het huis zit met zijn montagevlak tegen
# de voorkant van de slede; M8 van voren door het huis in de slede (Helicoil in het alu).
# ---------------------------------------------------------------------
beam_z = (760.0, 1060.0)            # hart onderste / bovenste buis en dwarsbalk (= hoogte van de Z-lagerhuizen)
xbar_z = beam_z
xbeam = (40.0, 3.0)                 # dwarsbalk 40 x 40 x 3, direct achter de staanders
xbeam_v = (up_v1, up_v1 + xbeam[0])
xg_d = 50.0                         # X-buis: precisiebuis O50 x 4 E355 (zoals de Z-buis)
xg_t = 4.0
xg_house = (100.0, 70.0, 32.0)      # X-lagerhuis: breedte (z), lengte (x), uitsteek voor het buishart (zoals Z)
xg_hc = 42.0                        # buishart tot montagevlak (asafstand van het huis, geschat)
xg_house_bolt = (22.0, 40.0)        # 4x M8 op hart +- 22 (x) en +- 40 (z)
xg_house_gap = 8.0                  # vrije ruimte tussen dwarsbalk en de voorkant van het X-huis
tube_v = xbeam_v[1] + xg_house_gap + xg_house[2]     # hart X-buizen (128)
xg_upper_pitch = 240.0              # 2 huizen op de bovenbuis op x = +-120 (v6: hulzen op +-110)
xbar_L = 1470.0                     # buitenmaat zijplaten (v6: 1400; breder voor de slede van 410 met de X-motor op x 152)
end_plate_t = 12.0                  # zijplaat staal
plug_L = 25.0                       # prop in het buiseind (gelast), 2x M10 getapt
tube_bolt_dz = 10.0                 # M10 op z = buishart +- 10
side_plate_v = (xbeam_v[0], tube_v + 35.0)
side_plate_z = (xbar_z[0] - 40.0, xbar_z[1] + 40.0)

# X-slede (was de Z-montageplaat van v7): alu 12 mm, voor de X-huizen, achter de Z-huizen, X-motor en actuatorbeugel
slide_v0 = tube_v + xg_hc           # voorkant slede = montagevlak van de X-huizen (170)
slide_t = 12.0
slide_half_x = 205.0                # X-huizen tot x 155, X-motor tot 182, beugel spiraalkabel tot 201
slide_z = (700.0, 1120.0)
slide_tab = (-30.0, 30.0, 1450.0)   # verlengstuk midden boven aan de slede (x0, x1, z1): bovenste pen actuator

# Riemaandrijving (zoals v6): HTD5M 15 mm met de uiteinden geklemd op de zijplaten, omega om de poelie en 2
# spanrollen op de slede; NEMA 23 closed-loop + 5:1 achter op de slede, rechts naast de rechter Z-buis.
belt_z = 880.0
belt_w = 15.0
pulley_z = 923.0
motor_dx = 152.0                    # hart X-motor: vrij van de rechter Z-buis (x 65..115) en tussen de Z-huizen in z
chain_z = xbar_z[1] + 60.0          # kabelrups boven de bovenste X-huizen

# ---------------------------------------------------------------------
# Z-as (v7): 2 ronde precisiebuizen (E355, koudgetrokken naadloos, EN 10305-1) O50 x 4 links en rechts, die met
# de Z-slede mee naar beneden glijden door 2 x 2 lagerhuizen met een kunststof glijbus (iglidur / POM), vast op de
# X-slede. In het midden de spil (achter) en de Linak LA36 (voor, tussen de buizen). Onderaan staan de buizen
# op het onderjuk en 60 mm hoger gaan ze door de klemplaat; beide gelast (met de lagerhuizen als mal).
# ---------------------------------------------------------------------
zg_d = 50.0                         # buitendiameter buis
zg_t = 4.0                          # wand
zg_dx = 90.0                        # hart buis op x = +-90 (v6: +-64; zonder X-kast is er ruimte, breder = stijver tegen kantelen)
zg_hc = 42.0                        # hart buis achter de slede (asafstand van het lagerhuis, geschat)
zg_v = slide_v0 + slide_t + zg_hc   # hart buizen in v
zg_bottom = 420.0                   # onderkant buizen boven onderkant gereedschap (staat op het onderjuk)
zg_top = 1340.0                     # bovenkant buizen; tussen z+502 en z+1318 moet de buis kaal zijn (slag door de huizen)
zg_house_z = beam_z                 # hart van de 2 lagerhuizen per buis (op de hoogte van de dwarsbalken)
zg_house = (100.0, 70.0, 32.0)      # lagerhuis: breedte x, lengte z, uitsteek achter het buishart (geschat, type
                                    # drylin RJUM-06 / SC50 met kunststof bus: CONTROLEER aan het gekochte huis)
zg_house_bolt = (40.0, 22.0)        # 4x M8 op hart +- 40 (x) en +- 22 (z), van achter door het huis in de plaat (getapt)
zg_bush_d = 60.0                    # buitenmaat glijbus (geschat)
zg_wiper_t = 8.0                    # schraapring boven en onder elk huis
zg_yoke_t = 10.0                    # onderjuk en klemplaat, gelast aan de achterplaat van de spilbok
zg_clamp_z = 480.0
zg_yoke_half_x = zg_dx + 34.0

# Actuator: Linak LA36 (parts/actuator/linear-actuator-la36-data-sheet-eng.pdf), 24 V, 1700 N, spindel 20 mm,
# tandwiel F 1:18, slag 400, achterbevestiging en stangoog massief O12,2. Pen-op-pen recht in het midden tussen de
# buizen (x 0), huis boven, naar achteren (+v) boven de spilmotor. Ingetrokken = rijstand. (Zoals v6.)
act_stroke = depth_max + drive_z    # 400
act_Lr = 250.0 + act_stroke         # inbouwmaat ingetrokken (datasheet: slag > 300 -> 250 + slag) = 650
act_x = 0.0
act_v = slide_v0 + slide_t + 53.5   # hart actuator in v (zelfde afstand tot de slede als v6 en v7)
act_pin_z = 1420.0                  # bovenste pen (vast): huis 10 mm boven de spilmotor in rijstand
act_tube = (44.5, 50.0)             # buitenprofiel alu (x, v); 44,5 uit de datasheet, 50 geschat
act_rod_d = 28.0                    # binnenbuis (geschat; stangoog O27,8)
act_tube_end = 45.0                 # einde buitenbuis boven het hart van het stangoog, ingetrokken (geschat)
act_house_w = 76.0                  # huis: breedte 76, hoogte 148 waarvan 36 onder het hart, lengte 230 (datasheet)
act_house_h = (36.0, 112.0)         # huis voor (-v) / achter (+v) van het hart van de spindel
act_house_L = 230.0
act_house_dz = 25.0                 # hart achterste pen tot achterkant huis
act_eye_dz = act_pin_z - act_Lr - drive_z    # 570: hart stangoog boven de onderkant van het gereedschap
act_pin_d = 12.2
act_eye_c = 27.8
act_back_c = 25.2
act_force = 1700.0                  # max. last [N]; zelfremming 2200 N
act_selflock = 2200.0
act_speed = (72.0, 52.0)            # snelheid onbelast / bij 1700 N [mm/s] (datasheet)
act_amp = (2.4, 10.3)               # stroom onbelast / bij 1700 N [A] (datasheet)
act_duty = 0.20                     # inschakelduur bij volle last, slag <= 600 (datasheet: 4 min aan, 16 uit)
act_V = 24.0
act_kg = (5.3, 0.7)                 # 6,0 kg totaal; vast / stang
dcdc = (48.0, 24.0, 20.0)           # omvormer 48 -> 24 V, 20 A

# ---------------------------------------------------------------------
# Spilbok, spil, motor (zoals v6)
# ---------------------------------------------------------------------
sb_back_t = 6.0
sb_back_v0 = slide_v0 + slide_t + 96.0   # voorkant achterplaat spilbok (zelfde afstand tot de slede als v6 en v7)
spindle_dv = 75.0                   # hart spil achter de achterplaat
sb_lo = 408.0                       # onderste plaat boven onderkant gereedschap
sb_side_x = 87.5                    # hart zijplaten (5 mm), net buiten de lagervoeten
sb_back_top = 710.0                 # bovenkant achterplaat spilbok

# 2x UCP 206 staand lagerblok (as 30). Catalogusmaten: CONTROLEER aan het gekochte lagerblok.
ucp_d = 30.0
ucp_bolt = 121.0
ucp_L = 165.0
ucp_b = 48.0
ucp_slot = (17.0, 20.0)
ucp_H = 82.0
ucp_h = 42.9
ucp_foot_t = 17.0                   # geschat
ucp_ring_d = 80.0                   # geschat
ucp_ring_w = 38.1
ucp_kg = 1.4
ucp_C = 19500.0                     # dynamisch draaggetal [N] (UC206, catalogus)
bearing_plate_t = 10.0
bearing_lo = sb_lo + 8.0 + ucp_b / 2 + 7.0
bearing_dist = 140.0
bearing_hi = bearing_lo + bearing_dist
sb_mo = bearing_hi + ucp_b / 2 + 4.0
shaft_d = ucp_d                     # spilas O30 C45 massief, onderin in de spilflens gelast

# Flexibele klauwkoppeling maat 28: naaf O19 (motor, spie 6) en O30 (spil, spie 8).
jaw_d = 65.0
jaw_L = 90.0
jaw_star = 20.0
jaw_T = (95.0, 190.0)               # nominaal / max. koppel [Nm] (catalogus, controleer)
jaw_hub_L = 35.0
jaw_z0 = sb_mo + 8.0 + 7.0
jaw_kg = 0.95
shaft_top = jaw_z0 + jaw_hub_L

# Spilmotor: 800 W tandwielmotor met voet (op voorraad, parts/800 watt motor; 48 V geborsteld, 500 rpm volgens de
# advertentie: CONTROLEER het typeplaatje). Staat recht boven de spil, as omlaag in de klauwkoppeling.
motor_P = 800.0
motor_rpm = 500.0
motor_V = 48.0
motor_peak = 2.0
motor_shaft_d = 19.0
motor_shaft_out = 35.0
motor_total_len = 260.0
motor_nose = (35.0, 65.0, 45.0, 80.0)
motor_ring = (65.0, 110.0, 120.0)
motor_body = (110.0, 255.0, 105.0)
motor_cap = (255.0, 260.0, 95.0)
motor_foot = (119.0, 234.0)
motor_foot_holes = (139.0, 219.0)
motor_foot_w = 90.0                      # AANNAME
motor_foot_hole_dx = 70.0                # AANNAME
motor_foot_t = 6.0
motor_foot_h = 64.0
motor_kg = 9.0                           # geschat
motor_shaft_end = jaw_z0 + jaw_L - jaw_hub_L
motor_plate_t = 10.0
motor_plate_v = (-62.0, 72.0)
gusset_mp_t = 6.0

cutter_rpm = motor_rpm
idle_w = 45.0                       # verlies spil + lagers + koppeling bij 500 rpm (geschat)

# ---------------------------------------------------------------------
# Bus (zoals v5 / v6 / Robot Ruud): stalen pijp DN200 met deksel, rust met eigen gewicht op de zode
# ---------------------------------------------------------------------
pot_d = 219.1
pot_h = 180.0
pot_t = 3.6
pot_lid_t = 5.0
pot_rim = 30.0
pot_rod_dx = 100.0
pot_rod_d = 16.0

# ---------------------------------------------------------------------
# Gereedschap (alleen de frees: 500 rpm is te langzaam voor de maaischijf)
# ---------------------------------------------------------------------
cutter_d = 180.0
cutter_teeth = 4

# ---------------------------------------------------------------------
# Aandrijving en proces
# ---------------------------------------------------------------------
stepper_T = 3.0                     # NEMA 23 closed-loop [Nm] (zoals v6)
x_gear = 5.0
x_pulley_T = 20
htd_pitch = 5.0
rapid_x = 200.0                     # mm/s
xg_mu = 0.15                        # wrijving iglidur op de buis (droog tot licht gesmeerd, zoals Z)
plunge_v = 25.0                     # insteeksnelheid [mm/s]
rapid_z = act_speed[0] - (act_speed[0] - act_speed[1]) * 800.0 / act_force   # LA36 bij ca. 800 N (optillen)
dwell_s = 1.0
z_force_limit = 600.0               # software-begrenzing [N]
cut_energy = (0.5e6, 2.0e6)
cut_energy_std = 1.0e6
thrust_n = (150.0, 1.0)
side_force = 300.0
drive_speed = 500.0                 # mm/s
stop_start_s = 4.0
plant_period_s = 60.0               # typische tijd tussen twee planten in het veld (opgave gebruiker: soms een minuut)
position_tol = 40.0                 # toelaatbare fout spil-plant [mm] (bus O219 rond een frees O180)

# ---------------------------------------------------------------------
# Camera, licht, elektra
# ---------------------------------------------------------------------
cam_x = 0.0                         # vaste camera hoog boven de spillijn
cam_mast_x = 250.0                  # mast 40 x 40 op de rechter staander
cam_z = 1900.0
cam_v = 740.0                       # camera achter de spillijn (rijrichting -y: ziet de plant eerst)
ebox = (300.0, 250.0, 120.0)
ebox_z0 = 745.0
ebox_plate_t = 3.0
spiral_turns = 12
spiral_x = 175.0                    # spiraalkabel rechts naast de rechter Z-buis en het lagerhuis, boven de X-motor
spiral_z0 = 965.0                   # onderste anker op de X-slede, boven de X-motor (bovenkant 953)
