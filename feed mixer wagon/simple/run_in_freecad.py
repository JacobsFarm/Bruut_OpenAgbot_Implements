import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\feed mixer wagon\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import fmw_params
import fmw_parts
import fmw_calc
import build_fmw

for module in (fmw_params, fmw_parts, fmw_calc, build_fmw):
    importlib.reload(module)

doc = build_fmw.build()
fmw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
