import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\windbreak inspector\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import wbi_params
import fin_params
import fin_parts
import pbl_params
import pbl_parts
import build_pbl
import wbi_parts
import wbi_calc
import build_wbi

for module in (pbl_params, pbl_parts, build_pbl, fin_params, fin_parts, wbi_params, wbi_parts,
               wbi_calc, build_wbi):
    importlib.reload(module)

doc = build_wbi.build()
wbi_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
