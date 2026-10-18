import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\feed pusher auger\parts_list"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import aug_params
import aug_parts
import build_aug

for module in (aug_params, aug_parts, build_aug):
    importlib.reload(module)

doc = build_aug.build()
print("interference:", build_aug.check_interference(doc))
print("mass:", build_aug.mass_properties(doc))

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
