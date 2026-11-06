import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dockweed drill\v7"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd7_params
import dwd7_parts
import dwd7_calc
import build_dwd7

for module in (dwd7_params, dwd7_parts, dwd7_calc, build_dwd7):
    importlib.reload(module)

doc = build_dwd7.build()
print(build_dwd7.mass_properties(doc))
for key, value in dwd7_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.getDocument(build_dwd7.DOC_NAME).ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
