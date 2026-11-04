import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\weeding bed\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import wdb_params
import wdb_parts
import wdb_calc
import build_wdb

for module in (wdb_params, wdb_parts, wdb_calc, build_wdb):
    importlib.reload(module)

doc = build_wdb.build()
wdb_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
