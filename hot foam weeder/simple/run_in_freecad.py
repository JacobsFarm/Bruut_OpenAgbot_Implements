import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\hot foam weeder\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import hfw_params
import flw_params
import flw_calc
import flw_parts
import build_flw
import hfw_parts
import hfw_calc
import build_hfw

for module in (flw_params, flw_calc, flw_parts, build_flw, hfw_params, hfw_parts, hfw_calc, build_hfw):
    importlib.reload(module)

doc = build_hfw.build()
hfw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
