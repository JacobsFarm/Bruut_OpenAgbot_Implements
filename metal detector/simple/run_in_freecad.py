import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\metal detector\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mdt_params
import pbl_params
import pbl_parts
import build_pbl
import mdt_parts
import mdt_calc
import build_mdt

for module in (pbl_params, pbl_parts, build_pbl, mdt_params, mdt_parts, mdt_calc, build_mdt):
    importlib.reload(module)

doc = build_mdt.build()
mdt_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
