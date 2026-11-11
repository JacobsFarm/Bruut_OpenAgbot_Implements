import math

# =====================================================================
# Dockweed drill v9 (ridderzuringfrees) - parameters
# Portaal achter op de Bruut OpenAgbot: X-as (links-rechts, slag 1000) + Z-as (op-neer), de robot is de Y-as.
# v9 = proces, spilbok, spil, motor, bus en Linak LA36 van v8, maar beide geleidingen op skeelerwielen in U-profielen:
# - 1 type wielblok (L-beugel staal 10 mm) met 4 skeelerwielen O80 x 24 (78A, 2x 608ZZ): 2 flenswielen (as in de
#   diepte van het profiel, rollen tegen de voorste resp. achterste flens: samen spelingvrij) en 2 lijfwielen op een
#   gezamenlijke as (rollen op het lijf van het profiel). Het blok schroeft met 4x M8 in sleufgaten op de slede.
# - X-as: 2 UPE 100 met de openingen naar elkaar toe (boven open naar beneden, onder open naar boven), aan de uiteinden
#   gelast aan 2 eindplaten (= 1 X-frame), met verzonken M8 door de voorflens direct op de 2 staanders. 4 wielblokken
#   op de voorkant van de X-slede. Riem HTD5M rond 2 poelies aan de uiteinden, NEMA 23 + 5:1 VAST aan de rechter
#   eindplaat (zoals de schets: motor aan het eind), de riem geklemd op de slede.
# - Z-as: 2 UPE 100 staand, openingen naar elkaar toe (naar x 0), gelast op het onderjuk van de spilbok: ze bewegen
#   mee met de spil (zoals de buizen van v7/v8). 4 wielblokken achter op de X-slede. LA36 in het midden.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong = midden van de robot. Het werktuig hangt achter de achterste onderbalk (rear_outer).
# Hulpmaat v = afstand achter de achterkant van die balk: robot-y = robot_beam_rear_face - v.
# De onderdelen worden in (x, v, z) getekend en daarna gespiegeld naar robotcoordinaten (dwd9_parts.to_robot).
# Alle maten staan hier; nooit hardcoden in dwd9_parts.py / build_dwd9.py.
# =====================================================================

VARIANT = "v9"

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
up_z1 = 1130.0                      # tot boven het bovenste X-profiel (1124,5)
up_cap_t = 6.0
gusset_t = 6.0
gusset_h = 75.0                     # schoor boven de bovenplaat, tegen de staander
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
x_stroke = 1000.0                   # zoals v6 / v8
x_min, x_max = -x_stroke / 2.0, x_stroke / 2.0
work_x = 150.0                      # stand voor de standaardafbeeldingen

# ---------------------------------------------------------------------
# Skeelerwiel O80 x 24 met 2x 608ZZ. Eerst 78A (Zandstra, nietzoduur.nl); op verzoek van de gebruiker 90A (harder,
# zelfde maat: zie RATIONALE). Set van 8 incl. 16 lagers.
# ---------------------------------------------------------------------
wheel_d = 80.0
wheel_w = 24.0
wheel_hub_d = 52.0                  # kern / naaf (kunststof) onder het PU-loopvlak (geschat)
wheel_edge_r = 9.0                  # afronding van het loopvlak (getekend)
wheel_bore = 8.0                    # 608: as O8 (M8-bout als as)
wheel_kg = 0.11                     # wiel + 2 lagers (geschat)
wheel_shore = 90.0                  # 90A (was 78A)
wheel_load_ok = 600.0               # toelaatbare duurlast per wiel [N] voor 90A op staal (GESCHAT, niet gemeten)
wheel_load_peak = 1500.0            # korte piek [N] (GESCHAT)
wheel_tread_t = 14.0                # dikte PU-loopvlak (geschat)
wheel_tread_w = 15.0                # effectieve contactbreedte van het bolle loopvlak (geschat)
wheel_crr = 0.015                   # rolweerstandscoefficient hard PU op staal (geschat)
bearing_608_C0 = 1370.0             # statisch draaggetal 608 [N] (catalogus)
bearing_608_C = 3300.0              # dynamisch draaggetal 608 [N] (catalogus)

# ---------------------------------------------------------------------
# U-profiel UPE 100 (EN 10365, evenwijdige flenzen: het wiel loopt op een vlakke flens, niet op een schuine UNP-flens)
# Lokaal assenstelsel van een profiel: u = langs het profiel, s = dwars over de opening (s 0 = midden tussen de
# flenzen, +s = naar de slede), d = vanaf de binnenkant van het lijf naar de opening.
# ---------------------------------------------------------------------
ch_h = 100.0                        # hoogte (over de flenzen, in s)
ch_b = 55.0                         # flensbreedte (in d, incl. lijf)
ch_tw = 4.5                         # lijf
ch_tf = 7.5                         # flens
ch_kg_m = 9.82
ch_gap = ch_h - 2 * ch_tf           # 85: vrije maat tussen de flenzen (wiel 80: 2,5 mm per kant, met sleufgaten bijstellen)
ch_depth = ch_b - ch_tw             # 50,5: lijf (binnen) tot flenspunt
ch_Iy = 207.0e4                     # mm4, buiging in het vlak van het lijf (sterke as)
ch_Iz = 38.3e4                      # mm4, zwakke as
ch_A = 1250.0                       # mm2

# Wielblok (zelfde blok op X en Z, 8 stuks): L-beugel staal 10 mm, in lokale (u, s, d) van het profiel
blk_t = 10.0                        # bodemplaat (boven de flenspunten) en montageflens
blk_gap = 3.0                       # bodemplaat boven de flenspunten
blk_d0 = ch_depth + blk_gap         # 53,5: onderkant bodemplaat
blk_half_u = 130.0                  # blok 260 lang
blk_s0 = -44.0                      # voorkant bodemplaat (aan de kant van de verste flens)
blk_flange_s = ch_h / 2 + 5.0       # 55: voorkant montageflens (5 mm vrij van het profiel)
blk_flange_d1 = blk_d0 + 70.0       # 123,5: einde montageflens
blk_bolt = ((-100.0, 85.0), (100.0, 85.0), (-100.0, 110.0), (100.0, 110.0))   # (u, d) M8 in sleuf +-5 langs d
fw_u = 84.0                         # flenswielen op u = +-84
fw_d = 26.0                         # hart flenswiel (loopvlak d 14..38, vrij van de hoekafronding r 10 en de flenspunt)
fw_gap = 0.3                        # getekende speling tot de flens (in werkelijkheid licht voorgespannen)
fw_s = ch_gap / 2 - wheel_d / 2 - fw_gap    # 2,2: as uit het midden, + tegen de +s-flens, - tegen de -s-flens
fw_slot = 4.0                       # sleufgat as in s: +-4 (flenstolerantie UPE h +-2)
ww_d = wheel_d / 2 + fw_gap         # hart lijfwielen (40,3 van het lijf)
ww_s = 15.0                         # 2 lijfwielen op s = +-15 op 1 as (tussenbus 6)
ear_s = (28.5, 33.5)                # 2 oren 5 mm onder de bodemplaat, as M8 langs s
ear_half_u = 22.0
win_half_u = 43.0                   # venster in de bodemplaat voor de lijfwielen
win_half_s = 28.0

# ---------------------------------------------------------------------
# X-as (v9): X-frame = 2 UPE 100 met de openingen naar elkaar toe + 2 eindplaten 10 mm (gelast). Het voorste flensvlak
# ligt tegen de achterkant van de staanders: 2x M8 verzonken (DIN 7991) per kruising, kop vlak in de flens, moer voor
# op de staander. Geen dwarsbalken meer: het profiel is zelf de balk (zwakke as 38 cm4 tegen 9 cm4 voor 40x40x3).
# ---------------------------------------------------------------------
xch_v = up_v1 + ch_h / 2            # 98: midden X-profielen in v (voorflens v 48..55,5 tegen de staander)
xch_web_z = (710.0, 1120.0)         # binnenkant lijf onder (open naar boven) / boven (open naar beneden)
xch_bolt_d = 42.0                   # verzonken M8 in de flens, 42 van het lijf (wielspoor d 14..38)
xch_bolt_dx = 10.0                  # 2 bouten per staander op x = hs_x +- 10
xch_drain_s = 34.0                  # afwateringsgaten O10 in het lijf van het onderste profiel, buiten het wielspoor (|s| 3..27)
xch_drain_pitch = 150.0
xbar_L = 1570.0                     # buitenmaat eindplaten: slede 540 breed + slag 1000 + 2x 5 + 2x 10
end_plate_t = 10.0
end_plate_v = (48.0, 185.0)          # eindplaat tot achter de slede (eindschakelaar en aanslag op slede-hoogte)
end_plate_z0 = 640.0
limit_vz = (169.0, 660.0)            # eindschakelaar X-min (links) en rubberen aanslag (rechts) op de slede
xblk_x = 132.0                      # 2 wielblokken per X-profiel op x = +-132 op de slede

# X-slede: alu 12 mm, voor 4 X-wielblokken + riemklem, achter 4 Z-wielblokken + LA36-beugel + spiraalkabel
slide_v0 = xch_v + blk_flange_s + blk_t      # 163: voorkant slede = achterkant montageflenzen X-blokken
slide_t = 12.0
slide_half_x = 270.0
slide_z = (620.0, 1200.0)
slide_tab = (-30.0, 30.0, 1450.0)   # verlengstuk midden boven aan de slede (x0, x1, z1): bovenste pen actuator

# Riemaandrijving (zoals de schets): HTD5M 15 mm rond 2 poelies 20T aan de uiteinden (as langs v), NEMA 23 closed-loop
# + 5:1 vast op een beugel aan de rechter eindplaat, spanpoelie links in een sleuf; onderste part geklemd op de slede.
belt_z = 915.0                      # hart poelies (tussen de montageflenzen van de X-blokken: z 833..997 vrij)
belt_w = 15.0
belt_v = (110.0, 125.0)
pulley_x = 740.0
pulley_r = 15.0                     # 20T HTD5M: steekdiameter 31,8
belt_r = (15.2, 18.6)               # riem binnen / buiten (getekend)
drive_bracket_v = (95.0, 105.0)     # beugelplaat poelie / motor (aan de eindplaat gelast)
belt_len = 2 * 2 * pulley_x + math.pi * 31.8        # riemlengte (open lengte, met klem), ca. 3060
chain_z = xch_web_z[1] + ch_tw + 6.0    # kabelrups boven op het bovenste X-profiel (steunplaat 6 mm links)

# ---------------------------------------------------------------------
# Z-as (v9): 2 UPE 100 staand op x = +-zch_x (binnenkant lijf), openingen naar x 0, onderaan gelast op het onderjuk
# (met schoren buiten de profielen); de 4 Z-wielblokken zitten achter op de X-slede op 2 hoogten.
# ---------------------------------------------------------------------
zch_x = 175.0                       # binnenkant lijf: lijfwielen op |x| >= 95 (achterplaat spilbok +-80, LA36 +-38 ertussen)
zch_v = slide_v0 + slide_t + blk_t + 5.0 + ch_h / 2               # 240: midden Z-profielen in v
zblk_z = (760.0, 1060.0)            # hart van de Z-wielblokken (300 uit elkaar)
zg_bottom = 420.0                   # onderkant profielen boven onderkant gereedschap (staat op het onderjuk)
zg_top = 1400.0                     # bovenkant profielen (bij de diepste stand nog boven het bovenste blok)
zg_yoke_t = 12.0                    # onderjuk
zg_yoke_half_x = 215.0
zg_gusset = (6.0, 80.0)             # schoren 6 mm buiten de profielen (dikte, hoogte)

# Actuator: Linak LA36 (parts/actuator/linear-actuator-la36-data-sheet-eng.pdf), 24 V, 1700 N, spindel 20 mm,
# tandwiel F 1:18, slag 400, achterbevestiging en stangoog massief O12,2. Pen-op-pen recht in het midden tussen de
# buizen (x 0), huis boven, naar achteren (+v) boven de spilmotor. Ingetrokken = rijstand. (Zoals v6.)
act_stroke = depth_max + drive_z    # 400
act_Lr = 250.0 + act_stroke         # inbouwmaat ingetrokken (datasheet: slag > 300 -> 250 + slag) = 650
act_x = 0.0
act_v = slide_v0 + slide_t + 53.5   # hart actuator in v (zelfde afstand tot de slede als v6..v8)
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
x_crr = wheel_crr                    # rolweerstand X-wielen (PU 90A, geschat)
plunge_v = 25.0                     # insteeksnelheid [mm/s]
rapid_z = act_speed[0] - (act_speed[0] - act_speed[1]) * 800.0 / act_force   # LA36 bij ca. 800 N (optillen)
dwell_s = 1.0
z_force_limit = 600.0               # software-begrenzing [N]
cut_energy = (0.5e6, 2.0e6)
cut_energy_std = 1.0e6
thrust_n = (150.0, 1.0)
side_force = 300.0                  # zijkracht op de frees, ontwerpwaarde (piek)
side_force_normal = 100.0           # zijkracht in normaal bedrijf (geschat)
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
spiral_x = 232.0                    # spiraalkabel rechts naast het rechter Z-profiel (buitenkant x 179,5)
spiral_z0 = 965.0                   # onderste anker op de X-slede (achterkant)
