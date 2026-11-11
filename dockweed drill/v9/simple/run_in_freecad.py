import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dockweed drill\v9\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dwd9s_params
import dwd9s_parts
import dwd9s_calc
import build_dwd9s

for module in (dwd9s_params, dwd9s_parts, dwd9s_calc, build_dwd9s):
    importlib.reload(module)

doc = build_dwd9s.build()
print(build_dwd9s.mass_properties(doc))
for key, value in dwd9s_calc.report().items():      # voorlopig: zonder geleiding
    print(key, value)

try:
    import FreeCADGui as Gui
    Gui.getDocument(build_dwd9s.DOC_NAME).ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
