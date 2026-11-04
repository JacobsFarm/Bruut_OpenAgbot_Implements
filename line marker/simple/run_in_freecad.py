import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\line marker\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import lmk_params
import ssp_params
import ssp_parts
import build_ssp
import ddb_params
import ddb_parts
import lmk_parts
import lmk_calc
import build_lmk

for module in (ssp_params, ssp_parts, build_ssp, ddb_params, ddb_parts, lmk_params, lmk_parts, lmk_calc, build_lmk):
    importlib.reload(module)

doc = build_lmk.build()
lmk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
