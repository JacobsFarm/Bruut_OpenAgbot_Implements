import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\soil scanner\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ssc_params
import ssc_parts
import ssc_calc
import build_ssc

for module in (ssc_params, ssc_parts, ssc_calc, build_ssc):
    importlib.reload(module)

doc = build_ssc.build()
ssc_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
