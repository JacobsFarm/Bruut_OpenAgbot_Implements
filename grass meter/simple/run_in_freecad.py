import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\grass meter\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import gmt_params
import gmt_parts
import gmt_calc
import build_gmt

for module in (gmt_params, gmt_parts, gmt_calc, build_gmt):
    importlib.reload(module)

doc = build_gmt.build()
gmt_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
