import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dockweed drill\v1"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd1_params
import dwd1_parts
import dwd1_calc
import build_dwd1

for module in (dwd1_params, dwd1_parts, dwd1_calc, build_dwd1):
    importlib.reload(module)

doc = build_dwd1.build()
print(build_dwd1.mass_properties(doc))
for key, value in dwd1_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
