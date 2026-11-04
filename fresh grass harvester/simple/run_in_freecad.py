import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\fresh grass harvester\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import fgh_params
import fgh_parts
import fgh_calc
import build_fgh

for module in (fgh_params, fgh_parts, fgh_calc, build_fgh):
    importlib.reload(module)

doc = build_fgh.build()
fgh_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
