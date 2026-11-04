import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\swarm operation\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import swm_params
import pbl_params
import pbl_parts
import build_pbl
import swm_parts
import swm_calc
import build_swm

for module in (pbl_params, pbl_parts, build_pbl, swm_params, swm_parts,
               swm_calc, build_swm):
    importlib.reload(module)

doc = build_swm.build()
swm_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
