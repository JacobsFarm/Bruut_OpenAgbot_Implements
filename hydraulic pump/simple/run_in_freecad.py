import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\hydraulic pump\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import hpu_params
import hpu_parts
import hpu_calc
import build_hpu

for module in (hpu_params, hpu_parts, hpu_calc, build_hpu):
    importlib.reload(module)

doc = build_hpu.build()
hpu_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
