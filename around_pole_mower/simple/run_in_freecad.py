import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\around_pole_mower\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import apm_params
import apm_parts
import apm_kin
import apm_calc
import build_apm

for module in (apm_params, apm_parts, apm_kin, apm_calc, build_apm):
    importlib.reload(module)

doc = build_apm.build()
apm_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
