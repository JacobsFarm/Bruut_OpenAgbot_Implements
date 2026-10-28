import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\sawdust spreader\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import sds_params
import sds_parts
import sds_calc
import build_sds

for module in (sds_params, sds_parts, sds_calc, build_sds):
    importlib.reload(module)

doc = build_sds.build()
sds_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
