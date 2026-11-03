import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\cauliflower applicator\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import cfa_params
import cfa_calc
import cfa_parts
import build_cfa

for module in (cfa_params, cfa_calc, cfa_parts, build_cfa):
    importlib.reload(module)

doc = build_cfa.build()
cfa_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
