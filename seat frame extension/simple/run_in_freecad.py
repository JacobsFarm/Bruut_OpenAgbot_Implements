import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\seat frame extension\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import sfe_params
import sfe_parts
import sfe_calc
import build_sfe

for module in (sfe_params, sfe_parts, sfe_calc, build_sfe):
    importlib.reload(module)

doc = build_sfe.build()
sfe_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
