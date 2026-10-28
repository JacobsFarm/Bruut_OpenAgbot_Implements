import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\bag trailer\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import bgt_params
import bgt_parts
import bgt_calc
import build_bgt

for module in (bgt_params, bgt_parts, bgt_calc, build_bgt):
    importlib.reload(module)

doc = build_bgt.build()
bgt_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
