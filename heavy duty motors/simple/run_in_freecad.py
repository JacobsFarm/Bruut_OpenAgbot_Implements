import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\heavy duty motors\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import hdm_params
import hdm_parts
import hdm_calc
import build_hdm

for module in (hdm_params, hdm_parts, hdm_calc, build_hdm):
    importlib.reload(module)

doc = build_hdm.build()
hdm_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
