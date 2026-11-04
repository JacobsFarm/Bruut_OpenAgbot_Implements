import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\drone combination\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import drn_params
import pbl_params
import pbl_parts
import build_pbl
import drn_parts
import drn_calc
import build_drn

for module in (pbl_params, pbl_parts, build_pbl, drn_params, drn_parts,
               drn_calc, build_drn):
    importlib.reload(module)

doc = build_drn.build()
drn_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
