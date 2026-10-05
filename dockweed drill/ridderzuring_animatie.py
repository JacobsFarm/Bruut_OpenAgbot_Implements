# -*- coding: utf-8 -*-
"""
Animatie van de ridderzuringfrees: rijden -> stoppen bij de plant -> X naar de plant -> pot op de grond ->
vermorzelen tot 150 mm -> draaiend omhoog -> doorrijden. Maakt frames met FreeCAD en zet ze met Pillow om
naar een GIF.

Uitvoeren in FreeCAD (Python-console):
    exec(open(r"F:/veldrobot/aanbouwdelen/Design ridderzuring boor/Design/ridderzuring_animatie.py", encoding="utf-8").read())
"""
import math
import os
import FreeCAD as App
import Part

MAP = r"F:/veldrobot/aanbouwdelen/Design ridderzuring boor/Design/"
FRAMES = MAP + "animatie_frames/"
RZ = {"__name__": "rz_anim"}
_src = open(MAP + "ridderzuring_ontwerp.py", encoding="utf-8").read()
exec(_src.split('if __name__ == "__main__" or True:')[0], RZ)
V = App.Vector

A = dict(
    plant_x=280.0, plant_y=1500.0,      # plant die behandeld wordt (wereldcoordinaten)
    start_afstand=1400.0,               # zoveel mm rijdt de robot voordat hij stopt
    door_afstand=900.0,                 # doorrijden na de behandeling
    rijstand=280.0, diepte=150.0, pot_rand=30.0,
    graden_per_frame=37.0,              # draaiing van de frees per frame (stroboscopisch)
    breedte=960, hoogte=600, ms=80,     # GIF: framegrootte en ms per frame
    richting=(-0.9, -0.8, -0.55),       # camerarichting
)

# onderdelen die met de X-slede meebewegen (naam begint met ...)
X_MEE = ("HGH15CA_wagen_X", "X_slede", "Planetaire_kast", "NEMA23_X", "Poelie", "Spanrol", "Kabelrups_meenemer")
Z_VAST = ("HGH15CA_wagen_Z", "Moerhuis", "Kogelomloopmoer")     # Z-as-delen op de X-slede (niet in Z)


def bouw():
    doc, info = RZ["build"]("Ridderzuring_animatie", x_slede=0.0, z_frees=A["rijstand"])
    ys = info["ys"]
    # extra lang maaiveld, oude maaiveld en losse gereedschap verbergen
    for o in doc.Objects:
        if o.TypeId == "Part::Feature" and (o.Name.startswith("Maaiveld") or o.Name.startswith("Ridderzuring_plant")
                                            or o.Groep == "Wisselgereedschap_los"):
            o.ViewObject.Visibility = False
    def nieuw(naam, sh, kleur, tr=0, zicht=True):
        o = doc.addObject("Part::Feature", naam)
        o.Shape = sh
        o.ViewObject.ShapeColor = kleur
        o.ViewObject.Transparency = tr
        o.ViewObject.Visibility = zicht
        return o
    nieuw("Anim_maaiveld", RZ["box"](-1100, 1100, -1600, 3300, -4, 0), RZ["GROEN"], 0)
    # planten: de doelplant + een paar andere (worden niet behandeld)
    planten = {}
    for k, (px, py, schaal) in enumerate(((A["plant_x"], A["plant_y"], 1.0), (-380, 2500, 0.8), (450, 2900, 0.7), (-250, 400, 0.75))):
        bl = []
        for i in range(7):
            b = RZ["blad"]((230 - 15 * (i % 3)) * schaal, 85 * schaal, 3)
            b.rotate(V(0, 0, 0), V(0, 1, 0), -22)
            b.rotate(V(0, 0, 0), V(0, 0, 1), i * 360.0 / 7 + 10 + 20 * k)
            b.translate(V(px, py, 2))
            bl.append(b)
        planten[k] = nieuw("Anim_plant_%d" % k, Part.makeCompound(bl), RZ["BLAD"])
        nieuw("Anim_wortelkop_%d" % k, RZ["cyl"](20 * schaal, V(px, py, -8), V(0, 0, 1), 18), RZ["BRUIN"])
    # na de behandeling: vermorzelde plek
    plek = nieuw("Anim_vermorzelde_plek", RZ["cyl"](90, V(A["plant_x"], A["plant_y"], 0), V(0, 0, 1), 3), RZ["GROND"], 0, False)
    doc.recompute()
    basis = {o.Name: o.Placement.copy() for o in doc.Objects if o.TypeId == "Part::Feature"}
    return doc, ys, planten[0], plek, basis


def soort(o):
    """'vast' (omgeving), 'robot' (alleen Y), 'x' (Y+X), 'z' (Y+X+Z), 'pot', 'frees'."""
    if o.Name.startswith("Anim_") or o.Groep in ("Omgeving", "Detail", "Wisselgereedschap_los"):
        return "vast"
    if o.Groep == "Gereedschap":
        return "frees"
    if o.Groep == "Pot":
        return "pot"
    if o.Groep in ("Spil",) or (o.Groep == "Z_as" and not o.Name.startswith(Z_VAST)):
        return "z"
    if o.Groep == "Camera" or o.Name.startswith(X_MEE) or o.Name.startswith(Z_VAST):
        return "x"
    return "robot"


def zet_stand(doc, ys, basis, dy, x, z, hoek):
    dz = z - A["rijstand"]
    dz_pot = max(dz, -(A["rijstand"] - A["pot_rand"]))      # pot blijft op de grond liggen
    for o in doc.Objects:
        if o.TypeId != "Part::Feature" or o.Name not in basis:
            continue
        s = soort(o)
        if s == "vast":
            continue
        if s == "robot":
            v = V(0, dy, 0)
        elif s == "x":
            v = V(x, dy, 0)
        elif s == "pot":
            v = V(x, dy, dz_pot)
        else:
            v = V(x, dy, dz)
        if s == "frees":
            beweging = App.Placement(v, App.Rotation(V(0, 0, 1), hoek), V(0, ys, 0))
        else:
            beweging = App.Placement(v, App.Rotation())
        o.Placement = beweging.multiply(basis[o.Name])      # eigen plaatsing van het onderdeel behouden


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def tijdlijn(ys):
    dy_stop = A["plant_y"] - ys
    dy0 = dy_stop - A["start_afstand"]
    d, rijst, px = A["diepte"], A["rijstand"], A["plant_x"]
    st = []          # (dy, x, z, draait, tekst)
    def fase(n, f, draait, tekst):
        for i in range(n):
            t = ease((i + 1) / float(n))
            dy, x, z = f(t)
            st.append((dy, x, z, draait, tekst))
    st.append((dy0, 0, rijst, False, "1. Rijden langs de AB-lijn, camera zoekt ridderzuring"))
    fase(30, lambda t: (dy0 + t * A["start_afstand"], 0, rijst), False, "1. Rijden langs de AB-lijn, camera zoekt ridderzuring")
    fase(5, lambda t: (dy_stop, 0, rijst), False, "2. Plant gevonden: robot stopt met de plant onder het portaal")
    fase(12, lambda t: (dy_stop, t * px, rijst), False, "3. X-as naar de plant (%.0f mm)" % px)
    fase(12, lambda t: (dy_stop, px, rijst - t * (rijst - A["pot_rand"])), True, "4. Spil 1500 rpm, Z zakt tot de pot de zode voelt (= maaiveld)")
    fase(24, lambda t: (dy_stop, px, A["pot_rand"] - t * (A["pot_rand"] + d)), True, "5. Vermorzelen: 25 mm/s insteken tot %.0f mm diep" % d)
    fase(6, lambda t: (dy_stop, px, -d), True, "6. Nadraaien op diepte")
    fase(14, lambda t: (dy_stop, px, -d + t * (d + A["pot_rand"])), True, "7. Draaiend omhoog (mengt nog eens), grond blijft in het gat")
    fase(10, lambda t: (dy_stop, px, A["pot_rand"] + t * (rijst - A["pot_rand"])), False, "8. Rijstand, spil remt af")
    fase(10, lambda t: (dy_stop, px * (1 - t), rijst), False, "9. Klaar: gat van 18 cm met fijngemalen wortel. Door naar de volgende")
    fase(22, lambda t: (dy_stop + t * A["door_afstand"], 0, rijst), False, "9. Klaar: gat van 18 cm met fijngemalen wortel. Door naar de volgende")
    return st


def camera(v, richting, middelpunt, hoogte):
    """Vaste orthografische camera: kijkrichting, punt in beeldmidden en zichtbare hoogte [mm]."""
    from pivy import coin
    RZ["zet_camera"](v, richting)
    v.fitAll()
    cam = v.getCameraNode()
    pos = cam.position.getValue()
    kijk = cam.orientation.getValue().multVec(coin.SbVec3f(0, 0, -1))
    f = cam.focalDistance.getValue()
    brand = V(pos[0] + kijk[0] * f, pos[1] + kijk[1] * f, pos[2] + kijk[2] * f)
    s = middelpunt - brand                     # camera evenwijdig verschuiven naar het gewenste midden
    cam.position.setValue(pos[0] + s.x, pos[1] + s.y, pos[2] + s.z)
    cam.height.setValue(hoogte)


def maak_animatie(naam="animatie_ridderzuringfrees.gif", closeup=False):
    import FreeCADGui as Gui
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(FRAMES, exist_ok=True)
    for f in os.listdir(FRAMES):
        os.remove(FRAMES + f)
    doc, ys, plant, plek, basis = bouw()
    v = RZ["actieve_view"](doc)
    st = tijdlijn(ys)
    gr = doc.getObject("Anim_maaiveld")
    gr.ViewObject.Transparency = 45                       # frees in de grond zichtbaar
    if closeup:
        # alleen stilstaan + vermorzelen, dicht op de spil, pot doorzichtig
        st = [s for s in st if s[4][0] in "345678"]
        for o in doc.Objects:
            if getattr(o, "Groep", "") == "Pot":
                o.ViewObject.Transparency = 70
        camera(v, (-1.0, -0.45, -0.3), V(A["plant_x"], A["plant_y"], 230), 1450)
    else:
        camera(v, A["richting"], V(0, A["plant_y"] - 700, 450), 2900)
    try:
        font = ImageFont.truetype("arialbd.ttf", 22)
        klein = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font = klein = ImageFont.load_default()
    beelden = []
    hoek = 0.0
    behandeld = False
    for i, (dy, x, z, draait, tekst) in enumerate(st):
        if draait:
            hoek += A["graden_per_frame"]
        if z <= A["pot_rand"] + 0.1 and x > 1:
            plant.ViewObject.Visibility = False          # pot staat erop, frees maalt alles fijn
            doc.getObject("Anim_wortelkop_0").ViewObject.Visibility = False
            behandeld = True
        if behandeld and z > A["pot_rand"] + 5:
            plek.ViewObject.Visibility = True
        zet_stand(doc, ys, basis, dy, x, z, hoek)
        Gui.updateGui()
        pad = FRAMES + "f%03d.png" % i
        v.saveImage(pad, A["breedte"], A["hoogte"], "White")
        im = Image.open(pad).convert("RGB")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, A["breedte"], 40], fill=(32, 60, 30))
        d.text((14, 8), tekst, font=font, fill=(255, 255, 255))
        diep = max(0.0, -z)
        info = "X %4.0f mm   Z %+4.0f mm   %s   diepte %3.0f mm" % (x, z, "spil 1500 rpm" if draait else "spil uit", diep)
        d.text((14, A["hoogte"] - 26), info, font=klein, fill=(40, 40, 40))
        d.text((A["breedte"] - 330, A["hoogte"] - 26), "AgBot 'Bruut' - ridderzuringfrees", font=klein, fill=(110, 110, 110))
        im.save(pad)
        beelden.append(im)
    # laatste beeld even vasthouden
    duur = [A["ms"]] * len(beelden)
    duur[-1] = 1500
    gif = MAP + naam
    pal = [b.convert("P", palette=Image.ADAPTIVE, colors=128) for b in beelden]
    pal[0].save(gif, save_all=True, append_images=pal[1:], duration=duur, loop=0, optimize=True)
    print("GIF: %s (%d frames, %.1f MB)" % (gif, len(beelden), os.path.getsize(gif) / 1e6))
    return doc


if __name__ == "__main__" or True:
    _anim_doc = maak_animatie()
    _anim_doc = maak_animatie("animatie_closeup_vermorzelen.gif", closeup=True)
