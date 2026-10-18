import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dockweed drill\v6"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd6_params
import dwd6_parts
import dwd6_calc
import build_dwd6

for module in (dwd6_params, dwd6_parts, dwd6_calc, build_dwd6):
    importlib.reload(module)

doc = build_dwd6.build()
print(build_dwd6.mass_properties(doc))
for key, value in dwd6_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
