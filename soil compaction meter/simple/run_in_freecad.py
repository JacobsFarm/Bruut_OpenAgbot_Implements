import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\soil compaction meter\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import scm_params
import scm_parts
import scm_calc
import build_scm

for module in (scm_params, scm_parts, scm_calc, build_scm):
    importlib.reload(module)

doc = build_scm.build()
scm_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
