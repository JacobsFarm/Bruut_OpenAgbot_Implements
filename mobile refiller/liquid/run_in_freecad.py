import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\liquid"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mrl_params
import mrl_parts
import mrl_calc
import build_mrl

for module in (mrl_params, mrl_parts, mrl_calc, build_mrl):
    importlib.reload(module)

doc = build_mrl.build()
print(mrl_calc.report())

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
