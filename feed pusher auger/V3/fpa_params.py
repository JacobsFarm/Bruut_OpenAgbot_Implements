import math

# =====================================================================
# Feed pusher auger (voerschuifvijzel), V3 - parameters
# V2 = V1 met een aandrijfbus (200 mm insteek + breekbout) links en een pennenplaat met lagers in de vijzel rechts.
# V3 = V2 met de bestaande wokkel (gemeten, zie ../parts_list/auger_specs.txt): Ø300, buis Ø60 x 3, 1420 lang,
# M12 breekbout 35 mm van het eind tussen 2 opgelaste ringen, rechts een kunststof ring Ø20 op een vaste pen Ø20.
# Aanbouwdeel aan de achterkant van de Bruut OpenAgbot (kant van de vaste wielmotoren).
# De robot rijdt bij het voerschuiven met de vijzel voorop (richting -y), de stuurkoppen zitten dan achter.
#
# Assen = robotmodel: x = rechts, y = rijrichting van de robot (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong = midden van de robot (wielmiddens op (+-375, +-500)). Het werktuig staat dus direct in
# robotcoordinaten. Voerhek aan de +x kant: de vijzel voert naar +x.
# Alle maten staan hier; nooit hardcoden in fpa_parts.py / build_fpa.py.
# =====================================================================

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbot design/agbot_params.py", die map staat niet in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375             # align_width / 2
robot_axle_y = -500             # achteras (align_length / 2)
robot_axle_z = 215              # ground_to_axle
robot_wheelbase = 1000
robot_tire_d = 430
robot_tire_w = 100

# wielbeugel: zijplaat met naar buiten gezette flens (40 breed, 4 dik), 4 gaten M10 op 100 mm steek.
# Lokaal (oorsprong hart as): flens x 72..112 (beide zijden), achterste flens y -82..-78,
# gaten op x +-92, z -15 / 85 / 185 / 285.
wf_x = (72.0, 112.0)            # flens over x (lokaal, absolute waarde)
wf_hole_dx = 92.0               # hart gat t.o.v. hart wiel
wf_face_y = robot_axle_y - 82.0  # achtervlak achterste flens (wereld): -582
wf_t = 4.0
wf_hole_z = tuple(robot_axle_z + z for z in (-15.0, 85.0, 185.0, 285.0))   # 200, 300, 400, 500
wf_z = (robot_axle_z - 35.0, robot_axle_z + 345.0)                        # zijplaat 180..560
m10_hole = 10.4
robot_lower_beam_z = (619.0, 659.0)   # onderste dwarsbalken, voor de botscontrole
robot_front_beam_y = 575.0            # chassis_beam_1 front_outer
robot_grid = 50

# ---------------------------------------------------------------------
# Vijzel
# ---------------------------------------------------------------------
auger_y = -960.0                # hart vijzelas (wereld-y): 48 mm vrij achter de band
auger_z = 175.0                 # hart as boven de vloer (zelfde als V2): blad Ø300 nu 25 mm vrij van de vloer
shaft_d = 30.0                  # lagertap van de aandrijfbus (UCF206), C45 h9
# V3: bestaande wokkel, gemeten (parts_list/auger_specs.txt)
auger_len = 1420.0              # totale lengte wokkel (kernbuis)
blade_d = 300.0
core_d = 60.0                   # kernbuis Ø60, binnen Ø54
core_t = 3.0
core_x = (-700.0, -700.0 + auger_len)   # kernbuis -700..720: rechts 8 mm van de hangende strip (pen 27 mm in de ring)
# geschat (niet gemeten)
blade_pitch = 260.0             # rechtsgangig: draait de voorkant omhoog en voert naar +x (voerhek)
blade_t = 5.0
blade_x = (core_x[0] + 60.0, core_x[1] - 10.0)   # beblading vrij van de breekbout, tot vlak bij de uitworp

# Aandrijfkant (links): getrapte bus (gedraaid uit Ø65 C45): lagertap Ø30 door de UCF206 met spiebaan voor het
# 38T kettingwiel, kraag tegen de kopse kant van de kernbuis, holle insteek in de kernbuis, vast met de breekbout.
bush_spigot_d = 53.7            # V3: kernbuis binnen Ø54 -> 0,3 mm speling
bush_spigot_id = 36.0
bush_spigot_len = 200.0
bush_collar_x = (-713.0, core_x[0])    # kraag Ø60 tussen lagerplaat (-720) en begin kernbuis (-700)
# V3: M12 breekbout (gat Ø12,4 35 mm van het eind, gemeten) tussen 2 opgelaste ringen boven en onder, zodat kop en
# borgmoer recht zitten. Dubbele afschuiving op de spleet insteek/kernbuis.
shear_bolt_d = 12.0
shear_hole_d = 12.4
shear_bolt_As = 84.3            # mm2 spanningsdoorsnede M12
shear_bolt_Rm = 400.0           # 4.6 (AANNAME: klasse van de bestaande breekbout onbekend)
shear_bolt_dx = 35.0            # hart gat vanaf de kopse kant van de kernbuis (gemeten)
shear_bolt_len = 90.0           # M12 x 90: 2 x 35 + borgmoer 12 + uitsteek
lock_nut_h = 12.0               # borgmoer DIN 985
boss_d = 24.0                   # opgelaste ringen (geschat uit de foto)
boss_top = 35.0                 # vlakke kant 35 uit het hart, 5 mm boven de buis

# Vrije kant (rechts): de rechter eindplaat heeft een uitsparing (open aan onder- en voorkant) waar de hele vijzel
# doorheen kan. De pen zit op een hangende strip (zoals de oude ophanging): 10 mm met 2 opgezette randen, boven de
# uitsparing met 4x M12 aan de eindplaat.
# V3: geen lagers meer. De wokkel draait met een slijtvaste kunststof ring (Ø54 / Ø20 x 30, gemeten) in het eind van
# de kernbuis om een vaste pen Ø20 die 35 mm uit de strip steekt (gemeten), door de strip gestoken en gelast.
# Uitbouwen: breekbout eruit, 4 moeren los, strip met pen eraf, vijzel 200 mm naar rechts door de uitsparing.
pin_d = 20.0
pin_len = 35.0                  # vrije lengte uit de strip
wear_bush_bore = 20.0
wear_bush_len = 30.0
opening_v = 170.0               # uitsparing tot v 170 (blad tot v 160)
opening_z = 350.0               # en tot z 350 (blad tot z 335)
pin_plate_t = 10.0              # hangende strip
pin_plate_v = (-55.0, 55.0)     # horizontaal (v), rond de vijzelas
pin_plate_z = (auger_z - 55.0, 475.0)   # van onder de pen tot boven de bouten (wereld-z)
pin_lip = 30.0                  # opgezette randen (kantbank) aan beide v-einden, naar buiten (+x)
pin_bolt_v = (-30.0, 30.0)
pin_bolt_z = (395.0, 455.0)

inner_width = 1440.0            # tussen linker zijplaat en rechter lagerplaat
plate_t = 8.0
xi = inner_width / 2.0          # 720
xo = xi + plate_t               # 728
pin_end_x = xo - pin_len        # 693: eind van de pen in de wokkel, 27 mm in de ring

# ---------------------------------------------------------------------
# Kap: één plaat 2 mm, 4 zetten op de kantbank (zelfde principe als de simpele versie).
# Hartlijn (v, dz) t.o.v. de vijzelas, v = y - auger_y (+v = naar de robot).
# ---------------------------------------------------------------------
hood_t = 2.0
hood_pts = ((195.0, -115.0), (195.0, 140.0), (150.0, 195.0), (-115.0, 195.0), (-195.0, 65.0), (-215.0, 42.0))
hood_top_z = auger_z + 195.0    # 370, hartlijn bovenplaat
hood_top_outer = hood_top_z + hood_t / 2.0

flap_t = 10.0                   # rubber afstrijkflap aan de robotzijde, tot 5 mm boven de vloer
flap_z = (5.0, 110.0)
strip_t = 5.0
strip_z = (70.0, 100.0)

# ---------------------------------------------------------------------
# Dwarsligger op de kap (draagt alles) en kopplaten
# ---------------------------------------------------------------------
beam = 80.0                     # koker 80 x 80 x 3
beam_wall = 3.0
beam_v = (105.0, 185.0)
beam_z = (hood_top_outer, hood_top_outer + beam)
cap_t = 8.0                     # kopplaat op elk eind (gelast), steekt 40 mm boven de ligger uit:
cap_v = (95.0, 195.0)           # daar 2x M12 door de zijplaat, moeren bereikbaar boven de ligger
cap_z = (hood_top_outer + 1.0, hood_top_outer + beam + 40.0)
cap_bolt_v = (115.0, 175.0)
cap_bolt_z = hood_top_outer + beam + 20.0

# ---------------------------------------------------------------------
# Zijplaat links (aandrijfkant) en lagerplaat rechts (open uitworp naar het voerhek), (v, z)
# ---------------------------------------------------------------------
side_left_pts = ((205.0, 15.0), (105.0, 15.0), (68.0, 95.0), (-75.0, 95.0), (-225.0, 240.0),
                 (-225.0, 272.0), (-122.0, 380.0), (95.0, 380.0), (95.0, cap_z[1] + 10.0),
                 (205.0, cap_z[1] + 10.0))
# V2: groter naar voren en naar boven, met de uitsparing voor de vijzel (open aan onder- en voorkant)
side_right_pts = ((205.0, cap_z[1] + 10.0), (-60.0, cap_z[1] + 10.0), (-120.0, 410.0), (-120.0, opening_z),
                  (opening_v, opening_z), (opening_v, 105.0), (205.0, 140.0))
skid_v = (100.0, 190.0)         # PE-1000 glijslof onder de linker zijplaat
skid_z = (3.0, 33.0)
skid_w = 36.0

# ---------------------------------------------------------------------
# Lagers UCF206 (vierkant 108, gatafstand 83, M12) buiten op beide platen
# ---------------------------------------------------------------------
ucf_L = 108.0
ucf_J = 83.0
ucf_tf = 14.0

# ---------------------------------------------------------------------
# Aandrijving: voetmotor op de kap, ketting 10B-1 (5/8"), 12T -> 38T aan de linkerkant
# ---------------------------------------------------------------------
chain_pitch = 15.875             # 10B-1 (ISO 606), breukkracht min. 22,2 kN
roller_d = 10.16
z_motor = 12                    # V2: 12T op de motoras Ø19 (kracht, vijzel < 100 omw/min)
z_auger = 38                    # V2: 38T op de aandrijfbus Ø30 (Taper-Lock 2012)
sprocket_w = 9.1                # tandbreedte 10B-1
chain_break_N = 22200.0
guard_gap = 28.0                # kettingkast: ruimte rondom de kettingwielen (38T: kast ca. 50 mm boven de vloer)
x_sprocket = -xo - ucf_tf - 24.0 - 30.0     # -796, vlak van beide kettingwielen

# V2: tandwielmotor 800 W met voet (AliExpress 1005013021961260, maten uit parts/800 watt motor/data.json en de
# maattekening). Toerental en spanning staan niet op de tekening: motor_rpm is een aanname, controleer het typeplaatje.
motor_rpm = 300.0               # uitgaand toerental tandwielmotor (AANNAME)
motor_P = 800.0                 # W, opgegeven vermogen
motor_shaft_d = 19.0            # uitgaande as Ø19 h6 met spie
motor_key = (6.0, 6.0, 3.5, 2.8, 25.0)   # spie DIN 6885 A 6x6: (b, h, t1 asgroef, t2 naafgroef, lengte)
motor_v = -20.0                 # hart uitgaande as, t.o.v. vijzelas
# maten langs de motoras, gemeten vanaf het einde van de uitgaande as (tekening: totaal 260)
motor_total_len = 260.0
motor_shaft_out = 35.0          # as steekt 35 uit de neus van de tandwielkast
motor_nose = (35.0, 65.0, 45.0, 80.0)    # (van, tot, Ø bij van, Ø bij tot) conische neus tandwielkast (geschat uit de foto)
motor_ring = (65.0, 110.0, 120.0)        # (van, tot, Ø) tandwielkast met spanring, "120MM"
motor_body = (110.0, 255.0, 105.0)       # (van, tot, Ø) motorhuis (geschat uit de foto: 132 hoog incl. voet)
motor_cap = (255.0, 260.0, 95.0)         # aluminium achterkap
motor_foot = (119.0, 234.0)              # voet 115 lang (tekening), positie geschat uit de foto
motor_foot_holes = (139.0, 219.0)        # 2 gaten op 80 (tekening), midden onder de voet
motor_foot_w = 90.0                      # breedte voet (AANNAME, niet op de tekening)
motor_foot_hole_dv = 70.0                # gatafstand dwars (AANNAME)
motor_foot_t = 6.0
motor_foot_hole = 8.5                    # M8 (AANNAME)
base_t = 8.0                    # motorplaat op de kap (verdeelt de voetkrachten over de kapplaat)
base_x = (-712.0, -552.0)
base_v = (-105.0, 105.0 - 0.5)       # tot tegen de ligger; opstaande rand met 2x M10 aan de ligger
base_up_z = 52.0                # hoogte opstaande rand boven de kap
base_bolt_x = (-690.0, -575.0)
motor_shaft_end_x = x_sprocket - 20.0   # einde uitgaande as (buitenkant naaf kettingwiel), -816


def motor_x(d):
    """x (wereld) op afstand d vanaf het einde van de uitgaande as, richting de motor (+x)."""
    return motor_shaft_end_x + d


foot_t = motor_foot_t
foot_x = (motor_x(motor_foot[0]), motor_x(motor_foot[1]))
foot_v = (motor_v - motor_foot_w / 2.0, motor_v + motor_foot_w / 2.0)
foot_holes = tuple((motor_x(d), motor_v + s * motor_foot_hole_dv / 2.0)
                   for d in motor_foot_holes for s in (-1, 1))   # (x, v) 4x M8
shaft_height = 64.0             # hart as boven de onderkant van de voet (tekening)
motor_z = hood_top_outer + base_t + shaft_height    # 443

tens_pivot = (95.0, 330.0)      # (v, z) draaipunt kettingspanner, binnen de lus (slappe kant)
tens_idler_d = 40.0

# ---------------------------------------------------------------------
# Armen naar de wielmodules: 4 stuks (binnen- en buitenflens van beide achterwielen)
# ---------------------------------------------------------------------
arm_t = 8.0
adapter_w = 50.0
adapter_z = (180.0, 540.0)
end_w = 90.0
end_bolt_dx = 28.0
end_bolt_z = ((beam_z[0] + beam_z[1]) / 2.0 - 20.0, (beam_z[0] + beam_z[1]) / 2.0 + 20.0)
end_slot = 30.0                 # langgaten in de eindplaat: hoogte +-15 mm bijstellen (slijtage glijslof)
m12_hole = 13.0

# ---------------------------------------------------------------------
# Contragewicht voorop (2 blokken op de voorste onderbalk, M10 door het gatenraster)
# ---------------------------------------------------------------------
ballast_x = (110.0, 270.0)      # beide zijden
ballast_y = (500.0, 650.0)
ballast_h = 106.0               # 2 x ca. 20 kg

# ---------------------------------------------------------------------
# Werking (voor fpa_calc en de animatie)
# ---------------------------------------------------------------------
drive_speed = 0.30              # m/s rijsnelheid bij voerschuiven (1,1 km/h)
conveying_eff = 0.65            # axiale voersnelheid / (spoed x toerental), open vijzel op de vloer
fill_max = 0.6                  # max vulgraad (open vijzel met stapel ervoor)
feed_density = 280.0            # kg/m3 losgestort ruwvoer / TMR op de vloer
mu_floor = 0.5                  # voer op betonvloer
lambda_conv = 4.0               # weerstandsgetal vijzel (CEMA, vezelig/kleverig materiaal)
mu_blade = 0.5                  # wrijving voer op blad
idle_torque = 2.0               # Nm lagers, ketting
eta_drive = 0.9 * 0.97 * 0.8    # tandwielkast x ketting x motor
battery_v = 24.0


def pitch_d(z):
    return chain_pitch / math.sin(math.pi / z)


auger_rpm = motor_rpm * z_motor / float(z_auger)            # 94,7
