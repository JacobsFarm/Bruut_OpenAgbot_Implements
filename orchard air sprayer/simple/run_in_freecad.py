import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\orchard air sprayer\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import oas_params
import oas_parts
import oas_calc
import build_oas

for module in (oas_params, oas_parts, oas_calc, build_oas):
    importlib.reload(module)

doc = build_oas.build()
oas_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
