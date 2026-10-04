# -*- coding: utf-8 -*-
"""
Voervijzel (feed-pusher auger) - aanbouwdeel voorop de agbot / veldrobot.

Parametrisch FreeCAD-script. Uitvoeren in FreeCAD (Macro of via MCP):
    exec(open(r"F:/veldrobot/aanbouwdelen/voervijzel/advanced/voervijzel_ontwerp.py", encoding="utf-8").read())

Assenstelsel:
    X = over de breedte (as-richting), 0 = midden
    Y = rijrichting, +Y = voorkant (weg van de robot), robot zit aan -Y
    Z = omhoog, 0 = vloer
Alle maten in mm.
"""
import math
import FreeCAD as App
import Part

V = App.Vector

# ---------------------------------------------------------------- parameters
P = dict(
    # vijzel
    as_d=30.0,           # hoofdas C45, h9
    as_hoogte=185.0,     # hart as boven de vloer
    blad_D=320.0,        # buitendiameter vijzelblad
    blad_spoed=260.0,    # spoed
    blad_t=5.0,          # plaatdikte blad (S355)
    blad_L=1400.0,       # lengte beblading
    kern_D=60.3,         # kernbuis 60.3x4 (op as gepend)
    kern_t=4.0,
    # frame
    binnenmaat=1440.0,   # tussen de zijplaten
    zij_t=8.0,           # zijplaat dikte
    kap_R=188.0,         # binnenradius kap
    kap_t=3.0,
    kap_hoek_voor=20.0,  # graden, gemeten vanaf +Y richting +Z
    kap_hoek_achter=235.0,
    # aandrijving (08B-1 ketting, 1/2")
    tand_motor=15,
    tand_as=30,
    ketting_steek=12.7,
    motor_Y=-60.0,
    motor_Z=500.0,
    motor_rpm=150.0,     # uitgaand toerental haakse/inline tandwielmotor
    motor_P=400.0,       # W
)


def pd(z, p):
    """Steekcirkeldiameter kettingwiel."""
    return p / math.sin(math.pi / z)


def color(obj, rgb, transp=0):
    try:
        obj.ViewObject.ShapeColor = rgb
        obj.ViewObject.Transparency = transp
    except Exception:
        pass


def add(doc, name, shape, rgb=(0.3, 0.3, 0.3), transp=0, group=None):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    color(o, rgb, transp)
    if group is not None:
        group.addObject(o)
    return o


def prism_yz(points, x0, thickness):
    """Extrudeer een gesloten YZ-polygoon in +X vanaf x0."""
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    face = Part.Face(Part.makePolygon(pts))
    return face.extrude(V(thickness, 0, 0))


def fillet_x_edges(solid, radius, skip=()):
    """Rond de randen evenwijdig aan X af (de hoeken van het plaatprofiel)."""
    edges = []
    for e in solid.Edges:
        if isinstance(e.Curve, Part.Line):
            d = e.Vertexes[1].Point - e.Vertexes[0].Point
            if abs(d.y) < 1e-6 and abs(d.z) < 1e-6:
                mid = (e.Vertexes[0].Point + e.Vertexes[1].Point) * 0.5
                if not any((abs(mid.y - s[0]) < 1 and abs(mid.z - s[1]) < 1) for s in skip):
                    edges.append(e)
    try:
        return solid.makeFillet(radius, edges)
    except Exception:
        return solid


def cyl_x(r, x0, length, y=0.0, z=0.0):
    return Part.makeCylinder(r, length, V(x0, y, z), V(1, 0, 0))


def sprocket(z_teeth, p, x0, width, y, zc, bore):
    """Vereenvoudigd kettingwiel met tandvorm (rollen Ø8.51 voor 08B)."""
    d_p = pd(z_teeth, p)
    d_roll = 8.51
    d_out = d_p + 0.6 * d_roll
    body = cyl_x(d_out / 2, x0, width, y, zc)
    for i in range(z_teeth):
        a = 2 * math.pi * i / z_teeth
        cy = y + d_p / 2 * math.cos(a)
        cz = zc + d_p / 2 * math.sin(a)
        body = body.cut(cyl_x(d_roll / 2 + 0.1, x0 - 1, width + 2, cy, cz))
    hub = cyl_x(min(d_p * 0.35, 30), x0 - 18, 18, y, zc)
    body = body.fuse(hub).removeSplitter()
    return body.cut(cyl_x(bore / 2, x0 - 20, width + 40, y, zc))


def ucf206(x_face, direction, y, z):
    """UCF206 flenslager (vierkant 108, gatafstand 83, M12) - vereenvoudigd.
    x_face = plaatvlak waar de flens tegenaan zit, direction = +1/-1 (naar buiten)."""
    L, J, tf = 108.0, 83.0, 14.0
    s = direction
    x0 = x_face if s > 0 else x_face - tf
    flange = Part.makeBox(tf, L, L, V(x0, y - L / 2, z - L / 2))
    flange = fillet_x_edges(flange, 18)
    boss_x = x_face + s * tf if s > 0 else x_face - tf - 24
    boss = cyl_x(40, boss_x, 24, y, z)
    ring_x = x_face - 6 if s > 0 else x_face - tf - 32
    ring = cyl_x(24, ring_x, 44, y, z)  # binnenring + borgschroef-kraag
    h = flange.fuse(boss).fuse(ring).removeSplitter()
    for dy in (-J / 2, J / 2):
        for dz in (-J / 2, J / 2):
            h = h.cut(cyl_x(7, x0 - 1, tf + 2, y + dy, z + dz))
    h = h.cut(cyl_x(15.2, x_face - 60, 120, y, z))
    return h


def bolts_ucf(x_face, direction, y, z, through):
    """M12 bouten + moeren voor UCF206."""
    J = 83.0
    out = []
    for dy in (-J / 2, J / 2):
        for dz in (-J / 2, J / 2):
            if direction < 0:
                xs, xe = x_face - 14 - 8, x_face + through + 10
            else:
                xs, xe = x_face - through - 10, x_face + 14 + 8
            b = cyl_x(6, xs, xe - xs, y + dy, z + dz)
            head = Part.makePolygon([V(0, 9.2 * math.cos(math.radians(60 * k + 30)), 9.2 * math.sin(math.radians(60 * k + 30))) for k in range(7)])
            hf = Part.Face(head).extrude(V(8, 0, 0))
            hf.translate(V(xs - 8 if direction < 0 else xe, y + dy, z + dz))
            out.append(b.fuse(hf))
    return Part.makeCompound(out)


def build(doc_name="Voervijzel"):
    if doc_name in App.listDocuments():
        App.closeDocument(doc_name)
    doc = App.newDocument(doc_name)

    zs = P["as_hoogte"]
    xi = P["binnenmaat"] / 2          # binnenvlak zijplaat
    xo = xi + P["zij_t"]               # buitenvlak zijplaat

    g_vijzel = doc.addObject("App::DocumentObjectGroup", "Vijzel")
    g_frame = doc.addObject("App::DocumentObjectGroup", "Frame")
    g_aandr = doc.addObject("App::DocumentObjectGroup", "Aandrijving")
    g_lager = doc.addObject("App::DocumentObjectGroup", "Lagering")
    g_bev = doc.addObject("App::DocumentObjectGroup", "Bevestiging_robot")

    STAAL = (0.22, 0.24, 0.26)
    GEEL = (0.95, 0.70, 0.05)
    ZWART = (0.08, 0.08, 0.08)
    BLAUW = (0.10, 0.20, 0.45)
    ZILVER = (0.75, 0.75, 0.78)

    # ------------------------------------------------------------ as + vijzel
    x_as_l = -xo - 14 - 24 - 40 - 20   # tot voorbij kettingwiel
    x_as_r = xo + 14 + 24 + 12
    as_ = cyl_x(P["as_d"] / 2, x_as_l, x_as_r - x_as_l, 0, zs)
    # spiebaan 8x7 voor kettingwiel (DIN 6885)
    spie = Part.makeBox(45, 8, 4, V(x_as_l + 3, -4, zs + P["as_d"] / 2 - 4))
    as_ = as_.cut(spie)
    add(doc, "As_D30_C45", as_, ZILVER, group=g_vijzel)

    Lb = P["blad_L"]
    kern = cyl_x(P["kern_D"] / 2, -Lb / 2, Lb, 0, zs).cut(
        cyl_x(P["kern_D"] / 2 - P["kern_t"], -Lb / 2 - 1, Lb + 2, 0, zs))
    # eindschijven met naaf (geboord Ø30 H7) - dragen de kernbuis op de as
    for xe in (-Lb / 2 - 10, Lb / 2):
        ring = cyl_x(P["kern_D"] / 2, xe, 10, 0, zs).cut(cyl_x(P["as_d"] / 2 + 0.05, xe - 1, 12, 0, zs))
        kern = kern.fuse(ring)
    # dwarsgaten M10 (pen / breekbout) door kern + as
    pen_gaten = []
    for xe in (-Lb / 2 + 40, Lb / 2 - 40):
        pen_gaten.append(Part.makeCylinder(5.25, 80, V(xe, 0, zs - 40), V(0, 0, 1)))
    for g in pen_gaten:
        kern = kern.cut(g)
    add(doc, "Kernbuis_60x4", kern, GEEL, group=g_vijzel)

    # vijzelblad: schroefvormig blad, gesweept langs helix (in lokale Z, daarna naar X gedraaid)
    r_in = P["kern_D"] / 2
    r_out = P["blad_D"] / 2
    t = P["blad_t"]
    helix = Part.makeHelix(P["blad_spoed"], Lb - 20, r_out)
    prof = Part.makePolygon([V(r_in - 0.5, 0, -t / 2), V(r_out, 0, -t / 2),
                             V(r_out, 0, t / 2), V(r_in - 0.5, 0, t / 2), V(r_in - 0.5, 0, -t / 2)])
    sweep = Part.Wire(helix).makePipeShell([prof], True, True)
    blad = Part.Solid(sweep) if sweep.ShapeType != "Solid" else sweep
    blad.rotate(V(0, 0, 0), V(0, 1, 0), 90)          # Z-as -> X-as
    blad.translate(V(-(Lb - 20) / 2, 0, zs))
    add(doc, "Vijzelblad_D320_S260", blad, GEEL, group=g_vijzel)

    for i, g in enumerate(pen_gaten):
        pen = Part.makeCylinder(5, 76, V(g.BoundBox.Center.x, 0, zs - 38), V(0, 0, 1))
        add(doc, "Pen_M10_%d" % (i + 1), pen, ZILVER, group=g_vijzel)

    # ------------------------------------------------------------ zijplaten
    prof_zij = [(-235, 15), (-100, 15), (-50, 95), (60, 95), (140, 150),
                (215, 260), (215, 330), (120, 420), (-235, 420)]
    skip = []
    plates = {}
    for side, x0 in (("L", -xo), ("R", xi)):
        pl = prism_yz(prof_zij, x0, P["zij_t"])
        pl = fillet_x_edges(pl, 25)
        if side == "L":
            # motortoren op linker zijplaat
            toren = prism_yz([(-150, 400), (30, 400), (30, P["motor_Z"]), (-150, P["motor_Z"])], x0, P["zij_t"])
            toren = toren.fuse(cyl_x(90, x0, P["zij_t"], P["motor_Y"], P["motor_Z"]))
            pl = pl.fuse(toren).removeSplitter()
            # sleufgaten motorflens (kettingspanning, verticaal 20 mm)
            for dy in (-50, 50):
                for dz in (-50, 50):
                    sl = Part.makeBox(P["zij_t"] + 2, 13, 20, V(x0 - 1, P["motor_Y"] + dy - 6.5, P["motor_Z"] + dz - 10))
                    sl = sl.fuse(cyl_x(6.5, x0 - 1, P["zij_t"] + 2, P["motor_Y"] + dy, P["motor_Z"] + dz - 10))
                    sl = sl.fuse(cyl_x(6.5, x0 - 1, P["zij_t"] + 2, P["motor_Y"] + dy, P["motor_Z"] + dz + 10))
                    pl = pl.cut(sl)
            # sleufgat motoras
            pl = pl.cut(Part.makeBox(P["zij_t"] + 2, 50, 40, V(x0 - 1, P["motor_Y"] - 25, P["motor_Z"] - 20)))
        # asgat + lagergaten
        pl = pl.cut(cyl_x(22, x0 - 1, P["zij_t"] + 2, 0, zs))
        for dy in (-41.5, 41.5):
            for dz in (-41.5, 41.5):
                pl = pl.cut(cyl_x(6.6, x0 - 1, P["zij_t"] + 2, dy, zs + dz))
        plates[side] = add(doc, "Zijplaat_%s_8mm" % side, pl, STAAL, group=g_frame)

    # kap (3 mm, gezet/gerold) tussen de zijplaten
    a0, a1 = math.radians(P["kap_hoek_voor"]), math.radians(P["kap_hoek_achter"])
    R1, R2 = P["kap_R"], P["kap_R"] + P["kap_t"]
    span = P["kap_hoek_achter"] - P["kap_hoek_voor"]
    kap = Part.makeCylinder(R2, 2 * xi, V(0, 0, 0), V(0, 0, 1), span).cut(
        Part.makeCylinder(R1, 2 * xi + 2, V(0, 0, -1), V(0, 0, 1)))
    kap.rotate(V(0, 0, 0), V(0, 0, 1), P["kap_hoek_voor"])
    m = App.Matrix(0, 0, 1, -xi,      # lokaal Z -> globaal X
                   1, 0, 0, 0,        # lokaal X -> globaal Y
                   0, 1, 0, zs,       # lokaal Y -> globaal Z
                   0, 0, 0, 1)
    kap = kap.transformGeometry(m)
    # zetrand (stijfheid) langs de voorkant van de kap
    yv, zv = R1 * math.cos(a0), zs + R1 * math.sin(a0)
    rand = Part.makeBox(2 * xi, 30, P["kap_t"], V(-xi, yv, zv + 4))
    rand.rotate(V(0, yv, zv), V(1, 0, 0), P["kap_hoek_voor"])
    kap = kap.fuse(rand).removeSplitter()
    add(doc, "Kap_3mm", kap, STAAL, transp=40, group=g_frame)

    # rubber afstrijkflap achter onder de kap
    ya = R1 * math.cos(a1)
    za = zs + R1 * math.sin(a1)
    flap = Part.makeBox(2 * xi, 10, za - 5 + 15, V(-xi, ya - 10, 5))
    add(doc, "Rubberflap_10mm", flap, ZWART, group=g_frame)

    # dwarsligger koker 80x80x4 (ruggengraat, verbindt zijplaten)
    kok = Part.makeBox(2 * xi, 80, 80, V(-xi, -220, 310)).cut(
        Part.makeBox(2 * xi + 2, 72, 72, V(-xi - 1, -216, 314)))
    add(doc, "Dwarsligger_80x80x4", kok, STAAL, group=g_frame)

    # ------------------------------------------------------------ lagers
    for side, xf, d in (("L", -xo, -1), ("R", xo, +1)):
        add(doc, "UCF206_%s" % side, ucf206(xf, d, 0, zs), BLAUW, group=g_lager)
        add(doc, "Bouten_M12_%s" % side, bolts_ucf(xf, d, 0, zs, P["zij_t"]), ZILVER, group=g_lager)

    # ------------------------------------------------------------ aandrijving
    x_wiel = -xo - 14 - 24 - 30                # kettingwielvlak (buiten lager)
    bw = 7.2                                   # tandbreedte 08B-1
    zw_as = sprocket(P["tand_as"], P["ketting_steek"], x_wiel, bw, 0, zs, P["as_d"])
    add(doc, "Kettingwiel_08B_Z%d" % P["tand_as"], zw_as, ZILVER, group=g_aandr)
    my, mz = P["motor_Y"], P["motor_Z"]
    zw_m = sprocket(P["tand_motor"], P["ketting_steek"], x_wiel, bw, my, mz, 25)
    add(doc, "Kettingwiel_08B_Z%d" % P["tand_motor"], zw_m, ZILVER, group=g_aandr)

    # ketting (als band langs de steekcirkels)
    r1 = pd(P["tand_as"], P["ketting_steek"]) / 2
    r2 = pd(P["tand_motor"], P["ketting_steek"]) / 2
    def stadium(ra, rb, grow):
        a = cyl_x(ra + grow, 0, 1, 0, zs)
        b = cyl_x(rb + grow, 0, 1, my, mz)
        # buitenraaklijnen via convex omhulsel van veel punten
        pts2 = []
        for k in range(72):
            ang = 2 * math.pi * k / 72
            pts2.append((0 + (ra + grow) * math.cos(ang), zs + (ra + grow) * math.sin(ang)))
            pts2.append((my + (rb + grow) * math.cos(ang), mz + (rb + grow) * math.sin(ang)))
        return hull2d(pts2)
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
    ket_out = prism_yz(stadium(r1, r2, 6), x_wiel - 2, bw + 4)
    ket_in = prism_yz(stadium(r1, r2, -4), x_wiel - 3, bw + 6)
    add(doc, "Ketting_08B-1", ket_out.cut(ket_in), ZWART, group=g_aandr)

    # kettingkast (2 mm plaat), afneembaar, op afstandsbussen op de zijplaat
    kast_x0 = -xo - 14 - 26
    kast_x1 = x_wiel - 12
    k_out = prism_yz(stadium(r1, r2, 40), kast_x1 - 2, kast_x0 - kast_x1 + 2)
    k_in = prism_yz(stadium(r1, r2, 38), kast_x1, kast_x0 - kast_x1 + 5)
    add(doc, "Kettingkast_2mm", k_out.cut(k_in), GEEL, transp=55, group=g_aandr)

    # tandwielmotor (24 V DC, ~400 W, i≈20) - flens aan binnenzijde linker zijplaat
    gb = Part.makeBox(110, 130, 130, V(-xi, my - 65, mz - 65))
    gb = fillet_x_edges(gb, 12)
    mot = cyl_x(55, -xi + 110, 230, my, mz)
    kap_m = cyl_x(45, -xi + 340, 25, my, mz)
    kast = Part.makeBox(60, 70, 40, V(-xi + 200, my - 35, mz + 50))   # aansluitkast
    motor = gb.fuse(mot).fuse(kap_m).fuse(kast)
    add(doc, "Tandwielmotor_24V_400W", motor, ZWART, group=g_aandr)
    mas = cyl_x(12.5, x_wiel - 22, -xi - x_wiel + 22, my, mz)
    add(doc, "Motoras_D25", mas, ZILVER, group=g_aandr)

    # ------------------------------------------------------------ bevestiging robot
    for i, xa in enumerate((-420, 420)):
        arm = Part.makeBox(60, 260, 60, V(xa - 30, -480, 320)).cut(
            Part.makeBox(52, 262, 52, V(xa - 26, -481, 324)))
        add(doc, "Arm_60x60x4_%d" % (i + 1), arm, STAAL, group=g_bev)
        plaat = Part.makeBox(200, 12, 260, V(xa - 100, -492, 230))
        for dx in (-70, 70):
            for dz in (40, 90, 140, 190, 240):   # gatenrij = hoogteverstelling
                plaat = plaat.cut(Part.makeCylinder(6.6, 14, V(xa + dx, -493, 230 + dz - 10), V(0, 1, 0)))
        add(doc, "Montageplaat_%d" % (i + 1), plaat, STAAL, group=g_bev)
        # driehoekige knieplaten (2x per arm) tussen arm en dwarsligger
        for k, s in enumerate((-1, 1)):
            xb = xa + s * 30
            tri = Part.Face(Part.makePolygon([V(xb, -220, 374), V(xb + s * 80, -220, 374),
                                              V(xb, -300, 374), V(xb, -220, 374)]))
            kn = tri.extrude(V(0, 0, 6))
            add(doc, "Knieplaat_%d_%d" % (i + 1, k + 1), kn, STAAL, group=g_bev)

    # PE-1000 glijsloffen onder de achterpoten van de zijplaten (vervangbaar)
    for side, x0 in (("L", -xo - 12), ("R", xi - 12)):
        slof = Part.makeBox(P["zij_t"] + 24, 150, 15, V(x0, -240, 0))
        slof = fillet_x_edges(slof, 6)
        add(doc, "Glijslof_PE1000_%s" % side, slof, (0.92, 0.92, 0.88), group=g_frame)

    doc.recompute()
    return doc


def berekening():
    zs_rpm = P["motor_rpm"] * P["tand_motor"] / P["tand_as"]
    T_motor = P["motor_P"] / (2 * math.pi * P["motor_rpm"] / 60)
    T_as = T_motor * P["tand_as"] / P["tand_motor"] * 0.95
    d = P["as_d"]
    tau = 16 * T_as * 1000 / (math.pi * d ** 3)
    F_rand = T_as / (P["blad_D"] / 2000)
    v_axiaal = P["blad_spoed"] / 1000 * zs_rpm / 60
    a_c = P["motor_Z"] - P["as_hoogte"]
    # kettinglengte in schakels
    p = P["ketting_steek"]
    z1, z2 = P["tand_motor"], P["tand_as"]
    a = math.hypot(P["motor_Y"], a_c)
    X = 2 * a / p + (z1 + z2) / 2 + ((z2 - z1) / (2 * math.pi)) ** 2 * p / a
    # massa vijzel
    rho = 7.85e-6
    r_o, r_i = P["blad_D"] / 2, P["kern_D"] / 2
    spoed = P["blad_spoed"]
    gangen = P["blad_L"] / spoed
    r_m = (r_o + r_i) / 2
    blad_opp = math.pi * (r_o ** 2 - r_i ** 2) * math.hypot(1, spoed / (2 * math.pi * r_m)) / 1.0
    m_blad = blad_opp * gangen * P["blad_t"] * rho * (2 * math.pi * r_m) / math.hypot(2 * math.pi * r_m, spoed)
    m_kern = math.pi * (r_i ** 2 - (r_i - P["kern_t"]) ** 2) * P["blad_L"] * rho
    m_as = math.pi * (d / 2) ** 2 * (P["binnenmaat"] + 200) * rho
    # doorbuiging kern+as (kernbuis draagt), gelijkmatige last, scharnierend
    E = 210000.0
    I = math.pi * (P["kern_D"] ** 4 - (P["kern_D"] - 2 * P["kern_t"]) ** 4) / 64 + math.pi * d ** 4 / 64
    L = P["binnenmaat"] + 2 * P["zij_t"] + 2 * 20
    w = (m_blad + m_kern + m_as) * 9.81 / L
    w_tot = w + F_rand / L * 2      # incl. voerdruk als verdeelde last (schatting)
    delta = 5 * w_tot * L ** 4 / (384 * E * I)
    print("=== Voervijzel - kernwaarden ===")
    print("Vijzeltoerental          : %.0f rpm" % zs_rpm)
    print("Koppel motor / as        : %.1f / %.1f Nm" % (T_motor, T_as))
    print("Torsiespanning as Ø%.0f   : %.1f MPa (C45 toelaatbaar ~ 100 MPa)" % (d, tau))
    print("Omtrekskracht blad       : %.0f N" % F_rand)
    print("Axiale voersnelheid      : %.2f m/s" % v_axiaal)
    print("Kettinglengte 08B-1      : %.1f -> %d schakels (even, spannen via sleufgaten)" % (X, 2 * math.ceil(X / 2)))
    print("Hartafstand kettingwielen: %.0f mm" % a)
    print("Massa blad/kern/as       : %.1f / %.1f / %.1f kg" % (m_blad, m_kern, m_as))
    print("Doorbuiging midden       : %.2f mm" % delta)


if __name__ == "__main__" or True:
    _doc = build()
    berekening()
    _map = r"F:/veldrobot/aanbouwdelen/voervijzel/advanced/"
    _doc.saveAs(_map + "voervijzel.FCStd")
    import Import
    Import.export([o for o in _doc.Objects if hasattr(o, "Shape") and not o.isDerivedFrom("App::DocumentObjectGroup")],
                  _map + "voervijzel.step")
