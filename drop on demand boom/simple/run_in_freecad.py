import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\drop on demand boom\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ddb_params
import ssp_params
import ssp_calc
import ssp_parts
import build_ssp
import ddb_parts
import ddb_calc
import build_ddb

for module in (ssp_params, ssp_calc, ssp_parts, build_ssp, ddb_params, ddb_parts, ddb_calc, build_ddb):
    importlib.reload(module)

doc = build_ddb.build()
ddb_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
