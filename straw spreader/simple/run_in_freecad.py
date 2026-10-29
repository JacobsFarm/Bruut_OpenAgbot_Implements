import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\straw spreader\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import stw_params
import stw_parts
import stw_calc
import build_stw

for module in (stw_params, stw_parts, stw_calc, build_stw):
    importlib.reload(module)

doc = build_stw.build()
stw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
