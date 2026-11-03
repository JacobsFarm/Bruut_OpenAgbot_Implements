import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\soil moisture placer\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import smp_params
import ssa_params
import ssa_calc
import ssa_parts
import build_ssa
import smp_parts
import smp_calc
import build_smp

for module in (ssa_params, ssa_calc, ssa_parts, build_ssa, smp_params, smp_parts, smp_calc, build_smp):
    importlib.reload(module)

doc = build_smp.build()
smp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
