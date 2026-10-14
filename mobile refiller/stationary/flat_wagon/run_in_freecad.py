import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\stationary\flat_wagon"
STATIONARY = os.path.dirname(FOLDER)

for p in (STATIONARY, FOLDER):
    if p not in sys.path:
        sys.path.insert(0, p)

import stc_params
import stc_parts
import stc_build
import stc_calc
import sfw_params
import sfw_parts
import sfw_calc
import build_sfw

for module in (stc_params, stc_parts, stc_build, stc_calc, sfw_params, sfw_parts, sfw_calc, build_sfw):
    importlib.reload(module)

doc = build_sfw.build()
print(sfw_calc.report())

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
