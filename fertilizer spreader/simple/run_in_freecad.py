import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\fertilizer spreader\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import fsp_params
import fsp_parts
import fsp_calc
import build_fsp

for module in (fsp_params, fsp_parts, fsp_calc, build_fsp):
    importlib.reload(module)

doc = build_fsp.build()
fsp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
