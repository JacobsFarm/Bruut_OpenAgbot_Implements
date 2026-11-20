import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\Agbot\aanbouwdelen\dockweed drill\v10"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd10_params
import dwd10_parts
import dwd10_calc
import build_dwd10

for module in (dwd10_params, dwd10_parts, dwd10_calc, build_dwd10):
    importlib.reload(module)

doc = build_dwd10.build()
print(build_dwd10.mass_properties(doc))
for key, value in dwd10_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.getDocument(build_dwd10.DOC_NAME).ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
