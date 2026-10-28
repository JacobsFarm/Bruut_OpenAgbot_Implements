import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mulch layer\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mly_params
import mly_parts
import mly_calc
import build_mly

for module in (mly_params, mly_parts, mly_calc, build_mly):
    importlib.reload(module)

doc = build_mly.build()
mly_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
