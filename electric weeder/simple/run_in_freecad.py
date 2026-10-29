import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\electric weeder\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import elw_params
import elw_parts
import elw_calc
import build_elw

for module in (elw_params, elw_parts, elw_calc, build_elw):
    importlib.reload(module)

doc = build_elw.build()
elw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
