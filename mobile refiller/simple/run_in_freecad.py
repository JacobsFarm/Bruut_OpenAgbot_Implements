import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mrs_params
import mrs_calc
import mrs_parts
import build_mrs

for module in (mrs_params, mrs_calc, mrs_parts, build_mrs):
    importlib.reload(module)

doc = build_mrs.build()
print(mrs_calc.report())

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
