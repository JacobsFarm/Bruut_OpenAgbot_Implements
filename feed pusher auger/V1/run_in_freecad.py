import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\feed pusher auger\advanced"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import fpa_params
import fpa_parts
import fpa_calc
import build_fpa

for module in (fpa_params, fpa_parts, fpa_calc, build_fpa):
    importlib.reload(module)

doc = build_fpa.build()
fpa_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
