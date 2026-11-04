import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\flail mulcher\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import flm_params
import flm_parts
import flm_calc
import build_flm

for module in (flm_params, flm_parts, flm_calc, build_flm):
    importlib.reload(module)

doc = build_flm.build()
flm_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
