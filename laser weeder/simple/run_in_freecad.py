import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\laser weeder\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import lzw_params
import ddb_params
import ssp_params
import ssp_calc
import ssp_parts
import build_ssp
import ddb_calc
import ddb_parts
import build_ddb
import lzw_parts
import lzw_calc
import build_lzw

for module in (ssp_params, ssp_calc, ssp_parts, build_ssp, ddb_params, ddb_calc, ddb_parts, build_ddb, lzw_params, lzw_parts, lzw_calc, build_lzw):
    importlib.reload(module)

doc = build_lzw.build()
lzw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
