import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\asparagus harvester\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import asp_params
import asp_parts
import asp_calc
import build_asp

for module in (asp_params, asp_parts, asp_calc, build_asp):
    importlib.reload(module)

doc = build_asp.build()
asp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
