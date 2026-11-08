import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dockweed drill\v8"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd8_params
import dwd8_parts
import dwd8_calc
import build_dwd8

for module in (dwd8_params, dwd8_parts, dwd8_calc, build_dwd8):
    importlib.reload(module)

doc = build_dwd8.build()
print(build_dwd8.mass_properties(doc))
for key, value in dwd8_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.getDocument(build_dwd8.DOC_NAME).ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
