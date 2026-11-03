import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\yield estimator\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import yld_params
import mmp_params
import mmp_parts
import pbl_params
import pbl_parts
import build_pbl
import yld_parts
import yld_calc
import build_yld

for module in (pbl_params, pbl_parts, build_pbl, mmp_params, mmp_parts, yld_params, yld_parts,
               yld_calc, build_yld):
    importlib.reload(module)

doc = build_yld.build()
yld_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
