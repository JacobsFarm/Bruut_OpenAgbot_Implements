import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\fence inspector\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import fin_params
import pbl_params
import pbl_parts
import build_pbl
import fin_parts
import fin_calc
import build_fin

for module in (pbl_params, pbl_parts, build_pbl, fin_params, fin_parts,
               fin_calc, build_fin):
    importlib.reload(module)

doc = build_fin.build()
fin_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
