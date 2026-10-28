import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\biocontrol spreader\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import bcs_params
import bcs_parts
import bcs_calc
import build_bcs

for module in (bcs_params, bcs_parts, bcs_calc, build_bcs):
    importlib.reload(module)

doc = build_bcs.build()
bcs_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
