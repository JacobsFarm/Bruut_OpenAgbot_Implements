import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dockweed drill\v9\advanced"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd9_params
import dwd9_parts
import dwd9_calc
import build_dwd9

for module in (dwd9_params, dwd9_parts, dwd9_calc, build_dwd9):
    importlib.reload(module)

doc = build_dwd9.build()
print(build_dwd9.mass_properties(doc))
for key, value in dwd9_calc.report().items():
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.getDocument(build_dwd9.DOC_NAME).ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
