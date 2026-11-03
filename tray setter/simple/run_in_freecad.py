import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\tray setter\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import tst_params
import tst_parts
import tst_calc
import build_tst

for module in (tst_params, tst_parts, tst_calc, build_tst):
    importlib.reload(module)

doc = build_tst.build()
tst_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
