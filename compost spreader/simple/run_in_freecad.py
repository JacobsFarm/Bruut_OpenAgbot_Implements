import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\compost spreader\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import csp_params
import csp_parts
import csp_calc
import build_csp

for module in (csp_params, csp_parts, csp_calc, build_csp):
    importlib.reload(module)

doc = build_csp.build()
csp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
