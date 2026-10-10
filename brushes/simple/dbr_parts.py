import math

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import dbr_params as P

X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)


# ---------------------------------------------------------------------
# Basisfuncties (zelfde stijl als fpa_parts.py)
# ---------------------------------------------------------------------
def box_span(x, y, z):
    return Part.makeBox(x[1] - x[0], y[1] - y[0], z[1] - z[0], V(x[0], y[0], z[0]))


def cyl_x(d, x0, x1, y, z):
    x0, x1 = sorted((x0, x1))
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, y, z), X)


def cyl_y(d, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), Y)


def cyl_z(d, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0), Z)


def tube_x(x, y, z, wall):
    return box_span(x, y, z).cut(box_span((x[0] - 1, x[1] + 1), (y[0] + wall, y[1] - wall), (z[0] + wall, z[1] - wall)))


def fuse_all(shapes):
    shapes = list(shapes)
    result = shapes[0]
    if len(shapes) > 1:
        result = result.fuse(shapes[1:])
    try:
        result = result.removeSplitter()
    except Exception:
        pass
    return result


def poly_yz(points, x0, t):
    """Gesloten polygoon in het y-z vlak, (y, z) wereld, geëxtrudeerd over +x vanaf x0."""
    pts = [V(x0, y, z) for (y, z) in points]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(t, 0, 0))


def _hex(af, p0, axis, length):
    """Zeskant (sleutelwijdte af) vanaf p0 langs axis (X, Y of Z) over length."""
    r = af / math.sqrt(3.0)
    if axis == "x":
        pts = [V(p0[0], p0[1] + r * math.cos(math.radians(60 * i + 30)), p0[2] + r * math.sin(math.radians(60 * i + 30)))
               for i in range(6)]
        d = V(length, 0, 0)
    elif axis == "y":
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1], p0[2] + r * math.sin(math.radians(60 * i)))
               for i in range(6)]
        d = V(0, length, 0)
    else:
        pts = [V(p0[0] + r * math.cos(math.radians(60 * i)), p0[1] + r * math.sin(math.radians(60 * i)), p0[2])
               for i in range(6)]
        d = V(0, 0, length)
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(d)


def hex_y(af, y0, y1, x, z):
    y0, y1 = sorted((y0, y1))
    return _hex(af, (x, y0, z), "y", y1 - y0)


def hex_z(af, z0, z1, x, y):
    z0, z1 = sorted((z0, z1))
    return _hex(af, (x, y, z0), "z", z1 - z0)


def slot_y(w, x, z0, z1, y0, y1):
    """Verticaal sleufgat (breedte w, hart z0..z1) door een plaat loodrecht op y."""
    s = box_span((x - w / 2.0, x + w / 2.0), (y0, y1), (z0, z1))
    return s.fuse([cyl_y(w, y0, y1, x, z0), cyl_y(w, y0, y1, x, z1)])


AF = {8: 13.0, 10: 17.0, 16: 24.0}
NUT_M = {8: 6.8, 10: 8.4, 16: 13.0}
HEAD_K = {8: 5.3, 10: 6.4, 16: 10.0}


# ---------------------------------------------------------------------
# Toolbar en hangers
# ---------------------------------------------------------------------
def toolbar():
    return tube_x(P.tb_x, P.tb_y, P.tb_z, P.tb_wall)


def toolbar_caps():
    """Kunststof eindkappen 80 x 80 (water en vuil uit de koker)."""
    out = []
    for x0, x1 in ((P.tb_x[0] - 3.0, P.tb_x[0]), (P.tb_x[1], P.tb_x[1] + 3.0)):
        out.append(box_span((x0, x1), P.tb_y, P.tb_z))
    return out


def hanger_bolt_xy(sx):
    xc = sx * P.hanger_x
    return [(xc + dx, y) for dx in (-P.hanger_bolt_dx, P.hanger_bolt_dx) for y in P.robot_rear_beam_y]


def hanger_top(sx):
    xc = sx * P.hanger_x
    z1 = P.robot_lower_beam_z[0]
    plate = box_span((xc - P.hanger_top_w / 2.0, xc + P.hanger_top_w / 2.0), P.hanger_top_y, (z1 - P.hanger_top_t, z1))
    return plate.cut([cyl_z(P.m10_hole, z1 - 20, z1 + 1, x, y) for (x, y) in hanger_bolt_xy(sx)])


def hanger_webs(sx):
    xc = sx * P.hanger_x
    return [poly_yz(P.web_pts, xc + dx - P.web_t / 2.0, P.web_t) for dx in (-P.web_dx, P.web_dx)]


def hanger_bolts(sx):
    """M10 8.8 x 60 van boven door de onderbalk en de bovenplaat, moer onder de plaat."""
    out = []
    z_top = P.robot_lower_beam_z[1]
    z_plate = P.robot_lower_beam_z[0] - P.hanger_top_t
    for (x, y) in hanger_bolt_xy(sx):
        out.append(hex_z(AF[10], z_top, z_top + HEAD_K[10], x, y))
        out.append(cyl_z(10.0, z_plate - NUT_M[10] - 3.0, z_top, x, y))
        out.append(hex_z(AF[10], z_plate - NUT_M[10], z_plate, x, y))
    return out


# ---------------------------------------------------------------------
# Borstelunit. Een unit wordt beschreven door unit_frame(c, xc, s, h):
#   c = config (dbr_params.config), xc = hart borstel in x, s = motor naar +x (1) of -x (-1),
#   h = stand in de sleufgaten (mm, + = omhoog; None = juiste stand voor een nieuwe borstel).
# Kop, motor en borstel worden rechtop getekend en daarna om de scharnierlijn (x-as door y = head_y0,
# z = bovenkant kopplaat) gekanteld met tilt_deg: de voorkant (-y) gaat omlaag.
# ---------------------------------------------------------------------
def unit_frame(c, xc, s=1, h=None):
    if h is None:
        h = P.unit_height(c)
    zt = P.HEAD_TOP_NOM + h
    return {"c": c, "xc": xc, "s": s, "h": h, "zt": zt, "yc": c["yc"]}


def tilt(shape, u):
    s = shape.copy()
    s.rotate(V(0, P.head_y0, u["zt"]), X, P.tilt_deg)
    return s


def tilt_point(u, y, z):
    a = math.radians(P.tilt_deg)
    dy, dz = y - P.head_y0, z - u["zt"]
    return (P.head_y0 + dy * math.cos(a) - dz * math.sin(a), u["zt"] + dy * math.sin(a) + dz * math.cos(a))


def brush_axis(u):
    """(punt, richting) van de gekantelde borstelas, voor de rotatie in de animatie."""
    a = math.radians(P.tilt_deg)
    y, z = tilt_point(u, u["yc"], u["zt"])
    return V(u["xc"], y, z), V(0, -math.sin(a), math.cos(a))


def levels(u):
    """z-niveaus rechtop (langs de borstelas) t.o.v. de wereld, voor de kanteling."""
    zt = u["zt"]
    z = {"head_top": zt, "head_bot": zt - P.head_t}
    z["boss_top"] = z["head_bot"] - P.hub_gap
    z["flange_top"] = z["boss_top"] - P.hub_boss_h
    z["plate_top"] = z["flange_top"] - P.hub_flange_t
    z["plate_bot"] = z["plate_top"] - P.brush_plate_t
    z["bristle_bot"] = z["plate_bot"] - u["c"]["h"]
    z["fa_top"] = zt + P.fa_t
    z["gb_top"] = z["fa_top"] + P.gb_h
    z["worm"] = z["fa_top"] + P.gb_h / 2.0
    z["shaft_top"] = z["gb_top"] + 5.0
    return z


def clamp_plate(u):
    xc, h = u["xc"], u["h"]
    y0, y1 = P.tb_y[0] - P.unit_t, P.tb_y[0]
    plate = box_span((xc - P.unit_w / 2.0, xc + P.unit_w / 2.0), (y0, y1), (P.UNIT_BOTTOM_NOM + h, P.unit_top_z + h))
    tools = []
    for dx in (-P.ub_dx, P.ub_dx):
        for zl in P.ub_leg_z:
            tools.append(slot_y(P.slot_w, xc + dx, zl + P.height_range[0] + h, zl + P.height_range[1] + h, y0 - 1, y1 + 1))
    return plate.cut(tools)


def jack_tab(u):
    xc, h = u["xc"], u["h"]
    z1 = P.unit_top_z + h
    tab = box_span((xc - P.tab_w / 2.0, xc + P.tab_w / 2.0), P.tab_y, (z1 - P.tab_t, z1))
    return tab.cut(cyl_z(P.m16_hole, z1 - P.tab_t - 1, z1 + 1, xc, P.jack_y))


def jack_hw(u):
    """Gelaste moer M16 op de lip, contramoer, stelbout tot op de bovenkant van de toolbar."""
    xc, z1 = u["xc"], P.unit_top_z + u["h"]
    y = P.jack_y
    nut = hex_z(AF[16], z1, z1 + NUT_M[16], xc, y).cut(cyl_z(16.0, z1 - 1, z1 + 20, xc, y))
    lock = hex_z(AF[16], z1 + NUT_M[16], z1 + 2 * NUT_M[16], xc, y).cut(cyl_z(16.0, z1, z1 + 40, xc, y))
    top = z1 + 2 * NUT_M[16] + 12.0
    bolt = fuse_all([cyl_z(16.0, P.tb_z[1], top, xc, y), hex_z(AF[16], top, top + HEAD_K[16], xc, y)])
    return [nut, lock, bolt]


def u_bolts(u):
    """2 vierkante U-beugels M16 om de toolbar: beugel aan de voorkant, poten boven en onder de koker door de
    sleufgaten, sluitring + moer achter de klemplaat."""
    xc = u["xc"]
    d = P.ub_d
    yb = P.tb_y[1] + d / 2.0 + 0.5
    y_plate = P.tb_y[0] - P.unit_t
    y_end = y_plate - 3.0 - NUT_M[16] - 8.0
    z0, z1 = P.ub_leg_z
    out = []
    for dx in (-P.ub_dx, P.ub_dx):
        x = xc + dx
        bow = [cyl_y(d, yb, y_end, x, z0), cyl_y(d, yb, y_end, x, z1), cyl_z(d, z0, z1, x, yb),
               Part.makeSphere(d / 2.0, V(x, yb, z0)), Part.makeSphere(d / 2.0, V(x, yb, z1))]
        out.append(fuse_all(bow))
        for z in (z0, z1):
            out.append(cyl_y(32.0, y_plate - 3.0, y_plate, x, z).cut(cyl_y(17.0, y_plate - 4, y_plate + 1, x, z)))
            out.append(hex_y(AF[16], y_plate - 3.0 - NUT_M[16], y_plate - 3.0, x, z).cut(
                cyl_y(16.0, y_plate - 20, y_plate, x, z)))
    return out


def head_plate(u):
    xc, zt = u["xc"], u["zt"]
    plate = box_span((xc - P.unit_w / 2.0, xc + P.unit_w / 2.0), (P.head_y0 - P.head_len, P.head_y0), (zt - P.head_t, zt))
    tools = []
    r = P.fa_pcd / 2.0
    yc = u["yc"]
    tools.append(cyl_z(36.0, zt - 20, zt + 5, xc, yc))
    for (dx, dy) in ((r, 0), (-r, 0), (0, r), (0, -r)):
        tools.append(cyl_z(11.0, zt - 20, zt + 5, xc + dx, yc + dy))
    return tilt(plate.cut(tools), u)


def gussets(u):
    """2 schoren 8 mm op de randen van de kopplaat, tegen de achterkant van de klemplaat (in wereldcoördinaten:
    voorkant verticaal, onderkant op de gekantelde kopplaat)."""
    xc = u["xc"]
    yf = P.tb_y[0] - P.unit_t
    a = math.radians(P.tilt_deg)

    def z_on(y):
        return u["zt"] + (y - P.head_y0) * math.tan(a)
    y2 = yf - P.gusset_len
    pts = [(yf, z_on(yf)), (yf, z_on(yf) + P.gusset_h), (y2, z_on(y2))]
    w = P.unit_w / 2.0
    return [poly_yz(pts, xc - w, P.gusset_t), poly_yz(pts, xc + w - P.gusset_t, P.gusset_t)]


def gearmotor(u):
    """NMRV063 met FA-flens en 48 V DC motor (IEC 71 B14). Wormas aan de verre kant (-y), motor naar s * x."""
    xc, yc, s = u["xc"], u["yc"], u["s"]
    z = levels(u)
    r = P.fa_pcd / 2.0
    flange = cyl_z(P.fa_d, z["head_top"], z["fa_top"], xc, yc)
    flange = flange.cut([cyl_z(11.0, z["head_top"] - 1, z["fa_top"] + 1, xc + dx, yc + dy)
                         for (dx, dy) in ((r, 0), (-r, 0), (0, r), (0, -r))])
    b = P.gb_body / 2.0
    body = box_span((xc - b, xc + b), (yc - b, yc + b), (z["fa_top"], z["gb_top"]))
    yw = yc - P.gm_center
    worm = cyl_x(P.worm_d, xc - P.worm_len / 2.0, xc + P.worm_len / 2.0, yw, z["worm"])
    x0 = xc + s * P.worm_len / 2.0
    x1 = x0 + s * P.motor_flange_t
    x2 = x1 + s * P.motor_len
    mflange = cyl_x(P.motor_flange_d, x0, x1, yw, z["worm"])
    motor = cyl_x(P.motor_d, x1, x2, yw, z["worm"])
    cap = cyl_x(P.motor_d - 20.0, x2, x2 + s * 15.0, yw, z["worm"])
    xm = (x1 + x2) / 2.0
    term = box_span(sorted((xm - 35.0, xm + 35.0)), (yw - 30.0, yw + 30.0),
                    (z["worm"] + P.motor_d / 2.0 - 8.0, z["worm"] + P.motor_d / 2.0 + 32.0))
    gm = fuse_all([flange, body, worm, mflange, motor, cap, term])
    gm = gm.cut(cyl_z(P.shaft_d + 0.4, z["head_top"] - 1, z["gb_top"] + 1, xc, yc))   # holle uitgaande as
    return tilt(gm, u)


def gearmotor_bolts(u):
    """4 x M10 door FA-flens en kopplaat, moer onder de kopplaat."""
    xc, yc = u["xc"], u["yc"]
    z = levels(u)
    r = P.fa_pcd / 2.0
    out = []
    for (dx, dy) in ((r, 0), (-r, 0), (0, r), (0, -r)):
        x, y = xc + dx, yc + dy
        out.append(hex_z(AF[10], z["fa_top"], z["fa_top"] + HEAD_K[10], x, y))
        out.append(cyl_z(10.0, z["head_bot"] - NUT_M[10] - 3.0, z["fa_top"], x, y))
        out.append(hex_z(AF[10], z["head_bot"] - NUT_M[10], z["head_bot"], x, y))
    return [tilt(fuse_all(out[i:i + 3]), u) for i in range(0, len(out), 3)]


# ---------------------------------------------------------------------
# Borstel (draait mee): insteekas, naaf, plaat, haarkrans, bouten
# ---------------------------------------------------------------------
def shaft(u):
    z = levels(u)
    s = cyl_z(P.shaft_d, z["plate_top"], z["shaft_top"], u["xc"], u["yc"])
    s = s.cut(cyl_z(10.0, z["plate_top"] - 1, z["plate_top"] + 25.0, u["xc"], u["yc"]))   # draadgat M10 eindbout
    return tilt(s, u)


def hub(u):
    xc, yc = u["xc"], u["yc"]
    z = levels(u)
    fl = cyl_z(P.hub_flange_d, z["plate_top"], z["flange_top"], xc, yc)
    boss = cyl_z(P.hub_boss_d, z["flange_top"], z["boss_top"], xc, yc)
    r = P.hub_pcd / 2.0
    h = fuse_all([fl, boss]).cut([cyl_z(P.shaft_d + 0.1, z["plate_top"] - 1, z["boss_top"] + 1, xc, yc)] +
                                 [cyl_z(11.0, z["plate_top"] - 1, z["flange_top"] + 1, xc + dx, yc + dy)
                                  for (dx, dy) in hub_holes()])
    return tilt(h, u)


def hub_holes():
    r = P.hub_pcd / 2.0
    return ((r, 0), (-r, 0), (0, r), (0, -r))


def hub_bolts(u):
    """4 x M10 van onder door borstelplaat en naafflens, moer op de flens; eindbout M10 met sluitring Ø45."""
    xc, yc = u["xc"], u["yc"]
    z = levels(u)
    out = []
    for (dx, dy) in hub_holes():
        x, y = xc + dx, yc + dy
        out.append(fuse_all([hex_z(AF[10], z["plate_bot"] - HEAD_K[10], z["plate_bot"], x, y),
                             cyl_z(10.0, z["plate_bot"], z["flange_top"] + NUT_M[10] + 3.0, x, y)]))
        out.append(hex_z(AF[10], z["flange_top"], z["flange_top"] + NUT_M[10], x, y).cut(
            cyl_z(10.0, z["flange_top"] - 1, z["flange_top"] + 20, x, y)))
    washer = cyl_z(45.0, z["plate_top"] - 5.0, z["plate_top"], xc, yc).cut(
        cyl_z(10.5, z["plate_top"] - 6, z["plate_top"] + 1, xc, yc))
    end = fuse_all([hex_z(AF[10], z["plate_top"] - 5.0 - HEAD_K[10], z["plate_top"] - 5.0, xc, yc),
                    cyl_z(10.0, z["plate_top"] - 5.0, z["plate_top"] + 22.0, xc, yc)])
    return [tilt(s, u) for s in out + [washer, end]]


def brush_plate(u):
    xc, yc = u["xc"], u["yc"]
    z = levels(u)
    p = cyl_z(u["c"]["plate_d"], z["plate_bot"], z["plate_top"], xc, yc)
    p = p.cut([cyl_z(60.0, z["plate_bot"] - 1, z["plate_top"] + 1, xc, yc)] +
              [cyl_z(11.0, z["plate_bot"] - 1, z["plate_top"] + 1, xc + dx, yc + dy) for (dx, dy) in hub_holes()])
    return tilt(p, u)


def bristles(u):
    """Haarkrans: afgeknotte kegelring, onder Ø d, boven Ø plaat; hol in het midden."""
    c = u["c"]
    xc, yc = u["xc"], u["yc"]
    z = levels(u)
    h = c["h"]
    R, Rp = c["R"], c["plate_d"] / 2.0
    wb, wt = P.bristle_ring
    outer = Part.makeCone(R, Rp, h, V(xc, yc, z["bristle_bot"]), Z)
    ri_b, ri_t = R - wb, Rp - wt
    k = (ri_b - ri_t) / h
    inner = Part.makeCone(ri_b + k, ri_t - k, h + 2.0, V(xc, yc, z["bristle_bot"] - 1.0), Z)
    cuts = [inner]
    for i in range(P.bristle_tufts):          # sleuven tussen de bundelrijen (ook zichtbaar als de borstel draait)
        s = box_span((0.0, R + 10.0), (-2.5, 2.5), (z["bristle_bot"] - 1.0, z["plate_bot"] - 15.0))
        s.rotate(V(0, 0, 0), Z, 360.0 * i / P.bristle_tufts)
        s.translate(V(xc, yc, 0))
        cuts.append(s)
    return tilt(outer.cut(cuts), u)


# ---------------------------------------------------------------------
# Regelkast op de achterste onderbalken
# ---------------------------------------------------------------------
def box_base():
    z0 = P.robot_lower_beam_z[1]
    b = box_span(P.box_base_x, P.box_base_y, (z0, z0 + P.box_base_t))
    return b.cut([cyl_z(8.4, z0 - 1, z0 + 5, x, y) for x in (-125.0, 125.0) for y in P.robot_rear_beam_y])


def controller_box():
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    b = box_span(P.box_x, P.box_y, (z0, z0 + P.box_h))
    lid = box_span((P.box_x[0] - 3, P.box_x[1] + 3), (P.box_y[0] - 3, P.box_y[1] + 3), (z0 + P.box_h, z0 + P.box_h + 12))
    glands = [cyl_y(20.0, P.box_y[0] - 18.0, P.box_y[0], x, z0 + 30.0) for x in (-60.0, 0.0, 60.0)]
    return fuse_all([b, lid] + glands)


def box_bolts():
    out = []
    z0 = P.robot_lower_beam_z[1] + P.box_base_t
    zb = P.robot_lower_beam_z[0]
    for x in (-125.0, 125.0):
        for y in P.robot_rear_beam_y:
            out += [hex_z(AF[8], z0, z0 + HEAD_K[8], x, y), cyl_z(8.0, zb - NUT_M[8] - 3.0, z0, x, y),
                    hex_z(AF[8], zb - NUT_M[8], zb, x, y)]
    return out


# ---------------------------------------------------------------------
# Contragewicht voorop (zelfde blokken als de voerschuifvijzel)
# ---------------------------------------------------------------------
def ballast():
    z0 = P.robot_lower_beam_z[1]
    out = []
    for sx in (-1, 1):
        x = sorted((sx * P.ballast_x[0], sx * P.ballast_x[1]))
        b = box_span(x, P.ballast_y, (z0, z0 + P.ballast_h))
        for xh in (sx * 175.0, sx * 225.0):
            b = b.cut(cyl_z(11.0, z0 - 1, z0 + P.ballast_h + 1, xh, P.robot_front_beam_y))
        out.append(b)
    return out


def ballast_bolts():
    z0 = P.robot_lower_beam_z[0]
    z1 = P.robot_lower_beam_z[1] + P.ballast_h
    y = P.robot_front_beam_y
    out = []
    for sx in (-1, 1):
        for xh in (sx * 175.0, sx * 225.0):
            out += [cyl_z(10.0, z0 - 12.0, z1 + 10.0, xh, y), hex_z(AF[10], z1, z1 + HEAD_K[10], xh, y),
                    hex_z(AF[10], z0 - NUT_M[10], z0, xh, y)]
    return out
