import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\overseeder\advanced"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ova_params
import ova_kin
import ova_parts
import build_ova

for module in (ova_params, ova_kin, ova_parts, build_ova):
    importlib.reload(module)

doc = build_ova.build()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
