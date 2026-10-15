import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dockweed drill\v2"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd3_params
import dwd3_parts
import dwd3_calc
import build_dwd3

for module in (dwd3_params, dwd3_parts, dwd3_calc, build_dwd3):
    importlib.reload(module)

doc = build_dwd3.build()
print(build_dwd3.mass_properties(doc))
for key, value in dwd3_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
