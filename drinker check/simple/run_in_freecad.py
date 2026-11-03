import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\drinker check\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dck_params
import fin_params
import fin_parts
import pbl_params
import pbl_parts
import build_pbl
import dck_parts
import dck_calc
import build_dck

for module in (pbl_params, pbl_parts, build_pbl, fin_params, fin_parts, dck_params, dck_parts,
               dck_calc, build_dck):
    importlib.reload(module)

doc = build_dck.build()
dck_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
