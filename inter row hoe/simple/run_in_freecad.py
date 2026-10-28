import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\inter row hoe\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import irh_params
import irh_parts
import irh_calc
import build_irh

for module in (irh_params, irh_parts, irh_calc, build_irh):
    importlib.reload(module)

doc = build_irh.build()
irh_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
