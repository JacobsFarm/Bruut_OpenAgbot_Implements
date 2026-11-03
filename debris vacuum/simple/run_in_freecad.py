import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\debris vacuum\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dvc_params
import pbl_params
import pbl_parts
import build_pbl
import bsw_params
import bsw_parts
import mgs_params
import mgs_parts
import dvc_parts
import dvc_calc
import build_dvc

for module in (pbl_params, pbl_parts, build_pbl, bsw_params, bsw_parts, mgs_params, mgs_parts, dvc_params, dvc_parts,
               dvc_calc, build_dvc):
    importlib.reload(module)

doc = build_dvc.build()
dvc_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
