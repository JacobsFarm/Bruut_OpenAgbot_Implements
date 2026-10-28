import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\push blade\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import pbl_params
import pbl_parts
import pbl_calc
import build_pbl

for module in (pbl_params, pbl_parts, pbl_calc, build_pbl):
    importlib.reload(module)

doc = build_pbl.build()
pbl_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
