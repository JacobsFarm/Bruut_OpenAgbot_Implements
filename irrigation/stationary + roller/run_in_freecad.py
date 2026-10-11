import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\irrigation\stationary + roller"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import irr_params
import irr_calc
import irr_parts
import build_irr

for module in (irr_params, irr_calc, irr_parts, build_irr):
    importlib.reload(module)

doc = build_irr.build()
irr_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
