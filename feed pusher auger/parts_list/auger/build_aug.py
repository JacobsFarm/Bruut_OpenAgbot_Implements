import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

import aug_params as P
import aug_parts as G

DOC_NAME = "Auger"
FOLDER = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(FOLDER, "Auger.FCStd")
STEP_PATH = os.path.join(FOLDER, "Auger.step")
PREVIEW_DIR = os.path.join(FOLDER, "previews")

COLOR = {
    "auger": (0.95, 0.70, 0.05),
    "steel": (0.75, 0.75, 0.78),
    "zinc": (0.82, 0.84, 0.87),
    "pe": (0.92, 0.92, 0.88),
}
DENSITY = {"auger": P.rho_steel, "steel": P.rho_steel, "zinc": P.rho_steel, "pe": P.rho_pe}
MATERIAL = {}                      # objectnaam -> COLOR-sleutel, voor de massa


def new_part(doc, parent, name, label):
    part = doc.addObject("App::Part", name)
    part.Label = label
    if parent is not None:
        parent.addObject(part)
    return part


def add_shape(doc, parent, name, label, shape, color, visible=True, transparency=0):
    if isinstance(shape, (list, tuple)):
        shape = Part.makeCompound(list(shape))
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    parent.addObject(obj)
    MATERIAL[name] = color
    view = obj.ViewObject
    if view is not None:
        view.ShapeColor = COLOR[color]
        view.Visibility = visible
        view.Transparency = transparency
    return obj


def build(save_path=SAVE_PATH, step_path=STEP_PATH):
    if App.listDocuments().get(DOC_NAME):
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    root = new_part(doc, None, "auger", "auger")
    rotor = new_part(doc, root, "rotor", "rotor")
    add_shape(doc, rotor, "core", "core", G.core(), "auger")
    add_shape(doc, rotor, "blade", "blade", G.blade(), "auger")
    add_shape(doc, rotor, "wear_bush", "wear_bush", G.wear_bush(), "pe")
    add_shape(doc, rotor, "bolt_bosses", "bolt_bosses", G.bolt_bosses(), "auger")
    add_shape(doc, rotor, "shear_bolt", "shear_bolt", G.shear_bolt(), "zinc")
    doc.recompute()
    if save_path:
        doc.saveAs(save_path)
    if step_path:
        Part.export([o for o in doc.Objects if o.TypeId == "Part::Feature"], step_path)
    return doc


def features(doc=None):
    doc = doc or App.getDocument(DOC_NAME)
    return [o for o in doc.Objects if o.TypeId == "Part::Feature" and (o.ViewObject is None or o.ViewObject.Visibility)]


def check_interference(doc=None, tol=1.0):
    """common()-volume tussen zichtbare delen (mm3), met bounding-box voorfilter. Moet leeg zijn."""
    objs = features(doc)
    out = []
    for i, a in enumerate(objs):
        for b in objs[i + 1:]:
            if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                continue
            v = a.Shape.common(b.Shape).Volume
            if v > tol:
                out.append((a.Name, b.Name, round(v, 1)))
    return out


def mass_properties(doc=None):
    """Massa per deel (kg) en zwaartepunt van de draaiende wokkel (rotor)."""
    doc = doc or App.getDocument(DOC_NAME)
    parts = {}
    m_rot, cg = 0.0, V(0, 0, 0)
    for o in features(doc):
        rho = DENSITY[MATERIAL.get(o.Name, "steel")]
        parts[o.Name] = round(o.Shape.Volume * rho, 2)
        for s in o.Shape.Solids:
            m_rot += s.Volume * rho
            cg += s.CenterOfMass * (s.Volume * rho)
    cg = cg * (1.0 / m_rot)
    return {"parts_kg": parts, "rotor_kg": round(m_rot, 2), "rotor_cg": (round(cg.x, 1), round(cg.y, 1), round(cg.z, 1))}


def set_camera(direction, target, height, up=(0.0, 0.0, 1.0)):
    import FreeCADGui as Gui
    from pivy import coin
    view = Gui.ActiveDocument.ActiveView
    view.setCameraType("Orthographic")
    d = V(*direction)
    d.normalize()
    tgt = V(*target)
    eye = tgt - d * 5000.0
    cam = view.getCameraNode()
    cam.position.setValue(coin.SbVec3f(eye.x, eye.y, eye.z))
    cam.pointAt(coin.SbVec3f(tgt.x, tgt.y, tgt.z), coin.SbVec3f(*up))
    cam.nearDistance.setValue(10.0)
    cam.farDistance.setValue(20000.0)
    cam.height.setValue(height)
    return view


def save_view(name, direction, target, height, up=(0.0, 0.0, 1.0), size_px=(1600, 900)):
    import FreeCADGui as Gui
    Gui.updateGui()
    view = set_camera(direction, target, height, up)
    Gui.updateGui()
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    path = os.path.join(PREVIEW_DIR, name)
    view.saveImage(path, size_px[0], size_px[1], "White")
    return path


def render_all():
    doc = build()
    import FreeCADGui as Gui
    Gui.setActiveDocument(doc.Name)
    mid = (P.length / 2.0, 0, 0)
    out = [save_view("1_iso.png", (-1, 1, -0.6), mid, 900),
           save_view("2_side.png", (0, 1, 0), mid, 800),
           save_view("3_drive_end.png", (1, 1, -0.5), (P.shear_hole_x + 60, 0, 0), 380)]
    doc.getObject("blade").ViewObject.Visibility = False
    out.append(save_view("5_bolt_bosses.png", (0.4, 1, -0.2), (P.shear_hole_x, 0, 0), 140))
    doc.getObject("core").ViewObject.Transparency = 70
    out.append(save_view("4_passive_end_bush.png", (-1, 1, -0.5), (P.length - 20, 0, 0), 200))
    doc.getObject("core").ViewObject.Transparency = 0
    doc.getObject("blade").ViewObject.Visibility = True
    return out
