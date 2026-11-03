import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\disease scout\potato"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dsc_params
import dsc_calc
import dsc_parts
import dsc_field
import build_dsc

for module in (dsc_params, dsc_calc, dsc_parts, dsc_field, build_dsc):
    importlib.reload(module)

doc = build_dsc.build()
print(build_dsc.mass_properties(doc))
print(build_dsc.size(doc))
dsc_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
