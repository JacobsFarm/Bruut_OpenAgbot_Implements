import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\cover crop undersower\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ccu_params
import ccu_parts
import ccu_calc
import build_ccu

for module in (ccu_params, ccu_parts, ccu_calc, build_ccu):
    importlib.reload(module)

doc = build_ccu.build()
ccu_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
