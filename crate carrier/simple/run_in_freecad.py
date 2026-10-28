import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\crate carrier\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ccr_params
import ccr_parts
import ccr_calc
import build_ccr

for module in (ccr_params, ccr_parts, ccr_calc, build_ccr):
    importlib.reload(module)

doc = build_ccr.build()
ccr_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
