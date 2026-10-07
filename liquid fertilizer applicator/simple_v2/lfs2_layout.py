"""Opstelling van de eenvoudige toediener (v2) op de kleine robot: gewicht, asbelasting, trekkracht en stabiliteit
met een tank van 100 tot 300 l, op 3, 4 of 6 wielen en met 5, 3 of 2 elementen (puur Python).

Gebruik:  python lfs2_layout.py        (in deze map; werkt samen met lfs2_calc.py, lfs2_kin.py, lfs2_params.py)

Vraag: waar zet je toediener, tank en eventuele extra wielen zodat de robot genoeg grip, een voldoende zware
stuuras en een lage zwaartepunt houdt? Alles is geschat, zie ROBOT, KIT_6WD, TANK en de aannames in lfs2_calc.

Coordinaten (robot): y = rijrichting (voor = +y), z = omhoog, mm; midden van de robot y = 0; assen op y = +-500.
Het werktuig staat in eigen coordinaten (lfs2_params: y = 0 is het hart van de achterste onderbalk, robot y = y - 575).
"""
import contextlib
import math

import lfs2_params as P
import lfs2_kin as K
import lfs2_calc as C

G = 9.81

# robot 4WD rijklaar, uit agbots/agbot comparison/weight_traction.json (geschat, niet gewogen)
ROBOT = {
    "mass_kg": 161.5,
    "cg_y": 95.2,               # mm voor het midden (stappenmotoren en accu zitten voorin)
    "cg_z": 543.5,
    "wheelbase": 1000.0,
    "track": 750.0,
    "r_load": 0.20,             # belaste straal band 4.00-8 (m)
    "torque_cont_nm": 55.0,     # nominaal wielkoppel 8" hubmotor (davilot)
    "torque_peak_nm": 97.4,     # maximaal wielkoppel
    "mu_dry": 0.6,              # droge, stevige grond / gras (aanname agbot comparison)
    "mu_wet": 0.35,             # nat gras
    "crr": 0.08,                # rolweerstand op gras / akker
    "usable": 0.7,              # reken continu met 70 % van de netto trekkracht (marge voor slip, oneffenheden)
    "front_min": 0.20,          # minimaal aandeel van het gewicht op de stuurwielen (agbot comparison)
    "steer_deg": 25.0,
}
FORCE_CONT = ROBOT["torque_cont_nm"] / ROBOT["r_load"] / G     # kgf per wiel, continu
FORCE_PEAK = ROBOT["torque_peak_nm"] / ROBOT["r_load"] / G     # kgf per wiel, kort

# extra middenas (2 wielen met hubmotor 8", wielbeugel, houten blok, onderbalk 40x40x2 van 1 m, regelaars, kabels)
KIT_6WD = {"mass_kg": 2 * (8.0 + 3.0 + 35.4 / 4.0) + 2.4 + 1.5, "z": 300.0}

# onderdelen van een wielunit (kg, geschat; agbots/agbot comparison/weight_traction.json): hubmotor, band, wielbeugel met
# houten blok en boutwerk, stuurkop (stappenmotor, planeetkast, lagers, platen), wiel zonder motor
UNIT = {"hub": 8.0, "tire": 3.0, "bracket": 35.4 / 4.0, "steer": 31.8 / 2.0, "std_wheel": 2.5}
EFFICIENCY = 0.8                # accu -> wiel (agbots/agbot comparison)
BATTERY_KWH = 2.4               # 48 V 50 Ah


def trike_robot(front_driven):
    """Robot met 1 voorwiel op het midden (stuurkop + wiel) en 2 vaste achterwielen: een voorwielunit minder. De
    overgebleven voorunit staat op x = 0, de massa daarvan verandert dus niet; het zwaartepunt schuift naar achteren."""
    wheel_kg = UNIT["hub"] + UNIT["tire"] + UNIT["bracket"]
    removed = wheel_kg + UNIT["steer"]
    m = ROBOT["mass_kg"] - removed
    my = ROBOT["mass_kg"] * ROBOT["cg_y"] - removed * 500.0
    mz = ROBOT["mass_kg"] * ROBOT["cg_z"] - wheel_kg * 300.0 - UNIT["steer"] * 800.0
    if not front_driven:                 # voorwiel zonder motor: gewoon wiel van 2,5 kg in plaats van een hubmotor van 8 kg
        d = UNIT["std_wheel"] - UNIT["hub"]
        m, my, mz = m + d, my + d * 500.0, mz + d * 300.0
    return dict(ROBOT, mass_kg=m, cg_y=my / m, cg_z=mz / m)


# werktuig met n elementen: element 9,1 kg, 2 dieptewielen 14 kg, balk met armen en dwarsbuis 10,7 kg bij 5 elementen
# (schaalt met de breedte); bok, doseerunit en actuator blijven gelijk
ELEMENT_KG = 9.1
DEPTH_WHEELS_KG = 14.0
BASE_MODEL = dict(C.MODEL)
BASE_ROWS = P.row_x


def moving_kg(n):
    other = BASE_MODEL["moving_kg"] - 5 * ELEMENT_KG - DEPTH_WHEELS_KG
    return n * ELEMENT_KG + DEPTH_WHEELS_KG + other * (n * P.row_spacing + 100.0) / (5 * P.row_spacing + 100.0)


@contextlib.contextmanager
def elements(n):
    """Reken binnen dit blok met n elementen (steek 200 mm, symmetrisch): trekkracht, neerdruk, hefraam en massa volgen mee."""
    fixed = BASE_MODEL["implement_kg"] - BASE_MODEL["moving_kg"]
    cg, mv = BASE_MODEL["implement_cg"], BASE_MODEL["moving_cg"]
    cg_fixed = ((BASE_MODEL["implement_kg"] * cg[0] - BASE_MODEL["moving_kg"] * mv[0]) / fixed,
                (BASE_MODEL["implement_kg"] * cg[1] - BASE_MODEL["moving_kg"] * mv[1]) / fixed)
    m_mov = moving_kg(n)
    total = fixed + m_mov
    C.MODEL.update(moving_kg=m_mov, implement_kg=total,
                   implement_cg=((fixed * cg_fixed[0] + m_mov * mv[0]) / total, (fixed * cg_fixed[1] + m_mov * mv[1]) / total))
    P.row_x = tuple((i - (n - 1) / 2.0) * P.row_spacing for i in range(n))
    try:
        yield
    finally:
        C.MODEL.clear()
        C.MODEL.update(BASE_MODEL)
        P.row_x = BASE_ROWS


# tank tussen de wielen (binnenmaat tussen de naven ca. 610 mm), bodem 180 mm boven de grond
TANK = {"width": 580.0, "floor_z": 180.0, "beam_z": 619.0, "density": P.liquid_density}


def tank_empty_kg(volume_l):
    """Tank van PE met beugels en slangen: 6 kg + 0,05 kg per liter."""
    return 6.0 + 0.05 * volume_l


def tank_geometry(volume_l, on_top=False):
    """(zwaartepunt z, y-bereik +-) van een liggende tank: 580 mm breed, 500 mm lang tot 150 l, daarboven 800 mm.
    Onder de onderbalken (z 619) mag hij tot y = +-600; erboven alleen tussen de balken (y +-400).
    on_top: de tank staat op het frame (bovenkant bovenbalken, z 700) omdat de ruimte eronder bezet is."""
    length = 500.0 if volume_l <= 150 else 800.0
    height = volume_l * 1e6 / (TANK["width"] * length)
    if on_top:
        return 700.0 + height / 2.0, 300.0 - length / 2.0 if length < 600 else 0.0
    top = TANK["floor_z"] + height
    reach = 600.0 if top <= TANK["beam_z"] + 1.0 else 400.0
    return TANK["floor_z"] + height / 2.0, max(0.0, reach - length / 2.0)


# ---------------------------------------------------------------------
# Het werktuig op de robot: puntmassa's en trekkracht, per plaats (achter, voor, tussen)
# ---------------------------------------------------------------------
IMPL_SHIFT = {"behind": -575.0, "between": 200.0}


def to_robot_y(position, y_impl):
    """Werktuig-y naar robot-y. Voor = gespiegeld om het midden. Tussen: bok op een nieuwe dwarsbalk op y = +200,
    zodat de messen net voor de achterband (y = -285) blijven."""
    if position == "front":
        return 575.0 - y_impl
    return y_impl + IMPL_SHIFT[position]


def implement_load(position, working, case="normaal", ballast=0.0):
    """Wat de robot draagt van het werktuig. Werkstand: bok + doseerunit en de kracht in het draaipunt, het hefraam
    rust op de grond. Geheven: alles. Geeft (puntmassa's [(kg, y, z)], trekkracht N, hoogte mm, rolweerstand N)."""
    m_fixed = C.MODEL["implement_kg"] - C.MODEL["moving_kg"]
    cg = C.MODEL["implement_cg"]
    mv = C.MODEL["moving_cg"]
    cg_fixed = ((C.MODEL["implement_kg"] * cg[0] - C.MODEL["moving_kg"] * mv[0]) / m_fixed,
                (C.MODEL["implement_kg"] * cg[1] - C.MODEL["moving_kg"] * mv[1]) / m_fixed)
    pts = [(m_fixed, to_robot_y(position, cg_fixed[0]), cg_fixed[1])]
    if working:
        ff = C.frame_forces(case, ballast)
        pts.append((ff["pivot_vertical_N"] / G, to_robot_y(position, P.pivot[0]), P.pivot[1]))
        return pts, float(ff["pivot_horizontal_N"]), P.pivot[1], float(ff["rolling_resistance_N"])
    lifted = K.rot_up(mv, K.lift_angle())
    pts.append((C.MODEL["moving_kg"] + ballast, to_robot_y(position, lifted[0]), lifted[1]))
    return pts, 0.0, 0.0, 0.0


# ---------------------------------------------------------------------
# Asbelasting: stijf frame op banden met gelijke veerstijfheid, N_i = a + b y_i
# ---------------------------------------------------------------------
def axle_loads(axle_y, points, draft_n=0.0, draft_h=0.0):
    """Last per as (kg). points = [(kg, y, z)]. De trekkracht werkt naar achteren op hoogte draft_h en schuift last
    naar de achteras (neus omhoog). Bij 3 assen deelt een stijf frame de last over een vlak; een as met negatieve last
    komt los van de grond en valt weg (last 0)."""
    w = sum(m for m, _, _ in points)
    moment = sum(m * y for m, y, _ in points) - draft_n / G * draft_h
    active = list(range(len(axle_y)))
    while True:
        ys = [axle_y[i] for i in active]
        n, s1, s2 = len(ys), sum(ys), sum(y * y for y in ys)
        if n == 1:
            a, b = w, 0.0
        else:
            det = n * s2 - s1 * s1
            a, b = (w * s2 - s1 * moment) / det, (n * moment - s1 * w) / det
        loads = {i: a + b * axle_y[i] for i in active}
        neg = [i for i in active if loads[i] < 0.0]
        if not neg:
            break
        active.remove(min(neg, key=lambda i: loads[i]))
    return [loads.get(i, 0.0) for i in range(len(axle_y))], w


def cg_of(points):
    w = sum(m for m, _, _ in points)
    return sum(m * y for m, y, _ in points) / w, sum(m * z for m, _, z in points) / w, w


# ---------------------------------------------------------------------
# Opstellingen
# ---------------------------------------------------------------------
# as = (y, aangedreven). work = assen die in werkstand op de grond staan, lift = assen als het werktuig geheven is
# (kop van het perceel, draaien). extra = y van de extra assen (massa van KIT_6WD per as-paar).
FRONT, REAR = 500.0, -500.0
AX4 = ((FRONT, True), (REAR, True))
CONFIGS = {
    "4-achter": dict(label="4 wielen, toediener achter (nu)", impl="behind", work=AX4, lift=AX4, extra=(), top=False),
    "4-voor": dict(label="4 wielen, toediener voor", impl="front", work=AX4, lift=AX4, extra=(), top=False),
    "4-tussen": dict(label="4 wielen, toediener tussen de assen", impl="between", work=AX4, lift=AX4, extra=(), top=True),
    "6-midden": dict(label="6 wielen, middenas vast", impl="behind",
                     work=((FRONT, True), (0.0, True), (REAR, True)),
                     lift=((FRONT, True), (0.0, True), (REAR, True)), extra=(0.0,), top=False),
    "6-liftas": dict(label="6 wielen, middenas alleen neer bij werk", impl="behind",
                     work=((FRONT, True), (0.0, True), (REAR, True)), lift=AX4, extra=(0.0,), top=False),
    "6-naast": dict(label="6 wielen, extra as naast de toediener (y -900)", impl="behind",
                    work=((FRONT, True), (REAR, True), (-900.0, True)), lift=AX4, extra=(-900.0,), top=False),
    "6-achter": dict(label="6 wielen, extra as achter de toediener (y -1200)", impl="behind",
                     work=((FRONT, True), (REAR, True), (-1200.0, True)), lift=AX4, extra=(-1200.0,), top=False),
    # driewieler: 1 stuurwiel voor op x = 0, 2 vaste achterwielen. Het voorwiel (y 500, band tot y 285) zit in de weg van
    # de tank: die mag niet verder naar voren dan y = 0 (500 mm lang, voorkant op y 250).
    "3-alle": dict(label="driewieler, alle 3 aangedreven", impl="behind", work=((FRONT, True, 1), (REAR, True, 2)),
                   lift=((FRONT, True, 1), (REAR, True, 2)), extra=(), top=False, robot=trike_robot(True), tank_max_y=0.0),
    "3-achter": dict(label="driewieler, alleen achterwielen aangedreven", impl="behind",
                     work=((FRONT, False, 1), (REAR, True, 2)), lift=((FRONT, False, 1), (REAR, True, 2)), extra=(),
                     top=False, robot=trike_robot(False), tank_max_y=0.0),
}


def build_points(cfg, volume_l, tank_y, fill, working, case="normaal", ballast=0.0):
    """Alle massa's op de robot voor een toestand. Geeft (puntmassa's, trekkracht N, hoogte, rolweerstand werktuig N)."""
    robot = cfg.get("robot", ROBOT)
    pts = [(robot["mass_kg"], robot["cg_y"], robot["cg_z"])]
    for y in cfg["extra"]:
        pts.append((KIT_6WD["mass_kg"] / len(cfg["extra"]), y, KIT_6WD["z"]))
    if cfg.get("front_kg"):
        pts.append((cfg["front_kg"], 520.0, 400.0))      # ballast of accu vooraan, op de voorste dwarsbalk
    tz, _ = tank_geometry(volume_l, cfg["top"])
    pts.append((tank_empty_kg(volume_l) + fill * volume_l * TANK["density"], tank_y, tz))
    ip, draft, h, roll = implement_load(cfg["impl"], working, case, ballast)
    return pts + ip, draft, h, roll


def ax(a):
    """(y, aangedreven, aantal wielen op de as); een as zonder derde waarde heeft 2 wielen op x = +-375."""
    return a[0], a[1], (a[2] if len(a) > 2 else 2)


def drive_force(axles, loads, mu, force=FORCE_CONT):
    """Som van min(grip, motor) over alle aangedreven wielen (kgf)."""
    total = 0.0
    for a, n in zip(axles, loads):
        _, driven, nw = ax(a)
        if driven and n > 0.0:
            total += nw * min(mu * n / nw, force)
    return total


def convex_hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def half(points):
        h = []
        for p in points:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h
    lower, upper = half(pts), half(reversed(pts))
    return lower[:-1] + upper[:-1]


def tip_min_deg(axles, loads, cgy, cgz):
    """Kleinste kantelhoek (graden) over alle randen van het kantelvlak (convexe omhulling van de wielcontacten op de
    grond), zwaartepunt op x = 0. Een driewieler heeft diagonale randen: aanzienlijk minder dan 4 wielen."""
    half_track = ROBOT["track"] / 2.0
    pts = []
    for a, n in zip(axles, loads):
        y, _, nw = ax(a)
        if n > 0.0:
            pts += [(-half_track, y), (half_track, y)] if nw == 2 else [(0.0, y)]
    hull = convex_hull(pts)
    best = None
    for i in range(len(hull)):
        p, q = hull[i], hull[(i + 1) % len(hull)]
        ex, ey = q[0] - p[0], q[1] - p[1]
        d = (ex * (cgy - p[1]) - ey * (0.0 - p[0])) / math.hypot(ex, ey)     # > 0 binnen (omhulling tegen de klok in)
        ang = math.degrees(math.atan(d / cgz))
        best = ang if best is None else min(best, ang)
    return best


def state(cfg, volume_l, tank_y, fill, working, case="normaal", ballast=0.0):
    pts, draft, h, roll = build_points(cfg, volume_l, tank_y, fill, working, case, ballast)
    axles = cfg["work"] if working else cfg["lift"]
    loads, w = axle_loads([a[0] for a in axles], pts, draft, h)
    front = loads[0] / w
    cgy, cgz, wtot = cg_of(pts)
    supported = [a[0] for a, n in zip(axles, loads) if n > 0.0]
    out = {"loads": loads, "mass": w, "front_share": front, "max_wheel_kg": max(n / ax(a)[2] for a, n in zip(axles, loads)),
           "draft_n": draft, "roll_impl_n": roll, "cg": (cgy, cgz), "tip_min_deg": tip_min_deg(axles, loads, cgy, cgz)}
    out["tip_back_deg"] = math.degrees(math.atan((cgy - min(supported)) / cgz))
    out["tip_fwd_deg"] = math.degrees(math.atan((max(supported) - cgy) / cgz))
    out["tip_side_deg"] = math.degrees(math.atan(ROBOT["track"] / 2.0 / cgz))
    if working:
        for name, mu in (("dry", ROBOT["mu_dry"]), ("wet", ROBOT["mu_wet"])):
            drive = drive_force(axles, loads, mu)
            roll_robot = ROBOT["crr"] * w
            net = drive - roll_robot
            need = (draft + roll) / G
            out[name] = {"drive_kgf": drive, "rolling_kgf": roll_robot, "net_kgf": net, "need_kgf": need,
                         "margin_kgf": net - need, "slope_pct": 100.0 * (net - need) / w,
                         "usable_ok": need <= ROBOT["usable"] * net,
                         "motor_load_pct": 100.0 * (need + roll_robot) / (FORCE_CONT * sum(ax(a)[2] for a in axles if a[1]))}
    return out


def tank_range(cfg, volume_l, step=50.0):
    _, lim = tank_geometry(volume_l, cfg["top"])
    n = int(lim // step)
    ys = [i * step for i in range(-n, n + 1) if i * step <= cfg.get("tank_max_y", 1e9)]
    return ys if ys else [0.0]


def evaluate(cfg, volume_l, tank_y, ballast=0.0):
    """Alle toestanden voor een opstelling en tankstand."""
    return {
        "work_full": state(cfg, volume_l, tank_y, 1.0, True),
        "work_empty": state(cfg, volume_l, tank_y, 0.0, True),
        "work_full_heavy": state(cfg, volume_l, tank_y, 1.0, True, "zwaar", ballast),
        "lift_full": state(cfg, volume_l, tank_y, 1.0, False),
        "lift_empty": state(cfg, volume_l, tank_y, 0.0, False),
        "lift_empty_ballast": state(cfg, volume_l, tank_y, 0.0, False, "zwaar", ballast),
    }


PLAIN = ("work_full", "work_empty", "work_full_heavy", "lift_full", "lift_empty")


def front_extremes(ev):
    """Laagste en hoogste aandeel op de voorwielen over alle toestanden zonder ballast op de balk."""
    shares = [ev[s]["front_share"] for s in PLAIN]
    return min(shares), max(shares)


def best_tank_y(cfg, volume_l, ballast=0.0):
    """Tankstand (mm) waarbij de slechtste toestand het best verdeeld is: maximaliseer over de toestanden zonder
    ballast het minimum van min(voor, achter)."""
    best = None
    for y in tank_range(cfg, volume_l):
        ev = evaluate(cfg, volume_l, y, ballast)
        score = min(min(ev[s]["front_share"], 1.0 - ev[s]["front_share"]) for s in PLAIN)
        if best is None or score > best[0] + 1e-9:
            best = (score, y)
    return best[1]


def max_tank_l(cfg, case="work_full", ground="dry", ballast=0.0, limit=700):
    """Grootste tank (l, stappen van 10) waarbij het werktuig nog binnen 70 % van de netto trekkracht blijft."""
    best = 0
    for v in range(50, limit + 1, 10):
        ev = evaluate(cfg, v, best_tank_y(cfg, v, ballast), ballast)
        if ev[case][ground]["usable_ok"]:
            best = v
        else:
            break
    return best


def front_ballast_needed(cfg, volume_l, ballast, target=ROBOT["front_min"], with_toolbar_ballast=True):
    """Kleinste massa (kg, stappen van 5) vooraan op de voorste dwarsbalk (y 520, z 400) waarmee het aandeel op de
    voorwielen in alle geheven toestanden minstens target blijft; de tankstand wordt telkens opnieuw gekozen."""
    states = ["lift_full", "lift_empty"] + (["lift_empty_ballast"] if with_toolbar_ballast else [])
    for kg in range(0, 201, 5):
        c = dict(cfg, front_kg=float(kg))
        ev = evaluate(c, volume_l, best_tank_y(c, volume_l, ballast), ballast)
        if min(ev[st]["front_share"] for st in states) >= target:
            return kg
    return None


def scrub_deg(cfg):
    """Dwarsslip (graden) van de vaste assen als de voorwielen 25 graden sturen: draaipunt op de lijn door het midden
    van de vaste assen die op de grond staan (liftas omhoog tijdens het draaien)."""
    fixed = [a[0] for a in cfg["lift"] if a[0] != FRONT]
    yv = sum(fixed) / len(fixed)
    radius = (FRONT - yv) / math.tan(math.radians(ROBOT["steer_deg"]))
    return max(abs(math.degrees(math.atan((y - yv) / radius))) for y in fixed), radius / 1000.0


def ha_per_tank(volume_l, dose_l_ha):
    return volume_l / dose_l_ha


def capacity_ha_h(n):
    return n * P.row_spacing / 1000.0 * P.work_speed * 3600.0 / 10000.0


def energy_kwh_ha(t, n):
    """Accu-energie per hectare voor rijden + trekken (alleen de wielen, zonder pomp en stuurmotoren)."""
    force_n = (t["need_kgf"] + t["rolling_kgf"]) * G
    return force_n * P.work_speed / EFFICIENCY / 1000.0 / capacity_ha_h(n)


# ---------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------
def _pct(x):
    return "%3.0f" % (100.0 * x)


def report_masses(volume_l=100):
    m_fixed = C.MODEL["implement_kg"] - C.MODEL["moving_kg"]
    fluid = volume_l * TANK["density"]
    total = ROBOT["mass_kg"] + C.MODEL["implement_kg"] + tank_empty_kg(volume_l) + fluid
    print("== Massa's (kg) ==")
    print("robot rijklaar 4WD                      %6.1f" % ROBOT["mass_kg"])
    print("toediener v2 (bok %.1f + hefraam %.1f)   %6.1f" % (m_fixed, C.MODEL["moving_kg"], C.MODEL["implement_kg"]))
    print("tank %d l leeg (PE + beugels)           %6.1f" % (volume_l, tank_empty_kg(volume_l)))
    print("vloeistof %d l x %.1f kg/l              %6.1f" % (volume_l, TANK["density"], fluid))
    print("totaal 4 wielen, tank vol               %6.1f   (%.1f x de lege robot)" % (total, total / ROBOT["mass_kg"]))
    print("extra middenas (2 wielen + balk)        %6.1f" % KIT_6WD["mass_kg"])
    print("totaal 6 wielen, tank vol               %6.1f" % (total + KIT_6WD["mass_kg"]))
    print("motor per wiel: continu %.1f kgf, kort %.1f kgf" % (FORCE_CONT, FORCE_PEAK))


def report_configs(keys, volume_l, ballast):
    print("\n== Opstellingen, tank %d l: aandeel op de voorwielen (%%) en kantelhoeken ==" % volume_l)
    print("%-50s %6s | werk  werk | geheven geheven geheven | wiel  | tip graden" % ("", "tank"))
    print("%-50s %6s | vol   leeg | vol     leeg    leeg+%dkg| max kg| achter voor zij" % ("opstelling", "y mm", ballast))
    for k in keys:
        cfg = CONFIGS[k]
        ty = best_tank_y(cfg, volume_l, ballast)
        ev = evaluate(cfg, volume_l, ty, ballast)
        sh = [_pct(ev[s]["front_share"]) for s in ("work_full", "work_empty", "lift_full", "lift_empty", "lift_empty_ballast")]
        wl = max(ev[s]["max_wheel_kg"] for s in PLAIN)
        lifts = (ev["lift_full"], ev["lift_empty"])
        print("%-50s %6.0f | %s   %s | %s     %s     %s    | %5.0f | %4.0f %4.0f %4.0f" % (
            cfg["label"], ty, sh[0], sh[1], sh[2], sh[3], sh[4], wl, min(s["tip_back_deg"] for s in lifts),
            min(s["tip_fwd_deg"] for s in lifts), lifts[0]["tip_side_deg"]))


def report_axles(keys, volume_l, ballast):
    print("\n== Last per as (kg), tank %d l; assen van voor naar achter ==" % volume_l)
    for k in keys:
        cfg = CONFIGS[k]
        ty = best_tank_y(cfg, volume_l, ballast)
        ev = evaluate(cfg, volume_l, ty, ballast)
        print("%s  (tank y %.0f, assen y %s)" % (cfg["label"], ty, [int(a[0]) for a in cfg["work"]]))
        for s in ("work_full", "work_empty", "lift_full", "lift_empty"):
            e = ev[s]
            print("   %-11s %s  totaal %.0f kg" % (s, "  ".join("%5.0f" % n for n in e["loads"]), e["mass"]))


def report_traction(keys, volume_l, ballast):
    print("\n== Trekkracht continu (kgf), tank %d l vol ==" % volume_l)
    print("netto = aandrijfkracht (min van grip en motor) - rolweerstand robot; nodig = trekkracht werktuig;")
    print("bruikbaar = nodig <= 70 %% van netto; motor %% = belasting t.o.v. nominaal koppel van de aangedreven motoren")
    print("%-50s | netto d/n  | nodig norm/zwaar | marge norm d/n | marge zwaar d/n | bruikbaar norm d/n, zwaar d/n | helling%% norm d | motor%% norm/zwaar" % "")
    for k in keys:
        cfg = CONFIGS[k]
        ev = evaluate(cfg, volume_l, best_tank_y(cfg, volume_l, ballast), ballast)
        n, h = ev["work_full"], ev["work_full_heavy"]
        yn = lambda t: "ja " if t["usable_ok"] else "NEE"
        print("%-50s | %4.0f/%-4.0f | %3.0f/%-3.0f         | %4.0f/%-4.0f      | %4.0f/%-4.0f       | %s/%s    %s/%s            | %4.1f           | %3.0f/%-3.0f" % (
            cfg["label"], n["dry"]["net_kgf"], n["wet"]["net_kgf"], n["dry"]["need_kgf"], h["dry"]["need_kgf"],
            n["dry"]["margin_kgf"], n["wet"]["margin_kgf"], h["dry"]["margin_kgf"], h["wet"]["margin_kgf"],
            yn(n["dry"]), yn(n["wet"]), yn(h["dry"]), yn(h["wet"]), n["dry"]["slope_pct"],
            n["dry"]["motor_load_pct"], h["dry"]["motor_load_pct"]))


def report_tank_sizes(key, ballast, volumes=(100, 150, 200, 300), doses=(150, 300, 538)):
    cfg = CONFIGS[key]
    cap = P.work_width / 1000.0 * P.work_speed * 3600 / 10000.0
    print("\n== Tankgrootte: %s ==" % cfg["label"])
    print("werkcapaciteit %.2f ha/h (%.1f m breed, %.2f m/s); ha en minuten per vulling bij %s l/ha" % (
        cap, P.work_width / 1000.0, P.work_speed, "/".join(str(d) for d in doses)))
    print("l    tank y  kg    | netto droog/nat | marge normaal d/n | voor% min-max | wiel max kg | tip achter | ha per vulling | minuten per vulling | voorballast nodig kg")
    for v in volumes:
        ty = best_tank_y(cfg, v, ballast)
        ev = evaluate(cfg, v, ty, ballast)
        w = ev["work_full"]
        lo, hi = front_extremes(ev)
        tb = min(ev["lift_full"]["tip_back_deg"], ev["lift_empty"]["tip_back_deg"])
        wl = max(ev[s]["max_wheel_kg"] for s in PLAIN)
        fb = front_ballast_needed(cfg, v, ballast)
        print("%-4d %5.0f %5.0f | %4.0f/%-4.0f       | %4.0f/%-4.0f         | %s-%s       | %5.0f       | %2.0f         | %s | %s | %s" % (
            v, ty, w["mass"], w["dry"]["net_kgf"], w["wet"]["net_kgf"], w["dry"]["margin_kgf"], w["wet"]["margin_kgf"],
            _pct(lo), _pct(hi), wl, tb, "/".join("%.2f" % ha_per_tank(v, d) for d in doses),
            "/".join("%.0f" % (60.0 * ha_per_tank(v, d) / cap) for d in doses), fb))
    print("grootste tank binnen 70 %% van de netto trekkracht: normaal droog %d l, normaal nat %d l, zwaar droog %d l, zwaar nat %d l" % (
        max_tank_l(cfg, "work_full", "dry", ballast), max_tank_l(cfg, "work_full", "wet", ballast),
        max_tank_l(cfg, "work_full_heavy", "dry", ballast), max_tank_l(cfg, "work_full_heavy", "wet", ballast)))


ROBOTS_COMPARED = (("4 wielen", "4-achter"), ("driewieler, 3 aangedreven", "3-alle"), ("driewieler, 2 aangedreven", "3-achter"))


def report_trike(volume_l=100, element_counts=(5, 3, 2)):
    print()
    print("== Robot x aantal elementen, tank %d l (toediener achter, tank zo ver naar voren als kan) ==" % volume_l)
    print("%-26s %2s %5s %5s | %5s | netto d/n | nodig n/z | bruikbaar norm d/n zwaar d/n | ballast | voor%% leeg/+ballast | wiel max | tip min | kWh/ha | ha/accu" % (
        "robot", "el", "ha/h", "kg", "tank y"))
    for label, key in ROBOTS_COMPARED:
        for n in element_counts:
            with elements(n):
                ballast = round(C.ballast_for("zwaar", 100.0))
                cfg = CONFIGS[key]
                ty = best_tank_y(cfg, volume_l, ballast)
                ev = evaluate(cfg, volume_l, ty, ballast)
                w, h = ev["work_full"], ev["work_full_heavy"]
                yn = lambda t: "ja " if t["usable_ok"] else "NEE"
                wheel = max(ev[s]["max_wheel_kg"] for s in PLAIN)
                tip = min(ev[s]["tip_min_deg"] for s in ("lift_full", "lift_empty"))
                kwh = energy_kwh_ha(w["dry"], n)
                print("%-26s %2d %5.2f %5.0f | %5.0f | %4.0f/%-4.0f | %3.0f/%-3.0f   | %s/%s        %s/%s       | %5d   | %s/%s       | %5.0f    | %5.1f   | %5.1f  | %4.2f" % (
                    label, n, capacity_ha_h(n), w["mass"], ty, w["dry"]["net_kgf"], w["wet"]["net_kgf"], w["dry"]["need_kgf"],
                    h["dry"]["need_kgf"], yn(w["dry"]), yn(w["wet"]), yn(h["dry"]), yn(h["wet"]), ballast,
                    _pct(ev["lift_empty"]["front_share"]), _pct(ev["lift_empty_ballast"]["front_share"]), wheel, tip, kwh,
                    BATTERY_KWH / kwh))


def report_trike_balance(volume_l=100, n=3):
    print()
    print("== Driewieler met %d elementen: last per wiel (kg) en kantelhoek, tank %d l ==" % (n, volume_l))
    with elements(n):
        ballast = round(C.ballast_for("zwaar", 100.0))
        for key in ("3-alle", "3-achter"):
            cfg = CONFIGS[key]
            ty = best_tank_y(cfg, volume_l, ballast)
            ev = evaluate(cfg, volume_l, ty, ballast)
            print("%s (tank y %.0f, robot %.0f kg, zwaartepunt y %.0f z %.0f)" % (
                cfg["label"], ty, cfg["robot"]["mass_kg"], cfg["robot"]["cg_y"], cfg["robot"]["cg_z"]))
            for s in ("work_full", "work_empty", "lift_full", "lift_empty", "lift_empty_ballast"):
                e = ev[s]
                print("   %-18s voor %4.0f  achter %4.0f per wiel  | totaal %4.0f kg | voor %% %s | kantelhoek %4.1f graden" % (
                    s, e["loads"][0], e["loads"][1] / 2.0, e["mass"], _pct(e["front_share"]), e["tip_min_deg"]))
            print("   voorballast nodig (min. 20 %% voor, geheven): zonder balkballast %s kg, met %s kg" % (
                front_ballast_needed(cfg, volume_l, ballast, with_toolbar_ballast=False), front_ballast_needed(cfg, volume_l, ballast)))
    ref = CONFIGS["4-achter"]
    ev = evaluate(ref, volume_l, best_tank_y(ref, volume_l, 0), 0)
    print("ter vergelijking 4 wielen, 5 elementen: kantelhoek %.1f graden" % min(ev[s]["tip_min_deg"] for s in ("lift_full", "lift_empty")))


def report_scrub():
    print("\n== Draaien met 25 graden sturen: dwarsslip van de vaste wielen (liftassen omhoog) ==")
    for k, cfg in CONFIGS.items():
        s, r = scrub_deg(cfg)
        print("%-50s dwarsslip %4.1f graden, draaicirkel %.2f m" % (cfg["label"], s, r))
    fixed = ((REAR, True), (0.0, True))
    s, r = scrub_deg(dict(lift=((FRONT, True),) + fixed))
    print("%-50s dwarsslip %4.1f graden, draaicirkel %.2f m" % ("6 wielen, middenas blijft neer tijdens het draaien", s, r))


def main():
    ballast = round(C.ballast_for("zwaar", 100.0))
    report_masses(100)
    print("ballast op de balk voor harde zode: %d kg (alleen in het zware geval, geheven mee naar de robot)" % ballast)
    for v in (100, 200):
        report_configs(list(CONFIGS), v, ballast)
    report_axles(["4-achter", "4-tussen", "6-midden", "6-liftas"], 100, ballast)
    report_traction(list(CONFIGS), 100, ballast)
    for k in ("4-achter", "6-liftas"):
        report_tank_sizes(k, ballast)
    report_scrub()
    report_trike()
    report_trike_balance()


if __name__ == "__main__":
    main()
