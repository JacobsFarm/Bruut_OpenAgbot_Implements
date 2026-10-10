import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\brushes\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dbr_params
import dbr_parts
import dbr_calc
import build_dbr

for module in (dbr_params, dbr_parts, dbr_calc, build_dbr):
    importlib.reload(module)

CONFIG = "double_750"           # of "double_650", "single_850"
doc = build_dbr.build(CONFIG)
dbr_calc.report(CONFIG)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
