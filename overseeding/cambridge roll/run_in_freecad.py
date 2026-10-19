import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\cambridge roll\cambridge roll"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import cbr_params
import cbr_parts
import cbr_calc
import build_cbr

for module in (cbr_params, cbr_parts, cbr_calc, build_cbr):
    importlib.reload(module)

doc = build_cbr.build()
cbr_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
