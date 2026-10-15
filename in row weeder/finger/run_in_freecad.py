import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\in row weeder\finger"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import irw_params
import irw_calc
import irw_parts
import build_irw

for module in (irw_params, irw_calc, irw_parts, build_irw):
    importlib.reload(module)

doc = build_irw.build()
irw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
