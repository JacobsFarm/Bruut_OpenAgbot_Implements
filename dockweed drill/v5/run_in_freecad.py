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

import dwd5_params
import dwd5_parts
import dwd5_calc
import build_dwd5

for module in (dwd5_params, dwd5_parts, dwd5_calc, build_dwd5):
    importlib.reload(module)

doc = build_dwd5.build()
print(build_dwd5.mass_properties(doc))
for key, value in dwd5_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
