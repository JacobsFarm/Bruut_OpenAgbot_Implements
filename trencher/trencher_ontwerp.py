# -*- coding: utf-8 -*-
"""
Geulfrees / trencher voor AgOpenBot "Bruut" - elektrisch, zo eenvoudig mogelijk.

Principe: schoepenschijf (greppelfrees-principe, maar klein)
  * Eén schijf Ø600 x 10 mm (laser) met 6 gelaste schoepen + verwisselbare snijmessen
    (Hardox / oud graafbakmes, 10 mm). Mesbreedte 100 / 150 / 200 mm = geulbreedte.
    Alle messen wijzen naar links -> rechts van de schijf blijft ruimte voor lager en
    kettingkast BUITEN de geul. Tipdiameter Ø700 -> max. diepte 200 mm met de naaf
    nog 150 mm boven maaiveld.
  * Tegenlopend (onderkant schijf beweegt mee met rijrichting): grond wordt van onder naar
    boven gesneden, over de top gegooid en door de kap naar LINKS uitgeworpen (verspreid).
  * Aandrijving: BLDC-motor 48 V 1,5 kW 3000 rpm + planetaire kast i=10 -> 300 rpm,
    via ketting 08B-1 15T/15T (1:1) in een smalle kettingkast naar de schijfas.
    Toerental en overbelasting worden elektronisch geregeld (stroomgrens controller).
  * Ophanging: één scharnierarm aan een bok die met 2 beugelbouten op de achterbalk van
    de robot klemt (niets boren/lassen aan de robot). Elektrische lineaire actuator
    (6000 N, slag 200) voor heffen; sleufgat in het onderste oog = zweefstand, de
    diepte wordt bepaald door een verstelbare glijslof naast de geul.
  * Omdat de schijf rotatiesymmetrisch is, maakt de hoek van de arm niets uit voor de
    geulvorm -> geen parallellogram nodig.

Uitvoeren in FreeCAD:
    exec(open(r"F:/veldrobot/aanbouwdelen/trencher/trencher_ontwerp.py", encoding="utf-8").read())
Assen: X = breedte (0 = midden robot), Y = rijrichting (+Y = voor, robot staat bij Y>0),
Z = omhoog (0 = maaiveld). Maten in mm. Het gereedschap wordt opgebouwd in de stand
"max. diepte 200 mm" en daarna om het scharnier gedraaid naar P["diepte"].
"""
import math
import FreeCAD as App
import Part

V = App.Vector
MAP = r"F:/veldrobot/aanbouwdelen/trencher/"

P = dict(
    diepte=150.0,          # getoonde werkdiepte (100..200)
    geul_b=150.0,          # mesbreedte = geulbreedte (100 / 150 / 200)
    tip_D=700.0,           # tipdiameter schijf incl. messen
    schijf_D=600.0,
    schijf_t=10.0,
    n_schoep=6,
    as_d=35.0,
    naaf_Y=-750.0,         # schijfnaaf achter de robotbalk
    scharnier=(-110.0, 420.0),   # (Y, Z) scharnierpen arm
    act_boven=(-120.0, 960.0),   # (Y, Z) bovenste pen actuator
    act_onder=(-420.0, 480.0),   # (Y, Z) onderste pen (op arm, stand max. diepte)
    motor_rpm=3000.0,
    motor_P=1500.0,
    i_kast=10.0,
    tand_motor=15,
    tand_as=15,
    ketting_steek=12.7,
    rijsnelheid=3.0,       # m/min tijdens frezen
)

STAAL = (0.22, 0.24, 0.26)
GEEL = (0.95, 0.70, 0.05)
ZWART = (0.08, 0.08, 0.08)
BLAUW = (0.10, 0.20, 0.45)
ZILVER = (0.75, 0.75, 0.78)
GALV = (0.62, 0.66, 0.68)
ORANJE = (0.90, 0.35, 0.05)
PE = (0.92, 0.92, 0.88)


# ------------------------------------------------------------------ hulpfuncties
def pd(z, p):
    return p / math.sin(math.pi / z)


def face_yz(points, x0=0.0):
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


def prism_yz(points, x0, thickness):
    return face_yz(points, x0).extrude(V(thickness, 0, 0))


def cyl_x(r, x0, length, y=0.0, z=0.0):
    return Part.makeCylinder(r, length, V(x0, y, z), V(1, 0, 0))


def hull2d(pts):
    pts = sorted(set((round(a, 4), round(b, 4)) for a, b in pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p_ in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p_) <= 0:
            lo.pop()
        lo.append(p_)
    for p_ in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p_) <= 0:
            up.pop()
        up.append(p_)
    return lo[:-1] + up[:-1]


def cirkel(c, r, n=48):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def rect(y0, y1, z0, z1):
    return [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]


def stadium(c1, r1, c2, r2):
    return hull2d(cirkel(c1, r1, 72) + cirkel(c2, r2, 72))


def sprocket(z_teeth, p, x0, width, y, zc, bore):
    d_p = pd(z_teeth, p)
    body = cyl_x((d_p + 0.6 * 8.51) / 2, x0, width, y, zc)
    for i in range(z_teeth):
        a = 2 * math.pi * i / z_teeth
        body = body.cut(cyl_x(4.36, x0 - 1, width + 2, y + d_p / 2 * math.cos(a), zc + d_p / 2 * math.sin(a)))
    body = body.fuse(cyl_x(min(d_p * 0.35, 22), x0 - 15, 15, y, zc)).removeSplitter()
    return body.cut(cyl_x(bore / 2, x0 - 20, width + 40, y, zc))


def ucfl207(x_face, s, y, z):
    """UCFL207 (≈): ovale 2-gats flens L=163, J=130 (M14), flens 15, bouten verticaal-ish (in Z)."""
    L, J, H, tf = 163.0, 130.0, 92.0, 15.0
    x0 = x_face if s > 0 else x_face - tf
    pts = []
    for k in range(73):
        a = 2 * math.pi * k / 72
        pts += [(y + 16 * math.cos(a), z - J / 2 + 16 * math.sin(a)),
                (y + 16 * math.cos(a), z + J / 2 + 16 * math.sin(a)),
                (y + H / 2 * math.cos(a), z + H / 2 * math.sin(a))]
    h = prism_yz(hull2d(pts), x0, tf)
    boss = cyl_x(42, x_face + tf if s > 0 else x_face - tf - 22, 22, y, z)
    h = h.fuse(boss).removeSplitter()
    for dz in (-J / 2, J / 2):
        h = h.cut(cyl_x(8, x0 - 1, tf + 2, y, z + dz))
    return h.cut(cyl_x(P["as_d"] / 2 + 0.2, x_face - 60, 120, y, z))


def koker_x(x0, length, y0, z0, b, h, t):
    return Part.makeBox(length, b, h, V(x0, y0, z0)).cut(
        Part.makeBox(length + 2, b - 2 * t, h - 2 * t, V(x0 - 1, y0 + t, z0 + t)))


def koker_y(x0, y0, length, z0, b, h, t):
    return Part.makeBox(b, length, h, V(x0, y0, z0)).cut(
        Part.makeBox(b - 2 * t, length + 2, h - 2 * t, V(x0 + t, y0 - 1, z0 + t)))


def rot(pt, c, hoek_deg):
    """draai punt (Y,Z) om c in het YZ-vlak (positief = om +X, rechterhand)."""
    a = math.radians(hoek_deg)
    y, z = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + y * math.cos(a) - z * math.sin(a), c[1] + y * math.sin(a) + z * math.cos(a))


# ------------------------------------------------------------------ ontwerp
def build(doc_name="Trencher_Bruut"):
    if doc_name in App.listDocuments():
        App.closeDocument(doc_name)
    doc = App.newDocument(doc_name)

    R_tip = P["tip_D"] / 2
    Hy = P["naaf_Y"]
    Hz = R_tip - 200.0                  # naafhoogte bij max. diepte 200
    H = (Hy, Hz)
    U = (Hy + 60.0, Hz + 470.0)         # motor-/bovenste kettingwiel
    S = P["scharnier"]

    gereedschap = []                    # (naam, shape, kleur, transp, groep) -> wordt mee gedraaid

    def tool(name, shape, rgb=STAAL, transp=0, grp="Schijf"):
        gereedschap.append((name, shape, rgb, transp, grp))

    vast = []

    def fix(name, shape, rgb=STAAL, transp=0, grp="Bok"):
        vast.append((name, shape, rgb, transp, grp))

    # ---------------- schijf + schoepen + messen (X: schijf 65..75, messen naar links)
    xs0, xs1 = 65.0, 65.0 + P["schijf_t"]
    rs = P["schijf_D"] / 2
    schijf = cyl_x(rs, xs0, P["schijf_t"], Hy, Hz)
    for i in range(P["n_schoep"]):
        a = 2 * math.pi * (i + 0.5) / P["n_schoep"]
        schijf = schijf.cut(cyl_x(60, xs0 - 1, 12, Hy + 170 * math.cos(a), Hz + 170 * math.sin(a)))
    schijf = schijf.fuse(cyl_x(45, xs1, 15, Hy, Hz)).removeSplitter()          # gelaste naaf
    schijf = schijf.cut(cyl_x(P["as_d"] / 2, xs0 - 1, 40, Hy, Hz))
    tool("Schijf_D600x10_met_naaf", schijf, GEEL)

    xm1 = xs1 + 5.0                      # rechterkant mes steekt 5 mm buiten schijf
    xm0 = xm1 - P["geul_b"]
    for i in range(P["n_schoep"]):
        hoek = 360.0 * i / P["n_schoep"]
        # schoep: 8 mm plaat, gelast loodrecht op schijf, radiaal r=230..300
        sch = Part.makeBox(xs0 - (xm0 + 10), 8, 70, V(xm0 + 10, 0, 230))
        # mes: 10 mm, radiaal r=270..350, met inkeping voor de schijf
        mes = Part.makeBox(xm1 - xm0, 10, 80, V(xm0, -10, 270))
        mes = mes.cut(Part.makeBox(xs1 - xs0 + 2, 14, 33, V(xs0 - 1, -12, 269)))
        for xb in (xm0 + 25, xs0 - 25):
            mes = mes.cut(Part.makeCylinder(6.5, 14, V(xb, -12, 295), V(0, 1, 0)))
        for sh, nm, kl in ((sch, "Schoep_8mm_%d", GEEL), (mes, "Mes_%dmm_Hardox_%%d" % P["geul_b"], ZILVER)):
            sh.rotate(V(0, 0, 0), V(1, 0, 0), hoek)
            sh.translate(V(0, Hy, Hz))
            tool(nm % (i + 1), sh, kl)

    # as + lagers
    tool("As_D35", cyl_x(P["as_d"] / 2, xs0, 205 - xs0, Hy, Hz), ZILVER, grp="Aandrijving")
    xdp0, xdp1 = 120.0, 130.0            # draagplaat
    xk1 = 162.0                          # kettingkast band 130..162, deksel 162..168
    xk2 = 168.0
    tool("UCFL207_binnen", ucfl207(xdp0, -1, Hy, Hz), BLAUW, grp="Aandrijving")
    tool("UCFL207_buiten", ucfl207(xk2, 1, Hy, Hz), BLAUW, grp="Aandrijving")

    # ---------------- draagplaat 10 mm (hoofddeel, alleen rechte lijnen + bogen)
    dp_prof = hull2d(cirkel(H, 90) + cirkel(U, 85) + rect(-580, -400, 380, 470) + rect(-630, -560, 250, 380))
    dp = prism_yz(dp_prof, xdp0, xdp1 - xdp0)
    dp = dp.cut(cyl_x(26, xdp0 - 1, 12, Hy, Hz))
    dp = dp.cut(cyl_x(21, xdp0 - 1, 12, U[0], U[1]))
    for dz in (-65, 65):
        dp = dp.cut(cyl_x(8, xdp0 - 1, 12, Hy, Hz + dz))
    for dy in (-35, 35):
        for dz in (-35, 35):
            dp = dp.cut(cyl_x(4.5, xdp0 - 1, 12, U[0] + dy, U[1] + dz))
    tool("Draagplaat_10mm", dp, STAAL, grp="Frame")

    # ---------------- kettingkast: band 32 mm (gezet strip 3 mm) + deksel 6 mm
    r_k = pd(P["tand_motor"], P["ketting_steek"]) / 2 + 22
    band = prism_yz(stadium(H, r_k, U, r_k), xdp1, xk1 - xdp1).cut(
        prism_yz(stadium(H, r_k - 3, U, r_k - 3), xdp1 - 1, xk1 - xdp1 + 2))
    tool("Kettingkast_band_3mm", band, GEEL, transp=50, grp="Aandrijving")
    dek = prism_yz(stadium(H, r_k, U, r_k), xk1, xk2 - xk1).cut(cyl_x(26, xk1 - 1, 10, Hy, Hz))
    tool("Kettingkast_deksel_6mm", dek, GEEL, transp=50, grp="Aandrijving")
    xw = 140.0
    tool("Kettingwiel_08B_Z%d_schijf" % P["tand_as"],
         sprocket(P["tand_as"], P["ketting_steek"], xw, 7.2, Hy, Hz, P["as_d"]), ZILVER, grp="Aandrijving")
    tool("Kettingwiel_08B_Z%d_motor" % P["tand_motor"],
         sprocket(P["tand_motor"], P["ketting_steek"], xw, 7.2, U[0], U[1], 20), ZILVER, grp="Aandrijving")
    r1 = pd(P["tand_as"], P["ketting_steek"]) / 2
    r2 = pd(P["tand_motor"], P["ketting_steek"]) / 2
    ket = prism_yz(stadium(H, r1 + 6, U, r2 + 6), xw - 2, 11.2).cut(
        prism_yz(stadium(H, r1 - 4, U, r2 - 4), xw - 3, 13.2))
    tool("Ketting_08B-1", ket, ZWART, grp="Aandrijving")

    # ---------------- motor: BLDC 48V 1,5 kW + planetaire kast i=10, links op draagplaat
    kast = Part.makeBox(100, 90, 90, V(xdp0 - 100, U[0] - 45, U[1] - 45))
    mot = cyl_x(55, xdp0 - 100 - 170, 170, U[0], U[1])
    mot = mot.fuse(kast).fuse(Part.makeBox(60, 50, 30, V(xdp0 - 230, U[0] - 25, U[1] + 50)))
    tool("BLDC_48V_1500W_planetair_i10", mot, ZWART, grp="Aandrijving")
    tool("Motoras_D20", cyl_x(10, xdp0, xw + 8 - xdp0, U[0], U[1]), ZILVER, grp="Aandrijving")

    # ---------------- kap: 3 mm, gezet in segmenten van 15°, rechterwand, links open
    rk = R_tip + 33
    seg = [(Hy + rk * math.cos(math.radians(a)), Hz + rk * math.sin(math.radians(a))) for a in range(15, 166, 15)]
    w = Part.makePolygon([V(xm0 - 20, y, z) for (y, z) in seg])
    kap = Part.Face(w.makeOffset2D(1.5, 0, False, False)).extrude(V(xs1 + 10 - (xm0 - 20) + 3, 0, 0))
    ring = []
    for a in range(15, 166, 15):
        ring.append((Hy + rk * math.cos(math.radians(a)), Hz + rk * math.sin(math.radians(a))))
    for a in range(165, 14, -15):
        ring.append((Hy + (rs + 8) * math.cos(math.radians(a)), Hz + (rs + 8) * math.sin(math.radians(a))))
    zw = prism_yz(ring, xs1 + 10, 3)
    tool("Kap_3mm_gezet", kap.fuse(zw).removeSplitter(), ORANJE, transp=35, grp="Frame")
    for a in (50, 130):
        yb = Hy + (rk - 20) * math.cos(math.radians(a))
        zb = Hz + (rk - 20) * math.sin(math.radians(a))
        tool("Kapsteun_40x8", Part.makeBox(xdp0 - (xs1 + 13), 40, 8, V(xs1 + 13, yb - 20, zb - 4)), GALV, grp="Frame")
    # werpklep links achter (verstelbaar met 1 bout)
    tool("Werpklep_3mm", prism_yz([(Hy - 200, Hz + 300), (Hy - 330, Hz + 230), (Hy - 330, Hz + 120), (Hy - 260, Hz + 140)],
                                  xm0 - 25, 3), ORANJE, transp=35, grp="Frame")

    # ---------------- arm 60x60x4 + scharnierbus, gelast aan draagplaat
    xa0, xa1 = 130.0, 190.0
    tool("Arm_60x60x4", koker_y(xa0, -580, 580 - 130, S[1] - 30, 60, 60, 4), STAAL, grp="Frame")
    tool("Scharnierbus_42.4x5", cyl_x(21.2, -198, 396, S[0], S[1]).cut(cyl_x(13, -200, 400, S[0], S[1])), STAAL, grp="Frame")
    # actuatoroog: 2 lipjes 8 mm met sleufgat (zweefstand 40 mm)
    ao = P["act_onder"]
    for xl in (xa0 + 12, xa1 - 20):
        lip = prism_yz([(ao[0] - 45, S[1] + 30), (ao[0] + 45, S[1] + 30), (ao[0] + 25, ao[1] + 25), (ao[0] - 25, ao[1] + 25)], xl, 8)
        sl = cyl_x(6.5, xl - 1, 10, ao[0], ao[1]).fuse(cyl_x(6.5, xl - 1, 10, ao[0], ao[1] - 20)).fuse(
            Part.makeBox(10, 13, 20, V(xl - 1, ao[0] - 6.5, ao[1] - 20)))
        tool("Actuatorlip_8mm_sleuf", lip.cut(sl), STAAL, grp="Frame")

    # ---------------- glijslof (diepte-instelling) rechts naast de geul
    dz_slof = -(200.0 - P["diepte"])     # slof zakt t.o.v. gereedschap bij minder diepte
    hz = Part.makeBox(10, 50, 330, V(xdp1, -620, 50))
    for k in range(6):
        hz = hz.cut(Part.makeCylinder(6.5, 12, V(xdp1 - 1, -595, 260 + 22 * k), V(1, 0, 0)))
    hz.translate(V(0, 0, dz_slof))
    tool("Slofhouder_50x10_gatenrij", hz, GALV, grp="Diepte")
    slof = prism_yz([(-700, 0), (-470, 0), (-420, 60), (-410, 54), (-464, 8), (-700, 8)], xdp1, 70)
    slof.translate(V(0, 0, dz_slof))
    tool("Glijslof_8mm", slof, GALV, grp="Diepte")
    for k in (2, 4):
        b = Part.makeCylinder(6, 40, V(xdp1 - 20, -595, 260 + 22 * k), V(1, 0, 0))
        tool("Bout_M12_slof", b, ZILVER, grp="Diepte")

    # ---------------- bok op robot (vast)
    xb = 200.0
    fp = Part.makeBox(2 * (xb + 10), 8, 260, V(-xb - 10, -8, 360))
    for xu in (-120, 120):
        for zu in (494, 566):
            fp = fp.cut(Part.makeCylinder(6.5, 12, V(xu, -10, zu), V(0, 1, 0)))
    fix("Bok_voorplaat_8mm", fp)
    bok_prof = [(-8, 360), (-170, 360), (-170, 480), (-160, 1000), (-80, 1000), (-8, 620)]
    for side, x0 in (("L", -xb - 10), ("R", xb)):
        pl = prism_yz(bok_prof, x0, 10)
        pl = pl.cut(cyl_x(12.7, x0 - 1, 12, S[0], S[1]))
        pl = pl.cut(cyl_x(12.7, x0 - 1, 12, P["act_boven"][0], P["act_boven"][1]))
        fix("Bok_zijplaat_10mm_%s" % side, pl)
    fix("Bok_dwarsbuis_boven_42.4", cyl_x(21.2, -xb, 2 * xb, *P["act_boven"]).cut(cyl_x(13, -xb - 1, 2 * xb + 2, *P["act_boven"])))
    fix("Scharnierpen_D25", cyl_x(12.5, -xb - 25, 2 * xb + 50, S[0], S[1]), ZILVER)
    fix("Pen_D25_boven", cyl_x(12.5, -xb - 25, 2 * xb + 50, *P["act_boven"]), ZILVER)
    for xu in (-120, 120):           # beugelbouten M12 om de robotbalk
        u = Part.makeCylinder(6, 100, V(xu, -30, 494), V(0, 1, 0)).fuse(
            Part.makeCylinder(6, 100, V(xu, -30, 566), V(0, 1, 0))).fuse(
            Part.makeCylinder(6, 84, V(xu, 70, 488), V(0, 0, 1)))
        fix("Beugelbout_M12", u, ZILVER)
    fix("Hoeksensor_scharnier", cyl_x(22, -xb - 45, 35, S[0], S[1]), BLAUW, grp="Elektra")
    fix("Controller_BLDC_+_actuator_IP65", Part.makeBox(60, 160, 140, V(xb + 10, -175, 640)), (0.15, 0.15, 0.17), grp="Elektra")

    # referentie robot
    fix("Robot_achterbalk_REF", koker_x(-800, 1600, 0, 500, 60, 60, 3), (0.45, 0.30, 0.20), 60, "Referentie_robot")
    for xr in (-800, 740):
        fix("Robot_langsbalk_REF", koker_y(xr, 0, 1200, 500, 60, 60, 3), (0.45, 0.30, 0.20), 60, "Referentie_robot")

    # ---------------- stand: draai gereedschap om scharnier naar gewenste diepte
    def hub_z(h):
        return rot(H, S, h)[1]
    doel = Hz + (200.0 - P["diepte"])
    lo, hi = -40.0, 5.0
    for _ in range(60):
        m = (lo + hi) / 2
        if hub_z(m) > doel:
            lo = m
        else:
            hi = m
    hoek = (lo + hi) / 2

    groups = {}

    def grp(n):
        if n not in groups:
            groups[n] = doc.addObject("App::DocumentObjectGroup", n)
        return groups[n]

    def add(name, shape, rgb, transp, g):
        o = doc.addObject("Part::Feature", name)
        o.Shape = shape
        try:
            o.ViewObject.ShapeColor = rgb
            o.ViewObject.Transparency = transp
        except Exception:
            pass
        grp(g).addObject(o)
        return o

    def draai(sh):
        sh = sh.copy()
        sh.rotate(V(0, S[0], S[1]), V(1, 0, 0), hoek)
        return sh
    # glijslof na draaien precies op maaiveld zetten (= gatenrij-instelling)
    dz_corr = -draai([t[1] for t in gereedschap if t[0] == "Glijslof_8mm"][0]).BoundBox.ZMin
    for (n, sh, kl, tr, g) in gereedschap:
        sh = draai(sh)
        if g == "Diepte":
            sh.translate(V(0, 0, dz_corr))
        add(n, sh, kl, tr, g)
    for (n, sh, kl, tr, g) in vast:
        add(n, sh, kl, tr, g)

    # actuator tussen bovenpen en onderste oog (midden sleuf)
    ab = P["act_boven"]
    ao_w = rot((ao[0], ao[1] - 10), S, hoek)
    pa, pb = V(160, ab[0], ab[1]), V(160, ao_w[0], ao_w[1])
    d = pb - pa
    L = d.Length
    d.normalize()
    body = Part.makeCylinder(30, 330, pa, d)
    stang = Part.makeCylinder(10, L, pa, d)
    add("Lineaire_actuator_6000N_slag200", body.fuse(stang), (0.3, 0.3, 0.32), 0, "Bok")

    doc.recompute()

    # actuatorlengtes
    def act_len(h):
        q = rot(ao, S, h)
        return math.hypot(q[0] - ab[0], q[1] - ab[1])
    # heffen tot 150 mm vrij boven maaiveld
    lo2, hi2 = -60.0, 0.0
    for _ in range(60):
        m = (lo2 + hi2) / 2
        if hub_z(m) - R_tip < 150:
            hi2 = m
        else:
            lo2 = m
    info = dict(hoek_werk=hoek, hoek_hef=lo2, L_diep=act_len(0), L_werk=act_len(hoek), L_hef=act_len(lo2))
    return doc, info


def rekenwerk(doc, info):
    n_as = P["motor_rpm"] / P["i_kast"] * P["tand_motor"] / P["tand_as"]
    T_as = P["motor_P"] / (2 * math.pi * P["motor_rpm"] / 60) * P["i_kast"] * 0.92
    v_tip = math.pi * P["tip_D"] / 1000 * n_as / 60
    F_tip = T_as / (P["tip_D"] / 2000)
    A = P["geul_b"] / 1000 * P["diepte"] / 1000
    v = P["rijsnelheid"] / 60
    hap = v * 1000 / (n_as / 60 * P["n_schoep"])
    massa = 12.0 + 5.0 + 2 * 2.6       # koopdelen: motor+kast, actuator, 2x UCFL207 (catalogus, ca.)
    for o in doc.Objects:
        if (hasattr(o, "Shape") and o.TypeId == "Part::Feature" and "REF" not in o.Name
                and not o.Name.startswith(("BLDC", "Lineaire", "UCFL", "Controller", "Hoeksensor"))):
            massa += o.Shape.Volume * 7.85e-6
    print("=== Geulfrees Bruut - kengetallen ===")
    print("Schijf %.0f rpm, tipsnelheid %.1f m/s, askoppel %.0f Nm, tipkracht %.0f N" % (n_as, v_tip, T_as, F_tip))
    print("Geul %.0f x %.0f mm: %.4f m3/m, bij %.1f m/min = %.3f m3/min" % (P["geul_b"], P["diepte"], A, P["rijsnelheid"], A * P["rijsnelheid"]))
    for e in (200e3, 500e3):
        print("  specifieke snij-energie %.0f kJ/m3 -> vermogen %.0f W" % (e / 1e3, e * A * v))
    print("Hap per mes %.1f mm, 20 m geul in %.1f min" % (hap, 20 / P["rijsnelheid"]))
    print("Massa ca. %.0f kg (staaldelen uit model + koopdelen)" % massa)
    print("Armhoek werkstand %.1f deg, heffen %.1f deg" % (info["hoek_werk"], info["hoek_hef"]))
    print("Actuator pen-pen: max diepte %.0f, werk %.0f, geheven %.0f -> slag %.0f mm (+40 sleuf)"
          % (info["L_diep"], info["L_werk"], info["L_hef"], info["L_diep"] - info["L_hef"]))


if __name__ == "__main__" or True:
    _doc, _info = build()
    rekenwerk(_doc, _info)
    _doc.saveAs(MAP + "trencher_bruut.FCStd")
    import Import
    Import.export([o for o in _doc.Objects if hasattr(o, "Shape") and o.TypeId == "Part::Feature"
                   and "REF" not in o.Name], MAP + "trencher_bruut.step")
    try:
        import FreeCADGui as Gui
        Gui.ActiveDocument.ActiveView.viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass
