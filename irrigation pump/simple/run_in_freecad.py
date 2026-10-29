import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\irrigation pump\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import idp_params
import hpu_params
import hpu_parts
import idp_parts
import idp_calc
import build_idp

for module in (hpu_params, hpu_parts, idp_params, idp_parts, idp_calc, build_idp):
    importlib.reload(module)

doc = build_idp.build()
idp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
