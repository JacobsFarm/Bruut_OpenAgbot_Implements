import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\marker\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mrk_params
import mrk_parts
import mrk_calc
import build_mrk

for module in (mrk_params, mrk_parts, mrk_calc, build_mrk):
    importlib.reload(module)

doc = build_mrk.build()
mrk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
