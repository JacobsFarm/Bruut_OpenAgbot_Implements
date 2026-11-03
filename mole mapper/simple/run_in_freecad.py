import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mole mapper\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mmp_params
import scm_params
import scm_parts
import build_scm
import pbl_params
import pbl_parts
import build_pbl
import mmp_parts
import mmp_calc
import build_mmp

for module in (pbl_params, pbl_parts, build_pbl, scm_params, scm_parts, build_scm, mmp_params, mmp_parts,
               mmp_calc, build_mmp):
    importlib.reload(module)

doc = build_mmp.build()
mmp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
