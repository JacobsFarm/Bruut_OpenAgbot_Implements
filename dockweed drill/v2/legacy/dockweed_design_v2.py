# -*- coding: utf-8 -*-
"""
Ridderzuringfrees ("vermorzelaar") voor de AgBot / OpenAgbot "Bruut": elektrisch, plant voor plant.

Principe (nagebouwd op Robot Ruud van WUR en Joost Samsom):
  * Een portaal aan de kop van de robot met een X-as (links-rechts, slag 1000 mm) en een Z-as
    (op-neer, slag 480 mm). De robot zelf is de Y-as: hij stopt met de plant onder het portaal.
  * Het portaal komt aan de kant van de AANGEDREVEN as (hubmotoren); de robot rijdt tijdens het
    wieden met die kant vooruit. Met ~90 kg aan de gestuurde kant houden de hubmotorwielen te
    weinig grip (zie rekenwerk). De accu gaat bij voorkeur naar de verre (gestuurde) kant.
  * Een snellopende vermorzelfrees Ø180 (werkt als een "staafmixer", 1500 rpm) gaat de plant in tot
    150 mm diep (max. 200 mm) en maalt de wortelkop en de bovenste penwortel fijn. Hoog toerental en
    langzaam insteken geven plakjes van tienden van een mm, en die kunnen niet meer uitlopen.
  * Een pot Ø250 hangt los op 2 stangen om de frees. Hij zakt mee, landt op de zode en houdt de grond
    op zijn plek, zodat er geen grond of stenen worden weggeslingerd. Een sensor op de stang meldt
    "pot op de grond". Dat is de maaiveldreferentie, net als een taster (probe) op een CNC-machine.
  * Wisselgereedschap 2 is een maaischijf met 3 scharnierende mesjes om de plant bovengronds
    (of net boven de grond) af te maaien. Zelfde spil, 4 bouten M10.
  * Spil: BLDC-motor 48 V 1,5 kW 3000 rpm (dezelfde motor als bij de geulfrees, maar zonder kast).
    Direct aangedreven via een klauwkoppeling op een as Ø35 in 2x UCF207. Toerental en stroomgrens
    regelt een VESC (CAN).
  * X (V2): 2 aftakasbuizen (citroenprofiel, binnenbuis 49x39,5x4,5) als geleiding. Over elke buis schuift een
    stuk buitenbuis (57,5x48x4) als huls, aan de achterkant ingezaagd zodat de steunribben erdoor kunnen.
    3 hulzen: 2 op de bovenbuis, 1 op de onderbuis (sleufgaten, dus niet overbepaald). Tandriem HTD-5M en
    NEMA 23 closed-loop met 5:1-kast zoals in V1.
  * Z: Z-slede van koker 120x60x3 met HGR15-rails. Kogelomloopspindel SFU1610 en een NEMA 23
    closed-loop met rem.
  * Bevestiging: 2 draagarmen met kruisklemmen op 2 dwarsbalken van de robot. Niets boren of lassen.

Uitvoeren in FreeCAD (Python-console):
    exec(open(r"F:/veldrobot/aanbouwdelen/dockweed drill/V2/dockweed_design_v2.py", encoding="utf-8").read())
Daarna eventueel:  maak_renders()

Assen: X = breedte (0 = midden robot, + = rechts in rijrichting), Y = rijrichting tijdens het wieden
(+Y = vooruit = portaalkant, kopse kant robotframe op Y = 0), Z = omhoog (0 = maaiveld). Maten in mm.
"""
import math
import os
import FreeCAD as App
import Part

V = App.Vector
OMHOOG = V(0, 0, 1)
MAP = r"F:/veldrobot/aanbouwdelen/dockweed drill/V2/"

P = dict(
    # ---- stand van de machine in het model
    x_slede=150.0,          # X van het spilhart (0 = midden robot), bereik -500..+500
    z_frees=-150.0,         # onderkant freestanden t.o.v. maaiveld: -150 = 150 mm diep, +280 = rijstand
    gereedschap="frees",    # "frees" (vermorzelen) of "maai" (bovengronds maaien / kort frezen)
    # ---- AgBot (AANNAME uit OpenAgbot parameters.scad: koker 40x40x2, raster 50 mm) -> opmeten!
    rb_b=40.0,              # kokermaat chassis
    rb_langs_x=375.0,       # hart langsbalken (chassis_width 750)
    rb_langs_z=564.0,       # onderkant langsbalk (= bovenkant wielbeugel: 215 + 345 + 4)
    rb_dwars_y=(-20.0, -470.0),  # hart van de 2 dwarsbalken waarop de draagarmen klemmen
    rb_as_portaal_y=-150.0,  # as aan de portaalkant = AANGEDREVEN as (hubmotoren, 4.00-8)
    rb_as_ver_y=-850.0,     # as aan de andere kant = GESTUURDE as (NEMA34)
    robot_massa=150.0,      # aanname: robot incl. accu [kg]
    robot_zw_y=-500.0,      # aanname: zwaartepunt robot (Y), midden tussen de assen
    robot_zw_y_accu=-650.0,  # zwaartepunt als de accu naar de verre kant gaat
    # ---- portaal
    arm_x=340.0,            # hart draagarm + staander (V2: verder naar buiten = kortere uitkraging van de buizen)
    staander_y=60.0,        # achterkant staander (voorkant robotframe = 0)
    xbalk_L=1400.0,         # V2: lengte aftakasbuizen X (1500 kopen, op maat zagen)
    xbalk_z=(760.0, 1060.0),  # hart onderste / bovenste X-buis
    x_slag=1000.0,
    # ---- V2: aftakas-geleiding (citroenprofiel). Maten Sparex 1B (binnen) / 2A (buiten): CONTROLEER aan het echte stuk
    pto_b=49.0, pto_h=39.5, pto_t=4.5,        # binnenbuis: lengte (Z), dikte (Y), wand
    huls_b=57.5, huls_h=48.0, huls_t=4.0,     # buitenbuis (huls)
    huls_L=100.0, huls_afstand=220.0, huls_onder_L=140.0, sleuf=14.0,
    # ---- frees / spil / pot
    frees_D=180.0,          # gatdiameter (Joost: ~18 cm, MEV-Ampferfräse: 180 mm)
    diepte=150.0,           # standaard freesdiepte (Ruud: 15 cm)
    diepte_max=200.0,
    rijstand=280.0,         # onderkant frees boven maaiveld tijdens rijden
    pot_D=250.0, pot_h=150.0, pot_t=2.0,
    pot_rand=30.0,          # potrand hangt in rust zoveel onder de freesonderkant
    as_d=35.0,
    # ---- aandrijving
    motor_P=1500.0, motor_rpm=3000.0, motor_piek=2.0,
    frees_rpm=1500.0, maai_rpm=3000.0,
    stap_T=3.0,             # NEMA 23 closed-loop [Nm]
    x_kast=5.0, x_poelie_T=20, htd_steek=5.0,
    z_spoed=10.0,           # SFU1610
    insteek=25.0,           # insteeksnelheid [mm/s]
    ijl_x=200.0, ijl_z=100.0,
    # ---- omgeving (alleen voor de plaatjes)
    plant_x=-300.0, plant_y=1000.0,
)
Q = dict(P)

STAAL = (0.25, 0.27, 0.30)
GALV = (0.62, 0.66, 0.68)
ALU = (0.80, 0.82, 0.85)
ZILVER = (0.72, 0.74, 0.77)
RVS = (0.83, 0.85, 0.87)
HARDOX = (0.95, 0.72, 0.08)
ORANJE = (0.90, 0.40, 0.06)
ZWART = (0.08, 0.08, 0.09)
BLAUW = (0.10, 0.25, 0.55)
GRIJS = (0.55, 0.57, 0.60)
RUBBER = (0.13, 0.13, 0.13)
PE = (0.94, 0.94, 0.88)
ROOD = (0.80, 0.12, 0.10)
GROEN = (0.45, 0.66, 0.32)
BLAD = (0.18, 0.45, 0.12)
BRUIN = (0.45, 0.30, 0.20)
GROND = (0.42, 0.29, 0.16)
LED = (0.98, 0.92, 0.55)

DICHTHEID = dict(staal=7.85e-6, galv=7.85e-6, hardox=7.85e-6, rvs=7.9e-6, alu=2.70e-6,
                 rubber=1.2e-6, pe=0.95e-6, koop=7.85e-6)
# koopdelen met catalogusmassa [kg] (vereenvoudigd gemodelleerd, dus niet via volume)
KOOP_KG = {"Spilmotor": 6.5, "NEMA23_X": 1.6, "Planetaire_kast": 0.9, "NEMA23_Z": 2.0,
           "E_kast": 3.0, "Camera_industrieel": 0.4, "LED_lamp": 0.6, "Kabelrups": 0.4,
           "Klauwkoppeling": 0.9, "UCF207": 1.6, "Kogelomloopmoer": 0.4, "Moerhuis": 0.3,
           "BK12": 0.6, "BF12": 0.4}
# profielen en rails: catalogusmassa per meter
KG_PER_M = {"Alu_profiel_40x80": 2.8, "HGR15_rail": 1.45}


# ------------------------------------------------------------------ hulpfuncties
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def koker(x0, x1, y0, y1, z0, z1, t, as_):
    o = box(x0, x1, y0, y1, z0, z1)
    if as_ == "x":
        i = box(x0 - 1, x1 + 1, y0 + t, y1 - t, z0 + t, z1 - t)
    elif as_ == "y":
        i = box(x0 + t, x1 - t, y0 - 1, y1 + 1, z0 + t, z1 - t)
    else:
        i = box(x0 + t, x1 - t, y0 + t, y1 - t, z0 - 1, z1 + 1)
    return o.cut(i)


def cyl(r, p, d, L):
    return Part.makeCylinder(r, L, p, d)


def buis(ro, ri, p, d, L):
    d = V(d)
    d.normalize()
    return cyl(ro, p, d, L).cut(cyl(ri, p - d * 1.0, d, L + 2.0))


def plaats(sh, p, d):
    """Vorm die langs +Z vanaf de oorsprong is gemaakt op punt p in richting d zetten."""
    sh = sh.copy()
    sh.transformShape(App.Placement(p, App.Rotation(V(0, 0, 1), d)).toMatrix())
    return sh


def koker_tussen(p1, p2, b, t):
    d = p2 - p1
    L = d.Length
    s = box(-b / 2, b / 2, -b / 2, b / 2, 0, L).cut(box(-b / 2 + t, b / 2 - t, -b / 2 + t, b / 2 - t, -1, L + 1))
    return plaats(s, p1, d)


def gaten_z(sh, pts, r, z0, h):
    for (px, py) in pts:
        sh = sh.cut(cyl(r, V(px, py, z0 - 1), OMHOOG, h + 2))
    return sh


def zwaartepunt(sh):
    vol, m = 0.0, V(0, 0, 0)
    for s in sh.Solids:
        vol += s.Volume
        m = m + s.CenterOfMass * s.Volume
    return m * (1.0 / vol) if vol > 0 else sh.BoundBox.Center


def alu_40x80_x(x0, x1, y0, z0):
    """Alu-constructieprofiel 40x80 met sleuf 8, lengte langs X, 80 diep (Y) en 40 hoog (Z)."""
    p = box(x0, x1, y0, y0 + 80, z0, z0 + 40)
    sw, sd = 8.2, 9.0
    zc = z0 + 20
    p = p.cut(box(x0 - 1, x1 + 1, y0 - 1, y0 + sd, zc - sw / 2, zc + sw / 2))
    p = p.cut(box(x0 - 1, x1 + 1, y0 + 80 - sd, y0 + 81, zc - sw / 2, zc + sw / 2))
    for yc in (y0 + 20, y0 + 60):
        p = p.cut(box(x0 - 1, x1 + 1, yc - sw / 2, yc + sw / 2, z0 - 1, z0 + sd))
        p = p.cut(box(x0 - 1, x1 + 1, yc - sw / 2, yc + sw / 2, z0 + 40 - sd, z0 + 41))
        p = p.cut(box(x0 - 1, x1 + 1, yc - 10, yc + 10, zc - 10, zc + 10))      # holle kamer
        p = p.fuse(buis(7, 3.4, V(x0, yc, zc), V(1, 0, 0), x1 - x0))           # kernboring
    return p.removeSplitter()


def citroen_x(x0, x1, yc, zc, b, h):
    """Massief citroenprofiel langs X: b = lengte in Z (tip tot tip), h = dikte in Y. Twee cirkelbogen."""
    R = (b * b / 4 + h * h / 4) / h
    d = R - h / 2
    c1 = Part.makeCylinder(R, x1 - x0, V(x0, yc + d, zc), V(1, 0, 0))
    c2 = Part.makeCylinder(R, x1 - x0, V(x0, yc - d, zc), V(1, 0, 0))
    return c1.common(c2)


def citroen_buis(x0, x1, yc, zc, b, h, t):
    """Holle citroenbuis (aftakas-profiel) met buitenmaat b x h en wand t."""
    return citroen_x(x0, x1, yc, zc, b, h).cut(citroen_x(x0 - 1, x1 + 1, yc, zc, b - 2 * t, h - 2 * t))


def citroen_ring(x0, x1, yc, zc, bo, ho, bi, hi):
    return citroen_x(x0, x1, yc, zc, bo, ho).cut(citroen_x(x0 - 1, x1 + 1, yc, zc, bi, hi))


def doorsnede_I():
    """Oppervlaktetraagheidsmomenten van de binnenbuis [mm4]: (om Y-as = buiging in Z, om Z-as = buiging in Y), vlak A [mm2]."""
    q = Q
    fo = Part.Face(Part.Wire(citroen_x(0, 10, 0, 0, q["pto_b"], q["pto_h"]).slice(V(1, 0, 0), 5)[0]))
    fi = Part.Face(Part.Wire(citroen_x(0, 10, 0, 0, q["pto_b"] - 2 * q["pto_t"], q["pto_h"] - 2 * q["pto_t"]).slice(V(1, 0, 0), 5)[0]))
    r = fo.cut(fi)
    m = r.MatrixOfInertia
    return m.A22, m.A33, r.Area


def hgr15_rail_x(x0, x1, yf, zc):
    """HGR15-rail langs X op vlak y=yf, steekt uit naar +Y."""
    r = box(x0, x1, yf, yf + 15, zc - 7.5, zc + 7.5)
    r = r.cut(box(x0 - 1, x1 + 1, yf + 8, yf + 11, zc - 8.5, zc - 5.0))
    return r.cut(box(x0 - 1, x1 + 1, yf + 8, yf + 11, zc + 5.0, zc + 8.5))


def hgh15_blok_x(xc, yf, zc):
    """HGH15CA-wagen op een X-rail (railvoet op y=yf); bovenvlak op yf+28."""
    b = box(xc - 30.7, xc + 30.7, yf + 4.3, yf + 28, zc - 17, zc + 17)
    return b.cut(box(xc - 31, xc + 31, yf + 4.0, yf + 15.3, zc - 7.8, zc + 7.8))


def hgr15_rail_z(z0, z1, yf, xc):
    """HGR15-rail langs Z, railvoet op y=yf, steekt uit naar -Y."""
    r = box(xc - 7.5, xc + 7.5, yf - 15, yf, z0, z1)
    r = r.cut(box(xc - 8.5, xc - 5.0, yf - 11, yf - 8, z0 - 1, z1 + 1))
    return r.cut(box(xc + 5.0, xc + 8.5, yf - 11, yf - 8, z0 - 1, z1 + 1))


def hgh15_blok_z(zc, yf, xc):
    """HGH15CA-wagen op een Z-rail (railvoet op y=yf); bovenvlak op yf-28."""
    b = box(xc - 17, xc + 17, yf - 28, yf - 4.3, zc - 30.7, zc + 30.7)
    return b.cut(box(xc - 7.8, xc + 7.8, yf - 15.3, yf - 4.0, zc - 31, zc + 31))


def ucf207(x, y, zf):
    """UCF207 vierkant flenslager (as 35): flens op z=zf, huis naar boven."""
    A, J, tf = 117.0, 92.0, 14.0
    fl = box(x - A / 2, x + A / 2, y - A / 2, y + A / 2, zf, zf + tf)
    fl = fl.common(cyl(A * 0.64, V(x, y, zf - 1), OMHOOG, tf + 2))
    h = fl.fuse(cyl(42, V(x, y, zf + tf), OMHOOG, 20)).fuse(cyl(27, V(x, y, zf + tf + 20), OMHOOG, 9)).removeSplitter()
    for dx in (-J / 2, J / 2):
        for dy in (-J / 2, J / 2):
            h = h.cut(cyl(7, V(x + dx, y + dy, zf - 1), OMHOOG, tf + 2))
    return h.cut(cyl(Q["as_d"] / 2 + 0.3, V(x, y, zf - 1), OMHOOG, tf + 32))


def kruis(L, b, t, gat=0.0):
    k = box(-L / 2, L / 2, -b / 2, b / 2, 0, t).fuse(box(-b / 2, b / 2, -L / 2, L / 2, 0, t))
    k = k.fuse(cyl(b * 1.25, V(0, 0, 0), OMHOOG, t)).removeSplitter()
    if gat > 0:
        k = k.cut(cyl(gat, V(0, 0, -1), OMHOOG, t + 2))
    # snijkant: afschuining op de voorlopende onderkant van elke arm (draairichting linksom van boven)
    for k_ in range(4):
        pts = [V(22, b / 2 + 0.01, -0.01), V(22, b / 2 - 9, -0.01), V(22, b / 2 + 0.01, t * 0.55)]
        wig = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(L / 2 - 20, 0, 0))
        wig.rotate(V(0, 0, 0), OMHOOG, 90 * k_)
        k = k.cut(wig)
    return k


def flens_gaten(sh, x, y, z0, t):
    """Steekcirkel Ø80 met 4x M10 (gereedschapswissel) + centreergat."""
    for k_ in range(4):
        a = math.radians(45 + 90 * k_)
        sh = sh.cut(cyl(5.5, V(x + 40 * math.cos(a), y + 40 * math.sin(a), z0 - 1), OMHOOG, t + 2))
    return sh


def vermorzelfrees(x, y, zc):
    """Gereedschap 1: kruisfrees Ø180 van Hardox, 2 niveaus, 4 tanden en een centreerpunt.
    zc = onderkant tanden. Bovenkant flens op zc+100 (tegen de spilflens)."""
    R = Q["frees_D"] / 2
    d = []
    ko = kruis(2 * (R - 8), 30, 10)
    ko.translate(V(x, y, zc + 25))
    d.append(("Frees_kruis_onder_Hardox_10mm", ko, HARDOX, "hardox"))
    for k_ in range(4):
        t = box(R - 18, R, 5, 15, 0, 26)          # tand 10 mm aan de voorlopende kant van de arm
        t.rotate(V(0, 0, 0), OMHOOG, 90 * k_)
        t.translate(V(x, y, zc))
        d.append(("Frees_tand_Hardox_10mm", t, HARDOX, "hardox"))
    kb = kruis(2 * (R - 5), 28, 10, gat=24.4)
    kb.rotate(V(0, 0, 0), OMHOOG, 45)
    kb.translate(V(x, y, zc + 60))
    d.append(("Frees_kruis_boven_Hardox_10mm", kb, HARDOX, "hardox"))
    d.append(("Frees_kernbuis_48x5", buis(24.15, 19.15, V(x, y, zc + 35), OMHOOG, 55), STAAL, "staal"))
    fl = flens_gaten(cyl(55, V(x, y, zc + 90), OMHOOG, 10), x, y, zc + 90, 10)
    d.append(("Frees_flens_10mm", fl, STAAL, "staal"))
    d.append(("Frees_centreerpunt", Part.makeCone(1.0, 12.0, 60, V(x, y, zc - 35), OMHOOG), ZILVER, "staal"))
    return d


def maaischijf(x, y, zb):
    """Gereedschap 2: maaischijf Ø200 met 3 scharnierende mesjes (robotmaaiermes), tipcirkel Ø230.
    zb = onderkant mesjes. Bovenkant flens op zb+100."""
    d = []
    s = cyl(100, V(x, y, zb + 4), OMHOOG, 4)
    for k_ in range(3):
        a = math.radians(60 + 120 * k_)
        s = s.cut(cyl(22, V(x + 55 * math.cos(a), y + 55 * math.sin(a), zb + 3), OMHOOG, 6))
    d.append(("Maaischijf_4mm", s, ZILVER, "staal"))
    d.append(("Maaischijf_kernbuis_48x5", buis(24.15, 19.15, V(x, y, zb + 8), OMHOOG, 82), STAAL, "staal"))
    fl = flens_gaten(cyl(55, V(x, y, zb + 90), OMHOOG, 10), x, y, zb + 90, 10)
    d.append(("Maaischijf_flens_10mm", fl, STAAL, "staal"))
    for k_ in range(3):
        m = box(80, 115, -9, 9, 0, 1.0)
        m.rotate(V(80, 0, 0), OMHOOG, -15)
        m = m.fuse(cyl(4, V(85, 0, -3), OMHOOG, 15))
        m.rotate(V(0, 0, 0), OMHOOG, 120 * k_)
        m.translate(V(x, y, zb))
        d.append(("Maaimesje_scharnierend", m, ZILVER, "staal"))
    return d


def blad(lengte, breedte, dikte):
    e = Part.Ellipse(V(0, 0, 0), lengte / 2, breedte / 2)
    s = Part.Face(Part.Wire(e.toShape())).extrude(V(0, 0, dikte))
    s.translate(V(lengte / 2, 0, 0))
    return s


# ------------------------------------------------------------------ ontwerp
def build(doc_name="Ridderzuringfrees_V2", **kw):
    global Q
    Q = dict(P)
    Q.update(kw)
    if doc_name in App.listDocuments():
        App.closeDocument(doc_name)
    doc = App.newDocument(doc_name)

    delen = []          # (naam, shape, kleur, transparantie, groep, materiaal)

    def add(naam, sh, kleur, groep, mat="staal", transp=0):
        delen.append((naam, sh, kleur, transp, groep, mat))

    x = Q["x_slede"]
    zc = Q["z_frees"]
    L = Q["xbalk_L"]
    zb_lo, zb_hi = Q["xbalk_z"]

    # --- Y-opbouw (van achter naar voor)
    y_st0 = Q["staander_y"]
    y_st1 = y_st0 + 50                 # staander 50x50
    yt = y_st1 + 45.0                  # V2: hart aftakasbuizen (steunplaat 8 + rib 19 + halve buisdikte)
    y_pr0, y_pr1 = y_st1, yt + 4       # y_pr1 = referentie voor riem en X-slede
    y_sl0 = yt + 32                    # huls voorkant (yt + 24) + opzetplaat 8 mm
    y_sl1 = y_sl0 + 10                 # X-slede 10 mm alu
    y_zr = y_sl1 + 28                  # railvoet Z-rails (= bovenkant riser)
    y_zs0, y_zs1 = y_zr + 23, y_zr + 83   # Z-slede koker 120x60
    y_ks = y_zs0 - 25                  # hart kogelomloopspindel
    y_sp0, y_sp1 = y_zs1, y_zs1 + 6    # achterplaat spilbok 6 mm
    ys = y_sp1 + 75                    # hart spil

    # ================================================================ referentie robot (AANNAME)
    rb = Q["rb_b"]
    zl0 = Q["rb_langs_z"]
    zl1 = zl0 + rb
    zd1 = zl1 + rb
    xl = Q["rb_langs_x"]
    for s in (-1, 1):
        add("Robot_langsbalk_REF", koker(s * xl - rb / 2, s * xl + rb / 2, -1000, 0, zl0, zl1, 2, "y"), BRUIN, "Referentie_robot", "ref", 55)
    for yd in (Q["rb_dwars_y"][0], Q["rb_dwars_y"][1], -980.0):
        add("Robot_dwarsbalk_REF", koker(-650, 650, yd - rb / 2, yd + rb / 2, zl1, zd1, 2, "x"), BRUIN, "Referentie_robot", "ref", 55)
    for s in (-1, 1):
        for yw, D, stuur in ((Q["rb_as_portaal_y"], 400.0, False), (Q["rb_as_ver_y"], 430.0, True)):
            nm_w = "Robot_wiel_stuur_REF" if stuur else "Robot_wiel_hubmotor_REF"
            add(nm_w, cyl(D / 2, V(s * xl - 50, yw, D / 2), V(1, 0, 0), 100), ZWART, "Referentie_robot", "ref", 55)
            if not stuur:
                add("Robot_hubmotor_REF", cyl(80, V(s * xl - 70, yw, D / 2), V(1, 0, 0), 140), GRIJS, "Referentie_robot", "ref", 55)
            for dxp in (-74, 70):
                add("Robot_wielbeugel_REF", box(s * xl + dxp, s * xl + dxp + 4, yw - 120, yw + 120, D / 2 - 40, zl0), BRUIN, "Referentie_robot", "ref", 65)
            add("Robot_wielbeugel_REF", box(s * xl - 74, s * xl + 74, yw - 120, yw + 120, zl0 - 4, zl0), BRUIN, "Referentie_robot", "ref", 65)
            if stuur:
                add("Robot_stuurmotor_NEMA34_REF", box(s * xl - 43, s * xl + 43, yw - 43, yw + 43, zd1 + 10, zd1 + 280), ZWART, "Referentie_robot", "ref", 55)

    # ================================================================ bok (vast op de robot)
    xa = Q["arm_x"]
    for s, nm in ((-1, "L"), (1, "R")):
        xb = s * xa
        add("Bok_draagarm_40x40x3_" + nm, koker(xb - 20, xb + 20, -540, y_st1, zd1, zd1 + 40, 3, "y"), STAAL, "Bok")
        add("Bok_staander_50x50x3_" + nm, koker(xb - 25, xb + 25, y_st0, y_st1, zd1 + 40, 1110, 3, "z"), STAAL, "Bok")
        add("Bok_kopplaatje_6mm_" + nm, box(xb - 25, xb + 25, y_st0, y_st1, 1110, 1116), STAAL, "Bok")
        add("Bok_schoor_25x25x2_" + nm, koker_tussen(V(xb, y_st0 - 12.5, 1030), V(xb, -360, zd1 + 52), 25, 2), STAAL, "Bok")
        for yd in Q["rb_dwars_y"]:
            pts = [(xb + dx, yd + dy) for dx in (-32, 32) for dy in (-32, 32)]
            pb = gaten_z(box(xb - 45, xb + 45, yd - 45, yd + 45, zd1 + 40, zd1 + 45), pts, 5.5, zd1 + 40, 5)
            po = gaten_z(box(xb - 45, xb + 45, yd - 45, yd + 45, zl1 - 5, zl1), pts, 5.5, zl1 - 5, 5)
            add("Kruisklem_plaat_5mm", pb, GALV, "Bok", "galv")
            add("Kruisklem_plaat_5mm", po, GALV, "Bok", "galv")
            for (px, py) in pts:
                bt = cyl(5, V(px, py, zl1 - 13), OMHOOG, (zd1 + 53) - (zl1 - 13))
                bt = bt.fuse(cyl(9.2, V(px, py, zd1 + 45), OMHOOG, 8)).fuse(cyl(9.2, V(px, py, zl1 - 13), OMHOOG, 8))
                add("Bout_M10x100_kruisklem", bt, ZILVER, "Bok")

    # ================================================================ X-as (V2: aftakasbuizen + hulzen)
    Lb = Q["xbalk_L"]
    pb, ph, pt_ = Q["pto_b"], Q["pto_h"], Q["pto_t"]
    hb, hh, ht_ = Q["huls_b"], Q["huls_h"], Q["huls_t"]
    hsl = Q["sleuf"]
    for zp, nm in ((zb_lo, "onder"), (zb_hi, "boven")):
        add("PTO_buis_X_" + nm, citroen_buis(-Lb / 2, Lb / 2, yt, zp, pb, ph, pt_), STAAL, "X_as")
        # steunrib (10 mm, aan de buis gelast) + flensplaat op de staander. De rib loopt door de ingezaagde huls.
        for s in (-1, 1):
            xs_ = s * xa
            add("Steunrib_10mm", box(xs_ - 30, xs_ + 30, y_st1 + 8, yt - ph / 2 + 3, zp - 5, zp + 5), STAAL, "X_as")
            fl = box(xs_ - 35, xs_ + 35, y_st1, y_st1 + 8, zp - 45, zp + 45)
            for dx in (-22, 22):
                for dz in (-30, 30):
                    fl = fl.cut(cyl(5.5, V(xs_ + dx, y_st1 - 1, zp + dz), V(0, 1, 0), 10))
                    add("Bout_M10_steunflens", cyl(5, V(xs_ + dx, y_st0 - 10, zp + dz), V(0, 1, 0), (y_st1 + 20) - (y_st0 - 10)).fuse(
                        cyl(9.2, V(xs_ + dx, y_st1 + 8, zp + dz), V(0, 1, 0), 7)), ZILVER, "X_as")
            add("Steunflens_8mm", fl, STAAL, "X_as")
        # hulzen: stukken buitenbuis, achterzijde ingezaagd (sleuf) voor de steunribben
        if nm == "boven":
            pos = [(x - Q["huls_afstand"] / 2, Q["huls_L"]), (x + Q["huls_afstand"] / 2, Q["huls_L"])]
        else:
            pos = [(x, Q["huls_onder_L"])]
        for xh, Lh in pos:
            hl = citroen_ring(xh - Lh / 2, xh + Lh / 2, yt, zp, hb, hh, hb - 2 * ht_, hh - 2 * ht_)
            hl = hl.cut(box(xh - Lh / 2 - 1, xh + Lh / 2 + 1, yt - hh / 2 - 2, yt - hh / 2 + ht_ + 2.5, zp - hsl / 2, zp + hsl / 2))
            add("PTO_huls_buitenbuis", hl, STAAL, "X_as")
            pad = box(xh - Lh / 2, xh + Lh / 2, yt + hh / 2 - 2, yt + hh / 2 + 8, zp - 50, zp + 50)
            pad = pad.cut(citroen_x(xh - Lh / 2 - 1, xh + Lh / 2 + 1, yt, zp, hb - 2 * ht_, hh - 2 * ht_))
            bpts = [(xh + dx, zp + dz) for dx in (-(Lh / 2 - 20), Lh / 2 - 20) for dz in (-35, 35)]
            for (bx, bz) in bpts:
                pad = pad.cut(cyl(3.4, V(bx, yt + hh / 2 - 3, bz), V(0, 1, 0), 12))
                add("Bout_M8_huls", cyl(4, V(bx, yt + hh / 2 + 2, bz), V(0, 1, 0), (y_sl1 + 5) - (yt + hh / 2 + 2)).fuse(
                    cyl(6.5, V(bx, y_sl1, bz), V(0, 1, 0), 5)), ZILVER, "X_as")
            add("Huls_opzetplaat_8mm", pad, STAAL, "X_as")
            for xw in (xh - Lh / 2 - 8, xh + Lh / 2):
                add("Schraper_rubber", citroen_ring(xw, xw + 8, yt, zp, hb + 3, hh + 3, pb - 1.0, ph - 1.0), RUBBER, "X_as", "rubber")
            add("Smeernippel", cyl(3.2, V(xh, yt, zp + hb / 2 - 2), OMHOOG, 12), ZILVER, "X_as")
    for s, nm in ((-1, "L"), (1, "R")):
        xe = s * (Lb / 2 - 12)           # binnenvlak eindplaat
        x0 = Lb / 2 - 12 if s > 0 else -Lb / 2
        ep = box(x0, x0 + 12, yt - 30, yt + 30, zb_lo - 40, zb_hi + 40)
        ep = ep.cut(box(x0 - 1, x0 + 13, yt - 20, yt + 20, zb_lo + 55, zb_hi - 55))
        for zp in (zb_lo, zb_hi):
            ep = ep.cut(citroen_x(x0 - 1, x0 + 13, yt, zp, pb, ph))
        add("Eindplaat_X_staal_12mm_" + nm, ep, STAAL, "X_as")
        add("Riemklembeugel_6mm_" + nm, box(min(xe, xe - s * 55), max(xe, xe - s * 55), yt - 16, yt + 4, 850, 910), GALV, "X_as", "galv")
        xk = s * (Lb / 2 - 52)
        add("Riemklem_" + nm, box(xk - 15, xk + 15, y_pr1, y_pr1 + 26, 862, 898), GALV, "X_as", "galv")
        add("Eindschakelaar_inductief_M12" if s < 0 else "Eindaanslag_rubber",
            cyl(6 if s < 0 else 10, V(s * 660, yt + 37, 930), V(s, 0, 0), 28), ROOD if s < 0 else RUBBER, "X_as", "rubber")
    zr = 880.0
    add("Tandriem_HTD5M_15mm_staalkoord", box(-(Lb / 2 - 52), Lb / 2 - 52, y_pr1 + 6, y_pr1 + 21, zr - 1.7, zr + 1.7), ZWART, "X_as", "rubber")
    xm = x + 120.0
    pl = cyl(15.9, V(xm, y_pr1 + 6, 923), V(0, 1, 0), 15).fuse(cyl(18.5, V(xm, y_pr1 + 4, 923), V(0, 1, 0), 2)).fuse(
        cyl(18.5, V(xm, y_pr1 + 21, 923), V(0, 1, 0), 2))
    add("Poelie_HTD5M_20T", pl, ZILVER, "X_as", "alu")
    for dx in (-32, 32):
        add("Spanrol_D30_kogellager", cyl(15, V(xm + dx, y_pr1 + 5, 897), V(0, 1, 0), 18), ZILVER, "X_as", "alu")

    # X-slede (wagenplaat)
    sl = box(x - 150, x + 150, y_sl0, y_sl1, 700, 1120)
    sl = sl.cut(cyl(9, V(xm, y_sl0 - 1, 923), V(0, 1, 0), 12))
    for (gx, gz) in ((x - 100, 910), (x + 70, 830)):
        sl = sl.cut(cyl(20, V(gx, y_sl0 - 1, gz), V(0, 1, 0), 12))
    for xh_ in (x - Q["huls_afstand"] / 2, x + Q["huls_afstand"] / 2):                      # bovenste hulzen: ronde gaten
        for bx in (xh_ - (Q["huls_L"] / 2 - 20), xh_ + (Q["huls_L"] / 2 - 20)):
            for bz in (zb_hi - 35, zb_hi + 35):
                sl = sl.cut(cyl(4.5, V(bx, y_sl0 - 1, bz), V(0, 1, 0), 12))
    for bx in (x - (Q["huls_onder_L"] / 2 - 20), x + (Q["huls_onder_L"] / 2 - 20)):         # onderste huls: sleufgaten (tolerantie in Z)
        for bz in (zb_lo - 35, zb_lo + 35):
            sl = sl.cut(box(bx - 4.5, bx + 4.5, y_sl0 - 1, y_sl1 + 1, bz - 8, bz + 8))
    add("X_slede_alu_10mm", sl, ALU, "X_as", "alu")
    add("Planetaire_kast_5_1_NEMA23", box(xm - 30, xm + 30, y_sl1, y_sl1 + 55, 893, 953), ZWART, "X_as", "koop")
    add("NEMA23_X_closed_loop_3Nm", box(xm - 28.5, xm + 28.5, y_sl1 + 55, y_sl1 + 167, 894.5, 951.5).fuse(
        box(xm - 25, xm + 25, y_sl1 + 167, y_sl1 + 190, 898, 948)), ZWART, "X_as", "koop")

    # ================================================================ Z-as
    for zp in (zb_lo, zb_hi):
        for dx in (-40, 40):
            add("HGH15CA_wagen_Z", hgh15_blok_z(zp, y_zr, x + dx), BLAUW, "Z_as")
    add("Moerhuis_SFU1610", box(x - 26, x + 26, y_sl1, y_zs0 - 1, 890, 930).cut(cyl(14.5, V(x, y_ks, 889), OMHOOG, 42)), ZWART, "Z_as", "koop")
    add("Kogelomloopmoer_SFU1610", buis(24, 8.6, V(x, y_ks, 930), OMHOOG, 10).fuse(buis(14, 8.6, V(x, y_ks, 940), OMHOOG, 30)), ZILVER, "Z_as", "koop")
    S_b = zc + 400.0                   # onderkant Z-slede
    L_zs = 950.0
    add("Z_slede_koker_120x60x3", koker(x - 60, x + 60, y_zs0, y_zs1, S_b, S_b + L_zs, 3, "z"), STAAL, "Z_as")
    add("Z_slede_kopplaat_8mm", box(x - 45, x + 45, y_ks - 35, y_zs1, S_b + L_zs, S_b + L_zs + 8), STAAL, "Z_as")
    for dx in (-40, 40):
        add("Riser_alu_strip_25x23", box(x + dx - 12.5, x + dx + 12.5, y_zr, y_zs0, S_b + 45, S_b + 893), ALU, "Z_as", "alu")
        add("HGR15_rail_Z", hgr15_rail_z(S_b + 45, S_b + 893, y_zr, x + dx), ZILVER, "Z_as")
    add("BF12_loslager", box(x - 30, x + 30, y_zs0 - 43, y_zs0, S_b + 15, S_b + 35).cut(cyl(6, V(x, y_ks, S_b + 14), OMHOOG, 22)), ZWART, "Z_as", "koop")
    add("BK12_vastlager", box(x - 30, x + 30, y_zs0 - 43, y_zs0, S_b + 895, S_b + 920).cut(cyl(6, V(x, y_ks, S_b + 894), OMHOOG, 27)), ZWART, "Z_as", "koop")
    add("Kogelomloopspindel_SFU1610", cyl(8, V(x, y_ks, S_b + 20), OMHOOG, 920), ZILVER, "Z_as")
    add("Koppeling_spindel_10x8", cyl(12.5, V(x, y_ks, S_b + 922), OMHOOG, 28), ZILVER, "Z_as")
    add("NEMA23_Z_closed_loop_met_rem", box(x - 28.5, x + 28.5, y_ks - 28.5, y_ks + 28.5, S_b + L_zs + 8, S_b + L_zs + 160), ZWART, "Z_as", "koop")

    # ================================================================ spilbok + spil + motor
    z_lo = zc + 368.0                  # onderste lagerplaat (onderkant)
    z_bo = zc + 528.0                  # bovenste lagerplaat
    z_mo = zc + 660.0                  # motorplaat
    ach = box(x - 80, x + 80, y_sp0, y_sp1, z_lo, z_mo + 10)
    for (wz0, wz1) in ((z_lo + 30, z_lo + 135), (z_lo + 175, z_mo - 25)):     # lichtgaten
        ach = ach.cut(box(x - 32, x + 32, y_sp0 - 1, y_sp1 + 1, wz0, wz1))
    for dx in (-55, 55):
        for dz in (60, 160, 260):
            if S_b < z_lo + dz < z_mo:
                ach = ach.cut(cyl(5.5, V(x + dx, y_sp0 - 1, z_lo + dz), V(0, 1, 0), 10))
                add("Bout_M10_blindklinkmoer", cyl(8.5, V(x + dx, y_sp1, z_lo + dz), V(0, 1, 0), 7), ZILVER, "Spil")
    add("Spilbok_achterplaat_6mm", ach, ORANJE, "Spil")
    bolt_pts = [(x + dx, ys + dy) for dx in (-46, 46) for dy in (-46, 46)]
    on = box(x - 75, x + 75, y_sp1, ys + 80, z_lo, z_lo + 8).fuse(
        box(x - 125, x + 125, ys - 25, ys + 25, z_lo, z_lo + 8)).removeSplitter()   # met armen naar de potstangen
    on = gaten_z(on, [(x, ys)], 25, z_lo, 8)
    on = gaten_z(on, bolt_pts, 7, z_lo, 8)
    on = gaten_z(on, [(x - 100, ys), (x + 100, ys)], 10.5, z_lo, 8)
    add("Spilbok_lagerplaat_onder_8mm", on, ORANJE, "Spil")
    bo = box(x - 75, x + 75, y_sp1, ys + 80, z_bo, z_bo + 6)
    bo = gaten_z(gaten_z(bo, [(x, ys)], 25, z_bo, 6), bolt_pts, 7, z_bo, 6)
    add("Spilbok_lagerplaat_boven_6mm", bo, ORANJE, "Spil")
    mp = box(x - 75, x + 75, y_sp1, ys + 80, z_mo, z_mo + 8)
    mp = gaten_z(gaten_z(mp, [(x, ys)], 21, z_mo, 8), [(x + dx, ys + dy) for dx in (-46, 46) for dy in (-46, 46)], 5.5, z_mo, 8)
    add("Spilbok_motorplaat_8mm", mp, ORANJE, "Spil")
    for s, nm in ((-1, "L"), (1, "R")):
        zp_ = box(x + s * 78 - 2.5, x + s * 78 + 2.5, y_sp1, ys + 80, z_lo + 8, z_mo)
        zp_ = zp_.cut(box(x + s * 78 - 4, x + s * 78 + 4, y_sp1 + 28, ys + 55, z_lo + 40, z_bo - 12))
        zp_ = zp_.cut(box(x + s * 78 - 4, x + s * 78 + 4, y_sp1 + 28, ys + 55, z_bo + 40, z_mo - 22))
        add("Spilbok_zijplaat_5mm_" + nm, zp_, ORANJE, "Spil")
    add("UCF207_onder", ucf207(x, ys, z_lo + 8), BLAUW, "Spil", "koop")
    add("UCF207_boven", ucf207(x, ys, z_bo + 8), BLAUW, "Spil", "koop")
    add("Spilas_D35_C45", cyl(Q["as_d"] / 2, V(x, ys, zc + 112), OMHOOG, 528), ZILVER, "Spil")
    add("Spilflens_D110x12_gelast", flens_gaten(cyl(55, V(x, ys, zc + 100), OMHOOG, 12), x, ys, zc + 100, 12), ZILVER, "Spil")
    add("Klauwkoppeling_D65", cyl(32.5, V(x, ys, zc + 584), OMHOOG, 76), ROOD, "Spil", "koop")
    mot = box(x - 55, x + 55, ys - 55, ys + 55, z_mo + 10, z_mo + 22).fuse(cyl(55, V(x, ys, z_mo + 22), OMHOOG, 160))
    mot = mot.fuse(box(x - 30, x + 30, ys + 50, ys + 80, z_mo + 60, z_mo + 120)).fuse(cyl(30, V(x, ys, z_mo + 182), OMHOOG, 12))
    add("Spilmotor_BLDC_48V_1500W_3000rpm", mot, ZWART, "Spil", "koop")

    # ================================================================ pot (rust met eigen gewicht op de grond)
    R = Q["pot_D"] / 2
    H = Q["pot_h"]
    rim = max(0.0, zc - Q["pot_rand"])
    add("Pot_RVS_D250x2", buis(R, R - Q["pot_t"], V(x, ys, rim), OMHOOG, H), RVS, "Pot", "rvs", 30)
    dek = gaten_z(cyl(R, V(x, ys, rim + H), OMHOOG, 3), [(x, ys)], 25, rim + H, 3)
    dek = gaten_z(dek, [(x - 100, ys), (x + 100, ys)], 8, rim + H, 3)
    add("Pot_deksel_RVS_3mm", dek, RVS, "Pot", "rvs", 30)
    add("Pot_rubberrand", buis(R + 3, R, V(x, ys, rim), OMHOOG, 25), RUBBER, "Pot", "rubber")
    sk = Part.makeCone(R + 50, R + 3, 50, V(x, ys, rim + H - 60), OMHOOG).cut(
        Part.makeCone(R + 47, R, 50, V(x, ys, rim + H - 60), OMHOOG))
    add("Pot_spatflap_rubber", sk, RUBBER, "Pot", "rubber")      # V2: tegen wegvliegende steentjes bij maaien met opgetilde pot
    add("Asafdichting_rubber", buis(32, 18, V(x, ys, rim + H + 3), OMHOOG, 8), RUBBER, "Pot", "rubber")
    for s in (-1, 1):
        px = x + s * 100
        add("Potstang_D16", cyl(8, V(px, ys, rim + H + 3), OMHOOG, 291), ZILVER, "Pot")
        add("Stelring_D28", buis(14, 8, V(px, ys, rim + H + 3 + 279), OMHOOG, 12), ZILVER, "Pot")
        add("Glijbus_PE_D40", buis(20, 8.5, V(px, ys, z_lo + 8), OMHOOG, 25), PE, "Pot", "pe")
    zring = z_lo + 8 + 25 + 7          # hoogte stelring in rust
    add("Sensor_grondcontact_M12", cyl(6, V(x + 100, ys + 20, zring), V(0, 1, 0), 45), ROOD, "Pot", "rubber")
    add("Sensorbeugel_3mm", box(x + 92, x + 108, ys + 40, ys + 43, z_lo + 8, zring + 10), GALV, "Pot", "galv")

    # ================================================================ gereedschap
    gereedschap = []
    if Q["gereedschap"] == "frees":
        for (n, sh, kl, mat) in vermorzelfrees(x, ys, zc):
            add(n, sh, kl, "Gereedschap", mat)
        los = maaischijf(850, 700, 0.0)
    else:
        for (n, sh, kl, mat) in maaischijf(x, ys, zc):
            add(n, sh, kl, "Gereedschap", mat)
        los = vermorzelfrees(850, 700, 35.0)
    for (n, sh, kl, mat) in los:
        add("Los_" + n, sh, kl, "Wisselgereedschap_los", mat)

    # ================================================================ camera + licht (op de X-slede)
    xc_ = x - 120.0
    add("Cameramast_alu_30x30x2", koker(xc_ - 15, xc_ + 15, y_sl1, y_sl1 + 30, 1000, 1420, 2, "z"), ALU, "Camera", "alu")
    add("Cameraarm_alu_30x30x2", koker(xc_ - 15, xc_ + 15, y_sl1 + 30, 760, 1390, 1420, 2, "y"), ALU, "Camera", "alu")
    cam = box(xc_ - 30, xc_ + 30, 712, 768, 1325, 1390).fuse(cyl(14, V(xc_, 740, 1300), OMHOOG, 25))
    add("Camera_industrieel_USB3", cam, ZWART, "Camera", "koop")
    add("LED_lamp_48V_lichtbalk", box(xc_ - 150, xc_ + 150, 670, 700, 1360, 1390).fuse(
        box(xc_ - 150, xc_ + 150, 672, 698, 1356, 1360)), LED, "Camera", "koop")

    # ================================================================ elektra
    add("E_kast_IP65_300x250x120", box(-300, 0, -15, 105, 790, 1040), GRIJS, "Elektra", "koop")
    for k_ in range(4):
        add("Kabelwartel_M20", cyl(10, V(-270 + 60 * k_, 45, 770), OMHOOG, 20), ZWART, "Elektra", "rubber")
    zk = zb_hi + 60                    # V2: boven de hulzen en smeernippels
    x_vast = -L / 2 + 30
    x_mee = x - 80
    x_b = max(x_vast, x_mee) + 120
    yk0, yk1 = yt - 25, yt + 25
    add("Kabelrups_X_onderpart", box(x_vast, x_b, yk0, yk1, zk, zk + 25), ZWART, "Elektra", "koop")
    add("Kabelrups_X_bovenpart", box(x_mee, x_b, yk0, yk1, zk + 55, zk + 80), ZWART, "Elektra", "koop")
    add("Kabelrups_X_bocht", box(x_b, x_b + 25, yk0, yk1, zk, zk + 80), ZWART, "Elektra", "koop")
    add("Kabelrups_meenemer_3mm", box(x_mee - 20, x_mee + 20, yk0, y_sl1, zk + 80, zk + 86).fuse(
        box(x_mee - 20, x_mee + 20, y_sl0 - 3, y_sl0, 1112, zk + 86)), GALV, "Elektra", "galv")

    # V2: spiraalkabel van de X-slede naar de Z-slede (spilmotor, Z-motor, pot-sensor). Rekt mee met de Z-slag.
    z_top = S_b + L_zs + 8             # bovenkant kopplaat Z-slede
    xsp, ysp = x + 95.0, y_zs0 + 15.0
    z_b0 = 1128.0                      # beugel op de X-slede
    add("Kabelbeugel_X_slede_6mm", box(xsp - 20, xsp + 20, y_sl0, ysp + 15, 1120, z_b0), GALV, "Elektra", "galv")
    add("Kabelbeugel_Z_slede_6mm", box(x + 45, xsp + 20, y_zs0, y_zs0 + 30, z_top, z_top + 6), GALV, "Elektra", "galv")
    n_w = 26
    z_a, z_c = z_b0, max(z_top, z_b0 + 60)
    steek = (z_c - z_a) / n_w
    for k_ in range(n_w):
        ring = Part.makeTorus(22, 4.5, V(xsp, ysp, z_a + steek * (k_ + 0.5)), OMHOOG)
        add("Spiraalkabel_Z", ring, ZWART, "Elektra", "rubber")

    # ================================================================ omgeving (alleen voor de plaatjes)
    gr = box(-900, 900, -1150, 1350, -4, 0)
    gd = box(x - 330, x + 330, ys - 330, ys + 330, -4, 0)        # klein stuk maaiveld voor de detailplaat
    if Q["gereedschap"] == "frees" and zc < 0:
        gat = cyl(Q["frees_D"] / 2 + 2, V(x, ys, -10), OMHOOG, 20)
        gr, gd = gr.cut(gat), gd.cut(gat)
        add("Vermorzelde_kolom_REF", cyl(Q["frees_D"] / 2, V(x, ys, zc), OMHOOG, -zc), GROND, "Omgeving", "ref", 55)
    add("Maaiveld_REF", gr, GROEN, "Omgeving", "ref", 40)
    add("Maaiveld_detail_REF", gd, GROEN, "Detail", "ref", 60)
    px, py = Q["plant_x"], Q["plant_y"]
    for k_ in range(7):
        b = blad(230 - 15 * (k_ % 3), 85, 3)
        b.rotate(V(0, 0, 0), V(0, 1, 0), -22)
        b.rotate(V(0, 0, 0), OMHOOG, k_ * 360.0 / 7 + 10)
        b.translate(V(px, py, 15))
        add("Ridderzuring_plant_blad_REF", b, BLAD, "Omgeving", "ref", 0)
    add("Ridderzuring_plant_wortelkop_REF", cyl(22, V(px, py, -10), OMHOOG, 30), BRUIN, "Omgeving", "ref", 0)
    add("Ridderzuring_plant_penwortel_REF", Part.makeCone(2.0, 20.0, 320, V(px, py, -330), OMHOOG), BRUIN, "Omgeving", "ref", 30)

    # ================================================================ objecten aanmaken
    groepen = {}
    for (naam, sh, kleur, transp, groep, mat) in delen:
        if groep not in groepen:
            groepen[groep] = doc.addObject("App::DocumentObjectGroup", groep)
        o = doc.addObject("Part::Feature", naam)
        o.Shape = sh
        o.addProperty("App::PropertyString", "Materiaal", "Ridderzuring")
        o.Materiaal = mat
        o.addProperty("App::PropertyString", "Groep", "Ridderzuring")
        o.Groep = groep
        try:
            o.ViewObject.ShapeColor = kleur
            o.ViewObject.Transparency = transp
        except Exception:
            pass
        groepen[groep].addObject(o)
        if groep == "Detail":
            try:
                o.ViewObject.Visibility = False
            except Exception:
                pass
    doc.recompute()
    info = dict(ys=ys, S_b=S_b, y_ks=y_ks, z_lo=z_lo, yt=yt)
    return doc, info


# ------------------------------------------------------------------ rekenwerk
def massa(doc, groep_filter=None, uitsluit=()):
    """Massa [kg] en zwaartepunt van het aanbouwdeel (zonder REF, omgeving en losse gereedschap)."""
    tot, mom, per = 0.0, V(0, 0, 0), {}
    for o in doc.Objects:
        if o.TypeId != "Part::Feature" or not hasattr(o, "Materiaal"):
            continue
        if o.Materiaal == "ref" or o.Groep in ("Wisselgereedschap_los",):
            continue
        if groep_filter and o.Groep not in groep_filter:
            continue
        if o.Name.startswith(tuple(uitsluit)) if uitsluit else False:
            continue
        kg = None
        for k, v in KOOP_KG.items():
            if o.Name.startswith(k):
                kg = v
        for k, v in KG_PER_M.items():
            if o.Name.startswith(k):
                bb = o.Shape.BoundBox
                kg = v * max(bb.XLength, bb.YLength, bb.ZLength) / 1000
        if kg is None:
            kg = o.Shape.Volume * DICHTHEID.get(o.Materiaal, 7.85e-6)
        tot += kg
        mom = mom + zwaartepunt(o.Shape) * kg
        per[o.Groep] = per.get(o.Groep, 0.0) + kg
    return tot, (mom * (1.0 / tot) if tot > 0 else V(0, 0, 0)), per


def rekenwerk(doc, info):
    g = 9.81
    q = Q
    T_nom = q["motor_P"] / (2 * math.pi * q["motor_rpm"] / 60)
    n = q["frees_rpm"]
    P_nom = T_nom * 2 * math.pi * n / 60
    P_piek = min(P_nom * q["motor_piek"], q["motor_P"] * q["motor_piek"])
    R = q["frees_D"] / 2000
    v_tip = 2 * math.pi * R * n / 60
    F_tip = T_nom / R
    v_maai = math.pi * 0.230 * q["maai_rpm"] / 60
    tanden = 4
    hap = q["insteek"] / (n / 60 * tanden)
    V_gat = math.pi * R ** 2 * q["diepte"] / 1000
    t_in = q["diepte"] / q["insteek"]
    F_z = 2 * math.pi * q["stap_T"] * 0.9 / (q["z_spoed"] / 1000)
    r_p = q["x_poelie_T"] * q["htd_steek"] / (2 * math.pi) / 1000
    F_x = q["stap_T"] * q["x_kast"] * 0.95 / r_p
    # cyclus per plant [s]
    z_naar_grond = q["rijstand"] - q["pot_rand"]      # freesonderkant van rijstand tot potcontact
    cyc = dict(X_verplaatsen=333 / q["ijl_x"] + 0.5, Z_omlaag_tot_pot=z_naar_grond / q["ijl_z"] + 0.3,
               insteken=t_in, nadraaien=1.0, mengend_omhoog=q["diepte"] / (2 * q["insteek"]),
               Z_omhoog=z_naar_grond / q["ijl_z"] + 0.3, robot_stop_start=4.0)
    t_cyc = sum(cyc.values())
    # massa en aslasten: yf = as aan de portaalkant (aangedreven), yr = verre as (gestuurd)
    m_a, zw, per = massa(doc)
    m_r = q["robot_massa"]
    yf, yr = q["rb_as_portaal_y"], q["rb_as_ver_y"]
    Lw = yf - yr
    N_f0 = m_r * (q["robot_zw_y"] - yr) / Lw
    N_f = (m_r * (q["robot_zw_y"] - yr) + m_a * (zw.y - yr)) / Lw
    N_r = m_r + m_a - N_f
    N_fa = (m_r * (q["robot_zw_y_accu"] - yr) + m_a * (zw.y - yr)) / Lw
    F_max = g * (m_r * (q["robot_zw_y"] - yr) + m_a * (zw.y - yr)) / (info["ys"] - yr)
    # spilas: overhang onderste lager -> zwaartepunt frees, zijkracht 300 N
    d = q["as_d"]
    I = math.pi * d ** 4 / 64
    E = 210e3
    a = 396.0 - 40.0                   # lagerhart onderste UCF207 (zc+396) tot snijniveau (zc+40)
    Ls = 160.0
    F = 300.0
    delta = F * a ** 2 * (Ls + a) / (3 * E * I)
    sigma = F * a / (math.pi * d ** 3 / 32)
    m_tool = 2.6
    k = 3 * E * I / (a ** 2 * (Ls + a)) * 1000          # N/m
    n_kr = math.sqrt(k / m_tool) * 60 / (2 * math.pi)
    m_x = massa(doc, ("X_as", "Z_as", "Spil", "Pot", "Gereedschap", "Camera"),
                uitsluit=("PTO_buis", "Steunrib", "Steunflens", "Bout_M10_steunflens", "Eindplaat", "Riemklem", "Tandriem", "Eind"))[0]
    m_z = massa(doc, ("Z_as", "Spil", "Pot", "Gereedschap"),
                uitsluit=("HGH15CA_wagen_Z", "Moerhuis", "Kogelomloopmoer"))[0]
    E_lo, E_hi = 500e3 * V_gat, 2000e3 * V_gat
    print("=== Ridderzuringfrees - kengetallen ===")
    print("Spil: %.0f rpm, Ø%.0f -> tipsnelheid %.1f m/s | maaien %.0f rpm Ø230 -> %.0f m/s" % (n, q["frees_D"], v_tip, q["maai_rpm"], v_maai))
    print("Motor %.0f W / %.0f rpm: nominaal %.1f Nm -> bij %.0f rpm %.0f W nominaal, %.0f W piek (VESC %.0fx stroom)"
          % (q["motor_P"], q["motor_rpm"], T_nom, n, P_nom, P_piek, q["motor_piek"]))
    print("Tipkracht nominaal %.0f N, piek %.0f N" % (F_tip, F_tip * q["motor_piek"]))
    print("Insteken %.0f mm/s: %.2f mm per tand per omwenteling (%d tanden) -> wortel in plakjes van %.2f mm"
          % (q["insteek"], hap, tanden, hap))
    print("Gat Ø%.0f x %.0f: %.2f liter grond; snij-energie %.1f - %.1f kJ -> %.0f - %.0f W gemiddeld in %.0f s"
          % (q["frees_D"], q["diepte"], V_gat * 1000, E_lo / 1e3, E_hi / 1e3, E_lo / t_in, E_hi / t_in, t_in))
    print("Z: SFU16%02d + NEMA23 %.0f Nm -> %.0f N (begrenzen op ~600 N), ijlgang %.0f mm/s" % (q["z_spoed"], q["stap_T"], F_z, q["ijl_z"]))
    print("X: 5:1 + HTD5M %dT -> houdkracht %.0f N, ijlgang %.0f mm/s" % (q["x_poelie_T"], F_x, q["ijl_x"]))
    print("Cyclus per plant: " + ", ".join("%s %.1f s" % (k_, v_) for k_, v_ in cyc.items()))
    print("  totaal %.1f s -> ca. %.0f planten per uur" % (t_cyc, 3600 / t_cyc))
    print("Massa aanbouwdeel ca. %.0f kg (zwaartepunt Y=%.0f, Z=%.0f mm)" % (m_a, zw.y, zw.z))
    for k_, v_ in sorted(per.items(), key=lambda t: -t[1]):
        print("    %-14s %5.1f kg" % (k_, v_))
    print("Bewegende massa X ca. %.0f kg, Z ca. %.0f kg" % (m_x, m_z))
    print("Aslast (aanname robot %.0f kg, zw Y=%.0f): portaalkant/aangedreven %.0f kg, gestuurd %.0f kg (zonder aanbouw %.0f / %.0f)"
          % (m_r, q["robot_zw_y"], N_f, N_r, N_f0, m_r - N_f0))
    print("  met de accu aan de verre kant (zw Y=%.0f): aangedreven %.0f kg, gestuurd %.0f kg"
          % (q["robot_zw_y_accu"], N_fa, m_r + m_a - N_fa))
    print("Max. neerwaartse kracht voordat de portaal-as loskomt: %.0f N" % F_max)
    print("Spilas Ø%.0f, lagerafstand %.0f, overhang %.0f: bij %.0f N zijkracht %.2f mm doorbuiging, %.0f MPa"
          % (d, Ls, a, F, delta, sigma))
    print("  kritisch toerental ca. %.0f rpm (maaien %.0f rpm = %.0f%%)" % (n_kr, q["maai_rpm"], 100 * q["maai_rpm"] / n_kr))
    # ---- V2: X-geleiding op aftakasbuizen
    Iy, Iz, A_buis = doorsnede_I()
    Lb = q["xbalk_L"]
    a_ov = q["x_slag"] / 2 + q["huls_afstand"] / 2 - q["arm_x"]       # uitkraging van het uiterste hulscentrum voorbij de steun
    L_sp = 2 * q["arm_x"]
    P_z = m_x * g / 2                                                  # gewicht per buis (2 buizen)
    d_z = P_z * a_ov ** 2 * (a_ov + L_sp) / (3 * E * Iy)
    F_zz = 600.0                                                       # max. Z-kracht (software-begrenzing)
    lever = info["ys"] - info["yt"]       # afstand spilhart - hart buizen in Y
    F_c = F_zz * lever / (q["xbalk_z"][1] - q["xbalk_z"][0])           # koppel om X-as -> kracht in Y op boven- en onderbuis
    d_y = F_c * a_ov ** 2 * (a_ov + L_sp) / (3 * E * Iz)
    m_buizen = 2 * A_buis * Lb * 7.85e-6
    mu = 0.15                                                          # gesmeerd staal op PE-glijbus
    F_fr = mu * (2 * F_c + m_x * g * 0.5)
    print("--- V2 X-geleiding: aftakasbuizen %.1fx%.1fx%.1f, L=%.0f, steun op X=±%.0f ---" % (q["pto_b"], q["pto_h"], q["pto_t"], Lb, q["arm_x"]))
    print("  doorsnede %.0f mm2, I(buigen in Z) %.0f mm4, I(buigen in Y) %.0f mm4, 2 buizen samen %.1f kg" % (A_buis, Iy, Iz, m_buizen))
    print("  uitkraging tot uiterste huls %.0f mm; doorbuiging in Z onder gewicht X-slede (%.0f kg): %.2f mm" % (a_ov, m_x, d_z))
    print("  bij %.0f N Z-kracht en hefboom %.0f mm: kracht in Y per buis %.0f N -> doorbuiging in Y %.2f mm per buis (tegengesteld)" % (F_zz, lever, F_c, d_y))
    print("  verdraaiing X-slede om X-as aan de uiterste stand ca. %.2f graden" % math.degrees(2 * d_y / (q["xbalk_z"][1] - q["xbalk_z"][0])))
    print("  wrijving X (mu %.2f): %.0f N tegen houdkracht %.0f N -> versnelling %.1f m/s2 mogelijk" % (mu, F_fr, F_x, (F_x - F_fr) / m_x))
    return dict(T_nom=T_nom, P_nom=P_nom, P_piek=P_piek, v_tip=v_tip, v_maai=v_maai, F_tip=F_tip, hap=hap,
                V_gat=V_gat, E_lo=E_lo, E_hi=E_hi, t_in=t_in, F_z=F_z, F_x=F_x, cyc=cyc, t_cyc=t_cyc,
                m_a=m_a, zw=zw, per=per, m_x=m_x, m_z=m_z, N_f=N_f, N_r=N_r, N_f0=N_f0, N_fa=N_fa, F_max=F_max,
                delta=delta, sigma=sigma, n_kr=n_kr)


# ------------------------------------------------------------------ export
LASERDELEN = [  # (objectnaam, normaal) - snijcontour op halve dikte, plat gelegd
    ("Spilbok_achterplaat_6mm", "y"), ("Spilbok_lagerplaat_onder_8mm", "z"),
    ("Spilbok_lagerplaat_boven_6mm", "z"), ("Spilbok_motorplaat_8mm", "z"),
    ("Spilbok_zijplaat_5mm_L", "x"), ("Pot_deksel_RVS_3mm", "z"),
    ("Frees_kruis_onder_Hardox_10mm", "z"), ("Frees_kruis_boven_Hardox_10mm", "z"),
    ("Frees_flens_10mm", "z"), ("Frees_tand_Hardox_10mm", "y"),
    ("Los_Maaischijf_4mm", "z"), ("Los_Maaischijf_flens_10mm", "z"),
    ("Kruisklem_plaat_5mm", "z"), ("Eindplaat_X_staal_12mm_L", "x"), ("Steunflens_8mm", "y"), ("Huls_opzetplaat_8mm", "y"), ("X_slede_alu_10mm", "y"),
]


def export_dxf(doc):
    try:
        import importDXF
    except Exception as e:
        print("DXF-export overgeslagen:", e)
        return []
    os.makedirs(MAP + "dxf", exist_ok=True)
    klaar = []
    for naam, nrm in LASERDELEN:
        o = doc.getObject(naam)
        if o is None:
            continue
        sh = o.Shape
        bb = sh.BoundBox
        if nrm == "z":
            mid = bb.ZMin + 0.8 * (bb.ZMax - bb.ZMin)       # boven de afschuining van de snijkanten
            c = Part.makeCompound(sh.slice(V(0, 0, 1), mid))
            c.translate(V(-bb.XMin, -bb.YMin, -mid))
        elif nrm == "y":
            mid = (bb.YMin + bb.YMax) / 2
            c = Part.makeCompound(sh.slice(V(0, 1, 0), mid))
            c.translate(V(-bb.XMin, -mid, -bb.ZMin))
            c.rotate(V(0, 0, 0), V(1, 0, 0), 90)
        else:
            mid = (bb.XMin + bb.XMax) / 2
            c = Part.makeCompound(sh.slice(V(1, 0, 0), mid))
            c.translate(V(-mid, -bb.YMin, -bb.ZMin))
            c.rotate(V(0, 0, 0), V(0, 1, 0), -90)
        t = doc.addObject("Part::Feature", "DXF_tmp")
        t.Shape = c
        importDXF.export([t], MAP + "dxf/" + naam.replace("Los_", "") + ".dxf")
        doc.removeObject(t.Name)
        klaar.append(naam)
    print("DXF (%d stuks) in %sdxf/" % (len(klaar), MAP))
    return klaar


def export_alles(doc):
    os.makedirs(MAP, exist_ok=True)
    doc.saveAs(MAP + "dockweed_drill_v2.FCStd")
    import Import
    Import.export([o for o in doc.Objects if o.TypeId == "Part::Feature" and getattr(o, "Materiaal", "") != "ref"
                   and o.Groep != "Wisselgereedschap_los"], MAP + "dockweed_drill_v2.step")
    export_dxf(doc)


# ------------------------------------------------------------------ plaatjes
def zet_camera(view, richting):
    d = V(*richting)
    d.normalize()
    r = d.cross(OMHOOG)
    r.normalize()
    u = r.cross(d)
    u.normalize()
    try:
        view.setCameraOrientation(App.Rotation(r, u, d * -1.0, "ZXY"))
    except Exception:
        view.setViewDirection((d.x, d.y, d.z))


def actieve_view(doc):
    import FreeCADGui as Gui
    App.setActiveDocument(doc.Name)
    return Gui.getDocument(doc.Name).activeView()


def render(doc, bestand, richting, alleen=None, transp=None, b=1600, h=1000, zoom=0.82):
    """alleen = groepen en/of objectnamen die zichtbaar moeten zijn (None = alles behalve 'Detail')."""
    v = actieve_view(doc)
    oud_zicht, oud_tr = {}, {}
    for o in doc.Objects:
        if o.TypeId != "Part::Feature":
            continue
        oud_zicht[o.Name] = o.ViewObject.Visibility
        oud_tr[o.Name] = o.ViewObject.Transparency
        if alleen is not None:
            o.ViewObject.Visibility = o.Groep in alleen or o.Name in alleen
        if transp and o.Name in transp:
            o.ViewObject.Transparency = transp[o.Name]
    zet_camera(v, richting)
    v.fitAll()
    try:
        cam = v.getCameraNode()
        cam.height.setValue(cam.height.getValue() * zoom)
    except Exception:
        pass
    v.saveImage(MAP + bestand, b, h, "White")
    for o in doc.Objects:
        if o.Name in oud_zicht:
            o.ViewObject.Visibility = oud_zicht[o.Name]
            o.ViewObject.Transparency = oud_tr[o.Name]


VOOR_LINKS = (0.55, -1.0, -0.55)
VOOR_RECHTS = (-0.55, -1.0, -0.55)


def maak_renders():
    doc, info = build("Ridderzuring_rijstand", x_slede=-250.0, z_frees=P["rijstand"])
    render(doc, "render_driving_position.png", VOOR_LINKS)
    App.closeDocument(doc.Name)
    doc, info = build("Ridderzuring_maaien", x_slede=250.0, z_frees=30.0, gereedschap="maai")
    render(doc, "render_mowing.png", VOOR_RECHTS)
    App.closeDocument(doc.Name)
    doc, info = build()
    render(doc, "render_front_left.png", VOOR_LINKS)
    render(doc, "render_front_right_top.png", (-0.7, -1.0, -0.9))
    render(doc, "render_side_view.png", (-1.0, 0.0, 0.0))
    render(doc, "render_front_view.png", (0.0, -1.0, 0.0))
    pot = [o.Name for o in doc.Objects if o.TypeId == "Part::Feature" and o.Groep == "Pot"]
    render(doc, "render_detail_cutter_in_soil.png", (-1.0, -0.45, -0.3),
           alleen=("Spil", "Pot", "Gereedschap", "Detail", "Vermorzelde_kolom_REF"),
           transp=dict([(n, 72) for n in pot] + [("Vermorzelde_kolom_REF", 82)]), b=1100, h=1400, zoom=0.95)
    export_alles(doc)
    return doc


if __name__ == "__main__" or True:
    _doc, _info = build()
    _res = rekenwerk(_doc, _info)
    export_alles(_doc)
    try:
        if App.GuiUp:
            _v = actieve_view(_doc)
            zet_camera(_v, VOOR_LINKS)
            _v.fitAll()
    except Exception:
        pass
