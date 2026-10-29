import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\broom sweeper\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import bsw_params
import pbl_params
import pbl_parts
import build_pbl
import bsw_parts
import bsw_calc
import build_bsw

for module in (pbl_params, pbl_parts, build_pbl, bsw_params, bsw_parts, bsw_calc, build_bsw):
    importlib.reload(module)

doc = build_bsw.build()
bsw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
