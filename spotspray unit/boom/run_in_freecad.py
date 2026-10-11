import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\spotspray unit\boom"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ssp_params
import ssp_calc
import ssp_parts
import build_ssp

for module in (ssp_params, ssp_calc, ssp_parts, build_ssp):
    importlib.reload(module)

doc = build_ssp.build()
ssp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
