import math

# =====================================================================
# Schotelborstels (disc brushes), simple - parameters
# Aanbouwdeel aan de achterkant van de Bruut OpenAgbot (standaard robot, kant van de vaste wielmotoren).
# De robot rijdt bij het borstelen met de borstels voorop (richting -y), net als bij de voerschuifvijzel.
#
# Eén bouwset, drie uitvoeringen (CONFIGS): 2 x Ø650, 2 x Ø750 of 1 x Ø850. Dezelfde toolbar, dezelfde
# borstelunit (klemplaat + kop) en dezelfde motor; alleen de borstel en zijn stand in de sleufgaten verschillen.
#
# Assen = robotmodel: x = rechts, y = rijrichting van de robot (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong = midden van de robot (wielmiddens op (+-375, +-500)). Alle maten staan hier; nooit hardcoden.
# =====================================================================

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbot design/agbot_params.py", die map staat niet in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375             # align_width / 2
robot_axle_y = -500             # achteras
robot_axle_z = 215              # ground_to_axle
robot_tire_d = 430
robot_tire_w = 100
robot_beam = 40                 # kokerprofiel 40 x 40 x 2
robot_rear_beam_y = (-575.0, -425.0)    # hart onderste dwarsbalken achter: rear_outer, rear_inner
robot_lower_beam_z = (619.0, 659.0)     # onder- en bovenkant onderste balken (wereld)
robot_front_beam_y = 575.0              # voorste onderbalk (contragewicht)
robot_bracket_x = 375.0 - 114.0         # binnenkant top plate wielbeugel achter (x 261..489): hanger blijft er binnen
robot_grid = 50                 # gatenraster balken, M10 (gat 10.4) op x = +-125, +-175, ... +-475
m10_hole = 10.4
m16_hole = 17.0

# ---------------------------------------------------------------------
# Toolbar: koker 80 x 80 x 4 dwars achter de robot, gelast aan 2 hangers onder de achterste onderbalken
# ---------------------------------------------------------------------
tb = 80.0
tb_wall = 4.0
tb_x = (-650.0, 650.0)          # 1300 lang, zelfde lengte als de bovenste robotbalken
tb_y = (-855.0, -775.0)         # voorkant 60 mm achter de band (band achter tot y -715)
tb_z = (370.0, 450.0)           # hoog genoeg dat de kop in de hoogste stand (+60) onder de U-beugels blijft

# Hangers (2x): bovenplaat onder beide achterste onderbalken, 2 x M10 per balk door het gatenraster,
# twee lijven van 8 mm naar de toolbar. Tussen de lijven blijft x 163..237 vrij voor de moeren.
hanger_x = 200.0                # hart hanger (beide zijden)
hanger_bolt_dx = 25.0           # bouten op x = 175 en 225 (rastergaten)
hanger_top_t = 10.0
hanger_top_w = 100.0            # x 150..250: 11 mm vrij van de wielbeugel (x 261)
hanger_top_y = (-610.0, -390.0)
web_t = 6.0
web_dx = 42.0                   # hart lijf t.o.v. hart hanger: lijven op x 155..161 en 239..245
# lijf (y, z): onder de bovenplaat, schuin naar achteren omlaag, om de toolbar heen (boven + voorkant)
web_pts = ((-390.0, 609.0), (-610.0, 609.0), (tb_y[0], tb_z[1] + 30.0), (tb_y[0], tb_z[1]), (tb_y[1], tb_z[1]),
           (tb_y[1], tb_z[0]), (tb_y[1] + 30.0, tb_z[0]), (-390.0, 560.0))

# ---------------------------------------------------------------------
# Borstelunit (zelfde voor alle uitvoeringen)
# Klemplaat met 4 sleufgaten tegen de achterkant van de toolbar, 2 vierkante U-beugels M16 om de toolbar:
#   beugels los -> unit schuift opzij (tussenruimte) en op/neer (hoogte, slijtage borstel, transport).
# Stelbout M16 op een lip boven de toolbar draagt de unit tijdens het stellen.
# Kop: horizontale plaat (onder de borsteltilt) met 2 lippen; motor erop, borstel eronder.
# ---------------------------------------------------------------------
unit_t = 10.0
unit_w = 220.0                  # klemplaat en kopplaat, x = hart unit +-110
unit_top_z = 550.0              # bovenkant klemplaat (bij hoogte 0)
ub_d = 16.0                     # vierkante U-beugel M16 voor koker 80
ub_dx = 60.0                    # beugels op hart unit +-60
ub_leg_z = (tb_z[0] - ub_d / 2.0 - 0.5, tb_z[1] + ub_d / 2.0 + 0.5)   # 361.5 / 458.5
height_range = (-60.0, 60.0)    # sleufgaten: hoogte-instelling t.o.v. nominaal (+ = omhoog)
slot_w = 17.0
tab_y = (tb_y[0], tb_y[0] + 65.0)   # stellip boven de toolbar
tab_w = 60.0
tab_t = 10.0
jack_y = (tb_y[0] + tb_y[1]) / 2.0  # stelbout boven het hart van de toolbar

head_t = 10.0
head_y0 = tb_y[0]               # kopplaat begint aan de voorkant van de klemplaat (scharnierlijn van de tilt)
head_len = 360.0                # tot y -1215
gusset_t = 8.0
gusset_h = 150.0
gusset_len = 120.0
tilt_deg = 4.0                  # borstel helt naar voren (rijrichting -y): alleen de voorkant raakt de vloer

# hart borstel (en motor) op de kop: afstand tot de voorkant van de klemplaat. Eén gatenpatroon voor alle borstels.
# Bepaald door de Ø750 achter de band: >= 55 mm vrij bij een nieuwe borstel, >= 28 mm in de hoogste stand.
brush_pos = 255.0               # hart borstel y -1110

# ---------------------------------------------------------------------
# Aandrijving: 48 V DC motor 550 W (IEC 71 B14), direct van de robotaccu (48 V LiFePO4), op een
# wormwielkast NMRV063 i = 30 met uitgaande flens FA (Ø180, steek 150, 4 x M10) en insteekas Ø25.
# Wormas (motor) aan de verre kant van de borstelas (-y), motor naar buiten.
# Rechts en links dezelfde motor: de kast omgedraaid, de FA-flens aan de andere kant gezet.
# ---------------------------------------------------------------------
gm_center = 63.0                # hartafstand worm - wormwiel
gm_ratio = 30.0
motor_rpm_nom = 3000.0
motor_P = 550.0                 # W afgegeven
battery_v = 48.0                # robotaccu 48 V 50 Ah LiFePO4 (agbot comparison)
eta_worm = 0.72                 # NMRV i = 30
eta_motor = 0.80
fa_d = 180.0
fa_t = 12.0
fa_pcd = 150.0                  # 4 gaten op 0 / 90 graden (koppen vrij van de kast)
gb_body = 100.0                 # kast boven de flens: 100 x 100 (x, y)
gb_h = 130.0                    # hoogte kast; wormas op fa_t + gb_h / 2 boven de kopplaat
worm_d = 90.0
worm_len = 150.0
motor_flange_d = 105.0          # IEC 71 B14
motor_flange_t = 12.0
motor_d = 110.0
motor_len = 190.0
shaft_d = 25.0                  # insteekas met spie, onderaan M10 eindbout + sluitring

hub_flange_d = 160.0            # borstelnaaf (spie + eindbout), flens 4 x M10 op steek 120
hub_flange_t = 10.0
hub_boss_d = 60.0
hub_boss_h = 30.0
hub_gap = 12.0                  # onderkant kopplaat -> bovenkant naaf
hub_pcd = 120.0

# ---------------------------------------------------------------------
# Borstels: standaard schotelborstel (veegmachine), stalen plaat met bundels PP / staaldraad
# d = buitenmaat op de vloer, plate_d = plaat, h = haarlengte (hoogte), F_c = aandrukkracht (geschat)
# ---------------------------------------------------------------------
BRUSHES = {
    650: {"d": 650.0, "plate_d": 350.0, "h": 150.0, "F_c": 150.0, "rpm": 100.0},
    750: {"d": 750.0, "plate_d": 450.0, "h": 160.0, "F_c": 180.0, "rpm": 100.0},
    850: {"d": 850.0, "plate_d": 550.0, "h": 170.0, "F_c": 200.0, "rpm": 90.0},
}
brush_plate_t = 4.0
bristle_ring = (70.0, 55.0)     # breedte van de haarkrans onder / boven (holle kern)
bristle_tufts = 24              # bundelrijen rond de omtrek (getekend als sleuven van 5 mm)

# ---------------------------------------------------------------------
# Uitvoeringen. gap = ruimte tussen de borstels (rand tot rand) op de vloer.
#   breed leggen: borstels tegen elkaar (gap_spread 0: de haren lopen op het raakpunt dezelfde kant op), voorkant naar buiten;
#   wiers maken: borstels uit elkaar (gap_windrow), voorkant draait naar binnen, het materiaal komt in het midden.
# ---------------------------------------------------------------------
CONFIGS = {
    "double_650": {"brush": 650, "n": 2, "gap_spread": 0.0, "gap_windrow": 200.0},
    "double_750": {"brush": 750, "n": 2, "gap_spread": 0.0, "gap_windrow": 200.0},
    "single_850": {"brush": 850, "n": 1, "offset_x": 0.0},
}
DEFAULT_CONFIG = "double_750"
NOMINAL = "double_750"          # hoogte 0 van de unit hoort bij een nieuwe Ø750 borstel

# ---------------------------------------------------------------------
# Regelkast (2 motorregelaars 48 V / 30 A, omkeerbaar, zekering, noodstoprelais) op de achterste onderbalken
# ---------------------------------------------------------------------
box_x = (-110.0, 110.0)
box_y = (-590.0, -410.0)
box_h = 90.0
box_base_t = 3.0
box_base_x = (-140.0, 140.0)    # M8 door de rastergaten op x = +-125
box_base_y = (-600.0, -400.0)

# ---------------------------------------------------------------------
# Contragewicht (optioneel, zelfde 2 blokken als de voerschuifvijzel) op de voorste onderbalk
# ---------------------------------------------------------------------
ballast_x = (110.0, 270.0)
ballast_y = (500.0, 650.0)
ballast_h = 106.0               # 2 x ca. 20 kg

# ---------------------------------------------------------------------
# Werking (voor dbr_calc en de animatie)
# ---------------------------------------------------------------------
drive_speed = 0.5               # m/s rijsnelheid bij borstelen (1,8 km/h)
mu_bristle = 0.40               # haar (PP) op beton, nat/vuil
r_contact = 0.85                # effectieve straal van het contact (fractie van R): alleen de buitenrand raakt
mu_material = 0.5               # los materiaal (zaagsel, zand, voerresten, mest) op beton
layer_kg_m2 = 2.0               # materiaal op de vloer (geschat, zaagsel/zand/voerresten)
idle_torque = 1.5               # Nm wormkast, afdichting


def config(name=None):
    """Afgeleide maten van een uitvoering: borstel, motorpositie en hart(en) van de borstel(s)."""
    name = name or DEFAULT_CONFIG
    c = dict(CONFIGS[name])
    b = BRUSHES[c["brush"]]
    c["name"] = name
    c.update({"d": b["d"], "R": b["d"] / 2.0, "plate_d": b["plate_d"], "h": b["h"], "F_c": b["F_c"], "rpm": b["rpm"]})
    c["yc"] = head_y0 - brush_pos                               # hart borstel (wereld-y)
    return c


def centres_x(c, mode="spread", gap=None):
    """x-hart van de borstel(s). mode 'spread' of 'windrow' (alleen bij 2 borstels)."""
    if c["n"] == 1:
        return [c.get("offset_x", 0.0)]
    g = gap if gap is not None else c["gap_spread" if mode == "spread" else "gap_windrow"]
    xc = c["R"] + g / 2.0
    return [-xc, xc]


def brush_signs(c, mode):
    """Draairichting per borstel, +1 = linksom van boven gezien (robot rijdt naar -y, de voorkant is -y).
    Wiers: voorkant naar binnen (links linksom, rechts rechtsom); breed leggen: andersom.
    Enkele borstel: 'right' (of 'spread') gooit naar +x, 'left' naar -x."""
    if c["n"] == 1:
        return [1 if mode in ("right", "spread") else -1]
    s = 1 if mode == "windrow" else -1
    return [s, -s]


def stack(c):
    """Afstand bovenkant kopplaat -> onderkant haar (rechtop, langs de borstelas)."""
    return head_t + hub_gap + hub_boss_h + hub_flange_t + brush_plate_t + c["h"]


def head_top_z(c):
    """Hoogte (wereld) van de bovenkant kopplaat op de scharnierlijn y = head_y0, zodat het laagste punt van het haar
    (voorkant, -y) na de tilt precies op de vloer staat."""
    a = math.radians(tilt_deg)
    return stack(c) * math.cos(a) - (c["yc"] - c["R"] - head_y0) * math.sin(a)


def unit_height(c):
    """Stand van de unit in de sleufgaten (mm, + = omhoog) t.o.v. nominaal, voor een nieuwe borstel."""
    return head_top_z(c) - head_top_z(config(NOMINAL))


def floor_centre_y(c):
    """y (wereld) van het midden van de haarkrans op de vloer, na de tilt (voor het materiaalmodel)."""
    a = math.radians(tilt_deg)
    return head_y0 + (c["yc"] - head_y0) * math.cos(a) + stack(c) * math.sin(a)


HEAD_TOP_NOM = head_top_z(config(NOMINAL))          # ca. 270
UNIT_BOTTOM_NOM = HEAD_TOP_NOM                      # klemplaat staat op de kopplaat


def gm_out_rpm():
    return motor_rpm_nom / gm_ratio                  # 100
