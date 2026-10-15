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

import dwd4_params
import dwd4_parts
import dwd4_calc
import build_dwd4

for module in (dwd4_params, dwd4_parts, dwd4_calc, build_dwd4):
    importlib.reload(module)

doc = build_dwd4.build()
print(build_dwd4.mass_properties(doc))
for key, value in dwd4_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
