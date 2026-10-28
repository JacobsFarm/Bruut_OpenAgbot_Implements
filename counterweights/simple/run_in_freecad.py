import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\counterweights\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import cwt_params
import cwt_parts
import cwt_calc
import build_cwt

for module in (cwt_params, cwt_parts, cwt_calc, build_cwt):
    importlib.reload(module)

doc = build_cwt.build()
cwt_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
