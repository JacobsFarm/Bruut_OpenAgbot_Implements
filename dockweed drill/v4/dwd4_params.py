import math

# =====================================================================
# Dockweed drill v4 (ridderzuringfrees: X-as op aftakasbuizen, Z-as = steunpoot / drop-leg trailer jack) - parameters
# Portaal achter op de Bruut OpenAgbot: X-as (links-rechts, slag 1000) + Z-as (op-neer),
# de robot is de Y-as. Snellopende vermorzelfrees O180 in een pot O250 die op de zode landt.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong = midden van de robot. Het portaal hangt achter de achterste onderbalk (rear_outer).
# Hulpmaat v = afstand achter de achterkant van die balk: robot-y = robot_beam_rear_face - v.
# De onderdelen worden in (x, v, z) getekend en daarna gespiegeld naar robotcoordinaten (dwd4_parts.to_robot).
# Alle maten staan hier; nooit hardcoden in dwd4_parts.py / build_dwd4.py.
# =====================================================================

VARIANT = "v4"

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
drive_z = 180.0                     # onderkant frees boven maaiveld tijdens rijden (slag steunpoot 380)
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
# X-as v2: 2 aftakasbuizen (citroenprofiel) als geleiding, 3 hulzen van de buitenbuis
# Maten Sparex 1B (binnen) / 2A (buiten): CONTROLEER aan het echte stuk.
# ---------------------------------------------------------------------
xbar_L = 1400.0                     # lengte binnenbuizen (1500 kopen, op maat zagen)
xbar_z = (760.0, 1060.0)            # hart onderste / bovenste buis
pto_b, pto_h, pto_t = 49.0, 39.5, 4.5        # binnenbuis: lengte in Z (tip-tip), dikte in V, wand
sl_b, sl_h, sl_t = 57.5, 48.0, 4.0           # buitenbuis (huls)
sleeve_L = 100.0                    # 2 hulzen op de bovenbuis
sleeve_pitch = 220.0
sleeve_low_L = 140.0                # 1 huls op de onderbuis (sleufgaten in de slede)
sleeve_slot = 14.0                  # ingezaagde sleuf aan de robotkant voor de steunribben
flange_t = 8.0                      # steunflens op de staander
flange_half_x = 35.0
flange_half_z = 45.0
rib_t = 10.0
rib_half_x = 30.0
tube_v = up_v1 + 45.0               # hart buizen
pad_t = 8.0                         # opzetplaat op de huls
pad_half_z = 50.0
scraper_t = 8.0
end_plate_t = 12.0                  # eindplaat staal, verbindt de 2 buizen
slide_t = 10.0                      # X-slede alu
slide_v0 = tube_v + sl_h / 2.0 + pad_t
slide_half_x = 150.0
slide_z = (700.0, 1120.0)
belt_z = 880.0
belt_w = 15.0
pulley_z = 923.0
motor_dx = 120.0                    # NEMA 23 + 5:1 naast het spilhart

# ---------------------------------------------------------------------
# Z-as v4: steunpoot ("drop-leg" trailer jack, side-wind, vierkant 2,5"/2", slag 15" = 380 mm).
# Buitenbuis vast op de X-slede, binnenbuis met de spilbok beweegt. In de poot zit een trapeziumspindel met een
# kegelwiel bovenin; een NEMA 23 zit op de slingeras. Trapeziumspindel = zelfremmend: geen rem nodig.
# Maten van een gangbare 7000 lb drop-leg jack: CONTROLEER aan het gekochte exemplaar.
# ---------------------------------------------------------------------
jack_outer = (65.0, 4.0)            # buitenbuis 65 x 65 x 4 (2,5")
jack_inner = (50.0, 5.0)            # binnenbuis 50 x 50 x 5 (2")
jack_stroke = 380.0
jack_outer_z = (910.0, 1670.0)      # buitenbuis, vast (onderkant boven de spilbok in rijstand)
jack_head = 90.0                    # kegelwielhuis op de buitenbuis
jack_mount_z = (920.0, 1110.0)      # montageplaat op de X-slede
jack_mount_t = 8.0
inner_bottom = 600.0                # onderkant binnenbuis boven onderkant gereedschap
inner_L = 810.0                     # binnenbuis: 300 mm overlap op de diepste stand
guide_bush_L = 150.0                # PE-bus onder in de buitenbuis + PE-ring boven op de binnenbuis (speling weg)
jack_lead = 6.0                     # spindelspoed per slingeromwenteling in de snelle stand [mm] (geschat)
jack_eff = 0.27                     # trapeziumspindel 0,3 x kegelwiel 0,9 (geschat)
jack_motor_T = (2.2, 1.6)           # NEMA 23 closed-loop: koppel bij 250 / 400 rpm [Nm] (geschat)
jack_rpm_max = 450.0                # max. slingertoerental (spindel en kegelwiel zijn voor handbediening gemaakt)
jack_play = 0.3                     # speling na het opvullen met PE-strips [mm]

# ---------------------------------------------------------------------
# Spilbok, spil, motor
# ---------------------------------------------------------------------
sb_back_t = 6.0
spindle_dv = 75.0                   # hart spil achter de achterplaat (achterplaat op de achterkant van de binnenbuis)
sb_lo = 408.0                       # onderste plaat boven onderkant gereedschap (40 hoger dan v2: hoge bus)

# 2x UCP 204 staand lagerblok (op voorraad, parts/lagers/UCP 204: IBU 995.00647). De spil staat verticaal, dus de
# lagerblokken zitten met hun voet tegen een staande lagerplaat tussen de zijplaten.
ucp_d = 20.0                        # asdiameter
ucp_bolt = 95.0                     # boutgatafstand (e)
ucp_L = 127.0                       # lengte voet (a)
ucp_b = 38.0                        # breedte voet (b), hier langs de spil (z)
ucp_slot = (13.0, 19.0)             # sleufgaten
ucp_H = 65.0                        # totale hoogte (I)
ucp_h = 33.3                        # ashoogte vanaf de voet (Z)
ucp_foot_t = 14.0                   # dikte voet (geschat)
ucp_ring_d = 64.0                   # buitenmaat lagerhuis rond de as (geschat)
ucp_ring_w = 31.0                   # breedte binnenring met stelschroeven (UC204)
ucp_kg = 0.65
bearing_plate_t = 10.0              # staande lagerplaat, voet van de lagerblokken ertegen
bearing_lo = sb_lo + 8.0 + 31.0     # hart onderste UCP 204 boven onderkant gereedschap
bearing_dist = 140.0                # hart-hart lagers
bearing_hi = bearing_lo + bearing_dist
sb_mo = bearing_hi + ucp_b / 2 + 4.0          # bovenplaat van de spilbok (boven het bovenste lager, onder de ketting)
shaft_d = ucp_d                     # spilas O20 C45 (h7) door de lagers
shaft_top = sb_mo + 8.0 + 40.0      # bovenkant spilas (kettingwiel erop)
spindle_tube = (42.4, 4.0)          # buis 42,4 x 4 over de overhang (gelast op de as en de spilflens): O20 alleen is
                                    # te slap voor 400 mm overhang (zie dwd4_calc.shaft)
spindle_tube_top = bearing_lo - ucp_b / 2 - 3.0        # buis stopt net onder het onderste lagerhuis

# Spilmotor: 800 W tandwielmotor met voet (op voorraad, parts/800 watt motor; AliExpress 1005013021961260, 48 V
# geborsteld, 500 rpm uitgaand volgens de advertentie: CONTROLEER het typeplaatje). Staat rechtop achter de spil,
# uitgaande as omhoog, 10B-1 ketting naar de spil (snelle overbrenging 38T -> 12T).
motor_P = 800.0                     # W, opgegeven vermogen
motor_rpm = 500.0                   # uitgaand toerental tandwielmotor (advertentie)
motor_V = 48.0
motor_peak = 2.0                    # stroomgrens regelaar x nominaal (geborsteld, kort)
motor_shaft_d = 19.0                # uitgaande as O19 h6, spie 6x6
motor_shaft_out = 35.0
motor_total_len = 260.0             # tekening: 260 over de as
motor_nose = (35.0, 65.0, 45.0, 80.0)    # (van, tot, O van, O tot) langs de as vanaf het aseinde (als fpa V2, geschat)
motor_ring = (65.0, 110.0, 120.0)        # tandwielkast met spanring
motor_body = (110.0, 255.0, 105.0)       # motorhuis
motor_cap = (255.0, 260.0, 95.0)
motor_foot = (119.0, 234.0)              # voet 115 lang (tekening)
motor_foot_holes = (139.0, 219.0)        # 2 gaten op 80 (tekening)
motor_foot_w = 90.0                      # AANNAME
motor_foot_hole_dx = 70.0                # gatafstand dwars (AANNAME)
motor_foot_t = 6.0
motor_foot_h = 64.0                      # ashoogte boven de onderkant van de voet (tekening)
motor_kg = 9.0                           # geschat
motor_plate_t = 10.0                # motorplaat achter de spilbok, met lippen in sleuven van de zijplaten (kettingspanning)
motor_slot = 12.0                   # verstelling langs de ketting (sleuven in de zijplaten)
chain_pitch = 15.875                # 10B-1 (ISO 606), zie parts/Kettingwielen/ketting 10B.txt
roller_d = 10.16
sprocket_w = 9.1
chain_break_N = 22200.0
z_motor_sprocket = 38               # 10B-1-38-T, Taper-Lock 2012 + bus 19 (parts/Kettingwielen/19mm h6 shaft)
z_spindle_sprocket = 12             # 10B-1-12, boring 20 H7 + spie 6x6 (CONTROLEER levering, lijst heeft 16/19/30)
chain_links = 50                    # even aantal schakels -> hartafstand (dwd4_calc.chain_center)
drive_chain_z = sb_mo + 8.0 + 18.0  # kettingvlak boven onderkant gereedschap
chain_guard_gap = 8.0               # kettingkast: ruimte rond de schakelplaten
sb_back_top = 710.0                 # bovenkant achterplaat spilbok (boven de onderkant van de binnenbuis: bouten)


def pitch_d(z):
    """Steekcirkel kettingwiel (mm)."""
    return chain_pitch / math.sin(math.pi / z)


def chain_center(links=None):
    """Hartafstand (mm) motor - spil bij een even aantal schakels (ISO 606 benadering)."""
    n = chain_links if links is None else links
    z1, z2 = z_spindle_sprocket, z_motor_sprocket
    a = n - (z1 + z2) / 2.0
    k = ((z2 - z1) / (2 * math.pi)) ** 2
    c = (a + math.sqrt(a * a - 8 * k)) / 4.0
    return c * chain_pitch


spindle_motor_dv = chain_center()   # spilmotor achter de spil (+v, van de robot af), x = 0: vrij van de potstangen op x = +-100

cutter_rpm = 1500.0                 # regelaar op 95 % (max. 500 x 38/12 = 1583 rpm)
mower_rpm = 1500.0                  # zelfde spil: de geborstelde tandwielmotor haalt geen 3000 rpm meer
idle_w = 80.0                       # verlies spil + lagers + ketting bij 1500 rpm (geschat)

# ---------------------------------------------------------------------
# Pot (rust met eigen gewicht op de zode, sensor = maaiveldreferentie)
# ---------------------------------------------------------------------
pot_d = 219.1                       # "bus" zoals Robot Ruud: stuk stalen pijp DN200 (219,1 x 3,6)
pot_h = 180.0
pot_t = 3.6
pot_lid_t = 5.0
pot_rim = 30.0                      # busrand hangt in rust zoveel onder de freesonderkant
pot_rod_dx = 100.0
pot_rod_d = 16.0
pot_kg_est = 6.5
flap = False                        # geen spatflap: de hoge bus vangt het zelf op

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
rapid_z = 40.0                      # steunpoot: max. ca. 450 slingeromw./min x 6 mm
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
cam_x = 0.0                         # vaste camera hoog boven de werkstrook (zoals Robot Ruud)
cam_mast_x = 250.0                  # mast 40 x 40 op de rechter staander
cam_z = 1900.0                      # bovenkant camera-arm (boven de steunpootkop en de spilmotor)
cam_v = 680.0                       # camera achter de spillijn (rijrichting -y: ziet de plant eerst)
ebox = (300.0, 250.0, 120.0)        # IP65 kast (x, z, v)
ebox_z0 = 745.0
ebox_plate_t = 3.0                  # montageplaat E-kast op de dwarskoker
chain_z = xbar_z[1] + 60.0          # kabelrups boven de hulzen
spiral_turns = 22
spiral_x = -95.0                    # spiraalkabel links van de spilbok
spiral_z0 = 1150.0                  # bovenste anker op de buitenbuis van de steunpoot
