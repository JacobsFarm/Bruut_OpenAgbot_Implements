import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\magnet sweeper\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mgs_params
import pbl_params
import pbl_parts
import build_pbl
import bsw_params
import bsw_parts
import mgs_parts
import mgs_calc
import build_mgs

for module in (pbl_params, pbl_parts, build_pbl, bsw_params, bsw_parts, mgs_params, mgs_parts, mgs_calc, build_mgs):
    importlib.reload(module)

doc = build_mgs.build()
mgs_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
