import math

# =====================================================================
# Dockweed drill v9 simple (ridderzuringfrees) - parameters
# Portaal achter op de Bruut OpenAgbot: X-as (links-rechts, slag 1000) + Z-as (op-neer), de robot is de Y-as.
# v9 simple = v9 advanced met een eenvoudige geleiding, alles in staal 4 mm (opgave gebruiker):
# - loopprofiel = gezet U 4 mm, binnen 25 breed: het skeelerwiel (80 x 24, 90A) rolt op het lijf, de flenzen houden
#   het opzij. 2 wielen per profiel, alle wielassen langs v.
# - X-as: 2 balken 50 x 30 x 4 met het profiel erop (onder open naar boven, boven open naar beneden) op de staanders,
#   X-slede 4 mm met 4 wielen. Motor vast aan de rechter eindplaat.
# - Z-as: 2 profielen VAST op de X-slede (zelfde plaat als de LA36), boorplaat 4 mm met 2 + 2 wielen rolt erin omlaag.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Hulpmaat v = afstand achter de achterkant van de achterste onderbalk: robot-y = robot_beam_rear_face - v.
# Alle maten staan hier; nooit hardcoden in dwd9s_parts.py / build_dwd9s.py.
# =====================================================================

VARIANT = "v9_simple"

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
up_z1 = 1180.0                      # tot boven de bovenste X-balk (1174)
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
# Skeelerwiel O80 x 24, 90A, 2x 608ZZ (zelfde wiel als v9 advanced)
# ---------------------------------------------------------------------
wheel_d = 80.0
wheel_w = 24.0
wheel_hub_d = 52.0                  # kern / naaf (kunststof) onder het PU-loopvlak (geschat)
wheel_edge_r = 9.0                  # afronding van het loopvlak (getekend)
wheel_bore = 8.0                    # 608: as O8 (M8-bout als as)
wheel_kg = 0.11
wheel_shore = 90.0
wheel_load_ok = 600.0               # (GESCHAT)
wheel_load_peak = 1500.0            # (GESCHAT)
wheel_tread_t = 14.0
wheel_tread_w = 15.0
wheel_crr = 0.015
bearing_608_C0 = 1370.0
bearing_608_C = 3300.0

# ---------------------------------------------------------------------
# Loopprofiel (v9 simple): gezet U-profiel staal 4 mm, binnen 25 breed (wiel 24: 0,5 mm per kant), 25 diep.
# Het wiel loopt met zijn loopvlak op het lijf; de 2 flenzen houden het wiel opzij (de zijkant van het wiel loopt
# langs de flens: dat is de "zijkracht" uit de opdracht). Alle wielassen liggen langs v (loodrecht op de platen).
# ---------------------------------------------------------------------
tk_t = 4.0
tk_gap = 25.0                       # binnenmaat tussen de flenzen (in v)
tk_depth = 25.0                     # lijf (binnen) tot flenspunt
tk_out = tk_gap + 2 * tk_t          # 33: buitenmaat in v
wh_gap = 0.3                        # getekende speling loopvlak - lijf
wh_d = wheel_d / 2 + wh_gap         # hart wiel 40,3 van de binnenkant van het lijf (15,3 buiten de flenspunt)
bolt_head = (6.5, 5.3)              # M8: kop (straal, hoogte); moer (straal, hoogte) gelijk getekend
nut_h = 6.5

# ---------------------------------------------------------------------
# X-as (v9 simple): 2 balken koker 50 x 30 x 4 (50 hoog) met het loopprofiel erop gelast: onder open naar boven
# (draagt het gewicht), boven open naar beneden. Elke balk zit met 1x M10 per staander en een vulplaat 10 mm tegen de
# achterkant van de staanders. 2 eindplaten 4 mm verbinden de balkeinden (= X-frame) en dragen motor en spanpoelie.
# ---------------------------------------------------------------------
x_v0 = up_v1 + 10.0                 # 58: voorkant balk en loopprofiel (vulplaat 10 mm; robot-bovenbalken eindigen op v 55)
xtk_web_z = (710.0, 1120.0)         # binnenkant lijf onder (open naar boven) / boven (open naar beneden)
xbm = (50.0, 30.0, 4.0)             # balk: hoogte (z), diepte (v), wand
x_shim_t = 10.0
xbm_bolt_dx = 14.0                  # 2x M10 per staander op x = hs_x +- 14 (vrij van de schoor op hs_x)
xbar_L = 1500.0                     # buitenmaat eindplaten
end_plate_t = 4.0
end_plate_v = (x_v0, 100.0)
limit_vz = (95.0, 860.0)            # eindschakelaar X-min / aanslag X-max op slede-hoogte
xwh_x = 200.0                       # 2 wielen per profiel op x = +-200 van het hart van de slede

# X-slede: staalplaat 4 mm achter de X-wielen; voor de X-wielen, achter de Z-loopprofielen en de LA36
slide_v0 = x_v0 + tk_out + 2.0      # 93
slide_t = 4.0
slide_half_x = 240.0
slide_z = (440.0, 1240.0)           # onderkant 10 mm boven de achterbanden (z 430)
slide_tab = (-30.0, 30.0, 1545.0)

# Riemaandrijving zoals v9 advanced: motor vast rechts, spanpoelie links, onderste part geklemd op de slede
belt_z = 915.0
belt_w = 15.0
belt_v = (64.0, 79.0)
pulley_x = 700.0
pulley_r = 15.0
belt_r = (15.2, 18.6)
drive_bracket_v = (52.0, 58.0)      # beugelplaat 6 mm voor de poelies, aan de eindplaat
chain_v = 70.0                      # midden kabelrups 40 breed (v 50..90, voor de slede) boven op de bovenste balk
chain_hw = 20.0
chain_z = xtk_web_z[1] + tk_t + xbm[0]      # 1174

# ---------------------------------------------------------------------
# Z-as (v9 simple): 2 loopprofielen VAST op de X-slede (zelfde plaat als de LA36), staand op x = +-ztk_x (binnenkant
# lijf), open naar x 0, op een strip 10 mm (getapt, M8 van voren door de slede). De boorplaat (= achterplaat
# spilbok, 4 mm) heeft links en rechts 2 wielen die in de profielen naar beneden rollen.
# ---------------------------------------------------------------------
ztk_x = 150.0
ztk_bar_t = 10.0
ztk_v0 = slide_v0 + slide_t + ztk_bar_t     # 107: voorkant voorste flens Z-profiel
ztk_z = (445.0, 1235.0)             # lengte van de vaste Z-profielen
ztk_bolt_z = (485.0, 590.0, 860.0, 1010.0, 1225.0)   # M8 in de strip, buiten de hoogte van de X-balken
zwh_dz = (690.0, 990.0)             # wielen op de boorplaat boven de onderkant van het gereedschap
zplate_half_x = 135.0
zplate_top = 1015.0                 # bovenkant boorplaat boven de onderkant van het gereedschap
zg_top = zplate_top                 # (voor de spiraalkabel)

# Actuator: Linak LA36 (parts/actuator/linear-actuator-la36-data-sheet-eng.pdf), 24 V, 1700 N, spindel 20 mm,
# tandwiel F 1:18, slag 400, achterbevestiging en stangoog massief O12,2. Pen-op-pen recht in het midden tussen de
# buizen (x 0), huis boven, naar achteren (+v) boven de spilmotor. Ingetrokken = rijstand. (Zoals v6.)
act_stroke = depth_max + drive_z    # 400
act_Lr = 250.0 + act_stroke         # inbouwmaat ingetrokken (datasheet: slag > 300 -> 250 + slag) = 650
act_x = 0.0
act_v = ztk_v0 + tk_out + 2.0 + 4.0 + 28.0   # 174: LA36 3 mm achter de boorplaat (buis 50 diep)
act_pin_z = drive_z + 665.0 + 650.0     # 1515: stangoog 665 boven de frees (beugel boven de bovenplaat spilbok)
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
sb_back_t = 4.0                     # achterplaat spilbok = boorplaat 4 mm
sb_back_v0 = ztk_v0 + tk_out + 2.0   # 142: boorplaat 2 mm achter de Z-profielen
spindle_dv = 120.0                  # hart spil achter de boorplaat (LA36-buis ertussen)
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
x_crr = wheel_crr
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
spiral_x = 185.0                    # spiraalkabel rechts naast het rechter Z-profiel (buitenkant 154)
spiral_z0 = 455.0                   # vast anker onder op de X-slede, bewegend anker boven op de boorplaat
