import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\battery pack\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import bpk_params
import bpk_parts
import bpk_calc
import build_bpk

for module in (bpk_params, bpk_parts, bpk_calc, build_bpk):
    importlib.reload(module)

doc = build_bpk.build()
bpk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
