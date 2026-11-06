import math
import os
import sys

# =====================================================================
# Liquid fertilizer applicator advanced V2 - parameters
# Ophanging (aanbouwbok, parallellogram, actuator met langgat, toolbar, veerpoten, zwenkarmen) als advanced.
# Nieuw per element: V-schijfpaar (twin-bemester), dubbel injectormes van precision applicator V3 (slepend 20
# graden, twee vloeistoffen) en het aandrukwiel van advanced erachter. De 10-sectie rollenpomp staat op de robot.
#
# Assen zoals het robotmodel: x = rechts, y = rijrichting (voor = +y), z = omhoog, grond = z 0, mm.
# Oorsprong werktuig: x = 0 midden, y = 0 hart van de achterste onderbalk van de robot
# (chassis_beam_1 "rear_outer"), z = 0 grond. Op de robot: wereld-y = y + robot_mount_y.
# Alle maten staan hier; nooit hardcoden in lfa2_parts.py / build_lfa2.py.
# =====================================================================
FOLDER = os.path.dirname(os.path.abspath(__file__))
LFA_ROOT = os.path.dirname(os.path.dirname(FOLDER))                     # liquid fertilizer applicator
PA_ROOT = os.path.join(LFA_ROOT, "precision_applicator")
KNIFE_FOLDERS = (os.path.join(PA_ROOT, "parts", "injector_knife"),
                 os.path.join(PA_ROOT, "parts", "injector_knife_double"))
PUMP_FOLDER = os.path.join(PA_ROOT, "roller_pump")


def setup_path():
    """Het (dubbele) mes komt uit precision_applicator/parts, de pomp uit precision_applicator/roller_pump (niet
    gekopieerd)."""
    for folder in (PUMP_FOLDER,) + KNIFE_FOLDERS:
        if folder in sys.path:
            sys.path.remove(folder)
        sys.path.insert(0, folder)


setup_path()

# ---------------------------------------------------------------------
# Robot-interface (overgenomen uit "agbot design/agbot_params.py")
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
# Rijen en werkbreedte
# ---------------------------------------------------------------------
row_spacing = 200
row_x = (-400.0, -200.0, 0.0, 200.0, 400.0)
work_width = row_spacing * len(row_x)       # 1000 mm

# ---------------------------------------------------------------------
# Gereedschapsbalk (toolbar) 60 x 60 x 4; 900 lang zodat alles binnen de robotbreedte (+-489) blijft.
# De werkbreedte is 5 x 200 = 1000 mm (elke rij bedient een strook van 200 mm).
# ---------------------------------------------------------------------
bar_size = 60
bar_wall = 4
bar_length = 900
bar_y = -395
bar_z = 400
bar_front = bar_y + bar_size / 2.0          # -365
bar_rear = bar_y - bar_size / 2.0           # -425
bar_top = bar_z + bar_size / 2.0            # 430
bar_bot = bar_z - bar_size / 2.0            # 370
bar_cap_t = 3

# ---------------------------------------------------------------------
# Aanbouwbok (headstock), vast aan de robotbalk, 2 stuks gespiegeld
# ---------------------------------------------------------------------
plate_t = 8
hs_x = 100                      # hart van de parallellogramstangen
hs_link_gap = 44                # binnenmaat tussen de wangen
hs_bolt_x = (125.0, 175.0)      # M10 door de robotbalk (gatenraster)
hs_top_x = (62.0, 200.0)
hs_top_y = (-28.0, 34.0)
hs_clamp_x = (100.0, 200.0)
hs_clamp_y = (-20.0, 34.0)
hs_back_y = (-28.0, -20.0)      # achterplaat tegen de achterkant van de balk
hs_z_bot = 375
hs_cheek_y_rear = -110
hs_cross_size = 40
hs_cross_y = 40                 # bovenste dwarsbuis boven de robotbalk; binnenwangen kragen daarvoor uit
hs_cross_z = 800                # draagt de langgatplaten van de actuator
hs_low_cross_size = 30
hs_low_cross_y = -43
hs_low_cross_z = 400
m10_d = 10.0
m10_af = 17
m10_k = 6.4
m10_m = 8.4

# ---------------------------------------------------------------------
# Parallellogram en hefinrichting
# ---------------------------------------------------------------------
pin_front_y = -80
pin_upper_z = 600
pin_lower_z = 420
link_length = 260
link_tube = 30                  # koker 30 x 30 x 3
link_wall = 3
link_boss_d = 32
pin_d = 16
pin_hole = 16.4
pin_rear_y = pin_front_y - link_length       # -340

rf_y = (bar_front, -318.0)      # achterframe-platen, gelast op de toolbar
rf_z = (375.0, 622.0)
rf_cross = 30                   # dwarsbuis tussen de achterframes (ophangpunt actuator)
rf_cross_y = -350
rf_cross_z = 480                # tussen de achterste pennen, boven de klemmen van element 3

lift_height = 140               # toolbar omhoog op de kopakker
unit_drop_deg = 8.0             # elementen zakken op hun aanslag (stelmoer) als de balk omhoog is

# Elektrische lineaire actuator: Linak LA36 (parts/actuator/linear-actuator-la36-data-sheet-eng.pdf).
# Zweefstand: de bovenste pen zit in een langgat (act_slot) langs de actuator-as. In het werk staat de
# actuator volledig uit en kan de balk vrij zweven; bij heffen trekt de actuator het langgat dicht.
# Vlakke ligging (ca. 35 graden): weinig slag per mm hefhoogte, zodat 140 mm heffen en ruim zweven
# samen binnen 150 mm slag passen. De LA36 is 60 mm langer dan de eerdere aanname (inbouwmaat 200 + slag
# i.p.v. 140 + slag): pen A ligt daarom verder van B langs de as (zelfde hoek, zelfde zweefbereik).
ACT_DATASHEET = os.path.join(os.path.dirname(os.path.dirname(LFA_ROOT)), "parts", "actuator",
                             "linear-actuator-la36-data-sheet-eng.pdf")
# 24 V-tabel van het datasheet (blz. 14): spoed -> (max last N, zelfrem N, overbrenging, snelheid onbelast /
# nominale last mm/s, stroom onbelast / nominale last A, eindspeling mm)
LA36_24V = {
    "20F": (1700, 2200, "F 1:18", 72.0, 52.0, 2.4, 10.3, 3.5),
    "16F": (2000, 2600, "F 1:18", 60.0, 43.0, 2.4, 10.3, 2.9),
    "12F": (2600, 3400, "F 1:18", 44.0, 32.0, 2.4, 10.4, 2.6),
    "16G": (3400, 4400, "G 1:31", 35.0, 25.0, 2.4, 10.3, 2.3),
    "12G": (4500, 5800, "G 1:31", 26.0, 19.0, 2.4, 10.2, 2.3),
}
act_variant = "12F"             # 12 mm spoed, F-tandwiel: 2600 N, 32 mm/s bij nominale last (keuze: RATIONALE 10)
act_voltage = 24
act_duty = 0.20                 # inschakelduur bij vollast, slag <= 600 (datasheet blz. 9: 4 min aan, 16 min uit)
act_mass_100 = 4.55             # kg bij slag 100, +0.24 kg per 50 mm (blz. 7, zonder kabel)
act_mass_per_50 = 0.24
# bestelcode (blz. 10-12): LA36, spindel 12, slag 150, geen veiligheidsmoer, geen terugmelding, standaard met
# eindschakelaars, 24 V met slipkoppeling, reinforced IP66, geen reed, kleur 6, achteroog 0 gr., massief stangoog,
# tandwiel F, rem, inbouwmaat 350, eindstandmelding N, losse aders, rechte kabel
act_order_code = "36 120 150 0 0 01 B 6 - 6 1 2 F 3 0350 N C S 0 0 0"

act_b = (-314.0, 470.0)         # (y, z) onderste pen (achteroog), aan het achterframe; 6 mm voor advanced zodat
                                # het achteroog (13 mm achter de pen) 3 mm vrij blijft van de dwarsbuis
# (y, z) onderkant langgat. Advanced: (5, 700) met de korte actuator. Voor de LA36 ligt A 60 mm verder van B en iets
# steiler, zodat (a) geheven de actuator 354 lang is (4 mm voor zijn eindstop), (b) de stang in de laagste
# zweefstand 3 mm boven de achterste robotbalk blijft en (c) het stangoog bovenin het langgat vrij blijft van de
# dwarsbuis (zoekrooster in RATIONALE 10). Zweven -70 ... +68 mm.
act_a = (52.0, 751.0)
act_stroke = 150
act_bid_base = 200              # inbouwmaat = 200 + slag (slag <= 300, massief achteroog en stangoog, blz. 21)
act_retracted = act_bid_base + act_stroke      # 350
act_extended = act_retracted + act_stroke     # 500: werkstand
act_slot = 85                   # langgat: balk zweeft ca. -70 / +68 mm rond de ontwerphoogte
act_pin_d = 12                  # pen in de ogen (oog Ø 12.2, blz. 23/26)
act_pin_hole = 12.4             # gat / langgat in de lipjes
act_eye_hole = 12.2
act_eye_clear = 1.0             # speling oog - lip per kant (datasheet: 0.5 ... 1.0)
# achteroog (back fixture, massief, 0 graden: gat evenwijdig aan de huisbreedte), blz. 26
act_back_c = 25.2               # breedte/diameter
act_back_d = 13.0               # hart gat - eind
act_back_f = 27.9               # lengte tot de zeskant
act_back_nut = (36.0, 10.0)     # zeskant: sleutelwijdte, dikte (geschat uit de tekening)
# stangoog (piston rod eye, massief), blz. 23
act_rod_eye_c = 27.8
act_rod_eye_d = 13.5
act_rod_eye_f = 29.0
# huis (reinforced housing, blz. 20): 148 hoog, as op 37 van de onderkant, 76 breed, 230 lang
act_house_h = 148.0
act_house_below = 37.0          # van de spindelas naar de vlakke kant
act_house_w = 76.0
act_house_len = 230.0
act_house_start = 24.0          # hart achteroog - achterkant huis (geschat uit de tekening)
act_gear_len = 62.0             # tandwielkast over de volle hoogte (geschat)
act_motor_d = 72.0              # motor parallel aan de spindel, bovenkant op act_house_h - act_house_below (geschat)
act_tube = 44.5                 # buitenbuis (aluminium profiel)
act_tube_end_gap = 20.0         # eind buitenbuis tot hart stangoog bij ingetrokken (geschat; min. 2 mm tot de lipjes)
act_rod_d = 26.0                # binnenbuis / zuigerstang (geschat; past tussen de langgatplaten)
act_motor_side = -1             # -1: motor boven de buis (+1 = eronder: raakt geheven de robotbalk)

# ---------------------------------------------------------------------
# Injectie-element (5x), lokale x = 0 is het hart van de rij
# ---------------------------------------------------------------------
u_clamp_w = 60
u_clamp_t = 8
u_clamp_z = (340.0, 460.0)
u_bolt_d = 12
u_bolt_af = 19
u_bolt_k = 7.5
u_bolt_m = 10.8
u_bolt_dx = 20
u_bolt_dz = 46                  # bouten op bar_z +- 46, boven en onder de koker

u_tongue_t = 10
u_pivot = (bar_y - 95.0, 270.0)          # (y, z) draaipunt arm
u_pin_d = 20
u_fork_t = 6
u_fork_in = 15.0                         # binnenkant vorkplaat (x): smal, de messen en bouten zitten tussen de schijven
u_lug_rel = (-140.0, 40.0)               # pen veerpoot t.o.v. draaipunt
u_anchor_rel = (-150.0, 220.0)           # gat in de veerplaat t.o.v. draaipunt
u_anchor_plate = (56.0, 50.0, 8.0)       # y, x, dikte

# ---------------------------------------------------------------------
# V-schijfpaar (twin-bemester): twee schijven die voor-onder bijna tegen elkaar lopen en naar achteren uit elkaar.
# Elke schijf staat schuin: toespoor (voorkant naar binnen) en camber (onderkant naar binnen, bovenkant naar buiten).
# Zo snijden ze voor in een smalle snede, en tillen ze daarachter de zode iets op en duwen hem opzij; in die open V
# zit het dubbele mes. Rechter schijf hier; de linker is het spiegelbeeld (x -> -x).
# Elke schijf op een eigen naaf en stompe as, aan een hangplaat buiten de schijf. De hangplaten hangen aan een
# dwarskoker boven de schijven, die aan de vorkplaten van de arm gelast is. Diepteringen buiten op elke schijf.
# ---------------------------------------------------------------------
disc_d = 325                             # als de precisie-applicator (Ø 325): met ring Ø 220 ca. 50 diep
disc_t = 3
disc_toe = 5.0                           # graden per schijf (samen 10): voorkant naar binnen
disc_camber = 8.0                        # graden per schijf: onderkant naar binnen, bovenkant naar buiten
disc_meet_gap = 2.0                      # kleinste afstand tussen de randen, voor-onder (snijden samen een snede)
band_d = 220
band_w = 15
band_r_in = 85
band_chamfer = (4.0, 5.0)                # afschuining buitenrand ring (axiaal, radiaal)
hub_d = 60
hub_w = (-8.0, 28.0)                     # naaf langs de schijfas (0 = midden schijf, + = naar buiten)
hub_flange_d = 90
axle_d = 25                              # stompe as
boss_d = 50                              # lagerbus/as-oog gelast in de hangplaat
boss_gap = 3.0                           # naaf -> bus (borgring/aanloopschijf)
hanger_in = 66.0                         # binnenkant hangplaat (x): buiten de diepteringen (bovenkant ring x 59)
hanger_t = 8.0
hanger_r = 24.0                          # halve breedte hangplaat
yoke_size = 40                           # dwarskoker 40 x 40 x 3 boven de schijven
yoke_wall = 3
yoke_gap = 13.0                          # bovenkant schijf -> onderkant koker
u_disc_dx = 240                          # horizontale afstand draaipunt -> schijfas
disc_y = u_pivot[0] - u_disc_dx          # -730


def _rz(a, v):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2])


def _ry(a, v):
    # zelfde teken als App.Rotation(Y, a): (x, z) -> (x cos + z sin, -x sin + z cos)
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c)


def disc_rot(v):
    """Richting v (schijfframe: x = as naar buiten, y = voor, z = boven) naar de rechter schijf."""
    return _rz(math.radians(disc_toe), _ry(math.radians(disc_camber), v))


def disc_axis():
    return disc_rot((1.0, 0.0, 0.0))


def _rim_x_min(r=None, w=0.0, n=720):
    """Kleinste x (t.o.v. het schijfmidden) van een cirkel met straal r op axiale afstand w (schijfframe)."""
    r = disc_d / 2.0 if r is None else r
    best = (1e9, 0.0)
    for k in range(n):
        t = 2.0 * math.pi * k / n
        x = disc_rot((w, r * math.cos(t), r * math.sin(t)))[0]
        if x < best[0]:
            best = (x, t)
    return best


DISC_CX = disc_meet_gap / 2.0 - _rim_x_min()[0]          # x van het midden van de rechter schijf (ca. 27.6)


def _band_lowest():
    """Laagste punt van de diepteringen t.o.v. het schijfmidden (z < 0) en waar (w, r) op het profiel."""
    a = disc_axis()
    sin_t = math.sqrt(1.0 - a[2] ** 2)
    ro = band_d / 2.0
    x0 = disc_t / 2.0
    x1 = x0 + band_w
    best = None
    for w, r in ((x0, ro), (x1 - band_chamfer[0], ro), (x1, ro - band_chamfer[1])):
        z = w * a[2] - r * sin_t
        if best is None or z < best[0]:
            best = (z, w, r)
    return best


disc_z = -_band_lowest()[0]              # hoogte schijfmidden: de ringen rollen op de grond (ca. 110.7)
DISC_C = (DISC_CX, disc_y, disc_z)       # midden rechter schijf
work_depth = disc_d / 2.0 * math.sqrt(1.0 - disc_axis()[2] ** 2) - disc_z      # ca. 50


def disc_point(w, r, t):
    """Punt van de rechter schijf: axiale afstand w, straal r, hoek t (0 = voor, + omhoog), werktuigcoordinaten."""
    p = disc_rot((w, r * math.cos(t), r * math.sin(t)))
    return (DISC_C[0] + p[0], DISC_C[1] + p[1], DISC_C[2] + p[2])


def meet_point():
    """Punt waar de twee schijven het dichtst bij elkaar zijn (rechter rand), en de diepte daar."""
    t = _rim_x_min()[1]
    p = disc_point(0.0, disc_d / 2.0, t)
    return p, -p[2]


def band_contact():
    """(punt op de as van de rechter schijf, effectieve straal) zodat 'punt.z - straal' het laagste punt van de ring
    is; voor de animatie (grondcontact van een schuin staande ring)."""
    z, w, r = _band_lowest()
    a = disc_axis()
    return (DISC_C[0] + w * a[0], DISC_C[1] + w * a[1], DISC_C[2] + w * a[2]), r * math.sqrt(1.0 - a[2] ** 2)


def disc_dist(p):
    """Afstand van punt p tot de rechter of linker schijf (dunne schijf, dikte disc_t), het kleinste van beide."""
    a = disc_axis()
    best = 1e9
    for sx in (1.0, -1.0):
        q = (sx * p[0] - DISC_C[0], p[1] - DISC_C[1], p[2] - DISC_C[2])
        h = q[0] * a[0] + q[1] * a[1] + q[2] * a[2]
        rad = math.sqrt(max(0.0, q[0] ** 2 + q[1] ** 2 + q[2] ** 2 - h * h))
        dh = max(0.0, abs(h) - disc_t / 2.0)
        dr = max(0.0, rad - disc_d / 2.0)
        best = min(best, math.hypot(dh, dr))
    return best


def disc_inner_x(y, z):
    """x van de binnenkant van de rechter schijf op hoogte (y, z), en of dat punt binnen de schijfomtrek valt."""
    a = disc_axis()
    h = -disc_t / 2.0
    x = DISC_C[0] + (h - (y - DISC_C[1]) * a[1] - (z - DISC_C[2]) * a[2]) / a[0]
    q = (x - DISC_C[0], y - DISC_C[1], z - DISC_C[2])
    rad = math.sqrt(max(0.0, sum(c * c for c in q) - h * h))
    return x, rad <= disc_d / 2.0


def disc_top_z():
    """Hoogste punt van de schijven (z)."""
    return DISC_C[2] + disc_d / 2.0 * math.sqrt(1.0 - disc_axis()[2] ** 2)


yoke_c = (disc_y, disc_top_z() + yoke_gap + yoke_size / 2.0)    # (y, z) hart dwarskoker

# ---------------------------------------------------------------------
# Dubbel injectormes (precision_applicator/parts/injector_knife_double): 370 x 50 x 10, twee buisjes Ø 10 achter
# elkaar langs de rugkant (A voor, B erachter), voor twee vloeistoffen. Slepend 20 graden (punt naar achteren) zoals
# precision applicator V3: het glijdt over stenen en wortels en drukt de grond omlaag. De uitlaat van buisje A ligt
# 50 diep. Het mes staat in het midden tussen de schijven, zo ver naar voren als kan: knife_gap van beide schijven.
# Twee M10-bouten door de langgaten en de vorkplaten (afstandsbussen ertussen), zoals advanced.
# ---------------------------------------------------------------------
import ikd_params as K                    # noqa: E402  (setup_path hierboven)

knife_trail = 20.0                       # graden met de verticaal: punt achter, bovenkant voor (als V3)
outlet_depth = 50.0                      # hart uitlaat buisje A onder maaiveld (als V3)
knife_gap = 6.0                          # kleinste afstand mes/buisjes - schijven
knife_bolt_d = 10.0
knife_bolt_af = 17.0


def knife_axes():
    """Richtingen (y, z): d = lengte (bovenkant -> punt), n = breedte (rug -> snijkant)."""
    a = math.radians(knife_trail)
    return (-math.sin(a), -math.cos(a)), (math.cos(a), -math.sin(a))


def knife_world(origin, xl, yl):
    (dy, dz), (ny, nz) = knife_axes()
    return origin[0] + dy * xl + ny * yl, origin[1] + dz * xl + nz * yl


def _knife_samples():
    """Punten (xl, yl, straal) op blad en buisjes in mescoordinaten; straal = halve dikte (blad) of buisstraal."""
    pts = []
    corners = ((0.0, 0.0), (K.blade_l, 0.0), (K.blade_l_front, K.blade_w), (0.0, K.blade_w))
    for i in range(4):
        (x0, y0), (x1, y1) = corners[i], corners[(i + 1) % 4]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 5.0))
        pts += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n, K.blade_t / 2.0) for k in range(n)]
    for (xe, ye, xb, xo, yo) in ((K.tube_x_end, K.tube_y, K.tube_x_bend, K.tube_out_x, K.tube_out_y),
                                 (K.tube2_x_end, K.tube2_y, K.tube2_x_bend,
                                  K.tube2_x_bend - K.tube2_leg * math.cos(math.radians(K.tube2_angle)),
                                  K.tube2_y - K.tube2_leg * math.sin(math.radians(K.tube2_angle)))):
        for (xa, ya, xc, yc) in ((xe, ye, xb, ye), (xb, ye, xo, yo)):
            n = max(2, int(math.hypot(xc - xa, yc - ya) / 5.0))
            pts += [(xa + (xc - xa) * k / n, ya + (yc - ya) * k / n, K.tube_d / 2.0) for k in range(n + 1)]
    return pts


_KNIFE_PTS = _knife_samples()


def knife_clearance(origin):
    """Kleinste afstand van mes en buisjes tot de schijven (mm) voor mesoorsprong origin (y, z)."""
    best = 1e9
    for xl, yl, r in _KNIFE_PTS:
        y, z = knife_world(origin, xl, yl)
        for x in ((-r, r) if r == K.blade_t / 2.0 else (0.0,)):
            d = disc_dist((x, y, z)) - (0.0 if r == K.blade_t / 2.0 else r)
            best = min(best, d)
    return best


def _knife_origin():
    """(y, z) van de mesoorsprong: uitlaat A op outlet_depth, zo ver naar voren dat knife_gap overblijft."""
    def at(y):
        oz = knife_world((y, 0.0), K.tube_x_end, K.tube_y)[1]
        return y, -outlet_depth - oz
    lo, hi = disc_y - 600.0, disc_y + 100.0       # lo: ver achter de schijven (vrij), hi: erin
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if knife_clearance(at(mid)) > knife_gap:
            lo = mid
        else:
            hi = mid
    return at(lo)


KNIFE_ORIGIN = _knife_origin()


def knife_point(xl, yl):
    return knife_world(KNIFE_ORIGIN, xl, yl)


def knife_tip():
    return knife_point(K.blade_l, 0.0)


def knife_outlets():
    """(y, z) van de uitlaten van buisje A en B."""
    return knife_point(K.tube_x_end, K.tube_y), knife_point(K.tube2_x_end, K.tube2_y)


def knife_slots():
    """(y, z) van de twee langgaten (M10-bouten door de vorkplaten)."""
    return [knife_point(x, K.slot_y) for x in K.slot_x]


# veerpoot
rod_d = 12
spring_od = 35
spring_wire = 5
spring_free = 160
spring_rate = 4.0                        # N/mm: zachte veer verdeelt het balkgewicht over de elementen
eye_d = 28
eye_w = 20
seat_d = 40
seat_offset = 45                         # lagere veerschotel boven de pen
stop_gap = 20                            # stelmoer = onderaanslag (arm zakt unit_drop_deg)

# ---------------------------------------------------------------------
# Aandrukwiel per rij: drukt de sleuf achter het mes weer dicht
# Sleeparm (2 strippen, het wiel ertussen) draait op een oor van de vorkplaten, achter het buisje. Twee torsieveren
# op de as geven de aandrukkracht (3 gaten = 3 standen); een aanslagbout in een booggat begrenst de slag en draagt
# het vaste veerbeen. De arm hangt aan de element-arm, dus het wiel volgt de schijf en loopt precies op de sleuf.
# Het oor zit altijd aan de vorkplaten; press_wheel = False laat de set (arm, wiel, veren, bouten) weg.
# ---------------------------------------------------------------------
press_wheel = True
pw_pivot = (-985.0, 165.0)               # (y, z) draaipunt sleeparm (element-arm, 0 graden)
pw_wheel_rel = (-160.0, -40.0)           # wielas t.o.v. het draaipunt: wiel raakt de grond bij armhoek 0
pw_d = 250                               # half-massieve rubber band, smal: drukt de sleufranden tegen elkaar
pw_w = 40                                # binnen de vorkplaten (+-21,5): het wiel kan langs het oor draaien
pw_rim_d = 170
pw_hub_d = 40
pw_hub_half = 28.0                       # naaf tot tegen de strippen
pw_axle_d = 12                           # M12 as-bout
pw_strap_t = 6
pw_strap_in = 28.5                       # binnenkant strip (vorkplaat buitenkant 21, ring ertussen)
pw_strap_r = 18.0                        # halve breedte strip
pw_head_r = 48.0                         # kop van de strip rond het draaipunt (booggat, veergaten)
pw_pin_d = 16
pw_ear_r = 22.0                          # oor van de vorkplaat rond het draaipunt
pw_stop_rel = (0.0, -35.0)               # aanslagbout t.o.v. het draaipunt, vast in de vorkplaten
pw_stop_d = 10                           # M10 pasbout
pw_sleeve_d = 16                         # afstandsbus (tussen de vorkplaten en buiten de strip)
pw_up_deg = -30.0                        # sleeparm omhoog t.o.v. de element-arm (aanslag, ca. 80 mm)
pw_down_deg = 8.0                        # omlaag (aanslag, ca. 25 mm); geheven hangt de arm hierop
# torsieveren (2x, links en rechts op de as, buiten de strippen)
pw_spring_wire = 4.0                     # zacht en veel voorspanning: vlakke kracht over de slag, weinig
pw_spring_dm = 30.0                      # gemiddelde wikkeldiameter
pw_spring_coils = 8                      # terugwerking op de schijf (zie RATIONALE)
pw_spring_e = 206000.0                   # N/mm2 verenstaal
pw_spring_x0 = 40.0                      # binnenkant wikkeling (x); het bewegende veerbeen ligt ervoor
pw_peg_r = 35.0                          # gaten voor de veerpen in de strip, t.o.v. het draaipunt
pw_peg_angles = (120.0, 135.0, 150.0)    # graden (y-z vlak); verder rond = meer voorspanning
pw_preload_deg = (40.0, 55.0, 70.0)      # voorspanning bij armhoek 0 per gat (aanname: vrije beenhoek)
pw_preload_index = 1                     # standaard: middelste gat
# De kracht op het aandrukwiel werkt met een lange arm (ca. 655 mm) tegen de veerpoot van het element in. Zonder
# aanpassing zakt de balk dan tot het aandrukwiel loskomt. Daarom de veerschotel van de veerpoot hoger: in de
# zweefstand staat de element-arm weer op ca. 2,7 graden en het aandrukwiel midden in zijn slag (lfa2_calc.report()).
# Zonder loopwiel dragen de elementen ook de 150 N die het loopwiel droeg (advanced: 30 mm). V2: de arm met twee schijven,
# hangplaten en dwarskoker is zwaarder (13,2 i.p.v. 8,1 kg) en draagt zelf meer; 18 mm geeft weer ca. 2,7 graden.
press_seat_shift = 18.0
if press_wheel:
    seat_offset = seat_offset + press_seat_shift

pw_behind_knife = 75.0                   # draaipunt sleeparm achter het achterste punt van mes/buisjes

# Het oor van de sleeparm zit achter het mes (de buisjes en hun slangeinden): pw_pivot volgt uit de mesplaats.
pw_pivot = (round(min(knife_point(K.tube2_x_end, K.tube2_y)[0], knife_tip()[0]) - pw_behind_knife, 1), pw_pivot[1])

# ---------------------------------------------------------------------
# Rollenpomp op de robot (precision_applicator/roller_pump, 10 secties) met twee jerrycans, als combined_v3:
# rechter 5 secties vloeistof A (blauw) naar buisje A, linker 5 vloeistof B (oranje) naar buisje B. Een as, een
# stappenmotor: beide vloeistoffen volgen de rijsnelheid met dezelfde dosis per rij.
# Robotcoordinaten (rc); in werktuigcoordinaten is y = rc - robot_mount_y.
# De pomp staat 100 mm hoger dan in combined_v3 (op 4 blokken op de pompsteun): de bok van advanced heeft een
# dwarskoker (hs_cross_top, bovenkant z 820) net achter de uitlaten; de slangen moeten daar overheen.
# ---------------------------------------------------------------------
pump_channels = 10
pump_x = -42.5                           # rc, als combined_v3
pump_y_rc = -390.0                       # rc, hart pompas (combined: pump_y)
pump_riser = 100.0                       # blokken onder de onderstelbalken van de pomp
pump_z_rc = robot_upper_beam_z_top + 40.0 + pump_riser      # onderkant pomp: dwarskokers 40 + blokken
riser_size = (40.0, 60.0)                # blok x, y (tussen dwarskoker en onderstelbalk)
pump_ml_rev = 10.0                       # ml per omwenteling per kanaal (roller_pump: opgegeven)
pump_rpm_max = 60.0                      # roller_pump README: ca. 60 omw/min maximum
CHANNEL = {"A": (5, 6, 7, 8, 9), "B": (0, 1, 2, 3, 4)}
LIQUIDS = ("A", "B")
dose_l_ha = 500.0                        # per vloeistof (combined_v3: 500 l/ha bij 0,75 m/s = 45 omw/min)

# Slangen 8 x 12 van de pomp naar de buisjes, in twee lagen over de bok: B laag, A hoog (A0..A2 gaan naar links over
# de B-slangen, B3, B4 naar rechts onder de A-slangen). Binnen een laag schuiven alle slangen tegelijk schuin
# opzij: begin en eind liggen in dezelfde volgorde, dus ze komen nooit dichter bij elkaar dan 62 mm.
hose_od = 12.0
hose_exit_r = 40.0                       # boog uit de pompslang (schuin omlaag) tot horizontaal
layer_z = {"B": 836.0, "A": 862.0}       # hart slang; bovenkant dwarskoker van de bok z 820
climb_r = 30.0                           # A: na de boog in een S omhoog naar de hoge laag
lateral_y = (-70.0, -400.0)              # werktuig-y: begin en eind van het schuin opzij gaan (beide lagen);
                                         # eerder (-20) gaf een bocht R 13 vlak achter de S omhoog (A1)
lane_dx = {"A": -26.0, "B": 26.0}        # baan t.o.v. het hart van de rij: naast veerpoot en moer (x +-11)
drop_y = {"A": -560.0, "B": -600.0}      # werktuig-y waar de slang uit de laag naar het element zakt
over_unit_z = {"A": 560.0, "B": 520.0}   # boven het element (veerpoot, ankerplaat z ~500) naar achteren
knife_hose_over = {"A": (-700.0, 420.0), "B": (-720.0, 420.0)}   # (y boven de veerpoot, z boven het slangeinde)
end_lead = 40.0                          # recht stuk op het buisje
