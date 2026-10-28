import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\soil sampler\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ssa_params
import ssa_parts
import ssa_calc
import build_ssa

for module in (ssa_params, ssa_parts, ssa_calc, build_ssa):
    importlib.reload(module)

doc = build_ssa.build()
ssa_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
