import math

# =====================================================================
# Dockweed drill v6 (ridderzuringfrees) - parameters
# Portaal achter op de Bruut OpenAgbot: X-as (links-rechts, slag 1000) + Z-as (op-neer), de robot is de Y-as.
# v6: frame van kokers 40 x 40 x 3; de 2 aftakasbuizen zitten met 2x M10 per eind tussen 2 zijplaten (los te
# bouten); Z-as = koker met 2 HGR15-rails en een elektrische actuator 24 V (LA36-klasse) pen-op-pen naast de koker;
# 800 W tandwielmotor direct op een spilas O30 in 2x UCP 206 (klauwkoppeling maat 28); stalen bus O219 zoals v5.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong = midden van de robot. Het portaal hangt achter de achterste onderbalk (rear_outer).
# Hulpmaat v = afstand achter de achterkant van die balk: robot-y = robot_beam_rear_face - v.
# De onderdelen worden in (x, v, z) getekend en daarna gespiegeld naar robotcoordinaten (dwd6_parts.to_robot).
# Alle maten staan hier; nooit hardcoden in dwd6_parts.py / build_dwd6.py.
# =====================================================================

VARIANT = "v6"

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
drive_z = 200.0                     # onderkant frees boven maaiveld tijdens rijden (actuator ingetrokken)
z_ref = drive_z                     # referentiestand van de Z-slede in de build (rijstand)
work_x = 150.0                      # stand voor de standaardafbeeldingen
work_z = -depth_std

# ---------------------------------------------------------------------
# Aanbouwbok (headstock): 2 staanders 40 x 40 x 3 achter de onderbalk, op het gatenraster
# Vrije gaten in rear_outer: x = +-225 en +-275 (+-325/+-425 = frame_bolts, +-375 boven het houten blok).
# ---------------------------------------------------------------------
hs_x = 250.0                        # hart staander
hs_bolt_dx = 25.0                   # M10 op x = hs_x +- 25 (gaten 225 en 275)
hs_bolt_v = -robot_beam / 2.0       # hart onderbalk
hs_plate_half_x = 50.0
hs_plate_t = 8.0                    # bovenplaat, klemplaat, achterplaat
up_size = 40.0                      # staander 40 x 40 x 3 (v6: overal kokers van 40)
up_wall = 3.0
up_v0 = hs_plate_t                  # voorkant staander (tegen de achterplaat)
up_v1 = up_v0 + up_size
up_z0 = robot_lower_beam_z[0] - hs_plate_t        # 611: onderkant klemplaat
up_z1 = 1110.0
up_cap_t = 6.0
gusset_t = 6.0
gusset_h = 75.0                     # schoor boven de bovenplaat, tegen de staander (v6: onder de M12 van de dwarsbalk)
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
# X-as: 2 aftakasbuizen (citroenprofiel) als geleiding, 3 hulzen van de buitenbuis
# Maten Sparex 1B (binnen) / 2A (buiten): CONTROLEER aan het echte stuk.
# v6: de buizen liggen tussen 2 zijplaten (12 mm) op x = +-xbar_L/2. Per buiseind een ingelaste prop met 2x M10
# (tap), bouten van buiten door de zijplaat: buis los = 4 bouten eruit. Geen steunribben meer, de hulzen zijn dicht.
# De zijplaten hangen aan 2 dwarsbalken 40 x 40 x 3 (een per buishoogte, voor de buizen langs), die met 1x M12
# per kruising tegen de achterkant van de staanders zitten.
# ---------------------------------------------------------------------
xbar_L = 1400.0                     # buitenmaat tussen de buitenkanten van de zijplaten
end_plate_t = 12.0                  # zijplaat staal (heet hier end_plate, zoals v5)
xbar_z = (760.0, 1060.0)            # hart onderste / bovenste buis
pto_b, pto_h, pto_t = 49.0, 39.5, 4.5        # binnenbuis: lengte in Z (tip-tip), dikte in V, wand
sl_b, sl_h, sl_t = 57.5, 48.0, 4.0           # buitenbuis (huls)
sleeve_L = 100.0                    # 2 hulzen op de bovenbuis
sleeve_pitch = 220.0
sleeve_low_L = 140.0                # 1 huls op de onderbuis (sleufgaten in de slede)
xbeam = (40.0, 3.0)                 # dwarsbalk 40 x 40 x 3, direct achter de staanders
xbeam_v = (up_v1, up_v1 + xbeam[0])
tube_gap = 6.0                      # vrije ruimte tussen dwarsbalk en schraper van de huls
tube_v = xbeam_v[1] + sl_h / 2.0 + 1.5 + tube_gap   # hart buizen (schraper 1,5 groter dan de huls)
plug_L = 25.0                       # prop in het buiseind (gelast), 2x M10 getapt
tube_bolt_dz = 10.0                 # M10 op z = buishart +- 10
side_plate_v = (xbeam_v[0], tube_v + 35.0)
side_plate_z = (xbar_z[0] - 40.0, xbar_z[1] + 40.0)
pad_t = 8.0                         # opzetplaat op de huls
pad_half_z = 50.0
scraper_t = 8.0
slide_t = 10.0                      # X-slede alu
slide_v0 = tube_v + sl_h / 2.0 + pad_t
slide_half_x = 150.0
slide_z = (700.0, 1120.0)
slide_tab = (-150.0, -40.0, 1300.0)  # verlengstuk links boven aan de slede (x0, x1, z1): bovenste pen actuator
belt_z = 880.0
belt_w = 15.0
pulley_z = 923.0
motor_dx = 120.0                    # NEMA 23 + 5:1 naast het spilhart

# ---------------------------------------------------------------------
# Z-as: koker 120 x 60 x 3 met 2 HGR15-rails (beweegt), 4 HGH15CA-wagens vast op de X-slede (zoals v2).
# Aandrijving: elektrische actuator 24 V pen-op-pen links naast de koker: bovenste pen op de X-slede, stangoog
# onderaan de Z-koker. Ingetrokken = rijstand. Maten van een Linak LA36-klasse actuator, slag 400: AANNAME,
# CONTROLEER op de datasheet van de gekozen variant (inbouwlengte, stangoog, kracht/snelheid).
# ---------------------------------------------------------------------
rail_h = 28.0                       # HGR15 + HGH15CA
riser_t = 8.0                        # platstaal 25 x 8 onder de rails (M4 getapt; geen spindel ertussen zoals v2)
zt_w, zt_d, zt_wall = 120.0, 60.0, 3.0
zt_L = 900.0
zt_bottom = 410.0                   # onderkant Z-koker boven onderkant gereedschap
z_rail = (110.0, 890.0)             # rails t.o.v. de onderkant van de koker (dekt de wagens over de hele slag)
z_rail_dx = 40.0

act_stroke = depth_max + drive_z    # 400
act_Lr = 640.0                      # inbouwmaat ingetrokken, hart pen - hart pen (AANNAME: slag + 240)
act_x = -(zt_w / 2.0 + 5.0 + 30.0)  # hart actuator: links naast de koker
act_tube_d = 60.0                   # buitenbuis (rond getekend)
act_rod_d = 30.0                    # binnenbuis / stang
act_rod_out = 60.0                  # stang zichtbaar onder de buis, ingetrokken
act_house = (90.0, 80.0, 150.0)     # huis met tandwielkast bovenaan (x, v, z)
act_motor = (70.0, 190.0)           # motor parallel aan de spindel, naar -x (O, lengte)
act_eye_dz = 25.0                   # hart stangoog boven de onderkant van de Z-koker
act_pin_d = 12.2                    # pennen O12
act_eye_w = 20.0                    # dikte stangoog / achterste oog
act_force = 1700.0                  # nominale kracht [N] (AANNAME, kies de spindelvariant)
act_speed = (100.0, 75.0)           # snelheid onbelast / bij 600 N [mm/s] (AANNAME)
act_eff = 0.30                      # rendement trapeziumspindel + kast (zelfremmend)
act_duty = 0.20                     # toegestane inschakelduur (catalogus LA36: 20 %)
act_V = 24.0
act_kg = (5.5, 0.8)                 # vast deel (huis, buis, motor) / bewegend deel (stang)
dcdc = (48.0, 24.0, 20.0)           # omvormer 48 -> 24 V, 20 A

# ---------------------------------------------------------------------
# Spilbok, spil, motor
# ---------------------------------------------------------------------
sb_back_t = 6.0
spindle_dv = 75.0                   # hart spil achter de achterplaat (achterplaat op de achterkant van de Z-koker)
sb_lo = 408.0                       # onderste plaat boven onderkant gereedschap
sb_side_x = 87.5                    # hart zijplaten (5 mm), net buiten de lagervoeten
sb_back_top = 710.0                 # bovenkant achterplaat spilbok

# 2x UCP 206 staand lagerblok (as 30). De spil staat verticaal, de voeten zitten tegen een staande lagerplaat.
# Catalogusmaten UCP 206: CONTROLEER aan het gekochte lagerblok.
ucp_d = 30.0                        # asdiameter
ucp_bolt = 121.0                    # boutgatafstand (e)
ucp_L = 165.0                       # lengte voet (a)
ucp_b = 48.0                        # breedte voet (b), hier langs de spil (z)
ucp_slot = (17.0, 20.0)             # sleufgaten (M14)
ucp_H = 82.0                        # totale hoogte
ucp_h = 42.9                        # ashoogte vanaf de voet
ucp_foot_t = 17.0                   # dikte voet (geschat)
ucp_ring_d = 80.0                   # buitenmaat lagerhuis rond de as (geschat)
ucp_ring_w = 38.1                   # breedte binnenring met stelschroeven (UC206)
ucp_kg = 1.4
ucp_C = 19500.0                     # dynamisch draaggetal [N] (UC206, catalogus)
bearing_plate_t = 10.0
bearing_lo = sb_lo + 8.0 + ucp_b / 2 + 7.0     # hart onderste lager boven onderkant gereedschap
bearing_dist = 140.0
bearing_hi = bearing_lo + bearing_dist
sb_mo = bearing_hi + ucp_b / 2 + 4.0          # bovenplaat van de spilbok
shaft_d = ucp_d                     # spilas O30 C45 massief, onderin in de spilflens gelast (geen buis meer nodig)

# Flexibele klauwkoppeling maat 28 (GR / ROTEX 28, ster 92 Sh A): naaf O19 (motor, spie 6) en O30 (spil, spie 8).
# Maat 24 kan maximaal O28 boren.
jaw_d = 65.0
jaw_L = 90.0
jaw_star = 20.0
jaw_T = (95.0, 190.0)               # nominaal / max. koppel [Nm] (catalogus, controleer)
jaw_hub_L = 35.0
jaw_z0 = sb_mo + 8.0 + 7.0          # onderkant koppeling boven onderkant gereedschap
jaw_kg = 0.95
shaft_top = jaw_z0 + jaw_hub_L      # bovenkant spilas (in de onderste naaf)

# Spilmotor: 800 W tandwielmotor met voet (op voorraad, parts/800 watt motor; 48 V geborsteld, 500 rpm volgens de
# advertentie: CONTROLEER het typeplaatje). Staat recht boven de spil, as omlaag in de klauwkoppeling (als v5).
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
mower_rpm = motor_rpm
idle_w = 45.0                       # verlies spil + lagers + koppeling bij 500 rpm (geschat, grotere lagers)

# ---------------------------------------------------------------------
# Bus (zoals v5 / Robot Ruud): stalen pijp DN200 met deksel, rust met eigen gewicht op de zode
# ---------------------------------------------------------------------
pot_d = 219.1
pot_h = 180.0
pot_t = 3.6
pot_lid_t = 5.0
pot_rim = 30.0
pot_rod_dx = 100.0
pot_rod_d = 16.0
pot_kg_est = 6.5
flap = False

# ---------------------------------------------------------------------
# Gereedschap
# ---------------------------------------------------------------------
cutter_d = 180.0
cutter_teeth = 4
mower_tip_d = 230.0
mower_rim = 30.0

# ---------------------------------------------------------------------
# Aandrijving en proces
# ---------------------------------------------------------------------
stepper_T = 3.0                     # NEMA 23 closed-loop [Nm]
x_gear = 5.0
x_pulley_T = 20
htd_pitch = 5.0
plunge_v = 25.0                     # insteeksnelheid [mm/s]
rapid_x = 200.0
rapid_z = act_speed[1]              # actuator bij last
dwell_s = 1.0
z_force_limit = 600.0               # software-begrenzing [N]
cut_energy = (0.5e6, 2.0e6)
cut_energy_std = 1.0e6
thrust_n = (150.0, 1.0)
side_force = 300.0
drive_speed = 500.0
stop_start_s = 4.0

# ---------------------------------------------------------------------
# Camera, licht, elektra
# ---------------------------------------------------------------------
cam_x = 0.0                         # vaste camera hoog boven de werkstrook (zoals v5)
cam_mast_x = 250.0                  # mast 40 x 40 op de rechter staander
cam_z = 1900.0
cam_v = 740.0                       # camera achter de spillijn (rijrichting -y: ziet de plant eerst)
ebox = (300.0, 250.0, 120.0)
ebox_z0 = 745.0
ebox_plate_t = 3.0
chain_z = xbar_z[1] + 60.0          # kabelrups boven de hulzen
spiral_turns = 12
spiral_x = 100.0                    # spiraalkabel rechts naast de Z-koker, boven de X-motor
spiral_z0 = 965.0                   # onderste (vaste) anker op de X-slede
