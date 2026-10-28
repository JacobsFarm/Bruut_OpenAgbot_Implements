import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\charging dock\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import cdk_params
import cdk_parts
import cdk_calc
import build_cdk

for module in (cdk_params, cdk_parts, cdk_calc, build_cdk):
    importlib.reload(module)

doc = build_cdk.build()
cdk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
