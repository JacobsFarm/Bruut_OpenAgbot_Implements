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

import dwd2_params
import dwd2_parts
import dwd2_calc
import build_dwd2

for module in (dwd2_params, dwd2_parts, dwd2_calc, build_dwd2):
    importlib.reload(module)

doc = build_dwd2.build()
print(build_dwd2.mass_properties(doc))
for key, value in dwd2_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
