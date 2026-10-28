import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\grassland harrow\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import gha_params
import gha_parts
import gha_calc
import build_gha

for module in (gha_params, gha_parts, gha_calc, build_gha):
    importlib.reload(module)

doc = build_gha.build()
gha_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
