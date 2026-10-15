import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\in row weeder\double_arm"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ird_params
import ird_calc
import ird_parts
import build_ird

for module in (ird_params, ird_calc, ird_parts, build_ird):
    importlib.reload(module)

doc = build_ird.build()
ird_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
