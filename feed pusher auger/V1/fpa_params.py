import math

# =====================================================================
# Feed pusher auger (voerschuifvijzel), advanced - parameters
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
auger_z = 175.0                 # hart as boven de vloer: blad 15 mm vrij van de vloer
shaft_d = 30.0                  # C45, h9
blade_d = 320.0
blade_pitch = 260.0             # rechtsgangig: draait de voorkant omhoog en voert naar +x (voerhek)
blade_t = 5.0
core_d = 60.3                   # kernbuis 60,3 x 4, op de as gepend
core_t = 4.0
blade_x = (-705.0, 715.0)       # beblading tot vlak bij de open eindplaat rechts (uitworp)
pin_d = 10.0                    # M10 8.8 pen rechts (door kern en asstomp)
shear_pin_d = 6.0               # M6 4.6 breekbout links (aandrijfkant), in geharde bus
pin_dx = 40.0
stub_in = 70.0                  # asstompen steken 70 mm in de kernbuis, gedragen door 2 ingelaste schijven

inner_width = 1440.0            # tussen linker zijplaat en rechter lagerplaat
plate_t = 8.0
xi = inner_width / 2.0          # 720
xo = xi + plate_t               # 728

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
side_right_pts = ((205.0, cap_z[1] + 10.0), (95.0, cap_z[1] + 10.0), (95.0, 380.0), (-75.0, 380.0),
                  (-75.0, 105.0), (70.0, 105.0), (205.0, 240.0))
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
# Aandrijving: voetmotor (B3) op de kap, ketting 08B-1 15T -> 30T aan de linkerkant
# ---------------------------------------------------------------------
chain_pitch = 12.7
roller_d = 8.51
z_motor = 15
z_auger = 30
sprocket_w = 7.2
x_sprocket = -xo - ucf_tf - 24.0 - 30.0     # -796, vlak van beide kettingwielen

motor_rpm = 300.0               # uitgaand toerental tandwielmotor
motor_P = 550.0                 # W afgegeven, 24 V DC, coaxiale tandwielkast i ~ 10
motor_shaft_d = 25.0
motor_v = -20.0                 # hart uitgaande as, t.o.v. vijzelas
base_t = 8.0                    # motorplaat op de kap (verdeelt de voetkrachten over de kapplaat)
base_x = (-712.0, -552.0)
base_v = (-105.0, 105.0 - 0.5)       # tot tegen de ligger; opstaande rand met 2x M10 aan de ligger
base_up_z = 52.0                # hoogte opstaande rand boven de kap
base_bolt_x = (-690.0, -575.0)
foot_t = 14.0
foot_x = (-707.0, -577.0)
foot_v = (-95.0, 55.0)
foot_holes = ((-692.0, -80.0), (-592.0, -80.0), (-692.0, 40.0), (-592.0, 40.0))   # (x, v) 4x M10
shaft_height = 75.0             # as boven de voetvlakken
gearbox_w = 120.0
motor_d = 120.0
motor_len = 230.0
motor_z = hood_top_outer + base_t + foot_t + shaft_height    # 468,5

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


auger_rpm = motor_rpm * z_motor / float(z_auger)            # 150
