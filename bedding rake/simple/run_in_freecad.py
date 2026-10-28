import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\bedding rake\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import bdr_params
import bdr_parts
import bdr_calc
import build_bdr

for module in (bdr_params, bdr_parts, bdr_calc, build_bdr):
    importlib.reload(module)

doc = build_bdr.build()
bdr_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
