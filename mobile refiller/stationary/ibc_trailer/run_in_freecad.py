import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\stationary\ibc_trailer"
STATIONARY = os.path.dirname(FOLDER)

for p in (STATIONARY, FOLDER):
    if p not in sys.path:
        sys.path.insert(0, p)

import stc_params
import stc_parts
import stc_build
import stc_calc
import sit_params
import sit_parts
import sit_calc
import build_sit

for module in (stc_params, stc_parts, stc_build, stc_calc, sit_params, sit_parts, sit_calc, build_sit):
    importlib.reload(module)

N = globals().get("N_IBC", 1)
doc = build_sit.build(N)
print(sit_calc.report(N))

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
