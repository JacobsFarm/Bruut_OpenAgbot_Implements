# -*- coding: utf-8 -*-
"""
Voervijzel - ONTWERP 2: zo eenvoudig en goedkoop mogelijk te fabriceren.

Uitgangspunten t.o.v. ontwerp 1:
  * Alle plaatdelen uit slechts 2 diktes (6 mm en 3 mm), alleen rechte snijlijnen
    -> laser/plasma in één bestelling, of zelf met plasma/slijptol.
  * Linker en rechter zijplaat IDENTIEK (1 tekening, 2 stuks). De motorsteun is een
    losse geboute plaat.
  * Kap = één vlakke plaat 3 mm met 4 zetten op de kantbank (geen walsen).
  * Vijzelblad = sectionele bladen (vlakke ringen, ingezaagd en uitgetrokken tot 1 spoed),
    of kant-en-klaar gekocht. Geen geperste/gesweepte helix nodig.
  * Eén kokerprofiel (50x50x3) voor dwarsligger en armen.
  * Armen met beugelbouten (U-bouten) op dwarsligger én op de robot:
    niets lassen of boren aan het robotframe, breedte/positie verstelbaar.
  * Lassen beperkt tot: blad op kernbuis, 2 kopplaten op de dwarsligger.
  * Standaard koopdelen: 2x UCFL206 (2-gats flenslager), ketting 08B-1 + 2 wielen.

Uitvoeren in FreeCAD:
    exec(open(r"F:/veldrobot/aanbouwdelen/voervijzel/simpel/voervijzel_ontwerp_v2_goedkoop.py", encoding="utf-8").read())
Assen: X = breedte (0 = midden), Y = rijrichting (+Y = voor), Z = omhoog (0 = vloer). Maten in mm.
"""
import math
import os
import FreeCAD as App
import Part

V = App.Vector
MAP = r"F:/veldrobot/aanbouwdelen/voervijzel/simpel/"

P = dict(
    as_d=30.0,
    as_hoogte=185.0,
    blad_D=320.0,
    blad_spoed=260.0,
    blad_t=4.0,
    blad_L=1400.0,
    kern_D=60.3,
    kern_t=4.0,
    binnenmaat=1440.0,
    zij_t=6.0,
    kap_t=3.0,
    koker=50.0,
    koker_t=3.0,
    tand_motor=15,
    tand_as=30,
    ketting_steek=12.7,
    motor_Y=-60.0,
    motor_Z=500.0,
    motor_rpm=150.0,
    motor_P=400.0,
)

STAAL = (0.22, 0.24, 0.26)
GEEL = (0.95, 0.70, 0.05)
ZWART = (0.08, 0.08, 0.08)
BLAUW = (0.10, 0.20, 0.45)
ZILVER = (0.75, 0.75, 0.78)
GALV = (0.62, 0.66, 0.68)


# ------------------------------------------------------------------ hulpfuncties
def pd(z, p):
    return p / math.sin(math.pi / z)


def add(doc, name, shape, rgb=STAAL, transp=0, group=None):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    try:
        o.ViewObject.ShapeColor = rgb
        o.ViewObject.Transparency = transp
    except Exception:
        pass
    if group is not None:
        group.addObject(o)
    return o


def face_yz(points, x0=0.0):
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


def prism_yz(points, x0, thickness):
    return face_yz(points, x0).extrude(V(thickness, 0, 0))


def cyl_x(r, x0, length, y=0.0, z=0.0):
    return Part.makeCylinder(r, length, V(x0, y, z), V(1, 0, 0))


def hull2d(pts):
    pts = sorted(set(pts))

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


def stadium(c1, r1, c2, r2):
    pts = []
    for k in range(72):
        a = 2 * math.pi * k / 72
        pts.append((c1[0] + r1 * math.cos(a), c1[1] + r1 * math.sin(a)))
        pts.append((c2[0] + r2 * math.cos(a), c2[1] + r2 * math.sin(a)))
    return hull2d(pts)


def sprocket(z_teeth, p, x0, width, y, zc, bore):
    d_p = pd(z_teeth, p)
    d_roll = 8.51
    body = cyl_x((d_p + 0.6 * d_roll) / 2, x0, width, y, zc)
    for i in range(z_teeth):
        a = 2 * math.pi * i / z_teeth
        body = body.cut(cyl_x(d_roll / 2 + 0.1, x0 - 1, width + 2,
                              y + d_p / 2 * math.cos(a), zc + d_p / 2 * math.sin(a)))
    body = body.fuse(cyl_x(min(d_p * 0.35, 30), x0 - 18, 18, y, zc)).removeSplitter()
    return body.cut(cyl_x(bore / 2, x0 - 20, width + 40, y, zc))


def ucfl206(x_face, s, y, z):
    """UCFL206: ovale 2-gats flens, L=148, J=117 (M12), flens 14, bouten horizontaal (in Y)."""
    L, J, H, tf = 148.0, 117.0, 83.0, 14.0
    x0 = x_face if s > 0 else x_face - tf
    pts = []
    for k in range(73):        # ovaal = omhulsel van 2 eindcirkels + middencirkel
        a = 2 * math.pi * k / 72
        pts.append((y - J / 2 + 15.5 * math.cos(a), z + 15.5 * math.sin(a)))
        pts.append((y + J / 2 + 15.5 * math.cos(a), z + 15.5 * math.sin(a)))
        pts.append((y + H / 2 * math.cos(a), z + H / 2 * math.sin(a)))
    fl = prism_yz(hull2d(pts), x0, tf)
    boss = cyl_x(40, x_face + s * tf if s > 0 else x_face - tf - 24, 24, y, z)
    ring = cyl_x(24, x_face - 6 if s > 0 else x_face - tf - 32, 44, y, z)
    h = fl.fuse(boss).fuse(ring).removeSplitter()
    for dy in (-J / 2, J / 2):
        h = h.cut(cyl_x(7, x0 - 1, tf + 2, y + dy, z))
    return h.cut(cyl_x(15.2, x_face - 60, 120, y, z))


def koker_x(x0, length, y0, z0, b, t):
    return Part.makeBox(length, b, b, V(x0, y0, z0)).cut(
        Part.makeBox(length + 2, b - 2 * t, b - 2 * t, V(x0 - 1, y0 + t, z0 + t)))


def koker_y(x0, y0, length, z0, b, t):
    return Part.makeBox(b, length, b, V(x0, y0, z0)).cut(
        Part.makeBox(b - 2 * t, length + 2, b - 2 * t, V(x0 + t, y0 - 1, z0 + t)))


def kruisklem(xa, ba, y0, bl, z_onder, h_stapel, d=10.0):
    """Kruisverbinding: arm (in Y, breedte ba, op x=xa) ligt bovenop een balk in X
    (y0..y0+bl, onderkant z_onder). 2 vierkante beugelbouten M10 om de onderste balk,
    poten naast de arm omhoog door een klemplaat 8 mm bovenop de arm."""
    r = d / 2
    z_top = z_onder + h_stapel
    delen = []
    for xc in (xa - r - 2, xa + ba + r + 2):
        for yy in (y0 - r - 1, y0 + bl + r + 1):
            delen.append(Part.makeCylinder(r, h_stapel + r + 8 + 18, V(xc, yy, z_onder - r), V(0, 0, 1)))
        delen.append(Part.makeCylinder(r, bl + 2 * r + 2, V(xc, y0 - r - 1, z_onder - r), V(0, 1, 0)))
    plaat = Part.makeBox(ba + 4 * r + 30, bl + 4 * r + 10, 8,
                         V(xa - 2 * r - 15, y0 - 2 * r - 5, z_top))
    delen.append(plaat)
    s = delen[0]
    for p_ in delen[1:]:
        s = s.fuse(p_)
    return s


# ------------------------------------------------------------------ ontwerp
def build(doc_name="Voervijzel_v2"):
    if doc_name in App.listDocuments():
        App.closeDocument(doc_name)
    doc = App.newDocument(doc_name)
    zs = P["as_hoogte"]
    xi = P["binnenmaat"] / 2
    xo = xi + P["zij_t"]
    b, tk = P["koker"], P["koker_t"]

    g_v = doc.addObject("App::DocumentObjectGroup", "Vijzel")
    g_f = doc.addObject("App::DocumentObjectGroup", "Frame_plaatwerk")
    g_a = doc.addObject("App::DocumentObjectGroup", "Aandrijving")
    g_l = doc.addObject("App::DocumentObjectGroup", "Lagering")
    g_b = doc.addObject("App::DocumentObjectGroup", "Bevestiging_robot")
    g_r = doc.addObject("App::DocumentObjectGroup", "Referentie_robot")

    # ---------------- as + kernbuis + sectionele bladen
    x_wiel = -xo - 14 - 24 - 30
    x_as_l = x_wiel - 30
    x_as_r = xo + 14 + 24 + 12
    as_ = cyl_x(P["as_d"] / 2, x_as_l, x_as_r - x_as_l, 0, zs)
    as_ = as_.cut(Part.makeBox(45, 8, 4, V(x_as_l + 3, -4, zs + P["as_d"] / 2 - 4)))
    add(doc, "As_D30_blank_getrokken", as_, ZILVER, group=g_v)

    Lb = P["blad_L"]
    kern = cyl_x(P["kern_D"] / 2, -Lb / 2, Lb, 0, zs).cut(
        cyl_x(P["kern_D"] / 2 - P["kern_t"], -Lb / 2 - 1, Lb + 2, 0, zs))
    for xe in (-Lb / 2, Lb / 2 - 8):   # ingelaste ringschijf Ø30 H8 (laser, 8 mm)
        kern = kern.fuse(cyl_x(P["kern_D"] / 2 - P["kern_t"], xe, 8, 0, zs).cut(
            cyl_x(P["as_d"] / 2 + 0.1, xe - 1, 10, 0, zs)))
    gaten = [Part.makeCylinder(5.25, 80, V(xe, 0, zs - 40), V(0, 0, 1)) for xe in (-Lb / 2 + 30, Lb / 2 - 30)]
    for g in gaten:
        kern = kern.cut(g)
    add(doc, "Kernbuis_60.3x4", kern, GEEL, group=g_v)
    for i, g in enumerate(gaten):
        add(doc, "Bout_M10_%s" % ("breekbout_8.8" if i == 0 else "10.9"),
            Part.makeCylinder(5, 76, V(g.BoundBox.Center.x, 0, zs - 38), V(0, 0, 1)), ZILVER, group=g_v)

    # sectionele bladen: elk 1 spoed, uit vlakke ring getrokken
    r_in, r_out, t, S = P["kern_D"] / 2, P["blad_D"] / 2, P["blad_t"], P["blad_spoed"]
    lengte = Lb - 20
    n_vol = int(lengte // S)
    rest = lengte - n_vol * S
    prof = Part.makePolygon([V(r_in - 0.3, 0, -t / 2), V(r_out, 0, -t / 2),
                             V(r_out, 0, t / 2), V(r_in - 0.3, 0, t / 2), V(r_in - 0.3, 0, -t / 2)])

    def sectie(h):
        sh = Part.Wire(Part.makeHelix(S, h, r_out)).makePipeShell([prof], True, True)
        return sh if sh.ShapeType == "Solid" else Part.Solid(sh)
    vol = sectie(S - 0.5)                          # 0.5 mm = lasnaad tussen secties
    hoogtes = [S] * n_vol + ([rest] if rest > 20 else [])
    for i, h in enumerate(hoogtes):
        s_ = vol.copy() if h == S else sectie(h)
        s_.translate(V(0, 0, i * S))
        s_.rotate(V(0, 0, 0), V(0, 1, 0), 90)
        s_.translate(V(-lengte / 2, 0, zs))
        add(doc, "Bladsectie_%d" % (i + 1), s_, GEEL, group=g_v)

    # ---------------- zijplaten: identiek L en R, alleen rechte snijlijnen
    prof_zij = [(-265, 10), (-110, 10), (-60, 100), (70, 100), (205, 235),
                (205, 260), (120, 390), (-265, 390)]
    bout_kap = [(-182, 60), (-182, 280), (-30, 362), (118, 318)]     # haakjes kap
    bout_lig = [(-230, 275), (-230, 375)]                           # kopplaat dwarsligger
    bout_mot = [(-110, 270), (-10, 270), (-110, 360), (-10, 360)]   # motorsteun
    for side, x0 in (("L", -xo), ("R", xi)):
        pl = prism_yz(prof_zij, x0, P["zij_t"])
        pl = pl.cut(cyl_x(22, x0 - 1, 10, 0, zs))
        for dy in (-58.5, 58.5):
            pl = pl.cut(cyl_x(6.6, x0 - 1, 10, dy, zs))
        for (yy, zz) in bout_kap + bout_lig + bout_mot:
            pl = pl.cut(cyl_x(5.5 if (yy, zz) in bout_kap else 6.6, x0 - 1, 10, yy, zz))
        add(doc, "Zijplaat_%s_6mm_identiek" % side, pl, STAAL, group=g_f)

    # ---------------- kap: 1 plaat 3 mm, 4 zetten (kantbank), hartlijn-profiel
    hart = [(-195, 40), (-195, 300), (-120, 375), (110, 375), (190, 240), (205, 215)]
    w = Part.makePolygon([V(-xi, y, z) for (y, z) in hart])
    kapf = Part.Face(w.makeOffset2D(P["kap_t"] / 2, 0, False, False))
    kap = kapf.extrude(V(2 * xi, 0, 0))
    add(doc, "Kap_3mm_gezet", kap, STAAL, transp=40, group=g_f)
    # zethoekjes 40x40x3 (4 per zijde) om de kap aan de zijplaat te bouten
    for side, xh in (("L", -xi), ("R", xi - 40)):
        for k, (yy, zz) in enumerate(bout_kap):
            add(doc, "Hoekje_kap_%s%d" % (side, k + 1),
                Part.makeBox(40, 20, 20, V(xh, yy - 10, zz - 10)), GALV, group=g_f)

    # rubber flap met klemstrip achter onder
    add(doc, "Rubberflap_10mm", Part.makeBox(2 * xi, 10, 80, V(-xi, -206.5, 5)), ZWART, group=g_f)
    add(doc, "Klemstrip_30x5", Part.makeBox(2 * xi, 5, 30, V(-xi, -211.5, 45)), GALV, group=g_f)

    # PE glijsloffen (zelfde blok L/R)
    for x0 in (-xo - 7, xi - 7):
        add(doc, "Glijslof_PE1000", Part.makeBox(P["zij_t"] + 14, 150, 10, V(x0, -260, 0)),
            (0.92, 0.92, 0.88), group=g_f)

    # ---------------- dwarsligger: koker 50x50x3 + 2 kopplaten 6 mm (enige laswerk frame)
    yl, zl = -255.0, 300.0
    add(doc, "Dwarsligger_50x50x3", koker_x(-xi + 6, 2 * xi - 12, yl, zl, b, tk), STAAL, group=g_b)
    for xk in (-xi, xi - 6):
        kp = Part.makeBox(6, 60, 130, V(xk, -260, 258))
        for (yy, zz) in bout_lig:
            kp = kp.cut(cyl_x(6.6, xk - 1, 8, yy, zz))
        add(doc, "Kopplaat_6mm", kp, STAAL, group=g_b)

    # ---------------- armen: koker 50x50x3, recht afgezaagd, U-bouten
    y_robot = -470.0           # aanname: voorste dwarsbalk robot (60x40) ligt hier
    for i, xa in enumerate((-420.0, 370.0)):
        arm = koker_y(xa, -560, 560 - 205, zl + b, b, tk)
        add(doc, "Arm_50x50x3_%d" % (i + 1), arm, STAAL, group=g_b)
        add(doc, "Kruisklem_ligger_%d" % (i + 1), kruisklem(xa, b, yl, b, zl, 2 * b), GALV, group=g_b)
        add(doc, "Kruisklem_robot_%d" % (i + 1),
            kruisklem(xa, b, y_robot, 60, zl + b - 60, 60 + b), GALV, group=g_b)

    # referentie: voorste dwarsbalk robot (alleen ter oriëntatie)
    rb = koker_x(-800, 1600, y_robot, zl + b - 60, 60, 3)
    add(doc, "Robot_dwarsbalk_REF", rb, (0.45, 0.30, 0.20), transp=60, group=g_r)

    # ---------------- lagers UCFL206
    for side, xf, s in (("L", -xo, -1), ("R", xo, 1)):
        add(doc, "UCFL206_%s" % side, ucfl206(xf, s, 0, zs), BLAUW, group=g_l)

    # ---------------- aandrijving
    my, mz = P["motor_Y"], P["motor_Z"]
    add(doc, "Kettingwiel_08B_Z%d" % P["tand_as"],
        sprocket(P["tand_as"], P["ketting_steek"], x_wiel, 7.2, 0, zs, P["as_d"]), ZILVER, group=g_a)
    add(doc, "Kettingwiel_08B_Z%d" % P["tand_motor"],
        sprocket(P["tand_motor"], P["ketting_steek"], x_wiel, 7.2, my, mz, 25), ZILVER, group=g_a)
    r1 = pd(P["tand_as"], P["ketting_steek"]) / 2
    r2 = pd(P["tand_motor"], P["ketting_steek"]) / 2
    ket = prism_yz(stadium((0, zs), r1 + 6, (my, mz), r2 + 6), x_wiel - 2, 11.2).cut(
        prism_yz(stadium((0, zs), r1 - 4, (my, mz), r2 - 4), x_wiel - 3, 13.2))
    add(doc, "Ketting_08B-1", ket, ZWART, group=g_a)

    # motorsteun: vlakke plaat 6 mm, buitenop linker zijplaat geboute, sleufgaten voor spanning
    ms_x0 = -xo - P["zij_t"]
    ms = prism_yz([(-150, 230), (30, 230), (30, mz + 80), (-150, mz + 80)], ms_x0, P["zij_t"])
    for (yy, zz) in bout_mot:
        ms = ms.cut(cyl_x(6.6, ms_x0 - 1, 10, yy, zz))
    for dy in (-50, 50):
        for dz in (-50, 50):
            sl = Part.makeBox(10, 13, 20, V(ms_x0 - 1, my + dy - 6.5, mz + dz - 10))
            sl = sl.fuse(cyl_x(6.5, ms_x0 - 1, 10, my + dy, mz + dz - 10))
            sl = sl.fuse(cyl_x(6.5, ms_x0 - 1, 10, my + dy, mz + dz + 10))
            ms = ms.cut(sl)
    ms = ms.cut(Part.makeBox(10, 50, 50, V(ms_x0 - 1, my - 25, mz - 25)))
    add(doc, "Motorsteun_6mm", ms, STAAL, group=g_a)

    # kettingkast: 1.5 mm, deksel + omgezette rand (gezet), 2 bouten
    kx1 = x_wiel - 14
    kx0 = -xo - P["zij_t"] - 2
    k_o = prism_yz(stadium((0, zs), r1 + 38, (my, mz), r2 + 38), kx1, kx0 - kx1)
    k_i = prism_yz(stadium((0, zs), r1 + 36.5, (my, mz), r2 + 36.5), kx1 + 1.5, kx0 - kx1)
    add(doc, "Kettingkast_1.5mm", k_o.cut(k_i), GEEL, transp=55, group=g_a)

    gb = Part.makeBox(110, 130, 130, V(-xo, my - 65, mz - 65))
    motor = gb.fuse(cyl_x(55, -xo + 110, 230, my, mz)).fuse(cyl_x(45, -xo + 340, 25, my, mz)).fuse(
        Part.makeBox(60, 70, 40, V(-xo + 200, my - 35, mz + 50)))
    add(doc, "Tandwielmotor_24V_400W", motor, ZWART, group=g_a)
    add(doc, "Motoras_D25", cyl_x(12.5, x_wiel - 22, -xo - x_wiel + 22, my, mz), ZILVER, group=g_a)

    doc.recompute()
    return doc, prof_zij, hart


# ------------------------------------------------------------------ werkplaatsgegevens
def plaatgegevens(prof_zij, hart):
    D, d, S = P["blad_D"], P["kern_D"], P["blad_spoed"]
    Lo = math.hypot(math.pi * D, S)
    Li = math.hypot(math.pi * d, S)
    bb = (D - d) / 2
    r = bb * Li / (Lo - Li)
    R = r + bb
    hoek = 360.0 * (1 - Lo / (2 * math.pi * R))
    ontw = sum(math.hypot(hart[i + 1][0] - hart[i][0], hart[i + 1][1] - hart[i][1]) for i in range(len(hart) - 1))
    lengte = P["blad_L"] - 20
    n = math.ceil(lengte / S)

    zs_rpm = P["motor_rpm"] * P["tand_motor"] / P["tand_as"]
    T_as = P["motor_P"] / (2 * math.pi * P["motor_rpm"] / 60) * P["tand_as"] / P["tand_motor"] * 0.95
    a = math.hypot(P["motor_Y"], P["motor_Z"] - P["as_hoogte"])
    p, z1, z2 = P["ketting_steek"], P["tand_motor"], P["tand_as"]
    X = 2 * a / p + (z1 + z2) / 2 + ((z2 - z1) / (2 * math.pi)) ** 2 * p / a

    print("=== Ontwerp 2 (goedkoop) - werkplaatsgegevens ===")
    print("Vlakke ring per bladsectie : buiten Ø%.0f  binnen Ø%.0f  (t=%.0f), %d stuks" % (2 * R, 2 * r, P["blad_t"], n))
    print("  ring 1x radiaal inzagen, segment van %.1f° eruit, uittrekken tot spoed %.0f" % (hoek, S))
    print("Kap: plaat %.0f x %.0f x %.0f mm, 4 zetten" % (2 * (P["binnenmaat"] / 2), ontw, P["kap_t"]))
    print("Vijzel %.0f rpm, askoppel %.0f Nm, ketting %d schakels" % (zs_rpm, T_as, 2 * math.ceil(X / 2)))
    return dict(ring_R=R, ring_r=r, hoek=hoek)


def export_dxf(doc, prof_zij, ring):
    """2D snijcontouren (incl. gaten) voor laser/plasma."""
    try:
        import importDXF
    except Exception as e:
        print("DXF-export overgeslagen:", e)
        return
    tmp = []
    # zijplaat: doorsnede op halve dikte, plat gelegd (Y->X, Z->Y)
    zp = doc.getObject("Zijplaat_R_6mm_identiek").Shape
    sec = zp.slice(V(1, 0, 0), P["binnenmaat"] / 2 + P["zij_t"] / 2)
    m = App.Matrix(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
    vlak = Part.makeCompound([w.transformGeometry(m) for w in sec])
    o1 = doc.addObject("Part::Feature", "DXF_zijplaat")
    o1.Shape = vlak
    tmp.append(o1)
    # ring voor bladsectie, met zaagsnede-segment
    R, r, h = ring["ring_R"], ring["ring_r"], ring["hoek"]
    ringf = Part.makeCircle(R)
    o2 = doc.addObject("Part::Feature", "DXF_bladring")
    o2.Shape = Part.makeCompound([Part.makeCircle(R, V(0, 0, 0), V(0, 0, 1), 0, 360 - h),
                                  Part.makeCircle(r, V(0, 0, 0), V(0, 0, 1), 0, 360 - h),
                                  Part.makeLine(V(r, 0, 0), V(R, 0, 0)),
                                  Part.makeLine(V(r * math.cos(math.radians(360 - h)), r * math.sin(math.radians(360 - h)), 0),
                                                V(R * math.cos(math.radians(360 - h)), R * math.sin(math.radians(360 - h)), 0))])
    tmp.append(o2)
    for o in tmp:
        importDXF.export([o], MAP + "v2_%s.dxf" % o.Name.replace("DXF_", ""))
        doc.removeObject(o.Name)
    print("DXF: v2_zijplaat.dxf, v2_bladring.dxf")


if __name__ == "__main__" or True:
    _doc, _pz, _h = build()
    _ring = plaatgegevens(_pz, _h)
    export_dxf(_doc, _pz, _ring)
    _doc.recompute()
    _doc.saveAs(MAP + "voervijzel_v2_goedkoop.FCStd")
    import Import
    Import.export([o for o in _doc.Objects if hasattr(o, "Shape") and o.TypeId == "Part::Feature"
                   and not o.Name.startswith("Robot")], MAP + "voervijzel_v2_goedkoop.step")
